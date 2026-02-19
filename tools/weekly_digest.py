#!/usr/bin/env python3
"""
Weekly Digest Email — sends a summary of the past week's metrics.

Usage:
    python3 tools/weekly_digest.py                    # send digest now
    python3 tools/weekly_digest.py --dry-run          # print without sending
    python3 tools/weekly_digest.py --to tom@email.com # custom recipient

Schedule with cron (every Monday at 8am):
    0 8 * * 1 cd /Users/thomaswest/socialtradingvlog-website && python3 tools/weekly_digest.py
"""

import sys
import os
import json
import pathlib
import argparse
import re
from datetime import datetime, timedelta

sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

SCRIPT_DIR = pathlib.Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
REPORTS_DIR = PROJECT_DIR / "reports"
SECRETS_DIR = pathlib.Path.home() / ".config" / "stv-secrets"
SENT_LOG = PROJECT_DIR / "outreach" / "sent.json"
GOALS_FILE = PROJECT_DIR / "outreach" / "goals.json"
CONTENT_TRACKER_FILE = PROJECT_DIR / "outreach" / "content-tracker.json"


def get_weekly_stats():
    """Aggregate stats from the last 7 daily reports."""
    reports = sorted(REPORTS_DIR.glob("daily-*.txt"))
    week_reports = reports[-7:]
    if not week_reports:
        return None

    stats = {
        "days": len(week_reports),
        "start": week_reports[0].stem.replace("daily-", ""),
        "end": week_reports[-1].stem.replace("daily-", ""),
        "sessions": [],
        "users": [],
        "pageviews": [],
        "bounces": [],
    }

    for r in week_reports:
        text = r.read_text()
        first = text.split("OVERVIEW")[1] if "OVERVIEW" in text else text
        first = first.split("TOP PAGES")[0] if "TOP PAGES" in first else first

        for line in first.split("\n"):
            line = line.strip()
            if re.match(r'^Sessions:\s+', line):
                try:
                    stats["sessions"].append(int(line.split(":")[-1].strip().split()[0].replace(",", "")))
                except (ValueError, IndexError):
                    pass
            elif re.match(r'^Users:\s+', line):
                try:
                    stats["users"].append(int(line.split(":")[-1].strip().split()[0].replace(",", "")))
                except (ValueError, IndexError):
                    pass
            elif re.match(r'^Page views:\s+', line):
                try:
                    stats["pageviews"].append(int(line.split(":")[-1].strip().split()[0].replace(",", "")))
                except (ValueError, IndexError):
                    pass
            elif re.match(r'^Bounce rate:\s+', line):
                try:
                    stats["bounces"].append(float(line.split(":")[-1].strip().rstrip("%")))
                except (ValueError, IndexError):
                    pass

    return stats


def get_outreach_summary():
    """Summarise outreach activity."""
    if not SENT_LOG.exists():
        return {"sent_this_week": 0, "total_sent": 0, "replies": 0}
    sent = json.loads(SENT_LOG.read_text())
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    sent_this_week = sum(1 for s in sent if s.get("sent_at", "") >= week_ago)
    replies = sum(1 for s in sent if s.get("reply_received"))
    return {"sent_this_week": sent_this_week, "total_sent": len(sent), "replies": replies}


def get_goals_summary():
    """Summarise goal progress."""
    if not GOALS_FILE.exists():
        return []
    goals = json.loads(GOALS_FILE.read_text())
    return [{"title": g["title"], "status": g["status"], "progress": g.get("progress", 0)} for g in goals]


def build_digest_html(stats, outreach, goals):
    """Build the HTML email body."""
    today = datetime.now().strftime("%B %d, %Y")

    # Traffic stats
    total_sessions = sum(stats["sessions"]) if stats else 0
    total_users = sum(stats["users"]) if stats else 0
    total_pageviews = sum(stats["pageviews"]) if stats else 0
    avg_bounce = round(sum(stats["bounces"]) / len(stats["bounces"]), 1) if stats and stats["bounces"] else 0

    # Goals bar
    goals_html = ""
    for g in goals:
        color = "#2BB3FF" if g["status"] == "in_progress" else "#59DDAA" if g["status"] == "completed" else "#E0E1E9"
        goals_html += f"""
        <tr>
            <td style="padding:8px 12px;border-bottom:1px solid #E0E1E9;font-size:14px;color:#191B23">{g['title']}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #E0E1E9;text-align:center">
                <span style="display:inline-block;padding:2px 10px;border-radius:24px;font-size:11px;font-weight:600;background:{color}22;color:{color}">{g['status'].replace('_',' ')}</span>
            </td>
            <td style="padding:8px 12px;border-bottom:1px solid #E0E1E9;text-align:right;font-weight:600;color:#191B23">{g['progress']}%</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;background:#F4F5F9;margin:0;padding:24px">
<div style="max-width:600px;margin:0 auto;background:#FFFFFF;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(25,27,35,0.12)">

  <!-- Header -->
  <div style="background:#382E5E;padding:24px 32px;text-align:center">
    <h1 style="color:#FFFFFF;font-size:20px;font-weight:700;margin:0">SocialTradingVlog</h1>
    <p style="color:rgba(255,255,255,0.6);font-size:13px;margin:4px 0 0">Weekly Digest — {today}</p>
  </div>

  <div style="padding:32px">

    <!-- Traffic Overview -->
    <h2 style="font-size:18px;font-weight:700;color:#191B23;margin:0 0 16px">Traffic This Week</h2>
    <table style="width:100%;border-collapse:collapse;margin-bottom:24px">
      <tr>
        <td style="text-align:center;padding:16px;background:#F4F5F9;border-radius:8px">
          <div style="font-size:28px;font-weight:700;color:#2BB3FF">{total_sessions}</div>
          <div style="font-size:12px;color:#6C6E79;margin-top:4px">Sessions</div>
        </td>
        <td style="width:8px"></td>
        <td style="text-align:center;padding:16px;background:#F4F5F9;border-radius:8px">
          <div style="font-size:28px;font-weight:700;color:#59DDAA">{total_users}</div>
          <div style="font-size:12px;color:#6C6E79;margin-top:4px">Users</div>
        </td>
        <td style="width:8px"></td>
        <td style="text-align:center;padding:16px;background:#F4F5F9;border-radius:8px">
          <div style="font-size:28px;font-weight:700;color:#FF642D">{total_pageviews}</div>
          <div style="font-size:12px;color:#6C6E79;margin-top:4px">Page Views</div>
        </td>
        <td style="width:8px"></td>
        <td style="text-align:center;padding:16px;background:#F4F5F9;border-radius:8px">
          <div style="font-size:28px;font-weight:700;color:#FF4953">{avg_bounce}%</div>
          <div style="font-size:12px;color:#6C6E79;margin-top:4px">Bounce Rate</div>
        </td>
      </tr>
    </table>

    <!-- Outreach -->
    <h2 style="font-size:18px;font-weight:700;color:#191B23;margin:0 0 12px">Outreach</h2>
    <p style="font-size:14px;color:#6C6E79;line-height:1.6;margin:0 0 24px">
      Emails sent this week: <strong style="color:#191B23">{outreach['sent_this_week']}</strong> &middot;
      Total sent: <strong style="color:#191B23">{outreach['total_sent']}</strong> &middot;
      Replies: <strong style="color:#009F81">{outreach['replies']}</strong>
    </p>

    <!-- Goals -->
    <h2 style="font-size:18px;font-weight:700;color:#191B23;margin:0 0 12px">Growth Goals</h2>
    <table style="width:100%;border-collapse:collapse;margin-bottom:24px">
      <tr style="background:#F4F5F9">
        <th style="padding:8px 12px;text-align:left;font-size:12px;font-weight:700;color:#191B23">Goal</th>
        <th style="padding:8px 12px;text-align:center;font-size:12px;font-weight:700;color:#191B23">Status</th>
        <th style="padding:8px 12px;text-align:right;font-size:12px;font-weight:700;color:#191B23">Progress</th>
      </tr>
      {goals_html}
    </table>

    <p style="font-size:12px;color:#8A8E9B;text-align:center;margin:24px 0 0">
      Generated by STV Command Centre &middot; <a href="http://localhost:8080" style="color:#006DCA">Open Dashboard</a>
    </p>
  </div>
</div>
</body></html>"""
    return html


def send_digest(to, html, dry_run=False):
    """Send the digest email using Resend."""
    if dry_run:
        print("=== DRY RUN — would send to:", to)
        print(html)
        return True

    api_key_file = SECRETS_DIR / "resend-api-key.txt"
    if not api_key_file.exists():
        print("ERROR: Resend API key not found at", api_key_file)
        return False

    api_key = api_key_file.read_text().strip()
    import urllib.request
    payload = json.dumps({
        "from": "STV Dashboard <digest@socialtradingvlog.com>",
        "to": [to],
        "subject": f"STV Weekly Digest — {datetime.now().strftime('%B %d')}",
        "html": html,
    }).encode()

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            print("Digest sent! ID:", result.get("id", "?"))
            return True
    except Exception as e:
        print("Failed to send:", e)
        return False


def main():
    parser = argparse.ArgumentParser(description="STV Weekly Digest Email")
    parser.add_argument("--dry-run", action="store_true", help="Print HTML without sending")
    parser.add_argument("--to", default="tom@socialtradingvlog.com", help="Recipient email")
    args = parser.parse_args()

    stats = get_weekly_stats()
    outreach = get_outreach_summary()
    goals = get_goals_summary()
    html = build_digest_html(stats, outreach, goals)
    send_digest(args.to, html, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
