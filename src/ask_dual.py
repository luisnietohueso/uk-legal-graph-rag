import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
import sys

# === Config ===
K = 10   # Retrieve more initially for reranking
FINAL_K = 5

def rerank_with_llm(question, candidates):
    numbered = []
    for i, c in enumerate(candidates):
        clean_text = c['text'][:300].replace('\n', ' ')
        numbered.append(f"[{i+1}] {clean_text}")

    context = "\n\n".join(numbered)

    rerank_prompt = f"""
You are a legal assistant. You will receive a question and 10 legal paragraphs (labeled [1] to [10]).
Rank them from most to least relevant by returning a list of numbers.

Question:
{question}

Paragraphs:
{context}

Return the ranking like this:
[3, 1, 5, 2, 4, 6, 7, 8, 9, 10]
Only return the list. No explanation.
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": rerank_prompt}]
    )
    
    # Parse the returned list
    try:
        text = response["message"]["content"]
        order = eval(text.strip())  # Returns a list like [3,1,5,...]
        return [candidates[i - 1] for i in order if 1 <= i <= len(candidates)]
    except Exception as e:
        print(" Rerank failed, using original order")
        return candidates

# === Load Embedding Model ===
print("🔍 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Load FAISS Indexes + Metadata ===
faiss_legislation = faiss.read_index("data/faiss_index_with_refs.idx")
with open("data/faiss_metadata_with_refs.json", "r", encoding="utf-8") as f:
    metadata_legislation = json.load(f)

faiss_cases = faiss.read_index("data/faiss_index_cases.idx")
with open("data/faiss_metadata_cases.json", "r", encoding="utf-8") as f:
    metadata_cases = json.load(f)

# === Read User Query ===
query = " ".join(sys.argv[1:])
if not query:
    print(" No query provided.")
    sys.exit(1)

query_embedding = model.encode([query])[0]
query_embedding_np = np.array([query_embedding]).astype(np.float32)

# === Retrieve Candidates ===
D_leg, I_leg = faiss_legislation.search(query_embedding_np, K)
D_case, I_case = faiss_cases.search(query_embedding_np, K)

# === Collect all results with source type ===
candidates = []

for idx in I_leg[0]:
    if idx == -1: continue
    item = metadata_legislation[idx]
    text = item["Text"]
    label = item.get("Label", "Unknown")
    embedding = model.encode(text)
    candidates.append({
        "text": text,
        "ref": f"Equality Act - {label}",
        "embedding": embedding
    })

for idx in I_case[0]:
    if idx == -1: continue
    item = metadata_cases[idx]
    text = item["text"]
    title = item.get("case_title", "Unknown")
    embedding = model.encode(text)
    candidates.append({
        "text": text,
        "ref": f"Case Law - {title}",
        "embedding": embedding
    })

# === Cosine Rerank ===
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

for c in candidates:
    c["score"] = cosine_similarity(query_embedding, c["embedding"])

# LLM rerank
reranked_chunks = rerank_with_llm(query, candidates)
top_chunks = reranked_chunks[:FINAL_K]


# === Build Prompt ===
context = "\n\n".join([f"[{i+1}] {c['ref']}\n{c['text']}" for i, c in enumerate(top_chunks)])
prompt = f"""
You are a helpful UK legal assistant. Use only the context below to answer the question, citing the references.

Context:
{context}

Question: {query}

Answer:
"""

print(" Sending prompt to Mistral via Ollama...\n")

# === LLM Call ===
response = ollama.chat(
    model="mistral",
    messages=[{"role": "user", "content": prompt}]
)

print(" Answer:\n")
print(response["message"]["content"])

# === Print Sources ===
print("\n Sources:")
for i, c in enumerate(top_chunks):
    print(f"[{i+1}] {c['ref']}")