def score_robustness(insample: dict[str, float], outsample: dict[str, float], neighborhood_std: float) -> float:
    stability = max(0.0, 1.0 - neighborhood_std)
    oos_ratio = outsample.get("net_profit", 0.0) / max(insample.get("net_profit", 1e-9), 1e-9)
    drawdown_penalty = abs(outsample.get("max_drawdown", 0.0))
    return max(0.0, 0.5 * stability + 0.4 * min(oos_ratio, 1.0) - 0.1 * drawdown_penalty)
