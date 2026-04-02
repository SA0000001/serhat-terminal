import pandas as pd


def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    frame = df.set_index("timestamp")
    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    out = frame.resample(timeframe).agg(agg).dropna().reset_index()
    return out
