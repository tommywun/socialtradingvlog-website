#!/usr/bin/env python3
"""
Generate SEO-optimised video landing pages for each transcribed video.

VIDEO PAGES PIPELINE (Feb 2025):
  Pages are no longer generated from raw transcripts. Each video page must be
  a proper SEO-rewritten article based on the video's key points, targeting a
  specific keyphrase. Tom must approve each article before it goes live.

  To publish a video page, set "approved": True in its KEYWORD_MAP entry and
  provide article_sections with the rewritten content.

Creates /video/SLUG/index.html with:
  - Intro paragraph (keyphrase before the embed)
  - YouTube thumbnail as featured image
  - Embedded YouTube video
  - Table of contents
  - Properly written article content (NOT a raw transcript dump)
  - FAQ section with FAQPage schema (rich snippets)
  - Breadcrumb + VideoObject schema
  - Auto-linked key terms
  - Sidebar CTA + related guides
  - Full site nav + footer

Usage:
    python3 tools/generate_video_pages.py              # generate all approved
    python3 tools/generate_video_pages.py --video-id YZYgjitj7DM
    python3 tools/generate_video_pages.py --force      # regenerate even if exists
"""

import sys
import os
import re
import html
import json
import pathlib
import argparse

BASE_DIR = pathlib.Path(__file__).parent.parent
TRANS_DIR = BASE_DIR / "transcriptions"
VIDEO_DIR = BASE_DIR / "video"

# ── Internal link targets (applied once per page in transcript) ───────────────
# Pattern → relative URL from /video/SLUG/
INTERNAL_LINKS = [
    (r'\bcopy trading\b',               '../../copy-trading.html'),
    (r'\bsocial trading\b',             '../../social-trading.html'),
    (r'\bpopular investor\b',           '../../popular-investor.html'),
    (r'\bspread fee[s]?\b',             '../../video/etoro-spread-fees-explained/'),
    (r'\bovernight fee[s]?\b',          '../../video/etoro-rollover-overnight-fees/'),
    (r'\brollover fee[s]?\b',           '../../video/etoro-rollover-overnight-fees/'),
    (r'\bwithdrawal fee[s]?\b',         '../../video/etoro-withdrawal-fees/'),
    (r'\bnegative balance protection\b','../../video/etoro-negative-balance-protection-most-you-can-lose/'),
    (r'\bcopy open trades\b',           '../../video/should-i-copy-open-trades-etoro/'),
    (r'\bstop loss\b',                  '../../video/etoro-copy-trading-stop-loss-risk/'),
    (r'\btake profit\b',                '../../video/etoro-take-profit-can-i-change-it/'),
    (r'\bdrawdown[s]?\b',               '../../video/etoro-drawdowns-copy-trading-risk/'),
    (r'\bleverage trading\b',           '../../video/etoro-leverage-trading-beginners/'),
    (r'\bvirtual.{0,10}account\b',      '../../video/etoro-virtual-practice-account/'),
]

# ── CTA presets ───────────────────────────────────────────────────────────────
# Each preset: url, label (button text), headline (sidebar h3), body (sidebar p)
CTA_PRESETS = {
    "main": {
        "url":      "https://etoro.tw/4cuYCBg",
        "label":    "Explore eToro",
        "headline": "Ready to try eToro?",
        "body":     "Tom's been on eToro since 2017. Here's his affiliate link.",
    },
    "copy": {
        "url":      "https://etoro.tw/46TVRpv",
        "label":    "Explore Smart Portfolios",
        "headline": "eToro Smart Portfolios",
        "body":     "Diversified, ready-made portfolios — a step up from copying a single trader.",
    },
    "stocks": {
        "url":      "https://etoro.tw/40cMvkX",
        "label":    "Trade Stocks on eToro",
        "headline": "Buy Real Stocks on eToro",
        "body":     "Commission-free real shares — own the underlying asset, not just a contract.",
    },
    "crypto": {
        "url":      "https://etoro.tw/46G4iVo",
        "label":    "Explore Crypto on eToro",
        "headline": "Trade Crypto on eToro",
        "body":     "Buy and hold crypto on a regulated, multi-asset platform.",
    },
    "etf": {
        "url":      "https://etoro.tw/4tJQR0I",
        "label":    "Explore ETFs on eToro",
        "headline": "Invest in ETFs on eToro",
        "body":     "Low-cost, diversified ETFs — invest in the whole market, not just one stock.",
    },
    "indices": {
        "url":      "https://etoro.tw/4kE9pLJ",
        "label":    "Trade Indices on eToro",
        "headline": "Trade Indices on eToro",
        "body":     "The S&P 500, NASDAQ, FTSE 100 and more — trade the world's major indices.",
    },
    "commodities": {
        "url":      "https://etoro.tw/4tDGoDJ",
        "label":    "Trade Commodities on eToro",
        "headline": "Trade Commodities on eToro",
        "body":     "Gold, oil, silver — trade commodities on a regulated platform.",
    },
    "currencies": {
        "url":      "https://etoro.tw/4kC8pHO",
        "label":    "Trade Forex on eToro",
        "headline": "Trade Currencies on eToro",
        "body":     "Major and minor forex pairs with competitive spreads.",
    },
    "fees": {
        "url":      "https://etoro.tw/40bkzhp",
        "label":    "See eToro's Full Fee Schedule",
        "headline": "Understand eToro's Fees",
        "body":     "Spreads, overnight fees, withdrawal costs — Tom's full breakdown.",
    },
    "pi": {
        "url":      "https://etoro.tw/3OTPXME",
        "label":    "Learn About Popular Investor",
        "headline": "Become an eToro Popular Investor",
        "body":     "Get paid when people copy your trades — full program details here.",
    },
    "demo": {
        "url":      "https://etoro.tw/4cyvSYl",
        "label":    "Try the eToro Demo Account",
        "headline": "Start with the Free Demo Account",
        "body":     "Practice with $100,000 virtual funds — no real money at risk.",
    },
    "tutorials": {
        "url":      "https://etoro.tw/40ifoMA",
        "label":    "Browse eToro's Beginner Guides",
        "headline": "New to eToro? Start Here.",
        "body":     "eToro's official beginner tutorials — learn the platform before risking any money.",
    },
}

# ── Per-video CTA assignment ──────────────────────────────────────────────────
# Maps video_id → CTA_PRESETS key. Unmapped videos default to "main".
VIDEO_CTA_MAP = {
    # Copy trading / Smart Portfolios
    "hO1zncbWqFM": "copy",    # should-i-copy-open-trades
    "hc8AXNKxJgk": "copy",    # etoro-take-profit
    "Gx1x01n8i8A": "copy",    # etoro-pause-copy
    "cx3Kc3M2Jxg": "copy",    # copy-trading-stop-loss-risk
    "noSTWBJkfvk": "copy",    # how-much-money-copy-trading
    "UZ9F2F42vvI": "copy",    # taking-profits-from-copytrading
    "mbaSu_VQ9bY": "copy",    # stop-copy-explained
    "yZNrUTMpbS8": "copy",    # minimum-trade-size-risks
    "ugHCBe5-coQ": "copy",    # copy-trading-blocked-fix
    "Gbhfgkhb90s": "copy",    # add-remove-funds-copy-trade
    # Fees
    "MjzXbe8lz40": "fees",    # spread-fees-explained
    "kP68l37HwiY": "fees",    # rollover-overnight-fees
    "4_EiZBcUT1U": "fees",    # withdrawal-fees
    "_kOIMbkqi-I": "fees",    # leverage-trading-fees-beginners
    "Po_WDHWJQtk": "fees",    # copy-trading-fees
    # Stocks / dividends
    "FEel7OxVfKc": "stocks",  # copy-trading-dividends
    "8Am2q7Kb5BU": "stocks",  # cfds-vs-real-stocks
    "lSmkRjtoMno": "stocks",  # dividends-social-trading
    # Popular Investor
    "tHNtskWEV0c": "pi",      # popular-investor-program-requirements
    # Demo / virtual account
    "OFhVWUqzIGA": "demo",        # etoro-virtual-practice-account
    "YZYgjitj7DM": "demo",        # etoro-dangerous-beginner-mistake
    # Beginner tutorials
    "k48YLAbEcY0": "tutorials",   # etoro-beginners-start-here
}

# ── Keyword mapping ────────────────────────────────────────────────────────────
# video_id → {slug, keyphrase, h1, tag, description, intro, headings, faqs}
# 'intro'    → 1-2 sentence paragraph shown before the embed (contains keyphrase)
# 'headings' → list of H2 labels to use in the transcript body
# 'faqs'     → list of {q, a} for the FAQ section (3 recommended)

KEYWORD_MAP = {
    # ── Tier 1: Low competition, high intent ──────────────────────────────────
    "daMK1Y54M-E": {
        "slug": "why-do-most-etoro-traders-lose-money",
        "keyphrase": "Why Do Most eToro Traders Lose Money?",
        "h1": "Why Do 76% of eToro Traders Lose Money?",
        "tag": "Platform reality",
        "description": "The uncomfortable truth about eToro's loss statistics — Tom explains why most retail traders lose money and what to do differently.",
        "intro": "As an eToro affiliate, I have to display a risk warning on every page — and at its peak, it said 76% of retail investors lose money on the platform. That's over three quarters. So what's going on, why are so many people losing, and how do you make sure you're not one of them?",
        "headings": ["The 76% Statistic — What It Actually Means", "The Get-Rich-Quick Trap", "Why Small Amounts Make It Worse", "Leverage: The Account Killer", "Fear of Missing Out", "The Emotional Rollercoaster", "What the Profitable 24% Do Differently", "Copy Trading Isn't a Shortcut Either", "Tom's Conclusion"],
        "article_sections": [
            {
                "h2": "The 76% Statistic — What It Actually Means",
                "paragraphs": [
                    "As an eToro affiliate, I HAVE to display a little warning on all my pages, and update it whenever eToro asks. At the moment it says:",
                    {"type": "note", "text": "Risk warning: 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk."},
                    "In the past that little warning (which is a legal requirement) has been as high as 76%. 76% are losing money when using the platform - What a sobering thought! That's over 3 quarters. It's a really scary stat for new users - so how do we make sure we're not part of that majority?",
                    "eToro has done a brilliant job of making trading accessible. The interface looks like social media which we're all used to — nice profiles, white backgrounds, everything beautifully designed. Whilst it makes everything simple and possible for us noobs to use, it may also be part of the problem - we think we're possibly safer than we are.",
                    "Compare it to something like MetaTrader 4, which looks like a NASA control panel, and you can see why people flock to eToro. But that accessibility can create a false sense of simplicity. Trading is not simple. The platform is. The markets are not.",
                ]
            },
            {
                "h2": "The Get-Rich-Quick Trap",
                "paragraphs": [
                    "If there's one single reason that explains most of that 76%, it's this: the desire to get rich quick.",
                    "As a kid, my ideas about trading and investing came from films and tv. Rich guys looking stressed but winning, white Lamborghinis, Manhattan glass skylines, expensive dinners and clubs. Everyone was beautiful, houses were huge, they all stared at numbers I didn't understand. No idea how they were doing it, but it looked great.",
                    "So when sites like eToro started popping up, my ideas of investing and trading were fuelled by hopes of finally being part of it all - let's go!",
                    {"type": "h3", "text": "What Happens Next"},
                    "So what do we do? We find a thing called 'leverage' which lets you amplify your trade sizes and we think \"yes please!\" Without the slightest clue what we're doing or how the markets work we pile into amplified trades, and immediately start panicking when the markets move against us. Chasing volatile assets, panic-buying into trends, doubling-down to recoup our losses — but underneath all of it is the same impulse. People come to eToro hoping to turn a small amount of money into a life-changing amount of money, fast. And that mindset is almost guaranteed to lose you money.",
                    {"type": "h3", "text": "So What Do the Pros Actually Make?"},
                    "The top hedge funds in the world — the Quantum Fund, Berkshire Hathaway, the absolute best in the business — generate returns of around 16-20% per year. These are people with decades of experience, teams of analysts, and billions under management. And they're making 20%.",
                    "When a new user deposits $500 and expects to turn it into $2,000 in a year, they're expecting to outperform Warren Buffett by a factor of four. It's not realistic, and chasing that kind of return leads to terrible decisions.",
                ]
            },
            {
                "h2": "Why Small Amounts Make It Worse",
                "paragraphs": [
                    "Most of us aren't rich. We come to eToro with maybe a few hundred dollars, or even a couple of thousand. If you put in $100, would you be extremely happy with $20 profit after a year? That's 20% - you're alongside the best in the world. But nobody wants $20 after a year. What are we really looking for?",
                    "We're looking for money that can make a significant difference to our lives. $500 needs to produce another $500. At least. Even then, it won't make much difference but there's no way $50 in a year is even worth our time. But that's a 100% return. It's almost completely impossible. If you've managed it, it's because you've taken incredible amounts of risk and somehow come out ahead. Statistically most people lose this bet.",
                    {"type": "h3", "text": "Think Percentages, Not Pounds"},
                    "We've got to think in terms of percentages, not in terms of cash amounts. What does this mean? It means when we see huge cash profits being reported by the Warren Buffets of the world, we need to realise they started with much more money, so it's easy to make seemingly huge returns whilst taking less risk than your average retail investor.",
                    "They invest a million and at the end of the year come away with $100,000 in profit. Wow! We say - $100,000! But that's a 10% return. They could have kept their risk reasonably low to get that return.",
                    {"type": "h3", "text": "The \"I've Got Nothing to Lose\" Mindset"},
                    "We who want to strike it rich are generally thinking \"Look, I don't have much money. I've put in $500 - I either hit big and it changes my life a bit, or I lose $500 and I'm pretty much in the same situation as I am now. My $500 isn't going to get me anywhere anyway.\"",
                    "So what happens? You start looking at the traders who are up 200%, 400%. \"This is the guy for me!\" You start using leverage. You start making manual trades on gut instinct. (Believe me, in the beginning I was trying to trade Gold with 20X leverage before I was even fully awake - it would have been a comedy sketch if I wasn't losing real money quite so fast.) And before you know it, you're part of the 76%.",
                    "The irony is that 20% on $500 is genuinely excellent. It's world-class performance. But it doesn't feel like it when the number is only $100. This is a psychological trap, and it catches almost everyone who starts small.",
                ]
            },
            {
                "h2": "Leverage: The Account Killer",
                "paragraphs": [
                    "Leverage is a way to amplify your trade — eToro lends you extra money so you can control a bigger position than your balance would normally allow. And for beginners, it's the single fastest way to blow your account.",
                    {"type": "h3", "text": "A Quick Example: The Apple Trade"},
                    "Let's say. You want to open a $100 trade in Apple stock. But then you see the leverage \"X10\" button.",
                    "All of a sudden your $100 trade could be a $1000 trade! \"Wow\" you think\u2026, \"if Apple stock goes up 10%, I'll make $100! - Apple always does well - let's go!\" And so, you open your new Apple trade.",
                    "You put in $100, and chose X10 leverage, so your position size is actually now $1000. It's like magic! We don't have much money so this seems like a great way to level the playing field and really have some proper trades open!",
                    "Now the thing about the markets is that they never go up or down in a straight line - it takes time to get used to this, but in the beginning, these jagged moves can be terrifying. Markets can move fast, and losses can appear suddenly.",
                    "Apple stock drops 2%. We're watching our trade like a hawk, and it's not 2% of $100 we've lost, (an easy to deal with $2), it's 2% of $1000 we've lost (because of our leverage) - a slightly harder $20. And it's a bad day, so it keeps dropping (this often happens). Now we're down 4% - $40 dollars in less than an hour.",
                    {"type": "h3", "text": "When Panic Takes the Wheel"},
                    "Over time, you may get used to this fluctuation and it doesn't worry you so much - you start looking at longer term trends, but in the beginning, when you see your money vanishing and you really don't know why, statistically you'll make terrible decisions based on emotion and panic, and you'll lose money. We hold when we should cut our losses. We panic-sell when we should have held, we double down to chase our losses, and statistically overall, we lose more than we win.",
                    "The other problem is that when our Apple trade loses 5%, we'll have lost $50 of our original $100 investment, as it's 5% of $1000 we've lost due to our leverage use. This could lead to eToro closing our position automatically so that we don't lose too much money - in some cases they set mandatory 'stop-losses' on trades as protection\u2026 All of a sudden, we've lost half of our $100, we're out of the trade and we're wondering what just happened.",
                    "So, in the beginning, watch out for leverage. You can do what you want, this isn't investment advice! But be aware that a LOT of people get themselves into trouble using it before they understand the markets or how leverage works\u2026",
                ]
            },
            {
                "h2": "Fear of Missing Out",
                "paragraphs": [
                    "FOMO — the fear of missing out — is another major driver of losses. It's that feeling of 'if I don't make this trade right now, I'll never get another chance.' Every opportunity feels urgent. Every price movement feels like the last train leaving the station.",
                    "The reality is the exact opposite. In financial markets, there's a new opportunity every five minutes. There are thousands of instruments to trade — stocks, crypto, commodities, forex — and the markets are open almost around the clock. The experienced traders know this. They don't rush. They wait for the right setup.",
                    "But when you're new and you're desperate to make money, everything feels like now or never. And that urgency leads to over-trading, chasing trends that have already peaked, and entering positions without proper analysis.",
                    {"type": "h3", "text": "The Life Lessons Nobody Mentions"},
                    "It's a strange thing about trading and investing that so many of the lessons we need to learn aren't about maths or technical analysis or analysing businesses (although if we're going to trade manually, we'll need to learn all that as well!) but rather, there's a whole bunch of self-development lessons to learn. How to stay detached and rational instead of letting our emotions control us - how to let go of that tempting fear that \"If I don't make this one trade, there'll never be another like it! This is my one big chance!\"",
                    "It sounds overly dramatic but you'll see :) This thought pops up for everyone, and it comes back repeatedly throughout our investing life cycle - sales and marketing people actually try to trigger it in us by saying there's limited supply, and \"only 20 spots left!\" etc. It's a powerful emotional trigger, and we need to learn to recognise it and not fall for the bait...",
                ]
            },
            {
                "h2": "The Emotional Rollercoaster",
                "paragraphs": [
                    "One pattern that's incredibly common on eToro — and you can see it on hundreds of profiles — is the boom-bust cycle. A trader has a few great months, gains are flying, everything looks brilliant. Then one bad month wipes out everything.",
                    "This happens because the strategies that produce big gains are usually the same ones that carry big risk. You can't consistently make 30-40% monthly returns without taking on enormous risk — and eventually that risk catches up with you. If you keep rolling the dice, and greed takes over, eventually, statistically, it goes wrong.",
                    {"type": "h3", "text": "Popular Investors Have It Even Worse"},
                    "And if you're planning to become a popular investor on the site and hopefully have people copying your trades, (it can be very lucrative if you do well enough on the popular investor program) it's on a whole other level\u2026",
                    "I can't tell you how many times I've seen this, even with popular investors. They gather loads of new copiers during their huge-gains months. It's going up and up, and everyone's praising the trader they're copying for what looks like an almost magical ability to win in the markets.",
                    "Then the losses start, and the followers turn ugly - constant comments about \"what's happening to my money!\" Suggestions fly in from people who've only been on the site for a few weeks, but suddenly everyone's a pro telling them how it should be done, and you see the trader start to buckle under the pressure\u2026",
                    "Instead of following their carefully constructed plan and taking things slow, they react to the pressure and fear and start making bad decisions - trades which they'd normally avoid due to risk suddenly become their only way to 'make it all back' and pretty soon they're blown 80% of their account and all the copiers are gone.",
                    "I don't envy them - having a channel and having my account so public, it's very easy to start thinking \"What will they all say..\" before making investing decisions, and that's a terrible motivation. Investing and trading really require cold hard logic - it's another one of those life-lessons we all need to learn if we're hoping to really make this work for us.",
                ]
            },
            {
                "h2": "What the Profitable 24% Do Differently",
                "paragraphs": [
                    "So if 76% are losing, what are the 24% doing right? From years of watching profiles on eToro, a few patterns emerge.",
                    "They accept lower returns. A 15-20% annual return with low drawdowns is their goal, not 400%. They understand that consistent, boring gains compound into real wealth over time.",
                    "They use little or no leverage. By trading with their own money (x1 leverage), they avoid overnight fees, reduce risk dramatically, and can ride out temporary dips without being forced to close.",
                    "There ARE experienced great traders who employ leverage as part of their strategy, but these are traders who really understand what they're doing - statistics show that for beginners, the use of leverage is one of the greatest risks, and tends toward gambling rather than trading or investing. I'm not a pro, I'm not a financial advisor, but wow does it seem to cause us all problems as beginners, so be warned!",
                    "They invest more capital at lower risk, rather than less capital at higher risk. It's better to put $5,000 in and expect 20% ($1,000 gain) than to put $500 in and chase 200% ($1,000 gain). The expected return is the same but the risk profile is completely different.",
                    {"type": "h3", "text": "The Excitement Trap"},
                    "I think when we come in, it's all so exciting that we're just brimming with enthusiasm - we log in all the time watching our money - how much have we made? Did I choose right? What are other people saying? It's exciting, it's new and we want to see some action.",
                    "What we need to realise is that it can all be a lot slower than we anticipated. If we approach it sensibly, expecting 15% in a year, and we've put in $1000, then we're looking at $150 profit after 12 months. We're not going to be seeing huge movements all the time. It's going to be much slower than we expect...",
                    "So the temptation can be to try to make something happen - open extra trades, use leverage to make things move faster, constantly try to jump onto a new asset which might make things happen and create some excitement. It's understandable, and it's another little trap - if we're here for the dopamine fix, it's another version of the wrong approach. This requires a certain detachment (I know! I want adrenaline too!! but this isn't the place for it, as statistically that's where losses stack up)",
                    {"type": "h3", "text": "\"Why Aren't You Trading?!\""},
                    "The same's true for copy trading - I see a lot of new people copy a trader who has years of steady statistics showing profit. But the new guy is impatient, and the trader they've copied is taking things slow, watching the markets, waiting for their right entry point. \"Why aren't you trading?\" comes the comment from the new guy... \"What's wrong with this guy??\" says another - It's all too familiar :) We want some action - we want to see those big moves that happen in the films.",
                    "Be aware that whilst copying someone, it's long term success we're looking for - that's the whole point. Let them take care of the day to day ups and downs and worries. It takes some getting used to though as we realise we just have to get on with life as normal - this isn't going to change everything in a month... again - more letting go and life lessons :)",
                    "They don't panic. They have a plan, they stick to it, and they don't react emotionally to every dip. If a copied trader has a bad month but their long-term statistics are solid, they stay the course.",
                ]
            },
            {
                "h2": "Copy Trading Isn't a Shortcut Either",
                "paragraphs": [
                    "Copy trading removes one big problem — you don't need to know how to trade. But it introduces its own risks. If you're copying someone who trades with a boom-bust style, you'll get the same boom-bust results.",
                    "The key is choosing who to copy very carefully. Look for low risk scores, low drawdowns, and consistent returns over at least 12 months. The traders who look exciting — up 80% one month, down 40% the next — are the ones most likely to blow up your account along with theirs.",
                    {"type": "h3", "text": "How My Approach Has Changed"},
                    "Over time my approach to who I copy has changed. I've tried copying some of the traders who appear to be vastly outperforming everyone else and haven't had any losing months for over a year, only to watch them lose it all after a couple of terrible months and that dreaded switch in behaviour.",
                    "I used to think 12 months trading history was enough, but now I think the longer the better - I look for at least two years of trading history now, and I've learned to check their charts looking for hidden large sudden losses and other patterns which might signal trouble in future. I've made videos about that if you're interested.",
                    {"type": "h3", "text": "What to Look For When Choosing a Trader"},
                    "You get used to it really - looking at all the stats shown and getting a rough idea of their trading style. That takes a little time, but as a general rule of thumb I look for a few years of trading history and stability above all. I can't deal with the boom/bust guys anymore as you spend two years accumulating gains only to lose it all in a month, and suddenly those entire two years were a waste of time!",
                    "eToro's copy people page was revamped a while ago, and they included some useful new filtering options - 'most consistent' has been my favourite and how I found some really good traders. You can also filter by those who outperformed the markets in general and things like that - it's got more helpful over time and there's a large pool of traders, but it still tends to be the best ones who can somehow beat or equal the broader markets but also avoid the inevitable drawdowns who attract all the copiers. When they get too big, eToro usually raises the amount needed to copy them, so there's a bit of an art to timing when to copy.",
                    "If you want to manually trade instead of copy, invest in education first. Do a proper course. Learn the fundamentals before you put real money at risk. The cost of a good trading course is almost always less than the cost of learning by losing money on the platform.",
                    {"type": "h3", "text": "Only Invest What You Can Afford to Lose"},
                    "They say \"only invest what you can afford to lose\" and that sounds great, but as beginners, we're just hoping we don't lose and it can often be money we actually really need. You've got to watch out for this - as we all know, things pop up unexpectedly in life and suddenly we need money for something urgently. Investing can be a long slow process, and if we have to close trades just because we desperately need the cash and have no other backup, then it can mean closing trades at the wrong time and incurring significant losses.",
                    "Unless you plan to be an incredibly active trader, and it's your profession, understand that if you're somehow relying on this as a primary driver of your income, you're liable to start gambling to get the kind of gains you need. The pros make a life of it - It's slow, methodical, and they've got a plan. For the more passive among us, we've got to realise that at times the investment will be down and may stay down for quite a while before things pick back up. It might be a wise idea to have your emergency fund for unexpected life-events separate from your trading account if possible to avoid forced sells at bad times.",
                    {"type": "h3", "text": "When Losses Get Real"},
                    "You've got to also realise that losses are a huge potential reality. If the money you're trading with is really money you need and not money you can genuinely afford to lose, it's going to put a lot of stress on you. Is that worth it? It's a horrible situation when you've lost money you or your family needs and you're not wanting to tell them about it.",
                    "\"Maybe I can make it back without telling them..\" It's a classic line which many have thought before us, and which often leads to taking huge risks and losing even more. That's a terrible situation for anyone to be in, and before starting, realise it's a genuine possibility and people do find themselves in this situation.",
                    "It's really easy to see the potential huge gains we might make and just brush the risks aside, but if the worst happens, it's just not worth even the huge potential gains. This takes some real discipline, as everyone's tempted when they try this out.",
                    "They say \"Only risk what you can afford to lose\". I think there's real wisdom in that. We may get away with it for a while, but eventually if we don't follow this rule, the stress is going to be enormous.",
                    {"type": "note", "text": "I'd say the single most important thing I've learned is this: it's not a get-rich-quick scheme. It can make money — I believe that — but it's a get-rich-slowly scheme. Or more honestly, a make-some-money-slowly scheme. The sooner you accept that, the sooner you stop making the mistakes that put you in the 76%."},
                ]
            },
            {
                "h2": "Tom's Conclusion",
                "paragraphs": [
                    "76% is a big, real, frightening number. And it's not because eToro is a scam or the fees are unfair — it's because trading is inherently risky, and the platform's accessibility makes people underestimate that risk.",
                    "If you're starting out, here's what I'd suggest: use the virtual account first, copy low-risk traders, forget about getting rich quick, and put in money you can genuinely afford to leave alone for years. The returns will feel small at first, but that's exactly what sustainable investing looks like.",
                    "The people who make money on eToro are the patient ones. The boring ones. The ones who aren't trying to turn $500 into a Lamborghini by next month. I hope I'm finally learning to be one of those people!",
                ]
            },
        ],
        "faqs": [
            {"q": "Why do most eToro traders lose money?", "a": "The main reasons are over-leveraging, chasing quick profits, poor risk management, and emotional decision-making. eToro's platform makes trading feel simple, which can lead beginners to underestimate the risks of CFDs and leverage."},
            {"q": "What percentage of eToro traders are profitable?", "a": "According to eToro's own risk disclosure, around 76% of retail investor accounts lose money when trading CFDs. Only roughly 24% of traders are consistently profitable on the platform."},
            {"q": "How can I avoid losing money on eToro?", "a": "Avoid high leverage, use the virtual practice account first, copy only lower-risk traders with consistent long-term returns, and never invest more than you can afford to lose. Treat it as a long-term investment, not a get-rich-quick scheme."},
            {"q": "Is eToro a scam?", "a": "No. eToro is a regulated platform authorised by the FCA, CySEC, and ASIC. The 76% statistic reflects the inherent risk of trading CFDs, not a problem with the platform itself. Most traders lose money on every CFD platform, not just eToro."},
            {"q": "What returns should I realistically expect from eToro copy trading?", "a": "Realistic annual returns from copy trading lower-risk traders are around 10-25% per year. The world's best hedge funds average 16-20% annually. Anyone promising significantly more than that is taking on significant risk."},
        ],
    },
    "hO1zncbWqFM": {
        "slug": "should-i-copy-open-trades-etoro",
        "keyphrase": "Should I Copy Open Trades on eToro?",
        "h1": "Should I Copy Open Trades on eToro?",
        "tag": "Copy trading guide",
        "description": "Tom explains what 'copy open trades' actually means on eToro, the risks of copying existing positions, and when it makes sense to do it.",
        "intro": "When you start copying a new trader on eToro, you face an important decision: should you copy open trades or only new ones going forward? Tom walks through exactly what this means, the risks involved, and how to make the right call for your situation.",
        "headings": ["What 'Copy Open Trades' Actually Means", "The Risk of Copying Existing Positions", "When It Makes Sense to Copy Open Trades", "When to Avoid Copying Open Trades", "Tom's Recommendation"],
        "faqs": [
            {"q": "What does 'copy open trades' mean on eToro?", "a": "When you enable 'copy open trades', your money is immediately used to buy into all the positions the trader currently holds, in proportion to your copy amount. If you don't enable it, you only copy new trades they open from that point forward."},
            {"q": "Should I copy open trades when starting to copy someone on eToro?", "a": "It depends on the trader's style. For long-term investors who hold positions for months, copying open trades is usually fine. For short-term traders, you risk buying into positions that are already extended and may be near their target — so it's often safer to skip open trades."},
            {"q": "What happens if I don't copy open trades on eToro?", "a": "You will only mirror trades the trader opens after you start copying them. You won't have exposure to their current portfolio, which means you may miss some gains but also avoid buying into overextended positions."},
        ],
    },
    "hc8AXNKxJgk": {
        "slug": "etoro-take-profit-can-i-change-it",
        "keyphrase": "eToro Take Profit — Can I Change or Disable It?",
        "h1": "eToro Take Profit — Can I Change or Disable It?",
        "tag": "eToro how-to",
        "description": "Can you edit or remove a take profit on eToro copy trades? Tom walks through exactly what's possible and what isn't.",
        "intro": "A common question from eToro users is whether you can change or disable the take profit level on a copy trade after it's already been set. Tom answers this directly — explaining what eToro does and doesn't let you control when you're copying another trader.",
        "headings": ["What Take Profit Does on eToro", "Can You Change Take Profit on a Copy Trade?", "What eToro Actually Allows", "The Workaround", "Tom's Take"],
        "faqs": [
            {"q": "Can I change the take profit on an eToro copy trade?", "a": "Yes, you can edit the take profit level on a copy trade in most cases. Go to your portfolio, tap on the copy, and look for the edit options. However, individual positions within a copy may have limitations depending on the trader's settings."},
            {"q": "Can I disable take profit on eToro?", "a": "You can remove a take profit level by editing it and clearing the value. Without a take profit set, the position will stay open until you manually close it or your stop loss is triggered."},
            {"q": "What happens when take profit is triggered on a copy trade?", "a": "When the take profit level is reached, the position is automatically closed at that price and you receive the profit in your available balance. The trader you're copying may still hold their position — your copy simply closes at your set level."},
        ],
    },
    "Gx1x01n8i8A": {
        "slug": "etoro-pause-copy-explained",
        "keyphrase": "eToro Pause Copy — How It Works",
        "h1": "eToro Pause Copy — What It Does and When to Use It",
        "tag": "Copy trading guide",
        "description": "What does pausing a copy do on eToro? Tom explains the difference between pause copy and stop copy, and when you'd use each one.",
        "intro": "eToro's 'Pause Copy' feature is one of the least understood tools on the platform. Tom explains exactly what happens to your positions when you pause a copy, how it differs from stopping it entirely, and the scenarios where pausing is the right move.",
        "headings": ["Pause Copy vs Stop Copy — The Difference", "What Happens When You Pause a Copy", "When to Use Pause Copy", "How to Pause a Copy on eToro", "Tom's Recommendation"],
        "faqs": [
            {"q": "What does pausing a copy do on eToro?", "a": "Pausing a copy means the trader you're copying can still open and close trades, but your copy will not mirror any new trades they open. Your existing copied positions remain open and continue to run as normal."},
            {"q": "What's the difference between pause copy and stop copy on eToro?", "a": "Pause copy keeps your existing positions open but stops new ones being copied. Stop copy closes all your copied positions and ends the copy relationship entirely, returning your funds to available balance."},
            {"q": "When should I pause a copy on eToro?", "a": "Pausing is useful when you think a trader is about to take on more risk than you're comfortable with (e.g. before a major market event), but you want to keep your current profitable positions running rather than closing everything."},
        ],
    },
    "cx3Kc3M2Jxg": {
        "slug": "etoro-copy-trading-stop-loss-risk",
        "keyphrase": "eToro Copy Trading Stop Loss and Risk Management",
        "h1": "eToro Copy Trading: Managing Your Stop Loss and Risk",
        "tag": "Risk management",
        "description": "Tom walks through how stop losses work when copy trading on eToro, how he sets his own risk levels, and what drawdowns to watch for.",
        "intro": "Understanding your stop loss settings when copy trading on eToro is one of the most important — and most overlooked — parts of risk management. Tom explains how copy trading stop losses work, how to set them correctly, and what the drawdown figures really mean.",
        "headings": ["How Stop Loss Works in Copy Trading", "Setting Your Copy Stop Loss Level", "Understanding Drawdowns", "Tom's Own Risk Settings", "Key Risk Management Rules"],
        "faqs": [
            {"q": "How does stop loss work when copy trading on eToro?", "a": "When you copy a trader, you can set a copy stop loss as a percentage of your copy amount. If the total value of your copy falls by that percentage, the copy is automatically stopped and all positions are closed. This limits your maximum loss on that copy."},
            {"q": "What stop loss percentage should I set for copy trading on eToro?", "a": "Tom typically recommends a copy stop loss of around 20-40% depending on the trader's risk score and drawdown history. A very aggressive trader might warrant a tighter stop loss, while a low-risk trader with shallow drawdowns could be given more room."},
            {"q": "What is a drawdown in eToro copy trading?", "a": "A drawdown is the peak-to-trough decline in a trader's portfolio value over a given period. It shows the worst loss you would have experienced following that trader historically. A 20% maximum drawdown means the trader's portfolio once fell 20% from its highest point before recovering."},
        ],
    },
    "FEel7OxVfKc": {
        "slug": "etoro-copy-trading-dividends",
        "keyphrase": "Do You Get Dividends Copy Trading on eToro?",
        "h1": "Copy Trading Dividends on eToro — How They Work",
        "tag": "eToro income",
        "description": "Do copy traders on eToro receive dividends? Tom explains how copy dividends work and the difference between CFD and real-asset dividends.",
        "intro": "One question that comes up a lot: if you copy a trader on eToro who holds dividend-paying stocks, do you receive those dividends too? Tom explains exactly how dividends work in copy trading — including the important difference between CFD positions and real stock positions.",
        "headings": ["Do Copy Traders Get Dividends?", "CFD Dividends vs Real Stock Dividends", "How eToro Credits Copy Dividends", "Which Positions Pay Dividends", "Maximising Dividend Income on eToro"],
        "faqs": [
            {"q": "Do you receive dividends when copy trading on eToro?", "a": "Yes, you can receive dividends when copy trading on eToro, but only on positions held as real assets (non-leveraged). CFD positions receive a dividend adjustment instead — the equivalent cash value is added to your account, but it's treated differently for tax purposes in some countries."},
            {"q": "What is a copy dividend on eToro?", "a": "A copy dividend is the dividend payment you receive on a position that was opened as part of a copy trade. It works the same way as a regular dividend on eToro — if the position is a real asset, you receive the dividend; if it's a CFD, you receive a cash adjustment."},
            {"q": "How do I make sure I get dividends on eToro copy trades?", "a": "Ensure the copied positions are held as real assets rather than CFDs. You can check this in your portfolio. Non-leveraged stock positions on eToro are held as real shares and qualify for dividends. Leveraged or short positions are CFDs and receive cash adjustments instead."},
        ],
    },
    "A1iTColkAck": {
        "slug": "etoro-negative-balance-protection-most-you-can-lose",
        "keyphrase": "eToro Negative Balance Protection — What's the Most You Can Lose?",
        "h1": "eToro Negative Balance Protection: What's the Most You Can Lose?",
        "tag": "Risk management",
        "description": "Tom explains eToro's negative balance protection in plain English — what it means, who it covers, and the real limit on how much you can lose.",
        "intro": "A big fear for new eToro users is: could I lose more than I put in? Tom answers this question directly by explaining eToro's negative balance protection — what it guarantees, who it applies to, and what the absolute worst-case scenario actually looks like.",
        "headings": ["What Is Negative Balance Protection?", "Does eToro Have Negative Balance Protection?", "Who Is Covered", "The Real Worst-Case Scenario", "How to Protect Yourself Further"],
        "faqs": [
            {"q": "Can you lose more money than you put into eToro?", "a": "For most retail clients, no. eToro offers negative balance protection, which means your account balance cannot go below zero. The maximum you can lose is what you've deposited. However, this applies to retail accounts — professional traders do not have this protection."},
            {"q": "What is negative balance protection on eToro?", "a": "Negative balance protection means that if your losses on leveraged trades exceed your account balance, eToro absorbs the excess loss and resets your balance to zero rather than asking you to pay additional funds. It's a regulatory requirement in the EU and UK for retail clients."},
            {"q": "Is eToro's negative balance protection reliable?", "a": "Yes, eToro is regulated by the FCA (UK) and CySEC (EU), both of which require negative balance protection for retail clients. This means the protection is not just a company policy but a legal requirement they must honour."},
        ],
    },
    "MjzXbe8lz40": {
        "slug": "etoro-spread-fees-explained",
        "keyphrase": "eToro Spread Fees Explained",
        "h1": "eToro Spread Fees — What Are They and How Much Do They Cost?",
        "tag": "eToro fees",
        "description": "What are spread fees on eToro and how do they affect your trades? Tom breaks down the hidden cost that every eToro user pays.",
        "intro": "Every time you open a trade on eToro, you pay a spread fee — even if it's not shown as a separate line item. Tom explains exactly what spread fees are, how they're built into the price you see, and how they affect your profitability over time.",
        "headings": ["What Is the Spread on eToro?", "How Spread Fees Are Charged", "Spread Costs by Asset Type", "The Impact on Your Trades", "How to Minimise Spread Costs"],
        "faqs": [
            {"q": "What are spread fees on eToro?", "a": "The spread is the difference between the buy (ask) price and the sell (bid) price of an asset. When you open a trade on eToro, you immediately pay this spread — which is why new positions show a small loss the moment they open. It's eToro's primary way of charging for trades."},
            {"q": "How much are eToro's spread fees?", "a": "Spread fees vary by asset. For stocks and ETFs, eToro charges no additional markup on the market spread. For cryptocurrency, the spread is around 1%. For forex pairs, spreads typically range from 1 to 4 pips depending on the currency pair and market conditions."},
            {"q": "Why is my eToro trade immediately showing a loss?", "a": "When you open a new position on eToro, the spread fee is immediately applied, which puts the trade slightly into the negative. As the asset price moves in your favour, you'll first break even (recovering the spread cost) and then move into profit."},
        ],
    },
    "kP68l37HwiY": {
        "slug": "etoro-rollover-overnight-fees",
        "keyphrase": "eToro Overnight Rollover Fees Explained",
        "h1": "eToro Overnight (Rollover) Fees — How to Track and Understand Them",
        "tag": "eToro fees",
        "description": "Tom explains what eToro's overnight rollover fees are, when they're charged, how much they cost, and how to keep track of them simply.",
        "intro": "If you hold leveraged or short positions on eToro overnight, you'll be charged an overnight rollover fee. Tom explains what these fees are, when they hit your account, how they're calculated, and — crucially — how to keep track of them so they don't quietly erode your returns.",
        "headings": ["What Are eToro Overnight Fees?", "When Are Overnight Fees Charged?", "How to Calculate Your Overnight Fee", "Weekend Fees on eToro", "How to Minimise Overnight Costs"],
        "faqs": [
            {"q": "What are overnight fees on eToro?", "a": "Overnight fees (also called rollover fees) are charged when you hold a leveraged CFD position open past 21:00 GMT. They represent the cost of borrowing money to maintain the leverage on your position overnight. Non-leveraged real asset positions do not incur overnight fees."},
            {"q": "How much are eToro's overnight fees?", "a": "Overnight fees vary by asset and leverage level, and are calculated as an annualised interest rate applied to the leveraged portion of your position. Weekend fees are triple the standard overnight fee, charged once per week to account for Saturday and Sunday."},
            {"q": "How can I avoid overnight fees on eToro?", "a": "The simplest way to avoid overnight fees is to only hold non-leveraged positions in real assets (set leverage to x1). Short positions and any leveraged position will always incur overnight fees. If you're investing long-term, buying real shares without leverage is the most cost-effective approach."},
        ],
    },
    "4_EiZBcUT1U": {
        "slug": "etoro-withdrawal-fees",
        "keyphrase": "eToro Withdrawal Fees and Minimum Amount",
        "h1": "eToro Withdrawal Fees — Current Amounts and Minimum",
        "tag": "eToro fees",
        "description": "What does eToro charge to withdraw? Tom covers the current withdrawal fee, minimum withdrawal amount, and tips to avoid surprises.",
        "intro": "eToro charges a fee when you withdraw money from your account — and there's a minimum withdrawal amount too. Tom gives a clear breakdown of the current withdrawal fee and minimum, and explains what happens when you withdraw in different currencies.",
        "headings": ["eToro's Current Withdrawal Fee", "The Minimum Withdrawal Amount", "Currency Conversion Costs", "How Long Does Withdrawal Take?", "Tips to Reduce Withdrawal Costs"],
        "faqs": [
            {"q": "How much does eToro charge for withdrawals?", "a": "eToro charges a flat $5 withdrawal fee for USD accounts. GBP and EUR accounts currently have free withdrawals. The fee is deducted from your withdrawal amount, so if you withdraw $30 (the minimum), you receive $25."},
            {"q": "What is the minimum withdrawal from eToro?", "a": "The minimum withdrawal from eToro is $30 for USD accounts. For GBP and EUR accounts, there is no minimum withdrawal amount and no fee."},
            {"q": "How long do eToro withdrawals take?", "a": "eToro typically processes withdrawals within 1-3 business days. Funds then take an additional 1-5 business days to appear in your bank account depending on your bank and payment method."},
        ],
    },
    "_kOIMbkqi-I": {
        "slug": "etoro-leverage-trading-fees-beginners",
        "keyphrase": "eToro Leverage Trading Fees for Beginners",
        "h1": "eToro Leverage Trading Fees — What Beginners Need to Know",
        "tag": "eToro fees",
        "description": "Tom explains the fees attached to using leverage on eToro — the overnight charges, spread costs, and why leverage can quietly drain your account.",
        "intro": "Leverage on eToro lets you control a larger position with less money — but it comes with fees that can quickly eat into your returns. Tom breaks down exactly what leverage trading costs on eToro and why beginners often underestimate how these fees stack up.",
        "headings": ["How Leverage Works on eToro", "The Fees Attached to Leverage", "Overnight Fees on Leveraged Positions", "A Real-World Cost Example", "Is Leverage Worth It for Beginners?"],
        "faqs": [
            {"q": "What fees does eToro charge for using leverage?", "a": "Using leverage on eToro means your position is a CFD, which incurs overnight fees for every night you hold it open. There are no upfront fees for using leverage itself, but the overnight charges accumulate quickly on large or long-held leveraged positions."},
            {"q": "Does leverage cost money on eToro?", "a": "Indirectly, yes. Leverage doesn't carry an upfront cost, but leveraged positions on eToro are CFDs that incur nightly rollover fees. The higher your leverage and the longer you hold the position, the more you pay. Weekend fees are also triple the normal nightly rate."},
            {"q": "Should beginners use leverage on eToro?", "a": "Most experienced traders would advise beginners to avoid leverage entirely until they have a solid understanding of how it works. Leverage amplifies both gains and losses, and the associated overnight fees can make profitable trades unprofitable if held too long."},
        ],
    },
    "8Am2q7Kb5BU": {
        "slug": "etoro-cfds-vs-real-stocks",
        "keyphrase": "eToro CFDs vs Real Stocks — What's the Difference?",
        "h1": "eToro: CFDs or Real Stocks — What Are You Actually Buying?",
        "tag": "eToro explained",
        "description": "Do you actually own shares when you trade on eToro? Tom explains the difference between CFDs and real stocks and why it matters.",
        "intro": "One of the most common points of confusion on eToro: are you actually buying real shares, or just a CFD contract? The answer depends on how you trade. Tom explains the key differences between CFDs and real stock ownership on eToro — and why it matters for fees, dividends, and risk.",
        "headings": ["What Is a CFD on eToro?", "When eToro Uses Real Stocks vs CFDs", "Key Differences That Affect You", "Dividends: CFDs vs Real Shares", "Which Should You Choose?"],
        "faqs": [
            {"q": "Do you actually own stocks when you buy them on eToro?", "a": "It depends. Non-leveraged Buy positions in stocks are held as real shares — you actually own the underlying asset. Any leveraged position, short position, or non-stock asset is held as a CFD, meaning you own a contract tracking the price but not the asset itself."},
            {"q": "What is the difference between a CFD and a real stock on eToro?", "a": "A CFD (Contract for Difference) lets you speculate on the price of an asset without owning it. It can be leveraged, can go short, and incurs overnight fees. A real stock gives you actual ownership, qualifies for dividends, and has no overnight fees — but cannot be leveraged or shorted."},
            {"q": "How do I know if my eToro position is a CFD or a real stock?", "a": "Check the leverage setting on your position. If leverage is set to x1 and the position is a Buy, it's a real asset. If any leverage above x1 is applied, or if it's a Sell (short) position, it's a CFD. You can also see this in the position details in your portfolio."},
        ],
    },
    "noSTWBJkfvk": {
        "slug": "how-much-money-can-i-make-copy-trading-etoro",
        "keyphrase": "How Much Money Can I Make Copy Trading on eToro?",
        "h1": "How Much Money Will You Make Copy Trading on eToro?",
        "tag": "Copy trading returns",
        "description": "Tom gives a realistic answer to the most common eToro question — how much can you actually expect to make copy trading?",
        "intro": "How much money can you realistically make copy trading on eToro? It's the question everyone asks first, and the answer might surprise you. Tom gives a realistic breakdown based on years of personal experience — covering expected returns, the impact of your starting amount, and what 'good' actually looks like.",
        "headings": ["Realistic Returns from eToro Copy Trading", "Why Your Starting Amount Matters More Than % Returns", "What Good Copy Traders Actually Make", "The Maths That Surprises People", "Tom's Advice"],
        "faqs": [
            {"q": "How much money can you make copy trading on eToro?", "a": "Realistic annual returns from copy trading on eToro range from around 10-25% per year when following lower-risk traders with consistent track records. Higher returns are possible but come with higher risk. On a $1,000 investment at 20% annual return, that's $200 per year."},
            {"q": "Is copy trading on eToro worth it?", "a": "For most people, copy trading on eToro is worth it as a long-term investment strategy if you invest an amount you can afford to lose, copy lower-risk traders, and treat it as a supplement to your income rather than a replacement. It's not a route to quick wealth."},
            {"q": "How much do I need to start copy trading on eToro?", "a": "The minimum to copy a trader on eToro is $200. However, with small amounts the percentage returns translate to very small absolute gains. Tom recommends investing only money you can genuinely afford to leave invested for several years."},
        ],
    },
    "z9M1eB-DTMI": {
        "slug": "etoro-leverage-trading-beginners",
        "keyphrase": "Leverage Trading for Beginners on eToro",
        "h1": "Leverage Trading for Beginners — eToro Explained",
        "tag": "Beginners guide",
        "description": "Tom explains leverage trading on eToro for complete beginners — what it means, how it multiplies gains and losses, and whether you should use it.",
        "intro": "Leverage trading is one of the most misunderstood features on eToro — and one of the most dangerous for beginners. Tom explains what leverage actually means, shows you how it multiplies both your gains and your losses, and gives his view on whether beginners should use it at all.",
        "headings": ["What Is Leverage Trading?", "How Leverage Works on eToro", "The Danger: Losses Are Multiplied Too", "Leverage Fees and Overnight Costs", "Tom's Verdict for Beginners"],
        "faqs": [
            {"q": "What is leverage trading on eToro?", "a": "Leverage trading means eToro lends you extra money to open a position larger than your own funds would allow. For example, with x5 leverage and $100 of your own money, you can control a $500 position. If the price moves 10% in your favour, you gain 50% on your original $100 — but a 10% move against you also loses 50%."},
            {"q": "Is leverage trading safe for beginners on eToro?", "a": "No — leverage is one of the main reasons most retail traders lose money on eToro. It amplifies losses as much as gains, and leveraged positions incur overnight fees that accumulate over time. Most experienced traders recommend beginners avoid leverage until they fully understand the risks."},
            {"q": "How do I turn off leverage on eToro?", "a": "When opening a trade, set the leverage multiplier to x1. This means you're only using your own money and the position will be held as a real asset (for stocks). You can also change leverage on existing positions in some cases via the portfolio edit screen."},
        ],
    },
    "k48YLAbEcY0": {
        "slug": "etoro-beginners-start-here",
        "keyphrase": "eToro Beginners Guide — Start Here",
        "h1": "eToro Beginners — Everything You Need to Know Before You Start",
        "tag": "Beginners guide",
        "description": "Tom's complete eToro beginners guide — the essential tutorials covering copy trading, fees, leverage, and everything you need before depositing money.",
        "intro": "If you're new to eToro and wondering where to begin, this is the right place. Tom's eToro beginners guide covers the essentials — copy trading, fees, leverage, and the biggest mistakes to avoid — so you don't have to learn them the hard way.",
        "headings": ["Getting Started on eToro", "Understanding Copy Trading", "Fees You Need to Know About", "The Virtual Practice Account", "Tom's Top Tips for Beginners"],
        "faqs": [
            {"q": "Is eToro good for complete beginners?", "a": "eToro is one of the more beginner-friendly trading platforms due to its copy trading feature, social elements, and clean interface. However, beginners should still understand the risks of CFDs, leverage, and spread fees before depositing real money."},
            {"q": "How does eToro work for beginners?", "a": "eToro allows you to invest in stocks, crypto, and ETFs, or copy the trades of other investors automatically using the CopyTrader feature. You can start with a free virtual practice account before using real money."},
            {"q": "What is the minimum deposit for eToro?", "a": "The minimum deposit on eToro is $50 for most countries (though this varies by region). The minimum to copy a trader is $200."},
        ],
    },
    "YZYgjitj7DM": {
        "slug": "etoro-dangerous-beginner-mistake",
        "keyphrase": "The Most Dangerous eToro Beginner Mistake",
        "h1": "eToro — A Dangerous Beginner Mistake You Need to Avoid",
        "tag": "Beginners guide",
        "description": "Tom reveals the single most common and costly mistake beginners make on eToro — and how to avoid wiping out your account early on.",
        "intro": "Most beginners on eToro make the same mistake — and it often wipes out a significant portion of their account before they realise what's happening. Tom reveals what this mistake is, why it's so easy to fall into, and exactly how to avoid it.",
        "headings": ["The Mistake Most Beginners Make", "Why It's So Easy to Fall Into", "What Happens to Your Account", "The Right Approach Instead", "Tom's Advice"],
        "faqs": [
            {"q": "What is the most common mistake beginners make on eToro?", "a": "The most common beginner mistake is using too much leverage on early trades — chasing big gains with borrowed money. This typically leads to rapid losses that can wipe out a large portion of a new account quickly. The second most common mistake is copying high-risk traders based on short-term returns rather than long-term consistency."},
            {"q": "How do beginners avoid losing money on eToro?", "a": "Start with the virtual practice account, use minimal or zero leverage (set leverage to x1), copy only lower-risk traders with long track records and low drawdowns, and invest only what you can genuinely afford to lose over a long time horizon."},
            {"q": "Is eToro risky for beginners?", "a": "eToro carries real risk, especially for beginners who use leverage or trade CFDs without understanding how they work. The platform itself is legitimate and regulated, but the instruments it offers (particularly CFDs and leveraged positions) are high-risk and most retail traders lose money using them."},
        ],
    },
    "UZ9F2F42vvI": {
        "slug": "etoro-taking-profits-from-copytrading",
        "keyphrase": "Taking Profits from Copy Trading on eToro",
        "h1": "eToro — How and When to Take Profits from Copy Trading",
        "tag": "Copy trading guide",
        "description": "Tom explains the best strategies for taking profits from copy trading on eToro — when to close positions, how to withdraw gains, and what to watch out for.",
        "intro": "Knowing when and how to take profits from copy trading on eToro is just as important as picking the right traders to copy. Tom shares his approach to closing positions, withdrawing gains, and avoiding the common mistakes people make when they finally see their account in profit.",
        "headings": ["When to Take Profits from Copy Trading", "How to Withdraw Gains from eToro", "Partial vs Full Close", "The Tax Consideration", "Tom's Profit-Taking Strategy"],
        "faqs": [
            {"q": "How do you take profits from copy trading on eToro?", "a": "You can take profits by either closing individual copied positions manually, stopping the copy entirely (which closes all positions), or withdrawing your available balance after closing trades. You can also remove funds from a copy to take partial profits without closing the entire copy."},
            {"q": "When should I take profits on eToro?", "a": "There's no universal rule, but common approaches include closing when you've hit a target return (e.g. 20%), rebalancing periodically (e.g. annually), or closing when the trader's risk profile changes significantly. Tom recommends not timing the market but instead having a clear plan before you start copying."},
            {"q": "Can I take partial profits from a copy trade on eToro?", "a": "Yes. You can remove funds from an active copy trade without closing it entirely. Go to your portfolio, open the copy, and select 'Edit'. From there you can reduce the copy amount and any freed-up funds will be returned to your available balance."},
        ],
    },
    # ── More mapped videos ────────────────────────────────────────────────────
    "-qeBPdi5LR8": {
        "slug": "is-etoro-a-scam",
        "keyphrase": "Is eToro a Scam?",
        "h1": "Is eToro a Scam? Will They Steal Your Money?",
        "tag": "Platform review",
        "description": "Tom answers the question directly — is eToro a scam? After years of real deposits, withdrawals and copy trading, here's his answer.",
        "intro": "Is eToro a scam? It's the first question most people ask before putting any money in — and it's exactly the question Tom asked too. After years of real deposits, withdrawals, and copy trading on the platform, here's his first-hand answer.",
        "headings": ["Why People Ask 'Is eToro a Scam'?", "Tom's First Deposit and Withdrawal Test", "How eToro Actually Makes Money", "What Real Users Experience", "Tom's Verdict"],
        "faqs": [
            {"q": "Is eToro a scam?", "a": "No, eToro is not a scam. It is a legitimate, regulated trading platform authorised by the FCA (UK), CySEC (EU), and ASIC (Australia). Tom has personally deposited and withdrawn real money multiple times and can confirm funds are returned as expected."},
            {"q": "Can I trust eToro with my money?", "a": "Yes, eToro is regulated by multiple top-tier financial authorities and has been operating since 2007 with millions of users worldwide. Client funds are held in segregated accounts at tier-1 banks. The bigger risk is not the platform itself but the investments you make on it."},
            {"q": "Has anyone been scammed by eToro?", "a": "eToro itself is not a scam, but scammers sometimes impersonate eToro through fake websites, emails, and social media accounts. Always access eToro only through the official website and never share your login credentials. The FCA has issued warnings about clone firms using eToro's name."},
        ],
    },
    "tHNtskWEV0c": {
        "slug": "etoro-popular-investor-program-requirements",
        "keyphrase": "eToro Popular Investor Program Requirements",
        "h1": "eToro Popular Investor Program — Getting Started and Requirements",
        "tag": "Popular Investor",
        "description": "Tom explains the eToro Popular Investor program requirements — what you need to qualify, how long it takes, and whether it's worth pursuing.",
        "intro": "Becoming an eToro Popular Investor means people copy your trades and eToro pays you based on how much money follows you. Tom explains what the requirements are, how the application process works, and whether the program is realistically worth pursuing.",
        "headings": ["What Is the Popular Investor Program?", "The Requirements to Apply", "How Long Does It Take?", "What Do Popular Investors Earn?", "Is It Worth Pursuing?"],
        "faqs": [
            {"q": "What are the requirements for eToro's Popular Investor program?", "a": "To apply, you need: an active eToro account with equity over $1,000, at least 2 months of trading history, a verified account with real name and photo, a bio of at least 150 characters, and an average risk score of 7 or below for at least 6 months. You also need at least one person copying you."},
            {"q": "How much do eToro Popular Investors earn?", "a": "Popular Investor earnings depend on the tier level and Assets Under Copy (AUC). Higher tiers can earn up to 1.5% of their AUC annually, paid monthly. For example, a Champion-tier Popular Investor with $1 million AUC could earn around $15,000 per year from eToro payments."},
            {"q": "How do I become an eToro Popular Investor?", "a": "Build a strong, consistent track record with a low risk score over at least 6 months. Add a professional photo, real name, and detailed bio. Once you have at least one copier, you can apply through the Popular Investor website. eToro reviews applications within 14 days."},
        ],
    },
    "OFhVWUqzIGA": {
        "slug": "etoro-virtual-practice-account",
        "keyphrase": "eToro Virtual Practice Account Guide",
        "h1": "eToro's Virtual Practice Account — How to Use It",
        "tag": "eToro how-to",
        "description": "Tom walks through eToro's virtual demo account — how to use it, how to copy traders with fake money, and when to switch to real funds.",
        "intro": "Every eToro account comes with a free virtual practice account loaded with $100,000 in fake money. Tom shows you how to make the most of it — practising copy trading, testing strategies, and building confidence before you risk any real money.",
        "headings": ["What Is the eToro Virtual Account?", "How to Switch to the Virtual Account", "Copying Traders with Virtual Money", "The Limitations of the Virtual Account", "When to Switch to Real Money"],
        "faqs": [
            {"q": "What is eToro's virtual practice account?", "a": "eToro's virtual practice account is a simulated trading environment with $100,000 in virtual funds. It mirrors the real platform exactly — you can copy traders, open positions, and test strategies — but no real money is at risk."},
            {"q": "How do I use the virtual account on eToro?", "a": "In the eToro platform, toggle between 'Real' and 'Virtual' portfolio in the left sidebar or settings. All trades and copies in virtual mode use simulated money only. You can switch back to real mode at any time."},
            {"q": "Is the eToro virtual account realistic?", "a": "Yes and no. Prices and platform features are identical to the real account. However, virtual trading removes the psychological pressure of real money — which is actually one of the biggest factors in real trading performance. Use it to learn mechanics, but know that real trading will feel different."},
        ],
    },
    "mbaSu_VQ9bY": {
        "slug": "etoro-stop-copy-explained",
        "keyphrase": "eToro Stop Copy — What Happens When You Stop Copying",
        "h1": "eToro 'Stop Copy' — What Happens to Your Trades?",
        "tag": "Copy trading guide",
        "description": "What actually happens to your open positions when you stop copying a trader on eToro? Tom explains step by step.",
        "intro": "If you decide to stop copying a trader on eToro, all of your copied positions are closed immediately at the current market price. Tom explains exactly what happens, how the funds are returned, and what to think about before you hit that button.",
        "headings": ["What Happens When You Stop a Copy", "Are Positions Closed Immediately?", "What Happens to Your Money", "The Difference Between Stop Copy and Pause Copy", "When Should You Stop a Copy?"],
        "faqs": [
            {"q": "What happens when you stop copying a trader on eToro?", "a": "When you stop copying a trader, all copied positions are closed at the current market price. The resulting cash (profit or loss) is returned to your eToro available balance. This happens immediately when you confirm the stop."},
            {"q": "Can I keep my positions open after stopping a copy on eToro?", "a": "No — stopping a copy on eToro closes all copied positions. If you want to keep specific positions open, you would need to manually open them as separate trades before stopping the copy."},
            {"q": "What's the difference between stop copy and pause copy on eToro?", "a": "Stop Copy closes all positions and ends the copy relationship. Pause Copy keeps existing positions open and running, but new trades by the copied trader will not be mirrored until you unpause."},
        ],
    },
    "n6MRzOyGlUE": {
        "slug": "etoro-short-selling-explained",
        "keyphrase": "Short Selling on eToro — How to Make Money When Prices Fall",
        "h1": "Short Selling on eToro — Profit When Prices Fall",
        "tag": "Trading strategies",
        "description": "Tom explains short selling on eToro in plain English — what it is, how to do it, and the risks involved for beginners.",
        "intro": "Short selling lets you profit when an asset's price falls — but most beginners on eToro don't know it's possible or how it works. Tom explains short selling in plain English: what it is, how to place a short on eToro, and why it's a high-risk strategy that beginners should approach with caution.",
        "headings": ["What Is Short Selling?", "How to Short Sell on eToro", "The Risks of Going Short", "Overnight Fees on Short Positions", "Should Beginners Short Sell on eToro?"],
        "faqs": [
            {"q": "Can you short sell on eToro?", "a": "Yes, you can short sell on eToro by opening a Sell position on any CFD-eligible asset. Short positions profit when the asset price falls. All short positions on eToro are CFDs, which means they incur overnight fees and there is no limit to the loss if the price rises significantly."},
            {"q": "How do you make money when prices fall on eToro?", "a": "Open a Sell (short) position on the asset. If the price falls, your position gains value. For example, if you short an asset at $100 and it falls to $80, your position gains $20 per unit. If the price rises instead, you lose money at the same rate."},
            {"q": "Is short selling risky on eToro?", "a": "Short selling carries unlimited theoretical risk because asset prices can rise without limit. It also incurs overnight fees for every night the position is held. For these reasons, it's considered a high-risk strategy and is not recommended for beginners."},
        ],
    },
    "lSmkRjtoMno": {
        "slug": "etoro-dividends-social-trading",
        "keyphrase": "How to Get Dividends on eToro",
        "h1": "How to Get Dividends on eToro — Social Trading Guide",
        "tag": "eToro income",
        "description": "Tom explains how dividends work on eToro, how to make sure you receive them, and the difference between CFD and non-leveraged positions.",
        "intro": "You can earn dividends from stocks held on eToro — but only if you hold them in the right way. Tom explains how the dividend system works on eToro, the key difference between CFD and real-asset dividends, and how to make sure you're set up to receive them.",
        "headings": ["How Dividends Work on eToro", "CFD Dividends vs Real Asset Dividends", "Which Positions Qualify for Dividends", "How to Check Your Dividend History", "Maximising Dividend Income"],
        "faqs": [
            {"q": "Do you get dividends on eToro?", "a": "Yes. Non-leveraged Buy positions in dividend-paying stocks held as real assets will receive dividends. CFD positions receive a cash adjustment equal to the dividend amount instead. The key is to hold positions at x1 leverage (real shares) to qualify for actual dividends."},
            {"q": "How much dividend do you get on eToro?", "a": "The dividend amount matches the real-world dividend paid by the company, proportional to the number of shares you hold. You can see your dividend history in your portfolio transaction history under 'Dividends'."},
            {"q": "Does copy trading on eToro pay dividends?", "a": "Yes, if the trader you're copying holds dividend-paying stocks as real assets (non-leveraged), your proportional share of those dividends will be credited to your account. Check whether the copied positions are real assets or CFDs to understand what dividend treatment you'll receive."},
        ],
    },
    "Po_WDHWJQtk": {
        "slug": "etoro-copy-trading-fees",
        "keyphrase": "eToro Copy Trading Fees — What Do You Actually Pay?",
        "h1": "eToro Copy Trading Fees — The Full Picture",
        "tag": "eToro fees",
        "description": "Is copy trading on eToro really free? Tom breaks down all the costs — spreads, overnight fees, and what you actually pay when copying traders.",
        "intro": "eToro advertises copy trading as 'free' — but there are still costs involved. Tom breaks down the full picture of what copy trading on eToro actually costs you, covering spread fees, overnight charges, and the situations where costs can quietly build up.",
        "headings": ["Is Copy Trading on eToro Free?", "Spread Fees in Copy Trading", "Overnight Fees on Copied Positions", "The True Cost of Copy Trading", "How to Minimise Copy Trading Costs"],
        "faqs": [
            {"q": "Is copy trading on eToro free?", "a": "Copy trading itself carries no management fee or subscription cost — eToro doesn't charge you extra for using the CopyTrader feature. However, you still pay the same spread fees and overnight fees on copied positions that you would pay if you opened those trades manually."},
            {"q": "What fees do I pay when copy trading on eToro?", "a": "You pay spread fees when positions are opened and closed, and overnight rollover fees if leveraged or short positions are held overnight. If the trader you copy is active with many trades, these fees can accumulate. Low-activity, long-term traders tend to generate lower total fees."},
            {"q": "Are there hidden fees in eToro copy trading?", "a": "No hidden management fees, but overnight fees can catch people off guard. If the trader you're copying holds many leveraged CFD positions long-term, the overnight fees across all those positions add up and can significantly reduce returns. Checking a trader's position types before copying helps."},
        ],
    },
    "yZNrUTMpbS8": {
        "slug": "etoro-minimum-trade-size-risks",
        "keyphrase": "eToro Minimum Trade Sizes — The Risks",
        "h1": "eToro Minimum Trade Sizes and Why They Matter",
        "tag": "Risk management",
        "description": "Tom explains eToro's minimum trade size rules and why they create hidden risks that beginners often don't see until it's too late.",
        "intro": "eToro's minimum trade sizes might seem like a minor technical detail, but they create real risks that catch beginners off guard. Tom explains what the minimums are, why they matter, and the specific situations where they can lead to unexpected losses.",
        "headings": ["eToro's Minimum Trade Size Rules", "Why Minimums Create Hidden Risk", "The Copy Trading Impact", "Real Examples of the Problem", "How to Avoid the Pitfall"],
        "faqs": [
            {"q": "What is the minimum trade size on eToro?", "a": "The minimum trade size on eToro is $1 per position. When copy trading, if a proportional position would be less than $1 based on your copy amount, that trade is simply not opened. This means your portfolio may not fully mirror the trader you're copying."},
            {"q": "How do minimum trade sizes affect copy trading on eToro?", "a": "If your copy amount is small relative to the trader's portfolio, many of their trades may fall below the $1 minimum and won't be copied. This means your copy is less diversified than the original portfolio, which can either increase or decrease your returns relative to the trader's actual performance."},
            {"q": "What is the minimum amount to copy a trader on eToro?", "a": "The minimum to copy a trader on eToro is $200. However, Tom recommends using more than the minimum if you want your copy to accurately track the trader's performance, since small copy amounts mean many positions fall below the $1 minimum trade size and aren't opened."},
        ],
    },
    "ugHCBe5-coQ": {
        "slug": "etoro-copy-trading-blocked-fix",
        "keyphrase": "eToro Copy Trading Blocked — How to Fix It",
        "h1": "eToro 'Copy Trading Blocked' — What It Means and How to Fix It",
        "tag": "eToro troubleshooting",
        "description": "Getting the 'copy trading blocked' error on eToro? Tom shows you exactly what causes it and how to resolve it quickly.",
        "intro": "If you've seen the 'copy trading blocked' message on eToro, you're not alone — it's a common error that confuses a lot of beginners. Tom shows you exactly what causes this message, the different scenarios where it can appear, and how to fix it.",
        "headings": ["What Does 'Copy Trading Blocked' Mean?", "Common Causes of the Error", "How to Fix It — Step by Step", "When eToro Blocks Copying Automatically", "Preventing It From Happening Again"],
        "faqs": [
            {"q": "Why does eToro say copy trading is blocked?", "a": "Copy trading can be blocked for several reasons: the trader has reached their maximum number of copiers, they've voluntarily disabled copying on their account, they're in a region where copying is restricted, or there's a temporary platform issue. Check the trader's profile for any notice about copy availability."},
            {"q": "How do I fix 'copy trading blocked' on eToro?", "a": "First, check if the trader still accepts copiers on their profile page. If copying is temporarily unavailable, you may need to wait or choose a different trader. If the issue seems like a platform error, try refreshing, clearing cache, or contacting eToro support."},
            {"q": "Can all eToro traders be copied?", "a": "No. Traders can opt out of being copied, reach a maximum copier limit, or be restricted from copying in certain regions. Only traders who have opted in and have available copy capacity can be copied. The Popular Investor section shows traders who actively participate in copy trading."},
        ],
    },
    "Gbhfgkhb90s": {
        "slug": "etoro-add-remove-funds-copy-trade",
        "keyphrase": "How to Add or Remove Funds from a Copy Trade on eToro",
        "h1": "eToro: How to Add or Remove Funds from a Copy Trade",
        "tag": "eToro how-to",
        "description": "Step-by-step guide to adding and removing funds from an existing copy trade on eToro, including what happens to open positions.",
        "intro": "One of the most useful but least-known features in eToro copy trading is the ability to add or remove funds from an existing copy without closing it entirely. Tom walks through exactly how to do both — and what happens to your open positions when you do.",
        "headings": ["Adding Funds to an Active Copy Trade", "Removing Funds from a Copy Trade", "What Happens to Open Positions", "Partial Withdrawal vs Closing the Copy", "Step-by-Step Instructions"],
        "faqs": [
            {"q": "How do I add more money to a copy trade on eToro?", "a": "Go to your portfolio, tap on the copy trade, and select 'Edit'. From there you can increase your copy amount. The additional funds will be proportionally distributed across the trader's current open positions."},
            {"q": "How do I remove funds from a copy trade on eToro without closing it?", "a": "Open your portfolio, select the copy trade, and choose 'Edit Copy'. Reduce the copy amount and the difference will be returned to your available balance. Some of the trader's open positions may be partially or fully closed to free up the funds."},
            {"q": "What happens to my open positions when I remove funds from an eToro copy?", "a": "When you reduce your copy amount, eToro may close some of the proportional positions to return funds to your balance. Smaller positions are typically closed first. The copy continues with the reduced amount and the trader's new trades will be mirrored at the new proportional level."},
        ],
    },
}


def slug_from_title(title):
    """Generate a URL-safe slug from a video title (fallback for unmapped videos)."""
    title = re.sub(r'[^a-z0-9\s-]', '', title.lower())
    title = re.sub(r'\s+', '-', title.strip())
    title = re.sub(r'-+', '-', title)
    return title[:60].rstrip('-')


def get_video_id_title_map():
    """Extract all video ID → title pairs from videos.html."""
    content = (BASE_DIR / "videos.html").read_text(encoding="utf-8")
    cards = re.findall(
        r'<a class="vid-card" href="https://www\.youtube\.com/watch\?v=([A-Za-z0-9_-]{11})"[^>]*>.*?<div class="vid-title">(.*?)</div>',
        content, re.DOTALL
    )
    return {vid_id: html.unescape(title).strip() for vid_id, title in cards}


def apply_internal_links(text, current_slug):
    """Replace first occurrence of key terms with internal links (skip self-links)."""
    linked = set()
    def replacer(pattern, url, text):
        if url.rstrip('/').endswith(current_slug):
            return text  # don't self-link
        match = re.search(pattern, text, re.IGNORECASE)
        if not match or pattern in linked:
            return text
        linked.add(pattern)
        term = match.group(0)
        linked_text = f'<a href="{url}">{term}</a>'
        return text[:match.start()] + linked_text + text[match.end():]

    for pattern, url in INTERNAL_LINKS:
        text = replacer(pattern, url, text)
    return text


def format_transcript(text, headings=None):
    """
    Split raw transcript into readable paragraphs with H2 headings.
    Target: ~3-4 sentences per paragraph, heading every ~5 paragraphs.
    Returns list of (type, content) tuples: ('p', text), ('h2', text)
    """
    default_headings = [
        "In This Video",
        "Key Points",
        "What Tom Found",
        "Going Deeper",
        "More Details",
        "Further Thoughts",
        "The Full Picture",
        "Tom's Conclusion",
    ]
    heading_list = headings if headings else default_headings

    text = re.sub(r'\s+', ' ', text.strip())
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'(])', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return [('p', text)]

    paragraphs = []
    chunk = []
    for s in sentences:
        chunk.append(s)
        if len(chunk) >= 4:
            paragraphs.append(' '.join(chunk))
            chunk = []
    if chunk:
        paragraphs.append(' '.join(chunk))

    blocks = []
    heading_idx = 1
    for i, para in enumerate(paragraphs):
        if i > 0 and i % 5 == 0 and heading_idx < len(heading_list):
            blocks.append(('h2', heading_list[heading_idx]))
            heading_idx += 1
        blocks.append(('p', para))

    return blocks


def build_toc(blocks, first_h2):
    """Build a table of contents from H2 headings."""
    h2s = list(dict.fromkeys([first_h2] + [content for typ, content in blocks if typ == 'h2']))
    if len(h2s) < 2:
        return ''
    items = ''
    for heading in h2s:
        anchor = re.sub(r'[^a-z0-9]+', '-', heading.lower()).strip('-')
        items += f'<li><a href="#{anchor}">{html.escape(heading)}</a></li>\n'
    return f'<nav class="toc" aria-label="Contents"><h4>In this article</h4><ul>\n{items}</ul></nav>'


def build_faq_html(faqs):
    """Build FAQ HTML section."""
    items = ''
    for faq in faqs:
        items += f'''    <div class="faq-item">
      <h3 class="faq-q">{html.escape(faq["q"])}</h3>
      <p class="faq-a">{html.escape(faq["a"])}</p>
    </div>\n'''
    return f'<section class="faq-section">\n  <h2>Frequently Asked Questions</h2>\n{items}</section>'


def build_faq_schema(faqs, page_url):
    """Build FAQPage JSON-LD schema."""
    entries = [
        {
            "@type": "Question",
            "name": f["q"],
            "acceptedAnswer": {"@type": "Answer", "text": f["a"]}
        }
        for f in faqs
    ]
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entries}
    return json.dumps(schema, ensure_ascii=False, indent=2)


def generate_page(video_id, title, meta, transcript_text):
    slug = meta["slug"]
    keyphrase = meta["keyphrase"]
    h1 = meta["h1"]
    tag = meta["tag"]
    description = meta["description"]
    intro = meta.get("intro", description)
    headings = meta.get("headings", None)
    faqs = meta.get("faqs", [
        {"q": f"What does Tom cover in this video about {keyphrase}?",
         "a": f"Tom covers {keyphrase.lower()} from a practical, beginner-friendly perspective based on his own real experience on eToro. Watch the full video above or read the transcript below for the complete details."},
        {"q": "Is eToro safe to use?",
         "a": "eToro is a regulated platform authorised by the FCA, CySEC, and ASIC. Tom has personally deposited and withdrawn funds many times. The platform itself is legitimate, but trading CFDs and leveraged instruments carries significant risk — 51% of retail accounts lose money."},
        {"q": "Where can I find more eToro tutorials?",
         "a": "Social Trading Vlog has hundreds of videos covering every aspect of eToro copy trading, fees, popular investors, and more. Browse the full video library or read the written guides on this site."},
    ])

    cta          = CTA_PRESETS.get(meta.get("cta", "main"), CTA_PRESETS["main"])
    cta_url      = cta["url"]
    cta_label    = html.escape(cta["label"])
    cta_headline = html.escape(cta["headline"])
    cta_body     = html.escape(cta["body"])

    canonical = f"https://socialtradingvlog.com/video/{slug}/"
    thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

    # Check for hand-written article content (overrides raw transcript)
    article_sections = meta.get("article_sections", None)

    if article_sections:
        # Build article HTML from structured sections
        transcript_html_parts = []
        blocks = []  # for TOC
        for section in article_sections:
            h2 = section["h2"]
            anchor = re.sub(r'[^a-z0-9]+', '-', h2.lower()).strip('-')
            transcript_html_parts.append(f'<h2 id="{anchor}">{html.escape(h2)}</h2>')
            blocks.append(('h2', h2))
            for para in section["paragraphs"]:
                if isinstance(para, dict) and para.get("type") == "note":
                    transcript_html_parts.append(f'<p class="toms-note">{html.escape(para["text"])}</p>')
                elif isinstance(para, dict) and para.get("type") == "h3":
                    transcript_html_parts.append(f'<h3>{html.escape(para["text"])}</h3>')
                else:
                    linked = apply_internal_links(html.escape(para), slug)
                    transcript_html_parts.append(f'<p>{linked}</p>')
                    blocks.append(('p', para))
        transcript_html = '\n        '.join(transcript_html_parts)
        first_h2 = article_sections[0]["h2"]
        toc_html = build_toc(blocks, first_h2)
    else:
        # Fall back to auto-formatted raw transcript
        first_h2 = headings[0] if headings else "In This Video"
        first_h2_anchor = re.sub(r'[^a-z0-9]+', '-', first_h2.lower()).strip('-')

        blocks = format_transcript(transcript_text, headings)

        transcript_html_parts = [f'<h2 id="{first_h2_anchor}">{html.escape(first_h2)}</h2>']
        for typ, content in blocks:
            if typ == 'h2':
                anchor = re.sub(r'[^a-z0-9]+', '-', content.lower()).strip('-')
                transcript_html_parts.append(f'<h2 id="{anchor}">{html.escape(content)}</h2>')
            else:
                linked = apply_internal_links(html.escape(content), slug)
                transcript_html_parts.append(f'<p>{linked}</p>')
        transcript_html = '\n        '.join(transcript_html_parts)

        toc_html = build_toc(blocks, first_h2)

    # FAQ section
    faq_html = build_faq_html(faqs)
    faq_schema = build_faq_schema(faqs, canonical)

    # Schemas
    video_schema = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": h1,
        "description": description,
        "thumbnailUrl": thumbnail,
        "embedUrl": f"https://www.youtube.com/embed/{video_id}",
        "uploadDate": "2024-01-01",
        "publisher": {"@type": "Organization", "name": "Social Trading Vlog", "url": "https://socialtradingvlog.com"}
    }
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://socialtradingvlog.com"},
            {"@type": "ListItem", "position": 2, "name": "Videos", "item": "https://socialtradingvlog.com/videos.html"},
            {"@type": "ListItem", "position": 3, "name": h1, "item": canonical},
        ]
    }

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{html.escape(description)}" />
  <meta property="og:title" content="{html.escape(keyphrase)} | SocialTradingVlog" />
  <meta property="og:description" content="{html.escape(description)}" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="{thumbnail}" />
  <link rel="canonical" href="{canonical}" />
  <title>{html.escape(keyphrase)} | SocialTradingVlog</title>
  <link rel="stylesheet" href="../../css/style.css" />
  <script type="application/ld+json">
  {json.dumps(video_schema, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
  {faq_schema}
  </script>
  <script type="application/ld+json">
  {json.dumps(breadcrumb_schema, ensure_ascii=False, indent=2)}
  </script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-PBGDJ951LL"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-PBGDJ951LL');
  </script>
</head>
<body>

  <nav>
    <div class="container nav-inner">
      <a href="../../index.html" class="nav-logo">Social<span>Trading</span>Vlog</a>
      <ul class="nav-links">
        <li><a href="../../social-trading.html">Social Trading</a></li>
        <li><a href="../../copy-trading.html">Copy Trading</a></li>
        <li><a href="../../updates.html">Updates</a></li>
        <li><a href="../../videos.html">Videos</a></li>
        <li><a href="../../about.html">About</a></li>
        <li><a href="../../faq.html">FAQ</a></li>
        <li><a href="#etoro-cta" class="nav-cta">Try eToro</a></li>
      </ul>
      <button class="nav-hamburger" id="nav-hamburger" aria-label="Open navigation" aria-expanded="false" aria-controls="nav-drawer">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
  <div class="nav-drawer" id="nav-drawer" role="navigation" aria-label="Mobile navigation">
    <ul>
      <li><a href="../../social-trading.html">Social Trading</a></li>
      <li><a href="../../copy-trading.html">Copy Trading</a></li>
      <li><a href="../../updates.html">Updates</a></li>
      <li><a href="../../videos.html">Videos</a></li>
      <li><a href="../../about.html">About</a></li>
      <li><a href="../../faq.html">FAQ</a></li>
      <li><a href="#etoro-cta" class="nav-cta">Try eToro</a></li>
    </ul>
  </div>

  <div class="risk-warning-banner">
    <span>Risk warning:</span> 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk.
  </div>

  <div class="article-hero">
    <div class="container">
      <div class="article-tag">{html.escape(tag)}</div>
      <h1>{html.escape(h1)}</h1>
      <p class="article-meta">By Tom &nbsp;·&nbsp; Social Trading Vlog</p>
    </div>
  </div>

  <div class="container">
    <div class="article-body">

      <article class="article-content">

        <img
          src="{thumbnail}"
          alt="{html.escape(h1)}"
          style="width:100%;height:auto;border-radius:8px;margin:0 0 24px;display:block;"
          loading="eager"
          width="480" height="270"
        >

        <p class="article-intro">{html.escape(intro)}</p>

        {toc_html}

        <div class="video-embed">
          <iframe
            src="https://www.youtube.com/embed/{video_id}"
            title="{html.escape(h1)}"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
            loading="lazy">
          </iframe>
        </div>
        <p style="font-size:0.85rem;color:var(--muted);margin-top:-8px;margin-bottom:24px;">
          Prefer reading? The full transcript is below. &nbsp;·&nbsp;
          <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" rel="noopener">Watch on YouTube with captions</a>
        </p>

        <div class="risk-warning">
          <strong>Risk Warning</strong>
          eToro is a multi-asset investment platform. The value of your investments may go up or down. 51% of retail investor accounts lose money when trading CFDs with eToro. You should consider whether you can afford to take the high risk of losing your money.
        </div>

        <div class="inline-cta">
          <p class="inline-cta-text">{cta_headline} — Tom's affiliate link.</p>
          <a href="{cta_url}" class="btn btn-primary" target="_blank" rel="noopener sponsored">{cta_label} →</a>
        </div>

        {transcript_html}

        {faq_html}

        <div class="risk-warning">
          <strong>Important Reminder</strong>
          51% of retail investor accounts lose money when trading CFDs with eToro. You should consider whether you can afford to take the high risk of losing your money. Past performance is not an indication of future results. This content is for educational purposes only and is not investment advice.
        </div>

      </article>

      <aside class="article-sidebar">
        <div class="sidebar-cta" id="etoro-cta">
          <h3>{cta_headline}</h3>
          <p>{cta_body}</p>
          <a href="{cta_url}" class="btn btn-primary" target="_blank" rel="noopener sponsored">{cta_label} →</a>
          <div class="risk-warning">
            <strong>51% of retail investor accounts lose money when trading CFDs with eToro.</strong>
            You should consider whether you can afford to take the high risk of losing your money. This is an affiliate link — Tom may earn a commission at no cost to you.
          </div>
        </div>
        <div class="sidebar-nav">
          <h4>More guides</h4>
          <ul>
            <li><a href="../../social-trading.html">What is Social Trading?</a></li>
            <li><a href="../../copy-trading.html">What is Copy Trading?</a></li>
            <li><a href="../../copy-trading-returns.html">How Much Can You Make?</a></li>
            <li><a href="../../etoro-scam.html">Is eToro a Scam?</a></li>
            <li><a href="../../taking-profits.html">Taking Profits</a></li>
            <li><a href="../../popular-investor.html">Popular Investor Program</a></li>
            <li><a href="../../videos.html">All Videos</a></li>
          </ul>
        </div>
      </aside>

    </div>
  </div>

  <footer>
    <div class="container">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="nav-logo">Social<span style="color:var(--accent)">Trading</span>Vlog</div>
          <p>Documenting the copy trading journey since 2017. Independent, honest, and always learning.</p>
        </div>
        <div class="footer-col">
          <h4>Guides</h4>
          <ul>
            <li><a href="../../social-trading.html">What is Social Trading?</a></li>
            <li><a href="../../copy-trading.html">What is Copy Trading?</a></li>
            <li><a href="../../etoro-scam.html">Is eToro a Scam?</a></li>
            <li><a href="../../copy-trading-returns.html">How Much Can You Make?</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Site</h4>
          <ul>
            <li><a href="../../updates.html">Trading Updates</a></li>
            <li><a href="../../about.html">About</a></li>
            <li><a href="../../faq.html">FAQ</a></li>
            <li><a href="../../contact.html">Contact</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 SocialTradingVlog.com</p>
        <p class="footer-disclaimer">Your capital is at risk. 51% of retail investor accounts lose money when trading CFDs with eToro. This website is for educational and informational purposes only and does not constitute investment advice. Copy Trading does not amount to investment advice.</p>
      </div>
    </div>
  </footer>

  <script src="../../js/lightbox.js"></script>
  <script src="../../js/nav.js"></script>
  <script>
  document.addEventListener('click', function(e) {{
    var link = e.target.closest('a.btn-primary');
    if (!link) return;
    if (typeof gtag === 'function') {{
      gtag('event', 'cta_click', {{
        'event_category': 'affiliate',
        'event_label': link.textContent.trim(),
        'link_url': link.href || '',
        'page_path': location.pathname
      }});
    }}
  }});
  </script>
</body>
</html>'''

    return page


def get_meta_for_video(video_id, title):
    """Return keyword meta — use mapping if available, else generate from title."""
    if video_id in KEYWORD_MAP:
        meta = dict(KEYWORD_MAP[video_id])
    else:
        slug = slug_from_title(title)
        meta = {
            "slug": slug,
            "keyphrase": title,
            "h1": title,
            "tag": "Copy trading video",
            "description": f"Tom's video: {title}. Watch with full transcript on Social Trading Vlog.",
            "intro": f"In this video, Tom covers {title.lower()} — sharing his personal experience from years of copy trading on eToro.",
        }
    meta["cta"] = VIDEO_CTA_MAP.get(video_id, "main")
    return meta


def main():
    parser = argparse.ArgumentParser(description="Generate video landing pages")
    parser.add_argument("--video-id", help="Generate page for a single video ID only")
    parser.add_argument("--force", action="store_true", help="Regenerate even if page already exists")
    args = parser.parse_args()

    video_titles = get_video_id_title_map()
    target_ids = [args.video_id] if args.video_id else list(video_titles.keys())

    VIDEO_DIR.mkdir(exist_ok=True)
    generated = skipped = no_transcript = 0

    pending_approval = 0

    for video_id in target_ids:
        title = video_titles.get(video_id, f"Video {video_id}")
        transcript_path = TRANS_DIR / video_id / "transcript.txt"

        if not transcript_path.exists():
            no_transcript += 1
            continue

        meta = get_meta_for_video(video_id, title)

        # Only generate pages that Tom has approved for publication
        if not meta.get("approved"):
            pending_approval += 1
            continue

        out_dir = VIDEO_DIR / meta["slug"]
        out_path = out_dir / "index.html"

        if out_path.exists() and not args.force:
            skipped += 1
            continue

        transcript_text = transcript_path.read_text(encoding="utf-8")
        if len(transcript_text.strip()) < 100:
            print(f"  Skipping {video_id} — transcript too short")
            no_transcript += 1
            continue

        out_dir.mkdir(exist_ok=True)
        out_path.write_text(generate_page(video_id, title, meta, transcript_text), encoding="utf-8")
        print(f"  [{video_id}] → /video/{meta['slug']}/")
        generated += 1

    print(f"\nDone: {generated} generated, {skipped} skipped, {pending_approval} pending approval, {no_transcript} waiting for transcript")
    if generated > 0:
        print("Run with --force to regenerate existing pages.")


if __name__ == "__main__":
    main()
