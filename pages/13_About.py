import streamlit as st


st.set_page_config(page_title="About | SciReview Chem", page_icon="ℹ️", layout="wide")
st.title("About SciReview Chem")
st.markdown("""
**SciReview Chem** is a local-first workbench for transparent evidence-review workflows in chemistry, materials science, environmental science, toxicology, and related fields.

### Responsible automation

The software automates parsing, matching proposals, counting, filtering, visualization, and reporting. Researchers retain responsibility for eligibility decisions, quality judgments, interpretation, and conclusions.

### Methodological boundaries

- A literature review is not automatically systematic because it includes many papers.
- A systematic review does not automatically require meta-analysis.
- Fuzzy similarity never silently deletes records.
- Full-text exclusions require explicit reasons.
- Missing information remains missing and is not treated as zero.
- Quality assessment depends on review context and study design; no universal score is produced.
- Paywalls and publisher access controls are never bypassed.

### Zero-cost operation

The application runs locally with open-source Python packages and requires no API key, paid database, cloud account, or hosted service.

### Roadmap

Full meta-analysis is deliberately outside the MVP. A future, separately validated phase may add effect-size extraction, fixed- and random-effects models, forest plots, heterogeneity, and publication-bias diagnostics.
""")

