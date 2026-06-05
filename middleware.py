import time
from collections import defaultdict

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate = refill_rate
        self.last_refill = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        now = time.monotonic()

        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate,
        )
        self.last_refill = now

        if self.tokens < tokens:
            return False

        self.tokens -= tokens
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

        # 10 tokens, refills 1 token/sec
        self.buckets = defaultdict(lambda: TokenBucket(capacity=10, refill_rate=1))

    async def dispatch(self, request, call_next):
        client_ip = request.client.host  # type: ignore
        bucket = self.buckets[client_ip]

        if bucket.consume():
            response = await call_next(request)
            return response
        else:
            return JSONResponse(
                status_code=429, content={"detail": "Too Many Requests"}
            )
