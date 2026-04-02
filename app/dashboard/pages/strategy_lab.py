import streamlit as st

from app.dashboard.data_provider import strategy_lab


def render() -> None:
    st.header("Strategy Lab")
    st.dataframe(strategy_lab(), use_container_width=True)
