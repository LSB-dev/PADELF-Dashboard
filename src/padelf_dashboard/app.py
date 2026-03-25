# Streamlit entry

import pandas as pd
import streamlit as st

try:
    from st_aggrid import AgGrid, DataReturnMode, GridOptionsBuilder, GridUpdateMode

    HAS_AGGRID = True
except ImportError:
    AgGrid = None
    DataReturnMode = None
    GridOptionsBuilder = None
    GridUpdateMode = None
    HAS_AGGRID = False

from padelf_dashboard.data.client import load_datasets
from padelf_dashboard.ui.results import (
    build_results_dataframe,
    pick_random_dataset,
    render_results_table,
    search_datasets,
)
from padelf_dashboard.ui.filters import render_filter_sidebar, apply_filters
from padelf_dashboard.ui.datasets_detail import render_detail
from padelf_dashboard.ui.statistics import render_statistics_button
from padelf_dashboard.ui.glossary import render_glossary


@st.cache_data(ttl=3600)  # Cache for 1 hour (3600 seconds)
def get_datasets():
    return load_datasets()


st.set_page_config(page_title="PADELF Dashboard - Browse Electric Load Forecasting Datasets",
                   layout="wide", initial_sidebar_state="expanded")

try:
    datasets = get_datasets()

    title_col, glossary_col = st.columns([7, 1])
    with title_col:
        st.title("PADELF Dashboard")
    with glossary_col:
        render_glossary(datasets)

    st.caption(
        "Browse and search datasets for electric load forecasting. Data loaded from the [PADELF Repository](https://github.com/LSB-dev/Publicly-Available-Datasets-For-Electric-Load-Forecasting) on GitHub. Use the filters and search box to find datasets that match your needs, and click on each dataset for more details.")
    st.caption(f"{len(datasets)} datasets loaded from PADELF repository")

    if "random_dataset_id" not in st.session_state:
        st.session_state.random_dataset_id = None

    if "selected_dataset" not in st.session_state:
        st.session_state.selected_dataset = None

    # Step 1: Render filters sidebar
    filters = render_filter_sidebar(datasets)

    with st.sidebar:
        random_clicked = st.button("Load random dataset", width="stretch")
        clear_random_clicked = st.button(
            "Show all datasets",
            width="stretch",
            disabled=st.session_state.random_dataset_id is None,
        )

    if random_clicked:
        random_dataset = pick_random_dataset(datasets)
        st.session_state.random_dataset_id = (
            random_dataset.dataset_id if random_dataset is not None else None
        )

    if clear_random_clicked:
        st.session_state.random_dataset_id = None

    # Step 2: Apply filters
    filtered_by_filters = apply_filters(filters, datasets)

    # Step 3: Search in filtered results
    query = st.text_input(
        "Search",
        placeholder="Search by name, abbreviation, or domain... ",
        key="search_query"
    )

    final_results = search_datasets(query, filtered_by_filters)

    if st.session_state.random_dataset_id is not None:
        random_result = [
            ds
            for ds in datasets
            if ds.dataset_id == st.session_state.random_dataset_id
        ]

        if random_result:
            final_results = random_result
            st.info(f"Showing random dataset: {random_result[0].name}")
        else:
            st.session_state.random_dataset_id = None

    result_ids = {dataset.dataset_id for dataset in final_results}
    if st.session_state.selected_dataset not in result_ids:
        st.session_state.selected_dataset = None

    # Step 4: Show result count in sidebar
    st.sidebar.caption(f"Showing {len(final_results)} of {len(datasets)} datasets")

    if not final_results:
        st.info("No datasets match your criteria.")
        render_statistics_button(datasets, final_results)
    else:
        dataset_by_id = {dataset.dataset_id: dataset for dataset in final_results}
        display_df = build_results_dataframe(final_results)

        left_col, right_col = st.columns([3, 2])

        with left_col:
            if HAS_AGGRID:
                assert GridOptionsBuilder is not None
                assert GridUpdateMode is not None
                assert DataReturnMode is not None
                assert AgGrid is not None

                gb = GridOptionsBuilder.from_dataframe(display_df)
                gb.configure_selection(selection_mode="single", use_checkbox=False)
                gb.configure_default_column(resizable=True, sortable=True)
                gb.configure_column("Dataset Name", headerTooltip="Dataset name", flex=2)
                gb.configure_column("Abbreviation", headerTooltip="Short dataset acronym", flex=1)
                gb.configure_column(
                    "Domain",
                    headerTooltip="Application domain: system, residential, industrial, or unknown",
                )
                gb.configure_column(
                    "Type",
                    headerTooltip="Data format: collection, file_archive, or platform_api",
                )
                gb.configure_column(
                    "Resolution (min)",
                    headerTooltip="Temporal resolution of the data in minutes",
                )
                gb.configure_column(
                    "Horizons",
                    headerTooltip=(
                        "Forecasting horizons: vst (very short-term), st (short-term), "
                        "mt (medium-term), lt (long-term)"
                    ),
                )
                gb.configure_column(
                    "Completeness",
                    headerTooltip=(
                        "Metadata completeness: license, citation, and resolution "
                        "(3/3 = complete)"
                    ),
                )

                grid_options = gb.build()

                grid_kwargs = {
                    "gridOptions": grid_options,
                    "update_mode": GridUpdateMode.SELECTION_CHANGED,
                    "data_return_mode": DataReturnMode.FILTERED_AND_SORTED,
                    "fit_columns_on_grid_load": True,
                    "height": 600,
                    "allow_unsafe_jscode": False,
                    "theme": "streamlit",
                }

                try:
                    grid_response = AgGrid(display_df, **grid_kwargs)
                except TypeError:
                    # Fallback for streamlit-ag-grid versions without "streamlit" theme support.
                    grid_kwargs["theme"] = "alpine"
                    grid_response = AgGrid(display_df, **grid_kwargs)

                selected_rows = grid_response.get("selected_rows", []) if grid_response else []

                selected_name: str | None = None
                if isinstance(selected_rows, pd.DataFrame):
                    if len(selected_rows) > 0:
                        selected_name = selected_rows.iloc[0].get("Dataset Name")
                elif isinstance(selected_rows, list):
                    if len(selected_rows) > 0 and isinstance(selected_rows[0], dict):
                        selected_name = selected_rows[0].get("Dataset Name")

                if isinstance(selected_name, str) and selected_name:
                    selected_dataset = next(
                        (dataset for dataset in final_results if dataset.name == selected_name),
                        None,
                    )
                    if selected_dataset is not None:
                        st.session_state.selected_dataset = selected_dataset.dataset_id
            else:
                st.warning("streamlit-ag-grid is not available. Falling back to Streamlit table.")
                selected_dataset_id = render_results_table(
                    final_results,
                    enable_selection=True,
                    key="datasets_master_table",
                )
                if selected_dataset_id is not None:
                    st.session_state.selected_dataset = selected_dataset_id

            render_statistics_button(datasets, final_results)

        with right_col:
            selected_dataset_key = st.session_state.selected_dataset
            selected_dataset = (
                dataset_by_id.get(selected_dataset_key)
                if isinstance(selected_dataset_key, str)
                else None
            )

            with st.container(height=650):
                if selected_dataset is None:
                    st.info("Select a dataset from the table to view details.")
                else:
                    render_detail(selected_dataset)

except Exception as e:
    st.error("Failed to load or validate metadata. ")
    st.exception(e)

# Footer with link to GitHub repo

st.markdown("""
---
Made by [Guilherme](https://github.com/guischmid). View on [GitHub](https://github.com/LSB-dev/PADELF-Dashboard).
""")
