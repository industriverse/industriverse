"""
Reputation System for the Overseer System.

This module provides a comprehensive reputation management system for entities
within the Overseer System ecosystem. It tracks, calculates, and manages reputation
scores based on behavior, performance, and trust relationships.

The Reputation System is a critical component of the Trust Management framework,
providing quantifiable metrics for trust decisions and governance.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
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
logger = logging.getLogger("reputation_system")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="reputation-system"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="reputation-system",
    auto_offset_reset="earliest"
)

# Data models
class ReputationEvent(BaseModel):
    """Model for reputation-affecting events."""
    entity_id: str = Field(..., description="Entity ID the event applies to")
    event_type: str = Field(..., description="Type of reputation event")
    event_value: float = Field(..., description="Impact value of the event")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    context: Dict[str, Any] = Field(default_factory=dict, description="Event context")
    source_id: Optional[str] = Field(None, description="Source of the event, if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ReputationScore(BaseModel):
    """Model for entity reputation scores."""
    entity_id: str = Field(..., description="Entity ID")
    overall_score: float = Field(..., description="Overall reputation score (0.0 to 1.0)", ge=0.0, le=1.0)
    dimension_scores: Dict[str, float] = Field(default_factory=dict, description="Scores across different dimensions")
    confidence: float = Field(..., description="Confidence in the score (0.0 to 1.0)", ge=0.0, le=1.0)
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    trend: str = Field("stable", description="Score trend (increasing, decreasing, stable)")
    event_count: int = Field(0, description="Number of events factored into the score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ReputationQuery(BaseModel):
    """Model for querying reputation information."""
    entity_ids: List[str] = Field(..., description="Entity IDs to query")
    dimensions: Optional[List[str]] = Field(None, description="Specific dimensions to query")
    include_history: bool = Field(False, description="Whether to include historical data")
    history_days: Optional[int] = Field(None, description="Days of history to include")
    include_events: bool = Field(False, description="Whether to include recent events")
    event_limit: Optional[int] = Field(None, description="Maximum number of events to include")

class ReputationDimension(BaseModel):
    """Model for reputation dimensions."""
    dimension_id: str = Field(..., description="Unique dimension identifier")
    name: str = Field(..., description="Human-readable dimension name")
    description: str = Field(..., description="Dimension description")
    weight: float = Field(1.0, description="Weight in overall score calculation")
    decay_rate: float = Field(0.0, description="Score decay rate per day")
    event_types: List[str] = Field(..., description="Event types that affect this dimension")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# In-memory storage (would be replaced with database in production)
reputation_scores = {}
reputation_events = []
reputation_dimensions = {}

class ReputationSystem:
    """
    Reputation System implementation for the Overseer System.
    
    This class provides methods for managing entity reputation, including:
    - Recording reputation events
    - Calculating reputation scores
    - Managing reputation dimensions
    - Querying reputation information
    """
    
    def __init__(self):
        """Initialize the Reputation System."""
        self._initialize_default_dimensions()
        logger.info("Reputation System initialized")
    
    def _initialize_default_dimensions(self):
        """Initialize default reputation dimensions."""
        default_dimensions = [
            ReputationDimension(
                dimension_id="reliability",
                name="Reliability",
                description="Measure of entity's reliability in performing tasks and meeting expectations",
                weight=1.0,
                decay_rate=0.01,
                event_types=["task_completion", "sla_violation", "uptime", "downtime"]
            ),
            ReputationDimension(
                dimension_id="security",
                name="Security",
                description="Measure of entity's security posture and practices",
                weight=1.2,
                decay_rate=0.005,
                event_types=["security_scan", "vulnerability_detected", "patch_applied", "security_incident"]
            ),
            ReputationDimension(
                dimension_id="performance",
                name="Performance",
                description="Measure of entity's performance metrics",
                weight=0.9,
                decay_rate=0.02,
                event_types=["response_time", "throughput", "resource_usage", "optimization"]
            ),
            ReputationDimension(
                dimension_id="compliance",
                name="Compliance",
                description="Measure of entity's compliance with policies and regulations",
                weight=1.1,
                decay_rate=0.008,
                event_types=["policy_violation", "compliance_check", "audit_result"]
            ),
            ReputationDimension(
                dimension_id="collaboration",
                name="Collaboration",
                description="Measure of entity's effectiveness in collaboration with other entities",
                weight=0.8,
                decay_rate=0.015,
                event_types=["collaboration_success", "communication_quality", "knowledge_sharing"]
            )
        ]
        
        for dimension in default_dimensions:
            reputation_dimensions[dimension.dimension_id] = dimension.dict()
    
    def record_event(self, event: ReputationEvent) -> str:
        """
        Record a reputation-affecting event.
        
        Args:
            event: The reputation event to record
            
        Returns:
            str: Event ID
        """
        event_dict = event.dict()
        event_id = f"{event.entity_id}:{int(time.time())}:{len(reputation_events)}"
        event_dict["event_id"] = event_id
        
        # Store the event
        reputation_events.append(event_dict)
        
        # Update reputation scores
        self._update_reputation_score(event)
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="reputation-events",
            key=event.entity_id,
            value=json.dumps({
                "event_type": "reputation_event",
                "entity_id": event.entity_id,
                "event_id": event_id,
                "timestamp": event.timestamp.isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "reputation_event_recorded",
            "entity_id": event.entity_id,
            "event_type": event.event_type,
            "event_value": event.event_value
        }
        mcp_bridge.send_context_update("reputation_system", mcp_context)
        
        return event_id
    
    def _update_reputation_score(self, event: ReputationEvent):
        """
        Update reputation scores based on an event.
        
        Args:
            event: The reputation event
        """
        entity_id = event.entity_id
        
        # Initialize score if not exists
        if entity_id not in reputation_scores:
            reputation_scores[entity_id] = ReputationScore(
                entity_id=entity_id,
                overall_score=0.5,  # Start with neutral score
                dimension_scores={},
                confidence=0.1,  # Low initial confidence
                event_count=0
            ).dict()
        
        # Get current score
        score_dict = reputation_scores[entity_id]
        
        # Determine which dimensions are affected
        affected_dimensions = []
        for dim_id, dim_data in reputation_dimensions.items():
            if event.event_type in dim_data["event_types"]:
                affected_dimensions.append(dim_id)
        
        # If no dimensions are affected, use a default impact
        if not affected_dimensions:
            affected_dimensions = ["reliability"]  # Default dimension
        
        # Update dimension scores
        for dim_id in affected_dimensions:
            if dim_id not in score_dict["dimension_scores"]:
                score_dict["dimension_scores"][dim_id] = 0.5  # Initialize with neutral score
            
            # Calculate impact based on event value and confidence
            impact = event.event_value * (1.0 / len(affected_dimensions))
            
            # Apply impact with dampening based on event count
            dampening = min(1.0, 5.0 / (score_dict["event_count"] + 5))  # Reduces impact as event count increases
            score_dict["dimension_scores"][dim_id] += impact * dampening
            
            # Ensure score stays in valid range
            score_dict["dimension_scores"][dim_id] = max(0.0, min(1.0, score_dict["dimension_scores"][dim_id]))
        
        # Recalculate overall score
        total_weight = 0.0
        weighted_sum = 0.0
        
        for dim_id, dim_score in score_dict["dimension_scores"].items():
            if dim_id in reputation_dimensions:
                weight = reputation_dimensions[dim_id]["weight"]
                total_weight += weight
                weighted_sum += dim_score * weight
        
        if total_weight > 0:
            score_dict["overall_score"] = weighted_sum / total_weight
        
        # Update confidence based on event count
        score_dict["event_count"] += 1
        score_dict["confidence"] = min(0.95, 0.1 + 0.85 * (1 - (1 / (score_dict["event_count"] + 1))))
        
        # Update timestamp
        score_dict["last_updated"] = datetime.now().isoformat()
        
        # Determine trend
        # (In a real implementation, this would compare to historical values)
        score_dict["trend"] = "stable"
        
        # Store updated score
        reputation_scores[entity_id] = score_dict
    
    def get_reputation_score(self, entity_id: str) -> Optional[ReputationScore]:
        """
        Get the reputation score for an entity.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            Optional[ReputationScore]: The reputation score, or None if not found
        """
        if entity_id not in reputation_scores:
            return None
        
        return ReputationScore(**reputation_scores[entity_id])
    
    def query_reputation(self, query: ReputationQuery) -> Dict[str, Any]:
        """
        Query reputation information for multiple entities.
        
        Args:
            query: The reputation query
            
        Returns:
            Dict[str, Any]: Query results
        """
        results = {
            "entities": {},
            "query_timestamp": datetime.now().isoformat()
        }
        
        for entity_id in query.entity_ids:
            if entity_id in reputation_scores:
                entity_result = {
                    "overall_score": reputation_scores[entity_id]["overall_score"],
                    "confidence": reputation_scores[entity_id]["confidence"],
                    "last_updated": reputation_scores[entity_id]["last_updated"],
                    "trend": reputation_scores[entity_id]["trend"]
                }
                
                # Include dimension scores if requested
                if query.dimensions:
                    entity_result["dimension_scores"] = {
                        dim: reputation_scores[entity_id]["dimension_scores"].get(dim, 0.0)
                        for dim in query.dimensions
                        if dim in reputation_dimensions
                    }
                else:
                    entity_result["dimension_scores"] = reputation_scores[entity_id]["dimension_scores"]
                
                # Include history if requested
                if query.include_history:
                    # In a real implementation, this would query historical data from a database
                    entity_result["history"] = []
                
                # Include events if requested
                if query.include_events:
                    limit = query.event_limit or 10
                    entity_events = [
                        event for event in reputation_events
                        if event["entity_id"] == entity_id
                    ]
                    entity_events.sort(key=lambda e: e["timestamp"], reverse=True)
                    entity_result["recent_events"] = entity_events[:limit]
                
                results["entities"][entity_id] = entity_result
            else:
                results["entities"][entity_id] = {"error": "Entity not found"}
        
        return results
    
    def add_dimension(self, dimension: ReputationDimension) -> str:
        """
        Add a new reputation dimension.
        
        Args:
            dimension: The dimension to add
            
        Returns:
            str: Dimension ID
        """
        dimension_dict = dimension.dict()
        reputation_dimensions[dimension.dimension_id] = dimension_dict
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="reputation-events",
            key=dimension.dimension_id,
            value=json.dumps({
                "event_type": "dimension_added",
                "dimension_id": dimension.dimension_id,
                "name": dimension.name,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        return dimension.dimension_id
    
    def get_dimension(self, dimension_id: str) -> Optional[ReputationDimension]:
        """
        Get a reputation dimension by ID.
        
        Args:
            dimension_id: The dimension ID
            
        Returns:
            Optional[ReputationDimension]: The dimension, or None if not found
        """
        if dimension_id not in reputation_dimensions:
            return None
        
        return ReputationDimension(**reputation_dimensions[dimension_id])
    
    def list_dimensions(self) -> List[ReputationDimension]:
        """
        List all reputation dimensions.
        
        Returns:
            List[ReputationDimension]: List of all dimensions
        """
        return [ReputationDimension(**dim_data) for dim_data in reputation_dimensions.values()]
    
    def apply_decay(self):
        """Apply time-based decay to reputation scores."""
        current_time = datetime.now()
        
        for entity_id, score_dict in reputation_scores.items():
            last_updated = datetime.fromisoformat(score_dict["last_updated"])
            days_since_update = (current_time - last_updated).days
            
            if days_since_update > 0:
                # Apply decay to each dimension
                for dim_id, dim_score in score_dict["dimension_scores"].items():
                    if dim_id in reputation_dimensions:
                        decay_rate = reputation_dimensions[dim_id]["decay_rate"]
                        decay_factor = (1.0 - decay_rate) ** days_since_update
                        
                        # Apply decay and move toward neutral (0.5)
                        new_score = 0.5 + (dim_score - 0.5) * decay_factor
                        score_dict["dimension_scores"][dim_id] = new_score
                
                # Recalculate overall score
                total_weight = 0.0
                weighted_sum = 0.0
                
                for dim_id, dim_score in score_dict["dimension_scores"].items():
                    if dim_id in reputation_dimensions:
                        weight = reputation_dimensions[dim_id]["weight"]
                        total_weight += weight
                        weighted_sum += dim_score * weight
                
                if total_weight > 0:
                    score_dict["overall_score"] = weighted_sum / total_weight
                
                # Update timestamp
                score_dict["last_updated"] = current_time.isoformat()
                
                # Store updated score
                reputation_scores[entity_id] = score_dict

# Create singleton instance
reputation_system = ReputationSystem()

# API endpoints (if this were a standalone service)
app = FastAPI(
    title="Reputation System",
    description="Reputation System for the Overseer System",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "reputation_system", "timestamp": datetime.now().isoformat()}

@app.post("/reputation/events")
async def create_reputation_event(event: ReputationEvent):
    """Create a new reputation event."""
    event_id = reputation_system.record_event(event)
    return {"event_id": event_id, "status": "recorded"}

@app.get("/reputation/scores/{entity_id}")
async def get_entity_reputation(entity_id: str):
    """Get reputation score for an entity."""
    score = reputation_system.get_reputation_score(entity_id)
    if not score:
        raise HTTPException(status_code=404, detail=f"Reputation score for entity {entity_id} not found")
    return score

@app.post("/reputation/query")
async def query_reputation(query: ReputationQuery):
    """Query reputation information."""
    results = reputation_system.query_reputation(query)
    return results

@app.post("/reputation/dimensions")
async def create_dimension(dimension: ReputationDimension):
    """Create a new reputation dimension."""
    dimension_id = reputation_system.add_dimension(dimension)
    return {"dimension_id": dimension_id, "status": "created"}

@app.get("/reputation/dimensions")
async def list_dimensions():
    """List all reputation dimensions."""
    dimensions = reputation_system.list_dimensions()
    return {"dimensions": dimensions, "count": len(dimensions)}

@app.get("/reputation/dimensions/{dimension_id}")
async def get_dimension(dimension_id: str):
    """Get a reputation dimension by ID."""
    dimension = reputation_system.get_dimension(dimension_id)
    if not dimension:
        raise HTTPException(status_code=404, detail=f"Dimension {dimension_id} not found")
    return dimension

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Reputation System starting up")
    
    # Subscribe to relevant Kafka topics
    kafka_consumer.subscribe(["entity-events", "task-events", "system-events"])
    
    logger.info("Reputation System started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Reputation System shutting down")
    
    # Close Kafka connections
    kafka_producer.close()
    kafka_consumer.close()
    
    logger.info("Reputation System shut down successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
