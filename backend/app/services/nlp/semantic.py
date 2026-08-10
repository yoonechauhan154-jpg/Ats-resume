"""Semantic keyword matching.

Primary: sentence-transformers (all-MiniLM-L6-v2) embeddings -> cosine similarity.
Fallback: TF-IDF cosine similarity (scikit-learn) if sentence-transformers is
unavailable or the model download fails.

The scorer uses this to decide whether a keyword is *effectively* present in
the resume (e.g. "led a cross-functional team" vs the literal keyword
"cross-functional collaboration").
"""

from __future__ import annotations

import logging
import re
import threading

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
SIM_THRESHOLD = 0.62

_model = None
_model_lock = threading.Lock()


def _load_model():
    """Lazy, once-per-process model load. Returns None if unavailable."""
    global _model
    if _model is not None:
        return _model or None
    with _model_lock:
        if _model is not None:
            return _model or None
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer(MODEL_NAME)
        except Exception as exc:
            logger.warning("sentence-transformers unavailable (%s); using TF-IDF fallback", exc)
            _model = False
    return _model or None


def semantic_available() -> bool:
    return _load_model() is not None


def _tfidf_vectorizer():
    from sklearn.feature_extraction.text import TfidfVectorizer

    return TfidfVectorizer(stop_words="english", lowercase=True)


def semantic_similarity(keyword: str, resume_sentences: list[str]) -> tuple[float, str]:
    """Return (best_score, best_matching_resume_sentence)."""
    best_score = 0.0
    best_sent = ""
    if not resume_sentences:
        return 0.0, ""

    model = _load_model()
    if model is not None:
        try:
            kw_emb = model.encode([keyword])
            sent_emb = model.encode(resume_sentences[:80])  # cap for latency
            import numpy as np

            from numpy.linalg import norm

            def cos(a, b):
                return float(np.dot(a, b) / (norm(a) * norm(b) + 1e-9))

            for sent, emb in zip(resume_sentences[:80], sent_emb):
                score = cos(kw_emb[0], emb)
                if score > best_score:
                    best_score = score
                    best_sent = sent
            return best_score, best_sent
        except Exception as exc:  # pragma: no cover
            logger.warning("embedding path failed, falling back: %s", exc)

    # TF-IDF fallback.
    try:
        import numpy as np

        vec = _tfidf_vectorizer()
        docs = [keyword] + resume_sentences[:200]
        matrix = vec.fit_transform(docs)
        kw_vec = matrix[0]
        sims = (matrix[1:] @ kw_vec.T).toarray().ravel()
        idx = int(np.argmax(sims)) if len(sims) else -1
        if idx >= 0 and sims[idx] > 0:
            return float(sims[idx]), resume_sentences[idx]
    except Exception as exc:  # pragma: no cover
        logger.debug("tfidf similarity failed: %s", exc)

    return 0.0, ""


def keyword_present(
    keyword: str, resume_lower: str, resume_sentences: list[str]
) -> tuple[bool, str]:
    """Decide if a keyword is effectively present.

    Returns (present, evidence). Evidence is the matching resume sentence when
    only a semantic match was found, or the literal term when it appears.
    """
    kw = keyword.strip().lower()
    if not kw:
        return False, ""

    # 1) Exact / normalized literal match (try a few resume normalizations so
    # "ci/cd" matches "CI/CD pipelines" and "ci cd pipelines" alike).
    norm = re.sub(r"[^a-z0-9+#.]+", " ", kw)
    resume_variants = [resume_lower]
    if "/" in resume_lower:
        resume_variants.append(re.sub(r"/", " ", resume_lower))
    if any(norm in v for v in resume_variants):
        return True, norm

    # 2) Token-level match for single words (covers stemming-ish variants).
    tokens = [t for t in norm.split() if len(t) > 1]
    if len(tokens) == 1 and tokens[0] in resume_lower:
        return True, tokens[0]

    # 3) Semantic similarity.
    score, best_sent = semantic_similarity(keyword, resume_sentences)
    if score >= SIM_THRESHOLD and best_sent:
        return True, best_sent
    return False, ""
