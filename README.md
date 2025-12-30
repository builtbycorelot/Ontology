# CORELOT Ontology Crosswalk

**Purpose:** Synthesize open, non-proprietary classification standards for construction project management, accounting, and contract data.

**Methodology:** Linguistic derivation from first principles using only public domain and openly-licensed source materials.

---

## Licensing Audit

All standards must be defensibly non-proprietary. This section documents the legal basis for each inclusion.

### ✅ CONFIRMED OPEN - Can Use Freely

| Standard | Source | License | Citation | Git Repo |
|----------|--------|---------|----------|----------|
| **NAICS 2022** | US Census Bureau | **Public Domain** (17 U.S.C. § 105) | [census.gov/naics](https://www.census.gov/naics/) | [uscensusbureau/BEACON](https://github.com/uscensusbureau/BEACON), [leereilly/csi](https://github.com/leereilly/csi) |
| **SIC** | US DOL/OSHA | **Public Domain** (17 U.S.C. § 105) | [osha.gov/data/sic-manual](https://www.osha.gov/data/sic-manual/) | [leereilly/csi](https://github.com/leereilly/csi) |
| **OASIS UBL 2.3** | OASIS | **Royalty-free, no license fees** | [OASIS UBL TC](https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=ubl) | [oasis-tcs/ubl](https://github.com/oasis-tcs/ubl) |
| **Dublin Core** | DCMI | **CC BY 4.0** | [dublincore.org/about/copyright](https://www.dublincore.org/about/copyright/) | [dcmi](https://github.com/dcmi) |

### ✅ OPEN WITH CONDITIONS

| Standard | Source | License | Conditions | Citation | Git Repo |
|----------|--------|---------|------------|----------|----------|
| **Schema.org** | W3C Community | **CC-BY-SA 3.0** | Attribution + ShareAlike required | [schema.org/docs/terms.html](https://schema.org/docs/terms.html) | [schemaorg/schemaorg](https://github.com/schemaorg/schemaorg) |
| **Uniclass 2015** | NBS | **CC BY-ND 4.0** | Attribution required, **no derivatives** (cannot modify tables) | [uniclass.thenbs.com](https://uniclass.thenbs.com/) | [buildig/uniclass-2015](https://github.com/buildig/uniclass-2015) |
| **buildingSMART IFC** | buildingSMART | **CC BY-ND 4.0** | Attribution required, **no derivatives** | [buildingsmart.org](https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/) | [buildingSMART/IFC4.3.x-development](https://github.com/buildingSMART/IFC4.3.x-development) |
| **Peppol BIS 3.0** | OpenPEPPOL | **Open** (CEN derivative agreement) | Based on CEN CWA, customization allowed | [docs.peppol.eu](https://docs.peppol.eu/poacc/billing/3.0/bis/) | [OpenPEPPOL/peppol-bis-invoice-3](https://github.com/OpenPEPPOL/peppol-bis-invoice-3) |
| **UN/CEFACT CCL** | UNECE | **Free of charge** | Published freely by UN | [unece.org/trade/uncefact](https://unece.org/trade/uncefact) | Various |

### ❌ PROPRIETARY - Cannot Use as Basis

| Standard | Owner | Issue | Alternative |
|----------|-------|-------|-------------|
| **ISO 12006-2** | ISO | Must purchase (~CHF 177), strict copyright, no reproduction | Use Uniclass (based on ISO framework but independently licensed) |
| **ISO 16739** (IFC) | ISO | Must purchase | Use buildingSMART IFC directly (CC BY-ND 4.0) |
| **CSI MasterFormat** | CSI | Licensed, copyrighted | Use NAICS + Uniclass crosswalk |
| **AIA Documents** | AIA | Licensed, copyrighted | Use UBL + Peppol for invoice/payment structures |
| **ConsensusDocs** | AGC et al. | Licensed, copyrighted | Use generic contract terms |
| **EJCDC** | NSPE/ASCE/ACEC | Licensed (3-year term) | Use generic contract terms |

---

## Legal Derivation Chain

To prove non-infringement, we document the derivation logic:

```
CORELOT Ontology
│
├── Trade/Scope Classification
│   └── DERIVED FROM: NAICS 2022 (Public Domain - US Govt Work)
│       ├── Source: US Census Bureau
│       ├── Legal basis: 17 U.S.C. § 105 - no copyright in govt works
│       └── Verification: https://www.census.gov/naics/
│
├── Work/Product Classification
│   └── REFERENCE TO: Uniclass 2015 (CC BY-ND 4.0)
│       ├── Source: NBS (UK)
│       ├── Legal basis: Creative Commons license
│       ├── Condition: Attribution required, no modification of tables
│       └── Verification: https://uniclass.thenbs.com/
│
├── Invoice/Payment Structures
│   └── DERIVED FROM: OASIS UBL 2.3 (Royalty-free)
│       ├── Source: OASIS
│       ├── Legal basis: OASIS RF on Limited Terms policy
│       ├── Condition: Acknowledge derivation, don't claim compliance
│       └── Verification: https://docs.oasis-open.org/ubl/UBL-2.3.html
│
├── Base Vocabulary
│   └── USES: Schema.org (CC-BY-SA 3.0)
│       ├── Source: W3C Schema.org Community Group
│       ├── Legal basis: Creative Commons license
│       ├── Condition: Attribution + ShareAlike
│       └── Verification: https://schema.org/docs/terms.html
│
└── Metadata Terms
    └── USES: Dublin Core (CC BY 4.0)
        ├── Source: DCMI
        ├── Legal basis: Creative Commons license
        ├── Condition: Attribution
        └── Verification: https://www.dublincore.org/about/copyright/
```

---

## Semantic Conflicts to Resolve

When crosswalking standards, we expect conflicts in:

| Conflict Area | Standards Involved | Nature of Conflict |
|---------------|-------------------|-------------------|
| **Scope granularity** | NAICS vs Uniclass | NAICS = business entity, Uniclass = work result |
| **Product vs Trade** | NAICS (who does it) vs Uniclass (what is done) | Different classification axes |
| **Geographic scope** | NAICS (North America) vs Uniclass (UK/ISO-aligned) | Regional terminology differences |
| **Invoice structure** | UBL vs Schema.org Invoice | UBL more detailed, Schema.org more general |
| **Hierarchy depth** | 6-digit NAICS vs variable Uniclass | Different granularity levels |

These conflicts will be documented in `/docs/SEMANTIC_CONFLICTS.md` with resolution strategies.

---

## Repository Structure

```
Ontology/
├── README.md                      # This file (licensing audit)
├── LICENSE                        # Apache 2.0 for tooling
├── CONTRIBUTING.md                # How to contribute
│
├── sources/                       # Git submodules to upstream repos
│   ├── naics/                     # -> leereilly/csi or census data
│   ├── uniclass/                  # -> buildig/uniclass-2015
│   ├── ubl/                       # -> oasis-tcs/ubl
│   ├── schemaorg/                 # -> schemaorg/schemaorg
│   ├── dcmi/                      # -> dcmi/usage
│   ├── peppol/                    # -> OpenPEPPOL/peppol-bis-invoice-3
│   └── buildingsmart/             # -> buildingSMART/IFC4.3.x-development
│
├── crosswalk/                     # Our original work
│   ├── naics-to-uniclass.csv      # Mapping table
│   ├── uniclass-to-naics.csv      # Reverse mapping
│   ├── unified-taxonomy.jsonld    # Synthesized result
│   └── mapping-methodology.md     # How mappings were derived
│
├── schemas/                       # JSON-LD schemas (Apache 2.0)
│   ├── context.jsonld             # JSON-LD context
│   └── entities/
│       ├── project.jsonld
│       ├── contract.jsonld
│       └── ...
│
├── docs/
│   ├── LICENSING_AUDIT.md         # Detailed legal analysis
│   ├── SEMANTIC_CONFLICTS.md      # Conflict documentation
│   ├── CROSSWALK_METHODOLOGY.md   # Derivation methodology
│   └── UPSTREAM_PR_PLAN.md        # Strategy for contributing back
│
└── examples/                      # Example documents
```

---

## Upstream Contribution Strategy

Our crosswalk work should benefit the communities we derive from:

| Upstream Project | Potential Contribution | Expected Reception |
|-----------------|----------------------|-------------------|
| **schemaorg/schemaorg** | Construction industry usage examples | Positive - they seek real-world examples |
| **oasis-tcs/ubl** | Construction invoice profiles | Positive - industry-specific implementations valued |
| **buildig/uniclass-2015** | NAICS crosswalk mappings | Positive - expands international utility |
| **OpenPEPPOL** | Construction sector invoice type guidance | Positive - expanding globally, sector input needed |
| **buildingSMART** | Alignment with open business standards | Positive - interoperability is core mission |

---

## Getting Started

```bash
# Clone with submodules
git clone --recursive https://github.com/[org]/Ontology.git

# Or add submodules after clone
git submodule update --init --recursive

# View crosswalk data
cat crosswalk/naics-to-uniclass.csv
```

---

## License

- **Tooling & Original Work:** Apache 2.0
- **Documentation:** CC BY 4.0
- **Source Data:** See individual source licenses (submodule READMEs)

---

## References

### Primary Sources (Verified Open)
- [NAICS 2022](https://www.census.gov/naics/) - US Census Bureau (Public Domain)
- [Uniclass 2015](https://uniclass.thenbs.com/) - NBS (CC BY-ND 4.0)
- [OASIS UBL 2.3](https://docs.oasis-open.org/ubl/UBL-2.3.html) - OASIS (Royalty-free)
- [Schema.org](https://schema.org/) - W3C (CC-BY-SA 3.0)
- [Dublin Core](https://www.dublincore.org/) - DCMI (CC BY 4.0)
- [Peppol BIS Billing 3.0](https://docs.peppol.eu/poacc/billing/3.0/bis/) - OpenPEPPOL (Open)
- [buildingSMART IFC](https://technical.buildingsmart.org/standards/ifc/) - buildingSMART (CC BY-ND 4.0)
- [UN/CEFACT](https://unece.org/trade/uncefact) - UNECE (Free of charge)

### Git Repositories
- [schemaorg/schemaorg](https://github.com/schemaorg/schemaorg)
- [oasis-tcs/ubl](https://github.com/oasis-tcs/ubl)
- [dcmi](https://github.com/dcmi)
- [buildig/uniclass-2015](https://github.com/buildig/uniclass-2015)
- [OpenPEPPOL/peppol-bis-invoice-3](https://github.com/OpenPEPPOL/peppol-bis-invoice-3)
- [buildingSMART/IFC4.3.x-development](https://github.com/buildingSMART/IFC4.3.x-development)
- [leereilly/csi](https://github.com/leereilly/csi) (NAICS/SIC data)
- [uscensusbureau/BEACON](https://github.com/uscensusbureau/BEACON)
