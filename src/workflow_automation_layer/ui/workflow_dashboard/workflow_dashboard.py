"""
Workflow Dashboard Component for the Workflow Automation Layer.

This module implements the workflow dashboard UI component that provides a comprehensive
overview of all workflows, their status, performance metrics, and management capabilities.
It serves as the central hub for workflow monitoring and management.

Key features:
- Workflow status overview with filtering and sorting
- Performance metrics and KPIs
- Trust score visualization
- Execution mode distribution
- Agent activity monitoring
- Integration with Dynamic Agent Capsules
- Debug trace access
- Workflow management actions
"""

import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta

class WorkflowStatusCard:
    """
    Represents a workflow status card in the dashboard.
    
    A status card provides a summary of a workflow's current state.
    """
    
    def __init__(self, 
                workflow_id: str,
                name: str,
                description: str,
                status: str,
                execution_mode: str,
                last_execution: Optional[float] = None,
                trust_score: Optional[float] = None,
                metrics: Dict[str, Any] = None,
                tags: List[str] = None):
        """
        Initialize a workflow status card.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Name of the workflow
            description: Description of the workflow
            status: Current status of the workflow
            execution_mode: Current execution mode
            last_execution: Optional timestamp of the last execution
            trust_score: Optional trust score
            metrics: Optional performance metrics
            tags: Optional tags for categorization
        """
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.status = status
        self.execution_mode = execution_mode
        self.last_execution = last_execution
        self.trust_score = trust_score
        self.metrics = metrics or {}
        self.tags = tags or []
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the status card to a dictionary.
        
        Returns:
            Dictionary representation of the status card
        """
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "execution_mode": self.execution_mode,
            "last_execution": self.last_execution,
            "trust_score": self.trust_score,
            "metrics": self.metrics,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStatusCard':
        """
        Create a status card from a dictionary.
        
        Args:
            data: Dictionary representation of the status card
            
        Returns:
            WorkflowStatusCard instance
        """
        return cls(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data["description"],
            status=data["status"],
            execution_mode=data["execution_mode"],
            last_execution=data.get("last_execution"),
            trust_score=data.get("trust_score"),
            metrics=data.get("metrics", {}),
            tags=data.get("tags", [])
        )


class PerformanceMetric:
    """
    Represents a performance metric in the dashboard.
    
    A performance metric tracks a specific aspect of workflow performance.
    """
    
    def __init__(self, 
                metric_id: str,
                name: str,
                description: str,
                value: float,
                unit: str,
                timestamp: float,
                trend: List[Tuple[float, float]] = None,
                thresholds: Dict[str, float] = None):
        """
        Initialize a performance metric.
        
        Args:
            metric_id: Unique identifier for the metric
            name: Name of the metric
            description: Description of the metric
            value: Current value of the metric
            unit: Unit of measurement
            timestamp: Timestamp of the measurement
            trend: Optional list of (timestamp, value) pairs for trend analysis
            thresholds: Optional thresholds for warning and critical levels
        """
        self.metric_id = metric_id
        self.name = name
        self.description = description
        self.value = value
        self.unit = unit
        self.timestamp = timestamp
        self.trend = trend or []
        self.thresholds = thresholds or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the metric to a dictionary.
        
        Returns:
            Dictionary representation of the metric
        """
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "trend": self.trend,
            "thresholds": self.thresholds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetric':
        """
        Create a metric from a dictionary.
        
        Args:
            data: Dictionary representation of the metric
            
        Returns:
            PerformanceMetric instance
        """
        return cls(
            metric_id=data["metric_id"],
            name=data["name"],
            description=data["description"],
            value=data["value"],
            unit=data["unit"],
            timestamp=data["timestamp"],
            trend=data.get("trend", []),
            thresholds=data.get("thresholds", {})
        )
    
    def add_trend_point(self, timestamp: float, value: float):
        """
        Add a point to the trend data.
        
        Args:
            timestamp: Timestamp of the measurement
            value: Value of the measurement
        """
        self.trend.append((timestamp, value))
        
        # Limit trend data to 100 points
        if len(self.trend) > 100:
            self.trend = self.trend[-100:]
    
    def get_status(self) -> str:
        """
        Get the status of the metric based on thresholds.
        
        Returns:
            Status string: "normal", "warning", or "critical"
        """
        if "critical" in self.thresholds and self.value >= self.thresholds["critical"]:
            return "critical"
        elif "warning" in self.thresholds and self.value >= self.thresholds["warning"]:
            return "warning"
        else:
            return "normal"


class AgentActivitySummary:
    """
    Represents an agent activity summary in the dashboard.
    
    An agent activity summary provides information about an agent's activity.
    """
    
    def __init__(self, 
                agent_id: str,
                name: str,
                agent_type: str,
                status: str,
                workflows: List[str],
                tasks_completed: int,
                tasks_pending: int,
                trust_score: float,
                last_active: float):
        """
        Initialize an agent activity summary.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
            agent_type: Type of the agent
            status: Current status of the agent
            workflows: List of workflow IDs the agent is involved in
            tasks_completed: Number of tasks completed
            tasks_pending: Number of tasks pending
            trust_score: Trust score of the agent
            last_active: Timestamp of the last activity
        """
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.status = status
        self.workflows = workflows
        self.tasks_completed = tasks_completed
        self.tasks_pending = tasks_pending
        self.trust_score = trust_score
        self.last_active = last_active
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the activity summary to a dictionary.
        
        Returns:
            Dictionary representation of the activity summary
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "agent_type": self.agent_type,
            "status": self.status,
            "workflows": self.workflows,
            "tasks_completed": self.tasks_completed,
            "tasks_pending": self.tasks_pending,
            "trust_score": self.trust_score,
            "last_active": self.last_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentActivitySummary':
        """
        Create an activity summary from a dictionary.
        
        Args:
            data: Dictionary representation of the activity summary
            
        Returns:
            AgentActivitySummary instance
        """
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            agent_type=data["agent_type"],
            status=data["status"],
            workflows=data["workflows"],
            tasks_completed=data["tasks_completed"],
            tasks_pending=data["tasks_pending"],
            trust_score=data["trust_score"],
            last_active=data["last_active"]
        )


class WorkflowDashboard:
    """
    Represents the workflow dashboard UI component.
    
    The workflow dashboard provides a comprehensive overview of all workflows,
    their status, performance metrics, and management capabilities.
    """
    
    def __init__(self, dashboard_id: Optional[str] = None):
        """
        Initialize a workflow dashboard.
        
        Args:
            dashboard_id: Optional unique identifier for the dashboard
        """
        self.dashboard_id = dashboard_id or f"dashboard-{uuid.uuid4()}"
        self.workflow_cards: Dict[str, WorkflowStatusCard] = {}
        self.performance_metrics: Dict[str, PerformanceMetric] = {}
        self.agent_activities: Dict[str, AgentActivitySummary] = {}
        self.filters = {
            "status": [],
            "execution_mode": [],
            "tags": [],
            "trust_score_min": 0.0,
            "trust_score_max": 1.0
        }
        self.sort_by = "last_execution"
        self.sort_order = "desc"
        self.time_range = "day"
        self.view_mode = "grid"
        self.metadata = {
            "name": "Workflow Dashboard",
            "description": "Overview of all workflows",
            "created": time.time(),
            "modified": time.time(),
            "version": "1.0"
        }
        
    def add_workflow_card(self, card: WorkflowStatusCard):
        """
        Add a workflow status card to the dashboard.
        
        Args:
            card: Workflow status card to add
        """
        self.workflow_cards[card.workflow_id] = card
        self.metadata["modified"] = time.time()
    
    def update_workflow_card(self, workflow_id: str, updates: Dict[str, Any]) -> Optional[WorkflowStatusCard]:
        """
        Update a workflow status card.
        
        Args:
            workflow_id: ID of the workflow to update
            updates: Updates to apply to the card
            
        Returns:
            The updated card if successful, None otherwise
        """
        if workflow_id not in self.workflow_cards:
            return None
        
        card = self.workflow_cards[workflow_id]
        
        for key, value in updates.items():
            if hasattr(card, key):
                setattr(card, key, value)
        
        self.metadata["modified"] = time.time()
        
        return card
    
    def remove_workflow_card(self, workflow_id: str) -> bool:
        """
        Remove a workflow status card from the dashboard.
        
        Args:
            workflow_id: ID of the workflow to remove
            
        Returns:
            True if successful, False otherwise
        """
        if workflow_id not in self.workflow_cards:
            return False
        
        del self.workflow_cards[workflow_id]
        self.metadata["modified"] = time.time()
        
        return True
    
    def add_performance_metric(self, metric: PerformanceMetric):
        """
        Add a performance metric to the dashboard.
        
        Args:
            metric: Performance metric to add
        """
        self.performance_metrics[metric.metric_id] = metric
        self.metadata["modified"] = time.time()
    
    def update_performance_metric(self, metric_id: str, value: float, timestamp: Optional[float] = None) -> Optional[PerformanceMetric]:
        """
        Update a performance metric.
        
        Args:
            metric_id: ID of the metric to update
            value: New value for the metric
            timestamp: Optional timestamp for the update
            
        Returns:
            The updated metric if successful, None otherwise
        """
        if metric_id not in self.performance_metrics:
            return None
        
        metric = self.performance_metrics[metric_id]
        timestamp = timestamp or time.time()
        
        # Update the metric
        metric.value = value
        metric.timestamp = timestamp
        
        # Add to trend data
        metric.add_trend_point(timestamp, value)
        
        self.metadata["modified"] = time.time()
        
        return metric
    
    def remove_performance_metric(self, metric_id: str) -> bool:
        """
        Remove a performance metric from the dashboard.
        
        Args:
            metric_id: ID of the metric to remove
            
        Returns:
            True if successful, False otherwise
        """
        if metric_id not in self.performance_metrics:
            return False
        
        del self.performance_metrics[metric_id]
        self.metadata["modified"] = time.time()
        
        return True
    
    def add_agent_activity(self, activity: AgentActivitySummary):
        """
        Add an agent activity summary to the dashboard.
        
        Args:
            activity: Agent activity summary to add
        """
        self.agent_activities[activity.agent_id] = activity
        self.metadata["modified"] = time.time()
    
    def update_agent_activity(self, agent_id: str, updates: Dict[str, Any]) -> Optional[AgentActivitySummary]:
        """
        Update an agent activity summary.
        
        Args:
            agent_id: ID of the agent to update
            updates: Updates to apply to the activity summary
            
        Returns:
            The updated activity summary if successful, None otherwise
        """
        if agent_id not in self.agent_activities:
            return None
        
        activity = self.agent_activities[agent_id]
        
        for key, value in updates.items():
            if hasattr(activity, key):
                setattr(activity, key, value)
        
        self.metadata["modified"] = time.time()
        
        return activity
    
    def remove_agent_activity(self, agent_id: str) -> bool:
        """
        Remove an agent activity summary from the dashboard.
        
        Args:
            agent_id: ID of the agent to remove
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agent_activities:
            return False
        
        del self.agent_activities[agent_id]
        self.metadata["modified"] = time.time()
        
        return True
    
    def set_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set the dashboard filters.
        
        Args:
            filters: New filter settings
            
        Returns:
            The updated filters
        """
        self.filters.update(filters)
        self.metadata["modified"] = time.time()
        
        return self.filters
    
    def set_sort(self, sort_by: str, sort_order: str = "desc") -> Dict[str, str]:
        """
        Set the dashboard sorting.
        
        Args:
            sort_by: Field to sort by
            sort_order: Sort order ("asc" or "desc")
            
        Returns:
            The updated sorting settings
        """
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.metadata["modified"] = time.time()
        
        return {
            "sort_by": self.sort_by,
            "sort_order": self.sort_order
        }
    
    def set_time_range(self, time_range: str) -> str:
        """
        Set the dashboard time range.
        
        Args:
            time_range: Time range ("hour", "day", "week", "month", "year", "all")
            
        Returns:
            The updated time range
        """
        self.time_range = time_range
        self.metadata["modified"] = time.time()
        
        return self.time_range
    
    def set_view_mode(self, view_mode: str) -> str:
        """
        Set the dashboard view mode.
        
        Args:
            view_mode: View mode ("grid", "list", "table")
            
        Returns:
            The updated view mode
        """
        self.view_mode = view_mode
        self.metadata["modified"] = time.time()
        
        return self.view_mode
    
    def get_filtered_workflows(self) -> List[WorkflowStatusCard]:
        """
        Get workflows filtered by the current filters.
        
        Returns:
            List of filtered workflow status cards
        """
        filtered = list(self.workflow_cards.values())
        
        # Apply status filter
        if self.filters["status"]:
            filtered = [card for card in filtered if card.status in self.filters["status"]]
        
        # Apply execution mode filter
        if self.filters["execution_mode"]:
            filtered = [card for card in filtered if card.execution_mode in self.filters["execution_mode"]]
        
        # Apply tags filter
        if self.filters["tags"]:
            filtered = [card for card in filtered if any(tag in card.tags for tag in self.filters["tags"])]
        
        # Apply trust score filter
        filtered = [card for card in filtered if card.trust_score is None or 
                   (self.filters["trust_score_min"] <= card.trust_score <= self.filters["trust_score_max"])]
        
        # Apply sorting
        reverse = self.sort_order == "desc"
        
        if self.sort_by == "name":
            filtered.sort(key=lambda card: card.name, reverse=reverse)
        elif self.sort_by == "status":
            filtered.sort(key=lambda card: card.status, reverse=reverse)
        elif self.sort_by == "execution_mode":
            filtered.sort(key=lambda card: card.execution_mode, reverse=reverse)
        elif self.sort_by == "last_execution":
            filtered.sort(key=lambda card: card.last_execution or 0, reverse=reverse)
        elif self.sort_by == "trust_score":
            filtered.sort(key=lambda card: card.trust_score or 0, reverse=reverse)
        
        return filtered
    
    def get_time_filtered_metrics(self) -> Dict[str, PerformanceMetric]:
        """
        Get metrics filtered by the current time range.
        
        Returns:
            Dictionary of filtered performance metrics
        """
        now = time.time()
        
        if self.time_range == "hour":
            cutoff = now - 3600
        elif self.time_range == "day":
            cutoff = now - 86400
        elif self.time_range == "week":
            cutoff = now - 604800
        elif self.time_range == "month":
            cutoff = now - 2592000
        elif self.time_range == "year":
            cutoff = now - 31536000
        else:  # "all"
            return self.performance_metrics
        
        # Filter metrics by timestamp
        filtered = {}
        
        for metric_id, metric in self.performance_metrics.items():
            if metric.timestamp >= cutoff:
                # Also filter trend data
                filtered_trend = [(ts, val) for ts, val in metric.trend if ts >= cutoff]
                
                # Create a copy of the metric with filtered trend
                filtered_metric = PerformanceMetric(
                    metric_id=metric.metric_id,
                    name=metric.name,
                    description=metric.description,
                    value=metric.value,
                    unit=metric.unit,
                    timestamp=metric.timestamp,
                    trend=filtered_trend,
                    thresholds=metric.thresholds
                )
                
                filtered[metric_id] = filtered_metric
        
        return filtered
    
    def get_active_agents(self) -> List[AgentActivitySummary]:
        """
        Get active agents sorted by last activity.
        
        Returns:
            List of active agent activity summaries
        """
        active = [activity for activity in self.agent_activities.values() 
                 if activity.status == "active"]
        
        # Sort by last active time (descending)
        active.sort(key=lambda activity: activity.last_active, reverse=True)
        
        return active
    
    def get_execution_mode_distribution(self) -> Dict[str, int]:
        """
        Get the distribution of execution modes.
        
        Returns:
            Dictionary mapping execution modes to counts
        """
        distribution = {
            "autonomous": 0,
            "supervised": 0,
            "collaborative": 0,
            "assistive": 0,
            "manual": 0
        }
        
        for card in self.workflow_cards.values():
            if card.execution_mode in distribution:
                distribution[card.execution_mode] += 1
        
        return distribution
    
    def get_trust_score_distribution(self) -> Dict[str, int]:
        """
        Get the distribution of trust scores.
        
        Returns:
            Dictionary mapping trust score ranges to counts
        """
        distribution = {
            "very_high": 0,  # 0.9 - 1.0
            "high": 0,       # 0.7 - 0.9
            "medium": 0,     # 0.5 - 0.7
            "low": 0,        # 0.3 - 0.5
            "very_low": 0    # 0.0 - 0.3
        }
        
        for card in self.workflow_cards.values():
            if card.trust_score is not None:
                if card.trust_score >= 0.9:
                    distribution["very_high"] += 1
                elif card.trust_score >= 0.7:
                    distribution["high"] += 1
                elif card.trust_score >= 0.5:
                    distribution["medium"] += 1
                elif card.trust_score >= 0.3:
                    distribution["low"] += 1
                else:
                    distribution["very_low"] += 1
        
        return distribution
    
    def get_status_distribution(self) -> Dict[str, int]:
        """
        Get the distribution of workflow statuses.
        
        Returns:
            Dictionary mapping statuses to counts
        """
        distribution = {
            "not_started": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "stopped": 0
        }
        
        for card in self.workflow_cards.values():
            if card.status in distribution:
                distribution[card.status] += 1
        
        return distribution
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dashboard to a dictionary.
        
        Returns:
            Dictionary representation of the dashboard
        """
        return {
            "dashboard_id": self.dashboard_id,
            "workflow_cards": {wf_id: card.to_dict() for wf_id, card in self.workflow_cards.items()},
            "performance_metrics": {m_id: metric.to_dict() for m_id, metric in self.performance_metrics.items()},
            "agent_activities": {a_id: activity.to_dict() for a_id, activity in self.agent_activities.items()},
            "filters": self.filters,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order,
            "time_range": self.time_range,
            "view_mode": self.view_mode,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowDashboard':
        """
        Create a dashboard from a dictionary.
        
        Args:
            data: Dictionary representation of the dashboard
            
        Returns:
            WorkflowDashboard instance
        """
        dashboard = cls(dashboard_id=data.get("dashboard_id"))
        
        # Set metadata
        if "metadata" in data:
            dashboard.metadata = data["metadata"]
        
        # Set filters and sorting
        if "filters" in data:
            dashboard.filters = data["filters"]
        
        if "sort_by" in data:
            dashboard.sort_by = data["sort_by"]
        
        if "sort_order" in data:
            dashboard.sort_order = data["sort_order"]
        
        if "time_range" in data:
            dashboard.time_range = data["time_range"]
        
        if "view_mode" in data:
            dashboard.view_mode = data["view_mode"]
        
        # Add workflow cards
        for wf_id, card_data in data.get("workflow_cards", {}).items():
            dashboard.workflow_cards[wf_id] = WorkflowStatusCard.from_dict(card_data)
        
        # Add performance metrics
        for m_id, metric_data in data.get("performance_metrics", {}).items():
            dashboard.performance_metrics[m_id] = PerformanceMetric.from_dict(metric_data)
        
        # Add agent activities
        for a_id, activity_data in data.get("agent_activities", {}).items():
            dashboard.agent_activities[a_id] = AgentActivitySummary.from_dict(activity_data)
        
        return dashboard


class WorkflowDashboardManager:
    """
    Manages workflow dashboards for the Workflow Automation Layer.
    
    This class provides methods for creating, managing, and persisting
    workflow dashboards.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the Workflow Dashboard Manager.
        
        Args:
            storage_path: Optional path for storing dashboards
        """
        self.storage_path = storage_path or "/data/workflow_dashboards"
        self.dashboards: Dict[str, WorkflowDashboard] = {}
        self._load_dashboards()
        
    def _load_dashboards(self):
        """Load dashboards from persistent storage."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.storage_path, filename), 'r') as f:
                        dashboard_data = json.load(f)
                        dashboard = WorkflowDashboard.from_dict(dashboard_data)
                        self.dashboards[dashboard.dashboard_id] = dashboard
                except Exception as e:
                    print(f"Error loading dashboard {filename}: {e}")
    
    def _store_dashboard(self, dashboard: WorkflowDashboard):
        """
        Store a dashboard to persistent storage.
        
        Args:
            dashboard: The dashboard to store
        """
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
        
        file_path = os.path.join(self.storage_path, f"{dashboard.dashboard_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(dashboard.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error storing dashboard: {e}")
    
    def create_dashboard(self, 
                        name: str = "Workflow Dashboard",
                        description: str = "",
                        dashboard_id: Optional[str] = None) -> WorkflowDashboard:
        """
        Create a new workflow dashboard.
        
        Args:
            name: Name for the dashboard
            description: Description for the dashboard
            dashboard_id: Optional unique identifier for the dashboard
            
        Returns:
            The created dashboard
        """
        dashboard = WorkflowDashboard(dashboard_id=dashboard_id)
        dashboard.metadata["name"] = name
        dashboard.metadata["description"] = description
        
        self.dashboards[dashboard.dashboard_id] = dashboard
        self._store_dashboard(dashboard)
        
        return dashboard
    
    def get_dashboard(self, dashboard_id: str) -> Optional[WorkflowDashboard]:
        """
        Get a dashboard by its identifier.
        
        Args:
            dashboard_id: Identifier for the dashboard
            
        Returns:
            The dashboard if found, None otherwise
        """
        return self.dashboards.get(dashboard_id)
    
    def list_dashboards(self) -> List[Dict[str, Any]]:
        """
        List all available dashboards.
        
        Returns:
            List of dashboard metadata
        """
        return [
            {
                "id": dashboard.dashboard_id,
                "name": dashboard.metadata.get("name", "Workflow Dashboard"),
                "description": dashboard.metadata.get("description", ""),
                "created": dashboard.metadata.get("created", 0),
                "modified": dashboard.metadata.get("modified", 0),
                "version": dashboard.metadata.get("version", "1.0"),
                "workflow_count": len(dashboard.workflow_cards)
            }
            for dashboard in self.dashboards.values()
        ]
    
    def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> Optional[WorkflowDashboard]:
        """
        Update a dashboard.
        
        Args:
            dashboard_id: Identifier for the dashboard
            updates: Updates to apply to the dashboard
            
        Returns:
            The updated dashboard if successful, None otherwise
        """
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return None
        
        # Apply updates
        if "metadata" in updates:
            dashboard.metadata.update(updates["metadata"])
            dashboard.metadata["modified"] = time.time()
        
        if "filters" in updates:
            dashboard.set_filters(updates["filters"])
        
        if "sort" in updates:
            sort_by = updates["sort"].get("sort_by", dashboard.sort_by)
            sort_order = updates["sort"].get("sort_order", dashboard.sort_order)
            dashboard.set_sort(sort_by, sort_order)
        
        if "time_range" in updates:
            dashboard.set_time_range(updates["time_range"])
        
        if "view_mode" in updates:
            dashboard.set_view_mode(updates["view_mode"])
        
        # Add/update workflow cards
        if "workflow_cards" in updates:
            for card_data in updates["workflow_cards"]:
                if "workflow_id" in card_data and card_data["workflow_id"] in dashboard.workflow_cards:
                    # Update existing card
                    dashboard.update_workflow_card(card_data["workflow_id"], card_data)
                else:
                    # Add new card
                    card = WorkflowStatusCard(
                        workflow_id=card_data.get("workflow_id", f"workflow-{uuid.uuid4()}"),
                        name=card_data.get("name", "Unnamed Workflow"),
                        description=card_data.get("description", ""),
                        status=card_data.get("status", "not_started"),
                        execution_mode=card_data.get("execution_mode", "manual"),
                        last_execution=card_data.get("last_execution"),
                        trust_score=card_data.get("trust_score"),
                        metrics=card_data.get("metrics", {}),
                        tags=card_data.get("tags", [])
                    )
                    dashboard.add_workflow_card(card)
        
        # Add/update performance metrics
        if "performance_metrics" in updates:
            for metric_data in updates["performance_metrics"]:
                if "metric_id" in metric_data and metric_data["metric_id"] in dashboard.performance_metrics:
                    # Update existing metric
                    dashboard.update_performance_metric(
                        metric_id=metric_data["metric_id"],
                        value=metric_data.get("value", 0),
                        timestamp=metric_data.get("timestamp")
                    )
                else:
                    # Add new metric
                    metric = PerformanceMetric(
                        metric_id=metric_data.get("metric_id", f"metric-{uuid.uuid4()}"),
                        name=metric_data.get("name", "Unnamed Metric"),
                        description=metric_data.get("description", ""),
                        value=metric_data.get("value", 0),
                        unit=metric_data.get("unit", ""),
                        timestamp=metric_data.get("timestamp", time.time()),
                        trend=metric_data.get("trend", []),
                        thresholds=metric_data.get("thresholds", {})
                    )
                    dashboard.add_performance_metric(metric)
        
        # Add/update agent activities
        if "agent_activities" in updates:
            for activity_data in updates["agent_activities"]:
                if "agent_id" in activity_data and activity_data["agent_id"] in dashboard.agent_activities:
                    # Update existing activity
                    dashboard.update_agent_activity(activity_data["agent_id"], activity_data)
                else:
                    # Add new activity
                    activity = AgentActivitySummary(
                        agent_id=activity_data.get("agent_id", f"agent-{uuid.uuid4()}"),
                        name=activity_data.get("name", "Unnamed Agent"),
                        agent_type=activity_data.get("agent_type", "generic"),
                        status=activity_data.get("status", "inactive"),
                        workflows=activity_data.get("workflows", []),
                        tasks_completed=activity_data.get("tasks_completed", 0),
                        tasks_pending=activity_data.get("tasks_pending", 0),
                        trust_score=activity_data.get("trust_score", 0.5),
                        last_active=activity_data.get("last_active", time.time())
                    )
                    dashboard.add_agent_activity(activity)
        
        # Remove workflow cards
        if "remove_workflow_cards" in updates:
            for workflow_id in updates["remove_workflow_cards"]:
                dashboard.remove_workflow_card(workflow_id)
        
        # Remove performance metrics
        if "remove_performance_metrics" in updates:
            for metric_id in updates["remove_performance_metrics"]:
                dashboard.remove_performance_metric(metric_id)
        
        # Remove agent activities
        if "remove_agent_activities" in updates:
            for agent_id in updates["remove_agent_activities"]:
                dashboard.remove_agent_activity(agent_id)
        
        # Store the updated dashboard
        self._store_dashboard(dashboard)
        
        return dashboard
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """
        Delete a dashboard.
        
        Args:
            dashboard_id: Identifier for the dashboard
            
        Returns:
            True if successful, False otherwise
        """
        if dashboard_id not in self.dashboards:
            return False
        
        # Remove from memory
        del self.dashboards[dashboard_id]
        
        # Remove from storage
        file_path = os.path.join(self.storage_path, f"{dashboard_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting dashboard: {e}")
            return False


class WorkflowDashboardService:
    """
    Service for integrating the workflow dashboard with the Workflow Automation Layer.
    
    This class provides methods for updating the dashboard with workflow execution
    data and handling user interactions.
    """
    
    def __init__(self, dashboard_manager: WorkflowDashboardManager):
        """
        Initialize the Workflow Dashboard Service.
        
        Args:
            dashboard_manager: Workflow Dashboard Manager instance
        """
        self.dashboard_manager = dashboard_manager
        self.update_callbacks: Dict[str, List[Callable]] = {}
        
    def register_update_callback(self, dashboard_id: str, callback: Callable):
        """
        Register a callback for dashboard updates.
        
        Args:
            dashboard_id: Identifier for the dashboard
            callback: Callback function
        """
        if dashboard_id not in self.update_callbacks:
            self.update_callbacks[dashboard_id] = []
            
        self.update_callbacks[dashboard_id].append(callback)
    
    def unregister_update_callback(self, dashboard_id: str, callback: Callable) -> bool:
        """
        Unregister a callback for dashboard updates.
        
        Args:
            dashboard_id: Identifier for the dashboard
            callback: Callback function
            
        Returns:
            True if successful, False otherwise
        """
        if dashboard_id not in self.update_callbacks:
            return False
        
        if callback in self.update_callbacks[dashboard_id]:
            self.update_callbacks[dashboard_id].remove(callback)
            return True
        
        return False
    
    def notify_update(self, 
                     dashboard_id: str,
                     update_type: str,
                     update_data: Dict[str, Any]):
        """
        Notify update callbacks of a dashboard update.
        
        Args:
            dashboard_id: Identifier for the dashboard
            update_type: Type of the update
            update_data: Update data
        """
        if dashboard_id in self.update_callbacks:
            for callback in self.update_callbacks[dashboard_id]:
                try:
                    callback(update_type, update_data)
                except Exception as e:
                    print(f"Error in update callback: {e}")
    
    def update_workflow_status(self, 
                              dashboard_id: str,
                              workflow_id: str,
                              status: str,
                              execution_mode: Optional[str] = None,
                              last_execution: Optional[float] = None,
                              trust_score: Optional[float] = None,
                              metrics: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update the status of a workflow in the dashboard.
        
        Args:
            dashboard_id: Identifier for the dashboard
            workflow_id: Identifier for the workflow
            status: New status for the workflow
            execution_mode: Optional new execution mode
            last_execution: Optional timestamp of the last execution
            trust_score: Optional new trust score
            metrics: Optional new performance metrics
            
        Returns:
            True if successful, False otherwise
        """
        dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            return False
        
        # Prepare updates
        updates = {"status": status}
        
        if execution_mode is not None:
            updates["execution_mode"] = execution_mode
            
        if last_execution is not None:
            updates["last_execution"] = last_execution
            
        if trust_score is not None:
            updates["trust_score"] = trust_score
            
        if metrics is not None:
            updates["metrics"] = metrics
        
        # Update the workflow card
        if workflow_id in dashboard.workflow_cards:
            # Update existing card
            dashboard.update_workflow_card(workflow_id, updates)
        else:
            # Create new card with minimal information
            card = WorkflowStatusCard(
                workflow_id=workflow_id,
                name=f"Workflow {workflow_id}",
                description="",
                status=status,
                execution_mode=execution_mode or "manual",
                last_execution=last_execution,
                trust_score=trust_score,
                metrics=metrics or {}
            )
            dashboard.add_workflow_card(card)
        
        # Store the updated dashboard
        self.dashboard_manager._store_dashboard(dashboard)
        
        # Notify update
        self.notify_update(
            dashboard_id=dashboard_id,
            update_type="workflow_status",
            update_data={
                "workflow_id": workflow_id,
                "status": status,
                "execution_mode": execution_mode,
                "last_execution": last_execution,
                "trust_score": trust_score,
                "metrics": metrics
            }
        )
        
        return True
    
    def update_performance_metrics(self, 
                                 dashboard_id: str,
                                 metrics_updates: List[Dict[str, Any]]) -> bool:
        """
        Update performance metrics in the dashboard.
        
        Args:
            dashboard_id: Identifier for the dashboard
            metrics_updates: List of metric updates
            
        Returns:
            True if successful, False otherwise
        """
        dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            return False
        
        for update in metrics_updates:
            metric_id = update.get("metric_id")
            value = update.get("value")
            
            if metric_id and value is not None:
                if metric_id in dashboard.performance_metrics:
                    # Update existing metric
                    dashboard.update_performance_metric(
                        metric_id=metric_id,
                        value=value,
                        timestamp=update.get("timestamp")
                    )
                else:
                    # Create new metric
                    metric = PerformanceMetric(
                        metric_id=metric_id,
                        name=update.get("name", f"Metric {metric_id}"),
                        description=update.get("description", ""),
                        value=value,
                        unit=update.get("unit", ""),
                        timestamp=update.get("timestamp", time.time()),
                        thresholds=update.get("thresholds", {})
                    )
                    dashboard.add_performance_metric(metric)
        
        # Store the updated dashboard
        self.dashboard_manager._store_dashboard(dashboard)
        
        # Notify update
        self.notify_update(
            dashboard_id=dashboard_id,
            update_type="performance_metrics",
            update_data={
                "updates": metrics_updates
            }
        )
        
        return True
    
    def update_agent_activities(self, 
                              dashboard_id: str,
                              activities_updates: List[Dict[str, Any]]) -> bool:
        """
        Update agent activities in the dashboard.
        
        Args:
            dashboard_id: Identifier for the dashboard
            activities_updates: List of activity updates
            
        Returns:
            True if successful, False otherwise
        """
        dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            return False
        
        for update in activities_updates:
            agent_id = update.get("agent_id")
            
            if agent_id:
                if agent_id in dashboard.agent_activities:
                    # Update existing activity
                    dashboard.update_agent_activity(agent_id, update)
                else:
                    # Create new activity
                    activity = AgentActivitySummary(
                        agent_id=agent_id,
                        name=update.get("name", f"Agent {agent_id}"),
                        agent_type=update.get("agent_type", "generic"),
                        status=update.get("status", "inactive"),
                        workflows=update.get("workflows", []),
                        tasks_completed=update.get("tasks_completed", 0),
                        tasks_pending=update.get("tasks_pending", 0),
                        trust_score=update.get("trust_score", 0.5),
                        last_active=update.get("last_active", time.time())
                    )
                    dashboard.add_agent_activity(activity)
        
        # Store the updated dashboard
        self.dashboard_manager._store_dashboard(dashboard)
        
        # Notify update
        self.notify_update(
            dashboard_id=dashboard_id,
            update_type="agent_activities",
            update_data={
                "updates": activities_updates
            }
        )
        
        return True
    
    def handle_user_interaction(self, 
                              dashboard_id: str,
                              interaction_type: str,
                              interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user interaction with the dashboard.
        
        Args:
            dashboard_id: Identifier for the dashboard
            interaction_type: Type of the interaction
            interaction_data: Interaction data
            
        Returns:
            Response data
        """
        dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            return {"success": False, "error": "Dashboard not found"}
        
        if interaction_type == "set_filters":
            filters = interaction_data.get("filters", {})
            
            updated_filters = dashboard.set_filters(filters)
            self.dashboard_manager._store_dashboard(dashboard)
            
            return {
                "success": True,
                "filters": updated_filters
            }
            
        elif interaction_type == "set_sort":
            sort_by = interaction_data.get("sort_by")
            sort_order = interaction_data.get("sort_order", "desc")
            
            if sort_by:
                updated_sort = dashboard.set_sort(sort_by, sort_order)
                self.dashboard_manager._store_dashboard(dashboard)
                
                return {
                    "success": True,
                    "sort": updated_sort
                }
            else:
                return {
                    "success": False,
                    "error": "Missing sort_by parameter"
                }
                
        elif interaction_type == "set_time_range":
            time_range = interaction_data.get("time_range")
            
            if time_range:
                updated_time_range = dashboard.set_time_range(time_range)
                self.dashboard_manager._store_dashboard(dashboard)
                
                return {
                    "success": True,
                    "time_range": updated_time_range
                }
            else:
                return {
                    "success": False,
                    "error": "Missing time_range parameter"
                }
                
        elif interaction_type == "set_view_mode":
            view_mode = interaction_data.get("view_mode")
            
            if view_mode:
                updated_view_mode = dashboard.set_view_mode(view_mode)
                self.dashboard_manager._store_dashboard(dashboard)
                
                return {
                    "success": True,
                    "view_mode": updated_view_mode
                }
            else:
                return {
                    "success": False,
                    "error": "Missing view_mode parameter"
                }
                
        elif interaction_type == "get_filtered_workflows":
            filtered_workflows = dashboard.get_filtered_workflows()
            
            return {
                "success": True,
                "workflows": [card.to_dict() for card in filtered_workflows]
            }
            
        elif interaction_type == "get_time_filtered_metrics":
            filtered_metrics = dashboard.get_time_filtered_metrics()
            
            return {
                "success": True,
                "metrics": {m_id: metric.to_dict() for m_id, metric in filtered_metrics.items()}
            }
            
        elif interaction_type == "get_active_agents":
            active_agents = dashboard.get_active_agents()
            
            return {
                "success": True,
                "agents": [activity.to_dict() for activity in active_agents]
            }
            
        elif interaction_type == "get_distributions":
            execution_mode_distribution = dashboard.get_execution_mode_distribution()
            trust_score_distribution = dashboard.get_trust_score_distribution()
            status_distribution = dashboard.get_status_distribution()
            
            return {
                "success": True,
                "distributions": {
                    "execution_mode": execution_mode_distribution,
                    "trust_score": trust_score_distribution,
                    "status": status_distribution
                }
            }
            
        else:
            return {
                "success": False,
                "error": f"Unknown interaction type: {interaction_type}"
            }


# Example usage
if __name__ == "__main__":
    # Initialize the dashboard manager
    dashboard_manager = WorkflowDashboardManager()
    
    # Create a dashboard
    dashboard = dashboard_manager.create_dashboard(
        name="Example Dashboard",
        description="An example dashboard for testing"
    )
    
    # Add some workflow cards
    dashboard.add_workflow_card(WorkflowStatusCard(
        workflow_id="workflow-1",
        name="Example Workflow 1",
        description="An example workflow",
        status="running",
        execution_mode="autonomous",
        last_execution=time.time(),
        trust_score=0.85,
        metrics={
            "execution_time": 1250,
            "success_rate": 0.95
        },
        tags=["example", "test"]
    ))
    
    dashboard.add_workflow_card(WorkflowStatusCard(
        workflow_id="workflow-2",
        name="Example Workflow 2",
        description="Another example workflow",
        status="completed",
        execution_mode="supervised",
        last_execution=time.time() - 3600,
        trust_score=0.75,
        metrics={
            "execution_time": 2500,
            "success_rate": 0.85
        },
        tags=["example", "production"]
    ))
    
    # Add some performance metrics
    dashboard.add_performance_metric(PerformanceMetric(
        metric_id="metric-1",
        name="Average Execution Time",
        description="Average execution time of workflows",
        value=1875,
        unit="ms",
        timestamp=time.time(),
        trend=[(time.time() - i * 3600, 1800 + i * 50) for i in range(10)],
        thresholds={
            "warning": 2000,
            "critical": 3000
        }
    ))
    
    dashboard.add_performance_metric(PerformanceMetric(
        metric_id="metric-2",
        name="Success Rate",
        description="Success rate of workflows",
        value=0.9,
        unit="%",
        timestamp=time.time(),
        trend=[(time.time() - i * 3600, 0.9 - i * 0.01) for i in range(10)],
        thresholds={
            "warning": 0.8,
            "critical": 0.7
        }
    ))
    
    # Add some agent activities
    dashboard.add_agent_activity(AgentActivitySummary(
        agent_id="agent-1",
        name="Workflow Trigger Agent",
        agent_type="trigger",
        status="active",
        workflows=["workflow-1", "workflow-2"],
        tasks_completed=15,
        tasks_pending=2,
        trust_score=0.9,
        last_active=time.time()
    ))
    
    dashboard.add_agent_activity(AgentActivitySummary(
        agent_id="agent-2",
        name="Human Intervention Agent",
        agent_type="intervention",
        status="active",
        workflows=["workflow-1"],
        tasks_completed=5,
        tasks_pending=1,
        trust_score=0.95,
        last_active=time.time() - 600
    ))
    
    # Initialize the dashboard service
    dashboard_service = WorkflowDashboardService(dashboard_manager)
    
    # Register an update callback
    def update_callback(update_type, update_data):
        print(f"Dashboard update: {update_type}")
        print(f"Update data: {update_data}")
    
    dashboard_service.register_update_callback(dashboard.dashboard_id, update_callback)
    
    # Update workflow status
    dashboard_service.update_workflow_status(
        dashboard_id=dashboard.dashboard_id,
        workflow_id="workflow-1",
        status="completed",
        trust_score=0.9,
        last_execution=time.time()
    )
    
    # Update performance metrics
    dashboard_service.update_performance_metrics(
        dashboard_id=dashboard.dashboard_id,
        metrics_updates=[
            {
                "metric_id": "metric-1",
                "value": 1750,
                "timestamp": time.time()
            },
            {
                "metric_id": "metric-2",
                "value": 0.92,
                "timestamp": time.time()
            }
        ]
    )
    
    # Handle user interaction
    response = dashboard_service.handle_user_interaction(
        dashboard_id=dashboard.dashboard_id,
        interaction_type="get_distributions",
        interaction_data={}
    )
    
    print(f"Distributions: {response['distributions']}")
"""
