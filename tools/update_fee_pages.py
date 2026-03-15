#!/usr/bin/env python3
"""
Update Fee Pages — bridges weekly scraper to live site.

After scrape_platform_fees.py updates data/platform-fees.json, this script
checks if the committed copy has changed and either:
  - Auto-commits + pushes (if git remote is configured with deploy key), or
  - Alerts Tom via Telegram that fees changed and need a push.

Usage:
    python3 tools/update_fee_pages.py            # Check + commit if possible
    python3 tools/update_fee_pages.py --dry-run   # Check only, don't commit

Chain after scraper in cron:
    0 2 * * 1  PYTHON scraper && PYTHON update_fee_pages.py

Architecture:
    scrape_platform_fees.py → data/platform-fees.json (updated)
    update_fee_pages.py     → git add + commit + push (or Telegram alert)
    GitHub Pages            → serves the updated JSON at /data/platform-fees.json
    trade-comparison/       → fetch('/data/platform-fees.json') on page load
"""

import sys
import os
import json
import pathlib
import subprocess
import argparse
from datetime import datetime

PROJECT_DIR = pathlib.Path(__file__).parent.parent
FEES_FILE = PROJECT_DIR / "data" / "platform-fees.json"

def send_telegram(subject, body):
    """Send alert via security_lib (rate-limited, deduped)."""
    try:
        sys.path.insert(0, str(PROJECT_DIR / "tools"))
        from security_lib import send_telegram as _send
        _send(subject, body, emoji="📊")
    except Exception as e:
        print(f"  Telegram alert failed: {e}")

def run_git(*args):
    """Run a git command in the project directory."""
    result = subprocess.run(
        ["git"] + list(args),
        cwd=str(PROJECT_DIR),
        capture_output=True, text=True, timeout=30
    )
    return result

def main():
    parser = argparse.ArgumentParser(description="Update fee data on live site")
    parser.add_argument("--dry-run", action="store_true", help="Check only, don't commit")
    args = parser.parse_args()

    if not FEES_FILE.exists():
        print("ERROR: data/platform-fees.json not found. Run scrape_platform_fees.py first.")
        sys.exit(1)

    data = json.loads(FEES_FILE.read_text())
    updated = data.get("_last_updated", "unknown")
    platform_count = len(data.get("platforms", {}))
    print(f"Fee data updated: {updated} ({platform_count} platforms)")

    # Check if we're in a git repo — VPS copy is NOT a git repo (synced via rsync)
    is_git = run_git("rev-parse", "--git-dir").returncode == 0

    if not is_git:
        # VPS environment — just alert Tom that data was updated
        print("Not a git repo (VPS) — sending Telegram alert only.")
        if not args.dry_run:
            send_telegram(
                "Fee Data Updated on VPS",
                f"Platform fees scraped and JSON updated on VPS.\n"
                f"Date: {updated}\nPlatforms: {platform_count}\n\n"
                f"Data will go live next time local repo is synced and pushed."
            )
        return

    # Git repo (local Mac) — check for changes and commit
    diff = run_git("diff", "--name-only", "data/platform-fees.json", "data/platform-verified.json")
    if not diff.stdout.strip():
        print("Fee data unchanged — nothing to update.")
        return

    if args.dry_run:
        print("Dry run — would commit and push.")
        print(f"  Changed files: {diff.stdout.strip()}")
        return

    # Stage the files
    stage = run_git("add", "data/platform-fees.json", "data/platform-verified.json")
    if stage.returncode != 0:
        print(f"ERROR: git add failed: {stage.stderr}")
        sys.exit(1)

    # Commit
    msg = f"Update platform fee data ({updated})\n\nWeekly fee verification by scrape_platform_fees.py.\n{platform_count} platforms checked."
    commit = run_git("commit", "-m", msg)
    if commit.returncode != 0:
        print(f"ERROR: git commit failed: {commit.stderr}")
        sys.exit(1)
    print(f"Committed: {msg.splitlines()[0]}")

    # Try to push
    push = run_git("push")
    if push.returncode == 0:
        print("Pushed to remote successfully.")
        send_telegram(
            "Fee Data Updated",
            f"Platform fees verified and pushed to live site.\n"
            f"Date: {updated}\nPlatforms: {platform_count}"
        )
    else:
        print(f"Push failed: {push.stderr.strip()}")
        send_telegram(
            "Fee Data Updated — Push Needed",
            f"Platform fees have been verified and committed locally.\n"
            f"Date: {updated}\nPlatforms: {platform_count}\n\n"
            f"Run: cd ~/socialtradingvlog-website && git push"
        )

if __name__ == "__main__":
    main()
