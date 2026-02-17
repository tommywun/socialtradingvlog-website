#!/usr/bin/env python3
"""
Add Google Analytics tag and CTA click event tracking to all HTML pages.
Run once — safe to re-run (skips pages that already have the tag).
"""

import pathlib
import re

BASE_DIR = pathlib.Path(__file__).parent.parent

GA_TAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-PBGDJ951LL"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-PBGDJ951LL');
</script>"""

# Click tracking script — fires GA event when any CTA button is clicked
CLICK_TRACKING = """<script>
document.addEventListener('click', function(e) {
  var link = e.target.closest('a.btn-primary');
  if (!link) return;
  var page = location.pathname;
  var label = link.textContent.trim();
  var dest = link.href || '';
  if (typeof gtag === 'function') {
    gtag('event', 'cta_click', {
      'event_category': 'affiliate',
      'event_label': label,
      'link_url': dest,
      'page_path': page
    });
  }
});
</script>"""


def process_file(path):
    text = path.read_text(encoding="utf-8")

    # Skip if already has GA tag
    if "G-PBGDJ951LL" in text:
        return False

    modified = False

    # Add GA tag right after <head> or after first <meta charset>
    if "</head>" in text:
        # Insert GA tag just before </head>
        text = text.replace("</head>", f"{GA_TAG}\n</head>", 1)
        modified = True

    # Add click tracking before </body>
    if "</body>" in text and CLICK_TRACKING not in text:
        text = text.replace("</body>", f"{CLICK_TRACKING}\n</body>", 1)
        modified = True

    if modified:
        path.write_text(text, encoding="utf-8")
    return modified


def main():
    # Find all HTML files
    html_files = list(BASE_DIR.glob("*.html"))
    html_files += list(BASE_DIR.glob("articles/*.html"))
    html_files += list(BASE_DIR.glob("updates/*.html"))
    # Skip generated pages (video/* and article slug dirs) — those are handled by generators

    updated = 0
    skipped = 0
    for f in sorted(html_files):
        if process_file(f):
            print(f"  + {f.relative_to(BASE_DIR)}")
            updated += 1
        else:
            skipped += 1

    print(f"\nDone: {updated} updated, {skipped} already had GA tag")


if __name__ == "__main__":
    main()
