from dataclasses import dataclass
from datetime import datetime
from app.core.enums import SignalDirection


@dataclass(slots=True)
class Signal:
    symbol: str
    strategy: str
    timeframe: str
    direction: SignalDirection
    entry: float
    stop_loss: float
    take_profit: float
    atr: float
    confidence_label: str
    reason: str
    ts: datetime
