from __future__ import annotations

import streamlit as st

from scireview.models import BibliographicRecord, ReviewProtocol


def render_record(record: BibliographicRecord) -> None:
    st.markdown(f"## {record.title or 'Title not reported'}")
    metadata = ["; ".join(record.authors) or "Authors NR"]
    metadata.append(str(record.year) if record.year else "Year NR")
    metadata.append(record.journal or "Journal NR")
    st.caption(" · ".join(metadata))
    st.markdown("#### Abstract")
    st.write(record.abstract or "NR — abstract not reported in the imported metadata.")
    cols = st.columns(3)
    cols[0].write(f"**DOI:** {record.doi or 'NR'}")
    cols[1].write(f"**Keywords:** {'; '.join(record.keywords) or 'NR'}")
    cols[2].write(f"**Source:** {record.source_database or 'NR'}")


def render_protocol_criteria(protocol: ReviewProtocol) -> None:
    st.markdown("#### Protocol criteria")
    st.markdown("**Inclusion**")
    if protocol.inclusion_criteria:
        for criterion in protocol.inclusion_criteria:
            st.markdown(f"- {criterion}")
    else:
        st.caption("No inclusion criteria recorded.")
    st.markdown("**Exclusion**")
    if protocol.exclusion_criteria:
        for criterion in protocol.exclusion_criteria:
            st.markdown(f"- {criterion}")
    else:
        st.caption("No exclusion criteria recorded.")

