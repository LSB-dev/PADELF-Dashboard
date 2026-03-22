from __future__ import annotations

import random
from typing import List

import pandas as pd
import streamlit as st

from padelf_dashboard.data.model import Dataset
from padelf_dashboard.ui.data_quality import completeness_score


TABLE_COLUMNS = [
    "Dataset Name",
    "Abbreviation",
    "Domain",
    "Type",
    "Resolution (min)",
    "Horizons",
    "Completeness",
]


def build_results_dataframe(datasets: List[Dataset]) -> pd.DataFrame:
    """Build the results dataframe used by the app table views."""

    rows = []
    for ds in datasets:
        rows.append(
            {
                "Dataset Name": ds.name or "",
                "Abbreviation": ds.abbreviation or "",
                "Domain": ds.domain or "",
                "Type": ds.type or "",
                "Resolution (min)": (
                    ds.resolution_minutes if ds.resolution_minutes is not None else None
                ),
                "Horizons": ", ".join(ds.horizons) if ds.horizons else "",
                "Completeness": completeness_score(ds),
            }
        )

    return pd.DataFrame(rows, columns=TABLE_COLUMNS)


def pick_random_dataset(datasets: List[Dataset]) -> Dataset | None:
    """Return one random dataset from the provided list, or None when empty."""

    if not datasets:
        return None

    return random.choice(datasets)


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


def render_results_table(
    datasets: List[Dataset],
    *,
    enable_selection: bool = False,
    key: str = "results_table",
) -> str | None:
    """Renders a Streamlit dataframe showing a summary of the given datasets.

    Columns: name, abbreviation, domain, type, resolution_minutes, horizons
    None values displayed as empty string or "N/A".
    horizons list displayed as comma-separated string.
    """

    if not datasets:
        st.info("No datasets match your search.")
        return None

    df = build_results_dataframe(datasets)
    table_height = min(len(datasets) * 35 + 38, 600)

    dataframe_kwargs = {
        "height": table_height,
        "hide_index": True,
        "width": "stretch",
        "column_config": {
            "Dataset Name": st.column_config.Column(width="large"),
            "Abbreviation": st.column_config.Column(width="small"),
            "Domain": st.column_config.Column(
                help="Application domain: system, residential, industrial, or unknown",
            ),
            "Type": st.column_config.Column(
                help="Data format: collection, file_archive, or platform_api",
            ),
            "Resolution (min)": st.column_config.Column(
                help="Temporal resolution of the data in minutes",
            ),
            "Horizons": st.column_config.Column(
                help=(
                    "Forecasting horizons: vst (very short-term), st (short-term), "
                    "mt (medium-term), lt (long-term)"
                ),
            ),
            "Completeness": st.column_config.Column(
                help="Metadata completeness: license, citation, and resolution (3/3 = complete)",
                width="small",
            ),
        },
    }

    if not enable_selection:
        st.dataframe(df, **dataframe_kwargs)
        return None

    selection_event = st.dataframe(
        df,
        key=key,
        on_select="rerun",
        selection_mode="single-row",
        **dataframe_kwargs,
    )

    selected_rows = (
        selection_event.get("selection", {}).get("rows", []) if selection_event else []
    )
    if selected_rows:
        selected_index = selected_rows[0]
        if 0 <= selected_index < len(datasets):
            return datasets[selected_index].dataset_id

    return None
