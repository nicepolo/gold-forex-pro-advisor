import streamlit as st
import yfinance as yf

# 頁面設定
st.set_page_config(page_title="黃金即時價格", page_icon="💹", layout="centered")

# 自動刷新（每3秒自動重整一次）
count = st.experimental_get_query_params().get('count', [0])[0]
st.experimental_set_query_params(count=int(count) + 1)

st.experimental_rerun() if int(count) % 3 == 0 else None

# 畫面
st.title("💹 黃金即時價格")

# 抓取資料
data = yf.download('GC=F', period='1d', interval='1m', progress=False)

if not data.empty:
    latest_price = data['Close'].iloc[-1]
    st.subheader(f"最新價格：{latest_price:.2f} USD")
    st.caption("每3秒自動更新一次")
else:
    st.warning("⏳ 正在載入資料，請稍候...")
