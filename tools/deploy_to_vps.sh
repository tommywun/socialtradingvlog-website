#!/bin/bash
# Deploy tool scripts and dashboard to VPS.
# Runs rsync, restarts the dashboard service, then silently updates the
# security baseline so the integrity monitor doesn't alert on legitimate changes.

set -e

VPS="stv@89.167.73.64"
LOCAL="$HOME/socialtradingvlog-website"
REMOTE="~/socialtradingvlog-website"

echo "=== Syncing to VPS ==="
rsync -avz --delete \
  --exclude='.git' \
  --exclude='reports/' \
  --exclude='data/' \
  --exclude='venv/' \
  --exclude='docs/' \
  --exclude='transcriptions/' \
  --exclude='logs/' \
  --exclude='tools/__pycache__/' \
  "$LOCAL/" "$VPS:$REMOTE/"

echo ""
echo "=== Restarting dashboard ==="
ssh "$VPS" "sudo systemctl restart stv-dashboard"

echo ""
echo "=== Updating security baseline ==="
ssh "$VPS" "cd $REMOTE && source venv/bin/activate && python3 tools/security_monitor.py --update-baseline"

echo ""
echo "Done. Dashboard restarted, security baseline updated."
