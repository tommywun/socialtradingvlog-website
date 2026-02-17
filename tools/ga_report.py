#!/usr/bin/env python3
"""
Pull Google Analytics data for socialtradingvlog.com and print a summary report.

Usage:
    python3 tools/ga_report.py              # last 30 days
    python3 tools/ga_report.py --days 7     # last 7 days
    python3 tools/ga_report.py --days 90    # last 90 days
"""

import sys
import os
import argparse
import pathlib
from datetime import datetime, timedelta

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    OrderBy,
)

PROPERTY_ID = "525085627"
KEY_FILE = pathlib.Path.home() / ".config" / "stv-secrets" / "ga-service-account.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(KEY_FILE)


def make_client():
    return BetaAnalyticsDataClient()


def run_report(client, dimensions, metrics, date_range, order_by=None, limit=20):
    dims = [Dimension(name=d) for d in dimensions]
    mets = [Metric(name=m) for m in metrics]
    orders = []
    if order_by:
        for field, desc in order_by:
            if field in metrics:
                orders.append(OrderBy(metric=OrderBy.MetricOrderBy(metric_name=field), desc=desc))
            else:
                orders.append(OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name=field), desc=desc))

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=dims,
        metrics=mets,
        date_ranges=[date_range],
        order_bys=orders or None,
        limit=limit,
    )
    return client.run_report(request)


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="GA report for socialtradingvlog.com")
    parser.add_argument("--days", type=int, default=30, help="Number of days to look back (default: 30)")
    args = parser.parse_args()

    end = datetime.now()
    start = end - timedelta(days=args.days)
    date_range = DateRange(
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
    )

    client = make_client()
    print(f"\nGoogle Analytics Report — socialtradingvlog.com")
    print(f"Period: {start.strftime('%d %b %Y')} → {end.strftime('%d %b %Y')} ({args.days} days)")

    # ── Overview ──────────────────────────────────────────────────
    print_section("OVERVIEW")
    resp = run_report(
        client,
        dimensions=[],
        metrics=["sessions", "totalUsers", "screenPageViews", "averageSessionDuration", "bounceRate"],
        date_range=date_range,
    )
    if resp.rows:
        r = resp.rows[0]
        sessions = r.metric_values[0].value
        users = r.metric_values[1].value
        pageviews = r.metric_values[2].value
        avg_dur = float(r.metric_values[3].value)
        bounce = float(r.metric_values[4].value) * 100
        print(f"  Sessions:           {sessions}")
        print(f"  Users:              {users}")
        print(f"  Page views:         {pageviews}")
        print(f"  Avg session:        {int(avg_dur // 60)}m {int(avg_dur % 60)}s")
        print(f"  Bounce rate:        {bounce:.1f}%")

    # ── Top pages ─────────────────────────────────────────────────
    print_section("TOP PAGES (by page views)")
    resp = run_report(
        client,
        dimensions=["pagePath"],
        metrics=["screenPageViews", "totalUsers", "averageSessionDuration"],
        date_range=date_range,
        order_by=[("screenPageViews", True)],
        limit=20,
    )
    print(f"  {'Page':<50} {'Views':>6} {'Users':>6} {'Avg Time':>8}")
    print(f"  {'-'*50} {'-'*6} {'-'*6} {'-'*8}")
    for row in resp.rows:
        page = row.dimension_values[0].value
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        dur = float(row.metric_values[2].value)
        dur_str = f"{int(dur // 60)}m {int(dur % 60)}s"
        print(f"  {page:<50} {views:>6} {users:>6} {dur_str:>8}")

    # ── Traffic sources ───────────────────────────────────────────
    print_section("TRAFFIC SOURCES")
    resp = run_report(
        client,
        dimensions=["sessionDefaultChannelGroup"],
        metrics=["sessions", "totalUsers"],
        date_range=date_range,
        order_by=[("sessions", True)],
        limit=10,
    )
    print(f"  {'Channel':<30} {'Sessions':>10} {'Users':>10}")
    print(f"  {'-'*30} {'-'*10} {'-'*10}")
    for row in resp.rows:
        channel = row.dimension_values[0].value
        sessions = row.metric_values[0].value
        users = row.metric_values[1].value
        print(f"  {channel:<30} {sessions:>10} {users:>10}")

    # ── Top referrers ─────────────────────────────────────────────
    print_section("TOP REFERRERS")
    resp = run_report(
        client,
        dimensions=["sessionSource"],
        metrics=["sessions"],
        date_range=date_range,
        order_by=[("sessions", True)],
        limit=10,
    )
    print(f"  {'Source':<40} {'Sessions':>10}")
    print(f"  {'-'*40} {'-'*10}")
    for row in resp.rows:
        source = row.dimension_values[0].value
        sessions = row.metric_values[0].value
        print(f"  {source:<40} {sessions:>10}")

    # ── Countries ─────────────────────────────────────────────────
    print_section("TOP COUNTRIES")
    resp = run_report(
        client,
        dimensions=["country"],
        metrics=["sessions", "totalUsers"],
        date_range=date_range,
        order_by=[("sessions", True)],
        limit=10,
    )
    print(f"  {'Country':<30} {'Sessions':>10} {'Users':>10}")
    print(f"  {'-'*30} {'-'*10} {'-'*10}")
    for row in resp.rows:
        country = row.dimension_values[0].value
        sessions = row.metric_values[0].value
        users = row.metric_values[1].value
        print(f"  {country:<30} {sessions:>10} {users:>10}")

    # ── Devices ───────────────────────────────────────────────────
    print_section("DEVICES")
    resp = run_report(
        client,
        dimensions=["deviceCategory"],
        metrics=["sessions", "totalUsers"],
        date_range=date_range,
        order_by=[("sessions", True)],
    )
    print(f"  {'Device':<20} {'Sessions':>10} {'Users':>10}")
    print(f"  {'-'*20} {'-'*10} {'-'*10}")
    for row in resp.rows:
        device = row.dimension_values[0].value
        sessions = row.metric_values[0].value
        users = row.metric_values[1].value
        print(f"  {device:<20} {sessions:>10} {users:>10}")

    # ── CTA clicks (if any) ───────────────────────────────────────
    print_section("CTA CLICKS (affiliate button clicks)")
    resp = run_report(
        client,
        dimensions=["pagePath", "eventName"],
        metrics=["eventCount"],
        date_range=date_range,
        order_by=[("eventCount", True)],
        limit=20,
    )
    has_cta = False
    for row in resp.rows:
        if row.dimension_values[1].value == "cta_click":
            if not has_cta:
                print(f"  {'Page':<50} {'Clicks':>8}")
                print(f"  {'-'*50} {'-'*8}")
                has_cta = True
            page = row.dimension_values[0].value
            clicks = row.metric_values[0].value
            print(f"  {page:<50} {clicks:>8}")
    if not has_cta:
        print("  No CTA clicks recorded yet (tracking was just added)")

    print(f"\n{'=' * 60}")
    print(f"  Report complete.")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
