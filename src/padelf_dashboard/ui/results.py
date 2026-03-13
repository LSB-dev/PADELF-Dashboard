from __future__ import annotations

from typing import List

import streamlit as st

from padelf_dashboard.data.model import Dataset


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
            }
        )

    st.dataframe(rows, use_container_width=True)
