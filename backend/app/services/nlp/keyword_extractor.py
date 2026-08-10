"""Keyword extraction from a job description.

Pipeline:
1. spaCy (en_core_web_sm) noun chunks + POS-based candidate phrases, when loaded.
2. Curated skills lexicon matching (exact, normalized).
3. Capitalized multi-word terms / tech-token patterns (e.g. "Node.js", "CI/CD").
4. Frequency ranking + dedup, keeping only terms the JD actually stresses.

Everything is deterministic and explainable.
"""

from __future__ import annotations

import logging
import re
from collections import Counter

from .skill_lexicon import (
    HARD_SKILLS,
    SOFT_SKILLS,
    DEGREE_KEYWORDS,
    CERTIFICATIONS,
    CATEGORY_EXPLANATIONS,
)
from ...utils.text import (
    STOPWORDS,
    normalize_whitespace,
    remove_masked_pii,
    tokenize,
    words,
)

logger = logging.getLogger(__name__)

# Load spaCy lazily (optional dependency).
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy

            _nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer", "parser"])
        except Exception:
            _nlp = False
    return _nlp or None


_CAP_TERM = re.compile(
    r"(?<!\w)(?:\d+\.?[a-z]*|[A-Z][A-Za-z0-9+#.\-]*)(?:[ /+]\d+\.?[a-z]*|[ /+][A-Z][A-Za-z0-9+#.\-]*){0,4}"
)
_TECH_TOKEN = re.compile(
    r"^\w+(?:\.\w+)+$|^\w+#$|^[\w+-]+/[\w+-]+$|^ci/cd$|^rest(?:ful)?$|^api$|^c\+\+$|^c#"
)


def _normalize(term: str) -> str:
    return re.sub(r"[^a-z0-9+#.]+", " ", term.lower()).strip()


def _stopword_phrase(term: str) -> bool:
    return _normalize(term) in STOPWORDS


def extract_jd_keywords(jd: str, max_keywords: int = 40) -> list[dict]:
    """Return ranked keywords with category + JD context sentence."""
    jd = normalize_whitespace(remove_masked_pii(jd))
    jd_lower = jd.lower()
    candidates: dict[str, dict] = {}

    def add(term: str, category: str, strength: float = 1.0) -> None:
        norm = _normalize(term)
        if not norm or len(norm) < 2 or _stopword_phrase(term):
            return
        entry = candidates.setdefault(
            norm,
            {"term": term, "category": category, "count": 0, "strength": 0.0},
        )
        entry["count"] += 1
        entry["strength"] = max(entry["strength"], strength)

    # 1) Lexicon matching (hard skills, tools, soft skills, credentials).
    _match_lexicon(jd_lower, add)

    # 2) Capitalized / tech-token phrases.
    for m in _CAP_TERM.finditer(jd):
        token = m.group(0).rstrip(".,;:!?")
        norm = _normalize(token)
        if 2 <= len(norm) <= 6 and not _is_common_capital(norm):
            add(token, "tool" if _looks_tech(token) else "hard_skill", 0.8)

    # 3) spaCy noun chunks (when available).
    nlp = _get_nlp()
    if nlp:
        try:
            doc = nlp(jd)
            for chunk in doc.noun_chunks:
                text = chunk.text.strip()
                if 2 <= len(words(text)) <= 5:
                    add(text, "hard_skill", 0.6)
            for token in doc:
                if token.is_upper and len(token.text) >= 3:
                    add(token.text, "hard_skill", 0.5)
        except Exception as exc:  # pragma: no cover
            logger.debug("spaCy extraction failed: %s", exc)

    # 4) Drop noise: terms absent from JD are filtered by construction; now rank.
    ranked = sorted(
        candidates.values(),
        key=lambda e: (e["count"], e["strength"]),
        reverse=True,
    )
    # Ensure the term text used for display is the original casing.
    seen: set[str] = set()
    result: list[dict] = []
    for entry in ranked:
        norm = _normalize(entry["term"])
        if norm in seen:
            continue
        seen.add(norm)
        result.append(
            {
                "keyword": entry["term"],
                "category": entry["category"],
                "count": entry["count"],
                "jd_context": _find_context_sentence(jd, entry["term"]),
            }
        )
        if len(result) >= max_keywords:
            break
    return result


def _matches_credential(norm: str, jd_lower: str) -> bool:
    # Credentials are only meaningful if literally mentioned in the JD.
    return norm in jd_lower


def _is_common_capital(norm: str) -> bool:
    return norm in {
        "the", "and", "you", "your", "will", "should", "must", "have", "has",
        "with", "this", "that", "from", "they", "their", "our", "its", "are",
        "for", "job", "role", "position", "join", "about", "work", "team",
        "experience", "skills", "responsibilities", "qualifications", "plus",
        "requirements", "apply", "company", "benefits", "salary", "location",
        "design", "build", "develop", "developing", "manage", "managed",
        "lead", "leading", "support", "supporting", "help", "helping",
        "create", "creating", "provide", "providing", "ensure", "collaborate",
        "working", "knowledge", "understanding", "familiar", "preferred",
        "nice", "equal", "opportunity", "employer", "diversity", "inclusion",
        "description", "summary", "responsibility", "qualification", "requirement",
    }


def _looks_tech(token: str) -> bool:
    if _TECH_TOKEN.match(token):
        return True
    norm = _normalize(token)
    return any(k in norm for k in ("react", "node", "aws", "azure", "kubernetes",
                                   "docker", "tensorflow", "pytorch", "spark"))


def _match_lexicon(jd_lower: str, add) -> None:
    # Multi-word first: iterate HARD_SKILLS sorted by length desc.
    for term in sorted(HARD_SKILLS, key=len, reverse=True):
        if term in jd_lower:
            cat = "tool" if _tool_category(term) else "hard_skill"
            add(term, cat, 1.0)
    for term in SOFT_SKILLS:
        if term in jd_lower:
            add(term, "soft_skill", 0.9)
    for term in DEGREE_KEYWORDS:
        if term in jd_lower:
            add(term, "credential", 0.9)
    for term in CERTIFICATIONS:
        if term in jd_lower:
            add(term, "credential", 0.9)


def _tool_category(term: str) -> bool:
    tools = {
        "docker", "kubernetes", "jenkins", "terraform", "ansible", "git",
        "github", "gitlab", "jira", "confluence", "slack", "notion", "figma",
        "tableau", "power bi", "postman", "swagger", "jupyter", "excel",
        "aws", "azure", "gcp", "mongodb", "redis", "elasticsearch",
        "tensorflow", "pytorch", "pandas", "numpy", "docker compose",
    }
    return _normalize(term) in {_normalize(t) for t in tools}


def _find_context_sentence(jd: str, term: str) -> str:
    """Find the JD sentence containing the term."""
    term_low = _normalize(term)
    for part in re.split(r"(?<=[.!?])\s+|\n+", jd):
        if term_low in _normalize(part):
            return part.strip()
    # Fallback: substring search.
    for part in re.split(r"(?<=[.!?])\s+|\n+", jd):
        if term_low.split()[0] in _normalize(part):
            return part.strip()
    return ""


def explain_keyword(category: str) -> str:
    return CATEGORY_EXPLANATIONS.get(category, CATEGORY_EXPLANATIONS["hard_skill"])
