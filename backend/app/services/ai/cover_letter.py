"""JD-synced cover letter generation (fact-constrained)."""

from __future__ import annotations

import logging

from .client import get_ai_client
from .prompts import COVER_LETTER_SYSTEM, COVER_LETTER_USER
from ...models.schemas import CoverLetterRequest, CoverLetterResponse

logger = logging.getLogger(__name__)

_MAX_FACT_WORDS = 1500


def generate_cover_letter(req: CoverLetterRequest) -> CoverLetterResponse:
    facts = req.resume_summary.strip()
    warning = ""
    if not facts:
        warning = (
            "No resume text was provided, so this letter can only use the job "
            "description. For a strong letter, upload your resume first."
        )
        facts = "The candidate's resume was not uploaded. Write generically without inventing any facts."
    if len(facts.split()) > _MAX_FACT_WORDS:
        facts = " ".join(facts.split()[: _MAX_FACT_WORDS])
        warning = "Resume was truncated for the letter; only a summary was used."

    user_payload = COVER_LETTER_USER.format(
        jd=req.jd,
        resume_summary=facts,
        company=req.company.strip() or "the company",
        role=req.role.strip() or "this role",
        tone=req.tone,
        max_length_words=req.max_length_words,
    )
    client = get_ai_client()
    raw, model = client.chat(
        [
            {"role": "system", "content": COVER_LETTER_SYSTEM},
            {"role": "user", "content": user_payload},
        ],
        temperature=0.5,
        # Cap output tokens so reasoning models don't blow past the request
        # timeout producing long "thinking" chains. ~800 tokens ≈ 600 words.
        max_output_tokens=900,
    )
    return CoverLetterResponse(cover_letter=raw.strip(), model_used=model, warning=warning)
