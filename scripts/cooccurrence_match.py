#!/usr/bin/env python3
"""Co-occurrence based matching using structural proximity.

Since we lack real-world usage data, we infer co-occurrence from:
1. NAICS hierarchy siblings (same parent = likely co-occur in projects)
2. Uniclass table cross-references (Ss systems use Pr products)
3. Structural patterns (contractors doing related work)

This is a deterministic approximation of co-occurrence analysis.
"""

import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
EXTRACTED = BASE / "extracted"
CANDIDATES = BASE / "candidates"

def load_extracted(name: str) -> list:
    """Load extracted nodes."""
    path = EXTRACTED / f"{name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def get_naics_siblings() -> dict:
    """Group NAICS codes by parent (siblings co-occur in projects)."""
    naics = load_extracted("naics")
    siblings = defaultdict(list)

    for node in naics:
        code = node['id'].replace('naics:', '')
        if len(code) >= 4:
            parent = code[:4] if len(code) > 4 else code[:3]
            siblings[parent].append(node)

    return siblings

def get_uniclass_cross_refs() -> dict:
    """Map Uniclass tables that reference each other."""
    # Ss (Systems) typically use Pr (Products)
    # Ac (Activities) operate on Ss and Pr
    cross_refs = {
        'ss': ['pr'],  # Systems use products
        'pr': ['ss'],  # Products are used in systems
        'ac': ['ss', 'pr'],  # Activities work with systems and products
        'en': ['ss', 'pr'],  # Entities own/operate systems
    }
    return cross_refs

def build_cooccurrence_candidates():
    """Build candidates based on co-occurrence patterns."""
    naics = load_extracted("naics")
    siblings = get_naics_siblings()

    # Load existing linguistic matches to boost
    results = {}

    for table in ['ss', 'pr']:
        uc_nodes = load_extracted(f"uniclass_{table}")
        uc_by_prefix = defaultdict(list)

        # Group Uniclass by prefix (related systems/products)
        for node in uc_nodes:
            code = node['id'].replace('uc:', '')
            parts = code.split('_')
            if len(parts) >= 2:
                prefix = f"{parts[0]}_{parts[1]}"
                uc_by_prefix[prefix].append(node)

        # For each NAICS sibling group, find Uniclass groups they map to
        candidates = []

        for parent_code, sibling_nodes in siblings.items():
            # Load existing candidates for these siblings
            existing_file = CANDIDATES / f"naics_to_uniclass_{table}.json"
            if not existing_file.exists():
                continue

            with open(existing_file) as f:
                existing = json.load(f)

            existing_by_source = {c['source_id']: c for c in existing}

            # Find Uniclass codes that siblings map to
            uc_codes_used = defaultdict(int)
            for sib in sibling_nodes:
                if sib['id'] in existing_by_source:
                    for match in existing_by_source[sib['id']].get('matches', []):
                        uc_code = match['target_id'].replace('uc:', '')
                        parts = uc_code.split('_')
                        if len(parts) >= 2:
                            prefix = f"{parts[0]}_{parts[1]}"
                            uc_codes_used[prefix] += 1

            # Boost siblings that don't have matches but their cousins do
            for sib in sibling_nodes:
                if sib['id'] not in existing_by_source or not existing_by_source[sib['id']].get('matches'):
                    # Find best Uniclass prefix from siblings
                    if uc_codes_used:
                        best_prefix = max(uc_codes_used, key=uc_codes_used.get)
                        count = uc_codes_used[best_prefix]

                        if count >= 2 and best_prefix in uc_by_prefix:
                            # Add co-occurrence based candidates
                            for uc_node in uc_by_prefix[best_prefix][:3]:  # Top 3
                                candidates.append({
                                    'source_id': sib['id'],
                                    'source_name': sib['name'],
                                    'target_id': uc_node['id'],
                                    'target_name': uc_node['name'],
                                    'method': 'cooccurrence',
                                    'confidence': 'C',  # Lower confidence
                                    'score': min(0.25, count * 0.05),
                                    'evidence': f"siblings_with_match={count}"
                                })

        results[table] = candidates

    return results

def merge_with_existing(new_candidates: dict):
    """Merge co-occurrence candidates with existing."""
    for table, candidates in new_candidates.items():
        outfile = CANDIDATES / f"naics_to_uniclass_{table}_cooccur.json"

        # Group by source
        by_source = defaultdict(list)
        for c in candidates:
            by_source[c['source_id']].append({
                'target_id': c['target_id'],
                'target_name': c['target_name'],
                'relationship': 'related_to',
                'confidence': c['confidence'],
                'score': c['score'],
                'method': c['method'],
                'evidence': c['evidence']
            })

        output = []
        for source_id, matches in by_source.items():
            # Find source name
            name = matches[0].get('source_name', source_id) if matches else source_id
            for c in candidates:
                if c['source_id'] == source_id:
                    name = c['source_name']
                    break

            output.append({
                'source_id': source_id,
                'source_name': name,
                'matches': matches
            })

        with open(outfile, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Co-occurrence {table.upper()}: {len(candidates)} candidates -> {outfile.name}")

def stats():
    """Print co-occurrence statistics."""
    total = 0
    for table in ['ss', 'pr']:
        path = CANDIDATES / f"naics_to_uniclass_{table}_cooccur.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            count = sum(len(c.get('matches', [])) for c in data)
            total += count
            print(f"  {table.upper()}: {count} mappings")
    print(f"  Total: {total}")

if __name__ == "__main__":
    print("Building co-occurrence candidates...")
    candidates = build_cooccurrence_candidates()
    merge_with_existing(candidates)
    print("\nCo-occurrence stats:")
    stats()
