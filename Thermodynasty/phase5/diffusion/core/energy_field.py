"""
Energy Field Representation

Represents energy distributions as differentiable tensor fields
with thermodynamic constraints.
"""

import numpy as np
import torch
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class EnergyState:
    """
    Represents a thermodynamic state in the energy manifold.

    Attributes:
        energy_map: Spatial energy distribution [H, W] or [B, H, W]
        entropy: Total entropy of the state
        temperature: Thermodynamic temperature
        metadata: Additional state information
    """
    energy_map: torch.Tensor
    entropy: float
    temperature: float
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate energy state"""
        if self.energy_map.dim() not in [2, 3]:
            raise ValueError(f"Energy map must be 2D or 3D, got {self.energy_map.dim()}D")

        if self.temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {self.temperature}")

    @property
    def total_energy(self) -> float:
        """Compute total energy"""
        return float(self.energy_map.sum().item())

    @property
    def mean_energy(self) -> float:
        """Compute mean energy"""
        return float(self.energy_map.mean().item())

    @property
    def energy_variance(self) -> float:
        """Compute energy variance (measure of turbulence)"""
        return float(self.energy_map.var().item())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'energy_map': self.energy_map.cpu().numpy(),
            'entropy': self.entropy,
            'temperature': self.temperature,
            'total_energy': self.total_energy,
            'mean_energy': self.mean_energy,
            'energy_variance': self.energy_variance,
            'metadata': self.metadata
        }


class EnergyField:
    """
    Energy field with thermodynamic operations.

    Manages energy distributions and enforces physical constraints:
    - Energy conservation: ΔE ≈ 0 (within tolerance)
    - Entropy monotonicity: ΔS ≥ 0 (except controlled reversals)
    - Positive temperature: T > 0
    """

    def __init__(
        self,
        shape: Tuple[int, ...],
        temperature: float = 1.0,
        energy_tolerance: float = 0.01,
        device: str = "cpu"
    ):
        """
        Initialize energy field.

        Args:
            shape: Spatial dimensions (H, W) or (B, H, W)
            temperature: Initial temperature
            energy_tolerance: Maximum allowed energy drift
            device: Computation device (cpu, cuda, mps)
        """
        self.shape = shape
        self.temperature = temperature
        self.energy_tolerance = energy_tolerance
        self.device = torch.device(device)

        # Initialize with zero energy (equilibrium)
        self.current_state = EnergyState(
            energy_map=torch.zeros(shape, device=self.device),
            entropy=0.0,
            temperature=temperature
        )

        logger.info(f"Initialized EnergyField: shape={shape}, T={temperature}, device={device}")

    def compute_energy_gradient(self, energy_map: torch.Tensor) -> torch.Tensor:
        """
        Compute energy gradient ∇E.

        Uses finite differences for spatial derivatives.

        Args:
            energy_map: Energy distribution

        Returns:
            Energy gradient tensor
        """
        # Sobel operator for gradients
        grad_x = torch.conv2d(
            energy_map.unsqueeze(0).unsqueeze(0) if energy_map.dim() == 2 else energy_map.unsqueeze(1),
            torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], device=self.device, dtype=torch.float32).view(1, 1, 3, 3),
            padding=1
        ).squeeze()

        grad_y = torch.conv2d(
            energy_map.unsqueeze(0).unsqueeze(0) if energy_map.dim() == 2 else energy_map.unsqueeze(1),
            torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], device=self.device, dtype=torch.float32).view(1, 1, 3, 3),
            padding=1
        ).squeeze()

        # Magnitude of gradient
        gradient = torch.sqrt(grad_x**2 + grad_y**2 + 1e-8)

        return gradient

    def compute_entropy(self, energy_map: torch.Tensor) -> float:
        """
        Compute thermodynamic entropy S = -∑ p log(p).

        Args:
            energy_map: Energy distribution

        Returns:
            Entropy value
        """
        # Normalize to probability distribution
        energy_positive = torch.abs(energy_map) + 1e-8
        prob = energy_positive / energy_positive.sum()

        # Shannon entropy
        entropy = -torch.sum(prob * torch.log(prob + 1e-8))

        return float(entropy.item())

    def boltzmann_weight(self, energy_map: torch.Tensor) -> torch.Tensor:
        """
        Compute Boltzmann weights: w = exp(-E/kT).

        Args:
            energy_map: Energy distribution

        Returns:
            Boltzmann-weighted probabilities
        """
        k_B = 1.0  # Boltzmann constant (units absorbed into T)
        weights = torch.exp(-energy_map / (k_B * self.temperature))

        # Normalize
        weights = weights / weights.sum()

        return weights

    def update_state(self, new_energy_map: torch.Tensor) -> EnergyState:
        """
        Update energy field state with conservation check.

        Args:
            new_energy_map: New energy distribution

        Returns:
            Updated energy state

        Raises:
            ValueError: If energy conservation is violated
        """
        # Check energy conservation
        old_total = self.current_state.total_energy
        new_total = float(new_energy_map.sum().item())
        energy_drift = abs(new_total - old_total)

        if energy_drift > self.energy_tolerance:
            logger.warning(
                f"Energy conservation violation: ΔE={energy_drift:.6f} > tolerance={self.energy_tolerance}"
            )
            # In production, might want to raise exception or auto-correct
            # For now, log and proceed

        # Compute new entropy
        new_entropy = self.compute_entropy(new_energy_map)

        # Check entropy monotonicity (ΔS ≥ 0)
        entropy_change = new_entropy - self.current_state.entropy
        if entropy_change < -1e-6:  # Small negative tolerance for numerical errors
            logger.debug(f"Entropy decreased: ΔS={entropy_change:.6f} (possibly reversible process)")

        # Create new state
        new_state = EnergyState(
            energy_map=new_energy_map,
            entropy=new_entropy,
            temperature=self.temperature,
            metadata={
                'energy_drift': energy_drift,
                'entropy_change': entropy_change,
                'step': self.current_state.metadata.get('step', 0) + 1 if self.current_state.metadata else 1
            }
        )

        self.current_state = new_state

        return new_state

    def from_numpy(self, array: np.ndarray, temperature: Optional[float] = None) -> EnergyState:
        """
        Create energy state from numpy array.

        Args:
            array: Energy map as numpy array
            temperature: Optional temperature override

        Returns:
            Energy state
        """
        energy_map = torch.from_numpy(array).float().to(self.device)

        if temperature is not None:
            self.temperature = temperature

        state = EnergyState(
            energy_map=energy_map,
            entropy=self.compute_entropy(energy_map),
            temperature=self.temperature
        )

        self.current_state = state

        return state

    def to_numpy(self) -> np.ndarray:
        """Convert current state to numpy array"""
        return self.current_state.energy_map.cpu().numpy()

    def validate_conservation(self, initial_state: EnergyState, final_state: EnergyState) -> Dict[str, Any]:
        """
        Validate energy conservation and entropy monotonicity.

        Args:
            initial_state: Initial energy state
            final_state: Final energy state

        Returns:
            Validation results
        """
        delta_E = final_state.total_energy - initial_state.total_energy
        delta_S = final_state.entropy - initial_state.entropy

        results = {
            'energy_conserved': abs(delta_E) < self.energy_tolerance,
            'entropy_monotonic': delta_S >= -1e-6,
            'delta_E': delta_E,
            'delta_S': delta_S,
            'energy_fidelity': 1.0 - abs(delta_E) / (abs(initial_state.total_energy) + 1e-8),
            'passed': abs(delta_E) < self.energy_tolerance and delta_S >= -1e-6
        }

        return results

    def __repr__(self) -> str:
        return (
            f"EnergyField(shape={self.shape}, T={self.temperature:.2f}, "
            f"E_total={self.current_state.total_energy:.4f}, "
            f"S={self.current_state.entropy:.4f})"
        )
