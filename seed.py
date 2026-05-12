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
        "phase": "Phase 1",
        "status": "Under Review",
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
        "value_components": "SAIDI reduction via faster detection ($10M); Crew dispatch efficiency ($2.25M); Predictive pre-staging savings ($20M); OMS accuracy improvement ($1.6M)",
        "key_assumptions": "Current SAIDI of 90 min; Phase 1 reduces by 5 min; 50,000 annual truck rolls; 15% reduction in unnecessary rolls; $100M annual storm restoration costs",
        "roi_timeline": "9-15 months",
        "prerequisites": "AMI + OMS integration; clean GIS network model",
    },
    {
        "title": "Fault Location, Isolation, and Service Restoration (FLISR)",
        "phase": "Phase 1",
        "status": "Under Review",
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
        "value_components": "SAIDI reduction from automated isolation ($16M); Restoration labor reduction ($8.5M); CSAT penalty avoidance ($3M); Reduced customer compensation claims ($750K)",
        "key_assumptions": "8 SAIDI min reduced via automated switching vs. manual; 500K annual crew hours on restoration; FLISR effectiveness depends on clean GIS model",
        "roi_timeline": "12-18 months",
        "prerequisites": "Outage Detection & Prediction; clean GIS connectivity model",
    },
    {
        "title": "Predictive Maintenance for OH & UG Assets",
        "phase": "Phase 1",
        "status": "Refinement",
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
        "value_components": "Transformer failure avoidance ($3M); UG cable failure avoidance ($3.75M); Planned vs. emergency maintenance premium ($18M); Transformer life extension ($1.575M)",
        "key_assumptions": "200K distribution transformers; 5% annual failure rate; $300M/yr distribution O&M budget; 250 UG cable failures/yr, reduce by 50",
        "roi_timeline": "15-24 months",
        "prerequisites": "AMI integration; historical inspection / failure records digitized",
    },
    {
        "title": "Load Forecasting at Feeder Level",
        "phase": "Phase 1",
        "status": "Refinement",
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
        "value_components": "Deferred distribution capital ($9M); EV charging infra optimization ($525K); DER interconnection backlog reduction ($750K); DR targeting efficiency ($1M)",
        "key_assumptions": "$300M annual distribution capital budget; 3,000 distribution feeders; 500 DER interconnection applications/yr; EV penetration +20%/yr",
        "roi_timeline": "12-18 months",
        "prerequisites": "AMI interval data aggregated by feeder and transformer",
    },
    {
        "title": "Grid Reliability Monitoring",
        "phase": "Phase 1",
        "status": "Approved",
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
        "value_components": "Regulatory reporting automation ($2.03M); Targeted capital investment efficiency ($15M); Regulatory penalty avoidance ($2M); JD Power ranking improvement ($1M)",
        "key_assumptions": "15 analysts at 50% time on manual reliability reporting; reliability benchmarks tied to $1-5M rate case outcomes; 5% efficiency on $300M capital budget",
        "roi_timeline": "6-9 months",
        "prerequisites": "Phase 1 AMI/OMS/SCADA integration",
    },

    # ---- Phase 2 (proactive optimization) ----
    {
        "title": "DER & EV Charging Management",
        "phase": "Phase 2",
        "status": "Backlog",
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
        "value_components": "Distribution infra deferral ($7M); EV charging infra deferral ($7.5M); Wholesale market value from DER aggregation ($7.3M); Curtailment avoidance ($7.5M); DR revenue ($3.65M)",
        "key_assumptions": "500 MW total DER installed; 80,000 EVs (10% of 800K residential); 200 transformers at risk without managed charging",
        "roi_timeline": "18-24 months",
        "prerequisites": "Load Forecasting at Feeder Level; DER telemetry feeds",
    },
    {
        "title": "Grid Model Clean-up & Connectivity Inference",
        "phase": "Phase 2",
        "status": "Refinement",
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
        "value_components": "Outage location accuracy ($3M); FLISR accuracy ($2.5M); DER interconnection accuracy ($625K); Field crew efficiency ($1M); Engineering planning accuracy ($600K)",
        "key_assumptions": "15-25% GIS connectivity error rate; 500 DER interconnection studies/yr; 10,000 failed work orders/yr from bad connectivity",
        "roi_timeline": "12-18 months",
        "prerequisites": "Phase 1 data quality issues triaged",
    },
    {
        "title": "Storm Impact Prediction & Crew Pre-Staging",
        "phase": "Phase 2",
        "status": "Backlog",
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
        "value_components": "Pre-staged crews faster restoration ($20M); Crew overtime reduction ($9.56M); Pre-staged material savings ($3M); CSAT ($2M); Mutual aid efficiency ($2M)",
        "key_assumptions": "5 major storms/yr at $100M total restoration cost; pre-staging cuts restoration time 20%; 500 restoration crews; $10M annual mutual aid costs",
        "roi_timeline": "12-18 months",
        "prerequisites": "Outage Detection & Prediction; Grid Reliability Monitoring",
    },
    {
        "title": "Voltage Optimization & Loss Reduction",
        "phase": "Phase 2",
        "status": "Backlog",
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
        "value_components": "Energy loss reduction 1-3% ($7.5M); VAR cost reduction ($2M); Voltage violation reduction ($1M); Equipment life extension ($1.05M); CVR ($10M)",
        "key_assumptions": "5,000 MW avg system load; 5% technical losses (250 MW); CVR factor 0.7; voltage cut 1.5% within limits",
        "roi_timeline": "12-18 months",
        "prerequisites": "Clean AMI voltage data; volt/VAR device telemetry",
    },
    {
        "title": "Hosting Capacity Analysis",
        "phase": "Phase 2",
        "status": "Backlog",
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
        "value_components": "Interconnection study cost reduction ($2M); Faster approvals revenue ($5M); Infra deferral via optimal siting ($3.5M); Feeder upgrade avoidance ($20M); Regulatory compliance ($2M)",
        "key_assumptions": "500 DER applications/yr +20%/yr; cycle time 3-6 months -> 2-4 weeks; 10 feeder upgrades/yr deferrable",
        "roi_timeline": "12-18 months",
        "prerequisites": "Load Forecasting at Feeder Level",
    },

    # ---- Phase 3 (risk mitigation / advanced automation) ----
    {
        "title": "Distribution Network Digital Twin",
        "phase": "Phase 3",
        "status": "Backlog",
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
        "value_components": "SAIDI reduction via twin automation ($30M); Planning cost reduction ($8M); Switching optimization ($4M); Energy loss reduction ($876K); DER hosting value ($10M)",
        "key_assumptions": "4+ years of Phase 1-2 data; clean GIS model; +15 SAIDI min eliminated beyond Phase 1-2; 100K switching ops/yr",
        "roi_timeline": "48-60 months",
        "prerequisites": "All Phase 1-2 distribution data; clean GIS model",
    },
    {
        "title": "Automated Work Package Generation for Crews",
        "phase": "Phase 3",
        "status": "Backlog",
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
        "value_components": "Planning labor savings ($17M); Crew productivity ($5.3M); Permit cycle time reduction ($2M); Safety plan quality ($1.5M); Material availability ($4.5M)",
        "key_assumptions": "200 planners at 50% on manual package assembly; 5,000 field crews x 30 min/day pre-job prep; 5,000 jobs/yr delayed",
        "roi_timeline": "36-48 months",
        "prerequisites": "Mature work-management data; integrated material/skills systems",
    },
    {
        "title": "Automated Work Order Creation & Crew Dispatching",
        "phase": "Phase 3",
        "status": "Backlog",
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
        "value_components": "SAIDI reduction faster dispatch ($10M); Dispatcher efficiency ($3.19M); Crew utilization ($8.5M); Overtime reduction ($4.5M); Mutual aid coordination ($10M)",
        "key_assumptions": "Validated digital twin; 50 dispatchers at 37% manual time; 5,000 field crews; $30M annual distribution crew overtime",
        "roi_timeline": "48-60 months",
        "prerequisites": "Distribution Network Digital Twin",
    },
    {
        "title": "Self-healing Distribution Networks",
        "phase": "Phase 3",
        "status": "Backlog",
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
        "value_components": "SAIDI elimination ($40M); Crew overtime reduction ($9M); Regulatory performance ($5M); CSAT premium ($5M); Capital deferral ($3.5M)",
        "key_assumptions": "Requires digital twin, automated dispatch, FLISR foundation; self-healing handles 60% of fault events; cumulative SAIDI reduction across Phase 3: 40+ min",
        "roi_timeline": "60-72 months",
        "prerequisites": "Distribution Network Digital Twin; Automated Work Order Creation; FLISR",
    },
    {
        "title": "Hyper-local Probabilistic Risk Pricing",
        "phase": "Phase 3",
        "status": "Backlog",
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
        "value_components": "Capital investment precision ($9M); Insurance optimization ($4M); Regulatory capital justification ($600K); Catastrophic failure prevention ($10M); Litigation avoidance ($3M)",
        "key_assumptions": "$300M annual distribution capital; 3% allocation improvement; 5 high-consequence failures/yr preventable; 3 litigation cases/yr at $1M avg",
        "roi_timeline": "48-60 months",
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
