"""OCR fallback for scanned documents (pytesseract).

Optional dependency: if tesseract or pytesseract is unavailable, we degrade
gracefully and let the caller report a "no text layer" format issue.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_TESSERACT_OK = True
try:
    import pytesseract
    from PIL import Image
except Exception:  # pragma: no cover
    _TESSERACT_OK = False


def tesseract_available() -> bool:
    if not _TESSERACT_OK:
        return False
    try:
        from PIL import Image  # noqa: F401
        return True
    except Exception:
        return False


def ocr_images(images: list[tuple[bytes, str]]) -> tuple[str, float]:
    """Run OCR over a list of (bytes, format) images.

    Returns (concatenated_text, average_confidence).
    """
    if not _TESSERACT_OK:
        return "", 0.0

    parts: list[str] = []
    confs: list[float] = []
    try:
        import io

        import pytesseract
        from PIL import Image

        for raw, fmt in images:
            img = Image.open(io.BytesIO(raw))
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            text_parts = []
            for i, conf in enumerate(data["conf"]):
                try:
                    c = float(conf)
                    if c >= 0:
                        confs.append(c)
                except (TypeError, ValueError):
                    pass
                if data["text"][i] and data["text"][i].strip():
                    text_parts.append(data["text"][i])
            parts.append(" ".join(text_parts))
    except Exception as exc:  # pragma: no cover
        logger.warning("OCR run failed: %s", exc)
        return "", 0.0

    avg_conf = (sum(confs) / len(confs)) if confs else 0.0
    return "\n".join(p for p in parts if p.strip()), avg_conf
