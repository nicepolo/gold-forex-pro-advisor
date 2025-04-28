import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 頁面設定
st.set_page_config(page_title="黃金即時多空建議系統", page_icon="💹", layout="centered")
st.markdown(
    """
    <div style='text-align: center; padding: 10px; background-color: #FFF8DC; border-radius: 10px;'>
    <h1 style='color: #FF8C00;'>💹 黃金即時多空建議系統</h1>
    <h4 style='color: gray;'>（每3秒自動更新）</h4>
    </div>
    """, 
    unsafe_allow_html=True
)

placeholder = st.empty()

# 抓取資料
def fetch_data():
    data = yf.download('GC=F', period='1d', interval='1m', progress=False)
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA60'] = data['Close'].rolling(window=60).mean()
    return data

while True:
    data = fetch_data()

if data.empty or pd.isna(data['MA60'].iloc[-1]):
        placeholder.warning("⏳ 正在載入資料，請稍候...")
        time.sleep(3)
        continue

    latest_price = data['Close'].iloc[-1]
    ma5 = data['MA5'].iloc[-1]
    ma20 = data['MA20'].iloc[-1]
    ma60 = data['MA60'].iloc[-1]

if pd.notna(ma5) and pd.notna(ma20) and pd.notna(ma60):
        if latest_price > ma5 > ma20 > ma60:
            advice = "📈 **建議：做多 ✅**"
        elif latest_price < ma5 < ma20 < ma60:
            advice = "📉 **建議：做空 🔻**"
        else:
            advice = "⚖️ **建議：觀望中**"
    else:
        advice = "⏳ 數據初始化中，請稍候..."

    with placeholder.container():
        st.metric("🌟 最新金價 (XAU/USD)", f"{latest_price:.2f} USD")
        st.markdown("### 📊 移動平均線參考")
        st.markdown(f"- **MA5：** {ma5:.2f}")
        st.markdown(f"- **MA20：** {ma20:.2f}")
        st.markdown(f"- **MA60：** {ma60:.2f}")
        st.markdown("---")
        st.markdown(f"## 🚨 {advice}")
        st.caption("⏱️ 每3秒自動刷新一次數據")

    time.sleep(3)

    # 判斷方向
    if latest_price > ma5 > ma20 > ma60:
        advice = "📈 **建議：做多 ✅**"
    elif latest_price < ma5 < ma20 < ma60:
        advice = "📉 **建議：做空 🔻**"
    else:
        advice = "⚖️ **建議：觀望中**"

    # 顯示內容
    with placeholder.container():
        st.metric("🌟 最新金價 (XAU/USD)", f"{latest_price:.2f} USD")
        st.markdown(
            f"""
            <div style='background-color: #F5F5F5; padding: 15px; border-radius: 10px;'>
            <h3>📊 移動平均線</h3>
            <ul>
            <li>MA5：<b>{ma5:.2f}</b></li>
            <li>MA20：<b>{ma20:.2f}</b></li>
            <li>MA60：<b>{ma60:.2f}</b></li>
            </ul>
            <hr>
            <h2 style='color: #FF4500;'>{advice}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("⏱️ 每3秒自動更新一次數據")

    time.sleep(3)
