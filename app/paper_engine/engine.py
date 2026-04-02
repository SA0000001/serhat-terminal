from dataclasses import asdict, dataclass

from sqlalchemy.orm import Session

from app.core.exceptions import HardStopTriggered
from app.core.models import Signal
from app.risk.emergency import EmergencyManager
from app.storage.repositories.paper import PaperRepository


@dataclass
class PaperEngineState:
    realized_pnl: float = 0.0


class PaperTradingEngine:
    def __init__(self, db: Session, emergency: EmergencyManager) -> None:
        self.repo = PaperRepository(db)
        self.emergency = emergency
        loaded = self.repo.load_engine_state("paper_engine")
        self.state = PaperEngineState(**loaded) if loaded else PaperEngineState()

    def on_signal(self, signal: Signal, qty: float = 1.0) -> int:
        if self.emergency.state.hard_stop or self.emergency.state.no_new_signals:
            raise HardStopTriggered("paper engine blocked by emergency state")
        pos = self.repo.open_position(
            symbol=signal.symbol,
            direction=signal.direction.value,
            entry_price=signal.entry,
            quantity=qty,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
        )
        self._persist_state()
        return pos.id

    def close_position(self, position_id: int, exit_price: float, reason_code: str) -> None:
        positions = {p.id: p for p in self.repo.list_positions()}
        pos = positions[position_id]
        side = 1 if pos.direction == "LONG" else -1
        pnl = (exit_price - pos.entry_price) * pos.quantity * side
        self.state.realized_pnl += pnl
        self.repo.close_position(position_id, pnl=pnl, reason_code=reason_code)
        self._persist_state()

    def _persist_state(self) -> None:
        self.repo.save_engine_state("paper_engine", asdict(self.state))
