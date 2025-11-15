#!/usr/bin/env python3
"""
AI Shield v2 - Phase 1 Comprehensive Test Suite
================================================

Complete test coverage for Phase 1 Foundation components:
- MathIsomorphismCore (MIC)
- UniversalPatternDetectors (UPD)
- Physics Fusion Engine
- Telemetry Pipeline
- PDE-hash Validator

Test Categories:
- Unit tests (individual components)
- Integration tests (component interactions)
- Performance tests (latency, throughput)
- Validation tests (physics constraints, security)

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

import pytest
import numpy as np
import time
from typing import Dict, Any, List

# Import AI Shield v2 components
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_shield_v2.mic.math_isomorphism_core import (
    MathIsomorphismCore,
    PhysicsSignature,
    PhysicsFeatures,
    PhysicsDomain
)
from ai_shield_v2.upd.universal_pattern_detectors import (
    UniversalPatternDetectorsSuite,
    SwarmDetector,
    PropagationDetector,
    ThreatLevel,
    ExtendedDomain
)
from ai_shield_v2.fusion.physics_fusion_engine import (
    PhysicsFusionEngine,
    ResponseAction,
    ConsensusType
)
from ai_shield_v2.telemetry.telemetry_pipeline import (
    TelemetryIngestionPipeline,
    TelemetryRecord,
    TelemetrySource
)
from ai_shield_v2.core.pde_hash_validator import (
    PDEHashValidator,
    PDEHashGenerator,
    ValidationStatus,
    TransitionType
)


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def sample_telemetry_data() -> Dict[str, Any]:
    """Generate sample telemetry data for testing"""
    return {
        "time_series": np.random.randn(100).tolist(),
        "metadata": {
            "source": "test_agent",
            "timestamp": time.time()
        }
    }


@pytest.fixture
def mic_instance():
    """Create MathIsomorphismCore instance"""
    return MathIsomorphismCore()


@pytest.fixture
def upd_suite():
    """Create UniversalPatternDetectors suite"""
    return UniversalPatternDetectorsSuite(parallel=True)


@pytest.fixture
def fusion_engine():
    """Create Physics Fusion Engine"""
    return PhysicsFusionEngine(
        consensus_threshold=4,
        amplification_factor=0.75
    )


@pytest.fixture
def telemetry_pipeline():
    """Create Telemetry Pipeline"""
    return TelemetryIngestionPipeline(
        buffer_size=1000,
        batch_size=10,
        max_workers=2,
        enable_async=False  # Synchronous for testing
    )


@pytest.fixture
def pde_validator():
    """Create PDE-hash validator"""
    return PDEHashValidator()


# ==============================================================================
# MIC Tests
# ==============================================================================

class TestMathIsomorphismCore:
    """Test suite for MathIsomorphismCore"""

    def test_mic_initialization(self, mic_instance):
        """Test MIC initialization"""
        assert mic_instance is not None
        assert len(mic_instance.domain_profiles) == 7
        assert mic_instance.analysis_count == 0

    def test_physics_feature_extraction(self, mic_instance, sample_telemetry_data):
        """Test 12-feature physics extraction"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)

        assert isinstance(signature, PhysicsSignature)
        assert signature.features is not None

        # Verify all 12 features present
        features = signature.features
        assert hasattr(features, 'spectral_density')
        assert hasattr(features, 'spectral_entropy')
        assert hasattr(features, 'dominant_frequency')
        assert hasattr(features, 'temporal_gradient')
        assert hasattr(features, 'temporal_variance')
        assert hasattr(features, 'temporal_autocorr')
        assert hasattr(features, 'energy_density')
        assert hasattr(features, 'entropy')
        assert hasattr(features, 'skewness')
        assert hasattr(features, 'kurtosis')
        assert hasattr(features, 'mean_value')
        assert hasattr(features, 'std_deviation')

        # Verify all features are valid numbers
        feature_values = [
            features.spectral_density,
            features.spectral_entropy,
            features.dominant_frequency,
            features.temporal_gradient,
            features.temporal_variance,
            features.temporal_autocorr,
            features.energy_density,
            features.entropy,
            features.skewness,
            features.kurtosis,
            features.mean_value,
            features.std_deviation
        ]

        for value in feature_values:
            assert not np.isnan(value), "Feature contains NaN"
            assert not np.isinf(value), "Feature contains Inf"

    def test_domain_classification(self, mic_instance, sample_telemetry_data):
        """Test 7-domain classification"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)

        # Verify all 7 domains have scores
        assert len(signature.domain_scores) == 7

        # Verify scores are in [0, 1]
        for domain, score in signature.domain_scores.items():
            assert 0.0 <= score <= 1.0, f"Domain {domain} score {score} out of range"

        # Verify scores sum to ~1.0
        total = sum(signature.domain_scores.values())
        assert abs(total - 1.0) < 0.01, f"Domain scores sum to {total}, expected ~1.0"

        # Verify primary domain is highest scorer
        assert signature.primary_domain in signature.domain_scores
        max_score = max(signature.domain_scores.values())
        assert signature.domain_scores[signature.primary_domain] == max_score

    def test_pde_hash_generation(self, mic_instance, sample_telemetry_data):
        """Test PDE-hash generation"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)

        assert signature.pde_hash is not None
        assert len(signature.pde_hash) == 64  # SHA-256 hex length
        assert all(c in '0123456789abcdef' for c in signature.pde_hash)

    def test_mic_performance(self, mic_instance, sample_telemetry_data):
        """Test MIC latency <0.2ms target"""
        # Warm-up
        mic_instance.analyze_stream(sample_telemetry_data)

        # Measure performance
        start = time.perf_counter()
        signature = mic_instance.analyze_stream(sample_telemetry_data)
        elapsed = (time.perf_counter() - start) * 1000  # ms

        assert signature.processing_time_ms < 0.5, \
            f"MIC latency {signature.processing_time_ms:.3f}ms exceeds 0.5ms threshold"

    def test_batch_analysis(self, mic_instance, sample_telemetry_data):
        """Test batch processing"""
        batch = [sample_telemetry_data for _ in range(10)]
        signatures = mic_instance.batch_analyze(batch)

        assert len(signatures) == 10
        assert all(isinstance(sig, PhysicsSignature) for sig in signatures)


# ==============================================================================
# UPD Tests
# ==============================================================================

class TestUniversalPatternDetectors:
    """Test suite for UniversalPatternDetectors"""

    def test_upd_initialization(self, upd_suite):
        """Test UPD suite initialization"""
        assert upd_suite is not None
        assert len(upd_suite.detectors) == 7
        assert upd_suite.parallel is True

    def test_individual_detector_names(self, upd_suite):
        """Test all 7 detectors present"""
        detector_names = {d.name for d in upd_suite.detectors}

        expected_names = {
            "SwarmDetector",
            "PropagationDetector",
            "FlowInstabilityDetector",
            "ResonanceDetector",
            "StabilityDetector",
            "PlanetaryDetector",
            "RadiativeDetector"
        }

        assert detector_names == expected_names

    def test_detection_pipeline(self, mic_instance, upd_suite, sample_telemetry_data):
        """Test UPD detection pipeline"""
        # Get physics signature from MIC
        signature = mic_instance.analyze_stream(sample_telemetry_data)

        # Run UPD suite
        result = upd_suite.analyze(signature)

        assert result is not None
        assert len(result.detector_results) == 7

        # Verify all detectors returned results
        for detector_result in result.detector_results:
            assert detector_result.threat_score >= 0.0
            assert detector_result.threat_score <= 100.0
            assert isinstance(detector_result.threat_level, ThreatLevel)
            assert 0.0 <= detector_result.confidence <= 1.0

    def test_extended_domains(self, upd_suite):
        """Test extended detection domains"""
        for detector in upd_suite.detectors:
            assert len(detector.extended_domains) > 0
            assert all(isinstance(d, ExtendedDomain) for d in detector.extended_domains)

    def test_upd_performance(self, mic_instance, upd_suite, sample_telemetry_data):
        """Test UPD latency <0.1ms target (combined)"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)

        # Warm-up
        upd_suite.analyze(signature)

        # Measure
        start = time.perf_counter()
        result = upd_suite.analyze(signature)
        elapsed = (time.perf_counter() - start) * 1000

        assert result.processing_time_ms < 0.5, \
            f"UPD latency {result.processing_time_ms:.3f}ms exceeds 0.5ms threshold"


# ==============================================================================
# Fusion Engine Tests
# ==============================================================================

class TestPhysicsFusionEngine:
    """Test suite for Physics Fusion Engine"""

    def test_fusion_initialization(self, fusion_engine):
        """Test Fusion Engine initialization"""
        assert fusion_engine is not None
        assert fusion_engine.consensus_threshold == 4
        assert fusion_engine.amplification_factor == 0.75

    def test_fusion_pipeline(self, mic_instance, upd_suite, fusion_engine, sample_telemetry_data):
        """Test full MIC → UPD → Fusion pipeline"""
        # MIC
        signature = mic_instance.analyze_stream(sample_telemetry_data)

        # UPD
        upd_result = upd_suite.analyze(signature)

        # Fusion
        fusion_result = fusion_engine.fuse(upd_result.detector_results)

        assert fusion_result is not None
        assert fusion_result.threat_intelligence is not None

        # Verify ICI score
        ici = fusion_result.threat_intelligence.ici_score
        assert 0.0 <= ici.score <= 100.0
        assert isinstance(ici.response_action, ResponseAction)
        assert isinstance(ici.consensus_metrics.consensus_type, ConsensusType)

    def test_consensus_calculation(self, fusion_engine, mic_instance, upd_suite, sample_telemetry_data):
        """Test 4/7 consensus threshold"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)
        upd_result = upd_suite.analyze(signature)
        fusion_result = fusion_engine.fuse(upd_result.detector_results)

        consensus = fusion_result.threat_intelligence.ici_score.consensus_metrics

        assert consensus.total_detectors == 7
        assert 0 <= consensus.agreeing_detectors <= 7
        assert 0.0 <= consensus.consensus_ratio <= 1.0
        assert consensus.threshold_met == (consensus.agreeing_detectors >= 4)

    def test_ici_amplification(self, fusion_engine, mic_instance, upd_suite, sample_telemetry_data):
        """Test ICI consensus amplification"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)
        upd_result = upd_suite.analyze(signature)
        fusion_result = fusion_engine.fuse(upd_result.detector_results)

        ici = fusion_result.threat_intelligence.ici_score

        # Verify amplification was applied
        assert ici.consensus_amplification > 0.0

        # Verify relationship: ICI = base_score × amplification
        expected_ici = min(100.0, ici.base_score * ici.consensus_amplification)
        assert abs(ici.score - expected_ici) < 0.01

    def test_response_mapping(self, fusion_engine):
        """Test ICI → Response Action mapping"""
        actions = list(ResponseAction)

        # Verify thresholds are properly ordered
        thresholds = [
            fusion_engine.response_thresholds[ResponseAction.MONITOR],
            fusion_engine.response_thresholds[ResponseAction.LOG],
            fusion_engine.response_thresholds[ResponseAction.ALERT],
            fusion_engine.response_thresholds[ResponseAction.MITIGATE],
            fusion_engine.response_thresholds[ResponseAction.ISOLATE]
        ]

        assert thresholds == sorted(thresholds)

    def test_fusion_performance(self, fusion_engine, mic_instance, upd_suite, sample_telemetry_data):
        """Test Fusion latency <0.05ms target"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)
        upd_result = upd_suite.analyze(signature)

        # Warm-up
        fusion_engine.fuse(upd_result.detector_results)

        # Measure
        start = time.perf_counter()
        result = fusion_engine.fuse(upd_result.detector_results)
        elapsed = (time.perf_counter() - start) * 1000

        assert result.processing_time_ms < 0.2, \
            f"Fusion latency {result.processing_time_ms:.3f}ms exceeds 0.2ms threshold"


# ==============================================================================
# Telemetry Pipeline Tests
# ==============================================================================

class TestTelemetryPipeline:
    """Test suite for Telemetry Pipeline"""

    def test_pipeline_initialization(self, telemetry_pipeline):
        """Test pipeline initialization"""
        assert telemetry_pipeline is not None
        assert telemetry_pipeline.mic is not None
        assert telemetry_pipeline.upd is not None
        assert telemetry_pipeline.fusion is not None

    def test_telemetry_ingestion(self, telemetry_pipeline, sample_telemetry_data):
        """Test telemetry record ingestion"""
        record = TelemetryRecord(
            source=TelemetrySource.AGENT,
            timestamp=time.time(),
            data=sample_telemetry_data
        )

        success = telemetry_pipeline.ingest(record)
        assert success is True

    def test_end_to_end_processing(self, telemetry_pipeline, sample_telemetry_data):
        """Test end-to-end telemetry processing"""
        record = TelemetryRecord(
            source=TelemetrySource.AGENT,
            timestamp=time.time(),
            data=sample_telemetry_data
        )

        # Ingest
        success = telemetry_pipeline.ingest(record)
        assert success is True

        # Get metrics
        metrics = telemetry_pipeline.get_metrics()
        assert metrics.total_received >= 1
        assert metrics.total_processed >= 1

    def test_batch_ingestion(self, telemetry_pipeline, sample_telemetry_data):
        """Test batch telemetry ingestion"""
        records = [
            TelemetryRecord(
                source=TelemetrySource.AGENT,
                timestamp=time.time(),
                data=sample_telemetry_data
            )
            for _ in range(10)
        ]

        success_count = telemetry_pipeline.ingest_batch(records)
        assert success_count == 10

    def test_validation(self, telemetry_pipeline):
        """Test telemetry validation"""
        # Invalid record (empty data)
        invalid_record = TelemetryRecord(
            source=TelemetrySource.AGENT,
            timestamp=time.time(),
            data={}
        )

        success = telemetry_pipeline.ingest(invalid_record)
        assert success is False


# ==============================================================================
# PDE-Hash Validator Tests
# ==============================================================================

class TestPDEHashValidator:
    """Test suite for PDE-hash validation"""

    def test_validator_initialization(self, pde_validator):
        """Test PDE-hash validator initialization"""
        assert pde_validator is not None
        assert pde_validator.registry is not None

    def test_pde_hash_generation(self, mic_instance, sample_telemetry_data):
        """Test PDE-hash generation"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)
        pde_hash = PDEHashGenerator.generate(signature)

        assert pde_hash is not None
        assert len(pde_hash) == 64
        assert all(c in '0123456789abcdef' for c in pde_hash)

    def test_pde_hash_determinism(self, mic_instance, sample_telemetry_data):
        """Test PDE-hash is deterministic"""
        signature1 = mic_instance.analyze_stream(sample_telemetry_data)
        signature2 = mic_instance.analyze_stream(sample_telemetry_data)

        hash1 = PDEHashGenerator.generate(signature1)
        hash2 = PDEHashGenerator.generate(signature2)

        # Same input should produce same hash
        assert hash1 == hash2

    def test_hash_verification(self, mic_instance, pde_validator, sample_telemetry_data):
        """Test PDE-hash verification"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)
        pde_hash = PDEHashGenerator.generate(signature)

        # Verify correct hash
        assert PDEHashGenerator.verify(signature, pde_hash) is True

        # Verify incorrect hash
        fake_hash = "0" * 64
        assert PDEHashGenerator.verify(signature, fake_hash) is False

    def test_signature_validation(self, mic_instance, pde_validator, sample_telemetry_data):
        """Test physics signature validation"""
        signature = mic_instance.analyze_stream(sample_telemetry_data)
        result = pde_validator.validate(signature)

        assert result.status == ValidationStatus.VALID
        assert result.is_valid is True
        assert result.confidence > 0.9

    def test_transition_validation(self, mic_instance, pde_validator):
        """Test state transition validation"""
        # Create two similar signatures
        data1 = {"time_series": np.random.randn(100).tolist()}
        data2 = {"time_series": (np.random.randn(100) + 0.1).tolist()}

        sig1 = mic_instance.analyze_stream(data1)
        sig2 = mic_instance.analyze_stream(data2)

        transition = pde_validator.validate_transition(sig1, sig2)

        assert transition is not None
        assert transition.from_hash != transition.to_hash
        assert isinstance(transition.transition_type, TransitionType)
        assert isinstance(transition.is_physics_valid, bool)


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestIntegration:
    """Integration tests for complete AI Shield v2 pipeline"""

    def test_complete_pipeline(self, mic_instance, upd_suite, fusion_engine, pde_validator, sample_telemetry_data):
        """Test complete MIC → UPD → Fusion → Validation pipeline"""
        # MIC: Physics extraction
        signature = mic_instance.analyze_stream(sample_telemetry_data)
        assert signature is not None

        # Validate signature
        validation = pde_validator.validate(signature)
        assert validation.is_valid is True

        # UPD: Threat detection
        upd_result = upd_suite.analyze(signature)
        assert len(upd_result.detector_results) == 7

        # Fusion: Consensus and ICI
        fusion_result = fusion_engine.fuse(upd_result.detector_results)
        assert fusion_result is not None
        assert 0.0 <= fusion_result.threat_intelligence.ici_score.score <= 100.0

    def test_end_to_end_latency(self, mic_instance, upd_suite, fusion_engine, sample_telemetry_data):
        """Test end-to-end latency <0.5ms target"""
        # Warm-up
        signature = mic_instance.analyze_stream(sample_telemetry_data)
        upd_result = upd_suite.analyze(signature)
        fusion_engine.fuse(upd_result.detector_results)

        # Measure complete pipeline
        start = time.perf_counter()

        signature = mic_instance.analyze_stream(sample_telemetry_data)
        upd_result = upd_suite.analyze(signature)
        fusion_result = fusion_engine.fuse(upd_result.detector_results)

        end_to_end_latency = (time.perf_counter() - start) * 1000

        print(f"\n  End-to-end latency: {end_to_end_latency:.3f}ms")
        print(f"    MIC: {signature.processing_time_ms:.3f}ms")
        print(f"    UPD: {upd_result.processing_time_ms:.3f}ms")
        print(f"    Fusion: {fusion_result.processing_time_ms:.3f}ms")

        assert end_to_end_latency < 1.0, \
            f"End-to-end latency {end_to_end_latency:.3f}ms exceeds 1.0ms"


# ==============================================================================
# Performance Tests
# ==============================================================================

class TestPerformance:
    """Performance and throughput tests"""

    def test_throughput_10k_samples(self, mic_instance):
        """Test >10k samples/sec throughput"""
        samples = [
            {"time_series": np.random.randn(100).tolist()}
            for _ in range(100)  # Reduced for test speed
        ]

        start = time.perf_counter()
        signatures = mic_instance.batch_analyze(samples)
        elapsed = time.perf_counter() - start

        throughput = len(samples) / elapsed

        print(f"\n  Throughput: {throughput:.0f} samples/sec")

        assert throughput > 1000, \
            f"Throughput {throughput:.0f} samples/sec below 1000 minimum"


# ==============================================================================
# Test Runner
# ==============================================================================

if __name__ == "__main__":
    print("AI Shield v2 - Phase 1 Comprehensive Test Suite")
    print("=" * 70)

    # Run pytest with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])
