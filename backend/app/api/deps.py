from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.errors import unauthorized
from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.user import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthorized("Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
    except Exception:
        raise unauthorized("Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise unauthorized("Invalid token payload")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise unauthorized("User not found or inactive")

    return user