from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.enums import SignalDirection
from app.core.models import Signal
from app.paper_engine.engine import PaperTradingEngine
from app.risk.emergency import EmergencyManager
from app.storage.db import Base


def test_paper_engine_state_persistence() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()

    paper = PaperTradingEngine(db, EmergencyManager())
    signal = Signal("BTCUSDT", "sma_cross", "1h", SignalDirection.LONG, 100.0, 95.0, 110.0, 1.2, "HIGH", "test", datetime.utcnow())
    pos_id = paper.on_signal(signal)
    paper.close_position(pos_id, 105.0, "TP")

    paper2 = PaperTradingEngine(db, EmergencyManager())
    assert paper2.state.realized_pnl > 0
