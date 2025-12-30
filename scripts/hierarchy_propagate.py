#!/usr/bin/env python3
"""Propagate mappings through hierarchies."""

import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
EXTRACTED = BASE / "extracted"
CANDIDATES = BASE / "candidates"

def build_naics_hierarchy(nodes):
    """Build parent→children mapping for NAICS."""
    hierarchy = defaultdict(list)
    for n in nodes:
        code = n['code']
        # Parent is code with last digit(s) removed
        if len(code) > 2:
            parent = code[:-1]
            hierarchy[parent].append(code)
    return hierarchy

def build_uniclass_hierarchy(nodes):
    """Build parent→children mapping for Uniclass."""
    hierarchy = defaultdict(list)
    for n in nodes:
        code = n['code']
        parts = code.split('_')
        if len(parts) > 2:
            # Parent is one level up
            parent = '_'.join(parts[:-1])
            hierarchy[parent].append(code)
    return hierarchy

def propagate_mappings(candidates, naics_hier, uniclass_hier):
    """Propagate high-confidence mappings to children."""
    # Build lookup of existing mappings
    existing = {}
    for c in candidates:
        source = c['source_id'].replace('naics:', '')
        for m in c['matches']:
            if m['confidence'] in ['A', 'B']:
                target = m['target_id'].replace('uc:', '')
                key = (source, target)
                existing[key] = m

    propagated = []

    for (naics, uniclass), mapping in existing.items():
        # Get children of this NAICS
        naics_children = naics_hier.get(naics, [])

        # Get children of this Uniclass
        uniclass_children = uniclass_hier.get(uniclass, [])

        # Propagate to NAICS children → same Uniclass
        for nc in naics_children:
            key = (nc, uniclass)
            if key not in existing:
                propagated.append({
                    'source_id': f'naics:{nc}',
                    'target_id': f'uc:{uniclass}',
                    'relationship': mapping['relationship'],
                    'confidence': 'C',  # Lower confidence for propagated
                    'method': 'hierarchy_propagate',
                    'parent_source': f'naics:{naics}'
                })

        # Propagate to same NAICS → Uniclass children
        for uc in uniclass_children:
            key = (naics, uc)
            if key not in existing:
                propagated.append({
                    'source_id': f'naics:{naics}',
                    'target_id': f'uc:{uc}',
                    'relationship': mapping['relationship'],
                    'confidence': 'C',
                    'method': 'hierarchy_propagate',
                    'parent_target': f'uc:{uniclass}'
                })

    return propagated

def main():
    print("Loading data...")
    with open(EXTRACTED / "naics.json") as f:
        naics = json.load(f)

    naics_hier = build_naics_hierarchy(naics)
    print(f"  NAICS hierarchy: {len(naics_hier)} parent nodes")

    for table in ['Ss', 'Pr']:
        with open(EXTRACTED / f"uniclass_{table.lower()}.json") as f:
            uniclass = json.load(f)

        uniclass_hier = build_uniclass_hierarchy(uniclass)
        print(f"  Uniclass {table} hierarchy: {len(uniclass_hier)} parent nodes")

        # Load existing candidates
        cand_file = CANDIDATES / f"naics_to_uniclass_{table.lower()}.json"
        if cand_file.exists():
            with open(cand_file) as f:
                candidates = json.load(f)

            propagated = propagate_mappings(candidates, naics_hier, uniclass_hier)
            print(f"  Propagated {len(propagated)} new mappings for {table}")

            # Save propagated
            outfile = CANDIDATES / f"naics_to_uniclass_{table.lower()}_propagated.json"
            with open(outfile, 'w') as f:
                json.dump(propagated, f, indent=2)

if __name__ == "__main__":
    main()
