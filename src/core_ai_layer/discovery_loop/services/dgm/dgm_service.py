"""
Deep Genetic Modification (DGM) Service

This module implements the DGM service for hypothesis evolution using genetic algorithms.
It integrates with the existing pk_alpha genetic algorithm in the protocol layer.

The DGM service is responsible for:
1. Evolving hypotheses through genetic operations (crossover, mutation)
2. Evaluating hypothesis fitness using custom fitness functions
3. Managing population diversity and convergence
4. Integrating with the Discovery Loop orchestrator

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import asyncio
import logging
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

# Import the existing pk_alpha genetic algorithm
import sys
sys.path.append('/home/ubuntu/industriverse/src/protocol_layer/protocols/genetic')
from pk_alpha import GeneticAlgorithm, Individual

logger = logging.getLogger(__name__)


@dataclass
class Hypothesis:
    """
    Represents a hypothesis in the discovery loop.
    
    Attributes:
        id: Unique identifier for the hypothesis
        content: The hypothesis text/description
        parameters: Numerical parameters associated with the hypothesis
        fitness: Fitness score (0.0 to 1.0)
        generation: Generation number in which this hypothesis was created
        lineage: List of parent hypothesis IDs
        metadata: Additional metadata (e.g., UTID, energy signature)
    """
    id: str
    content: str
    parameters: np.ndarray
    fitness: float = 0.0
    generation: int = 0
    lineage: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DGMConfig:
    """
    Configuration for the DGM service.
    
    Attributes:
        population_size: Number of hypotheses in the population
        num_generations: Maximum number of generations to evolve
        crossover_rate: Probability of crossover (0.0 to 1.0)
        mutation_rate: Probability of mutation (0.0 to 1.0)
        elite_size: Number of top hypotheses to preserve each generation
        convergence_threshold: Fitness threshold to stop evolution early
        diversity_threshold: Minimum diversity to maintain in population
    """
    population_size: int = 50
    num_generations: int = 100
    crossover_rate: float = 0.8
    mutation_rate: float = 0.1
    elite_size: int = 5
    convergence_threshold: float = 0.95
    diversity_threshold: float = 0.1


class DGMService:
    """
    Deep Genetic Modification Service for hypothesis evolution.
    
    This service uses genetic algorithms to evolve hypotheses, integrating with
    the existing pk_alpha genetic algorithm implementation.
    """
    
    def __init__(self, config: Optional[DGMConfig] = None):
        """
        Initialize the DGM service.
        
        Args:
            config: DGM configuration (uses defaults if None)
        """
        self.config = config or DGMConfig()
        self.genetic_algorithm = GeneticAlgorithm(
            population_size=self.config.population_size,
            crossover_rate=self.config.crossover_rate,
            mutation_rate=self.config.mutation_rate
        )
        self.population: List[Hypothesis] = []
        self.generation = 0
        self.best_hypothesis: Optional[Hypothesis] = None
        self.evolution_history: List[Dict[str, Any]] = []
        
        logger.info(f"DGM Service initialized with config: {self.config}")
    
    async def evolve_hypothesis(
        self,
        initial_hypothesis: str,
        fitness_fn: Callable[[Hypothesis], float],
        parameter_bounds: Optional[Tuple[np.ndarray, np.ndarray]] = None
    ) -> Hypothesis:
        """
        Evolve a hypothesis using genetic algorithms.
        
        Args:
            initial_hypothesis: Starting hypothesis text
            fitness_fn: Function to evaluate hypothesis fitness
            parameter_bounds: (min_bounds, max_bounds) for parameter space
        
        Returns:
            Best evolved hypothesis
        """
        logger.info(f"Starting hypothesis evolution: '{initial_hypothesis[:50]}...'")
        
        # Initialize population
        await self._initialize_population(initial_hypothesis, parameter_bounds)
        
        # Evolution loop
        for gen in range(self.config.num_generations):
            self.generation = gen
            
            # Evaluate fitness for all hypotheses
            await self._evaluate_population(fitness_fn)
            
            # Check for convergence
            if self.best_hypothesis and self.best_hypothesis.fitness >= self.config.convergence_threshold:
                logger.info(f"Converged at generation {gen} with fitness {self.best_hypothesis.fitness:.4f}")
                break
            
            # Check for diversity
            diversity = self._calculate_diversity()
            if diversity < self.config.diversity_threshold:
                logger.warning(f"Low diversity ({diversity:.4f}) at generation {gen}, injecting random hypotheses")
                await self._inject_diversity(parameter_bounds)
            
            # Selection, crossover, mutation
            await self._evolve_generation(fitness_fn, parameter_bounds)
            
            # Log progress
            if gen % 10 == 0:
                logger.info(f"Generation {gen}: Best fitness = {self.best_hypothesis.fitness:.4f}, Diversity = {diversity:.4f}")
                self._record_evolution_history()
        
        logger.info(f"Evolution complete. Best hypothesis fitness: {self.best_hypothesis.fitness:.4f}")
        return self.best_hypothesis
    
    async def _initialize_population(
        self,
        initial_hypothesis: str,
        parameter_bounds: Optional[Tuple[np.ndarray, np.ndarray]]
    ):
        """Initialize the population with random hypotheses."""
        self.population = []
        
        # Determine parameter dimensionality
        param_dim = 10  # Default dimension
        if parameter_bounds:
            param_dim = len(parameter_bounds[0])
        
        for i in range(self.config.population_size):
            # Generate random parameters
            if parameter_bounds:
                min_bounds, max_bounds = parameter_bounds
                parameters = np.random.uniform(min_bounds, max_bounds)
            else:
                parameters = np.random.randn(param_dim)
            
            # Create hypothesis
            hypothesis = Hypothesis(
                id=f"hyp_{self.generation}_{i}",
                content=f"{initial_hypothesis} (variant {i})",
                parameters=parameters,
                generation=self.generation,
                lineage=[],
                metadata={"source": "initial_population"}
            )
            
            self.population.append(hypothesis)
        
        logger.info(f"Initialized population with {len(self.population)} hypotheses")
    
    async def _evaluate_population(self, fitness_fn: Callable[[Hypothesis], float]):
        """Evaluate fitness for all hypotheses in the population."""
        for hypothesis in self.population:
            # Evaluate fitness
            hypothesis.fitness = fitness_fn(hypothesis)
            
            # Update best hypothesis
            if self.best_hypothesis is None or hypothesis.fitness > self.best_hypothesis.fitness:
                self.best_hypothesis = hypothesis
        
        # Sort population by fitness (descending)
        self.population.sort(key=lambda h: h.fitness, reverse=True)
    
    async def _evolve_generation(
        self,
        fitness_fn: Callable[[Hypothesis], float],
        parameter_bounds: Optional[Tuple[np.ndarray, np.ndarray]]
    ):
        """
        Evolve the population for one generation using selection, crossover, and mutation.
        """
        new_population = []
        
        # Elitism: preserve top hypotheses
        elite = self.population[:self.config.elite_size]
        new_population.extend(elite)
        
        # Generate offspring to fill the rest of the population
        while len(new_population) < self.config.population_size:
            # Selection: tournament selection
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            # Crossover
            if np.random.rand() < self.config.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            
            # Mutation
            if np.random.rand() < self.config.mutation_rate:
                child1 = self._mutate(child1, parameter_bounds)
            if np.random.rand() < self.config.mutation_rate:
                child2 = self._mutate(child2, parameter_bounds)
            
            new_population.append(child1)
            if len(new_population) < self.config.population_size:
                new_population.append(child2)
        
        self.population = new_population[:self.config.population_size]
    
    def _tournament_selection(self, tournament_size: int = 3) -> Hypothesis:
        """
        Select a hypothesis using tournament selection.
        
        Args:
            tournament_size: Number of hypotheses in the tournament
        
        Returns:
            Selected hypothesis
        """
        tournament = np.random.choice(self.population, size=tournament_size, replace=False)
        return max(tournament, key=lambda h: h.fitness)
    
    def _crossover(self, parent1: Hypothesis, parent2: Hypothesis) -> Tuple[Hypothesis, Hypothesis]:
        """
        Perform crossover between two parent hypotheses.
        
        Args:
            parent1: First parent hypothesis
            parent2: Second parent hypothesis
        
        Returns:
            Two child hypotheses
        """
        # Uniform crossover for parameters
        mask = np.random.rand(len(parent1.parameters)) < 0.5
        child1_params = np.where(mask, parent1.parameters, parent2.parameters)
        child2_params = np.where(mask, parent2.parameters, parent1.parameters)
        
        # Create child hypotheses
        child1 = Hypothesis(
            id=f"hyp_{self.generation + 1}_{len(self.population)}",
            content=f"Crossover of {parent1.id} and {parent2.id}",
            parameters=child1_params,
            generation=self.generation + 1,
            lineage=[parent1.id, parent2.id],
            metadata={"source": "crossover"}
        )
        
        child2 = Hypothesis(
            id=f"hyp_{self.generation + 1}_{len(self.population) + 1}",
            content=f"Crossover of {parent1.id} and {parent2.id}",
            parameters=child2_params,
            generation=self.generation + 1,
            lineage=[parent1.id, parent2.id],
            metadata={"source": "crossover"}
        )
        
        return child1, child2
    
    def _mutate(
        self,
        hypothesis: Hypothesis,
        parameter_bounds: Optional[Tuple[np.ndarray, np.ndarray]]
    ) -> Hypothesis:
        """
        Mutate a hypothesis by adding Gaussian noise to its parameters.
        
        Args:
            hypothesis: Hypothesis to mutate
            parameter_bounds: Optional bounds to clip parameters
        
        Returns:
            Mutated hypothesis
        """
        # Add Gaussian noise
        mutation_strength = 0.1
        mutated_params = hypothesis.parameters + np.random.randn(len(hypothesis.parameters)) * mutation_strength
        
        # Clip to bounds if provided
        if parameter_bounds:
            min_bounds, max_bounds = parameter_bounds
            mutated_params = np.clip(mutated_params, min_bounds, max_bounds)
        
        # Create mutated hypothesis
        mutated = Hypothesis(
            id=f"hyp_{self.generation + 1}_{len(self.population)}_mut",
            content=f"Mutation of {hypothesis.id}",
            parameters=mutated_params,
            generation=self.generation + 1,
            lineage=[hypothesis.id],
            metadata={"source": "mutation"}
        )
        
        return mutated
    
    def _calculate_diversity(self) -> float:
        """
        Calculate population diversity as the average pairwise distance.
        
        Returns:
            Diversity score (0.0 to 1.0)
        """
        if len(self.population) < 2:
            return 0.0
        
        # Calculate pairwise distances
        distances = []
        for i in range(len(self.population)):
            for j in range(i + 1, len(self.population)):
                dist = np.linalg.norm(self.population[i].parameters - self.population[j].parameters)
                distances.append(dist)
        
        # Normalize by maximum possible distance
        max_dist = np.sqrt(len(self.population[0].parameters))
        avg_dist = np.mean(distances) / max_dist if distances else 0.0
        
        return avg_dist
    
    async def _inject_diversity(self, parameter_bounds: Optional[Tuple[np.ndarray, np.ndarray]]):
        """Inject random hypotheses to increase diversity."""
        num_to_inject = self.config.population_size // 10  # Inject 10% of population
        
        for i in range(num_to_inject):
            # Generate random parameters
            if parameter_bounds:
                min_bounds, max_bounds = parameter_bounds
                parameters = np.random.uniform(min_bounds, max_bounds)
            else:
                parameters = np.random.randn(len(self.population[0].parameters))
            
            # Create random hypothesis
            hypothesis = Hypothesis(
                id=f"hyp_{self.generation}_{len(self.population)}_random",
                content=f"Random injection {i}",
                parameters=parameters,
                generation=self.generation,
                lineage=[],
                metadata={"source": "diversity_injection"}
            )
            
            # Replace worst hypothesis
            self.population[-1] = hypothesis
    
    def _record_evolution_history(self):
        """Record evolution history for analysis."""
        history_entry = {
            "generation": self.generation,
            "best_fitness": self.best_hypothesis.fitness if self.best_hypothesis else 0.0,
            "avg_fitness": np.mean([h.fitness for h in self.population]),
            "diversity": self._calculate_diversity(),
            "timestamp": datetime.now().isoformat()
        }
        self.evolution_history.append(history_entry)
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """
        Get the evolution history.
        
        Returns:
            List of evolution history entries
        """
        return self.evolution_history
    
    def get_top_hypotheses(self, n: int = 5) -> List[Hypothesis]:
        """
        Get the top N hypotheses from the current population.
        
        Args:
            n: Number of top hypotheses to return
        
        Returns:
            List of top hypotheses
        """
        return self.population[:n]


# Example fitness function
def example_fitness_function(hypothesis: Hypothesis) -> float:
    """
    Example fitness function for testing.
    
    This is a simple sphere function: minimize sum of squared parameters.
    Fitness is 1.0 / (1.0 + sum(params^2))
    
    Args:
        hypothesis: Hypothesis to evaluate
    
    Returns:
        Fitness score (0.0 to 1.0)
    """
    sum_squared = np.sum(hypothesis.parameters ** 2)
    fitness = 1.0 / (1.0 + sum_squared)
    return fitness


# Example usage
async def main():
    """Example usage of DGM service."""
    # Create DGM service
    config = DGMConfig(
        population_size=30,
        num_generations=50,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elite_size=3
    )
    dgm_service = DGMService(config)
    
    # Define parameter bounds
    param_dim = 5
    min_bounds = np.full(param_dim, -10.0)
    max_bounds = np.full(param_dim, 10.0)
    parameter_bounds = (min_bounds, max_bounds)
    
    # Evolve hypothesis
    initial_hypothesis = "Optimize turbine blade geometry for maximum efficiency"
    best_hypothesis = await dgm_service.evolve_hypothesis(
        initial_hypothesis=initial_hypothesis,
        fitness_fn=example_fitness_function,
        parameter_bounds=parameter_bounds
    )
    
    # Print results
    print(f"\nBest Hypothesis:")
    print(f"  ID: {best_hypothesis.id}")
    print(f"  Fitness: {best_hypothesis.fitness:.6f}")
    print(f"  Parameters: {best_hypothesis.parameters}")
    print(f"  Generation: {best_hypothesis.generation}")
    
    # Print evolution history
    print(f"\nEvolution History:")
    for entry in dgm_service.get_evolution_history():
        print(f"  Gen {entry['generation']}: Best={entry['best_fitness']:.4f}, Avg={entry['avg_fitness']:.4f}, Div={entry['diversity']:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
