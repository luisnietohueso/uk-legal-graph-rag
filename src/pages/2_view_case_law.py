# src/view_case_law.py

import streamlit as st
import json
import os

# === Config ===
DATA_PATH = "data/case_law_results.json"

# === Load Data ===
if not os.path.exists(DATA_PATH):
    st.error(f"Case law data not found at {DATA_PATH}. Please fetch cases first!")
    st.stop()

with open(DATA_PATH, "r", encoding="utf-8") as f:
    cases = json.load(f)

# === Streamlit UI ===
st.set_page_config(page_title="Find Case Law Viewer", layout="wide")
st.title("⚖️ Recent UK Case Law Viewer")

# === Search and Filters ===
search_query = st.text_input("🔎 Search cases by keywords (title or summary):", "")

filtered_cases = []

if search_query:
    search_query_lower = search_query.lower()
    for case in cases:
        title_match = search_query_lower in case.get("title", "").lower()
        summary_match = search_query_lower in case.get("summary", "").lower()
        if title_match or summary_match:
            filtered_cases.append(case)
else:
    filtered_cases = cases

st.markdown(f"**Showing {len(filtered_cases)} cases.**")

# === Display Cases ===
if filtered_cases:
    for case in filtered_cases:
        st.markdown(f"## {case['title']}")
        st.markdown(f"**Updated:** {case['updated']}")
        if case.get("summary"):
            st.markdown(f"**Summary:** {case['summary']}")
        st.markdown(f"[📄 View PDF]({case['link_pdf']})")
        st.markdown(f"[🧾 View XML]({case['link_xml']})")
        st.markdown("---")
else:
    st.info("No matching cases found.")

