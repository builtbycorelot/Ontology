#!/usr/bin/env python3
"""Run hypothesis tests on crosswalk mappings.

Tests:
H1: Specific trades map better than generic trades
H2: Embedding over-matches on construction terms
H3: UK/US terminology gap
H4: Ss maps better than Pr
H5: Hierarchical inheritance quality
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics

BASE = Path(__file__).parent.parent
CANDIDATES = BASE / "candidates"
EXTRACTED = BASE / "extracted"
REPORTS = BASE / "reports"

def load_candidates(pattern: str = "naics_to_*.json") -> dict:
    """Load candidate files."""
    results = defaultdict(list)
    for f in CANDIDATES.glob(pattern):
        with open(f) as fp:
            data = json.load(fp)
        for item in data:
            for m in item.get('matches', []):
                results[item['source_id']].append({
                    'target': m['target_id'],
                    'conf': m['confidence'],
                    'score': m.get('score', 0),
                    'file': f.stem
                })
    return dict(results)

def h1_specificity_test():
    """H1: Specific trades map better than generic trades."""
    print("\n" + "="*60)
    print("H1: Specific trades map better than generic trades")
    print("="*60)

    candidates = load_candidates()

    # Group by code length (specificity)
    by_length = defaultdict(list)
    for source_id, matches in candidates.items():
        code = source_id.replace('naics:', '')
        if not code.startswith('23'):
            continue
        length = len(code)

        # Calculate quality metrics
        high_conf = sum(1 for m in matches if m['conf'] in ['A', 'B'])
        total = len(matches)
        avg_score = statistics.mean(m['score'] for m in matches) if matches else 0

        by_length[length].append({
            'code': code,
            'high_pct': 100 * high_conf / total if total else 0,
            'avg_score': avg_score
        })

    print(f"\n{'Code Length':<12} {'Count':<8} {'Avg High-Conf %':<18} {'Avg Score'}")
    print("-" * 60)

    results = {}
    for length in sorted(by_length.keys()):
        items = by_length[length]
        avg_high = statistics.mean(i['high_pct'] for i in items)
        avg_score = statistics.mean(i['avg_score'] for i in items)
        results[length] = {'avg_high': avg_high, 'avg_score': avg_score}
        print(f"{length:<12} {len(items):<8} {avg_high:<18.1f} {avg_score:.3f}")

    # Verdict
    if results.get(6, {}).get('avg_high', 0) > results.get(4, {}).get('avg_high', 0):
        print("\n[OK] SUPPORTED: 6-digit codes have higher quality than 4-digit codes")
    else:
        print("\n[X] NOT SUPPORTED: No clear quality improvement with specificity")

    return results

def h2_embedding_overfit_test():
    """H2: Embedding over-matches on construction domain terms."""
    print("\n" + "="*60)
    print("H2: Embedding over-matches on construction terms")
    print("="*60)

    # Load embedding-only high confidence
    emb_only_high = []

    # Get linguistic mappings
    ling_map = set()
    for f in CANDIDATES.glob("naics_to_uniclass_*.json"):
        if 'embedding' in f.name or 'cooccur' in f.name or 'propagated' in f.name:
            continue
        with open(f) as fp:
            for item in json.load(fp):
                for m in item.get('matches', []):
                    if m['confidence'] in ['A', 'B']:
                        ling_map.add((item['source_id'], m['target_id']))

    # Find embedding A that linguistic didn't find as A/B
    for f in CANDIDATES.glob("*_embedding.json"):
        with open(f) as fp:
            for item in json.load(fp):
                for m in item.get('matches', []):
                    if m['confidence'] == 'A':
                        key = (item['source_id'], m['target_id'])
                        if key not in ling_map:
                            emb_only_high.append({
                                'source': item['source_id'],
                                'target': m['target_id'],
                                'target_name': m.get('target_name', ''),
                                'score': m['score']
                            })

    print(f"\nEmbedding-only A-confidence mappings: {len(emb_only_high)}")

    # Check for suspicious patterns
    construction_terms = ['construction', 'building', 'contractor']
    suspicious = []

    for m in emb_only_high:
        name = m['target_name'].lower()
        has_generic = any(t in name for t in construction_terms)
        if has_generic and m['score'] > 0.5:
            suspicious.append(m)

    print(f"Potentially over-matched (generic terms, score>0.5): {len(suspicious)}")

    print("\nSample suspicious matches:")
    for m in suspicious[:5]:
        print(f"  {m['source']} -> {m['target_name']} (score={m['score']:.3f})")

    if len(suspicious) > len(emb_only_high) * 0.3:
        print("\n[!] PARTIALLY SUPPORTED: >30% of embedding-only matches may be over-fitted")
    else:
        print("\n[OK] NOT SUPPORTED: Embedding matches appear semantically valid")

    return {'total': len(emb_only_high), 'suspicious': len(suspicious)}

def h3_ukus_terminology_test():
    """H3: UK/US terminology gap causes systematic misses."""
    print("\n" + "="*60)
    print("H3: UK/US terminology gap")
    print("="*60)

    # US-specific terms and UK equivalents
    us_uk_terms = {
        'siding': 'cladding',
        'drywall': 'plasterboard',
        'lumber': 'timber',
        'elevator': 'lift',
        'faucet': 'tap',
        'outlet': 'socket',
    }

    candidates = load_candidates()

    # Check which US terms appear in sources
    naics_path = EXTRACTED / "naics.json"
    with open(naics_path) as f:
        naics = json.load(f)

    us_coverage = {}
    for us_term, uk_term in us_uk_terms.items():
        us_sources = [n for n in naics if us_term in n['name'].lower()]
        if us_sources:
            # Check if they have high-confidence mappings
            high_conf = 0
            total = 0
            for source in us_sources:
                if source['id'] in candidates:
                    matches = candidates[source['id']]
                    high_conf += sum(1 for m in matches if m['conf'] in ['A', 'B'])
                    total += len(matches)
            us_coverage[us_term] = {
                'sources': len(us_sources),
                'high_conf': high_conf,
                'total': total,
                'uk_equiv': uk_term
            }

    print(f"\n{'US Term':<12} {'UK Equiv':<12} {'Sources':<10} {'High-Conf'}")
    print("-" * 50)
    for term, stats in us_coverage.items():
        pct = 100 * stats['high_conf'] / stats['total'] if stats['total'] else 0
        print(f"{term:<12} {stats['uk_equiv']:<12} {stats['sources']:<10} {pct:.1f}%")

    # Verdict based on whether US terms have lower coverage
    if us_coverage:
        avg_coverage = statistics.mean(
            100 * s['high_conf'] / s['total'] if s['total'] else 0
            for s in us_coverage.values()
        )
        print(f"\nAverage coverage for US-specific terms: {avg_coverage:.1f}%")
        if avg_coverage < 50:
            print("[!] SUPPORTED: US terminology has below-average coverage")
        else:
            print("[OK] NOT SUPPORTED: US terminology adequately covered")

    return us_coverage

def h4_ss_vs_pr_test():
    """H4: Uniclass Ss (Systems) maps better than Pr (Products)."""
    print("\n" + "="*60)
    print("H4: Ss (Systems) maps better than Pr (Products)")
    print("="*60)

    table_stats = {}

    for table in ['ss', 'pr', 'ac', 'en', 'co']:
        high_conf = 0
        total = 0
        scores = []

        for f in CANDIDATES.glob(f"naics_to_uniclass_{table}*.json"):
            with open(f) as fp:
                data = json.load(fp)
            for item in data:
                for m in item.get('matches', []):
                    total += 1
                    scores.append(m.get('score', 0))
                    if m['confidence'] in ['A', 'B']:
                        high_conf += 1

        if total:
            table_stats[table] = {
                'total': total,
                'high_conf': high_conf,
                'pct': 100 * high_conf / total,
                'avg_score': statistics.mean(scores) if scores else 0
            }

    print(f"\n{'Table':<8} {'Total':<10} {'High-Conf':<12} {'%':<8} {'Avg Score'}")
    print("-" * 50)
    for table, stats in sorted(table_stats.items(), key=lambda x: -x[1]['pct']):
        print(f"{table.upper():<8} {stats['total']:<10} {stats['high_conf']:<12} {stats['pct']:<8.1f} {stats['avg_score']:.3f}")

    ss_pct = table_stats.get('ss', {}).get('pct', 0)
    pr_pct = table_stats.get('pr', {}).get('pct', 0)

    if ss_pct > pr_pct:
        print(f"\n[OK] SUPPORTED: Ss ({ss_pct:.1f}%) > Pr ({pr_pct:.1f}%)")
    else:
        print(f"\n[X] NOT SUPPORTED: Pr ({pr_pct:.1f}%) >= Ss ({ss_pct:.1f}%)")

    return table_stats

def h5_hierarchy_quality_test():
    """H5: Hierarchical inheritance maintains quality."""
    print("\n" + "="*60)
    print("H5: Hierarchical inheritance quality")
    print("="*60)

    direct_stats = {'high': 0, 'total': 0, 'scores': []}
    propagated_stats = {'high': 0, 'total': 0, 'scores': []}

    for f in CANDIDATES.glob("naics_to_*.json"):
        is_propagated = 'propagated' in f.name
        target = propagated_stats if is_propagated else direct_stats

        with open(f) as fp:
            data = json.load(fp)

        for item in data:
            for m in item.get('matches', []):
                target['total'] += 1
                target['scores'].append(m.get('score', 0))
                if m['confidence'] in ['A', 'B']:
                    target['high'] += 1

    print(f"\n{'Type':<15} {'Total':<10} {'High-Conf':<12} {'%':<8} {'Avg Score'}")
    print("-" * 55)

    for name, stats in [('Direct', direct_stats), ('Propagated', propagated_stats)]:
        pct = 100 * stats['high'] / stats['total'] if stats['total'] else 0
        avg = statistics.mean(stats['scores']) if stats['scores'] else 0
        print(f"{name:<15} {stats['total']:<10} {stats['high']:<12} {pct:<8.1f} {avg:.3f}")

    direct_pct = 100 * direct_stats['high'] / direct_stats['total'] if direct_stats['total'] else 0
    prop_pct = 100 * propagated_stats['high'] / propagated_stats['total'] if propagated_stats['total'] else 0

    if prop_pct >= direct_pct * 0.8:  # Within 20%
        print(f"\n[OK] SUPPORTED: Propagated quality ({prop_pct:.1f}%) within 20% of direct ({direct_pct:.1f}%)")
    else:
        print(f"\n[!] PARTIALLY SUPPORTED: Quality degradation beyond 20%")

    return {'direct': direct_stats, 'propagated': propagated_stats}

def run_all_tests():
    """Run all hypothesis tests."""
    REPORTS.mkdir(exist_ok=True)

    print("\n" + "#"*60)
    print("# HYPOTHESIS TEST SUITE")
    print("#"*60)

    results = {
        'H1_specificity': h1_specificity_test(),
        'H2_embedding_overfit': h2_embedding_overfit_test(),
        'H3_ukus_gap': h3_ukus_terminology_test(),
        'H4_ss_vs_pr': h4_ss_vs_pr_test(),
        'H5_hierarchy': h5_hierarchy_quality_test(),
    }

    # Save results
    with open(REPORTS / 'hypothesis_tests.json', 'w') as f:
        # Convert to serializable
        def serialize(obj):
            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            else:
                return obj
        json.dump(serialize(results), f, indent=2, default=str)

    print("\n" + "#"*60)
    print(f"# Results saved to: {REPORTS / 'hypothesis_tests.json'}")
    print("#"*60)

if __name__ == "__main__":
    run_all_tests()
