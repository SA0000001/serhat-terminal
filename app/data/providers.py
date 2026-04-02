from pathlib import Path

import pandas as pd

from app.core.exceptions import DataValidationError
from app.core.interfaces import IDataProvider
from app.data.validators import validate_ohlcv


class CsvDataProvider(IDataProvider):
    """CSV backed provider for historical research datasets."""

    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir = Path(base_dir)

    def get_ohlcv(self, symbol: str, timeframe: str) -> pd.DataFrame:
        path = self.base_dir / f"{symbol}_{timeframe}.csv"
        if not path.exists():
            raise DataValidationError(f"missing csv: {path}")
        df = pd.read_csv(path, parse_dates=["timestamp"])
        validate_ohlcv(df)
        return df.sort_values("timestamp").reset_index(drop=True)


class TradingViewAdapterPlaceholder(IDataProvider):
    """TODO: implement webhook + adapter ingestion for TradingView data."""

    def get_ohlcv(self, symbol: str, timeframe: str) -> pd.DataFrame:
        raise NotImplementedError("TradingView adapter is planned for phase 2")
