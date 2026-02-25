#!/usr/bin/env python3
"""
Auto-pin channel owner comments on YouTube Studio using Playwright.

On first run, opens a browser for you to log into YouTube Studio manually.
Your session is saved so subsequent runs are automatic.

Reads from reports/video-comments.json (created by post_video_comments.py)
to know which videos have owner comments that need pinning.

Usage:
    python3 tools/pin_youtube_comments.py --login         # first-time login (saves session)
    python3 tools/pin_youtube_comments.py --dry-run       # preview what would be pinned
    python3 tools/pin_youtube_comments.py                  # pin all unfinished comments
    python3 tools/pin_youtube_comments.py --video VIDEO_ID # pin one video only
    python3 tools/pin_youtube_comments.py --limit 50       # pin up to 50 videos

Requires: pip3 install playwright && python3 -m playwright install chromium
"""

import sys
import os
import json
import time
import argparse
import pathlib
from datetime import datetime

if sys.platform == "darwin":
    sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

PROJECT_DIR = pathlib.Path(__file__).parent.parent
COMMENT_LOG = PROJECT_DIR / "reports" / "video-comments.json"
SESSION_FILE = PROJECT_DIR / "data" / "youtube-studio-session.json"
STUDIO_BASE = "https://studio.youtube.com"

# Delay between actions (seconds) — keeps it human-like
ACTION_DELAY = 1.5
PAGE_LOAD_DELAY = 3


def load_comment_log():
    if COMMENT_LOG.exists():
        return json.load(open(COMMENT_LOG))
    return {}


def save_comment_log(log):
    COMMENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(COMMENT_LOG, "w") as f:
        json.dump(log, f, indent=2)


def do_login():
    """Open browser for manual YouTube Studio login, then save session."""
    from playwright.sync_api import sync_playwright

    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("Opening browser for YouTube Studio login...")
    print("Log in with your Google account, then close the browser when done.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.goto(f"{STUDIO_BASE}/channel/videos")

        print("Waiting for you to log in...")
        print("Once you see YouTube Studio dashboard, press Enter here to save session.")
        input("\n>>> Press Enter after logging in: ")

        # Save session state
        context.storage_state(path=str(SESSION_FILE))
        print(f"\nSession saved to {SESSION_FILE}")
        browser.close()

    print("Done! You can now run the pin script without --login.")


def pin_comment_on_video(page, video_id):
    """Navigate to a video's comments in Studio and pin the owner comment.

    Returns: 'pinned', 'already_pinned', 'not_found', or 'error'
    """
    url = f"{STUDIO_BASE}/video/{video_id}/comments"
    page.goto(url)
    time.sleep(PAGE_LOAD_DELAY)

    # Wait for comments to load
    try:
        page.wait_for_selector("#comments-list, ytcp-comment-thread", timeout=10000)
    except Exception:
        # Try alternative: might be empty or different layout
        pass

    time.sleep(ACTION_DELAY)

    # Check if there's already a pinned comment (look for pin icon/badge)
    pinned = page.query_selector_all(
        "[pinned-badge], .pinned-badge, .ytcp-pinned-comment-badge, "
        "[icon=pin], .pin-icon"
    )
    if pinned:
        return "already_pinned"

    # Find all comment threads — look for the one with the owner badge
    # YouTube Studio marks channel owner comments with a specific badge/class
    owner_selectors = [
        "ytcp-comment-thread:has(.owner-badge)",
        "ytcp-comment-thread:has([owner])",
        "#comments-list .comment-thread:has(.owner)",
        "ytcp-comment-thread:has(.ytcp-badge--owner)",
    ]

    owner_thread = None
    for sel in owner_selectors:
        try:
            owner_thread = page.query_selector(sel)
            if owner_thread:
                break
        except Exception:
            continue

    if not owner_thread:
        # Fallback: look for any comment with owner-like indicators
        threads = page.query_selector_all("ytcp-comment-thread, .comment-thread")
        for thread in threads:
            html = thread.inner_html()
            if "owner" in html.lower() or "badge" in html.lower():
                owner_thread = thread
                break

    if not owner_thread:
        return "not_found"

    # Click the three-dot menu on the owner comment
    menu_selectors = [
        "ytcp-icon-button#overflow-menu-button",
        "#overflow-menu-button",
        "[aria-label='More actions']",
        "button.overflow-menu",
        ".more-actions-button",
    ]

    menu_btn = None
    for sel in menu_selectors:
        try:
            menu_btn = owner_thread.query_selector(sel)
            if menu_btn:
                break
        except Exception:
            continue

    if not menu_btn:
        # Try hovering first — menu might appear on hover
        try:
            owner_thread.hover()
            time.sleep(0.5)
            for sel in menu_selectors:
                menu_btn = owner_thread.query_selector(sel)
                if menu_btn:
                    break
        except Exception:
            pass

    if not menu_btn:
        return "error"

    menu_btn.click()
    time.sleep(ACTION_DELAY)

    # Click "Pin" from the dropdown menu
    pin_selectors = [
        "tp-yt-paper-item:has-text('Pin')",
        "[test-id='pin']",
        "ytcp-text-menu tp-yt-paper-item:has-text('Pin')",
        ".ytcp-text-menu tp-yt-paper-item >> text=Pin",
    ]

    pin_btn = None
    for sel in pin_selectors:
        try:
            pin_btn = page.query_selector(sel)
            if pin_btn:
                break
        except Exception:
            continue

    if not pin_btn:
        # Try clicking by text content directly
        try:
            page.click("text=Pin", timeout=3000)
        except Exception:
            return "error"
    else:
        pin_btn.click()

    time.sleep(ACTION_DELAY)

    # Confirm the pin dialog (YouTube shows a confirmation)
    confirm_selectors = [
        "#confirm-button",
        "ytcp-button#confirm-button",
        "[label='Pin']",
        "button:has-text('Pin')",
        ".confirm-dialog button:has-text('Pin')",
    ]

    for sel in confirm_selectors:
        try:
            confirm = page.query_selector(sel)
            if confirm:
                confirm.click()
                time.sleep(ACTION_DELAY)
                return "pinned"
        except Exception:
            continue

    # If no confirm dialog, the pin might have been applied directly
    return "pinned"


def main():
    parser = argparse.ArgumentParser(description="Auto-pin YouTube comments via Studio")
    parser.add_argument("--login", action="store_true",
                        help="Open browser to log in and save session")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without pinning")
    parser.add_argument("--video", help="Pin comment on a specific video only")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max number of videos to process (0 = all)")
    parser.add_argument("--headless", action="store_true",
                        help="Run in headless mode (no visible browser)")
    args = parser.parse_args()

    if args.login:
        do_login()
        return

    # Check session exists
    if not SESSION_FILE.exists():
        print(f"No session file found at {SESSION_FILE}")
        print("Run with --login first to authenticate with YouTube Studio.")
        sys.exit(1)

    # Load comment log
    comment_log = load_comment_log()
    if not comment_log:
        print("No comments found in log. Run post_video_comments.py first.")
        sys.exit(1)

    # Get videos that need pinning
    if args.video:
        to_pin = {args.video: comment_log.get(args.video, {})}
    else:
        to_pin = {
            vid: data for vid, data in comment_log.items()
            if data.get("status") == "posted" and not data.get("pinned")
        }

    if not to_pin:
        print("No unpinned comments found. All done!")
        return

    total = len(to_pin)
    if args.limit > 0:
        to_pin = dict(list(to_pin.items())[:args.limit])

    print(f"Videos to pin: {len(to_pin)}" + (f" (of {total} total)" if args.limit else ""))

    if args.dry_run:
        print("\nDRY RUN — no pinning will happen\n")
        for vid in to_pin:
            print(f"  Would pin: {vid}")
        return

    from playwright.sync_api import sync_playwright

    print("Launching browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context(
            storage_state=str(SESSION_FILE),
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        # Quick check: navigate to Studio to verify session is valid
        page.goto(f"{STUDIO_BASE}/channel/videos")
        time.sleep(PAGE_LOAD_DELAY)
        if "accounts.google.com" in page.url:
            print("Session expired! Run with --login to re-authenticate.")
            browser.close()
            sys.exit(1)

        print("Session valid. Starting pin process...\n")

        pinned = 0
        skipped = 0
        errors = 0

        for i, (vid_id, data) in enumerate(to_pin.items(), 1):
            print(f"  [{i}/{len(to_pin)}] {vid_id}: ", end="", flush=True)

            try:
                result = pin_comment_on_video(page, vid_id)
                print(result.upper())

                if result == "pinned":
                    comment_log[vid_id]["pinned"] = True
                    comment_log[vid_id]["pinned_at"] = datetime.now().isoformat()
                    save_comment_log(comment_log)
                    pinned += 1
                elif result == "already_pinned":
                    comment_log[vid_id]["pinned"] = True
                    comment_log[vid_id]["pinned_at"] = "pre-existing"
                    save_comment_log(comment_log)
                    skipped += 1
                elif result == "not_found":
                    skipped += 1
                else:
                    errors += 1

                # Human-like delay between videos
                time.sleep(ACTION_DELAY * 2)

            except Exception as e:
                print(f"ERROR — {str(e)[:80]}")
                errors += 1
                time.sleep(2)

        # Save session state (in case cookies were refreshed)
        context.storage_state(path=str(SESSION_FILE))
        browser.close()

    print(f"\nDone: {pinned} pinned, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
