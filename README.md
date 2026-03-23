# PADELF-Dashboard

## Overview

PADELF-Dashboard is an interactive Streamlit web application that enables researchers and practitioners to explore and discover electric load forecasting datasets from 43+ publicly available sources, streamlining the dataset selection process for load forecasting research and applications.

Dashboard complete locally; deployment platform pending.

## Data Source

This dashboard pulls dataset metadata from [Publicly-Available-Datasets-For-Electric-Load-Forecasting](https://github.com/LSB-dev/Publicly-Available-Datasets-For-Electric-Load-Forecasting) repository. The dashboard loads dataset definitions from the `datasets.yaml` file generated from the README.md catalog.

## Docker Deployment

Prerequisites: Docker and Docker Compose.

- Build: `docker compose build`
- Start: `docker compose up -d`
- Access: http://localhost:8501
- Stop: `docker compose down`

Note: For production, place a reverse proxy (e.g., nginx) in front to terminate HTTPS and route traffic to the target domain load-datasets.ipa.fraunhofer.de.

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
