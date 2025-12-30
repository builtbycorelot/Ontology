# Crosswalk Analysis and Adoption Recommendations

## Executive Summary

This analysis examines 2,820 candidate mappings between NAICS (North American Industry Classification) and Uniclass (UK construction classification) generated through multiple deterministic methods. We identify patterns, propose validation tests, and recommend a phased adoption strategy.

**Key Findings:**
- 250 mappings have strong agreement across methods (ground truth candidates)
- Specific trade contractors (framing, masonry, electrical) map excellently
- Generic "Other" categories have poor coverage
- Embedding method shows semantic understanding but may over-match
- Linguistic method is conservative but precise

---

## 1. Coverage Analysis

### 1.1 Strong Coverage Trades (>90% high-confidence)

| NAICS Code | Trade | Avg Score | Observation |
|------------|-------|-----------|-------------|
| 23813 | Framing Contractors | 0.634 | Direct mapping to structural systems |
| 23814 | Masonry Contractors | 0.583 | Strong material-based matching |
| 23815 | Glass and Glazing | 0.554 | Specialized systems align well |
| 23833 | Flooring Contractors | 0.498 | Clear system-product relationship |
| 23816 | Roofing Contractors | 0.488 | Distinct roof systems category |
| 23821 | Electrical Contractors | 0.431 | Electrical systems well-defined |

**Pattern:** Trades with specific materials or systems have strong Uniclass equivalents.

### 1.2 Weak Coverage Trades (<50% high-confidence)

| NAICS Code | Trade | Avg Score | Issue |
|------------|-------|-----------|-------|
| 23817 | Siding Contractors | 0.250 | Limited UK equivalent (cladding?) |
| 23829 | Other Building Equipment | 0.290 | Catch-all category |
| 23891 | Site Preparation | 0.288 | Civil vs building taxonomy gap |
| 23899 | All Other Specialty Trade | 0.227 | Too generic |
| 23839 | Other Building Finishing | 0.312 | Catch-all category |

**Pattern:** Generic categories don't map well because Uniclass has specific categories.

---

## 2. Method Performance

### 2.1 Method Contributions

| Method | Mappings | % of Total | High-Conf % |
|--------|----------|------------|-------------|
| Linguistic (token-based) | 1,684 | 59.7% | 82.9% |
| TF-IDF Embedding | 1,085 | 38.5% | 90.4% |
| Co-occurrence | 51 | 1.8% | 0.0% |

### 2.2 Method Agreement

- **250 mappings** where both Linguistic AND Embedding agree on A or B confidence
- These represent highest-confidence ground truth candidates
- Examples:
  - "Construction" → "Construction" (perfect 1.0 match)
  - "Framing Contractors" → "Structural framing systems" (0.667 + 0.664)
  - "Masonry Contractors" → "Masonry surveying" (0.600 + 0.833)

### 2.3 Conflict Analysis

All analyzed conflicts show **Embedding more confident than Linguistic**:

| Conflict Type | Count | Interpretation |
|---------------|-------|----------------|
| Embedding A vs Linguistic C | 15 | Embedding sees semantic similarity |
| Embedding A vs Linguistic D | 5 | Token overlap minimal but concept matches |

**Hypothesis:** Embedding captures domain semantics (e.g., "construction joint sealants" relates to "construction" even without exact token match).

---

## 3. Relationship Types

| Relationship | Count | High-Conf % | Notes |
|--------------|-------|-------------|-------|
| semantically_similar | 1,085 | 90.4% | TF-IDF embedding matches |
| produces | 802 | 82.8% | Contractor → Work result |
| uses | 358 | 80.7% | Contractor → Product |
| coordinates | 204 | 78.9% | Builder → Building type |
| manages | 123 | 95.1% | Entity → Construction site |
| performs | 184 | 48.9% | Needs refinement |

---

## 4. Testable Hypotheses

### H1: Specific trades map better than generic trades
**Test:** Compare mapping quality for codes ending in 0 (general) vs specific digits.
**Prediction:** Specific codes (23813, 238210) outperform general (2381, 23810).
**Validation:** Calculate average confidence by code specificity level.

### H2: Embedding over-matches on construction domain terms
**Test:** Check if embedding gives high scores to unrelated Uniclass codes that contain "construction".
**Prediction:** Some false positives where only shared term is "construction/building".
**Validation:** Manual review of embedding-only A-confidence matches.

### H3: UK/US terminology gap causes systematic misses
**Test:** Check for common US terms missing UK equivalents (siding, drywall, HVAC).
**Prediction:** These terms have lower coverage than UK-aligned terms.
**Validation:** Compile US-specific vocabulary and measure match rates.

### H4: Uniclass Ss (Systems) maps better than Pr (Products)
**Test:** Compare coverage between Ss and Pr tables.
**Prediction:** Ss has higher match quality (more abstract = more matches).
**Validation:** Compare confidence distributions.

### H5: Hierarchical inheritance improves coverage without hurting quality
**Test:** Compare quality of direct matches vs propagated matches.
**Prediction:** Propagated matches have slightly lower but acceptable quality.
**Validation:** Sample audit of propagated mappings.

---

## 5. Validation Framework

### 5.1 Ground Truth Set (Tier 1)

**250 mappings where both methods agree with A or B confidence.**

Suggested validation process:
1. Export to CSV for manual review
2. Domain expert validates each mapping
3. Calculate precision: correct / reviewed
4. Target: >90% precision

### 5.2 High-Confidence Singles (Tier 2)

**Mappings with A confidence from one method only.**

Suggested validation:
1. Sample 50 from each method
2. Expert review
3. Identify systematic errors

### 5.3 Conflict Resolution (Tier 3)

**124 mappings where methods disagree by 2+ confidence levels.**

Suggested process:
1. Present both interpretations to expert
2. Record which method was correct
3. Adjust method weights accordingly

### 5.4 Gap Filling (Tier 4)

**NAICS codes with no high-confidence mappings:**
- 23817 (Siding Contractors)
- 23829 (Other Building Equipment)
- 23891 (Site Preparation)
- 23899 (All Other Specialty Trade)

Suggested process:
1. Manual expert mapping
2. Document reasoning
3. Consider if Uniclass needs extension

---

## 6. Adoption Recommendations

### Phase 1: Core Adoption (Immediate)

**250 ground truth mappings** - Both methods agree, ready for production use.

Actions:
- [ ] Export to final crosswalk format
- [ ] Mark as "validated:automated"
- [ ] Integrate into CORELOT ontology

### Phase 2: Extended Adoption (After Tier 2 Validation)

**~1,500 additional high-confidence mappings** - Single method A or B.

Actions:
- [ ] Complete Tier 2 validation sample
- [ ] If precision >85%, bulk accept
- [ ] Mark as "validated:semi-automated"

### Phase 3: Gap Filling (Expert Required)

**~400 low-confidence or missing mappings** - Need expert input.

Actions:
- [ ] Prioritize by trade importance
- [ ] Schedule expert review sessions
- [ ] Document as "validated:expert"

### Phase 4: Maintenance

Actions:
- [ ] Monitor for Uniclass/NAICS updates
- [ ] Re-run pipeline on new versions
- [ ] Track mapping deprecations

---

## 7. Recommendations for CORELOT Ontology

### 7.1 Grouping Strategy

Based on analysis, recommend organizing by:

1. **Primary Trade Category** (NAICS 4-digit)
   - 2361: Residential Building
   - 2362: Nonresidential Building
   - 2381: Foundation/Structure/Exterior
   - 2382: Building Equipment
   - 2383: Building Finishing

2. **Work Result Type** (Uniclass Ss groups)
   - Ss_20: Structural systems
   - Ss_25: Wall/window systems
   - Ss_30: Floor/roof systems
   - Ss_65: HVAC systems
   - Ss_70: Electrical systems

3. **Product Category** (Uniclass Pr groups)
   - Pr_20: Structural products
   - Pr_25: Cladding products
   - Pr_30: Covering products

### 7.2 Semantic Relationships

Recommend standardizing on 5 relationship types:

| Relationship | From → To | Example |
|--------------|-----------|---------|
| `produces` | Contractor → System | Framing → Structural framing systems |
| `uses` | Contractor → Product | Framing → Framing anchors |
| `performs` | Contractor → Activity | Electrical → Wiring installation |
| `operates_at` | Contractor → Entity | Construction → Construction sites |
| `coordinates` | Builder → Complex | Residential Builder → Residential properties |

### 7.3 Quality Tiers

Recommend marking each mapping with quality tier:

```json
{
  "mapping": "naics:23813 → uc:Ss_20_10_75",
  "quality_tier": 1,
  "validation": "automated",
  "methods_agreed": ["linguistic", "embedding"],
  "confidence": "A",
  "score": 0.665
}
```

---

## 8. Next Steps

1. **Immediate:** Export 250 ground truth mappings for adoption
2. **This week:** Run H1-H5 hypothesis tests
3. **This month:** Complete Tier 2 validation
4. **Ongoing:** Expert review of gaps and conflicts

---

*Generated: 2024-12-30*
*Methods: Linguistic (Jaccard), TF-IDF Embedding, Co-occurrence, Hierarchical Propagation*
*Data: NAICS 2022, Uniclass 2015 (latest)*
