from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.models import ReviewProject
from scireview.prisma import create_prisma_figure, derive_prisma_counts, export_prisma_figure


st.set_page_config(page_title="PRISMA Flow | SciReview Chem", page_icon="🔀", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project
counts = derive_prisma_counts(project)

st.title("PRISMA Flow")
st.caption("All counts are calculated from imported records, duplicate resolutions, and current screening decisions. They cannot be edited here.")

metrics = st.columns(5)
for column, label, value in zip(metrics,
                                ("Identified", "Duplicates removed", "Screened", "Full texts assessed", "Included"),
                                (counts.identified, counts.duplicates_removed, counts.records_screened, counts.full_texts_assessed, counts.studies_included)):
    column.metric(label, value)

if counts.reconciled:
    st.success("The tracked workflow is complete and its current categories reconcile.")
else:
    st.warning("The review is incomplete or requires reconciliation attention.")
    if counts.pending_title_abstract:
        st.write(f"- {counts.pending_title_abstract} active record(s) still need title/abstract screening.")
    if counts.pending_full_text:
        st.write(f"- {counts.pending_full_text} eligible report(s) still need a full-text decision.")
    for warning in counts.warnings:
        st.write(f"- {warning}")

title = project.protocol.title.strip() or "PRISMA-style review flow"
figure = create_prisma_figure(counts, title)
st.pyplot(figure, use_container_width=True)

st.subheader("Figure export")
downloads = st.columns(3)
for column, format, mime in zip(downloads, ("png", "svg", "pdf"), ("image/png", "image/svg+xml", "application/pdf")):
    column.download_button(
        f"Download {format.upper()}", export_prisma_figure(counts, format, title),
        f"scireview_prisma_flow.{format}", mime, use_container_width=True,
    )

left, right = st.columns(2)
with left:
    st.subheader("Title/abstract exclusion reasons")
    if counts.title_exclusion_reasons:
        st.dataframe([{"Reason": reason, "Records": value} for reason, value in counts.title_exclusion_reasons.items()],
                     use_container_width=True, hide_index=True)
    else:
        st.caption("No title/abstract exclusions recorded.")
with right:
    st.subheader("Full-text exclusion reasons")
    if counts.full_text_exclusion_reasons:
        st.dataframe([{"Reason": reason, "Reports": value} for reason, value in counts.full_text_exclusion_reasons.items()],
                     use_container_width=True, hide_index=True)
    else:
        st.caption("No full-text exclusions recorded.")

