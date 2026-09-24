from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from scireview.models import ReviewProject
from scireview.demo import DEMO_WARNING, build_demo_project
from scireview.prisma import derive_prisma_counts


st.set_page_config(page_title="SciReview Chem", page_icon="🔬", layout="wide")

st.markdown("""
<style>
:root { --navy:#0B3558; --teal:#159E9C; --ink:#102A43; --muted:#627D98; }
.stApp { background:#F7F9FC; color:var(--ink); }
.hero {padding:1.5rem 1.7rem;border-radius:14px;background:#0B3558;color:white;margin-bottom:1.2rem;}
.hero h1 {margin:0;font-size:2.05rem}.hero p{margin:.35rem 0 0;color:#D9EAF2}
[data-testid="stMetric"] {background:white;border:1px solid #D9E2EC;border-radius:10px;padding:1rem;}
</style>
""", unsafe_allow_html=True)

if "project" not in st.session_state:
    st.session_state.project = ReviewProject()

project: ReviewProject = st.session_state.project
counts = derive_prisma_counts(project)

st.markdown('<section class="hero"><h1>SciReview Chem</h1><p>From Search Strategy to Defensible Evidence</p></section>', unsafe_allow_html=True)
st.caption("Systematic Literature Review & Evidence Synthesis Workbench · local-first · human-controlled")

st.subheader("Start a review")
with st.form("topic_quick_start"):
    topic = st.text_input(
        "Review topic",
        value=project.protocol.title,
        placeholder="e.g., Iron-oxide-modified biochar for arsenic removal from groundwater",
        help="This creates the project topic. SciReview Chem does not automatically search external databases.",
    )
    research_question = st.text_area(
        "Research question (optional)",
        value=project.protocol.research_question,
        placeholder="How do modification methods, water chemistry, and regeneration affect arsenic adsorption?",
        height=90,
    )
    start_review = st.form_submit_button("Save topic and start review", type="primary")
if start_review:
    if not topic.strip():
        st.error("Enter a review topic before starting.")
    else:
        project.protocol.title = topic.strip()
        project.protocol.research_question = research_question.strip()
        project.metadata.name = topic.strip()
        st.success("Topic saved. Continue with Review Protocol, then build database-specific queries in Search Strategy.")

cols = st.columns(4)
cols[0].metric("Records identified", counts.identified)
cols[1].metric("Duplicates removed", counts.duplicates_removed)
cols[2].metric("Records screened", counts.records_screened)
cols[3].metric("Studies included", counts.studies_included)

st.subheader("Review progress")
phases = ["Question", "Search", "Import", "Deduplicate", "Screen", "Extract", "Assess", "Synthesize", "Report"]
st.markdown(" &nbsp; → &nbsp; ".join(f"**{p}**" if p == "Question" else p for p in phases))

left, right = st.columns([2, 1])
with left:
    st.info("Start with a review protocol. Counts remain zero until real or explicitly labelled demonstration records are imported.")
    if st.button("Load fictional demonstration project"):
        st.session_state.project = build_demo_project()
        st.rerun()
    if project.metadata.demonstration:
        st.error(DEMO_WARNING)
    st.subheader("Scientific integrity")
    st.write("Inclusion, exclusion, quality assessment, and interpretation remain reviewer decisions. Raw metadata and decision history are preserved.")
with right:
    st.subheader("Current project")
    st.write(project.metadata.name)
    st.write("Current phase: **Protocol**")
    st.write(f"Schema version: `{project.schema_version}`")
