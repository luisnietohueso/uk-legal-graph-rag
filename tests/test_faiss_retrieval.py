import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import faiss
import numpy as np
import pytest
from sentence_transformers import SentenceTransformer
from src.ask import embed_query, retrieve_top_k, format_context

# === Constants ===
FAISS_INDEX_PATH = "data/faiss_index.idx"
METADATA_PATH = "data/faiss_metadata.json"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

@pytest.fixture(scope="module")
def load_resources():
    model = SentenceTransformer(EMBEDDING_MODEL)
    index = faiss.read_index(FAISS_INDEX_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return model, index, metadata

def test_embed_query_and_retrieve(load_resources):
    model, index, metadata = load_resources
    query = "What protections exist for disability discrimination?"

    query_vec = embed_query(query, model)
    assert isinstance(query_vec, np.ndarray)
    assert query_vec.shape[0] > 0

    top_k = 5
    results = retrieve_top_k(query_vec, index, metadata, top_k=top_k)

    assert isinstance(results, list)
    assert len(results) > 0
    for item in results:
        assert "Text" in item or "Paragraph Text" in item

def test_format_context(load_resources):
    _, _, metadata = load_resources
    context = format_context(metadata[:2])  # Just test with first 2 items

    assert isinstance(context, str)
    assert "[1]" in context or "[2]" in context
