"""DOCX parsing using python-docx.

Detects tables, inline images, and fonts, and extracts text in reading order
(paragraphs then table cells) so keyword scanning covers the whole document.
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.table import Table
from docx.text.paragraph import Paragraph

from .base import ParsedText
from ...utils.text import normalize_whitespace, word_count

_UNWANTED = {
    "header", "footer", "footnote", "endnote", "caption",
    "Page Number", "Empty Header", "Empty Footer",
}


def _iter_block_items(parent: DocxDocument):
    from docx.oxml.ns import qn

    parent_elm = parent.element.body
    for child in parent_elm.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


def _font_of(paragraph) -> str:
    try:
        for run in paragraph.runs:
            name = run.font.name
            if name:
                return name
    except Exception:
        pass
    try:
        rpr = paragraph._p.rPr
        if rpr is not None:
            from docx.oxml.ns import qn

            rfonts = rpr.find(qn("w:rFonts"))
            if rfonts is not None:
                name = rfonts.get(qn("w:ascii")) or rfonts.get(qn("w:hAnsi"))
                if name:
                    return name
    except Exception:
        pass
    return ""


def parse_docx(path: Path) -> ParsedText:
    result = ParsedText()
    doc = Document(str(path))

    parts: list[str] = []
    fonts: set[str] = set()

    def walk(tables: list[Table]) -> None:
        for table in tables:
            result.has_tables = True
            result.table_count += 1
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        if p.text.strip():
                            parts.append(p.text.strip())
                    walk(cell.tables)

    def inline_image_count(paragraph) -> int:
        try:
            from docx.oxml.ns import qn

            return len(paragraph._p.findall(".//" + qn("a:blip")))
        except Exception:
            return 0

    for block in _iter_block_items(doc):
        if isinstance(block, Paragraph):
            style = block.style.name if block.style else ""
            if style in _UNWANTED or style.startswith(("Header", "Footer")):
                continue
            if block.text.strip():
                parts.append(block.text.strip())
                fname = _font_of(block)
                if fname:
                    fonts.add(fname)
                if inline_image_count(block):
                    result.has_images = True
                    result.image_count += 1
        elif isinstance(block, Table):
            walk([block])

    result.text = "\n".join(parts)
    result.fonts_used = sorted(fonts)
    result.has_text_layer = bool(result.text.strip())
    result.scanned = not result.has_text_layer
    result.page_count = 1
    result.text = normalize_whitespace(result.text)
    result.word_count = word_count(result.text)
    return result
