from pathlib import Path
from typing import List

class ShardedFossilLoader:
    def get_shard_files(self, all_files: List[Path], rank: int, world_size: int) -> List[Path]:
        """
        Returns the subset of files this rank should process.
        """
        if world_size <= 1:
            return all_files
            
        # Deterministic sort to ensure consistent sharding
        all_files = sorted(all_files)
        
        # Split
        my_files = all_files[rank::world_size]
        return my_files
