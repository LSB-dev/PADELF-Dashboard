# src/padelf_dashboard/data/model.py
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .schema import (
    DATASET_ID_PATTERN,
    DATASET_TYPE_ENUM,
    DOMAIN_ENUM,
    HORIZON_ENUM,
)



class TimeCoverage(BaseModel):
    """
    Matches the YAML block:
      time_coverage:
        start_date: "YYYY-MM" | "YYYY-MM-DD"
        end_date: "YYYY-MM" | "YYYY-MM-DD" | null
    """
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Access(BaseModel):
    """
    Matches the YAML block:
      access:
        url: "https://..."
        access_notes: "..."
    """
    url: str
    access_notes: str = ""


class Citation(BaseModel):
    """
    Matches the YAML block:
      citation:
        preferred_citation: "..."
        bibtex: null | "..."
    """
    preferred_citation: str
    bibtex: Optional[str] = None


class SourcePaper(BaseModel):
    """
    Matches the YAML block:
      source_paper:
        in_baur_2024: true|false
        baur_2024_usage_count: int|null
    """
    in_baur_2024: bool = False
    baur_2024_usage_count: Optional[int] = None


class Dataset(BaseModel):
    """
    One dataset entry from metadata/datasets.yaml (v0.01).
    """

    dataset_id: str
    name: str
    abbreviation: Optional[str] = None

    type: str
    domain: str

    resolution_minutes: Optional[int] = None
    features: List[str] = Field(default_factory=list)

    time_coverage: TimeCoverage
    duration_months: Optional[int] = None

    horizons: List[str] = Field(default_factory=list)
    regions_multiple: bool = False

    access: Access
    license: str = "unknown"

    citation: Citation
    source_paper: SourcePaper

    # --- Validators (use rules from schema.py) ---

    @field_validator("dataset_id")
    @classmethod
    def validate_dataset_id(cls, v: str) -> str:
        if not DATASET_ID_PATTERN.match(v):
            raise ValueError("dataset_id must match ^[a-z0-9_]+$")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in DATASET_TYPE_ENUM:
            raise ValueError(f"type must be one of {sorted(DATASET_TYPE_ENUM)}")
        return v

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if v not in DOMAIN_ENUM:
            raise ValueError(f"domain must be one of {sorted(DOMAIN_ENUM)}")
        return v

    @field_validator("horizons")
    @classmethod
    def validate_horizons(cls, v: List[str]) -> List[str]:
        invalid = [x for x in v if x not in HORIZON_ENUM]
        if invalid:
            raise ValueError(f"horizons contains invalid values: {invalid}")
        return v
