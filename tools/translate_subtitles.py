#!/usr/bin/env python3
"""
Translate SRT subtitle files into multiple languages.

Engines:
  openai          GPT-4o-mini — high quality, ~$0.05/video/language
  deep-translator Google Translate via deep-translator — free, lower quality

Both engines pass through a quality gate before writing the SRT file.
Failed translations are deleted so the pipeline retries next run.

Usage:
    python3 tools/translate_subtitles.py VIDEO_ID
    python3 tools/translate_subtitles.py VIDEO_ID --engine openai
    python3 tools/translate_subtitles.py VIDEO_ID --langs es fr de
    python3 tools/translate_subtitles.py VIDEO_ID --engine openai --langs es fr de

Safe to re-run — skips languages that already have an SRT file.
"""

import sys
import os
import re
import time
import pathlib
import argparse

if sys.platform == "darwin":
    sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

# Load OpenAI API key from secrets file if not already in environment
if not os.environ.get("OPENAI_API_KEY"):
    key_file = pathlib.Path.home() / ".config" / "stv-secrets" / "openai-api-key.txt"
    if key_file.exists():
        os.environ["OPENAI_API_KEY"] = key_file.read_text().strip()

LANGUAGES = {
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "ar": "Arabic",
    "ko": "Korean",
    "ru": "Russian",
    "ja": "Japanese",
    "zh-CN": "Chinese (Simplified)",
    "hi": "Hindi",
}

# Character-set validators for non-Latin scripts.
# If a translated text doesn't contain ANY characters from the target script,
# it's almost certainly not translated (e.g. still English).
CHAR_CHECKS = {
    "ar": lambda t: any(0x0600 <= ord(c) <= 0x06FF for c in t),
    "ko": lambda t: any(0xAC00 <= ord(c) <= 0xD7AF for c in t),
    "zh-CN": lambda t: any(0x4E00 <= ord(c) <= 0x9FFF for c in t),
    "ja": lambda t: any(
        0x3040 <= ord(c) <= 0x30FF or 0x4E00 <= ord(c) <= 0x9FFF for c in t
    ),
    "ru": lambda t: any(0x0400 <= ord(c) <= 0x04FF for c in t),
    "hi": lambda t: any(0x0900 <= ord(c) <= 0x097F for c in t),
}


# ── SRT Parsing ───────────────────────────────────────────────────────


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


# ── Quality Gate ──────────────────────────────────────────────────────


def quality_check(entries_en, translated_texts, lang_code):
    """Validate translation quality. Returns (passed, reason)."""
    if not translated_texts:
        return False, "no translated segments"

    # Empty segments
    empty = sum(1 for t in translated_texts if not t.strip())
    if empty > 0:
        return False, f"{empty} empty segment(s)"

    # Identity ratio — if >50% of segments are identical to English, it wasn't translated
    if len(entries_en) == len(translated_texts):
        identical = sum(
            1 for (_, _, en), tr in zip(entries_en, translated_texts)
            if en.strip().lower() == tr.strip().lower()
        )
        ratio = identical / len(entries_en)
        if ratio > 0.5:
            return False, f"{ratio:.0%} segments identical to English"

    # Character-set check for non-Latin scripts
    if lang_code in CHAR_CHECKS:
        all_text = " ".join(translated_texts)
        if not CHAR_CHECKS[lang_code](all_text):
            return False, f"no {LANGUAGES.get(lang_code, lang_code)} characters detected"

    return True, "ok"


# ── OpenAI Engine ─────────────────────────────────────────────────────


def translate_openai(entries, lang_code, lang_name):
    """Translate using GPT-4o-mini. Returns list of translated text strings."""
    from openai import OpenAI
    client = OpenAI()

    translated = []
    batch_size = 25

    for batch_start in range(0, len(entries), batch_size):
        batch = entries[batch_start:batch_start + batch_size]

        # Build numbered input
        segment_text = "\n".join(
            f"{i+1}: {text}" for i, (_, _, text) in enumerate(batch)
        )

        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f"Translate the following English subtitle segments to {lang_name}. "
                                f"Output ONLY the translated text for each numbered segment, "
                                f"preserving the exact numbering format 'N: translated text'. "
                                f"Do not add explanations or notes."
                            ),
                        },
                        {"role": "user", "content": segment_text},
                    ],
                    temperature=0.3,
                )

                result_text = response.choices[0].message.content.strip()
                batch_translations = {}
                for line in result_text.split("\n"):
                    m = re.match(r"(\d+)\s*[:\.]\s*(.+)", line.strip())
                    if m:
                        batch_translations[int(m.group(1))] = m.group(2).strip()

                for i, (_, _, orig_text) in enumerate(batch):
                    translated.append(batch_translations.get(i + 1, orig_text))

                break  # success

            except Exception as e:
                if attempt < 2:
                    wait = 2 ** (attempt + 1)
                    print(f"    retry in {wait}s: {e}")
                    time.sleep(wait)
                else:
                    print(f"    OpenAI failed after 3 attempts: {e}")
                    for _, _, orig_text in batch:
                        translated.append(orig_text)

        if batch_start > 0:
            print(f"    {batch_start + len(batch)}/{len(entries)}...", end="\r")

    return translated


# ── deep-translator Engine ────────────────────────────────────────────


def translate_deep(entries, lang_code):
    """Translate using Google Translate (free). Returns list of translated text strings."""
    from deep_translator import GoogleTranslator
    translator = GoogleTranslator(source="en", target=lang_code)

    translated = []
    for i, (idx, timecode, text) in enumerate(entries):
        if i % 20 == 0 and i > 0:
            print(f"    {i}/{len(entries)}...", end="\r")

        for attempt in range(3):
            try:
                result = translator.translate(text) or text
                translated.append(result)
                time.sleep(0.06)
                break
            except Exception as e:
                if attempt < 2:
                    wait = 2 ** attempt  # 1s, 2s
                    time.sleep(wait)
                else:
                    print(f"\n    Warning: failed segment {idx}: {e}")
                    translated.append(text)

    return translated


# ── Main Translation Function ─────────────────────────────────────────


def translate_srt(srt_path, lang_code, output_path, engine="deep-translator"):
    """Translate an SRT file. Returns True on success, False on failure."""
    entries = parse_srt(srt_path)
    if not entries:
        print(f"    Warning: no entries in {srt_path}")
        return False

    lang_name = LANGUAGES.get(lang_code, lang_code)
    total = len(entries)

    if engine == "openai":
        translated_texts = translate_openai(entries, lang_code, lang_name)
    else:
        translated_texts = translate_deep(entries, lang_code)

    if len(translated_texts) != total:
        print(f"    Warning: got {len(translated_texts)} translations for {total} segments")
        return False

    # Quality gate
    passed, reason = quality_check(entries, translated_texts, lang_code)
    if not passed:
        print(f"    REJECTED: {reason}")
        return False

    # Write SRT
    srt_blocks = []
    for (idx, timecode, _), tr_text in zip(entries, translated_texts):
        srt_blocks.append(f"{idx}\n{timecode}\n{tr_text}")

    output_path.write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8")
    print(f"    {total}/{total} done  ")
    return True


# ── CLI ───────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Translate SRT subtitle files")
    parser.add_argument("video_id", help="YouTube video ID")
    parser.add_argument(
        "--langs", nargs="+", default=list(LANGUAGES.keys()),
        metavar="LANG",
        help=f"Language codes. Available: {', '.join(LANGUAGES)}",
    )
    parser.add_argument(
        "--engine", choices=["openai", "deep-translator"], default="deep-translator",
        help="Translation engine (default: deep-translator)",
    )
    args = parser.parse_args()

    base_dir = pathlib.Path(__file__).parent.parent / "transcriptions" / args.video_id
    srt_en = base_dir / "subtitles.en.srt"

    if not srt_en.exists():
        print(f"English SRT not found: {srt_en}")
        print("Run transcribe_video.py first.")
        sys.exit(1)

    engine = args.engine
    if engine == "openai" and not os.environ.get("OPENAI_API_KEY"):
        print("  Warning: OPENAI_API_KEY not set, falling back to deep-translator")
        engine = "deep-translator"

    errors = 0
    for lang in args.langs:
        if lang not in LANGUAGES:
            print(f"  Unknown language: {lang}. Available: {', '.join(LANGUAGES)}")
            continue

        output_path = base_dir / f"subtitles.{lang}.srt"
        if output_path.exists():
            print(f"  {LANGUAGES[lang]}: already exists (skipping)")
            continue

        print(f"  Translating to {LANGUAGES[lang]} ({lang}) [{engine}]...")
        success = translate_srt(srt_en, lang, output_path, engine=engine)

        if success:
            print(f"  Saved: subtitles.{lang}.srt")
        else:
            if output_path.exists():
                output_path.unlink()
            print(f"  FAILED: subtitles.{lang}.srt (will retry next run)")
            errors += 1

    if errors:
        print(f"\n{errors} language(s) failed — will retry next pipeline run")
        sys.exit(1)

    print("\nAll done!")


if __name__ == "__main__":
    main()
