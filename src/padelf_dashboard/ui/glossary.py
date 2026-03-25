import streamlit as st


def render_glossary(datasets: list) -> None:
    metadata_fields = {
        "Domain": "Application area of the dataset (e.g. energy, building, transport)",
        "Resolution": "Temporal granularity of measurements in minutes",
        "Horizons": "Forecasting horizon categories supported by the dataset",
        "Type": "How the dataset is distributed",
        "Access": "Whether the dataset is openly downloadable or requires registration",
        "Features": "Types of measured variables included (e.g. E = electrical, W = weather, T = temperature)",
        "Time Coverage": "Start and end year of the data",
        "License": "Usage license governing the dataset",
        "Completeness": "Percentage of key metadata fields that are filled",
    }

    horizon_values = {
        "vst": "Very short-term (seconds to minutes)",
        "st": "Short-term (hours to 1 day)",
        "mt": "Medium-term (days to weeks)",
        "lt": "Long-term (months to years)",
    }

    type_values = {
        "collection": "Curated collection of multiple sources",
        "file_archive": "Downloadable file archive",
        "platform_api": "Accessible via platform or API",
    }

    @st.dialog("Glossary")
    def show_glossary_dialog() -> None:
        st.subheader("Metadata Fields")
        for field, explanation in metadata_fields.items():
            st.markdown(f"**{field}** - {explanation}")

        st.subheader("Filter Values")
        st.caption("Horizons")
        for code, explanation in horizon_values.items():
            st.markdown(f"**{code}** - {explanation}")

        st.caption("Type")
        for code, explanation in type_values.items():
            st.markdown(f"**{code}** - {explanation}")

        st.subheader("Dataset Abbreviations")
        abbreviations: list[tuple[str, str]] = []
        for dataset in datasets:
            if isinstance(dataset, dict):
                abbreviation = str(dataset.get("abbreviation") or "").strip()
                name = str(dataset.get("name") or "").strip()
            else:
                abbreviation = str(getattr(dataset, "abbreviation", "") or "").strip()
                name = str(getattr(dataset, "name", "") or "").strip()

            if abbreviation:
                abbreviations.append((abbreviation, name))

        abbreviations.sort(key=lambda item: item[0].lower())

        if not abbreviations:
            st.caption("No dataset abbreviations available.")
            return

        for abbreviation, name in abbreviations:
            left_col, right_col = st.columns([1, 3])
            with left_col:
                st.markdown(f"**{abbreviation}**")
            with right_col:
                st.markdown(name)

    if st.button("Glossary", key="glossary_button"):
        show_glossary_dialog()
