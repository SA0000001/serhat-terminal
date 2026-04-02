import pandas as pd

from app.strategies.base import StrategyBase


class MeanReversionStrategy(StrategyBase):
    name = "mean_reversion"

    def generate(self, df: pd.DataFrame, params: dict) -> pd.Series:
        length = int(params.get("length", 20))
        z = float(params.get("z", 1.5))
        mean = df["close"].rolling(length).mean()
        std = df["close"].rolling(length).std()
        score = (df["close"] - mean) / std
        signal = pd.Series(0, index=df.index)
        signal[score > z] = -1
        signal[score < -z] = 1
        return signal
