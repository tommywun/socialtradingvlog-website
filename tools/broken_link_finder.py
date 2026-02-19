#!/usr/bin/env python3
"""
Broken link finder for link building outreach.

Scans competitor pages about copy trading / eToro / social trading for broken links.
When found, we can pitch socialtradingvlog.com content as a replacement.

Usage:
    python3 tools/broken_link_finder.py                    # scan all target pages
    python3 tools/broken_link_finder.py --url URL          # scan a single page
    python3 tools/broken_link_finder.py --report           # show last scan results

Reports saved to: reports/broken-links-YYYY-MM-DD.md
"""

import sys
import os
import json
import pathlib
import argparse
import urllib.request
import urllib.error
import urllib.parse
import re
from datetime import datetime
from html.parser import HTMLParser
import ssl
import time

SCRIPT_DIR = pathlib.Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
REPORTS_DIR = PROJECT_DIR / "reports"
REPORT_FILE = REPORTS_DIR / f"broken-links-{datetime.now().strftime('%Y-%m-%d')}.md"
REPORT_LATEST = REPORTS_DIR / "broken-links-latest.md"

# Pages to scan for broken links — competitor content about copy trading / eToro
TARGET_PAGES = [
    # "Best copy trading" / "eToro review" roundup pages
    "https://www.babypips.com/forexpedia/copy-trading",
    "https://www.investopedia.com/etoro-review-5089532",
    "https://www.investopedia.com/terms/s/social-trading.asp",
    "https://www.nerdwallet.com/reviews/investing/brokers/etoro",
    "https://www.forbes.com/advisor/investing/etoro-review/",
    "https://www.bankrate.com/investing/etoro-review/",
    "https://brokerchooser.com/broker-reviews/etoro-review",
    "https://www.stockbrokers.com/review/etoro",
    "https://tradingplatforms.com/uk/copy-trading/",
    "https://www.ig.com/en/trading-strategies/what-is-copy-trading-and-how-does-it-work--200730",
    # Blogs / articles about copy trading
    "https://www.fool.com/investing/stock-market/market-sectors/financials/broker-stocks/copy-trading/",
    "https://www.finder.com/etoro-review",
    "https://moneytothemasses.com/saving-for-your-future/investing/etoro-review",
]

# Our content that could replace broken links
REPLACEMENT_CONTENT = {
    "copy trading": "https://socialtradingvlog.com/articles/copy-trading-beginners-guide/",
    "social trading": "https://socialtradingvlog.com/articles/what-is-social-trading/",
    "etoro review": "https://socialtradingvlog.com/articles/etoro-review-2026/",
    "etoro": "https://socialtradingvlog.com/",
    "take profit": "https://socialtradingvlog.com/articles/take-profits-copy-trading/",
    "how much": "https://socialtradingvlog.com/articles/how-much-money-copy-trading/",
    "why lose": "https://socialtradingvlog.com/video/why-do-most-etoro-traders-lose-money/",
}

# SSL context that doesn't verify (some sites have cert issues)
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class LinkExtractor(HTMLParser):
    """Extract all links from HTML."""
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_text = ""
        self.in_a = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href:
                self.links.append({"href": href, "text": ""})
                self.in_a = True
                self.current_text = ""

    def handle_data(self, data):
        if self.in_a:
            self.current_text += data

    def handle_endtag(self, tag):
        if tag == "a" and self.in_a and self.links:
            self.links[-1]["text"] = self.current_text.strip()
            self.in_a = False


def fetch_page(url, timeout=15):
    """Fetch a URL and return (status_code, html_content)."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


def check_link(url, timeout=10):
    """Check if a URL is alive. Returns (status_code, is_broken)."""
    req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            return resp.status, False
    except urllib.error.HTTPError as e:
        if e.code in (404, 410, 403, 500, 502, 503):
            # Try GET as some servers reject HEAD
            try:
                req2 = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req2, timeout=timeout, context=SSL_CTX) as resp:
                    return resp.status, False
            except urllib.error.HTTPError as e2:
                return e2.code, e2.code in (404, 410)
            except Exception:
                return e.code, e.code in (404, 410)
        return e.code, e.code in (404, 410)
    except Exception:
        return 0, True


def suggest_replacement(link_text, link_url):
    """Suggest our content as a replacement for a broken link."""
    text = (link_text + " " + link_url).lower()
    for keyword, replacement_url in REPLACEMENT_CONTENT.items():
        if keyword in text:
            return replacement_url
    return "https://socialtradingvlog.com/"


def scan_page(url):
    """Scan a page for broken outbound links."""
    print(f"\n  Scanning: {url[:70]}...")

    status, html = fetch_page(url)
    if status != 200:
        print(f"    Could not fetch page (HTTP {status})")
        return []

    parser = LinkExtractor()
    try:
        parser.feed(html)
    except Exception:
        print(f"    Error parsing HTML")
        return []

    # Filter to external links only
    base_domain = urllib.parse.urlparse(url).netloc
    external_links = []
    for link in parser.links:
        href = link["href"]
        if not href.startswith("http"):
            continue
        link_domain = urllib.parse.urlparse(href).netloc
        if link_domain == base_domain:
            continue
        # Skip common non-content links
        if any(skip in link_domain for skip in ["google.com", "facebook.com", "twitter.com",
               "linkedin.com", "youtube.com", "instagram.com", "apple.com",
               "amazon.com", "wikipedia.org", "github.com"]):
            continue
        external_links.append(link)

    print(f"    Found {len(external_links)} external links to check...")

    broken = []
    for i, link in enumerate(external_links):
        href = link["href"]
        time.sleep(0.5)  # be polite
        status, is_broken = check_link(href)
        if is_broken:
            replacement = suggest_replacement(link["text"], href)
            broken.append({
                "source_page": url,
                "broken_url": href,
                "link_text": link["text"][:100],
                "status": status,
                "suggested_replacement": replacement,
            })
            print(f"    BROKEN [{status}]: {href[:60]}")

    if not broken:
        print(f"    No broken links found.")

    return broken


def generate_report(all_broken):
    """Generate a markdown report of broken links found."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Broken Link Report — {datetime.now().strftime('%Y-%m-%d')}",
        f"",
        f"Found **{len(all_broken)}** broken links across scanned pages.",
        f"",
    ]

    if not all_broken:
        lines.append("No broken links found! Try again in a few weeks.")
    else:
        # Group by source page
        by_source = {}
        for b in all_broken:
            src = b["source_page"]
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(b)

        for source, broken_links in by_source.items():
            lines.append(f"## {source}")
            lines.append(f"")
            for b in broken_links:
                lines.append(f"- **Broken**: [{b['link_text'][:50]}]({b['broken_url']}) (HTTP {b['status']})")
                lines.append(f"  - **Replacement**: {b['suggested_replacement']}")
            lines.append(f"")

        lines.append("## Outreach Template")
        lines.append("")
        lines.append("```")
        lines.append("Subject: Broken link on your [TOPIC] page")
        lines.append("")
        lines.append("Hi,")
        lines.append("")
        lines.append("I was reading your article at [PAGE_URL] and noticed a broken link:")
        lines.append("")
        lines.append("  [LINK_TEXT] → [BROKEN_URL] (returns 404)")
        lines.append("")
        lines.append("I have a similar resource that could work as a replacement:")
        lines.append("  [REPLACEMENT_URL]")
        lines.append("")
        lines.append("It covers [TOPIC] from a real user perspective — I've been copy trading")
        lines.append("on eToro since 2016 with everything documented on video.")
        lines.append("")
        lines.append("Either way, thought you'd want to know about the broken link!")
        lines.append("")
        lines.append("Best,")
        lines.append("Tom")
        lines.append("Social Trading Vlog")
        lines.append("```")

    content = "\n".join(lines)
    REPORT_FILE.write_text(content)
    REPORT_LATEST.write_text(content)
    print(f"\nReport saved to: {REPORT_FILE}")
    return content


def cmd_scan_all():
    """Scan all target pages for broken links."""
    print(f"Scanning {len(TARGET_PAGES)} pages for broken links...")
    all_broken = []
    for url in TARGET_PAGES:
        broken = scan_page(url)
        all_broken.extend(broken)
        time.sleep(1)  # be polite between pages

    generate_report(all_broken)
    print(f"\nDone! Found {len(all_broken)} broken links total.")


def cmd_scan_url(url):
    """Scan a single URL for broken links."""
    broken = scan_page(url)
    generate_report(broken)


def cmd_show_report():
    """Show the latest broken link report."""
    if not REPORT_LATEST.exists():
        print("No broken link report found. Run a scan first.")
        return
    print(REPORT_LATEST.read_text())


def main():
    parser = argparse.ArgumentParser(description="Broken link finder for link building")
    parser.add_argument("--url", help="Scan a single URL")
    parser.add_argument("--report", action="store_true", help="Show last scan results")
    args = parser.parse_args()

    if args.url:
        cmd_scan_url(args.url)
    elif args.report:
        cmd_show_report()
    else:
        cmd_scan_all()


if __name__ == "__main__":
    main()
