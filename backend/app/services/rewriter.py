"""AI Rewriter Service — TokenRouter (Kimi K3) primary + Ollama fallback.

A self-contained rewriter built on the OpenAI SDK:

- PRIMARY:  TokenRouter, model ``moonshotai/kimi-k3-free`` (OpenAI-compatible).
- FALLBACK: local Ollama, model ``qwen2.5-coder:7b`` (no key required).

Config is read through ``get_settings()`` (environment variables or ``.env``),
never hardcoded. If the primary call fails (timeout, rate limit, 4xx/5xx) or no
API key is configured, the request is retried against Ollama. If both fail a
clear, user-facing error is raised.

After generation, the same deterministic guard layer used by the rest of the
app runs locally: numbers/metrics must be preserved byte-for-byte and no skill
absent from the resume may be introduced.
"""

from __future__ import annotations

import logging
import threading

from .ai.client import AIUnavailableError
from .ai.prompts import REWRITE_SYSTEM, REWRITE_USER
from .ai.rewrite import (
    RULES_APPLIED,
    _NUM_TOKEN,
    _detect_invented_tools,
    _numbers_preserved,
    _parse_json,
    _strip_terms,
)
from ..core.config import get_settings
from ..models.schemas import RewriteResponse, RewrittenBullet

logger = logging.getLogger(__name__)

_PRIMARY_TIMEOUT_S = 20
_FALLBACK_TIMEOUT_S = 30


class AIRewriter:
    """Rewrite resume bullets against a JD using TokenRouter then Ollama."""

    def __init__(
        self,
        primary_client=None,
        fallback_client=None,
        primary_model: str | None = None,
        fallback_model: str | None = None,
    ) -> None:
        """Create the two OpenAI-compatible clients (models load at init).

        ``primary_client`` / ``fallback_client`` are injectable for tests;
        when omitted they are built from configuration.
        """
        from openai import OpenAI

        self.settings = get_settings()

        self.primary_model = primary_model or self.settings.tokenrouter_model
        self.fallback_model = fallback_model or self.settings.ollama_model

        if primary_client is not None:
            self.primary_client = primary_client
        elif self.settings.tokenrouter_api_key:
            self.primary_client = OpenAI(
                api_key=self.settings.tokenrouter_api_key,
                base_url=self.settings.tokenrouter_base_url,
                timeout=_PRIMARY_TIMEOUT_S,
                max_retries=1,
            )
        else:
            self.primary_client = None

        if fallback_client is not None:
            self.fallback_client = fallback_client
        else:
            self.fallback_client = OpenAI(
                api_key="ollama",  # Ollama ignores the key but the SDK requires one
                base_url=self.settings.ollama_base_url,
                timeout=_FALLBACK_TIMEOUT_S,
                max_retries=0,
            )

    @property
    def primary_configured(self) -> bool:
        return self.primary_client is not None

    # ------------------------------------------------------------------ #
    # Low-level chat: primary -> fallback
    # ------------------------------------------------------------------ #
    def chat(self, messages: list[dict], temperature: float = 0.4) -> tuple[str, str]:
        """Return (response_text, model_used). Raises AIUnavailableError."""
        last_err: Exception | None = None

        if self.primary_client is not None:
            try:
                resp = self.primary_client.chat.completions.create(
                    model=self.primary_model,
                    messages=messages,
                    temperature=temperature,
                )
                text = (resp.choices[0].message.content or "").strip()
                if text:
                    return text, self.primary_model
                raise RuntimeError("empty completion")
            except Exception as exc:  # rate limit, timeout, 4xx/5xx
                last_err = exc
                logger.warning("TokenRouter failed (%s); falling back to Ollama", exc)

        try:
            resp = self.fallback_client.chat.completions.create(
                model=self.fallback_model,
                messages=messages,
                temperature=temperature,
            )
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text, self.fallback_model
            raise RuntimeError("empty completion")
        except Exception as exc:
            last_err = exc
            logger.warning("Ollama fallback failed: %s", exc)

        detail = f" Last error: {last_err}" if last_err else ""
        raise AIUnavailableError(
            "AI rewriting is temporarily unavailable. No API key is configured "
            "and the local Ollama service is not reachable. Please try again "
            "later." + detail
        )

    # ------------------------------------------------------------------ #
    # High-level rewrite with the deterministic guard layer
    # ------------------------------------------------------------------ #
    def rewrite(
        self,
        jd: str,
        bullets: list[str],
        context: str = "",
        temperature: float = 0.3,
    ) -> RewriteResponse:
        """Rewrite bullets for ATS alignment; numbers and facts are guarded."""
        facts = context.strip() or (
            "The candidate's full resume text was not provided for this rewrite; "
            "only rephrase the given bullets without adding any new facts."
        )
        user_payload = REWRITE_USER.format(
            jd=jd,
            context=facts,
            bullets="\n".join(f"- {b}" for b in bullets),
        )
        raw, model = self.chat(
            [
                {"role": "system", "content": REWRITE_SYSTEM},
                {"role": "user", "content": user_payload},
            ],
            temperature=temperature,
        )

        parsed = _parse_json(raw)
        items = parsed.get("bullets") if isinstance(parsed, dict) else None
        if not isinstance(items, list):
            raise AIUnavailableError(
                "The model returned an unparseable response. Please try again."
            )

        result: list[RewrittenBullet] = []
        for item in items:
            original = str(item.get("original", "")).strip()
            rewritten = str(item.get("rewritten", "")).strip()
            if not original or not rewritten:
                continue
            # Guard: numbers must be preserved.
            if not _numbers_preserved(original, rewritten):
                rewritten = original
                changed: list[str] = []
                reason = "Rewrite was rejected: it altered a number/metric."
            else:
                changed = [c for c in item.get("changed", []) if str(c).strip()]
                reason = str(item.get("reason", "")).strip()
                if context.strip():  # only guard against invention when facts exist
                    invented = _detect_invented_tools(rewritten, facts)
                    if invented:
                        cleaned = _strip_terms(rewritten, invented)
                        if cleaned and cleaned != rewritten:
                            rewritten = cleaned
                            changed.append(
                                "removed unsupported term(s): " + ", ".join(invented)
                            )
            result.append(
                RewrittenBullet(
                    original=original,
                    rewritten=rewritten,
                    changed=changed,
                    preserved=sorted(set(_NUM_TOKEN.findall(original))),
                    reason=reason,
                )
            )

        if not result:
            raise AIUnavailableError("No valid bullets were produced. Please try again.")

        return RewriteResponse(
            rewritten=result, rules_applied=RULES_APPLIED, model_used=model
        )


# ---------------------------------------------------------------------- #
# Shared instance: construct once, reuse across requests.
# ---------------------------------------------------------------------- #
_rewriter: AIRewriter | None = None
_rewriter_lock = threading.Lock()


def get_rewriter() -> AIRewriter:
    """Return the process-wide AIRewriter (clients build at most once)."""
    global _rewriter
    if _rewriter is None:
        with _rewriter_lock:
            if _rewriter is None:
                _rewriter = AIRewriter()
    return _rewriter


def reset_rewriter() -> None:
    global _rewriter
    _rewriter = None
