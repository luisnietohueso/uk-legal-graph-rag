import xml.etree.ElementTree as ET
import json
import re


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

def parse_nested_structure_with_index(root):
    ns = get_namespace(root)
    parts_data = []
    index = {}

    print("🔎 Looking for <Part>, <Chapter>, and <Section> tags...")

    for part_index, part in enumerate(root.findall(".//leg:Part", ns), start=1):
        part_number = f"Part {part_index}"
        part_heading = part.findtext("leg:Title", default="", namespaces=ns)
        part_text = clean_text(extract_all_text(part))
        print(f"📘 {part_number}: {part_heading}")

        part_entry = {
            "section": part_number,
            "heading": part_heading,
            "text": part_text,
            "chapters": []
        }
        index[part_number] = {
            "heading": part_heading,
            "text": part_text
        }

        for chapter_index, chapter in enumerate(part.findall("leg:Chapter", ns), start=1):
            chapter_number = f"{part_number}.Chapter {chapter_index}"
            chapter_heading = chapter.findtext("leg:Title", default="", namespaces=ns)
            chapter_text = clean_text(extract_all_text(chapter))
            print(f"    📗 {chapter_number}: {chapter_heading}")

            chapter_entry = {
                "section": chapter_number,
                "heading": chapter_heading,
                "text": chapter_text,
                "sections": []
            }
            index[chapter_number] = {
                "heading": chapter_heading,
                "text": chapter_text
            }

            for section in chapter.findall(".//leg:Section", ns):
                sec_num = section.findtext("leg:Number", default="", namespaces=ns)
                sec_heading = section.findtext("leg:Heading", default="", namespaces=ns)

                paras = section.findall(".//leg:P1", ns) + section.findall(".//leg:P", ns) + section.findall(".//leg:Para", ns)
                text = "\n".join([p.text.strip() if p.text else "" for p in paras])
                section_text = clean_text(text)

                full_sec_id = f"{chapter_number}.Section {sec_num}" if sec_num else f"{chapter_number}.Section"
                print(f"        📄 {full_sec_id}: {sec_heading}")

                section_entry = {
                    "section": full_sec_id,
                    "heading": sec_heading,
                    "text": section_text
                }
                index[full_sec_id] = {
                    "heading": sec_heading,
                    "text": section_text
                }

                chapter_entry["sections"].append(section_entry)

            part_entry["chapters"].append(chapter_entry)

        parts_data.append(part_entry)

    return { "tree": parts_data, "index": index }

if __name__ == "__main__":
    xml_path = "data/equality_act_body.xml"
    output_path = "data/equality_act_structured3.json"

    root = load_local_xml(xml_path)
    result = parse_nested_structure_with_index(root)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved full structured output with index to {output_path}")
