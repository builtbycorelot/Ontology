# License Audit - Data Sources

**Audit Date:** 2024-12-30
**Purpose:** Verify that all data sources used in this ontology crosswalk are truly open source, non-proprietary, and legally usable.

---

## Summary

| Source | License | Derivatives OK? | Commercial OK? | Status |
|--------|---------|-----------------|----------------|--------|
| **NAICS 2022** | Public Domain | Yes | Yes | VERIFIED OPEN |
| **Wikidata** | CC0 1.0 | Yes | Yes | VERIFIED OPEN |
| **O*NET** | CC BY 4.0 | Yes | Yes | VERIFIED OPEN |
| **Brick Schema** | BSD-3-Clause | Yes | Yes | VERIFIED OPEN |
| **WordNet** | BSD-like | Yes | Yes | VERIFIED OPEN |
| **Schema.org** | CC BY-SA 3.0 | Yes (ShareAlike) | Yes | VERIFIED OPEN |
| **DBpedia** | CC BY-SA 3.0 | Yes (ShareAlike) | Yes | VERIFIED OPEN |
| **Uniclass 2015** | CC BY-ND 4.0 | **NO** | Yes | LEGAL GRAY AREA |
| **ifcOWL/IFC** | CC BY-ND 4.0 | **NO** | Yes | LEGAL GRAY AREA |
| **ISO Standards** | Proprietary | No | Purchase Required | NOT USABLE |

---

## Tier 1: Verified Open (No Restrictions)

### NAICS 2022
- **Publisher:** U.S. Census Bureau, Statistics Canada, INEGI
- **License:** Public Domain (U.S. Government Work)
- **Legal Basis:** 17 U.S.C. Section 105 - works produced by the US federal government are not subject to copyright
- **Verification:** [Census Bureau NAICS](https://www.census.gov/naics/)
- **Status:** FREE TO USE - No restrictions

### Wikidata
- **Publisher:** Wikimedia Foundation
- **License:** Creative Commons CC0 1.0 Universal (Public Domain Dedication)
- **Verification:** [Wikidata:Licensing](https://www.wikidata.org/wiki/Wikidata:Licensing)
- **Key Terms:** "You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission."
- **Status:** FREE TO USE - No restrictions

### O*NET Database
- **Publisher:** U.S. Department of Labor, Employment and Training Administration
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Verification:** [O*NET License](https://www.onetcenter.org/license_db.html)
- **Attribution Required:** "O*NET 30.1 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license."
- **Note:** Some external data on O*NET OnLine may have different licenses
- **Status:** FREE TO USE - Attribution required

### Brick Schema
- **Publisher:** Brick Consortium, Inc.
- **License:** BSD 3-Clause "New" or "Revised" License
- **Verification:** [GitHub License](https://github.com/BrickSchema/Brick/blob/master/LICENSE)
- **Key Terms:** Free for commercial use, modifications allowed, must retain copyright notice
- **Status:** FREE TO USE - Attribution required

### Princeton WordNet
- **Publisher:** Princeton University
- **License:** WordNet License (BSD-style)
- **Verification:** [WordNet License](https://wordnet.princeton.edu/license-and-commercial-use)
- **Key Terms:** Free for commercial use with attribution
- **Status:** FREE TO USE - Attribution required

---

## Tier 2: Verified Open (ShareAlike Required)

### Schema.org
- **Publisher:** Schema.org Community Group (Google, Microsoft, Yahoo, Yandex)
- **License:** Creative Commons Attribution-ShareAlike 3.0 (CC BY-SA 3.0)
- **Verification:** [Schema.org Terms](https://schema.org/docs/terms.html)
- **Key Terms:** Derivatives must be shared under same or compatible license
- **Implication:** Any crosswalk incorporating Schema.org terms must be CC BY-SA
- **Status:** USABLE - ShareAlike condition applies to output

### DBpedia
- **Publisher:** DBpedia Association
- **License:** Creative Commons Attribution-ShareAlike 3.0 (CC BY-SA 3.0)
- **Verification:** [DBpedia About](https://www.dbpedia.org/about/)
- **Key Terms:** Same as Schema.org - ShareAlike required
- **Status:** USABLE - ShareAlike condition applies to output

---

## Tier 3: Legal Gray Area (NoDerivatives Clause)

### Uniclass 2015
- **Publisher:** NBS (National Building Specification), RIBA Enterprises Ltd.
- **License:** Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)
- **Verification:** [NBS Uniclass](https://www.thenbs.com/our-tools/uniclass)
- **Key Terms:**
  - "You cannot modify, transform, or create derivative works from the tables"
  - "You must use the tables as-is without creating your own adaptations"
  - Commercial use IS allowed
  - Attribution required

#### Legal Analysis for Crosswalk Use

The CC BY-ND 4.0 license prohibits "Adapted Material" defined as:
> "Material that is derived from or based upon the Licensed Material and in which the Licensed Material is translated, altered, arranged, transformed, or otherwise modified"

**Question:** Is a crosswalk mapping a "derivative work"?

**Arguments that crosswalk IS allowed:**
1. A crosswalk references codes, does not modify them
2. CC licenses distinguish "Collections" from "Adaptations" - a collection of unchanged works is NOT a derivative
3. We are not altering Uniclass codes or descriptions
4. We are creating relationships between independent classification systems

**Arguments that crosswalk may NOT be allowed:**
1. "Arranged" could include creating new structural relationships
2. NBS explicitly states "users should not adapt the tables"
3. A semantic mapping could be considered a transformation

**Recommendation:**
- Reference Uniclass codes only (e.g., "Ss_70")
- Do not reproduce full descriptions in outputs
- Mark Uniclass-related mappings as requiring independent verification
- Consider contacting NBS for clarification if distributing commercially

### ifcOWL / IFC
- **Publisher:** buildingSMART International Limited
- **License:** Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)
- **Verification:** [buildingSMART Technical](https://technical.buildingsmart.org/standards/ifc/)
- **Copyright:** "Copyright 1996-2024 buildingSMART International Limited"
- **Key Terms:** Same restrictions as Uniclass - no derivative works
- **Status:** Same legal gray area as Uniclass

---

## Tier 4: Proprietary / Not Usable

### ISO Standards
- **Publisher:** International Organization for Standardization
- **Examples:** ISO 19650, ISO 16739-1:2024
- **License:** Proprietary - purchase required
- **Cost:** Typically CHF 150-300 per standard
- **Key Terms:** Cannot reproduce, distribute, or create derivatives without license

**Important Clarification:**
- While IFC is registered as ISO 16739, the **content** is owned by buildingSMART under CC BY-ND
- The ISO registration is for standards recognition, not licensing
- The buildingSMART-published versions (ifcOWL) are the usable open versions
- Do NOT cite ISO standard numbers in data outputs - cite buildingSMART sources

### Other Potentially Proprietary Standards
- **MasterFormat** - CSI (Construction Specifications Institute) - Proprietary
- **OmniClass** - CSI/CSC - Partially proprietary (some tables free, others licensed)
- **RICS Standards** - Royal Institution of Chartered Surveyors - Proprietary

---

## Compliance Actions Taken

### What We Use
1. **NAICS codes** - Public domain, no restrictions
2. **Wikidata** - CC0 for UK/US synonyms, no restrictions
3. **O*NET** - CC BY 4.0 for occupation data, attribution included
4. **Brick Schema** - BSD-3 for HVAC/electrical concepts, attribution in code
5. **WordNet** - BSD-style for synonym expansion, attribution in code
6. **Schema.org** - CC BY-SA for business types, ShareAlike on outputs

### What We Reference (Legal Gray Area)
1. **Uniclass codes** - Referenced by code only, not descriptions modified
2. **ifcOWL concepts** - Referenced for compatibility, not adapted

### What We Do NOT Use
1. **ISO standard text** - Not reproduced
2. **MasterFormat** - Not included
3. **Any proprietary classification** - Excluded

---

## Output Licensing

Given the ShareAlike requirements from Schema.org and DBpedia, this crosswalk is released under:

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

This is compatible with:
- CC0 (can be incorporated)
- CC BY (can be incorporated with attribution)
- CC BY-SA 3.0 (forward-compatible)
- BSD licenses (can be incorporated)
- Public domain (can be incorporated)

---

## Verification Sources

1. [Wikidata Licensing](https://www.wikidata.org/wiki/Wikidata:Licensing) - CC0 verified
2. [O*NET License](https://www.onetcenter.org/license_db.html) - CC BY 4.0 verified
3. [Brick Schema GitHub](https://github.com/BrickSchema/Brick/blob/master/LICENSE) - BSD-3 verified
4. [Schema.org Terms](https://schema.org/docs/terms.html) - CC BY-SA 3.0 verified
5. [NBS Uniclass](https://uniclass.thenbs.com/download) - CC BY-ND 4.0 noted
6. [buildingSMART IFC](https://technical.buildingsmart.org/standards/ifc/) - CC BY-ND 4.0 noted
7. [Creative Commons ND Definition](https://creativecommons.org/licenses/by-nd/4.0/deed.en) - NoDerivatives terms reviewed

---

## Recommendations

1. **Safe to proceed** with NAICS, Wikidata, O*NET, Brick, WordNet, Schema.org, DBpedia
2. **Use caution** with Uniclass and IFC - reference codes only, do not modify or adapt
3. **Avoid** ISO standard text, MasterFormat, and other proprietary sources
4. **License output** as CC BY-SA 4.0 to comply with ShareAlike requirements
5. **Consider** contacting NBS for written clarification on crosswalk use if pursuing commercial distribution

---

*Audit conducted: 2024-12-30*
*Auditor: Automated license review with manual verification*
