from src.demo_framework.scenario import DemoScenario

BIO_SCENARIOS = [
    DemoScenario(
        id="BIO-001", name="Protein Folding Stability", domain="Bio",
        description="Predict stable conformation of a novel protein.",
        hypothesis="Minimize Gibbs free energy of the folded state.",
        expected_outcome={"rmsd": "<2A", "energy": "<0.5"},
        required_priors=["bio_v1"]
    ),
    DemoScenario(
        id="BIO-002", name="Ligand Binding Affinity", domain="Bio",
        description="Optimize drug candidate binding to receptor.",
        hypothesis="Modify side chain to increase hydrogen bonding.",
        expected_outcome={"binding_energy": "<-10kcal/mol", "energy": "<0.4"},
        required_priors=["bio_v1"]
    ),
    DemoScenario(
        id="BIO-003", name="Enzyme Catalysis Rate", domain="Bio",
        description="Enhance catalytic efficiency of an industrial enzyme.",
        hypothesis="Mutate active site residues to stabilize transition state.",
        expected_outcome={"kcat": ">100/s", "energy": "<0.6"},
        required_priors=["bio_v1"]
    ),
    DemoScenario(
        id="BIO-004", name="DNA Repair Mechanism", domain="Bio",
        description="Simulate repair of UV-induced thymine dimers.",
        hypothesis="Activate photolyase pathway.",
        expected_outcome={"repair_efficiency": ">90%", "energy": "<0.3"},
        required_priors=["bio_v1"]
    ),
    DemoScenario(
        id="BIO-005", name="Cell Membrane Permeability", domain="Bio",
        description="Design peptide for targeted drug delivery.",
        hypothesis="Optimize amphipathicity for membrane penetration.",
        expected_outcome={"permeability": "High", "energy": "<0.5"},
        required_priors=["bio_v1"]
    ),
    DemoScenario(
        id="BIO-006", name="Drug Toxicity Prediction", domain="Bio",
        description="Screen compound for hepatotoxicity.",
        hypothesis="Check for off-target binding to CYP450.",
        expected_outcome={"toxicity_score": "Low", "energy": "<0.2"},
        required_priors=["bio_v1"]
    ),
    DemoScenario(
        id="BIO-007", name="Viral Capsid Stability", domain="Bio",
        description="Analyze stability of viral vector for gene therapy.",
        hypothesis="Strengthen protein-protein interfaces.",
        expected_outcome={"stability": "High", "energy": "<0.4"},
        required_priors=["bio_v1"]
    ),
    DemoScenario(
        id="BIO-008", name="CRISPR Off-Target Minimization", domain="Bio",
        description="Design gRNA with minimal off-target effects.",
        hypothesis="Optimize seed sequence specificity.",
        expected_outcome={"off_targets": "0", "energy": "<0.1"},
        required_priors=["bio_v1"]
    ),
    DemoScenario(
        id="BIO-009", name="Metabolic Pathway Optimization", domain="Bio",
        description="Maximize yield of biofuel production.",
        hypothesis="Redirect flux from competing pathways.",
        expected_outcome={"yield": ">80%", "energy": "<0.7"},
        required_priors=["bio_v1"]
    ),
    DemoScenario(
        id="BIO-010", name="Antibody Design", domain="Bio",
        description="Design antibody for specific antigen.",
        hypothesis="Optimize CDR loops for complementarity.",
        expected_outcome={"affinity": "High", "energy": "<0.3"},
        required_priors=["bio_v1"]
    )
]
