"""
Merge O*NET task evidence with existing validation tiers
Adds a third confirmation method to boost confidence
"""

import json
from pathlib import Path
from collections import defaultdict

VALIDATION_TIERS = Path("crosswalk/validation_tiers.json")
ONET_MATCHES = Path("crosswalk/onet_task_matches.json")
OUTPUT = Path("crosswalk/enhanced_mappings.json")

def normalize_naics(code):
    """Normalize NAICS code to 6-digit format"""
    code = str(code).replace("naics:", "")
    return code

def normalize_uniclass(code):
    """Normalize Uniclass code"""
    code = str(code).replace("uc:", "")
    # Convert Ss_70 to match format
    return code

def load_onet_by_naics():
    """Load O*NET matches indexed by NAICS code"""
    naics_to_systems = defaultdict(list)

    with open(ONET_MATCHES, 'r') as f:
        data = json.load(f)
        for m in data.get('mappings', []):
            naics = m.get('naics_code', '')
            if naics and naics != 'unknown':
                naics_to_systems[naics].append({
                    'uniclass': m['uniclass_ss'],
                    'score': m['confidence'],
                    'occupation': m['occupation'],
                    'keywords': m['keywords']
                })

    return naics_to_systems

def main():
    print("Loading existing validation tiers...")
    with open(VALIDATION_TIERS, 'r') as f:
        tiers_data = json.load(f)

    print(f"  Total existing mappings: {tiers_data['summary']['total']}")
    print(f"  Tier 1 (ground truth): {tiers_data['summary']['tier1_ground_truth']}")

    print("\nLoading O*NET task matches...")
    onet_by_naics = load_onet_by_naics()
    print(f"  NAICS codes with O*NET matches: {len(onet_by_naics)}")

    # Build enhancement map
    enhancements = {
        'promoted_to_tier1': 0,
        'onet_confirmed': 0,
        'new_onet_only': 0,
        'detailed': []
    }

    # Check each tier for O*NET confirmation
    all_tiers = ['tier1_ground_truth', 'tier2_high_single', 'tier3_conflicts', 'tier4_low_confidence']

    for tier_name in all_tiers:
        mappings = tiers_data['tiers'].get(tier_name, [])
        for mapping in mappings:
            naics_full = normalize_naics(mapping['source_id'])
            # Try both 6-digit and shorter versions
            naics_codes = [naics_full, naics_full[:5], naics_full[:4], naics_full[:3]]

            for naics in naics_codes:
                if naics in onet_by_naics:
                    # Check if any O*NET system matches the Uniclass target
                    uniclass = normalize_uniclass(mapping['target_id'])

                    for onet_match in onet_by_naics[naics]:
                        # Check for prefix match (Ss_70 matches Ss_70_xxx)
                        if uniclass.startswith(onet_match['uniclass']) or onet_match['uniclass'].startswith(uniclass.split('_')[0] + '_' + uniclass.split('_')[1] if '_' in uniclass else ''):
                            enhancements['onet_confirmed'] += 1

                            if 'onet_task' not in mapping.get('methods', []):
                                mapping['methods'].append('onet_task')
                                mapping['method_count'] = len(mapping['methods'])
                                mapping['onet_evidence'] = {
                                    'occupation': onet_match['occupation'],
                                    'keywords': onet_match['keywords'],
                                    'score': onet_match['score']
                                }

                                # Promote tier 2 to tier 1 if now has 3 methods
                                if tier_name == 'tier2_high_single' and mapping['method_count'] >= 3:
                                    enhancements['promoted_to_tier1'] += 1
                                    enhancements['detailed'].append({
                                        'naics': naics_full,
                                        'uniclass': uniclass,
                                        'promotion': 'tier2 -> tier1',
                                        'occupation': onet_match['occupation']
                                    })
                            break
                    break

    # Summary
    print(f"\n=== Enhancement Results ===")
    print(f"Mappings confirmed by O*NET: {enhancements['onet_confirmed']}")
    print(f"Promoted to Tier 1: {enhancements['promoted_to_tier1']}")

    # Update summary counts
    new_tier1 = tiers_data['summary']['tier1_ground_truth'] + enhancements['promoted_to_tier1']

    output = {
        "_meta": {
            "description": "Enhanced mappings with O*NET task evidence",
            "enhancement_date": "2024-12-30",
            "methods": ["linguistic", "embedding", "onet_task"],
            "sources": {
                "onet": "O*NET 30.1 Database (CC BY 4.0)",
                "wikidata": "Wikidata (CC0)",
                "original": "Linguistic + Embedding matching"
            }
        },
        "summary": {
            "original_total": tiers_data['summary']['total'],
            "original_tier1": tiers_data['summary']['tier1_ground_truth'],
            "enhanced_tier1": new_tier1,
            "onet_confirmations": enhancements['onet_confirmed'],
            "promotions": enhancements['promoted_to_tier1']
        },
        "enhancements": enhancements['detailed'][:20],  # Sample
        "tiers": tiers_data['tiers']
    }

    with open(OUTPUT, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nNew Tier 1 count: {new_tier1} (was {tiers_data['summary']['tier1_ground_truth']})")
    print(f"Saved to: {OUTPUT}")

    # Show sample promotions
    if enhancements['detailed']:
        print(f"\nSample promotions:")
        for p in enhancements['detailed'][:5]:
            print(f"  {p['naics']} -> {p['uniclass']} ({p['occupation']})")

if __name__ == "__main__":
    main()
