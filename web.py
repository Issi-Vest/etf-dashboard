import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

now = datetime.now(ZoneInfo("Europe/Paris"))
TICKERS = {"MSFT": "MSFT", "Visa": "V"}

def fetch_data(ticker):
    df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=False)
    if df is None or df.empty:
        return None
    close = df["Close"].squeeze().dropna()
    sma200 = close.rolling(200).mean()
    dates = [d.strftime("%Y-%m-%d") for d in close.index]
    return {
        "dates": dates,
        "close": [round(float(v), 2) for v in close],
        "sma200": [round(float(v), 2) if not pd.isna(v) else None for v in sma200],
    }

charts_data = {}
for name, ticker in TICKERS.items():
    data = fetch_data(ticker)
    if data:
        charts_data[name] = data

os.makedirs("output", exist_ok=True)

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ETF Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
  h1 {{ color: #333; }}
  .updated {{ color: #999; font-size: 0.85em; margin-bottom: 20px; }}
  .chart-block {{ background: #fff; border: 1px solid #ddd; border-radius: 8px;
                  padding: 16px; margin-bottom: 24px; }}
  h2 {{ margin-top: 0; color: #333; }}
</style>
</head>
<body>
<h1>📈 ETF Dashboard</h1>
<p class="updated">Mis à jour le {now.strftime("%d/%m/%Y à %Hh%M")} (heure de Paris)</p>
"""

for name, data in charts_data.items():
    chart_id = f"chart_{name.replace(' ', '_')}"
    html += f"""
<div class="chart-block">
  <h2>{name}</h2>
  <canvas id="{chart_id}"></canvas>
</div>
<script>
new Chart(document.getElementById("{chart_id}"), {{
  type: "line",
  data: {{
    labels: {json.dumps(data["dates"])},
    datasets: [
      {{
        label: "Cours",
        data: {json.dumps(data["close"])},
        borderColor: "#2196F3",
        backgroundColor: "rgba(33,150,243,0.08)",
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1,
        fill: true,
      }},
      {{
        label: "MM200",
        data: {json.dumps(data["sma200"])},
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
</script>
"""

html += """
</body>
</html>"""

with open("output/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard généré.")
