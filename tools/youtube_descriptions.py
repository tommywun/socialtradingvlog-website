#!/usr/bin/env python3
"""
Update YouTube video descriptions with links to socialtradingvlog.com articles.

IMPORTANT: This script PRESERVES existing description content (disclaimers,
affiliate links, etc.) and INSERTS site links after the eToro disclaimer
but before social media links.

Usage:
    python3 tools/youtube_descriptions.py --list          # show all videos
    python3 tools/youtube_descriptions.py --preview       # preview changes (dry run)
    python3 tools/youtube_descriptions.py --update        # apply changes

First run will open a browser for OAuth — approve it with your Google account.
"""

import sys
import os
import re
import json
import pathlib
import argparse
import pickle

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
CLIENT_SECRET = SECRETS_DIR / "youtube-oauth.json"
TOKEN_FILE = SECRETS_DIR / "youtube-token.pickle"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

SITE_URL = "https://socialtradingvlog.com"
SUBSCRIBE_URL = "https://www.youtube.com/@SocialTradingVlog?sub_confirmation=1"
HASHTAGS_ETORO = "#eToro #CopyTrading #Investing"
HASHTAGS_GENERAL = "#Investing #Trading #PersonalFinance"

# Map video IDs to their corresponding article pages on the site.
# Add new entries here when new video articles are published.
VIDEO_ARTICLE_MAP = {
    "daMK1Y54M-E": {
        "article_url": f"{SITE_URL}/video/why-do-most-etoro-traders-lose-money/",
        "label": "Full article: Why Do 76% of eToro Traders Lose Money?",
    },
}

# General site links to add to ALL video descriptions
SITE_LINKS = [
    (f"{SITE_URL}/copy-trading.html", "What is Copy Trading? — Complete Guide"),
    (f"{SITE_URL}/social-trading.html", "What is Social Trading?"),
    (f"{SITE_URL}/copy-trading-returns.html", "How Much Can You Make Copy Trading?"),
    (f"{SITE_URL}/taking-profits.html", "How to Take Profits from Copy Trading"),
    (f"{SITE_URL}/etoro-review/", "eToro Review 2026 — My Honest Experience After 9 Years"),
    (f"{SITE_URL}/faq.html", "FAQ"),
]

# Standard separator line
SEP = "_" * 50


def get_credentials():
    """Get or refresh YouTube API credentials."""
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return creds


def get_youtube():
    """Build authenticated YouTube API client."""
    creds = get_credentials()
    return build("youtube", "v3", credentials=creds)


def get_channel_videos(youtube, max_results=500):
    """Get all videos from the authenticated user's channel."""
    # First get the channel's upload playlist
    channels = youtube.channels().list(part="contentDetails", mine=True).execute()
    if not channels["items"]:
        print("No channel found for this account.")
        return []

    uploads_id = channels["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    next_page = None
    while True:
        req = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_id,
            maxResults=min(max_results - len(videos), 50),
            pageToken=next_page,
        )
        resp = req.execute()
        for item in resp["items"]:
            vid = item["snippet"]
            videos.append({
                "video_id": vid["resourceId"]["videoId"],
                "title": vid["title"],
                "description": vid["description"],
                "published": vid["publishedAt"][:10],
            })
        next_page = resp.get("nextPageToken")
        if not next_page or len(videos) >= max_results:
            break

    return videos


def clean_description(desc):
    """Clean up formatting issues in existing description text."""
    # Standardize all separator lines to consistent length
    desc = re.sub(r'_{10,}', SEP, desc)

    # Fix missing space: "Facebook@" → "Facebook @"
    desc = desc.replace('Facebook@', 'Facebook @')

    # Fix missing space after period: "lose.Past" → "lose. Past"
    desc = desc.replace('lose.Past', 'lose. Past')

    # Fix jammed URL+text: "tomsmetaverseTwitter" → "tomsmetaverse\nTwitter"
    desc = desc.replace('tomsmetaverseTwitter', 'tomsmetaverse\nTwitter')

    # Fix ALL CAPS heading
    desc = desc.replace('MY Metaverse YOUTUBE CHANNEL:', 'My Metaverse YouTube Channel:')

    # Clean up excess blank lines (3+ in a row → 2)
    desc = re.sub(r'\n{4,}', '\n\n\n', desc)

    # Remove trailing whitespace on lines
    desc = re.sub(r'[ \t]+\n', '\n', desc)

    return desc


def build_site_links_block(video_id, compact=False):
    """Build the site links text block.

    If compact=True, only include website + subscribe (for videos near the char limit).
    """
    lines = []

    # Website and subscribe links
    lines.append(f"🌐 Website: {SITE_URL}")
    lines.append(f"🔔 Subscribe: {SUBSCRIBE_URL}")

    if compact:
        return "\n".join(lines)

    lines.append("")

    # Specific article link for this video (if mapped)
    if video_id in VIDEO_ARTICLE_MAP:
        entry = VIDEO_ARTICLE_MAP[video_id]
        lines.append(f"📖 {entry['label']}")
        lines.append(entry["article_url"])
        lines.append("")

    # General site links
    lines.append("📚 Guides on SocialTradingVlog.com:")
    for url, label in SITE_LINKS:
        lines.append(f"  ▸ {label}: {url}")

    return "\n".join(lines)


MARKER = "📚 Guides on SocialTradingVlog.com:"
MARKER_COMPACT = "🌐 Website:"
YT_MAX_DESC = 5000

# Pattern: line of 10+ underscores followed (within a few lines) by social links
SOCIAL_SECTION_RE = re.compile(
    r'\n(_{10,})\s*\n+\s*(Twitter\s*@|Instagram\s*@|Facebook\s*@)',
    re.IGNORECASE,
)


def needs_update(description):
    """Check if description already has our links."""
    return MARKER not in description and MARKER_COMPACT not in description


def find_social_section_start(description):
    """Find the position of the underscore separator before social links.

    Returns the index of the separator line, or -1 if not found.
    """
    m = SOCIAL_SECTION_RE.search(description)
    if m:
        return m.start()
    return -1


def is_etoro_video(description, title=""):
    """Check if a video is eToro-related based on its content."""
    text = (description + " " + title).lower()
    return "etoro" in text


def get_hashtags(description, title=""):
    """Return appropriate hashtags based on video content."""
    if is_etoro_video(description, title):
        return HASHTAGS_ETORO
    return HASHTAGS_GENERAL


def add_hashtags(desc, hashtags):
    """Append hashtags at the very end if not already present."""
    if hashtags in desc:
        return desc
    return desc.rstrip() + "\n\n" + hashtags


def build_new_description(video_id, current_description, title=""):
    """Build updated description: clean up, insert site links, add hashtags."""
    # Step 1: Clean up existing formatting
    desc = clean_description(current_description)

    # Determine correct hashtags based on video content
    hashtags = get_hashtags(current_description, title)

    # Step 2: Try full site links block first
    block = build_site_links_block(video_id, compact=False)
    result = _insert_block(desc, block)

    # Step 3: Add hashtags
    result = add_hashtags(result, hashtags)

    # Step 4: If over limit, fall back to compact block (website + subscribe only)
    if len(result) > YT_MAX_DESC:
        block = build_site_links_block(video_id, compact=True)
        result = _insert_block(desc, block)
        result = add_hashtags(result, hashtags)

    # Step 5: If still over limit, just do cleanup + hashtags (no new links)
    if len(result) > YT_MAX_DESC:
        result = add_hashtags(desc, hashtags)

    # Step 6: If even that's over, just do cleanup only
    if len(result) > YT_MAX_DESC:
        result = desc

    return result


def _insert_block(desc, block):
    """Insert a block after the disclaimer, before social links."""
    social_pos = find_social_section_start(desc)
    if social_pos >= 0:
        before = desc[:social_pos].rstrip()
        after = desc[social_pos:]
        return before + "\n\n" + block + "\n" + after
    else:
        return desc + "\n\n" + SEP + "\n\n" + block


def cmd_list(youtube):
    """List all videos."""
    videos = get_channel_videos(youtube)
    print(f"\nFound {len(videos)} videos:\n")
    for v in videos:
        needs = "✓ needs update" if needs_update(v["description"]) else "  already done"
        print(f"  [{v['published']}] {v['video_id']}  {needs}  {v['title'][:60]}")
    print()


def cmd_preview(youtube):
    """Preview what changes would be made."""
    videos = get_channel_videos(youtube)
    to_update = [v for v in videos if needs_update(v["description"])]
    print(f"\n{len(to_update)} video(s) need updating out of {len(videos)} total.\n")

    for v in to_update:
        new_desc = build_new_description(v["video_id"], v["description"], v["title"])
        print(f"{'=' * 60}")
        print(f"  {v['title']}")
        print(f"  ID: {v['video_id']}")
        print(f"{'=' * 60}")
        # Show the area around the inserted site links
        marker_pos = new_desc.find(MARKER)
        if marker_pos >= 0:
            # Show 200 chars before and 200 chars after the marker block
            start = max(0, marker_pos - 200)
            end = min(len(new_desc), marker_pos + 500)
            if start > 0:
                print("  [... earlier description preserved ...]\n")
            print(new_desc[start:end])
            if end < len(new_desc):
                print("\n  [... rest of description preserved ...]")
        print()


def cmd_update(youtube):
    """Apply description updates."""
    videos = get_channel_videos(youtube)
    to_update = [v for v in videos if needs_update(v["description"])]
    print(f"\n{len(to_update)} video(s) to update.\n")

    updated = 0
    for v in to_update:
        new_desc = build_new_description(v["video_id"], v["description"], v["title"])

        try:
            # YouTube API requires full video resource for update
            video_resp = youtube.videos().list(
                part="snippet", id=v["video_id"]
            ).execute()

            if not video_resp["items"]:
                print(f"  SKIP {v['video_id']} — could not fetch details")
                continue

            video_resource = video_resp["items"][0]
            video_resource["snippet"]["description"] = new_desc
            # categoryId is required for update
            if "categoryId" not in video_resource["snippet"]:
                video_resource["snippet"]["categoryId"] = "22"  # People & Blogs

            youtube.videos().update(
                part="snippet",
                body=video_resource
            ).execute()

            updated += 1
            print(f"  UPDATED {v['video_id']}  {v['title'][:50]}")

        except Exception as e:
            err = str(e)
            if "quotaExceeded" in err:
                print(f"\n  API quota exceeded after {updated} updates.")
                print(f"  {len(to_update) - updated} videos remaining — re-run after quota resets (midnight PT).")
                return
            else:
                print(f"  ERROR {v['video_id']}: {err[:100]}")
                continue

    print(f"\nDone — {updated} video(s) updated.")


def main():
    parser = argparse.ArgumentParser(description="Update YouTube descriptions with site links")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List all videos")
    group.add_argument("--preview", action="store_true", help="Preview changes (dry run)")
    group.add_argument("--update", action="store_true", help="Apply changes")
    args = parser.parse_args()

    youtube = get_youtube()

    if args.list:
        cmd_list(youtube)
    elif args.preview:
        cmd_preview(youtube)
    elif args.update:
        cmd_update(youtube)


if __name__ == "__main__":
    main()
