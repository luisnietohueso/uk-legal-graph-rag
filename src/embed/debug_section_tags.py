import xml.etree.ElementTree as ET

def load_local_xml(file_path):
    with open(file_path, "rb") as f:
        return ET.fromstring(f.read())

def get_namespace(root):
    return {'leg': root.tag.split('}')[0].strip('{')}

def collect_section_tags(root):
    ns = get_namespace(root)
    print("🔍 Looking inside <Section> elements for tag structure...\n")

    seen_tags = set()
    for section in root.findall(".//leg:Section", ns):
        for elem in section.iter():
            tag_clean = elem.tag.split('}')[-1]  # Remove namespace
            seen_tags.add(tag_clean)

    return sorted(seen_tags)

if __name__ == "__main__":
    xml_path = "data/equality_act_body.xml"
    root = load_local_xml(xml_path)
    tags = collect_section_tags(root)

    print("✅ Unique tags found inside <Section> elements:\n")
    for tag in tags:
        print(f" - {tag}")
