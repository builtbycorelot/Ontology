#!/usr/bin/env python3
"""Deterministic linguistic matching between standards."""

import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
EXTRACTED = BASE / "extracted"
OUTPUT = BASE / "candidates"

# Domain-specific synonyms for construction
SYNONYMS = {
    'frame': ['framing', 'structure', 'structural'],
    'timber': ['wood', 'lumber', 'wooden'],
    'concrete': ['cement', 'masonry'],
    'electric': ['electrical', 'wiring', 'power'],
    'plumb': ['plumbing', 'pipe', 'piping', 'water'],
    'hvac': ['heating', 'cooling', 'ventilation', 'air'],
    'roof': ['roofing'],
    'floor': ['flooring'],
    'wall': ['partition', 'barrier'],
    'paint': ['painting', 'coating', 'finish'],
    'tile': ['tiling', 'ceramic'],
    'glass': ['glazing', 'glazed', 'window'],
    'steel': ['metal', 'iron'],
    'insulation': ['insulating', 'thermal'],
    'drywall': ['gypsum', 'plasterboard', 'sheetrock'],
    'excavate': ['excavation', 'earthwork', 'grading'],
    'foundation': ['footing', 'substructure'],
    'bridge': ['span', 'overpass'],
    'road': ['highway', 'street', 'paving', 'pavement'],
    'sewer': ['drainage', 'wastewater', 'sanitary'],
    'residential': ['housing', 'dwelling', 'home'],
    'commercial': ['office', 'retail', 'business'],
    'industrial': ['factory', 'manufacturing', 'warehouse'],
}

def expand_synonyms(tokens: set) -> set:
    """Expand token set with synonyms."""
    expanded = set(tokens)
    for token in tokens:
        for root, syns in SYNONYMS.items():
            if token == root or token in syns:
                expanded.add(root)
                expanded.update(syns)
    return expanded

def jaccard(set1: set, set2: set) -> float:
    """Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def match_naics_to_uniclass(naics_nodes, uniclass_nodes, min_score=0.15):
    """Find linguistic matches between NAICS and Uniclass."""
    candidates = []

    for n in naics_nodes:
        n_tokens = expand_synonyms(set(n['tokens']))
        if not n_tokens:
            continue

        matches = []
        for u in uniclass_nodes:
            u_tokens = expand_synonyms(set(u['tokens']))
            score = jaccard(n_tokens, u_tokens)
            if score >= min_score:
                matches.append({
                    'target_id': u['id'],
                    'target_name': u['name'],
                    'score': round(score, 3),
                    'shared_tokens': list(n_tokens & u_tokens)
                })

        if matches:
            matches.sort(key=lambda x: -x['score'])
            candidates.append({
                'source_id': n['id'],
                'source_name': n['name'],
                'source_tokens': list(n_tokens),
                'matches': matches[:10]  # Top 10
            })

    return candidates

def infer_relationship(naics_code: str, uniclass_table: str) -> str:
    """Infer relationship type from code patterns."""
    # NAICS 236 = GCs (manages), 237 = Heavy (produces), 238 = Trades (produces)
    if naics_code.startswith('236'):
        if uniclass_table in ['En', 'Co']:
            return 'manages'
        return 'coordinates'
    elif naics_code.startswith('237'):
        return 'produces'
    elif naics_code.startswith('238'):
        if uniclass_table == 'Pr':
            return 'uses'
        elif uniclass_table == 'Ac':
            return 'performs'
        return 'produces'
    return 'relatedTo'

def score_to_confidence(score: float) -> str:
    """Convert numeric score to confidence letter."""
    if score >= 0.5:
        return 'A'
    elif score >= 0.3:
        return 'B'
    elif score >= 0.2:
        return 'C'
    return 'D'

def main():
    OUTPUT.mkdir(exist_ok=True)

    # Load extracted nodes
    print("Loading extracted nodes...")
    with open(EXTRACTED / "naics.json") as f:
        naics = json.load(f)

    # Filter to construction sector only (23*)
    naics_construction = [n for n in naics if n['code'].startswith('23')]
    print(f"  NAICS construction: {len(naics_construction)}")

    for table in ['Ss', 'Pr', 'Ac', 'En', 'Co']:
        with open(EXTRACTED / f"uniclass_{table.lower()}.json") as f:
            uniclass = json.load(f)
        print(f"  Uniclass {table}: {len(uniclass)}")

        print(f"\nMatching NAICS -> Uniclass {table}...")
        candidates = match_naics_to_uniclass(naics_construction, uniclass)
        print(f"  Found {len(candidates)} NAICS codes with matches")

        # Enrich with relationship inference
        for c in candidates:
            naics_code = c['source_id'].replace('naics:', '')
            for m in c['matches']:
                m['relationship'] = infer_relationship(naics_code, table)
                m['confidence'] = score_to_confidence(m['score'])

        outfile = OUTPUT / f"naics_to_uniclass_{table.lower()}.json"
        with open(outfile, 'w') as f:
            json.dump(candidates, f, indent=2)
        print(f"  Saved to {outfile.name}")

    # Summary stats
    print("\n=== CANDIDATE SUMMARY ===")
    total_candidates = 0
    for table in ['Ss', 'Pr', 'Ac', 'En', 'Co']:
        with open(OUTPUT / f"naics_to_uniclass_{table.lower()}.json") as f:
            data = json.load(f)
        count = sum(len(c['matches']) for c in data)
        total_candidates += count
        print(f"  NAICS -> Uniclass {table}: {count} candidate mappings")
    print(f"  TOTAL: {total_candidates}")

if __name__ == "__main__":
    main()
