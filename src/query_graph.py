from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def find_paragraphs_by_keyword(keyword):
    with driver.session() as session:
        result = session.run("""
        MATCH (pg:Paragraph)
        WHERE toLower(pg.text) CONTAINS toLower($kw)
        RETURN pg.label AS label, pg.group_id AS group_id, substring(pg.text, 0, 300) AS preview
        ORDER BY pg.group_id
        LIMIT 10
        """, kw=keyword)
        return result.data()

def find_paragraphs_in_section(section_label):
    with driver.session() as session:
        result = session.run("""
        MATCH (s:Section {name: $section_label})-[:CONTAINS]->(pg:Paragraph)
        RETURN pg.label AS label, substring(pg.text, 0, 300) AS preview
        """, section_label=section_label)
        return result.data()

def get_paragraph_full_chain(label):
    with driver.session() as session:
        result = session.run("""
        MATCH (p:Part)-[:CONTAINS]->(c:Chapter)-[:CONTAINS]->(s:Section)-[:CONTAINS]->(pg:Paragraph {label: $label})
        RETURN p.name AS part, c.name AS chapter, s.name AS section, pg.text AS paragraph
        LIMIT 1
        """, label=label)
        return result.single()

# === Example Usage ===
if __name__ == "__main__":
    print("🔍 Paragraphs containing 'disability':")
    for row in find_paragraphs_by_keyword("disability"):
        print(f"- [{row['label']}] {row['preview']}")

    print("\n🔗 Full context for a paragraph:")
    result = get_paragraph_full_chain("section-6")
    if result:
        print(f"Part: {result['part']}\nChapter: {result['chapter']}\nSection: {result['section']}\nText: {result['paragraph'][:300]}")
