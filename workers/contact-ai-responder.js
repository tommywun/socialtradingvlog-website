/**
 * Cloudflare Worker: Contact Form AI Auto-Responder
 *
 * This worker receives form submissions directly from the contact form,
 * drafts a suggested reply using Claude API, and emails you the original
 * question + suggested reply via Resend.
 *
 * SETUP:
 * 1. Create a Cloudflare Worker at dash.cloudflare.com > Workers & Pages
 * 2. Paste this code
 * 3. Add these environment variables (Settings > Variables):
 *    - ANTHROPIC_API_KEY: Your Claude API key from console.anthropic.com
 *    - RESEND_API_KEY: Your Resend API key from resend.com (free 100 emails/day)
 *    - NOTIFY_EMAIL: Your email address to receive notifications
 *    - FROM_EMAIL: Your verified sender (e.g. contact@socialtradingvlog.com)
 *    - WEBHOOK_SECRET: A random string to verify Formspree webhooks (optional)
 * 4. Set up a custom route: contact-api.socialtradingvlog.com/*
 *    OR use the workers.dev URL
 *
 * TWO MODES:
 * A) Direct form backend: Point <form action="WORKER_URL/submit">
 * B) Formspree webhook: Configure Formspree to POST to WORKER_URL/webhook
 */

const SITE_CONTEXT = `You are an AI assistant helping Tom from SocialTradingVlog.com draft replies to contact form messages. Tom runs a website documenting his personal experience with copy trading on eToro since 2017.

Key facts about the site:
- Tom is NOT a financial adviser and cannot give investment advice
- eToro is a regulated social trading platform (FCA, CySEC, ASIC)
- Copy trading lets you automatically copy another investor's trades
- 51% of retail investor accounts lose money when trading CFDs with eToro
- Copying someone is free — the copied trader gets incentives from eToro
- Minimum copy amount is typically $200 per trader
- There are fees: spreads, withdrawal fee, currency conversion, overnight fees on leveraged positions
- Tom has an affiliate relationship with eToro
- The site has guides on: social trading, copy trading, taking profits, how much you can make, eToro fees, risk scores, choosing traders to copy

Tone: Friendly, helpful, honest, conversational. Like replying to a mate. Keep it brief. If the question is about investment advice, politely decline and point to relevant guides instead. Always include the risk disclaimer if discussing trading.`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': 'https://socialtradingvlog.com',
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    // Mode A: Direct form submission
    if (url.pathname === '/submit' && request.method === 'POST') {
      return handleDirectSubmission(request, env);
    }

    // Mode B: Formspree webhook
    if (url.pathname === '/webhook' && request.method === 'POST') {
      return handleWebhook(request, env);
    }

    return new Response('Not found', { status: 404 });
  },
};

async function handleDirectSubmission(request, env) {
  try {
    const contentType = request.headers.get('content-type') || '';
    let data;

    if (contentType.includes('application/x-www-form-urlencoded')) {
      const formData = await request.formData();
      data = {
        name: formData.get('name') || '',
        email: formData.get('email') || '',
        message: formData.get('message') || '',
        _gotcha: formData.get('_gotcha') || '',
      };
    } else {
      data = await request.json();
    }

    // Honeypot spam check
    if (data._gotcha) {
      return Response.redirect('https://socialtradingvlog.com/contact-thanks.html', 302);
    }

    // Basic validation
    if (!data.name || !data.email || !data.message) {
      return new Response('All fields are required.', { status: 400 });
    }

    // Process in background, redirect immediately
    const ctx = { waitUntil: (p) => p };
    ctx.waitUntil = request.ctx?.waitUntil || (() => {});

    // Draft AI response and send email
    await processMessage(data, env);

    return Response.redirect('https://socialtradingvlog.com/contact-thanks.html', 302);
  } catch (err) {
    console.error('Direct submission error:', err);
    return Response.redirect('https://socialtradingvlog.com/contact-thanks.html', 302);
  }
}

async function handleWebhook(request, env) {
  try {
    const payload = await request.json();

    // Formspree sends: { name, email, message, _replyto, ... }
    const data = {
      name: payload.name || payload.Name || 'Unknown',
      email: payload.email || payload.Email || payload._replyto || 'Unknown',
      message: payload.message || payload.Message || JSON.stringify(payload),
    };

    await processMessage(data, env);

    return new Response('OK', { status: 200 });
  } catch (err) {
    console.error('Webhook error:', err);
    return new Response('Error', { status: 500 });
  }
}

async function processMessage(data, env) {
  // Step 1: Draft a suggested reply using Claude
  let suggestedReply = '';
  try {
    suggestedReply = await draftReply(data, env);
  } catch (err) {
    console.error('Claude API error:', err);
    suggestedReply = '(AI draft unavailable — please write your own reply)';
  }

  // Step 2: Send notification email with original message + suggested reply
  await sendNotification(data, suggestedReply, env);
}

async function draftReply(data, env) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 500,
      system: SITE_CONTEXT,
      messages: [
        {
          role: 'user',
          content: `Draft a short, friendly reply from Tom to this contact form message.\n\nFrom: ${data.name} (${data.email})\nMessage: ${data.message}\n\nKeep it under 150 words. Be helpful but don't give financial advice. If it's a common question, point them to the relevant guide on the site.`,
        },
      ],
    }),
  });

  const result = await response.json();
  if (result.content && result.content[0]) {
    return result.content[0].text;
  }
  return '(Could not generate suggested reply)';
}

async function sendNotification(data, suggestedReply, env) {
  const emailHtml = `
    <div style="font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #00c896; margin-bottom: 4px;">New Contact Form Message</h2>
      <p style="color: #666; font-size: 14px;">From socialtradingvlog.com</p>

      <div style="background: #f5f5f5; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <p style="margin: 0 0 8px;"><strong>From:</strong> ${escapeHtml(data.name)}</p>
        <p style="margin: 0 0 8px;"><strong>Email:</strong> <a href="mailto:${escapeHtml(data.email)}">${escapeHtml(data.email)}</a></p>
        <p style="margin: 0 0 8px;"><strong>Message:</strong></p>
        <p style="margin: 0; white-space: pre-wrap;">${escapeHtml(data.message)}</p>
      </div>

      <div style="background: #e8f8f2; border-left: 4px solid #00c896; border-radius: 0 8px 8px 0; padding: 20px; margin: 20px 0;">
        <p style="margin: 0 0 8px; font-weight: 700; color: #00c896;">Suggested Reply (AI Draft)</p>
        <p style="margin: 0; white-space: pre-wrap;">${escapeHtml(suggestedReply)}</p>
      </div>

      <p style="color: #999; font-size: 12px; margin-top: 32px;">
        <a href="mailto:${escapeHtml(data.email)}?subject=Re: Your message to SocialTradingVlog&body=${encodeURIComponent(suggestedReply)}">
          Click here to reply with the suggested text
        </a>
      </p>
    </div>
  `;

  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
    },
    body: JSON.stringify({
      from: env.FROM_EMAIL || 'SocialTradingVlog <noreply@socialtradingvlog.com>',
      to: env.NOTIFY_EMAIL,
      subject: `Contact: ${data.name} — ${data.message.substring(0, 60)}`,
      html: emailHtml,
      reply_to: data.email,
    }),
  });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
