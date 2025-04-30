import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# === Config ===
INPUT_JSON = "data/equality_act_paragraphs_with_refs.json"
FAISS_INDEX_PATH = "data/faiss_index_with_refs.idx"
METADATA_PATH = "data/faiss_metadata_with_refs.json"

# === Load Paragraphs ===
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# Auto-detect the correct key for paragraph text
possible_keys = ["Text", "Paragraph Text", "paragraph_text"]
text_key = next((k for k in data[0].keys() if k in possible_keys), None)
if not text_key:
    raise KeyError(f"No paragraph text key found in: {list(data[0].keys())}")

texts = [item[text_key] for item in data]
print(f"✅ Loaded {len(texts)} paragraphs using key: '{text_key}'")

# === Load Embedding Model ===
print("🔍 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Generate Embeddings ===
print("📐 Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# === Create FAISS Index ===
print("💾 Saving FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
faiss.write_index(index, FAISS_INDEX_PATH)

# === Save Metadata ===
with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"📁 FAISS index saved to: {FAISS_INDEX_PATH}")
print(f"📁 Metadata saved to: {METADATA_PATH}")
