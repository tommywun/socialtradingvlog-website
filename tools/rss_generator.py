#!/usr/bin/env python3
"""
Generate per-language RSS/Atom feeds for socialtradingvlog.com.

Scans HTML files, extracts metadata, and generates feed.xml for each
language variant. Feeds get auto-ingested by Flipboard, Feedly, Feedspot,
and other aggregators.

Usage:
    python3 tools/rss_generator.py              # Generate all feeds
    python3 tools/rss_generator.py --lang en     # English only
    python3 tools/rss_generator.py --dry-run     # Preview without writing

Cron:
    0 1 * * 1  python3 tools/rss_generator.py
"""

import sys
import os
import re
import json
import pathlib
import argparse
from datetime import datetime
from html.parser import HTMLParser
from xml.sax.saxutils import escape

PROJECT_DIR = pathlib.Path(__file__).parent.parent
SITE_URL = "https://socialtradingvlog.com"

# Language configs: subdirectory → language code + feed metadata
LANGUAGES = {
    "en": {
        "subdir": "",  # root
        "title": "Social Trading Vlog",
        "description": "Copy trading education and honest eToro reviews by Tom West.",
    },
    "es": {
        "subdir": "es",
        "title": "Social Trading Vlog — Español",
        "description": "Educación sobre copy trading y reseñas honestas de eToro por Tom West.",
    },
    "de": {
        "subdir": "de",
        "title": "Social Trading Vlog — Deutsch",
        "description": "Copy-Trading-Bildung und ehrliche eToro-Bewertungen von Tom West.",
    },
    "fr": {
        "subdir": "fr",
        "title": "Social Trading Vlog — Français",
        "description": "Éducation sur le copy trading et avis honnêtes sur eToro par Tom West.",
    },
    "pt": {
        "subdir": "pt",
        "title": "Social Trading Vlog — Português",
        "description": "Educação sobre copy trading e análises honestas do eToro por Tom West.",
    },
    "ar": {
        "subdir": "ar",
        "title": "Social Trading Vlog — العربية",
        "description": "تعليم نسخ التداول ومراجعات صادقة لمنصة eToro بقلم توم ويست.",
    },
}

# Directory names to skip in RSS (not articles — utility/nav pages)
SKIP_DIRS = {
    # EN
    "contact", "contact-thanks", "privacy", "faq", "videos", "about",
    "calculators", "author", "tag", "articles",
    # DE
    "kontakt", "haeufig-gestellte-fragen", "ueber-uns", "rechner",
    # ES
    "contacto", "preguntas-frecuentes", "sobre-nosotros", "calculadoras",
    # FR
    "contact", "foire-aux-questions", "questions-frequentes", "a-propos", "calculateurs",
    # PT
    "contato", "perguntas-frequentes", "sobre", "calculadoras",
    # AR
    "al-asilah-al-shaaiah", "an-na", "atisal-bina", "calculators",
}

# Root-level files to skip
SKIP_ROOT_FILES = {
    "404.html", "contact.html", "contact-thanks.html", "privacy.html",
    "faq.html", "videos.html", "index.html", "about.html",
}


class MetaExtractor(HTMLParser):
    """Extract title, meta description, canonical URL, dates from HTML."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.og_image = ""
        self.date_published = ""
        self.date_modified = ""
        self._in_title = False
        self._title_parts = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "title":
            self._in_title = True
            self._title_parts = []
        elif tag == "meta":
            name = d.get("name", "").lower()
            prop = d.get("property", "").lower()
            content = d.get("content", "")
            if name == "description":
                self.description = content
            elif prop == "og:image":
                self.og_image = content
        elif tag == "link":
            rel = d.get("rel", "")
            if rel == "canonical":
                self.canonical = d.get("href", "")

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.title = "".join(self._title_parts).strip()


def extract_date_from_filename(filename):
    """Try to parse a date from update filenames across all languages.

    Handles: copy-trading-update-01-sep-2025.html (EN)
             actualizacion-copy-trading-01-mar-2019 (ES dir)
             copy-trading-update-01-maerz-2019 (DE dir)
             mise-a-jour-copy-trading-28-novembre-2017 (FR dir)
             etc.
    """
    # Map localized month names → English abbreviation
    month_map = {
        # English
        "jan": "jan", "feb": "feb", "mar": "mar", "apr": "apr", "may": "may",
        "jun": "jun", "jul": "jul", "aug": "aug", "sep": "sep", "oct": "oct",
        "nov": "nov", "dec": "dec",
        # Spanish
        "ene": "jan", "abr": "apr", "ago": "aug", "dic": "dec",
        # German (full names in filenames)
        "januar": "jan", "februar": "feb", "maerz": "mar", "april": "apr",
        "mai": "may", "juni": "jun", "juli": "jul", "august": "aug",
        "september": "sep", "oktober": "oct", "november": "nov", "dezember": "dec",
        # French
        "janvier": "jan", "fevrier": "feb", "mars": "mar", "avril": "apr",
        "juin": "jun", "juillet": "jul", "aout": "aug", "septembre": "sep",
        "octobre": "oct", "novembre": "nov", "decembre": "dec",
        # Portuguese
        "janeiro": "jan", "fevereiro": "feb", "marco": "mar", "abril": "apr",
        "maio": "may", "junho": "jun", "julho": "jul", "agosto": "aug",
        "setembro": "sep", "outubro": "oct", "novembro": "nov", "dezembro": "dec",
    }

    # Strip .html and /index.html for directory-style names
    name = filename.replace(".html", "").replace("/index.html", "")

    # Pattern: DD-month-YYYY or just month-YYYY
    m = re.search(r'(\d{1,2})-([a-z]+)-(\d{4})$', name, re.IGNORECASE)
    if m:
        day, mon_raw, year = m.groups()
        mon = month_map.get(mon_raw.lower())
        if mon:
            try:
                return datetime.strptime(f"{day} {mon} {year}", "%d %b %Y")
            except ValueError:
                pass

    # Pattern: month-YYYY (no day)
    m = re.search(r'-([a-z]+)-(\d{4})$', name, re.IGNORECASE)
    if m:
        mon_raw, year = m.groups()
        mon = month_map.get(mon_raw.lower())
        if mon:
            try:
                return datetime.strptime(f"1 {mon} {year}", "%d %b %Y")
            except ValueError:
                pass

    return None


def extract_date_from_schema(html_content):
    """Try to extract datePublished/dateModified from JSON-LD schema."""
    for field in ["dateModified", "datePublished"]:
        m = re.search(rf'"{field}"\s*:\s*"([^"]+)"', html_content)
        if m:
            try:
                return datetime.fromisoformat(m.group(1))
            except ValueError:
                pass
    return None


def get_articles_for_language(lang_code, lang_config):
    """Scan HTML files and return list of article dicts for a language."""
    subdir = lang_config["subdir"]
    if subdir:
        base_path = PROJECT_DIR / subdir
    else:
        base_path = PROJECT_DIR

    articles = []

    # Collect HTML files
    html_files = []

    if lang_code == "en":
        # English: root-level .html files + subdirectory index.html files
        for f in base_path.glob("*.html"):
            html_files.append(f)
        for f in base_path.glob("*/index.html"):
            html_files.append(f)
        # Update articles
        updates_dir = base_path / "updates"
        if updates_dir.exists():
            for f in updates_dir.glob("*.html"):
                html_files.append(f)
    else:
        # Translated: all are subdir/article-name/index.html
        for f in base_path.glob("*/index.html"):
            html_files.append(f)
        # Update articles in translated dirs (updates/article-name/index.html)
        updates_dir = base_path / "updates"
        if updates_dir.exists():
            for f in updates_dir.glob("*/index.html"):
                html_files.append(f)

    for filepath in html_files:
        filename = filepath.name
        rel_path = filepath.relative_to(PROJECT_DIR)

        # Get the immediate parent directory name for skip checks
        parent_dir = filepath.parent.name

        # Skip non-article pages
        if lang_code == "en" and filename in SKIP_ROOT_FILES:
            continue
        if parent_dir in SKIP_DIRS:
            continue

        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            continue

        # Extract metadata
        parser = MetaExtractor()
        try:
            parser.feed(content)
        except Exception:
            continue

        title = parser.title
        if not title:
            continue

        # Strip " | SocialTradingVlog" suffix for cleaner feed
        title = re.sub(r'\s*\|\s*SocialTradingVlog\s*$', '', title)

        description = parser.description
        canonical = parser.canonical

        # Build URL if no canonical
        if not canonical:
            canonical = f"{SITE_URL}/{rel_path}"
            # Clean up index.html in URL
            canonical = canonical.replace("/index.html", "/")

        # Extract date
        pub_date = extract_date_from_schema(content)
        if not pub_date:
            pub_date = extract_date_from_filename(filename)
        if not pub_date:
            # For translated updates in dir/index.html format, try parent dir name
            pub_date = extract_date_from_filename(parent_dir)
        if not pub_date:
            # Use file modification time as last resort
            pub_date = datetime.fromtimestamp(filepath.stat().st_mtime)

        articles.append({
            "title": title,
            "description": description,
            "url": canonical,
            "date": pub_date,
            "image": parser.og_image,
        })

    # Sort by date descending (newest first)
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles


def generate_atom_feed(lang_code, lang_config, articles):
    """Generate Atom XML feed string."""
    title = escape(lang_config["title"])
    description = escape(lang_config["description"])
    subdir = lang_config["subdir"]
    feed_url = f"{SITE_URL}/{subdir}/feed.xml" if subdir else f"{SITE_URL}/feed.xml"
    site_link = f"{SITE_URL}/{subdir}/" if subdir else f"{SITE_URL}/"
    updated = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    entries = []
    for article in articles[:50]:  # Max 50 items
        entry_title = escape(article["title"])
        entry_desc = escape(article["description"] or article["title"])
        entry_url = escape(article["url"])
        entry_date = article["date"].strftime("%Y-%m-%dT%H:%M:%SZ")

        entry = f"""  <entry>
    <title>{entry_title}</title>
    <link href="{entry_url}" rel="alternate" type="text/html"/>
    <id>{entry_url}</id>
    <updated>{entry_date}</updated>
    <summary type="html">{entry_desc}</summary>
    <author><name>Tom West</name></author>
  </entry>"""
        entries.append(entry)

    feed = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{lang_code}">
  <title>{title}</title>
  <subtitle>{description}</subtitle>
  <link href="{escape(feed_url)}" rel="self" type="application/atom+xml"/>
  <link href="{escape(site_link)}" rel="alternate" type="text/html"/>
  <id>{escape(site_link)}</id>
  <updated>{updated}</updated>
  <author><name>Tom West</name></author>
  <generator>STV RSS Generator</generator>
{chr(10).join(entries)}
</feed>
"""
    return feed


def main():
    parser = argparse.ArgumentParser(description="Generate per-language RSS feeds")
    parser.add_argument("--lang", type=str, default=None, help="Generate for specific language only")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    args = parser.parse_args()

    langs = {args.lang: LANGUAGES[args.lang]} if args.lang else LANGUAGES
    total_articles = 0

    for lang_code, lang_config in langs.items():
        articles = get_articles_for_language(lang_code, lang_config)
        if not articles:
            print(f"[{lang_code}] No articles found — skipping")
            continue

        feed_xml = generate_atom_feed(lang_code, lang_config, articles)

        subdir = lang_config["subdir"]
        if subdir:
            feed_path = PROJECT_DIR / subdir / "feed.xml"
        else:
            feed_path = PROJECT_DIR / "feed.xml"

        if args.dry_run:
            print(f"[{lang_code}] Would write {feed_path} ({len(articles)} articles)")
            for a in articles[:5]:
                print(f"  - {a['title']} ({a['date'].strftime('%Y-%m-%d')})")
            if len(articles) > 5:
                print(f"  ... and {len(articles) - 5} more")
        else:
            feed_path.parent.mkdir(parents=True, exist_ok=True)
            feed_path.write_text(feed_xml, encoding="utf-8")
            print(f"[{lang_code}] Wrote {feed_path} ({len(articles)} articles)")

        total_articles += len(articles)

    print(f"\nTotal: {total_articles} articles across {len(langs)} languages")


if __name__ == "__main__":
    main()
