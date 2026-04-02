from dataclasses import dataclass


@dataclass
class EmergencyState:
    hard_stop: bool = False
    no_new_signals: bool = False
    reason: str = ""


class EmergencyManager:
    def __init__(self) -> None:
        self.state = EmergencyState()

    def trigger_hard_stop(self, reason: str) -> None:
        self.state.hard_stop = True
        self.state.no_new_signals = True
        self.state.reason = reason

    def clear(self) -> None:
        self.state = EmergencyState()
