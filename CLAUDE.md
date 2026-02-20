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
- `python3 tools/generate_sitemap.py` — regenerate sitemap.xml (289 URLs, hreflang)

## VPS (Command Centre)
- **Host**: 89.167.73.64, user `stv`
- **Dashboard**: app.socialtradingvlog.com (tools/dashboard.py, port 8080)
- **Service**: `sudo systemctl restart stv-dashboard`
- **Sessions**: Persisted to `data/sessions.json` (90-day expiry)
- **WebAuthn**: Face ID credentials in `data/webauthn-credentials.json`, RP ID = `socialtradingvlog.com`
- **Review queue**: 20 articles in `data/review-staging/`, metadata in `data/review-queue.json`
- **Cron**: `overnight.sh` runs at 0,2,4,6,8 UTC for pipeline retries, sitemap gen, git pulls
- **GA key**: `~/.config/stv-secrets/ga-service-account.json` (copied from Mac)

## Newsletter
- Provider: Resend API
- Verified domain: `send.socialtradingvlog.com` (NOT socialtradingvlog.com)
- Subscribers stored in `data/subscribers.json` on VPS

## Calculators
4 tools at `/calculators/`:
- Fee Calculator — spread, overnight, conversion, withdrawal cost breakdown
- ROI Calculator — compound growth projections for copy trading
- Compare Platforms — eToro vs Trading 212, Interactive Brokers, etc.
- Position Size Calculator — allocation per copied trader with risk profiles

Translated to 5 languages: ES (`/es/calculadoras/`), DE (`/de/rechner/`), FR (`/fr/calculateurs/`), PT (`/pt/calculadoras/`), AR (`/ar/calculators/`)
- German and Arabic are missing compare-platforms translations (hit rate limit)

## Content review queue (20 articles)
Articles in `data/review-staging/` on VPS. Review/publish via command centre Review tab.
- 14 SEO articles, 5 comparison articles, 1 checklist
- Checklist was unpublished from live site (removed from git)

## Dashboard features
- Persistent sessions (no logout on restart)
- WebAuthn Face ID login (browser passkey)
- Content review queue (preview, edit, publish to git)
- SEO checker (10-point analysis per article)
- Clickable error resolution with fix guides and "Fix It" buttons
- Auto-fix system for common issues
- Health monitoring with actionable steps

## SSH/VPS editing pattern
When editing dashboard.py on VPS, avoid SSH heredocs for Python code containing regex
or quote characters. Instead: write a Python script to /tmp locally, scp it to VPS,
then run it remotely. This avoids quote mangling through SSH.

## Schema markup
All pages have proper JSON-LD: Article/Review + FAQPage + BreadcrumbList.
Author name: "Tom West". Publisher: "SocialTradingVlog".
Homepage has Organization, WebSite with SearchAction.
eToro review has Review schema with itemReviewed.

## Internal linking
13 SEO articles have "You might also like" sections with contextually relevant cross-links.
Calculator pages link to each other via nav bar.
