# Crosswalk Derivation Log

Scientific reproducibility requires documenting the exact process used to derive mappings.

---

## Source Data Versions

| Standard | Source Repo | Commit/Version | Files Used |
|----------|-------------|----------------|------------|
| NAICS | leereilly/csi | submodule HEAD | `lib/data/naics/*.toml`, `lib/data/naics/naics-lookup.csv` |
| Uniclass 2015 | buildig/uniclass-2015 | submodule HEAD | `uniclass2015/Uniclass2015_*.csv` |

---

## Files Processed

### NAICS Sector 23 - Construction

Total NAICS construction codes processed: 23 (6-digit national industry level)

| Subsector | Codes Processed | Mappings Created |
|-----------|-----------------|------------------|
| 236 - Construction of Buildings | 6 codes | 16 mappings |
| 237 - Heavy and Civil Engineering | 6 codes | 23 mappings |
| 238 - Specialty Trade Contractors | 18 codes | 51 mappings |

### Uniclass Tables Referenced

| Table | Code Prefix | Purpose |
|-------|-------------|---------|
| Ss (Systems) | `Ss_*` | Work results - what is produced |
| Pr (Products) | `Pr_*` | Materials used |
| Ac (Activities) | `Ac_*` | Construction processes |
| En (Entities) | `En_*` | Building types (for 236 GCs) |
| Co (Complexes) | `Co_*` | Site/complex types (for 236/237) |

---

## Derivation Rules Applied

### Rule 1: Trade Name → Work Domain Mapping

```
Input: NAICS trade name (e.g., "Framing Contractors")
Process:
  1. Extract core work noun: "Framing" → "frame"
  2. Identify construction domain: structural, enclosure, MEP, finish
  3. Map to Uniclass group: Ss_25 (Wall/barrier systems)
  4. Refine to specific system: Ss_25_10_30 (Timber frame wall)
Output: NAICS code → Uniclass code with relationship type
```

### Rule 2: Relationship Type Classification

| Relationship | Applied When | NAICS Type | Uniclass Type |
|--------------|--------------|------------|---------------|
| `produces` | Trade's primary deliverable | 238 (trades) | Ss (systems) |
| `uses` | Materials consumed | 238 (trades) | Pr (products) |
| `performs` | Activity type | 236, 238 | Ac (activities) |
| `manages` | Project oversight | 236 (GCs) | En, Co (entities) |

### Rule 3: Confidence Level Assignment

| Level | Criteria |
|-------|----------|
| A (Definitive) | Direct linguistic match, industry standard practice |
| B (Strong) | Common practice, implied by trade scope |
| C (Moderate) | Sometimes applicable, secondary scope |
| D (Weak) | Edge case, uncommon |

---

## Derivation Examples

### Example 1: NAICS 238130 → Uniclass Ss_25_10_30

**Input:**
```toml
# sources/naics/lib/data/naics/238130.toml
code = "238130"
name = "Framing Contractors"
sic_correlations = ["1751"]
```

**Derivation chain:**
1. Trade name: "Framing Contractors"
2. Core noun: "Framing" (verb → noun: frame assembly)
3. Material inference: US residential = timber (SIC 1751 = "Carpentry Work")
4. Uniclass search: "frame" in Ss table
5. Match: `Ss_25_10_30` = "Timber frame wall structure systems"
6. Confidence: A (definitive - trade name directly maps)

**Output:**
```csv
238130,Framing Contractors,produces,Ss_25_10_30,Ss,Timber frame wall structure systems,1:N,A,Primary work output
```

### Example 2: NAICS 237310 → Uniclass Ss_20_50

**Input:**
```toml
# sources/naics/lib/data/naics/237310.toml
code = "237310"
name = "Highway, Street, and Bridge Construction"
sic_correlations = ["1622", "1611", "8741", "1721"]
```

**Derivation chain:**
1. Trade name: "Highway, Street, and Bridge Construction"
2. Core nouns: "Highway", "Street", "Bridge"
3. Uniclass search: "road" → Ss_30_14, "bridge" → Ss_20_50
4. Multiple matches for compound scope
5. Confidence: A (each noun directly maps)

**Output:**
```csv
237310,Highway Street and Bridge Construction,produces,Ss_30_14,Ss,Road and paving systems,1:N,A,Road construction
237310,Highway Street and Bridge Construction,produces,Ss_20_50,Ss,Bridge structure systems,1:N,A,Bridge construction
```

### Example 3: NAICS 236220 → Uniclass En_20 (GC to Entity)

**Input:**
```toml
# sources/naics/lib/data/naics/236220.toml
code = "236220"
name = "Commercial and Institutional Building Construction"
sic_correlations = ["1541", "1542", "1522", "8741", "1531", "1799"]
```

**Derivation chain:**
1. Trade name: "Commercial and Institutional Building Construction"
2. Role type: General Contractor (236 subsector = building construction)
3. Relationship: `manages` (GCs coordinate, not directly produce)
4. Building types: Commercial → En_20, Institutional → En_25
5. Confidence: A (industry standard practice)

**Output:**
```csv
236220,Commercial and Institutional Building Construction,manages,En_20,En,Administrative commercial and protective entities,1:N,A,Commercial buildings
236220,Commercial and Institutional Building Construction,manages,En_25,En,Cultural educational scientific entities,1:N,A,Institutional buildings
```

---

## Audit Trail

| Date | Action | Lines Added | Reviewer |
|------|--------|-------------|----------|
| 2025-12-30 | Initial 238 mappings | 48 | Claude/Human |
| 2025-12-30 | Add 236 (Buildings) | 16 | Claude |
| 2025-12-30 | Add 237 (Heavy/Civil) | 23 | Claude |
| 2025-12-30 | Add missing 238 codes | 4 | Claude |

---

## Verification Checklist

- [x] Every 6-digit NAICS in sector 23 has at least one mapping
- [x] All mappings use valid Uniclass codes from source CSV
- [x] Relationship types follow methodology rules
- [x] Confidence levels documented with rationale
- [ ] Peer review of linguistic derivations
- [ ] Cross-validate with industry specifications

---

## How to Reproduce

```bash
# 1. Clone the Ontology repo with submodules
git clone --recurse-submodules https://github.com/[org]/Ontology.git

# 2. Verify source data versions
git -C sources/naics log -1 --oneline
git -C sources/uniclass log -1 --oneline

# 3. Extract NAICS construction codes (sector 23)
ls sources/naics/lib/data/naics/23*.toml

# 4. Extract Uniclass Systems table
head sources/uniclass/uniclass2015/Uniclass2015_Ss.csv

# 5. Apply derivation rules per CROSSWALK_METHODOLOGY.md
# Result should match crosswalk/naics-to-uniclass.csv
```

---

*This log enables independent verification that all mappings are derived from first principles using public domain and openly-licensed sources.*
