#!/usr/bin/env python3
"""
atlas_loader.py
Energy Atlas Data Layer - Phase 4 Core Component

Loads, validates, and vectorizes energy maps from the Energy Atlas.
Implements multi-scale pyramid precomputation and gradient calculation.

Thermodynamic Principle:
    Energy conservation must hold across all scales:
    ∑E(scale=256) = ∑E(scale=128) = ∑E(scale=64)
"""

import numpy as np
import h5py
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
from scipy.ndimage import zoom, gaussian_filter
from py2neo import Graph, Node, Relationship

# Thermodynamic Constants
ENERGY_CONSERVATION_TOLERANCE = 0.05  # 5% tolerance for energy conservation
VALID_SCALES = [64, 128, 256]
VALID_ASPECT_RATIOS = [(1, 1), (2, 3), (3, 2)]  # Square or 2:3 ratio


@dataclass
class EnergyMapMetadata:
    """Metadata for an energy map snapshot."""
    map_id: str
    domain: str
    scale: int
    timestamp: datetime
    energy_mean: float
    energy_var: float
    entropy: float
    regime: Optional[str] = None
    confidence: Optional[float] = None
    gradient_magnitude_mean: float = 0.0
    gradient_magnitude_max: float = 0.0


class ThermodynamicViolation(Exception):
    """Raised when physical constraints are violated."""
    pass


class EnergyAtlasLoader:
    """
    Energy Atlas data loader with thermodynamic validation.

    Loads energy maps from disk, validates physical constraints,
    and precomputes multi-scale pyramids with gradients.

    Args:
        data_dir: Root directory for energy map storage
        neo4j_uri: Neo4j connection URI (default: bolt://localhost:7687)
        neo4j_auth: Tuple of (username, password) or None for no auth
    """

    def __init__(
        self,
        data_dir: Union[str, Path],
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_auth: Optional[Tuple[str, str]] = None
    ):
        self.data_dir = Path(data_dir)
        self.neo4j_uri = neo4j_uri

        # Initialize Neo4j connection (lazy - only connect when needed)
        self._graph = None
        self._neo4j_auth = neo4j_auth

        # Create directory structure if it doesn't exist
        self.maps_dir = self.data_dir / "energy_maps"
        self.pyramids_dir = self.data_dir / "energy_maps" / "pyramids"
        self.maps_dir.mkdir(parents=True, exist_ok=True)
        self.pyramids_dir.mkdir(parents=True, exist_ok=True)

        # Cache for loaded maps
        self._map_cache: Dict[str, np.ndarray] = {}
        self._metadata_cache: Dict[str, EnergyMapMetadata] = {}

    @property
    def graph(self) -> Graph:
        """Lazy Neo4j connection."""
        if self._graph is None:
            try:
                self._graph = Graph(self.neo4j_uri, auth=self._neo4j_auth)
            except Exception as e:
                print(f"Warning: Could not connect to Neo4j: {e}")
                print("Operating in offline mode (no metadata persistence)")
                self._graph = None
        return self._graph

    def validate_shape(self, energy_map: np.ndarray) -> bool:
        """
        Validate energy map shape.

        Must be:
        - 2D array
        - Square (H=W) or 2:3/3:2 aspect ratio
        - Dimensions in VALID_SCALES or multiples thereof

        Args:
            energy_map: 2D numpy array

        Returns:
            True if valid

        Raises:
            ValueError if invalid
        """
        if energy_map.ndim != 2:
            raise ValueError(f"Energy map must be 2D, got {energy_map.ndim}D")

        h, w = energy_map.shape

        # Check if dimensions are valid scales or multiples
        valid_dims = VALID_SCALES + [s * 2 for s in VALID_SCALES]

        if h not in valid_dims and w not in valid_dims:
            raise ValueError(
                f"Invalid dimensions {energy_map.shape}. "
                f"Must use scales {VALID_SCALES} or multiples"
            )

        # Check aspect ratio
        aspect_ratio = (min(h, w), max(h, w))
        normalized_aspect = (aspect_ratio[0] // np.gcd(h, w),
                            aspect_ratio[1] // np.gcd(h, w))

        if normalized_aspect not in VALID_ASPECT_RATIOS:
            raise ValueError(
                f"Invalid aspect ratio {h}:{w}. "
                f"Must be square or 2:3 ratio"
            )

        return True

    def compute_entropy(self, energy_map: np.ndarray) -> float:
        """
        Compute Shannon entropy of energy distribution.

        H = -∑ p(E) log p(E)

        Args:
            energy_map: 2D energy array

        Returns:
            Entropy in nats
        """
        # Normalize to probability distribution
        E_normalized = energy_map / (np.sum(energy_map) + 1e-10)

        # Compute entropy
        entropy = -np.sum(E_normalized * np.log(E_normalized + 1e-10))

        return float(entropy)

    def compute_gradients(self, energy_map: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute energy gradients ∇E = (∂E/∂x, ∂E/∂y).

        Args:
            energy_map: 2D energy array (H, W)

        Returns:
            grad_x: Gradient in x direction (H, W)
            grad_y: Gradient in y direction (H, W)
        """
        grad_x = np.gradient(energy_map, axis=1)
        grad_y = np.gradient(energy_map, axis=0)

        return grad_x, grad_y

    def precompute_pyramids(
        self,
        energy_map: np.ndarray,
        target_scales: Optional[List[int]] = None
    ) -> Dict[int, Dict[str, np.ndarray]]:
        """
        Generate multi-scale pyramid and precompute gradients.

        Secret Sauce #1: Atlas Pyramids + ∇E Precompute

        Args:
            energy_map: Original energy map (any resolution)
            target_scales: List of target scales (default: [64, 128, 256])

        Returns:
            Dictionary mapping scale → {
                'energy': downsampled energy map,
                'grad_x': x-gradient,
                'grad_y': y-gradient,
                'grad_magnitude': |∇E|
            }
        """
        if target_scales is None:
            target_scales = VALID_SCALES

        # Original energy for conservation check
        E_original = np.sum(energy_map)

        pyramids = {}

        for scale in target_scales:
            # Compute zoom factor
            # Assume square maps for simplicity; extend for aspect ratios
            current_size = max(energy_map.shape)
            factor = scale / current_size

            # Downsample using bicubic interpolation (order=3)
            if factor != 1.0:
                energy_scaled = zoom(energy_map, factor, order=3)
            else:
                energy_scaled = energy_map.copy()

            # Renormalize to preserve total energy
            E_scaled = np.sum(energy_scaled)
            if E_scaled > 1e-10:
                energy_scaled *= E_original / E_scaled

            # Compute gradients
            grad_x, grad_y = self.compute_gradients(energy_scaled)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)

            # Store in pyramid
            pyramids[scale] = {
                'energy': energy_scaled,
                'grad_x': grad_x,
                'grad_y': grad_y,
                'grad_magnitude': grad_magnitude
            }

            # Verify energy conservation
            E_after = np.sum(energy_scaled)
            conservation_error = abs(E_after - E_original) / (E_original + 1e-10)

            if conservation_error > ENERGY_CONSERVATION_TOLERANCE:
                raise ThermodynamicViolation(
                    f"Energy conservation violated at scale {scale}: "
                    f"ΔE/E = {conservation_error:.3f} > {ENERGY_CONSERVATION_TOLERANCE}"
                )

        return pyramids

    def _load_energy_file(self, file_path: Path) -> np.ndarray:
        """
        Load energy map from .npy or .npz file.

        Args:
            file_path: Path to .npy or .npz file

        Returns:
            Energy map as numpy array
        """
        if file_path.suffix == '.npy':
            return np.load(file_path)
        elif file_path.suffix == '.npz':
            data = np.load(file_path)
            # Try common keys
            for key in ['energy', 'data']:
                if key in data:
                    return data[key]
            # Fall back to first key
            keys = list(data.keys())
            if keys:
                return data[keys[0]]
            raise ValueError(f"No data found in {file_path}")
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def load_map(
        self,
        domain: str,
        map_id: Optional[str] = None,
        scale: int = 256
    ) -> Tuple[np.ndarray, EnergyMapMetadata]:
        """
        Load a single energy map from disk.

        Supports both .npy and .npz formats.

        Args:
            domain: Physics domain name
            map_id: Specific map ID (if None, loads latest)
            scale: Target resolution

        Returns:
            energy_map: 2D numpy array
            metadata: EnergyMapMetadata object
        """
        # Construct file path
        domain_dir = self.maps_dir / domain

        if not domain_dir.exists():
            raise FileNotFoundError(f"Domain directory not found: {domain_dir}")

        # Find map file
        if map_id is None:
            # Load most recent (try both .npy and .npz)
            map_files = sorted(list(domain_dir.glob("*.npy")) + list(domain_dir.glob("*.npz")))
            if not map_files:
                raise FileNotFoundError(f"No energy maps found in {domain_dir}")
            map_path = map_files[-1]
            map_id = map_path.stem
        else:
            # Try .npy first, then .npz
            map_path = domain_dir / f"{map_id}.npy"
            if not map_path.exists():
                map_path = domain_dir / f"{map_id}.npz"
            if not map_path.exists():
                raise FileNotFoundError(f"Map not found: {map_id}")

        # Load from disk
        energy_map = self._load_energy_file(map_path)

        # Validate
        self.validate_shape(energy_map)

        # Compute metadata
        grad_x, grad_y = self.compute_gradients(energy_map)
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        metadata = EnergyMapMetadata(
            map_id=map_id,
            domain=domain,
            scale=max(energy_map.shape),
            timestamp=datetime.now(),
            energy_mean=float(np.mean(energy_map)),
            energy_var=float(np.var(energy_map)),
            entropy=self.compute_entropy(energy_map),
            gradient_magnitude_mean=float(np.mean(grad_magnitude)),
            gradient_magnitude_max=float(np.max(grad_magnitude))
        )

        # Store in Neo4j if connected
        if self.graph is not None:
            self._store_metadata_neo4j(metadata)

        return energy_map, metadata

    def load_batch(
        self,
        domain: str,
        window: int = 10,
        scale: int = 256,
        stride: int = 1
    ) -> Tuple[np.ndarray, List[EnergyMapMetadata]]:
        """
        Load temporal batch of energy maps.

        Args:
            domain: Physics domain name
            window: Number of time steps to load
            scale: Target resolution
            stride: Temporal stride (1 = consecutive)

        Returns:
            batch: (T, H, W) array of energy maps
            metadata_list: List of metadata for each time step
        """
        domain_dir = self.maps_dir / domain

        if not domain_dir.exists():
            raise FileNotFoundError(f"Domain directory not found: {domain_dir}")

        # Get sorted list of map files (both .npy and .npz)
        map_files = sorted(list(domain_dir.glob("*.npy")) + list(domain_dir.glob("*.npz")))

        if len(map_files) < window * stride:
            raise ValueError(
                f"Not enough maps for window={window}, stride={stride}. "
                f"Found {len(map_files)} maps"
            )

        # Load maps
        batch = []
        metadata_list = []

        for i in range(0, window * stride, stride):
            energy_map = self._load_energy_file(map_files[i])

            # Resize to target scale if needed
            if max(energy_map.shape) != scale:
                pyramids = self.precompute_pyramids(energy_map, [scale])
                energy_map = pyramids[scale]['energy']

            batch.append(energy_map)

            # Create metadata
            map_id = map_files[i].stem
            grad_x, grad_y = self.compute_gradients(energy_map)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)

            metadata = EnergyMapMetadata(
                map_id=map_id,
                domain=domain,
                scale=scale,
                timestamp=datetime.now(),
                energy_mean=float(np.mean(energy_map)),
                energy_var=float(np.var(energy_map)),
                entropy=self.compute_entropy(energy_map),
                gradient_magnitude_mean=float(np.mean(grad_magnitude)),
                gradient_magnitude_max=float(np.max(grad_magnitude))
            )
            metadata_list.append(metadata)

        # Stack into (T, H, W) array
        batch_array = np.stack(batch, axis=0)

        return batch_array, metadata_list

    def save_map(
        self,
        energy_map: np.ndarray,
        domain: str,
        map_id: Optional[str] = None,
        metadata: Optional[EnergyMapMetadata] = None
    ) -> str:
        """
        Save energy map to disk.

        Args:
            energy_map: 2D numpy array
            domain: Physics domain name
            map_id: Optional map ID (generated if None)
            metadata: Optional metadata to store

        Returns:
            map_id: Saved map identifier
        """
        # Validate
        self.validate_shape(energy_map)

        # Generate map_id if not provided
        if map_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            map_id = f"{domain}_{timestamp}"

        # Create domain directory
        domain_dir = self.maps_dir / domain
        domain_dir.mkdir(parents=True, exist_ok=True)

        # Save to disk
        map_path = domain_dir / f"{map_id}.npy"
        np.save(map_path, energy_map)

        # Auto-generate metadata if not provided
        if metadata is None:
            grad_x, grad_y = self.compute_gradients(energy_map)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)

            metadata = EnergyMapMetadata(
                map_id=map_id,
                domain=domain,
                scale=max(energy_map.shape),
                timestamp=datetime.now(),
                energy_mean=float(np.mean(energy_map)),
                energy_var=float(np.var(energy_map)),
                entropy=self.compute_entropy(energy_map),
                gradient_magnitude_mean=float(np.mean(grad_magnitude)),
                gradient_magnitude_max=float(np.max(grad_magnitude))
            )

        # Save metadata
        if metadata is not None:
            metadata_path = domain_dir / f"{map_id}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump({
                    'map_id': metadata.map_id,
                    'domain': metadata.domain,
                    'scale': metadata.scale,
                    'timestamp': metadata.timestamp.isoformat(),
                    'energy_mean': metadata.energy_mean,
                    'energy_var': metadata.energy_var,
                    'entropy': metadata.entropy,
                    'gradient_magnitude_mean': metadata.gradient_magnitude_mean,
                    'gradient_magnitude_max': metadata.gradient_magnitude_max
                }, f, indent=2)

            # Store in Neo4j if connected
            if self.graph is not None:
                self._store_metadata_neo4j(metadata)

        return map_id

    def update_map(self, domain: str, updated_map: np.ndarray, map_id: str) -> None:
        """
        Update existing energy map (used by Thermal Tap).

        Args:
            domain: Physics domain name
            updated_map: New energy map
            map_id: Map identifier to update
        """
        # Validate
        self.validate_shape(updated_map)

        # Save with existing map_id
        self.save_map(updated_map, domain, map_id)

    def _store_metadata_neo4j(self, metadata: EnergyMapMetadata) -> None:
        """Store metadata in Neo4j."""
        if self.graph is None:
            return

        try:
            # Create or update EnergySnapshot node
            snapshot_node = Node(
                "EnergySnapshot",
                snapshot_id=metadata.map_id,
                map_id=metadata.map_id,
                domain=metadata.domain,
                timestamp=metadata.timestamp.isoformat(),
                energy_mean=metadata.energy_mean,
                energy_var=metadata.energy_var,
                entropy=metadata.entropy,
                scale=metadata.scale,
                gradient_magnitude_mean=metadata.gradient_magnitude_mean,
                gradient_magnitude_max=metadata.gradient_magnitude_max
            )

            self.graph.merge(snapshot_node, "EnergySnapshot", "snapshot_id")

            # Link to domain if exists
            domain_node = self.graph.nodes.match("EnergyDomain", name=metadata.domain).first()
            if domain_node:
                rel = Relationship(domain_node, "HAS_SNAPSHOT", snapshot_node)
                self.graph.merge(rel)

        except Exception as e:
            print(f"Warning: Failed to store metadata in Neo4j: {e}")

    def get_domain_stats(self, domain: str) -> Dict[str, float]:
        """
        Get statistics for a domain.

        Args:
            domain: Physics domain name

        Returns:
            Dictionary with stats (mean energy, entropy, etc.)
        """
        domain_dir = self.maps_dir / domain

        if not domain_dir.exists():
            raise FileNotFoundError(f"Domain directory not found: {domain_dir}")

        map_files = list(domain_dir.glob("*.npy"))

        if not map_files:
            return {}

        # Compute aggregate stats
        energies = []
        entropies = []

        for map_file in map_files:
            energy_map = np.load(map_file)
            energies.append(np.mean(energy_map))
            entropies.append(self.compute_entropy(energy_map))

        return {
            'num_maps': len(map_files),
            'energy_mean': float(np.mean(energies)),
            'energy_std': float(np.std(energies)),
            'entropy_mean': float(np.mean(entropies)),
            'entropy_std': float(np.std(entropies))
        }


# Export public API
__all__ = [
    'EnergyAtlasLoader',
    'EnergyMapMetadata',
    'ThermodynamicViolation',
    'VALID_SCALES',
    'ENERGY_CONSERVATION_TOLERANCE'
]
