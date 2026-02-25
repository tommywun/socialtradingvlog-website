#!/usr/bin/env python3
"""
Shared Security Library — Common utilities for all STV security tools.

Used by: security_monitor.py, threat_scanner.py, security_selftest.py,
         threat_response.py, verify_dependencies.py

Provides:
  - Common path constants (PROJECT_DIR, SECRETS_DIR, etc.)
  - Unified logging with persistent file writes
  - Telegram alerting with rate limiting and deduplication
  - IP validation (proper octet checking)
  - PEP 503 package name normalization
  - Centralized security state tracking
"""

import fcntl
import json
import pathlib
import re
import urllib.request
from datetime import datetime

# ─── Common Paths ────────────────────────────────────────────────────

PROJECT_DIR = pathlib.Path(__file__).parent.parent
TOOLS_DIR = PROJECT_DIR / "tools"
DATA_DIR = PROJECT_DIR / "data"
LOGS_DIR = PROJECT_DIR / "logs"
SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"

# State file for alert deduplication and cross-tool coordination
STATE_FILE = DATA_DIR / "security-state.json"

# Rate limit: max alerts per hour
MAX_ALERTS_PER_HOUR = 10


# ─── Logging ─────────────────────────────────────────────────────────


def log(msg, level="INFO", log_file=None):
    """Unified logging with persistent file writes.

    Args:
        msg: Log message
        level: INFO, WARN, ERROR, CRITICAL, ACTION
        log_file: Path to log file (default: logs/security.log)
    """
    timestamp = datetime.now().isoformat()
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        target = log_file or (LOGS_DIR / "security.log")
        with open(target, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ─── Telegram Alerting ───────────────────────────────────────────────


def _load_state():
    """Load security state for dedup/rate limiting (file-locked)."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f, fcntl.LOCK_UN)
                return data
        except Exception:
            pass
    return {
        "recent_alerts": [],
        "last_tool_runs": {},
    }


def _save_state(state):
    """Save security state (file-locked to prevent corruption from concurrent crons)."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(state, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
    except Exception:
        pass


def send_telegram(subject, body, emoji="🔴", dedupe_key=None):
    """Send Telegram alert with rate limiting and deduplication.

    Args:
        subject: Alert subject line
        body: Alert body text
        emoji: Emoji prefix for the message
        dedupe_key: Optional key for deduplication. If the same key was
                    sent in the last 30 minutes, the alert is skipped.

    Returns:
        True if alert was sent, False if skipped/failed.
    """
    state = _load_state()
    now = datetime.now()
    now_iso = now.isoformat()

    # Clean old alerts (keep last hour only)
    cutoff = (now.timestamp() - 3600)
    state["recent_alerts"] = [
        a for a in state.get("recent_alerts", [])
        if _parse_ts(a.get("time", "")) > cutoff
    ]

    # Rate limiting
    if len(state["recent_alerts"]) >= MAX_ALERTS_PER_HOUR:
        log("Alert rate limit reached — suppressing", "WARN")
        _save_state(state)
        return False

    # Deduplication (same key within 30 minutes)
    if dedupe_key:
        dedupe_cutoff = now.timestamp() - 1800
        for a in state["recent_alerts"]:
            if a.get("key") == dedupe_key and _parse_ts(a.get("time", "")) > dedupe_cutoff:
                log(f"Alert deduplicated (key={dedupe_key})", "INFO")
                _save_state(state)
                return False

    # Send the alert
    try:
        token_file = SECRETS_DIR / "telegram-bot-token.txt"
        chat_file = SECRETS_DIR / "telegram-chat-id.txt"
        if not token_file.exists() or not chat_file.exists():
            return False

        token = token_file.read_text().strip()
        chat_id = chat_file.read_text().strip()

        # Escape Markdown special chars in body to prevent parse errors
        safe_body = body[:1500].replace("_", "\\_").replace("*", "\\*").replace("[", "\\[")
        msg = f"{emoji} *{subject}*\n\n{safe_body}"

        payload = json.dumps({
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)

        # Record this alert
        state["recent_alerts"].append({
            "time": now_iso,
            "subject": subject[:100],
            "key": dedupe_key,
        })
        _save_state(state)
        return True

    except Exception as e:
        log(f"Telegram alert failed: {e}", "ERROR")
        return False


def _parse_ts(iso_str):
    """Parse ISO timestamp to epoch, returning 0 on failure."""
    try:
        return datetime.fromisoformat(iso_str).timestamp()
    except Exception:
        return 0


def record_tool_run(tool_name):
    """Record that a security tool ran successfully."""
    state = _load_state()
    state.setdefault("last_tool_runs", {})[tool_name] = datetime.now().isoformat()
    _save_state(state)


# ─── Validation Helpers ──────────────────────────────────────────────


def validate_ip(ip):
    """Validate IPv4 address — checks each octet is 0-255.

    Returns True if valid, False otherwise.
    """
    if not ip or not isinstance(ip, str):
        return False
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def normalize_package_name(name):
    """PEP 503 package name normalization.

    Converts runs of [-_.] to single hyphens and lowercases.
    e.g. "My_Package.name" → "my-package-name"
    """
    return re.sub(r"[-_.]+", "-", name).lower()
