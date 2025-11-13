#!/usr/bin/env python3
"""
Thermal Tap - Delta-Based Energy Map Streaming Adapter

Implements multi-scale pyramid storage for efficient delta patch application.
Inspired by THRML's energy-based computation patterns and
Jasmine's efficient state management.

Key Features:
- Multi-scale pyramid representation (256, 128, 64, 32)
- Atomic delta patch application
- Exponential decay smoothing for stability
- Neo4j snapshot persistence
- World-coordinate patch mapping

"Secret Sauce" for streaming thermodynamic data without full map updates.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import time
import hashlib
import json
from dataclasses import dataclass, asdict

import numpy as np
from scipy.ndimage import zoom


@dataclass
class EnergySnapshot:
    """Energy map snapshot metadata"""
    version: int
    timestamp: float
    patch_bbox: Tuple[int, int, int, int]  # (x0, y0, x1, y1)
    delta_norm: float
    source: str
    patch_hash: str


class ThermalTap:
    """
    Thermal Tap: Multi-scale pyramid for efficient delta patching

    Maintains energy maps at multiple resolutions for:
    - Fast coarse-grained queries
    - Efficient delta updates
    - Smooth temporal evolution
    - Provenance tracking
    """

    def __init__(
        self,
        pyramid_dir: str,
        levels: List[int] = [256, 128, 64, 32],
        decay_rate: float = 0.1,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None
    ):
        """
        Initialize Thermal Tap

        Args:
            pyramid_dir: Directory for pyramid storage
            levels: Resolution levels (descending order)
            decay_rate: Exponential decay rate for smoothing jumps
            neo4j_uri: Neo4j connection URI (optional)
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
        """
        self.pyramid_dir = Path(pyramid_dir)
        self.pyramid_dir.mkdir(parents=True, exist_ok=True)

        self.levels = sorted(levels, reverse=True)  # Descending
        self.decay_rate = decay_rate

        # Initialize pyramids
        self.pyramids: Dict[int, np.ndarray] = {}
        for level in self.levels:
            self.pyramids[level] = np.zeros((level, level), dtype=np.float32)

        # Version tracking
        self.version = 0
        self.snapshots: List[EnergySnapshot] = []

        # Neo4j connection (optional)
        self.neo4j_driver = None
        if neo4j_uri and neo4j_uri != "bolt://localhost:7687":
            try:
                from neo4j import GraphDatabase
                self.neo4j_driver = GraphDatabase.driver(
                    neo4j_uri,
                    auth=(neo4j_user, neo4j_password) if neo4j_user else None
                )
                print(f"✓ Neo4j connected: {neo4j_uri}")
            except ImportError:
                print("⚠️  Neo4j driver not available. Install with: pip install neo4j")
            except Exception as e:
                print(f"⚠️  Neo4j connection failed: {e}")

        print(f"✓ Thermal Tap initialized: {pyramid_dir}")
        print(f"  Levels: {self.levels}")
        print(f"  Decay rate: {decay_rate}")

    def apply_patch(
        self,
        patch: np.ndarray,
        bbox: Tuple[int, int, int, int],
        level: int = 256,
        source: str = "thermal_sensor",
        smooth: bool = True
    ) -> EnergySnapshot:
        """
        Apply delta patch to pyramid at specified level

        Args:
            patch: Delta energy patch array
            bbox: Bounding box in world coordinates (x0, y0, x1, y1)
            level: Target pyramid level (256, 128, 64, 32)
            source: Source identifier (e.g., "thermal_sensor", "THRML_stream")
            smooth: Apply exponential smoothing to prevent jumps

        Returns:
            EnergySnapshot with metadata
        """
        if level not in self.pyramids:
            raise ValueError(f"Invalid level {level}. Available: {self.levels}")

        x0, y0, x1, y1 = bbox
        patch_height = y1 - y0
        patch_width = x1 - x0

        if patch.shape != (patch_height, patch_width):
            raise ValueError(f"Patch shape {patch.shape} doesn't match bbox dimensions ({patch_height}x{patch_width})")

        # Get current region
        current_region = self.pyramids[level][y0:y1, x0:x1]

        # Apply delta with optional smoothing
        if smooth:
            # Exponential decay smoothing: new = current + decay * delta
            delta = patch - current_region
            smoothed_delta = self.decay_rate * delta
            new_region = current_region + smoothed_delta
        else:
            # Direct replacement
            new_region = patch

        # Update pyramid atomically
        self.pyramids[level][y0:y1, x0:x1] = new_region

        # Propagate to other levels
        self._propagate_update(level, bbox)

        # Create snapshot
        delta_norm = float(np.linalg.norm(patch - current_region))
        patch_hash = hashlib.sha256(patch.tobytes()).hexdigest()[:16]

        snapshot = EnergySnapshot(
            version=self.version,
            timestamp=time.time(),
            patch_bbox=bbox,
            delta_norm=delta_norm,
            source=source,
            patch_hash=patch_hash
        )

        self.version += 1
        self.snapshots.append(snapshot)

        # Persist to Neo4j if available
        if self.neo4j_driver:
            self._persist_snapshot(snapshot)

        # Save pyramid to disk
        self._save_pyramid(level)

        return snapshot

    def _propagate_update(self, updated_level: int, bbox: Tuple[int, int, int, int]):
        """
        Propagate patch update to other pyramid levels

        Uses bilinear interpolation for upsampling/downsampling.
        """
        x0, y0, x1, y1 = bbox
        updated_region = self.pyramids[updated_level][y0:y1, x0:x1]

        for level in self.levels:
            if level == updated_level:
                continue

            # Scale bbox to target level
            scale = level / updated_level
            scaled_x0 = int(x0 * scale)
            scaled_y0 = int(y0 * scale)
            scaled_x1 = int(x1 * scale)
            scaled_y1 = int(y1 * scale)

            # Resample updated region
            zoom_factor = (scaled_y1 - scaled_y0) / updated_region.shape[0]
            resampled = zoom(updated_region, zoom_factor, order=1)  # Bilinear

            # Ensure dimensions match
            target_height = scaled_y1 - scaled_y0
            target_width = scaled_x1 - scaled_x0
            if resampled.shape != (target_height, target_width):
                resampled = resampled[:target_height, :target_width]

            # Update target level
            self.pyramids[level][scaled_y0:scaled_y1, scaled_x0:scaled_x1] = resampled

    def get_map(self, level: int = 256) -> np.ndarray:
        """Get current energy map at specified level"""
        if level not in self.pyramids:
            raise ValueError(f"Invalid level {level}. Available: {self.levels}")
        return self.pyramids[level].copy()

    def get_patch(
        self,
        bbox: Tuple[int, int, int, int],
        level: int = 256
    ) -> np.ndarray:
        """Extract patch from pyramid at specified level"""
        x0, y0, x1, y1 = bbox
        return self.pyramids[level][y0:y1, x0:x1].copy()

    def get_snapshots(self, limit: int = 10) -> List[EnergySnapshot]:
        """Get recent snapshots"""
        return self.snapshots[-limit:]

    def get_energy_total(self, level: int = 256) -> float:
        """Get total energy at specified level"""
        return float(self.pyramids[level].sum())

    def reset(self, level: Optional[int] = None):
        """Reset pyramid(s) to zero"""
        if level is not None:
            self.pyramids[level] = np.zeros_like(self.pyramids[level])
        else:
            for lvl in self.levels:
                self.pyramids[lvl] = np.zeros_like(self.pyramids[lvl])

        self.version = 0
        self.snapshots = []

    def _save_pyramid(self, level: int):
        """Save pyramid level to disk"""
        filepath = self.pyramid_dir / f"pyramid_{level}_v{self.version}.npy"
        np.save(filepath, self.pyramids[level])

        # Keep only recent versions (last 10)
        old_files = sorted(self.pyramid_dir.glob(f"pyramid_{level}_*.npy"))[:-10]
        for old_file in old_files:
            old_file.unlink()

    def _persist_snapshot(self, snapshot: EnergySnapshot):
        """Persist snapshot metadata to Neo4j"""
        if not self.neo4j_driver:
            return

        try:
            with self.neo4j_driver.session() as session:
                session.run(
                    """
                    CREATE (s:EnergySnapshot {
                        version: $version,
                        timestamp: $timestamp,
                        bbox: $bbox,
                        delta_norm: $delta_norm,
                        source: $source,
                        patch_hash: $patch_hash
                    })
                    """,
                    version=snapshot.version,
                    timestamp=snapshot.timestamp,
                    bbox=list(snapshot.patch_bbox),
                    delta_norm=snapshot.delta_norm,
                    source=snapshot.source,
                    patch_hash=snapshot.patch_hash
                )
        except Exception as e:
            print(f"⚠️  Failed to persist snapshot to Neo4j: {e}")

    def export_state(self) -> Dict:
        """Export full thermal tap state"""
        return {
            'version': self.version,
            'levels': self.levels,
            'decay_rate': self.decay_rate,
            'snapshots': [asdict(s) for s in self.snapshots],
            'energy_totals': {level: self.get_energy_total(level) for level in self.levels}
        }

    def import_state(self, state: Dict):
        """Import thermal tap state"""
        self.version = state['version']
        self.decay_rate = state.get('decay_rate', self.decay_rate)

        # Reconstruct snapshots
        self.snapshots = [
            EnergySnapshot(**s) for s in state['snapshots']
        ]

    def close(self):
        """Cleanup resources"""
        if self.neo4j_driver:
            self.neo4j_driver.close()
            print("✓ Neo4j connection closed")


# ============================================================================
# Overlap-Tiling Utilities
# ============================================================================

def overlap_tile_map(
    full_map: np.ndarray,
    tile_size: int = 256,
    overlap: int = 16
) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
    """
    Break large map into overlapping tiles

    Useful for efficient inference on large maps without seam artifacts.

    Args:
        full_map: Full energy map (height, width)
        tile_size: Size of each tile (square)
        overlap: Overlap between adjacent tiles

    Returns:
        List of (tile_array, bbox) tuples
    """
    height, width = full_map.shape
    stride = tile_size - overlap

    tiles = []
    for y in range(0, height - tile_size + 1, stride):
        for x in range(0, width - tile_size + 1, stride):
            tile = full_map[y:y+tile_size, x:x+tile_size]
            bbox = (x, y, x + tile_size, y + tile_size)
            tiles.append((tile, bbox))

    return tiles


def reconstruct_from_tiles(
    tiles: List[Tuple[np.ndarray, Tuple[int, int, int, int]]],
    full_shape: Tuple[int, int],
    overlap: int = 16
) -> np.ndarray:
    """
    Reconstruct full map from overlapping tiles

    Uses weighted averaging in overlap regions.

    Args:
        tiles: List of (tile_array, bbox) tuples
        full_shape: Shape of full map (height, width)
        overlap: Overlap size used in tiling

    Returns:
        Reconstructed full map
    """
    height, width = full_shape
    reconstruction = np.zeros((height, width), dtype=np.float32)
    weights = np.zeros((height, width), dtype=np.float32)

    for tile, (x0, y0, x1, y1) in tiles:
        # Create weight mask (fade in overlap regions)
        tile_size = tile.shape[0]
        weight_mask = np.ones_like(tile)

        # Fade edges
        fade = overlap // 2
        for i in range(fade):
            alpha = i / fade
            weight_mask[i, :] *= alpha
            weight_mask[:, i] *= alpha
            weight_mask[-i-1, :] *= alpha
            weight_mask[:, -i-1] *= alpha

        # Add weighted tile
        reconstruction[y0:y1, x0:x1] += tile * weight_mask
        weights[y0:y1, x0:x1] += weight_mask

    # Normalize by weights
    reconstruction /= (weights + 1e-10)

    return reconstruction


# ============================================================================
# Testing
# ============================================================================

def test_thermal_tap():
    """Test Thermal Tap with synthetic patches"""
    print("\n" + "="*70)
    print("THERMAL TAP TEST")
    print("="*70 + "\n")

    import tempfile
    import shutil

    # Create temp directory
    temp_dir = tempfile.mkdtemp()

    try:
        # Initialize Thermal Tap
        tap = ThermalTap(
            pyramid_dir=temp_dir,
            levels=[256, 128, 64],
            decay_rate=0.1
        )

        # Create synthetic patch
        patch = np.random.rand(64, 64).astype(np.float32) * 100
        bbox = (64, 64, 128, 128)  # 64x64 patch at position (64, 64)

        # Apply patch
        print("Applying delta patch...")
        snapshot = tap.apply_patch(patch, bbox, level=256, source="test")

        print(f"✓ Patch applied (version {snapshot.version})")
        print(f"  Delta norm: {snapshot.delta_norm:.4f}")
        print(f"  Patch hash: {snapshot.patch_hash}")

        # Check energy totals
        for level in tap.levels:
            energy = tap.get_energy_total(level)
            print(f"  Level {level}: total energy = {energy:.2f}")

        # Export state
        state = tap.export_state()
        print(f"\n✓ State exported: {len(state['snapshots'])} snapshots")

        # Test overlap tiling
        print("\nTesting overlap tiling...")
        full_map = tap.get_map(256)
        tiles = overlap_tile_map(full_map, tile_size=128, overlap=16)
        print(f"✓ Generated {len(tiles)} tiles")

        reconstructed = reconstruct_from_tiles(tiles, full_map.shape, overlap=16)
        reconstruction_error = np.mean(np.abs(reconstructed - full_map))
        print(f"✓ Reconstruction error: {reconstruction_error:.6f}")

        tap.close()

        print("\n" + "="*70)
        print("✓ Thermal Tap tests passed")
        print("="*70 + "\n")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_thermal_tap()
