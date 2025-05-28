"""
Agent State Visualizer for Agent Ecosystem

This module provides visualization capabilities for agent states, relationships,
and activities within the Industriverse UI/UX Layer. It translates complex agent
state data into intuitive visual representations that help users understand agent
behavior, trust levels, and decision processes.

The Agent State Visualizer:
1. Renders agent state information in various visual formats
2. Visualizes agent relationships and communication patterns
3. Provides interactive visualizations for exploring agent behavior
4. Adapts visualizations based on device capabilities and user preferences
5. Supports different visualization modes for different contexts

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import math

# Local imports
from ..rendering_engine.rendering_engine import RenderingEngine
from ..context_engine.context_engine import ContextEngine
from ..universal_skin.device_adapter import DeviceAdapter
from .avatar_expression_engine import AvatarExpressionEngine

# Configure logging
logger = logging.getLogger(__name__)

class VisualizationMode(Enum):
    """Enumeration of visualization modes for agent states."""
    NETWORK = "network"           # Network/graph visualization of agent relationships
    TIMELINE = "timeline"         # Timeline visualization of agent activities
    HEATMAP = "heatmap"           # Heatmap visualization of agent metrics
    HIERARCHY = "hierarchy"       # Hierarchical visualization of agent organization
    FLOW = "flow"                 # Flow diagram of agent processes
    RADAR = "radar"               # Radar chart of agent capabilities
    TRUST_PATH = "trust_path"     # Visualization of trust pathways
    SWARM = "swarm"               # Swarm visualization of agent collective behavior

class VisualMetric(Enum):
    """Enumeration of metrics that can be visualized."""
    TRUST = "trust"               # Trust score
    CONFIDENCE = "confidence"     # Confidence level
    ACTIVITY = "activity"         # Activity level
    PERFORMANCE = "performance"   # Performance metrics
    ERRORS = "errors"             # Error rates
    LATENCY = "latency"           # Response latency
    THROUGHPUT = "throughput"     # Processing throughput
    RELATIONSHIPS = "relationships"  # Number of relationships
    DECISIONS = "decisions"       # Decision counts
    ESCALATIONS = "escalations"   # Escalation counts

class AgentStateVisualizer:
    """
    Provides visualization capabilities for agent states and relationships.
    
    This class is responsible for translating complex agent state data into
    intuitive visual representations that help users understand agent behavior,
    trust levels, and decision processes within the Industriverse UI/UX Layer.
    """
    
    def __init__(
        self, 
        rendering_engine: RenderingEngine,
        context_engine: ContextEngine,
        device_adapter: DeviceAdapter,
        avatar_expression_engine: AvatarExpressionEngine
    ):
        """
        Initialize the Agent State Visualizer.
        
        Args:
            rendering_engine: The Rendering Engine instance for visual rendering
            context_engine: The Context Engine instance for context awareness
            device_adapter: The Device Adapter instance for device-specific adaptations
            avatar_expression_engine: The Avatar Expression Engine for coordinating with avatar expressions
        """
        self.rendering_engine = rendering_engine
        self.context_engine = context_engine
        self.device_adapter = device_adapter
        self.avatar_expression_engine = avatar_expression_engine
        
        # Visualization configuration
        self.visualization_config = self._load_visualization_config()
        
        # Color schemes for different visualization types
        self.color_schemes = self._load_color_schemes()
        
        # Currently active visualizations
        self.active_visualizations = {}
        
        # Cached agent state data for visualization
        self.agent_state_cache = {}
        
        # Visualization history
        self.visualization_history = {}
        
        logger.info("Agent State Visualizer initialized")
    
    def _load_visualization_config(self) -> Dict:
        """
        Load visualization configuration.
        
        Returns:
            Dictionary of visualization configuration
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard visualization configurations inline
        
        return {
            VisualizationMode.NETWORK.value: {
                "node_size_range": [5, 30],
                "edge_width_range": [1, 5],
                "layout_algorithm": "force_directed",
                "animation_enabled": True,
                "interaction_enabled": True,
                "tooltip_enabled": True,
                "legend_enabled": True,
                "filter_enabled": True,
                "zoom_enabled": True,
                "pan_enabled": True,
                "highlight_enabled": True,
                "physics_settings": {
                    "gravity": -50,
                    "spring_length": 100,
                    "spring_strength": 0.1,
                    "damping": 0.09
                }
            },
            VisualizationMode.TIMELINE.value: {
                "item_height_range": [20, 50],
                "group_height": 70,
                "axis_position": "bottom",
                "stack_items": True,
                "snap_to_grid": False,
                "tooltip_enabled": True,
                "legend_enabled": True,
                "filter_enabled": True,
                "zoom_enabled": True,
                "pan_enabled": True,
                "highlight_enabled": True,
                "time_axis_settings": {
                    "scale": "minute",
                    "step": 1
                }
            },
            VisualizationMode.HEATMAP.value: {
                "cell_size_range": [10, 30],
                "color_range": ["#FFFFFF", "#FF0000"],
                "grid_lines": True,
                "tooltip_enabled": True,
                "legend_enabled": True,
                "zoom_enabled": True,
                "highlight_enabled": True,
                "label_settings": {
                    "show_row_labels": True,
                    "show_column_labels": True,
                    "label_font_size": 12
                }
            },
            VisualizationMode.HIERARCHY.value: {
                "node_size_range": [5, 30],
                "level_height": 100,
                "layout_algorithm": "tree",
                "orientation": "top_to_bottom",
                "tooltip_enabled": True,
                "legend_enabled": True,
                "filter_enabled": True,
                "zoom_enabled": True,
                "pan_enabled": True,
                "highlight_enabled": True,
                "tree_settings": {
                    "node_separation": 50,
                    "subtree_separation": 100
                }
            },
            VisualizationMode.FLOW.value: {
                "node_size_range": [30, 100],
                "edge_width_range": [1, 10],
                "layout_algorithm": "dagre",
                "orientation": "left_to_right",
                "tooltip_enabled": True,
                "legend_enabled": True,
                "filter_enabled": True,
                "zoom_enabled": True,
                "pan_enabled": True,
                "highlight_enabled": True,
                "flow_settings": {
                    "node_separation": 50,
                    "rank_separation": 100,
                    "edge_routing": "orthogonal"
                }
            },
            VisualizationMode.RADAR.value: {
                "radius": 150,
                "axis_count": 6,
                "fill_opacity": 0.5,
                "stroke_width": 2,
                "tooltip_enabled": True,
                "legend_enabled": True,
                "animation_enabled": True,
                "radar_settings": {
                    "start_angle": 0,
                    "clockwise": True,
                    "axis_labels_enabled": True
                }
            },
            VisualizationMode.TRUST_PATH.value: {
                "node_size_range": [5, 30],
                "edge_width_range": [1, 5],
                "layout_algorithm": "force_directed",
                "path_highlight_color": "#27AE60",
                "tooltip_enabled": True,
                "legend_enabled": True,
                "filter_enabled": True,
                "zoom_enabled": True,
                "pan_enabled": True,
                "highlight_enabled": True,
                "trust_path_settings": {
                    "show_trust_scores": True,
                    "animate_path_traversal": True,
                    "path_traversal_speed": 500  # ms
                }
            },
            VisualizationMode.SWARM.value: {
                "particle_size_range": [3, 15],
                "swarm_density": 0.7,
                "animation_enabled": True,
                "interaction_enabled": True,
                "tooltip_enabled": True,
                "legend_enabled": True,
                "filter_enabled": True,
                "zoom_enabled": True,
                "pan_enabled": True,
                "highlight_enabled": True,
                "swarm_settings": {
                    "cohesion": 0.8,
                    "separation": 0.3,
                    "alignment": 0.5,
                    "speed_limit": 5,
                    "boundary_behavior": "wrap"
                }
            }
        }
    
    def _load_color_schemes(self) -> Dict:
        """
        Load color schemes for different visualization types.
        
        Returns:
            Dictionary of color schemes
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard color schemes inline
        
        return {
            "default": {
                "background": "#FFFFFF",
                "text": "#333333",
                "accent": "#4A90E2",
                "highlight": "#27AE60",
                "warning": "#F39C12",
                "error": "#E74C3C",
                "neutral": "#95A5A6",
                "gradient": ["#3498DB", "#2ECC71", "#F1C40F", "#E74C3C"]
            },
            "trust": {
                "high": "#27AE60",
                "medium": "#F1C40F",
                "low": "#E74C3C",
                "unknown": "#95A5A6",
                "gradient": ["#E74C3C", "#F39C12", "#F1C40F", "#2ECC71", "#27AE60"]
            },
            "activity": {
                "high": "#E74C3C",
                "medium": "#F1C40F",
                "low": "#3498DB",
                "inactive": "#95A5A6",
                "gradient": ["#95A5A6", "#3498DB", "#F1C40F", "#E74C3C"]
            },
            "performance": {
                "excellent": "#27AE60",
                "good": "#2ECC71",
                "average": "#F1C40F",
                "poor": "#E74C3C",
                "unknown": "#95A5A6",
                "gradient": ["#E74C3C", "#F39C12", "#F1C40F", "#2ECC71", "#27AE60"]
            },
            "dark_mode": {
                "background": "#2C3E50",
                "text": "#ECF0F1",
                "accent": "#3498DB",
                "highlight": "#2ECC71",
                "warning": "#F39C12",
                "error": "#E74C3C",
                "neutral": "#95A5A6",
                "gradient": ["#3498DB", "#2ECC71", "#F1C40F", "#E74C3C"]
            }
        }
    
    def visualize_agent_state(
        self, 
        agent_id: str, 
        container_id: str,
        visualization_mode: str = VisualizationMode.NETWORK.value,
        metrics: List[str] = None,
        options: Dict = None
    ) -> bool:
        """
        Visualize the state of a specific agent.
        
        Args:
            agent_id: The ID of the agent to visualize
            container_id: The ID of the container to render the visualization in
            visualization_mode: The visualization mode to use
            metrics: Optional list of metrics to include in the visualization
            options: Optional additional visualization options
            
        Returns:
            Boolean indicating success
        """
        # Verify visualization mode exists
        if visualization_mode not in self.visualization_config:
            logger.error(f"Visualization mode {visualization_mode} not found in visualization configuration")
            return False
        
        # Get agent state data
        agent_state = self.context_engine.get_agent_state(agent_id)
        if not agent_state:
            logger.error(f"Agent state data not found for agent {agent_id}")
            return False
        
        # Cache agent state data
        self.agent_state_cache[agent_id] = agent_state
        
        # Get visualization configuration
        viz_config = self.visualization_config[visualization_mode]
        
        # Apply options if provided
        if options:
            viz_config = {**viz_config, **options}
        
        # Determine metrics to visualize
        if not metrics:
            # Default metrics based on visualization mode
            if visualization_mode == VisualizationMode.NETWORK.value:
                metrics = [VisualMetric.RELATIONSHIPS.value, VisualMetric.TRUST.value]
            elif visualization_mode == VisualizationMode.TIMELINE.value:
                metrics = [VisualMetric.ACTIVITY.value, VisualMetric.DECISIONS.value]
            elif visualization_mode == VisualizationMode.HEATMAP.value:
                metrics = [VisualMetric.PERFORMANCE.value, VisualMetric.ERRORS.value]
            elif visualization_mode == VisualizationMode.HIERARCHY.value:
                metrics = [VisualMetric.RELATIONSHIPS.value]
            elif visualization_mode == VisualizationMode.FLOW.value:
                metrics = [VisualMetric.DECISIONS.value, VisualMetric.ESCALATIONS.value]
            elif visualization_mode == VisualizationMode.RADAR.value:
                metrics = [m.value for m in VisualMetric]  # All metrics
            elif visualization_mode == VisualizationMode.TRUST_PATH.value:
                metrics = [VisualMetric.TRUST.value, VisualMetric.CONFIDENCE.value]
            elif visualization_mode == VisualizationMode.SWARM.value:
                metrics = [VisualMetric.ACTIVITY.value, VisualMetric.RELATIONSHIPS.value]
        
        # Prepare visualization data
        visualization_data = self._prepare_visualization_data(
            agent_id, 
            agent_state, 
            visualization_mode, 
            metrics
        )
        
        # Get color scheme
        color_scheme = self._get_color_scheme()
        
        # Prepare rendering options
        render_options = {
            "mode": visualization_mode,
            "config": viz_config,
            "colors": color_scheme,
            "data": visualization_data,
            "metrics": metrics
        }
        
        # Store active visualization
        self.active_visualizations[container_id] = {
            "agent_id": agent_id,
            "mode": visualization_mode,
            "metrics": metrics,
            "options": viz_config,
            "timestamp": time.time()
        }
        
        # Add to visualization history
        if agent_id not in self.visualization_history:
            self.visualization_history[agent_id] = []
        
        # Limit history length
        if len(self.visualization_history[agent_id]) > 20:
            self.visualization_history[agent_id].pop(0)
        
        self.visualization_history[agent_id].append({
            "mode": visualization_mode,
            "metrics": metrics,
            "timestamp": time.time()
        })
        
        # Render visualization
        self.rendering_engine.render_visualization(container_id, render_options)
        
        logger.info(f"Visualized agent {agent_id} state in {visualization_mode} mode")
        return True
    
    def _prepare_visualization_data(
        self, 
        agent_id: str, 
        agent_state: Dict, 
        visualization_mode: str,
        metrics: List[str]
    ) -> Dict:
        """
        Prepare data for visualization based on agent state.
        
        Args:
            agent_id: The ID of the agent
            agent_state: The agent state data
            visualization_mode: The visualization mode
            metrics: List of metrics to include
            
        Returns:
            Dictionary of prepared visualization data
        """
        # Prepare data structure based on visualization mode
        if visualization_mode == VisualizationMode.NETWORK.value:
            return self._prepare_network_visualization(agent_id, agent_state, metrics)
        elif visualization_mode == VisualizationMode.TIMELINE.value:
            return self._prepare_timeline_visualization(agent_id, agent_state, metrics)
        elif visualization_mode == VisualizationMode.HEATMAP.value:
            return self._prepare_heatmap_visualization(agent_id, agent_state, metrics)
        elif visualization_mode == VisualizationMode.HIERARCHY.value:
            return self._prepare_hierarchy_visualization(agent_id, agent_state, metrics)
        elif visualization_mode == VisualizationMode.FLOW.value:
            return self._prepare_flow_visualization(agent_id, agent_state, metrics)
        elif visualization_mode == VisualizationMode.RADAR.value:
            return self._prepare_radar_visualization(agent_id, agent_state, metrics)
        elif visualization_mode == VisualizationMode.TRUST_PATH.value:
            return self._prepare_trust_path_visualization(agent_id, agent_state, metrics)
        elif visualization_mode == VisualizationMode.SWARM.value:
            return self._prepare_swarm_visualization(agent_id, agent_state, metrics)
        else:
            # Default to network visualization
            return self._prepare_network_visualization(agent_id, agent_state, metrics)
    
    def _prepare_network_visualization(
        self, 
        agent_id: str, 
        agent_state: Dict, 
        metrics: List[str]
    ) -> Dict:
        """
        Prepare data for network visualization.
        
        Args:
            agent_id: The ID of the agent
            agent_state: The agent state data
            metrics: List of metrics to include
            
        Returns:
            Dictionary of prepared network visualization data
        """
        # Extract relationships from agent state
        relationships = agent_state.get("relationships", [])
        
        # Prepare nodes and edges
        nodes = [{
            "id": agent_id,
            "label": agent_state.get("name", agent_id),
            "type": agent_state.get("type", "unknown"),
            "metrics": {
                metric: agent_state.get(metric, 0) for metric in metrics if metric in agent_state
            },
            "size": 20,  # Base size, will be adjusted based on metrics
            "color": self._get_node_color(agent_state, metrics),
            "is_central": True
        }]
        
        edges = []
        
        # Add related agents as nodes and create edges
        for relationship in relationships:
            related_agent_id = relationship.get("agent_id")
            if not related_agent_id:
                continue
            
            # Get related agent state
            related_agent_state = self.context_engine.get_agent_state(related_agent_id)
            if not related_agent_state:
                # If state not available, create minimal node
                related_agent_state = {
                    "name": relationship.get("agent_name", related_agent_id),
                    "type": relationship.get("agent_type", "unknown")
                }
            
            # Add node for related agent
            nodes.append({
                "id": related_agent_id,
                "label": related_agent_state.get("name", related_agent_id),
                "type": related_agent_state.get("type", "unknown"),
                "metrics": {
                    metric: related_agent_state.get(metric, 0) for metric in metrics if metric in related_agent_state
                },
                "size": 15,  # Slightly smaller than central agent
                "color": self._get_node_color(related_agent_state, metrics),
                "is_central": False
            })
            
            # Add edge for relationship
            edges.append({
                "source": agent_id,
                "target": related_agent_id,
                "label": relationship.get("type", "related"),
                "weight": relationship.get("strength", 1),
                "metrics": {
                    metric: relationship.get(metric, 0) for metric in metrics if metric in relationship
                },
                "color": self._get_edge_color(relationship, metrics),
                "width": self._get_edge_width(relationship, metrics)
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _prepare_timeline_visualization(
        self, 
        agent_id: str, 
        agent_state: Dict, 
        metrics: List[str]
    ) -> Dict:
        """
        Prepare data for timeline visualization.
        
        Args:
            agent_id: The ID of the agent
            agent_state: The agent state data
            metrics: List of metrics to include
            
        Returns:
            Dictionary of prepared timeline visualization data
        """
        # Extract activity history from agent state
        activity_history = agent_state.get("activity_history", [])
        
        # Prepare timeline items
        items = []
        
        for activity in activity_history:
            # Create timeline item
            item = {
                "id": activity.get("id", f"activity_{len(items)}"),
                "content": activity.get("description", "Activity"),
                "start": activity.get("timestamp", time.time()),
                "group": activity.get("type", "default"),
                "type": "box",  # box, point, range
                "className": f"activity-{activity.get('status', 'unknown')}",
                "metrics": {
                    metric: activity.get(metric, 0) for metric in metrics if metric in activity
                }
            }
            
            # Add end time if available (for range items)
            if "end_timestamp" in activity:
                item["end"] = activity["end_timestamp"]
                item["type"] = "range"
            
            items.append(item)
        
        # Prepare timeline groups
        groups = []
        
        # Extract unique activity types for groups
        activity_types = set(activity.get("type", "default") for activity in activity_history)
        
        for activity_type in activity_types:
            groups.append({
                "id": activity_type,
                "content": activity_type.capitalize(),
                "className": f"group-{activity_type}"
            })
        
        return {
            "items": items,
            "groups": groups
        }
    
    def _prepare_heatmap_visualization(
        self, 
        agent_id: str, 
        agent_state: Dict, 
        metrics: List[str]
    ) -> Dict:
        """
        Prepare data for heatmap visualization.
        
        Args:
            agent_id: The ID of the agent
            agent_state: The agent state data
            metrics: List of metrics to include
            
        Returns:
            Dictionary of prepared heatmap visualization data
        """
        # Extract performance metrics from agent state
        performance_metrics = agent_state.get("performance_metrics", {})
        
        # Prepare heatmap data
        rows = []
        columns = []
        values = []
        
        # Extract metrics for rows and time periods for columns
        for metric_name, metric_data in performance_metrics.items():
            if metric_name in metrics:
                rows.append(metric_name)
                
                for time_period, value in metric_data.items():
                    if time_period not in columns:
                        columns.append(time_period)
                    
                    values.append({
                        "row": metric_name,
                        "column": time_period,
                        "value": value
                    })
        
        return {
            "rows": rows,
            "columns": columns,
            "values": values
        }
    
    def _prepare_hierarchy_visualization(
        self, 
        agent_id: str, 
        agent_state: Dict, 
        metrics: List[str]
    ) -> Dict:
        """
        Prepare data for hierarchy visualization.
        
        Args:
            agent_id: The ID of the agent
            agent_state: The agent state data
            metrics: List of metrics to include
            
        Returns:
            Dictionary of prepared hierarchy visualization data
        """
        # Extract hierarchy information from agent state
        hierarchy = agent_state.get("hierarchy", {})
        
        # Prepare hierarchy data
        root = {
            "id": agent_id,
            "name": agent_state.get("name", agent_id),
            "type": agent_state.get("type", "unknown"),
            "metrics": {
                metric: agent_state.get(metric, 0) for metric in metrics if metric in agent_state
            },
            "children": []
        }
        
        # Add children from hierarchy
        children = hierarchy.get("children", [])
        for child in children:
            child_id = child.get("agent_id")
            if not child_id:
                continue
            
            # Get child agent state
            child_agent_state = self.context_engine.get_agent_state(child_id)
            if not child_agent_state:
                # If state not available, create minimal node
                child_agent_state = {
                    "name": child.get("agent_name", child_id),
                    "type": child.get("agent_type", "unknown")
                }
            
            # Create child node
            child_node = {
                "id": child_id,
                "name": child_agent_state.get("name", child_id),
                "type": child_agent_state.get("type", "unknown"),
                "metrics": {
                    metric: child_agent_state.get(metric, 0) for metric in metrics if metric in child_agent_state
                },
                "children": []
            }
            
            # Recursively add grandchildren (if available)
            if "children" in child and child["children"]:
                for grandchild in child["children"]:
                    grandchild_id = grandchild.get("agent_id")
                    if not grandchild_id:
                        continue
                    
                    # Get grandchild agent state
                    grandchild_agent_state = self.context_engine.get_agent_state(grandchild_id)
                    if not grandchild_agent_state:
                        # If state not available, create minimal node
                        grandchild_agent_state = {
                            "name": grandchild.get("agent_name", grandchild_id),
                            "type": grandchild.get("agent_type", "unknown")
                        }
                    
                    # Create grandchild node
                    grandchild_node = {
                        "id": grandchild_id,
                        "name": grandchild_agent_state.get("name", grandchild_id),
                        "type": grandchild_agent_state.get("type", "unknown"),
                        "metrics": {
                            metric: grandchild_agent_state.get(metric, 0) for metric in metrics if metric in grandchild_agent_state
                        },
                        "children": []
                    }
                    
                    child_node["children"].append(grandchild_node)
            
            root["children"].append(child_node)
        
        return {
            "root": root
        }
    
    def _prepare_flow_visualization(
        self, 
        agent_id: str, 
        agent_state: Dict, 
        metrics: List[str]
    ) -> Dict:
        """
        Prepare data for flow visualization.
        
        Args:
            agent_id: The ID of the agent
            agent_state: The agent state data
            metrics: List of metrics to include
            
        Returns:
            Dictionary of prepared flow visualization data
        """
        # Extract workflow information from agent state
        workflow = agent_state.get("workflow", {})
        
        # Prepare nodes and edges
        nodes = [{
            "id": agent_id,
            "label": agent_state.get("name", agent_id),
            "type": "agent",
            "metrics": {
                metric: agent_state.get(metric, 0) for metric in metrics if metric in agent_state
            }
        }]
        
        edges = []
        
        # Add workflow steps as nodes and create edges
        steps = workflow.get("steps", [])
        for i, step in enumerate(steps):
            step_id = step.get("id", f"step_{i}")
            
            # Add node for step
            nodes.append({
                "id": step_id,
                "label": step.get("name", f"Step {i+1}"),
                "type": "step",
                "metrics": {
                    metric: step.get(metric, 0) for metric in metrics if metric in step
                }
            })
            
            # Add edge from previous node to this step
            if i == 0:
                # First step connects from agent
                edges.append({
                    "source": agent_id,
                    "target": step_id,
                    "label": "initiates",
                    "metrics": {}
                })
            else:
                # Connect from previous step
                prev_step_id = steps[i-1].get("id", f"step_{i-1}")
                edges.append({
                    "source": prev_step_id,
                    "target": step_id,
                    "label": step.get("transition_type", "next"),
                    "metrics": {}
                })
            
            # Add decision branches if present
            branches = step.get("branches", [])
            for branch in branches:
                branch_id = branch.get("id", f"{step_id}_branch_{len(edges)}")
                branch_target = branch.get("target_step_id")
                
                if branch_target:
                    # Add edge for branch
                    edges.append({
                        "source": step_id,
                        "target": branch_target,
                        "label": branch.get("condition", "branch"),
                        "metrics": {
                            metric: branch.get(metric, 0) for metric in metrics if metric in branch
                        }
                    })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _prepare_radar_visualization(
        self, 
        agent_id: str, 
        agent_state: Dict, 
        metrics: List[str]
    ) -> Dict:
        """
        Prepare data for radar visualization.
        
        Args:
            agent_id: The ID of the agent
            agent_state: The agent state data
            metrics: List of metrics to include
            
        Returns:
            Dictionary of prepared radar visualization data
        """
        # Prepare radar data
        axes = []
        values = []
        
        # Add axis and value for each metric
        for metric in metrics:
            # Skip metrics not present in agent state
            if metric not in agent_state:
                continue
            
            # Add axis
            axes.append({
                "name": metric,
                "min": 0,
                "max": 1  # Assuming normalized values
            })
            
            # Add value
            values.append({
                "axis": metric,
                "value": agent_state[metric]
            })
        
        return {
            "axes": axes,
            "values": values
        }
    
    def _prepare_trust_path_visualization(
        self, 
        agent_id: str, 
        agent_state: Dict, 
        metrics: List[str]
    ) -> Dict:
        """
        Prepare data for trust path visualization.
        
        Args:
            agent_id: The ID of the agent
            agent_state: The agent state data
            metrics: List of metrics to include
            
        Returns:
            Dictionary of prepared trust path visualization data
        """
        # Extract trust paths from agent state
        trust_paths = agent_state.get("trust_paths", [])
        
        # Prepare nodes and edges
        nodes = [{
            "id": agent_id,
            "label": agent_state.get("name", agent_id),
            "type": agent_state.get("type", "unknown"),
            "trust_score": agent_state.get("trust", 0.5),
            "is_source": True
        }]
        
        edges = []
        paths = []
        
        # Process each trust path
        for path_index, path in enumerate(trust_paths):
            path_nodes = path.get("nodes", [])
            path_edges = []
            
            # Add nodes and edges for this path
            prev_node_id = agent_id
            for i, node in enumerate(path_nodes):
                node_id = node.get("agent_id")
                if not node_id:
                    continue
                
                # Check if node already exists
                existing_node = next((n for n in nodes if n["id"] == node_id), None)
                if not existing_node:
                    # Add new node
                    nodes.append({
                        "id": node_id,
                        "label": node.get("agent_name", node_id),
                        "type": node.get("agent_type", "unknown"),
                        "trust_score": node.get("trust_score", 0.5),
                        "is_source": False,
                        "is_target": i == len(path_nodes) - 1
                    })
                elif i == len(path_nodes) - 1:
                    # Mark existing node as target if it's the last node in this path
                    existing_node["is_target"] = True
                
                # Add edge
                edge_id = f"{prev_node_id}_{node_id}"
                edges.append({
                    "id": edge_id,
                    "source": prev_node_id,
                    "target": node_id,
                    "trust_score": node.get("edge_trust_score", 0.5),
                    "path_index": path_index
                })
                
                path_edges.append(edge_id)
                prev_node_id = node_id
            
            # Add path
            paths.append({
                "id": f"path_{path_index}",
                "name": path.get("name", f"Trust Path {path_index + 1}"),
                "trust_score": path.get("aggregate_trust", 0.5),
                "edges": path_edges
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "paths": paths
        }
    
    def _prepare_swarm_visualization(
        self, 
        agent_id: str, 
        agent_state: Dict, 
        metrics: List[str]
    ) -> Dict:
        """
        Prepare data for swarm visualization.
        
        Args:
            agent_id: The ID of the agent
            agent_state: The agent state data
            metrics: List of metrics to include
            
        Returns:
            Dictionary of prepared swarm visualization data
        """
        # Extract swarm information from agent state
        swarm = agent_state.get("swarm", {})
        
        # Prepare particles
        particles = [{
            "id": agent_id,
            "label": agent_state.get("name", agent_id),
            "type": agent_state.get("type", "unknown"),
            "metrics": {
                metric: agent_state.get(metric, 0) for metric in metrics if metric in agent_state
            },
            "size": 10,
            "color": self._get_node_color(agent_state, metrics),
            "is_central": True
        }]
        
        # Add swarm members as particles
        members = swarm.get("members", [])
        for member in members:
            member_id = member.get("agent_id")
            if not member_id:
                continue
            
            # Get member agent state
            member_agent_state = self.context_engine.get_agent_state(member_id)
            if not member_agent_state:
                # If state not available, create minimal particle
                member_agent_state = {
                    "name": member.get("agent_name", member_id),
                    "type": member.get("agent_type", "unknown")
                }
            
            # Add particle for member
            particles.append({
                "id": member_id,
                "label": member_agent_state.get("name", member_id),
                "type": member_agent_state.get("type", "unknown"),
                "metrics": {
                    metric: member_agent_state.get(metric, 0) for metric in metrics if metric in member_agent_state
                },
                "size": 7,  # Smaller than central agent
                "color": self._get_node_color(member_agent_state, metrics),
                "is_central": False
            })
        
        # Prepare swarm behaviors
        behaviors = swarm.get("behaviors", [])
        
        return {
            "particles": particles,
            "behaviors": behaviors
        }
    
    def _get_node_color(self, agent_state: Dict, metrics: List[str]) -> str:
        """
        Determine node color based on agent state and metrics.
        
        Args:
            agent_state: The agent state data
            metrics: List of metrics being visualized
            
        Returns:
            Color string
        """
        color_scheme = self._get_color_scheme()
        
        # Prioritize trust if it's one of the metrics
        if VisualMetric.TRUST.value in metrics and VisualMetric.TRUST.value in agent_state:
            trust = agent_state[VisualMetric.TRUST.value]
            
            if trust >= 0.8:
                return color_scheme["trust"]["high"]
            elif trust >= 0.5:
                return color_scheme["trust"]["medium"]
            elif trust >= 0:
                return color_scheme["trust"]["low"]
            else:
                return color_scheme["trust"]["unknown"]
        
        # Otherwise use agent type
        agent_type = agent_state.get("type", "unknown")
        
        if agent_type == "router":
            return color_scheme["default"]["accent"]
        elif agent_type == "processor":
            return color_scheme["default"]["highlight"]
        elif agent_type == "monitor":
            return color_scheme["default"]["warning"]
        elif agent_type == "controller":
            return color_scheme["default"]["error"]
        else:
            return color_scheme["default"]["neutral"]
    
    def _get_edge_color(self, relationship: Dict, metrics: List[str]) -> str:
        """
        Determine edge color based on relationship and metrics.
        
        Args:
            relationship: The relationship data
            metrics: List of metrics being visualized
            
        Returns:
            Color string
        """
        color_scheme = self._get_color_scheme()
        
        # Prioritize trust if it's one of the metrics
        if VisualMetric.TRUST.value in metrics and VisualMetric.TRUST.value in relationship:
            trust = relationship[VisualMetric.TRUST.value]
            
            if trust >= 0.8:
                return color_scheme["trust"]["high"]
            elif trust >= 0.5:
                return color_scheme["trust"]["medium"]
            elif trust >= 0:
                return color_scheme["trust"]["low"]
            else:
                return color_scheme["trust"]["unknown"]
        
        # Otherwise use relationship type
        relationship_type = relationship.get("type", "unknown")
        
        if relationship_type == "parent":
            return color_scheme["default"]["accent"]
        elif relationship_type == "child":
            return color_scheme["default"]["highlight"]
        elif relationship_type == "peer":
            return color_scheme["default"]["warning"]
        elif relationship_type == "service":
            return color_scheme["default"]["error"]
        else:
            return color_scheme["default"]["neutral"]
    
    def _get_edge_width(self, relationship: Dict, metrics: List[str]) -> float:
        """
        Determine edge width based on relationship and metrics.
        
        Args:
            relationship: The relationship data
            metrics: List of metrics being visualized
            
        Returns:
            Edge width
        """
        # Base width
        width = 1.0
        
        # Adjust based on relationship strength if available
        if "strength" in relationship:
            width = 1.0 + (relationship["strength"] * 2.0)
        
        # Adjust based on activity if it's one of the metrics
        if VisualMetric.ACTIVITY.value in metrics and VisualMetric.ACTIVITY.value in relationship:
            activity = relationship[VisualMetric.ACTIVITY.value]
            width *= (1.0 + activity)
        
        return min(5.0, width)  # Cap at 5.0
    
    def _get_color_scheme(self) -> Dict:
        """
        Get the appropriate color scheme based on context and preferences.
        
        Returns:
            Dictionary of color scheme
        """
        # Check user preferences for dark mode
        user_preferences = self.context_engine.get_user_preferences()
        if user_preferences.get("dark_mode", False):
            return self.color_schemes["dark_mode"]
        
        return self.color_schemes["default"]
    
    def update_visualization(self, container_id: str) -> bool:
        """
        Update an active visualization with latest data.
        
        Args:
            container_id: The ID of the container with the visualization
            
        Returns:
            Boolean indicating success
        """
        # Check if container has an active visualization
        if container_id not in self.active_visualizations:
            logger.error(f"No active visualization found for container {container_id}")
            return False
        
        # Get active visualization details
        viz = self.active_visualizations[container_id]
        
        # Visualize with same parameters but updated data
        return self.visualize_agent_state(
            viz["agent_id"],
            container_id,
            viz["mode"],
            viz["metrics"],
            viz["options"]
        )
    
    def get_visualization_history(self, agent_id: str, limit: int = 10) -> List[Dict]:
        """
        Get visualization history for a specific agent.
        
        Args:
            agent_id: The ID of the agent to get history for
            limit: Maximum number of history items to return
            
        Returns:
            List of dictionaries containing historical visualization information
        """
        history = self.visualization_history.get(agent_id, [])
        return history[-limit:]
    
    def adapt_to_context_change(self, context_update: Dict) -> None:
        """
        Adapt visualizations based on a context change.
        
        Args:
            context_update: Dictionary containing context update information
        """
        # Update all active visualizations
        for container_id in list(self.active_visualizations.keys()):
            self.update_visualization(container_id)
        
        logger.info(f"Visualizations adapted to context change: {context_update.get('type', 'unknown')}")
"""
