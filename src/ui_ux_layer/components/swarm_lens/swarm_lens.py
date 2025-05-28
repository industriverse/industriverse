"""
Swarm Lens Component for the UI/UX Layer

This component provides a visual interface for monitoring and interacting with
swarms of agents in the Industriverse ecosystem. It visualizes agent relationships,
activities, and collective intelligence patterns.

The Swarm Lens:
1. Visualizes agent swarms and their relationships
2. Displays agent activities and communications in real-time
3. Provides insights into collective intelligence patterns
4. Enables interaction with individual agents and agent groups
5. Supports filtering and focusing on specific swarm behaviors
6. Integrates with the Agent Ecosystem for agent management

Author: Manus
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable
import time
import uuid
import math

# Local imports
from ..core.rendering_engine.rendering_engine import RenderingEngine
from ..core.context_engine.context_engine import ContextEngine
from ..core.agent_ecosystem.agent_interaction_protocol import AgentInteractionProtocol
from ..core.capsule_framework.capsule_manager import CapsuleManager
from ..core.agent_ecosystem.agent_state_visualizer import AgentStateVisualizer

# Configure logging
logger = logging.getLogger(__name__)

class SwarmLens:
    """
    Swarm Lens component for visualizing and interacting with agent swarms.
    """
    
    def __init__(
        self,
        rendering_engine: RenderingEngine,
        context_engine: ContextEngine,
        agent_protocol: AgentInteractionProtocol,
        capsule_manager: CapsuleManager,
        agent_state_visualizer: AgentStateVisualizer,
        config: Dict = None
    ):
        """
        Initialize the Swarm Lens.
        
        Args:
            rendering_engine: Rendering Engine instance
            context_engine: Context Engine instance
            agent_protocol: Agent Interaction Protocol instance
            capsule_manager: Capsule Manager instance
            agent_state_visualizer: Agent State Visualizer instance
            config: Optional configuration dictionary
        """
        self.rendering_engine = rendering_engine
        self.context_engine = context_engine
        self.agent_protocol = agent_protocol
        self.capsule_manager = capsule_manager
        self.agent_state_visualizer = agent_state_visualizer
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "max_agents_to_display": 100,
            "node_size": 1.0,
            "edge_width": 1.0,
            "animation_speed": 1.0,
            "default_layout": "force_directed",
            "enable_physics": True,
            "physics_settings": {
                "gravity": -50,
                "spring_length": 100,
                "spring_coefficient": 0.8,
                "damping": 0.4,
                "avoidance": 5
            },
            "enable_clustering": True,
            "clustering_threshold": 0.7,
            "enable_heatmap": True,
            "heatmap_resolution": 50,
            "enable_timeline": True,
            "timeline_window": 60,  # seconds
            "enable_agent_details": True,
            "enable_communication_visualization": True,
            "communication_fade_time": 5.0,  # seconds
            "default_filter": {
                "agent_types": [],
                "capabilities": [],
                "states": [],
                "tags": []
            },
            "color_scheme": {
                "background": "#1E1E2E",
                "nodes": {
                    "default": "#4CAF50",
                    "selected": "#FFC107",
                    "highlighted": "#E91E63",
                    "inactive": "#9E9E9E"
                },
                "edges": {
                    "default": "#FFFFFF",
                    "communication": "#2196F3",
                    "delegation": "#FF9800",
                    "collaboration": "#8BC34A"
                },
                "clusters": [
                    "#3F51B5",
                    "#009688",
                    "#FF5722",
                    "#9C27B0",
                    "#CDDC39",
                    "#795548"
                ]
            }
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Current state
        self.agents = {}
        self.relationships = {}
        self.communications = []
        self.clusters = {}
        self.selected_agents = []
        self.highlighted_agents = []
        self.current_filter = self.config["default_filter"].copy()
        self.current_layout = self.config["default_layout"]
        self.zoom_level = 1.0
        self.pan_offset = {"x": 0, "y": 0}
        self.heatmap_data = []
        self.timeline_data = []
        self.last_update_time = 0
        
        # Event handlers
        self.event_handlers = {
            "agent_added": [],
            "agent_removed": [],
            "agent_updated": [],
            "relationship_added": [],
            "relationship_removed": [],
            "communication_visualized": [],
            "selection_changed": [],
            "filter_changed": [],
            "layout_changed": [],
            "clusters_updated": [],
            "heatmap_updated": [],
            "timeline_updated": [],
            "error": []
        }
        
        # Register with context engine
        self.context_engine.register_context_listener(self._handle_context_change)
        
        # Register with agent protocol for agent updates
        self.agent_protocol.register_message_handler(
            "state_update",
            self._handle_agent_update,
            "*"
        )
        
        # Register with agent protocol for agent communications
        self.agent_protocol.register_message_handler(
            "request",
            self._handle_agent_communication,
            "*"
        )
        self.agent_protocol.register_message_handler(
            "response",
            self._handle_agent_communication,
            "*"
        )
        self.agent_protocol.register_message_handler(
            "command",
            self._handle_agent_communication,
            "*"
        )
        self.agent_protocol.register_message_handler(
            "notification",
            self._handle_agent_communication,
            "*"
        )
        
        logger.info("Swarm Lens initialized")
    
    def _merge_config(self) -> None:
        """Merge provided configuration with defaults."""
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                # Merge nested dictionaries
                for nested_key, nested_value in value.items():
                    if nested_key not in self.config[key]:
                        self.config[key][nested_key] = nested_value
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        context_type = event.get("type")
        
        # Handle agent filter context changes
        if context_type == "agent_filter":
            filter_data = event.get("data", {})
            self.set_filter(filter_data)
        
        # Handle agent selection context changes
        elif context_type == "agent_selection":
            selection_data = event.get("data", {})
            if "agent_id" in selection_data:
                self.select_agent(selection_data["agent_id"])
    
    def _handle_agent_update(self, message: Dict) -> None:
        """
        Handle agent state updates.
        
        Args:
            message: State update message
        """
        try:
            payload = message.get("payload", {})
            source_id = message.get("source", {}).get("id")
            source_type = message.get("source", {}).get("type")
            
            # Only process agent updates
            if source_type != "agent":
                return
            
            # Update or add agent
            self._update_agent(source_id, payload)
        except Exception as e:
            logger.error(f"Error handling agent update: {str(e)}")
    
    def _handle_agent_communication(self, message: Dict) -> None:
        """
        Handle agent communications.
        
        Args:
            message: Communication message
        """
        try:
            if not self.config["enable_communication_visualization"]:
                return
                
            source_id = message.get("source", {}).get("id")
            source_type = message.get("source", {}).get("type")
            target_id = message.get("target", {}).get("id")
            target_type = message.get("target", {}).get("type")
            message_type = message.get("type")
            
            # Only process agent-to-agent communications
            if source_type != "agent" or target_type != "agent":
                return
            
            # Check if both agents are being visualized
            if source_id not in self.agents or target_id not in self.agents:
                return
            
            # Create communication visualization
            self._visualize_communication(source_id, target_id, message_type, message)
        except Exception as e:
            logger.error(f"Error handling agent communication: {str(e)}")
    
    def _update_agent(self, agent_id: str, state: Dict) -> None:
        """
        Update or add an agent.
        
        Args:
            agent_id: Agent identifier
            state: Agent state data
        """
        # Check if agent exists
        is_new = agent_id not in self.agents
        
        # Get current time
        current_time = time.time()
        
        if is_new:
            # Create new agent
            agent = {
                "id": agent_id,
                "type": state.get("type", "unknown"),
                "name": state.get("name", agent_id),
                "capabilities": state.get("capabilities", []),
                "state": state.get("state", "idle"),
                "position": state.get("position", self._generate_random_position()),
                "velocity": {"x": 0, "y": 0},
                "size": state.get("size", self.config["node_size"]),
                "color": self._get_agent_color(state),
                "tags": state.get("tags", []),
                "data": state.get("data", {}),
                "last_activity": current_time,
                "creation_time": current_time
            }
            
            # Add to agents dictionary
            self.agents[agent_id] = agent
            
            # Add to rendering engine
            self.rendering_engine.add_swarm_agent(agent_id, agent)
            
            # Trigger agent added event
            self._trigger_event("agent_added", {
                "agent_id": agent_id,
                "agent": agent
            })
            
            # Check for relationships
            if "relationships" in state:
                for rel in state["relationships"]:
                    self._add_relationship(agent_id, rel["target_id"], rel["type"], rel.get("strength", 1.0))
            
            # Update clusters if enabled
            if self.config["enable_clustering"]:
                self._update_clusters()
            
            # Update heatmap if enabled
            if self.config["enable_heatmap"]:
                self._update_heatmap()
        else:
            # Update existing agent
            agent = self.agents[agent_id]
            
            # Update properties
            if "type" in state:
                agent["type"] = state["type"]
            
            if "name" in state:
                agent["name"] = state["name"]
            
            if "capabilities" in state:
                agent["capabilities"] = state["capabilities"]
            
            if "state" in state:
                agent["state"] = state["state"]
            
            if "tags" in state:
                agent["tags"] = state["tags"]
            
            if "data" in state:
                agent["data"] = {**agent.get("data", {}), **state["data"]}
            
            # Update color based on new state
            agent["color"] = self._get_agent_color(state)
            
            # Update last activity
            agent["last_activity"] = current_time
            
            # Update in rendering engine
            self.rendering_engine.update_swarm_agent(agent_id, agent)
            
            # Trigger agent updated event
            self._trigger_event("agent_updated", {
                "agent_id": agent_id,
                "agent": agent,
                "updates": state
            })
            
            # Check for relationship changes
            if "relationships" in state:
                # Remove existing relationships for this agent
                self._remove_agent_relationships(agent_id)
                
                # Add new relationships
                for rel in state["relationships"]:
                    self._add_relationship(agent_id, rel["target_id"], rel["type"], rel.get("strength", 1.0))
            
            # Update clusters if enabled
            if self.config["enable_clustering"]:
                self._update_clusters()
        
        # Update timeline if enabled
        if self.config["enable_timeline"]:
            self._update_timeline(agent_id, is_new)
    
    def _generate_random_position(self) -> Dict:
        """
        Generate a random position for a new agent.
        
        Returns:
            Position dictionary
        """
        return {
            "x": (math.random() - 0.5) * 500,
            "y": (math.random() - 0.5) * 500
        }
    
    def _get_agent_color(self, state: Dict) -> str:
        """
        Get the color for an agent based on its state.
        
        Args:
            state: Agent state data
            
        Returns:
            Color string
        """
        agent_state = state.get("state", "idle")
        
        if agent_state == "inactive":
            return self.config["color_scheme"]["nodes"]["inactive"]
        
        # Check if agent is selected
        if state.get("id") in self.selected_agents:
            return self.config["color_scheme"]["nodes"]["selected"]
        
        # Check if agent is highlighted
        if state.get("id") in self.highlighted_agents:
            return self.config["color_scheme"]["nodes"]["highlighted"]
        
        # Use default color
        return self.config["color_scheme"]["nodes"]["default"]
    
    def _add_relationship(self, source_id: str, target_id: str, relationship_type: str, strength: float = 1.0) -> None:
        """
        Add a relationship between agents.
        
        Args:
            source_id: Source agent identifier
            target_id: Target agent identifier
            relationship_type: Relationship type
            strength: Relationship strength (0.0-1.0)
        """
        # Skip if either agent doesn't exist
        if source_id not in self.agents or target_id not in self.agents:
            return
        
        # Create relationship ID
        relationship_id = f"{source_id}_{target_id}"
        
        # Create relationship object
        relationship = {
            "id": relationship_id,
            "source": source_id,
            "target": target_id,
            "type": relationship_type,
            "strength": strength,
            "color": self._get_relationship_color(relationship_type),
            "width": self.config["edge_width"] * strength,
            "creation_time": time.time()
        }
        
        # Add to relationships dictionary
        self.relationships[relationship_id] = relationship
        
        # Add to rendering engine
        self.rendering_engine.add_swarm_relationship(relationship_id, relationship)
        
        # Trigger relationship added event
        self._trigger_event("relationship_added", {
            "relationship_id": relationship_id,
            "relationship": relationship
        })
    
    def _get_relationship_color(self, relationship_type: str) -> str:
        """
        Get the color for a relationship based on its type.
        
        Args:
            relationship_type: Relationship type
            
        Returns:
            Color string
        """
        if relationship_type in self.config["color_scheme"]["edges"]:
            return self.config["color_scheme"]["edges"][relationship_type]
        
        return self.config["color_scheme"]["edges"]["default"]
    
    def _remove_agent_relationships(self, agent_id: str) -> None:
        """
        Remove all relationships for an agent.
        
        Args:
            agent_id: Agent identifier
        """
        # Find relationships to remove
        relationships_to_remove = []
        for rel_id, rel in self.relationships.items():
            if rel["source"] == agent_id or rel["target"] == agent_id:
                relationships_to_remove.append(rel_id)
        
        # Remove relationships
        for rel_id in relationships_to_remove:
            self._remove_relationship(rel_id)
    
    def _remove_relationship(self, relationship_id: str) -> None:
        """
        Remove a relationship.
        
        Args:
            relationship_id: Relationship identifier
        """
        if relationship_id not in self.relationships:
            return
        
        # Get relationship
        relationship = self.relationships.pop(relationship_id)
        
        # Remove from rendering engine
        self.rendering_engine.remove_swarm_relationship(relationship_id)
        
        # Trigger relationship removed event
        self._trigger_event("relationship_removed", {
            "relationship_id": relationship_id,
            "relationship": relationship
        })
    
    def _visualize_communication(self, source_id: str, target_id: str, message_type: str, message: Dict) -> None:
        """
        Visualize a communication between agents.
        
        Args:
            source_id: Source agent identifier
            target_id: Target agent identifier
            message_type: Message type
            message: Message data
        """
        # Generate communication ID
        communication_id = str(uuid.uuid4())
        
        # Create communication object
        communication = {
            "id": communication_id,
            "source": source_id,
            "target": target_id,
            "type": message_type,
            "message": message,
            "color": self._get_communication_color(message_type),
            "creation_time": time.time(),
            "fade_time": self.config["communication_fade_time"]
        }
        
        # Add to communications list
        self.communications.append(communication)
        
        # Add to rendering engine
        self.rendering_engine.add_swarm_communication(communication_id, communication)
        
        # Schedule removal after fade time
        # In a real implementation, this would use a timer or animation system
        # For this example, we'll rely on periodic updates
        
        # Trigger communication visualized event
        self._trigger_event("communication_visualized", {
            "communication_id": communication_id,
            "communication": communication
        })
        
        # Update agent activity timestamps
        if source_id in self.agents:
            self.agents[source_id]["last_activity"] = time.time()
            self.rendering_engine.update_swarm_agent(source_id, self.agents[source_id])
        
        if target_id in self.agents:
            self.agents[target_id]["last_activity"] = time.time()
            self.rendering_engine.update_swarm_agent(target_id, self.agents[target_id])
    
    def _get_communication_color(self, message_type: str) -> str:
        """
        Get the color for a communication based on its type.
        
        Args:
            message_type: Message type
            
        Returns:
            Color string
        """
        if message_type == "request":
            return self.config["color_scheme"]["edges"]["communication"]
        elif message_type == "response":
            return self.config["color_scheme"]["edges"]["collaboration"]
        elif message_type == "command":
            return self.config["color_scheme"]["edges"]["delegation"]
        else:
            return self.config["color_scheme"]["edges"]["default"]
    
    def _update_clusters(self) -> None:
        """Update agent clusters."""
        try:
            # Skip if clustering is disabled
            if not self.config["enable_clustering"]:
                return
            
            # Simple clustering based on agent tags and capabilities
            clusters = {}
            
            # Group agents by tags
            for agent_id, agent in self.agents.items():
                # Skip agents that don't pass the filter
                if not self._agent_passes_filter(agent):
                    continue
                
                # Use the first tag as cluster key (simplified approach)
                if agent["tags"]:
                    cluster_key = agent["tags"][0]
                elif agent["capabilities"]:
                    cluster_key = agent["capabilities"][0]
                else:
                    cluster_key = agent["type"]
                
                if cluster_key not in clusters:
                    clusters[cluster_key] = []
                
                clusters[cluster_key].append(agent_id)
            
            # Update clusters
            self.clusters = {}
            cluster_index = 0
            
            for cluster_key, agent_ids in clusters.items():
                # Only create clusters with multiple agents
                if len(agent_ids) > 1:
                    cluster_id = f"cluster_{cluster_index}"
                    cluster_index += 1
                    
                    # Create cluster
                    self.clusters[cluster_id] = {
                        "id": cluster_id,
                        "key": cluster_key,
                        "agents": agent_ids,
                        "size": len(agent_ids),
                        "color": self.config["color_scheme"]["clusters"][cluster_index % len(self.config["color_scheme"]["clusters"])],
                        "position": self._calculate_cluster_center(agent_ids)
                    }
            
            # Update rendering engine
            self.rendering_engine.update_swarm_clusters(self.clusters)
            
            # Trigger clusters updated event
            self._trigger_event("clusters_updated", {
                "clusters": self.clusters
            })
        except Exception as e:
            logger.error(f"Error updating clusters: {str(e)}")
    
    def _calculate_cluster_center(self, agent_ids: List[str]) -> Dict:
        """
        Calculate the center position of a cluster.
        
        Args:
            agent_ids: List of agent identifiers
            
        Returns:
            Center position
        """
        if not agent_ids:
            return {"x": 0, "y": 0}
        
        total_x = 0
        total_y = 0
        count = 0
        
        for agent_id in agent_ids:
            if agent_id in self.agents:
                total_x += self.agents[agent_id]["position"]["x"]
                total_y += self.agents[agent_id]["position"]["y"]
                count += 1
        
        if count == 0:
            return {"x": 0, "y": 0}
        
        return {
            "x": total_x / count,
            "y": total_y / count
        }
    
    def _update_heatmap(self) -> None:
        """Update activity heatmap."""
        try:
            # Skip if heatmap is disabled
            if not self.config["enable_heatmap"]:
                return
            
            # Create a grid for the heatmap
            resolution = self.config["heatmap_resolution"]
            grid = [[0 for _ in range(resolution)] for _ in range(resolution)]
            
            # Calculate bounds
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            
            for agent in self.agents.values():
                # Skip agents that don't pass the filter
                if not self._agent_passes_filter(agent):
                    continue
                
                pos = agent["position"]
                min_x = min(min_x, pos["x"])
                min_y = min(min_y, pos["y"])
                max_x = max(max_x, pos["x"])
                max_y = max(max_y, pos["y"])
            
            # Ensure valid bounds
            if min_x == float('inf') or min_y == float('inf') or max_x == float('-inf') or max_y == float('-inf'):
                min_x = min_y = -500
                max_x = max_y = 500
            
            # Add padding
            padding = 50
            min_x -= padding
            min_y -= padding
            max_x += padding
            max_y += padding
            
            # Calculate cell size
            cell_width = (max_x - min_x) / resolution
            cell_height = (max_y - min_y) / resolution
            
            # Fill grid with agent activity
            current_time = time.time()
            for agent in self.agents.values():
                # Skip agents that don't pass the filter
                if not self._agent_passes_filter(agent):
                    continue
                
                pos = agent["position"]
                
                # Calculate grid cell
                cell_x = int((pos["x"] - min_x) / cell_width)
                cell_y = int((pos["y"] - min_y) / cell_height)
                
                # Ensure within bounds
                cell_x = max(0, min(resolution - 1, cell_x))
                cell_y = max(0, min(resolution - 1, cell_y))
                
                # Calculate activity value (higher for recent activity)
                activity_age = current_time - agent["last_activity"]
                activity_value = max(0, 1.0 - activity_age / 60.0)  # Normalize to 0-1 over 60 seconds
                
                # Add to grid
                grid[cell_y][cell_x] += activity_value
            
            # Normalize grid values
            max_value = 0
            for row in grid:
                max_value = max(max_value, max(row))
            
            if max_value > 0:
                for y in range(resolution):
                    for x in range(resolution):
                        grid[y][x] /= max_value
            
            # Create heatmap data
            self.heatmap_data = {
                "grid": grid,
                "bounds": {
                    "min_x": min_x,
                    "min_y": min_y,
                    "max_x": max_x,
                    "max_y": max_y
                },
                "resolution": resolution,
                "timestamp": current_time
            }
            
            # Update rendering engine
            self.rendering_engine.update_swarm_heatmap(self.heatmap_data)
            
            # Trigger heatmap updated event
            self._trigger_event("heatmap_updated", {
                "heatmap": self.heatmap_data
            })
        except Exception as e:
            logger.error(f"Error updating heatmap: {str(e)}")
    
    def _update_timeline(self, agent_id: str, is_new: bool) -> None:
        """
        Update the activity timeline.
        
        Args:
            agent_id: Agent identifier
            is_new: Whether the agent is new
        """
        try:
            # Skip if timeline is disabled
            if not self.config["enable_timeline"]:
                return
            
            current_time = time.time()
            
            # Add event to timeline
            event_type = "agent_added" if is_new else "agent_updated"
            
            timeline_event = {
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "type": event_type,
                "timestamp": current_time,
                "data": {
                    "agent": self.agents[agent_id]
                }
            }
            
            # Add to timeline data
            self.timeline_data.append(timeline_event)
            
            # Limit timeline length
            window_start = current_time - self.config["timeline_window"]
            self.timeline_data = [event for event in self.timeline_data if event["timestamp"] >= window_start]
            
            # Update rendering engine
            self.rendering_engine.update_swarm_timeline(self.timeline_data)
            
            # Trigger timeline updated event
            self._trigger_event("timeline_updated", {
                "timeline": self.timeline_data
            })
        except Exception as e:
            logger.error(f"Error updating timeline: {str(e)}")
    
    def _clean_old_communications(self) -> None:
        """Remove old communications."""
        try:
            current_time = time.time()
            communications_to_remove = []
            
            for comm in self.communications:
                fade_time = comm["fade_time"]
                age = current_time - comm["creation_time"]
                
                if age > fade_time:
                    communications_to_remove.append(comm["id"])
            
            # Remove old communications
            for comm_id in communications_to_remove:
                self._remove_communication(comm_id)
        except Exception as e:
            logger.error(f"Error cleaning old communications: {str(e)}")
    
    def _remove_communication(self, communication_id: str) -> None:
        """
        Remove a communication.
        
        Args:
            communication_id: Communication identifier
        """
        # Find the communication
        for i, comm in enumerate(self.communications):
            if comm["id"] == communication_id:
                # Remove from list
                self.communications.pop(i)
                break
        
        # Remove from rendering engine
        self.rendering_engine.remove_swarm_communication(communication_id)
    
    def _agent_passes_filter(self, agent: Dict) -> bool:
        """
        Check if an agent passes the current filter.
        
        Args:
            agent: Agent data
            
        Returns:
            Boolean indicating if the agent passes the filter
        """
        # If no filters are set, all agents pass
        if not self.current_filter["agent_types"] and not self.current_filter["capabilities"] and not self.current_filter["states"] and not self.current_filter["tags"]:
            return True
        
        # Check agent type
        if self.current_filter["agent_types"] and agent["type"] not in self.current_filter["agent_types"]:
            return False
        
        # Check capabilities
        if self.current_filter["capabilities"]:
            has_capability = False
            for capability in self.current_filter["capabilities"]:
                if capability in agent["capabilities"]:
                    has_capability = True
                    break
            if not has_capability:
                return False
        
        # Check state
        if self.current_filter["states"] and agent["state"] not in self.current_filter["states"]:
            return False
        
        # Check tags
        if self.current_filter["tags"]:
            has_tag = False
            for tag in self.current_filter["tags"]:
                if tag in agent["tags"]:
                    has_tag = True
                    break
            if not has_tag:
                return False
        
        return True
    
    def _trigger_event(self, event_type: str, data: Dict) -> None:
        """
        Trigger an event.
        
        Args:
            event_type: Event type
            data: Event data
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in {event_type} event handler: {str(e)}")
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler.
        
        Args:
            event_type: Event type
            handler: Event handler function
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            logger.debug(f"Registered {event_type} event handler")
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def unregister_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Unregister an event handler.
        
        Args:
            event_type: Event type
            handler: Event handler function
        """
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.debug(f"Unregistered {event_type} event handler")
    
    def update(self) -> None:
        """Update the Swarm Lens (called periodically)."""
        try:
            current_time = time.time()
            
            # Skip if not enough time has passed since last update
            if current_time - self.last_update_time < 0.1:  # 10 updates per second max
                return
            
            self.last_update_time = current_time
            
            # Clean old communications
            self._clean_old_communications()
            
            # Update physics if enabled
            if self.config["enable_physics"]:
                self._update_physics()
            
            # Update clusters if enabled
            if self.config["enable_clustering"]:
                self._update_clusters()
            
            # Update heatmap if enabled
            if self.config["enable_heatmap"]:
                self._update_heatmap()
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
    
    def _update_physics(self) -> None:
        """Update agent positions based on physics simulation."""
        try:
            # Physics settings
            settings = self.config["physics_settings"]
            gravity = settings["gravity"]
            spring_length = settings["spring_length"]
            spring_coefficient = settings["spring_coefficient"]
            damping = settings["damping"]
            avoidance = settings["avoidance"]
            
            # Calculate forces for each agent
            forces = {agent_id: {"x": 0, "y": 0} for agent_id in self.agents}
            
            # Apply spring forces for relationships
            for rel in self.relationships.values():
                source_id = rel["source"]
                target_id = rel["target"]
                
                if source_id not in self.agents or target_id not in self.agents:
                    continue
                
                source = self.agents[source_id]
                target = self.agents[target_id]
                
                # Calculate distance
                dx = target["position"]["x"] - source["position"]["x"]
                dy = target["position"]["y"] - source["position"]["y"]
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance == 0:
                    continue
                
                # Normalize direction
                nx = dx / distance
                ny = dy / distance
                
                # Calculate spring force
                force = (distance - spring_length) * spring_coefficient * rel["strength"]
                
                # Apply force to both agents
                forces[source_id]["x"] += nx * force
                forces[source_id]["y"] += ny * force
                forces[target_id]["x"] -= nx * force
                forces[target_id]["y"] -= ny * force
            
            # Apply repulsive forces between all agents
            for agent1_id, agent1 in self.agents.items():
                for agent2_id, agent2 in self.agents.items():
                    if agent1_id == agent2_id:
                        continue
                    
                    # Calculate distance
                    dx = agent2["position"]["x"] - agent1["position"]["x"]
                    dy = agent2["position"]["y"] - agent1["position"]["y"]
                    distance_squared = dx * dx + dy * dy
                    
                    if distance_squared < 1:
                        distance_squared = 1
                    
                    # Calculate repulsive force
                    force = avoidance / distance_squared
                    
                    # Normalize direction
                    distance = math.sqrt(distance_squared)
                    nx = dx / distance
                    ny = dy / distance
                    
                    # Apply force
                    forces[agent1_id]["x"] -= nx * force
                    forces[agent1_id]["y"] -= ny * force
            
            # Apply gravity towards center
            for agent_id, agent in self.agents.items():
                # Calculate direction to center
                dx = -agent["position"]["x"]
                dy = -agent["position"]["y"]
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance > 0:
                    # Normalize direction
                    nx = dx / distance
                    ny = dy / distance
                    
                    # Apply gravity force
                    forces[agent_id]["x"] += nx * gravity
                    forces[agent_id]["y"] += ny * gravity
            
            # Update velocities and positions
            for agent_id, agent in self.agents.items():
                # Apply damping to current velocity
                agent["velocity"]["x"] *= damping
                agent["velocity"]["y"] *= damping
                
                # Apply forces to velocity
                agent["velocity"]["x"] += forces[agent_id]["x"]
                agent["velocity"]["y"] += forces[agent_id]["y"]
                
                # Apply velocity to position
                agent["position"]["x"] += agent["velocity"]["x"]
                agent["position"]["y"] += agent["velocity"]["y"]
                
                # Update in rendering engine
                self.rendering_engine.update_swarm_agent(agent_id, agent)
        except Exception as e:
            logger.error(f"Error updating physics: {str(e)}")
    
    def set_filter(self, filter_data: Dict) -> None:
        """
        Set the agent filter.
        
        Args:
            filter_data: Filter configuration
        """
        try:
            logger.info(f"Setting agent filter: {filter_data}")
            
            # Update current filter
            self.current_filter = {
                **self.config["default_filter"],
                **filter_data
            }
            
            # Update rendering engine
            self.rendering_engine.update_swarm_filter(self.current_filter)
            
            # Trigger filter changed event
            self._trigger_event("filter_changed", {
                "filter": self.current_filter
            })
            
            # Update clusters
            if self.config["enable_clustering"]:
                self._update_clusters()
            
            # Update heatmap
            if self.config["enable_heatmap"]:
                self._update_heatmap()
        except Exception as e:
            logger.error(f"Error setting filter: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to set filter: {str(e)}"
            })
    
    def get_filter(self) -> Dict:
        """
        Get the current agent filter.
        
        Returns:
            Current filter configuration
        """
        return self.current_filter.copy()
    
    def set_layout(self, layout: str) -> None:
        """
        Set the layout algorithm.
        
        Args:
            layout: Layout algorithm name
        """
        try:
            logger.info(f"Setting layout: {layout}")
            
            # Update current layout
            self.current_layout = layout
            
            # Apply layout
            if layout == "force_directed":
                # Already using force-directed layout via physics
                pass
            elif layout == "circular":
                self._apply_circular_layout()
            elif layout == "grid":
                self._apply_grid_layout()
            elif layout == "radial":
                self._apply_radial_layout()
            else:
                logger.warning(f"Unknown layout: {layout}")
                return
            
            # Update rendering engine
            self.rendering_engine.update_swarm_layout(layout)
            
            # Trigger layout changed event
            self._trigger_event("layout_changed", {
                "layout": layout
            })
        except Exception as e:
            logger.error(f"Error setting layout: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to set layout: {str(e)}"
            })
    
    def _apply_circular_layout(self) -> None:
        """Apply circular layout to agents."""
        try:
            # Get filtered agents
            filtered_agents = [agent for agent_id, agent in self.agents.items() if self._agent_passes_filter(agent)]
            
            if not filtered_agents:
                return
            
            # Calculate circle
            count = len(filtered_agents)
            radius = 200 + count * 10  # Scale radius with agent count
            center_x = 0
            center_y = 0
            
            # Position agents in a circle
            for i, agent in enumerate(filtered_agents):
                angle = 2 * math.pi * i / count
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                
                # Update position
                agent["position"]["x"] = x
                agent["position"]["y"] = y
                
                # Reset velocity
                agent["velocity"]["x"] = 0
                agent["velocity"]["y"] = 0
                
                # Update in rendering engine
                self.rendering_engine.update_swarm_agent(agent["id"], agent)
        except Exception as e:
            logger.error(f"Error applying circular layout: {str(e)}")
    
    def _apply_grid_layout(self) -> None:
        """Apply grid layout to agents."""
        try:
            # Get filtered agents
            filtered_agents = [agent for agent_id, agent in self.agents.items() if self._agent_passes_filter(agent)]
            
            if not filtered_agents:
                return
            
            # Calculate grid dimensions
            count = len(filtered_agents)
            cols = math.ceil(math.sqrt(count))
            rows = math.ceil(count / cols)
            
            # Calculate cell size
            cell_width = 100
            cell_height = 100
            
            # Calculate grid origin (top-left)
            origin_x = -((cols - 1) * cell_width) / 2
            origin_y = -((rows - 1) * cell_height) / 2
            
            # Position agents in a grid
            for i, agent in enumerate(filtered_agents):
                col = i % cols
                row = i // cols
                
                x = origin_x + col * cell_width
                y = origin_y + row * cell_height
                
                # Update position
                agent["position"]["x"] = x
                agent["position"]["y"] = y
                
                # Reset velocity
                agent["velocity"]["x"] = 0
                agent["velocity"]["y"] = 0
                
                # Update in rendering engine
                self.rendering_engine.update_swarm_agent(agent["id"], agent)
        except Exception as e:
            logger.error(f"Error applying grid layout: {str(e)}")
    
    def _apply_radial_layout(self) -> None:
        """Apply radial layout to agents based on clusters."""
        try:
            # Get filtered agents
            filtered_agents = [agent for agent_id, agent in self.agents.items() if self._agent_passes_filter(agent)]
            
            if not filtered_agents:
                return
            
            # Group agents by cluster
            clusters = {}
            for agent in filtered_agents:
                # Use the first tag as cluster key (simplified approach)
                if agent["tags"]:
                    cluster_key = agent["tags"][0]
                elif agent["capabilities"]:
                    cluster_key = agent["capabilities"][0]
                else:
                    cluster_key = agent["type"]
                
                if cluster_key not in clusters:
                    clusters[cluster_key] = []
                
                clusters[cluster_key].append(agent)
            
            # Calculate layout
            cluster_count = len(clusters)
            cluster_radius = 300  # Distance from center to cluster centers
            
            # Position clusters in a circle
            cluster_index = 0
            for cluster_key, cluster_agents in clusters.items():
                # Calculate cluster center
                angle = 2 * math.pi * cluster_index / cluster_count
                center_x = cluster_radius * math.cos(angle)
                center_y = cluster_radius * math.sin(angle)
                
                # Calculate agent positions within cluster
                agent_count = len(cluster_agents)
                agent_radius = 50 + agent_count * 5  # Scale with agent count
                
                for i, agent in enumerate(cluster_agents):
                    if agent_count == 1:
                        # Single agent at cluster center
                        x = center_x
                        y = center_y
                    else:
                        # Multiple agents in a circle around cluster center
                        agent_angle = 2 * math.pi * i / agent_count
                        x = center_x + agent_radius * math.cos(agent_angle)
                        y = center_y + agent_radius * math.sin(agent_angle)
                    
                    # Update position
                    agent["position"]["x"] = x
                    agent["position"]["y"] = y
                    
                    # Reset velocity
                    agent["velocity"]["x"] = 0
                    agent["velocity"]["y"] = 0
                    
                    # Update in rendering engine
                    self.rendering_engine.update_swarm_agent(agent["id"], agent)
                
                cluster_index += 1
        except Exception as e:
            logger.error(f"Error applying radial layout: {str(e)}")
    
    def select_agent(self, agent_id: str, multi_select: bool = False) -> bool:
        """
        Select an agent.
        
        Args:
            agent_id: Agent identifier
            multi_select: Whether to add to current selection
            
        Returns:
            Boolean indicating success
        """
        try:
            if agent_id not in self.agents:
                logger.warning(f"Agent not found: {agent_id}")
                return False
            
            logger.info(f"Selecting agent: {agent_id}")
            
            # Clear selection if not multi-select
            if not multi_select:
                self.selected_agents = []
            
            # Add to selection if not already selected
            if agent_id not in self.selected_agents:
                self.selected_agents.append(agent_id)
            
            # Update agent color
            agent = self.agents[agent_id]
            agent["color"] = self.config["color_scheme"]["nodes"]["selected"]
            
            # Update in rendering engine
            self.rendering_engine.update_swarm_agent(agent_id, agent)
            
            # Trigger selection changed event
            self._trigger_event("selection_changed", {
                "selected_agents": self.selected_agents
            })
            
            # Create a capsule for the agent
            self._create_agent_capsule(agent_id)
            
            return True
        except Exception as e:
            logger.error(f"Error selecting agent: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to select agent: {str(e)}",
                "agent_id": agent_id
            })
            return False
    
    def _create_agent_capsule(self, agent_id: str) -> None:
        """
        Create a capsule for an agent.
        
        Args:
            agent_id: Agent identifier
        """
        # Check if agent exists
        if agent_id not in self.agents:
            return
        
        # Check if capsule already exists
        capsule_id = f"agent_{agent_id}"
        if self.capsule_manager.has_capsule(capsule_id):
            # Just focus the existing capsule
            self.capsule_manager.focus_capsule(capsule_id)
            return
        
        # Get agent data
        agent = self.agents[agent_id]
        
        # Create capsule data
        capsule_data = {
            "id": capsule_id,
            "type": "agent",
            "title": agent["name"],
            "description": f"Agent of type {agent['type']}",
            "icon": "robot",
            "color": agent["color"],
            "source": {
                "type": "agent",
                "id": agent_id
            },
            "actions": [
                {
                    "id": "focus",
                    "label": "Focus",
                    "icon": "search"
                },
                {
                    "id": "message",
                    "label": "Message",
                    "icon": "comment"
                },
                {
                    "id": "details",
                    "label": "Details",
                    "icon": "info-circle"
                }
            ],
            "properties": {
                "type": agent["type"],
                "state": agent["state"],
                "capabilities": agent["capabilities"],
                "tags": agent["tags"],
                "creation_time": agent["creation_time"],
                "last_activity": agent["last_activity"]
            }
        }
        
        # Create the capsule
        self.capsule_manager.create_capsule(capsule_data)
    
    def deselect_agent(self, agent_id: str) -> bool:
        """
        Deselect an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if agent_id not in self.agents:
                logger.warning(f"Agent not found: {agent_id}")
                return False
            
            logger.info(f"Deselecting agent: {agent_id}")
            
            # Remove from selection
            if agent_id in self.selected_agents:
                self.selected_agents.remove(agent_id)
            
            # Update agent color
            agent = self.agents[agent_id]
            agent["color"] = self._get_agent_color(agent)
            
            # Update in rendering engine
            self.rendering_engine.update_swarm_agent(agent_id, agent)
            
            # Trigger selection changed event
            self._trigger_event("selection_changed", {
                "selected_agents": self.selected_agents
            })
            
            return True
        except Exception as e:
            logger.error(f"Error deselecting agent: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to deselect agent: {str(e)}",
                "agent_id": agent_id
            })
            return False
    
    def clear_selection(self) -> None:
        """Clear the current selection."""
        try:
            logger.info("Clearing selection")
            
            # Update colors for all selected agents
            for agent_id in self.selected_agents:
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    agent["color"] = self._get_agent_color(agent)
                    self.rendering_engine.update_swarm_agent(agent_id, agent)
            
            # Clear selection
            self.selected_agents = []
            
            # Trigger selection changed event
            self._trigger_event("selection_changed", {
                "selected_agents": []
            })
        except Exception as e:
            logger.error(f"Error clearing selection: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to clear selection: {str(e)}"
            })
    
    def highlight_agent(self, agent_id: str) -> bool:
        """
        Highlight an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if agent_id not in self.agents:
                logger.warning(f"Agent not found: {agent_id}")
                return False
            
            logger.info(f"Highlighting agent: {agent_id}")
            
            # Add to highlighted agents
            if agent_id not in self.highlighted_agents:
                self.highlighted_agents.append(agent_id)
            
            # Update agent color if not selected
            if agent_id not in self.selected_agents:
                agent = self.agents[agent_id]
                agent["color"] = self.config["color_scheme"]["nodes"]["highlighted"]
                self.rendering_engine.update_swarm_agent(agent_id, agent)
            
            return True
        except Exception as e:
            logger.error(f"Error highlighting agent: {str(e)}")
            return False
    
    def unhighlight_agent(self, agent_id: str) -> bool:
        """
        Remove highlight from an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if agent_id not in self.agents:
                logger.warning(f"Agent not found: {agent_id}")
                return False
            
            logger.info(f"Unhighlighting agent: {agent_id}")
            
            # Remove from highlighted agents
            if agent_id in self.highlighted_agents:
                self.highlighted_agents.remove(agent_id)
            
            # Update agent color if not selected
            if agent_id not in self.selected_agents:
                agent = self.agents[agent_id]
                agent["color"] = self._get_agent_color(agent)
                self.rendering_engine.update_swarm_agent(agent_id, agent)
            
            return True
        except Exception as e:
            logger.error(f"Error unhighlighting agent: {str(e)}")
            return False
    
    def clear_highlights(self) -> None:
        """Clear all highlights."""
        try:
            logger.info("Clearing highlights")
            
            # Update colors for all highlighted agents
            for agent_id in self.highlighted_agents:
                if agent_id in self.agents and agent_id not in self.selected_agents:
                    agent = self.agents[agent_id]
                    agent["color"] = self._get_agent_color(agent)
                    self.rendering_engine.update_swarm_agent(agent_id, agent)
            
            # Clear highlights
            self.highlighted_agents = []
        except Exception as e:
            logger.error(f"Error clearing highlights: {str(e)}")
    
    def focus_on_agent(self, agent_id: str) -> bool:
        """
        Focus the view on an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if agent_id not in self.agents:
                logger.warning(f"Agent not found: {agent_id}")
                return False
            
            logger.info(f"Focusing on agent: {agent_id}")
            
            # Get agent position
            agent = self.agents[agent_id]
            position = agent["position"]
            
            # Set pan offset to center on agent
            self.pan_offset = {
                "x": -position["x"],
                "y": -position["y"]
            }
            
            # Update rendering engine
            self.rendering_engine.set_swarm_view({
                "zoom": self.zoom_level,
                "pan": self.pan_offset
            })
            
            return True
        except Exception as e:
            logger.error(f"Error focusing on agent: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to focus on agent: {str(e)}",
                "agent_id": agent_id
            })
            return False
    
    def set_zoom(self, zoom_level: float) -> None:
        """
        Set the zoom level.
        
        Args:
            zoom_level: Zoom level
        """
        try:
            logger.debug(f"Setting zoom level: {zoom_level}")
            
            # Clamp zoom level
            zoom_level = max(0.1, min(5.0, zoom_level))
            
            # Update zoom level
            self.zoom_level = zoom_level
            
            # Update rendering engine
            self.rendering_engine.set_swarm_view({
                "zoom": self.zoom_level,
                "pan": self.pan_offset
            })
        except Exception as e:
            logger.error(f"Error setting zoom: {str(e)}")
    
    def set_pan(self, pan_offset: Dict) -> None:
        """
        Set the pan offset.
        
        Args:
            pan_offset: Pan offset
        """
        try:
            logger.debug(f"Setting pan offset: {pan_offset}")
            
            # Update pan offset
            self.pan_offset = pan_offset
            
            # Update rendering engine
            self.rendering_engine.set_swarm_view({
                "zoom": self.zoom_level,
                "pan": self.pan_offset
            })
        except Exception as e:
            logger.error(f"Error setting pan: {str(e)}")
    
    def get_agent_details(self, agent_id: str) -> Optional[Dict]:
        """
        Get detailed information about an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent details or None if not found
        """
        try:
            if agent_id not in self.agents:
                logger.warning(f"Agent not found: {agent_id}")
                return None
            
            logger.info(f"Getting agent details: {agent_id}")
            
            # Get agent data
            agent = self.agents[agent_id]
            
            # Get relationships
            relationships = []
            for rel_id, rel in self.relationships.items():
                if rel["source"] == agent_id or rel["target"] == agent_id:
                    relationships.append(rel)
            
            # Get recent communications
            communications = []
            for comm in self.communications:
                if comm["source"] == agent_id or comm["target"] == agent_id:
                    communications.append(comm)
            
            # Create details object
            details = {
                "agent": agent,
                "relationships": relationships,
                "communications": communications
            }
            
            # Get additional details from backend if available
            if self.config["enable_agent_details"]:
                response = self.agent_protocol.send_request_sync(
                    {
                        "request_type": "get_agent_details",
                        "agent_id": agent_id
                    },
                    {
                        "type": "agent",
                        "id": "agent_manager",
                        "protocol": "a2a"
                    }
                )
                
                if "error" not in response or not response["error"]:
                    additional_details = response.get("payload", {})
                    details["additional"] = additional_details
            
            return details
        except Exception as e:
            logger.error(f"Error getting agent details: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to get agent details: {str(e)}",
                "agent_id": agent_id
            })
            return None
    
    def get_cluster_details(self, cluster_id: str) -> Optional[Dict]:
        """
        Get detailed information about a cluster.
        
        Args:
            cluster_id: Cluster identifier
            
        Returns:
            Cluster details or None if not found
        """
        try:
            if cluster_id not in self.clusters:
                logger.warning(f"Cluster not found: {cluster_id}")
                return None
            
            logger.info(f"Getting cluster details: {cluster_id}")
            
            # Get cluster data
            cluster = self.clusters[cluster_id]
            
            # Get agents in cluster
            agents = []
            for agent_id in cluster["agents"]:
                if agent_id in self.agents:
                    agents.append(self.agents[agent_id])
            
            # Create details object
            details = {
                "cluster": cluster,
                "agents": agents
            }
            
            return details
        except Exception as e:
            logger.error(f"Error getting cluster details: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to get cluster details: {str(e)}",
                "cluster_id": cluster_id
            })
            return None
    
    def get_timeline_events(self, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[Dict]:
        """
        Get timeline events within a time range.
        
        Args:
            start_time: Optional start time (defaults to timeline window start)
            end_time: Optional end time (defaults to current time)
            
        Returns:
            List of timeline events
        """
        try:
            if not self.config["enable_timeline"]:
                return []
            
            current_time = time.time()
            
            # Set default time range
            if start_time is None:
                start_time = current_time - self.config["timeline_window"]
            
            if end_time is None:
                end_time = current_time
            
            # Filter events by time range
            events = [event for event in self.timeline_data if start_time <= event["timestamp"] <= end_time]
            
            return events
        except Exception as e:
            logger.error(f"Error getting timeline events: {str(e)}")
            return []
    
    def get_heatmap_data(self) -> Dict:
        """
        Get the current heatmap data.
        
        Returns:
            Heatmap data
        """
        return self.heatmap_data
    
    def get_agents(self) -> List[Dict]:
        """
        Get the list of agents.
        
        Returns:
            List of agent data
        """
        return list(self.agents.values())
    
    def get_relationships(self) -> List[Dict]:
        """
        Get the list of relationships.
        
        Returns:
            List of relationship data
        """
        return list(self.relationships.values())
    
    def get_clusters(self) -> List[Dict]:
        """
        Get the list of clusters.
        
        Returns:
            List of cluster data
        """
        return list(self.clusters.values())
    
    def clear(self) -> None:
        """Clear all data."""
        try:
            logger.info("Clearing Swarm Lens")
            
            # Clear data
            self.agents = {}
            self.relationships = {}
            self.communications = []
            self.clusters = {}
            self.selected_agents = []
            self.highlighted_agents = []
            self.heatmap_data = []
            self.timeline_data = []
            
            # Reset view
            self.zoom_level = 1.0
            self.pan_offset = {"x": 0, "y": 0}
            
            # Clear rendering engine
            self.rendering_engine.clear_swarm()
        except Exception as e:
            logger.error(f"Error clearing Swarm Lens: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to clear Swarm Lens: {str(e)}"
            })
    
    def shutdown(self) -> None:
        """Shutdown the Swarm Lens."""
        logger.info("Shutting down Swarm Lens")
        
        # Clear all data
        self.clear()
