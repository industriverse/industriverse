"""
Override Logger for the Overseer System's Capsule Evolution Service.

This module provides comprehensive override logging capabilities for the Overseer System,
enabling detailed tracking, analysis, and management of capsule overrides over time.

The Override Logger is a critical component of the Capsule Evolution framework,
providing insights into how capsules are overridden and modified by various actors.

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
logger = logging.getLogger("override_logger")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="override-logger"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="override-logger",
    auto_offset_reset="earliest"
)

# Data models
class OverrideEvent(BaseModel):
    """Model for capsule override events."""
    override_id: str = Field(..., description="Unique override identifier")
    capsule_id: str = Field(..., description="Capsule ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Override timestamp")
    override_type: str = Field(..., description="Override type")
    actor_id: str = Field(..., description="ID of the actor performing the override")
    actor_type: str = Field(..., description="Type of actor (e.g., 'human', 'agent', 'system')")
    target_component: str = Field(..., description="Component being overridden")
    reason: str = Field(..., description="Reason for the override")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Override parameters")
    previous_state: Dict[str, Any] = Field(default_factory=dict, description="Previous component state")
    new_state: Dict[str, Any] = Field(default_factory=dict, description="New component state")
    approval_chain: List[Dict[str, Any]] = Field(default_factory=list, description="Chain of approvals")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class OverridePattern(BaseModel):
    """Model for override patterns."""
    pattern_id: str = Field(..., description="Unique pattern identifier")
    capsule_id: str = Field(..., description="Capsule ID")
    pattern_name: str = Field(..., description="Pattern name")
    pattern_description: str = Field(..., description="Pattern description")
    override_types: List[str] = Field(..., description="Override types in the pattern")
    actor_types: List[str] = Field(..., description="Actor types in the pattern")
    frequency: float = Field(..., description="Pattern frequency")
    confidence: float = Field(..., description="Pattern confidence")
    first_observed: datetime = Field(..., description="When pattern was first observed")
    last_observed: datetime = Field(..., description="When pattern was last observed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class OverrideAnalysisRequest(BaseModel):
    """Model for override analysis requests."""
    capsule_id: str = Field(..., description="Capsule ID to analyze")
    time_period: str = Field("7d", description="Time period to analyze (e.g., '1d', '7d', '30d')")
    include_patterns: bool = Field(True, description="Whether to include pattern detection")

# In-memory storage (would be replaced with database in production)
override_events = {}
override_patterns = {}

class OverrideLogger:
    """
    Override Logger implementation for the Overseer System.
    
    This class provides methods for logging and analyzing capsule overrides, including:
    - Logging override events
    - Detecting override patterns
    - Analyzing override history
    - Generating override reports
    """
    
    def __init__(self):
        """Initialize the Override Logger."""
        self.pattern_detection_schedule = {
            "daily": 24 * 60 * 60,  # Every day
            "weekly": 7 * 24 * 60 * 60  # Every week
        }
        self.last_pattern_detection_time = {
            "daily": datetime.now() - timedelta(days=2),  # Force immediate detection
            "weekly": datetime.now() - timedelta(weeks=2)
        }
        logger.info("Override Logger initialized")
    
    def log_override(self, override: OverrideEvent) -> str:
        """
        Log a capsule override event.
        
        Args:
            override: The override event
            
        Returns:
            str: Override ID
        """
        # Store the override
        override_events[override.override_id] = override.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-override-events",
            key=override.capsule_id,
            value=json.dumps({
                "override_id": override.override_id,
                "capsule_id": override.capsule_id,
                "override_type": override.override_type,
                "actor_id": override.actor_id,
                "actor_type": override.actor_type,
                "timestamp": override.timestamp.isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "capsule_override",
            "override_id": override.override_id,
            "capsule_id": override.capsule_id,
            "override_type": override.override_type,
            "actor_id": override.actor_id,
            "actor_type": override.actor_type
        }
        mcp_bridge.send_context_update("override_logger", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="override_logger",
            message={
                "type": "capsule_override",
                "override_id": override.override_id,
                "capsule_id": override.capsule_id,
                "override_type": override.override_type,
                "actor_id": override.actor_id,
                "actor_type": override.actor_type
            }
        )
        
        # Create evolution event
        from .capsule_evolution_service import capsule_evolution_service, CapsuleEvolutionEvent
        
        evolution_event = CapsuleEvolutionEvent(
            event_id=f"event-{uuid.uuid4()}",
            capsule_id=override.capsule_id,
            event_type="override",
            source="override_logger",
            details={
                "override_id": override.override_id,
                "override_type": override.override_type,
                "actor_id": override.actor_id,
                "actor_type": override.actor_type,
                "target_component": override.target_component
            },
            metadata={
                "reason": override.reason,
                "parameters": override.parameters
            }
        )
        
        capsule_evolution_service.track_evolution_event(evolution_event)
        
        # Check for sovereign override conditions
        if override.actor_type == "human" and override.metadata.get("sovereign", False):
            # Notify sovereign override explainer
            from ..capsule_governance.sovereign_override_explainer import sovereign_override_explainer
            
            sovereign_override_explainer.process_sovereign_override(
                override_id=override.override_id,
                capsule_id=override.capsule_id,
                actor_id=override.actor_id,
                target_component=override.target_component,
                reason=override.reason,
                previous_state=override.previous_state,
                new_state=override.new_state
            )
        
        return override.override_id
    
    def get_override(self, override_id: str) -> Optional[OverrideEvent]:
        """
        Get an override event by ID.
        
        Args:
            override_id: The override ID
            
        Returns:
            Optional[OverrideEvent]: The override event, or None if not found
        """
        if override_id not in override_events:
            return None
        
        return OverrideEvent(**override_events[override_id])
    
    def list_overrides(
        self, 
        capsule_id: Optional[str] = None,
        override_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 10
    ) -> List[OverrideEvent]:
        """
        List override events, optionally filtered.
        
        Args:
            capsule_id: Optional capsule ID to filter by
            override_type: Optional override type to filter by
            actor_id: Optional actor ID to filter by
            actor_type: Optional actor type to filter by
            start_time: Optional start time to filter by
            end_time: Optional end time to filter by
            limit: Maximum number of events to return
            
        Returns:
            List[OverrideEvent]: List of matching override events
        """
        results = []
        
        for override_dict in override_events.values():
            # Apply filters
            if capsule_id and override_dict["capsule_id"] != capsule_id:
                continue
            
            if override_type and override_dict["override_type"] != override_type:
                continue
            
            if actor_id and override_dict["actor_id"] != actor_id:
                continue
            
            if actor_type and override_dict["actor_type"] != actor_type:
                continue
            
            override_time = datetime.fromisoformat(override_dict["timestamp"]) if isinstance(override_dict["timestamp"], str) else override_dict["timestamp"]
            
            if start_time and override_time < start_time:
                continue
            
            if end_time and override_time > end_time:
                continue
            
            results.append(OverrideEvent(**override_dict))
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda o: o.timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def detect_patterns(self, capsule_id: str) -> List[str]:
        """
        Detect override patterns for a capsule.
        
        Args:
            capsule_id: The capsule ID
            
        Returns:
            List[str]: List of detected pattern IDs
        """
        # Get recent overrides for the capsule
        now = datetime.now()
        start_time = now - timedelta(days=30)  # Last 30 days
        
        overrides = self.list_overrides(
            capsule_id=capsule_id,
            start_time=start_time,
            end_time=now,
            limit=1000  # High limit to get all overrides
        )
        
        if len(overrides) < 5:
            # Not enough data for pattern detection
            return []
        
        pattern_ids = []
        
        # Detect actor patterns
        actor_patterns = self._detect_actor_patterns(overrides)
        for pattern in actor_patterns:
            pattern_id = f"pattern-{uuid.uuid4()}"
            pattern_obj = OverridePattern(
                pattern_id=pattern_id,
                capsule_id=capsule_id,
                pattern_name=pattern["name"],
                pattern_description=pattern["description"],
                override_types=pattern["override_types"],
                actor_types=pattern["actor_types"],
                frequency=pattern["frequency"],
                confidence=pattern["confidence"],
                first_observed=pattern["first_observed"],
                last_observed=pattern["last_observed"],
                metadata={
                    "pattern_type": "actor",
                    "actor_id": pattern["actor_id"]
                }
            )
            
            override_patterns[pattern_id] = pattern_obj.dict()
            pattern_ids.append(pattern_id)
            
            # Publish pattern to Kafka
            kafka_producer.produce(
                topic="capsule-override-patterns",
                key=capsule_id,
                value=json.dumps({
                    "pattern_id": pattern_id,
                    "capsule_id": capsule_id,
                    "pattern_name": pattern["name"],
                    "pattern_type": "actor",
                    "confidence": pattern["confidence"],
                    "timestamp": now.isoformat()
                })
            )
        
        # Detect component patterns
        component_patterns = self._detect_component_patterns(overrides)
        for pattern in component_patterns:
            pattern_id = f"pattern-{uuid.uuid4()}"
            pattern_obj = OverridePattern(
                pattern_id=pattern_id,
                capsule_id=capsule_id,
                pattern_name=pattern["name"],
                pattern_description=pattern["description"],
                override_types=pattern["override_types"],
                actor_types=pattern["actor_types"],
                frequency=pattern["frequency"],
                confidence=pattern["confidence"],
                first_observed=pattern["first_observed"],
                last_observed=pattern["last_observed"],
                metadata={
                    "pattern_type": "component",
                    "target_component": pattern["target_component"]
                }
            )
            
            override_patterns[pattern_id] = pattern_obj.dict()
            pattern_ids.append(pattern_id)
            
            # Publish pattern to Kafka
            kafka_producer.produce(
                topic="capsule-override-patterns",
                key=capsule_id,
                value=json.dumps({
                    "pattern_id": pattern_id,
                    "capsule_id": capsule_id,
                    "pattern_name": pattern["name"],
                    "pattern_type": "component",
                    "confidence": pattern["confidence"],
                    "timestamp": now.isoformat()
                })
            )
        
        # Detect temporal patterns
        temporal_patterns = self._detect_temporal_patterns(overrides)
        for pattern in temporal_patterns:
            pattern_id = f"pattern-{uuid.uuid4()}"
            pattern_obj = OverridePattern(
                pattern_id=pattern_id,
                capsule_id=capsule_id,
                pattern_name=pattern["name"],
                pattern_description=pattern["description"],
                override_types=pattern["override_types"],
                actor_types=pattern["actor_types"],
                frequency=pattern["frequency"],
                confidence=pattern["confidence"],
                first_observed=pattern["first_observed"],
                last_observed=pattern["last_observed"],
                metadata={
                    "pattern_type": "temporal",
                    "period_hours": pattern["period_hours"]
                }
            )
            
            override_patterns[pattern_id] = pattern_obj.dict()
            pattern_ids.append(pattern_id)
            
            # Publish pattern to Kafka
            kafka_producer.produce(
                topic="capsule-override-patterns",
                key=capsule_id,
                value=json.dumps({
                    "pattern_id": pattern_id,
                    "capsule_id": capsule_id,
                    "pattern_name": pattern["name"],
                    "pattern_type": "temporal",
                    "confidence": pattern["confidence"],
                    "timestamp": now.isoformat()
                })
            )
        
        return pattern_ids
    
    def _detect_actor_patterns(self, overrides: List[OverrideEvent]) -> List[Dict[str, Any]]:
        """
        Detect actor-based override patterns.
        
        Args:
            overrides: List of override events
            
        Returns:
            List[Dict[str, Any]]: List of detected patterns
        """
        patterns = []
        
        # Group overrides by actor
        overrides_by_actor = {}
        for override in overrides:
            actor_key = f"{override.actor_id}:{override.actor_type}"
            if actor_key not in overrides_by_actor:
                overrides_by_actor[actor_key] = []
            overrides_by_actor[actor_key].append(override)
        
        # For each actor with enough data, look for patterns
        for actor_key, actor_overrides in overrides_by_actor.items():
            if len(actor_overrides) < 3:
                continue  # Not enough data
            
            actor_id, actor_type = actor_key.split(":", 1)
            
            # Count override types for this actor
            type_counts = {}
            for override in actor_overrides:
                if override.override_type not in type_counts:
                    type_counts[override.override_type] = 0
                type_counts[override.override_type] += 1
            
            # Find dominant override types (>25% of overrides)
            dominant_types = []
            for override_type, count in type_counts.items():
                if count / len(actor_overrides) > 0.25:
                    dominant_types.append(override_type)
            
            if dominant_types:
                # Calculate frequency
                frequency = len(actor_overrides) / len(overrides)
                
                # Calculate confidence based on frequency and dominance
                dominance = sum(type_counts[t] for t in dominant_types) / len(actor_overrides)
                confidence = min(0.5 + (frequency * 0.3) + (dominance * 0.2), 1.0)
                
                # Sort actor overrides by timestamp
                sorted_actor_overrides = sorted(actor_overrides, key=lambda o: o.timestamp)
                
                # Create pattern
                pattern = {
                    "name": f"Actor Pattern: {actor_type}:{actor_id} -> {', '.join(dominant_types)}",
                    "description": f"Actor '{actor_type}:{actor_id}' predominantly performs {', '.join(dominant_types)} overrides",
                    "override_types": dominant_types,
                    "actor_types": [actor_type],
                    "frequency": frequency,
                    "confidence": confidence,
                    "first_observed": sorted_actor_overrides[0].timestamp,
                    "last_observed": sorted_actor_overrides[-1].timestamp,
                    "actor_id": actor_id
                }
                
                patterns.append(pattern)
        
        # Sort by confidence (highest first)
        patterns.sort(key=lambda p: p["confidence"], reverse=True)
        
        return patterns
    
    def _detect_component_patterns(self, overrides: List[OverrideEvent]) -> List[Dict[str, Any]]:
        """
        Detect component-based override patterns.
        
        Args:
            overrides: List of override events
            
        Returns:
            List[Dict[str, Any]]: List of detected patterns
        """
        patterns = []
        
        # Group overrides by target component
        overrides_by_component = {}
        for override in overrides:
            if override.target_component not in overrides_by_component:
                overrides_by_component[override.target_component] = []
            overrides_by_component[override.target_component].append(override)
        
        # For each component with enough data, look for patterns
        for component, component_overrides in overrides_by_component.items():
            if len(component_overrides) < 3:
                continue  # Not enough data
            
            # Count actor types for this component
            actor_type_counts = {}
            for override in component_overrides:
                if override.actor_type not in actor_type_counts:
                    actor_type_counts[override.actor_type] = 0
                actor_type_counts[override.actor_type] += 1
            
            # Find dominant actor types (>25% of overrides)
            dominant_actor_types = []
            for actor_type, count in actor_type_counts.items():
                if count / len(component_overrides) > 0.25:
                    dominant_actor_types.append(actor_type)
            
            # Count override types for this component
            override_type_counts = {}
            for override in component_overrides:
                if override.override_type not in override_type_counts:
                    override_type_counts[override.override_type] = 0
                override_type_counts[override.override_type] += 1
            
            # Find dominant override types (>25% of overrides)
            dominant_override_types = []
            for override_type, count in override_type_counts.items():
                if count / len(component_overrides) > 0.25:
                    dominant_override_types.append(override_type)
            
            if dominant_actor_types and dominant_override_types:
                # Calculate frequency
                frequency = len(component_overrides) / len(overrides)
                
                # Calculate confidence based on frequency and dominance
                actor_dominance = sum(actor_type_counts[t] for t in dominant_actor_types) / len(component_overrides)
                override_dominance = sum(override_type_counts[t] for t in dominant_override_types) / len(component_overrides)
                confidence = min(0.5 + (frequency * 0.2) + (actor_dominance * 0.15) + (override_dominance * 0.15), 1.0)
                
                # Sort component overrides by timestamp
                sorted_component_overrides = sorted(component_overrides, key=lambda o: o.timestamp)
                
                # Create pattern
                pattern = {
                    "name": f"Component Pattern: {component} <- {', '.join(dominant_actor_types)}",
                    "description": f"Component '{component}' is predominantly overridden by {', '.join(dominant_actor_types)} actors with {', '.join(dominant_override_types)} operations",
                    "override_types": dominant_override_types,
                    "actor_types": dominant_actor_types,
                    "frequency": frequency,
                    "confidence": confidence,
                    "first_observed": sorted_component_overrides[0].timestamp,
                    "last_observed": sorted_component_overrides[-1].timestamp,
                    "target_component": component
                }
                
                patterns.append(pattern)
        
        # Sort by confidence (highest first)
        patterns.sort(key=lambda p: p["confidence"], reverse=True)
        
        return patterns
    
    def _detect_temporal_patterns(self, overrides: List[OverrideEvent]) -> List[Dict[str, Any]]:
        """
        Detect temporal override patterns.
        
        Args:
            overrides: List of override events
            
        Returns:
            List[Dict[str, Any]]: List of detected patterns
        """
        patterns = []
        
        # Sort overrides by timestamp
        sorted_overrides = sorted(overrides, key=lambda o: o.timestamp)
        
        # Group overrides by type
        overrides_by_type = {}
        for override in sorted_overrides:
            if override.override_type not in overrides_by_type:
                overrides_by_type[override.override_type] = []
            overrides_by_type[override.override_type].append(override)
        
        # For each override type with enough data, look for temporal patterns
        for override_type, type_overrides in overrides_by_type.items():
            if len(type_overrides) < 3:
                continue  # Not enough data
            
            # Calculate time differences between consecutive overrides
            time_diffs = []
            for i in range(1, len(type_overrides)):
                diff = (type_overrides[i].timestamp - type_overrides[i-1].timestamp).total_seconds() / 3600  # Hours
                time_diffs.append(diff)
            
            # Check if time differences are consistent
            if len(time_diffs) < 2:
                continue
            
            mean_diff = sum(time_diffs) / len(time_diffs)
            variance = sum((diff - mean_diff) ** 2 for diff in time_diffs) / len(time_diffs)
            std_dev = variance ** 0.5
            
            # If standard deviation is less than 25% of mean, consider it a pattern
            if std_dev < mean_diff * 0.25 and mean_diff > 1:  # At least 1 hour apart
                # Count actor types for this override type
                actor_type_counts = {}
                for override in type_overrides:
                    if override.actor_type not in actor_type_counts:
                        actor_type_counts[override.actor_type] = 0
                    actor_type_counts[override.actor_type] += 1
                
                # Find dominant actor types (>25% of overrides)
                dominant_actor_types = []
                for actor_type, count in actor_type_counts.items():
                    if count / len(type_overrides) > 0.25:
                        dominant_actor_types.append(actor_type)
                
                # Calculate confidence based on consistency and number of occurrences
                consistency = 1.0 - (std_dev / mean_diff)
                occurrences = len(type_overrides)
                confidence = min(0.5 + (consistency * 0.3) + (occurrences / 20), 1.0)
                
                # Create pattern
                pattern = {
                    "name": f"Temporal Pattern: {override_type} every {mean_diff:.1f} hours",
                    "description": f"{override_type} overrides occur approximately every {mean_diff:.1f} hours (±{std_dev:.1f} hours)",
                    "override_types": [override_type],
                    "actor_types": dominant_actor_types,
                    "frequency": 1.0 / mean_diff,  # Frequency per hour
                    "confidence": confidence,
                    "first_observed": type_overrides[0].timestamp,
                    "last_observed": type_overrides[-1].timestamp,
                    "period_hours": mean_diff
                }
                
                patterns.append(pattern)
        
        # Sort by confidence (highest first)
        patterns.sort(key=lambda p: p["confidence"], reverse=True)
        
        return patterns
    
    def get_pattern(self, pattern_id: str) -> Optional[OverridePattern]:
        """
        Get an override pattern by ID.
        
        Args:
            pattern_id: The pattern ID
            
        Returns:
            Optional[OverridePattern]: The pattern, or None if not found
        """
        if pattern_id not in override_patterns:
            return None
        
        return OverridePattern(**override_patterns[pattern_id])
    
    def list_patterns(
        self, 
        capsule_id: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 10
    ) -> List[OverridePattern]:
        """
        List override patterns, optionally filtered.
        
        Args:
            capsule_id: Optional capsule ID to filter by
            min_confidence: Minimum confidence level
            limit: Maximum number of patterns to return
            
        Returns:
            List[OverridePattern]: List of matching patterns
        """
        results = []
        
        for pattern_dict in override_patterns.values():
            # Apply filters
            if capsule_id and pattern_dict["capsule_id"] != capsule_id:
                continue
            
            if pattern_dict["confidence"] < min_confidence:
                continue
            
            results.append(OverridePattern(**pattern_dict))
        
        # Sort by confidence (highest first)
        results.sort(key=lambda p: p.confidence, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def analyze_overrides(self, request: OverrideAnalysisRequest) -> Dict[str, Any]:
        """
        Analyze overrides for a capsule.
        
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
        
        # Get overrides for the capsule in the time period
        overrides = self.list_overrides(
            capsule_id=request.capsule_id,
            start_time=start_time,
            end_time=now,
            limit=1000  # High limit to get all overrides
        )
        
        if not overrides:
            return {
                "capsule_id": request.capsule_id,
                "status": "insufficient_data",
                "message": "No overrides found in the specified time period",
                "time_period": request.time_period
            }
        
        # Count overrides by type
        override_types = {}
        for override in overrides:
            if override.override_type not in override_types:
                override_types[override.override_type] = 0
            override_types[override.override_type] += 1
        
        # Count overrides by actor type
        actor_types = {}
        for override in overrides:
            if override.actor_type not in actor_types:
                actor_types[override.actor_type] = 0
            actor_types[override.actor_type] += 1
        
        # Count overrides by target component
        target_components = {}
        for override in overrides:
            if override.target_component not in target_components:
                target_components[override.target_component] = 0
            target_components[override.target_component] += 1
        
        # Calculate override frequency over time
        # Group overrides by day
        overrides_by_day = {}
        for override in overrides:
            day = override.timestamp.date().isoformat()
            if day not in overrides_by_day:
                overrides_by_day[day] = 0
            overrides_by_day[day] += 1
        
        # Ensure all days in the range are represented
        current_date = start_time.date()
        while current_date <= now.date():
            day = current_date.isoformat()
            if day not in overrides_by_day:
                overrides_by_day[day] = 0
            current_date += timedelta(days=1)
        
        # Sort days
        days = sorted(overrides_by_day.keys())
        daily_counts = [overrides_by_day[day] for day in days]
        
        # Calculate override rate (overrides per day)
        days_in_period = (now - start_time).days or 1  # Avoid division by zero
        override_rate = len(overrides) / days_in_period
        
        # Get patterns if requested
        patterns = []
        if request.include_patterns:
            # Detect new patterns
            self.detect_patterns(request.capsule_id)
            
            # Get existing patterns
            patterns = self.list_patterns(
                capsule_id=request.capsule_id,
                min_confidence=0.5,  # Only include reasonably confident patterns
                limit=5
            )
        
        # Compile results
        results = {
            "capsule_id": request.capsule_id,
            "status": "success",
            "analysis_timestamp": now.isoformat(),
            "time_period": request.time_period,
            "override_count": len(overrides),
            "override_rate": override_rate,
            "override_types": override_types,
            "actor_types": actor_types,
            "target_components": target_components,
            "daily_activity": {
                "days": days,
                "counts": daily_counts
            },
            "patterns": [p.dict() for p in patterns] if patterns else []
        }
        
        return results
    
    def generate_override_report(self, capsule_id: str, time_period: str = "30d") -> Dict[str, Any]:
        """
        Generate a comprehensive override report for a capsule.
        
        Args:
            capsule_id: The capsule ID
            time_period: Time period to analyze (e.g., '1d', '7d', '30d')
            
        Returns:
            Dict[str, Any]: Override report
        """
        # Analyze overrides
        analysis_request = OverrideAnalysisRequest(
            capsule_id=capsule_id,
            time_period=time_period,
            include_patterns=True
        )
        
        analysis_results = self.analyze_overrides(analysis_request)
        
        if analysis_results["status"] == "insufficient_data":
            return {
                "capsule_id": capsule_id,
                "status": "insufficient_data",
                "message": analysis_results["message"],
                "time_period": time_period,
                "generated_at": datetime.now().isoformat()
            }
        
        # Get recent overrides
        now = datetime.now()
        
        if time_period == "1d":
            start_time = now - timedelta(days=1)
        elif time_period == "7d":
            start_time = now - timedelta(days=7)
        elif time_period == "30d":
            start_time = now - timedelta(days=30)
        else:
            # Default to 30 days
            start_time = now - timedelta(days=30)
            time_period = "30d"
        
        recent_overrides = self.list_overrides(
            capsule_id=capsule_id,
            start_time=start_time,
            end_time=now,
            limit=10  # Just get the 10 most recent
        )
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(analysis_results, recent_overrides)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis_results, risk_metrics)
        
        # Compile report
        report = {
            "capsule_id": capsule_id,
            "status": "success",
            "report_type": "override_report",
            "time_period": time_period,
            "generated_at": now.isoformat(),
            "summary": {
                "override_count": analysis_results["override_count"],
                "override_rate": analysis_results["override_rate"],
                "top_override_types": self._get_top_items(analysis_results["override_types"], 3),
                "top_actor_types": self._get_top_items(analysis_results["actor_types"], 3),
                "top_target_components": self._get_top_items(analysis_results["target_components"], 3)
            },
            "risk_assessment": risk_metrics,
            "recommendations": recommendations,
            "patterns": analysis_results["patterns"],
            "recent_overrides": [o.dict() for o in recent_overrides],
            "detailed_analysis": analysis_results
        }
        
        return report
    
    def _calculate_risk_metrics(self, analysis_results: Dict[str, Any], recent_overrides: List[OverrideEvent]) -> Dict[str, Any]:
        """
        Calculate risk metrics based on override analysis.
        
        Args:
            analysis_results: Override analysis results
            recent_overrides: Recent override events
            
        Returns:
            Dict[str, Any]: Risk metrics
        """
        # Initialize risk metrics
        risk_metrics = {
            "overall_risk_score": 0.0,
            "human_intervention_frequency": 0.0,
            "component_vulnerability": {},
            "override_volatility": 0.0,
            "risk_factors": []
        }
        
        # Calculate human intervention frequency
        human_overrides = 0
        for actor_type, count in analysis_results["actor_types"].items():
            if actor_type == "human":
                human_overrides = count
                break
        
        total_overrides = analysis_results["override_count"]
        if total_overrides > 0:
            risk_metrics["human_intervention_frequency"] = human_overrides / total_overrides
        
        # Calculate component vulnerability
        for component, count in analysis_results["target_components"].items():
            vulnerability = min(count / (total_overrides or 1), 1.0)
            risk_metrics["component_vulnerability"][component] = vulnerability
        
        # Calculate override volatility
        daily_counts = analysis_results["daily_activity"]["counts"]
        if len(daily_counts) > 1:
            mean_daily = sum(daily_counts) / len(daily_counts)
            if mean_daily > 0:
                variance = sum((count - mean_daily) ** 2 for count in daily_counts) / len(daily_counts)
                std_dev = variance ** 0.5
                risk_metrics["override_volatility"] = std_dev / mean_daily
        
        # Identify risk factors
        if risk_metrics["human_intervention_frequency"] > 0.5:
            risk_metrics["risk_factors"].append({
                "factor": "high_human_intervention",
                "description": "High frequency of human overrides may indicate insufficient automation or trust issues",
                "severity": "medium"
            })
        
        for component, vulnerability in risk_metrics["component_vulnerability"].items():
            if vulnerability > 0.3:
                risk_metrics["risk_factors"].append({
                    "factor": "vulnerable_component",
                    "description": f"Component '{component}' is frequently overridden, indicating potential design issues",
                    "severity": "high" if vulnerability > 0.6 else "medium",
                    "component": component
                })
        
        if risk_metrics["override_volatility"] > 0.5:
            risk_metrics["risk_factors"].append({
                "factor": "high_volatility",
                "description": "High override volatility indicates unpredictable behavior or unstable conditions",
                "severity": "high" if risk_metrics["override_volatility"] > 0.8 else "medium"
            })
        
        # Check for sovereign overrides
        sovereign_overrides = [o for o in recent_overrides if o.actor_type == "human" and o.metadata.get("sovereign", False)]
        if sovereign_overrides:
            risk_metrics["risk_factors"].append({
                "factor": "sovereign_overrides",
                "description": f"Detected {len(sovereign_overrides)} sovereign overrides, indicating critical interventions",
                "severity": "high",
                "count": len(sovereign_overrides)
            })
        
        # Calculate overall risk score
        risk_score = (
            risk_metrics["human_intervention_frequency"] * 0.3 +
            max(risk_metrics["component_vulnerability"].values() if risk_metrics["component_vulnerability"] else [0.0]) * 0.3 +
            risk_metrics["override_volatility"] * 0.2 +
            (0.2 if sovereign_overrides else 0.0)
        )
        
        risk_metrics["overall_risk_score"] = min(risk_score, 1.0)
        
        return risk_metrics
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any], risk_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on override analysis and risk metrics.
        
        Args:
            analysis_results: Override analysis results
            risk_metrics: Risk metrics
            
        Returns:
            List[Dict[str, Any]]: Recommendations
        """
        recommendations = []
        
        # Recommendation for high human intervention
        if risk_metrics["human_intervention_frequency"] > 0.5:
            recommendations.append({
                "id": "reduce_human_intervention",
                "title": "Reduce Human Intervention Frequency",
                "description": "The high frequency of human overrides suggests potential trust issues or insufficient automation. Consider reviewing automation policies and improving capsule autonomy.",
                "actions": [
                    "Review automation policies",
                    "Improve capsule autonomy",
                    "Implement better self-healing mechanisms"
                ],
                "priority": "high" if risk_metrics["human_intervention_frequency"] > 0.7 else "medium"
            })
        
        # Recommendations for vulnerable components
        vulnerable_components = [(c, v) for c, v in risk_metrics["component_vulnerability"].items() if v > 0.3]
        for component, vulnerability in vulnerable_components:
            recommendations.append({
                "id": f"strengthen_{component.lower().replace(' ', '_')}",
                "title": f"Strengthen '{component}' Component",
                "description": f"Component '{component}' is frequently overridden, indicating potential design issues or insufficient capabilities. Consider reviewing and enhancing this component.",
                "actions": [
                    f"Review '{component}' design",
                    f"Enhance '{component}' capabilities",
                    f"Implement better validation for '{component}'"
                ],
                "priority": "high" if vulnerability > 0.6 else "medium"
            })
        
        # Recommendation for high volatility
        if risk_metrics["override_volatility"] > 0.5:
            recommendations.append({
                "id": "stabilize_override_patterns",
                "title": "Stabilize Override Patterns",
                "description": "High override volatility indicates unpredictable behavior or unstable conditions. Consider implementing more consistent policies and improving predictability.",
                "actions": [
                    "Implement more consistent override policies",
                    "Improve predictability through better monitoring",
                    "Establish regular maintenance windows for planned overrides"
                ],
                "priority": "high" if risk_metrics["override_volatility"] > 0.8 else "medium"
            })
        
        # Recommendation for sovereign overrides
        sovereign_override_factor = next((f for f in risk_metrics["risk_factors"] if f["factor"] == "sovereign_overrides"), None)
        if sovereign_override_factor:
            recommendations.append({
                "id": "review_sovereign_overrides",
                "title": "Review Sovereign Overrides",
                "description": f"Detected {sovereign_override_factor['count']} sovereign overrides, indicating critical interventions. Review these overrides to understand root causes and prevent future occurrences.",
                "actions": [
                    "Review sovereign override logs",
                    "Identify root causes",
                    "Implement preventive measures",
                    "Consider updating sovereign override policies"
                ],
                "priority": "high"
            })
        
        # General recommendation for pattern-based optimization
        if analysis_results["patterns"]:
            recommendations.append({
                "id": "optimize_based_on_patterns",
                "title": "Optimize Based on Detected Patterns",
                "description": "Several override patterns have been detected. Consider optimizing capsule behavior based on these patterns to reduce the need for overrides.",
                "actions": [
                    "Review detected patterns",
                    "Implement pattern-based optimizations",
                    "Monitor effectiveness of optimizations"
                ],
                "priority": "medium"
            })
        
        return recommendations
    
    def _get_top_items(self, items_dict: Dict[str, int], limit: int) -> List[Dict[str, Any]]:
        """
        Get top items from a dictionary by count.
        
        Args:
            items_dict: Dictionary of items and counts
            limit: Maximum number of items to return
            
        Returns:
            List[Dict[str, Any]]: Top items
        """
        sorted_items = sorted(items_dict.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for item, count in sorted_items[:limit]:
            result.append({
                "name": item,
                "count": count
            })
        
        return result
    
    def run_scheduled_pattern_detection(self):
        """Run scheduled pattern detection."""
        now = datetime.now()
        
        # Check daily pattern detection
        if (now - self.last_pattern_detection_time["daily"]).total_seconds() >= self.pattern_detection_schedule["daily"]:
            logger.info("Running daily override pattern detection")
            self._detect_patterns_for_all_capsules()
            self.last_pattern_detection_time["daily"] = now
    
    def _detect_patterns_for_all_capsules(self):
        """Detect patterns for all capsules."""
        # Get unique capsule IDs from overrides
        capsule_ids = set()
        for override_dict in override_events.values():
            capsule_ids.add(override_dict["capsule_id"])
        
        for capsule_id in capsule_ids:
            try:
                self.detect_patterns(capsule_id)
            except Exception as e:
                logger.error(f"Error detecting patterns for capsule {capsule_id}: {e}")

# Create singleton instance
override_logger = OverrideLogger()

# API endpoints (if this were a standalone service)
app = FastAPI(
    title="Override Logger",
    description="Override Logger for the Overseer System",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "override_logger", "timestamp": datetime.now().isoformat()}

@app.post("/overrides")
async def create_override(override: OverrideEvent):
    """Log a capsule override event."""
    override_id = override_logger.log_override(override)
    return {"override_id": override_id, "status": "created"}

@app.get("/overrides")
async def list_overrides(
    capsule_id: Optional[str] = None,
    override_type: Optional[str] = None,
    actor_id: Optional[str] = None,
    actor_type: Optional[str] = None,
    limit: int = 10
):
    """List override events."""
    overrides = override_logger.list_overrides(
        capsule_id=capsule_id,
        override_type=override_type,
        actor_id=actor_id,
        actor_type=actor_type,
        limit=limit
    )
    return {"overrides": overrides, "count": len(overrides)}

@app.get("/overrides/{override_id}")
async def get_override(override_id: str):
    """Get an override event by ID."""
    override = override_logger.get_override(override_id)
    if not override:
        raise HTTPException(status_code=404, detail=f"Override {override_id} not found")
    return override

@app.post("/patterns/{capsule_id}")
async def detect_patterns(capsule_id: str):
    """Detect override patterns for a capsule."""
    pattern_ids = override_logger.detect_patterns(capsule_id)
    return {"pattern_ids": pattern_ids, "count": len(pattern_ids)}

@app.get("/patterns")
async def list_patterns(
    capsule_id: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 10
):
    """List override patterns."""
    patterns = override_logger.list_patterns(
        capsule_id=capsule_id,
        min_confidence=min_confidence,
        limit=limit
    )
    return {"patterns": patterns, "count": len(patterns)}

@app.get("/patterns/{pattern_id}")
async def get_pattern(pattern_id: str):
    """Get an override pattern by ID."""
    pattern = override_logger.get_pattern(pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not found")
    return pattern

@app.post("/analyze")
async def analyze_overrides(request: OverrideAnalysisRequest):
    """Analyze overrides for a capsule."""
    results = override_logger.analyze_overrides(request)
    return results

@app.get("/reports/{capsule_id}")
async def generate_override_report(
    capsule_id: str,
    time_period: str = "30d"
):
    """Generate a comprehensive override report for a capsule."""
    report = override_logger.generate_override_report(capsule_id, time_period)
    return report

@app.post("/run-scheduled")
async def run_scheduled_pattern_detection():
    """Manually trigger scheduled pattern detection."""
    override_logger.run_scheduled_pattern_detection()
    return {"status": "success", "message": "Scheduled pattern detection triggered"}

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Override Logger starting up")
    
    # Subscribe to relevant Kafka topics
    kafka_consumer.subscribe(["capsule-events", "capsule-override-events"])
    
    logger.info("Override Logger started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Override Logger shutting down")
    
    # Close Kafka connections
    kafka_producer.close()
    kafka_consumer.close()
    
    logger.info("Override Logger shut down successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
