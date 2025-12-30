#!/usr/bin/env python3
"""Generate crosswalk CSV from reviewed candidates."""

import json
import csv
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
CANDIDATES = BASE / "candidates"
CROSSWALK = BASE / "crosswalk"
REVIEWED = BASE / "reviewed"

def load_candidates(table: str):
    """Load candidate mappings for a table."""
    path = CANDIDATES / f"naics_to_uniclass_{table.lower()}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def load_reviewed(table: str):
    """Load expert-reviewed decisions."""
    path = REVIEWED / f"naics_to_uniclass_{table.lower()}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def generate_csv(table: str, min_confidence='C'):
    """Generate crosswalk CSV for a table."""
    candidates = load_candidates(table)
    reviewed = load_reviewed(table)

    conf_order = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    min_conf_val = conf_order.get(min_confidence, 2)

    rows = []
    for c in candidates:
        source_id = c['source_id']
        source_name = c['source_name']
        naics_code = source_id.replace('naics:', '')

        for m in c['matches']:
            target_id = m['target_id']
            conf = m['confidence']

            # Skip low confidence unless reviewed
            review_key = f"{source_id}|{target_id}"
            if review_key in reviewed:
                decision = reviewed[review_key]
                if decision['action'] == 'reject':
                    continue
                if decision['action'] == 'accept':
                    conf = decision.get('confidence', conf)
                    m['relationship'] = decision.get('relationship', m['relationship'])
            elif conf_order.get(conf, 3) > min_conf_val:
                continue

            rows.append({
                'naics_code': naics_code,
                'naics_name': source_name,
                'relationship': m['relationship'],
                'uniclass_code': target_id.replace('uc:', ''),
                'uniclass_table': table,
                'uniclass_title': m['target_name'],
                'cardinality': '1:N',
                'confidence': conf,
                'notes': f"score={m['score']}"
            })

    return rows

def main():
    REVIEWED.mkdir(exist_ok=True)

    all_rows = []
    for table in ['Ss', 'Pr', 'Ac', 'En', 'Co']:
        rows = generate_csv(table)
        all_rows.extend(rows)
        print(f"Uniclass {table}: {len(rows)} mappings")

    # Sort by NAICS code
    all_rows.sort(key=lambda x: x['naics_code'])

    # Write CSV
    outfile = CROSSWALK / "naics-to-uniclass-generated.csv"
    fieldnames = ['naics_code', 'naics_name', 'relationship', 'uniclass_code',
                  'uniclass_table', 'uniclass_title', 'cardinality', 'confidence', 'notes']

    with open(outfile, 'w', newline='', encoding='utf-8') as f:
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write("# Source: scripts/generate_crosswalk.py\n")
        f.write("# Review status: auto-generated, pending expert review\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nTotal: {len(all_rows)} mappings")
    print(f"Output: {outfile}")

if __name__ == "__main__":
    main()
