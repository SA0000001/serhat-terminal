import pandas as pd

from app.strategies.base import StrategyBase


class BreakoutStrategy(StrategyBase):
    name = "breakout"

    def generate(self, df: pd.DataFrame, params: dict) -> pd.Series:
        lookback = int(params.get("lookback", 20))
        hh = df["high"].rolling(lookback).max().shift(1)
        ll = df["low"].rolling(lookback).min().shift(1)
        long = (df["close"] > hh).astype(int)
        short = (df["close"] < ll).astype(int) * -1
        return long + short
