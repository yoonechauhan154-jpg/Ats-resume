"""Application configuration.

All secrets are read from environment variables at runtime (or from a `.env`
file in the project root, loaded via pydantic-settings/python-dotenv). Never
hardcode keys.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Runtime settings. Values come from environment variables, falling back
    to `.env` (loaded automatically by pydantic-settings via python-dotenv).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Don't let pydantic-settings auto-decode list fields as JSON at the
        # boundary; we handle JSON/CSV/list in the `mode="before"` validator
        # below. Without this, a non-JSON env value like
        # "https://a.com, https://b.com" raises SettingsError before the
        # validator ever sees it.
        enable_decoding=False,
    )

    # --- AI integration ---
    # PRIMARY: TokenRouter (OpenAI-compatible)
    tokenrouter_api_key: str = ""
    tokenrouter_base_url: str = "https://api.tokenrouter.com/v1"
    tokenrouter_model: str = "moonshotai/kimi-k3-free"

    # FALLBACK: Ollama (local, no key required)
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5-coder:7b"

    # --- Rate limiting ---
    # Optional Upstash Redis URL. Falls back to in-memory when unset.
    redis_url: str = ""
    rate_limit_per_day: int = 5

    # Optional Upstash REST credentials (upstash-redis AsyncRedis). When both
    # are set, the async rate limiter in utils/rate_limiter.py uses them.
    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""

    # --- Anonymous analytics (never contains resume content) ---
    supabase_url: str = ""
    supabase_service_key: str = ""

    # --- Files ---
    max_upload_mb: int = 5
    temp_dir: str = "/tmp/ats_optimizer"
    delete_after_scan: bool = True

    # --- Request handling ---
    # Hard cap on total request processing time (seconds).
    request_timeout_seconds: int = 60

    # --- CORS ---
    cors_origins: list[str] = [
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.monkeycode-ai.live",
    ]

    # --- Uploaded file extensions we accept ---
    allowed_extensions: list[str] = [".pdf", ".docx"]

    @field_validator("cors_origins", "allowed_extensions", mode="before")
    @classmethod
    def _split_csv_or_json(cls, value):
        """Accept three formats from env (HF Spaces Secrets, .env, shell):
        1) JSON list string: '["https://a.com","https://b.com"]'
        2) Comma-separated:  'https://a.com, https://b.com'
        3) A real Python list (default used when env unset)
        Falls back silently to input if it's already a list.
        """
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return []
            # Try JSON first — this lets HF Spaces Secrets users paste a
            # complete ["origin1","origin2"] string.
            if s.startswith("["):
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        return [str(o).strip() for o in parsed if str(o).strip()]
                except json.JSONDecodeError:
                    logger.warning("cors_origins: invalid JSON list; falling back to CSV split")
            # CSV fallback
            return [o.strip() for o in s.split(",") if o.strip()]
        return value

    @property
    def ai_configured(self) -> bool:
        return bool(self.tokenrouter_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
