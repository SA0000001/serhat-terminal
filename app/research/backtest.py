import pandas as pd

from app.research.metrics import compute_returns, summary_metrics
from app.strategies.base import StrategyBase


class BacktestRunner:
    def __init__(self, commission_bps: float = 10, slippage_bps: float = 5) -> None:
        self.commission_bps = commission_bps
        self.slippage_bps = slippage_bps

    def run(self, df: pd.DataFrame, strategy: StrategyBase, params: dict) -> dict:
        signal = strategy.generate(df, params)
        returns = compute_returns(df, signal, self.commission_bps, self.slippage_bps)
        metrics = summary_metrics(returns)
        return {"metrics": metrics, "returns": returns, "params": params, "strategy": strategy.name}
