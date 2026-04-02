import streamlit as st

from app.dashboard.data_provider import trade_history


def render() -> None:
    st.header("Trade History")
    st.dataframe(trade_history(), use_container_width=True)
