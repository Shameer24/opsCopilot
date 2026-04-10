# app/api/routers/chat.py
import logging
import time
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.services.retrieval import vector_search
from app.services.llm import llm_client
from app.services.evaluation import citation_coverage, citations_in_retrieval_ratio
from app.api.deps import get_current_user
from app.models.user import User
from app.models.query_log import QueryLog
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.chat import AskRequest, AskResponse, Citation

logger = logging.getLogger("opscopilot.chat")

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_sources_block(results: list[dict]) -> str:
    blocks: list[str] = []
    for r in results:
        header = (
            f"[CHUNK_ID={r['chunk_id']}] "
            f"[DOC_ID={r['document_id']}] "
            f"[SCORE={float(r.get('score', 0.0)):.4f}]"
        )
        text = (r.get("text") or "").strip()
        if text:
            blocks.append(header + "\n" + text)
    return "\n---\n".join(blocks)


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AskResponse:
    t_start = time.perf_counter()

    try:
        # Vector retrieval (includes embed time)
        t_retrieval_start = time.perf_counter()
        results = vector_search(
            db,
            user_id=str(current_user.id),
            query=payload.question,
            top_k=settings.TOP_K,
        )
        retrieval_ms = int((time.perf_counter() - t_retrieval_start) * 1000)

        sources_block = _build_sources_block(results)

        # LLM call
        t_llm_start = time.perf_counter()
        llm_result = llm_client.answer_with_citations(payload.question, sources_block)
        llm_ms = int((time.perf_counter() - t_llm_start) * 1000)

        answer_markdown: str = llm_result.get("answer_markdown", "")
        cited_ids_str: List[str] = llm_result.get("cited_chunk_ids", [])

        # Build lookup maps from retrieval results
        retrieval_map = {r["chunk_id"]: r for r in results}
        retrieved_chunk_ids = [r["chunk_id"] for r in results]
        retrieved_scores = [float(r.get("score", 0.0)) for r in results]

        # Resolve cited chunks to full Citation objects
        citations: List[Citation] = []
        for cid_str in cited_ids_str:
            if cid_str not in retrieval_map:
                continue
            try:
                chunk_uuid = uuid.UUID(cid_str)
                chunk = db.get(Chunk, chunk_uuid)
                if chunk is None:
                    continue
                doc = db.get(Document, chunk.document_id)
                filename = doc.filename if doc else "unknown"
                citations.append(
                    Citation(
                        chunk_id=chunk_uuid,
                        document_id=chunk.document_id,
                        filename=filename,
                        page_start=chunk.page_start,
                        page_end=chunk.page_end,
                        line_start=chunk.line_start,
                        line_end=chunk.line_end,
                        score=float(retrieval_map[cid_str].get("score", 0.0)),
                    )
                )
            except Exception:
                logger.warning("citation_build_failed", extra={"chunk_id": cid_str})

        # Evaluation metrics
        cited_uuids = [c.chunk_id for c in citations]
        retrieved_uuids = [uuid.UUID(cid) for cid in retrieved_chunk_ids]
        cov = citation_coverage(answer_markdown, len(citations))
        cir = citations_in_retrieval_ratio(cited_uuids, retrieved_uuids)

        total_ms = int((time.perf_counter() - t_start) * 1000)

        usage = llm_result.get("_usage") or {}
        prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
        completion_tokens = usage.get("completion_tokens") if isinstance(usage, dict) else None

        # Persist query log
        qlog = QueryLog(
            user_id=current_user.id,
            question=payload.question,
            answer=answer_markdown,
            retrieved_chunk_ids=retrieved_chunk_ids,
            retrieved_scores=retrieved_scores,
            cited_chunk_ids=cited_ids_str,
            citation_count=len(citations),
            top_k=settings.TOP_K,
            min_score=settings.MIN_SCORE,
            embed_ms=0,
            retrieval_ms=retrieval_ms,
            llm_ms=llm_ms,
            total_ms=total_ms,
            llm_provider=llm_result.get("_provider", "unknown"),
            llm_model=llm_result.get("_model", "unknown"),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            citation_coverage=cov,
            citations_in_retrieval_ratio=cir,
        )
        db.add(qlog)
        db.commit()
        db.refresh(qlog)

        logger.info(
            "chat_ask_ok",
            extra={
                "query_log_id": str(qlog.id),
                "citations": len(citations),
                "total_ms": total_ms,
            },
        )

        return AskResponse(
            answer_markdown=answer_markdown,
            citations=citations,
            query_log_id=qlog.id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("chat_ask_failed")
        raise HTTPException(status_code=500, detail=str(e))
