import time
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter(tags=["health"])
logger = logging.getLogger("opscopilot.health")


@router.get("/health")
def health(db: Session = Depends(get_db)):
    """
    Liveness + readiness probe.
    Returns {"ok": true, "db": "up"} when all dependencies are healthy.
    Returns {"ok": false, "db": "down"} and HTTP 503 if the database is unreachable.
    """
    t0 = time.perf_counter()
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        logger.warning("health_db_fail", extra={"extra": {"error": str(exc)}})

    db_ms = int((time.perf_counter() - t0) * 1000)
    status_code = 200 if db_ok else 503

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": db_ok,
            "db": "up" if db_ok else "down",
            "db_ms": db_ms,
        },
    )
