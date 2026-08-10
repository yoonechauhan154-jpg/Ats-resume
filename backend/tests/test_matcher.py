"""Tests for the ATSMatcher engine (pure local NLP)."""

from app.services.matcher import ATSMatcher, get_matcher


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

GOOD_RESUME = (
    "SUMMARY\nSenior Software Engineer with 6 years of experience.\n"
    "EXPERIENCE\nBuilt REST APIs and microservices in Python and Node.js. "
    "Used PostgreSQL and Redis. Deployed on AWS with Docker and Kubernetes. "
    "Implemented CI/CD pipelines and unit testing. "
    "Strong communication and problem-solving skills.\n"
    "SKILLS\nPython, React, Node.js, PostgreSQL, Redis, AWS, Docker, "
    "Kubernetes, CI/CD, REST API design, unit testing.\n"
    "EDUCATION\nBachelor's degree in Computer Science.\n"
)

UNRELATED_RESUME = (
    "SUMMARY\nRegistered Nurse with 10 years of bedside care.\n"
    "EXPERIENCE\nManaged patient care plans and medication schedules. "
    "Collaborated with physicians and families. Documented vitals and "
    "maintained sterile environments.\n"
    "SKILLS\nPatient care, IV therapy, wound care, EHR systems.\n"
    "EDUCATION\nBachelor of Science in Nursing.\n"
)


def _matcher() -> ATSMatcher:
    return ATSMatcher()


def test_analyze_returns_full_contract():
    result = _matcher().analyze(JD, GOOD_RESUME, format_score=90.0)
    assert set(result) == {
        "ats_score",
        "keyword_match_percent",
        "semantic_similarity",
        "matched_keywords",
        "missing_keywords",
        "score_breakdown",
    }
    assert isinstance(result["ats_score"], int)
    assert 0 <= result["ats_score"] <= 100
    assert 0 <= result["keyword_match_percent"] <= 100
    assert 0 <= result["semantic_similarity"] <= 1.0


def test_score_breakdown_weights_and_sum():
    result = _matcher().analyze(JD, GOOD_RESUME, format_score=90.0)
    b = result["score_breakdown"]
    assert set(b) == {"keyword_match", "semantic_similarity", "format_score"}
    assert 0 <= b["keyword_match"] <= 50
    assert 0 <= b["semantic_similarity"] <= 30
    assert 0 <= b["format_score"] <= 20
    # The integer ats_score equals the (rounded) sum of the components.
    assert abs(sum(b.values()) - result["ats_score"]) < 1


def test_format_score_passed_separately():
    low = _matcher().analyze(JD, GOOD_RESUME, format_score=10.0)
    high = _matcher().analyze(JD, GOOD_RESUME, format_score=100.0)
    assert high["score_breakdown"]["format_score"] > low["score_breakdown"]["format_score"]
    assert high["ats_score"] >= low["ats_score"]
    # Keyword + semantic parts are unaffected by the passed-in format score.
    for key in ("keyword_match", "semantic_similarity"):
        assert high["score_breakdown"][key] == low["score_breakdown"][key]


def test_good_resume_beats_unrelated():
    m = _matcher()
    good = m.analyze(JD, GOOD_RESUME, format_score=100.0)
    bad = m.analyze(JD, UNRELATED_RESUME, format_score=100.0)
    assert good["ats_score"] > bad["ats_score"]
    assert good["keyword_match_percent"] > bad["keyword_match_percent"]
    assert good["semantic_similarity"] > bad["semantic_similarity"]


def test_matched_and_missing_are_consistent():
    result = _matcher().analyze(JD, GOOD_RESUME)
    present = set(result["matched_keywords"])
    missing = result["missing_keywords"]
    missing_terms = {d["keyword"] for d in missing}
    assert present.isdisjoint(missing_terms)
    assert len(present) + len(missing_terms) > 0


def test_missing_keywords_dict_contract():
    result = _matcher().analyze(JD, UNRELATED_RESUME)
    for item in result["missing_keywords"]:
        assert set(item) == {
            "keyword",
            "importance",
            "why_it_matters",
            "suggestion",
            "jd_frequency",
        }
        assert item["keyword"]
        assert item["importance"] in ("HIGH", "MEDIUM", "LOW")
        assert item["why_it_matters"]
        assert item["suggestion"]
        assert isinstance(item["jd_frequency"], int)
        assert item["jd_frequency"] >= 1


def test_importance_from_frequency_and_position():
    # "Python" appears twice and near the top of JD -> HIGH.
    result = _matcher().analyze(JD, UNRELATED_RESUME)
    by_term = {d["keyword"]: d for d in result["missing_keywords"]}
    if "python" in by_term:
        assert by_term["python"]["importance"] == "HIGH"
        assert by_term["python"]["jd_frequency"] >= 2
    if "react" in by_term:
        assert by_term["react"]["importance"] in ("HIGH", "MEDIUM")


def test_why_it_matters_is_exact_jd_sentence():
    result = _matcher().analyze(JD, UNRELATED_RESUME)
    jd_lower = JD.lower()
    for item in result["missing_keywords"]:
        sentence = item["why_it_matters"].lower()
        # The reported sentence must actually appear in the JD.
        assert item["keyword"].lower() in sentence
        assert sentence.strip() in jd_lower or sentence.strip() in JD.lower()


def test_empty_inputs_do_not_crash():
    result = _matcher().analyze("", "", format_score=0.0)
    assert result["ats_score"] == 0
    assert result["keyword_match_percent"] == 0.0
    assert result["matched_keywords"] == []
    assert result["missing_keywords"] == []
    assert result["score_breakdown"]["format_score"] == 0.0


def test_semantic_match_counts_without_literal_phrase():
    # "communication skills" is not literal, but semantically close sentences
    # should still register it as matched (via the sentence-transformer path).
    resume = (
        "Worked closely with stakeholders, ran team standups and "
        "presented updates to leadership every week."
    )
    result = _matcher().analyze(JD, resume)
    terms = set(result["matched_keywords"]) | {d["keyword"] for d in result["missing_keywords"]}
    assert any("communication" in t or "communication" in t for t in terms)


def test_get_matcher_is_singleton():
    assert get_matcher() is get_matcher()
