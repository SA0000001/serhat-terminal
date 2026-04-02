from sqlalchemy.orm import Session

from app.paper_engine.reconciliation import reconcile_engine_state


def run_reconciliation(db: Session) -> dict:
    return reconcile_engine_state(db)
