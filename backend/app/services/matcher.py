"""ATS Matcher Engine — pure local NLP, zero API cost.

Composes the existing NLP building blocks into a single deterministic
entry point:

- keyword extraction      -> nlp.keyword_extractor.extract_jd_keywords
- keyword matching        -> nlp.semantic.keyword_present (literal + semantic)
- document similarity     -> sentence-transformer (all-MiniLM-L6-v2) mean-max,
                             TF-IDF fallback (sklearn)
- format score            -> passed in separately (computed by format_checker)

Models (spaCy + sentence-transformers) are loaded once at init and shared
with the rest of the app through the module-level singletons, so a scan
never triggers a second model download or a second copy in memory.

Everything is deterministic and explainable — nothing here calls an API.
"""

from __future__ import annotations

import logging
import threading

from .nlp.keyword_extractor import _get_nlp, extract_jd_keywords
from .nlp.semantic import _load_model, keyword_present
from ..utils.text import (
    normalize_whitespace,
    remove_masked_pii,
    sentences,
)

logger = logging.getLogger(__name__)

KEYWORD_WEIGHT = 50.0   # max points for keyword_match in the final score
SEMANTIC_WEIGHT = 30.0  # max points for semantic_similarity
FORMAT_WEIGHT = 20.0    # max points for format_score

# Importance buckets, driven by JD frequency + position (earlier = more vital).
IMPORTANCE_HIGH_POS = 0.25
IMPORTANCE_MED_POS = 0.60


class ATSMatcher:
    """Match a resume against a job description using only local NLP.

    >>> matcher = ATSMatcher()
    >>> result = matcher.analyze(jd, resume, format_score=90.0)
    """

    def __init__(self) -> None:
        # Load once, at init. Reuses the app-wide singletons so repeated
        # instantiations (or the scorer) never load a second model copy.
        self.nlp = _get_nlp()
        self.embedder = _load_model()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def analyze(
        self,
        jd_text: str,
        resume_text: str,
        format_score: float = 0.0,
    ) -> dict:
        """Return a full ATS match report.

        ``format_score`` (0-100) is expected to come from format_checker and
        is folded in as the last 20 points.
        """
        jd = normalize_whitespace(remove_masked_pii(jd_text or ""))
        resume = normalize_whitespace(resume_text or "")
        resume_lower = resume.lower()
        resume_sents = sentences(resume)
        jd_lower = jd.lower()
        jd_len = max(1, len(jd_lower))

        keywords = extract_jd_keywords(jd, max_keywords=40)

        matched: list[str] = []
        missing: list[dict] = []
        for kw in keywords:
            term = kw["keyword"]
            is_present, _ = keyword_present(term, resume_lower, resume_sents)
            if is_present:
                matched.append(term)
            else:
                idx = jd_lower.find(term.lower())
                pos_ratio = idx / jd_len if idx >= 0 else 1.0
                missing.append(
                    {
                        "keyword": term,
                        "importance": _importance(kw["count"], pos_ratio),
                        "why_it_matters": kw["jd_context"],
                        "suggestion": _suggestion(term, kw["category"], _importance(kw["count"], pos_ratio)),
                        "jd_frequency": kw["count"],
                    }
                )

        keyword_match_percent = round(len(matched) / max(1, len(keywords)) * 100, 1)
        semantic_similarity = self._document_similarity(jd, resume)

        breakdown = {
            "keyword_match": round(min(keyword_match_percent * (KEYWORD_WEIGHT / 100), KEYWORD_WEIGHT), 1),
            "semantic_similarity": round(max(0.0, min(semantic_similarity, 1.0)) * SEMANTIC_WEIGHT, 1),
            "format_score": round(max(0.0, min(float(format_score), 100.0)) * (FORMAT_WEIGHT / 100), 1),
        }
        ats_score = int(round(sum(breakdown.values())))
        ats_score = max(0, min(100, ats_score))

        return {
            "ats_score": ats_score,
            "keyword_match_percent": keyword_match_percent,
            "semantic_similarity": round(semantic_similarity, 4),
            "matched_keywords": matched,
            "missing_keywords": missing,
            "score_breakdown": breakdown,
        }

    # ------------------------------------------------------------------ #
    # Semantic similarity between the two documents (0..1)
    # ------------------------------------------------------------------ #
    def _document_similarity(self, jd: str, resume: str) -> float:
        """Mean over JD sentences of their best cosine to any resume sentence.

        More discriminative than a single whole-document cosine, which is
        nearly always high regardless of fit. Falls back to a TF-IDF
        document cosine when sentence-transformers is unavailable.
        """
        if not jd or not resume:
            return 0.0

        if self.embedder is not None:
            try:
                jd_sents = [s for s in sentences(jd) if len(s.split()) >= 3][:40]
                res_sents = [s for s in sentences(resume) if len(s.split()) >= 3][:80]
                if not jd_sents or not res_sents:
                    return 0.0
                import numpy as np
                from numpy.linalg import norm

                jd_emb = self.embedder.encode(jd_sents)
                res_emb = self.embedder.encode(res_sents)
                jd_emb = jd_emb / (norm(jd_emb, axis=1, keepdims=True) + 1e-9)
                res_emb = res_emb / (norm(res_emb, axis=1, keepdims=True) + 1e-9)
                best = (jd_emb @ res_emb.T).max(axis=1)
                return float(np.mean(best))
            except Exception as exc:  # pragma: no cover
                logger.debug("embedding document similarity failed: %s", exc)

        # TF-IDF fallback.
        try:
            import numpy as np
            from sklearn.feature_extraction.text import TfidfVectorizer

            vec = TfidfVectorizer(stop_words="english", lowercase=True)
            matrix = vec.fit_transform([jd, resume])
            a, b = matrix[0], matrix[1]
            denom = float(np.sqrt(a.power(2).sum()) * np.sqrt(b.power(2).sum())) + 1e-9
            return float((a @ b.T).toarray()[0, 0] / denom)
        except Exception as exc:  # pragma: no cover
            logger.debug("tfidf document similarity failed: %s", exc)

        return 0.0


def _importance(count: int, pos_ratio: float) -> str:
    """Importance from JD frequency + position (earlier in the JD = higher)."""
    if count >= 2 or pos_ratio <= IMPORTANCE_HIGH_POS:
        return "HIGH"
    if count == 1 and pos_ratio <= IMPORTANCE_MED_POS:
        return "MEDIUM"
    return "LOW"


def _suggestion(term: str, category: str, importance: str = "MEDIUM") -> str:
    if category == "credential":
        base = (
            f"The JD asks for '{term}'. If you hold it, list it plainly under "
            "Education / Certifications — only if it is true."
        )
    else:
        base = (
            f"The JD uses '{term}'. If you have done this work, use the same phrasing "
            "in your Skills or Experience section (facts only, never invent). "
            "If you haven't, skip it — honesty beats padding."
        )
    if importance == "HIGH":
        return (
            f"'{term}' is a HIGH-priority requirement for this role "
            f"(mentioned repeatedly or near the top of the JD). {base}"
        )
    if importance == "LOW":
        return (
            f"'{term}' is a nice-to-have for this role — only add it if you "
            f"genuinely have the experience. {base}"
        )
    return base


# ---------------------------------------------------------------------- #
# Shared instance: construct once, reuse across requests.
# ---------------------------------------------------------------------- #
_matcher = None
_matcher_lock = threading.Lock()


def get_matcher() -> ATSMatcher:
    """Return the process-wide ATSMatcher (models load at most once)."""
    global _matcher
    if _matcher is None:
        with _matcher_lock:
            if _matcher is None:
                _matcher = ATSMatcher()
    return _matcher
