import sys
import h5py
import json
import os
import argparse

ATLAS_PATH = "/Volumes/Expansion/industriverse_datasets/energy_atlas_v1.h5"

def search_atlas(max_energy=None, max_time=None, material=None, limit=5):
    """
    Searches the Energy Atlas for models matching the criteria.
    """
    if not os.path.exists(ATLAS_PATH):
        return {"error": "Atlas not found"}

    results = []
    
    try:
        with h5py.File(ATLAS_PATH, 'r') as f:
            if 'planned' not in f:
                return {"error": "Invalid Atlas format"}
            
            planned = f['planned']
            
            for model_id in planned.keys():
                attrs = planned[model_id].attrs
                
                # Extract Metrics
                energy = attrs.get('total_energy_j', 0.0)
                time = attrs.get('estimated_time_s', 0.0)
                filament = attrs.get('filament_used_cm3', 0.0)
                
                # Apply Filters
                if max_energy and energy > max_energy: continue
                if max_time and time > max_time: continue
                # Material filter would check filament type if available (future)
                
                results.append({
                    "id": model_id,
                    "energy_j": energy,
                    "time_s": time,
                    "filament_cm3": filament,
                    "score": energy # Lower is better
                })
                
            # Sort by Score (Energy Efficiency)
            results.sort(key=lambda x: x['score'])
            
            return {
                "count": len(results),
                "top_matches": results[:limit]
            }
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search the Energy Atlas")
    parser.add_argument("--max_energy", type=float, help="Max Energy in Joules")
    parser.add_argument("--max_time", type=float, help="Max Time in Seconds")
    parser.add_argument("--limit", type=int, default=5, help="Max results")
    
    args = parser.parse_args()
    
    result = search_atlas(args.max_energy, args.max_time, limit=args.limit)
    print(json.dumps(result, indent=2))
