#!/usr/bin/env python3
"""
Translate the site HTML pages into multiple languages.

Creates translated versions at /{lang}/page.html, e.g.:
    /es/index.html, /es/social-trading.html, etc.
    /fr/index.html, /fr/social-trading.html, etc.

Usage:
    python3 tools/translate_site.py [--langs es fr de it pt] [--pages index.html social-trading.html]
    python3 tools/translate_site.py               # translate all pages into all languages
    python3 tools/translate_site.py --langs es fr  # Spanish and French only
    python3 tools/translate_site.py --pages index.html --langs es  # just homepage to Spanish

Note: Translates <title>, meta description, and all text content
      (headings, paragraphs, lists). Navigation labels and buttons
      are preserved as-is (they're already short/simple).
      Uses Google Translate (free, no API key needed).
"""

import sys
import os
import time
import pathlib
import argparse

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup, NavigableString

LANGUAGES = {
    "es": ("Spanish", "es"),
    "fr": ("French", "fr"),
    "de": ("German", "de"),
    "it": ("Italian", "it"),
    "pt": ("Portuguese", "pt"),
    "nl": ("Dutch", "nl"),
    "pl": ("Polish", "pl"),
    "ru": ("Russian", "ru"),
    "ja": ("Japanese", "ja"),
    "zh-CN": ("Chinese (Simplified)", "zh-CN"),
    "ar": ("Arabic", "ar"),
}

PAGES = [
    "index.html",
    "social-trading.html",
    "copy-trading.html",
    "etoro-scam.html",
    "copy-trading-returns.html",
    "taking-profits.html",
    "popular-investor.html",
    "about.html",
    "faq.html",
    "updates.html",
]

# Tags whose text content should be translated
TRANSLATE_TAGS = {"h1", "h2", "h3", "h4", "p", "li", "dt", "dd", "figcaption", "blockquote"}

# Tags to skip entirely (don't translate nav/footer labels to keep them consistent)
SKIP_CLASSES = {"nav-logo", "nav-links", "nav-drawer", "footer-bottom"}


def translate_text(text, translator):
    text = text.strip()
    if not text or len(text) < 3:
        return text
    # Don't translate things that look like pure numbers, symbols, or risk warning boilerplate
    try:
        result = translator.translate(text)
        time.sleep(0.07)
        return result or text
    except Exception as e:
        print(f"  Warning: translation error: {e}")
        return text


def should_skip(tag):
    """Return True if this tag is inside a nav or footer (skip translation)."""
    for parent in tag.parents:
        if parent.name in ("nav", "footer"):
            return True
        if hasattr(parent, "get"):
            classes = parent.get("class", [])
            if any(c in SKIP_CLASSES for c in classes):
                return True
    return False


def translate_page(src_path, output_path, lang_code, lang_name):
    content = src_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(content, "html.parser")
    translator = GoogleTranslator(source="en", target=lang_code)

    # Set lang attribute on <html>
    html_tag = soup.find("html")
    if html_tag:
        html_tag["lang"] = lang_code

    # Translate <title>
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        title_tag.string = translate_text(str(title_tag.string), translator)

    # Translate meta description
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        meta["content"] = translate_text(meta["content"], translator)

    # Update og:title and og:description
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        og_title["content"] = translate_text(og_title["content"], translator)

    og_desc = soup.find("meta", attrs={"property": "og:description"})
    if og_desc and og_desc.get("content"):
        og_desc["content"] = translate_text(og_desc["content"], translator)

    # Add/update canonical to point to the English source
    head = soup.find("head")
    if head:
        existing_canonical = soup.find("link", attrs={"rel": "canonical"})
        canon_url = f"https://socialtradingvlog.com/{src_path.name}"
        if existing_canonical:
            existing_canonical["href"] = canon_url
        else:
            head.append(soup.new_tag("link", rel="canonical", href=canon_url))

    # Add hreflang alternate links
    if head:
        hreflang_en = soup.new_tag(
            "link", rel="alternate", hreflang="en",
            href=f"https://socialtradingvlog.com/{src_path.name}"
        )
        head.append(hreflang_en)
        hreflang_self = soup.new_tag(
            "link", rel="alternate", hreflang=lang_code,
            href=f"https://socialtradingvlog.com/{lang_code}/{src_path.name}"
        )
        head.append(hreflang_self)

    # Translate content tags
    tags = soup.find_all(TRANSLATE_TAGS)
    for tag in tags:
        if should_skip(tag):
            continue
        # Only translate if the tag has direct text content (not just child tags)
        if tag.string and tag.string.strip():
            original = str(tag.string).strip()
            if len(original) > 2:
                tag.string = translate_text(original, translator)

    # Fix internal links to point back to English root (language pages link to /en/ pages)
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Relative links like "social-trading.html" -> "../social-trading.html"
        if href and not href.startswith(("http", "#", "mailto", "/")):
            a["href"] = f"../{href}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(str(soup), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Translate site pages into multiple languages")
    parser.add_argument(
        "--langs",
        nargs="+",
        default=["es", "fr", "de", "it", "pt"],
        metavar="LANG",
        help=f"Language codes. Available: {', '.join(LANGUAGES)}. Default: es fr de it pt",
    )
    parser.add_argument(
        "--pages",
        nargs="+",
        default=PAGES,
        metavar="PAGE",
        help="HTML files to translate (default: all main pages)",
    )
    args = parser.parse_args()

    site_root = pathlib.Path(__file__).parent.parent

    for lang_code in args.langs:
        if lang_code not in LANGUAGES:
            print(f"Unknown language: {lang_code}. Available: {', '.join(LANGUAGES)}")
            continue

        lang_name, _ = LANGUAGES[lang_code]
        print(f"\nTranslating to {lang_name} ({lang_code})...")

        lang_dir = site_root / lang_code
        lang_dir.mkdir(exist_ok=True)

        for page in args.pages:
            src = site_root / page
            if not src.exists():
                print(f"  Skipping {page} (not found)")
                continue

            output = lang_dir / page
            if output.exists():
                print(f"  {page}: already exists (skipping)")
                continue

            print(f"  Translating {page}...")
            translate_page(src, output, lang_code, lang_name)
            print(f"  -> {lang_code}/{page}")

    print("\nAll done!")
    print("Translated pages are in subdirectories: es/, fr/, de/, it/, pt/")
    print("Add these to your sitemap.xml for multilingual SEO.")


if __name__ == "__main__":
    main()
