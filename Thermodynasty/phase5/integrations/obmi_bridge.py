#!/usr/bin/env python3
"""
OBMI Quantum Bridge - Quantum State to Energy Map Adapter

Translates quantum state vectors from OBMI Quantum Enhancement service
into energy map representations suitable for ACE NVP inference.

OBMI Integration:
- Receives quantum state vectors (complex amplitudes)
- Computes probability distributions and energy eigenvalues
- Maps to thermodynamic energy maps
- Applies quantum-informed constraints

Inspired by THRML's discrete probabilistic sampling and energy-based models.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class OBMIQuantumBridge:
    """
    Bridge between OBMI quantum states and Thermodynasty energy maps

    Architecture:
    1. Accept quantum state vectors (complex amplitudes)
    2. Compute probability distributions via Born rule
    3. Map to energy eigenvalue basis
    4. Transform to spatial energy maps
    5. Apply thermodynamic constraints
    """

    def __init__(
        self,
        target_resolution: int = 256,
        energy_scale: float = 1.0,
        temperature: float = 1.0,
        use_gibbs_distribution: bool = True
    ):
        """
        Initialize OBMI Quantum Bridge

        Args:
            target_resolution: Target energy map resolution
            energy_scale: Scaling factor for energy values
            temperature: Temperature for Gibbs/Boltzmann distribution
            use_gibbs_distribution: Use Gibbs distribution for thermal equilibrium
        """
        self.target_resolution = target_resolution
        self.energy_scale = energy_scale
        self.temperature = temperature
        self.use_gibbs_distribution = use_gibbs_distribution

        print(f"✓ OBMI Quantum Bridge initialized")
        print(f"  Target resolution: {target_resolution}x{target_resolution}")
        print(f"  Energy scale: {energy_scale}")
        print(f"  Temperature: {temperature}")
        print(f"  Gibbs distribution: {use_gibbs_distribution}")

    def quantum_state_to_energy_map(
        self,
        state_vector: np.ndarray,
        eigenvalues: Optional[np.ndarray] = None,
        observable: str = "hamiltonian"
    ) -> Tuple[np.ndarray, Dict]:
        """
        Convert quantum state vector to thermodynamic energy map

        Args:
            state_vector: Complex quantum state vector (N,)
            eigenvalues: Energy eigenvalues for each basis state (optional)
            observable: Observable operator ("hamiltonian", "density", "entropy")

        Returns:
            (energy_map, metadata) - 2D energy map and conversion metadata
        """
        # Validate input
        if not np.iscomplexobj(state_vector):
            raise ValueError("State vector must be complex-valued")

        if not np.isclose(np.linalg.norm(state_vector), 1.0, atol=1e-6):
            # Normalize if needed
            state_vector = state_vector / np.linalg.norm(state_vector)

        # Compute probability distribution (Born rule: |ψ|²)
        probabilities = np.abs(state_vector) ** 2

        # If no eigenvalues provided, use position-space representation
        if eigenvalues is None:
            eigenvalues = np.arange(len(state_vector), dtype=np.float64)

        # Compute expectation value of energy
        mean_energy = np.dot(probabilities, eigenvalues)
        energy_variance = np.dot(probabilities, (eigenvalues - mean_energy) ** 2)

        # Map to 2D spatial representation
        if observable == "hamiltonian":
            energy_map = self._map_hamiltonian_to_spatial(
                probabilities, eigenvalues
            )
        elif observable == "density":
            energy_map = self._map_density_to_spatial(
                state_vector
            )
        elif observable == "entropy":
            energy_map = self._map_entropy_to_spatial(
                probabilities
            )
        else:
            raise ValueError(f"Unknown observable: {observable}")

        # Apply thermodynamic constraints
        if self.use_gibbs_distribution:
            energy_map = self._apply_gibbs_distribution(energy_map)

        # Scale to target range
        energy_map = self._normalize_energy_map(energy_map)

        # Metadata
        metadata = {
            'mean_energy': float(mean_energy),
            'energy_variance': float(energy_variance),
            'entropy': float(self._compute_von_neumann_entropy(probabilities)),
            'purity': float(np.sum(probabilities ** 2)),
            'dimension': len(state_vector),
            'observable': observable,
            'resolution': f"{energy_map.shape[0]}x{energy_map.shape[1]}"
        }

        return energy_map, metadata

    def _map_hamiltonian_to_spatial(
        self,
        probabilities: np.ndarray,
        eigenvalues: np.ndarray
    ) -> np.ndarray:
        """
        Map Hamiltonian expectation to 2D energy map

        Uses weighted spatial decomposition based on probability amplitudes.
        """
        dim = len(probabilities)

        # Reshape to 2D (closest square)
        side = int(np.sqrt(dim))
        if side * side < dim:
            side += 1

        # Create padded arrays
        prob_padded = np.zeros(side * side)
        eigen_padded = np.zeros(side * side)
        prob_padded[:dim] = probabilities
        eigen_padded[:dim] = eigenvalues

        # Reshape to 2D
        prob_2d = prob_padded.reshape(side, side)
        eigen_2d = eigen_padded.reshape(side, side)

        # Compute energy density
        energy_density = prob_2d * eigen_2d * self.energy_scale

        # Resize to target resolution
        energy_map = self._resize_map(energy_density, self.target_resolution)

        return energy_map

    def _map_density_to_spatial(
        self,
        state_vector: np.ndarray
    ) -> np.ndarray:
        """
        Map quantum density matrix to spatial energy representation

        Uses position-space density matrix elements.
        """
        # Compute density matrix: ρ = |ψ⟩⟨ψ|
        density_matrix = np.outer(state_vector, np.conj(state_vector))

        # Take real part (diagonal dominates for position representation)
        density_real = np.real(density_matrix)

        # Resize to target resolution
        energy_map = self._resize_map(density_real, self.target_resolution)

        return energy_map

    def _map_entropy_to_spatial(
        self,
        probabilities: np.ndarray
    ) -> np.ndarray:
        """
        Map entropy distribution to spatial energy map

        Higher entropy regions correspond to higher energy density.
        """
        # Local entropy (Shannon entropy per basis state)
        local_entropy = -probabilities * np.log(probabilities + 1e-10)

        # Reshape to 2D
        dim = len(probabilities)
        side = int(np.sqrt(dim))
        if side * side < dim:
            side += 1

        entropy_padded = np.zeros(side * side)
        entropy_padded[:dim] = local_entropy
        entropy_2d = entropy_padded.reshape(side, side)

        # Resize to target resolution
        energy_map = self._resize_map(entropy_2d, self.target_resolution)

        return energy_map

    def _apply_gibbs_distribution(self, energy_map: np.ndarray) -> np.ndarray:
        """
        Apply Gibbs/Boltzmann distribution for thermal equilibrium

        P(E) ∝ exp(-E / kT)

        Reweights energy distribution according to thermal statistics.
        """
        beta = 1.0 / (self.temperature + 1e-10)  # Inverse temperature

        # Gibbs weights
        gibbs_weights = np.exp(-beta * energy_map)
        gibbs_weights = gibbs_weights / (gibbs_weights.sum() + 1e-10)

        # Reweight energy map
        thermal_energy = energy_map * gibbs_weights

        return thermal_energy

    def _normalize_energy_map(self, energy_map: np.ndarray) -> np.ndarray:
        """Normalize energy map to [0, 1] range with physical scaling"""
        # Shift to positive
        energy_min = energy_map.min()
        if energy_min < 0:
            energy_map = energy_map - energy_min

        # Scale by energy scale factor
        energy_map = energy_map * self.energy_scale

        # Normalize to unit total energy (conservation)
        total_energy = energy_map.sum()
        if total_energy > 0:
            energy_map = energy_map / total_energy * self.target_resolution ** 2

        return energy_map.astype(np.float32)

    def _resize_map(self, array_2d: np.ndarray, target_size: int) -> np.ndarray:
        """Resize 2D array to target size using bilinear interpolation"""
        from scipy.ndimage import zoom

        current_size = array_2d.shape[0]
        zoom_factor = target_size / current_size

        if zoom_factor != 1.0:
            resized = zoom(array_2d, zoom_factor, order=1)  # Bilinear
        else:
            resized = array_2d

        # Ensure exact target size
        if resized.shape[0] != target_size:
            resized = resized[:target_size, :target_size]

        return resized

    def _compute_von_neumann_entropy(self, probabilities: np.ndarray) -> float:
        """
        Compute von Neumann entropy of quantum state

        S = -Tr(ρ log ρ) = -Σ p_i log(p_i)

        For pure states, this is Shannon entropy of probability distribution.
        """
        # Avoid log(0)
        probs_safe = probabilities + 1e-10
        entropy = -np.sum(probabilities * np.log(probs_safe))
        return entropy

    def batch_convert(
        self,
        state_vectors: List[np.ndarray],
        eigenvalues_list: Optional[List[np.ndarray]] = None,
        observable: str = "hamiltonian"
    ) -> List[Tuple[np.ndarray, Dict]]:
        """
        Batch conversion of multiple quantum states to energy maps

        Args:
            state_vectors: List of quantum state vectors
            eigenvalues_list: List of eigenvalue arrays (optional)
            observable: Observable operator

        Returns:
            List of (energy_map, metadata) tuples
        """
        if eigenvalues_list is None:
            eigenvalues_list = [None] * len(state_vectors)

        results = []
        for state, eigenvals in zip(state_vectors, eigenvalues_list):
            energy_map, metadata = self.quantum_state_to_energy_map(
                state, eigenvals, observable
            )
            results.append((energy_map, metadata))

        return results


# ============================================================================
# OBMI Service Client
# ============================================================================

class OBMIServiceClient:
    """
    Client for OBMI Quantum Enhancement service

    Handles HTTP/gRPC communication with OBMI service running
    in the industriverse-aws cluster.
    """

    def __init__(
        self,
        service_url: str = "http://obmi-quantum-service.obmi-quantum-enhancement.svc.cluster.local:8080",
        timeout: int = 30
    ):
        """
        Initialize OBMI service client

        Args:
            service_url: OBMI service endpoint URL
            timeout: Request timeout in seconds
        """
        self.service_url = service_url
        self.timeout = timeout
        self.bridge = OBMIQuantumBridge()

        print(f"✓ OBMI Service Client initialized: {service_url}")

    def get_quantum_state(self, state_id: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetch quantum state from OBMI service

        Args:
            state_id: Quantum state identifier

        Returns:
            (state_vector, eigenvalues) tuple

        TODO: Implement actual HTTP/gRPC client for OBMI service
        """
        # Stub implementation
        # In production, this would make HTTP/gRPC call to OBMI service
        raise NotImplementedError("OBMI service client not yet implemented")

    def stream_quantum_states(self):
        """
        Stream quantum states from OBMI service

        Yields:
            (state_id, state_vector, eigenvalues) tuples

        TODO: Implement streaming connection to OBMI
        """
        raise NotImplementedError("OBMI streaming not yet implemented")


# ============================================================================
# Testing
# ============================================================================

def test_obmi_bridge():
    """Test OBMI Quantum Bridge with synthetic quantum states"""
    print("\n" + "="*70)
    print("OBMI QUANTUM BRIDGE TEST")
    print("="*70 + "\n")

    # Create bridge
    bridge = OBMIQuantumBridge(
        target_resolution=256,
        energy_scale=1.0,
        temperature=1.0
    )

    # Test 1: Simple quantum state (superposition)
    print("Test 1: Quantum superposition state")
    dim = 1024  # 32x32 when reshaped
    state_vector = np.random.randn(dim) + 1j * np.random.randn(dim)
    state_vector = state_vector / np.linalg.norm(state_vector)

    eigenvalues = np.linspace(0, 10, dim)  # Energy spectrum

    energy_map, metadata = bridge.quantum_state_to_energy_map(
        state_vector,
        eigenvalues,
        observable="hamiltonian"
    )

    print(f"  Energy map shape: {energy_map.shape}")
    print(f"  Mean energy: {metadata['mean_energy']:.4f}")
    print(f"  Entropy: {metadata['entropy']:.4f}")
    print(f"  Purity: {metadata['purity']:.4f}")
    print(f"  Total energy: {energy_map.sum():.2f}")

    # Test 2: Density matrix representation
    print("\nTest 2: Density matrix representation")
    energy_map_density, metadata_density = bridge.quantum_state_to_energy_map(
        state_vector,
        observable="density"
    )

    print(f"  Energy map shape: {energy_map_density.shape}")
    print(f"  Mean energy: {metadata_density['mean_energy']:.4f}")

    # Test 3: Entropy distribution
    print("\nTest 3: Entropy distribution")
    energy_map_entropy, metadata_entropy = bridge.quantum_state_to_energy_map(
        state_vector,
        observable="entropy"
    )

    print(f"  Energy map shape: {energy_map_entropy.shape}")
    print(f"  Entropy: {metadata_entropy['entropy']:.4f}")

    # Test 4: Batch conversion
    print("\nTest 4: Batch conversion")
    states = [state_vector for _ in range(3)]
    results = bridge.batch_convert(states, observable="hamiltonian")

    print(f"  Converted {len(results)} states")
    print(f"  Average entropy: {np.mean([m['entropy'] for _, m in results]):.4f}")

    print("\n" + "="*70)
    print("✓ OBMI Quantum Bridge tests passed")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_obmi_bridge()
