#!/usr/bin/env python3
"""
_risk_disclaimer.py — the ONE place that knows how to find and rewrite the
eToro CFD risk-disclaimer percentage. Read this before touching the figure
anywhere.

────────────────────────────────────────────────────────────────────────────
WHY THIS MODULE EXISTS (read me — you will otherwise be confused)
────────────────────────────────────────────────────────────────────────────
eToro requires the line "<N>% of retail investor accounts lose money when
trading CFDs with eToro" (and its es/de/fr/pt/ar translations) on every page.
N changes when eToro updates it (was 51 → 50 → 52 as of 2026-05-17).

That number used to be hand-hardcoded in HUNDREDS of places: every generated
HTML page, every generator template, and ~25 localized translation-source
files. Hardcoded duplication always drifts — and it did: the site sat on a
stale 50% for months while eToro showed 52%, and 8 German pages were stranded
at 51%.

The fix has TWO layers and this module is the shared core of both:

  1. LIVE STATIC HTML  → `update_risk_warnings.py` (monthly cron + on demand)
       Scans the already-published .html files and rewrites the figure.
       Safety net for pages that already exist on disk.

  2. PAGE GENERATION   → `generate_article_pages.py`, `generate_video_pages.py`,
       `generate_translated_pages.py` each pass their output through
       `normalize_html()` immediately before writing. So a freshly generated
       page is correct BY CONSTRUCTION, regardless of what literal the
       generator's template happens to contain.

⚠️  CONSEQUENCE FOR FUTURE READERS: the generators and the
    tools/translations/* files STILL CONTAIN A STALE HARDCODED "51%" in the
    disclaimer strings. THIS IS DELIBERATE AND HARMLESS. Do NOT "helpfully"
    find-and-replace those literals — they are overwritten at write time by
    normalize_html(). Editing them does nothing useful and risks corrupting
    the editorial "76%" prose (see below). The single source of truth for the
    real number is `data/etoro-risk-warning.json` (written by
    scrape_etoro_risk.py), with a live-HTML fallback. Change the figure THERE,
    nowhere else.

────────────────────────────────────────────────────────────────────────────
THE ONE SUBTLETY: editorial "76%" must never be touched
────────────────────────────────────────────────────────────────────────────
The "why most eToro traders lose money" video article contains EDITORIAL prose
like "around 76% of retail investor accounts lose money ... only 24% are
profitable". That sentence contains the exact regulatory phrase but is NOT the
compliance disclaimer — it's commentary about a historical/peak figure. It is
distinguished by an approximation word ("around / etwa / حوالي / alrededor")
right before the number. `HEDGE_RE` detects that and such matches are
classified "editorial" and left exactly as-is. Replacing them would both
corrupt the article and make it nonsensical (52% + 24% ≠ 100%).

This regex + hedge logic was validated against 1016 live disclaimer
occurrences + 8 editorial ones across all 6 languages (2026-05-17) — do not
weaken it without re-validating.
────────────────────────────────────────────────────────────────────────────
"""

import re
import json
import pathlib
import functools

PROJECT_DIR = pathlib.Path(__file__).parent.parent
RISK_FILE = PROJECT_DIR / "data" / "etoro-risk-warning.json"

# Plausible bounds for the official figure. Anything outside this is treated as
# a scrape error / corruption and refused — never silently written to the site.
MIN_SANE = 30
MAX_SANE = 90

# The regulatory disclaimer phrase, per language. Group 1 = the number; the
# rest is preserved verbatim so spacing ("50 % der" vs "50% of") and the FR
# apostrophe variants are never disturbed. These anchors are specific enough
# that unrelated percentages ("50% discount", "50% per month") cannot match.
DISCLAIMER_RE = re.compile(
    r"(\d+)(\s*%\s*(?:"
    r"of\s+retail\s+investor\s+accounts"                              # EN
    r"|der\s+Privatanlegerkonten"                                     # DE
    r"|de\s+las\s+cuentas\s+de\s+inversores\s+minoristas"             # ES
    r"|des\s+comptes\s+d(?:&#x27;|&#39;|'|’|\s)?investisseurs\s+particuliers"  # FR
    r"|das\s+contas\s+de\s+investidores\s+de\s+varejo"                # PT
    r"|من\s+حسابات\s+المستثمرين\s+الأفراد"  # AR
    r"))",
    re.IGNORECASE | re.UNICODE,
)

# An approximation word immediately before the number ⇒ editorial prose, NOT
# the compliance disclaimer ⇒ leave it exactly as-is (see module docstring).
HEDGE_RE = re.compile(
    r"(?:around|roughly|approximately|about|nearly|some|circa|~|"          # EN
    r"etwa|ungefähr|ungefaehr|rund|ca\.?|"                                 # DE
    r"alrededor(?:\s+de[l]?)?|aproximadamente|cerca\s+de|casi|en\s+torno|" # ES
    r"aproximadamente|cerca\s+de|em\s+torno|por\s+volta|quase|"            # PT
    r"environ|prè?s\s+de|autour\s+de|à\s+peu\s+près|quelque|"              # FR
    r"حوالي|تقريبا|نحو|قرابة"  # AR
    r")\s*(?:de[l]?\s*)?$",
    re.IGNORECASE | re.UNICODE,
)

HEDGE_WINDOW = 32  # chars of left-context inspected for a hedge word


def classify(text, m):
    """'editorial' if the matched number is hedged, else 'official'."""
    left = text[max(0, m.start(1) - HEDGE_WINDOW): m.start(1)]
    return "editorial" if HEDGE_RE.search(left) else "official"


def analyze(text):
    """Yield (match, kind, value) for every disclaimer-phrase match in text.

    Used by update_risk_warnings.py for its line-numbered CHANGE/SKIP report.
    """
    for m in DISCLAIMER_RE.finditer(text):
        yield m, classify(text, m), int(m.group(1))


def normalize(text, target):
    """Rewrite every OFFICIAL disclaimer figure in `text` to `target`.

    Editorial (hedged) occurrences are left untouched. Returns
    (new_text, n_changed, n_skipped). This is the single transformation used
    by BOTH the live-HTML updater and every page generator.
    """
    changed = skipped = 0

    def repl(m):
        nonlocal changed, skipped
        if classify(text, m) == "editorial":
            skipped += 1
            return m.group(0)
        if int(m.group(1)) == target:
            return m.group(0)
        changed += 1
        return f"{target}{m.group(2)}"

    return DISCLAIMER_RE.sub(repl, text), changed, skipped


def normalize_html(html, target=None):
    """Convenience wrapper for generators: normalize and return ONLY the html.

    `target` defaults to current_target(). Safe to call on any page output —
    pages with no disclaimer phrase pass through unchanged.
    """
    if target is None:
        target = current_target()
    new_html, _c, _s = normalize(html, target)
    return new_html


def html_target():
    """Fallback source of truth: the dominant non-hedged disclaimer figure
    actually live in the site's HTML. Used when the JSON is missing/insane so
    generators can never re-introduce the local/VPS JSON split-brain.
    """
    tally = {}
    for p in PROJECT_DIR.rglob("*.html"):
        if any(s in p.parts for s in ("node_modules", "venv", "backups")):
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for _m, kind, val in analyze(txt):
            if kind == "official":
                tally[val] = tally.get(val, 0) + 1
    return max(tally, key=tally.get) if tally else None


@functools.lru_cache(maxsize=1)
def current_target():
    """The official figure. JSON (scrape_etoro_risk.py's output) first; if
    missing or out of sane bounds, fall back to the live-HTML mode. Raises
    RuntimeError if neither yields a sane value — callers must NOT guess.

    Cached: the figure cannot change within a single run, so generators that
    call this once per page pay the (tiny) cost only once.
    """
    if RISK_FILE.exists():
        try:
            pct = int(json.loads(RISK_FILE.read_text())["percentage"])
            if MIN_SANE <= pct <= MAX_SANE:
                return pct
        except Exception:
            pass
    pct = html_target()
    if pct is not None and MIN_SANE <= pct <= MAX_SANE:
        return pct
    raise RuntimeError(
        "Cannot determine the official eToro risk %: data/etoro-risk-warning.json "
        "is missing/insane AND no sane figure found in live HTML. Run "
        "scrape_etoro_risk.py. Refusing to guess."
    )
