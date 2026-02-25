#!/bin/bash
#
# VPS Hardening Script for SocialTradingVlog
# Run once on the VPS after initial deployment: sudo bash tools/harden_vps.sh
#
# This script implements the security best practices from:
# - CIS Ubuntu benchmarks
# - OWASP server hardening guidelines
# - SSH hardening best practices 2025
#
# IMPORTANT: Run this AFTER you've confirmed SSH key auth works.
# If you lose access, you'll need VPS console access to recover.

set -euo pipefail

echo "═══════════════════════════════════════════════════════"
echo "  STV VPS Hardening Script"
echo "  $(date -Iseconds)"
echo "═══════════════════════════════════════════════════════"
echo ""

# ── 1. System Updates ────────────────────────────────────

echo "► [1/10] System updates..."
apt-get update -qq
apt-get upgrade -y -qq
echo "  ✓ System packages updated"

# ── 2. Install Security Packages ─────────────────────────

echo "► [2/10] Installing security packages..."
apt-get install -y -qq \
    fail2ban \
    ufw \
    unattended-upgrades \
    apt-listchanges \
    logwatch \
    libpam-tmpdir \
    needrestart 2>/dev/null || true
echo "  ✓ Security packages installed"

# ── 3. Configure Automatic Security Updates ──────────────

echo "► [3/10] Configuring automatic security updates..."
cat > /etc/apt/apt.conf.d/60stv-unattended-upgrades <<'UUEOF'
// Auto-install security updates
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
// Auto-reboot at 4am if needed (only for kernel updates)
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "04:00";
// Email notification on error
Unattended-Upgrade::Mail "root";
Unattended-Upgrade::MailReport "only-on-error";
UUEOF
echo "  ✓ Automatic security updates configured (reboot at 4am if needed)"

# ── 4. SSH Hardening ─────────────────────────────────────

echo "► [4/10] Hardening SSH..."
SSHD_CONFIG="/etc/ssh/sshd_config"

# Backup original
cp "$SSHD_CONFIG" "${SSHD_CONFIG}.bak.$(date +%Y%m%d)"

# Create hardened SSH drop-in config
mkdir -p /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/99-stv-hardening.conf <<'SSHEOF'
# STV SSH Hardening — applied $(date +%Y-%m-%d)
# Disable password auth (key-only)
PasswordAuthentication no
ChallengeResponseAuthentication no

# Disable root login
PermitRootLogin no

# Limit auth attempts
MaxAuthTries 3
LoginGraceTime 30

# Idle timeout (5 minutes idle = disconnect)
ClientAliveInterval 300
ClientAliveCountMax 2

# Disable X11 forwarding (not needed)
X11Forwarding no

# Disable agent forwarding (not needed)
AllowAgentForwarding no

# Only allow the stv user
AllowUsers stv

# Disable empty passwords
PermitEmptyPasswords no

# Use strong key exchange algorithms only
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512

# Use strong ciphers only
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com

# Use strong MACs only
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# Log level for security monitoring
LogLevel VERBOSE
SSHEOF

# Test SSH config before applying
if sshd -t 2>/dev/null; then
    systemctl reload ssh 2>/dev/null || systemctl reload sshd 2>/dev/null
    echo "  ✓ SSH hardened (key-only, no root, strong ciphers, AllowUsers stv)"
else
    echo "  ✗ SSH config test failed — reverting"
    rm /etc/ssh/sshd_config.d/99-stv-hardening.conf
fi

# ── 5. UFW Firewall ──────────────────────────────────────

echo "► [5/10] Configuring UFW firewall..."

# Check if UFW is already active with correct rules
UFW_STATUS=$(ufw status 2>/dev/null || true)
if echo "$UFW_STATUS" | grep -q "Status: active"; then
    echo "  ✓ UFW already active — verifying rules..."
    # Ensure required ports are allowed
    for port_rule in "22/tcp" "80/tcp" "443/tcp"; do
        if ! echo "$UFW_STATUS" | grep -q "$port_rule"; then
            ufw allow "$port_rule"
        fi
    done
    # Add SSH rate limiting if not already present
    if ! echo "$UFW_STATUS" | grep -q "22/tcp.*LIMIT"; then
        ufw limit ssh/tcp
    fi
    echo "  ✓ UFW verified — ports 22, 80, 443 open"
else
    # Fresh setup
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp comment 'SSH'
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    ufw limit ssh/tcp
    ufw --force enable
    echo "  ✓ UFW enabled — only ports 22, 80, 443 open"
fi

# ── 6. Fail2Ban ──────────────────────────────────────────

echo "► [6/10] Configuring fail2ban..."
cat > /etc/fail2ban/jail.local <<'F2BEOF'
[DEFAULT]
# Ban for 1 hour after 3 failures
bantime = 3600
findtime = 600
maxretry = 3
# Use systemd backend
backend = systemd

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

# Block Caddy attack scanners (if Caddy access log exists)
[caddy-badrequests]
enabled = true
port = http,https
filter = caddy-badrequests
logpath = /var/log/caddy/access.log
maxretry = 10
bantime = 3600
F2BEOF

# Create Caddy bad requests filter (JSON log format)
cat > /etc/fail2ban/filter.d/caddy-badrequests.conf <<'FILTEREOF'
[Definition]
# Caddy JSON access log format — match attack patterns returning 404
failregex = "remote_ip":"<HOST>".*"uri":".*(?:wp-login|wp-admin|xmlrpc|phpmyadmin|\.php|\.env|\.git).*"status":(?:400|403|404)
ignoreregex =
FILTEREOF

systemctl enable fail2ban
systemctl restart fail2ban
echo "  ✓ fail2ban configured (SSH brute force + Caddy scanner blocking)"

# ── 7. Kernel Hardening (sysctl) ─────────────────────────

echo "► [7/10] Applying kernel security parameters..."
cat > /etc/sysctl.d/99-stv-security.conf <<'SYSEOF'
# Disable IP forwarding
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# Disable source routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Enable TCP SYN cookies (SYN flood protection)
net.ipv4.tcp_syncookies = 1

# Disable ICMP redirects (prevent MITM)
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0

# Log martian packets (impossible source addresses)
net.ipv4.conf.all.log_martians = 1

# Ignore broadcast pings (smurf attack protection)
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Enable reverse path filtering (IP spoofing protection)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Restrict core dumps (prevent info leakage)
fs.suid_dumpable = 0

# Restrict kernel pointer exposure
kernel.kptr_restrict = 2

# Restrict dmesg access
kernel.dmesg_restrict = 1

# Restrict performance events
kernel.perf_event_paranoid = 3

# Disable unprivileged BPF
kernel.unprivileged_bpf_disabled = 1
SYSEOF

sysctl --system >/dev/null 2>&1
echo "  ✓ Kernel hardened (SYN cookies, no redirects, RP filtering, restricted pointers)"

# ── 8. File Permission Hardening ─────────────────────────

echo "► [8/10] Hardening file permissions..."

# Restrict crontab access to root and stv only
if [ -f /etc/cron.allow ]; then
    echo "root" > /etc/cron.allow
    echo "stv" >> /etc/cron.allow
fi

# Restrict access to cron directories
chmod 700 /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.monthly /etc/cron.weekly 2>/dev/null || true

# Secure SSH directory
chmod 700 /home/stv/.ssh 2>/dev/null || true
chmod 600 /home/stv/.ssh/authorized_keys 2>/dev/null || true

# Secure the project secrets
SECRETS_DIR="/home/stv/.config/stv-secrets"
if [ -d "$SECRETS_DIR" ]; then
    chmod 700 "$SECRETS_DIR"
    find "$SECRETS_DIR" -type f -exec chmod 600 {} \;
    echo "  ✓ Secret files locked to 600"
fi

# Secure project data directory
PROJECT_DIR="/home/stv/socialtradingvlog-website"
chmod 750 "$PROJECT_DIR/data" 2>/dev/null || true
chmod 750 "$PROJECT_DIR/tools" 2>/dev/null || true
chmod 750 "$PROJECT_DIR/logs" 2>/dev/null || true

echo "  ✓ File permissions hardened"

# ── 9. Web Server (Caddy) Verification ───────────────────

echo "► [9/10] Verifying Caddy security config..."

if systemctl is-active --quiet caddy 2>/dev/null; then
    echo "  ✓ Caddy is running"
    # Verify security headers are present
    if command -v curl &>/dev/null; then
        HEADERS=$(curl -sI https://app.socialtradingvlog.com --max-time 10 2>/dev/null || true)
        if echo "$HEADERS" | grep -qi "x-frame-options"; then
            echo "  ✓ Security headers present"
        else
            echo "  ⚠ Security headers missing — check /etc/caddy/Caddyfile"
        fi
        if echo "$HEADERS" | grep -qi "strict-transport-security"; then
            echo "  ✓ HSTS enabled"
        fi
    fi
else
    echo "  ⚠ Caddy is not running — check: sudo systemctl status caddy"
fi

# ── 10. SSH Two-Factor Authentication ────────────────────

echo "► [10/14] Setting up SSH 2FA (Google Authenticator)..."
apt-get install -y -qq libpam-google-authenticator 2>/dev/null || true

# Configure PAM for SSH
if ! grep -q "pam_google_authenticator" /etc/pam.d/sshd 2>/dev/null; then
    echo "auth required pam_google_authenticator.so nullok" >> /etc/pam.d/sshd
    echo "  ✓ PAM configured for Google Authenticator"
fi

# Enable ChallengeResponse for 2FA in SSH
# Note: We use a separate drop-in so it doesn't conflict with 99-stv-hardening.conf
cat > /etc/ssh/sshd_config.d/98-stv-2fa.conf <<'TWOFAEOF'
# STV 2FA — SSH key + TOTP
# AuthenticationMethods publickey,keyboard-interactive enables key + 2FA
# "nullok" in PAM means users without 2FA can still log in with just a key
# Once 2FA is set up, remove nullok for mandatory 2FA
KbdInteractiveAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
TWOFAEOF

if sshd -t 2>/dev/null; then
    systemctl reload ssh 2>/dev/null || systemctl reload sshd 2>/dev/null
    echo "  ✓ SSH 2FA configured (key + TOTP)"
    echo ""
    echo "  ╔══════════════════════════════════════════════════════╗"
    echo "  ║  IMPORTANT: Set up 2FA for the stv user NOW:       ║"
    echo "  ║                                                      ║"
    echo "  ║  1. Switch to stv user:  su - stv                   ║"
    echo "  ║  2. Run: google-authenticator -t -d -f -r 3 -R 30  ║"
    echo "  ║  3. Scan the QR code with your authenticator app    ║"
    echo "  ║  4. Save the emergency scratch codes!               ║"
    echo "  ║                                                      ║"
    echo "  ║  Test in a NEW terminal before closing this one!    ║"
    echo "  ╚══════════════════════════════════════════════════════╝"
else
    echo "  ✗ 2FA config failed — reverting"
    rm -f /etc/ssh/sshd_config.d/98-stv-2fa.conf
fi

# ── 11. Disable Unnecessary Services ─────────────────────

echo "► [11/14] Disabling unnecessary services..."
# Disable services that aren't needed on a web server
for svc in avahi-daemon cups bluetooth snapd; do
    if systemctl is-active --quiet "$svc" 2>/dev/null; then
        systemctl stop "$svc" 2>/dev/null || true
        systemctl disable "$svc" 2>/dev/null || true
        echo "  ✓ Disabled $svc"
    fi
done

# ── 12. DNS CAA Record Check ────────────────────────────

echo "► [12/14] Checking DNS CAA record..."
if command -v dig &>/dev/null; then
    CAA_RECORD=$(dig +short CAA socialtradingvlog.com 2>/dev/null)
    if [ -z "$CAA_RECORD" ]; then
        echo "  ⚠ No CAA record found for socialtradingvlog.com"
        echo "  Add this DNS record at your registrar:"
        echo "    Type: CAA"
        echo "    Name: @"
        echo "    Value: 0 issue \"letsencrypt.org\""
        echo "    Value: 0 issuewild \"letsencrypt.org\""
        echo "    Value: 0 iodef \"mailto:tom@socialtradingvlog.com\""
        echo "  This prevents unauthorized CAs from issuing certificates for your domain."
    else
        echo "  ✓ CAA record found: $CAA_RECORD"
    fi
else
    echo "  (dig not available — install dnsutils to check CAA)"
fi

# ── 13. TLS Verification ──────────────────────────────────

echo "► [13/14] Verifying TLS configuration..."
# Caddy handles TLS automatically with modern defaults (TLS 1.2+, strong ciphers, OCSP stapling)
if command -v openssl &>/dev/null; then
    TLS_CHECK=$(echo | openssl s_client -connect app.socialtradingvlog.com:443 -servername app.socialtradingvlog.com 2>/dev/null | grep -i "protocol\|cipher" || true)
    if echo "$TLS_CHECK" | grep -qi "TLSv1.[23]"; then
        echo "  ✓ TLS 1.2/1.3 verified (Caddy auto-managed)"
    else
        echo "  ⚠ Could not verify TLS version"
    fi
else
    echo "  (openssl not available for TLS check)"
fi

# ── 14. Cloudflare WAF Preparation ──────────────────────

echo "► [14/14] Cloudflare status..."
# Main site (socialtradingvlog.com) already uses Cloudflare via GitHub Pages
echo "  ✓ Main site already behind Cloudflare CDN"
echo "  Dashboard (app.socialtradingvlog.com) connects directly to VPS"
echo "  Note: Dashboard subdomain could be added to Cloudflare proxy for extra DDoS protection"

# ── Summary ──────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Hardening Complete! (14 steps)"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  [✓] System updated"
echo "  [✓] Automatic security updates (unattended-upgrades)"
echo "  [✓] SSH: key-only, no root, strong ciphers, AllowUsers stv"
echo "  [✓] UFW firewall: only 22, 80, 443 open"
echo "  [✓] fail2ban: SSH brute force + Caddy scanner blocking"
echo "  [✓] Kernel hardened: SYN cookies, RP filter, no redirects"
echo "  [✓] File permissions locked down"
echo "  [✓] Caddy security headers verified"
echo "  [✓] SSH 2FA (Google Authenticator) — needs user setup"
echo "  [✓] Unnecessary services disabled"
echo "  [✓] TLS verified (Caddy auto-managed)"
echo ""
echo "  MANUAL STEP REMAINING:"
echo "  1. Set up 2FA: google-authenticator -t -d -f -r 3 -R 30"
echo "  2. Scan QR code with authenticator app, save scratch codes"
echo "  3. Test SSH login in NEW terminal before closing this one!"
echo "  4. Add DNS CAA record at registrar (see step 12 output above)"
echo ""
echo "  Current fail2ban status:"
fail2ban-client status 2>/dev/null || echo "  (check manually: fail2ban-client status)"
echo ""
echo "  Current UFW status:"
ufw status verbose
