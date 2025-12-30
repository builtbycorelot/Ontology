# Instance Storage

Simple file-based storage for ontology instances using **double-write pattern** (JSON-LD + CSV) for continuity checks.

## Directory Structure

```
instances/
├── nodes/           # JSON-LD files for node instances
│   ├── trades/      # NAICS trade instances
│   ├── systems/     # Uniclass system instances
│   └── entities/    # Building/complex instances
├── edges/           # CSV files for relationships
│   └── relationships.csv
├── chunks/          # Bundled JSON-LD chunks (max 1000 nodes)
│   └── chunk_001.jsonld
└── README.md
```

## Double-Write Pattern

Every node is written in two formats:

1. **JSON-LD** (primary) - Full semantic representation
2. **CSV** (mirror) - Flat tabular backup for continuity checks

### Validation

```bash
# Count nodes in JSON-LD chunks
jq '.["@graph"] | length' chunks/*.jsonld | paste -sd+ | bc

# Count rows in CSV (minus header)
tail -n +2 edges/relationships.csv | wc -l

# These should match when in sync
```

## Node File Format

### JSON-LD (`nodes/{type}/{id}.jsonld`)

```json
{
  "@context": "../schemas/corelot-context.jsonld",
  "@id": "naics:238130",
  "@type": "corelot:Trade",
  "schema:name": "Framing Contractors",
  "produces": [
    {"@id": "uc:Ss_25_10_30"},
    {"@id": "uc:Ss_25_13_30"}
  ]
}
```

### CSV Mirror (`edges/relationships.csv`)

```csv
source_id,relationship,target_id,confidence,timestamp
naics:238130,produces,uc:Ss_25_10_30,A,2025-12-30T00:00:00Z
naics:238130,produces,uc:Ss_25_13_30,A,2025-12-30T00:00:00Z
```

## Chunk Files

For bulk operations, nodes are bundled into chunks of max 1000 nodes:

```json
{
  "@context": "../schemas/corelot-context.jsonld",
  "@graph": [
    {"@id": "naics:238110", "@type": "corelot:Trade", ...},
    {"@id": "naics:238120", "@type": "corelot:Trade", ...},
    ...
  ],
  "meta": {
    "chunk": 1,
    "count": 1000,
    "created": "2025-12-30T00:00:00Z"
  }
}
```

## Usage

### Add a Node

1. Write JSON-LD to `nodes/{type}/{id}.jsonld`
2. Append edge rows to `edges/relationships.csv`
3. Regenerate chunk if needed

### Query Nodes

For now, use grep/jq on files:

```bash
# Find all trades that produce timber systems
grep -l "Ss_25_10_30" nodes/trades/*.jsonld

# Find all relationships for a trade
grep "naics:238130" edges/relationships.csv
```

## Future: Database Migration

When ready to migrate to PostgreSQL or Graph DB:

1. Load `edges/relationships.csv` for bulk edge import
2. Load `chunks/*.jsonld` for bulk node import
3. Validate counts match
4. Switch adapter in application config
