"""Pydantic schemas shared across the API."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class FileKind(str, Enum):
    pdf = "pdf"
    docx = "docx"


class FormatIssueType(str, Enum):
    table = "table"
    columns = "columns"
    image = "image"
    font = "font"
    scanned = "scanned"
    no_text_layer = "no_text_layer"
    textbox = "textbox"
    watermark = "watermark"
    too_short = "too_short"
    missing_contact = "missing_contact"


class Severity(str, Enum):
    critical = "critical"
    warning = "warning"
    info = "info"


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #
class KeywordHit(BaseModel):
    keyword: str
    in_resume: bool
    context: str = Field(default="", description="Exact JD sentence where the keyword appears")
    category: str = Field(default="hard_skill", description="hard_skill | soft_skill | credential | tool")
    importance: str = Field(default="MEDIUM", description="HIGH | MEDIUM | LOW priority for this role")
    jd_frequency: int = Field(default=0, description="How many times the JD mentions this keyword")
    why_it_matters: str = Field(default="", description="Plain-language explanation of why the keyword matters")
    suggestion: str = Field(default="", description="Where / how to add it without inventing anything")


class ScoreComponent(BaseModel):
    name: str
    weight: float  # 0..1
    score: float  # 0..100
    details: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    overall: float = Field(ge=0, le=100)
    components: list[ScoreComponent] = Field(default_factory=list)
    methodology: str = Field(
        default=(
            "Weighted average: keyword match (40%) + format compatibility (30%) + "
            "section coverage (15%) + content quality (15%). Every point is derived "
            "from explicit evidence in your resume and the job description."
        )
    )


class FormatIssue(BaseModel):
    type: FormatIssueType
    severity: Severity
    title: str
    description: str
    ats_impact: str = Field(default="", description="How this can hurt ATS parsing")
    fix: str = Field(default="", description="Actionable fix")


class ResumeSection(BaseModel):
    name: str
    present: bool
    words: int = 0


# --------------------------------------------------------------------------- #
# Scan response
# --------------------------------------------------------------------------- #
class ScanResponse(BaseModel):
    score: ScoreBreakdown
    missing_keywords: list[KeywordHit] = Field(default_factory=list)
    present_keywords: list[str] = Field(default_factory=list)
    format_issues: list[FormatIssue] = Field(default_factory=list)
    sections: list[ResumeSection] = Field(default_factory=list)
    resume_word_count: int = 0
    jd_word_count: int = 0
    format_summary: str = Field(default="")
    headline: str = Field(default="")
    scanned_at: str = Field(default="")
    # Returned so the user can reuse their own extracted text for AI features.
    # Never persisted server-side.
    resume_text: str = Field(default="")
    resume_bullets: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# AI rewrite / cover letter
# --------------------------------------------------------------------------- #
class RewrittenBullet(BaseModel):
    original: str
    rewritten: str
    changed: list[str] = Field(default_factory=list, description="What was changed, for the diff view")
    preserved: list[str] = Field(default_factory=list, description="Numbers / facts that were kept intact")
    reason: str = Field(default="")


class RewriteRequest(BaseModel):
    bullets: list[str] = Field(min_length=1)
    jd: str = Field(min_length=20)
    role: str = Field(default="")
    context: str = Field(default="", description="Optional resume context so the model never invents skills")


class RewriteResponse(BaseModel):
    rewritten: list[RewrittenBullet]
    rules_applied: list[str] = Field(default_factory=list)
    model_used: str = Field(default="")


class CoverLetterRequest(BaseModel):
    jd: str = Field(min_length=20)
    resume_summary: str = Field(default="", description="Plain-text resume facts; the model must stay inside them")
    company: str = Field(default="")
    role: str = Field(default="")
    tone: str = Field(default="professional")
    max_length_words: int = Field(default=280, ge=100, le=600)


class CoverLetterResponse(BaseModel):
    cover_letter: str
    model_used: str = Field(default="")
    warning: str = Field(default="")


# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #
class APIError(BaseModel):
    error: str
    detail: str = Field(default="")


class HealthResponse(BaseModel):
    status: str
    ai_primary: bool = False
    ai_fallback: bool = False
    rate_limiter: Literal["redis", "memory", "disabled"] = "memory"
