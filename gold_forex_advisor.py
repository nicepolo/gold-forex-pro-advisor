import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd

# ─── 頁面 & 自動刷新設定 ─────────────────────────────
st.set_page_config(page_title="黃金即時多空建議系統", layout="centered")
st.title("💴 黃金即時多空建議系統 （3秒自動更新＋趨勢翻轉提醒）")

# 每 3000 ms 自動重新執行整個腳本
st_autorefresh(interval=3000, limit=None, key="datarefresh")

# ─── 用來記錄上一次建議的 Session State ────────────
if "last_advice" not in st.session_state:
    st.session_state.last_advice = None

# ─── 抓資料 & 計算 MA（快取 60 秒） ────────────────────
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

# ─── 資料尚未準備好 ─────────────────────────────────
if data.empty or pd.isna(data["MA60"].iloc[-1]):
    st.warning("⏳ 資料載入中/尚未初始化，請稍候…")
    st.stop()

# ─── 明確取出「最後一筆」單一 float ─────────────────
lp   = data["Close"].iloc[-1]
ma5  = data["MA5"].iloc[-1]
ma20 = data["MA20"].iloc[-1]
ma60 = data["MA60"].iloc[-1]

# ─── 再次防呆：如果任一為 NaN ────────────────────────
if any(pd.isna(v) for v in (lp, ma5, ma20, ma60)):
    st.warning("⏳ 資料尚未完整，稍後再試…")
    st.stop()

# ─── 多空/觀望 邏輯 ─────────────────────────────────
if lp > ma5 > ma20 > ma60:
    advice = "📈 做多"
elif lp < ma5 < ma20 < ma60:
    advice = "📉 做空"
else:
    advice = "⚖️ 觀望中"

# ─── 趨勢翻轉提醒 ───────────────────────────────────
flip_alert = ""
last = st.session_state.last_advice
if last and last != advice:
    if ("做多" in last and "做空" in advice) or ("做空" in last and "做多" in advice):
        flip_alert = "⚡ **趨勢翻轉提醒！**"

st.session_state.last_advice = advice

# ─── 顯示畫面 ───────────────────────────────────────
st.metric("🌟 最新金價 (XAU/USD)", f"{lp:.2f} USD")
st.markdown("### 📊 移動平均線參考")
st.markdown(f"- MA5：**{ma5:.2f}**")
st.markdown(f"- MA20：**{ma20:.2f}**")
st.markdown(f"- MA60：**{ma60:.2f}**")
st.markdown("---")
st.markdown(f"## 🚨 {advice}")
if flip_alert:
    st.markdown(f"### {flip_alert}")
