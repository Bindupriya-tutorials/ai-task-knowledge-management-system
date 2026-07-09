from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=schemas.AnalyticsOut)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task_query = db.query(models.Task)
    if current_user.role.name.value == "user":
        task_query = task_query.filter(models.Task.assigned_to == current_user.id)

    all_tasks = task_query.all()
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t.status == models.TaskStatus.completed)
    pending_tasks = total_tasks - completed_tasks

    total_documents = db.query(models.Document).count()
    total_users = db.query(models.User).count()

    search_logs = (
        db.query(models.ActivityLog).filter(models.ActivityLog.action == "search").all()
    )
    counts = Counter(log.details.strip().lower() for log in search_logs if log.details)
    most_searched = [
        {"query": q, "count": c} for q, c in counts.most_common(10)
    ]

    return schemas.AnalyticsOut(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        total_documents=total_documents,
        total_users=total_users,
        most_searched_queries=most_searched,
    )
