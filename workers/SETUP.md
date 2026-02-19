# Contact Form + AI Auto-Responder Setup

## Step 1: Formspree (gets the form working immediately)

1. Go to https://formspree.io and create a free account
2. Click "New Form" → give it a name like "SocialTradingVlog Contact"
3. Copy the form ID (looks like `xwpkabcd`)
4. In `contact.html`, replace `FORM_ID_HERE` with your actual form ID
5. Push to GitHub — the form now works (messages go to your email)

Free tier: 50 submissions/month. More than enough to start.

## Step 2: AI Auto-Responder (optional upgrade)

This Cloudflare Worker drafts suggested replies to contact messages using Claude.
You receive an email with the original question + a suggested reply you can send
with one click.

### What you need:
- **Anthropic API key** — https://console.anthropic.com (pay-as-you-go, ~$0.001 per message with Haiku)
- **Resend account** — https://resend.com (free 100 emails/day)
- **Cloudflare account** — you already have this

### Deploy the Worker:

1. Go to Cloudflare Dashboard → Workers & Pages → Create Worker
2. Name it `contact-ai-responder`
3. Paste the contents of `contact-ai-responder.js`
4. Go to Settings → Variables and add:
   - `ANTHROPIC_API_KEY` = your Claude API key (encrypt this)
   - `RESEND_API_KEY` = your Resend API key (encrypt this)
   - `NOTIFY_EMAIL` = your email address
   - `FROM_EMAIL` = `SocialTradingVlog <noreply@socialtradingvlog.com>`
5. Optional: Set up a custom route `contact-api.socialtradingvlog.com`

### Connect to Formspree:

Option A (recommended — keeps Formspree as form backend):
- Upgrade Formspree to Growth plan ($8/mo) for webhook support
- In Formspree, go to Form Settings → Plugins → Webhook
- Set webhook URL to: `https://contact-ai-responder.YOUR_SUBDOMAIN.workers.dev/webhook`

Option B (free — use Worker as form backend directly):
- Change the `<form action="...">` in contact.html to your Worker URL + `/submit`
- Remove Formspree entirely
- Example: `action="https://contact-ai-responder.YOUR_SUBDOMAIN.workers.dev/submit"`

### How it works:

1. Visitor submits contact form
2. Message arrives (via Formspree or directly to Worker)
3. Worker calls Claude Haiku to draft a suggested reply (~0.1 second, ~$0.001)
4. Worker sends you an email via Resend containing:
   - The original message + sender details
   - An AI-drafted suggested reply
   - A "click to reply" mailto link pre-filled with the suggested text
5. You review, edit if needed, and send

### Resend DNS setup:

To send from `@socialtradingvlog.com`, add these DNS records in Cloudflare:
- Resend will provide the exact records when you verify your domain
- Typically: 1 MX record + 2 TXT records (SPF + DKIM)

### Cost estimate:
- 10 messages/month: ~$0.01 for Claude API, $0 for Resend = essentially free
- 50 messages/month: ~$0.05 for Claude API, $0 for Resend = essentially free
