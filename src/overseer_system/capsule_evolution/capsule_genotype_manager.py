"""
Capsule Genotype Manager for the Overseer System.

This module provides comprehensive capsule genotype management capabilities for the Overseer System,
enabling the definition, storage, retrieval, and analysis of capsule genotypes.

The Capsule Genotype Manager is a critical component of the Capsule Evolution phase,
providing the foundation for genetic-inspired breeding and mutation of capsules.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any, Set

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from pydantic import BaseModel, Field, validator

# Import MCP/A2A integration
from ..mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from ..a2a_integration.a2a_protocol_bridge import A2AProtocolBridge

# Import event bus
from ..event_bus.kafka_client import KafkaProducer, KafkaConsumer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("capsule_genotype_manager")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="capsule-genotype-manager"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="capsule-genotype-manager",
    auto_offset_reset="earliest"
)

# Data models
class GenotypeTraitDefinition(BaseModel):
    """Model for genotype trait definition."""
    trait_id: str = Field(..., description="Unique trait identifier")
    name: str = Field(..., description="Trait name")
    description: str = Field(..., description="Trait description")
    value_type: str = Field(..., description="Type of value (string, number, boolean, object, array)")
    default_value: Any = Field(None, description="Default value for the trait")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Constraints for the trait value")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleGenotype(BaseModel):
    """Model for capsule genotype."""
    genotype_id: str = Field(..., description="Unique genotype identifier")
    name: str = Field(..., description="Genotype name")
    description: str = Field(..., description="Genotype description")
    version: str = Field(..., description="Genotype version")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    traits: Dict[str, Any] = Field(..., description="Trait values")
    parent_genotypes: List[str] = Field(default_factory=list, description="Parent genotype IDs")
    industry_tags: List[str] = Field(default_factory=list, description="Industry tags")
    capability_tags: List[str] = Field(default_factory=list, description="Capability tags")
    fitness_score: float = Field(0.0, description="Fitness score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class GenotypeAnalysisRequest(BaseModel):
    """Model for genotype analysis requests."""
    genotype_ids: List[str] = Field(..., description="List of genotype IDs to analyze")
    analysis_type: str = Field(..., description="Type of analysis to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Analysis parameters")

class GenotypeAnalysisResult(BaseModel):
    """Model for genotype analysis results."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    genotype_ids: List[str] = Field(..., description="List of analyzed genotype IDs")
    analysis_type: str = Field(..., description="Type of analysis performed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# In-memory storage (would be replaced with database in production)
genotype_traits = {}
genotypes = {}
genotype_analyses = {}

class GenotypeDefinitionManager:
    """
    Manages the definition of genotype traits.
    
    This class provides methods for creating, retrieving, updating, and deleting
    genotype trait definitions.
    """
    
    def __init__(self):
        """Initialize the Genotype Definition Manager."""
        logger.info("Genotype Definition Manager initialized")
    
    def create_trait_definition(self, trait_def: GenotypeTraitDefinition) -> str:
        """
        Create a new genotype trait definition.
        
        Args:
            trait_def: The trait definition to create
            
        Returns:
            str: The trait ID
        """
        # Store the trait definition
        genotype_traits[trait_def.trait_id] = trait_def.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-genotype-traits",
            key=trait_def.trait_id,
            value=json.dumps({
                "action": "create",
                "trait_id": trait_def.trait_id,
                "name": trait_def.name
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "trait_definition_created",
            "trait_id": trait_def.trait_id,
            "name": trait_def.name
        }
        mcp_bridge.send_context_update("capsule_genotype_manager", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="capsule_genotype_manager",
            message={
                "type": "trait_definition_created",
                "trait_id": trait_def.trait_id,
                "name": trait_def.name
            }
        )
        
        return trait_def.trait_id
    
    def get_trait_definition(self, trait_id: str) -> Optional[GenotypeTraitDefinition]:
        """
        Get a genotype trait definition by ID.
        
        Args:
            trait_id: The trait ID
            
        Returns:
            Optional[GenotypeTraitDefinition]: The trait definition, or None if not found
        """
        if trait_id not in genotype_traits:
            return None
        
        return GenotypeTraitDefinition(**genotype_traits[trait_id])
    
    def update_trait_definition(self, trait_id: str, trait_def: GenotypeTraitDefinition) -> bool:
        """
        Update a genotype trait definition.
        
        Args:
            trait_id: The trait ID to update
            trait_def: The updated trait definition
            
        Returns:
            bool: True if successful, False if trait not found
        """
        if trait_id not in genotype_traits:
            return False
        
        # Update the trait definition
        genotype_traits[trait_id] = trait_def.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-genotype-traits",
            key=trait_id,
            value=json.dumps({
                "action": "update",
                "trait_id": trait_id,
                "name": trait_def.name
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "trait_definition_updated",
            "trait_id": trait_id,
            "name": trait_def.name
        }
        mcp_bridge.send_context_update("capsule_genotype_manager", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="capsule_genotype_manager",
            message={
                "type": "trait_definition_updated",
                "trait_id": trait_id,
                "name": trait_def.name
            }
        )
        
        return True
    
    def delete_trait_definition(self, trait_id: str) -> bool:
        """
        Delete a genotype trait definition.
        
        Args:
            trait_id: The trait ID to delete
            
        Returns:
            bool: True if successful, False if trait not found
        """
        if trait_id not in genotype_traits:
            return False
        
        # Get trait name before deletion
        trait_name = genotype_traits[trait_id]["name"]
        
        # Delete the trait definition
        del genotype_traits[trait_id]
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-genotype-traits",
            key=trait_id,
            value=json.dumps({
                "action": "delete",
                "trait_id": trait_id,
                "name": trait_name
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "trait_definition_deleted",
            "trait_id": trait_id,
            "name": trait_name
        }
        mcp_bridge.send_context_update("capsule_genotype_manager", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="capsule_genotype_manager",
            message={
                "type": "trait_definition_deleted",
                "trait_id": trait_id,
                "name": trait_name
            }
        )
        
        return True
    
    def list_trait_definitions(
        self,
        name_filter: Optional[str] = None,
        value_type_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[GenotypeTraitDefinition]:
        """
        List genotype trait definitions, optionally filtered.
        
        Args:
            name_filter: Optional filter for trait name (case-insensitive substring match)
            value_type_filter: Optional filter for value type
            limit: Maximum number of traits to return
            
        Returns:
            List[GenotypeTraitDefinition]: List of matching trait definitions
        """
        results = []
        
        for trait_dict in genotype_traits.values():
            # Apply filters
            if name_filter and name_filter.lower() not in trait_dict["name"].lower():
                continue
            
            if value_type_filter and trait_dict["value_type"] != value_type_filter:
                continue
            
            results.append(GenotypeTraitDefinition(**trait_dict))
        
        # Sort by name
        results.sort(key=lambda t: t.name)
        
        # Apply limit
        return results[:limit]

class GenotypeStorageManager:
    """
    Manages the storage and retrieval of capsule genotypes.
    
    This class provides methods for creating, retrieving, updating, and deleting
    capsule genotypes.
    """
    
    def __init__(self):
        """Initialize the Genotype Storage Manager."""
        logger.info("Genotype Storage Manager initialized")
    
    def create_genotype(self, genotype: CapsuleGenotype) -> str:
        """
        Create a new capsule genotype.
        
        Args:
            genotype: The genotype to create
            
        Returns:
            str: The genotype ID
        """
        # Store the genotype
        genotypes[genotype.genotype_id] = genotype.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-genotypes",
            key=genotype.genotype_id,
            value=json.dumps({
                "action": "create",
                "genotype_id": genotype.genotype_id,
                "name": genotype.name,
                "version": genotype.version
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "genotype_created",
            "genotype_id": genotype.genotype_id,
            "name": genotype.name,
            "version": genotype.version
        }
        mcp_bridge.send_context_update("capsule_genotype_manager", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="capsule_genotype_manager",
            message={
                "type": "genotype_created",
                "genotype_id": genotype.genotype_id,
                "name": genotype.name,
                "version": genotype.version
            }
        )
        
        return genotype.genotype_id
    
    def get_genotype(self, genotype_id: str) -> Optional[CapsuleGenotype]:
        """
        Get a capsule genotype by ID.
        
        Args:
            genotype_id: The genotype ID
            
        Returns:
            Optional[CapsuleGenotype]: The genotype, or None if not found
        """
        if genotype_id not in genotypes:
            return None
        
        return CapsuleGenotype(**genotypes[genotype_id])
    
    def update_genotype(self, genotype_id: str, genotype: CapsuleGenotype) -> bool:
        """
        Update a capsule genotype.
        
        Args:
            genotype_id: The genotype ID to update
            genotype: The updated genotype
            
        Returns:
            bool: True if successful, False if genotype not found
        """
        if genotype_id not in genotypes:
            return False
        
        # Update the genotype
        genotype.updated_at = datetime.now()
        genotypes[genotype_id] = genotype.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-genotypes",
            key=genotype_id,
            value=json.dumps({
                "action": "update",
                "genotype_id": genotype_id,
                "name": genotype.name,
                "version": genotype.version
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "genotype_updated",
            "genotype_id": genotype_id,
            "name": genotype.name,
            "version": genotype.version
        }
        mcp_bridge.send_context_update("capsule_genotype_manager", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="capsule_genotype_manager",
            message={
                "type": "genotype_updated",
                "genotype_id": genotype_id,
                "name": genotype.name,
                "version": genotype.version
            }
        )
        
        return True
    
    def delete_genotype(self, genotype_id: str) -> bool:
        """
        Delete a capsule genotype.
        
        Args:
            genotype_id: The genotype ID to delete
            
        Returns:
            bool: True if successful, False if genotype not found
        """
        if genotype_id not in genotypes:
            return False
        
        # Get genotype name before deletion
        genotype_name = genotypes[genotype_id]["name"]
        genotype_version = genotypes[genotype_id]["version"]
        
        # Delete the genotype
        del genotypes[genotype_id]
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-genotypes",
            key=genotype_id,
            value=json.dumps({
                "action": "delete",
                "genotype_id": genotype_id,
                "name": genotype_name,
                "version": genotype_version
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "genotype_deleted",
            "genotype_id": genotype_id,
            "name": genotype_name,
            "version": genotype_version
        }
        mcp_bridge.send_context_update("capsule_genotype_manager", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="capsule_genotype_manager",
            message={
                "type": "genotype_deleted",
                "genotype_id": genotype_id,
                "name": genotype_name,
                "version": genotype_version
            }
        )
        
        return True
    
    def list_genotypes(
        self,
        name_filter: Optional[str] = None,
        industry_tag_filter: Optional[str] = None,
        capability_tag_filter: Optional[str] = None,
        min_fitness_score: Optional[float] = None,
        limit: int = 100
    ) -> List[CapsuleGenotype]:
        """
        List capsule genotypes, optionally filtered.
        
        Args:
            name_filter: Optional filter for genotype name (case-insensitive substring match)
            industry_tag_filter: Optional filter for industry tag
            capability_tag_filter: Optional filter for capability tag
            min_fitness_score: Optional minimum fitness score
            limit: Maximum number of genotypes to return
            
        Returns:
            List[CapsuleGenotype]: List of matching genotypes
        """
        results = []
        
        for genotype_dict in genotypes.values():
            # Apply filters
            if name_filter and name_filter.lower() not in genotype_dict["name"].lower():
                continue
            
            if industry_tag_filter and industry_tag_filter not in genotype_dict["industry_tags"]:
                continue
            
            if capability_tag_filter and capability_tag_filter not in genotype_dict["capability_tags"]:
                continue
            
            if min_fitness_score is not None and genotype_dict["fitness_score"] < min_fitness_score:
                continue
            
            results.append(CapsuleGenotype(**genotype_dict))
        
        # Sort by fitness score (highest first)
        results.sort(key=lambda g: g.fitness_score, reverse=True)
        
        # Apply limit
        return results[:limit]

class GenotypeAnalysisManager:
    """
    Manages the analysis of capsule genotypes.
    
    This class provides methods for analyzing genotypes, including trait distribution,
    fitness correlation, and genetic diversity.
    """
    
    def __init__(self):
        """Initialize the Genotype Analysis Manager."""
        logger.info("Genotype Analysis Manager initialized")
    
    def analyze_genotypes(self, request: GenotypeAnalysisRequest) -> GenotypeAnalysisResult:
        """
        Analyze capsule genotypes.
        
        Args:
            request: The analysis request
            
        Returns:
            GenotypeAnalysisResult: The analysis result
        """
        analysis_id = f"analysis-{uuid.uuid4()}"
        
        # Get the genotypes to analyze
        genotype_list = []
        for genotype_id in request.genotype_ids:
            if genotype_id in genotypes:
                genotype_list.append(CapsuleGenotype(**genotypes[genotype_id]))
        
        if not genotype_list:
            # No valid genotypes to analyze
            return GenotypeAnalysisResult(
                analysis_id=analysis_id,
                genotype_ids=request.genotype_ids,
                analysis_type=request.analysis_type,
                results={"error": "No valid genotypes found for analysis"}
            )
        
        # Perform the requested analysis
        results = {}
        
        if request.analysis_type == "trait_distribution":
            results = self._analyze_trait_distribution(genotype_list, request.parameters)
        elif request.analysis_type == "fitness_correlation":
            results = self._analyze_fitness_correlation(genotype_list, request.parameters)
        elif request.analysis_type == "genetic_diversity":
            results = self._analyze_genetic_diversity(genotype_list, request.parameters)
        elif request.analysis_type == "lineage_analysis":
            results = self._analyze_lineage(genotype_list, request.parameters)
        else:
            results = {"error": f"Unknown analysis type: {request.analysis_type}"}
        
        # Create the analysis result
        analysis_result = GenotypeAnalysisResult(
            analysis_id=analysis_id,
            genotype_ids=request.genotype_ids,
            analysis_type=request.analysis_type,
            results=results
        )
        
        # Store the analysis result
        genotype_analyses[analysis_id] = analysis_result.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-genotype-analyses",
            key=analysis_id,
            value=json.dumps({
                "analysis_id": analysis_id,
                "analysis_type": request.analysis_type,
                "genotype_count": len(genotype_list)
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "genotype_analysis_completed",
            "analysis_id": analysis_id,
            "analysis_type": request.analysis_type,
            "genotype_count": len(genotype_list)
        }
        mcp_bridge.send_context_update("capsule_genotype_manager", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="capsule_genotype_manager",
            message={
                "type": "genotype_analysis_completed",
                "analysis_id": analysis_id,
                "analysis_type": request.analysis_type,
                "genotype_count": len(genotype_list)
            }
        )
        
        return analysis_result
    
    def get_analysis_result(self, analysis_id: str) -> Optional[GenotypeAnalysisResult]:
        """
        Get an analysis result by ID.
        
        Args:
            analysis_id: The analysis ID
            
        Returns:
            Optional[GenotypeAnalysisResult]: The analysis result, or None if not found
        """
        if analysis_id not in genotype_analyses:
            return None
        
        return GenotypeAnalysisResult(**genotype_analyses[analysis_id])
    
    def _analyze_trait_distribution(
        self, 
        genotypes: List[CapsuleGenotype], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze the distribution of trait values across genotypes.
        
        Args:
            genotypes: List of genotypes to analyze
            parameters: Analysis parameters
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Get the traits to analyze
        trait_keys = set()
        for genotype in genotypes:
            trait_keys.update(genotype.traits.keys())
        
        # Filter traits if specified
        if "trait_filter" in parameters and parameters["trait_filter"]:
            trait_filter = parameters["trait_filter"]
            trait_keys = {k for k in trait_keys if k in trait_filter}
        
        # Analyze distribution for each trait
        trait_distributions = {}
        
        for trait_key in trait_keys:
            # Count occurrences of each value
            value_counts = {}
            
            for genotype in genotypes:
                if trait_key in genotype.traits:
                    value = genotype.traits[trait_key]
                    
                    # Convert value to string for counting
                    value_str = str(value)
                    
                    if value_str in value_counts:
                        value_counts[value_str] += 1
                    else:
                        value_counts[value_str] = 1
            
            # Calculate statistics
            total_count = sum(value_counts.values())
            distribution = {
                "value_counts": value_counts,
                "total_count": total_count,
                "unique_values": len(value_counts)
            }
            
            trait_distributions[trait_key] = distribution
        
        return {
            "trait_distributions": trait_distributions,
            "analyzed_traits": len(trait_distributions),
            "total_genotypes": len(genotypes)
        }
    
    def _analyze_fitness_correlation(
        self, 
        genotypes: List[CapsuleGenotype], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze correlation between trait values and fitness scores.
        
        Args:
            genotypes: List of genotypes to analyze
            parameters: Analysis parameters
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Get the traits to analyze
        trait_keys = set()
        for genotype in genotypes:
            trait_keys.update(genotype.traits.keys())
        
        # Filter traits if specified
        if "trait_filter" in parameters and parameters["trait_filter"]:
            trait_filter = parameters["trait_filter"]
            trait_keys = {k for k in trait_keys if k in trait_filter}
        
        # Analyze correlation for each trait
        trait_correlations = {}
        
        for trait_key in trait_keys:
            # Collect trait values and fitness scores
            trait_values = []
            fitness_scores = []
            
            for genotype in genotypes:
                if trait_key in genotype.traits:
                    value = genotype.traits[trait_key]
                    
                    # Only analyze numeric traits
                    if isinstance(value, (int, float)):
                        trait_values.append(value)
                        fitness_scores.append(genotype.fitness_score)
            
            # Calculate correlation if enough data points
            if len(trait_values) >= 2:
                # Simple correlation calculation
                # (would use scipy.stats.pearsonr in production)
                mean_trait = sum(trait_values) / len(trait_values)
                mean_fitness = sum(fitness_scores) / len(fitness_scores)
                
                numerator = sum((t - mean_trait) * (f - mean_fitness) for t, f in zip(trait_values, fitness_scores))
                denominator_trait = sum((t - mean_trait) ** 2 for t in trait_values)
                denominator_fitness = sum((f - mean_fitness) ** 2 for f in fitness_scores)
                
                if denominator_trait > 0 and denominator_fitness > 0:
                    correlation = numerator / ((denominator_trait ** 0.5) * (denominator_fitness ** 0.5))
                else:
                    correlation = 0.0
                
                trait_correlations[trait_key] = {
                    "correlation": correlation,
                    "data_points": len(trait_values),
                    "significance": "high" if abs(correlation) > 0.7 else "medium" if abs(correlation) > 0.3 else "low"
                }
        
        # Sort traits by absolute correlation (highest first)
        sorted_correlations = sorted(
            trait_correlations.items(),
            key=lambda x: abs(x[1]["correlation"]),
            reverse=True
        )
        
        return {
            "trait_correlations": dict(sorted_correlations),
            "analyzed_traits": len(trait_correlations),
            "total_genotypes": len(genotypes)
        }
    
    def _analyze_genetic_diversity(
        self, 
        genotypes: List[CapsuleGenotype], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze genetic diversity across genotypes.
        
        Args:
            genotypes: List of genotypes to analyze
            parameters: Analysis parameters
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Get the traits to analyze
        trait_keys = set()
        for genotype in genotypes:
            trait_keys.update(genotype.traits.keys())
        
        # Calculate diversity metrics
        trait_coverage = {}  # Percentage of genotypes with each trait
        unique_values = {}   # Number of unique values for each trait
        
        for trait_key in trait_keys:
            # Count genotypes with this trait
            genotypes_with_trait = sum(1 for g in genotypes if trait_key in g.traits)
            coverage = genotypes_with_trait / len(genotypes)
            
            # Count unique values
            values = set()
            for genotype in genotypes:
                if trait_key in genotype.traits:
                    # Convert value to string for set membership
                    values.add(str(genotype.traits[trait_key]))
            
            trait_coverage[trait_key] = coverage
            unique_values[trait_key] = len(values)
        
        # Calculate industry and capability tag diversity
        industry_tags = set()
        capability_tags = set()
        
        for genotype in genotypes:
            industry_tags.update(genotype.industry_tags)
            capability_tags.update(genotype.capability_tags)
        
        # Calculate overall diversity score
        # Simple metric: average of normalized unique values across traits
        if trait_keys:
            trait_diversity = sum(unique_values.values()) / (len(genotypes) * len(trait_keys))
        else:
            trait_diversity = 0.0
        
        # Normalize to 0-1 range
        trait_diversity = min(1.0, trait_diversity)
        
        return {
            "trait_coverage": trait_coverage,
            "unique_values": unique_values,
            "industry_tags": list(industry_tags),
            "capability_tags": list(capability_tags),
            "industry_tag_count": len(industry_tags),
            "capability_tag_count": len(capability_tags),
            "trait_diversity_score": trait_diversity,
            "analyzed_traits": len(trait_keys),
            "total_genotypes": len(genotypes)
        }
    
    def _analyze_lineage(
        self, 
        genotypes: List[CapsuleGenotype], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze lineage relationships between genotypes.
        
        Args:
            genotypes: List of genotypes to analyze
            parameters: Analysis parameters
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Build genotype ID lookup
        genotype_lookup = {g.genotype_id: g for g in genotypes}
        
        # Build parent-child relationships
        parent_to_children = {}
        child_to_parents = {}
        
        for genotype in genotypes:
            child_id = genotype.genotype_id
            
            # Record child-to-parents relationship
            child_to_parents[child_id] = genotype.parent_genotypes
            
            # Record parent-to-children relationships
            for parent_id in genotype.parent_genotypes:
                if parent_id in parent_to_children:
                    parent_to_children[parent_id].append(child_id)
                else:
                    parent_to_children[parent_id] = [child_id]
        
        # Identify root genotypes (no parents or parents not in the analyzed set)
        root_genotypes = []
        for genotype in genotypes:
            if not genotype.parent_genotypes or not any(p in genotype_lookup for p in genotype.parent_genotypes):
                root_genotypes.append(genotype.genotype_id)
        
        # Identify leaf genotypes (no children)
        leaf_genotypes = []
        for genotype in genotypes:
            if genotype.genotype_id not in parent_to_children:
                leaf_genotypes.append(genotype.genotype_id)
        
        # Calculate lineage depth for each genotype
        lineage_depths = {}
        
        def calculate_depth(genotype_id, visited=None):
            if visited is None:
                visited = set()
            
            # Prevent cycles
            if genotype_id in visited:
                return 0
            
            visited.add(genotype_id)
            
            # If no parents, depth is 0
            if genotype_id not in child_to_parents or not child_to_parents[genotype_id]:
                return 0
            
            # Calculate maximum depth of parents
            parent_depths = []
            for parent_id in child_to_parents[genotype_id]:
                if parent_id in genotype_lookup:
                    parent_depths.append(calculate_depth(parent_id, visited.copy()))
            
            # Depth is 1 + maximum parent depth
            return 1 + (max(parent_depths) if parent_depths else 0)
        
        for genotype in genotypes:
            lineage_depths[genotype.genotype_id] = calculate_depth(genotype.genotype_id)
        
        # Calculate maximum lineage depth
        max_depth = max(lineage_depths.values()) if lineage_depths else 0
        
        # Build lineage graph
        lineage_graph = {
            "nodes": [
                {
                    "id": g.genotype_id,
                    "name": g.name,
                    "fitness": g.fitness_score,
                    "depth": lineage_depths[g.genotype_id],
                    "is_root": g.genotype_id in root_genotypes,
                    "is_leaf": g.genotype_id in leaf_genotypes
                }
                for g in genotypes
            ],
            "edges": [
                {
                    "source": parent_id,
                    "target": child_id
                }
                for parent_id, children in parent_to_children.items()
                for child_id in children
                if parent_id in genotype_lookup and child_id in genotype_lookup
            ]
        }
        
        return {
            "lineage_graph": lineage_graph,
            "root_genotypes": root_genotypes,
            "leaf_genotypes": leaf_genotypes,
            "max_depth": max_depth,
            "lineage_depths": lineage_depths,
            "total_genotypes": len(genotypes)
        }

class CapsuleGenotypeManager:
    """
    Capsule Genotype Manager implementation for the Overseer System.
    
    This class provides methods for managing capsule genotypes, including:
    - Defining genotype traits
    - Creating and managing genotypes
    - Analyzing genotypes
    - Visualizing genotype data
    """
    
    def __init__(self):
        """Initialize the Capsule Genotype Manager."""
        self.definition_manager = GenotypeDefinitionManager()
        self.storage_manager = GenotypeStorageManager()
        self.analysis_manager = GenotypeAnalysisManager()
        logger.info("Capsule Genotype Manager initialized")
    
    def create_trait_definition(self, trait_def: GenotypeTraitDefinition) -> str:
        """
        Create a new genotype trait definition.
        
        Args:
            trait_def: The trait definition to create
            
        Returns:
            str: The trait ID
        """
        return self.definition_manager.create_trait_definition(trait_def)
    
    def get_trait_definition(self, trait_id: str) -> Optional[GenotypeTraitDefinition]:
        """
        Get a genotype trait definition by ID.
        
        Args:
            trait_id: The trait ID
            
        Returns:
            Optional[GenotypeTraitDefinition]: The trait definition, or None if not found
        """
        return self.definition_manager.get_trait_definition(trait_id)
    
    def update_trait_definition(self, trait_id: str, trait_def: GenotypeTraitDefinition) -> bool:
        """
        Update a genotype trait definition.
        
        Args:
            trait_id: The trait ID to update
            trait_def: The updated trait definition
            
        Returns:
            bool: True if successful, False if trait not found
        """
        return self.definition_manager.update_trait_definition(trait_id, trait_def)
    
    def delete_trait_definition(self, trait_id: str) -> bool:
        """
        Delete a genotype trait definition.
        
        Args:
            trait_id: The trait ID to delete
            
        Returns:
            bool: True if successful, False if trait not found
        """
        return self.definition_manager.delete_trait_definition(trait_id)
    
    def list_trait_definitions(
        self,
        name_filter: Optional[str] = None,
        value_type_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[GenotypeTraitDefinition]:
        """
        List genotype trait definitions, optionally filtered.
        
        Args:
            name_filter: Optional filter for trait name (case-insensitive substring match)
            value_type_filter: Optional filter for value type
            limit: Maximum number of traits to return
            
        Returns:
            List[GenotypeTraitDefinition]: List of matching trait definitions
        """
        return self.definition_manager.list_trait_definitions(
            name_filter=name_filter,
            value_type_filter=value_type_filter,
            limit=limit
        )
    
    def create_genotype(self, genotype: CapsuleGenotype) -> str:
        """
        Create a new capsule genotype.
        
        Args:
            genotype: The genotype to create
            
        Returns:
            str: The genotype ID
        """
        return self.storage_manager.create_genotype(genotype)
    
    def get_genotype(self, genotype_id: str) -> Optional[CapsuleGenotype]:
        """
        Get a capsule genotype by ID.
        
        Args:
            genotype_id: The genotype ID
            
        Returns:
            Optional[CapsuleGenotype]: The genotype, or None if not found
        """
        return self.storage_manager.get_genotype(genotype_id)
    
    def update_genotype(self, genotype_id: str, genotype: CapsuleGenotype) -> bool:
        """
        Update a capsule genotype.
        
        Args:
            genotype_id: The genotype ID to update
            genotype: The updated genotype
            
        Returns:
            bool: True if successful, False if genotype not found
        """
        return self.storage_manager.update_genotype(genotype_id, genotype)
    
    def delete_genotype(self, genotype_id: str) -> bool:
        """
        Delete a capsule genotype.
        
        Args:
            genotype_id: The genotype ID to delete
            
        Returns:
            bool: True if successful, False if genotype not found
        """
        return self.storage_manager.delete_genotype(genotype_id)
    
    def list_genotypes(
        self,
        name_filter: Optional[str] = None,
        industry_tag_filter: Optional[str] = None,
        capability_tag_filter: Optional[str] = None,
        min_fitness_score: Optional[float] = None,
        limit: int = 100
    ) -> List[CapsuleGenotype]:
        """
        List capsule genotypes, optionally filtered.
        
        Args:
            name_filter: Optional filter for genotype name (case-insensitive substring match)
            industry_tag_filter: Optional filter for industry tag
            capability_tag_filter: Optional filter for capability tag
            min_fitness_score: Optional minimum fitness score
            limit: Maximum number of genotypes to return
            
        Returns:
            List[CapsuleGenotype]: List of matching genotypes
        """
        return self.storage_manager.list_genotypes(
            name_filter=name_filter,
            industry_tag_filter=industry_tag_filter,
            capability_tag_filter=capability_tag_filter,
            min_fitness_score=min_fitness_score,
            limit=limit
        )
    
    def analyze_genotypes(self, request: GenotypeAnalysisRequest) -> GenotypeAnalysisResult:
        """
        Analyze capsule genotypes.
        
        Args:
            request: The analysis request
            
        Returns:
            GenotypeAnalysisResult: The analysis result
        """
        return self.analysis_manager.analyze_genotypes(request)
    
    def get_analysis_result(self, analysis_id: str) -> Optional[GenotypeAnalysisResult]:
        """
        Get an analysis result by ID.
        
        Args:
            analysis_id: The analysis ID
            
        Returns:
            Optional[GenotypeAnalysisResult]: The analysis result, or None if not found
        """
        return self.analysis_manager.get_analysis_result(analysis_id)
    
    def validate_genotype(self, genotype: CapsuleGenotype) -> Tuple[bool, List[str]]:
        """
        Validate a capsule genotype against trait definitions.
        
        Args:
            genotype: The genotype to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of validation errors)
        """
        errors = []
        
        # Check required fields
        if not genotype.name:
            errors.append("Genotype name is required")
        
        if not genotype.description:
            errors.append("Genotype description is required")
        
        if not genotype.version:
            errors.append("Genotype version is required")
        
        # Validate traits against definitions
        for trait_id, trait_value in genotype.traits.items():
            trait_def = self.definition_manager.get_trait_definition(trait_id)
            
            if trait_def is None:
                errors.append(f"Unknown trait: {trait_id}")
                continue
            
            # Validate value type
            if trait_def.value_type == "string" and not isinstance(trait_value, str):
                errors.append(f"Trait {trait_id} should be a string")
            elif trait_def.value_type == "number" and not isinstance(trait_value, (int, float)):
                errors.append(f"Trait {trait_id} should be a number")
            elif trait_def.value_type == "boolean" and not isinstance(trait_value, bool):
                errors.append(f"Trait {trait_id} should be a boolean")
            elif trait_def.value_type == "object" and not isinstance(trait_value, dict):
                errors.append(f"Trait {trait_id} should be an object")
            elif trait_def.value_type == "array" and not isinstance(trait_value, list):
                errors.append(f"Trait {trait_id} should be an array")
            
            # Validate constraints
            if trait_def.constraints:
                if trait_def.value_type == "string" and isinstance(trait_value, str):
                    if "min_length" in trait_def.constraints and len(trait_value) < trait_def.constraints["min_length"]:
                        errors.append(f"Trait {trait_id} should have minimum length of {trait_def.constraints['min_length']}")
                    
                    if "max_length" in trait_def.constraints and len(trait_value) > trait_def.constraints["max_length"]:
                        errors.append(f"Trait {trait_id} should have maximum length of {trait_def.constraints['max_length']}")
                    
                    if "pattern" in trait_def.constraints:
                        # Would use re.match in production
                        if not trait_value.startswith(trait_def.constraints["pattern"]):
                            errors.append(f"Trait {trait_id} should match pattern {trait_def.constraints['pattern']}")
                
                elif trait_def.value_type == "number" and isinstance(trait_value, (int, float)):
                    if "minimum" in trait_def.constraints and trait_value < trait_def.constraints["minimum"]:
                        errors.append(f"Trait {trait_id} should be at least {trait_def.constraints['minimum']}")
                    
                    if "maximum" in trait_def.constraints and trait_value > trait_def.constraints["maximum"]:
                        errors.append(f"Trait {trait_id} should be at most {trait_def.constraints['maximum']}")
                
                elif trait_def.value_type == "array" and isinstance(trait_value, list):
                    if "min_items" in trait_def.constraints and len(trait_value) < trait_def.constraints["min_items"]:
                        errors.append(f"Trait {trait_id} should have at least {trait_def.constraints['min_items']} items")
                    
                    if "max_items" in trait_def.constraints and len(trait_value) > trait_def.constraints["max_items"]:
                        errors.append(f"Trait {trait_id} should have at most {trait_def.constraints['max_items']} items")
        
        # Validate parent genotypes
        for parent_id in genotype.parent_genotypes:
            parent = self.storage_manager.get_genotype(parent_id)
            
            if parent is None:
                errors.append(f"Unknown parent genotype: {parent_id}")
        
        return (len(errors) == 0, errors)
    
    def calculate_fitness_score(self, genotype: CapsuleGenotype) -> float:
        """
        Calculate a fitness score for a genotype based on its traits.
        
        Args:
            genotype: The genotype to evaluate
            
        Returns:
            float: The calculated fitness score (0.0 to 1.0)
        """
        # This is a simplified fitness calculation
        # In production, this would be a more sophisticated algorithm
        
        # Base score
        score = 0.5
        
        # Adjust based on trait completeness
        trait_defs = self.definition_manager.list_trait_definitions(limit=1000)
        if trait_defs:
            coverage = len(genotype.traits) / len(trait_defs)
            score += 0.2 * coverage
        
        # Adjust based on industry and capability tags
        if genotype.industry_tags:
            score += 0.1
        
        if genotype.capability_tags:
            score += 0.1
        
        # Adjust based on lineage (having parents is good)
        if genotype.parent_genotypes:
            score += 0.1
        
        # Ensure score is in 0.0 to 1.0 range
        return max(0.0, min(1.0, score))
    
    def generate_visualization_data(self, genotype_ids: List[str]) -> Dict[str, Any]:
        """
        Generate visualization data for genotypes.
        
        Args:
            genotype_ids: List of genotype IDs to visualize
            
        Returns:
            Dict[str, Any]: Visualization data
        """
        # Get the genotypes to visualize
        genotype_list = []
        for genotype_id in genotype_ids:
            genotype = self.storage_manager.get_genotype(genotype_id)
            if genotype:
                genotype_list.append(genotype)
        
        if not genotype_list:
            return {"error": "No valid genotypes found for visualization"}
        
        # Generate lineage graph
        lineage_request = GenotypeAnalysisRequest(
            genotype_ids=genotype_ids,
            analysis_type="lineage_analysis",
            parameters={}
        )
        lineage_result = self.analysis_manager.analyze_genotypes(lineage_request)
        
        # Generate trait distribution data
        trait_request = GenotypeAnalysisRequest(
            genotype_ids=genotype_ids,
            analysis_type="trait_distribution",
            parameters={}
        )
        trait_result = self.analysis_manager.analyze_genotypes(trait_request)
        
        # Generate fitness data
        fitness_data = [
            {
                "id": g.genotype_id,
                "name": g.name,
                "fitness": g.fitness_score,
                "industry_tags": g.industry_tags,
                "capability_tags": g.capability_tags
            }
            for g in genotype_list
        ]
        
        # Sort by fitness score (highest first)
        fitness_data.sort(key=lambda x: x["fitness"], reverse=True)
        
        return {
            "lineage_graph": lineage_result.results.get("lineage_graph", {}),
            "trait_distributions": trait_result.results.get("trait_distributions", {}),
            "fitness_data": fitness_data,
            "genotype_count": len(genotype_list)
        }
