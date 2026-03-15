from __future__ import annotations

import streamlit as st

from padelf_dashboard.data.model import Dataset


def render_detail(dataset: Dataset) -> None:
    """
    Renders a full expanded view of one dataset using Streamlit.
    
    Layout:
    - Subheader with dataset name and abbreviation
    - Two-column metadata layout
    - Access link and notes
    - Citation section
    - Source paper information
    
    All None values display as "N/A". List values display as comma-separated strings.
    """
    
    # Subheader with name and abbreviation
    if dataset.abbreviation:
        st.subheader(f"{dataset.name} ({dataset.abbreviation})")
    else:
        st.subheader(dataset.name)
    
    # Helper function to format values
    def format_value(value):
        """Convert value to displayable string, handling None and lists."""
        if value is None:
            return "N/A"
        if isinstance(value, bool):
            return "Yes" if value else "No"
        if isinstance(value, list):
            return ", ".join(str(v) for v in value) if value else "N/A"
        if isinstance(value, int):
            return str(value)
        return str(value) if value else "N/A"
    
    # Two-column layout for metadata
    col1, col2 = st.columns(2)
    
    metadata_fields = [
        ("dataset_id", dataset.dataset_id),
        ("type", dataset.type),
        ("domain", dataset.domain),
        ("resolution_minutes", dataset.resolution_minutes),
        ("time_coverage", 
         f"{dataset.time_coverage.start_date} – {dataset.time_coverage.end_date or 'Present'}"
         if dataset.time_coverage and dataset.time_coverage.start_date 
         else "N/A"),
        ("duration_months", dataset.duration_months),
        ("features", dataset.features),
        ("horizons", dataset.horizons),
        ("regions_multiple", dataset.regions_multiple),
        ("license", dataset.license),
    ]
    
    # Split fields across two columns
    for idx, (field_label, value) in enumerate(metadata_fields):
        if idx % 2 == 0:
            col = col1
        else:
            col = col2
        
        with col:
            st.write(f"**{field_label}**: {format_value(value)}")
    
    # Access link
    st.markdown("---")
    if dataset.access and dataset.access.url:
        st.markdown(f"**Access**: [Link]({dataset.access.url})")
    
    # Access notes
    if dataset.access and dataset.access.access_notes:
        st.caption(dataset.access.access_notes)
    
    # Citation section
    st.markdown("---")
    st.subheader("Citation")
    
    if dataset.citation:
        if dataset.citation.preferred_citation:
            st.code(dataset.citation.preferred_citation, language="text")
        
        if dataset.citation.bibtex:
            st.code(dataset.citation.bibtex, language="bibtex")
        
        if not dataset.citation.preferred_citation and not dataset.citation.bibtex:
            st.info("No citation available.")
    else:
        st.info("No citation available.")
    
    # Source paper information
    if dataset.source_paper and dataset.source_paper.in_baur_2024:
        st.markdown("---")
        st.write("📄 **Included in Baur et al. 2024**")
        if dataset.source_paper.baur_2024_usage_count is not None:
            st.caption(f"Usage count: {dataset.source_paper.baur_2024_usage_count}")
