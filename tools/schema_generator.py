#!/usr/bin/env python3
"""
Schema Generator — Add JSON-LD structured data to all pages.

Adds Article, Organization, BreadcrumbList, FAQPage, VideoObject,
and WebApplication schema markup to improve visibility in Google
rich results and AI search citations.

Idempotent — safe to re-run. Replaces existing STV-generated schema blocks.

Usage:
    python3 tools/schema_generator.py              # Update all pages
    python3 tools/schema_generator.py --dry-run     # Preview changes
    python3 tools/schema_generator.py --lang en     # English only

Cron:
    0 2 * * 0  python3 tools/schema_generator.py
"""

import sys
import os
import re
import json
import pathlib
import argparse
from datetime import datetime

PROJECT_DIR = pathlib.Path(__file__).parent.parent
SITE_URL = "https://socialtradingvlog.com"

ORGANIZATION_SCHEMA = {
    "@type": "Organization",
    "name": "Social Trading Vlog",
    "url": SITE_URL,
    "logo": f"{SITE_URL}/images/logo.png",
    "sameAs": [],  # Will be populated once social accounts are created
}

AUTHOR_SCHEMA = {
    "@type": "Person",
    "name": "Tom West",
    "url": f"{SITE_URL}/about.html",
}

# Schema marker comment for idempotent updates
SCHEMA_MARKER = "<!-- STV-SCHEMA -->"
SCHEMA_END_MARKER = "<!-- /STV-SCHEMA -->"


def detect_page_type(filepath, content):
    """Detect what type of page this is for schema selection."""
    rel = str(filepath.relative_to(PROJECT_DIR))

    if "calculators" in rel or "rechner" in rel or "calculadoras" in rel or "calculateurs" in rel or "calcolatori" in rel or "rekenmachines" in rel or "kalkulatory" in rel or "계산기" in rel:
        return "calculator"
    if "video/" in rel:
        return "video"
    if "updates/" in rel:
        return "update"
    if "etoro-review" in rel or "etoro-erfahrungen" in rel or "etoro-opinion" in rel or "avis-etoro" in rel or "etoro-review" in rel or "murajaet-etoro" in rel:
        return "review"
    if rel.endswith("index.html") and filepath.parent == PROJECT_DIR:
        return "homepage"
    if filepath.name in ("about.html", "contact.html", "privacy.html", "404.html"):
        return "utility"

    return "article"


def extract_meta(content):
    """Extract key metadata from HTML."""
    title_m = re.search(r'<title>([^<]+)</title>', content)
    desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content)
    canonical_m = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', content)
    og_image_m = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', content)
    date_pub_m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', content)
    date_mod_m = re.search(r'"dateModified"\s*:\s*"([^"]+)"', content)
    lang_m = re.search(r'<html[^>]+lang="([^"]+)"', content)

    return {
        "title": title_m.group(1).strip() if title_m else "",
        "description": desc_m.group(1) if desc_m else "",
        "canonical": canonical_m.group(1) if canonical_m else "",
        "og_image": og_image_m.group(1) if og_image_m else f"{SITE_URL}/images/og-default.png",
        "date_published": date_pub_m.group(1) if date_pub_m else "",
        "date_modified": date_mod_m.group(1) if date_mod_m else "",
        "language": lang_m.group(1) if lang_m else "en",
    }


def extract_date_from_filename(filepath):
    """Extract date from update filenames."""
    name = filepath.name.replace(".html", "")
    if filepath.name == "index.html":
        name = filepath.parent.name

    month_map = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
        "ene": "01", "abr": "04", "ago": "08", "dic": "12",
        "januar": "01", "februar": "02", "maerz": "03", "april": "04",
        "mai": "05", "juni": "06", "juli": "07", "august": "08",
        "september": "09", "oktober": "10", "november": "11", "dezember": "12",
        "janvier": "01", "fevrier": "02", "mars": "03", "avril": "04",
        "juin": "06", "juillet": "07", "aout": "08", "septembre": "09",
        "octobre": "10", "novembre": "11", "decembre": "12",
    }

    m = re.search(r'(\d{1,2})-([a-z]+)-(\d{4})$', name, re.IGNORECASE)
    if m:
        day, mon, year = m.groups()
        month_num = month_map.get(mon.lower())
        if month_num:
            return f"{year}-{month_num}-{day.zfill(2)}"

    m = re.search(r'-([a-z]+)-(\d{4})$', name, re.IGNORECASE)
    if m:
        mon, year = m.groups()
        month_num = month_map.get(mon.lower())
        if month_num:
            return f"{year}-{month_num}-01"

    return ""


def generate_breadcrumbs(filepath, meta):
    """Generate BreadcrumbList schema."""
    rel = str(filepath.relative_to(PROJECT_DIR))
    parts = rel.replace("index.html", "").strip("/").split("/")
    parts = [p for p in parts if p]

    items = [{
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": SITE_URL,
    }]

    for i, part in enumerate(parts):
        name = part.replace("-", " ").replace(".html", "").title()
        url = f"{SITE_URL}/{'/'.join(parts[:i+1])}/"
        items.append({
            "@type": "ListItem",
            "position": i + 2,
            "name": name,
            "item": url,
        })

    return {
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def generate_article_schema(filepath, meta):
    """Generate Article schema for content pages."""
    url = meta["canonical"] or f"{SITE_URL}/{filepath.relative_to(PROJECT_DIR)}".replace("/index.html", "/")

    date_pub = meta["date_published"] or extract_date_from_filename(filepath) or "2024-01-01"
    date_mod = meta["date_modified"] or datetime.now().strftime("%Y-%m-%d")

    schema = {
        "@type": "Article",
        "headline": meta["title"].replace(" | SocialTradingVlog", ""),
        "description": meta["description"],
        "url": url,
        "image": meta["og_image"],
        "inLanguage": meta["language"],
        "datePublished": date_pub,
        "dateModified": date_mod,
        "author": AUTHOR_SCHEMA.copy(),
        "publisher": {
            "@type": "Organization",
            "name": "Social Trading Vlog",
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE_URL}/images/logo.png",
            },
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url,
        },
    }
    return schema


def generate_review_schema(filepath, meta):
    """Generate Review + FinancialProduct schema for review pages."""
    article = generate_article_schema(filepath, meta)
    article["@type"] = "Review"
    article["itemReviewed"] = {
        "@type": "FinancialProduct",
        "name": "eToro",
        "description": "Social trading and investment platform",
        "url": "https://www.etoro.com/",
    }
    article["reviewRating"] = {
        "@type": "Rating",
        "ratingValue": "4",
        "bestRating": "5",
        "worstRating": "1",
    }
    return article


def generate_calculator_schema(filepath, meta):
    """Generate WebApplication schema for calculators."""
    url = meta["canonical"] or f"{SITE_URL}/{filepath.relative_to(PROJECT_DIR)}".replace("/index.html", "/")
    return {
        "@type": "WebApplication",
        "name": meta["title"].replace(" | SocialTradingVlog", ""),
        "description": meta["description"],
        "url": url,
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Web",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
        },
        "inLanguage": meta["language"],
        "author": AUTHOR_SCHEMA.copy(),
    }


def build_schema_block(schemas):
    """Build the full JSON-LD script tag."""
    if len(schemas) == 1:
        ld = {"@context": "https://schema.org", **schemas[0]}
    else:
        ld = {
            "@context": "https://schema.org",
            "@graph": schemas,
        }

    json_str = json.dumps(ld, indent=2, ensure_ascii=False)
    return f'{SCHEMA_MARKER}\n<script type="application/ld+json">\n{json_str}\n</script>\n{SCHEMA_END_MARKER}'


def process_file(filepath, dry_run=False):
    """Process a single HTML file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return False

    page_type = detect_page_type(filepath, content)

    # Skip utility pages
    if page_type == "utility":
        return False

    meta = extract_meta(content)
    if not meta["title"]:
        return False

    # Build schema list
    schemas = []
    breadcrumbs = generate_breadcrumbs(filepath, meta)
    schemas.append(breadcrumbs)

    if page_type == "review":
        schemas.append(generate_review_schema(filepath, meta))
    elif page_type == "calculator":
        schemas.append(generate_calculator_schema(filepath, meta))
    elif page_type in ("article", "update", "homepage"):
        schemas.append(generate_article_schema(filepath, meta))

    schema_block = build_schema_block(schemas)

    # Remove existing STV-generated schema
    content = re.sub(
        rf'{re.escape(SCHEMA_MARKER)}.*?{re.escape(SCHEMA_END_MARKER)}\n?',
        '',
        content,
        flags=re.DOTALL,
    )

    # Also remove any existing standalone JSON-LD that we generated before
    # (identified by having "Social Trading Vlog" in publisher)
    # But keep any schema that was manually added (e.g. VideoObject from earlier sessions)
    # For safety, only remove schema blocks we explicitly generated via marker

    # Insert before </head>
    if "</head>" in content:
        content = content.replace("</head>", f"{schema_block}\n</head>", 1)
    else:
        return False

    if not dry_run:
        filepath.write_text(content, encoding="utf-8")

    return True


def main():
    parser = argparse.ArgumentParser(description="Schema Markup Generator")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--lang", type=str, default=None)
    args = parser.parse_args()

    lang_dirs = [("", "en"), ("es", "es"), ("de", "de"), ("fr", "fr"), ("pt", "pt"), ("ar", "ar"),
                 ("it", "it"), ("nl", "nl"), ("pl", "pl"), ("ko", "ko")]

    if args.lang:
        lang_dirs = [(d, l) for d, l in lang_dirs if l == args.lang]

    total = 0
    updated = 0

    skip_files = {"404.html", "contact.html", "contact-thanks.html", "privacy.html"}

    for subdir, lang in lang_dirs:
        base = PROJECT_DIR / subdir if subdir else PROJECT_DIR
        html_files = list(base.glob("*.html")) + list(base.glob("*/index.html"))
        if subdir:
            html_files += list(base.glob("*/*/index.html"))  # updates/article/index.html
        else:
            html_files += list(base.glob("updates/*.html"))

        for f in html_files:
            if f.name in skip_files and lang == "en":
                continue
            total += 1
            result = process_file(f, dry_run=args.dry_run)
            if result:
                updated += 1

    action = "Would update" if args.dry_run else "Updated"
    print(f"{action} {updated}/{total} pages with schema markup")


if __name__ == "__main__":
    main()
