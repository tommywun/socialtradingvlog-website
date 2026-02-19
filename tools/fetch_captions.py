#!/usr/bin/env python3
"""
Fetch YouTube auto-generated English captions using the YouTube Data API.

This replaces yt-dlp for caption fetching on VPS where YouTube blocks
datacenter IPs. Uses the same OAuth credentials as upload_subtitles.py.

Usage:
    python3 tools/fetch_captions.py VIDEO_ID
    python3 tools/fetch_captions.py VIDEO_ID --force  # re-download even if exists

Outputs:
    transcriptions/VIDEO_ID/subtitles.en.srt
    transcriptions/VIDEO_ID/transcript.txt
"""

import sys
import os
import pathlib
import argparse
import pickle
import re

if sys.platform == "darwin":
    sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
YOUTUBE_TOKEN = SECRETS_DIR / "youtube-token.pickle"
YOUTUBE_OAUTH = SECRETS_DIR / "youtube-oauth.json"


def get_youtube_client():
    """Authenticate and return a YouTube API client."""
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    if not YOUTUBE_TOKEN.exists():
        raise RuntimeError(f"YouTube token not found at {YOUTUBE_TOKEN}")

    with open(YOUTUBE_TOKEN, "rb") as f:
        creds = pickle.load(f)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(YOUTUBE_TOKEN, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def srt_time(seconds):
    """Convert seconds to SRT timestamp format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_youtube_srt(raw_srt):
    """Parse YouTube's SRT format into segments."""
    segments = []
    blocks = raw_srt.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            # Line 1: index, Line 2: timestamps, Line 3+: text
            time_line = lines[1]
            text = " ".join(lines[2:]).strip()
            match = re.match(
                r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
                time_line,
            )
            if match:
                g = [int(x) for x in match.groups()]
                start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
                end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
                segments.append({"start": start, "end": end, "text": text})
    return segments


def fetch_captions(video_id, output_dir, force=False):
    """Fetch auto-generated English captions for a video."""
    srt_path = output_dir / "subtitles.en.srt"
    txt_path = output_dir / "transcript.txt"

    if srt_path.exists() and txt_path.exists() and not force:
        print(f"  Already have captions for {video_id}")
        return True

    youtube = get_youtube_client()

    # List caption tracks for this video
    caption_list = youtube.captions().list(part="snippet", videoId=video_id).execute()

    # Find English caption track (prefer manual, fall back to auto-generated)
    en_caption = None
    for item in caption_list.get("items", []):
        lang = item["snippet"]["language"]
        track_kind = item["snippet"].get("trackKind", "")
        if lang == "en":
            if track_kind != "ASR":
                # Manual English captions — preferred
                en_caption = item
                break
            else:
                en_caption = item  # Auto-generated, keep looking for manual

    if not en_caption:
        print(f"  No English captions found for {video_id}")
        return False

    caption_id = en_caption["id"]
    kind = en_caption["snippet"].get("trackKind", "standard")
    print(f"  Found {'auto-generated' if kind == 'ASR' else 'manual'} English captions")

    # Download the caption track in SRT format
    srt_content = (
        youtube.captions()
        .download(id=caption_id, tfmt="srt")
        .execute()
    )

    # Handle bytes or string response
    if isinstance(srt_content, bytes):
        srt_content = srt_content.decode("utf-8")

    # Write SRT file
    output_dir.mkdir(parents=True, exist_ok=True)
    srt_path.write_text(srt_content, encoding="utf-8")

    # Extract plain text transcript
    segments = parse_youtube_srt(srt_content)
    plain_text = " ".join(seg["text"] for seg in segments)
    txt_path.write_text(plain_text, encoding="utf-8")

    word_count = len(plain_text.split())
    print(f"  Saved: {srt_path.name} ({word_count} words, {len(segments)} segments)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube captions via API")
    parser.add_argument("video_id", help="YouTube video ID")
    parser.add_argument("--force", action="store_true", help="Re-download even if exists")
    args = parser.parse_args()

    base_dir = pathlib.Path(__file__).parent.parent / "transcriptions" / args.video_id
    base_dir.mkdir(parents=True, exist_ok=True)

    success = fetch_captions(args.video_id, base_dir, args.force)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
