#!/bin/bash
# Daily GA + pipeline status report for socialtradingvlog.com
# Runs via launchd each morning at 8am

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export OPENAI_API_KEY="$(cat ~/.config/stv-secrets/openai-api-key.txt 2>/dev/null)"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/stv-secrets/ga-service-account.json"

PYTHON="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python"
SITE_DIR="$HOME/socialtradingvlog-website"
REPORT_DIR="$SITE_DIR/reports"
TODAY=$(date +%Y-%m-%d)
REPORT_FILE="$REPORT_DIR/daily-$TODAY.txt"
LATEST="$REPORT_DIR/latest.txt"

mkdir -p "$REPORT_DIR"

{
    echo "============================================================"
    echo "  DAILY REPORT — socialtradingvlog.com — $TODAY"
    echo "============================================================"
    echo ""

    # GA report (last 7 days + last 30 days)
    echo "── LAST 7 DAYS ─────────────────────────────────────────────"
    $PYTHON "$SITE_DIR/tools/ga_report.py" --days 7 2>/dev/null
    echo ""
    echo "── LAST 30 DAYS ────────────────────────────────────────────"
    $PYTHON "$SITE_DIR/tools/ga_report.py" --days 30 2>/dev/null
    echo ""

    # Pipeline status
    echo "── PIPELINE STATUS ─────────────────────────────────────────"
    TOTAL_FOLDERS=$(ls -d "$SITE_DIR/transcriptions"/*/  2>/dev/null | wc -l | tr -d ' ')
    TRANSCRIBED=$(ls "$SITE_DIR/transcriptions"/*/transcript.txt 2>/dev/null | wc -l | tr -d ' ')
    VIDEO_PAGES=$(ls "$SITE_DIR/video"/*/index.html 2>/dev/null | wc -l | tr -d ' ')
    ARTICLE_PAGES=$(find "$SITE_DIR" -maxdepth 2 -name "index.html" -not -path "*/video/*" 2>/dev/null | wc -l | tr -d ' ')

    echo "  Transcriptions:  $TRANSCRIBED completed"
    echo "  Video pages:     $VIDEO_PAGES generated"
    echo "  Article pages:   $ARTICLE_PAGES generated"
    echo ""

    # Last pipeline log entries
    if [ -f "$SITE_DIR/transcriptions/pipeline.log" ]; then
        echo "  Last pipeline activity:"
        tail -5 "$SITE_DIR/transcriptions/pipeline.log" | sed 's/^/    /'
    fi

    echo ""
    echo "============================================================"
    echo "  Report saved: $REPORT_FILE"
    echo "============================================================"

} > "$REPORT_FILE" 2>&1

# Also save as 'latest' for easy access
cp "$REPORT_FILE" "$LATEST"
