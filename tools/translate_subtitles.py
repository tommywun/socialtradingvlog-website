#!/usr/bin/env python3
"""
Translate SRT subtitle files into multiple languages.

Usage:
    python3 tools/translate_subtitles.py VIDEO_ID [--langs es fr de it pt]
    python3 tools/translate_subtitles.py VIDEO_ID  # translates all languages

Example:
    python3 tools/translate_subtitles.py YZYgjitj7DM --langs es fr de

Outputs (in transcriptions/VIDEO_ID/):
    subtitles.es.srt, subtitles.fr.srt, subtitles.de.srt, etc.

Note: Uses Google Translate (free, no API key needed).
      Rate-limited to ~1 request per 50ms to avoid blocks.
"""

import sys
import os
import re
import time
import pathlib
import argparse

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

from deep_translator import GoogleTranslator

LANGUAGES = {
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "ru": "Russian",
    "ja": "Japanese",
    "zh-CN": "Chinese (Simplified)",
    "ar": "Arabic",
}


def parse_srt(srt_path):
    """Parse SRT into list of (index, timecode, text) tuples."""
    content = srt_path.read_text(encoding="utf-8").strip()
    blocks = re.split(r"\n\n+", content)
    entries = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            idx = lines[0].strip()
            timecode = lines[1].strip()
            text = " ".join(lines[2:]).strip()
            entries.append((idx, timecode, text))
    return entries


def translate_srt(srt_path, lang_code, output_path):
    entries = parse_srt(srt_path)
    if not entries:
        print(f"  Warning: no entries found in {srt_path}")
        return

    translator = GoogleTranslator(source="en", target=lang_code)

    total = len(entries)
    translated_lines = []

    for i, (idx, timecode, text) in enumerate(entries):
        if i % 20 == 0:
            print(f"  {i}/{total}...", end="\r")
        try:
            translated = translator.translate(text) or text
            time.sleep(0.06)
        except Exception as e:
            print(f"\n  Warning: failed on segment {idx}: {e}")
            translated = text
        translated_lines.append(f"{idx}\n{timecode}\n{translated}")

    output_path.write_text("\n\n".join(translated_lines) + "\n", encoding="utf-8")
    print(f"  {total}/{total} done  ")


def main():
    parser = argparse.ArgumentParser(description="Translate SRT subtitle files")
    parser.add_argument("video_id", help="YouTube video ID")
    parser.add_argument(
        "--langs",
        nargs="+",
        default=list(LANGUAGES.keys()),
        metavar="LANG",
        help=f"Language codes to translate to. Available: {', '.join(LANGUAGES)}",
    )
    args = parser.parse_args()

    base_dir = pathlib.Path(__file__).parent.parent / "transcriptions" / args.video_id
    srt_en = base_dir / "subtitles.en.srt"

    if not srt_en.exists():
        print(f"English SRT not found: {srt_en}")
        print("Run transcribe_video.py first.")
        sys.exit(1)

    for lang in args.langs:
        if lang not in LANGUAGES:
            print(f"Unknown language code: {lang}. Available: {', '.join(LANGUAGES)}")
            continue

        output_path = base_dir / f"subtitles.{lang}.srt"
        if output_path.exists():
            print(f"  {LANGUAGES[lang]}: already exists (skipping)")
            continue

        print(f"  Translating to {LANGUAGES[lang]} ({lang})...")
        translate_srt(srt_en, lang, output_path)
        print(f"  Saved: subtitles.{lang}.srt")

    print("\nAll done!")
    print(f"SRT files are in: transcriptions/{args.video_id}/")
    print("Upload .srt files to YouTube Studio > Subtitles for each video.")


if __name__ == "__main__":
    main()
