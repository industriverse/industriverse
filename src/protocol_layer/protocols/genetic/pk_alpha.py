"""
Protocol-Driven Genetic Algorithm Layer (PK-Alpha) for Industriverse Protocol Layer

This module implements the Protocol-Driven Genetic Algorithm Layer (PK-Alpha),
enabling evolutionary algorithm capabilities for protocol optimization,
algorithm building, and adaptive behavior within the Industriverse ecosystem.

Features:
1. Genetic algorithm framework for protocol optimization
2. Algorithm building capabilities through genetic programming
3. Integration with AlphaEvolve for advanced algorithm evolution
4. Fitness evaluation based on protocol performance metrics
5. Synthetic data generation for algorithm training
6. Distributed evolution across the protocol mesh
"""

import uuid
import time
import random
import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GeneticOperationType(Enum):
    """Types of genetic operations."""
    CROSSOVER = "crossover"
    MUTATION = "mutation"
    SELECTION = "selection"
    EVALUATION = "evaluation"


@dataclass
class GeneticIndividual:
    """
    Represents an individual in the genetic algorithm population.
    """
    id: str
    genotype: Any  # The genetic representation (could be dict, list, etc.)
    fitness: float = -1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    creation_time: float = field(default_factory=time.time)
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "genotype": self.genotype,
            "fitness": self.fitness,
            "metadata": self.metadata,
            "creation_time": self.creation_time,
            "generation": self.generation,
            "parent_ids": self.parent_ids
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneticIndividual':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            genotype=data["genotype"],
            fitness=data.get("fitness", -1.0),
            metadata=data.get("metadata", {}),
            creation_time=data.get("creation_time", time.time()),
            generation=data.get("generation", 0),
            parent_ids=data.get("parent_ids", [])
        )


@dataclass
class GeneticPopulation:
    """
    Represents a population of individuals in the genetic algorithm.
    """
    id: str
    individuals: List[GeneticIndividual] = field(default_factory=list)
    generation: int = 0
    target_size: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_individual(self, individual: GeneticIndividual) -> None:
        """Add an individual to the population."""
        self.individuals.append(individual)
    
    def get_individual(self, individual_id: str) -> Optional[GeneticIndividual]:
        """Get an individual by ID."""
        for ind in self.individuals:
            if ind.id == individual_id:
                return ind
        return None
    
    def get_fittest(self, n: int = 1) -> List[GeneticIndividual]:
        """Get the n fittest individuals."""
        sorted_individuals = sorted(self.individuals, key=lambda x: x.fitness, reverse=True)
        return sorted_individuals[:n]
    
    def get_random(self, n: int = 1) -> List[GeneticIndividual]:
        """Get n random individuals."""
        if n >= len(self.individuals):
            return self.individuals.copy()
        return random.sample(self.individuals, n)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "individuals": [ind.to_dict() for ind in self.individuals],
            "generation": self.generation,
            "target_size": self.target_size,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneticPopulation':
        """Create from dictionary representation."""
        population = cls(
            id=data["id"],
            generation=data.get("generation", 0),
            target_size=data.get("target_size", 100),
            metadata=data.get("metadata", {})
        )
        for ind_data in data.get("individuals", []):
            population.add_individual(GeneticIndividual.from_dict(ind_data))
        return population


class GeneticOperator:
    """
    Base class for genetic operators (crossover, mutation, selection).
    """
    def __init__(self, operator_type: GeneticOperationType, config: Dict[str, Any] = None):
        self.operator_type = operator_type
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.GeneticOperator.{operator_type.value}")
    
    async def apply(self, population: GeneticPopulation, **kwargs) -> Any:
        """Apply the genetic operator to the population."""
        raise NotImplementedError("Subclasses must implement apply()")


class CrossoverOperator(GeneticOperator):
    """
    Performs crossover between individuals to create offspring.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(GeneticOperationType.CROSSOVER, config)
        self.crossover_rate = self.config.get("crossover_rate", 0.7)
    
    async def apply(self, population: GeneticPopulation, **kwargs) -> List[GeneticIndividual]:
        """Apply crossover to selected parents."""
        parents = kwargs.get("parents", population.get_fittest(2))
        if len(parents) < 2:
            self.logger.warning("Not enough parents for crossover")
            return []
        
        # Simple example for dictionary genotypes
        parent1, parent2 = parents[0], parents[1]
        
        if not isinstance(parent1.genotype, dict) or not isinstance(parent2.genotype, dict):
            self.logger.warning("Crossover only implemented for dictionary genotypes")
            return []
        
        # Create offspring genotype by combining parent genotypes
        offspring_genotype = {}
        all_keys = set(parent1.genotype.keys()) | set(parent2.genotype.keys())
        
        for key in all_keys:
            if key in parent1.genotype and key in parent2.genotype:
                # For shared keys, randomly select from either parent
                if random.random() < 0.5:
                    offspring_genotype[key] = parent1.genotype[key]
                else:
                    offspring_genotype[key] = parent2.genotype[key]
            elif key in parent1.genotype:
                offspring_genotype[key] = parent1.genotype[key]
            else:
                offspring_genotype[key] = parent2.genotype[key]
        
        # Create offspring individual
        offspring = GeneticIndividual(
            id=str(uuid.uuid4()),
            genotype=offspring_genotype,
            generation=population.generation + 1,
            parent_ids=[parent1.id, parent2.id]
        )
        
        return [offspring]


class MutationOperator(GeneticOperator):
    """
    Performs mutation on individuals to introduce variation.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(GeneticOperationType.MUTATION, config)
        self.mutation_rate = self.config.get("mutation_rate", 0.1)
    
    async def apply(self, population: GeneticPopulation, **kwargs) -> List[GeneticIndividual]:
        """Apply mutation to individuals."""
        individuals = kwargs.get("individuals", population.individuals)
        if not individuals:
            return []
        
        mutated = []
        for individual in individuals:
            if random.random() < self.mutation_rate:
                mutated_individual = await self._mutate_individual(individual)
                mutated.append(mutated_individual)
        
        return mutated
    
    async def _mutate_individual(self, individual: GeneticIndividual) -> GeneticIndividual:
        """Mutate a single individual."""
        if not isinstance(individual.genotype, dict):
            self.logger.warning("Mutation only implemented for dictionary genotypes")
            return individual
        
        # Create a copy of the genotype
        mutated_genotype = individual.genotype.copy()
        
        # Select a random key to mutate
        if not mutated_genotype:
            return individual
        
        key_to_mutate = random.choice(list(mutated_genotype.keys()))
        value = mutated_genotype[key_to_mutate]
        
        # Apply mutation based on value type
        if isinstance(value, (int, float)):
            # Add random noise
            noise = random.uniform(-0.1, 0.1) * value
            mutated_genotype[key_to_mutate] = value + noise
        elif isinstance(value, str):
            # Modify string (simple example)
            if value:
                chars = list(value)
                idx = random.randint(0, len(chars) - 1)
                chars[idx] = chr(ord(chars[idx]) + random.randint(-1, 1))
                mutated_genotype[key_to_mutate] = ''.join(chars)
        elif isinstance(value, list):
            # Modify list (simple example)
            if value:
                idx = random.randint(0, len(value) - 1)
                if isinstance(value[idx], (int, float)):
                    value[idx] += random.uniform(-0.1, 0.1) * value[idx]
                mutated_genotype[key_to_mutate] = value
        
        # Create mutated individual
        mutated_individual = GeneticIndividual(
            id=str(uuid.uuid4()),
            genotype=mutated_genotype,
            generation=individual.generation,
            parent_ids=[individual.id]
        )
        
        return mutated_individual


class SelectionOperator(GeneticOperator):
    """
    Performs selection of individuals for reproduction.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(GeneticOperationType.SELECTION, config)
        self.selection_method = self.config.get("selection_method", "tournament")
        self.tournament_size = self.config.get("tournament_size", 3)
    
    async def apply(self, population: GeneticPopulation, **kwargs) -> List[GeneticIndividual]:
        """Select individuals for reproduction."""
        num_to_select = kwargs.get("num_to_select", 2)
        
        if self.selection_method == "tournament":
            return await self._tournament_selection(population, num_to_select)
        elif self.selection_method == "roulette":
            return await self._roulette_selection(population, num_to_select)
        else:
            self.logger.warning(f"Unknown selection method: {self.selection_method}")
            return population.get_fittest(num_to_select)
    
    async def _tournament_selection(self, population: GeneticPopulation, num_to_select: int) -> List[GeneticIndividual]:
        """Tournament selection."""
        selected = []
        for _ in range(num_to_select):
            # Select random individuals for tournament
            tournament = population.get_random(self.tournament_size)
            if not tournament:
                continue
            
            # Select the fittest from the tournament
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        
        return selected
    
    async def _roulette_selection(self, population: GeneticPopulation, num_to_select: int) -> List[GeneticIndividual]:
        """Roulette wheel selection."""
        if not population.individuals:
            return []
        
        # Calculate selection probabilities based on fitness
        total_fitness = sum(max(0.0, ind.fitness) for ind in population.individuals)
        if total_fitness <= 0:
            # If all fitnesses are negative or zero, use uniform selection
            return population.get_random(num_to_select)
        
        selection_probs = [max(0.0, ind.fitness) / total_fitness for ind in population.individuals]
        
        # Select individuals based on probabilities
        selected_indices = np.random.choice(
            len(population.individuals),
            size=num_to_select,
            p=selection_probs,
            replace=True
        )
        
        return [population.individuals[i] for i in selected_indices]


class FitnessEvaluator(GeneticOperator):
    """
    Evaluates the fitness of individuals.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(GeneticOperationType.EVALUATION, config)
        self.evaluation_function = self.config.get("evaluation_function")
    
    async def apply(self, population: GeneticPopulation, **kwargs) -> List[GeneticIndividual]:
        """Evaluate fitness of individuals."""
        individuals = kwargs.get("individuals", population.individuals)
        unevaluated = [ind for ind in individuals if ind.fitness < 0]
        
        if not unevaluated:
            return []
        
        self.logger.info(f"Evaluating fitness for {len(unevaluated)} individuals")
        
        # If a custom evaluation function is provided, use it
        if self.evaluation_function and callable(self.evaluation_function):
            for individual in unevaluated:
                individual.fitness = await self.evaluation_function(individual.genotype)
        else:
            # Default simple evaluation (placeholder)
            for individual in unevaluated:
                individual.fitness = await self._default_evaluation(individual)
        
        return unevaluated
    
    async def _default_evaluation(self, individual: GeneticIndividual) -> float:
        """Default evaluation function (placeholder)."""
        # This should be replaced with a meaningful evaluation
        # based on the specific problem domain
        if not isinstance(individual.genotype, dict):
            return 0.0
        
        # Simple example: sum of values if they are numeric
        fitness = 0.0
        for value in individual.genotype.values():
            if isinstance(value, (int, float)):
                fitness += value
        
        return fitness


class PKAlphaService(ProtocolService):
    """
    Protocol-Driven Genetic Algorithm Layer (PK-Alpha) service.
    
    This service provides genetic algorithm capabilities for protocol optimization,
    algorithm building, and adaptive behavior.
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "pk_alpha")
        self.config = config or {}
        
        # Initialize populations
        self.populations: Dict[str, GeneticPopulation] = {}
        
        # Initialize operators
        self.operators = {
            GeneticOperationType.CROSSOVER: CrossoverOperator(self.config.get("crossover", {})),
            GeneticOperationType.MUTATION: MutationOperator(self.config.get("mutation", {})),
            GeneticOperationType.SELECTION: SelectionOperator(self.config.get("selection", {})),
            GeneticOperationType.EVALUATION: FitnessEvaluator(self.config.get("evaluation", {}))
        }
        
        # Evolution parameters
        self.max_generations = self.config.get("max_generations", 100)
        self.population_size = self.config.get("population_size", 100)
        self.elitism_count = self.config.get("elitism_count", 2)
        
        # State
        self.running_evolutions: Dict[str, asyncio.Task] = {}
        
        self.is_async = True
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"{__name__}.PKAlphaService.{self.component_id[:8]}")
        self.logger.info(f"PK-Alpha Service initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("genetic_algorithm", "Genetic algorithm framework for optimization")
        self.add_capability("algorithm_building", "Build algorithms through genetic programming")
        self.add_capability("synthetic_data", "Generate synthetic data for algorithm training")
        self.add_capability("distributed_evolution", "Evolve algorithms across the protocol mesh")

    # --- Population Management ---

    async def create_population(
        self,
        population_id: str = None,
        initial_individuals: List[Dict[str, Any]] = None,
        target_size: int = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new population."""
        population_id = population_id or str(uuid.uuid4())
        target_size = target_size or self.population_size
        metadata = metadata or {}
        
        async with self.lock:
            if population_id in self.populations:
                self.logger.warning(f"Population {population_id} already exists")
                return population_id
            
            population = GeneticPopulation(
                id=population_id,
                target_size=target_size,
                metadata=metadata
            )
            
            # Add initial individuals if provided
            if initial_individuals:
                for ind_data in initial_individuals:
                    individual = GeneticIndividual(
                        id=ind_data.get("id", str(uuid.uuid4())),
                        genotype=ind_data.get("genotype", {}),
                        fitness=ind_data.get("fitness", -1.0),
                        metadata=ind_data.get("metadata", {}),
                        generation=0,
                        parent_ids=[]
                    )
                    population.add_individual(individual)
            
            self.populations[population_id] = population
            self.logger.info(f"Created population {population_id} with {len(population.individuals)} initial individuals")
        
        return population_id

    async def add_individual(self, population_id: str, individual_data: Dict[str, Any]) -> Optional[str]:
        """Add an individual to a population."""
        async with self.lock:
            if population_id not in self.populations:
                self.logger.error(f"Population {population_id} not found")
                return None
            
            individual = GeneticIndividual(
                id=individual_data.get("id", str(uuid.uuid4())),
                genotype=individual_data.get("genotype", {}),
                fitness=individual_data.get("fitness", -1.0),
                metadata=individual_data.get("metadata", {}),
                generation=individual_data.get("generation", self.populations[population_id].generation),
                parent_ids=individual_data.get("parent_ids", [])
            )
            
            self.populations[population_id].add_individual(individual)
            self.logger.debug(f"Added individual {individual.id} to population {population_id}")
        
        return individual.id

    async def get_population(self, population_id: str) -> Optional[Dict[str, Any]]:
        """Get a population by ID."""
        async with self.lock:
            if population_id not in self.populations:
                self.logger.error(f"Population {population_id} not found")
                return None
            
            return self.populations[population_id].to_dict()

    async def get_individual(self, population_id: str, individual_id: str) -> Optional[Dict[str, Any]]:
        """Get an individual by ID from a population."""
        async with self.lock:
            if population_id not in self.populations:
                self.logger.error(f"Population {population_id} not found")
                return None
            
            individual = self.populations[population_id].get_individual(individual_id)
            if not individual:
                self.logger.error(f"Individual {individual_id} not found in population {population_id}")
                return None
            
            return individual.to_dict()

    # --- Evolution ---

    async def start_evolution(
        self,
        population_id: str,
        max_generations: int = None,
        evolution_config: Dict[str, Any] = None
    ) -> bool:
        """Start evolving a population."""
        async with self.lock:
            if population_id not in self.populations:
                self.logger.error(f"Population {population_id} not found")
                return False
            
            if population_id in self.running_evolutions and not self.running_evolutions[population_id].done():
                self.logger.warning(f"Evolution for population {population_id} already running")
                return True
            
            # Create and start evolution task
            task = asyncio.create_task(
                self._run_evolution(
                    population_id,
                    max_generations or self.max_generations,
                    evolution_config or {}
                )
            )
            self.running_evolutions[population_id] = task
            self.logger.info(f"Started evolution for population {population_id}")
        
        return True

    async def stop_evolution(self, population_id: str) -> bool:
        """Stop evolving a population."""
        async with self.lock:
            if population_id not in self.running_evolutions:
                self.logger.warning(f"No evolution running for population {population_id}")
                return False
            
            task = self.running_evolutions[population_id]
            if not task.done():
                task.cancel()
                self.logger.info(f"Stopped evolution for population {population_id}")
            
            self.running_evolutions.pop(population_id)
        
        return True

    async def _run_evolution(
        self,
        population_id: str,
        max_generations: int,
        config: Dict[str, Any]
    ) -> None:
        """Run the evolution process for a population."""
        try:
            self.logger.info(f"Evolution started for population {population_id}")
            
            # Get initial population
            population = None
            async with self.lock:
                if population_id in self.populations:
                    population = self.populations[population_id]
                else:
                    self.logger.error(f"Population {population_id} not found")
                    return
            
            # Initialize if needed
            if not population.individuals:
                await self._initialize_population(population, config.get("initialization", {}))
            
            # Evaluate initial population
            await self.operators[GeneticOperationType.EVALUATION].apply(population)
            
            # Main evolution loop
            for generation in range(population.generation, population.generation + max_generations):
                self.logger.info(f"Generation {generation} for population {population_id}")
                
                # Update population generation
                async with self.lock:
                    population.generation = generation
                
                # Create new generation
                new_individuals = []
                
                # Elitism: Keep best individuals
                elites = population.get_fittest(self.elitism_count)
                for elite in elites:
                    # Create copies of elites with new IDs
                    elite_copy = GeneticIndividual(
                        id=str(uuid.uuid4()),
                        genotype=elite.genotype,
                        fitness=elite.fitness,
                        metadata=elite.metadata.copy(),
                        generation=generation + 1,
                        parent_ids=[elite.id]
                    )
                    new_individuals.append(elite_copy)
                
                # Fill rest of population with offspring
                while len(new_individuals) < population.target_size:
                    # Selection
                    parents = await self.operators[GeneticOperationType.SELECTION].apply(
                        population, num_to_select=2
                    )
                    
                    if len(parents) < 2:
                        self.logger.warning("Not enough parents selected")
                        break
                    
                    # Crossover
                    offspring = await self.operators[GeneticOperationType.CROSSOVER].apply(
                        population, parents=parents
                    )
                    
                    # Mutation
                    for ind in offspring:
                        if random.random() < self.operators[GeneticOperationType.MUTATION].mutation_rate:
                            mutated = await self.operators[GeneticOperationType.MUTATION].apply(
                                population, individuals=[ind]
                            )
                            if mutated:
                                ind = mutated[0]
                    
                    new_individuals.extend(offspring)
                
                # Trim to target size if needed
                if len(new_individuals) > population.target_size:
                    new_individuals = new_individuals[:population.target_size]
                
                # Update population
                async with self.lock:
                    population.individuals = new_individuals
                
                # Evaluate new individuals
                await self.operators[GeneticOperationType.EVALUATION].apply(population)
                
                # Check for termination conditions
                best_fitness = population.get_fittest(1)[0].fitness if population.individuals else -1
                self.logger.info(f"Generation {generation} best fitness: {best_fitness}")
                
                # Optional: Check for convergence or other termination conditions
                
                # Yield to allow other tasks to run
                await asyncio.sleep(0)
            
            self.logger.info(f"Evolution completed for population {population_id} after {max_generations} generations")
        
        except asyncio.CancelledError:
            self.logger.info(f"Evolution for population {population_id} was cancelled")
        except Exception as e:
            self.logger.exception(f"Error in evolution for population {population_id}: {e}")

    async def _initialize_population(self, population: GeneticPopulation, config: Dict[str, Any]) -> None:
        """Initialize a population with random individuals."""
        self.logger.info(f"Initializing population {population.id} with {population.target_size} individuals")
        
        # Get genotype template from config
        genotype_template = config.get("genotype_template", {})
        
        # Create random individuals
        for _ in range(population.target_size):
            # Generate random genotype based on template
            genotype = await self._generate_random_genotype(genotype_template)
            
            # Create individual
            individual = GeneticIndividual(
                id=str(uuid.uuid4()),
                genotype=genotype,
                generation=population.generation,
                parent_ids=[]
            )
            
            population.add_individual(individual)
        
        self.logger.info(f"Population {population.id} initialized with {len(population.individuals)} individuals")

    async def _generate_random_genotype(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a random genotype based on a template."""
        genotype = {}
        
        for key, value_spec in template.items():
            if isinstance(value_spec, dict) and "type" in value_spec:
                value_type = value_spec["type"]
                
                if value_type == "int":
                    min_val = value_spec.get("min", 0)
                    max_val = value_spec.get("max", 100)
                    genotype[key] = random.randint(min_val, max_val)
                
                elif value_type == "float":
                    min_val = value_spec.get("min", 0.0)
                    max_val = value_spec.get("max", 1.0)
                    genotype[key] = random.uniform(min_val, max_val)
                
                elif value_type == "bool":
                    genotype[key] = random.choice([True, False])
                
                elif value_type == "choice":
                    options = value_spec.get("options", [])
                    if options:
                        genotype[key] = random.choice(options)
                    else:
                        genotype[key] = None
                
                elif value_type == "dict":
                    sub_template = value_spec.get("template", {})
                    genotype[key] = await self._generate_random_genotype(sub_template)
                
                elif value_type == "list":
                    item_template = value_spec.get("item_template", {})
                    min_len = value_spec.get("min_length", 0)
                    max_len = value_spec.get("max_length", 5)
                    length = random.randint(min_len, max_len)
                    
                    if isinstance(item_template, dict):
                        genotype[key] = [
                            await self._generate_random_genotype(item_template)
                            for _ in range(length)
                        ]
                    else:
                        genotype[key] = [item_template for _ in range(length)]
            
            else:
                # Use value directly as a constant
                genotype[key] = value_spec
        
        return genotype

    # --- Synthetic Data Generation ---

    async def generate_synthetic_data(
        self,
        data_type: str,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate synthetic data for algorithm training."""
        config = config or {}
        
        if data_type == "time_series":
            return await self._generate_time_series(config)
        elif data_type == "categorical":
            return await self._generate_categorical(config)
        elif data_type == "numerical":
            return await self._generate_numerical(config)
        else:
            self.logger.error(f"Unknown data type: {data_type}")
            return {"error": f"Unknown data type: {data_type}"}

    async def _generate_time_series(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate synthetic time series data."""
        length = config.get("length", 100)
        num_features = config.get("num_features", 1)
        noise_level = config.get("noise_level", 0.1)
        
        # Generate time points
        time_points = np.linspace(0, 10, length)
        
        # Generate features
        features = []
        for i in range(num_features):
            # Base signal (sine wave with random frequency and phase)
            freq = random.uniform(0.5, 2.0)
            phase = random.uniform(0, 2 * np.pi)
            amplitude = random.uniform(0.5, 2.0)
            
            signal = amplitude * np.sin(freq * time_points + phase)
            
            # Add noise
            noise = np.random.normal(0, noise_level, length)
            feature = signal + noise
            
            features.append(feature.tolist())
        
        return {
            "type": "time_series",
            "time_points": time_points.tolist(),
            "features": features,
            "metadata": {
                "length": length,
                "num_features": num_features,
                "noise_level": noise_level
            }
        }

    async def _generate_categorical(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate synthetic categorical data."""
        num_samples = config.get("num_samples", 100)
        categories = config.get("categories", ["A", "B", "C"])
        probabilities = config.get("probabilities", None)
        
        if probabilities is None:
            # Equal probabilities
            probabilities = [1.0 / len(categories) for _ in categories]
        
        # Generate samples
        samples = np.random.choice(categories, size=num_samples, p=probabilities).tolist()
        
        return {
            "type": "categorical",
            "samples": samples,
            "metadata": {
                "num_samples": num_samples,
                "categories": categories,
                "probabilities": probabilities
            }
        }

    async def _generate_numerical(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate synthetic numerical data."""
        num_samples = config.get("num_samples", 100)
        num_features = config.get("num_features", 2)
        distribution = config.get("distribution", "normal")
        
        # Generate features
        features = []
        for i in range(num_features):
            if distribution == "normal":
                mean = config.get("mean", 0.0)
                std = config.get("std", 1.0)
                feature = np.random.normal(mean, std, num_samples).tolist()
            elif distribution == "uniform":
                min_val = config.get("min", 0.0)
                max_val = config.get("max", 1.0)
                feature = np.random.uniform(min_val, max_val, num_samples).tolist()
            else:
                self.logger.error(f"Unknown distribution: {distribution}")
                feature = [0.0] * num_samples
            
            features.append(feature)
        
        # Transpose to get samples as rows
        samples = [[features[j][i] for j in range(num_features)] for i in range(num_samples)]
        
        return {
            "type": "numerical",
            "samples": samples,
            "metadata": {
                "num_samples": num_samples,
                "num_features": num_features,
                "distribution": distribution
            }
        }

    # --- AlphaEvolve Integration ---

    async def create_alphaevolve_task(
        self,
        task_type: str,
        task_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a task for AlphaEvolve integration."""
        # This is a placeholder for AlphaEvolve integration
        # In a real implementation, this would interface with AlphaEvolve
        
        task_id = str(uuid.uuid4())
        task_config = task_config or {}
        
        self.logger.info(f"Created AlphaEvolve task {task_id} of type {task_type}")
        
        return {
            "task_id": task_id,
            "task_type": task_type,
            "status": "created",
            "config": task_config
        }

    # --- ProtocolService Methods ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "create_population":
                population_id = await self.create_population(
                    population_id=msg_obj.params.get("population_id"),
                    initial_individuals=msg_obj.params.get("initial_individuals"),
                    target_size=msg_obj.params.get("target_size"),
                    metadata=msg_obj.params.get("metadata")
                )
                response_payload = {"population_id": population_id}
            
            elif msg_obj.command == "add_individual":
                params = msg_obj.params
                if "population_id" in params and "individual" in params:
                    individual_id = await self.add_individual(params["population_id"], params["individual"])
                    if individual_id:
                        response_payload = {"individual_id": individual_id}
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Failed to add individual"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing population_id or individual"}
            
            elif msg_obj.command == "start_evolution":
                params = msg_obj.params
                if "population_id" in params:
                    success = await self.start_evolution(
                        params["population_id"],
                        params.get("max_generations"),
                        params.get("evolution_config")
                    )
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing population_id"}
            
            elif msg_obj.command == "stop_evolution":
                params = msg_obj.params
                if "population_id" in params:
                    success = await self.stop_evolution(params["population_id"])
                    response_payload = {"success": success}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing population_id"}
            
            elif msg_obj.command == "generate_synthetic_data":
                params = msg_obj.params
                if "data_type" in params:
                    data = await self.generate_synthetic_data(
                        params["data_type"],
                        params.get("config")
                    )
                    response_payload = data
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing data_type"}
            
            elif msg_obj.command == "create_alphaevolve_task":
                params = msg_obj.params
                if "task_type" in params:
                    task = await self.create_alphaevolve_task(
                        params["task_type"],
                        params.get("task_config")
                    )
                    response_payload = task
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing task_type"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_population":
                params = msg_obj.params
                if "population_id" in params:
                    population = await self.get_population(params["population_id"])
                    if population:
                        response_payload = population
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Population not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing population_id"}
            
            elif msg_obj.query == "get_individual":
                params = msg_obj.params
                if "population_id" in params and "individual_id" in params:
                    individual = await self.get_individual(params["population_id"], params["individual_id"])
                    if individual:
                        response_payload = individual
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Individual not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing population_id or individual_id"}
            
            elif msg_obj.query == "list_populations":
                async with self.lock:
                    response_payload = {
                        "populations": [
                            {
                                "id": pop_id,
                                "generation": pop.generation,
                                "size": len(pop.individuals),
                                "target_size": pop.target_size,
                                "best_fitness": max([ind.fitness for ind in pop.individuals]) if pop.individuals else -1
                            }
                            for pop_id, pop in self.populations.items()
                        ]
                    }
            
            elif msg_obj.query == "get_evolution_status":
                params = msg_obj.params
                if "population_id" in params:
                    population_id = params["population_id"]
                    async with self.lock:
                        is_running = (
                            population_id in self.running_evolutions and
                            not self.running_evolutions[population_id].done()
                        )
                        pop = self.populations.get(population_id)
                        if pop:
                            response_payload = {
                                "population_id": population_id,
                                "is_running": is_running,
                                "generation": pop.generation,
                                "size": len(pop.individuals),
                                "best_fitness": max([ind.fitness for ind in pop.individuals]) if pop.individuals else -1
                            }
                        else:
                            status = MessageStatus.FAILED
                            response_payload = {"error": "Population not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing population_id"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        else:
            # Ignore other message types
            return None

        # Create response
        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message (synchronous wrapper)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check."""
        async with self.lock:
            num_populations = len(self.populations)
            num_running_evolutions = sum(
                1 for task in self.running_evolutions.values()
                if not task.done()
            )
            total_individuals = sum(
                len(pop.individuals) for pop in self.populations.values()
            )
        
        return {
            "status": "healthy",
            "populations": num_populations,
            "running_evolutions": num_running_evolutions,
            "total_individuals": total_individuals
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
