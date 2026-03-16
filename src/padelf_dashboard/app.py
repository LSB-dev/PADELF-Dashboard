#Streamlit entry

import streamlit as st
from padelf_dashboard.data.client import load_datasets
from padelf_dashboard.ui.results import render_results_table, search_datasets
from padelf_dashboard.ui.filters import render_filter_sidebar, apply_filters
from padelf_dashboard.ui.datasets_detail import render_detail

@st.cache_data(ttl=3600)  # Cache for 1 hour (3600 seconds)
def get_datasets():
    return load_datasets()

st.set_page_config(page_title="PADELF Dashboard (v0.04)", layout="wide", initial_sidebar_state="expanded")
st.title("PADELF Dashboard (v0.04)")
st.caption("Browse and search datasets for electric load forecasting. Data loaded from the [PADELF Repository](https://github.com/LSB-dev/Publicly-Available-Datasets-For-Electric-Load-Forecasting)")

try:
    datasets = get_datasets()
    st.success(f"Metadata loaded. Datasets: {len(datasets)}")

    # Step 1: Render filters sidebar
    filters = render_filter_sidebar(datasets)

    # Step 2: Apply filters
    filtered_by_filters = apply_filters(filters, datasets)

    # Step 3: Search in filtered results
    query = st.text_input(
        "Search",
        placeholder="Search by name, abbreviation, or domain...",
        key="search_query"
    )

    final_results = search_datasets(query, filtered_by_filters)

    # Step 4 & 5: Update result count and render results
    st.caption(f"Showing {len(final_results)} of {len(datasets)} datasets")

    render_results_table(final_results)

    # Step 6: Render expandable detail views
    st.markdown("---")
    st.subheader("Dataset Details")
    
    for dataset in final_results:
        with st.expander(label=dataset.name, expanded=False):
            render_detail(dataset)

except Exception as e:
    st.error("Failed to load or validate metadata.")
    st.exception(e)

# Footer with link to GitHub repo

st.markdown("""
---
Made by [Guilherme](https://github.com/guischmid). View on [GitHub](https://github.com/LSB-dev/PADELF-Dashboard).
""")
