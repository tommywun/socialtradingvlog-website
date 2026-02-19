#!/usr/bin/env python3
"""
SocialTradingVlog Newsletter System — Welcome emails + Newsletter sending via Resend API.

Usage:
    python3 tools/send_newsletter.py --welcome EMAIL         # send welcome email to one subscriber
    python3 tools/send_newsletter.py --newsletter SUBJECT     # send newsletter to all active subscribers
    python3 tools/send_newsletter.py --preview SUBJECT        # preview newsletter (dry run, send to Tom only)
    python3 tools/send_newsletter.py --stats                  # show subscriber stats
    python3 tools/send_newsletter.py --test                   # send test email to Tom

Newsletter content:
    Put your newsletter HTML in data/newsletter-draft.html on the VPS.
    The script wraps it in the email template automatically.
"""

import sys
import os
import json
import argparse
import pathlib
from datetime import datetime

# Add venv to path
VENV_SITE = pathlib.Path.home() / "socialtradingvlog-website" / "venv" / "lib"
for p in VENV_SITE.glob("python*/site-packages"):
    sys.path.insert(0, str(p))

import resend

# ─── Config ───
PROJECT_DIR = pathlib.Path(__file__).parent.parent
SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
SUBSCRIBERS_FILE = PROJECT_DIR / "data" / "subscribers.json"
NEWSLETTER_DRAFT = PROJECT_DIR / "data" / "newsletter-draft.html"
SEND_LOG = PROJECT_DIR / "data" / "send-log.json"

FROM_EMAIL = "Tom <tom@send.socialtradingvlog.com>"
TOM_EMAIL = "tradertommalta@gmail.com"
SITE_URL = "https://socialtradingvlog.com"
UNSUBSCRIBE_URL = "https://app.socialtradingvlog.com/api/unsubscribe"

# ─── Init Resend ───
def init_resend():
    key_file = SECRETS_DIR / "resend-api-key.txt"
    if not key_file.exists():
        print("ERROR: Resend API key not found at", key_file)
        sys.exit(1)
    resend.api_key = key_file.read_text().strip()


# ─── Subscriber Management ───
def load_subscribers():
    if SUBSCRIBERS_FILE.exists():
        return json.loads(SUBSCRIBERS_FILE.read_text())
    return []


def get_active_subscribers():
    return [s for s in load_subscribers() if not s.get("unsubscribed")]


# ─── Send Logging ───
def load_send_log():
    if SEND_LOG.exists():
        return json.loads(SEND_LOG.read_text())
    return []


def log_send(email, email_type, subject, success, error=None):
    log = load_send_log()
    log.append({
        "email": email,
        "type": email_type,
        "subject": subject,
        "success": success,
        "error": error,
        "sent_at": datetime.now().isoformat(),
    })
    SEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    SEND_LOG.write_text(json.dumps(log, indent=2))


# ─── Email Templates ───
def email_wrapper(content_html, email_for_unsubscribe=""):
    """Wrap content in the standard email template."""
    unsubscribe_link = f"{UNSUBSCRIBE_URL}?email={email_for_unsubscribe}" if email_for_unsubscribe else "#"
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ margin: 0; padding: 0; background: #0a0a0a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
  .container {{ max-width: 600px; margin: 0 auto; background: #1a1a2e; }}
  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 32px 24px; text-align: center; border-bottom: 2px solid #e94560; }}
  .header h1 {{ color: #ffffff; font-size: 22px; margin: 0; font-weight: 700; }}
  .header p {{ color: #a0a0b0; font-size: 14px; margin: 8px 0 0; }}
  .content {{ padding: 32px 24px; color: #e0e0e0; font-size: 16px; line-height: 1.7; }}
  .content h2 {{ color: #ffffff; font-size: 20px; margin: 24px 0 12px; }}
  .content h3 {{ color: #e94560; font-size: 17px; margin: 20px 0 8px; }}
  .content a {{ color: #e94560; text-decoration: none; }}
  .content a:hover {{ text-decoration: underline; }}
  .content p {{ margin: 0 0 16px; }}
  .content ul {{ padding-left: 20px; margin: 0 0 16px; }}
  .content li {{ margin: 0 0 8px; }}
  .cta-box {{ background: linear-gradient(135deg, #16213e, #1a1a2e); border: 1px solid #e94560; border-radius: 8px; padding: 20px; margin: 24px 0; text-align: center; }}
  .cta-box p {{ color: #a0a0b0; font-size: 14px; margin: 0 0 12px; }}
  .cta-btn {{ display: inline-block; background: #e94560; color: #ffffff !important; padding: 12px 28px; border-radius: 6px; font-weight: 600; font-size: 15px; text-decoration: none !important; }}
  .divider {{ border: none; border-top: 1px solid #2a2a4a; margin: 24px 0; }}
  .footer {{ padding: 24px; text-align: center; border-top: 1px solid #2a2a4a; }}
  .footer p {{ color: #666; font-size: 12px; margin: 0 0 8px; line-height: 1.5; }}
  .footer a {{ color: #888; }}
  .risk {{ background: #1e1e3a; border-left: 3px solid #e94560; padding: 12px 16px; margin: 20px 0; font-size: 12px; color: #888; line-height: 1.5; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Social Trading Vlog</h1>
    <p>Honest copy trading insights from 9 years on eToro</p>
  </div>
  <div class="content">
    {content_html}
  </div>
  <div class="footer">
    <p><a href="{SITE_URL}">socialtradingvlog.com</a></p>
    <p>You received this because you subscribed to the Social Trading Vlog newsletter.</p>
    <p><a href="{unsubscribe_link}">Unsubscribe</a></p>
  </div>
</div>
</body>
</html>"""


def welcome_email_html():
    """Generate welcome email content."""
    return """<h2>Welcome aboard! 👋</h2>

<p>I'm Tom, and I've been copy trading on eToro since 2017. Thanks for subscribing — I'm glad you're here.</p>

<p>Here's what you can expect from me:</p>

<ul>
  <li><strong>Weekly updates</strong> — honest portfolio numbers, what's working, what isn't</li>
  <li><strong>Practical tips</strong> — things I've learned the hard way so you don't have to</li>
  <li><strong>New guides</strong> — when I publish something useful, you'll be first to know</li>
</ul>

<p>No hype, no "guaranteed returns" nonsense. Just real numbers from a real account.</p>

<hr class="divider">

<h3>Your free checklist</h3>

<p>As promised, here's my <strong>Copy Trading Checklist — 10 Things I Check Before Copying a Trader</strong>. These are the exact things I look at before putting real money behind someone:</p>

<div class="cta-box">
  <p>Free download — no PDF, just a clean web page you can bookmark or print</p>
  <a href="https://socialtradingvlog.com/checklist/" class="cta-btn">Get the Checklist →</a>
</div>

<hr class="divider">

<h3>Start here</h3>

<p>If you're new to copy trading, these guides will save you a lot of time:</p>

<ul>
  <li><a href="https://socialtradingvlog.com/copy-trading/">What Is Copy Trading?</a> — the basics, explained simply</li>
  <li><a href="https://socialtradingvlog.com/copy-trading-returns/">Can You Actually Make Money?</a> — my real returns over 9 years</li>
  <li><a href="https://socialtradingvlog.com/best-traders-to-copy-etoro/">How to Find Good Traders to Copy</a> — what to look for (and avoid)</li>
  <li><a href="https://socialtradingvlog.com/etoro-review/">My Honest eToro Review</a> — the good, bad, and ugly after 9 years</li>
</ul>

<div class="risk">
  <strong>Risk warning:</strong> Copy trading is not financial advice. 51% of retail investor accounts lose money when trading CFDs with eToro. You should consider whether you can afford to take the high risk of losing your money. Past performance is not an indication of future results.
</div>

<p>Got questions? Just reply to this email — I read every one.</p>

<p>— Tom</p>"""


# ─── Send Functions ───
def send_email(to_email, subject, html_content, email_type="newsletter"):
    """Send a single email via Resend."""
    try:
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        # Add List-Unsubscribe header for newsletters
        if email_type == "newsletter":
            unsubscribe = f"{UNSUBSCRIBE_URL}?email={to_email}"
            params["headers"] = {
                "List-Unsubscribe": f"<{unsubscribe}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            }

        r = resend.Emails.send(params)
        log_send(to_email, email_type, subject, True)
        return True, r
    except Exception as e:
        log_send(to_email, email_type, subject, False, str(e))
        return False, str(e)


def send_welcome(email):
    """Send welcome email to a new subscriber."""
    content = welcome_email_html()
    html = email_wrapper(content, email)
    subject = "Welcome to Social Trading Vlog — here's your checklist"
    ok, result = send_email(email, subject, html, "welcome")
    if ok:
        print(f"  ✓ Welcome email sent to {email}")
    else:
        print(f"  ✗ Failed to send welcome to {email}: {result}")
    return ok


def send_newsletter(subject, preview_only=False):
    """Send newsletter to all active subscribers (or just Tom for preview)."""
    if not NEWSLETTER_DRAFT.exists():
        print(f"ERROR: Newsletter draft not found at {NEWSLETTER_DRAFT}")
        print("Create your newsletter content there first.")
        sys.exit(1)

    content = NEWSLETTER_DRAFT.read_text()
    subscribers = get_active_subscribers()

    if preview_only:
        print(f"\n  PREVIEW MODE — sending to {TOM_EMAIL} only\n")
        html = email_wrapper(content, TOM_EMAIL)
        ok, result = send_email(TOM_EMAIL, f"[PREVIEW] {subject}", html, "preview")
        if ok:
            print(f"  ✓ Preview sent to {TOM_EMAIL}")
        else:
            print(f"  ✗ Failed: {result}")
        return

    print(f"\n  Sending newsletter: \"{subject}\"")
    print(f"  Recipients: {len(subscribers)} active subscribers\n")

    # Confirm before sending
    if not preview_only:
        confirm = input(f"  Send to {len(subscribers)} subscribers? [y/N] ")
        if confirm.lower() != "y":
            print("  Cancelled.")
            return

    success = 0
    failed = 0
    for sub in subscribers:
        email = sub["email"]
        html = email_wrapper(content, email)
        ok, result = send_email(email, subject, html, "newsletter")
        if ok:
            success += 1
            print(f"  ✓ {email}")
        else:
            failed += 1
            print(f"  ✗ {email}: {result}")

    print(f"\n  Done: {success} sent, {failed} failed")


def show_stats():
    """Show subscriber and send stats."""
    subs = load_subscribers()
    active = [s for s in subs if not s.get("unsubscribed")]
    unsub = [s for s in subs if s.get("unsubscribed")]

    print(f"\n  Subscribers: {len(active)} active, {len(unsub)} unsubscribed ({len(subs)} total)")

    if active:
        print(f"\n  Active subscribers:")
        for s in active:
            print(f"    {s['email']} (from {s.get('source', 'unknown')}, {s['subscribed_at'][:10]})")

    log = load_send_log()
    if log:
        print(f"\n  Send history: {len(log)} emails sent")
        # Show last 10
        for entry in log[-10:]:
            status = "✓" if entry["success"] else "✗"
            print(f"    {status} {entry['sent_at'][:16]} → {entry['email']} ({entry['type']}: {entry['subject'][:40]})")


def send_test():
    """Send a test email to Tom."""
    content = "<h2>Test email</h2><p>If you're reading this, Resend is working! 🎉</p><p>— Your newsletter system</p>"
    html = email_wrapper(content, TOM_EMAIL)
    ok, result = send_email(TOM_EMAIL, "STV Newsletter System — Test", html, "test")
    if ok:
        print(f"  ✓ Test email sent to {TOM_EMAIL}")
    else:
        print(f"  ✗ Failed: {result}")


# ─── Main ───
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="STV Newsletter System")
    parser.add_argument("--welcome", metavar="EMAIL", help="Send welcome email to a subscriber")
    parser.add_argument("--newsletter", metavar="SUBJECT", help="Send newsletter to all subscribers")
    parser.add_argument("--preview", metavar="SUBJECT", help="Preview newsletter (send to Tom only)")
    parser.add_argument("--stats", action="store_true", help="Show subscriber stats")
    parser.add_argument("--test", action="store_true", help="Send test email to Tom")
    args = parser.parse_args()

    init_resend()

    if args.welcome:
        send_welcome(args.welcome)
    elif args.newsletter:
        send_newsletter(args.newsletter)
    elif args.preview:
        send_newsletter(args.preview, preview_only=True)
    elif args.stats:
        show_stats()
    elif args.test:
        send_test()
    else:
        parser.print_help()
