"""
Unit tests for Energy Signature Calculator

Tests cover:
1. Energy state calculation (E_state)
2. Energy flow calculation (dE/dt)
3. Entropy calculation (S_state)
4. Free energy and work potential
5. Efficiency metrics
6. Thermodynamic state classification
7. Signature creation and updates
8. Statistics and monitoring

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
from datetime import datetime, timedelta

from ..energy_signature import (
    EnergySignatureCalculator,
    EnergySignatureConfig,
    EnergyState,
    EnergyFlow,
    EnergySignature,
    EnergyComponent,
    ThermodynamicState
)


class TestEnergySignatureCalculator:
    """Test suite for Energy Signature Calculator."""
    
    def test_calculator_initialization(self):
        """Test calculator initialization with default config."""
        calculator = EnergySignatureCalculator()
        
        assert calculator.config is not None
        assert calculator.config.history_window == 100
        assert len(calculator.signatures) == 0
    
    def test_calculator_initialization_custom_config(self):
        """Test calculator initialization with custom config."""
        config = EnergySignatureConfig(
            history_window=50,
            temperature_baseline=310.0,
            efficiency_threshold=0.6
        )
        
        calculator = EnergySignatureCalculator(config=config)
        
        assert calculator.config.history_window == 50
        assert calculator.config.temperature_baseline == 310.0
        assert calculator.config.efficiency_threshold == 0.6
    
    def test_calculate_computational_energy(self):
        """Test computational energy calculation."""
        calculator = EnergySignatureCalculator()
        
        metrics = {
            "cpu_utilization": 0.5,
            "cpu_power": 100.0,
            "duration": 1.0
        }
        
        energy = calculator._calculate_component_energy(
            EnergyComponent.COMPUTATIONAL,
            metrics
        )
        
        assert energy == 50.0  # 0.5 * 100.0 * 1.0
    
    def test_calculate_storage_energy(self):
        """Test storage energy calculation."""
        calculator = EnergySignatureCalculator()
        
        metrics = {
            "read_ops": 1000,
            "write_ops": 500
        }
        
        energy = calculator._calculate_component_energy(
            EnergyComponent.STORAGE,
            metrics
        )
        
        assert energy > 0
    
    def test_calculate_network_energy(self):
        """Test network energy calculation."""
        calculator = EnergySignatureCalculator()
        
        metrics = {
            "bytes_transferred": 1000000
        }
        
        energy = calculator._calculate_component_energy(
            EnergyComponent.NETWORK,
            metrics
        )
        
        assert energy > 0
    
    def test_calculate_memory_energy(self):
        """Test memory energy calculation."""
        calculator = EnergySignatureCalculator()
        
        metrics = {
            "memory_accesses": 10000
        }
        
        energy = calculator._calculate_component_energy(
            EnergyComponent.MEMORY,
            metrics
        )
        
        assert energy > 0
    
    def test_calculate_quantum_energy(self):
        """Test quantum energy calculation."""
        calculator = EnergySignatureCalculator()
        
        metrics = {
            "coherence_level": 0.8,
            "frequency": 1e9
        }
        
        energy = calculator._calculate_component_energy(
            EnergyComponent.QUANTUM,
            metrics
        )
        
        assert energy > 0
    
    def test_calculate_quantum_energy_disabled(self):
        """Test quantum energy calculation when disabled."""
        config = EnergySignatureConfig(enable_quantum_component=False)
        calculator = EnergySignatureCalculator(config=config)
        
        metrics = {
            "coherence_level": 0.8,
            "frequency": 1e9
        }
        
        energy = calculator._calculate_component_energy(
            EnergyComponent.QUANTUM,
            metrics
        )
        
        assert energy == 0.0
    
    def test_calculate_entropy(self):
        """Test entropy calculation."""
        calculator = EnergySignatureCalculator()
        
        energy_components = {
            "computational": 50.0,
            "storage": 10.0,
            "network": 5.0
        }
        
        entropy = calculator._calculate_entropy(energy_components, 300.0)
        
        assert entropy > 0
    
    def test_calculate_entropy_zero_energy(self):
        """Test entropy calculation with zero energy."""
        calculator = EnergySignatureCalculator()
        
        energy_components = {
            "computational": 0.0,
            "storage": 0.0
        }
        
        entropy = calculator._calculate_entropy(energy_components, 300.0)
        
        assert entropy == 0.0
    
    def test_calculate_free_energy(self):
        """Test free energy calculation (F = E - TS)."""
        calculator = EnergySignatureCalculator()
        
        free_energy = calculator._calculate_free_energy(
            total_energy=100.0,
            temperature=300.0,
            entropy=0.1
        )
        
        assert free_energy == 100.0 - 300.0 * 0.1
    
    def test_calculate_work_potential(self):
        """Test work potential calculation."""
        calculator = EnergySignatureCalculator()
        
        work_potential = calculator._calculate_work_potential(
            free_energy=50.0,
            total_energy=100.0
        )
        
        assert work_potential == 50.0
    
    def test_calculate_work_potential_negative(self):
        """Test work potential with negative free energy."""
        calculator = EnergySignatureCalculator()
        
        work_potential = calculator._calculate_work_potential(
            free_energy=-10.0,
            total_energy=100.0
        )
        
        assert work_potential == 0.0
    
    def test_calculate_efficiency(self):
        """Test efficiency calculation."""
        calculator = EnergySignatureCalculator()
        
        efficiency = calculator._calculate_efficiency(
            work_potential=50.0,
            total_energy=100.0
        )
        
        assert efficiency == 0.5
    
    def test_calculate_efficiency_zero_energy(self):
        """Test efficiency calculation with zero energy."""
        calculator = EnergySignatureCalculator()
        
        efficiency = calculator._calculate_efficiency(
            work_potential=0.0,
            total_energy=0.0
        )
        
        assert efficiency == 0.0
    
    def test_calculate_efficiency_capped(self):
        """Test efficiency is capped at 1.0."""
        calculator = EnergySignatureCalculator()
        
        efficiency = calculator._calculate_efficiency(
            work_potential=150.0,
            total_energy=100.0
        )
        
        assert efficiency == 1.0
    
    def test_classify_thermodynamic_state_equilibrium(self):
        """Test equilibrium state classification."""
        calculator = EnergySignatureCalculator()
        
        state = calculator._classify_thermodynamic_state(
            entropy_production=1e-7,
            stability_score=0.95
        )
        
        assert state == ThermodynamicState.EQUILIBRIUM
    
    def test_classify_thermodynamic_state_near_equilibrium(self):
        """Test near-equilibrium state classification."""
        calculator = EnergySignatureCalculator()
        
        state = calculator._classify_thermodynamic_state(
            entropy_production=1e-4,
            stability_score=0.8
        )
        
        assert state == ThermodynamicState.NEAR_EQUILIBRIUM
    
    def test_classify_thermodynamic_state_far_from_equilibrium(self):
        """Test far-from-equilibrium state classification."""
        calculator = EnergySignatureCalculator()
        
        state = calculator._classify_thermodynamic_state(
            entropy_production=1e-2,
            stability_score=0.6
        )
        
        assert state == ThermodynamicState.FAR_FROM_EQUILIBRIUM
    
    def test_classify_thermodynamic_state_critical(self):
        """Test critical state classification."""
        calculator = EnergySignatureCalculator()
        
        state = calculator._classify_thermodynamic_state(
            entropy_production=1.0,
            stability_score=0.3
        )
        
        assert state == ThermodynamicState.CRITICAL
    
    def test_calculate_stability_score(self):
        """Test stability score calculation."""
        calculator = EnergySignatureCalculator()
        
        score = calculator._calculate_stability_score(
            energy_variance=0.1,
            entropy_production=1e-6
        )
        
        assert 0.0 <= score <= 1.0
    
    def test_calculate_energy_state(self):
        """Test energy state calculation."""
        calculator = EnergySignatureCalculator()
        
        component_metrics = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            },
            "storage": {
                "read_ops": 1000,
                "write_ops": 500
            }
        }
        
        state = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics,
            temperature=300.0
        )
        
        assert isinstance(state, EnergyState)
        assert state.total_energy > 0
        assert state.temperature == 300.0
        assert state.entropy >= 0
        assert 0.0 <= state.efficiency <= 1.0
    
    def test_calculate_energy_state_with_metadata(self):
        """Test energy state calculation with metadata."""
        calculator = EnergySignatureCalculator()
        
        component_metrics = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics,
            metadata={"version": "1.0.0"}
        )
        
        assert state.metadata["version"] == "1.0.0"
    
    def test_calculate_energy_state_default_temperature(self):
        """Test energy state calculation uses default temperature."""
        calculator = EnergySignatureCalculator()
        
        component_metrics = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics
        )
        
        assert state.temperature == calculator.config.temperature_baseline
    
    def test_calculate_energy_flow(self):
        """Test energy flow calculation."""
        calculator = EnergySignatureCalculator()
        
        # Create two states
        component_metrics1 = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state1 = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics1,
            temperature=300.0
        )
        
        # Second state with higher energy
        component_metrics2 = {
            "computational": {
                "cpu_utilization": 0.7,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state2 = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics2,
            temperature=305.0
        )
        
        # Manually set timestamps for consistent testing
        state1.timestamp = datetime.now()
        state2.timestamp = state1.timestamp + timedelta(seconds=1)
        
        flow = calculator.calculate_energy_flow("capsule-001", state1, state2)
        
        assert isinstance(flow, EnergyFlow)
        assert flow.power != 0  # Energy changed
    
    def test_create_signature(self):
        """Test creating energy signature."""
        calculator = EnergySignatureCalculator()
        
        component_metrics = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics
        )
        
        signature = calculator.create_signature("capsule-001", state)
        
        assert isinstance(signature, EnergySignature)
        assert signature.capsule_id == "capsule-001"
        assert signature.current_state == state
        assert len(signature.state_history) == 1
        assert signature.thermodynamic_state == ThermodynamicState.EQUILIBRIUM
    
    def test_signature_storage(self):
        """Test that signatures are stored."""
        calculator = EnergySignatureCalculator()
        
        component_metrics = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics
        )
        
        signature = calculator.create_signature("capsule-001", state)
        
        assert "capsule-001" in calculator.signatures
        assert calculator.signatures["capsule-001"] == signature
    
    def test_update_signature(self):
        """Test updating energy signature."""
        calculator = EnergySignatureCalculator()
        
        # Create initial signature
        component_metrics1 = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state1 = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics1
        )
        
        signature = calculator.create_signature("capsule-001", state1)
        
        # Update with new state
        component_metrics2 = {
            "computational": {
                "cpu_utilization": 0.7,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state2 = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics2
        )
        
        updated_signature = calculator.update_signature("capsule-001", state2)
        
        assert updated_signature.current_state == state2
        assert len(updated_signature.state_history) == 2
        assert len(updated_signature.flow_history) == 2
    
    def test_update_signature_not_found(self):
        """Test updating non-existent signature."""
        calculator = EnergySignatureCalculator()
        
        component_metrics = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics
        )
        
        with pytest.raises(ValueError):
            calculator.update_signature("nonexistent", state)
    
    def test_signature_history_trimming(self):
        """Test that signature history is trimmed."""
        config = EnergySignatureConfig(history_window=5)
        calculator = EnergySignatureCalculator(config=config)
        
        # Create initial signature
        component_metrics = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics
        )
        
        signature = calculator.create_signature("capsule-001", state)
        
        # Add 10 more states
        for i in range(10):
            state = calculator.calculate_energy_state(
                "capsule-001",
                component_metrics
            )
            calculator.update_signature("capsule-001", state)
        
        # History should be trimmed to 5
        assert len(signature.state_history) == 5
        assert len(signature.flow_history) == 5
    
    def test_get_signature(self):
        """Test getting energy signature."""
        calculator = EnergySignatureCalculator()
        
        component_metrics = {
            "computational": {
                "cpu_utilization": 0.5,
                "cpu_power": 100.0,
                "duration": 1.0
            }
        }
        
        state = calculator.calculate_energy_state(
            "capsule-001",
            component_metrics
        )
        
        signature = calculator.create_signature("capsule-001", state)
        
        retrieved = calculator.get_signature("capsule-001")
        
        assert retrieved is not None
        assert retrieved.capsule_id == "capsule-001"
    
    def test_get_signature_not_found(self):
        """Test getting non-existent signature."""
        calculator = EnergySignatureCalculator()
        
        retrieved = calculator.get_signature("nonexistent")
        
        assert retrieved is None
    
    def test_get_statistics(self):
        """Test getting energy statistics."""
        calculator = EnergySignatureCalculator()
        
        # Create multiple signatures
        for i in range(3):
            component_metrics = {
                "computational": {
                    "cpu_utilization": 0.5,
                    "cpu_power": 100.0,
                    "duration": 1.0
                }
            }
            
            state = calculator.calculate_energy_state(
                f"capsule-{i:03d}",
                component_metrics
            )
            
            calculator.create_signature(f"capsule-{i:03d}", state)
        
        stats = calculator.get_statistics()
        
        assert stats["total_signatures"] == 3
        assert stats["total_energy"] > 0
        assert 0.0 <= stats["average_efficiency"] <= 1.0


class TestEnergyStateDataclass:
    """Test suite for EnergyState dataclass."""
    
    def test_energy_state_to_dict(self):
        """Test energy state serialization."""
        state = EnergyState(
            timestamp=datetime.now(),
            total_energy=100.0,
            components={"computational": 50.0},
            temperature=300.0,
            entropy=0.1,
            free_energy=70.0,
            work_potential=60.0,
            efficiency=0.6,
            metadata={"version": "1.0"}
        )
        
        state_dict = state.to_dict()
        
        assert isinstance(state_dict, dict)
        assert state_dict["total_energy"] == 100.0
        assert state_dict["efficiency"] == 0.6


class TestEnergyFlowDataclass:
    """Test suite for EnergyFlow dataclass."""
    
    def test_energy_flow_to_dict(self):
        """Test energy flow serialization."""
        flow = EnergyFlow(
            timestamp=datetime.now(),
            power=50.0,
            power_components={"computational": 25.0},
            entropy_production=0.01,
            dissipation=10.0,
            work_rate=40.0,
            efficiency_rate=0.001
        )
        
        flow_dict = flow.to_dict()
        
        assert isinstance(flow_dict, dict)
        assert flow_dict["power"] == 50.0
        assert flow_dict["work_rate"] == 40.0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
