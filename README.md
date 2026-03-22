# PADELF-Dashboard

## Overview

PADELF-Dashboard is an interactive Streamlit web application that enables researchers and practitioners to explore and discover electric load forecasting datasets from 43+ publicly available sources, streamlining the dataset selection process for load forecasting research and applications.

Dashboard complete locally; deployment platform pending.

## Data Source

This dashboard pulls dataset metadata from [Publicly-Available-Datasets-For-Electric-Load-Forecasting](../Publicly-Available-Datasets-For-Electric-Load-Forecasting) repository. The dashboard loads dataset definitions from the `datasets.yaml` file generated from the README.md catalog.

## Docker Deployment

Prerequisites: Docker and Docker Compose.

- Build: `docker compose build`
- Start: `docker compose up -d`
- Access: http://localhost:8501
- Stop: `docker compose down`

Note: For production, place a reverse proxy (e.g., nginx) in front to terminate HTTPS and route traffic to the target domain load-datasets.ipa.fraunhofer.de.
