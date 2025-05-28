"""
Breeding Strategy Agent for the Overseer System.

This module provides comprehensive breeding strategy capabilities for the Overseer System,
enabling the recombination of traits from high-performing capsules in similar industries.

The Breeding Strategy Agent is a critical component of the Capsule Evolution phase,
providing mechanisms for genetic-inspired evolution of capsules.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import os
import time
import uuid
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any, Set

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from pydantic import BaseModel, Field, validator

# Import MCP/A2A integration
from ..mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from ..a2a_integration.a2a_protocol_bridge import A2AProtocolBridge

# Import event bus
from ..event_bus.kafka_client import KafkaProducer, KafkaConsumer

# Import related components
from .capsule_genotype_manager import CapsuleGenotype, CapsuleGenotypeManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("breeding_strategy_agent")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="breeding-strategy-agent"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="breeding-strategy-agent",
    auto_offset_reset="earliest"
)

# Initialize Genotype Manager
genotype_manager = CapsuleGenotypeManager()

# Data models
class BreedingStrategy(BaseModel):
    """Model for breeding strategy definition."""
    strategy_id: str = Field(..., description="Unique strategy identifier")
    name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    industry_focus: List[str] = Field(default_factory=list, description="Industry focus")
    capability_focus: List[str] = Field(default_factory=list, description="Capability focus")
    trait_weights: Dict[str, float] = Field(default_factory=dict, description="Trait importance weights")
    crossover_rate: float = Field(0.7, description="Crossover rate (0.0 to 1.0)")
    mutation_rate: float = Field(0.1, description="Mutation rate (0.0 to 1.0)")
    selection_criteria: str = Field("fitness", description="Selection criteria (fitness, diversity, hybrid)")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class BreedingRequest(BaseModel):
    """Model for breeding requests."""
    request_id: str = Field(..., description="Unique request identifier")
    strategy_id: str = Field(..., description="Strategy ID to use")
    parent_genotype_ids: List[str] = Field(..., description="Parent genotype IDs")
    offspring_count: int = Field(1, description="Number of offspring to generate")
    timestamp: datetime = Field(default_factory=datetime.now, description="Request timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class BreedingResult(BaseModel):
    """Model for breeding results."""
    result_id: str = Field(..., description="Unique result identifier")
    request_id: str = Field(..., description="Request ID")
    strategy_id: str = Field(..., description="Strategy ID used")
    parent_genotype_ids: List[str] = Field(..., description="Parent genotype IDs")
    offspring_genotype_ids: List[str] = Field(..., description="Offspring genotype IDs")
    timestamp: datetime = Field(default_factory=datetime.now, description="Result timestamp")
    success: bool = Field(True, description="Whether breeding was successful")
    error_message: Optional[str] = Field(None, description="Error message if unsuccessful")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class OffspringEvaluation(BaseModel):
    """Model for offspring evaluation."""
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    genotype_id: str = Field(..., description="Genotype ID")
    fitness_score: float = Field(..., description="Fitness score")
    evaluation_metrics: Dict[str, float] = Field(default_factory=dict, description="Evaluation metrics")
    timestamp: datetime = Field(default_factory=datetime.now, description="Evaluation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# In-memory storage (would be replaced with database in production)
breeding_strategies = {}
breeding_requests = {}
breeding_results = {}
offspring_evaluations = {}

class StrategyDefinition:
    """
    Manages breeding strategy definitions.
    
    This class provides methods for creating, retrieving, updating, and deleting
    breeding strategies.
    """
    
    def __init__(self):
        """Initialize the Strategy Definition manager."""
        logger.info("Strategy Definition manager initialized")
    
    def create_strategy(self, strategy: BreedingStrategy) -> str:
        """
        Create a new breeding strategy.
        
        Args:
            strategy: The strategy to create
            
        Returns:
            str: The strategy ID
        """
        # Store the strategy
        breeding_strategies[strategy.strategy_id] = strategy.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-breeding-strategies",
            key=strategy.strategy_id,
            value=json.dumps({
                "action": "create",
                "strategy_id": strategy.strategy_id,
                "name": strategy.name
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "breeding_strategy_created",
            "strategy_id": strategy.strategy_id,
            "name": strategy.name
        }
        mcp_bridge.send_context_update("breeding_strategy_agent", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="breeding_strategy_agent",
            message={
                "type": "breeding_strategy_created",
                "strategy_id": strategy.strategy_id,
                "name": strategy.name
            }
        )
        
        return strategy.strategy_id
    
    def get_strategy(self, strategy_id: str) -> Optional[BreedingStrategy]:
        """
        Get a breeding strategy by ID.
        
        Args:
            strategy_id: The strategy ID
            
        Returns:
            Optional[BreedingStrategy]: The strategy, or None if not found
        """
        if strategy_id not in breeding_strategies:
            return None
        
        return BreedingStrategy(**breeding_strategies[strategy_id])
    
    def update_strategy(self, strategy_id: str, strategy: BreedingStrategy) -> bool:
        """
        Update a breeding strategy.
        
        Args:
            strategy_id: The strategy ID to update
            strategy: The updated strategy
            
        Returns:
            bool: True if successful, False if strategy not found
        """
        if strategy_id not in breeding_strategies:
            return False
        
        # Update the strategy
        strategy.updated_at = datetime.now()
        breeding_strategies[strategy_id] = strategy.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-breeding-strategies",
            key=strategy_id,
            value=json.dumps({
                "action": "update",
                "strategy_id": strategy_id,
                "name": strategy.name
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "breeding_strategy_updated",
            "strategy_id": strategy_id,
            "name": strategy.name
        }
        mcp_bridge.send_context_update("breeding_strategy_agent", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="breeding_strategy_agent",
            message={
                "type": "breeding_strategy_updated",
                "strategy_id": strategy_id,
                "name": strategy.name
            }
        )
        
        return True
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """
        Delete a breeding strategy.
        
        Args:
            strategy_id: The strategy ID to delete
            
        Returns:
            bool: True if successful, False if strategy not found
        """
        if strategy_id not in breeding_strategies:
            return False
        
        # Get strategy name before deletion
        strategy_name = breeding_strategies[strategy_id]["name"]
        
        # Delete the strategy
        del breeding_strategies[strategy_id]
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-breeding-strategies",
            key=strategy_id,
            value=json.dumps({
                "action": "delete",
                "strategy_id": strategy_id,
                "name": strategy_name
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "breeding_strategy_deleted",
            "strategy_id": strategy_id,
            "name": strategy_name
        }
        mcp_bridge.send_context_update("breeding_strategy_agent", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="breeding_strategy_agent",
            message={
                "type": "breeding_strategy_deleted",
                "strategy_id": strategy_id,
                "name": strategy_name
            }
        )
        
        return True
    
    def list_strategies(
        self,
        name_filter: Optional[str] = None,
        industry_filter: Optional[str] = None,
        capability_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[BreedingStrategy]:
        """
        List breeding strategies, optionally filtered.
        
        Args:
            name_filter: Optional filter for strategy name (case-insensitive substring match)
            industry_filter: Optional filter for industry focus
            capability_filter: Optional filter for capability focus
            limit: Maximum number of strategies to return
            
        Returns:
            List[BreedingStrategy]: List of matching strategies
        """
        results = []
        
        for strategy_dict in breeding_strategies.values():
            # Apply filters
            if name_filter and name_filter.lower() not in strategy_dict["name"].lower():
                continue
            
            if industry_filter and industry_filter not in strategy_dict["industry_focus"]:
                continue
            
            if capability_filter and capability_filter not in strategy_dict["capability_focus"]:
                continue
            
            results.append(BreedingStrategy(**strategy_dict))
        
        # Sort by name
        results.sort(key=lambda s: s.name)
        
        # Apply limit
        return results[:limit]

class TraitRecombiner:
    """
    Recombines traits from parent genotypes to create offspring.
    
    This class provides methods for performing crossover and mutation
    operations on genotypes.
    """
    
    def __init__(self):
        """Initialize the Trait Recombiner."""
        logger.info("Trait Recombiner initialized")
    
    def recombine_traits(
        self,
        parent_genotypes: List[CapsuleGenotype],
        strategy: BreedingStrategy
    ) -> Dict[str, Any]:
        """
        Recombine traits from parent genotypes according to the breeding strategy.
        
        Args:
            parent_genotypes: List of parent genotypes
            strategy: Breeding strategy to use
            
        Returns:
            Dict[str, Any]: Recombined traits
        """
        if len(parent_genotypes) < 2:
            raise ValueError("At least two parent genotypes are required for recombination")
        
        # Get all trait keys from parents
        all_trait_keys = set()
        for parent in parent_genotypes:
            all_trait_keys.update(parent.traits.keys())
        
        # Initialize offspring traits
        offspring_traits = {}
        
        # Apply crossover for each trait
        for trait_key in all_trait_keys:
            # Get parents that have this trait
            parents_with_trait = [p for p in parent_genotypes if trait_key in p.traits]
            
            if not parents_with_trait:
                continue
            
            # Determine if crossover occurs for this trait
            if random.random() < strategy.crossover_rate:
                # Select a parent based on trait weights if available
                if trait_key in strategy.trait_weights:
                    # Weight selection by trait weights and fitness score
                    weights = []
                    for parent in parents_with_trait:
                        weight = parent.fitness_score
                        if trait_key in strategy.trait_weights:
                            weight *= strategy.trait_weights[trait_key]
                        weights.append(weight)
                    
                    # Normalize weights
                    total_weight = sum(weights)
                    if total_weight > 0:
                        weights = [w / total_weight for w in weights]
                    else:
                        weights = [1.0 / len(parents_with_trait)] * len(parents_with_trait)
                    
                    # Select parent based on weights
                    selected_parent = random.choices(parents_with_trait, weights=weights, k=1)[0]
                else:
                    # Random selection
                    selected_parent = random.choice(parents_with_trait)
                
                # Copy trait from selected parent
                offspring_traits[trait_key] = selected_parent.traits[trait_key]
            
            # Apply mutation if it occurs
            if random.random() < strategy.mutation_rate:
                offspring_traits[trait_key] = self._mutate_trait(
                    trait_key, 
                    offspring_traits.get(trait_key),
                    [p.traits.get(trait_key) for p in parent_genotypes if trait_key in p.traits]
                )
        
        return offspring_traits
    
    def _mutate_trait(self, trait_key: str, trait_value: Any, parent_values: List[Any]) -> Any:
        """
        Mutate a trait value.
        
        Args:
            trait_key: The trait key
            trait_value: The current trait value
            parent_values: List of parent trait values
            
        Returns:
            Any: The mutated trait value
        """
        if trait_value is None:
            # If no current value, use a parent value
            return random.choice(parent_values) if parent_values else None
        
        # Mutation depends on the type of value
        if isinstance(trait_value, bool):
            # Flip boolean
            return not trait_value
        
        elif isinstance(trait_value, int):
            # Adjust integer by small amount
            adjustment = random.choice([-2, -1, 1, 2])
            return trait_value + adjustment
        
        elif isinstance(trait_value, float):
            # Adjust float by percentage
            adjustment = random.uniform(-0.2, 0.2)  # -20% to +20%
            return trait_value * (1.0 + adjustment)
        
        elif isinstance(trait_value, str):
            # For strings, either:
            # 1. Use a parent value
            # 2. Add a suffix
            # 3. Remove a character
            mutation_type = random.choice(["parent", "suffix", "remove"])
            
            if mutation_type == "parent" and parent_values:
                return random.choice(parent_values)
            elif mutation_type == "suffix":
                suffixes = ["_v2", "_enhanced", "_modified", "_evolved"]
                return trait_value + random.choice(suffixes)
            elif mutation_type == "remove" and len(trait_value) > 1:
                pos = random.randint(0, len(trait_value) - 1)
                return trait_value[:pos] + trait_value[pos+1:]
            else:
                return trait_value
        
        elif isinstance(trait_value, list):
            # For lists, either:
            # 1. Add an element from a parent
            # 2. Remove an element
            # 3. Shuffle elements
            if not trait_value:
                # Empty list, try to add from parents
                for parent_value in parent_values:
                    if isinstance(parent_value, list) and parent_value:
                        return [random.choice(parent_value)]
                return trait_value
            
            mutation_type = random.choice(["add", "remove", "shuffle"])
            
            if mutation_type == "add":
                # Add element from parent if available
                for parent_value in parent_values:
                    if isinstance(parent_value, list) and parent_value:
                        element = random.choice(parent_value)
                        if element not in trait_value:
                            return trait_value + [element]
                return trait_value
            
            elif mutation_type == "remove" and len(trait_value) > 1:
                # Remove random element
                result = trait_value.copy()
                result.pop(random.randint(0, len(result) - 1))
                return result
            
            elif mutation_type == "shuffle":
                # Shuffle elements
                result = trait_value.copy()
                random.shuffle(result)
                return result
            
            else:
                return trait_value
        
        elif isinstance(trait_value, dict):
            # For dicts, either:
            # 1. Add a key-value from a parent
            # 2. Remove a key-value
            # 3. Modify a value
            if not trait_value:
                # Empty dict, try to add from parents
                for parent_value in parent_values:
                    if isinstance(parent_value, dict) and parent_value:
                        key = random.choice(list(parent_value.keys()))
                        return {key: parent_value[key]}
                return trait_value
            
            mutation_type = random.choice(["add", "remove", "modify"])
            
            if mutation_type == "add":
                # Add key-value from parent if available
                for parent_value in parent_values:
                    if isinstance(parent_value, dict) and parent_value:
                        keys_not_in_trait = [k for k in parent_value.keys() if k not in trait_value]
                        if keys_not_in_trait:
                            key = random.choice(keys_not_in_trait)
                            result = trait_value.copy()
                            result[key] = parent_value[key]
                            return result
                return trait_value
            
            elif mutation_type == "remove" and len(trait_value) > 1:
                # Remove random key
                result = trait_value.copy()
                key = random.choice(list(result.keys()))
                del result[key]
                return result
            
            elif mutation_type == "modify" and trait_value:
                # Modify a value
                result = trait_value.copy()
                key = random.choice(list(result.keys()))
                
                # Find this key in parents
                parent_key_values = []
                for parent_value in parent_values:
                    if isinstance(parent_value, dict) and key in parent_value:
                        parent_key_values.append(parent_value[key])
                
                if parent_key_values:
                    # Use a parent value
                    result[key] = random.choice(parent_key_values)
                else:
                    # Try to mutate the value itself
                    result[key] = self._mutate_trait(key, result[key], [])
                
                return result
            
            else:
                return trait_value
        
        else:
            # For other types, return as is
            return trait_value
    
    def create_offspring_genotype(
        self,
        parent_genotypes: List[CapsuleGenotype],
        strategy: BreedingStrategy
    ) -> CapsuleGenotype:
        """
        Create a new offspring genotype by recombining traits from parents.
        
        Args:
            parent_genotypes: List of parent genotypes
            strategy: Breeding strategy to use
            
        Returns:
            CapsuleGenotype: The offspring genotype
        """
        # Generate a unique ID for the offspring
        genotype_id = f"genotype-{uuid.uuid4()}"
        
        # Recombine traits
        offspring_traits = self.recombine_traits(parent_genotypes, strategy)
        
        # Combine industry and capability tags
        industry_tags = set()
        capability_tags = set()
        
        for parent in parent_genotypes:
            industry_tags.update(parent.industry_tags)
            capability_tags.update(parent.capability_tags)
        
        # Filter by strategy focus if specified
        if strategy.industry_focus:
            industry_tags = {tag for tag in industry_tags if tag in strategy.industry_focus}
        
        if strategy.capability_focus:
            capability_tags = {tag for tag in capability_tags if tag in strategy.capability_focus}
        
        # Create name and description
        parent_names = [p.name for p in parent_genotypes]
        name = f"Bred from {' × '.join(parent_names)}"
        
        description = f"Offspring genotype created by breeding strategy '{strategy.name}'. "
        description += f"Parents: {', '.join(parent_names)}."
        
        # Create the offspring genotype
        offspring = CapsuleGenotype(
            genotype_id=genotype_id,
            name=name,
            description=description,
            version="1.0.0",
            traits=offspring_traits,
            parent_genotypes=[p.genotype_id for p in parent_genotypes],
            industry_tags=list(industry_tags),
            capability_tags=list(capability_tags),
            fitness_score=0.0,  # Will be evaluated later
            metadata={
                "breeding_strategy_id": strategy.strategy_id,
                "breeding_timestamp": datetime.now().isoformat()
            }
        )
        
        return offspring

class OffspringEvaluator:
    """
    Evaluates offspring genotypes for fitness and performance.
    
    This class provides methods for evaluating the fitness of bred capsules
    and generating evaluation reports.
    """
    
    def __init__(self):
        """Initialize the Offspring Evaluator."""
        logger.info("Offspring Evaluator initialized")
    
    def evaluate_offspring(
        self,
        offspring: CapsuleGenotype,
        parent_genotypes: List[CapsuleGenotype],
        strategy: BreedingStrategy
    ) -> OffspringEvaluation:
        """
        Evaluate an offspring genotype.
        
        Args:
            offspring: The offspring genotype to evaluate
            parent_genotypes: The parent genotypes
            strategy: The breeding strategy used
            
        Returns:
            OffspringEvaluation: The evaluation result
        """
        evaluation_id = f"eval-{uuid.uuid4()}"
        
        # Calculate base fitness score
        base_fitness = genotype_manager.calculate_fitness_score(offspring)
        
        # Calculate additional metrics
        metrics = self._calculate_evaluation_metrics(offspring, parent_genotypes, strategy)
        
        # Adjust fitness based on metrics
        adjusted_fitness = base_fitness
        
        if "trait_coverage" in metrics:
            adjusted_fitness += 0.1 * metrics["trait_coverage"]
        
        if "trait_diversity" in metrics:
            adjusted_fitness += 0.1 * metrics["trait_diversity"]
        
        if "parent_improvement" in metrics:
            adjusted_fitness += 0.2 * metrics["parent_improvement"]
        
        # Ensure fitness is in 0.0 to 1.0 range
        fitness_score = max(0.0, min(1.0, adjusted_fitness))
        
        # Create evaluation result
        evaluation = OffspringEvaluation(
            evaluation_id=evaluation_id,
            genotype_id=offspring.genotype_id,
            fitness_score=fitness_score,
            evaluation_metrics=metrics,
            metadata={
                "breeding_strategy_id": strategy.strategy_id,
                "parent_genotype_ids": [p.genotype_id for p in parent_genotypes]
            }
        )
        
        # Store the evaluation
        offspring_evaluations[evaluation_id] = evaluation.dict()
        
        # Update offspring fitness score
        offspring.fitness_score = fitness_score
        genotype_manager.update_genotype(offspring.genotype_id, offspring)
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-offspring-evaluations",
            key=evaluation_id,
            value=json.dumps({
                "evaluation_id": evaluation_id,
                "genotype_id": offspring.genotype_id,
                "fitness_score": fitness_score
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "offspring_evaluated",
            "evaluation_id": evaluation_id,
            "genotype_id": offspring.genotype_id,
            "fitness_score": fitness_score
        }
        mcp_bridge.send_context_update("breeding_strategy_agent", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="breeding_strategy_agent",
            message={
                "type": "offspring_evaluated",
                "evaluation_id": evaluation_id,
                "genotype_id": offspring.genotype_id,
                "fitness_score": fitness_score
            }
        )
        
        return evaluation
    
    def _calculate_evaluation_metrics(
        self,
        offspring: CapsuleGenotype,
        parent_genotypes: List[CapsuleGenotype],
        strategy: BreedingStrategy
    ) -> Dict[str, float]:
        """
        Calculate evaluation metrics for an offspring.
        
        Args:
            offspring: The offspring genotype
            parent_genotypes: The parent genotypes
            strategy: The breeding strategy used
            
        Returns:
            Dict[str, float]: Evaluation metrics
        """
        metrics = {}
        
        # Calculate trait coverage
        all_trait_keys = set()
        for parent in parent_genotypes:
            all_trait_keys.update(parent.traits.keys())
        
        if all_trait_keys:
            trait_coverage = len(offspring.traits) / len(all_trait_keys)
            metrics["trait_coverage"] = trait_coverage
        else:
            metrics["trait_coverage"] = 0.0
        
        # Calculate trait diversity
        if offspring.traits:
            # Count unique trait values
            unique_values = set()
            for value in offspring.traits.values():
                # Convert to string for set membership
                unique_values.add(str(value))
            
            trait_diversity = len(unique_values) / len(offspring.traits)
            metrics["trait_diversity"] = trait_diversity
        else:
            metrics["trait_diversity"] = 0.0
        
        # Calculate improvement over parents
        parent_fitness_scores = [p.fitness_score for p in parent_genotypes]
        if parent_fitness_scores:
            avg_parent_fitness = sum(parent_fitness_scores) / len(parent_fitness_scores)
            max_parent_fitness = max(parent_fitness_scores)
            
            # Improvement over average
            if avg_parent_fitness > 0:
                improvement_over_avg = (offspring.fitness_score - avg_parent_fitness) / avg_parent_fitness
                metrics["improvement_over_avg"] = improvement_over_avg
            else:
                metrics["improvement_over_avg"] = 0.0
            
            # Improvement over best parent
            if max_parent_fitness > 0:
                improvement_over_best = (offspring.fitness_score - max_parent_fitness) / max_parent_fitness
                metrics["improvement_over_best"] = improvement_over_best
            else:
                metrics["improvement_over_best"] = 0.0
            
            # Overall parent improvement score
            parent_improvement = 0.7 * metrics["improvement_over_avg"] + 0.3 * metrics["improvement_over_best"]
            metrics["parent_improvement"] = parent_improvement
        
        # Calculate strategy alignment
        strategy_alignment = 0.0
        alignment_count = 0
        
        # Industry focus alignment
        if strategy.industry_focus and offspring.industry_tags:
            industry_overlap = len(set(strategy.industry_focus) & set(offspring.industry_tags))
            industry_alignment = industry_overlap / len(strategy.industry_focus) if strategy.industry_focus else 0.0
            strategy_alignment += industry_alignment
            alignment_count += 1
        
        # Capability focus alignment
        if strategy.capability_focus and offspring.capability_tags:
            capability_overlap = len(set(strategy.capability_focus) & set(offspring.capability_tags))
            capability_alignment = capability_overlap / len(strategy.capability_focus) if strategy.capability_focus else 0.0
            strategy_alignment += capability_alignment
            alignment_count += 1
        
        # Trait weights alignment
        if strategy.trait_weights and offspring.traits:
            weighted_traits = set(strategy.trait_weights.keys()) & set(offspring.traits.keys())
            trait_weight_alignment = len(weighted_traits) / len(strategy.trait_weights) if strategy.trait_weights else 0.0
            strategy_alignment += trait_weight_alignment
            alignment_count += 1
        
        if alignment_count > 0:
            metrics["strategy_alignment"] = strategy_alignment / alignment_count
        else:
            metrics["strategy_alignment"] = 0.0
        
        return metrics
    
    def get_evaluation(self, evaluation_id: str) -> Optional[OffspringEvaluation]:
        """
        Get an evaluation by ID.
        
        Args:
            evaluation_id: The evaluation ID
            
        Returns:
            Optional[OffspringEvaluation]: The evaluation, or None if not found
        """
        if evaluation_id not in offspring_evaluations:
            return None
        
        return OffspringEvaluation(**offspring_evaluations[evaluation_id])
    
    def list_evaluations(
        self,
        genotype_id: Optional[str] = None,
        min_fitness: Optional[float] = None,
        max_fitness: Optional[float] = None,
        limit: int = 100
    ) -> List[OffspringEvaluation]:
        """
        List evaluations, optionally filtered.
        
        Args:
            genotype_id: Optional filter for genotype ID
            min_fitness: Optional minimum fitness score
            max_fitness: Optional maximum fitness score
            limit: Maximum number of evaluations to return
            
        Returns:
            List[OffspringEvaluation]: List of matching evaluations
        """
        results = []
        
        for eval_dict in offspring_evaluations.values():
            # Apply filters
            if genotype_id and eval_dict["genotype_id"] != genotype_id:
                continue
            
            if min_fitness is not None and eval_dict["fitness_score"] < min_fitness:
                continue
            
            if max_fitness is not None and eval_dict["fitness_score"] > max_fitness:
                continue
            
            results.append(OffspringEvaluation(**eval_dict))
        
        # Sort by fitness score (highest first)
        results.sort(key=lambda e: e.fitness_score, reverse=True)
        
        # Apply limit
        return results[:limit]

class BreedingReporter:
    """
    Generates reports on breeding outcomes.
    
    This class provides methods for generating reports on breeding results,
    including success rates, fitness improvements, and trait distributions.
    """
    
    def __init__(self):
        """Initialize the Breeding Reporter."""
        logger.info("Breeding Reporter initialized")
    
    def generate_breeding_report(
        self,
        result: BreedingResult,
        evaluations: List[OffspringEvaluation],
        parent_genotypes: List[CapsuleGenotype],
        offspring_genotypes: List[CapsuleGenotype],
        strategy: BreedingStrategy
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive report on a breeding result.
        
        Args:
            result: The breeding result
            evaluations: List of offspring evaluations
            parent_genotypes: List of parent genotypes
            offspring_genotypes: List of offspring genotypes
            strategy: The breeding strategy used
            
        Returns:
            Dict[str, Any]: The breeding report
        """
        # Basic information
        report = {
            "result_id": result.result_id,
            "strategy_name": strategy.name,
            "parent_count": len(parent_genotypes),
            "offspring_count": len(offspring_genotypes),
            "timestamp": result.timestamp.isoformat()
        }
        
        # Parent information
        parent_info = []
        for parent in parent_genotypes:
            parent_info.append({
                "genotype_id": parent.genotype_id,
                "name": parent.name,
                "fitness_score": parent.fitness_score,
                "trait_count": len(parent.traits),
                "industry_tags": parent.industry_tags,
                "capability_tags": parent.capability_tags
            })
        
        report["parents"] = parent_info
        
        # Offspring information
        offspring_info = []
        for i, offspring in enumerate(offspring_genotypes):
            # Find corresponding evaluation
            evaluation = next((e for e in evaluations if e.genotype_id == offspring.genotype_id), None)
            
            offspring_data = {
                "genotype_id": offspring.genotype_id,
                "name": offspring.name,
                "fitness_score": offspring.fitness_score,
                "trait_count": len(offspring.traits),
                "industry_tags": offspring.industry_tags,
                "capability_tags": offspring.capability_tags
            }
            
            if evaluation:
                offspring_data["evaluation_metrics"] = evaluation.evaluation_metrics
            
            offspring_info.append(offspring_data)
        
        report["offspring"] = offspring_info
        
        # Calculate success metrics
        if parent_genotypes and offspring_genotypes:
            # Average fitness
            avg_parent_fitness = sum(p.fitness_score for p in parent_genotypes) / len(parent_genotypes)
            avg_offspring_fitness = sum(o.fitness_score for o in offspring_genotypes) / len(offspring_genotypes)
            
            # Best fitness
            best_parent_fitness = max(p.fitness_score for p in parent_genotypes)
            best_offspring_fitness = max(o.fitness_score for o in offspring_genotypes)
            
            # Improvement rates
            avg_improvement = (avg_offspring_fitness - avg_parent_fitness) / avg_parent_fitness if avg_parent_fitness > 0 else 0
            best_improvement = (best_offspring_fitness - best_parent_fitness) / best_parent_fitness if best_parent_fitness > 0 else 0
            
            # Success rate (offspring with higher fitness than average parent)
            success_count = sum(1 for o in offspring_genotypes if o.fitness_score > avg_parent_fitness)
            success_rate = success_count / len(offspring_genotypes) if offspring_genotypes else 0
            
            # Elite rate (offspring with higher fitness than best parent)
            elite_count = sum(1 for o in offspring_genotypes if o.fitness_score > best_parent_fitness)
            elite_rate = elite_count / len(offspring_genotypes) if offspring_genotypes else 0
            
            report["success_metrics"] = {
                "avg_parent_fitness": avg_parent_fitness,
                "avg_offspring_fitness": avg_offspring_fitness,
                "best_parent_fitness": best_parent_fitness,
                "best_offspring_fitness": best_offspring_fitness,
                "avg_improvement": avg_improvement,
                "best_improvement": best_improvement,
                "success_rate": success_rate,
                "elite_rate": elite_rate
            }
        
        # Trait analysis
        if offspring_genotypes:
            # Collect all traits
            all_traits = set()
            for offspring in offspring_genotypes:
                all_traits.update(offspring.traits.keys())
            
            # Analyze trait distribution
            trait_distribution = {}
            for trait_key in all_traits:
                # Count occurrences
                count = sum(1 for o in offspring_genotypes if trait_key in o.traits)
                frequency = count / len(offspring_genotypes)
                
                # Collect values
                values = [str(o.traits[trait_key]) for o in offspring_genotypes if trait_key in o.traits]
                unique_values = len(set(values))
                
                trait_distribution[trait_key] = {
                    "count": count,
                    "frequency": frequency,
                    "unique_values": unique_values
                }
            
            report["trait_analysis"] = {
                "trait_count": len(all_traits),
                "trait_distribution": trait_distribution
            }
        
        # Strategy effectiveness
        if strategy.trait_weights and offspring_genotypes:
            weighted_traits = set(strategy.trait_weights.keys())
            
            # Calculate coverage of weighted traits
            weighted_trait_coverage = {}
            for trait_key in weighted_traits:
                count = sum(1 for o in offspring_genotypes if trait_key in o.traits)
                frequency = count / len(offspring_genotypes)
                weighted_trait_coverage[trait_key] = frequency
            
            # Calculate overall strategy effectiveness
            if weighted_traits:
                effectiveness = sum(weighted_trait_coverage.values()) / len(weighted_traits)
            else:
                effectiveness = 0.0
            
            report["strategy_effectiveness"] = {
                "weighted_trait_coverage": weighted_trait_coverage,
                "overall_effectiveness": effectiveness
            }
        
        return report

class BreedingStrategyAgent:
    """
    Breeding Strategy Agent implementation for the Overseer System.
    
    This class provides methods for breeding capsules, including:
    - Managing breeding strategies
    - Recombining traits from parent capsules
    - Evaluating offspring
    - Generating breeding reports
    """
    
    def __init__(self):
        """Initialize the Breeding Strategy Agent."""
        self.strategy_definition = StrategyDefinition()
        self.trait_recombiner = TraitRecombiner()
        self.offspring_evaluator = OffspringEvaluator()
        self.breeding_reporter = BreedingReporter()
        logger.info("Breeding Strategy Agent initialized")
    
    def create_strategy(self, strategy: BreedingStrategy) -> str:
        """
        Create a new breeding strategy.
        
        Args:
            strategy: The strategy to create
            
        Returns:
            str: The strategy ID
        """
        return self.strategy_definition.create_strategy(strategy)
    
    def get_strategy(self, strategy_id: str) -> Optional[BreedingStrategy]:
        """
        Get a breeding strategy by ID.
        
        Args:
            strategy_id: The strategy ID
            
        Returns:
            Optional[BreedingStrategy]: The strategy, or None if not found
        """
        return self.strategy_definition.get_strategy(strategy_id)
    
    def update_strategy(self, strategy_id: str, strategy: BreedingStrategy) -> bool:
        """
        Update a breeding strategy.
        
        Args:
            strategy_id: The strategy ID to update
            strategy: The updated strategy
            
        Returns:
            bool: True if successful, False if strategy not found
        """
        return self.strategy_definition.update_strategy(strategy_id, strategy)
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """
        Delete a breeding strategy.
        
        Args:
            strategy_id: The strategy ID to delete
            
        Returns:
            bool: True if successful, False if strategy not found
        """
        return self.strategy_definition.delete_strategy(strategy_id)
    
    def list_strategies(
        self,
        name_filter: Optional[str] = None,
        industry_filter: Optional[str] = None,
        capability_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[BreedingStrategy]:
        """
        List breeding strategies, optionally filtered.
        
        Args:
            name_filter: Optional filter for strategy name (case-insensitive substring match)
            industry_filter: Optional filter for industry focus
            capability_filter: Optional filter for capability focus
            limit: Maximum number of strategies to return
            
        Returns:
            List[BreedingStrategy]: List of matching strategies
        """
        return self.strategy_definition.list_strategies(
            name_filter=name_filter,
            industry_filter=industry_filter,
            capability_filter=capability_filter,
            limit=limit
        )
    
    def breed_capsules(self, request: BreedingRequest) -> BreedingResult:
        """
        Breed capsules according to the specified request.
        
        Args:
            request: The breeding request
            
        Returns:
            BreedingResult: The breeding result
        """
        result_id = f"result-{uuid.uuid4()}"
        
        try:
            # Get the breeding strategy
            strategy = self.strategy_definition.get_strategy(request.strategy_id)
            if not strategy:
                raise ValueError(f"Unknown breeding strategy: {request.strategy_id}")
            
            # Get the parent genotypes
            parent_genotypes = []
            for parent_id in request.parent_genotype_ids:
                parent = genotype_manager.get_genotype(parent_id)
                if parent:
                    parent_genotypes.append(parent)
            
            if len(parent_genotypes) < 2:
                raise ValueError("At least two valid parent genotypes are required")
            
            # Breed offspring
            offspring_genotypes = []
            offspring_ids = []
            
            for _ in range(request.offspring_count):
                # Create offspring genotype
                offspring = self.trait_recombiner.create_offspring_genotype(parent_genotypes, strategy)
                
                # Store the offspring
                genotype_manager.create_genotype(offspring)
                
                offspring_genotypes.append(offspring)
                offspring_ids.append(offspring.genotype_id)
            
            # Create breeding result
            result = BreedingResult(
                result_id=result_id,
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                parent_genotype_ids=request.parent_genotype_ids,
                offspring_genotype_ids=offspring_ids,
                success=True,
                metadata={
                    "strategy_name": strategy.name,
                    "parent_count": len(parent_genotypes),
                    "offspring_count": len(offspring_genotypes)
                }
            )
            
            # Store the result
            breeding_results[result_id] = result.dict()
            
            # Evaluate offspring
            evaluations = []
            for offspring in offspring_genotypes:
                evaluation = self.offspring_evaluator.evaluate_offspring(
                    offspring,
                    parent_genotypes,
                    strategy
                )
                evaluations.append(evaluation)
            
            # Generate breeding report
            report = self.breeding_reporter.generate_breeding_report(
                result,
                evaluations,
                parent_genotypes,
                offspring_genotypes,
                strategy
            )
            
            # Update result metadata with report summary
            if "success_metrics" in report:
                result.metadata["success_metrics"] = report["success_metrics"]
                breeding_results[result_id] = result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="capsule-breeding-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "strategy_id": request.strategy_id,
                    "parent_count": len(parent_genotypes),
                    "offspring_count": len(offspring_genotypes),
                    "success": True
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "capsules_bred",
                "result_id": result_id,
                "strategy_id": request.strategy_id,
                "parent_count": len(parent_genotypes),
                "offspring_count": len(offspring_genotypes)
            }
            mcp_bridge.send_context_update("breeding_strategy_agent", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="breeding_strategy_agent",
                message={
                    "type": "capsules_bred",
                    "result_id": result_id,
                    "strategy_id": request.strategy_id,
                    "parent_count": len(parent_genotypes),
                    "offspring_count": len(offspring_genotypes)
                }
            )
            
            return result
        
        except Exception as e:
            # Create error result
            error_result = BreedingResult(
                result_id=result_id,
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                parent_genotype_ids=request.parent_genotype_ids,
                offspring_genotype_ids=[],
                success=False,
                error_message=str(e),
                metadata={}
            )
            
            # Store the result
            breeding_results[result_id] = error_result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="capsule-breeding-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "strategy_id": request.strategy_id,
                    "success": False,
                    "error": str(e)
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "breeding_failed",
                "result_id": result_id,
                "strategy_id": request.strategy_id,
                "error": str(e)
            }
            mcp_bridge.send_context_update("breeding_strategy_agent", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="breeding_strategy_agent",
                message={
                    "type": "breeding_failed",
                    "result_id": result_id,
                    "strategy_id": request.strategy_id,
                    "error": str(e)
                }
            )
            
            return error_result
    
    def get_breeding_result(self, result_id: str) -> Optional[BreedingResult]:
        """
        Get a breeding result by ID.
        
        Args:
            result_id: The result ID
            
        Returns:
            Optional[BreedingResult]: The result, or None if not found
        """
        if result_id not in breeding_results:
            return None
        
        return BreedingResult(**breeding_results[result_id])
    
    def list_breeding_results(
        self,
        strategy_id: Optional[str] = None,
        success_only: bool = False,
        limit: int = 100
    ) -> List[BreedingResult]:
        """
        List breeding results, optionally filtered.
        
        Args:
            strategy_id: Optional filter for strategy ID
            success_only: Whether to include only successful results
            limit: Maximum number of results to return
            
        Returns:
            List[BreedingResult]: List of matching results
        """
        results = []
        
        for result_dict in breeding_results.values():
            # Apply filters
            if strategy_id and result_dict["strategy_id"] != strategy_id:
                continue
            
            if success_only and not result_dict["success"]:
                continue
            
            results.append(BreedingResult(**result_dict))
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda r: r.timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def get_offspring_evaluation(self, evaluation_id: str) -> Optional[OffspringEvaluation]:
        """
        Get an offspring evaluation by ID.
        
        Args:
            evaluation_id: The evaluation ID
            
        Returns:
            Optional[OffspringEvaluation]: The evaluation, or None if not found
        """
        return self.offspring_evaluator.get_evaluation(evaluation_id)
    
    def list_offspring_evaluations(
        self,
        genotype_id: Optional[str] = None,
        min_fitness: Optional[float] = None,
        max_fitness: Optional[float] = None,
        limit: int = 100
    ) -> List[OffspringEvaluation]:
        """
        List offspring evaluations, optionally filtered.
        
        Args:
            genotype_id: Optional filter for genotype ID
            min_fitness: Optional minimum fitness score
            max_fitness: Optional maximum fitness score
            limit: Maximum number of evaluations to return
            
        Returns:
            List[OffspringEvaluation]: List of matching evaluations
        """
        return self.offspring_evaluator.list_evaluations(
            genotype_id=genotype_id,
            min_fitness=min_fitness,
            max_fitness=max_fitness,
            limit=limit
        )
    
    def generate_breeding_report(self, result_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive report on a breeding result.
        
        Args:
            result_id: The result ID
            
        Returns:
            Dict[str, Any]: The breeding report
        """
        # Get the breeding result
        result = self.get_breeding_result(result_id)
        if not result or not result.success:
            return {"error": "Invalid or unsuccessful breeding result"}
        
        # Get the strategy
        strategy = self.strategy_definition.get_strategy(result.strategy_id)
        if not strategy:
            return {"error": "Strategy not found"}
        
        # Get parent genotypes
        parent_genotypes = []
        for parent_id in result.parent_genotype_ids:
            parent = genotype_manager.get_genotype(parent_id)
            if parent:
                parent_genotypes.append(parent)
        
        # Get offspring genotypes
        offspring_genotypes = []
        for offspring_id in result.offspring_genotype_ids:
            offspring = genotype_manager.get_genotype(offspring_id)
            if offspring:
                offspring_genotypes.append(offspring)
        
        # Get evaluations
        evaluations = []
        for offspring_id in result.offspring_genotype_ids:
            evals = self.offspring_evaluator.list_evaluations(genotype_id=offspring_id, limit=1)
            if evals:
                evaluations.append(evals[0])
        
        # Generate the report
        return self.breeding_reporter.generate_breeding_report(
            result,
            evaluations,
            parent_genotypes,
            offspring_genotypes,
            strategy
        )
