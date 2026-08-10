"""Anonymized usage analytics for Supabase (optional).

PRIVACY: only aggregate/technical fields are sent (score, component scores,
counts, file type). We NEVER send resume text, JD text, keywords, or names.
If Supabase is not configured or the call fails, this is a silent no-op.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid

from ..core.config import get_settings

logger = logging.getLogger(__name__)

_SUPABASE_URL = "https://{ref}.supabase.co/rest/v1"
_MAX_QUEUE = 64


def _enabled() -> bool:
    s = get_settings()
    return bool(s.supabase_url and s.supabase_service_key)


def record_scan(scan_result) -> None:
    """Fire-and-forget analytics for one completed scan."""
    if not _enabled():
        return
    payload = {
        "event": "scan_completed",
        "ts": time.time(),
        "client_id": str(uuid.uuid4())[:16],  # random per event, not the IP
        "overall_score": scan_result.score.overall,
        "keyword_score": _component(scan_result, "keyword_match"),
        "format_score": _component(scan_result, "format_compat"),
        "section_score": _component(scan_result, "section_coverage"),
        "content_score": _component(scan_result, "content_quality"),
        "missing_keyword_count": len(scan_result.missing_keywords),
        "format_issue_count": len(scan_result.format_issues),
        "resume_words": scan_result.resume_word_count,
        "jd_words": scan_result.jd_word_count,
    }
    threading.Thread(target=_post, args=(payload,), daemon=True).start()


def _component(scan_result, name: str) -> float:
    for c in scan_result.score.components:
        if c.name == name:
            return c.score
    return 0.0


def _post(payload: dict) -> None:
    try:
        s = get_settings()
        url = f"{s.supabase_url}/rest/v1/analytics"
        headers = {
            "apikey": s.supabase_service_key,
            "Authorization": f"Bearer {s.supabase_service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        import urllib.request

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status >= 400:
                logger.debug("analytics post returned %s", resp.status)
    except Exception as exc:  # never break the scan flow
        logger.debug("analytics skipped: %s", exc)
