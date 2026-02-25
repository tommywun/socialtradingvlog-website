#!/usr/bin/env python3
"""
Weekly eToro Risk Percentage Checker.

Scrapes eToro's site for the current "X% of retail investor accounts lose
money when trading CFDs" percentage. Stores it in data/etoro-risk-warning.json.
If the percentage has changed, alerts Tom via Telegram so the updater can
propagate the change across all 79+ HTML files on the site.

Usage:
    python3 tools/scrape_etoro_risk.py              # Check and update JSON
    python3 tools/scrape_etoro_risk.py --dry-run    # Check only, don't write

Cron (weekly, Mondays 1:30am — before fee scraper):
    30 1 * * 1  python3 PROJECT/tools/scrape_etoro_risk.py

Requires: pip3 install playwright && playwright install chromium
"""

import sys
import os
import json
import re
import pathlib
import argparse
from datetime import datetime

PROJECT_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
RISK_FILE = DATA_DIR / "etoro-risk-warning.json"

# Pages where eToro publishes the CFD risk percentage
ETORO_URLS = [
    "https://www.etoro.com/trading/fees/",
    "https://www.etoro.com/",
    "https://www.etoro.com/about/risk-disclosure/",
]

# Regex patterns to extract the percentage
RISK_PATTERNS = [
    r"(\d+)%\s*of\s*retail\s*investor\s*accounts?\s*lose\s*money",
    r"(\d+)%\s*of\s*retail\s*(?:CFD\s*)?(?:investor\s*)?accounts?\s*lose",
    r"(\d+)%\s*(?:des|der|de\s*los|dos)\s*(?:comptes?|Konten|cuentas|contas)",
]

# Sanity bounds — eToro's percentage has historically been 51-80%
MIN_SANE = 30
MAX_SANE = 90


def send_telegram(subject, body, emoji="📊"):
    """Send alert via security_lib."""
    try:
        sys.path.insert(0, str(PROJECT_DIR / "tools"))
        from security_lib import send_telegram as _send
        _send(subject, body, emoji=emoji)
    except Exception as e:
        print(f"  Telegram alert failed: {e}")


def scrape_page(url, timeout=30):
    """Fetch a page using Playwright (headless Chromium)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Playwright not installed. Trying urllib fallback.")
        return scrape_urllib(url, timeout)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"
            )
            page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
            page.wait_for_timeout(3000)
            text = page.inner_text("body")
            browser.close()
            return text
    except Exception as e:
        print(f"    Playwright error on {url}: {e}")
        return None


def scrape_urllib(url, timeout=15):
    """Fallback: fetch with urllib (won't bypass Cloudflare)."""
    import urllib.request
    import ssl

    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        html = resp.read().decode("utf-8", errors="ignore")
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text
    except Exception as e:
        print(f"    urllib error on {url}: {e}")
        return None


def extract_percentage(text):
    """Extract the retail investor loss percentage from page text."""
    for pattern in RISK_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pct = int(match.group(1))
            if MIN_SANE <= pct <= MAX_SANE:
                return pct
            else:
                print(f"  Found {pct}% but outside sane range ({MIN_SANE}-{MAX_SANE}), skipping.")
    return None


def load_data():
    """Load existing risk warning data, or return defaults."""
    if RISK_FILE.exists():
        return json.loads(RISK_FILE.read_text())
    return {
        "percentage": 51,
        "last_checked": None,
        "last_changed": None,
        "source_url": None,
        "history": [
            {"date": "2025-01-01", "percentage": 51}
        ]
    }


def save_data(data):
    """Write risk warning data to JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RISK_FILE.write_text(json.dumps(data, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Check eToro CFD risk percentage")
    parser.add_argument("--dry-run", action="store_true", help="Check only, don't update files")
    args = parser.parse_args()

    print(f"eToro Risk Percentage Checker — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    data = load_data()
    old_pct = data["percentage"]
    found_pct = None
    source_url = None

    for url in ETORO_URLS:
        print(f"\n  Checking {url} ...")
        text = scrape_page(url)
        if not text:
            print(f"    Failed to fetch page.")
            continue

        pct = extract_percentage(text)
        if pct is not None:
            found_pct = pct
            source_url = url
            print(f"    Found: {pct}% of retail investor accounts lose money")
            break
        else:
            print(f"    Risk percentage not found on this page.")

    if found_pct is None:
        print("\nERROR: Could not find risk percentage on any eToro page.")
        send_telegram(
            "eToro Risk Scraper Failed",
            "Could not extract the retail investor loss percentage from any eToro page.\n"
            "Pages tried:\n" + "\n".join(f"  • {u}" for u in ETORO_URLS) +
            "\n\nManual check needed.",
            emoji="🔴"
        )
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")
    data["last_checked"] = today
    data["source_url"] = source_url

    if found_pct != old_pct:
        print(f"\n  CHANGE DETECTED: {old_pct}% → {found_pct}%")
        data["percentage"] = found_pct
        data["last_changed"] = today
        data["history"].append({"date": today, "percentage": found_pct})

        if args.dry_run:
            print("  Dry run — would update JSON and alert.")
        else:
            save_data(data)
            print(f"  Updated {RISK_FILE.name}")
            send_telegram(
                "eToro Risk Percentage Changed",
                f"The CFD risk warning percentage has changed.\n\n"
                f"Old: {old_pct}%\nNew: {found_pct}%\n"
                f"Source: {source_url}\n\n"
                f"Running update_risk_warnings.py to update all site pages...",
                emoji="⚠️"
            )
    else:
        print(f"\n  No change — still {found_pct}%")
        if not args.dry_run:
            save_data(data)

    print(f"\nDone. Current percentage: {found_pct}%")


if __name__ == "__main__":
    main()
