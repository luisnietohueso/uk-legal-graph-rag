import xml.etree.ElementTree as ET
from collections import defaultdict

def load_local_xml(file_path):
    with open(file_path, "rb") as f:
        return ET.fromstring(f.read())

def get_namespace(root):
    return root.tag.split('}')[0].strip('{')

def summarize_structure(element, level=0, summary=None):
    if summary is None:
        summary = defaultdict(set)
    tag = element.tag.split('}')[-1]
    summary[level].add(tag)
    for child in element:
        summarize_structure(child, level + 1, summary)
    return summary

if __name__ == "__main__":
    xml_path = "data/equality_act_body.xml"
    root = load_local_xml(xml_path)
    namespace_uri = get_namespace(root)
    print(f"📂 Namespace: {namespace_uri}\n")
    print("📊 XML Tag Summary (by depth level):\n")

    summary = summarize_structure(root)

    for level in sorted(summary.keys()):
        tags = sorted(summary[level])
        print(f"Level {level}: {len(tags)} unique tag(s)")
        print("  - " + ", ".join(tags))
