from src.demo_framework.scenario import DemoScenario

PHYSICS_SCENARIOS = [
    DemoScenario(
        id="PHYS-001", name="Fusion Plasma Stability", domain="Physics",
        description="Optimize magnetic confinement to prevent plasma disruption.",
        hypothesis="Increase toroidal field strength to stabilize kink modes.",
        expected_outcome={"stability_index": ">0.9", "energy": "<1.0"},
        required_priors=["fusion_v1"]
    ),
    DemoScenario(
        id="PHYS-002", name="Grid Load Balancing", domain="Physics",
        description="Balance microgrid load during peak demand.",
        hypothesis="Dispatch battery storage to offset solar dip.",
        expected_outcome={"frequency_deviation": "<0.1Hz", "energy": "<0.5"},
        required_priors=["microgrid_v1"]
    ),
    DemoScenario(
        id="PHYS-003", name="Motor Harmonic Reduction", domain="Physics",
        description="Minimize torque ripple in EV motor.",
        hypothesis="Adjust PWM switching frequency to cancel 5th harmonic.",
        expected_outcome={"torque_ripple": "<2%", "energy": "<0.8"},
        required_priors=["motor_v1"]
    ),
    DemoScenario(
        id="PHYS-004", name="Robotic Arm Damping", domain="Physics",
        description="Reduce oscillation in high-speed pick-and-place.",
        hypothesis="Increase derivative gain in PID controller.",
        expected_outcome={"settling_time": "<0.5s", "energy": "<0.3"},
        required_priors=["robotics_v1"]
    ),
    DemoScenario(
        id="PHYS-005", name="Wafer Thermal Uniformity", domain="Physics",
        description="Ensure uniform temperature across silicon wafer.",
        hypothesis="Optimize zone heating profile.",
        expected_outcome={"temp_variance": "<0.1C", "energy": "<0.2"},
        required_priors=["wafer_v1"]
    ),
    DemoScenario(
        id="PHYS-006", name="PCB Reflow Profile", domain="Physics",
        description="Optimize solder reflow curve.",
        hypothesis="Adjust soak time to prevent thermal shock.",
        expected_outcome={"defects": "0", "energy": "<0.4"},
        required_priors=["pcbmfg_v1"]
    ),
    DemoScenario(
        id="PHYS-007", name="Casting Porosity Control", domain="Physics",
        description="Minimize porosity in aluminum casting.",
        hypothesis="Control cooling rate to optimize nucleation.",
        expected_outcome={"porosity": "<1%", "energy": "<0.6"},
        required_priors=["casting_v1"]
    ),
    DemoScenario(
        id="PHYS-008", name="Battery Thermal Runaway", domain="Physics",
        description="Prevent thermal runaway in Li-ion pack.",
        hypothesis="Limit discharge rate when temp > 45C.",
        expected_outcome={"max_temp": "<50C", "energy": "<0.1"},
        required_priors=["battery_v1"]
    ),
    DemoScenario(
        id="PHYS-009", name="Apparel Tensioning", domain="Physics",
        description="Optimize fabric tension in automated sewing.",
        hypothesis="Adjust feed rate based on fabric elasticity.",
        expected_outcome={"seam_pucker": "None", "energy": "<0.2"},
        required_priors=["apparel_v1"]
    ),
    DemoScenario(
        id="PHYS-010", name="Tokamak Divertor Load", domain="Physics",
        description="Manage heat flux on tokamak divertor.",
        hypothesis="Inject impurity gas to radiate power.",
        expected_outcome={"heat_flux": "<10MW/m2", "energy": "<0.9"},
        required_priors=["fusion_v1"]
    )
]
