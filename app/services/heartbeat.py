from datetime import datetime

from sqlalchemy.orm import Session

from app.storage.models import EngineHeartbeat


def record_heartbeat(db: Session, engine_name: str, status: str = "ok") -> None:
    row = EngineHeartbeat(engine_name=engine_name, status=status, last_seen=datetime.utcnow())
    db.add(row)
    db.commit()
