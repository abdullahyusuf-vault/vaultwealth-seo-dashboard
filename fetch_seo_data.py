#!/usr/bin/env python3
"""
SEO Dashboard — VaultWealth
Fetches keyword performance from Google Search Console and generates dashboard.html

Usage:
  python fetch_seo_data.py

Requirements:
  pip install google-auth google-api-python-client

Place your service account JSON file as 'credentials.json' in this folder.
"""

import json
import os
import sys
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────
CREDENTIALS_FILE = "credentials.json"   # Your service account JSON file
SITE_URL         = "sc-domain:vaultwealth.com"
OUTPUT_HTML      = "seo_dashboard.html"
DAYS_LOOKBACK    = 28  # How many days of data to pull

KEYWORDS = [
    "wealth management UAE",
    "wealth management Dubai",
    "private wealth management UAE",
    "financial advisor UAE",
    "financial advisor Dubai",
    "investment advisor UAE",
    "financial planning Dubai",
    "wealth advisor UAE",
    "portfolio management UAE",
    "investment management Dubai",
    "asset management UAE",
    "wealth management for expats UAE",
    "high net worth wealth management UAE",
    "private banking UAE",
    "financial advisor Dubai for expats",
    "expat wealth management UAE",
    "investment advisor for expats Dubai",
    "UK expat financial advisor Dubai",
    "retirement planning UAE expats",
    "offshore investment advice UAE",
    "international wealth management Dubai",
    "cross-border financial planning UAE",
    "investment opportunities UAE",
    "passive income investments UAE",
    "monthly income investments UAE",
    "diversified investment portfolio UAE",
    "fixed income investments Dubai",
    "alternative investments UAE",
    "global investment opportunities Dubai",
    "ETF investing UAE",
    "portfolio diversification UAE",
    "wealth management firm Dubai",
    "financial advisor near me UAE",
    "financial planning firm Dubai",
    "investment advisor Abu Dhabi",
    "wealth manager Dubai DIFC",
    "private wealth firm UAE",
    "how to invest in UAE",
    "best investments in UAE",
    "how to build wealth in Dubai",
    "investment strategies for expats UAE",
    "tax planning for expats UAE",
    "retirement planning Dubai guide",
    "UAE wealth management guide",
    "how to create passive income UAE",
]

# ──────────────────────────────────────────────────────────────
# INSTALL DEPENDENCIES IF MISSING
# ──────────────────────────────────────────────────────────────
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("Installing required libraries...")
    os.system(f'"{sys.executable}" -m pip install google-auth google-api-python-client')
    from google.oauth2 import service_account
    from googleapiclient.discovery import build


# ──────────────────────────────────────────────────────────────
# GSC API HELPERS
# ──────────────────────────────────────────────────────────────
def get_gsc_service():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
    )
    return build("searchconsole", "v1", credentials=credentials)


def fetch_keyword_data(service, keyword):
    end_date   = datetime.now().date()
    start_date = end_date - timedelta(days=DAYS_LOOKBACK)

    request = {
        "startDate": str(start_date),
        "endDate":   str(end_date),
        "dimensions": ["query", "page"],
        "dimensionFilterGroups": [{
            "filters": [{
                "dimension":  "query",
                "operator":   "equals",
                "expression": keyword
            }]
        }],
        "rowLimit": 1
    }

    try:
        response = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body=request
        ).execute()

        rows = response.get("rows", [])

        if not rows:
            return {
                "keyword":     keyword,
                "position":    None,
                "clicks":      0,
                "impressions": 0,
                "ctr":         0.0,
                "top_page":    "Not ranking"
            }

        row = rows[0]
        return {
            "keyword":     keyword,
            "position":    round(row["position"], 1),
            "clicks":      int(row["clicks"]),
            "impressions": int(row["impressions"]),
            "ctr":         round(row["ctr"] * 100, 2),
            "top_page":    row["keys"][1] if len(row["keys"]) > 1 else "Unknown"
        }

    except Exception as e:
        print(f"    ⚠ Error: {e}")
        return {
            "keyword":     keyword,
            "position":    None,
            "clicks":      0,
            "impressions": 0,
            "ctr":         0.0,
            "top_page":    "Error"
        }


# ──────────────────────────────────────────────────────────────
# HTML DASHBOARD TEMPLATE
# ──────────────────────────────────────────────────────────────
def generate_html(data, last_updated):
    data_json = json.dumps(data, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>SEO Dashboard — VaultWealth</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{
      font-family: -apple-system, 'Inter', sans-serif;
      background: #0c0e1a;
      color: #e2e8f0;
    }}
    .card {{ background: #161929; border: 1px solid #252840; border-radius: 12px; }}
    .tbl-header {{ background: #0f1120; position: sticky; top: 0; z-index: 10; }}
    .tbl-row:hover td {{ background: #1a1e32 !important; }}
    .pos-1-3   {{ background: #052e16; color: #4ade80; }}
    .pos-4-10  {{ background: #422006; color: #fbbf24; }}
    .pos-11-20 {{ background: #431407; color: #f97316; }}
    .pos-21    {{ background: #3b0d0d; color: #f87171; }}
    .pos-none  {{ background: #1f2937; color: #6b7280; }}
    input, select {{
      background: #161929;
      border: 1px solid #252840;
      color: #e2e8f0;
      border-radius: 8px;
      padding: 8px 14px;
      font-size: 14px;
      outline: none;
    }}
    input:focus, select:focus {{ border-color: #6366f1; }}
    th {{ cursor: pointer; user-select: none; white-space: nowrap; }}
    th:hover {{ color: #a5b4fc; }}
    .bar {{
      height: 4px;
      border-radius: 2px;
      background: #6366f1;
      margin-top: 4px;
    }}
  </style>
</head>
<body class="min-h-screen">

  <div class="max-w-7xl mx-auto px-6 py-8">

    <!-- Header -->
    <div class="flex flex-wrap items-start justify-between gap-4 mb-8">
      <div>
        <div class="flex items-center gap-3 mb-1">
          <div class="w-3 h-3 rounded-full bg-indigo-500"></div>
          <span class="text-slate-400 text-sm font-medium uppercase tracking-widest">VaultWealth</span>
        </div>
        <h1 class="text-3xl font-bold text-white tracking-tight">SEO Dashboard</h1>
        <p class="text-slate-500 text-sm mt-1">sc-domain:vaultwealth.com &nbsp;·&nbsp; Last {DAYS_LOOKBACK} days &nbsp;·&nbsp; Updated {last_updated}</p>
      </div>
      <button onclick="window.location.reload()" class="text-xs text-slate-500 border border-slate-700 rounded-lg px-3 py-2 hover:text-slate-300 hover:border-slate-500 transition">
        ↻ Refresh
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8" id="summary-cards"></div>

    <!-- Filter Bar -->
    <div class="card p-4 mb-5 flex flex-wrap gap-3 items-center">
      <input type="text" id="kw-search" placeholder="🔍  Filter keywords…" oninput="applyFilters()" class="flex-1 min-w-48"/>
      <select id="pos-filter" onchange="applyFilters()">
        <option value="all">All positions</option>
        <option value="top3">Top 3</option>
        <option value="top10">Top 10</option>
        <option value="11-20">Position 11–20</option>
        <option value="21plus">Position 21+</option>
        <option value="none">Not ranking</option>
      </select>
      <span class="text-slate-500 text-xs ml-auto" id="result-count"></span>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="tbl-header text-slate-400 text-xs uppercase tracking-wider">
              <th class="text-left px-5 py-4" onclick="doSort('keyword')">
                Keyword <span id="s-keyword" class="text-indigo-400"></span>
              </th>
              <th class="text-center px-4 py-4 w-24" onclick="doSort('position')">
                Rank <span id="s-position" class="text-indigo-400">↑</span>
              </th>
              <th class="text-center px-4 py-4 w-24" onclick="doSort('clicks')">
                Clicks <span id="s-clicks" class="text-indigo-400"></span>
              </th>
              <th class="text-center px-4 py-4 w-28" onclick="doSort('impressions')">
                Impr. <span id="s-impressions" class="text-indigo-400"></span>
              </th>
              <th class="text-center px-4 py-4 w-20" onclick="doSort('ctr')">
                CTR <span id="s-ctr" class="text-indigo-400"></span>
              </th>
              <th class="text-left px-4 py-4">Ranking Page</th>
            </tr>
          </thead>
          <tbody id="tbl-body"></tbody>
        </table>
      </div>
    </div>

    <p class="text-center text-slate-700 text-xs mt-5">
      Data from Google Search Console · VaultWealth SEO Dashboard
    </p>
  </div>

  <script>
    const ALL_DATA = {data_json};
    let view = [...ALL_DATA];
    let sortState = {{ key: 'position', asc: true }};

    // ── Summary Cards ──────────────────────────────────────
    function renderCards() {{
      const ranked = ALL_DATA.filter(d => d.position !== null);
      const top3   = ranked.filter(d => d.position <= 3).length;
      const top10  = ranked.filter(d => d.position <= 10).length;
      const clicks = ALL_DATA.reduce((s, d) => s + d.clicks, 0);
      const impr   = ALL_DATA.reduce((s, d) => s + d.impressions, 0);

      const cards = [
        {{ label: 'Keywords Tracked', value: ALL_DATA.length,              color: 'text-indigo-400', icon: '🔑' }},
        {{ label: 'In Top 10',         value: top10,                        color: 'text-green-400',  icon: '🏆' }},
        {{ label: 'Total Clicks',      value: clicks.toLocaleString(),      color: 'text-blue-400',   icon: '👆' }},
        {{ label: 'Impressions',       value: impr.toLocaleString(),        color: 'text-purple-400', icon: '👁' }},
      ];

      document.getElementById('summary-cards').innerHTML = cards.map(c => `
        <div class="card px-5 py-4">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-lg">${{c.icon}}</span>
            <span class="text-slate-400 text-xs uppercase tracking-wider">${{c.label}}</span>
          </div>
          <div class="text-2xl font-bold ${{c.color}}">${{c.value}}</div>
        </div>
      `).join('');
    }}

    // ── Position Badge ────────────────────────────────────
    function posBadge(pos) {{
      if (pos === null) return `<span class="pos-none px-2 py-1 rounded text-xs font-semibold">—</span>`;
      const cls = pos <= 3 ? 'pos-1-3' : pos <= 10 ? 'pos-4-10' : pos <= 20 ? 'pos-11-20' : 'pos-21';
      return `<span class="${{cls}} px-2 py-1 rounded text-xs font-bold">${{pos}}</span>`;
    }}

    // ── Format Page URL ───────────────────────────────────
    function fmtPage(url) {{
      if (!url || url === 'Not ranking' || url === 'Error')
        return `<span class="text-slate-600 text-xs">${{url || '—'}}</span>`;
      const short = url.replace(/^https?:\/\//, '').replace(/\/$/, '');
      return `<a href="${{url}}" target="_blank" title="${{url}}"
        class="text-indigo-400 hover:text-indigo-300 text-xs block max-w-xs truncate transition">
        ${{short}}
      </a>`;
    }}

    // ── Render Table ──────────────────────────────────────
    function renderTable() {{
      const tbody = document.getElementById('tbl-body');
      tbody.innerHTML = view.map((d, i) => `
        <tr class="tbl-row border-t border-[#1e2235]">
          <td class="px-5 py-3 text-slate-200 font-medium">${{d.keyword}}</td>
          <td class="px-4 py-3 text-center">${{posBadge(d.position)}}</td>
          <td class="px-4 py-3 text-center text-slate-300">${{d.clicks.toLocaleString()}}</td>
          <td class="px-4 py-3 text-center text-slate-300">${{d.impressions.toLocaleString()}}</td>
          <td class="px-4 py-3 text-center text-slate-300">${{d.ctr}}%</td>
          <td class="px-4 py-3">${{fmtPage(d.top_page)}}</td>
        </tr>
      `).join('') || `<tr><td colspan="6" class="text-center text-slate-500 py-10">No results match your filter.</td></tr>`;

      document.getElementById('result-count').textContent =
        `Showing ${{view.length}} of ${{ALL_DATA.length}} keywords`;
    }}

    // ── Sort ──────────────────────────────────────────────
    function doSort(key) {{
      ['keyword','position','clicks','impressions','ctr'].forEach(k =>
        document.getElementById('s-' + k).textContent = '');

      if (sortState.key === key) {{
        sortState.asc = !sortState.asc;
      }} else {{
        sortState = {{ key, asc: key === 'position' }};
      }}

      document.getElementById('s-' + key).textContent = sortState.asc ? '↑' : '↓';
      sortView();
      renderTable();
    }}

    function sortView() {{
      const {{ key, asc }} = sortState;
      view.sort((a, b) => {{
        let va = a[key], vb = b[key];
        if (va === null) va = asc ?  9999 : -9999;
        if (vb === null) vb = asc ?  9999 : -9999;
        if (typeof va === 'string') return asc ? va.localeCompare(vb) : vb.localeCompare(va);
        return asc ? va - vb : vb - va;
      }});
    }}

    // ── Filter ────────────────────────────────────────────
    function applyFilters() {{
      const search = document.getElementById('kw-search').value.toLowerCase();
      const pf     = document.getElementById('pos-filter').value;

      view = ALL_DATA.filter(d => {{
        const ms = d.keyword.toLowerCase().includes(search);
        let mp = true;
        if      (pf === 'top3')   mp = d.position !== null && d.position <= 3;
        else if (pf === 'top10')  mp = d.position !== null && d.position <= 10;
        else if (pf === '11-20')  mp = d.position !== null && d.position > 10 && d.position <= 20;
        else if (pf === '21plus') mp = d.position !== null && d.position > 20;
        else if (pf === 'none')   mp = d.position === null;
        return ms && mp;
      }});

      sortView();
      renderTable();
    }}

    // ── Init ──────────────────────────────────────────────
    renderCards();
    sortView();
    renderTable();
    document.getElementById('s-position').textContent = '↑';
  </script>
</body>
</html>"""


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"\n❌  '{CREDENTIALS_FILE}' not found.")
        print(f"    Place your Google service account JSON file in the same folder as this script,")
        print(f"    renamed to 'credentials.json'.\n")
        sys.exit(1)

    print(f"\n🔗  Connecting to Google Search Console ({SITE_URL})...\n")

    try:
        service = get_gsc_service()
    except Exception as e:
        print(f"❌  Authentication failed: {e}\n")
        sys.exit(1)

    print(f"📊  Fetching {len(KEYWORDS)} keywords (last {DAYS_LOOKBACK} days)...\n")

    results = []
    for i, kw in enumerate(KEYWORDS):
        print(f"  [{i+1:2d}/{len(KEYWORDS)}]  {kw}")
        results.append(fetch_keyword_data(service, kw))

    # Sort by position (ranked first, then unranked)
    results.sort(key=lambda x: x["position"] if x["position"] is not None else 9999)

    last_updated = datetime.now().strftime("%B %d, %Y at %H:%M")
    html = generate_html(results, last_updated)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    ranked = sum(1 for r in results if r["position"] is not None)
    top10  = sum(1 for r in results if r["position"] and r["position"] <= 10)

    print(f"\n✅  Done!")
    print(f"    Ranked keywords : {ranked}/{len(KEYWORDS)}")
    print(f"    In top 10       : {top10}")
    print(f"    Dashboard saved : {OUTPUT_HTML}")
    print(f"\n    Open {OUTPUT_HTML} in your browser to view.\n")


if __name__ == "__main__":
    main()
