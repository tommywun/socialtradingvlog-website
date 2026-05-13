#!/usr/bin/env python3
"""
Site Autopilot — Automated health checks, monitoring, and alerting.

Keeps socialtradingvlog.com running smoothly without manual intervention.

Usage:
    python3 tools/site_autopilot.py --check uptime        # Quick uptime check
    python3 tools/site_autopilot.py --check daily          # Daily full system check
    python3 tools/site_autopilot.py --check weekly         # Full weekly health digest
    python3 tools/site_autopilot.py --check links          # Broken link scan
    python3 tools/site_autopilot.py --check disk           # Disk/memory check
    python3 tools/site_autopilot.py --check content-dates  # Stale year references
    python3 tools/site_autopilot.py --check all            # Everything

Cron setup (add to VPS crontab):
    */5 * * * *  python3 /var/www/socialtradingvlog-website/tools/site_autopilot.py --check uptime
    0 8 * * *    python3 /var/www/socialtradingvlog-website/tools/site_autopilot.py --check daily
    0 3 * * 1    python3 /var/www/socialtradingvlog-website/tools/site_autopilot.py --check weekly
"""

import sys
import os
import json
import time
import pathlib
import argparse
import urllib.request
import urllib.error
import ssl
import subprocess
import smtplib
import glob as glob_module
import re
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─── Config ────────────────────────────────────────────────────────────────

SCRIPT_DIR = pathlib.Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
ALERT_LOG = PROJECT_DIR / "data" / "autopilot-alerts.json"
HEALTH_LOG = PROJECT_DIR / "data" / "autopilot-health.json"

SITE_URL = "https://socialtradingvlog.com"

# Key pages to check for uptime
UPTIME_URLS = [
    SITE_URL,
]

# Alert config
TELEGRAM_BOT_TOKEN_FILE = SECRETS_DIR / "telegram-bot-token.txt"
TELEGRAM_CHAT_ID_FILE = SECRETS_DIR / "telegram-chat-id.txt"
EMAIL_CONFIG_FILE = SECRETS_DIR / "email-alerts.json"

# SSL context for HTTPS requests
SSL_CTX = ssl.create_default_context()


# ─── Alerting ──────────────────────────────────────────────────────────────

def load_alert_config():
    """Load email config from secrets."""
    if EMAIL_CONFIG_FILE.exists():
        return json.loads(EMAIL_CONFIG_FILE.read_text())
    return None


def send_telegram(message, level="info"):
    """Send alert via Telegram bot (delegates to security_lib for rate limiting + dedup)."""
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        from security_lib import send_telegram as _send_tg
        icon = {"critical": "🔴", "warning": "🟡", "info": "🟢", "success": "✅"}.get(level, "ℹ️")
        return _send_tg("STV Autopilot", message, emoji=icon)
    except Exception as e:
        print(f"  Telegram alert failed: {e}")
        return False



def log_to_dashboard(alert_type, message, level="info", details=None):
    """Log alert to dashboard-readable JSON file."""
    alerts = []
    if ALERT_LOG.exists():
        try:
            alerts = json.loads(ALERT_LOG.read_text())
        except Exception:
            alerts = []

    alerts.append({
        "type": alert_type,
        "message": message,
        "level": level,
        "details": details,
        "timestamp": datetime.now().isoformat(),
    })

    # Auto-expire alerts older than 7 days and keep max 500
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    alerts = [a for a in alerts if a.get("timestamp", "") > cutoff]
    alerts = alerts[-500:]

    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    ALERT_LOG.write_text(json.dumps(alerts, indent=2))


def send_alert(alert_type, message, level="info", details=None):
    """Send alert via all configured channels."""
    print(f"  [{level.upper()}] {message}")
    log_to_dashboard(alert_type, message, level, details)

    if level in ("critical", "warning"):
        send_telegram(message, level)


# ─── Health Checks ─────────────────────────────────────────────────────────

def check_uptime():
    """Check if key site pages are responding."""
    print("Checking uptime...")
    results = []
    all_ok = True

    for url in UPTIME_URLS:
        try:
            start = time.time()
            req = urllib.request.Request(url, headers={"User-Agent": "STV-Autopilot/1.0"})
            resp = urllib.request.urlopen(req, timeout=15, context=SSL_CTX)
            elapsed = round((time.time() - start) * 1000)
            status = resp.getcode()

            if status == 200:
                results.append({"url": url, "status": status, "ms": elapsed, "ok": True})
                print(f"  ✓ {url} — {status} ({elapsed}ms)")
            else:
                results.append({"url": url, "status": status, "ms": elapsed, "ok": False})
                send_alert("uptime", f"{url} returned status {status}", "warning")
                all_ok = False
        except Exception as e:
            results.append({"url": url, "status": 0, "error": str(e), "ok": False})
            send_alert("uptime", f"{url} is DOWN: {e}", "critical")
            all_ok = False

    if all_ok:
        print("  All pages responding normally.")

    save_health("uptime", {"results": results, "all_ok": all_ok})
    return all_ok


def check_ssl_expiry():
    """Check SSL certificate expiry date."""
    print("Checking SSL certificate...")
    import socket

    try:
        hostname = "socialtradingvlog.com"
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(10)
            s.connect((hostname, 443))
            cert = s.getpeercert()

        expiry_str = cert["notAfter"]
        # Format: 'May 20 12:00:00 2026 GMT'
        expiry = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
        days_left = (expiry - datetime.now()).days

        print(f"  SSL expires: {expiry_str} ({days_left} days left)")

        if days_left < 7:
            send_alert("ssl", f"SSL certificate expires in {days_left} days!", "critical")
        elif days_left < 30:
            send_alert("ssl", f"SSL certificate expires in {days_left} days", "warning")
        else:
            print(f"  ✓ SSL OK ({days_left} days)")

        save_health("ssl", {"expiry": expiry_str, "days_left": days_left})
        return days_left > 7
    except Exception as e:
        send_alert("ssl", f"SSL check failed: {e}", "warning")
        return False


def check_disk():
    """Check disk space and memory usage."""
    print("Checking disk and memory...")
    try:
        # Disk usage
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            usage_pct = int(parts[4].replace("%", ""))
            print(f"  Disk usage: {parts[4]} ({parts[2]} used of {parts[1]})")

            if usage_pct > 90:
                send_alert("disk", f"Disk usage at {usage_pct}%!", "critical")
            elif usage_pct > 80:
                send_alert("disk", f"Disk usage at {usage_pct}%", "warning")
            else:
                print(f"  ✓ Disk OK ({usage_pct}%)")

        save_health("disk", {"usage_pct": usage_pct})
        return usage_pct < 90
    except Exception as e:
        print(f"  Disk check failed: {e}")
        return True  # Don't alert on check failure


def check_broken_links():
    """Scan HTML files for broken internal and external links.

    Persists the full broken set to data/broken-links-snapshot.json and only
    alerts when the broken set grows since the last run — stops the identical
    weekly nag when a known set of broken links isn't yet fully fixed.
    """
    print("Checking for broken links...")
    broken = []
    checked = 0

    # External URLs that are known to be flaky/anti-bot/rate-limited but actually live
    EXTERNAL_ALLOWLIST = {
        # Add hostnames or full URLs here as they are confirmed live-but-flaky
        # e.g. "https://www.etoro.com/", "https://www.linkedin.com/"
    }

    html_files = list(PROJECT_DIR.glob("**/*.html"))
    html_files = [f for f in html_files if not any(
        skip in str(f) for skip in [".git", "node_modules", "tools/", "venv/", "backups/"]
    )]

    link_pattern = re.compile(r'href=["\']([^"\'#]+)["\']')

    external_urls = set()
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding="utf-8", errors="ignore")
            links = link_pattern.findall(content)
            for link in links:
                if link.startswith("http://") or link.startswith("https://"):
                    external_urls.add(link)
                elif link.startswith(("mailto:", "javascript:", "tel:", "data:", "sms:", "ftp:")):
                    continue
                else:
                    if link.startswith("/"):
                        target = PROJECT_DIR / link.lstrip("/")
                    else:
                        target = html_file.parent / link

                    if target.is_dir():
                        target = target / "index.html"
                    if not target.exists() and not target.with_suffix(".html").exists():
                        broken.append({"file": str(html_file.relative_to(PROJECT_DIR)), "link": link, "type": "internal"})
        except Exception:
            continue

    # External URLs — check a sample to avoid rate limits
    external_sample = [u for u in list(external_urls)[:50] if u not in EXTERNAL_ALLOWLIST]
    for url in external_sample:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "STV-LinkChecker/1.0"}, method="HEAD")
            urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
            checked += 1
            time.sleep(0.3)
        except urllib.error.HTTPError as e:
            if e.code in (404, 410, 403):
                broken.append({"url": url, "status": e.code, "type": "external"})
            checked += 1
        except Exception:
            checked += 1

    # Diff against last run — only alert on NEW broken links
    snapshot_path = PROJECT_DIR / "data" / "broken-links-snapshot.json"
    def link_key(b):
        return f"{b.get('type','?')}|{b.get('file','')}|{b.get('link','')}|{b.get('url','')}"
    current_keys = {link_key(b): b for b in broken}

    previous_keys = set()
    if snapshot_path.exists():
        try:
            prev = json.loads(snapshot_path.read_text())
            previous_keys = {link_key(b) for b in prev.get("broken", [])}
        except Exception:
            previous_keys = set()

    new_broken = [b for k, b in current_keys.items() if k not in previous_keys]
    fixed_count = len(previous_keys - set(current_keys.keys()))

    if new_broken:
        send_alert(
            "broken_links",
            f"{len(new_broken)} NEW broken link(s) (total {len(broken)}, fixed {fixed_count} since last run)",
            "warning",
            json.dumps(new_broken[:20], indent=2),
        )
    elif broken:
        print(f"  {len(broken)} broken link(s) — same as last run, no alert "
              f"(fixed {fixed_count} since last run)")
    else:
        print(f"  ✓ No broken links found ({checked} external URLs checked)")

    # Persist full snapshot so next run can diff
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps({
        "ts": datetime.now().isoformat(),
        "count": len(broken),
        "broken": broken,
    }, indent=2))

    save_health("broken_links", {"broken_count": len(broken), "checked": checked, "broken": broken[:50]})
    return len(broken) == 0


def check_content_dates():
    """Find evergreen pages whose latest year reference is stale.

    Only flags pages where no year >= current_year-1 appears anywhere — so
    archive pages, historical articles, and dated content (e.g. "update 2019")
    don't trigger. Translated/update directories are skipped wholesale.
    """
    print("Checking content dates...")
    current_year = datetime.now().year
    stale = []

    html_files = list(PROJECT_DIR.glob("**/*.html"))
    # Skip code/build dirs and historical/translated content that is dated by design
    skip_segments = (
        ".git", "node_modules", "tools/", "venv/", "backups/", "/updates/",
        "/es/", "/de/", "/fr/", "/it/", "/pt/", "/ar/", "/pl/", "/nl/", "/ko/",
    )
    html_files = [f for f in html_files if not any(seg in str(f) for seg in skip_segments)]

    year_pattern = re.compile(r'\b(20[12]\d)\b')

    for html_file in html_files:
        try:
            content = html_file.read_text(encoding="utf-8", errors="ignore")
            years = [int(y) for y in year_pattern.findall(content)]
            if not years:
                continue
            # Only flag if the most recent year on the page is itself stale
            if max(years) < current_year - 1:
                stale.append({
                    "file": str(html_file.relative_to(PROJECT_DIR)),
                    "latest_year": max(years),
                })
        except Exception:
            continue

    if stale:
        send_alert("content_dates", f"{len(stale)} evergreen pages with stale year references", "info",
                   json.dumps(stale[:20], indent=2))
    else:
        print(f"  ✓ All evergreen content dates look current")

    save_health("content_dates", {"stale_count": len(stale), "stale": stale[:50]})
    return len(stale) == 0


ERROR_JOURNAL = PROJECT_DIR / "data" / "error-journal.md"


def log_to_error_journal(system, error, diagnosis, resolution, status="Fixed"):
    """Append an entry to the error journal .md file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"""
### {now} — {system}
- **System**: {system}
- **Error**: {error}
- **Diagnosis**: {diagnosis}
- **Resolution**: {resolution}
- **Status**: {status}
"""
    try:
        content = ERROR_JOURNAL.read_text() if ERROR_JOURNAL.exists() else "# STV Error Journal\n\n## Log\n"
        content += entry
        ERROR_JOURNAL.write_text(content)
    except Exception as e:
        print(f"  Failed to write to error journal: {e}")


def check_cron_jobs():
    """Verify cron jobs are still installed (VPS only — skipped if no crontab)."""
    print("Checking cron jobs...")
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        cron_content = result.stdout

        # If there's no #STV cron at all, assume this isn't the VPS — skip silently.
        if "#STV" not in cron_content:
            print("  (no #STV crontab — non-VPS environment, skipping)")
            return True

        expected_jobs = [
            "site_autopilot",
            "security_monitor",
            "threat_scanner",
            "security_selftest",
            "verify_dependencies",
            "system_doctor",
        ]

        missing = []
        for job in expected_jobs:
            if job not in cron_content:
                missing.append(job)

        if missing:
            send_alert("cron", f"Missing cron jobs: {', '.join(missing)}", "warning",
                       "Run: bash tools/setup_cron.sh to reinstall")
            log_to_error_journal(
                "Cron Jobs",
                f"Missing cron jobs: {', '.join(missing)}",
                "Cron jobs may have been removed or not installed",
                "Alert sent. Run 'bash tools/setup_cron.sh' to reinstall",
                "Needs Manual Intervention",
            )
            return False
        else:
            print(f"  ✓ All {len(expected_jobs)} cron jobs present")
            return True
    except Exception:
        print("  (crontab not available)")
        return True


def run_daily_check():
    """Daily comprehensive system check — deep dive on errors."""
    print("\n═══ Daily System Check ═══")
    results = {}

    results["uptime"] = check_uptime()
    results["ssl"] = check_ssl_expiry()
    results["disk"] = check_disk()
    results["cron_jobs"] = check_cron_jobs()

    # Summary
    failed = [k for k, v in results.items() if not v]
    if failed:
        summary = f"Daily check: {len(failed)} issue(s) — {', '.join(failed)}"
        send_alert("daily_check", summary, "warning")
    else:
        print("\n  ✓ All daily checks passed")
        # Only alert on success once a week (don't spam)
        health = load_health()
        last_ok = health.get("daily_ok_alert", {}).get("last_checked")
        if not last_ok or (datetime.now() - datetime.fromisoformat(last_ok)).days >= 7:
            send_alert("daily_check", "All systems operating normally", "success")
            save_health("daily_ok_alert", {"status": "ok"})

    save_health("daily_check", {
        "results": results,
        "failed": failed,
    })

    return len(failed) == 0


def generate_weekly_digest():
    """Generate a summary of all health checks."""
    print("\n═══ Weekly Health Digest ═══")
    results = {}

    results["uptime"] = check_uptime()
    results["ssl"] = check_ssl_expiry()
    results["disk"] = check_disk()
    results["broken_links"] = check_broken_links()
    results["content_dates"] = check_content_dates()

    # Build digest
    ok_count = sum(1 for v in results.values() if v)
    total = len(results)
    status = "✅ All OK" if ok_count == total else f"⚠️ {total - ok_count} issues found"

    digest = f"""STV Weekly Health Digest — {datetime.now().strftime('%Y-%m-%d')}

Status: {status} ({ok_count}/{total} checks passed)

Checks:
"""
    for check, passed in results.items():
        icon = "✓" if passed else "✗"
        digest += f"  {icon} {check}\n"

    print(digest)

    # Send digest via all channels
    send_telegram(digest.replace("*", ""), "info")
    log_to_dashboard("weekly_digest", status, "info", digest)

    save_health("weekly_digest", {
        "results": {k: v for k, v in results.items()},
        "status": status,
    })

    return all(results.values())


# ─── Health Log ────────────────────────────────────────────────────────────

def load_health():
    """Load health check history."""
    if HEALTH_LOG.exists():
        try:
            return json.loads(HEALTH_LOG.read_text())
        except Exception:
            return {}
    return {}


def save_health(check_name, data):
    """Save health check result."""
    health = load_health()
    health[check_name] = {
        "data": data,
        "last_checked": datetime.now().isoformat(),
    }
    HEALTH_LOG.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_LOG.write_text(json.dumps(health, indent=2))


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="STV Site Autopilot")
    parser.add_argument("--check", required=True,
                        choices=["uptime", "daily", "weekly", "links", "disk",
                                 "content-dates", "ssl", "cron", "all"],
                        help="Which check to run")
    args = parser.parse_args()

    print(f"STV Autopilot — {args.check} check — {datetime.now().isoformat()}")
    print()

    if args.check == "uptime":
        check_uptime()
    elif args.check == "ssl":
        check_ssl_expiry()
    elif args.check == "disk":
        check_disk()
    elif args.check == "links":
        check_broken_links()
    elif args.check == "content-dates":
        check_content_dates()
    elif args.check == "cron":
        check_cron_jobs()
    elif args.check == "daily":
        run_daily_check()
    elif args.check == "weekly":
        generate_weekly_digest()
    elif args.check == "all":
        generate_weekly_digest()

    print("\nDone.")


if __name__ == "__main__":
    main()
