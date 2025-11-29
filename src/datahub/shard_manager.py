import os
import json
import glob
import time
from typing import List

class ShardManager:
    """
    Industriverse Data Hub: Shard Manager.
    
    Purpose:
    Aggregates raw shards into structured datasets (ManuBase-1).
    Manages storage lifecycle (Raw -> Verified -> Compressed).
    """
    def __init__(self, raw_dir="data/datahub/raw", processed_dir="data/datahub/processed"):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        os.makedirs(self.processed_dir, exist_ok=True)
        
    def scan_raw_shards(self) -> List[str]:
        return glob.glob(os.path.join(self.raw_dir, "*.json"))

    def aggregate_dataset(self, dataset_name="ManuBase-1"):
        """
        Aggregates all raw shards into a single dataset file.
        """
        shards = self.scan_raw_shards()
        if not shards:
            print("ShardManager: No raw shards found.")
            return
            
        print(f"ShardManager: Aggregating {len(shards)} shards into {dataset_name}...")
        
        dataset = []
        for shard_path in shards:
            with open(shard_path, 'r') as f:
                dataset.append(json.load(f))
                
        # Save as "Parquet" (Mock: JSON)
        output_path = os.path.join(self.processed_dir, f"{dataset_name}.json")
        with open(output_path, 'w') as f:
            json.dump(dataset, f, indent=2)
            
        print(f"✅ Dataset {dataset_name} created at {output_path}")
        print(f"   Total Samples: {len(dataset)}")
        
        # Cleanup raw shards
        for shard_path in shards:
            os.remove(shard_path)
        print("   Raw shards cleaned up.")

if __name__ == "__main__":
    manager = ShardManager()
    manager.aggregate_dataset()
