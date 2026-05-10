#!/usr/bin/env python3
"""
STV Rank Tracker — slim dashboard for GSC data.

Usage:
    python3 tools/dashboard.py              # localhost:8080, no auth
    python3 tools/dashboard.py --auth       # localhost:8080, password required
    python3 tools/dashboard.py --public     # 0.0.0.0:8080, password required
"""

import sys
import os
import json
import pathlib
import argparse
import hashlib
import secrets
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie

if sys.platform == "darwin":
    sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))

# ─── Paths ───
PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent
AUTH_FILE = pathlib.Path.home() / ".config" / "stv-secrets" / "dashboard-auth.json"
SESSIONS_FILE = PROJECT_DIR / "data" / "sessions.json"
GSC_CACHE = PROJECT_DIR / "reports" / "gsc-cache.json"

# ─── State ───
ACTIVE_SESSIONS = {}  # token -> expiry_timestamp
LOGIN_ATTEMPTS = {}   # ip -> [timestamps]


# ─── Session persistence ───

def _load_sessions():
    global ACTIVE_SESSIONS
    if SESSIONS_FILE.exists():
        try:
            ACTIVE_SESSIONS = json.loads(SESSIONS_FILE.read_text())
            # Prune expired
            now = time.time()
            ACTIVE_SESSIONS = {k: v for k, v in ACTIVE_SESSIONS.items() if v > now}
        except Exception:
            ACTIVE_SESSIONS = {}


def _save_sessions():
    SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSIONS_FILE.write_text(json.dumps(ACTIVE_SESSIONS, indent=2))


# ─── Auth helpers ───

def init_auth():
    """Ensure auth file exists; prompt to create if missing."""
    if not AUTH_FILE.exists():
        import getpass
        pw = getpass.getpass("Set dashboard password: ")
        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        AUTH_FILE.write_text(json.dumps({
            "password_hash": hashlib.sha256(pw.encode()).hexdigest()
        }))
        AUTH_FILE.chmod(0o600)
        print(f"Auth saved to {AUTH_FILE}")
    _load_sessions()


def check_password(password):
    if not AUTH_FILE.exists():
        return False
    data = json.loads(AUTH_FILE.read_text())
    expected = data.get("password_hash", "")
    return hashlib.sha256(password.encode()).hexdigest() == expected


def create_session():
    token = secrets.token_hex(32)
    expiry = time.time() + 14 * 86400  # 14 days
    ACTIVE_SESSIONS[token] = expiry
    _save_sessions()
    return token


def validate_session(token):
    if not token:
        return False
    expiry = ACTIVE_SESSIONS.get(token)
    if not expiry:
        return False
    if time.time() > expiry:
        ACTIVE_SESSIONS.pop(token, None)
        _save_sessions()
        return False
    return True


def destroy_session(token):
    ACTIVE_SESSIONS.pop(token, None)
    _save_sessions()


def is_rate_limited(ip):
    now = time.time()
    attempts = LOGIN_ATTEMPTS.get(ip, [])
    # Keep only last hour
    attempts = [t for t in attempts if now - t < 3600]
    LOGIN_ATTEMPTS[ip] = attempts
    return len(attempts) >= 5


def record_login_attempt(ip):
    LOGIN_ATTEMPTS.setdefault(ip, []).append(time.time())


# ─── GSC functions ───

def get_gsc_data():
    """Return cached GSC data (1h TTL) or latest snapshot."""
    if GSC_CACHE.exists():
        data = json.loads(GSC_CACHE.read_text())
        if time.time() - data.get("timestamp", 0) < 3600:
            return data
    snapshots = sorted(PROJECT_DIR.glob("reports/gsc-*.json"))
    if snapshots:
        return json.loads(snapshots[-1].read_text())
    return {"error": "No GSC data. Click Refresh to fetch."}


def fetch_gsc_data():
    """Live-fetch GSC data via service account API."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from datetime import datetime, timedelta

    key_file = pathlib.Path.home() / ".config" / "stv-secrets" / "ga-service-account.json"
    creds = service_account.Credentials.from_service_account_file(
        str(key_file), scopes=["https://www.googleapis.com/auth/webmasters"])
    svc = build("searchconsole", "v1", credentials=creds)

    site_url = None
    for s in svc.sites().list().execute().get("siteEntry", []):
        if "socialtradingvlog" in s["siteUrl"]:
            site_url = s["siteUrl"]
            break
    if not site_url:
        return {"error": "Site not found in GSC"}

    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")

    overview = svc.searchanalytics().query(siteUrl=site_url, body={
        "startDate": start, "endDate": end, "dimensions": [], "rowLimit": 1
    }).execute()
    queries = svc.searchanalytics().query(siteUrl=site_url, body={
        "startDate": start, "endDate": end, "dimensions": ["query"], "rowLimit": 20
    }).execute()
    pages = svc.searchanalytics().query(siteUrl=site_url, body={
        "startDate": start, "endDate": end, "dimensions": ["page"], "rowLimit": 15
    }).execute()

    ov = overview.get("rows", [{}])[0] if overview.get("rows") else {}
    result = {
        "timestamp": time.time(),
        "period": {"start": start, "end": end},
        "overview": {
            "clicks": ov.get("clicks", 0),
            "impressions": ov.get("impressions", 0),
            "ctr": round(ov.get("ctr", 0), 4),
            "position": round(ov.get("position", 0), 1),
        },
        "queries": [{"query": r["keys"][0], "clicks": r["clicks"],
                     "impressions": r["impressions"], "position": round(r["position"], 1)}
                    for r in queries.get("rows", [])],
        "pages": [{"page": r["keys"][0].replace("https://socialtradingvlog.com", ""),
                   "clicks": r["clicks"], "impressions": r["impressions"],
                   "position": round(r["position"], 1)}
                  for r in pages.get("rows", [])],
    }
    GSC_CACHE.parent.mkdir(parents=True, exist_ok=True)
    GSC_CACHE.write_text(json.dumps(result, indent=2))
    return result


def get_gsc_history():
    """Read all GSC snapshots and build position history per query."""
    snapshots = sorted(PROJECT_DIR.glob("reports/gsc-*.json"))
    history = {}
    for snap_path in snapshots:
        try:
            data = json.loads(snap_path.read_text())
            date = data.get("date", snap_path.stem.replace("gsc-", ""))
            for q in data.get("queries", []):
                query = q["query"]
                if query not in history:
                    history[query] = []
                history[query].append({
                    "date": date,
                    "position": q["position"],
                    "clicks": q.get("clicks", 0),
                    "impressions": q.get("impressions", 0),
                })
        except Exception:
            continue
    return history


# ─── HTML UI ───

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>STV Rank Tracker</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  background:#f6f8fa;color:#1f2328;min-height:100vh}
a{color:#0969da;text-decoration:none}

/* Login */
.login-wrap{display:flex;align-items:center;justify-content:center;min-height:100vh}
.login-box{background:#fff;border:1px solid #d0d7de;border-radius:12px;padding:2.5rem;
  width:100%;max-width:380px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.login-box h1{font-size:1.4rem;margin-bottom:1.5rem;color:#1f2328}
.login-box input{width:100%;padding:.75rem 1rem;background:#fff;border:1px solid #d0d7de;
  border-radius:8px;color:#1f2328;font-size:1rem;margin-bottom:1rem;outline:none}
.login-box input:focus{border-color:#0969da;box-shadow:0 0 0 3px rgba(9,105,218,.15)}
.login-box button{width:100%;padding:.75rem;background:#1a7f37;border:none;border-radius:8px;
  color:#fff;font-size:1rem;font-weight:600;cursor:pointer}
.login-box button:hover{background:#116329}
.login-error{color:#cf222e;font-size:.9rem;margin-bottom:1rem;display:none}

/* Dashboard */
.dashboard{display:none;max-width:1200px;margin:0 auto;padding:1.5rem}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;
  flex-wrap:wrap;gap:.75rem;padding-bottom:1rem;border-bottom:1px solid #d0d7de}
header h1{font-size:1.4rem;color:#1f2328;font-weight:600}
.header-actions{display:flex;gap:.75rem;align-items:center}
.btn{padding:.45rem 1rem;border:1px solid #d0d7de;border-radius:8px;font-size:.85rem;
  font-weight:500;cursor:pointer;transition:background .15s;background:#fff;color:#1f2328}
.btn:hover{background:#f3f4f6;border-color:#adb5bd}
.btn-refresh{background:#0969da;color:#fff;border-color:#0969da}
.btn-refresh:hover{background:#0860ca;border-color:#0860ca}
.meta{color:#656d76;font-size:.8rem;margin-bottom:1.5rem}

/* Cards */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;
  margin-bottom:2rem}
.card{background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:1.25rem;
  box-shadow:0 1px 3px rgba(0,0,0,.04)}
.card-label{font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:#656d76;
  margin-bottom:.35rem}
.card-value{font-size:1.7rem;font-weight:700;color:#1f2328}

/* Tables */
.section{margin-bottom:2rem}
.section-header{display:flex;align-items:center;justify-content:space-between;
  margin-bottom:.75rem;gap:1rem;flex-wrap:wrap}
.section-header h2{font-size:1rem;color:#1f2328;font-weight:600;white-space:nowrap}
.filter-input{background:#fff;border:1px solid #d0d7de;border-radius:8px;
  color:#1f2328;font-size:.85rem;padding:.4rem .85rem;outline:none;width:220px}
.filter-input:focus{border-color:#0969da;box-shadow:0 0 0 3px rgba(9,105,218,.1)}
.filter-input::placeholder{color:#adb5bd}
.table-wrap{overflow-x:auto;border:1px solid #d0d7de;border-radius:10px;
  background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.04)}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th{background:#f6f8fa;color:#656d76;text-transform:uppercase;font-size:.68rem;
  letter-spacing:.05em;padding:.65rem 1rem;text-align:left;cursor:pointer;
  user-select:none;white-space:nowrap;border-bottom:1px solid #d0d7de}
th.cb-col{width:36px;cursor:default}
th:hover{color:#1f2328}
th.cb-col:hover{color:#656d76}
th.sorted-asc::after{content:" \25B2";font-size:.6rem}
th.sorted-desc::after{content:" \25BC";font-size:.6rem}
td{padding:.65rem 1rem;border-top:1px solid #eaeef2;color:#1f2328}
td.cb-col{padding:.4rem .5rem .4rem 1rem}
tr:hover td{background:#f6f8fa}
tr.kw-checked td{background:#ddf4ff}
.num{text-align:right;font-variant-numeric:tabular-nums}

/* Position badge */
.pos-badge{display:inline-block;font-size:.75rem;font-weight:700;padding:.15rem .55rem;
  border-radius:20px;color:#fff;min-width:32px;text-align:center}
.pos-1-3{background:#1a7f37}
.pos-4-10{background:#0969da}
.pos-11-20{background:#9a6700}
.pos-21plus{background:#adb5bd;color:#fff}

/* Delta */
.delta{font-size:.75rem;font-weight:600;white-space:nowrap}
.delta-up{color:#1a7f37}
.delta-dn{color:#cf222e}
.delta-eq{color:#adb5bd}

/* Checkbox */
input[type=checkbox]{width:14px;height:14px;accent-color:#0969da;cursor:pointer}

/* Spinner */
.spinner{display:none;width:18px;height:18px;border:2px solid #d0d7de;
  border-top-color:#0969da;border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* Chart */
.chart-section{margin-bottom:2rem}
.chart-section h2{font-size:1rem;color:#1f2328;font-weight:600;margin-bottom:.75rem}
.chart-wrap{background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:1.5rem;
  box-shadow:0 1px 3px rgba(0,0,0,.04)}
.chart-legend{display:flex;flex-wrap:wrap;gap:.75rem 1.5rem;margin-bottom:1rem}
.legend-item{display:flex;align-items:center;gap:.4rem;font-size:.8rem;color:#1f2328}
.legend-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.chart-hint{font-size:.75rem;color:#656d76;margin-top:.75rem}

@media(max-width:600px){
  .cards{grid-template-columns:repeat(2,1fr)}
  header h1{font-size:1.2rem}
  td,th{padding:.5rem .6rem;font-size:.8rem}
  .filter-input{width:100%}
}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>

<!-- Login Screen -->
<div class="login-wrap" id="loginScreen">
  <div class="login-box">
    <h1>STV Rank Tracker</h1>
    <div class="login-error" id="loginError"></div>
    <input type="password" id="passwordInput" placeholder="Password" autocomplete="current-password">
    <button onclick="doLogin()">Sign In</button>
  </div>
</div>

<!-- Dashboard -->
<div class="dashboard" id="dashboard">
  <header>
    <h1>STV Rank Tracker</h1>
    <div class="header-actions">
      <div class="spinner" id="spinner"></div>
      <button class="btn btn-refresh" onclick="doRefresh()">Refresh</button>
      <button class="btn btn-logout" onclick="doLogout()">Logout</button>
    </div>
  </header>
  <div class="meta" id="meta"></div>

  <div class="cards" id="cards"></div>

  <!-- Position History Chart -->
  <div class="chart-section" id="chartSection">
    <h2>Position History</h2>
    <div class="chart-wrap">
      <div class="chart-legend" id="chartLegend"></div>
      <canvas id="rankChart" height="110"></canvas>
      <div class="chart-hint">Tick keywords below to compare. Y-axis: lower position = higher ranking.</div>
    </div>
  </div>

  <!-- Keywords Table -->
  <div class="section">
    <div class="section-header">
      <h2>Top Keywords</h2>
      <input class="filter-input" id="kwFilter" placeholder="Filter keywords…" oninput="filterKeywords(this.value)">
    </div>
    <div class="table-wrap">
      <table id="keywordsTable">
        <thead><tr>
          <th class="cb-col"></th>
          <th data-key="query">Keyword</th>
          <th data-key="clicks" class="num">Clicks</th>
          <th data-key="impressions" class="num">Impr.</th>
          <th data-key="position" class="num">Position</th>
          <th class="num">Change</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <!-- Pages Table -->
  <div class="section">
    <div class="section-header">
      <h2>Top Pages</h2>
    </div>
    <div class="table-wrap">
      <table id="pagesTable">
        <thead><tr>
          <th data-key="page">Page</th>
          <th data-key="clicks" class="num">Clicks</th>
          <th data-key="impressions" class="num">Impr.</th>
          <th data-key="position" class="num">Position</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
</div>

<script>
const $ = s => document.querySelector(s);

let gscHistory = {};
let rankChart = null;
let checkedKeywords = [];
let allKeywords = [];
const CHART_COLORS = ['#58a6ff','#3fb950','#d29922','#f78166','#bc8cff'];
const MAX_CHART_KW = 5;

// Check if already logged in
fetch('/api/gsc-data').then(r => {
  if (r.ok) { r.json().then(showDashboard); }
});

$('#passwordInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') doLogin();
});

function doLogin() {
  const pw = $('#passwordInput').value;
  if (!pw) return;
  fetch('/api/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({password: pw})
  }).then(r => r.json()).then(d => {
    if (d.ok) {
      $('#loginScreen').style.display = 'none';
      loadData();
    } else {
      const el = $('#loginError');
      el.textContent = d.error || 'Login failed';
      el.style.display = 'block';
    }
  }).catch(() => {
    const el = $('#loginError');
    el.textContent = 'Connection error';
    el.style.display = 'block';
  });
}

function doLogout() {
  fetch('/api/logout', {method: 'POST'}).then(() => {
    $('#dashboard').style.display = 'none';
    $('#loginScreen').style.display = 'flex';
    $('#passwordInput').value = '';
  });
}

function loadData() {
  Promise.all([
    fetch('/api/gsc-data').then(r => {
      if (r.status === 401) {
        $('#dashboard').style.display = 'none';
        $('#loginScreen').style.display = 'flex';
        return null;
      }
      return r.json();
    }),
    fetch('/api/gsc-history').then(r => r.ok ? r.json() : {})
  ]).then(([data, history]) => {
    gscHistory = history || {};
    if (data) { showDashboard(data); renderChart(); }
  });
}

function doRefresh() {
  $('#spinner').style.display = 'block';
  fetch('/api/gsc-refresh', {method: 'POST'}).then(r => r.json()).then(d => {
    $('#spinner').style.display = 'none';
    if (d) showDashboard(d);
  }).catch(() => { $('#spinner').style.display = 'none'; });
}

function showDashboard(data) {
  $('#loginScreen').style.display = 'none';
  $('#dashboard').style.display = 'block';

  if (data.error) { $('#meta').textContent = data.error; return; }

  const ov = data.overview || {};
  const ts = data.timestamp ? new Date(data.timestamp * 1000).toLocaleString() : 'Unknown';
  const period = data.period ? data.period.start + ' — ' + data.period.end : '';
  $('#meta').textContent = 'Last updated: ' + ts + (period ? ' | ' + period : '');

  $('#cards').innerHTML = [
    card('Total Clicks', fmt(ov.clicks)),
    card('Total Impressions', fmt(ov.impressions)),
    card('Avg CTR', ((ov.ctr||0) * 100).toFixed(1) + '%'),
    card('Avg Position', ov.position || '-')
  ].join('');

  // Compute deltas from history, sort by clicks desc (most valuable first)
  const queries = (data.queries || []).map(q => {
    const hist = gscHistory[q.query] || [];
    const prev = hist.length >= 2 ? hist[hist.length - 2].position : null;
    const delta = prev !== null ? Math.round((prev - q.position) * 10) / 10 : null;
    return {...q, delta};
  }).sort((a, b) => b.clicks - a.clicks);
  allKeywords = queries;

  // Auto-select top keyword for chart
  checkedKeywords = [];
  if (queries.length > 0) checkedKeywords = [queries[0].query];

  fillKeywordsTable(queries);
  setupSort('keywordsTable', queries);
  fillTable('pagesTable', data.pages || [], ['page','clicks','impressions','position']);
  setupSort('pagesTable', data.pages || [], ['page','clicks','impressions','position']);
}

function posBadge(pos) {
  let cls = 'pos-21plus';
  if (pos <= 3) cls = 'pos-1-3';
  else if (pos <= 10) cls = 'pos-4-10';
  else if (pos <= 20) cls = 'pos-11-20';
  return '<span class="pos-badge ' + cls + '">' + pos + '</span>';
}

function deltaHtml(delta) {
  if (delta === null) return '<span class="delta delta-eq">—</span>';
  if (delta > 0) return '<span class="delta delta-up">&#9650; ' + delta + '</span>';
  if (delta < 0) return '<span class="delta delta-dn">&#9660; ' + Math.abs(delta) + '</span>';
  return '<span class="delta delta-eq">—</span>';
}

function fillKeywordsTable(rows) {
  const tbody = document.querySelector('#keywordsTable tbody');
  tbody.innerHTML = rows.map(r => {
    const checked = checkedKeywords.includes(r.query);
    const colorIdx = checkedKeywords.indexOf(r.query);
    const dotStyle = checked ? 'display:inline-block;width:8px;height:8px;border-radius:50%;background:' + CHART_COLORS[colorIdx] + ';margin-right:4px' : 'display:none';
    return '<tr class="' + (checked ? 'kw-checked' : '') + '" data-query="' + esc(r.query) + '">' +
      '<td class="cb-col"><input type="checkbox" ' + (checked ? 'checked' : '') + ' onchange="toggleKeyword(\'' + esc(r.query).replace(/'/g,"&#39;") + '\',this.checked)"></td>' +
      '<td><span style="' + dotStyle + '"></span>' + esc(r.query) + '</td>' +
      '<td class="num">' + fmt(r.clicks) + '</td>' +
      '<td class="num">' + fmt(r.impressions) + '</td>' +
      '<td class="num">' + posBadge(r.position) + '</td>' +
      '<td class="num">' + deltaHtml(r.delta) + '</td>' +
      '</tr>';
  }).join('');
}

function filterKeywords(text) {
  const q = text.toLowerCase();
  const filtered = q ? allKeywords.filter(r => r.query.toLowerCase().includes(q)) : allKeywords;
  fillKeywordsTable(filtered);
}

function toggleKeyword(query, checked) {
  if (checked) {
    if (checkedKeywords.length >= MAX_CHART_KW) {
      // Uncheck the checkbox visually
      event.target.checked = false;
      return;
    }
    checkedKeywords.push(query);
  } else {
    checkedKeywords = checkedKeywords.filter(k => k !== query);
  }
  // Re-render table to update dot colours
  filterKeywords($('#kwFilter').value);
  renderChart();
}

function renderChart() {
  const section = $('#chartSection');
  if (checkedKeywords.length === 0) {
    section.style.display = 'none';
    if (rankChart) { rankChart.destroy(); rankChart = null; }
    return;
  }

  section.style.display = 'block';

  // Build unified date labels across all selected keywords
  const dateSet = new Set();
  checkedKeywords.forEach(kw => {
    (gscHistory[kw] || []).forEach(h => dateSet.add(h.date));
  });
  const labels = Array.from(dateSet).sort();

  const datasets = checkedKeywords.map((kw, i) => {
    const hist = gscHistory[kw] || [];
    const byDate = {};
    hist.forEach(h => { byDate[h.date] = h.position; });
    return {
      label: kw,
      data: labels.map(d => byDate[d] != null ? byDate[d] : null),
      borderColor: CHART_COLORS[i],
      backgroundColor: CHART_COLORS[i] + '18',
      tension: 0.3,
      pointRadius: 5,
      pointHoverRadius: 7,
      spanGaps: true,
      fill: false,
    };
  });

  // Legend
  $('#chartLegend').innerHTML = checkedKeywords.map((kw, i) =>
    '<div class="legend-item"><span class="legend-dot" style="background:' + CHART_COLORS[i] + '"></span>' + esc(kw) + '</div>'
  ).join('');

  if (rankChart) rankChart.destroy();
  rankChart = new Chart($('#rankChart'), {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ctx.dataset.label + ': #' + ctx.parsed.y
          }
        }
      },
      scales: {
        y: {
          reverse: true,
          min: 1,
          title: { display: true, text: 'Position', color: '#8b949e', font: {size:11} },
          ticks: { color: '#8b949e', stepSize: 1 },
          grid: { color: '#21262d' },
        },
        x: {
          ticks: { color: '#8b949e', maxRotation: 30 },
          grid: { color: '#21262d' },
        }
      }
    }
  });
}

function card(label, value) {
  return '<div class="card"><div class="card-label">' + label +
    '</div><div class="card-value">' + value + '</div></div>';
}

function fmt(n) {
  return n != null ? Number(n).toLocaleString() : '-';
}

function fillTable(id, rows, keys) {
  const tbody = document.querySelector('#' + id + ' tbody');
  tbody.innerHTML = rows.map(r =>
    '<tr>' + keys.map(k =>
      '<td' + (k !== keys[0] ? ' class="num"' : '') + '>' +
      (k === 'position' ? posBadge(r[k]) : (typeof r[k] === 'number' ? fmt(r[k]) : esc(r[k]))) +
      '</td>'
    ).join('') + '</tr>'
  ).join('');
}

function setupSort(tableId, rows, keys) {
  const isKeywords = tableId === 'keywordsTable';
  const ths = document.querySelectorAll('#' + tableId + ' th[data-key]');
  ths.forEach(th => {
    th.addEventListener('click', () => {
      const key = th.dataset.key;
      if (!key) return;
      const asc = !th.classList.contains('sorted-asc');
      document.querySelectorAll('#' + tableId + ' th').forEach(t => t.classList.remove('sorted-asc','sorted-desc'));
      th.classList.add(asc ? 'sorted-asc' : 'sorted-desc');
      const sorted = [...rows].sort((a, b) => {
        const av = a[key], bv = b[key];
        if (typeof av === 'number') return asc ? av - bv : bv - av;
        return asc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
      });
      if (isKeywords) {
        allKeywords = sorted;
        fillKeywordsTable(sorted);
      } else {
        fillTable(tableId, sorted, keys || []);
      }
    });
  });
}

function esc(s) {
  if (s == null) return '';
  const d = document.createElement('div');
  d.textContent = String(s);
  return d.innerHTML;
}
</script>
</body>
</html>"""


# ─── Request handler ───

class DashboardHandler(BaseHTTPRequestHandler):
    require_auth = False

    def log_message(self, fmt, *args):
        pass  # Silence default logging

    def _send(self, code, body, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if isinstance(body, str):
            body = body.encode()
        self.wfile.write(body)

    def _send_json(self, code, obj):
        self._send(code, json.dumps(obj))

    def _get_cookie(self, name):
        cookie_header = self.headers.get("Cookie", "")
        cookie = SimpleCookie()
        cookie.load(cookie_header)
        if name in cookie:
            return cookie[name].value
        return None

    def _set_session_cookie(self, token):
        self.send_header(
            "Set-Cookie",
            f"stv_session={token}; Path=/; Max-Age=1209600; SameSite=Strict; HttpOnly"
        )

    def _clear_session_cookie(self):
        self.send_header(
            "Set-Cookie",
            "stv_session=; Path=/; Max-Age=0; SameSite=Strict; HttpOnly"
        )

    def _is_authed(self):
        if not self.require_auth:
            return True
        token = self._get_cookie("stv_session")
        return validate_session(token)

    def _client_ip(self):
        return self.headers.get("X-Real-IP", self.client_address[0])

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 10000:
            return None
        return self.rfile.read(length)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/":
            self._send(200, DASHBOARD_HTML, "text/html; charset=utf-8")
        elif path == "/api/gsc-data":
            if not self._is_authed():
                self._send_json(401, {"error": "Unauthorized"})
                return
            self._send_json(200, get_gsc_data())
        elif path == "/api/gsc-history":
            if not self._is_authed():
                self._send_json(401, {"error": "Unauthorized"})
                return
            self._send_json(200, get_gsc_history())
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/api/login":
            self._handle_login()
        elif path == "/api/logout":
            self._handle_logout()
        elif path == "/api/gsc-refresh":
            if not self._is_authed():
                self._send_json(401, {"error": "Unauthorized"})
                return
            try:
                data = fetch_gsc_data()
                self._send_json(200, data)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_login(self):
        ip = self._client_ip()
        if is_rate_limited(ip):
            self._send_json(429, {"error": "Too many attempts. Try again later."})
            return

        body = self._read_body()
        if not body:
            self._send_json(400, {"error": "Bad request"})
            return

        try:
            data = json.loads(body)
        except Exception:
            self._send_json(400, {"error": "Bad request"})
            return

        password = data.get("password", "")
        record_login_attempt(ip)

        if check_password(password):
            token = create_session()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-Content-Type-Options", "nosniff")
            self._set_session_cookie(token)
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
        else:
            self._send_json(401, {"error": "Invalid password"})

    def _handle_logout(self):
        token = self._get_cookie("stv_session")
        if token:
            destroy_session(token)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Content-Type-Options", "nosniff")
        self._clear_session_cookie()
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())


# ─── Main ───

def main():
    parser = argparse.ArgumentParser(description="STV Rank Tracker")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--auth", action="store_true")
    args = parser.parse_args()

    bind = "0.0.0.0" if args.public else "127.0.0.1"
    if args.auth or args.public:
        init_auth()
        DashboardHandler.require_auth = True

    server = HTTPServer((bind, args.port), DashboardHandler)
    print(f"STV Rank Tracker running at http://{bind}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
