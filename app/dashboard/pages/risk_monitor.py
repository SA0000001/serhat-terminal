import streamlit as st

from app.dashboard.data_provider import risk_monitor


def render() -> None:
    st.header("Risk Monitor")
    r = risk_monitor()
    col1, col2, col3 = st.columns(3)
    col1.metric("Daily DD", f"{r['daily_drawdown']*100:.2f}%")
    col2.metric("Weekly DD", f"{r['weekly_drawdown']*100:.2f}%")
    col3.metric("Total DD", f"{r['total_drawdown']*100:.2f}%")
    st.write({k: v for k, v in r.items() if k not in {"daily_drawdown", "weekly_drawdown", "total_drawdown"}})
