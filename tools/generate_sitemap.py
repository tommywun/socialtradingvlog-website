#!/usr/bin/env python3
"""
Sitemap Generator for socialtradingvlog.com

Scans the project directory for all index.html files, generates a proper
sitemap.xml with priorities, changefreq, lastmod dates, and hreflang
alternate links for multilingual pages.

Also generates robots.txt if one doesn't already exist.

Usage:
    python3 tools/generate_sitemap.py
"""

import os
import re
import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://socialtradingvlog.com"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LANGUAGES = ["en", "es", "de", "fr", "pt", "ar"]

# Directories to exclude entirely (relative to project root)
EXCLUDED_DIRS = {
    "data",
    "tools",
    "outreach",
    "node_modules",
    ".git",
    "review-staging",
    "css",
    "js",
    "images",
    "workers",
    "transcriptions",
    "reports",
    "checklist",
    "articles",
}

# Any path component containing these strings triggers exclusion
EXCLUDED_PATH_PARTS = {"review-staging"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def is_excluded(rel_path: str) -> bool:
    """Return True if the path should be excluded from the sitemap."""
    parts = Path(rel_path).parts
    for part in parts:
        if part in EXCLUDED_DIRS or part in EXCLUDED_PATH_PARTS:
            return True
    return False


def rel_to_url(rel_path: str) -> str:
    """Convert a relative file path (to project root) into a full URL.

    index.html          -> https://socialtradingvlog.com/
    etoro-review/index.html -> https://socialtradingvlog.com/etoro-review/
    video/slug/index.html   -> https://socialtradingvlog.com/video/slug/
    about.html              -> https://socialtradingvlog.com/about.html
    """
    # For index.html files, use the directory URL
    if rel_path == "index.html":
        return BASE_URL + "/"
    if rel_path.endswith("/index.html"):
        directory = rel_path[: -len("index.html")]
        return BASE_URL + "/" + directory
    # For standalone .html files
    return BASE_URL + "/" + rel_path


def get_lastmod(filepath: Path) -> str:
    """Return the file modification time as a YYYY-MM-DD string."""
    mtime = filepath.stat().st_mtime
    return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")


def classify_page(rel_path: str):
    """Classify a page and return (priority, changefreq).

    Priority rules:
        homepage = 1.0
        main articles (root-level slug dirs) = 0.8
        calculators = 0.8
        video pages = 0.6
        translated pages = 0.5
        standalone .html pages = 0.7
        updates = 0.4

    Changefreq rules:
        homepage = daily
        articles = weekly
        others = monthly
    """
    parts = Path(rel_path).parts
    lang_prefixes = {"es", "de", "fr", "pt", "ar"}

    # Homepage
    if rel_path == "index.html":
        return 1.0, "daily"

    # Check if it's a translated page
    is_translated = len(parts) > 0 and parts[0] in lang_prefixes

    # Strip language prefix for classification
    if is_translated:
        inner_parts = parts[1:]
    else:
        inner_parts = parts

    inner_path = "/".join(inner_parts)

    # Translated homepage (e.g. es/index.html — though these are dirs)
    # Not present in the current structure, but handle just in case

    # Calculators (English or translated)
    calculator_dirs = {"calculators", "calculadoras", "rechner", "calculateurs", "calculadoras"}
    if len(inner_parts) > 0 and inner_parts[0] in calculator_dirs:
        return (0.5 if is_translated else 0.8), "monthly"

    # Video pages
    if len(inner_parts) > 0 and inner_parts[0] == "video":
        return (0.5 if is_translated else 0.6), "monthly"

    # Update pages
    if len(inner_parts) > 0 and inner_parts[0] == "updates":
        return (0.3 if is_translated else 0.4), "monthly"

    # Root-level standalone .html files (about.html, faq.html, etc.)
    if not is_translated and len(inner_parts) == 1 and inner_parts[0].endswith(".html"):
        return 0.7, "monthly"

    # Main articles — root-level slug directories (e.g. etoro-review/index.html)
    if not is_translated and len(inner_parts) <= 2:
        return 0.8, "weekly"

    # Translated articles
    if is_translated:
        return 0.5, "monthly"

    # Fallback
    return 0.5, "monthly"


def extract_hreflang_alternates(filepath: Path) -> dict:
    """Parse an HTML file and extract hreflang alternate links.

    Returns a dict like {"en": "https://...", "es": "https://...", ...}
    """
    alternates = {}
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        # Match: <link rel="alternate" hreflang="xx" href="URL" />
        pattern = r'<link\s+rel="alternate"\s+hreflang="([^"]+)"\s+href="([^"]+)"'
        for match in re.finditer(pattern, content):
            lang = match.group(1)
            href = match.group(2)
            alternates[lang] = href
    except Exception:
        pass
    return alternates


# ---------------------------------------------------------------------------
# Main scanning and generation
# ---------------------------------------------------------------------------


def find_all_pages(root: Path) -> list:
    """Find all publishable HTML pages in the project.

    Returns a list of tuples: (rel_path, abs_path)
    where rel_path is relative to project root.
    """
    pages = []

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""

        # Prune excluded directories
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDED_DIRS and d not in EXCLUDED_PATH_PARTS
        ]

        for filename in filenames:
            if not filename.endswith(".html"):
                continue

            if rel_dir:
                rel_path = rel_dir + "/" + filename
            else:
                rel_path = filename

            # Skip if any path component is excluded
            if is_excluded(rel_path):
                continue

            abs_path = Path(dirpath) / filename
            pages.append((rel_path, abs_path))

    return pages


def generate_sitemap(root: Path) -> str:
    """Generate sitemap.xml content and write it to the project root.

    Returns a summary string.
    """
    pages = find_all_pages(root)

    # Sort pages: homepage first, then alphabetically
    def sort_key(item):
        rel_path = item[0]
        if rel_path == "index.html":
            return (0, "")
        return (1, rel_path)

    pages.sort(key=sort_key)

    # XML namespaces
    nsmap = {
        "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "xmlns:xhtml": "http://www.w3.org/1999/xhtml",
    }

    # Build XML manually for cleaner output with xhtml namespace
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')

    # Counters for summary
    count_total = 0
    count_with_alternates = 0
    count_by_type = {
        "homepage": 0,
        "article": 0,
        "calculator": 0,
        "video": 0,
        "translated": 0,
        "update": 0,
        "other": 0,
    }

    for rel_path, abs_path in pages:
        url = rel_to_url(rel_path)
        priority, changefreq = classify_page(rel_path)
        lastmod = get_lastmod(abs_path)

        # Extract hreflang alternates from the HTML file
        alternates = extract_hreflang_alternates(abs_path)

        # Build the <url> block
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")

        # Add hreflang alternate links if present
        if alternates:
            count_with_alternates += 1
            for lang, href in sorted(alternates.items()):
                lines.append(
                    f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{href}" />'
                )

        lines.append("  </url>")

        # Categorize for summary
        count_total += 1
        parts = Path(rel_path).parts
        lang_prefixes = {"es", "de", "fr", "pt", "ar"}
        is_translated = len(parts) > 0 and parts[0] in lang_prefixes

        if rel_path == "index.html":
            count_by_type["homepage"] += 1
        elif is_translated:
            count_by_type["translated"] += 1
        elif len(parts) > 0 and parts[0] == "video":
            count_by_type["video"] += 1
        elif len(parts) > 0 and parts[0] == "calculators":
            count_by_type["calculator"] += 1
        elif len(parts) > 0 and parts[0] == "updates":
            count_by_type["update"] += 1
        elif priority == 0.8:
            count_by_type["article"] += 1
        else:
            count_by_type["other"] += 1

    lines.append("</urlset>")
    lines.append("")  # trailing newline

    xml_content = "\n".join(lines)

    # Write sitemap.xml
    sitemap_path = root / "sitemap.xml"
    sitemap_path.write_text(xml_content, encoding="utf-8")

    # Build summary
    summary_lines = [
        "",
        "=" * 60,
        "  SITEMAP GENERATION COMPLETE",
        "=" * 60,
        f"  Output: {sitemap_path}",
        f"  Total URLs: {count_total}",
        "",
        "  Breakdown:",
        f"    Homepage:          {count_by_type['homepage']}",
        f"    Articles:          {count_by_type['article']}",
        f"    Calculators:       {count_by_type['calculator']}",
        f"    Video pages:       {count_by_type['video']}",
        f"    Translated pages:  {count_by_type['translated']}",
        f"    Update pages:      {count_by_type['update']}",
        f"    Other pages:       {count_by_type['other']}",
        "",
        f"  Pages with hreflang alternates: {count_with_alternates}",
        "=" * 60,
        "",
    ]

    return "\n".join(summary_lines)


def ensure_robots_txt(root: Path):
    """Create robots.txt at the project root if it doesn't already exist."""
    robots_path = root / "robots.txt"
    if robots_path.exists():
        print(f"  robots.txt already exists at {robots_path} — skipping creation.")
        return

    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )
    robots_path.write_text(content, encoding="utf-8")
    print(f"  robots.txt created at {robots_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating sitemap for socialtradingvlog.com ...")
    print()

    summary = generate_sitemap(PROJECT_ROOT)
    print(summary)

    print("Checking robots.txt ...")
    ensure_robots_txt(PROJECT_ROOT)
    print()
    print("Done.")
