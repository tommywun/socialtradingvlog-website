#!/usr/bin/env python3
"""
Update Risk Warnings — propagates eToro percentage changes across the site.

After scrape_etoro_risk.py detects a change in the CFD risk percentage,
this script finds every HTML file containing the old percentage in a
risk-warning context and replaces it with the new value. Then commits
and pushes (or alerts Tom if push fails).

Usage:
    python3 tools/update_risk_warnings.py              # Update + commit
    python3 tools/update_risk_warnings.py --dry-run    # Show what would change

Chain after scraper in cron:
    30 1 * * 1  PYTHON scrape_etoro_risk.py && PYTHON update_risk_warnings.py
"""

import sys
import os
import json
import re
import pathlib
import subprocess
import argparse
from datetime import datetime

PROJECT_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
RISK_FILE = DATA_DIR / "etoro-risk-warning.json"

# Context words that must appear near the percentage to confirm it's a
# risk warning (not some random "51%" in unrelated text).
# Covers EN, DE, ES, FR, PT, AR translations.
CONTEXT_WORDS = [
    "retail",
    "cfd",
    "lose money",
    "verlieren geld",    # DE
    "pierden dinero",    # ES
    "perdem dinheiro",   # PT
    "perdent de l'argent",  # FR
    "يخسرون",            # AR (lose)
    "capital is at risk",
    "capital at risk",
    "high risk",
    "risque",            # FR
    "riesgo",            # ES
    "risco",             # PT
    "risiko",            # DE
]

# Sanity bounds
MIN_SANE = 30
MAX_SANE = 90


def send_telegram(subject, body, emoji="📊"):
    """Send alert via security_lib."""
    try:
        sys.path.insert(0, str(PROJECT_DIR / "tools"))
        from security_lib import send_telegram as _send
        _send(subject, body, emoji=emoji)
    except Exception as e:
        print(f"  Telegram alert failed: {e}")


def run_git(*args):
    """Run a git command in the project directory."""
    result = subprocess.run(
        ["git"] + list(args),
        cwd=str(PROJECT_DIR),
        capture_output=True, text=True, timeout=30
    )
    return result


def load_data():
    """Load risk warning data."""
    if not RISK_FILE.exists():
        print("ERROR: data/etoro-risk-warning.json not found.")
        print("Run scrape_etoro_risk.py first.")
        sys.exit(1)
    return json.loads(RISK_FILE.read_text())


def find_html_files():
    """Find all HTML files in the project (excluding calculators which are self-contained)."""
    files = []
    for root, dirs, filenames in os.walk(str(PROJECT_DIR)):
        # Skip directories that don't contain risk warnings
        rel_root = os.path.relpath(root, str(PROJECT_DIR))
        if any(skip in rel_root for skip in ["node_modules", "venv", ".git", "backups"]):
            continue
        for f in filenames:
            if f.endswith(".html"):
                files.append(pathlib.Path(root) / f)
    return files


def line_has_risk_context(line):
    """Check if a line contains risk-warning context words."""
    lower = line.lower()
    return any(word in lower for word in CONTEXT_WORDS)


def replace_percentage_in_file(filepath, old_pct, new_pct, dry_run=False):
    """Replace old percentage with new in a single file. Returns count of replacements."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return 0

    old_str = f"{old_pct}%"
    if old_str not in content:
        return 0

    lines = content.split("\n")
    replacements = 0
    new_lines = []

    for i, line in enumerate(lines):
        if old_str in line and line_has_risk_context(line):
            new_line = line.replace(old_str, f"{new_pct}%")
            new_lines.append(new_line)
            replacements += 1
            if dry_run:
                rel = filepath.relative_to(PROJECT_DIR)
                print(f"    {rel}:{i+1}  {old_str} → {new_pct}%")
        else:
            new_lines.append(line)

    if replacements > 0 and not dry_run:
        filepath.write_text("\n".join(new_lines), encoding="utf-8")

    return replacements


def main():
    parser = argparse.ArgumentParser(description="Update risk warning percentage across site")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--force", type=int, help="Force replacement to this percentage (for testing)")
    args = parser.parse_args()

    print(f"Risk Warning Updater — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    data = load_data()
    current_pct = data["percentage"]

    # Determine old and new percentages
    if args.force:
        new_pct = args.force
        # Find the old percentage from history
        if len(data["history"]) >= 2:
            old_pct = data["history"][-2]["percentage"]
        else:
            old_pct = 51  # default assumption
        print(f"  Force mode: replacing {old_pct}% → {new_pct}%")
    else:
        # Normal mode: check if the percentage actually changed
        if len(data["history"]) < 2:
            print("  No previous percentage in history — nothing to update.")
            return

        new_pct = data["history"][-1]["percentage"]
        old_pct = data["history"][-2]["percentage"]

        if old_pct == new_pct:
            print(f"  Percentage unchanged ({new_pct}%) — nothing to update.")
            return

    # Sanity check
    if not (MIN_SANE <= new_pct <= MAX_SANE):
        print(f"  ERROR: New percentage {new_pct}% is outside sane range ({MIN_SANE}-{MAX_SANE}).")
        print("  Aborting to prevent damage. Check scraper output.")
        sys.exit(1)

    print(f"\n  Replacing {old_pct}% → {new_pct}% in risk warning context\n")

    # Find and replace
    html_files = find_html_files()
    total_replacements = 0
    files_changed = 0

    for filepath in html_files:
        count = replace_percentage_in_file(filepath, old_pct, new_pct, dry_run=args.dry_run)
        if count > 0:
            total_replacements += count
            files_changed += 1

    print(f"\n  Summary: {total_replacements} replacements across {files_changed} files")

    if args.dry_run:
        print("  Dry run — no files were modified.")
        return

    if total_replacements == 0:
        print("  No replacements made (old percentage not found in risk context).")
        return

    # Stage all changed HTML files
    stage = run_git("add", "-A", "*.html")
    # Also add files in subdirectories
    for ext_dir in ["ar", "de", "es", "fr", "pt", "updates", "video", "etoro-review", "checklist", "calculators"]:
        run_git("add", "-A", f"{ext_dir}/")

    # Check if there are staged changes
    diff = run_git("diff", "--cached", "--name-only")
    if not diff.stdout.strip():
        print("  No changes staged (git says nothing changed).")
        return

    staged_count = len(diff.stdout.strip().splitlines())
    print(f"  Staged {staged_count} files for commit.")

    # Commit
    msg = (
        f"Update eToro risk percentage: {old_pct}% → {new_pct}%\n\n"
        f"Weekly risk warning check detected a change on etoro.com.\n"
        f"{files_changed} files updated, {total_replacements} replacements."
    )
    commit = run_git("commit", "-m", msg)
    if commit.returncode != 0:
        print(f"  ERROR: git commit failed: {commit.stderr}")
        sys.exit(1)
    print(f"  Committed: {msg.splitlines()[0]}")

    # Try to push
    push = run_git("push")
    if push.returncode == 0:
        print("  Pushed to remote successfully.")
        send_telegram(
            "Risk Warning Updated on Live Site",
            f"eToro CFD risk percentage updated across the site.\n\n"
            f"Change: {old_pct}% → {new_pct}%\n"
            f"Files: {files_changed}\n"
            f"Replacements: {total_replacements}",
            emoji="✅"
        )
    else:
        print(f"  Push failed (expected on VPS): {push.stderr.strip()}")
        send_telegram(
            "Risk Warning Updated — Push Needed",
            f"eToro risk percentage committed locally ({old_pct}% → {new_pct}%).\n"
            f"{files_changed} files updated.\n\n"
            f"Run on Mac:\n"
            f"  cd ~/socialtradingvlog-website\n"
            f"  git pull stv:~/socialtradingvlog-website\n"
            f"  git push",
            emoji="⚠️"
        )


if __name__ == "__main__":
    main()
