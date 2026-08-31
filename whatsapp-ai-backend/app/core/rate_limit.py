from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock


class InMemoryRateLimiter:
    """Per-user sliding window limiter. Use Redis in production via REDIS_URL later."""

    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            bucket = self._hits[key]
            cutoff = now - self.window
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= self.limit:
                return False
            bucket.append(now)
            return True


class RedisRateLimiter:
    def __init__(self, redis_url: str, limit: int, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window = window_seconds
        self._fallback = InMemoryRateLimiter(limit, window_seconds)
        self._redis = None
        try:
            import redis  # type: ignore

            self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
        except Exception:
            self._redis = None

    def allow(self, key: str) -> bool:
        if self._redis is None:
            return self._fallback.allow(key)
        try:
            redis_key = f"rl:{key}"
            pipe = self._redis.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, self.window, nx=True)
            count, _ = pipe.execute()
            return int(count) <= self.limit
        except Exception:
            return self._fallback.allow(key)


def build_rate_limiter(limit: int, redis_url: str = "") -> InMemoryRateLimiter | RedisRateLimiter:
    if redis_url:
        return RedisRateLimiter(redis_url, limit)
    return InMemoryRateLimiter(limit)
