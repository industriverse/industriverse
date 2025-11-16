"""
Energy Signature Calculator

This module implements thermodynamic energy signature calculation for DAC capsules
based on the OBMI (Objective-Based Machine Intelligence) framework.

The Energy Signature Calculator computes:
1. E_state: Total energy state of the capsule
2. dE/dt: Energy flow rate (power)
3. S_state: Entropy state
4. Work potential and efficiency metrics
5. Thermodynamic stability indicators

These signatures provide a physical grounding for capsule behavior and enable
energy-aware optimization and monitoring.

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math

logger = logging.getLogger(__name__)


class EnergyComponent(Enum):
    """Energy components in capsule state."""
    COMPUTATIONAL = "computational"  # CPU/GPU compute energy
    STORAGE = "storage"  # Data storage energy
    NETWORK = "network"  # Network I/O energy
    MEMORY = "memory"  # Memory access energy
    QUANTUM = "quantum"  # Quantum coherence energy (OBMI)


class ThermodynamicState(Enum):
    """Thermodynamic state classification."""
    EQUILIBRIUM = "equilibrium"  # Stable, minimal entropy production
    NEAR_EQUILIBRIUM = "near_equilibrium"  # Small deviations
    FAR_FROM_EQUILIBRIUM = "far_from_equilibrium"  # High entropy production
    CRITICAL = "critical"  # Phase transition point


@dataclass
class EnergyState:
    """
    Energy state snapshot of a capsule.
    
    Attributes:
        timestamp: Measurement timestamp
        total_energy: Total energy (Joules)
        components: Energy by component
        temperature: Effective temperature (Kelvin)
        entropy: Entropy state (J/K)
        free_energy: Helmholtz free energy (J)
        work_potential: Available work (J)
        efficiency: Energy efficiency (0-1)
        metadata: Additional metadata
    """
    timestamp: datetime
    total_energy: float
    components: Dict[str, float]
    temperature: float
    entropy: float
    free_energy: float
    work_potential: float
    efficiency: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_energy": self.total_energy,
            "components": self.components,
            "temperature": self.temperature,
            "entropy": self.entropy,
            "free_energy": self.free_energy,
            "work_potential": self.work_potential,
            "efficiency": self.efficiency,
            "metadata": self.metadata
        }


@dataclass
class EnergyFlow:
    """
    Energy flow measurement (dE/dt).
    
    Attributes:
        timestamp: Measurement timestamp
        power: Power (Watts = J/s)
        power_components: Power by component
        entropy_production: Entropy production rate (W/K)
        dissipation: Energy dissipation rate (W)
        work_rate: Useful work rate (W)
        efficiency_rate: Efficiency change rate (1/s)
        metadata: Additional metadata
    """
    timestamp: datetime
    power: float
    power_components: Dict[str, float]
    entropy_production: float
    dissipation: float
    work_rate: float
    efficiency_rate: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "power": self.power,
            "power_components": self.power_components,
            "entropy_production": self.entropy_production,
            "dissipation": self.dissipation,
            "work_rate": self.work_rate,
            "efficiency_rate": self.efficiency_rate,
            "metadata": self.metadata
        }


@dataclass
class EnergySignature:
    """
    Complete energy signature of a capsule.
    
    Attributes:
        capsule_id: Capsule identifier
        current_state: Current energy state
        current_flow: Current energy flow
        state_history: Historical energy states
        flow_history: Historical energy flows
        thermodynamic_state: Thermodynamic classification
        stability_score: Stability score (0-1)
        created_at: Signature creation time
        updated_at: Last update time
    """
    capsule_id: str
    current_state: EnergyState
    current_flow: EnergyFlow
    state_history: List[EnergyState] = field(default_factory=list)
    flow_history: List[EnergyFlow] = field(default_factory=list)
    thermodynamic_state: ThermodynamicState = ThermodynamicState.EQUILIBRIUM
    stability_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class EnergySignatureConfig:
    """
    Configuration for Energy Signature Calculator.
    
    Attributes:
        history_window: Number of historical measurements to keep
        temperature_baseline: Baseline temperature (K)
        efficiency_threshold: Minimum acceptable efficiency
        stability_threshold: Stability score threshold
        enable_quantum_component: Enable quantum coherence energy
    """
    history_window: int = 100
    temperature_baseline: float = 300.0  # Room temperature (K)
    efficiency_threshold: float = 0.5
    stability_threshold: float = 0.7
    enable_quantum_component: bool = True


class EnergySignatureCalculator:
    """
    Energy Signature Calculator for DAC capsules.
    
    This calculator computes thermodynamic energy signatures that provide
    physical grounding for capsule behavior and enable energy-aware optimization.
    """
    
    def __init__(self, config: Optional[EnergySignatureConfig] = None):
        """
        Initialize Energy Signature Calculator.
        
        Args:
            config: Calculator configuration
        """
        self.config = config or EnergySignatureConfig()
        self.signatures: Dict[str, EnergySignature] = {}
        
        # Physical constants
        self.BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
        self.PLANCK_CONSTANT = 6.62607015e-34  # J⋅s
        
        logger.info(f"Energy Signature Calculator initialized with config: {self.config}")
    
    def _calculate_component_energy(
        self,
        component: EnergyComponent,
        metrics: Dict[str, float]
    ) -> float:
        """
        Calculate energy for a specific component.
        
        Args:
            component: Energy component type
            metrics: Component metrics
        
        Returns:
            Energy in Joules
        """
        if component == EnergyComponent.COMPUTATIONAL:
            # E = CPU_utilization * CPU_power * time
            cpu_util = metrics.get("cpu_utilization", 0.0)  # 0-1
            cpu_power = metrics.get("cpu_power", 100.0)  # Watts
            duration = metrics.get("duration", 1.0)  # seconds
            return cpu_util * cpu_power * duration
        
        elif component == EnergyComponent.STORAGE:
            # E = read_ops * read_energy + write_ops * write_energy
            read_ops = metrics.get("read_ops", 0)
            write_ops = metrics.get("write_ops", 0)
            read_energy = 1e-6  # 1 µJ per read
            write_energy = 5e-6  # 5 µJ per write
            return read_ops * read_energy + write_ops * write_energy
        
        elif component == EnergyComponent.NETWORK:
            # E = bytes_transferred * energy_per_byte
            bytes_transferred = metrics.get("bytes_transferred", 0)
            energy_per_byte = 1e-9  # 1 nJ per byte
            return bytes_transferred * energy_per_byte
        
        elif component == EnergyComponent.MEMORY:
            # E = memory_accesses * energy_per_access
            memory_accesses = metrics.get("memory_accesses", 0)
            energy_per_access = 1e-12  # 1 pJ per access
            return memory_accesses * energy_per_access
        
        elif component == EnergyComponent.QUANTUM:
            # E = ℏω (quantum harmonic oscillator)
            # For OBMI quantum coherence
            if not self.config.enable_quantum_component:
                return 0.0
            
            coherence_level = metrics.get("coherence_level", 0.0)  # 0-1
            frequency = metrics.get("frequency", 1e9)  # Hz
            return self.PLANCK_CONSTANT * frequency * coherence_level
        
        return 0.0
    
    def _calculate_entropy(
        self,
        energy_components: Dict[str, float],
        temperature: float
    ) -> float:
        """
        Calculate entropy state.
        
        Uses Boltzmann entropy: S = k_B * ln(Ω)
        Approximated from energy distribution.
        
        Args:
            energy_components: Energy by component
            temperature: Temperature (K)
        
        Returns:
            Entropy (J/K)
        """
        total_energy = sum(energy_components.values())
        
        if total_energy == 0:
            return 0.0
        
        # Calculate entropy from energy distribution
        entropy = 0.0
        for energy in energy_components.values():
            if energy > 0:
                probability = energy / total_energy
                entropy -= probability * math.log(probability)
        
        # Scale by Boltzmann constant and temperature
        entropy *= self.BOLTZMANN_CONSTANT * temperature
        
        return entropy
    
    def _calculate_free_energy(
        self,
        total_energy: float,
        temperature: float,
        entropy: float
    ) -> float:
        """
        Calculate Helmholtz free energy.
        
        F = E - TS
        
        Args:
            total_energy: Total energy (J)
            temperature: Temperature (K)
            entropy: Entropy (J/K)
        
        Returns:
            Free energy (J)
        """
        return total_energy - temperature * entropy
    
    def _calculate_work_potential(
        self,
        free_energy: float,
        total_energy: float
    ) -> float:
        """
        Calculate available work potential.
        
        Args:
            free_energy: Free energy (J)
            total_energy: Total energy (J)
        
        Returns:
            Work potential (J)
        """
        # Work potential is the free energy available for useful work
        return max(0.0, free_energy)
    
    def _calculate_efficiency(
        self,
        work_potential: float,
        total_energy: float
    ) -> float:
        """
        Calculate energy efficiency.
        
        η = W / E
        
        Args:
            work_potential: Available work (J)
            total_energy: Total energy (J)
        
        Returns:
            Efficiency (0-1)
        """
        if total_energy == 0:
            return 0.0
        
        return min(1.0, work_potential / total_energy)
    
    def _classify_thermodynamic_state(
        self,
        entropy_production: float,
        stability_score: float
    ) -> ThermodynamicState:
        """
        Classify thermodynamic state.
        
        Args:
            entropy_production: Entropy production rate (W/K)
            stability_score: Stability score (0-1)
        
        Returns:
            Thermodynamic state classification
        """
        if stability_score > 0.9 and entropy_production < 1e-6:
            return ThermodynamicState.EQUILIBRIUM
        elif stability_score > 0.7 and entropy_production < 1e-3:
            return ThermodynamicState.NEAR_EQUILIBRIUM
        elif stability_score > 0.5:
            return ThermodynamicState.FAR_FROM_EQUILIBRIUM
        else:
            return ThermodynamicState.CRITICAL
    
    def _calculate_stability_score(
        self,
        energy_variance: float,
        entropy_production: float
    ) -> float:
        """
        Calculate stability score.
        
        Args:
            energy_variance: Energy variance
            entropy_production: Entropy production rate
        
        Returns:
            Stability score (0-1)
        """
        # Stability decreases with variance and entropy production
        variance_factor = 1.0 / (1.0 + energy_variance)
        entropy_factor = 1.0 / (1.0 + entropy_production * 1e6)
        
        return (variance_factor + entropy_factor) / 2.0
    
    def calculate_energy_state(
        self,
        capsule_id: str,
        component_metrics: Dict[str, Dict[str, float]],
        temperature: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EnergyState:
        """
        Calculate energy state for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            component_metrics: Metrics for each energy component
            temperature: Temperature (K), uses baseline if None
            metadata: Additional metadata
        
        Returns:
            Energy state
        """
        timestamp = datetime.now()
        temperature = temperature or self.config.temperature_baseline
        
        # Calculate energy for each component
        energy_components = {}
        for component_name, metrics in component_metrics.items():
            try:
                component = EnergyComponent(component_name)
                energy = self._calculate_component_energy(component, metrics)
                energy_components[component_name] = energy
            except ValueError:
                logger.warning(f"Unknown energy component: {component_name}")
        
        # Calculate total energy
        total_energy = sum(energy_components.values())
        
        # Calculate entropy
        entropy = self._calculate_entropy(energy_components, temperature)
        
        # Calculate free energy
        free_energy = self._calculate_free_energy(total_energy, temperature, entropy)
        
        # Calculate work potential
        work_potential = self._calculate_work_potential(free_energy, total_energy)
        
        # Calculate efficiency
        efficiency = self._calculate_efficiency(work_potential, total_energy)
        
        # Create energy state
        state = EnergyState(
            timestamp=timestamp,
            total_energy=total_energy,
            components=energy_components,
            temperature=temperature,
            entropy=entropy,
            free_energy=free_energy,
            work_potential=work_potential,
            efficiency=efficiency,
            metadata=metadata or {}
        )
        
        logger.info(f"Calculated energy state for capsule {capsule_id}: E={total_energy:.2e}J, η={efficiency:.2f}")
        return state
    
    def calculate_energy_flow(
        self,
        capsule_id: str,
        previous_state: EnergyState,
        current_state: EnergyState
    ) -> EnergyFlow:
        """
        Calculate energy flow (dE/dt) between two states.
        
        Args:
            capsule_id: Capsule identifier
            previous_state: Previous energy state
            current_state: Current energy state
        
        Returns:
            Energy flow
        """
        # Calculate time delta
        dt = (current_state.timestamp - previous_state.timestamp).total_seconds()
        
        if dt == 0:
            dt = 1.0  # Avoid division by zero
        
        # Calculate power (dE/dt)
        power = (current_state.total_energy - previous_state.total_energy) / dt
        
        # Calculate power components
        power_components = {}
        for component in current_state.components:
            if component in previous_state.components:
                dE = current_state.components[component] - previous_state.components[component]
                power_components[component] = dE / dt
        
        # Calculate entropy production rate
        entropy_production = (current_state.entropy - previous_state.entropy) / dt
        
        # Calculate dissipation rate (energy lost to heat)
        dissipation = max(0.0, -power * (1 - current_state.efficiency))
        
        # Calculate work rate
        work_rate = power * current_state.efficiency
        
        # Calculate efficiency rate
        efficiency_rate = (current_state.efficiency - previous_state.efficiency) / dt
        
        # Create energy flow
        flow = EnergyFlow(
            timestamp=current_state.timestamp,
            power=power,
            power_components=power_components,
            entropy_production=entropy_production,
            dissipation=dissipation,
            work_rate=work_rate,
            efficiency_rate=efficiency_rate
        )
        
        logger.info(f"Calculated energy flow for capsule {capsule_id}: P={power:.2e}W, dS/dt={entropy_production:.2e}W/K")
        return flow
    
    def create_signature(
        self,
        capsule_id: str,
        initial_state: EnergyState
    ) -> EnergySignature:
        """
        Create energy signature for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            initial_state: Initial energy state
        
        Returns:
            Energy signature
        """
        # Create initial flow (zero flow)
        initial_flow = EnergyFlow(
            timestamp=initial_state.timestamp,
            power=0.0,
            power_components={},
            entropy_production=0.0,
            dissipation=0.0,
            work_rate=0.0,
            efficiency_rate=0.0
        )
        
        # Create signature
        signature = EnergySignature(
            capsule_id=capsule_id,
            current_state=initial_state,
            current_flow=initial_flow,
            state_history=[initial_state],
            flow_history=[initial_flow],
            thermodynamic_state=ThermodynamicState.EQUILIBRIUM,
            stability_score=1.0
        )
        
        # Store signature
        self.signatures[capsule_id] = signature
        
        logger.info(f"Created energy signature for capsule {capsule_id}")
        return signature
    
    def update_signature(
        self,
        capsule_id: str,
        new_state: EnergyState
    ) -> EnergySignature:
        """
        Update energy signature with new state.
        
        Args:
            capsule_id: Capsule identifier
            new_state: New energy state
        
        Returns:
            Updated energy signature
        
        Raises:
            ValueError: If signature not found
        """
        signature = self.signatures.get(capsule_id)
        if not signature:
            raise ValueError(f"Signature not found for capsule: {capsule_id}")
        
        # Calculate energy flow
        flow = self.calculate_energy_flow(capsule_id, signature.current_state, new_state)
        
        # Update signature
        signature.current_state = new_state
        signature.current_flow = flow
        signature.updated_at = datetime.now()
        
        # Add to history
        signature.state_history.append(new_state)
        signature.flow_history.append(flow)
        
        # Trim history
        if len(signature.state_history) > self.config.history_window:
            signature.state_history = signature.state_history[-self.config.history_window:]
            signature.flow_history = signature.flow_history[-self.config.history_window:]
        
        # Calculate energy variance
        if len(signature.state_history) > 1:
            energies = [s.total_energy for s in signature.state_history]
            mean_energy = sum(energies) / len(energies)
            variance = sum((e - mean_energy) ** 2 for e in energies) / len(energies)
        else:
            variance = 0.0
        
        # Calculate stability score
        signature.stability_score = self._calculate_stability_score(
            variance,
            abs(flow.entropy_production)
        )
        
        # Classify thermodynamic state
        signature.thermodynamic_state = self._classify_thermodynamic_state(
            abs(flow.entropy_production),
            signature.stability_score
        )
        
        logger.info(f"Updated energy signature for capsule {capsule_id}: state={signature.thermodynamic_state.value}")
        return signature
    
    def get_signature(self, capsule_id: str) -> Optional[EnergySignature]:
        """
        Get energy signature for a capsule.
        
        Args:
            capsule_id: Capsule identifier
        
        Returns:
            Energy signature or None if not found
        """
        return self.signatures.get(capsule_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get energy signature statistics.
        
        Returns:
            Statistics dictionary
        """
        total_signatures = len(self.signatures)
        
        by_state = {}
        total_energy = 0.0
        total_power = 0.0
        avg_efficiency = 0.0
        
        for signature in self.signatures.values():
            # Count by thermodynamic state
            state_name = signature.thermodynamic_state.value
            by_state[state_name] = by_state.get(state_name, 0) + 1
            
            # Sum energy and power
            total_energy += signature.current_state.total_energy
            total_power += signature.current_flow.power
            avg_efficiency += signature.current_state.efficiency
        
        if total_signatures > 0:
            avg_efficiency /= total_signatures
        
        return {
            "total_signatures": total_signatures,
            "by_thermodynamic_state": by_state,
            "total_energy": total_energy,
            "total_power": total_power,
            "average_efficiency": avg_efficiency
        }


# Example usage
def main():
    """Example usage of Energy Signature Calculator."""
    # Create calculator
    calculator = EnergySignatureCalculator()
    
    # Calculate initial energy state
    print("\nCalculating initial energy state...")
    component_metrics = {
        "computational": {
            "cpu_utilization": 0.5,
            "cpu_power": 100.0,
            "duration": 1.0
        },
        "storage": {
            "read_ops": 1000,
            "write_ops": 500
        },
        "network": {
            "bytes_transferred": 1000000
        },
        "memory": {
            "memory_accesses": 10000
        },
        "quantum": {
            "coherence_level": 0.8,
            "frequency": 1e9
        }
    }
    
    state1 = calculator.calculate_energy_state(
        "capsule-001",
        component_metrics,
        temperature=300.0
    )
    
    print(f"  Total energy: {state1.total_energy:.2e} J")
    print(f"  Entropy: {state1.entropy:.2e} J/K")
    print(f"  Efficiency: {state1.efficiency:.2%}")
    
    # Create signature
    print("\nCreating energy signature...")
    signature = calculator.create_signature("capsule-001", state1)
    print(f"  Capsule ID: {signature.capsule_id}")
    print(f"  Thermodynamic state: {signature.thermodynamic_state.value}")
    print(f"  Stability score: {signature.stability_score:.2f}")
    
    # Update with new state
    print("\nUpdating energy signature...")
    component_metrics["computational"]["cpu_utilization"] = 0.7
    state2 = calculator.calculate_energy_state(
        "capsule-001",
        component_metrics,
        temperature=305.0
    )
    
    signature = calculator.update_signature("capsule-001", state2)
    print(f"  Power: {signature.current_flow.power:.2e} W")
    print(f"  Entropy production: {signature.current_flow.entropy_production:.2e} W/K")
    print(f"  Thermodynamic state: {signature.thermodynamic_state.value}")
    
    # Get statistics
    print("\nEnergy Signature Statistics:")
    stats = calculator.get_statistics()
    print(f"  Total signatures: {stats['total_signatures']}")
    print(f"  Total energy: {stats['total_energy']:.2e} J")
    print(f"  Average efficiency: {stats['average_efficiency']:.2%}")


if __name__ == "__main__":
    main()
