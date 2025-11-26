import argparse
import os
import sys

TEMPLATE_MODEL = """
import torch
import torch.nn as nn
from src.tmf.scaffold.ebdm import BaseEBDM

class {class_name}(BaseEBDM):
    def __init__(self):
        super().__init__(energy_prior_path="priors/energy_map.npy")
        # Define UNet or ScoreNet here
        self.net = nn.Linear(10, 10) # Placeholder

    def score_network(self, x, t):
        # Implement score prediction
        return self.net(x)

    def energy_gradient(self, x):
        # Implement analytic energy gradient -grad(E)(x)
        # E = ...
        return -x # Placeholder
"""

TEMPLATE_TRAIN = """
import torch
from model import {class_name}

def train():
    model = {class_name}()
    # Load data...
    # Loop...
    print("Training {class_name}...")

if __name__ == "__main__":
    train()
"""

TEMPLATE_MANIFEST = """
name: {name}
domain: {domain}
prin_target: 0.75
safety:
  runtime_energy_budget_j: 10000
utid_pattern: HOST-{{sha256(model)}}-{{ts}}
"""

def create_scaffold(name, domain):
    class_name = "".join(x.title() for x in name.split('_'))
    
    base_dir = f"capsules/{name}"
    os.makedirs(f"{base_dir}/data", exist_ok=True)
    os.makedirs(f"{base_dir}/priors", exist_ok=True)
    os.makedirs(f"{base_dir}/tests", exist_ok=True)
    
    # Write model.py
    with open(f"{base_dir}/model.py", "w") as f:
        f.write(TEMPLATE_MODEL.format(class_name=class_name))
        
    # Write train.py
    with open(f"{base_dir}/train.py", "w") as f:
        f.write(TEMPLATE_TRAIN.format(class_name=class_name))
        
    # Write manifest.yaml
    with open(f"{base_dir}/manifest.yaml", "w") as f:
        f.write(TEMPLATE_MANIFEST.format(name=name, domain=domain))
        
    # Write empty energy map placeholder
    with open(f"{base_dir}/priors/energy_map.npy", "w") as f:
        f.write("") # Empty file
        
    print(f"✅ Created EBDM scaffold at {base_dir}")
    print(f"   - model.py")
    print(f"   - train.py")
    print(f"   - manifest.yaml")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Name of the capsule/model")
    parser.add_argument("--domain", required=True, help="Domain (fusion, wafer, etc)")
    args = parser.parse_args()
    
    create_scaffold(args.name, args.domain)
