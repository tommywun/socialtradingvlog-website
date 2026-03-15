#!/usr/bin/env python3
"""
Social Media Poster — Automated posting to Pinterest, X, Mastodon, Bluesky,
Facebook, Threads, and Telegram.

Rations articles across platforms (1-2 per platform per slot). Posts in the
language of the article with language-appropriate hashtags.

All accounts must be clearly identified as automated STV Team Assistant feeds.

Usage:
    python3 tools/social_poster.py                    # Post to all platforms
    python3 tools/social_poster.py --slot morning     # Morning slot only
    python3 tools/social_poster.py --platform pinterest  # Specific platform
    python3 tools/social_poster.py --dry-run          # Preview without posting
    python3 tools/social_poster.py --list             # Show post queue

Cron:
    0 8 * * *   python3 tools/social_poster.py --slot morning
    0 13 * * *  python3 tools/social_poster.py --slot afternoon
    0 18 * * *  python3 tools/social_poster.py --slot evening
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
BACKUP_PASSPHRASE = SECRETS_DIR / "backup-passphrase.txt"


def load_secret(name):
    """Load a secret, decrypting GPG-encrypted files if needed."""
    gpg_file = SECRETS_DIR / f"{name}.gpg"
    plain_file = SECRETS_DIR / name
    if gpg_file.exists() and BACKUP_PASSPHRASE.exists():
        import subprocess
        result = subprocess.run(
            ["gpg", "--batch", "--yes", "--passphrase-file", str(BACKUP_PASSPHRASE),
             "--decrypt", str(gpg_file)],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    if plain_file.exists():
        return plain_file.read_text().strip()
    return None
POST_LOG = DATA_DIR / "social-post-log.json"
SITE_URL = "https://socialtradingvlog.com"

SSL_CTX = ssl.create_default_context()

# Max posts per platform per run
MAX_PER_PLATFORM = 1

# Hashtags per language
HASHTAGS = {
    "en": ["#CopyTrading", "#eToro", "#Investing", "#Trading"],
    "es": ["#CopyTrading", "#eToro", "#Inversión", "#Trading"],
    "de": ["#CopyTrading", "#eToro", "#Geldanlage", "#Trading"],
    "fr": ["#CopyTrading", "#eToro", "#Investissement", "#Trading"],
    "pt": ["#CopyTrading", "#eToro", "#Investimento", "#Trading"],
    "ar": ["#CopyTrading", "#eToro", "#تداول", "#استثمار"],
}


class MetaExtractor(HTMLParser):
    """Extract title, description, OG image from HTML."""
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.og_image = ""
        self._in_title = False
        self._title_parts = []

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

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.title = "".join(self._title_parts).strip()


def get_articles():
    """Get all articles for social posting."""
    articles = []
    lang_dirs = [("", "en"), ("es", "es"), ("de", "de"), ("fr", "fr"), ("pt", "pt"), ("ar", "ar")]

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
            if filepath.parent.name in skip_dirs:
                continue
            if lang == "en" and filepath.name in skip_root:
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
            except Exception:
                continue

            parser = MetaExtractor()
            try:
                parser.feed(content)
            except Exception:
                continue

            title = parser.title
            if not title:
                continue
            title = re.sub(r'\s*\|\s*SocialTradingVlog\s*$', '', title)

            canonical = parser.canonical
            if not canonical:
                rel_path = filepath.relative_to(PROJECT_DIR)
                canonical = f"{SITE_URL}/{rel_path}".replace("/index.html", "/")

            articles.append({
                "title": title,
                "description": parser.description or title,
                "url": canonical,
                "og_image": parser.og_image,
                "language": lang,
            })

    return articles


def load_log():
    if POST_LOG.exists():
        try:
            return json.loads(POST_LOG.read_text())
        except Exception:
            return {}
    return {}


def save_log(log):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    POST_LOG.write_text(json.dumps(log, indent=2))


def is_posted(log, platform, url):
    return f"{platform}:{url}" in log


def mark_posted(log, platform, url, post_url=""):
    log[f"{platform}:{url}"] = {
        "posted_at": datetime.now().isoformat(),
        "post_url": post_url,
    }


def make_post_text(article, max_length=280, hashtag_count=2):
    """Generate platform-appropriate post text."""
    lang = article["language"]
    tags = HASHTAGS.get(lang, HASHTAGS["en"])[:hashtag_count]
    tag_str = " ".join(tags)

    desc = article["description"]
    url = article["url"]
    suffix = f"\n\n{url}\n\n{tag_str}"
    max_desc = max_length - len(suffix) - 5
    if len(desc) > max_desc:
        desc = desc[:max_desc - 3] + "..."

    return f"{desc}{suffix}"


# ─── Platform implementations ────────────────────────────────────────────────


def post_to_pinterest(article, dry_run=False):
    """Create a Pin via Pinterest API v5."""
    creds_raw = load_secret("pinterest-credentials.json")
    if not creds_raw:
        print(f"    [pinterest] Credentials not found")
        return None

    creds = json.loads(creds_raw)
    access_token = creds.get("access_token", "")
    board_id = creds.get("board_id", "")

    if not access_token or not board_id:
        print(f"    [pinterest] Missing access_token or board_id")
        return None

    image_url = article.get("og_image") or f"{SITE_URL}/images/og-default.png"

    payload = json.dumps({
        "board_id": board_id,
        "title": article["title"][:100],
        "description": article["description"][:500],
        "link": article["url"],
        "media_source": {
            "source_type": "image_url",
            "url": image_url,
        },
    }).encode()

    if dry_run:
        print(f"    [pinterest] Would pin: {article['title']}")
        return "dry-run"

    try:
        req = urllib.request.Request(
            "https://api.pinterest.com/v5/pins",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )
        resp = urllib.request.urlopen(req, timeout=30, context=SSL_CTX)
        data = json.loads(resp.read().decode())
        pin_id = data.get("id", "")
        print(f"    [pinterest] Pinned: {pin_id}")
        return f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else None
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"    [pinterest] Error {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"    [pinterest] Error: {e}")
        return None


def post_to_twitter(article, dry_run=False):
    """Post to X/Twitter via API v2 (free tier)."""
    creds_raw = load_secret("twitter-credentials.json")
    if not creds_raw:
        print(f"    [twitter] Credentials not found")
        return None

    creds = json.loads(creds_raw)
    bearer_token = creds.get("bearer_token", "")
    # For posting, need OAuth 1.0a user context
    api_key = creds.get("api_key", "")
    api_secret = creds.get("api_secret", "")
    access_token = creds.get("access_token", "")
    access_secret = creds.get("access_token_secret", "")

    if not all([api_key, api_secret, access_token, access_secret]):
        print(f"    [twitter] Missing OAuth credentials")
        return None

    text = make_post_text(article, max_length=280, hashtag_count=2)

    if dry_run:
        print(f"    [twitter] Would tweet: {text[:80]}...")
        return "dry-run"

    # OAuth 1.0a signing
    try:
        import hmac
        import hashlib
        import base64
        import time
        import uuid

        url = "https://api.twitter.com/2/tweets"
        method = "POST"
        oauth_nonce = uuid.uuid4().hex
        oauth_timestamp = str(int(time.time()))

        oauth_params = {
            "oauth_consumer_key": api_key,
            "oauth_nonce": oauth_nonce,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": oauth_timestamp,
            "oauth_token": access_token,
            "oauth_version": "1.0",
        }

        # Create signature base string
        params_str = "&".join(f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
                              for k, v in sorted(oauth_params.items()))
        base_str = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(params_str, safe='')}"
        signing_key = f"{urllib.parse.quote(api_secret, safe='')}&{urllib.parse.quote(access_secret, safe='')}"
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_str.encode(), hashlib.sha1).digest()
        ).decode()
        oauth_params["oauth_signature"] = signature

        auth_header = "OAuth " + ", ".join(
            f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
            for k, v in sorted(oauth_params.items())
        )

        payload = json.dumps({"text": text}).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": auth_header,
            },
        )
        resp = urllib.request.urlopen(req, timeout=30, context=SSL_CTX)
        data = json.loads(resp.read().decode())
        tweet_id = data.get("data", {}).get("id", "")
        print(f"    [twitter] Tweeted: {tweet_id}")
        return f"https://x.com/i/status/{tweet_id}" if tweet_id else None
    except Exception as e:
        print(f"    [twitter] Error: {e}")
        return None


def post_to_mastodon(article, dry_run=False):
    """Post to Mastodon via REST API."""
    token = load_secret("mastodon-token.txt")
    if not token:
        print(f"    [mastodon] Token not found")
        return None

    instance = load_secret("mastodon-instance.txt") or "mastodon.social"

    text = make_post_text(article, max_length=500, hashtag_count=3)

    if dry_run:
        print(f"    [mastodon] Would toot: {text[:80]}...")
        return "dry-run"

    try:
        payload = urllib.parse.urlencode({"status": text}).encode()
        req = urllib.request.Request(
            f"https://{instance}/api/v1/statuses",
            data=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = urllib.request.urlopen(req, timeout=30, context=SSL_CTX)
        data = json.loads(resp.read().decode())
        post_url = data.get("url", "")
        print(f"    [mastodon] Posted: {post_url}")
        return post_url
    except Exception as e:
        print(f"    [mastodon] Error: {e}")
        return None


def post_to_bluesky(article, dry_run=False):
    """Post to Bluesky via AT Protocol."""
    creds_raw = load_secret("bluesky-credentials.json")
    if not creds_raw:
        print(f"    [bluesky] Credentials not found")
        return None

    creds = json.loads(creds_raw)
    handle = creds.get("handle", "")
    app_password = creds.get("app_password", "")

    if not handle or not app_password:
        print(f"    [bluesky] Missing handle or app_password")
        return None

    text = make_post_text(article, max_length=300, hashtag_count=2)

    if dry_run:
        print(f"    [bluesky] Would post: {text[:80]}...")
        return "dry-run"

    try:
        # Create session
        auth_payload = json.dumps({"identifier": handle, "password": app_password}).encode()
        auth_req = urllib.request.Request(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            data=auth_payload,
            headers={"Content-Type": "application/json"},
        )
        auth_resp = urllib.request.urlopen(auth_req, timeout=15, context=SSL_CTX)
        auth_data = json.loads(auth_resp.read().decode())
        access_jwt = auth_data.get("accessJwt", "")
        did = auth_data.get("did", "")

        # Create post with link card
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        # Find URL position in text for facet
        url = article["url"]
        url_start = text.find(url)
        url_end = url_start + len(url) if url_start >= 0 else 0

        facets = []
        if url_start >= 0:
            facets.append({
                "index": {
                    "byteStart": len(text[:url_start].encode("utf-8")),
                    "byteEnd": len(text[:url_end].encode("utf-8")),
                },
                "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}],
            })

        post_payload = json.dumps({
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": text,
                "createdAt": now,
                "facets": facets,
            },
        }).encode()

        post_req = urllib.request.Request(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            data=post_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_jwt}",
            },
        )
        post_resp = urllib.request.urlopen(post_req, timeout=15, context=SSL_CTX)
        post_data = json.loads(post_resp.read().decode())
        uri = post_data.get("uri", "")
        print(f"    [bluesky] Posted: {uri}")
        return uri
    except Exception as e:
        print(f"    [bluesky] Error: {e}")
        return None


def post_to_facebook(article, dry_run=False):
    """Post to Facebook Page via Graph API."""
    token = load_secret("facebook-page-token.txt")
    if not token:
        print(f"    [facebook] Page token not found")
        return None

    page_id = load_secret("facebook-page-id.txt") or "me"

    text = make_post_text(article, max_length=500, hashtag_count=3)

    if dry_run:
        print(f"    [facebook] Would post: {text[:80]}...")
        return "dry-run"

    try:
        payload = urllib.parse.urlencode({
            "message": text,
            "link": article["url"],
            "access_token": token,
        }).encode()
        req = urllib.request.Request(
            f"https://graph.facebook.com/v19.0/{page_id}/feed",
            data=payload,
        )
        resp = urllib.request.urlopen(req, timeout=30, context=SSL_CTX)
        data = json.loads(resp.read().decode())
        post_id = data.get("id", "")
        print(f"    [facebook] Posted: {post_id}")
        return f"https://www.facebook.com/{post_id}" if post_id else None
    except Exception as e:
        print(f"    [facebook] Error: {e}")
        return None


def post_to_threads(article, dry_run=False):
    """Post to Threads via Meta Threads API."""
    token = load_secret("threads-token.txt")
    if not token:
        print(f"    [threads] Token not found")
        return None

    user_id = load_secret("threads-user-id.txt") or "me"

    # Threads: 500 chars, 1 hashtag
    lang = article["language"]
    tag = HASHTAGS.get(lang, HASHTAGS["en"])[0]
    desc = article["description"][:300]
    text = f"{desc}\n\n{article['url']}\n\n{tag}"

    if dry_run:
        print(f"    [threads] Would post: {text[:80]}...")
        return "dry-run"

    try:
        # Step 1: Create media container
        create_payload = urllib.parse.urlencode({
            "media_type": "TEXT",
            "text": text,
            "access_token": token,
        }).encode()
        create_req = urllib.request.Request(
            f"https://graph.threads.net/v1.0/{user_id}/threads",
            data=create_payload,
        )
        create_resp = urllib.request.urlopen(create_req, timeout=30, context=SSL_CTX)
        create_data = json.loads(create_resp.read().decode())
        container_id = create_data.get("id", "")

        if not container_id:
            print(f"    [threads] No container ID returned")
            return None

        # Step 2: Publish
        publish_payload = urllib.parse.urlencode({
            "creation_id": container_id,
            "access_token": token,
        }).encode()
        pub_req = urllib.request.Request(
            f"https://graph.threads.net/v1.0/{user_id}/threads_publish",
            data=publish_payload,
        )
        pub_resp = urllib.request.urlopen(pub_req, timeout=30, context=SSL_CTX)
        pub_data = json.loads(pub_resp.read().decode())
        post_id = pub_data.get("id", "")
        print(f"    [threads] Posted: {post_id}")
        return post_id
    except Exception as e:
        print(f"    [threads] Error: {e}")
        return None


def post_to_telegram(article, dry_run=False):
    """Post to Telegram public channel via Bot API."""
    bot_token = load_secret("telegram-bot-token.txt")
    if not bot_token:
        print(f"    [telegram] Bot token not found")
        return None

    channel_id = load_secret("telegram-channel-id.txt") or ""

    if not channel_id:
        print(f"    [telegram] Channel ID not found")
        return None

    lang = article["language"]
    tags = " ".join(HASHTAGS.get(lang, HASHTAGS["en"])[:3])
    text = f"<b>{article['title']}</b>\n\n{article['description'][:300]}\n\n<a href=\"{article['url']}\">Read more</a>\n\n{tags}"

    if dry_run:
        print(f"    [telegram] Would post: {article['title']}")
        return "dry-run"

    try:
        payload = urllib.parse.urlencode({
            "chat_id": channel_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "false",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
        )
        resp = urllib.request.urlopen(req, timeout=15, context=SSL_CTX)
        data = json.loads(resp.read().decode())
        msg_id = data.get("result", {}).get("message_id", "")
        print(f"    [telegram] Sent message: {msg_id}")
        return str(msg_id)
    except Exception as e:
        print(f"    [telegram] Error: {e}")
        return None


# ─── Main ────────────────────────────────────────────────────────────────────

PLATFORMS = {
    "pinterest": post_to_pinterest,
    "twitter": post_to_twitter,
    "mastodon": post_to_mastodon,
    "bluesky": post_to_bluesky,
    "facebook": post_to_facebook,
    "threads": post_to_threads,
    "telegram": post_to_telegram,
}


def main():
    parser = argparse.ArgumentParser(description="Social Media Poster")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--platform", choices=list(PLATFORMS.keys()))
    parser.add_argument("--slot", choices=["morning", "afternoon", "evening"],
                        help="Time slot (determines which platforms post)")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--lang", type=str, default=None)
    args = parser.parse_args()

    articles = get_articles()
    if args.lang:
        articles = [a for a in articles if a["language"] == args.lang]

    log = load_log()

    # Determine which platforms to use
    if args.platform:
        platforms = {args.platform: PLATFORMS[args.platform]}
    elif args.slot == "morning":
        platforms = {k: v for k, v in PLATFORMS.items() if k in ("pinterest", "twitter", "mastodon")}
    elif args.slot == "afternoon":
        platforms = {k: v for k, v in PLATFORMS.items() if k in ("bluesky", "facebook", "telegram")}
    elif args.slot == "evening":
        platforms = {k: v for k, v in PLATFORMS.items() if k in ("threads",)}
    else:
        platforms = PLATFORMS

    print(f"Social Poster — {datetime.now().isoformat()}")
    print(f"Articles: {len(articles)} | Platforms: {', '.join(platforms.keys())}")

    if args.list:
        for name in platforms:
            pending = [a for a in articles if not is_posted(log, name, a["url"])]
            print(f"\n[{name}] {len(pending)} pending")
            for a in pending[:5]:
                print(f"  [{a['language']}] {a['title']}")
            if len(pending) > 5:
                print(f"  ... and {len(pending) - 5} more")
        return

    total = 0
    for name, fn in platforms.items():
        pending = [a for a in articles if not is_posted(log, name, a["url"])]
        if not pending:
            print(f"\n[{name}] All articles already posted")
            continue

        print(f"\n[{name}] {len(pending)} pending, posting {MAX_PER_PLATFORM}")
        posted = 0
        for article in pending:
            if posted >= MAX_PER_PLATFORM:
                break
            print(f"  [{article['language']}] {article['title']}")
            result = fn(article, dry_run=args.dry_run)
            if result:
                if not args.dry_run:
                    mark_posted(log, name, article["url"], result)
                posted += 1
                total += 1

    if not args.dry_run and total > 0:
        save_log(log)

    print(f"\nDone: posted {total} items")

    if total > 0 and not args.dry_run:
        try:
            sys.path.insert(0, str(pathlib.Path(__file__).parent))
            from security_lib import send_telegram
            send_telegram(
                f"Social Poster: {total} posts",
                f"Posted {total} items to social platforms.",
                emoji="📢",
                dedupe_key="social-poster",
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
