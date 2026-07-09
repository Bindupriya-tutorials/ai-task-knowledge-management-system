from sqlalchemy.orm import Session

from app import models


def log_activity(db: Session, user_id: int, action: str, details: str = None) -> models.ActivityLog:
    entry = models.ActivityLog(user_id=user_id, action=action, details=details)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
