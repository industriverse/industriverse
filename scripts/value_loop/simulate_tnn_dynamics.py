#!/usr/bin/env python3
"""
Script 5: simulate_tnn_dynamics.py
Purpose: Runs time-domain simulations using Diffusion Dynamics (TNN + IDF).
Usage: python simulate_tnn_dynamics.py --capsule <name> --steps 50
"""

import argparse
import sys
import os
import json
import logging
import numpy as np
import importlib
import yaml

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from frameworks.idf.core.diffusion_dynamics import DiffusionDynamics
from frameworks.idf.core.energy_field import EnergyField

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_manifest(capsule_name):
    path = os.path.join("src", "capsules", "sovereign", f"{capsule_name}_v1", "manifest.yaml")
    if not os.path.exists(path):
        # Try without _v1
        path = os.path.join("src", "capsules", "sovereign", capsule_name, "manifest.yaml")
        
    if not os.path.exists(path):
        logger.error(f"Manifest for {capsule_name} not found.")
        sys.exit(1)
        
    with open(path, "r") as f:
        return yaml.safe_load(f)

def import_class(path):
    try:
        mod_name, cls_name = path.rsplit(".", 1)
        mod = importlib.import_module(mod_name)
        return getattr(mod, cls_name)
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import TNN class {path}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Simulate TNN dynamics with Diffusion.")
    parser.add_argument("--capsule", type=str, required=True, help="Capsule name (e.g., fusion, grid).")
    parser.add_argument("--steps", type=int, default=50, help="Simulation steps.")
    parser.add_argument("--use_diffusion", action="store_true", help="Inject IDF diffusion noise.")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path.")
    
    args = parser.parse_args()
    
    logger.info(f"Loading capsule: {args.capsule}")
    manifest = load_manifest(args.capsule)
    
    tnn_class_path = manifest.get("tnn_class")
    if not tnn_class_path:
        logger.error("No TNN class defined in manifest.")
        sys.exit(1)
        
    TNNClass = import_class(tnn_class_path)
    if not TNNClass:
        sys.exit(1)
        
    tnn = TNNClass()
    
    # Initial State Heuristics (same as run_all_demos)
    state = {}
    if "fusion" in args.capsule:
        state={"B": np.random.randn(8,3)*0.1, "v": np.random.randn(8,3)*0.01, "rho":1.0}
    elif "wafer" in args.capsule:
        state={"temperature_grid": np.random.randn(16,16)}
    elif "grid" in args.capsule:
        state={"frequency": 60.0}
    else:
        state = {"state_vector": np.random.randn(16)}
        
    logger.info(f"Running TNN Simulation ({args.steps} steps)...")
    
    # Run Base Simulation
    result = tnn.simulate(state, {}, dt=0.05, steps=args.steps)
    
    # If Diffusion enabled, we post-process or co-process
    # Since TNN interface is fixed, we'll simulate "Diffusion Injection" by modifying the trajectory
    if args.use_diffusion:
        logger.info("Injecting Energy-Based Diffusion Noise...")
        field = EnergyField(f"{args.capsule}_map")
        dynamics = DiffusionDynamics(field, learning_rate=0.01, temperature=0.1)
        
        # We assume the state has a 'state_vector' or similar we can diffuse
        # For complex states (B, v), we'd need a mapping. 
        # For this demo, we'll just diffuse a parallel 'energy_state' vector
        
        diffused_traj = []
        x_curr = np.random.rand(2) # 2D abstract state on the energy map
        
        for step in result["trajectory"]:
            x_curr = dynamics.step(x_curr)
            step["diffusion_state"] = x_curr.tolist()
            step["energy_potential"] = field.get_energy(x_curr)
            
    # Serialize
    if args.output:
        # Convert numpy
        for step in result["trajectory"]:
            for k, v in step.items():
                if isinstance(v, np.ndarray):
                    step[k] = v.tolist()
                    
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        logger.info(f"Simulation saved to {args.output}")
    else:
        logger.info("Simulation complete (output suppressed, use --output to save).")

if __name__ == "__main__":
    main()
