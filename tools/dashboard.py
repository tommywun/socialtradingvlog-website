#!/usr/bin/env python3
"""
SocialTradingVlog Dashboard — local web dashboard for tracking everything.

Usage:
    python3 tools/dashboard.py              # start dashboard on http://localhost:8080
    python3 tools/dashboard.py --port 9090  # custom port
"""

import sys
import os
import json
import pathlib
import argparse
import urllib.parse
import base64
import pickle
import hashlib
import secrets
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

if sys.platform == "darwin":
    sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

# ─── Authentication ───
AUTH_TOKEN_FILE = pathlib.Path.home() / ".config" / "stv-secrets" / "dashboard-auth.json"
SESSIONS_FILE = None  # set after PROJECT_DIR is defined
DEVICES_FILE = None   # set after PROJECT_DIR is defined
ACTIVE_SESSIONS = {}  # token -> expiry timestamp
TRUSTED_DEVICES = {}  # device_token -> {name, created, last_used}


def _init_session_files():
    global SESSIONS_FILE, DEVICES_FILE
    SESSIONS_FILE = PROJECT_DIR / "data" / "sessions.json"
    DEVICES_FILE = PROJECT_DIR / "data" / "trusted-devices.json"
    _load_sessions()
    _load_devices()


def _load_sessions():
    global ACTIVE_SESSIONS
    if SESSIONS_FILE and SESSIONS_FILE.exists():
        try:
            ACTIVE_SESSIONS = json.loads(SESSIONS_FILE.read_text())
        except Exception:
            ACTIVE_SESSIONS = {}


def _save_sessions():
    if SESSIONS_FILE:
        SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SESSIONS_FILE.write_text(json.dumps(ACTIVE_SESSIONS))


def _load_devices():
    global TRUSTED_DEVICES
    if DEVICES_FILE and DEVICES_FILE.exists():
        try:
            TRUSTED_DEVICES = json.loads(DEVICES_FILE.read_text())
        except Exception:
            TRUSTED_DEVICES = {}


def _save_devices():
    if DEVICES_FILE:
        DEVICES_FILE.parent.mkdir(parents=True, exist_ok=True)
        DEVICES_FILE.write_text(json.dumps(TRUSTED_DEVICES, indent=2))




# ─── WebAuthn Passkey (Face ID) ───
WEBAUTHN_FILE = None  # set after PROJECT_DIR
WEBAUTHN_CHALLENGES = {}  # challenge -> expiry timestamp
WEBAUTHN_RP_ID = "socialtradingvlog.com"
WEBAUTHN_RP_NAME = "STV Command Centre"


def _load_webauthn_credentials():
    if WEBAUTHN_FILE.exists():
        try:
            return json.loads(WEBAUTHN_FILE.read_text())
        except Exception:
            return []
    return []


def _save_webauthn_credentials(creds):
    WEBAUTHN_FILE.parent.mkdir(parents=True, exist_ok=True)
    WEBAUTHN_FILE.write_text(json.dumps(creds, indent=2))


def webauthn_register_options():
    """Generate registration challenge and options."""
    import base64
    challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    WEBAUTHN_CHALLENGES[challenge] = datetime.now().timestamp() + 300  # 5 min expiry
    existing = _load_webauthn_credentials()
    exclude = [{"id": c["id"], "type": "public-key"} for c in existing]
    return {
        "challenge": challenge,
        "rp": {"id": WEBAUTHN_RP_ID, "name": WEBAUTHN_RP_NAME},
        "user": {"id": base64.urlsafe_b64encode(b"stv-admin").rstrip(b"=").decode(), "name": "admin", "displayName": "STV Admin"},
        "pubKeyCredParams": [
            {"alg": -7, "type": "public-key"},
            {"alg": -257, "type": "public-key"}
        ],
        "authenticatorSelection": {
            "authenticatorAttachment": "platform",
            "userVerification": "required",
            "residentKey": "preferred"
        },
        "timeout": 60000,
        "excludeCredentials": exclude,
        "attestation": "none"
    }


def webauthn_register_complete(data):
    """Store the credential after registration."""
    challenge = data.get("challenge", "")
    expiry = WEBAUTHN_CHALLENGES.pop(challenge, 0)
    if not expiry or expiry < datetime.now().timestamp():
        return {"error": "Challenge expired or invalid"}

    cred_id = data.get("credentialId", "")
    if not cred_id:
        return {"error": "No credential ID"}

    creds = _load_webauthn_credentials()
    creds.append({
        "id": cred_id,
        "created": datetime.now().isoformat(),
        "name": data.get("name", "Face ID")
    })
    _save_webauthn_credentials(creds)
    return {"success": True}


def webauthn_login_options():
    """Generate authentication challenge and options."""
    import base64
    creds = _load_webauthn_credentials()
    if not creds:
        return {"error": "No passkeys registered"}

    challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    WEBAUTHN_CHALLENGES[challenge] = datetime.now().timestamp() + 300

    allow = [{"id": c["id"], "type": "public-key"} for c in creds]
    return {
        "challenge": challenge,
        "rpId": WEBAUTHN_RP_ID,
        "allowCredentials": allow,
        "userVerification": "required",
        "timeout": 60000
    }


def webauthn_login_complete(data):
    """Verify the assertion and create a session."""
    challenge = data.get("challenge", "")
    expiry = WEBAUTHN_CHALLENGES.pop(challenge, 0)
    if not expiry or expiry < datetime.now().timestamp():
        return {"error": "Challenge expired or invalid"}

    cred_id = data.get("credentialId", "")
    creds = _load_webauthn_credentials()
    if not any(c["id"] == cred_id for c in creds):
        return {"error": "Unknown credential"}

    # Credential matched + biometric verified on device + challenge valid
    token = create_session()
    return {"success": True, "session_token": token}

def init_auth():
    """Create auth file with random password if it doesn't exist."""
    if not AUTH_TOKEN_FILE.exists():
        password = secrets.token_urlsafe(16)
        AUTH_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        AUTH_TOKEN_FILE.write_text(json.dumps({"password_hash": hashlib.sha256(password.encode()).hexdigest()}))
        print(f"\n  Dashboard password (save this!): {password}\n")
    return json.loads(AUTH_TOKEN_FILE.read_text())


def verify_password(password):
    auth = json.loads(AUTH_TOKEN_FILE.read_text())
    return hashlib.sha256(password.encode()).hexdigest() == auth["password_hash"]


def create_session():
    token = secrets.token_urlsafe(32)
    ACTIVE_SESSIONS[token] = datetime.now().timestamp() + 86400 * 90  # 90 days
    _save_sessions()
    return token


def verify_session(cookie_header):
    if not cookie_header:
        return False
    for part in cookie_header.split(";"):
        part = part.strip()
        if part.startswith("stv_session="):
            token = part.split("=", 1)[1]
            expiry = ACTIVE_SESSIONS.get(token)
            if expiry and expiry > datetime.now().timestamp():
                return True
            elif token in ACTIVE_SESSIONS:
                del ACTIVE_SESSIONS[token]
                _save_sessions()
    return False


def create_device_token(name=""):
    token = secrets.token_urlsafe(48)
    TRUSTED_DEVICES[token] = {
        "name": name or "Phone",
        "created": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat()
    }
    _save_devices()
    return token


def verify_device_token(token):
    if not token or token not in TRUSTED_DEVICES:
        return False
    TRUSTED_DEVICES[token]["last_used"] = datetime.now().isoformat()
    _save_devices()
    return True


# ─── VPS Task Runner ───
RUNNING_TASKS = {}  # task_id -> {process, log_file, name, started}
TASK_HISTORY = []   # list of completed tasks


def run_task(task_id, name, cmd, cwd=None):
    """Run a command in the background, capture output."""
    log_dir = PROJECT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"task-{task_id}.log"

    def _run():
        try:
            with open(log_file, "w") as f:
                f.write(f"=== {name} started at {datetime.now().isoformat()} ===\n")
                f.flush()
                proc = subprocess.Popen(
                    cmd, stdout=f, stderr=subprocess.STDOUT,
                    cwd=cwd or str(PROJECT_DIR), shell=isinstance(cmd, str)
                )
                RUNNING_TASKS[task_id]["pid"] = proc.pid
                proc.wait()
                f.write(f"\n=== Finished at {datetime.now().isoformat()} (exit code {proc.returncode}) ===\n")
            RUNNING_TASKS[task_id]["status"] = "completed" if proc.returncode == 0 else "failed"
            RUNNING_TASKS[task_id]["exit_code"] = proc.returncode
            RUNNING_TASKS[task_id]["finished"] = datetime.now().isoformat()
            TASK_HISTORY.append(RUNNING_TASKS.pop(task_id))
        except Exception as e:
            with open(log_file, "a") as f:
                f.write(f"\n=== ERROR: {e} ===\n")
            if task_id in RUNNING_TASKS:
                RUNNING_TASKS[task_id]["status"] = "failed"
                TASK_HISTORY.append(RUNNING_TASKS.pop(task_id))

    task_info = {
        "id": task_id, "name": name, "status": "running",
        "started": datetime.now().isoformat(), "log_file": str(log_file), "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
    }
    RUNNING_TASKS[task_id] = task_info
    threading.Thread(target=_run, daemon=True).start()
    return task_info


def get_task_log(task_id, tail=100):
    """Read last N lines of a task log."""
    log_file = PROJECT_DIR / "logs" / f"task-{task_id}.log"
    if not log_file.exists():
        return ""
    lines = log_file.read_text().split("\n")
    return "\n".join(lines[-tail:])


def get_automation_status():
    """Get status of all automation tasks and VPS pipeline."""
    # Check pipeline log
    pipeline_log = PROJECT_DIR / "transcriptions" / "pipeline.log"
    pipeline_status = {"running": False, "last_run": None, "progress": ""}
    if pipeline_log.exists():
        import re as _re
        text = pipeline_log.read_text()
        # Check if pipeline is currently running (started but not finished)
        starts = list(_re.finditer(r'Pipeline started (\S+)', text))
        finishes = list(_re.finditer(r'Pipeline finished (\S+)', text))
        if starts and (not finishes or starts[-1].start() > finishes[-1].start()):
            pipeline_status["running"] = True
        if finishes:
            pipeline_status["last_run"] = finishes[-1].group(1)
        # Get progress from last completion line
        m_list = list(_re.finditer(r'Completed:\s+(\d+)/(\d+)', text))
        if m_list:
            m = m_list[-1]
            pipeline_status["progress"] = f"{m.group(1)}/{m.group(2)} videos"

    # Count transcription/translation stats
    trans_dir = PROJECT_DIR / "transcriptions"
    en_count = len(list(trans_dir.glob("*/subtitles.en.srt"))) if trans_dir.exists() else 0
    all_srt = len(list(trans_dir.glob("*/subtitles.*.srt"))) if trans_dir.exists() else 0

    return {
        "pipeline": pipeline_status,
        "transcriptions": en_count,
        "total_subtitles": all_srt,
        "running_tasks": list(RUNNING_TASKS.values()),
        "recent_tasks": TASK_HISTORY[-10:][::-1],
    }

SCRIPT_DIR = pathlib.Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
_init_session_files()
WEBAUTHN_FILE = PROJECT_DIR / "data" / "webauthn-credentials.json"

# ─── Newsletter Subscribers ───
# Welcome email sender (runs in background thread)
def _send_welcome_email_bg(email):
    """Send welcome email in background thread — don't block the API response."""
    try:
        # Import here to avoid circular dependency at startup
        import importlib.util
        spec = importlib.util.spec_from_file_location("send_newsletter", SCRIPT_DIR / "send_newsletter.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.init_resend()
        mod.send_welcome(email)
    except Exception as e:
        print(f"[WARN] Welcome email failed for {email}: {e}")

SUBSCRIBERS_FILE = PROJECT_DIR / "data" / "subscribers.json"


def load_subscribers():
    if SUBSCRIBERS_FILE.exists():
        return json.loads(SUBSCRIBERS_FILE.read_text())
    return []


def save_subscribers(subs):
    SUBSCRIBERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUBSCRIBERS_FILE.write_text(json.dumps(subs, indent=2))


def add_subscriber(email, source=""):
    import re as _re
    email = email.strip().lower()
    if not _re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return {"error": "Invalid email address"}
    subs = load_subscribers()
    for s in subs:
        if s["email"] == email:
            if s.get("unsubscribed"):
                s["unsubscribed"] = False
                s["resubscribed_at"] = datetime.now().isoformat()
                save_subscribers(subs)
                # Trigger welcome email for resubscriber
                threading.Thread(target=_send_welcome_email_bg, args=(email,), daemon=True).start()
                return {"success": True, "message": "Welcome back!"}
            return {"success": True, "message": "Already subscribed"}
    subs.append({
        "email": email,
        "source": source,
        "subscribed_at": datetime.now().isoformat(),
        "unsubscribed": False,
    })
    save_subscribers(subs)
    # Trigger welcome email in background
    threading.Thread(target=_send_welcome_email_bg, args=(email,), daemon=True).start()
    return {"success": True, "message": "Subscribed successfully"}


def unsubscribe(email):
    email = email.strip().lower()
    subs = load_subscribers()
    for s in subs:
        if s["email"] == email:
            s["unsubscribed"] = True
            s["unsubscribed_at"] = datetime.now().isoformat()
            save_subscribers(subs)
            return True
    return False


def get_subscriber_stats():
    subs = load_subscribers()
    active = [s for s in subs if not s.get("unsubscribed")]
    return {
        "total": len(subs),
        "active": len(active),
        "unsubscribed": len(subs) - len(active),
        "recent": sorted(active, key=lambda x: x.get("subscribed_at", ""), reverse=True)[:10],
    }
REPORTS_DIR = PROJECT_DIR / "reports"
DRAFTS_DIR = PROJECT_DIR / "outreach" / "drafts"
SENT_LOG = PROJECT_DIR / "outreach" / "sent.json"
FOLLOWUP_LOG = PROJECT_DIR / "outreach" / "followups.json"
SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
GMAIL_TOKEN_FILE = SECRETS_DIR / "gmail-token.pickle"
GMAIL_CLIENT_SECRET = SECRETS_DIR / "gmail-oauth.json"


def get_gmail_service():
    """Get Gmail API service (cached)."""
    if not hasattr(get_gmail_service, '_service'):
        try:
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            creds = None
            if GMAIL_TOKEN_FILE.exists():
                with open(GMAIL_TOKEN_FILE, "rb") as f:
                    creds = pickle.load(f)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            if creds and creds.valid:
                get_gmail_service._service = build("gmail", "v1", credentials=creds)
            else:
                get_gmail_service._service = None
        except Exception:
            get_gmail_service._service = None
    return get_gmail_service._service


def get_ga_data():
    latest = REPORTS_DIR / "latest.txt"
    if not latest.exists():
        return {"raw": "No GA report found. Run: python3 tools/ga_report.py --days 7"}
    return {"raw": latest.read_text()}


def get_ga_history():
    """Get historical GA data from daily reports for charting."""
    import re as _re
    reports = sorted(REPORTS_DIR.glob("daily-*.txt"))
    history = []
    for r in reports[-30:]:  # last 30 days
        date = r.stem.replace("daily-", "")
        text = r.read_text()
        # Only parse the FIRST overview section (7-day data)
        first_overview = text.split("OVERVIEW")[1] if "OVERVIEW" in text else text
        # Stop at next section header
        first_overview = first_overview.split("TOP PAGES")[0] if "TOP PAGES" in first_overview else first_overview
        sessions = 0
        users = 0
        pageviews = 0
        bounce = 0.0
        for line in first_overview.split("\n"):
            line_stripped = line.strip()
            if _re.match(r'^Sessions:\s+', line_stripped):
                try:
                    sessions = int(line_stripped.split(":")[-1].strip().split()[0].replace(",", ""))
                except (ValueError, IndexError):
                    pass
            elif _re.match(r'^Users:\s+', line_stripped):
                try:
                    users = int(line_stripped.split(":")[-1].strip().split()[0].replace(",", ""))
                except (ValueError, IndexError):
                    pass
            elif _re.match(r'^Page views:\s+', line_stripped):
                try:
                    pageviews = int(line_stripped.split(":")[-1].strip().split()[0].replace(",", ""))
                except (ValueError, IndexError):
                    pass
            elif _re.match(r'^Bounce rate:\s+', line_stripped):
                try:
                    bounce = float(line_stripped.split(":")[-1].strip().rstrip("%"))
                except (ValueError, IndexError):
                    pass
        history.append({"date": date, "sessions": sessions, "users": users, "pageviews": pageviews, "bounce": bounce})
    return history


def get_outreach_data():
    sent = json.loads(SENT_LOG.read_text()) if SENT_LOG.exists() else []
    followups = json.loads(FOLLOWUP_LOG.read_text()) if FOLLOWUP_LOG.exists() else []
    followed_up_to = {f["to"] for f in followups}
    for entry in sent:
        entry["followed_up"] = entry["to"] in followed_up_to
        sent_at = datetime.fromisoformat(entry["sent_at"])
        entry["days_ago"] = (datetime.now() - sent_at).days
    return {"sent": sent, "followups": followups}


def get_drafts():
    if not DRAFTS_DIR.exists():
        return []
    drafts = []
    sent_entries = json.loads(SENT_LOG.read_text()) if SENT_LOG.exists() else []
    for f in sorted(DRAFTS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            data["_name"] = f.stem
            data["_sent"] = any(e.get("draft") == f.stem for e in sent_entries)
            drafts.append(data)
        except Exception:
            pass
    return drafts


OPPS_DONE_FILE = PROJECT_DIR / "outreach" / "opportunities-done.json"


def get_opps_done():
    if OPPS_DONE_FILE.exists():
        return set(json.loads(OPPS_DONE_FILE.read_text()))
    return set()


def save_opps_done(done_set):
    OPPS_DONE_FILE.parent.mkdir(parents=True, exist_ok=True)
    OPPS_DONE_FILE.write_text(json.dumps(sorted(done_set), indent=2))


def parse_opportunities():
    """Parse opportunities-latest.md into structured sections."""
    import re
    latest = REPORTS_DIR / "opportunities-latest.md"
    if not latest.exists():
        return {"sections": [], "total": 0, "date": ""}
    text = latest.read_text()
    done = get_opps_done()

    # Extract date from header
    date_match = re.search(r'Opportunity Digest — (.+)', text)
    date = date_match.group(1).strip() if date_match else ""

    sections = []
    # Split on --- separators, then parse each section
    parts = re.split(r'\n---\n', text)

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Find section header: ## Section Name (N items)
        sec_match = re.match(r'^##\s+(.+?)(?:\s*\((\d+)\s+\w+\))?\s*$', part, re.MULTILINE)
        if not sec_match:
            # Check for the intro block or engagement rules
            if 'Engagement Rules' in part:
                rules_match = re.search(r'## Engagement Rules\s*\n([\s\S]+)', part)
                if rules_match:
                    rules = []
                    for line in rules_match.group(1).strip().split('\n'):
                        line = line.strip()
                        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                            # Strip bold markers
                            clean = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
                            rules.append(clean)
                    sections.append({
                        "name": "Engagement Rules",
                        "type": "rules",
                        "count": len(rules),
                        "items": [{"text": r} for r in rules],
                    })
            continue

        sec_name = sec_match.group(1).strip()
        sec_count = int(sec_match.group(2)) if sec_match.group(2) else 0

        # Skip intro paragraphs
        if sec_name.startswith('Opportunity Digest'):
            continue

        items = []
        # Find all ### items
        item_blocks = re.split(r'###\s+', part)
        for block in item_blocks[1:]:  # skip first (section header)
            lines = block.strip().split('\n')
            title = lines[0].strip() if lines else ""
            # Clean up title
            title = re.sub(r'^\d+\.\s*', '', title)

            # Extract metadata
            link = ""
            subreddit = ""
            comments = ""
            snippet = ""
            angle = ""
            relevant_page = ""

            for line in lines[1:]:
                line = line.strip()
                if line.startswith('Link:'):
                    link = line.replace('Link:', '').strip()
                elif line.startswith('**r/'):
                    sub_match = re.match(r'\*\*r/(\w+)\*\*\s*\|\s*(\d+)\s*comments', line)
                    if sub_match:
                        subreddit = 'r/' + sub_match.group(1)
                        comments = sub_match.group(2)
                elif line.startswith('**Suggested angle**'):
                    angle = line.replace('**Suggested angle**:', '').strip()
                elif line.startswith('**Relevant page**'):
                    relevant_page = line.replace('**Relevant page**:', '').strip()
                elif line.startswith('> _'):
                    snippet = line.replace('> _', '').rstrip('_').strip()
                elif line.startswith('story |') or line.startswith('comment |'):
                    parts_meta = line.split('|')
                    if len(parts_meta) >= 3:
                        comments = parts_meta[2].strip().split()[0]
                elif line.startswith('- ['):
                    # Manual check link
                    link_match = re.match(r'- \[(.+?)\]\((.+?)\)', line)
                    if link_match:
                        items.append({
                            "title": link_match.group(1),
                            "link": link_match.group(2),
                            "type": "manual_link",
                        })
                        continue

            # Create a stable ID for tracking
            opp_id = re.sub(r'[^a-z0-9]', '', (sec_name + title).lower())[:60]

            if title and not title.startswith('['):  # skip manual link subsections
                items.append({
                    "id": opp_id,
                    "title": title,
                    "link": link,
                    "subreddit": subreddit,
                    "comments": comments,
                    "snippet": snippet[:120],
                    "angle": angle,
                    "relevant_page": relevant_page,
                    "done": opp_id in done,
                })

        # Handle manual check subsections (Quora, BabyPips, etc.)
        if 'Manual Checks' in sec_name:
            sub_sections = re.split(r'###\s+', part)
            manual_items = []
            for sub in sub_sections[1:]:
                sub_lines = sub.strip().split('\n')
                sub_name = sub_lines[0].strip() if sub_lines else ""
                sub_links = []
                sub_note = ""
                for sl in sub_lines[1:]:
                    sl = sl.strip()
                    link_match = re.match(r'- \[(.+?)\]\((.+?)\)', sl)
                    if link_match:
                        sub_links.append({"label": link_match.group(1), "url": link_match.group(2)})
                    elif sl.startswith('_') and sl.endswith('_'):
                        sub_note = sl.strip('_').strip()
                manual_items.append({
                    "name": sub_name,
                    "links": sub_links,
                    "note": sub_note,
                })
            sections.append({
                "name": sec_name,
                "type": "manual",
                "count": len(manual_items),
                "items": manual_items,
            })
            continue

        # Engagement Rules — numbered list items, no ### headers
        if 'Engagement Rules' in sec_name:
            rules = []
            for line in part.split('\n'):
                line = line.strip()
                if re.match(r'^\d+\.', line):
                    clean = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
                    rules.append(clean)
            sections.append({
                "name": "Engagement Rules",
                "type": "rules",
                "count": len(rules),
                "items": [{"text": r} for r in rules],
            })
            continue

        if not items and sec_count == 0:
            sections.append({
                "name": sec_name,
                "type": "empty",
                "count": 0,
                "items": [],
            })
            continue

        done_count = sum(1 for i in items if i.get("done"))
        sections.append({
            "name": sec_name,
            "type": "opportunities",
            "count": len(items),
            "done_count": done_count,
            "items": items,
        })

    total = sum(s.get("count", 0) for s in sections if s.get("type") == "opportunities")
    total_done = sum(s.get("done_count", 0) for s in sections if s.get("type") == "opportunities")
    return {"sections": sections, "total": total, "total_done": total_done, "date": date}


def get_opportunities():
    latest = REPORTS_DIR / "opportunities-latest.md"
    if not latest.exists():
        return {"raw": "No opportunity scan found. Run: python3 tools/opportunity_scanner.py"}
    return {"raw": latest.read_text()}


def get_broken_links():
    latest = REPORTS_DIR / "broken-links-latest.md"
    if not latest.exists():
        return {"raw": "No broken link scan yet. Run: python3 tools/broken_link_finder.py"}
    return {"raw": latest.read_text()}


def get_overview():
    sent = json.loads(SENT_LOG.read_text()) if SENT_LOG.exists() else []
    replied = sum(1 for s in sent if s.get("reply_received"))
    waiting = sum(1 for s in sent if not s.get("reply_received"))
    drafts = list(DRAFTS_DIR.glob("*.json")) if DRAFTS_DIR.exists() else []
    sent_names = {e.get("draft") for e in sent}
    unsent_drafts = sum(1 for d in drafts if d.stem not in sent_names)
    return {
        "emails_sent": len(sent),
        "replies": replied,
        "waiting": waiting,
        "drafts_ready": unsent_drafts,
        "total_drafts": len(drafts),
    }


def get_reply_email(email_domain, after_date=None):
    """Fetch the latest reply email from a domain, optionally only after a date."""
    gmail = get_gmail_service()
    if not gmail:
        return {"error": "Gmail not connected"}
    try:
        query = f"from:{email_domain} in:inbox"
        if after_date:
            query += f" after:{after_date}"
        results = gmail.users().messages().list(userId="me", q=query, maxResults=1).execute()
        messages = results.get("messages", [])
        if not messages:
            return {"error": "No reply found"}
        msg = gmail.users().messages().get(userId="me", id=messages[0]["id"], format="full").execute()
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
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
        return {
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "body": body_text,
        }
    except Exception as e:
        return {"error": str(e)}


def send_draft(name):
    from tools.email_outreach import send_email, log_sent
    path = DRAFTS_DIR / f"{name}.json"
    if not path.exists():
        return {"error": f"Draft not found: {name}"}
    draft = json.loads(path.read_text())
    result = send_email(draft["to"], draft["subject"], draft["body"])
    if result:
        log_sent(draft["to"], draft["subject"], name)
        return {"success": True, "id": result.get("id", "?")}
    return {"error": "Failed to send"}


def send_reply_email(to, subject, body):
    from tools.email_outreach import send_email, log_sent
    result = send_email(to, subject, body)
    if result:
        log_sent(to, subject)
        return {"success": True, "id": result.get("id", "?")}
    return {"error": "Failed to send"}


def save_draft(name, data):
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    path = DRAFTS_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2))
    return {"success": True}


BACKLINKS_FILE = PROJECT_DIR / "outreach" / "backlinks.json"
CONTENT_TRACKER_FILE = PROJECT_DIR / "outreach" / "content-tracker.json"


def get_report_details():
    """Parse latest daily report into structured sections for dashboard widgets."""
    import re as _re
    reports = sorted(REPORTS_DIR.glob("daily-*.txt"))
    if not reports:
        return {"sources": [], "pages": [], "countries": [], "devices": [], "pipeline": {}}

    text = reports[-1].read_text()
    seven_day = text.split("LAST 30 DAYS")[0] if "LAST 30 DAYS" in text else text
    result = {"sources": [], "pages": [], "countries": [], "devices": [], "pipeline": {}}

    def extract_section(txt, header):
        """Extract lines between a section header and the next section."""
        lines = txt.split("\n")
        collecting = False
        eq_seen = 0
        out = []
        for line in lines:
            if header in line:
                collecting = True
                eq_seen = 0
                continue
            if collecting:
                if line.strip().startswith("====="):
                    eq_seen += 1
                    if eq_seen >= 2:
                        break
                    continue
                out.append(line)
        return "\n".join(out)

    # Traffic sources
    section = extract_section(seven_day, "TRAFFIC SOURCES")
    for line in section.split("\n"):
        m = _re.match(r'^\s*(.+?)\s{2,}(\d+)\s+(\d+)\s*$', line)
        if m and not line.strip().startswith("Channel") and "---" not in line:
            result["sources"].append({
                "channel": m.group(1).strip(),
                "sessions": int(m.group(2)),
                "users": int(m.group(3)),
            })

    # Top pages
    section = extract_section(seven_day, "TOP PAGES")
    for line in section.split("\n"):
        m = _re.match(r'^\s*(/\S*)\s+(\d+)\s+(\d+)\s+(.+)$', line)
        if m:
            result["pages"].append({
                "page": m.group(1),
                "views": int(m.group(2)),
                "users": int(m.group(3)),
                "avg_time": m.group(4).strip(),
            })

    # Countries
    section = extract_section(seven_day, "TOP COUNTRIES")
    for line in section.split("\n"):
        m = _re.match(r'^\s*(.+?)\s{2,}(\d+)\s+(\d+)\s*$', line)
        if m and not line.strip().startswith("Country") and "---" not in line:
            name = m.group(1).strip() or "(unknown)"
            result["countries"].append({
                "country": name,
                "sessions": int(m.group(2)),
                "users": int(m.group(3)),
            })

    # Devices
    section = extract_section(seven_day, "DEVICES")
    for line in section.split("\n"):
        m = _re.match(r'^\s*(\w+)\s+(\d+)\s+(\d+)\s*$', line)
        if m and not line.strip().startswith("Device") and "---" not in line:
            result["devices"].append({
                "device": m.group(1),
                "sessions": int(m.group(2)),
                "users": int(m.group(3)),
            })

    # CTA clicks
    result["cta_clicks"] = 0
    result["cta_note"] = ""
    if "CTA CLICKS" in seven_day:
        cta_section = extract_section(seven_day, "CTA CLICKS")
        if "No CTA clicks" in cta_section:
            result["cta_note"] = "No CTA clicks recorded yet"
        else:
            for line in cta_section.split("\n"):
                m = _re.search(r'(\d+)\s+click', line)
                if m:
                    result["cta_clicks"] += int(m.group(1))

    # Pipeline status (from full report)
    if "PIPELINE STATUS" in text:
        ps = text.split("PIPELINE STATUS")[1]
        m = _re.search(r'Transcriptions:\s+(\d+)', ps)
        if m: result["pipeline"]["transcriptions"] = int(m.group(1))
        m = _re.search(r'Video pages:\s+(\d+)', ps)
        if m: result["pipeline"]["video_pages"] = int(m.group(1))
        m = _re.search(r'Article pages:\s+(\d+)', ps)
        if m: result["pipeline"]["article_pages"] = int(m.group(1))
        m = _re.search(r'Completed:\s+(\d+)/(\d+)', ps)
        if m:
            result["pipeline"]["completed"] = int(m.group(1))
            result["pipeline"]["total"] = int(m.group(2))

    # Pipeline errors
    pipeline_log = PROJECT_DIR / "transcriptions" / "pipeline.log"
    if pipeline_log.exists():
        log_text = pipeline_log.read_text()
        error_count = log_text.count("ERROR:")
        last_errors = []
        for line in log_text.split("\n"):
            if "ERROR:" in line:
                last_errors.append(line.strip())
        result["pipeline"]["errors"] = error_count
        result["pipeline"]["last_errors"] = last_errors[-5:]  # last 5 errors
        # Check completion line
        m = _re.search(r'Completed:\s+(\d+)/(\d+)\s*\|\s*Errors:\s+(\d+)', log_text)
        if m:
            result["pipeline"]["completed"] = int(m.group(1))
            result["pipeline"]["total"] = int(m.group(2))
            result["pipeline"]["error_count"] = int(m.group(3))
        # Check if pipeline is currently running
        m = _re.search(r'Pipeline finished (\d{4}-\d{2}-\d{2}T[\d:]+)', log_text)
        if m:
            result["pipeline"]["last_run"] = m.group(1)
    else:
        result["pipeline"]["errors"] = 0
        result["pipeline"]["last_errors"] = []

    return result


def get_system_health():
    """Check system health — API keys, services, cron jobs, etc."""
    import re as _re
    try:
        health = []
        secrets = pathlib.Path.home() / ".config" / "stv-secrets"

        # Resolution guides for each check
        fix_guides = {
            "OpenAI API Key": {
                "steps": [
                    "Go to platform.openai.com/api-keys",
                    "Create a new API key",
                    "Ask Claude to save it to the VPS secrets folder"
                ],
                "auto_fix": None
            },
            "YouTube Token": {
                "steps": [
                    "The YouTube OAuth token needs refreshing",
                    "Ask Claude to run the YouTube re-auth flow on the VPS",
                    "This will open a browser auth link you need to visit"
                ],
                "auto_fix": "reauth_youtube"
            },
            "Gmail Token": {
                "steps": [
                    "Gmail OAuth token is missing or expired",
                    "This is needed for reading reply emails in Outreach",
                    "Ask Claude to run the Gmail re-auth flow on the VPS",
                    "You will get a link to authorize Gmail access"
                ],
                "auto_fix": "reauth_gmail"
            },
            "Resend API Key": {
                "steps": [
                    "Go to resend.com/api-keys",
                    "Copy your API key",
                    "Ask Claude to save it to the VPS secrets folder"
                ],
                "auto_fix": None
            },
            "GA Service Account": {
                "steps": [
                    "The Google Analytics service account JSON is missing on the VPS",
                    "It exists on your Mac at ~/.config/stv-secrets/",
                    "Ask Claude to copy it from your Mac to the VPS"
                ],
                "auto_fix": "copy_ga_key"
            },
            "Transcription Pipeline": {
                "steps": [
                    "The transcription pipeline processes YouTube videos",
                    "If errors occurred, some videos failed to transcribe",
                    "Ask Claude to check the pipeline log and retry failed videos"
                ],
                "auto_fix": "retry_pipeline"
            },
            "Subtitle Uploads": {
                "steps": [
                    "YouTube subtitle uploads require OAuth re-authentication",
                    "The YouTube token needs the captions.force scope",
                    "Ask Claude to set up YouTube subtitle uploads on the VPS"
                ],
                "auto_fix": "reauth_youtube"
            },
        }

        # Check all secret files (simple file-exists checks, no heavy imports)
        checks = [
            ("OpenAI API Key", "openai-api-key.txt", True),
            ("YouTube Token", "youtube-token.pickle", False),
            ("Gmail Token", "gmail-token.pickle", False),
            ("Resend API Key", "resend-api-key.txt", True),
            ("GA Service Account", "ga-service-account.json", False),
        ]
        for name, filename, check_content in checks:
            fpath = secrets / filename
            guide = fix_guides.get(name, {})
            if fpath.exists():
                if check_content:
                    content = fpath.read_text().strip()
                    if len(content) > 10:
                        health.append({"name": name, "status": "ok", "detail": "Key loaded"})
                    else:
                        health.append({"name": name, "status": "error", "detail": "File looks empty/invalid", "fix": guide.get("steps", []), "auto_fix": guide.get("auto_fix")})
                else:
                    health.append({"name": name, "status": "ok", "detail": "File exists"})
            else:
                health.append({"name": name, "status": "error", "detail": f"Missing", "fix": guide.get("steps", []), "auto_fix": guide.get("auto_fix")})

        # Check pipeline log for recent errors
        pipeline_log = PROJECT_DIR / "transcriptions" / "pipeline.log"
        if pipeline_log.exists():
            log_text = pipeline_log.read_text()
            # Find the LAST completion line (most recent run)
            matches = list(_re.finditer(r'Completed:\s+(\d+)/(\d+)\s*\|\s*Errors:\s+(\d+)', log_text))
            if matches:
                m = matches[-1]
                completed, total, errors = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if errors > 0 and completed < total:
                    health.append({"name": "Transcription Pipeline", "status": "error", "detail": f"{errors} failures \u2014 {completed}/{total} complete", "fix": fix_guides.get("Transcription Pipeline", {}).get("steps", []), "auto_fix": "retry_pipeline"})
                else:
                    health.append({"name": "Transcription Pipeline", "status": "ok", "detail": f"{completed}/{total} complete"})
            else:
                # Pipeline might be running (no completion line yet)
                running_match = _re.findall(r'\[(\d+)/(\d+)\]', log_text)
                if running_match:
                    last = running_match[-1]
                    health.append({"name": "Transcription Pipeline", "status": "warning", "detail": f"Running... ({last[0]}/{last[1]})", "fix": ["Pipeline is currently running", "Check back in a few minutes for completion status"]})
                else:
                    health.append({"name": "Transcription Pipeline", "status": "ok", "detail": "Log exists"})
        else:
            health.append({"name": "Transcription Pipeline", "status": "warning", "detail": "No pipeline log found", "fix": ["The transcription pipeline hasn\u2019t been run yet", "Ask Claude to run the transcription pipeline on the VPS"]})

        # Check for status overrides (set by Claude when situations change)
        overrides_file = PROJECT_DIR / "data" / "status-overrides.json"
        overrides = {}
        if overrides_file.exists():
            try:
                overrides = json.loads(overrides_file.read_text())
            except Exception:
                pass

        # Check subtitle uploads
        subtitle_log = PROJECT_DIR / "reports" / "subtitle-uploads.json"
        if "Subtitle Uploads" in overrides:
            o = overrides["Subtitle Uploads"]
            health.append({"name": "Subtitle Uploads", "status": o.get("status", "warning"), "detail": o.get("detail", ""), "fix": o.get("fix", [])})
        elif subtitle_log.exists():
            data = json.loads(subtitle_log.read_text())
            total_uploads = sum(len(v) for v in data.values())
            health.append({"name": "Subtitle Uploads", "status": "ok" if total_uploads > 0 else "warning", "detail": f"{total_uploads} tracks uploaded"})
        else:
            health.append({"name": "Subtitle Uploads", "status": "warning", "detail": "Not started", "fix": fix_guides.get("Subtitle Uploads", {}).get("steps", []), "auto_fix": "reauth_youtube"})

        # Apply any additional status overrides
        for override_name, o in overrides.items():
            if override_name == "Subtitle Uploads":
                continue
            existing = [h for h in health if h["name"] == override_name]
            if existing:
                existing[0]["status"] = o.get("status", existing[0]["status"])
                existing[0]["detail"] = o.get("detail", existing[0]["detail"])
                if "fix" in o:
                    existing[0]["fix"] = o["fix"]
            else:
                health.append({"name": override_name, "status": o.get("status", "info"), "detail": o.get("detail", "")})

        return health
    except Exception as e:
        return [{"name": "Health Check", "status": "error", "detail": str(e)}]

    return health


def get_translation_coverage():
    """Check which pages exist in each language."""
    languages = {"es": "Spanish", "de": "German", "fr": "French", "pt": "Portuguese", "ar": "Arabic"}
    coverage = {}
    for code, name in languages.items():
        lang_dir = PROJECT_DIR / code
        count = 0
        if lang_dir.exists():
            count = sum(1 for _ in lang_dir.rglob("index.html"))
        coverage[code] = {"name": name, "count": count}
    en_pages = len(list(PROJECT_DIR.glob("*.html")))
    en_pages += sum(1 for _ in (PROJECT_DIR / "video").rglob("index.html")) if (PROJECT_DIR / "video").exists() else 0
    coverage["en"] = {"name": "English", "count": en_pages}
    return coverage


def get_backlinks():
    if BACKLINKS_FILE.exists():
        return json.loads(BACKLINKS_FILE.read_text())
    return []


def save_backlink(data):
    backlinks = get_backlinks()
    backlinks.append({
        "url": data.get("url", ""),
        "source": data.get("source", ""),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": data.get("type", ""),
    })
    BACKLINKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    BACKLINKS_FILE.write_text(json.dumps(backlinks, indent=2))
    return {"success": True, "count": len(backlinks)}


def get_content_tracker():
    if CONTENT_TRACKER_FILE.exists():
        return json.loads(CONTENT_TRACKER_FILE.read_text())
    return []


def save_content_item(data):
    items = get_content_tracker()
    items.append({
        "title": data.get("title", ""),
        "status": data.get("status", "idea"),
        "type": data.get("type", "article"),
    })
    CONTENT_TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTENT_TRACKER_FILE.write_text(json.dumps(items, indent=2))
    return {"success": True}


def update_content_status(index, new_status):
    items = get_content_tracker()
    if 0 <= index < len(items):
        items[index]["status"] = new_status
        CONTENT_TRACKER_FILE.write_text(json.dumps(items, indent=2))
        return {"success": True}
    return {"error": "Invalid index"}



# ─── Content Review Queue ───
REVIEW_QUEUE_FILE = PROJECT_DIR / "data" / "review-queue.json"
REVIEW_STAGING_DIR = PROJECT_DIR / "data" / "review-staging"


def get_review_queue():
    if REVIEW_QUEUE_FILE.exists():
        return json.loads(REVIEW_QUEUE_FILE.read_text())
    return []


def save_review_queue(queue):
    REVIEW_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def get_review_article(slug):
    article_path = REVIEW_STAGING_DIR / slug / "index.html"
    if article_path.exists():
        return article_path.read_text()
    return None


def save_review_article(slug, html):
    article_path = REVIEW_STAGING_DIR / slug / "index.html"
    article_path.parent.mkdir(parents=True, exist_ok=True)
    article_path.write_text(html)
    return {"success": True}


def publish_review_article(slug):
    """Copy article from staging to repo, git add/commit/push."""
    queue = get_review_queue()
    article = next((a for a in queue if a["slug"] == slug), None)
    if not article:
        return {"error": "Article not found in queue"}

    src = REVIEW_STAGING_DIR / slug
    dest = PROJECT_DIR / slug
    if not src.exists():
        return {"error": "Staging files not found"}

    # Copy files from staging to repo
    import shutil
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(str(src), str(dest))

    # Git add, commit, push
    title = article.get("title", slug)
    try:
        subprocess.run(["git", "add", slug + "/"], cwd=str(PROJECT_DIR), check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Publish: {title}"],
            cwd=str(PROJECT_DIR), check=True, capture_output=True
        )
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=str(PROJECT_DIR), check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        return {"error": f"Git failed: {e.stderr or e.stdout or str(e)}"}

    # Update queue status
    article["status"] = "published"
    article["published_date"] = datetime.now().strftime("%Y-%m-%d")
    save_review_queue(queue)
    return {"success": True, "message": f"Published: {title}"}


def get_preview_html(slug):
    """Get article HTML with paths rewritten for preview."""
    html = get_review_article(slug)
    if not html:
        return None
    # Rewrite relative CSS/JS paths to absolute URLs on live site
    html = html.replace('"../css/', '"https://socialtradingvlog.com/css/')
    html = html.replace('"../js/', '"https://socialtradingvlog.com/js/')
    html = html.replace('"../../css/', '"https://socialtradingvlog.com/css/')
    html = html.replace('"../../js/', '"https://socialtradingvlog.com/js/')
    html = html.replace("'../css/", "'https://socialtradingvlog.com/css/")
    html = html.replace("'../js/", "'https://socialtradingvlog.com/js/")
    return html



# ─── Auto-Fix Commands ───
def run_auto_fix(fix_id):
    """Run a predefined fix command for a known issue."""
    fixes = {
        "copy_ga_key": {
            "desc": "Copy GA service account from local backup",
            "cmd": None,  # Needs Mac access — cannot auto-fix from VPS
            "message": "This needs your Mac connected. Ask Claude in your next session: 'copy the GA service account to the VPS'"
        },
        "reauth_gmail": {
            "desc": "Re-authenticate Gmail OAuth",
            "cmd": None,
            "message": "Gmail re-auth requires a browser. Ask Claude: 'set up Gmail OAuth on the VPS' — you will get a link to visit."
        },
        "reauth_youtube": {
            "desc": "Re-authenticate YouTube OAuth",
            "cmd": None,
            "message": "YouTube re-auth requires a browser. Ask Claude: 'refresh the YouTube OAuth token on the VPS'"
        },
        "retry_pipeline": {
            "desc": "Retry failed transcriptions",
            "cmd": [sys.executable, "tools/run_pipeline.py", "--retry-failed"],
            "message": "Retrying failed transcriptions..."
        },
        "update_sitemap": {
            "desc": "Regenerate sitemap.xml",
            "cmd": [sys.executable, "tools/generate_sitemap.py"],
            "message": "Regenerating sitemap..."
        },
        "fix_broken_links": {
            "desc": "Scan and report broken links",
            "cmd": [sys.executable, "tools/broken_link_finder.py"],
            "message": "Scanning for broken links..."
        },
    }

    fix = fixes.get(fix_id)
    if not fix:
        return {"error": f"Unknown fix: {fix_id}"}

    if fix["cmd"] is None:
        # Cannot auto-fix — return instructions
        return {"success": False, "manual": True, "message": fix["message"]}

    # Run the command as a background task
    task_id = f"fix-{fix_id}-{datetime.now().strftime('%H%M%S')}"
    try:
        run_task(task_id, fix["cmd"])
        return {"success": True, "message": fix["message"], "task_id": task_id}
    except Exception as e:
        return {"error": str(e)}



# ─── SEO Checker ───
def analyze_seo(slug):
    """Analyze an article's SEO quality and return scores + suggestions."""
    import re as _re
    html = get_review_article(slug)
    if not html:
        return {"error": "Article not found"}

    results = {"score": 0, "max_score": 100, "checks": []}
    total = 0
    earned = 0

    # 1. Title tag
    title_match = _re.search(r'<title>(.*?)</title>', html, _re.IGNORECASE)
    title = title_match.group(1) if title_match else ""
    title_len = len(title)
    total += 10
    if 30 <= title_len <= 65:
        earned += 10
        results["checks"].append({"name": "Title length", "status": "pass", "detail": f"{title_len} chars (ideal: 30-65)"})
    elif title_len > 0:
        earned += 5
        results["checks"].append({"name": "Title length", "status": "warn", "detail": f"{title_len} chars (ideal: 30-65)"})
    else:
        results["checks"].append({"name": "Title length", "status": "fail", "detail": "Missing title tag"})

    # 2. Meta description
    meta_match = _re.search(r"<meta\s+name=.description.\s+content=.([^>]*?).", html, _re.IGNORECASE)
    meta_desc = meta_match.group(1) if meta_match else ""
    meta_len = len(meta_desc)
    total += 10
    if 120 <= meta_len <= 160:
        earned += 10
        results["checks"].append({"name": "Meta description", "status": "pass", "detail": f"{meta_len} chars (ideal: 120-160)"})
    elif meta_len > 0:
        earned += 5
        results["checks"].append({"name": "Meta description", "status": "warn", "detail": f"{meta_len} chars (ideal: 120-160)"})
    else:
        results["checks"].append({"name": "Meta description", "status": "fail", "detail": "Missing meta description"})

    # 3. H1 tag
    h1_matches = _re.findall(r'<h1[^>]*>(.*?)</h1>', html, _re.IGNORECASE | _re.DOTALL)
    total += 10
    if len(h1_matches) == 1:
        earned += 10
        results["checks"].append({"name": "H1 tag", "status": "pass", "detail": "Single H1 found"})
    elif len(h1_matches) > 1:
        earned += 5
        results["checks"].append({"name": "H1 tag", "status": "warn", "detail": f"{len(h1_matches)} H1 tags (should be 1)"})
    else:
        results["checks"].append({"name": "H1 tag", "status": "fail", "detail": "No H1 tag found"})

    # 4. Heading structure (H2s)
    h2_matches = _re.findall(r'<h2[^>]*>(.*?)</h2>', html, _re.IGNORECASE | _re.DOTALL)
    total += 10
    if len(h2_matches) >= 3:
        earned += 10
        results["checks"].append({"name": "H2 subheadings", "status": "pass", "detail": f"{len(h2_matches)} subheadings"})
    elif len(h2_matches) >= 1:
        earned += 5
        results["checks"].append({"name": "H2 subheadings", "status": "warn", "detail": f"{len(h2_matches)} subheadings (aim for 3+)"})
    else:
        results["checks"].append({"name": "H2 subheadings", "status": "fail", "detail": "No H2 subheadings"})

    # 5. Word count
    text = _re.sub(r'<script[^>]*>.*?</script>', '', html, flags=_re.DOTALL | _re.IGNORECASE)
    text = _re.sub(r'<style[^>]*>.*?</style>', '', text, flags=_re.DOTALL | _re.IGNORECASE)
    text = _re.sub(r'<[^>]+>', ' ', text)
    text = _re.sub(r'\s+', ' ', text).strip()
    word_count = len(text.split())
    reading_time = max(1, round(word_count / 250))
    total += 10
    if word_count >= 1500:
        earned += 10
        results["checks"].append({"name": "Word count", "status": "pass", "detail": f"{word_count:,} words ({reading_time} min read)"})
    elif word_count >= 800:
        earned += 7
        results["checks"].append({"name": "Word count", "status": "warn", "detail": f"{word_count:,} words ({reading_time} min read) — aim for 1500+"})
    else:
        earned += 3
        results["checks"].append({"name": "Word count", "status": "fail", "detail": f"{word_count:,} words ({reading_time} min read) — too short for SEO"})

    # 6. Internal links
    internal_links = _re.findall(r"href=.(/[^\s>]*?).", html)
    total += 10
    if len(internal_links) >= 5:
        earned += 10
        results["checks"].append({"name": "Internal links", "status": "pass", "detail": f"{len(internal_links)} internal links"})
    elif len(internal_links) >= 2:
        earned += 5
        results["checks"].append({"name": "Internal links", "status": "warn", "detail": f"{len(internal_links)} internal links (aim for 5+)"})
    else:
        results["checks"].append({"name": "Internal links", "status": "fail", "detail": f"{len(internal_links)} internal links — add more cross-links"})

    # 7. Schema markup
    schema_matches = _re.findall(r'application/ld\+json', html)
    total += 10
    if len(schema_matches) >= 2:
        earned += 10
        results["checks"].append({"name": "Schema markup", "status": "pass", "detail": f"{len(schema_matches)} schema blocks"})
    elif len(schema_matches) >= 1:
        earned += 7
        results["checks"].append({"name": "Schema markup", "status": "warn", "detail": f"{len(schema_matches)} schema block (add FAQPage + BreadcrumbList)"})
    else:
        results["checks"].append({"name": "Schema markup", "status": "fail", "detail": "No schema markup found"})

    # 8. Canonical URL
    canonical = _re.search(r"<link[^>]+rel=.canonical.", html, _re.IGNORECASE)
    total += 10
    if canonical:
        earned += 10
        results["checks"].append({"name": "Canonical URL", "status": "pass", "detail": "Canonical tag present"})
    else:
        results["checks"].append({"name": "Canonical URL", "status": "fail", "detail": "Missing canonical URL"})

    # 9. Image alt tags
    images = _re.findall(r'<img[^>]*>', html, _re.IGNORECASE)
    imgs_with_alt = [img for img in images if 'alt=' in img.lower() and 'alt=""' not in img.lower()]
    total += 10
    if len(images) == 0:
        earned += 5
        results["checks"].append({"name": "Image alt tags", "status": "warn", "detail": "No images found"})
    elif len(imgs_with_alt) == len(images):
        earned += 10
        results["checks"].append({"name": "Image alt tags", "status": "pass", "detail": f"All {len(images)} images have alt text"})
    else:
        missing = len(images) - len(imgs_with_alt)
        earned += 5
        results["checks"].append({"name": "Image alt tags", "status": "warn", "detail": f"{missing}/{len(images)} images missing alt text"})

    # 10. Risk disclaimer (required for finance)
    total += 10
    has_disclaimer = 'capital is at risk' in html.lower() or 'risk disclaimer' in html.lower() or '51% of retail' in html.lower()
    if has_disclaimer:
        earned += 10
        results["checks"].append({"name": "Risk disclaimer", "status": "pass", "detail": "Financial risk disclaimer present"})
    else:
        results["checks"].append({"name": "Risk disclaimer", "status": "fail", "detail": "Missing risk disclaimer (required for finance content)"})

    results["score"] = round((earned / total) * 100) if total > 0 else 0
    results["word_count"] = word_count
    results["reading_time"] = reading_time
    results["title"] = title
    results["meta_description"] = meta_desc
    return results

# ─── Goals / Growth Strategy ───
GOALS_FILE = PROJECT_DIR / "outreach" / "goals.json"


def get_goals():
    if GOALS_FILE.exists():
        return json.loads(GOALS_FILE.read_text())
    return []


def update_goal(goal_id, updates):
    goals = get_goals()
    for g in goals:
        if g["id"] == goal_id:
            for k, v in updates.items():
                if k in ("status", "progress", "notes"):
                    g[k] = v
            GOALS_FILE.write_text(json.dumps(goals, indent=2))
            return {"success": True}
    return {"error": "Goal not found"}


def toggle_goal_task(goal_id, task_index):
    goals = get_goals()
    for g in goals:
        if g["id"] == goal_id:
            if 0 <= task_index < len(g.get("tasks", [])):
                g["tasks"][task_index]["done"] = not g["tasks"][task_index]["done"]
                done_count = sum(1 for t in g["tasks"] if t["done"])
                g["progress"] = round((done_count / len(g["tasks"])) * 100)
                GOALS_FILE.write_text(json.dumps(goals, indent=2))
                return {"success": True, "done": g["tasks"][task_index]["done"], "progress": g["progress"]}
    return {"error": "Invalid goal or task"}


# ─── CTA A/B Testing ───
AB_TESTS_FILE = PROJECT_DIR / "outreach" / "ab-tests.json"


def get_ab_tests():
    if AB_TESTS_FILE.exists():
        return json.loads(AB_TESTS_FILE.read_text())
    return {"tests": [], "active_variant": "A"}


def save_ab_tests(data):
    AB_TESTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    AB_TESTS_FILE.write_text(json.dumps(data, indent=2))


def get_cta_stats():
    """Aggregate CTA click data from GA reports for A/B test tracking."""
    import re as _re
    reports = sorted(REPORTS_DIR.glob("daily-*.txt"))
    daily_clicks = []
    for r in reports[-30:]:
        date = r.stem.replace("daily-", "")
        text = r.read_text()
        clicks = 0
        if "CTA CLICKS" in text:
            for line in text.split("\n"):
                m = _re.search(r'(\d+)\s+click', line)
                if m:
                    clicks += int(m.group(1))
        daily_clicks.append({"date": date, "clicks": clicks})
    return daily_clicks


# ─── Page Speed ───
PAGESPEED_CACHE = PROJECT_DIR / "reports" / "pagespeed-cache.json"


def get_pagespeed():
    """Get cached PageSpeed scores or return empty."""
    if PAGESPEED_CACHE.exists():
        import time
        data = json.loads(PAGESPEED_CACHE.read_text())
        # Cache for 24 hours
        if time.time() - data.get("timestamp", 0) < 86400:
            return data
    return {"scores": {}, "timestamp": 0, "note": "No PageSpeed data cached. Run a scan from the dashboard."}


def run_pagespeed_check():
    """Fetch PageSpeed scores for the site. Returns results dict."""
    import urllib.request
    url = "https://socialtradingvlog.com"
    strategies = ["mobile", "desktop"]
    scores = {}
    for strategy in strategies:
        try:
            api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}"
            req = urllib.request.Request(api_url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                cats = result.get("lighthouseResult", {}).get("categories", {})
                scores[strategy] = {
                    "performance": round((cats.get("performance", {}).get("score", 0) or 0) * 100),
                    "accessibility": round((cats.get("accessibility", {}).get("score", 0) or 0) * 100),
                    "best_practices": round((cats.get("best-practices", {}).get("score", 0) or 0) * 100),
                    "seo": round((cats.get("seo", {}).get("score", 0) or 0) * 100),
                }
        except Exception as e:
            scores[strategy] = {"error": str(e)}
    import time
    data = {"scores": scores, "timestamp": time.time()}
    PAGESPEED_CACHE.parent.mkdir(parents=True, exist_ok=True)
    PAGESPEED_CACHE.write_text(json.dumps(data, indent=2))
    return data


# ─── Activity Feed ───
ACTIVITY_LOG = PROJECT_DIR / "outreach" / "activity-log.json"


def get_activity_feed():
    """Build activity feed from various sources."""
    activities = []

    # From sent emails
    if SENT_LOG.exists():
        for entry in json.loads(SENT_LOG.read_text()):
            activities.append({
                "type": "email",
                "text": f"Email sent to {entry.get('to', '?')}",
                "date": entry.get("sent_at", "")[:16],
                "icon": "mail",
            })

    # From follow-ups
    if FOLLOWUP_LOG.exists():
        for entry in json.loads(FOLLOWUP_LOG.read_text()):
            activities.append({
                "type": "followup",
                "text": f"Follow-up sent to {entry.get('to', '?')}",
                "date": entry.get("sent_at", "")[:16],
                "icon": "reply",
            })

    # From daily reports
    reports = sorted(REPORTS_DIR.glob("daily-*.txt"))
    for r in reports[-7:]:
        date = r.stem.replace("daily-", "")
        activities.append({
            "type": "report",
            "text": f"Daily GA report generated",
            "date": date + "T08:00",
            "icon": "chart",
        })

    # Custom activity log entries
    if ACTIVITY_LOG.exists():
        activities.extend(json.loads(ACTIVITY_LOG.read_text()))

    # Sort by date descending, take last 20
    activities.sort(key=lambda a: a.get("date", ""), reverse=True)
    return activities[:20]


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="STV Command">
<meta name="theme-color" content="#191B23">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon-192.png">
<title>STV Command Centre</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>
/* ─── Semrush-style Design Tokens (Light Theme) ─── */
:root {
  --bg-page: #F4F5F9;
  --bg-card: #FFFFFF;
  --bg-card-hover: #FFFFFF;
  --bg-input: #FFFFFF;
  --bg-table-header: #F4F5F9;
  --bg-table-hover: #F4F5F9;
  --bg-overlay: rgba(25, 27, 35, 0.7);
  --bg-reply: #F4F5F9;

  --border-primary: #E0E1E9;
  --border-secondary: #E0E1E9;
  --border-input: #C4C7CF;

  --text-primary: #191B23;
  --text-secondary: #6C6E79;
  --text-placeholder: #8A8E9B;
  --text-link: #006DCA;
  --text-invert: #FFFFFF;

  --brand: #FF642D;
  --brand-hover: #C33909;
  --brand-active: #8B1500;
  --info: #008FF8;
  --info-hover: #006DCA;
  --info-active: #044792;
  --success: #009F81;
  --success-text: #007C65;
  --success-bg: #CFF1EA;
  --critical: #FF4953;
  --critical-text: #D1002F;
  --critical-bg: #FFCEDC;
  --warning-text: #C33909;
  --warning-bg: #FFDDD2;
  --waiting-text: #C33909;
  --waiting-bg: #FEE6D1;

  --chart-1: #2BB3FF;
  --chart-2: #59DDAA;
  --chart-3: #FF642D;
  --chart-grid: #E0E1E9;
  --chart-axis-text: #6C6E79;

  --header-bg: #382E5E;
  --header-border: rgba(255,255,255,0.15);
  --header-text: #FFFFFF;
  --header-text-dim: rgba(255,255,255,0.6);
  --header-tab-active: #FFFFFF;
  --header-tab-hover: rgba(255,255,255,0.8);

  --shadow-card: 0px 0px 1px 0px rgba(25,27,35,0.16), 0px 1px 2px 0px rgba(25,27,35,0.12);
  --shadow-card-hover: 3px 3px 30px 0px rgba(25,27,35,0.15);
  --shadow-modal: 0px 3px 8px 0px rgba(25,27,35,0.2);
  --shadow-tooltip: 0px 1px 12px 0px rgba(25,27,35,0.15);
  --shadow-focus: 0px 0px 0px 3px rgba(0,143,248,0.5);

  --radius-sm: 6px;
  --radius-md: 6px;
  --radius-lg: 12px;
  --radius-pill: 24px;

  --toast-success-bg: #CFF1EA;
  --toast-success-text: #007C65;
  --toast-error-bg: #FFCEDC;
  --toast-error-text: #D1002F;

  --tag-gray-bg: #ECEDF0;
  --tag-gray-text: #6C6E79;
  --tag-blue-bg: #D0EEFF;
  --tag-blue-text: #006DCA;
  --tag-green-bg: #CFF1EA;
  --tag-green-text: #007C65;
  --tag-orange-bg: #FFDDD2;
  --tag-orange-text: #C33909;
  --tag-red-bg: #FFCEDC;
  --tag-red-text: #D1002F;

  --scrollbar-thumb: #C4C7CF;
  --scrollbar-track: transparent;
  --pre-text: #484A54;
}

/* ─── Dark Theme ─── */
[data-theme="dark"] {
  --bg-page: #0d1017;
  --bg-card: #191B23;
  --bg-card-hover: #1f2130;
  --bg-input: #12141c;
  --bg-table-header: #1f2130;
  --bg-table-hover: #1f2130;
  --bg-overlay: rgba(0,0,0,0.8);
  --bg-reply: #12141c;

  --border-primary: #2B2E38;
  --border-secondary: #2B2E38;
  --border-input: #3a3d4a;

  --text-primary: #F4F5F9;
  --text-secondary: #8A8E9B;
  --text-placeholder: #6C6E79;
  --text-link: #2BB3FF;
  --text-invert: #191B23;

  --brand: #FF642D;
  --brand-hover: #FF8C43;
  --brand-active: #FFB26E;
  --info: #2BB3FF;
  --info-hover: #8ECDFF;
  --info-active: #C4E5FE;
  --success: #59DDAA;
  --success-text: #59DDAA;
  --success-bg: rgba(89,221,170,0.15);
  --critical: #FF4953;
  --critical-text: #FF8786;
  --critical-bg: rgba(255,73,83,0.15);
  --warning-text: #FFB26E;
  --warning-bg: rgba(255,178,110,0.15);
  --waiting-text: #FDC23C;
  --waiting-bg: rgba(253,194,60,0.15);

  --chart-grid: #2B2E38;
  --chart-axis-text: #6C6E79;

  --header-bg: #282040;
  --header-border: rgba(255,255,255,0.1);

  --shadow-card: 0px 0px 1px 0px rgba(0,0,0,0.4), 0px 1px 3px 0px rgba(0,0,0,0.3);
  --shadow-card-hover: 0px 4px 20px 0px rgba(0,0,0,0.4);
  --shadow-modal: 0px 8px 32px 0px rgba(0,0,0,0.5);
  --shadow-tooltip: 0px 4px 16px 0px rgba(0,0,0,0.4);

  --toast-success-bg: rgba(89,221,170,0.15);
  --toast-success-text: #59DDAA;
  --toast-error-bg: rgba(255,73,83,0.15);
  --toast-error-text: #FF8786;

  --tag-gray-bg: #2B2E38;
  --tag-gray-text: #8A8E9B;
  --tag-blue-bg: rgba(43,179,255,0.15);
  --tag-blue-text: #2BB3FF;
  --tag-green-bg: rgba(89,221,170,0.15);
  --tag-green-text: #59DDAA;
  --tag-orange-bg: rgba(255,100,45,0.15);
  --tag-orange-text: #FFB26E;
  --tag-red-bg: rgba(255,73,83,0.15);
  --tag-red-text: #FF8786;

  --scrollbar-thumb: #3a3d4a;
  --scrollbar-track: transparent;
  --pre-text: #8A8E9B;
}

/* ─── Base ─── */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg-page); color: var(--text-primary); font-size: 14px; line-height: 1.42; transition: background 0.3s, color 0.3s; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--scrollbar-track); }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 3px; }

/* ─── Header (Semrush dusty violet) ─── */
.header { background: var(--header-bg); border-bottom: 1px solid var(--header-border); padding: 0 24px; display: flex; align-items: center; gap: 32px; position: sticky; top: 0; z-index: 100; height: 48px; }
.header-brand { display: flex; align-items: center; gap: 10px; }
.header-brand .logo { width: 28px; height: 28px; background: var(--brand); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; color: #fff; }
.header-brand h1 { font-size: 14px; font-weight: 600; color: var(--header-text); letter-spacing: -0.2px; }
.header-tabs { display: flex; gap: 0; height: 100%; }
.header-tab { padding: 0 16px; height: 100%; display: flex; align-items: center; cursor: pointer; font-size: 13px; font-weight: 500; color: var(--header-text-dim); border: none; background: none; transition: all 0.2s; border-bottom: 2px solid transparent; font-family: inherit; }
.header-tab:hover { color: var(--header-tab-hover); }
.header-tab.active { color: var(--header-tab-active); border-bottom-color: var(--header-tab-active); }
.header-actions { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.header-btn { padding: 6px 12px; border-radius: var(--radius-sm); background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15); color: var(--header-text-dim); cursor: pointer; font-size: 12px; font-weight: 500; font-family: inherit; transition: all 0.2s; }
.header-btn:hover { color: var(--header-text); background: rgba(255,255,255,0.15); }
.theme-toggle { width: 32px; height: 32px; border-radius: var(--radius-sm); background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15); color: var(--header-text-dim); cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.theme-toggle:hover { color: var(--header-text); background: rgba(255,255,255,0.15); }

/* ─── Layout ─── */
.container { max-width: 1200px; margin: 0 auto; padding: 24px; }
.section { display: none; animation: fadeIn 0.3s ease; }
.section.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

/* ─── Section Headers ─── */
.section-header { margin-bottom: 20px; }
.section-header h2 { font-size: 24px; font-weight: 600; color: var(--text-primary); line-height: 1.17; }
.section-header p { font-size: 14px; color: var(--text-secondary); margin-top: 4px; }

/* ─── Stat Cards (KPI widgets) ─── */
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--bg-card); border-radius: var(--radius-md); padding: 20px; box-shadow: var(--shadow-card); transition: box-shadow 0.2s; }
.stat-card:hover { box-shadow: var(--shadow-card-hover); }
.stat-card .label { font-size: 14px; color: var(--text-secondary); font-weight: 400; margin-bottom: 8px; }
.stat-card .value { font-size: 24px; font-weight: 600; color: var(--text-primary); line-height: 1.17; }
.stat-card .value.blue { color: var(--info); }
.stat-card .value.green { color: var(--success-text); }
.stat-card .value.orange { color: var(--waiting-text); }
.stat-card .value.red { color: var(--critical-text); }

/* ─── Cards ─── */
.card { background: var(--bg-card); border-radius: var(--radius-md); box-shadow: var(--shadow-card); margin-bottom: 16px; transition: box-shadow 0.2s; }
.card:hover { box-shadow: var(--shadow-card-hover); }
.card-header { padding: 16px 20px; border-bottom: 1px solid var(--border-primary); display: flex; align-items: center; justify-content: space-between; }
.card-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); line-height: 1.5; }
.card-body { padding: 20px; }
.card-body pre { font-size: 12px; line-height: 1.7; white-space: pre-wrap; word-wrap: break-word; color: var(--pre-text); font-family: 'SF Mono', 'JetBrains Mono', Menlo, monospace; max-height: 500px; overflow-y: auto; }

/* ─── Charts ─── */
.chart-container { height: 250px; position: relative; }
.chart-svg { width: 100%; height: 100%; }
.chart-empty { color: var(--text-secondary); text-align: center; padding: 60px; font-size: 13px; }

/* Chart tooltip (Semrush style) */
.chart-tooltip { position: fixed; pointer-events: none; background: var(--bg-card); border-radius: var(--radius-md); padding: 10px 14px; font-size: 12px; color: var(--text-primary); z-index: 800; opacity: 0; transition: opacity 0.15s ease; box-shadow: var(--shadow-tooltip); white-space: nowrap; }
.chart-tooltip.visible { opacity: 1; }
.chart-tooltip .tt-date { color: var(--text-secondary); font-size: 11px; font-weight: 700; margin-bottom: 2px; }
.chart-tooltip .tt-value { font-size: 18px; font-weight: 600; letter-spacing: -0.5px; }

/* ─── Tables ─── */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead th { text-align: left; padding: 10px 20px; font-size: 12px; color: var(--text-primary); font-weight: 700; background: var(--bg-table-header); border-bottom: 1px solid var(--border-primary); }
tbody td { padding: 12px 20px; font-size: 14px; color: var(--text-primary); border-bottom: 1px solid var(--border-primary); }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: var(--bg-table-hover); }
tbody tr.clickable { cursor: pointer; }

/* ─── Tags (pill-shaped, Semrush style) ─── */
.tag { display: inline-block; padding: 2px 10px; border-radius: var(--radius-pill); font-size: 12px; font-weight: 400; line-height: 1.33; }
.tag-green { background: var(--tag-green-bg); color: var(--tag-green-text); }
.tag-orange { background: var(--tag-orange-bg); color: var(--tag-orange-text); }
.tag-red { background: var(--tag-red-bg); color: var(--tag-red-text); }
.tag-blue { background: var(--tag-blue-bg); color: var(--tag-blue-text); }
.tag-gray { background: var(--tag-gray-bg); color: var(--tag-gray-text); }

/* ─── Draft List ─── */
.draft-list { display: grid; gap: 8px; margin-bottom: 20px; }
.draft-item { background: var(--bg-card); border-radius: var(--radius-md); padding: 16px 20px; cursor: pointer; box-shadow: var(--shadow-card); transition: box-shadow 0.2s, transform 0.2s; }
.draft-item:hover { box-shadow: var(--shadow-card-hover); transform: translateY(-1px); }
.draft-item.sent { opacity: 0.5; }
.draft-item h4 { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.draft-item .meta { font-size: 12px; color: var(--text-secondary); }
.draft-item .draft-badge { float: right; }

/* ─── Overlay / Modals ─── */
.overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: var(--bg-overlay); z-index: 900; justify-content: center; align-items: center; padding: 40px; }
.overlay.visible { display: flex; }
.modal { background: var(--bg-card); border-radius: var(--radius-lg); width: 100%; max-width: 720px; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-modal); }
.modal-header { padding: 16px 24px; border-bottom: 1px solid var(--border-primary); display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.modal-close { background: none; border: none; color: var(--text-secondary); font-size: 20px; cursor: pointer; padding: 4px 8px; border-radius: var(--radius-sm); font-family: inherit; transition: all 0.2s; }
.modal-close:hover { color: var(--text-primary); background: var(--bg-table-hover); }
.modal-body { padding: 24px; }
.modal-body label { display: block; font-size: 12px; color: var(--text-secondary); font-weight: 700; margin-bottom: 4px; margin-top: 16px; }
.modal-body label:first-child { margin-top: 0; }
.modal-body input, .modal-body textarea { width: 100%; padding: 10px 12px; background: var(--bg-input); border: 1px solid var(--border-input); border-radius: var(--radius-sm); color: var(--text-primary); font-size: 14px; font-family: 'Inter', sans-serif; transition: border-color 0.2s, box-shadow 0.2s; }
.modal-body input:focus, .modal-body textarea:focus { outline: none; border-color: var(--info); box-shadow: var(--shadow-focus); }
.modal-body textarea { min-height: 200px; resize: vertical; line-height: 1.7; }
.modal-actions { padding: 16px 24px; border-top: 1px solid var(--border-primary); display: flex; gap: 8px; justify-content: flex-end; }

/* Reply viewer */
.reply-content { background: var(--bg-reply); border: 1px solid var(--border-primary); border-radius: var(--radius-sm); padding: 16px; margin: 12px 0; }
.reply-meta { font-size: 12px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.8; }
.reply-meta strong { color: var(--text-primary); font-weight: 600; }
.reply-body-text { font-size: 14px; color: var(--text-primary); white-space: pre-wrap; line-height: 1.7; }
.reply-divider { border: none; border-top: 1px solid var(--border-primary); margin: 20px 0; }

/* ─── Buttons (Semrush style) ─── */
.btn { padding: 8px 16px; border-radius: var(--radius-sm); font-size: 14px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; font-family: 'Inter', sans-serif; height: 40px; display: inline-flex; align-items: center; }
.btn-primary { background: var(--brand); color: #FFFFFF; }
.btn-primary:hover { background: var(--brand-hover); }
.btn-primary:active { background: var(--brand-active); }
.btn-info { background: var(--info); color: #FFFFFF; }
.btn-info:hover { background: var(--info-hover); }
.btn-secondary { background: var(--bg-card); border: 1px solid var(--border-input); color: var(--text-primary); }
.btn-secondary:hover { background: var(--bg-table-hover); }
.btn-success { background: var(--success); color: #FFFFFF; }
.btn-success:hover { background: var(--success-text); }

/* ─── Toast ─── */
.toast { position: fixed; bottom: 24px; right: 24px; padding: 12px 20px; border-radius: var(--radius-md); font-size: 14px; font-weight: 500; z-index: 999; animation: slideUp 0.3s ease; box-shadow: var(--shadow-tooltip); }
.toast-success { background: var(--toast-success-bg); color: var(--toast-success-text); }
.toast-error { background: var(--toast-error-bg); color: var(--toast-error-text); }
@keyframes slideUp { from { transform: translateY(16px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

/* ─── Opportunity Digest ─── */
.opps-section {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  margin-bottom: 16px;
  border-left: 4px solid var(--border-primary);
  overflow: hidden;
}
.opps-section-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}
.opps-section-header:hover { background: var(--bg-table-hover); }
.opps-section-header h3 {
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}
.opps-section-header .source-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.opps-count-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  flex-shrink: 0;
}
.opps-count-badge .done-count { color: var(--success-text); }
.opps-count-badge .total-count { color: var(--text-secondary); }
.opps-progress {
  width: 60px;
  height: 6px;
  background: var(--border-primary);
  border-radius: 3px;
  overflow: hidden;
}
.opps-progress-fill {
  height: 100%;
  border-radius: 3px;
  background: var(--success);
  transition: width 0.3s;
}
.opps-chevron {
  font-size: 12px;
  color: var(--text-secondary);
  transition: transform 0.3s;
  margin-left: 8px;
}
.opps-section.collapsed .opps-chevron { transform: rotate(-90deg); }
.opps-section.collapsed .opps-items { display: none; }
.opps-items { border-top: 1px solid var(--border-primary); }
.opp-item {
  padding: 12px 20px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  border-bottom: 1px solid var(--border-primary);
  transition: background 0.15s;
}
.opp-item:last-child { border-bottom: none; }
.opp-item:hover { background: var(--bg-table-hover); }
.opp-item.done { opacity: 0.45; }
.opp-item.done .opp-title { text-decoration: line-through; }
.opp-check {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 2px solid var(--border-input);
  cursor: pointer;
  flex-shrink: 0;
  margin-top: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  background: var(--bg-card);
}
.opp-check:hover { border-color: var(--info); }
.opp-check.checked {
  background: var(--success);
  border-color: var(--success);
  color: #fff;
  font-size: 11px;
}
.opp-content { flex: 1; min-width: 0; }
.opp-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  line-height: 1.4;
}
.opp-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
  align-items: center;
}
.opp-meta .tag { font-size: 11px; padding: 1px 8px; }
.opp-snippet {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 4px;
}
.opp-angle {
  font-size: 12px;
  color: var(--info);
  font-weight: 500;
}
.opp-link-btn {
  flex-shrink: 0;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--info);
  background: none;
  border: 1px solid var(--info);
  border-radius: var(--radius-sm);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
  white-space: nowrap;
  align-self: center;
}
.opp-link-btn:hover { background: var(--info); color: #fff; }
.manual-sub {
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-primary);
}
.manual-sub:last-child { border-bottom: none; }
.manual-sub h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.manual-sub .note {
  font-size: 12px;
  color: var(--text-secondary);
  font-style: italic;
  margin-bottom: 6px;
}
.manual-links { display: flex; flex-wrap: wrap; gap: 6px; }
.manual-link {
  display: inline-block;
  padding: 4px 12px;
  background: var(--tag-blue-bg);
  color: var(--tag-blue-text);
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}
.manual-link:hover { background: var(--info); color: #fff; }
.rules-list { padding: 16px 20px; list-style: none; }
.rules-list li {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.7;
  padding: 4px 0 4px 24px;
  position: relative;
}
.rules-list li::before {
  content: attr(data-num);
  position: absolute;
  left: 0;
  color: var(--success-text);
  font-weight: 700;
  font-size: 13px;
}

/* ─── Trend Cards ─── */
.trend-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
.trend-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-card);
  transition: box-shadow 0.2s;
}
.trend-card:hover { box-shadow: var(--shadow-card-hover); }
.trend-card .trend-label { font-size: 13px; color: var(--text-secondary); font-weight: 500; margin-bottom: 8px; }
.trend-card .trend-value-row { display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px; }
.trend-card .trend-value { font-size: 28px; font-weight: 700; color: var(--text-primary); line-height: 1; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; }
.trend-card .trend-change {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 13px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-pill);
}
.trend-change.up { background: var(--tag-green-bg); color: var(--tag-green-text); }
.trend-change.down { background: var(--tag-red-bg); color: var(--tag-red-text); }
.trend-change.flat { background: var(--tag-gray-bg); color: var(--tag-gray-text); }
.trend-periods { display: flex; gap: 12px; margin-top: 8px; }
.trend-period { font-size: 11px; color: var(--text-secondary); }
.trend-period .period-val { font-weight: 600; }
.trend-period .period-val.up { color: var(--tag-green-text); }
.trend-period .period-val.down { color: var(--tag-red-text); }
.trend-sparkline { height: 32px; margin-top: 8px; }
.trend-sparkline svg { width: 100%; height: 100%; }

/* ─── Donut Chart ─── */
.donut-wrap { display: flex; align-items: center; gap: 24px; padding: 4px 0; }
.donut-svg { width: 140px; height: 140px; flex-shrink: 0; }
.donut-legend { display: flex; flex-direction: column; gap: 6px; }
.donut-legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.donut-legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.donut-legend-label { color: var(--text-secondary); }
.donut-legend-val { font-weight: 600; color: var(--text-primary); margin-left: auto; min-width: 24px; text-align: right; }

/* ─── Mini Table ─── */
.mini-table { width: 100%; border-collapse: collapse; }
.mini-table td { padding: 8px 12px; font-size: 13px; border-bottom: 1px solid var(--border-primary); }
.mini-table tr:last-child td { border-bottom: none; }
.mini-table tr:hover { background: var(--bg-table-hover); }
.mini-table .page-name { color: var(--text-link); font-weight: 500; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mini-table .num { text-align: right; font-weight: 600; color: var(--text-primary); }
.mini-table .dim { color: var(--text-secondary); text-align: right; }

/* ─── Device Bar ─── */
.device-bar-wrap { display: flex; flex-direction: column; gap: 10px; }
.device-row { display: flex; align-items: center; gap: 12px; }
.device-label { font-size: 13px; color: var(--text-primary); font-weight: 500; min-width: 70px; text-transform: capitalize; }
.device-bar-bg { flex: 1; height: 24px; background: var(--border-primary); border-radius: 4px; overflow: hidden; position: relative; }
.device-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; }
.device-bar-fill span { font-size: 11px; font-weight: 700; color: #fff; }
.device-bar-count { font-size: 13px; font-weight: 600; color: var(--text-primary); min-width: 30px; text-align: right; }

/* ─── Country List ─── */
.country-list { display: flex; flex-direction: column; gap: 4px; }
.country-row { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
.country-flag { font-size: 18px; width: 24px; text-align: center; }
.country-name { flex: 1; font-size: 13px; color: var(--text-primary); font-weight: 500; }
.country-val { font-size: 13px; font-weight: 600; color: var(--text-primary); }

/* ─── Funnel ─── */
.funnel-wrap { display: flex; align-items: flex-end; gap: 16px; padding: 12px 0; justify-content: center; }
.funnel-stage { display: flex; flex-direction: column; align-items: center; gap: 8px; flex: 1; max-width: 140px; }
.funnel-bar-wrap { width: 100%; display: flex; justify-content: center; }
.funnel-bar { border-radius: 6px 6px 0 0; transition: height 0.5s ease; min-height: 8px; }
.funnel-count { font-size: 24px; font-weight: 700; color: var(--text-primary); font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; }
.funnel-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; text-align: center; }
.funnel-arrow { color: var(--text-secondary); font-size: 18px; align-self: center; margin-bottom: 40px; }

/* ─── Pipeline Progress Bars ─── */
.pipeline-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.pipeline-item { background: var(--bg-card); border-radius: var(--radius-md); padding: 16px 20px; box-shadow: var(--shadow-card); }
.pipeline-item .pi-label { font-size: 13px; color: var(--text-secondary); font-weight: 500; margin-bottom: 8px; }
.pipeline-item .pi-value { font-size: 22px; font-weight: 700; color: var(--text-primary); font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; margin-bottom: 8px; }
.pipeline-item .pi-bar { height: 6px; background: var(--border-primary); border-radius: 3px; overflow: hidden; }
.pipeline-item .pi-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }

/* ─── Translation Grid ─── */
.lang-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 8px; }
.lang-card { background: var(--bg-card); border-radius: var(--radius-md); padding: 14px; text-align: center; box-shadow: var(--shadow-card); transition: box-shadow 0.2s; }
.lang-card:hover { box-shadow: var(--shadow-card-hover); }
.lang-card .lc-code { font-size: 22px; font-weight: 800; color: var(--text-primary); font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; text-transform: uppercase; }
.lang-card .lc-name { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }
.lang-card .lc-count { font-size: 13px; font-weight: 600; color: var(--info); margin-top: 6px; }

/* ─── Status Cards (traffic light system) ─── */
.status-card { border-radius: var(--radius-md); padding: 14px 18px; margin-bottom: 10px; }
.status-card .status-header { display: flex; align-items: center; gap: 10px; }
.status-card .status-name { font-size: 14px; font-weight: 700; }
.status-card .status-badge { font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 12px; margin-left: auto; white-space: nowrap; }
.status-card .status-detail { font-size: 13px; margin-top: 6px; line-height: 1.5; }
.status-card .status-steps { font-size: 12px; margin-top: 8px; line-height: 1.7; padding-left: 18px; }
.status-card .status-steps li { margin-bottom: 2px; }
/* Error — red, stuck, needs attention */
.status-card.status-error { background: #FEE2E2; border: 2px solid #EF4444; }
.status-card.status-error .status-name { color: #991B1B; }
.status-card.status-error .status-badge { background: #EF4444; color: #fff; }
.status-card.status-error .status-detail { color: #B91C1C; }
.status-card.status-error .status-steps { color: #991B1B; }
[data-theme="dark"] .status-card.status-error { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.4); }
[data-theme="dark"] .status-card.status-error .status-name { color: #FCA5A5; }
[data-theme="dark"] .status-card.status-error .status-badge { background: #DC2626; }
[data-theme="dark"] .status-card.status-error .status-detail { color: #FCA5A5; }
[data-theme="dark"] .status-card.status-error .status-steps { color: #FCA5A5; }
/* In progress — green border, fix underway */
.status-card.status-in-progress { background: #F0FDF4; border: 2px solid #22C55E; }
.status-card.status-in-progress .status-name { color: #166534; }
.status-card.status-in-progress .status-badge { background: #22C55E; color: #fff; }
.status-card.status-in-progress .status-detail { color: #15803D; }
.status-card.status-in-progress .status-steps { color: #166534; }
[data-theme="dark"] .status-card.status-in-progress { background: rgba(34,197,94,0.08); border-color: rgba(34,197,94,0.4); }
[data-theme="dark"] .status-card.status-in-progress .status-name { color: #86EFAC; }
[data-theme="dark"] .status-card.status-in-progress .status-badge { background: #16A34A; }
[data-theme="dark"] .status-card.status-in-progress .status-detail { color: #86EFAC; }
[data-theme="dark"] .status-card.status-in-progress .status-steps { color: #86EFAC; }
/* Warning — amber, needs review */
.status-card.status-warning { background: #FFFBEB; border: 2px solid #F59E0B; }
.status-card.status-warning .status-name { color: #92400E; }
.status-card.status-warning .status-badge { background: #F59E0B; color: #fff; }
.status-card.status-warning .status-detail { color: #B45309; }
.status-card.status-warning .status-steps { color: #92400E; }
[data-theme="dark"] .status-card.status-warning { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.4); }
[data-theme="dark"] .status-card.status-warning .status-name { color: #FCD34D; }
[data-theme="dark"] .status-card.status-warning .status-badge { background: #D97706; }
[data-theme="dark"] .status-card.status-warning .status-detail { color: #FCD34D; }
[data-theme="dark"] .status-card.status-warning .status-steps { color: #FCD34D; }
/* Info — blue, informational status */
.status-card.status-info { background: #EFF6FF; border: 2px solid #3B82F6; }
.status-card.status-info .status-name { color: #1E40AF; }
.status-card.status-info .status-badge { background: #3B82F6; color: #fff; }
.status-card.status-info .status-detail { color: #1D4ED8; }
.status-card.status-info .status-steps { color: #1E40AF; }
[data-theme="dark"] .status-card.status-info { background: rgba(59,130,246,0.08); border-color: rgba(59,130,246,0.4); }
[data-theme="dark"] .status-card.status-info .status-name { color: #93C5FD; }
[data-theme="dark"] .status-card.status-info .status-badge { background: #2563EB; }
[data-theme="dark"] .status-card.status-info .status-detail { color: #93C5FD; }
[data-theme="dark"] .status-card.status-info .status-steps { color: #93C5FD; }
/* OK items — compact row */
.health-ok-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; }
.health-ok-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--success); flex-shrink: 0; }
.health-ok-name { font-size: 12px; font-weight: 600; color: var(--text-primary); }
.health-ok-detail { font-size: 11px; color: var(--text-secondary); margin-left: auto; }

/* ─── Content Tracker ─── */
.content-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-primary); }
.content-item:last-child { border-bottom: none; }
.content-status { padding: 2px 10px; border-radius: var(--radius-pill); font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.content-status.idea { background: var(--tag-gray-bg); color: var(--tag-gray-text); }
.content-status.drafted { background: var(--tag-blue-bg); color: var(--tag-blue-text); }
.content-status.published { background: var(--tag-green-bg); color: var(--tag-green-text); }
.content-status.translated { background: var(--tag-orange-bg); color: var(--tag-orange-text); }
.content-title { flex: 1; font-size: 14px; color: var(--text-primary); font-weight: 500; }
.content-type { font-size: 12px; color: var(--text-secondary); }

/* ─── Backlink Mini ─── */
.backlink-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--border-primary); font-size: 13px; }
.backlink-item:last-child { border-bottom: none; }
.backlink-source { font-weight: 600; color: var(--text-primary); }
.backlink-url { color: var(--text-link); text-decoration: none; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.backlink-date { color: var(--text-secondary); font-size: 12px; flex-shrink: 0; }

/* ─── Two Column Grid ─── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
@media (max-width: 768px) { .two-col { grid-template-columns: 1fr; } .pipeline-grid { grid-template-columns: 1fr; } }

/* ─── Goal Cards ─── */
.goals-grid { display: flex; flex-direction: column; gap: 12px; }
.goal-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  transition: box-shadow 0.2s;
  border-left: 4px solid var(--info);
}
.goal-card:hover { box-shadow: var(--shadow-card-hover); }
.goal-card.cat-content { border-left-color: #2BB3FF; }
.goal-card.cat-seo { border-left-color: #59DDAA; }
.goal-card.cat-distribution { border-left-color: #FF642D; }
.goal-card.cat-monetization { border-left-color: #8B5CF6; }
.goal-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}
.goal-header:hover { background: var(--bg-table-hover); }
.goal-priority {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
  color: #fff;
  flex-shrink: 0;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.goal-info { flex: 1; min-width: 0; }
.goal-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  margin-bottom: 2px;
}
.goal-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.goal-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}
.goal-status-badge {
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.goal-status-badge.not_started { background: var(--tag-gray-bg); color: var(--tag-gray-text); }
.goal-status-badge.in_progress { background: var(--tag-blue-bg); color: var(--tag-blue-text); }
.goal-status-badge.blocked { background: var(--tag-red-bg); color: var(--tag-red-text); }
.goal-status-badge.completed { background: var(--tag-green-bg); color: var(--tag-green-text); }
.goal-progress-ring { width: 40px; height: 40px; }
.goal-chevron {
  font-size: 12px;
  color: var(--text-secondary);
  transition: transform 0.3s;
}
.goal-card.collapsed .goal-chevron { transform: rotate(-90deg); }
.goal-card.collapsed .goal-body { display: none; }
.goal-body {
  border-top: 1px solid var(--border-primary);
  padding: 16px 20px;
}
.goal-section-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 12px 0 8px 0;
}
.goal-section-title:first-child { margin-top: 0; }
.goal-rec {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.6;
  padding: 3px 0 3px 20px;
  position: relative;
}
.goal-rec::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 11px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--info);
}
.goal-task {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
  font-size: 13px;
  color: var(--text-primary);
}
.goal-task-check {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 2px solid var(--border-input);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
  font-size: 10px;
  background: var(--bg-card);
}
.goal-task-check:hover { border-color: var(--info); }
.goal-task-check.checked { background: var(--success); border-color: var(--success); color: #fff; }
.goal-task.done { opacity: 0.5; }
.goal-task.done .goal-task-text { text-decoration: line-through; }
.goal-notes-input {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  font-family: 'Inter', sans-serif;
  resize: vertical;
  min-height: 32px;
}
.goal-notes-input:focus { outline: none; border-color: var(--info); box-shadow: var(--shadow-focus); }
.goal-category-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.goal-filter-btn {
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--border-input);
  background: var(--bg-card);
  color: var(--text-secondary);
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}
.goal-filter-btn:hover { border-color: var(--info); color: var(--text-primary); }
.goal-filter-btn.active { background: var(--info); color: #fff; border-color: var(--info); }
.goal-summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 20px; }

/* ─── CTA A/B Testing ─── */
.ab-test-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  padding: 16px 20px;
  margin-bottom: 12px;
}
.ab-variant-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-primary);
}
.ab-variant-row:last-child { border-bottom: none; }
.ab-variant-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  min-width: 60px;
}
.ab-variant-bar { flex: 1; height: 28px; background: var(--border-primary); border-radius: 4px; overflow: hidden; position: relative; }
.ab-variant-fill { height: 100%; border-radius: 4px; display: flex; align-items: center; padding: 0 10px; transition: width 0.5s ease; }
.ab-variant-fill span { font-size: 11px; font-weight: 700; color: #fff; }
.ab-winner { color: var(--success-text); font-weight: 700; font-size: 12px; }

/* ─── Activity Feed ─── */
.activity-feed { display: flex; flex-direction: column; gap: 0; }
.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-primary);
  font-size: 13px;
}
.activity-item:last-child { border-bottom: none; }
.activity-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
  margin-top: 1px;
}
.activity-icon.mail { background: var(--tag-blue-bg); color: var(--tag-blue-text); }
.activity-icon.reply { background: var(--tag-green-bg); color: var(--tag-green-text); }
.activity-icon.chart { background: var(--tag-orange-bg); color: var(--tag-orange-text); }
.activity-icon.scan { background: var(--tag-gray-bg); color: var(--tag-gray-text); }
.activity-text { flex: 1; color: var(--text-primary); line-height: 1.4; }
.activity-date { font-size: 11px; color: var(--text-secondary); white-space: nowrap; flex-shrink: 0; }

/* ─── Page Speed Gauges ─── */
.speed-gauges { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 12px; }
.speed-gauge { text-align: center; }
.speed-gauge svg { width: 80px; height: 80px; }
.speed-gauge .gauge-label { font-size: 12px; color: var(--text-secondary); margin-top: 6px; font-weight: 500; }
.speed-gauge .gauge-score { font-size: 20px; font-weight: 700; font-family: 'Plus Jakarta Sans', sans-serif; }

/* ─── Config Placeholder ─── */
.config-placeholder {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}
.config-placeholder h4 {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.config-placeholder p { font-size: 13px; line-height: 1.6; }
.config-placeholder code { background: var(--bg-table-header); padding: 2px 6px; border-radius: 3px; font-size: 12px; }

/* ─── Responsive ─── */
@media (max-width: 768px) {
  .header { padding: 0 16px; flex-wrap: wrap; height: auto; padding-top: 10px; padding-bottom: 10px; gap: 8px; }
  .header-tabs { flex-wrap: wrap; height: auto; }
  .header-tab { height: 36px; font-size: 12px; padding: 0 10px; }
  .container { padding: 16px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .overlay { padding: 16px; }
  .modal { max-width: 100%; }
  table { font-size: 12px; }
  thead th, tbody td { padding: 8px 12px; }
}
@media (max-width: 480px) {
  .stats-row { grid-template-columns: 1fr; }
  .header-brand h1 { display: none; }
}

/* ─── Login Screen ─── */
.login-screen { display:flex; align-items:center; justify-content:center; min-height:100vh; background:var(--bg-page); }
.login-box { background:var(--bg-card); padding:40px; border-radius:12px; box-shadow:var(--shadow-card); width:100%; max-width:360px; text-align:center; }
.login-box h2 { font-family:'Plus Jakarta Sans',sans-serif; font-weight:800; font-size:24px; margin-bottom:8px; color:var(--text-primary); }
.login-box p { color:var(--text-secondary); font-size:14px; margin-bottom:24px; }
.login-box input { width:100%; padding:12px 16px; border:1px solid var(--border-input); border-radius:6px; font-size:16px; background:var(--bg-input); color:var(--text-primary); margin-bottom:16px; box-sizing:border-box; }
.login-box button { width:100%; padding:12px; background:var(--brand); color:#fff; border:none; border-radius:6px; font-size:16px; font-weight:600; cursor:pointer; }
.login-box button:hover { background:var(--brand-hover); }
.login-error { color:var(--critical); font-size:13px; margin-top:8px; display:none; }

/* ─── Automation Tab ─── */
.auto-actions { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
@media (max-width:768px) { .auto-actions { grid-template-columns:repeat(2,1fr); } }
@media (max-width:480px) { .auto-actions { grid-template-columns:1fr; } }
.auto-btn { display:flex; align-items:center; gap:12px; padding:16px; border:1px solid var(--border-primary); border-radius:8px; background:var(--bg-card); cursor:pointer; transition:all 0.2s; text-align:left; }
.auto-btn:hover { transform:translateY(-2px); box-shadow:var(--shadow-card-hover); }
.auto-btn-icon { font-size:24px; width:40px; height:40px; display:flex; align-items:center; justify-content:center; border-radius:8px; flex-shrink:0; }
.auto-btn-text { display:flex; flex-direction:column; gap:2px; }
.auto-btn-text strong { font-size:14px; color:var(--text-primary); }
.auto-btn-text small { font-size:12px; color:var(--text-secondary); }
.auto-btn-primary .auto-btn-icon { background:#E8F4FD; color:var(--info); }
.auto-btn-info .auto-btn-icon { background:#E0F7FA; color:#00ACC1; }
.auto-btn-success .auto-btn-icon { background:var(--success-bg); color:var(--success); }
.auto-btn-warning .auto-btn-icon { background:var(--warning-bg); color:var(--brand); }
.auto-btn-purple .auto-btn-icon { background:#EDE7F6; color:#8B5CF6; }
.auto-btn-secondary .auto-btn-icon { background:var(--bg-table-header); color:var(--text-secondary); }
.auto-btn:active { transform:translateY(0); }
.auto-btn.running { border-color:var(--info); background:rgba(0,143,248,0.05); }
.auto-btn.running .auto-btn-icon { animation:pulse 1.5s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }

.auto-badge { background:var(--info); color:#fff; font-size:12px; font-weight:600; padding:2px 8px; border-radius:10px; margin-left:8px; }
.auto-badge:empty { display:none; }

.auto-log-viewer { background:var(--bg-page); border:1px solid var(--border-primary); border-radius:6px; padding:16px; font-family:'SF Mono',Monaco,Consolas,monospace; font-size:12px; line-height:1.6; max-height:400px; overflow-y:auto; white-space:pre-wrap; word-break:break-all; color:var(--text-primary); }

.auto-task-item { display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border:1px solid var(--border-primary); border-radius:6px; margin-bottom:8px; }
.auto-task-item:last-child { margin-bottom:0; }
.auto-task-name { font-weight:600; font-size:14px; color:var(--text-primary); }
.auto-task-meta { font-size:12px; color:var(--text-secondary); }
.auto-task-status { font-size:12px; font-weight:600; padding:4px 10px; border-radius:4px; }
.auto-task-status.running { background:rgba(0,143,248,0.1); color:var(--info); }
.auto-task-status.completed { background:var(--success-bg); color:var(--success-text); }
.auto-task-status.failed { background:var(--critical-bg); color:var(--critical-text); }

/* ─── PWA install prompt ─── */
.pwa-install-banner { display:none; position:fixed; bottom:16px; left:16px; right:16px; background:var(--bg-card); border:1px solid var(--border-primary); border-radius:12px; padding:16px; box-shadow:0 4px 24px rgba(0,0,0,0.15); z-index:1000; text-align:center; }
.pwa-install-banner button { margin:8px 4px 0; padding:8px 20px; border-radius:6px; font-weight:600; cursor:pointer; }
.pwa-install-banner .pwa-install-btn { background:var(--brand); color:#fff; border:none; }
.pwa-install-banner .pwa-dismiss-btn { background:transparent; color:var(--text-secondary); border:1px solid var(--border-primary); }
</style>
</head>
<body>

<header class="header">
  <div class="header-brand">
    <div class="logo">S</div>
    <h1>SocialTradingVlog</h1>
  </div>
  <nav class="header-tabs">
    <button class="header-tab active" data-section="overview">Overview</button>
    <button class="header-tab" data-section="traffic">Traffic</button>
    <button class="header-tab" data-section="outreach">Outreach</button>
    <button class="header-tab" data-section="seo">SEO & Links</button>
    <button class="header-tab" data-section="growth">Growth</button>
    <button class="header-tab" data-section="automation">Automation</button>
    <button class="header-tab" data-section="performance">Performance</button>
    <button class="header-tab" data-section="review">Review</button>
  </nav>
  <div class="header-actions">
    <button class="header-btn" onclick="loadAll()">Refresh</button>
    <button class="header-btn" id="faceid-setup-btn" style="display:none;background:var(--info);color:white;" onclick="registerPasskey()">Set up Face ID</button>
    <button class="header-btn" id="trust-device-btn" style="display:none;" onclick="trustDevice()">Trust Device</button>
    <button class="theme-toggle" onclick="toggleTheme()" id="theme-btn" title="Toggle dark mode">&#9789;</button>
  </div>
</header>

<div class="container">

  <!-- OVERVIEW -->
  <div id="overview" class="section active">
    <div id="system-alerts"></div>
    <div class="section-header"><h2>Overview</h2><p>Everything at a glance</p></div>
    <div class="stats-row" id="overview-stats"></div>
    <div class="section-header" style="margin-top:8px"><h2 style="font-size:18px">Content Pipeline</h2></div>
    <div class="pipeline-grid" id="overview-pipeline"></div>
    <div id="system-health" style="margin-top:16px;margin-bottom:16px"></div>
    <div class="section-header" style="margin-top:20px"><h2 style="font-size:18px">Translation Coverage</h2></div>
    <div class="lang-grid" id="overview-translations"></div>
    <div class="two-col" style="margin-top:20px">
      <div class="card"><div class="card-header"><h3>Activity Feed</h3></div><div class="card-body"><div id="overview-activity">Loading...</div></div></div>
      <div class="card"><div class="card-header"><h3>CTA Clicks</h3></div><div class="card-body"><div id="overview-cta">Loading...</div></div></div>
    </div>
    <div class="card" style="margin-top:4px"><div class="card-header"><h3>Latest Analytics Report</h3></div><div class="card-body"><pre id="overview-ga">Loading...</pre></div></div>
  </div>

  <!-- TRAFFIC -->
  <div id="traffic" class="section">
    <div class="section-header"><h2>Website Traffic</h2><p>Google Analytics data and trends</p></div>
    <div class="trend-cards" id="trend-cards"></div>
    <div class="two-col">
      <div class="card"><div class="card-header"><h3>Traffic Sources</h3></div><div class="card-body"><div id="traffic-sources"><div class="chart-empty">Loading...</div></div></div></div>
      <div class="card"><div class="card-header"><h3>Devices</h3></div><div class="card-body"><div id="traffic-devices"><div class="chart-empty">Loading...</div></div></div></div>
    </div>
    <div class="two-col">
      <div class="card"><div class="card-header"><h3>Top Pages</h3></div><div class="card-body"><div id="traffic-pages">Loading...</div></div></div>
      <div class="card"><div class="card-header"><h3>Top Countries</h3></div><div class="card-body"><div id="traffic-countries">Loading...</div></div></div>
    </div>
    <div class="card"><div class="card-header"><h3>Sessions (7-day rolling)</h3></div><div class="card-body"><div class="chart-container" id="sessions-chart"></div></div></div>
    <div class="card"><div class="card-header"><h3>Users (7-day rolling)</h3></div><div class="card-body"><div class="chart-container" id="users-chart"></div></div></div>
    <div class="card"><div class="card-header"><h3>Full Report</h3></div><div class="card-body"><pre id="traffic-report">Loading...</pre></div></div>
  </div>

  <!-- OUTREACH -->
  <div id="outreach" class="section">
    <div class="section-header"><h2>Email Outreach</h2><p>Track pitches, replies, and manage drafts</p></div>
    <div id="outreach-alert"></div>
    <div class="two-col">
      <div><div class="stats-row" id="outreach-stats"></div></div>
      <div class="card"><div class="card-header"><h3>Outreach Funnel</h3></div><div class="card-body"><div id="outreach-funnel"></div></div></div>
    </div>
    <div class="card">
      <div class="card-header"><h3>Sent Emails</h3></div>
      <div class="table-wrap">
        <table><thead><tr><th>To</th><th>Subject</th><th>Sent</th><th>Status</th></tr></thead><tbody id="outreach-table"></tbody></table>
      </div>
    </div>
    <div class="section-header" style="margin-top:24px"><h2>Drafts</h2><p>Click to edit and send</p></div>
    <div class="draft-list" id="draft-list"></div>
    <button class="btn btn-secondary" onclick="openNewDraft()">+ New Draft</button>
  </div>

  <!-- SEO -->
  <div id="seo" class="section">
    <div class="section-header"><h2>SEO & Link Building</h2><p>Opportunities and competitive analysis</p></div>
    <div class="stats-row" id="opps-stats"></div>
    <div id="opps-sections"></div>
    <div class="two-col" style="margin-top:16px">
      <div class="card"><div class="card-header"><h3>Backlinks</h3><button class="btn btn-secondary" style="height:32px;font-size:12px;padding:0 12px" onclick="openAddBacklink()">+ Add</button></div><div class="card-body"><div id="seo-backlinks">No backlinks tracked yet</div></div></div>
      <div class="card"><div class="card-header"><h3>Content Tracker</h3><button class="btn btn-secondary" style="height:32px;font-size:12px;padding:0 12px" onclick="openAddContent()">+ Add</button></div><div class="card-body"><div id="seo-content">Loading...</div></div></div>
    </div>
    <div class="card" style="margin-top:8px"><div class="card-header"><h3>Broken Link Report</h3></div><div class="card-body"><pre id="seo-broken-links">Loading...</pre></div></div>
  </div>

  <!-- GROWTH STRATEGY -->
  <div id="growth" class="section">
    <div class="section-header">
      <h2>Growth Strategy</h2>
      <p>9 strategic priorities to grow traffic, backlinks, and affiliate revenue</p>
    </div>
    <div class="goal-summary-cards" id="goal-summary"></div>
    <div class="goal-category-filters" id="goal-filters">
      <button class="goal-filter-btn active" data-cat="all" onclick="filterGoals('all',this)">All</button>
      <button class="goal-filter-btn" data-cat="content" onclick="filterGoals('content',this)">Content</button>
      <button class="goal-filter-btn" data-cat="seo" onclick="filterGoals('seo',this)">SEO</button>
      <button class="goal-filter-btn" data-cat="distribution" onclick="filterGoals('distribution',this)">Distribution</button>
      <button class="goal-filter-btn" data-cat="monetization" onclick="filterGoals('monetization',this)">Monetisation</button>
    </div>
    <div class="goals-grid" id="goals-list"></div>
  </div>

  <!-- AUTOMATION -->
  <div id="automation" class="section">
    <div class="section-header">
      <h2>Automation & Tasks</h2>
      <p>Run pipeline tasks, view logs, and monitor your VPS</p>
    </div>

    <!-- Status cards -->
    <div class="stats-row" id="auto-stats"></div>

    <!-- Quick Actions -->
    <div class="card" style="margin-top:8px">
      <div class="card-header"><h3>Quick Actions</h3></div>
      <div class="card-body">
        <div class="auto-actions">
          <button class="auto-btn auto-btn-primary" onclick="runAction('pipeline','Run Translation Pipeline','translate-pipeline')">
            <span class="auto-btn-icon">&#9654;</span>
            <span class="auto-btn-text">
              <strong>Run Pipeline</strong>
              <small>Translate + upload subtitles</small>
            </span>
          </button>
          <button class="auto-btn auto-btn-info" onclick="runAction('sync','Sync From Mac','sync-from-mac')">
            <span class="auto-btn-icon">&#8635;</span>
            <span class="auto-btn-text">
              <strong>Sync From Mac</strong>
              <small>Pull latest transcriptions</small>
            </span>
          </button>
          <button class="auto-btn auto-btn-success" onclick="runAction('transcribe','Transcribe New Videos','transcribe-batch')">
            <span class="auto-btn-icon">&#127908;</span>
            <span class="auto-btn-text">
              <strong>Transcribe Batch</strong>
              <small>Download + Whisper API</small>
            </span>
          </button>
          <button class="auto-btn auto-btn-warning" onclick="runAction('opportunities','Scan Opportunities','scan-opps')">
            <span class="auto-btn-icon">&#128269;</span>
            <span class="auto-btn-text">
              <strong>Scan Opportunities</strong>
              <small>Find link-building targets</small>
            </span>
          </button>
          <button class="auto-btn auto-btn-purple" onclick="runAction('ga-report','Generate GA Report','ga-report')">
            <span class="auto-btn-icon">&#128200;</span>
            <span class="auto-btn-text">
              <strong>GA Report</strong>
              <small>Pull latest analytics</small>
            </span>
          </button>
          <button class="auto-btn auto-btn-secondary" onclick="openCustomCommand()">
            <span class="auto-btn-icon">&#9881;</span>
            <span class="auto-btn-text">
              <strong>Custom Command</strong>
              <small>Run any shell command</small>
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Running Tasks -->
    <div class="card" style="margin-top:8px">
      <div class="card-header"><h3>Running Tasks</h3><span class="auto-badge" id="running-count">0</span></div>
      <div class="card-body" id="auto-running">
        <div class="chart-empty">No tasks running</div>
      </div>
    </div>

    <!-- Live Log Viewer -->
    <div class="card" style="margin-top:8px">
      <div class="card-header">
        <h3>Log Viewer</h3>
        <select id="log-select" onchange="loadTaskLog(this.value)" style="background:var(--bg-input);border:1px solid var(--border-input);border-radius:4px;padding:4px 8px;font-size:13px;color:var(--text-primary)">
          <option value="">Select a task...</option>
        </select>
      </div>
      <div class="card-body">
        <pre id="auto-log" class="auto-log-viewer">Select a task to view its log output...</pre>
      </div>
    </div>

    <!-- Task History -->
    <div class="card" style="margin-top:8px">
      <div class="card-header"><h3>Recent Tasks</h3></div>
      <div class="card-body" id="auto-history">
        <div class="chart-empty">No completed tasks yet</div>
      </div>
    </div>
  </div>

  <!-- Custom command modal -->
  <div class="overlay" id="cmd-overlay">
    <div class="modal">
      <div class="modal-header"><h3>Run Custom Command</h3><button class="modal-close" onclick="closeCmdModal()">&times;</button></div>
      <div class="modal-body">
        <label>Task Name</label><input type="text" id="cmd-name" placeholder="e.g. Fix broken links">
        <label>Command</label><textarea id="cmd-input" placeholder="e.g. python3 tools/broken_link_finder.py" style="font-family:monospace;font-size:13px;min-height:80px"></textarea>
      </div>
      <div class="modal-actions">
        <button class="btn btn-secondary" onclick="closeCmdModal()">Cancel</button>
        <button class="btn btn-primary" onclick="runCustomCommand()">Run</button>
      </div>
    </div>
  </div>

  <!-- PERFORMANCE -->
  <div id="performance" class="section">
    <div class="section-header">
      <h2>Performance & Integrations</h2>
      <p>Page speed, CTA testing, YouTube stats, and Search Console</p>
    </div>
    <div class="two-col">
      <div class="card">
        <div class="card-header"><h3>Page Speed — Mobile</h3><button class="btn btn-secondary" style="height:32px;font-size:12px;padding:0 12px" onclick="runPageSpeed()">Scan Now</button></div>
        <div class="card-body"><div id="speed-mobile" class="speed-gauges"><div class="chart-empty">No scan yet. Click "Scan Now".</div></div></div>
      </div>
      <div class="card">
        <div class="card-header"><h3>Page Speed — Desktop</h3></div>
        <div class="card-body"><div id="speed-desktop" class="speed-gauges"><div class="chart-empty">No scan yet.</div></div></div>
      </div>
    </div>
    <div class="card">
      <div class="card-header"><h3>CTA A/B Testing</h3></div>
      <div class="card-body"><div id="perf-cta">
        <div class="config-placeholder">
          <h4>CTA Split Testing</h4>
          <p>Tracks different CTA variants across your site pages.<br>Click data populates as GA reports accumulate.</p>
        </div>
        <div id="cta-test-results"></div>
        <div id="cta-click-chart" style="margin-top:16px"></div>
      </div></div>
    </div>
    <div class="two-col">
      <div class="card">
        <div class="card-header"><h3>YouTube Stats</h3></div>
        <div class="card-body"><div id="perf-youtube">
          <div class="config-placeholder">
            <h4>YouTube Integration</h4>
            <p>YouTube OAuth credentials detected. Needs API quota to fetch channel stats.<br>Shows: subscribers, views, latest video performance.</p>
          </div>
        </div></div>
      </div>
      <div class="card">
        <div class="card-header"><h3>Search Console</h3></div>
        <div class="card-body"><div id="perf-gsc">
          <div class="config-placeholder">
            <h4>Search Console — Not Configured</h4>
            <p>Gmail credentials have <code>gmail.readonly</code> scope only.<br>To enable, add <code>webmasters.readonly</code> scope to your OAuth consent screen and re-authenticate.</p>
          </div>
        </div></div>
      </div>
    </div>
  </div>

</div>


  <div id="review" class="section">
    <div class="section-header">
      <h2>Content Review Queue</h2>
      <p>Review, edit, and publish articles to the live site</p>
    </div>
    <div class="review-layout" style="display:grid;grid-template-columns:320px 1fr;gap:16px;min-height:600px;">
      <div class="card" style="overflow-y:auto;max-height:80vh;">
        <div class="card-header"><h3>Articles</h3><span id="review-count" class="badge" style="background:var(--warning-bg);color:var(--warning-text);padding:2px 8px;border-radius:12px;font-size:12px;"></span></div>
        <div class="card-body" id="review-list" style="padding:0;">
          <div class="chart-empty">Loading...</div>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div class="card" style="flex:1;min-height:0;">
          <div class="card-header">
            <h3 id="review-article-title">Select an article</h3>
            <div id="review-actions" style="display:none;gap:8px;display:flex;">
              <button class="btn btn-secondary" style="height:32px;font-size:12px;padding:0 12px" onclick="saveReviewDraft()">Save Draft</button>
              <button class="btn btn-primary" style="height:32px;font-size:12px;padding:0 12px" onclick="publishArticle()">Publish to Live Site</button>
            </div>
          </div>
          <div class="card-body" style="padding:0;display:flex;flex-direction:column;min-height:400px;">
            <div id="review-empty" style="padding:40px;text-align:center;color:var(--text-secondary);">
              <p>Select an article from the list to preview and edit it.</p>
            </div>
            <div id="review-split" style="display:none;flex:1;min-height:0;">
              <div style="display:flex;border-bottom:1px solid var(--border-primary);padding:4px 12px;gap:8px;background:var(--bg-table-header);">
                <button class="review-view-btn active" data-view="preview" style="border:none;background:none;padding:4px 12px;cursor:pointer;font-size:13px;font-weight:500;border-radius:6px;">Preview</button>
                <button class="review-view-btn" data-view="code" style="border:none;background:none;padding:4px 12px;cursor:pointer;font-size:13px;font-weight:500;border-radius:6px;">Edit HTML</button>
                <button class="review-view-btn" data-view="split" style="border:none;background:none;padding:4px 12px;cursor:pointer;font-size:13px;font-weight:500;border-radius:6px;">Split View</button>
              </div>
              <div id="review-preview-pane" style="flex:1;min-height:400px;">
                <iframe id="review-iframe" style="width:100%;height:100%;border:none;min-height:500px;" sandbox="allow-same-origin allow-scripts"></iframe>
              </div>
              <div id="review-code-pane" style="display:none;flex:1;min-height:400px;">
                <textarea id="review-editor" style="width:100%;height:100%;min-height:500px;font-family:monospace;font-size:13px;padding:12px;border:none;resize:none;background:var(--bg-input);color:var(--text-primary);"></textarea>
              </div>
              <div id="review-split-pane" style="display:none;flex:1;min-height:400px;">
                <div style="display:grid;grid-template-columns:1fr 1fr;height:100%;min-height:500px;">
                  <iframe id="review-iframe-split" style="width:100%;height:100%;border:none;border-right:1px solid var(--border-primary);" sandbox="allow-same-origin allow-scripts"></iframe>
                  <textarea id="review-editor-split" style="width:100%;height:100%;font-family:monospace;font-size:12px;padding:12px;border:none;resize:none;background:var(--bg-input);color:var(--text-primary);"></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="card" id="review-seo-card" style="display:none;">
          <div class="card-header"><h3>SEO Score</h3><span id="seo-score-badge" style="font-size:18px;font-weight:700;font-family:Plus Jakarta Sans,sans-serif;"></span></div>
          <div class="card-body" id="seo-results" style="padding:8px 16px;">
            <div class="chart-empty">Select an article to see SEO analysis</div>
          </div>
        </div>
        <div class="card" id="review-notes-card" style="display:none;">
          <div class="card-header"><h3>Review Notes</h3></div>
          <div class="card-body">
            <textarea id="review-notes" rows="3" style="width:100%;font-size:13px;padding:8px;border:1px solid var(--border-input);border-radius:6px;resize:vertical;" placeholder="Add notes about this article..."></textarea>
            <button class="btn btn-secondary" style="margin-top:8px;height:32px;font-size:12px;padding:0 12px;" onclick="saveReviewNotes()">Save Notes</button>
          </div>
        </div>
      </div>
    </div>
  </div>

<!-- Draft editor modal -->
<div class="overlay" id="editor-overlay">
  <div class="modal">
    <div class="modal-header"><h3 id="editor-title">Edit Draft</h3><button class="modal-close" onclick="closeEditor()">&times;</button></div>
    <div class="modal-body">
      <label>Draft Name</label><input type="text" id="editor-name" placeholder="e.g. guest-post-example">
      <label>To</label><input type="email" id="editor-to" placeholder="email@example.com">
      <label>Subject</label><input type="text" id="editor-subject" placeholder="Email subject">
      <label>Body</label><textarea id="editor-body" placeholder="Email body..."></textarea>
    </div>
    <div class="modal-actions">
      <button class="btn btn-secondary" onclick="closeEditor()">Cancel</button>
      <button class="btn btn-secondary" onclick="saveDraft()">Save Draft</button>
      <button class="btn btn-primary" onclick="sendDraft()">Send Email</button>
    </div>
  </div>
</div>

<!-- Reply viewer modal -->
<div class="overlay" id="reply-overlay">
  <div class="modal">
    <div class="modal-header"><h3 id="reply-title">Reply</h3><button class="modal-close" onclick="closeReply()">&times;</button></div>
    <div class="modal-body" id="reply-body-container">
      <div id="reply-loading" style="text-align:center;padding:40px;color:var(--text-secondary);">Loading reply...</div>
      <div id="reply-content" style="display:none;">
        <div class="reply-content">
          <div class="reply-meta">
            <strong>From:</strong> <span id="reply-from"></span><br>
            <strong>Date:</strong> <span id="reply-date"></span><br>
            <strong>Subject:</strong> <span id="reply-subject"></span>
          </div>
          <div class="reply-body-text" id="reply-text"></div>
        </div>
        <hr class="reply-divider">
        <label>Your Response</label>
        <input type="hidden" id="reply-to-addr">
        <input type="text" id="reply-re-subject" placeholder="Re: ...">
        <label style="margin-top:12px">Message</label>
        <textarea id="reply-response" placeholder="Type your response..."></textarea>
      </div>
    </div>
    <div class="modal-actions">
      <button class="btn btn-secondary" onclick="closeReply()">Close</button>
      <button class="btn btn-success" onclick="sendReplyEmail()">Send Reply</button>
    </div>
  </div>
</div>

<div class="chart-tooltip" id="chart-tooltip"><div class="tt-date"></div><div class="tt-value"></div></div>

<script>
// ─── Theme Toggle ───
function getTheme() { return localStorage.getItem('stv-theme') || 'light'; }
function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  document.getElementById('theme-btn').textContent = t === 'dark' ? '\u2600' : '\u263D';
}
function toggleTheme() {
  const next = getTheme() === 'light' ? 'dark' : 'light';
  localStorage.setItem('stv-theme', next);
  applyTheme(next);
  // Redraw charts with updated theme
  loadTraffic();
}
applyTheme(getTheme());

// ─── Navigation ───
document.querySelectorAll('.header-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.header-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.section).classList.add('active');
  });
});

async function api(path, opts = {}) {
  const res = await fetch('/api' + path, opts);
  if (res.status === 401 && path !== '/login') {
    showLogin();
    throw new Error('unauthorized');
  }
  return res.json();
}

// ─── Login Screen ───
function showLogin() {
  document.querySelector('.header').style.display = 'none';
  document.querySelector('.container').style.display = 'none';
  const pwa = document.getElementById('pwa-banner');
  if (pwa) pwa.style.display = 'none';
  let loginEl = document.getElementById('login-screen');
  if (!loginEl) {
    loginEl = document.createElement('div');
    loginEl.id = 'login-screen';
    loginEl.className = 'login-screen';
    loginEl.innerHTML = `<div class="login-box">
      <h2>STV Command Centre</h2>
      <p>Enter your password to continue</p>
      <div id="faceid-login-btn" style="display:none;margin-bottom:16px;">
        <button onclick="loginWithPasskey()" style="width:100%;padding:14px;font-size:16px;font-weight:600;background:var(--info);color:white;border:none;border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          Sign in with Face ID
        </button>
        <div style="text-align:center;color:var(--text-secondary);font-size:12px;margin-top:8px;">or enter password below</div>
      </div>
      <input type="password" id="login-pass" placeholder="Password" autofocus onkeydown="if(event.key==='Enter')doLogin()">
      <button onclick="doLogin()">Sign In</button>
      <div class="login-error" id="login-error">Incorrect password</div>
    </div>`;
    // Check if passkeys are registered and show Face ID button
    fetch('/api/webauthn-has-credentials').then(r=>r.json()).then(d=>{
      if(d.has_credentials){
        document.getElementById('faceid-login-btn').style.display='block';
        // Auto-trigger Face ID
        loginWithPasskey();
      }
    }).catch(()=>{});
    document.body.appendChild(loginEl);
  }
  loginEl.style.display = 'flex';
}

async function doLogin() {
  const pass = document.getElementById('login-pass').value;
  try {
    const res = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({password:pass})});
    const data = await res.json();
    if (data.success) {
      document.getElementById('login-screen').style.display = 'none';
      document.querySelector('.header').style.display = '';
      document.querySelector('.container').style.display = '';
      loadAll();
      // Offer Face ID setup or device trust
      setTimeout(async () => {
        const hasWebAuthn = await checkWebAuthnSupport();
        const hasCreds = await fetch('/api/webauthn-has-credentials').then(r=>r.json()).catch(()=>({has_credentials:false}));
        if (hasWebAuthn && !hasCreds.has_credentials) {
          if (confirm('Set up Face ID?\n\nYou can sign in with Face ID instead of a password.')) {
            await registerPasskey();
          }
        } else if (!localStorage.getItem('stv_device_token')) {
          if (confirm('Trust this device?\n\nYou will not need to enter a password on this device again.')) {
            trustDevice();
          }
        }
      }, 500);
    } else {
      document.getElementById('login-error').style.display = 'block';
    }
  } catch(e) {
    document.getElementById('login-error').style.display = 'block';
  }
}

function toast(msg, type = 'success') {
  const el = document.createElement('div');
  el.className = 'toast toast-' + type;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function copyStatusText(btn, text) {
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = 'Copied!';
    btn.style.background = 'var(--success)';
    btn.style.color = '#fff';
    btn.style.borderColor = 'var(--success)';
    setTimeout(() => {
      btn.textContent = 'Copy for Claude';
      btn.style.background = 'var(--bg-table-header)';
      btn.style.color = 'var(--text-primary)';
      btn.style.borderColor = 'var(--border-primary)';
    }, 2000);
  });
}

// ─── Charts (Semrush palette) ───
const tooltip = document.getElementById('chart-tooltip');
function drawChart(containerId, data, key, color) {
  const container = document.getElementById(containerId);
  if (!data || data.length === 0) {
    container.innerHTML = '<div class="chart-empty">No historical data yet. Charts populate as daily reports accumulate.</div>';
    return;
  }
  const cs = getComputedStyle(document.documentElement);
  const gridColor = cs.getPropertyValue('--chart-grid').trim() || '#E0E1E9';
  const axisText = cs.getPropertyValue('--chart-axis-text').trim() || '#6C6E79';

  const values = data.map(d => d[key]);
  const max = Math.max(...values, 1);
  const w = 800, h = 220, pad = 44;
  const stepX = (w - pad * 2) / Math.max(data.length - 1, 1);

  let points = data.map((d, i) => `${pad + i * stepX},${h - pad - (d[key] / max) * (h - pad * 2)}`).join(' ');
  let areaPoints = points + ` ${pad + (data.length - 1) * stepX},${h - pad} ${pad},${h - pad}`;

  // X-axis labels
  let labels = '';
  const labelStep = Math.max(1, Math.floor(data.length / 6));
  for (let i = 0; i < data.length; i += labelStep) {
    const x = pad + i * stepX;
    labels += `<text x="${x}" y="${h - 8}" fill="${axisText}" font-size="11" text-anchor="middle" font-family="Inter" font-weight="700">${data[i].date.slice(5)}</text>`;
  }
  // Dots (invisible hit area + visible dot)
  let dots = data.map((d, i) => {
    const x = pad + i * stepX;
    const y = h - pad - (d[key] / max) * (h - pad * 2);
    return `<circle cx="${x}" cy="${y}" r="14" fill="transparent" class="dot-hit" data-idx="${i}" data-key="${key}"/>` +
           `<circle cx="${x}" cy="${y}" r="3.5" fill="${color}" opacity="0.9" class="dot-vis" data-idx="${i}" data-key="${key}"/>`;
  }).join('');
  // Y-axis grid + labels
  let yLabels = '';
  for (let i = 0; i <= 4; i++) {
    const val = Math.round(max * i / 4);
    const y = h - pad - (i / 4) * (h - pad * 2);
    yLabels += `<text x="${pad - 8}" y="${y + 4}" fill="${axisText}" font-size="11" text-anchor="end" font-family="Inter" font-weight="700">${val}</text>`;
    yLabels += `<line x1="${pad}" y1="${y}" x2="${w - pad}" y2="${y}" stroke="${gridColor}" stroke-width="1"/>`;
  }

  container.innerHTML = `<svg class="chart-svg" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
    ${yLabels}
    <polygon points="${areaPoints}" fill="url(#grad-${key})" opacity="0.15"/>
    <polyline points="${points}" fill="none" stroke="${color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
    ${dots}
    ${labels}
    <defs><linearGradient id="grad-${key}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${color}" stop-opacity="0.5"/><stop offset="100%" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>
  </svg>`;

  // Hover events
  container.querySelectorAll('.dot-hit, .dot-vis').forEach(dot => {
    dot.addEventListener('mouseenter', () => {
      const idx = parseInt(dot.dataset.idx);
      const d = data[idx];
      tooltip.querySelector('.tt-date').textContent = d.date;
      tooltip.querySelector('.tt-value').textContent = d[key].toLocaleString();
      tooltip.querySelector('.tt-value').style.color = color;
      tooltip.classList.add('visible');
      const vis = container.querySelector(`.dot-vis[data-idx="${idx}"][data-key="${key}"]`);
      if (vis) { vis.setAttribute('r', '6'); vis.setAttribute('opacity', '1'); }
    });
    dot.addEventListener('mousemove', (e) => {
      tooltip.style.left = (e.clientX + 14) + 'px';
      tooltip.style.top = (e.clientY - 44) + 'px';
    });
    dot.addEventListener('mouseleave', () => {
      tooltip.classList.remove('visible');
      const idx = parseInt(dot.dataset.idx);
      const vis = container.querySelector(`.dot-vis[data-idx="${idx}"][data-key="${key}"]`);
      if (vis) { vis.setAttribute('r', '3.5'); vis.setAttribute('opacity', '0.9'); }
    });
  });
}

// ─── Load Sections ───
// Country code to flag emoji
const countryFlags = {China:'\u{1F1E8}\u{1F1F3}',Singapore:'\u{1F1F8}\u{1F1EC}',Malta:'\u{1F1F2}\u{1F1F9}',Netherlands:'\u{1F1F3}\u{1F1F1}','United Kingdom':'\u{1F1EC}\u{1F1E7}','United States':'\u{1F1FA}\u{1F1F8}',Germany:'\u{1F1E9}\u{1F1EA}',France:'\u{1F1EB}\u{1F1F7}',Spain:'\u{1F1EA}\u{1F1F8}',Brazil:'\u{1F1E7}\u{1F1F7}',India:'\u{1F1EE}\u{1F1F3}',Australia:'\u{1F1E6}\u{1F1FA}',Canada:'\u{1F1E8}\u{1F1E6}',Japan:'\u{1F1EF}\u{1F1F5}',Portugal:'\u{1F1F5}\u{1F1F9}',Italy:'\u{1F1EE}\u{1F1F9}',Ireland:'\u{1F1EE}\u{1F1EA}',Poland:'\u{1F1F5}\u{1F1F1}',Sweden:'\u{1F1F8}\u{1F1EA}',Belgium:'\u{1F1E7}\u{1F1EA}',Switzerland:'\u{1F1E8}\u{1F1ED}'};

function donutSVG(data, colors) {
  if (!data || data.length === 0) return '<div class="chart-empty">No data</div>';
  const total = data.reduce((s, d) => s + d.value, 0);
  if (total === 0) return '<div class="chart-empty">No traffic yet</div>';
  let angle = 0;
  const r = 60, cx = 70, cy = 70;
  let paths = '';
  data.forEach((d, i) => {
    const pct = d.value / total;
    const a1 = angle * Math.PI / 180;
    angle += pct * 360;
    const a2 = angle * Math.PI / 180;
    const large = pct > 0.5 ? 1 : 0;
    const x1 = cx + r * Math.sin(a1), y1 = cy - r * Math.cos(a1);
    const x2 = cx + r * Math.sin(a2), y2 = cy - r * Math.cos(a2);
    if (pct >= 0.999) {
      paths += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${colors[i % colors.length]}"/>`;
    } else if (pct > 0.001) {
      paths += `<path d="M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${large},1 ${x2},${y2} Z" fill="${colors[i % colors.length]}"/>`;
    }
  });
  const legend = data.map((d, i) => `<div class="donut-legend-item"><span class="donut-legend-dot" style="background:${colors[i % colors.length]}"></span><span class="donut-legend-label">${escapeHtml(d.label)}</span><span class="donut-legend-val">${d.value}</span></div>`).join('');
  return `<div class="donut-wrap"><svg class="donut-svg" viewBox="0 0 140 140">${paths}<circle cx="${cx}" cy="${cy}" r="38" fill="var(--bg-card)"/><text x="${cx}" y="${cy + 5}" text-anchor="middle" font-size="18" font-weight="700" fill="var(--text-primary)" font-family="Plus Jakarta Sans,Inter,sans-serif">${total}</text></svg><div class="donut-legend">${legend}</div></div>`;
}

function pipelineBar(label, current, total, color) {
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;
  return `<div class="pipeline-item"><div class="pi-label">${label}</div><div class="pi-value">${current} <span style="font-size:14px;font-weight:400;color:var(--text-secondary)">/ ${total}</span></div><div class="pi-bar"><div class="pi-bar-fill" style="width:${pct}%;background:${color}"></div></div></div>`;
}

async function loadOverview() {
  const [data, ga, details, trans, health] = await Promise.all([api('/overview'), api('/ga'), api('/report-details'), api('/translations'), api('/health')]);
  document.getElementById('overview-stats').innerHTML = `
    <div class="stat-card"><div class="label">Emails Sent</div><div class="value blue">${data.emails_sent}</div></div>
    <div class="stat-card"><div class="label">Replies</div><div class="value green">${data.replies}</div></div>
    <div class="stat-card"><div class="label">Awaiting Reply</div><div class="value orange">${data.waiting}</div></div>
    <div class="stat-card"><div class="label">Drafts Ready</div><div class="value">${data.drafts_ready}</div></div>
  `;
  document.getElementById('overview-ga').textContent = ga.raw;

  // Pipeline
  const p = details.pipeline || {};
  const total = p.total || 333;
  document.getElementById('overview-pipeline').innerHTML =
    pipelineBar('Transcriptions', p.transcriptions || 0, total, '#2BB3FF') +
    pipelineBar('Video Pages', p.video_pages || 0, total, '#59DDAA') +
    pipelineBar('Article Pages', p.article_pages || 0, 50, '#FF642D') +
    pipelineBar('YouTube Descriptions', p.video_pages || 0, total, '#8B5CF6');

  // Status section — traffic light system
  // Sort: errors first, then in_progress, then warnings, then info, then ok
  const statusOrder = {error: 0, in_progress: 1, warning: 2, info: 3, ok: 4};
  const sorted = [...(health || [])].sort((a, b) => (statusOrder[a.status] ?? 5) - (statusOrder[b.status] ?? 5));
  const badgeLabels = {error: 'Stuck', in_progress: 'In Progress', warning: 'Needs Attention', info: 'Info', ok: 'OK'};

  // Only show items that need attention — hide OK items entirely
  const actionItems = sorted.filter(h => h.status !== 'ok');

  if (actionItems.length === 0) {
    document.getElementById('system-alerts').innerHTML = '';
    document.getElementById('system-health').innerHTML = '';
    return;
  }

  // Split: red errors at top (system-alerts), everything else below pipeline (system-health)
  const errorCards = actionItems.filter(h => h.status === 'error');
  const otherCards = actionItems.filter(h => h.status !== 'error');

  const renderCard = (h) => {
    const cssClass = h.status === 'in_progress' ? 'status-in-progress' : `status-${h.status}`;
    const stepsText = (h.fix || []).map((s, j) => `${j+1}. ${s}`).join('\\n');
    const copyText = `${h.name}: ${h.detail}${stepsText ? '\\n' + stepsText : ''}`;
    const stepsHtml = h.fix && h.fix.length > 0
      ? `<ol class="status-steps">${h.fix.map(s => '<li>' + escapeHtml(s) + '</li>').join('')}</ol>`
      : '';
    const copyBtn = `<button class="btn" style="margin-top:8px;height:30px;font-size:12px;padding:0 14px;background:var(--bg-table-header);color:var(--text-primary);border:1px solid var(--border-primary);" onclick="event.stopPropagation();copyStatusText(this, \`${copyText.replace(/`/g, '\\`')}\`)">Copy for Claude</button>`;
    const autoFixBtn = h.auto_fix
      ? ` <button class="btn btn-primary" style="margin-top:8px;height:30px;font-size:12px;padding:0 14px;" onclick="runAutoFix('${h.auto_fix}', this)">Fix It</button>`
      : '';
    return `<div class="status-card ${cssClass}">
      <div class="status-header">
        <span class="status-name">${escapeHtml(h.name)}</span>
        <span class="status-badge">${badgeLabels[h.status] || h.status}</span>
      </div>
      <div class="status-detail">${escapeHtml(h.detail)}</div>
      ${stepsHtml}
      <div style="display:flex;gap:8px;">${copyBtn}${autoFixBtn}</div>
    </div>`;
  };

  document.getElementById('system-alerts').innerHTML = errorCards.map(renderCard).join('');
  document.getElementById('system-health').innerHTML = otherCards.map(renderCard).join('');

  // Translation coverage
  const langOrder = ['en', 'es', 'de', 'fr', 'pt', 'ar'];
  const langColors = {en:'var(--info)', es:'#FF642D', de:'var(--text-primary)', fr:'#2BB3FF', pt:'#59DDAA', ar:'#8B5CF6'};
  document.getElementById('overview-translations').innerHTML = langOrder.map(code => {
    const l = trans[code] || {name: code, count: 0};
    return `<div class="lang-card"><div class="lc-code" style="color:${langColors[code] || 'var(--text-primary)'}">${code}</div><div class="lc-name">${escapeHtml(l.name)}</div><div class="lc-count">${l.count} pages</div></div>`;
  }).join('');
}

function calcChange(current, previous) {
  if (previous === 0 && current === 0) return { pct: 0, dir: 'flat' };
  if (previous === 0) return { pct: 100, dir: 'up' };
  const pct = Math.round(((current - previous) / previous) * 100);
  return { pct: Math.abs(pct), dir: pct > 0 ? 'up' : pct < 0 ? 'down' : 'flat' };
}

function sparklineSVG(values, color) {
  if (!values || values.length < 2) return '';
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;
  const w = 120, h = 28, pad = 2;
  const stepX = (w - pad * 2) / (values.length - 1);
  const pts = values.map((v, i) => `${pad + i * stepX},${h - pad - ((v - min) / range) * (h - pad * 2)}`).join(' ');
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/></svg>`;
}

function renderTrendCard(label, current, history, key, color, inverted) {
  // inverted: true for metrics where lower is better (bounce rate)
  const values = history.map(d => d[key]);
  const len = values.length;
  const prev = len >= 2 ? values[len - 2] : null;
  const weekAgo = len >= 7 ? values[len - 7] : null;
  const monthAgo = len >= 30 ? values[len - 30] : null;

  const dayChange = prev !== null ? calcChange(current, prev) : null;
  const weekChange = weekAgo !== null ? calcChange(current, weekAgo) : null;
  const monthChange = monthAgo !== null ? calcChange(current, monthAgo) : null;

  // For inverted metrics, swap up/down colors
  const colorDir = (ch) => {
    if (!ch || ch.dir === 'flat') return 'flat';
    if (inverted) return ch.dir === 'up' ? 'down' : 'up';
    return ch.dir;
  };

  const arrow = (ch) => ch.dir === 'up' ? '&#9650;' : ch.dir === 'down' ? '&#9660;' : '&#8211;';
  const badge = (ch) => ch ? `<span class="trend-change ${colorDir(ch)}">${arrow(ch)} ${ch.pct}%</span>` : '';

  const mainChange = dayChange || weekChange || monthChange;
  const suffix = key === 'bounce' ? '%' : '';

  const pv = (ch, periodLabel) => {
    if (!ch) return `<div class="trend-period">${periodLabel}: <span class="period-val flat">&#8211;</span></div>`;
    const sign = ch.dir === 'up' ? '+' : ch.dir === 'down' ? '-' : '';
    return `<div class="trend-period">${periodLabel}: <span class="period-val ${colorDir(ch)}">${sign}${ch.pct}%</span></div>`;
  };
  const periods = pv(dayChange, 'Day') + pv(weekChange, 'Week') + pv(monthChange, 'Month');

  return `<div class="trend-card">
    <div class="trend-label">${label}</div>
    <div class="trend-value-row">
      <span class="trend-value">${current}${suffix}</span>
      ${mainChange ? badge(mainChange) : '<span class="trend-change flat">&#8211; New</span>'}
    </div>
    <div class="trend-periods">${periods}</div>
    <div class="trend-sparkline">${sparklineSVG(values, color)}</div>
  </div>`;
}

async function loadTraffic() {
  const [ga, history, details] = await Promise.all([api('/ga'), api('/ga-history'), api('/report-details')]);
  document.getElementById('traffic-report').textContent = ga.raw;
  drawChart('sessions-chart', history, 'sessions', '#2BB3FF');
  drawChart('users-chart', history, 'users', '#59DDAA');

  // Trend cards
  if (history.length > 0) {
    const latest = history[history.length - 1];
    document.getElementById('trend-cards').innerHTML =
      renderTrendCard('Sessions', latest.sessions, history, 'sessions', '#2BB3FF', false) +
      renderTrendCard('Users', latest.users, history, 'users', '#59DDAA', false) +
      renderTrendCard('Page Views', latest.pageviews, history, 'pageviews', '#FF642D', false) +
      renderTrendCard('Bounce Rate', latest.bounce, history, 'bounce', '#FF4953', true);
  }

  // Traffic sources donut
  const srcColors = ['#2BB3FF', '#59DDAA', '#FF642D', '#FF4953', '#8B5CF6', '#FDC23C'];
  const srcData = (details.sources || []).map(s => ({label: s.channel, value: s.sessions}));
  document.getElementById('traffic-sources').innerHTML = donutSVG(srcData, srcColors);

  // Devices bar
  const devTotal = (details.devices || []).reduce((s, d) => s + d.sessions, 0) || 1;
  const devColors = {desktop: '#2BB3FF', mobile: '#59DDAA', tablet: '#FF642D'};
  document.getElementById('traffic-devices').innerHTML = (details.devices || []).length === 0
    ? '<div class="chart-empty">No device data</div>'
    : '<div class="device-bar-wrap">' + (details.devices || []).map(d => {
      const pct = Math.round((d.sessions / devTotal) * 100);
      const col = devColors[d.device] || '#8B5CF6';
      return `<div class="device-row"><span class="device-label">${d.device}</span><div class="device-bar-bg"><div class="device-bar-fill" style="width:${pct}%;background:${col}"><span>${pct}%</span></div></div><span class="device-bar-count">${d.sessions}</span></div>`;
    }).join('') + '</div>';

  // Top pages
  document.getElementById('traffic-pages').innerHTML = (details.pages || []).length === 0
    ? '<div class="chart-empty">No page data</div>'
    : '<table class="mini-table">' + (details.pages || []).map(p =>
      `<tr><td class="page-name" title="${escapeHtml(p.page)}">${escapeHtml(p.page)}</td><td class="num">${p.views}</td><td class="dim">${escapeHtml(p.avg_time)}</td></tr>`
    ).join('') + '</table>';

  // Countries
  document.getElementById('traffic-countries').innerHTML = (details.countries || []).length === 0
    ? '<div class="chart-empty">No country data</div>'
    : '<div class="country-list">' + (details.countries || []).map(c => {
      const flag = countryFlags[c.country] || '\u{1F310}';
      return `<div class="country-row"><span class="country-flag">${flag}</span><span class="country-name">${escapeHtml(c.country)}</span><span class="country-val">${c.sessions}</span></div>`;
    }).join('') + '</div>';
}

async function loadOutreach() {
  const [data, drafts] = await Promise.all([api('/outreach'), api('/drafts')]);
  const sent = data.sent || [];
  const replied = sent.filter(s => s.reply_received).length;
  const waiting = sent.filter(s => !s.reply_received && !s.followed_up).length;
  const followedUp = sent.filter(s => s.followed_up && !s.reply_received).length;
  const needsFollowUp = sent.filter(s => !s.reply_received && !s.followed_up && s.days_ago >= 5).length;

  // Follow-up alert
  document.getElementById('outreach-alert').innerHTML = needsFollowUp > 0
    ? `<div class="alert-card"><span class="alert-icon">!</span><span class="alert-text">${needsFollowUp} email${needsFollowUp > 1 ? 's' : ''} waiting 5+ days with no reply or follow-up</span><span class="alert-count">${needsFollowUp}</span></div>`
    : '';

  document.getElementById('outreach-stats').innerHTML = `
    <div class="stat-card"><div class="label">Total Sent</div><div class="value blue">${sent.length}</div></div>
    <div class="stat-card"><div class="label">Replies</div><div class="value green">${replied}</div></div>
    <div class="stat-card"><div class="label">Awaiting</div><div class="value orange">${waiting}</div></div>
    <div class="stat-card"><div class="label">Followed Up</div><div class="value">${followedUp}</div></div>
  `;

  // Funnel
  const funnelData = [
    {label: 'Sent', count: sent.length, color: '#2BB3FF'},
    {label: 'Awaiting', count: waiting, color: '#FDC23C'},
    {label: 'Followed Up', count: followedUp, color: '#FF642D'},
    {label: 'Replied', count: replied, color: '#59DDAA'},
  ];
  const maxFunnel = Math.max(...funnelData.map(f => f.count), 1);
  document.getElementById('outreach-funnel').innerHTML = '<div class="funnel-wrap">' +
    funnelData.map((f, i) => {
      const h = Math.max(8, Math.round((f.count / maxFunnel) * 100));
      const w = 60 - i * 8;
      return (i > 0 ? '<span class="funnel-arrow">&rarr;</span>' : '') +
        `<div class="funnel-stage"><div class="funnel-count">${f.count}</div><div class="funnel-bar-wrap"><div class="funnel-bar" style="height:${h}px;width:${w}px;background:${f.color}"></div></div><div class="funnel-label">${f.label}</div></div>`;
    }).join('') + '</div>';

  document.getElementById('outreach-table').innerHTML = sent.map(s => {
    let tag, clickAttr = '';
    const domain = s.to.split('@')[1] || '';
    if (s.reply_received) {
      tag = '<span class="tag tag-green" style="cursor:pointer">Replied &rarr;</span>';
      clickAttr = `class="clickable" onclick="viewReply('${domain}', '${s.to}')"`;
    }
    else if (s.followed_up) tag = '<span class="tag tag-blue">Followed up</span>';
    else if (s.days_ago >= 5) tag = '<span class="tag tag-red">Needs follow-up</span>';
    else tag = `<span class="tag tag-orange">Waiting (${s.days_ago}d)</span>`;
    return `<tr ${clickAttr}><td>${s.to}</td><td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${(s.subject||'').substring(0,55)}</td><td style="white-space:nowrap">${(s.sent_at||'').substring(0,10)}</td><td>${tag}</td></tr>`;
  }).join('');

  document.getElementById('draft-list').innerHTML = drafts.map(d => `
    <div class="draft-item ${d._sent ? 'sent' : ''}" onclick="openDraft('${d._name}')">
      <span class="draft-badge">${d._sent ? '<span class="tag tag-gray">Sent</span>' : '<span class="tag tag-green">Ready</span>'}</span>
      <h4>${d.subject || 'No subject'}</h4>
      <div class="meta">To: ${d.to || '?'} &middot; ${d._name}</div>
    </div>
  `).join('');
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

async function toggleOppDone(id, el) {
  const res = await api('/opportunity-done', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: id}),
  });
  if (res.success) {
    const item = el.closest('.opp-item');
    item.classList.toggle('done', res.done);
    el.classList.toggle('checked', res.done);
    el.innerHTML = res.done ? '&#10003;' : '';
    loadSEO();
  }
}

// Backlink + Content tracker modals
function openAddBacklink() {
  const url = prompt('Backlink URL:');
  if (!url) return;
  const source = prompt('Source name (e.g. "BabyPips Forum"):') || '';
  const type = prompt('Type (guest-post, forum, directory, social):') || 'other';
  api('/backlink', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({url, source, type})}).then(r => { if (r.success) { toast('Backlink added!'); loadSEO(); }});
}
function openAddContent() {
  const title = prompt('Content title:');
  if (!title) return;
  const type = prompt('Type (article, page, video):') || 'article';
  api('/content-item', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({title, type, status:'idea'})}).then(r => { if (r.success) { toast('Content added!'); loadSEO(); }});
}
function cycleContentStatus(idx) {
  const statuses = ['idea', 'drafted', 'published', 'translated'];
  api('/content-status', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({index: idx})}).then(r => { if (r.success) loadSEO(); });
}

async function loadSEO() {
  const [parsed, broken, backlinks, content] = await Promise.all([api('/opportunities-parsed'), api('/broken-links'), api('/backlinks'), api('/content-tracker')]);
  document.getElementById('seo-broken-links').textContent = broken.raw;

  // Backlinks
  if (backlinks.length === 0) {
    document.getElementById('seo-backlinks').innerHTML = '<div class="chart-empty">No backlinks tracked yet. Click + Add to log one.</div>';
  } else {
    document.getElementById('seo-backlinks').innerHTML = '<div style="margin-bottom:12px"><span style="font-size:28px;font-weight:700;font-family:Plus Jakarta Sans,sans-serif;color:var(--text-primary)">' + backlinks.length + '</span> <span style="color:var(--text-secondary);font-size:13px">backlinks tracked</span></div>' +
      backlinks.slice(-8).reverse().map(b => `<div class="backlink-item"><span class="backlink-source">${escapeHtml(b.source || b.type)}</span><a class="backlink-url" href="${escapeHtml(b.url)}" target="_blank" rel="noopener">${escapeHtml(b.url)}</a><span class="backlink-date">${b.date}</span></div>`).join('');
  }

  // Content tracker
  if (content.length === 0) {
    document.getElementById('seo-content').innerHTML = '<div class="chart-empty">No content tracked yet. Click + Add.</div>';
  } else {
    const statusCounts = {idea:0, drafted:0, published:0, translated:0};
    content.forEach(c => { if (statusCounts[c.status] !== undefined) statusCounts[c.status]++; });
    document.getElementById('seo-content').innerHTML =
      '<div style="display:flex;gap:12px;margin-bottom:14px">' +
      Object.entries(statusCounts).map(([s,c]) => `<span class="content-status ${s}" style="cursor:default">${s}: ${c}</span>`).join('') + '</div>' +
      content.map((c, i) => `<div class="content-item"><span class="content-status ${c.status}" onclick="cycleContentStatus(${i})" title="Click to advance status">${c.status}</span><span class="content-title">${escapeHtml(c.title)}</span><span class="content-type">${c.type}</span></div>`).join('');
  }

  const remaining = parsed.total - parsed.total_done;
  document.getElementById('opps-stats').innerHTML = `
    <div class="stat-card"><div class="label">Opportunities Found</div><div class="value blue">${parsed.total}</div></div>
    <div class="stat-card"><div class="label">Completed</div><div class="value green">${parsed.total_done}</div></div>
    <div class="stat-card"><div class="label">Remaining</div><div class="value orange">${remaining}</div></div>
    <div class="stat-card"><div class="label">Last Scan</div><div class="value" style="font-size:14px;font-weight:500">${parsed.date || 'N/A'}</div></div>
  `;

  const colors = {
    'Reddit': '#FF4953',
    'Stack Exchange': '#008FF8',
    'Hacker News': '#FF642D',
    'Manual Checks': '#8B5CF6',
    'Engagement Rules': '#009F81',
  };
  function getColor(name) {
    for (const [key, c] of Object.entries(colors)) { if (name.includes(key)) return c; }
    return '#6C6E79';
  }

  let html = '';
  for (const sec of parsed.sections) {
    const color = getColor(sec.name);

    if (sec.type === 'opportunities' || sec.type === 'empty') {
      const done = sec.done_count || 0;
      const total = sec.count || 0;
      const pct = total > 0 ? Math.round((done / total) * 100) : 0;

      html += `<div class="opps-section${total === 0 ? ' collapsed' : ''}" style="border-left-color:${color}">
        <div class="opps-section-header" onclick="this.parentElement.classList.toggle('collapsed')">
          <h3><span class="source-dot" style="background:${color}"></span>${escapeHtml(sec.name)}</h3>
          <div class="opps-count-badge">
            ${total > 0 ? `<span class="done-count">${done}</span><span class="total-count">/ ${total}</span>
            <div class="opps-progress"><div class="opps-progress-fill" style="width:${pct}%;background:${color}"></div></div>` : '<span class="total-count">No items</span>'}
            <span class="opps-chevron">&#9660;</span>
          </div>
        </div>
        <div class="opps-items">`;

      for (const item of sec.items) {
        html += `<div class="opp-item ${item.done ? 'done' : ''}">
          <div class="opp-check ${item.done ? 'checked' : ''}" onclick="toggleOppDone('${item.id}', this)" title="Mark as done">${item.done ? '&#10003;' : ''}</div>
          <div class="opp-content">
            <div class="opp-title">${escapeHtml(item.title)}</div>
            <div class="opp-meta">
              ${item.subreddit ? `<span class="tag tag-red">${escapeHtml(item.subreddit)}</span>` : ''}
              ${item.comments ? `<span class="tag tag-gray">${item.comments} comments</span>` : ''}
            </div>
            ${item.snippet ? `<div class="opp-snippet">${escapeHtml(item.snippet)}</div>` : ''}
            ${item.angle ? `<div class="opp-angle">${escapeHtml(item.angle)}</div>` : ''}
          </div>
          ${item.link ? `<a class="opp-link-btn" href="${escapeHtml(item.link)}" target="_blank" rel="noopener">Open &rarr;</a>` : ''}
        </div>`;
      }
      html += '</div></div>';
    }
    else if (sec.type === 'manual') {
      html += `<div class="opps-section" style="border-left-color:${color}">
        <div class="opps-section-header" onclick="this.parentElement.classList.toggle('collapsed')">
          <h3><span class="source-dot" style="background:${color}"></span>${escapeHtml(sec.name)}</h3>
          <div class="opps-count-badge">
            <span class="total-count">${sec.count} platforms</span>
            <span class="opps-chevron">&#9660;</span>
          </div>
        </div>
        <div class="opps-items">`;
      for (const sub of sec.items) {
        html += `<div class="manual-sub">
          <h4>${escapeHtml(sub.name)}</h4>
          ${sub.note ? `<div class="note">${escapeHtml(sub.note)}</div>` : ''}
          <div class="manual-links">
            ${sub.links.map(l => `<a class="manual-link" href="${escapeHtml(l.url)}" target="_blank" rel="noopener">${escapeHtml(l.label)}</a>`).join('')}
          </div>
        </div>`;
      }
      html += '</div></div>';
    }
    else if (sec.type === 'rules') {
      html += `<div class="opps-section" style="border-left-color:${color}">
        <div class="opps-section-header" onclick="this.parentElement.classList.toggle('collapsed')">
          <h3><span class="source-dot" style="background:${color}"></span>${escapeHtml(sec.name)}</h3>
          <div class="opps-count-badge">
            <span class="total-count">${sec.count} rules</span>
            <span class="opps-chevron">&#9660;</span>
          </div>
        </div>
        <div class="opps-items">
          <ol class="rules-list">
            ${sec.items.map((r, i) => `<li data-num="${i+1}.">${escapeHtml(r.text)}</li>`).join('')}
          </ol>
        </div>
      </div>`;
    }
  }
  document.getElementById('opps-sections').innerHTML = html;
}

// ─── Reply Viewer ───
async function viewReply(domain, toAddr) {
  document.getElementById('reply-overlay').classList.add('visible');
  document.getElementById('reply-loading').style.display = 'block';
  document.getElementById('reply-content').style.display = 'none';
  const data = await api('/reply/' + encodeURIComponent(domain));
  document.getElementById('reply-loading').style.display = 'none';
  if (data.error) {
    document.getElementById('reply-content').style.display = 'block';
    document.getElementById('reply-text').textContent = 'Could not load reply: ' + data.error;
    return;
  }
  document.getElementById('reply-content').style.display = 'block';
  document.getElementById('reply-from').textContent = data.from;
  document.getElementById('reply-date').textContent = data.date;
  document.getElementById('reply-subject').textContent = data.subject;
  document.getElementById('reply-text').textContent = data.body;
  document.getElementById('reply-title').textContent = 'Reply from ' + domain;
  document.getElementById('reply-to-addr').value = toAddr;
  document.getElementById('reply-re-subject').value = 'Re: ' + data.subject;
  document.getElementById('reply-response').value = '';
}

function closeReply() { document.getElementById('reply-overlay').classList.remove('visible'); }

async function sendReplyEmail() {
  const to = document.getElementById('reply-to-addr').value;
  const subject = document.getElementById('reply-re-subject').value;
  const body = document.getElementById('reply-response').value;
  if (!body.trim()) { toast('Write a response first', 'error'); return; }
  if (!confirm('Send reply to ' + to + '?')) return;
  const res = await api('/send-reply', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ to, subject, body }),
  });
  if (res.success) { toast('Reply sent!'); closeReply(); loadOutreach(); }
  else toast(res.error || 'Failed', 'error');
}

// ─── Draft Editor ───
let currentDraftName = '';
async function openDraft(name) {
  const drafts = await api('/drafts');
  const draft = drafts.find(d => d._name === name);
  if (!draft) return;
  currentDraftName = name;
  document.getElementById('editor-title').textContent = 'Edit: ' + name;
  document.getElementById('editor-name').value = name;
  document.getElementById('editor-to').value = draft.to || '';
  document.getElementById('editor-subject').value = draft.subject || '';
  document.getElementById('editor-body').value = draft.body || '';
  document.getElementById('editor-overlay').classList.add('visible');
}
function openNewDraft() {
  currentDraftName = '';
  document.getElementById('editor-title').textContent = 'New Draft';
  document.getElementById('editor-name').value = '';
  document.getElementById('editor-to').value = '';
  document.getElementById('editor-subject').value = '';
  document.getElementById('editor-body').value = '';
  document.getElementById('editor-overlay').classList.add('visible');
}
function closeEditor() { document.getElementById('editor-overlay').classList.remove('visible'); }

async function saveDraft() {
  const name = document.getElementById('editor-name').value.trim();
  if (!name) { toast('Name required', 'error'); return; }
  const res = await api('/drafts/' + encodeURIComponent(name), {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ to: document.getElementById('editor-to').value, subject: document.getElementById('editor-subject').value, body: document.getElementById('editor-body').value }),
  });
  if (res.success) { toast('Saved!'); closeEditor(); loadOutreach(); } else toast(res.error || 'Failed', 'error');
}

async function sendDraft() {
  const name = document.getElementById('editor-name').value.trim();
  if (!name) { toast('Save first', 'error'); return; }
  await saveDraft();
  if (!confirm('Send to ' + document.getElementById('editor-to').value + '?')) return;
  const res = await api('/send/' + encodeURIComponent(name), { method: 'POST' });
  if (res.success) { toast('Sent! ID: ' + res.id); closeEditor(); loadOutreach(); loadOverview(); } else toast(res.error || 'Failed', 'error');
}

// Close modals on backdrop click
document.querySelectorAll('.overlay').forEach(o => o.addEventListener('click', e => { if (e.target === e.currentTarget) e.target.classList.remove('visible'); }));

// ─── Growth Strategy Tab ───
const catColors = {content:'#2BB3FF', seo:'#59DDAA', distribution:'#FF642D', monetization:'#8B5CF6'};
const catLabels = {content:'Content', seo:'SEO', distribution:'Distribution', monetization:'Monetisation'};
let goalsData = [];
let goalFilter = 'all';

function filterGoals(cat, btn) {
  goalFilter = cat;
  document.querySelectorAll('.goal-filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderGoals();
}

function progressRingSVG(pct, color) {
  const r = 16, c = 2 * Math.PI * r;
  const offset = c - (pct / 100) * c;
  return `<svg class="goal-progress-ring" viewBox="0 0 40 40"><circle cx="20" cy="20" r="${r}" fill="none" stroke="var(--border-primary)" stroke-width="3"/><circle cx="20" cy="20" r="${r}" fill="none" stroke="${color}" stroke-width="3" stroke-dasharray="${c}" stroke-dashoffset="${offset}" stroke-linecap="round" transform="rotate(-90 20 20)"/><text x="20" y="24" text-anchor="middle" font-size="11" font-weight="700" fill="var(--text-primary)" font-family="Plus Jakarta Sans,Inter,sans-serif">${pct}</text></svg>`;
}

function renderGoals() {
  const filtered = goalFilter === 'all' ? goalsData : goalsData.filter(g => g.category === goalFilter);

  // Summary cards
  const byStatus = {not_started:0, in_progress:0, blocked:0, completed:0};
  goalsData.forEach(g => { if (byStatus[g.status] !== undefined) byStatus[g.status]++; });
  const avgProgress = goalsData.length > 0 ? Math.round(goalsData.reduce((s,g) => s + (g.progress||0), 0) / goalsData.length) : 0;
  document.getElementById('goal-summary').innerHTML = `
    <div class="stat-card"><div class="label">Total Goals</div><div class="value blue">${goalsData.length}</div></div>
    <div class="stat-card"><div class="label">In Progress</div><div class="value" style="color:var(--tag-blue-text)">${byStatus.in_progress}</div></div>
    <div class="stat-card"><div class="label">Completed</div><div class="value green">${byStatus.completed}</div></div>
    <div class="stat-card"><div class="label">Avg Progress</div><div class="value">${avgProgress}%</div></div>
  `;

  // Goal cards
  let html = '';
  for (const g of filtered) {
    const color = catColors[g.category] || '#6C6E79';
    const doneTasks = (g.tasks || []).filter(t => t.done).length;
    const totalTasks = (g.tasks || []).length;

    html += `<div class="goal-card cat-${g.category} collapsed" id="goal-${g.id}">
      <div class="goal-header" onclick="this.parentElement.classList.toggle('collapsed')">
        <div class="goal-priority" style="background:${color}">${g.id}</div>
        <div class="goal-info">
          <div class="goal-title">${escapeHtml(g.title)}</div>
          <div class="goal-desc">${escapeHtml(g.description)}</div>
        </div>
        <div class="goal-right">
          <span class="tag" style="background:${color}20;color:${color};font-weight:600;font-size:11px">${catLabels[g.category] || g.category}</span>
          <span class="goal-status-badge ${g.status}">${g.status.replace('_',' ')}</span>
          ${progressRingSVG(g.progress || 0, color)}
          <span class="goal-chevron">&#9660;</span>
        </div>
      </div>
      <div class="goal-body">
        <div class="goal-section-title">My Recommendations</div>
        ${(g.recommendations || []).map(r => `<div class="goal-rec">${escapeHtml(r)}</div>`).join('')}
        <div class="goal-section-title">Tasks (${doneTasks}/${totalTasks})</div>
        ${(g.tasks || []).map((t, i) => `<div class="goal-task ${t.done ? 'done' : ''}">
          <div class="goal-task-check ${t.done ? 'checked' : ''}" onclick="toggleGoalTask(${g.id},${i},this)" title="Toggle">${t.done ? '&#10003;' : ''}</div>
          <span class="goal-task-text">${escapeHtml(t.text)}</span>
        </div>`).join('')}
        <div class="goal-section-title">Notes</div>
        <textarea class="goal-notes-input" placeholder="Add your notes..." onblur="saveGoalNotes(${g.id},this.value)">${escapeHtml(g.notes || '')}</textarea>
        <div style="margin-top:12px;display:flex;gap:8px">
          <select onchange="updateGoalStatus(${g.id},this.value)" style="padding:6px 10px;border-radius:var(--radius-sm);border:1px solid var(--border-input);background:var(--bg-input);color:var(--text-primary);font-size:12px;font-family:Inter,sans-serif">
            <option value="not_started" ${g.status==='not_started'?'selected':''}>Not Started</option>
            <option value="in_progress" ${g.status==='in_progress'?'selected':''}>In Progress</option>
            <option value="blocked" ${g.status==='blocked'?'selected':''}>Blocked</option>
            <option value="completed" ${g.status==='completed'?'selected':''}>Completed</option>
          </select>
        </div>
      </div>
    </div>`;
  }
  document.getElementById('goals-list').innerHTML = html;
}

async function toggleGoalTask(goalId, taskIdx, el) {
  const res = await api('/goal-task', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({goal_id: goalId, task_index: taskIdx})});
  if (res.success) {
    const item = el.closest('.goal-task');
    item.classList.toggle('done', res.done);
    el.classList.toggle('checked', res.done);
    el.innerHTML = res.done ? '&#10003;' : '';
    // Update local data
    const g = goalsData.find(g => g.id === goalId);
    if (g) { g.tasks[taskIdx].done = res.done; g.progress = res.progress; }
    // Update progress ring
    const ring = document.querySelector('#goal-' + goalId + ' .goal-progress-ring');
    if (ring && g) ring.outerHTML = progressRingSVG(g.progress, catColors[g.category] || '#6C6E79');
  }
}

async function saveGoalNotes(goalId, notes) {
  await api('/goal-update', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({goal_id: goalId, notes: notes})});
}

async function updateGoalStatus(goalId, status) {
  const res = await api('/goal-update', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({goal_id: goalId, status: status})});
  if (res.success) {
    const g = goalsData.find(g => g.id === goalId);
    if (g) g.status = status;
    renderGoals();
    toast('Status updated');
  }
}

async function loadGrowth() {
  goalsData = await api('/goals');
  renderGoals();
}

// ─── Performance Tab ───
function gaugeArc(score, color) {
  const r = 32, cx = 40, cy = 40;
  const angle = (score / 100) * 270 - 135;
  const startAngle = -135 * Math.PI / 180;
  const endAngle = angle * Math.PI / 180;
  const bgEnd = 135 * Math.PI / 180;
  const x1bg = cx + r * Math.cos(startAngle), y1bg = cy + r * Math.sin(startAngle);
  const x2bg = cx + r * Math.cos(bgEnd), y2bg = cy + r * Math.sin(bgEnd);
  const x1 = cx + r * Math.cos(startAngle), y1 = cy + r * Math.sin(startAngle);
  const x2 = cx + r * Math.cos(endAngle), y2 = cy + r * Math.sin(endAngle);
  const large = score > 50 ? 1 : 0;
  const scoreColor = score >= 90 ? 'var(--success)' : score >= 50 ? '#FDC23C' : 'var(--critical)';
  return `<svg viewBox="0 0 80 80">
    <path d="M${x1bg},${y1bg} A${r},${r} 0 1,1 ${x2bg},${y2bg}" fill="none" stroke="var(--border-primary)" stroke-width="6" stroke-linecap="round"/>
    ${score > 0 ? `<path d="M${x1},${y1} A${r},${r} 0 ${large},1 ${x2},${y2}" fill="none" stroke="${scoreColor}" stroke-width="6" stroke-linecap="round"/>` : ''}
    <text x="${cx}" y="${cy + 6}" text-anchor="middle" class="gauge-score" fill="${scoreColor}">${score}</text>
  </svg>`;
}

function renderPageSpeed(data) {
  for (const strategy of ['mobile', 'desktop']) {
    const el = document.getElementById('speed-' + strategy);
    const scores = (data.scores || {})[strategy];
    if (!scores || scores.error) {
      el.innerHTML = `<div class="chart-empty">${scores?.error || 'No data'}</div>`;
      continue;
    }
    const metrics = [
      {label: 'Performance', key: 'performance'},
      {label: 'Accessibility', key: 'accessibility'},
      {label: 'Best Practices', key: 'best_practices'},
      {label: 'SEO', key: 'seo'},
    ];
    el.innerHTML = metrics.map(m => `<div class="speed-gauge">${gaugeArc(scores[m.key] || 0)}<div class="gauge-label">${m.label}</div></div>`).join('');
  }
}

async function runPageSpeed() {
  document.getElementById('speed-mobile').innerHTML = '<div class="chart-empty">Scanning... (takes ~30 seconds)</div>';
  document.getElementById('speed-desktop').innerHTML = '<div class="chart-empty">Scanning...</div>';
  const data = await api('/pagespeed-scan', {method: 'POST'});
  renderPageSpeed(data);
  toast('PageSpeed scan complete');
}

async function loadPerformance() {
  const [speed, ctaStats] = await Promise.all([api('/pagespeed'), api('/cta-stats')]);
  renderPageSpeed(speed);

  // CTA click trend chart
  if (ctaStats && ctaStats.length > 0 && ctaStats.some(d => d.clicks > 0)) {
    const total = ctaStats.reduce((s,d) => s + d.clicks, 0);
    const thisWeek = ctaStats.slice(-7).reduce((s,d) => s + d.clicks, 0);
    const prevWeek = ctaStats.slice(-14,-7).reduce((s,d) => s + d.clicks, 0);
    const ch = calcChange(thisWeek, prevWeek);
    document.getElementById('cta-test-results').innerHTML = `
      <div style="display:flex;gap:24px;align-items:baseline;margin-bottom:16px">
        <div><span style="font-size:28px;font-weight:700;font-family:Plus Jakarta Sans,sans-serif;color:var(--text-primary)">${total}</span> <span style="color:var(--text-secondary);font-size:13px">total CTA clicks</span></div>
        <div><span style="font-size:18px;font-weight:700;font-family:Plus Jakarta Sans,sans-serif;color:var(--text-primary)">${thisWeek}</span> <span style="color:var(--text-secondary);font-size:13px">this week</span>
        ${ch ? `<span class="trend-change ${ch.dir}" style="margin-left:6px">${ch.dir==='up'?'&#9650;':ch.dir==='down'?'&#9660;':'&#8211;'} ${ch.pct}%</span>` : ''}</div>
      </div>`;
    // Mini chart
    const vals = ctaStats.map(d => d.clicks);
    const sparkEl = document.getElementById('cta-click-chart');
    if (sparkEl) {
      const max = Math.max(...vals, 1);
      const w = 600, h = 80, pad = 4;
      const stepX = (w - pad * 2) / Math.max(vals.length - 1, 1);
      const pts = vals.map((v, i) => `${pad + i * stepX},${h - pad - (v / max) * (h - pad * 2)}`).join(' ');
      sparkEl.innerHTML = `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:80px" preserveAspectRatio="none"><polygon points="${pts} ${pad + (vals.length-1)*stepX},${h-pad} ${pad},${h-pad}" fill="var(--tag-green-bg)" opacity="0.5"/><polyline points="${pts}" fill="none" stroke="var(--success)" stroke-width="2" stroke-linejoin="round"/></svg>`;
    }
  }
}

// ─── Activity Feed + CTA for Overview ───
async function loadActivityFeed() {
  const activities = await api('/activity-feed');
  const iconMap = {mail:'&#9993;', reply:'&#8617;', chart:'&#9670;', scan:'&#8853;'};
  if (!activities || activities.length === 0) {
    document.getElementById('overview-activity').innerHTML = '<div class="chart-empty">No activity yet</div>';
    return;
  }
  document.getElementById('overview-activity').innerHTML = '<div class="activity-feed">' +
    activities.slice(0, 10).map(a => `<div class="activity-item">
      <div class="activity-icon ${a.icon || 'chart'}">${iconMap[a.icon] || '&#9670;'}</div>
      <div class="activity-text">${escapeHtml(a.text)}</div>
      <div class="activity-date">${(a.date || '').replace('T', ' ')}</div>
    </div>`).join('') + '</div>';
}

async function loadOverviewCTA() {
  const details = await api('/report-details');
  const clicks = details.cta_clicks || 0;
  const note = details.cta_note || '';
  if (clicks > 0) {
    document.getElementById('overview-cta').innerHTML = `
      <div style="text-align:center;padding:16px 0">
        <div style="font-size:42px;font-weight:800;font-family:Plus Jakarta Sans,sans-serif;color:var(--success)">${clicks}</div>
        <div style="font-size:14px;color:var(--text-secondary);margin-top:4px">CTA Clicks (7 days)</div>
      </div>`;
  } else {
    document.getElementById('overview-cta').innerHTML = `
      <div class="chart-empty">${note || 'No CTA clicks recorded yet. Clicks will appear as GA tracks affiliate link events.'}</div>`;
  }
}

// ─── Automation Tab ───
let autoRefreshTimer = null;

async function loadAutomation() {
  try {
    const data = await api('/automation-status');
    // Status cards
    document.getElementById('auto-stats').innerHTML = `
      <div class="stat-card"><div class="stat-value">${data.transcriptions}</div><div class="stat-label">Transcriptions</div></div>
      <div class="stat-card"><div class="stat-value">${data.total_subtitles}</div><div class="stat-label">Total Subtitles</div></div>
      <div class="stat-card"><div class="stat-value">${data.running_tasks.length}</div><div class="stat-label">Running Tasks</div></div>
      <div class="stat-card"><div class="stat-value" style="font-size:14px">${data.pipeline.last_run ? new Date(data.pipeline.last_run).toLocaleDateString() : 'Never'}</div><div class="stat-label">Last Pipeline Run</div></div>`;

    // Running count badge
    document.getElementById('running-count').textContent = data.running_tasks.length || '';

    // Running tasks
    const runEl = document.getElementById('auto-running');
    if (data.running_tasks.length === 0) {
      runEl.innerHTML = '<div class="chart-empty">No tasks running</div>';
    } else {
      runEl.innerHTML = data.running_tasks.map(t => `
        <div class="auto-task-item">
          <div>
            <div class="auto-task-name">${t.name}</div>
            <div class="auto-task-meta">Started ${new Date(t.started).toLocaleTimeString()} &middot; ${t.cmd}</div>
          </div>
          <div style="display:flex;gap:8px;align-items:center">
            <span class="auto-task-status running">Running</span>
            <button class="btn btn-secondary" style="height:28px;font-size:12px;padding:0 10px" onclick="viewTaskLog('${t.id}')">View Log</button>
            <button class="btn btn-secondary" style="height:28px;font-size:12px;padding:0 10px;color:var(--critical)" onclick="stopTask('${t.id}')">Stop</button>
          </div>
        </div>`).join('');
    }

    // Update log selector
    const sel = document.getElementById('log-select');
    const curVal = sel.value;
    let options = '<option value="">Select a task...</option>';
    data.running_tasks.forEach(t => { options += `<option value="${t.id}" ${curVal===t.id?'selected':''}>${t.name} (running)</option>`; });
    data.recent_tasks.forEach(t => { options += `<option value="${t.id}" ${curVal===t.id?'selected':''}>${t.name} (${t.status})</option>`; });
    sel.innerHTML = options;

    // Task history
    const histEl = document.getElementById('auto-history');
    if (data.recent_tasks.length === 0) {
      histEl.innerHTML = '<div class="chart-empty">No completed tasks yet</div>';
    } else {
      histEl.innerHTML = data.recent_tasks.map(t => `
        <div class="auto-task-item">
          <div>
            <div class="auto-task-name">${t.name}</div>
            <div class="auto-task-meta">${t.started ? new Date(t.started).toLocaleString() : ''} ${t.finished ? '&rarr; ' + new Date(t.finished).toLocaleTimeString() : ''}</div>
          </div>
          <div style="display:flex;gap:8px;align-items:center">
            <span class="auto-task-status ${t.status}">${t.status}</span>
            <button class="btn btn-secondary" style="height:28px;font-size:12px;padding:0 10px" onclick="viewTaskLog('${t.id}')">Log</button>
          </div>
        </div>`).join('');
    }

    // Auto-refresh log if viewing a running task
    if (curVal && data.running_tasks.some(t => t.id === curVal)) {
      loadTaskLog(curVal);
    }
  } catch (e) { console.warn('loadAutomation error:', e); }
}

async function runAction(type, name, actionId) {
  const btn = event.currentTarget;
  btn.classList.add('running');
  try {
    const res = await api('/run-task', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({action: actionId, name: name})
    });
    if (res.error) { toast(res.error, 'error'); }
    else { toast(`Started: ${name}`); }
    setTimeout(loadAutomation, 500);
  } catch(e) { toast('Failed to start task', 'error'); }
  setTimeout(() => btn.classList.remove('running'), 2000);
}

async function loadTaskLog(taskId) {
  if (!taskId) {
    document.getElementById('auto-log').textContent = 'Select a task to view its log output...';
    return;
  }
  try {
    const res = await api('/task-log/' + taskId);
    const el = document.getElementById('auto-log');
    el.textContent = res.log || '(empty)';
    el.scrollTop = el.scrollHeight;
  } catch(e) { console.warn('loadTaskLog error:', e); }
}

function viewTaskLog(taskId) {
  document.getElementById('log-select').value = taskId;
  loadTaskLog(taskId);
  // Scroll to log viewer
  document.getElementById('auto-log').scrollIntoView({behavior:'smooth'});
}

async function stopTask(taskId) {
  if (!confirm('Stop this task?')) return;
  await api('/stop-task', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({task_id: taskId})});
  toast('Task stopped');
  setTimeout(loadAutomation, 500);
}

function openCustomCommand() { document.getElementById('cmd-overlay').classList.add('visible'); }
function closeCmdModal() { document.getElementById('cmd-overlay').classList.remove('visible'); }

async function runCustomCommand() {
  const name = document.getElementById('cmd-name').value || 'Custom task';
  const cmd = document.getElementById('cmd-input').value;
  if (!cmd) { toast('Enter a command', 'error'); return; }
  closeCmdModal();
  const res = await api('/run-task', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action:'custom', name, cmd})});
  if (res.error) toast(res.error, 'error');
  else toast(`Started: ${name}`);
  setTimeout(loadAutomation, 500);
}

// ─── PWA Install Prompt ───
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const banner = document.getElementById('pwa-banner');
  if (banner) banner.style.display = 'block';
});

function installPWA() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then(r => {
      document.getElementById('pwa-banner').style.display = 'none';
      deferredPrompt = null;
    });
  }
}

function dismissPWA() { document.getElementById('pwa-banner').style.display = 'none'; }

// Register service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}

// ─── Load All + Auto-Refresh ───
async function loadAll() {
  await Promise.all([loadOverview(), loadTraffic(), loadOutreach(), loadSEO(), loadGrowth(), loadAutomation(), loadPerformance(), loadActivityFeed(), loadOverviewCTA(), loadReview()]);
}
loadAll();

// Auto-refresh every 30 seconds (faster for automation monitoring)
setInterval(() => {
  loadAll().catch(e => console.warn('Auto-refresh failed:', e));
}, 30000);

// Refresh automation tab more frequently when viewing it
setInterval(() => {
  const autoTab = document.getElementById('automation');
  if (autoTab && autoTab.classList.contains('active')) {
    loadAutomation();
  }
}, 5000);

// Refresh review tab when viewing it
setInterval(() => {
  const reviewTab = document.getElementById('review');
  if (reviewTab && reviewTab.classList.contains('active')) {
    loadReview();
  }
}, 10000);

// ─── Review Queue ───
let reviewQueue = [];
let currentReviewSlug = null;
let reviewDirty = false;

async function loadReview() {
  try {
    reviewQueue = await api('/review-queue');
    const list = document.getElementById('review-list');
    const count = document.getElementById('review-count');
    const pending = reviewQueue.filter(a => a.status !== 'published').length;
    count.textContent = pending + ' pending';

    if (!reviewQueue.length) {
      list.innerHTML = '<div class="chart-empty">No articles in review queue.</div>';
      return;
    }

    const typeColors = {seo: 'var(--info)', comparison: 'var(--chart-3)', checklist: 'var(--success)'};
    const statusColors = {pending: 'var(--warning-bg)', reviewed: 'var(--info)', published: 'var(--success-bg)'};
    const statusTextColors = {pending: 'var(--warning-text)', reviewed: 'var(--info-hover)', published: 'var(--success-text)'};

    list.innerHTML = reviewQueue.map(a => `
      <div class="review-item ${currentReviewSlug === a.slug ? 'active' : ''}" onclick="selectReviewArticle('${a.slug}')"
           style="padding:12px 16px;cursor:pointer;border-bottom:1px solid var(--border-primary);transition:background 0.15s;${currentReviewSlug === a.slug ? 'background:var(--bg-table-hover);border-left:3px solid var(--info);' : ''}">
        <div style="font-weight:500;font-size:13px;line-height:1.3;margin-bottom:4px;">${a.title}</div>
        <div style="display:flex;gap:6px;align-items:center;">
          <span style="font-size:11px;padding:1px 6px;border-radius:10px;background:${typeColors[a.type] || 'var(--info)'};color:white;font-weight:500;">${a.type}</span>
          <span style="font-size:11px;padding:1px 6px;border-radius:10px;background:${statusColors[a.status] || statusColors.pending};color:${statusTextColors[a.status] || statusTextColors.pending};font-weight:500;">${a.status}</span>
        </div>
      </div>
    `).join('');
  } catch(e) { console.warn('Review load failed:', e); }
}

async function selectReviewArticle(slug) {
  if (reviewDirty && !confirm('You have unsaved changes. Discard?')) return;
  currentReviewSlug = slug;
  reviewDirty = false;
  const article = reviewQueue.find(a => a.slug === slug);

  document.getElementById('review-article-title').textContent = article ? article.title : slug;
  document.getElementById('review-actions').style.display = 'flex';
  document.getElementById('review-empty').style.display = 'none';
  document.getElementById('review-split').style.display = 'flex';
  document.getElementById('review-notes-card').style.display = 'block';
  document.getElementById('review-seo-card').style.display = 'block';
  loadSeoCheck(slug);

  // Load preview
  const previewUrl = '/preview/' + slug + '/';
  document.getElementById('review-iframe').src = previewUrl;
  const splitIframe = document.getElementById('review-iframe-split');
  if (splitIframe) splitIframe.src = previewUrl;

  // Load raw HTML for editor
  try {
    const data = await api('/review-article?slug=' + slug);
    document.getElementById('review-editor').value = data.html || '';
    const splitEditor = document.getElementById('review-editor-split');
    if (splitEditor) splitEditor.value = data.html || '';
  } catch(e) { console.warn('Could not load article HTML:', e); }

  // Load notes
  if (article && article.notes) {
    document.getElementById('review-notes').value = article.notes;
  } else {
    document.getElementById('review-notes').value = '';
  }

  // Re-render list to show active state
  loadReview();
}

// View mode switching (preview / code / split)
document.querySelectorAll('.review-view-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.review-view-btn').forEach(b => {
      b.classList.remove('active');
      b.style.background = 'none';
      b.style.color = 'var(--text-secondary)';
    });
    btn.classList.add('active');
    btn.style.background = 'var(--bg-card)';
    btn.style.color = 'var(--text-primary)';

    const view = btn.dataset.view;
    document.getElementById('review-preview-pane').style.display = view === 'preview' ? 'flex' : 'none';
    document.getElementById('review-code-pane').style.display = view === 'code' ? 'flex' : 'none';
    document.getElementById('review-split-pane').style.display = view === 'split' ? 'flex' : 'none';
  });
});
// Init first button style
const firstViewBtn = document.querySelector('.review-view-btn.active');
if (firstViewBtn) { firstViewBtn.style.background = 'var(--bg-card)'; firstViewBtn.style.color = 'var(--text-primary)'; }

// Track editor changes
document.getElementById('review-editor').addEventListener('input', () => { reviewDirty = true; });
const splitEd = document.getElementById('review-editor-split');
if (splitEd) splitEd.addEventListener('input', () => {
  reviewDirty = true;
  // Sync to main editor
  document.getElementById('review-editor').value = splitEd.value;
});

async function loadSeoCheck(slug) {
  const container = document.getElementById('seo-results');
  const badge = document.getElementById('seo-score-badge');
  container.innerHTML = '<div style="text-align:center;padding:12px;color:var(--text-secondary);">Analyzing...</div>';
  try {
    const seo = await api('/seo-check?slug=' + slug);
    if (seo.error) { container.innerHTML = seo.error; return; }

    const scoreColor = seo.score >= 80 ? 'var(--success)' : seo.score >= 50 ? 'var(--chart-3)' : 'var(--critical)';
    badge.textContent = seo.score + '/100';
    badge.style.color = scoreColor;

    const statusIcon = {pass: '\u2705', warn: '\u26A0\uFE0F', fail: '\u274C'};
    const statusColor = {pass: 'var(--success-text)', warn: 'var(--warning-text)', fail: 'var(--critical-text)'};

    let html = `<div style="display:flex;gap:16px;margin-bottom:12px;font-size:13px;color:var(--text-secondary);">
      <span>${seo.word_count.toLocaleString()} words</span>
      <span>${seo.reading_time} min read</span>
    </div>`;
    html += seo.checks.map(c => `
      <div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--border-primary);font-size:13px;">
        <span>${statusIcon[c.status] || ''}</span>
        <span style="font-weight:500;min-width:120px;">${c.name}</span>
        <span style="color:${statusColor[c.status] || 'var(--text-secondary)'}">${c.detail}</span>
      </div>
    `).join('');
    container.innerHTML = html;
  } catch(e) { container.innerHTML = 'SEO check failed'; }
}

async function saveReviewDraft() {
  if (!currentReviewSlug) return;
  const html = document.getElementById('review-editor').value || document.getElementById('review-editor-split').value;
  try {
    await api('/review-save', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({slug: currentReviewSlug, html})});
    reviewDirty = false;
    // Refresh preview
    document.getElementById('review-iframe').src = '/preview/' + currentReviewSlug + '/';
    const si = document.getElementById('review-iframe-split');
    if (si) si.src = '/preview/' + currentReviewSlug + '/';
    showToast('Draft saved');
  } catch(e) { showToast('Save failed: ' + e.message, true); }
}

async function publishArticle() {
  if (!currentReviewSlug) return;
  const article = reviewQueue.find(a => a.slug === currentReviewSlug);
  if (!confirm('Publish "' + (article ? article.title : currentReviewSlug) + '" to the live site?\n\nThis will push it to GitHub and it will go live on socialtradingvlog.com immediately.')) return;

  // Save any pending edits first
  if (reviewDirty) await saveReviewDraft();

  try {
    const result = await api('/review-publish', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({slug: currentReviewSlug})});
    if (result.success) {
      showToast('Published! Live on socialtradingvlog.com');
      loadReview();
    } else {
      showToast('Publish failed: ' + (result.error || 'unknown'), true);
    }
  } catch(e) { showToast('Publish failed: ' + e.message, true); }
}

async function saveReviewNotes() {
  if (!currentReviewSlug) return;
  const notes = document.getElementById('review-notes').value;
  try {
    await api('/review-status', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({slug: currentReviewSlug, notes})});
    showToast('Notes saved');
  } catch(e) { showToast('Failed to save notes', true); }
}

async function runAutoFix(fixId, btn) {
  btn.disabled = true;
  btn.textContent = 'Working...';
  try {
    const result = await api('/auto-fix', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({fix_id: fixId})});
    if (result.manual) {
      btn.textContent = 'Manual fix needed';
      btn.disabled = true;
      showToast(result.message);
    } else if (result.success) {
      btn.textContent = 'Running...';
      showToast(result.message);
      if (result.task_id) {
        // Switch to automation tab to see progress
        setTimeout(() => {
          document.querySelector('[data-section="automation"]').click();
        }, 1000);
      }
      // Refresh health after a delay
      setTimeout(() => loadAll(), 5000);
    } else {
      btn.textContent = 'Failed';
      showToast(result.error || 'Fix failed', true);
    }
  } catch(e) {
    btn.textContent = 'Error';
    showToast('Fix failed: ' + e.message, true);
  }
}

function toggleHealthFix(el, index) {
  const fix = document.getElementById('health-fix-' + index);
  if (!fix) return;
  const isOpen = fix.style.display !== 'none';
  // Close all others first
  document.querySelectorAll('.health-fix').forEach(f => f.style.display = 'none');
  document.querySelectorAll('.health-item').forEach(h => {
    const chevron = h.querySelector('span:last-child');
    if (chevron && chevron.textContent === '\u25BC') chevron.textContent = '\u25B6';
  });
  if (!isOpen) {
    fix.style.display = 'block';
    const chevron = el.querySelector('span:last-child');
    if (chevron) chevron.textContent = '\u25BC';
  }
}

function showToast(msg, isError) {
  let toast = document.getElementById('stv-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'stv-toast';
    toast.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);padding:10px 20px;border-radius:8px;font-size:14px;font-weight:500;z-index:10000;transition:opacity 0.3s;pointer-events:none;';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.background = isError ? 'var(--critical)' : 'var(--success)';
  toast.style.color = 'white';
  toast.style.opacity = '1';
  setTimeout(() => { toast.style.opacity = '0'; }, 3000);
}

// ─── Device Trust ───
async function trustDevice() {
  try {
    const result = await api('/trust-device', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name: navigator.userAgent.includes('iPhone') ? 'iPhone' : 'Device'})});
    if (result.device_token) {
      localStorage.setItem('stv_device_token', result.device_token);
      showToast('Device trusted — you will not need to log in again');
      const tbtn = document.getElementById('trust-device-btn');
      if (tbtn) tbtn.style.display = 'none';
    }
  } catch(e) { console.warn('Trust device failed:', e); }
}

// Auto-login with device token on page load
(async function autoLogin() {
  const deviceToken = localStorage.getItem('stv_device_token');
  if (deviceToken) {
    try {
      const res = await fetch('/api/auto-login?token=' + encodeURIComponent(deviceToken));
      if (res.ok) {
        // Session cookie set by server, reload to skip login
        const loginOverlay = document.getElementById('login-overlay');
        if (loginOverlay && loginOverlay.style.display !== 'none') {
          location.reload();
        }
      }
    } catch(e) {}
  }
})();

// Show setup buttons if not yet configured
(async function showSetupButtons() {
  const hasCreds = await fetch('/api/webauthn-has-credentials').then(r=>r.json()).catch(()=>({has_credentials:false}));
  const hasDevice = localStorage.getItem('stv_device_token');
  const faceidBtn = document.getElementById('faceid-setup-btn');
  const trustBtn = document.getElementById('trust-device-btn');
  const supportsWebAuthn = await checkWebAuthnSupport();
  if (faceidBtn && !hasCreds.has_credentials && supportsWebAuthn) {
    faceidBtn.style.display = '';
  }
  if (trustBtn && !hasDevice) {
    trustBtn.style.display = '';
  }
})();

// ─── WebAuthn Face ID ───
async function checkWebAuthnSupport() {
  if (!window.PublicKeyCredential) return false;
  try {
    return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
  } catch(e) { return false; }
}

async function registerPasskey() {
  try {
    const options = await api('/webauthn-register-options', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'});
    if (options.error) { showToast(options.error, true); return; }

    // Convert base64url strings to ArrayBuffers
    const challenge = base64urlToBuffer(options.challenge);
    const userId = base64urlToBuffer(options.user.id);
    const excludeCreds = (options.excludeCredentials || []).map(c => ({
      ...c, id: base64urlToBuffer(c.id)
    }));

    const credential = await navigator.credentials.create({
      publicKey: {
        challenge,
        rp: options.rp,
        user: { ...options.user, id: userId },
        pubKeyCredParams: options.pubKeyCredParams,
        authenticatorSelection: options.authenticatorSelection,
        timeout: options.timeout,
        excludeCredentials: excludeCreds,
        attestation: options.attestation
      }
    });

    // Send credential ID back to server
    const result = await api('/webauthn-register-complete', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        challenge: options.challenge,
        credentialId: bufferToBase64url(credential.rawId),
        name: 'Face ID'
      })
    });

    if (result.success) {
      showToast('Face ID registered successfully!');
      const btn = document.getElementById('faceid-setup-btn');
      if (btn) btn.style.display = 'none';
      const tbtn2 = document.getElementById('trust-device-btn');
      if (tbtn2) tbtn2.style.display = 'none';
    } else {
      showToast(result.error || 'Registration failed', true);
    }
  } catch(e) {
    if (e.name !== 'NotAllowedError') {
      showToast('Face ID setup failed: ' + e.message, true);
    }
  }
}

async function loginWithPasskey() {
  try {
    const res = await fetch('/api/webauthn-login-options', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'});
    const options = await res.json();
    if (options.error) { showToast(options.error, true); return; }

    const challenge = base64urlToBuffer(options.challenge);
    const allowCreds = (options.allowCredentials || []).map(c => ({
      ...c, id: base64urlToBuffer(c.id)
    }));

    const assertion = await navigator.credentials.get({
      publicKey: {
        challenge,
        rpId: options.rpId,
        allowCredentials: allowCreds,
        userVerification: options.userVerification,
        timeout: options.timeout
      }
    });

    // Send assertion back to server
    const loginRes = await fetch('/api/webauthn-login-complete', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        challenge: options.challenge,
        credentialId: bufferToBase64url(assertion.rawId)
      })
    });
    const loginData = await loginRes.json();

    if (loginData.success) {
      document.getElementById('login-screen').style.display = 'none';
      document.querySelector('.header').style.display = '';
      document.querySelector('.container').style.display = '';
      loadAll();
    } else {
      showToast(loginData.error || 'Face ID login failed', true);
    }
  } catch(e) {
    if (e.name !== 'NotAllowedError') {
      showToast('Face ID login failed: ' + e.message, true);
    }
  }
}

// Base64url helpers
function base64urlToBuffer(base64url) {
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
  const pad = base64.length % 4 === 0 ? '' : '='.repeat(4 - base64.length % 4);
  const binary = atob(base64 + pad);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes.buffer;
}

function bufferToBase64url(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

</script>

<!-- PWA install banner -->
<div class="pwa-install-banner" id="pwa-banner">
  <strong>Install STV Command Centre</strong><br>
  <small>Add to your home screen for quick access</small><br>
  <button class="pwa-install-btn" onclick="installPWA()">Install</button>
  <button class="pwa-dismiss-btn" onclick="dismissPWA()">Not now</button>
</div>

</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    require_auth = False  # Set True for VPS/public mode

    def log_message(self, format, *args):
        pass

    def check_auth(self):
        """Check if request is authenticated. Returns True if OK."""
        if not self.require_auth:
            return True
        # These endpoints are always accessible (login page, PWA assets)
        if self.path in ("/", "", "/api/login", "/api/subscribe", "/api/unsubscribe", "/manifest.json", "/sw.js", "/icon-192.png", "/icon-512.png", "/api/webauthn-login-options", "/api/webauthn-login-complete", "/api/webauthn-has-credentials"):
            return True
        return verify_session(self.headers.get("Cookie", ""))

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        # Serve PWA manifest and service worker without auth
        if path == "/manifest.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/manifest+json")
            self.end_headers()
            manifest = json.dumps({
                "name": "STV Command Centre",
                "short_name": "STV Command",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#191B23",
                "theme_color": "#191B23",
                "description": "SocialTradingVlog command centre — manage automation, track growth, monitor analytics.",
                "icons": [
                    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}
                ]
            })
            self.wfile.write(manifest.encode())
            return

        if path == "/sw.js":
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            sw = """const CACHE = 'stv-v1';
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(clients.claim()); });
self.addEventListener('fetch', e => {
  if (e.request.url.includes('/api/')) return;
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});"""
            self.wfile.write(sw.encode())
            return

        if path == "/icon-192.png" or path == "/icon-512.png":
            # Generate a simple SVG-based PNG icon
            size = 192 if "192" in path else 512
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.end_headers()
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"><rect width="{size}" height="{size}" rx="40" fill="#191B23"/><text x="50%" y="55%" font-family="sans-serif" font-size="{size//2.5}" font-weight="800" fill="#FF642D" text-anchor="middle" dominant-baseline="middle">S</text></svg>'
            self.wfile.write(svg.encode())
            return

        # Unsubscribe endpoint (always accessible, no auth)
        if path == "/api/unsubscribe":
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            email = params.get("email", [""])[0]
            if email and unsubscribe(email):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<html><body style='font-family:sans-serif;text-align:center;padding:60px'><h2>Unsubscribed</h2><p>You've been removed from the mailing list.</p></body></html>")
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<html><body style='font-family:sans-serif;text-align:center;padding:60px'><h2>Not Found</h2><p>That email was not on the list.</p></body></html>")
            return

        if not self.check_auth():
            self.send_json({"error": "unauthorized"}, 401)
            return

        if path in ("/", ""):
            self.send_html(DASHBOARD_HTML)
        elif path == "/api/overview":
            self.send_json(get_overview())
        elif path == "/api/ga":
            self.send_json(get_ga_data())
        elif path == "/api/ga-history":
            self.send_json(get_ga_history())
        elif path == "/api/outreach":
            self.send_json(get_outreach_data())
        elif path == "/api/drafts":
            self.send_json(get_drafts())
        elif path == "/api/report-details":
            self.send_json(get_report_details())
        elif path == "/api/translations":
            self.send_json(get_translation_coverage())
        elif path == "/api/backlinks":
            self.send_json(get_backlinks())
        elif path == "/api/content-tracker":
            self.send_json(get_content_tracker())
        elif path == "/api/opportunities":
            self.send_json(get_opportunities())
        elif path == "/api/opportunities-parsed":
            self.send_json(parse_opportunities())
        elif path == "/api/broken-links":
            self.send_json(get_broken_links())
        elif path == "/api/goals":
            self.send_json(get_goals())
        elif path == "/api/health":
            self.send_json(get_system_health())
        elif path == "/api/pagespeed":
            self.send_json(get_pagespeed())
        elif path == "/api/cta-stats":
            self.send_json(get_cta_stats())
        elif path == "/api/activity-feed":
            self.send_json(get_activity_feed())
        elif path.startswith("/api/reply/"):
            domain = urllib.parse.unquote(path.replace("/api/reply/", ""))
            # Find sent date for this domain to filter out old emails
            after_date = None
            if SENT_LOG.exists():
                sent = json.loads(SENT_LOG.read_text())
                for entry in sent:
                    if domain in entry.get("to", ""):
                        sent_at = entry.get("sent_at", "")[:10]
                        if sent_at:
                            after_date = sent_at.replace("-", "/")
                        break
            self.send_json(get_reply_email(domain, after_date=after_date))
        elif path == "/api/subscribers":
            self.send_json(get_subscriber_stats())
        elif path == "/api/automation-status":
            self.send_json(get_automation_status())
        elif path.startswith("/api/task-log/"):
            task_id = path.replace("/api/task-log/", "")
            self.send_json({"log": get_task_log(task_id)})
        elif path == "/api/webauthn-register-options":
            self.send_json(webauthn_register_options())
        elif path.startswith("/api/seo-check"):
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            slug = params.get("slug", [""])[0]
            if slug:
                self.send_json(analyze_seo(slug))
            else:
                self.send_json({"error": "Missing slug parameter"}, 400)
        elif path == "/api/review-queue":
            self.send_json(get_review_queue())
        elif path.startswith("/api/review-article"):
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            slug = params.get("slug", [""])[0]
            html = get_review_article(slug)
            if html:
                self.send_json({"slug": slug, "html": html})
            else:
                self.send_json({"error": "Article not found"}, 404)
        elif path.startswith("/preview/"):
            slug = path.replace("/preview/", "").strip("/")
            html = get_preview_html(slug)
            if html:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode())
            else:
                self.send_response(404)
                self.end_headers()
        elif path == "/api/webauthn-has-credentials":
            creds = _load_webauthn_credentials()
            self.send_json({"has_credentials": len(creds) > 0, "count": len(creds)})
        elif path == "/api/auto-login":
            # Check for device trust token in query string
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            device_token = params.get("token", [""])[0]
            if verify_device_token(device_token):
                session_token = create_session()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", f"stv_session={session_token}; Path=/; Max-Age={86400*90}; SameSite=Lax")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            else:
                self.send_json({"error": "Invalid device token"}, 401)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""

        # Login + WebAuthn endpoints (always accessible, no auth required)
        if path == "/api/login":
            try:
                data = json.loads(body)
                if verify_password(data.get("password", "")):
                    token = create_session()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Set-Cookie", f"stv_session={token}; Path=/; Max-Age=2592000; SameSite=Strict")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode())
                else:
                    self.send_json({"error": "Invalid password"}, 401)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
            return

        # Newsletter subscribe endpoint (always accessible, CORS enabled)
        if path == "/api/subscribe":
            try:
                data = json.loads(body)
                result = add_subscriber(data.get("email", ""), data.get("source", ""))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "https://socialtradingvlog.com")
                self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "https://socialtradingvlog.com")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        if not self.check_auth():
            self.send_json({"error": "unauthorized"}, 401)
            return

        if path == "/api/run-task":
            try:
                data = json.loads(body)
                action = data.get("action", "")
                name = data.get("name", action)
                task_id = f"{action}-{int(datetime.now().timestamp())}"
                venv_python = str(PROJECT_DIR / "venv" / "bin" / "python3")
                python = venv_python if pathlib.Path(venv_python).exists() else sys.executable

                TASK_COMMANDS = {
                    "translate-pipeline": [python, str(SCRIPT_DIR / "run_pipeline.py"), "--translate-only"],
                    "transcribe-batch": [python, str(SCRIPT_DIR / "run_pipeline.py")],
                    "scan-opps": [python, str(SCRIPT_DIR / "opportunity_scanner.py")],
                    "ga-report": [python, str(SCRIPT_DIR / "ga_report.py"), "--days", "7"],
                    "sync-from-mac": "echo 'Sync must be triggered from Mac (run tools/sync_to_vps.sh)'",
                }

                if action == "custom":
                    cmd = data.get("cmd", "")
                    if not cmd:
                        self.send_json({"error": "No command provided"}, 400)
                        return
                    result = run_task(task_id, name, cmd)
                elif action in TASK_COMMANDS:
                    result = run_task(task_id, name, TASK_COMMANDS[action])
                else:
                    self.send_json({"error": f"Unknown action: {action}"}, 400)
                    return
                self.send_json(result)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        if path == "/api/stop-task":
            try:
                data = json.loads(body)
                tid = data.get("task_id", "")
                if tid in RUNNING_TASKS and "pid" in RUNNING_TASKS[tid]:
                    os.kill(RUNNING_TASKS[tid]["pid"], 9)
                    RUNNING_TASKS[tid]["status"] = "stopped"
                    TASK_HISTORY.append(RUNNING_TASKS.pop(tid))
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "Task not found"}, 404)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        if path.startswith("/api/drafts/"):
            name = urllib.parse.unquote(path.replace("/api/drafts/", ""))
            try:
                self.send_json(save_draft(name, json.loads(body)))
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path.startswith("/api/send/"):
            name = urllib.parse.unquote(path.replace("/api/send/", ""))
            try:
                self.send_json(send_draft(name))
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        elif path == "/api/send-reply":
            try:
                data = json.loads(body)
                self.send_json(send_reply_email(data["to"], data["subject"], data["body"]))
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        elif path == "/api/backlink":
            try:
                self.send_json(save_backlink(json.loads(body)))
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/content-item":
            try:
                self.send_json(save_content_item(json.loads(body)))
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/content-status":
            try:
                data = json.loads(body)
                idx = data.get("index", -1)
                items = get_content_tracker()
                if 0 <= idx < len(items):
                    order = ["idea", "drafted", "published", "translated"]
                    cur = items[idx].get("status", "idea")
                    nxt = order[(order.index(cur) + 1) % len(order)] if cur in order else "idea"
                    items[idx]["status"] = nxt
                    CONTENT_TRACKER_FILE.write_text(json.dumps(items, indent=2))
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "Invalid index"}, 400)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/goal-update":
            try:
                data = json.loads(body)
                self.send_json(update_goal(data["goal_id"], data))
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/goal-task":
            try:
                data = json.loads(body)
                self.send_json(toggle_goal_task(data["goal_id"], data["task_index"]))
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/pagespeed-scan":
            try:
                self.send_json(run_pagespeed_check())
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        elif path == "/api/opportunity-done":
            try:
                data = json.loads(body)
                opp_id = data.get("id", "")
                done = get_opps_done()
                if opp_id in done:
                    done.discard(opp_id)
                    is_done = False
                else:
                    done.add(opp_id)
                    is_done = True
                save_opps_done(done)
                self.send_json({"success": True, "done": is_done})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/webauthn-register-options":
            self.send_json(webauthn_register_options())
        elif path == "/api/webauthn-register-complete":
            try:
                data = json.loads(body)
                self.send_json(webauthn_register_complete(data))
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/webauthn-login-options":
            # This endpoint doesn't require auth (used on login screen)
            self.send_json(webauthn_login_options())
        elif path == "/api/webauthn-login-complete":
            try:
                data = json.loads(body)
                result = webauthn_login_complete(data)
                if result.get("success"):
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Set-Cookie", f"stv_session={result['session_token']}; Path=/; Max-Age={86400*90}; SameSite=Lax")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode())
                else:
                    self.send_json(result, 401)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/auto-fix":
            try:
                data = json.loads(body)
                fix_id = data.get("fix_id", "")
                result = run_auto_fix(fix_id)
                self.send_json(result)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        elif path == "/api/trust-device":
            try:
                data = json.loads(body) if body else {}
                name = data.get("name", "Phone")
                device_token = create_device_token(name)
                self.send_json({"success": True, "device_token": device_token})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/review-save":
            try:
                data = json.loads(body)
                slug = data.get("slug", "")
                html = data.get("html", "")
                if slug and html:
                    self.send_json(save_review_article(slug, html))
                else:
                    self.send_json({"error": "Missing slug or html"}, 400)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif path == "/api/review-publish":
            try:
                data = json.loads(body)
                slug = data.get("slug", "")
                if slug:
                    self.send_json(publish_review_article(slug))
                else:
                    self.send_json({"error": "Missing slug"}, 400)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        elif path == "/api/review-status":
            try:
                data = json.loads(body)
                slug = data.get("slug", "")
                status = data.get("status", "")
                notes = data.get("notes")
                queue = get_review_queue()
                article = next((a for a in queue if a["slug"] == slug), None)
                if article:
                    if status:
                        article["status"] = status
                    if notes is not None:
                        article["notes"] = notes
                    save_review_queue(queue)
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "Article not found"}, 404)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        origin = self.headers.get("Origin", "")
        if origin in ("https://socialtradingvlog.com", "http://localhost:8080"):
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            self.send_header("Access-Control-Allow-Origin", "https://socialtradingvlog.com")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="STV Dashboard")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--public", action="store_true", help="Listen on all interfaces (for VPS deployment)")
    parser.add_argument("--auth", action="store_true", help="Require password authentication")
    args = parser.parse_args()

    bind = "0.0.0.0" if args.public else "127.0.0.1"

    if args.auth or args.public:
        auth_data = init_auth()
        DashboardHandler.require_auth = True
        print(f"  Authentication ENABLED")

    server = HTTPServer((bind, args.port), DashboardHandler)
    addr = f"http://{bind}:{args.port}" if args.public else f"http://localhost:{args.port}"
    print(f"\n  STV Command Centre running at {addr}")
    print(f"  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
