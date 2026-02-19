#!/usr/bin/env python3
"""
Extract translatable content from all update post HTML files.

Reads every .html file in ../updates/, parses it with BeautifulSoup,
and writes a structured JSON file to translations/update_posts_content.json.
"""

import json
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

UPDATES_DIR = Path(__file__).resolve().parent.parent / "updates"
OUTPUT_DIR = Path(__file__).resolve().parent / "translations"
OUTPUT_FILE = OUTPUT_DIR / "update_posts_content.json"


def is_boilerplate_paragraph(p_tag):
    """Return True if this <p> is boilerplate we should skip."""
    text = p_tag.get_text(strip=True)

    # "← Back to all updates" link
    if "Back to all updates" in text:
        return True

    # "Want to see my current eToro statistics?" link paragraph
    if "Want to see my current eToro statistics?" in text:
        return True

    return False


def extract_content_blocks(article):
    """
    Walk through direct children of the <article class="article-content">,
    skipping the first risk-warning div and video-embed div, then extract
    all meaningful content blocks in order.
    """
    blocks = []
    found_first_risk_warning = False
    found_video = False

    for child in article.children:
        # Skip NavigableStrings (whitespace, newlines)
        if isinstance(child, NavigableString):
            continue

        tag_name = child.name
        if tag_name is None:
            continue

        classes = child.get("class", [])

        # --- Skip the first risk-warning div (standard boilerplate at top) ---
        if tag_name == "div" and "risk-warning" in classes:
            if not found_first_risk_warning:
                found_first_risk_warning = True
                continue
            else:
                # Mid-content risk warning — include it
                text = child.get_text(" ", strip=True)
                blocks.append({"type": "risk_warning", "text": text})
                continue

        # --- Skip video-embed divs (but record nothing — handled separately) ---
        if tag_name == "div" and "video-embed" in classes:
            found_video = True
            continue

        # --- Detect image grids: div with display:grid in style ---
        if tag_name == "div":
            style = child.get("style", "")
            if "display:grid" in style or "display: grid" in style:
                images = []
                for img in child.find_all("img"):
                    images.append({
                        "src": img.get("src", ""),
                        "alt": img.get("alt", ""),
                    })
                if images:
                    blocks.append({"type": "img_grid", "images": images})
                continue

        # --- Paragraphs ---
        if tag_name == "p":
            if is_boilerplate_paragraph(child):
                continue
            # Include full inner HTML (preserves links etc.)
            inner_html = child.decode_contents().strip()
            blocks.append({"type": "p", "text": inner_html})
            continue

        # --- Headings ---
        if tag_name in ("h2", "h3"):
            text = child.get_text(strip=True)
            blocks.append({"type": tag_name, "text": text})
            continue

        # --- Standalone images ---
        if tag_name == "img":
            blocks.append({
                "type": "img",
                "src": child.get("src", ""),
                "alt": child.get("alt", ""),
            })
            continue

    return blocks


def extract_page(filepath):
    """Extract all translatable content from a single update HTML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    data = {}

    # --- Filename / page ID ---
    filename = os.path.basename(filepath)
    page_id = filename.replace(".html", "")
    data["filename"] = filename

    # --- <head> ---
    meta_desc = soup.find("meta", attrs={"name": "description"})
    data["meta_description"] = meta_desc["content"] if meta_desc else ""

    title_tag = soup.find("title")
    data["title"] = title_tag.get_text(strip=True) if title_tag else ""

    # --- article-hero ---
    hero = soup.find("div", class_="article-hero")
    if hero:
        tag_div = hero.find("div", class_="article-tag")
        data["article_tag"] = tag_div.get_text(strip=True) if tag_div else ""

        h1 = hero.find("h1")
        data["h1"] = h1.get_text(strip=True) if h1 else ""

    # --- Video embed ---
    article = soup.find("article", class_="article-content")
    if article:
        video_div = article.find("div", class_="video-embed")
        if video_div:
            iframe = video_div.find("iframe")
            if iframe:
                data["video_embed_src"] = iframe.get("src", "")
                data["video_embed_title"] = iframe.get("title", "")

        # --- Content blocks ---
        data["content_blocks"] = extract_content_blocks(article)

    # --- Sidebar nav ---
    sidebar_nav = soup.find("div", class_="sidebar-nav")
    if sidebar_nav:
        links = []
        for a in sidebar_nav.find_all("a"):
            links.append({
                "text": a.get_text(strip=True),
                "href": a.get("href", ""),
            })
        data["sidebar_links"] = links

    return page_id, data


def main():
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    html_files = sorted(UPDATES_DIR.glob("*.html"))
    if not html_files:
        print("No HTML files found in", UPDATES_DIR)
        return

    result = {}
    for fpath in html_files:
        page_id, data = extract_page(fpath)
        result[page_id] = data

    # Sort by key (filename without extension)
    result = dict(sorted(result.items()))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(result)} update posts → {OUTPUT_FILE}")

    # Print summary of first entry
    first_key = next(iter(result))
    first = result[first_key]
    print(f"\n--- Sample: {first_key} ---")
    print(f"  title:            {first.get('title', '')}")
    print(f"  meta_description: {first.get('meta_description', '')}")
    print(f"  article_tag:      {first.get('article_tag', '')}")
    print(f"  h1:               {first.get('h1', '')}")
    print(f"  video_embed_src:  {first.get('video_embed_src', '')}")
    print(f"  video_embed_title:{first.get('video_embed_title', '')}")
    print(f"  content_blocks:   {len(first.get('content_blocks', []))} blocks")
    for i, block in enumerate(first.get("content_blocks", [])):
        btype = block["type"]
        if btype in ("p", "h2", "h3", "risk_warning"):
            preview = block["text"][:80]
            print(f"    [{i}] {btype}: {preview}...")
        elif btype == "img":
            print(f"    [{i}] img: src={block['src']}, alt={block['alt'][:40]}")
        elif btype == "img_grid":
            print(f"    [{i}] img_grid: {len(block['images'])} images")
    print(f"  sidebar_links:    {first.get('sidebar_links', [])}")


if __name__ == "__main__":
    main()
