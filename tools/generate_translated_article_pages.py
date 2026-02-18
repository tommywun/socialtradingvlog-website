#!/usr/bin/env python3
"""
Generate translated SEO-optimised article landing pages.

Creates /{lang}/SLUG/index.html for each language with:
  - Full translated article content
  - Localised SEO (keyphrase, meta description, h1, FAQs)
  - Hreflang tags linking all language variants
  - Same template structure as English article pages
  - Correct asset paths (2 levels deep)

Usage:
    python3 tools/generate_translated_article_pages.py              # generate all
    python3 tools/generate_translated_article_pages.py --lang es     # Spanish only
    python3 tools/generate_translated_article_pages.py --force       # regenerate
"""

import sys
import os
import re
import html
import json
import pathlib
import argparse

BASE_DIR = pathlib.Path(__file__).parent.parent

# ── Asset prefix for translated article pages (2 levels deep: /es/slug/) ─────
ASSET_PREFIX = "../../"

# ── Base URL ──────────────────────────────────────────────────────────────────
BASE_URL = "https://socialtradingvlog.com"

# ── Translations directory ───────────────────────────────────────────────────
TRANSLATIONS_DIR = pathlib.Path(__file__).parent / "translations"

# ── Import UI_STRINGS from the video page generator ──────────────────────────
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate_translated_pages import UI_STRINGS

# ── Article definitions ──────────────────────────────────────────────────────
# Each article: id → { en_slug, cta_url, translation_prefix }
ARTICLES = {
    "etoro-review": {
        "en_slug": "etoro-review",
        "cta_url": "https://etoro.tw/4cuYCBg",
        "translation_prefix": "etoro-review",  # JSON files: etoro-review_es.json etc.
    },
}

# ── Sidebar "More guides" links (same across all article pages) ──────────────
SIDEBAR_GUIDES = [
    {"href": "etoro-review/", "key": "guide_etoro_review", "fallback": "eToro Review 2026"},
    {"href": "social-trading.html", "key": "guide_social"},
    {"href": "copy-trading.html", "key": "guide_copy"},
    {"href": "etoro-scam.html", "key": "guide_scam"},
    {"href": "copy-trading-returns.html", "key": "guide_returns"},
    {"href": "videos.html", "key": "guide_all_videos"},
]


def load_translation(article_id, lang):
    """Load a translation JSON file for an article+language."""
    article = ARTICLES[article_id]
    json_file = TRANSLATIONS_DIR / f"{article['translation_prefix']}_{lang}.json"
    if not json_file.exists():
        return None
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_available_languages(article_id):
    """Find all available translation languages for an article."""
    article = ARTICLES[article_id]
    prefix = article["translation_prefix"]
    langs = []
    if TRANSLATIONS_DIR.exists():
        for json_file in TRANSLATIONS_DIR.glob(f"{prefix}_*.json"):
            lang = json_file.stem.split("_")[-1]
            langs.append(lang)
    return sorted(langs)


def build_hreflang_tags(article_id, available_langs, translations_cache):
    """Build hreflang link tags for all language variants."""
    article = ARTICLES[article_id]
    en_slug = article["en_slug"]
    lines = []
    # English (default + en)
    en_url = f"{BASE_URL}/{en_slug}/"
    lines.append(f'  <link rel="alternate" hreflang="en" href="{en_url}" />')
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{en_url}" />')
    # Each translation
    for lang in available_langs:
        trans = translations_cache[lang]
        url = f"{BASE_URL}/{lang}/{trans['slug']}/"
        lines.append(f'  <link rel="alternate" hreflang="{lang}" href="{url}" />')
    return "\n".join(lines)


def build_toc(sections, ui):
    """Build table of contents from sections."""
    items = []
    for sec in sections:
        sid = sec.get("id", slugify(sec["h2"]))
        items.append(f'<li><a href="#{sid}">{html.escape(sec["h2"])}</a></li>')
    return "\n".join(items)


def slugify(text):
    """Convert heading text to URL-safe anchor id."""
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def render_article_body(sections):
    """Render all sections as HTML."""
    parts = []
    for sec in sections:
        sid = sec.get("id", slugify(sec["h2"]))
        parts.append(f'        <h2 id="{sid}">{html.escape(sec["h2"])}</h2>')
        for p in sec["paragraphs"]:
            if isinstance(p, dict):
                if p["type"] == "note":
                    parts.append(f'        <p class="toms-note">{html.escape(p["text"])}</p>')
                elif p["type"] == "h3":
                    parts.append(f'        <h3>{html.escape(p["text"])}</h3>')
            else:
                parts.append(f'        <p>{html.escape(p)}</p>')
    return "\n".join(parts)


def render_faq_html(faqs):
    """Render FAQ items HTML (without wrapping section tag)."""
    parts = []
    for faq in faqs:
        parts.append('    <div class="faq-item">')
        parts.append(f'      <h3 class="faq-q">{html.escape(faq["q"])}</h3>')
        parts.append(f'      <p class="faq-a">{html.escape(faq["a"])}</p>')
        parts.append('    </div>')
    return "\n".join(parts)


def render_faq_schema(faqs):
    """Render FAQPage JSON-LD schema."""
    entities = []
    for faq in faqs:
        entities.append({
            "@type": "Question",
            "name": faq["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["a"],
            }
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }
    return json.dumps(schema, indent=2, ensure_ascii=False)


def generate_article_page(lang, article_id, trans, hreflang_tags):
    """Generate a full translated article HTML page."""
    ui = UI_STRINGS[lang]
    article = ARTICLES[article_id]
    slug = trans["slug"]
    h1 = trans["h1"]
    desc = trans["description"]
    intro = trans["intro"]
    tag = trans.get("tag", "")
    sections = trans["sections"]
    faqs = trans["faqs"]
    cta_url = article["cta_url"]

    canonical = f"{BASE_URL}/{lang}/{slug}/"
    toc_items = build_toc(sections, ui)
    article_body = render_article_body(sections)
    faq_items_html = render_faq_html(faqs)
    faq_schema = render_faq_schema(faqs)
    faq_heading = ui.get("faq_heading", "FAQ")

    # Article schema (not VideoObject)
    article_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "description": desc,
        "author": {
            "@type": "Person",
            "name": "Tom",
            "url": f"{BASE_URL}/about.html"
        },
        "publisher": {
            "@type": "Organization",
            "name": "Social Trading Vlog",
            "url": BASE_URL
        },
        "url": canonical
    }, indent=2, ensure_ascii=False)

    # Breadcrumb schema (2 levels for article pages)
    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": ui.get("breadcrumb_home", "Home"), "item": BASE_URL},
            {"@type": "ListItem", "position": 2, "name": h1, "item": canonical},
        ]
    }, indent=2, ensure_ascii=False)

    p = ASSET_PREFIX  # ../../
    dir_attr = ' dir="rtl"' if lang == "ar" else ""

    # Build sidebar guides
    sidebar_items = []
    for guide in SIDEBAR_GUIDES:
        label_key = guide["key"]
        label = ui.get(label_key, guide.get("fallback", label_key))
        sidebar_items.append(f'            <li><a href="{p}{guide["href"]}">{html.escape(label)}</a></li>')
    sidebar_html = "\n".join(sidebar_items)

    page_html = f'''<!DOCTYPE html>
<html lang="{lang}"{dir_attr}>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{html.escape(desc)}" />
  <meta property="og:title" content="{html.escape(h1)} | SocialTradingVlog" />
  <meta property="og:description" content="{html.escape(desc)}" />
  <meta property="og:type" content="article" />
  <link rel="canonical" href="{canonical}" />
{hreflang_tags}
  <title>{html.escape(h1)} | SocialTradingVlog</title>
  <link rel="stylesheet" href="{p}css/style.css" />
  <script type="application/ld+json">
    {article_schema}
  </script>
  <script type="application/ld+json">
    {faq_schema}
  </script>
  <script type="application/ld+json">
    {breadcrumb_schema}
  </script>
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
      <p class="article-meta">{ui["by_tom"]} &nbsp;&middot;&nbsp; Social Trading Vlog</p>
    </div>
  </div>

  <div class="container">
    <div class="article-body">

      <article class="article-content">

        <p class="article-intro">{html.escape(intro)}</p>

        <nav class="toc" aria-label="Contents"><h4>{html.escape(ui.get("in_this_article", "In this article"))}</h4><ul>
{toc_items}
</ul></nav>

        <div class="risk-warning">
          <strong>{html.escape(ui["risk_warning_label"])}</strong>
          {html.escape(ui["risk_warning_full"])}
        </div>

        <div class="inline-cta">
          <p class="inline-cta-text">{html.escape(ui["ready_cta_inline"])}</p>
          <a href="{cta_url}" class="btn btn-primary" target="_blank" rel="noopener sponsored">{html.escape(ui["explore_etoro"])}</a>
        </div>

{article_body}

        <section class="faq-section">
  <h2>{html.escape(faq_heading)}</h2>
{faq_items_html}
</section>

        <div class="risk-warning">
          <strong>{html.escape(ui["important_reminder"])}</strong>
          {html.escape(ui["important_reminder_text"])}
        </div>

      </article>

      <aside class="article-sidebar">
        <div class="sidebar-cta" id="etoro-cta">
          <h3>{html.escape(ui["ready_to_try"])}</h3>
          <p>{html.escape(ui["toms_affiliate"])}</p>
          <a href="{cta_url}" class="btn btn-primary" target="_blank" rel="noopener sponsored">{html.escape(ui["explore_etoro"])}</a>
          <div class="risk-warning">
            <strong>{ui["risk_warning_sidebar"].split(".")[0]}.</strong>
            {".".join(ui["risk_warning_sidebar"].split(".")[1:])}
          </div>
        </div>
        <div class="sidebar-nav">
          <h4>{html.escape(ui["more_guides"])}</h4>
          <ul>
{sidebar_html}
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
    parser = argparse.ArgumentParser(description="Generate translated article pages")
    parser.add_argument("--lang", help="Generate only this language (es, de, fr, pt, ar)")
    parser.add_argument("--article", help="Generate only for this article ID")
    parser.add_argument("--force", action="store_true", help="Overwrite existing pages")
    args = parser.parse_args()

    count = 0
    for article_id, article in ARTICLES.items():
        if args.article and article_id != args.article:
            continue

        available_langs = get_available_languages(article_id)
        if not available_langs:
            print(f"  No translations found for {article_id}")
            continue

        # Pre-load all translations for hreflang building
        translations_cache = {}
        for lang in available_langs:
            trans = load_translation(article_id, lang)
            if trans:
                translations_cache[lang] = trans

        # Build hreflang tags (shared across all languages for this article)
        hreflang_tags = build_hreflang_tags(article_id, available_langs, translations_cache)

        for lang in available_langs:
            if args.lang and lang != args.lang:
                continue

            trans = translations_cache[lang]
            slug = trans["slug"]
            out_dir = BASE_DIR / lang / slug
            out_file = out_dir / "index.html"

            if out_file.exists() and not args.force:
                print(f"  SKIP {lang}/{slug}/ (exists)")
                continue

            out_dir.mkdir(parents=True, exist_ok=True)
            page_html = generate_article_page(lang, article_id, trans, hreflang_tags)
            out_file.write_text(page_html, encoding="utf-8")
            count += 1
            print(f"  WROTE {lang}/{slug}/index.html")

    print(f"\nDone — {count} translated article page(s) generated.")


if __name__ == "__main__":
    main()
