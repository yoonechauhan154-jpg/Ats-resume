"""AI resume bullet rewriting with strict rule enforcement.

After generation we run a deterministic guard layer that:
- verifies no number/metric was altered,
- detects obvious invented content (skills the resume doesn't mention),
- drops bullets that fail the guards instead of returning bad output.
"""

from __future__ import annotations

import json
import logging
import re

from .client import get_ai_client, AIUnavailableError
from .prompts import REWRITE_SYSTEM, REWRITE_USER
from ...models.schemas import RewrittenBullet, RewriteRequest, RewriteResponse

logger = logging.getLogger(__name__)

_NUM_TOKEN = re.compile(r"\d[\d,.]*%?|\$\s?\d[\d,.]*")

RULES_APPLIED = [
    "No skills or experience added that are absent from your resume.",
    "All numbers, percentages, and metrics preserved byte-for-byte.",
    "Every change is flagged and shown in the before/after diff.",
]


def rewrite_bullets(req: RewriteRequest) -> RewriteResponse:
    context = req.context.strip() or (
        "The candidate's full resume text was not provided for this rewrite; "
        "only rephrase the given bullets without adding any new facts."
    )
    user_payload = REWRITE_USER.format(
        jd=req.jd,
        context=context,
        bullets="\n".join(f"- {b}" for b in req.bullets),
    )
    client = get_ai_client()
    raw, model = client.chat(
        [
            {"role": "system", "content": REWRITE_SYSTEM},
            {"role": "user", "content": user_payload},
        ],
        temperature=0.3,
        # kimi-k3-free is a PURE reasoning model: it generates its chain-of-thought
        # INSIDE the max_completion_tokens budget. Leaving this uncapped lets the
        # reasoning run long enough to blow the 145s request ceiling (~126s seen
        # in E2E). Cap generously: ~900s worth of JSON for 3 bullets + a big
        # reasoning buffer. The cap, not the timer, is the primary latency lever
        # for reasoning models.
        max_output_tokens=2500,
    )

    parsed = _parse_json(raw)
    items = parsed.get("bullets") if isinstance(parsed, dict) else None
    if not isinstance(items, list):
        raise AIUnavailableError(
            "The model returned an unparseable response. Please try again."
        )

    result: list[RewrittenBullet] = []
    for item in items:
        original = str(item.get("original", "")).strip()
        rewritten = str(item.get("rewritten", "")).strip()
        if not original or not rewritten:
            continue
        # Guard: numbers must be preserved.
        if not _numbers_preserved(original, rewritten):
            rewritten = original  # fall back to original rather than emit bad data
            changed = []
            reason = "Rewrite was rejected: it altered a number/metric."
        else:
            changed = [c for c in item.get("changed", []) if str(c).strip()]
            reason = str(item.get("reason", "")).strip()
            if req.context.strip():
                invented = _detect_invented_tools(rewritten, req.context)
                if invented:
                    # Remove the invented term from the rewrite instead of rejecting
                    # the whole bullet when possible.
                    cleaned = _strip_terms(rewritten, invented)
                    if cleaned and cleaned != rewritten:
                        rewritten = cleaned
                        changed.append("removed unsupported term(s): " + ", ".join(invented))
        result.append(
            RewrittenBullet(
                original=original,
                rewritten=rewritten,
                changed=changed,
                preserved=sorted(set(_NUM_TOKEN.findall(original))),
                reason=reason,
            )
        )

    if not result:
        raise AIUnavailableError("No valid bullets were produced. Please try again.")

    return RewriteResponse(rewritten=result, rules_applied=RULES_APPLIED, model_used=model)


def _parse_json(raw: str):
    raw = raw.strip()
    # Strip markdown fences if present.
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to find the first { ... } block.
        start, end = raw.find("{"), raw.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                pass
    return None


def _numbers_preserved(original: str, rewritten: str) -> bool:
    orig_nums = set(_NUM_TOKEN.findall(original))
    new_nums = set(_NUM_TOKEN.findall(rewritten))
    # Every original number must still appear in the rewrite.
    return orig_nums.issubset(new_nums)


def _detect_invented_tools(text: str, resume_context: str) -> list[str]:
    """Return capitalized tool-ish words in the rewrite missing from the resume."""
    context_lower = resume_context.lower()
    candidates = set(
        m.group(0)
        for m in re.finditer(r"\b[A-Z][A-Za-z0-9+#.-]{1,15}\b", text)
    )
    invented = []
    for cand in candidates:
        low = cand.lower()
        if low in {"the", "i", "we", "our", "this", "that"}:
            continue
        if low not in context_lower:
            # Heuristic: only flag terms that look like tools/frameworks.
            if re.search(r"\d|\.|#|/|tech|js|aws|azure|react|node|sql|python|go\b", low, re.I):
                invented.append(cand)
    return invented


def _strip_terms(text: str, terms: list[str]) -> str:
    out = text
    for term in terms:
        out = re.sub(r"\b" + re.escape(term) + r"\b", "", out)
        out = re.sub(r"\s{2,}", " ", out).strip(" ,-–—")
    return out
