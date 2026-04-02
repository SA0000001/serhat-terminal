from app.core.models import Signal
from app.storage.models import SignalModel
from app.storage.repositories.base import BaseRepository


class SignalRepository(BaseRepository):
    def add(self, signal: Signal) -> SignalModel:
        model = SignalModel(
            symbol=signal.symbol,
            strategy=signal.strategy,
            timeframe=signal.timeframe,
            direction=signal.direction.value,
            entry=signal.entry,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            confidence_label=signal.confidence_label,
            reason=signal.reason,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
