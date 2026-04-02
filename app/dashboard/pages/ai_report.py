import streamlit as st

from app.dashboard.data_provider import ai_report_text


def render() -> None:
    st.header("AI Report")
    st.code(ai_report_text())
