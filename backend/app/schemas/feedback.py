import uuid
from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    query_log_id: uuid.UUID
    rating: int = Field(..., description="1 for up, -1 for down")
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackResponse(BaseModel):
    ok: bool = True