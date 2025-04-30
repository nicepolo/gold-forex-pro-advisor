import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ─── 最先執行：Page config & Title ─────────────────────────
st.set_page_config(
    page_title="XAU/USD 全功能儀表板",
    layout="wide"
)
st.title("💴 XAU/USD 全功能儀表板")

# ─── 接著才注入自訂 CSS (圓角、陰影等微調) ─────────────────────────
st.markdown(
    """
    <style>
    /* 卡片圓角 */
    .css-1d391kg, .css-1v3fvcr, .css-1wbqebj {
        border-radius: 12px !important;
    }
    /* 卡片陰影 */
    .css-12w0qpk {
        box-shadow: 0 4px 20px rgba(0,0,0,0.05) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─── 自動每 3 秒刷新 ───────────────────────────────
st_autorefresh(interval=3000, limit=None, key="refresh")

# ─── 側邊欄：控制面板 ─────────────────────────────────
st.sidebar.header("控制面板")
price_source = st.sidebar.radio("價格來源：", ("自動抓價", "手動輸入"))
interval     = st.sidebar.selectbox("K 線週期：", ["1m","5m","15m","30m","1h"], index=0)
dark_mode    = st.sidebar.checkbox("深色模式")

# ─── 自動抓價函式 (免費免 Key) ─────────────────────────
def fetch_spot_price():
    url    = "https://api.exchangerate.host/convert"
    params = {"from": "XAU", "to": "USD"}
    try:
        r = requests.get(url, params=params, timeout=5).json()
        return float(r.get("result", 0))
    except:
        return None

# ─── 取得最新價 lp ────────────────────────────────────
lp = None
if price_source == "自動抓價":
    lp = fetch_spot_price()
    if lp is None:
        st.sidebar.error("⚠️ 無法取得現貨價格")
else:
    lp = st.sidebar.number_input(
        "💰 手動輸入最新金價 (XAU/USD)",
        min_value=0.0, value=0.0, step=0.01, format="%.2f"
    )

if not lp or lp <= 0:
    st.warning("請在側邊欄選擇有效價格來源並取得價格")
    st.stop()

# ─── 載入 K 線資料並計算均線 ─────────────────────────
@st.cache_data(ttl=300)
def load_ohlc(period: str="1d", interval: str="1m"):
    df = yf.download("GC=F", period=period, interval=interval, progress=False)
    df["MA5"]  = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()
    return df

data = load_ohlc(period="1d", interval=interval)
if data.empty:
    st.warning("⏳ K 線資料尚未就緒，請稍候…")
    st.stop()

# ─── 取得最後一筆均線值 ───────────────────────────────
ma5, ma20, ma60 = data["MA5"].iloc[-1], data["MA20"].iloc[-1], data["MA60"].iloc[-1]

# ─── 多空建議邏輯 ────────────────────────────────────
if lp > ma5 > ma20 > ma60:
    advice = "📈 建議：做多"
elif lp < ma5 < ma20 < ma60:
    advice = "📉 建議：做空"
else:
    advice = "⚖️ 建議：觀望中"

# ─── 版面配置：左側指標、右側圖表 ─────────────────────
col1, col2 = st.columns([1,3], gap="large")

with col1:
    st.metric("🌟 最新金價", f"{lp:.2f} USD")
    st.markdown("### 移動平均線")
    st.markdown(f"- MA5：**{ma5:.2f}**")
    st.markdown(f"- MA20：**{ma20:.2f}**")
    st.markdown(f"- MA60：**{ma60:.2f}**")
    st.markdown("---")
    st.markdown(f"## 🚨 {advice}")

with col2:
    recent = data.tail(200).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=recent["Datetime"], open=recent["Open"], high=recent["High"],
        low=recent["Low"], close=recent["Close"], name="K 線"
    ))
    fig.add_trace(go.Scatter(x=recent["Datetime"], y=recent["MA5"],  mode="lines", name="MA5"))
    fig.add_trace(go.Scatter(x=recent["Datetime"], y=recent["MA20"], mode="lines", name="MA20"))
    fig.add_trace(go.Scatter(x=recent["Datetime"], y=recent["MA60"], mode="lines", name="MA60"))
    fig.add_trace(go.Bar(
        x=recent["Datetime"], y=recent["Volume"], name="成交量",
        yaxis="y2", opacity=0.3
    ))
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        yaxis2=dict(overlaying="y", side="right", title="Volume"),
        template="plotly_dark" if dark_mode else "plotly_white",
        margin=dict(l=20, r=20, t=30, b=20), height=600
    )
    st.plotly_chart(fig, use_container_width=True)
