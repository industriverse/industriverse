import json
import os
import random
import logging
from pathlib import Path
from typing import Iterator, List, Dict, Optional

from src.scf.config import EXTERNAL_DRIVE, FOSSIL_VAULT

LOG = logging.getLogger("SCF.FossilBatcher")

class FossilBatcher:
    def __init__(self, vault_path: Path = FOSSIL_VAULT):
        self.vault_path = vault_path
        if not self.vault_path.exists():
            # Fallback for testing if drive not mounted
            self.vault_path = Path("data/energy_atlas/raw_fossils")

    def iterate_fossils(self, shuffle: bool = True) -> Iterator[Path]:
        """Yields fossil file paths from the vault."""
        # Support both single JSON and NDJSON
        files = list(self.vault_path.glob("fossil-*.ndjson")) + list(self.vault_path.glob("fossil-*.json"))
        
        if not files:
            LOG.warning("No fossils found in %s", self.vault_path)
            return

        if shuffle:
            random.shuffle(files)
            
        for f in files:
            yield f

    def fossil_stream(self, fossil_path: Path) -> Iterator[Dict]:
        """Streams samples from a single fossil file."""
        try:
            with fossil_path.open("r", encoding="utf-8") as fh:
                if fossil_path.suffix == '.json':
                    # Standard JSON (load whole file)
                    data = json.load(fh)
                    if isinstance(data, list):
                        for item in data:
                            yield item
                    elif isinstance(data, dict):
                        yield data
                else:
                    # NDJSON (Line delimited)
                    for line in fh:
                        if not line.strip(): continue
                        try:
                            yield json.loads(line)
                        except Exception:
                            continue
        except Exception as e:
            LOG.error("Error reading fossil %s: %s", fossil_path, e)

    def stream_minibatches(self, batch_size: int = 64, fossils_to_consume: Optional[int] = None) -> Iterator[List[Dict]]:
        """
        Yields minibatches of samples by streaming from disk.
        This ensures we never load the full dataset into RAM.
        """
        consumed_fossils = 0
        current_batch = []

        for fossil_file in self.iterate_fossils():
            for sample in self.fossil_stream(fossil_file):
                current_batch.append(sample)
                
                if len(current_batch) >= batch_size:
                    yield current_batch
                    current_batch = []
            
            consumed_fossils += 1
            if fossils_to_consume and consumed_fossils >= fossils_to_consume:
                break
        
        # Yield remaining samples
        if current_batch:
            yield current_batch

if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    batcher = FossilBatcher()
    count = 0
    for batch in batcher.stream_minibatches(batch_size=10, fossils_to_consume=1):
        print(f"Yielded batch of size {len(batch)}")
        count += 1
    print(f"Total batches: {count}")
