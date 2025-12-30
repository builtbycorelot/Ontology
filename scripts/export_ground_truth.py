#!/usr/bin/env python3
"""Export ground truth mappings - where multiple methods agree.

Exports mappings to:
1. ground_truth.csv - For direct use
2. ground_truth.json - For programmatic use
3. validation_tiers.json - Organized by confidence tier
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE = Path(__file__).parent.parent
CANDIDATES = BASE / "candidates"
EXTRACTED = BASE / "extracted"
CROSSWALK = BASE / "crosswalk"

def load_names():
    """Load all node names."""
    names = {}

    # NAICS
    naics_path = EXTRACTED / "naics.json"
    if naics_path.exists():
        with open(naics_path) as f:
            for n in json.load(f):
                names[n['id']] = n['name']

    # Uniclass
    for table in ['ss', 'pr', 'ac', 'en', 'co']:
        path = EXTRACTED / f"uniclass_{table}.json"
        if path.exists():
            with open(path) as f:
                for n in json.load(f):
                    names[n['id']] = n['name']

    return names

def load_all_mappings():
    """Load all mappings grouped by source-target pair."""
    mappings = defaultdict(lambda: {'methods': [], 'confidences': [], 'scores': []})

    for f in CANDIDATES.glob("*.json"):
        # Determine method
        if 'propagated' in f.name:
            method = 'hierarchy'
        elif 'cooccur' in f.name:
            method = 'cooccurrence'
        elif 'embedding' in f.name:
            method = 'embedding'
        elif 'graph' in f.name:
            method = 'graph'
        else:
            method = 'linguistic'

        with open(f) as fp:
            try:
                data = json.load(fp)
            except:
                continue

        for item in data:
            source_id = item.get('source_id', '')
            for match in item.get('matches', []):
                target_id = match.get('target_id', '')
                key = (source_id, target_id)

                mappings[key]['methods'].append(method)
                mappings[key]['confidences'].append(match.get('confidence', 'D'))
                mappings[key]['scores'].append(match.get('score', 0))
                mappings[key]['relationship'] = match.get('relationship', 'related_to')

    return dict(mappings)

def classify_tiers(mappings):
    """Classify mappings into validation tiers."""
    tiers = {
        'tier1_ground_truth': [],  # Both linguistic and embedding agree A/B
        'tier2_high_single': [],    # One method A confidence
        'tier3_conflicts': [],       # Methods disagree by 2+ levels
        'tier4_low_confidence': [],  # Only C/D confidence
    }

    conf_rank = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    names = load_names()

    for (source_id, target_id), data in mappings.items():
        methods = set(data['methods'])
        confs = data['confidences']
        scores = data['scores']

        best_conf = min(confs, key=lambda c: conf_rank.get(c, 3))
        worst_conf = max(confs, key=lambda c: conf_rank.get(c, 3))
        avg_score = sum(scores) / len(scores) if scores else 0

        record = {
            'source_id': source_id,
            'source_name': names.get(source_id, source_id),
            'target_id': target_id,
            'target_name': names.get(target_id, target_id),
            'relationship': data.get('relationship', 'related_to'),
            'best_confidence': best_conf,
            'methods': list(methods),
            'method_count': len(methods),
            'avg_score': round(avg_score, 3),
        }

        # Classify
        has_linguistic = 'linguistic' in methods
        has_embedding = 'embedding' in methods
        ling_high = any(c in ['A', 'B'] for c, m in zip(confs, data['methods']) if m == 'linguistic')
        emb_high = any(c in ['A', 'B'] for c, m in zip(confs, data['methods']) if m == 'embedding')

        conf_spread = conf_rank.get(worst_conf, 3) - conf_rank.get(best_conf, 0)

        if has_linguistic and has_embedding and ling_high and emb_high:
            tiers['tier1_ground_truth'].append(record)
        elif best_conf == 'A':
            tiers['tier2_high_single'].append(record)
        elif conf_spread >= 2:
            tiers['tier3_conflicts'].append(record)
        else:
            tiers['tier4_low_confidence'].append(record)

    # Sort each tier by score
    for tier in tiers.values():
        tier.sort(key=lambda x: -x['avg_score'])

    return tiers

def export_ground_truth():
    """Export ground truth to CSV and JSON."""
    print("Loading mappings...")
    mappings = load_all_mappings()
    print(f"Loaded {len(mappings)} unique source-target pairs")

    print("\nClassifying into tiers...")
    tiers = classify_tiers(mappings)

    for name, items in tiers.items():
        print(f"  {name}: {len(items)}")

    CROSSWALK.mkdir(exist_ok=True)

    # Export Tier 1 (ground truth) to CSV
    tier1 = tiers['tier1_ground_truth']
    csv_path = CROSSWALK / "ground_truth.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'source_id', 'source_name', 'target_id', 'target_name',
            'relationship', 'best_confidence', 'method_count', 'avg_score'
        ])
        writer.writeheader()
        for item in tier1:
            row = {k: v for k, v in item.items() if k in writer.fieldnames}
            writer.writerow(row)
    print(f"\nExported {len(tier1)} ground truth mappings to {csv_path}")

    # Export all tiers to JSON
    json_path = CROSSWALK / "validation_tiers.json"
    export_data = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'tier1_ground_truth': len(tiers['tier1_ground_truth']),
            'tier2_high_single': len(tiers['tier2_high_single']),
            'tier3_conflicts': len(tiers['tier3_conflicts']),
            'tier4_low_confidence': len(tiers['tier4_low_confidence']),
            'total': len(mappings),
        },
        'tiers': tiers
    }
    with open(json_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    print(f"Exported all tiers to {json_path}")

    # Print summary
    print("\n" + "="*60)
    print("VALIDATION TIER SUMMARY")
    print("="*60)
    print(f"""
Tier 1 - Ground Truth (both methods agree A/B): {len(tiers['tier1_ground_truth'])}
  -> Ready for immediate adoption
  -> Export: {csv_path}

Tier 2 - High Single Method (one method A): {len(tiers['tier2_high_single'])}
  -> Needs spot-check validation
  -> If >85% accurate, bulk accept

Tier 3 - Conflicts (methods disagree): {len(tiers['tier3_conflicts'])}
  -> Needs expert review
  -> Use to calibrate method weights

Tier 4 - Low Confidence (C/D only): {len(tiers['tier4_low_confidence'])}
  -> Manual mapping or discard
  -> May indicate gaps in Uniclass coverage
""")

    return tiers

if __name__ == "__main__":
    export_ground_truth()
