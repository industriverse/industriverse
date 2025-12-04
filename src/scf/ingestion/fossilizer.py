import os
import json
import uuid
import time
import pandas as pd
import numpy as np
import h5py
from pathlib import Path
from typing import Dict, Any, List

class Fossilizer:
    """
    The Digestive System of the Sovereign Daemon.
    Ingests raw data and converts it into 'Fossils' (Standardized NDJSON).
    """
    def __init__(self, raw_dir: str, vault_dir: str):
        self.raw_dir = Path(raw_dir)
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        print(f"🦖 Fossilizer Online. Watching: {self.raw_dir}")

    def process_all(self):
        """
        Process all files in raw_ingest, following symlinks.
        """
        print(f"   Scanning {self.raw_dir}...")
        file_count = 0
        
        for root, dirs, files in os.walk(self.raw_dir, followlinks=True):
            for name in files:
                if name.startswith('.'): continue
                if name == "README.txt": continue
                
                file_path = Path(root) / name
                self._fossilize_file(file_path)
                file_count += 1
                
        print(f"   Processed {file_count} files.")

    def _fossilize_file(self, file_path: Path):
        print(f"   Processing {file_path.name}...")
        try:
            # Special Handlers
            if "slice100k" in str(file_path).lower():
                self._handle_slice100k(file_path)
                return
            elif "energyflow" in str(file_path).lower():
                self._handle_energyflow(file_path)
                return
            elif "active_matter" in str(file_path).lower():
                self._handle_active_matter(file_path)
                return
            elif "gray_scott" in str(file_path).lower():
                self._handle_gray_scott(file_path)
                return
            elif file_path.suffix in ['.h5', '.hdf5']:
                self._handle_generic_hdf5(file_path)
                return

            # Generic Handlers
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix == '.json':
                df = pd.read_json(file_path)
            elif file_path.suffix == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                print(f"   ⚠️ Skipping unsupported type: {file_path.suffix}")
                return

            # Extract Features
            fossils = self._extract_fossils(df, file_path.name)
            self._write_batch(fossils)
            
        except Exception as e:
            print(f"   ❌ Error processing {file_path.name}: {e}")

    def _handle_active_matter(self, file_path: Path):
        print(f"   🦠 Ingesting Active Matter: {file_path.name}")
        try:
            with h5py.File(file_path, 'r') as f:
                # Extract metadata if available, otherwise mock
                # The Well usually has 'data' or similar keys
                keys = list(f.keys())
                fossil = {
                    "id": str(uuid.uuid4()),
                    "source": "active_matter",
                    "timestamp": time.time(),
                    "data": {"filename": file_path.name, "keys": keys, "type": "active_matter_simulation"},
                    "meta": {"domain": "soft_matter_physics"}
                }
                self._write_batch([fossil])
        except Exception as e:
            print(f"   ❌ Failed to read HDF5: {e}")

    def _handle_gray_scott(self, file_path: Path):
        print(f"   🧪 Ingesting Gray-Scott: {file_path.name}")
        try:
            with h5py.File(file_path, 'r') as f:
                keys = list(f.keys())
                fossil = {
                    "id": str(uuid.uuid4()),
                    "source": "gray_scott",
                    "timestamp": time.time(),
                    "data": {"filename": file_path.name, "keys": keys, "type": "reaction_diffusion"},
                    "meta": {"domain": "chemical_kinetics"}
                }
                self._write_batch([fossil])
        except Exception as e:
            print(f"   ❌ Failed to read HDF5: {e}")

    def _handle_generic_hdf5(self, file_path: Path):
        print(f"   📦 Ingesting Generic HDF5: {file_path.name}")
        try:
            with h5py.File(file_path, 'r') as f:
                keys = list(f.keys())
                # For massive files, we only store metadata/pointers
                fossil = {
                    "id": str(uuid.uuid4()),
                    "source": "hdf5_generic",
                    "timestamp": time.time(),
                    "data": {
                        "filename": file_path.name,
                        "keys": keys,
                        "path": str(file_path),
                        "size_bytes": file_path.stat().st_size
                    },
                    "meta": {"type": "pointer_fossil", "format": "hdf5"}
                }
                self._write_batch([fossil])
        except Exception as e:
            print(f"   ❌ Failed to read HDF5: {e}")

    def _handle_slice100k(self, file_path: Path):
        # Slice100k usually contains G-code or Images
        # For this demo, we assume it's a metadata CSV or we extract from filename
        print(f"   🖨️  Ingesting Slice100k artifact: {file_path.name}")
        fossil = {
            "id": str(uuid.uuid4()),
            "source": "slice100k",
            "timestamp": time.time(),
            "data": {"filename": file_path.name, "type": "additive_layer"},
            "meta": {"domain": "manufacturing"}
        }
        self._write_batch([fossil])

    def _handle_energyflow(self, file_path: Path):
        # EnergyFlow is often HDF5 or NumPy
        print(f"   ⚛️  Ingesting EnergyFlow artifact: {file_path.name}")
        # Mock extraction for now
        fossil = {
            "id": str(uuid.uuid4()),
            "source": "energyflow",
            "timestamp": time.time(),
            "data": {"filename": file_path.name, "type": "particle_collision"},
            "meta": {"domain": "physics"}
        }
        self._write_batch([fossil])

    def _write_batch(self, fossils: List[Dict[str, Any]]):
        if not fossils: return
        batch_id = uuid.uuid4().hex[:8]
        out_path = self.vault_dir / f"fossil_batch_{batch_id}.ndjson"
        with open(out_path, 'w') as f:
            for fossil in fossils:
                f.write(json.dumps(fossil) + "\n")
        print(f"   ✅ Created {len(fossils)} fossils -> {out_path.name}")

    def _extract_fossils(self, df: pd.DataFrame, source_name: str) -> List[Dict[str, Any]]:
        """
        Converts DataFrame rows into Fossil dictionaries.
        Calculates Entropy Gradient (dS/dt) if possible.
        """
        fossils = []
        
        # Standardize Columns (Heuristic)
        # We look for 'time', 'temp', 'power', 'flow', etc.
        cols = df.columns.str.lower()
        
        for idx, row in df.iterrows():
            # Base Fossil
            fossil = {
                "id": str(uuid.uuid4()),
                "source": source_name,
                "timestamp": time.time(), # Default to now if no time col
                "data": row.to_dict(),
                "meta": {"type": "raw_observation"}
            }
            
            # Heuristic Feature Extraction
            # 1. Entropy Proxy (Variance/Complexity)
            # For single row, we can't calculate variance, but if we had a window...
            # For now, let's just tag it.
            
            fossils.append(fossil)
            
        return fossils

if __name__ == "__main__":
    # Example Usage
    import sys
    if len(sys.argv) > 2:
        fossilizer = Fossilizer(sys.argv[1], sys.argv[2])
        fossilizer.process_all()
    else:
        print("Usage: python fossilizer.py <raw_dir> <vault_dir>")
