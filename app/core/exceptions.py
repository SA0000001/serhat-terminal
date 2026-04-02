class PlatformError(Exception):
    """Base domain error."""


class DataValidationError(PlatformError):
    """Raised when market data is invalid."""


class HardStopTriggered(PlatformError):
    """Raised when risk hard-stop prevents action."""
