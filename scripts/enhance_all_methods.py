"""
Comprehensive Enhancement - All Methods
1. BLS Industry-Occupation Matrix (SOC-NAICS bridge)
2. Brick Schema parsing (HVAC/electrical systems)
3. WordNet synonym expansion
4. Public document search references
"""

import json
import re
import urllib.request
from pathlib import Path
from collections import defaultdict

# WordNet is optional - skip if not available
WORDNET_AVAILABLE = False
try:
    from nltk.corpus import wordnet
    import nltk
    try:
        wordnet.synsets('test')
        WORDNET_AVAILABLE = True
    except LookupError:
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        WORDNET_AVAILABLE = True
except Exception as e:
    print(f"WordNet not available ({e}) - using manual synonyms instead")

OUTPUT_DIR = Path("data/enhanced")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================
# 1. BLS INDUSTRY-OCCUPATION MATRIX
# ============================================

# Construction industry NAICS -> typical SOC occupations
# Source: BLS Industry-Occupation Matrix (public domain)
BLS_CONSTRUCTION_MATRIX = {
    "238210": {  # Electrical Contractors
        "primary_soc": ["47-2111"],  # Electricians
        "secondary_soc": ["47-1011", "49-2022"],  # Supervisors, Telecom installers
        "description": "Electrical wiring, fixtures, equipment"
    },
    "238220": {  # Plumbing, Heating, AC Contractors
        "primary_soc": ["47-2152"],  # Plumbers, Pipefitters
        "secondary_soc": ["49-9021", "47-2011"],  # HVAC mechanics, Boilermakers
        "description": "Plumbing, HVAC installation"
    },
    "238310": {  # Drywall and Insulation Contractors
        "primary_soc": ["47-2081", "47-2131"],  # Drywall installers, Insulation workers
        "secondary_soc": ["47-2082"],  # Tapers
        "description": "Drywall, insulation, acoustical work"
    },
    "238320": {  # Painting and Wall Covering Contractors
        "primary_soc": ["47-2141", "47-2142"],  # Painters, Paperhangers
        "description": "Painting, wallpaper, coatings"
    },
    "238340": {  # Tile and Terrazzo Contractors
        "primary_soc": ["47-2044", "47-2053"],  # Tile setters, Terrazzo workers
        "description": "Tile, stone, terrazzo installation"
    },
    "238110": {  # Poured Concrete Foundation Contractors
        "primary_soc": ["47-2051", "47-2061"],  # Concrete finishers, Construction laborers
        "description": "Concrete foundations, slabs"
    },
    "238120": {  # Structural Steel and Precast Concrete
        "primary_soc": ["47-2221", "47-2171"],  # Structural iron workers, Rebar workers
        "description": "Steel erection, precast concrete"
    },
    "238130": {  # Framing Contractors
        "primary_soc": ["47-2031"],  # Carpenters
        "description": "Wood framing, structural carpentry"
    },
    "238140": {  # Masonry Contractors
        "primary_soc": ["47-2021", "47-2022"],  # Brickmasons, Stonemasons
        "description": "Brick, block, stone masonry"
    },
    "238150": {  # Glass and Glazing Contractors
        "primary_soc": ["47-2121"],  # Glaziers
        "description": "Glass installation, curtain walls"
    },
    "238160": {  # Roofing Contractors
        "primary_soc": ["47-2181"],  # Roofers
        "description": "Roofing systems, waterproofing"
    },
    "238170": {  # Siding Contractors
        "primary_soc": ["47-2031"],  # Carpenters (siding specialty)
        "description": "Siding, cladding, exterior finish"
    },
    "238190": {  # Other Foundation/Exterior Contractors
        "primary_soc": ["47-2061", "47-4051"],  # Laborers, Highway maintenance
        "description": "Waterproofing, dampproofing"
    },
    "238910": {  # Site Preparation Contractors
        "primary_soc": ["47-2073", "47-2072"],  # Operating engineers, Pile drivers
        "description": "Excavation, grading, demolition"
    },
    "238990": {  # All Other Specialty Trade Contractors
        "primary_soc": ["47-2061", "47-4090"],  # Laborers, Misc construction
        "description": "Specialty trades not elsewhere classified"
    }
}

def save_bls_matrix():
    """Save BLS matrix as structured JSON"""
    output = {
        "_meta": {
            "source": "BLS Industry-Occupation Matrix",
            "license": "Public Domain (US Government)",
            "url": "https://www.bls.gov/emp/tables/industry-occupation-matrix-industry.htm",
            "description": "Maps NAICS industries to typical SOC occupations"
        },
        "matrix": BLS_CONSTRUCTION_MATRIX
    }

    with open(OUTPUT_DIR / "bls_naics_soc_matrix.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"BLS Matrix: {len(BLS_CONSTRUCTION_MATRIX)} NAICS codes mapped")
    return output

# ============================================
# 2. BRICK SCHEMA PARSER
# ============================================

def parse_brick_schema():
    """Extract system classes from Brick Schema TTL"""
    brick_file = Path("data/Brick.ttl")
    if not brick_file.exists():
        print("Brick Schema not found - skipping")
        return None

    # Parse TTL for system classes
    systems = {}
    current_class = None

    with open(brick_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all System subclasses
    # Pattern: brick:XXX_System a owl:Class ; rdfs:subClassOf brick:System
    system_pattern = re.compile(
        r'brick:(\w+_System)\s+a\s+(?:owl:Class|rdfs:Class).*?rdfs:label\s+"([^"]+)"',
        re.DOTALL
    )

    for match in system_pattern.finditer(content):
        class_name = match.group(1)
        label = match.group(2)
        systems[class_name] = {
            "label": label,
            "uri": f"https://brickschema.org/schema/Brick#{class_name}"
        }

    # Also find direct mentions of key systems
    key_systems = [
        "HVAC_System", "Electrical_System", "Lighting_System",
        "Plumbing_System", "Fire_Safety_System", "Security_System",
        "Water_System", "Air_System", "Heating_System", "Cooling_System"
    ]

    for sys in key_systems:
        if sys not in systems:
            if f"brick:{sys}" in content:
                systems[sys] = {
                    "label": sys.replace("_", " "),
                    "uri": f"https://brickschema.org/schema/Brick#{sys}"
                }

    # Map Brick systems to Uniclass
    brick_to_uniclass = {
        "HVAC_System": "Ss_60",
        "Electrical_System": "Ss_70",
        "Lighting_System": "Ss_70_40",
        "Plumbing_System": "Ss_55",
        "Fire_Safety_System": "Ss_75",
        "Security_System": "Ss_75_70",
        "Water_System": "Ss_55",
        "Heating_System": "Ss_60_40",
        "Cooling_System": "Ss_60_30",
        "Air_System": "Ss_60_50"
    }

    output = {
        "_meta": {
            "source": "Brick Schema v1.4.4",
            "license": "BSD-3-Clause",
            "url": "https://brickschema.org/",
            "description": "Building system ontology - HVAC, electrical, etc."
        },
        "systems": systems,
        "brick_to_uniclass": brick_to_uniclass
    }

    with open(OUTPUT_DIR / "brick_systems.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Brick Schema: {len(systems)} system classes extracted")
    return output

# ============================================
# 3. WORDNET SYNONYM EXPANSION
# ============================================

# Construction terms to expand
CONSTRUCTION_TERMS = [
    "siding", "cladding", "drywall", "plasterboard", "lumber", "timber",
    "roofing", "glazing", "masonry", "plumbing", "electrical", "framing",
    "insulation", "flooring", "ceiling", "foundation", "concrete", "steel",
    "carpentry", "painting", "tile", "terrazzo", "demolition", "excavation"
]

def expand_with_wordnet():
    """Expand construction terms with synonyms (manual fallback if WordNet unavailable)"""

    # Manual UK/US construction synonyms (from Wikidata CC0 research)
    MANUAL_SYNONYMS = {
        "siding": {"synonyms": ["cladding", "wall cladding", "external cladding", "facade"], "hypernyms": ["exterior finish"]},
        "cladding": {"synonyms": ["siding", "wall covering", "facade"], "hypernyms": ["exterior finish"]},
        "drywall": {"synonyms": ["plasterboard", "wallboard", "gypsum board", "sheetrock"], "hypernyms": ["wall material"]},
        "plasterboard": {"synonyms": ["drywall", "wallboard", "gypsum board"], "hypernyms": ["wall material"]},
        "lumber": {"synonyms": ["timber", "softwood", "wood", "dimensional lumber"], "hypernyms": ["building material"]},
        "timber": {"synonyms": ["lumber", "wood", "softwood"], "hypernyms": ["building material"]},
        "roofing": {"synonyms": ["roof covering", "roof system", "roof membrane"], "hypernyms": ["building envelope"]},
        "glazing": {"synonyms": ["glass installation", "fenestration", "window work"], "hypernyms": ["building envelope"]},
        "masonry": {"synonyms": ["brickwork", "stonework", "blockwork"], "hypernyms": ["wall construction"]},
        "plumbing": {"synonyms": ["pipework", "sanitary installation", "water systems"], "hypernyms": ["building services"]},
        "electrical": {"synonyms": ["electrics", "wiring", "power installation"], "hypernyms": ["building services"]},
        "framing": {"synonyms": ["structural frame", "studwork", "timber frame"], "hypernyms": ["structure"]},
        "insulation": {"synonyms": ["thermal insulation", "acoustic insulation", "lagging"], "hypernyms": ["building material"]},
        "flooring": {"synonyms": ["floor covering", "floor finish", "floor system"], "hypernyms": ["interior finish"]},
        "ceiling": {"synonyms": ["suspended ceiling", "ceiling system", "soffit"], "hypernyms": ["interior finish"]},
        "foundation": {"synonyms": ["footings", "substructure", "base"], "hypernyms": ["structure"]},
        "concrete": {"synonyms": ["cement", "reinforced concrete", "cast concrete"], "hypernyms": ["building material"]},
        "steel": {"synonyms": ["structural steel", "metal framing", "steelwork"], "hypernyms": ["building material"]},
        "carpentry": {"synonyms": ["joinery", "woodwork", "timber construction"], "hypernyms": ["construction trade"]},
        "painting": {"synonyms": ["decorating", "coating", "finishing"], "hypernyms": ["interior finish"]},
        "tile": {"synonyms": ["tiling", "ceramic tile", "floor tile"], "hypernyms": ["floor covering"]},
        "terrazzo": {"synonyms": ["terrazzo flooring", "aggregate flooring"], "hypernyms": ["floor covering"]},
        "demolition": {"synonyms": ["demo", "deconstruction", "wrecking"], "hypernyms": ["site work"]},
        "excavation": {"synonyms": ["earthwork", "digging", "groundwork"], "hypernyms": ["site work"]}
    }

    if WORDNET_AVAILABLE:
        expansions = {}
        for term in CONSTRUCTION_TERMS:
            synonyms = set()
            hypernyms = set()

            for syn in wordnet.synsets(term):
                for lemma in syn.lemmas():
                    name = lemma.name().replace('_', ' ')
                    if name.lower() != term.lower():
                        synonyms.add(name)

                for hyper in syn.hypernyms():
                    for lemma in hyper.lemmas():
                        hypernyms.add(lemma.name().replace('_', ' '))

            if synonyms or hypernyms:
                expansions[term] = {
                    "synonyms": list(synonyms)[:10],
                    "hypernyms": list(hypernyms)[:5]
                }
        source = "Princeton WordNet"
    else:
        # Use manual synonyms
        expansions = MANUAL_SYNONYMS
        source = "Manual UK/US synonyms (Wikidata research)"

    output = {
        "_meta": {
            "source": source,
            "license": "WordNet License (BSD-like) / CC0",
            "description": "Synonym expansion for construction terms"
        },
        "expansions": expansions
    }

    with open(OUTPUT_DIR / "wordnet_expansions.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Synonyms: {len(expansions)} terms expanded (source: {source})")
    return output

# ============================================
# 4. PUBLIC DOCUMENT REFERENCES
# ============================================

def compile_document_sources():
    """Compile references to public documents with dual classifications"""

    # These are known public sources that use both NAICS and Uniclass/similar
    document_sources = {
        "_meta": {
            "description": "Public document sources with construction classifications",
            "note": "These sources contain real-world usage of classification codes",
            "license": "Various - see individual sources"
        },
        "sources": [
            {
                "name": "UK Government Digital Marketplace",
                "url": "https://www.digitalmarketplace.service.gov.uk/",
                "classifications": ["Uniclass"],
                "license": "Open Government License",
                "content": "Public sector construction procurement"
            },
            {
                "name": "GSA Federal Acquisition Service",
                "url": "https://www.gsa.gov/",
                "classifications": ["NAICS", "PSC"],
                "license": "Public Domain",
                "content": "US federal construction contracts"
            },
            {
                "name": "Open BIM Standards",
                "url": "https://github.com/topics/openbim",
                "classifications": ["IFC", "Uniclass"],
                "license": "Various open source",
                "content": "BIM model classification examples"
            },
            {
                "name": "NBS National BIM Library",
                "url": "https://www.nationalbimlibrary.com/",
                "classifications": ["Uniclass", "NBS"],
                "license": "Free to use",
                "content": "BIM objects with Uniclass codes"
            },
            {
                "name": "Census Bureau Construction Statistics",
                "url": "https://www.census.gov/construction/",
                "classifications": ["NAICS"],
                "license": "Public Domain",
                "content": "Construction industry data by NAICS"
            },
            {
                "name": "RICS Construction Data",
                "url": "https://www.rics.org/",
                "classifications": ["NRM", "RICS"],
                "license": "Proprietary (reference only)",
                "content": "Cost data with work classifications"
            }
        ],
        "academic_papers": [
            {
                "title": "Classification systems for the construction industry",
                "doi": "Various",
                "note": "Search Google Scholar for 'NAICS Uniclass crosswalk construction'"
            }
        ]
    }

    with open(OUTPUT_DIR / "document_sources.json", "w") as f:
        json.dump(document_sources, f, indent=2)

    print(f"Document Sources: {len(document_sources['sources'])} reference sources compiled")
    return document_sources

# ============================================
# MAIN
# ============================================

def main():
    print("=" * 50)
    print("COMPREHENSIVE ENHANCEMENT - ALL METHODS")
    print("=" * 50)

    print("\n1. BLS Industry-Occupation Matrix...")
    bls = save_bls_matrix()

    print("\n2. Brick Schema Parsing...")
    brick = parse_brick_schema()

    print("\n3. WordNet Synonym Expansion...")
    wordnet_data = expand_with_wordnet()

    print("\n4. Public Document References...")
    docs = compile_document_sources()

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Files created:")
    for f in OUTPUT_DIR.glob("*.json"):
        print(f"  - {f.name}")

    # Create combined enhancement index
    index = {
        "enhanced_at": "2024-12-30",
        "methods": {
            "bls_matrix": {
                "file": "bls_naics_soc_matrix.json",
                "naics_codes": len(BLS_CONSTRUCTION_MATRIX) if bls else 0
            },
            "brick_schema": {
                "file": "brick_systems.json",
                "systems": len(brick["systems"]) if brick else 0
            },
            "wordnet": {
                "file": "wordnet_expansions.json",
                "terms": len(wordnet_data["expansions"]) if wordnet_data else 0
            },
            "document_sources": {
                "file": "document_sources.json",
                "sources": len(docs["sources"]) if docs else 0
            }
        }
    }

    with open(OUTPUT_DIR / "enhancement_index.json", "w") as f:
        json.dump(index, f, indent=2)

    print(f"\nEnhancement index: {OUTPUT_DIR / 'enhancement_index.json'}")

if __name__ == "__main__":
    main()
