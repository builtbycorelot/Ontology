#!/usr/bin/env python3
"""Expert review interface for candidate mappings."""

import json
import csv
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
CANDIDATES = BASE / "candidates"
REVIEWED = BASE / "reviewed"
CROSSWALK = BASE / "crosswalk"

def load_candidates_for_review(table: str, min_conf='D', max_conf='A'):
    """Load candidates needing review."""
    path = CANDIDATES / f"naics_to_uniclass_{table.lower()}.json"
    if not path.exists():
        return []

    with open(path) as f:
        data = json.load(f)

    conf_order = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    min_val = conf_order.get(min_conf, 3)
    max_val = conf_order.get(max_conf, 0)

    items = []
    for c in data:
        for m in c['matches']:
            conf_val = conf_order.get(m['confidence'], 3)
            if max_val <= conf_val <= min_val:
                items.append({
                    'source_id': c['source_id'],
                    'source_name': c['source_name'],
                    'target_id': m['target_id'],
                    'target_name': m['target_name'],
                    'relationship': m['relationship'],
                    'confidence': m['confidence'],
                    'score': m['score'],
                    'shared_tokens': m.get('shared_tokens', [])
                })
    return items

def save_decision(source_id, target_id, action, confidence=None, relationship=None, notes=None):
    """Save expert decision."""
    REVIEWED.mkdir(exist_ok=True)

    decisions_file = REVIEWED / "decisions.json"
    if decisions_file.exists():
        with open(decisions_file) as f:
            decisions = json.load(f)
    else:
        decisions = {}

    key = f"{source_id}|{target_id}"
    decisions[key] = {
        'action': action,  # accept, reject, modify
        'confidence': confidence,
        'relationship': relationship,
        'notes': notes,
        'reviewed_at': datetime.now().isoformat()
    }

    with open(decisions_file, 'w') as f:
        json.dump(decisions, f, indent=2)

def batch_accept(items, relationship_override=None):
    """Accept a batch of mappings."""
    for item in items:
        save_decision(
            item['source_id'],
            item['target_id'],
            'accept',
            item['confidence'],
            relationship_override or item['relationship']
        )
    print(f"Accepted {len(items)} mappings")

def batch_reject(items):
    """Reject a batch of mappings."""
    for item in items:
        save_decision(item['source_id'], item['target_id'], 'reject')
    print(f"Rejected {len(items)} mappings")

def export_for_review(table: str, output_format='csv'):
    """Export candidates for offline review."""
    items = load_candidates_for_review(table)

    if output_format == 'csv':
        outfile = REVIEWED / f"review_{table.lower()}.csv"
        with open(outfile, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'source_id', 'source_name', 'target_id', 'target_name',
                'relationship', 'confidence', 'score', 'decision', 'notes'
            ])
            writer.writeheader()
            for item in items:
                row = {k: v for k, v in item.items() if k in writer.fieldnames}
                row['decision'] = ''  # For expert to fill
                row['notes'] = ''
                writer.writerow(row)
        print(f"Exported {len(items)} items to {outfile}")
        return outfile

def import_reviewed(table: str):
    """Import reviewed CSV with decisions."""
    infile = REVIEWED / f"review_{table.lower()}.csv"
    if not infile.exists():
        print(f"No review file found: {infile}")
        return

    with open(infile, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        accepted = 0
        rejected = 0
        for row in reader:
            decision = row.get('decision', '').strip().lower()
            if decision in ['a', 'accept', 'y', 'yes', '1']:
                save_decision(
                    row['source_id'],
                    row['target_id'],
                    'accept',
                    row.get('confidence'),
                    row.get('relationship'),
                    row.get('notes')
                )
                accepted += 1
            elif decision in ['r', 'reject', 'n', 'no', '0']:
                save_decision(row['source_id'], row['target_id'], 'reject')
                rejected += 1

    print(f"Imported: {accepted} accepted, {rejected} rejected")

def stats():
    """Show review statistics."""
    decisions_file = REVIEWED / "decisions.json"
    if not decisions_file.exists():
        print("No decisions yet")
        return

    with open(decisions_file) as f:
        decisions = json.load(f)

    accepted = sum(1 for d in decisions.values() if d['action'] == 'accept')
    rejected = sum(1 for d in decisions.values() if d['action'] == 'reject')
    modified = sum(1 for d in decisions.values() if d['action'] == 'modify')

    print(f"Total decisions: {len(decisions)}")
    print(f"  Accepted: {accepted}")
    print(f"  Rejected: {rejected}")
    print(f"  Modified: {modified}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: expert_review.py <command> [args]")
        print("Commands:")
        print("  export <table>  - Export candidates for review")
        print("  import <table>  - Import reviewed decisions")
        print("  stats           - Show review statistics")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'export' and len(sys.argv) >= 3:
        export_for_review(sys.argv[2])
    elif cmd == 'import' and len(sys.argv) >= 3:
        import_reviewed(sys.argv[2])
    elif cmd == 'stats':
        stats()
    else:
        print(f"Unknown command: {cmd}")
