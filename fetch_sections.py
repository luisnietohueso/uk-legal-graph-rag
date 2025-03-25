import requests
import xml.etree.ElementTree as ET
import csv

# CSV data storage
sections_data = []

def fetch_legislation_xml(url):
    print(f"📥 Fetching: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ Successfully retrieved XML.")
        return ET.fromstring(response.content)
    else:
        print(f"❌ Failed to fetch data. Status code: {response.status_code}")
        return None

def parse_legislation(root):
    print("\n📚 Extracting Sections and Headings...\n")
    
    # Get the namespace from the XML root
    ns = {'ns': root.tag.split('}')[0].strip('{')}

    for contents_part in root.findall(".//ns:ContentsPart", ns):
        part_title = contents_part.findtext("ns:ContentsTitle", default="", namespaces=ns)

        # Look inside each chapter
        for chapter in contents_part.findall(".//ns:ContentsChapter", ns):
            chapter_title = chapter.findtext("ns:ContentsTitle", default="", namespaces=ns)

            # Look for ContentsItem entries (sections)
            for item in chapter.findall(".//ns:ContentsItem", ns):
                number = item.findtext("ns:ContentsNumber", default="", namespaces=ns)
                title = item.findtext("ns:ContentsTitle", default="", namespaces=ns)

                if number or title:
                    print(f"    🔹 Section {number}: {title}")
                    sections_data.append([part_title, chapter_title, number, title])  # Store data

        # Also catch items directly under ContentsPblock (sometimes not inside chapters)
        for pblock in contents_part.findall(".//ns:ContentsPblock", ns):
            for item in pblock.findall("ns:ContentsItem", ns):
                number = item.findtext("ns:ContentsNumber", default="", namespaces=ns)
                title = item.findtext("ns:ContentsTitle", default="", namespaces=ns)

                if number or title:
                    print(f"    🔹 Section {number}: {title}")
                    sections_data.append([part_title, "", number, title])  # Store data

def export_to_csv(filename="equality_act_sections.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Part', 'Chapter', 'Section', 'Description'])
        writer.writerows(sections_data)
    print(f"✅ CSV exported to {filename}")

if __name__ == "__main__":
    url = "https://www.legislation.gov.uk/ukpga/2010/15/contents/data.xml"
    xml_root = fetch_legislation_xml(url)

    if xml_root:
        parse_legislation(xml_root)
        export_to_csv()
