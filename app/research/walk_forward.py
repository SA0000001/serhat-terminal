import pandas as pd

from app.research.backtest import BacktestRunner
from app.strategies.base import StrategyBase


def run_walk_forward(
    df: pd.DataFrame,
    strategy: StrategyBase,
    params: dict,
    train_bars: int,
    test_bars: int,
    step_bars: int,
    backtester: BacktestRunner,
) -> list[dict]:
    out: list[dict] = []
    i = train_bars
    while i + test_bars <= len(df):
        test = df.iloc[i : i + test_bars].copy()
        result = backtester.run(test, strategy, params)
        out.append(result["metrics"])
        i += step_bars
    return out
