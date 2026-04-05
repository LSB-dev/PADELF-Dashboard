# Contributing to PADELF-Dashboard

## Getting Started

Thank you for contributing to PADELF-Dashboard. See README.md for a project overview and local setup instructions before starting implementation work.

## Development Setup

See the Development Setup section in README.md.

## How to Contribute

### Bug Reports

Use GitHub Issues for bug reports. Include clear steps to reproduce, expected versus actual behavior, and your browser and Python version.

### Feature Requests

Use GitHub Issues with the label "enhancement". Describe the use case and expected behavior.

### Code Contributions

1. Fork the repo and create a feature branch from `main`.
2. Implement your changes.
3. Test locally with `streamlit run src/padelf_dashboard/app.py` and verify the UI behaves correctly.
4. Run tests: `pytest tests/`
5. Open a pull request with a descriptive title. Include a screenshot if the change affects the UI.

## Code Guidelines

**Python style**: Follow PEP 8. Use type hints where practical.

**UI components**: Use AgGrid (via `streamlit-ag-grid`) for tables, not `st.dataframe`. Use `st.dialog` for modal overlays. Keep the sidebar for filters only.

**Data layer**: The dashboard must not modify or write data. It is a read-only consumer of `datasets_full.yaml` from the Catalog repo. Any changes to dataset metadata belong in the Catalog repo, not here.

**Tests**: Add or update tests in `tests/` for any new logic. UI-only changes don't require tests but should be manually verified.

## Pull Request Guidelines

Keep pull requests focused on a single change. Reference the related GitHub Issue when applicable, and ensure CI passes before merge.
