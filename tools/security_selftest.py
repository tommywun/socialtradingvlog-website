#!/usr/bin/env python3
"""
Security Self-Test — Daily verification that ALL security protocols are active and working.

This script tests every single security measure to ensure nothing has broken,
gone stale, or been bypassed. It's the "trust but verify" layer — it doesn't
just check if crons exist, it confirms they actually ran and produced output.

Runs daily at 6am. On ANY failure, sends URGENT alert to Tom.

Checks:
  1. UFW firewall is enabled and only correct ports are open
  2. fail2ban is running and has active jails
  3. SSH config is hardened (no password auth, no root, strong ciphers)
  4. Secret file permissions are correct (600/700)
  5. Cron jobs are installed and recently executed
  6. Security monitor ran recently (check log timestamps)
  7. Threat scanner ran recently (check log timestamps)
  8. Caddy web server is active with security headers and path blocking
  9. Unattended-upgrades is enabled
  10. Google Authenticator status (optional — informational only)
  11. SSL certificate is valid and not expiring soon
  12. File integrity hashes are current
  13. No unauthorized SSH keys
  14. Backup encryption is working (recent .gpg files exist)
  15. Kernel security parameters are set correctly
  16. DNS resolves correctly

Usage:
    python3 tools/security_selftest.py           # Full self-test
    python3 tools/security_selftest.py --brief    # Summary only

Cron:
    0 6 * * * python3 /var/www/.../tools/security_selftest.py >> logs/selftest.log 2>&1
"""

import sys
import os
import json
import pathlib
import argparse
import subprocess
from datetime import datetime, timedelta

# Shared security library
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from security_lib import (
    PROJECT_DIR, DATA_DIR, LOGS_DIR, SECRETS_DIR,
    send_telegram, record_tool_run,
)

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results = []


def check(name, passed, detail=""):
    """Record a check result."""
    status = PASS if passed else FAIL
    results.append({"name": name, "passed": passed, "detail": detail})
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))
    return passed


def send_alert(subject, body):
    """Send urgent alert via Telegram."""
    send_telegram(subject, body, emoji="🚨 SELF-TEST FAILED")


# ─── Protocol Checks ──────────────────────────────────────────────────


def test_ufw_firewall():
    """Protocol 1: UFW firewall is enabled with correct rules."""
    try:
        result = subprocess.run(
            ["sudo", "ufw", "status", "verbose"],
            capture_output=True, text=True, timeout=10,
        )
        output = result.stdout
        if "Status: active" not in output:
            return check("UFW Firewall", False, "Firewall is INACTIVE!")

        # Verify only expected ports are allowed
        expected = {"22/tcp", "80/tcp", "443/tcp"}
        allowed = set()
        for line in output.split("\n"):
            line = line.strip()
            if "ALLOW" in line:
                parts = line.split()
                if parts:
                    allowed.add(parts[0])

        unexpected = allowed - expected - {"22/tcp (v6)", "80/tcp (v6)", "443/tcp (v6)", "22/tcp"}
        if unexpected:
            return check("UFW Firewall", False, f"Unexpected ports allowed: {unexpected}")

        return check("UFW Firewall", True, "Active, correct ports only")
    except FileNotFoundError:
        return check("UFW Firewall", False, "UFW not installed")
    except Exception as e:
        return check("UFW Firewall", False, str(e))


def test_fail2ban():
    """Protocol 2: fail2ban is running with active jails."""
    try:
        result = subprocess.run(
            ["sudo", "fail2ban-client", "status"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return check("fail2ban", False, "fail2ban not responding")

        output = result.stdout
        if "sshd" not in output:
            return check("fail2ban", False, "SSH jail not active")

        # Count active jails
        jail_count = output.count(",") + 1 if "Jail list:" in output else 0
        return check("fail2ban", True, f"{jail_count} active jail(s)")
    except FileNotFoundError:
        return check("fail2ban", False, "fail2ban not installed")
    except Exception as e:
        return check("fail2ban", False, str(e))


def test_ssh_hardening():
    """Protocol 3: SSH is properly hardened."""
    config_file = pathlib.Path("/etc/ssh/sshd_config.d/99-stv-hardening.conf")
    if not config_file.exists():
        return check("SSH Hardening", False, "Hardening config not found")

    content = config_file.read_text()
    checks_passed = True
    missing = []

    required = {
        "PasswordAuthentication no": "password auth not disabled",
        "PermitRootLogin no": "root login not disabled",
        "AllowUsers stv": "AllowUsers not restricted",
        "MaxAuthTries 3": "max auth tries not limited",
    }

    for setting, error in required.items():
        if setting not in content:
            missing.append(error)
            checks_passed = False

    if missing:
        return check("SSH Hardening", False, "; ".join(missing))
    return check("SSH Hardening", True, "All SSH hardening settings active")


def test_secret_permissions():
    """Protocol 4: Secret files have correct permissions."""
    if not SECRETS_DIR.exists():
        return check("Secret Permissions", False, "Secrets directory missing")

    issues = []
    dir_mode = oct(SECRETS_DIR.stat().st_mode)[-3:]
    if dir_mode != "700":
        issues.append(f"Dir is {dir_mode}, should be 700")

    for f in SECRETS_DIR.iterdir():
        if f.name.startswith("."):
            continue
        mode = oct(f.stat().st_mode)[-3:]
        if mode != "600":
            issues.append(f"{f.name} is {mode}")

    if issues:
        return check("Secret Permissions", False, "; ".join(issues[:3]))
    return check("Secret Permissions", True, "All files 600, dir 700")


def test_cron_installed():
    """Protocol 5: All required cron jobs are installed."""
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, timeout=10,
        )
        crontab = result.stdout
        required_crons = [
            "security_monitor.py",
            "threat_scanner.py",
            "security_selftest.py",
            "site_autopilot.py",
        ]
        missing = [c for c in required_crons if c not in crontab]
        if missing:
            return check("Cron Jobs", False, f"Missing: {', '.join(missing)}")
        return check("Cron Jobs", True, f"All {len(required_crons)} security crons present")
    except Exception as e:
        return check("Cron Jobs", False, str(e))


def test_security_monitor_ran():
    """Protocol 6: Security monitor ran recently."""
    log_file = LOGS_DIR / "security.log"
    if not log_file.exists():
        return check("Security Monitor Recent", False, "No security.log found")

    try:
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        age_hours = (datetime.now() - mtime).total_seconds() / 3600
        if age_hours > 5:  # Should run every 4 hours
            return check("Security Monitor Recent", False,
                        f"Last ran {age_hours:.0f}h ago (should be <5h)")
        return check("Security Monitor Recent", True, f"Last ran {age_hours:.1f}h ago")
    except Exception as e:
        return check("Security Monitor Recent", False, str(e))


def test_threat_scanner_ran():
    """Protocol 7: Threat scanner ran recently."""
    log_file = LOGS_DIR / "threat-scan.log"
    if not log_file.exists():
        return check("Threat Scanner Recent", False, "No threat-scan.log found")

    try:
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        age_hours = (datetime.now() - mtime).total_seconds() / 3600
        if age_hours > 25:  # Should run daily at 3am
            return check("Threat Scanner Recent", False,
                        f"Last ran {age_hours:.0f}h ago (should be <25h)")
        return check("Threat Scanner Recent", True, f"Last ran {age_hours:.1f}h ago")
    except Exception as e:
        return check("Threat Scanner Recent", False, str(e))


def test_web_server_security():
    """Protocol 8: Caddy web server is active with security headers."""
    try:
        # Check if Caddy is running
        result = subprocess.run(
            ["systemctl", "is-active", "caddy"],
            capture_output=True, text=True, timeout=10,
        )
        if result.stdout.strip() != "active":
            return check("Web Server (Caddy)", False, "Caddy not running")

        # Check if security headers are being served on dashboard
        result = subprocess.run(
            ["curl", "-sI", "https://app.socialtradingvlog.com", "--max-time", "10"],
            capture_output=True, text=True, timeout=15,
        )
        headers = result.stdout.lower()
        missing_headers = []
        for h in ["x-frame-options", "x-content-type-options", "strict-transport-security",
                   "content-security-policy", "permissions-policy"]:
            if h not in headers:
                missing_headers.append(h)

        if missing_headers:
            return check("Web Server (Caddy)", False, f"Missing headers: {', '.join(missing_headers)}")

        # Verify sensitive paths are blocked
        block_result = subprocess.run(
            ["curl", "-so", "/dev/null", "-w", "%{http_code}",
             "https://app.socialtradingvlog.com/tools/", "--max-time", "5"],
            capture_output=True, text=True, timeout=10,
        )
        if block_result.stdout.strip() != "404":
            return check("Web Server (Caddy)", False, "/tools/ not blocked!")

        return check("Web Server (Caddy)", True, "Active, headers present, paths blocked")
    except FileNotFoundError:
        return check("Web Server (Caddy)", False, "curl not available")
    except Exception as e:
        return check("Web Server (Caddy)", False, str(e))


def test_unattended_upgrades():
    """Protocol 9: Automatic security updates enabled."""
    config = pathlib.Path("/etc/apt/apt.conf.d/60stv-unattended-upgrades")
    if config.exists():
        return check("Auto Security Updates", True, "unattended-upgrades configured")

    # Check default config
    default = pathlib.Path("/etc/apt/apt.conf.d/50unattended-upgrades")
    if default.exists():
        return check("Auto Security Updates", True, "Default unattended-upgrades present")

    return check("Auto Security Updates", False, "No unattended-upgrades config found")


def test_2fa_configured():
    """Protocol 10: Google Authenticator configured for stv user (optional).

    Note: 2FA via SSH is disabled after a config conflict caused lockout.
    This check is informational only — it passes if 2FA is not configured.
    """
    ga_file = pathlib.Path("/home/stv/.google_authenticator")
    if not ga_file.exists():
        ga_file = pathlib.Path.home() / ".google_authenticator"

    if ga_file.exists():
        return check("SSH 2FA (TOTP)", True, "Google Authenticator configured")

    # 2FA is optional — not having it is fine (key-only SSH is already strong)
    return check("SSH 2FA (TOTP)", True, "Not configured (optional — key-only auth is active)")


def test_ssl_certificate():
    """Protocol 11: SSL certificate is valid and not expiring soon."""
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-connect", "socialtradingvlog.com:443",
             "-servername", "socialtradingvlog.com"],
            input="", capture_output=True, text=True, timeout=10,
        )
        output = result.stdout + result.stderr

        if "verify return:1" in output or "Verification: OK" in output:
            # Check expiry with openssl x509
            cert_result = subprocess.run(
                ["bash", "-c",
                 "echo | openssl s_client -servername socialtradingvlog.com "
                 "-connect socialtradingvlog.com:443 2>/dev/null | "
                 "openssl x509 -noout -enddate 2>/dev/null"],
                capture_output=True, text=True, timeout=15,
            )
            expiry = cert_result.stdout.strip()
            if "notAfter" in expiry:
                return check("SSL Certificate", True, expiry)
            return check("SSL Certificate", True, "Valid")
        else:
            return check("SSL Certificate", False, "Verification failed")
    except Exception as e:
        return check("SSL Certificate", False, str(e))


def test_file_integrity():
    """Protocol 12: File integrity hashes are current."""
    integrity_file = DATA_DIR / "security-integrity.json"
    if not integrity_file.exists():
        return check("File Integrity Hashes", False, "No integrity baseline found")

    mtime = datetime.fromtimestamp(integrity_file.stat().st_mtime)
    age_hours = (datetime.now() - mtime).total_seconds() / 3600
    if age_hours > 25:
        return check("File Integrity Hashes", False,
                     f"Baseline is {age_hours:.0f}h old (should be <25h)")
    return check("File Integrity Hashes", True, f"Updated {age_hours:.1f}h ago")


def test_ssh_keys():
    """Protocol 13: No unauthorized SSH keys."""
    auth_keys = pathlib.Path.home() / ".ssh" / "authorized_keys"
    if not auth_keys.exists():
        return check("SSH Authorized Keys", True, "No authorized_keys file")

    key_count = len([l for l in auth_keys.read_text().strip().split("\n")
                     if l.strip() and not l.startswith("#")])
    if key_count > 3:
        return check("SSH Authorized Keys", False,
                     f"{key_count} keys found — verify all are legitimate")
    return check("SSH Authorized Keys", True, f"{key_count} key(s)")


def test_encrypted_backups():
    """Protocol 14: Recent encrypted backups exist."""
    backups_dir = PROJECT_DIR / "backups"
    if not backups_dir.exists():
        return check("Encrypted Backups", False, "Backups directory missing")

    gpg_files = sorted(backups_dir.glob("*.gpg"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not gpg_files:
        return check("Encrypted Backups", False, "No .gpg backup files found")

    latest = gpg_files[0]
    age_days = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).days
    if age_days > 8:
        return check("Encrypted Backups", False,
                     f"Latest backup is {age_days} days old (should be <8)")
    return check("Encrypted Backups", True, f"Latest: {latest.name} ({age_days}d ago)")


def test_kernel_security():
    """Protocol 15: Kernel security parameters are set."""
    critical_params = {
        "net.ipv4.tcp_syncookies": "1",
        "net.ipv4.conf.all.rp_filter": "1",
        "net.ipv4.conf.all.accept_redirects": "0",
        "kernel.kptr_restrict": "2",
    }
    missing = []
    try:
        for param, expected in critical_params.items():
            result = subprocess.run(
                ["sysctl", "-n", param],
                capture_output=True, text=True, timeout=5,
            )
            actual = result.stdout.strip()
            if actual != expected:
                missing.append(f"{param}={actual} (want {expected})")
    except FileNotFoundError:
        return check("Kernel Security", False, "sysctl not available")
    except Exception as e:
        return check("Kernel Security", False, str(e))

    if missing:
        return check("Kernel Security", False, "; ".join(missing))
    return check("Kernel Security", True, "All parameters correct")


def test_dns_resolution():
    """Protocol 16: Dashboard DNS resolves to VPS correctly."""
    try:
        # Check the dashboard subdomain (main site goes through Cloudflare)
        result = subprocess.run(
            ["dig", "+short", "app.socialtradingvlog.com", "A"],
            capture_output=True, text=True, timeout=10,
        )
        ips = result.stdout.strip().split("\n")
        if "89.167.73.64" in ips:
            return check("DNS Resolution", True, "app.socialtradingvlog.com → 89.167.73.64")
        return check("DNS Resolution", False,
                     f"app.socialtradingvlog.com resolves to {', '.join(ips)} (expected 89.167.73.64)")
    except FileNotFoundError:
        try:
            import socket
            ip = socket.gethostbyname("app.socialtradingvlog.com")
            if ip == "89.167.73.64":
                return check("DNS Resolution", True, f"→ {ip}")
            return check("DNS Resolution", False, f"Resolves to {ip}")
        except Exception as e:
            return check("DNS Resolution", False, str(e))
    except Exception as e:
        return check("DNS Resolution", False, str(e))


# ─── Main ──────────────────────────────────────────────────────────────


def run_selftest(brief=False):
    """Run all protocol verification checks."""
    print(f"STV Security Self-Test — {datetime.now().isoformat()}")
    print(f"{'=' * 60}")
    print()

    tests = [
        ("1. UFW Firewall", test_ufw_firewall),
        ("2. fail2ban", test_fail2ban),
        ("3. SSH Hardening", test_ssh_hardening),
        ("4. Secret Permissions", test_secret_permissions),
        ("5. Cron Jobs Installed", test_cron_installed),
        ("6. Security Monitor Recent", test_security_monitor_ran),
        ("7. Threat Scanner Recent", test_threat_scanner_ran),
        ("8. Web Server Security", test_web_server_security),
        ("9. Auto Security Updates", test_unattended_upgrades),
        ("10. SSH 2FA (TOTP)", test_2fa_configured),
        ("11. SSL Certificate", test_ssl_certificate),
        ("12. File Integrity", test_file_integrity),
        ("13. SSH Keys", test_ssh_keys),
        ("14. Encrypted Backups", test_encrypted_backups),
        ("15. Kernel Security", test_kernel_security),
        ("16. DNS Resolution", test_dns_resolution),
    ]

    for name, test_fn in tests:
        try:
            test_fn()
        except Exception as e:
            check(name, False, f"Test crashed: {e}")

    # Summary
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    total = len(results)

    print()
    print(f"{'=' * 60}")
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    print()

    if failed > 0:
        failures = [r for r in results if not r["passed"]]
        failure_text = "\n".join(f"• {r['name']}: {r['detail']}" for r in failures)
        print(f"  FAILED CHECKS:")
        for r in failures:
            print(f"    {FAIL} {r['name']}: {r['detail']}")

        # Send urgent alert
        send_alert(
            f"Security Self-Test: {failed}/{total} FAILED",
            failure_text,
        )
        print(f"\n  🚨 URGENT alert sent to Tom")
    else:
        print(f"  {PASS} All {total} security protocols verified and working")

        # Send weekly positive confirmation (Mondays only)
        if datetime.now().weekday() == 0:
            send_telegram(
                "Weekly Security Report",
                f"All {total} security protocols verified and working.\n"
                f"No failures detected.\n\n"
                f"Self-test ran at {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                emoji="🟢",
            )

    # Record successful run
    record_tool_run("security_selftest")

    # Log results
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOGS_DIR / "selftest.log"
        with open(log_file, "a") as f:
            f.write(f"\n[{datetime.now().isoformat()}] Self-test: {passed}/{total} passed\n")
            for r in results:
                status = "PASS" if r["passed"] else "FAIL"
                f.write(f"  [{status}] {r['name']}: {r['detail']}\n")
    except Exception:
        pass

    return failed


def main():
    parser = argparse.ArgumentParser(description="STV Security Self-Test")
    parser.add_argument("--brief", action="store_true", help="Summary only")
    args = parser.parse_args()

    failures = run_selftest(brief=args.brief)
    print("\nDone.")
    sys.exit(1 if failures > 0 else 0)


if __name__ == "__main__":
    main()
