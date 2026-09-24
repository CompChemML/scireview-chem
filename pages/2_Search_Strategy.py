from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.models import ReviewProject, SearchStrategy
from scireview.utils import lines_to_list


st.set_page_config(page_title="Search Strategy | SciReview Chem", page_icon="🔎", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project

st.title("Search Strategy")
st.caption("OR combines terms within a concept; AND combines concept blocks. Save the exact database-specific query you actually ran.")

left, right = st.columns([1, 1])
with left:
    st.subheader("Concept builder")
    concept_a = st.text_area("Concept A terms (one per line)", placeholder="biochar\nhydrochar\ncarbonaceous adsorbent")
    concept_b = st.text_area("Concept B terms (one per line)", placeholder="adsorption\nsorption\nremoval")
    concept_c = st.text_area("Concept C terms (one per line, optional)", placeholder="lead\ncadmium\nheavy metal")

def quote(term: str) -> str:
    term = term.strip()
    if not term or term.startswith('"') or any(char in term for char in "*()"):
        return term
    return f'"{term}"' if " " in term else term

blocks = []
for raw in (concept_a, concept_b, concept_c):
    terms = lines_to_list(raw)
    if terms:
        blocks.append("(" + " OR ".join(quote(term) for term in terms) + ")")
built_query = "\nAND\n".join(blocks)

with right:
    st.subheader("Boolean preview")
    st.code(built_query or "Add terms to build a query.", language=None)
    st.warning("Database syntax differs. Review field tags, phrase behavior, truncation, and query limits in each database before running the search.")

st.divider()
st.subheader("Search audit trail")
with st.form("search_record"):
    database = st.selectbox("Database", ["PubMed", "Scopus", "Web of Science", "Google Scholar", "Crossref", "OpenAlex", "Other/manual"])
    exact_query = st.text_area("Exact query used", value=built_query, height=160)
    search_date = st.date_input("Search date", value=None)
    retrieved_text = st.text_input("Records retrieved (optional)")
    screened_text = st.text_input("Records screened from this search (optional)")
    retained_text = st.text_input("Records retained from this search (optional)")
    notes = st.text_area("Database-specific notes")
    save = st.form_submit_button("Add search record", type="primary")

if save:
    try:
        retrieved = int(retrieved_text) if retrieved_text.strip() else None
        screened = int(screened_text) if screened_text.strip() else None
        retained = int(retained_text) if retained_text.strip() else None
        if any(value is not None and value < 0 for value in (retrieved, screened, retained)):
            raise ValueError("Search counts cannot be negative")
        if retrieved is not None and screened is not None and screened > retrieved:
            raise ValueError("Records screened cannot exceed records retrieved")
        if screened is not None and retained is not None and retained > screened:
            raise ValueError("Records retained cannot exceed records screened")
        if not exact_query.strip():
            raise ValueError("Record the exact query before saving")
        project.searches.append(SearchStrategy(
            database=database, exact_query=exact_query.strip(),
            search_date=search_date.isoformat() if search_date else None,
            records_retrieved=retrieved, records_screened=screened,
            records_retained=retained, notes=notes.strip(),
        ))
        st.success("Search strategy added to the audit trail.")
    except ValueError as error:
        st.error(str(error))

if project.searches:
    st.dataframe([
        {"Database": item.database, "Search date": item.search_date, "Retrieved": item.records_retrieved,
         "Screened": item.records_screened, "Retained": item.records_retained,
         "Exact query": item.exact_query, "Notes": item.notes}
        for item in project.searches
    ], use_container_width=True, hide_index=True)
else:
    st.info("No searches recorded yet.")
