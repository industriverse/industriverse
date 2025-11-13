"""
Physics Dataset Loader for Real Scientific Data

Loads existing HDF5 physics simulations and converts to
energy maps for EIL testing and validation.

Supported datasets:
- Turbulent Radiative Layer 2D
- OpenKIM atomistic simulations
- The Well physical systems
"""

import h5py
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class PhysicsDataSample:
    """Sample from physics simulation dataset"""
    energy_map: np.ndarray  # [height, width]
    regime: str  # Physics regime classification
    parameters: Dict[str, float]  # Simulation parameters
    ground_truth: Dict[str, Any]  # True physics values
    metadata: Dict[str, Any]


class TurbulentLayerLoader:
    """Loader for Turbulent Radiative Layer 2D dataset

    Converts fluid dynamics simulations to energy maps
    for EIL regime detection testing.

    HDF5 Structure:
    - t0_fields/density: [ensemble, time, x, y]
    - t0_fields/pressure: [ensemble, time, x, y]
    - t1_fields/velocity: [ensemble, time, x, y, 2]
    - dimensions/time, x, y
    - scalars/tcool: cooling timescale
    """

    def __init__(self, data_root: str = "/Volumes/Expansion/datasets/raw/datasets/turbulent_radiative_layer_2D"):
        self.data_root = Path(data_root)
        self.train_path = self.data_root / "data" / "train"
        self.valid_path = self.data_root / "data" / "valid"
        self.test_path = self.data_root / "data" / "test"

    def load_sample(self, file_path: Path) -> PhysicsDataSample:
        """Load single HDF5 file and convert to EIL format"""

        with h5py.File(file_path, 'r') as f:
            # Extract cooling timescale from filename
            # e.g., "turbulent_radiative_layer_tcool_0.32.hdf5"
            filename = file_path.name
            tcool_str = filename.split('tcool_')[1].split('.hdf5')[0]
            tcool = float(tcool_str)

            # Classify regime based on cooling timescale
            if tcool < 0.1:
                regime = "fast_cooling_chaotic"
            elif tcool < 1.0:
                regime = "moderate_cooling_transitional"
            else:
                regime = "slow_cooling_stable"

            # Load density field: [ensemble, time, x, y]
            # Use first ensemble member, last timestep
            density = f['t0_fields/density'][0, -1, :, :]  # [128, 384]

            # Load pressure field
            pressure = f['t0_fields/pressure'][0, -1, :, :]  # [128, 384]

            # Compute "energy" as combination of density and pressure
            # This is a proxy for thermodynamic energy
            # E ~ P (ideal gas approximation)
            energy_field = pressure

            # Normalize to [0, 1] for EIL
            energy_map = (energy_field - energy_field.min()) / (energy_field.max() - energy_field.min() + 1e-8)

            # Create sample
            sample = PhysicsDataSample(
                energy_map=energy_map,
                regime=regime,
                parameters={'tcool': tcool},
                ground_truth={
                    'physics_type': 'turbulent_radiative_layer',
                    'dimensionality': '2D',
                    'cooling_time': tcool,
                    'spatial_shape': density.shape,
                    'density_range': (float(density.min()), float(density.max())),
                    'pressure_range': (float(pressure.min()), float(pressure.max()))
                },
                metadata={
                    'source_file': str(file_path),
                    'ensemble_member': 0,
                    'timestep': -1  # Last timestep
                }
            )

            return sample

    def iter_split(self, split: str = 'train', max_samples: int = None) -> List[PhysicsDataSample]:
        """Iterate over train/valid/test split"""

        if split == 'train':
            path = self.train_path
        elif split == 'valid':
            path = self.valid_path
        elif split == 'test':
            path = self.test_path
        else:
            raise ValueError(f"Unknown split: {split}")

        hdf5_files = sorted(path.glob("*.hdf5"))

        if max_samples:
            hdf5_files = hdf5_files[:max_samples]

        samples = []
        for file_path in hdf5_files:
            try:
                sample = self.load_sample(file_path)
                samples.append(sample)
            except Exception as e:
                print(f"⚠️  Failed to load {file_path.name}: {e}")
                import traceback
                traceback.print_exc()

        return samples


if __name__ == "__main__":
    print("=" * 70)
    print("Physics Dataset Loader Test")
    print("=" * 70)

    # Initialize loader
    loader = TurbulentLayerLoader()

    # Load training samples
    print("\n📊 Loading training samples...")
    train_samples = loader.iter_split('train', max_samples=5)

    print(f"\n✅ Loaded {len(train_samples)} samples\n")

    for i, sample in enumerate(train_samples):
        print(f"Sample {i+1}:")
        print(f"   Energy map shape: {sample.energy_map.shape}")
        print(f"   Regime: {sample.regime}")
        print(f"   Parameters: {sample.parameters}")
        print(f"   Range: [{sample.energy_map.min():.4f}, {sample.energy_map.max():.4f}]")
        print(f"   Ground truth: {sample.ground_truth}")
        print()

    print("=" * 70)
    print("✅ PHYSICS DATASET LOADER TEST COMPLETE")
    print("=" * 70)
