from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.errors import bad_request
from app.models.user import User
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.rating not in (1, -1):
        raise bad_request("rating must be 1 or -1")

    fb = Feedback(
        user_id=user.id,
        query_log_id=payload.query_log_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(fb)
    db.commit()
    return FeedbackResponse(ok=True)