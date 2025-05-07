# src/pages/3_ask_legal_question.py

import streamlit as st
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
import re
import io
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import textwrap

st.set_page_config(page_title="Ask Legal Question", layout="wide")

# === Config ===
K = 10       # Retrieve more, rerank later
FINAL_K = 5  # Show top 5
FAISS_LEGISLATION_INDEX = "data/faiss_index_with_refs.idx"
FAISS_LEGISLATION_META = "data/faiss_metadata_with_refs.json"
FAISS_CASES_INDEX = "data/faiss_index_cases.idx"
FAISS_CASES_META = "data/faiss_metadata_cases.json"

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

    try:
        text = response["message"]["content"]
        order = eval(text.strip())
        return [candidates[i - 1] for i in order if 1 <= i <= len(candidates)]
    except Exception as e:
        st.warning(" LLM reranking failed, using original order")
        return candidates

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

def wrap_text(text, max_chars=95):
    return textwrap.wrap(text, width=max_chars)

def generate_pdf(answer_text, sources):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    # Set metadata
    c.setTitle("Legal RAG Answer")
    c.setAuthor("UK Legal Graph RAG Assistant")

    y = height - 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y, "📘 Equality Act Assistant - Legal Response")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(30, y, "UK Legal Assistant - Generated Answer")
    y -= 30

    # Draw the answer text with wrapping
    c.setFont("Helvetica", 10)
    for line in answer_text.split('\n'):
        for wrapped_line in wrap_text(line.strip()):
            if y < 60:
                c.showPage()
                y = height - 50
            c.drawString(30, y, wrapped_line)
            y -= 14

    # Draw sources
    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30, y, "Sources:")
    y -= 20

    c.setFont("Helvetica", 9)
    for i, c_item in enumerate(sources):
        ref_line = f"[{i+1}] {c_item['ref']}"
        for wrapped_ref in wrap_text(ref_line):
            if y < 60:
                c.showPage()
                y = height - 50
            c.drawString(30, y, wrapped_ref)
            y -= 12

        for src_line in c_item["text"].split('\n'):
            for wrapped_src in wrap_text(src_line.strip()):
                if y < 60:
                    c.showPage()
                    y = height - 50
                c.drawString(40, y, wrapped_src)
                y -= 11
        y -= 10  # extra spacing between sources

    c.save()
    buffer.seek(0)
    return buffer


# === Cosine similarity function ===
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# === UI ===
st.title(" Ask a Legal Question")

question = st.text_input(" Enter your legal question:", "")

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        query_embedding = model.encode([question])[0]
        query_embedding_np = np.array(query_embedding).astype(np.float32).reshape(1, -1)


        # Search FAISS
        D_leg, I_leg = faiss_legislation.search(query_embedding_np, K)
        D_case, I_case = faiss_cases.search(query_embedding_np, K)

        candidates = []

                # === Collect + Format Candidates ===
        for idx in I_leg[0]:
            if idx == -1:
                continue
            item = metadata_legislation[idx]
            text = item["Text"]

            # 🎯 Structured legal citation
            part = item.get("Part", "")
            chapter = item.get("Chapter", "")
            section = item.get("Section", "")
            label = item.get("Label", "Unknown")

            ref = f"Equality Act - {label}"  # simple version
            # Optional enhanced version: f"Equality Act - {part} {chapter} {section} ({label})"

            emb = model.encode(text)
            candidates.append({"text": text, "ref": ref, "embedding": emb})

        for idx in I_case[0]:
            if idx == -1:
                continue
            item = metadata_cases[idx]
            text = item["text"]

            raw_title = item.get("case_title", "Unknown")
            pretty_title = raw_title.replace("_", " ").replace(",", ", ")
            ref = f"Case Law - {pretty_title}"

            emb = model.encode(text)
            candidates.append({"text": text, "ref": ref, "embedding": emb})

        # Rerank
        # LLM-based reranking (Mistral will sort best 10 chunks)
        reranked_chunks = rerank_with_llm(question, candidates)
        top_chunks = reranked_chunks[:FINAL_K]



        # Build Prompt
        context = "\n\n".join([f"[{i+1}] {c['ref']}\n{c['text']}" for i, c in enumerate(top_chunks)])
        prompt = f"""
You are a helpful UK legal assistant. Use only the context below to answer the question, citing the references.

Context:
{context}

Question: {question}

Answer:
"""

        st.info(" Sending to Mistral model via Ollama...")

        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response["message"]["content"]

        st.subheader(" Answer")
        # Detect [1], [2], etc. and bold them
        answer_with_links = re.sub(r"\[(\d+)\]", r"[\1](#ref\1)", answer)
        st.markdown(answer_with_links)

        st.subheader(" Sources")
        for i, c in enumerate(top_chunks):
            st.markdown(f"<a name='ref{i+1}'></a>", unsafe_allow_html=True)
            with st.expander(f"[{i+1}] {c['ref']}"):
                st.markdown(c["text"])
        st.subheader(" Download Answer")
        pdf_data = generate_pdf(answer, top_chunks)
        st.download_button(
            label=" Download PDF",
            data=pdf_data,
            file_name="legal_answer.pdf",
            mime="application/pdf"
        )



       
