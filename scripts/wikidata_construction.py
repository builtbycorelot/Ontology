"""
Wikidata SPARQL Query for Construction Occupations
License: CC0 (Wikidata)
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
OUTPUT = Path("data/wikidata_construction.json")

CONSTRUCTION_QUERY = """
SELECT DISTINCT ?occupation ?occupationLabel ?occupationAltLabel ?field ?fieldLabel
WHERE {
  # Get occupations in construction field
  ?occupation wdt:P31 wd:Q28640.  # instance of: profession

  # Optional: field of work
  OPTIONAL { ?occupation wdt:P425 ?field. }

  # Filter for construction-related
  {
    ?occupation wdt:P425 wd:Q385378.  # construction
  } UNION {
    ?occupation wdt:P425 wd:Q11303.   # architecture
  } UNION {
    ?occupation wdt:P361 wd:Q385378.  # part of construction
  } UNION {
    ?occupation rdfs:label ?label.
    FILTER(LANG(?label) = "en")
    FILTER(CONTAINS(LCASE(?label), "construction") ||
           CONTAINS(LCASE(?label), "mason") ||
           CONTAINS(LCASE(?label), "plumber") ||
           CONTAINS(LCASE(?label), "electrician") ||
           CONTAINS(LCASE(?label), "carpenter") ||
           CONTAINS(LCASE(?label), "roofer") ||
           CONTAINS(LCASE(?label), "glazier") ||
           CONTAINS(LCASE(?label), "painter"))
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 200
"""

UK_US_TERMS_QUERY = """
SELECT ?item ?enLabel ?enGbLabel ?enUsLabel
WHERE {
  # Construction materials and systems
  {
    ?item wdt:P31/wdt:P279* wd:Q206615.  # building material
  } UNION {
    ?item wdt:P31/wdt:P279* wd:Q811430.  # building element
  }

  # Get labels in different English variants
  OPTIONAL { ?item rdfs:label ?enLabel. FILTER(LANG(?enLabel) = "en") }
  OPTIONAL { ?item rdfs:label ?enGbLabel. FILTER(LANG(?enGbLabel) = "en-gb") }
  OPTIONAL { ?item rdfs:label ?enUsLabel. FILTER(LANG(?enUsLabel) = "en-us") }

  # Only items with both UK and US labels
  FILTER(BOUND(?enGbLabel) || BOUND(?enUsLabel))
}
LIMIT 500
"""

def query_wikidata(query):
    """Execute SPARQL query against Wikidata"""
    params = {"query": query, "format": "json"}
    url = f"{WIKIDATA_ENDPOINT}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url)
    req.add_header("User-Agent", "OntologyCrosswalk/1.0 (research project)")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error querying Wikidata: {e}")
        return None

def main():
    print("Querying Wikidata for construction occupations...")

    # Query occupations
    results = query_wikidata(CONSTRUCTION_QUERY)

    if not results:
        print("Failed to query Wikidata")
        return

    occupations = []
    for binding in results.get("results", {}).get("bindings", []):
        occ = {
            "qid": binding.get("occupation", {}).get("value", "").split("/")[-1],
            "label": binding.get("occupationLabel", {}).get("value", ""),
            "aliases": binding.get("occupationAltLabel", {}).get("value", "").split(", ") if binding.get("occupationAltLabel") else [],
            "field": binding.get("fieldLabel", {}).get("value", "")
        }
        if occ["label"] and occ["qid"]:
            occupations.append(occ)

    print(f"  Found {len(occupations)} construction occupations")

    # Query UK/US terms
    print("\nQuerying Wikidata for UK/US terminology variants...")
    uk_us_results = query_wikidata(UK_US_TERMS_QUERY)

    uk_us_terms = []
    if uk_us_results:
        for binding in uk_us_results.get("results", {}).get("bindings", []):
            term = {
                "qid": binding.get("item", {}).get("value", "").split("/")[-1],
                "en": binding.get("enLabel", {}).get("value", ""),
                "en_gb": binding.get("enGbLabel", {}).get("value", ""),
                "en_us": binding.get("enUsLabel", {}).get("value", "")
            }
            # Only keep if we have different UK/US terms
            if term["en_gb"] and term["en_us"] and term["en_gb"].lower() != term["en_us"].lower():
                uk_us_terms.append(term)

        print(f"  Found {len(uk_us_terms)} UK/US term variants")

    # Build output
    output = {
        "_meta": {
            "source": "Wikidata",
            "license": "CC0",
            "query_date": "2024-12-30"
        },
        "occupations": occupations,
        "uk_us_variants": uk_us_terms
    }

    # Save
    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {OUTPUT}")

    # Show sample
    print("\nSample occupations:")
    for occ in occupations[:10]:
        aliases = f" (aliases: {', '.join(occ['aliases'][:3])})" if occ['aliases'] else ""
        print(f"  {occ['qid']}: {occ['label']}{aliases}")

    if uk_us_terms:
        print("\nUK/US term differences found:")
        for term in uk_us_terms[:10]:
            print(f"  {term['en_us']} (US) <-> {term['en_gb']} (UK)")

if __name__ == "__main__":
    main()
