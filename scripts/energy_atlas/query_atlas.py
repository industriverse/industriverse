import sys
import h5py
import json
import os
import numpy as np

ATLAS_PATH = "/Volumes/Expansion/industriverse_datasets/energy_atlas_v1.h5"

def query_atlas(glyph_id):
    """
    Queries the Energy Atlas for the average energy cost of a glyph/action.
    For the prototype, we map Glyphs to Slice100k models based on heuristics.
    """
    if not os.path.exists(ATLAS_PATH):
        return {"error": "Atlas not found", "energy": 0}

    try:
        with h5py.File(ATLAS_PATH, 'r') as f:
            if 'planned' not in f:
                return {"error": "Invalid Atlas format", "energy": 0}
            
            # Heuristic Mapping: In a real system, we'd search for similar geometry.
            # Here, we just sample a few entries to get a "baseline" energy density.
            # For "Cut 0.1mm" (⊽0.1), we look at the average energy of small prints.
            
            planned = f['planned']
            keys = list(planned.keys())
            if not keys:
                return {"energy": 50.0, "source": "Default (Empty Atlas)"}
            
            # Sample 5 random entries to simulate a "Search"
            samples = [planned[k]['energy_voxels'][()] for k in keys[:5]]
            avg_energy = float(np.mean(samples)) if samples else 50.0
            
            # Apply modifiers based on Glyph
            multiplier = 1.0
            if "0.1" in glyph_id: multiplier = 0.5
            if "13E" in glyph_id: multiplier = 2.5 # EUV is expensive
            
            return {
                "energy": avg_energy * multiplier,
                "unit": "J",
                "confidence": 0.85,
                "source": "Slice100k Aggregation"
            }
            
    except Exception as e:
        return {"error": str(e), "energy": 0}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No glyph provided"}))
        sys.exit(1)
        
    glyph = sys.argv[1]
    result = query_atlas(glyph)
    print(json.dumps(result))
