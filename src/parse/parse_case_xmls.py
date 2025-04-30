import os
import json
import xml.etree.ElementTree as ET
from tqdm import tqdm

# === Config ===
CASE_XML_FOLDER = "data/case_xmls"
OUTPUT_JSON = "data/parsed_case_paragraphs.json"

def clean_text(text):
    if text:
        return " ".join(text.split())
    return ""

def extract_paragraphs_from_xml(filepath):
    paragraphs = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Namespace detection
        ns = {'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0'}

        # Find the body
        body = root.find(".//akn:body", ns)
        if body is None:
            body = root.find(".//akn:judgment", ns)  # fallback for older structure

        if body is None:
            return []

        # Find all paragraphs (like <p> or <paragraph>)
        for para in body.findall(".//akn:p", ns):
            para_text = clean_text("".join(para.itertext()))
            if para_text:
                paragraphs.append(para_text)

        if not paragraphs:
            # Fallback: if no <p> tags, grab any text chunks
            for elem in body.iter():
                if elem.text and elem.tag.endswith('p'):
                    paragraphs.append(clean_text(elem.text))

    except Exception as e:
        print(f"⚠️ Failed to parse {filepath}: {e}")
    
    return paragraphs

def main():
    output = []
    files = [f for f in os.listdir(CASE_XML_FOLDER) if f.endswith(".xml")]
    
    print(f"🔎 Parsing {len(files)} case XML files...")

    for filename in tqdm(files):
        filepath = os.path.join(CASE_XML_FOLDER, filename)
        paragraphs = extract_paragraphs_from_xml(filepath)
        
        for idx, para in enumerate(paragraphs):
            output.append({
                "case_id": filename.replace(".xml", ""),
                "paragraph_id": idx + 1,
                "text": para
            })

    # Save parsed paragraphs
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Parsed {len(output)} paragraphs and saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
