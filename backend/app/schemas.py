from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import RoleName, TaskStatus


# ---------- Auth ----------
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleName = RoleName.user


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleName
    username: str
    user_id: int


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: RoleName
    is_active: bool
    created_at: datetime


# ---------- Documents ----------
class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    filename: str
    content_preview: Optional[str] = None
    uploaded_by: int
    created_at: datetime


class SearchQuery(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    document_id: int
    title: str
    snippet: str
    score: float


# ---------- Tasks ----------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    document_id: Optional[int] = None


class TaskUpdate(BaseModel):
    status: TaskStatus


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    assigned_to: Optional[int] = None
    created_by: int
    document_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# ---------- Activity Logs ----------
class ActivityLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    action: str
    details: Optional[str] = None
    created_at: datetime


# ---------- Analytics ----------
class AnalyticsOut(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    total_documents: int
    total_users: int
    most_searched_queries: List[dict]
