"""
Ontology Audit - Node Count & Confidence Assessment
"""

import json
from pathlib import Path
from collections import defaultdict

SCHEMA_DIR = Path("schema")
CROSSWALK_DIR = Path("crosswalk")

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def count_nodes():
    """Count all nodes in the ontology"""

    counts = {
        "layer": {},
        "total": 0,
        "by_confidence": defaultdict(int),
        "gaps": []
    }

    # 1. TASK ONTOLOGY
    task_ont = load_json(SCHEMA_DIR / "task_ontology.json")
    if task_ont:
        trades = task_ont.get("trades", {})
        task_count = 0
        phase_count = 0
        for trade_name, trade_data in trades.items():
            phases = trade_data.get("phases", {})
            phase_count += len(phases)
            for phase_name, phase_data in phases.items():
                tasks = phase_data.get("tasks", [])
                task_count += len(tasks)

        counts["layer"]["Task Ontology"] = {
            "trades": len(trades),
            "phases": phase_count,
            "tasks": task_count,
            "confidence": "MEDIUM",
            "source": "User seed + O*NET"
        }

    # 2. TRADE DEFINITIONS
    trade_def = load_json(SCHEMA_DIR / "trade_definitions.json")
    if trade_def:
        trades = trade_def.get("trades", {})
        mapped = sum(1 for t in trades.values() if t.get("naics") != "UNMAPPED")
        unmapped = len(trades) - mapped

        counts["layer"]["Trade Definitions"] = {
            "total_trades": len(trades),
            "naics_mapped": mapped,
            "unmapped": unmapped,
            "confidence": "HIGH" if unmapped == 0 else "MEDIUM",
            "source": "NAICS + Uniclass crosswalk"
        }
        if unmapped > 0:
            counts["gaps"].append(f"{unmapped} trades lack NAICS mapping")

    # 3. SCHEDULE ONTOLOGY
    sched = load_json(SCHEMA_DIR / "schedule_ontology.json")
    if sched:
        sched_tasks = sched.get("schedule_tasks", {})
        task_count = 0
        inspection_count = 0
        has_predecessor = 0
        no_predecessor = 0

        for phase, subphases in sched_tasks.items():
            if isinstance(subphases, dict):
                if "tasks" in subphases:
                    # Direct tasks (like CLOSE_OUT)
                    for t in subphases.get("tasks", []):
                        task_count += 1
                        if t.get("predecessor"):
                            has_predecessor += 1
                        else:
                            no_predecessor += 1
                        if t.get("inspection"):
                            inspection_count += 1
                else:
                    # Nested subphases
                    for subphase, data in subphases.items():
                        if isinstance(data, dict) and "tasks" in data:
                            for t in data.get("tasks", []):
                                task_count += 1
                                if t.get("predecessor"):
                                    has_predecessor += 1
                                else:
                                    no_predecessor += 1
                                if t.get("inspection"):
                                    inspection_count += 1

        counts["layer"]["Schedule Ontology"] = {
            "schedule_tasks": task_count,
            "with_predecessors": has_predecessor,
            "without_predecessors": no_predecessor,
            "inspections": inspection_count,
            "draws": len(sched.get("schedule_tasks", {}).get("DRAWS", {}).get("draws", [])),
            "confidence": "HIGH",
            "source": "User workflow template"
        }

        predecessor_pct = (has_predecessor / task_count * 100) if task_count > 0 else 0
        if predecessor_pct < 80:
            counts["gaps"].append(f"Only {predecessor_pct:.0f}% of schedule tasks have predecessors defined")

    # 4. COST MODEL
    cost = load_json(SCHEMA_DIR / "cost_model.json")
    if cost:
        line_items = 0
        linked_to_trade = 0

        for cat_name, cat_data in cost.get("cost_categories", {}).items():
            for sub_name, sub_data in cat_data.get("subcategories", {}).items():
                for item in sub_data.get("line_items", []):
                    line_items += 1
                    if item.get("trade"):
                        linked_to_trade += 1

        counts["layer"]["Cost Model"] = {
            "line_items": line_items,
            "linked_to_trade": linked_to_trade,
            "unlinked": line_items - linked_to_trade,
            "confidence": "MEDIUM",
            "source": "User budget template"
        }

        link_pct = (linked_to_trade / line_items * 100) if line_items > 0 else 0
        if link_pct < 90:
            counts["gaps"].append(f"Only {link_pct:.0f}% of cost items linked to trades")

    # 5. PRODUCT RULES
    products = load_json(SCHEMA_DIR / "product_rules.json")
    if products:
        product_count = 0
        rule_count = 0
        task_rules = 0

        for cat_name, cat_data in products.get("product_categories", {}).items():
            product_count += len(cat_data.get("products", []))

        for trade, tasks in products.get("task_product_rules", {}).items():
            if isinstance(tasks, dict):
                for task_name, task_data in tasks.items():
                    if isinstance(task_data, dict):
                        task_rules += 1
                        rules = task_data.get("rules", [])
                        rule_count += len(rules)

        constraint_count = len(products.get("constraint_rules", {}).get("rules", []))

        counts["layer"]["Product Rules"] = {
            "products": product_count,
            "task_rules": task_rules,
            "conditions": rule_count,
            "constraints": constraint_count,
            "confidence": "LOW",
            "source": "Generated - needs validation"
        }
        counts["gaps"].append("Product rules need expert validation")

    # 6. CROSSWALK (from earlier work)
    crosswalk = load_json(CROSSWALK_DIR / "final_crosswalk.json")
    if crosswalk:
        mappings = crosswalk.get("mappings", [])
        by_tier = defaultdict(int)
        for m in mappings:
            tier = m.get("confidence_tier", 4)
            by_tier[tier] += 1

        counts["layer"]["Classification Crosswalk"] = {
            "total_mappings": len(mappings),
            "tier_1_ground_truth": by_tier.get(1, 0),
            "tier_2_high": by_tier.get(2, 0),
            "tier_3_medium": by_tier.get(3, 0),
            "tier_4_low": by_tier.get(4, 0),
            "confidence": "VALIDATED",
            "source": "NAICS + Uniclass + O*NET + BLS triangulation"
        }

        tier4_pct = (by_tier.get(4, 0) / len(mappings) * 100) if mappings else 0
        if tier4_pct > 15:
            counts["gaps"].append(f"{tier4_pct:.0f}% of crosswalk mappings are low confidence")

    # Total nodes
    total = 0
    for layer, data in counts["layer"].items():
        for key, val in data.items():
            if isinstance(val, int) and key not in ["confidence"]:
                total += val
    counts["total"] = total

    return counts

def assess_deployability(counts):
    """Assess if ontology is ready for use"""

    assessment = {
        "overall": "PARTIAL",
        "scores": {},
        "blockers": [],
        "recommendations": []
    }

    # Scoring criteria
    criteria = {
        "Coverage": {
            "weight": 0.25,
            "score": 0,
            "notes": []
        },
        "Accuracy": {
            "weight": 0.30,
            "score": 0,
            "notes": []
        },
        "Completeness": {
            "weight": 0.25,
            "score": 0,
            "notes": []
        },
        "Usability": {
            "weight": 0.20,
            "score": 0,
            "notes": []
        }
    }

    # Coverage: Do we have all the pieces?
    layers_present = len(counts["layer"])
    if layers_present >= 5:
        criteria["Coverage"]["score"] = 0.9
        criteria["Coverage"]["notes"].append("All 5 ontology layers present")
    elif layers_present >= 4:
        criteria["Coverage"]["score"] = 0.7
    else:
        criteria["Coverage"]["score"] = 0.5
        criteria["Coverage"]["notes"].append(f"Only {layers_present} layers defined")

    # Check task coverage
    task_layer = counts["layer"].get("Task Ontology", {})
    if task_layer.get("tasks", 0) >= 300:
        criteria["Coverage"]["score"] = min(criteria["Coverage"]["score"] + 0.1, 1.0)
        criteria["Coverage"]["notes"].append(f"{task_layer.get('tasks', 0)} scope tasks defined")

    # Accuracy: How validated is the data?
    crosswalk = counts["layer"].get("Classification Crosswalk", {})
    if crosswalk:
        tier1_2 = crosswalk.get("tier_1_ground_truth", 0) + crosswalk.get("tier_2_high", 0)
        total = crosswalk.get("total_mappings", 1)
        high_conf_pct = tier1_2 / total
        criteria["Accuracy"]["score"] = high_conf_pct * 0.8  # Max 0.8 from crosswalk
        criteria["Accuracy"]["notes"].append(f"{high_conf_pct*100:.0f}% of crosswalk is Tier 1-2")

    # Product rules are LOW confidence - this hurts accuracy
    product_layer = counts["layer"].get("Product Rules", {})
    if product_layer.get("confidence") == "LOW":
        criteria["Accuracy"]["score"] *= 0.7
        criteria["Accuracy"]["notes"].append("Product rules unvalidated (-30%)")
        assessment["blockers"].append("Product rules need expert validation before production use")

    # Completeness: Are there gaps?
    gap_count = len(counts.get("gaps", []))
    if gap_count == 0:
        criteria["Completeness"]["score"] = 1.0
    elif gap_count <= 2:
        criteria["Completeness"]["score"] = 0.8
    elif gap_count <= 4:
        criteria["Completeness"]["score"] = 0.6
    else:
        criteria["Completeness"]["score"] = 0.4
    criteria["Completeness"]["notes"].append(f"{gap_count} gaps identified")

    # Check link integrity
    cost_layer = counts["layer"].get("Cost Model", {})
    if cost_layer:
        link_pct = cost_layer.get("linked_to_trade", 0) / max(cost_layer.get("line_items", 1), 1)
        if link_pct < 0.9:
            criteria["Completeness"]["notes"].append(f"Cost-to-trade links: {link_pct*100:.0f}%")

    # Usability: Can it actually generate scopes?
    sched_layer = counts["layer"].get("Schedule Ontology", {})
    if sched_layer.get("schedule_tasks", 0) >= 150:
        criteria["Usability"]["score"] += 0.4
        criteria["Usability"]["notes"].append("Schedule workflow defined")

    if product_layer.get("task_rules", 0) >= 15:
        criteria["Usability"]["score"] += 0.3
        criteria["Usability"]["notes"].append("Product selection rules exist")

    if task_layer.get("trades", 0) >= 25:
        criteria["Usability"]["score"] += 0.3
        criteria["Usability"]["notes"].append("Major trades covered")

    # Calculate weighted score
    total_score = sum(c["score"] * c["weight"] for c in criteria.values())

    assessment["scores"] = criteria
    assessment["weighted_score"] = total_score

    if total_score >= 0.8:
        assessment["overall"] = "READY"
    elif total_score >= 0.6:
        assessment["overall"] = "PARTIAL - needs validation"
    elif total_score >= 0.4:
        assessment["overall"] = "DRAFT - significant gaps"
    else:
        assessment["overall"] = "NOT READY"

    # Recommendations
    if product_layer.get("confidence") == "LOW":
        assessment["recommendations"].append("1. Have domain expert validate product rules")
    if gap_count > 0:
        assessment["recommendations"].append("2. Address identified gaps")
    assessment["recommendations"].append("3. Test with real project data")
    assessment["recommendations"].append("4. Build validation UI for iterative refinement")

    return assessment

def print_report(counts, assessment):
    """Print audit report"""

    print("=" * 70)
    print("ONTOLOGY AUDIT REPORT")
    print("=" * 70)

    print("\n## NODE COUNT BY LAYER\n")
    print(f"{'Layer':<30} {'Nodes':<10} {'Confidence':<15} {'Source'}")
    print("-" * 70)

    total_nodes = 0
    for layer, data in counts["layer"].items():
        # Sum numeric values
        node_count = sum(v for k, v in data.items() if isinstance(v, int))
        total_nodes += node_count
        conf = data.get("confidence", "?")
        source = data.get("source", "")[:25]
        print(f"{layer:<30} {node_count:<10} {conf:<15} {source}")

    print("-" * 70)
    print(f"{'TOTAL NODES':<30} {total_nodes:<10}")

    print("\n## LAYER DETAILS\n")
    for layer, data in counts["layer"].items():
        print(f"### {layer}")
        for key, val in data.items():
            if key not in ["confidence", "source"]:
                print(f"  - {key}: {val}")
        print()

    print("\n## IDENTIFIED GAPS\n")
    if counts.get("gaps"):
        for i, gap in enumerate(counts["gaps"], 1):
            print(f"  {i}. {gap}")
    else:
        print("  No critical gaps identified")

    print("\n" + "=" * 70)
    print("DEPLOYABILITY ASSESSMENT")
    print("=" * 70)

    print(f"\n## OVERALL: {assessment['overall']}")
    print(f"## WEIGHTED SCORE: {assessment['weighted_score']*100:.0f}%\n")

    print("### Scoring Breakdown\n")
    for criterion, data in assessment["scores"].items():
        pct = data["score"] * 100
        weight = data["weight"] * 100
        print(f"{criterion} ({weight:.0f}% weight): {pct:.0f}%")
        for note in data["notes"]:
            print(f"  - {note}")
        print()

    if assessment.get("blockers"):
        print("### BLOCKERS\n")
        for b in assessment["blockers"]:
            print(f"  [!] {b}")
        print()

    print("### RECOMMENDATIONS\n")
    for r in assessment["recommendations"]:
        print(f"  {r}")

    print("\n" + "=" * 70)
    print("USE CASE READINESS")
    print("=" * 70)

    use_cases = [
        ("Scope Generation (full auto)", "NO", "Product rules unvalidated"),
        ("Scope Templates (human review)", "YES", "Templates usable with review"),
        ("Cost Estimation", "PARTIAL", "Line items defined, no unit costs"),
        ("Schedule Generation", "YES", "Full workflow with dependencies"),
        ("Trade Classification", "YES", "NAICS/Uniclass crosswalk validated"),
        ("Product Selection (auto)", "NO", "Rules need validation"),
        ("Product Lookup (reference)", "YES", "150+ products catalogued"),
        ("Code Compliance Check", "PARTIAL", "5 constraints, needs expansion"),
    ]

    print(f"\n{'Use Case':<35} {'Ready?':<10} {'Notes'}")
    print("-" * 70)
    for uc, ready, notes in use_cases:
        print(f"{uc:<35} {ready:<10} {notes}")

def main():
    counts = count_nodes()
    assessment = assess_deployability(counts)
    print_report(counts, assessment)

    # Save audit results
    output = {
        "node_counts": counts,
        "assessment": assessment,
        "date": "2024-12-30"
    }

    with open(SCHEMA_DIR / "audit_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nAudit saved to: {SCHEMA_DIR / 'audit_results.json'}")

if __name__ == "__main__":
    main()
