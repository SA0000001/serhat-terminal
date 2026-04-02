from abc import ABC, abstractmethod

import pandas as pd


class StrategyBase(ABC):
    name: str

    @abstractmethod
    def generate(self, df: pd.DataFrame, params: dict) -> pd.Series:
        """Return signal series with values in {-1,0,1}."""
