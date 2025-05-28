"""
Capsule Evolution Service for the Overseer System.

This module provides comprehensive capsule evolution capabilities for the Overseer System,
enabling the tracking, management, and optimization of capsule evolution over time.

The Capsule Evolution Service is a critical component of the Overseer System,
providing insights into how capsules evolve and enabling strategic management of their lifecycle.

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
logger = logging.getLogger("capsule_evolution_service")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="capsule-evolution-service"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="capsule-evolution-service",
    auto_offset_reset="earliest"
)

# Data models
class CapsuleEvolutionEvent(BaseModel):
    """Model for capsule evolution events."""
    event_id: str = Field(..., description="Unique event identifier")
    capsule_id: str = Field(..., description="Capsule ID")
    event_type: str = Field(..., description="Event type (e.g., 'mutation', 'override', 'drift')")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    source: str = Field(..., description="Event source")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event details")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleEvolutionMetrics(BaseModel):
    """Model for capsule evolution metrics."""
    capsule_id: str = Field(..., description="Capsule ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Metrics timestamp")
    mutation_rate: float = Field(0.0, description="Mutation rate")
    override_rate: float = Field(0.0, description="Override rate")
    drift_rate: float = Field(0.0, description="Drift rate")
    stability_score: float = Field(0.0, description="Stability score")
    adaptability_score: float = Field(0.0, description="Adaptability score")
    evolution_velocity: float = Field(0.0, description="Evolution velocity")
    genetic_diversity: float = Field(0.0, description="Genetic diversity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleEvolutionRecommendation(BaseModel):
    """Model for capsule evolution recommendations."""
    recommendation_id: str = Field(..., description="Unique recommendation identifier")
    capsule_id: str = Field(..., description="Capsule ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Recommendation timestamp")
    recommendation_type: str = Field(..., description="Recommendation type")
    priority: str = Field(..., description="Priority (low, medium, high)")
    description: str = Field(..., description="Recommendation description")
    rationale: str = Field(..., description="Recommendation rationale")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested actions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleEvolutionAnalysisRequest(BaseModel):
    """Model for capsule evolution analysis requests."""
    capsule_id: str = Field(..., description="Capsule ID to analyze")
    time_period: str = Field("7d", description="Time period to analyze (e.g., '1d', '7d', '30d')")
    include_recommendations: bool = Field(True, description="Whether to include recommendations")

# In-memory storage (would be replaced with database in production)
evolution_events = {}
evolution_metrics = {}
evolution_recommendations = {}

class CapsuleEvolutionService:
    """
    Capsule Evolution Service implementation for the Overseer System.
    
    This class provides methods for tracking and analyzing capsule evolution, including:
    - Tracking evolution events (mutations, overrides, drift)
    - Calculating evolution metrics
    - Generating evolution recommendations
    - Analyzing evolution patterns
    """
    
    def __init__(self):
        """Initialize the Capsule Evolution Service."""
        self.metrics_schedule = {
            "hourly": 60 * 60,  # Every hour
            "daily": 24 * 60 * 60,  # Every day
            "weekly": 7 * 24 * 60 * 60  # Every week
        }
        self.last_metrics_time = {
            "hourly": datetime.now() - timedelta(hours=2),  # Force immediate calculation
            "daily": datetime.now() - timedelta(days=2),
            "weekly": datetime.now() - timedelta(weeks=2)
        }
        logger.info("Capsule Evolution Service initialized")
    
    def track_evolution_event(self, event: CapsuleEvolutionEvent) -> str:
        """
        Track a capsule evolution event.
        
        Args:
            event: The evolution event
            
        Returns:
            str: Event ID
        """
        # Store the event
        evolution_events[event.event_id] = event.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-evolution-events",
            key=event.capsule_id,
            value=json.dumps({
                "event_type": event.event_type,
                "event_id": event.event_id,
                "capsule_id": event.capsule_id,
                "timestamp": event.timestamp.isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "capsule_evolution_event",
            "event_id": event.event_id,
            "capsule_id": event.capsule_id,
            "event_type": event.event_type
        }
        mcp_bridge.send_context_update("capsule_evolution_service", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="capsule_evolution_service",
            message={
                "type": "capsule_evolution_event",
                "event_id": event.event_id,
                "capsule_id": event.capsule_id,
                "event_type": event.event_type
            }
        )
        
        return event.event_id
    
    def get_evolution_event(self, event_id: str) -> Optional[CapsuleEvolutionEvent]:
        """
        Get a capsule evolution event by ID.
        
        Args:
            event_id: The event ID
            
        Returns:
            Optional[CapsuleEvolutionEvent]: The event, or None if not found
        """
        if event_id not in evolution_events:
            return None
        
        return CapsuleEvolutionEvent(**evolution_events[event_id])
    
    def list_evolution_events(
        self, 
        capsule_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 10
    ) -> List[CapsuleEvolutionEvent]:
        """
        List capsule evolution events, optionally filtered.
        
        Args:
            capsule_id: Optional capsule ID to filter by
            event_type: Optional event type to filter by
            start_time: Optional start time to filter by
            end_time: Optional end time to filter by
            limit: Maximum number of events to return
            
        Returns:
            List[CapsuleEvolutionEvent]: List of matching events
        """
        results = []
        
        for event_dict in evolution_events.values():
            # Apply filters
            if capsule_id and event_dict["capsule_id"] != capsule_id:
                continue
            
            if event_type and event_dict["event_type"] != event_type:
                continue
            
            event_time = datetime.fromisoformat(event_dict["timestamp"]) if isinstance(event_dict["timestamp"], str) else event_dict["timestamp"]
            
            if start_time and event_time < start_time:
                continue
            
            if end_time and event_time > end_time:
                continue
            
            results.append(CapsuleEvolutionEvent(**event_dict))
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def calculate_evolution_metrics(self, capsule_id: str) -> CapsuleEvolutionMetrics:
        """
        Calculate evolution metrics for a capsule.
        
        Args:
            capsule_id: The capsule ID
            
        Returns:
            CapsuleEvolutionMetrics: The calculated metrics
        """
        # Get recent events for the capsule
        now = datetime.now()
        start_time = now - timedelta(days=30)  # Last 30 days
        
        events = self.list_evolution_events(
            capsule_id=capsule_id,
            start_time=start_time,
            end_time=now,
            limit=1000  # High limit to get all events
        )
        
        if not events:
            # No events, return default metrics
            metrics = CapsuleEvolutionMetrics(
                capsule_id=capsule_id,
                timestamp=now,
                mutation_rate=0.0,
                override_rate=0.0,
                drift_rate=0.0,
                stability_score=1.0,  # Max stability if no changes
                adaptability_score=0.0,  # Min adaptability if no changes
                evolution_velocity=0.0,
                genetic_diversity=0.0,
                metadata={
                    "event_count": 0,
                    "time_period_days": 30
                }
            )
        else:
            # Count events by type
            mutation_events = [e for e in events if e.event_type == "mutation"]
            override_events = [e for e in events if e.event_type == "override"]
            drift_events = [e for e in events if e.event_type == "drift"]
            
            # Calculate rates (events per day)
            days = 30
            mutation_rate = len(mutation_events) / days
            override_rate = len(override_events) / days
            drift_rate = len(drift_events) / days
            
            # Calculate stability score (inverse of total event rate, normalized)
            total_rate = mutation_rate + override_rate + drift_rate
            stability_score = 1.0 / (1.0 + total_rate)  # Approaches 1 as rate approaches 0
            
            # Calculate adaptability score (based on mutation rate, normalized)
            adaptability_score = 1.0 - (1.0 / (1.0 + mutation_rate))  # Approaches 1 as rate increases
            
            # Calculate evolution velocity (weighted sum of rates)
            evolution_velocity = (0.5 * mutation_rate) + (0.3 * override_rate) + (0.2 * drift_rate)
            
            # Calculate genetic diversity (based on unique mutation types)
            if mutation_events:
                unique_mutations = set()
                for event in mutation_events:
                    if "mutation_type" in event.details:
                        unique_mutations.add(event.details["mutation_type"])
                
                genetic_diversity = len(unique_mutations) / max(10, len(unique_mutations))  # Normalize to 0-1 range
            else:
                genetic_diversity = 0.0
            
            # Create metrics object
            metrics = CapsuleEvolutionMetrics(
                capsule_id=capsule_id,
                timestamp=now,
                mutation_rate=mutation_rate,
                override_rate=override_rate,
                drift_rate=drift_rate,
                stability_score=stability_score,
                adaptability_score=adaptability_score,
                evolution_velocity=evolution_velocity,
                genetic_diversity=genetic_diversity,
                metadata={
                    "event_count": len(events),
                    "mutation_count": len(mutation_events),
                    "override_count": len(override_events),
                    "drift_count": len(drift_events),
                    "time_period_days": days
                }
            )
        
        # Store the metrics
        metrics_id = f"{capsule_id}-{now.isoformat()}"
        evolution_metrics[metrics_id] = metrics.dict()
        
        # Publish metrics to Kafka
        kafka_producer.produce(
            topic="capsule-evolution-metrics",
            key=capsule_id,
            value=json.dumps({
                "capsule_id": capsule_id,
                "timestamp": now.isoformat(),
                "mutation_rate": metrics.mutation_rate,
                "override_rate": metrics.override_rate,
                "drift_rate": metrics.drift_rate,
                "stability_score": metrics.stability_score,
                "adaptability_score": metrics.adaptability_score,
                "evolution_velocity": metrics.evolution_velocity,
                "genetic_diversity": metrics.genetic_diversity
            })
        )
        
        # Generate recommendations based on metrics
        self._generate_recommendations(metrics)
        
        return metrics
    
    def get_latest_metrics(self, capsule_id: str) -> Optional[CapsuleEvolutionMetrics]:
        """
        Get the latest evolution metrics for a capsule.
        
        Args:
            capsule_id: The capsule ID
            
        Returns:
            Optional[CapsuleEvolutionMetrics]: The latest metrics, or None if not found
        """
        # Filter metrics for the capsule
        capsule_metrics = [
            CapsuleEvolutionMetrics(**m) 
            for m in evolution_metrics.values() 
            if m["capsule_id"] == capsule_id
        ]
        
        if not capsule_metrics:
            return None
        
        # Sort by timestamp (newest first)
        capsule_metrics.sort(key=lambda m: m.timestamp, reverse=True)
        
        return capsule_metrics[0]
    
    def _generate_recommendations(self, metrics: CapsuleEvolutionMetrics) -> List[str]:
        """
        Generate recommendations based on evolution metrics.
        
        Args:
            metrics: The evolution metrics
            
        Returns:
            List[str]: List of generated recommendation IDs
        """
        recommendation_ids = []
        
        # Check for high mutation rate
        if metrics.mutation_rate > 0.5:  # More than 0.5 mutations per day
            recommendation_id = f"rec-{uuid.uuid4()}"
            recommendation = CapsuleEvolutionRecommendation(
                recommendation_id=recommendation_id,
                capsule_id=metrics.capsule_id,
                recommendation_type="high_mutation_rate",
                priority="medium",
                description="High mutation rate detected",
                rationale=f"The capsule is experiencing a high mutation rate ({metrics.mutation_rate:.2f} mutations/day), which may indicate instability or rapid adaptation.",
                suggested_actions=[
                    "Review recent mutations to identify patterns",
                    "Consider implementing mutation rate limiting",
                    "Monitor performance impact of frequent mutations"
                ]
            )
            
            evolution_recommendations[recommendation_id] = recommendation.dict()
            recommendation_ids.append(recommendation_id)
        
        # Check for high override rate
        if metrics.override_rate > 0.3:  # More than 0.3 overrides per day
            recommendation_id = f"rec-{uuid.uuid4()}"
            recommendation = CapsuleEvolutionRecommendation(
                recommendation_id=recommendation_id,
                capsule_id=metrics.capsule_id,
                recommendation_type="high_override_rate",
                priority="high",
                description="High override rate detected",
                rationale=f"The capsule is experiencing a high override rate ({metrics.override_rate:.2f} overrides/day), which may indicate misalignment with user expectations.",
                suggested_actions=[
                    "Review override patterns to identify common issues",
                    "Consider retraining or reconfiguring the capsule",
                    "Implement feedback loop to incorporate override learnings"
                ]
            )
            
            evolution_recommendations[recommendation_id] = recommendation.dict()
            recommendation_ids.append(recommendation_id)
        
        # Check for low stability
        if metrics.stability_score < 0.3:  # Low stability score
            recommendation_id = f"rec-{uuid.uuid4()}"
            recommendation = CapsuleEvolutionRecommendation(
                recommendation_id=recommendation_id,
                capsule_id=metrics.capsule_id,
                recommendation_type="low_stability",
                priority="high",
                description="Low stability detected",
                rationale=f"The capsule has a low stability score ({metrics.stability_score:.2f}), indicating frequent changes that may impact reliability.",
                suggested_actions=[
                    "Implement version control for capsule configurations",
                    "Consider freezing non-critical parameters",
                    "Establish stability thresholds and alerts"
                ]
            )
            
            evolution_recommendations[recommendation_id] = recommendation.dict()
            recommendation_ids.append(recommendation_id)
        
        # Check for low adaptability
        if metrics.adaptability_score < 0.2:  # Low adaptability score
            recommendation_id = f"rec-{uuid.uuid4()}"
            recommendation = CapsuleEvolutionRecommendation(
                recommendation_id=recommendation_id,
                capsule_id=metrics.capsule_id,
                recommendation_type="low_adaptability",
                priority="medium",
                description="Low adaptability detected",
                rationale=f"The capsule has a low adaptability score ({metrics.adaptability_score:.2f}), which may limit its ability to respond to changing conditions.",
                suggested_actions=[
                    "Increase mutation rate parameters",
                    "Implement adaptive learning mechanisms",
                    "Expose more parameters to evolutionary processes"
                ]
            )
            
            evolution_recommendations[recommendation_id] = recommendation.dict()
            recommendation_ids.append(recommendation_id)
        
        # Check for low genetic diversity
        if metrics.genetic_diversity < 0.3:  # Low genetic diversity
            recommendation_id = f"rec-{uuid.uuid4()}"
            recommendation = CapsuleEvolutionRecommendation(
                recommendation_id=recommendation_id,
                capsule_id=metrics.capsule_id,
                recommendation_type="low_genetic_diversity",
                priority="low",
                description="Low genetic diversity detected",
                rationale=f"The capsule has low genetic diversity ({metrics.genetic_diversity:.2f}), which may limit its evolutionary potential.",
                suggested_actions=[
                    "Introduce new mutation types",
                    "Implement cross-pollination with related capsules",
                    "Periodically inject random variations"
                ]
            )
            
            evolution_recommendations[recommendation_id] = recommendation.dict()
            recommendation_ids.append(recommendation_id)
        
        return recommendation_ids
    
    def get_recommendation(self, recommendation_id: str) -> Optional[CapsuleEvolutionRecommendation]:
        """
        Get a recommendation by ID.
        
        Args:
            recommendation_id: The recommendation ID
            
        Returns:
            Optional[CapsuleEvolutionRecommendation]: The recommendation, or None if not found
        """
        if recommendation_id not in evolution_recommendations:
            return None
        
        return CapsuleEvolutionRecommendation(**evolution_recommendations[recommendation_id])
    
    def list_recommendations(
        self, 
        capsule_id: Optional[str] = None,
        recommendation_type: Optional[str] = None,
        min_priority: str = "low",
        limit: int = 10
    ) -> List[CapsuleEvolutionRecommendation]:
        """
        List recommendations, optionally filtered.
        
        Args:
            capsule_id: Optional capsule ID to filter by
            recommendation_type: Optional recommendation type to filter by
            min_priority: Minimum priority level to include
            limit: Maximum number of recommendations to return
            
        Returns:
            List[CapsuleEvolutionRecommendation]: List of matching recommendations
        """
        results = []
        
        # Map priority levels to numeric values for comparison
        priority_levels = {
            "low": 0,
            "medium": 1,
            "high": 2
        }
        min_priority_level = priority_levels.get(min_priority.lower(), 0)
        
        for rec_dict in evolution_recommendations.values():
            # Apply filters
            if capsule_id and rec_dict["capsule_id"] != capsule_id:
                continue
            
            if recommendation_type and rec_dict["recommendation_type"] != recommendation_type:
                continue
            
            rec_priority_level = priority_levels.get(rec_dict["priority"].lower(), 0)
            if rec_priority_level < min_priority_level:
                continue
            
            results.append(CapsuleEvolutionRecommendation(**rec_dict))
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda r: r.timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def analyze_evolution(self, request: CapsuleEvolutionAnalysisRequest) -> Dict[str, Any]:
        """
        Analyze capsule evolution over time.
        
        Args:
            request: The analysis request
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Determine time range based on period
        now = datetime.now()
        
        if request.time_period == "1d":
            start_time = now - timedelta(days=1)
        elif request.time_period == "7d":
            start_time = now - timedelta(days=7)
        elif request.time_period == "30d":
            start_time = now - timedelta(days=30)
        else:
            # Default to 7 days
            start_time = now - timedelta(days=7)
            request.time_period = "7d"
        
        # Get events for the capsule in the time period
        events = self.list_evolution_events(
            capsule_id=request.capsule_id,
            start_time=start_time,
            end_time=now,
            limit=1000  # High limit to get all events
        )
        
        if not events:
            return {
                "capsule_id": request.capsule_id,
                "status": "insufficient_data",
                "message": "No evolution events found in the specified time period",
                "time_period": request.time_period
            }
        
        # Count events by type
        event_types = {}
        for event in events:
            if event.event_type not in event_types:
                event_types[event.event_type] = 0
            event_types[event.event_type] += 1
        
        # Count events by source
        event_sources = {}
        for event in events:
            if event.source not in event_sources:
                event_sources[event.source] = 0
            event_sources[event.source] += 1
        
        # Calculate event frequency over time
        # Group events by day
        events_by_day = {}
        for event in events:
            day = event.timestamp.date().isoformat()
            if day not in events_by_day:
                events_by_day[day] = 0
            events_by_day[day] += 1
        
        # Ensure all days in the range are represented
        current_date = start_time.date()
        while current_date <= now.date():
            day = current_date.isoformat()
            if day not in events_by_day:
                events_by_day[day] = 0
            current_date += timedelta(days=1)
        
        # Sort days
        days = sorted(events_by_day.keys())
        daily_counts = [events_by_day[day] for day in days]
        
        # Calculate metrics
        latest_metrics = self.get_latest_metrics(request.capsule_id)
        if not latest_metrics:
            # Calculate metrics if not available
            latest_metrics = self.calculate_evolution_metrics(request.capsule_id)
        
        # Get recommendations if requested
        recommendations = []
        if request.include_recommendations:
            recommendations = self.list_recommendations(
                capsule_id=request.capsule_id,
                min_priority="low",
                limit=5
            )
        
        # Compile results
        results = {
            "capsule_id": request.capsule_id,
            "status": "success",
            "analysis_timestamp": now.isoformat(),
            "time_period": request.time_period,
            "event_count": len(events),
            "event_types": event_types,
            "event_sources": event_sources,
            "daily_activity": {
                "days": days,
                "counts": daily_counts
            },
            "metrics": latest_metrics.dict() if latest_metrics else None,
            "recommendations": [r.dict() for r in recommendations] if recommendations else []
        }
        
        return results
    
    def run_scheduled_metrics(self):
        """Run scheduled metrics calculations."""
        now = datetime.now()
        
        # Check hourly metrics
        if (now - self.last_metrics_time["hourly"]).total_seconds() >= self.metrics_schedule["hourly"]:
            logger.info("Running hourly evolution metrics")
            self._calculate_metrics_for_all_capsules()
            self.last_metrics_time["hourly"] = now
    
    def _calculate_metrics_for_all_capsules(self):
        """Calculate evolution metrics for all capsules."""
        # Get unique capsule IDs from events
        capsule_ids = set()
        for event_dict in evolution_events.values():
            capsule_ids.add(event_dict["capsule_id"])
        
        for capsule_id in capsule_ids:
            try:
                self.calculate_evolution_metrics(capsule_id)
            except Exception as e:
                logger.error(f"Error calculating metrics for capsule {capsule_id}: {e}")

# Create singleton instance
capsule_evolution_service = CapsuleEvolutionService()

# API endpoints (if this were a standalone service)
app = FastAPI(
    title="Capsule Evolution Service",
    description="Capsule Evolution Service for the Overseer System",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "capsule_evolution_service", "timestamp": datetime.now().isoformat()}

@app.post("/events")
async def create_event(event: CapsuleEvolutionEvent):
    """Create a capsule evolution event."""
    event_id = capsule_evolution_service.track_evolution_event(event)
    return {"event_id": event_id, "status": "created"}

@app.get("/events")
async def list_events(
    capsule_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 10
):
    """List capsule evolution events."""
    events = capsule_evolution_service.list_evolution_events(
        capsule_id=capsule_id,
        event_type=event_type,
        limit=limit
    )
    return {"events": events, "count": len(events)}

@app.get("/events/{event_id}")
async def get_event(event_id: str):
    """Get a capsule evolution event by ID."""
    event = capsule_evolution_service.get_evolution_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return event

@app.post("/metrics/{capsule_id}")
async def calculate_metrics(capsule_id: str):
    """Calculate evolution metrics for a capsule."""
    metrics = capsule_evolution_service.calculate_evolution_metrics(capsule_id)
    return metrics

@app.get("/metrics/{capsule_id}")
async def get_metrics(capsule_id: str):
    """Get the latest evolution metrics for a capsule."""
    metrics = capsule_evolution_service.get_latest_metrics(capsule_id)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"No metrics found for capsule {capsule_id}")
    return metrics

@app.get("/recommendations")
async def list_recommendations(
    capsule_id: Optional[str] = None,
    recommendation_type: Optional[str] = None,
    min_priority: str = "low",
    limit: int = 10
):
    """List evolution recommendations."""
    recommendations = capsule_evolution_service.list_recommendations(
        capsule_id=capsule_id,
        recommendation_type=recommendation_type,
        min_priority=min_priority,
        limit=limit
    )
    return {"recommendations": recommendations, "count": len(recommendations)}

@app.get("/recommendations/{recommendation_id}")
async def get_recommendation(recommendation_id: str):
    """Get a recommendation by ID."""
    recommendation = capsule_evolution_service.get_recommendation(recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail=f"Recommendation {recommendation_id} not found")
    return recommendation

@app.post("/analyze")
async def analyze_evolution(request: CapsuleEvolutionAnalysisRequest):
    """Analyze capsule evolution."""
    results = capsule_evolution_service.analyze_evolution(request)
    return results

@app.post("/run-scheduled")
async def run_scheduled_metrics():
    """Manually trigger scheduled metrics calculations."""
    capsule_evolution_service.run_scheduled_metrics()
    return {"status": "success", "message": "Scheduled metrics calculations triggered"}

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Capsule Evolution Service starting up")
    
    # Subscribe to relevant Kafka topics
    kafka_consumer.subscribe(["capsule-events", "capsule-evolution-events"])
    
    logger.info("Capsule Evolution Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Capsule Evolution Service shutting down")
    
    # Close Kafka connections
    kafka_producer.close()
    kafka_consumer.close()
    
    logger.info("Capsule Evolution Service shut down successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
