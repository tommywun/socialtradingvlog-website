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
- `python3 tools/run_pipeline.py` — transcription + translation pipeline (Mac: full, VPS: --vps-auto)
- `python3 tools/run_pipeline.py --vps-auto` — VPS pipeline: fetch captions + translate + upload
- `python3 tools/transcribe_top_videos.py --top 30` — Mac-only: Whisper-transcribe top 30 by views
- `python3 tools/translate_subtitles.py VID --engine openai` — translate with GPT-4o-mini
- `python3 tools/upload_subtitles.py --dry-run` — preview YouTube subtitle uploads
- `python3 tools/system_doctor.py` — self-healing: scan logs, fix known errors, check system health
- `python3 tools/generate_sitemap.py` — regenerate sitemap.xml (hreflang)

## VPS (Command Centre)
- **Host**: 89.167.73.64, user `stv`
- **Dashboard**: app.socialtradingvlog.com (tools/dashboard.py, port 8080)
- **Service**: `sudo systemctl restart stv-dashboard`
- **Sessions**: Persisted to `data/sessions.json` (90-day expiry)
- **WebAuthn**: Face ID credentials in `data/webauthn-credentials.json`, RP ID = `socialtradingvlog.com`
- **Review queue**: 20 articles in `data/review-staging/`, metadata in `data/review-queue.json`
- **Cron**: `setup_cron.sh` installs all #STV cron jobs (pipeline, security, doctor, backups)
- **GA key**: `~/.config/stv-secrets/ga-service-account.json` (copied from Mac)

## VPS Autonomous Pipeline Architecture

The subtitle pipeline runs fully autonomously on VPS. Mac is only needed for one-time Whisper transcriptions.

**Daily VPS pipeline (6am cron, `run_pipeline.py --vps-auto`):**
1. For each video (sorted by view count, highest first):
   - English SRT exists? Skip to translate
   - No SRT? Fetch via YouTube Captions API (`fetch_captions.py`)
   - API fails? Skip, retry tomorrow
2. Translate to 9 languages:
   - Top 30 videos by views: GPT-4o-mini (`--engine openai`, high quality)
   - Remaining videos: deep-translator (`--engine deep-translator`, free)
   - Quality gate on both: reject if >50% identical to English, empty segments, wrong character set
3. Upload to YouTube (max 2 videos/day, ~7,200 API units, quota-aware)
4. Telegram summary on completion

**Hybrid transcription strategy:**
- Mac: Whisper API for top 30 by views (`transcribe_top_videos.py`) → sync to VPS
- VPS: YouTube ASR captions for remaining 303 (`fetch_captions.py`)
- Whisper videos get priority (already sorted by views)

**Self-healing (every 4h, `system_doctor.py`):**
- Scan logs for errors → match known patterns → auto-fix
- Check disk space (auto-clean if >85%), services, OAuth tokens, pipeline progress
- Write heartbeat → dead man's switch alerts if stale (every 12h)
- Alert Tom only for unknown/unfixable errors

**YouTube API quota:** 10,000 units/day. Caption insert = ~400 units. 2 full videos (18 tracks) per day is safe. Tom has applied for quota increase.

**Quota budget per API call:**
- `captions.list`: ~50 units per video
- `captions.download`: ~200 units per video
- `captions.insert` (upload): ~400 units per language track
- 9 languages × 400 = 3,600 units to upload subtitles for 1 video
- Can fetch captions for ~30-40 videos per day before quota runs out

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

## Video Pages Pipeline
Each of the 333 YouTube videos will get a proper SEO-rewritten article page (NOT a transcript dump).
Pipeline: transcribe video → extract key points → rewrite as SEO article targeting specific keyphrase → Tom approves → publish → translate to all 9 languages with localised SEO terms.
- `generate_video_pages.py` has an `"approved": True` gate — no pages generated without approval
- Old transcript-dump pages have been purged (30 EN + 5 translated = 35 pages removed, Feb 2025)
- Transcriptions in `transcriptions/` are preserved (used for subtitles and as source material for rewriting)

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
- **Learn and document immediately**: Whenever something goes wrong, a mistake is made, a workaround is discovered, or a non-obvious pattern emerges — immediately add it to this file as a rule with the most efficient protocol to follow next time. Don't wait to be asked. Don't rely on memory across sessions. If it could come up again, write it down now with a clear, actionable procedure. This is the single most important rule — every other rule in this section exists because of it.
- **Advocate for the optimal approach**: Always state the most efficient strategy with reasoning, even if Tom suggests something different. Don't defer just to be agreeable — Tom values logical pushback and a second perspective. If you think a different approach is better, say so clearly and explain why. Wasted exchanges from passive agreement cost more than one confident recommendation. Give your honest assessment first, then let Tom decide.
- Run session start checks (GA report, pipeline status, fix queue) as a matter of course at the start of every session without being asked.
- **VPS access: ALWAYS use `stv@89.167.73.64`** — never `root@`, never `socialtradingvlog.com`. The domain goes through Cloudflare which only proxies HTTP (ports 80/443), not SSH (port 22). Using the domain for SSH will fail with "No route to host". This applies to all SSH, rsync, and scp commands.
- **Deep debugging standard**: When anything fails, apply maximum rigour before concluding. This means:
  1. Read the actual error output first (don't trust summary messages — find the real traceback/log)
  2. Check the code thoroughly — look for swallowed errors, missing env vars, incorrect logic, silent failures
  3. Ask questions from every angle: Is the key loaded? Is the env inherited? Does the path resolve? Is the process context different (e.g. launchd vs terminal)?
  4. Test components in isolation to pinpoint exactly where the failure occurs
  5. Cross-check assumptions with data (e.g. "credits ran out" — actually calculate the spend before assuming)
  6. Only rule out code issues after concrete evidence — never assume it's an external/billing/network problem without proof
  7. If error messages are unhelpful, improve the logging as part of the fix
  8. Don't stop at the first plausible explanation — verify it matches ALL the evidence
  9. Before proposing a fix, check what already exists. Don't assume something needs creating when it might just need copying or enabling. `ls` before you build.
  10. Don't take command output at face value. When a script reports "success" or "X/Y complete, 0 errors", ask: what do those numbers actually mean? Does "complete" mean fully processed or just "didn't crash"? Does "0 errors" mean real progress or just that failures were silently skipped? Cross-check reported numbers against the known ground truth (e.g. 35/333 transcribed) before reporting them to Tom. This rule exists because a translate-only run reported "333/333 complete, 0 errors" when it had actually skipped 295 untranscribed videos — and that misleading output was reported as a success.
- **Before fixing anything, check if it was already fixed**: When an error appears on CC or in logs, the FIRST step is NOT to investigate from scratch. Instead: (1) Search this file and session history for prior fixes to the same system. (2) Check if the code on VPS matches the local code — if it doesn't, rsync likely overwrote a VPS-only patch. (3) If a prior fix exists, the problem is that the fix wasn't applied locally and got overwritten by rsync. Re-apply it locally and sync. This rule exists because the same error (pipeline running full transcription on VPS) was fixed THREE times in one session — each time the VPS-only fix was overwritten by rsync, and each time the earlier fix was forgotten and a new (sometimes wrong) solution was proposed instead.
  Specifically for quota/pipeline errors, check: (1) Is pipeline in "vps-auto" mode? (log shows "(vps-auto)" vs "(full)") (2) Stale cron entries? (`crontab -l | grep run_pipeline`) (3) Lock file blocking? (`cat /tmp/stv-pipeline.lock`)
- **Dual environment**: The site runs from two locations — local Mac and VPS (89.167.73.64). ALWAYS edit locally first, then sync to VPS. Never patch VPS directly — rsync --delete will overwrite VPS-only changes with the local version. The flow is: edit local → commit → rsync to VPS. Never the other way around.
- **MANDATORY pre-deletion audit**: Before ANY bulk removal or unpublishing, you MUST complete this checklist and show it to Tom BEFORE executing:
  1. List every item that will be affected
  2. For each item, check: does it have `"approved": True` in any generation script?
  3. For each item, check: does it have `article_sections` or other hand-written content?
  4. For each item, check: is it mentioned in CLAUDE.md as reviewed/approved/live?
  5. For each item, check: did Tom explicitly approve it in conversation history?
  6. Present the audit to Tom: "These X items will be removed. These Y items appear to be approved/hand-written and will be KEPT: [list]"
  7. Only proceed after Tom confirms
  This rule exists because bulk deletions have destroyed approved content TWICE (etoro-review, why-do-most-etoro-traders-lose-money). The fix is to audit first, act second — never the other way around.
- **Update CC immediately when status changes**: Whenever a task is completed, a situation changes, or progress is made on any tracked item (pipeline, subtitles, video pages, articles, etc.), immediately update `data/status-overrides.json` on VPS to reflect the current state. The command centre is Tom's window into what's happening — stale or inaccurate statuses are misleading. Use: `ssh stv@89.167.73.64 "cat > ~/socialtradingvlog-website/data/status-overrides.json << 'EOF' ... EOF"`
- **VPS rsync excludes**: When syncing to VPS with rsync --delete, ALWAYS exclude: `.git`, `transcriptions`, `node_modules`, `data`, `.env`, `venv`, `logs`, `tools/__pycache__`. Logs are generated on VPS by cron jobs (pipeline, security, doctor, etc.) and don't exist locally — rsync --delete will wipe them. The __pycache__ is VPS-specific (Python 3.12 vs local version). The venv on VPS is not in git and must not be deleted.
- **After adding new pages, regenerate sitemap**: Run `python3 tools/generate_sitemap.py` after creating new pages or translations. The sitemap includes hreflang links — missing pages mean missing SEO signals. This was missed when 5 scam page translations were created (Feb 2026).
- **Always check CLAUDE.md before asking Tom**: When something fails or you need project info (VPS credentials, tool paths, architecture, prior fixes), check this file FIRST. Don't ask Tom questions that are already answered here.

## Affiliate Partnerships
- **eToro**: $450 CPA (signed, active). This is the benchmark — don't accept less than $300 from others.
- Full strategy, platform map per language, and pitch templates in `outreach/affiliate-strategy.md`
- Comparison tool platforms differ by language version — see strategy doc for which to feature/omit per market
- KO version: most current platforms blocked in South Korea, needs local platforms (Kiwoom, Toss)
- AR version: DEGIRO not available, Trading 212 limited — add Sarwa, SNB Capital
- EN-US: needs separate geo-targeted page (Schwab, Fidelity, Robinhood, Webull, IBKR)
- New market priorities: India (#1), Turkey (#2), Thailand (#3), Japan (#4), Indonesia (#5)

## Comparison Tool Enhancement (planned)
- Scrape real fees from all platforms weekly (fixed fees, overnight rates, typical spreads)
- Side-by-side trade cost simulation across platforms per asset class
- Each language version features different platforms appropriate to that market
- "Special Offer" badge for affiliate partners who provide exclusive user deals

## Security Policy — TOP PRIORITY

Security of the entire system (VPS, laptop, secrets, Telegram bot, all tools) is the highest priority. Every session must verify security posture. Every code change must be evaluated for security implications.

### Secrets management
- **Location**: `~/.config/stv-secrets/` — NEVER in the repo
- **Required permissions**: Directory = `700`, all files = `600`
- **Files**: telegram-bot-token.txt, telegram-chat-id.txt, resend-api-key.txt, email-alerts.json, ga-service-account.json, gmail-oauth.json, gmail-token.pickle, openai-api-key.txt, youtube-oauth.json, youtube-token.pickle, cloudflare-api-token.txt
- **Rule**: If any secret file is found with permissions wider than 600, fix immediately and alert Tom
- **Rule**: NEVER log, print, or echo secret values. NEVER pass secrets as CLI arguments (visible in `ps`). Use files or environment variables only.

### Telegram bot hardening
- **Chat ID verification**: Only process messages from Tom's verified chat_id (stored in `telegram-chat-id.txt`)
- **Input sanitization**: All input stripped of control chars, limited to 50 chars, lowercased, checked against injection patterns
- **Blocked patterns**: `ignore`, `forget`, `pretend`, `system`, `admin`, `execute`, `eval(`, `exec(`, `import `, `os.`, `subprocess`, `__`, `$(`, backtick, `&&`, `||`, `;`, `|`, `>`, `<`, `\`, `{`, `}`, `curl`, `wget`
- **Rate limiting**: Max 20 commands/hour per chat_id
- **Strict parsing**: Only exact commands accepted: `yes [N]`, `no [N]`, `/proposals`, `/list`, `/status`
- **No shell execution**: Approved proposals are queued only — NEVER executed automatically. No `subprocess.run(shell=True)` anywhere in the codebase.
- **Silent rejection**: Unknown/invalid messages are silently ignored (no error messages that help attackers understand the interface)

### Security monitoring (cron schedule)
- **Every 2 hours**: Quick scan — open ports, suspicious processes, secret file permissions (`security_monitor.py --quick`)
- **Every 4 hours**: Full scan — all 9 checks including SSH brute force, file integrity, crontab integrity, data tampering, web exposure, outbound connections (`security_monitor.py`)
- **Daily at 2am**: File integrity check — SHA-256 hashes of all critical tool scripts (`security_monitor.py --integrity`)
- **Alert threshold**: 3+ issues triggers Telegram + email alert to Tom

### Web server security
**VPS uses Caddy v2.10** (not nginx). Config at `/etc/caddy/Caddyfile` — hardened Feb 2026.
- Caddy auto-provisions TLS certificates via Let's Encrypt (auto-renew)
- **Path blocking** (returns 404): `/.git/*`, `/.env`, `/.claude/*`, `/tools/*`, `/data/*`, `/logs/*`, `/reports/*`, `/node_modules/*`, `/CLAUDE.md`, `/*.py`, `/*.sh`, config files
- **Security headers**: X-Frame-Options DENY, X-Content-Type-Options nosniff, X-XSS-Protection, Strict-Transport-Security (1 year + includeSubDomains), Content-Security-Policy, Permissions-Policy, Referrer-Policy strict-origin-when-cross-origin
- **CSP**: self + cdn.jsdelivr.net for scripts/styles, fonts.googleapis.com/gstatic.com for fonts, frame-ancestors none
- **Server header removed** (-Server directive)
- **Request body limit**: 10MB
- **Access logging**: JSON format to `/var/log/caddy/access.log` (50MB rotation, keep 5)
- **Reverse proxy**: X-Real-IP header passthrough, 5s dial timeout, 30s response timeout
- To edit: `ssh stv@89.167.73.64 'sudo nano /etc/caddy/Caddyfile'` then `sudo systemctl reload caddy`

### VPS hardening script (`tools/harden_vps.sh`)
Run once on deployment: `sudo bash tools/harden_vps.sh` — 14-step automated hardening:
1. System updates + security package installation
2. **SSH hardening**: key-only auth, no root login, `AllowUsers stv`, strong ciphers only (chacha20, aes256-gcm), `MaxAuthTries 3`, idle timeout 5min, `LogLevel VERBOSE`
3. **UFW firewall**: default deny, only ports 22/80/443/8080, SSH rate-limited
4. **fail2ban**: SSH brute force (ban 1hr after 3 fails), nginx scanner blocking (404 scanners, bad requests, bot search), custom filter for attack path probes
5. **Kernel hardening** (sysctl): SYN cookies, disable IP forwarding, disable ICMP redirects, reverse path filtering, restrict core dumps, restrict kernel pointers, disable unprivileged BPF
6. **Automatic security updates**: `unattended-upgrades` with auto-reboot at 4am for kernel updates
7. **File permissions**: crontab restricted, SSH keys locked, secrets at 600/700, project dirs at 750
8. **Nginx**: `server_tokens off`, rate limit zones, include `nginx-security.conf`
9. **Disabled services**: avahi-daemon, cups, bluetooth, snapd
10. **SSH 2FA**: Google Authenticator (TOTP) — key + one-time code for SSH login
11. **TLS hardening**: TLS 1.2/1.3 only, strong ciphers, 2048-bit DH params, session tickets off
12. **DNS CAA record check**: Warns if no CAA record exists, provides exact record to add
13. **Cloudflare WAF prep**: Creates nginx snippet to restrict traffic to Cloudflare IPs only
14. **DH parameters**: Generates strong 2048-bit Diffie-Hellman parameters for forward secrecy

### Encrypted backups
- Weekly data backup encrypted with AES-256 GPG (Sundays 1am)
- Daily secrets backup encrypted with AES-256 GPG (kept 7 days)
- Passphrase stored at `~/.config/stv-secrets/backup-passphrase.txt` — auto-generated on first cron setup
- **CRITICAL**: Save backup passphrase somewhere outside the VPS. Without it, backups can't be restored.
- To restore: `gpg --decrypt backups/data-YYYYMMDD.tar.gz.gpg | tar xzf -`

### VPS hardening checklist (manual verification after script)
1. Set up 2FA: `su - stv && google-authenticator -t -d -f -r 3 -R 30`
2. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
3. Save the emergency scratch codes somewhere safe!
4. Test SSH login in a NEW terminal — verify key + TOTP works before closing current session
5. Include `nginx-security.conf` in server block
6. Include `snippets/ssl-hardening.conf` in server block
7. Run `tools/setup_cron.sh` to install all monitoring crons
8. Run `python3 tools/security_monitor.py` — should report 0 issues
9. Run `python3 tools/threat_scanner.py` — baseline threat scan
10. Add DNS CAA records at registrar:
    - `0 issue "letsencrypt.org"`
    - `0 issuewild "letsencrypt.org"`
    - `0 iodef "mailto:tom@socialtradingvlog.com"`
11. Set up Cloudflare (free tier) for DDoS protection + WAF:
    - SSL/TLS → Full (Strict), WAF managed rules on, Bot Fight Mode on
    - Then enable `include snippets/cloudflare-only.conf;` in nginx to block direct origin access

### Automated threat response (`tools/threat_response.py`)
When the scanner detects a threat, it automatically takes safe, reversible actions:

**Automatic (no approval needed — safe and reversible):**
- **Permission violations**: Auto-fixed to 600/700 immediately
- **Suspicious processes** (cryptominer, meterpreter, reverse_shell): Killed with SIGTERM
- **Aggressive scanner IPs** (>20 attack attempts): Blocked via UFW (`ufw deny from IP`)
- **Safelist protection**: Never kills sshd, nginx, python3, bash, systemd, cron, fail2ban

**Manual Telegram commands (for Tom only):**
- Emergency lockdown: shuts all ports except SSH, stops dashboard
- Unlock: restores all services from lockdown
- Block specific IP: `python3 tools/threat_response.py --block-ip X.X.X.X`

**Response hierarchy (fastest to most thorough):**
1. **Seconds**: Auto-block IP, auto-kill process, auto-fix permissions
2. **Minutes**: Telegram alert sent to Tom with details
3. **Hours**: Full scan runs (every 4h), threat scanner runs (every 6h)
4. **Daily**: Self-test verifies all 16 protocols working, dependency hashes checked

### Incident response playbook
**Level 1 — Scanner alert (automated):**
1. Check `logs/security.log` and `logs/threat-scan.log`
2. Auto-response already handled (IP blocked / process killed / perms fixed)
3. Verify the auto-response worked: `ufw status`, `ps aux`

**Level 2 — Credential exposure:**
1. If Telegram bot token exposed: Generate new token via @BotFather, update `telegram-bot-token.txt`
2. If SSH key compromised: Remove from `~/.ssh/authorized_keys`, add new key
3. If API key exposed: Rotate at provider (Google, Resend), update secrets file
4. After rotation: `chmod 600` on all changed files, run `security_monitor.py`

**Level 3 — File integrity breach:**
1. `aide --check` to see all changed files at OS level
2. `ausearch -k stv_tools` to see who changed tool files and when
3. Compare with git: `git diff HEAD -- tools/`
4. If changes don't match a known deployment → assume compromise
5. Restore from last known-good git commit: `git checkout <known-good-hash> -- tools/`
6. Re-run `security_monitor.py --integrity` to rebuild baseline

**Level 4 — Active intrusion:**
1. IMMEDIATE: `python3 tools/threat_response.py --lockdown` (SSH only, everything else down)
2. Check who's logged in: `w`, `who`, `last`
3. Check active connections: `ss -tnp`
4. Check for persistence: `crontab -l`, `ls /etc/cron.d/`, `ausearch -k crontab`
5. Check for backdoor users: `cat /etc/passwd | grep -v nologin`
6. Check for modified binaries: `aide --check`
7. If confirmed compromised: Rebuild VPS from scratch (re-deploy from git)

**Level 5 — Full compromise (nuclear option):**
1. Destroy VPS instance at hosting provider
2. Create new VPS
3. Deploy from clean git repo
4. Run `harden_vps.sh` + `harden_vps_advanced.sh`
5. Restore data from most recent encrypted backup
6. Rotate ALL credentials (Telegram, Google, Resend, SSH keys)
7. Run full verification: `security_selftest.py` + `verify_dependencies.py`

### Daily threat intelligence (`tools/threat_scanner.py`)
Automated threat scanning that runs via cron:
- **Daily at 3am**: Full scan — CVE advisories (Ubuntu + CISA KEV), nginx attack pattern analysis, SSH key tampering, package integrity, SSL cert validity, DNS integrity, AI agent threats (OpenClaw-style), user account audit, listening services
- **Twice daily (7am/7pm)**: CVE advisory check — catches critical vulns fast
- **Every 6 hours**: Quick scan — SSH keys, listeners, AI agent processes
- Checks CISA Known Exploited Vulnerabilities catalog for actively-exploited CVEs affecting our stack
- Scans web files for prompt injection patterns (`ignore previous instructions`, `<|im_start|>`, etc.)
- Detects AI agent processes (OpenClaw, AutoGPT, etc.) that shouldn't be running on the VPS
- Monitors for DNS hijacking (verifies socialtradingvlog.com → 89.167.73.64)
- Alerts via Telegram on any findings

### AI-era threat awareness (February 2026)
- **OpenClaw**: Open-source AI agent that can execute shell commands. 12% of its skill marketplace was compromised (341/2857 malicious skills). Infostealer malware is targeting OpenClaw config files and API keys. CVE-2026-25253 allowed one-click RCE. Over 30,000 exposed instances found.
- **GPT-5.3-Codex**: OpenAI warns this model can meaningfully enable real-world cyber harm. Scored 76% on CTF exercises (up from 27% with GPT-5). Autonomous operation makes brute-force attacks feasible.
- **AI-powered attacks**: Nation-state groups using Claude/GPT to automate 80-90% of cyberespionage attack chains.
- **Mitigation**: No AI agents installed on VPS. Telegram bot has strict input sanitization blocking injection patterns. All tool scripts have file integrity monitoring. No shell execution on user input. Daily threat scans for AI agent processes.

### Daily security self-test (`tools/security_selftest.py`)
Runs daily at 6am — verifies ALL 16 security protocols are actually working:
1. UFW firewall enabled + correct ports only
2. fail2ban running with active jails
3. SSH config hardened (no password, no root, strong ciphers)
4. Secret file permissions correct (600/700)
5. All security cron jobs installed
6. Security monitor ran recently (<5h ago)
7. Threat scanner ran recently (<25h ago)
8. Nginx security headers present + tokens hidden
9. Unattended-upgrades enabled
10. SSH 2FA (Google Authenticator) configured
11. SSL certificate valid + not expiring soon
12. File integrity hashes current
13. No unauthorized SSH keys
14. Recent encrypted backups exist
15. Kernel security parameters correct
16. DNS resolves to 89.167.73.64

On ANY failure: sends URGENT Telegram alert. On Monday: sends weekly "all clear" confirmation.

### Supply chain verification (`tools/verify_dependencies.py`)
All 8 direct dependencies + 14 transitive dependencies are pinned with SHA-256 hashes in `requirements.txt`.
- **Weekly (Mondays 4am)**: Full verification — hash match against PyPI, CVE scan, rogue package detection
- **Daily (5am)**: Quick hash check — detect supply chain tampering fast
- Checks: version pinning, SHA-256 hash vs PyPI, package yanked/removed status, unexpected packages
- Install ONLY with: `pip install --require-hashes -r requirements.txt`
- **NEVER** install packages without hash verification
- To update a package: download, hash, update requirements.txt, verify, commit
- Our 8 packages (verified 2026-02-22): beautifulsoup4, deep-translator, google-analytics-data, google-api-python-client, google-auth, google-auth-httplib2, google-auth-oauthlib, resend

### Advanced VPS hardening (`tools/harden_vps_advanced.sh`)
Run after basic hardening: `sudo bash tools/harden_vps_advanced.sh`
1. **CrowdSec**: Crowd-sourced threat intelligence — processes 1M+ unique IPs daily, shares threat data globally, behavioral detection, zero-day scenarios
2. **AIDE**: OS-level file integrity monitoring for /etc/ssh, /etc/nginx, /etc/pam.d, STV tools/data
3. **auditd**: Kernel-level audit logging — monitors SSH config, crontab, user changes, nginx config, SSH keys, STV tools dir, STV secrets dir, all root commands
4. **Process accounting**: Tracks all executed commands (use `lastcomm` to review)
5. **USB storage blocked**: No removable media on VPS
6. **SSH login banner**: Legal warning displayed before auth
7. **Core dumps disabled**: System-wide via limits.conf + sysctl
8. **Compiler access restricted**: gcc/g++/cc/make root-only (prevents compile-on-server attacks)
9. **Logwatch**: Daily summary of all system security events
10. **Immutable flags**: Critical security configs can't be changed even by root without explicit `chattr -i`

### CLAUDE.md protection
This file contains sensitive infrastructure details (VPS IP, user, service names, credential locations).
- **Web-blocked**: nginx-security.conf blocks all `.md` files from being served
- **Git-only**: Only accessible via git repo, never served to the public
- On VPS: file permissions set to 640 (owner + group read, no world access)
- If this file is found to be web-accessible, treat as a security incident

### Shared security library (`tools/security_lib.py`)
All security tools share a common library that provides:
- **Unified Telegram alerting** with rate limiting (max 10/hour) and deduplication (30-min window)
- **Centralized logging** with persistent file writes
- **IP validation** (proper octet range checking 0-255)
- **PEP 503 package name normalization** for dependency checking
- **Security state tracking** via `data/security-state.json` — records last tool runs, recent alerts (file-locked with fcntl)
- Used by: security_monitor.py, threat_scanner.py, security_selftest.py, threat_response.py, verify_dependencies.py, code_audit.py, run_pipeline.py, upload_subtitles.py, system_doctor.py

### Automated code audit (`tools/code_audit.py`)
Weekly security and quality scan of all STV code:
- **Pattern-based scanning**: Command injection, hardcoded secrets, eval/exec, pickle, unsafe temp files, SQL injection, XSS
- **AST analysis**: Unused imports, function complexity (>80 lines flagged), code structure
- **Shell script audit**: eval, unquoted variables, predictable /tmp, curl|bash
- **File permission checks**: World-writable files flagged
- **HTML security scan**: HTTP scripts, innerHTML, document.write
- **Refactoring opportunities**: Duplicate functions, large files, code duplication
- **Allowlist**: Known false positives (pattern definitions, injection blocklists, Google OAuth pickle.load) are manually reviewed and suppressed
- Cron: Weekly on Wednesdays at 4am
- Alerts Tom via Telegram on CRITICAL/HIGH findings

### Code security rules
- **NEVER** use `subprocess.run(..., shell=True)` — always pass commands as lists
- **NEVER** use `eval()`, `exec()`, or `__import__()` on any user-supplied data
- **NEVER** interpolate user input into shell commands, SQL queries, or HTML without proper escaping
- **ALWAYS** validate and sanitize external input (Telegram messages, web form data, API responses)
- **ALWAYS** use parameterized queries for any future database operations
- **ALWAYS** check file permissions after creating/modifying secret files
- **NEVER** install AI agent frameworks (OpenClaw, AutoGPT, BabyAGI, LangChain agents) on the VPS
- **ALWAYS** pin Python package versions and verify no unexpected packages were added
- **NEVER** install packages without `--require-hashes` and a verified requirements.txt
- **ALWAYS** verify new package hashes against PyPI before adding to requirements.txt

### VPS path configuration
- **VPS project path**: `/home/stv/socialtradingvlog-website/` (NOT `/var/www/`)
- **Cron setup**: `setup_cron.sh` auto-detects project path — no hardcoded paths
- **Venv**: ALL tools run from `./venv/bin/python3` (crons use venv python, not system python)
- **Web server**: Caddy (not nginx) — auto-TLS, reverse proxy to dashboard on port 8080
- **Docker**: Running on VPS (containerd + docker services active)
- **Expected ports**: 22 (SSH), 53 (DNS resolver, localhost only), 80 (HTTP→HTTPS redirect), 443 (HTTPS)

### Security architecture summary
```
┌─────────────────────────────────────────────────────────┐
│                    VPS (89.167.73.64)                     │
│                                                           │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Caddy    │  │  Dashboard   │  │  Security Stack   │  │
│  │  (HTTPS)  │→ │  (Flask)     │  │                   │  │
│  │  :80/:443 │  │  :8080       │  │  security_lib.py  │  │
│  └──────────┘  └──────────────┘  │  ├─ monitor.py     │  │
│                                   │  ├─ scanner.py     │  │
│  ┌──────────┐  ┌──────────────┐  │  ├─ selftest.py    │  │
│  │  UFW     │  │  CrowdSec    │  │  ├─ response.py    │  │
│  │ Firewall │  │  (IDS/IPS)   │  │  ├─ deps.py        │  │
│  └──────────┘  └──────────────┘  │  └─ audit.py       │  │
│                                   └───────────────────┘  │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  SSH     │  │  auditd      │  │  Encrypted       │   │
│  │  + 2FA   │  │  + AIDE      │  │  Backups (GPG)   │   │
│  └──────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                    │
         │ SSH (key+TOTP)     │ Telegram Alerts
         ▼                    ▼
    ┌──────────┐       ┌──────────────┐
    │  Tom's   │       │  Tom's Phone │
    │  Laptop  │       │  (Telegram)  │
    └──────────┘       └──────────────┘
```
