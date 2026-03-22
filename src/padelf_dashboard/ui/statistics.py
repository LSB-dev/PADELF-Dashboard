
from collections import Counter
import streamlit as st
import pandas as pd
from typing import List

from padelf_dashboard.data.model import Dataset


@st.dialog("Dataset Statistics", width="large")
def _show_statistics_dialog(all_datasets: List[Dataset], filtered_datasets: List[Dataset]) -> None:
    tab_all, tab_filtered = st.tabs(["All datasets", "Filtered results"])

    with tab_all:
        _render_charts(all_datasets)

    with tab_filtered:
        _render_charts(filtered_datasets)


def render_statistics_button(all_datasets: List[Dataset], filtered_datasets: List[Dataset]) -> None:
    if st.button("Show statistics"):
        _show_statistics_dialog(all_datasets, filtered_datasets)


def _render_charts(datasets: List[Dataset]) -> None:
    st.caption(f"Based on {len(datasets)} datasets")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Domain distribution**")
        domain_counts = Counter([ds.domain for ds in datasets])
        domain_df = pd.DataFrame(domain_counts.items(), columns=["Domain", "Count"])
        st.bar_chart(domain_df, x="Domain", y="Count")

    with col_right:
        st.markdown("**Type distribution**")
        type_counts = Counter([ds.type for ds in datasets])
        type_df = pd.DataFrame(type_counts.items(), columns=["Type", "Count"])
        st.bar_chart(type_df, x="Type", y="Count")

    col_left_2, col_right_2 = st.columns(2)

    with col_left_2:
        st.markdown("**Horizons distribution**")
        horizon_labels = {
            "vst": "Very short-term",
            "st": "Short-term",
            "mt": "Medium-term",
            "lt": "Long-term",
        }
        all_horizons = [h for ds in datasets for h in ds.horizons]
        horizon_counts = Counter(all_horizons)
        horizon_df = pd.DataFrame(
            [
                {"Horizon": horizon_labels.get(h, h), "Count": c}
                for h, c in horizon_counts.items()
            ]
        )
        if horizon_df.empty:
            horizon_df = pd.DataFrame(columns=["Horizon", "Count"])
        st.bar_chart(horizon_df, x="Horizon", y="Count")

    with col_right_2:
        st.markdown("**Resolution distribution**")
        resolution_counts = Counter(
            [ds.resolution_minutes for ds in datasets if ds.resolution_minutes is not None]
        )
        resolution_df = pd.DataFrame(
            [
                {"Resolution (min)": minutes, "Count": count}
                for minutes, count in sorted(resolution_counts.items(), key=lambda item: item[0])
            ]
        )
        if resolution_df.empty:
            resolution_df = pd.DataFrame(columns=["Resolution (min)", "Count"])
        st.bar_chart(resolution_df, x="Resolution (min)", y="Count")
