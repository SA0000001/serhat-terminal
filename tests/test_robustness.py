from app.research.robustness import score_robustness


def test_robustness_score_bounds() -> None:
    s = score_robustness({"net_profit": 0.2}, {"net_profit": 0.1, "max_drawdown": -0.05}, 0.1)
    assert 0 <= s <= 1
