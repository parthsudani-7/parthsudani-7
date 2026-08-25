import urllib.request
import json
import re
import os
import ssl
import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(assets_dir, exist_ok=True)

# ==============================================================================
# 1. GENERATE UNIFIED COMPETITIVE PROGRAMMING STATS CARD
# ==============================================================================
lc_total, lc_easy, lc_medium, lc_hard = 263, 112, 137, 14
cf_total, cf_easy, cf_medium, cf_hard = 114, 105, 6, 3
gfg_total, gfg_easy, gfg_medium, gfg_hard = 226, 110, 98, 18
cc_total, cc_easy, cc_medium, cc_hard = 171, 120, 43, 8

# Fetch LeetCode
try:
    url = "https://leetcode.com/graphql"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/json',
        'Referer': 'https://leetcode.com'
    }
    query = """
    query userProblemsSolved($username: String!) {
      matchedUser(username: $username) {
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """
    req = urllib.request.Request(url, data=json.dumps({"query": query, "variables": {"username": "ParthSudani"}}).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        ac = data.get('data', {}).get('matchedUser', {}).get('submitStatsGlobal', {}).get('acSubmissionNum', [])
        for item in ac:
            d = item.get('difficulty')
            c = item.get('count', 0)
            if d == 'All': lc_total = c
            elif d == 'Easy': lc_easy = c
            elif d == 'Medium': lc_medium = c
            elif d == 'Hard': lc_hard = c
    print(f"LeetCode fetched: {lc_total} (E: {lc_easy}, M: {lc_medium}, H: {lc_hard})")
except Exception as e:
    print(f"LeetCode fetch error (using fallback): {e}")

# Fetch Codeforces
try:
    req = urllib.request.Request("https://codeforces.com/api/user.status?handle=sudaniparth80", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
        cf_data = json.loads(resp.read().decode('utf-8'))
        if cf_data.get("status") == "OK":
            solved = {}
            for sub in cf_data.get("result", []):
                if sub.get("verdict") == "OK":
                    p = sub.get("problem", {})
                    p_id = f"{p.get('contestId')}_{p.get('index')}"
                    if p_id not in solved:
                        solved[p_id] = p.get('rating', 800)
            cf_total = len(solved)
            e, m, h = 0, 0, 0
            for r in solved.values():
                if r < 1200: e += 1
                elif r <= 1600: m += 1
                else: h += 1
            cf_easy, cf_medium, cf_hard = e, m, h
    print(f"Codeforces fetched: {cf_total} (E: {cf_easy}, M: {cf_medium}, H: {cf_hard})")
except Exception as e:
    print(f"Codeforces fetch error (using fallback): {e}")

# Fetch GFG
try:
    req = urllib.request.Request("https://www.geeksforgeeks.org/profile/sudanipzsd3/", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
        html = resp.read().decode('utf-8')
        m = re.search(r'\"total_problems_solved\":\s*(\d+)', html)
        if m:
            gfg_total = int(m.group(1))
            gfg_easy = int(gfg_total * 0.49)
            gfg_medium = int(gfg_total * 0.43)
            gfg_hard = gfg_total - gfg_easy - gfg_medium
    print(f"GFG fetched: {gfg_total} (E: {gfg_easy}, M: {gfg_medium}, H: {gfg_hard})")
except Exception as e:
    print(f"GFG fetch error (using fallback): {e}")

# Fetch CodeChef
try:
    req = urllib.request.Request("https://www.codechef.com/users/parth_sudani7", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
        html = resp.read().decode('utf-8')
        m = re.search(r'Total Problems Solved:\s*(\d+)', html, re.I)
        if m:
            cc_total = int(m.group(1))
            cc_easy = int(cc_total * 0.70)
            cc_medium = int(cc_total * 0.25)
            cc_hard = cc_total - cc_easy - cc_medium
    print(f"CodeChef fetched: {cc_total} (E: {cc_easy}, M: {cc_medium}, H: {cc_hard})")
except Exception as e:
    print(f"CodeChef fetch error (using fallback): {e}")

total_solved = lc_total + cf_total + gfg_total + cc_total
total_easy = lc_easy + cf_easy + gfg_easy + cc_easy
total_medium = lc_medium + cf_medium + gfg_medium + cc_medium
total_hard = lc_hard + cf_hard + gfg_hard + cc_hard

p_easy = (total_easy / total_solved) * 100 if total_solved > 0 else 0
p_medium = (total_medium / total_solved) * 100 if total_solved > 0 else 0
p_hard = (total_hard / total_solved) * 100 if total_solved > 0 else 0

w_easy = round((p_easy / 100) * 320, 1)
w_med = round((p_medium / 100) * 320, 1)
w_hard = round((p_hard / 100) * 320, 1)

svg_stats = f'''<svg width="680" height="340" viewBox="0 0 680 340" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    @keyframes pulse {{
      0%, 100% {{ transform: scale(1); opacity: 0.9; }}
      50% {{ transform: scale(1.03); opacity: 1; }}
    }}
    @keyframes fillEasy {{
      from {{ width: 0; }}
      to {{ width: {w_easy}px; }}
    }}
    @keyframes fillMed {{
      from {{ width: 0; }}
      to {{ width: {w_med}px; }}
    }}
    @keyframes fillHard {{
      from {{ width: 0; }}
      to {{ width: {w_hard}px; }}
    }}
    .glow-title {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 20px;
      font-weight: 700;
      fill: #38BDF8;
    }}
    .stat-label {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 13px;
      font-weight: 600;
      fill: #94A3B8;
    }}
    .stat-val {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 16px;
      font-weight: 700;
    }}
    .total-num {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 42px;
      font-weight: 800;
      fill: #F8FAFC;
    }}
    .total-sub {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 12px;
      font-weight: 600;
      fill: #38BDF8;
      letter-spacing: 1.5px;
      text-transform: uppercase;
    }}
    .platform-card {{
      fill: #131A26;
      stroke: #1E293B;
      stroke-width: 1.2;
      rx: 10;
    }}
    .platform-name {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 12px;
      font-weight: 600;
      fill: #94A3B8;
    }}
    .platform-num {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 15px;
      font-weight: 700;
      fill: #F1F5F9;
    }}
    .bar-bg {{
      fill: #1E293B;
      rx: 5;
    }}
    .bar-easy {{
      fill: url(#grad-easy);
      rx: 5;
      animation: fillEasy 1.5s ease-out forwards;
    }}
    .bar-med {{
      fill: url(#grad-med);
      rx: 5;
      animation: fillMed 1.5s ease-out forwards;
    }}
    .bar-hard {{
      fill: url(#grad-hard);
      rx: 5;
      animation: fillHard 1.5s ease-out forwards;
    }}
    .circle-pulse {{
      transform-origin: 110px 170px;
      animation: pulse 3s infinite ease-in-out;
    }}
  </style>

  <defs>
    <linearGradient id="card-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B0F17" />
      <stop offset="50%" stop-color="#0D1117" />
      <stop offset="100%" stop-color="#111827" />
    </linearGradient>
    <linearGradient id="border-glow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.8" />
      <stop offset="50%" stop-color="#818CF8" stop-opacity="0.3" />
      <stop offset="100%" stop-color="#A855F7" stop-opacity="0.8" />
    </linearGradient>
    <linearGradient id="grad-easy" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10B981" />
      <stop offset="100%" stop-color="#34D399" />
    </linearGradient>
    <linearGradient id="grad-med" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#F59E0B" />
      <stop offset="100%" stop-color="#FBBF24" />
    </linearGradient>
    <linearGradient id="grad-hard" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#EF4444" />
      <stop offset="100%" stop-color="#F87171" />
    </linearGradient>
    <radialGradient id="circle-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.25" />
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0" />
    </radialGradient>
  </defs>

  <rect x="2" y="2" width="676" height="336" rx="16" fill="url(#card-bg)" stroke="url(#border-glow)" stroke-width="1.8"/>

  <g transform="translate(32, 40)">
    <circle cx="10" cy="0" r="6" fill="#38BDF8"/>
    <circle cx="10" cy="0" r="10" fill="#38BDF8" fill-opacity="0.2"/>
    <text x="28" y="5" class="glow-title">⚡ Competitive Programming &amp; Problem Solving</text>
    <text x="590" y="5" class="stat-label" text-anchor="end">Live Analytics</text>
  </g>

  <g class="circle-pulse">
    <circle cx="110" cy="170" r="75" fill="url(#circle-glow)"/>
    <circle cx="110" cy="170" r="68" fill="#131A26" stroke="#1E293B" stroke-width="2"/>
    <circle cx="110" cy="170" r="68" fill="none" stroke="#38BDF8" stroke-width="3" stroke-dasharray="380" stroke-dashoffset="60" stroke-linecap="round"/>
    <text x="110" y="165" class="total-num" text-anchor="middle">{total_solved}</text>
    <text x="110" y="190" class="total-sub" text-anchor="middle">TOTAL SOLVED</text>
  </g>

  <g transform="translate(225, 95)">
    <g transform="translate(0, 0)">
      <text x="0" y="15" class="stat-label">Easy Solved</text>
      <text x="320" y="15" class="stat-val" fill="#34D399" text-anchor="end">{total_easy}</text>
      <rect x="0" y="24" width="320" height="10" class="bar-bg"/>
      <rect x="0" y="24" width="{w_easy}" height="10" class="bar-easy"/>
    </g>
    <g transform="translate(0, 52)">
      <text x="0" y="15" class="stat-label">Medium Solved</text>
      <text x="320" y="15" class="stat-val" fill="#FBBF24" text-anchor="end">{total_medium}</text>
      <rect x="0" y="24" width="320" height="10" class="bar-bg"/>
      <rect x="0" y="24" width="{w_med}" height="10" class="bar-med"/>
    </g>
    <g transform="translate(0, 104)">
      <text x="0" y="15" class="stat-label">Hard Solved</text>
      <text x="320" y="15" class="stat-val" fill="#F87171" text-anchor="end">{total_hard}</text>
      <rect x="0" y="24" width="320" height="10" class="bar-bg"/>
      <rect x="0" y="24" width="{w_hard}" height="10" class="bar-hard"/>
    </g>
  </g>

  <g transform="translate(32, 255)">
    <g transform="translate(0, 0)">
      <rect width="144" height="52" class="platform-card"/>
      <circle cx="18" cy="26" r="6" fill="#FFA116"/>
      <text x="32" y="23" class="platform-name">LeetCode</text>
      <text x="32" y="42" class="platform-num">{lc_total} Solved</text>
    </g>
    <g transform="translate(157, 0)">
      <rect width="144" height="52" class="platform-card"/>
      <circle cx="18" cy="26" r="6" fill="#2F8D46"/>
      <text x="32" y="23" class="platform-name">GeeksforGeeks</text>
      <text x="32" y="42" class="platform-num">{gfg_total} Solved</text>
    </g>
    <g transform="translate(314, 0)">
      <rect width="144" height="52" class="platform-card"/>
      <circle cx="18" cy="26" r="6" fill="#A0522D"/>
      <text x="32" y="23" class="platform-name">CodeChef</text>
      <text x="32" y="42" class="platform-num">{cc_total} Solved</text>
    </g>
    <g transform="translate(471, 0)">
      <rect width="144" height="52" class="platform-card"/>
      <circle cx="18" cy="26" r="6" fill="#1F8ACB"/>
      <text x="32" y="23" class="platform-name">Codeforces</text>
      <text x="32" y="42" class="platform-num">{cf_total} Solved</text>
    </g>
  </g>
</svg>
'''

with open(os.path.join(assets_dir, "competitive-stats.svg"), "w", encoding="utf-8") as f:
    f.write(svg_stats)

print("Generated assets/competitive-stats.svg")

# ==============================================================================
# 2. GENERATE CUSTOM CONTRIBUTION ACTIVITY GRAPH SVG (ZERO EXTERNAL DOWNTIME)
# ==============================================================================
username = "parthsudani-7"
days_to_show = 31
contributions = []

try:
    url = f"https://github-contributions-api.jogruber.de/v4/{username}?y=last"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        contributions = data.get('contributions', [])[-days_to_show:]
except Exception as e:
    print(f"Fallback contributions fetch: {e}")

if not contributions:
    today = datetime.date.today()
    contributions = [{"date": (today - datetime.timedelta(days=i)).isoformat(), "count": 0} for i in range(days_to_show-1, -1, -1)]

total_in_period = sum(c.get('count', 0) for c in contributions)
max_count = max(max((c.get('count', 0) for c in contributions), default=1), 5)

width = 820
height = 280
padding_left = 55
padding_right = 35
padding_top = 65
padding_bottom = 45

plot_w = width - padding_left - padding_right
plot_h = height - padding_top - padding_bottom

n = len(contributions)
step_x = plot_w / (n - 1) if n > 1 else plot_w

points = []
for i, c in enumerate(contributions):
    cnt = c.get('count', 0)
    x = padding_left + i * step_x
    y = padding_top + plot_h - (cnt / max_count) * plot_h
    points.append((x, y, cnt, c.get('date', '')))

# Smooth bezier path
path_d = f"M {points[0][0]:.1f},{points[0][1]:.1f}"
for i in range(len(points) - 1):
    p0 = points[max(i - 1, 0)]
    p1 = points[i]
    p2 = points[i + 1]
    p3 = points[min(i + 2, len(points) - 1)]
    cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
    cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
    cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
    cp2y = p2[1] - (p3[1] - p1[1]) / 6.0
    path_d += f" C {cp1x:.1f},{cp1y:.1f} {cp2x:.1f},{cp2y:.1f} {p2[0]:.1f},{p2[1]:.1f}"

area_d = path_d + f" L {points[-1][0]:.1f},{padding_top + plot_h:.1f} L {points[0][0]:.1f},{padding_top + plot_h:.1f} Z"

gridlines_svg = ""
for step in range(4):
    val = int(round((max_count / 3) * step))
    y_pos = padding_top + plot_h - (val / max_count) * plot_h
    gridlines_svg += f'<line x1="{padding_left}" y1="{y_pos:.1f}" x2="{width - padding_right}" y2="{y_pos:.1f}" stroke="#1E293B" stroke-dasharray="3 3"/>\n'
    gridlines_svg += f'<text x="{padding_left - 12}" y="{y_pos + 4:.1f}" class="axis-text" text-anchor="end">{val}</text>\n'

date_labels_svg = ""
for i in range(0, n, max(1, n // 5)):
    p = points[i]
    d_str = p[3]
    try:
        dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
        lbl = dt.strftime("%b %d")
    except:
        lbl = d_str
    date_labels_svg += f'<text x="{p[0]:.1f}" y="{height - 15}" class="axis-text" text-anchor="middle">{lbl}</text>\n'

dots_svg = ""
for p in points:
    if p[2] > 0:
        dots_svg += f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.5" fill="#38BDF8" stroke="#0D1117" stroke-width="2"/>\n'
        if p[2] >= max_count * 0.5:
            dots_svg += f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="7.5" fill="#38BDF8" fill-opacity="0.25"/>\n'

svg_graph = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    @keyframes drawLine {{
      from {{ stroke-dashoffset: 2000; }}
      to {{ stroke-dashoffset: 0; }}
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}
    .card-title {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 17px;
      font-weight: 700;
      fill: #F8FAFC;
    }}
    .card-subtitle {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 13px;
      font-weight: 600;
      fill: #38BDF8;
    }}
    .axis-text {{
      font-family: 'Segoe UI', Roboto, Ubuntu, sans-serif;
      font-size: 11px;
      font-weight: 500;
      fill: #64748B;
    }}
    .chart-line {{
      stroke-dasharray: 2000;
      animation: drawLine 2s ease-out forwards;
    }}
    .chart-area {{
      animation: fadeIn 1.5s ease-out forwards;
    }}
  </style>

  <defs>
    <linearGradient id="graph-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B0F17" />
      <stop offset="50%" stop-color="#0D1117" />
      <stop offset="100%" stop-color="#111827" />
    </linearGradient>
    <linearGradient id="area-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#A855F7" stop-opacity="0.45" />
      <stop offset="50%" stop-color="#38BDF8" stop-opacity="0.15" />
      <stop offset="100%" stop-color="#0D1117" stop-opacity="0.0" />
    </linearGradient>
    <linearGradient id="line-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#A855F7" />
      <stop offset="50%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#00F2FE" />
    </linearGradient>
    <linearGradient id="border-glow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.6" />
      <stop offset="50%" stop-color="#818CF8" stop-opacity="0.2" />
      <stop offset="100%" stop-color="#A855F7" stop-opacity="0.6" />
    </linearGradient>
  </defs>

  <rect x="2" y="2" width="{width - 4}" height="{height - 4}" rx="12" fill="url(#graph-bg)" stroke="url(#border-glow)" stroke-width="1.5"/>

  <g transform="translate(30, 36)">
    <circle cx="6" cy="0" r="4" fill="#38BDF8"/>
    <circle cx="6" cy="0" r="8" fill="#38BDF8" fill-opacity="0.2"/>
    <text x="20" y="5" class="card-title">📈 Contribution Activity Curve</text>
    <text x="{width - 60}" y="5" class="card-subtitle" text-anchor="end">{total_in_period} Contributions in Last {days_to_show} Days</text>
  </g>

  {gridlines_svg}
  <path d="{area_d}" fill="url(#area-grad)" class="chart-area" />
  <path d="{path_d}" fill="none" stroke="url(#line-grad)" stroke-width="3" stroke-linecap="round" class="chart-line" />
  {dots_svg}
  {date_labels_svg}
</svg>
'''

with open(os.path.join(assets_dir, "activity-graph.svg"), "w", encoding="utf-8") as f:
    f.write(svg_graph)

print("Generated assets/activity-graph.svg")
