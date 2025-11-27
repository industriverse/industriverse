import os
import glob
import h5py
import numpy as np
import torch
from pathlib import Path

# Configuration
DATA_ROOT = "/Volumes/Expansion"
OUTPUT_DIR = "src/ebm_lib/energy_maps"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Keyword Mapping: Capsule Name -> List of Keywords to search in filenames
# The crawler will look for *any* HDF5 file containing these keywords.
DOMAIN_KEYWORDS = {
    "fusion_v1": ["MHD", "plasma", "tokamak"],
    "wafer_v1": ["wafer", "thermal", "diffusion"],
    "robotics_v1": ["robot", "arm", "trajectory"],
    "motor_v1": ["motor", "torque", "harmonic"],
    "battery_v1": ["battery", "cell", "lithium"],
    "grid_v1": ["grid", "frequency", "power"],
    "pcbmfg_v1": ["pcb", "reflow", "solder"],
    "casting_v1": ["casting", "metal", "cooling"],
    "microgrid_v1": ["microgrid", "solar", "load"],
    "apparel_v1": ["apparel", "fabric", "tension"],
    "heat_v1": ["hvac", "building", "climate"],
    "electronics_v1": ["converter", "buck", "boost"],
    "failure_v1": ["failure", "anomaly", "log"],
    "lifecycle_v1": ["yield", "process", "sigma"],
    "qctherm_v1": ["qc", "thermography", "ir"],
    # Add generic keywords for others or leave empty to rely on synthetic
}

def find_file_by_keywords(keywords):
    """Scan drive for files matching keywords."""
    # This is a simplified crawler. In production, we'd index the drive first.
    # Here we use 'find' via glob if possible, or just walk.
    # Walking 10TB is slow, so we look in specific known dirs or use a broad glob if provided.
    # For this implementation, we'll assume a structured dataset folder exists or look recursively.
    
    # Optimization: Look in datasets/raw first
    search_roots = [
        os.path.join(DATA_ROOT, "datasets", "raw"),
        DATA_ROOT
    ]
    
    for root in search_roots:
        if not os.path.exists(root): continue
        for dirpath, _, filenames in os.walk(root):
            for f in filenames:
                if not f.endswith(".hdf5"): continue
                f_lower = f.lower()
                if any(k.lower() in f_lower for k in keywords):
                    return os.path.join(dirpath, f)
    return None

def generate_map(capsule_name, keywords):
    print(f"[{capsule_name}] Crawling for keywords: {keywords}...")
    
    file_path = find_file_by_keywords(keywords)
    
    if file_path:
        print(f"  > FOUND REAL DATA: {file_path}")
        try:
            with h5py.File(file_path, 'r') as f:
                # Extraction Logic (Simplified Generic)
                # We try to find a 3D or 4D dataset to use as the map
                dataset = None
                
                def find_dataset(name, obj):
                    nonlocal dataset
                    if dataset is not None: return
                    if isinstance(obj, h5py.Dataset) and obj.ndim >= 3:
                        dataset = obj
                
                f.visititems(find_dataset)
                
                if dataset is not None:
                    # Load and downsample to 32x32x3 (or similar)
                    # This is a very rough heuristic for the demo
                    data = dataset[:]
                    # Simple resize/slice to target shape (32, 32, 3)
                    # Real ETL would be more sophisticated
                    if data.ndim == 3:
                        data = data[:32, :32, :3] # Slice
                    elif data.ndim == 4:
                        data = data[0, :32, :32, :3] # Time slice
                    elif data.ndim == 5: # MHD
                         data = data[0, 0, :32, :32, :3]
                    
                    # Pad if too small
                    if data.shape != (32, 32, 3):
                         # Just fallback to synthetic if shape is weird for now
                         print(f"    > Shape {data.shape} mismatch. Using synthetic fallback.")
                         data = None
                else:
                    data = None

                if data is not None:
                    save_path = os.path.join(OUTPUT_DIR, f"{capsule_name}.npz")
                    np.savez_compressed(save_path, energy_map=data)
                    print(f"  > Generated REAL Energy Map: {save_path}")
                    return

        except Exception as e:
            print(f"  > Error reading {file_path}: {e}")
    
    # Fallback to Synthetic (Ideal State) if no file or error
    print(f"  > No valid data found. Generating synthetic baseline (Ideal State).")
    
    # Default shape
    shape = (32, 32, 3)
    if capsule_name == "pcbmfg_v1": shape = (32, 32, 4)
    if capsule_name == "apparel_v1": shape = (32, 32, 4)
    if capsule_name == "wafer_v1": shape = (32, 32, 5)
    
    dummy_data = np.zeros(shape, dtype=np.float32) + 0.001 * np.random.randn(*shape).astype(np.float32)
    
    # Specific overrides (Ideal Targets)
    if capsule_name == "wafer_v1": dummy_data += 1000.0
    if capsule_name == "pcbmfg_v1": dummy_data[:] = [2.0, 175.0, 245.0, 4.0]
    if capsule_name == "casting_v1": dummy_data[:] = [50.0, 1000.0, 0.0]
    if capsule_name == "microgrid_v1": dummy_data[:] = [100.0, 100.0, 60.0]
    if capsule_name == "battery_v1": dummy_data[:] = [4.0, 25.0, 0.8]
    if capsule_name == "apparel_v1": dummy_data += 5.0
    if capsule_name == "heat_v1": dummy_data[:] = [22.0, 0.0, 0.0]
    if capsule_name == "grid_v1": dummy_data[:] = [60.0, 0.0, 0.0]
    if capsule_name == "electronics_v1": dummy_data[:] = [0.0, 0.41, 0.0]
    if capsule_name == "failure_v1": dummy_data[:] = [0.0, 0.0, 0.0]
    if capsule_name == "lifecycle_v1": dummy_data[:] = [0.0, 0.0, 0.0]
    if capsule_name == "qctherm_v1": dummy_data[:] = [80.0, 100.0, 0.0]
    
    np.savez_compressed(os.path.join(OUTPUT_DIR, f"{capsule_name}.npz"), energy_map=dummy_data)

def main():
    print("=== Physics Crawler: Scaling to 10TB ===")
    
    # 1. Process all domains
    all_capsules = [
        "fusion_v1", "wafer_v1", "robotics_v1", "motor_v1", "battery_v1", "grid_v1",
        "pcbmfg_v1", "casting_v1", "microgrid_v1", "apparel_v1", "heat_v1", 
        "electronics_v1", "failure_v1", "lifecycle_v1", "qctherm_v1",
        "chem_v1", "polymer_v1", "assembly_v1", "amrsafety_v1", "sensorint_v1",
        "surface_v1", "workforce_v1", "schedule_v1", "magnet_v1", "chassis_v1",
        "metal_v1", "cnc_v1"
    ]
    
    for cap in all_capsules:
        keywords = DOMAIN_KEYWORDS.get(cap, [])
        generate_map(cap, keywords)

if __name__ == "__main__":
    main()
