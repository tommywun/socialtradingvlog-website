#!/usr/bin/env python3
"""
Post comments on YouTube videos as the channel owner.

Scans all videos and:
  - Videos with NO pinned comment: posts our comment directly
  - Videos WITH an existing pinned comment: adds to a review queue on the CC
    for Tom to decide (leave existing or replace with one of 3 templates)
  - Videos where we've already posted: skips

Note: The YouTube Data API does NOT support pinning comments programmatically.
Use pin_youtube_comments.py (Playwright) to pin after posting.

Usage:
    python3 tools/post_video_comments.py --dry-run          # preview
    python3 tools/post_video_comments.py                     # scan + post + queue
    python3 tools/post_video_comments.py --video VIDEO_ID    # one video only
    python3 tools/post_video_comments.py --scan-only         # only scan for pinned, don't post

Quota: commentThreads.list = 1 unit, commentThreads.insert = 50 units.
"""

import sys
import os
import pathlib
import pickle
import argparse
import json
import time
import re
from datetime import datetime

if sys.platform == "darwin":
    sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
YOUTUBE_TOKEN = SECRETS_DIR / "youtube-token.pickle"
YOUTUBE_OAUTH = SECRETS_DIR / "youtube-oauth.json"
PROJECT_DIR = pathlib.Path(__file__).parent.parent
COMMENT_LOG = PROJECT_DIR / "reports" / "video-comments.json"
PINNED_QUEUE = PROJECT_DIR / "data" / "pinned-comment-queue.json"

# ─── Comment Templates ──────────────────────────────────────────────────────
# These are the 3 options Tom can choose from in the CC review queue.
# Each has an id, label (shown in CC), and the full comment text.

COMMENT_TEMPLATES = {
    "calculator": {
        "label": "Free Tools (Calculators)",
        "message": (
            "Try my free eToro tools \u2014 built from years of experience on the platform:\n\n"
            "\ud83d\udcca Fee Calculator \u2014 see exactly what you'll pay in spreads, overnight & withdrawal fees\n"
            "\ud83d\udcc8 ROI Calculator \u2014 project your copy trading returns over time\n"
            "\ud83d\udccf Position Size Calculator \u2014 work out how much to allocate per trader\n\n"
            "\u27a1\ufe0f https://www.socialtradingvlog.com/calculators/"
        ),
    },
    "comparison": {
        "label": "Platform Comparison",
        "message": (
            "Thinking about which trading platform is best for you?\n\n"
            "I've compared eToro vs Trading 212, Interactive Brokers & more \u2014 "
            "fees, features, pros and cons side by side:\n\n"
            "\u27a1\ufe0f https://www.socialtradingvlog.com/compare-trading-platforms\n\n"
            "Free tools: Fee Calculator, ROI Calculator, Position Sizer\n"
            "\u27a1\ufe0f https://www.socialtradingvlog.com/calculators/"
        ),
    },
    "how-much": {
        "label": "How Much Will I Make?",
        "message": (
            "Want to know how much you can realistically make copy trading?\n\n"
            "I break down the maths \u2014 what good traders actually return, "
            "why your starting amount matters more than you think, and how compound growth works:\n\n"
            "\u27a1\ufe0f https://www.socialtradingvlog.com/video/how-much-money-can-i-make-copy-trading-etoro\n\n"
            "Try the ROI Calculator to see your projected returns:\n"
            "\u27a1\ufe0f https://www.socialtradingvlog.com/calculators/"
        ),
    },
}

# Default template for videos with no existing pinned comment
DEFAULT_TEMPLATE = "calculator"

QUOTA_PER_LIST = 1
QUOTA_PER_INSERT = 50


def get_youtube_credentials():
    """Load and refresh YouTube API credentials."""
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if YOUTUBE_TOKEN.exists():
        with open(YOUTUBE_TOKEN, "rb") as f:
            creds = pickle.load(f)

    required_scope = "https://www.googleapis.com/auth/youtube.force-ssl"
    needs_reauth = False

    if creds and hasattr(creds, 'scopes') and creds.scopes:
        if required_scope not in creds.scopes:
            print(f"Token missing required scope: {required_scope}")
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


def load_comment_log():
    if COMMENT_LOG.exists():
        return json.load(open(COMMENT_LOG))
    return {}


def save_comment_log(log):
    COMMENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(COMMENT_LOG, "w") as f:
        json.dump(log, f, indent=2)


def load_pinned_queue():
    if PINNED_QUEUE.exists():
        return json.load(open(PINNED_QUEUE))
    return {}


def save_pinned_queue(queue):
    PINNED_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    with open(PINNED_QUEUE, "w") as f:
        json.dump(queue, f, indent=2)


def get_channel_id(youtube):
    response = youtube.channels().list(part="id", mine=True).execute()
    items = response.get("items", [])
    if not items:
        print("ERROR: Could not determine channel ID")
        sys.exit(1)
    return items[0]["id"]


def check_video_comments(youtube, video_id, channel_id):
    """Check a video's comment state.

    Returns a dict with:
      has_pinned: bool
      pinned_text: str or None
      pinned_author: str or None
      has_our_comment: bool
      comments_disabled: bool
    """
    result = {
        "has_pinned": False,
        "pinned_text": None,
        "pinned_author": None,
        "has_our_comment": False,
        "comments_disabled": False,
    }

    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
        ).execute()

        for thread in response.get("items", []):
            snippet = thread["snippet"]
            comment = snippet["topLevelComment"]["snippet"]

            # Check for pinned
            if snippet.get("snippet", {}).get("isPinned") or comment.get("isPinned"):
                result["has_pinned"] = True
                result["pinned_text"] = comment.get("textOriginal", comment.get("textDisplay", ""))
                result["pinned_author"] = comment.get("authorDisplayName", "")

            # Check for our comment
            if comment.get("authorChannelId", {}).get("value") == channel_id:
                result["has_our_comment"] = True

    except Exception as e:
        if "commentsDisabled" in str(e):
            result["comments_disabled"] = True
        else:
            print(f"  WARNING: Could not check {video_id}: {e}")

    return result


def post_comment(youtube, video_id, message):
    body = {
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {
                "snippet": {
                    "textOriginal": message,
                }
            }
        }
    }
    response = youtube.commentThreads().insert(
        part="snippet",
        body=body,
    ).execute()
    return response.get("id", "")


def get_all_video_ids():
    videos_html = PROJECT_DIR / "videos.html"
    content = videos_html.read_text(encoding="utf-8")
    ids = re.findall(r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})', content)
    seen = set()
    unique = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            unique.append(i)
    return unique


def main():
    parser = argparse.ArgumentParser(description="Post comments on YouTube videos")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--scan-only", action="store_true",
                        help="Only scan for existing pinned comments, don't post anything")
    parser.add_argument("--video", help="Process a specific video ID only")
    parser.add_argument("--template", choices=list(COMMENT_TEMPLATES.keys()),
                        default=DEFAULT_TEMPLATE,
                        help="Comment template to use (default: calculator)")
    parser.add_argument("--quota-limit", type=int, default=5000,
                        help="Max quota units to use (default 5000)")
    args = parser.parse_args()

    template = COMMENT_TEMPLATES[args.template]
    message = template["message"]
    max_inserts = args.quota_limit // QUOTA_PER_INSERT

    # Get video IDs
    video_ids = [args.video] if args.video else get_all_video_ids()

    print(f"Videos: {len(video_ids)}")
    print(f"Template: {template['label']}")
    if not args.scan_only:
        print(f"Quota limit: {args.quota_limit} units ({max_inserts} posts max)")
    print()

    if args.dry_run:
        print("DRY RUN \u2014 no comments will be posted\n")
    if args.scan_only:
        print("SCAN ONLY \u2014 checking for existing pinned comments\n")

    comment_log = load_comment_log()
    pinned_queue = load_pinned_queue()

    if not args.dry_run:
        print("Authenticating with YouTube API...")
        creds = get_youtube_credentials()
        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", credentials=creds)
        channel_id = get_channel_id(youtube)
        print(f"Channel ID: {channel_id}\n")
    else:
        youtube = None
        channel_id = None

    posted = 0
    queued = 0
    skipped = 0
    errors = 0

    for i, vid_id in enumerate(video_ids, 1):
        # Skip if we've already posted our comment on this video
        if vid_id in comment_log and comment_log[vid_id].get("status") == "posted":
            skipped += 1
            continue

        # Skip if already in pinned queue and reviewed
        if vid_id in pinned_queue and pinned_queue[vid_id].get("decision"):
            skipped += 1
            continue

        if not args.scan_only and posted >= max_inserts:
            print(f"\nQuota limit reached. Run again later to continue.")
            break

        if args.dry_run:
            print(f"  [{i}/{len(video_ids)}] {vid_id}: would scan + process")
            continue

        # Check this video's comment state
        state = check_video_comments(youtube, vid_id, channel_id)

        if state["comments_disabled"]:
            print(f"  [{i}/{len(video_ids)}] {vid_id}: SKIP (comments disabled)")
            comment_log[vid_id] = {"status": "comments_disabled",
                                   "checked_at": datetime.now().isoformat()}
            save_comment_log(comment_log)
            skipped += 1
            time.sleep(0.3)
            continue

        if state["has_our_comment"]:
            print(f"  [{i}/{len(video_ids)}] {vid_id}: SKIP (already has our comment)")
            comment_log[vid_id] = {"status": "posted",
                                   "checked_at": datetime.now().isoformat(),
                                   "note": "found existing owner comment during scan"}
            save_comment_log(comment_log)
            skipped += 1
            time.sleep(0.3)
            continue

        if state["has_pinned"]:
            # Add to review queue for Tom to decide
            print(f"  [{i}/{len(video_ids)}] {vid_id}: QUEUED (has pinned comment from {state['pinned_author']})")
            pinned_queue[vid_id] = {
                "pinned_text": state["pinned_text"],
                "pinned_author": state["pinned_author"],
                "queued_at": datetime.now().isoformat(),
                "decision": None,  # Tom will set: "leave" or "change"
                "template": None,  # If "change", which template
            }
            save_pinned_queue(pinned_queue)
            queued += 1
            time.sleep(0.3)
            continue

        # No pinned comment, no existing owner comment — post our comment
        if args.scan_only:
            print(f"  [{i}/{len(video_ids)}] {vid_id}: WOULD POST (no pinned comment)")
            posted += 1
            time.sleep(0.3)
            continue

        try:
            comment_id = post_comment(youtube, vid_id, message)
            print(f"  [{i}/{len(video_ids)}] {vid_id}: POSTED ({template['label']})")
            comment_log[vid_id] = {
                "status": "posted",
                "comment_id": comment_id,
                "template": args.template,
                "message": message,
                "posted_at": datetime.now().isoformat(),
            }
            save_comment_log(comment_log)
            posted += 1
            time.sleep(0.5)

        except Exception as e:
            error_str = str(e)
            print(f"  [{i}/{len(video_ids)}] {vid_id}: ERROR \u2014 {error_str[:100]}")
            errors += 1
            if "quotaExceeded" in error_str or "rateLimitExceeded" in error_str:
                print("\nAPI quota exceeded. Run again later.")
                break
            time.sleep(1)

    action = "scanned" if args.scan_only else "posted"
    print(f"\nDone: {posted} {action}, {queued} queued for review, "
          f"{skipped} skipped, {errors} errors")
    if queued > 0:
        print(f"Review queue saved to {PINNED_QUEUE}")
        print("Check the CC dashboard To Do section to review pinned comments.")


if __name__ == "__main__":
    main()
