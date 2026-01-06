
#src/padelf_dashboard/data/schema.py
from __future__ import annotations
import re

#dataset_io : stable slug, only lowercase letters, numbers, underscores, hyphens
DATASET_ID_PATTERN = re.compile(r"^[a-z0-9_-]+$")

#enums for metadata fields (has to be kept in sync with metadata/datasets.yaml)
DATASET_TYPE_ENUM = {"collection", "file_archive", "platform_api"}
DOMAIN_ENUM = {"system", "residential", "industrial", "unknown"}
HORIZON_ENUM = {"vst", "st", "mt", "lt"}
