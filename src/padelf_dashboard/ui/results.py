from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from padelf_dashboard.data.model import Dataset
from padelf_dashboard.ui.data_quality import completeness_score


def search_datasets(query: str, datasets: List[Dataset]) -> List[Dataset]:
    """Case-insensitive substring search across: name, abbreviation, domain.

    Empty or whitespace-only query returns all datasets unchanged.
    None fields are treated as empty string (never crash).
    """

    if not query or not query.strip():
        return datasets

    query_lower = query.strip().lower()

    results: List[Dataset] = []
    for ds in datasets:
        name = getattr(ds, "name", "") or ""
        abbreviation = getattr(ds, "abbreviation", "") or ""
        domain = getattr(ds, "domain", "") or ""

        if (
            query_lower in name.lower()
            or query_lower in abbreviation.lower()
            or query_lower in domain.lower()
        ):
            results.append(ds)

    return results


def render_results_table(datasets: List[Dataset]) -> None:
    """Renders a Streamlit dataframe showing a summary of the given datasets.

    Columns: name, abbreviation, domain, type, resolution_minutes, horizons
    None values displayed as empty string or "N/A".
    horizons list displayed as comma-separated string.
    """

    if not datasets:
        st.info("No datasets match your search.")
        return

    rows = []
    for ds in datasets:
        rows.append(
            {
                "name": ds.name or "",
                "abbreviation": ds.abbreviation or "",
                "domain": ds.domain or "",
                "type": ds.type or "",
                "resolution_minutes": ds.resolution_minutes if ds.resolution_minutes is not None else "",
                "horizons": ", ".join(ds.horizons) if ds.horizons else "",
                "completeness": completeness_score(ds),
            }
        )

    df = pd.DataFrame(rows)
    table_height = min(len(rows) * 35 + 38, 600)

    st.dataframe(
        df,
        height=table_height,
        hide_index=True,
        use_container_width=True,
        column_config={
            "name": st.column_config.Column("Dataset Name", width="large"),
            "abbreviation": st.column_config.Column("Abbreviation", width="small"),
            "domain": st.column_config.Column(
                "Domain",
                help="Application domain: system, residential, industrial, or unknown",
            ),
            "type": st.column_config.Column(
                "Type",
                help="Data format: collection, file_archive, or platform_api",
            ),
            "resolution_minutes": st.column_config.Column(
                "Resolution (min)",
                help="Temporal resolution of the data in minutes",
            ),
            "horizons": st.column_config.Column(
                "Horizons",
                help=(
                    "Forecasting horizons: vst (very short-term), st (short-term), "
                    "mt (medium-term), lt (long-term)"
                ),
            ),
            "completeness": st.column_config.Column(
                "Completeness",
                help="Metadata completeness: license, citation, and resolution (3/3 = complete)",
                width="small",
            ),
        },
    )
