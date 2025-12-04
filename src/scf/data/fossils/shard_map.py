import json
import logging
from pathlib import Path
from typing import List, Dict, Any

LOG = logging.getLogger("SCF.FossilShardMap")

class FossilShardMap:
    def __init__(self, index_path: str = "data/energy_atlas/shard_index.json"):
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.shards: List[Dict[str, Any]] = []
        self._load_index()

    def _load_index(self):
        if self.index_path.exists():
            try:
                self.shards = json.loads(self.index_path.read_text())
            except Exception:
                self.shards = []

    def _save_index(self):
        self.index_path.write_text(json.dumps(self.shards, indent=2))

    def register_shard(self, shard_path: str, fossil_count: int, size_bytes: int, entropy_stats: Dict[str, float]):
        shard_entry = {
            "path": str(shard_path),
            "count": fossil_count,
            "size": size_bytes,
            "entropy_mean": entropy_stats.get("mean", 0.0),
            "entropy_var": entropy_stats.get("var", 0.0),
            "status": "ACTIVE"
        }
        # Remove existing if path matches
        self.shards = [s for s in self.shards if s["path"] != str(shard_path)]
        self.shards.append(shard_entry)
        self._save_index()
        LOG.info("Registered shard: %s (%d fossils)", shard_path, fossil_count)

    def get_shards_by_entropy(self, min_ent: float, max_ent: float) -> List[str]:
        return [s["path"] for s in self.shards if min_ent <= s["entropy_mean"] <= max_ent]

    def get_all_shards(self) -> List[str]:
        return [s["path"] for s in self.shards if s["status"] == "ACTIVE"]
