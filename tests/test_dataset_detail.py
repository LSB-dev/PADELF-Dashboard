#!/usr/bin/env python3
"""
Test the render_detail function implementation.
Verifies that all required fields are handled correctly and
no crashes occur with sample datasets.
"""
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from padelf_dashboard.data.model import Dataset, TimeCoverage, Access, Citation, SourcePaper
from padelf_dashboard.ui.datasets_detail import render_detail


def create_sample_dataset() -> Dataset:
    """Create a complete sample dataset for testing."""
    return Dataset(
        dataset_id="test-dataset",
        name="Test Dataset",
        abbreviation="TD",
        type="file_archive",
        domain="system",
        resolution_minutes=30,
        features=["load", "weather", "temperature"],
        time_coverage=TimeCoverage(start_date="2020-01-01", end_date="2023-12-31"),
        duration_months=48,
        horizons=["st", "mt"],
        regions_multiple=True,
        access=Access(
            url="https://example.com/dataset",
            access_notes="Available after registration"
        ),
        license="CC-BY-4.0",
        citation=Citation(
            preferred_citation="Smith et al., 2023, Test Dataset",
            bibtex="@dataset{smith2023,\n  author={Smith, J.},\n  year={2023}\n}"
        ),
        source_paper=SourcePaper(
            in_baur_2024=True,
            baur_2024_usage_count=5
        )
    )


def create_minimal_dataset() -> Dataset:
    """Create a minimal dataset with mostly None/empty values."""
    return Dataset(
        dataset_id="minimal-dataset",
        name="Minimal Dataset",
        abbreviation=None,
        type="collection",
        domain="unknown",
        resolution_minutes=None,
        features=[],
        time_coverage=TimeCoverage(start_date="2020-01", end_date=None),
        duration_months=None,
        horizons=[],
        regions_multiple=False,
        access=Access(url="https://example.com", access_notes=""),
        license="unknown",
        citation=Citation(
            preferred_citation="",
            bibtex=None
        ),
        source_paper=SourcePaper(in_baur_2024=False, baur_2024_usage_count=None)
    )


def test_render_detail_with_complete_data():
    """Test render_detail with a complete dataset."""
    dataset = create_sample_dataset()
    
    # Mock streamlit
    with patch('padelf_dashboard.ui.datasets_detail.st') as mock_st:
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        
        try:
            render_detail(dataset)
            print("✓ render_detail executed successfully with complete data")
            
            # Verify key calls were made
            assert mock_st.subheader.called, "subheader should be called"
            assert mock_st.columns.called, "columns should be called"
            assert mock_st.code.call_count >= 1, "code should be called for citations"
            print("✓ All expected Streamlit calls were made")
            
        except Exception as e:
            print(f"✗ Error with complete data: {e}")
            raise


def test_render_detail_with_minimal_data():
    """Test render_detail with minimal/None data."""
    dataset = create_minimal_dataset()
    
    with patch('padelf_dashboard.ui.datasets_detail.st') as mock_st:
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        
        try:
            render_detail(dataset)
            print("✓ render_detail executed successfully with minimal data")
            
            # Should show "No citation available" message
            assert mock_st.info.called, "info should be called for missing citations"
            print("✓ Correctly handled missing citation data")
            
        except Exception as e:
            print(f"✗ Error with minimal data: {e}")
            raise


def test_render_detail_no_abbreviation():
    """Test render_detail when abbreviation is None."""
    dataset = create_sample_dataset()
    dataset.abbreviation = None
    
    with patch('padelf_dashboard.ui.datasets_detail.st') as mock_st:
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        
        try:
            render_detail(dataset)
            print("✓ render_detail handled None abbreviation correctly")
            
            # Verify first subheader call (for dataset name) was called with just the name
            first_subheader_call = mock_st.subheader.call_args_list[0][0][0]
            assert dataset.name in first_subheader_call, "Name should be in first subheader"
            assert "(" not in first_subheader_call, "Should not have abbreviation parentheses"
            print("✓ Subheader correctly formatted without abbreviation")
            
        except Exception as e:
            print(f"✗ Error handling None abbreviation: {e}")
            raise


def test_render_detail_no_bibtex():
    """Test render_detail when bibtex is None (should not render it)."""
    dataset = create_sample_dataset()
    dataset.citation.bibtex = None
    
    with patch('padelf_dashboard.ui.datasets_detail.st') as mock_st:
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        
        try:
            render_detail(dataset)
            print("✓ render_detail handled None bibtex correctly")
            
            # Count code calls - should be 1 (only preferred_citation)
            code_calls = [call for call in mock_st.code.call_args_list 
                         if call[1].get('language') == 'bibtex']
            assert len(code_calls) == 0, "bibtex code block should not be rendered"
            print("✓ BibTeX code block correctly omitted when None")
            
        except Exception as e:
            print(f"✗ Error handling None bibtex: {e}")
            raise


def test_render_detail_list_fields():
    """Test render_detail with list fields (features, horizons)."""
    dataset = create_sample_dataset()
    dataset.features = ["load", "weather", "price"]
    dataset.horizons = ["vst", "st", "mt", "lt"]
    
    with patch('padelf_dashboard.ui.datasets_detail.st') as mock_st:
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        
        try:
            render_detail(dataset)
            print("✓ render_detail handled list fields correctly")
            print(f"  - Features: {dataset.features}")
            print(f"  - Horizons: {dataset.horizons}")
            
        except Exception as e:
            print(f"✗ Error handling list fields: {e}")
            raise


def test_render_detail_empty_lists():
    """Test render_detail with empty lists."""
    dataset = create_sample_dataset()
    dataset.features = []
    dataset.horizons = []
    
    with patch('padelf_dashboard.ui.datasets_detail.st') as mock_st:
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        
        try:
            render_detail(dataset)
            print("✓ render_detail handled empty lists correctly")
            
        except Exception as e:
            print(f"✗ Error handling empty lists: {e}")
            raise


def test_import_in_app():
    """Test that render_detail can be imported in app.py."""
    try:
        from padelf_dashboard.ui.datasets_detail import render_detail
        print("✓ render_detail successfully imported")
    except ImportError as e:
        print(f"✗ Failed to import render_detail: {e}")
        raise


if __name__ == "__main__":
    print("Running dataset detail view tests...\n")
    
    test_import_in_app()
    print()
    
    test_render_detail_with_complete_data()
    print()
    
    test_render_detail_with_minimal_data()
    print()
    
    test_render_detail_no_abbreviation()
    print()
    
    test_render_detail_no_bibtex()
    print()
    
    test_render_detail_list_fields()
    print()
    
    test_render_detail_empty_lists()
    print()
    
    print("✅ All tests passed!")
