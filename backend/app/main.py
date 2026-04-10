import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routers.health import router as health_router
from app.api.routers.auth import router as auth_router
from app.api.routers.documents import router as documents_router
from app.api.routers.chat import router as chat_router
from app.api.routers.feedback import router as feedback_router
from app.api.routers.eval import router as eval_router

setup_logging(settings.ENV)
logger = logging.getLogger("opscopilot.app")

app = FastAPI(
    title=settings.APP_NAME,
    description="RAG-powered Q&A over your operational documents.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every HTTP request with method, path, status and latency."""
    t0 = time.perf_counter()
    response = await call_next(request)
    ms = int((time.perf_counter() - t0) * 1000)
    logger.info(
        "http_request",
        extra={
            "extra": {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "ms": ms,
            }
        },
    )
    return response


app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(feedback_router, prefix=settings.API_PREFIX)
app.include_router(eval_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def on_startup():
    # Validate required env vars are set
    missing = []
    if not settings.JWT_SECRET or settings.JWT_SECRET == "change_me_to_a_long_random_string":
        missing.append("JWT_SECRET")
    if missing:
        logger.warning(
            "startup_missing_config",
            extra={"extra": {"missing": missing}},
        )
    logger.info("startup", extra={"extra": {"env": settings.ENV}})


@app.on_event("shutdown")
def on_shutdown():
    logger.info("shutdown")
