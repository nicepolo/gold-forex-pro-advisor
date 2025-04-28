import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 頁面設定
st.set_page_config(page_title="黃金即時多空建議系統（3秒刷新＋翻轉提醒）", layout="centered")
st.title("💴 黃金即時多空建議系統（3秒自動更新＋趨勢翻轉提醒）")

placeholder = st.empty()

# 初始化 session_state
if "last_advice" not in st.session_state:
    st.session_state.last_advice = None

def fetch_data():
    try:
        data = yf.download('GC=F', period='1d', interval='1m', progress=False)
        data['MA5'] = data['Close'].rolling(window=5).mean()
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA60'] = data['Close'].rolling(window=60).mean()
        return data
    except:
        return pd.DataFrame()

def main():
    while True:
        data = fetch_data()

        if data.empty:
            placeholder.warning("⏳ 資料載入中，請稍候...")
            time.sleep(3)
            continue

        try:
            lp = data['Close'].iloc[-1]
            ma5_v = data['MA5'].iloc[-1]
            ma20_v = data['MA20'].iloc[-1]
            ma60_v = data['MA60'].iloc[-1]
        except:
            placeholder.warning("⏳ 等待最新數據...")
            time.sleep(3)
            continue

        # 檢查是否有NaN
        if any([
            pd.isna(lp),
            pd.isna(ma5_v),
            pd.isna(ma20_v),
            pd.isna(ma60_v)
        ]):
            placeholder.warning("⏳ 資料尚未完整，稍後再試...")
            time.sleep(3)
            continue

        # 多空建議判斷（這次用單一數字比較）
        if lp > ma5_v > ma20_v > ma60_v:
            advice = "📈 做多"
        elif lp < ma5_v < ma20_v < ma60_v:
            advice = "📉 做空"
        else:
            advice = "⚖️ 觀望中"

        # 趨勢翻轉提醒
        flip_alert = ""
        if st.session_state.last_advice and (st.session_state.last_advice != advice):
            if ("做多" in st.session_state.last_advice and "做空" in advice) or \
               ("做空" in st.session_state.last_advice and "做多" in advice):
                flip_alert = "⚡ **趨勢翻轉提醒！**"

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
