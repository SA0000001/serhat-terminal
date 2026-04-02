from abc import ABC, abstractmethod
import pandas as pd


class IDataProvider(ABC):
    @abstractmethod
    def get_ohlcv(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Return standardized OHLCV dataframe."""
