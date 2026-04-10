import uuid
from sqlalchemy import String, DateTime, func, ForeignKey, Integer, Text, Float, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_format: Mapped[str] = mapped_column(String(64), nullable=False, default="markdown_v1")

    retrieved_chunk_ids: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    retrieved_scores: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    cited_chunk_ids: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)

    citation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    min_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    embed_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retrieval_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    llm_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    llm_provider: Mapped[str] = mapped_column(String(64), nullable=False, default="openai")
    llm_model: Mapped[str] = mapped_column(String(128), nullable=False, default="unknown")
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)

    citation_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    citations_in_retrieval_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)