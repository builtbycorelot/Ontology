#!/usr/bin/env python3
"""Embedding-based similarity matching using TF-IDF vectors.

Uses deterministic TF-IDF vectorization (no external APIs required).
This provides semantic similarity beyond simple token matching.

Method:
1. Build TF-IDF vectors from all node names/descriptions
2. Compute cosine similarity between NAICS and Uniclass vectors
3. Threshold to generate candidate mappings
"""

import json
import math
import re
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path(__file__).parent.parent
EXTRACTED = BASE / "extracted"
CANDIDATES = BASE / "candidates"

# Domain-specific term weights (boost construction terms)
DOMAIN_BOOST = {
    'construction': 1.5, 'building': 1.5, 'contractor': 1.3,
    'electrical': 1.4, 'plumbing': 1.4, 'hvac': 1.4,
    'concrete': 1.3, 'steel': 1.3, 'masonry': 1.3,
    'roofing': 1.3, 'flooring': 1.3, 'framing': 1.3,
    'system': 1.2, 'systems': 1.2, 'installation': 1.2,
}

def tokenize(text: str) -> list:
    """Tokenize text into normalized terms."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    stops = {'and', 'or', 'the', 'a', 'an', 'of', 'for', 'to', 'in', 'on', 'with', 'by', 'as', 'at', 'from', 'other'}
    return [t for t in tokens if t not in stops and len(t) > 1]

def load_extracted(name: str) -> list:
    """Load extracted nodes."""
    path = EXTRACTED / f"{name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

class TFIDFVectorizer:
    """Simple deterministic TF-IDF vectorizer."""

    def __init__(self):
        self.vocabulary = {}
        self.idf = {}
        self.doc_count = 0

    def fit(self, documents: list):
        """Build vocabulary and IDF from documents."""
        df = Counter()  # Document frequency
        self.doc_count = len(documents)

        # Build vocabulary and count document frequencies
        vocab_set = set()
        for doc in documents:
            tokens = set(tokenize(doc))
            vocab_set.update(tokens)
            for token in tokens:
                df[token] += 1

        # Create vocabulary index
        self.vocabulary = {term: i for i, term in enumerate(sorted(vocab_set))}

        # Compute IDF with smoothing
        for term, count in df.items():
            self.idf[term] = math.log((self.doc_count + 1) / (count + 1)) + 1

    def transform(self, text: str) -> dict:
        """Transform text to TF-IDF vector (sparse dict)."""
        tokens = tokenize(text)
        tf = Counter(tokens)

        vector = {}
        norm = 0

        for term, count in tf.items():
            if term in self.vocabulary:
                # TF-IDF with domain boost
                tfidf = count * self.idf.get(term, 1.0)
                tfidf *= DOMAIN_BOOST.get(term, 1.0)
                vector[term] = tfidf
                norm += tfidf ** 2

        # L2 normalize
        if norm > 0:
            norm = math.sqrt(norm)
            vector = {k: v / norm for k, v in vector.items()}

        return vector

def cosine_similarity(v1: dict, v2: dict) -> float:
    """Compute cosine similarity between sparse vectors."""
    common = set(v1.keys()) & set(v2.keys())
    if not common:
        return 0.0
    return sum(v1[k] * v2[k] for k in common)

def build_embedding_candidates(threshold: float = 0.15):
    """Build candidates using TF-IDF embedding similarity."""
    naics = load_extracted("naics")

    # Filter to construction sector (23xxx)
    naics = [n for n in naics if n['id'].replace('naics:', '').startswith('23')]

    results = {}

    for table in ['ss', 'pr', 'ac', 'en', 'co']:
        uc_nodes = load_extracted(f"uniclass_{table}")
        if not uc_nodes:
            continue

        # Build corpus from all documents
        all_docs = [n['name'] for n in naics] + [n['name'] for n in uc_nodes]

        # Fit vectorizer
        vectorizer = TFIDFVectorizer()
        vectorizer.fit(all_docs)

        # Vectorize all nodes
        naics_vectors = {n['id']: (n, vectorizer.transform(n['name'])) for n in naics}
        uc_vectors = {n['id']: (n, vectorizer.transform(n['name'])) for n in uc_nodes}

        candidates = []

        # Compute similarities
        for naics_id, (naics_node, naics_vec) in naics_vectors.items():
            matches = []

            for uc_id, (uc_node, uc_vec) in uc_vectors.items():
                sim = cosine_similarity(naics_vec, uc_vec)

                if sim >= threshold:
                    # Determine confidence from similarity
                    if sim >= 0.4:
                        conf = 'A'
                    elif sim >= 0.25:
                        conf = 'B'
                    elif sim >= 0.18:
                        conf = 'C'
                    else:
                        conf = 'D'

                    matches.append({
                        'target_id': uc_id,
                        'target_name': uc_node['name'],
                        'relationship': 'semantically_similar',
                        'confidence': conf,
                        'score': round(sim, 3),
                        'method': 'tfidf_embedding'
                    })

            if matches:
                # Sort by score, keep top 5
                matches.sort(key=lambda x: x['score'], reverse=True)
                candidates.append({
                    'source_id': naics_id,
                    'source_name': naics_node['name'],
                    'matches': matches[:5]
                })

        results[table] = candidates

    return results

def save_candidates(results: dict):
    """Save embedding candidates."""
    total = 0
    for table, candidates in results.items():
        if not candidates:
            continue

        outfile = CANDIDATES / f"naics_to_uniclass_{table}_embedding.json"
        with open(outfile, 'w') as f:
            json.dump(candidates, f, indent=2)

        count = sum(len(c.get('matches', [])) for c in candidates)
        total += count
        print(f"Embedding {table.upper()}: {len(candidates)} sources, {count} mappings")

    print(f"Total embedding mappings: {total}")

def stats():
    """Print embedding statistics."""
    total = 0
    for table in ['ss', 'pr', 'ac', 'en', 'co']:
        path = CANDIDATES / f"naics_to_uniclass_{table}_embedding.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            count = sum(len(c.get('matches', [])) for c in data)
            total += count
            print(f"  {table.upper()}: {count} mappings")
    print(f"  Total: {total}")

if __name__ == "__main__":
    print("Building TF-IDF embedding candidates...")
    print("(Deterministic - no external APIs)\n")
    results = build_embedding_candidates()
    save_candidates(results)
    print("\nEmbedding stats:")
    stats()
