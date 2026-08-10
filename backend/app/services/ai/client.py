"""AI client abstraction.

PRIMARY:  TokenRouter (OpenAI-compatible), key from TOKENROUTER_API_KEY.
FALLBACK: Ollama (local), optional. Disabled entirely when
          OLLAMA_BASE_URL is empty (recommended for hosted deploys).

Both use the `openai` Python SDK with a custom base_url, so the code stays
identical regardless of provider. If neither is reachable we raise a clear,
user-facing error.
"""

from __future__ import annotations

import logging
import time

from ...core.config import get_settings

logger = logging.getLogger(__name__)

# The primary model (moonshotai/kimi-k3-free) is a PURE reasoning model and is
# the ONLY model this TokenRouter token can access (catalog = 1 model; every
# other model returns 403). It always generates a long reasoning chain before
# any visible output, so a rewrite/cover-letter call routinely spends 60-120s
# in-flight. IMPORTANT: httpx surfaces a socket/read timeout as
# openai.APIConnectionError("Connection error") — the SAME message as a real
# connection failure — which is why the original 503s looked like a network
# problem. Do NOT cap this below the request-level budget (REQUEST_TIMEOUT),
# and do NOT retry (a retry doubles the latency and guarantees the outer
# asyncio.wait_for cancels first). The outer request_timeout middleware is the
# real ceiling.
_PRIMARY_TIMEOUT_S = 145
_PRIMARY_MAX_RETRIES = 0
# Ollama cloud reasoning models (e.g. nemotron-3-super) can be slow on long
# prompts. Give them 90s so /cover-letter can finish without 503.
_FALLBACK_TIMEOUT_S = 90


class AIUnavailableError(RuntimeError):
    """Raised when neither provider can be reached."""


class AIClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._primary = None
        self._fallback = None
        self._init_clients()

    def _init_clients(self) -> None:
        try:
            from openai import OpenAI

            if self._settings.tokenrouter_api_key:
                self._primary = OpenAI(
                    api_key=self._settings.tokenrouter_api_key,
                    base_url=self._settings.tokenrouter_base_url,
                    timeout=_PRIMARY_TIMEOUT_S,
                    max_retries=_PRIMARY_MAX_RETRIES,
                )

            # Skip the fallback entirely when OLLAMA_BASE_URL is empty. On
            # Hugging Face Spaces / Railway / any hosted runtime, localhost
            # Ollama is unreachable — leaving it empty makes the failure mode
            # obvious instead of burning the 90s fallback timeout per request.
            ollama_url = (self._settings.ollama_base_url or "").strip()
            if ollama_url:
                self._fallback = OpenAI(
                    api_key="ollama",  # Ollama ignores the key but SDK requires it
                    base_url=ollama_url,
                    timeout=_FALLBACK_TIMEOUT_S,
                    max_retries=0,
                )
            else:
                logger.info(
                    "OLLAMA_BASE_URL empty — fallback provider disabled; "
                    "TokenRouter is the only AI path"
                )
        except ImportError as exc:  # pragma: no cover
            raise AIUnavailableError(
                "The 'openai' package is not installed in this environment."
            ) from exc

    @property
    def primary_configured(self) -> bool:
        return self._primary is not None

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.4,
        max_output_tokens: int | None = None,
    ) -> tuple[str, str]:
        """Returns (response_text, model_used). Raises AIUnavailableError."""
        last_err: Exception | None = None
        extra: dict = {}
        if max_output_tokens is not None:
            extra["max_completion_tokens"] = max_output_tokens

        # Primary: TokenRouter
        if self._primary is not None:
            try:
                t0 = time.time()
                resp = self._primary.chat.completions.create(
                    model=self._settings.tokenrouter_model,
                    messages=messages,
                    temperature=temperature,
                    **extra,
                )
                text = (resp.choices[0].message.content or "").strip()
                if text:
                    logger.info("TokenRouter reply in %.1fs", time.time() - t0)
                    return text, self._settings.tokenrouter_model
                raise RuntimeError("empty completion")
            except Exception as exc:  # rate limit, timeout, 4xx/5xx
                last_err = exc
                logger.warning(
                    "TokenRouter failed (%s); attempting Ollama fallback", exc
                )

        # Fallback: Ollama (only if configured)
        if self._fallback is not None:
            try:
                t0 = time.time()
                resp = self._fallback.chat.completions.create(
                    model=self._settings.ollama_model,
                    messages=messages,
                    temperature=temperature,
                    **extra,
                )
                text = (resp.choices[0].message.content or "").strip()
                if text:
                    logger.info("Ollama reply in %.1fs", time.time() - t0)
                    return text, self._settings.ollama_model
                raise RuntimeError("empty completion")
            except Exception as exc:
                last_err = exc
                logger.warning("Ollama fallback failed: %s", exc)

        detail = f"Last error: {last_err}" if last_err else ""
        tr_state = "failed" if last_err else "not configured"
        ol_state = "disabled" if self._fallback is None else "unreachable"
        raise AIUnavailableError(
            f"AI generation is temporarily unavailable (TokenRouter {tr_state}; "
            f"Ollama {ol_state}). Contact the site administrator. {detail}"
        )


_client: AIClient | None = None


def get_ai_client() -> AIClient:
    global _client
    if _client is None:
        _client = AIClient()
    return _client


def reset_client() -> None:
    global _client
    _client = None
