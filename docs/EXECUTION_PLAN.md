# Ontology Crosswalk Execution Plan

## Scope

**Total Nodes:** ~16,400 across all standards
**Target:** Review and link every node with typed relationships

---

## Phase Structure

### Phase 1: NAICS Construction Sector (Complete)
- [x] Sector 23 (Construction): 73 codes → 90 mappings
- Remaining NAICS: 2,136 codes (non-construction, lower priority)

### Phase 2: Uniclass Core Tables
- [ ] Ss (Systems): 2,416 nodes - **PRIMARY TARGET**
- [ ] Pr (Products): 7,892 nodes - **LARGEST SET**
- [ ] Ac (Activities): 927 nodes
- [ ] En (Entities): 531 nodes
- [ ] Co (Complexes): 393 nodes

### Phase 3: Schema.org Business Types
- [ ] Construction-relevant: ~50 types (HomeAndConstructionBusiness hierarchy)
- [ ] Organization types: ~100 types
- [ ] Remaining: 1,800+ (general web vocabulary, lower priority)

### Phase 4: UBL Documents
- [ ] Core documents: ~30 (Invoice, Order, Contract, etc.)
- [ ] Supporting components: ~35

---

## Parallel Execution Strategy

### Branch Structure

```
master (stable, verified)
  │
  ├── crosswalk/naics-uniclass-ss     ← NAICS → Uniclass Systems
  ├── crosswalk/naics-uniclass-pr     ← NAICS → Uniclass Products
  ├── crosswalk/uniclass-ss-pr        ← Systems → Products (requires)
  ├── crosswalk/schemaorg-naics       ← Schema.org → NAICS
  ├── crosswalk/ubl-corelot           ← UBL → CORELOT entities
  └── crosswalk/uniclass-hierarchy    ← Internal Uniclass partOf
```

### Work Distribution

| Branch | Nodes | Estimated Mappings | Parallelizable |
|--------|-------|-------------------|----------------|
| naics-uniclass-ss | 2,209 × 2,416 | ~5,000 | Yes |
| naics-uniclass-pr | 2,209 × 7,892 | ~3,000 | Yes |
| uniclass-ss-pr | 2,416 × 7,892 | ~10,000 | Yes |
| schemaorg-naics | 1,954 × 2,209 | ~500 | Yes |
| ubl-corelot | 65 × 100 | ~200 | Yes |
| uniclass-hierarchy | 12,159 | ~12,000 | Yes |

**Total Estimated Mappings:** ~30,000

---

## Execution Chunks

Each branch processes in chunks of 100 nodes:

```
Chunk 001: NAICS 111110-111999 (Agriculture)
Chunk 002: NAICS 112110-112990 (Animal Production)
...
Chunk 023: NAICS 236115-238990 (Construction) ← PRIORITY
...
```

### Chunk Processing Steps

1. **Extract** - Pull 100 nodes from source CSV/TOML
2. **Analyze** - Linguistic analysis of names/descriptions
3. **Match** - Find candidate mappings in target standard
4. **Classify** - Assign relationship type and confidence
5. **Validate** - Cross-check with methodology rules
6. **Commit** - Add to crosswalk CSV with derivation notes

---

## Success Outcomes

### Quantitative Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Node coverage | 100% of priority nodes | `wc -l` source vs mapped |
| Mapping completeness | ≥1 mapping per node | Script validation |
| Confidence distribution | ≥70% A or B rated | Aggregate stats |
| Derivation documented | 100% | DERIVATION_LOG entries |

### Qualitative Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Semantic accuracy | Industry-standard usage | Expert review |
| Relationship consistency | No conflicting edges | Graph validation |
| Reproducibility | Any reviewer can re-derive | Methodology test |

---

## Verification Process

### Automated Checks

```bash
# 1. Coverage check - all source nodes have mappings
python scripts/verify_coverage.py crosswalk/*.csv

# 2. Consistency check - no conflicting relationships
python scripts/verify_consistency.py crosswalk/*.csv

# 3. Confidence distribution
python scripts/analyze_confidence.py crosswalk/*.csv

# 4. Orphan detection - unmapped nodes
python scripts/find_orphans.py
```

### Manual Review Gates

| Gate | Trigger | Reviewer |
|------|---------|----------|
| PR Review | Every 500 mappings | Peer |
| Domain Expert | Every 2,000 mappings | Industry SME |
| Conflict Resolution | Any D-rated mapping | Committee |

---

## Conflict Review & Management

### Conflict Types

| Type | Example | Resolution |
|------|---------|------------|
| **Scope Overlap** | Two NAICS → same Uniclass | Both valid, document cardinality |
| **Semantic Mismatch** | Name suggests X, definition suggests Y | Use definition, note conflict |
| **Hierarchy Conflict** | Parent maps differently than child | Review parent, cascade fix |
| **Regional Variance** | US term vs UK term | Document both, add equivalentTo |

### Conflict Log Format

```csv
conflict_id,source,target,conflict_type,proposed_a,proposed_b,resolution,resolved_by,date
C001,naics:238220,uc:Ss_60_40,scope_overlap,HVAC only,Plumbing+HVAC,split mapping,claude,2025-12-30
```

### Resolution Workflow

```
1. Detect conflict (automated or manual)
     ↓
2. Log in conflicts/pending.csv
     ↓
3. Research industry practice
     ↓
4. Propose resolution with evidence
     ↓
5. Review (peer or SME)
     ↓
6. Apply fix to crosswalk
     ↓
7. Move to conflicts/resolved.csv
```

---

## Persistence Strategy

### Long-Running Session

For ~30,000 mappings at ~2 min/mapping = ~1,000 hours

**Options:**

1. **Chunked Sessions** (Recommended)
   - Process 100-500 mappings per session
   - Commit and push after each session
   - Resume from last checkpoint

2. **Parallel Agents**
   - Multiple Claude sessions on different branches
   - Merge via PR review
   - Coordinate via GitHub Issues

3. **Hybrid Human+AI**
   - AI generates candidate mappings
   - Human reviews and approves
   - Batch commits

### Checkpoint Format

```json
{
  "session_id": "2025-12-30-001",
  "branch": "crosswalk/naics-uniclass-ss",
  "last_processed": "naics:238350",
  "mappings_created": 127,
  "conflicts_pending": 3,
  "next_chunk": "NAICS 238390-238990"
}
```

Save to: `checkpoints/{session_id}.json`

---

## Immediate Next Steps

1. **Create branch structure**
   ```bash
   git checkout -b crosswalk/naics-uniclass-ss
   git checkout -b crosswalk/uniclass-hierarchy
   # etc.
   ```

2. **Build verification scripts**
   - `scripts/verify_coverage.py`
   - `scripts/verify_consistency.py`

3. **Start priority chunk**
   - Construction NAICS (236-238) → Uniclass Ss
   - Already 90 mappings, expand to full coverage

4. **Establish review cadence**
   - Weekly PR reviews
   - Monthly expert review

---

## Resource Estimation

| Resource | Quantity | Notes |
|----------|----------|-------|
| Total mappings | ~30,000 | Estimated |
| AI processing time | ~1,000 hours | At 2 min/mapping |
| Human review time | ~100 hours | At 10% review rate |
| Expert review time | ~20 hours | At 2% escalation |
| Calendar time | 3-6 months | With parallel execution |

---

*Systematic execution. Verifiable results. Managed conflicts.*
