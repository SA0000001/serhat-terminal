import pandas as pd


def in_out_split(df: pd.DataFrame, ratio: float = 0.7) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = int(len(df) * ratio)
    return df.iloc[:idx].copy(), df.iloc[idx:].copy()
