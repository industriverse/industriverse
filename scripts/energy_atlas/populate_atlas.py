import os
import sys
import glob
import numpy as np
from tqdm import tqdm

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.energy_atlas.bgcode_decoder import BGCodeDecoder
from src.energy_atlas.atlas_builder import EnergyAtlas

SAMPLE_DIR = "/Volumes/Expansion/industriverse_datasets/slice100k/samples/GCode_1"
ATLAS_PATH = "/Volumes/Expansion/industriverse_datasets/energy_atlas_v1.h5"

def populate_atlas():
    decoder = BGCodeDecoder()
    
    # 1. Find Files
    files = glob.glob(os.path.join(SAMPLE_DIR, "*.bgcode"))
    print(f"Found {len(files)} sample files.")
    
    # 2. Open Atlas
    with EnergyAtlas(ATLAS_PATH, mode='w') as atlas:
        print(f"Created Energy Atlas at {ATLAS_PATH}")
        
        success_count = 0
        for fpath in tqdm(files):
            try:
                # Decode Metadata
                meta = decoder.decode_header(fpath)
                
                # Extract Energy Proxies
                # Energy = Power * Time
                # Assume avg power = 100W (heater + motors)
                print_time_str = meta.get('estimated printing time (normal mode)', '0m 0s')
                # Parse time string "27m 5s" -> seconds
                total_seconds = 0
                parts = print_time_str.split()
                for p in parts:
                    if 'h' in p: total_seconds += int(p.replace('h', '')) * 3600
                    if 'm' in p: total_seconds += int(p.replace('m', '')) * 60
                    if 's' in p: total_seconds += int(p.replace('s', ''))
                
                energy_joules = 100.0 * total_seconds
                
                # Create Mock Voxel Grid (Placeholder until full decode)
                # We'll store a 1x1x1 voxel with the total energy for now
                energy_voxels = np.array([[[energy_joules]]])
                material_voxels = np.array([[[1]]]) # 1 = PLA (Mock)
                geometry_voxels = np.array([[[1]]]) # 1 = Solid (Mock)
                
                # Add to Atlas
                model_id = os.path.basename(fpath).replace('.bgcode', '')
                atlas.add_planned_voxel_grid(
                    model_id, 
                    energy_voxels, 
                    material_voxels, 
                    geometry_voxels, 
                    energy_joules, 
                    meta
                )
                success_count += 1
                
            except Exception as e:
                print(f"Failed {fpath}: {e}")
                pass
                
        print(f"Successfully populated {success_count} entries into the Energy Atlas.")

if __name__ == "__main__":
    populate_atlas()
