import os
import streamlit as st
import requests
import ccxt
import yfinance as yf
from openai import OpenAI
import pandas as pd
import streamlit.components.v1 as components
from dotenv import load_dotenv

# --- ORTAM DEĞİŞKENLERİ (Güvenli yükleme) ---
load_dotenv()
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
FRED_API_KEY      = os.getenv("FRED_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# API anahtarı kontrolü
if not OPENROUTER_API_KEY:
    st.error("❌ .env dosyasında OPENROUTER_API_KEY eksik! Lütfen doldurun.")
    st.stop()

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

# --- SAYFA YAPISI ---
st.set_page_config(
    page_title="Serhat Alpha Terminal v15.1",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    body { background-color: #020617; }
    .stMetric {
        background-color: #0f172a;
        padding: 20px;
        border-radius: 12px;
        border-bottom: 4px solid #00ff88;
        margin-bottom: 15px;
    }
    .stMetric-macro {
        background-color: #1e1e2f;
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #facc15;
        margin-bottom: 15px;
    }
    .stMetric-data {
        background-color: #170f2a;
        padding: 15px;
        border-radius: 12px;
        border-right: 4px solid #a855f7;
        margin-bottom: 15px;
    }
    .stButton button {
        background-color: #00ff88 !important;
        color: #000 !important;
        font-weight: bold;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        margin-top: 10px;
    }
    .report-box {
        background-color: #020617;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #1e293b;
        line-height: 1.7;
        font-size: 0.95em;
    }
    </style>
""", unsafe_allow_html=True)

# --- VERİ MOTORU ---
@st.cache_data(ttl=300)
def veri_motoru():
    """
    Tüm piyasa verilerini bağımsız try/except bloklarıyla çeker.
    Herhangi bir kaynakta hata olursa diğerleri çalışmaya devam eder.
    """
    v = {}

    # 1. BTC FİYAT VE HACİM (Binance)
    try:
        ex = ccxt.binance()
        t = ex.fetch_ticker("BTC/USDT")
        v["BTC_P"] = f"${t['last']:,.0f}"
        v["BTC_C"] = f"{t['percentage']:.2f}%"
        v["Vol_24h"] = f"${int(t['quoteVolume']):,}"
    except Exception as e:
        v["BTC_P"] = "Hata"; v["BTC_C"] = "—"; v["Vol_24h"] = "—"

    # 2. IBIT (BlackRock Bitcoin ETF)
    try:
        ibit = yf.Ticker("IBIT").history(period="5d")
        last  = ibit["Close"].iloc[-1]
        prev  = ibit["Close"].iloc[-2]
        v["IBIT_P"]   = f"${last:.2f}"
        v["IBIT_C"]   = f"{(last - prev) / prev * 100:.2f}%"
        v["IBIT_Vol"] = f"{int(ibit['Volume'].iloc[-1]):,}"
    except:
        v["IBIT_P"] = "Piyasa Kapalı"; v["IBIT_C"] = "0%"; v["IBIT_Vol"] = "—"

    # 3. GLOBAL MAKRO
    tickers = {
        "VIX":   ("^VIX",     lambda df: round(df["Close"].iloc[-1], 2)),
        "SP500": ("^GSPC",    lambda df: f"{int(df['Close'].iloc[-1]):,}"),
        "GOLD":  ("GC=F",     lambda df: f"${int(df['Close'].iloc[-1]):,}"),
        "US10Y": ("^TNX",     lambda df: f"%{df['Close'].iloc[-1]:.3f}"),
        "DXY":   ("DX-Y.NYB", lambda df: round(df["Close"].iloc[-1], 2)),
    }
    for key, (sym, fn) in tickers.items():
        try:
            df = yf.Ticker(sym).history(period="5d")
            v[key] = fn(df)
        except:
            v[key] = "—"

    # 4. BTC KORELASYONLARl (30 günlük)
    try:
        corr_data = yf.download(
            ["BTC-USD", "^GSPC", "GC=F"],
            period="30d", progress=False
        )["Close"]
        cm = corr_data.corr()
        v["Corr_SP500"] = round(cm.loc["BTC-USD", "^GSPC"], 2)
        v["Corr_Gold"]  = round(cm.loc["BTC-USD", "GC=F"],  2)
    except:
        v["Corr_SP500"] = "—"; v["Corr_Gold"] = "—"

    # 5. MAKRO BALİNA DUVARI AVCISI (5000 kademe, gürültü filtreli)
    try:
        ob = requests.get(
            "https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=5000",
            timeout=6
        ).json()
        bids = [(float(p), float(q)) for p, q in ob["bids"]]
        asks = [(float(p), float(q)) for p, q in ob["asks"]]
        current_p   = bids[0][0]
        noise       = 250     # Fiyata 250$ yakın emirler manipülatif kabul edilir
        bucket_size = 100

        filtered_bids = [(p, q) for p, q in bids if p < current_p - noise] or bids[len(bids)//2:]
        filtered_asks = [(p, q) for p, q in asks if p > current_p + noise] or asks[len(asks)//2:]

        def bucket(data, fn):
            d = {}
            for p, q in data:
                k = fn(p)
                d[k] = d.get(k, 0) + q
            return max(d.items(), key=lambda x: x[1])

        s_wall, s_vol = bucket(filtered_bids, lambda p: int(p / bucket_size) * bucket_size)
        r_wall, r_vol = bucket(filtered_asks, lambda p: int((p / bucket_size) + 1) * bucket_size)

        v["Sup_Wall"] = f"${s_wall:,}"
        v["Sup_Vol"]  = f"{int(s_vol):,} BTC"
        v["Res_Wall"] = f"${r_wall:,}"
        v["Res_Vol"]  = f"{int(r_vol):,} BTC"

        dist_sup = current_p - s_wall
        dist_res = r_wall   - current_p
        if dist_res < dist_sup:
            v["Wall_Status"] = "🔴 Makro Dirence Yakın"
        elif dist_sup < dist_res:
            v["Wall_Status"] = "🟢 Makro Desteğe Yakın"
        else:
            v["Wall_Status"] = "⚖️ Kanal Ortasında"

    except:
        v["Sup_Wall"] = "—"; v["Sup_Vol"] = "—"
        v["Res_Wall"] = "—"; v["Res_Vol"] = "—"
        v["Wall_Status"] = "Veri Yok"

    # 6. USDT MARKET CAP (CoinGecko)
    try:
        cg = requests.get(
            "https://api.coingecko.com/api/v3/simple/price"
            "?ids=tether&vs_currencies=usd&include_market_cap=true",
            timeout=5
        ).json()
        v["USDT_MCap"] = f"${cg['tether']['usd_market_cap'] / 1e9:.2f}B"
    except:
        v["USDT_MCap"] = "—"

    # 7. TAKER BUY/SELL ORANI (Binance Futures)
    try:
        tr = requests.get(
            "https://fapi.binance.com/futures/data/takerbuySellVol"
            "?symbol=BTCUSDT&period=1h&limit=1",
            timeout=5
        ).json()
        v["Taker"] = f"{float(tr[0]['buySellRatio']):.3f}"
    except:
        v["Taker"] = "1.000"

    # 8. OPEN INTEREST & FUNDING RATE
    try:
        oi = requests.get(
            "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT",
            timeout=5
        ).json()
        v["OI"] = f"{int(float(oi['openInterest'])):,} BTC"
    except:
        v["OI"] = "—"

    try:
        fr = requests.get(
            "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT",
            timeout=5
        ).json()
        v["FR"] = f"%{float(fr['lastFundingRate']) * 100:.4f}"
    except:
        v["FR"] = "—"

    # 9. FRED — M2 Para Arzı & FED Faiz
    try:
        m2_obs = requests.get(
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=M2SL&api_key={FRED_API_KEY}&file_type=json"
            f"&sort_order=desc&limit=13",
            timeout=6
        ).json()["observations"]
        latest = float(m2_obs[0]["value"])
        year_ago = float(m2_obs[12]["value"])
        v["M2"] = f"{(latest - year_ago) / year_ago * 100:.2f}"
    except:
        v["M2"] = "—"

    try:
        fed_obs = requests.get(
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=FEDFUNDS&api_key={FRED_API_KEY}&file_type=json"
            f"&sort_order=desc&limit=1",
            timeout=6
        ).json()["observations"]
        v["FED"] = f"%{fed_obs[0]['value']}"
    except:
        v["FED"] = "—"

    # 10. BİTCOİN ON-CHAIN (Blockchain.info)
    try:
        stats = requests.get("https://api.blockchain.info/stats", timeout=5).json()
        v["Active"] = f"{stats['n_blocks_mined'] * 2100:,}"
        v["Hash"]   = f"{stats['hash_rate'] / 1e9:.2f} EH/s"
    except:
        v["Active"] = "—"; v["Hash"] = "—"

    # 11. KORKU/AÇGÖZLÜLÜK & PAZAR PAYI
    try:
        fng = requests.get("https://api.alternative.me/fng/", timeout=5).json()["data"][0]
        v["FNG"] = f"{fng['value']} ({fng['value_classification']})"
    except:
        v["FNG"] = "—"

    try:
        cg_global = requests.get(
            "https://api.coingecko.com/api/v3/global", timeout=5
        ).json()["data"]
        v["Dom"]     = f"%{cg_global['market_cap_percentage']['btc']:.2f}"
        v["ETH_Dom"] = f"%{cg_global['market_cap_percentage']['eth']:.2f}"
    except:
        v["Dom"] = "—"; v["ETH_Dom"] = "—"

    return v


# =========================================================
# ARAYÜZ
# =========================================================

st.title("🛡️ Serhat's Alpha Terminal v15.1")
st.caption("Gerçek zamanlı kripto + makro + balina analizi | Veri her 5 dakikada güncellenir")

# Veriyi yükle
with st.spinner("Piyasa verileri yükleniyor..."):
    data = veri_motoru()

# --- SIDEBAR ---
st.sidebar.title("📥 Veri Arşivi")
st.sidebar.markdown("Anlık verileri CSV olarak indirin.")

df_export = pd.DataFrame(list(data.items()), columns=["Metrik", "Değer"])
csv = df_export.to_csv(index=False, sep=";").encode("utf-8-sig")

st.sidebar.download_button(
    label="💾 Tüm Verileri İndir (CSV)",
    data=csv,
    file_name=f"SerhatTerminal_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
)
st.sidebar.divider()
st.sidebar.markdown("""
**Model:** Gemini 2.0 Flash  
**Veri Kaynakları:** 11 bağımsız API  
**Güncelleme:** Her 5 dakika  
**Grafik:** TradingView  
""")

# --- SATIR 1: KRİPTO TEMEL METRİKLER ---
st.subheader("₿ BTC & Piyasa Göstergeleri")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("BTC Fiyatı",         data.get("BTC_P"),    data.get("BTC_C"))
c2.metric("IBIT (BlackRock)",   data.get("IBIT_P"),   data.get("IBIT_C"))
c3.metric("Korku / Açgözlülük", data.get("FNG"))
c4.metric("Taker B/S Oranı",    data.get("Taker"))
c5.metric("BTC Dominance",      data.get("Dom"))
c6.metric("M2 Likidite (YoY)",  f"%{data.get('M2')}")

st.divider()

# --- SATIR 2: MAKRO EKONOMİ ---
st.subheader("🌍 Global Makro Ekonomi & Korelasyonlar")

m1, m2, m3, m4 = st.columns(4)
m1.markdown(f"<div class='stMetric-macro'><b>S&P 500</b><br><h2 style='margin:0'>{data.get('SP500')}</h2></div>", unsafe_allow_html=True)
m2.markdown(f"<div class='stMetric-macro'><b>Altın (XAU)</b><br><h2 style='margin:0'>{data.get('GOLD')}</h2></div>", unsafe_allow_html=True)
m3.markdown(f"<div class='stMetric-macro'><b>VIX Endeksi</b><br><h2 style='margin:0'>{data.get('VIX')}</h2></div>", unsafe_allow_html=True)
m4.markdown(f"<div class='stMetric-macro'><b>ABD 10 Yıllık Tahvil</b><br><h2 style='margin:0'>{data.get('US10Y')}</h2></div>", unsafe_allow_html=True)

m5, m6, m7, m8 = st.columns(4)
m5.markdown(f"<div class='stMetric-macro'><b>DXY (Dolar Endeksi)</b><br><h2 style='margin:0'>{data.get('DXY')}</h2></div>", unsafe_allow_html=True)
m6.markdown(f"<div class='stMetric-macro'><b>USDT Market Cap</b><br><h2 style='margin:0'>{data.get('USDT_MCap')}</h2></div>", unsafe_allow_html=True)
m7.markdown(f"<div class='stMetric-data'><b>BTC ↔ S&P500 Korelasyon</b><br><h2 style='margin:0'>{data.get('Corr_SP500')}</h2></div>", unsafe_allow_html=True)
m8.markdown(f"<div class='stMetric-data'><b>BTC ↔ Altın Korelasyon</b><br><h2 style='margin:0'>{data.get('Corr_Gold')}</h2></div>", unsafe_allow_html=True)

st.divider()

# --- SATIR 3: GRAFİK (SOL) + TAKVİM & RAPOR (SAĞ) ---
col_chart, col_side = st.columns([2.2, 1.2])

with col_chart:
    st.subheader("📊 Canlı Teknik Analiz + Balina Duvarları")

    ob1, ob2, ob3 = st.columns(3)
    ob1.metric("Tahta Durumu",        data.get("Wall_Status"))
    ob2.metric("🟢 Ana Destek Duvarı", data.get("Sup_Wall"), f"{data.get('Sup_Vol')} Bekliyor")
    ob3.metric("🔴 Ana Direnç Duvarı", data.get("Res_Wall"), f"−{data.get('Res_Vol')} Bekliyor")

    # TradingView Canlı Grafik
    components.html("""
        <div style="height:500px;">
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
                new TradingView.widget({
                    "autosize": true,
                    "symbol": "BINANCE:BTCUSDT",
                    "interval": "D",
                    "theme": "dark",
                    "style": "1",
                    "locale": "tr",
                    "toolbar_bg": "#020617",
                    "enable_publishing": false,
                    "hide_side_toolbar": false,
                    "container_id": "tv_chart"
                });
            </script>
            <div id="tv_chart" style="height:100%;"></div>
        </div>
    """, height=520)

    # Detay tablosu
    st.subheader("⚙️ Detaylı Metrik Tablosu")
    detail_df = pd.DataFrame({
        "Kategori": [
            "IBIT Günlük Hacim", "Open Interest", "Funding Rate",
            "Aktif Adres Tahmini (24s)", "Ağ Gücü (Hashrate)", "ETH Dominance",
            "FED Faiz Oranı", "BTC 24s Hacim (USDT)"
        ],
        "Değer": [
            data.get("IBIT_Vol"), data.get("OI"),      data.get("FR"),
            data.get("Active"),   data.get("Hash"),    data.get("ETH_Dom"),
            data.get("FED"),      data.get("Vol_24h")
        ]
    })
    st.dataframe(detail_df, use_container_width=True, hide_index=True)

with col_side:
    st.subheader("📅 Ekonomik Takvim")
    components.html("""
        <div class="tradingview-widget-container">
            <div class="tradingview-widget-container__widget"></div>
            <script type="text/javascript"
                src="https://s3.tradingview.com/external-embedding/embed-widget-events.js"
                async>
            {
                "colorTheme": "dark",
                "isTransparent": true,
                "width": "100%",
                "height": "480",
                "locale": "tr",
                "importanceFilter": "0,1",
                "currencyFilter": "USD,EUR"
            }
            </script>
        </div>
    """, height=500)

    st.divider()

    # --- AI RAPORU ---
    st.subheader("📄 God Mode Strateji Raporu")
    st.caption("Gemini 2.0 Flash ile anlık makro + balina analizi")

    if st.button("🚀 RAPOR OLUŞTUR", use_container_width=True):
        with st.spinner("AI piyasayı analiz ediyor..."):
            prompt = f"""
Sen deneyimli bir makro-kripto fon yöneticisisin. Aşağıdaki GERÇEK piyasa verilerini kullanarak 
Serhat için kısa ve net bir strateji raporu hazırla. Türkçe yaz.

PIYASA VERİLERİ:
{str(data)}

Rapor yapısı şu başlıkları içersin:
## 1. Makro Durum
BTC'nin S&P500 ve Altın korelasyonlarını yorumla. VIX, DXY ve FED faizinin mevcut anlamını açıkla.

## 2. Balina Duvarı Analizi  
Ana Destek: {data.get('Sup_Wall')} ({data.get('Sup_Vol')})  
Ana Direnç: {data.get('Res_Wall')} ({data.get('Res_Vol')})  
Bu seviyelerin fiyat üzerindeki olası etkisini analiz et.

## 3. On-Chain & Türev Sinyaller
Funding rate, open interest ve taker oranını yorumla.

## 4. Aksiyon Planı
Mevcut verilere göre kısa vadeli (1-3 gün) pozisyon tavsiyesi ver.
Kesin fiyat hedefleri ver, belirsiz ifadelerden kaçın.
"""
            try:
                resp = client.chat.completions.create(
                    model="google/gemini-2.0-flash-001",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500
                )
                rapor = resp.choices[0].message.content
                st.markdown(
                    f'<div class="report-box">{rapor}</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"AI hatası: {e}")
