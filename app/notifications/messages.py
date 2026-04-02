from app.core.models import Signal


def build_signal_message(signal: Signal) -> str:
    return (
        f"Asset: {signal.symbol}\n"
        f"Strategy: {signal.strategy}\n"
        f"TF: {signal.timeframe}\n"
        f"Direction: {signal.direction.value}\n"
        f"Entry: {signal.entry:.2f}\nSL: {signal.stop_loss:.2f}\nTP: {signal.take_profit:.2f}\n"
        f"ATR: {signal.atr:.4f}\nConfidence: {signal.confidence_label}\n"
        f"Time: {signal.ts.isoformat()}\nReason: {signal.reason}"
    )
