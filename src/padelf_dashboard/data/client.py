from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.request import urlopen

import yaml

from .model import Dataset

# Default: URL to datasets.yaml in the Publicly-Available-Datasets-For-Electric-Load-Forecasting repo
# TODO: switch to main branch URL after merge
DEFAULT_DATASETS_URL = (
    "https://raw.githubusercontent.com/LSB-dev/"
    "Publicly-Available-Datasets-For-Electric-Load-Forecasting/"
    "feature/add-datasets-yaml/metadata/datasets.yaml"
)  

@dataclass(frozen=True)
class MetadataSource:
    """
    Defines where metadata is loaded from.

    - url: load via HTTP (Raw GitHub URL)
    - path: load from local filesystem (useful for development/tests)
    """
    url: Optional[str] = None
    path: Optional[Path] = None


def _read_text_from_url(url: str) -> str:
    # Standard library HTTP GET request
    with urlopen(url) as resp:  # nosec - controlled URL (project config)
        return resp.read().decode("utf-8")


def _read_text_from_path(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_datasets(source: Optional[MetadataSource] = None) -> List[Dataset]:
    """
    Loads metadata/datasets.yaml and returns a list of validated Dataset objects.

    Rules:
    - Top-level YAML must be a list.
    - Empty content / comments-only file => treated as empty list.
    - Each entry is validated via Pydantic (Dataset.model_validate).
    """

    # Optional overrides (useful for deployment / local dev without code changes)
    env_url = os.getenv("PADELF_METADATA_URL")
    env_path = os.getenv("PADELF_METADATA_PATH")

    if source is None:
        source = MetadataSource(
            url=env_url or DEFAULT_DATASETS_URL,
            path=Path(env_path) if env_path else None,
        )

    if source.path is not None:
        text = _read_text_from_path(source.path)
    elif source.url is not None:
        text = _read_text_from_url(source.url)
    else:
        raise ValueError("No metadata source provided (url or path required).")

    raw = yaml.safe_load(text)

    # YAML can be None if file is empty / comments-only
    if raw is None:
        return []

    if not isinstance(raw, list):
        raise ValueError("datasets.yaml must be a YAML list at the top level.")

    return [Dataset.model_validate(item) for item in raw]
