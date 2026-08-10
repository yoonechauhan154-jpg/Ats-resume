"""Analyze endpoint: upload resume + JD text, return the full ATS report.

Security / privacy guarantees enforced here:
- file type is validated by extension AND by actual magic bytes (so a
  renamed .txt cannot bypass validation),
- uploads over the size limit are rejected before parsing,
- the JD text is capped at 10,000 characters,
- the upload is written to a throwaway per-request temp dir,
- it is deleted in a `finally` block immediately after processing,
- only the parsed *text* (never the file) is used for scoring,
- we never persist resume content anywhere.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile

from ..deps import enforce_rate_limit, rate_limit_headers
from ...core.config import get_settings
from ...models.schemas import ScanResponse
from ...services.parser import parse_resume
from ...services.scoring.scorer import run_scan
from ...services.analytics import record_scan
from ...services.temp_files import (
    delete_request_dir,
    make_request_dir,
    sweep_orphans,
    write_upload,
)

logger = logging.getLogger(__name__)

JD_MAX_CHARS = 10_000

# Magic bytes used to verify the *actual* file format, not just the extension.
_PDF_MAGIC = b"%PDF-"
_DOCX_MAGIC = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")  # ZIP / OOXML container

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=ScanResponse)
async def analyze_resume(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    jd: str = Form(...),
) -> ScanResponse:
    await enforce_rate_limit(request)
    settings = get_settings()
    sweep_orphans()

    filename = file.filename or ""
    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename.")

    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Please upload a .pdf or .docx resume.",
        )

    jd = (jd or "").strip()
    if len(jd) < 20:
        raise HTTPException(
            status_code=400,
            detail="The job description looks too short (min 20 characters). Paste the full JD text.",
        )
    if len(jd) > JD_MAX_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"The job description is too long (max {JD_MAX_CHARS:,} characters).",
        )

    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.max_upload_mb}MB limit.",
        )
    if not _matches_magic_bytes(data, ext):
        raise HTTPException(
            status_code=400,
            detail=(
                f"The file '{filename}' does not look like a real {ext[1:].upper()} "
                "file (magic bytes don't match). Renaming another file type will "
                "not bypass validation."
            ),
        )

    request_dir = make_request_dir()
    try:
        path = write_upload(request_dir, filename, data)
        parsed = parse_resume(path, filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # parse failure
        logger.exception("resume parse failed")
        raise HTTPException(status_code=422, detail=f"Could not parse the resume: {exc}")
    finally:
        # Privacy: remove the file immediately, before any further work.
        if settings.delete_after_scan:
            delete_request_dir(request_dir)

    result = run_scan(jd, parsed)

    # Expose quota to the client.
    for k, v in (await rate_limit_headers(request)).items():
        response.headers[k] = v

    # Anonymous analytics (never contains resume content).
    record_scan(result)

    return result


def _matches_magic_bytes(data: bytes, ext: str) -> bool:
    """Verify the file's header matches its claimed extension."""
    if ext == ".pdf":
        return data.startswith(_PDF_MAGIC)
    if ext == ".docx":
        return any(data.startswith(m) for m in _DOCX_MAGIC)
    return False
