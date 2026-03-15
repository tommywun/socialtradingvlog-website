"""
Shared configuration for the subtitle pipeline.

Used by: run_pipeline.py, translate_subtitles.py, upload_subtitles.py
"""

# The 9 languages we translate to (ordered by market priority)
# NOTE: eToro is BLOCKED in Russia, Japan, India, China, Turkey — those
# languages excluded.
PIPELINE_LANGUAGES = [
    "es",   # Spanish — Spain, Latin America
    "de",   # German — Germany, Austria, Switzerland
    "fr",   # French — France
    "it",   # Italian — Italy
    "pt",   # Portuguese — Portugal, Brazil
    "ar",   # Arabic — UAE, Saudi, Kuwait
    "pl",   # Polish — Poland
    "nl",   # Dutch — Netherlands
    "ko",   # Korean — South Korea
]

# Full language names
LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "de": "German",
    "fr": "French",
    "it": "Italian",
    "pt": "Portuguese",
    "ar": "Arabic",
    "nl": "Dutch",
    "pl": "Polish",
    "ko": "Korean",
}

# SRT language code → YouTube API language code
YOUTUBE_LANG_MAP = {
    "en": "en",
    "es": "es",
    "de": "de",
    "fr": "fr",
    "pt": "pt",
    "ar": "ar",
    "nl": "nl",
    "pl": "pl",
    "ko": "ko",
    "it": "it",
}
