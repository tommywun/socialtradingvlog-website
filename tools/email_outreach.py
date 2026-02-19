#!/usr/bin/env python3
"""
Email outreach tool for SocialTradingVlog.

Sends emails from tom@socialtradingvlog.com via Resend API.
Reads/monitors inbox via Gmail API (socialtradingvlog@gmail.com).
Manages draft emails for guest post pitches, outreach, etc.

Usage:
    python3 tools/email_outreach.py --send draft-name        # review + send a draft
    python3 tools/email_outreach.py --send-direct             # compose and send interactively
    python3 tools/email_outreach.py --inbox                   # check inbox for replies
    python3 tools/email_outreach.py --inbox --unread          # unread only
    python3 tools/email_outreach.py --list-drafts             # list available drafts
    python3 tools/email_outreach.py --status                  # show outreach tracking status
    python3 tools/email_outreach.py --check-followups         # check for emails needing follow-up
    python3 tools/email_outreach.py --send-followups          # send pending follow-up emails
    python3 tools/email_outreach.py --scan-journalist-queries # scan inbox for HARO/journalist queries
"""

import sys
import os
import json
import pathlib
import argparse
import pickle
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import base64
import re

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
RESEND_KEY_FILE = SECRETS_DIR / "resend-api-key.txt"
GMAIL_CLIENT_SECRET = SECRETS_DIR / "gmail-oauth.json"
GMAIL_TOKEN_FILE = SECRETS_DIR / "gmail-token.pickle"
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

SCRIPT_DIR = pathlib.Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DRAFTS_DIR = PROJECT_DIR / "outreach" / "drafts"
SENT_LOG = PROJECT_DIR / "outreach" / "sent.json"

FROM_EMAIL = "Tom <tom@send.socialtradingvlog.com>"
REPLY_TO = "socialtradingvlog@gmail.com"


def get_resend_key():
    """Load Resend API key."""
    if not RESEND_KEY_FILE.exists():
        print(f"ERROR: Resend API key not found at {RESEND_KEY_FILE}")
        print("Save your Resend API key to that file first.")
        sys.exit(1)
    return RESEND_KEY_FILE.read_text().strip()


def get_gmail_credentials():
    """Get or refresh Gmail API credentials."""
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None
    if GMAIL_TOKEN_FILE.exists():
        with open(GMAIL_TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not GMAIL_CLIENT_SECRET.exists():
                print(f"ERROR: Gmail OAuth credentials not found at {GMAIL_CLIENT_SECRET}")
                print("Set up Gmail API in Google Cloud Console first.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(GMAIL_CLIENT_SECRET), GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GMAIL_TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return creds


def get_gmail():
    """Build authenticated Gmail API client."""
    from googleapiclient.discovery import build
    creds = get_gmail_credentials()
    return build("gmail", "v1", credentials=creds)


# ─────────────────────────────────────────────
# Sending emails via Resend
# ─────────────────────────────────────────────

def send_email(to, subject, body_text, body_html=None):
    """Send an email via Resend API."""
    api_key = get_resend_key()

    payload = {
        "from": FROM_EMAIL,
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
        "reply_to": REPLY_TO,
        "text": body_text,
    }
    if body_html:
        payload["html"] = body_html

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SocialTradingVlog-Outreach/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"ERROR sending email: {e.code} — {error_body}")
        return None


def log_sent(to, subject, draft_name=None):
    """Log a sent email for tracking."""
    SENT_LOG.parent.mkdir(parents=True, exist_ok=True)

    log = []
    if SENT_LOG.exists():
        log = json.loads(SENT_LOG.read_text())

    log.append({
        "to": to,
        "subject": subject,
        "draft": draft_name,
        "sent_at": datetime.now().isoformat(),
        "reply_received": False,
    })

    SENT_LOG.write_text(json.dumps(log, indent=2))


# ─────────────────────────────────────────────
# Draft management
# ─────────────────────────────────────────────

def list_drafts():
    """List available email drafts."""
    if not DRAFTS_DIR.exists():
        print("No drafts directory found. Creating it...")
        DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
        return []

    drafts = sorted(DRAFTS_DIR.glob("*.json"))
    if not drafts:
        print("No drafts found. Create drafts in outreach/drafts/ as JSON files.")
        return []

    print(f"\nAvailable drafts ({len(drafts)}):\n")
    for d in drafts:
        data = json.loads(d.read_text())
        status = "SENT" if is_draft_sent(d.stem) else "ready"
        print(f"  [{status:5s}]  {d.stem}")
        print(f"           To: {data.get('to', '?')}")
        print(f"           Subject: {data.get('subject', '?')[:60]}")
        print()

    return drafts


def is_draft_sent(draft_name):
    """Check if a draft has already been sent."""
    if not SENT_LOG.exists():
        return False
    log = json.loads(SENT_LOG.read_text())
    return any(entry.get("draft") == draft_name for entry in log)


def load_draft(name):
    """Load a draft by name."""
    path = DRAFTS_DIR / f"{name}.json"
    if not path.exists():
        # Try without extension
        path = DRAFTS_DIR / name
        if not path.exists():
            print(f"Draft not found: {name}")
            print(f"Available drafts:")
            list_drafts()
            return None
    return json.loads(path.read_text()), path.stem


def cmd_send_draft(draft_name):
    """Review and send a draft email."""
    result = load_draft(draft_name)
    if not result:
        return
    draft, name = result

    to = draft["to"]
    subject = draft["subject"]
    body = draft["body"]

    if is_draft_sent(name):
        print(f"\nWARNING: This draft ({name}) has already been sent!")
        confirm = input("Send again? (y/N): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return

    print(f"\n{'=' * 60}")
    print(f"  DRAFT: {name}")
    print(f"{'=' * 60}")
    print(f"  From: {FROM_EMAIL}")
    print(f"  To:   {to}")
    print(f"  Subject: {subject}")
    print(f"  Reply-To: {REPLY_TO}")
    print(f"{'=' * 60}")
    print()
    print(body)
    print()
    print(f"{'=' * 60}")

    confirm = input("\nSend this email? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    print("Sending...")
    result = send_email(to, subject, body)
    if result:
        print(f"Sent! ID: {result.get('id', '?')}")
        log_sent(to, subject, name)
    else:
        print("Failed to send.")


def cmd_send_direct(to, subject, body):
    """Send an email directly (not from draft)."""
    print(f"\n{'=' * 60}")
    print(f"  From: {FROM_EMAIL}")
    print(f"  To:   {to}")
    print(f"  Subject: {subject}")
    print(f"  Reply-To: {REPLY_TO}")
    print(f"{'=' * 60}")
    print()
    print(body)
    print()
    print(f"{'=' * 60}")

    confirm = input("\nSend this email? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    print("Sending...")
    result = send_email(to, subject, body)
    if result:
        print(f"Sent! ID: {result.get('id', '?')}")
        log_sent(to, subject)
    else:
        print("Failed to send.")


# ─────────────────────────────────────────────
# Inbox monitoring via Gmail API
# ─────────────────────────────────────────────

def cmd_inbox(unread_only=False):
    """Check inbox for recent messages."""
    gmail = get_gmail()

    query = "in:inbox"
    if unread_only:
        query += " is:unread"

    results = gmail.users().messages().list(
        userId="me", q=query, maxResults=20
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        print("\nNo messages found.")
        return

    print(f"\n{'Unread' if unread_only else 'Recent'} inbox messages ({len(messages)}):\n")

    for msg_info in messages:
        msg = gmail.users().messages().get(
            userId="me", id=msg_info["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        is_unread = "UNREAD" in msg.get("labelIds", [])
        marker = "  NEW " if is_unread else "      "

        print(f"  {marker} From: {headers.get('From', '?')[:50]}")
        print(f"         Subject: {headers.get('Subject', '?')[:60]}")
        print(f"         Date: {headers.get('Date', '?')}")
        print()


# ─────────────────────────────────────────────
# Outreach status tracking
# ─────────────────────────────────────────────

def cmd_status():
    """Show outreach tracking status."""
    if not SENT_LOG.exists():
        print("\nNo emails sent yet.")
        return

    log = json.loads(SENT_LOG.read_text())
    print(f"\nOutreach status ({len(log)} emails sent):\n")

    for entry in log:
        replied = "REPLIED" if entry.get("reply_received") else "waiting"
        print(f"  [{replied:7s}]  {entry['sent_at'][:10]}")
        print(f"             To: {entry['to']}")
        print(f"             Subject: {entry['subject'][:50]}")
        if entry.get("draft"):
            print(f"             Draft: {entry['draft']}")
        print()


# ─────────────────────────────────────────────
# Auto follow-ups
# ─────────────────────────────────────────────

FOLLOWUP_DAYS = 5  # days before sending a follow-up
FOLLOWUP_LOG = PROJECT_DIR / "outreach" / "followups.json"

FOLLOWUP_TEMPLATE = """Hi,

Just wanted to follow up on my email from last week — I know inboxes get busy!

I'd love the opportunity to contribute. I have nearly 10 years of real, documented copy trading experience on eToro (since 2016), backed by 335 YouTube videos. Happy to send a draft or outline if that's easier.

No worries if it's not a fit — thanks for your time either way.

Best,
Tom
Social Trading Vlog
https://socialtradingvlog.com"""


def get_followup_log():
    """Load follow-up tracking log."""
    if not FOLLOWUP_LOG.exists():
        return []
    return json.loads(FOLLOWUP_LOG.read_text())


def save_followup_log(log):
    """Save follow-up tracking log."""
    FOLLOWUP_LOG.parent.mkdir(parents=True, exist_ok=True)
    FOLLOWUP_LOG.write_text(json.dumps(log, indent=2))


def check_for_reply(gmail, sender_email, sent_after=None):
    """Check if we've received a reply from this email address after a given date."""
    query = f"from:{sender_email} in:inbox"
    if sent_after:
        # Gmail search uses after:YYYY/MM/DD (messages received after this date)
        query += f" after:{sent_after.strftime('%Y/%m/%d')}"
    try:
        results = gmail.users().messages().list(
            userId="me", q=query, maxResults=1
        ).execute()
        return len(results.get("messages", [])) > 0
    except Exception:
        return False


def cmd_check_followups():
    """Check which sent emails need follow-ups."""
    if not SENT_LOG.exists():
        print("\nNo emails sent yet.")
        return

    log = json.loads(SENT_LOG.read_text())
    followup_log = get_followup_log()
    already_followed_up = {f["to"] for f in followup_log}

    # Connect to Gmail to check for replies
    try:
        gmail = get_gmail()
        can_check_replies = True
    except Exception:
        gmail = None
        can_check_replies = False
        print("(Gmail not available — can't check for replies)\n")

    now = datetime.now()
    needs_followup = []
    updated = False

    print(f"\nFollow-up check ({len(log)} emails sent):\n")

    for entry in log:
        to = entry["to"]
        sent_at = datetime.fromisoformat(entry["sent_at"])
        days_ago = (now - sent_at).days
        subject = entry["subject"]

        # Check for reply via Gmail (only replies received after we sent)
        if can_check_replies and not entry.get("reply_received"):
            domain = to.split("@")[1] if "@" in to else to
            if check_for_reply(gmail, domain, sent_after=sent_at):
                entry["reply_received"] = True
                updated = True

        if entry.get("reply_received"):
            print(f"  [REPLIED ]  {to}")
            print(f"              {subject[:50]}")
            print()
            continue

        if to in already_followed_up:
            print(f"  [FOLLOWED]  {to} (sent {days_ago}d ago)")
            print(f"              {subject[:50]}")
            print()
            continue

        if days_ago >= FOLLOWUP_DAYS:
            needs_followup.append(entry)
            print(f"  [NEEDS FU]  {to} (sent {days_ago}d ago)")
            print(f"              {subject[:50]}")
            print()
        else:
            remaining = FOLLOWUP_DAYS - days_ago
            print(f"  [WAIT {remaining}d  ]  {to} (sent {days_ago}d ago)")
            print(f"              {subject[:50]}")
            print()

    if updated:
        SENT_LOG.write_text(json.dumps(log, indent=2))

    if needs_followup:
        print(f"\n  {len(needs_followup)} email(s) ready for follow-up.")
        print(f"  Run --send-followups to send them.")
    else:
        print(f"\n  No follow-ups needed right now.")

    return needs_followup


def cmd_send_followups():
    """Send follow-up emails for unanswered outreach."""
    if not SENT_LOG.exists():
        print("\nNo emails sent yet.")
        return

    log = json.loads(SENT_LOG.read_text())
    followup_log = get_followup_log()
    already_followed_up = {f["to"] for f in followup_log}

    now = datetime.now()
    sent_count = 0

    for entry in log:
        to = entry["to"]
        sent_at = datetime.fromisoformat(entry["sent_at"])
        days_ago = (now - sent_at).days

        if entry.get("reply_received"):
            continue
        if to in already_followed_up:
            continue
        if days_ago < FOLLOWUP_DAYS:
            continue

        subject = f"Re: {entry['subject']}"
        body = FOLLOWUP_TEMPLATE

        print(f"\nFollowing up with {to}...")
        print(f"  Subject: {subject}")

        result = send_email(to, subject, body)
        if result:
            print(f"  SENT! ID: {result.get('id', '?')}")
            followup_log.append({
                "to": to,
                "subject": subject,
                "original_subject": entry["subject"],
                "sent_at": now.isoformat(),
            })
            sent_count += 1
        else:
            print(f"  FAILED!")

    save_followup_log(followup_log)
    print(f"\n{sent_count} follow-up(s) sent.")


# ─────────────────────────────────────────────
# Journalist query scanner (HARO/Connectively/SourceBottle)
# ─────────────────────────────────────────────

JOURNALIST_KEYWORDS = [
    "copy trading", "social trading", "etoro", "retail investor",
    "trading platform", "passive investing", "investing experience",
    "broker review", "trading for beginners", "fintech",
    "investment returns", "trading losses", "retail trading",
    "CFD", "forex trading", "online broker",
]

JOURNALIST_SENDERS = [
    "haro", "connectively", "sourcebottle", "journorequest",
    "helpab2bwriter", "qwoted", "terkel", "featured.com",
    "pressplug", "sourceofsources",
]


def cmd_scan_journalist_queries():
    """Scan inbox for journalist query digests and find relevant opportunities."""
    gmail = get_gmail()

    # Search for emails from known journalist query services
    sender_queries = " OR ".join(f"from:{s}" for s in JOURNALIST_SENDERS)
    query = f"({sender_queries}) newer_than:7d"

    results = gmail.users().messages().list(
        userId="me", q=query, maxResults=50
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        # Also check for any emails mentioning journalist/source/expert in subject
        query2 = "(subject:journalist OR subject:source OR subject:expert OR subject:HARO OR subject:query) newer_than:7d"
        results = gmail.users().messages().list(
            userId="me", q=query2, maxResults=20
        ).execute()
        messages = results.get("messages", [])

    if not messages:
        print("\nNo journalist query emails found in the last 7 days.")
        print("\nTo get journalist queries, sign up for these free services:")
        print("  - Connectively (formerly HARO): https://www.connectively.us")
        print("  - Qwoted: https://www.qwoted.com")
        print("  - SourceBottle: https://www.sourcebottle.com")
        print("  - Help a B2B Writer: https://helpab2bwriter.com")
        print("  - JournoRequests (UK): https://www.journorequests.com")
        print("  - Featured.com: https://featured.com")
        print("  - Terkel: https://terkel.io")
        print(f"\nUse {REPLY_TO} when signing up so I can scan for opportunities.")
        return

    print(f"\nScanning {len(messages)} journalist query emails...\n")

    matches = []
    for msg_info in messages:
        msg = gmail.users().messages().get(
            userId="me", id=msg_info["id"], format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        subject = headers.get("Subject", "")
        from_addr = headers.get("From", "")
        date = headers.get("Date", "")

        # Get body text
        body_text = ""
        payload = msg.get("payload", {})
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                        break
        elif "body" in payload:
            data = payload["body"].get("data", "")
            if data:
                body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

        # Check for keyword matches
        full_text = (subject + " " + body_text).lower()
        matched_keywords = [kw for kw in JOURNALIST_KEYWORDS if kw.lower() in full_text]

        if matched_keywords:
            matches.append({
                "from": from_addr,
                "subject": subject,
                "date": date,
                "keywords": matched_keywords,
                "snippet": body_text[:500],
            })

    if matches:
        print(f"Found {len(matches)} relevant journalist queries:\n")
        for m in matches:
            print(f"  From: {m['from'][:50]}")
            print(f"  Subject: {m['subject'][:60]}")
            print(f"  Date: {m['date']}")
            print(f"  Matched: {', '.join(m['keywords'])}")
            print(f"  Preview: {m['snippet'][:200]}...")
            print()
    else:
        print(f"Scanned {len(messages)} emails — no relevant queries found this week.")
        print("Keywords searched: " + ", ".join(JOURNALIST_KEYWORDS[:5]) + "...")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Email outreach for SocialTradingVlog")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--send", metavar="DRAFT", help="Review and send a draft email")
    group.add_argument("--send-direct", nargs=3, metavar=("TO", "SUBJECT", "BODY"),
                       help="Send email directly: --send-direct to@email.com 'Subject' 'Body'")
    group.add_argument("--inbox", action="store_true", help="Check inbox")
    group.add_argument("--list-drafts", action="store_true", help="List available drafts")
    group.add_argument("--status", action="store_true", help="Show outreach tracking")
    group.add_argument("--check-followups", action="store_true", help="Check which emails need follow-ups")
    group.add_argument("--send-followups", action="store_true", help="Send follow-up emails")
    group.add_argument("--scan-journalist-queries", action="store_true", help="Scan for journalist query opportunities")

    parser.add_argument("--unread", action="store_true", help="With --inbox: show unread only")

    args = parser.parse_args()

    if args.send:
        cmd_send_draft(args.send)
    elif args.send_direct:
        cmd_send_direct(*args.send_direct)
    elif args.inbox:
        cmd_inbox(unread_only=args.unread)
    elif args.list_drafts:
        list_drafts()
    elif args.status:
        cmd_status()
    elif args.check_followups:
        cmd_check_followups()
    elif args.send_followups:
        cmd_send_followups()
    elif args.scan_journalist_queries:
        cmd_scan_journalist_queries()


if __name__ == "__main__":
    main()
