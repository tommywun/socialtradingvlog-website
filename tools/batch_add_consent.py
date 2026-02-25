#!/usr/bin/env python3
"""
Batch add GDPR consent + analytics to all HTML pages.

Adds to every page:
1. Consent Mode v2 defaults snippet (before GA tag)
2. consent.js + analytics.js script tags (before </body>)
3. Privacy + Manage cookies links in footer (standard template pages only)

Usage:
    python3 tools/batch_add_consent.py              # Apply changes
    python3 tools/batch_add_consent.py --dry-run     # Preview changes
"""

import os
import re
import pathlib
import argparse

PROJECT_DIR = pathlib.Path(__file__).parent.parent
SKIP_DIRS = {"node_modules", "venv", ".git", "backups", ".claude"}

# Consent defaults snippet — goes BEFORE the GA tag
CONSENT_SNIPPET = """<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{'analytics_storage':'denied','ad_storage':'denied','ad_personalization':'denied','wait_for_update':500});
var c;try{c=JSON.parse(localStorage.getItem('stv-consent'))}catch(e){}
if(c&&c.accepted){gtag('consent','update',{'analytics_storage':'granted'})}
</script>"""

# GA tag patterns to find the insertion point
GA_PATTERNS = [
    "<!-- Google tag (gtag.js) -->",
    "<!-- GA -->",
    '<script async src="https://www.googletagmanager.com/gtag/js?id=G-PBGDJ951LL">',
]

PRIVACY_LINK = '<li><a href="{prefix}privacy.html">Privacy Policy</a></li>'
COOKIES_LINK = '<li><a href="#" id="manage-cookies">Manage cookies</a></li>'


def find_html_files():
    files = []
    for root, dirs, filenames in os.walk(str(PROJECT_DIR)):
        rel_root = os.path.relpath(root, str(PROJECT_DIR))
        if any(skip in rel_root.split(os.sep) for skip in SKIP_DIRS):
            continue
        for f in filenames:
            if f.endswith(".html"):
                files.append(pathlib.Path(root) / f)
    return sorted(files)


def get_prefix(filepath):
    """Calculate the relative path prefix from a file to the project root."""
    rel = filepath.relative_to(PROJECT_DIR)
    depth = len(rel.parts) - 1  # subtract the filename
    if depth == 0:
        return ""
    return "../" * depth


def add_consent_defaults(content, filepath, dry_run):
    """Add consent snippet before the GA tag if not already present."""
    if "consent','default'" in content or "consent\",\"default\"" in content:
        return content, False  # Already has consent defaults

    # Find the GA tag insertion point
    for pattern in GA_PATTERNS:
        idx = content.find(pattern)
        if idx != -1:
            new_content = content[:idx] + CONSENT_SNIPPET + "\n" + content[idx:]
            if dry_run:
                rel = filepath.relative_to(PROJECT_DIR)
                print(f"  + consent defaults → {rel}")
            return new_content, True

    return content, False


def add_script_tags(content, filepath, prefix, dry_run):
    """Add consent.js and analytics.js before </body>."""
    consent_tag = f'<script src="{prefix}js/consent.js"></script>'
    analytics_tag = f'<script src="{prefix}js/analytics.js"></script>'

    if "js/consent.js" in content:
        return content, False  # Already has consent.js

    # Find </body> and insert before it
    body_idx = content.rfind("</body>")
    if body_idx == -1:
        return content, False

    insert = f"\n  {consent_tag}\n  {analytics_tag}\n"
    new_content = content[:body_idx] + insert + content[body_idx:]

    if dry_run:
        rel = filepath.relative_to(PROJECT_DIR)
        print(f"  + consent.js + analytics.js → {rel}")

    return new_content, True


def add_footer_links(content, filepath, prefix, dry_run):
    """Add privacy policy and manage cookies links to standard footer."""
    if "privacy.html" in content or "manage-cookies" in content:
        return content, False  # Already has these links

    # Look for the standard footer pattern: last </ul> before </footer>
    footer_idx = content.rfind("</footer>")
    if footer_idx == -1:
        return content, False  # No standard footer

    # Find the footer-bottom div to add before it
    # Look for the last </ul> in the footer section
    footer_section = content[:footer_idx]
    last_ul_idx = footer_section.rfind("</ul>")
    if last_ul_idx == -1:
        return content, False

    # Insert privacy and cookies links before the closing </ul>
    privacy = PRIVACY_LINK.format(prefix=prefix)
    insert = f"\n            {privacy}\n            {COOKIES_LINK}"
    new_content = content[:last_ul_idx] + insert + "\n          " + content[last_ul_idx:]

    if dry_run:
        rel = filepath.relative_to(PROJECT_DIR)
        print(f"  + footer links → {rel}")

    return new_content, True


def process_file(filepath, dry_run):
    """Process a single HTML file. Returns number of changes made."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return 0

    prefix = get_prefix(filepath)
    changes = 0

    content, changed = add_consent_defaults(content, filepath, dry_run)
    if changed:
        changes += 1

    content, changed = add_script_tags(content, filepath, prefix, dry_run)
    if changed:
        changes += 1

    content, changed = add_footer_links(content, filepath, prefix, dry_run)
    if changed:
        changes += 1

    if changes > 0 and not dry_run:
        filepath.write_text(content, encoding="utf-8")

    return changes


def main():
    parser = argparse.ArgumentParser(description="Batch add consent + analytics to all HTML pages")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    args = parser.parse_args()

    print("Batch Consent + Analytics Update")
    print("=" * 60)

    files = find_html_files()
    print(f"Found {len(files)} HTML files\n")

    total_changes = 0
    files_modified = 0

    for filepath in files:
        changes = process_file(filepath, args.dry_run)
        if changes > 0:
            total_changes += changes
            files_modified += 1

    print(f"\nSummary: {total_changes} changes across {files_modified} files")
    if args.dry_run:
        print("Dry run — no files were modified.")


if __name__ == "__main__":
    main()
