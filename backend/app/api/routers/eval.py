import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.query_log import QueryLog
from app.models.feedback import Feedback

router = APIRouter(prefix="/eval", tags=["eval"])


@router.get("/recent")
def recent_queries(
    limit: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    limit = min(max(limit, 1), 100)

    rows = db.execute(
        select(QueryLog)
        .where(QueryLog.user_id == user.id)
        .order_by(desc(QueryLog.created_at))
        .limit(limit)
    ).scalars().all()

    return [
        {
            "id": str(r.id),
            "question": r.question,
            "citation_count": r.citation_count,
            "citation_coverage": r.citation_coverage,
            "citations_in_retrieval_ratio": r.citations_in_retrieval_ratio,
            "total_ms": r.total_ms,
            "created_at": r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
        }
        for r in rows
    ]


@router.get("/{query_log_id}")
def query_detail(
    query_log_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ql = db.get(QueryLog, query_log_id)
    if not ql or ql.user_id != user.id:
        return {"detail": "Not found"}

    fb = db.execute(
        select(Feedback).where(Feedback.query_log_id == ql.id, Feedback.user_id == user.id)
    ).scalar_one_or_none()

    return {
        "id": str(ql.id),
        "question": ql.question,
        "answer": ql.answer,
        "retrieved_chunk_ids": ql.retrieved_chunk_ids,
        "retrieved_scores": ql.retrieved_scores,
        "cited_chunk_ids": ql.cited_chunk_ids,
        "citation_count": ql.citation_count,
        "citation_coverage": ql.citation_coverage,
        "citations_in_retrieval_ratio": ql.citations_in_retrieval_ratio,
        "embed_ms": ql.embed_ms,
        "retrieval_ms": ql.retrieval_ms,
        "llm_ms": ql.llm_ms,
        "total_ms": ql.total_ms,
        "llm_model": ql.llm_model,
        "created_at": ql.created_at.isoformat() if hasattr(ql.created_at, "isoformat") else str(ql.created_at),
        "feedback": (
            {
                "rating": fb.rating,
                "comment": fb.comment,
                "created_at": fb.created_at.isoformat() if hasattr(fb.created_at, "isoformat") else str(fb.created_at),
            }
            if fb
            else None
        ),
    }