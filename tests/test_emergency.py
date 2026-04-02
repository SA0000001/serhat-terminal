from app.risk.emergency import EmergencyManager


def test_emergency_stop() -> None:
    em = EmergencyManager()
    em.trigger_hard_stop("max_dd")
    assert em.state.hard_stop
    assert em.state.no_new_signals
