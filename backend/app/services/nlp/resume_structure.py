"""Resume section detection and content-quality signals.

Section detection works on line boundaries (headers are usually short, all-caps
or title-cased lines) so we can report transparently which sections exist.
"""

from __future__ import annotations

import re

from .skill_lexicon import SOFT_SKILLS, HARD_SKILLS
from ...utils.text import normalize_whitespace, words, word_count

SECTION_HEADERS = {
    "summary": {"summary", "profile", "professional summary", "objective",
                "about me", "career summary", "executive summary"},
    "experience": {"experience", "work experience", "employment", "professional experience",
                   "career history", "work history", "relevant experience",
                   "professional background"},
    "education": {"education", "academic", "academics", "education & training",
                  "education and training", "educational background"},
    "skills": {"skills", "technical skills", "core skills", "skills & expertise",
               "skills and expertise", "key skills", "technologies", "expertise",
               "competencies", "technical competencies"},
    "projects": {"projects", "personal projects", "key projects", "project experience",
                 "notable projects", "selected projects"},
    "certifications": {"certifications", "certificates", "certification",
                       "licenses", "licenses & certifications", "licences",
                       "accreditations"},
    "awards": {"awards", "honors", "awards & honors", "honours", "awards and honors"},
    "languages": {"languages", "language skills"},
    "publications": {"publications", "papers", "research"},
    "volunteering": {"volunteer", "volunteering", "volunteer experience",
                     "community involvement"},
    "interests": {"interests", "hobbies", "additional interests"},
}

ACTION_VERBS = {
    "led", "managed", "developed", "built", "created", "designed", "implemented",
    "launched", "drove", "delivered", "increased", "improved", "reduced",
    "optimized", "optimised", "automated", "streamlined", "negotiated",
    "collaborated", "coordinated", "achieved", "grew", "established", "founded",
    "mentored", "trained", "architected", "engineered", "spearheaded", "owned",
    "accelerated", "transformed", "shipped", "generated", "saved", "cut",
    "boosted", "strengthened", "modernized", "migrated", "integrated",
    "refactored", "deployed", "configured", "maintained", "analyzed",
    "analysed", "researched", "produced", "presented", "wrote", "advocated",
}

QUANT_PATTERN = re.compile(
    r"(\d[\d,.]*\s*%|(?:by|of|to|from|at|for)\s+\d[\d,.]*\s*(?:%|x|X)?|"
    r"\$\s?\d[\d,.]*|(?:in|under|within)\s+\d+\s*(?:days?|weeks?|months?|hours?|ms|s|years?))"
)


def detect_sections(lines: list[str]) -> dict[str, dict]:
    """Map section name -> {present, words} using header heuristics."""
    result = {name: {"present": False, "words": 0} for name in SECTION_HEADERS}
    current = None
    for raw in lines:
        line = normalize_whitespace(raw)
        if not line:
            continue
        low = line.lower().strip(": .,-–—|")
        header = _match_header(low)
        if header:
            current = header
            result[header]["present"] = True
            # Words that belong to this section: everything after an inline
            # label like "Skills: ...", or the whole line otherwise.
            section_words = low.split(":", 1)[1] if ":" in low else low
            result[header]["words"] += word_count(section_words)
        elif current:
            result[current]["words"] += word_count(line)
    return result


def _match_header(low: str) -> str | None:
    for name, aliases in SECTION_HEADERS.items():
        for alias in aliases:
            if low == alias or low.startswith(alias + ":"):
                return name
    return None


def content_quality_signals(text: str) -> dict:
    """Quantified achievements, action verbs, bullet usage, length balance."""
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    total_words = word_count(text)
    quantified = [s.strip() for s in sentences if QUANT_PATTERN.search(s)]
    action_verbs_found = [v for v in ACTION_VERBS if re.search(rf"\b{v}\b", text.lower())]
    bullet_chars = text.count("•") + text.count("●") + text.count("▪") + text.count("- ") + text.count("* ")
    return {
        "quantified_sentences": len(quantified),
        "quantified_ratio": round(len(quantified) / max(1, len(sentences)), 3),
        "action_verbs": action_verbs_found,
        "action_verb_ratio": round(
            len(action_verbs_found) / max(1, min(len(sentences), 40)), 3
        ),
        "bullet_usage": bullet_chars > 0,
        "total_words": total_words,
    }


def split_lines(text: str) -> list[str]:
    return [l for l in text.splitlines() if l.strip()]
