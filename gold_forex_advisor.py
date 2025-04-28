import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 頁面設定
st.set_page_config(page_title="黃金即時多空建議系統", layout="centered")
st.title("💴 黃金即時多空建議系統\n（每3秒自動更新＋趨勢翻轉提醒）")

placeholder = st.empty()

# 建立一個 session_state 用來記錄上一次建議
if "last_advice" not in st.session_state:
    st.session_state.last_advice = None

def fetch_data():
    data = yf.download('GC=F', period='1d', interval='1m')
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA60'] = data['Close'].rolling(window=60).mean()
    return data

def main():
    while True:
        data = fetch_data()

        if data.empty or data['MA60'].isna().all():
            placeholder.warning("⏳ 正在載入資料中，請稍候...")
            time.sleep(3)
            continue

        latest_price = data['Close']
        ma5 = data['MA5']
        ma20 = data['MA20']
        ma60 = data['MA60']

        lp = latest_price.iloc[-1]
        ma5_v = ma5.iloc[-1]
        ma20_v = ma20.iloc[-1]
        ma60_v = ma60.iloc[-1]

        if pd.isna(lp) or pd.isna(ma5_v) or pd.isna(ma20_v) or pd.isna(ma60_v):
            placeholder.warning("⏳ 資料初始化中，請稍後...")
            time.sleep(3)
            continue

        # 多空判斷邏輯
        if lp > ma5_v > ma20_v > ma60_v:
            advice = "📈 做多"
        elif lp < ma5_v < ma20_v < ma60_v:
            advice = "📉 做空"
        else:
            advice = "⚖️ 觀望中"

        # 預設沒有翻轉提醒
        flip_alert = ""

        # 趨勢翻轉判斷
        if st.session_state.last_advice and (st.session_state.last_advice != advice):
            if ("做多" in st.session_state.last_advice and "做空" in advice) or \
               ("做空" in st.session_state.last_advice and "做多" in advice):
                flip_alert = "⚡ **趨勢翻轉提醒！**"

        # 更新上一次建議
        st.session_state.last_advice = advice

        # 畫面顯示
        with placeholder.container():
            st.metric("🌟 最新金價 (XAU/USD)", f"{lp:.2f}")
            st.markdown("### 📊 移動平均線參考")
            st.markdown(f"- **MA5 :** {ma5_v:.2f}")
            st.markdown(f"- **MA20:** {ma20_v:.2f}")
            st.markdown(f"- **MA60:** {ma60_v:.2f}")
            st.markdown("---")
            st.markdown(f"## 🚨 {advice}")

            if flip_alert:
                st.markdown(f"## {flip_alert}")

            st.caption("🕒 每3秒自動刷新一次數據")

        time.sleep(3)

if __name__ == "__main__":
    main()
