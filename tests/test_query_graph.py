import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch
from src.query_graph import find_paragraphs_by_keyword, find_paragraphs_in_section, get_paragraph_full_chain

# Sample fake Neo4j return data
sample_data = [{"label": "section-6", "group_id": "G1", "preview": "Disability is defined as..."}]
chain_data = {
    "part": "Part 2", "chapter": "Chapter 1", "section": "Section 6", "paragraph": "This paragraph defines disability..."
}

@patch("src.query_graph.driver")
def test_find_paragraphs_by_keyword(mock_driver):
    mock_session = MagicMock()
    mock_session.run.return_value.data.return_value = sample_data
    mock_driver.session.return_value.__enter__.return_value = mock_session

    results = find_paragraphs_by_keyword("disability")
    assert isinstance(results, list)
    assert "label" in results[0]

@patch("src.query_graph.driver")
def test_find_paragraphs_in_section(mock_driver):
    mock_session = MagicMock()
    mock_session.run.return_value.data.return_value = sample_data
    mock_driver.session.return_value.__enter__.return_value = mock_session

    results = find_paragraphs_in_section("Section 6")
    assert isinstance(results, list)
    assert "label" in results[0]

@patch("src.query_graph.driver")
def test_get_paragraph_full_chain(mock_driver):
    mock_session = MagicMock()
    mock_session.run.return_value.single.return_value = chain_data
    mock_driver.session.return_value.__enter__.return_value = mock_session

    result = get_paragraph_full_chain("section-6")
    assert isinstance(result, dict)
    assert "part" in result and "paragraph" in result
