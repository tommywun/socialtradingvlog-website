#!/usr/bin/env python3
"""
Google Search Console checker — uses the same service account as GA.

Prerequisites:
  1. Enable "Google Search Console API" in Google Cloud Console
     (APIs & Services > Enable APIs > search for "Search Console API")
  2. Add the service account email as a user in GSC:
     Search Console > Settings > Users and permissions > Add user
     Email: stv-analytics@vocal-affinity-487722-n4.iam.gserviceaccount.com
     Permission: Full (or at least Restricted for read-only)

Usage:
  python3 tools/gsc_check.py              # Full report
  python3 tools/gsc_check.py --submit     # Submit/resubmit sitemap
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from google.oauth2 import service_account
from googleapiclient.discovery import build

SITE_URL = "sc-domain:socialtradingvlog.com"  # Domain property
SITE_URL_PREFIX = "https://socialtradingvlog.com/"  # URL prefix property (fallback)
SITEMAP_URL = "https://socialtradingvlog.com/sitemap.xml"
KEY_FILE = os.path.expanduser("~/.config/stv-secrets/ga-service-account.json")

SCOPES = ["https://www.googleapis.com/auth/webmasters"]


def get_service():
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    return build("searchconsole", "v1", credentials=creds)


def list_sites(service):
    """List all sites the service account has access to."""
    result = service.sites().list().execute()
    sites = result.get("siteEntry", [])
    if not sites:
        print("  No sites found. The service account needs to be added as a user in GSC.")
        print(f"  Go to Search Console > Settings > Users and permissions > Add user")
        print(f"  Email: stv-analytics@vocal-affinity-487722-n4.iam.gserviceaccount.com")
        print(f"  Permission: Full")
        return []
    return sites


def check_sitemaps(service, site_url):
    """List all sitemaps and their status."""
    result = service.sitemaps().list(siteUrl=site_url).execute()
    sitemaps = result.get("sitemap", [])
    if not sitemaps:
        print("  No sitemaps submitted yet.")
    return sitemaps


def submit_sitemap(service, site_url):
    """Submit/resubmit the sitemap."""
    service.sitemaps().submit(siteUrl=site_url, feedpath=SITEMAP_URL).execute()
    print(f"  Sitemap submitted: {SITEMAP_URL}")


def search_analytics(service, site_url, days=7):
    """Get search performance data."""
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Overall stats
    response = service.searchanalytics().query(
        siteUrl=site_url,
        body={
            "startDate": start,
            "endDate": end,
            "dimensions": [],
            "rowLimit": 1,
        },
    ).execute()

    rows = response.get("rows", [])
    if rows:
        r = rows[0]
        print(f"  Clicks: {r.get('clicks', 0)}")
        print(f"  Impressions: {r.get('impressions', 0)}")
        print(f"  CTR: {r.get('ctr', 0):.1%}")
        print(f"  Average position: {r.get('position', 0):.1f}")
    else:
        print("  No search data available yet.")

    # Top queries
    response = service.searchanalytics().query(
        siteUrl=site_url,
        body={
            "startDate": start,
            "endDate": end,
            "dimensions": ["query"],
            "rowLimit": 20,
        },
    ).execute()

    queries = response.get("rows", [])
    if queries:
        print(f"\n  Top queries (last {days} days):")
        print(f"  {'Query':<50} {'Clicks':>6} {'Impr':>6} {'CTR':>7} {'Pos':>5}")
        print(f"  {'-'*50} {'-'*6} {'-'*6} {'-'*7} {'-'*5}")
        for row in queries:
            q = row["keys"][0][:50]
            print(f"  {q:<50} {row['clicks']:>6} {row['impressions']:>6} {row['ctr']:>6.1%} {row['position']:>5.1f}")

    # Top pages
    response = service.searchanalytics().query(
        siteUrl=site_url,
        body={
            "startDate": start,
            "endDate": end,
            "dimensions": ["page"],
            "rowLimit": 20,
        },
    ).execute()

    pages = response.get("rows", [])
    if pages:
        print(f"\n  Top pages (last {days} days):")
        print(f"  {'Page':<60} {'Clicks':>6} {'Impr':>6} {'Pos':>5}")
        print(f"  {'-'*60} {'-'*6} {'-'*6} {'-'*5}")
        for row in pages:
            p = row["keys"][0].replace("https://socialtradingvlog.com", "")[:60]
            print(f"  {p:<60} {row['clicks']:>6} {row['impressions']:>6} {row['position']:>5.1f}")

    # Index coverage - pages by country
    response = service.searchanalytics().query(
        siteUrl=site_url,
        body={
            "startDate": start,
            "endDate": end,
            "dimensions": ["country"],
            "rowLimit": 10,
        },
    ).execute()

    countries = response.get("rows", [])
    if countries:
        print(f"\n  Top countries (last {days} days):")
        print(f"  {'Country':<20} {'Clicks':>6} {'Impr':>6} {'CTR':>7} {'Pos':>5}")
        print(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*7} {'-'*5}")
        for row in countries:
            print(f"  {row['keys'][0]:<20} {row['clicks']:>6} {row['impressions']:>6} {row['ctr']:>6.1%} {row['position']:>5.1f}")


def main():
    parser = argparse.ArgumentParser(description="Google Search Console checker")
    parser.add_argument("--submit", action="store_true", help="Submit/resubmit sitemap")
    parser.add_argument("--days", type=int, default=28, help="Days of data to show (default: 28)")
    args = parser.parse_args()

    print("=" * 60)
    print("  GOOGLE SEARCH CONSOLE — socialtradingvlog.com")
    print("=" * 60)

    service = get_service()

    # Check access
    print("\n-- Sites with access --")
    sites = list_sites(service)
    if not sites:
        print("\n  ACTION NEEDED:")
        print("  1. Go to https://search.google.com/search-console")
        print("  2. Settings > Users and permissions > Add user")
        print("  3. Add: stv-analytics@vocal-affinity-487722-n4.iam.gserviceaccount.com")
        print("  4. Set permission to 'Full'")
        print("  5. Also enable the Search Console API in Google Cloud Console:")
        print("     https://console.cloud.google.com/apis/library/searchconsole.googleapis.com")
        return

    site_url = None
    for s in sites:
        print(f"  {s['siteUrl']} ({s['permissionLevel']})")
        if "socialtradingvlog" in s["siteUrl"]:
            site_url = s["siteUrl"]

    if not site_url:
        print(f"\n  socialtradingvlog.com not found in accessible sites.")
        print(f"  Available: {[s['siteUrl'] for s in sites]}")
        return

    # Sitemaps
    print(f"\n-- Sitemaps --")
    sitemaps = check_sitemaps(service, site_url)
    for sm in sitemaps:
        print(f"  {sm['path']}")
        print(f"    Last submitted: {sm.get('lastSubmitted', 'unknown')}")
        print(f"    Last downloaded: {sm.get('lastDownloaded', 'unknown')}")
        print(f"    URLs discovered: {sm.get('contents', [{}])[0].get('submitted', '?')}")
        print(f"    URLs indexed: {sm.get('contents', [{}])[0].get('indexed', '?')}")
        if sm.get("warnings"):
            print(f"    Warnings: {sm['warnings']}")
        if sm.get("errors"):
            print(f"    Errors: {sm['errors']}")

    if args.submit:
        print(f"\n  Submitting sitemap...")
        submit_sitemap(service, site_url)

    # Search analytics
    print(f"\n-- Search Performance (last {args.days} days) --")
    search_analytics(service, site_url, days=args.days)

    print(f"\n{'=' * 60}")
    print(f"  Report complete.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
