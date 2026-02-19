#!/usr/bin/env python3
"""
Upload SRT subtitle files to YouTube videos.

Scans the transcriptions/ directory for SRT files and uploads them as
captions to the corresponding YouTube videos via the YouTube Data API v3.

Usage:
    python3 tools/upload_subtitles.py                # upload all pending subtitles
    python3 tools/upload_subtitles.py --dry-run       # preview what would be uploaded
    python3 tools/upload_subtitles.py --video VIDEO_ID # upload subtitles for one video only
"""

import sys
import os
import pathlib
import pickle
import argparse
import json
import time
from datetime import datetime

if sys.platform == "darwin":
    sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
YOUTUBE_TOKEN = SECRETS_DIR / "youtube-token.pickle"
YOUTUBE_OAUTH = SECRETS_DIR / "youtube-oauth.json"
PROJECT_DIR = pathlib.Path(__file__).parent.parent
TRANSCRIPTIONS_DIR = PROJECT_DIR / "transcriptions"
UPLOAD_LOG = PROJECT_DIR / "reports" / "subtitle-uploads.json"

# YouTube API language codes mapping from our SRT filename convention
LANG_MAP = {
    "en": "en",
    "es": "es",
    "de": "de",
    "fr": "fr",
    "pt": "pt",
    "ar": "ar",
    "zh-CN": "zh-Hans",
    "ru": "ru",
    "ja": "ja",
    "hi": "hi",
    "ko": "ko",
}

LANG_NAMES = {
    "en": "English",
    "es": "Spanish",
    "de": "German",
    "fr": "French",
    "pt": "Portuguese",
    "ar": "Arabic",
    "zh-CN": "Chinese (Simplified)",
    "ru": "Russian",
    "ja": "Japanese",
    "hi": "Hindi",
    "ko": "Korean",
}


def get_youtube_credentials():
    """Load and refresh YouTube API credentials."""
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if YOUTUBE_TOKEN.exists():
        with open(YOUTUBE_TOKEN, "rb") as f:
            creds = pickle.load(f)

    # Captions API requires youtube.force-ssl scope
    required_scope = "https://www.googleapis.com/auth/youtube.force-ssl"
    needs_reauth = False

    if creds and hasattr(creds, 'scopes') and creds.scopes:
        if required_scope not in creds.scopes:
            print(f"Token missing required scope: {required_scope}")
            print(f"Current scopes: {creds.scopes}")
            needs_reauth = True

    if not creds or not creds.valid or needs_reauth:
        if creds and creds.expired and creds.refresh_token and not needs_reauth:
            creds.refresh(Request())
        else:
            if not YOUTUBE_OAUTH.exists():
                print(f"ERROR: YouTube OAuth credentials not found at {YOUTUBE_OAUTH}")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                str(YOUTUBE_OAUTH),
                scopes=[required_scope],
            )
            creds = flow.run_local_server(port=0)
        with open(YOUTUBE_TOKEN, "wb") as f:
            pickle.dump(creds, f)

    return creds


def load_upload_log():
    """Load the log of previously uploaded subtitles."""
    if UPLOAD_LOG.exists():
        with open(UPLOAD_LOG) as f:
            return json.load(f)
    return {}


def save_upload_log(log):
    """Save the upload log."""
    UPLOAD_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(UPLOAD_LOG, "w") as f:
        json.dump(log, f, indent=2)


def get_existing_captions(youtube, video_id):
    """Get list of existing caption tracks for a video."""
    try:
        response = youtube.captions().list(part="snippet", videoId=video_id).execute()
        return {item["snippet"]["language"]: item["id"] for item in response.get("items", [])}
    except Exception as e:
        print(f"  WARNING: Could not list captions for {video_id}: {e}")
        return {}


def upload_caption(youtube, video_id, lang_code, lang_name, srt_path, existing_captions):
    """Upload or update a caption track for a video."""
    from googleapiclient.http import MediaFileUpload

    yt_lang = LANG_MAP.get(lang_code, lang_code)

    body = {
        "snippet": {
            "videoId": video_id,
            "language": yt_lang,
            "name": lang_name,
            "isDraft": False,
        }
    }

    media = MediaFileUpload(str(srt_path), mimetype="application/x-subrip")

    if yt_lang in existing_captions:
        # Update existing caption
        body["id"] = existing_captions[yt_lang]
        response = youtube.captions().update(
            part="snippet", body=body, media_body=media
        ).execute()
        return "updated", response.get("id", "")
    else:
        # Insert new caption
        response = youtube.captions().insert(
            part="snippet", body=body, media_body=media
        ).execute()
        return "created", response.get("id", "")


def find_srt_files(video_id=None):
    """Find all SRT files to upload, grouped by video ID."""
    results = {}

    if video_id:
        video_dir = TRANSCRIPTIONS_DIR / video_id
        if not video_dir.exists():
            print(f"ERROR: No transcription directory for video {video_id}")
            return {}
        dirs = [video_dir]
    else:
        dirs = sorted(TRANSCRIPTIONS_DIR.iterdir())

    for d in dirs:
        if not d.is_dir():
            continue
        vid = d.name
        srt_files = {}
        for srt in sorted(d.glob("subtitles.*.srt")):
            # Extract language code from filename like subtitles.es.srt
            lang = srt.stem.replace("subtitles.", "")
            if lang in LANG_MAP:
                srt_files[lang] = srt
        if srt_files:
            results[vid] = srt_files

    return results


def main():
    parser = argparse.ArgumentParser(description="Upload SRT subtitles to YouTube")
    parser.add_argument("--dry-run", action="store_true", help="Preview without uploading")
    parser.add_argument("--video", help="Upload subtitles for a specific video ID only")
    parser.add_argument("--skip-english", action="store_true", help="Skip English subtitles (YouTube auto-generates these)")
    parser.add_argument("--languages", help="Comma-separated language codes to upload (e.g. es,de,fr)")
    args = parser.parse_args()

    # Find all SRT files
    srt_files = find_srt_files(video_id=args.video)

    if not srt_files:
        print("No SRT files found to upload.")
        return

    # Filter languages if specified
    target_langs = None
    if args.languages:
        target_langs = set(args.languages.split(","))

    # Default: skip English (YouTube auto-generates it and our English SRT may conflict)
    if args.skip_english is None:
        args.skip_english = True

    # Count totals
    total_uploads = 0
    for vid, langs in srt_files.items():
        for lang in langs:
            if args.skip_english and lang == "en":
                continue
            if target_langs and lang not in target_langs:
                continue
            total_uploads += 1

    print(f"Found {len(srt_files)} videos with SRT files ({total_uploads} subtitle tracks to upload)")
    print()

    if args.dry_run:
        print("DRY RUN — no uploads will be made\n")
        for vid, langs in sorted(srt_files.items()):
            filtered = {k: v for k, v in langs.items()
                       if not (args.skip_english and k == "en")
                       and not (target_langs and k not in target_langs)}
            if filtered:
                lang_list = ", ".join(sorted(filtered.keys()))
                print(f"  {vid}: {lang_list}")
        print(f"\nTotal: {total_uploads} subtitle tracks across {len(srt_files)} videos")
        return

    # Authenticate
    print("Authenticating with YouTube API...")
    creds = get_youtube_credentials()

    from googleapiclient.discovery import build
    youtube = build("youtube", "v3", credentials=creds)
    print("Authenticated.\n")

    # Load upload log
    upload_log = load_upload_log()

    uploaded = 0
    skipped = 0
    errors = 0

    for vid, langs in sorted(srt_files.items()):
        # Filter languages
        filtered_langs = {k: v for k, v in langs.items()
                         if not (args.skip_english and k == "en")
                         and not (target_langs and k not in target_langs)}

        if not filtered_langs:
            continue

        # Check if already uploaded
        vid_log = upload_log.get(vid, {})
        pending_langs = {}
        for lang, path in filtered_langs.items():
            if lang in vid_log:
                skipped += 1
            else:
                pending_langs[lang] = path

        if not pending_langs:
            continue

        print(f"Video {vid}: uploading {len(pending_langs)} subtitle tracks...")

        # Get existing captions for this video
        existing = get_existing_captions(youtube, vid)

        for lang, srt_path in sorted(pending_langs.items()):
            lang_name = LANG_NAMES.get(lang, lang)
            try:
                action, caption_id = upload_caption(
                    youtube, vid, lang, lang_name, srt_path, existing
                )
                print(f"  {action} {lang} ({lang_name}) — caption ID: {caption_id}")

                # Log success
                if vid not in upload_log:
                    upload_log[vid] = {}
                upload_log[vid][lang] = {
                    "caption_id": caption_id,
                    "action": action,
                    "uploaded_at": datetime.now().isoformat(),
                }
                save_upload_log(upload_log)
                uploaded += 1

                # Respect API rate limits
                time.sleep(0.5)

            except Exception as e:
                error_str = str(e)
                print(f"  ERROR uploading {lang} for {vid}: {error_str}")
                errors += 1

                # If quota exceeded, stop
                if "quotaExceeded" in error_str or "rateLimitExceeded" in error_str:
                    print("\nAPI quota exceeded. Stopping. Run again later to continue.")
                    save_upload_log(upload_log)
                    print(f"\nResults: {uploaded} uploaded, {skipped} skipped (already done), {errors} errors")
                    return

                time.sleep(1)

    save_upload_log(upload_log)
    print(f"\nDone! {uploaded} uploaded, {skipped} skipped (already done), {errors} errors")


if __name__ == "__main__":
    main()
