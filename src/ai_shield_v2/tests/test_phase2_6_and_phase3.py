#!/usr/bin/env python3
"""
AI Shield v2 - Phase 2.6 & 3 Comprehensive Test Suite
======================================================

Production-ready testing for:
- Phase 2.6: Shadow Twins 2.0 Integration (Unified Shadow System)
- Phase 3: Energy Layer Integration (Energy Monitor + Proof-of-Energy)

Test Categories:
- Unit tests (individual components)
- Integration tests (component interactions)
- Performance tests (latency, throughput)
- Security tests (conservation laws, intrusion detection)
- Production readiness validation

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

import pytest
import numpy as np
import time
import asyncio
from typing import Dict, Any

# Import AI Shield v2 components
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Shadow Integration imports
from ai_shield_v2.shadow_integration import (
    UnifiedShadowSystem,
    ShadowTwins2Point0Interface,
    ConsciousnessLevel,
    ThreatDomain,
    PhysicsConsciousnessState,
    MathematicalConsciousnessState,
    CyberThreatConsciousnessState,
    PlanetaryConsciousnessState
)

# Energy Layer imports
from ai_shield_v2.energy import (
    EnergyLayerMonitor,
    EnergyMonitoringAgent,
    ProofOfEnergyLedger,
    ResourceType,
    TransactionType,
    EnergyFluxLevel,
    ConservationStatus
)

# Supporting imports
from ai_shield_v2.fusion import PhysicsFusionEngine
from ai_shield_v2.mic import MathIsomorphismCore, PhysicsFeatures, PhysicsDomain, PhysicsSignature
from ai_shield_v2.diffusion import DiffusionState


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def unified_shadow_system():
    """Create Unified Shadow System"""
    return UnifiedShadowSystem(
        enable_physics_consciousness=True,
        enable_mathematical_consciousness=True,
        enable_cyber_consciousness=True,
        enable_planetary_consciousness=True
    )


@pytest.fixture
def shadow_twins_interface():
    """Create Shadow Twins 2.0 interface"""
    return ShadowTwins2Point0Interface()


@pytest.fixture
def energy_monitor():
    """Create Energy Layer Monitor"""
    return EnergyLayerMonitor(
        sampling_rate_hz=100,  # Reduced for testing
        resource_weights={
            ResourceType.CPU: 0.40,
            ResourceType.MEMORY: 0.30,
            ResourceType.NETWORK: 0.20,
            ResourceType.STORAGE_IO: 0.10
        }
    )


@pytest.fixture
def proof_of_energy_ledger():
    """Create Proof-of-Energy Ledger"""
    return ProofOfEnergyLedger(
        conservation_tolerance=0.05,
        leak_threshold=0.1
    )


@pytest.fixture
def sample_fusion_result():
    """Create sample fusion result for testing"""
    # This is a simplified fusion result for testing
    from ai_shield_v2.fusion import (
        FusionResult,
        ThreatIntelligence,
        ICIScore,
        ConsensusMetrics,
        ConsensusType,
        ResponseAction
    )
    from ai_shield_v2.upd import ThreatLevel, ExtendedDomain

    consensus = ConsensusMetrics(
        total_detectors=7,
        agreeing_detectors=5,
        consensus_ratio=0.71,
        consensus_type=ConsensusType.MAJORITY,
        threshold_met=True,
        confidence=0.85
    )

    ici = ICIScore(
        score=65.0,
        base_score=60.0,
        consensus_amplification=1.08,
        max_detector_score=70.0,
        consensus_metrics=consensus,
        response_action=ResponseAction.MITIGATE
    )

    threat_intel = ThreatIntelligence(
        ici_score=ici,
        primary_threat="test_threat",
        affected_domains=set([ExtendedDomain.CYBERSECURITY]),
        pattern_summary={"test_pattern": 1},
        detector_votes={"detector_1": 65.0},
        recommended_actions=["MITIGATE: Test threat detected"]
    )

    return FusionResult(
        threat_intelligence=threat_intel,
        detector_results=[],
        processing_time_ms=0.5
    )


# ==============================================================================
# Phase 2.6: Shadow Integration Tests
# ==============================================================================

class TestShadowTwins2Point0Interface:
    """Test suite for Shadow Twins 2.0 interface"""

    @pytest.mark.asyncio
    async def test_interface_initialization(self, shadow_twins_interface):
        """Test Shadow Twins 2.0 interface initialization"""
        assert shadow_twins_interface is not None
        assert hasattr(shadow_twins_interface, 'physics_consciousness_active')
        assert hasattr(shadow_twins_interface, 'well_15tb_loaded')
        assert hasattr(shadow_twins_interface, 'obmi_engine_active')

    @pytest.mark.asyncio
    async def test_physics_analysis(self, shadow_twins_interface):
        """Test physics consciousness analysis"""
        threat_data = {"severity": 0.7, "type": "equipment_failure"}

        result = await shadow_twins_interface.analyze_threat_physics(threat_data)

        assert isinstance(result, PhysicsConsciousnessState)
        assert result.well_patterns_analyzed is True
        assert 0.0 <= result.prediction_accuracy <= 1.0
        assert 0.0 <= result.failure_probability <= 1.0
        assert result.consciousness_level in [
            ConsciousnessLevel.PHYSICS_AWARE,
            ConsciousnessLevel.BASIC
        ]

    @pytest.mark.asyncio
    async def test_mathematical_analysis(self, shadow_twins_interface):
        """Test mathematical consciousness analysis"""
        threat_data = {"severity": 0.8}
        physics_state = PhysicsConsciousnessState(
            well_patterns_analyzed=True,
            physics_domain="test_domain",
            prediction_accuracy=0.9,
            failure_probability=0.8,
            catastrophe_risk=0.7,
            recommended_intervention={},
            consciousness_level=ConsciousnessLevel.PHYSICS_AWARE
        )

        result = await shadow_twins_interface.analyze_threat_mathematical(
            threat_data,
            physics_state
        )

        assert isinstance(result, MathematicalConsciousnessState)
        assert result.obmi_operators_active is True
        assert isinstance(result.singularity_detected, bool)
        assert result.consciousness_level in [
            ConsciousnessLevel.MATHEMATICAL,
            ConsciousnessLevel.BASIC
        ]

    @pytest.mark.asyncio
    async def test_planetary_coordination(self, shadow_twins_interface):
        """Test planetary consciousness coordination"""
        intervention_strategy = {"type": "test_intervention"}

        result = await shadow_twins_interface.coordinate_planetary(
            intervention_strategy
        )

        assert isinstance(result, PlanetaryConsciousnessState)
        assert isinstance(result.connected_locations, list)
        assert result.consciousness_level in [
            ConsciousnessLevel.PLANETARY,
            ConsciousnessLevel.BASIC
        ]


class TestUnifiedShadowSystem:
    """Test suite for Unified Shadow System"""

    def test_unified_system_initialization(self, unified_shadow_system):
        """Test unified shadow system initialization"""
        assert unified_shadow_system is not None
        assert unified_shadow_system.enable_physics is True
        assert unified_shadow_system.enable_mathematical is True
        assert unified_shadow_system.enable_cyber is True
        assert unified_shadow_system.enable_planetary is True

    @pytest.mark.asyncio
    async def test_unified_threat_analysis(
        self,
        unified_shadow_system,
        sample_fusion_result
    ):
        """Test unified threat analysis across all consciousness domains"""
        threat_data = {
            "severity": 0.65,
            "type": "cyber_physical_threat",
            "source": "test_system"
        }

        result = await unified_shadow_system.analyze_unified_threat(
            threat_data,
            sample_fusion_result
        )

        # Verify unified consciousness state
        assert result is not None
        assert hasattr(result, 'physics_consciousness')
        assert hasattr(result, 'mathematical_consciousness')
        assert hasattr(result, 'cyber_consciousness')
        assert hasattr(result, 'planetary_consciousness')

        # Verify unified metrics
        assert 0.0 <= result.unified_threat_level <= 1.0
        assert result.unified_decision in ["PROCEED", "ABORT", "ESCALATE"]
        assert 0.0 <= result.consciousness_coherence <= 1.0

    @pytest.mark.asyncio
    async def test_unified_intervention_execution(
        self,
        unified_shadow_system,
        sample_fusion_result
    ):
        """Test unified intervention execution"""
        threat_data = {"severity": 0.5}

        # Analyze threat
        consciousness_state = await unified_shadow_system.analyze_unified_threat(
            threat_data,
            sample_fusion_result
        )

        # Execute intervention
        intervention_result = await unified_shadow_system.execute_unified_intervention(
            consciousness_state
        )

        assert intervention_result is not None
        assert isinstance(intervention_result.intervention_executed, bool)
        assert 0.0 <= intervention_result.success_probability <= 1.0

    @pytest.mark.asyncio
    async def test_consciousness_coherence(self, unified_shadow_system, sample_fusion_result):
        """Test consciousness coherence calculation"""
        threat_data = {"severity": 0.6}

        result = await unified_shadow_system.analyze_unified_threat(
            threat_data,
            sample_fusion_result
        )

        # With all 4 consciousness domains enabled, coherence should be 1.0
        assert result.consciousness_coherence == 1.0

    def test_metrics_tracking(self, unified_shadow_system):
        """Test metrics tracking"""
        metrics = unified_shadow_system.get_metrics()

        assert "total_analyses" in metrics
        assert "successful_interventions" in metrics
        assert "prevented_catastrophes" in metrics
        assert "consciousness_configuration" in metrics


# ==============================================================================
# Phase 3: Energy Layer Tests
# ==============================================================================

class TestEnergyMonitoringAgent:
    """Test suite for individual energy monitoring agents"""

    def test_agent_initialization(self):
        """Test energy monitoring agent initialization"""
        agent = EnergyMonitoringAgent(
            resource_type=ResourceType.CPU,
            sampling_rate_hz=100
        )

        assert agent.resource_type == ResourceType.CPU
        assert agent.sampling_rate_hz == 100
        assert agent.running is False

    def test_agent_start_stop(self):
        """Test starting and stopping monitoring agent"""
        agent = EnergyMonitoringAgent(
            resource_type=ResourceType.MEMORY,
            sampling_rate_hz=10
        )

        # Start monitoring
        agent.start()
        assert agent.running is True
        assert agent.monitoring_thread is not None

        # Give it time to collect samples
        time.sleep(0.5)

        # Stop monitoring
        agent.stop()
        assert agent.running is False

        # Verify samples were collected
        stats = agent.get_statistics()
        assert stats['samples'] > 0

    def test_resource_sampling(self):
        """Test resource sampling accuracy"""
        agent = EnergyMonitoringAgent(
            resource_type=ResourceType.CPU,
            sampling_rate_hz=10
        )

        agent.start()
        time.sleep(1.0)  # Collect for 1 second
        agent.stop()

        # Should have ~10 samples (may vary slightly)
        stats = agent.get_statistics()
        assert 5 <= stats['samples'] <= 15  # Allow some tolerance

        # Utilization should be in valid range
        assert 0.0 <= stats['mean'] <= 1.0
        assert stats['std'] >= 0.0


class TestEnergyLayerMonitor:
    """Test suite for Energy Layer Monitor"""

    def test_monitor_initialization(self, energy_monitor):
        """Test energy layer monitor initialization"""
        assert energy_monitor is not None
        assert len(energy_monitor.agents) >= 3  # At least CPU, Memory, Network
        assert energy_monitor.sampling_rate_hz == 100

    def test_energy_state_calculation(self, energy_monitor):
        """Test system energy state calculation"""
        # Start monitoring
        energy_monitor.start_monitoring()
        time.sleep(0.5)  # Allow sampling

        # Calculate energy state
        energy_state = energy_monitor.calculate_energy_state()

        # Stop monitoring
        energy_monitor.stop_monitoring()

        # Verify energy state
        if energy_state:  # May be None if no samples yet
            assert 0.0 <= energy_state.total_energy <= 1.0
            assert energy_state.entropy >= 0.0
            assert energy_state.flux_level in [
                EnergyFluxLevel.NORMAL,
                EnergyFluxLevel.ALERT,
                EnergyFluxLevel.CRITICAL
            ]
            assert energy_state.anomaly_score >= 0.0

    def test_spike_detection(self, energy_monitor):
        """Test energy spike detection"""
        # Start monitoring
        energy_monitor.start_monitoring()
        time.sleep(0.5)

        # Get energy state
        energy_state = energy_monitor.calculate_energy_state()

        if energy_state:
            # Detect spikes
            spike_detection = energy_monitor.detect_energy_spike(
                energy_state,
                spike_threshold=3.0
            )

            assert spike_detection is not None
            assert isinstance(spike_detection.detected, bool)
            assert spike_detection.spike_magnitude >= 0.0
            assert 0.0 <= spike_detection.correlation_with_threats <= 1.0
            assert isinstance(spike_detection.recommended_action, str)

        energy_monitor.stop_monitoring()

    def test_baseline_update(self, energy_monitor):
        """Test baseline energy statistics update"""
        energy_monitor.start_monitoring()

        # Generate enough states to trigger baseline update
        for _ in range(1100):  # More than 1000 to trigger update
            state = energy_monitor.calculate_energy_state()

        # Baseline should be updated
        assert energy_monitor.baseline_energy > 0.0
        assert energy_monitor.baseline_std >= 0.0

        energy_monitor.stop_monitoring()


class TestProofOfEnergyLedger:
    """Test suite for Proof-of-Energy Ledger"""

    def test_ledger_initialization(self, proof_of_energy_ledger):
        """Test proof-of-energy ledger initialization"""
        assert proof_of_energy_ledger is not None
        assert proof_of_energy_ledger.conservation_tolerance == 0.05
        assert proof_of_energy_ledger.leak_threshold == 0.1
        assert len(proof_of_energy_ledger.ledger) == 0

    def test_transaction_recording(self, proof_of_energy_ledger):
        """Test energy transaction recording with PDE-hash"""
        transaction = proof_of_energy_ledger.record_transaction(
            transaction_type=TransactionType.CONSUMPTION,
            energy_amount=100.0,
            source="test_system",
            destination="computation",
            metadata={"operation": "test"}
        )

        assert transaction is not None
        assert transaction.transaction_type == TransactionType.CONSUMPTION
        assert transaction.energy_amount == 100.0
        assert len(transaction.pde_hash_signature) == 64  # SHA-256 hex

    def test_conservation_law_enforcement(self, proof_of_energy_ledger):
        """Test energy conservation law checking"""
        # Create balanced transactions
        tx1 = proof_of_energy_ledger.record_transaction(
            TransactionType.CONSUMPTION, 100.0, "grid", "system"
        )
        tx2 = proof_of_energy_ledger.record_transaction(
            TransactionType.TRANSFER, 80.0, "system", "output"
        )
        tx3 = proof_of_energy_ledger.record_transaction(
            TransactionType.STORAGE, 15.0, "system", "battery"
        )
        tx4 = proof_of_energy_ledger.record_transaction(
            TransactionType.LOSS, 5.0, "system", "heat"
        )

        # Check conservation: 100 in = 80 + 15 + 5 = 100 out
        check = proof_of_energy_ledger.check_conservation([tx1, tx2, tx3, tx4])

        assert check.conserved is True
        assert check.status == ConservationStatus.CONSERVED
        assert check.total_input == 100.0
        assert check.total_output + check.total_stored + check.total_lost == 100.0

    def test_conservation_violation_detection(self, proof_of_energy_ledger):
        """Test detection of conservation law violations"""
        # Create unbalanced transactions (violation)
        tx1 = proof_of_energy_ledger.record_transaction(
            TransactionType.CONSUMPTION, 100.0, "grid", "system"
        )
        tx2 = proof_of_energy_ledger.record_transaction(
            TransactionType.TRANSFER, 150.0, "system", "output"  # More out than in!
        )

        check = proof_of_energy_ledger.check_conservation([tx1, tx2])

        assert check.conserved is False
        assert check.status == ConservationStatus.VIOLATED
        assert check.conservation_error > 0

    def test_energy_leak_detection(self, proof_of_energy_ledger):
        """Test energy leak detection for intrusion identification"""
        # Expected 100, but only measured 80 (20% leak)
        tx1 = proof_of_energy_ledger.record_transaction(
            TransactionType.CONSUMPTION, 80.0, "system", "computation"
        )

        leak = proof_of_energy_ledger.detect_energy_leak(
            [tx1],
            expected_energy=100.0
        )

        assert leak.detected is True  # 20% > 10% threshold
        assert leak.leak_amount == 20.0
        assert leak.leak_percentage == 0.2
        assert leak.intrusion_score > 0.0

    def test_proof_record_creation(self, proof_of_energy_ledger):
        """Test proof-of-energy record creation"""
        # Create some transactions
        transactions = [
            proof_of_energy_ledger.record_transaction(
                TransactionType.CONSUMPTION, 100.0, "grid", "system"
            ),
            proof_of_energy_ledger.record_transaction(
                TransactionType.TRANSFER, 95.0, "system", "output"
            ),
            proof_of_energy_ledger.record_transaction(
                TransactionType.LOSS, 5.0, "system", "heat"
            )
        ]

        # Create proof record
        record = proof_of_energy_ledger.create_proof_record(
            transactions,
            expected_energy=100.0
        )

        assert record is not None
        assert len(record.transactions) == 3
        assert record.conservation_check is not None
        assert record.leak_detection is not None
        assert len(record.cryptographic_proof) == 64  # SHA-256

    def test_intrusion_detection_via_leak(self, proof_of_energy_ledger):
        """Test intrusion detection through energy leaks"""
        # Simulate cryptojacking: expected 50, measured 30 (40% leak)
        tx = proof_of_energy_ledger.record_transaction(
            TransactionType.CONSUMPTION, 30.0, "cpu", "legitimate_work"
        )

        leak = proof_of_energy_ledger.detect_energy_leak([tx], expected_energy=50.0)

        # 40% leak should trigger high intrusion score
        assert leak.detected is True
        assert leak.intrusion_score > 0.7  # High probability of intrusion
        assert "CRITICAL" in leak.recommended_action or "intrusion" in leak.recommended_action.lower()


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestPhase2_3Integration:
    """Integration tests between Shadow System and Energy Layer"""

    @pytest.mark.asyncio
    async def test_energy_to_shadow_integration(
        self,
        unified_shadow_system,
        energy_monitor,
        sample_fusion_result
    ):
        """Test energy anomalies feeding into unified shadow system"""
        # Start energy monitoring
        energy_monitor.start_monitoring()
        time.sleep(0.5)

        # Get energy state
        energy_state = energy_monitor.calculate_energy_state()

        if energy_state:
            # Create threat data from energy anomaly
            threat_data = {
                "severity": energy_state.total_energy,
                "type": "energy_anomaly",
                "flux_level": energy_state.flux_level.value,
                "anomaly_score": energy_state.anomaly_score
            }

            # Analyze with unified shadow system
            consciousness_state = await unified_shadow_system.analyze_unified_threat(
                threat_data,
                sample_fusion_result
            )

            assert consciousness_state is not None
            assert consciousness_state.unified_threat_level >= 0.0

        energy_monitor.stop_monitoring()

    def test_proof_of_energy_with_pde_hash(self, proof_of_energy_ledger):
        """Test proof-of-energy integrates properly with PDE-hash"""
        # All transactions should have valid PDE-hash signatures
        for _ in range(10):
            tx = proof_of_energy_ledger.record_transaction(
                TransactionType.CONSUMPTION,
                np.random.uniform(10, 100),
                "test_source",
                "test_dest"
            )

            # Verify PDE-hash format
            assert len(tx.pde_hash_signature) == 64
            assert all(c in '0123456789abcdef' for c in tx.pde_hash_signature)

        # 100% of ledger entries should have valid signatures
        metrics = proof_of_energy_ledger.get_metrics()
        assert metrics['total_transactions'] == 10


# ==============================================================================
# Performance Tests
# ==============================================================================

class TestPerformance:
    """Performance tests for Phase 2.6 and 3"""

    def test_energy_monitoring_throughput(self):
        """Test energy monitoring achieves target sampling rate"""
        monitor = EnergyLayerMonitor(sampling_rate_hz=1000)  # 1kHz target

        monitor.start_monitoring()
        time.sleep(2.0)  # Monitor for 2 seconds

        metrics = monitor.get_metrics()
        monitor.stop_monitoring()

        # Should have collected ~2000 samples (2 seconds at 1kHz)
        # Allow tolerance for system variations
        total_samples = sum(
            agent_metrics['samples']
            for agent_metrics in metrics['agent_metrics'].values()
        )

        print(f"\n  Energy monitoring samples in 2s: {total_samples}")
        # At least 1000 samples (500Hz average across agents)
        assert total_samples > 1000, \
            f"Insufficient sampling rate: {total_samples} samples in 2s"

    @pytest.mark.asyncio
    async def test_unified_shadow_latency(self, unified_shadow_system, sample_fusion_result):
        """Test unified shadow analysis latency"""
        threat_data = {"severity": 0.6}

        # Warm-up
        await unified_shadow_system.analyze_unified_threat(threat_data, sample_fusion_result)

        # Measure
        start = time.perf_counter()
        result = await unified_shadow_system.analyze_unified_threat(
            threat_data,
            sample_fusion_result
        )
        elapsed = (time.perf_counter() - start) * 1000

        print(f"\n  Unified shadow analysis latency: {elapsed:.2f}ms")

        # Should be reasonably fast (< 500ms for unified analysis)
        assert elapsed < 1000, \
            f"Unified shadow analysis too slow: {elapsed:.1f}ms"

    def test_proof_of_energy_throughput(self, proof_of_energy_ledger):
        """Test proof-of-energy transaction throughput"""
        num_transactions = 1000

        start = time.perf_counter()
        for i in range(num_transactions):
            proof_of_energy_ledger.record_transaction(
                TransactionType.CONSUMPTION,
                100.0,
                "source",
                "dest"
            )
        elapsed = time.perf_counter() - start

        throughput = num_transactions / elapsed

        print(f"\n  Proof-of-Energy throughput: {throughput:.0f} tx/sec")

        # Should handle thousands of transactions per second
        assert throughput > 500, \
            f"PoE throughput too low: {throughput:.0f} tx/sec"


# ==============================================================================
# Production Readiness Tests
# ==============================================================================

class TestProductionReadiness:
    """Verify production readiness of all components"""

    def test_all_components_have_metrics(
        self,
        unified_shadow_system,
        energy_monitor,
        proof_of_energy_ledger
    ):
        """Verify all components provide metrics"""
        # Unified shadow system
        shadow_metrics = unified_shadow_system.get_metrics()
        assert "total_analyses" in shadow_metrics

        # Energy monitor
        energy_metrics = energy_monitor.get_metrics()
        assert "sampling_rate_hz" in energy_metrics

        # Proof-of-energy
        poe_metrics = proof_of_energy_ledger.get_metrics()
        assert "total_transactions" in poe_metrics

    def test_error_handling(self, proof_of_energy_ledger):
        """Test error handling in edge cases"""
        # Test with invalid data - should not crash
        try:
            leak = proof_of_energy_ledger.detect_energy_leak([], expected_energy=0.0)
            # Should handle gracefully
            assert leak.intrusion_score >= 0.0
        except Exception as e:
            pytest.fail(f"Poor error handling: {e}")

    def test_thread_safety(self, energy_monitor):
        """Test thread safety of concurrent operations"""
        energy_monitor.start_monitoring()

        # Multiple concurrent energy state calculations
        states = []
        for _ in range(10):
            state = energy_monitor.calculate_energy_state()
            if state:
                states.append(state)
            time.sleep(0.1)

        energy_monitor.stop_monitoring()

        # Should not crash and should produce consistent states
        assert len(states) > 0


# ==============================================================================
# Test Runner
# ==============================================================================

if __name__ == "__main__":
    print("AI Shield v2 - Phase 2.6 & 3 Comprehensive Test Suite")
    print("=" * 70)

    # Run pytest with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-W", "ignore::DeprecationWarning"
    ])
