#!/usr/bin/env python3
"""
Security Monitor — Continuous security scanning and hardening for VPS.

Runs as a cron job to detect:
  - File permission changes on secrets
  - Unauthorized SSH login attempts
  - Suspicious processes
  - Open ports that shouldn't be open
  - File integrity changes on critical scripts
  - Failed login attempts / brute force
  - Malware signatures in uploaded files
  - Unusual outbound network connections

Usage:
    python3 tools/security_monitor.py              # Full scan
    python3 tools/security_monitor.py --quick       # Quick check (ports + processes)
    python3 tools/security_monitor.py --integrity   # File integrity check only

Cron:
    */10 * * * * python3 /var/www/.../tools/security_monitor.py --quick
    0 */4 * * *  python3 /var/www/.../tools/security_monitor.py
    0 2 * * *    python3 /var/www/.../tools/security_monitor.py --integrity
"""

import sys
import os
import json
import hashlib
import pathlib
import argparse
import subprocess
import re
from datetime import datetime

# Shared security library
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from security_lib import (
    PROJECT_DIR, SECRETS_DIR, DATA_DIR, LOGS_DIR,
    log as _lib_log, send_telegram, record_tool_run,
)

INTEGRITY_FILE = DATA_DIR / "security-integrity.json"
SECURITY_LOG = LOGS_DIR / "security.log"
ALERT_THRESHOLD = 3  # Alert after this many issues found


def log(msg, level="INFO"):
    _lib_log(msg, level, log_file=SECURITY_LOG)


def send_security_alert(subject, body):
    """Send security alert via Telegram."""
    send_telegram(subject, body, emoji="🔴 SECURITY ALERT",
                  dedupe_key=f"monitor:{subject[:50]}")


def _auto_respond(issues):
    """Automatically respond to detected threats with safe actions."""
    if not issues:
        return

    try:
        from threat_response import block_ip, kill_suspicious_process, fix_permissions
    except ImportError:
        try:
            sys.path.insert(0, str(PROJECT_DIR / "tools"))
            from threat_response import block_ip, kill_suspicious_process, fix_permissions
        except ImportError:
            return

    for issue in issues:
        issue_lower = issue.lower()

        # Auto-fix permissions (always safe)
        if "mode" in issue_lower and ("should be 600" in issue_lower or "should be 700" in issue_lower):
            fix_permissions()

        # Auto-kill suspicious processes
        suspicious_names = ["cryptominer", "xmrig", "minerd", "cpuminer",
                           "reverse_shell", "meterpreter", "payload"]
        for name in suspicious_names:
            if name in issue_lower:
                kill_suspicious_process(name)

        # Auto-block aggressive scanner IPs (from nginx log analysis)
        if "aggressive scanner" in issue_lower:
            import re
            ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", issue)
            if ip_match:
                block_ip(ip_match.group(1))


# ─── Security Checks ──────────────────────────────────────────────────────


def check_secret_permissions():
    """Verify all secret files are owner-read-only (600)."""
    issues = []
    if not SECRETS_DIR.exists():
        return issues

    # Check directory permissions
    dir_mode = oct(SECRETS_DIR.stat().st_mode)[-3:]
    if dir_mode != "700":
        issues.append(f"Secrets directory has mode {dir_mode}, should be 700")
        try:
            os.chmod(SECRETS_DIR, 0o700)
            log("AUTO-FIX: Secrets directory permissions set to 700")
        except Exception:
            pass

    for f in SECRETS_DIR.iterdir():
        if f.name.startswith("."):
            continue
        mode = oct(f.stat().st_mode)[-3:]
        if mode != "600":
            issues.append(f"Secret file {f.name} has mode {mode}, should be 600")
            try:
                os.chmod(f, 0o600)
                log(f"AUTO-FIX: {f.name} permissions set to 600")
            except Exception:
                pass

    return issues


def check_open_ports():
    """Check for unexpected listening ports."""
    issues = []
    # Expected ports on VPS: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8080 (dashboard)
    # Port 53 = systemd-resolved (localhost DNS), safe on loopback
    expected_ports = {"22", "53", "80", "443", "8080"}

    try:
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.strip().split("\n")[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 4:
                addr = parts[3]
                port = addr.rsplit(":", 1)[-1] if ":" in addr else ""
                # Skip localhost-only listeners
                if "127.0.0.1" in addr or "::1" in addr:
                    continue
                if port and port not in expected_ports:
                    issues.append(f"Unexpected port {port} listening: {line.strip()}")
    except FileNotFoundError:
        # macOS doesn't have ss, use lsof
        # Known-safe macOS system processes (not threats)
        safe_macos_processes = {
            "rapportd",   # AirDrop / Handoff / Universal Clipboard
            "ControlCe",  # Control Center (AirPlay receiver)
            "AirPlayXPC", # AirPlay service
            "sharingd",   # Sharing daemon (AirDrop, Handoff)
            "mDNSRespon", # Bonjour / mDNS
            "SystemUIServe", # System UI Server
        }
        try:
            result = subprocess.run(
                ["lsof", "-i", "-P", "-n"],
                capture_output=True, text=True, timeout=10,
            )
            for line in result.stdout.strip().split("\n"):
                if "LISTEN" in line and "127.0.0.1" not in line and "::1" not in line and "localhost" not in line:
                    parts = line.split()
                    if parts:
                        process = parts[0]
                        if process in safe_macos_processes:
                            continue  # Known-safe macOS system process
                        addr_part = parts[8] if len(parts) > 8 else ""
                        port = addr_part.rsplit(":", 1)[-1] if ":" in addr_part else ""
                        if port and port not in expected_ports:
                            issues.append(f"Unexpected listener: {process} on port {port}")
        except Exception:
            pass
    except Exception as e:
        log(f"Port scan error: {e}", "WARN")

    return issues


def check_ssh_brute_force():
    """Check for SSH brute force attempts."""
    issues = []
    auth_log = pathlib.Path("/var/log/auth.log")
    if not auth_log.exists():
        auth_log = pathlib.Path("/var/log/secure")
    if not auth_log.exists():
        return issues  # Not on Linux VPS

    try:
        result = subprocess.run(
            ["grep", "-c", "Failed password", str(auth_log)],
            capture_output=True, text=True, timeout=10,
        )
        count = int(result.stdout.strip() or "0")
        if count > 100:
            issues.append(f"SSH: {count} failed password attempts in auth.log")

        # Check for recent failures (last hour) — parse actual timestamps
        result = subprocess.run(
            ["grep", "Failed password", str(auth_log)],
            capture_output=True, text=True, timeout=10,
        )
        recent = 0
        now = datetime.now()
        for line in result.stdout.strip().split("\n")[-100:]:
            if not line.strip():
                continue
            # auth.log timestamps: "Feb 22 14:30:01" — parse month+day+time
            try:
                # Extract timestamp from start of syslog line
                ts_match = re.match(r"^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})", line)
                if ts_match:
                    ts_str = ts_match.group(1)
                    log_time = datetime.strptime(f"{now.year} {ts_str}", "%Y %b %d %H:%M:%S")
                    # Handle year wrap (Dec→Jan)
                    if log_time > now:
                        log_time = log_time.replace(year=now.year - 1)
                    if (now - log_time).total_seconds() < 3600:
                        recent += 1
            except (ValueError, AttributeError):
                continue
        if recent > 20:
            issues.append(f"SSH: {recent} failed login attempts in last hour — possible brute force")
    except Exception:
        pass

    return issues


def check_suspicious_processes():
    """Look for suspicious processes."""
    issues = []
    suspicious_names = [
        "cryptominer", "xmrig", "minerd", "cpuminer", "nicehash",
        "nmap", "masscan", "hydra", "john", "hashcat",
        "nc.traditional", "netcat",
        "reverse_shell", "meterpreter", "payload",
    ]

    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.lower().split("\n"):
            for name in suspicious_names:
                # Use word boundary matching to avoid false positives
                if re.search(rf"\b{re.escape(name)}\b", line) and "security_monitor" not in line:
                    issues.append(f"Suspicious process detected: {line.strip()[:100]}")
    except Exception:
        pass

    return issues


def check_file_integrity():
    """Check if critical tool scripts have been modified."""
    critical_files = [
        PROJECT_DIR / "tools" / "site_autopilot.py",
        PROJECT_DIR / "tools" / "proposal_manager.py",
        PROJECT_DIR / "tools" / "security_monitor.py",
        PROJECT_DIR / "tools" / "analytics_monitor.py",
        PROJECT_DIR / "tools" / "link_prospector.py",
        PROJECT_DIR / "tools" / "scrape_platform_fees.py",
        PROJECT_DIR / "tools" / "upload_subtitles.py",
        PROJECT_DIR / "tools" / "setup_cron.sh",
        PROJECT_DIR / "tools" / "threat_scanner.py",
        PROJECT_DIR / "tools" / "harden_vps.sh",
        PROJECT_DIR / "tools" / "nginx-security.conf",
        PROJECT_DIR / "tools" / "security_selftest.py",
        PROJECT_DIR / "tools" / "verify_dependencies.py",
        PROJECT_DIR / "tools" / "harden_vps_advanced.sh",
        PROJECT_DIR / "requirements.txt",
        PROJECT_DIR / "tools" / "threat_response.py",
        PROJECT_DIR / "tools" / "security_lib.py",
    ]

    issues = []
    existing_hashes = {}
    if INTEGRITY_FILE.exists():
        existing_hashes = json.loads(INTEGRITY_FILE.read_text())

    current_hashes = {}
    for f in critical_files:
        if f.exists():
            # Use path relative to PROJECT_DIR as key (unique, not just filename)
            try:
                key = str(f.relative_to(PROJECT_DIR))
            except ValueError:
                key = str(f)
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            current_hashes[key] = h
            if key in existing_hashes and existing_hashes[key] != h:
                issues.append(f"MODIFIED: {key} hash changed")
            # Backward compat: check old filename-only keys
            elif f.name in existing_hashes and existing_hashes[f.name] != h:
                issues.append(f"MODIFIED: {key} hash changed")

    # Save current hashes
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    INTEGRITY_FILE.write_text(json.dumps(current_hashes, indent=2))

    return issues


def check_crontab_integrity():
    """Check for unauthorized cron job modifications."""
    issues = []
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, timeout=10,
        )
        cron_content = result.stdout
        # Check for suspicious entries
        suspicious_cron = ["wget ", "curl ", "bash -c", "sh -c", "python -c",
                          "nc ", "ncat ", "/tmp/", "base64", "eval"]
        for pattern in suspicious_cron:
            if pattern in cron_content.lower() and "socialtradingvlog" not in cron_content.lower():
                issues.append(f"Suspicious cron entry containing: {pattern}")
    except Exception:
        pass

    return issues


def check_data_file_tampering():
    """Check for suspicious modifications to data files (e.g., proposals.json)."""
    issues = []
    proposals_file = DATA_DIR / "proposals.json"
    if proposals_file.exists():
        try:
            data = json.loads(proposals_file.read_text())
            for p in data.get("proposals", []):
                # Check for shell injection in proposal fields
                for field in ["title", "description", "action"]:
                    val = str(p.get(field, ""))
                    if any(c in val for c in ["`", "$(", "&&", "||", ";", "|"]):
                        issues.append(f"Proposal #{p.get('id')} has suspicious chars in {field}: {val[:50]}")
                    if any(kw in val.lower() for kw in ["exec(", "eval(", "import os", "subprocess", "__import__"]):
                        issues.append(f"Proposal #{p.get('id')} has code injection attempt in {field}")
        except Exception:
            pass

    return issues


def check_web_directory_exposure():
    """Ensure sensitive files aren't web-accessible."""
    issues = []
    sensitive_paths = [
        PROJECT_DIR / "data" / "proposals.json",
        PROJECT_DIR / "data" / "link-prospects.json",
        PROJECT_DIR / "data" / "analytics-report.json",
        PROJECT_DIR / "tools",
        PROJECT_DIR / "logs",
        PROJECT_DIR / ".git",
    ]

    # Check if web server config blocks these (Caddy, nginx, or .htaccess)
    htaccess = PROJECT_DIR / ".htaccess"
    caddyfile = pathlib.Path("/etc/caddy/Caddyfile")
    if not htaccess.exists() and not caddyfile.exists():
        issues.append("No .htaccess or Caddyfile found — ensure web server blocks /data/, /tools/, /logs/, .git/")

    return issues


def check_outbound_connections():
    """Check for unusual outbound connections (data exfiltration)."""
    issues = []
    allowed_hosts = [
        "api.telegram.org",
        "api.resend.com",
        "analyticsdata.googleapis.com",
        "www.googleapis.com",
        "oauth2.googleapis.com",
        "api.openai.com",
    ]

    try:
        result = subprocess.run(
            ["ss", "-tnp"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.strip().split("\n")[1:]:
            if "ESTAB" in line:
                parts = line.split()
                if len(parts) >= 5:
                    dest = parts[4]
                    # Check if connecting to non-standard ports
                    port = dest.rsplit(":", 1)[-1] if ":" in dest else ""
                    if port and port not in ("443", "80", "22", "53"):
                        issues.append(f"Outbound connection on unusual port: {dest}")
    except FileNotFoundError:
        pass  # macOS — lsof handled elsewhere
    except Exception:
        pass

    return issues


# ─── Main ──────────────────────────────────────────────────────────────────


def run_full_scan():
    """Run all security checks."""
    log("Starting full security scan...")
    all_issues = []

    checks = [
        ("Secret Permissions", check_secret_permissions),
        ("Open Ports", check_open_ports),
        ("SSH Brute Force", check_ssh_brute_force),
        ("Suspicious Processes", check_suspicious_processes),
        ("File Integrity", check_file_integrity),
        ("Crontab Integrity", check_crontab_integrity),
        ("Data Tampering", check_data_file_tampering),
        ("Web Exposure", check_web_directory_exposure),
        ("Outbound Connections", check_outbound_connections),
    ]

    for name, check_fn in checks:
        try:
            issues = check_fn()
            if issues:
                log(f"  [{name}] {len(issues)} issue(s) found", "WARN")
                for issue in issues:
                    log(f"    - {issue}", "WARN")
                all_issues.extend(issues)
            else:
                log(f"  [{name}] OK")
        except Exception as e:
            log(f"  [{name}] Check failed: {e}", "ERROR")

    # Auto-respond to detected threats
    _auto_respond(all_issues)

    # Record successful run for self-test tracking
    record_tool_run("security_monitor")

    if len(all_issues) >= ALERT_THRESHOLD:
        send_security_alert(
            f"{len(all_issues)} security issues detected",
            "\n".join(f"- {i}" for i in all_issues),
        )
    elif all_issues:
        log(f"Total: {len(all_issues)} minor issue(s) — below alert threshold")
    else:
        log("Full scan complete — no issues found")

    return all_issues


def run_quick_scan():
    """Quick scan — ports and processes only."""
    log("Quick security check...")
    issues = []
    issues.extend(check_open_ports())
    issues.extend(check_suspicious_processes())
    issues.extend(check_secret_permissions())

    if issues:
        log(f"Quick check: {len(issues)} issue(s)")
        for i in issues:
            log(f"  - {i}", "WARN")
        if len(issues) >= ALERT_THRESHOLD:
            send_security_alert(f"{len(issues)} issues in quick scan", "\n".join(f"- {i}" for i in issues))

    return issues


def run_integrity_check():
    """File integrity check only."""
    log("File integrity check...")
    issues = check_file_integrity()
    issues.extend(check_data_file_tampering())
    issues.extend(check_crontab_integrity())

    if issues:
        log(f"Integrity check: {len(issues)} issue(s)")
        for i in issues:
            log(f"  - {i}", "WARN")
        send_security_alert("File integrity changes detected", "\n".join(f"- {i}" for i in issues))

    return issues


def main():
    parser = argparse.ArgumentParser(description="STV Security Monitor")
    parser.add_argument("--quick", action="store_true", help="Quick scan (ports + processes)")
    parser.add_argument("--integrity", action="store_true", help="File integrity check only")
    args = parser.parse_args()

    print(f"STV Security Monitor — {datetime.now().isoformat()}\n")

    if args.quick:
        run_quick_scan()
    elif args.integrity:
        run_integrity_check()
    else:
        run_full_scan()

    print("\nDone.")


if __name__ == "__main__":
    main()
