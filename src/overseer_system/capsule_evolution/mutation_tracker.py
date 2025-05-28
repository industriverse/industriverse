"""
Mutation Tracker for the Overseer System's Capsule Evolution Service.

This module provides comprehensive mutation tracking capabilities for the Overseer System,
enabling detailed tracking, analysis, and management of capsule mutations over time.

The Mutation Tracker is a critical component of the Capsule Evolution framework,
providing insights into how capsules mutate and evolve over their lifecycle.

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
logger = logging.getLogger("mutation_tracker")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="mutation-tracker"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="mutation-tracker",
    auto_offset_reset="earliest"
)

# Data models
class MutationEvent(BaseModel):
    """Model for capsule mutation events."""
    mutation_id: str = Field(..., description="Unique mutation identifier")
    capsule_id: str = Field(..., description="Capsule ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Mutation timestamp")
    mutation_type: str = Field(..., description="Mutation type")
    source: str = Field(..., description="Mutation source (e.g., 'user', 'system', 'self')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Mutation parameters")
    previous_state: Dict[str, Any] = Field(default_factory=dict, description="Previous capsule state")
    new_state: Dict[str, Any] = Field(default_factory=dict, description="New capsule state")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class MutationPattern(BaseModel):
    """Model for mutation patterns."""
    pattern_id: str = Field(..., description="Unique pattern identifier")
    capsule_id: str = Field(..., description="Capsule ID")
    pattern_name: str = Field(..., description="Pattern name")
    pattern_description: str = Field(..., description="Pattern description")
    mutation_types: List[str] = Field(..., description="Mutation types in the pattern")
    frequency: float = Field(..., description="Pattern frequency")
    confidence: float = Field(..., description="Pattern confidence")
    first_observed: datetime = Field(..., description="When pattern was first observed")
    last_observed: datetime = Field(..., description="When pattern was last observed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class MutationAnalysisRequest(BaseModel):
    """Model for mutation analysis requests."""
    capsule_id: str = Field(..., description="Capsule ID to analyze")
    time_period: str = Field("7d", description="Time period to analyze (e.g., '1d', '7d', '30d')")
    include_patterns: bool = Field(True, description="Whether to include pattern detection")

# In-memory storage (would be replaced with database in production)
mutation_events = {}
mutation_patterns = {}

class MutationTracker:
    """
    Mutation Tracker implementation for the Overseer System.
    
    This class provides methods for tracking and analyzing capsule mutations, including:
    - Tracking mutation events
    - Detecting mutation patterns
    - Analyzing mutation history
    """
    
    def __init__(self):
        """Initialize the Mutation Tracker."""
        self.pattern_detection_schedule = {
            "daily": 24 * 60 * 60,  # Every day
            "weekly": 7 * 24 * 60 * 60  # Every week
        }
        self.last_pattern_detection_time = {
            "daily": datetime.now() - timedelta(days=2),  # Force immediate detection
            "weekly": datetime.now() - timedelta(weeks=2)
        }
        logger.info("Mutation Tracker initialized")
    
    def track_mutation(self, mutation: MutationEvent) -> str:
        """
        Track a capsule mutation event.
        
        Args:
            mutation: The mutation event
            
        Returns:
            str: Mutation ID
        """
        # Store the mutation
        mutation_events[mutation.mutation_id] = mutation.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="capsule-mutation-events",
            key=mutation.capsule_id,
            value=json.dumps({
                "mutation_id": mutation.mutation_id,
                "capsule_id": mutation.capsule_id,
                "mutation_type": mutation.mutation_type,
                "timestamp": mutation.timestamp.isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "capsule_mutation",
            "mutation_id": mutation.mutation_id,
            "capsule_id": mutation.capsule_id,
            "mutation_type": mutation.mutation_type
        }
        mcp_bridge.send_context_update("mutation_tracker", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="mutation_tracker",
            message={
                "type": "capsule_mutation",
                "mutation_id": mutation.mutation_id,
                "capsule_id": mutation.capsule_id,
                "mutation_type": mutation.mutation_type
            }
        )
        
        # Create evolution event
        from .capsule_evolution_service import capsule_evolution_service, CapsuleEvolutionEvent
        
        evolution_event = CapsuleEvolutionEvent(
            event_id=f"event-{uuid.uuid4()}",
            capsule_id=mutation.capsule_id,
            event_type="mutation",
            source="mutation_tracker",
            details={
                "mutation_id": mutation.mutation_id,
                "mutation_type": mutation.mutation_type,
                "source": mutation.source
            },
            metadata={
                "parameters": mutation.parameters
            }
        )
        
        capsule_evolution_service.track_evolution_event(evolution_event)
        
        return mutation.mutation_id
    
    def get_mutation(self, mutation_id: str) -> Optional[MutationEvent]:
        """
        Get a mutation event by ID.
        
        Args:
            mutation_id: The mutation ID
            
        Returns:
            Optional[MutationEvent]: The mutation event, or None if not found
        """
        if mutation_id not in mutation_events:
            return None
        
        return MutationEvent(**mutation_events[mutation_id])
    
    def list_mutations(
        self, 
        capsule_id: Optional[str] = None,
        mutation_type: Optional[str] = None,
        source: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 10
    ) -> List[MutationEvent]:
        """
        List mutation events, optionally filtered.
        
        Args:
            capsule_id: Optional capsule ID to filter by
            mutation_type: Optional mutation type to filter by
            source: Optional source to filter by
            start_time: Optional start time to filter by
            end_time: Optional end time to filter by
            limit: Maximum number of events to return
            
        Returns:
            List[MutationEvent]: List of matching mutation events
        """
        results = []
        
        for mutation_dict in mutation_events.values():
            # Apply filters
            if capsule_id and mutation_dict["capsule_id"] != capsule_id:
                continue
            
            if mutation_type and mutation_dict["mutation_type"] != mutation_type:
                continue
            
            if source and mutation_dict["source"] != source:
                continue
            
            mutation_time = datetime.fromisoformat(mutation_dict["timestamp"]) if isinstance(mutation_dict["timestamp"], str) else mutation_dict["timestamp"]
            
            if start_time and mutation_time < start_time:
                continue
            
            if end_time and mutation_time > end_time:
                continue
            
            results.append(MutationEvent(**mutation_dict))
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda m: m.timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def detect_patterns(self, capsule_id: str) -> List[str]:
        """
        Detect mutation patterns for a capsule.
        
        Args:
            capsule_id: The capsule ID
            
        Returns:
            List[str]: List of detected pattern IDs
        """
        # Get recent mutations for the capsule
        now = datetime.now()
        start_time = now - timedelta(days=30)  # Last 30 days
        
        mutations = self.list_mutations(
            capsule_id=capsule_id,
            start_time=start_time,
            end_time=now,
            limit=1000  # High limit to get all mutations
        )
        
        if len(mutations) < 5:
            # Not enough data for pattern detection
            return []
        
        pattern_ids = []
        
        # Detect sequential patterns
        sequential_patterns = self._detect_sequential_patterns(mutations)
        for pattern in sequential_patterns:
            pattern_id = f"pattern-{uuid.uuid4()}"
            pattern_obj = MutationPattern(
                pattern_id=pattern_id,
                capsule_id=capsule_id,
                pattern_name=pattern["name"],
                pattern_description=pattern["description"],
                mutation_types=pattern["mutation_types"],
                frequency=pattern["frequency"],
                confidence=pattern["confidence"],
                first_observed=pattern["first_observed"],
                last_observed=pattern["last_observed"],
                metadata={
                    "pattern_type": "sequential",
                    "occurrences": pattern["occurrences"]
                }
            )
            
            mutation_patterns[pattern_id] = pattern_obj.dict()
            pattern_ids.append(pattern_id)
            
            # Publish pattern to Kafka
            kafka_producer.produce(
                topic="capsule-mutation-patterns",
                key=capsule_id,
                value=json.dumps({
                    "pattern_id": pattern_id,
                    "capsule_id": capsule_id,
                    "pattern_name": pattern["name"],
                    "pattern_type": "sequential",
                    "confidence": pattern["confidence"],
                    "timestamp": now.isoformat()
                })
            )
        
        # Detect temporal patterns
        temporal_patterns = self._detect_temporal_patterns(mutations)
        for pattern in temporal_patterns:
            pattern_id = f"pattern-{uuid.uuid4()}"
            pattern_obj = MutationPattern(
                pattern_id=pattern_id,
                capsule_id=capsule_id,
                pattern_name=pattern["name"],
                pattern_description=pattern["description"],
                mutation_types=pattern["mutation_types"],
                frequency=pattern["frequency"],
                confidence=pattern["confidence"],
                first_observed=pattern["first_observed"],
                last_observed=pattern["last_observed"],
                metadata={
                    "pattern_type": "temporal",
                    "period_hours": pattern["period_hours"]
                }
            )
            
            mutation_patterns[pattern_id] = pattern_obj.dict()
            pattern_ids.append(pattern_id)
            
            # Publish pattern to Kafka
            kafka_producer.produce(
                topic="capsule-mutation-patterns",
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
        
        # Detect source patterns
        source_patterns = self._detect_source_patterns(mutations)
        for pattern in source_patterns:
            pattern_id = f"pattern-{uuid.uuid4()}"
            pattern_obj = MutationPattern(
                pattern_id=pattern_id,
                capsule_id=capsule_id,
                pattern_name=pattern["name"],
                pattern_description=pattern["description"],
                mutation_types=pattern["mutation_types"],
                frequency=pattern["frequency"],
                confidence=pattern["confidence"],
                first_observed=pattern["first_observed"],
                last_observed=pattern["last_observed"],
                metadata={
                    "pattern_type": "source",
                    "source": pattern["source"]
                }
            )
            
            mutation_patterns[pattern_id] = pattern_obj.dict()
            pattern_ids.append(pattern_id)
            
            # Publish pattern to Kafka
            kafka_producer.produce(
                topic="capsule-mutation-patterns",
                key=capsule_id,
                value=json.dumps({
                    "pattern_id": pattern_id,
                    "capsule_id": capsule_id,
                    "pattern_name": pattern["name"],
                    "pattern_type": "source",
                    "confidence": pattern["confidence"],
                    "timestamp": now.isoformat()
                })
            )
        
        return pattern_ids
    
    def _detect_sequential_patterns(self, mutations: List[MutationEvent]) -> List[Dict[str, Any]]:
        """
        Detect sequential mutation patterns.
        
        Args:
            mutations: List of mutation events
            
        Returns:
            List[Dict[str, Any]]: List of detected patterns
        """
        patterns = []
        
        # Sort mutations by timestamp
        sorted_mutations = sorted(mutations, key=lambda m: m.timestamp)
        
        # Extract mutation types sequence
        mutation_types = [m.mutation_type for m in sorted_mutations]
        
        # Look for repeating sequences of 2-4 mutation types
        for sequence_length in range(2, 5):
            if len(mutation_types) < sequence_length * 2:
                continue  # Not enough data for this sequence length
            
            # Count occurrences of each sequence
            sequence_counts = {}
            
            for i in range(len(mutation_types) - sequence_length + 1):
                sequence = tuple(mutation_types[i:i+sequence_length])
                if sequence not in sequence_counts:
                    sequence_counts[sequence] = 0
                sequence_counts[sequence] += 1
            
            # Find sequences that occur multiple times
            for sequence, count in sequence_counts.items():
                if count >= 2:  # At least 2 occurrences
                    # Calculate frequency
                    frequency = count / (len(mutation_types) - sequence_length + 1)
                    
                    # Calculate confidence based on frequency and count
                    confidence = min(0.5 + (frequency * 0.5) + (count / 10), 1.0)
                    
                    # Find first and last occurrence
                    first_index = mutation_types.index(sequence[0])
                    for i in range(first_index, len(mutation_types) - sequence_length + 1):
                        if tuple(mutation_types[i:i+sequence_length]) == sequence:
                            first_index = i
                            break
                    
                    last_index = len(mutation_types) - 1
                    for i in range(len(mutation_types) - sequence_length, -1, -1):
                        if tuple(mutation_types[i:i+sequence_length]) == sequence:
                            last_index = i + sequence_length - 1
                            break
                    
                    first_observed = sorted_mutations[first_index].timestamp
                    last_observed = sorted_mutations[last_index].timestamp
                    
                    # Create pattern
                    pattern = {
                        "name": f"Sequential Pattern: {' -> '.join(sequence)}",
                        "description": f"Sequence of {sequence_length} mutation types that repeats {count} times",
                        "mutation_types": list(sequence),
                        "frequency": frequency,
                        "confidence": confidence,
                        "first_observed": first_observed,
                        "last_observed": last_observed,
                        "occurrences": count
                    }
                    
                    patterns.append(pattern)
        
        # Sort by confidence (highest first)
        patterns.sort(key=lambda p: p["confidence"], reverse=True)
        
        return patterns
    
    def _detect_temporal_patterns(self, mutations: List[MutationEvent]) -> List[Dict[str, Any]]:
        """
        Detect temporal mutation patterns.
        
        Args:
            mutations: List of mutation events
            
        Returns:
            List[Dict[str, Any]]: List of detected patterns
        """
        patterns = []
        
        # Sort mutations by timestamp
        sorted_mutations = sorted(mutations, key=lambda m: m.timestamp)
        
        # Group mutations by type
        mutations_by_type = {}
        for mutation in sorted_mutations:
            if mutation.mutation_type not in mutations_by_type:
                mutations_by_type[mutation.mutation_type] = []
            mutations_by_type[mutation.mutation_type].append(mutation)
        
        # For each mutation type with enough data, look for temporal patterns
        for mutation_type, type_mutations in mutations_by_type.items():
            if len(type_mutations) < 3:
                continue  # Not enough data
            
            # Calculate time differences between consecutive mutations
            time_diffs = []
            for i in range(1, len(type_mutations)):
                diff = (type_mutations[i].timestamp - type_mutations[i-1].timestamp).total_seconds() / 3600  # Hours
                time_diffs.append(diff)
            
            # Check if time differences are consistent
            if len(time_diffs) < 2:
                continue
            
            mean_diff = sum(time_diffs) / len(time_diffs)
            variance = sum((diff - mean_diff) ** 2 for diff in time_diffs) / len(time_diffs)
            std_dev = variance ** 0.5
            
            # If standard deviation is less than 25% of mean, consider it a pattern
            if std_dev < mean_diff * 0.25 and mean_diff > 1:  # At least 1 hour apart
                # Calculate confidence based on consistency and number of occurrences
                consistency = 1.0 - (std_dev / mean_diff)
                occurrences = len(type_mutations)
                confidence = min(0.5 + (consistency * 0.3) + (occurrences / 20), 1.0)
                
                # Create pattern
                pattern = {
                    "name": f"Temporal Pattern: {mutation_type} every {mean_diff:.1f} hours",
                    "description": f"{mutation_type} mutations occur approximately every {mean_diff:.1f} hours (±{std_dev:.1f} hours)",
                    "mutation_types": [mutation_type],
                    "frequency": 1.0 / mean_diff,  # Frequency per hour
                    "confidence": confidence,
                    "first_observed": type_mutations[0].timestamp,
                    "last_observed": type_mutations[-1].timestamp,
                    "period_hours": mean_diff
                }
                
                patterns.append(pattern)
        
        # Sort by confidence (highest first)
        patterns.sort(key=lambda p: p["confidence"], reverse=True)
        
        return patterns
    
    def _detect_source_patterns(self, mutations: List[MutationEvent]) -> List[Dict[str, Any]]:
        """
        Detect source-based mutation patterns.
        
        Args:
            mutations: List of mutation events
            
        Returns:
            List[Dict[str, Any]]: List of detected patterns
        """
        patterns = []
        
        # Group mutations by source
        mutations_by_source = {}
        for mutation in mutations:
            if mutation.source not in mutations_by_source:
                mutations_by_source[mutation.source] = []
            mutations_by_source[mutation.source].append(mutation)
        
        # For each source with enough data, look for patterns
        for source, source_mutations in mutations_by_source.items():
            if len(source_mutations) < 3:
                continue  # Not enough data
            
            # Count mutation types for this source
            type_counts = {}
            for mutation in source_mutations:
                if mutation.mutation_type not in type_counts:
                    type_counts[mutation.mutation_type] = 0
                type_counts[mutation.mutation_type] += 1
            
            # Find dominant mutation types (>25% of mutations)
            dominant_types = []
            for mutation_type, count in type_counts.items():
                if count / len(source_mutations) > 0.25:
                    dominant_types.append(mutation_type)
            
            if dominant_types:
                # Calculate frequency
                frequency = len(source_mutations) / len(mutations)
                
                # Calculate confidence based on frequency and dominance
                dominance = sum(type_counts[t] for t in dominant_types) / len(source_mutations)
                confidence = min(0.5 + (frequency * 0.3) + (dominance * 0.2), 1.0)
                
                # Sort source mutations by timestamp
                sorted_source_mutations = sorted(source_mutations, key=lambda m: m.timestamp)
                
                # Create pattern
                pattern = {
                    "name": f"Source Pattern: {source} -> {', '.join(dominant_types)}",
                    "description": f"Source '{source}' predominantly causes {', '.join(dominant_types)} mutations",
                    "mutation_types": dominant_types,
                    "frequency": frequency,
                    "confidence": confidence,
                    "first_observed": sorted_source_mutations[0].timestamp,
                    "last_observed": sorted_source_mutations[-1].timestamp,
                    "source": source
                }
                
                patterns.append(pattern)
        
        # Sort by confidence (highest first)
        patterns.sort(key=lambda p: p["confidence"], reverse=True)
        
        return patterns
    
    def get_pattern(self, pattern_id: str) -> Optional[MutationPattern]:
        """
        Get a mutation pattern by ID.
        
        Args:
            pattern_id: The pattern ID
            
        Returns:
            Optional[MutationPattern]: The pattern, or None if not found
        """
        if pattern_id not in mutation_patterns:
            return None
        
        return MutationPattern(**mutation_patterns[pattern_id])
    
    def list_patterns(
        self, 
        capsule_id: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 10
    ) -> List[MutationPattern]:
        """
        List mutation patterns, optionally filtered.
        
        Args:
            capsule_id: Optional capsule ID to filter by
            min_confidence: Minimum confidence level
            limit: Maximum number of patterns to return
            
        Returns:
            List[MutationPattern]: List of matching patterns
        """
        results = []
        
        for pattern_dict in mutation_patterns.values():
            # Apply filters
            if capsule_id and pattern_dict["capsule_id"] != capsule_id:
                continue
            
            if pattern_dict["confidence"] < min_confidence:
                continue
            
            results.append(MutationPattern(**pattern_dict))
        
        # Sort by confidence (highest first)
        results.sort(key=lambda p: p.confidence, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def analyze_mutations(self, request: MutationAnalysisRequest) -> Dict[str, Any]:
        """
        Analyze mutations for a capsule.
        
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
        
        # Get mutations for the capsule in the time period
        mutations = self.list_mutations(
            capsule_id=request.capsule_id,
            start_time=start_time,
            end_time=now,
            limit=1000  # High limit to get all mutations
        )
        
        if not mutations:
            return {
                "capsule_id": request.capsule_id,
                "status": "insufficient_data",
                "message": "No mutations found in the specified time period",
                "time_period": request.time_period
            }
        
        # Count mutations by type
        mutation_types = {}
        for mutation in mutations:
            if mutation.mutation_type not in mutation_types:
                mutation_types[mutation.mutation_type] = 0
            mutation_types[mutation.mutation_type] += 1
        
        # Count mutations by source
        mutation_sources = {}
        for mutation in mutations:
            if mutation.source not in mutation_sources:
                mutation_sources[mutation.source] = 0
            mutation_sources[mutation.source] += 1
        
        # Calculate mutation frequency over time
        # Group mutations by day
        mutations_by_day = {}
        for mutation in mutations:
            day = mutation.timestamp.date().isoformat()
            if day not in mutations_by_day:
                mutations_by_day[day] = 0
            mutations_by_day[day] += 1
        
        # Ensure all days in the range are represented
        current_date = start_time.date()
        while current_date <= now.date():
            day = current_date.isoformat()
            if day not in mutations_by_day:
                mutations_by_day[day] = 0
            current_date += timedelta(days=1)
        
        # Sort days
        days = sorted(mutations_by_day.keys())
        daily_counts = [mutations_by_day[day] for day in days]
        
        # Calculate mutation rate (mutations per day)
        days_in_period = (now - start_time).days or 1  # Avoid division by zero
        mutation_rate = len(mutations) / days_in_period
        
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
            "mutation_count": len(mutations),
            "mutation_rate": mutation_rate,
            "mutation_types": mutation_types,
            "mutation_sources": mutation_sources,
            "daily_activity": {
                "days": days,
                "counts": daily_counts
            },
            "patterns": [p.dict() for p in patterns] if patterns else []
        }
        
        return results
    
    def run_scheduled_pattern_detection(self):
        """Run scheduled pattern detection."""
        now = datetime.now()
        
        # Check daily pattern detection
        if (now - self.last_pattern_detection_time["daily"]).total_seconds() >= self.pattern_detection_schedule["daily"]:
            logger.info("Running daily mutation pattern detection")
            self._detect_patterns_for_all_capsules()
            self.last_pattern_detection_time["daily"] = now
    
    def _detect_patterns_for_all_capsules(self):
        """Detect patterns for all capsules."""
        # Get unique capsule IDs from mutations
        capsule_ids = set()
        for mutation_dict in mutation_events.values():
            capsule_ids.add(mutation_dict["capsule_id"])
        
        for capsule_id in capsule_ids:
            try:
                self.detect_patterns(capsule_id)
            except Exception as e:
                logger.error(f"Error detecting patterns for capsule {capsule_id}: {e}")

# Create singleton instance
mutation_tracker = MutationTracker()

# API endpoints (if this were a standalone service)
app = FastAPI(
    title="Mutation Tracker",
    description="Mutation Tracker for the Overseer System",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mutation_tracker", "timestamp": datetime.now().isoformat()}

@app.post("/mutations")
async def create_mutation(mutation: MutationEvent):
    """Track a capsule mutation event."""
    mutation_id = mutation_tracker.track_mutation(mutation)
    return {"mutation_id": mutation_id, "status": "created"}

@app.get("/mutations")
async def list_mutations(
    capsule_id: Optional[str] = None,
    mutation_type: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 10
):
    """List mutation events."""
    mutations = mutation_tracker.list_mutations(
        capsule_id=capsule_id,
        mutation_type=mutation_type,
        source=source,
        limit=limit
    )
    return {"mutations": mutations, "count": len(mutations)}

@app.get("/mutations/{mutation_id}")
async def get_mutation(mutation_id: str):
    """Get a mutation event by ID."""
    mutation = mutation_tracker.get_mutation(mutation_id)
    if not mutation:
        raise HTTPException(status_code=404, detail=f"Mutation {mutation_id} not found")
    return mutation

@app.post("/patterns/{capsule_id}")
async def detect_patterns(capsule_id: str):
    """Detect mutation patterns for a capsule."""
    pattern_ids = mutation_tracker.detect_patterns(capsule_id)
    return {"pattern_ids": pattern_ids, "count": len(pattern_ids)}

@app.get("/patterns")
async def list_patterns(
    capsule_id: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 10
):
    """List mutation patterns."""
    patterns = mutation_tracker.list_patterns(
        capsule_id=capsule_id,
        min_confidence=min_confidence,
        limit=limit
    )
    return {"patterns": patterns, "count": len(patterns)}

@app.get("/patterns/{pattern_id}")
async def get_pattern(pattern_id: str):
    """Get a mutation pattern by ID."""
    pattern = mutation_tracker.get_pattern(pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not found")
    return pattern

@app.post("/analyze")
async def analyze_mutations(request: MutationAnalysisRequest):
    """Analyze mutations for a capsule."""
    results = mutation_tracker.analyze_mutations(request)
    return results

@app.post("/run-scheduled")
async def run_scheduled_pattern_detection():
    """Manually trigger scheduled pattern detection."""
    mutation_tracker.run_scheduled_pattern_detection()
    return {"status": "success", "message": "Scheduled pattern detection triggered"}

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Mutation Tracker starting up")
    
    # Subscribe to relevant Kafka topics
    kafka_consumer.subscribe(["capsule-events", "capsule-mutation-events"])
    
    logger.info("Mutation Tracker started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Mutation Tracker shutting down")
    
    # Close Kafka connections
    kafka_producer.close()
    kafka_consumer.close()
    
    logger.info("Mutation Tracker shut down successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
