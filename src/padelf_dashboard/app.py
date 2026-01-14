#Streamlit entry

import streamlit as st

from padelf_dashboard.data.client import load_datasets

st.set_page_config(page_title="PADELF Dashboard (v0.03)", layout="wide")
st.title("PADELF Dashboard (v0.01)")

try:
    datasets = load_datasets()
    st.success(f"Metadata loaded. Datasets: {len(datasets)}")

    if len(datasets) == 0:
        st.info("No datasets yet (datasets.yaml is empty).")
    else:
        # Minimal preview table (helps confirm parsing)
        st.dataframe(
            [
                {
                    "dataset_id": d.dataset_id,
                    "name": d.name,
                    "domain": d.domain,
                    "resolution_minutes": d.resolution_minutes,
                    "url": d.access.url,
                }
                for d in datasets
            ],
            use_container_width=True,
        )

except Exception as e:
    st.error("Failed to load or validate metadata.")
    st.exception(e)
