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
DASHBOARD_URL = "https://app.socialtradingvlog.com"

# Key pages to check for uptime
UPTIME_URLS = [
    SITE_URL,
    f"{SITE_URL}/calculators/",
    f"{SITE_URL}/calculators/compare-platforms/",
    f"{SITE_URL}/calculators/fee-calculator/",
    DASHBOARD_URL,
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


def send_email(subject, body, level="info"):
    """Send alert via Resend API."""
    try:
        config = load_alert_config()
        if not config or not config.get("api_key"):
            return False

        payload = json.dumps({
            "from": config["from_email"],
            "to": [config["to_email"]],
            "subject": f"[STV {level.upper()}] {subject}",
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
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.getcode() == 200
    except Exception as e:
        print(f"  Email alert failed: {e}")
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

    # Keep last 500 alerts
    alerts = alerts[-500:]

    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    ALERT_LOG.write_text(json.dumps(alerts, indent=2))


def send_alert(alert_type, message, level="info", details=None):
    """Send alert via all configured channels."""
    print(f"  [{level.upper()}] {message}")
    log_to_dashboard(alert_type, message, level, details)

    if level in ("critical", "warning"):
        send_telegram(message, level)
        send_email(alert_type, f"{message}\n\n{details or ''}", level)


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
        days_left = (expiry - datetime.utcnow()).days

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
    """Scan HTML files for broken internal and external links."""
    print("Checking for broken links...")
    broken = []
    checked = 0

    # Find all HTML files
    html_files = list(PROJECT_DIR.glob("**/*.html"))
    # Exclude node_modules, .git, tools
    html_files = [f for f in html_files if not any(
        skip in str(f) for skip in [".git", "node_modules", "tools/"]
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
                elif link.startswith("mailto:") or link.startswith("javascript:"):
                    continue
                else:
                    # Internal link — check file exists
                    if link.startswith("/"):
                        target = PROJECT_DIR / link.lstrip("/")
                    else:
                        target = html_file.parent / link

                    # Try with and without index.html
                    if target.is_dir():
                        target = target / "index.html"
                    if not target.exists() and not target.with_suffix(".html").exists():
                        broken.append({"file": str(html_file.relative_to(PROJECT_DIR)), "link": link, "type": "internal"})
        except Exception:
            continue

    # Check a sample of external URLs (max 50 to avoid rate limits)
    external_sample = list(external_urls)[:50]
    for url in external_sample:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "STV-LinkChecker/1.0"}, method="HEAD")
            resp = urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
            checked += 1
            time.sleep(0.3)  # Rate limit
        except urllib.error.HTTPError as e:
            if e.code in (404, 410, 403):
                broken.append({"url": url, "status": e.code, "type": "external"})
            checked += 1
        except Exception:
            checked += 1

    if broken:
        send_alert("broken_links", f"Found {len(broken)} broken links", "warning",
                   json.dumps(broken[:20], indent=2))
    else:
        print(f"  ✓ No broken links found ({checked} external URLs checked)")

    save_health("broken_links", {"broken_count": len(broken), "checked": checked, "broken": broken[:50]})
    return len(broken) == 0


def check_content_dates():
    """Find pages with stale year references."""
    print("Checking content dates...")
    current_year = datetime.now().year
    stale = []

    html_files = list(PROJECT_DIR.glob("**/*.html"))
    html_files = [f for f in html_files if not any(
        skip in str(f) for skip in [".git", "node_modules", "tools/"]
    )]

    # Look for year references that are more than 1 year old
    year_pattern = re.compile(r'\b(20[12]\d)\b')

    for html_file in html_files:
        try:
            content = html_file.read_text(encoding="utf-8", errors="ignore")
            years = year_pattern.findall(content)
            old_years = [y for y in years if int(y) < current_year - 1]
            if old_years:
                stale.append({
                    "file": str(html_file.relative_to(PROJECT_DIR)),
                    "old_years": list(set(old_years)),
                })
        except Exception:
            continue

    if stale:
        send_alert("content_dates", f"{len(stale)} pages have potentially stale year references", "info",
                   json.dumps(stale[:20], indent=2))
    else:
        print(f"  ✓ All content dates look current")

    save_health("content_dates", {"stale_count": len(stale), "stale": stale[:50]})
    return len(stale) == 0


def check_services():
    """Check that systemd services are running (VPS only)."""
    print("Checking services...")
    services = ["stv-dashboard"]
    all_ok = True

    for svc in services:
        try:
            result = subprocess.run(
                ["systemctl", "is-active", svc],
                capture_output=True, text=True,
            )
            status = result.stdout.strip()
            if status == "active":
                print(f"  ✓ {svc}: active")
            else:
                send_alert("service", f"Service {svc} is {status}!", "critical")
                all_ok = False
        except FileNotFoundError:
            print(f"  (systemctl not available — skipping service check)")
            break

    save_health("services", {"checked": services})
    return all_ok


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


def check_subtitle_pipeline():
    """Check subtitle pipeline health — is it producing output?"""
    print("Checking subtitle pipeline...")
    issues = []

    # Check if pipeline is running
    try:
        result = subprocess.run(["pgrep", "-f", "run_pipeline.py"], capture_output=True, text=True)
        pipeline_running = result.returncode == 0
    except Exception:
        pipeline_running = False

    # Check pipeline log for recent activity
    pipeline_log = PROJECT_DIR / "transcriptions" / "pipeline.log"
    if pipeline_log.exists():
        stat = pipeline_log.stat()
        hours_since_update = (time.time() - stat.st_mtime) / 3600
        if hours_since_update > 24:
            issues.append(f"Pipeline log hasn't been updated in {int(hours_since_update)} hours")
    else:
        issues.append("Pipeline log not found")

    # Check for stuck translations
    try:
        result = subprocess.run(["pgrep", "-f", "translate_subtitles"], capture_output=True, text=True)
        translate_pids = result.stdout.strip().split("\n") if result.stdout.strip() else []
        if len(translate_pids) > 3:
            issues.append(f"{len(translate_pids)} translate processes running (possible stuck/duplicate)")
            # Auto-fix: kill excess processes, keep newest
            if len(translate_pids) > 3:
                for pid in translate_pids[:-1]:
                    try:
                        subprocess.run(["kill", pid.strip()], capture_output=True)
                    except Exception:
                        pass
                log_to_error_journal(
                    "Subtitle Pipeline",
                    f"{len(translate_pids)} duplicate translate processes detected",
                    "Multiple pipeline starts without cleanup spawned competing processes",
                    f"Auto-killed {len(translate_pids) - 1} excess processes, kept newest",
                )
    except Exception:
        pass

    # Check upload status
    upload_log = PROJECT_DIR / "reports" / "subtitle-uploads.json"
    if upload_log.exists():
        uploads = json.loads(upload_log.read_text())
        total = sum(len(v) for v in uploads.values())
        print(f"  Uploads: {total} tracks across {len(uploads)} videos")
    else:
        print("  No uploads yet")

    # Count progress
    try:
        trans_dir = PROJECT_DIR / "transcriptions"
        complete = 0
        has_en = 0
        total_dirs = 0
        for d in trans_dir.iterdir():
            if not d.is_dir() or d.name.startswith("."):
                continue
            total_dirs += 1
            if (d / "subtitles.en.srt").exists():
                has_en += 1
                all_done = all((d / f"subtitles.{lang}.srt").exists()
                              for lang in ["es", "de", "fr", "it", "pt", "ar", "pl", "nl", "ko"])
                if all_done:
                    complete += 1
        print(f"  Progress: {complete}/{total_dirs} fully complete, {has_en} have English")
    except Exception:
        pass

    if issues:
        for issue in issues:
            send_alert("subtitle_pipeline", issue, "warning")
        return False

    print("  ✓ Subtitle pipeline OK")
    return True


def check_platform_data_freshness():
    """Check if platform comparison data has been verified recently."""
    print("Checking platform data freshness...")
    verified_file = PROJECT_DIR / "data" / "platform-verified.json"

    if not verified_file.exists():
        send_alert("platform_data", "Platform data has never been verified! Run scrape_platform_fees.py", "warning")
        return False

    verified = json.loads(verified_file.read_text())
    last_check = verified.get("_last_full_check")

    if last_check:
        last_dt = datetime.fromisoformat(last_check)
        days_ago = (datetime.now() - last_dt).days

        if days_ago > 14:
            send_alert("platform_data", f"Platform data hasn't been verified in {days_ago} days!", "warning")
            # Auto-fix: run the scraper
            print(f"  Auto-running platform fee scraper...")
            try:
                subprocess.run(
                    [sys.executable, str(PROJECT_DIR / "tools" / "scrape_platform_fees.py")],
                    capture_output=True, text=True, timeout=300,
                )
                log_to_error_journal(
                    "Platform Data",
                    f"Data hadn't been verified in {days_ago} days",
                    "Weekly scraper cron may have failed",
                    "Auto-ran scrape_platform_fees.py to update data",
                )
            except Exception as e:
                print(f"  Auto-scrape failed: {e}")
            return False
        elif days_ago > 7:
            send_alert("platform_data", f"Platform data last verified {days_ago} days ago", "info")
        else:
            print(f"  ✓ Platform data verified {days_ago} days ago")
    else:
        send_alert("platform_data", "No verification timestamp found", "warning")
        return False

    return True


def check_cron_jobs():
    """Verify cron jobs are still installed."""
    print("Checking cron jobs...")
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        cron_content = result.stdout

        expected_jobs = [
            "site_autopilot",
            "scrape_platform_fees",
            "upload_subtitles",
            "link_prospector",
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
    results["services"] = check_services()
    results["subtitle_pipeline"] = check_subtitle_pipeline()
    results["platform_data"] = check_platform_data_freshness()
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
    results["services"] = check_services()
    results["broken_links"] = check_broken_links()
    results["content_dates"] = check_content_dates()

    # Read health log for summary
    health = load_health()

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

    # Add subtitle pipeline status
    pipeline_log = PROJECT_DIR / "transcriptions" / "pipeline.log"
    if pipeline_log.exists():
        lines = pipeline_log.read_text().strip().split("\n")
        last_lines = lines[-5:] if len(lines) >= 5 else lines
        digest += f"\nSubtitle Pipeline (last activity):\n"
        for line in last_lines:
            digest += f"  {line}\n"

    # Add upload status
    upload_log = PROJECT_DIR / "reports" / "subtitle-uploads.json"
    if upload_log.exists():
        uploads = json.loads(upload_log.read_text())
        total_uploaded = sum(len(langs) for langs in uploads.values())
        digest += f"\nSubtitle Uploads: {total_uploaded} tracks across {len(uploads)} videos\n"

    print(digest)

    # Send digest via all channels
    send_telegram(digest.replace("*", ""), "info")
    send_email("Weekly Health Digest", digest, "info")
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
                                 "content-dates", "ssl", "services", "pipeline",
                                 "platform-data", "cron", "all"],
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
    elif args.check == "services":
        check_services()
    elif args.check == "pipeline":
        check_subtitle_pipeline()
    elif args.check == "platform-data":
        check_platform_data_freshness()
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
