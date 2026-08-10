"""Tests for the transparent scoring engine."""

from app.services.scoring.scorer import run_scan
from app.services.parser.base import ParsedText


JD = """
Senior Software Engineer
We need a Senior Software Engineer for our Platform team.
- Design and build REST APIs and microservices in Python and Node.js
- Work with PostgreSQL and Redis
- Deploy on AWS with Docker and Kubernetes
- Implement CI/CD pipelines and unit testing
- 5+ years of Python, React, and REST API design
- Strong communication and problem-solving skills
- Bachelor's degree in Computer Science
"""


def _parsed(text: str, **kwargs) -> ParsedText:
    base = dict(text=text, word_count=len(text.split()), has_text_layer=True)
    base.update(kwargs)
    return ParsedText(**base)


def test_scan_returns_breakdown():
    resume = (
        "SUMMARY\nSoftware engineer with 6 years of Python and Node.js.\n"
        "EXPERIENCE\nBuilt REST APIs with PostgreSQL and Redis at Acme.\n"
        "Deployed services on AWS using Docker and Kubernetes. "
        "Implemented CI/CD pipelines and unit testing.\n"
        "SKILLS\nPython, React, PostgreSQL, Redis, AWS, Docker, Kubernetes, "
        "REST API design, CI/CD, unit testing.\n"
        "EDUCATION\nBachelor's degree in Computer Science.\n"
    )
    result = run_scan(JD, _parsed(resume))
    assert result.score.overall >= 0
    assert result.score.overall <= 100
    names = [c.name for c in result.score.components]
    assert set(names) == {"keyword_match", "format_compat", "section_coverage", "content_quality"}
    assert sum(c.weight for c in result.score.components) == 1.0
    assert result.missing_keywords or result.present_keywords
    assert result.resume_word_count > 0
    assert result.jd_word_count > 0


def test_scan_penalizes_tables_and_scanned():
    good = _parsed(
        "SUMMARY\nPython engineer.\nEXPERIENCE\nBuilt APIs.\nSKILLS\nPython.\nEDUCATION\nBSc.\n",
        has_tables=False,
        scanned=False,
    )
    bad = _parsed(
        "SUMMARY\nPython engineer.\nEXPERIENCE\nBuilt APIs.\nSKILLS\nPython.\nEDUCATION\nBSc.\n",
        has_tables=True,
        table_count=4,
        scanned=True,
        has_text_layer=False,
    )
    good_result = run_scan(JD, good)
    bad_result = run_scan(JD, bad)
    fmt_good = next(c for c in good_result.score.components if c.name == "format_compat")
    fmt_bad = next(c for c in bad_result.score.components if c.name == "format_compat")
    assert fmt_bad.score < fmt_good.score
    assert bad_result.score.overall < good_result.score.overall


def test_scan_short_resume_flagged():
    result = run_scan(JD, _parsed("hello world", word_count=2))
    assert any(issue.type.value == "too_short" for issue in result.format_issues)


def test_scan_high_match_for_good_resume():
    resume = (
        "SUMMARY\nSenior Software Engineer, 6 years.\n"
        "EXPERIENCE\nBuilt REST APIs and microservices in Python and Node.js. "
        "Used PostgreSQL and Redis. Deployed on AWS with Docker and Kubernetes. "
        "Implemented CI/CD pipelines and unit testing. Strong communication and "
        "problem-solving on cross-functional teams.\n"
        "EDUCATION\nBachelor's degree in Computer Science.\n"
        "SKILLS\nPython, Node.js, React, PostgreSQL, Redis, AWS, Docker, "
        "Kubernetes, CI/CD, unit testing, REST API design.\n"
    )
    result = run_scan(JD, _parsed(resume))
    kw = next(c for c in result.score.components if c.name == "keyword_match")
    assert kw.score > 60
