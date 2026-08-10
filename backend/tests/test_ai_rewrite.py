"""Tests for AI rewrite with a mocked provider.

These verify the deterministic guard layer (number preservation, JSON parsing,
rule enforcement) without needing a live LLM.
"""

import pytest

from app.models.schemas import RewriteRequest
from app.services.ai.rewrite import rewrite_bullets, _numbers_preserved, _parse_json
from app.services.ai.client import AIUnavailableError


class _FakeClient:
    def __init__(self, content: str):
        self._content = content

    def chat(self, messages, temperature=0.4, max_output_tokens=None):
        return self._content, "mock-model"


GOOD_JSON = """{"bullets": [{
  "original": "Built REST APIs with Python.",
  "rewritten": "Designed and built REST APIs using Python.",
  "changed": ["added strong verb 'designed'"],
  "reason": "Adds an action verb favored by recruiters."
}]}"""


def _req():
    return RewriteRequest(
        bullets=["Built REST APIs with Python."],
        jd="Senior Software Engineer needing Python and REST APIs.",
        context="Built REST APIs with Python.",
    )


def test_rewrite_happy_path(monkeypatch):
    monkeypatch.setattr(
        "app.services.ai.rewrite.get_ai_client", lambda: _FakeClient(GOOD_JSON)
    )
    resp = rewrite_bullets(_req())
    assert resp.rewritten[0].rewritten == "Designed and built REST APIs using Python."
    assert resp.rewritten[0].changed == ["added strong verb 'designed'"]
    assert resp.rules_applied
    assert resp.model_used == "mock-model"


def test_rewrite_rejects_altered_numbers(monkeypatch):
    bad = """{"bullets": [{
      "original": "Cut processing time by 40%.",
      "rewritten": "Cut processing time by 60%.",
      "changed": ["increased metric"],
      "reason": "x"
    }]}"""
    monkeypatch.setattr(
        "app.services.ai.rewrite.get_ai_client", lambda: _FakeClient(bad)
    )
    resp = rewrite_bullets(
        RewriteRequest(bullets=["Cut processing time by 40%."], jd="x" * 20, context="")
    )
    # Guard must fall back to the original bullet.
    assert resp.rewritten[0].rewritten == "Cut processing time by 40%."
    assert resp.rewritten[0].changed == []


def test_rewrite_unparseable_json_raises(monkeypatch):
    monkeypatch.setattr(
        "app.services.ai.rewrite.get_ai_client", lambda: _FakeClient("not json at all")
    )
    with pytest.raises(AIUnavailableError):
        rewrite_bullets(_req())


def test_numbers_preserved():
    assert _numbers_preserved("Cut time by 40% and saved $12k", "Cut time by 40% and saved $12k in Q3")
    assert not _numbers_preserved("Cut time by 40%", "Cut time by 50%")


def test_parse_json_with_markdown_fence():
    raw = '```json\n{"a": 1}\n```'
    assert _parse_json(raw) == {"a": 1}
