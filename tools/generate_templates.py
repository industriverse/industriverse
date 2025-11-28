import os
import argparse

DOMAINS = [
    "fusion", "grid", "wafer", "motor", "battery", "cnc", "chassis", "microgrid",
    "casting", "heat", "chem", "polymer", "metal", "pipeline", "qctherm", "failure",
    "robotics", "matflow", "workforce", "schedule", "amrsafety", "conveyor", "assembly",
    "electronics", "pcbmfg", "sensorint", "surface", "lifecycle", "apparel"
]

PRIOR_TEMPLATE = """
import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class {class_name}Prior(EnergyPrior):
    name = "{domain}_v1"
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        # Placeholder physics for {domain}
        # x: [batch, features]
        target = torch.zeros_like(x)
        # Simple quadratic potential (harmonic oscillator)
        return 0.5 * (x - target).pow(2).sum(dim=-1)

prior = {class_name}Prior()
prior.register()
"""

TNN_TEMPLATE = """
import torch
from torch import nn

class {class_name}TNN(nn.Module):
    def forward(self, x, t):
        # Placeholder dynamics for {domain}
        # dx/dt = -x (decay)
        return -0.1 * x
"""

def generate(out_dir):
    priors_dir = os.path.join(out_dir, "src/ebm_lib/priors")
    tnn_dir = os.path.join(out_dir, "src/tnn")
    capsules_dir = os.path.join(out_dir, "src/capsules/sovereign")
    
    os.makedirs(priors_dir, exist_ok=True)
    os.makedirs(tnn_dir, exist_ok=True)
    os.makedirs(capsules_dir, exist_ok=True)
    
    # Create __init__.py files
    open(os.path.join(priors_dir, "__init__.py"), 'w').close()
    open(os.path.join(tnn_dir, "__init__.py"), 'w').close()

    for domain in DOMAINS:
        class_name = domain.capitalize()
        
        # 1. Create Prior
        with open(os.path.join(priors_dir, f"{domain}_v1.py"), "w") as f:
            f.write(PRIOR_TEMPLATE.format(class_name=class_name, domain=domain))
            
        # 2. Create TNN
        with open(os.path.join(tnn_dir, f"{domain}_tnn.py"), "w") as f:
            f.write(TNN_TEMPLATE.format(class_name=class_name, domain=domain))
            
        # 3. Create Capsule Manifest
        cap_dir = os.path.join(capsules_dir, f"{domain}_v1")
        os.makedirs(cap_dir, exist_ok=True)
        
        manifest = f"""
dac_id: {domain}_v1
version: 1.0.0
energy_prior: src.ebm_lib.priors.{domain}_v1
tnn_solver: src.tnn.{domain}_tnn
inputs: [state_vector]
outputs: [optimized_state]
"""
        with open(os.path.join(cap_dir, "manifest.yaml"), "w") as f:
            f.write(manifest.strip())
            
        print(f"Generated {domain} capsule.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=".")
    args = parser.parse_args()
    generate(args.out)
