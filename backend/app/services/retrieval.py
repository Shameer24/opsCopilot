# app/services/retrieval.py
from __future__ import annotations

import logging
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.embeddings import embedding_client

logger = logging.getLogger("opscopilot.retrieval")


def _vector_literal(vec: List[float]) -> str:
    # pgvector accepts: '[1,2,3]'::vector
    return "[" + ",".join(f"{x:.10f}" for x in vec) + "]"


def vector_search(db: Session, *, user_id: str, query: str, top_k: int = 6) -> List[Dict[str, Any]]:
    q_vec = embedding_client.embed_text(query)  # 1D list[float]
    if len(q_vec) != 384:
        raise ValueError(f"Query embedding dim mismatch: expected 384, got {len(q_vec)}")

    q_str = _vector_literal(q_vec)

    # cosine distance: smaller is closer. We'll convert to score in [~0..1] via (1 - distance)
    sql = text(
        """
        SELECT
          id::text              AS chunk_id,
          document_id::text     AS document_id,
          chunk_index           AS chunk_index,
          text                  AS text,
          embedding_model       AS embedding_model,
          (1.0 - (embedding <=> (:q_embedding)::vector)) AS score
        FROM chunks
        WHERE user_id = (:user_id)::uuid
        ORDER BY embedding <=> (:q_embedding)::vector
        LIMIT :top_k
        """
    )

    rows = db.execute(sql, {"q_embedding": q_str, "user_id": user_id, "top_k": int(top_k)}).mappings().all()
    results = [dict(r) for r in rows]
    logger.info("vector_search_ok", extra={"top_k": top_k, "returned": len(results)})
    return results