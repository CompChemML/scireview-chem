from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.models import ReviewProject
from scireview.screening import (
    TITLE_ABSTRACT_EXCLUSION_REASONS, current_decisions, record_decision,
    screening_records, screening_summary,
)
from scireview.ui import render_protocol_criteria, render_record


st.set_page_config(page_title="Screening | SciReview Chem", page_icon="🗂️", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project
records = screening_records(project, "title_abstract")
current = current_decisions(project, "title_abstract")
summary = screening_summary(project, "title_abstract")

st.title("Title / Abstract Screening")
st.caption("Eligibility is a reviewer decision. Every new decision is appended to history; previous decisions are not overwritten.")
metrics = st.columns(5)
for column, label, value in zip(metrics, ("Total", "Pending", "Included", "Excluded", "Uncertain"),
                                (summary.total, summary.pending, summary.included, summary.excluded, summary.uncertain)):
    column.metric(label, value)

if not records:
    st.info("Import and deduplicate records before screening.")
    st.stop()

filter_label = st.selectbox("Show", ["All", "Pending", "Included", "Excluded", "Uncertain"])
filtered = []
for record in records:
    decision = current.get(record.id)
    state = decision.decision if decision else "pending"
    if filter_label == "All" or state == filter_label.casefold():
        filtered.append(record)
if not filtered:
    st.info(f"No {filter_label.casefold()} records in the current view.")
    st.stop()

position_key = f"screen_position_{filter_label}"
st.session_state[position_key] = min(st.session_state.get(position_key, 0), len(filtered) - 1)
nav_a, nav_b, nav_c = st.columns([1, 3, 1])
if nav_a.button("← Previous", disabled=st.session_state[position_key] == 0):
    st.session_state[position_key] -= 1
    st.rerun()
nav_b.markdown(f"<p style='text-align:center'>Record {st.session_state[position_key] + 1} of {len(filtered)}</p>", unsafe_allow_html=True)
if nav_c.button("Next →", disabled=st.session_state[position_key] == len(filtered) - 1):
    st.session_state[position_key] += 1
    st.rerun()

record = filtered[st.session_state[position_key]]
main, criteria = st.columns([3, 1])
with main:
    render_record(record)
with criteria:
    render_protocol_criteria(project.protocol)

existing = current.get(record.id)
if existing:
    st.info(f"Current decision: **{existing.decision.title()}**" + (f" — {existing.reason}" if existing.reason else ""))
reason = st.selectbox("Exclusion reason (required when excluding)", [""] + list(TITLE_ABSTRACT_EXCLUSION_REASONS))
custom_reason = st.text_input("Other exclusion reason", disabled=reason != "Other")
notes = st.text_area("Reviewer notes", value=existing.notes if existing else "")
reviewer = st.text_input("Reviewer name or initials", value=existing.reviewer if existing else "")
buttons = st.columns(3)
for column, label, value in zip(buttons, ("INCLUDE", "EXCLUDE", "UNCERTAIN"), ("include", "exclude", "uncertain")):
    if column.button(label, type="primary" if value == "include" else "secondary", use_container_width=True):
        selected_reason = custom_reason if reason == "Other" else reason
        try:
            record_decision(project, record.id, "title_abstract", value, selected_reason, notes, reviewer)
            if st.session_state[position_key] < len(filtered) - 1:
                st.session_state[position_key] += 1
            st.rerun()
        except ValueError as error:
            st.error(str(error))

history = [item for item in project.screening_decisions if item.record_id == record.id and item.stage == "title_abstract"]
with st.expander(f"Decision history ({len(history)})"):
    st.dataframe([{"Decision": item.decision, "Reason": item.reason, "Notes": item.notes,
                   "Reviewer": item.reviewer, "Timestamp": item.decided_at} for item in reversed(history)],
                 use_container_width=True, hide_index=True)
