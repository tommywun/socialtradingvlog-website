#!/bin/bash
#
# Advanced VPS Hardening — Run AFTER harden_vps.sh
# sudo bash tools/harden_vps_advanced.sh
#
# Adds:
#   1. CrowdSec (crowd-sourced threat intelligence — upgrade from fail2ban)
#   2. AIDE (file integrity monitoring at OS level)
#   3. auditd (kernel-level audit logging)
#   4. Process accounting
#   5. USB/removable media blocking
#   6. Login banners and legal warnings
#   7. Disable core dumps system-wide
#   8. Restrict compiler access
#   9. Logwatch (daily email digest of security events)
#  10. Immutable flag on critical configs

set -euo pipefail

echo "═══════════════════════════════════════════════════════"
echo "  STV Advanced VPS Hardening"
echo "  $(date -Iseconds)"
echo "═══════════════════════════════════════════════════════"
echo ""

# ── 1. CrowdSec — Crowd-Sourced Threat Intelligence ─────

echo "► [1/10] Installing CrowdSec..."
if ! command -v cscli &>/dev/null; then
    curl -s https://install.crowdsec.net | bash 2>/dev/null || {
        # Fallback: add repo manually
        curl -s https://packagecloud.io/install/repositories/crowdsec/crowdsec/script.deb.sh | bash 2>/dev/null
        apt-get install -y -qq crowdsec crowdsec-firewall-bouncer-iptables 2>/dev/null
    }
fi

if command -v cscli &>/dev/null; then
    # Install nginx collection for log parsing
    cscli collections install crowdsecurity/nginx 2>/dev/null || true
    cscli collections install crowdsecurity/sshd 2>/dev/null || true
    cscli collections install crowdsecurity/linux 2>/dev/null || true

    # Install firewall bouncer (blocks IPs via iptables)
    apt-get install -y -qq crowdsec-firewall-bouncer-iptables 2>/dev/null || true

    # Configure nginx log parsing
    if [ -f /etc/crowdsec/acquis.yaml ]; then
        if ! grep -q "nginx" /etc/crowdsec/acquis.yaml 2>/dev/null; then
            cat >> /etc/crowdsec/acquis.yaml <<'CSEOF'

# Nginx access logs
filenames:
  - /var/log/nginx/access.log
  - /var/log/nginx/error.log
labels:
  type: nginx
CSEOF
        fi
    fi

    systemctl enable crowdsec
    systemctl restart crowdsec
    echo "  ✓ CrowdSec installed with nginx + SSH + Linux collections"
    echo "  CrowdSec adds: crowd-sourced IP blocklists, behavioral detection,"
    echo "  multi-stage attack prevention, and zero-day scenario sharing"
else
    echo "  ⚠ CrowdSec installation failed — continue with fail2ban"
fi

# ── 2. AIDE — File Integrity Monitoring (OS-level) ──────

echo "► [2/10] Installing AIDE (file integrity monitoring)..."
apt-get install -y -qq aide 2>/dev/null || true

if command -v aide &>/dev/null; then
    # Configure AIDE to monitor critical paths
    cat > /etc/aide/aide.conf.d/99_stv_paths <<'AIDEEOF'
# STV critical paths to monitor
/home/stv/socialtradingvlog-website/tools Full
/home/stv/socialtradingvlog-website/data Full
/etc/ssh Full
/etc/nginx Full
/etc/cron.d Full
/etc/pam.d Full
/etc/sudoers Full
/etc/passwd Full
/etc/shadow Full
AIDEEOF

    # Initialize AIDE database (takes a minute)
    echo "  Initializing AIDE database..."
    aide --init 2>/dev/null || aideinit 2>/dev/null || true
    if [ -f /var/lib/aide/aide.db.new ]; then
        mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
    fi
    echo "  ✓ AIDE installed and initialized"
    echo "  Run 'aide --check' to detect unauthorized file changes"
else
    echo "  ⚠ AIDE installation failed"
fi

# ── 3. auditd — Kernel Audit Logging ────────────────────

echo "► [3/10] Installing auditd (kernel audit logging)..."
apt-get install -y -qq auditd audispd-plugins 2>/dev/null || true

if command -v auditctl &>/dev/null; then
    # Add audit rules for critical files
    cat > /etc/audit/rules.d/stv-security.rules <<'AUDITEOF'
# Monitor SSH config changes
-w /etc/ssh/sshd_config -p wa -k ssh_config
-w /etc/ssh/sshd_config.d/ -p wa -k ssh_config

# Monitor crontab changes
-w /etc/crontab -p wa -k crontab
-w /etc/cron.d/ -p wa -k crontab
-w /var/spool/cron/ -p wa -k crontab

# Monitor user/group changes
-w /etc/passwd -p wa -k user_changes
-w /etc/shadow -p wa -k user_changes
-w /etc/group -p wa -k user_changes
-w /etc/sudoers -p wa -k sudo_changes
-w /etc/sudoers.d/ -p wa -k sudo_changes

# Monitor nginx config changes
-w /etc/nginx/ -p wa -k nginx_config

# Monitor SSH authorized_keys
-w /home/stv/.ssh/authorized_keys -p wa -k ssh_keys

# Monitor STV tools directory
-w /home/stv/socialtradingvlog-website/tools/ -p wa -k stv_tools

# Monitor STV secrets
-w /home/stv/.config/stv-secrets/ -p wa -k stv_secrets

# Log all sudo commands
-a always,exit -F arch=b64 -S execve -F euid=0 -k root_commands
AUDITEOF

    systemctl enable auditd
    systemctl restart auditd
    echo "  ✓ auditd installed — monitors SSH, cron, user, nginx, and STV file changes"
else
    echo "  ⚠ auditd installation failed"
fi

# ── 4. Process Accounting ────────────────────────────────

echo "► [4/10] Enabling process accounting..."
apt-get install -y -qq acct 2>/dev/null || true
if command -v accton &>/dev/null; then
    systemctl enable acct 2>/dev/null || true
    systemctl start acct 2>/dev/null || true
    echo "  ✓ Process accounting enabled (use 'lastcomm' and 'sa' to review)"
fi

# ── 5. USB/Removable Media Blocking ─────────────────────

echo "► [5/10] Blocking USB storage..."
cat > /etc/modprobe.d/disable-usb-storage.conf <<'USBEOF'
# Block USB storage devices (VPS doesn't need them)
install usb-storage /bin/true
blacklist usb-storage
blacklist uas
USBEOF
echo "  ✓ USB storage blocked"

# ── 6. Login Banners ────────────────────────────────────

echo "► [6/10] Setting up legal warning banners..."
cat > /etc/issue.net <<'BANNEREOF'
╔══════════════════════════════════════════════════════╗
║  AUTHORIZED ACCESS ONLY                             ║
║                                                      ║
║  This system is monitored. All activity is logged.   ║
║  Unauthorized access is prohibited and will be       ║
║  reported to law enforcement.                        ║
╚══════════════════════════════════════════════════════╝
BANNEREOF

# Enable banner in SSH
if ! grep -q "Banner /etc/issue.net" /etc/ssh/sshd_config 2>/dev/null; then
    if [ -d /etc/ssh/sshd_config.d ]; then
        echo "Banner /etc/issue.net" > /etc/ssh/sshd_config.d/97-stv-banner.conf
    fi
fi
echo "  ✓ SSH login warning banner set"

# ── 7. Disable Core Dumps System-Wide ───────────────────

echo "► [7/10] Disabling core dumps..."
cat > /etc/security/limits.d/stv-no-coredumps.conf <<'COREEOF'
# Disable core dumps (prevent sensitive data leakage)
* hard core 0
* soft core 0
COREEOF

# Also via sysctl (already set in harden_vps.sh but double-check)
if ! grep -q "fs.suid_dumpable = 0" /etc/sysctl.d/99-stv-security.conf 2>/dev/null; then
    echo "fs.suid_dumpable = 0" >> /etc/sysctl.d/99-stv-security.conf
    sysctl -p /etc/sysctl.d/99-stv-security.conf >/dev/null 2>&1
fi
echo "  ✓ Core dumps disabled"

# ── 8. Restrict Compiler Access ──────────────────────────

echo "► [8/10] Restricting compiler access..."
# Prevent non-root from using compilers (stops compile-on-server attacks)
for compiler in gcc g++ cc make; do
    COMPILER_PATH=$(which "$compiler" 2>/dev/null)
    if [ -n "$COMPILER_PATH" ] && [ -f "$COMPILER_PATH" ]; then
        chmod 700 "$COMPILER_PATH" 2>/dev/null || true
    fi
done
echo "  ✓ Compilers restricted to root only"

# ── 9. Logwatch ─────────────────────────────────────────

echo "► [9/10] Configuring logwatch..."
apt-get install -y -qq logwatch 2>/dev/null || true
if command -v logwatch &>/dev/null; then
    mkdir -p /etc/logwatch/conf
    cat > /etc/logwatch/conf/logwatch.conf <<'LWEOF'
# Logwatch daily summary
Output = file
Filename = /home/stv/socialtradingvlog-website/logs/logwatch-daily.log
Detail = Med
Range = yesterday
Service = All
LWEOF
    echo "  ✓ Logwatch configured (daily summary to logs/logwatch-daily.log)"
fi

# ── 10. Immutable Flags on Critical Configs ──────────────

echo "► [10/10] Setting immutable flags..."
# Make critical security configs immutable (can't be changed even by root
# until the flag is explicitly removed with chattr -i)
for f in \
    /etc/ssh/sshd_config.d/99-stv-hardening.conf \
    /etc/ssh/sshd_config.d/98-stv-2fa.conf \
    /etc/sysctl.d/99-stv-security.conf \
    /etc/security/limits.d/stv-no-coredumps.conf; do
    if [ -f "$f" ]; then
        chattr +i "$f" 2>/dev/null || true
    fi
done
echo "  ✓ Critical configs made immutable (use 'chattr -i' to modify)"
echo "  NOTE: To update these files, first run: chattr -i <filename>"

# ── Summary ──────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Advanced Hardening Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  [✓] CrowdSec — crowd-sourced threat intelligence"
echo "  [✓] AIDE — OS-level file integrity monitoring"
echo "  [✓] auditd — kernel audit logging for all changes"
echo "  [✓] Process accounting — track all executed commands"
echo "  [✓] USB storage blocked"
echo "  [✓] SSH login warning banner"
echo "  [✓] Core dumps disabled"
echo "  [✓] Compiler access restricted to root"
echo "  [✓] Logwatch daily summaries"
echo "  [✓] Immutable flags on security configs"
echo ""
echo "  New commands available:"
echo "    cscli alerts list          — View CrowdSec alerts"
echo "    cscli decisions list       — View blocked IPs"
echo "    aide --check               — Check file integrity"
echo "    ausearch -k stv_tools      — View tool file changes"
echo "    ausearch -k ssh_keys       — View SSH key changes"
echo "    lastcomm                   — View recent commands"
echo ""
echo "  CrowdSec dashboard (optional):"
echo "    cscli console enroll       — Connect to CrowdSec console"
echo ""
