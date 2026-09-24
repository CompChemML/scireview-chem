from __future__ import annotations

from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

from .engine import PrismaCounts


NAVY = "#0B3558"
TEAL = "#159E9C"
BLUE = "#2387C9"
RED = "#C94C4C"
AMBER = "#E7A63A"
INK = "#102A43"
PALE = "#F7F9FC"
BORDER = "#D9E2EC"


def _reason_text(reasons: dict[str, int]) -> str:
    if not reasons:
        return ""
    return "\n" + "\n".join(f"{reason}: {count}" for reason, count in sorted(reasons.items()))


def create_prisma_figure(counts: PrismaCounts, title: str = "PRISMA-style review flow") -> Figure:
    fig, axis = plt.subplots(figsize=(11, 13), facecolor="white")
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    axis.text(0.5, 0.975, title, ha="center", va="top", fontsize=18, fontweight="bold", color=NAVY)
    axis.text(0.5, 0.947, "Counts derived from tracked records and current reviewer decisions", ha="center", va="top", fontsize=9, color="#627D98")

    boxes = [
        (0.08, 0.83, 0.52, 0.075, f"Records identified\nDatabases: {counts.database_records}   Other sources: {counts.other_source_records}", BLUE),
        (0.68, 0.83, 0.24, 0.075, f"Duplicates removed\n{counts.duplicates_removed}", AMBER),
        (0.08, 0.68, 0.52, 0.075, f"Records screened\n{counts.records_screened}", TEAL),
        (0.68, 0.68, 0.24, 0.075, f"Records excluded\n{counts.records_excluded}" + _reason_text(counts.title_exclusion_reasons), RED),
        (0.08, 0.53, 0.52, 0.075, f"Reports sought for retrieval\n{counts.reports_sought}", BLUE),
        (0.68, 0.53, 0.24, 0.075, f"Reports not retrieved / awaiting PDF\n{counts.reports_not_retrieved}", AMBER),
        (0.08, 0.38, 0.52, 0.075, f"Full texts assessed\n{counts.full_texts_assessed}", TEAL),
        (0.68, 0.35, 0.24, 0.13, f"Full texts excluded\n{counts.full_texts_excluded}" + _reason_text(counts.full_text_exclusion_reasons), RED),
        (0.20, 0.19, 0.52, 0.08, f"Studies included in evidence synthesis\n{counts.studies_included}", NAVY),
    ]
    for x, y, width, height, text, color in boxes:
        patch = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.008,rounding_size=0.01",
                               linewidth=1.5, edgecolor=color, facecolor=PALE)
        axis.add_patch(patch)
        axis.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=9,
                  color=INK, linespacing=1.25)
    for y_top, y_bottom in ((0.83, 0.755), (0.68, 0.605), (0.53, 0.455), (0.38, 0.27)):
        axis.annotate("", xy=(0.34, y_bottom), xytext=(0.34, y_top), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.6))
    for y in (0.867, 0.717, 0.567, 0.417):
        axis.annotate("", xy=(0.68, y), xytext=(0.60, y), arrowprops=dict(arrowstyle="->", color="#627D98", lw=1.3))
    status = "Reconciled and complete" if counts.reconciled else "Review in progress / reconciliation attention required"
    status_color = TEAL if counts.reconciled else AMBER
    axis.text(0.5, 0.11, status, ha="center", fontsize=10, color=status_color, fontweight="bold")
    if counts.pending_title_abstract or counts.pending_full_text:
        axis.text(0.5, 0.083,
                  f"Pending title/abstract: {counts.pending_title_abstract}   Pending full text: {counts.pending_full_text}",
                  ha="center", fontsize=9, color="#627D98")
    fig.tight_layout()
    return fig


def export_prisma_figure(counts: PrismaCounts, format: str, title: str = "PRISMA-style review flow") -> bytes:
    allowed = {"png", "svg", "pdf"}
    if format not in allowed:
        raise ValueError(f"Unsupported figure format: {format}")
    figure = create_prisma_figure(counts, title)
    stream = BytesIO()
    figure.savefig(stream, format=format, dpi=300 if format == "png" else None, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return stream.getvalue()

