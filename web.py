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
    df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=False)
    if df is None or df.empty:
        print(f"  -> DataFrame vide pour {ticker}")
        return None
    print(f"  -> {len(df)} lignes téléchargées")
    close = df["Close"].squeeze().dropna()
    sma200 = close.rolling(200).mean()
    v1m = (close.iloc[-1] - close.iloc[-21]) / close.iloc[-21] * 100
    v3m = (close.iloc[-1] - close.iloc[-63]) / close.iloc[-63] * 100
    v6m = (close.iloc[-1] - close.iloc[-126]) / close.iloc[-126] * 100
    v1y_raw = (close.iloc[-1] - close.iloc[-252]) / close.iloc[-252] * 100 if len(close) >= 252 else v6m
    adm136 = (v1m + v3m + v6m) / 3 - 3
    v1y_minus3 = v1y_raw - 3
    sma200_last = float(sma200.iloc[-1])
    mm200 = (float(close.iloc[-1]) - sma200_last) / sma200_last * 100 if sma200_last else 0
    dates = [d.strftime("%Y-%m-%d") for d in close.index]
    return {
        "dates": dates,
        "close": [round(float(v), 2) for v in close],
        "sma200": [round(float(v), 2) if not pd.isna(v) else None for v in sma200],
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
for name, ticker in
