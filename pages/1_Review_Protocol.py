from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.models import ReviewProject
from scireview.utils import lines_to_list


st.set_page_config(page_title="Review Protocol | SciReview Chem", page_icon="📋", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project
protocol = project.protocol

st.title("Review Protocol")
st.caption("Predefine the question and eligibility rules before screening. The review type is an explicit methodological choice.")

with st.expander("How review types differ"):
    st.markdown("""
- **Narrative review:** broad interpretive overview; methods may be less formally predefined.
- **Systematic review:** predefined question with transparent, reproducible searching and screening.
- **Scoping review:** maps the breadth and characteristics of evidence.
- **Evidence map:** systematically describes the distribution of evidence across a question space.
- **Rapid review:** uses documented shortcuts to deliver evidence under time constraints.
- **Gap analysis:** identifies evidence patterns; the researcher decides whether they constitute meaningful gaps.

A systematic review does not automatically require meta-analysis.
""")

review_types = {
    "Narrative review": "narrative", "Systematic review": "systematic",
    "Scoping review": "scoping", "Evidence map": "evidence_map",
    "Rapid review": "rapid", "Gap analysis": "gap_analysis",
}
reverse_types = {value: key for key, value in review_types.items()}

with st.form("protocol_form"):
    title = st.text_input("Review title", value=protocol.title)
    review_label = st.selectbox("Review type", list(review_types), index=list(review_types).index(reverse_types[protocol.review_type]))
    research_question = st.text_area("Research question", value=protocol.research_question)
    objective = st.text_area("Review objective", value=protocol.objective)
    domain = st.text_input("Scientific domain", value=protocol.scientific_domain)
    framework = st.selectbox(
        "Question framework",
        ["chemistry_materials", "PICO", "PECO", "custom"],
        index=["chemistry_materials", "PICO", "PECO", "custom"].index(protocol.question_framework)
        if protocol.question_framework in {"chemistry_materials", "PICO", "PECO", "custom"} else 0,
        help="Chemistry/materials uses Material/System, Treatment/Exposure, Comparator, and Outcome.",
    )
    c1, c2 = st.columns(2)
    population = c1.text_input("Population / material / system", value=protocol.population_or_material)
    exposure = c2.text_input("Intervention / treatment / exposure", value=protocol.intervention_or_exposure)
    comparator = c1.text_input("Comparator", value=protocol.comparator)
    outcome = c2.text_input("Outcome", value=protocol.outcome)
    d1, d2 = st.columns(2)
    start_text = d1.text_input("Start year (optional)", value="" if protocol.date_start is None else str(protocol.date_start))
    end_text = d2.text_input("End year (optional)", value="" if protocol.date_end is None else str(protocol.date_end))
    languages = st.text_input("Language restrictions (comma-separated)", value=", ".join(protocol.language_restrictions))
    study_types = st.text_area("Study-type restrictions (one per line)", value="\n".join(protocol.study_type_restrictions))
    inclusion = st.text_area("Inclusion criteria (one per line)", value="\n".join(protocol.inclusion_criteria))
    exclusion = st.text_area("Exclusion criteria (one per line)", value="\n".join(protocol.exclusion_criteria))
    databases = st.multiselect(
        "Databases planned",
        ["PubMed", "Scopus", "Web of Science", "Google Scholar", "Crossref", "OpenAlex", "Other/manual"],
        default=[item for item in protocol.databases_planned if item in {"PubMed", "Scopus", "Web of Science", "Google Scholar", "Crossref", "OpenAlex", "Other/manual"}],
    )
    notes = st.text_area("Protocol notes", value=protocol.notes)
    submitted = st.form_submit_button("Save protocol", type="primary")

if submitted:
    try:
        date_start = int(start_text) if start_text.strip() else None
        date_end = int(end_text) if end_text.strip() else None
        if date_start and date_end and date_start > date_end:
            raise ValueError("Start year cannot be later than end year")
        protocol.title = title.strip()
        protocol.review_type = review_types[review_label]
        protocol.research_question = research_question.strip()
        protocol.objective = objective.strip()
        protocol.scientific_domain = domain.strip()
        protocol.question_framework = framework
        protocol.population_or_material = population.strip()
        protocol.intervention_or_exposure = exposure.strip()
        protocol.comparator = comparator.strip()
        protocol.outcome = outcome.strip()
        protocol.date_start, protocol.date_end = date_start, date_end
        protocol.language_restrictions = [x.strip() for x in languages.split(",") if x.strip()]
        protocol.study_type_restrictions = lines_to_list(study_types)
        protocol.inclusion_criteria = lines_to_list(inclusion)
        protocol.exclusion_criteria = lines_to_list(exclusion)
        protocol.databases_planned = databases
        protocol.notes = notes.strip()
        project.metadata.name = protocol.title or project.metadata.name
        st.success("Protocol saved in the current project session.")
    except ValueError as error:
        st.error(str(error))

