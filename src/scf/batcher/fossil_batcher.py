import json
import os
import pickle
import uuid
from pathlib import Path
from typing import Iterator, List, Dict, Any
import torch

from src.scf.config import FOSSIL_VAULT

class FossilBatcher:
    def __init__(self, fossils_dir: str = None, batch_dir: str = "data/energy_atlas/fossil_batches", batch_size: int = 250):
        # Use config path if not provided
        self.fossils_dir = Path(fossils_dir) if fossils_dir else FOSSIL_VAULT
        self.batch_dir = Path(batch_dir)
        self.batch_size = batch_size
        self.fossils_dir.mkdir(parents=True, exist_ok=True)
        self.batch_dir.mkdir(parents=True, exist_ok=True)

    def load_fossils_stream(self) -> Iterator[Dict[str, Any]]:
        """Yields one fossil at a time (memory safe)."""
        # Supports both individual JSON files and NDJSON streams
        for fp in self.fossils_dir.glob("**/*.json"):
            try:
                yield json.load(open(fp))
            except Exception:
                pass
        
        for fp in self.fossils_dir.glob("**/*.ndjson"):
            try:
                with open(fp) as f:
                    for line in f:
                        if line.strip():
                            yield json.loads(line)
            except Exception:
                pass

    def aggregate_batch(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Turn raw fossils -> training tensors."""
        # Extract features. If missing, use placeholders (for mock/bootstrap)
        tnn_features = []
        ebdm_features = []
        
        for s in samples:
            # TNN expects entropy gradient or similar physics scalar/vector
            grad = s.get("entropy_gradient", 0.0)
            if isinstance(grad, (float, int)):
                grad = [grad] # ensure vector
            tnn_features.append(grad)
            
            # EBDM expects energy signature (embedding)
            # Handle potential dicts or lists
            sig = s.get("energy_signature", s.get("features", [0.0]*128))
            if isinstance(sig, dict):
                # Fallback if features are a dict (e.g. from some synthetic generators)
                sig = list(sig.values())
            if not isinstance(sig, list):
                sig = [0.0]*128
            
            ebdm_features.append(sig)

        tnn_tensor = torch.tensor(tnn_features, dtype=torch.float32)
        ebdm_tensor = torch.tensor(ebdm_features, dtype=torch.float32)

        return {
            "batch_id": uuid.uuid4().hex,
            "samples": samples, # Keep raw metadata
            "tnn_ready_tensor": tnn_tensor,
            "ebdm_ready_tensor": ebdm_tensor,
            "negentropy_score": float(tnn_tensor.mean()),
            "entropy_variance": float(tnn_tensor.var()) if tnn_tensor.numel() > 1 else 0.0,
        }

    def build_batches(self):
        """Reads fossils and writes batch files."""
        buffer = []
        count = 0
        for fossil in self.load_fossils_stream():
            buffer.append(fossil)
            if len(buffer) >= self.batch_size:
                batch = self.aggregate_batch(buffer)
                self.save_batch(batch)
                buffer = []
                count += 1
        
        # Flush remaining
        if buffer:
            batch = self.aggregate_batch(buffer)
            self.save_batch(batch)
            count += 1
        return count

    def save_batch(self, batch: Dict[str, Any]):
        fp = self.batch_dir / f"batch_{batch['batch_id']}.pkl"
        with open(fp, "wb") as f:
            pickle.dump(batch, f)

    # Helper for the Daemon to ingest a stream and return count
    def ingest_stream(self, batch_target_count=10) -> int:
        # In a real system, this would track processed files to avoid re-ingestion.
        # For now, we just run build_batches which processes everything found.
        # To make it "stream" in a daemon, we'd move processed files to an archive.
        return self.build_batches()

    def ready_for_training(self) -> bool:
        return any(self.batch_dir.glob("*.pkl"))

    def build_batch(self) -> Dict[str, Any]:
        # Return a single batch for immediate training (mocking the queue pop)
        # In prod, this would pop from a queue or pick a random file
        files = list(self.batch_dir.glob("*.pkl"))
        if not files:
            return None
        with open(files[0], "rb") as f:
            return pickle.load(f)
