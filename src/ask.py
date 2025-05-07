import argparse
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ollama import chat

# === Config ===
FAISS_INDEX_PATH = "data/faiss_index.idx"
METADATA_PATH = "data/faiss_metadata.json"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "mistral"  # must be available via `ollama list`

# === Functions ===
def embed_query(query, model):
    return model.encode([query])[0]

def retrieve_top_k(query_embedding, faiss_index, metadata, top_k=5):
    query_embedding = np.array([query_embedding]).astype("float32")
    distances, indices = faiss_index.search(query_embedding, top_k)
    results = []
    for idx in indices[0]:
        if idx < len(metadata):
            results.append(metadata[idx])
    return results

def format_context(paragraphs):
    lines = []
    for i, p in enumerate(paragraphs):
        label = p.get("Label") or p.get("Paragraph Label") or f"({i+1})"
        location = f"{p.get('Part', '')}.{p.get('Chapter', '')}.{p.get('Section', '')}".replace("..", ".")
        lines.append(f"[{i+1}] ({location} {label}) {p.get('Text', p.get('Paragraph Text', ''))}")
    return "\n\n".join(lines)


def ask_llm(context, question):
    prompt = f"""Use the following Equality Act paragraphs to answer the question. Be thorough and cite the references.

Context:
{context}

Question: {question}

Answer:"""

    response = chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# === Main Script ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("question", type=str, help="Legal question to ask")
    parser.add_argument("--top-k", type=int, default=5, help="Number of paragraphs to retrieve (default=5)")
    args = parser.parse_args()

    # Load embedding model
    print(f" Loading embedding model ({EMBEDDING_MODEL})...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Load FAISS + metadata
    print(" Loading FAISS index and metadata...")
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Embed query and retrieve
    print(f" Sending prompt to Mistral via Ollama...\n")
    query_vector = embed_query(args.question, model)
    top_paragraphs = retrieve_top_k(query_vector, index, metadata, top_k=args.top_k)
    context = format_context(top_paragraphs)

    # Generate answer
    answer = ask_llm(context, args.question)
    print("\n Answer:\n")
    print(answer)

    print("\n Sources:")
    for i, para in enumerate(top_paragraphs, start=1):
        label = para.get("Label") or para.get("Paragraph Label") or f"#{i}"
        location = f"{para.get('Part', '')}.{para.get('Chapter', '')}.{para.get('Section', '')}".replace("..", ".")
        print(f"[{i}] {location} {label}: {para.get('Text', para.get('Paragraph Text', ''))[:100]}...")

