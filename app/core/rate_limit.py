import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status

from app.core.config import settings
from app.core.errors import error_response

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, *, limit: int, window_seconds: int) -> bool:
        now = time.time()
        window_start = now - window_seconds
        hits = self._hits[key]
        while hits and hits[0] < window_start:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True

    def reset(self) -> None:
        self._hits.clear()


rate_limiter = InMemoryRateLimiter()


def should_rate_limit(request: Request) -> bool:
    return request.url.path == "/api/v1/auth/login" or request.method in WRITE_METHODS


async def rate_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if not should_rate_limit(request):
        return await call_next(request)

    forwarded_for = request.headers.get("X-Forwarded-For")
    client_host = forwarded_for.split(",")[0].strip() if forwarded_for else None
    client_host = client_host or (request.client.host if request.client else "unknown")
    key = f"{client_host}:{request.url.path}:{request.method}"

    if not rate_limiter.allow(
        key,
        limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    ):
        request_id = getattr(request.state, "request_id", None)
        return error_response(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="rate_limit_exceeded",
            message="Too many requests",
            request_id=request_id,
        )

    return await call_next(request)
