"""
Protocol Visualizer Component for the UI/UX Layer

This component provides a visual representation of the communication protocols
(MCP, A2A) being used within the Industriverse ecosystem. It helps users
understand the flow of information and interactions between different layers,
agents, and models.

The Protocol Visualizer:
1. Visualizes MCP and A2A message flows in real-time
2. Represents layers, agents, and models as nodes
3. Shows message types, sources, targets, and payloads
4. Allows filtering and inspection of messages
5. Provides statistics on protocol usage and performance
6. Integrates with the Context Engine for contextual filtering

Author: Manus
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable
import time
import uuid

# Local imports
from ..core.rendering_engine.rendering_engine import RenderingEngine
from ..core.context_engine.context_engine import ContextEngine
from ..core.agent_ecosystem.agent_interaction_protocol import AgentInteractionProtocol, MessageType

# Configure logging
logger = logging.getLogger(__name__)

class ProtocolVisualizer:
    """
    Protocol Visualizer component for visualizing MCP and A2A message flows.
    """
    
    def __init__(
        self,
        rendering_engine: RenderingEngine,
        context_engine: ContextEngine,
        agent_protocol: AgentInteractionProtocol,
        config: Dict = None
    ):
        """
        Initialize the Protocol Visualizer.
        
        Args:
            rendering_engine: Rendering Engine instance
            context_engine: Context Engine instance
            agent_protocol: Agent Interaction Protocol instance
            config: Optional configuration dictionary
        """
        self.rendering_engine = rendering_engine
        self.context_engine = context_engine
        self.agent_protocol = agent_protocol
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "max_messages_to_display": 100,
            "node_size": 1.0,
            "message_speed": 5.0,
            "show_payloads": False,
            "default_filter": {
                "protocols": ["a2a", "mcp"],
                "message_types": ["request", "response", "event", "command"],
                "sources": [],
                "targets": []
            },
            "enable_statistics": True,
            "stats_update_interval": 5.0,  # seconds
            "layout_algorithm": "force_directed",
            "node_colors": {
                "ui": "#4CAF50",
                "agent": "#2196F3",
                "model": "#FFC107",
                "system": "#9E9E9E",
                "layer": "#E91E63"
            },
            "message_colors": {
                "request": "#FF9800",
                "response": "#8BC34A",
                "event": "#03A9F4",
                "state_update": "#CDDC39",
                "command": "#F44336",
                "notification": "#9C27B0",
                "error": "#B00020"
            }
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Current state
        self.nodes = {}
        self.edges = {}
        self.messages = []
        self.current_filter = self.config["default_filter"].copy()
        self.statistics = {
            "total_messages": 0,
            "messages_per_second": 0,
            "protocol_counts": {"a2a": 0, "mcp": 0},
            "type_counts": {},
            "active_nodes": 0,
            "active_edges": 0
        }
        self.last_stats_update = 0
        self.last_message_time = 0
        
        # Event handlers
        self.event_handlers = {
            "node_added": [],
            "node_removed": [],
            "message_visualized": [],
            "filter_changed": [],
            "stats_updated": []
        }
        
        # Register with context engine
        self.context_engine.register_context_listener(self._handle_context_change)
        
        # Register with agent protocol for all messages
        self.agent_protocol.register_message_handler(
            MessageType.REQUEST.value,
            self._handle_protocol_message,
            "*"
        )
        self.agent_protocol.register_message_handler(
            MessageType.RESPONSE.value,
            self._handle_protocol_message,
            "*"
        )
        self.agent_protocol.register_message_handler(
            MessageType.EVENT.value,
            self._handle_protocol_message,
            "*"
        )
        self.agent_protocol.register_message_handler(
            MessageType.STATE_UPDATE.value,
            self._handle_protocol_message,
            "*"
        )
        self.agent_protocol.register_message_handler(
            MessageType.COMMAND.value,
            self._handle_protocol_message,
            "*"
        )
        self.agent_protocol.register_message_handler(
            MessageType.NOTIFICATION.value,
            self._handle_protocol_message,
            "*"
        )
        self.agent_protocol.register_message_handler(
            MessageType.ERROR.value,
            self._handle_protocol_message,
            "*"
        )
        
        logger.info("Protocol Visualizer initialized")
    
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
        
        # Handle filter context changes
        if context_type == "protocol_filter":
            filter_data = event.get("data", {})
            self.set_filter(filter_data)
    
    def _handle_protocol_message(self, message: Dict) -> None:
        """
        Handle incoming protocol messages.
        
        Args:
            message: Protocol message
        """
        try:
            # Check if message passes the current filter
            if not self._filter_message(message):
                return
            
            # Add nodes if they don't exist
            source_node = self._add_or_update_node(message["source"])
            target_node = self._add_or_update_node(message["target"])
            
            # Add edge if it doesn't exist
            edge_id = f"{source_node["id"]}_{target_node["id"]}"
            if edge_id not in self.edges:
                self._add_edge(source_node, target_node)
            
            # Visualize the message
            self._visualize_message(message, source_node, target_node)
            
            # Update statistics
            self._update_statistics(message)
            
            # Trigger message visualized event
            self._trigger_event("message_visualized", {"message": message})
        except Exception as e:
            logger.error(f"Error handling protocol message: {str(e)}")
    
    def _filter_message(self, message: Dict) -> bool:
        """
        Check if a message passes the current filter.
        
        Args:
            message: Message to check
            
        Returns:
            Boolean indicating if the message passes the filter
        """
        # Filter by protocol
        protocol = message.get("metadata", {}).get("original_protocol", "unknown")
        if protocol not in self.current_filter["protocols"]:
            return False
        
        # Filter by message type
        message_type = message["type"]
        if message_type not in self.current_filter["message_types"]:
            return False
        
        # Filter by source ID
        source_id = message["source"]["id"]
        if self.current_filter["sources"] and source_id not in self.current_filter["sources"]:
            return False
        
        # Filter by target ID
        target_id = message["target"]["id"]
        if self.current_filter["targets"] and target_id not in self.current_filter["targets"]:
            return False
        
        return True
    
    def _add_or_update_node(self, node_data: Dict) -> Dict:
        """
        Add or update a node in the visualization.
        
        Args:
            node_data: Node data (from message source/target)
            
        Returns:
            Node definition
        """
        node_id = node_data["id"]
        node_type = node_data["type"]
        
        if node_id not in self.nodes:
            # Create new node
            node = {
                "id": node_id,
                "type": node_type,
                "label": node_id,
                "color": self.config["node_colors"].get(node_type, "#FFFFFF"),
                "size": self.config["node_size"],
                "last_activity": time.time()
            }
            
            # Add node to dictionary
            self.nodes[node_id] = node
            
            # Add node to rendering engine
            self.rendering_engine.add_graph_node(node_id, node)
            
            # Trigger node added event
            self._trigger_event("node_added", {"node": node})
            
            logger.debug(f"Added node: {node_id} ({node_type})")
        else:
            # Update existing node
            node = self.nodes[node_id]
            node["last_activity"] = time.time()
            
            # Update node in rendering engine (e.g., for activity indication)
            self.rendering_engine.update_graph_node(node_id, {"last_activity": node["last_activity"]})
        
        return node
    
    def _add_edge(self, source_node: Dict, target_node: Dict) -> None:
        """
        Add an edge between two nodes.
        
        Args:
            source_node: Source node definition
            target_node: Target node definition
        """
        edge_id = f"{source_node["id"]}_{target_node["id"]}"
        
        # Create edge definition
        edge = {
            "id": edge_id,
            "source": source_node["id"],
            "target": target_node["id"],
            "color": "#888888",
            "width": 1.0,
            "last_activity": time.time()
        }
        
        # Add edge to dictionary
        self.edges[edge_id] = edge
        
        # Add edge to rendering engine
        self.rendering_engine.add_graph_edge(edge_id, edge)
        
        logger.debug(f"Added edge: {edge_id}")
    
    def _visualize_message(self, message: Dict, source_node: Dict, target_node: Dict) -> None:
        """
        Visualize a message flowing between nodes.
        
        Args:
            message: Message to visualize
            source_node: Source node definition
            target_node: Target node definition
        """
        message_id = message["id"]
        message_type = message["type"]
        
        # Create message visualization data
        message_viz = {
            "id": message_id,
            "source": source_node["id"],
            "target": target_node["id"],
            "type": message_type,
            "color": self.config["message_colors"].get(message_type, "#FFFFFF"),
            "size": 0.5,
            "speed": self.config["message_speed"],
            "payload": message["payload"] if self.config["show_payloads"] else None,
            "timestamp": message["timestamp"]
        }
        
        # Add message to list
        self.messages.append(message_viz)
        
        # Limit message history
        if len(self.messages) > self.config["max_messages_to_display"]:
            # Remove oldest message visualization
            oldest_message = self.messages.pop(0)
            self.rendering_engine.remove_graph_message(oldest_message["id"])
        
        # Add message visualization to rendering engine
        self.rendering_engine.add_graph_message(message_id, message_viz)
        
        # Update edge activity
        edge_id = f"{source_node["id"]}_{target_node["id"]}"
        if edge_id in self.edges:
            self.edges[edge_id]["last_activity"] = time.time()
            self.rendering_engine.update_graph_edge(edge_id, {"last_activity": self.edges[edge_id]["last_activity"]})
    
    def _update_statistics(self, message: Dict) -> None:
        """
        Update protocol statistics.
        
        Args:
            message: New message
        """
        if not self.config["enable_statistics"]:
            return
        
        current_time = time.time()
        
        # Update total messages
        self.statistics["total_messages"] += 1
        
        # Update messages per second
        if self.last_message_time > 0:
            time_diff = current_time - self.last_message_time
            if time_diff > 0:
                current_mps = 1.0 / time_diff
                # Use moving average for smoother MPS
                self.statistics["messages_per_second"] = (
                    self.statistics["messages_per_second"] * 0.9 + current_mps * 0.1
                )
        self.last_message_time = current_time
        
        # Update protocol counts
        protocol = message.get("metadata", {}).get("original_protocol", "unknown")
        self.statistics["protocol_counts"][protocol] = (
            self.statistics["protocol_counts"].get(protocol, 0) + 1
        )
        
        # Update type counts
        message_type = message["type"]
        self.statistics["type_counts"][message_type] = (
            self.statistics["type_counts"].get(message_type, 0) + 1
        )
        
        # Update active nodes and edges
        self.statistics["active_nodes"] = len(self.nodes)
        self.statistics["active_edges"] = len(self.edges)
        
        # Trigger stats updated event periodically
        if current_time - self.last_stats_update > self.config["stats_update_interval"]:
            self._trigger_event("stats_updated", {"statistics": self.statistics})
            self.last_stats_update = current_time
    
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
    
    def set_filter(self, filter_data: Dict) -> None:
        """
        Set the message filter.
        
        Args:
            filter_data: Filter configuration
        """
        try:
            logger.info(f"Setting protocol filter: {filter_data}")
            
            # Update current filter
            self.current_filter = {
                **self.config["default_filter"],
                **filter_data
            }
            
            # Clear existing visualizations (optional, or update visibility)
            # self.clear_visualization()
            
            # Trigger filter changed event
            self._trigger_event("filter_changed", {"filter": self.current_filter})
        except Exception as e:
            logger.error(f"Error setting filter: {str(e)}")
    
    def get_filter(self) -> Dict:
        """
        Get the current message filter.
        
        Returns:
            Current filter configuration
        """
        return self.current_filter.copy()
    
    def get_statistics(self) -> Dict:
        """
        Get the current protocol statistics.
        
        Returns:
            Protocol statistics
        """
        return self.statistics.copy()
    
    def get_nodes(self) -> List[Dict]:
        """
        Get the list of current nodes.
        
        Returns:
            List of node definitions
        """
        return list(self.nodes.values())
    
    def get_edges(self) -> List[Dict]:
        """
        Get the list of current edges.
        
        Returns:
            List of edge definitions
        """
        return list(self.edges.values())
    
    def get_messages(self) -> List[Dict]:
        """
        Get the list of visualized messages.
        
        Returns:
            List of message visualization data
        """
        return self.messages.copy()
    
    def clear_visualization(self) -> None:
        """
        Clear the entire visualization.
        """
        try:
            logger.info("Clearing protocol visualization")
            
            # Clear internal state
            self.nodes = {}
            self.edges = {}
            self.messages = []
            
            # Clear rendering engine
            self.rendering_engine.clear_graph()
            
            # Reset statistics
            self.statistics = {
                "total_messages": 0,
                "messages_per_second": 0,
                "protocol_counts": {"a2a": 0, "mcp": 0},
                "type_counts": {},
                "active_nodes": 0,
                "active_edges": 0
            }
            self.last_stats_update = 0
            self.last_message_time = 0
        except Exception as e:
            logger.error(f"Error clearing visualization: {str(e)}")
    
    def set_layout_algorithm(self, algorithm: str) -> None:
        """
        Set the graph layout algorithm.
        
        Args:
            algorithm: Layout algorithm name (e.g., force_directed, circular)
        """
        try:
            logger.info(f"Setting layout algorithm: {algorithm}")
            
            # Update config
            self.config["layout_algorithm"] = algorithm
            
            # Update rendering engine
            self.rendering_engine.set_graph_layout(algorithm)
        except Exception as e:
            logger.error(f"Error setting layout algorithm: {str(e)}")
    
    def toggle_payload_visibility(self, show: bool) -> None:
        """
        Toggle visibility of message payloads.
        
        Args:
            show: Boolean indicating whether to show payloads
        """
        try:
            logger.info(f"Setting payload visibility: {show}")
            
            # Update config
            self.config["show_payloads"] = show
            
            # Update existing message visualizations (optional)
            # This might require re-rendering messages
        except Exception as e:
            logger.error(f"Error toggling payload visibility: {str(e)}")
    
    def shutdown(self) -> None:
        """Shutdown the Protocol Visualizer."""
        logger.info("Shutting down Protocol Visualizer")
        
        # Clear the visualization
        self.clear_visualization()
        
        # Unregister handlers (important to avoid memory leaks)
        # This requires the agent protocol to support unregistration
        # self.agent_protocol.unregister_message_handler(...) # Unregister all handlers
