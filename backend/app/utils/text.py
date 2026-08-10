"""Small pure-text helpers shared across services."""

from __future__ import annotations

import re

_MULTI_WS = re.compile(r"[ \t]+")
_NEWLINES = re.compile(r"\n{3,}")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(\+?\d[\d\s().-]{6,}\d)(?!\d)")
_URL = re.compile(r"(https?://[^\s]+|www\.[^\s]+)")

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "have", "has", "are",
    "was", "were", "will", "can", "all", "any", "our", "your", "their", "its",
    "into", "over", "under", "about", "after", "before", "between", "during",
    "including", "using", "such", "also", "very", "just", "but", "not", "you",
    "we", "they", "them", "she", "he", "him", "her", "who", "whom", "which",
    "what", "when", "where", "how", "than", "then", "other", "another", "each",
    "both", "few", "more", "most", "some", "work", "role", "job", "position",
    "responsibilities", "responsibility", "requirements", "requirement",
    "qualified", "qualifications", "candidate", "experience", "plus", "must",
    "should", "ability", "strong", "skills", "skill", "team", "knowledge",
}


def normalize_whitespace(text: str) -> str:
    text = text.replace("\xa0", " ")
    lines = []
    for line in text.splitlines():
        line = _MULTI_WS.sub(" ", line).strip()
        if line:
            lines.append(line)
        else:
            lines.append("")
    text = "\n".join(lines)
    text = _NEWLINES.sub("\n\n", text)
    return text.strip()


def remove_masked_pii(text: str) -> str:
    """Replace emails/phones/URLs with placeholders so they aren't analyzed
    as keywords or echoed into analytics."""
    text = _EMAIL.sub("[email]", text)
    text = _PHONE.sub("[phone]", text)
    text = _URL.sub("[url]", text)
    return text


def clean_line(line: str) -> str:
    return normalize_whitespace(line.replace("\x00", ""))


def sentences(text: str) -> list[str]:
    """Very small sentence splitter (no nltk dependency)."""
    text = normalize_whitespace(text)
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 1]


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9+#./\-_]+", text.lower()) if t]


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[A-Za-z]+(?:[A-Za-z0-9.]*[A-Za-z0-9])?", text) if w]


def word_count(text: str) -> int:
    return len(words(text))


def phrase_ngrams(tokens: list[str], n: int = 2) -> list[str]:
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def levenshtein(a: str, b: str) -> int:
    """Edit distance for small keyword fuzzy-matching."""
    if a == b:
        return 0
    if not a or not b:
        return len(a) or len(b)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]
