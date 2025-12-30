#!/usr/bin/env python3
"""Node health report - assess mapping coverage and quality.

Generates a comprehensive report on:
1. Node coverage (how many nodes have mappings)
2. Mapping quality (confidence distribution)
3. Method coverage (which methods found which mappings)
4. Conflicts and gaps
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

BASE = Path(__file__).parent.parent
EXTRACTED = BASE / "extracted"
CANDIDATES = BASE / "candidates"
REPORTS = BASE / "reports"

def load_extracted(name: str) -> list:
    """Load extracted nodes."""
    path = EXTRACTED / f"{name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def load_all_candidates() -> dict:
    """Load all candidate files."""
    all_mappings = defaultdict(lambda: defaultdict(list))  # source_id -> target_id -> [methods]
    method_stats = Counter()
    confidence_stats = Counter()

    for path in CANDIDATES.glob("*.json"):
        if 'propagated' in path.name:
            method = 'hierarchy'
        elif 'cooccur' in path.name:
            method = 'cooccurrence'
        elif 'embedding' in path.name:
            method = 'embedding'
        elif 'graph' in path.name:
            method = 'graph_propagation'
        else:
            method = 'linguistic'

        with open(path) as f:
            try:
                data = json.load(f)
            except:
                continue

        for item in data:
            source_id = item.get('source_id', '')
            for match in item.get('matches', []):
                target_id = match.get('target_id', '')
                conf = match.get('confidence', 'D')

                all_mappings[source_id][target_id].append({
                    'method': method,
                    'confidence': conf,
                    'score': match.get('score', 0)
                })
                method_stats[method] += 1
                confidence_stats[conf] += 1

    return dict(all_mappings), dict(method_stats), dict(confidence_stats)

def analyze_coverage():
    """Analyze node coverage across standards."""
    # Load node counts
    standards = {
        'naics': load_extracted('naics'),
        'uniclass_ss': load_extracted('uniclass_ss'),
        'uniclass_pr': load_extracted('uniclass_pr'),
        'uniclass_ac': load_extracted('uniclass_ac'),
        'uniclass_en': load_extracted('uniclass_en'),
        'uniclass_co': load_extracted('uniclass_co'),
        'schemaorg': load_extracted('schemaorg'),
    }

    all_mappings, method_stats, confidence_stats = load_all_candidates()

    # Count covered nodes
    coverage = {}
    for name, nodes in standards.items():
        node_ids = {n['id'] for n in nodes}
        covered = {sid for sid in all_mappings.keys() if sid in node_ids}

        # Also check if nodes appear as targets
        as_target = set()
        for source_mappings in all_mappings.values():
            for target_id in source_mappings.keys():
                if target_id in node_ids:
                    as_target.add(target_id)

        coverage[name] = {
            'total': len(nodes),
            'as_source': len(covered),
            'as_target': len(as_target),
            'combined': len(covered | as_target),
            'pct_source': round(100 * len(covered) / len(nodes), 1) if nodes else 0,
            'pct_combined': round(100 * len(covered | as_target) / len(nodes), 1) if nodes else 0,
        }

    return coverage, method_stats, confidence_stats, all_mappings

def find_conflicts(all_mappings: dict) -> list:
    """Find mappings where methods disagree."""
    conflicts = []

    for source_id, targets in all_mappings.items():
        for target_id, methods in targets.items():
            if len(methods) > 1:
                confidences = [m['confidence'] for m in methods]
                # Conflict if confidences differ by more than 1 level
                conf_order = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                conf_vals = [conf_order.get(c, 3) for c in confidences]
                if max(conf_vals) - min(conf_vals) >= 2:
                    conflicts.append({
                        'source': source_id,
                        'target': target_id,
                        'methods': methods
                    })

    return conflicts

def find_gaps(all_mappings: dict) -> dict:
    """Find nodes with no or low-quality mappings."""
    naics = load_extracted('naics')
    naics_23 = [n for n in naics if n['id'].replace('naics:', '').startswith('23')]

    gaps = {
        'no_mapping': [],
        'low_confidence_only': [],
    }

    for node in naics_23:
        nid = node['id']
        if nid not in all_mappings or not all_mappings[nid]:
            gaps['no_mapping'].append(node)
        else:
            # Check if only low confidence
            all_conf = []
            for target_methods in all_mappings[nid].values():
                all_conf.extend([m['confidence'] for m in target_methods])
            if all_conf and all(c in ['C', 'D'] for c in all_conf):
                gaps['low_confidence_only'].append(node)

    return gaps

def generate_report():
    """Generate comprehensive health report."""
    REPORTS.mkdir(exist_ok=True)

    coverage, method_stats, confidence_stats, all_mappings = analyze_coverage()
    conflicts = find_conflicts(all_mappings)
    gaps = find_gaps(all_mappings)

    # Calculate totals
    total_mappings = sum(method_stats.values())
    unique_pairs = sum(len(targets) for targets in all_mappings.values())

    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_mapping_instances': total_mappings,
            'unique_source_target_pairs': unique_pairs,
            'sources_with_mappings': len(all_mappings),
            'conflicts_detected': len(conflicts),
            'naics_gaps': len(gaps['no_mapping']),
            'naics_low_quality': len(gaps['low_confidence_only']),
        },
        'coverage': coverage,
        'methods': dict(method_stats),
        'confidence_distribution': dict(confidence_stats),
        'conflicts_sample': conflicts[:20],  # First 20
        'gaps_sample': {
            'no_mapping': [n['id'] for n in gaps['no_mapping'][:20]],
            'low_confidence': [n['id'] for n in gaps['low_confidence_only'][:20]],
        }
    }

    # Save JSON report
    with open(REPORTS / 'node_health.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("=" * 60)
    print("NODE HEALTH REPORT")
    print("=" * 60)
    print(f"Generated: {report['generated_at']}")
    print()

    print("SUMMARY")
    print("-" * 40)
    for k, v in report['summary'].items():
        print(f"  {k.replace('_', ' ').title()}: {v}")
    print()

    print("COVERAGE BY STANDARD")
    print("-" * 40)
    for name, stats in coverage.items():
        print(f"  {name}:")
        print(f"    Total nodes: {stats['total']}")
        print(f"    As source: {stats['as_source']} ({stats['pct_source']}%)")
        print(f"    Combined: {stats['combined']} ({stats['pct_combined']}%)")
    print()

    print("METHOD CONTRIBUTIONS")
    print("-" * 40)
    for method, count in sorted(method_stats.items(), key=lambda x: -x[1]):
        pct = round(100 * count / total_mappings, 1) if total_mappings else 0
        print(f"  {method}: {count} ({pct}%)")
    print()

    print("CONFIDENCE DISTRIBUTION")
    print("-" * 40)
    for conf in ['A', 'B', 'C', 'D']:
        count = confidence_stats.get(conf, 0)
        pct = round(100 * count / total_mappings, 1) if total_mappings else 0
        bar = '#' * int(pct / 2)
        print(f"  {conf}: {count:5} ({pct:5.1f}%) {bar}")
    print()

    print(f"Full report saved to: {REPORTS / 'node_health.json'}")
    print("=" * 60)

    return report

if __name__ == "__main__":
    generate_report()
