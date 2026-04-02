import streamlit as st

from app.dashboard.data_provider import open_positions


def render() -> None:
    st.header("Open Positions")
    st.dataframe(open_positions(), use_container_width=True)
