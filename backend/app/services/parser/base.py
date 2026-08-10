"""Parsing result data structure shared by all parsers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedText:
    """Normalized output of a resume/document parser."""

    text: str = ""
    page_count: int = 1
    word_count: int = 0
    # format signals collected while parsing
    has_tables: bool = False
    table_count: int = 0
    has_columns: bool = False
    has_images: bool = False
    image_count: int = 0
    fonts_used: list[str] = field(default_factory=list)
    font_size_min: float = 0.0
    font_size_max: float = 0.0
    has_text_layer: bool = True
    was_ocr: bool = False
    ocr_conf: float = 0.0
    scanned: bool = False
    textboxes: int = 0
    watermarks: list[str] = field(default_factory=list)
    error: Optional[str] = None
