import streamlit as st
import yfinance as yf
import time

st.set_page_config(page_title="黃金即時價格", page_icon="💹", layout="centered")

placeholder = st.empty()

while True:
    data = yf.download('GC=F', period='1d', interval='1m', progress=False)

    if not data.empty:
        latest_price = data['Close'].iloc[-1]
        with placeholder.container():
            st.title("💹 黃金即時價格")
            st.subheader(f"最新價格：{latest_price:.2f} USD")
            st.caption("每3秒自動更新一次")

    time.sleep(3)
    st.experimental_rerun()
