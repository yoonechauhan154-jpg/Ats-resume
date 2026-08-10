"""Transparent ATS scoring engine.

Overall score = weighted sum of 4 components, each fully explained:
  1. keyword_match      (40%) - share of JD keywords found in the resume
  2. format_compat      (30%) - ATS-safe formatting (no tables/scanned/...)
  3. section_coverage   (15%) - standard resume sections present
  4. content_quality    (15%) - quantified achievements + action verbs + length

Nothing is a black box: every deduction maps to concrete evidence.
"""

from __future__ import annotations

import datetime as dt
import logging
import re

from .format_checker import analyze_format
from ..nlp.keyword_extractor import extract_jd_keywords, explain_keyword
from ..nlp.semantic import keyword_present
from ..nlp.resume_structure import (
    detect_sections,
    content_quality_signals,
    split_lines,
    ACTION_VERBS,
)
from ..parser.base import ParsedText
from ...models.schemas import (
    KeywordHit,
    ScoreBreakdown,
    ScoreComponent,
    ScanResponse,
    FormatIssue,
    ResumeSection,
)
from ...utils.text import (
    normalize_whitespace,
    remove_masked_pii,
    sentences,
    word_count,
)

logger = logging.getLogger(__name__)

WEIGHTS = {
    "keyword_match": 0.40,
    "format_compat": 0.30,
    "section_coverage": 0.15,
    "content_quality": 0.15,
}


def run_scan(jd: str, parsed: ParsedText) -> ScanResponse:
    jd_clean = normalize_whitespace(remove_masked_pii(jd))
    resume_clean = normalize_whitespace(parsed.text)

    jd_words = word_count(jd_clean)
    resume_words = word_count(resume_clean)
    resume_sents = sentences(resume_clean)
    resume_lower = resume_clean.lower()
    jd_lower = jd_clean.lower()
    jd_len = max(1, len(jd_lower))

    # --- Keyword component ---
    keywords = extract_jd_keywords(jd_clean, max_keywords=40)
    hits: list[KeywordHit] = []
    present: list[str] = []
    missing: list[KeywordHit] = []

    for kw in keywords:
        term = kw["keyword"]
        is_present, evidence = keyword_present(term, resume_lower, resume_sents)
        idx = jd_lower.find(term.lower())
        pos_ratio = idx / jd_len if idx >= 0 else 1.0
        importance = _importance(kw["count"], pos_ratio)
        hit = KeywordHit(
            keyword=term,
            in_resume=is_present,
            context=kw["jd_context"],
            category=kw["category"],
            importance=importance,
            jd_frequency=kw["count"],
            why_it_matters=explain_keyword(kw["category"]),
            suggestion=(
                "The JD uses this exact term. If you have done this work, use the "
                "same phrasing in your Skills or Experience section (facts only, "
                "never invent). If you haven't, skip it — honesty beats padding."
                if not is_present
                else ""
            ),
        )
        if is_present:
            present.append(term)
        else:
            missing.append(hit)
        hits.append(hit)

    matched_ratio = len(present) / max(1, len(keywords))
    keyword_score = round(matched_ratio * 100, 1)
    keyword_details = [
        f"{len(present)} of {len(keywords)} JD keywords found in the resume.",
        "Matched includes exact terms plus close semantic equivalents (e.g. synonyms).",
    ]

    # --- Format component ---
    format_issues, format_score = analyze_format(parsed, resume_words)
    format_details = [
        f"{len(format_issues)} potential ATS parsing issue(s) identified.",
        "Scanned documents and tables are the largest single deductions.",
    ]

    # --- Section coverage ---
    lines = split_lines(resume_clean)
    sections = detect_sections(lines)
    core = ["summary", "experience", "education", "skills"]
    covered = sum(1 for s in core if sections[s]["present"])
    section_score = round(covered / len(core) * 100, 1)
    section_details = [
        f"{covered}/{len(core)} core sections detected (summary, experience, education, skills).",
        "Core sections help ATS structure your resume into the fields it screens.",
    ]

    # --- Content quality ---
    q = content_quality_signals(resume_clean)
    quality_score = 50.0
    quality_details: list[str] = []
    if q["quantified_ratio"] >= 0.25:
        quality_score += 30
        quality_details.append(
            f"{q['quantified_sentences']} sentences contain metrics or quantified outcomes."
        )
    else:
        quality_score += 15
        quality_details.append("Few quantified outcomes found. Numbers (facts only) strongly help ranking.")
    if q["action_verb_ratio"] >= 0.35:
        quality_score += 15
        quality_details.append("Strong action-verb usage detected.")
    else:
        quality_score += 8
        quality_details.append("More action verbs (led, built, improved, ...) would strengthen bullets.")
    if 250 <= resume_words <= 750:
        quality_score += 5
        quality_details.append("Resume length is in the typical 1-2 page sweet spot.")
    elif resume_words > 0:
        quality_details.append("Resume length is outside the typical 250-750 word range.")
    quality_score = round(min(100.0, quality_score), 1)

    components = [
        ScoreComponent(name="keyword_match", weight=WEIGHTS["keyword_match"], score=keyword_score, details=keyword_details),
        ScoreComponent(name="format_compat", weight=WEIGHTS["format_compat"], score=format_score, details=format_details),
        ScoreComponent(name="section_coverage", weight=WEIGHTS["section_coverage"], score=section_score, details=section_details),
        ScoreComponent(name="content_quality", weight=WEIGHTS["content_quality"], score=quality_score, details=quality_details),
    ]
    overall = round(sum(c.score * c.weight for c in components), 1)

    format_summary, headline = _headline(overall, keyword_score, format_score, covered)

    return ScanResponse(
        score=ScoreBreakdown(overall=overall, components=components),
        missing_keywords=missing[:25],
        present_keywords=present[:40],
        format_issues=format_issues,
        sections=[
            ResumeSection(
                name=name,
                present=sections[name]["present"],
                words=sections[name]["words"],
            )
            for name in sections
        ],
        resume_word_count=resume_words,
        jd_word_count=jd_words,
        format_summary=format_summary,
        headline=headline,
        scanned_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        resume_text=resume_clean,
        resume_bullets=_extract_bullets(resume_clean),
    )


def _importance(count: int, pos_ratio: float) -> str:
    """HIGH when the JD repeats the term or lists it in the first quarter."""
    if count >= 2 or pos_ratio <= 0.25:
        return "HIGH"
    if count == 1 and pos_ratio <= 0.60:
        return "MEDIUM"
    return "LOW"


def _extract_bullets(text: str, limit: int = 30) -> list[str]:
    """Split resume text into candidate bullets (lines that look like bullets)."""
    bullets: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Bullet markers
        if re.match(r"^[•●▪◦‣*\-–—›>]\s*", line):
            clean = re.sub(r"^[•●▪◦‣*\-–—›>]\s*", "", line).strip()
            if clean:
                bullets.append(clean)
    if not bullets:
        # Fallback: sentences that contain an action verb and look achievement-like.
        for sent in sentences(text):
            if any(v in sent.lower().split() for v in ACTION_VERBS):
                bullets.append(sent)
    return bullets[:limit]


def _headline(overall: float, kw: float, fmt: float, sections_covered: int) -> tuple[str, str]:
    if overall >= 80:
        return (
            "Strong ATS compatibility.",
            f"Great news: your resume scores {overall:.0f}/100. Minor tweaks below can push it higher.",
        )
    if overall >= 60:
        return (
            "Good foundation with room to improve.",
            f"Score {overall:.0f}/100. The biggest levers are below — usually keyword match and formatting.",
        )
    if overall >= 40:
        return (
            "Several issues are holding your resume back.",
            f"Score {overall:.0f}/100. Focus first on the critical format issues and the top missing keywords.",
        )
    return (
        "This resume will likely struggle in ATS screening.",
        f"Score {overall:.0f}/100. Fix the critical format issues below first, then address missing keywords.",
    )
