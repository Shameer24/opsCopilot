import os
import uuid
import logging
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.errors import bad_request, not_found
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.models.document import Document
from app.models.chunk import Chunk
from app.schemas.documents import UploadResponse, DocumentOut
from app.services.storage import storage
from app.utils.hashing import sha256_bytes
from app.workers.ingestion_tasks import ingest_document_task

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger("opscopilot.documents")


@router.get("", response_model=list[DocumentOut])
def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    limit = min(max(limit, 1), 100)
    skip = max(skip, 0)
    docs = db.execute(
        select(Document)
        .where(Document.user_id == user.id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).scalars().all()

    return [
        DocumentOut(
            id=d.id,
            filename=d.filename,
            content_type=d.content_type,
            status=d.status,
            file_size_bytes=d.file_size_bytes,
            page_count=d.page_count,
            created_at=d.created_at.isoformat() if hasattr(d.created_at, "isoformat") else str(d.created_at),
        )
        for d in docs
    ]


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    request: Request,
    background: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # rate limit
    rate_limit(request, key=f"upload:{user.id}", limit=settings.RL_UPLOAD_PER_MINUTE, window_seconds=60)

    if not file.filename:
        raise bad_request("Missing filename")

    # size check (UploadFile doesn't always expose size; we read bytes)
    data = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(data) > max_bytes:
        raise bad_request(f"File too large. Max {settings.MAX_UPLOAD_MB}MB")

    content_type = file.content_type or "application/octet-stream"
    if content_type not in ["application/pdf", "text/plain", "application/octet-stream"]:
        logger.info("upload_unusual_content_type", extra={"extra": {"ct": content_type}})

    digest = sha256_bytes(data)

    # store
    doc_id = uuid.uuid4()
    safe_name = os.path.basename(file.filename)
    rel_path = f"{user.id}/{doc_id}/{safe_name}"
    abs_path = storage.save_bytes(rel_path, data)

    doc = Document(
        id=doc_id,
        user_id=user.id,
        filename=safe_name,
        content_type=content_type,
        storage_path=abs_path,
        file_size_bytes=len(data),
        sha256=digest,
        status="UPLOADED",
    )
    db.add(doc)
    db.commit()

    # async ingestion
    background.add_task(ingest_document_task, doc_id)

    logger.info("document_uploaded", extra={"extra": {"doc_id": str(doc_id), "filename": safe_name}})
    return UploadResponse(document_id=doc_id, status="UPLOADED")


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = db.get(Document, document_id)
    if doc is None or doc.user_id != user.id:
        raise not_found("Document not found")

    # Delete associated chunks first (FK cascade not assumed)
    db.execute(delete(Chunk).where(Chunk.document_id == document_id))

    # Remove file from disk (best-effort)
    storage.delete_file(doc.storage_path)

    db.delete(doc)
    db.commit()
    logger.info("document_deleted", extra={"extra": {"doc_id": str(document_id)}})
