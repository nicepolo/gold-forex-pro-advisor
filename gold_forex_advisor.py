import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ─── 頁面 & 自動刷新設定 ─────────────────────────
st.set_page_config(page_title="XAU/USD 多空建議系統", layout="wide")
st.title("💴 XAU/USD 多空建議系統（自動抓價＋手動輸入）")

# 每 3000 ms 自動重新執行腳本
st_autorefresh(interval=3000, limit=None, key="refresh")

# ─── 側邊欄：選擇價格來源 ─────────────────────────
price_source = st.sidebar.radio(
    "📌 價格來源",
    ("自動抓價", "手動輸入")
)

# 自動抓價函式（exchangerate.host 免費介面）
def fetch_xau_usd():
    url    = "https://api.exchangerate.host/convert"
    params = {"from": "XAU", "to": "USD"}
    r      = requests.get(url, params=params, timeout=5).json()
    return float(r.get("result", 0))

# ─── 取得最新價 lp ───────────────────────────────
lp = None
if price_source == "自動抓價":
    try:
        lp = fetch_xau_usd()
    except:
        st.sidebar.error("⚠️ 抓價失敗")
elif price_source == "手動輸入":
    lp = st.sidebar.number_input(
        "💰 手動輸入最新金價 (XAU/USD)",
        min_value=0.0, value=0.0, step=0.01, format="%.2f"
    )

if lp is None or lp <= 0:
    st.warning("⏳ 等待有效價格…")
    st.stop()

# ─── 抓取歷史數據 & 計算 MA ──────────────────────
@st.cache_data(ttl=300)
def fetch_data():
    df = yf.download("GC=F", period="1d", interval="1m", progress=False)
    df["MA5"]  = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()
    return df

data = fetch_data()
if data.empty or pd.isna(data["MA60"].iloc[-1]):
    st.warning("⏳ 數據尚未就緒，稍候…")
    st.stop()

# 取得最後一筆 MA 值
ma5  = float(data["MA5"].iloc[-1])
ma20 = float(data["MA20"].iloc[-1])
ma60 = float(data["MA60"].iloc[-1])

# ─── 多空/觀望建議 ───────────────────────────────
if lp > ma5 > ma20 > ma60:
    advice = "📈 建議：做多"
elif lp < ma5 < ma20 < ma60:
    advice = "📉 建議：做空"
else:
    advice = "⚖️ 建議：觀望中"

# ─── 佈局：左側指標 右側 K 線圖 ─────────────────
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.metric("🌟 最新金價 (XAU/USD)", f"{lp:.2f} USD")
    st.markdown("### 📊 移動平均線")
    st.markdown(f"- MA5：**{ma5:.2f}**")
    st.markdown(f"- MA20：**{ma20:.2f}**")
    st.markdown(f"- MA60：**{ma60:.2f}**")
    st.markdown("---")
    st.markdown(f"## 🚨 {advice}")

with col2:
    recent = data.tail(120).reset_index()
    fig = go.Figure(data=[
        go.Candlestick(
            x=recent["Datetime"], open=recent["Open"],
            high=recent["High"], low=recent["Low"],
            close=recent["Close"], name="期貨K線"
        ),
        go.Scatter(x=recent["Datetime"], y=recent["MA5"],  mode="lines", name="MA5"),
        go.Scatter(x=recent["Datetime"], y=recent["MA20"], mode="lines", name="MA20"),
        go.Scatter(x=recent["Datetime"], y=recent["MA60"], mode="lines", name="MA60")
    ])
    fig.update_layout(xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
