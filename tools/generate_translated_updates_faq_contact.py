#!/usr/bin/env python3
"""
Generate translated update posts, FAQ and contact pages.

Creates:
  - /{lang}/updates/{slug}/index.html for each update post (3 levels deep)
  - /{lang}/{slug}/index.html for FAQ and contact pages (2 levels deep)

Usage:
    python3 tools/generate_translated_updates_faq_contact.py              # all
    python3 tools/generate_translated_updates_faq_contact.py --lang es    # Spanish only
    python3 tools/generate_translated_updates_faq_contact.py --type faq   # FAQ only
    python3 tools/generate_translated_updates_faq_contact.py --force      # overwrite
"""

import sys
import os
import html
import json
import pathlib
import argparse

BASE_DIR = pathlib.Path(__file__).parent.parent
BASE_URL = "https://socialtradingvlog.com"
TRANSLATIONS_DIR = pathlib.Path(__file__).parent / "translations"
CTA_URL = "https://etoro.tw/4tEsDF4"

# Import UI_STRINGS from the video page generator
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate_translated_pages import UI_STRINGS

# Load the English update posts content for reference (video embeds, images, sidebar links)
ENGLISH_CONTENT_FILE = TRANSLATIONS_DIR / "update_posts_content.json"


def load_translations(lang):
    """Load the combined translation file for a language."""
    json_file = TRANSLATIONS_DIR / f"updates_faq_contact_{lang}.json"
    if not json_file.exists():
        return None
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_english_content():
    """Load the extracted English update post content."""
    if not ENGLISH_CONTENT_FILE.exists():
        return {}
    with open(ENGLISH_CONTENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_available_languages():
    """Find all languages with translations."""
    langs = []
    if TRANSLATIONS_DIR.exists():
        for json_file in TRANSLATIONS_DIR.glob("updates_faq_contact_*.json"):
            lang = json_file.stem.replace("updates_faq_contact_", "")
            langs.append(lang)
    return sorted(langs)


def render_content_block(block, asset_prefix):
    """Render a content block to HTML."""
    t = block["type"]
    p = asset_prefix

    if t == "p":
        return f'        <p>{block["text"]}</p>'

    elif t == "h2":
        return f'        <h2>{html.escape(block["text"])}</h2>'

    elif t == "h3":
        return f'        <h3>{html.escape(block["text"])}</h3>'

    elif t == "img":
        src = block["src"]
        alt = html.escape(block.get("alt", ""))
        return f'        <img src="{p}{src}" alt="{alt}" style="max-width:100%;height:auto;border-radius:8px;margin:24px 0;display:block;" loading="lazy">'

    elif t == "img_grid":
        cols = block.get("cols", 2)
        images = block.get("images", [])
        parts = [f'        <div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:12px;margin:24px 0;">']
        for img in images:
            alt = html.escape(img.get("alt", ""))
            parts.append(f'          <img src="{p}{img["src"]}" alt="{alt}" style="width:100%;height:auto;border-radius:8px;object-fit:cover;" loading="lazy">')
        parts.append('        </div>')
        return "\n".join(parts)

    elif t == "risk_warning":
        title = html.escape(block.get("title", "Reminder"))
        text = block.get("text", "Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice.")
        return f'''        <div class="risk-warning">
          <strong>{title}</strong>
          {text}
        </div>'''

    else:
        return f'        <!-- unknown block type: {t} -->'


def build_update_hreflang(page_id, available_langs, all_translations, english_content):
    """Build hreflang tags for an update post."""
    en_filename = english_content.get(page_id, {}).get("filename", f"{page_id}.html")
    en_url = f"{BASE_URL}/updates/{en_filename}"
    lines = []
    lines.append(f'  <link rel="alternate" hreflang="en" href="{en_url}" />')
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{en_url}" />')
    for lang in available_langs:
        trans = all_translations.get(lang, {})
        updates = trans.get("updates", {})
        if page_id in updates:
            slug = updates[page_id]["slug"]
            url = f"{BASE_URL}/{lang}/updates/{slug}/"
            lines.append(f'  <link rel="alternate" hreflang="{lang}" href="{url}" />')
    return "\n".join(lines)


def build_page_hreflang(page_type, available_langs, all_translations, en_filename):
    """Build hreflang tags for FAQ or contact page."""
    en_url = f"{BASE_URL}/{en_filename}"
    lines = []
    lines.append(f'  <link rel="alternate" hreflang="en" href="{en_url}" />')
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{en_url}" />')
    for lang in available_langs:
        trans = all_translations.get(lang, {})
        page = trans.get(page_type, {})
        if "slug" in page:
            slug = page["slug"]
            url = f"{BASE_URL}/{lang}/{slug}/"
            lines.append(f'  <link rel="alternate" hreflang="{lang}" href="{url}" />')
    return "\n".join(lines)


def generate_update_page(lang, page_id, update_data, english_post, hreflang_tags):
    """Generate a translated update post page."""
    ui = UI_STRINGS[lang]
    p = "../../../"  # 3 levels deep: /{lang}/updates/{slug}/

    slug = update_data["slug"]
    h1_text = update_data.get("h1", "")
    desc = update_data.get("meta_description", "")
    title = update_data.get("title", f"{h1_text} | SocialTradingVlog")
    tag = update_data.get("article_tag", "")

    # Video embed from English content
    video_src = english_post.get("video_embed_src", "")
    video_title = english_post.get("video_embed_title", "")

    # Sidebar links from English (prev/next navigation)
    sidebar_links = english_post.get("sidebar_links", [])

    dir_attr = ' dir="rtl"' if lang == "ar" else ""

    # Render content blocks
    blocks = update_data.get("content_blocks", [])
    content_html = "\n\n".join(render_content_block(b, p) for b in blocks)

    # Sidebar prev/next links
    sidebar_items = ""
    for link in sidebar_links:
        sidebar_items += f'            <li><a href="{html.escape(link["href"])}">{html.escape(link["text"])}</a></li>\n'

    # Build back link
    back_text = ui.get("back_to_updates", "All updates")

    return f'''<!DOCTYPE html>
<html lang="{lang}"{dir_attr}>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{html.escape(desc)}" />
  <link rel="canonical" href="{BASE_URL}/{lang}/updates/{slug}/" />
{hreflang_tags}
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{p}css/style.css" />
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
      <h1>{html.escape(h1_text)}</h1>
      <p class="article-meta">{ui.get("by_tom", "By Tom")} &nbsp;&middot;&nbsp; Social Trading Vlog</p>
    </div>
  </div>

  <div class="container">
    <div class="article-body">
      <article class="article-content">

        <div class="risk-warning">
          <strong>{html.escape(ui["risk_warning_label"])}</strong>
          {ui["risk_warning_full"]}
        </div>
        <div class="video-embed">
          <iframe src="{video_src}" title="{html.escape(video_title)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
        </div>

{content_html}

        <p><a href="{p}updates.html">&larr; {html.escape(back_text)}</a></p>

      </article>

      <aside class="article-sidebar">
        <div class="sidebar-cta" id="etoro-cta">
          <h3>{html.escape(ui["ready_to_try"])}</h3>
          <p>{html.escape(ui["toms_affiliate"])}</p>
          <a href="{CTA_URL}" class="btn btn-primary" target="_blank" rel="noopener sponsored">{html.escape(ui["explore_etoro"])}</a>
          <div class="risk-warning">
            <strong>{ui["risk_warning_sidebar"].split(".")[0]}.</strong>
            {".".join(ui["risk_warning_sidebar"].split(".")[1:])}
          </div>
        </div>
        <div class="sidebar-nav">
          <h4>{html.escape(ui.get("more_updates", "More updates"))}</h4>
          <ul>
{sidebar_items}            <li><a href="{p}updates.html">{html.escape(back_text)} &rarr;</a></li>
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
  <script src="{p}js/lang-switcher.js"></script>
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


def generate_faq_page(lang, faq_data, hreflang_tags):
    """Generate a translated FAQ page."""
    ui = UI_STRINGS[lang]
    p = "../../"  # 2 levels deep
    slug = faq_data["slug"]
    h1_text = faq_data.get("h1", "FAQ")
    desc = faq_data.get("meta_description", "")
    title = faq_data.get("title", f"{h1_text} | SocialTradingVlog")
    tag = faq_data.get("article_tag", "FAQ")
    meta = faq_data.get("article_meta", "")
    questions = faq_data.get("questions", [])
    sidebar_h3 = faq_data.get("sidebar_h3", ui["ready_to_try"])
    sidebar_p = faq_data.get("sidebar_p", ui["toms_affiliate"])
    sidebar_nav_h4 = faq_data.get("sidebar_nav_h4", "Guides")

    dir_attr = ' dir="rtl"' if lang == "ar" else ""

    # Build FAQ schema
    faq_entities = []
    for q in questions:
        faq_entities.append({
            "@type": "Question",
            "name": q["question"],
            "acceptedAnswer": {"@type": "Answer", "text": q["answer"]}
        })
    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_entities
    }, indent=4, ensure_ascii=False)

    # Build question HTML
    qa_html = ""
    for q in questions:
        qa_html += f'''
        <h2>{html.escape(q["question"])}</h2>
        <p>{q["answer"]}</p>
'''

    # Sidebar guides
    sidebar_items = "\n".join(
        f'            <li><a href="{p}{href}">{html.escape(label)}</a></li>'
        for href, label in [
            ("social-trading.html", ui["guide_social"]),
            ("copy-trading.html", ui["guide_copy"]),
            ("etoro-scam.html", ui["guide_scam"]),
            ("copy-trading-returns.html", ui["guide_returns"]),
            ("taking-profits.html", ui.get("guide_profits", "Taking Profits")),
            ("etoro-review/", "eToro Review 2026"),
        ]
    )

    return f'''<!DOCTYPE html>
<html lang="{lang}"{dir_attr}>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{html.escape(desc)}" />
  <meta property="og:title" content="{html.escape(title)}" />
  <meta property="og:description" content="{html.escape(desc)}" />
  <meta property="og:type" content="website" />
  <link rel="canonical" href="{BASE_URL}/{lang}/{slug}/" />
{hreflang_tags}
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{p}css/style.css" />
  <script type="application/ld+json">
  {faq_schema}
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
      <h1>{html.escape(h1_text)}</h1>
      <p class="article-meta">{html.escape(meta)}</p>
    </div>
  </div>

  <div class="container">
    <div class="article-body">

      <article class="article-content">

        <div class="risk-warning">
          <strong>{html.escape(ui["risk_warning_label"])}</strong>
          {ui["risk_warning_full"]}
        </div>
{qa_html}
        <div class="risk-warning">
          <strong>{html.escape(ui.get("important_reminder", "Important Reminder"))}</strong>
          {ui["risk_warning_full"]}
        </div>

      </article>

      <aside class="article-sidebar">
        <div class="sidebar-cta" id="etoro-cta">
          <h3>{html.escape(sidebar_h3)}</h3>
          <p>{html.escape(sidebar_p)}</p>
          <a href="{CTA_URL}" class="btn btn-primary" target="_blank" rel="noopener sponsored">{html.escape(ui["explore_etoro"])}</a>
          <div class="risk-warning">
            <strong>{ui["risk_warning_sidebar"].split(".")[0]}.</strong>
            {".".join(ui["risk_warning_sidebar"].split(".")[1:])}
          </div>
        </div>
        <div class="sidebar-nav">
          <h4>{html.escape(sidebar_nav_h4)}</h4>
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
  <script src="{p}js/lang-switcher.js"></script>
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


def generate_contact_page(lang, contact_data, hreflang_tags):
    """Generate a translated contact page."""
    ui = UI_STRINGS[lang]
    p = "../../"
    slug = contact_data["slug"]
    h1_text = contact_data.get("h1", "Contact")
    desc = contact_data.get("meta_description", "")
    title = contact_data.get("title", f"{h1_text} | SocialTradingVlog")
    tag = contact_data.get("article_tag", "Contact")
    intro = contact_data.get("intro", "")
    form = contact_data.get("form_labels", {})
    reminder_title = contact_data.get("reminder_title", "Reminder")
    reminder_text = contact_data.get("reminder_text", "")

    dir_attr = ' dir="rtl"' if lang == "ar" else ""

    return f'''<!DOCTYPE html>
<html lang="{lang}"{dir_attr}>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{html.escape(desc)}" />
  <link rel="canonical" href="{BASE_URL}/{lang}/{slug}/" />
{hreflang_tags}
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{p}css/style.css" />
  <style>
    .contact-form {{
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 40px;
      max-width: 600px;
    }}
    .form-group {{ margin-bottom: 20px; }}
    .form-group label {{
      display: block;
      font-size: 0.88rem;
      font-weight: 600;
      margin-bottom: 8px;
      color: var(--text);
    }}
    .form-group input,
    .form-group textarea {{
      width: 100%;
      background: var(--bg3);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 12px 14px;
      color: var(--text);
      font-size: 0.95rem;
      font-family: inherit;
      transition: border-color 0.2s;
    }}
    .form-group input:focus,
    .form-group textarea:focus {{
      outline: none;
      border-color: var(--accent);
    }}
    .form-group textarea {{ min-height: 140px; resize: vertical; }}
  </style>
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
      <h1>{html.escape(h1_text)}</h1>
    </div>
  </div>

  <section>
    <div class="container">
      <p style="color:var(--muted); margin-bottom: 32px; max-width: 560px;">{html.escape(intro)}</p>

      <form class="contact-form" action="https://formspree.io/f/FORM_ID_HERE" method="POST">
        <input type="hidden" name="_subject" value="New message from SocialTradingVlog ({lang})" />
        <input type="hidden" name="_next" value="https://socialtradingvlog.com/contact-thanks.html" />
        <input type="text" name="_gotcha" style="display:none" />
        <div class="form-group">
          <label for="name">{html.escape(form.get("name", "Your name"))}</label>
          <input type="text" id="name" name="name" placeholder="{html.escape(form.get("name_placeholder", ""))}" required />
        </div>
        <div class="form-group">
          <label for="email">{html.escape(form.get("email", "Email"))}</label>
          <input type="email" id="email" name="email" placeholder="{html.escape(form.get("email_placeholder", ""))}" required />
        </div>
        <div class="form-group">
          <label for="message">{html.escape(form.get("message", "Message"))}</label>
          <textarea id="message" name="message" placeholder="{html.escape(form.get("message_placeholder", ""))}" required></textarea>
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%">{html.escape(form.get("submit", "Send message"))}</button>
      </form>

      <div class="risk-warning" style="max-width:600px; margin-top: 32px;">
        <strong>{html.escape(reminder_title)}</strong>
        {html.escape(reminder_text)}
      </div>
    </div>
  </section>

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
  <script src="{p}js/lang-switcher.js"></script>
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


def main():
    parser = argparse.ArgumentParser(description="Generate translated update/FAQ/contact pages")
    parser.add_argument("--lang", help="Generate only this language")
    parser.add_argument("--type", choices=["updates", "faq", "contact"], help="Generate only this type")
    parser.add_argument("--force", action="store_true", help="Overwrite existing pages")
    args = parser.parse_args()

    available_langs = get_available_languages()
    if not available_langs:
        print("No translation files found (updates_faq_contact_*.json)")
        return

    # Load all translations for hreflang building
    all_translations = {}
    for lang in available_langs:
        data = load_translations(lang)
        if data:
            all_translations[lang] = data

    english_content = load_english_content()

    count = 0

    for lang in available_langs:
        if args.lang and lang != args.lang:
            continue

        trans = all_translations.get(lang, {})

        # Generate update posts
        if not args.type or args.type == "updates":
            updates = trans.get("updates", {})
            for page_id, update_data in updates.items():
                slug = update_data.get("slug", page_id)
                en_post = english_content.get(page_id, {})

                hreflang = build_update_hreflang(page_id, available_langs, all_translations, english_content)

                out_dir = BASE_DIR / lang / "updates" / slug
                out_file = out_dir / "index.html"

                if out_file.exists() and not args.force:
                    print(f"  SKIP {lang}/updates/{slug}/ (exists)")
                    continue

                out_dir.mkdir(parents=True, exist_ok=True)
                page_html = generate_update_page(lang, page_id, update_data, en_post, hreflang)
                out_file.write_text(page_html, encoding="utf-8")
                count += 1
                print(f"  WROTE {lang}/updates/{slug}/index.html")

        # Generate FAQ page
        if not args.type or args.type == "faq":
            faq_data = trans.get("faq", {})
            if faq_data and "slug" in faq_data:
                slug = faq_data["slug"]
                hreflang = build_page_hreflang("faq", available_langs, all_translations, "faq.html")
                out_dir = BASE_DIR / lang / slug
                out_file = out_dir / "index.html"

                if out_file.exists() and not args.force:
                    print(f"  SKIP {lang}/{slug}/ (exists)")
                else:
                    out_dir.mkdir(parents=True, exist_ok=True)
                    page_html = generate_faq_page(lang, faq_data, hreflang)
                    out_file.write_text(page_html, encoding="utf-8")
                    count += 1
                    print(f"  WROTE {lang}/{slug}/index.html")

        # Generate contact page
        if not args.type or args.type == "contact":
            contact_data = trans.get("contact", {})
            if contact_data and "slug" in contact_data:
                slug = contact_data["slug"]
                hreflang = build_page_hreflang("contact", available_langs, all_translations, "contact.html")
                out_dir = BASE_DIR / lang / slug
                out_file = out_dir / "index.html"

                if out_file.exists() and not args.force:
                    print(f"  SKIP {lang}/{slug}/ (exists)")
                else:
                    out_dir.mkdir(parents=True, exist_ok=True)
                    page_html = generate_contact_page(lang, contact_data, hreflang)
                    out_file.write_text(page_html, encoding="utf-8")
                    count += 1
                    print(f"  WROTE {lang}/{slug}/index.html")

    print(f"\nDone — {count} page(s) generated.")


if __name__ == "__main__":
    main()
