import pandas as pd

from app.research.metrics import compute_returns, summary_metrics


def test_metrics_summary() -> None:
    df = pd.DataFrame({"close": [100, 101, 102, 103, 102, 104]})
    signal = pd.Series([0, 1, 1, -1, -1, 1])
    ret = compute_returns(df, signal, 10, 5)
    m = summary_metrics(ret)
    assert "net_profit" in m
    assert "max_drawdown" in m
