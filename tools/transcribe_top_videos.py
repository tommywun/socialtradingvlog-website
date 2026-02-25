#!/usr/bin/env python3
"""
Transcribe the top N videos by view count using Whisper API (Mac only).

Fetches view counts from YouTube API, sorts by views, and runs
transcribe_video.py on the top N that don't already have English SRTs.

Usage:
    python3 tools/transcribe_top_videos.py          # top 30 (default)
    python3 tools/transcribe_top_videos.py --top 50  # top 50
    python3 tools/transcribe_top_videos.py --dry-run  # preview only

After running, use sync_to_vps.sh to push the Whisper SRTs to VPS.
"""

import sys
import os
import json
import pathlib
import subprocess
import argparse
import time
from datetime import datetime

if sys.platform == "darwin":
    sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))
    os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"

# Load OpenAI API key
if not os.environ.get("OPENAI_API_KEY"):
    key_file = pathlib.Path.home() / ".config" / "stv-secrets" / "openai-api-key.txt"
    if key_file.exists():
        os.environ["OPENAI_API_KEY"] = key_file.read_text().strip()

BASE_DIR = pathlib.Path(__file__).parent.parent
TRANS_DIR = BASE_DIR / "transcriptions"
DATA_DIR = BASE_DIR / "data"
PYTHON = sys.executable
TRANSCRIBE = pathlib.Path(__file__).parent / "transcribe_video.py"

sys.path.insert(0, str(pathlib.Path(__file__).parent))


def get_all_video_ids():
    import re
    content = (BASE_DIR / "videos.html").read_text(encoding="utf-8")
    ids = re.findall(r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})', content)
    seen = set()
    unique = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            unique.append(i)
    return unique


def fetch_view_counts(video_ids):
    """Fetch view counts from YouTube API and cache them."""
    import pickle
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    token_path = pathlib.Path.home() / ".config" / "stv-secrets" / "youtube-token.pickle"
    with open(token_path, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    youtube = build("youtube", "v3", credentials=creds)
    counts = {}

    for batch_start in range(0, len(video_ids), 50):
        batch = video_ids[batch_start:batch_start + 50]
        resp = youtube.videos().list(part="statistics", id=",".join(batch)).execute()
        for item in resp.get("items", []):
            counts[item["id"]] = int(item["statistics"].get("viewCount", 0))

    # Cache
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = DATA_DIR / "video-view-counts.json"
    cache_path.write_text(json.dumps({
        "updated": datetime.now().isoformat(),
        "counts": counts,
    }, indent=2))

    return counts


def main():
    parser = argparse.ArgumentParser(description="Transcribe top videos by view count")
    parser.add_argument("--top", type=int, default=30, help="Number of top videos (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    all_ids = get_all_video_ids()
    print(f"Found {len(all_ids)} total videos")

    print("Fetching view counts from YouTube API...")
    counts = fetch_view_counts(all_ids)
    print(f"Got view counts for {len(counts)} videos")

    # Sort by views, filter to those missing English SRT
    sorted_ids = sorted(all_ids, key=lambda v: counts.get(v, 0), reverse=True)
    need_transcription = [
        v for v in sorted_ids
        if not (TRANS_DIR / v / "subtitles.en.srt").exists()
    ]

    targets = need_transcription[:args.top]
    print(f"\nTop {args.top} needing transcription: {len(targets)} videos")
    print()

    for i, vid_id in enumerate(targets, 1):
        views = counts.get(vid_id, 0)
        print(f"  {i:3d}. {vid_id}  ({views:>8,} views)")

    if args.dry_run:
        print(f"\nDry run — would transcribe {len(targets)} videos")
        return

    print(f"\nTranscribing {len(targets)} videos with Whisper API...")
    ok = 0
    errors = []

    for i, vid_id in enumerate(targets, 1):
        views = counts.get(vid_id, 0)
        print(f"\n[{i}/{len(targets)}] {vid_id} ({views:,} views)")
        t0 = time.time()

        r = subprocess.run(
            [PYTHON, str(TRANSCRIBE), "--model", "api", "--", vid_id],
            capture_output=True, text=True,
        )
        elapsed = int(time.time() - t0)

        if r.returncode == 0 and (TRANS_DIR / vid_id / "subtitles.en.srt").exists():
            print(f"  Done in {elapsed}s")
            ok += 1
        else:
            err = (r.stderr or r.stdout or "no output").strip().split('\n')[-1]
            print(f"  FAILED: {err}")
            errors.append(vid_id)

    print(f"\nDone! {ok}/{len(targets)} transcribed, {len(errors)} errors")
    if errors:
        print(f"Failed: {', '.join(errors)}")
    print(f"\nNow run: bash tools/sync_to_vps.sh")


if __name__ == "__main__":
    main()
