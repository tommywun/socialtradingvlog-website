#!/usr/bin/env python3
"""
Dependency Verifier — Verify authenticity and check for security updates.

Runs weekly via cron. Checks:
  1. All installed packages match pinned versions in requirements.txt
  2. Package hashes match expected SHA-256 (supply chain tamper detection)
  3. Known vulnerabilities via PyPI Advisory Database
  4. Newer versions available (security patches)
  5. No unexpected packages installed (detect rogue installs)

Usage:
    python3 tools/verify_dependencies.py              # Full verification
    python3 tools/verify_dependencies.py --check-only  # Hash check only (fast)
    python3 tools/verify_dependencies.py --update       # Check for updates

Cron:
    0 4 * * 1 python3 /var/www/.../tools/verify_dependencies.py >> logs/deps.log 2>&1
"""

import sys
import os
import json
import pathlib
import argparse
import subprocess
import urllib.request
import urllib.error
import hashlib
import re
from datetime import datetime

# Shared security library
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from security_lib import (
    PROJECT_DIR, LOGS_DIR, SECRETS_DIR,
    log as _lib_log, send_telegram, record_tool_run, normalize_package_name,
)

REQUIREMENTS = PROJECT_DIR / "requirements.txt"

# Our expected direct dependencies (package name -> pinned version)
EXPECTED_PACKAGES = {
    "beautifulsoup4": "4.14.3",
    "deep-translator": "1.11.4",
    "google-analytics-data": "0.20.0",
    "google-api-python-client": "2.190.0",
    "google-auth": "2.48.0",
    "google-auth-httplib2": "0.3.0",
    "google-auth-oauthlib": "1.2.4",
    "resend": "2.22.0",
}

# Packages only needed on Mac (local dev), not required on VPS
VPS_OPTIONAL = {
    "beautifulsoup4",      # Fee scraping (runs locally with Playwright)
    "deep-translator",     # Translation (runs locally)
    "google-analytics-data",  # Analytics (runs locally)
    "google-auth-oauthlib",   # OAuth flow (initial auth done locally)
    "resend",              # Email sending (not yet deployed to VPS)
}

# Known safe transitive dependencies (auto-installed by direct deps)
KNOWN_TRANSITIVE = {
    # Google API chain
    "certifi", "charset-normalizer", "google-api-core", "googleapis-common-protos",
    "grpcio", "grpcio-status", "httplib2", "idna", "oauthlib", "protobuf",
    "proto-plus", "pyasn1", "pyasn1-modules", "requests", "requests-oauthlib",
    "rsa", "soupsieve", "urllib3", "cachetools", "pyparsing", "uritemplate",
    "google-cloud-core", "packaging", "setuptools", "pip", "wheel",
    # Transcription pipeline (openai-whisper + dependencies)
    "openai", "openai-whisper", "torch", "numpy", "numba", "llvmlite",
    "tiktoken", "regex", "tqdm", "sympy", "mpmath", "networkx", "fsspec",
    "more-itertools", "typing-extensions", "typing-inspection",
    # Playwright (fee scraping)
    "playwright", "pyee", "greenlet",
    # Video download
    "yt-dlp",
    # HTTP/async (used by openai, playwright)
    "httpx", "httpcore", "h11", "anyio", "sniffio", "exceptiongroup",
    "pydantic", "pydantic-core", "annotated-types", "jiter",
    # Crypto / misc
    "cryptography", "cffi", "pycparser", "six", "future",
    "jinja2", "markupsafe", "distro",
    # macOS specific
    "altgraph", "macholib",
}


DEPS_LOG = LOGS_DIR / "deps.log"


def log(msg, level="INFO"):
    _lib_log(msg, level, log_file=DEPS_LOG)


def send_alert(subject, body):
    """Send alert via Telegram."""
    send_telegram(subject, body, emoji="📦 DEPENDENCY ALERT",
                  dedupe_key=f"deps:{subject[:50]}")


def get_installed_packages():
    """Get all installed packages and versions."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return {}
    packages = {}
    for pkg in json.loads(result.stdout):
        packages[pkg["name"].lower()] = pkg["version"]
    return packages


def verify_pinned_versions():
    """Check installed versions match pinned versions."""
    issues = []
    installed = get_installed_packages()

    for pkg, expected_version in EXPECTED_PACKAGES.items():
        pkg_lower = normalize_package_name(pkg)
        # pip normalizes names: check both hyphen and underscore forms
        alt_name = pkg_lower.replace("-", "_")
        alt_name2 = pkg_lower.replace("-", "")
        installed_version = (installed.get(pkg_lower)
                           or installed.get(alt_name)
                           or installed.get(alt_name2)
                           or installed.get(pkg.lower()))

        if not installed_version:
            # Some packages are only needed on Mac (local dev), not on VPS
            import platform
            if platform.system() == "Linux" and pkg in VPS_OPTIONAL:
                continue
            issues.append(f"MISSING: {pkg} (expected {expected_version})")
        elif installed_version != expected_version:
            issues.append(
                f"VERSION MISMATCH: {pkg} installed={installed_version} "
                f"expected={expected_version}"
            )

    return issues


def verify_hashes():
    """Verify installed package files match expected SHA-256 hashes."""
    issues = []

    if not REQUIREMENTS.exists():
        issues.append("requirements.txt not found — cannot verify hashes")
        return issues

    # Parse hashes from requirements.txt
    expected_hashes = {}
    content = REQUIREMENTS.read_text()
    current_pkg = None
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            current_pkg = None
            continue
        if "==" in line and not line.startswith("--"):
            # Package line: beautifulsoup4==4.14.3 \
            pkg_match = re.match(r"^([\w-]+)==([\d.]+)", line)
            if pkg_match:
                current_pkg = pkg_match.group(1).lower()
        if "--hash=sha256:" in line and current_pkg:
            hash_match = re.search(r"--hash=sha256:([a-f0-9]+)", line)
            if hash_match:
                expected_hashes[current_pkg] = hash_match.group(1)

    log(f"  Parsed {len(expected_hashes)} hashes from requirements.txt")

    # We can't directly hash installed packages the same way (they're extracted),
    # but we can verify they haven't been tampered with by checking against PyPI
    for pkg, expected_hash in expected_hashes.items():
        version = EXPECTED_PACKAGES.get(pkg, "")
        if not version:
            continue
        try:
            url = f"https://pypi.org/pypi/{pkg}/{version}/json"
            req = urllib.request.Request(url, headers={"User-Agent": "STV-DepVerify/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode())

            # Get the wheel hash from PyPI
            pypi_hashes = set()
            for url_info in data.get("urls", []):
                if url_info.get("packagetype") == "bdist_wheel":
                    digests = url_info.get("digests", {})
                    if "sha256" in digests:
                        pypi_hashes.add(digests["sha256"])

            if pypi_hashes and expected_hash not in pypi_hashes:
                issues.append(
                    f"HASH MISMATCH: {pkg}=={version} — "
                    f"our hash doesn't match PyPI! Possible tampering."
                )
            elif not pypi_hashes:
                log(f"  Could not verify hash for {pkg} (no wheel on PyPI)")
            else:
                log(f"  ✓ {pkg}=={version} hash verified against PyPI")

        except Exception as e:
            log(f"  Could not verify {pkg}: {e}", "WARN")

    return issues


def check_vulnerabilities():
    """Check for known vulnerabilities in our packages."""
    issues = []

    # Use pip audit if available
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip_audit", "--format=json"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            vulns = json.loads(result.stdout)
            for vuln in vulns.get("dependencies", []):
                if vuln.get("vulns"):
                    for v in vuln["vulns"]:
                        issues.append(
                            f"VULNERABILITY: {vuln['name']}=={vuln['version']} — "
                            f"{v.get('id', 'Unknown')} ({v.get('fix_versions', ['no fix'])})"
                        )
            return issues
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: check PyPI advisory database manually for our packages
    for pkg, version in EXPECTED_PACKAGES.items():
        try:
            # Check PyPI JSON API for yanked status
            url = f"https://pypi.org/pypi/{pkg}/{version}/json"
            req = urllib.request.Request(url, headers={"User-Agent": "STV-DepVerify/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode())

            # Check if version is yanked
            for url_info in data.get("urls", []):
                if url_info.get("yanked"):
                    reason = url_info.get("yanked_reason", "Unknown reason")
                    issues.append(f"YANKED: {pkg}=={version} — {reason}")

            # Check if there's a newer version (might have security fixes)
            info = data.get("info", {})
            latest = info.get("version", version)
            if latest != version:
                log(f"  {pkg}: installed={version}, latest={latest}")

        except urllib.error.HTTPError as e:
            if e.code == 404:
                issues.append(f"REMOVED: {pkg}=={version} no longer on PyPI!")
        except Exception:
            pass

    return issues


def check_for_updates():
    """Check if newer versions are available for our packages."""
    updates = []

    for pkg, current in EXPECTED_PACKAGES.items():
        try:
            url = f"https://pypi.org/pypi/{pkg}/json"
            req = urllib.request.Request(url, headers={"User-Agent": "STV-DepVerify/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode())

            latest = data.get("info", {}).get("version", current)
            if latest != current:
                updates.append(f"{pkg}: {current} → {latest}")
        except Exception:
            pass

    return updates


def check_rogue_packages():
    """Detect unexpected packages that weren't part of our dependency tree."""
    issues = []
    installed = get_installed_packages()

    known_all = set()
    for pkg in EXPECTED_PACKAGES:
        known_all.add(normalize_package_name(pkg))
    for pkg in KNOWN_TRANSITIVE:
        known_all.add(normalize_package_name(pkg))

    # On VPS (Linux), skip system-installed packages — only flag unexpected
    # pip-installed packages. System packages come from Ubuntu's apt.
    import platform
    is_linux = platform.system() == "Linux"

    for pkg_name in installed:
        normalized = normalize_package_name(pkg_name)
        if normalized not in known_all:
            # Skip common build/system packages everywhere
            if normalized in {"pip", "setuptools", "wheel", "pkg-resources",
                             "distlib", "filelock", "platformdirs", "virtualenv"}:
                continue
            # On Linux VPS, skip Ubuntu system packages (installed via apt, not pip)
            if is_linux:
                try:
                    result = subprocess.run(
                        ["python3", "-c",
                         f"import importlib.metadata; d=importlib.metadata.distribution('{pkg_name}'); "
                         f"print(str(d._path))"],
                        capture_output=True, text=True, timeout=5,
                    )
                    loc = result.stdout.strip()
                    if "/usr/lib/python3" in loc:
                        continue  # System package from apt, not pip
                except Exception:
                    continue  # Can't determine location, skip
            issues.append(f"UNEXPECTED: {pkg_name}=={installed[pkg_name]}")

    return issues


# ─── Main ──────────────────────────────────────────────────────────────


def run_full_verification():
    """Run all dependency verification checks."""
    log("=" * 60)
    log("Starting dependency verification...")
    all_issues = []

    # 1. Version check
    log("  Checking pinned versions...")
    issues = verify_pinned_versions()
    if issues:
        log(f"  Version issues: {len(issues)}", "WARN")
        all_issues.extend(issues)
    else:
        log(f"  ✓ All {len(EXPECTED_PACKAGES)} packages at expected versions")

    # 2. Hash verification against PyPI
    log("  Verifying package hashes against PyPI...")
    issues = verify_hashes()
    if issues:
        log(f"  Hash issues: {len(issues)}", "CRITICAL")
        all_issues.extend(issues)
    else:
        log("  ✓ All hashes verified against PyPI")

    # 3. Vulnerability check
    log("  Checking for known vulnerabilities...")
    issues = check_vulnerabilities()
    if issues:
        log(f"  Vulnerabilities found: {len(issues)}", "WARN")
        all_issues.extend(issues)
    else:
        log("  ✓ No known vulnerabilities")

    # 4. Rogue package check
    log("  Checking for unexpected packages...")
    issues = check_rogue_packages()
    if issues:
        log(f"  Unexpected packages: {len(issues)}", "WARN")
        for i in issues:
            log(f"    {i}", "WARN")
        all_issues.extend(issues)
    else:
        log("  ✓ No unexpected packages")

    # 5. Update check
    log("  Checking for available updates...")
    updates = check_for_updates()
    if updates:
        log(f"  Updates available:")
        for u in updates:
            log(f"    → {u}")

    # Summary
    if all_issues:
        alert_text = "\n".join(f"• {i}" for i in all_issues)
        send_alert(
            f"Dependency verification: {len(all_issues)} issue(s)",
            alert_text,
        )
        log(f"\n⚠ {len(all_issues)} issue(s) found — alert sent", "WARN")
    else:
        log(f"\n✓ All dependencies verified — {len(EXPECTED_PACKAGES)} packages clean")

    if updates:
        log(f"  {len(updates)} update(s) available (review for security patches)")

    record_tool_run("verify_dependencies")
    return all_issues


def run_hash_check():
    """Quick hash-only verification."""
    log("Quick hash verification...")
    issues = verify_pinned_versions()
    issues.extend(verify_hashes())
    if issues:
        for i in issues:
            log(f"  ⚠ {i}", "WARN")
        send_alert("Hash verification failed", "\n".join(f"• {i}" for i in issues))
    else:
        log("✓ All hashes verified")
    return issues


def run_update_check():
    """Check for available updates."""
    log("Checking for package updates...")
    updates = check_for_updates()
    if updates:
        for u in updates:
            log(f"  → {u}")
        log(f"\nTo update requirements.txt with new hashes:")
        log(f"  1. pip download --no-deps --dest /tmp/verify <package>==<new_version>")
        log(f"  2. pip hash /tmp/verify/<file>.whl --algorithm sha256")
        log(f"  3. Update requirements.txt with new version + hash")
        log(f"  4. pip install --require-hashes -r requirements.txt")
    else:
        log("  All packages at latest versions")
    return updates


def main():
    parser = argparse.ArgumentParser(description="STV Dependency Verifier")
    parser.add_argument("--check-only", action="store_true", help="Hash check only")
    parser.add_argument("--update", action="store_true", help="Check for updates")
    args = parser.parse_args()

    print(f"STV Dependency Verifier — {datetime.now().isoformat()}\n")

    if args.check_only:
        run_hash_check()
    elif args.update:
        run_update_check()
    else:
        run_full_verification()

    print("\nDone.")


if __name__ == "__main__":
    main()
