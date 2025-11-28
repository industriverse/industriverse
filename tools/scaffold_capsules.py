import os
import yaml

DOMAINS = [
    "grid", "wafer", "apparel", "battery",
    "motor", "magnet", "cnc", "chassis", "microgrid",
    "casting", "heat", "chem", "polymer", "metal",
    "pipeline", "qctherm", "failure",
    "robotics", "matflow", "workforce", "schedule",
    "amrsafety", "conveyor", "assembly",
    "electronics", "pcbmfg", "sensorint",
    "surface", "lifecycle",
]

# Adjust path to src
SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")

def create_prior(domain):
    content = f"""import numpy as np
from ebm_lib.base import EnergyPrior

class {domain.capitalize()}PriorV1:
    name = "{domain}"
    version = "v1"
    required_fields = ["state_vector"]
    metadata = {{
        "equations": ["Generic ODE"],
        "description": "Physics-informed energy function for {domain}",
    }}

    def validate(self, state):
        for f in self.required_fields:
            if f not in state:
                raise ValueError(f"Missing required field: {{f}}")

    def energy(self, state):
        x = state["state_vector"]
        # Placeholder energy function: simple quadratic well
        return float(np.sum(x**2))

    def grad(self, state):
        x = state["state_vector"]
        return {{"state_vector": 2 * x}}

PRIOR = {domain.capitalize()}PriorV1()
"""
    path = os.path.join(SRC_DIR, "ebm_lib", "priors", f"{domain}_v1.py")
    with open(path, "w") as f:
        f.write(content)
    print(f"Created {path}")

def create_tnn(domain):
    content = f"""import numpy as np
from tnn.base import TNN

class {domain.capitalize()}TNN(TNN):
    def simulate(self, state, control, dt, steps):
        # Generic placeholder simulation
        history = []
        # Default to 8-dim vector if not present
        x = state.get("state_vector", np.zeros(8))
        
        for s in range(steps):
            # Simple decay dynamics: dx/dt = -0.1 * x
            dx = -0.1 * x * dt
            x = x + dx
            history.append({{"step": s, "state_vector": x.copy()}})

        return {{"trajectory": history}}
"""
    path = os.path.join(SRC_DIR, "tnn", f"{domain}_tnn.py")
    with open(path, "w") as f:
        f.write(content)
    print(f"Created {path}")

def create_manifest(domain):
    capsule_id = f"{domain}_v1"
    path_dir = os.path.join(SRC_DIR, "capsules", "sovereign", capsule_id)
    os.makedirs(path_dir, exist_ok=True)
    
    manifest = {
        "id": capsule_id,
        "title": f"{domain.capitalize()} Capsule v1",
        "description": f"Sovereign capsule for {domain}.",
        "utid_pattern": f"urn:utid:{domain}:{{node}}:{{nonce}}",
        "energy_prior": f"{domain}_v1",
        "tnn_class": f"tnn.{domain}_tnn.{domain.capitalize()}TNN",
        "safety": {
            "energy_budget_j": 1000000.0,
            "runtime_budget_ms": 10000,
            "entropy_threshold": 10.0
        },
        "prin": {
            "approval_threshold": 0.75,
            "score_weights": {"physics": 0.6, "coherence": 0.2, "novelty": 0.2}
        },
        "visual": {
            "dac_schema": f"frontend/dac_schemas/{capsule_id}.json"
        }
    }
    
    path = os.path.join(path_dir, "manifest.yaml")
    with open(path, "w") as f:
        yaml.dump(manifest, f)
    print(f"Created {path}")

if __name__ == "__main__":
    for d in DOMAINS:
        # Skip fusion as it is already manually created
        if d == "fusion": continue
        
        create_prior(d)
        create_tnn(d)
        create_manifest(d)
