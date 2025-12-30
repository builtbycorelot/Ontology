# Crosswalk Methodology

## Fundamental Semantic Difference

The core insight driving this crosswalk:

| Standard | Classifies | Question Answered | Example |
|----------|-----------|-------------------|---------|
| **NAICS** | Business entity / Trade | "Who does this work?" | `238130` = Framing Contractors |
| **Uniclass** | Work result / Deliverable | "What is produced?" | `Ss_25_10_30` = Timber frame wall structure systems |

These are **orthogonal classification axes**, not synonyms. A single NAICS trade may produce multiple Uniclass work results, and a single Uniclass work result may involve multiple NAICS trades.

---

## Data Structures

### NAICS (Source: leereilly/csi)

**Format:** TOML files per code
**Location:** `sources/naics/lib/data/naics/{code}.toml`

```toml
code = "238130"
name = "Framing Contractors"
sic_correlations = ["1751"]
```

**Hierarchy:** 6-digit codes
- `23` = Sector (Construction)
- `238` = Subsector (Specialty Trade Contractors)
- `2381` = Industry Group (Foundation, Structure, Building Exterior)
- `23813` = Industry (Framing Contractors)
- `238130` = National Industry (Framing Contractors)

**Construction Sector (23):**
- `236` = Construction of Buildings
- `237` = Heavy and Civil Engineering Construction
- `238` = Specialty Trade Contractors

### Uniclass (Source: buildig/uniclass-2015)

**Format:** CSV files per table
**Location:** `sources/uniclass/uniclass2015/Uniclass2015_{Table}.csv`

```csv
Code,Group,Sub group,Section,Object,Title,NRM
Ss_25_10_30,25,10,30,,"Timber frame wall structure systems",
```

**Tables relevant to construction work:**

| Table | Prefix | Description | Use in Crosswalk |
|-------|--------|-------------|------------------|
| Ss | Systems | Building systems and assemblies | Primary - work results |
| Pr | Products | Construction products | Secondary - materials |
| Ac | Activities | Construction activities | Process mapping |
| EF | Elements/Functions | Functional elements | Design specification |
| PM | Project Management | Management activities | General conditions |

**Hierarchy:** Variable depth with alphanumeric codes
- `Ss_25` = Group (Wall and barrier systems)
- `Ss_25_10` = Sub-group (Wall structure systems)
- `Ss_25_10_30` = Section (Timber frame wall structure systems)
- `Ss_25_10_30_30` = Object (specific system)

---

## Mapping Methodology

### Step 1: Identify Semantic Relationship Type

For each NAICS-Uniclass pair, determine:

| Relationship | Symbol | Description |
|--------------|--------|-------------|
| **Produces** | `→` | Trade produces this work result |
| **Uses** | `⊃` | Trade uses this product/material |
| **Performs** | `⊢` | Trade performs this activity |
| **Manages** | `⊨` | Trade manages this function |

### Step 2: Establish Cardinality

| Cardinality | Notation | Example |
|-------------|----------|---------|
| One-to-One | `1:1` | Rare - exact equivalence |
| One-to-Many | `1:N` | Trade produces multiple systems |
| Many-to-One | `N:1` | Multiple trades produce same system |
| Many-to-Many | `M:N` | Complex relationships |

### Step 3: Document Confidence Level

| Level | Confidence | Basis |
|-------|------------|-------|
| `A` | Definitive | Industry standard practice |
| `B` | Strong | Common practice |
| `C` | Moderate | Sometimes applicable |
| `D` | Weak | Edge case only |

---

## Crosswalk CSV Format

**File:** `crosswalk/naics-to-uniclass.csv`

```csv
naics_code,naics_name,relationship,uniclass_code,uniclass_table,uniclass_title,cardinality,confidence,notes
238130,Framing Contractors,produces,Ss_25_10_30,Ss,Timber frame wall structure systems,1:N,A,Primary work output
238130,Framing Contractors,produces,Ss_25_13_30,Ss,Timber floor structure systems,1:N,A,Also performs floor framing
238130,Framing Contractors,produces,Ss_25_16_30,Ss,Timber roof structure systems,1:N,A,Also performs roof framing
238130,Framing Contractors,uses,Pr_20_93_52_89,Pr,Timber boards,1:N,A,Primary material
238210,Electrical Contractors,produces,Ss_55,Ss,Electrical power generation and distribution,1:N,A,Primary work output
238210,Electrical Contractors,produces,Ss_60,Ss,Communications and control systems,1:N,B,Secondary - low voltage
238220,Plumbing HVAC Contractors,produces,Ss_55_70,Ss,Plumbing supply systems,1:N,A,Primary - plumbing
238220,Plumbing HVAC Contractors,produces,Ss_60_40,Ss,Heating systems,1:N,A,Primary - HVAC
```

---

## Linguistic Derivation Rules

To maintain non-proprietary status, all mappings must be derivable from first principles:

### Rule 1: Trade Name → Work Domain

Extract the core work domain from the NAICS trade name:

```
"Framing Contractors" → "framing" → "frame" → "structure"
                      → Uniclass Ss_25 (Wall and barrier systems)
                      → Uniclass Ss_25_10 (Wall structure systems)
```

### Rule 2: Material Implication

Common trade materials imply product classifications:

```
"Framing" typically uses → "Timber"
                        → Uniclass Pr_20 (Structural products)
                        → Uniclass Pr_20_93 (Timber structural products)
```

### Rule 3: Activity Correlation

NAICS industry descriptions imply Uniclass activities:

```
"Install wood framing" → "Assembly"
                       → Uniclass Ac_05 (Assembling)
                       → Uniclass Ac_05_10 (Assembling structural components)
```

### Rule 4: Exclusion Mapping

NAICS definitions include "primarily engaged in" - use this to exclude:

```
"238130 - Framing Contractors"
NAICS says: "establishments primarily engaged in structural wood framing"
NOT primarily: Finish carpentry (238350), Metal framing (238120)

Therefore:
  238130 → Ss_25_10_30 (Timber frame) ✓
  238130 → Ss_25_10_27 (Metal frame) ✗
```

---

## Validation Approach

### Internal Consistency

Each mapping must satisfy:

1. **Reversibility** - If NAICS A → Uniclass X, then Uniclass X should list NAICS A as a potential producer
2. **Hierarchy preservation** - If NAICS A → Uniclass X, then NAICS A parent should → Uniclass X parent
3. **No orphans** - Every construction NAICS code (236-238) should have at least one Uniclass mapping

### External Validation

Cross-reference with:

1. **SIC correlations** - NAICS source includes SIC mappings; validate consistency
2. **NRM column** - Uniclass includes New Rules of Measurement references; validate scope
3. **Industry practice** - Construction specifications (non-proprietary sources)

---

## Example: Full Derivation for NAICS 238130

**Source data:**
```toml
# sources/naics/lib/data/naics/238130.toml
code = "238130"
name = "Framing Contractors"
sic_correlations = ["1751"]
```

**Derivation chain:**

1. **Parse trade name:** "Framing Contractors"
2. **Extract work type:** "Framing" = structural frame assembly
3. **Identify material:** Industry practice → primarily timber in residential
4. **Map to Uniclass Systems:**
   - Wall framing → `Ss_25_10_30` (Timber frame wall structure systems)
   - Floor framing → `Ss_25_13_30` (Timber floor structure systems)
   - Roof framing → `Ss_25_16_30` (Timber roof structure systems)
5. **Map to Uniclass Products:**
   - Dimensional lumber → `Pr_20_93_52` (Timber structural sections)
   - Sheathing → `Pr_25_71_63` (Sheathing panels)
6. **Validate SIC:** `1751` = "Carpentry Work" confirms wood focus

**Result:**
```csv
238130,Framing Contractors,produces,Ss_25_10_30,Ss,Timber frame wall structure systems,1:N,A,Primary
238130,Framing Contractors,produces,Ss_25_13_30,Ss,Timber floor structure systems,1:N,A,Primary
238130,Framing Contractors,produces,Ss_25_16_30,Ss,Timber roof structure systems,1:N,A,Primary
238130,Framing Contractors,uses,Pr_20_93_52,Pr,Timber structural sections,1:N,A,Material
```

---

## Semantic Conflicts Discovered

Document in `docs/SEMANTIC_CONFLICTS.md` when:

1. **Scope mismatch** - NAICS includes work that spans multiple Uniclass tables
2. **Granularity mismatch** - NAICS 6-digit more/less specific than Uniclass
3. **Regional terminology** - US vs UK naming differences
4. **Material vs trade** - When material type defines trade but not work result

---

## Version Control

All mappings include:

- **Date created**
- **Source versions** (NAICS year, Uniclass release date)
- **Author**
- **Review status**

Changes are tracked via git commit history with references to reasoning.
