#!/usr/bin/env python3
"""
System Doctor — Self-healing automation for STV VPS.

Runs every 4 hours via cron. Scans logs for errors, matches against known
patterns, applies automatic fixes, and alerts only for unfixable issues.

Also monitors: disk space, services, OAuth tokens, pipeline progress,
and writes a heartbeat for the dead man's switch.

Usage:
    python3 tools/system_doctor.py            # full scan + heal
    python3 tools/system_doctor.py --dry-run  # scan only, no fixes
"""

import sys
import os
import re
import json
import time
import pathlib
import subprocess
import argparse
import shutil
from datetime import datetime, timedelta

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from security_lib import send_telegram, log as sec_log, record_tool_run

PROJECT_DIR = pathlib.Path(__file__).parent.parent
TOOLS_DIR = PROJECT_DIR / "tools"
LOGS_DIR = PROJECT_DIR / "logs"
DATA_DIR = PROJECT_DIR / "data"
TRANS_DIR = PROJECT_DIR / "transcriptions"
VENV_PYTHON = PROJECT_DIR / "venv" / "bin" / "python3"
VENV_PIP = PROJECT_DIR / "venv" / "bin" / "pip"

HEARTBEAT_FILE = DATA_DIR / "doctor-heartbeat.json"
JOURNAL_FILE = DATA_DIR / "error-journal.md"

# Log files to scan for errors.
# NOTE: doctor.log is EXCLUDED to prevent feedback loops (doctor reading its
# own error reports and counting them as new errors).
# NOTE: selftest.log is handled separately — only the latest run is checked.
LOG_FILES = [
    LOGS_DIR / "pipeline.log",
    LOGS_DIR / "subtitle-upload.log",
    LOGS_DIR / "security.log",
    LOGS_DIR / "scrape-fees.log",
    LOGS_DIR / "analytics.log",
    LOGS_DIR / "link-prospector.log",
    LOGS_DIR / "deps.log",
    LOGS_DIR / "threat-scan.log",
    LOGS_DIR / "code-audit.log",
    TRANS_DIR / "pipeline.log",
]

SELFTEST_LOG = LOGS_DIR / "selftest.log"

# Error patterns to scan for in general logs
ERROR_PATTERNS = [
    "ERROR", "CRITICAL", "Traceback", "Exception",
    "Permission denied", "No space left", "quotaExceeded",
]

# Hours to look back when scanning logs
SCAN_HOURS = 4


def log(msg, level="INFO"):
    """Log to both stdout and doctor log file."""
    sec_log(msg, level=level, log_file=LOGS_DIR / "doctor.log")


def journal(entry):
    """Append to persistent error journal."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(JOURNAL_FILE, "a") as f:
            f.write(f"\n### {ts}\n{entry}\n")
    except Exception:
        pass


# ── Log Scanner ──────────────────────────────────────────────────────


def _parse_log_timestamp(line):
    """Try to extract a datetime from a log line. Returns None if unparseable."""
    import re
    # Match [2026-02-25T06:00:01] or [2026-02-25 06:00:01] or [2026-02-25T06:00:01.123456]
    m = re.match(r'\[(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', line)
    if m:
        ts_str = m.group(1).replace("T", " ")
        try:
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    return None


def _is_benign(line):
    """Return True if the error line is a known benign/handled pattern."""
    if "quotaExceeded" in line:
        return True  # Normal — YouTube quota, handled by pipeline
    if "Alert deduplicated" in line:
        return True
    if "Alert rate limit" in line:
        return True
    if "caption fetch failed" in line:
        return True  # Handled by pipeline — quota or transient
    # Summary lines that mention CRITICAL/ERROR as a count, not an actual error
    if re.search(r'CRITICAL:\s*\d+', line):
        return True
    if re.search(r'ERROR:\s*\d+', line):
        return True
    return False


def scan_logs():
    """Scan log files for recent errors. Returns deduplicated (file, line) tuples.

    Only includes errors from the last SCAN_HOURS. For lines without parseable
    timestamps, uses the file modification time as a proxy — if the file hasn't
    been modified within the scan window, those lines are skipped.
    """
    cutoff = datetime.now() - timedelta(hours=SCAN_HOURS)
    errors = []
    seen_signatures = set()  # Deduplicate by error signature

    for log_path in LOG_FILES:
        if not log_path.exists():
            continue

        # If the file hasn't been modified in the scan window, skip entirely
        try:
            file_mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
            if file_mtime < cutoff:
                continue
        except Exception:
            continue

        try:
            lines = log_path.read_text().splitlines()
            last_known_ts = None

            for line in lines[-500:]:
                # Try to parse timestamp from this line
                line_ts = _parse_log_timestamp(line)
                if line_ts:
                    last_known_ts = line_ts

                # Skip lines older than cutoff.
                # Lines WITHOUT a timestamp are only included if the most
                # recent timestamped line before them is within the window.
                # If no timestamp has been seen yet, skip (don't assume recent).
                if last_known_ts is None:
                    continue
                if last_known_ts < cutoff:
                    continue

                if any(pat in line for pat in ERROR_PATTERNS):
                    if _is_benign(line):
                        continue

                    # Create a dedup signature: filename + first 80 chars of
                    # the error (strips timestamps so identical errors don't
                    # repeat across scan cycles)
                    stripped = line.strip()[:200]
                    # Remove timestamp prefix for dedup
                    sig_line = re.sub(r'^\[\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\]]*\]\s*', '', stripped)
                    sig = f"{log_path.name}:{sig_line[:80]}"
                    if sig in seen_signatures:
                        continue
                    seen_signatures.add(sig)

                    errors.append((log_path.name, stripped))
        except Exception:
            pass

    # Also check the latest selftest run (separate logic)
    errors.extend(_scan_selftest())

    return errors


def _scan_selftest():
    """Check only the MOST RECENT selftest run for failures.

    The selftest appends results to selftest.log. We find the last run block
    (identified by the last 'Self-test:' summary line) and only report [FAIL]
    entries from that run. Historical failures from earlier runs are ignored.
    """
    if not SELFTEST_LOG.exists():
        return []

    try:
        lines = SELFTEST_LOG.read_text().splitlines()
    except Exception:
        return []

    # Find the last summary line like "[2026-02-25T06:00:02] Self-test: 16/16 passed"
    last_summary_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if "Self-test:" in lines[i] and "passed" in lines[i]:
            last_summary_idx = i
            break

    if last_summary_idx < 0:
        return []

    # Collect [FAIL] lines from the last run block (summary + detail lines after it)
    errors = []
    for line in lines[last_summary_idx:]:
        if "[FAIL]" in line:
            errors.append(("selftest.log", line.strip()[:200]))

    return errors


# ── Known Error Pattern Fixes ─────────────────────────────────────────


def try_fix_module_not_found(error_line, dry_run):
    """Fix: ModuleNotFoundError by pip installing the missing module."""
    import re
    m = re.search(r"No module named '([^']+)'", error_line)
    if not m:
        return False
    module = m.group(1).split(".")[0]  # top-level package

    if dry_run:
        log(f"  Would install: {module}")
        return True

    log(f"  Auto-fixing: pip install {module}")
    r = subprocess.run(
        [str(VENV_PIP), "install", module],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode == 0:
        log(f"  Installed {module} successfully")
        journal(f"Auto-installed missing module: {module}")
        return True
    else:
        log(f"  Failed to install {module}: {r.stderr[:200]}", "ERROR")
        return False


def try_fix_permission_denied(error_line, dry_run):
    """Fix: Permission denied on secret files."""
    import re
    m = re.search(r"Permission denied: '?([^']+)'?", error_line)
    if not m:
        return False
    path = m.group(1).strip()

    # Only fix files in known safe directories
    safe_prefixes = [str(PROJECT_DIR), str(pathlib.Path.home() / ".config" / "stv-secrets")]
    if not any(path.startswith(p) for p in safe_prefixes):
        return False

    if not os.path.exists(path):
        return False

    if dry_run:
        log(f"  Would chmod 600: {path}")
        return True

    log(f"  Auto-fixing: chmod 600 {path}")
    os.chmod(path, 0o600)
    journal(f"Fixed permissions on: {path}")
    return True


def try_fix_connection_error(error_line, dry_run):
    """Fix: Retry transient connection errors."""
    if dry_run:
        log("  Would retry connection (transient error)")
        return True
    # Connection errors are transient — just log and let next cron run retry
    log("  Connection error (transient) — will retry next run")
    return True


# ── System Checks ────────────────────────────────────────────────────


def check_disk_space(dry_run):
    """Check disk usage and auto-clean if >85%."""
    try:
        usage = shutil.disk_usage("/")
        pct = (usage.used / usage.total) * 100
        log(f"Disk usage: {pct:.1f}%")

        if pct < 85:
            return True

        log(f"Disk usage HIGH ({pct:.1f}%) — cleaning up", "WARN")

        if dry_run:
            log("  Would delete transcription audio files and compress old logs")
            return True

        freed = 0

        # Delete processed audio files
        for audio in TRANS_DIR.glob("*/audio.*"):
            try:
                size = audio.stat().st_size
                audio.unlink()
                freed += size
            except Exception:
                pass

        # Compress logs older than 7 days
        week_ago = time.time() - 7 * 86400
        for log_file in LOGS_DIR.glob("*.log"):
            try:
                if log_file.stat().st_mtime < week_ago:
                    subprocess.run(["gzip", "-f", str(log_file)], timeout=30)
            except Exception:
                pass

        # Delete rotated logs older than 90 days
        ninety_days = time.time() - 90 * 86400
        for gz in LOGS_DIR.glob("*.log.gz"):
            try:
                if gz.stat().st_mtime < ninety_days:
                    size = gz.stat().st_size
                    gz.unlink()
                    freed += size
            except Exception:
                pass

        freed_mb = freed / (1024 * 1024)
        log(f"  Freed {freed_mb:.1f} MB")
        journal(f"Disk cleanup: freed {freed_mb:.1f} MB (was {pct:.1f}%)")

        if freed_mb < 10:
            send_telegram(
                "Disk Space Warning",
                f"Disk still high ({pct:.1f}%) after cleanup. Freed only {freed_mb:.1f} MB. Check manually.",
                emoji="💾",
            )
        return True

    except Exception as e:
        log(f"Disk check failed: {e}", "ERROR")
        return False


def check_cron_jobs(dry_run):
    """Verify STV cron jobs are installed."""
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            log("No crontab found", "WARN")
            return False

        stv_count = r.stdout.count("#STV")
        log(f"Cron jobs: {stv_count} #STV entries")

        if stv_count < 15:
            log(f"Only {stv_count} STV crons — expected 20+", "WARN")
            if dry_run:
                log("  Would re-run setup_cron.sh")
                return False

            # Auto-repair by re-running setup_cron.sh
            setup = TOOLS_DIR / "setup_cron.sh"
            if setup.exists():
                log("  Auto-fixing: re-running setup_cron.sh")
                r = subprocess.run(
                    ["bash", str(setup)], capture_output=True, text=True, timeout=60,
                )
                if r.returncode == 0:
                    journal("Cron jobs repaired via setup_cron.sh")
                    return True
                else:
                    log(f"  setup_cron.sh failed: {r.stderr[:200]}", "ERROR")
                    return False
        return True

    except Exception as e:
        log(f"Cron check failed: {e}", "ERROR")
        return False


def check_services(dry_run):
    """Check if key services are running."""
    issues = []

    # Check if dashboard is running (only if systemd service exists)
    try:
        r = subprocess.run(
            ["systemctl", "is-active", "stv-dashboard"],
            capture_output=True, text=True, timeout=10,
        )
        if r.stdout.strip() != "active":
            issues.append("stv-dashboard")
            if not dry_run:
                log("  Auto-fixing: restarting stv-dashboard")
                subprocess.run(
                    ["systemctl", "restart", "stv-dashboard"],
                    capture_output=True, timeout=30,
                )
                journal("Restarted stv-dashboard service")
    except Exception:
        pass  # systemctl not available or service doesn't exist

    if issues:
        log(f"Service issues: {', '.join(issues)}", "WARN")
    else:
        log("Services: all OK")
    return len(issues) == 0


def check_oauth_token(dry_run):
    """Check YouTube OAuth token health."""
    token_path = pathlib.Path.home() / ".config" / "stv-secrets" / "youtube-token.pickle"
    if not token_path.exists():
        log("YouTube token: NOT FOUND", "WARN")
        send_telegram(
            "YouTube Token Missing",
            "Token not found on VPS.\nFix: scp ~/.config/stv-secrets/youtube-token.pickle stv:~/.config/stv-secrets/",
            emoji="🔑",
        )
        return False

    try:
        import pickle
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

        if hasattr(creds, "expiry") and creds.expiry:
            remaining = creds.expiry.replace(tzinfo=None) - datetime.now()
            hours_left = remaining.total_seconds() / 3600

            if hours_left < 0:
                log("YouTube token: expired, refreshing")
                # Try refresh
                if creds.refresh_token:
                    if not dry_run:
                        try:
                            from google.auth.transport.requests import Request
                            creds.refresh(Request())
                            with open(token_path, "wb") as f:
                                pickle.dump(creds, f)
                            log("  Refreshed YouTube token OK")
                            # Routine refresh — no journal entry needed
                            return True
                        except Exception as e:
                            log(f"  Token refresh failed: {e}", "ERROR")
                send_telegram(
                    "YouTube Token Expired",
                    "Token expired and refresh failed.\nFix: Re-auth on Mac, then:\n  scp ~/.config/stv-secrets/youtube-token.pickle stv:~/.config/stv-secrets/",
                    emoji="🔑",
                )
                return False
            elif hours_left < 1:
                # Token expires within the hour — proactively refresh (routine)
                log(f"YouTube token: expires in {hours_left:.0f}h, refreshing")
                if not dry_run and creds.refresh_token:
                    try:
                        from google.auth.transport.requests import Request
                        creds.refresh(Request())
                        with open(token_path, "wb") as f:
                            pickle.dump(creds, f)
                        log("  Proactively refreshed YouTube token")
                        return True
                    except Exception as e:
                        log(f"  Proactive refresh failed: {e}", "WARN")
            else:
                log(f"YouTube token: OK ({hours_left:.0f}h remaining)")
        else:
            log("YouTube token: loaded (no expiry info)")

        return True

    except Exception as e:
        log(f"YouTube token check failed: {e}", "ERROR")
        return False


def check_pipeline_progress():
    """Check subtitle pipeline progress."""
    try:
        complete = 0
        total = 0
        pipeline_langs = ["es", "de", "fr", "it", "pt", "ar", "pl", "nl", "ko"]

        if not TRANS_DIR.exists():
            log("Pipeline: transcriptions dir not found")
            return

        for d in TRANS_DIR.iterdir():
            if not d.is_dir() or d.name.startswith("."):
                continue
            total += 1
            en_srt = d / "subtitles.en.srt"
            if en_srt.exists() and all((d / f"subtitles.{l}.srt").exists() for l in pipeline_langs):
                complete += 1

        log(f"Pipeline progress: {complete}/{total} videos fully complete")

        # Check if progress is stale
        state_file = DATA_DIR / "doctor-state.json"
        prev_complete = 0
        prev_ts = None
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text())
                prev_complete = state.get("pipeline_complete", 0)
                prev_ts = state.get("pipeline_checked")
            except Exception:
                pass

        # Save current progress
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        state_data = {
            "pipeline_complete": complete,
            "pipeline_total": total,
            "pipeline_checked": datetime.now().isoformat(),
        }
        if state_file.exists():
            try:
                existing = json.loads(state_file.read_text())
                existing.update(state_data)
                state_data = existing
            except Exception:
                pass
        state_file.write_text(json.dumps(state_data, indent=2))

        # Alert if no progress in 48h
        if prev_ts and prev_complete == complete and complete < total:
            age_hours = (datetime.now() - datetime.fromisoformat(prev_ts)).total_seconds() / 3600
            if age_hours > 48:
                log(f"Pipeline stale: no progress in {age_hours:.0f}h", "WARN")
                send_telegram(
                    "Pipeline Stalled",
                    f"Subtitle pipeline stalled at {complete}/{total}. No progress in {age_hours:.0f}h. Check logs.",
                    emoji="⚠️",
                    dedupe_key="pipeline-stall",
                )

    except Exception as e:
        log(f"Pipeline progress check failed: {e}", "ERROR")


# ── Error Pattern Matching ────────────────────────────────────────────


def diagnose_and_fix(errors, dry_run):
    """Match errors against known patterns and attempt fixes."""
    fixed = 0
    unfixed = []

    for filename, error_line in errors:
        if "ModuleNotFoundError" in error_line or "No module named" in error_line:
            if try_fix_module_not_found(error_line, dry_run):
                fixed += 1
                continue

        if "Permission denied" in error_line:
            if try_fix_permission_denied(error_line, dry_run):
                fixed += 1
                continue

        if "ConnectionError" in error_line or "Connection refused" in error_line:
            if try_fix_connection_error(error_line, dry_run):
                fixed += 1
                continue

        if "Token has been expired" in error_line or "token" in error_line.lower() and "expired" in error_line.lower():
            # Token issues handled by check_oauth_token
            continue

        if "No space left" in error_line:
            # Disk issues handled by check_disk_space
            continue

        # Unknown error — needs human attention
        unfixed.append((filename, error_line))

    return fixed, unfixed


# ── Main ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="STV System Doctor — self-healing automation")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, don't apply fixes")
    args = parser.parse_args()

    log("=" * 60)
    log(f"System Doctor {'(DRY RUN)' if args.dry_run else ''} — {datetime.now().isoformat()}")
    log("=" * 60)

    # 1. Scan logs for errors
    log("Scanning logs for recent errors...")
    errors = scan_logs()
    log(f"Found {len(errors)} error(s) in last {SCAN_HOURS}h")

    # 2. Diagnose and fix known errors
    fixed = 0
    unfixed = []
    if errors:
        log("Diagnosing errors...")
        fixed, unfixed = diagnose_and_fix(errors, args.dry_run)
        log(f"Fixed: {fixed} | Unfixed: {len(unfixed)}")

    # 3. System checks
    log("\nRunning system checks...")
    check_disk_space(args.dry_run)
    check_cron_jobs(args.dry_run)
    check_services(args.dry_run)
    check_oauth_token(args.dry_run)
    check_pipeline_progress()

    # 4. Alert for unfixed errors (batch into one message)
    if unfixed:
        summary_lines = [f"- {f}: {e[:80]}" for f, e in unfixed[:10]]
        summary = "\n".join(summary_lines)
        log(f"\nUnfixed errors requiring attention:\n{summary}", "WARN")
        send_telegram(
            "System Doctor: Unfixed Errors",
            f"{len(unfixed)} unfixed error(s):\n{summary}",
            emoji="⚠️",
            dedupe_key="doctor-unfixed",
        )

    # 5. Write heartbeat (dead man's switch)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HEARTBEAT_FILE.write_text(json.dumps({
        "ts": time.time(),
        "time": datetime.now().isoformat(),
        "errors_found": len(errors),
        "errors_fixed": fixed,
        "errors_unfixed": len(unfixed),
    }, indent=2))

    # 6. Record tool run
    record_tool_run("system_doctor")

    status = "clean" if not unfixed else f"{len(unfixed)} unfixed"
    log(f"\nDoctor complete — {status}")


if __name__ == "__main__":
    main()
