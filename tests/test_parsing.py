import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.parse import parse_equality_act

import xml.etree.ElementTree as ET
from src.parse.parse_equality_act import (
    load_local_xml,
    get_namespace,
    parse_nested_structure_with_index,
)

def test_parse_equality_act_structure():
    xml_path = "data/equality_act_body.xml"
    root = load_local_xml(xml_path)
    assert isinstance(root, ET.Element)

    ns = get_namespace(root)
    assert "leg" in ns

    result = parse_nested_structure_with_index(root)
    assert "tree" in result and isinstance(result["tree"], list)
    assert "index" in result and isinstance(result["index"], dict)
    assert len(result["tree"]) > 0

    first_part = result["tree"][0]
    assert "chapters" in first_part
    assert isinstance(first_part["chapters"], list)
