import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama

# === Load Embedding Model ===
print("🔍 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Load Legislation FAISS Index and Metadata ===
faiss_legislation = faiss.read_index("data/faiss_index_with_refs.idx")
with open("data/faiss_metadata_with_refs.json", "r", encoding="utf-8") as f:
    metadata_legislation = json.load(f)

# === Load Case Law FAISS Index and Metadata ===
faiss_cases = faiss.read_index("data/faiss_index_cases.idx")
with open("data/faiss_metadata_cases.json", "r", encoding="utf-8") as f:
    metadata_cases = json.load(f)

# === User Query ===
import sys
query = " ".join(sys.argv[1:])
if not query:
    print("❌ No query provided.")
    sys.exit(1)

# === Encode Query ===
query_embedding = model.encode([query])
query_embedding = np.array(query_embedding).astype(np.float32)

# === Retrieve Top-k Results ===
k = 5

D_leg, I_leg = faiss_legislation.search(query_embedding, k)
D_case, I_case = faiss_cases.search(query_embedding, k)

retrieved_chunks = []

# === Collect legislation chunks ===
for idx in I_leg[0]:
    if idx == -1:
        continue
    item = metadata_legislation[idx]
    ref = f"Equality Act - {item.get('Label', 'Unknown')}"  # Use 'Label' instead of 'Reference'
    retrieved_chunks.append((ref, item["Text"]))

# === Collect case law chunks ===
for idx in I_case[0]:
    if idx == -1:
        continue
    item = metadata_cases[idx]
    ref = f"Case Law - {item.get('case_title', 'Unknown')}"  # <-- FIXED HERE
    retrieved_chunks.append((ref, item["text"]))

# === Build Prompt ===
context = "\n\n".join([f"[{i+1}] {ref}\n{txt}" for i, (ref, txt) in enumerate(retrieved_chunks)])
prompt = f"""
You are a helpful UK legal assistant. Use only the context below to answer the question, citing the references.

Context:
{context}

Question: {query}

Answer:
"""

print("📨 Sending prompt to Mistral via Ollama...\n")

# === Call LLM ===
response = ollama.chat(
    model="mistral",
    messages=[{"role": "user", "content": prompt}]
)

print("📜 Answer:\n")
print(response["message"]["content"])

# === Show Sources ===
print("\n🔎 Sources:")
for i, (ref, _) in enumerate(retrieved_chunks):
    print(f"[{i+1}] {ref}")
