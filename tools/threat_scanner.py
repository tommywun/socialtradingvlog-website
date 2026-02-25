#!/usr/bin/env python3
"""
Threat Scanner — Daily automated security threat intelligence and response.

Checks for:
  1. Known CVE advisories affecting our stack (caddy, python, openssh, ubuntu)
  2. Suspicious patterns in web server access logs (bot scanners, exploit attempts)
  3. AI agent attack patterns (OpenClaw-style skill injection, prompt injection)
  4. New SSH keys or authorized users added
  5. Package integrity (pip packages, system packages)
  6. SSL certificate validity and configuration
  7. DNS record tampering
  8. Unusual cron job additions

Runs daily at 3am via cron. Alerts via Telegram + email on findings.

Usage:
    python3 tools/threat_scanner.py                # Full daily scan
    python3 tools/threat_scanner.py --quick         # Quick scan only
    python3 tools/threat_scanner.py --check-cves    # CVE check only

Cron:
    0 3 * * * python3 /var/www/.../tools/threat_scanner.py >> logs/threat-scan.log 2>&1
"""

import sys
import os
import json
import pathlib
import argparse
import subprocess
import urllib.request
import urllib.error
import re
import hashlib
from datetime import datetime, timedelta

# Shared security library
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from security_lib import (
    PROJECT_DIR, DATA_DIR, LOGS_DIR, SECRETS_DIR,
    log as _lib_log, send_telegram, record_tool_run,
)

THREAT_LOG = LOGS_DIR / "threat-scan.log"
THREAT_DATA = DATA_DIR / "threat-intelligence.json"


def log(msg, level="INFO"):
    _lib_log(msg, level, log_file=THREAT_LOG)


def send_alert(subject, body):
    """Send threat alert via Telegram."""
    send_telegram(subject, body, emoji="🔴 THREAT ALERT",
                  dedupe_key=f"threat:{subject[:50]}")


def load_threat_data():
    """Load persistent threat intelligence data."""
    if THREAT_DATA.exists():
        return json.loads(THREAT_DATA.read_text())
    return {
        "last_scan": None,
        "known_ssh_keys": [],
        "known_packages_hash": None,
        "known_crontab_hash": None,
        "blocked_ips": [],
        "cve_alerts_sent": [],
        "scan_count": 0,
    }


def save_threat_data(data):
    """Save threat intelligence data."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    THREAT_DATA.write_text(json.dumps(data, indent=2))


# ─── Threat Checks ──────────────────────────────────────────────────────


def check_cve_advisories():
    """Check Ubuntu Security Notices for CVEs affecting our stack."""
    issues = []
    our_packages = ["caddy", "openssh", "python3", "openssl", "linux"]

    try:
        # Check Ubuntu Security Notices RSS
        url = "https://ubuntu.com/security/notices.rss"
        req = urllib.request.Request(url, headers={"User-Agent": "STV-ThreatScanner/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        content = resp.read().decode("utf-8", errors="replace")

        # Simple XML parsing — look for recent entries mentioning our packages
        entries = re.findall(r"<item>(.*?)</item>", content, re.DOTALL)
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()

        for entry in entries[:20]:  # Last 20 entries
            title = re.search(r"<title>(.*?)</title>", entry)
            link = re.search(r"<link>(.*?)</link>", entry)
            desc = re.search(r"<description>(.*?)</description>", entry, re.DOTALL)

            if title:
                title_text = title.group(1).lower()
                for pkg in our_packages:
                    if pkg in title_text:
                        issues.append(
                            f"CVE advisory for {pkg}: {title.group(1)}"
                            + (f" — {link.group(1)}" if link else "")
                        )
                        break
    except Exception as e:
        log(f"CVE check error: {e}", "WARN")

    # Also check CISA Known Exploited Vulnerabilities
    try:
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        req = urllib.request.Request(url, headers={"User-Agent": "STV-ThreatScanner/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())

        # Check for recent entries (last 14 days)
        cutoff = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
        for vuln in data.get("vulnerabilities", []):
            date_added = vuln.get("dateAdded", "")
            if date_added >= cutoff:
                vendor = vuln.get("vendorProject", "").lower()
                product = vuln.get("product", "").lower()
                # Check if it affects anything in our stack
                for pkg in our_packages + ["ubuntu", "debian", "apache", "node"]:
                    if pkg in vendor or pkg in product:
                        cve_id = vuln.get("cveID", "Unknown")
                        desc = vuln.get("shortDescription", "")[:100]
                        issues.append(
                            f"CISA KEV: {cve_id} — {vendor}/{product}: {desc}"
                        )
                        break
    except Exception as e:
        log(f"CISA KEV check error: {e}", "WARN")

    return issues


def check_web_server_attack_patterns():
    """Analyze web server access logs for attack patterns (Caddy or nginx)."""
    issues = []
    # Try Caddy first, then nginx
    access_log = pathlib.Path("/var/log/caddy/access.log")
    if not access_log.exists():
        access_log = pathlib.Path("/var/log/nginx/access.log")
    if not access_log.exists():
        return issues

    try:
        result = subprocess.run(
            ["tail", "-5000", str(access_log)],
            capture_output=True, text=True, timeout=10,
        )

        attack_patterns = {
            r"\.\.\/": "path traversal",
            r"(union|select|insert|delete|drop)\s": "SQL injection",
            r"<script": "XSS attempt",
            r"\.(env|git|htpasswd|htaccess)": "sensitive file probe",
            r"(wp-admin|wp-login|xmlrpc|phpmyadmin)": "WordPress/PHP scanner",
            r"(shell|cmd|exec|system)\(": "RCE attempt",
            r"(etc/passwd|etc/shadow|proc/self)": "LFI attempt",
            r"(base64_decode|eval\(|assert\()": "code injection",
            r"(\.aspx|\.jsp|\.cgi)": "technology probe",
        }

        attack_counts = {}
        attacker_ips = {}

        is_caddy_json = "caddy" in str(access_log)

        for line in result.stdout.split("\n"):
            if not line.strip():
                continue

            # Extract request URI and client IP from Caddy JSON or nginx combined format
            request_uri = ""
            client_ip = ""
            if is_caddy_json:
                try:
                    entry = json.loads(line)
                    req = entry.get("request", {})
                    request_uri = req.get("uri", "")
                    client_ip = req.get("remote_ip", entry.get("request", {}).get("remote_addr", "").split(":")[0])
                except (json.JSONDecodeError, ValueError):
                    request_uri = line
            else:
                request_uri = line
                ip_match = re.match(r"^(\d+\.\d+\.\d+\.\d+)", line)
                if ip_match:
                    client_ip = ip_match.group(1)

            line_lower = request_uri.lower() if request_uri else line.lower()
            for pattern, name in attack_patterns.items():
                if re.search(pattern, line_lower):
                    attack_counts[name] = attack_counts.get(name, 0) + 1
                    if client_ip:
                        attacker_ips[client_ip] = attacker_ips.get(client_ip, 0) + 1

        for name, count in attack_counts.items():
            if count > 10:
                issues.append(f"Web: {count} {name} attempts detected")

        # Report top attackers
        top_attackers = sorted(attacker_ips.items(), key=lambda x: -x[1])[:5]
        for ip, count in top_attackers:
            if count > 20:
                issues.append(f"Aggressive scanner: {ip} ({count} attack attempts)")

    except Exception as e:
        log(f"Web server log analysis error: {e}", "WARN")

    return issues


def check_ssh_key_tampering():
    """Check if SSH authorized_keys has been modified."""
    issues = []
    auth_keys = pathlib.Path.home() / ".ssh" / "authorized_keys"
    if not auth_keys.exists():
        return issues

    try:
        current_hash = hashlib.sha256(auth_keys.read_bytes()).hexdigest()
        threat_data = load_threat_data()

        if threat_data.get("known_ssh_keys_hash"):
            if threat_data["known_ssh_keys_hash"] != current_hash:
                issues.append(
                    "SSH authorized_keys file has been MODIFIED! "
                    "Possible unauthorized key addition."
                )
        # Update stored hash
        threat_data["known_ssh_keys_hash"] = current_hash
        save_threat_data(threat_data)

        # Check for suspicious key comments
        content = auth_keys.read_text()
        key_count = len([l for l in content.strip().split("\n") if l.strip() and not l.startswith("#")])
        if key_count > 3:
            issues.append(f"SSH: {key_count} authorized keys found — verify all are legitimate")

    except Exception as e:
        log(f"SSH key check error: {e}", "WARN")

    return issues


def check_package_integrity():
    """Verify no unexpected packages have been installed."""
    issues = []
    try:
        result = subprocess.run(
            ["dpkg", "--get-selections"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            current_hash = hashlib.sha256(result.stdout.encode()).hexdigest()
            threat_data = load_threat_data()

            if threat_data.get("known_packages_hash"):
                if threat_data["known_packages_hash"] != current_hash:
                    issues.append(
                        "System packages have changed since last scan. "
                        "Verify no unauthorized packages were installed."
                    )
            threat_data["known_packages_hash"] = current_hash
            save_threat_data(threat_data)
    except FileNotFoundError:
        pass  # Not on Debian/Ubuntu
    except Exception as e:
        log(f"Package integrity check error: {e}", "WARN")

    return issues


def check_ssl_certificate():
    """Check SSL certificate validity for main site and dashboard."""
    issues = []
    domains = ["socialtradingvlog.com", "app.socialtradingvlog.com"]

    for domain in domains:
        try:
            result = subprocess.run(
                ["openssl", "s_client", "-connect", f"{domain}:443",
                 "-servername", domain],
                input="", capture_output=True, text=True, timeout=10,
            )
            output = result.stdout + result.stderr

            if "verify return:1" not in output:
                issues.append(f"SSL verification failed for {domain}")

            for proto in ["TLSv1 ", "TLSv1.1 ", "SSLv3"]:
                if proto in output:
                    issues.append(f"Weak TLS protocol on {domain}: {proto.strip()}")

        except FileNotFoundError:
            break  # openssl not installed
        except Exception as e:
            log(f"SSL check error for {domain}: {e}", "WARN")

    return issues


def check_dns_integrity():
    """Verify DNS records haven't been tampered with."""
    issues = []
    expected_records = {
        # Main site goes through Cloudflare — don't check VPS IP
        # Only the dashboard subdomain should point to VPS
        "app.socialtradingvlog.com": "89.167.73.64",
    }

    for domain, expected_ip in expected_records.items():
        try:
            result = subprocess.run(
                ["dig", "+short", domain, "A"],
                capture_output=True, text=True, timeout=10,
            )
            actual_ips = result.stdout.strip().split("\n")
            if expected_ip not in actual_ips:
                issues.append(
                    f"DNS ALERT: {domain} resolves to {', '.join(actual_ips)} "
                    f"(expected {expected_ip}) — possible DNS hijacking!"
                )
        except FileNotFoundError:
            # Try nslookup as fallback
            try:
                result = subprocess.run(
                    ["nslookup", domain],
                    capture_output=True, text=True, timeout=10,
                )
                if expected_ip not in result.stdout:
                    issues.append(f"DNS may be tampered: {domain} doesn't resolve to {expected_ip}")
            except Exception:
                pass
        except Exception as e:
            log(f"DNS check error for {domain}: {e}", "WARN")

    return issues


def check_ai_agent_threats():
    """Check for AI agent attack patterns (OpenClaw-style attacks)."""
    issues = []

    # Check for signs of AI agent compromise
    suspicious_files = [
        pathlib.Path.home() / ".openclaw",
        pathlib.Path.home() / ".clawbot",
        pathlib.Path.home() / ".moltbot",
        pathlib.Path("/tmp") / "claw_skills",
        pathlib.Path("/tmp") / "ai_agent",
    ]

    for f in suspicious_files:
        if f.exists():
            issues.append(f"Suspicious AI agent directory found: {f}")

    # Check for AI agent processes
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True, text=True, timeout=10,
        )
        ai_agent_patterns = [
            "openclaw", "clawbot", "moltbot", "autogpt", "babyagi",
            "langchain serve", "agent_executor",
        ]
        for line in result.stdout.lower().split("\n"):
            for pattern in ai_agent_patterns:
                if pattern in line and "threat_scanner" not in line:
                    issues.append(f"AI agent process detected: {line.strip()[:100]}")
    except Exception:
        pass

    # Check for prompt injection in web-accessible files
    web_root = PROJECT_DIR
    prompt_injection_patterns = [
        r"ignore previous instructions",
        r"you are now",
        r"disregard all",
        r"new instructions:",
        r"system prompt:",
        r"<\|im_start\|>",
        r"\[INST\]",
    ]

    try:
        for html_file in web_root.rglob("*.html"):
            if any(skip in str(html_file) for skip in [".git", "node_modules", "transcriptions"]):
                continue
            try:
                content = html_file.read_text(errors="replace").lower()
                for pattern in prompt_injection_patterns:
                    if re.search(pattern, content):
                        issues.append(
                            f"Prompt injection pattern in {html_file.relative_to(web_root)}: "
                            f"matches '{pattern}'"
                        )
            except Exception:
                pass
    except Exception as e:
        log(f"Prompt injection scan error: {e}", "WARN")

    return issues


def check_new_users_and_sudoers():
    """Check for unauthorized user accounts or sudo access."""
    issues = []

    # Check for new users with login shells
    try:
        passwd = pathlib.Path("/etc/passwd")
        if passwd.exists():
            for line in passwd.read_text().split("\n"):
                if not line.strip():
                    continue
                parts = line.split(":")
                if len(parts) >= 7:
                    username = parts[0]
                    uid = int(parts[2]) if parts[2].isdigit() else 0
                    shell = parts[6]
                    # Flag unexpected users with login shells and UIDs >= 1000
                    if uid >= 1000 and shell not in ("/usr/sbin/nologin", "/bin/false", ""):
                        if username not in ("stv", "nobody", "ubuntu"):
                            issues.append(
                                f"Unexpected user with login shell: {username} "
                                f"(uid={uid}, shell={shell})"
                            )
    except Exception:
        pass

    # Check sudoers for unexpected entries
    sudoers_d = pathlib.Path("/etc/sudoers.d")
    if sudoers_d.exists():
        try:
            for f in sudoers_d.iterdir():
                if f.name not in ("README", "stv", "cloud-init", "90-cloud-init-users"):
                    issues.append(f"Unexpected sudoers file: /etc/sudoers.d/{f.name}")
        except PermissionError:
            pass

    return issues


def check_listening_services():
    """Enhanced port check — detect new services since last scan."""
    issues = []
    expected_ports = {"22", "53", "80", "443", "8080"}

    try:
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True, text=True, timeout=10,
        )
        current_listeners = set()
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 4:
                addr = parts[3]
                port = addr.rsplit(":", 1)[-1] if ":" in addr else ""
                if "127.0.0.1" in addr or "::1" in addr:
                    continue
                if port:
                    current_listeners.add(port)
                    if port not in expected_ports:
                        issues.append(f"Unexpected listener on port {port}: {line.strip()}")
    except FileNotFoundError:
        pass  # macOS
    except Exception as e:
        log(f"Listener check error: {e}", "WARN")

    return issues


# ─── Main ──────────────────────────────────────────────────────────────────


def run_full_scan():
    """Run all threat intelligence checks."""
    log("=" * 60)
    log("Starting daily threat intelligence scan...")
    all_issues = []

    checks = [
        ("CVE Advisories", check_cve_advisories),
        ("Web Server Attack Patterns", check_web_server_attack_patterns),
        ("SSH Key Tampering", check_ssh_key_tampering),
        ("Package Integrity", check_package_integrity),
        ("SSL Certificate", check_ssl_certificate),
        ("DNS Integrity", check_dns_integrity),
        ("AI Agent Threats", check_ai_agent_threats),
        ("User Accounts", check_new_users_and_sudoers),
        ("Listening Services", check_listening_services),
    ]

    for name, check_fn in checks:
        try:
            issues = check_fn()
            if issues:
                log(f"  [{name}] {len(issues)} finding(s)", "WARN")
                for issue in issues:
                    log(f"    ⚠ {issue}", "WARN")
                all_issues.extend(issues)
            else:
                log(f"  [{name}] Clean")
        except Exception as e:
            log(f"  [{name}] Check failed: {e}", "ERROR")

    # Update scan metadata
    threat_data = load_threat_data()
    threat_data["last_scan"] = datetime.now().isoformat()
    threat_data["scan_count"] = threat_data.get("scan_count", 0) + 1
    save_threat_data(threat_data)
    record_tool_run("threat_scanner")

    # Alert on any findings
    if all_issues:
        send_alert(
            f"Daily threat scan: {len(all_issues)} finding(s)",
            "\n".join(f"• {i}" for i in all_issues),
        )
        log(f"\nTotal: {len(all_issues)} finding(s) — alert sent")
    else:
        log("\nDaily threat scan complete — all clear")

    return all_issues


def run_quick_scan():
    """Quick scan — most critical checks only."""
    log("Quick threat scan...")
    issues = []
    issues.extend(check_ssh_key_tampering())
    issues.extend(check_listening_services())
    issues.extend(check_ai_agent_threats())

    if issues:
        log(f"Quick scan: {len(issues)} finding(s)")
        for i in issues:
            log(f"  ⚠ {i}", "WARN")
        if len(issues) >= 2:
            send_alert(f"Quick threat scan: {len(issues)} findings", "\n".join(f"• {i}" for i in issues))

    return issues


def run_cve_check():
    """CVE advisory check only."""
    log("CVE advisory check...")
    issues = check_cve_advisories()
    if issues:
        log(f"CVE check: {len(issues)} advisory(ies)")
        for i in issues:
            log(f"  ⚠ {i}", "WARN")
        send_alert("New CVE advisories", "\n".join(f"• {i}" for i in issues))
    else:
        log("No new CVE advisories affecting our stack")
    return issues


def main():
    parser = argparse.ArgumentParser(description="STV Threat Scanner")
    parser.add_argument("--quick", action="store_true", help="Quick scan only")
    parser.add_argument("--check-cves", action="store_true", help="CVE check only")
    args = parser.parse_args()

    print(f"STV Threat Scanner — {datetime.now().isoformat()}\n")

    if args.quick:
        run_quick_scan()
    elif args.check_cves:
        run_cve_check()
    else:
        run_full_scan()

    print("\nDone.")


if __name__ == "__main__":
    main()
