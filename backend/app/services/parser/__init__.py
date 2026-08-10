"""Parse an uploaded resume file into structured text + format signals."""

from __future__ import annotations

from pathlib import Path

from .base import ParsedText
from .docx_parser import parse_docx
from .pdf_parser import parse_pdf
from ...core.config import get_settings


def parse_resume(path: Path, filename: str) -> ParsedText:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(path)
    if suffix == ".docx":
        return parse_docx(path)
    raise ValueError(
        f"Unsupported file type '{suffix or '(none)'}'. "
        f"Supported: {', '.join(get_settings().allowed_extensions)}"
    )
