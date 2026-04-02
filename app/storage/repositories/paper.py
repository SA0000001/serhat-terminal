from datetime import datetime

from app.storage.models import ClosedTrade, EngineState, PaperPosition
from app.storage.repositories.base import BaseRepository


class PaperRepository(BaseRepository):
    def open_position(self, **kwargs) -> PaperPosition:
        pos = PaperPosition(**kwargs)
        self.db.add(pos)
        self.db.commit()
        self.db.refresh(pos)
        return pos

    def list_positions(self) -> list[PaperPosition]:
        return self.db.query(PaperPosition).all()

    def close_position(self, position_id: int, pnl: float, reason_code: str) -> ClosedTrade:
        pos = self.db.query(PaperPosition).filter(PaperPosition.id == position_id).one()
        self.db.delete(pos)
        trade = ClosedTrade(symbol=pos.symbol, pnl=pnl, reason_code=reason_code)
        self.db.add(trade)
        self.db.commit()
        return trade

    def save_engine_state(self, key: str, state: dict) -> EngineState:
        existing = self.db.query(EngineState).filter(EngineState.key == key).one_or_none()
        if existing:
            existing.state = state
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return existing
        row = EngineState(key=key, state=state)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def load_engine_state(self, key: str) -> dict | None:
        row = self.db.query(EngineState).filter(EngineState.key == key).one_or_none()
        return None if row is None else row.state
