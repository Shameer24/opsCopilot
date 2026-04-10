import uuid
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: str
    status: str
    file_size_bytes: int
    page_count: int | None = None
    created_at: str


class UploadResponse(BaseModel):
    document_id: uuid.UUID
    status: str
