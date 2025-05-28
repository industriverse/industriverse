"""
Trust Relationship Graph for the Overseer System.

This module provides a comprehensive trust relationship graph implementation for the Overseer System,
enabling the visualization, analysis, and management of trust relationships between entities.

The Trust Relationship Graph is a critical component of the Trust Management framework,
providing insights into trust relationships and enabling trust-based decision making.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any, Set

import networkx as nx
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from pydantic import BaseModel, Field

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
logger = logging.getLogger("trust_relationship_graph")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="trust-relationship-graph"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="trust-relationship-graph",
    auto_offset_reset="earliest"
)

# Data models
class Entity(BaseModel):
    """Model for entities in the trust graph."""
    entity_id: str = Field(..., description="Unique entity identifier")
    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type (agent, service, user, etc.)")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Entity attributes")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TrustRelationship(BaseModel):
    """Model for trust relationships between entities."""
    relationship_id: str = Field(..., description="Unique relationship identifier")
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    trust_score: float = Field(..., ge=0.0, le=1.0, description="Trust score (0.0-1.0)")
    relationship_type: str = Field(..., description="Type of relationship")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Relationship attributes")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    expiration: Optional[datetime] = Field(None, description="Expiration timestamp, if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PathQuery(BaseModel):
    """Model for trust path queries."""
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    min_trust_score: float = Field(0.0, ge=0.0, le=1.0, description="Minimum trust score for edges")
    max_path_length: int = Field(5, ge=1, description="Maximum path length")
    relationship_types: Optional[List[str]] = Field(None, description="Relationship types to consider")

class TrustPath(BaseModel):
    """Model for trust paths between entities."""
    path_id: str = Field(..., description="Unique path identifier")
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    path: List[str] = Field(..., description="List of entity IDs in the path")
    relationships: List[str] = Field(..., description="List of relationship IDs in the path")
    aggregate_trust: float = Field(..., ge=0.0, le=1.0, description="Aggregate trust score for the path")
    path_length: int = Field(..., ge=1, description="Path length")
    timestamp: datetime = Field(default_factory=datetime.now, description="Computation timestamp")

class GraphStats(BaseModel):
    """Model for trust graph statistics."""
    entity_count: int = Field(..., description="Number of entities in the graph")
    relationship_count: int = Field(..., description="Number of relationships in the graph")
    average_trust_score: float = Field(..., description="Average trust score across all relationships")
    highest_trust_score: float = Field(..., description="Highest trust score in the graph")
    lowest_trust_score: float = Field(..., description="Lowest trust score in the graph")
    most_trusted_entity: Optional[str] = Field(None, description="Entity with highest average incoming trust")
    most_trusting_entity: Optional[str] = Field(None, description="Entity with highest average outgoing trust")
    timestamp: datetime = Field(default_factory=datetime.now, description="Computation timestamp")

class TrustRelationshipGraph:
    """
    Trust Relationship Graph implementation for the Overseer System.
    
    This class provides methods for managing the trust relationship graph, including:
    - Adding and removing entities and relationships
    - Querying trust paths between entities
    - Computing trust metrics and statistics
    - Analyzing trust network properties
    """
    
    def __init__(self):
        """Initialize the Trust Relationship Graph."""
        # Initialize the graph using NetworkX
        self.graph = nx.DiGraph()
        
        # In-memory storage for entities and relationships
        self.entities = {}
        self.relationships = {}
        
        # Cache for computed paths
        self.path_cache = {}
        
        logger.info("Trust Relationship Graph initialized")
    
    def add_entity(self, entity: Entity) -> str:
        """
        Add an entity to the trust graph.
        
        Args:
            entity: The entity to add
            
        Returns:
            str: Entity ID
        """
        entity_dict = entity.dict()
        
        # Generate entity ID if not provided
        if not entity.entity_id:
            entity_dict["entity_id"] = f"entity-{uuid.uuid4()}"
        
        entity_id = entity_dict["entity_id"]
        
        # Set timestamps
        now = datetime.now()
        entity_dict["created_at"] = now.isoformat()
        entity_dict["updated_at"] = now.isoformat()
        
        # Store the entity
        self.entities[entity_id] = entity_dict
        
        # Add to graph
        self.graph.add_node(entity_id, **entity_dict)
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="entity-events",
            key=entity_id,
            value=json.dumps({
                "event_type": "entity_added",
                "entity_id": entity_id,
                "name": entity.name,
                "type": entity.type,
                "timestamp": now.isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "entity_added",
            "entity_id": entity_id,
            "name": entity.name,
            "type": entity.type
        }
        mcp_bridge.send_context_update("trust_relationship_graph", mcp_context)
        
        return entity_id
    
    def update_entity(self, entity_id: str, entity: Entity) -> bool:
        """
        Update an existing entity in the trust graph.
        
        Args:
            entity_id: The ID of the entity to update
            entity: The updated entity
            
        Returns:
            bool: Whether the update was successful
        """
        if entity_id not in self.entities:
            return False
        
        # Get existing entity
        existing_entity = self.entities[entity_id]
        
        # Create updated entity
        entity_dict = entity.dict()
        entity_dict["entity_id"] = entity_id  # Ensure ID remains the same
        entity_dict["created_at"] = existing_entity["created_at"]  # Preserve creation timestamp
        entity_dict["updated_at"] = datetime.now().isoformat()  # Update modification timestamp
        
        # Store the updated entity
        self.entities[entity_id] = entity_dict
        
        # Update in graph
        for key, value in entity_dict.items():
            self.graph.nodes[entity_id][key] = value
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="entity-events",
            key=entity_id,
            value=json.dumps({
                "event_type": "entity_updated",
                "entity_id": entity_id,
                "name": entity.name,
                "type": entity.type,
                "timestamp": entity_dict["updated_at"]
            })
        )
        
        return True
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            Optional[Entity]: The entity, or None if not found
        """
        if entity_id not in self.entities:
            return None
        
        return Entity(**self.entities[entity_id])
    
    def list_entities(self, entity_type: Optional[str] = None) -> List[Entity]:
        """
        List entities, optionally filtered by type.
        
        Args:
            entity_type: Optional entity type to filter by
            
        Returns:
            List[Entity]: List of matching entities
        """
        results = []
        
        for entity_dict in self.entities.values():
            # Apply filter
            if entity_type and entity_dict["type"] != entity_type:
                continue
            
            results.append(Entity(**entity_dict))
        
        return results
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity from the trust graph.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            bool: Whether the deletion was successful
        """
        if entity_id not in self.entities:
            return False
        
        # Get entity details for event
        entity_name = self.entities[entity_id]["name"]
        entity_type = self.entities[entity_id]["type"]
        
        # Find and delete all relationships involving this entity
        relationships_to_delete = []
        
        for rel_id, rel in self.relationships.items():
            if rel["source_id"] == entity_id or rel["target_id"] == entity_id:
                relationships_to_delete.append(rel_id)
        
        for rel_id in relationships_to_delete:
            self.delete_relationship(rel_id)
        
        # Delete the entity
        del self.entities[entity_id]
        
        # Remove from graph
        self.graph.remove_node(entity_id)
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="entity-events",
            key=entity_id,
            value=json.dumps({
                "event_type": "entity_deleted",
                "entity_id": entity_id,
                "name": entity_name,
                "type": entity_type,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        return True
    
    def add_relationship(self, relationship: TrustRelationship) -> str:
        """
        Add a trust relationship to the graph.
        
        Args:
            relationship: The relationship to add
            
        Returns:
            str: Relationship ID
        """
        relationship_dict = relationship.dict()
        
        # Generate relationship ID if not provided
        if not relationship.relationship_id:
            relationship_dict["relationship_id"] = f"rel-{uuid.uuid4()}"
        
        relationship_id = relationship_dict["relationship_id"]
        source_id = relationship.source_id
        target_id = relationship.target_id
        
        # Verify that source and target entities exist
        if source_id not in self.entities:
            raise ValueError(f"Source entity {source_id} does not exist")
        
        if target_id not in self.entities:
            raise ValueError(f"Target entity {target_id} does not exist")
        
        # Set timestamps
        now = datetime.now()
        relationship_dict["created_at"] = now.isoformat()
        relationship_dict["updated_at"] = now.isoformat()
        
        # Store the relationship
        self.relationships[relationship_id] = relationship_dict
        
        # Add to graph
        self.graph.add_edge(
            source_id, 
            target_id, 
            relationship_id=relationship_id,
            trust_score=relationship.trust_score,
            relationship_type=relationship.relationship_type,
            **relationship_dict
        )
        
        # Invalidate path cache
        self.path_cache = {}
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="relationship-events",
            key=relationship_id,
            value=json.dumps({
                "event_type": "relationship_added",
                "relationship_id": relationship_id,
                "source_id": source_id,
                "target_id": target_id,
                "trust_score": relationship.trust_score,
                "relationship_type": relationship.relationship_type,
                "timestamp": now.isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "relationship_added",
            "relationship_id": relationship_id,
            "source_id": source_id,
            "target_id": target_id,
            "trust_score": relationship.trust_score,
            "relationship_type": relationship.relationship_type
        }
        mcp_bridge.send_context_update("trust_relationship_graph", mcp_context)
        
        return relationship_id
    
    def update_relationship(self, relationship_id: str, relationship: TrustRelationship) -> bool:
        """
        Update an existing trust relationship.
        
        Args:
            relationship_id: The ID of the relationship to update
            relationship: The updated relationship
            
        Returns:
            bool: Whether the update was successful
        """
        if relationship_id not in self.relationships:
            return False
        
        # Get existing relationship
        existing_relationship = self.relationships[relationship_id]
        
        # Create updated relationship
        relationship_dict = relationship.dict()
        relationship_dict["relationship_id"] = relationship_id  # Ensure ID remains the same
        relationship_dict["created_at"] = existing_relationship["created_at"]  # Preserve creation timestamp
        relationship_dict["updated_at"] = datetime.now().isoformat()  # Update modification timestamp
        
        source_id = relationship.source_id
        target_id = relationship.target_id
        old_source_id = existing_relationship["source_id"]
        old_target_id = existing_relationship["target_id"]
        
        # Verify that source and target entities exist
        if source_id not in self.entities:
            raise ValueError(f"Source entity {source_id} does not exist")
        
        if target_id not in self.entities:
            raise ValueError(f"Target entity {target_id} does not exist")
        
        # Store the updated relationship
        self.relationships[relationship_id] = relationship_dict
        
        # Update in graph
        # If source or target changed, remove old edge and add new one
        if source_id != old_source_id or target_id != old_target_id:
            self.graph.remove_edge(old_source_id, old_target_id)
            self.graph.add_edge(
                source_id, 
                target_id, 
                relationship_id=relationship_id,
                trust_score=relationship.trust_score,
                relationship_type=relationship.relationship_type,
                **relationship_dict
            )
        else:
            # Just update edge attributes
            for key, value in relationship_dict.items():
                self.graph[source_id][target_id][key] = value
        
        # Invalidate path cache
        self.path_cache = {}
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="relationship-events",
            key=relationship_id,
            value=json.dumps({
                "event_type": "relationship_updated",
                "relationship_id": relationship_id,
                "source_id": source_id,
                "target_id": target_id,
                "trust_score": relationship.trust_score,
                "relationship_type": relationship.relationship_type,
                "timestamp": relationship_dict["updated_at"]
            })
        )
        
        return True
    
    def get_relationship(self, relationship_id: str) -> Optional[TrustRelationship]:
        """
        Get a trust relationship by ID.
        
        Args:
            relationship_id: The relationship ID
            
        Returns:
            Optional[TrustRelationship]: The relationship, or None if not found
        """
        if relationship_id not in self.relationships:
            return None
        
        return TrustRelationship(**self.relationships[relationship_id])
    
    def list_relationships(
        self, 
        source_id: Optional[str] = None, 
        target_id: Optional[str] = None,
        relationship_type: Optional[str] = None,
        min_trust_score: float = 0.0
    ) -> List[TrustRelationship]:
        """
        List trust relationships, optionally filtered.
        
        Args:
            source_id: Optional source entity ID to filter by
            target_id: Optional target entity ID to filter by
            relationship_type: Optional relationship type to filter by
            min_trust_score: Minimum trust score to filter by
            
        Returns:
            List[TrustRelationship]: List of matching relationships
        """
        results = []
        
        for rel_dict in self.relationships.values():
            # Apply filters
            if source_id and rel_dict["source_id"] != source_id:
                continue
            
            if target_id and rel_dict["target_id"] != target_id:
                continue
            
            if relationship_type and rel_dict["relationship_type"] != relationship_type:
                continue
            
            if rel_dict["trust_score"] < min_trust_score:
                continue
            
            results.append(TrustRelationship(**rel_dict))
        
        return results
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """
        Delete a trust relationship.
        
        Args:
            relationship_id: The relationship ID
            
        Returns:
            bool: Whether the deletion was successful
        """
        if relationship_id not in self.relationships:
            return False
        
        # Get relationship details for event and graph removal
        rel = self.relationships[relationship_id]
        source_id = rel["source_id"]
        target_id = rel["target_id"]
        
        # Delete the relationship
        del self.relationships[relationship_id]
        
        # Remove from graph
        self.graph.remove_edge(source_id, target_id)
        
        # Invalidate path cache
        self.path_cache = {}
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="relationship-events",
            key=relationship_id,
            value=json.dumps({
                "event_type": "relationship_deleted",
                "relationship_id": relationship_id,
                "source_id": source_id,
                "target_id": target_id,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        return True
    
    def find_trust_paths(self, query: PathQuery) -> List[TrustPath]:
        """
        Find trust paths between two entities.
        
        Args:
            query: The path query parameters
            
        Returns:
            List[TrustPath]: List of trust paths
        """
        source_id = query.source_id
        target_id = query.target_id
        min_trust_score = query.min_trust_score
        max_path_length = query.max_path_length
        relationship_types = query.relationship_types
        
        # Check if source and target exist
        if source_id not in self.entities:
            raise ValueError(f"Source entity {source_id} does not exist")
        
        if target_id not in self.entities:
            raise ValueError(f"Target entity {target_id} does not exist")
        
        # Check cache
        cache_key = f"{source_id}_{target_id}_{min_trust_score}_{max_path_length}_{relationship_types}"
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
        
        # Create a filtered graph based on trust score and relationship types
        filtered_graph = nx.DiGraph()
        
        for u, v, data in self.graph.edges(data=True):
            # Check trust score
            if data["trust_score"] < min_trust_score:
                continue
            
            # Check relationship type
            if relationship_types and data["relationship_type"] not in relationship_types:
                continue
            
            # Add edge to filtered graph
            filtered_graph.add_edge(u, v, **data)
        
        # Find all simple paths up to max_path_length
        paths = []
        
        try:
            # Use NetworkX to find all simple paths
            simple_paths = list(nx.all_simple_paths(
                filtered_graph, 
                source=source_id, 
                target=target_id, 
                cutoff=max_path_length
            ))
            
            # Convert to TrustPath objects
            for i, path_nodes in enumerate(simple_paths):
                # Get relationships along the path
                relationships = []
                aggregate_trust = 1.0  # Start with perfect trust
                
                for j in range(len(path_nodes) - 1):
                    u = path_nodes[j]
                    v = path_nodes[j + 1]
                    
                    # Get relationship data
                    rel_id = filtered_graph[u][v]["relationship_id"]
                    trust_score = filtered_graph[u][v]["trust_score"]
                    
                    relationships.append(rel_id)
                    
                    # Update aggregate trust (multiplicative)
                    aggregate_trust *= trust_score
                
                # Create TrustPath object
                path = TrustPath(
                    path_id=f"path-{uuid.uuid4()}",
                    source_id=source_id,
                    target_id=target_id,
                    path=path_nodes,
                    relationships=relationships,
                    aggregate_trust=aggregate_trust,
                    path_length=len(path_nodes) - 1
                )
                
                paths.append(path)
            
            # Sort paths by aggregate trust (highest first)
            paths.sort(key=lambda p: p.aggregate_trust, reverse=True)
            
        except nx.NetworkXNoPath:
            # No path exists
            pass
        
        # Cache the result
        self.path_cache[cache_key] = paths
        
        return paths
    
    def get_trust_score(self, source_id: str, target_id: str) -> Optional[float]:
        """
        Get the direct trust score between two entities.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            
        Returns:
            Optional[float]: The trust score, or None if no direct relationship exists
        """
        if not self.graph.has_edge(source_id, target_id):
            return None
        
        return self.graph[source_id][target_id]["trust_score"]
    
    def get_inferred_trust(self, source_id: str, target_id: str) -> Optional[float]:
        """
        Get the inferred trust between two entities based on the best path.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            
        Returns:
            Optional[float]: The inferred trust score, or None if no path exists
        """
        # Find trust paths
        query = PathQuery(
            source_id=source_id,
            target_id=target_id,
            min_trust_score=0.0,
            max_path_length=5
        )
        
        paths = self.find_trust_paths(query)
        
        if not paths:
            return None
        
        # Return the aggregate trust of the best path
        return paths[0].aggregate_trust
    
    def get_graph_stats(self) -> GraphStats:
        """
        Get statistics about the trust graph.
        
        Returns:
            GraphStats: Graph statistics
        """
        # Entity count
        entity_count = len(self.entities)
        
        # Relationship count
        relationship_count = len(self.relationships)
        
        # Trust score statistics
        if relationship_count == 0:
            average_trust_score = 0.0
            highest_trust_score = 0.0
            lowest_trust_score = 0.0
            most_trusted_entity = None
            most_trusting_entity = None
        else:
            trust_scores = [rel["trust_score"] for rel in self.relationships.values()]
            average_trust_score = sum(trust_scores) / len(trust_scores)
            highest_trust_score = max(trust_scores)
            lowest_trust_score = min(trust_scores)
            
            # Calculate average incoming and outgoing trust for each entity
            incoming_trust = {}
            outgoing_trust = {}
            
            for rel in self.relationships.values():
                source_id = rel["source_id"]
                target_id = rel["target_id"]
                trust_score = rel["trust_score"]
                
                # Update incoming trust for target
                if target_id not in incoming_trust:
                    incoming_trust[target_id] = []
                incoming_trust[target_id].append(trust_score)
                
                # Update outgoing trust for source
                if source_id not in outgoing_trust:
                    outgoing_trust[source_id] = []
                outgoing_trust[source_id].append(trust_score)
            
            # Calculate averages
            avg_incoming_trust = {
                entity_id: sum(scores) / len(scores)
                for entity_id, scores in incoming_trust.items()
            }
            
            avg_outgoing_trust = {
                entity_id: sum(scores) / len(scores)
                for entity_id, scores in outgoing_trust.items()
            }
            
            # Find entities with highest average trust
            if avg_incoming_trust:
                most_trusted_entity = max(avg_incoming_trust.items(), key=lambda x: x[1])[0]
            else:
                most_trusted_entity = None
            
            if avg_outgoing_trust:
                most_trusting_entity = max(avg_outgoing_trust.items(), key=lambda x: x[1])[0]
            else:
                most_trusting_entity = None
        
        return GraphStats(
            entity_count=entity_count,
            relationship_count=relationship_count,
            average_trust_score=average_trust_score,
            highest_trust_score=highest_trust_score,
            lowest_trust_score=lowest_trust_score,
            most_trusted_entity=most_trusted_entity,
            most_trusting_entity=most_trusting_entity
        )
    
    def get_entity_trust_metrics(self, entity_id: str) -> Dict[str, Any]:
        """
        Get trust metrics for a specific entity.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            Dict[str, Any]: Trust metrics for the entity
        """
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        # Get incoming and outgoing relationships
        incoming_relationships = self.list_relationships(target_id=entity_id)
        outgoing_relationships = self.list_relationships(source_id=entity_id)
        
        # Calculate average trust scores
        incoming_trust_scores = [rel.trust_score for rel in incoming_relationships]
        outgoing_trust_scores = [rel.trust_score for rel in outgoing_relationships]
        
        avg_incoming_trust = sum(incoming_trust_scores) / len(incoming_trust_scores) if incoming_trust_scores else 0.0
        avg_outgoing_trust = sum(outgoing_trust_scores) / len(outgoing_trust_scores) if outgoing_trust_scores else 0.0
        
        # Calculate centrality metrics
        try:
            # Degree centrality
            in_degree = self.graph.in_degree(entity_id)
            out_degree = self.graph.out_degree(entity_id)
            
            # Betweenness centrality (normalized)
            betweenness = nx.betweenness_centrality(self.graph, normalized=True).get(entity_id, 0.0)
            
            # PageRank (as a measure of importance)
            pagerank = nx.pagerank(self.graph).get(entity_id, 0.0)
            
        except Exception as e:
            logger.error(f"Error calculating centrality metrics: {e}")
            in_degree = 0
            out_degree = 0
            betweenness = 0.0
            pagerank = 0.0
        
        return {
            "entity_id": entity_id,
            "incoming_relationships": len(incoming_relationships),
            "outgoing_relationships": len(outgoing_relationships),
            "avg_incoming_trust": avg_incoming_trust,
            "avg_outgoing_trust": avg_outgoing_trust,
            "in_degree": in_degree,
            "out_degree": out_degree,
            "betweenness_centrality": betweenness,
            "pagerank": pagerank,
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_trust_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect anomalies in the trust graph.
        
        Returns:
            List[Dict[str, Any]]: List of detected anomalies
        """
        anomalies = []
        
        # Get graph statistics
        stats = self.get_graph_stats()
        avg_trust = stats.average_trust_score
        
        # Check for isolated entities (no relationships)
        for entity_id, entity in self.entities.items():
            in_degree = self.graph.in_degree(entity_id)
            out_degree = self.graph.out_degree(entity_id)
            
            if in_degree == 0 and out_degree == 0:
                anomalies.append({
                    "anomaly_type": "isolated_entity",
                    "entity_id": entity_id,
                    "entity_name": entity["name"],
                    "entity_type": entity["type"],
                    "severity": "medium",
                    "description": f"Entity {entity['name']} is isolated with no trust relationships"
                })
        
        # Check for extremely low trust relationships
        for rel_id, rel in self.relationships.items():
            if rel["trust_score"] < 0.2:  # Arbitrary threshold
                anomalies.append({
                    "anomaly_type": "low_trust_relationship",
                    "relationship_id": rel_id,
                    "source_id": rel["source_id"],
                    "target_id": rel["target_id"],
                    "trust_score": rel["trust_score"],
                    "severity": "high" if rel["trust_score"] < 0.1 else "medium",
                    "description": f"Very low trust relationship ({rel['trust_score']}) between {rel['source_id']} and {rel['target_id']}"
                })
        
        # Check for trust asymmetry (A trusts B much more than B trusts A)
        for source_id in self.entities:
            for target_id in self.entities:
                if source_id == target_id:
                    continue
                
                forward_trust = self.get_trust_score(source_id, target_id)
                backward_trust = self.get_trust_score(target_id, source_id)
                
                if forward_trust is not None and backward_trust is not None:
                    trust_diff = abs(forward_trust - backward_trust)
                    
                    if trust_diff > 0.4:  # Arbitrary threshold
                        anomalies.append({
                            "anomaly_type": "trust_asymmetry",
                            "source_id": source_id,
                            "target_id": target_id,
                            "forward_trust": forward_trust,
                            "backward_trust": backward_trust,
                            "trust_difference": trust_diff,
                            "severity": "high" if trust_diff > 0.6 else "medium",
                            "description": f"High trust asymmetry between {source_id} and {target_id} (difference: {trust_diff:.2f})"
                        })
        
        # Check for entities with unusually high or low average trust
        for entity_id in self.entities:
            metrics = self.get_entity_trust_metrics(entity_id)
            
            # Check incoming trust
            if metrics["incoming_relationships"] > 0:
                if metrics["avg_incoming_trust"] < avg_trust - 0.3:
                    anomalies.append({
                        "anomaly_type": "low_incoming_trust",
                        "entity_id": entity_id,
                        "avg_incoming_trust": metrics["avg_incoming_trust"],
                        "global_avg_trust": avg_trust,
                        "severity": "medium",
                        "description": f"Entity {entity_id} has unusually low incoming trust ({metrics['avg_incoming_trust']:.2f} vs global avg {avg_trust:.2f})"
                    })
                elif metrics["avg_incoming_trust"] > avg_trust + 0.3:
                    anomalies.append({
                        "anomaly_type": "high_incoming_trust",
                        "entity_id": entity_id,
                        "avg_incoming_trust": metrics["avg_incoming_trust"],
                        "global_avg_trust": avg_trust,
                        "severity": "low",
                        "description": f"Entity {entity_id} has unusually high incoming trust ({metrics['avg_incoming_trust']:.2f} vs global avg {avg_trust:.2f})"
                    })
        
        return anomalies
    
    def export_graph(self, format: str = "json") -> Dict[str, Any]:
        """
        Export the trust graph in various formats.
        
        Args:
            format: Export format (json, graphml, etc.)
            
        Returns:
            Dict[str, Any]: The exported graph data
        """
        if format == "json":
            return {
                "entities": list(self.entities.values()),
                "relationships": list(self.relationships.values()),
                "timestamp": datetime.now().isoformat()
            }
        elif format == "graphml":
            # Convert to NetworkX compatible format
            G = nx.DiGraph()
            
            # Add nodes with attributes
            for entity_id, entity in self.entities.items():
                G.add_node(entity_id, **{k: str(v) for k, v in entity.items()})
            
            # Add edges with attributes
            for rel_id, rel in self.relationships.items():
                source_id = rel["source_id"]
                target_id = rel["target_id"]
                G.add_edge(source_id, target_id, **{k: str(v) for k, v in rel.items()})
            
            # Export to GraphML string
            import io
            output = io.StringIO()
            nx.write_graphml(G, output)
            
            return {
                "graphml": output.getvalue(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_graph(self, data: Dict[str, Any], format: str = "json") -> bool:
        """
        Import a trust graph.
        
        Args:
            data: The graph data to import
            format: Import format (json, graphml, etc.)
            
        Returns:
            bool: Whether the import was successful
        """
        if format == "json":
            # Clear existing data
            self.entities = {}
            self.relationships = {}
            self.graph = nx.DiGraph()
            self.path_cache = {}
            
            # Import entities
            for entity_dict in data.get("entities", []):
                entity = Entity(**entity_dict)
                self.add_entity(entity)
            
            # Import relationships
            for rel_dict in data.get("relationships", []):
                relationship = TrustRelationship(**rel_dict)
                self.add_relationship(relationship)
            
            return True
        elif format == "graphml":
            # Import from GraphML string
            import io
            graphml_data = data.get("graphml", "")
            input_file = io.StringIO(graphml_data)
            
            try:
                G = nx.read_graphml(input_file)
                
                # Clear existing data
                self.entities = {}
                self.relationships = {}
                self.graph = nx.DiGraph()
                self.path_cache = {}
                
                # Import nodes as entities
                for node_id in G.nodes():
                    node_data = G.nodes[node_id]
                    
                    # Convert attributes to appropriate types
                    entity_dict = {
                        "entity_id": node_id,
                        "name": node_data.get("name", f"Entity {node_id}"),
                        "type": node_data.get("type", "unknown"),
                        "attributes": {},
                        "metadata": {}
                    }
                    
                    entity = Entity(**entity_dict)
                    self.add_entity(entity)
                
                # Import edges as relationships
                for source_id, target_id, edge_data in G.edges(data=True):
                    # Convert attributes to appropriate types
                    rel_dict = {
                        "relationship_id": edge_data.get("relationship_id", f"rel-{uuid.uuid4()}"),
                        "source_id": source_id,
                        "target_id": target_id,
                        "trust_score": float(edge_data.get("trust_score", 0.5)),
                        "relationship_type": edge_data.get("relationship_type", "unknown"),
                        "attributes": {},
                        "metadata": {}
                    }
                    
                    relationship = TrustRelationship(**rel_dict)
                    self.add_relationship(relationship)
                
                return True
                
            except Exception as e:
                logger.error(f"Error importing GraphML data: {e}")
                return False
        else:
            raise ValueError(f"Unsupported import format: {format}")

# Create singleton instance
trust_relationship_graph = TrustRelationshipGraph()

# API endpoints (if this were a standalone service)
app = FastAPI(
    title="Trust Relationship Graph",
    description="Trust Relationship Graph for the Overseer System",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "trust_relationship_graph", "timestamp": datetime.now().isoformat()}

@app.post("/entities")
async def create_entity(entity: Entity):
    """Create a new entity in the trust graph."""
    entity_id = trust_relationship_graph.add_entity(entity)
    return {"entity_id": entity_id, "status": "created"}

@app.get("/entities")
async def list_entities(entity_type: Optional[str] = None):
    """List entities in the trust graph."""
    entities = trust_relationship_graph.list_entities(entity_type)
    return {"entities": entities, "count": len(entities)}

@app.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    """Get an entity by ID."""
    entity = trust_relationship_graph.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return entity

@app.put("/entities/{entity_id}")
async def update_entity(entity_id: str, entity: Entity):
    """Update an entity."""
    success = trust_relationship_graph.update_entity(entity_id, entity)
    if not success:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return {"entity_id": entity_id, "status": "updated"}

@app.delete("/entities/{entity_id}")
async def delete_entity(entity_id: str):
    """Delete an entity."""
    success = trust_relationship_graph.delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return {"entity_id": entity_id, "status": "deleted"}

@app.post("/relationships")
async def create_relationship(relationship: TrustRelationship):
    """Create a new trust relationship."""
    try:
        relationship_id = trust_relationship_graph.add_relationship(relationship)
        return {"relationship_id": relationship_id, "status": "created"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/relationships")
async def list_relationships(
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    relationship_type: Optional[str] = None,
    min_trust_score: float = 0.0
):
    """List trust relationships."""
    relationships = trust_relationship_graph.list_relationships(
        source_id, target_id, relationship_type, min_trust_score
    )
    return {"relationships": relationships, "count": len(relationships)}

@app.get("/relationships/{relationship_id}")
async def get_relationship(relationship_id: str):
    """Get a trust relationship by ID."""
    relationship = trust_relationship_graph.get_relationship(relationship_id)
    if not relationship:
        raise HTTPException(status_code=404, detail=f"Relationship {relationship_id} not found")
    return relationship

@app.put("/relationships/{relationship_id}")
async def update_relationship(relationship_id: str, relationship: TrustRelationship):
    """Update a trust relationship."""
    try:
        success = trust_relationship_graph.update_relationship(relationship_id, relationship)
        if not success:
            raise HTTPException(status_code=404, detail=f"Relationship {relationship_id} not found")
        return {"relationship_id": relationship_id, "status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/relationships/{relationship_id}")
async def delete_relationship(relationship_id: str):
    """Delete a trust relationship."""
    success = trust_relationship_graph.delete_relationship(relationship_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Relationship {relationship_id} not found")
    return {"relationship_id": relationship_id, "status": "deleted"}

@app.post("/paths")
async def find_trust_paths(query: PathQuery):
    """Find trust paths between two entities."""
    try:
        paths = trust_relationship_graph.find_trust_paths(query)
        return {"paths": paths, "count": len(paths)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/trust/{source_id}/{target_id}")
async def get_trust_score(source_id: str, target_id: str, inferred: bool = False):
    """Get the trust score between two entities."""
    if inferred:
        trust_score = trust_relationship_graph.get_inferred_trust(source_id, target_id)
    else:
        trust_score = trust_relationship_graph.get_trust_score(source_id, target_id)
    
    if trust_score is None:
        if inferred:
            raise HTTPException(status_code=404, detail=f"No trust path found between {source_id} and {target_id}")
        else:
            raise HTTPException(status_code=404, detail=f"No direct trust relationship between {source_id} and {target_id}")
    
    return {"source_id": source_id, "target_id": target_id, "trust_score": trust_score, "inferred": inferred}

@app.get("/stats")
async def get_graph_stats():
    """Get statistics about the trust graph."""
    stats = trust_relationship_graph.get_graph_stats()
    return stats

@app.get("/entities/{entity_id}/metrics")
async def get_entity_trust_metrics(entity_id: str):
    """Get trust metrics for a specific entity."""
    try:
        metrics = trust_relationship_graph.get_entity_trust_metrics(entity_id)
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/anomalies")
async def detect_trust_anomalies():
    """Detect anomalies in the trust graph."""
    anomalies = trust_relationship_graph.detect_trust_anomalies()
    return {"anomalies": anomalies, "count": len(anomalies)}

@app.get("/export")
async def export_graph(format: str = "json"):
    """Export the trust graph."""
    try:
        data = trust_relationship_graph.export_graph(format)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/import")
async def import_graph(data: Dict[str, Any], format: str = "json"):
    """Import a trust graph."""
    try:
        success = trust_relationship_graph.import_graph(data, format)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to import graph")
        return {"status": "imported", "format": format}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Trust Relationship Graph starting up")
    
    # Subscribe to relevant Kafka topics
    kafka_consumer.subscribe(["entity-events", "relationship-events"])
    
    logger.info("Trust Relationship Graph started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Trust Relationship Graph shutting down")
    
    # Close Kafka connections
    kafka_producer.close()
    kafka_consumer.close()
    
    logger.info("Trust Relationship Graph shut down successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
