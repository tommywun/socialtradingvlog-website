# Platform Finder Tool — Design Specification

## Overview
An interactive, personalised tool that guides beginners to the best trading platform for their situation. Three design variations for split testing, plus shared architecture.

---

## Shared Architecture (all variations use this)

### Data Structure: `platform-data.json`

Each platform has this structure (extends the existing compare-platforms PLATFORMS array):

```javascript
const PLATFORMS = {
  etoro: {
    // Identity
    id: 'etoro',
    name: 'eToro',
    color: '#00C853',
    logo: 'etoro-logo.svg',
    since: 2007,
    tagline: 'Social trading pioneer with 35M+ users',

    // Availability (ISO country codes)
    available_in: ['GB', 'DE', 'FR', 'ES', 'IT', 'NL', 'PL', 'PT', 'AU', 'AE', ...],
    not_available_in: ['US_full', 'JP', 'KR', 'TR', 'IN', 'ID'],
    languages: ['en', 'de', 'fr', 'es', 'it', 'nl', 'pl', 'pt', 'ar'],

    // Fees (scraped weekly, with last_updated timestamp)
    fees: {
      stock_commission: 0,
      stock_spread_pct: 0.15,
      crypto_spread_pct: 1.0,
      forex_spread_pips: 1.0,
      etf_commission: 0,
      overnight_daily_pct: 0.01,
      withdrawal_fee: { USD: 5, GBP: 0, EUR: 0 },
      inactivity_fee: { amount: 10, currency: 'USD', after_months: 12 },
      conversion_fee_pct: 0.5,
      deposit_fee: 0,
      minimum_deposit: { USD: 50, GBP: 50, EUR: 50 },
    },

    // Features (boolean or descriptive)
    features: {
      copy_trading: true,
      demo_account: true,
      real_stocks: true,       // vs CFD-only
      fractional_shares: true,
      social_feed: true,
      isa_available: false,    // UK ISA
      pea_available: false,    // France PEA
      islamic_account: true,   // Swap-free
      auto_invest: false,
      robo_advisor: false,
    },

    // Asset coverage
    assets: {
      stocks: 3000,
      etfs: 300,
      crypto: 80,
      forex_pairs: 49,
      commodities: 30,
      indices: 20,
    },

    // Ratings
    ratings: {
      trustpilot: 4.2,
      app_store_ios: 4.4,
      app_store_android: 4.0,
      our_rating: null,  // Tom's personal rating (1-5, added later)
    },

    // Regulation
    regulation: ['FCA', 'CySEC', 'ASIC'],
    investor_protection: { GB: 85000, EU: 20000, AU: 0 },

    // Platform quality
    account_opening_days: 1,
    withdrawal_speed_days: 2,
    customer_support: ['live_chat', 'email', 'phone'],
    support_languages: ['en', 'de', 'fr', 'es', 'it', 'ar'],
    education_quality: 'good',  // 'excellent', 'good', 'basic', 'none'
    mobile_app_quality: 'good',

    // Affiliate
    is_affiliate: true,
    affiliate_link: 'https://etoro.tw/4tEsDF4',
    special_offer: null,  // or { text: '...', expires: '2026-06-01' }

    // Hidden fees / warnings
    hidden_fees: [
      'Currency conversion fee (0.5%) on every non-USD trade',
      'Crypto spreads are higher than dedicated exchanges',
    ],

    // Tom's take (personal, in his voice)
    toms_take: "I've used eToro for nearly 10 years. The copy trading is genuinely unique — nothing else comes close. The spreads aren't the lowest, but for beginners who want to copy experienced traders, this is the one.",

    // Best for tags
    best_for: ['copy_trading', 'beginners', 'social_trading'],
  },
  // ... more platforms
};
```

### Recommendation Algorithm

```javascript
function recommendPlatforms(userProfile, availablePlatforms) {
  // userProfile = { country, budget, interests, experience, priorities, wantsCopyTrading }

  // Step 1: Filter by country availability
  let candidates = availablePlatforms.filter(p =>
    p.available_in.includes(userProfile.country)
  );

  // Step 2: Score each platform (0-100)
  candidates = candidates.map(platform => {
    let score = 0;
    let reasons = [];

    // Fee score (30 points max)
    // Lower fees = higher score, weighted by user's interests
    const feeScore = calculateFeeScore(platform, userProfile);
    score += feeScore * 0.30;

    // Feature match (25 points max)
    // Does it have what they want? Copy trading, demo, real stocks, etc.
    const featureScore = calculateFeatureScore(platform, userProfile);
    score += featureScore * 0.25;

    // Asset coverage (15 points max)
    // Does it cover their interests?
    const assetScore = calculateAssetScore(platform, userProfile);
    score += assetScore * 0.15;

    // Ratings & trust (15 points max)
    const trustScore = (
      (platform.ratings.trustpilot / 5) * 50 +
      (platform.ratings.app_store_ios / 5) * 30 +
      (platform.regulation.length / 3) * 20
    );
    score += (trustScore / 100) * 0.15;

    // Beginner-friendliness (15 points max)
    // Weighted higher if user is a beginner
    const beginnerScore = calculateBeginnerScore(platform, userProfile);
    score += beginnerScore * 0.15;

    // Collect human-readable reasons
    if (featureScore > 80) reasons.push('Great feature match for your needs');
    if (feeScore > 80) reasons.push('Among the lowest fees for what you want to trade');
    if (platform.features.copy_trading && userProfile.wantsCopyTrading)
      reasons.push('Has the copy trading feature you want');
    if (platform.features.demo_account)
      reasons.push('Free demo account to practice first');

    return { platform, score: Math.round(score), reasons };
  });

  // Step 3: Sort by score, return top 3
  candidates.sort((a, b) => b.score - a.score);
  return candidates.slice(0, 3);
}
```

### Trade Cost Simulator

Built into the results — shows exact cost for the user's specific scenario:

```javascript
function simulateTradeCost(platform, asset, amount, holdingDays, currency) {
  const fees = platform.fees;
  const spreadCost = amount * (fees[`${asset}_spread_pct`] || fees.stock_spread_pct) / 100;
  const commission = fees[`${asset}_commission`] || fees.stock_commission || 0;
  const overnightCost = holdingDays > 0
    ? amount * (fees.overnight_daily_pct / 100) * holdingDays
    : 0;
  const conversionCost = currency !== 'USD'
    ? amount * (fees.conversion_fee_pct / 100)
    : 0;
  const withdrawalFee = fees.withdrawal_fee[currency] || 0;

  return {
    spread: spreadCost,
    commission,
    overnight: overnightCost,
    conversion: conversionCost,
    withdrawal: withdrawalFee,
    total: spreadCost + commission + overnightCost + conversionCost + withdrawalFee,
    totalPct: ((spreadCost + commission + overnightCost + conversionCost + withdrawalFee) / amount * 100),
  };
}
```

### Country Detection

```javascript
async function detectCountry() {
  // Use free IP geolocation API
  try {
    const res = await fetch('https://ipapi.co/json/');
    const data = await res.json();
    return { code: data.country_code, name: data.country_name };
  } catch {
    return null; // fallback to manual selection
  }
}
```

---

## Design Variation A: "The Wizard"

**Inspiration:** Helix Sleep quiz + NerdWallet credit card quiz
**Philosophy:** Full-screen, immersive, one question at a time. Feels like talking to a friend, not filling in a form. Minimal, distraction-free. Best for complete beginners.

### Visual Style
- Full viewport height per step — no header, no footer, no nav during the quiz
- Large, centred question text
- Tappable card-style answer options with icons
- Progress bar at top (thin, colour-coded)
- Smooth slide transition between steps
- Dark option (matches site) or light option (feels more approachable)
- Tom's avatar/photo in the corner as a "guide" presence

### User Flow

**Screen 0: Landing / Entry**
```
[Background: subtle gradient or abstract pattern]

                    Find Your Perfect
                    Trading Platform

    Answer 5 quick questions and I'll match you
    with the platform that suits you best.

    Based on real fee data, updated weekly.

              [ Start — takes 60 seconds ]

    "I've been trading since 2016. Let me help you
     skip the mistakes I made." — Tom

    [Small text: We may earn a commission if you
     sign up through our links. Our recommendations
     are based on real data.]
```

**Screen 1: Country (auto-detected)**
```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Step 1 of 5

    Where are you based?

    We detected: [🇬🇧 United Kingdom]

              [ Yes, that's right ]
              [ No, change country ▾ ]

    We ask because different platforms are
    available in different countries.
```

**Screen 2: Experience**
```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Step 2 of 5

    Have you invested or traded before?

    ┌─────────────────────────────────┐
    │  🌱  Complete beginner           │
    │  Never done any trading          │
    └─────────────────────────────────┘

    ┌─────────────────────────────────┐
    │  📈  I've tried a bit            │
    │  Used an app or demo account     │
    └─────────────────────────────────┘

    ┌─────────────────────────────────┐
    │  🎯  I know what I'm doing       │
    │  Regular trader/investor         │
    └─────────────────────────────────┘
```

**Screen 3: Interests**
```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Step 3 of 5

    What are you interested in?
    Pick as many as you like.

    [ 📊 Stocks ]  [ ₿ Crypto ]  [ 📈 ETFs ]
    [ 💱 Forex ]   [ 🥇 Gold/Commodities ]
    [ 👥 Copy Trading ]

    [ I'm not sure yet ]

    ─────────────────────────────
    [i] What's copy trading?
        "Instead of picking your own trades,
         you copy an experienced trader and
         your account mirrors theirs
         automatically. It's how I started."
         [Watch my 2-min explainer →]
```

**Screen 4: Budget**
```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Step 4 of 5

    How much are you thinking of starting with?

    There's no wrong answer — some platforms
    let you start with as little as £10.

    [ Under £100 ]
    [ £100 – £500 ]
    [ £500 – £2,000 ]
    [ £2,000 – £10,000 ]
    [ £10,000+ ]

    ─────────────────────────────
    ⚠️ "Only put in what you can afford to lose
        — seriously, it's exciting and an amazing
        opportunity, but the risk is real.
        Watch my vid to see more about this →"
```

**Screen 5: Priority**
```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Step 5 of 5

    What matters most to you?
    Pick your top 2.

    [ 💰 Lowest fees ]
    [ 📱 Best app / easiest to use ]
    [ 👥 Copy trading ]
    [ 🛡️ Safety & regulation ]
    [ 📚 Good for learning ]
    [ 🌍 Widest range of things to trade ]

              [ Show my results → ]
```

**Results Screen**
```
    Your Top 3 Matches

    ┌─ #1 BEST MATCH ─────────── 94% match ──┐
    │                                          │
    │  [eToro logo]  eToro                     │
    │  ★★★★☆ 4.2 Trustpilot · Since 2007      │
    │                                          │
    │  Why it's your best match:               │
    │  ✓ Best copy trading platform available  │
    │  ✓ Free demo account to practice first   │
    │  ✓ 3,000+ stocks, zero commission        │
    │                                          │
    │  What a £500 trade in Apple would cost:  │
    │  ┌──────────────────────────────────┐    │
    │  │ Spread: £0.75                    │    │
    │  │ Overnight (30 days): £1.50       │    │
    │  │ Currency conversion: £2.50       │    │
    │  │ Total: £4.75 (0.95%)            │    │
    │  └──────────────────────────────────┘    │
    │                                          │
    │  ⚠️ Watch out for:                       │
    │  · Currency conversion fee on every trade│
    │  · Crypto spreads higher than Binance    │
    │                                          │
    │  Tom's take: "I've used eToro for nearly │
    │  10 years. The copy trading is genuinely │
    │  unique — nothing else comes close."     │
    │                                          │
    │  🛡️ Regulated by FCA (UK)                │
    │  💰 Your money protected up to £85,000   │
    │                                          │
    │  [ Open Free Account → ]                 │
    │  [ Try Demo First → ]                    │
    │                                          │
    │  76% of retail CFD accounts lose money   │
    │  when trading with this provider.        │
    └──────────────────────────────────────────┘

    ┌─ #2 ───────────────────── 87% match ──┐
    │  [Trading 212 logo]  Trading 212       │
    │  ★★★★★ 4.6 Trustpilot                 │
    │  ...                                   │
    └────────────────────────────────────────┘

    ┌─ #3 ───────────────────── 82% match ──┐
    │  [XTB logo]  XTB                       │
    │  ★★★★☆ 3.8 Trustpilot                 │
    │  ...                                   │
    └────────────────────────────────────────┘

    ─────────────────────────────────────────
    Want to dig deeper?
    [ Compare all platforms side by side → ]
    [ How fees really work — my guide → ]
    [ What is copy trading? Watch → ]

    ─────────────────────────────────────────
    Transparency: We earn a commission if you
    sign up through our links. But every number
    on this page is real, scraped from the
    platforms themselves. Last updated: 18 Feb 2026.
```

### Technical Notes — Variation A
- Single HTML file with CSS transitions between steps
- Steps are `<section>` elements, one visible at a time via `transform: translateX()`
- Progress bar width updates with each step (20%, 40%, 60%, 80%, 100%)
- Results page scrolls normally (not a single-viewport step)
- Country detected on load, pre-filled in step 1
- All calculation runs client-side when "Show results" is clicked
- No page reloads — pure SPA within one HTML file

---

## Design Variation B: "The Dashboard"

**Inspiration:** BrokerChooser real-time updating + comparison tool pattern
**Philosophy:** Everything visible at once. Configure on the left, see results update live on the right. More like a power tool than a guided quiz. Good for users who already know roughly what they want.

### Visual Style
- Split layout: left panel (inputs, 40%) + right panel (results, 60%)
- Results update in real-time as inputs change (no "submit" button)
- Sticky left panel, scrollable right panel
- Compact, information-dense
- Uses existing calculator design language (pill buttons, sliders)

### Layout
```
┌─────────────────────┬──────────────────────────────────┐
│                     │                                  │
│  FIND YOUR PLATFORM │  YOUR TOP MATCHES                │
│                     │                                  │
│  📍 United Kingdom  │  ┌── #1 ── 94% match ────────┐  │
│     [change]        │  │ eToro                      │  │
│                     │  │ ★★★★☆ · £4.75 per £500    │  │
│  Experience:        │  │ [View details] [Open →]    │  │
│  ○ Beginner         │  └────────────────────────────┘  │
│  ● Some experience  │                                  │
│  ○ Experienced      │  ┌── #2 ── 87% match ────────┐  │
│                     │  │ Trading 212                │  │
│  Interested in:     │  │ ★★★★★ · £2.10 per £500    │  │
│  [✓ Stocks]         │  │ [View details] [Open →]    │  │
│  [  Crypto ]        │  └────────────────────────────┘  │
│  [✓ ETFs   ]        │                                  │
│  [  Forex  ]        │  ┌── #3 ── 82% match ────────┐  │
│  [✓ Copy   ]        │  │ XTB                        │  │
│                     │  │ ★★★★☆ · £1.80 per £500    │  │
│  Budget:            │  │ [View details] [Open →]    │  │
│  ====●======        │  └────────────────────────────┘  │
│  £500               │                                  │
│                     │  ── Compare All ──────────────   │
│  Priority:          │  [Full comparison table]         │
│  [● Lowest fees  ]  │                                  │
│  [  Best app     ]  │  ── Fee Breakdown ────────────   │
│  [  Copy trading ]  │  [Side-by-side cost chart]       │
│  [  Safety       ]  │                                  │
│                     │                                  │
│  ⚠️ Only invest     │                                  │
│  what you can       │                                  │
│  afford to lose.    │                                  │
│  Seriously. →       │                                  │
│                     │                                  │
└─────────────────────┴──────────────────────────────────┘
```

### Expanded Result Card
When user clicks "View details", the card expands:
```
┌── #1 ── 94% match ──────────────────────────┐
│                                              │
│  [eToro logo]  eToro                         │
│  ★★★★☆ 4.2/5 Trustpilot (29K reviews)       │
│  📱 iOS: 4.4/5 · Android: 4.0/5             │
│                                              │
│  Why it matches you:                         │
│  ✓ Only platform with proper copy trading    │
│  ✓ Zero commission on stocks                 │
│  ✓ Free demo account                         │
│                                              │
│  ── Your Trade Costs ────────────────────    │
│  £500 in Apple stock, held 30 days:          │
│  Spread     ████░░░░  £0.75                  │
│  Overnight  ██░░░░░░  £1.50                  │
│  FX fee     ███░░░░░  £2.50                  │
│  Total      ████░░░░  £4.75 (0.95%)          │
│                                              │
│  ── Hidden Fees ─────────────────────────    │
│  ⚠️ 0.5% currency conversion on every trade  │
│  ⚠️ $10/month inactivity fee after 12 months │
│  ⚠️ Crypto spreads 1% (higher than Binance)  │
│                                              │
│  ── Tom's Take ──────────────────────────    │
│  "I've used eToro for nearly 10 years..."    │
│  [Watch my full review →]                    │
│                                              │
│  ── Safety ──────────────────────────────    │
│  🛡️ FCA regulated (UK)                       │
│  💰 Protected up to £85,000 (FSCS)           │
│  📋 Account opening: ~1 day                  │
│  💸 Withdrawal: 1-2 business days            │
│                                              │
│  [ Open Free Account → ]                     │
│  [ Try Demo Account → ]                      │
│                                              │
│  76% of retail CFD accounts lose money       │
│  when trading with this provider.            │
└──────────────────────────────────────────────┘
```

### Technical Notes — Variation B
- Uses existing calculator layout patterns (pill buttons, sliders, breakdown cards)
- Left panel is `position: sticky; top: 0`
- Results re-render on every input change (debounced 200ms)
- On mobile (< 768px): stacks vertically — inputs on top, results below
- "View details" uses accordion expand/collapse (existing goal card pattern)

---

## Design Variation C: "The Conversation"

**Inspiration:** Chat UIs + personal voice
**Philosophy:** Feels like texting with Tom. The most personal, warmest approach. Questions appear as chat bubbles from Tom, answers are tappable options. Results feel like a personal recommendation from a friend.

### Visual Style
- Chat-style interface with message bubbles
- Tom's photo/avatar on left of his messages
- User responses on right in a different colour
- Tappable option buttons below each question
- Typing indicator ("Tom is typing...") between questions
- Scrolling conversation flow
- Background: subtle, clean (not a real messaging app)

### Conversation Flow

```
┌──────────────────────────────────────────┐
│                                          │
│  Find Your Trading Platform              │
│  A personal recommendation from Tom      │
│                                          │
│  ┌─────────────────────────────────┐     │
│  │ 👤 Hey! I'm Tom. I've been     │     │
│  │    trading since 2016 and I've  │     │
│  │    tried pretty much every      │     │
│  │    platform out there.          │     │
│  │                                 │     │
│  │    Let me help you find the     │     │
│  │    right one. Just answer a     │     │
│  │    few quick questions.         │     │
│  └─────────────────────────────────┘     │
│                                          │
│  ┌─────────────────────────────────┐     │
│  │ 👤 First — where are you        │     │
│  │    based? I'm asking because    │     │
│  │    different platforms are       │     │
│  │    available in different        │     │
│  │    countries.                    │     │
│  └─────────────────────────────────┘     │
│                                          │
│  It looks like you're in the UK.         │
│                                          │
│  [ 🇬🇧 Yes, I'm in the UK ]             │
│  [ 🌍 No, somewhere else ]               │
│                                          │
│                                          │
│  ┌─────────────────────────────────┐     │
│  │ 👤 Great! Have you done any     │     │
│  │    trading or investing before? │     │
│  │    No judgement — we all start  │     │
│  │    somewhere. I had no clue     │     │
│  │    when I started!              │     │
│  └─────────────────────────────────┘     │
│                                          │
│  [ 🌱 Nope, total beginner ]             │
│  [ 📈 A little bit ]                     │
│  [ 🎯 Yeah, I know my way around ]       │
│                                          │
│  ... continues with budget, interests,   │
│      priorities ...                      │
│                                          │
│  ┌─────────────────────────────────┐     │
│  │ 👤 OK here's what I'd          │     │
│  │    recommend for you...         │     │
│  │                                 │     │
│  │    Based on what you've told    │     │
│  │    me, your best bet is eToro.  │     │
│  │    Here's why:                  │     │
│  └─────────────────────────────────┘     │
│                                          │
│  [Full results card appears here]        │
│                                          │
│  ┌─────────────────────────────────┐     │
│  │ 👤 One more thing — only put    │     │
│  │    in what you can afford to    │     │
│  │    lose. Seriously. It's        │     │
│  │    exciting and an amazing      │     │
│  │    opportunity, but the risk    │     │
│  │    is real. I've lost money     │     │
│  │    too. Here's my video about   │     │
│  │    it → [watch]                 │     │
│  └─────────────────────────────────┘     │
│                                          │
└──────────────────────────────────────────┘
```

### Technical Notes — Variation C
- Messages rendered as `<div>` elements with chat bubble CSS
- "Typing" delay (800ms) before each new message appears for natural pacing
- User taps option → it appears as their "sent" message on the right
- Next question slides in after a brief delay
- Results section breaks out of chat style into full-width cards
- On mobile: feels especially natural (chat is a mobile-native pattern)

---

## A/B Testing Implementation

### Approach: Server-Side Split via Nginx

On VPS, use Nginx `split_clients` to route traffic:

```nginx
# In nginx.conf
split_clients "${remote_addr}" $variant {
    34%   "A";
    33%   "B";
    33%   "C";
}

server {
    # ... existing config ...

    # Platform finder tool
    location /find-your-platform/ {
        # Set cookie for consistent experience
        add_header Set-Cookie "ab_variant=$variant; Path=/; Max-Age=2592000" always;

        # If returning visitor, use their existing cookie
        if ($cookie_ab_variant) {
            set $variant $cookie_ab_variant;
        }

        # Serve the right variant
        try_files /find-your-platform/variant-$variant.html =404;
    }
}
```

### Tracking

Each variant includes a small tracking snippet:

```javascript
// Track which variant, plus key events
const variant = document.body.dataset.variant; // 'A', 'B', or 'C'

function trackEvent(action, label) {
  // Google Analytics
  gtag('event', action, {
    event_category: 'platform_finder',
    event_label: label,
    custom_map: { dimension1: variant }
  });
}

// Key events to track:
// - 'quiz_start' — user begins
// - 'step_complete' — each step completed (with step number)
// - 'quiz_complete' — reached results
// - 'quiz_abandon' — left before results (with last step)
// - 'result_click' — clicked a platform result
// - 'affiliate_click' — clicked "Open Account"
// - 'demo_click' — clicked "Try Demo"
// - 'compare_click' — clicked "Compare All"
// - 'video_click' — clicked any video link
```

### Metrics to Compare

| Metric | What It Tells Us |
|---|---|
| Completion rate | Which variant keeps people engaged through all steps |
| Time to complete | Which feels quickest (not always best — too fast may mean skipping) |
| Affiliate click rate | Which converts best |
| Demo click rate | Which builds trust (demo = "I want to try before committing") |
| Bounce rate at each step | Where each variant loses people |
| Return visits | Which variant users come back to |

### Minimum Sample Size
Need ~1,000 visitors per variant (3,000 total) for statistical significance at 95% confidence with a 5% minimum detectable effect. At current traffic levels, this determines how long to run the test.

---

## Content: Explainer Videos Needed

These are short (30-90 second) videos to embed at key points:

| Topic | Where It Appears | Length | Script Notes |
|---|---|---|---|
| "What is copy trading?" | Step 3 (interests) | 60 sec | Tom explaining how it works, showing his screen |
| "Only invest what you can afford to lose" | Step 4 (budget) | 90 sec | Personal story about a loss, why it matters |
| "What is a spread?" | Results (fee breakdown) | 45 sec | Simple visual: buy price vs sell price |
| "What are overnight fees?" | Results (fee breakdown) | 45 sec | Why holding costs money, with real numbers |
| "What is leverage and why it's dangerous" | Results (if CFDs mentioned) | 60 sec | The amplifier analogy, real loss example |
| "Demo accounts — try before you risk" | Results (demo CTA) | 30 sec | Quick encouragement to practice first |

These don't need to exist before launch — the tool works without them. But they massively increase trust and engagement. Placeholder: text-only explainers that get upgraded to video embeds as videos are produced.

---

## File Structure

```
/find-your-platform/
  index.html          (redirects to correct variant via JS or served by Nginx)
  variant-A.html      (The Wizard)
  variant-B.html      (The Dashboard)
  variant-C.html      (The Conversation)
  platform-data.js    (shared platform data, loaded by all variants)
  recommendation.js   (shared algorithm, loaded by all variants)
  tracking.js         (shared analytics, loaded by all variants)
```

Or for the translated versions:
```
/de/plattform-finden/
  variant-A.html
  variant-B.html
  variant-C.html
  platform-data-de.js  (German platform set — includes Trade Republic, etc.)
```

---

## Implementation Priority

### Phase 1: Build the engine (shared code)
1. Platform data JSON with all platforms per market
2. Recommendation algorithm
3. Trade cost simulator
4. Country detection

### Phase 2: Build Variation A first (The Wizard)
- Most beginner-friendly, likely highest completion rate
- Matches the Helix Sleep research (best-in-class UX)
- Works well on mobile (most traffic)

### Phase 3: Build Variation B (The Dashboard)
- Reuses existing calculator patterns (faster to build)
- Appeals to slightly more experienced users
- Good desktop experience

### Phase 4: Build Variation C (The Conversation)
- Most unique/differentiated approach
- Strongest "Tom's voice" presence
- Potentially highest trust factor

### Phase 5: Set up A/B testing
- Configure Nginx split
- Add tracking
- Run for 2-4 weeks
- Analyse and pick winner (or combine best elements)

---

## Questions for Tom

1. Should the tool live at `/find-your-platform/` or replace the homepage entirely?
2. Tom's photo/avatar — do we have one to use in Variation C?
3. Personal ratings — do you want to add your own 1-5 rating for each platform?
4. Special offers — should we approach affiliate partners about exclusive deals before or after building?
5. Which variation feels most "you"?
