"""FastAPI application entrypoint.

Run locally:  uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import ai as ai_routes
from .api.routes import analyze as analyze_routes
from .core.config import get_settings
from .models.schemas import HealthResponse
from .services.ai.client import get_ai_client
from .services.matcher import get_matcher
from .services.rate_limit import get_rate_limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load heavy NLP models once at startup, never per request."""
    logger.info("warming up NLP models (spaCy + sentence-transformers)...")
    try:
        matcher = get_matcher()
        logger.info(
            "NLP models ready (spaCy=%s, embedder=%s)",
            matcher.nlp is not None,
            matcher.embedder is not None,
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("NLP model warmup failed (%s); will load lazily", exc)
    yield


app = FastAPI(
    title="Resume ATS Optimizer API",
    version="1.0.0",
    description=(
        "Free, privacy-first ATS resume scanner + AI rewrite + cover letter. "
        "No signup. Resume files are deleted immediately after processing."
    ),
    lifespan=lifespan,
)


def _exact_origins(origins: list[str]) -> list[str]:
    """Origins without a wildcard are matched exactly by Starlette."""
    return [o for o in origins if "*" not in o]


def _origin_regex(origins: list[str]) -> str | None:
    """Convert `https://*.example.com` entries into an allow_origin_regex.

    Starlette matches ``allow_origins`` by exact string only; subdomain
    wildcards must go through ``allow_origin_regex``.
    """
    patterns = []
    for o in origins:
        if "*" in o:
            patterns.append("^" + o.replace(".", r"\.").replace("*", ".*") + "$")
    return "|".join(patterns) if patterns else None


app.add_middleware(
    CORSMiddleware,
    allow_origins=_exact_origins(settings.cors_origins),
    allow_origin_regex=_origin_regex(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.middleware("http")
async def request_timeout(request: Request, call_next):
    """Enforce a hard cap on total request processing time."""
    timeout = get_settings().request_timeout_seconds
    try:
        return await asyncio.wait_for(call_next(request), timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning("request timed out after %ss on %s %s", timeout, request.method, request.url.path)
        return JSONResponse(
            status_code=504,
            content={
                "error": "timeout",
                "detail": f"Request took longer than {timeout} seconds and was cancelled.",
            },
        )


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    return resp


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": "An unexpected error occurred."},
    )


@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    limiter = get_rate_limiter()
    ai_primary = False
    ai_fallback = False
    try:
        ai = get_ai_client()
        ai_primary = ai.primary_configured
        ai_fallback = True  # Ollama client always constructed; reachability probed on use
    except Exception:
        pass
    return HealthResponse(
        status="ok",
        ai_primary=ai_primary,
        ai_fallback=ai_fallback,
        rate_limiter=limiter.kind,  # type: ignore[attr-defined]
    )


app.include_router(analyze_routes.router)
app.include_router(ai_routes.router)
