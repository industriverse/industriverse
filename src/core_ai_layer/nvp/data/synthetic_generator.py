#!/usr/bin/env python3
"""
synthetic_generator.py
Synthetic Energy Map Generator - Phase 4 Data Component

Generates physics-based synthetic energy map sequences when real data is insufficient.
Maintains thermodynamic validity through energy conservation and entropy monitoring.

Thermodynamic Principle:
    All perturbations must preserve energy (within tolerance) and ensure ΔS ≥ 0.

Secret Sauce #8: Synthetic Data Generator with physics-based augmentation.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Callable
from dataclasses import dataclass
from scipy.ndimage import rotate, gaussian_filter, zoom
from scipy.stats import special_ortho_group
from datetime import datetime, timedelta
import json
from pathlib import Path

# Thermodynamic Constants
ENERGY_CONSERVATION_TOLERANCE = 0.05  # 5% tolerance
MIN_ENTROPY_INCREASE = 0.0  # Entropy must not decrease (2nd law)


@dataclass
class PerturbationConfig:
    """Configuration for synthetic perturbations."""
    rotation_range: Tuple[float, float] = (0.0, 360.0)  # degrees
    noise_sigma: float = 0.1  # Gaussian noise std dev
    thermal_blur_sigma: float = 2.0  # Thermal diffusion strength
    scaling_range: Tuple[float, float] = (0.95, 1.05)  # Energy scaling
    translation_range: int = 5  # pixels
    enable_rotation: bool = True
    enable_noise: bool = True
    enable_thermal_blur: bool = True
    enable_scaling: bool = False
    enable_translation: bool = True


class ThermodynamicViolation(Exception):
    """Raised when physical constraints are violated."""
    pass


def compute_entropy(energy_map: np.ndarray) -> float:
    """
    Compute Shannon entropy of energy distribution.

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


def validate_energy_conservation(
    E_before: np.ndarray,
    E_after: np.ndarray,
    tolerance: float = ENERGY_CONSERVATION_TOLERANCE
) -> bool:
    """
    Validate that energy is conserved within tolerance.

    Args:
        E_before: Energy map before transformation
        E_after: Energy map after transformation
        tolerance: Allowed fractional error

    Returns:
        True if conserved

    Raises:
        ThermodynamicViolation if violated
    """
    total_before = np.sum(E_before)
    total_after = np.sum(E_after)

    error = abs(total_after - total_before) / (total_before + 1e-10)

    if error > tolerance:
        raise ThermodynamicViolation(
            f"Energy conservation violated: ΔE/E = {error:.4f} > {tolerance}"
        )

    return True


def validate_entropy_increase(
    E_before: np.ndarray,
    E_after: np.ndarray
) -> bool:
    """
    Validate that entropy does not decrease (2nd law).

    Args:
        E_before: Energy map before transformation
        E_after: Energy map after transformation

    Returns:
        True if entropy increased or stayed same

    Raises:
        ThermodynamicViolation if violated
    """
    S_before = compute_entropy(E_before)
    S_after = compute_entropy(E_after)

    if S_after < S_before - MIN_ENTROPY_INCREASE:
        raise ThermodynamicViolation(
            f"Entropy decreased: ΔS = {S_after - S_before:.4f} < 0"
        )

    return True


def apply_rotation(
    energy_map: np.ndarray,
    angle: Optional[float] = None,
    angle_range: Tuple[float, float] = (0.0, 360.0)
) -> np.ndarray:
    """
    Apply rotation to energy map.

    Args:
        energy_map: 2D energy array
        angle: Rotation angle in degrees (random if None)
        angle_range: Range for random angle

    Returns:
        Rotated energy map
    """
    if angle is None:
        angle = np.random.uniform(*angle_range)

    # Rotate with reshape=False to preserve dimensions
    rotated = rotate(energy_map, angle, reshape=False, order=3, mode='wrap')

    # Renormalize to preserve total energy
    E_original = np.sum(energy_map)
    E_rotated = np.sum(rotated)

    if E_rotated > 1e-10:
        rotated *= E_original / E_rotated

    return rotated


def apply_gaussian_noise(
    energy_map: np.ndarray,
    sigma: float = 0.1
) -> np.ndarray:
    """
    Add Gaussian noise to energy map.

    Args:
        energy_map: 2D energy array
        sigma: Noise standard deviation (relative to mean)

    Returns:
        Noisy energy map
    """
    mean_energy = np.mean(energy_map)
    noise = np.random.normal(0, sigma * mean_energy, energy_map.shape)

    # Add noise and clip to non-negative
    noisy = energy_map + noise
    noisy = np.maximum(noisy, 0)

    # Renormalize to preserve total energy
    E_original = np.sum(energy_map)
    E_noisy = np.sum(noisy)

    if E_noisy > 1e-10:
        noisy *= E_original / E_noisy

    return noisy


def apply_thermal_blur(
    energy_map: np.ndarray,
    sigma: float = 2.0
) -> np.ndarray:
    """
    Apply thermal diffusion (Gaussian blur).

    Simulates heat diffusion via Gaussian kernel.

    Args:
        energy_map: 2D energy array
        sigma: Blur strength (pixels)

    Returns:
        Blurred energy map
    """
    # Apply Gaussian filter
    blurred = gaussian_filter(energy_map, sigma=sigma, mode='wrap')

    # Renormalize to preserve total energy
    E_original = np.sum(energy_map)
    E_blurred = np.sum(blurred)

    if E_blurred > 1e-10:
        blurred *= E_original / E_blurred

    return blurred


def apply_translation(
    energy_map: np.ndarray,
    shift_x: Optional[int] = None,
    shift_y: Optional[int] = None,
    max_shift: int = 5
) -> np.ndarray:
    """
    Apply spatial translation.

    Args:
        energy_map: 2D energy array
        shift_x: Horizontal shift in pixels (random if None)
        shift_y: Vertical shift in pixels (random if None)
        max_shift: Maximum shift magnitude

    Returns:
        Translated energy map
    """
    if shift_x is None:
        shift_x = np.random.randint(-max_shift, max_shift + 1)
    if shift_y is None:
        shift_y = np.random.randint(-max_shift, max_shift + 1)

    # Use np.roll for periodic boundary conditions
    translated = np.roll(energy_map, shift=(shift_y, shift_x), axis=(0, 1))

    return translated


def apply_energy_scaling(
    energy_map: np.ndarray,
    scale: Optional[float] = None,
    scale_range: Tuple[float, float] = (0.95, 1.05)
) -> np.ndarray:
    """
    Apply uniform energy scaling.

    Args:
        energy_map: 2D energy array
        scale: Scaling factor (random if None)
        scale_range: Range for random scaling

    Returns:
        Scaled energy map
    """
    if scale is None:
        scale = np.random.uniform(*scale_range)

    return energy_map * scale


def generate_base_pattern(
    size: int = 256,
    pattern_type: str = 'turbulent'
) -> np.ndarray:
    """
    Generate base energy pattern.

    Args:
        size: Map dimension (square)
        pattern_type: Type of pattern ('turbulent', 'laminar', 'vortex', 'random')

    Returns:
        Base energy map (size × size)
    """
    if pattern_type == 'turbulent':
        # Multi-scale Perlin-like noise
        base = np.zeros((size, size))
        for scale in [4, 8, 16, 32, 64]:
            noise = np.random.randn(size // scale, size // scale)
            noise_upsampled = zoom(noise, scale, order=3)
            # Crop or pad to exact size
            if noise_upsampled.shape[0] > size:
                noise_upsampled = noise_upsampled[:size, :size]
            else:
                pad_h = size - noise_upsampled.shape[0]
                pad_w = size - noise_upsampled.shape[1]
                noise_upsampled = np.pad(noise_upsampled, ((0, pad_h), (0, pad_w)))
            base += noise_upsampled / scale

        base = np.abs(base)  # Energy is non-negative

    elif pattern_type == 'laminar':
        # Smooth gradient
        x = np.linspace(0, 2 * np.pi, size)
        y = np.linspace(0, 2 * np.pi, size)
        X, Y = np.meshgrid(x, y)
        base = np.sin(X) * np.cos(Y) + 2.0

    elif pattern_type == 'vortex':
        # Radial vortex pattern
        x = np.linspace(-1, 1, size)
        y = np.linspace(-1, 1, size)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        Theta = np.arctan2(Y, X)
        base = np.exp(-R**2) * (1 + np.sin(5 * Theta))

    elif pattern_type == 'random':
        # Pure random
        base = np.random.exponential(1.0, (size, size))

    else:
        raise ValueError(f"Unknown pattern type: {pattern_type}")

    # Normalize to mean energy ~ 1.0
    base = base / np.mean(base)

    return base


def generate_sequence(
    base_map: np.ndarray,
    n_steps: int = 10,
    config: Optional[PerturbationConfig] = None,
    return_metadata: bool = True
) -> Tuple[np.ndarray, Optional[List[Dict]]]:
    """
    Generate synthetic time series from base map.

    Applies sequential perturbations while maintaining thermodynamic validity.

    Args:
        base_map: Initial energy map (H, W)
        n_steps: Number of time steps to generate
        config: Perturbation configuration
        return_metadata: Whether to return metadata for each step

    Returns:
        sequence: (T, H, W) array of energy maps
        metadata: List of dicts with per-step statistics (if return_metadata=True)
    """
    if config is None:
        config = PerturbationConfig()

    sequence = [base_map.copy()]
    metadata = [] if return_metadata else None

    # Initial metadata
    if return_metadata:
        metadata.append({
            'step': 0,
            'energy_mean': float(np.mean(base_map)),
            'energy_var': float(np.var(base_map)),
            'entropy': compute_entropy(base_map),
            'perturbations': []
        })

    current_map = base_map.copy()

    for step in range(1, n_steps):
        E_before = np.sum(current_map)
        S_before = compute_entropy(current_map)

        perturbations_applied = []

        # Apply perturbations
        if config.enable_rotation:
            current_map = apply_rotation(
                current_map,
                angle_range=config.rotation_range
            )
            perturbations_applied.append('rotation')

        if config.enable_thermal_blur:
            current_map = apply_thermal_blur(
                current_map,
                sigma=config.thermal_blur_sigma
            )
            perturbations_applied.append('thermal_blur')

        if config.enable_translation:
            current_map = apply_translation(
                current_map,
                max_shift=config.translation_range
            )
            perturbations_applied.append('translation')

        if config.enable_noise:
            current_map = apply_gaussian_noise(
                current_map,
                sigma=config.noise_sigma
            )
            perturbations_applied.append('noise')

        if config.enable_scaling:
            current_map = apply_energy_scaling(
                current_map,
                scale_range=config.scaling_range
            )
            perturbations_applied.append('scaling')

        # Validate thermodynamics
        E_after = np.sum(current_map)
        S_after = compute_entropy(current_map)

        # Check energy conservation
        energy_error = abs(E_after - E_before) / (E_before + 1e-10)
        if energy_error > ENERGY_CONSERVATION_TOLERANCE:
            # Renormalize
            current_map *= E_before / E_after
            E_after = np.sum(current_map)

        # Entropy should not decrease (allow small numerical errors)
        if S_after < S_before - 1e-6:
            # This shouldn't happen with our perturbations, but check
            print(f"Warning: Entropy decreased at step {step}: "
                  f"ΔS = {S_after - S_before:.6f}")

        sequence.append(current_map.copy())

        # Record metadata
        if return_metadata:
            metadata.append({
                'step': step,
                'energy_mean': float(np.mean(current_map)),
                'energy_var': float(np.var(current_map)),
                'entropy': S_after,
                'entropy_delta': S_after - S_before,
                'energy_conservation_error': energy_error,
                'perturbations': perturbations_applied
            })

    sequence_array = np.stack(sequence, axis=0)

    return sequence_array, metadata


def save_sequence(
    sequence: np.ndarray,
    output_dir: Path,
    domain: str,
    base_id: str,
    metadata: Optional[List[Dict]] = None
) -> List[str]:
    """
    Save sequence to disk as individual .npy files.

    Args:
        sequence: (T, H, W) array
        output_dir: Output directory
        domain: Physics domain name
        base_id: Base identifier for naming
        metadata: Optional metadata list

    Returns:
        List of saved file paths
    """
    output_dir = Path(output_dir)
    domain_dir = output_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []

    for t in range(sequence.shape[0]):
        # Generate filename
        timestamp = datetime.now() + timedelta(seconds=t)
        filename = f"{base_id}_t{t:04d}_{timestamp.strftime('%Y%m%d_%H%M%S')}.npy"
        filepath = domain_dir / filename

        # Save energy map
        np.save(filepath, sequence[t])
        saved_paths.append(str(filepath))

        # Save metadata if provided
        if metadata is not None and t < len(metadata):
            metadata_path = domain_dir / filename.replace('.npy', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata[t], f, indent=2)

    return saved_paths


def generate_domain_dataset(
    domain: str,
    output_dir: Path,
    n_sequences: int = 10,
    sequence_length: int = 10,
    pattern_type: str = 'turbulent',
    size: int = 256,
    config: Optional[PerturbationConfig] = None
) -> Dict[str, any]:
    """
    Generate complete synthetic dataset for a domain.

    Args:
        domain: Physics domain name
        output_dir: Output directory
        n_sequences: Number of sequences to generate
        sequence_length: Time steps per sequence
        pattern_type: Base pattern type
        size: Map size
        config: Perturbation configuration

    Returns:
        Statistics dictionary
    """
    output_dir = Path(output_dir)

    total_maps = 0
    all_metadata = []

    for seq_idx in range(n_sequences):
        # Generate base pattern
        base_map = generate_base_pattern(size=size, pattern_type=pattern_type)

        # Generate sequence
        sequence, metadata = generate_sequence(
            base_map,
            n_steps=sequence_length,
            config=config,
            return_metadata=True
        )

        # Save sequence
        base_id = f"{domain}_seq{seq_idx:04d}"
        saved_paths = save_sequence(
            sequence,
            output_dir,
            domain,
            base_id,
            metadata
        )

        total_maps += len(saved_paths)
        all_metadata.extend(metadata)

    # Compute statistics
    energies = [m['energy_mean'] for m in all_metadata]
    entropies = [m['entropy'] for m in all_metadata]

    stats = {
        'domain': domain,
        'n_sequences': n_sequences,
        'sequence_length': sequence_length,
        'total_maps': total_maps,
        'pattern_type': pattern_type,
        'size': size,
        'energy_mean': float(np.mean(energies)),
        'energy_std': float(np.std(energies)),
        'entropy_mean': float(np.mean(entropies)),
        'entropy_std': float(np.std(entropies))
    }

    return stats


# Export public API
__all__ = [
    'generate_sequence',
    'generate_base_pattern',
    'generate_domain_dataset',
    'save_sequence',
    'apply_rotation',
    'apply_gaussian_noise',
    'apply_thermal_blur',
    'apply_translation',
    'apply_energy_scaling',
    'compute_entropy',
    'validate_energy_conservation',
    'validate_entropy_increase',
    'PerturbationConfig',
    'ThermodynamicViolation'
]
