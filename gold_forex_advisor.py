import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="黃金即時多空建議系統", page_icon="💹", layout="centered")

page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
}
h1, h2, h3, h4, h5, h6, p {
    font-family: 'Arial', sans-serif;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

st_autorefresh(interval=3000, limit=None, key="auto-refresh")

st.markdown(
    """
    <div style='text-align: center; padding: 10px; background-color: #fff8dc; border-radius: 12px;'>
        <h1 style='color: #ff8c00;'>💹 黃金即時多空建議系統</h1>
        <h4 style='color: #666;'>（每3秒自動更新）</h4>
    </div>
    """, 
    unsafe_allow_html=True
)

def fetch_data():
    data = yf.download('GC=F', period='1d', interval='1m', progress=False)
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA60'] = data['Close'].rolling(window=60).mean()
    return data

def main():
    data = fetch_data()

    if data.empty or pd.isna(data['MA60'].iloc[-1]):
        st.warning("⏳ 正在載入資料，請稍候...")
        return

    latest_price = data['Close'].iloc[-1]
    ma5 = data['MA5'].iloc[-1]
    ma20 = data['MA20'].iloc[-1]
    ma60 = data['MA60'].iloc[-1]

    advice = "⏳ 數據初始化中，請稍候..."  # 預設訊息

    if pd.notna(latest_price) and pd.notna(ma5) and pd.notna(ma20) and pd.notna(ma60):
        if (latest_price > ma5) and (ma5 > ma20) and (ma20 > ma60):
            advice = "📈 **建議：做多 ✅**"
        elif (latest_price < ma5) and (ma5 < ma20) and (ma20 < ma60):
            advice = "📉 **建議：做空 🔻**"
        else:
            advice = "⚖️ **建議：觀望中**"

    st.markdown(
        f"""
        <div style='background-color: #ffffffdd; padding: 20px; border-radius: 12px; animation: fadeIn 1s;'>
            <h2 style='text-align: center;'>🌟 最新金價 (XAU/USD)</h2>
            <h1 style='text-align: center; color: #228B22;'>{latest_price:.2f} USD</h1>
            <hr style='margin: 10px 0;'>
            <h3>📊 移動平均線參考</h3>
            <ul>
                <li>MA5：<b>{ma5:.2f}</b></li>
                <li>MA20：<b>{ma20:.2f}</b></li>
                <li>MA60：<b>{ma60:.2f}</b></li>
            </ul>
            <hr style='margin: 10px 0;'>
            <h2 style='color: #DC143C; text-align: center;'>{advice}</h2>
        </div>
        <style>
        @keyframes fadeIn {{
            0% {{opacity: 0;}}
            100% {{opacity: 1;}}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.caption("⏱️ 每3秒自動刷新一次數據")

main()
