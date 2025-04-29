# src/pages/3_ask_legal_question.py

import streamlit as st
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama

st.set_page_config(page_title="Ask Legal Question", layout="wide")  # <-- MUST be here, FIRST!

# === Config ===
K = 5
FAISS_LEGISLATION_INDEX = "data/faiss_index_with_refs.idx"
FAISS_LEGISLATION_META = "data/faiss_metadata_with_refs.json"
FAISS_CASES_INDEX = "data/faiss_index_cases.idx"
FAISS_CASES_META = "data/faiss_metadata_cases.json"

# === Load Embedding Model ===
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# === Load FAISS Indexes and Metadata ===
@st.cache_resource
def load_faiss_and_metadata(index_path, meta_path):
    index = faiss.read_index(index_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata

faiss_legislation, metadata_legislation = load_faiss_and_metadata(FAISS_LEGISLATION_INDEX, FAISS_LEGISLATION_META)
faiss_cases, metadata_cases = load_faiss_and_metadata(FAISS_CASES_INDEX, FAISS_CASES_META)

# === Streamlit UI ===
st.title("🤖 Ask a Legal Question")

question = st.text_input("🔍 Enter your legal question:", "")

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        # === Encode Query ===
        query_embedding = model.encode([question])
        query_embedding = np.array(query_embedding).astype(np.float32)

        # === Search FAISS ===
        D_leg, I_leg = faiss_legislation.search(query_embedding, K)
        D_case, I_case = faiss_cases.search(query_embedding, K)

        retrieved_chunks = []

        # === Collect Legislation Chunks ===
        for idx in I_leg[0]:
            if idx == -1:
                continue
            item = metadata_legislation[idx]
            ref = f"Equality Act - {item.get('Label', 'Unknown')}"
            retrieved_chunks.append((ref, item["Text"]))

        # === Collect Case Law Chunks ===
        for idx in I_case[0]:
            if idx == -1:
                continue
            item = metadata_cases[idx]
            ref = f"Case Law - {item.get('case_title', 'Unknown')}"
            retrieved_chunks.append((ref, item["text"]))

        # === Build Prompt ===
        context = "\n\n".join([f"[{i+1}] {ref}\n{txt}" for i, (ref, txt) in enumerate(retrieved_chunks)])
        prompt = f"""
You are a helpful UK legal assistant. Use only the context below to answer the question, citing the references.

Context:
{context}

Question: {question}

Answer:
"""

        st.info("📨 Sending to Mistral model via Ollama... Please wait.")

        # === Call LLM ===
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )

        # === Show Results ===
        st.subheader("📜 Answer")
        st.markdown(response["message"]["content"])

        st.subheader("🔎 Sources")
        for i, (ref, _) in enumerate(retrieved_chunks):
            st.markdown(f"[{i+1}] {ref}")
