from neo4j import GraphDatabase
import json
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


PARAGRAPH_FILE = "data/equality_act_paragraphs_with_refs.json"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_graph(tx, para):
    part = para.get("Part", "")
    chapter = para.get("Chapter", "")
    section = para.get("Section", "")
    label = para.get("Label", "")
    text = para.get("Text", "")
    group_id = para.get("Group ID", "")

    tx.run("""
        MERGE (p:Part {name: $part})
        MERGE (c:Chapter {name: $chapter})
        MERGE (s:Section {name: $section})
        MERGE (pg:Paragraph {label: $label, text: $text, group_id: $group_id})

        MERGE (p)-[:CONTAINS]->(c)
        MERGE (c)-[:CONTAINS]->(s)
        MERGE (s)-[:CONTAINS]->(pg)
    """, part=part, chapter=chapter, section=section, label=label, text=text, group_id=group_id)

def import_paragraphs():
    with open(PARAGRAPH_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    with driver.session() as session:
        for item in data:
            session.execute_write(create_graph, item)

    print("✅ Imported all paragraph nodes and relationships.")

if __name__ == "__main__":
    import_paragraphs()