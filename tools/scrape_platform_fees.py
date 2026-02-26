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

# Fee page URLs, verification patterns, and auto-update extractors per platform
# "checks" = regex to VERIFY known data still exists on the page
# "extractors" = mapping from check keys to JSON paths for AUTO-UPDATING when values change
#   Each extractor has:
#     "json_path" = dot-separated path into platform-fees.json (relative to platforms.{id})
#     "transform" = how to convert the captured regex group to the JSON value type
#     "extract_patterns" = (optional) broader regex patterns to try if check fails

SCRAPE_TARGETS = {
    "etoro": {
        "urls": ["https://www.etoro.com/trading/fees/", "https://www.etoro.com/customer-service/fees/"],
        "checks": {
            "zero_commission": r"0%\s*commission|commission[\s-]*free",
            "min_deposit": r"minimum\s+deposit.*?\$(\d+)",
            "withdrawal_fee": r"withdrawal\s+fee.*?\$(\d+)|withdrawal.*?\$(\d+)",
            "crypto_spread": r"crypt.*?(\d+(?:\.\d+)?)\s*%|(\d+(?:\.\d+)?)\s*%.*?crypt",
            "inactivity": r"inactivity.*?\$(\d+)",
        },
        "extractors": {
            "min_deposit": {
                "json_path": "other_fees.min_deposit",
                "transform": lambda v: f"${v}",
            },
            "withdrawal_fee": {
                "json_path": "other_fees.withdrawal",
                "transform": lambda v: f"${v} (USD accounts), free for GBP/EUR",
            },
            "crypto_spread": {
                "json_path": "crypto.spread_pct",
                "transform": lambda v: round(float(v) / 100, 4),
            },
            "inactivity": {
                "json_path": "other_fees.inactivity",
                "transform": lambda v: f"${v}/month after 12 months",
            },
        },
    },
    "plus500": {
        "urls": ["https://www.plus500.com/fees", "https://www.plus500.com/en-gb/trading/fees"],
        "checks": {
            "no_commission": r"commission[\s-]*free|no\s*commission|zero\s*commission",
            "cfd_notice": r"CFD",
            "inactivity": r"inactivity.*?[\$£€](\d+)",
        },
        "extractors": {
            "inactivity": {
                "json_path": "other_fees.inactivity",
                "transform": lambda v: f"${v}/month after 3 months",
            },
        },
    },
    "trading212": {
        "urls": ["https://www.trading212.com/trading-fees"],
        "checks": {
            "zero_commission": r"commission[\s-]*free|0%\s*commission|zero\s*commission",
            "fx_fee": r"(?:currency|fx|conversion)\s+(?:conversion|fee).*?(\d+(?:\.\d+)?)\s*%",
        },
        "extractors": {
            "fx_fee": {
                "json_path": "stocks.fx_fee_pct",
                "transform": lambda v: round(float(v) / 100, 4),
            },
        },
    },
    "degiro": {
        "urls": ["https://www.degiro.com/fees", "https://www.degiro.co.uk/fees"],
        "checks": {
            "low_fees": r"€0|commission[\s-]*free",
            "connectivity": r"connectivity.*?€?(\d+(?:\.\d+)?)",
        },
        "extractors": {
            "connectivity": {
                "json_path": "stocks.connectivity_fee",
                "transform": lambda v: float(v),
            },
        },
    },
    "ibkr": {
        "urls": ["https://www.interactivebrokers.com/en/trading/commissions-stocks.php"],
        "checks": {
            "per_share": r"\$0\.(\d+)\s*/\s*share|per\s+share.*?\$0\.(\d+)",
            "tiered": r"tiered",
            "no_min_deposit": r"no\s+minimum|minimum.*?\$0|\$0\s*minimum",
        },
        "extractors": {
            "per_share": {
                "json_path": "stocks.rate_per_share",
                "transform": lambda v: round(float(f"0.{v}"), 4),
            },
        },
    },
    "xtb": {
        "urls": ["https://www.xtb.com/en/trading-fees"],
        "checks": {
            "zero_commission": r"0%\s*commission|commission[\s-]*free",
            "volume_cap": r"€?100[\.,]?000|100k",
        },
        "extractors": {},
    },
    "ig": {
        "urls": ["https://www.ig.com/uk/charges"],
        "checks": {
            "share_dealing": r"£(\d+(?:\.\d+)?)\s*(?:per\s+)?(?:trade|deal)",
        },
        "extractors": {},
    },
    "saxo": {
        "urls": ["https://www.home.saxo/en-gb/rates-and-conditions/stocks/commissions"],
        "checks": {
            "commission_rate": r"(\d+(?:\.\d+)?)\s*%",
        },
        "extractors": {},
    },
    "hl": {
        "urls": ["https://www.hl.co.uk/charges"],
        "checks": {
            "dealing_charge": r"£(\d+(?:\.\d+)?)\s*(?:per\s+)?(?:trade|deal)",
            "platform_fee": r"(\d+(?:\.\d+)?)\s*%\s*(?:platform|service)",
        },
        "extractors": {},
    },
    "freetrade": {
        "urls": ["https://freetrade.io/pricing"],
        "checks": {
            "free_plan": r"free|£0",
            "plus_price": r"£(\d+(?:\.\d+)?)\s*/\s*(?:month|mo)",
        },
        "extractors": {},
    },
    "robinhood": {
        "urls": ["https://robinhood.com/us/en/about/fees/"],
        "checks": {
            "zero_commission": r"commission[\s-]*free|\$0\s*commission",
        },
        "extractors": {},
    },
    "schwab": {
        "urls": ["https://www.schwab.com/pricing"],
        "checks": {
            "zero_commission": r"\$0\s*(?:commission|online)",
        },
        "extractors": {},
    },
    "fidelity": {
        "urls": ["https://www.fidelity.com/trading/commissions-margin-rates"],
        "checks": {
            "zero_commission": r"\$0\s*commission",
        },
        "extractors": {},
    },
    "scalable": {
        "urls": ["https://www.scalable.capital/en/broker-pricing"],
        "checks": {
            "trade_fee": r"€(\d+(?:\.\d+)?)\s*(?:per\s+)?(?:trade|order)",
        },
        "extractors": {},
    },
    "traderepublic": {
        "urls": ["https://traderepublic.com/en-de/pricing"],
        "checks": {
            "flat_fee": r"€1|one\s+euro",
        },
        "extractors": {},
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

    # Verify each data point and extract values for auto-update
    for key, pattern in target["checks"].items():
        match = re.search(pattern, all_text, re.IGNORECASE)
        if not match:
            match = re.search(pattern, all_html, re.IGNORECASE)

        if match:
            captured = extract_captured_value(match)
            result["verified"][key] = {
                "found": True,
                "match": match.group(0)[:100],
                "captured_value": captured,
            }
            print(f"    ✓ {key}: confirmed" + (f" (value: {captured})" if captured else ""))
        else:
            result["verified"][key] = {
                "found": False,
                "captured_value": None,
            }
            print(f"    ? {key}: not found — may have changed")
            result["changes"].append(key)

    result["status"] = "checked"
    return result


def get_json_value(data, platform_id, json_path):
    """Get a value from platform-fees.json by dot-separated path."""
    obj = data.get("platforms", {}).get(platform_id, {})
    for key in json_path.split("."):
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return None
    return obj


def set_json_value(data, platform_id, json_path, value):
    """Set a value in platform-fees.json by dot-separated path."""
    obj = data.get("platforms", {}).get(platform_id, {})
    keys = json_path.split(".")
    for key in keys[:-1]:
        if key not in obj:
            obj[key] = {}
        obj = obj[key]
    obj[keys[-1]] = value


def extract_captured_value(match):
    """Get the first non-None captured group from a regex match."""
    for g in match.groups():
        if g is not None:
            return g
    return None


def auto_update_fees(results, dry_run=False):
    """Extract fee values from scrape results and update platform-fees.json."""
    if not FEES_FILE.exists():
        return []

    fees = json.loads(FEES_FILE.read_text())
    updates = []

    for result in results:
        if not result or result.get("status") != "checked":
            continue

        pid = result["platform"]
        target = SCRAPE_TARGETS.get(pid, {})
        extractors = target.get("extractors", {})

        for check_key, verified in result.get("verified", {}).items():
            if check_key not in extractors:
                continue

            extractor = extractors[check_key]
            captured = verified.get("captured_value")
            if captured is None:
                continue

            try:
                new_value = extractor["transform"](captured)
            except (ValueError, TypeError) as e:
                print(f"    Transform error for {pid}.{check_key}: {e}")
                continue

            json_path = extractor["json_path"]
            old_value = get_json_value(fees, pid, json_path)

            if old_value != new_value:
                set_json_value(fees, pid, json_path, new_value)
                update_msg = f"{pid}.{json_path}: {old_value!r} → {new_value!r}"
                updates.append(update_msg)
                print(f"    AUTO-UPDATED: {update_msg}")

    if updates and not dry_run:
        fees["_last_updated"] = datetime.now().strftime("%Y-%m-%d")
        FEES_FILE.write_text(json.dumps(fees, indent=2))
        print(f"  Updated {len(updates)} fee values in {FEES_FILE}")

    return updates


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
    """No longer needed — compare-platforms now loads date dynamically from JSON.
    Kept as a no-op for backwards compatibility with cron scripts."""
    pass


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


def send_change_alerts(results, fee_updates=None):
    """Alert if any platform data has changed."""
    changes = []
    for r in results:
        if r and r.get("changes"):
            changes.append(f"{r['platform']}: {', '.join(r['changes'])}")

    unreachable = [r["platform"] for r in results if r and r.get("status") == "unreachable"]

    if changes or unreachable or fee_updates:
        try:
            sys.path.insert(0, str(PROJECT_DIR / "tools"))
            from site_autopilot import send_alert
            if fee_updates:
                update_lines = "\n".join(f"• {u}" for u in fee_updates)
                send_alert("platform_fees",
                           f"Fee data auto-updated ({len(fee_updates)} changes)",
                           "info",
                           f"The following fee values were automatically updated in platform-fees.json:\n{update_lines}\n\nThese will go live after update_fee_pages.py commits and pushes.")
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

    # Auto-update fee values in JSON when captured values differ
    fee_updates = auto_update_fees(results, dry_run=args.dry_run)

    # Update timestamps
    update_fees_timestamp(results, dry_run=args.dry_run)
    update_comparison_page_banner(dry_run=args.dry_run)
    save_verification_log(results, dry_run=args.dry_run)

    # Summary
    checked = sum(1 for r in results if r and r.get("status") == "checked")
    unreachable = sum(1 for r in results if r and r.get("status") == "unreachable")
    with_changes = sum(1 for r in results if r and r.get("changes"))

    print(f"\nDone! {checked} platforms checked, {unreachable} unreachable, {with_changes} with potential changes.")
    if fee_updates:
        print(f"  [AUTO-UPDATED] {len(fee_updates)} fee values changed in platform-fees.json:")
        for u in fee_updates:
            print(f"    • {u}")

    # Alert on changes
    send_change_alerts(results, fee_updates)


if __name__ == "__main__":
    main()
