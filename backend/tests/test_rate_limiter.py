"""Tests for the async rate limiter (utils/rate_limiter.py).

The Upstash Redis client is replaced with a fake for the Redis path; the
in-memory fallback is exercised directly.
"""

import asyncio

import pytest

from app.utils import rate_limiter as rl


@pytest.fixture(autouse=True)
def _clean_state():
    rl._memory.clear()
    rl._redis = None
    yield
    rl._memory.clear()
    rl._redis = None


def test_allowed_below_limit():
    assert asyncio.run(rl.check_rate_limit("203.0.113.1", limit=2)) is False
    assert asyncio.run(rl.check_rate_limit("203.0.113.1", limit=2)) is False


def test_blocked_at_limit():
    for _ in range(5):
        assert asyncio.run(rl.check_rate_limit("203.0.113.2")) is False
    # Sixth request in the same day is blocked.
    assert asyncio.run(rl.check_rate_limit("203.0.113.2")) is True


def test_key_embeds_date():
    day = rl._today()
    rl._memory[f"ratelimit:203.0.113.3:{day}"] = (5, day)
    assert asyncio.run(rl.check_rate_limit("203.0.113.3")) is True


def test_remaining_header_value():
    assert asyncio.run(rl.remaining("203.0.113.4", limit=5)) == 5
    asyncio.run(rl.check_rate_limit("203.0.113.4", limit=5))
    assert asyncio.run(rl.remaining("203.0.113.4", limit=5)) == 4


def test_reset_on_new_day():
    asyncio.run(rl.check_rate_limit("203.0.113.5", limit=1))
    assert asyncio.run(rl.check_rate_limit("203.0.113.5", limit=1)) is True
    # A new day must reset the counter even for the same IP.
    rl._memory = {}
    assert asyncio.run(rl.check_rate_limit("203.0.113.5", limit=1)) is False


class _FakeAsyncRedis:
    """Records calls and returns scripted results like AsyncRedis."""

    def __init__(self, incr_results, get_results=None):
        self._incr_results = list(incr_results)
        self._get_results = list(get_results or [])
        self.incr_keys = []
        self.expire_calls = []
        self.incr_calls = 0

    async def incr(self, key):
        self.incr_calls += 1
        self.incr_keys.append(key)
        return self._incr_results[self.incr_calls - 1]

    async def expire(self, key, seconds):
        self.expire_calls.append((key, seconds))
        return True

    async def get(self, key):
        return self._get_results.pop(0) if self._get_results else None


def test_uses_upstash_redis_path(monkeypatch):
    fake = _FakeAsyncRedis([1, 2, 3, 4, 5, 6])
    monkeypatch.setattr(rl, "_get_redis", lambda: fake)

    blocked = []
    for _ in range(6):
        blocked.append(asyncio.run(rl.check_rate_limit("198.51.100.7", limit=5)))
    assert blocked == [False, False, False, False, False, True]
    # Key uses the exact spec format and TTL is set every call.
    day = rl._today()
    for key in fake.incr_keys:
        assert key == f"ratelimit:198.51.100.7:{day}"
    assert fake.expire_calls and all(0 < s <= 86400 for _, s in fake.expire_calls)


def test_redis_failure_fails_open(monkeypatch):
    class _Boom:
        async def incr(self, key):
            raise ConnectionError("upstash down")

        async def expire(self, key, seconds):
            raise ConnectionError("upstash down")

    monkeypatch.setattr(rl, "_get_redis", lambda: _Boom())
    # Fail-open: a broken Redis never blocks the user.
    assert asyncio.run(rl.check_rate_limit("198.51.100.8", limit=5)) is False


def test_seconds_until_end_of_day_bounded():
    assert 0 < rl._seconds_until_end_of_day() <= 86400
