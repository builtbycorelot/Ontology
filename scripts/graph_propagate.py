#!/usr/bin/env python3
"""Graph propagation for mapping inference.

Propagates mappings through the semantic graph:
1. If NAICS A -> Uniclass X (high confidence)
2. And Uniclass X is related to Uniclass Y
3. Then NAICS A -> Uniclass Y (lower confidence)

Also propagates across standards:
- NAICS -> Uniclass Ss -> Uniclass Pr (systems use products)
- Schema.org -> NAICS -> Uniclass (business types to work results)
"""

import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
EXTRACTED = BASE / "extracted"
CANDIDATES = BASE / "candidates"
CROSSWALK = BASE / "crosswalk"

def load_candidates(pattern: str) -> dict:
    """Load all candidate files matching pattern."""
    results = {}
    for path in CANDIDATES.glob(pattern):
        table = path.stem.split('_')[-1]  # Get table name
        with open(path) as f:
            results[table] = json.load(f)
    return results

def load_uniclass_hierarchy(table: str) -> dict:
    """Build Uniclass hierarchy from codes."""
    path = EXTRACTED / f"uniclass_{table}.json"
    if not path.exists():
        return {}

    with open(path) as f:
        nodes = json.load(f)

    hierarchy = {}
    for node in nodes:
        code = node['id'].replace('uc:', '')
        parts = code.split('_')
        hierarchy[code] = {
            'node': node,
            'parent': '_'.join(parts[:-1]) if len(parts) > 1 else None,
            'children': []
        }

    # Build child references
    for code, info in hierarchy.items():
        if info['parent'] and info['parent'] in hierarchy:
            hierarchy[info['parent']]['children'].append(code)

    return hierarchy

def propagate_ss_to_pr():
    """Propagate from Ss (Systems) to Pr (Products).

    Logic: If a contractor produces a system, they likely use related products.
    """
    ss_file = CANDIDATES / "naics_to_uniclass_ss.json"
    if not ss_file.exists():
        print("No Ss candidates to propagate")
        return []

    with open(ss_file) as f:
        ss_candidates = json.load(f)

    pr_nodes = []
    pr_path = EXTRACTED / "uniclass_pr.json"
    if pr_path.exists():
        with open(pr_path) as f:
            pr_nodes = json.load(f)

    # Index Pr nodes by prefix for matching
    pr_by_prefix = defaultdict(list)
    for node in pr_nodes:
        code = node['id'].replace('uc:', 'Pr_')
        parts = code.split('_')
        if len(parts) >= 2:
            # Match on numeric prefix (e.g., Ss_20 -> Pr_20)
            prefix = parts[1]
            pr_by_prefix[prefix].append(node)

    propagated = []

    for source in ss_candidates:
        source_id = source['source_id']
        source_name = source['source_name']

        pr_matches = []

        for match in source.get('matches', []):
            if match.get('confidence') not in ['A', 'B']:
                continue  # Only propagate high-confidence

            ss_code = match['target_id'].replace('uc:', '')
            parts = ss_code.split('_')
            if len(parts) >= 2:
                prefix = parts[1]

                # Find related Pr nodes
                for pr_node in pr_by_prefix.get(prefix, [])[:3]:
                    pr_matches.append({
                        'target_id': pr_node['id'],
                        'target_name': pr_node['name'],
                        'relationship': 'uses_product',
                        'confidence': 'C',  # Lowered confidence
                        'score': round(match.get('score', 0.3) * 0.6, 3),
                        'method': 'graph_propagation',
                        'source_mapping': f"{match['target_id']}"
                    })

        if pr_matches:
            # Deduplicate
            seen = set()
            unique = []
            for m in pr_matches:
                if m['target_id'] not in seen:
                    seen.add(m['target_id'])
                    unique.append(m)

            propagated.append({
                'source_id': source_id,
                'source_name': source_name,
                'matches': unique[:5]  # Top 5
            })

    return propagated

def propagate_schema_to_uniclass():
    """Propagate from Schema.org -> NAICS -> Uniclass.

    Logic: If Schema.org Electrician -> NAICS 238210, and NAICS 238210 -> Uniclass Ss_70,
    then Schema.org Electrician -> Uniclass Ss_70.
    """
    # Load Schema.org to NAICS crosswalk
    schema_naics_path = CROSSWALK / "schemaorg-to-naics.csv"
    if not schema_naics_path.exists():
        print("No Schema.org -> NAICS crosswalk")
        return []

    schema_to_naics = {}
    with open(schema_naics_path, encoding='utf-8') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 2:
                schema_id = parts[0]
                naics_code = parts[1]
                if schema_id not in schema_to_naics:
                    schema_to_naics[schema_id] = []
                schema_to_naics[schema_id].append(naics_code)

    # Load NAICS -> Uniclass candidates
    naics_to_uc = {}
    for table in ['ss', 'pr']:
        path = CANDIDATES / f"naics_to_uniclass_{table}.json"
        if path.exists():
            with open(path) as f:
                for item in json.load(f):
                    source_code = item['source_id'].replace('naics:', '')
                    if source_code not in naics_to_uc:
                        naics_to_uc[source_code] = []
                    naics_to_uc[source_code].extend(item.get('matches', []))

    # Propagate through the graph
    propagated = []

    for schema_id, naics_codes in schema_to_naics.items():
        uc_matches = []

        for naics_code in naics_codes:
            if naics_code in naics_to_uc:
                for match in naics_to_uc[naics_code]:
                    if match.get('confidence') in ['A', 'B']:
                        uc_matches.append({
                            'target_id': match['target_id'],
                            'target_name': match['target_name'],
                            'relationship': 'performs_work_on',
                            'confidence': 'C',
                            'score': round(match.get('score', 0.3) * 0.5, 3),
                            'method': 'graph_propagation',
                            'via': f"naics:{naics_code}"
                        })

        if uc_matches:
            # Deduplicate and limit
            seen = set()
            unique = []
            for m in uc_matches:
                if m['target_id'] not in seen:
                    seen.add(m['target_id'])
                    unique.append(m)

            propagated.append({
                'source_id': f"schema:{schema_id}",
                'source_name': schema_id.replace('schema:', ''),
                'matches': unique[:10]
            })

    return propagated

def save_propagated():
    """Run all propagations and save results."""
    # Ss -> Pr propagation
    ss_to_pr = propagate_ss_to_pr()
    if ss_to_pr:
        outfile = CANDIDATES / "naics_to_uniclass_pr_graph.json"
        with open(outfile, 'w') as f:
            json.dump(ss_to_pr, f, indent=2)
        count = sum(len(c.get('matches', [])) for c in ss_to_pr)
        print(f"Ss->Pr propagation: {len(ss_to_pr)} sources, {count} mappings")

    # Schema -> Uniclass propagation
    schema_to_uc = propagate_schema_to_uniclass()
    if schema_to_uc:
        outfile = CANDIDATES / "schema_to_uniclass_graph.json"
        with open(outfile, 'w') as f:
            json.dump(schema_to_uc, f, indent=2)
        count = sum(len(c.get('matches', [])) for c in schema_to_uc)
        print(f"Schema->Uniclass propagation: {len(schema_to_uc)} sources, {count} mappings")

def stats():
    """Print propagation statistics."""
    for name in ['naics_to_uniclass_pr_graph', 'schema_to_uniclass_graph']:
        path = CANDIDATES / f"{name}.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            count = sum(len(c.get('matches', [])) for c in data)
            print(f"  {name}: {count} mappings")

if __name__ == "__main__":
    print("Running graph propagation...\n")
    save_propagated()
    print("\nGraph propagation stats:")
    stats()
