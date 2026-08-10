"""Shared API dependencies."""

from __future__ import annotations

from fastapi import HTTPException, Request

from ..core.config import get_settings
from ..utils.rate_limiter import check_rate_limit, remaining


def client_ip(request: Request) -> str:
    """Best-effort real client IP behind common proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def enforce_rate_limit(request: Request) -> None:
    ip = client_ip(request)
    blocked = await check_rate_limit(ip, limit=get_settings().rate_limit_per_day)
    if blocked:
        raise HTTPException(
            status_code=429,
            detail=(
                "You've reached the free limit of 5 scans per day for this IP. "
                "Come back tomorrow, or ask the site owner to raise the quota."
            ),
        )


async def enforce_ai_rate_limit(request: Request) -> None:
    ip = client_ip(request)
    settings = get_settings()
    # AI calls are the expensive ones; give them their own generous quota.
    blocked = await check_rate_limit(ip, limit=settings.rate_limit_per_day * 4)
    if blocked:
        raise HTTPException(
            status_code=429,
            detail=(
                "You've used today's free AI-generation allowance for this IP. "
                "Please try again tomorrow."
            ),
        )


async def rate_limit_headers(request: Request) -> dict[str, str]:
    ip = client_ip(request)
    settings = get_settings()
    limit = settings.rate_limit_per_day
    left = await remaining(ip, limit=limit)
    return {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(left),
    }
