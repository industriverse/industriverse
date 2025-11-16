"""
Unit tests for DGM Service

Tests cover:
1. Service initialization
2. Population initialization
3. Fitness evaluation
4. Genetic operations (crossover, mutation, selection)
5. Evolution loop
6. Diversity management
7. Convergence detection

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import numpy as np
import asyncio
from typing import List

import sys
sys.path.append('/home/ubuntu/industriverse/src/core_ai_layer/discovery_loop/services/dgm')
from dgm_service import DGMService, DGMConfig, Hypothesis, example_fitness_function


class TestDGMService:
    """Test suite for DGM Service."""
    
    @pytest.fixture
    def dgm_config(self):
        """Create a test DGM configuration."""
        return DGMConfig(
            population_size=20,
            num_generations=10,
            crossover_rate=0.8,
            mutation_rate=0.1,
            elite_size=2,
            convergence_threshold=0.95,
            diversity_threshold=0.1
        )
    
    @pytest.fixture
    def dgm_service(self, dgm_config):
        """Create a DGM service instance."""
        return DGMService(dgm_config)
    
    def test_initialization(self, dgm_service, dgm_config):
        """Test DGM service initialization."""
        assert dgm_service.config == dgm_config
        assert dgm_service.generation == 0
        assert dgm_service.best_hypothesis is None
        assert len(dgm_service.population) == 0
        assert len(dgm_service.evolution_history) == 0
    
    @pytest.mark.asyncio
    async def test_population_initialization(self, dgm_service):
        """Test population initialization."""
        initial_hypothesis = "Test hypothesis"
        param_dim = 5
        min_bounds = np.full(param_dim, -10.0)
        max_bounds = np.full(param_dim, 10.0)
        parameter_bounds = (min_bounds, max_bounds)
        
        await dgm_service._initialize_population(initial_hypothesis, parameter_bounds)
        
        assert len(dgm_service.population) == dgm_service.config.population_size
        
        for hypothesis in dgm_service.population:
            assert isinstance(hypothesis, Hypothesis)
            assert len(hypothesis.parameters) == param_dim
            assert np.all(hypothesis.parameters >= min_bounds)
            assert np.all(hypothesis.parameters <= max_bounds)
            assert hypothesis.generation == 0
    
    @pytest.mark.asyncio
    async def test_fitness_evaluation(self, dgm_service):
        """Test fitness evaluation."""
        # Initialize population
        await dgm_service._initialize_population("Test", None)
        
        # Evaluate fitness
        await dgm_service._evaluate_population(example_fitness_function)
        
        # Check that all hypotheses have fitness scores
        for hypothesis in dgm_service.population:
            assert 0.0 <= hypothesis.fitness <= 1.0
        
        # Check that population is sorted by fitness
        for i in range(len(dgm_service.population) - 1):
            assert dgm_service.population[i].fitness >= dgm_service.population[i + 1].fitness
        
        # Check that best hypothesis is set
        assert dgm_service.best_hypothesis is not None
        assert dgm_service.best_hypothesis.fitness == dgm_service.population[0].fitness
    
    def test_tournament_selection(self, dgm_service):
        """Test tournament selection."""
        # Create test population with known fitness values
        dgm_service.population = [
            Hypothesis(id=f"hyp_{i}", content="test", parameters=np.array([i]), fitness=i/10.0)
            for i in range(10)
        ]
        
        # Run tournament selection multiple times
        selected = [dgm_service._tournament_selection(tournament_size=3) for _ in range(100)]
        
        # Check that selected hypotheses have higher fitness on average
        avg_fitness = np.mean([h.fitness for h in selected])
        population_avg = np.mean([h.fitness for h in dgm_service.population])
        assert avg_fitness > population_avg
    
    def test_crossover(self, dgm_service):
        """Test crossover operation."""
        parent1 = Hypothesis(
            id="parent1",
            content="Parent 1",
            parameters=np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
            fitness=0.5
        )
        parent2 = Hypothesis(
            id="parent2",
            content="Parent 2",
            parameters=np.array([6.0, 7.0, 8.0, 9.0, 10.0]),
            fitness=0.6
        )
        
        child1, child2 = dgm_service._crossover(parent1, parent2)
        
        # Check that children have correct structure
        assert isinstance(child1, Hypothesis)
        assert isinstance(child2, Hypothesis)
        assert len(child1.parameters) == len(parent1.parameters)
        assert len(child2.parameters) == len(parent2.parameters)
        
        # Check that children have both parents in lineage
        assert parent1.id in child1.lineage
        assert parent2.id in child1.lineage
        
        # Check that child parameters are combinations of parent parameters
        for i in range(len(child1.parameters)):
            assert child1.parameters[i] in [parent1.parameters[i], parent2.parameters[i]]
    
    def test_mutation(self, dgm_service):
        """Test mutation operation."""
        original = Hypothesis(
            id="original",
            content="Original",
            parameters=np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
            fitness=0.5
        )
        
        param_dim = len(original.parameters)
        min_bounds = np.full(param_dim, -10.0)
        max_bounds = np.full(param_dim, 10.0)
        parameter_bounds = (min_bounds, max_bounds)
        
        mutated = dgm_service._mutate(original, parameter_bounds)
        
        # Check that mutated hypothesis has correct structure
        assert isinstance(mutated, Hypothesis)
        assert len(mutated.parameters) == len(original.parameters)
        assert original.id in mutated.lineage
        
        # Check that parameters are within bounds
        assert np.all(mutated.parameters >= min_bounds)
        assert np.all(mutated.parameters <= max_bounds)
        
        # Check that at least some parameters changed
        assert not np.array_equal(mutated.parameters, original.parameters)
    
    def test_diversity_calculation(self, dgm_service):
        """Test diversity calculation."""
        # Create population with identical hypotheses (zero diversity)
        dgm_service.population = [
            Hypothesis(id=f"hyp_{i}", content="test", parameters=np.array([1.0, 2.0, 3.0]))
            for i in range(10)
        ]
        diversity_zero = dgm_service._calculate_diversity()
        assert diversity_zero == 0.0
        
        # Create population with diverse hypotheses
        dgm_service.population = [
            Hypothesis(id=f"hyp_{i}", content="test", parameters=np.random.randn(3))
            for i in range(10)
        ]
        diversity_high = dgm_service._calculate_diversity()
        assert diversity_high > 0.0
    
    @pytest.mark.asyncio
    async def test_diversity_injection(self, dgm_service):
        """Test diversity injection."""
        # Initialize population with identical hypotheses
        dgm_service.population = [
            Hypothesis(id=f"hyp_{i}", content="test", parameters=np.array([1.0, 2.0, 3.0]))
            for i in range(20)
        ]
        
        initial_diversity = dgm_service._calculate_diversity()
        
        # Inject diversity
        param_dim = 3
        min_bounds = np.full(param_dim, -10.0)
        max_bounds = np.full(param_dim, 10.0)
        parameter_bounds = (min_bounds, max_bounds)
        
        await dgm_service._inject_diversity(parameter_bounds)
        
        final_diversity = dgm_service._calculate_diversity()
        
        # Check that diversity increased
        assert final_diversity > initial_diversity
    
    @pytest.mark.asyncio
    async def test_evolution_loop(self, dgm_service):
        """Test complete evolution loop."""
        initial_hypothesis = "Optimize parameters"
        param_dim = 5
        min_bounds = np.full(param_dim, -10.0)
        max_bounds = np.full(param_dim, 10.0)
        parameter_bounds = (min_bounds, max_bounds)
        
        best_hypothesis = await dgm_service.evolve_hypothesis(
            initial_hypothesis=initial_hypothesis,
            fitness_fn=example_fitness_function,
            parameter_bounds=parameter_bounds
        )
        
        # Check that best hypothesis exists
        assert best_hypothesis is not None
        assert isinstance(best_hypothesis, Hypothesis)
        
        # Check that fitness improved
        assert best_hypothesis.fitness > 0.0
        
        # Check that evolution history was recorded
        assert len(dgm_service.evolution_history) > 0
        
        # Check that fitness improved over generations
        first_gen_fitness = dgm_service.evolution_history[0]["best_fitness"]
        last_gen_fitness = dgm_service.evolution_history[-1]["best_fitness"]
        assert last_gen_fitness >= first_gen_fitness
    
    @pytest.mark.asyncio
    async def test_convergence_detection(self, dgm_service):
        """Test early convergence detection."""
        # Create a fitness function that always returns high fitness
        def high_fitness_fn(hypothesis: Hypothesis) -> float:
            return 0.99
        
        initial_hypothesis = "Test convergence"
        
        best_hypothesis = await dgm_service.evolve_hypothesis(
            initial_hypothesis=initial_hypothesis,
            fitness_fn=high_fitness_fn,
            parameter_bounds=None
        )
        
        # Check that evolution stopped early due to convergence
        assert len(dgm_service.evolution_history) < dgm_service.config.num_generations
        assert best_hypothesis.fitness >= dgm_service.config.convergence_threshold
    
    def test_get_top_hypotheses(self, dgm_service):
        """Test getting top hypotheses."""
        # Create test population
        dgm_service.population = [
            Hypothesis(id=f"hyp_{i}", content="test", parameters=np.array([i]), fitness=i/10.0)
            for i in range(10, 0, -1)  # Descending fitness
        ]
        
        top_5 = dgm_service.get_top_hypotheses(n=5)
        
        assert len(top_5) == 5
        for i in range(len(top_5) - 1):
            assert top_5[i].fitness >= top_5[i + 1].fitness
    
    def test_evolution_history(self, dgm_service):
        """Test evolution history recording."""
        # Manually record some history
        dgm_service.generation = 0
        dgm_service.best_hypothesis = Hypothesis(
            id="best", content="test", parameters=np.array([1.0]), fitness=0.8
        )
        dgm_service.population = [
            Hypothesis(id=f"hyp_{i}", content="test", parameters=np.array([i]), fitness=i/10.0)
            for i in range(10)
        ]
        
        dgm_service._record_evolution_history()
        
        history = dgm_service.get_evolution_history()
        assert len(history) == 1
        assert history[0]["generation"] == 0
        assert history[0]["best_fitness"] == 0.8
        assert "avg_fitness" in history[0]
        assert "diversity" in history[0]
        assert "timestamp" in history[0]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
