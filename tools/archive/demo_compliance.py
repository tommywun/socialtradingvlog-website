#!/usr/bin/env python3
"""
Demo: YouTube Subtitle Translation & Upload Pipeline
=====================================================
Screen recording demo for Google API compliance review.
Shows translation + upload of subtitles to YouTube.
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import sys
import os
import pickle
import pathlib
import time

# Load OpenAI API key
key_file = pathlib.Path.home() / ".config" / "stv-secrets" / "openai-api-key.txt"
if key_file.exists():
    os.environ["OPENAI_API_KEY"] = key_file.read_text().strip()

SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
YOUTUBE_TOKEN = SECRETS_DIR / "youtube-token.pickle"
PROJECT_DIR = pathlib.Path(__file__).parent.parent
TRANSCRIPTIONS_DIR = PROJECT_DIR / "transcriptions"


def get_youtube():
    """Authenticate with YouTube API."""
    from googleapiclient.discovery import build
    with open(YOUTUBE_TOKEN, "rb") as f:
        creds = pickle.load(f)
    return build("youtube", "v3", credentials=creds)


def parse_srt(text):
    """Parse SRT into blocks."""
    blocks = []
    current = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            if current:
                blocks.append(current)
                current = {}
            continue
        if not current:
            try:
                current["index"] = int(line)
            except ValueError:
                continue
        elif "start" not in current and "-->" in line:
            parts = line.split("-->")
            current["start"] = parts[0].strip()
            current["end"] = parts[1].strip()
        else:
            current.setdefault("text", "")
            if current["text"]:
                current["text"] += "\n"
            current["text"] += line
    if current:
        blocks.append(current)
    return blocks


def translate_srt(en_srt_text, lang_code, lang_name):
    """Translate SRT text using GPT-4o."""
    from openai import OpenAI
    client = OpenAI()

    blocks = parse_srt(en_srt_text)
    batch_size = 50
    translated_blocks = []

    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        texts = [b["text"] for b in batch]
        numbered = "\n".join(f"{j+1}|{t}" for j, t in enumerate(texts))

        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Translate these subtitle texts to {lang_name}. "
                        f"Each line: number|text. Return same format. "
                        f"Keep concise for subtitles. No explanations."
                    ),
                },
                {"role": "user", "content": numbered},
            ],
        )

        translated_text = response.choices[0].message.content.strip()
        translations = {}
        for line in translated_text.split("\n"):
            line = line.strip()
            if "|" in line:
                parts = line.split("|", 1)
                try:
                    idx = int(parts[0].strip())
                    translations[idx] = parts[1].strip()
                except ValueError:
                    continue

        for j, block in enumerate(batch):
            new_block = block.copy()
            new_block["text"] = translations.get(j + 1, block["text"])
            translated_blocks.append(new_block)

    # Build SRT
    lines = []
    for b in translated_blocks:
        lines.append(str(b["index"]))
        lines.append(f"{b['start']} --> {b['end']}")
        lines.append(b["text"])
        lines.append("")
    return "\n".join(lines)


def upload_caption(youtube, video_id, lang_code, lang_name, srt_text):
    """Upload a caption track to YouTube."""
    from googleapiclient.http import MediaInMemoryUpload

    body = {
        "snippet": {
            "videoId": video_id,
            "language": lang_code,
            "name": lang_name,
            "isDraft": False,
        }
    }

    media = MediaInMemoryUpload(
        srt_text.encode("utf-8"),
        mimetype="application/x-subrip",
        resumable=False,
    )

    response = youtube.captions().insert(
        part="snippet", body=body, media_body=media
    ).execute()

    return response.get("id", "")


def main():
    # Pick a video with existing translations
    VIDEO_ID = "hcWHSuCgn6k"
    video_dir = TRANSCRIPTIONS_DIR / VIDEO_ID

    print("=" * 65)
    print("  SocialTradingVlog — Subtitle Translation & Upload Pipeline")
    print("=" * 65)
    print()

    # --- Step 1: Show the English transcription ---
    en_srt_path = video_dir / "subtitles.en.srt"
    en_srt = en_srt_path.read_text()
    blocks = parse_srt(en_srt)

    print(f"  Video:  https://www.youtube.com/watch?v={VIDEO_ID}")
    print(f"  English transcription: {len(blocks)} subtitle blocks")
    print()
    print("  Sample subtitles:")
    for b in blocks[:3]:
        print(f"    {b['start']} --> {b['end']}")
        print(f"    \"{b['text']}\"")
        print()

    # --- Step 2: Translate new languages ---
    print("-" * 65)
    print("  STEP 1: Translating subtitles using GPT-4o API")
    print("-" * 65)

    # Translate and then upload these languages (full pipeline demo)
    demo_langs = {"hi": "Hindi", "zh-Hans": "Chinese (Simplified)"}
    translated_srts = {}

    for lang_code, lang_name in demo_langs.items():
        srt_path = video_dir / f"subtitles.{lang_code}.srt"
        if srt_path.exists():
            print(f"\n  {lang_name} ({lang_code}): already translated — skipping")
            translated_srts[lang_code] = srt_path.read_text()
            continue

        print(f"\n  Translating to {lang_name} ({lang_code})...")
        start_time = time.time()
        translated = translate_srt(en_srt, lang_code, lang_name)
        srt_path.write_text(translated)
        elapsed = time.time() - start_time
        t_blocks = parse_srt(translated)
        print(f"  Done — {len(t_blocks)} blocks in {elapsed:.1f}s")
        translated_srts[lang_code] = translated

        # Show sample
        if t_blocks:
            print(f"\n  Sample translation:")
            print(f"    English:  \"{blocks[0]['text']}\"")
            print(f"    {lang_name}: \"{t_blocks[0]['text']}\"")

    # --- Step 3: Upload translated subtitles to YouTube ---
    print()
    print("-" * 65)
    print("  STEP 2: Uploading translated subtitles to YouTube via API")
    print("-" * 65)

    youtube = get_youtube()

    for lang_code, lang_name in demo_langs.items():
        srt_text = translated_srts.get(lang_code)
        if not srt_text:
            continue

        print(f"\n  Uploading {lang_name} ({lang_code})...")

        try:
            caption_id = upload_caption(youtube, VIDEO_ID, lang_code, lang_name, srt_text)
            print(f"  Success — Caption ID: {caption_id}")
        except Exception as e:
            error_str = str(e)
            if "quotaExceeded" in error_str:
                print(f"  API quota limit reached — will continue tomorrow")
                break
            elif "Conflict" in error_str or "already exists" in error_str.lower():
                print(f"  Already exists on YouTube — skipping")
            else:
                print(f"  Error: {e}")

        time.sleep(1)

    print()
    print("=" * 65)
    print("  Done! Subtitles translated and uploaded to YouTube.")
    print(f"  Verify at: https://studio.youtube.com")
    print("=" * 65)


if __name__ == "__main__":
    main()
