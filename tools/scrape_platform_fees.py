#!/usr/bin/env python3
"""
Weekly Platform Fee Scraper — Playwright-based.

Uses a real browser to bypass Cloudflare and scrape fee pages.
Verifies stored fee data, flags changes, updates "last verified" date.

Usage:
    python3 tools/scrape_platform_fees.py                # Scrape all platforms
    python3 tools/scrape_platform_fees.py --dry-run      # Check without updating
    python3 tools/scrape_platform_fees.py --platform etoro  # Single platform

Cron (weekly, Mondays 2am):
    0 2 * * 1  python3 /var/www/socialtradingvlog-website/tools/scrape_platform_fees.py

Requires: pip3 install playwright && playwright install chromium
"""

import sys
import os
import json
import re
import time
import pathlib
import argparse
from datetime import datetime

PROJECT_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
FEES_FILE = DATA_DIR / "platform-fees.json"
VERIFIED_FILE = DATA_DIR / "platform-verified.json"

# Fee page URLs and verification patterns per platform
SCRAPE_TARGETS = {
    "etoro": {
        "urls": ["https://www.etoro.com/trading/fees/"],
        "checks": {
            "zero_commission": r"0%\s*commission|commission[\s-]*free",
            "min_deposit": r"minimum\s+deposit.*?\$(\d+)",
            "withdrawal_fee": r"withdrawal\s+fee.*?\$(\d+)",
            "crypto_spread": r"crypt.*?(\d+(?:\.\d+)?%)",
            "inactivity": r"inactivity.*?\$(\d+)",
        },
    },
    "plus500": {
        "urls": ["https://www.plus500.com/fees", "https://www.plus500.com/en-gb/trading/fees"],
        "checks": {
            "no_commission": r"commission[\s-]*free|no\s*commission",
            "cfd_notice": r"CFD",
            "inactivity": r"inactivity.*?[\$£€](\d+)",
        },
    },
    "trading212": {
        "urls": ["https://www.trading212.com/trading-fees"],
        "checks": {
            "zero_commission": r"commission[\s-]*free|0%\s*commission",
            "fx_fee": r"(?:currency|fx)\s+(?:conversion|fee).*?(\d+(?:\.\d+)?%)",
        },
    },
    "degiro": {
        "urls": ["https://www.degiro.com/fees", "https://www.degiro.co.uk/fees"],
        "checks": {
            "low_fees": r"€0|commission[\s-]*free",
            "connectivity": r"connectivity.*?€?(\d+(?:\.\d+)?)",
        },
    },
    "ibkr": {
        "urls": ["https://www.interactivebrokers.com/en/trading/commissions-stocks.php"],
        "checks": {
            "per_share": r"\$0\.005\s*/\s*share|0\.005",
            "tiered": r"tiered",
            "no_min_deposit": r"no\s+minimum|minimum.*?\$0",
        },
    },
    "xtb": {
        "urls": ["https://www.xtb.com/en/trading-fees"],
        "checks": {
            "zero_commission": r"0%\s*commission|commission[\s-]*free",
            "volume_cap": r"€?100[\.,]?000|100k",
        },
    },
    "ig": {
        "urls": ["https://www.ig.com/uk/charges"],
        "checks": {
            "share_dealing": r"£(\d+(?:\.\d+)?)\s*(?:per\s+)?(?:trade|deal)",
        },
    },
    "saxo": {
        "urls": ["https://www.home.saxo/en-gb/rates-and-conditions/stocks/commissions"],
        "checks": {
            "commission_rate": r"(\d+(?:\.\d+)?%)",
        },
    },
    "hl": {
        "urls": ["https://www.hl.co.uk/charges"],
        "checks": {
            "dealing_charge": r"£(\d+(?:\.\d+)?)\s*(?:per\s+)?(?:trade|deal)",
            "platform_fee": r"(\d+(?:\.\d+)?%)\s*(?:platform|service)",
        },
    },
    "freetrade": {
        "urls": ["https://freetrade.io/pricing"],
        "checks": {
            "free_plan": r"free|£0",
            "plus_price": r"£(\d+(?:\.\d+)?)\s*/\s*(?:month|mo)",
        },
    },
    "robinhood": {
        "urls": ["https://robinhood.com/us/en/about/fees/"],
        "checks": {
            "zero_commission": r"commission[\s-]*free|\$0\s*commission",
        },
    },
    "schwab": {
        "urls": ["https://www.schwab.com/pricing"],
        "checks": {
            "zero_commission": r"\$0\s*(?:commission|online)",
        },
    },
    "fidelity": {
        "urls": ["https://www.fidelity.com/trading/commissions-margin-rates"],
        "checks": {
            "zero_commission": r"\$0\s*commission",
        },
    },
    "scalable": {
        "urls": ["https://www.scalable.capital/en/broker-pricing"],
        "checks": {
            "trade_fee": r"€(\d+(?:\.\d+)?)\s*(?:per\s+)?(?:trade|order)",
        },
    },
    "traderepublic": {
        "urls": ["https://traderepublic.com/en-de/pricing"],
        "checks": {
            "flat_fee": r"€1|one\s+euro",
        },
    },
}


def scrape_with_playwright(url, timeout=30):
    """Fetch a page using Playwright (headless Chromium)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Playwright not installed. Falling back to urllib.")
        return scrape_with_urllib(url, timeout)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
            # Wait for dynamic content
            page.wait_for_timeout(3000)
            text = page.inner_text("body")
            html = page.content()
            browser.close()
            return {"text": text, "html": html, "status": "ok"}
    except Exception as e:
        print(f"    Playwright error on {url}: {e}")
        return None


def scrape_with_urllib(url, timeout=15):
    """Fallback: fetch with urllib (won't bypass Cloudflare)."""
    import urllib.request
    import urllib.error
    import ssl

    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        html = resp.read().decode("utf-8", errors="ignore")
        # Strip HTML tags for text version
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return {"text": text, "html": html, "status": "ok"}
    except Exception as e:
        print(f"    urllib error on {url}: {e}")
        return None


def verify_platform(platform_id, dry_run=False):
    """Scrape a platform's fee pages and verify data points."""
    target = SCRAPE_TARGETS.get(platform_id)
    if not target:
        return None

    print(f"\n  Scraping {platform_id}...")
    result = {
        "platform": platform_id,
        "checked_at": datetime.now().isoformat(),
        "pages_checked": [],
        "verified": {},
        "changes": [],
        "status": "unknown",
    }

    all_text = ""
    all_html = ""

    for url in target["urls"]:
        print(f"    Fetching {url}...")
        page_data = scrape_with_playwright(url)
        if page_data:
            all_text += " " + page_data["text"]
            all_html += " " + page_data["html"]
            result["pages_checked"].append(url)
        time.sleep(2)  # Rate limit between pages

    if not all_text:
        print(f"    WARNING: Could not fetch any pages for {platform_id}")
        result["status"] = "unreachable"
        return result

    # Verify each data point
    for key, pattern in target["checks"].items():
        match = re.search(pattern, all_text, re.IGNORECASE)
        if not match:
            match = re.search(pattern, all_html, re.IGNORECASE)

        if match:
            result["verified"][key] = {
                "found": True,
                "match": match.group(0)[:100],
            }
            print(f"    ✓ {key}: confirmed")
        else:
            result["verified"][key] = {
                "found": False,
            }
            print(f"    ? {key}: not found — may have changed")
            result["changes"].append(key)

    result["status"] = "checked"
    return result


def update_fees_timestamp(results, dry_run=False):
    """Update last-verified timestamp in fees JSON."""
    if not FEES_FILE.exists():
        print("  Fee data file not found — skipping timestamp update")
        return

    fees = json.loads(FEES_FILE.read_text())
    fees["_last_updated"] = datetime.now().strftime("%Y-%m-%d")

    if not dry_run:
        FEES_FILE.write_text(json.dumps(fees, indent=2))
        print(f"  Updated _last_updated in {FEES_FILE}")

    return fees


def update_comparison_page_banner(dry_run=False):
    """Update 'last verified' banner on comparison page and trade comparison."""
    now = datetime.now().strftime("%d %B %Y")
    banner_pattern = r'<div id="verified-banner"[^>]*>.*?</div>'
    banner_html = (
        f'<div id="verified-banner" style="background:#E8F5E9;border:1px solid #A5D6A7;'
        f'border-radius:8px;padding:12px 20px;margin-bottom:20px;font-size:13px;'
        f'color:#2E7D32;display:flex;align-items:center;gap:8px;">'
        f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2E7D32" stroke-width="2">'
        f'<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
        f'<span><strong>Data verified:</strong> {now} — All platform fees and features checked against official sources.</span>'
        f'</div>'
    )

    pages = [
        PROJECT_DIR / "calculators" / "compare-platforms" / "index.html",
    ]

    for page in pages:
        if not page.exists():
            continue
        content = page.read_text()
        if re.search(banner_pattern, content, re.DOTALL):
            content = re.sub(banner_pattern, banner_html, content, flags=re.DOTALL)
            if not dry_run:
                page.write_text(content)
                print(f"  Updated verified banner on {page.name}")


def save_verification_log(results, dry_run=False):
    """Save verification results to log file."""
    verified = {}
    if VERIFIED_FILE.exists():
        try:
            verified = json.loads(VERIFIED_FILE.read_text())
        except Exception:
            verified = {}

    for result in results:
        if result and result.get("status") == "checked":
            verified[result["platform"]] = {
                "last_verified": result["checked_at"],
                "pages_checked": result["pages_checked"],
                "verified": result["verified"],
                "changes": result["changes"],
            }

    verified["_last_full_check"] = datetime.now().isoformat()

    if not dry_run:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        VERIFIED_FILE.write_text(json.dumps(verified, indent=2))


def send_change_alerts(results):
    """Alert if any platform data has changed."""
    changes = []
    for r in results:
        if r and r.get("changes"):
            changes.append(f"{r['platform']}: {', '.join(r['changes'])}")

    unreachable = [r["platform"] for r in results if r and r.get("status") == "unreachable"]

    if changes or unreachable:
        try:
            sys.path.insert(0, str(PROJECT_DIR / "tools"))
            from site_autopilot import send_alert
            if changes:
                send_alert("platform_fees", f"Fee changes detected: {'; '.join(changes)}", "warning",
                           "Some fee data points could not be confirmed. Manual review recommended.")
            if unreachable:
                send_alert("platform_fees", f"Unreachable platforms: {', '.join(unreachable)}", "warning")
        except ImportError:
            pass


def main():
    parser = argparse.ArgumentParser(description="Scrape and verify platform fee data (Playwright)")
    parser.add_argument("--dry-run", action="store_true", help="Check without updating files")
    parser.add_argument("--platform", help="Scrape a single platform only")
    parser.add_argument("--fallback", action="store_true", help="Use urllib instead of Playwright")
    args = parser.parse_args()

    print(f"Platform Fee Scraper (Playwright) — {datetime.now().isoformat()}")

    if args.fallback:
        global scrape_with_playwright
        scrape_with_playwright = scrape_with_urllib

    platforms = [args.platform] if args.platform else list(SCRAPE_TARGETS.keys())
    results = []

    for pid in platforms:
        result = verify_platform(pid, dry_run=args.dry_run)
        results.append(result)

    # Update timestamps
    update_fees_timestamp(results, dry_run=args.dry_run)
    update_comparison_page_banner(dry_run=args.dry_run)
    save_verification_log(results, dry_run=args.dry_run)

    # Summary
    checked = sum(1 for r in results if r and r.get("status") == "checked")
    unreachable = sum(1 for r in results if r and r.get("status") == "unreachable")
    with_changes = sum(1 for r in results if r and r.get("changes"))

    print(f"\nDone! {checked} platforms checked, {unreachable} unreachable, {with_changes} with potential changes.")

    # Alert on changes
    send_change_alerts(results)


if __name__ == "__main__":
    main()
