import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="黃金即時多空建議系統", layout="centered")
st.title("💹 黃金即時多空建議系統（每3秒自動更新）")

placeholder = st.empty()

def fetch_data():
    data = yf.download('GC=F', period='1d', interval='1m')
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA60'] = data['Close'].rolling(window=60).mean()
    return data

def main():
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

        # 正確的空值判斷方式
        if pd.isna(latest_price) or pd.isna(ma5) or pd.isna(ma20) or pd.isna(ma60):
            placeholder.warning("⏳ 資料載入中，請稍候...")
            time.sleep(3)
            continue

        # 多空判斷
        if latest_price > ma5 and ma5 > ma20 and ma20 > ma60:
            advice = "📈 **建議：做多 ✅**"
        elif latest_price < ma5 and ma5 < ma20 and ma20 < ma60:
            advice = "📉 **建議：做空 ⛔**"
        else:
            advice = "⚖️ **建議：觀望中**"

        # 畫面顯示
        with placeholder.container():
            st.metric("🌟 最新金價 (XAU/USD)", f"{latest_price:.2f}")
            st.markdown(f"### 📊 移動平均線參考")
            st.markdown(f"- **MA5：** {ma5:.2f}")
            st.markdown(f"- **MA20：** {ma20:.2f}")
            st.markdown(f"- **MA60：** {ma60:.2f}")
            st.markdown("---")
            st.markdown(f"## 📢 {advice}")
            st.caption("⏱️ 每3秒自動刷新一次數據")

        time.sleep(3)

if __name__ == "__main__":
    main()
