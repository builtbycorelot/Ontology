"""
Generate Scope Templates for Missing Trades from O*NET Tasks
"""

import json
from pathlib import Path

OUTPUT = Path("data/generated_scopes.json")

# O*NET tasks extracted and converted to scope format
GENERATED_SCOPES = {
    "Electrical": {
        "naics": "238210",
        "naics_name": "Electrical Contractors",
        "uniclass_ss": ["Ss_70", "Ss_70_30", "Ss_70_80"],
        "phases": {
            "R/I": [
                "Prepare sketches or follow blueprints to determine the location of wiring or equipment",
                "Plan layout and installation of electrical wiring, equipment, or fixtures, based on job specifications and local codes",
                "Place conduit, pipes, or tubing, inside designated partitions, walls, or other concealed areas",
                "Pull insulated wires or cables through the conduit to complete circuits between boxes",
                "Fasten small metal or plastic boxes to walls to house electrical switches or outlets",
                "Install ground leads and connect power cables to equipment, such as motors",
                "Connect wires to circuit breakers, transformers, or other components",
            ],
            "Trim": [
                "Assemble, install, test, or maintain electrical wiring, equipment, appliances, apparatus, or fixtures",
                "Install switches, outlets, and fixtures per plans and code",
                "Install cover plates on all devices",
                "Label panel directory",
            ],
            "Final": [
                "Test electrical systems or continuity of circuits using testing devices (ohmmeters, voltmeters)",
                "Inspect electrical systems, equipment, or components to ensure compliance with codes",
                "Diagnose malfunctioning systems, apparatus, or components using test equipment",
                "Repair or replace wiring, equipment, or fixtures as needed",
            ],
            "Service": [
                "Install service entrance, meter base, and main panel",
                "Coordinate with utility company for meter installation",
                "Provide temporary power pole (if required)",
            ]
        },
        "products": ["Pr_65_70", "Pr_65_50_15", "Pr_65_50_96", "Pr_65_52_70"]  # Wire, conduit, panels, boxes
    },

    "HVAC": {
        "naics": "238220",
        "naics_name": "Plumbing, Heating, and Air-Conditioning Contractors",
        "uniclass_ss": ["Ss_60", "Ss_60_40", "Ss_60_30", "Ss_60_70"],
        "phases": {
            "R/I": [
                "Install ductwork per plans and code, seal all joints with mastic",
                "Install supply and return boots at designated locations",
                "Run refrigerant lines for split systems",
                "Install condensate drain lines with proper slope",
                "Furnish and install flue pipe for gas furnace",
                "Install gas piping to furnace location (if applicable)",
            ],
            "Equipment Set": [
                "Set furnace/air handler in designated location",
                "Set condenser on pad with proper clearances",
                "Connect refrigerant lines and pressure test system",
                "Connect condensate drain to approved location",
                "Connect gas line to furnace (if applicable)",
                "Install thermostat wiring",
            ],
            "Trim": [
                "Install registers, grilles, and diffusers",
                "Install thermostat(s) at designated locations",
                "Install filter grille or filter rack",
                "Seal all duct penetrations at fire-rated assemblies",
            ],
            "Final": [
                "Charge system with refrigerant per manufacturer specs",
                "Test and balance airflow at all registers",
                "Program thermostat and verify operation",
                "Provide homeowner orientation on system operation",
                "Complete startup checklist and warranty registration",
            ]
        },
        "products": ["Pr_70_65", "Pr_70_70", "Pr_70_60_30", "Pr_70_60_35"]  # Ductwork, equipment, controls
    },

    "Drywall": {
        "naics": "238310",
        "naics_name": "Drywall and Insulation Contractors",
        "uniclass_ss": ["Ss_25_50", "Ss_25_50_20", "Ss_25_50_65"],
        "phases": {
            "Stock": [
                "Count and verify quantity of drywall deliveries",
                "Distribute drywall throughout structure for hanging",
                "Protect materials from moisture damage",
            ],
            "Hang": [
                "Read blueprints to determine methods of installation and material requirements",
                "Measure and mark surfaces to lay out work according to blueprints",
                "Fit and fasten wallboard or drywall into position on wood or metal frameworks using screws",
                "Hang drywall panels on metal frameworks of walls and ceilings",
                "Measure and cut openings in panels for electrical outlets, windows, vents, plumbing",
                "Install horizontal and vertical metal or wooden studs to frames as needed",
                "Cut and install corner bead at all outside corners",
            ],
            "Tape/Finish": [
                "Spread sealing compound between boards or over cracks, holes, nail heads, or screw heads",
                "Press paper tape over joints to embed tape into sealing compound",
                "Spread and smooth cementing material over tape using trowels or floating machines",
                "Apply additional coats to fill in holes and make surfaces smooth",
                "Sand rough spots of dried cement between applications of compounds",
                "Sand to smooth finish ready for paint (Level 4 finish)",
            ],
            "Texture": [
                "Apply texturizing compounds to walls or ceilings using trowels, brushes, rollers, or spray guns",
                "Match existing texture on repair areas",
                "Apply orange peel, knockdown, or smooth finish per specs",
            ]
        },
        "products": ["Pr_25_71_28", "Pr_25_71_29", "Pr_25_71_25"]  # Drywall, tape, compound
    },

    "Painting": {
        "naics": "238320",
        "naics_name": "Painting and Wall Covering Contractors",
        "uniclass_ss": ["Ss_40", "Ss_40_10", "Ss_40_30"],
        "phases": {
            "Prep": [
                "Cover surfaces with dropcloths or masking tape and paper to protect surfaces",
                "Fill holes, cracks, and joints with caulk, putty, plaster, or other fillers",
                "Sand surfaces between coats for proper adhesion",
                "Remove hardware, covers, and fixtures before painting",
                "Clean surfaces to remove dust, dirt, grease, or other contaminants",
            ],
            "Prime": [
                "Apply primer coat to all new drywall surfaces",
                "Spot prime nail holes and repairs",
                "Apply stain-blocking primer where needed",
                "Prime all bare wood surfaces",
            ],
            "Paint": [
                "Apply paint, stain, or coating using brushes, rollers, or spray equipment",
                "Apply two coats of finish paint to walls and ceilings (or per specs)",
                "Cut in at corners, edges, and trim",
                "Roll or spray field areas for uniform coverage",
                "Apply trim paint to all doors, casings, and millwork",
            ],
            "Final": [
                "Touch up all scratches, holidays, and imperfections",
                "Remove all masking and dropcloths",
                "Clean paint from windows, hardware, and fixtures",
                "Reinstall all hardware and covers",
            ]
        },
        "products": ["Pr_45_30", "Pr_45_30_65", "Pr_45_30_50"]  # Paint, primer, coatings
    },

    "Tile": {
        "naics": "238340",
        "naics_name": "Tile and Terrazzo Contractors",
        "uniclass_ss": ["Ss_25_45_88", "Ss_25_45", "Ss_32_20_95"],
        "phases": {
            "Prep": [
                "Study blueprints and examine surface to determine amount of material needed",
                "Remove any old tile, grout and adhesive using chisels and scrapers",
                "Prepare surfaces for tiling by attaching cement board or waterproof membrane",
                "Level substrate and allow to dry",
                "Waterproof shower/tub areas with approved membrane system",
            ],
            "Layout": [
                "Measure and mark surfaces to be tiled, following blueprints",
                "Determine and implement the best layout to achieve desired pattern",
                "Establish level lines and reference points",
                "Dry-fit tile to verify layout before setting",
            ],
            "Set": [
                "Mix, apply, and spread thinset mortar or adhesive using trowels",
                "Apply mortar to tile back, position tile, and press into place",
                "Align and straighten tile using levels, squares, and straightedges",
                "Cut and shape tile to fit around obstacles using hand and power cutting tools",
                "Install tile edge trim and transitions",
                "Allow tile to set before grouting (24 hours typical)",
            ],
            "Grout": [
                "Mix grout per manufacturer instructions",
                "Apply grout to joints using rubber float",
                "Finish and dress the joints and wipe excess grout using damp sponge",
                "Apply sealer to make grout stain and water resistant",
                "Caulk all change-of-plane joints with color-matched silicone",
            ]
        },
        "products": ["Pr_25_75", "Pr_25_75_90", "Pr_25_75_40"]  # Tile, grout, thinset
    },

    "Insulation": {
        "naics": "238310",
        "naics_name": "Drywall and Insulation Contractors",
        "uniclass_ss": ["Ss_25_35", "Ss_25_35_30", "Ss_25_35_90"],
        "phases": {
            "Batt Insulation": [
                "Read blueprints and select appropriate insulation based on R-value requirements",
                "Measure and cut insulation for covering surfaces",
                "Fit, wrap, staple, or glue insulating materials to structures using hand tools",
                "Install faced batt insulation in exterior walls with vapor barrier facing conditioned space",
                "Install unfaced batt insulation in interior walls for sound attenuation",
                "Insulate rim joists and cantilevered areas",
            ],
            "Blown Insulation": [
                "Fill blower hoppers with insulating materials",
                "Distribute insulating materials evenly into small spaces using blowers and hose attachments",
                "Move controls to regulate flow of materials through nozzles",
                "Achieve specified depth/R-value in attic spaces",
                "Install depth markers per code requirements",
            ],
            "Air Sealing": [
                "Seal all penetrations at top and bottom plates",
                "Seal around electrical boxes and plumbing penetrations",
                "Install foam baffles at eaves to maintain ventilation",
                "Cover, seal, or finish insulated surfaces with plastic covers or tape",
            ],
            "Inspection": [
                "Verify insulation installation meets energy code requirements",
                "Provide insulation certificate with R-values",
                "Coordinate with energy rater for HERS inspection (if required)",
            ]
        },
        "products": ["Pr_25_50_35", "Pr_25_50_10", "Pr_25_50_45"]  # Batt, blown, foam insulation
    }
}

def generate_flat_scopes():
    """Generate flat scope list matching user's format"""
    flat_scopes = []

    for trade_name, trade_data in GENERATED_SCOPES.items():
        for phase_name, tasks in trade_data["phases"].items():
            for task in tasks:
                flat_scopes.append({
                    "trade": trade_name,
                    "phase": phase_name,
                    "task": task
                })

    return flat_scopes

def main():
    flat_scopes = generate_flat_scopes()

    output = {
        "_meta": {
            "source": "Generated from O*NET 30.1 Database tasks",
            "license": "CC BY 4.0 (O*NET)",
            "attribution": "U.S. Department of Labor, Employment and Training Administration",
            "description": "Scope templates for trades not in user seed data",
            "date": "2024-12-30"
        },
        "trade_details": GENERATED_SCOPES,
        "flat_scopes": flat_scopes,
        "summary": {
            "trades_generated": len(GENERATED_SCOPES),
            "total_scopes": len(flat_scopes)
        }
    }

    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 60)
    print("GENERATED SCOPE TEMPLATES")
    print("=" * 60)
    print(f"\nTrades generated: {len(GENERATED_SCOPES)}")
    print(f"Total scope items: {len(flat_scopes)}")

    print("\n" + "-" * 60)
    for trade_name, trade_data in GENERATED_SCOPES.items():
        phase_count = len(trade_data["phases"])
        task_count = sum(len(tasks) for tasks in trade_data["phases"].values())
        print(f"\n{trade_name}")
        print(f"  NAICS: {trade_data['naics']} - {trade_data['naics_name']}")
        print(f"  Uniclass: {', '.join(trade_data['uniclass_ss'])}")
        print(f"  Phases: {phase_count}, Tasks: {task_count}")
        for phase, tasks in trade_data["phases"].items():
            print(f"    {phase}: {len(tasks)} tasks")

    print(f"\nSaved to: {OUTPUT}")

    # Also output in user's format for easy copy-paste
    print("\n" + "=" * 60)
    print("COPY-PASTE FORMAT (matching your seed data)")
    print("=" * 60)
    for scope in flat_scopes:
        phase_str = f"    {scope['phase']}" if scope['phase'] else ""
        print(f"{scope['trade']}{phase_str}    {scope['task']}")

if __name__ == "__main__":
    main()
