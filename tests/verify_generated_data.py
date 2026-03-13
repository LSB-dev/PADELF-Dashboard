#!/usr/bin/env python3
"""
Verify that the generated datasets.yaml can be loaded by the Dashboard app logic.
"""
import sys
import os
from pathlib import Path

# Add src to path so we can import padelf_dashboard
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from padelf_dashboard.data.client import MetadataSource, load_datasets

def verify_generated_data():
    datasets_yaml_path = os.getenv("PADELF_LOCAL_YAML")
    if not datasets_yaml_path:
        print(
            "PADELF_LOCAL_YAML is not set; skipping metadata verification.\n"
            "Set PADELF_LOCAL_YAML to the local datasets.yaml path to enable this check."
        )
        sys.exit(0)

    datasets_yaml = Path(datasets_yaml_path)

    if not datasets_yaml.exists():
        print(f"Error: {datasets_yaml} does not exist.")
        sys.exit(1)
        
    print(f"Loading metadata from {datasets_yaml}...")
    try:
        datasets = load_datasets(MetadataSource(path=datasets_yaml))
        print(f"Success! Loaded {len(datasets)} datasets.")
        
        # Print some details to confirm
        print("\nFirst 3 datasets:")
        for d in datasets[:3]:
            print(f"- {d.dataset_id}: {d.name} (Start: {d.time_coverage.start_date})")
            
    except Exception as e:
        print(f"\nFailed to load datasets: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_generated_data()
