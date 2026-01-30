from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import mm


def export_letter_to_pdf(markdown_text: str, output_path: str):
    """
    Export a motivation letter (markdown-like plain text) to a styled PDF.
    Assumptions:
    - No markdown fencing (``` already stripped)
    - Blocks are separated by empty lines
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=25 * mm,
        leftMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )

    # ---------- Styles ----------
    date_style = ParagraphStyle(
        "DateStyle",
        alignment=TA_LEFT,
        fontSize=11,
        spaceAfter=14,
    )

    recipient_style = ParagraphStyle(
        "RecipientStyle",
        alignment=TA_RIGHT,
        fontSize=11,
        spaceAfter=18,
    )

    object_style = ParagraphStyle(
        "ObjectStyle",
        alignment=TA_LEFT,
        fontSize=11,
        spaceAfter=14,
        fontName="Helvetica-Bold",
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=14,
        spaceAfter=12,
    )

    closing_style = ParagraphStyle(
        "ClosingStyle",
        alignment=TA_LEFT,
        fontSize=11,
        spaceBefore=18,
    )

    signature_style = ParagraphStyle(
        "SignatureStyle",
        alignment=TA_LEFT,
        fontSize=11,
        spaceBefore=12,
    )

    # ---------- Pre-processing ----------
    lines = [l.rstrip() for l in markdown_text.strip().splitlines()]

    blocks = []
    current = []

    for line in lines:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)

    if current:
        blocks.append(current)

    story = []

    # ---------- Expected structure ----------
    # block 0: date / location
    # block 1: recipient (right aligned)
    # block 2: object
    # block 3+: body paragraphs + closing + signature

    if len(blocks) < 4:
        raise ValueError("Letter structure invalid: not enough blocks")

    # Date / location
    story.append(Paragraph(blocks[0][0], date_style))
    story.append(Spacer(1, 10))

    # Recipient block (right aligned)
    recipient_text = "<br/>".join(blocks[1])
    story.append(Paragraph(recipient_text, recipient_style))

    # Object
    story.append(Paragraph(blocks[2][0], object_style))
    story.append(Spacer(1, 10))

    # Body + closing + signature
    for block in blocks[3:]:
        text = "<br/>".join(block)

        # Detect signature block (very last block)
        if block == blocks[-1]:
            story.append(Paragraph(text, signature_style))
        else:
            story.append(Paragraph(text, body_style))

    # ---------- Build ----------
    doc.build(story)
