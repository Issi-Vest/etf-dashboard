import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

print("=== DEBUT WEB.PY ===")

try:
    import yfinance as yf
    print("yfinance OK")
except Exception as e:
    print(f"ERREUR yfinance: {e}")

try:
    import pandas as pd
    print("pandas OK")
except Exception as e:
    print(f"ERREUR pandas: {e}")

now = datetime.now(ZoneInfo("Europe/Paris"))
print(f"Heure: {now}")

# =========================
# STRUCTURE DES BLOCS
# =========================

# Paires (gauche, droite) — None si pas de paire
BLOCS = {
    "Indices actions": [
        ("SP500",        "^GSPC",     "PSP5",           "PSP5.PA"),
        ("NDQ",          "^NDX",      "PUST",           "PUST.PA"),
        ("DAX",          "^GDAXI",    "CG1 (DAX)",      "CG1.PA"),
        ("PX1GR (CAC)",  "PX1GR.PA",  "CACC (CAC GR)",  "CACC.PA"),
        ("EURO STOXX 50","^STOXX50E", "PDJE",           "PDJE.PA"),
        ("DJI",          "^DJI",      "MFED",           "MFED.PA"),
        ("RUSSELL 2000", "^RUT",      "RS2K",           "RS2K.PA"),
    ],
    "Matières premières": [
        ("XAUUSD",  "GC=F",   "4GLD (XETRA)", "4GLD.DE"),
        ("XAGUSD",  "SI=F",   None,            None),
        ("UKOIL",   "BZ=F",   "NRJ",           "NRJ.PA"),
        ("HG1!",    "HG=F",   "COPAP",         "COPAP.PA"),
        ("ALUM",    "ALUM.L", None,            None),
        ("DBC",     "DBC",    "ICOM",          "ICOM.L"),
    ],
    "Crypto": [
        ("BTCUSDT", "BTC-USD", "ETHUSDT", "ETH-USD"),
        ("XRPUSDT", "XRP-USD", "SOLUSDT", "SOL-USD"),
        ("Total2",  None,      "Total3",  None),
    ],
    "Autres actions": [
        ("NVDA",  "NVDA",    "MSFT",  "MSFT"),
        ("TSLA",  "TSLA",    "MC",    "MC.PA"),
        ("HO",    "HO.PA",   "ALFPC", "ALFPC.PA"),
        ("BUCN",  "BUCN.SW", "PM",    "PM"),
    ],
}

# Devises : lignes spéciales
DEVISES = [
    [("USDEUR", "USDEUR=X"), ("EURUSD", "EURUSD=X")],
    [("DXY",    "DX-Y.NYB")],
    [("CHFEUR", "CHFEUR=X"), ("EURCHF", "EURCHF=X")],
]

# Fundsmith : grille 2 colonnes
FUNDSMITH = [
    ("Marriott",    "MAR"),
    ("Waters",      "WAT"),
    ("L'Oréal",     "OR.PA"),
    ("Visa",        "V"),
    ("Amadeus",     "AMS.MC"),
    ("Stryker",     "SYK"),
    ("Alphabet",    "GOOGL"),
    ("Meta",        "META"),
    ("Microsoft",   "MSFT"),
    ("ADP",         "ADP"),
]

# =========================
# FETCH
# =========================
def fetch_data(ticker):
    if ticker is None:
        return None
    try:
        print(f"  -> fetch {ticker}")
        df = yf.download(ticker, period="2y", interval="1d",
                         progress=False, auto_adjust=False, threads=False)
        if df is None or df.empty:
            print(f"  -> vide")
            return None

        close = df["Close"]
        if hasattr(close, "squeeze"):
            close = close.squeeze()
        if not isinstance(close, pd.Series):
            return None
        close = close.dropna()

        if len(close) < 63:
            return None

        sma200 = close.rolling(200).mean()

        # Calcul des indicateurs
        v1m = (close.iloc[-1] - close.iloc[-21]) / close.iloc[-21] * 100 if len(close) >= 21 else 0
        v3m = (close.iloc[-1] - close.iloc[-63]) / close.iloc[-63] * 100 if len(close) >= 63 else 0
        v6m = (close.iloc[-1] - close.iloc[-126]) / close.iloc[-126] * 100 if len(close) >= 126 else 0
        v1y_raw = (close.iloc[-1] - close.iloc[-252]) / close.iloc[-252] * 100 if len(close) >= 252 else v6m
        adm136 = (v1m + v3m + v6m) / 3 - 3
        v1y_minus3 = v1y_raw - 3
        sma200_last = float(sma200.iloc[-1]) if not pd.isna(sma200.iloc[-1]) else 0
        mm200 = (float(close.iloc[-1]) - sma200_last) / sma200_last * 100 if sma200_last else 0

        # Signal jour par jour pour les zones colorées
        signals_daily = []
        for i in range(len(close)):
            if i < 21:
                signals_daily.append(None)
                continue
            vm1 = (close.iloc[i] - close.iloc[i-21]) / close.iloc[i-21] * 100
            vm3 = (close.iloc[i] - close.iloc[i-63]) / close.iloc[i-63] * 100 if i >= 63 else vm1
            vm6 = (close.iloc[i] - close.iloc[i-126]) / close.iloc[i-126] * 100 if i >= 126 else vm1
            adm = (vm1 + vm3 + vm6) / 3 - 3
            v1y_r = (close.iloc[i] - close.iloc[i-252]) / close.iloc[i-252] * 100 if i >= 252 else vm6
            v1y_m3 = v1y_r - 3
            if adm > 0:
                signals_daily.append("green")
            elif adm < 0 and v1y_m3 > 0:
                signals_daily.append("orange")
            else:
                signals_daily.append("red")

        dates_all = [d.strftime("%Y-%m-%d") for d in close.index]
        close_all = [round(float(v), 4) for v in close]
        sma200_all = [round(float(v), 4) if not pd.isna(v) else None for v in sma200]

        n1y = min(252, len(close))

        return {
            "dates_1y": dates_all[-n1y:],
            "close_1y": close_all[-n1y:],
            "sma200_1y": sma200_all[-n1y:],
            "signals_1y": signals_daily[-n1y:],
            "dates_2y": dates_all,
            "close_2y": close_all,
            "sma200_2y": sma200_all,
            "signals_2y": signals_daily,
            "adm136": round(float(adm136), 1),
            "v1y": round(float(v1y_minus3), 1),
            "mm200": round(float(mm200), 1),
            "last": round(float(close.iloc[-1]), 4),
        }
    except Exception as e:
        print(f"  -> ERREUR: {e}")
        return None

def indicator_color(value):
    return "#1a7f37" if value >= 0 else "#d1242f"

def fmt(value):
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%".replace(".", ",")

def fmt_price(value):
    if value is None:
        return "-"
    if value >= 100:
        return f"{value:.2f}"
    elif value >= 1:
        return f"{value:.4f}"
    else:
        return f"{value:.6f}"

# =========================
# CACHE DES DONNÉES
# =========================
data_cache = {}

def get_data(name, ticker):
    if ticker is None:
        return None
    key = ticker
    if key not in data_cache:
        data_cache[key] = fetch_data(ticker)
    return data_cache[key]

# Précharge toutes les données
print("=== CHARGEMENT DES DONNEES ===")
all_tickers = set()
for bloc_name, pairs in BLOCS.items():
    for row in pairs:
        name_l, ticker_l, name_r, ticker_r = row
        if ticker_l: all_tickers.add((name_l, ticker_l))
        if ticker_r: all_tickers.add((name_r, ticker_r))
for line in DEVISES:
    for name, ticker in line:
        all_tickers.add((name, ticker))
for name, ticker in FUNDSMITH:
    all_tickers.add((name, ticker))

for name, ticker in all_tickers:
    get_data(name, ticker)

print(f"=== {len(data_cache)} tickers chargés ===")

# =========================
# RENDU HTML D'UN GRAPHIQUE
# =========================
chart_counter = [0]

def render_chart(name, ticker, small=False):
    data = get_data(name, ticker)
    chart_counter[0] += 1
    cid = f"c{chart_counter[0]}"
    height = 180 if small else 220

    if data is None:
        return f"""
        <div class="chart-block {'small' if small else ''}">
          <div class="chart-header">
            <h2>{name}</h2>
          </div>
          <p style="color:#999;font-size:0.85em">Données indisponibles</p>
        </div>"""

    sig_color = indicator_color(data['adm136'])
    if data['adm136'] > 0:
        sig_emoji = "✅"
    elif data['v1y'] > 0:
        sig_emoji = "⚠️"
    else:
        sig_emoji = "🚨"

    return f"""
<div class="chart-block {'small' if small else ''}">
  <div class="chart-header">
    <h2>{sig_emoji} {name} <span class="price">{fmt_price(data['last'])}</span></h2>
    <div class="period-btns">
      <button class="btn-period active" onclick="setPeriod('{cid}','1y',this)">1a</button>
      <button class="btn-period" onclick="setPeriod('{cid}','2y',this)">2a</button>
    </div>
  </div>
  <canvas id="{cid}" height="{height}"></canvas>
  <div class="indicators">
    <div class="ind">
      <span class="ind-label">ADM136-3%</span>
      <span class="ind-value" style="color:{indicator_color(data['adm136'])}">{fmt(data['adm136'])}</span>
    </div>
    <div class="ind">
      <span class="ind-label">1Y-3%</span>
      <span class="ind-value" style="color:{indicator_color(data['v1y'])}">{fmt(data['v1y'])}</span>
    </div>
    <div class="ind">
      <span class="ind-label">MM200</span>
      <span class="ind-value" style="color:{indicator_color(data['mm200'])}">{fmt(data['mm200'])}</span>
    </div>
  </div>
</div>
<script>
(function(){{
  var d = {{
    "1y":{{labels:{json.dumps(data['dates_1y'])},close:{json.dumps(data['close_1y'])},sma:{json.dumps(data['sma200_1y'])},sig:{json.dumps(data['signals_1y'])}}},
    "2y":{{labels:{json.dumps(data['dates_2y'])},close:{json.dumps(data['close_2y'])},sma:{json.dumps(data['sma200_2y'])},sig:{json.dumps(data['signals_2y'])}}}
  }};

  var SIG_COLORS = {{
    "green":  "rgba(40,167,69,0.12)",
    "orange": "rgba(255,193,7,0.18)",
    "red":    "rgba(220,53,69,0.12)",
  }};

  var bgPlugin = {{
    id: "bgZones_{cid}",
    beforeDraw: function(chart) {{
      var ctx = chart.ctx;
      var xAxis = chart.scales.x;
      var yAxis = chart.scales.y;
      var sigs = chart._sigData || [];
      if (!sigs.length) return;
      var top = yAxis.top;
      var bottom = yAxis.bottom;
      ctx.save();
      for (var i = 0; i < sigs.length; i++) {{
        var s = sigs[i];
        if (!s) continue;
        var x1 = xAxis.getPixelForIndex(i);
        var x2 = xAxis.getPixelForIndex(i+1) || x1 + 2;
        ctx.fillStyle = SIG_COLORS[s] || "transparent";
        ctx.fillRect(x1, top, x2 - x1, bottom - top);
      }}
      ctx.restore();
    }}
  }};

  var chart = new Chart(document.getElementById("{cid}"), {{
    type: "line",
    plugins: [bgPlugin],
    data: {{
      labels: d["1y"].labels,
      datasets: [
        {{
          label: "Cours",
          data: d["1y"].close,
          borderColor: "#2196F3",
          backgroundColor: "rgba(33,150,243,0.06)",
          borderWidth: 1.5,
          pointRadius: 0,
          tension: 0.1,
          fill: true,
        }},
        {{
          label: "MM200",
          data: d["1y"].sma,
          borderColor: "#FF9800",
          borderWidth: 1.5,
          pointRadius: 0,
          borderDash: [4,3],
          fill: false,
        }}
      ]
    }},
    options: {{
      responsive: true,
      interaction: {{mode:"index", intersect:false}},
      plugins: {{
        legend: {{position:"top", labels:{{boxWidth:12, font:{{size:11}}}}}},
        tooltip: {{callbacks: {{label: ctx => ctx.dataset.label+": "+(ctx.parsed.y?.toFixed(2)??"-")}}}}
      }},
      scales: {{
        x: {{ticks:{{maxTicksLimit:8, font:{{size:10}}}}, grid:{{display:false}}}},
        y: {{ticks:{{font:{{size:10}}, callback: v => v >= 1000 ? (v/1000).toFixed(0)+"k" : v.toFixed(0)}}}}
      }}
    }}
  }});
  chart._sigData = d["1y"].sig;

  window.charts = window.charts || {{}};
  window.charts["{cid}"] = {{chart: chart, data: d}};
}})();
</script>"""

# =========================
# CONSTRUCTION DE LA PAGE
# =========================
os.makedirs("output", exist_ok=True)

body = ""

# --- Devises ---
body += '<div class="section-title">Devises</div>'
body += '<div class="devises-bloc">'
for line in DEVISES:
    body += '<div class="devise-line">'
    for name, ticker in line:
        body += render_chart(name, ticker, small=True)
    body += '</div>'
body += '</div>'

# --- Blocs principaux ---
for bloc_name, pairs in BLOCS.items():
    body += f'<div class="section-title">{bloc_name}</div>'
    body += '<div class="pairs-grid">'
    for row in pairs:
        name_l, ticker_l, name_r, ticker_r = row
        body += '<div class="pair-row">'
        if ticker_l:
            body += render_chart(name_l, ticker_l)
        else:
            body += '<div class="chart-block empty"></div>'
        if ticker_r:
            body += render_chart(name_r, ticker_r)
        else:
            body += '<div class="chart-block empty"></div>'
        body += '</div>'
    body += '</div>'

# --- Fundsmith ---
body += '<div class="section-title">Fundsmith — Top 10 holdings</div>'
body += '<div class="grid2">'
for name, ticker in FUNDSMITH:
    body += render_chart(name, ticker, small=True)
body += '</div>'

# =========================
# HTML FINAL
# =========================
html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ETF Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: Arial, sans-serif; background: #f0f2f5; padding: 12px; }}
h1 {{ font-size: 1.3em; color: #222; margin-bottom: 2px; }}
.updated {{ color: #999; font-size: 0.8em; margin-bottom: 14px; }}

.section-title {{
  font-size: 1em; font-weight: bold; color: #fff;
  background: #222; padding: 6px 12px;
  border-radius: 6px 6px 0 0; margin-top: 16px; margin-bottom: 0;
}}

/* Devises */
.devises-bloc {{ background: #fff; border: 1px solid #ddd; border-top: none; border-radius: 0 0 6px 6px; padding: 10px; }}
.devise-line {{ display: flex; gap: 10px; margin-bottom: 8px; }}
.devise-line:last-child {{ margin-bottom: 0; }}
.devise-line .chart-block {{ flex: 1; }}

/* Paires indice/ETF */
.pairs-grid {{ background: #fff; border: 1px solid #ddd; border-top: none; border-radius: 0 0 6px 6px; padding: 10px; }}
.pair-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }}
.pair-row:last-child {{ margin-bottom: 0; }}

/* Grille 2 colonnes */
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
          background: #fff; border: 1px solid #ddd; border-top: none;
          border-radius: 0 0 6px 6px; padding: 10px; }}

/* Bloc graphique */
.chart-block {{
  background: #fafafa; border: 1px solid #e0e0e0;
  border-radius: 6px; padding: 10px;
}}
.chart-block.empty {{ background: transparent; border: none; }}
.chart-block.small canvas {{ max-height: 160px; }}

.chart-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
h2 {{ font-size: 0.9em; color: #333; display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap; }}
.price {{ font-size: 0.85em; color: #666; font-weight: normal; }}

.period-btns {{ display: flex; gap: 3px; flex-shrink: 0; }}
.btn-period {{
  padding: 2px 7px; font-size: 0.75em;
  border: 1px solid #ccc; border-radius: 3px;
  background: #fff; cursor: pointer; color: #555;
}}
.btn-period.active {{ background: #2196F3; color: #fff; border-color: #2196F3; }}

.indicators {{ display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }}
.ind {{
  display: flex; flex-direction: column; align-items: center;
  background: #f0f0f0; border-radius: 4px;
  padding: 4px 8px; flex: 1; min-width: 70px;
}}
.ind-label {{ font-size: 0.7em; color: #888; margin-bottom: 1px; }}
.ind-value {{ font-size: 0.9em; font-weight: bold; }}

@media (max-width: 650px) {{
  .pair-row {{ grid-template-columns: 1fr; }}
  .grid2 {{ grid-template-columns: 1fr; }}
  .devise-line {{ flex-direction: column; }}
}}
</style>
</head>
<body>
<h1>📈 ETF Dashboard</h1>
<p class="updated">Mis à jour le {now.strftime("%d/%m/%Y à %Hh%M")} (heure de Paris)</p>
{body}
<script>
function setPeriod(cid, period, btn) {{
  var entry = window.charts[cid];
  if (!entry) return;
  var chart = entry.chart;
  var d = entry.data[period];
  chart.data.labels = d.labels;
  chart.data.datasets[0].data = d.close;
  chart.data.datasets[1].data = d.sma;
  chart._sigData = d.sig;
  chart.update();
  btn.parentNode.querySelectorAll(".btn-period").forEach(function(b) {{
    b.classList.remove("active");
  }});
  btn.classList.add("active");
}}
</script>
</body>
</html>"""

with open("output/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard généré.")
