# Social Trading Vlog — Project Notes

## At the start of each session
- Check the latest GA report: `cat reports/latest.txt`
- Check pipeline progress: `tail -20 transcriptions/pipeline.log`
- Check for fix requests from the command centre: `ssh stv@89.167.73.64 "cat ~/socialtradingvlog-website/data/fix-queue.json 2>/dev/null || echo '[]'"`
- Share key insights, any notable changes, and any pending fix requests with Tom

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

## Working rules
- Run session start checks (GA report, pipeline status, fix queue) as a matter of course at the start of every session without being asked.
- **Deep debugging standard**: When anything fails, apply maximum rigour before concluding. This means:
  1. Read the actual error output first (don't trust summary messages — find the real traceback/log)
  2. Check the code thoroughly — look for swallowed errors, missing env vars, incorrect logic, silent failures
  3. Ask questions from every angle: Is the key loaded? Is the env inherited? Does the path resolve? Is the process context different (e.g. launchd vs terminal)?
  4. Test components in isolation to pinpoint exactly where the failure occurs
  5. Cross-check assumptions with data (e.g. "credits ran out" — actually calculate the spend before assuming)
  6. Only rule out code issues after concrete evidence — never assume it's an external/billing/network problem without proof
  7. If error messages are unhelpful, improve the logging as part of the fix
  8. Don't stop at the first plausible explanation — verify it matches ALL the evidence
- **Dual environment**: When fixing files locally, ALWAYS apply the same fix on the VPS immediately. The site runs from two locations — local Mac and VPS (89.167.73.64). Never assume a local fix is sufficient.
- **Check before bulk actions**: Before removing, unpublishing, or modifying content in bulk, always cross-reference each item against existing approvals, live status, schema references, and CLAUDE.md notes. Never assume all items in a group have the same status — check individually. Ask: "Has Tom already reviewed/approved any of these?"
