#!/usr/bin/env python3
"""
Save daily GSC snapshot + track SEO changes over time.

Saves to:
  reports/gsc-YYYY-MM-DD.json  — daily snapshot of all GSC metrics
  reports/seo-changes.json     — log of title/meta changes with before/after

Can be added to launchd daily report or run on demand.

Usage:
  python3 tools/gsc_snapshot.py              # Save daily snapshot
  python3 tools/gsc_snapshot.py --compare 7  # Compare last 7 days vs previous 7
"""

import sys
import os
import json
import argparse
import pathlib
from datetime import datetime, timedelta

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY_FILE = pathlib.Path.home() / ".config" / "stv-secrets" / "ga-service-account.json"
BASE_DIR = pathlib.Path(__file__).parent.parent
REPORTS_DIR = BASE_DIR / "reports"
CHANGES_FILE = REPORTS_DIR / "seo-changes.json"
SCOPES = ["https://www.googleapis.com/auth/webmasters"]


def get_service():
    creds = service_account.Credentials.from_service_account_file(str(KEY_FILE), scopes=SCOPES)
    return build("searchconsole", "v1", credentials=creds)


def find_site_url(service):
    sites = service.sites().list().execute().get("siteEntry", [])
    for s in sites:
        if "socialtradingvlog" in s["siteUrl"]:
            return s["siteUrl"]
    return None


def save_snapshot(days=28):
    """Save a daily GSC snapshot."""
    REPORTS_DIR.mkdir(exist_ok=True)
    service = get_service()
    site_url = find_site_url(service)
    if not site_url:
        print("ERROR: socialtradingvlog.com not found in GSC")
        return

    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Queries
    queries_resp = service.searchanalytics().query(siteUrl=site_url, body={
        "startDate": start, "endDate": end, "dimensions": ["query"], "rowLimit": 100
    }).execute()

    # Pages
    pages_resp = service.searchanalytics().query(siteUrl=site_url, body={
        "startDate": start, "endDate": end, "dimensions": ["page"], "rowLimit": 50
    }).execute()

    # Overall
    overview_resp = service.searchanalytics().query(siteUrl=site_url, body={
        "startDate": start, "endDate": end, "dimensions": [], "rowLimit": 1
    }).execute()

    # Sitemaps
    sm_resp = service.sitemaps().list(siteUrl=site_url).execute()

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "period": {"start": start, "end": end, "days": days},
        "overview": overview_resp.get("rows", [{}])[0] if overview_resp.get("rows") else {},
        "queries": [{"query": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"],
                     "ctr": round(r["ctr"], 4), "position": round(r["position"], 1)}
                    for r in queries_resp.get("rows", [])],
        "pages": [{"page": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"],
                   "ctr": round(r["ctr"], 4), "position": round(r["position"], 1)}
                  for r in pages_resp.get("rows", [])],
        "sitemaps": [{"path": sm["path"],
                      "submitted": sm.get("contents", [{}])[0].get("submitted", 0),
                      "indexed": sm.get("contents", [{}])[0].get("indexed", 0)}
                     for sm in sm_resp.get("sitemap", [])],
    }

    out_path = REPORTS_DIR / f"gsc-{snapshot['date']}.json"
    out_path.write_text(json.dumps(snapshot, indent=2))
    print(f"Snapshot saved: {out_path}")
    print(f"  Queries: {len(snapshot['queries'])}")
    print(f"  Pages: {len(snapshot['pages'])}")
    ov = snapshot["overview"]
    if ov:
        print(f"  Impressions: {ov.get('impressions', 0)}")
        print(f"  Clicks: {ov.get('clicks', 0)}")
        print(f"  Position: {ov.get('position', 0):.1f}")
    return snapshot


def log_seo_change(page, field, old_value, new_value, notes=""):
    """Log a title/meta/CTA change for tracking."""
    REPORTS_DIR.mkdir(exist_ok=True)
    changes = []
    if CHANGES_FILE.exists():
        changes = json.loads(CHANGES_FILE.read_text())

    changes.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "page": page,
        "field": field,
        "old": old_value,
        "new": new_value,
        "notes": notes,
    })

    CHANGES_FILE.write_text(json.dumps(changes, indent=2))
    print(f"Change logged: {page} [{field}]")


def compare_snapshots(days_back=7):
    """Compare recent snapshot with older one to show trends."""
    snapshots = sorted(REPORTS_DIR.glob("gsc-*.json"))
    if len(snapshots) < 2:
        print("Need at least 2 snapshots to compare. Run daily snapshots first.")
        return

    latest = json.loads(snapshots[-1].read_text())
    # Find snapshot closest to days_back ago
    target_date = datetime.now() - timedelta(days=days_back)
    older = None
    for s in snapshots:
        d = datetime.strptime(s.stem.replace("gsc-", ""), "%Y-%m-%d")
        if d <= target_date:
            older = json.loads(s.read_text())

    if not older:
        older = json.loads(snapshots[0].read_text())

    print(f"\n{'='*60}")
    print(f"  GSC COMPARISON: {older['date']} vs {latest['date']}")
    print(f"{'='*60}")

    # Overview comparison
    ov_old = older.get("overview", {})
    ov_new = latest.get("overview", {})
    for metric in ["impressions", "clicks", "position"]:
        old_val = ov_old.get(metric, 0)
        new_val = ov_new.get(metric, 0)
        if isinstance(old_val, float):
            diff = new_val - old_val
            arrow = "↑" if (diff < 0 if metric == "position" else diff > 0) else "↓"
            print(f"  {metric.capitalize():>15}: {old_val:.1f} → {new_val:.1f} ({arrow} {abs(diff):.1f})")
        else:
            diff = new_val - old_val
            arrow = "↑" if diff > 0 else "↓"
            print(f"  {metric.capitalize():>15}: {old_val} → {new_val} ({arrow} {abs(diff)})")

    # Page-level changes
    old_pages = {p["page"]: p for p in older.get("pages", [])}
    new_pages = {p["page"]: p for p in latest.get("pages", [])}

    print(f"\n  Page position changes:")
    print(f"  {'Page':<50} {'Old':>5} {'New':>5} {'Change':>8}")
    print(f"  {'-'*50} {'-'*5} {'-'*5} {'-'*8}")

    for page, new_data in sorted(new_pages.items(), key=lambda x: x[1]["impressions"], reverse=True)[:15]:
        old_data = old_pages.get(page)
        if old_data:
            diff = old_data["position"] - new_data["position"]  # positive = improved
            arrow = "↑" if diff > 0 else "↓" if diff < 0 else "="
            short_page = page.replace("https://socialtradingvlog.com", "")[:50]
            print(f"  {short_page:<50} {old_data['position']:>5.1f} {new_data['position']:>5.1f} {arrow} {abs(diff):>5.1f}")

    # Show SEO changes in the period
    if CHANGES_FILE.exists():
        changes = json.loads(CHANGES_FILE.read_text())
        period_changes = [c for c in changes if c["date"] >= older["date"]]
        if period_changes:
            print(f"\n  SEO changes in this period:")
            for c in period_changes:
                print(f"    [{c['date']}] {c['page']} — {c['field']}")
                print(f"      Old: {c['old'][:80]}")
                print(f"      New: {c['new'][:80]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare", type=int, help="Compare with snapshot N days ago")
    parser.add_argument("--log-change", nargs=4, metavar=("PAGE", "FIELD", "OLD", "NEW"),
                        help="Log an SEO change")
    args = parser.parse_args()

    if args.log_change:
        log_seo_change(*args.log_change)
    elif args.compare:
        compare_snapshots(args.compare)
    else:
        save_snapshot()


if __name__ == "__main__":
    main()
