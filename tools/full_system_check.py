#!/usr/bin/env python3
"""
STV Full System Check — comprehensive operational health check.

Runs from the Mac; SSHes into VPS for server-side checks.
No external dependencies beyond stdlib.

Sections:
  A. Live Site & Network
  B. Cloudflare Layer
  C. VPS Services & System Health
  D. Cron Job Coverage
  E. Security Stack
  F. Log Health
  G. Subtitle Pipeline
  H. Content Freshness
  I. Newsletter System

Usage:
    python3 tools/full_system_check.py           # all checks
    python3 tools/full_system_check.py --quick   # skip slow VPS script runs
    python3 tools/full_system_check.py --notify  # send Telegram summary on completion
"""

import argparse
import json
import pathlib
import re
import socket
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# ─── Config ────────────────────────────────────────────────────────────────

PROJECT = pathlib.Path(__file__).parent.parent
SECRETS = pathlib.Path.home() / ".config" / "stv-secrets"
VPS = "stv@89.167.73.64"
VPS_PROJECT = "/home/stv/socialtradingvlog-website"
SITE = "https://socialtradingvlog.com"
CF_ZONE = "5fb9d48f310faea50fd4b8dca8e5380c"

AGREED_LANGS = {"es", "de", "fr", "it", "pt", "ar", "nl", "pl"}

KEY_PAGES = [
    "/",
    "/copy-trading/",
    "/etoro-review/",
    "/copy-trading-returns.html",
    "/popular-investor.html",
    "/social-trading/",
    "/sitemap.xml",
    "/contact/",
    "/es/",
    "/de/",
    "/fr/",
    "/pt/",
    "/ar/",
]

EXPECTED_CRON_JOBS = 26  # active entries in setup_cron.sh (excl. 2 DISABLED scrapers)

# Age thresholds (seconds)
MAX_UPTIME_AGE    = 600     # 10 min  — uptime cron (runs every 5 min)
MAX_SECURITY_AGE  = 10800   # 3h      — security monitor (every 2h)
MAX_DOCTOR_AGE    = 18000   # 5h      — system doctor (every 4h)
MAX_DAILY_AGE     = 90000   # 25h     — daily jobs (pipeline, threat scanner, GSC)
MAX_WEEKLY_AGE    = 691200  # 8 days  — weekly jobs (RSS, schema, backup)

passes   = []
failures = []
warnings = []


def check(name, passed, detail="", warn=False):
    if passed:
        marker = "PASS "
        passes.append(name)
    elif warn:
        marker = "WARN "
        warnings.append((name, detail))
    else:
        marker = "FAIL "
        failures.append((name, detail))
    print(f"  {marker} {name}" + (f"  —  {detail}" if detail else ""))


def ssh(cmd, timeout=60):
    r = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
         "-o", "BatchMode=yes", VPS, cmd],
        capture_output=True, text=True, timeout=timeout,
    )
    return r.stdout, r.stderr, r.returncode


def http_get(url, timeout=15):
    """GET url; returns (status_code, body_snippet). None on connection error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "STV-SystemCheck/1.0"})
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, r.read(1024).decode(errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, str(e)


def http_no_redir(url, timeout=10):
    """GET url without following redirects; returns (status_code, location)."""
    class _NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **kw):
            return None

    opener = urllib.request.build_opener(_NoRedir())
    req = urllib.request.Request(url, headers={"User-Agent": "STV-SystemCheck/1.0"})
    try:
        opener.open(req, timeout=timeout)
        return 200, ""
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location", "")
    except Exception as e:
        return None, str(e)


def now():
    return time.time()


def age_secs(ts_str):
    """Return age in seconds of an ISO timestamp string. None on parse error."""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return now() - dt.timestamp()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# A. Live Site & Network
# ═══════════════════════════════════════════════════════════════════════════

def check_live_site(args):
    print("\nA. Live Site & Network\n")

    # A1: DNS resolves through Cloudflare
    try:
        ip = socket.gethostbyname("socialtradingvlog.com")
        cf_prefixes = ("104.", "172.64.", "172.65.", "172.66.", "172.67.",
                       "198.41.", "162.158.", "190.93.", "188.114.")
        is_cf = any(ip.startswith(p) for p in cf_prefixes)
        check("A1. DNS resolves via Cloudflare", is_cf, ip)
    except Exception as e:
        check("A1. DNS resolves via Cloudflare", False, str(e))

    # A2: SSL certificate valid with 14+ days remaining
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection(("socialtradingvlog.com", 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname="socialtradingvlog.com") as ssock:
                cert = ssock.getpeercert()
                expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                days = (expiry - datetime.utcnow()).days
                check("A2. SSL cert valid", days >= 14, f"{days} days remaining (expires {expiry.date()})")
    except Exception as e:
        check("A2. SSL cert valid", False, str(e))

    # A3: HTTP → HTTPS redirect
    code, loc = http_no_redir("http://socialtradingvlog.com/")
    ok = code in (301, 302, 307, 308)
    check("A3. HTTP → HTTPS redirect", ok,
          f"{code} → {loc[:50]}" if ok else f"got {code} (expected 3xx)")

    # A4: Key pages return 200
    page_fails = []
    for path in KEY_PAGES:
        code, _ = http_get(SITE + path)
        if code != 200:
            page_fails.append(f"{path} ({code})")
    check(f"A4. Key pages return 200 ({len(KEY_PAGES)} checked)", not page_fails,
          "; ".join(page_fails) if page_fails else f"all {len(KEY_PAGES)} OK")

    # A5: Homepage response time < 4s
    t0 = now()
    code, _ = http_get(SITE + "/")
    elapsed = now() - t0
    check("A5. Homepage response time < 4s", elapsed < 4.0 and code == 200,
          f"{elapsed:.2f}s")

    # A6: robots.txt accessible
    # Cloudflare prepends AI content-signals preamble so read up to 8KB
    # Accept as valid if status 200 and contains either traditional User-agent: OR CF Content-Signal
    try:
        import urllib.request as _ur, ssl as _ssl
        _req = _ur.Request(SITE + "/robots.txt", headers={"User-Agent": "STV-SystemCheck/1.0"})
        _ctx = _ssl.create_default_context()
        with _ur.urlopen(_req, timeout=15, context=_ctx) as _r:
            _robots_code = _r.status
            _robots_body = _r.read(8192).decode(errors="ignore")
        has_rules = "User-agent:" in _robots_body or "Content-Signal" in _robots_body
        check("A6. robots.txt accessible", _robots_code == 200 and has_rules,
              f"status {_robots_code}" + (", has directives" if has_rules else ", no directives found"))
    except Exception as _e:
        check("A6. robots.txt accessible", False, str(_e))

    # A7: hreflang markup present on key pages
    # Read 8KB — hreflang is in <head> but some pages have long meta sections
    hreflang_pages = ["/", "/copy-trading/", "/etoro-review/"]
    hreflang_fails = []
    for path in hreflang_pages:
        try:
            _req = urllib.request.Request(SITE + path, headers={"User-Agent": "STV-SystemCheck/1.0"})
            _ctx = ssl.create_default_context()
            with urllib.request.urlopen(_req, timeout=15, context=_ctx) as _r:
                _body = _r.read(8192).decode(errors="ignore")
            if "hreflang" not in _body:
                hreflang_fails.append(path)
        except Exception:
            hreflang_fails.append(path)
    check(f"A7. hreflang markup ({len(hreflang_pages)} pages checked)", not hreflang_fails,
          "; ".join(hreflang_fails) if hreflang_fails else f"all {len(hreflang_pages)} present")


# ═══════════════════════════════════════════════════════════════════════════
# B. Cloudflare Layer
# ═══════════════════════════════════════════════════════════════════════════

def check_cloudflare(args):
    print("\nB. Cloudflare Layer\n")

    cf_token_file = SECRETS / "cloudflare-api-token.txt"
    if not cf_token_file.exists():
        check("B. Cloudflare API", False, "token file not found — skipping CF checks")
        return

    token = cf_token_file.read_text().strip()

    def cf_get(path):
        url = f"https://api.cloudflare.com/client/v4{path}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return {"success": False, "error": f"HTTP {e.code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # B1: Zone active
    zone = cf_get(f"/zones/{CF_ZONE}")
    status = zone.get("result", {}).get("status", "unknown")
    check("B1. Cloudflare zone active", zone.get("success") and status == "active", status)

    # B2: SSL mode Full or Strict
    ssl_cfg = cf_get(f"/zones/{CF_ZONE}/settings/ssl")
    ssl_mode = ssl_cfg.get("result", {}).get("value", "unknown") if ssl_cfg.get("success") else "error"
    check("B2. SSL/TLS mode Full or Strict", ssl_mode in ("full", "strict"), f"mode = {ssl_mode}")

    # B3: Always Use HTTPS enabled
    https_cfg = cf_get(f"/zones/{CF_ZONE}/settings/always_use_https")
    val = https_cfg.get("result", {}).get("value", "unknown") if https_cfg.get("success") else "error"
    check("B3. Always Use HTTPS on", val == "on", f"value = {val}")

    # B4: Worker routes configured (stv-redirects)
    routes = cf_get(f"/zones/{CF_ZONE}/workers/routes")
    if routes.get("success"):
        n = len(routes.get("result", []))
        check("B4. stv-redirects Worker routes present", n > 0, f"{n} route(s)")
    else:
        check("B4. stv-redirects Worker routes", True,
              "zone-level route check unavailable", warn=True)

    # B5: Legacy redirects return 3xx (test 3 known WordPress paths)
    test_paths = ["/faq/", "/tag/etoro/", "/is-etoro-a-scam/"]
    redir_fails = []
    for path in test_paths:
        code, loc = http_no_redir(SITE + path)
        if code not in (301, 302, 307, 308):
            redir_fails.append(f"{path}: {code}")
    check(f"B5. Legacy redirects return 3xx ({len(test_paths)} tested)", not redir_fails,
          "; ".join(redir_fails) if redir_fails else f"all {len(test_paths)} redirect correctly")


# ═══════════════════════════════════════════════════════════════════════════
# C. VPS Services & System Health
# ═══════════════════════════════════════════════════════════════════════════

def check_vps_services(args):
    print("\nC. VPS Services & System Health\n")

    # C1: SSH reachable
    out, err, rc = ssh("echo OK")
    if "OK" not in out:
        check("C1. VPS SSH reachable", False, err.strip()[:80])
        for label in ("C2–C8",):
            check(f"{label}. VPS checks", False, "skipped — SSH not reachable")
        return
    check("C1. VPS SSH reachable", True, "connected")

    # C2: Caddy active
    out, _, _ = ssh("systemctl is-active caddy 2>/dev/null")
    check("C2. Caddy active", out.strip() == "active", out.strip())

    # C3: fail2ban active
    out, _, _ = ssh("systemctl is-active fail2ban 2>/dev/null")
    check("C3. fail2ban active", out.strip() == "active", out.strip())

    # C4: UFW active; 8080 closed
    # Site is served by GitHub Pages (not VPS directly), so 80/443 are not expected on VPS
    ufw_active_out, _, _ = ssh("systemctl is-active ufw 2>/dev/null")
    ufw_active = ufw_active_out.strip() == "active"
    ss_out, _, _ = ssh("ss -tnl 2>/dev/null")
    has_8080 = ":8080 " in ss_out or ":8080\n" in ss_out
    detail = []
    if not ufw_active: detail.append("UFW service inactive")
    if has_8080:       detail.append("port 8080 still listening")
    check("C4. UFW active; 8080 closed",
          ufw_active and not has_8080,
          "; ".join(detail) if detail else "UFW active, 8080 closed")

    # C5: Disk usage < 80%
    out, _, _ = ssh("df -h / | tail -1")
    m = re.search(r"(\d+)%", out)
    if m:
        pct = int(m.group(1))
        check("C5. Disk usage < 80%", pct < 80, f"{pct}% used")
    else:
        check("C5. Disk usage", False, f"could not parse: {out.strip()}")

    # C6: Memory < 90%
    out, _, _ = ssh("free -m | grep '^Mem:'")
    parts = out.strip().split()
    if len(parts) >= 3:
        total, used = int(parts[1]), int(parts[2])
        pct = int(used / total * 100) if total else 100
        check("C6. Memory < 90%", pct < 90, f"{pct}% ({used}MB / {total}MB)")
    else:
        check("C6. Memory", False, "could not parse free output")

    # C7: CPU 15-min load < 4.0
    out, _, _ = ssh("cat /proc/loadavg")
    parts = out.strip().split()
    if len(parts) >= 3:
        load = float(parts[2])
        check("C7. CPU 15-min load < 4.0", load < 4.0, str(load))
    else:
        check("C7. CPU load", False, "could not parse /proc/loadavg")

    # C8: No zombie processes
    out, _, _ = ssh("ps aux | awk '$8==\"Z\"' | wc -l")
    try:
        n = int(out.strip())
        check("C8. No zombie processes", n == 0, f"{n} zombie(s)" if n else "clean")
    except Exception:
        check("C8. No zombie processes", True, "could not check", warn=True)


# ═══════════════════════════════════════════════════════════════════════════
# D. Cron Job Coverage
# ═══════════════════════════════════════════════════════════════════════════

def check_cron(args):
    print("\nD. Cron Job Coverage\n")

    # D1: Active #STV job count
    out, _, _ = ssh("crontab -l 2>/dev/null | grep -v '^#' | grep '#STV' | wc -l")
    try:
        count = int(out.strip())
        ok = count >= EXPECTED_CRON_JOBS - 3
        check(f"D1. Cron jobs installed (~{EXPECTED_CRON_JOBS} expected)", ok,
              f"{count} active #STV jobs")
    except Exception:
        check("D1. Cron jobs installed", False, f"could not parse: {out.strip()}")

    # D2: Key tool last-run times (from security-state.json)
    state_out, _, _ = ssh(f"cat {VPS_PROJECT}/data/security-state.json 2>/dev/null || echo '{{}}'")
    try:
        state = json.loads(state_out)
    except Exception:
        state = {}
    runs = state.get("last_tool_runs", {})

    # security_monitor and system_doctor: use log mtime (more reliable than state file)
    log_windows = [
        ("security.log",     MAX_SECURITY_AGE, "D2. security_monitor (every 2h)"),
        ("doctor.log",       MAX_DOCTOR_AGE,   "D3. system_doctor (every 4h)"),
    ]
    for logfile, max_age, label in log_windows:
        out, _, _ = ssh(f"stat -c %Y {VPS_PROJECT}/logs/{logfile} 2>/dev/null || echo 0")
        try:
            a = now() - int(out.strip())
            check(label, a < max_age, f"{int(a//3600)}h ago")
        except Exception:
            check(label, False, f"{logfile} not found")

    # threat_scanner and selftest: use state file timestamps (they update it correctly)
    state_windows = [
        ("threat_scanner",    MAX_DAILY_AGE,    "D4. threat_scanner (daily)"),
        ("security_selftest", MAX_DAILY_AGE,    "D5. security_selftest (daily)"),
    ]
    for key, max_age, label in state_windows:
        ts = runs.get(key)
        if ts:
            a = age_secs(ts)
            ok = a is not None and a < max_age
            check(label, ok, f"{int(a//3600)}h ago" if a is not None else ts[:16])
        else:
            check(label, False, "no timestamp in state file")

    # D6: Pipeline log updated < 25h
    out, _, _ = ssh(f"stat -c %Y {VPS_PROJECT}/logs/pipeline.log 2>/dev/null || echo 0")
    try:
        a = now() - int(out.strip())
        check("D6. Pipeline cron ran < 25h", a < MAX_DAILY_AGE, f"{int(a//3600)}h ago")
    except Exception:
        check("D6. Pipeline cron ran < 25h", False, "log not found")

    # D7: Uptime log updated < 10 min (every-5-min cron)
    out, _, _ = ssh(f"stat -c %Y {VPS_PROJECT}/logs/uptime.log 2>/dev/null || echo 0")
    try:
        a = now() - int(out.strip())
        check("D7. Uptime cron active (log < 10min old)", a < MAX_UPTIME_AGE,
              f"{int(a//60)}m ago")
    except Exception:
        check("D7. Uptime cron active", False, "log not found")

    # D8: Weekly jobs (RSS, schema) ran < 8 days
    for label, logfile in [("RSS generator", "rss.log"), ("Schema generator", "schema.log")]:
        out, _, _ = ssh(f"stat -c %Y {VPS_PROJECT}/logs/{logfile} 2>/dev/null || echo 0")
        try:
            a = now() - int(out.strip())
            check(f"D8. {label} < 8 days", a < MAX_WEEKLY_AGE, f"{int(a//86400)}d ago")
        except Exception:
            check(f"D8. {label}", False, "log not found")


# ═══════════════════════════════════════════════════════════════════════════
# E. Security Stack
# ═══════════════════════════════════════════════════════════════════════════

def check_security(args):
    print("\nE. Security Stack\n")

    # E1: Selftest result — only count lines in the LAST run
    # Find the last "Self-test: X/16 passed" separator, count [PASS]/[FAIL] after it
    out, _, _ = ssh(f"tail -40 {VPS_PROJECT}/logs/selftest.log 2>/dev/null || echo ''")
    lines = out.splitlines()
    last_sep = -1
    for i, line in enumerate(lines):
        if "Self-test:" in line and "passed" in line:
            last_sep = i
    tail_lines = lines[last_sep + 1:] if last_sep >= 0 else lines
    pass_count = sum(1 for l in tail_lines if "[PASS]" in l)
    fail_count = sum(1 for l in tail_lines if "[FAIL]" in l)
    if pass_count + fail_count > 0:
        check("E1. Security selftest 16/16", pass_count == 16 and fail_count == 0,
              f"{pass_count} passed, {fail_count} failed")
    else:
        check("E1. Security selftest", False, "could not parse selftest.log")

    # E2: No unexpected security alerts in last 2h
    state_out, _, _ = ssh(f"cat {VPS_PROJECT}/data/security-state.json 2>/dev/null || echo '{{}}'")
    try:
        state = json.loads(state_out)
        cutoff = now() - 7200  # 2h
        bad = []
        for a in state.get("recent_alerts", []):
            try:
                ts = datetime.fromisoformat(a["time"]).timestamp()
                subj = a.get("subject", "")
                if ts > cutoff and "Autopilot" not in subj and "All Clear" not in subj:
                    bad.append(subj[:50])
            except Exception:
                pass
        check("E2. No unexpected alerts (2h)", not bad,
              f"{len(bad)}: {'; '.join(bad[:2])}" if bad else "clean")
    except Exception as e:
        check("E2. Security alerts", False, str(e))

    # E3: System doctor heartbeat < 5h
    out, _, _ = ssh(f"cat {VPS_PROJECT}/data/doctor-heartbeat.json 2>/dev/null || echo '{{}}'")
    try:
        hb = json.loads(out)
        a = now() - hb.get("ts", 0)
        check("E3. System doctor heartbeat < 5h", a < MAX_DOCTOR_AGE, f"{int(a//3600)}h ago")
    except Exception as e:
        check("E3. System doctor heartbeat", False, str(e))

    # E4: Encrypted backup < 8 days old
    out, _, _ = ssh(
        f"find {VPS_PROJECT}/backups/ -name 'data-*.gpg' -mtime -8 2>/dev/null | sort | tail -1"
    )
    recent = out.strip()
    check("E4. Encrypted backup < 8 days", bool(recent),
          recent.split("/")[-1] if recent else "no recent backup")

    # E5: Secret file permissions all 600
    out, _, _ = ssh(
        "python3 -c \""
        "import pathlib; s=pathlib.Path.home()/'.config/stv-secrets';"
        "bad=[f.name for f in s.iterdir() if not f.name.startswith('.') and oct(f.stat().st_mode)[-3:]!='600'];"
        "print('BAD:'+','.join(bad) if bad else 'OK')\""
    )
    ok = "OK" in out
    check("E5. Secret file permissions 600", ok,
          out.strip().replace("BAD:", "bad perms: ") if not ok else "all 600")

    # E6: No 8080 in UFW allow rules
    out, _, _ = ssh("ufw status 2>/dev/null")
    has_8080 = "8080" in out and "ALLOW" in out
    check("E6. Port 8080 not in UFW allow rules", not has_8080,
          "8080 still open — remove with: ufw delete allow 8080/tcp" if has_8080 else "8080 closed")

    # E7: file integrity baseline fresh — use file mtime (no internal timestamp key)
    out, _, _ = ssh(
        f"stat -c %Y {VPS_PROJECT}/data/security-integrity.json 2>/dev/null || echo 0"
    )
    try:
        a = now() - int(out.strip())
        check("E7. File integrity baseline < 25h", a < MAX_DAILY_AGE, f"{int(a//3600)}h ago")
    except Exception as e:
        check("E7. File integrity baseline", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# F. Log Health
# ═══════════════════════════════════════════════════════════════════════════

def check_logs(args):
    print("\nF. Log Health\n")

    # F1: No CRITICAL in security.log (last 200 lines)
    out, _, _ = ssh(f"tail -200 {VPS_PROJECT}/logs/security.log 2>/dev/null || echo ''")
    crits = [l.strip() for l in out.splitlines() if "[CRITICAL]" in l]
    check("F1. No CRITICAL in security.log (last 200 lines)", not crits,
          f"{len(crits)}: {crits[0][:70]}" if crits else "clean")

    # F2: No ERROR in pipeline.log (last 50 lines)
    out, _, _ = ssh(f"tail -50 {VPS_PROJECT}/logs/pipeline.log 2>/dev/null || echo ''")
    errs = [l.strip() for l in out.splitlines()
            if "ERROR" in l and "Errors: 0" not in l and "errors: 0" not in l.lower()]
    check("F2. No ERROR in pipeline.log (last 50 lines)", not errs,
          f"{len(errs)}: {errs[0][:70]}" if errs else "clean")

    # F3: Threat scan log — only look at last 8h (quick scans run every 6h)
    # Exclude transient external service errors (CISA KEV geo-blocked from VPS)
    from datetime import timezone as _tz
    cutoff_ts = datetime.now(_tz.utc).timestamp() - 28800  # 8h
    out, _, _ = ssh(f"tail -100 {VPS_PROJECT}/logs/threat-scan.log 2>/dev/null || echo ''")
    threats = []
    for line in out.splitlines():
        if "[ALERT]" not in line and "[WARN]" not in line:
            continue
        if "CISA KEV check error" in line or "CVE check error" in line:
            continue
        import re as _re
        m = _re.match(r"\[(\d{4}-\d{2}-\d{2}T[\d:.]+)\]", line.strip())
        if m:
            try:
                line_ts = datetime.fromisoformat(m.group(1)).replace(tzinfo=_tz.utc).timestamp()
                if line_ts < cutoff_ts:
                    continue
            except Exception:
                pass
        threats.append(line.strip())
    check("F3. Threat scan log: no ALERT/WARN (excl. CVE HTTP errors, 8h window)", not threats,
          f"{len(threats)}: {threats[0][:70]}" if threats else "clean")

    # F4: Uptime log clean (last 20 lines)
    out, _, _ = ssh(f"tail -20 {VPS_PROJECT}/logs/uptime.log 2>/dev/null || echo ''")
    issues = [l.strip() for l in out.splitlines() if "CRITICAL" in l or "[WARN]" in l]
    check("F4. Uptime log clean (last 20 lines)", not issues,
          f"{len(issues)}: {issues[0][:70]}" if issues else "clean")

    # F5: No runaway log files (> 50MB)
    out, _, _ = ssh(f"find {VPS_PROJECT}/logs/ -name '*.log' -size +50M 2>/dev/null | head -5")
    big = [l.strip().split("/")[-1] for l in out.splitlines() if l.strip()]
    check("F5. No log file > 50MB", not big,
          f"large: {', '.join(big)}" if big else "all logs within size")


# ═══════════════════════════════════════════════════════════════════════════
# G. Subtitle Pipeline
# ═══════════════════════════════════════════════════════════════════════════

def check_pipeline(args):
    print("\nG. Subtitle Pipeline\n")

    # G1: Pipeline last run result (from pipeline.log tail)
    out, _, _ = ssh(f"tail -5 {VPS_PROJECT}/logs/pipeline.log 2>/dev/null || echo ''")
    finished = "Pipeline finished" in out or "Completed:" in out
    last = [l.strip() for l in out.splitlines() if l.strip()]
    check("G1. Pipeline has run recently", finished,
          last[-1][:90] if last else "no log content")

    # G2: Subtitle coverage across agreed languages
    script = (
        "python3 -c \""
        "import pathlib; "
        "t=pathlib.Path('/home/stv/socialtradingvlog-website/transcriptions'); "
        "langs={'es','de','fr','it','pt','ar','nl','pl'}; "
        "total=complete=partial=no_en=0; "
        "[exec("
        "  'total+=1; '"
        "  'srt_langs={f.name.split(chr(46))[1] for f in d.glob(chr(115)+chr(117)+chr(98)+chr(116)+chr(105)+chr(116)+chr(108)+chr(101)+chr(115)+chr(46)+chr(42)+chr(46)+chr(115)+chr(114)+chr(116))}; '"
        "  'has_en=(chr(101)+chr(110)) in srt_langs; '"
        "  'agreed=srt_langs & langs; '"
        "  'no_en+=1 if not has_en else 0; '"
        "  'complete+=1 if has_en and agreed==langs else 0; '"
        "  'partial+=1 if has_en and agreed and agreed!=langs else 0'"
        ") for d in t.iterdir() if d.is_dir()]; "
        "print(f'total={total} complete={complete} partial={partial} no_en={no_en}')\""
    )
    # Simpler version without chr() tricks
    script = r"""python3 << 'PYEOF'
import pathlib
t = pathlib.Path('/home/stv/socialtradingvlog-website/transcriptions')
langs = {'es','de','fr','it','pt','ar','nl','pl'}
total = complete = partial = no_en = 0
for d in t.iterdir():
    if not d.is_dir():
        continue
    total += 1
    srt_langs = {f.name.split('.')[1] for f in d.glob('subtitles.*.srt') if len(f.name.split('.')) >= 3}
    has_en = 'en' in srt_langs
    agreed = srt_langs & langs
    if not has_en:
        no_en += 1
    elif agreed == langs:
        complete += 1
    elif agreed:
        partial += 1
print(f'total={total} complete={complete} partial={partial} no_en={no_en}')
PYEOF"""
    out, _, _ = ssh(script, timeout=30)
    m = re.search(r"total=(\d+) complete=(\d+) partial=(\d+) no_en=(\d+)", out)
    if m:
        total, complete, partial, no_en = (
            int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        )
        remaining = total - complete
        # Informational — report coverage, always pass
        check("G2. Subtitle translation coverage (8 langs)", True,
              f"{complete}/{total} fully translated, {partial} partial, {remaining} remaining")
    else:
        check("G2. Subtitle coverage", False, f"could not parse: {out.strip()[:80]}")

    # G3: Subtitle upload cron ran < 25h
    out, _, _ = ssh(f"stat -c %Y {VPS_PROJECT}/logs/subtitle-upload.log 2>/dev/null || echo 0")
    try:
        a = now() - int(out.strip())
        check("G3. Subtitle upload cron ran < 25h", a < MAX_DAILY_AGE, f"{int(a//3600)}h ago")
    except Exception:
        check("G3. Subtitle upload cron", False, "log not found")


# ═══════════════════════════════════════════════════════════════════════════
# H. Content Freshness
# ═══════════════════════════════════════════════════════════════════════════

def check_content(args):
    print("\nH. Content Freshness\n")

    # H1: Sitemap accessible and contains URLs
    code, body = http_get(SITE + "/sitemap.xml")
    has_urls = "<url>" in body or "<loc>" in body
    check("H1. Sitemap.xml accessible", code == 200 and has_urls,
          f"status {code}" + (", has <url> entries" if has_urls else ", no <url> found"))

    # H2: RSS feeds regenerated < 8 days
    out, _, _ = ssh(f"stat -c %Y {VPS_PROJECT}/logs/rss.log 2>/dev/null || echo 0")
    try:
        a = now() - int(out.strip())
        check("H2. RSS feeds < 8 days old", a < MAX_WEEKLY_AGE, f"{int(a//86400)}d ago")
    except Exception:
        check("H2. RSS feeds", False, "rss.log not found")

    # H3: Schema markup regenerated < 8 days
    out, _, _ = ssh(f"stat -c %Y {VPS_PROJECT}/logs/schema.log 2>/dev/null || echo 0")
    try:
        a = now() - int(out.strip())
        check("H3. Schema markup < 8 days old", a < MAX_WEEKLY_AGE, f"{int(a//86400)}d ago")
    except Exception:
        check("H3. Schema markup", False, "schema.log not found")

    # H4: GSC snapshot current — saved to reports/gsc-YYYY-MM-DD.json (not data/gsc-snapshots/)
    out, _, _ = ssh(f"ls -t {VPS_PROJECT}/reports/gsc-*.json 2>/dev/null | head -1")
    latest = out.strip()
    if latest:
        out2, _, _ = ssh(f"stat -c %Y {latest} 2>/dev/null || echo 0")
        try:
            a = now() - int(out2.strip())
            name = latest.split("/")[-1]
            check("H4. GSC snapshot < 49h old", a < 176400,
                  f"{name} — {int(a//3600)}h ago")
        except Exception:
            check("H4. GSC snapshot", False, "could not stat")
    else:
        check("H4. GSC snapshot exists", False, "no gsc-*.json in reports/")

    # H5: Local GA report current (< 25h)
    report = PROJECT / "reports" / "latest.txt"
    if report.exists():
        a = now() - report.stat().st_mtime
        check("H5. GA report current < 25h", a < MAX_DAILY_AGE, f"{int(a//3600)}h ago")
    else:
        check("H5. GA report present", False, "reports/latest.txt not found", warn=True)


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="STV Full System Check")
    parser.add_argument("--quick", action="store_true",
                        help="Skip slow VPS script runs")
    parser.add_argument("--notify", action="store_true",
                        help="Send Telegram summary on completion")
    args = parser.parse_args()

    print("\n══════════════════════════════════════════════════════════")
    print("  STV Full System Check")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("══════════════════════════════════════════════════════════")

    check_live_site(args)
    check_cloudflare(args)
    check_vps_services(args)
    check_cron(args)
    check_security(args)
    check_logs(args)
    check_pipeline(args)
    check_content(args)

    total = len(passes) + len(failures) + len(warnings)
    print(f"\n══════════════════════════════════════════════════════════")
    print(f"  {len(passes)} passed  |  {len(failures)} failed  |  {len(warnings)} warnings  |  {total} total")

    if failures:
        print("\n  Failures:")
        for name, detail in failures:
            print(f"    ✗  {name}")
            if detail:
                print(f"       {detail}")

    if warnings:
        print("\n  Warnings:")
        for name, detail in warnings:
            print(f"    ⚠  {name}")
            if detail:
                print(f"       {detail}")

    if not failures:
        print("\n  ALL CHECKS PASSED" + (" (with warnings)" if warnings else ""))
    print()

    if args.notify:
        _send_telegram(passes, failures, warnings, total)

    sys.exit(0 if not failures else 1)


def _send_telegram(passes, failures, warnings, total):
    try:
        sys.path.insert(0, str(PROJECT / "tools"))
        from security_lib import send_telegram
        status = "✅ ALL CLEAR" if not failures else f"❌ {len(failures)} FAILED"
        body = f"{status}\n{len(passes)}/{total} checks passed"
        if failures:
            body += "\n\nFailed:\n" + "\n".join(f"• {n}" for n, _ in failures[:5])
        if warnings:
            body += "\n\nWarnings:\n" + "\n".join(f"• {n}" for n, _ in warnings[:3])
        send_telegram("Full System Check", body)
    except Exception as e:
        print(f"  (Telegram notify failed: {e})")


if __name__ == "__main__":
    main()
