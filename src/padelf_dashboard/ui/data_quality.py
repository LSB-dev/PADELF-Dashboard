from typing import List

from padelf_dashboard.data.model import Dataset


def compute_completeness(dataset: Dataset) -> dict:
    return {
        "license": bool(dataset.license and dataset.license != "unknown"),
        "preferred_citation": bool(
            dataset.citation
            and dataset.citation.preferred_citation
            and dataset.citation.preferred_citation.strip()
        ),
        "resolution_minutes": dataset.resolution_minutes is not None,
    }


def completeness_score(dataset: Dataset) -> str:
    completeness = compute_completeness(dataset)
    completed = sum(1 for value in completeness.values() if value)
    return f"{completed}/3"


def missing_fields(dataset: Dataset) -> List[str]:
    completeness = compute_completeness(dataset)
    labels = {
        "license": "License",
        "preferred_citation": "Citation",
        "resolution_minutes": "Resolution",
    }
    return [labels[field] for field, ok in completeness.items() if not ok]