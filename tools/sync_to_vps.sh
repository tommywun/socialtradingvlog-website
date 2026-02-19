#!/bin/bash
# Sync transcriptions from Mac to VPS, then trigger VPS pipeline.
#
# Run this after transcribing on Mac, or set as a launchd job.
# Only syncs English SRT files — the VPS handles translation + upload.

VPS="stv@89.167.73.64"
LOCAL_DIR="$HOME/socialtradingvlog-website/transcriptions"
REMOTE_DIR="socialtradingvlog-website/transcriptions"

echo "=== Syncing transcriptions to VPS ==="
echo "$(date)"

# Sync all transcription folders (English SRTs + transcripts)
rsync -avz --include='*/' \
    --include='subtitles.en.srt' \
    --include='subtitles.en.vtt' \
    --include='transcript.txt' \
    --exclude='*' \
    "$LOCAL_DIR/" "$VPS:~/$REMOTE_DIR/"

echo ""
echo "=== Triggering VPS pipeline ==="

# Run the VPS pipeline in background (translate + upload only)
ssh "$VPS" "cd ~/socialtradingvlog-website && source venv/bin/activate && nohup python3 tools/run_pipeline.py --translate-only > logs/pipeline-$(date +%Y-%m-%d-%H%M).log 2>&1 &"

echo "VPS pipeline started. Check logs with: ssh $VPS 'tail -f ~/socialtradingvlog-website/logs/pipeline-*.log'"
echo "Done!"
