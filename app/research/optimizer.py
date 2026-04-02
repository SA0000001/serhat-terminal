from itertools import product

import pandas as pd

from app.research.backtest import BacktestRunner
from app.research.robustness import score_robustness
from app.research.splitters import in_out_split
from app.strategies.base import StrategyBase


class GridOptimizer:
    def __init__(self, backtester: BacktestRunner) -> None:
        self.backtester = backtester

    def optimize(self, df: pd.DataFrame, strategy: StrategyBase, grid: dict[str, list]) -> list[dict]:
        ins, oos = in_out_split(df)
        keys = list(grid.keys())
        results: list[dict] = []
        for values in product(*[grid[k] for k in keys]):
            params = dict(zip(keys, values, strict=True))
            ins_r = self.backtester.run(ins, strategy, params)
            oos_r = self.backtester.run(oos, strategy, params)
            robust = score_robustness(ins_r["metrics"], oos_r["metrics"], neighborhood_std=0.2)
            results.append({"params": params, "ins": ins_r["metrics"], "oos": oos_r["metrics"], "robustness": robust})
        return sorted(results, key=lambda x: x["robustness"], reverse=True)
