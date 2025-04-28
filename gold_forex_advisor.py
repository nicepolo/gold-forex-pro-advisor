import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ─── 頁面 & 自動刷新 ───────────────────────────────
st.set_page_config(page_title="黃金即時K線圖＋建議系統", layout="wide")
st.title("💴 黃金即時K線圖＋多空建議系統（3秒自動更新）")
st_autorefresh(interval=3000, limit=None, key="refresher")

# ─── 下載資料 & 計算 MA ────────────────────────────
@st.cache_data(ttl=60)
def fetch_data():
    df = yf.download("GC=F", period="1d", interval="1m", progress=False)
    if df.empty:
        return df
    df["MA5"]  = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()
    return df

data = fetch_data()
if data.empty or pd.isna(data["MA60"].iloc[-1]):
    st.warning("⏳ 資料載入中，請稍候...")
    st.stop()

# ─── 取最後一筆值 ─────────────────────────────────
lp   = float(data["Close"].iloc[-1])
ma5  = float(data["MA5"].iloc[-1])
ma20 = float(data["MA20"].iloc[-1])
ma60 = float(data["MA60"].iloc[-1])

# ─── 多空建議 ─────────────────────────────────────
if lp > ma5 > ma20 > ma60:
    advice = "📈 做多"
elif lp < ma5 < ma20 < ma60:
    advice = "📉 做空"
else:
    advice = "⚖️ 觀望中"

# ─── 版面分兩欄 ───────────────────────────────────
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
    recent = data.tail(120).copy()
    recent.reset_index(inplace=True)
    # 建立 Plotly K 線圖
    fig = go.Figure(data=[
        go.Candlestick(
            x=recent["Datetime"],
            open=recent["Open"], high=recent["High"],
            low=recent["Low"], close=recent["Close"],
            name="K線"
        ),
        go.Scatter(
            x=recent["Datetime"], y=recent["MA5"],
            mode="lines", name="MA5"
        ),
        go.Scatter(
            x=recent["Datetime"], y=recent["MA20"],
            mode="lines", name="MA20"
        ),
        go.Scatter(
            x=recent["Datetime"], y=recent["MA60"],
            mode="lines", name="MA60"
        ),
        # 底部成交量
        go.Bar(
            x=recent["Datetime"], y=recent["Volume"],
            name="成交量", yaxis="y2", opacity=0.3
        )
    ])

    # 雙 Y 軸設定
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=False)),
        yaxis=dict(title="價格 (USD)"),
        yaxis2=dict(title="成交量", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=30, b=20),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
