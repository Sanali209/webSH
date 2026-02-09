import pytest
import polars as pl
from unittest.mock import MagicMock
from core.search import HybridSearcher

@pytest.fixture
def mock_db_manager():
    return MagicMock()

def test_rrf_calculation_mixed_results(mock_db_manager):
    """
    Verify RRF score calculation when both text and vector results are present.
    """
    searcher = HybridSearcher(database_manager=mock_db_manager)

    # Mock Text Results
    text_data = {
        "entity_id": ["A", "B", "C"],
        "filename": ["fileA", "fileB", "fileC"],
        "rank_text": [0, 1, 2] # A=1st, B=2nd, C=3rd
    }
    text_df = pl.DataFrame(text_data)

    # Mock Vector Results
    vector_data = {
        "entity_id": ["B", "A", "D"],
        "rank_vector": [0, 1, 2] # B=1st, A=2nd, D=3rd
    }
    vector_df = pl.DataFrame(vector_data)

    # Calculate RRF with k=1 for simple math
    # Score = 1/(1+rank_text) + 1/(1+rank_vector)
    # A: 1/(1+0) + 1/(1+1) = 1 + 0.5 = 1.5
    # B: 1/(1+1) + 1/(1+0) = 0.5 + 1 = 1.5
    # C: 1/(1+2) + 0 = 0.33
    # D: 0 + 1/(1+2) = 0.33

    result = searcher.reciprocal_rank_fusion(text_df, vector_df, k=1)

    # Top 2 should be A and B (or B and A)
    top_ids = result.head(2)["entity_id"].to_list()
    assert "A" in top_ids
    assert "B" in top_ids

    # Check D is included (outer join)
    assert "D" in result["entity_id"].to_list()

def test_rrf_text_only(mock_db_manager):
    """Verify behavior when only text results exist."""
    searcher = HybridSearcher(database_manager=mock_db_manager)

    text_df = pl.DataFrame({
        "entity_id": ["A", "B"],
        "rank_text": [0, 1]
    })
    vector_df = pl.DataFrame()

    result = searcher.reciprocal_rank_fusion(text_df, vector_df, k=1)

    assert len(result) == 2
    assert result["rrf_score"][0] > result["rrf_score"][1]
    assert result["entity_id"][0] == "A"

def test_rrf_vector_only(mock_db_manager):
    """Verify behavior when only vector results exist."""
    searcher = HybridSearcher(database_manager=mock_db_manager)

    text_df = pl.DataFrame()
    vector_df = pl.DataFrame({
        "entity_id": ["X", "Y"],
        "rank_vector": [0, 1]
    })

    result = searcher.reciprocal_rank_fusion(text_df, vector_df, k=1)

    assert len(result) == 2
    assert result["entity_id"][0] == "X"

def test_text_search_calls_db(mock_db_manager):
    """Verify text search interacts with DB manager correctly."""
    searcher = HybridSearcher(database_manager=mock_db_manager)

    # Mock Core Table
    mock_table = MagicMock()
    # Mock to_polars return
    mock_table.to_polars.return_value = pl.DataFrame({
        "filename": ["test_doc.txt", "image.png"],
        "tags": [["work"], ["personal"]]
    })
    # search() usually returns a query builder, let's mock the exception path fallback
    # causing it to hit to_polars() and filter manually
    mock_table.search.side_effect = Exception("No FTS index")

    mock_db_manager.get_core_table.return_value = mock_table

    results = searcher.search_text("test")

    assert len(results) == 1
    assert results["filename"][0] == "test_doc.txt"
