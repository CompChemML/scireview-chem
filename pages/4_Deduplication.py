from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.deduplication import apply_resolution, find_duplicate_candidates
from scireview.models import ReviewProject


st.set_page_config(page_title="Deduplication | SciReview Chem", page_icon="🧩", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project

st.title("Deduplication")
st.caption("Identifier and title matching proposes candidates. Only a reviewer can deactivate or merge a record; imported records and the audit trail remain preserved.")

top_a, top_b, top_c = st.columns(3)
top_a.metric("Records imported", len(project.records))
top_b.metric("Records active", sum(record.active for record in project.records))
top_c.metric("Candidates unresolved", sum(item.resolution is None for item in project.duplicate_candidates))

threshold = st.slider("Fuzzy-title candidate threshold", min_value=70, max_value=100, value=88,
                      help="Lower thresholds create more reviewer work and do not cause automatic deletion.")
if st.button("Scan active records for duplicate candidates", type="primary", disabled=len(project.records) < 2):
    existing_resolutions = {
        frozenset((item.record_a_id, item.record_b_id)): item
        for item in project.duplicate_candidates if item.resolution is not None
    }
    detected = find_duplicate_candidates(project.records, float(threshold))
    project.duplicate_candidates = [
        existing_resolutions.get(frozenset((item.record_a_id, item.record_b_id)), item)
        for item in detected
    ]
    st.success(f"Found {len(detected)} candidate pair(s). No records were automatically removed.")

records = {record.id: record for record in project.records}
unresolved = [item for item in project.duplicate_candidates if item.resolution is None]
resolved = [item for item in project.duplicate_candidates if item.resolution is not None]

if unresolved:
    index = st.number_input("Candidate", min_value=1, max_value=len(unresolved), value=1) - 1
    candidate = unresolved[index]
    left, right = records[candidate.record_a_id], records[candidate.record_b_id]
    st.subheader(f"{candidate.classification.title()} duplicate candidate")
    st.write(" · ".join(candidate.reasons))
    st.progress(candidate.similarity_score / 100, text=f"Title similarity {candidate.similarity_score:.1f}%")
    col_a, col_b = st.columns(2)
    for column, heading, record in ((col_a, "Left record", left), (col_b, "Right record", right)):
        with column:
            st.markdown(f"### {heading}")
            st.markdown(f"**{record.title or 'NR'}**")
            st.write(f"Authors: {'; '.join(record.authors) or 'NR'}")
            st.write(f"Year: {record.year or 'NR'}")
            st.write(f"Journal: {record.journal or 'NR'}")
            st.write(f"DOI: {record.doi or 'NR'}")
            st.write(f"Source: {record.source_database or 'NR'}")
            st.caption(f"Internal ID: {record.id}")
    reviewer = st.text_input("Reviewer name or initials (optional)")
    actions = st.columns(4)
    choices = (("Keep left", "keep_a"), ("Keep right", "keep_b"), ("Merge into left", "merge"), ("Keep both", "keep_both"))
    for column, (label, value) in zip(actions, choices):
        if column.button(label, use_container_width=True):
            apply_resolution(project, candidate.id, value, reviewer)
            st.rerun()
elif project.duplicate_candidates:
    st.success("All detected candidates have a reviewer resolution.")
else:
    st.info("Import at least two records, then scan for candidate duplicates.")

if resolved:
    st.subheader("Resolution audit log")
    st.dataframe([{
        "Left record": records[item.record_a_id].title,
        "Right record": records[item.record_b_id].title,
        "Classification": item.classification,
        "Resolution": item.resolution,
        "Reviewer": item.reviewer or "Not recorded",
        "Resolved at": item.resolved_at,
        "Evidence": "; ".join(item.reasons),
    } for item in resolved], use_container_width=True, hide_index=True)

