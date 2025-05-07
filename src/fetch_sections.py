import xml.etree.ElementTree as ET

def load_local_xml(file_path):
    with open(file_path, "rb") as f:
        return ET.fromstring(f.read())

def get_namespace(root):
    return {'leg': root.tag.split('}')[0].strip('{')}

def parse_sections(root):
    ns = get_namespace(root)
    sections = []

    for section in root.findall(".//leg:Section", ns):
        number = section.findtext("leg:Number", default="", namespaces=ns)
        heading = section.findtext("leg:Heading", default="", namespaces=ns)
        paras = section.findall(".//leg:P1", ns)
        text = "\n".join([p.text or "" for p in paras])

        if number or heading:
            sections.append({
                "section": number,
                "heading": heading,
                "text": text
            })

    return sections
