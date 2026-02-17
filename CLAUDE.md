# Social Trading Vlog — Project Notes

## At the start of each session
- Check the latest GA report: `cat reports/latest.txt`
- Check pipeline progress: `tail -20 transcriptions/pipeline.log`
- Share key insights and any notable changes with Tom

## Secrets location
All API keys and credentials are stored in `~/.config/stv-secrets/` (NOT in the repo).
- `ga-service-account.json` — Google Analytics API access
- `openai-api-key.txt` — OpenAI Whisper API key

## Daily report
Runs automatically at 8am via launchd. Reports saved to `reports/daily-YYYY-MM-DD.txt`.
Latest is always at `reports/latest.txt`.

## Key tools
- `python3 tools/ga_report.py --days 7` — pull GA stats on demand
- `python3 tools/generate_article_pages.py --force` — regenerate article pages
- `python3 tools/generate_video_pages.py --force` — regenerate video pages
- `python3 tools/run_pipeline.py` — transcription + translation pipeline
