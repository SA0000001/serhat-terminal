import pandas as pd

from app.strategies.base import StrategyBase


class SmaCrossStrategy(StrategyBase):
    name = "sma_cross"

    def generate(self, df: pd.DataFrame, params: dict) -> pd.Series:
        fast = int(params.get("fast", 20))
        slow = int(params.get("slow", 50))
        sma_fast = df["close"].rolling(fast).mean()
        sma_slow = df["close"].rolling(slow).mean()
        return (sma_fast > sma_slow).astype(int).replace({0: -1})
