"""Async rate limiter backed by Upstash Redis (with an in-memory fallback).

Implements the contract required by the API:

    check_rate_limit(ip_address, limit=5) -> bool
        Returns True when the caller is rate limited (blocked),
        False when the request is allowed.

Per-day windowing: the Redis key embeds the UTC date so the quota resets at
midnight automatically. The counter is incremented atomically and its TTL is
set to the end of the day (max 86400 seconds).

Privacy note: only the IP address + date are stored as the key — never the
request payload or resume content. The in-memory fallback keeps the same
key format so behavior is identical without Redis.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from ..core.config import get_settings

logger = logging.getLogger(__name__)

_MAX_TTL_SECONDS = 60 * 60 * 24  # 86400: end-of-day cap

_redis = None  # AsyncRedis instance or False once probed


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _seconds_until_end_of_day() -> int:
    now = datetime.now(timezone.utc)
    end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return min(_MAX_TTL_SECONDS, max(1, int((end - now).total_seconds()) + 1))


def _get_redis():
    """Return the shared AsyncRedis client or None (lazy, once)."""
    global _redis
    if _redis is None:
        settings = get_settings()
        if settings.upstash_redis_rest_url and settings.upstash_redis_rest_token:
            try:
                from upstash_redis import AsyncRedis

                _redis = AsyncRedis(
                    url=settings.upstash_redis_rest_url,
                    token=settings.upstash_redis_rest_token,
                    rest_retries=1,
                    allow_telemetry=False,
                )
            except Exception as exc:  # pragma: no cover
                logger.warning("failed to init upstash client (%s); using memory", exc)
                _redis = False
        else:
            _redis = False
    return _redis or None


# --- in-memory fallback (per-day keys; old dates never match again) -------- #
_memory: dict[str, tuple[int, str]] = {}


def _memory_record(key: str, day: str) -> int:
    """Increment the in-memory counter for key; returns the new count."""
    entry = _memory.get(key)
    if entry is None or entry[1] != day:
        _memory[key] = (1, day)
        return 1
    _memory[key] = (entry[0] + 1, day)
    if len(_memory) > 4096:  # light cleanup of stale day keys
        for k, (_, d) in list(_memory.items()):
            if d != day:
                del _memory[k]
    return _memory[key][0]


async def check_rate_limit(ip_address: str, limit: int = 5) -> bool:
    """Return True if rate limited (blocked), False if allowed.

    Uses Redis key ``f"ratelimit:{ip_address}:{today's_date}"``, increments the
    counter, and sets the key to expire at the end of the day.
    """
    day = _today()
    key = f"ratelimit:{ip_address}:{day}"

    client = _get_redis()
    if client is not None:
        try:
            count = await client.incr(key)
            await client.expire(key, _seconds_until_end_of_day())
            return int(count) > limit
        except Exception as exc:
            # Fail open: a broken Redis must never block legitimate users.
            logger.warning("rate limiter redis error (%s); failing open", exc)
            return False

    return _memory_record(key, day) > limit


async def remaining(ip_address: str, limit: int = 5) -> int:
    """Return how many more requests are allowed today (for headers)."""
    day = _today()
    key = f"ratelimit:{ip_address}:{day}"

    client = _get_redis()
    if client is not None:
        try:
            val = await client.get(key)
            count = int(val) if val is not None else 0
            return max(0, limit - count)
        except Exception:
            return -1

    entry = _memory.get(key)
    if entry is None or entry[1] != day:
        return limit
    return max(0, limit - entry[0])


async def reset(ip_address: str) -> None:
    """Clear today's quota for an IP (used by tests and admin tooling)."""
    day = _today()
    key = f"ratelimit:{ip_address}:{day}"

    client = _get_redis()
    if client is not None:
        try:
            await client.delete(key)
            return
        except Exception:
            pass

    _memory.pop(key, None)
