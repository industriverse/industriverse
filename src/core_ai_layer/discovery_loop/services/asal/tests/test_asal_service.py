"""
Unit tests for ASAL (Autonomous Scoring and Learning) Service

Tests cover:
1. Service initialization and configuration
2. Consciousness scoring across all dimensions
3. Hypothesis evaluation
4. Meta-learning and history tracking
5. Recommendation generation
6. Edge cases and error handling

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import numpy as np
from datetime import datetime
import asyncio

from ..asal_service import (
    ASALService,
    ASALConfig,
    ConsciousnessScore,
    ConsciousnessDimension,
    HypothesisEvaluation
)


class TestASALService:
    """Test suite for ASAL service."""
    
    @pytest.fixture
    def asal_service(self):
        """Create ASAL service for testing."""
        return ASALService()
    
    @pytest.fixture
    def custom_config(self):
        """Create custom ASAL configuration."""
        return ASALConfig(
            dimension_weights={
                "coherence": 0.2,
                "agency": 0.2,
                "memory": 0.1,
                "integration": 0.1,
                "complexity": 0.1,
                "novelty": 0.1,
                "stability": 0.1,
                "entanglement": 0.1
            },
            min_score_threshold=0.6,
            meta_learning_enabled=True,
            history_window=50
        )
    
    @pytest.fixture
    def sample_hypothesis(self):
        """Create sample hypothesis for testing."""
        return "Optimize turbine blade geometry using topology optimization and CFD analysis to maximize efficiency while maintaining structural integrity under high-temperature conditions."
    
    @pytest.fixture
    def sample_parameters(self):
        """Create sample parameters for testing."""
        return np.array([1.5, 2.3, 0.8, 1.2, 0.9])
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context for testing."""
        return {
            "domain": "aerospace",
            "priority": "high",
            "project": "turbine_optimization"
        }
    
    def test_service_initialization_default(self):
        """Test ASAL service initialization with default config."""
        service = ASALService()
        
        assert service.config is not None
        assert service.score_history == []
        assert len(service.meta_learning_data) == len(ConsciousnessDimension)
        
        # Check dimension weights sum to 1.0
        total_weight = sum(service.config.dimension_weights.values())
        assert np.isclose(total_weight, 1.0)
    
    def test_service_initialization_custom(self, custom_config):
        """Test ASAL service initialization with custom config."""
        service = ASALService(config=custom_config)
        
        assert service.config == custom_config
        assert service.config.min_score_threshold == 0.6
        assert service.config.history_window == 50
    
    def test_dimension_weights_normalization(self):
        """Test that dimension weights are normalized to sum to 1.0."""
        config = ASALConfig(
            dimension_weights={
                "coherence": 0.3,
                "agency": 0.3,
                "memory": 0.2,
                "integration": 0.2,
                "complexity": 0.2,
                "novelty": 0.2,
                "stability": 0.2,
                "entanglement": 0.2
            }
        )
        
        service = ASALService(config=config)
        total_weight = sum(service.config.dimension_weights.values())
        assert np.isclose(total_weight, 1.0)
    
    @pytest.mark.asyncio
    async def test_score_hypothesis_basic(self, asal_service, sample_hypothesis):
        """Test basic hypothesis scoring."""
        score = await asal_service.score_hypothesis(sample_hypothesis)
        
        assert isinstance(score, ConsciousnessScore)
        assert 0.0 <= score.coherence <= 1.0
        assert 0.0 <= score.agency <= 1.0
        assert 0.0 <= score.memory <= 1.0
        assert 0.0 <= score.integration <= 1.0
        assert 0.0 <= score.complexity <= 1.0
        assert 0.0 <= score.novelty <= 1.0
        assert 0.0 <= score.stability <= 1.0
        assert 0.0 <= score.entanglement <= 1.0
        assert 0.0 <= score.overall <= 1.0
        assert isinstance(score.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_score_hypothesis_with_parameters(
        self, asal_service, sample_hypothesis, sample_parameters
    ):
        """Test hypothesis scoring with parameters."""
        score = await asal_service.score_hypothesis(
            sample_hypothesis,
            parameters=sample_parameters
        )
        
        assert isinstance(score, ConsciousnessScore)
        assert 0.0 <= score.overall <= 1.0
    
    @pytest.mark.asyncio
    async def test_score_hypothesis_with_context(
        self, asal_service, sample_hypothesis, sample_context
    ):
        """Test hypothesis scoring with context."""
        score = await asal_service.score_hypothesis(
            sample_hypothesis,
            context=sample_context
        )
        
        assert isinstance(score, ConsciousnessScore)
        assert 0.0 <= score.overall <= 1.0
    
    @pytest.mark.asyncio
    async def test_score_hypothesis_complete(
        self, asal_service, sample_hypothesis, sample_parameters, sample_context
    ):
        """Test hypothesis scoring with all inputs."""
        score = await asal_service.score_hypothesis(
            sample_hypothesis,
            parameters=sample_parameters,
            context=sample_context
        )
        
        assert isinstance(score, ConsciousnessScore)
        assert 0.0 <= score.overall <= 1.0
        
        # Verify overall score is weighted average
        expected_overall = (
            score.coherence * asal_service.config.dimension_weights["coherence"] +
            score.agency * asal_service.config.dimension_weights["agency"] +
            score.memory * asal_service.config.dimension_weights["memory"] +
            score.integration * asal_service.config.dimension_weights["integration"] +
            score.complexity * asal_service.config.dimension_weights["complexity"] +
            score.novelty * asal_service.config.dimension_weights["novelty"] +
            score.stability * asal_service.config.dimension_weights["stability"] +
            score.entanglement * asal_service.config.dimension_weights["entanglement"]
        )
        assert np.isclose(score.overall, expected_overall)
    
    @pytest.mark.asyncio
    async def test_evaluate_hypothesis(
        self, asal_service, sample_hypothesis, sample_parameters, sample_context
    ):
        """Test complete hypothesis evaluation."""
        evaluation = await asal_service.evaluate_hypothesis(
            hypothesis_id="hyp_001",
            hypothesis=sample_hypothesis,
            parameters=sample_parameters,
            context=sample_context
        )
        
        assert isinstance(evaluation, HypothesisEvaluation)
        assert evaluation.hypothesis_id == "hyp_001"
        assert isinstance(evaluation.consciousness_score, ConsciousnessScore)
        assert isinstance(evaluation.quality_metrics, dict)
        assert isinstance(evaluation.recommendations, list)
        assert isinstance(evaluation.metadata, dict)
        
        # Check quality metrics
        assert "length_score" in evaluation.quality_metrics
        assert "structure_score" in evaluation.quality_metrics
        assert "parameter_quality" in evaluation.quality_metrics
        assert "overall_quality" in evaluation.quality_metrics
        
        # Check metadata
        assert "hypothesis_length" in evaluation.metadata
        assert "parameter_dim" in evaluation.metadata
        assert "context_keys" in evaluation.metadata
    
    @pytest.mark.asyncio
    async def test_score_history_tracking(self, asal_service, sample_hypothesis):
        """Test that score history is tracked correctly."""
        initial_history_len = len(asal_service.score_history)
        
        # Score multiple hypotheses
        for i in range(5):
            await asal_service.score_hypothesis(f"{sample_hypothesis} variant {i}")
        
        assert len(asal_service.score_history) == initial_history_len + 5
    
    @pytest.mark.asyncio
    async def test_score_history_window(self, sample_hypothesis):
        """Test that score history respects window size."""
        config = ASALConfig(history_window=3)
        service = ASALService(config=config)
        
        # Score more hypotheses than window size
        for i in range(5):
            await service.score_hypothesis(f"{sample_hypothesis} variant {i}")
        
        # History should be trimmed to window size
        assert len(service.score_history) == 3
    
    @pytest.mark.asyncio
    async def test_meta_learning_enabled(self, asal_service, sample_hypothesis):
        """Test that meta-learning data is collected when enabled."""
        asal_service.config.meta_learning_enabled = True
        
        await asal_service.score_hypothesis(sample_hypothesis)
        
        # Check that meta-learning data is populated
        for dim in ConsciousnessDimension:
            assert len(asal_service.meta_learning_data[dim.value]) > 0
    
    @pytest.mark.asyncio
    async def test_meta_learning_disabled(self, sample_hypothesis):
        """Test that meta-learning data is not collected when disabled."""
        config = ASALConfig(meta_learning_enabled=False)
        service = ASALService(config=config)
        
        await service.score_hypothesis(sample_hypothesis)
        
        # Meta-learning data should be empty
        for dim in ConsciousnessDimension:
            assert len(service.meta_learning_data[dim.value]) == 0
    
    def test_get_score_history(self, asal_service):
        """Test getting score history."""
        history = asal_service.get_score_history()
        assert isinstance(history, list)
    
    @pytest.mark.asyncio
    async def test_get_meta_learning_insights(self, asal_service, sample_hypothesis):
        """Test getting meta-learning insights."""
        # Score some hypotheses to populate meta-learning data
        for i in range(3):
            await asal_service.score_hypothesis(f"{sample_hypothesis} variant {i}")
        
        insights = asal_service.get_meta_learning_insights()
        
        assert isinstance(insights, dict)
        assert len(insights) == len(ConsciousnessDimension)
        
        # Check insight structure
        for dim in ConsciousnessDimension:
            assert dim.value in insights
            assert "mean" in insights[dim.value]
            assert "std" in insights[dim.value]
            assert "min" in insights[dim.value]
            assert "max" in insights[dim.value]
            assert "trend" in insights[dim.value]
    
    @pytest.mark.asyncio
    async def test_consciousness_score_to_dict(self, asal_service, sample_hypothesis):
        """Test converting consciousness score to dictionary."""
        score = await asal_service.score_hypothesis(sample_hypothesis)
        score_dict = score.to_dict()
        
        assert isinstance(score_dict, dict)
        assert "coherence" in score_dict
        assert "agency" in score_dict
        assert "memory" in score_dict
        assert "integration" in score_dict
        assert "complexity" in score_dict
        assert "novelty" in score_dict
        assert "stability" in score_dict
        assert "entanglement" in score_dict
        assert "overall" in score_dict
        assert "timestamp" in score_dict
    
    @pytest.mark.asyncio
    async def test_score_coherence_dimension(self, asal_service, sample_hypothesis):
        """Test coherence dimension scoring."""
        score = await asal_service._score_coherence(sample_hypothesis, None, None)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_score_agency_dimension(self, asal_service, sample_hypothesis):
        """Test agency dimension scoring."""
        score = await asal_service._score_agency(sample_hypothesis, None, None)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_score_memory_dimension(self, asal_service, sample_hypothesis):
        """Test memory dimension scoring."""
        score = await asal_service._score_memory(sample_hypothesis, None, None)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_score_integration_dimension(self, asal_service, sample_hypothesis):
        """Test integration dimension scoring."""
        score = await asal_service._score_integration(sample_hypothesis, None, None)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_score_complexity_dimension(self, asal_service, sample_hypothesis):
        """Test complexity dimension scoring."""
        score = await asal_service._score_complexity(sample_hypothesis, None, None)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_score_novelty_dimension(self, asal_service, sample_hypothesis):
        """Test novelty dimension scoring."""
        score = await asal_service._score_novelty(sample_hypothesis, None, None)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_score_stability_dimension(self, asal_service, sample_hypothesis):
        """Test stability dimension scoring."""
        score = await asal_service._score_stability(sample_hypothesis, None, None)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_score_entanglement_dimension(self, asal_service, sample_hypothesis):
        """Test entanglement dimension scoring."""
        score = await asal_service._score_entanglement(sample_hypothesis, None, None)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_recommendations_generation(self, asal_service, sample_hypothesis):
        """Test that recommendations are generated appropriately."""
        evaluation = await asal_service.evaluate_hypothesis(
            hypothesis_id="hyp_test",
            hypothesis=sample_hypothesis
        )
        
        assert len(evaluation.recommendations) > 0
        assert all(isinstance(rec, str) for rec in evaluation.recommendations)
    
    @pytest.mark.asyncio
    async def test_short_hypothesis_scoring(self, asal_service):
        """Test scoring of short hypothesis."""
        short_hypothesis = "Test hypothesis"
        score = await asal_service.score_hypothesis(short_hypothesis)
        
        assert isinstance(score, ConsciousnessScore)
        assert 0.0 <= score.overall <= 1.0
    
    @pytest.mark.asyncio
    async def test_long_hypothesis_scoring(self, asal_service):
        """Test scoring of long hypothesis."""
        long_hypothesis = " ".join(["Test hypothesis with many words"] * 50)
        score = await asal_service.score_hypothesis(long_hypothesis)
        
        assert isinstance(score, ConsciousnessScore)
        assert 0.0 <= score.overall <= 1.0
    
    @pytest.mark.asyncio
    async def test_empty_parameters(self, asal_service, sample_hypothesis):
        """Test scoring with empty parameters array."""
        empty_params = np.array([])
        score = await asal_service.score_hypothesis(
            sample_hypothesis,
            parameters=empty_params
        )
        
        assert isinstance(score, ConsciousnessScore)
        assert 0.0 <= score.overall <= 1.0
    
    @pytest.mark.asyncio
    async def test_large_parameters(self, asal_service, sample_hypothesis):
        """Test scoring with large parameters array."""
        large_params = np.random.randn(100)
        score = await asal_service.score_hypothesis(
            sample_hypothesis,
            parameters=large_params
        )
        
        assert isinstance(score, ConsciousnessScore)
        assert 0.0 <= score.overall <= 1.0
    
    @pytest.mark.asyncio
    async def test_empty_context(self, asal_service, sample_hypothesis):
        """Test scoring with empty context."""
        empty_context = {}
        score = await asal_service.score_hypothesis(
            sample_hypothesis,
            context=empty_context
        )
        
        assert isinstance(score, ConsciousnessScore)
        assert 0.0 <= score.overall <= 1.0
    
    @pytest.mark.asyncio
    async def test_multiple_evaluations_consistency(
        self, asal_service, sample_hypothesis
    ):
        """Test that multiple evaluations of same hypothesis are consistent."""
        score1 = await asal_service.score_hypothesis(sample_hypothesis)
        score2 = await asal_service.score_hypothesis(sample_hypothesis)
        
        # Scores should be similar (allowing for small variations due to history effects)
        assert abs(score1.overall - score2.overall) < 0.2
    
    @pytest.mark.asyncio
    async def test_different_hypotheses_different_scores(self, asal_service):
        """Test that different hypotheses get different scores."""
        hypothesis1 = "Simple test"
        hypothesis2 = "Complex hypothesis with detailed analysis and multiple components for comprehensive evaluation"
        
        score1 = await asal_service.score_hypothesis(hypothesis1)
        score2 = await asal_service.score_hypothesis(hypothesis2)
        
        # Scores should be different
        assert score1.overall != score2.overall


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
