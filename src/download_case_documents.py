# src/download_case_documents.py

import os
import json
import requests
from tqdm import tqdm

# === Config ===
CASE_LIST_PATH = "data/case_law_results.json"  # where your fetched cases are stored
PDF_DIR = "data/case_pdfs"
XML_DIR = "data/case_xmls"

# === Prepare folders ===
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(XML_DIR, exist_ok=True)

# === Load case list ===
with open(CASE_LIST_PATH, "r", encoding="utf-8") as f:
    cases = json.load(f)

# === Download files ===
for case in tqdm(cases, desc="Downloading cases"):
    title = case["title"].replace("/", "_").replace(" ", "_").replace(":", "").strip()

    # Download PDF
    pdf_url = case.get("link_pdf")
    if pdf_url:
        pdf_path = os.path.join(PDF_DIR, f"{title}.pdf")
        if not os.path.exists(pdf_path):
            r = requests.get(pdf_url)
            if r.status_code == 200:
                with open(pdf_path, "wb") as f:
                    f.write(r.content)

    # Download XML
    xml_url = case.get("link_xml")
    if xml_url:
        # The link_xml field is relative — need to add the domain!
        full_xml_url = "https://caselaw.nationalarchives.gov.uk" + xml_url
        xml_path = os.path.join(XML_DIR, f"{title}.xml")
        if not os.path.exists(xml_path):
            r = requests.get(full_xml_url)
            if r.status_code == 200:
                with open(xml_path, "wb") as f:
                    f.write(r.content)

print("\n✅ All PDFs and XMLs downloaded successfully!")
