"""PDF parsing.

Strategy:
1. pdfplumber -> text, tables, images, fonts (primary)
2. PyMuPDF (fitz) -> text fallback if pdfplumber yields nothing
3. pytesseract OCR -> scanned PDFs (no embedded text layer)

Privacy: the file is read from the caller-provided path and never copied
outside the request temp dir.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from .base import ParsedText
from ..temp_files import ensure_temp_root
from ...utils.text import normalize_whitespace, word_count

logger = logging.getLogger(__name__)

# Fonts that are safe for ATS parsing (rough heuristic).
_SAFE_FONTS = {"helvetica", "arial", "times", "calibri", "cambria", "garamond",
               "georgia", "verdana", "tahoma", "trebuchet", "open sans", "lato",
               "roboto", "source sans", "noto", "pt sans", "inter", "montserrat"}


def _font_key(name: str) -> str:
    return re.sub(r"[^a-z]+", " ", name.lower()).strip()


def _looks_like_columns(page) -> bool:
    """Heuristic: multiple vertical bands of text -> multi-column layout."""
    try:
        chars = page.chars
        if not chars:
            return False
        xs = [c["x0"] for c in chars]
        x0, x1 = min(xs), max(xs)
        width = x1 - x0
        if width <= 0:
            return False
        # Split into 4 equal bands and count chars in each.
        bands = [0.0] * 4
        for c in chars:
            idx = min(3, int(((c["x0"] - x0) / width) * 4))
            bands[idx] += 1
        total = sum(bands)
        if total == 0:
            return False
        # A two-column layout concentrates text in band 1 and 3.
        frac = [b / total for b in bands]
        return frac[1] < 0.15 and frac[2] > 0.15 and (frac[0] + frac[3]) > 0.3
    except Exception:
        return False


def parse_pdf(path: Path) -> ParsedText:
    result = ParsedText()
    try:
        result = _parse_with_pdfplumber(path)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("pdfplumber failed for %s: %s", path.name, exc)
        result.error = str(exc)[:300]

    # If nothing usable came out, try PyMuPDF.
    if not result.text.strip():
        try:
            result = _parse_with_fitz(path)
        except Exception as exc:  # pragma: no cover
            logger.warning("PyMuPDF failed for %s: %s", path.name, exc)
            result.error = result.error or str(exc)[:300]

    # Scanned fallback: no text layer at all -> OCR.
    if not result.text.strip() and result.page_count > 0:
        try:
            result = _ocr_pdf(path, result)
        except Exception as exc:  # pragma: no cover
            logger.warning("OCR failed for %s: %s", path.name, exc)
            result.error = result.error or str(exc)[:300]

    result.text = normalize_whitespace(result.text)
    result.word_count = word_count(result.text)
    return result


def _parse_with_pdfplumber(path: Path) -> ParsedText:
    import pdfplumber

    result = ParsedText()
    text_parts: list[str] = []
    fonts: set[str] = set()
    min_size, max_size = 0.0, 0.0

    with pdfplumber.open(str(path)) as pdf:
        result.page_count = len(pdf.pages)
        for page in pdf.pages:
            text = page.extract_text() or ""
            text_parts.append(text)
            try:
                if _looks_like_columns(page):
                    result.has_columns = True
            except Exception:
                pass
            try:
                tables = page.find_tables()
                if tables:
                    result.has_tables = True
                    result.table_count += len(tables)
            except Exception:
                pass
            try:
                imgs = page.images
                if imgs:
                    result.has_images = True
                    result.image_count += len(imgs)
            except Exception:
                pass
            try:
                for c in page.chars:
                    if c.get("size"):
                        size = float(c["size"])
                        min_size = min(min_size, size) if min_size else size
                        max_size = max(max_size, size)
                    fname = _font_key(c.get("fontname", ""))
                    if fname:
                        fonts.add(fname)
            except Exception:
                pass

    if text_parts:
        result.text = "\n".join(text_parts)
        result.has_text_layer = bool(result.text.strip())
        result.scanned = not result.has_text_layer
    else:
        result.has_text_layer = False
        result.scanned = True

    result.fonts_used = sorted(fonts)
    result.font_size_min = round(min_size, 1)
    result.font_size_max = round(max_size, 1)
    return result


def _parse_with_fitz(path: Path) -> ParsedText:
    import fitz  # PyMuPDF

    result = ParsedText()
    doc = fitz.open(str(path))
    result.page_count = doc.page_count
    parts: list[str] = []
    for page in doc:
        parts.append(page.get_text("text"))
    result.text = "\n".join(parts)
    result.has_text_layer = bool(result.text.strip())
    result.scanned = not result.has_text_layer
    # Image count
    try:
        count = 0
        for page in doc:
            count += len(page.get_images(full=True))
        if count:
            result.has_images = True
            result.image_count = count
    except Exception:
        pass
    doc.close()
    return result


def _ocr_pdf(path: Path, fallback: ParsedText) -> ParsedText:
    """Render pages to images with PyMuPDF, then run tesseract."""
    from .ocr import ocr_images
    import fitz

    images: list[tuple[bytes, str]] = []
    try:
        doc = fitz.open(str(path))
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            images.append((pix.tobytes("png"), "png"))
        doc.close()
    except Exception:
        return fallback

    if not images:
        return fallback

    text, conf = ocr_images(images)
    fallback.text = text
    fallback.was_ocr = True
    fallback.ocr_conf = round(conf, 1)
    fallback.has_text_layer = bool(text.strip())
    fallback.scanned = True
    return fallback
