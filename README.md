<img src="assets/logo_padelf_search.png" width="50%">

# PADELF-Search Dashboard

## Overview

PADELF-Search is an interactive Streamlit web application dashboard that enables researchers and practitioners to explore and discover electric load forecasting datasets from 43+ publicly available sources, streamlining the dataset selection process for load forecasting research and applications.

## Related Work
### pip-package: Easy access to the most popular datasets

![logo padelf pip](assets/logo_padelf_pip.png)

For programmatic access to datasets in Python, use the [PADELF-PIP package](https://github.com/LSB-dev/padelf-pip):

```bash
pip install padelf
```

This dashboard and the package are complementary: use the dashboard for discovery and filtering, and use the package to load selected datasets directly into pandas DataFrames.

### The original data collection

![logo padelf pip](assets/logo_padelf_repo.png)

This dashboard pulls dataset metadata from [Publicly-Available-Datasets-For-Electric-Load-Forecasting](https://github.com/LSB-dev/Publicly-Available-Datasets-For-Electric-Load-Forecasting) repository. 
The dashboard loads dataset definitions from the `datasets.yaml` file generated from the README.md catalog.

## Usage Guide

### Search and Filter

The dashboard provides two ways to find datasets:

- **Text search**: Search by dataset name, abbreviation, or domain using the search bar.
- **Sidebar filters**: Filter by domain, type, forecasting horizon, or license. Multiple selections per filter use OR logic; filters across categories use AND logic.

### Dataset Details

Click any dataset name in the expander list below the results table to see full metadata, including access links, citation information, and source paper references.

### Statistics

Click "Show statistics" below the results table to open a modal with distribution charts for domain, type, horizons, and resolution. Two tabs show statistics for all datasets and for the current filtered results.

### Data Quality

Each dataset has a completeness score (0/3 to 3/3) based on three key metadata fields: license, citation, and temporal resolution. Incomplete datasets show which fields are missing in the detail view.


## Run it on your own
### Docker Deployment

Prerequisites: Docker and Docker Compose.

- Build: `docker compose build`
- Start: `docker compose up -d`
- Access: http://localhost:8501
- Stop: `docker compose down`

Note: For production, place a reverse proxy (e.g., nginx) in front to terminate HTTPS and route traffic to the target domain load-datasets.ipa.fraunhofer.de.

### Repository Structure

The project follows a src layout:

```
.
├── README.md
├── Dockerfile / docker-compose.yml   # Container deployment
├── pyproject.toml                    # Project metadata and dependencies
├── assets/                           # Logos and icons
├── src/padelf_dashboard/
│   ├── app.py                        # Streamlit entry point
│   ├── data/
│   │   ├── client.py                 # Fetches and caches datasets_full.yaml from Catalog repo
│   │   ├── model.py                  # Data classes / domain objects
│   │   └── schema.py                 # Pydantic schema for validation
│   └── ui/
│       ├── filters.py                # Sidebar filter panel (domain, type, horizon, license)
│       ├── results.py                # AgGrid results table with click-based row selection
│       ├── datasets_detail.py        # Detail view for selected dataset (st.dialog modal)
│       ├── statistics.py             # Distribution charts (domain, type, horizons, resolution)
│       ├── data_quality.py           # Completeness score logic (0/3 to 3/3)
│       └── glossary.py               # Tooltip / hover explanations
└── tests/
    ├── test_filters.py
    ├── test_search.py
    ├── test_dataset_detail.py
    ├── test_integration_render_detail.py
    ├── test_load_metadata.py
    └── verify_generated_data.py
```

### Architecture

The dashboard consumes `datasets_full.yaml` as its sole data source, fetched from the Catalog repository at https://github.com/LSB-dev/Publicly-Available-Datasets-For-Electric-Load-Forecasting. In this flow, `client.py` is responsible for fetching and caching the file. The UI layer is split across focused modules: `filters.py` provides the sidebar filter panel, `results.py` renders the main AgGrid table (chosen over native `st.dataframe` to support click-based row selection without checkboxes), `datasets_detail.py` renders the detail modal using `st.dialog`, `statistics.py` renders distribution charts, and `data_quality.py` computes completeness scoring. The application entry point is `app.py`.

### Development Setup

1. Clone the repo.
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install in editable mode: `pip install -e .`
4. Run locally: `streamlit run src/padelf_dashboard/app.py`
5. Run tests: `pytest tests/`

