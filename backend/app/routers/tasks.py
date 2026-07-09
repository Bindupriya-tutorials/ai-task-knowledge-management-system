from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.deps import get_current_user, require_role
from app.services.activity_service import log_activity

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=schemas.TaskOut, status_code=201)
def create_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin")),
):
    if payload.assigned_to:
        assignee = db.query(models.User).filter(models.User.id == payload.assigned_to).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee user not found")

    task = models.Task(
        title=payload.title,
        description=payload.description,
        assigned_to=payload.assigned_to,
        document_id=payload.document_id,
        created_by=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=List[schemas.TaskOut])
def list_tasks(
    status_filter: Optional[models.TaskStatus] = Query(None, alias="status"),
    assigned_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Dynamic filtering API: /tasks?status=completed  /tasks?assigned_to=1
    Regular users only ever see their own tasks; admins see everything."""
    query = db.query(models.Task)

    if current_user.role.name.value == "user":
        query = query.filter(models.Task.assigned_to == current_user.id)
    elif assigned_to is not None:
        query = query.filter(models.Task.assigned_to == assigned_to)

    if status_filter is not None:
        query = query.filter(models.Task.status == status_filter)

    return query.order_by(models.Task.created_at.desc()).all()


@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task_status(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    is_admin = current_user.role.name.value == "admin"
    if not is_admin and task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own tasks")

    task.status = payload.status
    db.commit()
    db.refresh(task)

    log_activity(
        db, current_user.id, "task_update", f"Task '{task.title}' set to {payload.status.value}"
    )
    return task
