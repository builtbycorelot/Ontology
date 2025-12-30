"""
Map Seed Scopes to Ontology
Cross-reference user-provided scopes with NAICS, Uniclass, O*NET
"""

import json
from pathlib import Path
from collections import defaultdict

SEED_SCOPES = Path("data/seed_scopes.json")
OUTPUT = Path("crosswalk/scope_mappings.json")

# Trade name → NAICS mapping (from our ontology + industry knowledge)
TRADE_TO_NAICS = {
    "ALL": {"naics": "23", "name": "Construction (General Conditions)", "uniclass_ss": ["Ss_20", "Ss_25"]},
    "Due Diligence": {"naics": "541310", "name": "Architectural Services", "uniclass_ss": ["Ac_05", "Ac_10"]},
    "Site Plan": {"naics": "541370", "name": "Surveying and Mapping Services", "uniclass_ss": ["Ac_05_10", "Ac_10_70"]},
    "Surveying": {"naics": "541370", "name": "Surveying and Mapping Services", "uniclass_ss": ["Ac_15_10"]},
    "Lot Development": {"naics": "238910", "name": "Site Preparation Contractors", "uniclass_ss": ["Ss_15", "Ss_20_10"]},
    "Landscaping": {"naics": "561730", "name": "Landscaping Services", "uniclass_ss": ["Ss_15_10", "EF_25"]},
    "Utilities to site": {"naics": "237110", "name": "Water and Sewer Line Construction", "uniclass_ss": ["Ss_55", "Ss_65"]},
    "Concrete": {"naics": "238110", "name": "Poured Concrete Foundation and Structure Contractors", "uniclass_ss": ["Ss_30", "Ss_32"]},
    "Plumbing": {"naics": "238220", "name": "Plumbing, Heating, and Air-Conditioning Contractors", "uniclass_ss": ["Ss_55", "Ss_60"]},
    "Framer": {"naics": "238130", "name": "Framing Contractors", "uniclass_ss": ["Ss_25_10", "Ss_25_13"]},
    "Roofing": {"naics": "238160", "name": "Roofing Contractors", "uniclass_ss": ["Ss_25_30"]},
    "3rd Party Inspection": {"naics": "541350", "name": "Building Inspection Services", "uniclass_ss": ["Ac_35"]},
}

# Phase → Uniclass work stage mapping
PHASE_TO_UNICLASS = {
    "Base Map": "Ac_05_10",  # Surveying
    "Due Diligence": "Ac_05",  # Briefing
    "Lot Grading Plan": "Ac_10_70",  # Planning
    "Good Stake": "Ac_15_10_70",  # Setting out
    "Rough Stake": "Ac_15_10_70",
    "Wall Check": "Ac_35_10",  # Inspection
    "Demolition": "Ac_40_10",  # Demolition activities
    "Final Yard": "Ss_15_10",  # Soft landscaping
    "Landscaping": "Ss_15_10",
    "Private Ln": "Ss_15_30",  # Hard landscaping / access roads
    "Yard Maintenance": "Ss_15_10",
    "Clearing": "Ac_40_10_15",  # Site clearance
    "Construction Entrance": "Ss_15_30_10",  # Access
    "Erosion Control": "Ss_15_95",  # Land drainage
    "Basement Dig": "Ss_32_10",  # Excavation
    "Septic & Sewer": "Ss_65",  # Drainage systems
    "Well & Water Hookup": "Ss_55_10",  # Water supply
    "Rough Grade": "Ss_15_30",  # Earthworks
    "3rd Party Inspection": "Ac_35",  # Inspection
    "Foundation & Walls": "Ss_30",  # Structure - concrete
    "Waterproofing / Draintile": "Ss_25_60",  # Waterproofing
    "Interior Flat Work": "Ss_25_45",  # Flooring
    "Leadwalk & Pads": "Ss_32_50",  # External paving
    "Final": "Ac_50",  # Commissioning
    "Gas": "Ss_60_70",  # Gas systems
    "Groundworks": "Ss_55_10",  # Below ground drainage
    "Plumbing Fixtures": "Pr_40_50",  # Sanitary fittings
    "R/I": "Ss_55",  # Plumbing rough-in
}

# Task keywords → Uniclass products
TASK_KEYWORDS_TO_PRODUCTS = {
    "shingles": "Pr_25_71_72",  # Roof shingles
    "ridge vent": "Pr_25_71_97",  # Roof ventilators
    "house wrap": "Pr_25_93_50",  # Building membranes
    "flashing": "Pr_25_71_30",  # Flashings
    "lumber": "Pr_20_93_98",  # Timber
    "nails": "Pr_20_31_30",  # Fasteners
    "PVC": "Pr_65_52_26",  # PVC pipes
    "PEX": "Pr_65_52_24",  # PEX pipes
    "CPVC": "Pr_65_52_22",  # CPVC pipes
    "gravel": "Pr_15_56_50",  # Aggregates
    "fabric": "Pr_15_57_35",  # Geotextiles
    "concrete": "Pr_15_13_30",  # Concrete
    "sump": "Pr_65_54_85",  # Sumps
    "waterproofing": "Pr_25_93_96",  # Waterproofing
    "draintile": "Pr_65_52_28",  # Drainage pipes
    "septic": "Pr_70_60_78",  # Septic tanks
    "seed": "Pr_15_85_78",  # Seeds
    "straw": "Pr_15_85",  # Mulch/ground cover
    "erosion control": "Pr_15_57_35",  # Erosion control products
    "silt fence": "Pr_15_57_80",  # Silt fences
    "toilets": "Pr_40_50_96",  # WCs
    "dishwasher": "Pr_40_20_24",  # Dishwashers
    "refrigerator": "Pr_40_20_70",  # Refrigerators
    "doors": "Pr_25_30",  # Doors
    "windows": "Pr_25_80",  # Windows
    "tub": "Pr_40_50_10",  # Baths
    "radon": "Pr_70_75_70",  # Radon mitigation
}

def extract_products_from_task(task_text):
    """Find product references in task text"""
    products = []
    task_lower = task_text.lower()
    for keyword, pr_code in TASK_KEYWORDS_TO_PRODUCTS.items():
        if keyword in task_lower:
            products.append({"keyword": keyword, "uniclass_pr": pr_code})
    return products

def map_scopes():
    """Map all seed scopes to ontology"""

    with open(SEED_SCOPES, 'r') as f:
        data = json.load(f)

    scopes = data['scopes']

    # Group by trade
    by_trade = defaultdict(list)
    for scope in scopes:
        by_trade[scope['trade']].append(scope)

    # Build mappings
    results = {
        "_meta": {
            "description": "Seed scopes mapped to NAICS/Uniclass ontology",
            "source": "User-provided scope data",
            "confidence": "medium (seed data)",
            "date": "2024-12-30"
        },
        "summary": {
            "total_scopes": len(scopes),
            "trades_identified": len(by_trade),
            "naics_mapped": 0,
            "uniclass_ss_mapped": 0,
            "uniclass_pr_mapped": 0,
            "gaps_identified": []
        },
        "trade_mappings": [],
        "product_extractions": []
    }

    for trade, trade_scopes in by_trade.items():
        if trade == "DELETE":
            continue

        mapping = {
            "trade_name": trade,
            "naics": TRADE_TO_NAICS.get(trade, {}).get("naics", "UNMAPPED"),
            "naics_name": TRADE_TO_NAICS.get(trade, {}).get("name", ""),
            "uniclass_ss": TRADE_TO_NAICS.get(trade, {}).get("uniclass_ss", []),
            "phases": [],
            "task_count": len(trade_scopes),
            "confidence": "high" if trade in TRADE_TO_NAICS else "low"
        }

        if mapping["naics"] != "UNMAPPED":
            results["summary"]["naics_mapped"] += 1
        else:
            results["summary"]["gaps_identified"].append(f"Trade '{trade}' has no NAICS mapping")

        if mapping["uniclass_ss"]:
            results["summary"]["uniclass_ss_mapped"] += 1

        # Group by phase
        phases = defaultdict(list)
        for scope in trade_scopes:
            phase = scope.get('phase') or 'General'
            phases[phase].append(scope['task'])

        for phase_name, tasks in phases.items():
            phase_data = {
                "name": phase_name,
                "uniclass_activity": PHASE_TO_UNICLASS.get(phase_name, ""),
                "tasks": tasks,
                "products_referenced": []
            }

            # Extract products from tasks
            for task in tasks:
                products = extract_products_from_task(task)
                if products:
                    phase_data["products_referenced"].extend(products)
                    results["summary"]["uniclass_pr_mapped"] += len(products)
                    for p in products:
                        results["product_extractions"].append({
                            "trade": trade,
                            "phase": phase_name,
                            "task": task,
                            "product": p
                        })

            mapping["phases"].append(phase_data)

        results["trade_mappings"].append(mapping)

    # Save
    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)

    return results

def print_summary(results):
    """Print mapping summary"""
    print("=" * 60)
    print("SEED SCOPE MAPPING RESULTS")
    print("=" * 60)

    s = results["summary"]
    print(f"\nTotal scopes: {s['total_scopes']}")
    print(f"Trades identified: {s['trades_identified']}")
    print(f"NAICS codes mapped: {s['naics_mapped']}")
    print(f"Uniclass Ss mapped: {s['uniclass_ss_mapped']}")
    print(f"Products extracted: {s['uniclass_pr_mapped']}")

    print("\n" + "-" * 60)
    print("TRADE -> NAICS -> UNICLASS MAPPINGS")
    print("-" * 60)

    for tm in results["trade_mappings"]:
        conf = "[HIGH]" if tm["confidence"] == "high" else "[LOW]"
        print(f"\n{conf} {tm['trade_name']}")
        print(f"    NAICS: {tm['naics']} - {tm['naics_name']}")
        print(f"    Uniclass Ss: {', '.join(tm['uniclass_ss']) if tm['uniclass_ss'] else 'UNMAPPED'}")
        print(f"    Phases: {len(tm['phases'])}, Tasks: {tm['task_count']}")

    if s['gaps_identified']:
        print("\n" + "-" * 60)
        print("GAPS IDENTIFIED")
        print("-" * 60)
        for gap in s['gaps_identified']:
            print(f"  - {gap}")

    print("\n" + "-" * 60)
    print("SAMPLE PRODUCT EXTRACTIONS")
    print("-" * 60)
    for pe in results["product_extractions"][:10]:
        print(f"  {pe['trade']}/{pe['phase']}: '{pe['product']['keyword']}' -> {pe['product']['uniclass_pr']}")

    print(f"\nSaved to: {OUTPUT}")

if __name__ == "__main__":
    results = map_scopes()
    print_summary(results)
