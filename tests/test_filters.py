import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from padelf_dashboard.ui.filters import apply_filters
from padelf_dashboard.data.model import Dataset, TimeCoverage, Access, Citation, SourcePaper

# Helper to create Dataset

def make_ds(**kwargs):
    defaults = dict(
        dataset_id="id",
        name="name",
        abbreviation=None,
        type="collection",
        domain="system",
        resolution_minutes=15,
        features=["load", "weather"],
        time_coverage=TimeCoverage(start_date="2020-01", end_date="2021-01"),
        duration_months=12,
        horizons=["st", "mt"],
        regions_multiple=False,
        access=Access(url="https://example.com", access_notes=""),
        license="open",
        citation=Citation(preferred_citation="cite", bibtex=None),
        source_paper=SourcePaper(in_baur_2024=False, baur_2024_usage_count=None),
    )
    defaults.update(kwargs)
    return Dataset(**defaults)

import pytest

def test_no_filters_returns_all():
    ds1 = make_ds(dataset_id="a")
    ds2 = make_ds(dataset_id="b")
    result = apply_filters({}, [ds1, ds2])
    assert set(d.dataset_id for d in result) == {"a", "b"}

def test_single_filter_by_domain():
    ds1 = make_ds(dataset_id="a", domain="system")
    ds2 = make_ds(dataset_id="b", domain="residential")
    result = apply_filters({"domain": ["system"]}, [ds1, ds2])
    assert [d.dataset_id for d in result] == ["a"]

def test_multiple_filters_and_logic():
    ds1 = make_ds(dataset_id="a", domain="system", type="collection")
    ds2 = make_ds(dataset_id="b", domain="system", type="file_archive")
    ds3 = make_ds(dataset_id="c", domain="residential", type="collection")
    filters = {"domain": ["system"], "type": ["collection"]}
    result = apply_filters(filters, [ds1, ds2, ds3])
    assert [d.dataset_id for d in result] == ["a"]

def test_empty_list_for_field_ignored():
    ds1 = make_ds(dataset_id="a", domain="system")
    ds2 = make_ds(dataset_id="b", domain="residential")
    filters = {"domain": [], "type": ["collection"]}
    result = apply_filters(filters, [ds1, ds2])
    # Only type filter applied
    assert all(d.type == "collection" for d in result)

def test_list_field_horizons_matched():
    ds1 = make_ds(dataset_id="a", horizons=["st", "mt"])
    ds2 = make_ds(dataset_id="b", horizons=["lt"])
    filters = {"horizons": ["st"]}
    result = apply_filters(filters, [ds1, ds2])
    assert [d.dataset_id for d in result] == ["a"]

def test_none_field_value_handled():
    ds1 = make_ds(dataset_id="a", license="unknown")  # Use a non-matching string
    ds2 = make_ds(dataset_id="b", license="open")
    filters = {"license": ["open"]}
    result = apply_filters(filters, [ds1, ds2])
    assert [d.dataset_id for d in result] == ["b"]