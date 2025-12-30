# Node Interrelation Methods & Compute Estimation

## Interrelation Methods

We use **multiple complementary methods** to establish relationships between nodes. Each method has different accuracy/speed tradeoffs.

---

## Method 1: Linguistic Analysis (Primary)

**Approach:** Parse node names and descriptions for semantic matching.

```
Input:  NAICS "238130 Framing Contractors"
        Uniclass "Ss_25_10_30 Timber frame wall structure systems"

Analysis:
  - Extract root: "Framing" → "frame"
  - Match in target: "frame" appears in Uniclass title
  - Relationship: produces (trade → work result)
  - Confidence: A (direct linguistic match)
```

**Compute Cost:**
- Tokenization: O(n) per node name
- String matching: O(n × m) for n source × m target
- Total: ~0.01 sec/pair

**For 16,400 nodes × 16,400 potential pairs:**
- Pairs: 268 million (but filtered by relevance)
- Realistic pairs: ~500,000 (same domain)
- Time: ~1.4 hours (automated)

---

## Method 2: Hierarchical Inheritance

**Approach:** If parent maps, children likely map to children.

```
NAICS Hierarchy:
  238 (Specialty Trade) → 2381 (Foundation/Structure) → 23813 → 238130

Uniclass Hierarchy:
  Ss_25 (Wall systems) → Ss_25_10 (Wall structure) → Ss_25_10_30 (Timber frame)

Rule: If 238 → Ss, then 2381 likely → Ss_25
```

**Compute Cost:**
- Build hierarchy trees: O(n log n)
- Traverse and propagate: O(n)
- Total: ~0.001 sec/node

**For 16,400 nodes:**
- Time: ~16 seconds (automated)

---

## Method 3: Co-occurrence Analysis

**Approach:** Nodes that appear together in real documents are related.

```
Training Data: Industry specifications, invoices, contracts
Example: "Framing" and "dimensional lumber" co-occur frequently
Inference: naics:238130 → uc:Pr_20_93_52 (uses relationship)
```

**Compute Cost:**
- Corpus indexing: O(d × w) for d documents × w words
- PMI calculation: O(v²) for vocabulary v
- Total: Depends on corpus size

**Estimated (100K document corpus):**
- Indexing: ~2 hours
- Analysis: ~30 minutes
- Benefit: Discovers implicit relationships

---

## Method 4: Embedding Similarity (AI-Assisted)

**Approach:** Use language model embeddings to find semantic similarity.

```python
# Pseudocode
embedding_naics = model.encode("Framing Contractors")
embedding_uniclass = model.encode("Timber frame wall structure systems")
similarity = cosine(embedding_naics, embedding_uniclass)  # 0.87
```

**Compute Cost:**
- Embedding generation: ~0.05 sec/node (with GPU)
- Similarity matrix: O(n²) comparisons
- Total for 16,400 nodes: ~14 minutes embedding + 4.5 hours similarity

**With GPU acceleration:**
- Embedding: ~2 minutes (batch)
- Similarity: ~30 minutes (vectorized)

---

## Method 5: Expert Knowledge Graph Seeding

**Approach:** Start with known high-confidence mappings, expand.

```
Seed mappings (from industry standards):
  - CSI Division 06 ≈ NAICS 238350 (Finish Carpentry)
  - This implies: 238350 → Ss_25_11 (Internal wall systems)

Expansion:
  - Find similar NAICS codes
  - Suggest similar Uniclass mappings
```

**Compute Cost:**
- Seed collection: Manual (0 compute, human time)
- Expansion: O(n × k) for k neighbors
- Total: ~5 minutes (automated expansion)

---

## Method 6: Graph Propagation

**Approach:** Use existing edges to infer new edges.

```
Known:
  naics:238130 --produces--> uc:Ss_25_10_30
  uc:Ss_25_10_30 --requires--> uc:Pr_20_93_52

Inferred:
  naics:238130 --uses--> uc:Pr_20_93_52 (transitive)
```

**Compute Cost:**
- Graph construction: O(E) for E edges
- Transitive closure: O(V × E) worst case
- With pruning: O(E × k) for k-hop limit

**For 30,000 edges:**
- Time: ~2 minutes

---

## Combined Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERRELATION PIPELINE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Method 1   │    │   Method 2   │    │   Method 3   │  │
│  │  Linguistic  │    │  Hierarchy   │    │ Co-occurrence│  │
│  │   Analysis   │    │ Inheritance  │    │   Analysis   │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│         └───────────────────┼───────────────────┘           │
│                             ▼                               │
│                   ┌──────────────────┐                      │
│                   │   CANDIDATE      │                      │
│                   │   AGGREGATOR     │                      │
│                   └────────┬─────────┘                      │
│                            │                                │
│         ┌──────────────────┼──────────────────┐            │
│         ▼                  ▼                  ▼            │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │   Method 4   │   │   Method 5   │   │   Method 6   │   │
│  │  Embedding   │   │    Expert    │   │    Graph     │   │
│  │  Similarity  │   │   Seeding    │   │ Propagation  │   │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            ▼                               │
│                   ┌──────────────────┐                      │
│                   │    CONFLICT      │                      │
│                   │    RESOLVER      │                      │
│                   └────────┬─────────┘                      │
│                            │                                │
│                            ▼                                │
│                   ┌──────────────────┐                      │
│                   │   VALIDATED      │                      │
│                   │   CROSSWALK      │                      │
│                   └──────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Compute Requirements Summary

| Method | CPU Time | GPU Time | Memory | Notes |
|--------|----------|----------|--------|-------|
| Linguistic | 1.4 hrs | N/A | 2 GB | Parallelizable |
| Hierarchy | 16 sec | N/A | 1 GB | Fast |
| Co-occurrence | 2.5 hrs | N/A | 8 GB | Needs corpus |
| Embedding | 4.5 hrs | 32 min | 4 GB | GPU recommended |
| Expert Seed | 0 | 0 | 0 | Human time |
| Graph Prop | 2 min | N/A | 2 GB | Fast |
| **Total** | **~8.5 hrs** | **~35 min** | **8 GB peak** | |

### Hardware Options

| Setup | Total Time | Cost |
|-------|------------|------|
| Local CPU (8-core) | ~8 hours | $0 |
| Local GPU (RTX 3080) | ~2 hours | $0 |
| Cloud GPU (A100) | ~30 min | ~$5 |
| Cloud CPU cluster (32 vCPU) | ~2 hours | ~$10 |

---

## Conflict Detection & Resolution

### Conflict Types

| Type | Detection Method | Resolution Strategy |
|------|------------------|---------------------|
| **Duplicate Edge** | Hash collision | Keep highest confidence |
| **Contradictory Edge** | A→B and A→¬B | Expert review |
| **Cycle** | DFS traversal | Break weakest edge |
| **Orphan** | Degree = 0 | Force linguistic match |
| **Overload** | Degree > threshold | Split into subtypes |

### Conflict Resolution Algorithm

```python
def resolve_conflicts(candidates):
    conflicts = []

    for (source, target, rel, conf) in candidates:
        existing = graph.get_edge(source, target)

        if existing is None:
            graph.add_edge(source, target, rel, conf)

        elif existing.rel == rel:
            # Duplicate - keep higher confidence
            if conf > existing.conf:
                graph.update_edge(source, target, rel, conf)

        elif existing.rel != rel:
            # Contradiction - log for review
            conflicts.append({
                'source': source,
                'target': target,
                'existing': existing,
                'proposed': (rel, conf),
                'resolution': 'pending'
            })

    return conflicts
```

### Conflict Log Schema

```csv
conflict_id,source_id,target_id,existing_rel,existing_conf,proposed_rel,proposed_conf,detection_method,resolution,resolved_by,resolved_date
```

### Resolution Workflow

```
Conflict Detected
      │
      ▼
┌─────────────────┐
│ Confidence Gap? │──Yes──▶ Auto-resolve (keep higher)
│   > 2 levels    │
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐
│ Same Category?  │──Yes──▶ Keep both (multi-valued)
│                 │
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐
│ Expert Review   │──────▶ Human decision
│                 │
└─────────────────┘
```

---

## Parallel Execution Branches

| Branch | Focus | Method Priority | Estimated Time |
|--------|-------|-----------------|----------------|
| `crosswalk/naics-ss` | NAICS → Uniclass Ss | 1, 2, 4 | 3 hrs |
| `crosswalk/naics-pr` | NAICS → Uniclass Pr | 1, 3, 4 | 4 hrs |
| `crosswalk/ss-pr` | Uniclass Ss → Pr | 2, 6 | 2 hrs |
| `crosswalk/hierarchy` | All internal partOf | 2 | 30 min |
| `crosswalk/schemaorg` | Schema.org → NAICS | 1, 4 | 1 hr |

**Total with parallelization:** ~4 hours (bottleneck: naics-pr)

---

## Verification Gates

| Gate | Trigger | Auto/Manual | Action |
|------|---------|-------------|--------|
| Coverage | < 95% nodes mapped | Auto | Flag for review |
| Confidence | > 30% low-conf | Auto | Escalate batch |
| Conflict Rate | > 5% conflicts | Auto | Pause, review methodology |
| Cycle Detected | Any cycle | Auto | Break + log |
| Expert Review | Every 2000 mappings | Manual | Domain SME sign-off |

---

*Multiple methods. Verified results. Managed conflicts.*
