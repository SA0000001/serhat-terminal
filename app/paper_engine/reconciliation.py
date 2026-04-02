from sqlalchemy.orm import Session

from app.storage.repositories.paper import PaperRepository


def reconcile_engine_state(db: Session) -> dict:
    repo = PaperRepository(db)
    positions = repo.list_positions()
    state = repo.load_engine_state("paper_engine") or {}
    return {"open_positions": len(positions), "engine_state": state}
