"""
Example script to run the thermodynamic discovery loop end-to-end.
"""

import os
import shutil
# import torch # Not available in this env
from discovery_loop_v16.discovery.runner import run_discovery

def create_mock_lora(path):
    """Create a dummy LoRA file for testing."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Create a dummy file
    with open(path, "wb") as f:
        f.write(b"mock_lora_bytes")
    print(f"Created mock LoRA at {path}")

def main():
    # Setup paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    lora_path = os.path.join(base_dir, "mock_data", "mock_lora.pt")
    out_dir = os.path.join(base_dir, "output_capsules")
    
    # Clean previous output
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    # Create mock LoRA
    create_mock_lora(lora_path)
    
    # Define dataset metadata
    dataset_meta = {
        "dataset_name": "MOCK_FUSION_DATASET",
        "domain": "fusion",
        "meta_score": 0.85
    }
    
    print("\n--- Starting Discovery Loop V16 ---")
    result = run_discovery(
        dataset_meta=dataset_meta,
        lora_path=lora_path,
        out_dir=out_dir,
        num_candidates=4
    )
    
    print("\n--- Discovery Complete ---")
    print(f"Duration: {result['duration_s']:.2f}s")
    print(f"Approved Candidates: {result['approved_count']}")
    print(f"Generated Capsules: {len(result['capsules'])}")
    
    for cap in result['capsules']:
        print(f" - {cap}")

if __name__ == "__main__":
    main()
