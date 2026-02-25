#!/usr/bin/env python3
"""
Proposal Manager — Suggests improvements, Tom approves via Telegram.

The system proposes new tools, optimizations, or changes. Tom approves
or rejects by replying to the Telegram bot. Approved proposals are
queued for execution.

Flow:
  1. analytics_monitor.py generates proposals in weekly report
  2. Proposals sent via Telegram with an ID
  3. Tom replies: "yes 1" or "no 1" (or just "yes" for latest)
  4. This script checks for approvals every hour (cron)
  5. Approved proposals are executed or queued

Usage:
    python3 tools/proposal_manager.py --check          # Check for new approvals
    python3 tools/proposal_manager.py --list            # List all proposals
    python3 tools/proposal_manager.py --propose "..."   # Create a new proposal

Cron:
    0 * * * * python3 /var/www/.../tools/proposal_manager.py --check
"""

import sys
import os
import json
import pathlib
import argparse
import urllib.request
from datetime import datetime

PROJECT_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
PROPOSALS_FILE = DATA_DIR / "proposals.json"
SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"


def load_proposals():
    """Load all proposals."""
    if PROPOSALS_FILE.exists():
        return json.loads(PROPOSALS_FILE.read_text())
    return {"proposals": [], "last_update_id": 0}


def save_proposals(data):
    """Save proposals."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROPOSALS_FILE.write_text(json.dumps(data, indent=2))


def create_proposal(title, description, category="tool", action=None):
    """Create a new proposal and send to Tom via Telegram."""
    data = load_proposals()

    proposal_id = len(data["proposals"]) + 1
    proposal = {
        "id": proposal_id,
        "title": title,
        "description": description,
        "category": category,
        "action": action,  # Script/command to run if approved
        "status": "pending",
        "created": datetime.now().isoformat(),
        "decided": None,
    }

    data["proposals"].append(proposal)
    save_proposals(data)

    # Send via Telegram
    msg = (
        f"💡 *Proposal #{proposal_id}*\n\n"
        f"*{title}*\n"
        f"{description}\n\n"
        f"Reply *yes {proposal_id}* to approve or *no {proposal_id}* to reject."
    )
    send_telegram(msg)

    # Also send via email
    send_email_proposal(proposal)

    print(f"  Proposal #{proposal_id} created and sent to Tom.")
    return proposal_id


def send_telegram(message):
    """Send message via Telegram bot."""
    try:
        token_file = SECRETS_DIR / "telegram-bot-token.txt"
        chat_file = SECRETS_DIR / "telegram-chat-id.txt"
        if not token_file.exists() or not chat_file.exists():
            return False

        token = token_file.read_text().strip()
        chat_id = chat_file.read_text().strip()

        payload = json.dumps({
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }).encode()

        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"  Telegram send failed: {e}")
        return False


def send_email_proposal(proposal):
    """Send proposal via email."""
    try:
        config_file = SECRETS_DIR / "email-alerts.json"
        if not config_file.exists():
            return

        config = json.loads(config_file.read_text())

        body = (
            f"STV Autopilot Proposal #{proposal['id']}\n\n"
            f"Title: {proposal['title']}\n\n"
            f"{proposal['description']}\n\n"
            f"Category: {proposal['category']}\n\n"
            f"To approve, reply to the Telegram bot with: yes {proposal['id']}\n"
            f"To reject: no {proposal['id']}\n\n"
            f"— STV Autopilot"
        )

        payload = json.dumps({
            "from": config["from_email"],
            "to": [config["to_email"]],
            "subject": f"[STV PROPOSAL #{proposal['id']}] {proposal['title']}",
            "text": body,
        }).encode()

        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['api_key']}",
            },
        )
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"  Email send failed: {e}")


def _sanitize_input(text):
    """Sanitize Telegram input — strip control chars, limit length, reject injection."""
    if not text or not isinstance(text, str):
        return ""
    # Strip control characters except newline
    text = "".join(c for c in text if c == "\n" or (ord(c) >= 32 and ord(c) < 127))
    # Hard length limit — no legitimate command is longer than 50 chars
    text = text[:50].strip().lower()
    # Block common injection patterns
    injection_patterns = [
        "ignore", "forget", "pretend", "system", "admin", "execute",
        "eval(", "exec(", "import ", "os.", "subprocess", "__", "$(", "`",
        "&&", "||", ";", "|", ">", "<", "\\", "{", "}", "curl", "wget",
    ]
    for pattern in injection_patterns:
        if pattern in text:
            return ""  # Silently discard
    return text


# Rate limiting: max 20 commands per hour from any single chat_id
_rate_limit = {}
MAX_COMMANDS_PER_HOUR = 20


def _check_rate_limit(chat_id):
    """Return True if within rate limit, False if exceeded."""
    import time
    now = time.time()
    if chat_id not in _rate_limit:
        _rate_limit[chat_id] = []
    # Prune old entries
    _rate_limit[chat_id] = [t for t in _rate_limit[chat_id] if now - t < 3600]
    if len(_rate_limit[chat_id]) >= MAX_COMMANDS_PER_HOUR:
        return False
    _rate_limit[chat_id].append(now)
    return True


def check_for_approvals():
    """Poll Telegram for approval/rejection replies.

    Security measures:
      - Only processes messages from Tom's verified chat_id
      - All input sanitized and length-limited
      - Injection patterns blocked
      - Rate limited (20 commands/hour)
      - No shell execution on approval
      - Unknown messages from other users are logged and discarded
    """
    data = load_proposals()

    try:
        token_file = SECRETS_DIR / "telegram-bot-token.txt"
        chat_file = SECRETS_DIR / "telegram-chat-id.txt"
        if not token_file.exists() or not chat_file.exists():
            print("  Telegram credentials not found.")
            return

        token = token_file.read_text().strip()
        tom_chat_id = chat_file.read_text().strip()

        if not tom_chat_id or not tom_chat_id.isdigit():
            print("  Invalid chat ID configuration.")
            return

        last_update = data.get("last_update_id", 0)
        url = f"https://api.telegram.org/bot{token}/getUpdates?offset={last_update + 1}&limit=50"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=10)
        updates = json.loads(resp.read().decode())

        if not updates.get("ok"):
            return

        unauthorized_attempts = 0

        for update in updates.get("result", []):
            data["last_update_id"] = update["update_id"]

            msg = update.get("message", {})
            chat_id = str(msg.get("chat", {}).get("id", ""))

            # SECURITY: Only process messages from Tom's verified chat_id
            if chat_id != tom_chat_id:
                unauthorized_attempts += 1
                if unauthorized_attempts > 5:
                    # Alert on suspicious volume of unauthorized messages
                    print(f"  SECURITY WARNING: {unauthorized_attempts} unauthorized Telegram messages detected")
                continue

            # Rate limiting
            if not _check_rate_limit(chat_id):
                send_telegram("Rate limit reached. Please wait before sending more commands.")
                continue

            raw_text = (msg.get("text", "") or "").strip()
            text = _sanitize_input(raw_text)

            if not text:
                continue  # Empty or blocked input

            # STRICT command parsing — only exact patterns accepted
            if text == "yes" or (text.startswith("yes ") and len(text) <= 10):
                parts = text.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    proposal_id = int(parts[1])
                    if 0 < proposal_id <= 1000:  # Reasonable bounds
                        approve_proposal(data, proposal_id)
                else:
                    # Approve latest pending
                    pending = [p for p in data["proposals"] if p["status"] == "pending"]
                    proposal_id = pending[-1]["id"] if pending else None
                    if proposal_id:
                        approve_proposal(data, proposal_id)

            elif text.startswith("no ") and len(text) <= 10:
                parts = text.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    proposal_id = int(parts[1])
                    if 0 < proposal_id <= 1000:
                        reject_proposal(data, proposal_id)

            elif text in ("/proposals", "/list"):
                list_proposals_telegram(data)

            elif text == "/status":
                send_status_telegram()

            # All other input is silently ignored (no error messages that
            # could help an attacker understand the command interface)

        if unauthorized_attempts > 0:
            print(f"  Discarded {unauthorized_attempts} message(s) from unauthorized users.")

        save_proposals(data)

    except Exception as e:
        print(f"  Error checking approvals: {e}")


def approve_proposal(data, proposal_id):
    """Mark proposal as approved. No automatic execution — queued for manual review."""
    for p in data["proposals"]:
        if p["id"] == proposal_id and p["status"] == "pending":
            p["status"] = "approved"
            p["decided"] = datetime.now().isoformat()

            send_telegram(f"✅ Proposal #{proposal_id} approved: *{p['title']}*\n\nQueued for implementation.")

            # SECURITY: No automatic shell execution. Approved proposals are
            # logged and queued only. Implementation requires manual intervention
            # or a separate, sandboxed deployment pipeline.
            if p.get("action"):
                p["execution_result"] = "Queued — requires manual deployment"

            print(f"  Proposal #{proposal_id} approved: {p['title']}")
            return

    send_telegram(f"Proposal #{proposal_id} not found or already decided.")


def reject_proposal(data, proposal_id):
    """Mark proposal as rejected."""
    for p in data["proposals"]:
        if p["id"] == proposal_id and p["status"] == "pending":
            p["status"] = "rejected"
            p["decided"] = datetime.now().isoformat()
            send_telegram(f"❌ Proposal #{proposal_id} rejected: *{p['title']}*")
            print(f"  Proposal #{proposal_id} rejected: {p['title']}")
            return


def list_proposals_telegram(data):
    """Send list of pending proposals to Telegram."""
    pending = [p for p in data["proposals"] if p["status"] == "pending"]
    if not pending:
        send_telegram("No pending proposals. Everything is running smoothly! 🟢")
        return

    msg = "📋 *Pending Proposals:*\n\n"
    for p in pending:
        msg += f"#{p['id']} — {p['title']}\n"
    msg += "\nReply *yes [number]* to approve or *no [number]* to reject."
    send_telegram(msg)


def send_status_telegram():
    """Send quick system status via Telegram."""
    try:
        sys.path.insert(0, str(PROJECT_DIR / "tools"))
        from site_autopilot import check_uptime, check_subtitle_pipeline

        msg = "🔍 *Quick Status Check*\n\n"

        # Uptime
        try:
            uptime_ok = check_uptime()
            msg += f"Site: {'✅ Online' if uptime_ok else '🔴 Issues detected'}\n"
        except Exception:
            msg += "Site: ❓ Check failed\n"

        # Pipeline
        trans_dir = PROJECT_DIR / "transcriptions"
        if trans_dir.exists():
            total = sum(1 for d in trans_dir.iterdir() if d.is_dir() and not d.name.startswith("."))
            complete = sum(
                1 for d in trans_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
                and all((d / f"subtitles.{l}.srt").exists()
                        for l in ["en", "es", "de", "fr", "it", "pt", "ar", "pl", "nl", "ko"])
            )
            msg += f"Subtitles: {complete}/{total} complete\n"

        # Last fee check
        verified_file = DATA_DIR / "platform-verified.json"
        if verified_file.exists():
            v = json.loads(verified_file.read_text())
            last = v.get("_last_full_check", "Never")
            msg += f"Fee data last checked: {last[:10]}\n"

        send_telegram(msg)
    except Exception as e:
        send_telegram(f"Status check error: {str(e)[:200]}")


# ─── Preset Proposals (suggested by analytics) ───────────────────────────

TOOL_SUGGESTIONS = [
    {
        "title": "Add Tax Calculator by Country",
        "description": "A tool showing estimated capital gains tax on trading profits, "
                       "by country (UK CGT, US short/long-term, EU varies). "
                       "Helps beginners understand after-tax returns.",
        "category": "tool",
    },
    {
        "title": "Add Risk Profile Quiz",
        "description": "'What type of investor are you?' — 5-question quiz that recommends "
                       "suitable platforms and strategies based on risk tolerance, experience, "
                       "and goals. High engagement potential.",
        "category": "tool",
    },
    {
        "title": "Add Dividend Calculator",
        "description": "Calculator showing projected dividend income from stocks/ETFs "
                       "over time. Input: amount invested, dividend yield, reinvestment. "
                       "Output: passive income projection chart.",
        "category": "tool",
    },
    {
        "title": "Add Currency Conversion Cost Calculator",
        "description": "Shows true cost of FX conversion on each platform — hidden "
                       "fees that beginners don't know about. Very useful for non-USD investors.",
        "category": "tool",
    },
    {
        "title": "Add Portfolio Rebalancing Tool",
        "description": "Input target allocation + current holdings → shows what to buy/sell "
                       "to rebalance. Simple but very useful for copy traders diversifying.",
        "category": "tool",
    },
]


def suggest_new_tools():
    """Propose new tools based on analytics data and preset suggestions."""
    data = load_proposals()

    # Check which suggestions haven't been proposed yet
    existing_titles = {p["title"] for p in data["proposals"]}

    proposed = 0
    for suggestion in TOOL_SUGGESTIONS:
        if suggestion["title"] not in existing_titles:
            create_proposal(
                title=suggestion["title"],
                description=suggestion["description"],
                category=suggestion["category"],
            )
            proposed += 1
            if proposed >= 2:  # Max 2 new proposals per run
                break

    if proposed == 0:
        print("  No new tool suggestions to propose.")


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="STV Proposal Manager")
    parser.add_argument("--check", action="store_true", help="Check for new approvals via Telegram")
    parser.add_argument("--list", action="store_true", help="List all proposals")
    parser.add_argument("--propose", help="Create a new proposal with given title")
    parser.add_argument("--suggest", action="store_true", help="Suggest new tools from preset list")
    args = parser.parse_args()

    print(f"STV Proposal Manager — {datetime.now().isoformat()}\n")

    if args.check:
        check_for_approvals()
    elif args.list:
        data = load_proposals()
        for p in data["proposals"]:
            status_icon = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(p["status"], "?")
            print(f"  {status_icon} #{p['id']} [{p['status']}] {p['title']}")
    elif args.propose:
        create_proposal(args.propose, "Proposed via command line.", "manual")
    elif args.suggest:
        suggest_new_tools()

    print("\nDone.")


if __name__ == "__main__":
    main()
