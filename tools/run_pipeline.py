#!/usr/bin/env python3
"""
Full pipeline: transcribe/fetch captions + translate + upload subtitles.

Modes:
  Default (Mac):    Transcribe via Whisper API + translate
  --translate-only: Only translate videos that already have English SRT
  --vps-auto:       Fetch captions via YouTube API + translate + upload to YouTube
                    (for VPS where yt-dlp can't download from YouTube)

Safe to interrupt and re-run — skips already completed videos/languages.

Usage:
    python3 tools/run_pipeline.py                    # Mac: transcribe + translate
    python3 tools/run_pipeline.py --translate-only    # translate existing SRTs only
    python3 tools/run_pipeline.py --vps-auto          # VPS: fetch + translate + upload
"""

import sys
import os
import re
import json
import time
import pathlib
import subprocess
import argparse
from datetime import datetime

if sys.platform == "darwin":
    sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))
    os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"

BASE_DIR    = pathlib.Path(__file__).parent.parent
TRANS_DIR   = BASE_DIR / "transcriptions"
DATA_DIR    = BASE_DIR / "data"
TOOLS_DIR   = pathlib.Path(__file__).parent

# Load OpenAI API key from secrets file if not already in environment
if not os.environ.get("OPENAI_API_KEY"):
    key_file = pathlib.Path.home() / ".config" / "stv-secrets" / "openai-api-key.txt"
    if key_file.exists():
        os.environ["OPENAI_API_KEY"] = key_file.read_text().strip()

PYTHON      = sys.executable
TRANSCRIBE  = TOOLS_DIR / "transcribe_video.py"
TRANSLATE   = TOOLS_DIR / "translate_subtitles.py"
FETCH_CAPS  = TOOLS_DIR / "fetch_captions.py"
UPLOAD_SUBS = TOOLS_DIR / "upload_subtitles.py"
LOG_PATH    = TRANS_DIR / "pipeline.log"
LOCK_FILE   = pathlib.Path("/tmp/stv-pipeline.lock")

MODEL = "local-large"

# Max VIDEO uploads per pipeline run (YouTube quota: 10,000 units/day,
# caption insert = ~400 units each, 9 languages per video = ~3,600 units/video,
# so 2 full videos per day is safe with headroom for list/fetch operations)
MAX_VIDEO_UPLOADS_PER_RUN = 2

LANGUAGES = [
    "es",     # Spanish — Spain, Latin America (eToro available)
    "de",     # German — Germany, Austria, Switzerland (major eToro market)
    "fr",     # French — France (eToro available)
    "it",     # Italian — Italy (one of eToro's biggest markets)
    "pt",     # Portuguese — Portugal, Brazil (eToro available)
    "ar",     # Arabic — UAE, Saudi, Kuwait (eToro available)
    "pl",     # Polish — Poland (eToro available, strong Central EU market)
    "nl",     # Dutch — Netherlands (eToro available)
    "ko",     # Korean — South Korea (eToro available)
]

VIEW_COUNTS_FILE = DATA_DIR / "video-view-counts.json"


def get_all_video_ids():
    content = (BASE_DIR / "videos.html").read_text(encoding="utf-8")
    ids = re.findall(r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})', content)
    seen = set()
    unique = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            unique.append(i)
    return unique


def get_view_counts(video_ids):
    """Load cached view counts, refresh weekly via YouTube API."""
    cache = {}
    if VIEW_COUNTS_FILE.exists():
        try:
            data = json.loads(VIEW_COUNTS_FILE.read_text())
            cache = data.get("counts", {})
            last_updated = data.get("updated", "")
            # Refresh if older than 7 days
            if last_updated:
                age = (datetime.now() - datetime.fromisoformat(last_updated)).days
                if age < 7:
                    return cache
        except Exception:
            pass

    # Fetch from YouTube API
    try:
        import pickle
        token_path = pathlib.Path.home() / ".config" / "stv-secrets" / "youtube-token.pickle"
        if not token_path.exists():
            return cache

        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        with open(token_path, "rb") as f:
            creds = pickle.load(f)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "wb") as f:
                pickle.dump(creds, f)

        youtube = build("youtube", "v3", credentials=creds)

        # Batch in groups of 50 (API limit)
        for batch_start in range(0, len(video_ids), 50):
            batch = video_ids[batch_start:batch_start + 50]
            resp = youtube.videos().list(
                part="statistics", id=",".join(batch)
            ).execute()
            for item in resp.get("items", []):
                vid_id = item["id"]
                views = int(item["statistics"].get("viewCount", 0))
                cache[vid_id] = views

        # Save cache
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        VIEW_COUNTS_FILE.write_text(json.dumps({
            "updated": datetime.now().isoformat(),
            "counts": cache,
        }, indent=2))
        log(f"  Refreshed view counts for {len(cache)} videos")

    except Exception as e:
        log(f"  Warning: could not fetch view counts: {e}")

    return cache


def sort_by_views(video_ids, view_counts):
    """Sort video IDs by view count descending (highest traffic first)."""
    return sorted(video_ids, key=lambda v: view_counts.get(v, 0), reverse=True)


def is_fully_done(vid_id):
    d = TRANS_DIR / vid_id
    if not (d / "transcript.txt").exists():
        return False
    if not (d / "subtitles.en.srt").exists():
        return False
    for lang in LANGUAGES:
        if not (d / f"subtitles.{lang}.srt").exists():
            return False
    return True


def try_fetch_captions(vid_id):
    """Try to get English captions via YouTube API (VPS fallback).

    Returns:
        "ok"    — captions fetched successfully
        "quota" — YouTube API quota exceeded (stop trying)
        "error" — other error (skip this video, try next)
    """
    srt_en = TRANS_DIR / vid_id / "subtitles.en.srt"
    log(f"  fetching captions via YouTube API...")
    r = subprocess.run(
        [PYTHON, str(FETCH_CAPS), vid_id],
        capture_output=True, text=True,
    )
    if r.returncode == 0 and srt_en.exists():
        log(f"  captions fetched successfully")
        return "ok"
    else:
        output = (r.stderr or r.stdout or "no output").strip()
        err = output.split('\n')[-1:]
        if "quotaExceeded" in output:
            log(f"  caption fetch quota exceeded (stopping API calls)")
            return "quota"
        log(f"  caption fetch failed: {' '.join(err)}")
        return "error"


def try_upload_subtitles(vid_id):
    """Upload translated subtitles for a video to YouTube."""
    log(f"  uploading subtitles to YouTube...")
    r = subprocess.run(
        [PYTHON, str(UPLOAD_SUBS), "--video", vid_id, "--skip-english"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        # Count uploads from output
        output = r.stdout or ""
        uploaded = output.count("created") + output.count("updated")
        log(f"  uploaded {uploaded} subtitle tracks")
        return uploaded
    else:
        err = (r.stderr or r.stdout or "no output").strip().split('\n')[-2:]
        # Quota exceeded is expected — not an error
        if "quotaExceeded" in str(err):
            log(f"  YouTube quota reached (will continue tomorrow)")
            return -1  # Signal to stop uploading
        log(f"  upload failed: {' '.join(err)}")
        return 0


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def send_summary(ok, total, errors, uploads, mode):
    """Send pipeline summary via Telegram."""
    try:
        sys.path.insert(0, str(TOOLS_DIR))
        from security_lib import send_telegram

        if errors:
            emoji = "⚠️"
            subject = f"Pipeline: {ok}/{total} done, {len(errors)} errors"
        else:
            emoji = "✅"
            subject = f"Pipeline: {ok}/{total} done"

        body = f"Mode: {mode}\n"
        body += f"Completed: {ok}/{total}\n"
        if uploads > 0:
            body += f"Subtitles uploaded: {uploads} tracks\n"
        if errors:
            body += f"Failed: {', '.join(errors[:10])}\n"

        send_telegram(subject, body, emoji=emoji, dedupe_key="pipeline-summary")
    except Exception as e:
        log(f"  Warning: could not send Telegram summary: {e}")


def acquire_lock():
    """Prevent duplicate pipeline instances. Returns True if lock acquired."""
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            # Check if process is still running
            os.kill(pid, 0)
            print(f"Pipeline already running (PID {pid}). Exiting.")
            return False
        except (ValueError, ProcessLookupError, PermissionError):
            # Stale lock — process no longer exists
            pass
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def release_lock():
    """Remove lock file on exit."""
    try:
        if LOCK_FILE.exists():
            pid = int(LOCK_FILE.read_text().strip())
            if pid == os.getpid():
                LOCK_FILE.unlink()
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Transcription + translation pipeline")
    parser.add_argument("--translate-only", action="store_true",
                        help="Skip transcription — only translate videos that already have English SRT")
    parser.add_argument("--vps-auto", action="store_true",
                        help="VPS mode: fetch captions via API, translate, upload to YouTube")
    args = parser.parse_args()

    if not acquire_lock():
        sys.exit(1)

    import atexit
    atexit.register(release_lock)

    TRANS_DIR.mkdir(exist_ok=True)
    ids = get_all_video_ids()
    total = len(ids)

    # Determine mode
    if args.vps_auto:
        mode = "vps-auto"
    elif args.translate_only:
        mode = "translate-only"
    else:
        mode = "full"

    log(f"=== Pipeline started {datetime.now().isoformat()} ({mode}) ===")
    log(f"Videos: {total} | Model: {MODEL} | Languages: {len(LANGUAGES)}")

    # Prioritize by view count
    view_counts = get_view_counts(ids)
    if view_counts:
        ids = sort_by_views(ids, view_counts)
        top3 = [(v, view_counts.get(v, 0)) for v in ids[:3]]
        log(f"Top 3 by views: {', '.join(f'{v}({c:,})' for v, c in top3)}")

    # Top 30 by views get OpenAI translations (higher quality)
    top_30_ids = set(ids[:30]) if view_counts else set()

    done_count = sum(1 for v in ids if is_fully_done(v))
    log(f"Already complete: {done_count}/{total}")

    ok = 0
    errors = []
    videos_uploaded = 0
    upload_quota_hit = False
    caption_quota_hit = False

    for i, vid_id in enumerate(ids, 1):
        if is_fully_done(vid_id):
            ok += 1
            continue

        log(f"[{i}/{total}] {vid_id} —————————————————")
        t0 = time.time()

        # ── Step 1: Get English SRT ──────────────────────────────────────
        srt_en = TRANS_DIR / vid_id / "subtitles.en.srt"
        if srt_en.exists():
            log("  English SRT already exists")
        elif args.translate_only:
            log("  no English SRT yet (skipping — translate-only mode)")
            ok += 1
            continue
        elif args.vps_auto:
            # VPS: use YouTube API to fetch captions
            if caption_quota_hit:
                log("  skipping — API quota already exceeded")
                continue
            result = try_fetch_captions(vid_id)
            if result == "quota":
                caption_quota_hit = True
                errors.append(vid_id)
                continue
            elif result == "error":
                errors.append(vid_id)
                continue
        else:
            # Mac: use Whisper API transcription
            log(f"  transcribing with {MODEL} model...")
            r = subprocess.run(
                [PYTHON, str(TRANSCRIBE), "--model", MODEL, "--", vid_id],
                capture_output=True, text=True,
            )
            if r.returncode != 0 or not srt_en.exists():
                err_detail = (r.stderr or r.stdout or "no output").strip().split('\n')[-3:]
                log(f"  ERROR: transcription failed (exit {r.returncode})")
                for line in err_detail:
                    log(f"    {line.strip()}")
                errors.append(vid_id)
                continue

        # ── Step 2: Translate ────────────────────────────────────────────
        missing_langs = [
            lang for lang in LANGUAGES
            if not (TRANS_DIR / vid_id / f"subtitles.{lang}.srt").exists()
        ]
        if missing_langs:
            engine = "openai" if vid_id in top_30_ids else "deep-translator"
            log(f"  translating to {len(missing_langs)} languages [{engine}]: {' '.join(missing_langs)}")
            r = subprocess.run(
                [PYTHON, str(TRANSLATE), "--engine", engine, "--langs"] + missing_langs + ["--", vid_id],
                capture_output=False,
            )
            if r.returncode != 0:
                log(f"  WARNING: translation had errors (continuing)")
        else:
            log("  all translations already done")

        # ── Step 3: Upload (VPS-auto only) ───────────────────────────────
        if args.vps_auto and not upload_quota_hit and videos_uploaded < MAX_VIDEO_UPLOADS_PER_RUN:
            result = try_upload_subtitles(vid_id)
            if result == -1:
                upload_quota_hit = True
            elif result > 0:
                videos_uploaded += 1

        elapsed = int(time.time() - t0)
        log(f"  done in {elapsed//60}m {elapsed%60}s")
        ok += 1

    log(f"=== Pipeline finished {datetime.now().isoformat()} ===")
    log(f"Completed: {ok}/{total} | Errors: {len(errors)} | Videos uploaded: {videos_uploaded}")
    if errors:
        log(f"Failed video IDs: {', '.join(errors)}")

    # Send summary via Telegram
    send_summary(ok, total, errors, videos_uploaded, mode)


if __name__ == "__main__":
    main()
