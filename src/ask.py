import os
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from ollama import Client

# === CONFIG ===
FAISS_INDEX_PATH = "data/faiss_index.idx"
METADATA_PATH = "data/faiss_metadata.json"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "mistral"
TOP_K = 5

# === Load index and metadata ===
index = faiss.read_index(FAISS_INDEX_PATH)
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# === Load model and embedder ===
embedder = SentenceTransformer(EMBED_MODEL_NAME)
ollama_client = Client(host="http://localhost:11434")

def retrieve_chunks(query):
    query_vector = embedder.encode([query])
    distances, indices = index.search(np.array(query_vector), TOP_K)
    results = []
    for i in indices[0]:
        if 0 <= i < len(metadata):
            results.append(metadata[i])
    return results

def format_prompt(query, context_chunks):
    context_text = "\n\n".join(
        f"[{i+1}] {chunk['Text']}" for i, chunk in enumerate(context_chunks)
    )
    return f"""You are a legal assistant. Use the context below to answer the question.

Context:
{context_text}

Question:
{query}

Answer with clear explanation and cite sources like [1], [2].
"""

def ask(query):
    chunks = retrieve_chunks(query)
    prompt = format_prompt(query, chunks)
    print("📨 Sending prompt to Mistral via Ollama...")
    response = ollama_client.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
    print("\n📜 Answer:\n")
    print(response["message"]["content"])
    print("\n🔎 Sources:")
    for i, chunk in enumerate(chunks):
        print(f"[{i+1}] {chunk['Text'][:100]}...")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ask.py \"your question here\"")
    else:
        ask(" ".join(sys.argv[1:]))
