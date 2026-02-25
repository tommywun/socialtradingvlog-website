#!/usr/bin/env python3
"""
Automated Link Building Prospector

Finds link-building opportunities and queues outreach emails.
Safe, white-hat techniques only:
  1. Brand mention monitoring — find unlinked mentions of our site/tools
  2. Broken link finder — find dead links to trading tools, suggest ours
  3. Resource page finder — find "best trading tools" pages to submit to
  4. Directory submissions — submit to financial tool directories

Usage:
    python3 tools/link_prospector.py                # Run all prospecting
    python3 tools/link_prospector.py --type mentions # Brand mentions only
    python3 tools/link_prospector.py --type broken   # Broken link reclamation only
    python3 tools/link_prospector.py --type resources # Resource pages only
    python3 tools/link_prospector.py --dry-run       # Preview without saving

Cron:
    0 6 * * 3  python3 /var/www/socialtradingvlog-website/tools/link_prospector.py
"""

import sys
import os
import json
import re
import time
import pathlib
import argparse
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from html.parser import HTMLParser

PROJECT_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
PROSPECTS_FILE = DATA_DIR / "link-prospects.json"
OUTREACH_DIR = PROJECT_DIR / "outreach"
SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"

SSL_CTX = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Our brand terms to monitor
BRAND_TERMS = [
    "socialtradingvlog",
    "social trading vlog",
    "socialtradingvlog.com",
]

# Our tools/pages to find mentions of
TOOL_TERMS = [
    "etoro fee calculator",
    "etoro copy trading calculator",
    "compare trading platforms tool",
    "trading platform comparison tool",
]

# Search queries to find resource pages
RESOURCE_QUERIES = [
    "best trading tools list",
    "best investing calculators online",
    "best etoro tools",
    "trading platform comparison resources",
    "best free investing tools",
    "trading fee calculator tools",
    "copy trading resources",
    "social trading tools list",
    "best financial calculators",
    "investing tools directory",
]

# Search queries for broken link opportunities
BROKEN_LINK_QUERIES = [
    "trading fee calculator",
    "copy trading calculator",
    "etoro calculator",
    "platform comparison tool investing",
    "trading cost calculator",
]

# Directories to submit to
DIRECTORIES = [
    {"name": "Product Hunt", "url": "https://www.producthunt.com/", "type": "product_directory"},
    {"name": "AlternativeTo", "url": "https://alternativeto.net/", "type": "software_directory"},
    {"name": "FinancialToolsList", "url": "https://github.com/topics/finance-tools", "type": "github_topic"},
    {"name": "Awesome Fintech", "url": "https://github.com/topics/fintech", "type": "github_topic"},
]

# ─── Multi-Language Link Building ─────────────────────────────────────────
# Search queries in other languages to find link opportunities in those markets

MULTILANG_RESOURCE_QUERIES = {
    "es": [
        "mejores herramientas de trading",
        "calculadora de comisiones eToro",
        "comparar plataformas de trading",
        "herramientas gratuitas de inversión",
        "mejores calculadoras de trading",
    ],
    "de": [
        "beste Trading-Tools",
        "eToro Gebührenrechner",
        "Trading-Plattformen Vergleich",
        "kostenlose Anlage-Tools",
        "beste Finanzrechner",
    ],
    "fr": [
        "meilleurs outils de trading",
        "calculatrice frais eToro",
        "comparaison plateformes trading",
        "outils d'investissement gratuits",
        "meilleurs calculateurs financiers",
    ],
    "pt": [
        "melhores ferramentas de trading",
        "calculadora de taxas eToro",
        "comparar plataformas de negociação",
        "ferramentas gratuitas de investimento",
        "melhores calculadoras financeiras",
    ],
    "it": [
        "migliori strumenti di trading",
        "calcolatrice commissioni eToro",
        "confronto piattaforme trading",
        "strumenti di investimento gratuiti",
        "migliori calcolatrici finanziarie",
    ],
    "nl": [
        "beste trading tools",
        "eToro kosten calculator",
        "handelsplatformen vergelijken",
        "gratis beleggingstools",
        "beste financiële rekenmachines",
    ],
    "pl": [
        "najlepsze narzędzia tradingowe",
        "kalkulator opłat eToro",
        "porównanie platform tradingowych",
        "darmowe narzędzia inwestycyjne",
        "najlepsze kalkulatory finansowe",
    ],
    "ko": [
        "최고의 트레이딩 도구",
        "eToro 수수료 계산기",
        "트레이딩 플랫폼 비교",
        "무료 투자 도구",
        "최고의 금융 계산기",
    ],
}

MULTILANG_BROKEN_LINK_QUERIES = {
    "es": ["calculadora comisiones trading", "herramienta comparar brokers"],
    "de": ["Trading Gebühren Rechner", "Broker Vergleich Tool"],
    "fr": ["calculateur frais trading", "outil comparaison courtiers"],
    "pt": ["calculadora taxas corretora", "ferramenta comparação corretoras"],
}

# Language-specific landing page URLs for outreach
LANG_LANDING_PAGES = {
    "en": "https://socialtradingvlog.com/calculators/",
    "es": "https://socialtradingvlog.com/es/calculadoras/",
    "de": "https://socialtradingvlog.com/de/rechner/",
    "fr": "https://socialtradingvlog.com/fr/calculateurs/",
    "pt": "https://socialtradingvlog.com/pt/calculadoras/",
    "it": "https://socialtradingvlog.com/it/calcolatori/",
    "nl": "https://socialtradingvlog.com/nl/calculators/",
    "pl": "https://socialtradingvlog.com/pl/kalkulatory/",
    "ko": "https://socialtradingvlog.com/ko/계산기/",
}


def search_google(query, num_results=10):
    """Search Google and return results. Uses SerpAPI-style scraping."""
    results = []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=15, context=SSL_CTX)
        html = resp.read().decode("utf-8", errors="ignore")

        # Extract URLs from search results
        links = re.findall(r'href="(/url\?q=|)(https?://[^"&]+)', html)
        for _, link in links:
            # Filter out Google's own pages
            if not any(skip in link for skip in ["google.com", "googleapis.com", "gstatic.com", "youtube.com"]):
                results.append(link)

        time.sleep(2)  # Rate limit to avoid blocks
    except Exception as e:
        print(f"    Search failed for '{query}': {e}")

    return results[:num_results]


def check_page_for_our_link(url):
    """Check if a page already links to our site."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
        content = resp.read().decode("utf-8", errors="ignore")
        return "socialtradingvlog.com" in content.lower()
    except Exception:
        return False


def find_contact_info(url, html=None):
    """Try to find contact email or contact page from a URL."""
    try:
        if not html:
            req = urllib.request.Request(url, headers=HEADERS)
            resp = urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
            html = resp.read().decode("utf-8", errors="ignore")

        # Find email addresses
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
        # Filter out common non-contact emails
        emails = [e for e in emails if not any(skip in e.lower() for skip in
                  ["example.com", "sentry.io", "wixpress", "privacy", "abuse", "noreply"])]

        # Find contact page links
        contact_links = re.findall(r'href="([^"]*(?:contact|about|reach)[^"]*)"', html, re.IGNORECASE)

        return {
            "emails": list(set(emails))[:3],
            "contact_pages": list(set(contact_links))[:3],
        }
    except Exception:
        return {"emails": [], "contact_pages": []}


def find_brand_mentions():
    """Find pages that mention our brand but don't link to us."""
    print("\n── Brand Mention Monitoring ──")
    prospects = []

    for term in BRAND_TERMS:
        print(f"  Searching for: \"{term}\"")
        urls = search_google(f'"{term}" -site:socialtradingvlog.com -site:youtube.com')

        for url in urls:
            has_link = check_page_for_our_link(url)
            if not has_link:
                contact = find_contact_info(url)
                prospect = {
                    "type": "brand_mention",
                    "url": url,
                    "term": term,
                    "has_our_link": False,
                    "contact": contact,
                    "found_at": datetime.now().isoformat(),
                    "status": "new",
                    "outreach_template": "brand_mention",
                }
                prospects.append(prospect)
                print(f"    Found unlinked mention: {url}")
            time.sleep(1)

    print(f"  Found {len(prospects)} unlinked brand mentions")
    return prospects


def find_resource_pages():
    """Find resource/list pages where our tools could be listed."""
    print("\n── Resource Page Finder ──")
    prospects = []

    for query in RESOURCE_QUERIES:
        print(f"  Searching: \"{query}\"")
        urls = search_google(query, num_results=5)

        for url in urls:
            if "socialtradingvlog.com" in url:
                continue

            has_link = check_page_for_our_link(url)
            if not has_link:
                contact = find_contact_info(url)
                prospect = {
                    "type": "resource_page",
                    "url": url,
                    "query": query,
                    "has_our_link": False,
                    "contact": contact,
                    "found_at": datetime.now().isoformat(),
                    "status": "new",
                    "outreach_template": "resource_page",
                }
                prospects.append(prospect)
                print(f"    Potential resource page: {url}")
            time.sleep(1)

    print(f"  Found {len(prospects)} resource pages without our link")
    return prospects


def find_broken_link_opportunities():
    """Find pages with broken links to trading tools — we can suggest ours."""
    print("\n── Broken Link Reclamation ──")
    prospects = []

    for query in BROKEN_LINK_QUERIES:
        print(f"  Searching: \"{query}\"")
        urls = search_google(query, num_results=5)

        for url in urls:
            if "socialtradingvlog.com" in url:
                continue
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                resp = urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
                html = resp.read().decode("utf-8", errors="ignore")

                # Find all outbound links
                links = re.findall(r'href="(https?://[^"]+)"', html)
                broken_found = []

                for link in links[:20]:  # Check first 20 links
                    if any(skip in link for skip in ["google.com", "facebook.com", "twitter.com", "youtube.com"]):
                        continue
                    try:
                        check_req = urllib.request.Request(link, headers=HEADERS, method="HEAD")
                        check_resp = urllib.request.urlopen(check_req, timeout=5, context=SSL_CTX)
                    except urllib.error.HTTPError as e:
                        if e.code in (404, 410):
                            broken_found.append({"url": link, "status": e.code})
                    except Exception:
                        pass
                    time.sleep(0.3)

                if broken_found:
                    contact = find_contact_info(url, html)
                    prospect = {
                        "type": "broken_link",
                        "page_url": url,
                        "broken_links": broken_found,
                        "contact": contact,
                        "found_at": datetime.now().isoformat(),
                        "status": "new",
                        "outreach_template": "broken_link",
                    }
                    prospects.append(prospect)
                    print(f"    Found {len(broken_found)} broken links on: {url}")

            except Exception:
                pass
            time.sleep(1)

    print(f"  Found {len(prospects)} pages with broken links")
    return prospects


def find_multilang_opportunities():
    """Find link opportunities in non-English markets."""
    print("\n── Multi-Language Link Prospecting ──")
    prospects = []

    for lang, queries in MULTILANG_RESOURCE_QUERIES.items():
        print(f"\n  [{lang.upper()}] Searching {len(queries)} queries...")
        landing = LANG_LANDING_PAGES.get(lang, LANG_LANDING_PAGES["en"])

        for query in queries:
            print(f"    Searching: \"{query}\"")
            urls = search_google(query, num_results=5)

            for url in urls:
                if "socialtradingvlog.com" in url:
                    continue
                has_link = check_page_for_our_link(url)
                if not has_link:
                    contact = find_contact_info(url)
                    prospect = {
                        "type": "resource_page",
                        "url": url,
                        "query": query,
                        "language": lang,
                        "landing_page": landing,
                        "has_our_link": False,
                        "contact": contact,
                        "found_at": datetime.now().isoformat(),
                        "status": "new",
                        "outreach_template": "resource_page",
                    }
                    prospects.append(prospect)
                time.sleep(1)

    # Also check broken links in other languages
    for lang, queries in MULTILANG_BROKEN_LINK_QUERIES.items():
        for query in queries:
            print(f"    [{lang.upper()}] Broken link search: \"{query}\"")
            urls = search_google(query, num_results=3)
            for url in urls:
                if "socialtradingvlog.com" in url:
                    continue
                try:
                    req = urllib.request.Request(url, headers=HEADERS)
                    resp = urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
                    html = resp.read().decode("utf-8", errors="ignore")
                    links = re.findall(r'href="(https?://[^"]+)"', html)
                    broken_found = []
                    for link in links[:15]:
                        if any(skip in link for skip in ["google.com", "facebook.com", "twitter.com", "youtube.com"]):
                            continue
                        try:
                            check_req = urllib.request.Request(link, headers=HEADERS, method="HEAD")
                            urllib.request.urlopen(check_req, timeout=5, context=SSL_CTX)
                        except urllib.error.HTTPError as e:
                            if e.code in (404, 410):
                                broken_found.append({"url": link, "status": e.code})
                        except Exception:
                            pass
                        time.sleep(0.3)

                    if broken_found:
                        contact = find_contact_info(url, html)
                        prospect = {
                            "type": "broken_link",
                            "page_url": url,
                            "language": lang,
                            "broken_links": broken_found,
                            "contact": contact,
                            "found_at": datetime.now().isoformat(),
                            "status": "new",
                            "outreach_template": "broken_link",
                        }
                        prospects.append(prospect)
                        print(f"      Found {len(broken_found)} broken links on: {url}")
                except Exception:
                    pass
                time.sleep(1)

    print(f"\n  Multi-language total: {len(prospects)} prospects across {len(MULTILANG_RESOURCE_QUERIES)} languages")
    return prospects


# ─── Outreach Templates ───────────────────────────────────────────────────

OUTREACH_TEMPLATES = {
    "brand_mention": {
        "subject": "Thanks for mentioning Social Trading Vlog — quick request",
        "body": """Hi,

I'm reaching out on behalf of the Social Trading Vlog team. I noticed you mentioned Social Trading Vlog on your page ({page_url}).

Thanks for the mention! Would you be able to add a link to our site (https://socialtradingvlog.com) where you mention us? We have free trading calculators and comparison tools that your readers might find useful.

Happy to return the favour — let me know if there's anything we can help with.

Best regards,
The SocialTradingVlog Team
https://socialtradingvlog.com""",
    },
    "resource_page": {
        "subject": "Free trading tools for your resource page",
        "body": """Hi,

I'm reaching out on behalf of SocialTradingVlog.com. I came across your resource page ({page_url}) and thought our free trading tools might be a useful addition for your readers:

- Fee Calculator: https://socialtradingvlog.com/calculators/fee-calculator/
- Platform Comparison: https://socialtradingvlog.com/calculators/compare-platforms/
- ROI Calculator: https://socialtradingvlog.com/calculators/roi-calculator/

They're completely free, no signup required, and the data is verified and updated weekly.

Would you consider adding us to your list?

Best regards,
The SocialTradingVlog Team
https://socialtradingvlog.com""",
    },
    "broken_link": {
        "subject": "Heads up — broken link on your page",
        "body": """Hi,

I'm reaching out on behalf of SocialTradingVlog.com. While browsing your page ({page_url}), I noticed a broken link:
{broken_url} — returns a {status_code} error

If you're looking for a replacement, we have a free trading comparison tool that covers similar ground:
https://socialtradingvlog.com/calculators/compare-platforms/

No pressure at all — just thought I'd flag the broken link either way.

Best regards,
The SocialTradingVlog Team
https://socialtradingvlog.com""",
    },
}


def send_outreach_email(to_addr, subject, body):
    """Send an outreach email via Resend API."""
    config_file = SECRETS_DIR / "email-alerts.json"
    if not config_file.exists():
        return False

    config = json.loads(config_file.read_text())

    payload = json.dumps({
        "from": config.get("outreach_from", config["from_email"]),
        "to": [to_addr],
        "subject": subject,
        "text": body,
        "reply_to": config.get("outreach_reply_to", config["from_email"]),
    }).encode()

    try:
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['api_key']}",
            },
        )
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.getcode() == 200
    except Exception as e:
        print(f"    Failed to send to {to_addr}: {e}")
        return False


def generate_and_send_outreach(prospects, dry_run=False):
    """Generate and auto-send outreach emails. Max 5 per run to avoid spam."""
    MAX_PER_RUN = 5
    sent_log_file = OUTREACH_DIR / "link-outreach-sent.json"

    # Load sent history to avoid re-contacting
    sent_history = []
    if sent_log_file.exists():
        try:
            sent_history = json.loads(sent_log_file.read_text())
        except Exception:
            sent_history = []
    sent_emails = set(s.get("to", "") for s in sent_history)

    emails_to_send = []
    for prospect in prospects:
        template_key = prospect.get("outreach_template")
        template = OUTREACH_TEMPLATES.get(template_key)
        if not template:
            continue

        contact = prospect.get("contact", {})
        if not contact.get("emails"):
            continue

        for email_addr in contact["emails"][:1]:
            if email_addr in sent_emails:
                continue  # Already contacted

            email_data = {
                "to": email_addr,
                "subject": template["subject"],
                "body": template["body"].format(
                    page_url=prospect.get("url") or prospect.get("page_url", ""),
                    broken_url=prospect.get("broken_links", [{}])[0].get("url", "") if prospect.get("broken_links") else "",
                    status_code=prospect.get("broken_links", [{}])[0].get("status", "") if prospect.get("broken_links") else "",
                ),
                "prospect_type": prospect["type"],
                "generated_at": datetime.now().isoformat(),
            }
            emails_to_send.append(email_data)

    # Limit to MAX_PER_RUN
    batch = emails_to_send[:MAX_PER_RUN]

    sent_count = 0
    for email_data in batch:
        if dry_run:
            print(f"    [DRY RUN] Would send to: {email_data['to']}")
            sent_count += 1
        else:
            success = send_outreach_email(email_data["to"], email_data["subject"], email_data["body"])
            if success:
                email_data["status"] = "sent"
                email_data["sent_at"] = datetime.now().isoformat()
                sent_history.append(email_data)
                sent_count += 1
                print(f"    ✓ Sent to: {email_data['to']}")
                time.sleep(5)  # 5 second delay between emails
            else:
                email_data["status"] = "failed"
                sent_history.append(email_data)

    if not dry_run and sent_count > 0:
        OUTREACH_DIR.mkdir(parents=True, exist_ok=True)
        sent_log_file.write_text(json.dumps(sent_history, indent=2))

    print(f"\n  Sent {sent_count}/{len(emails_to_send)} outreach emails (max {MAX_PER_RUN}/run)")
    return sent_count


# ─── Main ──────────────────────────────────────────────────────────────────

def load_prospects():
    """Load existing prospects."""
    if PROSPECTS_FILE.exists():
        try:
            return json.loads(PROSPECTS_FILE.read_text())
        except Exception:
            return []
    return []


def save_prospects(prospects, dry_run=False):
    """Save prospects, deduplicating by URL."""
    existing = load_prospects()

    # Deduplicate by URL
    existing_urls = set()
    for p in existing:
        url = p.get("url") or p.get("page_url", "")
        existing_urls.add(url)

    new_count = 0
    for p in prospects:
        url = p.get("url") or p.get("page_url", "")
        if url not in existing_urls:
            existing.append(p)
            existing_urls.add(url)
            new_count += 1

    if not dry_run:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PROSPECTS_FILE.write_text(json.dumps(existing, indent=2))

    return new_count


def main():
    parser = argparse.ArgumentParser(description="Link Building Prospector")
    parser.add_argument("--type", choices=["mentions", "resources", "broken", "multilang", "all"],
                        default="all", help="Type of prospecting to run")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    parser.add_argument("--lang", type=str, default=None,
                        help="Limit multi-language search to specific language (es, de, fr, pt, etc.)")
    args = parser.parse_args()

    print(f"Link Prospector — {datetime.now().isoformat()}")
    all_prospects = []

    if args.type in ("mentions", "all"):
        all_prospects.extend(find_brand_mentions())

    if args.type in ("resources", "all"):
        all_prospects.extend(find_resource_pages())

    if args.type in ("broken", "all"):
        all_prospects.extend(find_broken_link_opportunities())

    if args.type in ("multilang", "all"):
        # Filter to specific language if --lang flag given
        if args.lang:
            global MULTILANG_RESOURCE_QUERIES, MULTILANG_BROKEN_LINK_QUERIES
            MULTILANG_RESOURCE_QUERIES = {k: v for k, v in MULTILANG_RESOURCE_QUERIES.items() if k == args.lang}
            MULTILANG_BROKEN_LINK_QUERIES = {k: v for k, v in MULTILANG_BROKEN_LINK_QUERIES.items() if k == args.lang}
        all_prospects.extend(find_multilang_opportunities())

    # Save prospects
    new_count = save_prospects(all_prospects, dry_run=args.dry_run)
    print(f"\nTotal prospects found: {len(all_prospects)} ({new_count} new)")

    # Generate and send outreach emails
    generate_and_send_outreach(all_prospects, dry_run=args.dry_run)

    # Try to alert via autopilot
    if new_count > 0:
        try:
            from site_autopilot import send_alert
            send_alert("link_building",
                       f"Found {new_count} new link-building opportunities",
                       "info",
                       f"Run 'python3 tools/link_prospector.py' to see details")
        except ImportError:
            pass

    print("\nDone.")


if __name__ == "__main__":
    main()
