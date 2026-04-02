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
