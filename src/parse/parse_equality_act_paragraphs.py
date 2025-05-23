import xml.etree.ElementTree as ET
import json
import csv
import re
import os

def load_local_xml(file_path):
    with open(file_path, "rb") as f:
        return ET.fromstring(f.read())

def get_namespace(root):
    namespace_uri = root.tag.split('}')[0].strip('{')
    print(f"Detected XML namespace: {namespace_uri}")
    return {'leg': namespace_uri}

def extract_all_text(element):
    text_parts = []
    if element.text:
        text_parts.append(element.text)
    for child in element:
        text_parts.append(extract_all_text(child))
        if child.tail:
            text_parts.append(child.tail)
    return ''.join(text_parts)

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def parse_to_paragraph_chunks(root):
    ns = get_namespace(root)
    chunks = []

    print("🔎 Parsing XML using <P1group>, <P1>, <P2>...")

    for group in root.findall(".//leg:P1group", ns):
        group_id = group.get("id", "unknown")

        for p1 in group.findall("leg:P1", ns):
            label = p1.findtext("leg:Label", default="", namespaces=ns)
            text = clean_text(extract_all_text(p1))
            if text:
                chunks.append({
                    "Group ID": group_id,
                    "Level": "P1",
                    "Label": label,
                    "Text": text
                })

        for p2 in group.findall("leg:P2", ns):
            label = p2.findtext("leg:Label", default="", namespaces=ns)
            text = clean_text(extract_all_text(p2))
            if text:
                chunks.append({
                    "Group ID": group_id,
                    "Level": "P2",
                    "Label": label,
                    "Text": text
                })

    print(f"✅ Extracted {len(chunks)} paragraphs")
    return chunks

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_to_csv(data, filename):
    if not data:
        print("⚠️ No data to save in CSV.")
        return
    fieldnames = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def save_to_html(data, filename):
    html = "<html><body>"
    for item in data:
        html += f"<h3>Group ID: {item['Group ID']}</h3>"
        html += f"<p><b>{item['Level']}</b> ({item['Label']}) {item['Text']}</p>"
    html += "</body></html>"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    xml_path = "data/equality_act_body.xml"
    json_out = "data/equality_act_paragraphs_fixed.json"
    csv_out = "data/equality_act_paragraphs_fixed.csv"
    html_out = "data/equality_act_paragraphs_fixed.html"

    root = load_local_xml(xml_path)
    paragraph_chunks = parse_to_paragraph_chunks(root)

    save_to_json(paragraph_chunks, json_out)
    save_to_csv(paragraph_chunks, csv_out)
    save_to_html(paragraph_chunks, html_out)

    print(f"📁 Saved JSON to {json_out}")
    print(f"📁 Saved CSV to {csv_out}")
    print(f"📁 Saved HTML to {html_out}")
