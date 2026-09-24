from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.extraction import ADSORPTION_FIELDS, GENERAL_FIELDS, MLIP_TRANSPORT_FIELDS, included_records, missing_fields, upsert_extraction
from scireview.models import ReviewProject


st.set_page_config(page_title="Data Extraction | SciReview Chem", page_icon="🧪", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project
records = included_records(project)

st.title("Data Extraction")
st.caption("Extract only information reported by the study. Leave absent values blank; the evidence table displays them as NR, never as zero.")
if not records:
    st.info("No included full-text studies are available for extraction.")
    st.stop()

record_labels = {record.id: f"{record.title or 'Untitled'} ({record.year or 'year NR'})" for record in records}
record_id = st.selectbox("Included study", list(record_labels), format_func=record_labels.get)
record = next(item for item in records if item.id == record_id)
existing = next((item for item in project.extraction_entries if item.record_id == record_id), None)
template_options = ["General", "Adsorption / materials", "MLIP ion transport"]
existing_indexes = {"general": 0, "adsorption": 1, "mlip_transport": 2}
template = st.selectbox("Extraction template", template_options,
                        index=existing_indexes.get(existing.template, 0) if existing else 0)
field_maps = {
    "General": (GENERAL_FIELDS, "general"),
    "Adsorption / materials": (ADSORPTION_FIELDS, "adsorption"),
    "MLIP ion transport": (MLIP_TRANSPORT_FIELDS, "mlip_transport"),
}
fields, template_key = field_maps[template]

st.markdown(f"### {record.title}")
st.caption("Custom fields are stored with the selected study and appear alongside template fields.")

with st.form(f"extraction_{record_id}_{template_key}"):
    values = {}
    defaults = existing.values if existing and existing.template == template_key else {}
    for field in fields:
        label = f"{field.label} ({field.unit})" if field.unit else field.label
        current = defaults.get(field.key)
        if field.kind == "number":
            values[field.key] = st.text_input(label, value="" if current is None else str(current),
                                              help="Enter the reported value and retain units in notes when they differ from the template.")
        elif field.kind == "yes_no":
            options = ["", "Yes", "No", "NR"]
            values[field.key] = st.selectbox(label, options, index=options.index(current) if current in options else 0)
        else:
            values[field.key] = st.text_area(label, value=current or "", height=80)
    custom_names = st.text_input("Custom field names (semicolon-separated)",
                                 value="; ".join(key[7:] for key in defaults if key.startswith("custom_")))
    custom_values = {}
    for name in [item.strip() for item in custom_names.split(";") if item.strip()]:
        key = f"custom_{name}"
        custom_values[key] = st.text_input(f"Custom: {name}", value=str(defaults.get(key) or ""))
    save = st.form_submit_button("Save extraction", type="primary")
if save:
    values.update(custom_values)
    upsert_extraction(project, record_id, template_key, values)
    st.success("Extraction saved. Blank fields remain explicitly missing.")
    st.rerun()

if existing and existing.template == template_key:
    missing = missing_fields(existing, fields)
    completed = len(fields) - len(missing)
    st.progress(completed / len(fields), text=f"{completed} of {len(fields)} template fields completed")
    if missing:
        st.caption(f"Missing / NR fields: {len(missing)}")
