#!/usr/bin/env python3
"""
Content Syndicator — Cross-post articles to dev.to, Hashnode, Blogger, Tumblr.

Rations articles across platforms slowly (1 per platform per day) so the
~35 English articles + translated variants last for weeks. Each post includes
a canonical URL pointing back to the original and is signed as STV Team Assistant.

Platforms:
  - dev.to:    REST API (API key)
  - Hashnode:  GraphQL API (Personal Access Token)
  - Blogger:   Google Blogger API v3 (OAuth)
  - Tumblr:    REST API v2 (OAuth)

Usage:
    python3 tools/content_syndicator.py              # Syndicate next batch
    python3 tools/content_syndicator.py --dry-run     # Preview without posting
    python3 tools/content_syndicator.py --platform devto  # Specific platform only
    python3 tools/content_syndicator.py --list        # Show syndication queue

Cron:
    0 7 * * *  python3 tools/content_syndicator.py
"""

import sys
import os
import re
import json
import pathlib
import argparse
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from html.parser import HTMLParser

PROJECT_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
SYNDICATION_LOG = DATA_DIR / "syndication-log.json"
SITE_URL = "https://socialtradingvlog.com"

SSL_CTX = ssl.create_default_context()

# Max articles to post per platform per run (ration the content)
MAX_PER_PLATFORM_PER_RUN = 1

FOOTER_TEMPLATE = """

---

*Originally published on [socialtradingvlog.com]({url}). Posted by STV Team Assistant.*
"""

# ─── Article extraction ──────────────────────────────────────────────────────


class ArticleExtractor(HTMLParser):
    """Extract article content, title, and metadata from HTML."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.og_image = ""
        self._in_title = False
        self._title_parts = []
        self._in_article = False
        self._article_parts = []
        self._current_tag = None
        self._skip_tags = {"script", "style", "nav", "header", "footer", "noscript"}
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "title":
            self._in_title = True
            self._title_parts = []
        elif tag == "meta":
            name = d.get("name", "").lower()
            prop = d.get("property", "").lower()
            content = d.get("content", "")
            if name == "description":
                self.description = content
            elif prop == "og:image":
                self.og_image = content
        elif tag == "link" and d.get("rel") == "canonical":
            self.canonical = d.get("href", "")
        elif tag == "article":
            self._in_article = True
        elif tag in self._skip_tags:
            self._skip_depth += 1

        if self._in_article and self._skip_depth == 0:
            self._current_tag = tag
            if tag in ("h2", "h3"):
                self._article_parts.append(f"\n\n{'##' if tag == 'h2' else '###'} ")
            elif tag == "p":
                self._article_parts.append("\n\n")
            elif tag == "li":
                self._article_parts.append("\n- ")
            elif tag == "br":
                self._article_parts.append("\n")
            elif tag == "strong" or tag == "b":
                self._article_parts.append("**")
            elif tag == "em" or tag == "i":
                self._article_parts.append("*")
            elif tag == "a":
                href = d.get("href", "")
                self._article_parts.append(f"[")
                self._current_href = href

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)
        if self._in_article and self._skip_depth == 0:
            self._article_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.title = "".join(self._title_parts).strip()
        elif tag == "article":
            self._in_article = False
        elif tag in self._skip_tags:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif self._in_article and self._skip_depth == 0:
            if tag == "strong" or tag == "b":
                self._article_parts.append("**")
            elif tag == "em" or tag == "i":
                self._article_parts.append("*")
            elif tag == "a":
                href = getattr(self, "_current_href", "")
                self._article_parts.append(f"]({href})")

    def get_markdown(self):
        text = "".join(self._article_parts)
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


def get_syndicatable_articles():
    """Get all articles eligible for syndication, with metadata."""
    articles = []

    # Language configs: (subdir, lang_code)
    lang_dirs = [
        ("", "en"),
        ("es", "es"), ("de", "de"), ("fr", "fr"), ("pt", "pt"), ("ar", "ar"),
    ]

    skip_dirs = {
        "contact", "contact-thanks", "privacy", "faq", "videos", "about",
        "calculators", "author", "tag", "articles", "updates",
        "kontakt", "haeufig-gestellte-fragen", "ueber-uns", "rechner",
        "contacto", "preguntas-frecuentes", "sobre-nosotros", "calculadoras",
        "foire-aux-questions", "questions-frequentes", "a-propos", "calculateurs",
        "contato", "perguntas-frequentes", "sobre",
        "al-asilah-al-shaaiah", "an-al-mawqi", "an-na", "ittisal", "atisal-bina",
    }

    skip_root = {"404.html", "contact.html", "contact-thanks.html", "privacy.html",
                 "faq.html", "videos.html", "index.html", "about.html", "updates.html"}

    for subdir, lang in lang_dirs:
        base = PROJECT_DIR / subdir if subdir else PROJECT_DIR

        html_files = []
        if lang == "en":
            for f in base.glob("*.html"):
                html_files.append(f)
            for f in base.glob("*/index.html"):
                html_files.append(f)
        else:
            for f in base.glob("*/index.html"):
                html_files.append(f)

        for filepath in html_files:
            parent_dir = filepath.parent.name
            if parent_dir in skip_dirs:
                continue
            if lang == "en" and filepath.name in skip_root:
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
            except Exception:
                continue

            parser = ArticleExtractor()
            try:
                parser.feed(content)
            except Exception:
                continue

            title = parser.title
            if not title:
                continue

            # Clean title
            title = re.sub(r'\s*\|\s*SocialTradingVlog\s*$', '', title)

            canonical = parser.canonical
            if not canonical:
                rel_path = filepath.relative_to(PROJECT_DIR)
                canonical = f"{SITE_URL}/{rel_path}".replace("/index.html", "/")

            markdown = parser.get_markdown()
            if len(markdown) < 200:
                continue  # Skip very short pages

            # Truncate to ~500 words for syndication summary
            words = markdown.split()
            if len(words) > 500:
                markdown = " ".join(words[:500]) + "\n\n*[Read the full article...](" + canonical + ")*"

            articles.append({
                "title": title,
                "description": parser.description,
                "url": canonical,
                "og_image": parser.og_image,
                "language": lang,
                "markdown": markdown + FOOTER_TEMPLATE.format(url=canonical),
                "filepath": str(filepath.relative_to(PROJECT_DIR)),
            })

    return articles


# ─── Syndication log ─────────────────────────────────────────────────────────


def load_log():
    if SYNDICATION_LOG.exists():
        try:
            return json.loads(SYNDICATION_LOG.read_text())
        except Exception:
            return {}
    return {}


def save_log(log):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SYNDICATION_LOG.write_text(json.dumps(log, indent=2))


def is_already_posted(log, platform, url):
    key = f"{platform}:{url}"
    return key in log


def mark_posted(log, platform, url, post_url=""):
    key = f"{platform}:{url}"
    log[key] = {
        "posted_at": datetime.now().isoformat(),
        "post_url": post_url,
    }


# ─── Platform APIs ───────────────────────────────────────────────────────────


def post_to_devto(article, dry_run=False):
    """Post article to dev.to via REST API."""
    key_file = SECRETS_DIR / "devto-api-key.txt"
    if not key_file.exists():
        print(f"    [dev.to] API key not found at {key_file}")
        return None

    api_key = key_file.read_text().strip()

    payload = json.dumps({
        "article": {
            "title": article["title"],
            "body_markdown": article["markdown"],
            "published": True,
            "canonical_url": article["url"],
            "tags": ["trading", "finance", "investing", "etoro"],
        }
    }).encode()

    if dry_run:
        print(f"    [dev.to] Would post: {article['title']}")
        return "dry-run"

    try:
        req = urllib.request.Request(
            "https://dev.to/api/articles",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "api-key": api_key,
            },
        )
        resp = urllib.request.urlopen(req, timeout=30, context=SSL_CTX)
        data = json.loads(resp.read().decode())
        post_url = data.get("url", "")
        print(f"    [dev.to] Posted: {post_url}")
        return post_url
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"    [dev.to] Error {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"    [dev.to] Error: {e}")
        return None


def post_to_hashnode(article, dry_run=False):
    """Post article to Hashnode via GraphQL API."""
    pat_file = SECRETS_DIR / "hashnode-pat.txt"
    pub_file = SECRETS_DIR / "hashnode-publication-id.txt"
    if not pat_file.exists():
        print(f"    [hashnode] PAT not found at {pat_file}")
        return None

    pat = pat_file.read_text().strip()
    pub_id = pub_file.read_text().strip() if pub_file.exists() else None

    # Build GraphQL mutation
    if pub_id:
        query = """
        mutation PublishPost($input: PublishPostInput!) {
            publishPost(input: $input) {
                post { url }
            }
        }
        """
        variables = {
            "input": {
                "title": article["title"],
                "contentMarkdown": article["markdown"],
                "publicationId": pub_id,
                "originalArticleURL": article["url"],
                "tags": [{"name": "Trading"}, {"name": "Finance"}],
            }
        }
    else:
        print(f"    [hashnode] No publication ID found at {pub_file}")
        return None

    payload = json.dumps({"query": query, "variables": variables}).encode()

    if dry_run:
        print(f"    [hashnode] Would post: {article['title']}")
        return "dry-run"

    try:
        req = urllib.request.Request(
            "https://gql.hashnode.com/",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": pat,
            },
        )
        resp = urllib.request.urlopen(req, timeout=30, context=SSL_CTX)
        data = json.loads(resp.read().decode())
        post_url = data.get("data", {}).get("publishPost", {}).get("post", {}).get("url", "")
        if post_url:
            print(f"    [hashnode] Posted: {post_url}")
        else:
            errors = data.get("errors", [])
            print(f"    [hashnode] Response: {json.dumps(errors)[:200]}")
        return post_url or None
    except Exception as e:
        print(f"    [hashnode] Error: {e}")
        return None


def post_to_blogger(article, dry_run=False):
    """Post article to Blogger via Google Blogger API v3."""
    token_file = SECRETS_DIR / "google-blogger-token.pickle"
    blog_id_file = SECRETS_DIR / "blogger-blog-id.txt"
    if not token_file.exists():
        print(f"    [blogger] OAuth token not found at {token_file}")
        return None
    if not blog_id_file.exists():
        print(f"    [blogger] Blog ID not found at {blog_id_file}")
        return None

    blog_id = blog_id_file.read_text().strip()

    try:
        import pickle
        from google.auth.transport.requests import Request

        with open(token_file, "rb") as f:
            creds = pickle.load(f)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)

        access_token = creds.token
    except Exception as e:
        print(f"    [blogger] Auth error: {e}")
        return None

    # Convert markdown to basic HTML for Blogger
    html_content = markdown_to_basic_html(article["markdown"])

    payload = json.dumps({
        "kind": "blogger#post",
        "title": article["title"],
        "content": html_content,
    }).encode()

    if dry_run:
        print(f"    [blogger] Would post: {article['title']}")
        return "dry-run"

    try:
        req = urllib.request.Request(
            f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )
        resp = urllib.request.urlopen(req, timeout=30, context=SSL_CTX)
        data = json.loads(resp.read().decode())
        post_url = data.get("url", "")
        print(f"    [blogger] Posted: {post_url}")
        return post_url
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"    [blogger] Error {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"    [blogger] Error: {e}")
        return None


def post_to_tumblr(article, dry_run=False):
    """Post article to Tumblr via REST API v2."""
    creds_file = SECRETS_DIR / "tumblr-credentials.json"
    if not creds_file.exists():
        print(f"    [tumblr] Credentials not found at {creds_file}")
        return None

    try:
        creds = json.loads(creds_file.read_text())
        blog_name = creds["blog_name"]
        oauth_token = creds["oauth_token"]
    except Exception as e:
        print(f"    [tumblr] Credentials error: {e}")
        return None

    payload = json.dumps({
        "type": "text",
        "title": article["title"],
        "body": markdown_to_basic_html(article["markdown"]),
        "tags": "trading,finance,investing,etoro,copy trading",
        "source_url": article["url"],
    }).encode()

    if dry_run:
        print(f"    [tumblr] Would post: {article['title']}")
        return "dry-run"

    try:
        req = urllib.request.Request(
            f"https://api.tumblr.com/v2/blog/{blog_name}/post",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {oauth_token}",
            },
        )
        resp = urllib.request.urlopen(req, timeout=30, context=SSL_CTX)
        data = json.loads(resp.read().decode())
        post_id = data.get("response", {}).get("id", "")
        post_url = f"https://{blog_name}.tumblr.com/post/{post_id}" if post_id else ""
        print(f"    [tumblr] Posted: {post_url}")
        return post_url
    except Exception as e:
        print(f"    [tumblr] Error: {e}")
        return None


def markdown_to_basic_html(md):
    """Very basic markdown → HTML for platforms that need HTML."""
    html = md
    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    # Bold/italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    # List items
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # Paragraphs (double newlines)
    parts = html.split('\n\n')
    result = []
    for part in parts:
        part = part.strip()
        if part and not part.startswith('<h') and not part.startswith('<li'):
            part = f'<p>{part}</p>'
        result.append(part)
    html = '\n'.join(result)
    return html


# ─── Main ────────────────────────────────────────────────────────────────────


PLATFORMS = {
    "devto": post_to_devto,
    "hashnode": post_to_hashnode,
    "blogger": post_to_blogger,
    "tumblr": post_to_tumblr,
}


def main():
    parser = argparse.ArgumentParser(description="Content Syndicator")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--platform", choices=list(PLATFORMS.keys()),
                        help="Post to specific platform only")
    parser.add_argument("--list", action="store_true", help="Show syndication queue")
    parser.add_argument("--lang", type=str, default=None,
                        help="Limit to specific language (en, es, de, fr, pt, ar)")
    args = parser.parse_args()

    articles = get_syndicatable_articles()
    if args.lang:
        articles = [a for a in articles if a["language"] == args.lang]

    log = load_log()

    platforms = {args.platform: PLATFORMS[args.platform]} if args.platform else PLATFORMS

    print(f"Content Syndicator — {datetime.now().isoformat()}")
    print(f"Total syndicatable articles: {len(articles)}")
    print(f"Platforms: {', '.join(platforms.keys())}")

    if args.list:
        for platform_name in platforms:
            pending = [a for a in articles if not is_already_posted(log, platform_name, a["url"])]
            print(f"\n[{platform_name}] {len(pending)} articles pending:")
            for a in pending[:10]:
                print(f"  [{a['language']}] {a['title']}")
            if len(pending) > 10:
                print(f"  ... and {len(pending) - 10} more")
        return

    total_posted = 0
    for platform_name, post_fn in platforms.items():
        # Find articles not yet posted to this platform
        pending = [a for a in articles if not is_already_posted(log, platform_name, a["url"])]
        if not pending:
            print(f"\n[{platform_name}] All articles already syndicated")
            continue

        print(f"\n[{platform_name}] {len(pending)} articles pending, posting up to {MAX_PER_PLATFORM_PER_RUN}")

        posted = 0
        for article in pending:
            if posted >= MAX_PER_PLATFORM_PER_RUN:
                break

            print(f"  [{article['language']}] {article['title']}")
            result = post_fn(article, dry_run=args.dry_run)
            if result:
                if not args.dry_run:
                    mark_posted(log, platform_name, article["url"], result)
                posted += 1
                total_posted += 1

    if not args.dry_run and total_posted > 0:
        save_log(log)

    print(f"\nDone: posted {total_posted} articles")

    # Send Telegram summary
    if total_posted > 0 and not args.dry_run:
        try:
            sys.path.insert(0, str(pathlib.Path(__file__).parent))
            from security_lib import send_telegram
            send_telegram(
                f"Content Syndicator: {total_posted} articles posted",
                f"Posted {total_posted} articles across platforms.\nCheck logs/syndication.log for details.",
                emoji="📝",
                dedupe_key="syndication",
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
