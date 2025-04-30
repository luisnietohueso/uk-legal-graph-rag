
# Legal Graph RAG: UK Equality Act and Case Law Assistant

## Project Overview

This project builds a **Retrieval-Augmented Generation (RAG) system** for UK law, combining:
- The **Equality Act 2010** (full legislation)
- **Recent UK Case Law** (parsed from the Find Case Law API)
- A **Knowledge Graph** (Neo4j)
- **Semantic Search** (FAISS)
- **Local LLM** inference (Ollama + Mistral or Gemma)

The system allows users to:
- Search UK legislation by keyword
- Explore recent real-world cases
- Ask legal questions and get AI-generated answers, based only on official sources

Built using **Streamlit**, **FAISS**, **Neo4j**, **Ollama**, and **Sentence Transformers**.

---

## Features

- Structured parsing of the Equality Act 2010 into Parts, Chapters, Sections, and Paragraphs
- Chunking and semantic embedding using `all-MiniLM-L6-v2`
- Dual FAISS vector retrieval: legislation + case law
- Local RAG pipeline with Mistral or Gemma models (via Ollama)
- Graph database structure with Neo4j for visual exploration
- Streamlit-based web app for easy search and interaction
- Clean citations and source referencing
- Ready for further deployment with Docker

---

## Folder Structure

```
/data/         - Parsed legislation and case law data
/src/
  main_app.py        - Streamlit Home Page
  /pages/
    1_view_graph.py        - Equality Act graph viewer
    2_view_case_law.py     - Case law browser
    3_ask_legal_question.py - Legal RAG Q&A assistant
/tests/       - (optional tests)
/docker/      - (for future dockerization)
requirements.txt
README.md
```

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/your-username/legal-graph-rag.git
cd legal-graph-rag
```

2. Create and activate a Python virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install and run [Ollama](https://ollama.com/) locally for LLM inference.

5. Set up Neo4j (either locally or with Docker).

6. Create a `.env` file inside `/src/`:

```plaintext
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword
```

---

## Running the App

Inside your project folder:

```bash
streamlit run src/main_app.py
```

- Home Page → Project introduction
- Equality Act Viewer → Keyword search in the Act
- Case Law Viewer → Search recent UK cases
- Ask Legal Assistant → Query UK law with AI-generated answers

---

## Models and Data

- Sentence embeddings: `all-MiniLM-L6-v2`
- Local LLM: `mistral` or `gemma:2b` via Ollama
- Data parsed from official UK Government and Judiciary sources (2010–2024)

---

## Notes

- `.env` is excluded from GitHub for security.
- `.idx` and large `.json` files are not uploaded to GitHub.
- Some models may require more than 5GB RAM to run locally (especially Mistral).

---

## License

This project is open source under the **MIT License**.


