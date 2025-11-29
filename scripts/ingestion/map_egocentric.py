import os
import json
import glob

DATASET_ROOT = "/Volumes/Expansion/Egocentric-10K"
OUTPUT_FILE = "data/egocentric_index.json"

def map_dataset():
    print(f"🔍 Scanning {DATASET_ROOT}...")
    
    index = {
        "factory_001": {
            "workers": {}
        }
    }
    
    # Scan for workers in Factory 001
    worker_dirs = glob.glob(os.path.join(DATASET_ROOT, "factory_001", "workers", "worker_*"))
    
    for w_dir in worker_dirs:
        worker_id = os.path.basename(w_dir)
        print(f"  Found {worker_id}")
        
        # Find video files (assuming .mp4 or .tar containing videos - for now just listing files)
        # The dataset structure has .tar files. We might need to untar them or just index the tars.
        # For this phase, let's index the .tar files as "chunks".
        files = sorted(glob.glob(os.path.join(w_dir, "*")))
        
        index["factory_001"]["workers"][worker_id] = {
            "path": w_dir,
            "chunks": files
        }
        
    print(f"✅ Indexed {len(index['factory_001']['workers'])} workers.")
    
    # Ensure data dir exists
    os.makedirs("data", exist_ok=True)
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(index, f, indent=2)
    
    print(f"💾 Index saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    if not os.path.exists(DATASET_ROOT):
        print(f"❌ Error: {DATASET_ROOT} not found.")
    else:
        map_dataset()
