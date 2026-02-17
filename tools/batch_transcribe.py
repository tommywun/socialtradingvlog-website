#!/usr/bin/env python3
"""
Batch transcribe multiple YouTube videos.

Usage:
    python3 tools/batch_transcribe.py --ids VIDEO_ID1 VIDEO_ID2 ...
    python3 tools/batch_transcribe.py --file video_ids.txt
    python3 tools/batch_transcribe.py --popular 20   # top 20 by view count

Examples:
    # Transcribe specific videos
    python3 tools/batch_transcribe.py --ids YZYgjitj7DM k48YLAbEcY0

    # Transcribe from a text file (one video ID per line)
    python3 tools/batch_transcribe.py --file my_videos.txt

    # Transcribe the top 20 most popular videos from the site
    python3 tools/batch_transcribe.py --popular 20

    # Use a larger model for better accuracy
    python3 tools/batch_transcribe.py --popular 10 --model medium

Notes:
    - Skips videos already transcribed (delete the folder to redo)
    - Saves a log of progress to transcriptions/batch_log.txt
    - With 'small' model: roughly 2-4 minutes per 10-minute video
"""

import sys
import os
import time
import pathlib
import argparse
import subprocess
import json
from datetime import datetime

BASE_DIR = pathlib.Path(__file__).parent.parent
TRANSCRIPTIONS_DIR = BASE_DIR / "transcriptions"
TRANSCRIBE_SCRIPT = pathlib.Path(__file__).parent / "transcribe_video.py"
PYTHON = sys.executable

# Extract video IDs from the generated videos.html (most popular first)
def get_popular_video_ids(n=None):
    import re
    videos_html = BASE_DIR / "videos.html"
    if not videos_html.exists():
        print("videos.html not found")
        return []
    content = videos_html.read_text(encoding="utf-8")
    ids = re.findall(r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})', content)
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for vid_id in ids:
        if vid_id not in seen:
            seen.add(vid_id)
            unique.append(vid_id)
    return unique[:n] if n else unique


def transcribe_one(video_id, model):
    out_dir = TRANSCRIPTIONS_DIR / video_id
    if (out_dir / "transcript.txt").exists() and (out_dir / "subtitles.en.srt").exists():
        return "skipped"

    cmd = [PYTHON, str(TRANSCRIBE_SCRIPT), "--model", model, "--", video_id]
    result = subprocess.run(cmd, capture_output=False, text=True)
    return "ok" if result.returncode == 0 else "error"


def main():
    parser = argparse.ArgumentParser(description="Batch transcribe YouTube videos")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ids", nargs="+", metavar="ID", help="One or more YouTube video IDs")
    group.add_argument("--file", metavar="FILE", help="Text file with one video ID per line")
    group.add_argument(
        "--popular", type=int, metavar="N",
        help="Transcribe the top N most popular videos (from videos.html)"
    )
    parser.add_argument(
        "--model", default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model (default: small)"
    )
    args = parser.parse_args()

    if args.ids:
        video_ids = args.ids
    elif args.file:
        file_path = pathlib.Path(args.file)
        if not file_path.exists():
            print(f"File not found: {args.file}")
            sys.exit(1)
        video_ids = [line.strip() for line in file_path.read_text().splitlines() if line.strip()]
    else:
        video_ids = get_popular_video_ids(args.popular)
        if not video_ids:
            print("No video IDs found")
            sys.exit(1)
        print(f"Found {len(video_ids)} video IDs from videos.html")

    total = len(video_ids)
    print(f"\nBatch transcription: {total} videos, model={args.model}")
    print("=" * 50)

    TRANSCRIPTIONS_DIR.mkdir(exist_ok=True)
    log_path = TRANSCRIPTIONS_DIR / "batch_log.txt"

    results = {"ok": 0, "skipped": 0, "error": 0}
    errors = []

    with open(log_path, "a") as log:
        log.write(f"\n--- Batch started {datetime.now().isoformat()} ---\n")
        for i, vid_id in enumerate(video_ids, 1):
            print(f"\n[{i}/{total}] {vid_id}")
            start = time.time()
            status = transcribe_one(vid_id, args.model)
            elapsed = time.time() - start
            results[status] += 1
            if status == "error":
                errors.append(vid_id)
            log.write(f"{vid_id}: {status} ({elapsed:.1f}s)\n")
            print(f"  {status} ({elapsed:.1f}s)")

    print("\n" + "=" * 50)
    print(f"Done: {results['ok']} transcribed, {results['skipped']} skipped, {results['error']} errors")
    if errors:
        print(f"Errors: {', '.join(errors)}")
    print(f"Log: {log_path}")


if __name__ == "__main__":
    main()
