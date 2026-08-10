"""AI rewrite and cover letter endpoints (JSON in/out; no file upload)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from ..deps import enforce_ai_rate_limit
from ...models.schemas import (
    APIError,
    CoverLetterRequest,
    CoverLetterResponse,
    RewriteRequest,
    RewriteResponse,
)
from ...services.ai.client import AIUnavailableError
from ...services.ai.cover_letter import generate_cover_letter
from ...services.ai.rewrite import rewrite_bullets

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai"])


@router.post(
    "/rewrite",
    response_model=RewriteResponse,
    responses={503: {"model": APIError}, 429: {"model": APIError}},
)
async def rewrite(req: RewriteRequest, request: Request) -> RewriteResponse:
    await enforce_ai_rate_limit(request)
    try:
        result = rewrite_bullets(req)
        return result
    except AIUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post(
    "/cover-letter",
    response_model=CoverLetterResponse,
    responses={503: {"model": APIError}, 429: {"model": APIError}},
)
async def cover_letter(req: CoverLetterRequest, request: Request) -> CoverLetterResponse:
    await enforce_ai_rate_limit(request)
    try:
        return generate_cover_letter(req)
    except AIUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
