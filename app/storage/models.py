from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.db import Base


class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True)


class Strategy(Base):
    __tablename__ = "strategies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)


class StrategyRun(Base):
    __tablename__ = "strategy_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategies.id"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    status: Mapped[str] = mapped_column(String(32), default="created")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    strategy_run_id: Mapped[int] = mapped_column(ForeignKey("strategy_runs.id"))
    metrics: Mapped[dict] = mapped_column(JSON)


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    strategy_run_id: Mapped[int] = mapped_column(ForeignKey("strategy_runs.id"))
    best_params: Mapped[dict] = mapped_column(JSON)


class WalkForwardRun(Base):
    __tablename__ = "walk_forward_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    strategy_run_id: Mapped[int] = mapped_column(ForeignKey("strategy_runs.id"))
    summary: Mapped[dict] = mapped_column(JSON)


class SignalModel(Base):
    __tablename__ = "signals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32))
    strategy: Mapped[str] = mapped_column(String(64))
    timeframe: Mapped[str] = mapped_column(String(16))
    direction: Mapped[str] = mapped_column(String(8))
    entry: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    take_profit: Mapped[float] = mapped_column(Float)
    confidence_label: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PaperPosition(Base):
    __tablename__ = "paper_positions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32))
    direction: Mapped[str] = mapped_column(String(8))
    entry_price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    take_profit: Mapped[float] = mapped_column(Float)
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ClosedTrade(Base):
    __tablename__ = "closed_trades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32))
    pnl: Mapped[float] = mapped_column(Float)
    reason_code: Mapped[str] = mapped_column(String(64))
    closed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MetricsSnapshot(Base):
    __tablename__ = "metrics_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EngineHeartbeat(Base):
    __tablename__ = "engine_heartbeat"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    engine_name: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EmergencyEvent(Base):
    __tablename__ = "emergency_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64))
    reason_code: Mapped[str] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StrategyHealthReport(Base):
    __tablename__ = "strategy_health_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32))
    report_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ConfigSnapshot(Base):
    __tablename__ = "config_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EngineState(Base):
    __tablename__ = "engine_state"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True)
    state: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
