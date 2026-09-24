from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.models import ReviewProject
from scireview.screening import (
    FULL_TEXT_EXCLUSION_REASONS, current_decisions, record_decision,
    screening_records, screening_summary,
)
from scireview.ui import render_protocol_criteria, render_record


st.set_page_config(page_title="Full-Text Review | SciReview Chem", page_icon="📄", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project
records = screening_records(project, "full_text")
current = current_decisions(project, "full_text")
summary = screening_summary(project, "full_text")

st.title("Full-Text Review")
st.caption("Only title/abstract includes and uncertain records enter this stage. Full-text exclusions require an explicit reason.")
metrics = st.columns(6)
for column, label, value in zip(metrics, ("Eligible", "Pending", "Included", "Excluded", "Uncertain", "Awaiting PDF"),
                                (summary.total, summary.pending, summary.included, summary.excluded, summary.uncertain, summary.awaiting_pdf)):
    column.metric(label, value)
if not records:
    st.info("No records are currently eligible. Complete title/abstract screening first.")
    st.stop()

filter_label = st.selectbox("Show", ["All", "Pending", "Included", "Excluded", "Uncertain", "Awaiting PDF"])
state_map = {"Awaiting PDF": "awaiting_pdf"}
target = state_map.get(filter_label, filter_label.casefold())
filtered = [record for record in records if filter_label == "All" or (current.get(record.id).decision if current.get(record.id) else "pending") == target]
if not filtered:
    st.info(f"No {filter_label.casefold()} records in the current view.")
    st.stop()

position_key = f"full_text_position_{filter_label}"
st.session_state[position_key] = min(st.session_state.get(position_key, 0), len(filtered) - 1)
nav_a, nav_b, nav_c = st.columns([1, 3, 1])
if nav_a.button("← Previous", disabled=st.session_state[position_key] == 0):
    st.session_state[position_key] -= 1; st.rerun()
nav_b.markdown(f"<p style='text-align:center'>Report {st.session_state[position_key] + 1} of {len(filtered)}</p>", unsafe_allow_html=True)
if nav_c.button("Next →", disabled=st.session_state[position_key] == len(filtered) - 1):
    st.session_state[position_key] += 1; st.rerun()

record = filtered[st.session_state[position_key]]
main, criteria = st.columns([3, 1])
with main:
    render_record(record)
    pdf_path = st.text_input("Local PDF filename or path reference", value=record.full_text_path or "",
                             help="SciReview Chem does not fetch or bypass access controls for articles.")
    if st.button("Save PDF reference"):
        record.full_text_path = pdf_path.strip() or None
        st.success("Local path reference saved. The file itself is not copied or uploaded.")
with criteria:
    render_protocol_criteria(project.protocol)

existing = current.get(record.id)
if existing:
    st.info(f"Current decision: **{existing.decision.replace('_', ' ').title()}**" + (f" — {existing.reason}" if existing.reason else ""))
reason = st.selectbox("Exclusion reason", [""] + list(FULL_TEXT_EXCLUSION_REASONS),
                      help="Required when the full text is excluded.")
custom_reason = st.text_input("Other exclusion reason", disabled=reason != "Other")
notes = st.text_area("Reviewer notes", value=existing.notes if existing else "")
reviewer = st.text_input("Reviewer name or initials", value=existing.reviewer if existing else "")
buttons = st.columns(4)
for column, label, value in zip(buttons, ("INCLUDE", "EXCLUDE", "UNCERTAIN", "AWAITING PDF"),
                                ("include", "exclude", "uncertain", "awaiting_pdf")):
    if column.button(label, type="primary" if value == "include" else "secondary", use_container_width=True):
        selected_reason = custom_reason if reason == "Other" else reason
        try:
            record_decision(project, record.id, "full_text", value, selected_reason, notes, reviewer)
            if st.session_state[position_key] < len(filtered) - 1:
                st.session_state[position_key] += 1
            st.rerun()
        except ValueError as error:
            st.error(str(error))

history = [item for item in project.screening_decisions if item.record_id == record.id and item.stage == "full_text"]
with st.expander(f"Decision history ({len(history)})"):
    st.dataframe([{"Decision": item.decision, "Reason": item.reason, "Notes": item.notes,
                   "Reviewer": item.reviewer, "Timestamp": item.decided_at} for item in reversed(history)],
                 use_container_width=True, hide_index=True)

