import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.deps import get_current_user, require_role
from app.core.config import settings
from app.services.activity_service import log_activity
from app.services.embedding_service import get_embedding_store

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("", response_model=schemas.DocumentOut, status_code=201)
def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin")),
):
    if not file.filename.lower().endswith((".txt", ".md")):
        raise HTTPException(
            status_code=400, detail="Only .txt (or .md) files are supported for upload"
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, stored_name)

    content_bytes = file.file.read()
    with open(filepath, "wb") as f:
        f.write(content_bytes)

    text_content = content_bytes.decode("utf-8", errors="ignore")

    document = models.Document(
        title=title,
        filename=file.filename,
        filepath=filepath,
        content_preview=text_content[:500],
        uploaded_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Core AI step: embed the document content and add to the vector store
    store = get_embedding_store()
    vector_id = store.add_document(document.id, document.title, text_content)
    document.vector_id = vector_id
    db.commit()
    db.refresh(document)

    log_activity(db, current_user.id, "document_upload", f"Uploaded document '{document.title}'")

    return document


@router.get("", response_model=List[schemas.DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Document).order_by(models.Document.created_at.desc()).all()
