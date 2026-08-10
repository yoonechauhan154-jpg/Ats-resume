"""Rate limiting via Upstash Redis, with an in-memory fallback.

Privacy note: keys are derived from a hash of the client IP + date. We never
store request payloads or resume content.
"""

from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from typing import Optional

from ..core.config import get_settings

_REDIS_EXPIRE_SECONDS = 60 * 60 * 24  # 24h rolling window per key


class MemoryRateLimiter:
    """Thread-safe-ish in-memory limiter used when REDIS_URL is not set."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _prune(self, key: str, now: float) -> None:
        self._hits[key] = [t for t in self._hits[key] if now - t < self.window]

    def hit(self, key: str) -> tuple[bool, int]:
        """Record a hit; return (allowed, remaining)."""
        now = time.monotonic()
        self._prune(key, now)
        if len(self._hits[key]) >= self.limit:
            return False, 0
        self._hits[key].append(now)
        return True, max(0, self.limit - len(self._hits[key]))

    def remaining(self, key: str) -> int:
        now = time.monotonic()
        self._prune(key, now)
        return max(0, self.limit - len(self._hits[key]))

    def reset(self, key: str) -> None:
        self._hits.pop(key, None)


class RedisRateLimiter:
    """Rate limiter backed by Upstash Redis (via redis-py)."""

    def __init__(self, limit: int, redis_url: str):
        import redis  # imported lazily so the app boots without it

        self.limit = limit
        self._r = redis.Redis.from_url(redis_url, socket_timeout=3, decode_responses=True)
        self._available = True

    def _pipeline_works(self) -> bool:
        try:
            self._r.ping()
            return True
        except Exception:
            return False

    def hit(self, key: str) -> tuple[bool, int]:
        if not self._available or not self._pipeline_works():
            self._available = False
            return True, -1
        try:
            pipe = self._r.pipeline()
            pipe.incr(key)
            pipe.expire(key, _REDIS_EXPIRE_SECONDS)
            count, _ = pipe.execute()
            count = int(count)
            return count <= self.limit, max(0, self.limit - count)
        except Exception:
            return True, -1

    def remaining(self, key: str) -> int:
        try:
            val = self._r.get(key)
            return max(0, self.limit - int(val)) if val else self.limit
        except Exception:
            return self.limit

    def reset(self, key: str) -> None:
        try:
            self._r.delete(key)
        except Exception:
            pass


def _hash_ip(ip: str) -> str:
    """Hash the IP so raw addresses are not retained in storage."""
    return hashlib.sha256(f"ats:{ip}".encode("utf-8")).hexdigest()[:24]


class RateLimiter:
    """Unified facade. Fails open on infra errors so users are never blocked
    by a broken Redis connection."""

    def __init__(self, prefix: str = "scan", limit: int | None = None) -> None:
        settings = get_settings()
        self.limit = limit if limit is not None else settings.rate_limit_per_day
        self.prefix = prefix
        self._backend: object
        if settings.redis_url:
            self._backend = RedisRateLimiter(self.limit, settings.redis_url)
            self.kind = "redis"
        else:
            self._backend = MemoryRateLimiter(self.limit, _REDIS_EXPIRE_SECONDS)
            self.kind = "memory"

    def key_for(self, ip: str) -> str:
        import datetime as dt

        day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
        return f"{self.prefix}:{_hash_ip(ip)}:{day}"

    def check(self, ip: str) -> tuple[bool, int]:
        """Returns (allowed, remaining). Never raises."""
        try:
            return self._backend.hit(self.key_for(ip))  # type: ignore[attr-defined]
        except Exception:
            return True, -1

    def remaining(self, ip: str) -> int:
        try:
            return self._backend.remaining(self.key_for(ip))  # type: ignore[attr-defined]
        except Exception:
            return -1

    def reset(self, ip: str) -> None:
        try:
            self._backend.reset(self.key_for(ip))  # type: ignore[attr-defined]
        except Exception:
            pass


_rate_limiter: Optional[RateLimiter] = None
_ai_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(prefix="scan")
    return _rate_limiter


def get_ai_rate_limiter() -> RateLimiter:
    global _ai_limiter
    if _ai_limiter is None:
        # AI calls are the expensive ones; give them their own generous quota.
        settings = get_settings()
        _ai_limiter = RateLimiter(prefix="ai", limit=settings.rate_limit_per_day * 4)
    return _ai_limiter
