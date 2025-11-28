from src.demo_framework.scenario import DemoScenario

SPACE_SCENARIOS = [
    DemoScenario(
        id="SPACE-001", name="Orbital Trajectory Optimization", domain="Space",
        description="Minimize fuel for geostationary transfer.",
        hypothesis="Use Oberth effect at perigee.",
        expected_outcome={"delta_v": "Minimized", "energy": "<0.5"},
        required_priors=["space_v1"]
    ),
    DemoScenario(
        id="SPACE-002", name="Solar Sail Attitude Control", domain="Space",
        description="Maintain orientation using radiation pressure.",
        hypothesis="Adjust vane angles to counteract torque.",
        expected_outcome={"pointing_error": "<0.1deg", "energy": "<0.3"},
        required_priors=["space_v1"]
    ),
    DemoScenario(
        id="SPACE-003", name="Ion Thruster Efficiency", domain="Space",
        description="Maximize specific impulse of Hall thruster.",
        hypothesis="Optimize magnetic field topology.",
        expected_outcome={"isp": ">2000s", "energy": "<0.6"},
        required_priors=["space_v1"]
    ),
    DemoScenario(
        id="SPACE-004", name="Re-entry Heat Shield", domain="Space",
        description="Design TPS for atmospheric entry.",
        hypothesis="Optimize ablative material thickness.",
        expected_outcome={"max_temp": "<2000C", "energy": "<0.8"},
        required_priors=["space_v1"]
    ),
    DemoScenario(
        id="SPACE-005", name="Space Debris Avoidance", domain="Space",
        description="Plan maneuver to avoid collision.",
        hypothesis="Execute radial burn to change period.",
        expected_outcome={"collision_prob": "0", "energy": "<0.2"},
        required_priors=["space_v1"]
    ),
    DemoScenario(
        id="SPACE-006", name="RF Camouflage", domain="Space",
        description="Minimize RF signature of satellite.",
        hypothesis="Spread spectrum and directional beamforming.",
        expected_outcome={"rf_leakage": "Low", "energy": "<0.1"},
        required_priors=["sat_security_v1"]
    ),
    DemoScenario(
        id="SPACE-007", name="Jamming Resistance", domain="Space",
        description="Maintain comms link under jamming.",
        hypothesis="Frequency hopping pattern optimization.",
        expected_outcome={"ber": "<1e-6", "energy": "<0.4"},
        required_priors=["sat_security_v1"]
    ),
    DemoScenario(
        id="SPACE-008", name="Swarm Formation Flying", domain="Space",
        description="Coordinate swarm for synthetic aperture.",
        hypothesis="Distributed consensus for relative station keeping.",
        expected_outcome={"baseline_error": "<1cm", "energy": "<0.5"},
        required_priors=["space_v1"]
    ),
    DemoScenario(
        id="SPACE-009", name="Inter-Satellite Link", domain="Space",
        description="Optimize optical link budget.",
        hypothesis="Dynamic power control based on range.",
        expected_outcome={"link_margin": ">3dB", "energy": "<0.3"},
        required_priors=["space_v1"]
    ),
    DemoScenario(
        id="SPACE-010", name="Deep Space Navigation", domain="Space",
        description="Autonomous navigation using pulsars.",
        hypothesis="Triangulate position from pulsar timing.",
        expected_outcome={"pos_error": "<100km", "energy": "<0.7"},
        required_priors=["space_v1"]
    )
]
