import requests
import feedparser
import csv
import json
import os

# === Config ===
QUERY = "Equality Act"
BASE_URL = "https://caselaw.nationalarchives.gov.uk/atom.xml"
OUTPUT_JSON = "data/case_law_results.json"
OUTPUT_CSV = "data/case_law_results.csv"
RESULTS_LIMIT = 100  # How many cases to fetch

# === Create output folder if missing ===
os.makedirs("data", exist_ok=True)

# === Build API URL ===
params = {
    "query": QUERY,
    "per_page": RESULTS_LIMIT
}
url = f"{BASE_URL}?query={QUERY}&per_page={RESULTS_LIMIT}"

# === Fetch feed ===
print(f"🔎 Fetching case law search for query: '{QUERY}'...")
response = requests.get(url)
if response.status_code != 200:
    print("❌ Failed to fetch data:", response.status_code)
    exit(1)

# === Parse Atom feed ===
feed = feedparser.parse(response.content)

cases = []
for entry in feed.entries:
    case = {
        "title": entry.title,
        "updated": entry.updated,
        "link_pdf": "",
        "link_xml": "",
        "summary": entry.summary if hasattr(entry, "summary") else ""
    }
    # Find links
    for link in entry.links:
        if link.type == "application/pdf":
            case["link_pdf"] = link.href
        if link.type == "application/akn+xml":
            case["link_xml"] = link.href
    cases.append(case)

print(f"✅ Found {len(cases)} cases.")

# === Save results ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(cases, f, indent=2, ensure_ascii=False)

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "updated", "link_pdf", "link_xml", "summary"])
    writer.writeheader()
    writer.writerows(cases)

print(f"📁 Saved {len(cases)} cases to {OUTPUT_JSON} and {OUTPUT_CSV}")
