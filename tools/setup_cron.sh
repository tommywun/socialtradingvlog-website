#!/bin/bash
#
# Setup all autopilot cron jobs on VPS
# Run this once: bash tools/setup_cron.sh
#
# This creates all the automated tasks that keep the site
# running smoothly without any manual intervention.

set -euo pipefail

# ─── Auto-detect project directory ─────────────────────
# Works for both /home/stv/... and /var/www/... layouts
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="$PROJECT_DIR/venv/bin/python3"
if [ ! -f "$PYTHON" ]; then
    echo "ERROR: venv python not found at $PYTHON"
    echo "Create the venv first: python3 -m venv $PROJECT_DIR/venv && $PROJECT_DIR/venv/bin/pip install -r $PROJECT_DIR/requirements.txt"
    exit 1
fi
LOG_DIR="$PROJECT_DIR/logs"

echo "═══ STV Autopilot Cron Setup ═══"
echo ""
echo "  Project: $PROJECT_DIR"
echo "  Python:  $PYTHON"
echo "  Logs:    $LOG_DIR"
echo ""

# Create required directories
mkdir -p "$LOG_DIR"
mkdir -p "$PROJECT_DIR/backups"

# Build the crontab entries
# NOTE: Uses #STV marker for safe filtering — never remove entries without it
CRON_ENTRIES=$(cat <<'CRONTAB'
# ═══════════════════════════════════════════════════════════════
# STV SITE AUTOPILOT — Automated maintenance cron jobs
# Last updated: DATE_PLACEHOLDER
# ═══════════════════════════════════════════════════════════════

# ── Health Monitoring ────────────────────────────────────── #STV

# Uptime check every 5 minutes
*/5 * * * * PYTHON_PATH PROJECT_PATH/tools/site_autopilot.py --check uptime >> LOG_PATH/uptime.log 2>&1 #STV

# Full weekly health digest every Monday at 3am
0 3 * * 1 PYTHON_PATH PROJECT_PATH/tools/site_autopilot.py --check weekly >> LOG_PATH/weekly-digest.log 2>&1 #STV

# Daily full system check at 8am
0 8 * * * PYTHON_PATH PROJECT_PATH/tools/site_autopilot.py --check daily >> LOG_PATH/daily-check.log 2>&1 #STV

# Broken link scan weekly on Tuesdays at 2am
0 2 * * 2 PYTHON_PATH PROJECT_PATH/tools/site_autopilot.py --check links >> LOG_PATH/links.log 2>&1 #STV

# Stale content date check monthly on the 1st at 4am
0 4 1 * * PYTHON_PATH PROJECT_PATH/tools/site_autopilot.py --check content-dates >> LOG_PATH/content-dates.log 2>&1 #STV

# ── Platform Data ───────────────────────────────────────── #STV

# Weekly platform fee scrape via Playwright + update verified date (Mondays 2am)
0 2 * * 1 PYTHON_PATH PROJECT_PATH/tools/scrape_platform_fees.py >> LOG_PATH/scrape-fees.log 2>&1 #STV

# ── Subtitle Pipeline ───────────────────────────────────── #STV

# Daily subtitle upload attempt at 5am (skips already-uploaded, handles quota)
0 5 * * * PYTHON_PATH PROJECT_PATH/tools/upload_subtitles.py --skip-english >> LOG_PATH/subtitle-upload.log 2>&1 #STV

# Daily transcription pipeline (VPS-auto: fetch captions via API, translate, upload)
0 6 * * * PYTHON_PATH PROJECT_PATH/tools/run_pipeline.py --vps-auto >> LOG_PATH/pipeline.log 2>&1 #STV

# ── Link Building ───────────────────────────────────────── #STV

# Weekly link prospecting on Wednesdays at 6am (max 5 outreach emails/run)
0 6 * * 3 PYTHON_PATH PROJECT_PATH/tools/link_prospector.py >> LOG_PATH/link-prospector.log 2>&1 #STV

# ── Analytics & Optimization ─────────────────────────────── #STV

# Weekly analytics report + A/B test results + optimization suggestions (Mondays 4am)
0 4 * * 1 PYTHON_PATH PROJECT_PATH/tools/analytics_monitor.py --report weekly >> LOG_PATH/analytics.log 2>&1 #STV

# Suggest new tools monthly (1st of month) based on analytics
0 5 1 * * PYTHON_PATH PROJECT_PATH/tools/proposal_manager.py --suggest >> LOG_PATH/proposals.log 2>&1 #STV

# ── Proposal Approvals ──────────────────────────────────── #STV

# Check Telegram for Tom's approval/rejection replies every hour
0 * * * * PYTHON_PATH PROJECT_PATH/tools/proposal_manager.py --check >> LOG_PATH/proposals.log 2>&1 #STV

# ── Security Monitoring ─────────────────────────────────── #STV

# Quick security scan every 2 hours (ports, processes, permissions)
0 */2 * * * PYTHON_PATH PROJECT_PATH/tools/security_monitor.py --quick >> LOG_PATH/security.log 2>&1 #STV

# Full security scan every 4 hours
0 */4 * * * PYTHON_PATH PROJECT_PATH/tools/security_monitor.py >> LOG_PATH/security.log 2>&1 #STV

# File integrity check daily at 2am
0 2 * * * PYTHON_PATH PROJECT_PATH/tools/security_monitor.py --integrity >> LOG_PATH/security.log 2>&1 #STV

# ── Threat Intelligence ──────────────────────────────────── #STV

# Daily threat intelligence scan at 3am (CVEs, attack patterns, AI agent threats, DNS integrity)
0 3 * * * PYTHON_PATH PROJECT_PATH/tools/threat_scanner.py >> LOG_PATH/threat-scan.log 2>&1 #STV

# CVE advisory check twice daily (7am and 7pm) — catch critical vulns fast
0 7,19 * * * PYTHON_PATH PROJECT_PATH/tools/threat_scanner.py --check-cves >> LOG_PATH/threat-scan.log 2>&1 #STV

# Quick threat scan every 6 hours (SSH keys, listeners, AI agents)
0 */6 * * * PYTHON_PATH PROJECT_PATH/tools/threat_scanner.py --quick >> LOG_PATH/threat-scan.log 2>&1 #STV

# ── Security Self-Test ───────────────────────────────────── #STV

# Daily at 6am — verify ALL security protocols are working (alerts on failure)
0 6 * * * PYTHON_PATH PROJECT_PATH/tools/security_selftest.py >> LOG_PATH/selftest.log 2>&1 #STV

# ── Dependency Verification ──────────────────────────────── #STV

# Weekly full dependency verification (Mondays 4am) — hashes, CVEs, rogue packages
0 4 * * 1 PYTHON_PATH PROJECT_PATH/tools/verify_dependencies.py >> LOG_PATH/deps.log 2>&1 #STV

# Daily quick hash check (5am) — detect supply chain tampering fast
0 5 * * * PYTHON_PATH PROJECT_PATH/tools/verify_dependencies.py --check-only >> LOG_PATH/deps.log 2>&1 #STV

# ── Code Audit ───────────────────────────────────────────── #STV

# Weekly security audit of own code (Wednesdays 4am)
0 4 * * 3 PYTHON_PATH PROJECT_PATH/tools/code_audit.py >> LOG_PATH/code-audit.log 2>&1 #STV

# ── Log Rotation ─────────────────────────────────────────── #STV

# Rotate logs monthly (keep last 3 months)
0 0 1 * * find LOG_PATH -name "*.log" -mtime +90 -delete 2>/dev/null #STV

# ── Encrypted Backup ─────────────────────────────────────── #STV

# Weekly encrypted backup of data files (Sundays 1am)
# Uses secure temp dir (mktemp) instead of predictable /tmp paths
0 1 * * 0 TMPDIR=$(mktemp -d) && chmod 700 "$TMPDIR" && tar czf "$TMPDIR/backup.tar.gz" -C PROJECT_PATH data/ reports/ outreach/ 2>/dev/null && gpg --batch --yes --passphrase-file HOME_PATH/.config/stv-secrets/backup-passphrase.txt --symmetric --cipher-algo AES256 -o PROJECT_PATH/backups/data-$(date +\%Y\%m\%d).tar.gz.gpg "$TMPDIR/backup.tar.gz" && rm -rf "$TMPDIR" && find PROJECT_PATH/backups/ -name "data-*.gpg" -mtime +30 -delete 2>/dev/null || { rm -rf "$TMPDIR" 2>/dev/null; PYTHON_PATH -c "from tools.security_lib import send_telegram; send_telegram('Backup Failed', 'Weekly data backup failed. Check manually.', emoji='⚠️')" 2>/dev/null; } #STV

# Daily encrypted backup of secrets directory (safety net)
0 1 * * * TMPDIR=$(mktemp -d) && chmod 700 "$TMPDIR" && tar czf "$TMPDIR/secrets.tar.gz" -C HOME_PATH/.config stv-secrets/ 2>/dev/null && gpg --batch --yes --passphrase-file HOME_PATH/.config/stv-secrets/backup-passphrase.txt --symmetric --cipher-algo AES256 -o PROJECT_PATH/backups/secrets-$(date +\%Y\%m\%d).tar.gz.gpg "$TMPDIR/secrets.tar.gz" && rm -rf "$TMPDIR" && find PROJECT_PATH/backups/ -name "secrets-*.gpg" -mtime +7 -delete 2>/dev/null || rm -rf "$TMPDIR" 2>/dev/null #STV

# ── Self-Healing (System Doctor) ──────────────────────── #STV

# System doctor every 4 hours — scan logs, auto-fix known errors, monitor health
0 */4 * * * PYTHON_PATH PROJECT_PATH/tools/system_doctor.py >> LOG_PATH/doctor.log 2>&1 #STV

# Dead man's switch every 12 hours — alert if system doctor itself stopped running
0 */12 * * * PYTHON_PATH -c "import json,pathlib,sys,time; sys.path.insert(0,'PROJECT_PATH/tools'); f=pathlib.Path('PROJECT_PATH/data/doctor-heartbeat.json'); alive=(f.exists() and time.time()-json.loads(f.read_text()).get('ts',0)<28800); exec('from security_lib import send_telegram; send_telegram(\"Dead Man Switch\",\"System doctor not running for 8+ hours. Check VPS.\",emoji=\"💀\")') if not alive else None" 2>/dev/null #STV

CRONTAB
)

# Replace placeholders using printf to avoid sed injection
CRON_ENTRIES="${CRON_ENTRIES//PYTHON_PATH/$PYTHON}"
CRON_ENTRIES="${CRON_ENTRIES//PROJECT_PATH/$PROJECT_DIR}"
CRON_ENTRIES="${CRON_ENTRIES//LOG_PATH/$LOG_DIR}"
CRON_ENTRIES="${CRON_ENTRIES//HOME_PATH/$HOME}"
CRON_ENTRIES="${CRON_ENTRIES//DATE_PLACEHOLDER/$(date +%Y-%m-%d)}"

echo "These cron jobs will be installed:"
echo ""
echo "$CRON_ENTRIES" | head -20
echo "  ... ($(echo "$CRON_ENTRIES" | wc -l) lines total)"
echo ""

# Generate backup encryption passphrase if it doesn't exist
SECRETS_DIR="$HOME/.config/stv-secrets"
BACKUP_PASS="$SECRETS_DIR/backup-passphrase.txt"
if [ ! -f "$BACKUP_PASS" ]; then
    mkdir -p "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"
    openssl rand -base64 32 > "$BACKUP_PASS"
    chmod 600 "$BACKUP_PASS"
    echo "✓ Generated backup encryption passphrase: $BACKUP_PASS"
    echo "  IMPORTANT: Save this passphrase somewhere safe outside the VPS!"
    echo "  Without it, encrypted backups cannot be restored."
    echo ""
fi

# Install crontab — preserve ONLY non-STV entries (uses #STV marker for safe filtering)
# Also strip known legacy entries (old pipeline/upload crons without #STV marker)
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -v "#STV" | grep -v "run_pipeline\.py" | grep -v "upload_subtitles\.py" | grep -v "site_autopilot\.py" | grep -v "security_monitor\.py" | grep -v "translate_subtitles\.py" | grep -v "run\.sh" | grep -v "overnight\.sh" | grep -v "backup_encrypted\.sh" || true)

# Use mktemp for secure temp file (not predictable /tmp path)
TEMP_CRON=$(mktemp)
chmod 600 "$TEMP_CRON"
echo "$EXISTING_CRON" > "$TEMP_CRON"
echo "" >> "$TEMP_CRON"
echo "$CRON_ENTRIES" >> "$TEMP_CRON"

crontab "$TEMP_CRON"
rm -f "$TEMP_CRON"

echo "✓ Cron jobs installed!"
echo ""
echo "Verify with: crontab -l"
echo ""
echo "Logs will be written to: $LOG_DIR"
echo ""
echo "To check autopilot status:"
echo "  python3 $PROJECT_DIR/tools/site_autopilot.py --check uptime"
echo "  tail -f $LOG_DIR/uptime.log"
