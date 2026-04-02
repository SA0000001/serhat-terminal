import streamlit as st

from app.dashboard.data_provider import overview_snapshot


def render() -> None:
    st.header("Overview")
    s = overview_snapshot()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total PnL", f"${s['total_pnl']:.2f}")
    c2.metric("Open Positions", s["open_positions"])
    c3.metric("Win Rate", f"{s['win_rate']*100:.1f}%")
    c4.metric("Drawdown", f"{s['drawdown']*100:.2f}%")
    st.caption(f"Engine: {s['engine_health']} | Heartbeat: {s['heartbeat']} | Active Strategies: {s['active_strategies']}")
