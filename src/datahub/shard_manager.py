import os
import json
import glob
import time
import logging
import gzip
import sys
from typing import List, Dict, Any

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/datahub/manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ShardManager")

class ShardManager:
    """
    Industriverse Data Hub: Shard Manager (Production Ready).
    
    Purpose:
    Aggregates raw shards into structured datasets (ManuBase-1).
    Features: Metadata indexing, Compression, Integrity Checks.
    """
    def __init__(self, raw_dir="data/datahub/raw", processed_dir="data/datahub/processed"):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        os.makedirs(self.processed_dir, exist_ok=True)
        
    def scan_raw_shards(self) -> List[str]:
        shards = glob.glob(os.path.join(self.raw_dir, "*.json"))
        logger.info(f"Found {len(shards)} raw shards.")
        return shards

    def validate_shard(self, shard_path: str) -> Dict[str, Any]:
        """
        Checks if shard is valid JSON and has required fields.
        """
        try:
            with open(shard_path, 'r') as f:
                data = json.load(f)
            if "timestamp" not in data or "source" not in data:
                logger.warning(f"Shard {shard_path} missing required fields.")
                return None
            return data
        except json.JSONDecodeError:
            logger.error(f"Shard {shard_path} is corrupt.")
            return None

    def aggregate_dataset(self, dataset_name="ManuBase-1", compress=True):
        """
        Aggregates shards into a dataset.
        """
        shards = self.scan_raw_shards()
        if not shards:
            logger.info("No raw shards to process.")
            return
            
        logger.info(f"Aggregating {len(shards)} shards into {dataset_name}...")
        
        dataset = []
        valid_shards = []
        
        for shard_path in shards:
            data = self.validate_shard(shard_path)
            if data:
                dataset.append(data)
                valid_shards.append(shard_path)
                
        if not dataset:
            logger.warning("No valid data found after validation.")
            return

        # Generate Metadata
        metadata = {
            "dataset_name": dataset_name,
            "created_at": time.time(),
            "sample_count": len(dataset),
            "sources": list(set(d["source"] for d in dataset)),
            "schema_version": "1.0"
        }
        
        # Save Dataset
        filename = f"{dataset_name}.json"
        if compress:
            filename += ".gz"
            output_path = os.path.join(self.processed_dir, filename)
            with gzip.open(output_path, 'wt', encoding='utf-8') as f:
                json.dump({"metadata": metadata, "data": dataset}, f)
        else:
            output_path = os.path.join(self.processed_dir, filename)
            with open(output_path, 'w') as f:
                json.dump({"metadata": metadata, "data": dataset}, f, indent=2)
            
        logger.info(f"✅ Dataset created at {output_path}")
        logger.info(f"   Samples: {len(dataset)}")
        
        # Cleanup
        self.cleanup_shards(valid_shards)

    def cleanup_shards(self, shard_paths: List[str]):
        for p in shard_paths:
            try:
                os.remove(p)
            except OSError as e:
                logger.error(f"Failed to delete {p}: {e}")
        logger.info(f"Cleaned up {len(shard_paths)} shards.")

if __name__ == "__main__":
    manager = ShardManager()
    manager.aggregate_dataset(compress=False) # No compression for demo readability
