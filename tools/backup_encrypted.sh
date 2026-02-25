#!/usr/bin/env bash
# Encrypted Backup — creates GPG-encrypted tar of critical data.
# Runs weekly via cron. Keeps last 4 backups (1 month).
#
# What's backed up:
#   - data/ (all JSON state files, review queue, sessions)
#   - ~/.config/stv-secrets/ (API keys, tokens)
#   - /etc/caddy/Caddyfile (web server config)
#   - /etc/ssh/sshd_config.d/ (SSH hardening)
#   - /etc/fail2ban/jail.local (fail2ban config)
#   - crontab (scheduled jobs)
#
# Encryption: AES-256 symmetric with passphrase from secrets file.
# To restore: gpg -d backup-YYYY-MM-DD.tar.gz.gpg | tar xzf -
#
# Cron (Sundays 2am):
#   0 2 * * 0 /home/stv/socialtradingvlog-website/tools/backup_encrypted.sh

set -euo pipefail

PROJECT_DIR="/home/stv/socialtradingvlog-website"
BACKUP_DIR="${PROJECT_DIR}/backups"
SECRETS_DIR="${HOME}/.config/stv-secrets"
DATE=$(date +%Y-%m-%d)
BACKUP_NAME="backup-${DATE}"
TMP_DIR=$(mktemp -d)
KEEP=4

# Passphrase from secrets (create if missing)
PASSFILE="${SECRETS_DIR}/backup-passphrase"
if [ ! -f "$PASSFILE" ]; then
    mkdir -p "$SECRETS_DIR"
    openssl rand -base64 32 > "$PASSFILE"
    chmod 600 "$PASSFILE"
    echo "[backup] Generated new backup passphrase at ${PASSFILE}"
    echo "[backup] IMPORTANT: Copy this passphrase somewhere safe outside the VPS!"
fi

echo "[backup] Starting encrypted backup — ${DATE}"

# Collect files into temp dir
mkdir -p "${TMP_DIR}/data"
mkdir -p "${TMP_DIR}/config"

# Data files
cp -r "${PROJECT_DIR}/data/"* "${TMP_DIR}/data/" 2>/dev/null || true

# Secrets
if [ -d "$SECRETS_DIR" ]; then
    cp -r "$SECRETS_DIR" "${TMP_DIR}/secrets" 2>/dev/null || true
fi

# System configs
cp /etc/caddy/Caddyfile "${TMP_DIR}/config/" 2>/dev/null || true
cp -r /etc/ssh/sshd_config.d/ "${TMP_DIR}/config/sshd_config.d/" 2>/dev/null || true
cp /etc/fail2ban/jail.local "${TMP_DIR}/config/" 2>/dev/null || true
cp /etc/sysctl.d/99-stv-security.conf "${TMP_DIR}/config/" 2>/dev/null || true

# Crontab
crontab -l > "${TMP_DIR}/config/crontab.txt" 2>/dev/null || true

# Create tar
tar czf "${TMP_DIR}/${BACKUP_NAME}.tar.gz" -C "${TMP_DIR}" data config secrets 2>/dev/null || \
tar czf "${TMP_DIR}/${BACKUP_NAME}.tar.gz" -C "${TMP_DIR}" data config 2>/dev/null

# Encrypt with GPG (symmetric AES-256)
mkdir -p "$BACKUP_DIR"
gpg --batch --yes --symmetric --cipher-algo AES256 \
    --passphrase-file "$PASSFILE" \
    --output "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz.gpg" \
    "${TMP_DIR}/${BACKUP_NAME}.tar.gz"

# Clean temp
rm -rf "$TMP_DIR"

# Rotate old backups (keep last $KEEP)
cd "$BACKUP_DIR"
ls -1t *.gpg 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f

# Report
SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz.gpg" | cut -f1)
COUNT=$(ls -1 "${BACKUP_DIR}/"*.gpg 2>/dev/null | wc -l)
echo "[backup] Done — ${BACKUP_NAME}.tar.gz.gpg (${SIZE}), ${COUNT} backup(s) retained"
