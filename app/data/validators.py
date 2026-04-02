import pandas as pd

from app.core.exceptions import DataValidationError


REQUIRED_COLS = {"timestamp", "open", "high", "low", "close", "volume"}


def validate_ohlcv(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise DataValidationError(f"missing columns: {sorted(missing)}")
    if df.empty:
        raise DataValidationError("dataset is empty")
