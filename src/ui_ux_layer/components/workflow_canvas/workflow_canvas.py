"""
Workflow Canvas Component for the UI/UX Layer

This component provides a visual interface for creating, editing, and monitoring
workflows in the Industriverse ecosystem. It integrates with the n8n workflow
engine and provides a rich, interactive canvas for workflow design.

The Workflow Canvas:
1. Provides a drag-and-drop interface for workflow design
2. Visualizes workflow execution in real-time
3. Supports node-based workflow creation with connections
4. Integrates with the Industriverse agent ecosystem
5. Provides access to workflow templates and patterns
6. Enables debugging and testing of workflows

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
from ..core.agent_ecosystem.agent_interaction_protocol import AgentInteractionProtocol
from ..core.capsule_framework.capsule_manager import CapsuleManager

# Configure logging
logger = logging.getLogger(__name__)

class WorkflowCanvas:
    """
    Workflow Canvas component for creating, editing, and monitoring workflows.
    """
    
    def __init__(
        self,
        rendering_engine: RenderingEngine,
        context_engine: ContextEngine,
        agent_protocol: AgentInteractionProtocol,
        capsule_manager: CapsuleManager,
        config: Dict = None
    ):
        """
        Initialize the Workflow Canvas.
        
        Args:
            rendering_engine: Rendering Engine instance
            context_engine: Context Engine instance
            agent_protocol: Agent Interaction Protocol instance
            capsule_manager: Capsule Manager instance
            config: Optional configuration dictionary
        """
        self.rendering_engine = rendering_engine
        self.context_engine = context_engine
        self.agent_protocol = agent_protocol
        self.capsule_manager = capsule_manager
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "grid_size": 20,
            "snap_to_grid": True,
            "auto_layout": True,
            "node_width": 200,
            "node_height": 100,
            "connection_curve": 0.5,
            "zoom_min": 0.1,
            "zoom_max": 2.0,
            "zoom_default": 1.0,
            "enable_minimap": True,
            "enable_node_preview": True,
            "enable_execution_visualization": True,
            "execution_animation_speed": 1.0,
            "max_undo_steps": 50,
            "auto_save_interval": 60,  # seconds
            "default_theme": "light",
            "node_categories": [
                {"id": "triggers", "name": "Triggers", "color": "#FF9800"},
                {"id": "actions", "name": "Actions", "color": "#2196F3"},
                {"id": "transformers", "name": "Transformers", "color": "#4CAF50"},
                {"id": "flow", "name": "Flow Control", "color": "#9C27B0"},
                {"id": "agents", "name": "Agents", "color": "#E91E63"}
            ]
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Current state
        self.current_workflow_id = None
        self.current_workflow = None
        self.nodes = {}
        self.connections = {}
        self.selected_nodes = []
        self.selected_connections = []
        self.clipboard = None
        self.undo_stack = []
        self.redo_stack = []
        self.is_executing = False
        self.execution_data = {}
        self.available_node_types = {}
        self.zoom_level = self.config["zoom_default"]
        self.pan_offset = {"x": 0, "y": 0}
        self.is_dirty = False
        self.last_auto_save = 0
        
        # Event handlers
        self.event_handlers = {
            "workflow_loaded": [],
            "workflow_saved": [],
            "node_added": [],
            "node_removed": [],
            "node_updated": [],
            "connection_added": [],
            "connection_removed": [],
            "selection_changed": [],
            "execution_started": [],
            "execution_finished": [],
            "execution_node_started": [],
            "execution_node_finished": [],
            "execution_error": [],
            "undo_performed": [],
            "redo_performed": [],
            "canvas_changed": [],
            "error": []
        }
        
        # Register with context engine
        self.context_engine.register_context_listener(self._handle_context_change)
        
        # Register with agent protocol for workflow updates
        self.agent_protocol.register_message_handler(
            "state_update",
            self._handle_workflow_update,
            "*"
        )
        
        # Load available node types
        self._load_available_node_types()
        
        logger.info("Workflow Canvas initialized")
    
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
        
        # Handle workflow context changes
        if context_type == "workflow":
            workflow_data = event.get("data", {})
            
            if "workflow_id" in workflow_data and workflow_data["workflow_id"] != self.current_workflow_id:
                # Load the new workflow
                self.load_workflow(workflow_data["workflow_id"])
    
    def _handle_workflow_update(self, message: Dict) -> None:
        """
        Handle workflow state updates.
        
        Args:
            message: State update message
        """
        try:
            payload = message.get("payload", {})
            source_id = message.get("source", {}).get("id")
            
            # Check if this update is for the current workflow
            if source_id == self.current_workflow_id:
                # Update the workflow state
                self._update_workflow_state(payload)
        except Exception as e:
            logger.error(f"Error handling workflow update: {str(e)}")
    
    def _update_workflow_state(self, state: Dict) -> None:
        """
        Update the workflow state.
        
        Args:
            state: New state data
        """
        try:
            # Update execution state
            if "execution" in state:
                self._update_execution_state(state["execution"])
            
            # Update node states
            if "nodes" in state:
                for node_id, node_state in state["nodes"].items():
                    self._update_node_state(node_id, node_state)
            
            # Update connection states
            if "connections" in state:
                for connection_id, connection_state in state["connections"].items():
                    self._update_connection_state(connection_id, connection_state)
        except Exception as e:
            logger.error(f"Error updating workflow state: {str(e)}")
    
    def _update_execution_state(self, execution_state: Dict) -> None:
        """
        Update the workflow execution state.
        
        Args:
            execution_state: Execution state data
        """
        # Update execution flag
        self.is_executing = execution_state.get("is_executing", False)
        
        # Update execution data
        self.execution_data = execution_state.get("data", {})
        
        # Update UI
        self.rendering_engine.update_workflow_execution_state({
            "is_executing": self.is_executing,
            "data": self.execution_data
        })
        
        # Trigger events
        if "status" in execution_state:
            status = execution_state["status"]
            
            if status == "started":
                self._trigger_event("execution_started", {
                    "workflow_id": self.current_workflow_id,
                    "execution_id": execution_state.get("execution_id")
                })
            elif status == "finished":
                self._trigger_event("execution_finished", {
                    "workflow_id": self.current_workflow_id,
                    "execution_id": execution_state.get("execution_id"),
                    "result": execution_state.get("result")
                })
            elif status == "error":
                self._trigger_event("execution_error", {
                    "workflow_id": self.current_workflow_id,
                    "execution_id": execution_state.get("execution_id"),
                    "error": execution_state.get("error")
                })
    
    def _update_node_state(self, node_id: str, node_state: Dict) -> None:
        """
        Update a node's state.
        
        Args:
            node_id: Node identifier
            node_state: Node state data
        """
        if node_id in self.nodes:
            node = self.nodes[node_id]
            
            # Update node state
            if "state" in node_state:
                node["state"] = node_state["state"]
            
            # Update node data
            if "data" in node_state:
                node["data"] = {**node.get("data", {}), **node_state["data"]}
            
            # Update node position if provided
            if "position" in node_state:
                node["position"] = node_state["position"]
            
            # Update node size if provided
            if "size" in node_state:
                node["size"] = node_state["size"]
            
            # Update node in rendering engine
            self.rendering_engine.update_workflow_node(node_id, node)
            
            # Trigger node execution events
            if "execution" in node_state:
                execution = node_state["execution"]
                
                if execution.get("status") == "started":
                    self._trigger_event("execution_node_started", {
                        "node_id": node_id,
                        "execution_id": execution.get("execution_id")
                    })
                elif execution.get("status") == "finished":
                    self._trigger_event("execution_node_finished", {
                        "node_id": node_id,
                        "execution_id": execution.get("execution_id"),
                        "result": execution.get("result")
                    })
                elif execution.get("status") == "error":
                    self._trigger_event("execution_error", {
                        "node_id": node_id,
                        "execution_id": execution.get("execution_id"),
                        "error": execution.get("error")
                    })
    
    def _update_connection_state(self, connection_id: str, connection_state: Dict) -> None:
        """
        Update a connection's state.
        
        Args:
            connection_id: Connection identifier
            connection_state: Connection state data
        """
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            
            # Update connection state
            if "state" in connection_state:
                connection["state"] = connection_state["state"]
            
            # Update connection data
            if "data" in connection_state:
                connection["data"] = {**connection.get("data", {}), **connection_state["data"]}
            
            # Update connection in rendering engine
            self.rendering_engine.update_workflow_connection(connection_id, connection)
    
    def _load_available_node_types(self) -> None:
        """Load available node types from the backend."""
        try:
            logger.info("Loading available node types")
            
            # Request node types from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "get_workflow_node_types"
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error loading node types: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to load node types: {response.get('error_message', 'Unknown error')}"
                })
                return
            
            # Extract node types
            node_types = response.get("payload", {}).get("node_types", {})
            
            # Store node types
            self.available_node_types = node_types
            
            logger.info(f"Loaded {len(node_types)} node types")
        except Exception as e:
            logger.error(f"Error loading node types: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to load node types: {str(e)}"
            })
    
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
    
    def _push_undo_state(self) -> None:
        """Push current state to undo stack."""
        try:
            # Create a snapshot of the current state
            state = {
                "nodes": {node_id: node.copy() for node_id, node in self.nodes.items()},
                "connections": {conn_id: conn.copy() for conn_id, conn in self.connections.items()},
                "selected_nodes": self.selected_nodes.copy(),
                "selected_connections": self.selected_connections.copy(),
                "zoom_level": self.zoom_level,
                "pan_offset": self.pan_offset.copy()
            }
            
            # Push to undo stack
            self.undo_stack.append(state)
            
            # Limit undo stack size
            if len(self.undo_stack) > self.config["max_undo_steps"]:
                self.undo_stack.pop(0)
            
            # Clear redo stack
            self.redo_stack = []
            
            # Mark as dirty
            self.is_dirty = True
            
            # Check auto-save
            current_time = time.time()
            if current_time - self.last_auto_save > self.config["auto_save_interval"]:
                self._auto_save()
        except Exception as e:
            logger.error(f"Error pushing undo state: {str(e)}")
    
    def _auto_save(self) -> None:
        """Auto-save the current workflow."""
        if self.current_workflow_id and self.is_dirty:
            logger.debug("Auto-saving workflow")
            self.save_workflow()
            self.last_auto_save = time.time()
    
    def load_workflow(self, workflow_id: str) -> bool:
        """
        Load a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            logger.info(f"Loading workflow: {workflow_id}")
            
            # Check for unsaved changes
            if self.is_dirty and self.current_workflow_id:
                # Auto-save current workflow
                self.save_workflow()
            
            # Clear current state
            self.clear_canvas()
            
            # Update current workflow ID
            self.current_workflow_id = workflow_id
            
            # Request workflow data from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "get_workflow",
                    "workflow_id": workflow_id
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error loading workflow: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to load workflow: {response.get('error_message', 'Unknown error')}",
                    "workflow_id": workflow_id
                })
                return False
            
            # Extract workflow data
            workflow_data = response.get("payload", {})
            self.current_workflow = workflow_data
            
            # Load nodes
            if "nodes" in workflow_data:
                for node_id, node_data in workflow_data["nodes"].items():
                    self._add_node_from_data(node_id, node_data)
            
            # Load connections
            if "connections" in workflow_data:
                for connection_id, connection_data in workflow_data["connections"].items():
                    self._add_connection_from_data(connection_id, connection_data)
            
            # Set canvas view
            if "view" in workflow_data:
                view = workflow_data["view"]
                self.zoom_level = view.get("zoom", self.config["zoom_default"])
                self.pan_offset = view.get("pan", {"x": 0, "y": 0})
                
                # Update rendering engine
                self.rendering_engine.set_workflow_view({
                    "zoom": self.zoom_level,
                    "pan": self.pan_offset
                })
            
            # Clear undo/redo stacks
            self.undo_stack = []
            self.redo_stack = []
            
            # Reset dirty flag
            self.is_dirty = False
            self.last_auto_save = time.time()
            
            # Trigger workflow loaded event
            self._trigger_event("workflow_loaded", {
                "workflow_id": workflow_id,
                "workflow_data": workflow_data
            })
            
            # Create a capsule for the workflow
            self._create_workflow_capsule(workflow_id, workflow_data)
            
            logger.info(f"Workflow loaded: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading workflow: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to load workflow: {str(e)}",
                "workflow_id": workflow_id
            })
            return False
    
    def _create_workflow_capsule(self, workflow_id: str, workflow_data: Dict) -> None:
        """
        Create a capsule for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            workflow_data: Workflow data
        """
        # Check if capsule already exists
        capsule_id = f"workflow_{workflow_id}"
        if self.capsule_manager.has_capsule(capsule_id):
            # Just focus the existing capsule
            self.capsule_manager.focus_capsule(capsule_id)
            return
        
        # Create capsule data
        capsule_data = {
            "id": capsule_id,
            "type": "workflow",
            "title": workflow_data.get("name", f"Workflow {workflow_id}"),
            "description": workflow_data.get("description", ""),
            "icon": "diagram-project",
            "color": "#0056B3",
            "source": {
                "type": "workflow",
                "id": workflow_id
            },
            "actions": [
                {
                    "id": "execute",
                    "label": "Execute",
                    "icon": "play"
                },
                {
                    "id": "edit",
                    "label": "Edit",
                    "icon": "edit"
                },
                {
                    "id": "duplicate",
                    "label": "Duplicate",
                    "icon": "copy"
                }
            ],
            "properties": {
                "node_count": len(workflow_data.get("nodes", {})),
                "connection_count": len(workflow_data.get("connections", {})),
                "created_at": workflow_data.get("created_at"),
                "updated_at": workflow_data.get("updated_at"),
                "tags": workflow_data.get("tags", [])
            }
        }
        
        # Create the capsule
        self.capsule_manager.create_capsule(capsule_data)
    
    def _add_node_from_data(self, node_id: str, node_data: Dict) -> None:
        """
        Add a node from loaded data.
        
        Args:
            node_id: Node identifier
            node_data: Node data
        """
        # Create node object
        node = {
            "id": node_id,
            "type": node_data.get("type"),
            "name": node_data.get("name", ""),
            "position": node_data.get("position", {"x": 0, "y": 0}),
            "size": node_data.get("size", {"width": self.config["node_width"], "height": self.config["node_height"]}),
            "data": node_data.get("data", {}),
            "state": node_data.get("state", "default"),
            "inputs": node_data.get("inputs", []),
            "outputs": node_data.get("outputs", [])
        }
        
        # Add to nodes dictionary
        self.nodes[node_id] = node
        
        # Add to rendering engine
        self.rendering_engine.add_workflow_node(node_id, node)
    
    def _add_connection_from_data(self, connection_id: str, connection_data: Dict) -> None:
        """
        Add a connection from loaded data.
        
        Args:
            connection_id: Connection identifier
            connection_data: Connection data
        """
        # Create connection object
        connection = {
            "id": connection_id,
            "source": connection_data.get("source", {}),
            "target": connection_data.get("target", {}),
            "data": connection_data.get("data", {}),
            "state": connection_data.get("state", "default")
        }
        
        # Add to connections dictionary
        self.connections[connection_id] = connection
        
        # Add to rendering engine
        self.rendering_engine.add_workflow_connection(connection_id, connection)
    
    def save_workflow(self) -> bool:
        """
        Save the current workflow.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.current_workflow_id:
                logger.warning("No workflow to save")
                return False
            
            logger.info(f"Saving workflow: {self.current_workflow_id}")
            
            # Prepare workflow data
            workflow_data = {
                "id": self.current_workflow_id,
                "name": self.current_workflow.get("name", ""),
                "description": self.current_workflow.get("description", ""),
                "nodes": {node_id: self._prepare_node_for_save(node) for node_id, node in self.nodes.items()},
                "connections": {conn_id: self._prepare_connection_for_save(conn) for conn_id, conn in self.connections.items()},
                "view": {
                    "zoom": self.zoom_level,
                    "pan": self.pan_offset
                },
                "tags": self.current_workflow.get("tags", []),
                "updated_at": time.time()
            }
            
            # Send save request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "save_workflow",
                    "workflow_id": self.current_workflow_id,
                    "workflow_data": workflow_data
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error saving workflow: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to save workflow: {response.get('error_message', 'Unknown error')}",
                    "workflow_id": self.current_workflow_id
                })
                return False
            
            # Update current workflow
            self.current_workflow = workflow_data
            
            # Reset dirty flag
            self.is_dirty = False
            self.last_auto_save = time.time()
            
            # Trigger workflow saved event
            self._trigger_event("workflow_saved", {
                "workflow_id": self.current_workflow_id,
                "workflow_data": workflow_data
            })
            
            logger.info(f"Workflow saved: {self.current_workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving workflow: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to save workflow: {str(e)}",
                "workflow_id": self.current_workflow_id
            })
            return False
    
    def _prepare_node_for_save(self, node: Dict) -> Dict:
        """
        Prepare a node for saving.
        
        Args:
            node: Node data
            
        Returns:
            Prepared node data
        """
        # Create a copy to avoid modifying the original
        node_copy = node.copy()
        
        # Remove any runtime-only properties
        if "runtime" in node_copy:
            del node_copy["runtime"]
        
        return node_copy
    
    def _prepare_connection_for_save(self, connection: Dict) -> Dict:
        """
        Prepare a connection for saving.
        
        Args:
            connection: Connection data
            
        Returns:
            Prepared connection data
        """
        # Create a copy to avoid modifying the original
        connection_copy = connection.copy()
        
        # Remove any runtime-only properties
        if "runtime" in connection_copy:
            del connection_copy["runtime"]
        
        return connection_copy
    
    def create_new_workflow(self, name: str = "New Workflow", description: str = "") -> bool:
        """
        Create a new workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
            
        Returns:
            Boolean indicating success
        """
        try:
            logger.info(f"Creating new workflow: {name}")
            
            # Check for unsaved changes
            if self.is_dirty and self.current_workflow_id:
                # Auto-save current workflow
                self.save_workflow()
            
            # Clear current state
            self.clear_canvas()
            
            # Send create request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "create_workflow",
                    "workflow_data": {
                        "name": name,
                        "description": description,
                        "nodes": {},
                        "connections": {},
                        "view": {
                            "zoom": self.config["zoom_default"],
                            "pan": {"x": 0, "y": 0}
                        },
                        "tags": [],
                        "created_at": time.time(),
                        "updated_at": time.time()
                    }
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error creating workflow: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to create workflow: {response.get('error_message', 'Unknown error')}"
                })
                return False
            
            # Extract workflow ID
            workflow_id = response.get("payload", {}).get("workflow_id")
            
            if not workflow_id:
                logger.error("No workflow ID returned from backend")
                self._trigger_event("error", {
                    "message": "Failed to create workflow: No workflow ID returned"
                })
                return False
            
            # Load the new workflow
            return self.load_workflow(workflow_id)
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to create workflow: {str(e)}"
            })
            return False
    
    def duplicate_workflow(self, new_name: Optional[str] = None) -> bool:
        """
        Duplicate the current workflow.
        
        Args:
            new_name: Optional new name for the duplicated workflow
            
        Returns:
            Boolean indicating success
        """
        try:
            if not self.current_workflow_id:
                logger.warning("No workflow to duplicate")
                return False
            
            # Generate new name if not provided
            if not new_name:
                new_name = f"Copy of {self.current_workflow.get('name', 'Workflow')}"
            
            logger.info(f"Duplicating workflow: {self.current_workflow_id} as {new_name}")
            
            # Save current workflow first
            if self.is_dirty:
                self.save_workflow()
            
            # Send duplicate request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "duplicate_workflow",
                    "workflow_id": self.current_workflow_id,
                    "new_name": new_name
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error duplicating workflow: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to duplicate workflow: {response.get('error_message', 'Unknown error')}",
                    "workflow_id": self.current_workflow_id
                })
                return False
            
            # Extract new workflow ID
            new_workflow_id = response.get("payload", {}).get("workflow_id")
            
            if not new_workflow_id:
                logger.error("No workflow ID returned from backend")
                self._trigger_event("error", {
                    "message": "Failed to duplicate workflow: No workflow ID returned"
                })
                return False
            
            # Load the new workflow
            return self.load_workflow(new_workflow_id)
        except Exception as e:
            logger.error(f"Error duplicating workflow: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to duplicate workflow: {str(e)}",
                "workflow_id": self.current_workflow_id
            })
            return False
    
    def delete_workflow(self) -> bool:
        """
        Delete the current workflow.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.current_workflow_id:
                logger.warning("No workflow to delete")
                return False
            
            logger.info(f"Deleting workflow: {self.current_workflow_id}")
            
            # Send delete request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "delete_workflow",
                    "workflow_id": self.current_workflow_id
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error deleting workflow: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to delete workflow: {response.get('error_message', 'Unknown error')}",
                    "workflow_id": self.current_workflow_id
                })
                return False
            
            # Clear current state
            workflow_id = self.current_workflow_id
            self.clear_canvas()
            self.current_workflow_id = None
            self.current_workflow = None
            
            # Remove workflow capsule
            capsule_id = f"workflow_{workflow_id}"
            if self.capsule_manager.has_capsule(capsule_id):
                self.capsule_manager.remove_capsule(capsule_id)
            
            logger.info(f"Workflow deleted: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting workflow: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to delete workflow: {str(e)}",
                "workflow_id": self.current_workflow_id
            })
            return False
    
    def clear_canvas(self) -> None:
        """Clear the canvas."""
        try:
            logger.info("Clearing canvas")
            
            # Clear nodes and connections
            self.nodes = {}
            self.connections = {}
            self.selected_nodes = []
            self.selected_connections = []
            
            # Reset view
            self.zoom_level = self.config["zoom_default"]
            self.pan_offset = {"x": 0, "y": 0}
            
            # Clear rendering engine
            self.rendering_engine.clear_workflow_canvas()
            
            # Reset undo/redo stacks
            self.undo_stack = []
            self.redo_stack = []
            
            # Reset dirty flag
            self.is_dirty = False
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "clear"
            })
        except Exception as e:
            logger.error(f"Error clearing canvas: {str(e)}")
    
    def add_node(self, node_type: str, position: Dict, data: Optional[Dict] = None) -> Optional[str]:
        """
        Add a node to the canvas.
        
        Args:
            node_type: Node type identifier
            position: Node position
            data: Optional node data
            
        Returns:
            Node ID if successful, None otherwise
        """
        try:
            if not self.current_workflow_id:
                logger.warning("No workflow loaded")
                return None
            
            # Check if node type exists
            if node_type not in self.available_node_types:
                logger.warning(f"Unknown node type: {node_type}")
                return None
            
            logger.info(f"Adding node of type: {node_type}")
            
            # Generate node ID
            node_id = str(uuid.uuid4())
            
            # Get node type definition
            node_type_def = self.available_node_types[node_type]
            
            # Create node object
            node = {
                "id": node_id,
                "type": node_type,
                "name": node_type_def.get("name", node_type),
                "position": position,
                "size": {"width": self.config["node_width"], "height": self.config["node_height"]},
                "data": data or {},
                "state": "default",
                "inputs": node_type_def.get("inputs", []),
                "outputs": node_type_def.get("outputs", [])
            }
            
            # Push current state to undo stack
            self._push_undo_state()
            
            # Add to nodes dictionary
            self.nodes[node_id] = node
            
            # Add to rendering engine
            self.rendering_engine.add_workflow_node(node_id, node)
            
            # Trigger node added event
            self._trigger_event("node_added", {
                "node_id": node_id,
                "node": node
            })
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "add_node",
                "node_id": node_id
            })
            
            return node_id
        except Exception as e:
            logger.error(f"Error adding node: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to add node: {str(e)}"
            })
            return None
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the canvas.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if node_id not in self.nodes:
                logger.warning(f"Node not found: {node_id}")
                return False
            
            logger.info(f"Removing node: {node_id}")
            
            # Push current state to undo stack
            self._push_undo_state()
            
            # Remove node from dictionary
            node = self.nodes.pop(node_id)
            
            # Remove from rendering engine
            self.rendering_engine.remove_workflow_node(node_id)
            
            # Remove any connections to/from this node
            connections_to_remove = []
            for conn_id, conn in self.connections.items():
                if conn["source"].get("node_id") == node_id or conn["target"].get("node_id") == node_id:
                    connections_to_remove.append(conn_id)
            
            for conn_id in connections_to_remove:
                self.remove_connection(conn_id, False)  # Don't push undo state again
            
            # Remove from selection
            if node_id in self.selected_nodes:
                self.selected_nodes.remove(node_id)
                self._trigger_event("selection_changed", {
                    "selected_nodes": self.selected_nodes,
                    "selected_connections": self.selected_connections
                })
            
            # Trigger node removed event
            self._trigger_event("node_removed", {
                "node_id": node_id,
                "node": node
            })
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "remove_node",
                "node_id": node_id
            })
            
            return True
        except Exception as e:
            logger.error(f"Error removing node: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to remove node: {str(e)}",
                "node_id": node_id
            })
            return False
    
    def update_node(self, node_id: str, updates: Dict) -> bool:
        """
        Update a node.
        
        Args:
            node_id: Node identifier
            updates: Updates to apply
            
        Returns:
            Boolean indicating success
        """
        try:
            if node_id not in self.nodes:
                logger.warning(f"Node not found: {node_id}")
                return False
            
            logger.info(f"Updating node: {node_id}")
            
            # Push current state to undo stack
            self._push_undo_state()
            
            # Get the node
            node = self.nodes[node_id]
            
            # Apply updates
            if "position" in updates:
                node["position"] = updates["position"]
            
            if "size" in updates:
                node["size"] = updates["size"]
            
            if "name" in updates:
                node["name"] = updates["name"]
            
            if "data" in updates:
                node["data"] = {**node.get("data", {}), **updates["data"]}
            
            if "state" in updates:
                node["state"] = updates["state"]
            
            # Update in rendering engine
            self.rendering_engine.update_workflow_node(node_id, node)
            
            # Trigger node updated event
            self._trigger_event("node_updated", {
                "node_id": node_id,
                "updates": updates,
                "node": node
            })
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "update_node",
                "node_id": node_id
            })
            
            return True
        except Exception as e:
            logger.error(f"Error updating node: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to update node: {str(e)}",
                "node_id": node_id
            })
            return False
    
    def add_connection(self, source_node_id: str, source_output: str, target_node_id: str, target_input: str) -> Optional[str]:
        """
        Add a connection between nodes.
        
        Args:
            source_node_id: Source node identifier
            source_output: Source output identifier
            target_node_id: Target node identifier
            target_input: Target input identifier
            
        Returns:
            Connection ID if successful, None otherwise
        """
        try:
            if source_node_id not in self.nodes:
                logger.warning(f"Source node not found: {source_node_id}")
                return None
            
            if target_node_id not in self.nodes:
                logger.warning(f"Target node not found: {target_node_id}")
                return None
            
            logger.info(f"Adding connection: {source_node_id}:{source_output} -> {target_node_id}:{target_input}")
            
            # Check if connection already exists
            for conn in self.connections.values():
                if (conn["source"].get("node_id") == source_node_id and
                    conn["source"].get("output") == source_output and
                    conn["target"].get("node_id") == target_node_id and
                    conn["target"].get("input") == target_input):
                    logger.warning("Connection already exists")
                    return None
            
            # Generate connection ID
            connection_id = str(uuid.uuid4())
            
            # Create connection object
            connection = {
                "id": connection_id,
                "source": {
                    "node_id": source_node_id,
                    "output": source_output
                },
                "target": {
                    "node_id": target_node_id,
                    "input": target_input
                },
                "data": {},
                "state": "default"
            }
            
            # Push current state to undo stack
            self._push_undo_state()
            
            # Add to connections dictionary
            self.connections[connection_id] = connection
            
            # Add to rendering engine
            self.rendering_engine.add_workflow_connection(connection_id, connection)
            
            # Trigger connection added event
            self._trigger_event("connection_added", {
                "connection_id": connection_id,
                "connection": connection
            })
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "add_connection",
                "connection_id": connection_id
            })
            
            return connection_id
        except Exception as e:
            logger.error(f"Error adding connection: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to add connection: {str(e)}"
            })
            return None
    
    def remove_connection(self, connection_id: str, push_undo: bool = True) -> bool:
        """
        Remove a connection.
        
        Args:
            connection_id: Connection identifier
            push_undo: Whether to push to undo stack
            
        Returns:
            Boolean indicating success
        """
        try:
            if connection_id not in self.connections:
                logger.warning(f"Connection not found: {connection_id}")
                return False
            
            logger.info(f"Removing connection: {connection_id}")
            
            # Push current state to undo stack if requested
            if push_undo:
                self._push_undo_state()
            
            # Remove connection from dictionary
            connection = self.connections.pop(connection_id)
            
            # Remove from rendering engine
            self.rendering_engine.remove_workflow_connection(connection_id)
            
            # Remove from selection
            if connection_id in self.selected_connections:
                self.selected_connections.remove(connection_id)
                self._trigger_event("selection_changed", {
                    "selected_nodes": self.selected_nodes,
                    "selected_connections": self.selected_connections
                })
            
            # Trigger connection removed event
            self._trigger_event("connection_removed", {
                "connection_id": connection_id,
                "connection": connection
            })
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "remove_connection",
                "connection_id": connection_id
            })
            
            return True
        except Exception as e:
            logger.error(f"Error removing connection: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to remove connection: {str(e)}",
                "connection_id": connection_id
            })
            return False
    
    def select_node(self, node_id: str, multi_select: bool = False) -> bool:
        """
        Select a node.
        
        Args:
            node_id: Node identifier
            multi_select: Whether to add to current selection
            
        Returns:
            Boolean indicating success
        """
        try:
            if node_id not in self.nodes:
                logger.warning(f"Node not found: {node_id}")
                return False
            
            logger.debug(f"Selecting node: {node_id}")
            
            # Clear selection if not multi-select
            if not multi_select:
                self.selected_nodes = []
                self.selected_connections = []
            
            # Add to selection if not already selected
            if node_id not in self.selected_nodes:
                self.selected_nodes.append(node_id)
            
            # Update rendering engine
            self.rendering_engine.set_workflow_selection({
                "nodes": self.selected_nodes,
                "connections": self.selected_connections
            })
            
            # Trigger selection changed event
            self._trigger_event("selection_changed", {
                "selected_nodes": self.selected_nodes,
                "selected_connections": self.selected_connections
            })
            
            return True
        except Exception as e:
            logger.error(f"Error selecting node: {str(e)}")
            return False
    
    def select_connection(self, connection_id: str, multi_select: bool = False) -> bool:
        """
        Select a connection.
        
        Args:
            connection_id: Connection identifier
            multi_select: Whether to add to current selection
            
        Returns:
            Boolean indicating success
        """
        try:
            if connection_id not in self.connections:
                logger.warning(f"Connection not found: {connection_id}")
                return False
            
            logger.debug(f"Selecting connection: {connection_id}")
            
            # Clear selection if not multi-select
            if not multi_select:
                self.selected_nodes = []
                self.selected_connections = []
            
            # Add to selection if not already selected
            if connection_id not in self.selected_connections:
                self.selected_connections.append(connection_id)
            
            # Update rendering engine
            self.rendering_engine.set_workflow_selection({
                "nodes": self.selected_nodes,
                "connections": self.selected_connections
            })
            
            # Trigger selection changed event
            self._trigger_event("selection_changed", {
                "selected_nodes": self.selected_nodes,
                "selected_connections": self.selected_connections
            })
            
            return True
        except Exception as e:
            logger.error(f"Error selecting connection: {str(e)}")
            return False
    
    def clear_selection(self) -> None:
        """Clear the current selection."""
        try:
            logger.debug("Clearing selection")
            
            # Clear selection
            self.selected_nodes = []
            self.selected_connections = []
            
            # Update rendering engine
            self.rendering_engine.set_workflow_selection({
                "nodes": [],
                "connections": []
            })
            
            # Trigger selection changed event
            self._trigger_event("selection_changed", {
                "selected_nodes": [],
                "selected_connections": []
            })
        except Exception as e:
            logger.error(f"Error clearing selection: {str(e)}")
    
    def delete_selected(self) -> bool:
        """
        Delete selected nodes and connections.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.selected_nodes and not self.selected_connections:
                logger.debug("Nothing selected to delete")
                return False
            
            logger.info("Deleting selected items")
            
            # Push current state to undo stack
            self._push_undo_state()
            
            # Delete selected connections
            for connection_id in self.selected_connections.copy():
                self.remove_connection(connection_id, False)  # Don't push undo state again
            
            # Delete selected nodes
            for node_id in self.selected_nodes.copy():
                self.remove_node(node_id)  # This will also remove connected connections
            
            # Clear selection
            self.clear_selection()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting selected items: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to delete selected items: {str(e)}"
            })
            return False
    
    def copy_selected(self) -> bool:
        """
        Copy selected nodes and connections to clipboard.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.selected_nodes:
                logger.debug("No nodes selected to copy")
                return False
            
            logger.info("Copying selected items")
            
            # Create clipboard data
            clipboard_data = {
                "nodes": {},
                "connections": {}
            }
            
            # Copy selected nodes
            for node_id in self.selected_nodes:
                if node_id in self.nodes:
                    clipboard_data["nodes"][node_id] = self.nodes[node_id].copy()
            
            # Copy connections between selected nodes
            for connection_id, connection in self.connections.items():
                source_node_id = connection["source"].get("node_id")
                target_node_id = connection["target"].get("node_id")
                
                if source_node_id in self.selected_nodes and target_node_id in self.selected_nodes:
                    clipboard_data["connections"][connection_id] = connection.copy()
            
            # Store in clipboard
            self.clipboard = clipboard_data
            
            return True
        except Exception as e:
            logger.error(f"Error copying selected items: {str(e)}")
            return False
    
    def paste(self, offset: Dict = {"x": 20, "y": 20}) -> bool:
        """
        Paste clipboard contents to canvas.
        
        Args:
            offset: Position offset for pasted items
            
        Returns:
            Boolean indicating success
        """
        try:
            if not self.clipboard or not self.clipboard.get("nodes"):
                logger.debug("Nothing to paste")
                return False
            
            logger.info("Pasting items")
            
            # Push current state to undo stack
            self._push_undo_state()
            
            # Clear selection
            self.clear_selection()
            
            # Create ID mapping for new nodes
            id_mapping = {}
            
            # Paste nodes
            for old_node_id, old_node in self.clipboard["nodes"].items():
                # Generate new ID
                new_node_id = str(uuid.uuid4())
                id_mapping[old_node_id] = new_node_id
                
                # Create new node with offset position
                new_node = old_node.copy()
                new_node["id"] = new_node_id
                new_node["position"] = {
                    "x": old_node["position"]["x"] + offset["x"],
                    "y": old_node["position"]["y"] + offset["y"]
                }
                
                # Add to nodes dictionary
                self.nodes[new_node_id] = new_node
                
                # Add to rendering engine
                self.rendering_engine.add_workflow_node(new_node_id, new_node)
                
                # Add to selection
                self.selected_nodes.append(new_node_id)
                
                # Trigger node added event
                self._trigger_event("node_added", {
                    "node_id": new_node_id,
                    "node": new_node
                })
            
            # Paste connections
            for old_connection_id, old_connection in self.clipboard["connections"].items():
                old_source_node_id = old_connection["source"]["node_id"]
                old_target_node_id = old_connection["target"]["node_id"]
                
                # Skip if source or target node wasn't copied
                if old_source_node_id not in id_mapping or old_target_node_id not in id_mapping:
                    continue
                
                # Get new node IDs
                new_source_node_id = id_mapping[old_source_node_id]
                new_target_node_id = id_mapping[old_target_node_id]
                
                # Create new connection
                new_connection_id = str(uuid.uuid4())
                new_connection = old_connection.copy()
                new_connection["id"] = new_connection_id
                new_connection["source"]["node_id"] = new_source_node_id
                new_connection["target"]["node_id"] = new_target_node_id
                
                # Add to connections dictionary
                self.connections[new_connection_id] = new_connection
                
                # Add to rendering engine
                self.rendering_engine.add_workflow_connection(new_connection_id, new_connection)
                
                # Add to selection
                self.selected_connections.append(new_connection_id)
                
                # Trigger connection added event
                self._trigger_event("connection_added", {
                    "connection_id": new_connection_id,
                    "connection": new_connection
                })
            
            # Update rendering engine selection
            self.rendering_engine.set_workflow_selection({
                "nodes": self.selected_nodes,
                "connections": self.selected_connections
            })
            
            # Trigger selection changed event
            self._trigger_event("selection_changed", {
                "selected_nodes": self.selected_nodes,
                "selected_connections": self.selected_connections
            })
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "paste"
            })
            
            return True
        except Exception as e:
            logger.error(f"Error pasting items: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to paste items: {str(e)}"
            })
            return False
    
    def undo(self) -> bool:
        """
        Undo the last action.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.undo_stack:
                logger.debug("Nothing to undo")
                return False
            
            logger.info("Performing undo")
            
            # Get current state for redo
            current_state = {
                "nodes": {node_id: node.copy() for node_id, node in self.nodes.items()},
                "connections": {conn_id: conn.copy() for conn_id, conn in self.connections.items()},
                "selected_nodes": self.selected_nodes.copy(),
                "selected_connections": self.selected_connections.copy(),
                "zoom_level": self.zoom_level,
                "pan_offset": self.pan_offset.copy()
            }
            
            # Push to redo stack
            self.redo_stack.append(current_state)
            
            # Pop state from undo stack
            state = self.undo_stack.pop()
            
            # Restore state
            self._restore_state(state)
            
            # Mark as dirty
            self.is_dirty = True
            
            # Trigger undo performed event
            self._trigger_event("undo_performed", {})
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "undo"
            })
            
            return True
        except Exception as e:
            logger.error(f"Error performing undo: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to perform undo: {str(e)}"
            })
            return False
    
    def redo(self) -> bool:
        """
        Redo the last undone action.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.redo_stack:
                logger.debug("Nothing to redo")
                return False
            
            logger.info("Performing redo")
            
            # Get current state for undo
            current_state = {
                "nodes": {node_id: node.copy() for node_id, node in self.nodes.items()},
                "connections": {conn_id: conn.copy() for conn_id, conn in self.connections.items()},
                "selected_nodes": self.selected_nodes.copy(),
                "selected_connections": self.selected_connections.copy(),
                "zoom_level": self.zoom_level,
                "pan_offset": self.pan_offset.copy()
            }
            
            # Push to undo stack
            self.undo_stack.append(current_state)
            
            # Pop state from redo stack
            state = self.redo_stack.pop()
            
            # Restore state
            self._restore_state(state)
            
            # Mark as dirty
            self.is_dirty = True
            
            # Trigger redo performed event
            self._trigger_event("redo_performed", {})
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "redo"
            })
            
            return True
        except Exception as e:
            logger.error(f"Error performing redo: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to perform redo: {str(e)}"
            })
            return False
    
    def _restore_state(self, state: Dict) -> None:
        """
        Restore canvas state.
        
        Args:
            state: State to restore
        """
        # Clear rendering engine
        self.rendering_engine.clear_workflow_canvas()
        
        # Restore nodes
        self.nodes = {node_id: node.copy() for node_id, node in state["nodes"].items()}
        for node_id, node in self.nodes.items():
            self.rendering_engine.add_workflow_node(node_id, node)
        
        # Restore connections
        self.connections = {conn_id: conn.copy() for conn_id, conn in state["connections"].items()}
        for conn_id, conn in self.connections.items():
            self.rendering_engine.add_workflow_connection(conn_id, conn)
        
        # Restore selection
        self.selected_nodes = state["selected_nodes"].copy()
        self.selected_connections = state["selected_connections"].copy()
        self.rendering_engine.set_workflow_selection({
            "nodes": self.selected_nodes,
            "connections": self.selected_connections
        })
        
        # Restore view
        self.zoom_level = state["zoom_level"]
        self.pan_offset = state["pan_offset"].copy()
        self.rendering_engine.set_workflow_view({
            "zoom": self.zoom_level,
            "pan": self.pan_offset
        })
    
    def set_zoom(self, zoom_level: float) -> None:
        """
        Set the zoom level.
        
        Args:
            zoom_level: Zoom level
        """
        try:
            # Clamp zoom level
            zoom_level = max(self.config["zoom_min"], min(self.config["zoom_max"], zoom_level))
            
            logger.debug(f"Setting zoom level: {zoom_level}")
            
            # Update zoom level
            self.zoom_level = zoom_level
            
            # Update rendering engine
            self.rendering_engine.set_workflow_view({
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
            self.rendering_engine.set_workflow_view({
                "zoom": self.zoom_level,
                "pan": self.pan_offset
            })
        except Exception as e:
            logger.error(f"Error setting pan: {str(e)}")
    
    def execute_workflow(self) -> bool:
        """
        Execute the current workflow.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.current_workflow_id:
                logger.warning("No workflow to execute")
                return False
            
            if self.is_executing:
                logger.warning("Workflow is already executing")
                return False
            
            logger.info(f"Executing workflow: {self.current_workflow_id}")
            
            # Save workflow first
            if self.is_dirty:
                self.save_workflow()
            
            # Send execute request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "execute_workflow",
                    "workflow_id": self.current_workflow_id
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error executing workflow: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to execute workflow: {response.get('error_message', 'Unknown error')}",
                    "workflow_id": self.current_workflow_id
                })
                return False
            
            # Extract execution ID
            execution_id = response.get("payload", {}).get("execution_id")
            
            if not execution_id:
                logger.error("No execution ID returned from backend")
                self._trigger_event("error", {
                    "message": "Failed to execute workflow: No execution ID returned"
                })
                return False
            
            # Update execution state
            self.is_executing = True
            self.execution_data = {
                "execution_id": execution_id,
                "start_time": time.time()
            }
            
            # Update rendering engine
            self.rendering_engine.update_workflow_execution_state({
                "is_executing": True,
                "data": self.execution_data
            })
            
            # Trigger execution started event
            self._trigger_event("execution_started", {
                "workflow_id": self.current_workflow_id,
                "execution_id": execution_id
            })
            
            logger.info(f"Workflow execution started: {execution_id}")
            return True
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to execute workflow: {str(e)}",
                "workflow_id": self.current_workflow_id
            })
            return False
    
    def stop_workflow_execution(self) -> bool:
        """
        Stop the current workflow execution.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.current_workflow_id:
                logger.warning("No workflow to stop")
                return False
            
            if not self.is_executing:
                logger.warning("Workflow is not executing")
                return False
            
            logger.info(f"Stopping workflow execution: {self.current_workflow_id}")
            
            # Send stop request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "stop_workflow_execution",
                    "workflow_id": self.current_workflow_id,
                    "execution_id": self.execution_data.get("execution_id")
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error stopping workflow execution: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to stop workflow execution: {response.get('error_message', 'Unknown error')}",
                    "workflow_id": self.current_workflow_id
                })
                return False
            
            # Update execution state
            self.is_executing = False
            
            # Update rendering engine
            self.rendering_engine.update_workflow_execution_state({
                "is_executing": False
            })
            
            logger.info("Workflow execution stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping workflow execution: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to stop workflow execution: {str(e)}",
                "workflow_id": self.current_workflow_id
            })
            return False
    
    def get_workflow_execution_results(self, execution_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get workflow execution results.
        
        Args:
            execution_id: Optional execution ID (defaults to current execution)
            
        Returns:
            Execution results or None if not available
        """
        try:
            if not self.current_workflow_id:
                logger.warning("No workflow loaded")
                return None
            
            # Use current execution ID if not provided
            if not execution_id:
                execution_id = self.execution_data.get("execution_id")
                
            if not execution_id:
                logger.warning("No execution ID available")
                return None
            
            logger.info(f"Getting execution results: {execution_id}")
            
            # Send request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "get_workflow_execution_results",
                    "workflow_id": self.current_workflow_id,
                    "execution_id": execution_id
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error getting execution results: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to get execution results: {response.get('error_message', 'Unknown error')}",
                    "workflow_id": self.current_workflow_id,
                    "execution_id": execution_id
                })
                return None
            
            # Extract results
            results = response.get("payload", {}).get("results")
            
            return results
        except Exception as e:
            logger.error(f"Error getting execution results: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to get execution results: {str(e)}",
                "workflow_id": self.current_workflow_id,
                "execution_id": execution_id
            })
            return None
    
    def get_workflow_templates(self) -> List[Dict]:
        """
        Get available workflow templates.
        
        Returns:
            List of workflow templates
        """
        try:
            logger.info("Getting workflow templates")
            
            # Send request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "get_workflow_templates"
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error getting workflow templates: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to get workflow templates: {response.get('error_message', 'Unknown error')}"
                })
                return []
            
            # Extract templates
            templates = response.get("payload", {}).get("templates", [])
            
            return templates
        except Exception as e:
            logger.error(f"Error getting workflow templates: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to get workflow templates: {str(e)}"
            })
            return []
    
    def create_workflow_from_template(self, template_id: str, name: Optional[str] = None) -> bool:
        """
        Create a workflow from a template.
        
        Args:
            template_id: Template identifier
            name: Optional name for the new workflow
            
        Returns:
            Boolean indicating success
        """
        try:
            logger.info(f"Creating workflow from template: {template_id}")
            
            # Send request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "create_workflow_from_template",
                    "template_id": template_id,
                    "name": name
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error creating workflow from template: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to create workflow from template: {response.get('error_message', 'Unknown error')}",
                    "template_id": template_id
                })
                return False
            
            # Extract workflow ID
            workflow_id = response.get("payload", {}).get("workflow_id")
            
            if not workflow_id:
                logger.error("No workflow ID returned from backend")
                self._trigger_event("error", {
                    "message": "Failed to create workflow from template: No workflow ID returned"
                })
                return False
            
            # Load the new workflow
            return self.load_workflow(workflow_id)
        except Exception as e:
            logger.error(f"Error creating workflow from template: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to create workflow from template: {str(e)}",
                "template_id": template_id
            })
            return False
    
    def export_workflow(self, format_type: str = "json") -> Optional[str]:
        """
        Export the current workflow.
        
        Args:
            format_type: Export format (json, yaml, etc.)
            
        Returns:
            Exported workflow string or None if failed
        """
        try:
            if not self.current_workflow_id:
                logger.warning("No workflow to export")
                return None
            
            logger.info(f"Exporting workflow: {self.current_workflow_id}")
            
            # Save workflow first
            if self.is_dirty:
                self.save_workflow()
            
            # Send export request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "export_workflow",
                    "workflow_id": self.current_workflow_id,
                    "format": format_type
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error exporting workflow: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to export workflow: {response.get('error_message', 'Unknown error')}",
                    "workflow_id": self.current_workflow_id
                })
                return None
            
            # Extract export data
            export_data = response.get("payload", {}).get("data")
            
            return export_data
        except Exception as e:
            logger.error(f"Error exporting workflow: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to export workflow: {str(e)}",
                "workflow_id": self.current_workflow_id
            })
            return None
    
    def import_workflow(self, import_data: str, format_type: str = "json", name: Optional[str] = None) -> bool:
        """
        Import a workflow.
        
        Args:
            import_data: Workflow data to import
            format_type: Import format (json, yaml, etc.)
            name: Optional name for the imported workflow
            
        Returns:
            Boolean indicating success
        """
        try:
            logger.info("Importing workflow")
            
            # Send import request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "import_workflow",
                    "data": import_data,
                    "format": format_type,
                    "name": name
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error importing workflow: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to import workflow: {response.get('error_message', 'Unknown error')}"
                })
                return False
            
            # Extract workflow ID
            workflow_id = response.get("payload", {}).get("workflow_id")
            
            if not workflow_id:
                logger.error("No workflow ID returned from backend")
                self._trigger_event("error", {
                    "message": "Failed to import workflow: No workflow ID returned"
                })
                return False
            
            # Load the imported workflow
            return self.load_workflow(workflow_id)
        except Exception as e:
            logger.error(f"Error importing workflow: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to import workflow: {str(e)}"
            })
            return False
    
    def auto_layout(self) -> bool:
        """
        Apply automatic layout to the workflow.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.nodes:
                logger.warning("No nodes to layout")
                return False
            
            logger.info("Applying auto layout")
            
            # Push current state to undo stack
            self._push_undo_state()
            
            # Request layout from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "auto_layout_workflow",
                    "workflow_id": self.current_workflow_id
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error applying auto layout: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to apply auto layout: {response.get('error_message', 'Unknown error')}"
                })
                return False
            
            # Extract layout data
            layout_data = response.get("payload", {}).get("layout", {})
            
            # Apply layout
            for node_id, position in layout_data.items():
                if node_id in self.nodes:
                    self.nodes[node_id]["position"] = position
                    self.rendering_engine.update_workflow_node(node_id, self.nodes[node_id])
            
            # Trigger canvas changed event
            self._trigger_event("canvas_changed", {
                "action": "auto_layout"
            })
            
            return True
        except Exception as e:
            logger.error(f"Error applying auto layout: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to apply auto layout: {str(e)}"
            })
            return False
    
    def validate_workflow(self) -> Dict:
        """
        Validate the current workflow.
        
        Returns:
            Validation results
        """
        try:
            if not self.current_workflow_id:
                logger.warning("No workflow to validate")
                return {"valid": False, "errors": ["No workflow loaded"]}
            
            logger.info(f"Validating workflow: {self.current_workflow_id}")
            
            # Save workflow first
            if self.is_dirty:
                self.save_workflow()
            
            # Send validate request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "validate_workflow",
                    "workflow_id": self.current_workflow_id
                },
                {
                    "type": "agent",
                    "id": "workflow_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error validating workflow: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to validate workflow: {response.get('error_message', 'Unknown error')}",
                    "workflow_id": self.current_workflow_id
                })
                return {"valid": False, "errors": [response.get("error_message", "Unknown error")]}
            
            # Extract validation results
            validation_results = response.get("payload", {})
            
            return validation_results
        except Exception as e:
            logger.error(f"Error validating workflow: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to validate workflow: {str(e)}",
                "workflow_id": self.current_workflow_id
            })
            return {"valid": False, "errors": [str(e)]}
    
    def shutdown(self) -> None:
        """Shutdown the Workflow Canvas."""
        logger.info("Shutting down Workflow Canvas")
        
        # Save any unsaved changes
        if self.is_dirty and self.current_workflow_id:
            self.save_workflow()
        
        # Clear the canvas
        self.clear_canvas()
        
        # Clear current workflow
        self.current_workflow_id = None
        self.current_workflow = None
