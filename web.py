import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

print("=== DEBUT WEB.PY ===")

try:
    import yfinance as yf
    print("yfinance importé OK")
except Exception as e:
    print(f"ERREUR import yfinance: {e}")

try:
    import pandas as pd
    print("pandas importé OK")
except Exception as e:
    print(f"ERREUR import pandas: {e}")

now = datetime.now(ZoneInfo("Europe/Paris"))
print(f"Heure: {now}")

TICKERS = {"MSFT": "MSFT", "Visa": "V"}

def fetch_data(ticker):
    print(f"  -> yf.download({ticker})...")
    df = yf.download(ticker, period="2y", interval="1d", progress=False, auto_adjust=False)
    if df is None or df.empty:
        print(f"  -> DataFrame vide pour {ticker}")
        return None
    print(f"  -> {len(df)} lignes téléchargées")

    close = df["Close"].squeeze().dropna()
    sma200 = close.rolling(200).mean()

    # Indicateurs sur 2 ans (pour avoir 252 points fiables)
    v1m = (close.iloc[-1] - close.iloc[-21]) / close.iloc[-21] * 100
    v3m = (close.iloc[-1] - close.iloc[-63]) / close.iloc[-63] * 100
    v6m = (close.iloc[-1] - close.iloc[-126]) / close.iloc[-126] * 100
    v1y_raw = (close.iloc[-1] - close.iloc[-252]) / close.iloc[-252] * 100 if len(close) >= 252 else v6m
    adm136 = (v1m + v3m + v6m) / 3 - 3
    v1y_minus3 = v1y_raw - 3
    sma200_last = float(sma200.iloc[-1])
    mm200 = (float(close.iloc[-1]) - sma200_last) / sma200_last * 100 if sma200_last else 0

    # Données complètes (2 ans) pour le graphique
    dates_2y = [d.strftime("%Y-%m-%d") for d in close.index]
    close_2y = [round(float(v), 2) for v in close]
    sma200_2y = [round(float(v), 2) if not pd.isna(v) else None for v in sma200]

    # Données filtrées (1 an) = derniers 252 points
    n = min(252, len(close))
    dates_1y = dates_2y[-n:]
    close_1y = close_2y[-n:]
    sma200_1y = sma200_2y[-n:]

    return {
        "dates_1y": dates_1y,
        "close_1y": close_1y,
        "sma200_1y": sma200_1y,
        "dates_2y": dates_2y,
        "close_2y": close_2y,
        "sma200_2y": sma200_2y,
        "adm136": round(float(adm136), 1),
        "v1y": round(float(v1y_minus3), 1),
        "mm200": round(float(mm200), 1),
        "last": round(float(close.iloc[-1]), 2),
    }

def indicator_color(value):
    return "#1a7f37" if value >= 0 else "#d1242f"

def fmt(value):
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%".replace(".", ",")

charts_data = {}
for name, ticker in TICKERS.items():
    print(f"Fetching {name} ({ticker})...")
    try:
        data = fetch_data(ticker)
        if data:
            print(f"{name}: {len(data['dates_2y'])} points OK")
            charts_data[name] = data
        else:
            print(f"{name}: AUCUNE DONNEE")
    except Exception as e:
        print(f"{name}: ERREUR - {e}")

print(f"charts_data contient: {list(charts_data.keys())}")

os.makedirs("output", exist_ok=True)

charts_html = ""
for name, data in charts_data.items():
    chart_id = f"chart_{name.replace(' ', '_').replace('/', '_')}"
    charts_html += f"""
<div class="chart-block">
  <div class="chart-header">
    <h2>{name} <span class="price">{data['last']:.2f}</span></h2>
    <div class="period-btns">
      <button class="btn-period active" onclick="setPeriod('{chart_id}', '1y', this)">1 an</button>
      <button class="btn-period" onclick="setPeriod('{chart_id}', '2y', this)">2 ans</button>
    </div>
  </div>
  <canvas id="{chart_id}"></canvas>
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
(function() {{
  var data = {{
    "1y": {{
      labels: {json.dumps(data['dates_1y'])},
      close: {json.dumps(data['close_1y'])},
      sma200: {json.dumps(data['sma200_1y'])}
    }},
    "2y": {{
      labels: {json.dumps(data['dates_2y'])},
      close: {json.dumps(data['close_2y'])},
      sma200: {json.dumps(data['sma200_2y'])}
    }}
  }};

  var chart_{chart_id} = new Chart(document.getElementById("{chart_id}"), {{
    type: "line",
    data: {{
      labels: data["1y"].labels,
      datasets: [
        {{
          label: "Cours",
          data: data["1y"].close,
          borderColor: "#2196F3",
          backgroundColor: "rgba(33,150,243,0.08)",
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.1,
          fill: true,
        }},
        {{
          label: "MM200",
          data: data["1y"].sma200,
          borderColor: "#FF9800",
          borderWidth: 1.5,
          pointRadius: 0,
          borderDash: [5, 3],
          fill: false,
        }}
      ]
    }},
    options: {{
      responsive: true,
      interaction: {{ mode: "index", intersect: false }},
      plugins: {{
        legend: {{ position: "top" }},
        tooltip: {{ callbacks: {{
          label: ctx => ctx.dataset.label + ": " + (ctx.parsed.y?.toFixed(2) ?? "-")
        }}}}
      }},
      scales: {{
        x: {{ ticks: {{ maxTicksLimit: 12 }} }},
        y: {{ ticks: {{ callback: v => v.toFixed(0) }} }}
      }}
    }}
  }});

  window.charts = window.charts || {{}};
  window.charts["{chart_id}"] = {{ chart: chart_{chart_id}, data: data }};
}})();
</script>
"""

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ETF Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 16px; margin: 0; }}
  h1 {{ color: #333; margin-bottom: 4px; font-size: 1.4em; }}
  .updated {{ color: #999; font-size: 0.85em; margin-bottom: 16px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  @media (max-width: 700px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  .chart-block {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 12px; }}
  .chart-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
  h2 {{ margin: 0; font-size: 1em; color: #333; display: flex; align-items: baseline; gap: 8px; }}
  .price {{ font-size: 0.9em; color: #666; font-weight: normal; }}
  .period-btns {{ display: flex; gap: 4px; }}
  .btn-period {{
    padding: 3px 10px; font-size: 0.8em; border: 1px solid #ddd;
    border-radius: 4px; background: #fff; cursor: pointer; color: #555;
  }}
  .btn-period.active {{ background: #2196F3; color: #fff; border-color: #2196F3; }}
  .indicators {{ display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }}
  .ind {{ display: flex; flex-direction: column; align-items: center; background: #f9f9f9; border: 1px solid #eee; border-radius: 6px; padding: 6px 12px; flex: 1; min-width: 80px; }}
  .ind-label {{ font-size: 0.75em; color: #999; margin-bottom: 2px; }}
  .ind-value {{ font-size: 1em; font-weight: bold; }}
</style>
</head>
<body>
<h1>📈 ETF Dashboard</h1>
<p class="updated">Mis à jour le {now.strftime("%d/%m/%Y à %Hh%M")} (heure de Paris)</p>
<div class="grid">
{charts_html}
</div>
<script>
function setPeriod(chartId, period, btn) {{
  var entry = window.charts[chartId];
  if (!entry) return;
  var chart = entry.chart;
  var d = entry.data[period];
  chart.data.labels = d.labels;
  chart.data.datasets[0].data = d.close;
  chart.data.datasets[1].data = d.sma200;
  chart.update();
  // Met à jour le style des boutons
  var btns = btn.parentNode.querySelectorAll(".btn-period");
  btns.forEach(function(b) {{ b.classList.remove("active"); }});
  btn.classList.add("active");
}}
</script>
</body>
</html>"""

with open("output/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard généré.")
