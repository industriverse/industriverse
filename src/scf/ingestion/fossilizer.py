import os
import json
import uuid
import time
import pandas as pd
import numpy as np
import h5py
from pathlib import Path
from typing import Dict, Any, List
from src.scf.ingestion.energy_signature import EnergySignature
from src.scf.ingestion.fossil_schema import Fossil
import subprocess

def auto_caffeinate():
    """
    Prevents system sleep during long processes by spawning a background caffeinate process.
    """
    try:
        subprocess.Popen(["caffeinate", "-i", "-w", str(os.getpid())])
        print("   ☕ Caffeinate active: System sleep prevented.")
    except Exception as e:
        print(f"   ⚠️ Could not start caffeinate: {e}")

class Fossilizer:
    """
    The Digestive System of the Sovereign Daemon.
    Ingests raw data and converts it into 'Fossils' (Standardized NDJSON).
    """
    def __init__(self, raw_dir: str, vault_dir: str):
        self.raw_dir = Path(raw_dir)
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.energy_sig = EnergySignature()
        auto_caffeinate()
        print(f"🦖 Fossilizer Online. Watching: {self.raw_dir}")

    def process_all(self):
        """
        Process all files in raw_ingest, following symlinks.
        """
        print(f"   Scanning {self.raw_dir}...")
        file_count = 0
        
        for root, dirs, files in os.walk(self.raw_dir, followlinks=True):
            # Skip already processed datasets
            if "MHD_256" in root or "active_matter" in root:
                continue
                
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
            elif "mhd" in str(file_path).lower():
                self._handle_mhd(file_path)
                return
            elif "the_well" in str(file_path).lower() or "datasets/raw/datasets" in str(file_path):
                # Catch-all for The Well datasets (checking path structure)
                self._handle_the_well_universal(file_path)
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
                # Extract Physics Signature
                # Active Matter: Use concentration field as entropy proxy
                signature = {}
                if 't0_fields' in f and 'concentration' in f['t0_fields']:
                    # Shape: (3, 81, 256, 256) -> Take first sample, first timestep
                    data_slice = f['t0_fields']['concentration'][0, 0] 
                    if isinstance(data_slice, np.ndarray):
                        signature = self.energy_sig.extract(data_slice.flatten())
                
                fossil = {
                    "id": str(uuid.uuid4()),
                    "source": "active_matter",
                    "timestamp": time.time(),
                    "data": {"filename": file_path.name, "keys": keys, "type": "active_matter_simulation"},
                    "meta": {
                        "domain": "soft_matter_physics",
                        "thermodynamics": signature
                    }
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

    def _handle_mhd(self, file_path: Path):
        print(f"   🧲 Ingesting MHD (Magnetohydrodynamics): {file_path.name}")
        try:
            with h5py.File(file_path, 'r') as f:
                keys = list(f.keys())
                # Extract simulation parameters if available
                meta = {"domain": "plasma_physics", "type": "mhd_simulation"}
                if 'attrs' in f.attrs:
                    # Convert attrs to dict, handling numpy types
                    for k, v in f.attrs.items():
                        if isinstance(v, (np.integer, int)):
                            meta[k] = int(v)
                        elif isinstance(v, (np.floating, float)):
                            meta[k] = float(v)
                        elif isinstance(v, (np.ndarray, list)):
                            meta[k] = str(v)
                        else:
                            meta[k] = str(v)
                
                # Extract Physics Signature from MHD fields (e.g. density, pressure)
                # Assuming keys like 'density', 'pressure', or similar exist, or we take a slice
                signature = {}
                # Heuristic: try to find a dataset that looks like a field
                for k in keys:
                    if k in ['density', 'pressure', 'velocity', 'B_field']:
                        if isinstance(f[k], h5py.Dataset):
                            # Take a small slice to avoid reading 100GB
                            data_slice = f[k][0] # First time step/slice
                            signature = self.energy_sig.extract(data_slice.flatten())
                            break
                
                fossil = {
                    "id": str(uuid.uuid4()),
                    "source": "mhd",
                    "timestamp": time.time(),
                    "data": {
                        "filename": file_path.name, 
                        "keys": keys, 
                        "size_bytes": file_path.stat().st_size
                    },
                    "meta": {
                        **meta,
                        "thermodynamics": signature
                    }
                }
                self._write_batch([fossil])
        except Exception as e:
            print(f"   ❌ Failed to read MHD HDF5: {e}")

    def _handle_the_well_universal(self, file_path: Path):
        # Determine dataset name from parent folder
        dataset_name = file_path.parent.parent.name # e.g. 'planetswe' or 'data' -> 'planetswe'
        if dataset_name == 'train' or dataset_name == 'valid':
             dataset_name = file_path.parent.parent.parent.name
             
        print(f"   🌌 Ingesting The Well ({dataset_name}): {file_path.name}")
        try:
            with h5py.File(file_path, 'r') as f:
                keys = list(f.keys())
                meta = {"domain": "physics_general", "dataset": dataset_name, "type": "the_well_simulation"}
                
                # Universal Energy Signature Extraction
                signature = {}
                # Priority list of fields to check
                priority_fields = ['density', 'pressure', 'temperature', 'concentration', 'height', 'velocity', 'B_field']
                
                found_sig = False
                for group in ['t0_fields', 't1_fields', 't2_fields', 'scalars']:
                    if group in f:
                        for field in priority_fields:
                            if field in f[group]:
                                # Extract from this field
                                data_node = f[group][field]
                                # Handle shape: usually (batch, time, x, y, ...)
                                # We take [0, 0] or flatten the first sample
                                if isinstance(data_node, h5py.Dataset):
                                    # Safe slice
                                    try:
                                        # Try to get a 1D slice of reasonable size
                                        if data_node.ndim >= 2:
                                            data_slice = data_node[0, 0] # First batch, first time
                                        elif data_node.ndim == 1:
                                            data_slice = data_node[:]
                                        else:
                                            data_slice = data_node[()]
                                            
                                        if isinstance(data_slice, np.ndarray):
                                            signature = self.energy_sig.extract(data_slice.flatten())
                                            found_sig = True
                                            break
                                    except Exception as slice_err:
                                        print(f"     ⚠️ Slice error on {field}: {slice_err}")
                        if found_sig: break
                
                fossil = {
                    "id": str(uuid.uuid4()),
                    "source": f"the_well_{dataset_name}",
                    "timestamp": time.time(),
                    "data": {
                        "filename": file_path.name,
                        "keys": keys,
                        "path": str(file_path),
                        "size_bytes": file_path.stat().st_size
                    },
                    "meta": {
                        **meta,
                        "thermodynamics": signature
                    }
                }
                self._write_batch([fossil])
        except Exception as e:
            print(f"   ❌ Failed to read The Well HDF5: {e}")

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
        
        # Convert dicts to Fossil objects and sign them
        validated_fossils = []
        for f_dict in fossils:
            try:
                fossil = Fossil(**f_dict)
                fossil.sign()
                validated_fossils.append(fossil)
            except Exception as e:
                print(f"   ⚠️ Invalid Fossil: {e}")
                continue
                
        if not validated_fossils: return

        batch_id = uuid.uuid4().hex[:8]
        out_path = self.vault_dir / f"fossil_batch_{batch_id}.ndjson"
        with open(out_path, 'w') as f:
            for fossil in validated_fossils:
                f.write(fossil.model_dump_json() + "\n")
        print(f"   ✅ Created {len(validated_fossils)} fossils -> {out_path.name}")

    def compute_entropy_gradients(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Computes thermodynamic gradients for the entire dataframe/window.
        """
        # Select numeric columns for signature extraction
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return {}
            
        # We can aggregate the signal (e.g., mean of all sensors) or pick a primary one
        # For now, let's flatten the numeric data to get a global entropy rate
        # or just pick the first column as the 'primary signal'
        signal = numeric_df.iloc[:, 0].values
        
        return self.energy_sig.extract(signal)

    def _extract_fossils(self, df: pd.DataFrame, source_name: str) -> List[Dict[str, Any]]:
        """
        Converts DataFrame rows into Fossil dictionaries.
        Calculates Entropy Gradient (dS/dt) for the file context.
        """
        fossils = []
        
        # 1. Compute Global/Window Physics Signature
        signature = self.compute_entropy_gradients(df)
        
        # Standardize Columns (Heuristic)
        cols = df.columns.str.lower()
        
        for idx, row in df.iterrows():
            # Base Fossil
            fossil = {
                "id": str(uuid.uuid4()),
                "source": source_name,
                "timestamp": time.time(), # Default to now if no time col
                "data": row.to_dict(),
                "meta": {
                    "type": "raw_observation",
                    "thermodynamics": signature  # Inject Physics Context
                }
            }
            
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
