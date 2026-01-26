import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
)
from reportlab.lib.units import mm


# ======================
# Helpers
# ======================

def strip_md(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"^\*\*(.+?)\*\*$", r"\1", text)
    text = re.sub(r"^\*(.+?)\*$", r"\1", text)
    text = re.sub(r"^#+\s*", "", text)
    return text.strip()

def is_section_title(line: str) -> bool:
    clean = strip_md(line)
    letters = [c for c in clean if c.isalpha()]
    return (
        len(clean) < 40
        and letters
        and all(c.upper() == c for c in letters)
    )

def split_cv_blocks(markdown_text: str):
    """
    Returns 3 blocks:
      - identity_lines: header + identity (until the blank line that follows identity)
      - intro_text: first paragraph after identity (merged into a single string)
      - body_lines: remaining lines (sections, bullets, etc.)
    """
    lines = markdown_text.splitlines()

    # 1) IDENTITY: from top until the blank line AFTER "Disponible immédiatement" block
    identity = []
    i = 0

    # consume leading empty lines (just in case)
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # take first line (header) + following lines until we hit an empty line
    # then keep consuming non-empty identity lines until next empty line ends identity
    while i < len(lines):
        identity.append(lines[i])
        i += 1
        # identity ends at the first empty line AFTER we have already collected some non-empty identity lines
        if i < len(lines) and lines[i].strip() == "" and len([x for x in identity if x.strip()]) >= 2:
            # consume exactly one empty line that separates identity from intro
            identity.append(lines[i])
            i += 1
            break

    # skip any extra empty lines between identity and intro
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # 2) INTRO: first paragraph (accumulate until blank line)
    intro_parts = []
    while i < len(lines) and lines[i].strip() != "":
        intro_parts.append(lines[i].strip())
        i += 1

    intro_text = " ".join(intro_parts).strip()

    # skip blank lines after intro
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # 3) BODY: rest
    body = lines[i:] if i < len(lines) else []

    return identity, intro_text, body


# ======================
# PDF Export
# ======================

def export_markdown_to_pdf(markdown_text: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    # ---------- Styles ----------

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=16,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=16,
        fontName="Helvetica-Bold",
    )

    identity_style = ParagraphStyle(
        "Identity",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        spaceAfter=2,
    )

    intro_style = ParagraphStyle(
        "Intro",
        parent=styles["Normal"],
        fontSize=11,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceBefore=8,
        spaceAfter=0,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=12,
        leading=12,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=4,
    )

    normal_style = ParagraphStyle(
        "NormalText",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=2,
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        leftIndent=6,
        spaceAfter=1,
    )

    story = []

    # ---------- Parsing ----------
    identity_lines, intro_text, body_lines = split_cv_blocks(markdown_text)

    # ---------- Header ----------
    header_line = strip_md(next(l for l in identity_lines if l.strip()))
    story.append(Paragraph(header_line, title_style))

    # ---------- Identity ----------
    started = False
    for line in identity_lines:
        clean = strip_md(line)
        if not clean:
            continue
        if not started:
            started = True
            continue  # skip header line
        story.append(Paragraph(clean, identity_style))

    # ---------- Intro ----------
    if intro_text:
        story.append(Spacer(1, 10))
        story.append(Paragraph(strip_md(intro_text), intro_style))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 8))

    # ---------- Body ----------
    bullets_buffer = []
    intro_done = False

    def flush_bullets():
        nonlocal bullets_buffer
        if bullets_buffer:
            story.append(
                ListFlowable(
                    [
                        ListItem(Paragraph(b, bullet_style))
                        for b in bullets_buffer
                    ],
                    bulletType="bullet",
                    start="•",
                    leftIndent=12,
                )
            )
            bullets_buffer = []

    for line in body_lines:
        raw = line.strip()

        if not raw:
            flush_bullets()
            story.append(Spacer(1, 6))
            continue

        # Section titles (ALL CAPS)
        if is_section_title(raw):
            flush_bullets()
            story.append(Paragraph(strip_md(raw), section_style))
            continue

        # Bullet
        if raw.startswith("•"):
            bullets_buffer.append(strip_md(raw[1:]))
            continue

        # Intro paragraph (first body paragraph only)
        if not intro_done:
            flush_bullets()
            story.append(Paragraph(strip_md(raw), intro_style))
            intro_done = True
            continue

        # Normal paragraph (LEFT aligned)
        flush_bullets()
        story.append(Paragraph(strip_md(raw), normal_style))

    flush_bullets()

    # ---------- Build ----------
    doc.build(story)
