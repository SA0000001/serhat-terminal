import streamlit as st

from app.dashboard.pages import overview, live_signals, open_positions, strategy_lab, trade_history, risk_monitor, ai_report

st.set_page_config(page_title="Trading Platform Dashboard", layout="wide")
st.title("Trading Research + Paper Trading Dashboard")

pages = {
    "Overview": overview.render,
    "Live Signals": live_signals.render,
    "Open Positions": open_positions.render,
    "Strategy Lab": strategy_lab.render,
    "Trade History": trade_history.render,
    "Risk Monitor": risk_monitor.render,
    "AI Report": ai_report.render,
}

choice = st.sidebar.selectbox("Page", list(pages.keys()))
pages[choice]()
