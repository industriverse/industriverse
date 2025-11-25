import os
import h5py
import numpy as np
import glob

# Configuration
SOURCE_ROOT = "/Volumes/Expansion/datasets/raw/datasets"
OUTPUT_DIR = "/tmp/energy_maps_test"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_energy_map(name, energy_map, formula):
    # Normalize to [0, 1]
    energy_min = np.min(energy_map)
    energy_max = np.max(energy_map)
    if energy_max > energy_min:
        normalized = (energy_map - energy_min) / (energy_max - energy_min)
    else:
        normalized = np.zeros_like(energy_map)
        
    output_path = os.path.join(OUTPUT_DIR, f"{name}_energy_map.npz")
    np.savez_compressed(output_path, energy=normalized)
    
    print(f"✓ {name}")
    print(f"  Shape: {energy_map.shape}")
    print(f"  Saved to: {output_path}")
    print(f"  Formula: {formula}")
    print("-" * 40)

def get_last_frame(dataset):
    # Helper to get the last time step of the first sample
    # Dataset shape could be (Time, ...) or (Sample, Time, ...)
    data = dataset[:]
    if data.ndim >= 4: # (Sample, Time, Y, X, ...)
        return data[0, -1]
    elif data.ndim >= 3: # (Time, Y, X, ...)
        return data[-1]
    return data

def process_turbulent_radiative_layer():
    # Find file
    files = glob.glob(f"{SOURCE_ROOT}/turbulent_radiative_layer_2D/data/test/turbulent_radiative_layer_tcool_0.32.hdf5")
    if not files:
        print("❌ turbulent_radiative_layer file not found")
        return
        
    path = files[0]
    print(f"Processing: {os.path.basename(path)}")
    
    with h5py.File(path, 'r') as f:
        # Keys: t0_fields/density, t0_fields/pressure, t1_fields/velocity
        rho = get_last_frame(f['t0_fields/density'])
        p = get_last_frame(f['t0_fields/pressure'])
        v = get_last_frame(f['t1_fields/velocity']) # Shape (Y, X, 2)
        
        # Calculate Energy
        # v shape is (Y, X, 2) -> vx = v[..., 0], vy = v[..., 1]
        vx = v[..., 0]
        vy = v[..., 1]
        
        gamma = 1.4
        kinetic = 0.5 * rho * (vx**2 + vy**2)
        thermal = p / (gamma - 1)
        energy = kinetic + thermal
        
        save_energy_map("turbulent_radiative_layer_2D", energy, "E = 0.5*rho*v^2 + P/(gamma-1)")

def process_active_matter():
    # Find file
    files = glob.glob(f"{SOURCE_ROOT}/active_matter/data/train/active_matter_L_10.0_zeta_11.0_alpha_-2.0.hdf5")
    if not files:
        print("❌ active_matter file not found")
        return

    path = files[0]
    print(f"Processing: {os.path.basename(path)}")
    
    with h5py.File(path, 'r') as f:
        # Keys: t0_fields/concentration, t1_fields/velocity
        phi = get_last_frame(f['t0_fields/concentration'])
        v = get_last_frame(f['t1_fields/velocity']) # Shape (Y, X, 2)
        
        vx = v[..., 0]
        vy = v[..., 1]
        
        energy = 0.5 * (vx**2 + vy**2) + phi
            
        save_energy_map("active_matter", energy, "E = 0.5*v^2 + concentration")

def process_supernova():
    files = glob.glob(f"{SOURCE_ROOT}/supernova_explosion_64/data/train/supernova_explosion_Msun_1_dim64_file_18.hdf5")
    if not files:
        print("❌ supernova file not found")
        return
        
    path = files[0]
    print(f"Processing: {os.path.basename(path)}")
    
    with h5py.File(path, 'r') as f:
        # Keys: t0_fields/density, t0_fields/pressure, t1_fields/velocity
        rho = get_last_frame(f['t0_fields/density'])
        p = get_last_frame(f['t0_fields/pressure'])
        v = get_last_frame(f['t1_fields/velocity']) # Shape (Z, Y, X, 3)
        
        vx = v[..., 0]
        vy = v[..., 1]
        vz = v[..., 2]
        
        gamma = 1.4
        kinetic = 0.5 * rho * (vx**2 + vy**2 + vz**2)
        thermal = p / (gamma - 1)
        total_3d = kinetic + thermal
        energy = np.sum(total_3d, axis=0) # Sum along z
        
        save_energy_map("supernova_explosion", energy, "E = 0.5*rho*v^2 + P/(gamma-1), summed along z")

def process_mhd():
    # Skipping MHD for now as I didn't verify keys, but structure is likely similar.
    # Focusing on the 3 verified ones.
    pass

if __name__ == "__main__":
    print("Regenerating Energy Maps...")
    try:
        process_turbulent_radiative_layer()
        process_active_matter()
        process_supernova()
        process_mhd()
        print("\nDone.")
    except Exception as e:
        print(f"\nError: {e}")
