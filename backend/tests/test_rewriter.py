"""Tests for AIRewriter (TokenRouter primary + Ollama fallback).

No live LLM calls: the two OpenAI-compatible clients are injected as fakes so
the primary->fallback routing and the deterministic guard layer can be tested.
"""

import pytest

from app.models.schemas import RewriteResponse
from app.services.rewriter import AIRewriter, get_rewriter, reset_rewriter
from app.services.ai.client import AIUnavailableError


class _Resp:
    def __init__(self, content: str):
        self.choices = [_Choice(content)]


class _Choice:
    def __init__(self, content: str):
        self.message = _Msg(content)


class _Msg:
    def __init__(self, content: str):
        self.content = content


class _Completions:
    """Replays a scripted list of results/exceptions per create() call."""

    def __init__(self, script=None):
        self.script = list(script or [])
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        if self.calls > len(self.script):
            raise RuntimeError("no more scripted responses")
        item = self.script[self.calls - 1]
        if isinstance(item, Exception):
            raise item
        return _Resp(item)


class _FakeChat:
    def __init__(self, script=None):
        self.completions = _Completions(script)


class _FakeOpenAI:
    def __init__(self, script=None):
        self.chat = _FakeChat(script)


GOOD_JSON = """{"bullets": [{
  "original": "Built REST APIs with Python.",
  "rewritten": "Designed and built REST APIs using Python.",
  "changed": ["added strong verb 'designed'"],
  "reason": "Adds an action verb favored by recruiters."
}]}"""


def test_constructor_defaults_match_spec():
    # Inject both models explicitly so this is independent of the developer's
    # local backend/.env (OLLAMA_MODEL / TOKENROUTER_MODEL may differ from the
    # code defaults; pydantic-settings' .env source beats the code default).
    r = AIRewriter(
        primary_client=_FakeOpenAI(),
        fallback_client=_FakeOpenAI(),
        primary_model="moonshotai/kimi-k3-free",
        fallback_model="qwen2.5-coder:7b",
    )
    assert r.primary_model == "moonshotai/kimi-k3-free"
    assert r.fallback_model == "qwen2.5-coder:7b"
    assert r.primary_configured


def test_chat_uses_primary_when_healthy():
    primary = _FakeOpenAI([GOOD_JSON])
    fallback = _FakeOpenAI([])
    r = AIRewriter(primary_client=primary, fallback_client=fallback)
    text, model = r.chat([{"role": "user", "content": "hi"}])
    assert text == GOOD_JSON
    assert model == r.primary_model
    assert fallback.chat.completions.calls == 0


def test_chat_falls_back_to_ollama_on_primary_failure():
    primary = _FakeOpenAI([RuntimeError("rate limited")])
    fallback = _FakeOpenAI(["fallback reply"])
    r = AIRewriter(primary_client=primary, fallback_client=fallback)
    text, model = r.chat([{"role": "user", "content": "hi"}])
    assert text == "fallback reply"
    assert model == r.fallback_model
    assert primary.chat.completions.calls == 1


def test_chat_raises_when_both_fail():
    primary = _FakeOpenAI([RuntimeError("boom")])
    fallback = _FakeOpenAI([RuntimeError("offline")])
    r = AIRewriter(primary_client=primary, fallback_client=fallback)
    with pytest.raises(AIUnavailableError):
        r.chat([{"role": "user", "content": "hi"}])


def test_rewrite_happy_path(monkeypatch):
    r = AIRewriter(primary_client=_FakeOpenAI([GOOD_JSON]), fallback_client=_FakeOpenAI())
    resp = r.rewrite(jd="Need Python and REST APIs.", bullets=["Built REST APIs with Python."])
    assert isinstance(resp, RewriteResponse)
    assert resp.rewritten[0].rewritten == "Designed and built REST APIs using Python."
    assert resp.rewritten[0].changed == ["added strong verb 'designed'"]
    assert resp.rules_applied
    assert resp.model_used == r.primary_model


def test_rewrite_rejects_altered_numbers():
    bad = """{"bullets": [{
      "original": "Cut processing time by 40%.",
      "rewritten": "Cut processing time by 60%.",
      "changed": ["increased metric"],
      "reason": "x"
    }]}"""
    r = AIRewriter(primary_client=_FakeOpenAI([bad]), fallback_client=_FakeOpenAI())
    resp = r.rewrite(jd="Need performance.", bullets=["Cut processing time by 40%."])
    assert resp.rewritten[0].rewritten == "Cut processing time by 40%."
    assert resp.rewritten[0].changed == []
    assert resp.rewritten[0].preserved == ["40%"]


def test_rewrite_unparseable_raises():
    r = AIRewriter(primary_client=_FakeOpenAI(["not json at all"]), fallback_client=_FakeOpenAI())
    with pytest.raises(AIUnavailableError):
        r.rewrite(jd="x" * 20, bullets=["Built APIs."])


def test_rewrite_falls_back_when_primary_fails():
    primary = _FakeOpenAI([RuntimeError("rate limited")])
    fallback = _FakeOpenAI([GOOD_JSON])
    r = AIRewriter(primary_client=primary, fallback_client=fallback)
    resp = r.rewrite(jd="Need Python.", bullets=["Built REST APIs with Python."])
    assert resp.model_used == r.fallback_model
    assert resp.rewritten[0].rewritten == "Designed and built REST APIs using Python."


def test_get_rewriter_is_singleton(monkeypatch):
    monkeypatch.setattr("app.services.rewriter._rewriter", None)
    assert get_rewriter() is get_rewriter()
    reset_rewriter()
