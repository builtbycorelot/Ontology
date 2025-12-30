"""
Build Unified Task Ontology
Merges all scope sources + adds missing trades + creates cost model
"""

import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("data")
SCHEMA_DIR = Path("schema")
SCHEMA_DIR.mkdir(exist_ok=True)

# =============================================================================
# TRADE DEFINITIONS (Complete with NAICS/Uniclass mappings)
# =============================================================================

TRADES = {
    # === GENERAL CONDITIONS ===
    "ALL": {
        "naics": "23",
        "naics_name": "Construction (General Conditions)",
        "uniclass_ss": ["Ss_20", "Ss_25"],
        "cost_category": "General Conditions",
        "description": "General requirements applying to all trades"
    },

    # === PRE-CONSTRUCTION / PROFESSIONAL SERVICES ===
    "Due Diligence": {
        "naics": "541310",
        "naics_name": "Architectural Services",
        "uniclass_ss": ["Ac_05", "Ac_10"],
        "cost_category": "Soft Costs > Professional Fees",
        "description": "Site research, feasibility, entitlements"
    },
    "Site Plan": {
        "naics": "541370",
        "naics_name": "Surveying and Mapping Services",
        "uniclass_ss": ["Ac_05_10", "Ac_10_70"],
        "cost_category": "Soft Costs > Engineering",
        "description": "Civil engineering and site design"
    },
    "Surveying": {
        "naics": "541370",
        "naics_name": "Surveying and Mapping Services",
        "uniclass_ss": ["Ac_15_10"],
        "cost_category": "Soft Costs > Engineering",
        "description": "Land surveying and staking"
    },
    "3rd Party Inspection": {
        "naics": "541350",
        "naics_name": "Building Inspection Services",
        "uniclass_ss": ["Ac_35"],
        "cost_category": "Soft Costs > Professional Fees",
        "description": "Third party inspections and testing"
    },
    "Engineering": {
        "naics": "541330",
        "naics_name": "Engineering Services",
        "uniclass_ss": ["Ac_10"],
        "cost_category": "Soft Costs > Engineering",
        "description": "Structural, MEP, civil engineering design"
    },

    # === SITE WORK ===
    "Lot Development": {
        "naics": "238910",
        "naics_name": "Site Preparation Contractors",
        "uniclass_ss": ["Ss_15", "Ss_20_10"],
        "cost_category": "Hard Costs > Site Costs",
        "description": "Clearing, grading, earthwork"
    },
    "Landscaping": {
        "naics": "561730",
        "naics_name": "Landscaping Services",
        "uniclass_ss": ["Ss_15_10", "EF_25"],
        "cost_category": "Hard Costs > Site Costs",
        "description": "Planting, irrigation, hardscape"
    },
    "Utilities to site": {
        "naics": "237110",
        "naics_name": "Water and Sewer Line Construction",
        "uniclass_ss": ["Ss_55", "Ss_65"],
        "cost_category": "Hard Costs > Site Costs",
        "description": "Utility connections to property"
    },
    "Driveway": {
        "naics": "238910",
        "naics_name": "Site Preparation Contractors",
        "uniclass_ss": ["Ss_15_30", "Ss_32_50"],
        "cost_category": "Hard Costs > Site Costs",
        "description": "Driveway base and paving"
    },
    "Paving": {
        "naics": "238990",
        "naics_name": "All Other Specialty Trade Contractors",
        "uniclass_ss": ["Ss_32_50"],
        "cost_category": "Hard Costs > Site Costs",
        "description": "Asphalt and concrete paving"
    },

    # === STRUCTURAL ===
    "Concrete": {
        "naics": "238110",
        "naics_name": "Poured Concrete Foundation and Structure Contractors",
        "uniclass_ss": ["Ss_30", "Ss_32"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Foundations, slabs, flatwork"
    },
    "Masonry": {
        "naics": "238140",
        "naics_name": "Masonry Contractors",
        "uniclass_ss": ["Ss_25_12", "Ss_30_40"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Block, brick, stone work"
    },
    "Steel Structure": {
        "naics": "238120",
        "naics_name": "Structural Steel and Precast Concrete Contractors",
        "uniclass_ss": ["Ss_25_11", "Ss_30_20"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Structural steel framing and erection"
    },
    "Framer": {
        "naics": "238130",
        "naics_name": "Framing Contractors",
        "uniclass_ss": ["Ss_25_10", "Ss_25_13"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Wood framing, sheathing, blocking"
    },

    # === BUILDING ENVELOPE ===
    "Roofing": {
        "naics": "238160",
        "naics_name": "Roofing Contractors",
        "uniclass_ss": ["Ss_25_30"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Roof systems and flashing"
    },
    "Siding": {
        "naics": "238170",
        "naics_name": "Siding Contractors",
        "uniclass_ss": ["Ss_25_20", "Ss_25_20_70"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Cladding, soffit, fascia"
    },
    "Exterior Features": {
        "naics": "238170",
        "naics_name": "Siding Contractors",
        "uniclass_ss": ["Ss_25_20", "Ss_25_20_50"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "PVC trim, column wraps, exterior millwork"
    },
    "EIFS": {
        "naics": "238170",
        "naics_name": "Siding Contractors",
        "uniclass_ss": ["Ss_25_20_30", "Ss_40_20"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Exterior Insulation Finish System (stucco)"
    },
    "Windows": {
        "naics": "238150",
        "naics_name": "Glass and Glazing Contractors",
        "uniclass_ss": ["Ss_25_80", "Pr_25_80"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Window units and installation"
    },
    "Exterior Doors": {
        "naics": "238350",
        "naics_name": "Finish Carpentry Contractors",
        "uniclass_ss": ["Ss_25_30_30", "Pr_25_30"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Entry doors, patio doors"
    },
    "Store Front": {
        "naics": "238150",
        "naics_name": "Glass and Glazing Contractors",
        "uniclass_ss": ["Ss_25_80_80", "Ss_25_30_80"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Commercial glazing systems"
    },
    "Garage Doors": {
        "naics": "238290",
        "naics_name": "Other Building Equipment Contractors",
        "uniclass_ss": ["Ss_25_30_33", "Pr_25_30_33"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Overhead doors and operators"
    },
    "Guttering": {
        "naics": "238170",
        "naics_name": "Siding Contractors",
        "uniclass_ss": ["Ss_55_70_38", "Pr_65_54_38"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Gutters and downspouts"
    },

    # === MEP (Mechanical, Electrical, Plumbing) ===
    "HVAC": {
        "naics": "238220",
        "naics_name": "Plumbing, Heating, and Air-Conditioning Contractors",
        "uniclass_ss": ["Ss_60", "Ss_60_40", "Ss_60_30"],
        "cost_category": "Hard Costs > Building MEP",
        "description": "Heating, ventilation, air conditioning"
    },
    "Plumbing": {
        "naics": "238220",
        "naics_name": "Plumbing, Heating, and Air-Conditioning Contractors",
        "uniclass_ss": ["Ss_55", "Ss_60"],
        "cost_category": "Hard Costs > Building MEP",
        "description": "Water supply and drainage systems"
    },
    "Electrical": {
        "naics": "238210",
        "naics_name": "Electrical Contractors",
        "uniclass_ss": ["Ss_70", "Ss_70_30", "Ss_70_80"],
        "cost_category": "Hard Costs > Building MEP",
        "description": "Power, lighting, low voltage"
    },
    "Sprinkler": {
        "naics": "238220",
        "naics_name": "Plumbing, Heating, and Air-Conditioning Contractors",
        "uniclass_ss": ["Ss_55_40", "Ss_70_80_30"],
        "cost_category": "Hard Costs > Building MEP",
        "description": "Fire suppression systems"
    },
    "Electrical Fixtures": {
        "naics": "238210",
        "naics_name": "Electrical Contractors",
        "uniclass_ss": ["Ss_70_40", "Pr_70_40"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Light fixtures, ceiling fans"
    },

    # === INTERIOR FINISHES ===
    "Insulation": {
        "naics": "238310",
        "naics_name": "Drywall and Insulation Contractors",
        "uniclass_ss": ["Ss_25_35", "Ss_25_35_30"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Thermal and acoustic insulation"
    },
    "Drywall": {
        "naics": "238310",
        "naics_name": "Drywall and Insulation Contractors",
        "uniclass_ss": ["Ss_25_50", "Ss_25_50_20"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Gypsum board, tape, finish"
    },
    "Paint": {
        "naics": "238320",
        "naics_name": "Painting and Wall Covering Contractors",
        "uniclass_ss": ["Ss_40", "Ss_40_10", "Ss_40_30"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Interior and exterior painting"
    },
    "Tile": {
        "naics": "238340",
        "naics_name": "Tile and Terrazzo Contractors",
        "uniclass_ss": ["Ss_25_45_88", "Ss_32_20_95"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Ceramic, porcelain, stone tile"
    },
    "Flooring": {
        "naics": "238330",
        "naics_name": "Flooring Contractors",
        "uniclass_ss": ["Ss_25_45", "Ss_32_20"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Carpet, LVP, hardwood, vinyl"
    },
    "Trim": {
        "naics": "238350",
        "naics_name": "Finish Carpentry Contractors",
        "uniclass_ss": ["Ss_25_50_55", "Ss_25_50_65"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Interior doors, casings, baseboards"
    },
    "Cabinets": {
        "naics": "238350",
        "naics_name": "Finish Carpentry Contractors",
        "uniclass_ss": ["Ss_25_50_15", "Pr_35_10"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Kitchen and bath cabinetry"
    },
    "Countertops": {
        "naics": "238350",
        "naics_name": "Finish Carpentry Contractors",
        "uniclass_ss": ["Ss_25_50_25", "Pr_35_93_15"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Stone, solid surface, laminate tops"
    },
    "Stairs": {
        "naics": "238350",
        "naics_name": "Finish Carpentry Contractors",
        "uniclass_ss": ["Ss_25_50_80", "Pr_25_71_82"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Stair treads, risers, stringers"
    },
    "Rails": {
        "naics": "238350",
        "naics_name": "Finish Carpentry Contractors",
        "uniclass_ss": ["Ss_25_50_65", "Pr_25_71_05"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Handrails, guardrails, balusters"
    },
    "Fireplace": {
        "naics": "238290",
        "naics_name": "Other Building Equipment Contractors",
        "uniclass_ss": ["Ss_60_10_30", "Pr_70_60_30"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Fireplace units and surrounds"
    },

    # === FIXTURES & EQUIPMENT ===
    "Plumbing Fixtures": {
        "naics": "238220",
        "naics_name": "Plumbing, Heating, and Air-Conditioning Contractors",
        "uniclass_ss": ["Pr_40_50", "Pr_40_50_96"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Sinks, toilets, tubs, faucets"
    },
    "Appliances": {
        "naics": "443141",
        "naics_name": "Household Appliance Stores",
        "uniclass_ss": ["Pr_40_20"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Kitchen appliances"
    },
    "Hardware": {
        "naics": "238350",
        "naics_name": "Finish Carpentry Contractors",
        "uniclass_ss": ["Pr_20_31", "Pr_35_47"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Door hardware, bath accessories"
    },
    "Mirrors": {
        "naics": "238150",
        "naics_name": "Glass and Glazing Contractors",
        "uniclass_ss": ["Pr_40_30_54", "Ss_25_80"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Bath and decorative mirrors"
    },
    "Shower Door": {
        "naics": "238150",
        "naics_name": "Glass and Glazing Contractors",
        "uniclass_ss": ["Pr_25_30_78", "Ss_25_80"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Glass shower enclosures"
    },
    "Shelving": {
        "naics": "238350",
        "naics_name": "Finish Carpentry Contractors",
        "uniclass_ss": ["Pr_35_93_78", "Ss_25_50"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Closet and utility shelving"
    },

    # === SPECIALTY ===
    "Termite Treatment": {
        "naics": "561710",
        "naics_name": "Exterminating and Pest Control Services",
        "uniclass_ss": ["Ac_45_70"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Pre-treatment and warranties"
    },
    "Cleaning": {
        "naics": "561720",
        "naics_name": "Janitorial Services",
        "uniclass_ss": ["Ac_45", "Ac_50"],
        "cost_category": "Hard Costs > Building Finish",
        "description": "Construction and final cleaning"
    },

    # === MATERIALS / SUPPLY ===
    "Lumber": {
        "naics": "423310",
        "naics_name": "Lumber Wholesalers",
        "uniclass_ss": ["Pr_20_93"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Framing lumber package"
    },
    "Trusses": {
        "naics": "321214",
        "naics_name": "Truss Manufacturing",
        "uniclass_ss": ["Pr_20_93_95", "Ss_25_13"],
        "cost_category": "Hard Costs > Building Shell",
        "description": "Roof and floor trusses"
    }
}

# =============================================================================
# COST MODEL STRUCTURE
# =============================================================================

COST_MODEL = {
    "_meta": {
        "description": "Construction Cost Model Schema",
        "version": "1.0",
        "date": "2024-12-30"
    },

    "financial_metrics": {
        "roi": {"description": "Return on Investment", "formula": "profit / total_cost"},
        "roe": {"description": "Return on Equity", "formula": "profit / required_equity", "note": "Typically at 70% LTV"},
        "ltv": {"description": "Loan to Value", "default": 0.70},
        "cost_per_sf": {"description": "Total Cost / Square Feet"},
        "hard_cost_per_sf": {"description": "Hard Costs / Square Feet"},
        "sales_price_per_sf": {"description": "Target or actual sales price / SF"},
        "market_lease_rate_sf": {"description": "Market lease rate per SF (commercial)"}
    },

    "cost_categories": {
        "Hard Costs": {
            "description": "Direct construction costs",
            "subcategories": {
                "Site Costs": {
                    "line_items": [
                        {"code": "HC-SITE-001", "name": "Lot Cost", "type": "fixed"},
                        {"code": "HC-SITE-002", "name": "Easements", "type": "fixed"},
                        {"code": "HC-SITE-010", "name": "Clearing", "trade": "Lot Development"},
                        {"code": "HC-SITE-011", "name": "Demolition", "trade": "Lot Development"},
                        {"code": "HC-SITE-012", "name": "Construction Entrance", "trade": "Lot Development"},
                        {"code": "HC-SITE-013", "name": "Dig Basement", "trade": "Lot Development"},
                        {"code": "HC-SITE-014", "name": "Rough Grade", "trade": "Lot Development"},
                        {"code": "HC-SITE-015", "name": "Erosion Control", "trade": "Lot Development"},
                        {"code": "HC-SITE-016", "name": "Private Ln Access", "trade": "Lot Development"},
                        {"code": "HC-SITE-017", "name": "SWM Facility", "trade": "Lot Development"},
                        {"code": "HC-SITE-020", "name": "Final Grade", "trade": "Landscaping"},
                        {"code": "HC-SITE-021", "name": "Seed & Straw", "trade": "Landscaping"},
                        {"code": "HC-SITE-022", "name": "Sod", "trade": "Landscaping"},
                        {"code": "HC-SITE-023", "name": "Plants & Mulch", "trade": "Landscaping"},
                        {"code": "HC-SITE-030", "name": "Septic / Sewer", "trade": "Utilities to site"},
                        {"code": "HC-SITE-031", "name": "Manhole & Water Tap", "trade": "Utilities to site"},
                        {"code": "HC-SITE-032", "name": "Run to Manhole", "trade": "Utilities to site"},
                        {"code": "HC-SITE-033", "name": "Well & Water Hookup Labor", "trade": "Utilities to site"},
                        {"code": "HC-SITE-034", "name": "Utilities Installation", "trade": "Utilities to site"},
                        {"code": "HC-SITE-040", "name": "Paving / Driveway", "trade": "Paving"},
                        {"code": "HC-SITE-041", "name": "Lead Walk & Pads", "trade": "Concrete"},
                        {"code": "HC-SITE-050", "name": "Signage", "trade": None},
                        {"code": "HC-SITE-051", "name": "Lawn Maintenance", "trade": "Landscaping"},
                        {"code": "HC-SITE-060", "name": "Dumpster", "trade": None},
                        {"code": "HC-SITE-061", "name": "Pump Truck", "trade": "Concrete"}
                    ]
                },
                "Building Shell": {
                    "line_items": [
                        {"code": "HC-SHELL-001", "name": "Concrete (Foundation & Walls)", "trade": "Concrete"},
                        {"code": "HC-SHELL-002", "name": "Gravel & Plastic", "trade": "Concrete"},
                        {"code": "HC-SHELL-003", "name": "Waterproofing / Draintile", "trade": "Concrete"},
                        {"code": "HC-SHELL-004", "name": "Termite Treatment", "trade": "Termite Treatment"},
                        {"code": "HC-SHELL-010", "name": "Steel Structure", "trade": "Steel Structure"},
                        {"code": "HC-SHELL-011", "name": "Erection Contractor", "trade": "Steel Structure"},
                        {"code": "HC-SHELL-012", "name": "Masonry", "trade": "Masonry"},
                        {"code": "HC-SHELL-020", "name": "Framing Sub-Contractor", "trade": "Framer"},
                        {"code": "HC-SHELL-021", "name": "Framing Material", "trade": "Lumber"},
                        {"code": "HC-SHELL-022", "name": "Trusses", "trade": "Trusses"},
                        {"code": "HC-SHELL-023", "name": "Roof Sheathing", "trade": "Framer"},
                        {"code": "HC-SHELL-030", "name": "EIFS", "trade": "EIFS"},
                        {"code": "HC-SHELL-031", "name": "Exterior Features", "trade": "Exterior Features"},
                        {"code": "HC-SHELL-032", "name": "Exterior Doors", "trade": "Exterior Doors"},
                        {"code": "HC-SHELL-033", "name": "Store Front", "trade": "Store Front"},
                        {"code": "HC-SHELL-034", "name": "Windows", "trade": "Windows"},
                        {"code": "HC-SHELL-035", "name": "Garage Doors", "trade": "Garage Doors"},
                        {"code": "HC-SHELL-040", "name": "Roofing", "trade": "Roofing"},
                        {"code": "HC-SHELL-041", "name": "Siding", "trade": "Siding"},
                        {"code": "HC-SHELL-042", "name": "Guttering", "trade": "Guttering"}
                    ]
                },
                "Building MEP": {
                    "line_items": [
                        {"code": "HC-MEP-001", "name": "HVAC", "trade": "HVAC"},
                        {"code": "HC-MEP-002", "name": "Plumbing", "trade": "Plumbing"},
                        {"code": "HC-MEP-003", "name": "Electrical", "trade": "Electrical"},
                        {"code": "HC-MEP-004", "name": "Sprinkler", "trade": "Sprinkler"}
                    ]
                },
                "Building Finish": {
                    "line_items": [
                        {"code": "HC-FIN-001", "name": "Insulation", "trade": "Insulation"},
                        {"code": "HC-FIN-002", "name": "Drywall", "trade": "Drywall"},
                        {"code": "HC-FIN-003", "name": "Interior Trim", "trade": "Trim"},
                        {"code": "HC-FIN-004", "name": "Stairs", "trade": "Stairs"},
                        {"code": "HC-FIN-005", "name": "Rails", "trade": "Rails"},
                        {"code": "HC-FIN-006", "name": "Paint", "trade": "Paint"},
                        {"code": "HC-FIN-010", "name": "Cabinets", "trade": "Cabinets"},
                        {"code": "HC-FIN-011", "name": "Countertops", "trade": "Countertops"},
                        {"code": "HC-FIN-012", "name": "Flooring", "trade": "Flooring"},
                        {"code": "HC-FIN-020", "name": "Fireplace", "trade": "Fireplace"},
                        {"code": "HC-FIN-030", "name": "Electrical Fixtures", "trade": "Electrical Fixtures"},
                        {"code": "HC-FIN-031", "name": "Plumbing Fixtures", "trade": "Plumbing Fixtures"},
                        {"code": "HC-FIN-032", "name": "Appliances", "trade": "Appliances"},
                        {"code": "HC-FIN-033", "name": "Hardware / Knobs", "trade": "Hardware"},
                        {"code": "HC-FIN-034", "name": "Mirrors", "trade": "Mirrors"},
                        {"code": "HC-FIN-035", "name": "Shelves", "trade": "Shelving"},
                        {"code": "HC-FIN-036", "name": "Shower Door", "trade": "Shower Door"},
                        {"code": "HC-FIN-040", "name": "Cleaning", "trade": "Cleaning"},
                        {"code": "HC-FIN-099", "name": "Miscellaneous", "trade": None}
                    ]
                }
            }
        },
        "Soft Costs": {
            "description": "Indirect project costs",
            "subcategories": {
                "Professional Fees": {
                    "line_items": [
                        {"code": "SC-PROF-001", "name": "Management Fee", "percent_of": "hard_costs", "typical": 0.03},
                        {"code": "SC-PROF-002", "name": "3rd Party Concrete Inspections", "trade": "3rd Party Inspection"},
                        {"code": "SC-PROF-003", "name": "Condo Organization", "type": "fixed"}
                    ]
                },
                "Engineering": {
                    "line_items": [
                        {"code": "SC-ENG-001", "name": "Site Plan", "trade": "Site Plan"},
                        {"code": "SC-ENG-002", "name": "Surveying", "trade": "Surveying"},
                        {"code": "SC-ENG-003", "name": "Sewer Design", "trade": "Engineering"},
                        {"code": "SC-ENG-004", "name": "Foundation Design", "trade": "Engineering"},
                        {"code": "SC-ENG-005", "name": "Slab Design", "trade": "Engineering"},
                        {"code": "SC-ENG-006", "name": "Research", "trade": "Due Diligence"},
                        {"code": "SC-ENG-010", "name": "Property Corners", "trade": "Surveying"},
                        {"code": "SC-ENG-011", "name": "Rough Stake", "trade": "Surveying"},
                        {"code": "SC-ENG-012", "name": "Good Stake", "trade": "Surveying"},
                        {"code": "SC-ENG-013", "name": "LOC", "trade": "Surveying"},
                        {"code": "SC-ENG-014", "name": "Wall Check", "trade": "Surveying"}
                    ]
                },
                "Permits & Fees": {
                    "line_items": [
                        {"code": "SC-PERM-001", "name": "Permits & County Fees (Bld & Health)", "type": "fixed"},
                        {"code": "SC-PERM-002", "name": "Erosion & VDOT Bond", "type": "fixed"},
                        {"code": "SC-PERM-003", "name": "Sewer Availability Fee", "type": "fixed"},
                        {"code": "SC-PERM-004", "name": "Water Availability Fee", "type": "fixed"}
                    ]
                },
                "Sales & Closing": {
                    "line_items": [
                        {"code": "SC-SALE-001", "name": "R/E Commission", "percent_of": "sales_price", "typical": 0.05},
                        {"code": "SC-SALE-002", "name": "Settlement Fees", "type": "fixed"},
                        {"code": "SC-SALE-003", "name": "Home Warranty", "percent_of": "sales_price", "typical": 0.00225}
                    ]
                },
                "Finance & Insurance": {
                    "line_items": [
                        {"code": "SC-FIN-001", "name": "Bank Fees (1 pt)", "percent_of": "loan_amount", "typical": 0.01},
                        {"code": "SC-FIN-002", "name": "Interest", "note": "Typically 6 months carry"},
                        {"code": "SC-FIN-003", "name": "Builders Risk Insurance", "type": "fixed"},
                        {"code": "SC-FIN-004", "name": "R/E Taxes", "type": "fixed"}
                    ]
                }
            }
        }
    }
}

# =============================================================================
# MERGE ALL SCOPE DATA
# =============================================================================

def load_existing_scopes():
    """Load all existing scope files"""
    all_scopes = []

    # Load seed_scopes.json
    seed_file = DATA_DIR / "seed_scopes.json"
    if seed_file.exists():
        with open(seed_file) as f:
            data = json.load(f)
            all_scopes.extend(data.get("scopes", []))
            print(f"Loaded {len(data.get('scopes', []))} scopes from seed_scopes.json")

    # Load seed_scopes_v2.json
    seed_v2_file = DATA_DIR / "seed_scopes_v2.json"
    if seed_v2_file.exists():
        with open(seed_v2_file) as f:
            data = json.load(f)
            all_scopes.extend(data.get("additional_scopes", []))
            print(f"Loaded {len(data.get('additional_scopes', []))} scopes from seed_scopes_v2.json")

    # Load generated_scopes.json
    gen_file = DATA_DIR / "generated_scopes.json"
    if gen_file.exists():
        with open(gen_file) as f:
            data = json.load(f)
            all_scopes.extend(data.get("flat_scopes", []))
            print(f"Loaded {len(data.get('flat_scopes', []))} scopes from generated_scopes.json")

    return all_scopes


def classify_scope(task_text):
    """Classify scope as standard or parameterized"""
    task_lower = task_text.lower()

    # Patterns indicating plan-specific (parameterized)
    parameterized_patterns = [
        r'\(\d+\)',           # (5) - quantity in parens
        r'\d+\s*(x|\'|\")',   # 5x, 5', 5"
        r'per\s+plan',        # per plan
        r'master\s+br',       # specific room
        r'great\s+room',      # specific room
        r'cathedral',         # specific feature
        r'if\s+applicable',   # conditional
        r'where\s+required',  # conditional
    ]

    import re
    for pattern in parameterized_patterns:
        if re.search(pattern, task_lower):
            return "parameterized"

    return "standard"


def build_unified_ontology():
    """Build the complete unified ontology"""

    # Load all scopes
    all_scopes = load_existing_scopes()
    print(f"\nTotal scopes loaded: {len(all_scopes)}")

    # Deduplicate by task text
    seen_tasks = set()
    unique_scopes = []
    for scope in all_scopes:
        task_key = (scope.get('trade', ''), scope.get('task', ''))
        if task_key not in seen_tasks:
            seen_tasks.add(task_key)
            unique_scopes.append(scope)

    print(f"Unique scopes after dedup: {len(unique_scopes)}")

    # Build structured ontology
    ontology = {
        "_meta": {
            "description": "Unified Construction Task Ontology",
            "version": "1.0",
            "date": "2024-12-30",
            "sources": [
                "User seed data (medium confidence)",
                "O*NET 30.1 Database (CC BY 4.0)",
                "Industry knowledge"
            ],
            "license": "CC BY-SA 4.0"
        },
        "trades": {},
        "summary": {
            "total_trades": 0,
            "total_phases": 0,
            "total_tasks": 0,
            "standard_tasks": 0,
            "parameterized_tasks": 0
        }
    }

    # Organize by trade
    by_trade = defaultdict(lambda: defaultdict(list))

    for scope in unique_scopes:
        trade = scope.get('trade', 'Unknown')
        phase = scope.get('phase') or 'General'
        task = scope.get('task', '')

        if task:
            classification = classify_scope(task)
            by_trade[trade][phase].append({
                "task": task,
                "type": classification
            })

    # Build final structure
    standard_count = 0
    param_count = 0
    phase_count = 0

    for trade_name, phases in by_trade.items():
        trade_def = TRADES.get(trade_name, {
            "naics": "UNMAPPED",
            "naics_name": "",
            "uniclass_ss": [],
            "cost_category": "Unknown",
            "description": ""
        })

        trade_entry = {
            "naics": trade_def.get("naics", "UNMAPPED"),
            "naics_name": trade_def.get("naics_name", ""),
            "uniclass_ss": trade_def.get("uniclass_ss", []),
            "cost_category": trade_def.get("cost_category", ""),
            "description": trade_def.get("description", ""),
            "phases": {}
        }

        for phase_name, tasks in phases.items():
            phase_count += 1
            phase_tasks = []
            for t in tasks:
                phase_tasks.append(t)
                if t["type"] == "standard":
                    standard_count += 1
                else:
                    param_count += 1

            trade_entry["phases"][phase_name] = {
                "tasks": phase_tasks,
                "task_count": len(phase_tasks)
            }

        ontology["trades"][trade_name] = trade_entry

    ontology["summary"]["total_trades"] = len(ontology["trades"])
    ontology["summary"]["total_phases"] = phase_count
    ontology["summary"]["total_tasks"] = standard_count + param_count
    ontology["summary"]["standard_tasks"] = standard_count
    ontology["summary"]["parameterized_tasks"] = param_count

    return ontology


def main():
    print("=" * 60)
    print("BUILDING UNIFIED ONTOLOGY")
    print("=" * 60)

    # Build unified ontology
    ontology = build_unified_ontology()

    # Save task ontology
    ontology_file = SCHEMA_DIR / "task_ontology.json"
    with open(ontology_file, "w") as f:
        json.dump(ontology, f, indent=2)
    print(f"\nSaved task ontology to: {ontology_file}")

    # Save cost model
    cost_file = SCHEMA_DIR / "cost_model.json"
    with open(cost_file, "w") as f:
        json.dump(COST_MODEL, f, indent=2)
    print(f"Saved cost model to: {cost_file}")

    # Save trade definitions separately for reference
    trades_file = SCHEMA_DIR / "trade_definitions.json"
    trades_output = {
        "_meta": {
            "description": "Trade definitions with NAICS/Uniclass mappings",
            "date": "2024-12-30"
        },
        "trades": TRADES
    }
    with open(trades_file, "w") as f:
        json.dump(trades_output, f, indent=2)
    print(f"Saved trade definitions to: {trades_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total trades: {ontology['summary']['total_trades']}")
    print(f"Total phases: {ontology['summary']['total_phases']}")
    print(f"Total tasks: {ontology['summary']['total_tasks']}")
    print(f"  - Standard: {ontology['summary']['standard_tasks']}")
    print(f"  - Parameterized: {ontology['summary']['parameterized_tasks']}")

    print("\n" + "-" * 60)
    print("TRADES BY COST CATEGORY")
    print("-" * 60)

    by_category = defaultdict(list)
    for trade_name, trade_def in TRADES.items():
        cat = trade_def.get("cost_category", "Unknown")
        by_category[cat].append(trade_name)

    for cat in sorted(by_category.keys()):
        print(f"\n{cat}:")
        for trade in sorted(by_category[cat]):
            naics = TRADES[trade].get("naics", "?")
            print(f"  - {trade} ({naics})")

    print("\n" + "-" * 60)
    print("COST MODEL STRUCTURE")
    print("-" * 60)
    for main_cat, main_data in COST_MODEL["cost_categories"].items():
        print(f"\n{main_cat}:")
        for sub_cat, sub_data in main_data["subcategories"].items():
            count = len(sub_data["line_items"])
            print(f"  {sub_cat}: {count} line items")


if __name__ == "__main__":
    main()
