from enum import Enum


class SignalDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


class RiskState(str, Enum):
    NORMAL = "NORMAL"
    SOFT_STOP = "SOFT_STOP"
    HARD_STOP = "HARD_STOP"
