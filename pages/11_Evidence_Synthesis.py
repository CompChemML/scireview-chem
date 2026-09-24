from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.evidence import build_evidence_table
from scireview.models import ReviewProject
from scireview.synthesis import build_synthesis_summary, frequency_table


st.set_page_config(page_title="Evidence Synthesis | SciReview Chem", page_icon="📈", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project
table = build_evidence_table(project)
summary = build_synthesis_summary(table)

st.title("Evidence Synthesis")
st.caption("These are descriptive patterns from entered evidence. They are not automatically generated scientific conclusions.")
if not table.rows:
    st.info("No included studies are available for synthesis.")
    st.stop()

st.metric("Included studies", summary.study_count)
left, right = st.columns(2)
with left:
    st.subheader("Publication years")
    if summary.year_counts:
        years = pd.DataFrame({"Year": list(summary.year_counts), "Studies": list(summary.year_counts.values())})
        st.plotly_chart(px.bar(years, x="Year", y="Studies", color_discrete_sequence=["#2387C9"]), use_container_width=True)
    else:
        st.info("Publication years were not reported.")
with right:
    st.subheader("Missing-data pattern")
    missing = pd.DataFrame({"Field": list(summary.missing_counts), "Missing": list(summary.missing_counts.values())})
    missing = missing[missing["Missing"] > 0].sort_values("Missing", ascending=True)
    if not missing.empty:
        st.plotly_chart(px.bar(missing, x="Missing", y="Field", orientation="h", color_discrete_sequence=["#E7A63A"]), use_container_width=True)
    else:
        st.success("No missing values in the current evidence table.")

st.subheader("Study characteristic frequencies")
category = st.selectbox("Evidence field", [column for column in table.columns if column not in {"study_id", "title", "authors", "doi"}])
split_multi = st.checkbox("Split semicolon/comma-separated values", value=category in {"keywords", "equilibrium_models", "kinetic_models"})
frequencies = frequency_table(table, category, split_multi)
if frequencies:
    freq_frame = pd.DataFrame({"Value": list(frequencies), "Studies": list(frequencies.values())})
    st.dataframe(freq_frame, hide_index=True, use_container_width=True)
    st.plotly_chart(px.bar(freq_frame.head(25), x="Studies", y="Value", orientation="h", color_discrete_sequence=["#159E9C"]), use_container_width=True)
else:
    st.info("No reported values are available for this field.")

st.subheader("Researcher synthesis notes")
notes = st.text_area("Interpretation, evidence gaps, contradictions, and limitations", value=project.synthesis_notes, height=180,
                     help="The researcher remains responsible for deciding whether a pattern is a meaningful scientific gap.")
if st.button("Save synthesis notes", type="primary"):
    project.synthesis_notes = notes.strip()
    st.success("Synthesis notes saved in the current project.")

