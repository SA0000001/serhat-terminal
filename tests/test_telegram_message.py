from datetime import datetime

from app.core.enums import SignalDirection
from app.core.models import Signal
from app.notifications.messages import build_signal_message


def test_signal_message_format() -> None:
    signal = Signal("EURUSD", "breakout", "1h", SignalDirection.SHORT, 1.1, 1.11, 1.08, 0.01, "MEDIUM", "breakout", datetime.utcnow())
    msg = build_signal_message(signal)
    assert "Asset: EURUSD" in msg
    assert "Direction: SHORT" in msg
