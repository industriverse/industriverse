from typing import List, Dict
from .capsule_blueprint import CapsuleBlueprint, CapsuleCategory, PRINConfig, SafetyBudget, MeshRoutingRules

# --- Category A: High-energy, dynamic systems (MHD priors) ---

CAPSULE_01_RAW_MATERIALS = CapsuleBlueprint(
    name="Raw Material Sourcing",
    capsule_id="capsule:rawmat:v1",
    category=CapsuleCategory.HIGH_ENERGY,
    description="Mining & Ore Ops: Granular flow + geomechanics.",
    physics_topology="Granular flow + geomechanics (avalanche, percolation)",
    domain_equations=["Granular stress models", "Coulomb failure", "Darcy flow"],
    energy_prior_file="MHD_64_energy_map",
    prin_config=PRINConfig(alpha=0.6, beta=0.25, gamma=0.15, approve_threshold=0.78),
    safety_budget=SafetyBudget(soft_energy_limit_j=100.0, hard_energy_limit_j=500.0),
    utid_pattern="UTID:REAL:mine01:rawmat:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["sample_chain_of_custody"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.rawmaterials.request",
        nats_result_subject="capsule.rawmaterials.result",
        priority_level="high"
    )
)

CAPSULE_02_RARE_EARTH = CapsuleBlueprint(
    name="Rare-earth Refining & Metallurgy",
    capsule_id="capsule:rareearth:v1",
    category=CapsuleCategory.HIGH_ENERGY,
    description="High-temperature phase transformations, diffusion.",
    physics_topology="High-temperature phase transformations, diffusion",
    domain_equations=["Arrhenius diffusion", "Phase diagram equilibrium", "Heat equation"],
    energy_prior_file="MHD_64_energy_map",
    prin_config=PRINConfig(alpha=0.6, beta=0.25, gamma=0.15, approve_threshold=0.80),
    safety_budget=SafetyBudget(soft_energy_limit_j=2000.0, hard_energy_limit_j=10000.0),
    utid_pattern="UTID:REAL:ref01:rareearth:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["material_cert"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.rareearth.request",
        nats_result_subject="capsule.rareearth.result",
        priority_level="critical"
    )
)

CAPSULE_03_POWDER_PROCESSING = CapsuleBlueprint(
    name="Powder Processing & Additive Feedstock",
    capsule_id="capsule:powder:v1",
    category=CapsuleCategory.HIGH_ENERGY,
    description="Particle packing, flowability, powder bed sintering.",
    physics_topology="Particle packing, flowability, powder bed sintering thermal fields",
    domain_equations=["Contact mechanics", "Sintering heat diffusion", "Porosity models"],
    energy_prior_file="MHD_64_energy_map",
    prin_config=PRINConfig(alpha=0.55, beta=0.30, gamma=0.15, approve_threshold=0.75),
    safety_budget=SafetyBudget(soft_energy_limit_j=300.0, hard_energy_limit_j=1200.0),
    utid_pattern="UTID:REAL:powder01:feed:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["particle_size_distribution_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.powder.request",
        nats_result_subject="capsule.powder.result",
        priority_level="normal"
    )
)

CAPSULE_04_CASTING = CapsuleBlueprint(
    name="Casting & Foundry Operations",
    capsule_id="capsule:casting:v1",
    category=CapsuleCategory.HIGH_ENERGY,
    description="Fluid metal flow, solidification fronts, shrinkage.",
    physics_topology="Fluid metal flow, solidification fronts, shrinkage",
    domain_equations=["Navier-Stokes (melt)", "Stefan condition", "Heat conduction"],
    energy_prior_file="turbulent_radiative_layer_2D_energy_map",
    prin_config=PRINConfig(alpha=0.58, beta=0.30, gamma=0.12, approve_threshold=0.77),
    safety_budget=SafetyBudget(soft_energy_limit_j=800.0, hard_energy_limit_j=3500.0),
    utid_pattern="UTID:REAL:foundry01:cast:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["cast_riser_design_hash", "NDT_expected_signature"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.casting.request",
        nats_result_subject="capsule.casting.result",
        priority_level="high"
    )
)

CAPSULE_05_FORMING = CapsuleBlueprint(
    name="Forming (Rolling, Extrusion)",
    capsule_id="capsule:forming:v1",
    category=CapsuleCategory.HIGH_ENERGY,
    description="Plastic flow, strain hardening, thermal-mechanical coupling.",
    physics_topology="Plastic flow, strain hardening, thermal-mechanical coupling",
    domain_equations=["Plasticity models (Von Mises)", "Work hardening relations", "Heat generation"],
    energy_prior_file="shear_flow_energy_map",
    prin_config=PRINConfig(alpha=0.6, beta=0.28, gamma=0.12, approve_threshold=0.78),
    safety_budget=SafetyBudget(soft_energy_limit_j=200.0, hard_energy_limit_j=800.0),
    utid_pattern="UTID:REAL:mill01:forming:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["strain_map_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.forming.request",
        nats_result_subject="capsule.forming.result",
        priority_level="normal"
    )
)

CAPSULE_06_MACHINING = CapsuleBlueprint(
    name="Machining & Precision Fabrication",
    capsule_id="capsule:machining:v1",
    category=CapsuleCategory.HIGH_ENERGY,
    description="Material removal, tool-chip interface, vibration dynamics.",
    physics_topology="Material removal, tool-chip interface, vibration dynamics",
    domain_equations=["Cutting force models", "Chatter stability diagrams", "Thermal tool wear"],
    energy_prior_file="shear_flow_energy_map",
    prin_config=PRINConfig(alpha=0.5, beta=0.35, gamma=0.15, approve_threshold=0.74),
    safety_budget=SafetyBudget(soft_energy_limit_j=50.0, hard_energy_limit_j=250.0),
    utid_pattern="UTID:REAL:fab01:machining:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["gcode_hash", "sensor_trace_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.machining.request",
        nats_result_subject="capsule.machining.result",
        priority_level="normal"
    )
)

CAPSULE_07_WELDING = CapsuleBlueprint(
    name="Joining & Welding",
    capsule_id="capsule:welding:v1",
    category=CapsuleCategory.HIGH_ENERGY,
    description="Arc/plasma heating, melt-pool dynamics, micro-structure evolution.",
    physics_topology="Arc/plasma heating, melt-pool dynamics, micro-structure evolution",
    domain_equations=["Heat transfer in welding", "Marangoni flow", "Phase solidification"],
    energy_prior_file="turbulent_radiative_layer_2D_energy_map",
    prin_config=PRINConfig(alpha=0.62, beta=0.28, gamma=0.10, approve_threshold=0.80),
    safety_budget=SafetyBudget(soft_energy_limit_j=500.0, hard_energy_limit_j=2000.0),
    utid_pattern="UTID:REAL:welder01:weld:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["weld_sequence_hash", "NDT_expected_signature"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.welding.request",
        nats_result_subject="capsule.welding.result",
        priority_level="high"
    )
)

# --- Category B: Flow, heat, pressure (Radiative + Fluid) ---

CAPSULE_08_COATINGS = CapsuleBlueprint(
    name="Surface Treatment & Coatings",
    capsule_id="capsule:coatings:v1",
    category=CapsuleCategory.FLOW_HEAT,
    description="Chemical kinetics, diffusion layers, adhesion mechanics.",
    physics_topology="Chemical kinetics, diffusion layers, adhesion mechanics",
    domain_equations=["Reaction-diffusion", "Adhesion energy", "Stress due to coating"],
    energy_prior_file="turbulent_radiative_layer_2D_energy_map",
    prin_config=PRINConfig(alpha=0.56, beta=0.30, gamma=0.14, approve_threshold=0.76),
    safety_budget=SafetyBudget(soft_energy_limit_j=100.0, hard_energy_limit_j=400.0),
    utid_pattern="UTID:REAL:coat01:surf:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["coating_thickness_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.coatings.request",
        nats_result_subject="capsule.coatings.result",
        priority_level="normal"
    )
)

CAPSULE_09_COMPOSITES = CapsuleBlueprint(
    name="Polymers, Composites & Molding",
    capsule_id="capsule:composites:v1",
    category=CapsuleCategory.FLOW_HEAT,
    description="Viscoelastic flow, cure kinetics, shrinkage/warpage.",
    physics_topology="Viscoelastic flow, cure kinetics, shrinkage/warpage",
    domain_equations=["Viscoelastic constitutive equations", "Cure kinetics", "Heat conduction"],
    energy_prior_file="rayleigh_benard_energy_map",
    prin_config=PRINConfig(alpha=0.58, beta=0.30, gamma=0.12, approve_threshold=0.77),
    safety_budget=SafetyBudget(soft_energy_limit_j=600.0, hard_energy_limit_j=2500.0),
    utid_pattern="UTID:REAL:compo01:mold:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["cure_profile_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.composites.request",
        nats_result_subject="capsule.composites.result",
        priority_level="normal"
    )
)

CAPSULE_10_PCB = CapsuleBlueprint(
    name="Electronics & PCB Assembly",
    capsule_id="capsule:pcb:v1",
    category=CapsuleCategory.FLOW_HEAT,
    description="Thermal reflow, solder wetting, EMI coupling.",
    physics_topology="Thermal reflow, solder wetting, EMI coupling",
    domain_equations=["Heat conduction", "Reflow phase transforms", "Circuit parasitics"],
    energy_prior_file="rayleigh_benard_energy_map",
    prin_config=PRINConfig(alpha=0.50, beta=0.40, gamma=0.10, approve_threshold=0.74),
    safety_budget=SafetyBudget(soft_energy_limit_j=120.0, hard_energy_limit_j=600.0),
    utid_pattern="UTID:REAL:pcb01:assembly:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["pcb_stencil_hash", "bom_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.pcb.request",
        nats_result_subject="capsule.pcb.result",
        priority_level="high"
    )
)

CAPSULE_11_SENSORS = CapsuleBlueprint(
    name="Sensor & Embedded Systems Integration",
    capsule_id="capsule:sensor:v1",
    category=CapsuleCategory.FLOW_HEAT,
    description="Signal propagation, sensor cross-sensitivity, thermal drift.",
    physics_topology="Signal propagation, sensor cross-sensitivity, thermal drift",
    domain_equations=["Transfer functions", "Noise models (SNR)", "Calibration curves"],
    energy_prior_file="rayleigh_benard_energy_map",
    prin_config=PRINConfig(alpha=0.5, beta=0.35, gamma=0.15, approve_threshold=0.74),
    safety_budget=SafetyBudget(soft_energy_limit_j=40.0, hard_energy_limit_j=200.0),
    utid_pattern="UTID:REAL:sensor01:embed:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["firmware_hash", "calibration_trace_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.sensor.request",
        nats_result_subject="capsule.sensor.result",
        priority_level="normal"
    )
)

CAPSULE_12_MAGNETS = CapsuleBlueprint(
    name="Permanent Magnets & Magnetic Assemblies",
    capsule_id="capsule:magnet:v1",
    category=CapsuleCategory.FLOW_HEAT,
    description="Magnetostatics, hysteresis, thermal demagnetization.",
    physics_topology="Magnetostatics, hysteresis, thermal demagnetization",
    domain_equations=["Maxwell magnetostatic equations", "Hysteresis loops", "Curie temperature"],
    energy_prior_file="MHD_64_energy_map",
    prin_config=PRINConfig(alpha=0.65, beta=0.25, gamma=0.10, approve_threshold=0.82),
    safety_budget=SafetyBudget(soft_energy_limit_j=1000.0, hard_energy_limit_j=5000.0),
    utid_pattern="UTID:REAL:magnet01:perm:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["BH_curve_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.magnet.request",
        nats_result_subject="capsule.magnet.result",
        priority_level="critical"
    )
)

CAPSULE_13_CHEMICAL = CapsuleBlueprint(
    name="Chemical Synthesis & Pharma Process Lines",
    capsule_id="capsule:chem:v1",
    category=CapsuleCategory.FLOW_HEAT,
    description="Reactive flows, multi-phase reactors, heat removal.",
    physics_topology="Reactive flows, multi-phase reactors, heat removal",
    domain_equations=["Reaction kinetics", "Mass balance", "Energy balance"],
    energy_prior_file="turbulent_radiative_layer_2D_energy_map",
    prin_config=PRINConfig(alpha=0.63, beta=0.27, gamma=0.10, approve_threshold=0.80),
    safety_budget=SafetyBudget(soft_energy_limit_j=3000.0, hard_energy_limit_j=12000.0),
    utid_pattern="UTID:REAL:chem01:synth:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["process_recipe_hash", "assay_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.chem.request",
        nats_result_subject="capsule.chem.result",
        priority_level="critical"
    )
)

CAPSULE_14_BATTERY = CapsuleBlueprint(
    name="Battery Chemistry & Cell Production",
    capsule_id="capsule:battery:v1",
    category=CapsuleCategory.FLOW_HEAT,
    description="Ion transport, phase changes (SEI formation), thermal runaway risk.",
    physics_topology="Ion transport, phase changes (SEI formation), thermal runaway risk",
    domain_equations=["Nernst-Planck", "Butler-Volmer kinetics", "Heat generation models"],
    energy_prior_file="MHD_64_energy_map",
    prin_config=PRINConfig(alpha=0.66, beta=0.24, gamma=0.10, approve_threshold=0.82),
    safety_budget=SafetyBudget(soft_energy_limit_j=3500.0, hard_energy_limit_j=15000.0),
    utid_pattern="UTID:REAL:batt01:cell:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["cycling_profile_hash", "safety_margin"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.battery.request",
        nats_result_subject="capsule.battery.result",
        priority_level="critical"
    )
)

CAPSULE_15_MICROGRID = CapsuleBlueprint(
    name="Energy Generation & Microgrids (On-site)",
    capsule_id="capsule:microgrid:v1",
    category=CapsuleCategory.FLOW_HEAT,
    description="Load balancing, transient response, inverter dynamics.",
    physics_topology="Load balancing, transient response, inverter dynamics",
    domain_equations=["Power flow", "Transient stability", "Control loops"],
    energy_prior_file="MHD_64_energy_map",
    prin_config=PRINConfig(alpha=0.55, beta=0.35, gamma=0.10, approve_threshold=0.78),
    safety_budget=SafetyBudget(soft_energy_limit_j=2000.0, hard_energy_limit_j=8000.0),
    utid_pattern="UTID:REAL:grid01:micro:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["grid_stability_snapshot_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.microgrid.request",
        nats_result_subject="capsule.microgrid.result",
        priority_level="normal"
    )
)

# --- Category C: Swarm, logistics, active matter ---

CAPSULE_16_OT_CONTROL = CapsuleBlueprint(
    name="Process Control & OT/PLC Integration",
    capsule_id="capsule:ot:v1",
    category=CapsuleCategory.SWARM_LOGISTICS,
    description="Closed-loop control, actuator delays, sensor noise.",
    physics_topology="Closed-loop control, actuator delays, sensor noise",
    domain_equations=["PID/advanced MPC equations", "Lag dynamics"],
    energy_prior_file="active_matter_energy_map",
    prin_config=PRINConfig(alpha=0.52, beta=0.38, gamma=0.10, approve_threshold=0.75),
    safety_budget=SafetyBudget(soft_energy_limit_j=150.0, hard_energy_limit_j=600.0),
    utid_pattern="UTID:REAL:plc01:control:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["control_config_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.ot.request",
        nats_result_subject="capsule.ot.result",
        priority_level="normal"
    )
)

CAPSULE_17_ROBOTICS = CapsuleBlueprint(
    name="Robotics & Material Handling (AGV/AMR)",
    capsule_id="capsule:robotics:v1",
    category=CapsuleCategory.SWARM_LOGISTICS,
    description="Multi-body dynamics, collision avoidance, load transfer.",
    physics_topology="Multi-body dynamics, collision avoidance, load transfer",
    domain_equations=["Rigid-body dynamics", "Contact models", "Path planning cost functions"],
    energy_prior_file="active_matter_energy_map",
    prin_config=PRINConfig(alpha=0.48, beta=0.42, gamma=0.10, approve_threshold=0.73),
    safety_budget=SafetyBudget(soft_energy_limit_j=80.0, hard_energy_limit_j=400.0),
    utid_pattern="UTID:REAL:robot01:amr:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["path_trace_hash", "collision_veto_log"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.robotics.request",
        nats_result_subject="capsule.robotics.result",
        priority_level="normal"
    )
)

CAPSULE_18_NDT = CapsuleBlueprint(
    name="Quality Control & NDT",
    capsule_id="capsule:ndt:v1",
    category=CapsuleCategory.SWARM_LOGISTICS,
    description="Wave propagation scattering, imaging inverse problems.",
    physics_topology="Wave propagation scattering, imaging inverse problems",
    domain_equations=["Helmholtz", "Scattering kernels", "Inverse transform models"],
    energy_prior_file="active_matter_energy_map",
    prin_config=PRINConfig(alpha=0.60, beta=0.30, gamma=0.10, approve_threshold=0.80),
    safety_budget=SafetyBudget(soft_energy_limit_j=120.0, hard_energy_limit_j=500.0),
    utid_pattern="UTID:REAL:ndt01:qc:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["scan_trace_hash", "ndt_report_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.ndt.request",
        nats_result_subject="capsule.ndt.result",
        priority_level="high"
    )
)

CAPSULE_19_TEST_LAB = CapsuleBlueprint(
    name="Testing & Certification Labs",
    capsule_id="capsule:testlab:v1",
    category=CapsuleCategory.SWARM_LOGISTICS,
    description="Controlled experiments with thermodynamic boundary conditions.",
    physics_topology="Controlled experiments with thermodynamic boundary conditions",
    domain_equations=["Measurement uncertainty models", "Calibration curve fits"],
    energy_prior_file="active_matter_energy_map",
    prin_config=PRINConfig(alpha=0.55, beta=0.35, gamma=0.10, approve_threshold=0.78),
    safety_budget=SafetyBudget(soft_energy_limit_j=500.0, hard_energy_limit_j=2000.0),
    utid_pattern="UTID:REAL:lab01:cert:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["cert_report_hash", "test_params_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.testlab.request",
        nats_result_subject="capsule.testlab.result",
        priority_level="normal"
    )
)

CAPSULE_20_ASSEMBLY = CapsuleBlueprint(
    name="Packaging & Final Assembly",
    capsule_id="capsule:assembly:v1",
    category=CapsuleCategory.SWARM_LOGISTICS,
    description="Kinematic assembly tolerances, thermal expansion, sealing tests.",
    physics_topology="Kinematic assembly tolerances, thermal expansion, sealing tests",
    domain_equations=["Tolerance stack-ups", "Boltzmann heat expansion model"],
    energy_prior_file="active_matter_energy_map",
    prin_config=PRINConfig(alpha=0.50, beta=0.40, gamma=0.10, approve_threshold=0.75),
    safety_budget=SafetyBudget(soft_energy_limit_j=80.0, hard_energy_limit_j=400.0),
    utid_pattern="UTID:REAL:pack01:final:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["assembly_dna_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.assembly.request",
        nats_result_subject="capsule.assembly.result",
        priority_level="normal"
    )
)

CAPSULE_21_LOGISTICS = CapsuleBlueprint(
    name="Logistics & Inbound/Outbound Routing",
    capsule_id="capsule:logistics:v1",
    category=CapsuleCategory.SWARM_LOGISTICS,
    description="Flow-of-goods, vehicle routing with stochastic demand.",
    physics_topology="Flow-of-goods, vehicle routing with stochastic demand",
    domain_equations=["VRP formulations", "Queueing network models"],
    energy_prior_file="active_matter_energy_map",
    prin_config=PRINConfig(alpha=0.40, beta=0.45, gamma=0.15, approve_threshold=0.70),
    safety_budget=SafetyBudget(soft_energy_limit_j=30.0, hard_energy_limit_j=150.0),
    utid_pattern="UTID:REAL:log01:rout:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["route_plan_hash", "delivery_eta_proof"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.logistics.request",
        nats_result_subject="capsule.logistics.result",
        priority_level="normal"
    )
)

CAPSULE_22_WAREHOUSING = CapsuleBlueprint(
    name="Warehousing & Inventory Optimization",
    capsule_id="capsule:warehousing:v1",
    category=CapsuleCategory.SWARM_LOGISTICS,
    description="Stochastic demand, shelf-space optimization.",
    physics_topology="Stochastic demand, shelf-space optimization (flow vs density tradeoffs)",
    domain_equations=["Inventory control (EOQ, (Q,R))", "Stochastic control"],
    energy_prior_file="active_matter_energy_map",
    prin_config=PRINConfig(alpha=0.40, beta=0.45, gamma=0.15, approve_threshold=0.70),
    safety_budget=SafetyBudget(soft_energy_limit_j=20.0, hard_energy_limit_j=100.0),
    utid_pattern="UTID:REAL:wh01:inv:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["stock_state_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.warehousing.request",
        nats_result_subject="capsule.warehousing.result",
        priority_level="normal"
    )
)

# --- Category D: High-complexity multi-physics ---
# (Note: Capsules 23-27 were listed in the prompt but not fully detailed in the final block.
# I will infer details based on the earlier list and standard patterns.)

CAPSULE_23_ELECTRONICS_ASSEMBLY = CapsuleBlueprint(
    name="Electronics Assembly (Reflow + Pick-Place)",
    capsule_id="capsule:electronics:v1",
    category=CapsuleCategory.MULTI_PHYSICS,
    description="Reflow soldering, pick and place dynamics.",
    physics_topology="Reflow soldering, pick and place dynamics",
    domain_equations=["Heat transfer", "Kinematics"],
    energy_prior_file="supernova_explosion_64_energy_map",
    prin_config=PRINConfig(alpha=0.50, beta=0.40, gamma=0.10, approve_threshold=0.74),
    safety_budget=SafetyBudget(soft_energy_limit_j=100.0, hard_energy_limit_j=500.0),
    utid_pattern="UTID:REAL:elec01:assy:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["assembly_log_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.electronics.request",
        nats_result_subject="capsule.electronics.result",
        priority_level="normal"
    )
)

CAPSULE_24_PCB_MFG = CapsuleBlueprint(
    name="PCB Manufacturing (EM + Thermal)",
    capsule_id="capsule:pcbmfg:v1",
    category=CapsuleCategory.MULTI_PHYSICS,
    description="EM + thermal coupling in PCB fabrication.",
    physics_topology="EM + thermal coupling",
    domain_equations=["Maxwell equations", "Heat diffusion"],
    energy_prior_file="supernova_explosion_64_energy_map",
    prin_config=PRINConfig(alpha=0.55, beta=0.35, gamma=0.10, approve_threshold=0.76),
    safety_budget=SafetyBudget(soft_energy_limit_j=150.0, hard_energy_limit_j=600.0),
    utid_pattern="UTID:REAL:pcb02:mfg:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["layer_stackup_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.pcbmfg.request",
        nats_result_subject="capsule.pcbmfg.result",
        priority_level="normal"
    )
)

CAPSULE_25_SENSOR_INTEGRATION = CapsuleBlueprint(
    name="Sensor Integration (Signal Entropy)",
    capsule_id="capsule:sensorint:v1",
    category=CapsuleCategory.MULTI_PHYSICS,
    description="Signal entropy and sensor fusion.",
    physics_topology="Signal entropy, sensor fusion",
    domain_equations=["Information theory", "Kalman filtering"],
    energy_prior_file="supernova_explosion_64_energy_map",
    prin_config=PRINConfig(alpha=0.50, beta=0.40, gamma=0.10, approve_threshold=0.75),
    safety_budget=SafetyBudget(soft_energy_limit_j=50.0, hard_energy_limit_j=200.0),
    utid_pattern="UTID:REAL:sens02:int:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["fusion_matrix_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.sensorint.request",
        nats_result_subject="capsule.sensorint.result",
        priority_level="normal"
    )
)

CAPSULE_26_SURFACE_FINISHING = CapsuleBlueprint(
    name="Surface Finishing (Fluid + Pressure)",
    capsule_id="capsule:surface:v1",
    category=CapsuleCategory.MULTI_PHYSICS,
    description="Fluid dynamics and pressure in surface finishing.",
    physics_topology="Fluid dynamics, pressure distribution",
    domain_equations=["Bernoulli equation", "Surface tension"],
    energy_prior_file="supernova_explosion_64_energy_map",
    prin_config=PRINConfig(alpha=0.55, beta=0.35, gamma=0.10, approve_threshold=0.76),
    safety_budget=SafetyBudget(soft_energy_limit_j=80.0, hard_energy_limit_j=300.0),
    utid_pattern="UTID:REAL:surf01:fin:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["finish_quality_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.surface.request",
        nats_result_subject="capsule.surface.result",
        priority_level="normal"
    )
)

CAPSULE_27_LIFECYCLE = CapsuleBlueprint(
    name="End-to-End Lifecycle Analytics",
    capsule_id="capsule:lifecycle:v1",
    category=CapsuleCategory.MULTI_PHYSICS,
    description="Entropy -> MTBF, lifecycle analytics.",
    physics_topology="Entropy accumulation, failure probability",
    domain_equations=["Weibull distribution", "Entropy production"],
    energy_prior_file="supernova_explosion_64_energy_map",
    prin_config=PRINConfig(alpha=0.45, beta=0.40, gamma=0.15, approve_threshold=0.72),
    safety_budget=SafetyBudget(soft_energy_limit_j=20.0, hard_energy_limit_j=100.0),
    utid_pattern="UTID:REAL:life01:cycle:{timestamp}:{nonce}",
    proof_schema={"additional_fields": ["mtbf_report_hash"]},
    mesh_rules=MeshRoutingRules(
        nats_request_subject="capsule.lifecycle.request",
        nats_result_subject="capsule.lifecycle.result",
        priority_level="normal"
    )
)

ALL_CAPSULES = [
    CAPSULE_01_RAW_MATERIALS,
    CAPSULE_02_RARE_EARTH,
    CAPSULE_03_POWDER_PROCESSING,
    CAPSULE_04_CASTING,
    CAPSULE_05_FORMING,
    CAPSULE_06_MACHINING,
    CAPSULE_07_WELDING,
    CAPSULE_08_COATINGS,
    CAPSULE_09_COMPOSITES,
    CAPSULE_10_PCB,
    CAPSULE_11_SENSORS,
    CAPSULE_12_MAGNETS,
    CAPSULE_13_CHEMICAL,
    CAPSULE_14_BATTERY,
    CAPSULE_15_MICROGRID,
    CAPSULE_16_OT_CONTROL,
    CAPSULE_17_ROBOTICS,
    CAPSULE_18_NDT,
    CAPSULE_19_TEST_LAB,
    CAPSULE_20_ASSEMBLY,
    CAPSULE_21_LOGISTICS,
    CAPSULE_22_WAREHOUSING,
    CAPSULE_23_ELECTRONICS_ASSEMBLY,
    CAPSULE_24_PCB_MFG,
    CAPSULE_25_SENSOR_INTEGRATION,
    CAPSULE_26_SURFACE_FINISHING,
    CAPSULE_27_LIFECYCLE
]

CAPSULE_REGISTRY = {c.capsule_id: c for c in ALL_CAPSULES}
