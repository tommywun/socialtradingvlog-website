#!/usr/bin/env python3
"""
Internal link checker for socialtradingvlog.com

Scans all HTML files in the site and verifies that every internal <a href>
points to a file that actually exists on disk. Reports dead links grouped
by source file.

Usage:
    python3 tools/check_internal_links.py              # full scan
    python3 tools/check_internal_links.py --fix        # remove <li> entries with dead links
    python3 tools/check_internal_links.py --sections   # only check sidebar/recommendation sections
"""

import os
import re
import sys
import argparse
import pathlib
from urllib.parse import urlparse, unquote

SITE_ROOT = pathlib.Path(__file__).parent.parent
SKIP_DIRS = {'.git', 'node_modules', '.claude', 'docs', 'tools', 'reports', 'data'}
SKIP_PREFIXES = ('http://', 'https://', 'mailto:', 'tel:', 'javascript:', '#', 'data:')


def find_html_files():
    """Find all HTML files in the site."""
    files = []
    for root, dirs, filenames in os.walk(SITE_ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in filenames:
            if f.endswith('.html'):
                files.append(pathlib.Path(root) / f)
    return sorted(files)


def extract_links(html_path, sections_only=False):
    """Extract internal links from an HTML file.

    Returns list of dicts: {href, line_num, context, in_section}
    where context is the surrounding HTML for display.
    """
    content = html_path.read_text(encoding='utf-8', errors='replace')
    links = []

    # Track if we're inside a recommendation section
    section_names = ['sidebar-nav', 'might also like', 'you might', 'related',
                     'more guides', 'weitere', 'más guías', 'plus de guides',
                     'mais guias', 'المزيد']

    lines = content.split('\n')
    in_section = False

    for i, line in enumerate(lines, 1):
        lower = line.lower()

        # Detect section boundaries
        for name in section_names:
            if name in lower:
                in_section = True
                break
        if '</section>' in lower or '</aside>' in lower:
            in_section = False

        # Find all href attributes
        for match in re.finditer(r'href=["\']([^"\']+)["\']', line):
            href = match.group(1)

            # Skip external, anchors, special protocols
            if any(href.startswith(p) for p in SKIP_PREFIXES):
                continue

            if sections_only and not in_section:
                continue

            links.append({
                'href': href,
                'line_num': i,
                'context': line.strip()[:120],
                'in_section': in_section,
            })

    return links


def resolve_link(html_path, href):
    """Resolve an internal link relative to the HTML file's location.

    Returns (resolved_path, exists).
    """
    # Strip query string and fragment
    clean = href.split('?')[0].split('#')[0]
    if not clean:
        return None, True  # anchor-only link

    clean = unquote(clean)

    # Resolve relative to the HTML file's directory
    base_dir = html_path.parent
    resolved = (base_dir / clean).resolve()

    # If it points to a directory, check for index.html
    if resolved.is_dir():
        index = resolved / 'index.html'
        return resolved, index.exists()

    return resolved, resolved.exists()


def scan_site(sections_only=False):
    """Scan all HTML files for dead internal links."""
    html_files = find_html_files()
    print(f"Scanning {len(html_files)} HTML files...\n")

    dead_links = []
    total_links = 0

    for html_path in html_files:
        links = extract_links(html_path, sections_only)
        total_links += len(links)

        for link in links:
            resolved, exists = resolve_link(html_path, link['href'])
            if resolved and not exists:
                rel_source = html_path.relative_to(SITE_ROOT)
                dead_links.append({
                    'source': str(rel_source),
                    'href': link['href'],
                    'line_num': link['line_num'],
                    'context': link['context'],
                    'in_section': link['in_section'],
                    'resolved': str(resolved),
                })

    return dead_links, total_links, len(html_files)


def print_report(dead_links, total_links, total_files):
    """Print a human-readable report."""
    print(f"{'=' * 60}")
    print(f"Internal Link Check Report")
    print(f"{'=' * 60}")
    print(f"Files scanned:  {total_files}")
    print(f"Links checked:  {total_links}")
    print(f"Dead links:     {len(dead_links)}")
    print(f"{'=' * 60}\n")

    if not dead_links:
        print("All internal links are valid!")
        return

    # Group by source file
    by_source = {}
    for dl in dead_links:
        src = dl['source']
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(dl)

    for source, links in sorted(by_source.items()):
        print(f"  {source}")
        for link in links:
            section_tag = " [recommendation]" if link['in_section'] else ""
            print(f"    Line {link['line_num']}: {link['href']}{section_tag}")
        print()


def fix_dead_links(dead_links):
    """Remove <li> entries that contain dead links from recommendation sections."""
    if not dead_links:
        print("No dead links to fix.")
        return

    # Only fix links in recommendation sections
    section_links = [dl for dl in dead_links if dl['in_section']]
    if not section_links:
        print("No dead links in recommendation sections to fix.")
        return

    # Group by source file
    by_source = {}
    for dl in section_links:
        src = dl['source']
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(dl)

    fixed_count = 0
    for source, links in by_source.items():
        filepath = SITE_ROOT / source
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Collect line numbers to remove (0-indexed)
        remove_lines = set()
        for link in links:
            line_idx = link['line_num'] - 1
            if 0 <= line_idx < len(lines):
                line = lines[line_idx].strip()
                # Only remove if it's a standalone <li> entry
                if line.startswith('<li>') and line.endswith('</li>'):
                    remove_lines.add(line_idx)

        if remove_lines:
            new_lines = [l for i, l in enumerate(lines) if i not in remove_lines]
            filepath.write_text('\n'.join(new_lines), encoding='utf-8')
            fixed_count += len(remove_lines)
            print(f"  Fixed {len(remove_lines)} entries in {source}")

    print(f"\nRemoved {fixed_count} dead-link entries total.")


def main():
    parser = argparse.ArgumentParser(description="Check internal links in the site")
    parser.add_argument('--fix', action='store_true',
                        help='Remove <li> entries with dead links from recommendation sections')
    parser.add_argument('--sections', action='store_true',
                        help='Only check sidebar/recommendation sections')
    args = parser.parse_args()

    dead_links, total_links, total_files = scan_site(sections_only=args.sections)
    print_report(dead_links, total_links, total_files)

    if args.fix:
        fix_dead_links(dead_links)


if __name__ == '__main__':
    main()
