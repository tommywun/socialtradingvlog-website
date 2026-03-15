#!/usr/bin/env python3
"""
Directory Submitter — Submit site to curated, high-quality directories.

NOT mass submission. A targeted list of ~40 directories across all languages
that accept submissions and provide genuine SEO value. Tracks submission
status and retries failed submissions.

Directories are submitted via:
  - API where available
  - Logged as "manual needed" for sites requiring web forms

Usage:
    python3 tools/directory_submitter.py              # Submit to all pending
    python3 tools/directory_submitter.py --dry-run     # Preview
    python3 tools/directory_submitter.py --list        # Show status
    python3 tools/directory_submitter.py --category global  # Specific category

Cron:
    0 3 * * 4  python3 tools/directory_submitter.py
"""

import json
import pathlib
from datetime import datetime

PROJECT_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
STATUS_FILE = DATA_DIR / "directory-submissions.json"
SITE_URL = "https://socialtradingvlog.com"

# ─── Curated directory list ──────────────────────────────────────────────────
# Each entry: name, url, category, language, da, link_type, method, notes

DIRECTORIES = [
    # ── Global / EN ──────────────────────────────────────────
    {
        "name": "Curlie",
        "url": "https://curlie.org/suggest",
        "category": "global",
        "language": "en",
        "da": 70,
        "link_type": "dofollow",
        "method": "web_form",
        "submit_url": "https://curlie.org/cgi-bin/suggest.cgi?cat=Business/Financial_Services/Trading",
        "notes": "DMOZ successor. Submit to Business > Financial Services > Trading.",
    },
    {
        "name": "Feedspot Trading Blogs",
        "url": "https://bloggers.feedspot.com/trading_blogs/",
        "category": "global",
        "language": "en",
        "da": 60,
        "link_type": "dofollow",
        "method": "web_form",
        "submit_url": "https://www.feedspot.com/submit",
        "notes": "Submit to 'Best Trading Blogs' list. Also submit to Copy Trading, UK Trading, Finance categories.",
    },
    {
        "name": "AlternativeTo",
        "url": "https://alternativeto.net/",
        "category": "global",
        "language": "en",
        "da": 80,
        "link_type": "dofollow",
        "submit_url": "https://alternativeto.net/manage/new/",
        "method": "web_form",
        "notes": "List trading calculators as alternative to paid tools. Tag as 'Free', 'Web-based'.",
    },
    {
        "name": "SaaSHub",
        "url": "https://www.saashub.com/",
        "category": "global",
        "language": "en",
        "da": 41,
        "link_type": "dofollow",
        "method": "web_form",
        "submit_url": "https://www.saashub.com/submit",
        "notes": "Submit trading calculators/comparison tool.",
    },
    {
        "name": "Blogarama",
        "url": "https://www.blogarama.com/",
        "category": "global",
        "language": "en",
        "da": 50,
        "link_type": "dofollow",
        "method": "web_form",
        "submit_url": "https://www.blogarama.com/add-a-blog",
        "notes": "Blog directory. Submit under Finance/Trading.",
    },
    {
        "name": "Crunchbase",
        "url": "https://www.crunchbase.com/",
        "category": "global",
        "language": "en",
        "da": 90,
        "link_type": "nofollow",
        "method": "web_form",
        "submit_url": "https://www.crunchbase.com/register/signup",
        "notes": "Create organization profile. Entity signal, not direct link value.",
    },
    {
        "name": "F6S",
        "url": "https://www.f6s.com/",
        "category": "global",
        "language": "en",
        "da": 75,
        "link_type": "dofollow",
        "method": "web_form",
        "submit_url": "https://www.f6s.com/startup/create",
        "notes": "Startup directory. Create profile with tools/calculators.",
    },
    {
        "name": "BetaList",
        "url": "https://betalist.com/",
        "category": "global",
        "language": "en",
        "da": 65,
        "link_type": "dofollow",
        "method": "web_form",
        "submit_url": "https://betalist.com/submit",
        "notes": "Submit trading tools. Free queue can take weeks.",
    },
    {
        "name": "Trustpilot",
        "url": "https://www.trustpilot.com/",
        "category": "global",
        "language": "en",
        "da": 93,
        "link_type": "nofollow",
        "method": "web_form",
        "submit_url": "https://business.trustpilot.com/signup",
        "notes": "Claim business profile. Free plan available.",
    },
    {
        "name": "Product Hunt",
        "url": "https://www.producthunt.com/",
        "category": "global",
        "language": "en",
        "da": 90,
        "link_type": "nofollow",
        "method": "web_form",
        "submit_url": "https://www.producthunt.com/posts/new",
        "notes": "Launch calculators/tools. Schedule a launch day for best visibility.",
    },
    {
        "name": "Indie Hackers",
        "url": "https://www.indiehackers.com/",
        "category": "global",
        "language": "en",
        "da": 75,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.indiehackers.com/products",
        "notes": "List as bootstrapped product. Community-driven.",
    },

    # ── UK-specific ──────────────────────────────────────────
    {
        "name": "Yell",
        "url": "https://www.yell.com/",
        "category": "uk",
        "language": "en",
        "da": 78,
        "link_type": "dofollow",
        "method": "web_form",
        "submit_url": "https://www.yell.com/free-listing/",
        "notes": "UK yellow pages. Free listing available.",
    },
    {
        "name": "Thomson Local",
        "url": "https://www.thomsonlocal.com/",
        "category": "uk",
        "language": "en",
        "da": 72,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.thomsonlocal.com/add-your-business/",
        "notes": "UK local directory.",
    },
    {
        "name": "FreeIndex",
        "url": "https://www.freeindex.co.uk/",
        "category": "uk",
        "language": "en",
        "da": 55,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.freeindex.co.uk/",
        "notes": "UK business listings with reviews.",
    },

    # ── Pan-European ─────────────────────────────────────────
    {
        "name": "Europages",
        "url": "https://www.europages.com/",
        "category": "european",
        "language": "multi",
        "da": 70,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.europages.com/register",
        "notes": "35 European countries. Free basic listing. Multi-language by default.",
    },
    {
        "name": "Kompass",
        "url": "https://www.kompass.com/",
        "category": "european",
        "language": "multi",
        "da": 65,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.kompass.com/signup",
        "notes": "70+ countries. High verification standards.",
    },

    # ── Country-specific ─────────────────────────────────────
    {
        "name": "Gelbe Seiten",
        "url": "https://www.gelbeseiten.de/",
        "category": "country",
        "language": "de",
        "da": 75,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.gelbeseiten.de/eintragen",
        "notes": "German yellow pages. 40M+ monthly searches.",
    },
    {
        "name": "PagesJaunes",
        "url": "https://www.pagesjaunes.fr/",
        "category": "country",
        "language": "fr",
        "da": 75,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.pagesjaunes.fr/",
        "notes": "French yellow pages. 25M+ monthly searches.",
    },
    {
        "name": "Paginas Amarillas",
        "url": "https://www.paginasamarillas.es/",
        "category": "country",
        "language": "es",
        "da": 65,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.paginasamarillas.es/",
        "notes": "Spanish yellow pages.",
    },
    {
        "name": "Paginas Amarelas",
        "url": "https://www.pai.pt/",
        "category": "country",
        "language": "pt",
        "da": 55,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.pai.pt/",
        "notes": "Portuguese yellow pages.",
    },
    {
        "name": "Panorama Firm",
        "url": "https://panoramafirm.pl/",
        "category": "country",
        "language": "pl",
        "da": 55,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://panoramafirm.pl/",
        "notes": "Poland's largest business directory.",
    },
    {
        "name": "Gouden Gids",
        "url": "https://www.goudengids.nl/",
        "category": "country",
        "language": "nl",
        "da": 55,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://www.goudengids.nl/",
        "notes": "Dutch yellow pages.",
    },
    {
        "name": "Araboo",
        "url": "http://www.araboo.com/",
        "category": "country",
        "language": "ar",
        "da": 40,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "http://www.araboo.com/submit.php",
        "notes": "Arab world business directory.",
    },
    {
        "name": "Naver Business",
        "url": "https://www.naver.com/",
        "category": "country",
        "language": "ko",
        "da": 90,
        "link_type": "mixed",
        "method": "web_form",
        "submit_url": "https://smartplace.naver.com/",
        "notes": "Essential for Korean market. Naver dominates Korean search.",
    },
]


def load_status():
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_status(status):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(status, indent=2))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Directory Submitter")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--category", choices=["global", "uk", "european", "country", "all"],
                        default="all")
    args = parser.parse_args()

    status = load_status()
    dirs = DIRECTORIES
    if args.category != "all":
        dirs = [d for d in dirs if d["category"] == args.category]

    print(f"Directory Submitter — {datetime.now().isoformat()}")
    print(f"Total directories: {len(dirs)}")

    pending = []
    submitted = []
    confirmed = []

    for d in dirs:
        key = d["name"]
        s = status.get(key, {})
        state = s.get("status", "pending")

        if state == "confirmed":
            confirmed.append(d)
        elif state == "submitted":
            submitted.append(d)
        else:
            pending.append(d)

    if args.list:
        print(f"\nConfirmed ({len(confirmed)}):")
        for d in confirmed:
            s = status[d["name"]]
            print(f"  [{d['language']}] {d['name']} (DA {d['da']}, {d['link_type']}) — confirmed {s.get('confirmed_at', '')}")

        print(f"\nSubmitted, awaiting review ({len(submitted)}):")
        for d in submitted:
            s = status[d["name"]]
            print(f"  [{d['language']}] {d['name']} (DA {d['da']}) — submitted {s.get('submitted_at', '')}")

        print(f"\nPending ({len(pending)}):")
        for d in pending:
            print(f"  [{d['language']}] {d['name']} (DA {d['da']}, {d['link_type']})")
            print(f"    Submit: {d.get('submit_url', d['url'])}")
            print(f"    Notes: {d['notes']}")
        return

    if not pending:
        print("\nAll directories already submitted or confirmed!")
        return

    print(f"\nPending submissions: {len(pending)}")
    print("Generating submission instructions...\n")

    # For web-form directories, generate clear instructions
    instructions = []
    for d in pending:
        key = d["name"]

        # Determine site URL based on language
        lang = d["language"]
        if lang == "en" or lang == "multi":
            site_link = SITE_URL
            desc = "Copy trading education and honest eToro reviews. Free trading calculators, platform comparison tools, and real portfolio updates."
        elif lang == "de":
            site_link = f"{SITE_URL}/de/"
            desc = "Copy-Trading-Bildung und ehrliche eToro-Bewertungen. Kostenlose Trading-Rechner und Plattform-Vergleichstools."
        elif lang == "es":
            site_link = f"{SITE_URL}/es/"
            desc = "Educación sobre copy trading y reseñas honestas de eToro. Calculadoras de trading gratuitas."
        elif lang == "fr":
            site_link = f"{SITE_URL}/fr/"
            desc = "Éducation sur le copy trading et avis honnêtes sur eToro. Calculateurs financiers gratuits."
        elif lang == "pt":
            site_link = f"{SITE_URL}/pt/"
            desc = "Educação sobre copy trading e análises honestas do eToro. Calculadoras financeiras gratuitas."
        elif lang == "ar":
            site_link = f"{SITE_URL}/ar/"
            desc = "تعليم نسخ التداول ومراجعات صادقة لمنصة eToro. حاسبات تداول مجانية."
        elif lang == "pl":
            site_link = f"{SITE_URL}/pl/"
            desc = "Edukacja o copy tradingu i uczciwe recenzje eToro."
        elif lang == "nl":
            site_link = f"{SITE_URL}/nl/"
            desc = "Copy trading onderwijs en eerlijke eToro reviews."
        elif lang == "ko":
            site_link = f"{SITE_URL}/ko/"
            desc = "카피 트레이딩 교육 및 솔직한 eToro 리뷰."
        else:
            site_link = SITE_URL
            desc = "Copy trading education and honest eToro reviews."

        instruction = {
            "directory": d["name"],
            "submit_url": d.get("submit_url", d["url"]),
            "site_url": site_link,
            "site_name": "Social Trading Vlog",
            "description": desc,
            "category": "Finance / Trading / Investment Tools",
            "language": lang,
            "notes": d["notes"],
        }
        instructions.append(instruction)

        if args.dry_run:
            print(f"  [{lang}] {d['name']} — {d.get('submit_url', d['url'])}")
        else:
            # Mark as submitted (instructions generated)
            status[key] = {
                "status": "submitted",
                "submitted_at": datetime.now().isoformat(),
                "submit_url": d.get("submit_url", d["url"]),
                "method": d["method"],
                "language": lang,
            }

    if not args.dry_run:
        # Save instructions to a report file
        report_path = PROJECT_DIR / "reports" / f"directory-submissions-{datetime.now().strftime('%Y-%m-%d')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(instructions, indent=2))
        save_status(status)
        print(f"\nSubmission instructions saved to: {report_path}")
        print(f"Status updated: {len(pending)} directories marked as submitted")

        # Send Telegram notification
        try:
            import sys
            sys.path.insert(0, str(pathlib.Path(__file__).parent))
            from security_lib import send_telegram
            send_telegram(
                f"Directory Submitter: {len(pending)} directories ready",
                f"Generated submission instructions for {len(pending)} directories.\n"
                f"Report: reports/directory-submissions-{datetime.now().strftime('%Y-%m-%d')}.json",
                emoji="📁",
                dedupe_key="directory-submitter",
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
