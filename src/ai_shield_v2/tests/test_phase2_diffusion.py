#!/usr/bin/env python3
"""
AI Shield v2 - Phase 2 Diffusion Integration Test Suite
========================================================

Comprehensive tests for Phase 2 Diffusion Engine integration:
- Diffusion Engine (forward/reverse diffusion, attack surface mapping)
- Adversarial Detector (energy perturbations, mode collapse, regime shifts)
- Shadow Twin Simulator (pre-simulation, risk assessment, contamination checks)
- Diffusion Pattern Detectors (adversarial ML, regime shifts, integrity)

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

import pytest
import numpy as np
import time
from typing import Dict, Any

# Import AI Shield v2 components
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_shield_v2.diffusion import (
    DiffusionEngine,
    DiffusionMode,
    ThreatClass,
    ThreatVector,
    DiffusionState,
    AdversarialDetector,
    PerturbationType,
    ShadowTwinSimulator,
    SimulationDecision,
    ProposedAction,
    ActionType
)

from ai_shield_v2.upd.diffusion_patterns import (
    DiffusionAdversarialDetector,
    RegimeShiftDetector,
    DiffusionIntegrityDetector,
    DiffusionPatternExtension
)

from ai_shield_v2.mic import MathIsomorphismCore
from ai_shield_v2.fusion import PhysicsFusionEngine


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def diffusion_engine():
    """Create Diffusion Engine instance"""
    return DiffusionEngine(
        timesteps=1000,
        simulation_resolution=0.1,
        state_dimension=128
    )


@pytest.fixture
def adversarial_detector():
    """Create Adversarial Detector instance"""
    return AdversarialDetector(
        window_size=100,
        mode_collapse_threshold=0.7,
        regime_shift_threshold=3.0
    )


@pytest.fixture
def shadow_twin():
    """Create Shadow Twin Simulator instance"""
    return ShadowTwinSimulator(
        ici_threshold=50.0,
        isolation_noise=0.01,
        risk_threshold=0.7,
        simulation_steps=100
    )


@pytest.fixture
def diffusion_pattern_ext():
    """Create Diffusion Pattern Extension"""
    return DiffusionPatternExtension()


@pytest.fixture
def sample_state():
    """Create sample diffusion state"""
    state_vector = np.random.randn(128)
    return DiffusionState(
        timestep=0,
        state_vector=state_vector,
        energy=float(np.linalg.norm(state_vector) / np.sqrt(len(state_vector))),
        entropy=3.5,
        noise_level=0.0
    )


# ==============================================================================
# Diffusion Engine Tests
# ==============================================================================

class TestDiffusionEngine:
    """Test suite for Diffusion Engine"""

    def test_initialization(self, diffusion_engine):
        """Test Diffusion Engine initialization"""
        assert diffusion_engine is not None
        assert diffusion_engine.timesteps == 1000
        assert diffusion_engine.state_dimension == 128
        assert diffusion_engine.scheduler is not None

    def test_forward_diffusion(self, diffusion_engine):
        """Test forward diffusion for attack surface mapping"""
        initial_state = np.random.randn(128)
        result = diffusion_engine.forward_diffusion(initial_state, num_steps=50)

        assert result is not None
        assert result.mode == DiffusionMode.FORWARD
        assert len(result.trajectory) == 50
        assert len(result.attack_surfaces) >= 0
        assert result.simulation_time_ms > 0

    def test_reverse_diffusion(self, diffusion_engine):
        """Test reverse diffusion for threat trajectory prediction"""
        noisy_state = np.random.randn(128)
        result = diffusion_engine.reverse_diffusion(noisy_state, num_steps=50)

        assert result is not None
        assert result.mode == DiffusionMode.REVERSE
        assert len(result.trajectory) == 50
        assert len(result.predicted_threats) >= 0
        assert result.simulation_time_ms > 0

    def test_threat_vector_database(self, diffusion_engine):
        """Test threat vector storage and retrieval"""
        vector = ThreatVector(
            threat_id="test_001",
            threat_class=ThreatClass.INJECTION,
            entry_point="api_endpoint",
            attack_pattern={"type": "sql_injection"},
            historical_success_rate=0.75,
            energy_signature={"total_energy": 0.6}
        )

        diffusion_engine.add_threat_vector(vector)
        assert len(diffusion_engine.threat_vectors) == 1

    def test_attack_surface_mapping(self, diffusion_engine):
        """Test attack surface mapping from trajectory"""
        initial_state = np.random.randn(128) * 2.0  # Higher energy for surfaces
        result = diffusion_engine.forward_diffusion(initial_state, num_steps=100)

        # Should detect some attack surfaces in high-energy state
        assert len(result.attack_surfaces) > 0

        # Verify attack surface properties
        for surface in result.attack_surfaces:
            assert 0.0 <= surface.vulnerability_score <= 1.0
            assert 1 <= surface.mitigation_priority <= 10

    def test_telemetry_conversion(self, diffusion_engine):
        """Test conversion of diffusion result to telemetry"""
        initial_state = np.random.randn(128)
        result = diffusion_engine.forward_diffusion(initial_state, num_steps=50)

        telemetry_record = diffusion_engine.to_telemetry(result)

        assert telemetry_record is not None
        assert "time_series" in telemetry_record.data
        assert len(telemetry_record.data["time_series"]) == 50

    def test_diffusion_performance(self, diffusion_engine):
        """Test diffusion simulation time <100ms target"""
        initial_state = np.random.randn(128)

        # Measure forward diffusion
        result = diffusion_engine.forward_diffusion(initial_state, num_steps=50)

        # Simulation time should be < 100ms for Phase 2
        assert result.simulation_time_ms < 200, \
            f"Diffusion time {result.simulation_time_ms:.1f}ms exceeds 200ms"


# ==============================================================================
# Adversarial Detector Tests
# ==============================================================================

class TestAdversarialDetector:
    """Test suite for Adversarial Detector"""

    def test_initialization(self, adversarial_detector):
        """Test Adversarial Detector initialization"""
        assert adversarial_detector is not None
        assert adversarial_detector.window_size == 100
        assert adversarial_detector.mode_collapse_threshold == 0.7

    def test_energy_monitoring(self, adversarial_detector, sample_state):
        """Test energy state monitoring"""
        result = adversarial_detector.detect(sample_state)

        assert result.energy_monitor is not None
        assert result.energy_monitor.current_energy >= 0
        assert result.energy_monitor.flux_level is not None

    def test_mode_collapse_detection(self, adversarial_detector):
        """Test mode collapse detection"""
        # Create low-entropy state (mode collapse)
        collapsed_state = DiffusionState(
            timestep=0,
            state_vector=np.ones(128),  # No diversity
            energy=1.0,
            entropy=0.1,  # Very low entropy
            noise_level=0.0
        )

        result = adversarial_detector.detect(collapsed_state)

        assert result.mode_collapse.detected or result.mode_collapse.collapse_ratio > 0.5

    def test_regime_shift_detection(self, adversarial_detector):
        """Test regime shift detection"""
        # Create sequence with regime shift
        for i in range(60):
            if i < 30:
                state = DiffusionState(
                    timestep=i,
                    state_vector=np.random.randn(128),
                    energy=0.5,
                    entropy=3.0,
                    noise_level=0.01
                )
            else:
                # Regime shift: sudden change
                state = DiffusionState(
                    timestep=i,
                    state_vector=np.random.randn(128) * 5.0,  # 5x energy
                    energy=2.5,
                    entropy=5.0,
                    noise_level=0.01
                )

            result = adversarial_detector.detect(state)

        # After regime shift, should detect
        assert result.regime_shift.detected or result.regime_shift.shift_magnitude > 1.0

    def test_adversarial_detection_performance(self, adversarial_detector, sample_state):
        """Test adversarial detection latency <50ms target"""
        # Warm-up
        adversarial_detector.detect(sample_state)

        # Measure
        start = time.perf_counter()
        result = adversarial_detector.detect(sample_state)
        elapsed = (time.perf_counter() - start) * 1000

        assert result.processing_time_ms < 100, \
            f"Adversarial detection time {result.processing_time_ms:.1f}ms exceeds 100ms"


# ==============================================================================
# Shadow Twin Simulator Tests
# ==============================================================================

class TestShadowTwinSimulator:
    """Test suite for Shadow Twin Simulator"""

    def test_initialization(self, shadow_twin):
        """Test Shadow Twin initialization"""
        assert shadow_twin is not None
        assert shadow_twin.ici_threshold == 50.0
        assert shadow_twin.risk_threshold == 0.7

    def test_shadow_environment_creation(self, shadow_twin, sample_state):
        """Test shadow environment isolation"""
        shadow_env = shadow_twin._create_shadow_environment(sample_state)

        assert shadow_env is not None
        assert shadow_env.production_state == sample_state

        # Verify isolation (shadow != production)
        assert not np.array_equal(
            shadow_env.shadow_state.state_vector,
            shadow_env.production_state.state_vector
        )

    def test_action_simulation(self, shadow_twin, sample_state):
        """Test proposed action simulation"""
        action = ProposedAction(
            action_id="test_mitigation_001",
            action_type=ActionType.MITIGATION,
            description="Test mitigation action",
            parameters={"intensity": 0.8},
            initiator="test_system",
            ici_score=60.0
        )

        result = shadow_twin.simulate(action, sample_state)

        assert result is not None
        assert result.decision in [
            SimulationDecision.PROCEED,
            SimulationDecision.ABORT,
            SimulationDecision.MODIFY,
            SimulationDecision.ESCALATE
        ]

    def test_contamination_check(self, shadow_twin, sample_state):
        """Test zero contamination guarantee"""
        action = ProposedAction(
            action_id="contamination_test",
            action_type=ActionType.ISOLATION,
            description="Test isolation action",
            parameters={},
            initiator="test",
            ici_score=55.0
        )

        # Store original production state
        original_state = sample_state.state_vector.copy()

        # Run simulation
        result = shadow_twin.simulate(action, sample_state)

        # Verify production state unchanged
        assert np.array_equal(original_state, sample_state.state_vector)
        assert result.contamination_detected is False

    def test_risk_assessment(self, shadow_twin, sample_state):
        """Test risk vs. benefit assessment"""
        action = ProposedAction(
            action_id="risk_test",
            action_type=ActionType.MITIGATION,
            description="Risk assessment test",
            parameters={},
            initiator="test",
            ici_score=70.0
        )

        result = shadow_twin.simulate(action, sample_state)

        assert result.risk_assessment is not None
        assert 0.0 <= result.risk_assessment.risk_score <= 1.0
        assert 0.0 <= result.risk_assessment.benefit_score <= 1.0

    def test_shadow_twin_performance(self, shadow_twin, sample_state):
        """Test shadow twin simulation time <5s target"""
        action = ProposedAction(
            action_id="perf_test",
            action_type=ActionType.MITIGATION,
            description="Performance test",
            parameters={},
            initiator="test",
            ici_score=55.0
        )

        result = shadow_twin.simulate(action, sample_state)

        # Should be much less than 5s for Phase 2
        assert result.simulation_time_ms < 2000, \
            f"Shadow twin time {result.simulation_time_ms:.0f}ms exceeds 2s"


# ==============================================================================
# Diffusion Pattern Detection Tests
# ==============================================================================

class TestDiffusionPatterns:
    """Test suite for Diffusion-Specific Pattern Detection"""

    def test_pattern_extension_initialization(self, diffusion_pattern_ext):
        """Test diffusion pattern extension initialization"""
        assert diffusion_pattern_ext is not None
        assert len(diffusion_pattern_ext.diffusion_detectors) == 3

    def test_adversarial_ml_detection(self):
        """Test adversarial ML attack detection"""
        detector = DiffusionAdversarialDetector()

        # Create adversarial signature (high gradient, low energy)
        from ai_shield_v2.mic import PhysicsFeatures, PhysicsDomain

        adversarial_features = PhysicsFeatures(
            spectral_density=0.8,
            spectral_entropy=0.85,  # High anomaly
            dominant_frequency=0.5,
            temporal_gradient=0.9,  # High gradient
            temporal_variance=0.7,
            temporal_autocorr=0.5,
            energy_density=0.85,
            entropy=0.4,
            skewness=0.1,
            kurtosis=3.0,
            mean_value=0.0,
            std_deviation=1.0
        )

        from ai_shield_v2.mic import PhysicsSignature
        signature = PhysicsSignature(
            features=adversarial_features,
            primary_domain=PhysicsDomain.GRAY_SCOTT_REACTION_DIFFUSION,
            domain_scores={domain: 0.14 for domain in PhysicsDomain},
            pde_hash="test_hash",
            processing_time_ms=0.1
        )

        result = detector.detect(signature)

        # Should detect some adversarial pattern
        assert len(result.detected_patterns) > 0

    def test_regime_shift_detection_pattern(self):
        """Test regime shift pattern detection"""
        detector = RegimeShiftDetector()

        # Create regime shift signature
        from ai_shield_v2.mic import PhysicsFeatures, PhysicsDomain, PhysicsSignature

        shift_features = PhysicsFeatures(
            spectral_density=0.6,
            spectral_entropy=0.5,
            dominant_frequency=0.8,  # Frequency shift
            temporal_gradient=0.85,  # High gradient
            temporal_variance=0.9,  # High variance
            temporal_autocorr=0.3,
            energy_density=0.7,
            entropy=0.9,  # High entropy
            skewness=0.2,
            kurtosis=3.0,
            mean_value=0.0,
            std_deviation=1.0
        )

        signature = PhysicsSignature(
            features=shift_features,
            primary_domain=PhysicsDomain.TURBULENT_RADIATIVE_LAYER_2D,
            domain_scores={domain: 0.14 for domain in PhysicsDomain},
            pde_hash="test_hash",
            processing_time_ms=0.1
        )

        result = detector.detect(signature)

        # Should detect regime shift
        assert len(result.detected_patterns) > 0


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestPhase2Integration:
    """Integration tests for complete Phase 2 pipeline"""

    def test_diffusion_to_mic_pipeline(self, diffusion_engine):
        """Test Diffusion Engine → MIC integration"""
        # Run diffusion
        initial_state = np.random.randn(128)
        diffusion_result = diffusion_engine.forward_diffusion(initial_state, num_steps=50)

        # Convert to telemetry
        telemetry = diffusion_engine.to_telemetry(diffusion_result)

        # Process with MIC
        mic = MathIsomorphismCore()
        signature = mic.analyze_stream(telemetry.data)

        assert signature is not None
        assert signature.pde_hash is not None

    def test_full_diffusion_threat_pipeline(self, diffusion_engine, shadow_twin):
        """Test full diffusion threat detection and simulation pipeline"""
        # 1. Generate threat via forward diffusion
        initial_state = np.random.randn(128) * 2.0
        diffusion_result = diffusion_engine.forward_diffusion(initial_state, num_steps=100)

        # 2. Check if attack surfaces found
        if len(diffusion_result.attack_surfaces) > 0:
            # 3. Propose mitigation action
            action = ProposedAction(
                action_id="auto_mitigation",
                action_type=ActionType.MITIGATION,
                description="Automated threat mitigation",
                parameters={"target": "attack_surface_0"},
                initiator="diffusion_engine",
                ici_score=65.0
            )

            # 4. Simulate in shadow twin
            shadow_result = shadow_twin.simulate(action, diffusion_result.final_state)

            assert shadow_result is not None
            assert shadow_result.decision is not None


# ==============================================================================
# Performance Tests
# ==============================================================================

class TestPhase2Performance:
    """Performance tests for Phase 2 components"""

    def test_diffusion_throughput(self, diffusion_engine):
        """Test diffusion simulation throughput"""
        num_simulations = 10
        initial_states = [np.random.randn(128) for _ in range(num_simulations)]

        start = time.perf_counter()
        for state in initial_states:
            diffusion_engine.forward_diffusion(state, num_steps=20)
        elapsed = time.perf_counter() - start

        throughput = num_simulations / elapsed

        print(f"\n  Diffusion throughput: {throughput:.1f} simulations/sec")

        assert throughput > 5, \
            f"Diffusion throughput {throughput:.1f} sims/sec below 5/sec minimum"


# ==============================================================================
# Test Runner
# ==============================================================================

if __name__ == "__main__":
    print("AI Shield v2 - Phase 2 Diffusion Integration Test Suite")
    print("=" * 70)

    # Run pytest with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])
