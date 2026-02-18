#!/usr/bin/env python3
"""
Generate translated SEO-optimised legacy pages (backbone pages).

Creates /{lang}/SLUG/index.html for each legacy page and language with:
  - Full translated content matching English page structure
  - Localised SEO (meta description, h1, headings)
  - Hreflang tags linking all language variants
  - Images and video embeds preserved from English pages
  - Correct asset paths (2 levels deep)

Usage:
    python3 tools/generate_translated_legacy_pages.py              # generate all
    python3 tools/generate_translated_legacy_pages.py --lang es     # Spanish only
    python3 tools/generate_translated_legacy_pages.py --page social-trading  # one page
    python3 tools/generate_translated_legacy_pages.py --force       # regenerate
"""

import sys
import os
import re
import html
import json
import pathlib
import argparse

BASE_DIR = pathlib.Path(__file__).parent.parent

# ── Asset prefix for translated pages (2 levels deep: /es/slug/) ─────────────
ASSET_PREFIX = "../../"

# ── Base URL ──────────────────────────────────────────────────────────────────
BASE_URL = "https://socialtradingvlog.com"

# ── Translations directory ───────────────────────────────────────────────────
TRANSLATIONS_DIR = pathlib.Path(__file__).parent / "translations"

# ── Import UI_STRINGS from the video page generator ──────────────────────────
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate_translated_pages import UI_STRINGS

# ── Legacy page definitions ──────────────────────────────────────────────────
# Maps page_id → English filename (for hreflang)
LEGACY_PAGES = {
    "social-trading": {"en_file": "social-trading.html"},
    "copy-trading": {"en_file": "copy-trading.html"},
    "about": {"en_file": "about.html"},
    "copy-trading-returns": {"en_file": "copy-trading-returns.html"},
    "taking-profits": {"en_file": "taking-profits.html"},
}

# ── CTA URL ──────────────────────────────────────────────────────────────────
CTA_URL = "https://etoro.tw/4tEsDF4"


def load_backbone_translations(lang):
    """Load backbone pages translations for a language."""
    json_file = TRANSLATIONS_DIR / f"backbone_pages_{lang}.json"
    if not json_file.exists():
        return None
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_available_languages():
    """Find all languages with backbone translations."""
    langs = []
    if TRANSLATIONS_DIR.exists():
        for json_file in TRANSLATIONS_DIR.glob("backbone_pages_*.json"):
            lang = json_file.stem.replace("backbone_pages_", "")
            langs.append(lang)
    return sorted(langs)


def build_hreflang_tags(page_id, available_langs, all_translations):
    """Build hreflang link tags for all language variants of a page."""
    en_file = LEGACY_PAGES[page_id]["en_file"]
    lines = []
    en_url = f"{BASE_URL}/{en_file}"
    lines.append(f'  <link rel="alternate" hreflang="en" href="{en_url}" />')
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{en_url}" />')
    for lang in available_langs:
        trans = all_translations[lang]
        if page_id in trans:
            slug = trans[page_id]["slug"]
            url = f"{BASE_URL}/{lang}/{slug}/"
            lines.append(f'  <link rel="alternate" hreflang="{lang}" href="{url}" />')
    return "\n".join(lines)


def render_content_block(block, p):
    """Render a single content block to HTML. p is asset prefix."""
    t = block["type"]

    if t == "p":
        return f'        <p>{html.escape(block["text"])}</p>'

    elif t == "h2":
        return f'        <h2>{html.escape(block["text"])}</h2>'

    elif t == "h3":
        return f'        <h3>{html.escape(block["text"])}</h3>'

    elif t == "img":
        src = block["src"]
        alt = html.escape(block.get("alt", ""))
        cls = block.get("class", "")
        class_attr = f' class="{cls}"' if cls else ""
        return f'        <img src="{p}{src}" alt="{alt}" style="max-width:100%;height:auto;border-radius:8px;margin:24px 0;display:block;" loading="lazy"{class_attr}>'

    elif t == "img_about":
        src = block["src"]
        alt = html.escape(block.get("alt", ""))
        cls = block.get("class", "about-portrait lb-trigger")
        return f'        <img src="{p}{src}" alt="{alt}" class="{cls}" loading="lazy">'

    elif t == "img_grid":
        cols = block.get("cols", 3)
        images = block.get("images", [])
        parts = [f'        <div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:12px;margin:24px 0;">']
        for img in images:
            alt = html.escape(img.get("alt", ""))
            parts.append(f'          <img src="{p}{img["src"]}" alt="{alt}" style="width:100%;height:auto;border-radius:8px;object-fit:cover;" loading="lazy">')
        parts.append('        </div>')
        return "\n".join(parts)

    elif t == "img_row":
        images = block.get("images", [])
        parts = ['        <div class="about-img-row">']
        for img in images:
            alt = html.escape(img.get("alt", ""))
            href = img.get("href", "#")
            parts.append(f'          <a href="{p}{href}"><img src="{p}{img["src"]}" alt="{alt}" loading="lazy"></a>')
        parts.append('        </div>')
        return "\n".join(parts)

    elif t == "video_embed":
        src = block["src"]
        title = html.escape(block.get("title", ""))
        return f'''        <div class="video-embed">
          <iframe src="{src}" title="{title}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
        </div>'''

    elif t == "risk_warning":
        title = html.escape(block.get("title", "Risk Warning"))
        text = html.escape(block.get("text", ""))
        return f'''        <div class="risk-warning">
          <strong>{title}</strong>
          {text}
        </div>'''

    elif t == "ul":
        items = block.get("items", [])
        parts = ['        <ul>']
        for item in items:
            parts.append(f'          <li>{html.escape(item)}</li>')
        parts.append('        </ul>')
        return "\n".join(parts)

    elif t == "p_html":
        # HTML content with links — pass through as-is (already contains <a> tags)
        return f'        <p>{block["html"]}</p>'

    elif t == "btn_outline":
        text = html.escape(block.get("text", ""))
        href = block.get("href", "#")
        return f'        <a href="{href}" class="btn btn-outline" target="_blank" rel="noopener sponsored">{text}</a>'

    elif t == "clear":
        return '        <div style="clear:both;"></div>'

    else:
        return f'        <!-- unknown block type: {t} -->'


def generate_legacy_page(lang, page_id, page_data, hreflang_tags):
    """Generate a full translated legacy page."""
    ui = UI_STRINGS[lang]
    slug = page_data["slug"]
    h1 = page_data["h1"]
    desc = page_data["description"]
    tag = page_data.get("tag", "")
    title = page_data.get("title", f"{h1} | SocialTradingVlog")
    og_title = page_data.get("og_title", title)
    og_desc = page_data.get("og_description", desc)
    og_type = page_data.get("og_type", "article")
    content_blocks = page_data.get("content", [])
    sidebar_cta = page_data.get("sidebar_cta", {})
    sidebar_nav_heading = page_data.get("sidebar_nav_heading", ui.get("more_guides", "More guides"))

    canonical = f"{BASE_URL}/{lang}/{slug}/"
    p = ASSET_PREFIX

    # Render content blocks
    content_html = "\n\n".join(render_content_block(block, p) for block in content_blocks)

    # Article schema
    article_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "author": {"@type": "Person", "name": "Tom"},
        "publisher": {"@type": "Organization", "name": "Social Trading Vlog"},
        "description": desc
    }, indent=4, ensure_ascii=False)

    dir_attr = ' dir="rtl"' if lang == "ar" else ""

    # Build sidebar guides (same as English pages)
    sidebar_guides = [
        (f"{p}social-trading.html", ui.get("guide_social", "What is Social Trading?")),
        (f"{p}copy-trading.html", ui.get("guide_copy", "What is Copy Trading?")),
        (f"{p}etoro-scam.html", ui.get("guide_scam", "Is eToro a Scam?")),
        (f"{p}copy-trading-returns.html", ui.get("guide_returns", "How Much Can You Make?")),
        (f"{p}taking-profits.html", ui.get("guide_profits", "Taking Profits")),
        (f"{p}etoro-review/", "eToro Review 2026"),
        (f"{p}videos.html", ui.get("guide_all_videos", "All Videos")),
    ]
    sidebar_items = "\n".join(
        f'            <li><a href="{href}">{html.escape(label)}</a></li>'
        for href, label in sidebar_guides
    )

    # Meta article-meta line
    if page_id == "about":
        meta_line = f'<p class="article-meta">Social Trading Vlog</p>'
    else:
        meta_line = f'<p class="article-meta">{ui.get("by_tom", "By Tom")} &nbsp;&middot;&nbsp; Social Trading Vlog</p>'

    # Schema block — skip for about page (og:type website)
    schema_block = ""
    if og_type == "article":
        schema_block = f'''  <script type="application/ld+json">
  {article_schema}
  </script>'''

    page_html = f'''<!DOCTYPE html>
<html lang="{lang}"{dir_attr}>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{html.escape(desc)}" />
  <meta property="og:title" content="{html.escape(og_title)}" />
  <meta property="og:description" content="{html.escape(og_desc)}" />
  <meta property="og:type" content="{og_type}" />
  <link rel="canonical" href="{canonical}" />
{hreflang_tags}
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{p}css/style.css" />
{schema_block}
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-PBGDJ951LL"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-PBGDJ951LL');
  </script>
</head>
<body>

  <nav>
    <div class="container nav-inner">
      <a href="{p}index.html" class="nav-logo">Social<span>Trading</span>Vlog</a>
      <ul class="nav-links">
        <li><a href="{p}social-trading.html">{html.escape(ui["social_trading"])}</a></li>
        <li><a href="{p}copy-trading.html">{html.escape(ui["copy_trading"])}</a></li>
        <li><a href="{p}updates.html">{html.escape(ui["updates"])}</a></li>
        <li><a href="{p}videos.html">{html.escape(ui["videos"])}</a></li>
        <li><a href="{p}about.html">{html.escape(ui["about"])}</a></li>
        <li><a href="{p}faq.html">{html.escape(ui["faq"])}</a></li>
        <li><a href="#etoro-cta" class="nav-cta">{html.escape(ui["try_etoro"])}</a></li>
      </ul>
      <button class="nav-hamburger" id="nav-hamburger" aria-label="Open navigation" aria-expanded="false" aria-controls="nav-drawer">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
  <div class="nav-drawer" id="nav-drawer" role="navigation" aria-label="Mobile navigation">
    <ul>
      <li><a href="{p}social-trading.html">{html.escape(ui["social_trading"])}</a></li>
      <li><a href="{p}copy-trading.html">{html.escape(ui["copy_trading"])}</a></li>
      <li><a href="{p}updates.html">{html.escape(ui["updates"])}</a></li>
      <li><a href="{p}videos.html">{html.escape(ui["videos"])}</a></li>
      <li><a href="{p}about.html">{html.escape(ui["about"])}</a></li>
      <li><a href="{p}faq.html">{html.escape(ui["faq"])}</a></li>
      <li><a href="#etoro-cta" class="nav-cta">{html.escape(ui["try_etoro"])}</a></li>
    </ul>
  </div>

  <div class="risk-warning-banner">
    <span>{html.escape(ui["risk_warning_label"])}:</span> {ui["risk_warning_banner"].split(": ", 1)[-1] if ": " in ui["risk_warning_banner"] else ui["risk_warning_banner"]}
  </div>

  <div class="article-hero">
    <div class="container">
      <div class="article-tag">{html.escape(tag)}</div>
      <h1>{html.escape(h1)}</h1>
      {meta_line}
    </div>
  </div>

  <div class="container">
    <div class="article-body">

      <article class="article-content">

{content_html}

      </article>

      <aside class="article-sidebar">
        <div class="sidebar-cta" id="etoro-cta">
          <h3>{html.escape(sidebar_cta.get("h3", ui["ready_to_try"]))}</h3>
          <p>{html.escape(sidebar_cta.get("p", ui["toms_affiliate"]))}</p>
          <a href="{CTA_URL}" class="btn btn-primary" target="_blank" rel="noopener sponsored">{html.escape(sidebar_cta.get("btn", ui["explore_etoro"]))}</a>
          <div class="risk-warning">
            <strong>{ui["risk_warning_sidebar"].split(".")[0]}.</strong>
            {".".join(ui["risk_warning_sidebar"].split(".")[1:])}
          </div>
        </div>
        <div class="sidebar-nav">
          <h4>{html.escape(sidebar_nav_heading)}</h4>
          <ul>
{sidebar_items}
          </ul>
        </div>
      </aside>

    </div>
  </div>

  <footer>
    <div class="container">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="nav-logo">Social<span style="color:var(--accent)">Trading</span>Vlog</div>
          <p>{html.escape(ui["footer_brand"])}</p>
        </div>
        <div class="footer-col">
          <h4>{html.escape(ui["footer_guides"])}</h4>
          <ul>
            <li><a href="{p}social-trading.html">{html.escape(ui["guide_social"])}</a></li>
            <li><a href="{p}copy-trading.html">{html.escape(ui["guide_copy"])}</a></li>
            <li><a href="{p}etoro-scam.html">{html.escape(ui["guide_scam"])}</a></li>
            <li><a href="{p}copy-trading-returns.html">{html.escape(ui["guide_returns"])}</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>{html.escape(ui["footer_site"])}</h4>
          <ul>
            <li><a href="{p}updates.html">{html.escape(ui["footer_updates"])}</a></li>
            <li><a href="{p}about.html">{html.escape(ui["footer_about"])}</a></li>
            <li><a href="{p}faq.html">{html.escape(ui["footer_faq"])}</a></li>
            <li><a href="{p}contact.html">{html.escape(ui["footer_contact"])}</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 SocialTradingVlog.com</p>
        <p class="footer-disclaimer">{html.escape(ui["risk_warning_footer"])}</p>
      </div>
    </div>
  </footer>

  <script src="{p}js/lightbox.js"></script>
  <script src="{p}js/nav.js"></script>
  <script>
  document.addEventListener('click', function(e) {{
    var link = e.target.closest('a.btn-primary');
    if (!link) return;
    if (typeof gtag === 'function') {{
      gtag('event', 'cta_click', {{
        'event_category': 'affiliate',
        'event_label': link.textContent.trim(),
        'link_url': link.href || '',
        'page_path': location.pathname
      }});
    }}
  }});
  </script>
</body>
</html>'''

    return page_html


def main():
    parser = argparse.ArgumentParser(description="Generate translated legacy pages")
    parser.add_argument("--lang", help="Generate only this language (es, de, fr, pt, ar)")
    parser.add_argument("--page", help="Generate only this page (e.g. social-trading)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing pages")
    args = parser.parse_args()

    available_langs = get_available_languages()
    if not available_langs:
        print("No backbone translation files found.")
        return

    # Load all translations for hreflang building
    all_translations = {}
    for lang in available_langs:
        data = load_backbone_translations(lang)
        if data:
            all_translations[lang] = data

    count = 0
    for page_id in LEGACY_PAGES:
        if args.page and page_id != args.page:
            continue

        # Build hreflang tags for this page
        hreflang_tags = build_hreflang_tags(page_id, available_langs, all_translations)

        for lang in available_langs:
            if args.lang and lang != args.lang:
                continue

            if page_id not in all_translations.get(lang, {}):
                print(f"  SKIP {lang}/{page_id} (no translation)")
                continue

            page_data = all_translations[lang][page_id]
            slug = page_data["slug"]
            out_dir = BASE_DIR / lang / slug
            out_file = out_dir / "index.html"

            if out_file.exists() and not args.force:
                print(f"  SKIP {lang}/{slug}/ (exists)")
                continue

            out_dir.mkdir(parents=True, exist_ok=True)
            page_html = generate_legacy_page(lang, page_id, page_data, hreflang_tags)
            out_file.write_text(page_html, encoding="utf-8")
            count += 1
            print(f"  WROTE {lang}/{slug}/index.html")

    print(f"\nDone — {count} translated legacy page(s) generated.")


if __name__ == "__main__":
    main()
