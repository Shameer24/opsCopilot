import uuid
from app.db.session import SessionLocal
from app.services.ingestion import ingest_document


def ingest_document_task(document_id: uuid.UUID) -> None:
    db = SessionLocal()
    try:
        ingest_document(db, document_id)
    finally:
        db.close()