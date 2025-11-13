"""
Phase 5 EIL Integration Test

Tests the complete Energy Intelligence Layer end-to-end:
1. RegimeDetector + MicroAdapt parallel ensemble
2. EIL decision fusion
3. Regime detection → ACE inference pipeline
4. Proof validation → PFT minting
5. Market Engine pricing
6. Feedback Trainer online learning

This validates Phase 5 EIL convergence with all components working together.
"""

import pytest
import numpy as np
import sys
import os
from pathlib import Path

# Add Thermodynasty to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from phase5.core.energy_intelligence_layer import EnergyIntelligenceLayer
from phase5.core.proof_validator import ProofValidator, ProofRecord
from phase5.core.market_engine import MarketEngine
from phase5.core.feedback_trainer import FeedbackTrainer


class TestPhase5EILIntegration:
    """Integration tests for Phase 5 Energy Intelligence Layer"""

    @pytest.fixture
    def eil(self):
        """Initialize EIL with test configuration"""
        # Note: In production, this would use actual model checkpoint
        eil = EnergyIntelligenceLayer(
            regime_detector_checkpoint=None,  # Will use default initialization
            microadapt_config={
                'max_units': 50,
                'initial_units': 5,
                'top_k': 3,
                'hierarchy_levels': 3,
                'window_sizes': [60, 600, 3600]
            }
        )
        return eil

    @pytest.fixture
    def proof_validator(self):
        """Initialize Proof Validator"""
        return ProofValidator(
            energy_tolerance=0.01,
            entropy_threshold=0.90,
            spectral_threshold=0.85
        )

    @pytest.fixture
    def market_engine(self):
        """Initialize Market Engine"""
        return MarketEngine(
            initial_ceu_supply=1000000.0,
            initial_pft_supply=100000.0
        )

    @pytest.fixture
    def feedback_trainer(self):
        """Initialize Feedback Trainer"""
        return FeedbackTrainer(
            learning_rate=0.01,
            adaptation_threshold=0.7,
            calibration_window=20
        )

    def test_01_eil_regime_detection(self, eil):
        """Test EIL regime detection with parallel ensemble"""
        # Create test energy map (stable regime)
        energy_map = np.random.randn(64, 64) * 0.1 + 1.0

        # Process through EIL
        decision = eil.process(
            energy_map=energy_map,
            domain="test_fluid_dynamics",
            cluster="cluster-1",
            node="node-1"
        )

        # Validate decision structure
        assert decision.regime is not None
        assert decision.confidence > 0.0
        assert isinstance(decision.approved, bool)
        assert decision.forecast_mean is not None
        assert decision.entropy_rate >= 0.0
        assert decision.temperature > 0.0
        assert decision.recommended_action in ['proceed', 'defer', 'reject', 'investigate']

        print(f"✅ Regime detected: {decision.regime} (confidence: {decision.confidence:.2f})")
        print(f"   Approved: {decision.approved}, Action: {decision.recommended_action}")

    def test_02_stable_regime_pipeline(self, eil, proof_validator, market_engine):
        """Test complete pipeline for stable regime"""
        # Step 1: Create stable energy map
        energy_map = np.random.randn(64, 64) * 0.05 + 1.0

        # Step 2: EIL regime detection
        decision = eil.process(
            energy_map=energy_map,
            domain="molecular_dynamics",
            cluster="cluster-1",
            node="node-1"
        )

        assert "stable" in decision.regime or decision.approved == True

        # Step 3: Calculate CEU cost
        ceu_cost = market_engine.calculate_ceu_cost(
            energy_consumption=1.0,
            regime=decision.regime,
            regime_approved=decision.approved,
            num_steps=10
        )

        assert ceu_cost.total_ceu > 0
        print(f"✅ CEU cost: {ceu_cost.total_ceu:.2f} CEU (${ceu_cost.total_usd:.4f})")

        # Step 4: Simulate ACE inference (predicted energy map)
        predicted_energy_map = energy_map + np.random.randn(64, 64) * 0.02

        # Step 5: Create proof
        proof = proof_validator.create_proof(
            domain="molecular_dynamics",
            predicted_energy_map=predicted_energy_map,
            regime=decision.regime,
            regime_approved=decision.approved
        )

        # Step 6: Validate proof against ground truth
        observed_energy_map = energy_map  # Ground truth
        validation_result = proof_validator.validate(proof, observed_energy_map)

        print(f"✅ Proof validation: {validation_result.passed}")
        print(f"   Energy: {validation_result.validation_details['tri_check']['energy']['passed']}")
        print(f"   Entropy: {validation_result.validation_details['tri_check']['entropy']['passed']}")
        print(f"   Spectral: {validation_result.validation_details['tri_check']['spectral']['passed']}")

        # Step 7: If validation passed, calculate PFT reward
        if validation_result.passed:
            avg_quality = (
                proof.energy_fidelity +
                proof.entropy_coherence +
                proof.spectral_similarity
            ) / 3.0

            pft_reward = market_engine.calculate_pft_reward(
                proof_quality=avg_quality,
                regime=decision.regime,
                regime_approved=decision.approved,
                regime_confidence=decision.confidence
            )

            print(f"✅ PFT reward: {pft_reward.total_pft:.2f} PFT (${pft_reward.total_usd:.2f})")
            print(f"   Quality bonus: {pft_reward.quality_bonus:.2f}x")
            print(f"   Regime bonus: {pft_reward.regime_bonus:.2f}x")

            assert pft_reward.total_pft > 0

    def test_03_chaotic_regime_rejection(self, eil, market_engine):
        """Test pipeline behavior for chaotic regime"""
        # Create chaotic energy map (high variance)
        energy_map = np.random.randn(64, 64) * 2.0 + 5.0

        # EIL regime detection
        decision = eil.process(
            energy_map=energy_map,
            domain="turbulent_flow",
            cluster="cluster-1",
            node="node-1"
        )

        # For chaotic regimes, expect higher CEU cost or rejection
        ceu_cost = market_engine.calculate_ceu_cost(
            energy_consumption=1.0,
            regime=decision.regime,
            regime_approved=decision.approved,
            num_steps=10
        )

        # Chaotic or unapproved regimes should have higher multiplier
        if not decision.approved or "chaotic" in decision.regime:
            assert ceu_cost.regime_multiplier >= 1.2

        print(f"✅ Chaotic regime detected: {decision.regime}")
        print(f"   CEU cost multiplier: {ceu_cost.regime_multiplier:.2f}x")
        print(f"   Recommended action: {decision.recommended_action}")

    def test_04_regime_gating_skip_inference(self, eil):
        """Test that regime gating skips ACE inference for unapproved regimes"""
        # Create energy map that should result in unapproved regime
        energy_map = np.random.randn(64, 64) * 3.0 + 10.0

        decision = eil.process(
            energy_map=energy_map,
            domain="unstable_system",
            cluster="cluster-1",
            node="node-1"
        )

        # Check if regime gating is working
        if not decision.approved:
            assert decision.recommended_action in ['defer', 'reject', 'investigate']
            print(f"✅ Regime gating: Inference skipped for {decision.regime}")
            print(f"   Risk level: {decision.risk_level}")

    def test_05_feedback_trainer_learning(self, feedback_trainer, proof_validator):
        """Test online learning from validation results"""
        # Simulate 20 validation events
        for i in range(20):
            # Create mock proof
            predicted = np.random.randn(64, 64) * 0.1 + 1.0
            observed = predicted + np.random.randn(64, 64) * 0.05

            proof = ProofRecord(
                proof_id=f"test-{i}",
                domain="test_domain",
                timestamp=float(i),
                predicted_energy_map=predicted,
                predicted_hash="abc",
                regime="stable_confirmed"
            )

            proof.energy_fidelity = 0.95 + np.random.randn() * 0.02
            proof.entropy_coherence = 0.92 + np.random.randn() * 0.02
            proof.spectral_similarity = 0.88 + np.random.randn() * 0.02
            proof.overall_passed = True

            from phase5.core.proof_validator import ProofValidationResult

            validation_result = ProofValidationResult(
                passed=True,
                proof_record=proof,
                validation_details={'overall': {'passed': True}},
                recommended_action="mint"
            )

            # Process feedback
            forecast_values = np.random.randn(60) * 0.1
            actual_values = forecast_values + np.random.randn(60) * 0.05

            feedback = feedback_trainer.process_validation_result(
                validation_result=validation_result,
                predicted_regime="stable_confirmed",
                regime_confidence=0.85,
                forecast_values=forecast_values,
                actual_values=actual_values,
                actual_regime="stable_confirmed"
            )

        # Check learning metrics
        stats = feedback_trainer.get_stats()

        assert stats['metrics']['total_events'] == 20
        assert stats['metrics']['regime_accuracy'] > 0.0
        print(f"✅ Feedback trainer: {stats['metrics']['total_events']} events processed")
        print(f"   Regime accuracy: {stats['metrics']['regime_accuracy']:.1%}")
        print(f"   Avg proof quality: {stats['metrics']['avg_proof_quality']:.1%}")
        print(f"   Adaptations: {stats['adaptations']}")

    def test_06_market_engine_amm_swap(self, market_engine):
        """Test AMM bonding curve swaps"""
        # Swap CEU for PFT
        pft_out, new_rate = market_engine.swap_ceu_for_pft(100.0)

        assert pft_out > 0
        assert new_rate > 0
        print(f"✅ AMM swap: 100 CEU → {pft_out:.4f} PFT")
        print(f"   New exchange rate: {new_rate:.6f}")

        # Swap PFT for CEU
        ceu_out, new_rate2 = market_engine.swap_pft_for_ceu(1.0)

        assert ceu_out > 0
        print(f"✅ AMM swap: 1 PFT → {ceu_out:.2f} CEU")

    def test_07_end_to_end_workflow(self, eil, proof_validator, market_engine, feedback_trainer):
        """Test complete end-to-end workflow"""
        print("\n" + "=" * 70)
        print("PHASE 5 EIL - END-TO-END WORKFLOW TEST")
        print("=" * 70)

        # Step 1: Energy map arrives
        energy_map = np.random.randn(64, 64) * 0.1 + 1.0
        print("\n[Step 1] Energy map received: shape", energy_map.shape)

        # Step 2: EIL regime detection
        decision = eil.process(
            energy_map=energy_map,
            domain="production_system",
            cluster="cluster-1",
            node="node-1"
        )
        print(f"[Step 2] Regime detected: {decision.regime}")
        print(f"         Confidence: {decision.confidence:.2%}, Approved: {decision.approved}")

        # Step 3: Calculate cost
        ceu_cost = market_engine.calculate_ceu_cost(
            energy_consumption=1.0,
            regime=decision.regime,
            regime_approved=decision.approved,
            num_steps=10
        )
        print(f"[Step 3] CEU cost: {ceu_cost.total_ceu:.2f} CEU (${ceu_cost.total_usd:.4f})")

        # Step 4: If approved, run ACE inference (simulated)
        if decision.approved:
            predicted_energy_map = energy_map + np.random.randn(64, 64) * 0.02
            print(f"[Step 4] ACE inference completed")

            # Step 5: Create and validate proof
            proof = proof_validator.create_proof(
                domain="production_system",
                predicted_energy_map=predicted_energy_map,
                regime=decision.regime,
                regime_approved=decision.approved
            )

            validation_result = proof_validator.validate(proof, energy_map)
            print(f"[Step 5] Proof validation: {validation_result.passed}")

            # Step 6: If validated, calculate PFT reward
            if validation_result.passed:
                avg_quality = (
                    proof.energy_fidelity +
                    proof.entropy_coherence +
                    proof.spectral_similarity
                ) / 3.0

                pft_reward = market_engine.calculate_pft_reward(
                    proof_quality=avg_quality,
                    regime=decision.regime,
                    regime_approved=decision.approved,
                    regime_confidence=decision.confidence
                )
                print(f"[Step 6] PFT reward: {pft_reward.total_pft:.2f} PFT")

                # Step 7: Learn from feedback
                forecast_values = np.random.randn(60) * 0.1
                actual_values = forecast_values + np.random.randn(60) * 0.05

                feedback = feedback_trainer.process_validation_result(
                    validation_result=validation_result,
                    predicted_regime=decision.regime,
                    regime_confidence=decision.confidence,
                    forecast_values=forecast_values,
                    actual_values=actual_values
                )
                print(f"[Step 7] Feedback processed: {feedback.adaptations_applied}")

        else:
            print(f"[Step 4] ACE inference skipped (regime not approved)")

        print("\n" + "=" * 70)
        print("✅ END-TO-END WORKFLOW COMPLETE")
        print("=" * 70)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
