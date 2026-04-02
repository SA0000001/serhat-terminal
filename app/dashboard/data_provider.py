"""Dashboard data provider with API-first and demo fallback behavior."""

from __future__ import annotations

from datetime import datetime, timezone
import os

import httpx
import pandas as pd

from app.config.settings import AppSettings


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _base_url() -> str:
    return AppSettings().api_base_url.rstrip("/")


def _get_json(path: str) -> object | None:
    try:
        with httpx.Client(timeout=4.0) as client:
            r = client.get(f"{_base_url()}{path}")
            r.raise_for_status()
            return r.json()
    except Exception:
        return None


def overview_snapshot() -> dict:
    api = _get_json("/dashboard/overview")
    if isinstance(api, dict):
        return api
    return {
        "total_pnl": 1250.35,
        "open_positions": 2,
        "win_rate": 0.56,
        "drawdown": -0.032,
        "active_strategies": 3,
        "engine_health": "DEMO",
        "heartbeat": _now(),
    }


def live_signals() -> pd.DataFrame:
    api = _get_json("/dashboard/live-signals")
    if isinstance(api, list):
        return pd.DataFrame(api)
    return pd.DataFrame(
        [
            {
                "asset": "BTCUSDT",
                "strategy": "sma_cross",
                "timeframe": "1h",
                "direction": "LONG",
                "entry": 68450.0,
                "stop_loss": 67120.0,
                "take_profit": 70600.0,
                "atr": 420.0,
                "confidence": "MEDIUM",
                "timestamp": _now(),
            }
        ]
    )


def open_positions() -> pd.DataFrame:
    api = _get_json("/dashboard/open-positions")
    if isinstance(api, list):
        return pd.DataFrame(api)
    return pd.DataFrame(
        [
            {
                "asset": "XAUUSD",
                "direction": "LONG",
                "entry": 2320.2,
                "current_price": 2333.8,
                "unrealized_pnl": 13.6,
                "holding_time": "5h",
                "stop_loss": 2295.0,
                "take_profit": 2360.0,
                "risk_status": "NORMAL",
            }
        ]
    )


def trade_history() -> pd.DataFrame:
    api = _get_json("/dashboard/trade-history")
    if isinstance(api, list):
        return pd.DataFrame(api)
    return pd.DataFrame(
        [
            {
                "asset": "EURUSD",
                "entry": 1.0821,
                "exit": 1.0849,
                "pnl": 0.0028,
                "exit_reason": "TP",
                "opened_at": "2026-04-01 09:00 UTC",
                "closed_at": "2026-04-01 15:00 UTC",
            }
        ]
    )


def strategy_lab() -> pd.DataFrame:
    api = _get_json("/dashboard/strategy-lab")
    if isinstance(api, list) and api:
        return pd.DataFrame(api)
    return pd.DataFrame(
        [
            {
                "asset": "BTCUSDT",
                "selected_strategy": "sma_cross",
                "oos_net_profit": 0.18,
                "walk_forward_score": 0.74,
                "robustness_score": 0.71,
                "degradation_flag": "NO",
            }
        ]
    )


def risk_monitor() -> dict:
    api = _get_json("/dashboard/risk-monitor")
    if isinstance(api, dict):
        return api
    return {
        "daily_drawdown": 0.021,
        "weekly_drawdown": 0.034,
        "total_drawdown": 0.052,
        "soft_stop": False,
        "hard_stop": False,
        "no_trade_mode": False,
        "last_emergency_event": "None",
    }


def ai_report_text() -> str:
    api = _get_json("/dashboard/ai-report")
    if isinstance(api, str):
        return api
    mode = os.getenv("AI_PROVIDER", "mock")
    return (
        f"Provider: {mode}\n"
        "- BTCUSDT strategy health: stable\n"
        "- XAUUSD: slight performance degradation (watch)\n"
        "- EURUSD: in expected range\n"
        "- Action: run weekly re-optimization and compare OOS drift"
    )
