from padelf_dashboard.data.model import (
    Access,
    Citation,
    Dataset,
    SourcePaper,
    TimeCoverage,
)
from padelf_dashboard.ui.results import pick_random_dataset, search_datasets


def _make_dataset(
    dataset_id: str,
    name: str,
    abbreviation: str | None,
    domain: str,
) -> Dataset:
    return Dataset(
        dataset_id=dataset_id,
        name=name,
        abbreviation=abbreviation,
        type="file_archive",
        domain=domain,
        time_coverage=TimeCoverage(start_date="2020-01"),
        access=Access(url="https://example.com"),
        citation=Citation(preferred_citation="cite"),
        source_paper=SourcePaper(in_baur_2024=False),
    )


def test_empty_query_returns_all_datasets():
    datasets = [
        _make_dataset("a", "Alpha", "A", "residential"),
        _make_dataset("b", "Beta", "B", "industrial"),
    ]

    assert search_datasets("", datasets) == datasets
    assert search_datasets("   ", datasets) == datasets


def test_query_matches_name_case_insensitive():
    datasets = [
        _make_dataset("a", "My Data", "MD", "residential"),
        _make_dataset("b", "Other", "OT", "industrial"),
    ]

    results = search_datasets("my d", datasets)
    assert len(results) == 1
    assert results[0].dataset_id == "a"


def test_query_matches_abbreviation_case_insensitive():
    datasets = [
        _make_dataset("a", "Alpha", "ABC", "residential"),
        _make_dataset("b", "Beta", "DEF", "industrial"),
    ]

    results = search_datasets("abc", datasets)
    assert len(results) == 1
    assert results[0].dataset_id == "a"


def test_query_matches_domain():
    datasets = [
        _make_dataset("a", "Alpha", "A", "residential"),
        _make_dataset("b", "Beta", "B", "industrial"),
    ]

    results = search_datasets("industrial", datasets)
    assert len(results) == 1
    assert results[0].dataset_id == "b"


def test_none_abbreviation_does_not_crash():
    datasets = [
        _make_dataset("a", "Alpha", None, "residential"),
    ]

    results = search_datasets("alpha", datasets)
    assert len(results) == 1
    assert results[0].dataset_id == "a"


def test_pick_random_dataset_returns_none_for_empty_input():
    assert pick_random_dataset([]) is None


def test_pick_random_dataset_returns_dataset_from_input_list():
    datasets = [
        _make_dataset("a", "Alpha", "A", "residential"),
        _make_dataset("b", "Beta", "B", "industrial"),
    ]

    result = pick_random_dataset(datasets)

    assert result in datasets
