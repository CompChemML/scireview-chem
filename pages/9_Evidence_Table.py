from pathlib import Path
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.evidence import build_evidence_table, filter_evidence_rows
from scireview.models import ReviewProject


st.set_page_config(page_title="Evidence Table | SciReview Chem", page_icon="📊", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project
table = build_evidence_table(project)

st.title("Evidence Table")
st.caption("Only studies included at full-text review appear here. NR means not reported or not extracted; it never means zero.")
if not table.rows:
    st.info("No included studies are available for the evidence table.")
    st.stop()

search = st.text_input("Search all evidence fields")
available_columns = list(table.columns)
default_columns = [column for column in available_columns if column != "study_id"]
selected_columns = st.multiselect("Columns", available_columns, default=default_columns)
filter_columns = st.multiselect("Add categorical filters", [column for column in available_columns if column not in {"study_id", "title", "authors"}])
filters = {}
for column in filter_columns:
    options = sorted({str(row.get(column)) for row in table.rows})
    filters[column] = set(st.multiselect(f"Filter: {column.replace('_', ' ').title()}", options))

rows = filter_evidence_rows(table, search, filters)
frame = pd.DataFrame(rows)
if selected_columns:
    frame = frame[[column for column in selected_columns if column in frame.columns]]
st.write(f"Showing {len(frame)} of {len(table.rows)} included studies")
st.dataframe(frame, use_container_width=True, hide_index=True)

csv_bytes = frame.to_csv(index=False).encode("utf-8-sig")
st.download_button("Download current view as CSV", csv_bytes, "scireview_evidence_table.csv", "text/csv")

if not frame.empty:
    missing = (frame.astype(str).apply(lambda column: column.str.strip().str.casefold().isin({"nr", "", "none", "nan"}))).sum()
    with st.expander("Missing-data counts in current view"):
        st.dataframe(pd.DataFrame({"Field": missing.index, "Missing / NR": missing.values}), hide_index=True, use_container_width=True)
