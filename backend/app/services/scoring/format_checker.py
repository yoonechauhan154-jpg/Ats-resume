"""Format compatibility analysis for ATS parsing.

Transparent rules that explain *why* each detected issue can hurt ATS rank and
exactly how to fix it.
"""

from __future__ import annotations

from ..parser.base import ParsedText
from ...models.schemas import FormatIssue, FormatIssueType, Severity


def analyze_format(parsed: ParsedText, resume_word_count: int) -> tuple[list[FormatIssue], float]:
    """Returns (issues, format_score 0-100)."""
    issues: list[FormatIssue] = []
    score = 100.0

    # --- Critical: no extractable text (scanned / image-only) ---
    if parsed.scanned or not parsed.has_text_layer:
        issues.append(
            FormatIssue(
                type=FormatIssueType.scanned,
                severity=Severity.critical,
                title="Scanned / image-only document (no selectable text)",
                description=(
                    "Your resume is an image without a text layer. ATS software "
                    "cannot read it at all, so it may be dropped or require an "
                    "expensive OCR step that often corrupts the content."
                ),
                ats_impact="Zero extractable text: the resume can't be keyword-matched.",
                fix=(
                    "Export your resume to PDF using 'File > Save As' (not 'Print to "
                    "PDF' from a scanner). Paste text into a text editor and confirm "
                    "you can select it with your cursor."
                ),
            )
        )
        score -= 60

    # --- Tables ---
    if parsed.has_tables:
        issues.append(
            FormatIssue(
                type=FormatIssueType.table,
                severity=Severity.critical if parsed.table_count > 2 else Severity.warning,
                title=f"Tables detected ({parsed.table_count})",
                description=(
                    "Tables scramble the reading order of text for many ATS parsers, "
                    "which can split or merge your skills and job titles."
                ),
                ats_impact="Parsers may reorder or drop text inside table cells.",
                fix=(
                    "Convert tables to plain single-column text with bullet points. "
                    "Keep 'Skills' as a comma-separated list, not a grid."
                ),
            )
        )
        score -= 25 if parsed.table_count > 2 else 12

    # --- Multi-column layout ---
    if parsed.has_columns:
        issues.append(
            FormatIssue(
                type=FormatIssueType.columns,
                severity=Severity.warning,
                title="Two-column layout detected",
                description=(
                    "Two-column resumes are read left-to-right by some parsers, "
                    "mixing content from both columns into unreadable lines."
                ),
                ats_impact="Keywords can end up garbled or merged across columns.",
                fix=(
                    "Use a single-column layout: sections stacked top to bottom. "
                    "This is the most ATS-safe structure."
                ),
            )
        )
        score -= 12

    # --- Images ---
    if parsed.has_images and not parsed.scanned:
        issues.append(
            FormatIssue(
                type=FormatIssueType.image,
                severity=Severity.warning,
                title=f"Embedded images detected ({parsed.image_count})",
                description=(
                    "Photos, logos and icon graphics add visual flair but ATS "
                    "parsers ignore them, and a photo can trigger bias filters."
                ),
                ats_impact="Images carry no text; they add no keywords and bloat the file.",
                fix="Remove photos and logos. Only keep images if they are actual content.",
            )
        )
        score -= 8

    # --- Unusual fonts ---
    unsafe = [f for f in parsed.fonts_used if f and not _safe_font(f)]
    if unsafe:
        issues.append(
            FormatIssue(
                type=FormatIssueType.font,
                severity=Severity.warning,
                title="Unusual fonts detected",
                description=(
                    "Fonts that don't embed properly can turn characters into "
                    "'glyphs' that parse as garbage or blank space."
                ),
                ats_impact="Garbled characters lower the readable word count and can break keyword matching.",
                fix=f"Switch to a standard font (e.g. Arial, Calibri, Georgia, Helvetica). Detected: {', '.join(unsafe[:3])}.",
            )
        )
        score -= 6

    # --- Very small font ---
    if 0 < parsed.font_size_min < 8:
        issues.append(
            FormatIssue(
                type=FormatIssueType.font,
                severity=Severity.warning,
                title=f"Small font size detected ({parsed.font_size_min}pt)",
                description=(
                    "Very small text can be mis-read by OCR-based ATS parsers."
                ),
                ats_impact="Characters below 8pt are commonly mis-extracted.",
                fix="Use body text of 10-12pt.",
            )
        )
        score -= 5

    # --- Missing contact info ---
    if _missing_contact(parsed.text):
        issues.append(
            FormatIssue(
                type=FormatIssueType.missing_contact,
                severity=Severity.warning,
                title="Contact details not detected",
                description=(
                    "We could not find an email or phone number. Recruiters and "
                    "ATS systems need them to route the application."
                ),
                ats_impact="Applications without contact info are often auto-rejected.",
                fix="Add an email address and phone number near your name at the top.",
            )
        )
        score -= 8

    # --- Too short ---
    if 0 < resume_word_count < 200:
        issues.append(
            FormatIssue(
                type=FormatIssueType.too_short,
                severity=Severity.info,
                title="Resume appears very short",
                description=(
                    "Under ~200 words most ATS keyword matchers have very little "
                    "content to score against."
                ),
                ats_impact="Fewer words -> fewer possible keyword matches.",
                fix="Expand with concrete, quantified achievements (only facts from your actual experience).",
            )
        )
        score -= 5

    if parsed.was_ocr:
        issues.append(
            FormatIssue(
                type=FormatIssueType.no_text_layer,
                severity=Severity.warning,
                title="Processed via OCR (no original text layer)",
                description=(
                    "Your PDF had no selectable text, so we ran OCR. OCR text is "
                    "lower fidelity and ATS may do the same."
                ),
                ats_impact="OCR mistakes can corrupt skill names (e.g. 'Node.js' -> 'Nodeis').",
                fix="Regenerate the PDF with real text (see 'Scanned document' fix above).",
            )
        )
        score -= 8

    return issues, max(0.0, round(score, 1))


def _safe_font(font: str) -> bool:
    base = font.split("bold")[0].split("italic")[0].split("regular")[0].strip()
    safe = {
        "helvetica", "arial", "arialmt", "times", "timesnewroman", "timesroman",
        "calibri", "cambria", "georgia", "verdana", "tahoma", "trebuchetms",
        "garamond", "courier", "couriernew", "liberation", "opensans", "lato",
        "roboto", "source", "noto", "pt", "inter", "montserrat", "carlito",
        "dejavu", "freesans", "droidsans",
    }
    return any(s in base.replace(" ", "").lower() for s in safe)


def _missing_contact(text: str) -> bool:
    import re

    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
    has_phone = bool(re.search(r"(?<!\d)\+?\d[\d\s().-]{6,}\d(?!\d)", text))
    return not (has_email or has_phone)
