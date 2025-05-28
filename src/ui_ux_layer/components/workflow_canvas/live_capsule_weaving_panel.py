"""
Live Capsule Weaving Panel for the Industriverse UI/UX Layer.

This module provides a drag-drop Composer Mode where capsules connect visually like threads,
with suggestions from the Generative Layer on optimal sequencing.

Author: Manus
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
import uuid
import json
import random
import math

class ConnectionType(Enum):
    """Enumeration of capsule connection types."""
    DATA_FLOW = "data_flow"  # Data flows from one capsule to another
    CONTROL_FLOW = "control_flow"  # Control flows from one capsule to another
    TRIGGER = "trigger"  # One capsule triggers another
    DEPENDENCY = "dependency"  # One capsule depends on another
    COLLABORATION = "collaboration"  # Capsules collaborate
    CUSTOM = "custom"  # Custom connection type

class ConnectionStrength(Enum):
    """Enumeration of connection strength levels."""
    WEAK = "weak"  # Weak connection
    MODERATE = "moderate"  # Moderate connection
    STRONG = "strong"  # Strong connection
    CRITICAL = "critical"  # Critical connection
    CUSTOM = "custom"  # Custom strength level

class ConnectionState(Enum):
    """Enumeration of connection states."""
    INACTIVE = "inactive"  # Connection is inactive
    ACTIVE = "active"  # Connection is active
    PENDING = "pending"  # Connection is pending
    FAILED = "failed"  # Connection has failed
    CUSTOM = "custom"  # Custom state

class CapsuleNode:
    """Represents a capsule node in the weaving panel."""
    
    def __init__(self,
                 node_id: str,
                 capsule_id: str,
                 position: Tuple[float, float],
                 size: Tuple[float, float] = (100, 100),
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a capsule node.
        
        Args:
            node_id: Unique identifier for this node
            capsule_id: ID of the capsule this node represents
            position: Position of the node (x, y)
            size: Size of the node (width, height)
            metadata: Additional metadata for this node
        """
        self.node_id = node_id
        self.capsule_id = capsule_id
        self.position = position
        self.size = size
        self.metadata = metadata or {}
        self.connections: List[str] = []  # List of connection IDs
        self.is_selected = False
        self.is_dragging = False
        self.z_index = 1
        self.last_update = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this node to a dictionary representation."""
        return {
            "node_id": self.node_id,
            "capsule_id": self.capsule_id,
            "position": self.position,
            "size": self.size,
            "connections": self.connections,
            "is_selected": self.is_selected,
            "is_dragging": self.is_dragging,
            "z_index": self.z_index,
            "last_update": self.last_update,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapsuleNode':
        """Create a capsule node from a dictionary representation."""
        node = cls(
            node_id=data["node_id"],
            capsule_id=data["capsule_id"],
            position=data["position"],
            size=data.get("size", (100, 100)),
            metadata=data.get("metadata", {})
        )
        
        node.connections = data.get("connections", [])
        node.is_selected = data.get("is_selected", False)
        node.is_dragging = data.get("is_dragging", False)
        node.z_index = data.get("z_index", 1)
        node.last_update = data.get("last_update", time.time())
        
        return node

class CapsuleConnection:
    """Represents a connection between capsule nodes."""
    
    def __init__(self,
                 connection_id: str,
                 source_node_id: str,
                 target_node_id: str,
                 connection_type: ConnectionType,
                 strength: ConnectionStrength = ConnectionStrength.MODERATE,
                 state: ConnectionState = ConnectionState.INACTIVE,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a capsule connection.
        
        Args:
            connection_id: Unique identifier for this connection
            source_node_id: ID of the source node
            target_node_id: ID of the target node
            connection_type: Type of connection
            strength: Strength of the connection
            state: State of the connection
            metadata: Additional metadata for this connection
        """
        self.connection_id = connection_id
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.connection_type = connection_type
        self.strength = strength
        self.state = state
        self.metadata = metadata or {}
        self.control_points: List[Tuple[float, float]] = []  # Bezier curve control points
        self.is_selected = False
        self.last_update = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this connection to a dictionary representation."""
        return {
            "connection_id": self.connection_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "connection_type": self.connection_type.value,
            "strength": self.strength.value,
            "state": self.state.value,
            "control_points": self.control_points,
            "is_selected": self.is_selected,
            "last_update": self.last_update,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapsuleConnection':
        """Create a capsule connection from a dictionary representation."""
        connection = cls(
            connection_id=data["connection_id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            connection_type=ConnectionType(data["connection_type"]),
            strength=ConnectionStrength(data["strength"]),
            state=ConnectionState(data["state"]),
            metadata=data.get("metadata", {})
        )
        
        connection.control_points = data.get("control_points", [])
        connection.is_selected = data.get("is_selected", False)
        connection.last_update = data.get("last_update", time.time())
        
        return connection

class CapsuleWeavingPanel:
    """
    Provides a drag-drop Composer Mode where capsules connect visually like threads.
    
    This class provides:
    - Visual canvas for arranging and connecting capsules
    - Drag-and-drop functionality for capsules
    - Connection creation and management
    - Suggestions from the Generative Layer on optimal sequencing
    - Visual representation of data and control flows
    - Integration with the Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Capsule Weaving Panel.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.nodes: Dict[str, CapsuleNode] = {}
        self.connections: Dict[str, CapsuleConnection] = {}
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.suggestion_providers: List[Callable[[Dict[str, Any]], List[Dict[str, Any]]]] = []
        self.canvas_size: Tuple[float, float] = (2000, 2000)  # Default canvas size
        self.view_position: Tuple[float, float] = (0, 0)  # View position (pan)
        self.view_scale: float = 1.0  # View scale (zoom)
        self.is_composer_mode = False  # Whether composer mode is active
        self.selected_nodes: Set[str] = set()  # Set of selected node IDs
        self.selected_connections: Set[str] = set()  # Set of selected connection IDs
        self.pending_connection: Optional[Dict[str, Any]] = None  # Pending connection being created
        self.last_update = time.time()
        
    def set_canvas_size(self, width: float, height: float) -> None:
        """
        Set the canvas size.
        
        Args:
            width: Canvas width
            height: Canvas height
        """
        self.canvas_size = (width, height)
        
    def set_view_position(self, x: float, y: float) -> None:
        """
        Set the view position (pan).
        
        Args:
            x: X position
            y: Y position
        """
        self.view_position = (x, y)
        
    def set_view_scale(self, scale: float) -> None:
        """
        Set the view scale (zoom).
        
        Args:
            scale: Scale factor
        """
        self.view_scale = max(0.1, min(scale, 5.0))  # Clamp between 0.1 and 5.0
        
    def toggle_composer_mode(self) -> bool:
        """
        Toggle composer mode.
        
        Returns:
            New composer mode state
        """
        self.is_composer_mode = not self.is_composer_mode
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "composer_mode_changed",
            "is_composer_mode": self.is_composer_mode
        })
        
        return self.is_composer_mode
    
    def add_node(self,
               capsule_id: str,
               position: Tuple[float, float],
               size: Tuple[float, float] = (100, 100),
               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a capsule node to the panel.
        
        Args:
            capsule_id: ID of the capsule this node represents
            position: Position of the node (x, y)
            size: Size of the node (width, height)
            metadata: Additional metadata for this node
            
        Returns:
            ID of the created node
        """
        node_id = str(uuid.uuid4())
        
        self.nodes[node_id] = CapsuleNode(
            node_id=node_id,
            capsule_id=capsule_id,
            position=position,
            size=size,
            metadata=metadata or {}
        )
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_added",
            "node_id": node_id,
            "capsule_id": capsule_id,
            "position": position
        })
        
        return node_id
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a capsule node from the panel.
        
        Args:
            node_id: ID of the node to remove
            
        Returns:
            True if the node was removed, False if not found
        """
        if node_id not in self.nodes:
            return False
            
        node = self.nodes[node_id]
        
        # Remove all connections to/from this node
        for connection_id in list(self.connections.keys()):
            connection = self.connections[connection_id]
            
            if connection.source_node_id == node_id or connection.target_node_id == node_id:
                self.remove_connection(connection_id)
                
        # Remove node
        del self.nodes[node_id]
        
        # Remove from selected nodes
        if node_id in self.selected_nodes:
            self.selected_nodes.remove(node_id)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_removed",
            "node_id": node_id,
            "capsule_id": node.capsule_id
        })
        
        return True
    
    def move_node(self, node_id: str, position: Tuple[float, float]) -> bool:
        """
        Move a capsule node to a new position.
        
        Args:
            node_id: ID of the node to move
            position: New position of the node (x, y)
            
        Returns:
            True if the node was moved, False if not found
        """
        if node_id not in self.nodes:
            return False
            
        node = self.nodes[node_id]
        old_position = node.position
        
        # Update node position
        node.position = position
        node.last_update = time.time()
        
        # Update control points for connected connections
        for connection_id in node.connections:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                self._update_connection_control_points(connection)
                
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_moved",
            "node_id": node_id,
            "old_position": old_position,
            "new_position": position
        })
        
        return True
    
    def select_node(self, node_id: str, add_to_selection: bool = False) -> bool:
        """
        Select a capsule node.
        
        Args:
            node_id: ID of the node to select
            add_to_selection: Whether to add to the current selection (True) or replace it (False)
            
        Returns:
            True if the node was selected, False if not found
        """
        if node_id not in self.nodes:
            return False
            
        # Clear selection if not adding to it
        if not add_to_selection:
            self.clear_selection()
            
        # Select node
        self.nodes[node_id].is_selected = True
        self.nodes[node_id].z_index = 2  # Bring to front
        self.selected_nodes.add(node_id)
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_selected",
            "node_id": node_id,
            "add_to_selection": add_to_selection
        })
        
        return True
    
    def deselect_node(self, node_id: str) -> bool:
        """
        Deselect a capsule node.
        
        Args:
            node_id: ID of the node to deselect
            
        Returns:
            True if the node was deselected, False if not found
        """
        if node_id not in self.nodes:
            return False
            
        # Deselect node
        self.nodes[node_id].is_selected = False
        self.nodes[node_id].z_index = 1
        
        if node_id in self.selected_nodes:
            self.selected_nodes.remove(node_id)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_deselected",
            "node_id": node_id
        })
        
        return True
    
    def start_node_drag(self, node_id: str) -> bool:
        """
        Start dragging a capsule node.
        
        Args:
            node_id: ID of the node to drag
            
        Returns:
            True if the node drag was started, False if not found
        """
        if node_id not in self.nodes:
            return False
            
        # Start dragging
        self.nodes[node_id].is_dragging = True
        self.nodes[node_id].z_index = 3  # Bring to front while dragging
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_drag_started",
            "node_id": node_id
        })
        
        return True
    
    def end_node_drag(self, node_id: str) -> bool:
        """
        End dragging a capsule node.
        
        Args:
            node_id: ID of the node being dragged
            
        Returns:
            True if the node drag was ended, False if not found
        """
        if node_id not in self.nodes:
            return False
            
        # End dragging
        self.nodes[node_id].is_dragging = False
        self.nodes[node_id].z_index = 2 if self.nodes[node_id].is_selected else 1
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "node_drag_ended",
            "node_id": node_id
        })
        
        return True
    
    def add_connection(self,
                     source_node_id: str,
                     target_node_id: str,
                     connection_type: ConnectionType,
                     strength: ConnectionStrength = ConnectionStrength.MODERATE,
                     state: ConnectionState = ConnectionState.INACTIVE,
                     metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add a connection between capsule nodes.
        
        Args:
            source_node_id: ID of the source node
            target_node_id: ID of the target node
            connection_type: Type of connection
            strength: Strength of the connection
            state: State of the connection
            metadata: Additional metadata for this connection
            
        Returns:
            ID of the created connection, or None if the nodes were not found
        """
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            return None
            
        # Create connection ID
        connection_id = str(uuid.uuid4())
        
        # Create connection
        connection = CapsuleConnection(
            connection_id=connection_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            connection_type=connection_type,
            strength=strength,
            state=state,
            metadata=metadata or {}
        )
        
        # Update control points
        self._update_connection_control_points(connection)
        
        # Add connection
        self.connections[connection_id] = connection
        
        # Update node connections
        self.nodes[source_node_id].connections.append(connection_id)
        self.nodes[target_node_id].connections.append(connection_id)
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "connection_added",
            "connection_id": connection_id,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "connection_type": connection_type.value
        })
        
        return connection_id
    
    def remove_connection(self, connection_id: str) -> bool:
        """
        Remove a connection between capsule nodes.
        
        Args:
            connection_id: ID of the connection to remove
            
        Returns:
            True if the connection was removed, False if not found
        """
        if connection_id not in self.connections:
            return False
            
        connection = self.connections[connection_id]
        
        # Remove connection from nodes
        if connection.source_node_id in self.nodes:
            if connection_id in self.nodes[connection.source_node_id].connections:
                self.nodes[connection.source_node_id].connections.remove(connection_id)
                
        if connection.target_node_id in self.nodes:
            if connection_id in self.nodes[connection.target_node_id].connections:
                self.nodes[connection.target_node_id].connections.remove(connection_id)
                
        # Remove connection
        del self.connections[connection_id]
        
        # Remove from selected connections
        if connection_id in self.selected_connections:
            self.selected_connections.remove(connection_id)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "connection_removed",
            "connection_id": connection_id,
            "source_node_id": connection.source_node_id,
            "target_node_id": connection.target_node_id
        })
        
        return True
    
    def update_connection_state(self, connection_id: str, state: ConnectionState) -> bool:
        """
        Update the state of a connection.
        
        Args:
            connection_id: ID of the connection
            state: New state of the connection
            
        Returns:
            True if the state was updated, False if the connection was not found
        """
        if connection_id not in self.connections:
            return False
            
        connection = self.connections[connection_id]
        old_state = connection.state
        
        # Update state
        connection.state = state
        connection.last_update = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "connection_state_changed",
            "connection_id": connection_id,
            "old_state": old_state.value,
            "new_state": state.value
        })
        
        return True
    
    def select_connection(self, connection_id: str, add_to_selection: bool = False) -> bool:
        """
        Select a connection.
        
        Args:
            connection_id: ID of the connection to select
            add_to_selection: Whether to add to the current selection (True) or replace it (False)
            
        Returns:
            True if the connection was selected, False if not found
        """
        if connection_id not in self.connections:
            return False
            
        # Clear selection if not adding to it
        if not add_to_selection:
            self.clear_selection()
            
        # Select connection
        self.connections[connection_id].is_selected = True
        self.selected_connections.add(connection_id)
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "connection_selected",
            "connection_id": connection_id,
            "add_to_selection": add_to_selection
        })
        
        return True
    
    def deselect_connection(self, connection_id: str) -> bool:
        """
        Deselect a connection.
        
        Args:
            connection_id: ID of the connection to deselect
            
        Returns:
            True if the connection was deselected, False if not found
        """
        if connection_id not in self.connections:
            return False
            
        # Deselect connection
        self.connections[connection_id].is_selected = False
        
        if connection_id in self.selected_connections:
            self.selected_connections.remove(connection_id)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "connection_deselected",
            "connection_id": connection_id
        })
        
        return True
    
    def clear_selection(self) -> None:
        """Clear all selections."""
        # Deselect all nodes
        for node_id in self.selected_nodes:
            if node_id in self.nodes:
                self.nodes[node_id].is_selected = False
                self.nodes[node_id].z_index = 1
                
        # Deselect all connections
        for connection_id in self.selected_connections:
            if connection_id in self.connections:
                self.connections[connection_id].is_selected = False
                
        # Clear selection sets
        self.selected_nodes.clear()
        self.selected_connections.clear()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "selection_cleared"
        })
    
    def start_connection_creation(self, source_node_id: str) -> bool:
        """
        Start creating a new connection.
        
        Args:
            source_node_id: ID of the source node
            
        Returns:
            True if connection creation was started, False if the node was not found
        """
        if source_node_id not in self.nodes:
            return False
            
        # Cancel any existing pending connection
        if self.pending_connection:
            self.cancel_connection_creation()
            
        # Create pending connection
        self.pending_connection = {
            "source_node_id": source_node_id,
            "target_position": self.nodes[source_node_id].position,  # Start at source node
            "connection_type": ConnectionType.DATA_FLOW,  # Default type
            "start_time": time.time()
        }
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "connection_creation_started",
            "source_node_id": source_node_id
        })
        
        return True
    
    def update_pending_connection(self, target_position: Tuple[float, float]) -> None:
        """
        Update the target position of the pending connection.
        
        Args:
            target_position: New target position (x, y)
        """
        if not self.pending_connection:
            return
            
        # Update target position
        self.pending_connection["target_position"] = target_position
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "pending_connection_updated",
            "source_node_id": self.pending_connection["source_node_id"],
            "target_position": target_position
        })
    
    def complete_connection_creation(self, target_node_id: str, connection_type: Optional[ConnectionType] = None) -> Optional[str]:
        """
        Complete the creation of a pending connection.
        
        Args:
            target_node_id: ID of the target node
            connection_type: Optional type of connection (defaults to the pending connection type)
            
        Returns:
            ID of the created connection, or None if creation failed
        """
        if not self.pending_connection or target_node_id not in self.nodes:
            return None
            
        source_node_id = self.pending_connection["source_node_id"]
        
        # Don't allow self-connections
        if source_node_id == target_node_id:
            self.cancel_connection_creation()
            return None
            
        # Use specified connection type or default from pending connection
        connection_type = connection_type or self.pending_connection["connection_type"]
        
        # Create the connection
        connection_id = self.add_connection(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            connection_type=connection_type
        )
        
        # Clear pending connection
        self.pending_connection = None
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "connection_creation_completed",
            "connection_id": connection_id,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id
        })
        
        return connection_id
    
    def cancel_connection_creation(self) -> None:
        """Cancel the creation of a pending connection."""
        if not self.pending_connection:
            return
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "connection_creation_cancelled",
            "source_node_id": self.pending_connection["source_node_id"]
        })
        
        # Clear pending connection
        self.pending_connection = None
    
    def get_node(self, node_id: str) -> Optional[CapsuleNode]:
        """
        Get a node by ID.
        
        Args:
            node_id: ID of the node
            
        Returns:
            The node, or None if not found
        """
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[CapsuleNode]:
        """
        Get all nodes.
        
        Returns:
            List of all nodes
        """
        return list(self.nodes.values())
    
    def get_connection(self, connection_id: str) -> Optional[CapsuleConnection]:
        """
        Get a connection by ID.
        
        Args:
            connection_id: ID of the connection
            
        Returns:
            The connection, or None if not found
        """
        return self.connections.get(connection_id)
    
    def get_all_connections(self) -> List[CapsuleConnection]:
        """
        Get all connections.
        
        Returns:
            List of all connections
        """
        return list(self.connections.values())
    
    def get_node_connections(self, node_id: str) -> List[CapsuleConnection]:
        """
        Get all connections for a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of all connections for the node
        """
        if node_id not in self.nodes:
            return []
            
        node = self.nodes[node_id]
        return [self.connections[conn_id] for conn_id in node.connections if conn_id in self.connections]
    
    def get_node_by_capsule(self, capsule_id: str) -> Optional[CapsuleNode]:
        """
        Get a node by its associated capsule ID.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            The node, or None if not found
        """
        for node in self.nodes.values():
            if node.capsule_id == capsule_id:
                return node
                
        return None
    
    def get_connection_path(self, connection_id: str) -> Optional[str]:
        """
        Get SVG path for a connection.
        
        Args:
            connection_id: ID of the connection
            
        Returns:
            SVG path string, or None if the connection was not found
        """
        if connection_id not in self.connections:
            return None
            
        connection = self.connections[connection_id]
        
        # Get source and target nodes
        if connection.source_node_id not in self.nodes or connection.target_node_id not in self.nodes:
            return None
            
        source_node = self.nodes[connection.source_node_id]
        target_node = self.nodes[connection.target_node_id]
        
        # Get source and target positions
        source_x, source_y = source_node.position
        source_width, source_height = source_node.size
        
        target_x, target_y = target_node.position
        target_width, target_height = target_node.size
        
        # Calculate source and target centers
        source_center_x = source_x + source_width / 2
        source_center_y = source_y + source_height / 2
        
        target_center_x = target_x + target_width / 2
        target_center_y = target_y + target_height / 2
        
        # If we have control points, use them
        if connection.control_points and len(connection.control_points) >= 2:
            cp1_x, cp1_y = connection.control_points[0]
            cp2_x, cp2_y = connection.control_points[1]
            
            # Create cubic bezier curve
            path = f"M {source_center_x} {source_center_y} "
            path += f"C {cp1_x} {cp1_y}, {cp2_x} {cp2_y}, {target_center_x} {target_center_y}"
            
            return path
        else:
            # Create simple line
            path = f"M {source_center_x} {source_center_y} "
            path += f"L {target_center_x} {target_center_y}"
            
            return path
    
    def get_connection_style(self, connection_id: str) -> Optional[Dict[str, str]]:
        """
        Get CSS style for a connection.
        
        Args:
            connection_id: ID of the connection
            
        Returns:
            CSS style dictionary, or None if the connection was not found
        """
        if connection_id not in self.connections:
            return None
            
        connection = self.connections[connection_id]
        style = {}
        
        # Set stroke based on connection type
        if connection.connection_type == ConnectionType.DATA_FLOW:
            style["stroke"] = "#3498db"  # Blue
        elif connection.connection_type == ConnectionType.CONTROL_FLOW:
            style["stroke"] = "#e74c3c"  # Red
        elif connection.connection_type == ConnectionType.TRIGGER:
            style["stroke"] = "#f39c12"  # Orange
        elif connection.connection_type == ConnectionType.DEPENDENCY:
            style["stroke"] = "#9b59b6"  # Purple
        elif connection.connection_type == ConnectionType.COLLABORATION:
            style["stroke"] = "#2ecc71"  # Green
        else:
            style["stroke"] = "#95a5a6"  # Gray
            
        # Set stroke width based on connection strength
        if connection.strength == ConnectionStrength.WEAK:
            style["stroke-width"] = "1"
        elif connection.strength == ConnectionStrength.MODERATE:
            style["stroke-width"] = "2"
        elif connection.strength == ConnectionStrength.STRONG:
            style["stroke-width"] = "3"
        elif connection.strength == ConnectionStrength.CRITICAL:
            style["stroke-width"] = "4"
        else:
            style["stroke-width"] = "2"
            
        # Set stroke dash based on connection state
        if connection.state == ConnectionState.INACTIVE:
            style["stroke-dasharray"] = "5,5"
        elif connection.state == ConnectionState.ACTIVE:
            style["stroke-dasharray"] = "none"
        elif connection.state == ConnectionState.PENDING:
            style["stroke-dasharray"] = "10,5"
        elif connection.state == ConnectionState.FAILED:
            style["stroke-dasharray"] = "2,2"
            
        # Set opacity
        style["opacity"] = "0.8"
        
        # Set selected style
        if connection.is_selected:
            style["stroke-width"] = str(int(style["stroke-width"]) + 2)
            style["filter"] = "drop-shadow(0 0 3px rgba(255, 255, 255, 0.5))"
            
        return style
    
    def get_node_style(self, node_id: str) -> Optional[Dict[str, str]]:
        """
        Get CSS style for a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            CSS style dictionary, or None if the node was not found
        """
        if node_id not in self.nodes:
            return None
            
        node = self.nodes[node_id]
        style = {}
        
        # Set position and size
        x, y = node.position
        width, height = node.size
        
        style["left"] = f"{x}px"
        style["top"] = f"{y}px"
        style["width"] = f"{width}px"
        style["height"] = f"{height}px"
        
        # Set z-index
        style["z-index"] = str(node.z_index)
        
        # Set selected style
        if node.is_selected:
            style["border"] = "2px solid #3498db"
            style["box-shadow"] = "0 0 10px rgba(52, 152, 219, 0.5)"
        else:
            style["border"] = "1px solid #95a5a6"
            style["box-shadow"] = "0 0 5px rgba(0, 0, 0, 0.2)"
            
        # Set dragging style
        if node.is_dragging:
            style["opacity"] = "0.8"
            style["cursor"] = "grabbing"
        else:
            style["opacity"] = "1.0"
            style["cursor"] = "grab"
            
        return style
    
    def get_suggestions(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Get suggestions for connections from the Generative Layer.
        
        Args:
            node_id: ID of the node to get suggestions for
            
        Returns:
            List of suggestion dictionaries
        """
        if node_id not in self.nodes:
            return []
            
        node = self.nodes[node_id]
        suggestions = []
        
        # Call all suggestion providers
        for provider in self.suggestion_providers:
            try:
                provider_suggestions = provider({
                    "node_id": node_id,
                    "capsule_id": node.capsule_id,
                    "existing_connections": [self.connections[conn_id] for conn_id in node.connections if conn_id in self.connections],
                    "all_nodes": self.nodes,
                    "all_connections": self.connections
                })
                
                suggestions.extend(provider_suggestions)
            except Exception as e:
                self.logger.error(f"Error in suggestion provider: {e}")
                
        return suggestions
    
    def add_suggestion_provider(self, provider: Callable[[Dict[str, Any]], List[Dict[str, Any]]]) -> None:
        """
        Add a suggestion provider for the Generative Layer.
        
        Args:
            provider: Callback function that will be called with node data and should return suggestions
        """
        self.suggestion_providers.append(provider)
        
    def remove_suggestion_provider(self, provider: Callable[[Dict[str, Any]], List[Dict[str, Any]]]) -> None:
        """
        Remove a suggestion provider.
        
        Args:
            provider: The provider to remove
        """
        if provider in self.suggestion_providers:
            self.suggestion_providers.remove(provider)
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for panel events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for panel events.
        
        Args:
            listener: The listener to remove
        """
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            
    def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_data: The event data to dispatch
        """
        event_data["timestamp"] = time.time()
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in event listener: {e}")
                
    def _update_connection_control_points(self, connection: CapsuleConnection) -> None:
        """
        Update the control points for a connection.
        
        Args:
            connection: The connection to update
        """
        # Get source and target nodes
        if connection.source_node_id not in self.nodes or connection.target_node_id not in self.nodes:
            return
            
        source_node = self.nodes[connection.source_node_id]
        target_node = self.nodes[connection.target_node_id]
        
        # Get source and target positions
        source_x, source_y = source_node.position
        source_width, source_height = source_node.size
        
        target_x, target_y = target_node.position
        target_width, target_height = target_node.size
        
        # Calculate source and target centers
        source_center_x = source_x + source_width / 2
        source_center_y = source_y + source_height / 2
        
        target_center_x = target_x + target_width / 2
        target_center_y = target_y + target_height / 2
        
        # Calculate distance between nodes
        dx = target_center_x - source_center_x
        dy = target_center_y - source_center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Calculate control points (for a curved line)
        control_distance = distance / 3
        
        # Direction vector
        if distance > 0:
            dir_x = dx / distance
            dir_y = dy / distance
        else:
            dir_x = 0
            dir_y = 0
            
        # Perpendicular vector (for curve)
        perp_x = -dir_y
        perp_y = dir_x
        
        # Add some randomness to make multiple connections between the same nodes look different
        random_offset = hash(connection.connection_id) % 100 / 100.0 - 0.5  # -0.5 to 0.5
        curve_factor = 0.5 + random_offset * 0.3  # 0.35 to 0.65
        
        # Calculate control points
        cp1_x = source_center_x + dir_x * control_distance + perp_x * control_distance * curve_factor
        cp1_y = source_center_y + dir_y * control_distance + perp_y * control_distance * curve_factor
        
        cp2_x = target_center_x - dir_x * control_distance + perp_x * control_distance * curve_factor
        cp2_y = target_center_y - dir_y * control_distance + perp_y * control_distance * curve_factor
        
        # Update control points
        connection.control_points = [(cp1_x, cp1_y), (cp2_x, cp2_y)]
    
    def export_to_json(self) -> str:
        """
        Export the panel state to JSON.
        
        Returns:
            JSON string representation of the panel state
        """
        data = {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "connections": {conn_id: conn.to_dict() for conn_id, conn in self.connections.items()},
            "canvas_size": self.canvas_size,
            "view_position": self.view_position,
            "view_scale": self.view_scale,
            "is_composer_mode": self.is_composer_mode,
            "timestamp": time.time()
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_str: str) -> bool:
        """
        Import the panel state from JSON.
        
        Args:
            json_str: JSON string representation of the panel state
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            data = json.loads(json_str)
            
            # Clear current state
            self.nodes.clear()
            self.connections.clear()
            self.selected_nodes.clear()
            self.selected_connections.clear()
            self.pending_connection = None
            
            # Import nodes
            for node_id, node_data in data.get("nodes", {}).items():
                self.nodes[node_id] = CapsuleNode.from_dict(node_data)
                
                if self.nodes[node_id].is_selected:
                    self.selected_nodes.add(node_id)
                    
            # Import connections
            for conn_id, conn_data in data.get("connections", {}).items():
                self.connections[conn_id] = CapsuleConnection.from_dict(conn_data)
                
                if self.connections[conn_id].is_selected:
                    self.selected_connections.add(conn_id)
                    
            # Import canvas settings
            self.canvas_size = data.get("canvas_size", (2000, 2000))
            self.view_position = data.get("view_position", (0, 0))
            self.view_scale = data.get("view_scale", 1.0)
            self.is_composer_mode = data.get("is_composer_mode", False)
            
            # Dispatch event
            self._dispatch_event({
                "event_type": "state_imported"
            })
            
            return True
        except Exception as e:
            self.logger.error(f"Error importing panel state: {e}")
            return False
"""
