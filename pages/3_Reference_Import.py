from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.importers import import_references
from scireview.models import ReviewProject


st.set_page_config(page_title="Reference Import | SciReview Chem", page_icon="📥", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project

st.title("Reference Import")
st.caption("Import preserves the original metadata alongside normalized working fields. Missing metadata is never guessed.")
source = st.text_input("Source database or export origin", value="Imported file")
upload = st.file_uploader("Choose RIS, BibTeX, CSV, TSV, or XLSX", type=["ris", "bib", "bibtex", "csv", "tsv", "xlsx"])

if upload is not None:
    fingerprint = (upload.name, upload.size, source)
    if st.session_state.get("import_fingerprint") != fingerprint:
        try:
            result = import_references(upload.getvalue(), upload.name, source.strip() or "Imported file")
            st.session_state.import_preview = result
            st.session_state.import_fingerprint = fingerprint
        except Exception as error:
            st.error(f"Import could not be parsed: {error}")
            st.stop()
    result = st.session_state.import_preview
    st.subheader("Import preview")
    st.metric("Records parsed", len(result.records))
    for warning in result.warnings:
        st.warning(warning)
    st.dataframe([{
        "Title": record.title or "NR", "Authors": "; ".join(record.authors) or "NR",
        "Year": record.year or "NR", "Journal": record.journal or "NR",
        "DOI": record.doi or "NR", "Source": record.source_database,
    } for record in result.records], use_container_width=True, hide_index=True)
    if st.button("Add parsed records to project", type="primary", disabled=not result.records):
        project.records.extend(result.records)
        st.success(f"Added {len(result.records)} records. Raw imported metadata was preserved.")
        del st.session_state.import_preview
        del st.session_state.import_fingerprint
        st.rerun()

st.divider()
st.subheader("Project records")
st.write(f"{len(project.records)} imported records across {len({r.import_batch_id for r in project.records})} batch(es).")
if project.records:
    st.dataframe([{
        "ID": record.id[:8], "Title": record.title or "NR", "Year": record.year or "NR",
        "DOI": record.doi or "NR", "Active": record.active, "Source": record.source_database,
    } for record in project.records], use_container_width=True, hide_index=True)

