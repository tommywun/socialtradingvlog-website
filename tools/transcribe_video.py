#!/usr/bin/env python3
"""
Transcribe a YouTube video using yt-dlp + OpenAI Whisper.

Usage:
    python3 tools/transcribe_video.py VIDEO_ID [--model small]

Example:
    python3 tools/transcribe_video.py YZYgjitj7DM
    python3 tools/transcribe_video.py YZYgjitj7DM --model medium

Outputs (in transcriptions/VIDEO_ID/):
    transcript.txt       - plain text transcript
    subtitles.en.srt     - SRT format (upload to YouTube)
    subtitles.en.vtt     - WebVTT format (for website use)

Models (speed vs accuracy trade-off):
    tiny   - fastest, least accurate (~1min for 10min video)
    base   - fast, decent accuracy
    small  - good balance (recommended, ~3min for 10min video)
    medium - better accuracy, slower (~6min for 10min video)
    large  - best accuracy, slowest (~12min for 10min video)

Models download automatically on first use to ~/.cache/whisper/
"""

import sys
import os
import subprocess
import pathlib
import argparse

# Ensure local user packages are on the path
sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

import whisper


YDLP = os.path.expanduser("~/Library/Python/3.9/bin/yt-dlp")
FFMPEG = "/opt/homebrew/bin/ffmpeg"

# Ensure Homebrew ffmpeg is on PATH (Whisper calls it by name)
os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"


def download_audio(video_id, output_dir):
    url = f"https://www.youtube.com/watch?v={video_id}"

    # YouTube sometimes forces SABR streaming which blocks direct format downloads.
    # Using the Android player client bypasses this. We download the combined
    # video+audio (format 18, ~32MB for a 10-min video) and Whisper reads it directly.
    audio_path = output_dir / "audio.mp4"
    if audio_path.exists():
        print(f"  (audio already downloaded)")
        return audio_path

    cmd = [
        YDLP,
        "--extractor-args", "youtube:player_client=android",
        "--format", "bestaudio[ext=m4a]/bestaudio/best",
        "-o", str(audio_path),
        "--no-playlist",
        "--quiet",
        "--ffmpeg-location", FFMPEG,
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # yt-dlp may have saved with a different extension
    if not audio_path.exists():
        matches = list(output_dir.glob("audio.*"))
        if matches:
            return matches[0]

    if result.returncode != 0 or not audio_path.exists():
        print(f"Error downloading audio:\n{result.stderr}")
        sys.exit(1)

    return audio_path


def seconds_to_srt(s):
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    ms = int((sec % 1) * 1000)
    return f"{int(h):02d}:{int(m):02d}:{int(sec):02d},{ms:03d}"


def seconds_to_vtt(s):
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    ms = int((sec % 1) * 1000)
    return f"{int(h):02d}:{int(m):02d}:{int(sec):02d}.{ms:03d}"


def write_srt(segments, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{seconds_to_srt(seg['start'])} --> {seconds_to_srt(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n\n")


def write_vtt(segments, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for seg in segments:
            f.write(f"{seconds_to_vtt(seg['start'])} --> {seconds_to_vtt(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n\n")


def main():
    parser = argparse.ArgumentParser(description="Transcribe a YouTube video with Whisper")
    parser.add_argument("video_id", help="YouTube video ID (the part after ?v=)")
    parser.add_argument(
        "--model",
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: small)",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the downloaded audio file (deleted by default to save space)",
    )
    args = parser.parse_args()

    base_dir = pathlib.Path(__file__).parent.parent / "transcriptions" / args.video_id
    base_dir.mkdir(parents=True, exist_ok=True)

    # Skip if already transcribed
    transcript_path = base_dir / "transcript.txt"
    srt_path = base_dir / "subtitles.en.srt"
    if transcript_path.exists() and srt_path.exists():
        print(f"Already transcribed: {args.video_id} (delete the folder to redo)")
        return

    print(f"Downloading audio for {args.video_id}...")
    audio_path = download_audio(args.video_id, base_dir)

    # Try MPS (Apple Silicon GPU) first; large model uses sparse tensors
    # that MPS doesn't support, so fall back to CPU automatically.
    import torch
    device = "mps" if torch.backends.mps.is_available() else "cpu"

    try:
        print(f"Loading Whisper ({args.model} model) on {device.upper()}...")
        model = whisper.load_model(args.model, device=device)
        print("Transcribing... (this takes a few minutes)")
        result = model.transcribe(str(audio_path), verbose=False, fp16=False, language="en")
    except Exception as e:
        if device == "mps":
            print(f"  MPS unsupported ({type(e).__name__}), retrying on CPU...")
            model = whisper.load_model(args.model, device="cpu")
            print("Transcribing on CPU...")
            result = model.transcribe(str(audio_path), verbose=False, fp16=False, language="en")
        else:
            raise

    print("Writing output files...")
    transcript_path.write_text(result["text"], encoding="utf-8")
    write_srt(result["segments"], srt_path)
    write_vtt(result["segments"], base_dir / "subtitles.en.vtt")

    if not args.keep_audio:
        audio_path.unlink(missing_ok=True)

    duration = sum(seg["end"] - seg["start"] for seg in result["segments"])
    word_count = len(result["text"].split())
    print(f"\nDone!")
    print(f"  Video duration : ~{int(duration // 60)}m {int(duration % 60)}s")
    print(f"  Words          : ~{word_count}")
    print(f"  Output folder  : transcriptions/{args.video_id}/")
    print(f"    transcript.txt      - plain text")
    print(f"    subtitles.en.srt    - upload to YouTube Studio")
    print(f"    subtitles.en.vtt    - for website use")


if __name__ == "__main__":
    main()
