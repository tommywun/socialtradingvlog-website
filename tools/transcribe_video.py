#!/usr/bin/env python3
"""
Transcribe a YouTube video using yt-dlp + OpenAI Whisper API.

Usage:
    python3 tools/transcribe_video.py VIDEO_ID
    python3 tools/transcribe_video.py VIDEO_ID --model local-large

Outputs (in transcriptions/VIDEO_ID/):
    transcript.txt       - plain text transcript
    subtitles.en.srt     - SRT format (upload to YouTube)
    subtitles.en.vtt     - WebVTT format (for website use)

By default uses the OpenAI Whisper API (whisper-1) which is fast and accurate.
Pass --model local-large to use the free local Whisper large model instead.
"""

import sys
import os
import subprocess
import pathlib
import argparse

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

YDLP = os.path.expanduser("~/Library/Python/3.9/bin/yt-dlp")
FFMPEG = "/opt/homebrew/bin/ffmpeg"

os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"


def download_audio(video_id, output_dir):
    url = f"https://www.youtube.com/watch?v={video_id}"

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


def compress_audio(audio_path):
    """Compress audio to mono mp3 at 64kbps to stay under OpenAI's 25MB limit."""
    mp3_path = audio_path.parent / "audio_compressed.mp3"
    if mp3_path.exists():
        return mp3_path

    print("  Compressing audio for API upload...")
    cmd = [
        FFMPEG, "-i", str(audio_path),
        "-ac", "1",           # mono
        "-ab", "64k",         # 64kbps — plenty for speech
        "-ar", "16000",       # 16kHz sample rate
        "-y",                 # overwrite
        str(mp3_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not mp3_path.exists():
        print(f"  Warning: compression failed, using original file")
        return audio_path
    return mp3_path


def transcribe_openai(audio_path):
    """Transcribe using OpenAI Whisper API (whisper-1 model)."""
    from openai import OpenAI

    client = OpenAI()

    # Compress if over 25MB
    if audio_path.stat().st_size > 24_000_000:
        upload_path = compress_audio(audio_path)
    else:
        upload_path = audio_path

    print("  Transcribing via OpenAI Whisper API...")
    with open(upload_path, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    # Clean up compressed file
    if upload_path != audio_path:
        upload_path.unlink(missing_ok=True)

    text = result.text
    segments = []
    for seg in result.segments:
        segments.append({
            "start": seg["start"] if isinstance(seg, dict) else seg.start,
            "end": seg["end"] if isinstance(seg, dict) else seg.end,
            "text": seg["text"] if isinstance(seg, dict) else seg.text,
        })

    return text, segments


def transcribe_local(audio_path, model_name="large"):
    """Transcribe using local Whisper model."""
    import whisper
    import torch

    device = "mps" if torch.backends.mps.is_available() else "cpu"

    try:
        print(f"  Loading Whisper ({model_name} model) on {device.upper()}...")
        model = whisper.load_model(model_name, device=device)
        print("  Transcribing locally... (this takes a while)")
        result = model.transcribe(str(audio_path), verbose=False, fp16=False, language="en")
    except Exception as e:
        if device == "mps":
            print(f"  MPS unsupported ({type(e).__name__}), retrying on CPU...")
            model = whisper.load_model(model_name, device="cpu")
            result = model.transcribe(str(audio_path), verbose=False, fp16=False, language="en")
        else:
            raise

    return result["text"], result["segments"]


def main():
    parser = argparse.ArgumentParser(description="Transcribe a YouTube video with Whisper")
    parser.add_argument("video_id", help="YouTube video ID (the part after ?v=)")
    parser.add_argument(
        "--model",
        default="api",
        help="'api' for OpenAI Whisper API (default), or 'local-large', 'local-small', etc.",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the downloaded audio file (deleted by default to save space)",
    )
    args = parser.parse_args()

    base_dir = pathlib.Path(__file__).parent.parent / "transcriptions" / args.video_id
    base_dir.mkdir(parents=True, exist_ok=True)

    transcript_path = base_dir / "transcript.txt"
    srt_path = base_dir / "subtitles.en.srt"
    if transcript_path.exists() and srt_path.exists():
        print(f"Already transcribed: {args.video_id} (delete the folder to redo)")
        return

    print(f"Downloading audio for {args.video_id}...")
    audio_path = download_audio(args.video_id, base_dir)

    if args.model == "api":
        text, segments = transcribe_openai(audio_path)
    else:
        local_model = args.model.replace("local-", "") if args.model.startswith("local-") else args.model
        text, segments = transcribe_local(audio_path, local_model)

    print("  Writing output files...")
    transcript_path.write_text(text, encoding="utf-8")
    write_srt(segments, srt_path)
    write_vtt(segments, base_dir / "subtitles.en.vtt")

    if not args.keep_audio:
        audio_path.unlink(missing_ok=True)

    duration = sum(seg["end"] - seg["start"] for seg in segments)
    word_count = len(text.split())
    print(f"\n  Done!")
    print(f"  Video duration : ~{int(duration // 60)}m {int(duration % 60)}s")
    print(f"  Words          : ~{word_count}")
    print(f"  Output folder  : transcriptions/{args.video_id}/")


if __name__ == "__main__":
    main()
