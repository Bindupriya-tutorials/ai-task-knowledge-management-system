from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.deps import get_current_user
from app.services.activity_service import log_activity
from app.services.embedding_service import get_embedding_store

router = APIRouter(prefix="/search", tags=["AI Semantic Search"])


@router.post("", response_model=List[schemas.SearchResult])
def semantic_search(
    payload: schemas.SearchQuery,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    store = get_embedding_store()
    raw_results = store.search(payload.query, top_k=payload.top_k)

    results = [
        schemas.SearchResult(
            document_id=meta["document_id"],
            title=meta["title"],
            snippet=meta["text"][:300],
            score=round(score, 4),
        )
        for meta, score in raw_results
    ]

    log_activity(db, current_user.id, "search", payload.query)
    return results
