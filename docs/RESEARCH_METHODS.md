# Research Methods for Confidence Enhancement

## Verified Open Sources Available

| Source | License | Data Available | Integration Value |
|--------|---------|----------------|-------------------|
| **O*NET** | CC BY 4.0 | 1,000+ occupations, skills, tasks, tools | HIGH - Maps trades to skills/tasks |
| **Brick Schema** | BSD-3 | 800+ HVAC/electrical/lighting classes | HIGH - System-level ontology |
| **Wikidata** | CC0 | 100M+ entities, Q-codes, relationships | MEDIUM - Entity linking, synonyms |
| **WordNet** | BSD | 117,000 synonym sets | MEDIUM - Term expansion |
| **DBpedia** | CC BY-SA | Structured Wikipedia | MEDIUM - Definitions, relationships |

---

## Method 1: O*NET Occupation Bridge

**Concept:** NAICS trades map to O*NET occupations, which have skills/tasks that align with Uniclass systems.

```
NAICS 238210 (Electrical Contractors)
    ↓ employs
O*NET 47-2111.00 (Electricians)
    ↓ performs tasks like
"Install electrical wiring, equipment, fixtures"
    ↓ validates mapping to
Uniclass Ss_70 (Electrical systems)
```

**Data Flow:**
1. Download O*NET-SOC crosswalk (NAICS → SOC → O*NET)
2. For each NAICS trade, find O*NET occupations
3. Extract task descriptions from O*NET
4. Match task keywords to Uniclass system names
5. Confidence boost when tasks align with systems

**Expected Yield:** +15-25% confidence boost on trade-to-system mappings

**API/Data:**
- https://www.onetcenter.org/database.html (bulk download)
- https://services.onetcenter.org/ (API)

---

## Method 2: Brick Schema Alignment

**Concept:** Brick has a detailed ontology for building systems (especially MEP). Align Uniclass systems with Brick classes.

```
Uniclass Ss_70 (Electrical systems)
    ↔ aligns with
Brick:Electrical_System
    ↔ has subclasses
Brick:Lighting_System, Brick:Power_System
    ↔ validates granular mappings
```

**Data Flow:**
1. Load Brick ontology (Turtle/RDF format)
2. Extract system classes (brick:System subclasses)
3. Match to Uniclass Ss codes by label similarity
4. Use Brick hierarchy to validate Uniclass hierarchy
5. Identify gaps where Brick has detail Uniclass lacks

**Expected Yield:** Strong validation for MEP trades (HVAC, Electrical, Plumbing)

**Files:**
- https://github.com/BrickSchema/Brick/releases (Brick.ttl)

---

## Method 3: Wikidata Entity Linking

**Concept:** Link trades, systems, and products to Wikidata Q-codes for additional relationships.

```
"Electrician"
    → Q168816 (Wikidata)
    → has occupation field: Q844569 (electrical engineering)
    → related to: Q12760 (electrical wiring)
    → validates connection to electrical systems
```

**Data Flow:**
1. Query Wikidata SPARQL for construction occupations
2. Get P31 (instance of), P279 (subclass of), P425 (field of work)
3. Find relationships between occupations and systems/products
4. Use wdt:P1566 for geographic variants (US/UK terms)

**SPARQL Examples:**
```sparql
# Find all construction occupations
SELECT ?occupation ?label WHERE {
  ?occupation wdt:P31 wd:Q28640;  # instance of profession
              wdt:P425 wd:Q385378. # field: construction
  ?occupation rdfs:label ?label.
  FILTER(LANG(?label) = "en")
}

# Find UK/US term variants
SELECT ?item ?usLabel ?ukLabel WHERE {
  ?item wdt:P31 wd:Q28640.
  ?item rdfs:label ?usLabel. FILTER(LANG(?usLabel) = "en-us")
  ?item rdfs:label ?ukLabel. FILTER(LANG(?ukLabel) = "en-gb")
}
```

**Expected Yield:** +10-15% coverage on UK/US synonyms, entity validation

---

## Method 4: WordNet Synonym Expansion

**Concept:** Expand matching vocabulary using WordNet synsets.

```
"siding"
    → synset: {cladding, facing, veneer}
    → improves match to "Cladding systems"
```

**Data Flow:**
1. For each NAICS term, get WordNet synsets
2. Expand search terms with synonyms
3. Re-run Jaccard matching with expanded vocabulary
4. Flag matches found only via synonyms (lower confidence)

**Implementation:**
```python
from nltk.corpus import wordnet

def expand_terms(term):
    synonyms = set()
    for syn in wordnet.synsets(term):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace('_', ' '))
    return synonyms
```

**Expected Yield:** +5-10% matches on terminology gaps

---

## Method 5: Triangulation Scoring

**Concept:** Confidence increases when multiple independent methods agree.

| Methods Agreeing | Confidence Tier |
|------------------|-----------------|
| 3+ methods | Tier 1 (Ground Truth) |
| 2 methods | Tier 2 (High Confidence) |
| 1 method only | Tier 3 (Needs Validation) |
| Methods conflict | Tier 4 (Review Required) |

**Current Methods:**
1. Linguistic (Jaccard)
2. Embedding (TF-IDF cosine)
3. Hierarchy propagation
4. Co-occurrence

**New Methods to Add:**
5. O*NET task matching
6. Brick alignment
7. Wikidata entity links

**Expected Yield:** More mappings promoted to Tier 1/2

---

## Method 6: Public Document Mining

**Concept:** Find public construction documents that use both NAICS and Uniclass.

**Sources (all public domain or CC):**
- UK Government construction contracts (gov.uk)
- US federal building specs (gsa.gov)
- Open BIM projects on GitHub
- Academic papers on construction classification

**Data Flow:**
1. Search for documents containing both classification systems
2. Extract co-occurring codes
3. Weight by document authority (government > academic > other)
4. Build co-occurrence matrix

**Expected Yield:** Real-world validation of theoretical mappings

---

## Implementation Priority

| Method | Effort | Value | Priority |
|--------|--------|-------|----------|
| O*NET Bridge | Medium | High | 1 |
| Triangulation | Low | High | 2 |
| Brick Alignment | Medium | High (MEP) | 3 |
| WordNet Expansion | Low | Medium | 4 |
| Wikidata Links | Medium | Medium | 5 |
| Document Mining | High | Medium | 6 |

---

## Quick Wins (Implementable Now)

### 1. O*NET NAICS-SOC Crosswalk
```bash
# Download from O*NET
curl -O https://www.onetcenter.org/dl_files/database/db_29_3_text/NAICS_2017_2_Digit_to_SOC_2018.txt
```

### 2. Brick Ontology
```bash
# Download from GitHub
curl -O https://github.com/BrickSchema/Brick/releases/download/v1.4.0/Brick.ttl
```

### 3. WordNet via NLTK
```python
import nltk
nltk.download('wordnet')
```

### 4. Wikidata SPARQL
```
https://query.wikidata.org/
# No download needed - query live
```

---

## Expected Confidence Improvement

| Current State | After Enhancement |
|---------------|-------------------|
| Ground Truth: 250 | Ground Truth: 400+ |
| Tier 1: 250 | Tier 1: 500+ |
| Precision: 86% | Precision: 92%+ |
| NAICS Coverage: 80% | NAICS Coverage: 95%+ |

---

*Document Created: 2024-12-30*
