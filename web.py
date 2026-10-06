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
    open_ = df["Open"].squeeze().dropna()
    high = df["High"].squeeze().dropna()
    low = df["Low"].squeeze().dropna()

    sma200 = close.rolling(200).mean()

    # Indicateurs
    v1m = (close.iloc[-1] - close.iloc[-21]) / close.iloc[-21] * 100
    v3m = (close.iloc[-1] - close.iloc[-63]) / close.iloc[-63] * 100
    v6m = (close.iloc[-1] - close.iloc[-126]) / close.iloc[-126] * 100
    v1y_raw = (close.iloc[-1] - close.iloc[-252]) / close.iloc[-252] * 100 if len(close) >= 252 else v6m
    adm136 = (v1m + v3m + v6m) / 3 - 3
    v1y_minus3 = v1y_raw - 3
    sma200_last = float(sma200.iloc[-1])
    mm200 = (float(close.iloc[-1]) - sma200_last) / sma200_last * 100 if sma200_last else 0

    # Données bougies pour Lightweight Charts
    candles = []
    sma_line = []
    for i in range(len(close)):
        d = close.index[i].strftime("%Y-%m-%d")
        candles.append({
            "time": d,
            "open": round(float(open_.iloc[i]), 4),
            "high": round(float(high.iloc[i]), 4),
            "low": round(float(low.iloc[i]), 4),
            "close": round(float(close.iloc[i]), 4),
        })
        if not pd.isna(sma200.iloc[i]):
            sma_line.append({
                "time": d,
                "value": round(float(sma200.iloc[i]), 4),
            })

    return {
        "candles": candles,
        "sma200": sma_line,
        "adm136": round(float(adm136), 1),
        "v1y": round(float(v1y_minus3), 1),
        "mm200": round(float(mm200), 1),
        "last": round(float(close.iloc[-1]), 2),
    }

charts_data = {}
for name, ticker in TICKERS.items():
    data = fetch_data(ticker)
    if data:
        charts_data[name] = data

os.makedirs("output", exist_ok=True)

def indicator_color(value):
    if value >= 0:
        return "#1a7f37"
    return "#d1242f"

def fmt(value):
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%".replace(".", ",")

charts_html = ""
for name, data in charts_data.items():
    chart_id = f"chart_{name.replace(' ', '_').replace('/', '_')}"
    charts_html += f"""
<div class="chart-block">
  <h2>{name} <span class="price">{fmt(data['last']).replace('%','')}</span></h2>
  <div id="{chart_id}" class="chart-container"></div>
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
  var chart = LightweightCharts.createChart(document.getElementById("{chart_id}"), {{
    width: 0,
    height: 280,
    layout: {{ background: {{ color: "#ffffff" }}, textColor: "#333" }},
    grid: {{ vertLines: {{ color: "#f0f0f0" }}, horzLines: {{ color: "#f0f0f0" }} }},
    rightPriceScale: {{ borderColor: "#ddd" }},
    timeScale: {{ borderColor: "#ddd", timeVisible: true }},
  }});

  // Redimensionnement responsive
  function resizeChart() {{
    var container = document.getElementById("{chart_id}");
    chart.resize(container.offsetWidth, 280);
  }}
  resizeChart();
  window.addEventListener("resize", resizeChart);

  var candleSeries = chart.addCandlestickSeries({{
    upColor: "#1a7f37",
    downColor: "#d1242f",
    borderUpColor: "#1a7f37",
    borderDownColor: "#d1242f",
    wickUpColor: "#1a7f37",
    wickDownColor: "#d1242f",
  }});
  candleSeries.setData({json.dumps(data['candles'])});

  var smaSeries = chart.addLineSeries({{
    color: "#FF9800",
    lineWidth: 1.5,
    lineStyle: 1,
    priceLineVisible: false,
    lastValueVisible: false,
    title: "MM200",
  }});
  smaSeries.setData({json.dumps(data['sma200'])});

  chart.timeScale().fitContent();
}})();
</script>
"""

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ETF Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lightweight-charts/4.1.3/lightweight-charts.standalone.production.js"></script>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: Arial, sans-serif;
    background: #f5f5f5;
    padding: 16px;
    margin: 0;
  }}
  h1 {{ color: #333; margin-bottom: 4px; font-size: 1.4em; }}
  .updated {{ color: #999; font-size: 0.85em; margin-bottom: 16px; }}

  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }}
  @media (max-width: 700px) {{
    .grid {{ grid-template-columns: 1fr; }}
  }}

  .chart-block {{
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px;
  }}
  h2 {{
    margin: 0 0 8px 0;
    font-size: 1em;
    color: #333;
    display: flex;
    align-items: baseline;
    gap: 8px;
  }}
  .price {{
    font-size: 0.9em;
    color: #666;
    font-weight: normal;
  }}
  .chart-container {{
    width: 100%;
    height: 280px;
  }}
  .indicators {{
    display: flex;
    gap: 16px;
    margin-top: 10px;
    flex-wrap: wrap;
  }}
  .ind {{
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #f9f9f9;
    border: 1px solid #eee;
    border-radius: 6px;
    padding: 6px 12px;
    flex: 1;
    min-width: 80px;
  }}
  .ind-label {{
    font-size: 0.75em;
    color: #999;
    margin-bottom: 2px;
  }}
  .ind-value {{
    font-size: 1em;
    font-weight: bold;
  }}
</style>
</head>
<body>
<h1>📈 ETF Dashboard</h1>
<p class="updated">Mis à jour le {now.strftime("%d/%m/%Y à %Hh%M")} (heure de Paris)</p>
<div class="grid">
{charts_html}
</div>
</body>
</html>"""

with open("output/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard généré.")
