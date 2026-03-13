#Streamlit entry

import streamlit as st
from padelf_dashboard.data.client import load_datasets
from padelf_dashboard.ui.results import render_results_table, search_datasets

@st.cache_data(ttl=3600)  # Cache for 1 hour (3600 seconds)
def get_datasets():
    return load_datasets()

st.set_page_config(page_title="PADELF Dashboard (v0.04)", layout="wide")
st.title("PADELF Dashboard (v0.04)")
st.caption("Browse and search datasets for electric load forecasting. Data loaded from the [PADELF Repository](https://github.com/LSB-dev/Publicly-Available-Datasets-For-Electric-Load-Forecasting)")

try:
    datasets = get_datasets()
    st.success(f"Metadata loaded. Datasets: {len(datasets)}")

    query = st.text_input(
        "Search",
        placeholder="Search by name, abbreviation, or domain...",
        key="search_query"
    )

    filtered = search_datasets(query, datasets)
    st.caption(f"Showing {len(filtered)} of {len(datasets)} datasets")

    render_results_table(filtered)

except Exception as e:
    st.error("Failed to load or validate metadata.")
    st.exception(e)

# Footer with link to GitHub repo

st.markdown("""
---
Made by [Guilherme](https://github.com/guischmid). View on [GitHub](https://github.com/LSB-dev/PADELF-Dashboard).
""")
