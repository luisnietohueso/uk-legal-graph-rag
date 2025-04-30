import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# === Config ===
INPUT_JSON = "data/equality_act_paragraphs_fixed.json"
FAISS_INDEX_PATH = "data/faiss_index.idx"
METADATA_PATH = "data/faiss_metadata.json"

# === Load Paragraphs ===
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

print("🧪 First record keys:")
print(data[0].keys())

# Auto-detect the correct paragraph key
possible_keys = ["Paragraph Text", "Text", "text", "paragraph_text"]
for key in possible_keys:
    if key in data[0]:
        print(f"✅ Using key: '{key}' for paragraph text")
        texts = [item[key] for item in data]
        break
else:
    raise KeyError("❌ Could not find a valid paragraph text key in the data.")

print(f"✅ Loaded {len(texts)} paragraphs")

# === Load Model ===
print("🔍 Loading embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Embed Texts ===
print("📐 Encoding texts...")
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# === Save FAISS Index ===
print("💾 Saving FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
faiss.write_index(index, FAISS_INDEX_PATH)

# === Save Metadata ===
with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done! Saved FAISS index to: {FAISS_INDEX_PATH}")
print(f"📎 Saved metadata to: {METADATA_PATH}")
