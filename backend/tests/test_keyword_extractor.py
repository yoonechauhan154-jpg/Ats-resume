"""Tests for keyword extraction."""

from app.services.nlp.keyword_extractor import extract_jd_keywords, explain_keyword
from app.services.nlp.semantic import keyword_present


JD = """
Senior Software Engineer
We are looking for a Senior Software Engineer to join our Platform team.
Responsibilities:
- Design and build robust REST APIs and microservices in Python and Node.js
- Work with PostgreSQL and Redis for high-traffic data
- Deploy services on AWS using Docker and Kubernetes
- Implement CI/CD pipelines and unit testing
Requirements:
- 5+ years of experience with Python, React, and REST API design
- Strong communication and problem-solving skills
- Experience with machine learning and data pipelines is a plus
- Bachelor's degree in Computer Science or related field
"""


def test_extract_jd_keywords_finds_core_terms():
    keywords = extract_jd_keywords(JD, max_keywords=40)
    terms = [k["keyword"].lower() for k in keywords]
    for expected in ["python", "node.js", "postgresql", "redis", "docker",
                     "kubernetes", "aws", "react", "machine learning"]:
        assert expected in terms, f"missing {expected} from {terms}"


def test_keywords_have_context():
    keywords = extract_jd_keywords(JD)
    assert all(k["jd_context"] for k in keywords)


def test_keyword_present_literal():
    present, evidence = keyword_present(
        "Docker", JD.lower(), [s.strip() for s in JD.split("\n") if s.strip()]
    )
    assert present is True
    assert evidence


def test_keyword_present_missing():
    present, _ = keyword_present("Terraform", "backend developer with python experience", [])
    assert present is False


def test_explain_keyword_covers_categories():
    for cat in ["hard_skill", "soft_skill", "credential", "tool"]:
        assert len(explain_keyword(cat)) > 20
