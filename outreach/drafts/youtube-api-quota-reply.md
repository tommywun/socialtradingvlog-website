# YouTube API Quota Increase — Draft Reply to Google

**Subject:** Re: YouTube Data API Quota Increase Request — SocialTradingVlog

---

Hi,

Thanks for getting back to me. Here's the information you've asked for.

## YouTube Channel

**https://youtube.com/socialtrading**

- 333 published videos (social/copy trading education, recorded since 2017)
- ~66,000 subscribers, ~4.5 million total views
- Active channel — I still publish regularly

## What I'm Building (Subtitle Translation Pipeline)

I'm adding translated subtitles to all 333 of my videos so non-English speakers can watch them in their own language. Right now, most of my audience is English-speaking, but the topics I cover (eToro, copy trading) are relevant in many countries where eToro operates.

### The process, step by step:

1. **Transcribe**: Each video's audio is transcribed to English using OpenAI's Whisper API, producing an SRT subtitle file with accurate timestamps.

2. **Translate**: The English SRT is translated into 9 languages using Google Translate — Spanish, German, French, Italian, Portuguese, Arabic, Polish, Dutch, and Korean. These are the countries where eToro (the platform I cover) is most popular.

3. **Upload to YouTube**: The translated SRT files are uploaded to each video via the YouTube Data API v3 `captions.insert` endpoint. The script checks for existing captions first (`captions.list`) and updates rather than duplicates.

### Why I need more quota

Each subtitle upload uses approximately 400 API units (captions.insert = 400 units). With 333 videos × 9 languages = ~2,997 subtitle tracks to upload, that's roughly 1.2 million units total.

At the default 10,000 units/day, it would take around 120 days just to upload the subtitles — and that's without any headroom for checking existing captions or handling retries.

With 50,000 units/day, I could complete the upload in a reasonable timeframe (~24 days) and have room for the ongoing maintenance as I publish new videos.

### The code

The upload script is straightforward — it:
- Scans a local `transcriptions/` directory for SRT files
- Authenticates via OAuth 2.0 (youtube.force-ssl scope)
- For each video, calls `captions.list` to check existing tracks
- Calls `captions.insert` for new subtitle tracks (or `captions.update` for existing ones)
- Logs each upload to avoid duplicates on re-runs
- Respects rate limits with a 0.5s delay between uploads
- Stops gracefully if quota is exceeded (safe to re-run later)

I'm not using the API for anything else — no bulk video uploads, no scraping, no automation beyond adding subtitles to my own content.

Happy to provide any further detail or a screen recording if needed.

Best,
Tom West
SocialTradingVlog
https://socialtradingvlog.com
https://youtube.com/socialtrading
