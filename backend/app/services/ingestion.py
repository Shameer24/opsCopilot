import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.chunk import Chunk
from app.services.storage import storage
from app.services.chunking import chunk_text_lines
from app.services.embeddings import embedding_client
from app.utils.hashing import sha256_text

logger = logging.getLogger("opscopilot.ingestion")


def extract_text_from_file(content_type: str, data: bytes) -> tuple[str, int | None]:
    """Returns (text, page_count)."""
    if content_type == "application/pdf":
        from pypdf import PdfReader
        import io

        reader = PdfReader(io.BytesIO(data))
        pages = []
        for p in reader.pages:
            pages.append(p.extract_text() or "")
        text = "\n\n".join(pages).strip()
        return text, len(reader.pages)

    # plain text/log fallback
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        text = data.decode(errors="ignore")
    return text, None


def ingest_document(db: Session, document_id: uuid.UUID) -> None:
    doc = db.get(Document, document_id)
    if not doc:
        return

    if doc.status == "READY":
        return

    doc.status = "PROCESSING"
    doc.error_message = None
    doc.ingestion_attempts = (doc.ingestion_attempts or 0) + 1
    db.add(doc)
    db.commit()

    try:
        data = storage.open_bytes(doc.storage_path)
        text, page_count = extract_text_from_file(doc.content_type, data)
        text = text.strip()
        if not text:
            raise ValueError("No extractable text found in document.")

        doc.page_count = page_count
        doc.char_count = len(text)

        chunks = chunk_text_lines(text)
        if not chunks:
            raise ValueError("Chunking produced no chunks.")

        # DB expects a fixed pgvector dim (set by migration). We must match it.
        try:
            expected_dim = int(getattr(getattr(Chunk.embedding, "type", None), "dim", 0) or 0)
        except Exception:
            expected_dim = 0

        batch_size = 64
        embeddings: list[list[float]] = []
        texts = [c.text for c in chunks]

        for i in range(0, len(texts), batch_size):
            batch_embeddings = embedding_client.embed_texts(texts[i : i + batch_size])
            for e in batch_embeddings:
                if not isinstance(e, list):
                    raise ValueError(f"Embedding backend returned {type(e)}; expected list[float].")
                e2 = [float(x) for x in e]
                if expected_dim and len(e2) != expected_dim:
                    raise ValueError(
                        f"Embedding dimension mismatch: DB expects {expected_dim}, got {len(e2)}. "
                        "Use the same embedding model for ingestion+query OR change the pgvector column dimension and re-migrate/reset DB."
                    )
                embeddings.append(e2)

        db.query(Chunk).filter(Chunk.document_id == doc.id).delete(synchronize_session=False)

        for c, emb in zip(chunks, embeddings):
            db.add(
                Chunk(
                    document_id=doc.id,
                    user_id=doc.user_id,
                    chunk_index=c.chunk_index,
                    text=c.text,
                    content_hash=sha256_text(c.text),
                    page_start=c.page_start,
                    page_end=c.page_end,
                    line_start=c.line_start,
                    line_end=c.line_end,
                    char_start=c.char_start,
                    char_end=c.char_end,
                    embedding=emb,
                    embedding_model=getattr(embedding_client, "model_name", "unknown"),
                )
            )

        doc.status = "READY"
        doc.processed_at = datetime.now(timezone.utc)
        db.add(doc)
        db.commit()

        logger.info(
            "ingestion_complete",
            extra={"extra": {"document_id": str(doc.id), "chunks": len(chunks)}},
        )

    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        doc.status = "FAILED"
        doc.error_message = str(e)[:2000]
        db.add(doc)
        try:
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
        logger.exception("ingestion_failed", extra={"extra": {"document_id": str(doc.id)}})