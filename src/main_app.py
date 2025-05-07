# src/main_app.py
import streamlit as st

st.set_page_config(page_title="Legal Graph RAG", layout="wide")
st.title(" UK Legal Graph RAG Assistant")

st.markdown("""
Welcome to the **UK Legal Graph RAG** assistant!

You can:
-  Browse the Equality Act 2010
-  Explore Recent UK Case Law
-  Ask Legal Questions with AI

Use the sidebar  to navigate between sections.

---
Built with  using Streamlit, FAISS, Neo4j, and Ollama.
""")
