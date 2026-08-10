"""End-to-end API tests (analyze endpoint, health, security, rate limiting)."""

import asyncio
import io

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.rate_limit import get_rate_limiter
from app.utils import rate_limiter as rl

client = TestClient(app)


@pytest.fixture(autouse=True)
def _fresh_quota():
    """Each test starts with a full daily quota for the test client IP."""
    asyncio.run(rl.reset("testclient"))
    yield

JD = """
Senior Software Engineer
We need a Senior Software Engineer for our Platform team.
- Design and build REST APIs and microservices in Python and Node.js
- Work with PostgreSQL and Redis
- Deploy on AWS with Docker and Kubernetes
- Implement CI/CD pipelines and unit testing
- Bachelor's degree in Computer Science
"""


def _make_pdf_bytes() -> bytes:
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "John Smith - Senior Software Engineer", fontsize=12, fontname="helv")
    page.insert_text((72, 100), "Built REST APIs with Python, PostgreSQL, Redis, AWS, Docker.", fontsize=11, fontname="helv")
    data = doc.tobytes()
    doc.close()
    return data


def _post_analyze(file_bytes: bytes, filename: str, jd: str = JD):
    files = {"file": (filename, io.BytesIO(file_bytes), "application/octet-stream")}
    return client.post("/analyze", files=files, data={"jd": jd})


# --------------------------------------------------------------------------- #
# Required test cases
# --------------------------------------------------------------------------- #
def test_health_returns_200():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_analyze_valid_pdf_with_jd():
    resp = _post_analyze(_make_pdf_bytes(), "resume.pdf")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["score"]["overall"] >= 0
    assert "keyword_match" in {c["name"] for c in body["score"]["components"]}
    assert resp.headers.get("X-RateLimit-Limit")


def test_analyze_rejects_bad_extension():
    resp = _post_analyze(b"MZ...not a real binary", "evil.exe")
    assert resp.status_code == 400


def test_analyze_rejects_renamed_fake_pdf():
    # A .txt file renamed to .pdf must be caught by magic-byte validation.
    fake = b"Hello, this is plain text pretending to be a PDF." * 20
    resp = _post_analyze(fake, "resume.pdf")
    assert resp.status_code == 400
    assert "magic bytes" in resp.json()["detail"].lower() or "does not look like" in resp.json()["detail"].lower()


def test_analyze_rejects_renamed_fake_docx():
    fake = b"This is text, not a real ZIP/DOCX container." * 20
    resp = _post_analyze(fake, "resume.docx")
    assert resp.status_code == 400


def test_analyze_rejects_oversized_file():
    # Valid PDF header (passes magic check) but padded to >5MB -> 413.
    big = _make_pdf_bytes() + b"\x00" * (6 * 1024 * 1024)
    resp = _post_analyze(big, "resume.pdf")
    assert resp.status_code == 413
    assert "limit" in resp.json()["detail"].lower()


def test_analyze_rejects_oversized_jd():
    resp = _post_analyze(_make_pdf_bytes(), "resume.pdf", jd="x" * 10_001)
    assert resp.status_code == 400
    assert "10,000" in resp.json()["detail"]


def test_analyze_rejects_short_jd():
    resp = _post_analyze(_make_pdf_bytes(), "resume.pdf", jd="too short")
    assert resp.status_code == 400


def test_rate_limit_blocks_sixth_request():
    asyncio.run(rl.reset("testclient"))
    pdf = _make_pdf_bytes()
    statuses = [_post_analyze(pdf, "resume.pdf").status_code for _ in range(6)]
    assert statuses[:5] == [200] * 5
    assert statuses[5] == 429


def test_rewrite_503_when_ai_unavailable(monkeypatch):
    # With no TokenRouter key and no Ollama, the endpoint must return a clear 503.
    from app.services.ai import rewrite as rewrite_mod

    def boom(*a, **k):
        raise rewrite_mod.AIUnavailableError("AI generation is temporarily unavailable.")

    monkeypatch.setattr(rewrite_mod, "get_ai_client", boom)
    resp = client.post(
        "/rewrite",
        json={"bullets": ["Built features."], "jd": JD, "context": "Python developer."},
    )
    assert resp.status_code == 503
