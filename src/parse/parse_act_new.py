import json
import xml.etree.ElementTree as ET
import re

# Load the Equality Act XML (already uploaded)
xml_path = "data/equality_act_body.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

# Get namespace
namespace_uri = root.tag.split("}")[0].strip("{")
ns = {"leg": namespace_uri}

def extract_all_text(element):
    """Recursively extract all text content from an XML element."""
    text_parts = []
    if element.text:
        text_parts.append(element.text)
    for child in element:
        text_parts.append(extract_all_text(child))
        if child.tail:
            text_parts.append(child.tail)
    return ''.join(text_parts)

def clean_text(text):
    """Normalize whitespace."""
    return re.sub(r'\s+', ' ', text).strip()

# Extract paragraphs with full references from <P1group>
paragraphs = []
for group in root.findall(".//leg:P1group", ns):
    group_id = group.get("id", "unknown")
    
    for p1 in group.findall("leg:P1", ns):
        text = clean_text(extract_all_text(p1))
        if text:
            paragraphs.append({
                "Group ID": group_id,
                "Level": "P1",
                "Label": p1.get("id", ""),
                "Text": text
            })

    for p2 in group.findall("leg:P2", ns):
        text = clean_text(extract_all_text(p2))
        if text:
            paragraphs.append({
                "Group ID": group_id,
                "Level": "P2",
                "Label": p2.get("id", ""),
                "Text": text
            })
# Add a Group ID (unique ID for each paragraph)
for i, item in enumerate(paragraphs):
    item["Group ID"] = f"P{i+1:4d}"

# Save the structured output with refs
output_path = "data/equality_act_paragraphs_with_refs.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(paragraphs, f, indent=2, ensure_ascii=False)

output_path
