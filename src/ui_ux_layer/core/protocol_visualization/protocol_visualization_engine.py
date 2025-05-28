"""
Protocol Visualization Engine for the Industriverse UI/UX Layer.

This module provides comprehensive visualization capabilities for MCP and A2A protocols,
enabling intuitive understanding of message flows, agent interactions, and protocol states
through the Universal Skin and Agent Capsules.

Author: Manus
"""

import logging
import time
import threading
import uuid
import json
import random
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass
import numpy as np

class ProtocolType(Enum):
    """Enumeration of protocol types."""
    MCP = "mcp"  # Model Context Protocol
    A2A = "a2a"  # Agent to Agent Protocol
    CUSTOM = "custom"  # Custom protocol type

class VisualizationMode(Enum):
    """Enumeration of visualization modes."""
    FLOW = "flow"  # Message flow visualization
    NETWORK = "network"  # Network/graph visualization
    TIMELINE = "timeline"  # Timeline visualization
    HIERARCHY = "hierarchy"  # Hierarchical visualization
    STATE = "state"  # State visualization
    CUSTOM = "custom"  # Custom visualization mode

class NodeType(Enum):
    """Enumeration of node types in protocol visualizations."""
    AGENT = "agent"  # Agent node
    MODEL = "model"  # Model node
    LAYER = "layer"  # Layer node
    SERVICE = "service"  # Service node
    ENDPOINT = "endpoint"  # Endpoint node
    GROUP = "group"  # Group node
    CUSTOM = "custom"  # Custom node type

class EdgeType(Enum):
    """Enumeration of edge types in protocol visualizations."""
    MESSAGE = "message"  # Message edge
    RELATIONSHIP = "relationship"  # Relationship edge
    FLOW = "flow"  # Flow edge
    DEPENDENCY = "dependency"  # Dependency edge
    CUSTOM = "custom"  # Custom edge type

@dataclass
class VisualizationNode:
    """Data class representing a node in a protocol visualization."""
    node_id: str  # Node identifier
    node_type: NodeType  # Node type
    label: str  # Node label
    description: Optional[str] = None  # Node description
    icon: Optional[str] = None  # Node icon
    position: Optional[Tuple[float, float, float]] = None  # 3D position
    size: Optional[float] = None  # Node size
    color: Optional[str] = None  # Node color
    state: Optional[str] = None  # Node state
    metadata: Dict[str, Any] = None  # Additional metadata
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class VisualizationEdge:
    """Data class representing an edge in a protocol visualization."""
    edge_id: str  # Edge identifier
    edge_type: EdgeType  # Edge type
    source_id: str  # Source node ID
    target_id: str  # Target node ID
    label: Optional[str] = None  # Edge label
    description: Optional[str] = None  # Edge description
    weight: Optional[float] = None  # Edge weight
    color: Optional[str] = None  # Edge color
    state: Optional[str] = None  # Edge state
    animated: bool = False  # Whether the edge is animated
    bidirectional: bool = False  # Whether the edge is bidirectional
    metadata: Dict[str, Any] = None  # Additional metadata
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ProtocolMessage:
    """Data class representing a protocol message."""
    message_id: str  # Message identifier
    protocol_type: ProtocolType  # Protocol type
    source_id: str  # Source node ID
    target_id: str  # Target node ID
    message_type: str  # Message type
    content: Dict[str, Any]  # Message content
    timestamp: float  # Message timestamp
    sequence_number: Optional[int] = None  # Message sequence number
    correlation_id: Optional[str] = None  # Correlation ID for related messages
    metadata: Dict[str, Any] = None  # Additional metadata
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ProtocolVisualizationEngine:
    """
    Provides protocol visualization capabilities for the Industriverse UI/UX Layer.
    
    This class provides:
    - MCP and A2A protocol visualization
    - Real-time message flow visualization
    - Protocol state visualization
    - Agent interaction visualization
    - Integration with the Universal Skin and Capsule Framework
    - Integration with the Protocol Visualizer component
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Protocol Visualization Engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.visualizations: Dict[str, Dict[str, Any]] = {}  # Map visualization ID to visualization data
        self.nodes: Dict[str, Dict[str, VisualizationNode]] = {}  # Map visualization ID to node map
        self.edges: Dict[str, Dict[str, VisualizationEdge]] = {}  # Map visualization ID to edge map
        self.messages: Dict[str, List[ProtocolMessage]] = {}  # Map visualization ID to message list
        self.visualization_listeners: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}  # Map visualization ID to listeners
        self.node_listeners: Dict[str, Dict[str, List[Callable[[Dict[str, Any]], None]]]] = {}  # Map visualization ID to node listeners
        self.edge_listeners: Dict[str, Dict[str, List[Callable[[Dict[str, Any]], None]]]] = {}  # Map visualization ID to edge listeners
        self.message_listeners: Dict[str, List[Callable[[ProtocolMessage], None]]] = {}  # Map visualization ID to message listeners
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []  # Event listeners
        self.logger = logging.getLogger(__name__)
        self.update_interval: float = self.config.get("update_interval", 0.1)  # 100ms by default
        
        # Initialize visualization backend (placeholder)
        self.visualization_backend = self._initialize_visualization_backend()
        
        # Load visualizations from config
        self._load_visualizations_from_config()
        
    def start(self) -> bool:
        """
        Start the Protocol Visualization Engine.
        
        Returns:
            True if the engine was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Start visualization backend (placeholder)
        # self.visualization_backend.start()
        
        # Start update thread
        threading.Thread(target=self._update_loop, daemon=True).start()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "protocol_visualization_engine_started"
        })
        
        self.logger.info("Protocol Visualization Engine started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Protocol Visualization Engine.
        
        Returns:
            True if the engine was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Stop visualization backend (placeholder)
        # self.visualization_backend.stop()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "protocol_visualization_engine_stopped"
        })
        
        self.logger.info("Protocol Visualization Engine stopped.")
        return True
    
    def create_visualization(self,
                           visualization_id: str,
                           name: str,
                           description: str,
                           protocol_type: ProtocolType,
                           visualization_mode: VisualizationMode,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new protocol visualization.
        
        Args:
            visualization_id: Unique identifier for this visualization
            name: Human-readable name
            description: Visualization description
            protocol_type: Type of protocol
            visualization_mode: Mode of visualization
            metadata: Additional metadata for this visualization
            
        Returns:
            True if the visualization was created, False if already exists
        """
        if visualization_id in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} already exists.")
            return False
            
        self.visualizations[visualization_id] = {
            "visualization_id": visualization_id,
            "name": name,
            "description": description,
            "protocol_type": protocol_type,
            "visualization_mode": visualization_mode,
            "creation_time": time.time(),
            "last_update_time": time.time(),
            "metadata": metadata or {}
        }
        
        # Initialize node, edge, and message maps
        self.nodes[visualization_id] = {}
        self.edges[visualization_id] = {}
        self.messages[visualization_id] = []
        self.visualization_listeners[visualization_id] = []
        self.node_listeners[visualization_id] = {}
        self.edge_listeners[visualization_id] = {}
        self.message_listeners[visualization_id] = []
        
        # --- Visualization Backend Interaction (Placeholder) ---
        try:
            # self.visualization_backend.create_visualization(visualization_id, {
            #     "name": name,
            #     "description": description,
            #     "protocol_type": protocol_type.value,
            #     "visualization_mode": visualization_mode.value,
            #     "metadata": metadata or {}
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error creating visualization with backend: {e}")
        # --- End Visualization Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "visualization_created",
            "visualization_id": visualization_id,
            "name": name,
            "protocol_type": protocol_type.value,
            "visualization_mode": visualization_mode.value
        })
        
        self.logger.debug(f"Created visualization: {visualization_id} ({name})")
        return True
    
    def delete_visualization(self, visualization_id: str) -> bool:
        """
        Delete a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization to delete
            
        Returns:
            True if the visualization was deleted, False if not found
        """
        if visualization_id not in self.visualizations:
            return False
            
        # --- Visualization Backend Interaction (Placeholder) ---
        try:
            # self.visualization_backend.delete_visualization(visualization_id)
            pass
        except Exception as e:
            self.logger.error(f"Error deleting visualization with backend: {e}")
        # --- End Visualization Backend Interaction ---
        
        # Clean up all visualization data
        del self.visualizations[visualization_id]
        del self.nodes[visualization_id]
        del self.edges[visualization_id]
        del self.messages[visualization_id]
        
        # Clean up listeners
        if visualization_id in self.visualization_listeners:
            del self.visualization_listeners[visualization_id]
        if visualization_id in self.node_listeners:
            del self.node_listeners[visualization_id]
        if visualization_id in self.edge_listeners:
            del self.edge_listeners[visualization_id]
        if visualization_id in self.message_listeners:
            del self.message_listeners[visualization_id]
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "visualization_deleted",
            "visualization_id": visualization_id
        })
        
        self.logger.debug(f"Deleted visualization: {visualization_id}")
        return True
    
    def add_node(self,
               visualization_id: str,
               node_id: str,
               node_type: NodeType,
               label: str,
               description: Optional[str] = None,
               icon: Optional[str] = None,
               position: Optional[Tuple[float, float, float]] = None,
               size: Optional[float] = None,
               color: Optional[str] = None,
               state: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a node to a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            node_id: Unique identifier for this node
            node_type: Type of node
            label: Node label
            description: Optional node description
            icon: Optional node icon
            position: Optional 3D position
            size: Optional node size
            color: Optional node color
            state: Optional node state
            metadata: Additional metadata for this node
            
        Returns:
            True if the node was added, False if visualization not found or node already exists
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if node_id in self.nodes[visualization_id]:
            self.logger.warning(f"Node {node_id} already exists in visualization {visualization_id}.")
            return False
            
        node = VisualizationNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            description=description,
            icon=icon,
            position=position,
            size=size,
            color=color,
            state=state,
            metadata=metadata or {}
        )
        
        self.nodes[visualization_id][node_id] = node
        
        # Initialize node listeners
        self.node_listeners[visualization_id][node_id] = []
        
        # --- Visualization Backend Interaction (Placeholder) ---
        try:
            # self.visualization_backend.add_node(visualization_id, node_id, {
            #     "node_type": node_type.value,
            #     "label": label,
            #     "description": description,
            #     "icon": icon,
            #     "position": position,
            #     "size": size,
            #     "color": color,
            #     "state": state,
            #     "metadata": metadata or {}
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error adding node with backend: {e}")
        # --- End Visualization Backend Interaction ---
        
        # Update visualization last update time
        self.visualizations[visualization_id]["last_update_time"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_added",
            "visualization_id": visualization_id,
            "node_id": node_id,
            "node_type": node_type.value,
            "label": label
        })
        
        self.logger.debug(f"Added node {node_id} to visualization {visualization_id}")
        return True
    
    def update_node(self,
                  visualization_id: str,
                  node_id: str,
                  label: Optional[str] = None,
                  description: Optional[str] = None,
                  icon: Optional[str] = None,
                  position: Optional[Tuple[float, float, float]] = None,
                  size: Optional[float] = None,
                  color: Optional[str] = None,
                  state: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a node in a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            node_id: ID of the node to update
            label: Optional new node label
            description: Optional new node description
            icon: Optional new node icon
            position: Optional new 3D position
            size: Optional new node size
            color: Optional new node color
            state: Optional new node state
            metadata: Optional new metadata for this node
            
        Returns:
            True if the node was updated, False if visualization or node not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if node_id not in self.nodes[visualization_id]:
            self.logger.warning(f"Node {node_id} not found in visualization {visualization_id}.")
            return False
            
        node = self.nodes[visualization_id][node_id]
        
        # Update node properties
        if label is not None:
            node.label = label
        if description is not None:
            node.description = description
        if icon is not None:
            node.icon = icon
        if position is not None:
            node.position = position
        if size is not None:
            node.size = size
        if color is not None:
            node.color = color
        if state is not None:
            node.state = state
        if metadata is not None:
            node.metadata.update(metadata)
            
        # --- Visualization Backend Interaction (Placeholder) ---
        try:
            # self.visualization_backend.update_node(visualization_id, node_id, {
            #     "label": label,
            #     "description": description,
            #     "icon": icon,
            #     "position": position,
            #     "size": size,
            #     "color": color,
            #     "state": state,
            #     "metadata": metadata
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error updating node with backend: {e}")
        # --- End Visualization Backend Interaction ---
        
        # Update visualization last update time
        self.visualizations[visualization_id]["last_update_time"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_updated",
            "visualization_id": visualization_id,
            "node_id": node_id,
            "node_type": node.node_type.value,
            "label": node.label,
            "state": node.state
        })
        
        # Notify node listeners
        node_event = {
            "event_type": "node_updated",
            "visualization_id": visualization_id,
            "node_id": node_id,
            "node_type": node.node_type.value,
            "label": node.label,
            "state": node.state,
            "timestamp": time.time()
        }
        
        for listener in self.node_listeners[visualization_id][node_id]:
            try:
                listener(node_event)
            except Exception as e:
                self.logger.error(f"Error in node listener for {visualization_id}.{node_id}: {e}")
                
        self.logger.debug(f"Updated node {node_id} in visualization {visualization_id}")
        return True
    
    def remove_node(self, visualization_id: str, node_id: str) -> bool:
        """
        Remove a node from a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            node_id: ID of the node to remove
            
        Returns:
            True if the node was removed, False if visualization or node not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if node_id not in self.nodes[visualization_id]:
            self.logger.warning(f"Node {node_id} not found in visualization {visualization_id}.")
            return False
            
        # --- Visualization Backend Interaction (Placeholder) ---
        try:
            # self.visualization_backend.remove_node(visualization_id, node_id)
            pass
        except Exception as e:
            self.logger.error(f"Error removing node with backend: {e}")
        # --- End Visualization Backend Interaction ---
        
        # Remove node
        del self.nodes[visualization_id][node_id]
        
        # Remove node listeners
        if node_id in self.node_listeners[visualization_id]:
            del self.node_listeners[visualization_id][node_id]
            
        # Remove edges connected to this node
        edges_to_remove = []
        for edge_id, edge in self.edges[visualization_id].items():
            if edge.source_id == node_id or edge.target_id == node_id:
                edges_to_remove.append(edge_id)
                
        for edge_id in edges_to_remove:
            self.remove_edge(visualization_id, edge_id)
            
        # Update visualization last update time
        self.visualizations[visualization_id]["last_update_time"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_removed",
            "visualization_id": visualization_id,
            "node_id": node_id
        })
        
        self.logger.debug(f"Removed node {node_id} from visualization {visualization_id}")
        return True
    
    def add_edge(self,
               visualization_id: str,
               edge_id: str,
               edge_type: EdgeType,
               source_id: str,
               target_id: str,
               label: Optional[str] = None,
               description: Optional[str] = None,
               weight: Optional[float] = None,
               color: Optional[str] = None,
               state: Optional[str] = None,
               animated: bool = False,
               bidirectional: bool = False,
               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add an edge to a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            edge_id: Unique identifier for this edge
            edge_type: Type of edge
            source_id: Source node ID
            target_id: Target node ID
            label: Optional edge label
            description: Optional edge description
            weight: Optional edge weight
            color: Optional edge color
            state: Optional edge state
            animated: Whether the edge is animated
            bidirectional: Whether the edge is bidirectional
            metadata: Additional metadata for this edge
            
        Returns:
            True if the edge was added, False if visualization not found, edge already exists, or source/target nodes not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if edge_id in self.edges[visualization_id]:
            self.logger.warning(f"Edge {edge_id} already exists in visualization {visualization_id}.")
            return False
            
        if source_id not in self.nodes[visualization_id]:
            self.logger.warning(f"Source node {source_id} not found in visualization {visualization_id}.")
            return False
            
        if target_id not in self.nodes[visualization_id]:
            self.logger.warning(f"Target node {target_id} not found in visualization {visualization_id}.")
            return False
            
        edge = VisualizationEdge(
            edge_id=edge_id,
            edge_type=edge_type,
            source_id=source_id,
            target_id=target_id,
            label=label,
            description=description,
            weight=weight,
            color=color,
            state=state,
            animated=animated,
            bidirectional=bidirectional,
            metadata=metadata or {}
        )
        
        self.edges[visualization_id][edge_id] = edge
        
        # Initialize edge listeners
        self.edge_listeners[visualization_id][edge_id] = []
        
        # --- Visualization Backend Interaction (Placeholder) ---
        try:
            # self.visualization_backend.add_edge(visualization_id, edge_id, {
            #     "edge_type": edge_type.value,
            #     "source_id": source_id,
            #     "target_id": target_id,
            #     "label": label,
            #     "description": description,
            #     "weight": weight,
            #     "color": color,
            #     "state": state,
            #     "animated": animated,
            #     "bidirectional": bidirectional,
            #     "metadata": metadata or {}
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error adding edge with backend: {e}")
        # --- End Visualization Backend Interaction ---
        
        # Update visualization last update time
        self.visualizations[visualization_id]["last_update_time"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "edge_added",
            "visualization_id": visualization_id,
            "edge_id": edge_id,
            "edge_type": edge_type.value,
            "source_id": source_id,
            "target_id": target_id
        })
        
        self.logger.debug(f"Added edge {edge_id} to visualization {visualization_id}")
        return True
    
    def update_edge(self,
                  visualization_id: str,
                  edge_id: str,
                  label: Optional[str] = None,
                  description: Optional[str] = None,
                  weight: Optional[float] = None,
                  color: Optional[str] = None,
                  state: Optional[str] = None,
                  animated: Optional[bool] = None,
                  bidirectional: Optional[bool] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an edge in a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            edge_id: ID of the edge to update
            label: Optional new edge label
            description: Optional new edge description
            weight: Optional new edge weight
            color: Optional new edge color
            state: Optional new edge state
            animated: Optional new animated flag
            bidirectional: Optional new bidirectional flag
            metadata: Optional new metadata for this edge
            
        Returns:
            True if the edge was updated, False if visualization or edge not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if edge_id not in self.edges[visualization_id]:
            self.logger.warning(f"Edge {edge_id} not found in visualization {visualization_id}.")
            return False
            
        edge = self.edges[visualization_id][edge_id]
        
        # Update edge properties
        if label is not None:
            edge.label = label
        if description is not None:
            edge.description = description
        if weight is not None:
            edge.weight = weight
        if color is not None:
            edge.color = color
        if state is not None:
            edge.state = state
        if animated is not None:
            edge.animated = animated
        if bidirectional is not None:
            edge.bidirectional = bidirectional
        if metadata is not None:
            edge.metadata.update(metadata)
            
        # --- Visualization Backend Interaction (Placeholder) ---
        try:
            # self.visualization_backend.update_edge(visualization_id, edge_id, {
            #     "label": label,
            #     "description": description,
            #     "weight": weight,
            #     "color": color,
            #     "state": state,
            #     "animated": animated,
            #     "bidirectional": bidirectional,
            #     "metadata": metadata
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error updating edge with backend: {e}")
        # --- End Visualization Backend Interaction ---
        
        # Update visualization last update time
        self.visualizations[visualization_id]["last_update_time"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "edge_updated",
            "visualization_id": visualization_id,
            "edge_id": edge_id,
            "edge_type": edge.edge_type.value,
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "state": edge.state
        })
        
        # Notify edge listeners
        edge_event = {
            "event_type": "edge_updated",
            "visualization_id": visualization_id,
            "edge_id": edge_id,
            "edge_type": edge.edge_type.value,
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "state": edge.state,
            "timestamp": time.time()
        }
        
        for listener in self.edge_listeners[visualization_id][edge_id]:
            try:
                listener(edge_event)
            except Exception as e:
                self.logger.error(f"Error in edge listener for {visualization_id}.{edge_id}: {e}")
                
        self.logger.debug(f"Updated edge {edge_id} in visualization {visualization_id}")
        return True
    
    def remove_edge(self, visualization_id: str, edge_id: str) -> bool:
        """
        Remove an edge from a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            edge_id: ID of the edge to remove
            
        Returns:
            True if the edge was removed, False if visualization or edge not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if edge_id not in self.edges[visualization_id]:
            self.logger.warning(f"Edge {edge_id} not found in visualization {visualization_id}.")
            return False
            
        # --- Visualization Backend Interaction (Placeholder) ---
        try:
            # self.visualization_backend.remove_edge(visualization_id, edge_id)
            pass
        except Exception as e:
            self.logger.error(f"Error removing edge with backend: {e}")
        # --- End Visualization Backend Interaction ---
        
        # Remove edge
        del self.edges[visualization_id][edge_id]
        
        # Remove edge listeners
        if edge_id in self.edge_listeners[visualization_id]:
            del self.edge_listeners[visualization_id][edge_id]
            
        # Update visualization last update time
        self.visualizations[visualization_id]["last_update_time"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "edge_removed",
            "visualization_id": visualization_id,
            "edge_id": edge_id
        })
        
        self.logger.debug(f"Removed edge {edge_id} from visualization {visualization_id}")
        return True
    
    def add_message(self,
                  visualization_id: str,
                  message_id: str,
                  protocol_type: ProtocolType,
                  source_id: str,
                  target_id: str,
                  message_type: str,
                  content: Dict[str, Any],
                  timestamp: Optional[float] = None,
                  sequence_number: Optional[int] = None,
                  correlation_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a protocol message to a visualization.
        
        Args:
            visualization_id: ID of the visualization
            message_id: Unique identifier for this message
            protocol_type: Type of protocol
            source_id: Source node ID
            target_id: Target node ID
            message_type: Message type
            content: Message content
            timestamp: Optional message timestamp (defaults to current time)
            sequence_number: Optional message sequence number
            correlation_id: Optional correlation ID for related messages
            metadata: Additional metadata for this message
            
        Returns:
            True if the message was added, False if visualization not found or source/target nodes not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if source_id not in self.nodes[visualization_id]:
            self.logger.warning(f"Source node {source_id} not found in visualization {visualization_id}.")
            return False
            
        if target_id not in self.nodes[visualization_id]:
            self.logger.warning(f"Target node {target_id} not found in visualization {visualization_id}.")
            return False
            
        # Use current time if timestamp not provided
        if timestamp is None:
            timestamp = time.time()
            
        message = ProtocolMessage(
            message_id=message_id,
            protocol_type=protocol_type,
            source_id=source_id,
            target_id=target_id,
            message_type=message_type,
            content=content,
            timestamp=timestamp,
            sequence_number=sequence_number,
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        
        # Add message to visualization
        self.messages[visualization_id].insert(0, message)
        
        # Limit message history
        max_messages = self.config.get("max_messages", 1000)
        if len(self.messages[visualization_id]) > max_messages:
            self.messages[visualization_id] = self.messages[visualization_id][:max_messages]
            
        # --- Visualization Backend Interaction (Placeholder) ---
        try:
            # self.visualization_backend.add_message(visualization_id, message_id, {
            #     "protocol_type": protocol_type.value,
            #     "source_id": source_id,
            #     "target_id": target_id,
            #     "message_type": message_type,
            #     "content": content,
            #     "timestamp": timestamp,
            #     "sequence_number": sequence_number,
            #     "correlation_id": correlation_id,
            #     "metadata": metadata or {}
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error adding message with backend: {e}")
        # --- End Visualization Backend Interaction ---
        
        # Update visualization last update time
        self.visualizations[visualization_id]["last_update_time"] = timestamp
        
        # Create or update edge for this message
        edge_id = f"{source_id}_{target_id}"
        if edge_id in self.edges[visualization_id]:
            # Update existing edge
            self.update_edge(
                visualization_id=visualization_id,
                edge_id=edge_id,
                state="active",
                animated=True
            )
        else:
            # Create new edge
            self.add_edge(
                visualization_id=visualization_id,
                edge_id=edge_id,
                edge_type=EdgeType.MESSAGE,
                source_id=source_id,
                target_id=target_id,
                label=message_type,
                state="active",
                animated=True
            )
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "message_added",
            "visualization_id": visualization_id,
            "message_id": message_id,
            "protocol_type": protocol_type.value,
            "source_id": source_id,
            "target_id": target_id,
            "message_type": message_type,
            "timestamp": timestamp
        })
        
        # Notify message listeners
        for listener in self.message_listeners[visualization_id]:
            try:
                listener(message)
            except Exception as e:
                self.logger.error(f"Error in message listener for visualization {visualization_id}: {e}")
                
        self.logger.debug(f"Added message {message_id} to visualization {visualization_id}")
        return True
    
    def get_messages(self,
                   visualization_id: str,
                   limit: int = 100,
                   source_id: Optional[str] = None,
                   target_id: Optional[str] = None,
                   message_type: Optional[str] = None,
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None) -> List[ProtocolMessage]:
        """
        Get messages from a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            limit: Maximum number of messages to return
            source_id: Optional filter by source node ID
            target_id: Optional filter by target node ID
            message_type: Optional filter by message type
            start_time: Optional start time (Unix timestamp)
            end_time: Optional end time (Unix timestamp)
            
        Returns:
            List of protocol messages, or empty list if visualization not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return []
            
        messages = self.messages[visualization_id]
        
        # Apply filters
        filtered_messages = []
        for message in messages:
            # Filter by source ID
            if source_id is not None and message.source_id != source_id:
                continue
                
            # Filter by target ID
            if target_id is not None and message.target_id != target_id:
                continue
                
            # Filter by message type
            if message_type is not None and message.message_type != message_type:
                continue
                
            # Filter by time range
            if start_time is not None and message.timestamp < start_time:
                continue
                
            if end_time is not None and message.timestamp > end_time:
                continue
                
            filtered_messages.append(message)
            
            # Limit number of messages
            if len(filtered_messages) >= limit:
                break
                
        return filtered_messages
    
    def get_visualization_info(self, visualization_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            
        Returns:
            Visualization information, or None if visualization not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return None
            
        return self.visualizations[visualization_id]
    
    def get_nodes(self, visualization_id: str) -> Dict[str, VisualizationNode]:
        """
        Get all nodes in a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            
        Returns:
            Map of node ID to node data, or empty dict if visualization not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return {}
            
        return self.nodes[visualization_id]
    
    def get_edges(self, visualization_id: str) -> Dict[str, VisualizationEdge]:
        """
        Get all edges in a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            
        Returns:
            Map of edge ID to edge data, or empty dict if visualization not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return {}
            
        return self.edges[visualization_id]
    
    def add_visualization_listener(self, visualization_id: str, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Add a listener for all events related to a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            listener: Callback function that will be called with event data
            
        Returns:
            True if the listener was added, False if visualization not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        self.visualization_listeners[visualization_id].append(listener)
        return True
    
    def add_node_listener(self, visualization_id: str, node_id: str, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Add a listener for a specific node in a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            node_id: ID of the node
            listener: Callback function that will be called when the node is updated
            
        Returns:
            True if the listener was added, False if visualization or node not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if node_id not in self.nodes[visualization_id]:
            self.logger.warning(f"Node {node_id} not found in visualization {visualization_id}.")
            return False
            
        self.node_listeners[visualization_id][node_id].append(listener)
        return True
    
    def add_edge_listener(self, visualization_id: str, edge_id: str, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Add a listener for a specific edge in a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            edge_id: ID of the edge
            listener: Callback function that will be called when the edge is updated
            
        Returns:
            True if the listener was added, False if visualization or edge not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if edge_id not in self.edges[visualization_id]:
            self.logger.warning(f"Edge {edge_id} not found in visualization {visualization_id}.")
            return False
            
        self.edge_listeners[visualization_id][edge_id].append(listener)
        return True
    
    def add_message_listener(self, visualization_id: str, listener: Callable[[ProtocolMessage], None]) -> bool:
        """
        Add a listener for messages in a protocol visualization.
        
        Args:
            visualization_id: ID of the visualization
            listener: Callback function that will be called when a message is added
            
        Returns:
            True if the listener was added, False if visualization not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        self.message_listeners[visualization_id].append(listener)
        return True
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all protocol visualization events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            return True
            
        return False
    
    def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_data: The event data to dispatch
        """
        # Add source if not present
        if "source" not in event_data:
            event_data["source"] = "ProtocolVisualizationEngine"
            
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = time.time()
            
        # Dispatch to visualization-specific listeners
        if "visualization_id" in event_data:
            visualization_id = event_data["visualization_id"]
            if visualization_id in self.visualization_listeners:
                for listener in self.visualization_listeners[visualization_id]:
                    try:
                        listener(event_data)
                    except Exception as e:
                        self.logger.error(f"Error in visualization listener for {visualization_id}: {e}")
                        
        # Dispatch to global event listeners
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in protocol visualization event listener: {e}")
                
    def _initialize_visualization_backend(self) -> Any:
        """Placeholder for initializing the visualization backend."""
        # In a real implementation, this would initialize a visualization backend
        # For now, we'll just return a dummy object
        return object()
    
    def _load_visualizations_from_config(self) -> None:
        """Load protocol visualizations from the configuration."""
        visualizations_config = self.config.get("visualizations", [])
        
        for visualization_config in visualizations_config:
            try:
                visualization_id = visualization_config["visualization_id"]
                name = visualization_config["name"]
                description = visualization_config["description"]
                protocol_type = ProtocolType(visualization_config["protocol_type"])
                visualization_mode = VisualizationMode(visualization_config["visualization_mode"])
                metadata = visualization_config.get("metadata")
                
                self.create_visualization(
                    visualization_id=visualization_id,
                    name=name,
                    description=description,
                    protocol_type=protocol_type,
                    visualization_mode=visualization_mode,
                    metadata=metadata
                )
                
                # Load nodes
                for node_config in visualization_config.get("nodes", []):
                    try:
                        self.add_node(
                            visualization_id=visualization_id,
                            node_id=node_config["node_id"],
                            node_type=NodeType(node_config["node_type"]),
                            label=node_config["label"],
                            description=node_config.get("description"),
                            icon=node_config.get("icon"),
                            position=node_config.get("position"),
                            size=node_config.get("size"),
                            color=node_config.get("color"),
                            state=node_config.get("state"),
                            metadata=node_config.get("metadata")
                        )
                    except (KeyError, ValueError) as e:
                        self.logger.warning(f"Error loading node for visualization {visualization_id}: {e}")
                        
                # Load edges
                for edge_config in visualization_config.get("edges", []):
                    try:
                        self.add_edge(
                            visualization_id=visualization_id,
                            edge_id=edge_config["edge_id"],
                            edge_type=EdgeType(edge_config["edge_type"]),
                            source_id=edge_config["source_id"],
                            target_id=edge_config["target_id"],
                            label=edge_config.get("label"),
                            description=edge_config.get("description"),
                            weight=edge_config.get("weight"),
                            color=edge_config.get("color"),
                            state=edge_config.get("state"),
                            animated=edge_config.get("animated", False),
                            bidirectional=edge_config.get("bidirectional", False),
                            metadata=edge_config.get("metadata")
                        )
                    except (KeyError, ValueError) as e:
                        self.logger.warning(f"Error loading edge for visualization {visualization_id}: {e}")
                        
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error loading visualization from config: {e}")
                
    def _update_loop(self) -> None:
        """Background thread for updating protocol visualizations."""
        while self.is_active:
            try:
                # --- Visualization Backend Interaction (Placeholder) ---
                # In a real implementation, this would poll the visualization backend for updates
                # For now, we'll just simulate some updates
                
                # Simulate edge animations
                for visualization_id, edges in self.edges.items():
                    for edge_id, edge in edges.items():
                        if edge.animated:
                            # Randomly deactivate edges occasionally
                            if random.random() < 0.01:  # 1% chance per update
                                self.update_edge(
                                    visualization_id=visualization_id,
                                    edge_id=edge_id,
                                    state="inactive",
                                    animated=False
                                )
                # --- End Visualization Backend Interaction ---
                
            except Exception as e:
                self.logger.error(f"Error in protocol visualization update loop: {e}")
                
            # Sleep until next update
            time.sleep(self.update_interval)

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create protocol visualization engine
    visualization_config = {
        "update_interval": 0.1,
        "max_messages": 1000,
        "visualizations": [
            {
                "visualization_id": "mcp_flow",
                "name": "MCP Message Flow",
                "description": "Visualization of MCP message flow between layers and models",
                "protocol_type": "mcp",
                "visualization_mode": "flow",
                "nodes": [
                    {
                        "node_id": "data_layer",
                        "node_type": "layer",
                        "label": "Data Layer",
                        "position": (0, 0, 0),
                        "color": "#3498db"
                    },
                    {
                        "node_id": "core_ai_layer",
                        "node_type": "layer",
                        "label": "Core AI Layer",
                        "position": (0, 1, 0),
                        "color": "#2ecc71"
                    },
                    {
                        "node_id": "generative_layer",
                        "node_type": "layer",
                        "label": "Generative Layer",
                        "position": (0, 2, 0),
                        "color": "#e74c3c"
                    }
                ],
                "edges": [
                    {
                        "edge_id": "data_to_core",
                        "edge_type": "flow",
                        "source_id": "data_layer",
                        "target_id": "core_ai_layer",
                        "label": "Data Flow",
                        "state": "inactive"
                    },
                    {
                        "edge_id": "core_to_generative",
                        "edge_type": "flow",
                        "source_id": "core_ai_layer",
                        "target_id": "generative_layer",
                        "label": "Model Output",
                        "state": "inactive"
                    }
                ]
            }
        ]
    }
    
    visualization_engine = ProtocolVisualizationEngine(config=visualization_config)
    
    # Start the engine
    visualization_engine.start()
    
    # Create a new visualization
    visualization_engine.create_visualization(
        visualization_id="a2a_network",
        name="A2A Agent Network",
        description="Visualization of A2A agent network",
        protocol_type=ProtocolType.A2A,
        visualization_mode=VisualizationMode.NETWORK
    )
    
    # Add nodes to the new visualization
    visualization_engine.add_node(
        visualization_id="a2a_network",
        node_id="agent_1",
        node_type=NodeType.AGENT,
        label="Agent 1",
        position=(0, 0, 0),
        color="#f39c12"
    )
    
    visualization_engine.add_node(
        visualization_id="a2a_network",
        node_id="agent_2",
        node_type=NodeType.AGENT,
        label="Agent 2",
        position=(1, 0, 0),
        color="#9b59b6"
    )
    
    # Add an edge between the agents
    visualization_engine.add_edge(
        visualization_id="a2a_network",
        edge_id="agent_1_to_2",
        edge_type=EdgeType.MESSAGE,
        source_id="agent_1",
        target_id="agent_2",
        label="A2A Messages",
        state="inactive"
    )
    
    # Add a message listener
    def on_message(message):
        print(f"Message from {message.source_id} to {message.target_id}: {message.message_type}")
        
    visualization_engine.add_message_listener("a2a_network", on_message)
    
    # Add a message
    visualization_engine.add_message(
        visualization_id="a2a_network",
        message_id=str(uuid.uuid4()),
        protocol_type=ProtocolType.A2A,
        source_id="agent_1",
        target_id="agent_2",
        message_type="AgentRequest",
        content={"action": "get_data", "parameters": {"data_type": "sensor_readings"}}
    )
    
    # Wait a bit to see updates
    time.sleep(2)
    
    # Add another message
    visualization_engine.add_message(
        visualization_id="a2a_network",
        message_id=str(uuid.uuid4()),
        protocol_type=ProtocolType.A2A,
        source_id="agent_2",
        target_id="agent_1",
        message_type="AgentResponse",
        content={"status": "success", "data": {"sensor_readings": [1.2, 3.4, 5.6]}}
    )
    
    # Get messages
    messages = visualization_engine.get_messages("a2a_network", limit=5)
    print(f"Retrieved {len(messages)} messages")
    
    # Stop the engine
    visualization_engine.stop()
"""
