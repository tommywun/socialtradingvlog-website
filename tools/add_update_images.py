#!/usr/bin/env python3
"""
Add topical images to update pages that don't already have them.

Scans each update HTML file, matches content to relevant images from the
existing image library (eToro screenshots, trader stats, charts, etc.),
and inserts them at varied positions throughout the article.

One-time script — safe to re-run (skips pages that already have images).

Usage:
    python3 tools/add_update_images.py
    python3 tools/add_update_images.py --dry-run
"""

import pathlib
import re
import argparse

PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent
UPDATES_DIR = PROJECT_DIR / "updates"
IMAGES_DIR = PROJECT_DIR / "images"
IMG_PREFIX = "../images"

# ── Header images: page basename (without .html) → image filename ──
HEADER_IMAGES = {
    "social-trading-update-jun-2017": "Etoro-Copy-Trading-Update-Website-2018.png",
    "copy-trading-update-28-nov-2017": "Etoro-Copy-Trading-Update-Website-2018.png",
    "copy-trading-update-jul-2018": "Etoro-Copy-Trading-Update-Website-2018.png",
    "copy-trading-update-23-aug-2018": "Etoro-Copy-trading-update-23-aug-2018.png",
    "copy-trading-update-25-nov-2018": "Etoro-Copy-Trading-Update-November-2018.png",
    "copy-trading-update-14-dec-2018": "Etoro-Copy-Trading-Update-Dec-14-2018.png",
    "copy-trading-update-11-jan-2019": "Etoro-Copy-Trading-Update-11-jan-2019.png",
    "copy-trading-update-13-jan-2019": "COPY-TRADING-UPDATE-3.png",
    "copy-trading-update-29-jan-2019": "Copy-Trading-Update-Jan-29-2019.png",
    "copy-trading-update-03-feb-2019": "Etoro-Copy-Trading-Update-3-feb-2019.png",
    "copy-trading-update-07-feb-2019": "Etoro-Copy-Trading-Update-7-feb-2019.png",
    "copy-trading-update-14-feb-2019": "Copy-Trading-Update-Etoro-14-feb-2019.png",
    "copy-trading-update-20-feb-2019": "Copy-Trading-Update-Etoro-20-feb-2019.png",
    "copy-trading-update-01-mar-2019": "Copy-Trading-Update-Etoro-01-march-2019.png",
    "copy-trading-update-13-mar-2019": "Etoro-Copy-Trading-Update-13-March-2019.png",
    "copy-trading-update-26-mar-2019": "Etoro-copy-trading-update-26-march-2019.png",
    "copy-trading-update-04-apr-2019": "Etoro-Copy-Trading-Update-04-April-2019.png",
    "copy-trading-update-16-apr-2019": "Etoro-Copy-Trading-Update-16-April-2019.png",
    "copy-trading-update-23-jul-2019": "Etoro-Copy-Trading-Update-23-July-2019.png",
    "copy-trading-update-02-aug-2019": "Etoro-Copy-Trading-Update-02-Aug-2019.png",
    "copy-trading-update-29-dec-2025": "Copytrading-investment-growth-1024x576.png",
    "copy-trading-update-11-dec-2025": "Etoro-Copytrading-chart-1024x673.png",
    "copy-trading-update-01-sep-2025": "Bitcoin-historic-Chart.png",
}

# ── Keyword → image list (searched in order, first match used per keyword) ──
KEYWORD_IMAGES = [
    # Specific traders — high priority
    ("alnayef", [
        ("Alnayef-12-month-trading-stats-etoro.png", "Alnayef 12-month trading statistics on eToro"),
        ("Alnayef-open-trade-may-07-2019-eToro-2400x1300.png", "Alnayef open trades on eToro — May 2019"),
        ("alnayef-fees-on-trades-may-2019-2400x1300.png", "Alnayef trading fees on eToro — May 2019"),
    ]),
    ("berrau", [
        ("Berrau-eToro-June-2019-profit-statistics-15-June-2019-1024x551.png", "Berrau profit statistics on eToro — June 2019"),
        ("Berrau-closed-trades-may-07-2019-eToro-2400x1300.png", "Berrau closed trades on eToro — May 2019"),
        ("Berrau-short-term-AUDUSD-trades-june-2019-2400x1150.png", "Berrau short-term AUD/USD trades on eToro — June 2019"),
    ]),
    ("harshsmith", [
        ("HArsmith-open-trades-etoro-14-May-2019-2400x1300.png", "Harshsmith open trades on eToro — May 2019"),
        ("Harshsmith-risk-scores-max-yerly-drawdonw-may-2019-1024x657.png", "Harshsmith risk scores and max yearly drawdown on eToro"),
    ]),
    ("chocowin", [
        ("Chocowin-risk-scores-max-yearly-drawdown-May-2019-1024x657.png", "Chocowin risk scores and max yearly drawdown on eToro"),
    ]),
    ("jaynemesis", [
        ("Jaynemesis-trading-stats-Etoro.png", "Jaynemesis trading statistics on eToro"),
    ]),
    ("olivier", [
        ("Olivier-Danvel-cost-averaging-forex-may-2019-2400x1264.png", "Olivier Danvel cost-averaging forex positions on eToro"),
        ("Olivier-eToro-0.45-May-14-2019-2400x1300.png", "Olivier Danvel eToro trading performance — May 2019"),
    ]),
    # Popular Investor program
    ("popular investor", [
        ("PI-Benefits-1600x1038.png", "eToro Popular Investor program benefits breakdown"),
        ("eToro-Popular-Investor-Signup-Page-2400x1300.png", "eToro Popular Investor program signup page"),
        ("Copy-People-Page-eToro-PI-Program-2260x1300.png", "eToro Copy People page — Popular Investor program"),
    ]),
    # Crypto / Ethereum / Bitcoin
    ("ethereum", [
        ("crypto-risk-in-copytrading-to-the-moon.jpg", "Cryptocurrency risk in copy trading — to the moon"),
        ("Bitcoin-historic-Chart.png", "Cryptocurrency historical price chart"),
    ]),
    ("bitcoin", [
        ("Bitcoin-historic-Chart.png", "Bitcoin historical price chart"),
        ("crypto-risk-in-copytrading-to-the-moon.jpg", "Cryptocurrency risk in copy trading"),
    ]),
    ("crypto", [
        ("crypto-risk-in-copytrading-to-the-moon.jpg", "Cryptocurrency risk in copy trading"),
        ("Bitcoin-historic-Chart.png", "Cryptocurrency historical price chart"),
    ]),
    ("staking", [
        ("crypto-risk-in-copytrading-to-the-moon.jpg", "Cryptocurrency staking and copy trading"),
    ]),
    # Gold / Silver / Commodities
    ("gold", [
        ("Gold-mini-chart-on-Etoro.png", "Gold price mini chart on eToro"),
        ("bag-of-gold.jpg", "Bag of gold coins — gold investment"),
    ]),
    ("silver", [
        ("U.S-Silver-Eagle-1-ounce-coin.jpg", "American Silver Eagle one-ounce coin — silver investment"),
    ]),
    ("commodit", [
        ("Gold-mini-chart-on-Etoro.png", "Commodities chart on eToro — gold"),
    ]),
    # Fees / Costs
    ("fees", [
        ("Fees-page-on-eToro.png", "eToro fees page showing trading costs explained"),
        ("My-copy-trading-portfolio-Alnayef-fees-june-2019-1600x822.png", "Copy trading portfolio fees on eToro"),
    ]),
    # Risk
    ("risk score", [
        ("Risk-Score-chart-Etoro-example-1024x466.png", "eToro risk score chart example"),
    ]),
    ("drawdown", [
        ("Risk-Score-chart-Etoro-example-1024x466.png", "eToro risk score and drawdown chart"),
    ]),
    # Copy Stop Loss
    ("stop loss", [
        ("Pause-Copy-Button-on-Etoro-Social-Trading.png", "Pause Copy button on eToro social trading platform"),
        ("Resume-Copy-Button-Etoro-Copy-Trading-1.png", "Resume Copy button on eToro"),
    ]),
    # Portfolio / stats
    ("portfolio", [
        ("Etoro-Copytrading-chart-1024x673.png", "eToro copy trading portfolio chart"),
        ("Copytrading-investment-growth-1024x576.png", "Copy trading investment growth over time"),
        ("My-Copy-Trading-Portfolio-June-15-2019-2400x1300.png", "My copy trading portfolio on eToro — June 2019"),
    ]),
    ("profit", [
        ("Trader-profit-percentage-etoro-1024x275.png", "Trader profit percentage on eToro"),
        ("10-profit-copytrading-in-a-month.png", "10% profit in copy trading in a month"),
    ]),
    # Forex
    ("forex", [
        ("AUD-USD-Forex-trade-June-2019-Berrau.png", "AUD/USD forex trade on eToro — June 2019"),
    ]),
    # Apple / S&P / Equities
    ("apple", [
        ("Apple-Equities-Copytrading-Mini-chart.png", "Apple equities mini chart on eToro"),
        ("apple-price-targets-12-months-1024x642.png", "Apple stock 12-month price targets"),
    ]),
    ("s&p", [
        ("SP-500-ETF-Chart.png", "S&P 500 ETF price chart"),
    ]),
    ("equit", [
        ("SP-500-ETF-Chart.png", "S&P 500 ETF price chart — equities"),
    ]),
    # Withdraw / Balance
    ("withdraw", [
        ("Available-balance-area-on-Etoro-social-trading.png", "Available balance area on eToro"),
        ("Uploading-money-to-etoro-euros.png", "Uploading money to eToro account"),
    ]),
    ("euro account", [
        ("Uploading-money-to-etoro-euros.png", "Uploading money to eToro in euros"),
    ]),
    # Browse / Copy traders
    ("copy trader", [
        ("Range-of-traders-to-copy-1024x579.png", "Range of traders to copy on eToro"),
        ("Copy-traders-over-100.png", "Over 100 traders to copy on eToro"),
    ]),
    ("browse", [
        ("Range-of-traders-to-copy-1024x579.png", "Browsing traders to copy on eToro"),
    ]),
]

# ── Generic fallback images (used when no keyword matches) ──
GENERIC_IMAGES = [
    ("Range-of-traders-to-copy-1024x579.png", "Range of traders to copy on eToro"),
    ("etoro-trader-stats-12-months.png", "eToro trader statistics over 12 months"),
    ("Etoro-Copytrading-chart-1024x673.png", "eToro copy trading portfolio performance chart"),
    ("Risk-Score-chart-Etoro-example-1024x466.png", "eToro risk score chart example"),
    ("Copytrading-investment-growth-1024x576.png", "Copy trading investment growth over time"),
    ("Copy-traders-over-100.png", "Over 100 traders available to copy on eToro"),
    ("fifty-five-trader-stats-etoro.png", "Trader statistics dashboard on eToro"),
    ("Trader-profit-percentage-etoro-1024x275.png", "Trader profit percentage displayed on eToro"),
]

# Layout styles to cycle through for variety
LAYOUTS = ["block", "float-right", "block", "float-left"]


def page_has_content_images(content):
    """Check if article-content already contains <img> tags (excluding the video-embed)."""
    start = content.find('<article class="article-content">')
    if start == -1:
        return True  # can't find article, skip it
    end = content.find('</article>', start)
    article = content[start:end] if end != -1 else content[start:]
    # Ignore any images that might be in the video-embed or newsletter
    # Count actual content images
    img_count = len(re.findall(r'<img\s', article))
    return img_count > 0


def find_matching_images(content, used_images):
    """Find images matching content keywords. Returns list of (filename, alt_text)."""
    content_lower = content.lower()
    matches = []

    for keyword, images in KEYWORD_IMAGES:
        if keyword.lower() in content_lower:
            for img_file, alt_text in images:
                if img_file not in used_images:
                    matches.append((img_file, alt_text))
                    used_images.add(img_file)
                    break  # one image per keyword

    return matches


def find_section_images(content, h2_positions, used_images):
    """Find images relevant to specific sections (between h2 headings)."""
    results = []  # list of (h2_index, img_file, alt_text)

    for i, (start, end) in enumerate(h2_positions):
        section_text = content[start:end].lower()
        found = False

        for keyword, images in KEYWORD_IMAGES:
            if keyword.lower() in section_text:
                for img_file, alt_text in images:
                    if img_file not in used_images:
                        results.append((i, img_file, alt_text))
                        used_images.add(img_file)
                        found = True
                        break
            if found:
                break

    return results


def make_image_html(img_file, alt_text, layout):
    """Generate HTML for an image with the given layout style."""
    if layout == "block":
        return (
            f'\n<img src="{IMG_PREFIX}/{img_file}" '
            f'alt="{alt_text}" '
            f'style="max-width:100%;height:auto;border-radius:8px;margin:24px 0;display:block;" '
            f'loading="lazy">\n'
        )
    elif layout == "float-right":
        return (
            f'\n<div class="review-float-right">'
            f'<img src="{IMG_PREFIX}/{img_file}" '
            f'alt="{alt_text}" '
            f'style="max-width:100%;height:auto;border-radius:8px;" '
            f'loading="lazy"></div>\n'
        )
    elif layout == "float-left":
        return (
            f'\n<div class="review-float-left">'
            f'<img src="{IMG_PREFIX}/{img_file}" '
            f'alt="{alt_text}" '
            f'style="max-width:100%;height:auto;border-radius:8px;" '
            f'loading="lazy"></div>\n'
        )
    return ""


def upgrade_h3_to_h2(content):
    """Convert ALL h3 content headings to h2 within article-content for uniformity.

    Upgrades h3 tags in the article body to h2. Skips h3 tags that are
    in sidebar, newsletter, or footer sections.
    """
    article_start = content.find('<article class="article-content">')
    if article_start == -1:
        return content

    article_end = content.find('</article>', article_start)
    if article_end == -1:
        article_end = len(content)

    # Process only the article section
    before = content[:article_start]
    article = content[article_start:article_end]
    after = content[article_end:]

    # Replace h3 tags, but skip ones inside newsletter/sidebar divs
    def replace_h3(match):
        pos = match.start()
        # Check preceding context for sidebar/newsletter markers
        preceding = article[max(0, pos - 400):pos]
        if 'newsletter' in preceding.lower() or 'sidebar' in preceding.lower():
            return match.group(0)
        tag = match.group(0)
        return tag.replace('<h3', '<h2').replace('</h3>', '</h2>')

    article = re.sub(r'<h3[^>]*>.*?</h3>', replace_h3, article, flags=re.DOTALL)
    return before + article + after


def find_h2_sections(content):
    """Find positions of content headings and their sections in article-content.

    Looks for h2 headings first; if none found, falls back to h3.
    Only considers headings within <article class="article-content">.
    """
    article_start = content.find('<article class="article-content">')
    if article_start == -1:
        return []
    article_end = content.find('</article>', article_start)
    if article_end == -1:
        article_end = len(content)

    # Try h2 first, fall back to h3
    for tag in ('h2', 'h3'):
        positions = []
        for m in re.finditer(rf'<{tag}[^>]*>', content[article_start:article_end]):
            abs_pos = article_start + m.start()
            # Skip headings in sidebar, newsletter, or footer sections
            preceding = content[abs_pos - 200:abs_pos] if abs_pos > 200 else content[:abs_pos]
            if 'sidebar' in preceding or 'newsletter' in preceding or 'footer' in preceding:
                continue
            positions.append(abs_pos)

        if positions:
            sections = []
            for i, pos in enumerate(positions):
                end = positions[i + 1] if i + 1 < len(positions) else article_end
                sections.append((pos, end))
            return sections

    return []


def find_insertion_point_after_heading(content, heading_pos):
    """Find the best insertion point after a heading (h2 or h3).

    Insert after the first </p> following the heading, so the image sits
    between the intro paragraph and the rest of the section.
    """
    # Find the closing tag (</h2> or </h3>)
    h_close = content.find('</h', heading_pos)
    if h_close == -1:
        return heading_pos
    # Skip past the closing tag (e.g., </h2> or </h3>)
    h_close_end = content.find('>', h_close)
    if h_close_end == -1:
        return heading_pos
    h_close_end += 1

    # Find first paragraph after the heading
    first_p_close = content.find('</p>', h_close_end)
    if first_p_close == -1 or first_p_close > heading_pos + 2000:
        # No paragraph found nearby, insert right after heading
        return h_close_end

    return first_p_close + 4  # len('</p>')


def process_file(filepath, dry_run=False):
    """Process a single update HTML file, adding images if needed."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  Error reading {filepath.name}: {e}")
        return False

    # Always upgrade h3→h2 for uniformity (even on pages with images)
    updated_content = upgrade_h3_to_h2(content)
    h3_upgraded = updated_content != content
    content = updated_content

    # Check if page already has content images
    already_has_images = page_has_content_images(content)

    if already_has_images and not h3_upgraded:
        print(f"  Skipping {filepath.name} — already has images")
        return False

    if already_has_images and h3_upgraded:
        # Only save the h3→h2 changes, no new images
        if not dry_run:
            filepath.write_text(content, encoding="utf-8")
            print(f"  Upgraded h3→h2 headings in {filepath.name}")
        else:
            print(f"  Would upgrade h3→h2 headings in {filepath.name}")
        return True

    page_base = filepath.stem  # filename without .html
    used_images = set()
    insertions = []  # list of (position, html) — applied in reverse order

    # 1. Insert header image after video-embed
    header_img = HEADER_IMAGES.get(page_base)
    if header_img and (IMAGES_DIR / header_img).exists():
        used_images.add(header_img)
        video_embed_close = content.find('</iframe>')
        if video_embed_close != -1:
            # Find the closing </div> of the video-embed container
            div_close = content.find('</div>', video_embed_close)
            if div_close != -1:
                insert_pos = div_close + 6  # len('</div>')
                alt = f"Copy trading update — {page_base.replace('copy-trading-update-', '').replace('social-trading-update-', '')}"
                header_html = make_image_html(header_img, alt, "block")
                insertions.append((insert_pos, header_html))

    # 2. Find h2 sections and match images
    sections = find_h2_sections(content)
    section_images = find_section_images(content, sections, used_images)

    # Limit to 3 content images max (plus header)
    section_images = section_images[:3]

    # If we got fewer than 2 images from keywords, add generic ones
    if len(section_images) < 2 and len(sections) >= 2:
        generic_idx = 0
        for i in range(len(sections)):
            if len(section_images) >= 3:
                break
            # Skip sections that already have an image
            if any(si == i for si, _, _ in section_images):
                continue
            # Add a generic image
            while generic_idx < len(GENERIC_IMAGES):
                img_file, alt_text = GENERIC_IMAGES[generic_idx]
                generic_idx += 1
                if img_file not in used_images and (IMAGES_DIR / img_file).exists():
                    section_images.append((i, img_file, alt_text))
                    used_images.add(img_file)
                    break

    # Space out images — don't put them on consecutive headings
    if len(section_images) > 1:
        spaced = [section_images[0]]
        last_idx = section_images[0][0]
        for si, img, alt in section_images[1:]:
            if si > last_idx + 1 or len(spaced) < 2:
                spaced.append((si, img, alt))
                last_idx = si
        section_images = spaced[:3]

    # 3. Create insertion points for content images
    layout_idx = 0
    for sec_idx, img_file, alt_text in section_images:
        if sec_idx < len(sections):
            h2_pos = sections[sec_idx][0]
            insert_pos = find_insertion_point_after_heading(content, h2_pos)
            layout = LAYOUTS[layout_idx % len(LAYOUTS)]
            layout_idx += 1
            img_html = make_image_html(img_file, alt_text, layout)
            insertions.append((insert_pos, img_html))

    if not insertions:
        print(f"  No images to add for {filepath.name}")
        return False

    # 4. Apply insertions in reverse order (so positions don't shift)
    insertions.sort(key=lambda x: x[0], reverse=True)
    for pos, html in insertions:
        content = content[:pos] + html + content[pos:]

    total = len(insertions)
    if dry_run:
        print(f"  Would add {total} images to {filepath.name}")
        for pos, html in sorted(insertions, key=lambda x: x[0]):
            img_match = re.search(r'src="[^"]*/(.*?)"', html)
            if img_match:
                print(f"    → {img_match.group(1)}")
    else:
        filepath.write_text(content, encoding="utf-8")
        print(f"  Added {total} images to {filepath.name}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Add images to update pages")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    count = 0
    for f in sorted(UPDATES_DIR.glob("*.html")):
        if process_file(f, dry_run=args.dry_run):
            count += 1

    print(f"\nProcessed {count} pages")


if __name__ == "__main__":
    main()
