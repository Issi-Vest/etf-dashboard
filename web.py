import json
import os
import re
import html as html_module
import urllib.request
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

try:
    from notes import NOTES
except Exception as e:
    print(f"notes.py non chargé: {e}")
    NOTES = {}

now = datetime.now(ZoneInfo("Europe/Paris"))
print(f"Heure: {now}")

dispatch_token = os.environ.get("DISPATCH_TOKEN", "")

# =========================
# STRUCTURE DES BLOCS
# =========================

TAUX_ETF = {"PR1T.L", "PR1T.DE", "YCSH.AS"}

BLOCS = {
        "ETF sur taux": [
        ("PR1T (LSE)", "PR1T.L",  "PR1T (XETRA)", "PR1T.DE"),
        ("YCSH",       "YCSH.AS", None,            None),
    ],
    
    "Indices actions": [
        ("MSCI WORLD",         "^990100-USD-STRD",     "DCAM",          "DCAM.PA"),
        ("SP500",         "^GSPC",     "PSP5",          "PSP5.PA"),
        ("NDQ",           "^NDX",      "PUST",          "PUST.PA"),
        ("DJI",           "^DJI",      "PDJE",          "PDJE.PA"),
        ("RUSSELL 2000",  "^RUT",      "RS2K",          "RS2K.PA"),  
        ("EURO STOXX 50", "^STOXX50E", "MFED",          "MFED.PA"),    
        ("DAX",           "^GDAXI",    "CG1 (DAX)",     "CG1.PA"),
        ("CAC 40 (dividendes non réinvestis)",   "^FCHI",  "CACC (CAC GR)", "CACC.PA"),
        ("GRE",           "GRE.PA",    "INR",     "INR.PA"),
        ("Emergents (EUNM)", "EUNM.DE",   None,            None),
        
    ],
    "Matières premières": [
        ("XAUUSD", "GC=F",   "4GLD (XETRA)", "4GLD.DE"),
        ("XAGUSD", "SI=F", "PHAG",            "PHAG.AS"),
        ("RING",   "RING", "GLDM",            "GLDM"),
        ("DBC",    "DBC",    "ICOM",          "ICOM.L"),
        ("COMO", "COMO.PA",   None,            None),
        ("DBA", "DBA", "AGAP", "AGAP.L"),
        ("UKOIL",  "BZ=F",   "Oil&Gas",           "IOGP.AS"),
        ("NRJ",   "NRJ.PA",   None,            None),
        ("HG1!",   "HG=F",   "COPAP",         "COPAP.PA"),
        ("ALUM",   "ALUM.L", "PHAG",            "PHAG.AS"),
    ],
    
    "Crypto": [
        ("BTCUSDT", "BTC-USD", "ETHUSDT", "ETH-USD"),
        ("XRPUSDT", "XRP-USD", "SOLUSDT", "SOL-USD"),
        ("BLOK", "BLOK", "Blokchain technology (CBUT)", "CBUT.DE"),
    ],
    "Autres actions": [
        ("NVDA",  "NVDA",    "MSFT",  "MSFT"),
        ("TSLA",  "TSLA",    "MC",    "MC.PA"),
        ("HO",    "HO.PA",   "ALFPC", "ALFPC.PA"),
        ("BUCN",  "BUCN.SW", "PM",    "PM"),
        ("IDEXX", "IDXX", "ADP", "ADP"),
        ("MC", "MC.PA", "TTE", "TTE.PA"),
        ("REALTY INCOME", "O", "WPC", "WPC"),
        ("VICI", "VICI", "NHI", "NHI"),
    ],
}

DEVISES = [
    [("USDEUR", "USDEUR=X"), ("EURUSD", "EURUSD=X")],
    [("DXY",    "DX-Y.NYB")],
    [("CHFEUR", "CHFEUR=X"), ("EURCHF", "EURCHF=X")],
]

FUNDSMITH_TICKERS = {
    "Marriott": "MAR",
    "Waters": "WAT",
    "L'Oréal": "OR.PA",
    "Visa": "V",
    "Amadeus": "AMS.MC",
    "Stryker": "SYK",
    "Alphabet": "GOOGL",
    "Meta Platforms": "META",
    "Microsoft": "MSFT",
    "Automatic Data Processing": "ADP",
    "Philip Morris": "PM",
    "Novo Nordisk": "NOVO-B.CO",
    "Mettler-Toledo": "MTD",
    "Church & Dwight": "CHD",
    "Domino's Pizza": "DPZ",
    "Fortinet": "FTNT",
    "Texas Instruments": "TXN",
    "Zoetis": "ZTS",
    "LVMH": "MC.PA",
    "Nike": "NKE",
    "Mastercard": "MA",
    "Veeva Systems": "VEEV",
    "Uber": "UBER",
    "Sage": "SGE.L",
    "Yum! Brands": "YUM"
}

# =========================
# FETCH FUNDSMITH
# =========================
def fetch_fundsmith_holdings():
    try:
        req = urllib.request.Request(
            "https://www.fundsmith.co.uk/factsheet/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
                "Accept-Encoding": "identity",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html_content = resp.read().decode("utf-8")
      
        month = ""
        month_match = re.search(r"Portfolio Comment for ([A-Za-z]+) (\d{4})", html_content)
        if month_match:
            mois_fr = {
                "January": "Janvier", "February": "Février", "March": "Mars",
                "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet",
                "August": "Août", "September": "Septembre", "October": "Octobre",
                "November": "Novembre", "December": "Décembre",
            }
            month = f"{mois_fr.get(month_match.group(1), month_match.group(1))} {month_match.group(2)}"

        comment = ""
        if month_match:
            start = month_match.end()
            end_idx = html_content.find("Top 10 holdings", start)
            raw = html_content[start:end_idx] if end_idx != -1 else html_content[start:start + 3000]
            paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", raw, re.DOTALL)
            comment = " ".join(
                html_module.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in paragraphs
            )
            comment = re.sub(r"\s+", " ", comment).strip()
        print(f"Fundsmith commentaire: {len(comment)} caractères")
        
        section = html_content.split("Top 10 holdings")
        holdings = []
        if len(section) > 1:
            after = section[1]
            ul_match = re.search(r"<ul[^>]*>(.*?)</ul>", after, re.DOTALL)
            if ul_match:
                items = re.findall(r"<li[^>]*>(.*?)</li>", ul_match.group(1), re.DOTALL)
                for it in items:
                    clean = html_module.unescape(re.sub(r"<[^>]+>", "", it)).strip()
                    if clean:
                        holdings.append(clean)

        print(f"Fundsmith holdings: {holdings[:10]}")
        return holdings[:10], month
    except Exception as e:
        print(f"Fundsmith fetch error: {e}")
        return [], ""

# Fetch dynamique des holdings Fundsmith
fundsmith_names, fundsmith_month = fetch_fundsmith_holdings()
FUNDSMITH = []
for name in fundsmith_names:
    ticker = FUNDSMITH_TICKERS.get(name)
    if ticker:
        FUNDSMITH.append((name, ticker))
    else:
        print(f"Fundsmith ticker inconnu: {name}")
        FUNDSMITH.append((name, None))

if not FUNDSMITH:
    FUNDSMITH = [
        ("Marriott", "MAR"), ("Waters", "WAT"),
        ("L'Oréal", "OR.PA"), ("Visa", "V"),
        ("Amadeus", "AMS.MC"), ("Stryker", "SYK"),
        ("Alphabet", "GOOGL"), ("Meta Platforms", "META"),
        ("Microsoft", "MSFT"), ("ADP", "ADP"),
    ]

# =========================
# FETCH YAHOO
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
            print(f"  -> {ticker} : Close n'est pas une Series ({type(close)})")
            return None
        close = close.dropna()

        # Complète la dernière séance si le journalier est en retard (cours à la minute)
        last_label = close.index[-1].strftime("%d/%m")
        try:
            intr = yf.Ticker(ticker).history(period="5d", interval="1m", auto_adjust=False)
            intr_close = intr["Close"].dropna() if intr is not None and len(intr) > 0 else None
            if intr_close is not None and len(intr_close) > 0:
                ts = intr_close.index[-1]
                if ts.tzinfo is None:
                    ts = ts.tz_localize("UTC")
                last_label = ts.tz_convert("Europe/Paris").strftime("%d/%m %Hh%M")
                trade_date = ts.date()
                if len(close) > 0 and trade_date > close.index[-1].date():
                    new_idx = pd.Timestamp(trade_date)
                    if close.index.tz is not None:
                        new_idx = new_idx.tz_localize(close.index.tz)
                    close = pd.concat([close, pd.Series([float(intr_close.iloc[-1])], index=[new_idx])])
                    print(f"  -> {ticker} : séance du {trade_date} ajoutée depuis les cours à la minute")
        except Exception as e:
            print(f"  -> {ticker} : heure de cotation indisponible ({e})")
            
        if len(close) < 63:
            return None

        sma200 = close.rolling(200).mean()

        v1m = (close.iloc[-1] - close.iloc[-21]) / close.iloc[-21] * 100 if len(close) >= 21 else 0
        v3m = (close.iloc[-1] - close.iloc[-63]) / close.iloc[-63] * 100 if len(close) >= 63 else 0
        v6m = (close.iloc[-1] - close.iloc[-126]) / close.iloc[-126] * 100 if len(close) >= 126 else 0
        v1y_raw = (close.iloc[-1] - close.iloc[-252]) / close.iloc[-252] * 100 if len(close) >= 252 else v6m
        adm136 = (v1m + v3m + v6m) / 3 - 3
        v1y_minus3 = v1y_raw - 3
        sma200_last = float(sma200.iloc[-1]) if not pd.isna(sma200.iloc[-1]) else 0
        mm200 = (float(close.iloc[-1]) - sma200_last) / sma200_last * 100 if sma200_last else 0

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

        # Variation sur 2 mois calendaires, x6 = taux annualisé
        perf_2m_x6 = None
        cible = close.index[-1] - pd.DateOffset(months=2)
        passe = close[close.index <= cible]
        if len(passe) > 0 and float(passe.iloc[-1]) != 0:
            perf_2m_x6 = (float(close.iloc[-1]) / float(passe.iloc[-1]) - 1) * 100 * 6

        return {
            "dates_3m":   dates_all[-63:],
            "close_3m":   close_all[-63:],
            "sma200_3m":  sma200_all[-63:],
            "signals_3m": signals_daily[-63:],
            "dates_6m":   dates_all[-126:],
            "close_6m":   close_all[-126:],
            "sma200_6m":  sma200_all[-126:],
            "signals_6m": signals_daily[-126:],            
            "dates_1y":   dates_all[-n1y:],
            "close_1y":   close_all[-n1y:],
            "sma200_1y":  sma200_all[-n1y:],
            "signals_1y": signals_daily[-n1y:],
            "dates_2y":   dates_all,
            "close_2y":   close_all,
            "sma200_2y":  sma200_all,
            "signals_2y": signals_daily,
            "adm136": round(float(adm136), 1),
            "v1y":    round(float(v1y_minus3), 1),
            "mm200":  round(float(mm200), 1),
            "last":   round(float(close.iloc[-1]), 4),
            "daily_change": round((float(close.iloc[-1]) - float(close.iloc[-2])) / float(close.iloc[-2]) * 100, 2) if len(close) >= 2 else 0,
            "last_date": last_label,
            "ath_2y": round(float(close.max()), 4),
            "ath_pct": round((float(close.iloc[-1]) - float(close.max())) / float(close.max()) * 100, 1),
            "perf_2m_x6": round(perf_2m_x6, 1) if perf_2m_x6 is not None else None,
        }
    except Exception as e:
        print(f"  -> ERREUR: {e}")
        return None

def indicator_color(v):
    return "#1a7f37" if v >= 0 else "#d1242f"

def fmt(v):
    return f"{'+'if v>=0 else ''}{v:.1f}%".replace(".", ",")

def fmt_price(v):
    if v is None: return "-"
    if v >= 100:  return f"{v:.2f}"
    if v >= 1:    return f"{v:.4f}"
    return f"{v:.6f}"

# =========================
# CACHE
# =========================
data_cache = {}

def get_data(name, ticker):
    if not ticker:
        return None
    if ticker not in data_cache:
        data_cache[ticker] = fetch_data(ticker)
    return data_cache[ticker]

print("=== CHARGEMENT DES DONNEES ===")
seen = set()
for pairs in BLOCS.values():
    for row in pairs:
        for t in [row[1], row[3]]:
            if t and t not in seen:
                seen.add(t)
                get_data("", t)
for line in DEVISES:
    for _, t in line:
        if t not in seen:
            seen.add(t)
            get_data("", t)
for _, t in FUNDSMITH:
    if t and t not in seen:
        seen.add(t)
        get_data("", t)
print(f"=== {len(data_cache)} tickers chargés ===")

# =========================
# RENDU GRAPHIQUE
# =========================
chart_counter = [0]

def render_chart(name, ticker, small=False):
    data = get_data(name, ticker)
    if not isinstance(data, dict):
        data = None
    chart_counter[0] += 1
    cid = f"c{chart_counter[0]}"
    height = 160 if small else 200

    if data is None:
        css_class = "chart-block small" if small else "chart-block"
        return f'<div class="{css_class}"><div class="chart-header"><h2>{name}</h2></div><p class="no-data">Données indisponibles</p></div>'

    if data['adm136'] > 0:
        sig = "✅"
    elif data['v1y'] > 0:
        sig = "⚠️"
    else:
        sig = "🚨"
    ath_badge = " 🏆" if data['ath_pct'] >= -2 else ""     

    extra_ind = ""
    if ticker in TAUX_ETF and data.get("perf_2m_x6") is not None:
        extra_ind = (
            '<div class="ind"><span class="ind-label">2M x6 (annualisé)</span>'
            f'<span class="ind-value" style="color:{indicator_color(data["perf_2m_x6"])}">{fmt(data["perf_2m_x6"])}</span></div>'
        )
    
    sigs_1y = json.dumps(data['signals_1y'])
    sigs_2y = json.dumps(data['signals_2y'])
    css_class = "chart-block small" if small else "chart-block"
    css_class = "chart-block small" if small else "chart-block"
    if data['mm200'] < 0:
        css_class += " below-mm"
    note = NOTES.get(name, "")
    note_html = f'<div class="note">{html_module.escape(note)}</div>' if note else ""
    
    return f"""<div class="{css_class}">
  <div class="chart-header">
    <h2>{sig} {name}{ath_badge} <span class="price">{fmt_price(data['last'])}</span>
    <span class="daily" style="color:{indicator_color(data['daily_change'])};font-size:0.8em">
      {fmt(data['daily_change'])} — {data['last_date']}
    </span></h2>
    <div class="period-btns">
    <button class="btn-period" onclick="setPeriod('{cid}','3m',this)">3m</button>
    <button class="btn-period active" onclick="setPeriod('{cid}','6m',this)">6m</button>
    <button class="btn-period" onclick="setPeriod('{cid}','1y',this)">1a</button>
    <button class="btn-period" onclick="setPeriod('{cid}','2y',this)">2a</button>
    </div>
  </div>
  <div class="chart-wrap" style="height:{height}px">
    <canvas id="{cid}"></canvas>
  </div>
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
    <div class="ind">
      <span class="ind-label">ATH 2Y</span>
      <span class="ind-value" style="color:{indicator_color(data['ath_pct'])}">{fmt(data['ath_pct'])}</span>
    </div>
    {extra_ind}
  </div>
  {note_html}
</div>
<script>
(function(){{
  var d = {{
    "3m":{{labels:{json.dumps(data['dates_3m'])},close:{json.dumps(data['close_3m'])},sma:{json.dumps(data['sma200_3m'])},sig:{json.dumps(data['signals_3m'])}}},
    "6m":{{labels:{json.dumps(data['dates_6m'])},close:{json.dumps(data['close_6m'])},sma:{json.dumps(data['sma200_6m'])},sig:{json.dumps(data['signals_6m'])}}},
    "1y":{{labels:{json.dumps(data['dates_1y'])},close:{json.dumps(data['close_1y'])},sma:{json.dumps(data['sma200_1y'])},sig:{sigs_1y}}},
    "2y":{{labels:{json.dumps(data['dates_2y'])},close:{json.dumps(data['close_2y'])},sma:{json.dumps(data['sma200_2y'])},sig:{sigs_2y}}}
  }};
  var SIG_ALPHA={{"green":"rgba(40,167,69,0.15)","orange":"rgba(255,193,7,0.2)","red":"rgba(220,53,69,0.15)"}};
  var bgPlugin={{
    id:"bg_{cid}",
    beforeDatasetsDraw:function(chart){{
      var ctx=chart.ctx,xScale=chart.scales.x,yScale=chart.scales.y,sigs=chart._sigs||[];
      if(!sigs.length||!xScale||!yScale)return;
      var top=yScale.top,bottom=yScale.bottom;
      ctx.save();
      for(var i=0;i<sigs.length;i++){{
        if(!sigs[i])continue;
        var color=SIG_ALPHA[sigs[i]];if(!color)continue;
        var meta=chart.getDatasetMeta(0);
        if(!meta||!meta.data||!meta.data[i])continue;
        var x1=meta.data[i].x;
        var x2=meta.data[i+1]?meta.data[i+1].x:x1+2;
        ctx.fillStyle=color;ctx.fillRect(x1,top,x2-x1+1,bottom-top);
      }}
      ctx.restore();
    }}
  }};
  var chart=new Chart(document.getElementById("{cid}"),{{
    type:"line",plugins:[bgPlugin],
    data:{{
      labels:d["6m"].labels,
      datasets:[
        {{label:"Cours",data:d["6m"].close,borderColor:"#1565C0",backgroundColor:"transparent",borderWidth:1.5,pointRadius:0,tension:0.1,order:1}},
        {{label:"MM200",data:d["6m"].sma,borderColor:"#E65100",borderWidth:1.5,pointRadius:0,borderDash:[4,3],fill:false,order:2}}
      ]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      interaction:{{mode:"index",intersect:false}},
      plugins:{{
        legend:{{position:"top",labels:{{boxWidth:10,font:{{size:10}}}}}},
        tooltip:{{callbacks:{{label:function(ctx){{return ctx.dataset.label+": "+(ctx.parsed.y!=null?ctx.parsed.y.toFixed(2):"-");}}}}}}
      }},
      scales:{{
        x:{{ticks:{{maxTicksLimit:8,font:{{size:10}}}},grid:{{display:false}}}},
        y:{{ticks:{{font:{{size:10}},callback:function(v){{if(v>=1000)return(v/1000).toFixed(0)+"k";return v.toFixed(0);}}}}}}
      }}
    }}
  }});
  chart._sigs=d["6m"].sig;
  window.charts=window.charts||{{}};
  window.charts["{cid}"]={{chart:chart,data:d}};
}})();
</script>"""

# =========================
# TAUX D'INTERET (valeur du jour, TradingView)
# =========================
TAUX = [
    ("FR 1 an",  "FR01Y", "FR 10 ans", "FR10Y"),
    ("DE 1 an",  "DE01Y", "DE 10 ans", "DE10Y"),
    ("US 1 an",  "US01Y", "US 10 ans", "US10Y"),
    ("CH 1 an",  "CH01Y", "CH 10 ans", "CH10Y"),
]

def fetch_taux_tv(code):
    url = f"https://fr.tradingview.com/symbols/TVC-{code}/"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
                "Accept-Encoding": "identity",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            page = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r"Le rendement actuel est de\s*([\d.,]+)\s*%", page)
        if m:
            val = float(m.group(1).replace(",", "."))
            print(f"Taux {code}: {val}")
            return val
        print(f"Taux {code}: valeur non trouvée dans la page")
    except Exception as e:
        print(f"Taux {code}: ERREUR - {e}")
    return None

def taux_card(label, code):
    val = fetch_taux_tv(code)
    txt = (f"{val:.3f}".replace(".", ",") + " %") if val is not None else "indisponible"
    link = f"https://fr.tradingview.com/chart/?symbol=TVC%3A{code}"
    return (
        '<div class="chart-block">'
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px">'
        f'<b>{label}</b>'
        f'<span style="font-size:1.3em;font-weight:bold">{txt}</span>'
        f'<a href="{link}" target="_blank" style="font-size:0.8em;color:#1565C0">Graphique ↗</a>'
        '</div></div>'
    )

# =========================
# PORTEFEUILLE FUNDSMITH EQUIPONDERE
# =========================
def perf_30j(data):
    if not isinstance(data, dict) or "dates_2y" not in data:
        print(f"  PF: données inattendues, type {type(data).__name__}, contenu : {repr(data)[:120]}")
        return None
    dates = pd.to_datetime(data["dates_2y"])
    closes = data["close_2y"]
    cible = dates[-1] - pd.Timedelta(days=30)
    idx = [i for i, d in enumerate(dates) if d <= cible]
    if not idx:
        return None
    base = closes[idx[-1]]
    if not base:
        return None
    return (closes[-1] / base - 1) * 100

def portefeuille_fundsmith():
    perfs = []
    for name, ticker in FUNDSMITH:
        d = get_data(name, ticker) if ticker else None
        p = perf_30j(d) if d else None
        if p is not None:
            perfs.append(p)
    if not perfs:
        return None, 0
    return sum(perfs) / len(perfs), len(perfs)

try:
    perf_pf, n_pf = portefeuille_fundsmith()
except Exception as e:
    print(f"Portefeuille Fundsmith: ERREUR - {e}")
    perf_pf, n_pf = None, 0
print(f"Portefeuille Fundsmith 30j: {perf_pf} ({n_pf} titres)")

# =========================
# CONSTRUCTION PAGE
# =========================

try:
    from notes import ALERTES
except Exception as e:
    print(f"ALERTES non chargées: {e}")
    ALERTES = []
    
try:
    from notes import MEMO
except Exception as e:
    print(f"MEMO non chargé: {e}")
    MEMO = ""

os.makedirs("output", exist_ok=True)
body = ""

body += '<div class="section-title">🔔 Alertes</div><div class="section-body">'
if ALERTES:
    body += '<ul style="margin-left:18px;font-size:0.85em">'
    for a in ALERTES:
        body += f'<li>{html_module.escape(a)}</li>'
    body += '</ul>'
else:
    body += '<p class="no-data" style="padding:8px 0">Aucune alerte pour le moment.</p>'
body += '</div>'

body += '<div class="section-title">📝 Mémo</div><div class="section-body">'
if MEMO.strip():
    body += f'<div class="memo">{html_module.escape(MEMO.strip())}</div>'
else:
    body += '<p class="no-data" style="padding:8px 0">Mémo vide.</p>'
body += '</div>'

body += '<div class="section-title">Devises</div><div class="section-body">'
for line in DEVISES:
    body += '<div class="devise-line">'
    for name, ticker in line:
        body += render_chart(name, ticker, small=True)
    body += '</div>'
body += '</div>'

body += '<div class="section-title">Taux d\'intérêt (1 an | 10 ans)</div><div class="section-body pairs-grid">'
for l1, c1, l2, c2 in TAUX:
    body += '<div class="pair-row">' + taux_card(l1, c1) + taux_card(l2, c2) + '</div>'
body += '</div>'

for bloc_name, pairs in BLOCS.items():
    body += f'<div class="section-title">{bloc_name}</div><div class="section-body pairs-grid">'
    for row in pairs:
        name_l, ticker_l, name_r, ticker_r = row
        body += '<div class="pair-row">'
        body += render_chart(name_l, ticker_l) if ticker_l else '<div class="chart-block empty"></div>'
        body += render_chart(name_r, ticker_r) if ticker_r else '<div class="chart-block empty"></div>'
        body += '</div>'
    body += '</div>'

titre_fs = "Fundsmith - Top 10 holdings" + (f" - {fundsmith_month}" if fundsmith_month else "")
body += f'<div class="section-title">{titre_fs}</div><div class="section-body grid2">'
if perf_pf is not None:
    body += (
        '<div class="chart-block" style="grid-column:1/-1">'
        '<b>Portefeuille équipondéré (10 % par titre), 30 derniers jours : </b>'
        f'<span style="font-size:1.2em;font-weight:bold;color:{indicator_color(perf_pf)}">{fmt(perf_pf)}</span>'
        f' <span style="color:#888;font-size:0.8em">({n_pf}/10 titres)</span>'
        '<div style="color:#888;font-size:0.75em;margin-top:4px">'
        'Note : variation sur 30 jours calendaires (et non 30 séances de bourse). '
        'Cours en devise locale : l\'effet de change n\'est pas pris en compte '
        '(par exemple L\'Oréal est en euros, Visa en dollars).'
        '</div>'
        '</div>'
    )
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
body {{ font-family: Arial, sans-serif; background: #ebebeb; padding: 12px; color: #222; }}
h1 {{ font-size: 1.2em; margin-bottom: 2px; }}
.updated {{ color: #888; font-size: 0.78em; margin-bottom: 12px; display: block; }}
.section-title {{ font-size: 0.9em; font-weight: bold; color: #fff; background: #1a1a2e; padding: 5px 10px; border-radius: 5px 5px 0 0; margin-top: 14px; }}
.section-body {{ background: #fff; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px; padding: 8px; }}
.devise-line {{ display: flex; gap: 8px; margin-bottom: 8px; }}
.devise-line:last-child {{ margin-bottom: 0; }}
.devise-line .chart-block {{ flex: 1; min-width: 0; }}
.pair-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }}
.pair-row:last-child {{ margin-bottom: 0; }}
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
.chart-block {{ background: #fafafa; border: 1px solid #e0e0e0; border-radius: 5px; padding: 8px; min-width: 0; }}
.chart-block.empty {{ background: transparent; border: 1px dashed #ddd; }}
.chart-block.below-mm {{ background: #fdecec; border: 3px solid #e60000; }}
.chart-wrap {{ position: relative; width: 100%; height: 200px; background: #fafafa; border-radius: 4px; }}
.chart-block.small .chart-wrap {{ height: 160px; }}
.chart-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; gap: 4px; }}
h2 {{ font-size: 0.85em; color: #333; display: flex; align-items: baseline; gap: 5px; flex-wrap: wrap; flex: 1; min-width: 0; }}
.price {{ font-size: 0.8em; color: #666; font-weight: normal; }}
.period-btns {{ display: flex; gap: 2px; flex-shrink: 0; }}
.btn-period {{ padding: 1px 6px; font-size: 0.7em; border: 1px solid #bbb; border-radius: 3px; background: #fff; cursor: pointer; color: #555; white-space: nowrap; }}
.btn-period.active {{ background: #1565C0; color: #fff; border-color: #1565C0; }}
.btn-period:hover {{ background: #e3f2fd; }}
.indicators {{ display: flex; gap: 5px; margin-top: 6px; flex-wrap: wrap; }}
.ind {{ display: flex; flex-direction: column; align-items: center; background: #f0f0f0; border-radius: 3px; padding: 3px 6px; flex: 1; min-width: 60px; }}
.ind-label {{ font-size: 0.65em; color: #888; margin-bottom: 1px; white-space: nowrap; }}
.ind-value {{ font-size: 0.85em; font-weight: bold; }}
.no-data {{ color: #bbb; font-size: 0.8em; padding: 20px 0; text-align: center; }}
.note {{ margin-top: 6px; padding: 5px 8px; background: #fff8e1; border-left: 3px solid #f9a825; font-size: 0.75em; color: #555; white-space: pre-line; }}
.memo {{ white-space: pre-line; font-size: 0.9em; font-family: "Segoe Print", "Bradley Hand", cursive; background: #fffde7; padding: 8px 10px; border-radius: 4px; line-height: 1.5; }}
@media (max-width: 600px) {{
  .pair-row {{ grid-template-columns: 1fr; }}
  .grid2 {{ grid-template-columns: 1fr; }}
  .devise-line {{ flex-direction: column; }}
}}
</style>
</head>
<body>
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
  <h1>📈 ETF Dashboard</h1>
  <button onclick="refreshDashboard()" id="refresh-btn"
    style="padding:6px 14px;background:#1565C0;color:#fff;border:none;border-radius:5px;cursor:pointer;font-size:0.85em">
    🔄 Actualiser
  </button>
</div>
<span class="updated">Mis à jour le {now.strftime("%d/%m/%Y à %Hh%M")} (heure de Paris)</span>
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
  chart._sigs = d.sig;
  chart.update();
  btn.parentNode.querySelectorAll(".btn-period").forEach(function(b) {{
    b.classList.remove("active");
  }});
  btn.classList.add("active");
}}

function refreshDashboard() {{
  var btn = document.getElementById("refresh-btn");
  btn.textContent = "⏳ En cours...";
  btn.disabled = true;
  fetch("https://api.github.com/repos/Issi-Vest/etf-dashboard/actions/workflows/dashboard.yml/dispatches", {{
    method: "POST",
    headers: {{
      "Authorization": "token {dispatch_token}",
      "Accept": "application/vnd.github.v3+json",
      "Content-Type": "application/json"
    }},
    body: JSON.stringify({{"ref": "main"}})
  }})
  .then(function(r) {{
    if (r.status === 204) {{
      btn.textContent = "✅ Lancé ! Recharger dans 2min";
      setTimeout(function() {{
        btn.textContent = "🔄 Actualiser";
        btn.disabled = false;
      }}, 120000);
    }} else {{
      btn.textContent = "❌ Erreur " + r.status;
      btn.disabled = false;
    }}
  }})
  .catch(function() {{
    btn.textContent = "❌ Erreur réseau";
    btn.disabled = false;
  }});
}}
</script>
</body>
</html>"""

with open("output/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard généré.")
