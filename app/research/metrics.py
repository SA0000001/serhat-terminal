import numpy as np
import pandas as pd


def compute_returns(df: pd.DataFrame, signal: pd.Series, commission_bps: float, slippage_bps: float) -> pd.Series:
    raw = df["close"].pct_change().fillna(0.0) * signal.shift(1).fillna(0)
    costs = (commission_bps + slippage_bps) / 10000
    turnover = signal.diff().abs().fillna(0)
    return raw - turnover * costs


def summary_metrics(returns: pd.Series) -> dict[str, float]:
    equity = (1 + returns).cumprod()
    dd = equity / equity.cummax() - 1
    wins = returns[returns > 0]
    losses = returns[returns < 0]
    profit_factor = float(wins.sum() / abs(losses.sum())) if len(losses) else 0.0
    sharpe = float(np.sqrt(252) * returns.mean() / returns.std()) if returns.std() else 0.0
    sortino_den = returns[returns < 0].std()
    sortino = float(np.sqrt(252) * returns.mean() / sortino_den) if sortino_den else 0.0
    expectancy = float(returns.mean())
    return {
        "net_profit": float(equity.iloc[-1] - 1),
        "max_drawdown": float(dd.min()),
        "profit_factor": profit_factor,
        "sharpe": sharpe,
        "sortino": sortino,
        "expectancy": expectancy,
        "trades": float((returns != 0).sum()),
        "win_rate": float((returns > 0).mean()),
    }
