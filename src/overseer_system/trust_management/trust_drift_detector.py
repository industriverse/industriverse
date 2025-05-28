"""
Trust Drift Detector for the Overseer System.

This module provides comprehensive trust drift detection capabilities for the Overseer System,
enabling the detection, analysis, and management of trust drift between entities over time.

The Trust Drift Detector is a critical component of the Trust Management framework,
providing insights into how trust relationships evolve and identifying potential issues.

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

import numpy as np
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from pydantic import BaseModel, Field
from scipy import stats

# Import MCP/A2A integration
from ..mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from ..a2a_integration.a2a_protocol_bridge import A2AProtocolBridge

# Import event bus
from ..event_bus.kafka_client import KafkaProducer, KafkaConsumer

# Import trust relationship graph
from .trust_relationship_graph import trust_relationship_graph

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("trust_drift_detector")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="trust-drift-detector"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="trust-drift-detector",
    auto_offset_reset="earliest"
)

# Data models
class TrustSnapshot(BaseModel):
    """Model for trust snapshots."""
    snapshot_id: str = Field(..., description="Unique snapshot identifier")
    entity_id: str = Field(..., description="Entity ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Snapshot timestamp")
    incoming_trust: Dict[str, float] = Field(default_factory=dict, description="Incoming trust scores by source entity")
    outgoing_trust: Dict[str, float] = Field(default_factory=dict, description="Outgoing trust scores by target entity")
    avg_incoming_trust: float = Field(0.0, description="Average incoming trust score")
    avg_outgoing_trust: float = Field(0.0, description="Average outgoing trust score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TrustDrift(BaseModel):
    """Model for trust drift between snapshots."""
    drift_id: str = Field(..., description="Unique drift identifier")
    entity_id: str = Field(..., description="Entity ID")
    start_snapshot_id: str = Field(..., description="Starting snapshot ID")
    end_snapshot_id: str = Field(..., description="Ending snapshot ID")
    start_timestamp: datetime = Field(..., description="Start timestamp")
    end_timestamp: datetime = Field(..., description="End timestamp")
    time_period: str = Field(..., description="Time period (e.g., '1d', '7d', '30d')")
    incoming_trust_drift: Dict[str, float] = Field(default_factory=dict, description="Incoming trust drift by source entity")
    outgoing_trust_drift: Dict[str, float] = Field(default_factory=dict, description="Outgoing trust drift by target entity")
    avg_incoming_drift: float = Field(0.0, description="Average incoming trust drift")
    avg_outgoing_drift: float = Field(0.0, description="Average outgoing trust drift")
    drift_magnitude: float = Field(0.0, description="Overall drift magnitude")
    drift_direction: str = Field("stable", description="Overall drift direction (increasing, decreasing, stable)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DriftAlert(BaseModel):
    """Model for trust drift alerts."""
    alert_id: str = Field(..., description="Unique alert identifier")
    drift_id: str = Field(..., description="Associated drift ID")
    entity_id: str = Field(..., description="Entity ID")
    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity (low, medium, high)")
    description: str = Field(..., description="Alert description")
    timestamp: datetime = Field(default_factory=datetime.now, description="Alert timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DriftAnalysisRequest(BaseModel):
    """Model for drift analysis requests."""
    entity_id: str = Field(..., description="Entity ID to analyze")
    time_period: str = Field("7d", description="Time period to analyze (e.g., '1d', '7d', '30d')")
    min_drift_threshold: float = Field(0.1, description="Minimum drift threshold to consider significant")

# In-memory storage (would be replaced with database in production)
trust_snapshots = {}
trust_drifts = {}
drift_alerts = {}

class TrustDriftDetector:
    """
    Trust Drift Detector implementation for the Overseer System.
    
    This class provides methods for detecting and analyzing trust drift, including:
    - Creating trust snapshots
    - Calculating trust drift between snapshots
    - Detecting significant drift
    - Generating alerts for concerning drift patterns
    """
    
    def __init__(self):
        """Initialize the Trust Drift Detector."""
        self.snapshot_schedule = {
            "hourly": 60 * 60,  # Every hour
            "daily": 24 * 60 * 60,  # Every day
            "weekly": 7 * 24 * 60 * 60  # Every week
        }
        self.last_snapshot_time = {
            "hourly": datetime.now() - timedelta(hours=2),  # Force immediate snapshot
            "daily": datetime.now() - timedelta(days=2),
            "weekly": datetime.now() - timedelta(weeks=2)
        }
        logger.info("Trust Drift Detector initialized")
    
    def create_snapshot(self, entity_id: str) -> str:
        """
        Create a trust snapshot for an entity.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            str: Snapshot ID
        """
        # Verify entity exists
        entity = trust_relationship_graph.get_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        # Get incoming relationships
        incoming_relationships = trust_relationship_graph.list_relationships(target_id=entity_id)
        incoming_trust = {}
        for rel in incoming_relationships:
            incoming_trust[rel.source_id] = rel.trust_score
        
        # Get outgoing relationships
        outgoing_relationships = trust_relationship_graph.list_relationships(source_id=entity_id)
        outgoing_trust = {}
        for rel in outgoing_relationships:
            outgoing_trust[rel.target_id] = rel.trust_score
        
        # Calculate average trust scores
        avg_incoming_trust = sum(incoming_trust.values()) / len(incoming_trust) if incoming_trust else 0.0
        avg_outgoing_trust = sum(outgoing_trust.values()) / len(outgoing_trust) if outgoing_trust else 0.0
        
        # Create snapshot
        snapshot_id = f"snapshot-{uuid.uuid4()}"
        snapshot = TrustSnapshot(
            snapshot_id=snapshot_id,
            entity_id=entity_id,
            timestamp=datetime.now(),
            incoming_trust=incoming_trust,
            outgoing_trust=outgoing_trust,
            avg_incoming_trust=avg_incoming_trust,
            avg_outgoing_trust=avg_outgoing_trust,
            metadata={
                "entity_name": entity.name,
                "entity_type": entity.type,
                "incoming_count": len(incoming_trust),
                "outgoing_count": len(outgoing_trust)
            }
        )
        
        # Store the snapshot
        trust_snapshots[snapshot_id] = snapshot.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="trust-events",
            key=entity_id,
            value=json.dumps({
                "event_type": "trust_snapshot_created",
                "snapshot_id": snapshot_id,
                "entity_id": entity_id,
                "timestamp": snapshot.timestamp.isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "trust_snapshot_created",
            "snapshot_id": snapshot_id,
            "entity_id": entity_id
        }
        mcp_bridge.send_context_update("trust_drift_detector", mcp_context)
        
        return snapshot_id
    
    def get_snapshot(self, snapshot_id: str) -> Optional[TrustSnapshot]:
        """
        Get a trust snapshot by ID.
        
        Args:
            snapshot_id: The snapshot ID
            
        Returns:
            Optional[TrustSnapshot]: The snapshot, or None if not found
        """
        if snapshot_id not in trust_snapshots:
            return None
        
        return TrustSnapshot(**trust_snapshots[snapshot_id])
    
    def list_snapshots(self, entity_id: Optional[str] = None, limit: int = 10) -> List[TrustSnapshot]:
        """
        List trust snapshots, optionally filtered by entity.
        
        Args:
            entity_id: Optional entity ID to filter by
            limit: Maximum number of snapshots to return
            
        Returns:
            List[TrustSnapshot]: List of matching snapshots
        """
        results = []
        
        for snapshot_dict in trust_snapshots.values():
            # Apply filter
            if entity_id and snapshot_dict["entity_id"] != entity_id:
                continue
            
            results.append(TrustSnapshot(**snapshot_dict))
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda s: s.timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def get_latest_snapshot(self, entity_id: str) -> Optional[TrustSnapshot]:
        """
        Get the latest trust snapshot for an entity.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            Optional[TrustSnapshot]: The latest snapshot, or None if not found
        """
        snapshots = self.list_snapshots(entity_id, limit=1)
        return snapshots[0] if snapshots else None
    
    def calculate_drift(self, entity_id: str, time_period: str) -> Optional[TrustDrift]:
        """
        Calculate trust drift for an entity over a time period.
        
        Args:
            entity_id: The entity ID
            time_period: Time period to analyze (e.g., '1d', '7d', '30d')
            
        Returns:
            Optional[TrustDrift]: The calculated drift, or None if insufficient data
        """
        # Get all snapshots for the entity
        all_snapshots = self.list_snapshots(entity_id, limit=100)
        if len(all_snapshots) < 2:
            return None
        
        # Determine time range based on period
        end_snapshot = all_snapshots[0]  # Latest snapshot
        end_time = end_snapshot.timestamp
        
        if time_period == "1d":
            start_time = end_time - timedelta(days=1)
        elif time_period == "7d":
            start_time = end_time - timedelta(days=7)
        elif time_period == "30d":
            start_time = end_time - timedelta(days=30)
        else:
            # Default to 7 days
            start_time = end_time - timedelta(days=7)
            time_period = "7d"
        
        # Find closest snapshot to start time
        start_snapshot = None
        min_diff = timedelta.max
        
        for snapshot in all_snapshots:
            diff = abs(snapshot.timestamp - start_time)
            if diff < min_diff:
                min_diff = diff
                start_snapshot = snapshot
        
        if start_snapshot == end_snapshot:
            return None
        
        # Calculate drift between snapshots
        incoming_trust_drift = {}
        outgoing_trust_drift = {}
        
        # Calculate incoming trust drift
        all_sources = set(start_snapshot.incoming_trust.keys()) | set(end_snapshot.incoming_trust.keys())
        for source_id in all_sources:
            start_trust = start_snapshot.incoming_trust.get(source_id, 0.0)
            end_trust = end_snapshot.incoming_trust.get(source_id, 0.0)
            incoming_trust_drift[source_id] = end_trust - start_trust
        
        # Calculate outgoing trust drift
        all_targets = set(start_snapshot.outgoing_trust.keys()) | set(end_snapshot.outgoing_trust.keys())
        for target_id in all_targets:
            start_trust = start_snapshot.outgoing_trust.get(target_id, 0.0)
            end_trust = end_snapshot.outgoing_trust.get(target_id, 0.0)
            outgoing_trust_drift[target_id] = end_trust - start_trust
        
        # Calculate average drift
        avg_incoming_drift = end_snapshot.avg_incoming_trust - start_snapshot.avg_incoming_trust
        avg_outgoing_drift = end_snapshot.avg_outgoing_trust - start_snapshot.avg_outgoing_trust
        
        # Calculate overall drift magnitude and direction
        drift_values = list(incoming_trust_drift.values()) + list(outgoing_trust_drift.values())
        drift_magnitude = sum(abs(v) for v in drift_values) / len(drift_values) if drift_values else 0.0
        
        if drift_magnitude < 0.05:  # Arbitrary threshold
            drift_direction = "stable"
        elif avg_incoming_drift + avg_outgoing_drift > 0:
            drift_direction = "increasing"
        else:
            drift_direction = "decreasing"
        
        # Create drift object
        drift_id = f"drift-{uuid.uuid4()}"
        drift = TrustDrift(
            drift_id=drift_id,
            entity_id=entity_id,
            start_snapshot_id=start_snapshot.snapshot_id,
            end_snapshot_id=end_snapshot.snapshot_id,
            start_timestamp=start_snapshot.timestamp,
            end_timestamp=end_snapshot.timestamp,
            time_period=time_period,
            incoming_trust_drift=incoming_trust_drift,
            outgoing_trust_drift=outgoing_trust_drift,
            avg_incoming_drift=avg_incoming_drift,
            avg_outgoing_drift=avg_outgoing_drift,
            drift_magnitude=drift_magnitude,
            drift_direction=drift_direction,
            metadata={
                "entity_name": start_snapshot.metadata.get("entity_name", ""),
                "entity_type": start_snapshot.metadata.get("entity_type", ""),
                "time_diff_hours": (end_snapshot.timestamp - start_snapshot.timestamp).total_seconds() / 3600
            }
        )
        
        # Store the drift
        trust_drifts[drift_id] = drift.dict()
        
        # Check for significant drift and generate alerts
        self._check_for_alerts(drift)
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="trust-events",
            key=entity_id,
            value=json.dumps({
                "event_type": "trust_drift_calculated",
                "drift_id": drift_id,
                "entity_id": entity_id,
                "time_period": time_period,
                "drift_magnitude": drift_magnitude,
                "drift_direction": drift_direction,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        return drift
    
    def get_drift(self, drift_id: str) -> Optional[TrustDrift]:
        """
        Get a trust drift by ID.
        
        Args:
            drift_id: The drift ID
            
        Returns:
            Optional[TrustDrift]: The drift, or None if not found
        """
        if drift_id not in trust_drifts:
            return None
        
        return TrustDrift(**trust_drifts[drift_id])
    
    def list_drifts(self, entity_id: Optional[str] = None, limit: int = 10) -> List[TrustDrift]:
        """
        List trust drifts, optionally filtered by entity.
        
        Args:
            entity_id: Optional entity ID to filter by
            limit: Maximum number of drifts to return
            
        Returns:
            List[TrustDrift]: List of matching drifts
        """
        results = []
        
        for drift_dict in trust_drifts.values():
            # Apply filter
            if entity_id and drift_dict["entity_id"] != entity_id:
                continue
            
            results.append(TrustDrift(**drift_dict))
        
        # Sort by end timestamp (newest first)
        results.sort(key=lambda d: d.end_timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def _check_for_alerts(self, drift: TrustDrift) -> List[str]:
        """
        Check for alert conditions in a trust drift.
        
        Args:
            drift: The trust drift to check
            
        Returns:
            List[str]: List of generated alert IDs
        """
        alert_ids = []
        
        # Check for rapid trust decrease
        if drift.drift_magnitude > 0.2 and drift.drift_direction == "decreasing":
            alert_id = f"alert-{uuid.uuid4()}"
            alert = DriftAlert(
                alert_id=alert_id,
                drift_id=drift.drift_id,
                entity_id=drift.entity_id,
                alert_type="rapid_trust_decrease",
                severity="high",
                description=f"Rapid trust decrease detected for entity {drift.entity_id} (magnitude: {drift.drift_magnitude:.2f})",
                metadata={
                    "drift_magnitude": drift.drift_magnitude,
                    "avg_incoming_drift": drift.avg_incoming_drift,
                    "avg_outgoing_drift": drift.avg_outgoing_drift
                }
            )
            
            drift_alerts[alert_id] = alert.dict()
            alert_ids.append(alert_id)
            
            # Publish alert to Kafka
            kafka_producer.produce(
                topic="alert-events",
                key=drift.entity_id,
                value=json.dumps({
                    "event_type": "trust_drift_alert",
                    "alert_id": alert_id,
                    "entity_id": drift.entity_id,
                    "alert_type": "rapid_trust_decrease",
                    "severity": "high",
                    "timestamp": datetime.now().isoformat()
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "trust_drift_alert",
                "alert_id": alert_id,
                "entity_id": drift.entity_id,
                "alert_type": "rapid_trust_decrease",
                "severity": "high"
            }
            mcp_bridge.send_context_update("trust_drift_detector", mcp_context)
        
        # Check for unusual trust increase
        elif drift.drift_magnitude > 0.3 and drift.drift_direction == "increasing":
            alert_id = f"alert-{uuid.uuid4()}"
            alert = DriftAlert(
                alert_id=alert_id,
                drift_id=drift.drift_id,
                entity_id=drift.entity_id,
                alert_type="unusual_trust_increase",
                severity="medium",
                description=f"Unusual trust increase detected for entity {drift.entity_id} (magnitude: {drift.drift_magnitude:.2f})",
                metadata={
                    "drift_magnitude": drift.drift_magnitude,
                    "avg_incoming_drift": drift.avg_incoming_drift,
                    "avg_outgoing_drift": drift.avg_outgoing_drift
                }
            )
            
            drift_alerts[alert_id] = alert.dict()
            alert_ids.append(alert_id)
            
            # Publish alert to Kafka
            kafka_producer.produce(
                topic="alert-events",
                key=drift.entity_id,
                value=json.dumps({
                    "event_type": "trust_drift_alert",
                    "alert_id": alert_id,
                    "entity_id": drift.entity_id,
                    "alert_type": "unusual_trust_increase",
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat()
                })
            )
        
        # Check for trust asymmetry
        if abs(drift.avg_incoming_drift - drift.avg_outgoing_drift) > 0.25:
            alert_id = f"alert-{uuid.uuid4()}"
            alert = DriftAlert(
                alert_id=alert_id,
                drift_id=drift.drift_id,
                entity_id=drift.entity_id,
                alert_type="trust_asymmetry",
                severity="medium",
                description=f"Trust asymmetry detected for entity {drift.entity_id} (incoming vs outgoing drift)",
                metadata={
                    "avg_incoming_drift": drift.avg_incoming_drift,
                    "avg_outgoing_drift": drift.avg_outgoing_drift,
                    "asymmetry": abs(drift.avg_incoming_drift - drift.avg_outgoing_drift)
                }
            )
            
            drift_alerts[alert_id] = alert.dict()
            alert_ids.append(alert_id)
            
            # Publish alert to Kafka
            kafka_producer.produce(
                topic="alert-events",
                key=drift.entity_id,
                value=json.dumps({
                    "event_type": "trust_drift_alert",
                    "alert_id": alert_id,
                    "entity_id": drift.entity_id,
                    "alert_type": "trust_asymmetry",
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat()
                })
            )
        
        # Check for specific relationship changes
        significant_changes = []
        
        for source_id, drift_value in drift.incoming_trust_drift.items():
            if abs(drift_value) > 0.3:  # Significant change threshold
                significant_changes.append({
                    "type": "incoming",
                    "entity_id": source_id,
                    "drift": drift_value
                })
        
        for target_id, drift_value in drift.outgoing_trust_drift.items():
            if abs(drift_value) > 0.3:  # Significant change threshold
                significant_changes.append({
                    "type": "outgoing",
                    "entity_id": target_id,
                    "drift": drift_value
                })
        
        if significant_changes:
            alert_id = f"alert-{uuid.uuid4()}"
            alert = DriftAlert(
                alert_id=alert_id,
                drift_id=drift.drift_id,
                entity_id=drift.entity_id,
                alert_type="significant_relationship_changes",
                severity="medium",
                description=f"Significant trust changes in {len(significant_changes)} relationships for entity {drift.entity_id}",
                metadata={
                    "significant_changes": significant_changes
                }
            )
            
            drift_alerts[alert_id] = alert.dict()
            alert_ids.append(alert_id)
            
            # Publish alert to Kafka
            kafka_producer.produce(
                topic="alert-events",
                key=drift.entity_id,
                value=json.dumps({
                    "event_type": "trust_drift_alert",
                    "alert_id": alert_id,
                    "entity_id": drift.entity_id,
                    "alert_type": "significant_relationship_changes",
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat()
                })
            )
        
        return alert_ids
    
    def get_alert(self, alert_id: str) -> Optional[DriftAlert]:
        """
        Get a drift alert by ID.
        
        Args:
            alert_id: The alert ID
            
        Returns:
            Optional[DriftAlert]: The alert, or None if not found
        """
        if alert_id not in drift_alerts:
            return None
        
        return DriftAlert(**drift_alerts[alert_id])
    
    def list_alerts(
        self, 
        entity_id: Optional[str] = None, 
        alert_type: Optional[str] = None,
        min_severity: str = "low",
        limit: int = 10
    ) -> List[DriftAlert]:
        """
        List drift alerts, optionally filtered.
        
        Args:
            entity_id: Optional entity ID to filter by
            alert_type: Optional alert type to filter by
            min_severity: Minimum severity level to include
            limit: Maximum number of alerts to return
            
        Returns:
            List[DriftAlert]: List of matching alerts
        """
        results = []
        
        # Map severity levels to numeric values for comparison
        severity_levels = {
            "low": 0,
            "medium": 1,
            "high": 2
        }
        min_severity_level = severity_levels.get(min_severity.lower(), 0)
        
        for alert_dict in drift_alerts.values():
            # Apply filters
            if entity_id and alert_dict["entity_id"] != entity_id:
                continue
            
            if alert_type and alert_dict["alert_type"] != alert_type:
                continue
            
            alert_severity_level = severity_levels.get(alert_dict["severity"].lower(), 0)
            if alert_severity_level < min_severity_level:
                continue
            
            results.append(DriftAlert(**alert_dict))
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda a: a.timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def analyze_drift_patterns(self, entity_id: str) -> Dict[str, Any]:
        """
        Analyze drift patterns for an entity over time.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Get all drifts for the entity
        drifts = self.list_drifts(entity_id, limit=100)
        if len(drifts) < 2:
            return {
                "entity_id": entity_id,
                "status": "insufficient_data",
                "message": "Not enough drift data for pattern analysis"
            }
        
        # Extract drift magnitudes and directions over time
        timestamps = [d.end_timestamp for d in drifts]
        magnitudes = [d.drift_magnitude for d in drifts]
        incoming_drifts = [d.avg_incoming_drift for d in drifts]
        outgoing_drifts = [d.avg_outgoing_drift for d in drifts]
        
        # Calculate trend using linear regression
        x = np.array([(t - timestamps[-1]).total_seconds() / (24 * 3600) for t in timestamps])  # Days from latest
        y_mag = np.array(magnitudes)
        y_in = np.array(incoming_drifts)
        y_out = np.array(outgoing_drifts)
        
        slope_mag, _, r_value_mag, p_value_mag, _ = stats.linregress(x, y_mag)
        slope_in, _, r_value_in, p_value_in, _ = stats.linregress(x, y_in)
        slope_out, _, r_value_out, p_value_out, _ = stats.linregress(x, y_out)
        
        # Determine patterns
        patterns = []
        
        # Magnitude trend
        if abs(r_value_mag) > 0.5 and p_value_mag < 0.05:  # Statistically significant trend
            if slope_mag > 0:
                patterns.append({
                    "type": "increasing_volatility",
                    "confidence": abs(r_value_mag),
                    "description": "Trust volatility is increasing over time"
                })
            else:
                patterns.append({
                    "type": "decreasing_volatility",
                    "confidence": abs(r_value_mag),
                    "description": "Trust volatility is decreasing over time"
                })
        
        # Incoming trust trend
        if abs(r_value_in) > 0.5 and p_value_in < 0.05:
            if slope_in > 0:
                patterns.append({
                    "type": "increasing_incoming_trust",
                    "confidence": abs(r_value_in),
                    "description": "Incoming trust is consistently increasing"
                })
            else:
                patterns.append({
                    "type": "decreasing_incoming_trust",
                    "confidence": abs(r_value_in),
                    "description": "Incoming trust is consistently decreasing"
                })
        
        # Outgoing trust trend
        if abs(r_value_out) > 0.5 and p_value_out < 0.05:
            if slope_out > 0:
                patterns.append({
                    "type": "increasing_outgoing_trust",
                    "confidence": abs(r_value_out),
                    "description": "Outgoing trust is consistently increasing"
                })
            else:
                patterns.append({
                    "type": "decreasing_outgoing_trust",
                    "confidence": abs(r_value_out),
                    "description": "Outgoing trust is consistently decreasing"
                })
        
        # Check for cyclical patterns using autocorrelation
        if len(magnitudes) >= 10:
            try:
                autocorr = np.correlate(magnitudes, magnitudes, mode='full')
                autocorr = autocorr[len(autocorr)//2:]
                autocorr /= autocorr[0]  # Normalize
                
                # Look for peaks in autocorrelation
                peaks = []
                for i in range(1, len(autocorr)-1):
                    if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.5:
                        peaks.append(i)
                
                if peaks:
                    patterns.append({
                        "type": "cyclical_pattern",
                        "confidence": autocorr[peaks[0]],
                        "cycle_length": peaks[0],
                        "description": f"Cyclical trust pattern detected with period of approximately {peaks[0]} time units"
                    })
            except Exception as e:
                logger.error(f"Error in cyclical pattern detection: {e}")
        
        # Check for trust asymmetry pattern
        asymmetry_values = [abs(d.avg_incoming_drift - d.avg_outgoing_drift) for d in drifts]
        avg_asymmetry = sum(asymmetry_values) / len(asymmetry_values)
        
        if avg_asymmetry > 0.2:
            patterns.append({
                "type": "persistent_trust_asymmetry",
                "confidence": min(avg_asymmetry * 2, 1.0),
                "description": "Persistent asymmetry between incoming and outgoing trust"
            })
        
        # Determine overall trust trajectory
        avg_total_drift = sum(incoming_drifts) / len(incoming_drifts) + sum(outgoing_drifts) / len(outgoing_drifts)
        
        if abs(avg_total_drift) < 0.05:
            trajectory = "stable"
        elif avg_total_drift > 0:
            trajectory = "improving"
        else:
            trajectory = "declining"
        
        # Compile results
        results = {
            "entity_id": entity_id,
            "status": "success",
            "analysis_timestamp": datetime.now().isoformat(),
            "data_points": len(drifts),
            "time_span_days": (drifts[0].end_timestamp - drifts[-1].end_timestamp).total_seconds() / (24 * 3600),
            "avg_magnitude": sum(magnitudes) / len(magnitudes),
            "max_magnitude": max(magnitudes),
            "avg_incoming_drift": sum(incoming_drifts) / len(incoming_drifts),
            "avg_outgoing_drift": sum(outgoing_drifts) / len(outgoing_drifts),
            "trust_trajectory": trajectory,
            "patterns": patterns,
            "statistical_significance": {
                "magnitude_trend": {
                    "slope": slope_mag,
                    "r_value": r_value_mag,
                    "p_value": p_value_mag
                },
                "incoming_trend": {
                    "slope": slope_in,
                    "r_value": r_value_in,
                    "p_value": p_value_in
                },
                "outgoing_trend": {
                    "slope": slope_out,
                    "r_value": r_value_out,
                    "p_value": p_value_out
                }
            }
        }
        
        return results
    
    def run_scheduled_snapshots(self):
        """Run scheduled trust snapshots."""
        now = datetime.now()
        
        # Check hourly snapshots
        if (now - self.last_snapshot_time["hourly"]).total_seconds() >= self.snapshot_schedule["hourly"]:
            logger.info("Running hourly trust snapshots")
            self._create_snapshots_for_all_entities()
            self.last_snapshot_time["hourly"] = now
        
        # Check daily snapshots
        if (now - self.last_snapshot_time["daily"]).total_seconds() >= self.snapshot_schedule["daily"]:
            logger.info("Running daily trust drift analysis")
            self._analyze_drift_for_all_entities("1d")
            self.last_snapshot_time["daily"] = now
        
        # Check weekly snapshots
        if (now - self.last_snapshot_time["weekly"]).total_seconds() >= self.snapshot_schedule["weekly"]:
            logger.info("Running weekly trust drift analysis")
            self._analyze_drift_for_all_entities("7d")
            self.last_snapshot_time["weekly"] = now
    
    def _create_snapshots_for_all_entities(self):
        """Create trust snapshots for all entities."""
        entities = trust_relationship_graph.list_entities()
        
        for entity in entities:
            try:
                self.create_snapshot(entity.entity_id)
            except Exception as e:
                logger.error(f"Error creating snapshot for entity {entity.entity_id}: {e}")
    
    def _analyze_drift_for_all_entities(self, time_period: str):
        """Analyze trust drift for all entities."""
        entities = trust_relationship_graph.list_entities()
        
        for entity in entities:
            try:
                self.calculate_drift(entity.entity_id, time_period)
            except Exception as e:
                logger.error(f"Error analyzing drift for entity {entity.entity_id}: {e}")

# Create singleton instance
trust_drift_detector = TrustDriftDetector()

# API endpoints (if this were a standalone service)
app = FastAPI(
    title="Trust Drift Detector",
    description="Trust Drift Detector for the Overseer System",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "trust_drift_detector", "timestamp": datetime.now().isoformat()}

@app.post("/snapshots/{entity_id}")
async def create_snapshot(entity_id: str):
    """Create a trust snapshot for an entity."""
    try:
        snapshot_id = trust_drift_detector.create_snapshot(entity_id)
        return {"snapshot_id": snapshot_id, "status": "created"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/snapshots")
async def list_snapshots(entity_id: Optional[str] = None, limit: int = 10):
    """List trust snapshots."""
    snapshots = trust_drift_detector.list_snapshots(entity_id, limit)
    return {"snapshots": snapshots, "count": len(snapshots)}

@app.get("/snapshots/{snapshot_id}")
async def get_snapshot(snapshot_id: str):
    """Get a trust snapshot by ID."""
    snapshot = trust_drift_detector.get_snapshot(snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found")
    return snapshot

@app.get("/snapshots/latest/{entity_id}")
async def get_latest_snapshot(entity_id: str):
    """Get the latest trust snapshot for an entity."""
    snapshot = trust_drift_detector.get_latest_snapshot(entity_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"No snapshots found for entity {entity_id}")
    return snapshot

@app.post("/drifts/analyze")
async def analyze_drift(request: DriftAnalysisRequest):
    """Analyze trust drift for an entity."""
    drift = trust_drift_detector.calculate_drift(request.entity_id, request.time_period)
    if not drift:
        raise HTTPException(status_code=404, detail=f"Insufficient snapshot data for entity {request.entity_id}")
    return drift

@app.get("/drifts")
async def list_drifts(entity_id: Optional[str] = None, limit: int = 10):
    """List trust drifts."""
    drifts = trust_drift_detector.list_drifts(entity_id, limit)
    return {"drifts": drifts, "count": len(drifts)}

@app.get("/drifts/{drift_id}")
async def get_drift(drift_id: str):
    """Get a trust drift by ID."""
    drift = trust_drift_detector.get_drift(drift_id)
    if not drift:
        raise HTTPException(status_code=404, detail=f"Drift {drift_id} not found")
    return drift

@app.get("/alerts")
async def list_alerts(
    entity_id: Optional[str] = None,
    alert_type: Optional[str] = None,
    min_severity: str = "low",
    limit: int = 10
):
    """List drift alerts."""
    alerts = trust_drift_detector.list_alerts(entity_id, alert_type, min_severity, limit)
    return {"alerts": alerts, "count": len(alerts)}

@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    """Get a drift alert by ID."""
    alert = trust_drift_detector.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return alert

@app.get("/patterns/{entity_id}")
async def analyze_patterns(entity_id: str):
    """Analyze drift patterns for an entity."""
    results = trust_drift_detector.analyze_drift_patterns(entity_id)
    return results

@app.post("/run-scheduled")
async def run_scheduled_snapshots():
    """Manually trigger scheduled snapshots and analysis."""
    trust_drift_detector.run_scheduled_snapshots()
    return {"status": "success", "message": "Scheduled snapshots and analysis triggered"}

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Trust Drift Detector starting up")
    
    # Subscribe to relevant Kafka topics
    kafka_consumer.subscribe(["entity-events", "relationship-events", "trust-events"])
    
    logger.info("Trust Drift Detector started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Trust Drift Detector shutting down")
    
    # Close Kafka connections
    kafka_producer.close()
    kafka_consumer.close()
    
    logger.info("Trust Drift Detector shut down successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
