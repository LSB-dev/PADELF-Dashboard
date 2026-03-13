from typing import List, Dict
from ..data.model import Dataset
import streamlit as st


# Horizon label mappings
HORIZON_LABELS = {
    "vst": "Very short-term",
    "st": "Short-term",
    "mt": "Medium-term",
    "lt": "Long-term",
}


def apply_filters(filters: dict[str, list], datasets: list[Dataset]) -> list[Dataset]:
    """
    Apply multiple filters with AND logic.
    filters: {field_name: [selected_values]}
    - Empty list for a field = no filter applied for that field
    - For scalar fields: dataset matches if its value is in selected_values
    - For list fields (horizons, features): dataset matches if any of its values
      appear in selected_values
    - None field value = treated as no match when a filter is active
    """
    if not filters or all(len(v) == 0 for v in filters.values()):
        return datasets

    def matches(dataset: Dataset, field: str, values: list) -> bool:
        if len(values) == 0:
            return True  # No filter for this field
        val = getattr(dataset, field, None)
        if val is None:
            return False
        if field in {"horizons", "features"}:
            # List field: match if any value in selected_values
            return any(x in values for x in val)
        else:
            # Scalar field: match if value in selected_values
            return val in values

    supported_fields = ["domain", "type", "horizons", "license"]
    filtered = []
    for ds in datasets:
        if all(matches(ds, f, filters.get(f, [])) for f in supported_fields):
            filtered.append(ds)
    return filtered


def render_filter_sidebar(datasets: list[Dataset]) -> dict[str, list]:
    """
    Renders multiselect widgets in the Streamlit sidebar for:
    domain, type, horizons, license

    All option values are derived dynamically from the datasets list.
    Never hardcode filter values.

    For list fields (horizons): collect all unique values across all datasets.
    For scalar fields: collect all unique non-None values.

    Returns a filters dict compatible with apply_filters().
    Stores selections in st.session_state under keys:
    'filter_domain', 'filter_type', 'filter_horizons', 'filter_license'
    """
    with st.sidebar:
        # Extract unique values for each field
        domains = sorted(set(ds.domain for ds in datasets if ds.domain is not None))
        types = sorted(set(ds.type for ds in datasets if ds.type is not None))
        all_horizons = set()
        for ds in datasets:
            all_horizons.update(ds.horizons)
        horizons = sorted(all_horizons)
        licenses = sorted(set(ds.license for ds in datasets if ds.license is not None))

        # Initialize session state for each filter
        if "filter_domain" not in st.session_state:
            st.session_state.filter_domain = []
        if "filter_type" not in st.session_state:
            st.session_state.filter_type = []
        if "filter_horizons" not in st.session_state:
            st.session_state.filter_horizons = []
        if "filter_license" not in st.session_state:
            st.session_state.filter_license = []

        # Count active filters
        active_filters = sum(
            1 for key in ["filter_domain", "filter_type", "filter_horizons", "filter_license"]
            if len(st.session_state[key]) > 0
        )

        # Sidebar header with active filter count
        st.markdown(f"### Filters ({active_filters} active)")

        # Domain filter
        st.session_state.filter_domain = st.multiselect(
            "Domain",
            options=domains,
            default=st.session_state.filter_domain,
            key="domain_select"
        )

        # Type filter
        st.session_state.filter_type = st.multiselect(
            "Type",
            options=types,
            default=st.session_state.filter_type,
            key="type_select"
        )

        # Horizons filter with human-readable labels
        horizons_options = {h: HORIZON_LABELS.get(h, h) for h in horizons}
        selected_horizons_labels = [horizons_options[h] for h in st.session_state.filter_horizons if h in horizons_options]
        selected_horizons_labels = st.multiselect(
            "Horizons",
            options=list(horizons_options.values()),
            default=selected_horizons_labels,
            key="horizons_select"
        )
        # Convert back from labels to values
        label_to_value = {v: k for k, v in horizons_options.items()}
        st.session_state.filter_horizons = [label_to_value[label] for label in selected_horizons_labels]

        # License filter
        st.session_state.filter_license = st.multiselect(
            "License",
            options=licenses,
            default=st.session_state.filter_license,
            key="license_select"
        )

    # Return filters dict compatible with apply_filters()
    return {
        "domain": st.session_state.filter_domain,
        "type": st.session_state.filter_type,
        "horizons": st.session_state.filter_horizons,
        "license": st.session_state.filter_license,
    }
