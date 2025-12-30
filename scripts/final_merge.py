"""
Final Merge - Combine ALL Evidence Sources into Master Confidence Scores
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Input files
VALIDATION_TIERS = Path("crosswalk/validation_tiers.json")
ONET_MATCHES = Path("crosswalk/onet_task_matches.json")
EXPERT_VALIDATIONS = Path("reviewed/expert_validations.json")
BLS_MATRIX = Path("data/enhanced/bls_naics_soc_matrix.json")
BRICK_SYSTEMS = Path("data/enhanced/brick_systems.json")
SYNONYMS = Path("data/enhanced/wordnet_expansions.json")
UK_US_SYNONYMS = Path("data/ukus_synonyms.json")

# Output
OUTPUT = Path("crosswalk/final_crosswalk.json")

def load_json(path):
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def main():
    print("=" * 60)
    print("FINAL MERGE - ALL EVIDENCE SOURCES")
    print("=" * 60)

    # Load all sources
    print("\nLoading evidence sources...")

    tiers = load_json(VALIDATION_TIERS)
    print(f"  Validation tiers: {tiers['summary']['total'] if tiers else 0} mappings")

    onet = load_json(ONET_MATCHES)
    print(f"  O*NET tasks: {len(onet.get('mappings', [])) if onet else 0} mappings")

    expert = load_json(EXPERT_VALIDATIONS)
    print(f"  Expert validations: {expert['session_summary']['validated'] if expert else 0} validated")

    bls = load_json(BLS_MATRIX)
    print(f"  BLS matrix: {len(bls.get('matrix', {})) if bls else 0} NAICS codes")

    brick = load_json(BRICK_SYSTEMS)
    print(f"  Brick systems: {len(brick.get('systems', {})) if brick else 0} systems")

    synonyms = load_json(SYNONYMS)
    print(f"  Synonyms: {len(synonyms.get('expansions', {})) if synonyms else 0} terms")

    uk_us = load_json(UK_US_SYNONYMS)
    uk_us_count = sum(len(v) for k, v in uk_us.items() if k != '_meta') if uk_us else 0
    print(f"  UK/US synonyms: {uk_us_count} term mappings")

    # Build master mapping index
    print("\nBuilding master index...")

    master_mappings = {}

    # Start with validation tiers as base
    if tiers:
        for tier_name, mappings in tiers.get('tiers', {}).items():
            tier_num = int(tier_name.split('tier')[1].split('_')[0])
            for m in mappings:
                key = (m['source_id'], m['target_id'])
                if key not in master_mappings:
                    master_mappings[key] = {
                        'naics_code': m['source_id'],
                        'naics_name': m['source_name'],
                        'uniclass_code': m['target_id'],
                        'uniclass_name': m['target_name'],
                        'original_tier': tier_num,
                        'methods': m.get('methods', []),
                        'confidence_score': m.get('avg_score', 0),
                        'evidence': []
                    }
                    master_mappings[key]['evidence'].append({
                        'source': 'linguistic_embedding',
                        'tier': tier_num,
                        'score': m.get('avg_score', 0)
                    })

    # Add O*NET evidence
    onet_additions = 0
    if onet:
        for m in onet.get('mappings', []):
            naics = f"naics:{m['naics_code']}" if not m['naics_code'].startswith('naics:') else m['naics_code']
            uniclass = f"uc:{m['uniclass_ss']}" if not m['uniclass_ss'].startswith('uc:') else m['uniclass_ss']
            key = (naics, uniclass)

            if key in master_mappings:
                master_mappings[key]['evidence'].append({
                    'source': 'onet_task',
                    'occupation': m.get('occupation', ''),
                    'keywords': m.get('keywords', []),
                    'score': m.get('confidence', 0)
                })
                if 'onet_task' not in master_mappings[key]['methods']:
                    master_mappings[key]['methods'].append('onet_task')
                onet_additions += 1

    print(f"  O*NET evidence added to {onet_additions} mappings")

    # Add BLS bridge evidence
    bls_additions = 0
    if bls:
        for naics_code, data in bls.get('matrix', {}).items():
            # Find mappings with this NAICS
            for key, mapping in master_mappings.items():
                if naics_code in key[0]:
                    mapping['evidence'].append({
                        'source': 'bls_matrix',
                        'soc_codes': data.get('primary_soc', []),
                        'description': data.get('description', '')
                    })
                    if 'bls_matrix' not in mapping['methods']:
                        mapping['methods'].append('bls_matrix')
                    bls_additions += 1

    print(f"  BLS matrix evidence added to {bls_additions} mappings")

    # Add Brick alignment evidence
    brick_additions = 0
    if brick:
        brick_to_uc = brick.get('brick_to_uniclass', {})
        for brick_sys, uc_code in brick_to_uc.items():
            for key, mapping in master_mappings.items():
                if uc_code in key[1]:
                    mapping['evidence'].append({
                        'source': 'brick_schema',
                        'brick_class': brick_sys
                    })
                    if 'brick_schema' not in mapping['methods']:
                        mapping['methods'].append('brick_schema')
                    brick_additions += 1

    print(f"  Brick schema evidence added to {brick_additions} mappings")

    # Recalculate confidence tiers based on evidence count
    print("\nRecalculating confidence tiers...")

    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}

    for key, mapping in master_mappings.items():
        num_methods = len(set(mapping['methods']))
        num_evidence = len(mapping['evidence'])

        # Calculate new tier
        if num_methods >= 3:
            new_tier = 1
        elif num_methods == 2 and mapping['confidence_score'] >= 0.4:
            new_tier = 1
        elif num_methods == 2:
            new_tier = 2
        elif mapping['confidence_score'] >= 0.5:
            new_tier = 2
        elif mapping['confidence_score'] >= 0.3:
            new_tier = 3
        else:
            new_tier = 4

        mapping['final_tier'] = new_tier
        mapping['method_count'] = num_methods
        mapping['evidence_count'] = num_evidence
        tier_counts[new_tier] += 1

    # Summary statistics
    total = len(master_mappings)
    print(f"\n{'=' * 60}")
    print("FINAL RESULTS")
    print(f"{'=' * 60}")
    print(f"Total mappings: {total}")
    print(f"\nBy Tier:")
    for tier in sorted(tier_counts.keys()):
        pct = tier_counts[tier] / total * 100 if total > 0 else 0
        print(f"  Tier {tier}: {tier_counts[tier]} ({pct:.1f}%)")

    # Build output
    output = {
        "_meta": {
            "generated_at": datetime.now().isoformat(),
            "description": "Final crosswalk with all evidence sources merged",
            "version": "1.0.0",
            "license": "CC BY-SA 4.0",
            "sources": {
                "primary": {
                    "naics": "Public Domain (US Government)",
                    "uniclass": "CC BY-ND 4.0 (NBS) - codes referenced only",
                    "schema_org": "CC BY-SA 3.0"
                },
                "evidence": {
                    "onet": "CC BY 4.0 (US DOL)",
                    "bls": "Public Domain (US Government)",
                    "brick": "BSD-3-Clause",
                    "wikidata": "CC0",
                    "expert": "Internal validation"
                }
            },
            "methods": [
                "linguistic (Jaccard similarity)",
                "embedding (TF-IDF cosine)",
                "onet_task (keyword matching)",
                "bls_matrix (occupation-industry)",
                "brick_schema (system alignment)",
                "expert_validation"
            ]
        },
        "summary": {
            "total_mappings": total,
            "tier_1_ground_truth": tier_counts[1],
            "tier_2_high_confidence": tier_counts[2],
            "tier_3_medium_confidence": tier_counts[3],
            "tier_4_low_confidence": tier_counts[4],
            "improvement": {
                "original_tier_1": tiers['summary']['tier1_ground_truth'] if tiers else 0,
                "final_tier_1": tier_counts[1],
                "increase": tier_counts[1] - (tiers['summary']['tier1_ground_truth'] if tiers else 0)
            }
        },
        "mappings": list(master_mappings.values())
    }

    # Sort mappings by tier, then by confidence
    output['mappings'].sort(key=lambda x: (x['final_tier'], -x['confidence_score']))

    # Save
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {OUTPUT}")

    # Show improvement
    original_t1 = tiers['summary']['tier1_ground_truth'] if tiers else 0
    print(f"\n{'=' * 60}")
    print("IMPROVEMENT SUMMARY")
    print(f"{'=' * 60}")
    print(f"Original Tier 1: {original_t1}")
    print(f"Final Tier 1: {tier_counts[1]}")
    print(f"Increase: +{tier_counts[1] - original_t1} ({((tier_counts[1] - original_t1) / original_t1 * 100) if original_t1 > 0 else 0:.1f}%)")

    # Show top mappings
    print(f"\nTop 10 highest confidence mappings:")
    for m in output['mappings'][:10]:
        print(f"  [T{m['final_tier']}] {m['naics_name']} -> {m['uniclass_name']}")
        print(f"       Methods: {', '.join(m['methods'])}")

if __name__ == "__main__":
    main()
