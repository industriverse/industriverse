"""
Workflow Canvas Component for the Workflow Automation Layer.

This module implements the interactive workflow canvas UI component that allows users
to visually design, edit, and monitor workflows. It provides a drag-and-drop interface
for workflow creation and a real-time visualization of workflow execution.

Key features:
- Interactive workflow design with drag-and-drop capabilities
- Real-time workflow execution visualization
- Support for all workflow node types and connections
- Integration with Dynamic Agent Capsules
- Trust-aware visualization with execution mode indicators
- Debug trace overlay for workflow forensics
"""

import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Callable

class WorkflowCanvasNode:
    """
    Represents a node in the workflow canvas.
    
    A node can represent a task, agent, decision point, or other workflow element.
    """
    
    def __init__(self, 
                node_id: str,
                node_type: str,
                position: Dict[str, float],
                data: Dict[str, Any],
                style: Dict[str, Any] = None):
        """
        Initialize a workflow canvas node.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of the node (task, agent, decision, etc.)
            position: Position of the node on the canvas (x, y coordinates)
            data: Data associated with the node
            style: Optional style information for the node
        """
        self.node_id = node_id
        self.node_type = node_type
        self.position = position
        self.data = data
        self.style = style or {}
        self.inputs = []
        self.outputs = []
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node to a dictionary.
        
        Returns:
            Dictionary representation of the node
        """
        return {
            "id": self.node_id,
            "type": self.node_type,
            "position": self.position,
            "data": self.data,
            "style": self.style
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowCanvasNode':
        """
        Create a node from a dictionary.
        
        Args:
            data: Dictionary representation of the node
            
        Returns:
            WorkflowCanvasNode instance
        """
        return cls(
            node_id=data["id"],
            node_type=data["type"],
            position=data["position"],
            data=data["data"],
            style=data.get("style", {})
        )


class WorkflowCanvasEdge:
    """
    Represents an edge (connection) between nodes in the workflow canvas.
    
    An edge connects two nodes and represents the flow of execution or data.
    """
    
    def __init__(self, 
                edge_id: str,
                source: str,
                target: str,
                source_handle: Optional[str] = None,
                target_handle: Optional[str] = None,
                data: Dict[str, Any] = None,
                style: Dict[str, Any] = None):
        """
        Initialize a workflow canvas edge.
        
        Args:
            edge_id: Unique identifier for the edge
            source: ID of the source node
            target: ID of the target node
            source_handle: Optional handle on the source node
            target_handle: Optional handle on the target node
            data: Optional data associated with the edge
            style: Optional style information for the edge
        """
        self.edge_id = edge_id
        self.source = source
        self.target = target
        self.source_handle = source_handle
        self.target_handle = target_handle
        self.data = data or {}
        self.style = style or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the edge to a dictionary.
        
        Returns:
            Dictionary representation of the edge
        """
        result = {
            "id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "data": self.data,
            "style": self.style
        }
        
        if self.source_handle:
            result["sourceHandle"] = self.source_handle
            
        if self.target_handle:
            result["targetHandle"] = self.target_handle
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowCanvasEdge':
        """
        Create an edge from a dictionary.
        
        Args:
            data: Dictionary representation of the edge
            
        Returns:
            WorkflowCanvasEdge instance
        """
        return cls(
            edge_id=data["id"],
            source=data["source"],
            target=data["target"],
            source_handle=data.get("sourceHandle"),
            target_handle=data.get("targetHandle"),
            data=data.get("data", {}),
            style=data.get("style", {})
        )


class WorkflowCanvas:
    """
    Represents the workflow canvas UI component.
    
    The workflow canvas allows users to visually design, edit, and monitor workflows.
    """
    
    def __init__(self, canvas_id: Optional[str] = None):
        """
        Initialize a workflow canvas.
        
        Args:
            canvas_id: Optional unique identifier for the canvas
        """
        self.canvas_id = canvas_id or f"canvas-{uuid.uuid4()}"
        self.nodes: Dict[str, WorkflowCanvasNode] = {}
        self.edges: Dict[str, WorkflowCanvasEdge] = {}
        self.viewport = {"x": 0, "y": 0, "zoom": 1}
        self.metadata = {
            "name": "Untitled Workflow",
            "description": "",
            "created": time.time(),
            "modified": time.time(),
            "version": "1.0"
        }
        self.execution_state = {
            "status": "not_started",
            "active_nodes": [],
            "completed_nodes": [],
            "error_nodes": [],
            "execution_mode": "manual"
        }
        self.debug_overlay = {
            "enabled": False,
            "trace_level": "standard",
            "visible_traces": []
        }
        
    def add_node(self, 
                node_type: str,
                position: Dict[str, float],
                data: Dict[str, Any],
                style: Dict[str, Any] = None,
                node_id: Optional[str] = None) -> WorkflowCanvasNode:
        """
        Add a node to the canvas.
        
        Args:
            node_type: Type of the node (task, agent, decision, etc.)
            position: Position of the node on the canvas (x, y coordinates)
            data: Data associated with the node
            style: Optional style information for the node
            node_id: Optional unique identifier for the node
            
        Returns:
            The created node
        """
        node_id = node_id or f"node-{uuid.uuid4()}"
        
        node = WorkflowCanvasNode(
            node_id=node_id,
            node_type=node_type,
            position=position,
            data=data,
            style=style
        )
        
        self.nodes[node_id] = node
        self.metadata["modified"] = time.time()
        
        return node
    
    def update_node(self, 
                   node_id: str,
                   updates: Dict[str, Any]) -> Optional[WorkflowCanvasNode]:
        """
        Update a node on the canvas.
        
        Args:
            node_id: ID of the node to update
            updates: Updates to apply to the node
            
        Returns:
            The updated node if successful, None otherwise
        """
        if node_id not in self.nodes:
            return None
        
        node = self.nodes[node_id]
        
        if "position" in updates:
            node.position = updates["position"]
            
        if "data" in updates:
            node.data.update(updates["data"])
            
        if "style" in updates:
            node.style.update(updates["style"])
            
        self.metadata["modified"] = time.time()
        
        return node
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the canvas.
        
        Args:
            node_id: ID of the node to remove
            
        Returns:
            True if successful, False otherwise
        """
        if node_id not in self.nodes:
            return False
        
        # Remove all edges connected to this node
        edges_to_remove = []
        
        for edge_id, edge in self.edges.items():
            if edge.source == node_id or edge.target == node_id:
                edges_to_remove.append(edge_id)
                
        for edge_id in edges_to_remove:
            del self.edges[edge_id]
        
        # Remove the node
        del self.nodes[node_id]
        
        self.metadata["modified"] = time.time()
        
        return True
    
    def add_edge(self, 
                source: str,
                target: str,
                source_handle: Optional[str] = None,
                target_handle: Optional[str] = None,
                data: Dict[str, Any] = None,
                style: Dict[str, Any] = None,
                edge_id: Optional[str] = None) -> Optional[WorkflowCanvasEdge]:
        """
        Add an edge to the canvas.
        
        Args:
            source: ID of the source node
            target: ID of the target node
            source_handle: Optional handle on the source node
            target_handle: Optional handle on the target node
            data: Optional data associated with the edge
            style: Optional style information for the edge
            edge_id: Optional unique identifier for the edge
            
        Returns:
            The created edge if successful, None otherwise
        """
        if source not in self.nodes or target not in self.nodes:
            return None
        
        edge_id = edge_id or f"edge-{uuid.uuid4()}"
        
        edge = WorkflowCanvasEdge(
            edge_id=edge_id,
            source=source,
            target=target,
            source_handle=source_handle,
            target_handle=target_handle,
            data=data or {},
            style=style or {}
        )
        
        self.edges[edge_id] = edge
        self.metadata["modified"] = time.time()
        
        return edge
    
    def update_edge(self, 
                   edge_id: str,
                   updates: Dict[str, Any]) -> Optional[WorkflowCanvasEdge]:
        """
        Update an edge on the canvas.
        
        Args:
            edge_id: ID of the edge to update
            updates: Updates to apply to the edge
            
        Returns:
            The updated edge if successful, None otherwise
        """
        if edge_id not in self.edges:
            return None
        
        edge = self.edges[edge_id]
        
        if "source" in updates and updates["source"] in self.nodes:
            edge.source = updates["source"]
            
        if "target" in updates and updates["target"] in self.nodes:
            edge.target = updates["target"]
            
        if "sourceHandle" in updates:
            edge.source_handle = updates["sourceHandle"]
            
        if "targetHandle" in updates:
            edge.target_handle = updates["targetHandle"]
            
        if "data" in updates:
            edge.data.update(updates["data"])
            
        if "style" in updates:
            edge.style.update(updates["style"])
            
        self.metadata["modified"] = time.time()
        
        return edge
    
    def remove_edge(self, edge_id: str) -> bool:
        """
        Remove an edge from the canvas.
        
        Args:
            edge_id: ID of the edge to remove
            
        Returns:
            True if successful, False otherwise
        """
        if edge_id not in self.edges:
            return False
        
        del self.edges[edge_id]
        self.metadata["modified"] = time.time()
        
        return True
    
    def update_viewport(self, viewport: Dict[str, float]) -> Dict[str, float]:
        """
        Update the canvas viewport.
        
        Args:
            viewport: New viewport information (x, y, zoom)
            
        Returns:
            The updated viewport
        """
        self.viewport.update(viewport)
        return self.viewport
    
    def update_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the canvas metadata.
        
        Args:
            metadata: New metadata information
            
        Returns:
            The updated metadata
        """
        self.metadata.update(metadata)
        self.metadata["modified"] = time.time()
        return self.metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the canvas to a dictionary.
        
        Returns:
            Dictionary representation of the canvas
        """
        return {
            "id": self.canvas_id,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges.values()],
            "viewport": self.viewport,
            "metadata": self.metadata,
            "execution_state": self.execution_state,
            "debug_overlay": self.debug_overlay
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowCanvas':
        """
        Create a canvas from a dictionary.
        
        Args:
            data: Dictionary representation of the canvas
            
        Returns:
            WorkflowCanvas instance
        """
        canvas = cls(canvas_id=data.get("id"))
        
        # Set metadata
        if "metadata" in data:
            canvas.metadata = data["metadata"]
            
        # Set viewport
        if "viewport" in data:
            canvas.viewport = data["viewport"]
            
        # Set execution state
        if "execution_state" in data:
            canvas.execution_state = data["execution_state"]
            
        # Set debug overlay
        if "debug_overlay" in data:
            canvas.debug_overlay = data["debug_overlay"]
        
        # Add nodes
        for node_data in data.get("nodes", []):
            node = WorkflowCanvasNode.from_dict(node_data)
            canvas.nodes[node.node_id] = node
            
        # Add edges
        for edge_data in data.get("edges", []):
            edge = WorkflowCanvasEdge.from_dict(edge_data)
            canvas.edges[edge.edge_id] = edge
            
        return canvas
    
    def update_execution_state(self, 
                              status: Optional[str] = None,
                              active_nodes: Optional[List[str]] = None,
                              completed_nodes: Optional[List[str]] = None,
                              error_nodes: Optional[List[str]] = None,
                              execution_mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the execution state of the canvas.
        
        Args:
            status: Optional new status
            active_nodes: Optional list of active node IDs
            completed_nodes: Optional list of completed node IDs
            error_nodes: Optional list of error node IDs
            execution_mode: Optional execution mode
            
        Returns:
            The updated execution state
        """
        if status is not None:
            self.execution_state["status"] = status
            
        if active_nodes is not None:
            self.execution_state["active_nodes"] = active_nodes
            
        if completed_nodes is not None:
            self.execution_state["completed_nodes"] = completed_nodes
            
        if error_nodes is not None:
            self.execution_state["error_nodes"] = error_nodes
            
        if execution_mode is not None:
            self.execution_state["execution_mode"] = execution_mode
            
        return self.execution_state
    
    def update_debug_overlay(self, 
                            enabled: Optional[bool] = None,
                            trace_level: Optional[str] = None,
                            visible_traces: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update the debug overlay settings.
        
        Args:
            enabled: Optional flag to enable/disable the overlay
            trace_level: Optional trace level (minimal, standard, verbose, forensic)
            visible_traces: Optional list of visible trace IDs
            
        Returns:
            The updated debug overlay settings
        """
        if enabled is not None:
            self.debug_overlay["enabled"] = enabled
            
        if trace_level is not None:
            self.debug_overlay["trace_level"] = trace_level
            
        if visible_traces is not None:
            self.debug_overlay["visible_traces"] = visible_traces
            
        return self.debug_overlay
    
    def export_to_workflow_manifest(self) -> Dict[str, Any]:
        """
        Export the canvas to a workflow manifest.
        
        Returns:
            Workflow manifest dictionary
        """
        # This is a simplified implementation
        # In a real system, this would convert the visual representation
        # to a proper workflow manifest format
        
        tasks = []
        connections = []
        
        # Convert nodes to tasks
        for node_id, node in self.nodes.items():
            if node.node_type == "task":
                task = {
                    "id": node_id,
                    "type": node.data.get("task_type", "generic"),
                    "name": node.data.get("name", "Unnamed Task"),
                    "description": node.data.get("description", ""),
                    "config": node.data.get("config", {})
                }
                tasks.append(task)
        
        # Convert edges to connections
        for edge_id, edge in self.edges.items():
            connection = {
                "id": edge_id,
                "source": edge.source,
                "target": edge.target,
                "condition": edge.data.get("condition", None)
            }
            connections.append(connection)
        
        # Create the manifest
        manifest = {
            "id": f"workflow-{uuid.uuid4()}",
            "name": self.metadata.get("name", "Untitled Workflow"),
            "description": self.metadata.get("description", ""),
            "version": self.metadata.get("version", "1.0"),
            "tasks": tasks,
            "connections": connections,
            "config": {
                "execution_mode": self.execution_state.get("execution_mode", "manual"),
                "debug_trace": {
                    "enabled": self.debug_overlay.get("enabled", False),
                    "level": self.debug_overlay.get("trace_level", "standard")
                }
            }
        }
        
        return manifest
    
    def import_from_workflow_manifest(self, manifest: Dict[str, Any]) -> bool:
        """
        Import a workflow manifest into the canvas.
        
        Args:
            manifest: Workflow manifest dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear existing canvas
            self.nodes = {}
            self.edges = {}
            
            # Update metadata
            self.metadata["name"] = manifest.get("name", "Untitled Workflow")
            self.metadata["description"] = manifest.get("description", "")
            self.metadata["version"] = manifest.get("version", "1.0")
            self.metadata["modified"] = time.time()
            
            # Update execution state
            config = manifest.get("config", {})
            self.execution_state["execution_mode"] = config.get("execution_mode", "manual")
            
            # Update debug overlay
            debug_trace = config.get("debug_trace", {})
            self.debug_overlay["enabled"] = debug_trace.get("enabled", False)
            self.debug_overlay["trace_level"] = debug_trace.get("level", "standard")
            
            # Position calculation helper
            def calculate_position(index, total):
                # Simple grid layout
                cols = max(1, min(5, total))
                rows = (total + cols - 1) // cols
                
                col = index % cols
                row = index // cols
                
                return {
                    "x": 100 + col * 250,
                    "y": 100 + row * 150
                }
            
            # Add tasks as nodes
            tasks = manifest.get("tasks", [])
            for i, task in enumerate(tasks):
                position = calculate_position(i, len(tasks))
                
                node_data = {
                    "task_type": task.get("type", "generic"),
                    "name": task.get("name", "Unnamed Task"),
                    "description": task.get("description", ""),
                    "config": task.get("config", {})
                }
                
                self.add_node(
                    node_type="task",
                    position=position,
                    data=node_data,
                    node_id=task.get("id")
                )
            
            # Add connections as edges
            connections = manifest.get("connections", [])
            for connection in connections:
                source = connection.get("source")
                target = connection.get("target")
                
                if source in self.nodes and target in self.nodes:
                    edge_data = {}
                    
                    if "condition" in connection and connection["condition"]:
                        edge_data["condition"] = connection["condition"]
                    
                    self.add_edge(
                        source=source,
                        target=target,
                        data=edge_data,
                        edge_id=connection.get("id")
                    )
            
            return True
        except Exception as e:
            print(f"Error importing workflow manifest: {e}")
            return False


class WorkflowCanvasManager:
    """
    Manages workflow canvases for the Workflow Automation Layer.
    
    This class provides methods for creating, managing, and persisting
    workflow canvases.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the Workflow Canvas Manager.
        
        Args:
            storage_path: Optional path for storing canvases
        """
        self.storage_path = storage_path or "/data/workflow_canvases"
        self.canvases: Dict[str, WorkflowCanvas] = {}
        self._load_canvases()
        
    def _load_canvases(self):
        """Load canvases from persistent storage."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.storage_path, filename), 'r') as f:
                        canvas_data = json.load(f)
                        canvas = WorkflowCanvas.from_dict(canvas_data)
                        self.canvases[canvas.canvas_id] = canvas
                except Exception as e:
                    print(f"Error loading canvas {filename}: {e}")
    
    def _store_canvas(self, canvas: WorkflowCanvas):
        """
        Store a canvas to persistent storage.
        
        Args:
            canvas: The canvas to store
        """
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
        
        file_path = os.path.join(self.storage_path, f"{canvas.canvas_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(canvas.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error storing canvas: {e}")
    
    def create_canvas(self, 
                     name: str = "Untitled Workflow",
                     description: str = "",
                     canvas_id: Optional[str] = None) -> WorkflowCanvas:
        """
        Create a new workflow canvas.
        
        Args:
            name: Name for the canvas
            description: Description for the canvas
            canvas_id: Optional unique identifier for the canvas
            
        Returns:
            The created canvas
        """
        canvas = WorkflowCanvas(canvas_id=canvas_id)
        canvas.metadata["name"] = name
        canvas.metadata["description"] = description
        
        self.canvases[canvas.canvas_id] = canvas
        self._store_canvas(canvas)
        
        return canvas
    
    def get_canvas(self, canvas_id: str) -> Optional[WorkflowCanvas]:
        """
        Get a canvas by its identifier.
        
        Args:
            canvas_id: Identifier for the canvas
            
        Returns:
            The canvas if found, None otherwise
        """
        return self.canvases.get(canvas_id)
    
    def list_canvases(self) -> List[Dict[str, Any]]:
        """
        List all available canvases.
        
        Returns:
            List of canvas metadata
        """
        return [
            {
                "id": canvas.canvas_id,
                "name": canvas.metadata.get("name", "Untitled Workflow"),
                "description": canvas.metadata.get("description", ""),
                "created": canvas.metadata.get("created", 0),
                "modified": canvas.metadata.get("modified", 0),
                "version": canvas.metadata.get("version", "1.0"),
                "status": canvas.execution_state.get("status", "not_started")
            }
            for canvas in self.canvases.values()
        ]
    
    def update_canvas(self, canvas_id: str, updates: Dict[str, Any]) -> Optional[WorkflowCanvas]:
        """
        Update a canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            updates: Updates to apply to the canvas
            
        Returns:
            The updated canvas if successful, None otherwise
        """
        canvas = self.get_canvas(canvas_id)
        if not canvas:
            return None
        
        # Apply updates
        if "metadata" in updates:
            canvas.update_metadata(updates["metadata"])
            
        if "viewport" in updates:
            canvas.update_viewport(updates["viewport"])
            
        if "execution_state" in updates:
            canvas.update_execution_state(**updates["execution_state"])
            
        if "debug_overlay" in updates:
            canvas.update_debug_overlay(**updates["debug_overlay"])
            
        # Add/update nodes
        if "nodes" in updates:
            for node_update in updates["nodes"]:
                if "id" in node_update and node_update["id"] in canvas.nodes:
                    # Update existing node
                    canvas.update_node(node_update["id"], node_update)
                else:
                    # Add new node
                    canvas.add_node(
                        node_type=node_update.get("type", "task"),
                        position=node_update.get("position", {"x": 0, "y": 0}),
                        data=node_update.get("data", {}),
                        style=node_update.get("style", {}),
                        node_id=node_update.get("id")
                    )
        
        # Add/update edges
        if "edges" in updates:
            for edge_update in updates["edges"]:
                if "id" in edge_update and edge_update["id"] in canvas.edges:
                    # Update existing edge
                    canvas.update_edge(edge_update["id"], edge_update)
                else:
                    # Add new edge
                    canvas.add_edge(
                        source=edge_update.get("source"),
                        target=edge_update.get("target"),
                        source_handle=edge_update.get("sourceHandle"),
                        target_handle=edge_update.get("targetHandle"),
                        data=edge_update.get("data", {}),
                        style=edge_update.get("style", {}),
                        edge_id=edge_update.get("id")
                    )
        
        # Remove nodes
        if "remove_nodes" in updates:
            for node_id in updates["remove_nodes"]:
                canvas.remove_node(node_id)
        
        # Remove edges
        if "remove_edges" in updates:
            for edge_id in updates["remove_edges"]:
                canvas.remove_edge(edge_id)
        
        # Store the updated canvas
        self._store_canvas(canvas)
        
        return canvas
    
    def delete_canvas(self, canvas_id: str) -> bool:
        """
        Delete a canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            
        Returns:
            True if successful, False otherwise
        """
        if canvas_id not in self.canvases:
            return False
        
        # Remove from memory
        del self.canvases[canvas_id]
        
        # Remove from storage
        file_path = os.path.join(self.storage_path, f"{canvas_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting canvas: {e}")
            return False
    
    def export_canvas_to_workflow_manifest(self, canvas_id: str) -> Optional[Dict[str, Any]]:
        """
        Export a canvas to a workflow manifest.
        
        Args:
            canvas_id: Identifier for the canvas
            
        Returns:
            Workflow manifest dictionary if successful, None otherwise
        """
        canvas = self.get_canvas(canvas_id)
        if not canvas:
            return None
        
        return canvas.export_to_workflow_manifest()
    
    def import_workflow_manifest_to_canvas(self, 
                                         manifest: Dict[str, Any],
                                         canvas_id: Optional[str] = None) -> Optional[WorkflowCanvas]:
        """
        Import a workflow manifest into a canvas.
        
        Args:
            manifest: Workflow manifest dictionary
            canvas_id: Optional identifier for the canvas
            
        Returns:
            The updated canvas if successful, None otherwise
        """
        # Create a new canvas or use an existing one
        canvas = None
        
        if canvas_id and canvas_id in self.canvases:
            canvas = self.canvases[canvas_id]
        else:
            canvas = self.create_canvas(
                name=manifest.get("name", "Imported Workflow"),
                description=manifest.get("description", ""),
                canvas_id=canvas_id
            )
        
        # Import the manifest
        success = canvas.import_from_workflow_manifest(manifest)
        
        if success:
            # Store the updated canvas
            self._store_canvas(canvas)
            return canvas
        else:
            return None
    
    def update_canvas_execution_state(self, 
                                     canvas_id: str,
                                     status: Optional[str] = None,
                                     active_nodes: Optional[List[str]] = None,
                                     completed_nodes: Optional[List[str]] = None,
                                     error_nodes: Optional[List[str]] = None,
                                     execution_mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update the execution state of a canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            status: Optional new status
            active_nodes: Optional list of active node IDs
            completed_nodes: Optional list of completed node IDs
            error_nodes: Optional list of error node IDs
            execution_mode: Optional execution mode
            
        Returns:
            The updated execution state if successful, None otherwise
        """
        canvas = self.get_canvas(canvas_id)
        if not canvas:
            return None
        
        execution_state = canvas.update_execution_state(
            status=status,
            active_nodes=active_nodes,
            completed_nodes=completed_nodes,
            error_nodes=error_nodes,
            execution_mode=execution_mode
        )
        
        # Store the updated canvas
        self._store_canvas(canvas)
        
        return execution_state
    
    def update_canvas_debug_overlay(self, 
                                   canvas_id: str,
                                   enabled: Optional[bool] = None,
                                   trace_level: Optional[str] = None,
                                   visible_traces: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Update the debug overlay settings of a canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            enabled: Optional flag to enable/disable the overlay
            trace_level: Optional trace level (minimal, standard, verbose, forensic)
            visible_traces: Optional list of visible trace IDs
            
        Returns:
            The updated debug overlay settings if successful, None otherwise
        """
        canvas = self.get_canvas(canvas_id)
        if not canvas:
            return None
        
        debug_overlay = canvas.update_debug_overlay(
            enabled=enabled,
            trace_level=trace_level,
            visible_traces=visible_traces
        )
        
        # Store the updated canvas
        self._store_canvas(canvas)
        
        return debug_overlay


class WorkflowCanvasService:
    """
    Service for integrating the workflow canvas with the Workflow Automation Layer.
    
    This class provides methods for synchronizing the canvas with workflow execution
    and handling user interactions.
    """
    
    def __init__(self, canvas_manager: WorkflowCanvasManager):
        """
        Initialize the Workflow Canvas Service.
        
        Args:
            canvas_manager: Workflow Canvas Manager instance
        """
        self.canvas_manager = canvas_manager
        self.execution_callbacks: Dict[str, List[Callable]] = {}
        
    def register_execution_callback(self, canvas_id: str, callback: Callable):
        """
        Register a callback for workflow execution events.
        
        Args:
            canvas_id: Identifier for the canvas
            callback: Callback function
        """
        if canvas_id not in self.execution_callbacks:
            self.execution_callbacks[canvas_id] = []
            
        self.execution_callbacks[canvas_id].append(callback)
    
    def unregister_execution_callback(self, canvas_id: str, callback: Callable) -> bool:
        """
        Unregister a callback for workflow execution events.
        
        Args:
            canvas_id: Identifier for the canvas
            callback: Callback function
            
        Returns:
            True if successful, False otherwise
        """
        if canvas_id not in self.execution_callbacks:
            return False
        
        if callback in self.execution_callbacks[canvas_id]:
            self.execution_callbacks[canvas_id].remove(callback)
            return True
        
        return False
    
    def notify_execution_event(self, 
                              canvas_id: str,
                              event_type: str,
                              event_data: Dict[str, Any]):
        """
        Notify execution callbacks of an event.
        
        Args:
            canvas_id: Identifier for the canvas
            event_type: Type of the event
            event_data: Event data
        """
        if canvas_id in self.execution_callbacks:
            for callback in self.execution_callbacks[canvas_id]:
                try:
                    callback(event_type, event_data)
                except Exception as e:
                    print(f"Error in execution callback: {e}")
    
    def start_workflow_execution(self, 
                               canvas_id: str,
                               execution_config: Dict[str, Any] = None) -> bool:
        """
        Start workflow execution for a canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            execution_config: Optional execution configuration
            
        Returns:
            True if successful, False otherwise
        """
        canvas = self.canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return False
        
        # Export the canvas to a workflow manifest
        manifest = canvas.export_to_workflow_manifest()
        
        # Update execution state
        self.canvas_manager.update_canvas_execution_state(
            canvas_id=canvas_id,
            status="running",
            active_nodes=[],
            completed_nodes=[],
            error_nodes=[]
        )
        
        # Notify execution start
        self.notify_execution_event(
            canvas_id=canvas_id,
            event_type="execution_start",
            event_data={
                "manifest": manifest,
                "config": execution_config or {}
            }
        )
        
        return True
    
    def stop_workflow_execution(self, canvas_id: str) -> bool:
        """
        Stop workflow execution for a canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            
        Returns:
            True if successful, False otherwise
        """
        canvas = self.canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return False
        
        # Update execution state
        self.canvas_manager.update_canvas_execution_state(
            canvas_id=canvas_id,
            status="stopped"
        )
        
        # Notify execution stop
        self.notify_execution_event(
            canvas_id=canvas_id,
            event_type="execution_stop",
            event_data={}
        )
        
        return True
    
    def update_execution_progress(self, 
                                canvas_id: str,
                                active_nodes: List[str],
                                completed_nodes: List[str],
                                error_nodes: List[str] = None) -> bool:
        """
        Update execution progress for a canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            active_nodes: List of active node IDs
            completed_nodes: List of completed node IDs
            error_nodes: Optional list of error node IDs
            
        Returns:
            True if successful, False otherwise
        """
        canvas = self.canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return False
        
        # Update execution state
        self.canvas_manager.update_canvas_execution_state(
            canvas_id=canvas_id,
            active_nodes=active_nodes,
            completed_nodes=completed_nodes,
            error_nodes=error_nodes or []
        )
        
        # Notify execution progress
        self.notify_execution_event(
            canvas_id=canvas_id,
            event_type="execution_progress",
            event_data={
                "active_nodes": active_nodes,
                "completed_nodes": completed_nodes,
                "error_nodes": error_nodes or []
            }
        )
        
        return True
    
    def complete_workflow_execution(self, 
                                  canvas_id: str,
                                  success: bool,
                                  result: Dict[str, Any] = None) -> bool:
        """
        Complete workflow execution for a canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            success: Whether the execution was successful
            result: Optional execution result
            
        Returns:
            True if successful, False otherwise
        """
        canvas = self.canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return False
        
        # Update execution state
        self.canvas_manager.update_canvas_execution_state(
            canvas_id=canvas_id,
            status="completed" if success else "failed"
        )
        
        # Notify execution completion
        self.notify_execution_event(
            canvas_id=canvas_id,
            event_type="execution_complete",
            event_data={
                "success": success,
                "result": result or {}
            }
        )
        
        return True
    
    def update_debug_traces(self, 
                          canvas_id: str,
                          traces: List[Dict[str, Any]]) -> bool:
        """
        Update debug traces for a canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            traces: List of debug traces
            
        Returns:
            True if successful, False otherwise
        """
        canvas = self.canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return False
        
        # Update debug overlay
        trace_ids = [trace["id"] for trace in traces]
        self.canvas_manager.update_canvas_debug_overlay(
            canvas_id=canvas_id,
            visible_traces=trace_ids
        )
        
        # Notify debug trace update
        self.notify_execution_event(
            canvas_id=canvas_id,
            event_type="debug_trace_update",
            event_data={
                "traces": traces
            }
        )
        
        return True
    
    def handle_user_interaction(self, 
                              canvas_id: str,
                              interaction_type: str,
                              interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user interaction with the canvas.
        
        Args:
            canvas_id: Identifier for the canvas
            interaction_type: Type of the interaction
            interaction_data: Interaction data
            
        Returns:
            Response data
        """
        canvas = self.canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return {"success": False, "error": "Canvas not found"}
        
        if interaction_type == "add_node":
            node = canvas.add_node(
                node_type=interaction_data.get("type", "task"),
                position=interaction_data.get("position", {"x": 0, "y": 0}),
                data=interaction_data.get("data", {}),
                style=interaction_data.get("style", {})
            )
            
            self.canvas_manager._store_canvas(canvas)
            
            return {
                "success": True,
                "node": node.to_dict()
            }
            
        elif interaction_type == "update_node":
            node_id = interaction_data.get("id")
            updates = interaction_data.get("updates", {})
            
            node = canvas.update_node(node_id, updates)
            
            if node:
                self.canvas_manager._store_canvas(canvas)
                
                return {
                    "success": True,
                    "node": node.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": "Node not found"
                }
                
        elif interaction_type == "remove_node":
            node_id = interaction_data.get("id")
            
            success = canvas.remove_node(node_id)
            
            if success:
                self.canvas_manager._store_canvas(canvas)
                
                return {
                    "success": True
                }
            else:
                return {
                    "success": False,
                    "error": "Node not found"
                }
                
        elif interaction_type == "add_edge":
            edge = canvas.add_edge(
                source=interaction_data.get("source"),
                target=interaction_data.get("target"),
                source_handle=interaction_data.get("sourceHandle"),
                target_handle=interaction_data.get("targetHandle"),
                data=interaction_data.get("data", {}),
                style=interaction_data.get("style", {})
            )
            
            if edge:
                self.canvas_manager._store_canvas(canvas)
                
                return {
                    "success": True,
                    "edge": edge.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid edge"
                }
                
        elif interaction_type == "update_edge":
            edge_id = interaction_data.get("id")
            updates = interaction_data.get("updates", {})
            
            edge = canvas.update_edge(edge_id, updates)
            
            if edge:
                self.canvas_manager._store_canvas(canvas)
                
                return {
                    "success": True,
                    "edge": edge.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": "Edge not found"
                }
                
        elif interaction_type == "remove_edge":
            edge_id = interaction_data.get("id")
            
            success = canvas.remove_edge(edge_id)
            
            if success:
                self.canvas_manager._store_canvas(canvas)
                
                return {
                    "success": True
                }
            else:
                return {
                    "success": False,
                    "error": "Edge not found"
                }
                
        elif interaction_type == "update_viewport":
            viewport = interaction_data.get("viewport", {})
            
            updated_viewport = canvas.update_viewport(viewport)
            self.canvas_manager._store_canvas(canvas)
            
            return {
                "success": True,
                "viewport": updated_viewport
            }
            
        elif interaction_type == "update_metadata":
            metadata = interaction_data.get("metadata", {})
            
            updated_metadata = canvas.update_metadata(metadata)
            self.canvas_manager._store_canvas(canvas)
            
            return {
                "success": True,
                "metadata": updated_metadata
            }
            
        elif interaction_type == "toggle_debug_overlay":
            enabled = interaction_data.get("enabled")
            
            debug_overlay = canvas.update_debug_overlay(enabled=enabled)
            self.canvas_manager._store_canvas(canvas)
            
            return {
                "success": True,
                "debug_overlay": debug_overlay
            }
            
        elif interaction_type == "set_trace_level":
            trace_level = interaction_data.get("trace_level")
            
            debug_overlay = canvas.update_debug_overlay(trace_level=trace_level)
            self.canvas_manager._store_canvas(canvas)
            
            return {
                "success": True,
                "debug_overlay": debug_overlay
            }
            
        else:
            return {
                "success": False,
                "error": f"Unknown interaction type: {interaction_type}"
            }


# Example usage
if __name__ == "__main__":
    # Initialize the canvas manager
    canvas_manager = WorkflowCanvasManager()
    
    # Create a canvas
    canvas = canvas_manager.create_canvas(
        name="Example Workflow",
        description="An example workflow for testing"
    )
    
    # Add some nodes
    task1 = canvas.add_node(
        node_type="task",
        position={"x": 100, "y": 100},
        data={
            "task_type": "start",
            "name": "Start",
            "description": "Start of the workflow"
        }
    )
    
    task2 = canvas.add_node(
        node_type="task",
        position={"x": 300, "y": 100},
        data={
            "task_type": "process",
            "name": "Process Data",
            "description": "Process the input data"
        }
    )
    
    task3 = canvas.add_node(
        node_type="task",
        position={"x": 500, "y": 100},
        data={
            "task_type": "end",
            "name": "End",
            "description": "End of the workflow"
        }
    )
    
    # Add some edges
    canvas.add_edge(
        source=task1.node_id,
        target=task2.node_id
    )
    
    canvas.add_edge(
        source=task2.node_id,
        target=task3.node_id
    )
    
    # Export to workflow manifest
    manifest = canvas.export_to_workflow_manifest()
    print(f"Exported manifest: {manifest['name']}")
    
    # Initialize the canvas service
    canvas_service = WorkflowCanvasService(canvas_manager)
    
    # Register an execution callback
    def execution_callback(event_type, event_data):
        print(f"Execution event: {event_type}")
        print(f"Event data: {event_data}")
    
    canvas_service.register_execution_callback(canvas.canvas_id, execution_callback)
    
    # Start workflow execution
    canvas_service.start_workflow_execution(canvas.canvas_id)
    
    # Update execution progress
    canvas_service.update_execution_progress(
        canvas_id=canvas.canvas_id,
        active_nodes=[task2.node_id],
        completed_nodes=[task1.node_id],
        error_nodes=[]
    )
    
    # Complete workflow execution
    canvas_service.complete_workflow_execution(
        canvas_id=canvas.canvas_id,
        success=True,
        result={"output": "Example output"}
    )
