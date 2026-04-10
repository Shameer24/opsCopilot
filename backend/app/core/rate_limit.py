import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import Request
from app.core.errors import AppError


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        q = self._hits[key]
        # evict old
        while q and q[0] <= now - window_seconds:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        return True


limiter = SlidingWindowRateLimiter()


def rate_limit(request: Request, key: str, limit: int, window_seconds: int) -> None:
    if not limiter.allow(key, limit, window_seconds):
        raise AppError(status_code=429, detail="Rate limit exceeded. Please try again shortly.")