from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.core.enums import SignalDirection
from app.core.models import Signal
from app.notifications.messages import build_signal_message
from app.notifications.telegram import TelegramNotificationService
from app.services.healthcheck import build_health_payload
from app.services.heartbeat import record_heartbeat
from app.storage.db import Base, engine
from app.storage.models import (
    Asset,
    BacktestRun,
    ClosedTrade,
    EmergencyEvent,
    EngineHeartbeat,
    OptimizationRun,
    PaperPosition,
    SignalModel,
    Strategy,
    StrategyHealthReport,
    StrategyRun,
    WalkForwardRun,
)
from app.storage.repositories.signals import SignalRepository
from app.config.settings import AppSettings
from app.api.deps import get_db

settings = AppSettings()
app = FastAPI(title="Trading Research API", version="0.1.0")
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return build_health_payload()


@app.post("/webhook/signal")
def webhook_signal(payload: dict, db: Session = Depends(get_db)) -> dict:
    signal = Signal(
        symbol=payload["symbol"],
        strategy=payload["strategy"],
        timeframe=payload["timeframe"],
        direction=SignalDirection(payload["direction"]),
        entry=float(payload["entry"]),
        stop_loss=float(payload["stop_loss"]),
        take_profit=float(payload["take_profit"]),
        atr=float(payload.get("atr", 0.0)),
        confidence_label=payload.get("confidence_label", "UNKNOWN"),
        reason=payload.get("reason", "webhook"),
        ts=datetime.utcnow(),
    )
    SignalRepository(db).add(signal)
    msg = build_signal_message(signal)
    TelegramNotificationService(settings.telegram_bot_token, settings.telegram_chat_id).send("New Paper Signal", msg)
    return {"status": "ok"}


@app.post("/heartbeat/{engine_name}")
def heartbeat(engine_name: str, db: Session = Depends(get_db)) -> dict:
    record_heartbeat(db, engine_name=engine_name)
    return {"status": "ok", "engine_name": engine_name}


@app.post("/paper/open")
def paper_open(payload: dict, db: Session = Depends(get_db)) -> dict:
    row = PaperPosition(
        symbol=payload["symbol"],
        direction=payload.get("direction", "LONG"),
        entry_price=float(payload["entry_price"]),
        quantity=float(payload.get("quantity", 1.0)),
        stop_loss=float(payload.get("stop_loss", payload["entry_price"])),
        take_profit=float(payload.get("take_profit", payload["entry_price"])),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "ok", "position_id": row.id}


@app.post("/paper/close/{position_id}")
def paper_close(position_id: int, payload: dict, db: Session = Depends(get_db)) -> dict:
    pos = db.query(PaperPosition).filter(PaperPosition.id == position_id).one()
    exit_price = float(payload["exit_price"])
    side = 1 if pos.direction == "LONG" else -1
    pnl = (exit_price - pos.entry_price) * pos.quantity * side
    db.delete(pos)
    trade = ClosedTrade(symbol=pos.symbol, pnl=pnl, reason_code=payload.get("reason_code", "MANUAL_CLOSE"))
    db.add(trade)
    db.commit()
    return {"status": "ok", "pnl": pnl}


@app.post("/dashboard/seed-demo")
def seed_demo(db: Session = Depends(get_db)) -> dict:
    btc = db.query(Asset).filter(Asset.symbol == "BTCUSDT").one_or_none() or Asset(symbol="BTCUSDT")
    sma = db.query(Strategy).filter(Strategy.name == "sma_cross").one_or_none() or Strategy(name="sma_cross")
    db.add_all([btc, sma])
    db.commit()
    db.refresh(btc)
    db.refresh(sma)

    run = StrategyRun(strategy_id=sma.id, asset_id=btc.id, status="completed")
    db.add(run)
    db.commit()
    db.refresh(run)

    db.add(BacktestRun(strategy_run_id=run.id, metrics={"net_profit": 0.18, "sharpe": 1.25, "profit_factor": 1.45}))
    db.add(OptimizationRun(strategy_run_id=run.id, best_params={"fast": 20, "slow": 55, "neighborhood_stability": 0.82}))
    db.add(WalkForwardRun(strategy_run_id=run.id, summary={"consistency": 0.77, "oos_net_profit": 0.11}))
    db.add(
        SignalModel(
            symbol="BTCUSDT",
            strategy="sma_cross",
            timeframe="1h",
            direction="LONG",
            entry=68000.0,
            stop_loss=67000.0,
            take_profit=70000.0,
            confidence_label="MEDIUM",
            reason="seed",
        )
    )
    db.add(PaperPosition(symbol="XAUUSD", direction="LONG", entry_price=2320.0, quantity=1.0, stop_loss=2295.0, take_profit=2360.0))
    db.add(StrategyHealthReport(symbol="EURUSD", report_text="Strategy healthy; no degradation detected."))
    db.commit()
    return {"status": "ok"}


@app.get("/dashboard/overview")
def dashboard_overview(db: Session = Depends(get_db)) -> dict:
    open_positions = db.query(PaperPosition).all()
    closed = db.query(ClosedTrade).all()
    heartbeat_row = db.query(EngineHeartbeat).order_by(EngineHeartbeat.last_seen.desc()).first()
    total_pnl = float(sum(t.pnl for t in closed))
    win_rate = (sum(1 for t in closed if t.pnl > 0) / len(closed)) if closed else 0.0
    return {
        "total_pnl": total_pnl,
        "open_positions": len(open_positions),
        "win_rate": win_rate,
        "drawdown": 0.0,
        "active_strategies": len({s.strategy for s in db.query(SignalModel).limit(200).all()}),
        "engine_health": "OK",
        "heartbeat": heartbeat_row.last_seen.isoformat() if heartbeat_row else "N/A",
    }


@app.get("/dashboard/live-signals")
def dashboard_live_signals(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(SignalModel).order_by(SignalModel.created_at.desc()).limit(50).all()
    return [
        {
            "asset": r.symbol,
            "strategy": r.strategy,
            "timeframe": r.timeframe,
            "direction": r.direction,
            "entry": r.entry,
            "stop_loss": r.stop_loss,
            "take_profit": r.take_profit,
            "atr": None,
            "confidence": r.confidence_label,
            "timestamp": r.created_at.isoformat(),
        }
        for r in rows
    ]


@app.get("/dashboard/open-positions")
def dashboard_open_positions(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(PaperPosition).order_by(PaperPosition.opened_at.desc()).all()
    return [
        {
            "asset": r.symbol,
            "direction": r.direction,
            "entry": r.entry_price,
            "current_price": r.entry_price,
            "unrealized_pnl": 0.0,
            "holding_time": "N/A",
            "stop_loss": r.stop_loss,
            "take_profit": r.take_profit,
            "risk_status": "NORMAL",
        }
        for r in rows
    ]


@app.get("/dashboard/trade-history")
def dashboard_trade_history(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(ClosedTrade).order_by(ClosedTrade.closed_at.desc()).limit(200).all()
    return [
        {
            "asset": r.symbol,
            "entry": None,
            "exit": None,
            "pnl": r.pnl,
            "exit_reason": r.reason_code,
            "opened_at": None,
            "closed_at": r.closed_at.isoformat(),
        }
        for r in rows
    ]


@app.get("/dashboard/strategy-lab")
def dashboard_strategy_lab(db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(StrategyRun, Strategy, Asset)
        .join(Strategy, Strategy.id == StrategyRun.strategy_id)
        .join(Asset, Asset.id == StrategyRun.asset_id)
        .order_by(StrategyRun.id.desc())
        .limit(100)
        .all()
    )

    payload: list[dict] = []
    for run, strategy, asset in rows:
        backtest = (
            db.query(BacktestRun)
            .filter(BacktestRun.strategy_run_id == run.id)
            .order_by(BacktestRun.id.desc())
            .first()
        )
        opt = (
            db.query(OptimizationRun)
            .filter(OptimizationRun.strategy_run_id == run.id)
            .order_by(OptimizationRun.id.desc())
            .first()
        )
        wf = (
            db.query(WalkForwardRun)
            .filter(WalkForwardRun.strategy_run_id == run.id)
            .order_by(WalkForwardRun.id.desc())
            .first()
        )

        metrics = backtest.metrics if backtest else {}
        wf_summary = wf.summary if wf else {}
        oos = float(wf_summary.get("oos_net_profit", 0.0))
        consistency = float(wf_summary.get("consistency", 0.0))
        pf = float(metrics.get("profit_factor", 0.0))
        stability = float((opt.best_params or {}).get("neighborhood_stability", 0.0)) if opt else 0.0
        robustness = round((0.4 * consistency) + (0.3 * pf) + (0.3 * stability), 4)
        degradation = "YES" if consistency < 0.4 or oos < 0 else "NO"

        payload.append(
            {
                "asset": asset.symbol,
                "selected_strategy": strategy.name,
                "oos_net_profit": oos,
                "walk_forward_score": consistency,
                "robustness_score": robustness,
                "degradation_flag": degradation,
            }
        )

    return payload


@app.get("/dashboard/risk-monitor")
def dashboard_risk_monitor(db: Session = Depends(get_db)) -> dict:
    event = db.query(EmergencyEvent).order_by(EmergencyEvent.created_at.desc()).first()
    return {
        "daily_drawdown": 0.0,
        "weekly_drawdown": 0.0,
        "total_drawdown": 0.0,
        "soft_stop": False,
        "hard_stop": False,
        "no_trade_mode": False,
        "last_emergency_event": event.reason_code if event else "None",
    }


@app.get("/dashboard/ai-report")
def dashboard_ai_report(db: Session = Depends(get_db)) -> str:
    row = db.query(StrategyHealthReport).order_by(StrategyHealthReport.created_at.desc()).first()
    return row.report_text if row else "No AI health report generated yet."
