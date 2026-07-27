"""Seed the database with Distribution-domain use cases from the utility AI whitepaper.

Run once after `init_schema()`:
    python seed.py
"""
from __future__ import annotations

import db


SEED_USE_CASES: list[dict] = [
    # ---- Phase 1 (foundational) ----
    {
        "title": "Outage Detection & Prediction",
        "status": "Qualify",
        "business_problem": (
            "Slow detection of outages drives long SAIDI minutes, wasted truck rolls, "
            "and customer dissatisfaction. AMI last-gasp signals are not integrated with OMS today."
        ),
        "solution_description": (
            "Integrate AMI last-gasp / power-on events with OMS and SCADA to detect, predict, "
            "and pre-stage for outages. Foundational to FLISR and storm response."
        ),
        "ai_capability": "Anomaly Detection",
        "business_area": "Distribution Operations",
        "value_stream": "Distribution",
        "annual_value_low_m": 30, "annual_value_high_m": 62,
        "complexity": 3,
        "time_to_value_low_mo": 9, "time_to_value_high_mo": 15,
        "data_sources": "AMI (last-gasp/power-on), OMS, SCADA, weather, historical outage records",
        "prerequisites": "AMI + OMS integration; clean GIS network model",
    },
    {
        "title": "Fault Location, Isolation, and Service Restoration (FLISR)",
        "status": "Qualify",
        "business_problem": (
            "Manual fault location and restoration takes 8+ SAIDI minutes per event and consumes "
            "500,000 crew hours annually."
        ),
        "solution_description": (
            "Use AMI, OMS, GIS, and recloser/switch telemetry to automatically locate, isolate, "
            "and restore faults. Direct extension of outage detection."
        ),
        "ai_capability": "Optimization",
        "business_area": "Distribution Operations",
        "value_stream": "Distribution",
        "annual_value_low_m": 25, "annual_value_high_m": 52,
        "complexity": 3,
        "time_to_value_low_mo": 12, "time_to_value_high_mo": 18,
        "data_sources": "AMI, OMS, GIS network model, SCADA (reclosers/switches), fault indicators",
        "prerequisites": "Outage Detection & Prediction; clean GIS connectivity model",
    },
    {
        "title": "Predictive Maintenance for OH & UG Assets",
        "status": "Discovery",
        "business_problem": (
            "200,000 distribution transformers with a 5% annual failure rate drive emergency O&M "
            "premiums and customer interruptions."
        ),
        "solution_description": (
            "Combine inspection records, AMI power-quality data, transformer loading, GIS, weather, "
            "and failure history to predict failures and shift from reactive to planned maintenance."
        ),
        "ai_capability": "Predictive Maintenance",
        "business_area": "Asset Management",
        "value_stream": "Distribution",
        "annual_value_low_m": 22, "annual_value_high_m": 45,
        "complexity": 3,
        "time_to_value_low_mo": 15, "time_to_value_high_mo": 24,
        "data_sources": "Inspection records, AMI power quality, transformer loading, GIS, weather, failure history",
        "prerequisites": "AMI integration; historical inspection / failure records digitized",
    },
    {
        "title": "Load Forecasting at Feeder Level",
        "status": "Discovery",
        "business_problem": (
            "System-level load forecasts miss feeder-level variation, leading to over-built capital "
            "and stalled DER interconnection studies."
        ),
        "solution_description": (
            "Granular AMI-driven load forecasts per feeder, enabling capacity planning, DER readiness, "
            "and EV-charging planning. Critical input to hosting capacity analysis."
        ),
        "ai_capability": "Forecasting",
        "business_area": "Distribution Planning",
        "value_stream": "Distribution",
        "annual_value_low_m": 12, "annual_value_high_m": 25,
        "complexity": 3,
        "time_to_value_low_mo": 12, "time_to_value_high_mo": 18,
        "data_sources": "AMI interval data, weather, DER interconnection records, GIS feeder maps, EV charging data",
        "prerequisites": "AMI interval data aggregated by feeder and transformer",
    },
    {
        "title": "Grid Reliability Monitoring",
        "status": "Prioritize & Plan",
        "business_problem": (
            "Reliability reporting is manual; 15 analysts spend 50% of their time on SAIDI/SAIFI/CAIDI "
            "compilation rather than analysis."
        ),
        "solution_description": (
            "Reporting and dashboard layer on top of AMI/SCADA/OMS data. Low incremental complexity once "
            "Phase 1 data is in place. Drives regulatory reporting automation and targeted investment."
        ),
        "ai_capability": "Other",
        "business_area": "Regulatory & Reliability",
        "value_stream": "Distribution",
        "annual_value_low_m": 8, "annual_value_high_m": 18,
        "complexity": 2,
        "time_to_value_low_mo": 6, "time_to_value_high_mo": 9,
        "data_sources": "AMI, SCADA, OMS, power quality meters, GIS, reliability indices",
        "prerequisites": "Phase 1 AMI/OMS/SCADA integration",
    },

    # ---- Phase 2 (proactive optimization) ----
    {
        "title": "DER & EV Charging Management",
        "status": "Demand",
        "business_problem": (
            "Uncoordinated DER and EV charging is overloading distribution transformers and forcing "
            "expensive capacity upgrades."
        ),
        "solution_description": (
            "Manage bidirectional power flows and EV-charging impacts using AMI, DER telemetry, and "
            "feeder models. Enables FERC Order 2222 market participation."
        ),
        "ai_capability": "Optimization",
        "business_area": "Distribution Operations",
        "value_stream": "Distribution",
        "annual_value_low_m": 30, "annual_value_high_m": 65,
        "complexity": 4,
        "time_to_value_low_mo": 18, "time_to_value_high_mo": 24,
        "data_sources": "AMI, DER telemetry, EV charger data, feeder models, weather, interconnection records",
        "prerequisites": "Load Forecasting at Feeder Level; DER telemetry feeds",
    },
    {
        "title": "Grid Model Clean-up & Connectivity Inference",
        "status": "Discovery",
        "business_problem": (
            "15-25% GIS connectivity error rate causes failed work orders, inaccurate outage "
            "locations, and FLISR misfires."
        ),
        "solution_description": (
            "Use ML to infer and correct connectivity errors in GIS / network models by reconciling "
            "GIS with AMI, SCADA, and as-built records."
        ),
        "ai_capability": "Anomaly Detection",
        "business_area": "GIS & Asset Records",
        "value_stream": "Distribution",
        "annual_value_low_m": 8, "annual_value_high_m": 18,
        "complexity": 3,
        "time_to_value_low_mo": 12, "time_to_value_high_mo": 18,
        "data_sources": "GIS, AMI, SCADA, as-built records, work orders, connectivity models",
        "prerequisites": "Phase 1 data quality issues triaged",
    },
    {
        "title": "Storm Impact Prediction & Crew Pre-Staging",
        "status": "Demand",
        "business_problem": (
            "Major storms cost $100M/yr in restoration; crews are staged reactively rather than "
            "predictively."
        ),
        "solution_description": (
            "Predict storm damage by asset vulnerability and weather forecast, pre-stage crews and "
            "materials, coordinate mutual aid more efficiently."
        ),
        "ai_capability": "Forecasting",
        "business_area": "Emergency Response",
        "value_stream": "Distribution",
        "annual_value_low_m": 22, "annual_value_high_m": 48,
        "complexity": 3,
        "time_to_value_low_mo": 12, "time_to_value_high_mo": 18,
        "data_sources": "Weather forecasts, historical storm damage, asset vulnerability, GIS, crew/equipment locations",
        "prerequisites": "Outage Detection & Prediction; Grid Reliability Monitoring",
    },
    {
        "title": "Voltage Optimization & Loss Reduction",
        "status": "Demand",
        "business_problem": (
            "Technical losses run ~5% of 5,000 MW system load; voltage violations and reactive-power "
            "costs are addressable but unmanaged."
        ),
        "solution_description": (
            "Optimize volt/VAR settings across the distribution network using AMI voltage data and "
            "capacitor/regulator telemetry. Enables conservation voltage reduction (CVR)."
        ),
        "ai_capability": "Optimization",
        "business_area": "Distribution Operations",
        "value_stream": "Distribution",
        "annual_value_low_m": 18, "annual_value_high_m": 38,
        "complexity": 3,
        "time_to_value_low_mo": 12, "time_to_value_high_mo": 18,
        "data_sources": "AMI voltage data, SCADA, capacitor bank status, regulator settings, feeder models",
        "prerequisites": "Clean AMI voltage data; volt/VAR device telemetry",
    },
    {
        "title": "Hosting Capacity Analysis",
        "status": "Demand",
        "business_problem": (
            "DER interconnection cycle time is 3-6 months; engineering studies are a bottleneck."
        ),
        "solution_description": (
            "Quantify where the grid can accept new DERs without upgrades. Feeder-by-feeder hosting "
            "capacity maps cut interconnection studies to 2-4 weeks."
        ),
        "ai_capability": "Optimization",
        "business_area": "DER Interconnection",
        "value_stream": "Distribution",
        "annual_value_low_m": 15, "annual_value_high_m": 32,
        "complexity": 4,
        "time_to_value_low_mo": 12, "time_to_value_high_mo": 18,
        "data_sources": "Feeder models, AMI, DER interconnection data, load forecasts, protection settings, thermal limits",
        "prerequisites": "Load Forecasting at Feeder Level",
    },

    # ---- Phase 3 (risk mitigation / advanced automation) ----
    {
        "title": "Distribution Network Digital Twin",
        "status": "Demand",
        "business_problem": (
            "No simulation environment to test switching, DER scenarios, or planning decisions "
            "before they hit the live grid."
        ),
        "solution_description": (
            "Full distribution digital twin combining AMI, SCADA, GIS, DER telemetry, weather, and "
            "real-time switching state. Enables operational simulation, planning, and real-time optimization."
        ),
        "ai_capability": "Optimization",
        "business_area": "Distribution Engineering",
        "value_stream": "Distribution",
        "annual_value_low_m": 35, "annual_value_high_m": 72,
        "complexity": 5,
        "time_to_value_low_mo": 48, "time_to_value_high_mo": 60,
        "data_sources": "AMI, SCADA, GIS, DER telemetry, weather, real-time switching state, customer data",
        "prerequisites": "All Phase 1-2 distribution data; clean GIS model",
    },
    {
        "title": "Automated Work Package Generation for Crews",
        "status": "Demand",
        "business_problem": (
            "200 planners spend 50% of their time manually assembling work packages; 5,000 jobs/yr "
            "are delayed by gaps."
        ),
        "solution_description": (
            "AI assembles complete work packages (instructions, materials, permits, safety plans) "
            "from work orders, GIS, asset condition, crew skills, and material availability."
        ),
        "ai_capability": "Generative AI / Agents",
        "business_area": "Work Management",
        "value_stream": "Distribution",
        "annual_value_low_m": 18, "annual_value_high_m": 38,
        "complexity": 4,
        "time_to_value_low_mo": 36, "time_to_value_high_mo": 48,
        "data_sources": "Work orders, GIS, asset condition, crew skills/certifications, material availability, schedules",
        "prerequisites": "Mature work-management data; integrated material/skills systems",
    },
    {
        "title": "Automated Work Order Creation & Crew Dispatching",
        "status": "Demand",
        "business_problem": (
            "50 dispatchers spend 37% of their time on manual work order creation; crew utilization "
            "and overtime remain stubbornly suboptimal."
        ),
        "solution_description": (
            "Close the loop from fault detection through automated dispatch using OMS, the digital "
            "twin, crew locations, and priority models."
        ),
        "ai_capability": "Generative AI / Agents",
        "business_area": "Dispatch Operations",
        "value_stream": "Distribution",
        "annual_value_low_m": 25, "annual_value_high_m": 52,
        "complexity": 5,
        "time_to_value_low_mo": 48, "time_to_value_high_mo": 60,
        "data_sources": "OMS, digital twin, crew locations, skills, equipment, traffic, priority models",
        "prerequisites": "Distribution Network Digital Twin",
    },
    {
        "title": "Self-healing Distribution Networks",
        "status": "Demand",
        "business_problem": (
            "Sustained outages still drive SAIDI minutes that customers and regulators no longer accept."
        ),
        "solution_description": (
            "Ultimate distribution automation: the network detects, isolates, and restores faults "
            "autonomously by orchestrating FLISR, DERs, switching, and protection."
        ),
        "ai_capability": "Optimization",
        "business_area": "Distribution Operations",
        "value_stream": "Distribution",
        "annual_value_low_m": 45, "annual_value_high_m": 92,
        "complexity": 5,
        "time_to_value_low_mo": 60, "time_to_value_high_mo": 72,
        "data_sources": "Digital twin, FLISR automation, DER orchestration, real-time switching, protection coordination",
        "prerequisites": "Distribution Network Digital Twin; Automated Work Order Creation; FLISR",
    },
    {
        "title": "Hyper-local Probabilistic Risk Pricing",
        "status": "Demand",
        "business_problem": (
            "$300M annual distribution capital is allocated with limited asset-level risk insight; "
            "5 high-consequence failures per year are currently preventable."
        ),
        "solution_description": (
            "Price risk at the individual asset/segment level using probabilistic failure and "
            "consequence models. Enables surgical investment decisions and insurance optimization."
        ),
        "ai_capability": "Predictive Maintenance",
        "business_area": "Asset Management",
        "value_stream": "Distribution",
        "annual_value_low_m": 20, "annual_value_high_m": 42,
        "complexity": 4,
        "time_to_value_low_mo": 48, "time_to_value_high_mo": 60,
        "data_sources": "Asset condition, weather exposure, vegetation, customer density, failure probability, consequence models",
        "prerequisites": "Predictive Maintenance baseline; asset condition data integrated",
    },
]


def seed(force: bool = False) -> int:
    """Insert seed records. Skips if table already has rows unless force=True."""
    existing = db.list_use_cases()
    if existing and not force:
        print(f"Already have {len(existing)} records; skipping seed. Use force=True to reseed.")
        return 0

    if force and existing:
        with db.connect() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM use_cases")
            conn.commit()

    n = 0
    for rec in SEED_USE_CASES:
        rec = {**rec, "category": "Distribution"}
        db.create_use_case(rec)
        n += 1
    print(f"Seeded {n} Distribution use cases.")
    return n


if __name__ == "__main__":
    import sys
    db.init_schema()
    force = "--force" in sys.argv
    seed(force=force)
