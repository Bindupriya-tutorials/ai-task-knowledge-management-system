from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app import models
from app.routers import auth, documents, tasks, search, analytics, users

# Create all tables (users, roles, tasks, documents, activity_logs)
Base.metadata.create_all(bind=engine)


def seed_roles():
    db = SessionLocal()
    try:
        for role_name in (models.RoleName.admin, models.RoleName.user):
            exists = db.query(models.Role).filter(models.Role.name == role_name).first()
            if not exists:
                db.add(models.Role(name=role_name))
        db.commit()
    finally:
        db.close()


seed_roles()

app = FastAPI(
    title="AI-Powered Task & Knowledge Management System",
    description=(
        "Backend for the assignment: admin uploads documents & assigns tasks, "
        "users search documents via AI semantic search and complete tasks."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(tasks.router)
app.include_router(search.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "message": "AI-Powered Task & Knowledge Management System API",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
