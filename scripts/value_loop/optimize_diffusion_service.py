#!/usr/bin/env python3
"""
Script 3: optimize_diffusion_service.py
Purpose: CLI wrapper for the Energy-Based Diffusion Engine (IDF).
Usage: python optimize_diffusion_service.py --map_name <domain_map> --steps 100
"""

import argparse
import sys
import os
import json
import logging
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from frameworks.idf.layers.eil_optimizer import EILOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Optimize configuration using Energy-Based Diffusion (IDF).")
    parser.add_argument("--map_name", type=str, required=True, help="Name of the energy map (domain).")
    parser.add_argument("--steps", type=int, default=100, help="Number of diffusion steps.")
    parser.add_argument("--output", type=str, default=None, help="Path to save output JSON.")
    
    args = parser.parse_args()
    
    logger.info(f"Initializing EIL Optimizer for map: {args.map_name}")
    optimizer = EILOptimizer(args.map_name)
    
    logger.info(f"Running optimization for {args.steps} steps...")
    result = optimizer.optimize_configuration(steps=args.steps)
    
    logger.info("Optimization Complete.")
    logger.info(f"Start Energy: {result['start_energy']:.4f}")
    logger.info(f"Final Energy: {result['final_energy']:.4f}")
    logger.info(f"Energy Delta: {result['energy_delta']:.4f}")
    logger.info(f"Converged: {result['converged']}")
    
    # Convert numpy arrays to list for JSON
    out_data = {
        "map_name": args.map_name,
        "steps": args.steps,
        "start_energy": float(result["start_energy"]),
        "final_energy": float(result["final_energy"]),
        "energy_delta": float(result["energy_delta"]),
        "trajectory_entropy": float(result["trajectory_entropy"]),
        "converged": bool(result["converged"]),
        "final_config_sample": np.array(result["final_config"]).flatten().tolist()[:20] # Sample
    }
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(out_data, f, indent=2)
        logger.info(f"Result saved to {args.output}")
    else:
        print(json.dumps(out_data, indent=2))

if __name__ == "__main__":
    main()
