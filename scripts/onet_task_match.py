"""
O*NET Task-Based Matching for NAICS-Uniclass Crosswalk
License: Uses O*NET Database (CC BY 4.0)
Attribution: O*NET 30.1 Database by U.S. Department of Labor (USDOL/ETA)
"""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict

# Paths
ONET_DIR = Path("data/onet/db_30_1_text")
UNICLASS_SS = Path("data/uniclass_ss.csv")
OUTPUT = Path("crosswalk/onet_task_matches.json")

# Keywords that map to Uniclass system categories
SYSTEM_KEYWORDS = {
    "Ss_70": ["electrical", "wiring", "circuit", "power", "lighting", "voltage"],
    "Ss_55": ["plumbing", "pipe", "water", "drain", "sewer", "sanitation"],
    "Ss_60": ["hvac", "heating", "cooling", "ventilation", "air conditioning", "ductwork"],
    "Ss_25_20": ["cladding", "siding", "facade", "exterior wall", "envelope"],
    "Ss_25_30": ["roofing", "roof", "shingle", "membrane"],
    "Ss_25_10": ["framing", "structural", "framework", "stud", "joist"],
    "Ss_25_45": ["flooring", "floor", "tile", "carpet", "terrazzo"],
    "Ss_25_50": ["ceiling", "drywall", "plasterboard", "gypsum"],
    "Ss_25_35": ["insulation", "thermal", "sound-deadening"],
    "Ss_30": ["masonry", "brick", "block", "stone", "concrete"],
    "Ss_35": ["glazing", "glass", "window", "skylight"],
    "Ss_40": ["painting", "coating", "finish", "wallpaper"],
    "Ss_32": ["foundation", "pile", "footing", "excavation"],
}

def load_onet_occupations():
    """Load O*NET construction occupations (47-xxxx)"""
    occupations = {}
    with open(ONET_DIR / "Occupation Data.txt", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            code = row["O*NET-SOC Code"]
            if code.startswith("47-"):
                occupations[code] = {
                    "title": row["Title"],
                    "description": row["Description"],
                    "tasks": []
                }
    return occupations

def load_onet_tasks(occupations):
    """Load task statements for construction occupations"""
    with open(ONET_DIR / "Task Statements.txt", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            code = row["O*NET-SOC Code"]
            if code in occupations:
                occupations[code]["tasks"].append(row["Task"])
    return occupations

def match_tasks_to_systems(occupations):
    """Match task text to Uniclass system categories"""
    matches = defaultdict(lambda: defaultdict(list))

    for onet_code, occ_data in occupations.items():
        title = occ_data["title"]
        all_text = " ".join([occ_data["description"]] + occ_data["tasks"]).lower()

        for ss_code, keywords in SYSTEM_KEYWORDS.items():
            matching_keywords = []
            for kw in keywords:
                if kw in all_text:
                    matching_keywords.append(kw)

            if matching_keywords:
                matches[onet_code][ss_code] = {
                    "keywords_matched": matching_keywords,
                    "score": len(matching_keywords) / len(keywords),
                    "occupation_title": title
                }

    return matches

def create_soc_to_naics_map():
    """Map SOC codes to NAICS codes (approximate based on construction sector)"""
    # This is a simplified mapping - O*NET provides more detailed crosswalks
    return {
        "47-2111.00": "238210",  # Electricians -> Electrical Contractors
        "47-2152.00": "238220",  # Plumbers -> Plumbing Contractors
        "47-2031.00": "238130",  # Carpenters -> Framing Contractors
        "47-2081.00": "238310",  # Drywall Installers -> Drywall Contractors
        "47-2044.00": "238340",  # Tile Setters -> Tile Contractors
        "47-2181.00": "238160",  # Roofers -> Roofing Contractors
        "47-2021.00": "238140",  # Brickmasons -> Masonry Contractors
        "47-2121.00": "238150",  # Glaziers -> Glass Contractors
        "47-2141.00": "238320",  # Painters -> Painting Contractors
        "47-2131.00": "238310",  # Insulation Workers -> Drywall/Insulation
        "47-2051.00": "238110",  # Concrete Finishers -> Concrete Contractors
        "47-2061.00": "238910",  # Construction Laborers -> Site Preparation
    }

def main():
    print("Loading O*NET construction occupations...")
    occupations = load_onet_occupations()
    print(f"  Found {len(occupations)} construction occupations")

    print("Loading task statements...")
    occupations = load_onet_tasks(occupations)
    total_tasks = sum(len(o["tasks"]) for o in occupations.values())
    print(f"  Loaded {total_tasks} task statements")

    print("Matching tasks to Uniclass systems...")
    matches = match_tasks_to_systems(occupations)

    # Build output
    soc_to_naics = create_soc_to_naics_map()
    results = {
        "_meta": {
            "source": "O*NET 30.1 Database",
            "license": "CC BY 4.0",
            "attribution": "U.S. Department of Labor, Employment and Training Administration",
            "method": "Task keyword matching to Uniclass system categories"
        },
        "mappings": []
    }

    for onet_code, systems in matches.items():
        naics = soc_to_naics.get(onet_code, "unknown")
        for ss_code, match_data in systems.items():
            if match_data["score"] >= 0.3:  # At least 30% keyword match
                results["mappings"].append({
                    "onet_code": onet_code,
                    "occupation": match_data["occupation_title"],
                    "naics_code": naics,
                    "uniclass_ss": ss_code,
                    "confidence": round(match_data["score"], 3),
                    "keywords": match_data["keywords_matched"],
                    "method": "onet_task_match"
                })

    # Sort by confidence
    results["mappings"].sort(key=lambda x: x["confidence"], reverse=True)

    # Save
    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults:")
    print(f"  Total task-based mappings: {len(results['mappings'])}")
    print(f"  High confidence (>0.5): {sum(1 for m in results['mappings'] if m['confidence'] > 0.5)}")
    print(f"  Saved to: {OUTPUT}")

    # Show top mappings
    print("\nTop 10 mappings by confidence:")
    for m in results["mappings"][:10]:
        print(f"  {m['occupation']} -> {m['uniclass_ss']} ({m['confidence']:.2f})")
        print(f"    Keywords: {', '.join(m['keywords'])}")

if __name__ == "__main__":
    main()
