from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.extraction import included_records
from scireview.models import ReviewProject
from scireview.quality import DEFAULT_QUALITY_DOMAINS, upsert_quality_assessment


st.set_page_config(page_title="Quality Assessment | SciReview Chem", page_icon="⚖️", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project
records = included_records(project)

st.title("Quality / Bias Assessment")
st.warning("Quality assessment depends on review context and study design. SciReview Chem records domain-level judgments and does not calculate a universal authoritative score.")
if not records:
    st.info("No included full-text studies are available for assessment.")
    st.stop()

labels = {record.id: f"{record.title or 'Untitled'} ({record.year or 'year NR'})" for record in records}
record_id = st.selectbox("Included study", list(labels), format_func=labels.get)
existing = next((item for item in project.quality_assessments if item.record_id == record_id), None)
framework = st.text_input("Framework / template name", value=existing.framework if existing else "Generic study-quality domains")
saved_custom_domains = [item.domain for item in existing.domains if item.domain not in DEFAULT_QUALITY_DOMAINS] if existing else []
custom_domains = st.text_area("Additional custom domains (one per line)", value="\n".join(saved_custom_domains))
domains = list(DEFAULT_QUALITY_DOMAINS) + [line.strip() for line in custom_domains.splitlines() if line.strip()]
existing_by_domain = {item.domain: item for item in existing.domains} if existing else {}
rating_labels = {
    "Unclear": "unclear", "Low concern": "low_concern", "Some concern": "some_concern",
    "High concern": "high_concern", "Not applicable": "not_applicable",
}
reverse = {value: key for key, value in rating_labels.items()}

with st.form(f"quality_{record_id}"):
    ratings = {}
    for domain in domains:
        st.markdown(f"**{domain}**")
        cols = st.columns([1, 2])
        prior = existing_by_domain.get(domain)
        label = reverse.get(prior.rating, "Unclear") if prior else "Unclear"
        selected = cols[0].selectbox("Rating", list(rating_labels), index=list(rating_labels).index(label), key=f"rating_{record_id}_{domain}")
        notes = cols[1].text_input("Rationale / notes", value=prior.notes if prior else "", key=f"notes_{record_id}_{domain}")
        ratings[domain] = (rating_labels[selected], notes)
    reviewer = st.text_input("Reviewer name or initials", value=existing.reviewer if existing else "")
    save = st.form_submit_button("Save domain assessment", type="primary")
if save:
    upsert_quality_assessment(project, record_id, framework, ratings, reviewer)
    st.success("Domain-level assessment saved without calculating an aggregate score.")
    st.rerun()
