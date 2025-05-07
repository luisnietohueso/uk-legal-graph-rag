import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock
from src.import_to_neo4j import create_graph

@pytest.fixture
def mock_tx():
    return MagicMock()

def test_create_graph_runs_cypher(mock_tx):
    sample_para = {
        "Part": "Part 1",
        "Chapter": "Chapter 1",
        "Section": "Section 1",
        "Label": "1",
        "Text": "This is a test paragraph.",
        "Group ID": "G1"
    }

    create_graph(mock_tx, sample_para)

    # Ensure Cypher was run once with correct parameters
    mock_tx.run.assert_called_once()
    args, kwargs = mock_tx.run.call_args

    assert "MERGE (p:Part" in args[0]
    assert kwargs["part"] == "Part 1"
    assert kwargs["chapter"] == "Chapter 1"
    assert kwargs["section"] == "Section 1"
    assert kwargs["label"] == "1"
    assert kwargs["text"] == "This is a test paragraph."
    assert kwargs["group_id"] == "G1"
