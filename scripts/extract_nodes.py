#!/usr/bin/env python3
"""Extract and normalize nodes from source standards."""

import csv
import json
import re
from pathlib import Path

BASE = Path(__file__).parent.parent
SOURCES = BASE / "sources"
OUTPUT = BASE / "extracted"

def normalize(text: str) -> set:
    """Extract normalized tokens from text."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = set(text.split())
    # Remove stopwords
    stops = {'and', 'or', 'the', 'a', 'an', 'of', 'for', 'to', 'in', 'on', 'with', 'by', 'as', 'at', 'from'}
    return tokens - stops

def extract_naics():
    """Extract NAICS codes from lookup CSV."""
    path = SOURCES / "naics/lib/data/naics/naics-lookup.csv"
    nodes = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                code, name = row[0].strip('"'), row[1].strip('"')
                if code.isdigit():
                    nodes.append({
                        'id': f'naics:{code}',
                        'code': code,
                        'name': name,
                        'tokens': list(normalize(name)),
                        'level': len(code)
                    })
    return nodes

def extract_uniclass(table: str):
    """Extract Uniclass codes from table CSV."""
    path = SOURCES / f"uniclass/uniclass2015/Uniclass2015_{table}.csv"
    nodes = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get('Code', '')
            title = row.get('Title', '')
            if code and title:
                nodes.append({
                    'id': f'uc:{code}',
                    'code': code,
                    'name': title,
                    'tokens': list(normalize(title)),
                    'table': table,
                    'group': row.get('Group', ''),
                    'subgroup': row.get('Sub group', '')
                })
    return nodes

def extract_schemaorg():
    """Extract Schema.org types."""
    # Try latest version first
    for ver in ['26.0', '9.0']:
        path = SOURCES / f"schemaorg/data/releases/{ver}/schemaorg-current-https-types.csv"
        if path.exists():
            break

    nodes = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            type_id = row.get('id', '')
            label = row.get('label', '')
            if type_id and label:
                # Extract just the type name
                name = type_id.split('/')[-1]
                nodes.append({
                    'id': f'schema:{name}',
                    'uri': type_id,
                    'name': label,
                    'tokens': list(normalize(label)),
                    'subTypeOf': row.get('subTypeOf', '')
                })
    return nodes

def main():
    OUTPUT.mkdir(exist_ok=True)

    # Extract all sources
    print("Extracting NAICS...")
    naics = extract_naics()
    with open(OUTPUT / "naics.json", 'w') as f:
        json.dump(naics, f, indent=2)
    print(f"  {len(naics)} nodes")

    for table in ['Ss', 'Pr', 'Ac', 'En', 'Co']:
        print(f"Extracting Uniclass {table}...")
        uc = extract_uniclass(table)
        with open(OUTPUT / f"uniclass_{table.lower()}.json", 'w') as f:
            json.dump(uc, f, indent=2)
        print(f"  {len(uc)} nodes")

    print("Extracting Schema.org...")
    schema = extract_schemaorg()
    with open(OUTPUT / "schemaorg.json", 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"  {len(schema)} nodes")

    print("\nDone. Output in extracted/")

if __name__ == "__main__":
    main()
