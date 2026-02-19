#!/bin/bash
# One-time script to finish YouTube description updates after quota reset.
# Runs the update, logs the result, then removes itself from launchd.

LOG="/tmp/stv-youtube-update.log"
echo "=== YouTube description update — $(date) ===" >> "$LOG"

cd /Users/thomaswest/socialtradingvlog-website
python3 tools/youtube_descriptions.py --update >> "$LOG" 2>&1

echo "=== Done — $(date) ===" >> "$LOG"

# Clean up: unload and remove the launchd plist
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.stv.youtube-update.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/com.stv.youtube-update.plist
rm -f /Users/thomaswest/socialtradingvlog-website/tools/finish_youtube_update.sh
