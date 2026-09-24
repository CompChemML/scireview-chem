from pathlib import Path
import re
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from scireview.models import ReviewProject
from scireview.persistence import project_from_json, project_to_json
from scireview.reporting import export_project_workbook, export_workflow_pdf


st.set_page_config(page_title="Reports & Export | SciReview Chem", page_icon="📦", layout="wide")
if "project" not in st.session_state:
    st.session_state.project = ReviewProject()
project = st.session_state.project

st.title("Reports & Export")
st.caption("Exports reproduce entered and imported evidence. They do not invent citations, missing metadata, or scientific conclusions.")

safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", project.metadata.name.strip()).strip("_") or "scireview_project"

st.subheader("Project save and reopen")
left, right = st.columns(2)
with left:
    st.download_button("Download project JSON", project_to_json(project), f"{safe_name}.json", "application/json", type="primary")
    st.caption("The project file contains protocol, searches, raw records, decision history, extraction, quality assessment, and notes.")
with right:
    upload = st.file_uploader("Reopen a project JSON", type=["json"])
    if upload and st.button("Load this project", type="primary"):
        try:
            loaded = project_from_json(upload.getvalue())
            st.session_state.project = loaded
            for key in list(st.session_state):
                if key.startswith(("screen_position_", "full_text_position_")):
                    del st.session_state[key]
            st.success(f"Loaded project: {loaded.metadata.name}")
            st.rerun()
        except Exception as error:
            st.error(f"Project could not be loaded: {error}")

st.divider()
st.subheader("Research workflow exports")
st.write("The Excel workbook keeps raw records, audit histories, included studies, extraction, quality domains, evidence, PRISMA counts, and metadata in separate sheets.")
try:
    workbook = export_project_workbook(project)
    report = export_workflow_pdf(project)
    exports = st.columns(2)
    exports[0].download_button("Download Excel workbook", workbook, f"{safe_name}_workflow.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    exports[1].download_button("Download PDF workflow report", report, f"{safe_name}_workflow_report.pdf",
                               "application/pdf", use_container_width=True)
except Exception as error:
    st.error(f"Export generation failed: {error}")

st.info("Narrative interpretation appears only when entered by the researcher in Evidence Synthesis. The software does not generate scientific conclusions.")

