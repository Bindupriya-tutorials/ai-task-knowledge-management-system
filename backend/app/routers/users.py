from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.deps import require_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin")),
):
    users = db.query(models.User).all()
    return [
        schemas.UserOut(
            id=u.id,
            username=u.username,
            email=u.email,
            role=u.role.name,
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]
