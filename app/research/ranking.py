def rank_candidates(candidates: list[dict]) -> list[dict]:
    def score(c: dict) -> float:
        ins = c["ins"]
        oos = c["oos"]
        return (
            0.30 * c["robustness"]
            + 0.20 * oos.get("sharpe", 0)
            + 0.15 * oos.get("profit_factor", 0)
            + 0.15 * oos.get("net_profit", 0)
            - 0.10 * abs(oos.get("max_drawdown", 0))
            + 0.10 * ins.get("expectancy", 0)
        )

    return sorted(candidates, key=score, reverse=True)
