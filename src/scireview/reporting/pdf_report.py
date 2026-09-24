from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from scireview.evidence import build_evidence_table
from scireview.models import ReviewProject
from scireview.prisma import derive_prisma_counts, export_prisma_figure


def _text(value) -> str:
    if value is None or value == "" or value == []:
        return "NR"
    if isinstance(value, list):
        return "; ".join(map(str, value)) or "NR"
    return str(value)


def export_workflow_pdf(project: ReviewProject) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
                                 topMargin=18 * mm, bottomMargin=18 * mm,
                                 title=project.protocol.title or project.metadata.name)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], textColor=colors.HexColor("#0B3558"), alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], textColor=colors.HexColor("#0B3558"), spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))
    story = [Paragraph(project.protocol.title or project.metadata.name, styles["ReportTitle"]),
             Paragraph("SciReview Chem - Systematic Literature Review & Evidence Synthesis Workbench", styles["Heading3"]),
             Paragraph("This report documents the tracked workflow. It does not generate scientific conclusions or replace reviewer judgment.", styles["BodyText"]), Spacer(1, 8)]
    if project.metadata.demonstration:
        story.append(Paragraph("DEMONSTRATION DATA - NOT REAL RESEARCH EVIDENCE", ParagraphStyle(name="Demo", parent=styles["Heading2"], textColor=colors.HexColor("#C94C4C"), alignment=TA_CENTER)))
    sections = [
        ("Research question", project.protocol.research_question), ("Review objective", project.protocol.objective),
        ("Review type", project.protocol.review_type.replace("_", " ").title()),
        ("Scientific domain", project.protocol.scientific_domain),
        ("Inclusion criteria", project.protocol.inclusion_criteria), ("Exclusion criteria", project.protocol.exclusion_criteria),
    ]
    for heading, value in sections:
        story.extend([Paragraph(heading, styles["Section"]), Paragraph(_text(value), styles["BodyText"])])
    story.extend([Paragraph("Search strategy", styles["Section"]),
                  Table([["Database", "Date", "Records", "Exact query"]] + [[s.database, _text(s.search_date), _text(s.records_retrieved), Paragraph(s.exact_query, styles["Small"])] for s in project.searches], colWidths=[30*mm, 24*mm, 20*mm, 90*mm])])
    prisma = derive_prisma_counts(project)
    story.extend([PageBreak(), Paragraph("PRISMA flow", styles["Section"]),
                  Image(BytesIO(export_prisma_figure(prisma, "png", project.protocol.title or "PRISMA-style review flow")), width=165*mm, height=195*mm)])
    evidence = build_evidence_table(project)
    story.extend([PageBreak(), Paragraph("Included-study evidence", styles["Section"]),
                  Paragraph(f"Included studies: {len(evidence.rows)}. NR indicates not reported or not extracted and is not treated as zero.", styles["BodyText"])])
    compact = [column for column in ("title", "year", "journal", "doi", "key_findings", "limitations") if column in evidence.columns]
    if evidence.rows:
        data = [[Paragraph(column.replace("_", " ").title(), styles["Small"]) for column in compact]]
        data += [[Paragraph(_text(row.get(column)), styles["Small"]) for column in compact] for row in evidence.rows]
        table = Table(data, repeatRows=1, colWidths=[(174*mm)/max(1, len(compact))] * len(compact))
        table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0B3558")), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                                   ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#D9E2EC")), ("VALIGN", (0,0), (-1,-1), "TOP"),
                                   ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F7F9FC")])]))
        story.append(table)
    else:
        story.append(Paragraph("No studies are currently included.", styles["BodyText"]))
    story.extend([Paragraph("Researcher synthesis notes", styles["Section"]), Paragraph(_text(project.synthesis_notes), styles["BodyText"]),
                  Paragraph("Reproducibility information", styles["Section"]),
                  Paragraph(f"Project schema version: {project.schema_version}. Generated locally by SciReview Chem. Raw imported metadata and decision histories remain in the project file.", styles["BodyText"])])
    document.build(story)
    return output.getvalue()

