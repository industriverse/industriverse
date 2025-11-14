"""
Energy Map Dataset Loaders

Dataset classes for loading and preprocessing energy distributions
from various domains (molecular, plasma, thermal, enterprise).
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Optional, List, Dict, Tuple, Callable
from pathlib import Path
import json
from dataclasses import dataclass


@dataclass
class EnergyMapConfig:
    """Configuration for energy map datasets"""

    domain: str  # molecular, plasma, thermal, enterprise
    resolution: Tuple[int, int] = (64, 64)
    normalize: bool = True
    augment: bool = False
    energy_range: Tuple[float, float] = (0.0, 1.0)
    temperature: float = 1.0


class EnergyMapDataset(Dataset):
    """
    Base dataset class for energy distributions.

    Loads energy maps from various sources and applies preprocessing
    for diffusion model training.
    """

    def __init__(
        self,
        data_path: str,
        config: EnergyMapConfig,
        transform: Optional[Callable] = None,
        cache_in_memory: bool = False
    ):
        """
        Initialize energy map dataset.

        Args:
            data_path: Path to dataset directory or file
            config: Dataset configuration
            transform: Optional transform to apply
            cache_in_memory: Cache all data in RAM
        """
        self.data_path = Path(data_path)
        self.config = config
        self.transform = transform
        self.cache_in_memory = cache_in_memory

        # Load dataset metadata
        self.samples = self._load_samples()

        # Cache if requested
        self.cache: Dict[int, torch.Tensor] = {}
        if cache_in_memory:
            self._cache_all()

    def _load_samples(self) -> List[Dict]:
        """Load dataset samples metadata"""
        samples = []

        if self.data_path.is_dir():
            # Load from directory of .npy files
            for energy_file in sorted(self.data_path.glob("*.npy")):
                samples.append({
                    'path': str(energy_file),
                    'domain': self.config.domain,
                    'format': 'numpy'
                })

        elif self.data_path.suffix == '.json':
            # Load from JSON manifest
            with open(self.data_path, 'r') as f:
                manifest = json.load(f)
                samples = manifest.get('samples', [])

        elif self.data_path.suffix == '.npy':
            # Single numpy file
            samples = [{
                'path': str(self.data_path),
                'domain': self.config.domain,
                'format': 'numpy'
            }]

        return samples

    def _cache_all(self):
        """Pre-cache all samples in memory"""
        for idx in range(len(self.samples)):
            self.cache[idx] = self._load_energy_map(idx)

    def _load_energy_map(self, idx: int) -> torch.Tensor:
        """Load a single energy map"""
        sample = self.samples[idx]

        if sample['format'] == 'numpy':
            energy_map = np.load(sample['path'])
            energy_map = torch.from_numpy(energy_map).float()

        else:
            raise ValueError(f"Unknown format: {sample['format']}")

        # Resize if needed
        if energy_map.shape != self.config.resolution:
            energy_map = torch.nn.functional.interpolate(
                energy_map.unsqueeze(0).unsqueeze(0),
                size=self.config.resolution,
                mode='bilinear',
                align_corners=False
            ).squeeze()

        # Normalize to energy range
        if self.config.normalize:
            e_min, e_max = self.config.energy_range
            energy_map = (energy_map - energy_map.min()) / (energy_map.max() - energy_map.min() + 1e-8)
            energy_map = energy_map * (e_max - e_min) + e_min

        return energy_map

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Get a single training sample"""
        # Load from cache or disk
        if idx in self.cache:
            energy_map = self.cache[idx]
        else:
            energy_map = self._load_energy_map(idx)

        # Apply augmentation
        if self.config.augment and np.random.rand() > 0.5:
            energy_map = self._augment(energy_map)

        # Apply custom transform
        if self.transform is not None:
            energy_map = self.transform(energy_map)

        # Add channel dimension if needed
        if energy_map.dim() == 2:
            energy_map = energy_map.unsqueeze(0)

        return {
            'energy_map': energy_map,
            'domain': self.config.domain,
            'metadata': self.samples[idx]
        }

    def _augment(self, energy_map: torch.Tensor) -> torch.Tensor:
        """Apply random augmentation"""
        # Random rotation (90, 180, 270 degrees)
        k = np.random.choice([1, 2, 3])
        energy_map = torch.rot90(energy_map, k=k, dims=(0, 1))

        # Random flip
        if np.random.rand() > 0.5:
            energy_map = torch.flip(energy_map, dims=[0])
        if np.random.rand() > 0.5:
            energy_map = torch.flip(energy_map, dims=[1])

        return energy_map


class SyntheticEnergyDataset(Dataset):
    """
    Synthetic energy map generator for testing and pretraining.

    Generates energy maps with known thermodynamic properties.
    """

    def __init__(
        self,
        num_samples: int,
        resolution: Tuple[int, int] = (64, 64),
        domain: str = "synthetic",
        energy_type: str = "gaussian_mixture"
    ):
        """
        Initialize synthetic dataset.

        Args:
            num_samples: Number of samples to generate
            resolution: Map resolution
            domain: Domain identifier
            energy_type: Type of energy distribution
                - 'gaussian_mixture': Multiple Gaussian peaks
                - 'harmonic': Harmonic potential
                - 'gradient': Linear energy gradients
                - 'turbulent': Turbulent energy fields
        """
        self.num_samples = num_samples
        self.resolution = resolution
        self.domain = domain
        self.energy_type = energy_type

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Generate a synthetic energy map"""
        np.random.seed(idx)  # Reproducible generation

        if self.energy_type == "gaussian_mixture":
            energy_map = self._generate_gaussian_mixture()

        elif self.energy_type == "harmonic":
            energy_map = self._generate_harmonic()

        elif self.energy_type == "gradient":
            energy_map = self._generate_gradient()

        elif self.energy_type == "turbulent":
            energy_map = self._generate_turbulent()

        else:
            raise ValueError(f"Unknown energy type: {self.energy_type}")

        energy_map = torch.from_numpy(energy_map).float().unsqueeze(0)

        return {
            'energy_map': energy_map,
            'domain': self.domain,
            'metadata': {'type': self.energy_type, 'index': idx}
        }

    def _generate_gaussian_mixture(self) -> np.ndarray:
        """Generate Gaussian mixture energy distribution"""
        H, W = self.resolution
        energy_map = np.zeros((H, W), dtype=np.float32)

        # Random number of peaks
        num_peaks = np.random.randint(2, 6)

        for _ in range(num_peaks):
            # Random peak location
            cx = np.random.uniform(0.2, 0.8) * W
            cy = np.random.uniform(0.2, 0.8) * H

            # Random peak width
            sigma = np.random.uniform(0.05, 0.2) * min(H, W)

            # Random peak amplitude
            amplitude = np.random.uniform(0.5, 2.0)

            # Generate Gaussian
            y, x = np.ogrid[:H, :W]
            gaussian = amplitude * np.exp(-((x - cx)**2 + (y - cy)**2) / (2 * sigma**2))
            energy_map += gaussian

        return energy_map

    def _generate_harmonic(self) -> np.ndarray:
        """Generate harmonic oscillator potential"""
        H, W = self.resolution

        # Create coordinate grids
        y, x = np.ogrid[:H, :W]
        cx, cy = W / 2, H / 2

        # Quadratic potential: E = k * r^2
        k = np.random.uniform(0.01, 0.1)
        r_squared = (x - cx)**2 + (y - cy)**2
        energy_map = k * r_squared

        return energy_map.astype(np.float32)

    def _generate_gradient(self) -> np.ndarray:
        """Generate linear energy gradient"""
        H, W = self.resolution

        # Random gradient direction
        theta = np.random.uniform(0, 2 * np.pi)

        y, x = np.ogrid[:H, :W]
        energy_map = (x * np.cos(theta) + y * np.sin(theta)).astype(np.float32)

        # Normalize
        energy_map = (energy_map - energy_map.min()) / (energy_map.max() - energy_map.min())

        return energy_map

    def _generate_turbulent(self) -> np.ndarray:
        """Generate turbulent energy field using Perlin-like noise"""
        H, W = self.resolution

        # Multi-scale noise
        energy_map = np.zeros((H, W), dtype=np.float32)

        for octave in range(4):
            scale = 2 ** octave
            noise = np.random.randn(H // scale, W // scale)

            # Upsample
            noise_upsampled = np.kron(noise, np.ones((scale, scale)))

            # Crop/pad to match resolution
            if noise_upsampled.shape[0] > H:
                noise_upsampled = noise_upsampled[:H, :W]
            elif noise_upsampled.shape[0] < H:
                padded = np.zeros((H, W))
                padded[:noise_upsampled.shape[0], :noise_upsampled.shape[1]] = noise_upsampled
                noise_upsampled = padded

            # Add with decreasing amplitude
            energy_map += noise_upsampled / (2 ** octave)

        return energy_map


def create_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    pin_memory: bool = True
) -> DataLoader:
    """
    Create PyTorch DataLoader for energy maps.

    Args:
        dataset: Energy map dataset
        batch_size: Batch size
        shuffle: Shuffle data
        num_workers: Number of worker processes
        pin_memory: Pin memory for GPU transfer

    Returns:
        DataLoader instance
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=True  # Drop incomplete batches for training stability
    )


# ============================================================================
# Domain-Specific Dataset Classes
# ============================================================================

class MolecularEnergyDataset(EnergyMapDataset):
    """Dataset for molecular energy landscapes"""

    def __init__(self, data_path: str, **kwargs):
        config = EnergyMapConfig(
            domain="molecular",
            resolution=(64, 64),
            normalize=True,
            augment=True,
            temperature=300.0  # Room temperature in Kelvin
        )
        super().__init__(data_path, config, **kwargs)


class PlasmaEnergyDataset(EnergyMapDataset):
    """Dataset for plasma stability maps"""

    def __init__(self, data_path: str, **kwargs):
        config = EnergyMapConfig(
            domain="plasma",
            resolution=(128, 128),
            normalize=True,
            augment=False,  # Don't augment plasma - breaks physics
            temperature=10000.0  # Plasma temperature
        )
        super().__init__(data_path, config, **kwargs)


class EnterpriseEnergyDataset(EnergyMapDataset):
    """Dataset for enterprise compute energy maps"""

    def __init__(self, data_path: str, **kwargs):
        config = EnergyMapConfig(
            domain="enterprise",
            resolution=(32, 32),
            normalize=True,
            augment=True,
            temperature=1.0  # Abstract energy units
        )
        super().__init__(data_path, config, **kwargs)
