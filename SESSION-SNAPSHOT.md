# Session Snapshot -- SocialTradingVlog Command Centre & Growth

## Date
2026-02-19

## Project Overview
SocialTradingVlog website (socialtradingvlog.com) -- eToro affiliate site with YouTube channel (335 videos). Building out SEO, content, tools, and automation to drive affiliate revenue. Command Centre dashboard at tools/dashboard.py for monitoring everything. Site is hosted on Cloudflare Pages via GitHub (github.com/tommywun/socialtradingvlog-website, main branch, auto-deploys). GA property: G-PBGDJ951LL (ID 525085627).

## What's Been Built (Complete)

### Command Centre Dashboard (tools/dashboard.py)
- Full Semrush-style dashboard with tabs: Overview, Outreach, Content, Growth, Performance
- Auto-refresh every 60 seconds
- Overview tab: traffic stats from GA daily reports, activity feed, CTA click tracking
- Outreach tab: email campaign management, follow-up tracking, sent log
- Content tab: content tracker for YouTube descriptions and page status
- Growth tab: 9 strategic goals with progress tracking, recommendations, sub-tasks, notes, category filters
- Performance tab: PageSpeed Insights integration (24h cache), CTA A/B testing framework, YouTube + GSC scaffolding
- Backend: Python stdlib http.server, JSON file persistence, all API endpoints for CRUD operations

### Weekly Digest Email (tools/weekly_digest.py)
- Aggregates weekly traffic stats, outreach activity, goal progress
- Beautiful HTML email with Semrush design
- Sends via Resend API
- Supports --dry-run and --to flags
- Schedule with cron: `0 8 * * 1 cd /path && python3 tools/weekly_digest.py`

### Strategic Goals System (outreach/goals.json)
9 growth goals tracked in command centre:
1. Accelerate Content Production (in_progress, 15%) -- video pages for 335 YouTube videos
2. Build Email List & Newsletter (not_started) -- lead magnets, Resend, capture forms
3. Long-Tail Keyword Articles (not_started) -- USER SAID "let's get started" on this
4. Complete Multi-Language SEO (in_progress, 40%) -- 8 pages translated to 5 languages (ES/DE/FR/PT/AR)
5. Create Linkable Assets & Tools (not_started in goals.json, but actually IN PROGRESS) -- calculator suite being built
6. Competitor Comparison Content (not_started) -- USER SAID "go ahead, approve before live"
7. Structured Data & Rich Snippets (not_started) -- USER SAID "let's do it"
8. Build Community Presence (not_started) -- Discord server idea, needs credentials
9. Social Media Content Automation (not_started) -- video repurposing into shorts

### Translations Completed
- 76% article -> 5 languages
- eToro review -> 5 languages
- About/FAQ/Contact -> 5 languages
- Copy trading pages -> 5 languages
- Copy trading updates -> 5 languages
- Total: 180 translated pages across 5 languages (ES/DE/FR/PT/AR)
- All stored in /translations/ directory as JSON files

### eToro Fee Calculator (calculators/fee-calculator/index.html) -- COMPLETE
- Self-contained HTML/CSS/JS with Semrush light design system (35,946 bytes)
- Interactive: asset class selector, trade amount slider, holding period, account currency
- Results: total cost, 4 breakdown cards, stacked bar chart, context callout
- Includes: fee explainer section, full spread table, FAQ with schema, CTA with affiliate link
- GA tracking, schema markup (WebApplication + FAQPage)

### Copy Trading ROI Calculator (calculators/roi-calculator/index.html) -- COMPLETE
- Self-contained HTML/CSS/JS with Semrush light design system (24,981 bytes)
- Interactive: investment amount, annual return scenarios, time period, compound toggle
- Results: projected value, profit/ROI badges, SVG growth chart, year-by-year table
- Includes: copy trading explainer, Tom's real returns context card, FAQ, CTA
- GA tracking, schema markup

### YouTube Description Updates (192/335 done)
- Script: tools/youtube_descriptions.py
- 192 updated, ~142 remaining (hit daily API quota)
- Scheduled: launchd job `com.stv.youtube-update` runs at 9am to finish remaining videos
- Adds site links block, hashtags, preserves all existing disclaimers and affiliate links

### Link Building Drafts (tools/link-building-drafts.md)
- 10 Quora answer drafts for high-traffic eToro/copy trading questions
- Reddit strategy with target subreddits and template responses
- 18+ guest post targets with pitch templates
- Tom needs to manually post these

### Opportunity Scanner (tools/opportunity_scanner.py)
- Scans Reddit/StackExchange/HN for link-building opportunities
- Runs daily at 8am via launchd
- Results saved to reports/opportunities-latest.md

## What's Been Completed This Session

### Tools Suite (Goal #5) -- COMPLETE (85%)
1. **Legal disclaimers** added to fee-calculator and roi-calculator (data accuracy + liability sections)
2. **Platform Comparison Tool** BUILT at calculators/compare-platforms/index.html -- 6 platforms, toggleable, color-coded, pros/cons cards, FAQ with schema
3. **Tools Hub landing page** BUILT at calculators/index.html -- 3 tool cards, credibility section, coming soon teasers
4. **"Tools" nav link** added to 150 site pages (desktop + mobile nav)
5. **goals.json updated** -- Goal #5 at 85% (5/6 tasks done, promotion remaining)

### Structured Data (Goal #7) -- 60% COMPLETE
Schema markup added to all main pages:
- **Homepage** (index.html): WebSite + Organization schema
- **popular-investor.html**: FAQPage (5 Qs) + BreadcrumbList (upgraded from Article-only)
- **social-trading.html**: FAQPage (4 Qs) + BreadcrumbList (upgraded)
- **copy-trading.html**: FAQPage (3 Qs) + BreadcrumbList (upgraded)
- **etoro-scam.html**: FAQPage (4 Qs) + BreadcrumbList (upgraded)
- **taking-profits.html**: FAQPage (3 Qs) + BreadcrumbList (upgraded)
- **copy-trading-returns.html**: FAQPage (2 Qs) + BreadcrumbList (upgraded)
- **about.html**: Person + BreadcrumbList (new)
- **videos.html**: CollectionPage + BreadcrumbList (new)
- **updates.html**: CollectionPage + BreadcrumbList (new)
- **contact.html**: ContactPage + BreadcrumbList (new)
- Video pages already had VideoObject + FAQPage from generation
- Calculator pages already had WebApplication + FAQPage
Remaining: validate with Google Rich Results Test, monitor GSC

### Research Completed
- **Keyword research** saved to outreach/keyword-research-content-calendar.md -- 9 articles planned, 5-week schedule
- **Competitor research** saved to outreach/competitor-research-notes.md -- detailed data on Plus500, Trading 212, DEGIRO, Interactive Brokers, XTB

### Tom needs to review before push:
All changes are LOCAL only -- NOT pushed to live site. Tom asked to review demos before pushing. Preview at:
- http://localhost:9090/calculators/ (Tools Hub)
- http://localhost:9090/calculators/fee-calculator/
- http://localhost:9090/calculators/roi-calculator/
- http://localhost:9090/calculators/compare-platforms/

## What's In Progress / Pending

### IMMEDIATE (Awaiting Tom's Approval)
- **Push all changes to GitHub** (auto-deploys to Cloudflare Pages) -- Tom said "can I review demos first?" so holding off

### NEXT PRIORITY (User explicitly requested)
- **Goal #3: Long-Tail Keyword Articles** -- Research DONE (outreach/keyword-research-content-calendar.md). Ready to start writing articles. Priority 1: "eToro Minimum Deposit in 2026"
- **Goal #6: Competitor Comparisons** -- Research DONE (outreach/competitor-research-notes.md). Ready to draft articles. Tom wants to approve before publishing.
- **Goal #7: Structured Data** -- Validate schema with Google Rich Results Test

### ONGOING COMMITMENTS
- **Auto-add all ideas/tasks to Growth Strategy tab** -- User confirmed: "will you be adding all of these to the command centre as a matter of course from now on?" Answer: YES, always add new ideas/agreements to goals.json automatically.
- **CTA split testing** -- User wants constant optimization of affiliate link click-throughs. Dashboard framework exists in Performance tab. Need to implement actual A/B testing rotation.
- **Analyse visitor flow** -- User wants ongoing analysis of how visitors move through the site, suggestions for CTA placement optimization.

### FUTURE (Discussed but not started)
- Goal #2: Email list with lead magnets
- Goal #8: Discord community (needs credentials from Tom)
- Goal #9: Video repurposing into shorts (Tom excited about this -- "I'd love a way to repurpose parts of my videos into shorts")
- VPS setup (Hetzner recommended, EUR 3.79/mo) for 24/7 agent operations
- YouTube description auto-updating via launchd (already running, 192/335 done)
- Language chooser UI component for site navigation
- Contact form needs real Formspree form ID (currently has placeholder FORM_ID_HERE)

## Key Design Decisions
- **Calculator tools use Semrush LIGHT theme** (not the dark site theme) -- Plus Jakarta Sans + Inter fonts, #F4F5F9 background, colorful cards
- **Each tool page is self-contained** -- inline CSS + JS, no external dependencies beyond Google Fonts
- **Affiliate links use etoro.tw/ format** with rel="noopener sponsored" (Tom's affiliate link: https://etoro.tw/4tEsDF4)
- **Risk disclaimers required on every tool page** -- eToro standard disclaimer: "51% of retail investor accounts lose money when trading CFDs with eToro"
- **All pages have GA tracking** (G-PBGDJ951LL) with CTA click events
- **Schema markup** on all calculator pages (WebApplication + FAQPage)
- **YouTube descriptions**: NEVER remove legally required eToro disclaimers or affiliate links
- **Tom is NOT a financial adviser** -- never give investment advice in content

## Key File Locations
```
/Users/thomaswest/socialtradingvlog-website/
├── tools/
│   ├── dashboard.py              # Command Centre (single-file, ~2200 lines)
│   ├── weekly_digest.py          # Weekly email script
│   ├── ga_report.py              # GA stats on demand
│   ├── youtube_descriptions.py   # YouTube description updater
│   ├── opportunity_scanner.py    # Reddit/SE/HN scanner
│   ├── email_outreach.py         # Email outreach management
│   ├── run_pipeline.py           # Transcription + translation pipeline
│   ├── generate_article_pages.py
│   ├── generate_video_pages.py
│   ├── generate_translated_pages.py
│   ├── generate_translated_updates_faq_contact.py
│   ├── link-building-drafts.md   # Quora/Reddit/guest post drafts
│   └── translations/             # Translation JSON files
├── calculators/
│   ├── fee-calculator/
│   │   └── index.html            # COMPLETE (35,946 bytes)
│   ├── roi-calculator/
│   │   └── index.html            # COMPLETE (24,981 bytes)
│   ├── compare-platforms/
│   │   └── (EMPTY)               # NOT YET BUILT
│   └── (no index.html)           # HUB PAGE NOT YET BUILT
├── outreach/
│   ├── goals.json                # 9 strategic goals
│   ├── sent.json                 # Outreach email log
│   ├── content-tracker.json      # Content status tracking
│   └── ...
├── translations/                 # All translation JSON files
├── reports/                      # Daily GA reports, pagespeed cache
│   ├── latest.txt                # Most recent GA report
│   └── opportunities-latest.md   # Latest opportunity scan
├── workers/
│   ├── contact-ai-responder.js   # Cloudflare Worker for auto-replies
│   └── SETUP.md                  # Worker setup instructions
├── CLAUDE.md                     # Comprehensive project notes (READ THIS FIRST)
└── .claude/plans/
    └── shimmying-foraging-chipmunk.md  # Current plan: tools suite spec
```

## Secrets Location
All API keys and credentials are stored in `~/.config/stv-secrets/` (NOT in the repo):
- `ga-service-account.json` -- Google Analytics API access
- `openai-api-key.txt` -- OpenAI Whisper API key
- `youtube-oauth.json` -- YouTube Data API OAuth credentials
- `youtube-token.pickle` -- YouTube OAuth token
- `resend-api-key.txt` -- Resend API key (tom@socialtradingvlog.com)
- `gmail-oauth.json` -- Gmail API OAuth credentials
- `gmail-token.pickle` -- Gmail OAuth token

## Plan File
The detailed tool suite plan is at: `/Users/thomaswest/.claude/plans/shimmying-foraging-chipmunk.md`
It contains full specs for all 4 calculator tools including:
- Design system tokens (colors, typography, shadows)
- Fee data structure for the fee calculator
- Detailed input/output specs for each tool
- Comparison tool platform data requirements
- Hub page layout spec
- File structure and nav design
- Verification checklist

## Goals.json Status vs Reality
NOTE: goals.json currently shows Goal #5 as `"status": "not_started"` and `"progress": 0` with all tasks marked `"done": false`. This is OUT OF DATE. In reality:
- Fee calculator: DONE (built and complete)
- ROI calculator: DONE (built and complete)
- Compare platforms: NOT DONE (empty directory exists)
- Hub page: NOT DONE
- goals.json needs to be updated to reflect the completed calculators

## User Preferences
- Tom wants things to look "magazine-like, colorful, easy to read for beginners, beautiful graphical elements"
- Friendly, accessible, professional and slick design
- Always add disclaimers for legal protection
- Auto-add all new ideas to command centre goals (ALWAYS)
- Approve competitor comparison articles before they go live
- Keep everything white-hat SEO, no spam
- Drive affiliate click-throughs through good UX, not manipulation
- Tom's email: tradertommalta@gmail.com
- Tom's Google Cloud project: vocal-affinity-487722-n4

## Session Start Checklist (from CLAUDE.md)
At the start of each session:
1. Check the latest GA report: `cat reports/latest.txt`
2. Check the latest opportunity digest: `cat reports/opportunities-latest.md` -- remind Tom of the top 3-5 best opportunities
3. Check pipeline progress: `tail -20 transcriptions/pipeline.log`
4. Share key insights and any notable changes with Tom
5. Review this snapshot and CLAUDE.md

## Resume Instructions
When resuming, start by:
1. Read this snapshot file (SESSION-SNAPSHOT.md)
2. Read CLAUDE.md for full project context
3. Read the plan file at `~/.claude/plans/shimmying-foraging-chipmunk.md` for tool suite specs
4. Continue with this priority order:
   a. Add stronger legal disclaimers to existing fee-calculator and roi-calculator
   b. Build compare-platforms tool (calculators/compare-platforms/index.html)
   c. Build hub page (calculators/index.html)
   d. Add "Tools" nav links across site pages
   e. Update goals.json to reflect completed work on Goal #5
   f. Then move to Goal #3 (long-tail keyword articles)
   g. Then Goal #6 (competitor comparisons -- get Tom's approval before publishing)
   h. Then Goal #7 (structured data markup across all pages)
