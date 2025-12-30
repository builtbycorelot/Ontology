# CORELOT Ontology Graph Model

## Design Principle

Each standard contributes **node types** and **vocabulary**. We create a unified graph where nodes from different standards connect via typed relationships.

---

## Node Types by Source Standard

### From NAICS (census.gov - Public Domain)

| Node Type | Prefix | Description |
|-----------|--------|-------------|
| `Trade` | `naics:` | Business entity classification |
| `Sector` | `naics:` | Industry sector (2-digit) |
| `Subsector` | `naics:` | Subsector (3-digit) |

### From Uniclass (NBS - CC BY-ND 4.0)

| Node Type | Prefix | Description |
|-----------|--------|-------------|
| `WorkResult` | `uc:Ss` | Systems - what is produced |
| `Product` | `uc:Pr` | Products - materials used |
| `Activity` | `uc:Ac` | Activities - processes performed |
| `Space` | `uc:SL` | Spaces/Locations |
| `Entity` | `uc:En` | Building entities |
| `Role` | `uc:Ro` | Project roles |

### From Schema.org (W3C - CC-BY-SA 3.0)

| Node Type | Prefix | Description |
|-----------|--------|-------------|
| `Organization` | `schema:` | Companies, contractors |
| `Person` | `schema:` | Individuals |
| `Place` | `schema:` | Locations |
| `Event` | `schema:` | Milestones, meetings |
| `Action` | `schema:` | Activities |

### From OASIS UBL (Royalty-free)

| Node Type | Prefix | Description |
|-----------|--------|-------------|
| `Invoice` | `ubl:` | Invoice document |
| `Order` | `ubl:` | Purchase order |
| `Despatch` | `ubl:` | Delivery/shipment |
| `Party` | `ubl:` | Business party |
| `LineItem` | `ubl:` | Transaction line |

### From Dublin Core (DCMI - CC BY 4.0)

| Node Type | Prefix | Description |
|-----------|--------|-------------|
| `Resource` | `dcterms:` | Any described resource |
| `Agent` | `dcterms:` | Entity responsible |
| `Collection` | `dcterms:` | Aggregation |

### From Peppol (Open)

| Node Type | Prefix | Description |
|-----------|--------|-------------|
| `BillingDocument` | `peppol:` | E-invoice |
| `CreditNote` | `peppol:` | Credit memo |

### From buildingSMART IFC (CC BY-ND 4.0)

| Node Type | Prefix | Description |
|-----------|--------|-------------|
| `Element` | `ifc:` | Building element |
| `Spatial` | `ifc:` | Spatial structure |
| `Process` | `ifc:` | Construction process |

---

## CORELOT Native Node Types

For concepts not covered by source standards:

| Node Type | Prefix | Description |
|-----------|--------|-------------|
| `Project` | `corelot:` | Construction project |
| `Contract` | `corelot:` | Agreement |
| `ChangeOrder` | `corelot:` | Contract modification |
| `PaymentApplication` | `corelot:` | Payment request |
| `ScheduleOfValues` | `corelot:` | Cost breakdown |
| `Milestone` | `corelot:` | Project milestone |

---

## Edge Types (Relationships)

Edges connect nodes across standards:

### Production Relationships

| Edge Type | From → To | Description |
|-----------|-----------|-------------|
| `produces` | Trade → WorkResult | Trade produces work |
| `requires` | WorkResult → Product | Work requires products |
| `uses` | Trade → Product | Trade uses materials |
| `performs` | Trade → Activity | Trade performs activity |

### Organizational Relationships

| Edge Type | From → To | Description |
|-----------|-----------|-------------|
| `employs` | Organization → Trade | Company has trade capability |
| `holds` | Organization → Contract | Party holds contract |
| `submits` | Organization → Invoice | Party submits invoice |

### Document Relationships

| Edge Type | From → To | Description |
|-----------|-----------|-------------|
| `referencesProject` | Invoice → Project | Document references project |
| `containsLine` | Invoice → LineItem | Document contains line |
| `classifiedAs` | LineItem → WorkResult | Line classified by work |
| `classifiedAs` | LineItem → Trade | Line classified by trade |

### Hierarchical Relationships

| Edge Type | From → To | Description |
|-----------|-----------|-------------|
| `partOf` | Node → Node | Child of parent |
| `broaderThan` | Node → Node | Broader category |
| `narrowerThan` | Node → Node | Narrower category |

### Equivalence Relationships

| Edge Type | From → To | Description |
|-----------|-----------|-------------|
| `equivalentTo` | Node → Node | Semantic equivalent |
| `relatedTo` | Node → Node | Related concept |
| `sameAs` | Node → Node | Identical (different vocab) |

---

## Example Graph Fragment

```
┌──────────────────┐         ┌───────────────────────┐
│ naics:238130     │produces │ uc:Ss_25_10_30        │
│ Trade:           │────────▶│ WorkResult:           │
│ "Framing         │         │ "Timber frame wall    │
│  Contractors"    │         │  structure systems"   │
└──────────────────┘         └───────────────────────┘
        │                              │
        │employs                       │requires
        ▼                              ▼
┌──────────────────┐         ┌───────────────────────┐
│ schema:Org       │         │ uc:Pr_20_93_52        │
│ "Acme Builders"  │         │ Product:              │
│                  │         │ "Timber structural    │
└──────────────────┘         │  sections"            │
        │                    └───────────────────────┘
        │holds
        ▼
┌──────────────────┐         ┌───────────────────────┐
│ corelot:Contract │contains │ corelot:SOV           │
│ "CTR-2024-001"   │────────▶│ ScheduleOfValues      │
└──────────────────┘         └───────────────────────┘
        │                              │
        │referencesProject             │containsLine
        ▼                              ▼
┌──────────────────┐         ┌───────────────────────┐
│ corelot:Project  │         │ ubl:LineItem          │
│ "Smith Residence"│         │ "Framing labor"       │
└──────────────────┘         └───────────────────────┘
                                       │
                                       │classifiedAs
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
           ┌───────────────┐                    ┌───────────────────┐
           │ naics:238130  │                    │ uc:Ss_25_10_30    │
           │ Trade         │                    │ WorkResult        │
           └───────────────┘                    └───────────────────┘
```

---

## JSON-LD Representation

Nodes use their source namespace. Edges are properties.

```json
{
  "@context": {
    "naics": "https://www.census.gov/naics/",
    "uc": "https://uniclass.thenbs.com/taxon/",
    "schema": "https://schema.org/",
    "ubl": "urn:oasis:names:specification:ubl:schema:xsd:",
    "corelot": "https://corelot.io/ontology/",
    "produces": "corelot:produces",
    "requires": "corelot:requires",
    "classifiedAs": "corelot:classifiedAs"
  },
  "@graph": [
    {
      "@id": "naics:238130",
      "@type": "corelot:Trade",
      "schema:name": "Framing Contractors",
      "produces": [
        {"@id": "uc:Ss_25_10_30"},
        {"@id": "uc:Ss_25_13_30"},
        {"@id": "uc:Ss_25_16_30"}
      ]
    },
    {
      "@id": "uc:Ss_25_10_30",
      "@type": "corelot:WorkResult",
      "schema:name": "Timber frame wall structure systems",
      "requires": [
        {"@id": "uc:Pr_20_93_52"}
      ]
    }
  ]
}
```

---

## Query Examples

With this graph model, we can answer:

1. **What work can this trade perform?**
   ```
   MATCH (t:Trade {code: "238130"})-[:produces]->(w:WorkResult)
   RETURN w
   ```

2. **What trades can produce this work?**
   ```
   MATCH (t:Trade)-[:produces]->(w:WorkResult {code: "Ss_25_10_30"})
   RETURN t
   ```

3. **What products are needed for this invoice line?**
   ```
   MATCH (l:LineItem)-[:classifiedAs]->(w:WorkResult)-[:requires]->(p:Product)
   RETURN p
   ```

4. **What trades does this company employ?**
   ```
   MATCH (o:Organization {name: "Acme"})-[:employs]->(t:Trade)
   RETURN t
   ```

---

## Extensibility

New standards can be added by:

1. Define new node types with appropriate prefix
2. Define edges connecting to existing node types
3. Document in this file
4. Add source repo as git submodule

The graph grows without breaking existing relationships.
