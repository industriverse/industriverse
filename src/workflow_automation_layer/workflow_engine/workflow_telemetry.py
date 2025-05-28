"""
Workflow Telemetry Module for Industriverse Workflow Automation Layer

This module is responsible for collecting, processing, and reporting telemetry
data for workflow executions. It provides insights into workflow performance,
reliability, and usage patterns across the Industriverse ecosystem.

The WorkflowTelemetry class is the central component that manages telemetry
data collection, storage, and reporting.
"""

import logging
import json
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from collections import defaultdict

import prometheus_client
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class TelemetryEventType(str, Enum):
    """Enum representing the types of telemetry events."""
    WORKFLOW_CREATED = "workflow_created"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_CANCELLED = "workflow_cancelled"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    HUMAN_INTERVENTION_REQUESTED = "human_intervention_requested"
    HUMAN_INTERVENTION_COMPLETED = "human_intervention_completed"
    AGENT_SELECTED = "agent_selected"
    AGENT_FAILED = "agent_failed"
    EXECUTION_MODE_CHANGED = "execution_mode_changed"
    ROUTING_DECISION = "routing_decision"
    ESCALATION_TRIGGERED = "escalation_triggered"
    FALLBACK_ACTIVATED = "fallback_activated"
    TRUST_SCORE_UPDATED = "trust_score_updated"
    PERFORMANCE_THRESHOLD_EXCEEDED = "performance_threshold_exceeded"


class TelemetryEvent(BaseModel):
    """Model representing a telemetry event."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: TelemetryEventType
    timestamp: datetime = Field(default_factory=datetime.now)
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    duration_ms: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TelemetryStorageType(str, Enum):
    """Enum representing the storage types for telemetry data."""
    MEMORY = "memory"
    FILE = "file"
    DATABASE = "database"
    PROMETHEUS = "prometheus"


class WorkflowTelemetry:
    """
    Telemetry manager for workflow executions.
    
    This class provides methods to collect, process, and report telemetry
    data for workflow executions across the Industriverse ecosystem.
    """
    
    def __init__(self, 
                storage_type: TelemetryStorageType = TelemetryStorageType.MEMORY, 
                storage_path: Optional[str] = None,
                enable_prometheus: bool = False,
                retention_days: int = 30):
        """
        Initialize the WorkflowTelemetry.
        
        Args:
            storage_type: The type of storage to use for telemetry data
            storage_path: The path to use for file storage (if applicable)
            enable_prometheus: Whether to enable Prometheus metrics
            retention_days: Number of days to retain telemetry data
        """
        self.storage_type = storage_type
        self.storage_path = storage_path
        self.enable_prometheus = enable_prometheus
        self.retention_days = retention_days
        
        # In-memory storage
        self.events: List[TelemetryEvent] = []
        
        # Event listeners
        self.event_listeners: Dict[TelemetryEventType, List[Callable]] = defaultdict(list)
        
        # Prometheus metrics (if enabled)
        if enable_prometheus:
            self._setup_prometheus_metrics()
        
        logger.info(f"WorkflowTelemetry initialized with {storage_type} storage")
    
    def _setup_prometheus_metrics(self):
        """Set up Prometheus metrics."""
        self.metrics = {
            # Workflow metrics
            "workflow_executions_total": prometheus_client.Counter(
                "workflow_executions_total",
                "Total number of workflow executions",
                ["workflow_id", "status"]
            ),
            "workflow_execution_duration_seconds": prometheus_client.Histogram(
                "workflow_execution_duration_seconds",
                "Duration of workflow executions in seconds",
                ["workflow_id"]
            ),
            "workflow_active_executions": prometheus_client.Gauge(
                "workflow_active_executions",
                "Number of currently active workflow executions",
                ["workflow_id"]
            ),
            
            # Task metrics
            "task_executions_total": prometheus_client.Counter(
                "task_executions_total",
                "Total number of task executions",
                ["workflow_id", "task_id", "status"]
            ),
            "task_execution_duration_seconds": prometheus_client.Histogram(
                "task_execution_duration_seconds",
                "Duration of task executions in seconds",
                ["workflow_id", "task_id"]
            ),
            
            # Agent metrics
            "agent_selections_total": prometheus_client.Counter(
                "agent_selections_total",
                "Total number of agent selections",
                ["agent_id"]
            ),
            "agent_failures_total": prometheus_client.Counter(
                "agent_failures_total",
                "Total number of agent failures",
                ["agent_id"]
            ),
            
            # Human intervention metrics
            "human_interventions_total": prometheus_client.Counter(
                "human_interventions_total",
                "Total number of human interventions",
                ["workflow_id"]
            ),
            "human_intervention_duration_seconds": prometheus_client.Histogram(
                "human_intervention_duration_seconds",
                "Duration of human interventions in seconds",
                ["workflow_id"]
            ),
            
            # Execution mode metrics
            "execution_mode_changes_total": prometheus_client.Counter(
                "execution_mode_changes_total",
                "Total number of execution mode changes",
                ["workflow_id", "from_mode", "to_mode"]
            ),
            
            # Escalation metrics
            "escalations_total": prometheus_client.Counter(
                "escalations_total",
                "Total number of escalations",
                ["workflow_id", "reason"]
            ),
            
            # Fallback metrics
            "fallbacks_total": prometheus_client.Counter(
                "fallbacks_total",
                "Total number of fallbacks",
                ["workflow_id", "reason"]
            ),
            
            # Trust metrics
            "trust_score_updates_total": prometheus_client.Counter(
                "trust_score_updates_total",
                "Total number of trust score updates",
                ["workflow_id", "agent_id"]
            ),
            "trust_score_value": prometheus_client.Gauge(
                "trust_score_value",
                "Current trust score value",
                ["workflow_id", "agent_id"]
            )
        }
    
    def register_event_listener(self, event_type: TelemetryEventType, listener: Callable):
        """
        Register a listener for telemetry events.
        
        Args:
            event_type: The type of event to listen for
            listener: The function to call when the event occurs
        """
        self.event_listeners[event_type].append(listener)
        logger.debug(f"Registered event listener for {event_type}")
    
    def _notify_listeners(self, event: TelemetryEvent):
        """
        Notify all registered listeners for an event.
        
        Args:
            event: The event to notify listeners about
        """
        for listener in self.event_listeners[event.type]:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in event listener for {event.type}: {e}")
    
    def record_event(self, event_type: TelemetryEventType, **kwargs) -> str:
        """
        Record a telemetry event.
        
        Args:
            event_type: The type of event to record
            **kwargs: Additional event data
            
        Returns:
            The ID of the recorded event
        """
        # Create the event
        event = TelemetryEvent(type=event_type, **kwargs)
        
        # Store the event
        self.events.append(event)
        
        # Update Prometheus metrics (if enabled)
        if self.enable_prometheus:
            self._update_prometheus_metrics(event)
        
        # Notify listeners
        self._notify_listeners(event)
        
        # Log the event
        logger.debug(f"Recorded telemetry event: {event.type} for workflow {event.workflow_id}")
        
        return event.id
    
    def _update_prometheus_metrics(self, event: TelemetryEvent):
        """
        Update Prometheus metrics based on a telemetry event.
        
        Args:
            event: The event to update metrics for
        """
        if not self.enable_prometheus:
            return
        
        try:
            # Update metrics based on event type
            if event.type == TelemetryEventType.WORKFLOW_STARTED:
                self.metrics["workflow_executions_total"].labels(
                    workflow_id=event.workflow_id or "unknown",
                    status="started"
                ).inc()
                self.metrics["workflow_active_executions"].labels(
                    workflow_id=event.workflow_id or "unknown"
                ).inc()
            
            elif event.type == TelemetryEventType.WORKFLOW_COMPLETED:
                self.metrics["workflow_executions_total"].labels(
                    workflow_id=event.workflow_id or "unknown",
                    status="completed"
                ).inc()
                self.metrics["workflow_active_executions"].labels(
                    workflow_id=event.workflow_id or "unknown"
                ).dec()
                if event.duration_ms:
                    self.metrics["workflow_execution_duration_seconds"].labels(
                        workflow_id=event.workflow_id or "unknown"
                    ).observe(event.duration_ms / 1000)
            
            elif event.type == TelemetryEventType.WORKFLOW_FAILED:
                self.metrics["workflow_executions_total"].labels(
                    workflow_id=event.workflow_id or "unknown",
                    status="failed"
                ).inc()
                self.metrics["workflow_active_executions"].labels(
                    workflow_id=event.workflow_id or "unknown"
                ).dec()
                if event.duration_ms:
                    self.metrics["workflow_execution_duration_seconds"].labels(
                        workflow_id=event.workflow_id or "unknown"
                    ).observe(event.duration_ms / 1000)
            
            elif event.type == TelemetryEventType.TASK_STARTED:
                pass  # No specific metric for task started
            
            elif event.type == TelemetryEventType.TASK_COMPLETED:
                self.metrics["task_executions_total"].labels(
                    workflow_id=event.workflow_id or "unknown",
                    task_id=event.task_id or "unknown",
                    status="completed"
                ).inc()
                if event.duration_ms:
                    self.metrics["task_execution_duration_seconds"].labels(
                        workflow_id=event.workflow_id or "unknown",
                        task_id=event.task_id or "unknown"
                    ).observe(event.duration_ms / 1000)
            
            elif event.type == TelemetryEventType.TASK_FAILED:
                self.metrics["task_executions_total"].labels(
                    workflow_id=event.workflow_id or "unknown",
                    task_id=event.task_id or "unknown",
                    status="failed"
                ).inc()
                if event.duration_ms:
                    self.metrics["task_execution_duration_seconds"].labels(
                        workflow_id=event.workflow_id or "unknown",
                        task_id=event.task_id or "unknown"
                    ).observe(event.duration_ms / 1000)
            
            elif event.type == TelemetryEventType.AGENT_SELECTED:
                self.metrics["agent_selections_total"].labels(
                    agent_id=event.agent_id or "unknown"
                ).inc()
            
            elif event.type == TelemetryEventType.AGENT_FAILED:
                self.metrics["agent_failures_total"].labels(
                    agent_id=event.agent_id or "unknown"
                ).inc()
            
            elif event.type == TelemetryEventType.HUMAN_INTERVENTION_REQUESTED:
                self.metrics["human_interventions_total"].labels(
                    workflow_id=event.workflow_id or "unknown"
                ).inc()
            
            elif event.type == TelemetryEventType.HUMAN_INTERVENTION_COMPLETED:
                if event.duration_ms:
                    self.metrics["human_intervention_duration_seconds"].labels(
                        workflow_id=event.workflow_id or "unknown"
                    ).observe(event.duration_ms / 1000)
            
            elif event.type == TelemetryEventType.EXECUTION_MODE_CHANGED:
                from_mode = event.metadata.get("from_mode", "unknown")
                to_mode = event.metadata.get("to_mode", "unknown")
                self.metrics["execution_mode_changes_total"].labels(
                    workflow_id=event.workflow_id or "unknown",
                    from_mode=from_mode,
                    to_mode=to_mode
                ).inc()
            
            elif event.type == TelemetryEventType.ESCALATION_TRIGGERED:
                reason = event.metadata.get("reason", "unknown")
                self.metrics["escalations_total"].labels(
                    workflow_id=event.workflow_id or "unknown",
                    reason=reason
                ).inc()
            
            elif event.type == TelemetryEventType.FALLBACK_ACTIVATED:
                reason = event.metadata.get("reason", "unknown")
                self.metrics["fallbacks_total"].labels(
                    workflow_id=event.workflow_id or "unknown",
                    reason=reason
                ).inc()
            
            elif event.type == TelemetryEventType.TRUST_SCORE_UPDATED:
                self.metrics["trust_score_updates_total"].labels(
                    workflow_id=event.workflow_id or "unknown",
                    agent_id=event.agent_id or "unknown"
                ).inc()
                
                trust_score = event.metadata.get("trust_score")
                if trust_score is not None:
                    self.metrics["trust_score_value"].labels(
                        workflow_id=event.workflow_id or "unknown",
                        agent_id=event.agent_id or "unknown"
                    ).set(trust_score)
        
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
    
    def get_events(self, 
                  workflow_id: Optional[str] = None,
                  execution_id: Optional[str] = None,
                  task_id: Optional[str] = None,
                  agent_id: Optional[str] = None,
                  event_type: Optional[TelemetryEventType] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  limit: Optional[int] = None) -> List[TelemetryEvent]:
        """
        Get telemetry events, optionally filtered by various criteria.
        
        Args:
            workflow_id: Filter by workflow ID
            execution_id: Filter by execution ID
            task_id: Filter by task ID
            agent_id: Filter by agent ID
            event_type: Filter by event type
            start_time: Filter by start time (inclusive)
            end_time: Filter by end time (inclusive)
            limit: Maximum number of events to return
            
        Returns:
            A list of TelemetryEvent objects matching the criteria
        """
        result = self.events
        
        # Apply filters
        if workflow_id:
            result = [e for e in result if e.workflow_id == workflow_id]
        
        if execution_id:
            result = [e for e in result if e.execution_id == execution_id]
        
        if task_id:
            result = [e for e in result if e.task_id == task_id]
        
        if agent_id:
            result = [e for e in result if e.agent_id == agent_id]
        
        if event_type:
            result = [e for e in result if e.type == event_type]
        
        if start_time:
            result = [e for e in result if e.timestamp >= start_time]
        
        if end_time:
            result = [e for e in result if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first)
        result.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            result = result[:limit]
        
        return result
    
    def get_workflow_execution_timeline(self, execution_id: str) -> List[TelemetryEvent]:
        """
        Get a timeline of events for a workflow execution.
        
        Args:
            execution_id: The execution ID of the workflow
            
        Returns:
            A list of TelemetryEvent objects for the workflow execution, sorted by timestamp
        """
        events = self.get_events(execution_id=execution_id)
        events.sort(key=lambda e: e.timestamp)
        return events
    
    def get_workflow_execution_duration(self, execution_id: str) -> Optional[int]:
        """
        Get the duration of a workflow execution in milliseconds.
        
        Args:
            execution_id: The execution ID of the workflow
            
        Returns:
            The duration in milliseconds, or None if the workflow is still running or not found
        """
        events = self.get_workflow_execution_timeline(execution_id)
        
        # Find start and end events
        start_event = next((e for e in events if e.type == TelemetryEventType.WORKFLOW_STARTED), None)
        end_event = next((e for e in events if e.type in [
            TelemetryEventType.WORKFLOW_COMPLETED,
            TelemetryEventType.WORKFLOW_FAILED,
            TelemetryEventType.WORKFLOW_CANCELLED
        ]), None)
        
        if not start_event or not end_event:
            return None
        
        # Calculate duration
        duration = (end_event.timestamp - start_event.timestamp).total_seconds() * 1000
        return int(duration)
    
    def get_task_execution_duration(self, execution_id: str, task_id: str) -> Optional[int]:
        """
        Get the duration of a task execution in milliseconds.
        
        Args:
            execution_id: The execution ID of the workflow
            task_id: The ID of the task
            
        Returns:
            The duration in milliseconds, or None if the task is still running or not found
        """
        events = self.get_events(execution_id=execution_id, task_id=task_id)
        
        # Find start and end events
        start_event = next((e for e in events if e.type == TelemetryEventType.TASK_STARTED), None)
        end_event = next((e for e in events if e.type in [
            TelemetryEventType.TASK_COMPLETED,
            TelemetryEventType.TASK_FAILED
        ]), None)
        
        if not start_event or not end_event:
            return None
        
        # Calculate duration
        duration = (end_event.timestamp - start_event.timestamp).total_seconds() * 1000
        return int(duration)
    
    def get_workflow_success_rate(self, workflow_id: str, time_window_days: int = 7) -> Optional[float]:
        """
        Get the success rate of a workflow over a time window.
        
        Args:
            workflow_id: The ID of the workflow
            time_window_days: The time window in days
            
        Returns:
            The success rate as a percentage, or None if no executions found
        """
        # Calculate start time
        start_time = datetime.now() - timedelta(days=time_window_days)
        
        # Get all completed or failed executions
        events = self.get_events(
            workflow_id=workflow_id,
            event_type=TelemetryEventType.WORKFLOW_COMPLETED,
            start_time=start_time
        )
        completed_count = len(events)
        
        events = self.get_events(
            workflow_id=workflow_id,
            event_type=TelemetryEventType.WORKFLOW_FAILED,
            start_time=start_time
        )
        failed_count = len(events)
        
        total_count = completed_count + failed_count
        if total_count == 0:
            return None
        
        return (completed_count / total_count) * 100
    
    def get_agent_success_rate(self, agent_id: str, time_window_days: int = 7) -> Optional[float]:
        """
        Get the success rate of an agent over a time window.
        
        Args:
            agent_id: The ID of the agent
            time_window_days: The time window in days
            
        Returns:
            The success rate as a percentage, or None if no executions found
        """
        # Calculate start time
        start_time = datetime.now() - timedelta(days=time_window_days)
        
        # Get all selections and failures
        events = self.get_events(
            agent_id=agent_id,
            event_type=TelemetryEventType.AGENT_SELECTED,
            start_time=start_time
        )
        selected_count = len(events)
        
        events = self.get_events(
            agent_id=agent_id,
            event_type=TelemetryEventType.AGENT_FAILED,
            start_time=start_time
        )
        failed_count = len(events)
        
        if selected_count == 0:
            return None
        
        return ((selected_count - failed_count) / selected_count) * 100
    
    def get_average_human_intervention_duration(self, workflow_id: Optional[str] = None, time_window_days: int = 7) -> Optional[float]:
        """
        Get the average duration of human interventions over a time window.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            time_window_days: The time window in days
            
        Returns:
            The average duration in milliseconds, or None if no interventions found
        """
        # Calculate start time
        start_time = datetime.now() - timedelta(days=time_window_days)
        
        # Get all human intervention completed events
        events = self.get_events(
            workflow_id=workflow_id,
            event_type=TelemetryEventType.HUMAN_INTERVENTION_COMPLETED,
            start_time=start_time
        )
        
        if not events:
            return None
        
        # Calculate average duration
        durations = [e.duration_ms for e in events if e.duration_ms is not None]
        if not durations:
            return None
        
        return sum(durations) / len(durations)
    
    def get_execution_mode_distribution(self, workflow_id: Optional[str] = None, time_window_days: int = 7) -> Dict[str, int]:
        """
        Get the distribution of execution modes over a time window.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            time_window_days: The time window in days
            
        Returns:
            A dictionary mapping execution modes to counts
        """
        # Calculate start time
        start_time = datetime.now() - timedelta(days=time_window_days)
        
        # Get all execution mode changed events
        events = self.get_events(
            workflow_id=workflow_id,
            event_type=TelemetryEventType.EXECUTION_MODE_CHANGED,
            start_time=start_time
        )
        
        # Count by to_mode
        result = defaultdict(int)
        for event in events:
            to_mode = event.metadata.get("to_mode", "unknown")
            result[to_mode] += 1
        
        return dict(result)
    
    def get_top_escalation_reasons(self, workflow_id: Optional[str] = None, time_window_days: int = 7, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top reasons for escalations over a time window.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            time_window_days: The time window in days
            limit: Maximum number of reasons to return
            
        Returns:
            A list of dictionaries with reason and count
        """
        # Calculate start time
        start_time = datetime.now() - timedelta(days=time_window_days)
        
        # Get all escalation triggered events
        events = self.get_events(
            workflow_id=workflow_id,
            event_type=TelemetryEventType.ESCALATION_TRIGGERED,
            start_time=start_time
        )
        
        # Count by reason
        reason_counts = defaultdict(int)
        for event in events:
            reason = event.metadata.get("reason", "unknown")
            reason_counts[reason] += 1
        
        # Sort by count (descending)
        sorted_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Apply limit
        sorted_reasons = sorted_reasons[:limit]
        
        return [{"reason": reason, "count": count} for reason, count in sorted_reasons]
    
    def get_trust_score_history(self, agent_id: str, time_window_days: int = 7) -> List[Dict[str, Any]]:
        """
        Get the history of trust score updates for an agent over a time window.
        
        Args:
            agent_id: The ID of the agent
            time_window_days: The time window in days
            
        Returns:
            A list of dictionaries with timestamp and trust_score
        """
        # Calculate start time
        start_time = datetime.now() - timedelta(days=time_window_days)
        
        # Get all trust score updated events
        events = self.get_events(
            agent_id=agent_id,
            event_type=TelemetryEventType.TRUST_SCORE_UPDATED,
            start_time=start_time
        )
        
        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)
        
        return [
            {
                "timestamp": event.timestamp,
                "trust_score": event.metadata.get("trust_score")
            }
            for event in events
            if event.metadata.get("trust_score") is not None
        ]
    
    def generate_workflow_performance_report(self, workflow_id: str, time_window_days: int = 7) -> Dict[str, Any]:
        """
        Generate a performance report for a workflow over a time window.
        
        Args:
            workflow_id: The ID of the workflow
            time_window_days: The time window in days
            
        Returns:
            A dictionary with performance metrics
        """
        # Calculate start time
        start_time = datetime.now() - timedelta(days=time_window_days)
        
        # Get all relevant events
        all_events = self.get_events(
            workflow_id=workflow_id,
            start_time=start_time
        )
        
        # Count executions by status
        completed_events = [e for e in all_events if e.type == TelemetryEventType.WORKFLOW_COMPLETED]
        failed_events = [e for e in all_events if e.type == TelemetryEventType.WORKFLOW_FAILED]
        cancelled_events = [e for e in all_events if e.type == TelemetryEventType.WORKFLOW_CANCELLED]
        
        total_executions = len(completed_events) + len(failed_events) + len(cancelled_events)
        success_rate = (len(completed_events) / total_executions * 100) if total_executions > 0 else 0
        
        # Calculate average duration
        durations = []
        for event in completed_events + failed_events:
            execution_id = event.execution_id
            if execution_id:
                duration = self.get_workflow_execution_duration(execution_id)
                if duration is not None:
                    durations.append(duration)
        
        avg_duration_ms = sum(durations) / len(durations) if durations else 0
        
        # Count human interventions
        human_intervention_events = [e for e in all_events if e.type == TelemetryEventType.HUMAN_INTERVENTION_REQUESTED]
        human_intervention_rate = (len(human_intervention_events) / total_executions * 100) if total_executions > 0 else 0
        
        # Count escalations
        escalation_events = [e for e in all_events if e.type == TelemetryEventType.ESCALATION_TRIGGERED]
        escalation_rate = (len(escalation_events) / total_executions * 100) if total_executions > 0 else 0
        
        # Get top escalation reasons
        top_escalation_reasons = self.get_top_escalation_reasons(workflow_id, time_window_days)
        
        # Get execution mode distribution
        execution_mode_distribution = self.get_execution_mode_distribution(workflow_id, time_window_days)
        
        return {
            "workflow_id": workflow_id,
            "time_window_days": time_window_days,
            "total_executions": total_executions,
            "completed_executions": len(completed_events),
            "failed_executions": len(failed_events),
            "cancelled_executions": len(cancelled_events),
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration_ms,
            "human_interventions": len(human_intervention_events),
            "human_intervention_rate": human_intervention_rate,
            "escalations": len(escalation_events),
            "escalation_rate": escalation_rate,
            "top_escalation_reasons": top_escalation_reasons,
            "execution_mode_distribution": execution_mode_distribution,
            "generated_at": datetime.now()
        }
    
    def cleanup_old_events(self):
        """
        Clean up events older than the retention period.
        """
        if self.retention_days <= 0:
            return
        
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        self.events = [e for e in self.events if e.timestamp >= cutoff_time]
        
        logger.info(f"Cleaned up events older than {self.retention_days} days")
    
    def export_events_to_json(self, 
                             file_path: str,
                             workflow_id: Optional[str] = None,
                             start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None):
        """
        Export events to a JSON file.
        
        Args:
            file_path: The path to save the JSON file
            workflow_id: Optional workflow ID to filter by
            start_time: Optional start time to filter by
            end_time: Optional end time to filter by
        """
        # Get filtered events
        events = self.get_events(
            workflow_id=workflow_id,
            start_time=start_time,
            end_time=end_time
        )
        
        # Convert to dict for JSON serialization
        events_dict = []
        for event in events:
            event_dict = event.dict()
            event_dict["timestamp"] = event_dict["timestamp"].isoformat()
            events_dict.append(event_dict)
        
        # Write to file
        with open(file_path, "w") as f:
            json.dump(events_dict, f, indent=2)
        
        logger.info(f"Exported {len(events)} events to {file_path}")
    
    def import_events_from_json(self, file_path: str):
        """
        Import events from a JSON file.
        
        Args:
            file_path: The path to the JSON file
        """
        try:
            with open(file_path, "r") as f:
                events_dict = json.load(f)
            
            # Convert to TelemetryEvent objects
            for event_dict in events_dict:
                # Convert timestamp string to datetime
                event_dict["timestamp"] = datetime.fromisoformat(event_dict["timestamp"])
                
                # Create event
                event = TelemetryEvent(**event_dict)
                self.events.append(event)
            
            logger.info(f"Imported {len(events_dict)} events from {file_path}")
        except Exception as e:
            logger.error(f"Failed to import events from {file_path}: {e}")
            raise ValueError(f"Failed to import events: {e}")
