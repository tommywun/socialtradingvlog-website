#!/usr/bin/env python3
"""
Daily opportunity scanner: finds questions about eToro, copy trading, and social
trading across Reddit, Stack Exchange, Hacker News, and other platforms.

Generates a markdown digest with the best opportunities for Tom to reply to
with a helpful answer + natural link to socialtradingvlog.com.

Usage:
    python3 tools/opportunity_scanner.py           # scan and generate report
    python3 tools/opportunity_scanner.py --test     # test connectivity only
"""

import json
import urllib.request
import urllib.parse
import html
import os
import re
import time
import argparse
from datetime import datetime, timedelta

SITE_URL = "https://socialtradingvlog.com"

# --- Keywords to scan for ---

CORE_KEYWORDS = [
    "etoro",
    "copy trading",
    "social trading",
]

EXTENDED_KEYWORDS = [
    "etoro review",
    "etoro scam",
    "is etoro safe",
    "etoro fees",
    "etoro copy",
    "copy trading beginners",
    "copy trading profit",
    "copy trading risk",
    "copy trader",
    "who to copy on etoro",
    "etoro popular investor",
    "etoro withdraw",
    "etoro vs",
]

# --- Reddit config ---

SUBREDDITS_PRIMARY = [
    "etoro", "copytrading", "UKInvesting", "eupersonalfinance",
]

SUBREDDITS_SECONDARY = [
    "investing", "stocks", "personalfinance", "trading",
    "Daytrading", "Forex", "UKPersonalFinance", "AusFinance",
    "CanadianInvestor", "dividends",
]

ALL_SUBREDDITS = SUBREDDITS_PRIMARY + SUBREDDITS_SECONDARY


def fetch_json(url, headers=None):
    """Fetch JSON from a URL with basic error handling."""
    if headers is None:
        headers = {"User-Agent": "STV-OpportunityScanner/1.0 (contact: tradertommalta@gmail.com)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"_error": str(e)}


# ─────────────────────────────────────────────
# Reddit (free public JSON API, no auth needed)
# ─────────────────────────────────────────────

def scan_reddit():
    """Scan Reddit for recent posts matching our keywords."""
    results = []
    seen_ids = set()

    for keyword in CORE_KEYWORDS + EXTENDED_KEYWORDS[:5]:
        encoded = urllib.parse.quote(keyword)
        url = f"https://www.reddit.com/search.json?q={encoded}&sort=new&t=week&limit=25"

        data = fetch_json(url)
        if "_error" in data:
            continue

        time.sleep(1.5)  # Reddit rate-limits aggressively

        for post in data.get("data", {}).get("children", []):
            p = post["data"]
            post_id = p["id"]

            if post_id in seen_ids:
                continue
            seen_ids.add(post_id)

            subreddit = p.get("subreddit", "")
            subreddit_lower = subreddit.lower()
            title_lower = p.get("title", "").lower()

            # Must be in a relevant subreddit OR have a very relevant title
            in_primary = subreddit_lower in [s.lower() for s in SUBREDDITS_PRIMARY]
            in_secondary = subreddit_lower in [s.lower() for s in SUBREDDITS_SECONDARY]
            title_relevant = any(kw in title_lower for kw in ["etoro", "copy trad", "social trad"])

            if not (in_primary or in_secondary or title_relevant):
                continue

            num_comments = p.get("num_comments", 0)
            score = p.get("score", 0)
            selftext = (p.get("selftext", "") or "")[:200]

            # Opportunity score: fewer comments = bigger opportunity
            opp = 0
            if in_primary:
                opp += 5  # Core subreddit bonus
            if num_comments < 3:
                opp += 5  # Few replies = opportunity
            elif num_comments < 10:
                opp += 2
            if title_relevant:
                opp += 3
            if score > 5:
                opp += 1  # Has engagement

            results.append({
                "platform": "Reddit",
                "subreddit": f"r/{subreddit}",
                "title": html.unescape(p.get("title", "")),
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "comments": num_comments,
                "score": score,
                "created": datetime.fromtimestamp(p.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M"),
                "selftext": html.unescape(selftext),
                "keyword": keyword,
                "opportunity_score": opp,
            })

    results.sort(key=lambda x: x["opportunity_score"], reverse=True)
    return results


# ─────────────────────────────────────────────────
# Stack Exchange — Money (free API, no auth needed)
# ─────────────────────────────────────────────────

def scan_stackexchange():
    """Scan Personal Finance & Money Stack Exchange for relevant questions."""
    results = []
    seen_ids = set()

    for keyword in ["etoro", "copy trading", "social trading", "copy trader", "copytrading"]:
        encoded = urllib.parse.quote(keyword)
        url = (
            f"https://api.stackexchange.com/2.3/search/advanced"
            f"?order=desc&sort=creation&q={encoded}"
            f"&site=money&filter=default&pagesize=20"
        )

        data = fetch_json(url)
        if "_error" in data or "items" not in data:
            continue

        time.sleep(0.5)

        for q in data["items"]:
            qid = q.get("question_id")
            if qid in seen_ids:
                continue
            seen_ids.add(qid)

            created = datetime.fromtimestamp(q.get("creation_date", 0))
            if (datetime.now() - created).days > 60:
                continue

            answer_count = q.get("answer_count", 0)
            is_answered = q.get("is_answered", False)

            opp = 0
            if not is_answered:
                opp += 5
            if answer_count == 0:
                opp += 5
            elif answer_count < 3:
                opp += 2

            results.append({
                "platform": "StackExchange (Money)",
                "title": html.unescape(q.get("title", "")),
                "url": q.get("link", ""),
                "answers": answer_count,
                "score": q.get("score", 0),
                "views": q.get("view_count", 0),
                "created": created.strftime("%Y-%m-%d"),
                "tags": ", ".join(q.get("tags", [])),
                "is_answered": is_answered,
                "opportunity_score": opp,
            })

    results.sort(key=lambda x: x["opportunity_score"], reverse=True)
    return results


# ─────────────────────────────────────────────────
# Hacker News (free Algolia API, no auth needed)
# ─────────────────────────────────────────────────

def scan_hackernews():
    """Scan Hacker News for relevant discussions."""
    results = []
    seen_ids = set()

    for keyword in ["etoro", "copy trading", "social trading", "copytrading"]:
        encoded = urllib.parse.quote(keyword)
        url = (
            f"https://hn.algolia.com/api/v1/search_by_date"
            f"?query={encoded}&tags=(story,comment)&hitsPerPage=20"
        )

        data = fetch_json(url)
        if "_error" in data or "hits" not in data:
            continue

        time.sleep(0.5)

        for hit in data["hits"]:
            hit_id = hit.get("objectID", "")
            if hit_id in seen_ids:
                continue
            seen_ids.add(hit_id)

            created = hit.get("created_at", "")[:10]
            try:
                created_dt = datetime.strptime(created, "%Y-%m-%d")
                if (datetime.now() - created_dt).days > 30:
                    continue
            except ValueError:
                continue

            title = hit.get("title") or ""
            comment_text = hit.get("comment_text", "") or ""
            # Clean HTML from comment text
            display = re.sub(r'<[^>]+>', '', comment_text)[:100] if comment_text else title

            # Filter out false positives (e.g. "Toronto" matching "etoro")
            full_text = (title + " " + comment_text).lower()
            if keyword.lower() == "etoro" and "etoro" not in full_text:
                continue

            results.append({
                "platform": "Hacker News",
                "title": display,
                "url": f"https://news.ycombinator.com/item?id={hit_id}",
                "points": hit.get("points", 0) or 0,
                "comments": hit.get("num_comments", 0) or 0,
                "created": created,
                "type": "story" if hit.get("title") else "comment",
                "keyword": keyword,
            })

    results.sort(key=lambda x: x.get("points", 0) or 0, reverse=True)
    return results


# ─────────────────────────────────────────────────
# Manual search links (platforms without free APIs)
# ─────────────────────────────────────────────────

def get_manual_search_links():
    """Generate Google search URLs for platforms without APIs."""
    platforms = {
        "Quora": {
            "site": "quora.com",
            "keywords": ["etoro", "copy trading worth it", "is etoro safe",
                         "etoro scam or legit", "copy trading beginners",
                         "copy trading risk", "is copy trading profitable"],
        },
        "BabyPips Forum": {
            "site": "forums.babypips.com",
            "keywords": ["etoro", "copy trading", "social trading"],
        },
        "Trade2Win": {
            "site": "trade2win.com",
            "keywords": ["etoro", "copy trading", "social trading"],
        },
        "Forex Factory": {
            "site": "forexfactory.com",
            "keywords": ["etoro", "copy trading"],
        },
        "Trustpilot (eToro reviews)": {
            "site": "trustpilot.com",
            "keywords": ["etoro"],
            "note": "Reply to recent eToro reviews with your genuine experience",
        },
        "Medium": {
            "site": "medium.com",
            "keywords": ["etoro copy trading", "social trading review", "copy trading results"],
            "note": "Consider writing a Medium article with your real results — these rank well",
        },
        "Elite Trader Forum": {
            "site": "elitetrader.com",
            "keywords": ["etoro", "copy trading", "social trading"],
        },
        "MoneySavingExpert Forum": {
            "site": "forums.moneysavingexpert.com",
            "keywords": ["etoro", "copy trading", "social trading"],
        },
    }

    results = {}
    for platform, config in platforms.items():
        links = []
        for kw in config["keywords"]:
            encoded = urllib.parse.quote(f"site:{config['site']} {kw}")
            links.append({
                "keyword": kw,
                "url": f"https://www.google.com/search?q={encoded}&tbs=qdr:m",
            })
        results[platform] = {
            "links": links,
            "note": config.get("note", ""),
        }
    return results


# ─────────────────────────────────────────────────
# Reply angle suggestions
# ─────────────────────────────────────────────────

def suggest_reply_angle(title):
    """Suggest a reply angle and relevant site link based on the question topic."""
    t = title.lower()

    if any(w in t for w in ["scam", "legit", "safe", "trust", "fraud", "fake"]):
        return (
            "Share your 6+ years of real experience — honest pros AND cons",
            f"{SITE_URL}/etoro-review/",
        )
    elif any(w in t for w in ["lose", "loss", "losing", "76%", "risk", "danger"]):
        return (
            "Explain the 76% stat with real context from your experience",
            f"{SITE_URL}/video/why-do-most-etoro-traders-lose-money/",
        )
    elif any(w in t for w in ["beginner", "start", "new to", "how to", "getting started"]):
        return (
            "Practical getting-started advice from someone who's done it 6 years",
            f"{SITE_URL}/copy-trading.html",
        )
    elif any(w in t for w in ["profit", "return", "make money", "earn", "how much", "worth"]):
        return (
            "Realistic expectations backed by 6 years of documented results",
            f"{SITE_URL}/copy-trading-returns.html",
        )
    elif any(w in t for w in ["fee", "cost", "charge", "spread", "withdraw"]):
        return (
            "Break down real costs with specific numbers from your account",
            f"{SITE_URL}/etoro-review/",
        )
    elif any(w in t for w in ["who to copy", "best trader", "pick trader", "choose"]):
        return (
            "How to evaluate traders — what metrics actually matter",
            f"{SITE_URL}/copy-trading.html",
        )
    elif any(w in t for w in ["take profit", "stop loss", "when to sell", "exit"]):
        return (
            "When and how to take profits from copy trading",
            f"{SITE_URL}/taking-profits.html",
        )
    else:
        return (
            "Share genuine experience as a 6-year eToro user",
            f"{SITE_URL}",
        )


# ─────────────────────────────────────────────────
# Report builder
# ─────────────────────────────────────────────────

def build_report(reddit, stackexchange, hackernews, manual_links):
    """Build the markdown digest report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(reddit) + len(stackexchange) + len(hackernews)

    lines = [
        f"# Opportunity Digest — {now}",
        "",
        f"Found **{total}** opportunities across automated scans,",
        f"plus manual search links for {len(manual_links)} additional platforms.",
        "",
        "**How to use this**: Pick 1-2 best opportunities per day. Write a genuinely",
        "helpful reply, mention your experience naturally, and include a relevant link",
        f"to {SITE_URL} at the end. Quality over quantity.",
        "",
    ]

    # ── Reddit ──
    lines.append("---")
    lines.append(f"## Reddit ({len(reddit)} posts)")
    lines.append("")

    if reddit:
        for i, post in enumerate(reddit[:15], 1):
            angle, link = suggest_reply_angle(post["title"])
            few_comments = " **← FEW REPLIES**" if post["comments"] < 3 else ""
            lines.append(f"### {i}. {post['title'][:90]}")
            lines.append(f"**{post['subreddit']}** | {post['comments']} comments{few_comments} | score {post['score']} | {post['created']}")
            lines.append(f"Link: {post['url']}")
            if post.get("selftext"):
                lines.append(f"> _{post['selftext'][:150]}..._")
            lines.append(f"**Suggested angle**: {angle}")
            lines.append(f"**Relevant page**: {link}")
            lines.append("")
    else:
        lines.append("_No Reddit opportunities found this scan._")
        lines.append("")

    # ── Stack Exchange ──
    lines.append("---")
    lines.append(f"## Stack Exchange — Money ({len(stackexchange)} questions)")
    lines.append("")

    if stackexchange:
        for i, q in enumerate(stackexchange[:10], 1):
            status = "**UNANSWERED**" if not q["is_answered"] else f"{q['answers']} answers"
            angle, link = suggest_reply_angle(q["title"])
            lines.append(f"### {i}. {q['title'][:90]}")
            lines.append(f"{status} | {q['views']} views | score {q['score']} | {q['created']}")
            lines.append(f"Tags: {q['tags']}")
            lines.append(f"Link: {q['url']}")
            lines.append(f"**Suggested angle**: {angle}")
            lines.append(f"**Relevant page**: {link}")
            lines.append("")
    else:
        lines.append("_No Stack Exchange opportunities found._")
        lines.append("")

    # ── Hacker News ──
    lines.append("---")
    lines.append(f"## Hacker News ({len(hackernews)} mentions)")
    lines.append("")

    if hackernews:
        for i, hit in enumerate(hackernews[:10], 1):
            lines.append(f"### {i}. {hit['title'][:90]}")
            lines.append(f"{hit['type']} | {hit['points']} points | {hit['comments']} comments | {hit['created']}")
            lines.append(f"Link: {hit['url']}")
            lines.append("")
    else:
        lines.append("_No recent Hacker News mentions._")
        lines.append("")

    # ── Manual search links ──
    lines.append("---")
    lines.append("## Manual Checks (click to search — last month's posts)")
    lines.append("")
    lines.append("These platforms don't have free APIs. Click each link to see recent")
    lines.append("questions/discussions you could reply to.")
    lines.append("")

    for platform, data in manual_links.items():
        lines.append(f"### {platform}")
        if data["note"]:
            lines.append(f"_{data['note']}_")
        for link in data["links"]:
            lines.append(f"- [{link['keyword']}]({link['url']})")
        lines.append("")

    # ── Tips ──
    lines.append("---")
    lines.append("## Engagement Rules")
    lines.append("")
    lines.append("1. **Answer the question first** — be genuinely helpful")
    lines.append("2. **Mention experience naturally** — \"I've been copy trading on eToro for 6 years...\"")
    lines.append("3. **Link at the end** — \"I wrote about this in more detail here: [link]\"")
    lines.append("4. **Reddit**: Keep to 90/10 ratio (genuine comments vs self-promo)")
    lines.append("5. **Stack Exchange**: Must be factual, well-sourced answers")
    lines.append("6. **Quora**: Personal experience format works best")
    lines.append("7. **Never copy-paste** the same answer twice — customise for each question")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan platforms for link-building opportunities")
    parser.add_argument("--test", action="store_true", help="Test API connectivity only")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    reports_dir = os.path.join(project_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    if args.test:
        print("Testing connectivity...\n")
        ok = 0

        test = fetch_json("https://www.reddit.com/r/etoro/new.json?limit=1")
        if "_error" in test:
            print(f"  Reddit:        FAILED — {test['_error'][:60]}")
        else:
            print("  Reddit:        OK")
            ok += 1

        test = fetch_json("https://api.stackexchange.com/2.3/info?site=money")
        if "_error" in test:
            print(f"  StackExchange: FAILED — {test['_error'][:60]}")
        else:
            print("  StackExchange: OK")
            ok += 1

        test = fetch_json("https://hn.algolia.com/api/v1/search?query=test&hitsPerPage=1")
        if "_error" in test:
            print(f"  Hacker News:   FAILED — {test['_error'][:60]}")
        else:
            print("  Hacker News:   OK")
            ok += 1

        print(f"\n{ok}/3 APIs reachable.")
        return

    print("Scanning platforms for opportunities...\n")

    print("  Scanning Reddit...")
    reddit = scan_reddit()
    print(f"    → {len(reddit)} posts found")

    print("  Scanning Stack Exchange (Money)...")
    stackexchange = scan_stackexchange()
    print(f"    → {len(stackexchange)} questions found")

    print("  Scanning Hacker News...")
    hackernews = scan_hackernews()
    print(f"    → {len(hackernews)} mentions found")

    print("  Generating manual search links...")
    manual_links = get_manual_search_links()

    report = build_report(reddit, stackexchange, hackernews, manual_links)

    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(reports_dir, f"opportunities-{date_str}.md")
    latest_path = os.path.join(reports_dir, "opportunities-latest.md")

    with open(report_path, "w") as f:
        f.write(report)
    with open(latest_path, "w") as f:
        f.write(report)

    total = len(reddit) + len(stackexchange) + len(hackernews)
    print(f"\nDone — {total} opportunities found.")
    print(f"  Reddit:        {len(reddit)}")
    print(f"  StackExchange: {len(stackexchange)}")
    print(f"  Hacker News:   {len(hackernews)}")
    print(f"  Manual links:  {len(manual_links)} platforms")
    print(f"\nReport: {report_path}")
    print(f"Latest: {latest_path}")


if __name__ == "__main__":
    main()
