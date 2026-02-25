#!/usr/bin/env python3
"""
Analytics Monitor — Weekly GA analysis + A/B testing + optimization suggestions.

Pulls Google Analytics data, analyzes tool popularity, CTA performance,
and runs simple A/B tests. Reports findings in weekly digest.

Usage:
    python3 tools/analytics_monitor.py --report weekly     # Full weekly report
    python3 tools/analytics_monitor.py --report ab-results # Check A/B test results
    python3 tools/analytics_monitor.py --report popular    # Most popular tools

Cron (weekly, Mondays 4am — after fee scraper):
    0 4 * * 1  python3 /var/www/socialtradingvlog-website/tools/analytics_monitor.py --report weekly
"""

import sys
import os
import json
import pathlib
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timedelta

PROJECT_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
ANALYTICS_FILE = DATA_DIR / "analytics-report.json"
AB_TESTS_FILE = DATA_DIR / "ab-tests.json"
# Numeric Property ID from GA Admin > Property Settings
GA_PROPERTY_ID = "525085627"

# ─── Google Analytics Data API ────────────────────────────────────────────

def get_ga_credentials():
    """Load GA service account credentials."""
    cred_file = SECRETS_DIR / "ga-service-account.json"
    if not cred_file.exists():
        print("  GA service account not found. Using fallback method.")
        return None
    return json.loads(cred_file.read_text())


def fetch_ga_data(metrics, dimensions, date_range_days=7):
    """Fetch data from GA4 Data API using service account."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Metric, Dimension,
        )
        from google.oauth2 import service_account

        cred_file = SECRETS_DIR / "ga-service-account.json"
        if not cred_file.exists():
            return None

        credentials = service_account.Credentials.from_service_account_file(
            str(cred_file),
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        client = BetaAnalyticsDataClient(credentials=credentials)

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=date_range_days)).strftime("%Y-%m-%d")

        # Validate property ID — must be numeric, not a Measurement ID
        prop_id = GA_PROPERTY_ID
        if prop_id.startswith("G-"):
            print("  WARNING: GA_PROPERTY_ID is a Measurement ID, not a numeric Property ID.")
            print("  Look up the numeric ID in GA Admin > Property Settings.")
            return None
        request = RunReportRequest(
            property=f"properties/{prop_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            metrics=[Metric(name=m) for m in metrics],
            dimensions=[Dimension(name=d) for d in dimensions],
        )

        response = client.run_report(request)
        rows = []
        for row in response.rows:
            entry = {}
            for i, dim in enumerate(dimensions):
                entry[dim] = row.dimension_values[i].value
            for i, met in enumerate(metrics):
                entry[met] = row.metric_values[i].value
            rows.append(entry)

        return rows

    except ImportError:
        print("  google-analytics-data not installed. Using Measurement Protocol fallback.")
        return None
    except Exception as e:
        print(f"  GA API error: {e}")
        return None


def fetch_ga_via_gtag_debug():
    """Fallback: check GA debug endpoint for basic validation."""
    # This is a minimal check — full data requires the Data API
    try:
        url = f"https://www.google-analytics.com/debug/collect?v=2&tid={GA_PROPERTY_ID}&cid=test"
        req = urllib.request.Request(url, headers={"User-Agent": "STV-Analytics/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.getcode() == 200
    except Exception:
        return False


# ─── Analysis Functions ───────────────────────────────────────────────────

def analyze_page_popularity(ga_data):
    """Analyze which pages/tools are most popular."""
    if not ga_data:
        return {"status": "no_data", "pages": []}

    # Sort by sessions/views
    sorted_pages = sorted(ga_data, key=lambda x: int(x.get("sessions", 0)), reverse=True)

    return {
        "status": "ok",
        "period": "7 days",
        "pages": sorted_pages[:20],
    }


def analyze_cta_performance(ga_data):
    """Analyze CTA click rates and suggest improvements."""
    if not ga_data:
        return {"status": "no_data", "suggestions": []}

    suggestions = []
    cta_events = [e for e in ga_data if "cta_click" in str(e.get("eventName", ""))]

    if not cta_events:
        suggestions.append({
            "type": "warning",
            "message": "No CTA click events detected. Verify gtag events are firing correctly.",
        })
    else:
        total_clicks = sum(int(e.get("eventCount", 0)) for e in cta_events)
        if total_clicks < 5:
            suggestions.append({
                "type": "optimization",
                "message": f"Only {total_clicks} CTA clicks this week. Consider: "
                           "moving CTAs higher on the page, making them more prominent, "
                           "or testing different copy/colors.",
            })

    return {
        "status": "ok",
        "cta_clicks": cta_events,
        "suggestions": suggestions,
    }


def generate_optimization_suggestions(popularity, cta_data):
    """Generate actionable optimization suggestions."""
    suggestions = []

    # Tool-specific suggestions based on popularity
    if popularity.get("pages"):
        top_pages = popularity["pages"][:5]
        tool_pages = [p for p in top_pages if "/calculators/" in str(p.get("pagePath", ""))]

        if tool_pages:
            most_popular = tool_pages[0]
            suggestions.append({
                "type": "insight",
                "message": f"Most popular tool: {most_popular.get('pagePath', 'unknown')} "
                           f"with {most_popular.get('sessions', '?')} sessions this week.",
            })

    # CTA suggestions
    if cta_data.get("suggestions"):
        suggestions.extend(cta_data["suggestions"])

    # General suggestions
    suggestions.append({
        "type": "suggestion",
        "message": "Consider adding the Trade Comparison calculator link to the homepage "
                   "hero section if it's driving traffic.",
    })

    return suggestions


# ─── A/B Testing ──────────────────────────────────────────────────────────

def get_active_tests():
    """Load active A/B tests."""
    if AB_TESTS_FILE.exists():
        return json.loads(AB_TESTS_FILE.read_text())
    return {"tests": [], "results": []}


def create_ab_test(test_id, element, variants, page):
    """Register a new A/B test."""
    tests = get_active_tests()
    tests["tests"].append({
        "id": test_id,
        "element": element,
        "variants": variants,
        "page": page,
        "created": datetime.now().isoformat(),
        "status": "active",
    })
    AB_TESTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    AB_TESTS_FILE.write_text(json.dumps(tests, indent=2))
    return test_id


def analyze_ab_results(ga_data):
    """Analyze A/B test results from GA events."""
    tests = get_active_tests()
    results = []

    for test in tests.get("tests", []):
        if test["status"] != "active":
            continue

        # Look for events matching this test
        test_events = [e for e in (ga_data or [])
                       if test["id"] in str(e.get("eventName", ""))]

        if test_events:
            variant_data = {}
            for e in test_events:
                variant = e.get("customEvent:variant", "unknown")
                variant_data.setdefault(variant, 0)
                variant_data[variant] += int(e.get("eventCount", 0))

            results.append({
                "test_id": test["id"],
                "element": test["element"],
                "variants": variant_data,
                "winner": max(variant_data, key=variant_data.get) if variant_data else None,
            })

    return results


# ─── AB Test JavaScript Injector ──────────────────────────────────────────

AB_TEST_JS = """
<!-- STV A/B Testing Framework -->
<script>
(function() {
  // Simple client-side A/B testing
  // Tests are defined in data/ab-tests.json and injected by the scraper
  const STV_AB = {
    getVariant: function(testId, variants) {
      // Consistent assignment per user (stored in localStorage)
      const key = 'stv_ab_' + testId;
      let variant = localStorage.getItem(key);
      if (!variant || !variants.includes(variant)) {
        variant = variants[Math.floor(Math.random() * variants.length)];
        localStorage.setItem(key, variant);
      }
      return variant;
    },
    trackView: function(testId, variant) {
      if (typeof gtag === 'function') {
        gtag('event', 'ab_view_' + testId, {
          event_category: 'ab_test',
          event_label: variant,
        });
      }
    },
    trackConversion: function(testId, variant) {
      if (typeof gtag === 'function') {
        gtag('event', 'ab_convert_' + testId, {
          event_category: 'ab_test',
          event_label: variant,
        });
      }
    },
  };
  window.STV_AB = STV_AB;
})();
</script>
"""


def inject_ab_tests(dry_run=False):
    """Inject A/B test JS into pages that have active tests."""
    tests = get_active_tests()
    active = [t for t in tests.get("tests", []) if t["status"] == "active"]

    if not active:
        print("  No active A/B tests.")
        return

    for test in active:
        page_path = PROJECT_DIR / test["page"]
        if not page_path.exists():
            continue

        content = page_path.read_text()
        if "STV A/B Testing Framework" in content:
            continue  # Already injected

        # Inject before </body>
        if "</body>" in content:
            content = content.replace("</body>", AB_TEST_JS + "\n</body>")
            if not dry_run:
                page_path.write_text(content)
                print(f"  Injected A/B test JS into {test['page']}")


# ─── Weekly Report ────────────────────────────────────────────────────────

def generate_weekly_report():
    """Generate the full weekly analytics report."""
    print("\n═══ Weekly Analytics Report ═══\n")

    report = {
        "generated": datetime.now().isoformat(),
        "period": "7 days",
    }

    # 1. Page popularity
    print("Fetching page popularity data...")
    ga_pages = fetch_ga_data(
        metrics=["sessions", "screenPageViews", "averageSessionDuration"],
        dimensions=["pagePath"],
        date_range_days=7,
    )
    popularity = analyze_page_popularity(ga_pages)
    report["popularity"] = popularity

    if popularity["status"] == "ok":
        print(f"\n  Top pages (last 7 days):")
        for p in popularity["pages"][:10]:
            print(f"    {p.get('sessions', '?'):>6} sessions — {p.get('pagePath', '?')}")
    else:
        print("  Could not fetch GA data. Check service account credentials.")

    # 2. CTA performance
    print("\nFetching CTA event data...")
    ga_events = fetch_ga_data(
        metrics=["eventCount"],
        dimensions=["eventName", "customEvent:event_label"],
        date_range_days=7,
    )
    cta_data = analyze_cta_performance(ga_events)
    report["cta_performance"] = cta_data

    # 3. A/B test results
    print("\nChecking A/B test results...")
    ab_results = analyze_ab_results(ga_events)
    report["ab_tests"] = ab_results
    if ab_results:
        for r in ab_results:
            print(f"  Test '{r['test_id']}': {r['variants']}")
            if r["winner"]:
                print(f"    Winner: {r['winner']}")

    # 4. Optimization suggestions
    suggestions = generate_optimization_suggestions(popularity, cta_data)
    report["suggestions"] = suggestions

    print("\n  Suggestions:")
    for s in suggestions:
        print(f"    [{s['type'].upper()}] {s['message']}")

    # 5. Save report
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ANALYTICS_FILE.write_text(json.dumps(report, indent=2))
    print(f"\n  Report saved to {ANALYTICS_FILE}")

    # 6. Send via alerts
    send_analytics_digest(report)

    return report


def send_analytics_digest(report):
    """Send analytics summary via Telegram + email."""
    try:
        sys.path.insert(0, str(PROJECT_DIR / "tools"))
        from site_autopilot import send_telegram, send_email

        # Build digest message
        msg = "📊 *Weekly Analytics Report*\n\n"

        if report.get("popularity", {}).get("pages"):
            msg += "*Top Pages:*\n"
            for p in report["popularity"]["pages"][:5]:
                sessions = p.get("sessions", "?")
                path = p.get("pagePath", "?")
                msg += f"  {sessions} sessions — {path}\n"
            msg += "\n"

        if report.get("suggestions"):
            msg += "*Suggestions:*\n"
            for s in report["suggestions"][:5]:
                msg += f"  • {s['message']}\n"
            msg += "\n"

        if report.get("ab_tests"):
            msg += "*A/B Tests:*\n"
            for t in report["ab_tests"]:
                msg += f"  {t['test_id']}: {t.get('winner', 'no winner yet')}\n"

        send_telegram(msg, "info")

        # Detailed email
        email_body = msg.replace("*", "").replace("📊", "[Analytics]")
        email_body += "\nFull report at: data/analytics-report.json"
        send_email("Weekly Analytics Report", email_body, "info")

    except Exception as e:
        print(f"  Failed to send analytics digest: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="STV Analytics Monitor")
    parser.add_argument("--report", required=True,
                        choices=["weekly", "popular", "cta", "ab-results", "ab-inject"],
                        help="Which report to generate")
    args = parser.parse_args()

    print(f"STV Analytics Monitor — {args.report} — {datetime.now().isoformat()}\n")

    if args.report == "weekly":
        generate_weekly_report()
    elif args.report == "popular":
        ga_data = fetch_ga_data(
            metrics=["sessions", "screenPageViews"],
            dimensions=["pagePath"],
            date_range_days=7,
        )
        result = analyze_page_popularity(ga_data)
        if result["pages"]:
            for p in result["pages"][:20]:
                print(f"  {p.get('sessions', '?'):>6} — {p.get('pagePath', '?')}")
    elif args.report == "cta":
        ga_data = fetch_ga_data(
            metrics=["eventCount"],
            dimensions=["eventName"],
            date_range_days=7,
        )
        result = analyze_cta_performance(ga_data)
        print(json.dumps(result, indent=2))
    elif args.report == "ab-results":
        ga_data = fetch_ga_data(
            metrics=["eventCount"],
            dimensions=["eventName", "customEvent:event_label"],
            date_range_days=7,
        )
        results = analyze_ab_results(ga_data)
        print(json.dumps(results, indent=2))
    elif args.report == "ab-inject":
        inject_ab_tests()

    print("\nDone.")


if __name__ == "__main__":
    main()
