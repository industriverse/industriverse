"""
Capsule Genetics Engine for the Overseer System.

This module provides the Capsule Genetics Engine that manages capsule genetic traits,
inheritance, mutation, and evolution across the Industriverse ecosystem.
"""

import os
import json
import logging
import asyncio
import datetime
import uuid
import random
from typing import Dict, Any, List, Optional, Union, Set
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("capsule_genetics_engine")

class GeneticTrait(BaseModel):
    """Genetic trait definition."""
    trait_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str  # functional, behavioral, structural, performance, security
    value_type: str  # boolean, integer, float, string, enum
    default_value: Any
    possible_values: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mutation_probability: float  # 0.0 to 1.0
    mutation_magnitude: float  # 0.0 to 1.0
    dominance: float  # 0.0 to 1.0 (how strongly it's expressed when inherited)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GeneticProfile(BaseModel):
    """Genetic profile for a capsule."""
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    traits: Dict[str, Any] = Field(default_factory=dict)  # trait_id -> trait_value
    fitness_score: float = 0.0
    generation: int = 0
    parent_ids: List[str] = Field(default_factory=list)
    creation_time: datetime.datetime = Field(default_factory=datetime.datetime.now)
    last_mutation: Optional[datetime.datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EvolutionEvent(BaseModel):
    """Evolution event."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    event_type: str  # mutation, inheritance, selection, crossover
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    description: str
    changes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)  # trait_id -> {old_value, new_value}
    fitness_impact: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CapsuleGeneticsEngine:
    """
    Capsule Genetics Engine.
    
    This engine manages capsule genetic traits, inheritance, mutation, and evolution
    across the Industriverse ecosystem.
    """
    
    def __init__(self, event_bus_client=None, mcp_client=None, a2a_client=None):
        """
        Initialize the Capsule Genetics Engine.
        
        Args:
            event_bus_client: Event bus client for publishing and subscribing to events
            mcp_client: MCP client for context-aware communication
            a2a_client: A2A client for agent-based communication
        """
        self.event_bus_client = event_bus_client
        self.mcp_client = mcp_client
        self.a2a_client = a2a_client
        
        # In-memory storage (would be replaced with database in production)
        self.genetic_traits = {}  # trait_id -> GeneticTrait
        self.genetic_profiles = {}  # profile_id -> GeneticProfile
        self.capsule_profiles = {}  # capsule_id -> profile_id
        self.evolution_events = []  # List of EvolutionEvent
        
        # Evolution parameters
        self.mutation_rate = 0.05  # Base probability of mutation
        self.crossover_rate = 0.7  # Probability of crossover during reproduction
        self.selection_pressure = 0.8  # How strongly fitness influences selection
        
        # Initialize default traits
        self._initialize_default_traits()
        
    def _initialize_default_traits(self):
        """Initialize default genetic traits."""
        # Functional traits
        self._add_trait(GeneticTrait(
            name="ProcessingEfficiency",
            description="Efficiency of data processing operations",
            category="functional",
            value_type="float",
            default_value=0.7,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.1,
            mutation_magnitude=0.1,
            dominance=0.8
        ))
        
        self._add_trait(GeneticTrait(
            name="MemoryOptimization",
            description="Efficiency of memory usage",
            category="functional",
            value_type="float",
            default_value=0.6,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.1,
            mutation_magnitude=0.1,
            dominance=0.7
        ))
        
        self._add_trait(GeneticTrait(
            name="ParallelProcessingCapability",
            description="Ability to process tasks in parallel",
            category="functional",
            value_type="float",
            default_value=0.5,
            min_value=0.0,
            max_value=1.0,
            mutation_probability=0.05,
            mutation_magnitude=0.15,
            dominance=0.9
        ))
        
        # Behavioral traits
        self._add_trait(GeneticTrait(
            name="Autonomy",
            description="Level of autonomous decision-making",
            category="behavioral",
            value_type="float",
            default_value=0.5,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.1,
            mutation_magnitude=0.1,
            dominance=0.8
        ))
        
        self._add_trait(GeneticTrait(
            name="Adaptability",
            description="Ability to adapt to changing conditions",
            category="behavioral",
            value_type="float",
            default_value=0.6,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.15,
            mutation_magnitude=0.1,
            dominance=0.7
        ))
        
        self._add_trait(GeneticTrait(
            name="Collaboration",
            description="Ability to collaborate with other capsules",
            category="behavioral",
            value_type="float",
            default_value=0.7,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.1,
            mutation_magnitude=0.1,
            dominance=0.6
        ))
        
        # Structural traits
        self._add_trait(GeneticTrait(
            name="Modularity",
            description="Degree of modular design",
            category="structural",
            value_type="float",
            default_value=0.6,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.05,
            mutation_magnitude=0.1,
            dominance=0.9
        ))
        
        self._add_trait(GeneticTrait(
            name="InterfaceComplexity",
            description="Complexity of external interfaces",
            category="structural",
            value_type="float",
            default_value=0.5,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.05,
            mutation_magnitude=0.1,
            dominance=0.7
        ))
        
        self._add_trait(GeneticTrait(
            name="StateManagement",
            description="Sophistication of internal state management",
            category="structural",
            value_type="float",
            default_value=0.6,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.1,
            mutation_magnitude=0.1,
            dominance=0.8
        ))
        
        # Performance traits
        self._add_trait(GeneticTrait(
            name="ResponseTime",
            description="Speed of response to requests",
            category="performance",
            value_type="float",
            default_value=0.7,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.1,
            mutation_magnitude=0.1,
            dominance=0.8
        ))
        
        self._add_trait(GeneticTrait(
            name="Throughput",
            description="Volume of operations per unit time",
            category="performance",
            value_type="float",
            default_value=0.6,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.1,
            mutation_magnitude=0.1,
            dominance=0.7
        ))
        
        self._add_trait(GeneticTrait(
            name="Reliability",
            description="Consistency of operation without failures",
            category="performance",
            value_type="float",
            default_value=0.8,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.05,
            mutation_magnitude=0.1,
            dominance=0.9
        ))
        
        # Security traits
        self._add_trait(GeneticTrait(
            name="ThreatResistance",
            description="Resistance to security threats",
            category="security",
            value_type="float",
            default_value=0.7,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.05,
            mutation_magnitude=0.1,
            dominance=0.9
        ))
        
        self._add_trait(GeneticTrait(
            name="DataProtection",
            description="Effectiveness of data protection mechanisms",
            category="security",
            value_type="float",
            default_value=0.8,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.05,
            mutation_magnitude=0.1,
            dominance=0.9
        ))
        
        self._add_trait(GeneticTrait(
            name="AuthenticationStrength",
            description="Strength of authentication mechanisms",
            category="security",
            value_type="float",
            default_value=0.8,
            min_value=0.1,
            max_value=1.0,
            mutation_probability=0.05,
            mutation_magnitude=0.1,
            dominance=0.9
        ))
        
    def _add_trait(self, trait: GeneticTrait):
        """
        Add a genetic trait.
        
        Args:
            trait: Genetic trait to add
        """
        self.genetic_traits[trait.trait_id] = trait
        
    async def initialize(self):
        """Initialize the Capsule Genetics Engine."""
        logger.info("Initializing Capsule Genetics Engine")
        
        # In a real implementation, we would initialize connections to external systems
        # For example:
        # await self.event_bus_client.connect()
        # await self.mcp_client.connect()
        # await self.a2a_client.connect()
        
        # Subscribe to events
        # await self.event_bus_client.subscribe("capsule.created", self._handle_capsule_created)
        # await self.event_bus_client.subscribe("capsule.performance.updated", self._handle_capsule_performance_updated)
        
        logger.info("Capsule Genetics Engine initialized")
        
    async def create_genetic_profile(self, capsule_id: str, parent_ids: Optional[List[str]] = None) -> GeneticProfile:
        """
        Create a genetic profile for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            parent_ids: Optional list of parent capsule IDs for inheritance
            
        Returns:
            Created genetic profile
        """
        logger.info(f"Creating genetic profile for capsule {capsule_id}")
        
        # Check if profile already exists
        if capsule_id in self.capsule_profiles:
            profile_id = self.capsule_profiles[capsule_id]
            logger.info(f"Genetic profile already exists for capsule {capsule_id}: {profile_id}")
            return self.genetic_profiles[profile_id]
            
        # Initialize traits
        traits = {}
        
        if parent_ids and len(parent_ids) > 0:
            # Inherit traits from parents
            parent_profiles = []
            for parent_id in parent_ids:
                if parent_id in self.capsule_profiles:
                    parent_profile_id = self.capsule_profiles[parent_id]
                    parent_profiles.append(self.genetic_profiles[parent_profile_id])
                    
            if parent_profiles:
                # Determine generation
                generation = max(profile.generation for profile in parent_profiles) + 1
                
                # Inherit traits
                traits = await self._inherit_traits(parent_profiles)
                
                # Record inheritance event
                event = EvolutionEvent(
                    capsule_id=capsule_id,
                    event_type="inheritance",
                    description=f"Inherited traits from {len(parent_profiles)} parents",
                    changes={},  # No changes to record for inheritance
                    fitness_impact=0.0  # Unknown until fitness is calculated
                )
                
                self.evolution_events.append(event)
                
                logger.info(f"Inherited traits for capsule {capsule_id} from {len(parent_profiles)} parents")
            else:
                # No valid parent profiles, use default traits
                generation = 0
                traits = self._generate_default_traits()
                
                logger.info(f"Using default traits for capsule {capsule_id} (no valid parents)")
        else:
            # No parents, use default traits
            generation = 0
            traits = self._generate_default_traits()
            
            logger.info(f"Using default traits for capsule {capsule_id} (no parents)")
            
        # Create profile
        profile = GeneticProfile(
            capsule_id=capsule_id,
            traits=traits,
            generation=generation,
            parent_ids=parent_ids or []
        )
        
        # Calculate initial fitness
        profile.fitness_score = await self._calculate_fitness(profile)
        
        # Store profile
        self.genetic_profiles[profile.profile_id] = profile
        self.capsule_profiles[capsule_id] = profile.profile_id
        
        # In a real implementation, we would publish the creation
        # For example:
        # await self.event_bus_client.publish("genetics.profile.created", profile.dict())
        
        logger.info(f"Created genetic profile {profile.profile_id} for capsule {capsule_id}: fitness={profile.fitness_score:.2f}")
        
        return profile
        
    def _generate_default_traits(self) -> Dict[str, Any]:
        """
        Generate default trait values.
        
        Returns:
            Dictionary of trait values
        """
        traits = {}
        
        for trait_id, trait in self.genetic_traits.items():
            traits[trait_id] = trait.default_value
            
        return traits
        
    async def _inherit_traits(self, parent_profiles: List[GeneticProfile]) -> Dict[str, Any]:
        """
        Inherit traits from parent profiles.
        
        Args:
            parent_profiles: List of parent profiles
            
        Returns:
            Dictionary of inherited trait values
        """
        traits = {}
        
        # For each trait, inherit from parents
        for trait_id, trait in self.genetic_traits.items():
            # Get parent values
            parent_values = []
            for profile in parent_profiles:
                if trait_id in profile.traits:
                    parent_values.append(profile.traits[trait_id])
                    
            if parent_values:
                if trait.value_type == "boolean":
                    # Boolean traits: weighted random choice
                    weights = [trait.dominance for _ in parent_values]
                    traits[trait_id] = random.choices(parent_values, weights=weights, k=1)[0]
                    
                elif trait.value_type in ["integer", "float"]:
                    # Numeric traits: weighted average with random variation
                    weights = [trait.dominance for _ in parent_values]
                    weighted_sum = sum(value * weight for value, weight in zip(parent_values, weights))
                    weighted_avg = weighted_sum / sum(weights)
                    
                    # Add random variation
                    variation = random.uniform(-0.1, 0.1) * trait.mutation_magnitude
                    value = weighted_avg * (1 + variation)
                    
                    # Ensure within bounds
                    if trait.min_value is not None:
                        value = max(trait.min_value, value)
                    if trait.max_value is not None:
                        value = min(trait.max_value, value)
                        
                    # Convert to integer if needed
                    if trait.value_type == "integer":
                        value = int(round(value))
                        
                    traits[trait_id] = value
                    
                elif trait.value_type == "string":
                    # String traits: select from parent with highest dominance
                    idx = weights.index(max(weights))
                    traits[trait_id] = parent_values[idx]
                    
                elif trait.value_type == "enum":
                    # Enum traits: weighted random choice
                    weights = [trait.dominance for _ in parent_values]
                    traits[trait_id] = random.choices(parent_values, weights=weights, k=1)[0]
                    
                else:
                    # Unknown type, use default
                    traits[trait_id] = trait.default_value
            else:
                # No parent values, use default
                traits[trait_id] = trait.default_value
                
        # Apply crossover
        if len(parent_profiles) >= 2 and random.random() < self.crossover_rate:
            traits = self._apply_crossover(traits, parent_profiles)
            
        # Apply mutations
        traits = self._apply_mutations(traits)
        
        return traits
        
    def _apply_crossover(self, traits: Dict[str, Any], parent_profiles: List[GeneticProfile]) -> Dict[str, Any]:
        """
        Apply genetic crossover.
        
        Args:
            traits: Dictionary of trait values
            parent_profiles: List of parent profiles
            
        Returns:
            Dictionary of trait values after crossover
        """
        # Select two parents for crossover
        if len(parent_profiles) >= 2:
            parent1, parent2 = random.sample(parent_profiles, 2)
        else:
            return traits
            
        # Select crossover point
        trait_ids = list(self.genetic_traits.keys())
        crossover_point = random.randint(1, len(trait_ids) - 1)
        
        # Apply crossover
        for i, trait_id in enumerate(trait_ids):
            if i < crossover_point:
                if trait_id in parent1.traits:
                    traits[trait_id] = parent1.traits[trait_id]
            else:
                if trait_id in parent2.traits:
                    traits[trait_id] = parent2.traits[trait_id]
                    
        return traits
        
    def _apply_mutations(self, traits: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply genetic mutations.
        
        Args:
            traits: Dictionary of trait values
            
        Returns:
            Dictionary of trait values after mutations
        """
        for trait_id, trait in self.genetic_traits.items():
            # Check if mutation occurs
            if random.random() < trait.mutation_probability * self.mutation_rate:
                # Apply mutation
                if trait.value_type == "boolean":
                    # Boolean traits: flip value
                    traits[trait_id] = not traits[trait_id]
                    
                elif trait.value_type in ["integer", "float"]:
                    # Numeric traits: add random variation
                    variation = random.uniform(-1.0, 1.0) * trait.mutation_magnitude
                    value = traits[trait_id] * (1 + variation)
                    
                    # Ensure within bounds
                    if trait.min_value is not None:
                        value = max(trait.min_value, value)
                    if trait.max_value is not None:
                        value = min(trait.max_value, value)
                        
                    # Convert to integer if needed
                    if trait.value_type == "integer":
                        value = int(round(value))
                        
                    traits[trait_id] = value
                    
                elif trait.value_type == "enum" and trait.possible_values:
                    # Enum traits: select random value
                    traits[trait_id] = random.choice(trait.possible_values)
                    
        return traits
        
    async def _calculate_fitness(self, profile: GeneticProfile) -> float:
        """
        Calculate fitness score for a genetic profile.
        
        Args:
            profile: Genetic profile
            
        Returns:
            Fitness score (0.0 to 1.0)
        """
        # In a real implementation, we would have a more sophisticated fitness function
        # that takes into account various factors such as performance, reliability, etc.
        # For simplicity, we'll use a weighted average of trait values
        
        weights = {
            "functional": 0.25,
            "behavioral": 0.2,
            "structural": 0.15,
            "performance": 0.25,
            "security": 0.15
        }
        
        category_scores = {category: [] for category in weights.keys()}
        
        # Calculate score for each trait
        for trait_id, value in profile.traits.items():
            if trait_id in self.genetic_traits:
                trait = self.genetic_traits[trait_id]
                
                # Normalize value to 0.0-1.0 range
                if trait.value_type == "boolean":
                    normalized_value = 1.0 if value else 0.0
                elif trait.value_type in ["integer", "float"]:
                    if trait.min_value is not None and trait.max_value is not None:
                        normalized_value = (value - trait.min_value) / (trait.max_value - trait.min_value)
                    else:
                        normalized_value = value
                else:
                    normalized_value = 0.5  # Default for non-numeric types
                    
                # Add to category scores
                category_scores[trait.category].append(normalized_value)
                
        # Calculate average score for each category
        category_averages = {}
        for category, scores in category_scores.items():
            if scores:
                category_averages[category] = sum(scores) / len(scores)
            else:
                category_averages[category] = 0.5  # Default if no traits in category
                
        # Calculate weighted average
        fitness = sum(category_averages[category] * weight for category, weight in weights.items())
        
        return fitness
        
    async def mutate_profile(self, capsule_id: str) -> Optional[GeneticProfile]:
        """
        Mutate the genetic profile of a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Updated genetic profile, or None if not found
        """
        logger.info(f"Mutating genetic profile for capsule {capsule_id}")
        
        # Check if profile exists
        if capsule_id not in self.capsule_profiles:
            logger.warning(f"No genetic profile found for capsule {capsule_id}")
            return None
            
        profile_id = self.capsule_profiles[capsule_id]
        profile = self.genetic_profiles[profile_id]
        
        # Store old traits for comparison
        old_traits = profile.traits.copy()
        
        # Apply mutations with increased probability
        increased_mutation_rate = self.mutation_rate * 3  # Triple the mutation rate
        
        for trait_id, trait in self.genetic_traits.items():
            # Check if mutation occurs
            if random.random() < trait.mutation_probability * increased_mutation_rate:
                # Apply mutation
                if trait.value_type == "boolean":
                    # Boolean traits: flip value
                    profile.traits[trait_id] = not profile.traits[trait_id]
                    
                elif trait.value_type in ["integer", "float"]:
                    # Numeric traits: add random variation
                    variation = random.uniform(-1.0, 1.0) * trait.mutation_magnitude * 2  # Double the magnitude
                    value = profile.traits[trait_id] * (1 + variation)
                    
                    # Ensure within bounds
                    if trait.min_value is not None:
                        value = max(trait.min_value, value)
                    if trait.max_value is not None:
                        value = min(trait.max_value, value)
                        
                    # Convert to integer if needed
                    if trait.value_type == "integer":
                        value = int(round(value))
                        
                    profile.traits[trait_id] = value
                    
                elif trait.value_type == "enum" and trait.possible_values:
                    # Enum traits: select random value
                    profile.traits[trait_id] = random.choice(trait.possible_values)
                    
        # Update mutation timestamp
        profile.last_mutation = datetime.datetime.now()
        
        # Calculate new fitness
        old_fitness = profile.fitness_score
        profile.fitness_score = await self._calculate_fitness(profile)
        
        # Record changes
        changes = {}
        for trait_id, new_value in profile.traits.items():
            if trait_id in old_traits and old_traits[trait_id] != new_value:
                changes[trait_id] = {
                    "old_value": old_traits[trait_id],
                    "new_value": new_value
                }
                
        # Record mutation event
        event = EvolutionEvent(
            capsule_id=capsule_id,
            event_type="mutation",
            description=f"Mutated {len(changes)} traits",
            changes=changes,
            fitness_impact=profile.fitness_score - old_fitness
        )
        
        self.evolution_events.append(event)
        
        # In a real implementation, we would publish the update
        # For example:
        # await self.event_bus_client.publish("genetics.profile.mutated", {
        #     "profile_id": profile.profile_id,
        #     "capsule_id": capsule_id,
        #     "changes": changes,
        #     "fitness_impact": profile.fitness_score - old_fitness
        # })
        
        logger.info(f"Mutated genetic profile for capsule {capsule_id}: {len(changes)} traits changed, fitness impact: {profile.fitness_score - old_fitness:.2f}")
        
        return profile
        
    async def breed_profiles(self, parent_ids: List[str], child_id: str) -> Optional[GeneticProfile]:
        """
        Breed genetic profiles to create a child profile.
        
        Args:
            parent_ids: List of parent capsule IDs
            child_id: ID of the child capsule
            
        Returns:
            Created genetic profile, or None if parents not found
        """
        logger.info(f"Breeding genetic profiles for child {child_id} from parents {parent_ids}")
        
        # Validate parents
        valid_parent_ids = []
        for parent_id in parent_ids:
            if parent_id in self.capsule_profiles:
                valid_parent_ids.append(parent_id)
                
        if not valid_parent_ids:
            logger.warning(f"No valid parent profiles found for breeding")
            return None
            
        # Create child profile
        return await self.create_genetic_profile(child_id, valid_parent_ids)
        
    async def get_genetic_profile(self, capsule_id: str) -> Optional[GeneticProfile]:
        """
        Get the genetic profile for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Genetic profile, or None if not found
        """
        if capsule_id not in self.capsule_profiles:
            return None
            
        profile_id = self.capsule_profiles[capsule_id]
        return self.genetic_profiles[profile_id]
        
    async def get_genetic_trait(self, trait_id: str) -> Optional[GeneticTrait]:
        """
        Get a genetic trait by ID.
        
        Args:
            trait_id: ID of the trait
            
        Returns:
            Genetic trait, or None if not found
        """
        return self.genetic_traits.get(trait_id)
        
    async def get_genetic_traits(self, category: Optional[str] = None) -> List[GeneticTrait]:
        """
        Get genetic traits.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of genetic traits
        """
        if category:
            return [trait for trait in self.genetic_traits.values() if trait.category == category]
        else:
            return list(self.genetic_traits.values())
            
    async def get_evolution_events(self, capsule_id: str) -> List[EvolutionEvent]:
        """
        Get evolution events for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            List of evolution events
        """
        events = [event for event in self.evolution_events if event.capsule_id == capsule_id]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return events
        
    async def create_genetic_trait(self, trait: GeneticTrait) -> GeneticTrait:
        """
        Create a new genetic trait.
        
        Args:
            trait: Genetic trait to create
            
        Returns:
            Created genetic trait
        """
        # Store trait
        self.genetic_traits[trait.trait_id] = trait
        
        # In a real implementation, we would publish the creation
        # For example:
        # await self.event_bus_client.publish("genetics.trait.created", trait.dict())
        
        logger.info(f"Created genetic trait {trait.trait_id}: {trait.name}")
        
        return trait
        
    async def update_genetic_trait(self, trait_id: str, updates: Dict[str, Any]) -> Optional[GeneticTrait]:
        """
        Update a genetic trait.
        
        Args:
            trait_id: ID of the trait to update
            updates: Updates to apply
            
        Returns:
            Updated genetic trait, or None if not found
        """
        if trait_id not in self.genetic_traits:
            logger.warning(f"Genetic trait {trait_id} not found")
            return None
            
        trait = self.genetic_traits[trait_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(trait, key):
                setattr(trait, key, value)
                
        # In a real implementation, we would publish the update
        # For example:
        # await self.event_bus_client.publish("genetics.trait.updated", trait.dict())
        
        logger.info(f"Updated genetic trait {trait_id}: {trait.name}")
        
        return trait
        
    async def delete_genetic_trait(self, trait_id: str) -> bool:
        """
        Delete a genetic trait.
        
        Args:
            trait_id: ID of the trait to delete
            
        Returns:
            True if deleted, False if not found
        """
        if trait_id not in self.genetic_traits:
            logger.warning(f"Genetic trait {trait_id} not found")
            return False
            
        # Delete trait
        del self.genetic_traits[trait_id]
        
        # In a real implementation, we would publish the deletion
        # For example:
        # await self.event_bus_client.publish("genetics.trait.deleted", {"trait_id": trait_id})
        
        logger.info(f"Deleted genetic trait {trait_id}")
        
        return True
        
    async def get_trait_distribution(self, trait_id: str) -> Dict[Any, int]:
        """
        Get the distribution of values for a trait across all capsules.
        
        Args:
            trait_id: ID of the trait
            
        Returns:
            Dictionary mapping trait values to counts
        """
        if trait_id not in self.genetic_traits:
            logger.warning(f"Genetic trait {trait_id} not found")
            return {}
            
        distribution = {}
        
        for profile in self.genetic_profiles.values():
            if trait_id in profile.traits:
                value = profile.traits[trait_id]
                
                # Convert to string for dictionary key
                key = str(value)
                
                if key in distribution:
                    distribution[key] += 1
                else:
                    distribution[key] = 1
                    
        return distribution
        
    async def get_fitness_distribution(self) -> Dict[str, int]:
        """
        Get the distribution of fitness scores across all capsules.
        
        Returns:
            Dictionary mapping fitness score ranges to counts
        """
        distribution = {
            "0.0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0
        }
        
        for profile in self.genetic_profiles.values():
            if profile.fitness_score < 0.2:
                distribution["0.0-0.2"] += 1
            elif profile.fitness_score < 0.4:
                distribution["0.2-0.4"] += 1
            elif profile.fitness_score < 0.6:
                distribution["0.4-0.6"] += 1
            elif profile.fitness_score < 0.8:
                distribution["0.6-0.8"] += 1
            else:
                distribution["0.8-1.0"] += 1
                
        return distribution
        
    async def get_generation_distribution(self) -> Dict[int, int]:
        """
        Get the distribution of generations across all capsules.
        
        Returns:
            Dictionary mapping generations to counts
        """
        distribution = {}
        
        for profile in self.genetic_profiles.values():
            generation = profile.generation
            
            if generation in distribution:
                distribution[generation] += 1
            else:
                distribution[generation] = 1
                
        return distribution
        
    async def _handle_capsule_created(self, event):
        """
        Handle capsule created event.
        
        Args:
            event: Capsule created event
        """
        capsule_id = event["capsule_id"]
        parent_ids = event.get("parent_ids", [])
        
        logger.info(f"Handling capsule created event for capsule {capsule_id}")
        
        # Create genetic profile
        await self.create_genetic_profile(capsule_id, parent_ids)
        
    async def _handle_capsule_performance_updated(self, event):
        """
        Handle capsule performance updated event.
        
        Args:
            event: Capsule performance updated event
        """
        capsule_id = event["capsule_id"]
        
        logger.info(f"Handling capsule performance updated event for capsule {capsule_id}")
        
        # Check if profile exists
        if capsule_id not in self.capsule_profiles:
            logger.warning(f"No genetic profile found for capsule {capsule_id}")
            return
            
        # Update fitness
        profile_id = self.capsule_profiles[capsule_id]
        profile = self.genetic_profiles[profile_id]
        
        old_fitness = profile.fitness_score
        profile.fitness_score = await self._calculate_fitness(profile)
        
        logger.info(f"Updated fitness for capsule {capsule_id}: {old_fitness:.2f} -> {profile.fitness_score:.2f}")
        
        # In a real implementation, we would publish the update
        # For example:
        # await self.event_bus_client.publish("genetics.fitness.updated", {
        #     "capsule_id": capsule_id,
        #     "old_fitness": old_fitness,
        #     "new_fitness": profile.fitness_score
        # })
