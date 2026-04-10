import uuid
from sqlalchemy import DateTime, func, ForeignKey, SmallInteger, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    query_log_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("query_logs.id"), index=True, nullable=False)

    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1 or -1
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)