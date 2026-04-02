import streamlit as st

from app.dashboard.data_provider import live_signals


def render() -> None:
    st.header("Live Signals")
    st.dataframe(live_signals(), use_container_width=True)
