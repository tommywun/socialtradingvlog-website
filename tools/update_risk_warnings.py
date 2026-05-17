#!/usr/bin/env python3
"""
Update Risk Warnings — mirrors eToro's official CFD risk percentage across the site.

Design (rebuilt 2026-05-17 — see CLAUDE.md "eToro risk percentage updater"):

  * TARGET ("new")  = eToro's current scraped figure, read from
    data/etoro-risk-warning.json["percentage"] (written by scrape_etoro_risk.py),
    or overridden with --target N.
  * OLD             = whatever the *live HTML* actually contains. We never trust
    JSON history deltas to decide what to replace — that was the bug that froze
    the site at a stale 50% (a JSON/HTML mismatch produced "0 replacements" and
    a silent exit 0). HTML is ground truth.
  * We match the *regulatory disclaimer phrase itself*, per language, and rewrite
    its leading number to the target — UNLESS the number is hedged by an
    approximation word ("around 76% ... only 24% profitable"), which is editorial
    prose, not the compliance line, and must never be touched.
  * Loud failure: any scrape problem, stale-pattern (zero anchored matches), or
    "a change is needed but 0 were applied" sends a Telegram alert and exits 1.
    A silent no-op is never treated as success again.

This script never writes the JSON (single writer = scrape_etoro_risk.py), which
removes the coupling that caused the local/VPS split-brain.

Usage:
    python3 tools/update_risk_warnings.py --dry-run     # list every change + skip
    python3 tools/update_risk_warnings.py --no-commit    # apply files, no git
    python3 tools/update_risk_warnings.py                # apply + commit + push
    python3 tools/update_risk_warnings.py --target 52    # override target

Cron chain (monthly):
    scrape_etoro_risk.py && update_risk_warnings.py
"""

import sys
import os
import re
import json
import pathlib
import subprocess
import argparse
from datetime import datetime

PROJECT_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
RISK_FILE = DATA_DIR / "etoro-risk-warning.json"

# Sanity bounds for the official figure.
MIN_SANE = 30
MAX_SANE = 90

# The regulatory disclaimer phrase, per language. Group 1 = the number; the rest
# is preserved verbatim so spacing ("50 % der" vs "50% of") and the FR apostrophe
# variants are never disturbed. These anchors are specific enough that unrelated
# percentages ("50% discount", "50% per month", "76%... 24% profitable") cannot
# match by phrase alone.
DISCLAIMER_RE = re.compile(
    r"(\d+)(\s*%\s*(?:"
    r"of\s+retail\s+investor\s+accounts"                              # EN
    r"|der\s+Privatanlegerkonten"                                     # DE
    r"|de\s+las\s+cuentas\s+de\s+inversores\s+minoristas"             # ES
    r"|des\s+comptes\s+d(?:&#x27;|&#39;|'|’|\s)?investisseurs\s+particuliers"  # FR
    r"|das\s+contas\s+de\s+investidores\s+de\s+varejo"                # PT
    r"|من\s+حسابات\s+المستثمرين\s+الأفراد"  # AR من حسابات المستثمرين الأفراد
    r"))",
    re.IGNORECASE | re.UNICODE,
)

# If one of these approximation words appears just before the number, this is
# editorial prose ("around 76% ...", "etwa 76% ...", "حوالي 76% ..."), NOT the
# compliance disclaimer — leave it exactly as-is.
HEDGE_RE = re.compile(
    r"(?:around|roughly|approximately|about|nearly|some|circa|~|"          # EN
    r"etwa|ungefähr|ungefaehr|rund|ca\.?|"                                 # DE
    r"alrededor(?:\s+de[l]?)?|aproximadamente|cerca\s+de|casi|en\s+torno|" # ES
    r"aproximadamente|cerca\s+de|em\s+torno|por\s+volta|quase|"            # PT
    r"environ|prè?s\s+de|autour\s+de|à\s+peu\s+près|quelque|"              # FR
    r"حوالي|تقريبا|نحو|قرابة"  # AR  approx. words
    r")\s*(?:de[l]?\s*)?$",
    re.IGNORECASE | re.UNICODE,
)

HEDGE_WINDOW = 32  # chars of left-context inspected for a hedge word


def send_telegram(subject, body, emoji="\U0001F4CA"):
    try:
        sys.path.insert(0, str(PROJECT_DIR / "tools"))
        from security_lib import send_telegram as _send
        _send(subject, body, emoji=emoji)
    except Exception as e:
        print(f"  Telegram alert failed: {e}")


def fail(subject, body):
    """Loud failure: alert + non-zero exit. Never a silent no-op."""
    print(f"\n  FAIL: {subject}\n  {body}")
    send_telegram(f"Risk Updater FAILED — {subject}", body, emoji="⚠️")
    sys.exit(1)


def run_git(*args):
    return subprocess.run(
        ["git"] + list(args), cwd=str(PROJECT_DIR),
        capture_output=True, text=True, timeout=60,
    )


def read_target(override):
    if override is not None:
        return override
    if not RISK_FILE.exists():
        fail("no scraped data",
             "data/etoro-risk-warning.json missing. Run scrape_etoro_risk.py "
             "first (it reads eToro's live figure).")
    try:
        pct = int(json.loads(RISK_FILE.read_text())["percentage"])
    except Exception as e:
        fail("bad scraped data", f"Could not read percentage from {RISK_FILE}: {e}")
    return pct


def find_html_files():
    files = []
    for root, _dirs, names in os.walk(str(PROJECT_DIR)):
        rel = os.path.relpath(root, str(PROJECT_DIR))
        if any(skip in rel for skip in ("node_modules", "venv", ".git",
                                        "backups", "tools/archive")):
            continue
        for n in names:
            if n.endswith(".html"):
                files.append(pathlib.Path(root) / n)
    return files


def classify(content, m):
    """Return 'editorial' if the matched number is hedged, else 'official'."""
    left = content[max(0, m.start(1) - HEDGE_WINDOW): m.start(1)]
    return "editorial" if HEDGE_RE.search(left) else "official"


def process_file(filepath, target, apply):
    """Return (changes, skips) lists of (line, old, snippet)."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return [], []

    changes, skips = [], []

    def line_of(idx):
        return content.count("\n", 0, idx) + 1

    def repl(m):
        kind = classify(content, m)
        val = int(m.group(1))
        snippet = m.group(0)[:60]
        ln = line_of(m.start(1))
        if kind == "editorial":
            skips.append((ln, val, snippet))
            return m.group(0)
        if val == target:
            return m.group(0)  # already correct, nothing to do
        changes.append((ln, val, snippet))
        return f"{target}{m.group(2)}"

    new_content = DISCLAIMER_RE.sub(repl, content)

    if apply and changes:
        filepath.write_text(new_content, encoding="utf-8")
    return changes, skips


def main():
    ap = argparse.ArgumentParser(description="Mirror eToro's official risk % across the site")
    ap.add_argument("--dry-run", action="store_true", help="List every change/skip; write nothing")
    ap.add_argument("--no-commit", action="store_true", help="Apply file edits but skip git commit/push")
    ap.add_argument("--target", type=int, help="Override the target percentage (testing/manual)")
    args = ap.parse_args()

    print(f"Risk Warning Updater — {datetime.now():%Y-%m-%d %H:%M}")
    print("=" * 60)

    target = read_target(args.target)
    if not (MIN_SANE <= target <= MAX_SANE):
        fail("target out of range",
             f"Target {target}% outside sane bounds ({MIN_SANE}-{MAX_SANE}). "
             "Refusing to touch the site. Check scraper output.")
    print(f"  Target (eToro official): {target}%\n")

    apply = not args.dry_run
    total_changes = total_skips = files_changed = matched_any = 0
    current_values = {}

    for fp in find_html_files():
        changes, skips = process_file(fp, target, apply)
        matched_any += len(changes) + len(skips)
        for ln, val, _snip in changes + skips:
            current_values[val] = current_values.get(val, 0) + 1
        if changes:
            files_changed += 1
            total_changes += len(changes)
            rel = fp.relative_to(PROJECT_DIR)
            for ln, val, snip in changes:
                print(f"  CHANGE {rel}:{ln}  {val}% -> {target}%   {snip!r}")
        for ln, val, snip in skips:
            total_skips += 1
            rel = fp.relative_to(PROJECT_DIR)
            print(f"  SKIP   {rel}:{ln}  {val}% (editorial/hedged — left as-is)   {snip!r}")

    # --- Stale-pattern guard: phrasing changed, our anchors no longer match ---
    if matched_any == 0:
        fail("no disclaimer matches",
             "Zero regulatory-disclaimer phrases matched site-wide. The page "
             "wording or DISCLAIMER_RE is stale — NOT silently doing nothing.")

    print(f"\n  Anchored figures found: " +
          ", ".join(f"{v}%×{c}" for v, c in sorted(current_values.items())))
    print(f"  Changes: {total_changes} across {files_changed} files | "
          f"Editorial skipped: {total_skips}")

    needed = sum(c for v, c in current_values.items() if v != target) - total_skips

    if args.dry_run:
        print("  Dry run — nothing written.")
        return

    # --- Silent-no-op guard: a change was due but none applied ---
    if needed > 0 and total_changes == 0:
        fail("change due but none applied",
             f"{needed} non-target official disclaimers exist but 0 were "
             f"replaced. Anchor/encoding mismatch — investigate, do not ignore.")

    if total_changes == 0:
        print(f"  Site already at {target}% — nothing to do.")
        return

    if args.no_commit:
        print("  --no-commit: files updated, git untouched (awaiting sign-off).")
        return

    run_git("add", "-A")
    diff = run_git("diff", "--cached", "--name-only")
    if not diff.stdout.strip():
        fail("nothing staged", "Files were edited but git sees no change — investigate.")

    msg = (f"Update eToro risk disclaimer to {target}% (compliance-mandated)\n\n"
           f"{files_changed} files, {total_changes} replacements. "
           f"Editorial mentions ({total_skips}) left intact.")
    if run_git("commit", "-m", msg).returncode != 0:
        fail("git commit failed", "Edits applied but commit failed. Resolve manually.")
    print(f"  Committed: {msg.splitlines()[0]}")

    push = run_git("push")
    if push.returncode == 0:
        print("  Pushed.")
        send_telegram("Risk Warning Updated on Live Site",
                      f"eToro CFD risk % mirrored to {target}%.\n"
                      f"{files_changed} files, {total_changes} replacements.",
                      emoji="✅")
    else:
        send_telegram("Risk Warning Committed — Push Needed",
                      f"Committed locally ({target}%), push failed:\n"
                      f"{push.stderr.strip()[:300]}", emoji="⚠️")
        print(f"  Push failed: {push.stderr.strip()}")


if __name__ == "__main__":
    main()
