from __future__ import annotations

import re
import streamlit as st

from padelf_dashboard.data.model import Dataset
from padelf_dashboard.ui.data_quality import completeness_score, missing_fields

# BibTeX constants
BIBTEX_PADELF2026 = r"""@article{padefl2026,
  title        = {PADELF -- A handy dashboard for finding open time series data for electric forecasting},
  author       = {Baur, Lukas and Schmid, Guilherme},
  year         = {2026},
  eprint       = {xxxx.yyyy},
  archivePrefix= {arXiv},
  primaryClass = {cs.DL},
  url          = {https://padelf.ipa.fraunhofer.de/},
  note         = {Preprint describing the dataset platform}
}"""

BIBTEX_BAUR2024 = r"""@inproceedings{baur2024datasets,
  author    = {Baur, Lukas and Chandramouli, Vignesh and Sauer, Alexander},
  title     = {Publicly Available Datasets For Electric Load Forecasting -- An Overview},
  booktitle = {Proceedings of the CPSL 2024},
  editor    = {Herberger, D. and H{\"u}bner, M.},
  location  = {Hannover},
  publisher = {publish-Ing.},
  year      = {2024},
  pages     = {1--12},
  doi       = {10.15488/17659}
}"""


def _format_value(value):
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

    score = completeness_score(dataset)
    missing = missing_fields(dataset)

    if score == "3/3":
        st.success("Metadata complete (3/3)")
    else:
        st.warning(f"Metadata incomplete ({score}) -- missing: {', '.join(missing)}")
    
    # Two-column layout for metadata
    col1, col2 = st.columns(2)
    
    metadata_fields = [
        ("Dataset ID", dataset.dataset_id),
        ("Type", dataset.type),
        ("Domain", dataset.domain),
        ("Resolution (min)", dataset.resolution_minutes),
        ("Time Coverage", 
         f"{dataset.time_coverage.start_date} – {dataset.time_coverage.end_date or 'Present'}"
         if dataset.time_coverage and dataset.time_coverage.start_date 
         else "N/A"),
        ("Duration (months)", dataset.duration_months),
        ("Features", dataset.features),
        ("Horizons", dataset.horizons),
        ("Multiple Regions", dataset.regions_multiple),
        ("License", dataset.license),
    ]
    
    # Split fields across two columns
    for idx, (field_label, value) in enumerate(metadata_fields):
        if idx % 2 == 0:
            col = col1
        else:
            col = col2
        
        with col:
            st.write(f"**{field_label}**: {_format_value(value)}")
    
    # Access link
    st.markdown("---")
    if dataset.access and dataset.access.url:
        st.markdown(f"**Access**: [{dataset.access.url}]({dataset.access.url})")
    
    # Access notes
    if dataset.access and dataset.access.access_notes:
        st.caption(dataset.access.access_notes)
    
    # Citation section
    st.markdown("---")
    st.subheader("Citation")
    
    # Extract origin key from bibtex if available and not legacy baur2024datasets
    origin_key = "originXXX"  # default placeholder
    has_origin = False
    if dataset.citation and dataset.citation.bibtex:
        bib = dataset.citation.bibtex.strip()
        if "baur2024datasets" not in bib:
            # Extract key: text between first '{' and first ','
            match = re.search(r'@\w+\{([^,]+)', bib)
            if match:
                origin_key = match.group(1).strip()
                has_origin = True
    
    # Block A: Example LaTeX text
    example_text = (
        r"The underlying dataset of this work is provided online~\cite{"
        + origin_key
        + r"} and was accessed via~\cite{padefl2026,baur2024datasets}."
    )
    st.caption("Example text body")
    st.code(example_text, language="latex")
    
    # Block B: BibTeX entries
    # Origin dataset reference
    if has_origin:
        st.caption("Origin dataset reference")
        st.code(dataset.citation.bibtex, language="bibtex")
    else:
        st.caption("Origin dataset reference (pending)")
        st.code("% originXXX: To be added for this dataset", language="bibtex")
    
    # PADELF platform reference
    st.caption("PADELF platform reference")
    st.code(BIBTEX_PADELF2026, language="bibtex")
    
    # Survey paper reference
    st.caption("Survey paper reference")
    st.code(BIBTEX_BAUR2024, language="bibtex")
    
    # Source paper information
    if dataset.source_paper and dataset.source_paper.in_baur_2024:
        st.markdown("---")
        st.write("Source Paper: **Included in Baur et al. 2024**")
        if dataset.source_paper.baur_2024_usage_count is not None:
            st.caption(f"Usage count: {dataset.source_paper.baur_2024_usage_count}")


def render_detail_expanded(dataset: Dataset) -> None:
    """Render dataset detail in full-width expanded mode."""

    # Subheader with name and abbreviation
    if dataset.abbreviation:
        st.subheader(f"{dataset.name} ({dataset.abbreviation})")
    else:
        st.subheader(dataset.name)

    score = completeness_score(dataset)
    missing = missing_fields(dataset)

    if score == "3/3":
        st.success("Metadata complete (3/3)")
    else:
        st.warning(f"Metadata incomplete ({score}) -- missing: {', '.join(missing)}")

    # Three-column layout for metadata (wider view)
    col1, col2, col3 = st.columns(3)

    metadata_fields = [
        ("Dataset ID", dataset.dataset_id),
        ("Type", dataset.type),
        ("Domain", dataset.domain),
        ("Resolution (min)", dataset.resolution_minutes),
        ("Time Coverage",
         f"{dataset.time_coverage.start_date} – {dataset.time_coverage.end_date or 'Present'}"
         if dataset.time_coverage and dataset.time_coverage.start_date
         else "N/A"),
        ("Duration (months)", dataset.duration_months),
        ("Features", dataset.features),
        ("Horizons", dataset.horizons),
        ("Multiple Regions", dataset.regions_multiple),
        ("License", dataset.license),
    ]

    for idx, (field_label, value) in enumerate(metadata_fields):
        col = [col1, col2, col3][idx % 3]
        with col:
            st.write(f"**{field_label}**: {_format_value(value)}")

    # Access link
    st.markdown("---")
    if dataset.access and dataset.access.url:
        st.markdown(f"**Access**: [{dataset.access.url}]({dataset.access.url})")

    # Access notes
    if dataset.access and dataset.access.access_notes:
        st.caption(dataset.access.access_notes)

    # Citation section
    st.markdown("---")
    st.subheader("Citation")

    # Extract origin key from bibtex if available and not legacy baur2024datasets
    origin_key = "originXXX"  # default placeholder
    has_origin = False
    if dataset.citation and dataset.citation.bibtex:
        bib = dataset.citation.bibtex.strip()
        if "baur2024datasets" not in bib:
            # Extract key: text between first '{' and first ','
            match = re.search(r'@\w+\{([^,]+)', bib)
            if match:
                origin_key = match.group(1).strip()
                has_origin = True

    # Block A: Example LaTeX text
    example_text = (
        r"The underlying dataset of this work is provided online~\cite{"
        + origin_key
        + r"} and was accessed via~\cite{padefl2026,baur2024datasets}."
    )
    st.caption("Example text body")
    st.code(example_text, language="latex")

    # Block B: BibTeX entries in side-by-side expanders
    bib_col1, bib_col2, bib_col3 = st.columns(3)

    with bib_col1:
        with st.expander("Origin dataset reference"):
            if has_origin:
                st.code(dataset.citation.bibtex, language="bibtex")
            else:
                st.code("% originXXX: To be added for this dataset", language="bibtex")

    with bib_col2:
        with st.expander("PADELF platform reference"):
            st.code(BIBTEX_PADELF2026, language="bibtex")

    with bib_col3:
        with st.expander("Survey paper reference"):
            st.code(BIBTEX_BAUR2024, language="bibtex")

    # Source paper information
    if dataset.source_paper and dataset.source_paper.in_baur_2024:
        st.markdown("---")
        st.write("Source Paper: **Included in Baur et al. 2024**")
        if dataset.source_paper.baur_2024_usage_count is not None:
            st.caption(f"Usage count: {dataset.source_paper.baur_2024_usage_count}")
