from pathlib import Path

from padelf_dashboard.data.client import MetadataSource, load_datasets


def test_load_empty_list_is_valid():
    fixture = Path(__file__).parent / "fixtures" / "datasets_empty.yaml"
    datasets = load_datasets(MetadataSource(path=fixture))
    assert datasets == []
