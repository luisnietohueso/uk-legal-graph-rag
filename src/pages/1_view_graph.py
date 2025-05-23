import re
import streamlit as st
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
# === Streamlit UI ===
st.set_page_config(page_title="Equality Act Graph Viewer", layout="wide")
st.title("📘 UK Equality Act - Graph Viewer")

query = st.text_input("🔍 Enter keyword to search in paragraphs:", "disability")

# === Cypher Query ===
cypher = '''
MATCH (s:Section)-[:CONTAINS]->(p:Paragraph)
WHERE toLower(p.text) CONTAINS toLower($keyword)
RETURN s.name AS section, p.label AS label, p.group_id AS group_id, p.text AS text
ORDER BY p.group_id
LIMIT 10
'''

# === Run Query ===
results = []
with driver.session() as session:
    rows = session.run(cypher, keyword=query)
    results = rows.data()

# === Display Results ===
# Run Neo4j query
results = []
with driver.session() as session:
    rows = session.run(cypher, keyword=query)
    results = rows.data()

# Render results
if results:
    for row in results:

        anchor = row['label'].replace(" ", "_").replace("section-", "sec_")
        st.markdown(f"<a name='{anchor}'></a>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#201c94;padding:10px;border-left:5px solid #2196f3;'>"
                    f"<h4>{row['section']} - {row['label']}</h4>"
                    f"<b>Group ID:</b> {row['group_id']}</div>", unsafe_allow_html=True)

        # Highlight keyword
        def highlight(text, term):
            return re.sub(f"(?i)({re.escape(term)})", r"<mark>\1</mark>", text)

        highlighted = highlight(row['text'], query)
        st.markdown(f"<div style='margin-bottom:30px;'>{highlighted}</div>", unsafe_allow_html=True)

    # Optional: Navigation at top
    st.sidebar.markdown("### Quick Nav")
    for row in results:
        anchor = row['label'].replace(" ", "_").replace("section-", "sec_")
        st.sidebar.markdown(f"- [{row['label']}](#{anchor})")

else:
    st.info("No results found. Try another keyword.")
