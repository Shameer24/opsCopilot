import uuid
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    document_ids: list[uuid.UUID] | None = None  # optional scope override


class Citation(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    page_start: int | None = None
    page_end: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    score: float


class AskResponse(BaseModel):
    answer_markdown: str
    citations: list[Citation]
    query_log_id: uuid.UUID