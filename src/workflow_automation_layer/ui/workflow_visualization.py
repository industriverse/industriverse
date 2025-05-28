"""
Workflow Visualization Module for the Workflow Automation Layer

This module provides visualization components for workflows, including:
- Workflow graph visualization
- Task status visualization
- Execution path tracing
- Performance metrics visualization
- Trust and confidence score visualization

The visualizations are designed to be embedded in web interfaces and
support the Dynamic Agent Capsules UI paradigm.
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualizationType(Enum):
    """Enum representing types of workflow visualizations."""
    GRAPH = "graph"
    TIMELINE = "timeline"
    METRICS = "metrics"
    HEATMAP = "heatmap"
    TRUST_CONFIDENCE = "trust_confidence"
    DEBUG_TRACE = "debug_trace"


class LayoutType(Enum):
    """Enum representing layout types for workflow graph visualization."""
    HIERARCHICAL = "hierarchical"
    FORCE_DIRECTED = "force_directed"
    RADIAL = "radial"
    SWIMLANE = "swimlane"
    GRID = "grid"


@dataclass
class VisualizationTheme:
    """Theme configuration for visualizations."""
    primary_color: str = "#3498db"
    secondary_color: str = "#2980b9"
    accent_color: str = "#e74c3c"
    success_color: str = "#2ecc71"
    warning_color: str = "#f39c12"
    error_color: str = "#e74c3c"
    neutral_color: str = "#95a5a6"
    background_color: str = "#ffffff"
    text_color: str = "#2c3e50"
    font_family: str = "Inter, system-ui, sans-serif"
    border_radius: str = "8px"
    animation_duration: str = "0.3s"
    shadow: str = "0 4px 6px rgba(0, 0, 0, 0.1)"


@dataclass
class NodeStyle:
    """Style configuration for workflow graph nodes."""
    shape: str = "rounded-rect"
    width: int = 180
    height: int = 80
    border_width: int = 2
    border_color: str = "#95a5a6"
    fill_color: str = "#ffffff"
    text_color: str = "#2c3e50"
    font_size: int = 14
    icon: Optional[str] = None
    shadow: bool = True
    animation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "shape": self.shape,
            "width": self.width,
            "height": self.height,
            "borderWidth": self.border_width,
            "borderColor": self.border_color,
            "fillColor": self.fill_color,
            "textColor": self.text_color,
            "fontSize": self.font_size,
            "icon": self.icon,
            "shadow": self.shadow,
            "animation": self.animation
        }


@dataclass
class EdgeStyle:
    """Style configuration for workflow graph edges."""
    line_type: str = "straight"  # straight, curved, orthogonal
    width: int = 2
    color: str = "#95a5a6"
    arrow_size: int = 10
    dashed: bool = False
    animation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lineType": self.line_type,
            "width": self.width,
            "color": self.color,
            "arrowSize": self.arrow_size,
            "dashed": self.dashed,
            "animation": self.animation
        }


class WorkflowGraphVisualizer:
    """
    Class for visualizing workflow graphs.
    
    This class provides methods for creating interactive visualizations
    of workflow graphs, showing task dependencies, execution paths,
    and current status.
    """
    
    def __init__(
        self,
        workflow_id: str,
        layout_type: LayoutType = LayoutType.HIERARCHICAL,
        theme: Optional[VisualizationTheme] = None
    ):
        """
        Initialize a new WorkflowGraphVisualizer.
        
        Args:
            workflow_id: ID of the workflow to visualize
            layout_type: Type of layout for the graph
            theme: Theme configuration for the visualization
        """
        self.workflow_id = workflow_id
        self.layout_type = layout_type
        self.theme = theme or VisualizationTheme()
        self.nodes = []
        self.edges = []
        self.node_styles = {}
        self.edge_styles = {}
        self.current_task_id = None
        self.completed_task_ids = []
        self.failed_task_ids = []
        self.waiting_task_ids = []
        
        logger.info(f"Initialized WorkflowGraphVisualizer for workflow {workflow_id}")
    
    def add_node(
        self,
        node_id: str,
        label: str,
        data: Dict[str, Any] = None,
        style: Optional[NodeStyle] = None
    ) -> None:
        """
        Add a node to the workflow graph.
        
        Args:
            node_id: Unique identifier for the node
            label: Display label for the node
            data: Additional data to associate with the node
            style: Style configuration for the node
        """
        self.nodes.append({
            "id": node_id,
            "label": label,
            "data": data or {}
        })
        
        if style:
            self.node_styles[node_id] = style
        
        logger.debug(f"Added node {node_id} to workflow graph")
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        label: Optional[str] = None,
        data: Dict[str, Any] = None,
        style: Optional[EdgeStyle] = None
    ) -> None:
        """
        Add an edge to the workflow graph.
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            label: Optional label for the edge
            data: Additional data to associate with the edge
            style: Style configuration for the edge
        """
        edge_id = f"{source_id}-{target_id}"
        
        self.edges.append({
            "id": edge_id,
            "source": source_id,
            "target": target_id,
            "label": label,
            "data": data or {}
        })
        
        if style:
            self.edge_styles[edge_id] = style
        
        logger.debug(f"Added edge {edge_id} to workflow graph")
    
    def update_node_status(
        self,
        node_id: str,
        status: str,
        progress: Optional[float] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update the status of a node in the workflow graph.
        
        Args:
            node_id: ID of the node to update
            status: New status of the node (e.g., "active", "completed", "failed")
            progress: Optional progress value (0-1)
            metrics: Optional metrics data to associate with the node
        """
        for node in self.nodes:
            if node["id"] == node_id:
                node["data"]["status"] = status
                
                if progress is not None:
                    node["data"]["progress"] = progress
                
                if metrics:
                    node["data"]["metrics"] = metrics
                
                # Update tracking lists
                if status == "active":
                    self.current_task_id = node_id
                elif status == "completed":
                    self.completed_task_ids.append(node_id)
                    if node_id == self.current_task_id:
                        self.current_task_id = None
                elif status == "failed":
                    self.failed_task_ids.append(node_id)
                    if node_id == self.current_task_id:
                        self.current_task_id = None
                elif status == "waiting":
                    self.waiting_task_ids.append(node_id)
                
                # Update node style based on status
                style = self.node_styles.get(node_id, NodeStyle())
                
                if status == "active":
                    style.border_color = self.theme.accent_color
                    style.border_width = 3
                    style.animation = "pulse"
                elif status == "completed":
                    style.border_color = self.theme.success_color
                    style.fill_color = f"{self.theme.success_color}22"  # Add transparency
                elif status == "failed":
                    style.border_color = self.theme.error_color
                    style.fill_color = f"{self.theme.error_color}22"  # Add transparency
                elif status == "waiting":
                    style.border_color = self.theme.warning_color
                    style.animation = "blink"
                
                self.node_styles[node_id] = style
                
                logger.debug(f"Updated status of node {node_id} to {status}")
                break
    
    def highlight_path(self, node_ids: List[str], highlight_type: str = "execution") -> None:
        """
        Highlight a path in the workflow graph.
        
        Args:
            node_ids: List of node IDs in the path
            highlight_type: Type of highlight (e.g., "execution", "critical", "alternative")
        """
        # Reset all edge styles first
        for edge in self.edges:
            edge_id = edge["id"]
            self.edge_styles[edge_id] = EdgeStyle()
        
        # Highlight edges in the path
        for i in range(len(node_ids) - 1):
            source_id = node_ids[i]
            target_id = node_ids[i + 1]
            edge_id = f"{source_id}-{target_id}"
            
            for edge in self.edges:
                if edge["source"] == source_id and edge["target"] == target_id:
                    style = EdgeStyle()
                    
                    if highlight_type == "execution":
                        style.color = self.theme.accent_color
                        style.width = 3
                        style.animation = "flow"
                    elif highlight_type == "critical":
                        style.color = self.theme.error_color
                        style.width = 3
                        style.animation = "pulse"
                    elif highlight_type == "alternative":
                        style.color = self.theme.secondary_color
                        style.dashed = True
                    
                    self.edge_styles[edge_id] = style
                    
                    logger.debug(f"Highlighted edge {edge_id} with type {highlight_type}")
                    break
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow graph visualization to a dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "layout_type": self.layout_type.value,
            "theme": vars(self.theme),
            "nodes": self.nodes,
            "edges": self.edges,
            "node_styles": {
                node_id: style.to_dict()
                for node_id, style in self.node_styles.items()
            },
            "edge_styles": {
                edge_id: style.to_dict()
                for edge_id, style in self.edge_styles.items()
            },
            "current_task_id": self.current_task_id,
            "completed_task_ids": self.completed_task_ids,
            "failed_task_ids": self.failed_task_ids,
            "waiting_task_ids": self.waiting_task_ids
        }
    
    def to_json(self) -> str:
        """Convert the workflow graph visualization to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_workflow_manifest(
        cls,
        workflow_manifest: Dict[str, Any],
        layout_type: LayoutType = LayoutType.HIERARCHICAL,
        theme: Optional[VisualizationTheme] = None
    ) -> 'WorkflowGraphVisualizer':
        """
        Create a workflow graph visualizer from a workflow manifest.
        
        Args:
            workflow_manifest: Workflow manifest dictionary
            layout_type: Type of layout for the graph
            theme: Theme configuration for the visualization
            
        Returns:
            A new WorkflowGraphVisualizer instance
        """
        workflow_id = workflow_manifest.get("name", "unknown")
        visualizer = cls(workflow_id, layout_type, theme)
        
        # Add nodes for each task
        for task in workflow_manifest.get("tasks", []):
            task_id = task.get("id")
            task_name = task.get("name", task_id)
            
            node_style = NodeStyle()
            
            # Set style based on task properties
            if task.get("human_in_loop"):
                node_style.shape = "rounded-rect"
                node_style.border_color = "#9b59b6"  # Purple for human tasks
                node_style.icon = "user"
            
            visualizer.add_node(
                node_id=task_id,
                label=task_name,
                data={
                    "description": task.get("description", ""),
                    "timeout_seconds": task.get("timeout_seconds"),
                    "retry_count": task.get("retry_count"),
                    "human_in_loop": task.get("human_in_loop", False)
                },
                style=node_style
            )
        
        # Add edges based on workflow transitions
        for transition in workflow_manifest.get("workflow", {}).get("transitions", []):
            source_id = transition.get("from")
            target_id = transition.get("to")
            condition = transition.get("condition", "")
            
            edge_style = EdgeStyle()
            
            # Set style based on transition properties
            if "wait_seconds" in transition:
                edge_style.dashed = True
                edge_style.color = "#3498db"  # Blue for wait transitions
            
            visualizer.add_edge(
                source_id=source_id,
                target_id=target_id,
                label=condition,
                data={
                    "condition": condition,
                    "wait_seconds": transition.get("wait_seconds")
                },
                style=edge_style
            )
        
        return visualizer


class TrustConfidenceVisualizer:
    """
    Class for visualizing trust and confidence scores.
    
    This class provides methods for creating visualizations of trust and
    confidence scores for workflow tasks and agents.
    """
    
    def __init__(
        self,
        theme: Optional[VisualizationTheme] = None
    ):
        """
        Initialize a new TrustConfidenceVisualizer.
        
        Args:
            theme: Theme configuration for the visualization
        """
        self.theme = theme or VisualizationTheme()
        self.data_points = []
        
        logger.info("Initialized TrustConfidenceVisualizer")
    
    def add_data_point(
        self,
        entity_id: str,
        entity_type: str,
        entity_name: str,
        trust_score: float,
        confidence_score: float,
        execution_mode: str,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a trust/confidence data point.
        
        Args:
            entity_id: ID of the entity (task, agent, etc.)
            entity_type: Type of entity
            entity_name: Display name of the entity
            trust_score: Trust score (0-1)
            confidence_score: Confidence score (0-1)
            execution_mode: Execution mode (e.g., "reactive", "proactive", "autonomous")
            timestamp: Optional timestamp for the data point
            metadata: Optional additional metadata
        """
        self.data_points.append({
            "entity_id": entity_id,
            "entity_type": entity_type,
            "entity_name": entity_name,
            "trust_score": trust_score,
            "confidence_score": confidence_score,
            "execution_mode": execution_mode,
            "timestamp": timestamp,
            "metadata": metadata or {}
        })
        
        logger.debug(f"Added trust/confidence data point for {entity_id}")
    
    def get_execution_mode_thresholds(
        self,
        workflow_manifest: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Extract execution mode thresholds from a workflow manifest.
        
        Args:
            workflow_manifest: Workflow manifest dictionary
            
        Returns:
            Dictionary mapping execution modes to their trust/confidence thresholds
        """
        thresholds = {}
        
        for mode in workflow_manifest.get("execution_modes", []):
            mode_name = mode.get("name")
            if mode_name:
                thresholds[mode_name] = {
                    "trust_threshold": mode.get("trust_threshold", 0.0),
                    "confidence_required": mode.get("confidence_required", 0.0),
                    "human_oversight": mode.get("human_oversight", True)
                }
        
        return thresholds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the trust/confidence visualization to a dictionary."""
        return {
            "theme": vars(self.theme),
            "data_points": self.data_points
        }
    
    def to_json(self) -> str:
        """Convert the trust/confidence visualization to a JSON string."""
        return json.dumps(self.to_dict())


class DebugTraceVisualizer:
    """
    Class for visualizing workflow debug traces.
    
    This class provides methods for creating visualizations of debug traces
    for workflow execution, showing detailed step-by-step agent logs and
    pattern-based optimization opportunities.
    """
    
    def __init__(
        self,
        workflow_id: str,
        theme: Optional[VisualizationTheme] = None
    ):
        """
        Initialize a new DebugTraceVisualizer.
        
        Args:
            workflow_id: ID of the workflow
            theme: Theme configuration for the visualization
        """
        self.workflow_id = workflow_id
        self.theme = theme or VisualizationTheme()
        self.trace_entries = []
        self.patterns = []
        self.filters = {
            "entity_types": [],
            "severity_levels": [],
            "time_range": None
        }
        
        logger.info(f"Initialized DebugTraceVisualizer for workflow {workflow_id}")
    
    def add_trace_entry(
        self,
        timestamp: str,
        entity_id: str,
        entity_type: str,
        message: str,
        severity: str = "info",
        data: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None
    ) -> None:
        """
        Add a debug trace entry.
        
        Args:
            timestamp: Timestamp of the entry
            entity_id: ID of the entity (task, agent, etc.)
            entity_type: Type of entity
            message: Debug message
            severity: Severity level (e.g., "info", "warning", "error")
            data: Optional additional data
            parent_id: Optional ID of the parent entry
        """
        entry_id = f"{len(self.trace_entries) + 1}"
        
        self.trace_entries.append({
            "id": entry_id,
            "timestamp": timestamp,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "message": message,
            "severity": severity,
            "data": data or {},
            "parent_id": parent_id
        })
        
        logger.debug(f"Added debug trace entry {entry_id} for {entity_id}")
    
    def add_pattern(
        self,
        pattern_type: str,
        name: str,
        description: str,
        affected_entities: List[str],
        optimization_suggestion: str,
        confidence: float,
        related_trace_ids: List[str]
    ) -> None:
        """
        Add a detected pattern in the debug trace.
        
        Args:
            pattern_type: Type of pattern (e.g., "bottleneck", "redundancy", "error_chain")
            name: Name of the pattern
            description: Description of the pattern
            affected_entities: List of affected entity IDs
            optimization_suggestion: Suggestion for optimization
            confidence: Confidence score for the pattern detection (0-1)
            related_trace_ids: List of related trace entry IDs
        """
        pattern_id = f"pattern-{len(self.patterns) + 1}"
        
        self.patterns.append({
            "id": pattern_id,
            "pattern_type": pattern_type,
            "name": name,
            "description": description,
            "affected_entities": affected_entities,
            "optimization_suggestion": optimization_suggestion,
            "confidence": confidence,
            "related_trace_ids": related_trace_ids
        })
        
        logger.debug(f"Added pattern {pattern_id} of type {pattern_type}")
    
    def set_filters(
        self,
        entity_types: Optional[List[str]] = None,
        severity_levels: Optional[List[str]] = None,
        time_range: Optional[Tuple[str, str]] = None
    ) -> None:
        """
        Set filters for the debug trace visualization.
        
        Args:
            entity_types: List of entity types to include
            severity_levels: List of severity levels to include
            time_range: Tuple of (start_time, end_time) to include
        """
        if entity_types is not None:
            self.filters["entity_types"] = entity_types
        
        if severity_levels is not None:
            self.filters["severity_levels"] = severity_levels
        
        if time_range is not None:
            self.filters["time_range"] = time_range
        
        logger.debug(f"Set filters for debug trace visualization: {self.filters}")
    
    def get_filtered_entries(self) -> List[Dict[str, Any]]:
        """
        Get filtered trace entries based on current filters.
        
        Returns:
            List of filtered trace entries
        """
        filtered = self.trace_entries
        
        # Apply entity type filter
        if self.filters["entity_types"]:
            filtered = [
                entry for entry in filtered
                if entry["entity_type"] in self.filters["entity_types"]
            ]
        
        # Apply severity level filter
        if self.filters["severity_levels"]:
            filtered = [
                entry for entry in filtered
                if entry["severity"] in self.filters["severity_levels"]
            ]
        
        # Apply time range filter
        if self.filters["time_range"]:
            start_time, end_time = self.filters["time_range"]
            filtered = [
                entry for entry in filtered
                if start_time <= entry["timestamp"] <= end_time
            ]
        
        return filtered
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the debug trace visualization to a dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "theme": vars(self.theme),
            "trace_entries": self.trace_entries,
            "patterns": self.patterns,
            "filters": self.filters
        }
    
    def to_json(self) -> str:
        """Convert the debug trace visualization to a JSON string."""
        return json.dumps(self.to_dict())


class WorkflowMetricsVisualizer:
    """
    Class for visualizing workflow performance metrics.
    
    This class provides methods for creating visualizations of workflow
    performance metrics, including execution time, resource usage,
    and success rates.
    """
    
    def __init__(
        self,
        workflow_id: str,
        theme: Optional[VisualizationTheme] = None
    ):
        """
        Initialize a new WorkflowMetricsVisualizer.
        
        Args:
            workflow_id: ID of the workflow
            theme: Theme configuration for the visualization
        """
        self.workflow_id = workflow_id
        self.theme = theme or VisualizationTheme()
        self.metrics = {}
        self.time_series = {}
        self.task_metrics = {}
        self.comparisons = {}
        
        logger.info(f"Initialized WorkflowMetricsVisualizer for workflow {workflow_id}")
    
    def set_overall_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Set overall workflow metrics.
        
        Args:
            metrics: Dictionary of overall metrics
        """
        self.metrics = metrics
        logger.debug(f"Set overall metrics for workflow {self.workflow_id}")
    
    def add_time_series(
        self,
        metric_name: str,
        data: List[Dict[str, Any]],
        unit: str,
        description: Optional[str] = None
    ) -> None:
        """
        Add a time series metric.
        
        Args:
            metric_name: Name of the metric
            data: List of data points (each with at least "timestamp" and "value")
            unit: Unit of measurement
            description: Optional description of the metric
        """
        self.time_series[metric_name] = {
            "data": data,
            "unit": unit,
            "description": description
        }
        
        logger.debug(f"Added time series for metric {metric_name}")
    
    def set_task_metrics(
        self,
        task_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Set metrics for a specific task.
        
        Args:
            task_id: ID of the task
            metrics: Dictionary of task metrics
        """
        self.task_metrics[task_id] = metrics
        logger.debug(f"Set metrics for task {task_id}")
    
    def add_comparison(
        self,
        comparison_name: str,
        data: Dict[str, Any],
        description: Optional[str] = None
    ) -> None:
        """
        Add a comparison metric.
        
        Args:
            comparison_name: Name of the comparison
            data: Comparison data
            description: Optional description of the comparison
        """
        self.comparisons[comparison_name] = {
            "data": data,
            "description": description
        }
        
        logger.debug(f"Added comparison {comparison_name}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow metrics visualization to a dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "theme": vars(self.theme),
            "metrics": self.metrics,
            "time_series": self.time_series,
            "task_metrics": self.task_metrics,
            "comparisons": self.comparisons
        }
    
    def to_json(self) -> str:
        """Convert the workflow metrics visualization to a JSON string."""
        return json.dumps(self.to_dict())


# Example usage
if __name__ == "__main__":
    # Create a workflow graph visualizer
    graph_viz = WorkflowGraphVisualizer("mfg-pm-001")
    
    # Add nodes
    graph_viz.add_node(
        node_id="data_collection",
        label="Collect Equipment Data",
        data={"description": "Collect sensor data from manufacturing equipment"}
    )
    
    graph_viz.add_node(
        node_id="anomaly_detection",
        label="Detect Anomalies",
        data={"description": "Analyze sensor data for anomalies"}
    )
    
    graph_viz.add_node(
        node_id="risk_assessment",
        label="Assess Maintenance Risk",
        data={"description": "Evaluate the risk level of detected anomalies"}
    )
    
    graph_viz.add_node(
        node_id="human_approval",
        label="Get Human Approval",
        data={"description": "Request approval for critical maintenance actions", "human_in_loop": True},
        style=NodeStyle(shape="rounded-rect", border_color="#9b59b6", icon="user")
    )
    
    # Add edges
    graph_viz.add_edge(
        source_id="data_collection",
        target_id="anomaly_detection",
        label="success"
    )
    
    graph_viz.add_edge(
        source_id="anomaly_detection",
        target_id="risk_assessment",
        label="anomalies.length > 0"
    )
    
    graph_viz.add_edge(
        source_id="risk_assessment",
        target_id="human_approval",
        label="risk_level == 'high'"
    )
    
    # Update node statuses
    graph_viz.update_node_status("data_collection", "completed", 1.0)
    graph_viz.update_node_status("anomaly_detection", "completed", 1.0)
    graph_viz.update_node_status("risk_assessment", "active", 0.7)
    
    # Highlight execution path
    graph_viz.highlight_path(["data_collection", "anomaly_detection", "risk_assessment"], "execution")
    
    # Print the graph visualization as JSON
    print(graph_viz.to_json())
    
    # Create a trust/confidence visualizer
    trust_viz = TrustConfidenceVisualizer()
    
    # Add data points
    trust_viz.add_data_point(
        entity_id="anomaly_detection",
        entity_type="task",
        entity_name="Detect Anomalies",
        trust_score=0.85,
        confidence_score=0.92,
        execution_mode="proactive"
    )
    
    trust_viz.add_data_point(
        entity_id="risk_assessment",
        entity_type="task",
        entity_name="Assess Maintenance Risk",
        trust_score=0.78,
        confidence_score=0.85,
        execution_mode="reactive"
    )
    
    # Print the trust/confidence visualization as JSON
    print(trust_viz.to_json())
