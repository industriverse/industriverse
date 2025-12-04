#!/usr/bin/env python3
import json
import time
import random
import argparse
from pathlib import Path
from src.scf.config import FOSSIL_VAULT

def generate_fossil(index: int, size_mb: int = 1):
    """Generates a synthetic fossil file."""
    filename = FOSSIL_VAULT / f"fossil-synthetic-{int(time.time())}-{index:04d}.ndjson"
    
    # Create dummy content to reach size_mb
    # 1MB ~ 1000 lines of 1KB each
    lines = size_mb * 1000
    
    with open(filename, "w") as f:
        for i in range(lines):
            sample = {
                "id": f"syn-{index}-{i}",
                "timestamp": time.time(),
                "energy": random.random() * 100,
                "features": [random.random() for _ in range(128)], # Small embedding
                "metadata": "synthetic_physics_data" * 10
            }
            f.write(json.dumps(sample) + "\n")
            
    print(f"Generated {filename} ({size_mb} MB)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5, help="Number of fossils to generate")
    parser.add_argument("--size", type=int, default=1, help="Size in MB per fossil")
    args = parser.parse_args()
    
    FOSSIL_VAULT.mkdir(parents=True, exist_ok=True)
    
    for i in range(args.count):
        generate_fossil(i, args.size)
