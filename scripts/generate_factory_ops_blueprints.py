import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = "src/capsules/blueprints/factory_ops"

# Define the 27 Areas
AREAS = [
    {
        "code": 1,
        "slug": "raw_material_sourcing",
        "name": "Raw Material Sourcing Capsule",
        "description": "Optimizes mining and ore operations with EDCoC sensors and RND1 extraction planning.",
        "connectors": [{"type": "sensor", "name": "drill_telemetry"}, {"type": "api", "name": "seismic_data"}],
        "models": [{"id": "rnd1_extraction", "type": "optimization"}, {"id": "shadow_twin_mine", "type": "simulation"}],
        "proofs": [{"type": "Sustainability", "claim": "ore_recovery_rate"}]
    },
    {
        "code": 2,
        "slug": "rare_earth_refining",
        "name": "Metallurgical Intelligence Capsule",
        "description": "Optimizes refining processes and minimizes reagent usage via chemical kinetics models.",
        "connectors": [{"type": "lims", "name": "lab_analysis"}, {"type": "sensor", "name": "reactor_temp"}],
        "models": [{"id": "kinetics_solver", "type": "simulation"}, {"id": "m2n2_alloy_opt", "type": "evolutionary"}],
        "proofs": [{"type": "Compliance", "claim": "purity_level"}]
    },
    {
        "code": 3,
        "slug": "powder_processing",
        "name": "Feedstock Integrity Capsule",
        "description": "Ensures powder consistency and quality for additive manufacturing.",
        "connectors": [{"type": "sensor", "name": "particle_size_analyzer"}, {"type": "env", "name": "humidity_log"}],
        "models": [{"id": "ace_drift_detector", "type": "inference"}, {"id": "flowability_sim", "type": "simulation"}],
        "proofs": [{"type": "Quality", "claim": "particle_distribution"}]
    },
    {
        "code": 4,
        "slug": "casting_foundry",
        "name": "Digital Foundry Capsule",
        "description": "Predicts defects and optimizes mold filling using CFD and MHD simulations.",
        "connectors": [{"type": "sensor", "name": "thermocouples"}, {"type": "camera", "name": "thermal_cam"}],
        "models": [{"id": "cfd_mold_fill", "type": "simulation"}, {"id": "defect_predictor", "type": "inference"}],
        "proofs": [{"type": "Quality", "claim": "porosity_free"}]
    },
    {
        "code": 5,
        "slug": "forming_rolling",
        "name": "Smart Forming Capsule",
        "description": "Optimizes rolling and extrusion parameters to maximize throughput and yield.",
        "connectors": [{"type": "plc", "name": "roller_speed"}, {"type": "sensor", "name": "load_cell"}],
        "models": [{"id": "stress_strain_sim", "type": "simulation"}, {"id": "rnd1_process_opt", "type": "optimization"}],
        "proofs": [{"type": "Efficiency", "claim": "yield_improvement"}]
    },
    {
        "code": 6,
        "slug": "machining_fabrication",
        "name": "Precision Fabrication Capsule",
        "description": "Auto-generates toolpaths and detects tool wear using vibration analysis.",
        "connectors": [{"type": "sensor", "name": "vibration_accel"}, {"type": "cnc", "name": "gcode_stream"}],
        "models": [{"id": "tool_wear_pred", "type": "inference"}, {"id": "cam_optimizer", "type": "optimization"}],
        "proofs": [{"type": "Quality", "claim": "tolerance_adherence"}]
    },
    {
        "code": 7,
        "slug": "joining_welding",
        "name": "Weld Quality Capsule",
        "description": "Ensures zero-defect welds through real-time arc monitoring and physics modeling.",
        "connectors": [{"type": "sensor", "name": "arc_voltage"}, {"type": "robot", "name": "arm_telemetry"}],
        "models": [{"id": "plasma_physics_sim", "type": "simulation"}, {"id": "weld_defect_detect", "type": "inference"}],
        "proofs": [{"type": "Safety", "claim": "weld_integrity"}]
    },
    {
        "code": 8,
        "slug": "surface_treatment",
        "name": "Surface Engineering Capsule",
        "description": "Optimizes coating thickness and adhesion via thin-film growth models.",
        "connectors": [{"type": "sensor", "name": "thickness_gauge"}, {"type": "env", "name": "bath_chemistry"}],
        "models": [{"id": "film_growth_sim", "type": "simulation"}, {"id": "adhesion_predictor", "type": "inference"}],
        "proofs": [{"type": "Durability", "claim": "corrosion_resistance"}]
    },
    {
        "code": 9,
        "slug": "polymers_composites",
        "name": "Composite Intelligence Capsule",
        "description": "Optimizes curing cycles and mold flow for polymer and composite parts.",
        "connectors": [{"type": "sensor", "name": "dielectric_cure"}, {"type": "sensor", "name": "pressure_transducer"}],
        "models": [{"id": "viscoelastic_sim", "type": "simulation"}, {"id": "cure_cycle_opt", "type": "optimization"}],
        "proofs": [{"type": "Quality", "claim": "cure_completeness"}]
    },
    {
        "code": 10,
        "slug": "electronics_pcb",
        "name": "PCB Flow Capsule",
        "description": "Optimizes reflow profiles and detects placement defects in electronics assembly.",
        "connectors": [{"type": "aoi", "name": "inspection_results"}, {"type": "oven", "name": "reflow_profile"}],
        "models": [{"id": "thermal_reflow_sim", "type": "simulation"}, {"id": "solder_joint_pred", "type": "inference"}],
        "proofs": [{"type": "Reliability", "claim": "ipc_compliance"}]
    },
    {
        "code": 11,
        "slug": "sensor_integration",
        "name": "Embedded Intelligence Capsule",
        "description": "Manages sensor fusion and on-device inference for embedded systems.",
        "connectors": [{"type": "firmware", "name": "debug_log"}, {"type": "sensor", "name": "raw_stream"}],
        "models": [{"id": "sensor_fusion_kalman", "type": "inference"}, {"id": "firmware_opt", "type": "optimization"}],
        "proofs": [{"type": "Performance", "claim": "sensor_accuracy"}]
    },
    {
        "code": 12,
        "slug": "magnet_assembly",
        "name": "Permanent Magnet Assembly Capsule",
        "description": "Optimizes magnet performance and reduces rare-earth dependence.",
        "connectors": [{"type": "csv", "name": "magnetization_curves"}, {"type": "mqtt", "name": "heat_treatment"}],
        "models": [{"id": "shadow_twin_magnetic", "type": "simulation"}, {"id": "m2n2_microstructure", "type": "evolutionary"}],
        "proofs": [{"type": "ASAL_SPA", "claim": "performance_uplift"}]
    },
    {
        "code": 13,
        "slug": "chemical_synthesis",
        "name": "Synthesis Capsule",
        "description": "Optimizes reaction kinetics and ensures safety in chemical processes.",
        "connectors": [{"type": "sensor", "name": "flow_rate"}, {"type": "sensor", "name": "reactor_pressure"}],
        "models": [{"id": "reaction_kinetics", "type": "simulation"}, {"id": "safety_monitor", "type": "inference"}],
        "proofs": [{"type": "Safety", "claim": "process_stability"}]
    },
    {
        "code": 14,
        "slug": "battery_production",
        "name": "Battery Intelligence Capsule",
        "description": "Optimizes electrode coating and cell formation for extended battery life.",
        "connectors": [{"type": "sensor", "name": "coating_thickness"}, {"type": "cycler", "name": "formation_data"}],
        "models": [{"id": "electrochemical_sim", "type": "simulation"}, {"id": "lifetime_pred", "type": "inference"}],
        "proofs": [{"type": "Performance", "claim": "cycle_life"}]
    },
    {
        "code": 15,
        "slug": "energy_microgrids",
        "name": "Microgrid Capsule",
        "description": "Balances distributed energy resources and optimizes microgrid stability.",
        "connectors": [{"type": "smart_meter", "name": "grid_tie"}, {"type": "inverter", "name": "solar_output"}],
        "models": [{"id": "load_flow_sim", "type": "simulation"}, {"id": "dispatch_opt", "type": "optimization"}],
        "proofs": [{"type": "Sustainability", "claim": "renewable_fraction"}]
    },
    {
        "code": 16,
        "slug": "process_control",
        "name": "Control Bridge Capsule",
        "description": "Bridges legacy OT/PLC systems with modern AI control and security.",
        "connectors": [{"type": "opc-ua", "name": "plc_tags"}, {"type": "network", "name": "packet_capture"}],
        "models": [{"id": "anomaly_detector", "type": "inference"}, {"id": "control_loop_tuner", "type": "optimization"}],
        "proofs": [{"type": "Security", "claim": "intrusion_free"}]
    },
    {
        "code": 17,
        "slug": "robotics_material_handling",
        "name": "Swarm Robotics Capsule",
        "description": "Coordinates AGV/AMR fleets for optimal routing and collision avoidance.",
        "connectors": [{"type": "fleet", "name": "agv_positions"}, {"type": "wms", "name": "task_list"}],
        "models": [{"id": "swarm_planner", "type": "optimization"}, {"id": "collision_pred", "type": "simulation"}],
        "proofs": [{"type": "Efficiency", "claim": "throughput_rate"}]
    },
    {
        "code": 18,
        "slug": "quality_ndt",
        "name": "Intelligent Inspection Capsule",
        "description": "Automated defect detection using multi-modal NDT data.",
        "connectors": [{"type": "stream", "name": "ultrasound"}, {"type": "image", "name": "thermal"}],
        "models": [{"id": "asal_detector", "type": "inference"}, {"id": "shadow_twin_defect", "type": "simulation"}],
        "proofs": [{"type": "ASAL_PCCA", "claim": "defect_free"}]
    },
    {
        "code": 19,
        "slug": "testing_labs",
        "name": "Verification Capsule",
        "description": "Automates test execution and generates proof-backed certification reports.",
        "connectors": [{"type": "daq", "name": "test_bench"}, {"type": "lims", "name": "sample_meta"}],
        "models": [{"id": "validity_checker", "type": "inference"}, {"id": "report_gen", "type": "inference"}],
        "proofs": [{"type": "Compliance", "claim": "spec_adherence"}]
    },
    {
        "code": 20,
        "slug": "packaging_assembly",
        "name": "Smart Assembly Capsule",
        "description": "Optimizes final assembly layout and packaging density.",
        "connectors": [{"type": "camera", "name": "line_feed"}, {"type": "sensor", "name": "weight_check"}],
        "models": [{"id": "layout_opt", "type": "optimization"}, {"id": "pack_density_sim", "type": "simulation"}],
        "proofs": [{"type": "Efficiency", "claim": "space_utilization"}]
    },
    {
        "code": 21,
        "slug": "logistics_routing",
        "name": "Adaptive Logistics Capsule",
        "description": "Optimizes supply chain routing and inventory flow.",
        "connectors": [{"type": "api", "name": "tms_feed"}, {"type": "gps", "name": "telematics"}],
        "models": [{"id": "rnd1_router", "type": "optimization"}, {"id": "shadow_twin_inventory", "type": "simulation"}],
        "proofs": [{"type": "Sustainability", "claim": "carbon_neutral"}]
    },
    {
        "code": 22,
        "slug": "warehousing_inventory",
        "name": "Inventory Intelligence Capsule",
        "description": "Optimizes warehouse layout and predicts stockout risks.",
        "connectors": [{"type": "wms", "name": "stock_levels"}, {"type": "erp", "name": "orders"}],
        "models": [{"id": "demand_forecast", "type": "inference"}, {"id": "layout_sim", "type": "simulation"}],
        "proofs": [{"type": "Efficiency", "claim": "pick_rate"}]
    },
    {
        "code": 23,
        "slug": "waste_management",
        "name": "Circular Economy Capsule",
        "description": "Tracks waste streams and identifies recycling opportunities.",
        "connectors": [{"type": "scale", "name": "waste_weight"}, {"type": "sensor", "name": "bin_level"}],
        "models": [{"id": "waste_classifier", "type": "inference"}, {"id": "recycling_opt", "type": "optimization"}],
        "proofs": [{"type": "Sustainability", "claim": "diversion_rate"}]
    },
    {
        "code": 24,
        "slug": "compliance_regulatory",
        "name": "Regulatory Proof Capsule",
        "description": "Automates compliance audits and export control verification.",
        "connectors": [{"type": "erp", "name": "transactions"}, {"type": "api", "name": "reg_db"}],
        "models": [{"id": "compliance_checker", "type": "inference"}, {"id": "risk_scorer", "type": "inference"}],
        "proofs": [{"type": "Compliance", "claim": "audit_pass"}]
    },
    {
        "code": 25,
        "slug": "workforce_labor",
        "name": "Workforce Orchestration Capsule",
        "description": "Optimizes shift scheduling and ensures worker safety.",
        "connectors": [{"type": "hris", "name": "schedule"}, {"type": "wearable", "name": "safety_monitor"}],
        "models": [{"id": "schedule_opt", "type": "optimization"}, {"id": "fatigue_pred", "type": "inference"}],
        "proofs": [{"type": "Safety", "claim": "incident_free"}]
    },
    {
        "code": 26,
        "slug": "finance_procurement",
        "name": "Procurement Capsule",
        "description": "Scores supplier risk and verifies financial compliance.",
        "connectors": [{"type": "erp", "name": "po_data"}, {"type": "api", "name": "market_feed"}],
        "models": [{"id": "supplier_risk_model", "type": "inference"}, {"id": "spend_analyzer", "type": "inference"}],
        "proofs": [{"type": "Risk", "claim": "supplier_health"}]
    },
    {
        "code": 27,
        "slug": "aftermarket_service",
        "name": "Service Twin Capsule",
        "description": "Predicts maintenance needs and verifies service execution.",
        "connectors": [{"type": "crm", "name": "service_logs"}, {"type": "iot", "name": "device_health"}],
        "models": [{"id": "predictive_maint", "type": "inference"}, {"id": "service_verifier", "type": "inference"}],
        "proofs": [{"type": "Reliability", "claim": "uptime_guarantee"}]
    }
]

def generate_blueprints():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"Created directory: {OUTPUT_DIR}")

    for area in AREAS:
        filename = f"{area['slug']}_v1.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        blueprint = {
            "capsule_id": f"{area['slug']}_v1",
            "version": "1.0.0",
            "area_code": area['code'],
            "name": area['name'],
            "description": area['description'],
            "connectors": area['connectors'],
            "models": area['models'],
            "proofs": area['proofs'],
            "ui_widgets": [
                {
                    "type": "dashboard_panel",
                    "data_source": area['models'][0]['id'],
                    "title": f"{area['name']} Dashboard"
                }
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(blueprint, f, indent=2)
        
        logger.info(f"Generated: {filename}")

    logger.info(f"Successfully generated {len(AREAS)} blueprints.")

if __name__ == "__main__":
    generate_blueprints()
