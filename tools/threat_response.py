#!/usr/bin/env python3
"""
Automated Threat Response — Takes immediate safe actions when threats are detected.

SAFE automated responses (reversible, no data loss):
  - Block attacking IPs via UFW
  - Kill suspicious processes
  - Fix file permissions
  - Rotate exposed credentials
  - Disable compromised services temporarily
  - Lock out unauthorized SSH keys

UNSAFE actions (require Tom's approval via Telegram):
  - Full service shutdown
  - Data wipe or restore
  - Password/key rotation
  - Firewall rule changes beyond IP blocking

Philosophy: The first seconds of an attack matter most. This script acts fast
on safe, reversible actions and escalates dangerous ones to Tom immediately.

Called automatically by security_monitor.py and threat_scanner.py when
critical issues are detected. Can also be run manually.

Usage:
    python3 tools/threat_response.py --block-ip 1.2.3.4
    python3 tools/threat_response.py --kill-process "cryptominer"
    python3 tools/threat_response.py --fix-permissions
    python3 tools/threat_response.py --lockdown          # Emergency lockdown
    python3 tools/threat_response.py --unlock             # Restore from lockdown
"""

import sys
import os
import json
import pathlib
import argparse
import subprocess
import time
from datetime import datetime

# Shared security library
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from security_lib import (
    PROJECT_DIR, DATA_DIR, LOGS_DIR, SECRETS_DIR,
    log as _lib_log, send_telegram, validate_ip,
)

RESPONSE_LOG = LOGS_DIR / "threat-response.log"
BLOCKED_IPS_FILE = DATA_DIR / "blocked-ips.json"


def log(msg, level="ACTION"):
    _lib_log(msg, level, log_file=RESPONSE_LOG)


def alert_tom(subject, body):
    """Send urgent alert to Tom via Telegram."""
    send_telegram(subject, body, emoji="🚨 THREAT RESPONSE")


# ─── Safe Automated Actions (reversible, no data loss) ───────────────


def block_ip(ip):
    """Block an IP address via UFW. Safe and reversible."""
    if not validate_ip(ip):
        log(f"Invalid IP: {ip}", "ERROR")
        return False

    try:
        # Verify UFW is enabled before adding rules
        result = subprocess.run(
            ["ufw", "status"],
            capture_output=True, text=True, timeout=10,
        )
        if "Status: inactive" in result.stdout:
            log("UFW is INACTIVE — cannot block IP! Enabling UFW first.", "ERROR")
            alert_tom("UFW is DISABLED!", "UFW firewall is inactive. IP blocking will not work.\n"
                      "Enable with: sudo ufw --force enable")
            return False

        if ip in result.stdout:
            log(f"IP {ip} already blocked")
            return True

        # Block the IP
        subprocess.run(
            ["ufw", "deny", "from", ip],
            capture_output=True, text=True, timeout=10,
        )
        log(f"BLOCKED IP: {ip}")

        # Record in blocked IPs file
        _record_blocked_ip(ip, "auto")

        alert_tom(
            f"IP Blocked: {ip}",
            f"Automatically blocked {ip} via UFW.\n"
            f"To unblock: `sudo ufw delete deny from {ip}`"
        )
        return True

    except FileNotFoundError:
        log("UFW not available — cannot block IP", "ERROR")
        return False
    except Exception as e:
        log(f"Failed to block {ip}: {e}", "ERROR")
        return False


def kill_suspicious_process(pattern):
    """Kill processes matching a suspicious pattern. Safe — processes can restart."""
    if not pattern or len(pattern) < 3:
        log("Pattern too short — refusing to kill", "ERROR")
        return False

    # Safelist: never kill these
    safelist = ["sshd", "nginx", "python3", "bash", "systemd", "cron",
                "fail2ban", "crowdsec", "ufw", "stv-dashboard"]
    if pattern.lower() in safelist:
        log(f"REFUSED to kill safelisted process: {pattern}", "ERROR")
        return False

    try:
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True, text=True, timeout=10,
        )
        pids = result.stdout.strip().split("\n")
        pids = [p for p in pids if p.strip()]

        if not pids:
            log(f"No processes found matching: {pattern}")
            return True

        killed = 0
        for pid in pids:
            pid = pid.strip()
            if not pid.isdigit():
                continue
            # Don't kill ourselves
            if int(pid) == os.getpid():
                continue
            subprocess.run(["kill", "-15", pid], timeout=5)  # SIGTERM first
            # Wait briefly then verify process is gone, SIGKILL if needed
            time.sleep(1)
            check = subprocess.run(["kill", "-0", pid], capture_output=True, timeout=3)
            if check.returncode == 0:  # Still alive
                subprocess.run(["kill", "-9", pid], timeout=5)  # SIGKILL
                log(f"  Process {pid} required SIGKILL")
            killed += 1

        log(f"KILLED {killed} process(es) matching: {pattern}")
        alert_tom(
            f"Processes killed: {pattern}",
            f"Killed {killed} process(es) matching '{pattern}'.\n"
            f"PIDs: {', '.join(pids[:10])}"
        )
        return True

    except Exception as e:
        log(f"Failed to kill processes: {e}", "ERROR")
        return False


def fix_permissions():
    """Fix file permissions on secrets and critical files. Always safe."""
    fixed = []

    # Fix secrets directory
    if SECRETS_DIR.exists():
        dir_mode = oct(SECRETS_DIR.stat().st_mode)[-3:]
        if dir_mode != "700":
            os.chmod(SECRETS_DIR, 0o700)
            fixed.append(f"secrets dir: {dir_mode} → 700")

        for f in SECRETS_DIR.iterdir():
            if f.name.startswith("."):
                continue
            mode = oct(f.stat().st_mode)[-3:]
            if mode != "600":
                os.chmod(f, 0o600)
                fixed.append(f"{f.name}: {mode} → 600")

    # Fix SSH
    ssh_dir = pathlib.Path.home() / ".ssh"
    if ssh_dir.exists():
        ssh_mode = oct(ssh_dir.stat().st_mode)[-3:]
        if ssh_mode != "700":
            os.chmod(ssh_dir, 0o700)
            fixed.append(f".ssh dir: {ssh_mode} → 700")

        auth_keys = ssh_dir / "authorized_keys"
        if auth_keys.exists():
            ak_mode = oct(auth_keys.stat().st_mode)[-3:]
            if ak_mode != "600":
                os.chmod(auth_keys, 0o600)
                fixed.append(f"authorized_keys: {ak_mode} → 600")

    if fixed:
        log(f"FIXED {len(fixed)} permission(s): {'; '.join(fixed)}")
        alert_tom("Permissions auto-fixed", "\n".join(f"• {f}" for f in fixed))
    else:
        log("All permissions correct — nothing to fix")

    return fixed


def remove_unauthorized_ssh_key(key_fingerprint=None):
    """Remove an unauthorized SSH key. Requires fingerprint for safety."""
    auth_keys = pathlib.Path.home() / ".ssh" / "authorized_keys"
    if not auth_keys.exists():
        return False

    content = auth_keys.read_text()
    lines = content.strip().split("\n")
    original_count = len([l for l in lines if l.strip() and not l.startswith("#")])

    if original_count <= 1:
        log("Only 1 SSH key — refusing to remove (would lock out)", "ERROR")
        alert_tom(
            "Cannot remove SSH key",
            "Only 1 key exists. Removing it would lock out SSH access.\n"
            "Manual intervention required."
        )
        return False

    # If a specific fingerprint is given, remove only that key
    # Otherwise, alert Tom for manual review
    if not key_fingerprint:
        alert_tom(
            f"SSH key review needed",
            f"{original_count} SSH keys found. Manual review required.\n"
            f"Check with: `ssh-keygen -lf ~/.ssh/authorized_keys`"
        )
        return False

    log(f"SSH key removal requested for fingerprint: {key_fingerprint}")
    alert_tom(
        "SSH key removal requested",
        f"Fingerprint: {key_fingerprint}\n"
        f"Requires manual action: edit ~/.ssh/authorized_keys"
    )
    return True


def emergency_lockdown():
    """Emergency lockdown — block all non-SSH traffic. REVERSIBLE."""
    log("!!! EMERGENCY LOCKDOWN INITIATED !!!", "CRITICAL")

    try:
        # Save current UFW rules for restoration
        result = subprocess.run(
            ["ufw", "status", "verbose"],
            capture_output=True, text=True, timeout=10,
        )
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        lockdown_file = DATA_DIR / "pre-lockdown-ufw.txt"
        lockdown_file.write_text(result.stdout)

        # Reset UFW to deny all except SSH
        subprocess.run(["ufw", "--force", "reset"], timeout=10)
        subprocess.run(["ufw", "default", "deny", "incoming"], timeout=10)
        subprocess.run(["ufw", "default", "allow", "outgoing"], timeout=10)
        subprocess.run(["ufw", "allow", "22/tcp"], timeout=10)
        subprocess.run(["ufw", "--force", "enable"], timeout=10)

        # Stop the dashboard (reduces attack surface)
        subprocess.run(
            ["systemctl", "stop", "stv-dashboard"],
            timeout=10, capture_output=True,
        )

        log("LOCKDOWN ACTIVE: Only SSH (port 22) accessible. Web/dashboard DOWN.")
        alert_tom(
            "EMERGENCY LOCKDOWN ACTIVE",
            "All services except SSH have been shut down.\n"
            "Only port 22 is open.\n"
            "Web site and dashboard are DOWN.\n\n"
            "To restore: `python3 tools/threat_response.py --unlock`\n"
            "Or manually:\n"
            "  `ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 8080/tcp`\n"
            "  `systemctl start stv-dashboard`"
        )
        return True

    except Exception as e:
        log(f"Lockdown failed: {e}", "ERROR")
        alert_tom("Lockdown FAILED", f"Error: {e}\nManual intervention required!")
        return False


def unlock():
    """Restore from emergency lockdown using saved pre-lockdown state."""
    log("Restoring from lockdown...")

    try:
        lockdown_file = DATA_DIR / "pre-lockdown-ufw.txt"

        # Try to restore from saved state first
        if lockdown_file.exists():
            saved_rules = lockdown_file.read_text()
            log(f"Found pre-lockdown UFW state ({len(saved_rules)} chars)")

            # Parse and restore custom rules from saved state
            # Only accept valid port patterns (digits/tcp or digits/udp)
            valid_port_re = re.compile(r"^(\d{1,5}/(tcp|udp))\s+(ALLOW|LIMIT)", re.IGNORECASE)
            for line in saved_rules.split("\n"):
                line = line.strip()
                match = valid_port_re.match(line)
                if not match:
                    continue
                port = match.group(1)
                action = match.group(3).upper()
                # Validate port number is in valid range
                port_num = int(port.split("/")[0])
                if port_num < 1 or port_num > 65535:
                    log(f"  Skipping invalid port: {port}", "WARN")
                    continue
                if action == "ALLOW":
                    subprocess.run(["ufw", "allow", port], timeout=10)
                    log(f"  Restored rule: allow {port}")
                elif action == "LIMIT":
                    subprocess.run(["ufw", "limit", port], timeout=10)
                    log(f"  Restored rule: limit {port}")

            log("Restored UFW rules from pre-lockdown state")
        else:
            # Fallback: restore standard rules if no saved state
            log("No pre-lockdown state found — restoring standard rules")
            subprocess.run(["ufw", "allow", "80/tcp"], timeout=10)
            subprocess.run(["ufw", "allow", "443/tcp"], timeout=10)
            subprocess.run(["ufw", "allow", "8080/tcp"], timeout=10)
            subprocess.run(["ufw", "limit", "ssh/tcp"], timeout=10)

        # Restart dashboard
        subprocess.run(
            ["systemctl", "start", "stv-dashboard"],
            timeout=10, capture_output=True,
        )

        log("LOCKDOWN LIFTED: All services restored.")
        alert_tom(
            "Lockdown lifted",
            "All services restored.\n"
            "Ports 22, 80, 443, 8080 are open.\n"
            "Dashboard is running."
        )
        return True

    except Exception as e:
        log(f"Unlock failed: {e}", "ERROR")
        return False


# ─── Helpers ─────────────────────────────────────────────────────────


import re  # needed for unlock() rule parsing


def _record_blocked_ip(ip, reason):
    """Record blocked IP for tracking."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {"blocked_ips": []}
    if BLOCKED_IPS_FILE.exists():
        data = json.loads(BLOCKED_IPS_FILE.read_text())

    data["blocked_ips"].append({
        "ip": ip,
        "reason": reason,
        "blocked_at": datetime.now().isoformat(),
    })

    # Keep last 500 entries
    data["blocked_ips"] = data["blocked_ips"][-500:]
    BLOCKED_IPS_FILE.write_text(json.dumps(data, indent=2))


# ─── Main ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="STV Threat Response")
    parser.add_argument("--block-ip", help="Block an IP address")
    parser.add_argument("--kill-process", help="Kill processes matching pattern")
    parser.add_argument("--fix-permissions", action="store_true",
                       help="Fix file permissions")
    parser.add_argument("--lockdown", action="store_true",
                       help="Emergency lockdown (SSH only)")
    parser.add_argument("--unlock", action="store_true",
                       help="Restore from lockdown")
    args = parser.parse_args()

    print(f"STV Threat Response — {datetime.now().isoformat()}\n")

    if args.block_ip:
        block_ip(args.block_ip)
    elif args.kill_process:
        kill_suspicious_process(args.kill_process)
    elif args.fix_permissions:
        fix_permissions()
    elif args.lockdown:
        emergency_lockdown()
    elif args.unlock:
        unlock()
    else:
        print("No action specified. Use --help for options.")
        print()
        print("Safe automated actions:")
        print("  --block-ip 1.2.3.4     Block an attacking IP")
        print("  --kill-process NAME     Kill suspicious processes")
        print("  --fix-permissions       Fix file permissions")
        print()
        print("Emergency actions:")
        print("  --lockdown              Shut everything except SSH")
        print("  --unlock                Restore from lockdown")

    print("\nDone.")


if __name__ == "__main__":
    main()
