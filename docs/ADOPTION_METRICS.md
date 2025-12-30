# Ontology Adoption Metrics & Value Proposition

## Why This Standard Will Be Adopted

### Problem Statement
Construction projects involve multiple parties using different classification systems:
- **US Contractors** use NAICS codes for business classification
- **UK/International Projects** use Uniclass for work breakdown
- **Software Systems** use Schema.org for business entities
- **Accounting** uses UBL for invoicing

**Result**: No interoperability. A US electrical contractor (NAICS 238210) can't easily find their equivalent Uniclass work results (Ss_70 Electrical systems).

### Solution
A validated crosswalk that maps between standards, enabling:
1. **Instant Classification** - Know what Uniclass codes apply to your NAICS trade
2. **Project Staffing** - Match contractors to work packages by capability
3. **Procurement** - Link trades to products they typically use
4. **International Bidding** - US contractors can bid on UK projects with correct classifications

---

## Top-Line Metrics

### Coverage Metrics

| Metric | Current | Target | Notes |
|--------|---------|--------|-------|
| **NAICS Sector 23 Coverage** | 72/90 codes (80%) | 90/90 (100%) | Construction trades |
| **Uniclass Ss Mapped** | 255/2,415 (10.6%) | 500+ (20%) | Focus on construction-relevant |
| **Uniclass Pr Mapped** | 258/7,891 (3.3%) | 1,000+ (12%) | Products used by trades |
| **Ground Truth Mappings** | 250 | 500+ | Both methods agree A/B |
| **Total Validated Mappings** | 976 | 2,000+ | Tier 1 + Tier 2 |

### Quality Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Precision (Tier 1)** | TBD | >95% | Expert validation sample |
| **Precision (Tier 2)** | TBD | >85% | Spot-check sample |
| **Method Agreement** | 250/2,361 (10.6%) | 30%+ | Both linguistic + embedding |
| **High-Confidence %** | 81.8% | 85%+ | A or B confidence |
| **Avg Jaccard Score** | 0.396 | 0.45+ | Token overlap quality |

### Validation Metrics

| Test | Result | Implication |
|------|--------|-------------|
| **H1: Specificity** | SUPPORTED | 6-digit codes map better than 4-digit |
| **H2: Embedding Valid** | NOT OVERFITTING | Semantic matches are real |
| **H3: UK/US Gap** | SUPPORTED (18%) | Need synonym expansion |
| **H4: Ss > Pr** | SUPPORTED | Systems map better than products |

---

## Adoption Drivers

### 1. Cost Savings
- **Manual Classification**: ~5 min per contractor to find Uniclass codes
- **With Crosswalk**: Instant lookup
- **At Scale**: 10,000 contractors × 5 min = 833 hours saved

### 2. Bid Accuracy
- Correct Uniclass classification → proper scope definition
- Reduces change orders from misclassification
- **Industry average**: 10% of project cost from scope changes

### 3. Compliance
- UK BIM Level 2 requires Uniclass classification
- US contractors bidding internationally need translation
- **ISO 19650** references classification standards

### 4. Software Integration
- ERP systems can auto-populate classifications
- Procurement platforms can match suppliers to requirements
- **API-ready** JSON-LD format

---

## Validation Chain Examples

### Electrical Contractors → Electrical Systems ✓
```
NAICS 238210 (Electrical Contractors)
  ↓ produces
Uniclass Ss_70 (Electrical systems)
  ↓ uses
Uniclass Pr_65 (Electrical products)
```
**Confidence**: A (0.5+) | **Methods**: Linguistic + Embedding agree

### Tile Contractors → Tiling Systems ✓
```
NAICS 238340 (Tile and Terrazzo Contractors)
  ↓ produces
Uniclass Ss_25_45_88 (Tiling systems)
  ↓ uses
Uniclass Pr_25_75 (Tiles)
```
**Confidence**: A | **Methods**: Both agree

### Siding Contractors → ??? (Gap)
```
NAICS 238170 (Siding Contractors)
  ↓ produces
Uniclass Ss_25_20 (Cladding systems)  ← NEEDS SYNONYM
```
**Issue**: "Siding" is US term, Uniclass uses "Cladding"
**Solution**: UK/US synonym mapping added

---

## Data Sources (All Non-Proprietary)

| Source | License | Use |
|--------|---------|-----|
| **NAICS 2022** | Public Domain (US Gov) | Trade classifications |
| **Uniclass 2015** | Free to use (NBS) | Work results, products |
| **Schema.org** | CC0 | Business entity types |
| **Wikidata** | CC0 | UK/US synonyms, aliases |
| **DBpedia** | CC-BY-SA | Construction concepts |
| **Princeton WordNet** | Open license | Synonym expansion |

---

## Measurement Framework

### Phase 1: Accuracy Validation (Current)
- [ ] Sample 50 Tier 1 mappings → expert review
- [ ] Calculate precision (target: >95%)
- [ ] Sample 50 Tier 2 mappings → expert review
- [ ] Calculate precision (target: >85%)

### Phase 2: Coverage Expansion
- [ ] Add UK/US synonyms to matching algorithm
- [ ] Re-run pipeline with expanded vocabulary
- [ ] Target: 20%+ improvement in US term coverage

### Phase 3: User Validation
- [ ] Deploy lookup tool for contractors
- [ ] Track usage metrics:
  - Queries per day
  - Mapping acceptance rate
  - User corrections submitted
- [ ] Iterate based on feedback

### Phase 4: Integration Metrics
- [ ] API calls per month
- [ ] Systems integrated
- [ ] Projects using crosswalk

---

## Success Criteria

### Minimum Viable (Launch)
- 250 ground truth mappings validated
- 80%+ NAICS Sector 23 coverage
- Precision >90% on sample

### Target (6 months)
- 1,000+ validated mappings
- 20%+ Uniclass coverage
- 3+ software integrations
- UK/US synonym coverage complete

### Stretch (12 months)
- Full NAICS-Uniclass crosswalk
- Bidirectional (Uniclass → NAICS)
- Additional standard integrations (OmniClass, MasterFormat)
- Industry adoption by >10 organizations

---

## References & Citations

### Primary Data Sources

1. **NAICS 2022** - North American Industry Classification System
   - Publisher: U.S. Census Bureau, Statistics Canada, INEGI
   - License: Public Domain (U.S. Government Work)
   - URL: https://www.census.gov/naics/
   - Citation: U.S. Census Bureau. (2022). *North American Industry Classification System*. Washington, DC.

2. **Uniclass 2015** - Unified Classification for the Construction Industry
   - Publisher: NBS (National Building Specification), UK
   - License: Free to use with attribution
   - URL: https://www.thenbs.com/our-tools/uniclass-2015
   - Citation: NBS. (2015). *Uniclass 2015*. Newcastle upon Tyne: RIBA Enterprises Ltd.

3. **Schema.org**
   - Publisher: Schema.org Community Group (Google, Microsoft, Yahoo, Yandex)
   - License: Creative Commons Attribution-ShareAlike 3.0 (CC BY-SA 3.0)
   - URL: https://schema.org/
   - Citation: Schema.org. (2024). *Schema.org Vocabulary*. Retrieved from https://schema.org/

4. **Wikidata**
   - Publisher: Wikimedia Foundation
   - License: Creative Commons CC0 1.0 Universal (Public Domain Dedication)
   - URL: https://www.wikidata.org/
   - Citation: Wikidata contributors. (2024). *Wikidata*. Retrieved from https://www.wikidata.org/
   - License Reference: https://www.wikidata.org/wiki/Wikidata:Licensing

5. **DBpedia**
   - Publisher: DBpedia Association
   - License: Creative Commons Attribution-ShareAlike 3.0 (CC BY-SA 3.0)
   - URL: https://www.dbpedia.org/
   - Citation: Auer, S., et al. (2007). DBpedia: A Nucleus for a Web of Open Data. *ISWC 2007*.

6. **Princeton WordNet**
   - Publisher: Princeton University
   - License: WordNet License (BSD-like, free for commercial use)
   - URL: https://wordnet.princeton.edu/
   - Citation: Miller, G. A. (1995). WordNet: A Lexical Database for English. *Communications of the ACM*, 38(11), 39-41.

### Methodology References

7. **Jaccard Similarity**
   - Citation: Jaccard, P. (1912). The distribution of the flora in the alpine zone. *New Phytologist*, 11(2), 37-50.

8. **TF-IDF Weighting**
   - Citation: Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management*, 24(5), 513-523.

### Standards References

9. **ISO 19650** - Organization and digitization of information about buildings and civil engineering works
   - Publisher: International Organization for Standardization
   - Citation: ISO. (2018). *ISO 19650-1:2018 - Organization and digitization of information about buildings and civil engineering works*.

10. **UK BIM Framework**
    - Publisher: UK BIM Alliance
    - URL: https://www.ukbimframework.org/
    - Citation: UK BIM Alliance. (2019). *Information Management according to BS EN ISO 19650*.

---

*Document Generated: 2024-12-30*
*Repository: https://github.com/builtbycorelot/Ontology*
*License: This crosswalk documentation is released under CC BY 4.0*
