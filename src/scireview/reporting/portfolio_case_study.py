from __future__ import annotations

from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from scireview.models import ReviewProject


NAVY = HexColor("#0B3558")
TEAL = HexColor("#159E9C")
BLUE = HexColor("#2387C9")
INK = HexColor("#102A43")
MUTED = HexColor("#627D98")
PALE = HexColor("#F7F9FC")
BORDER = HexColor("#D9E2EC")
AMBER = HexColor("#E7A63A")


def _wrap(text: str, font: str, size: float, width: float) -> list[str]:
    words = (text or "NR").split()
    lines: list[str] = []
    current = ""
    for word in words:
        proposed = f"{current} {word}".strip()
        if stringWidth(proposed, font, size) <= width:
            current = proposed
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _paragraph(canvas: Canvas, text: str, x: float, y: float, width: float, size: float = 11, leading: float = 15,
               font: str = "Helvetica", color=INK) -> float:
    canvas.setFont(font, size)
    canvas.setFillColor(color)
    for line in _wrap(text, font, size, width):
        canvas.drawString(x, y, line)
        y -= leading
    return y


def _heading(canvas: Canvas, text: str, x: float, y: float, size: float = 18) -> float:
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", size)
    canvas.drawString(x, y, text)
    return y - size - 8


def _footer(canvas: Canvas, page: int) -> None:
    width, _ = A4
    canvas.setStrokeColor(BORDER)
    canvas.line(46, 38, width - 46, 38)
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(46, 23, "SciReview Chem | Protocol-stage case study")
    canvas.drawRightString(width - 46, 23, str(page))


def _portrait_pages(project: ReviewProject) -> bytes:
    stream = BytesIO()
    canvas = Canvas(stream, pagesize=A4)
    width, height = A4
    margin = 52

    # Cover
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, height - 18, width, 18, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.setFillColor(white)
    canvas.drawString(margin, height - 72, "SCIREVIEW CHEM")
    canvas.setFont("Helvetica", 11)
    canvas.setFillColor(HexColor("#D9EAF2"))
    canvas.drawString(margin, height - 92, "Systematic Literature Review & Evidence Synthesis Workbench")
    y = height - 185
    canvas.setFont("Helvetica-Bold", 29)
    canvas.setFillColor(white)
    for line in _wrap(project.protocol.title, "Helvetica-Bold", 29, width - 2 * margin):
        canvas.drawString(margin, y, line)
        y -= 37
    y -= 22
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(4)
    canvas.line(margin, y, margin + 105, y)
    y -= 43
    canvas.setFont("Helvetica-Bold", 16)
    canvas.setFillColor(HexColor("#E7A63A"))
    canvas.drawString(margin, y, "PROTOCOL-STAGE CASE STUDY")
    y -= 31
    canvas.setFont("Helvetica", 12)
    canvas.setFillColor(white)
    for line in _wrap("A real scientific topic used to demonstrate review planning, eligibility criteria, database-specific search design, and auditable workflow status.", "Helvetica", 12, width - 2 * margin):
        canvas.drawString(margin, y, line)
        y -= 18
    y -= 35
    canvas.setFillColor(HexColor("#143F62"))
    canvas.roundRect(margin, y - 105, width - 2 * margin, 105, 10, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(margin + 20, y - 26, "CURRENT STATUS")
    canvas.setFont("Helvetica", 11)
    canvas.drawString(margin + 20, y - 49, "Protocol defined")
    canvas.drawString(margin + 190, y - 49, "Draft PubMed query recorded")
    canvas.drawString(margin + 20, y - 72, "References imported: 0")
    canvas.drawString(margin + 190, y - 72, "Evidence conclusions: none")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(HexColor("#B8CEDC"))
    canvas.drawString(margin, 35, "Prepared locally with SciReview Chem | Human-controlled evidence review")
    canvas.showPage()

    # Protocol
    _footer(canvas, 2)
    y = height - 58
    y = _heading(canvas, "1. Review protocol", margin, y, 22)
    canvas.setFillColor(PALE)
    canvas.setStrokeColor(BORDER)
    canvas.roundRect(margin, y - 92, width - 2 * margin, 92, 8, fill=1, stroke=1)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(TEAL)
    canvas.drawString(margin + 16, y - 23, "RESEARCH QUESTION")
    _paragraph(canvas, project.protocol.research_question, margin + 16, y - 45, width - 2 * margin - 32, 11.5, 15)
    y -= 118
    y = _heading(canvas, "Objective", margin, y, 16)
    y = _paragraph(canvas, project.protocol.objective, margin, y, width - 2 * margin, 11, 15)
    y -= 14
    y = _heading(canvas, "Scope framework", margin, y, 16)
    rows = [
        ("Material / system", project.protocol.population_or_material),
        ("Treatment / exposure", project.protocol.intervention_or_exposure),
        ("Comparator", project.protocol.comparator),
        ("Outcome", project.protocol.outcome),
    ]
    for label, value in rows:
        canvas.setFillColor(PALE)
        canvas.setStrokeColor(BORDER)
        canvas.roundRect(margin, y - 48, width - 2 * margin, 44, 5, fill=1, stroke=1)
        canvas.setFont("Helvetica-Bold", 9.5)
        canvas.setFillColor(NAVY)
        canvas.drawString(margin + 12, y - 20, label.upper())
        _paragraph(canvas, value, margin + 170, y - 20, width - 2 * margin - 183, 9.5, 12)
        y -= 54
    y -= 4
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(NAVY)
    canvas.drawString(margin, y, "SCOPE LIMITS")
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(INK)
    canvas.drawString(margin + 100, y, "2000-2026 | English | Primary experimental, peer-reviewed studies")
    canvas.showPage()

    # Eligibility + search
    _footer(canvas, 3)
    y = height - 58
    y = _heading(canvas, "2. Eligibility and search design", margin, y, 22)
    col_width = (width - 2 * margin - 18) / 2
    canvas.setFillColor(HexColor("#EAF6F4"))
    canvas.roundRect(margin, y - 185, col_width, 185, 8, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#FCEEEE"))
    canvas.roundRect(margin + col_width + 18, y - 185, col_width, 185, 8, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(TEAL)
    canvas.drawString(margin + 14, y - 25, "INCLUDE")
    left_y = y - 49
    for item in project.protocol.inclusion_criteria:
        left_y = _paragraph(canvas, f"- {item}", margin + 14, left_y, col_width - 28, 9.7, 13)
        left_y -= 4
    canvas.setFillColor(HexColor("#C94C4C"))
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(margin + col_width + 32, y - 25, "EXCLUDE")
    right_y = y - 49
    for item in project.protocol.exclusion_criteria:
        right_y = _paragraph(canvas, f"- {item}", margin + col_width + 32, right_y, col_width - 28, 9.7, 13)
        right_y -= 4
    y -= 220
    y = _heading(canvas, "Draft PubMed query", margin, y, 16)
    query = project.searches[0].exact_query if project.searches else "NR"
    query_lines = _wrap(query, "Courier", 9.5, width - 2 * margin - 30)
    box_height = max(96, 25 + len(query_lines) * 14)
    canvas.setFillColor(HexColor("#EEF4F8"))
    canvas.setStrokeColor(BLUE)
    canvas.roundRect(margin, y - box_height, width - 2 * margin, box_height, 7, fill=1, stroke=1)
    query_y = y - 25
    canvas.setFont("Courier", 9.5)
    canvas.setFillColor(INK)
    for line in query_lines:
        canvas.drawString(margin + 15, query_y, line)
        query_y -= 14
    y -= box_height + 23
    canvas.setFillColor(HexColor("#FFF5E5"))
    canvas.roundRect(margin, y - 72, width - 2 * margin, 72, 7, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(HexColor("#9A6414"))
    canvas.drawString(margin + 14, y - 22, "AUDIT NOTE")
    _paragraph(canvas, "This is a protocol-stage draft, not an executed search. Database field tags, search date, and retrieval count must be verified and recorded before screening begins.", margin + 14, y - 43, width - 2 * margin - 28, 10, 14, color=INK)
    canvas.showPage()

    # Boundaries / next steps (becomes page 5 after vector figure insertion)
    _footer(canvas, 5)
    y = height - 58
    y = _heading(canvas, "4. Interpretation boundaries and next steps", margin, y, 22)
    y = _heading(canvas, "What this case study demonstrates", margin, y, 16)
    demonstrated = ["A predefined, chemistry-appropriate research question", "Explicit inclusion and exclusion criteria",
                    "A database-specific Boolean search draft", "A state-derived PRISMA workflow with no invented counts",
                    "A reproducible local project file"]
    for item in demonstrated:
        canvas.setFillColor(TEAL)
        canvas.circle(margin + 4, y + 3, 3, fill=1, stroke=0)
        y = _paragraph(canvas, item, margin + 16, y, width - 2 * margin - 16, 11, 16)
        y -= 5
    y -= 13
    y = _heading(canvas, "What it does not claim", margin, y, 16)
    boundaries = ["No database search has yet been executed", "No references have been imported or screened",
                  "No study characteristics or quality judgments have been extracted", "No evidence synthesis or scientific conclusion has been produced"]
    for item in boundaries:
        canvas.setFillColor(AMBER)
        canvas.circle(margin + 4, y + 3, 3, fill=1, stroke=0)
        y = _paragraph(canvas, item, margin + 16, y, width - 2 * margin - 16, 11, 16)
        y -= 5
    y -= 18
    canvas.setFillColor(NAVY)
    canvas.roundRect(margin, y - 135, width - 2 * margin, 135, 8, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawString(margin + 18, y - 27, "NEXT WORKFLOW STEPS")
    next_steps = ["1. Adapt and execute the query in each selected database.", "2. Import legally obtained RIS, BibTeX, CSV, or XLSX exports.",
                  "3. Confirm duplicate candidates and screen every active record.", "4. Extract reported evidence, assess quality domains, and regenerate the report."]
    step_y = y - 51
    for item in next_steps:
        step_y = _paragraph(canvas, item, margin + 18, step_y, width - 2 * margin - 36, 10.5, 14, color=white)
        step_y -= 4
    canvas.save()
    return stream.getvalue()


def _prisma_vector_page(project: ReviewProject) -> bytes:
    fig, axis = plt.subplots(figsize=(11.69, 8.27), facecolor="white")
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    axis.text(0.06, 0.94, "3. PRISMA workflow status", fontsize=24, fontweight="bold", color="#0B3558", va="top")
    axis.text(0.06, 0.895, "Protocol stage - no records imported and no screening decisions recorded", fontsize=13, color="#627D98", va="top")
    boxes = [
        (0.07, 0.68, 0.34, 0.12, "Records identified\n0", "#2387C9"),
        (0.59, 0.68, 0.30, 0.12, "Duplicates removed\n0", "#E7A63A"),
        (0.07, 0.48, 0.34, 0.12, "Records screened\n0", "#159E9C"),
        (0.59, 0.48, 0.30, 0.12, "Records excluded\n0", "#C94C4C"),
        (0.07, 0.28, 0.34, 0.12, "Full texts assessed\n0", "#159E9C"),
        (0.59, 0.28, 0.30, 0.12, "Full texts excluded\n0", "#C94C4C"),
        (0.33, 0.08, 0.34, 0.12, "Studies included\n0", "#0B3558"),
    ]
    for x, y, w, h, label, color in boxes:
        axis.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.012", linewidth=2.2, edgecolor=color, facecolor="#F7F9FC"))
        axis.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=15, color="#102A43", linespacing=1.35)
    for start, end in [((0.24, 0.68), (0.24, 0.60)), ((0.24, 0.48), (0.24, 0.40)), ((0.24, 0.28), (0.45, 0.20))]:
        axis.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color="#0B3558", lw=2.1))
    for y in (0.74, 0.54, 0.34):
        axis.annotate("", xy=(0.59, y), xytext=(0.41, y), arrowprops=dict(arrowstyle="->", color="#627D98", lw=1.8))
    axis.text(0.95, 0.045, "SciReview Chem | 4", ha="right", fontsize=9, color="#627D98")
    stream = BytesIO()
    fig.savefig(stream, format="pdf", bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return stream.getvalue()


def export_portfolio_case_study(project: ReviewProject) -> bytes:
    portrait = PdfReader(BytesIO(_portrait_pages(project)))
    prisma = PdfReader(BytesIO(_prisma_vector_page(project)))
    writer = PdfWriter()
    writer.add_page(portrait.pages[0])
    writer.add_page(portrait.pages[1])
    writer.add_page(portrait.pages[2])
    writer.add_page(prisma.pages[0])
    writer.add_page(portrait.pages[3])
    output = BytesIO()
    writer.write(output)
    return output.getvalue()
