import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# === Config ===
INPUT_JSON = "data/parsed_case_paragraphs.json"
FAISS_INDEX_PATH = "data/faiss_index_cases.idx"
METADATA_PATH = "data/faiss_metadata_cases.json"

# === Load Data ===
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# === Load Model ===
print("🔍 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Prepare Texts and Metadata ===
texts = []
metadata = []

for item in data:
    texts.append(item["text"])
    metadata.append({
        "text": item["text"],
        "case_title": item.get("case_id", "Unknown"),  # <-- MAKE SURE we save the title here!
        "paragraph_id": item.get("paragraph_id", "Unknown")
    })

print(f"✅ Loaded {len(texts)} case paragraphs")

# === Embed Texts ===
print("📐 Encoding texts...")
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# === Save to FAISS ===
print("💾 Saving FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
faiss.write_index(index, FAISS_INDEX_PATH)

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"📁 FAISS index saved to: {FAISS_INDEX_PATH}")
print(f"📁 Metadata saved to: {METADATA_PATH}")
