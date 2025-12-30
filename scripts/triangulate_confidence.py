"""
Triangulation Scoring - Combine Multiple Evidence Sources
Confidence increases when multiple independent methods agree
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

# Input files
LINGUISTIC_MATCHES = Path("crosswalk/review_ss.csv")
EMBEDDING_MATCHES = Path("crosswalk/embedding_ss.csv")
ONET_MATCHES = Path("crosswalk/onet_task_matches.json")
GROUND_TRUTH = Path("crosswalk/ground_truth.csv")
EXPERT_VALIDATIONS = Path("reviewed/expert_validations.json")

# Output
OUTPUT = Path("crosswalk/triangulated_mappings.json")

def load_linguistic_matches():
    """Load linguistic (Jaccard) matches"""
    matches = {}
    if LINGUISTIC_MATCHES.exists():
        with open(LINGUISTIC_MATCHES, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row.get('naics_code', ''), row.get('uniclass_code', ''))
                if key[0] and key[1]:
                    matches[key] = {
                        'method': 'linguistic',
                        'score': float(row.get('jaccard_score', 0) or 0),
                        'naics_title': row.get('naics_title', ''),
                        'uniclass_title': row.get('uniclass_title', '')
                    }
    return matches

def load_embedding_matches():
    """Load embedding (TF-IDF) matches"""
    matches = {}
    if EMBEDDING_MATCHES.exists():
        with open(EMBEDDING_MATCHES, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row.get('naics_code', ''), row.get('uniclass_code', ''))
                if key[0] and key[1]:
                    matches[key] = {
                        'method': 'embedding',
                        'score': float(row.get('cosine_score', 0) or 0),
                    }
    return matches

def load_onet_matches():
    """Load O*NET task-based matches"""
    matches = {}
    if ONET_MATCHES.exists():
        with open(ONET_MATCHES, 'r') as f:
            data = json.load(f)
            for m in data.get('mappings', []):
                naics = m.get('naics_code', '')
                uniclass = m.get('uniclass_ss', '')
                if naics and naics != 'unknown' and uniclass:
                    key = (naics, uniclass)
                    matches[key] = {
                        'method': 'onet_task',
                        'score': m.get('confidence', 0),
                        'occupation': m.get('occupation', ''),
                        'keywords': m.get('keywords', [])
                    }
    return matches

def load_ground_truth():
    """Load ground truth mappings (both methods agree)"""
    matches = set()
    if GROUND_TRUTH.exists():
        with open(GROUND_TRUTH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row.get('naics_code', ''), row.get('uniclass_code', ''))
                if key[0] and key[1]:
                    matches.add(key)
    return matches

def load_expert_validations():
    """Load expert validation decisions"""
    validated = set()
    rejected = set()

    if EXPERT_VALIDATIONS.exists():
        with open(EXPERT_VALIDATIONS, 'r') as f:
            data = json.load(f)
            for v in data.get('validations', []):
                # Parse mapping like "Siding -> Cladding systems"
                mapping = v.get('mapping', '')
                decision = v.get('decision', '')
                # Note: These are simplified mappings, not full codes
                # In production, would need code-level tracking
                if decision == 'Y':
                    validated.add(mapping)
                elif decision == 'N':
                    rejected.add(mapping)

    return validated, rejected

def triangulate():
    """Combine all evidence sources"""
    print("Loading evidence sources...")

    linguistic = load_linguistic_matches()
    print(f"  Linguistic matches: {len(linguistic)}")

    embedding = load_embedding_matches()
    print(f"  Embedding matches: {len(embedding)}")

    onet = load_onet_matches()
    print(f"  O*NET task matches: {len(onet)}")

    ground_truth = load_ground_truth()
    print(f"  Ground truth: {len(ground_truth)}")

    validated, rejected = load_expert_validations()
    print(f"  Expert validated: {len(validated)}, rejected: {len(rejected)}")

    # Combine all mappings
    all_mappings = set(linguistic.keys()) | set(embedding.keys()) | set(onet.keys())
    print(f"\nTotal unique mappings: {len(all_mappings)}")

    # Score each mapping
    results = []
    for key in all_mappings:
        naics, uniclass = key
        evidence = []
        total_score = 0

        if key in linguistic:
            evidence.append('linguistic')
            total_score += linguistic[key]['score']

        if key in embedding:
            evidence.append('embedding')
            total_score += embedding[key]['score']

        if key in onet:
            evidence.append('onet_task')
            total_score += onet[key]['score']

        if key in ground_truth:
            evidence.append('ground_truth')
            total_score += 0.5  # Bonus for ground truth

        # Calculate confidence tier
        num_methods = len(evidence)
        avg_score = total_score / num_methods if num_methods > 0 else 0

        if num_methods >= 3:
            tier = 1
            confidence = 'ground_truth'
        elif num_methods == 2:
            tier = 2 if avg_score >= 0.4 else 3
            confidence = 'high' if avg_score >= 0.4 else 'medium'
        else:
            tier = 3 if avg_score >= 0.5 else 4
            confidence = 'medium' if avg_score >= 0.5 else 'low'

        result = {
            'naics_code': naics,
            'uniclass_code': uniclass,
            'naics_title': linguistic.get(key, {}).get('naics_title', ''),
            'uniclass_title': linguistic.get(key, {}).get('uniclass_title', ''),
            'evidence_sources': evidence,
            'num_methods': num_methods,
            'total_score': round(total_score, 3),
            'avg_score': round(avg_score, 3),
            'tier': tier,
            'confidence': confidence
        }

        # Add O*NET details if available
        if key in onet:
            result['onet_occupation'] = onet[key].get('occupation', '')
            result['task_keywords'] = onet[key].get('keywords', [])

        results.append(result)

    # Sort by tier, then by num_methods, then by score
    results.sort(key=lambda x: (x['tier'], -x['num_methods'], -x['avg_score']))

    return results

def main():
    results = triangulate()

    # Statistics
    tier_counts = defaultdict(int)
    method_agreement = defaultdict(int)

    for r in results:
        tier_counts[r['tier']] += 1
        method_agreement[r['num_methods']] += 1

    output = {
        "_meta": {
            "description": "Triangulated confidence scores from multiple evidence sources",
            "sources": [
                "Linguistic matching (Jaccard similarity)",
                "Embedding matching (TF-IDF cosine)",
                "O*NET task keyword matching",
                "Ground truth (both methods agree)",
                "Expert validation"
            ],
            "tier_definitions": {
                "1": "3+ methods agree - Ground Truth",
                "2": "2 methods agree with high score",
                "3": "Single method with good score",
                "4": "Low confidence - needs review"
            }
        },
        "statistics": {
            "total_mappings": len(results),
            "tier_1": tier_counts[1],
            "tier_2": tier_counts[2],
            "tier_3": tier_counts[3],
            "tier_4": tier_counts[4],
            "methods_1": method_agreement[1],
            "methods_2": method_agreement[2],
            "methods_3": method_agreement[3],
            "methods_4_plus": sum(v for k, v in method_agreement.items() if k >= 4)
        },
        "mappings": results
    }

    # Save
    with open(OUTPUT, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n=== Triangulation Results ===")
    print(f"Total mappings: {len(results)}")
    print(f"\nBy Tier:")
    for tier in sorted(tier_counts.keys()):
        pct = tier_counts[tier] / len(results) * 100
        print(f"  Tier {tier}: {tier_counts[tier]} ({pct:.1f}%)")

    print(f"\nBy Method Agreement:")
    for methods in sorted(method_agreement.keys()):
        pct = method_agreement[methods] / len(results) * 100
        print(f"  {methods} method(s): {method_agreement[methods]} ({pct:.1f}%)")

    print(f"\nTop 10 highest confidence mappings:")
    for m in results[:10]:
        print(f"  [{m['tier']}] {m['naics_code']} -> {m['uniclass_code']}")
        print(f"      Evidence: {', '.join(m['evidence_sources'])}")
        if m.get('task_keywords'):
            print(f"      Keywords: {', '.join(m['task_keywords'][:5])}")

    print(f"\nSaved to: {OUTPUT}")

if __name__ == "__main__":
    main()
