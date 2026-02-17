#!/usr/bin/env python3
"""
Full overnight pipeline: transcribe all 333 videos + translate to top 10 global languages.

Runs each video in sequence:
  1. Download audio from YouTube
  2. Transcribe with Whisper large model (Apple Silicon GPU accelerated)
  3. Translate SRT to 10 languages via Google Translate
  4. Delete audio to save disk space

Safe to interrupt and re-run — skips already completed videos/languages.

Top 10 global languages by total speakers (excluding English):
  zh-CN  Chinese (Simplified)  ~1.3B
  es     Spanish               ~570M
  hi     Hindi                 ~600M
  ar     Arabic                ~370M
  pt     Portuguese            ~280M
  fr     French                ~280M
  ru     Russian               ~260M
  de     German                ~135M
  ja     Japanese              ~125M
  ko     Korean                ~82M
"""

import sys
import os
import re
import time
import pathlib
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))
os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"

BASE_DIR    = pathlib.Path(__file__).parent.parent
TRANS_DIR   = BASE_DIR / "transcriptions"
PYTHON      = sys.executable
TRANSCRIBE  = pathlib.Path(__file__).parent / "transcribe_video.py"
TRANSLATE   = pathlib.Path(__file__).parent / "translate_subtitles.py"
LOG_PATH    = TRANS_DIR / "pipeline.log"

MODEL = "large"

LANGUAGES = [
    "zh-CN",  # Chinese (Simplified)
    "es",     # Spanish
    "hi",     # Hindi
    "ar",     # Arabic
    "pt",     # Portuguese
    "fr",     # French
    "ru",     # Russian
    "de",     # German
    "ja",     # Japanese
    "ko",     # Korean
]


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


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


def main():
    TRANS_DIR.mkdir(exist_ok=True)
    ids = get_all_video_ids()
    total = len(ids)

    log(f"=== Pipeline started {datetime.now().isoformat()} ===")
    log(f"Videos: {total} | Model: {MODEL} | Languages: {len(LANGUAGES)}")
    log(f"Output: {TRANS_DIR}")

    done_count = sum(1 for v in ids if is_fully_done(v))
    log(f"Already complete: {done_count}/{total}")

    ok = 0
    errors = []

    for i, vid_id in enumerate(ids, 1):
        if is_fully_done(vid_id):
            print(f"[{i}/{total}] {vid_id}: skip (done)")
            ok += 1
            continue

        log(f"[{i}/{total}] {vid_id} —————————————————")
        t0 = time.time()

        # ── Step 1: Transcribe ──────────────────────────────────────────────
        srt_en = TRANS_DIR / vid_id / "subtitles.en.srt"
        if srt_en.exists():
            log("  transcription already exists")
        else:
            log(f"  transcribing with {MODEL} model...")
            r = subprocess.run(
                [PYTHON, str(TRANSCRIBE), "--model", MODEL, "--", vid_id],
                capture_output=False,
            )
            if r.returncode != 0 or not srt_en.exists():
                log(f"  ERROR: transcription failed")
                errors.append(vid_id)
                continue

        # ── Step 2: Translate ───────────────────────────────────────────────
        missing_langs = [
            lang for lang in LANGUAGES
            if not (TRANS_DIR / vid_id / f"subtitles.{lang}.srt").exists()
        ]
        if missing_langs:
            log(f"  translating to {len(missing_langs)} languages: {' '.join(missing_langs)}")
            r = subprocess.run(
                [PYTHON, str(TRANSLATE), vid_id, "--langs"] + missing_langs,
                capture_output=False,
            )
            if r.returncode != 0:
                log(f"  WARNING: translation had errors (continuing)")
        else:
            log("  all translations already done")

        elapsed = int(time.time() - t0)
        log(f"  done in {elapsed//60}m {elapsed%60}s")
        ok += 1

    log(f"=== Pipeline finished {datetime.now().isoformat()} ===")
    log(f"Completed: {ok}/{total} | Errors: {len(errors)}")
    if errors:
        log(f"Failed video IDs: {', '.join(errors)}")


if __name__ == "__main__":
    main()
