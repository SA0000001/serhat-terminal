from app.core.enums import RiskState


def evaluate_drawdown(daily: float, weekly: float, total: float, cfg: dict) -> RiskState:
    if daily >= cfg["daily_hard"] or weekly >= cfg["weekly_hard"] or total >= cfg["max_total_hard"]:
        return RiskState.HARD_STOP
    if daily >= cfg["daily_warning"] or weekly >= cfg["weekly_warning"] or total >= cfg["max_total_warning"]:
        return RiskState.SOFT_STOP
    return RiskState.NORMAL
