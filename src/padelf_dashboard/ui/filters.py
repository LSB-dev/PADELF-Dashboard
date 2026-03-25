from typing import Optional, cast
from ..data.model import Dataset
import streamlit as st


# Horizon label mappings
HORIZON_LABELS = {
    "vst": "Very short-term",
    "st": "Short-term",
    "mt": "Medium-term",
    "lt": "Long-term",
}


def _parse_year(value: Optional[str]) -> Optional[int]:
    if not value or len(value) < 4:
        return None
    year_text = value[:4]
    if not year_text.isdigit():
        return None
    return int(year_text)


def apply_filters(filters: dict, datasets: list[Dataset]) -> list[Dataset]:
    """
    Apply multiple filters with AND logic.
    filters: {field_name: [selected_values]}
    - Empty list for a field = no filter applied for that field
    - For scalar fields: dataset matches if its value is in selected_values
    - For list fields (horizons, features): dataset matches if any of its values
      appear in selected_values
    - None field value = treated as no match when a filter is active
    """
    if not filters:
        return datasets

    domain_values = filters.get("domain", [])
    type_values = filters.get("type", [])
    horizons_values = filters.get("horizons", [])
    license_values = filters.get("license", [])
    features_values = filters.get("features", [])
    regions_value = filters.get("regions")
    resolution_value = filters.get("resolution")
    time_coverage_value = filters.get("time_coverage")
    duration_value = filters.get("duration")

    has_any_filter = (
        bool(domain_values)
        or bool(type_values)
        or bool(horizons_values)
        or bool(license_values)
        or bool(features_values)
        or (regions_value not in {None, "All"})
        or (resolution_value is not None)
        or (time_coverage_value is not None)
        or (duration_value not in {None, 0})
    )
    if not has_any_filter:
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

    def matches_regions(dataset: Dataset, value: Optional[str]) -> bool:
        if value in {None, "All"}:
            return True
        if value == "Single region":
            return dataset.regions_multiple is False
        if value == "Multiple regions":
            return dataset.regions_multiple is True
        return True

    def matches_resolution(dataset: Dataset, value: Optional[tuple[int, int]]) -> bool:
        if value is None:
            return True
        if dataset.resolution_minutes is None:
            return True
        selected_min, selected_max = value
        return selected_min <= dataset.resolution_minutes <= selected_max

    def matches_time_coverage(dataset: Dataset, value: Optional[tuple[int, int]]) -> bool:
        if value is None:
            return True
        selected_start, selected_end = value
        dataset_start = _parse_year(dataset.time_coverage.start_date)
        dataset_end = _parse_year(dataset.time_coverage.end_date)
        if dataset_start is None or dataset_end is None:
            return True
        return dataset_start <= selected_end and dataset_end >= selected_start

    def matches_duration(dataset: Dataset, value: Optional[int]) -> bool:
        if value is None or value == 0:
            return True
        if dataset.duration_months is None:
            return True
        return dataset.duration_months >= value

    supported_fields = ["domain", "type", "horizons", "license", "features"]
    filtered = []
    for ds in datasets:
        if (
            all(matches(ds, f, filters.get(f, [])) for f in supported_fields)
            and matches_regions(ds, regions_value)
            and matches_resolution(ds, resolution_value)
            and matches_time_coverage(ds, time_coverage_value)
            and matches_duration(ds, duration_value)
        ):
            filtered.append(ds)
    return filtered


def render_filter_sidebar(datasets: list[Dataset]) -> dict:
    """
    Renders sidebar filters for domain, type, horizons, features, license,
    region scope, resolution, time coverage, and duration.

    All option values are derived dynamically from the datasets list.
    Never hardcode filter values.

    For list fields (horizons, features): collect all unique values across all datasets.
    For scalar fields: collect all unique non-None values.

    Returns a filters dict compatible with apply_filters().
    Stores selections in st.session_state under keys:
    'filter_domain', 'filter_type', 'filter_horizons', 'filter_features',
    'filter_license', 'filter_regions', 'filter_resolution',
    'filter_time_coverage', 'filter_duration'
    """
    with st.sidebar:
        # Extract unique values for each field
        domains = sorted(set(ds.domain for ds in datasets if ds.domain is not None))
        types = sorted(set(ds.type for ds in datasets if ds.type is not None))
        all_horizons = set()
        for ds in datasets:
            all_horizons.update(ds.horizons)
        horizons = sorted(all_horizons)
        all_features = set()
        for ds in datasets:
            all_features.update(ds.features)
        features = sorted(all_features)
        licenses = sorted(set(ds.license for ds in datasets if ds.license is not None))

        resolutions = sorted(
            set(ds.resolution_minutes for ds in datasets if ds.resolution_minutes is not None)
        )
        has_resolution_slider = len(resolutions) >= 2
        min_res = resolutions[0] if has_resolution_slider else None
        max_res = resolutions[-1] if has_resolution_slider else None

        coverage_years = []
        for ds in datasets:
            start_year = _parse_year(ds.time_coverage.start_date)
            end_year = _parse_year(ds.time_coverage.end_date)
            if start_year is not None:
                coverage_years.append(start_year)
            if end_year is not None:
                coverage_years.append(end_year)
        distinct_coverage_years = sorted(set(coverage_years))
        has_time_coverage_slider = len(distinct_coverage_years) >= 2
        global_min_year = distinct_coverage_years[0] if has_time_coverage_slider else None
        global_max_year = distinct_coverage_years[-1] if has_time_coverage_slider else None

        durations = [ds.duration_months for ds in datasets if ds.duration_months is not None]
        has_duration_slider = len(durations) >= 1
        max_duration = max(durations) if has_duration_slider else 0

        # Initialize session state for each filter
        if "filter_domain" not in st.session_state:
            st.session_state.filter_domain = []
        if "filter_type" not in st.session_state:
            st.session_state.filter_type = []
        if "filter_horizons" not in st.session_state:
            st.session_state.filter_horizons = []
        if "filter_features" not in st.session_state:
            st.session_state.filter_features = []
        if "filter_license" not in st.session_state:
            st.session_state.filter_license = []
        if "filter_regions" not in st.session_state:
            st.session_state.filter_regions = "All"
        if "filter_resolution" not in st.session_state:
            st.session_state.filter_resolution = (min_res, max_res) if has_resolution_slider else None
        if "filter_time_coverage" not in st.session_state:
            st.session_state.filter_time_coverage = (
                (global_min_year, global_max_year) if has_time_coverage_slider else None
            )
        if "filter_duration" not in st.session_state:
            st.session_state.filter_duration = 0

        # Normalize stale slider session values when ranges are unavailable/changed.
        if has_resolution_slider:
            if st.session_state.filter_resolution is None:
                st.session_state.filter_resolution = (min_res, max_res)
        else:
            st.session_state.filter_resolution = None

        if has_time_coverage_slider:
            if st.session_state.filter_time_coverage is None:
                st.session_state.filter_time_coverage = (global_min_year, global_max_year)
        else:
            st.session_state.filter_time_coverage = None

        if has_duration_slider:
            st.session_state.filter_duration = min(
                st.session_state.filter_duration,
                max_duration,
            )
        else:
            st.session_state.filter_duration = 0

        # Count active filters
        active_filters = 0
        if len(st.session_state.filter_domain) > 0:
            active_filters += 1
        if len(st.session_state.filter_type) > 0:
            active_filters += 1
        if len(st.session_state.filter_horizons) > 0:
            active_filters += 1
        if len(st.session_state.filter_features) > 0:
            active_filters += 1
        if len(st.session_state.filter_license) > 0:
            active_filters += 1
        if st.session_state.filter_regions != "All":
            active_filters += 1
        if has_resolution_slider and st.session_state.filter_resolution != (min_res, max_res):
            active_filters += 1
        if (
            has_time_coverage_slider
            and st.session_state.filter_time_coverage != (global_min_year, global_max_year)
        ):
            active_filters += 1
        if st.session_state.filter_duration > 0:
            active_filters += 1

        # Sidebar header with active filter count
        st.markdown(f"### Filters ({active_filters} active)")

        if st.button("Reset all filters", use_container_width=True):
            # Reset both logical filter state and widget-bound state.
            st.session_state.filter_domain = []
            st.session_state.filter_type = []
            st.session_state.filter_horizons = []
            st.session_state.filter_features = []
            st.session_state.filter_license = []
            st.session_state.filter_regions = "All"
            st.session_state.filter_resolution = (min_res, max_res) if has_resolution_slider else None
            st.session_state.filter_time_coverage = (
                (global_min_year, global_max_year) if has_time_coverage_slider else None
            )
            st.session_state.filter_duration = 0

            st.session_state.domain_select = []
            st.session_state.type_select = []
            st.session_state.horizons_select = []
            st.session_state.features_select = []
            st.session_state.license_select = []
            st.session_state.regions_select = "All"
            if has_resolution_slider:
                st.session_state.resolution_select = (min_res, max_res)
            if has_time_coverage_slider:
                st.session_state.time_coverage_select = (global_min_year, global_max_year)
            if has_duration_slider:
                st.session_state.duration_select = 0

            st.rerun()

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

        # Features filter
        st.session_state.filter_features = st.multiselect(
            "Features",
            options=features,
            default=st.session_state.filter_features,
            key="features_select"
        )

        # License filter
        st.session_state.filter_license = st.multiselect(
            "License",
            options=licenses,
            default=st.session_state.filter_license,
            key="license_select"
        )

        st.divider()

        st.session_state.filter_regions = st.radio(
            "Region scope",
            options=["All", "Single region", "Multiple regions"],
            index=["All", "Single region", "Multiple regions"].index(st.session_state.filter_regions),
            key="regions_select",
            horizontal=True,
        )

        if has_resolution_slider and min_res is not None and max_res is not None:
            resolution_value = cast(
                tuple[int, int],
                st.session_state.filter_resolution or (min_res, max_res),
            )
            st.session_state.filter_resolution = st.slider(
                "Resolution (minutes)",
                min_value=min_res,
                max_value=max_res,
                value=resolution_value,
                key="resolution_select",
            )

        st.divider()

        if has_time_coverage_slider and global_min_year is not None and global_max_year is not None:
            time_coverage_value = cast(
                tuple[int, int],
                st.session_state.filter_time_coverage or (global_min_year, global_max_year),
            )
            st.session_state.filter_time_coverage = st.slider(
                "Time coverage (years)",
                min_value=global_min_year,
                max_value=global_max_year,
                value=time_coverage_value,
                key="time_coverage_select",
            )

        if has_duration_slider:
            st.session_state.filter_duration = st.slider(
                "Min. duration (months)",
                min_value=0,
                max_value=max_duration,
                value=st.session_state.filter_duration,
                key="duration_select",
            )

    # Return filters dict compatible with apply_filters()
    return {
        "domain": st.session_state.filter_domain,
        "type": st.session_state.filter_type,
        "horizons": st.session_state.filter_horizons,
        "features": st.session_state.filter_features,
        "license": st.session_state.filter_license,
        "regions": st.session_state.filter_regions,
        "resolution": st.session_state.filter_resolution,
        "time_coverage": st.session_state.filter_time_coverage,
        "duration": st.session_state.filter_duration,
    }
