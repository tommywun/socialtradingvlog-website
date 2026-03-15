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
  background:#0f1117;color:#e1e4e8;min-height:100vh}
a{color:#58a6ff;text-decoration:none}

/* Login */
.login-wrap{display:flex;align-items:center;justify-content:center;min-height:100vh}
.login-box{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:2.5rem;
  width:100%;max-width:380px;text-align:center}
.login-box h1{font-size:1.4rem;margin-bottom:1.5rem;color:#f0f6fc}
.login-box input{width:100%;padding:.75rem 1rem;background:#0d1117;border:1px solid #30363d;
  border-radius:8px;color:#e1e4e8;font-size:1rem;margin-bottom:1rem;outline:none}
.login-box input:focus{border-color:#58a6ff}
.login-box button{width:100%;padding:.75rem;background:#238636;border:none;border-radius:8px;
  color:#fff;font-size:1rem;font-weight:600;cursor:pointer}
.login-box button:hover{background:#2ea043}
.login-error{color:#f85149;font-size:.9rem;margin-bottom:1rem;display:none}

/* Dashboard */
.dashboard{display:none;max-width:1100px;margin:0 auto;padding:1.5rem}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;
  flex-wrap:wrap;gap:.75rem}
header h1{font-size:1.5rem;color:#f0f6fc}
.header-actions{display:flex;gap:.75rem;align-items:center}
.btn{padding:.5rem 1rem;border:none;border-radius:8px;font-size:.85rem;font-weight:600;
  cursor:pointer;transition:background .15s}
.btn-refresh{background:#1f6feb;color:#fff}
.btn-refresh:hover{background:#388bfd}
.btn-logout{background:#21262d;color:#c9d1d9;border:1px solid #30363d}
.btn-logout:hover{background:#30363d}
.meta{color:#8b949e;font-size:.8rem;margin-bottom:1.5rem}

/* Cards */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;
  margin-bottom:2rem}
.card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:1.25rem}
.card-label{font-size:.75rem;text-transform:uppercase;letter-spacing:.05em;color:#8b949e;
  margin-bottom:.35rem}
.card-value{font-size:1.6rem;font-weight:700;color:#f0f6fc}

/* Tables */
.section{margin-bottom:2rem}
.section h2{font-size:1.1rem;color:#f0f6fc;margin-bottom:.75rem}
.table-wrap{overflow-x:auto;border:1px solid #30363d;border-radius:10px}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th{background:#161b22;color:#8b949e;text-transform:uppercase;font-size:.7rem;
  letter-spacing:.05em;padding:.65rem 1rem;text-align:left;cursor:pointer;
  user-select:none;white-space:nowrap}
th:hover{color:#c9d1d9}
th.sorted-asc::after{content:" \25B2";font-size:.6rem}
th.sorted-desc::after{content:" \25BC";font-size:.6rem}
td{padding:.6rem 1rem;border-top:1px solid #21262d;color:#c9d1d9}
tr:hover td{background:#161b22}
.num{text-align:right;font-variant-numeric:tabular-nums}

/* Spinner */
.spinner{display:none;width:18px;height:18px;border:2px solid #30363d;
  border-top-color:#58a6ff;border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

@media(max-width:600px){
  .cards{grid-template-columns:repeat(2,1fr)}
  header h1{font-size:1.2rem}
  td,th{padding:.5rem .6rem;font-size:.8rem}
}
</style>
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

  <div class="section">
    <h2>Top Keywords</h2>
    <div class="table-wrap">
      <table id="keywordsTable">
        <thead><tr>
          <th data-key="query">Keyword</th>
          <th data-key="clicks" class="num">Clicks</th>
          <th data-key="impressions" class="num">Impressions</th>
          <th data-key="position" class="num">Position</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="section">
    <h2>Top Pages</h2>
    <div class="table-wrap">
      <table id="pagesTable">
        <thead><tr>
          <th data-key="page">Page</th>
          <th data-key="clicks" class="num">Clicks</th>
          <th data-key="impressions" class="num">Impressions</th>
          <th data-key="position" class="num">Position</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
</div>

<script>
const $ = s => document.querySelector(s);

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
  fetch('/api/gsc-data').then(r => {
    if (r.status === 401) {
      $('#dashboard').style.display = 'none';
      $('#loginScreen').style.display = 'flex';
      return;
    }
    return r.json();
  }).then(d => { if (d) showDashboard(d); });
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

  if (data.error) {
    $('#meta').textContent = data.error;
    return;
  }

  const ov = data.overview || {};
  const ts = data.timestamp ? new Date(data.timestamp * 1000).toLocaleString() : 'Unknown';
  const period = data.period ? data.period.start + ' to ' + data.period.end : '';
  $('#meta').textContent = 'Last updated: ' + ts + (period ? ' | ' + period : '');

  $('#cards').innerHTML = [
    card('Total Clicks', fmt(ov.clicks)),
    card('Total Impressions', fmt(ov.impressions)),
    card('Avg CTR', (ov.ctr * 100).toFixed(1) + '%'),
    card('Avg Position', ov.position || '-')
  ].join('');

  fillTable('keywordsTable', data.queries || [], ['query','clicks','impressions','position']);
  fillTable('pagesTable', data.pages || [], ['page','clicks','impressions','position']);
  setupSort('keywordsTable', data.queries || [], ['query','clicks','impressions','position']);
  setupSort('pagesTable', data.pages || [], ['page','clicks','impressions','position']);
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
      (k === 'position' ? r[k] : (typeof r[k] === 'number' ? fmt(r[k]) : esc(r[k]))) +
      '</td>'
    ).join('') + '</tr>'
  ).join('');
}

function setupSort(tableId, rows, keys) {
  const ths = document.querySelectorAll('#' + tableId + ' th');
  ths.forEach(th => {
    th.addEventListener('click', () => {
      const key = th.dataset.key;
      const asc = !th.classList.contains('sorted-asc');
      ths.forEach(t => { t.classList.remove('sorted-asc','sorted-desc'); });
      th.classList.add(asc ? 'sorted-asc' : 'sorted-desc');
      const sorted = [...rows].sort((a, b) => {
        const av = a[key], bv = b[key];
        if (typeof av === 'number') return asc ? av - bv : bv - av;
        return asc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
      });
      fillTable(tableId, sorted, keys);
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
