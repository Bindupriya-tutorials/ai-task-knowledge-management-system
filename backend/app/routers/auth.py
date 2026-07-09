from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.services.activity_service import log_activity

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = (
        db.query(models.User)
        .filter(
            (models.User.username == payload.username) | (models.User.email == payload.email)
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    role = db.query(models.Role).filter(models.Role.name == payload.role).first()
    if not role:
        role = models.Role(name=payload.role)
        db.add(role)
        db.commit()
        db.refresh(role)

    user = models.User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=role.name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"user_id": user.id, "role": user.role.name.value})
    log_activity(db, user.id, "login", f"User {user.username} logged in")
    return schemas.Token(
        access_token=token,
        role=user.role.name,
        username=user.username,
        user_id=user.id,
    )
