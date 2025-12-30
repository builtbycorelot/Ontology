# Knowledge Graph Expansion Roadmap

## Current State (After Final Merge)

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Tier 1 (Ground Truth)** | 250 | 472 | +88.8% |
| **Tier 2 (High)** | 726 | 773 | +6.5% |
| **Tier 3 (Medium)** | 24 | 781 | +3154% |
| **Tier 4 (Low - needs work)** | 1,361 | 335 | -75.4% |

---

## Expansion Strategy 1: Deep Product Research

### Concept
Use manufacturer installation instructions to validate trade → system → product chains.

### Data Sources (All Open/Public)

| Source | URL | License | Value |
|--------|-----|---------|-------|
| **NBS National BIM Library** | nationalbimlibrary.com | Free to use | BIM objects with Uniclass codes |
| **Open Product Data** | openproductdata.org | CC0 | Product classifications |
| **Manufacturer PDFs** | Various | Public | Install instructions |
| **GitHub BIM repos** | github.com/topics/ifc | Various open | IFC models with codes |

### Implementation

```python
# Example: Parse manufacturer install instructions
def extract_trade_system_from_install_guide(pdf_text):
    """
    Look for patterns like:
    - "installed by [trade]"
    - "part of [system] works"
    - "Uniclass code: Ss_xx_xx"
    """
    trade_patterns = [
        r"installed by (\w+ contractors?)",
        r"(\w+) trade",
        r"requires (\w+) certification"
    ]
    system_patterns = [
        r"Uniclass[:\s]+([A-Za-z]{2}_[\d_]+)",
        r"part of (\w+ system)",
        r"(\w+ works) package"
    ]
    # Extract and validate...
```

### Expected Yield
- Target: Resolve 200+ Tier 4 mappings
- Method: Cross-reference product specs with our mappings

---

## Expansion Strategy 2: International Standards

### Verified Open Standards

| Standard | Country | License | Download |
|----------|---------|---------|----------|
| **CCI** | International | **CC BY 4.0** | [cci-collaboration.org](https://cci-collaboration.org/the-standard/) |
| **ESCO** | EU (28 languages) | Open Data | [esco.ec.europa.eu](https://esco.ec.europa.eu/en/use-esco/download) |
| **O*NET** | USA | CC BY 4.0 | [onetcenter.org](https://www.onetcenter.org/database.html) |
| **Wikidata** | Global | CC0 | [wikidata.org](https://www.wikidata.org/) |

### Partially Open / Reference Only

| Standard | Country | License | Notes |
|----------|---------|---------|-------|
| **Uniclass** | UK | CC BY-ND 4.0 | Reference codes only |
| **IFC/ifcOWL** | International | CC BY-ND 4.0 | Reference, no derivatives |
| **OmniClass** | USA/Canada | CSI Copyright | Tables free, licensing required for commercial |
| **CoClass** | Sweden | Unknown | Check with Swedish authorities |
| **CCS** | Denmark | Unknown | Check with Danish authorities |

### Multilingual Expansion via ESCO

ESCO provides **3,039 occupations** in **28 languages**:
- All EU official languages
- Plus: Icelandic, Norwegian, Ukrainian, Arabic

**Construction occupations available in:**
- English, German, French, Spanish, Italian, Polish, Dutch
- Portuguese, Swedish, Danish, Finnish, Czech, etc.

```
Example ESCO mapping:
EN: "Electrician" (ESCO occupation)
DE: "Elektriker"
FR: "Électricien"
ES: "Electricista"
→ All map to ISCO-08: 7411
→ Which maps to: NAICS 238210, Uniclass Ss_70
```

### CCI Integration Path

CCI (Construction Classification International) uses ISO 81346 structure:
- **Free download** at cci-collaboration.org
- **CC BY 4.0 license** - derivatives allowed
- Countries using CCI: Czechia, Slovakia, Poland, Estonia, Lithuania

```
CCI Table Structure:
- Construction complexes
- Building entities
- Built spaces
- Functional systems (→ maps to Uniclass Ss)
- Technical systems
- Components (→ maps to Uniclass Pr)
```

---

## Expansion Strategy 3: Low-Confidence Node Resolution

### Current Tier 4 Analysis

335 mappings need validation. Common patterns:

1. **Terminology mismatch** (UK vs US)
   - Example: "Siding" has no direct Uniclass match
   - Solution: UK/US synonym expansion (already done)

2. **Granularity mismatch**
   - Example: NAICS 238990 "All Other Specialty Trade"
   - Solution: Break into sub-categories via O*NET tasks

3. **Missing intermediate links**
   - Example: "Low Voltage Contractor" → ???
   - Solution: Product research (what do they install?)

4. **Ambiguous mappings**
   - Example: "General Contractor" → multiple systems
   - Solution: Expert validation or exclude

### Resolution Approaches

| Approach | Effort | Yield | Priority |
|----------|--------|-------|----------|
| Product install guides | Medium | High | 1 |
| ESCO occupation mapping | Low | Medium | 2 |
| CCI alignment | Medium | Medium | 3 |
| Expert validation batch | High | High | 4 |
| Document mining | High | Variable | 5 |

---

## Expansion Strategy 4: Relationship Enrichment

### Current Relationships
- `produces` (trade → system)
- `uses` (trade → product)
- `semantically_similar`

### Additional Relationships to Add

| Relationship | Example | Source |
|--------------|---------|--------|
| `requires_certification` | Electrician → electrical license | O*NET |
| `typical_tools` | Plumber → pipe wrench | O*NET Tools Used |
| `related_occupation` | HVAC Tech ↔ Refrigeration Tech | ESCO |
| `subcontracted_by` | General → Electrical | Industry knowledge |
| `co_occurs_with` | Drywall → Painting (sequence) | Project data |
| `supersedes` | Old code → New code | Classification updates |

### Skills/Tasks Integration (from O*NET)

```
NAICS 238210 (Electrical Contractors)
  → employs SOC 47-2111 (Electricians)
    → performs tasks:
      - "Install electrical wiring, equipment, fixtures"
      - "Test electrical systems for continuity"
      - "Plan layout of electrical wiring"
    → requires skills:
      - Troubleshooting
      - Equipment maintenance
      - Quality control analysis
```

---

## Uniclass Licensing Clarification

### Status: CC BY-ND 4.0 (NoDerivatives)

**What we CAN do:**
- Reference Uniclass codes (e.g., "Ss_70")
- Create mappings that point TO Uniclass codes
- Build lookup tools that return Uniclass codes

**What we CANNOT do:**
- Modify Uniclass descriptions
- Create "adapted" versions of Uniclass tables
- Redistribute modified Uniclass content

**Our Approach:**
- Store NAICS data (public domain) as primary
- Store crosswalk relationships (our creation, CC BY-SA)
- Reference Uniclass codes by ID only
- Link to official NBS URLs for descriptions

**Legal Position:**
A crosswalk is arguably a "collection" (allowed) not an "adaptation" (restricted), because:
1. We don't modify Uniclass content
2. We create independent relationship data
3. Uniclass codes are referenced, not reproduced

**Recommendation:** For commercial use, seek written clarification from NBS.

---

## Implementation Priority

### Phase 1: Quick Wins (1-2 weeks)
- [x] O*NET task integration
- [x] BLS matrix bridge
- [x] Brick Schema alignment
- [x] UK/US synonyms
- [ ] ESCO occupation download
- [ ] CCI table download

### Phase 2: Product Research (2-4 weeks)
- [ ] NBS BIM Library scraping (for Uniclass codes)
- [ ] Manufacturer PDF parsing
- [ ] Product-to-system validation

### Phase 3: International (4-8 weeks)
- [ ] CCI ↔ Uniclass alignment
- [ ] ESCO multilingual labels
- [ ] European market expansion

### Phase 4: Advanced (ongoing)
- [ ] Skills/tasks ontology
- [ ] Project sequence modeling
- [ ] Real-time validation API

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Tier 1 mappings | 472 | 800+ |
| Tier 4 (unresolved) | 335 | <100 |
| Languages supported | 1 (EN) | 5+ |
| Standards integrated | 4 | 8+ |
| Product validations | 0 | 500+ |

---

*Document Created: 2024-12-30*
*License: CC BY-SA 4.0*
