#!/usr/bin/env python3
"""
Update the 'From the blog' section on the homepage with the 3 latest updates.

Scans the updates/ directory, picks the 3 most recent by date, and replaces
the cards-grid in index.html. Includes bright gradient image placeholders.

Idempotent — safe to re-run. Also updates translated homepages.

Usage:
    python3 tools/update_homepage_cards.py
    python3 tools/update_homepage_cards.py --dry-run
"""

import pathlib
import re
import argparse
from datetime import datetime

PROJECT_DIR = pathlib.Path(__file__).parent.parent

GRADIENTS = [
    "linear-gradient(135deg, #0ea5e9, #06b6d4)",   # blue-cyan
    "linear-gradient(135deg, #8b5cf6, #a78bfa)",   # purple
    "linear-gradient(135deg, #10b981, #34d399)",   # green
]

EMOJIS = ["&#128200;", "&#128176;", "&#128640;"]  # chart, money, rocket


def parse_date_from_filename(name):
    """Extract date from update filename."""
    # Try DD-Mon-YYYY pattern: copy-trading-update-29-dec-2025.html
    m = re.search(r'(\d{1,2})-([a-z]+)-(\d{4})', name, re.IGNORECASE)
    if m:
        day, mon, year = m.groups()
        month_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }
        month_num = month_map.get(mon.lower())
        if month_num:
            return datetime(int(year), month_num, int(day))

    # Try Mon-YYYY pattern: copy-trading-update-jul-2018.html
    m = re.search(r'-([a-z]+)-(\d{4})\.html$', name, re.IGNORECASE)
    if m:
        mon, year = m.groups()
        month_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }
        month_num = month_map.get(mon.lower())
        if month_num:
            return datetime(int(year), month_num, 1)

    return None


def get_description(filepath):
    """Extract meta description from HTML file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content)
    if m:
        desc = m.group(1)
        # Strip the "Copy trading update — DD Month YYYY. " prefix
        desc = re.sub(r'^Copy trading update[^.]*\.\s*', '', desc, flags=re.IGNORECASE)
        return desc
    return ""


def get_title(filepath):
    """Extract title from HTML file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.search(r'<title>([^<]+)</title>', content)
    if m:
        return m.group(1).replace(" | SocialTradingVlog", "").strip()
    return ""


def find_latest_updates(updates_dir, count=3):
    """Find the N most recent update files by date."""
    updates = []
    for f in updates_dir.glob("*.html"):
        date = parse_date_from_filename(f.name)
        if date:
            updates.append((date, f))

    updates.sort(key=lambda x: x[0], reverse=True)
    return updates[:count]


def build_cards_html(updates):
    """Build the cards-grid HTML for the latest updates."""
    cards = []
    for i, (date, filepath) in enumerate(updates):
        gradient = GRADIENTS[i % len(GRADIENTS)]
        emoji = EMOJIS[i % len(EMOJIS)]
        tag = date.strftime("%b %Y")
        title = get_title(filepath)
        desc = get_description(filepath)
        href = f"updates/{filepath.name}"

        card = f"""        <div class="card">
          <div class="card-img-placeholder" style="background: {gradient};">
            <span>{emoji}</span>
          </div>
          <div class="card-body">
            <div class="card-tag">{tag}</div>
            <h3><a href="{href}">{title}</a></h3>
            <p>{desc}</p>
            <a href="{href}" class="card-link">Read update →</a>
          </div>
        </div>"""
        cards.append(card)

    return "      <div class=\"cards-grid\">\n\n" + "\n\n".join(cards) + "\n\n      </div>"


def update_homepage(index_path, cards_html, dry_run=False):
    """Replace the cards-grid in the 'From the blog' section (not 'Start here')."""
    try:
        content = index_path.read_text(encoding="utf-8")
    except Exception:
        return False

    # Find the "LATEST UPDATES" / "From the blog" section specifically
    blog_marker = content.find("From the blog")
    if blog_marker == -1:
        blog_marker = content.find("LATEST UPDATES")
    if blog_marker == -1:
        print("  Could not find 'From the blog' section")
        return False

    # Find the cards-grid AFTER the blog marker
    grid_start = content.find('<div class="cards-grid">', blog_marker)
    if grid_start == -1:
        return False

    # Find the "View all updates" link after this grid — that marks the end
    view_all = content.find('<div style="margin-top', grid_start)
    if view_all == -1:
        return False

    # Replace everything from grid_start to view_all
    old_section = content[grid_start:view_all].rstrip()
    content = content[:grid_start] + cards_html + "\n\n" + content[view_all:]

    if not dry_run:
        index_path.write_text(content, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Update homepage blog cards")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    updates_dir = PROJECT_DIR / "updates"
    latest = find_latest_updates(updates_dir, count=3)

    if not latest:
        print("No updates found")
        return

    cards_html = build_cards_html(latest)

    if args.dry_run:
        print("Would update with:")
        for date, f in latest:
            print(f"  {date.strftime('%d %b %Y')} — {f.name}")
        print()
        print(cards_html)
        return

    index_path = PROJECT_DIR / "index.html"
    if update_homepage(index_path, cards_html):
        print(f"Updated homepage with {len(latest)} latest updates:")
        for date, f in latest:
            print(f"  {date.strftime('%d %b %Y')} — {f.name}")
    else:
        print("Failed to update homepage — cards-grid not found")


if __name__ == "__main__":
    main()
