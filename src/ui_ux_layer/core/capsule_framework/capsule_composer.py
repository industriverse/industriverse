"""
Capsule Composer Module for the UI/UX Layer of Industriverse

This module provides capabilities for composing and orchestrating Agent Capsules
in the UI/UX Layer, enabling users to create, connect, and manage complex capsule
compositions for industrial workflows and processes.

The Capsule Composer is responsible for:
1. Creating and managing capsule compositions
2. Establishing connections between capsules
3. Validating capsule compatibility and connections
4. Managing composition layouts and visualization
5. Providing composition templates and patterns

This module works closely with the Capsule Manager and other capsule-related
components to enable powerful workflow composition capabilities.
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from enum import Enum
import json

from .capsule_manager import CapsuleManager
from .capsule_state_manager import CapsuleStateManager
from .capsule_interaction_controller import CapsuleInteractionController
from .capsule_lifecycle_manager import CapsuleLifecycleManager
from ..context_engine.context_awareness_engine import ContextAwarenessEngine

logger = logging.getLogger(__name__)

class ConnectionType(Enum):
    """Enumeration of capsule connection types."""
    DATA = "data"
    CONTROL = "control"
    EVENT = "event"
    CONTEXT = "context"
    TRUST = "trust"
    FEEDBACK = "feedback"


class CompositionLayout(Enum):
    """Enumeration of capsule composition layouts."""
    FLOW = "flow"
    GRID = "grid"
    RADIAL = "radial"
    HIERARCHICAL = "hierarchical"
    FREEFORM = "freeform"


class CapsuleComposer:
    """
    Composes and orchestrates Agent Capsules in the UI/UX Layer.
    
    This class provides methods for creating, connecting, and managing
    capsule compositions for industrial workflows and processes.
    """

    def __init__(
        self,
        capsule_manager: CapsuleManager,
        capsule_state_manager: CapsuleStateManager,
        capsule_interaction_controller: CapsuleInteractionController,
        capsule_lifecycle_manager: CapsuleLifecycleManager,
        context_awareness_engine: ContextAwarenessEngine
    ):
        """
        Initialize the CapsuleComposer.
        
        Args:
            capsule_manager: Manager for capsules
            capsule_state_manager: Manager for capsule states
            capsule_interaction_controller: Controller for capsule interactions
            capsule_lifecycle_manager: Manager for capsule lifecycles
            context_awareness_engine: Engine for context awareness
        """
        self.capsule_manager = capsule_manager
        self.capsule_state_manager = capsule_state_manager
        self.capsule_interaction_controller = capsule_interaction_controller
        self.capsule_lifecycle_manager = capsule_lifecycle_manager
        self.context_awareness_engine = context_awareness_engine
        
        # Initialize composition tracking
        self.compositions = {}
        self.composition_templates = {}
        self.composition_layouts = {}
        self.composition_connections = {}
        self.composition_validation_rules = {}
        self.composition_callbacks = {}
        
        # Initialize default templates and validation rules
        self._initialize_default_templates()
        self._initialize_default_validation_rules()
        
        logger.info("CapsuleComposer initialized")

    def _initialize_default_templates(self):
        """Initialize default composition templates."""
        # Simple workflow template
        self.composition_templates["simple_workflow"] = {
            "name": "Simple Workflow",
            "description": "A simple linear workflow with input, processing, and output capsules",
            "layout": CompositionLayout.FLOW.value,
            "capsules": [
                {"id": "input", "type": "input", "position": {"x": 100, "y": 200}},
                {"id": "process", "type": "process", "position": {"x": 300, "y": 200}},
                {"id": "output", "type": "output", "position": {"x": 500, "y": 200}}
            ],
            "connections": [
                {"source": "input", "target": "process", "type": ConnectionType.DATA.value},
                {"source": "process", "target": "output", "type": ConnectionType.DATA.value}
            ]
        }
        
        # Feedback loop template
        self.composition_templates["feedback_loop"] = {
            "name": "Feedback Loop",
            "description": "A workflow with a feedback loop for iterative processing",
            "layout": CompositionLayout.FLOW.value,
            "capsules": [
                {"id": "input", "type": "input", "position": {"x": 100, "y": 200}},
                {"id": "process", "type": "process", "position": {"x": 300, "y": 200}},
                {"id": "decision", "type": "decision", "position": {"x": 500, "y": 200}},
                {"id": "output", "type": "output", "position": {"x": 700, "y": 200}},
                {"id": "feedback", "type": "feedback", "position": {"x": 400, "y": 300}}
            ],
            "connections": [
                {"source": "input", "target": "process", "type": ConnectionType.DATA.value},
                {"source": "process", "target": "decision", "type": ConnectionType.DATA.value},
                {"source": "decision", "target": "output", "type": ConnectionType.DATA.value},
                {"source": "decision", "target": "feedback", "type": ConnectionType.FEEDBACK.value},
                {"source": "feedback", "target": "process", "type": ConnectionType.CONTROL.value}
            ]
        }
        
        # Parallel processing template
        self.composition_templates["parallel_processing"] = {
            "name": "Parallel Processing",
            "description": "A workflow with parallel processing paths",
            "layout": CompositionLayout.FLOW.value,
            "capsules": [
                {"id": "input", "type": "input", "position": {"x": 100, "y": 200}},
                {"id": "split", "type": "split", "position": {"x": 250, "y": 200}},
                {"id": "process_a", "type": "process", "position": {"x": 400, "y": 100}},
                {"id": "process_b", "type": "process", "position": {"x": 400, "y": 200}},
                {"id": "process_c", "type": "process", "position": {"x": 400, "y": 300}},
                {"id": "merge", "type": "merge", "position": {"x": 550, "y": 200}},
                {"id": "output", "type": "output", "position": {"x": 700, "y": 200}}
            ],
            "connections": [
                {"source": "input", "target": "split", "type": ConnectionType.DATA.value},
                {"source": "split", "target": "process_a", "type": ConnectionType.DATA.value},
                {"source": "split", "target": "process_b", "type": ConnectionType.DATA.value},
                {"source": "split", "target": "process_c", "type": ConnectionType.DATA.value},
                {"source": "process_a", "target": "merge", "type": ConnectionType.DATA.value},
                {"source": "process_b", "target": "merge", "type": ConnectionType.DATA.value},
                {"source": "process_c", "target": "merge", "type": ConnectionType.DATA.value},
                {"source": "merge", "target": "output", "type": ConnectionType.DATA.value}
            ]
        }

    def _initialize_default_validation_rules(self):
        """Initialize default composition validation rules."""
        # Basic connection validation rules
        self.composition_validation_rules["basic_connection"] = {
            "name": "Basic Connection Validation",
            "description": "Validates basic connection compatibility between capsules",
            "rules": [
                {
                    "condition": "source.type == 'input' and target.type == 'output'",
                    "message": "Cannot connect input directly to output",
                    "severity": "error"
                },
                {
                    "condition": "source.type == 'output'",
                    "message": "Output capsules cannot be source of connections",
                    "severity": "error"
                },
                {
                    "condition": "target.type == 'input'",
                    "message": "Input capsules cannot be target of connections",
                    "severity": "error"
                }
            ]
        }
        
        # Cycle detection validation rules
        self.composition_validation_rules["cycle_detection"] = {
            "name": "Cycle Detection",
            "description": "Detects cycles in the composition graph",
            "rules": [
                {
                    "condition": "has_cycle(composition)",
                    "message": "Composition contains cycles",
                    "severity": "warning"
                }
            ]
        }
        
        # Connection type validation rules
        self.composition_validation_rules["connection_type"] = {
            "name": "Connection Type Validation",
            "description": "Validates connection types between capsules",
            "rules": [
                {
                    "condition": "connection.type == 'trust' and not (source.supports_trust and target.supports_trust)",
                    "message": "Trust connections require both capsules to support trust",
                    "severity": "error"
                },
                {
                    "condition": "connection.type == 'context' and not (source.supports_context and target.supports_context)",
                    "message": "Context connections require both capsules to support context",
                    "severity": "error"
                }
            ]
        }

    def create_composition(
        self,
        name: str,
        description: str,
        layout: CompositionLayout = CompositionLayout.FLOW,
        template_id: Optional[str] = None
    ) -> str:
        """
        Create a new capsule composition.
        
        Args:
            name: Name of the composition
            description: Description of the composition
            layout: Layout for the composition
            template_id: Optional template ID to use
            
        Returns:
            Composition ID
        """
        # Generate composition ID
        composition_id = str(uuid.uuid4())
        
        # Create composition record
        composition = {
            "id": composition_id,
            "name": name,
            "description": description,
            "layout": layout.value,
            "created_at": time.time(),
            "updated_at": time.time(),
            "capsules": [],
            "connections": []
        }
        
        # Apply template if provided
        if template_id and template_id in self.composition_templates:
            template = self.composition_templates[template_id]
            
            # Copy capsules from template
            for capsule_def in template["capsules"]:
                capsule_id = f"{capsule_def['id']}_{composition_id[:8]}"
                capsule_type = capsule_def["type"]
                position = capsule_def.get("position", {"x": 0, "y": 0})
                
                composition["capsules"].append({
                    "id": capsule_id,
                    "type": capsule_type,
                    "position": position,
                    "created_at": time.time()
                })
            
            # Copy connections from template
            for connection_def in template["connections"]:
                source_id = f"{connection_def['source']}_{composition_id[:8]}"
                target_id = f"{connection_def['target']}_{composition_id[:8]}"
                connection_type = connection_def["type"]
                
                composition["connections"].append({
                    "id": str(uuid.uuid4()),
                    "source": source_id,
                    "target": target_id,
                    "type": connection_type,
                    "created_at": time.time()
                })
        
        # Store composition
        self.compositions[composition_id] = composition
        
        # Store layout
        self.composition_layouts[composition_id] = {
            "type": layout.value,
            "positions": {}
        }
        
        logger.info(f"Created composition {composition_id}: {name}")
        return composition_id

    def delete_composition(self, composition_id: str) -> bool:
        """
        Delete a capsule composition.
        
        Args:
            composition_id: ID of the composition to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return False
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Delete all capsules in the composition
        for capsule_def in composition["capsules"]:
            capsule_id = capsule_def["id"]
            self.capsule_lifecycle_manager.deactivate_capsule(capsule_id)
        
        # Delete composition
        del self.compositions[composition_id]
        
        # Delete layout
        if composition_id in self.composition_layouts:
            del self.composition_layouts[composition_id]
        
        # Delete connections
        if composition_id in self.composition_connections:
            del self.composition_connections[composition_id]
        
        logger.info(f"Deleted composition {composition_id}")
        return True

    def get_composition(self, composition_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a capsule composition.
        
        Args:
            composition_id: ID of the composition to get
            
        Returns:
            Composition record if found, None otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return None
        
        return self.compositions[composition_id]

    def get_all_compositions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all capsule compositions.
        
        Returns:
            Dictionary of composition records
        """
        return self.compositions

    def add_capsule_to_composition(
        self,
        composition_id: str,
        capsule_type: str,
        position: Dict[str, float],
        capsule_config: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Add a capsule to a composition.
        
        Args:
            composition_id: ID of the composition
            capsule_type: Type of capsule to add
            position: Position of the capsule in the composition
            capsule_config: Optional configuration for the capsule
            
        Returns:
            Capsule ID if addition was successful, None otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return None
        
        # Generate capsule ID
        capsule_id = f"{capsule_type}_{str(uuid.uuid4())[:8]}"
        
        # Create capsule
        if not self.capsule_manager.create_capsule(capsule_id, capsule_type, capsule_config or {}):
            logger.error(f"Failed to create capsule of type {capsule_type}")
            return None
        
        # Add capsule to composition
        self.compositions[composition_id]["capsules"].append({
            "id": capsule_id,
            "type": capsule_type,
            "position": position,
            "created_at": time.time()
        })
        
        # Update composition
        self.compositions[composition_id]["updated_at"] = time.time()
        
        # Update layout
        if composition_id in self.composition_layouts:
            self.composition_layouts[composition_id]["positions"][capsule_id] = position
        
        logger.info(f"Added capsule {capsule_id} to composition {composition_id}")
        return capsule_id

    def remove_capsule_from_composition(
        self,
        composition_id: str,
        capsule_id: str
    ) -> bool:
        """
        Remove a capsule from a composition.
        
        Args:
            composition_id: ID of the composition
            capsule_id: ID of the capsule to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return False
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Find capsule in composition
        capsule_index = None
        for i, capsule_def in enumerate(composition["capsules"]):
            if capsule_def["id"] == capsule_id:
                capsule_index = i
                break
        
        if capsule_index is None:
            logger.warning(f"Capsule {capsule_id} not found in composition {composition_id}")
            return False
        
        # Remove capsule from composition
        composition["capsules"].pop(capsule_index)
        
        # Remove connections involving this capsule
        connections_to_remove = []
        for i, connection in enumerate(composition["connections"]):
            if connection["source"] == capsule_id or connection["target"] == capsule_id:
                connections_to_remove.append(i)
        
        # Remove connections in reverse order to avoid index issues
        for i in sorted(connections_to_remove, reverse=True):
            composition["connections"].pop(i)
        
        # Update composition
        composition["updated_at"] = time.time()
        
        # Update layout
        if composition_id in self.composition_layouts and capsule_id in self.composition_layouts[composition_id]["positions"]:
            del self.composition_layouts[composition_id]["positions"][capsule_id]
        
        # Deactivate capsule
        self.capsule_lifecycle_manager.deactivate_capsule(capsule_id)
        
        logger.info(f"Removed capsule {capsule_id} from composition {composition_id}")
        return True

    def update_capsule_position(
        self,
        composition_id: str,
        capsule_id: str,
        position: Dict[str, float]
    ) -> bool:
        """
        Update the position of a capsule in a composition.
        
        Args:
            composition_id: ID of the composition
            capsule_id: ID of the capsule
            position: New position of the capsule
            
        Returns:
            True if update was successful, False otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return False
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Find capsule in composition
        capsule_found = False
        for capsule_def in composition["capsules"]:
            if capsule_def["id"] == capsule_id:
                capsule_def["position"] = position
                capsule_found = True
                break
        
        if not capsule_found:
            logger.warning(f"Capsule {capsule_id} not found in composition {composition_id}")
            return False
        
        # Update composition
        composition["updated_at"] = time.time()
        
        # Update layout
        if composition_id in self.composition_layouts:
            self.composition_layouts[composition_id]["positions"][capsule_id] = position
        
        logger.debug(f"Updated position of capsule {capsule_id} in composition {composition_id}")
        return True

    def connect_capsules(
        self,
        composition_id: str,
        source_id: str,
        target_id: str,
        connection_type: ConnectionType = ConnectionType.DATA,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Connect two capsules in a composition.
        
        Args:
            composition_id: ID of the composition
            source_id: ID of the source capsule
            target_id: ID of the target capsule
            connection_type: Type of connection
            metadata: Optional metadata for the connection
            
        Returns:
            Connection ID if connection was successful, None otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return None
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Verify capsules exist in composition
        source_found = False
        target_found = False
        
        for capsule_def in composition["capsules"]:
            if capsule_def["id"] == source_id:
                source_found = True
            if capsule_def["id"] == target_id:
                target_found = True
        
        if not source_found:
            logger.warning(f"Source capsule {source_id} not found in composition {composition_id}")
            return None
        
        if not target_found:
            logger.warning(f"Target capsule {target_id} not found in composition {composition_id}")
            return None
        
        # Validate connection
        validation_result = self._validate_connection(
            composition_id,
            source_id,
            target_id,
            connection_type
        )
        
        if not validation_result["valid"]:
            logger.warning(f"Invalid connection: {validation_result['message']}")
            return None
        
        # Generate connection ID
        connection_id = str(uuid.uuid4())
        
        # Create connection
        connection = {
            "id": connection_id,
            "source": source_id,
            "target": target_id,
            "type": connection_type.value,
            "metadata": metadata or {},
            "created_at": time.time()
        }
        
        # Add connection to composition
        composition["connections"].append(connection)
        
        # Update composition
        composition["updated_at"] = time.time()
        
        # Store connection
        if composition_id not in self.composition_connections:
            self.composition_connections[composition_id] = {}
        
        self.composition_connections[composition_id][connection_id] = connection
        
        logger.info(f"Connected capsules {source_id} and {target_id} in composition {composition_id}")
        return connection_id

    def disconnect_capsules(
        self,
        composition_id: str,
        connection_id: str
    ) -> bool:
        """
        Disconnect two capsules in a composition.
        
        Args:
            composition_id: ID of the composition
            connection_id: ID of the connection
            
        Returns:
            True if disconnection was successful, False otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return False
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Find connection in composition
        connection_index = None
        for i, connection in enumerate(composition["connections"]):
            if connection["id"] == connection_id:
                connection_index = i
                break
        
        if connection_index is None:
            logger.warning(f"Connection {connection_id} not found in composition {composition_id}")
            return False
        
        # Remove connection from composition
        composition["connections"].pop(connection_index)
        
        # Update composition
        composition["updated_at"] = time.time()
        
        # Remove connection from storage
        if composition_id in self.composition_connections and connection_id in self.composition_connections[composition_id]:
            del self.composition_connections[composition_id][connection_id]
        
        logger.info(f"Disconnected connection {connection_id} in composition {composition_id}")
        return True

    def _validate_connection(
        self,
        composition_id: str,
        source_id: str,
        target_id: str,
        connection_type: ConnectionType
    ) -> Dict[str, Any]:
        """
        Validate a connection between two capsules.
        
        Args:
            composition_id: ID of the composition
            source_id: ID of the source capsule
            target_id: ID of the target capsule
            connection_type: Type of connection
            
        Returns:
            Validation result
        """
        # Basic validation
        if source_id == target_id:
            return {
                "valid": False,
                "message": "Cannot connect a capsule to itself",
                "severity": "error"
            }
        
        # Get capsule types
        source_type = None
        target_type = None
        
        for capsule_def in self.compositions[composition_id]["capsules"]:
            if capsule_def["id"] == source_id:
                source_type = capsule_def["type"]
            if capsule_def["id"] == target_id:
                target_type = capsule_def["type"]
        
        # Apply validation rules
        for rule_set_id, rule_set in self.composition_validation_rules.items():
            for rule in rule_set["rules"]:
                # Simple rule evaluation
                # In a real implementation, this would use a proper rule engine
                
                if "source.type" in rule["condition"] and "target.type" in rule["condition"]:
                    # Rule involves both source and target types
                    condition = rule["condition"]
                    condition = condition.replace("source.type", f"'{source_type}'")
                    condition = condition.replace("target.type", f"'{target_type}'")
                    
                    try:
                        if eval(condition):
                            return {
                                "valid": False,
                                "message": rule["message"],
                                "severity": rule["severity"]
                            }
                    except Exception as e:
                        logger.error(f"Error evaluating rule condition: {e}")
                
                if "connection.type" in rule["condition"]:
                    # Rule involves connection type
                    condition = rule["condition"]
                    condition = condition.replace("connection.type", f"'{connection_type.value}'")
                    condition = condition.replace("source.supports_trust", "True")  # Simplified
                    condition = condition.replace("target.supports_trust", "True")  # Simplified
                    condition = condition.replace("source.supports_context", "True")  # Simplified
                    condition = condition.replace("target.supports_context", "True")  # Simplified
                    
                    try:
                        if eval(condition):
                            return {
                                "valid": False,
                                "message": rule["message"],
                                "severity": rule["severity"]
                            }
                    except Exception as e:
                        logger.error(f"Error evaluating rule condition: {e}")
                
                if "has_cycle" in rule["condition"]:
                    # Check for cycles
                    # In a real implementation, this would use a proper cycle detection algorithm
                    # For simplicity, we'll just check for direct cycles
                    
                    for connection in self.compositions[composition_id]["connections"]:
                        if connection["source"] == target_id and connection["target"] == source_id:
                            return {
                                "valid": False,
                                "message": rule["message"],
                                "severity": rule["severity"]
                            }
        
        # If no rules failed, connection is valid
        return {
            "valid": True,
            "message": "Connection is valid",
            "severity": "info"
        }

    def validate_composition(self, composition_id: str) -> Dict[str, Any]:
        """
        Validate a composition.
        
        Args:
            composition_id: ID of the composition
            
        Returns:
            Validation result
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return {
                "valid": False,
                "message": f"Unknown composition ID: {composition_id}",
                "issues": []
            }
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Validate all connections
        issues = []
        
        for connection in composition["connections"]:
            source_id = connection["source"]
            target_id = connection["target"]
            connection_type = ConnectionType(connection["type"])
            
            validation_result = self._validate_connection(
                composition_id,
                source_id,
                target_id,
                connection_type
            )
            
            if not validation_result["valid"]:
                issues.append({
                    "type": "connection",
                    "connection_id": connection["id"],
                    "source_id": source_id,
                    "target_id": target_id,
                    "message": validation_result["message"],
                    "severity": validation_result["severity"]
                })
        
        # Check for orphaned capsules (no connections)
        connected_capsules = set()
        
        for connection in composition["connections"]:
            connected_capsules.add(connection["source"])
            connected_capsules.add(connection["target"])
        
        for capsule_def in composition["capsules"]:
            capsule_id = capsule_def["id"]
            
            if capsule_id not in connected_capsules:
                issues.append({
                    "type": "capsule",
                    "capsule_id": capsule_id,
                    "message": "Capsule is not connected to any other capsule",
                    "severity": "warning"
                })
        
        # Return validation result
        return {
            "valid": len(issues) == 0,
            "message": "Composition is valid" if len(issues) == 0 else f"Composition has {len(issues)} issues",
            "issues": issues
        }

    def apply_layout(
        self,
        composition_id: str,
        layout_type: CompositionLayout
    ) -> bool:
        """
        Apply a layout to a composition.
        
        Args:
            composition_id: ID of the composition
            layout_type: Type of layout to apply
            
        Returns:
            True if layout was applied, False otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return False
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Update layout type
        composition["layout"] = layout_type.value
        
        # Calculate positions based on layout type
        positions = self._calculate_layout_positions(composition, layout_type)
        
        # Update capsule positions
        for capsule_id, position in positions.items():
            for capsule_def in composition["capsules"]:
                if capsule_def["id"] == capsule_id:
                    capsule_def["position"] = position
                    break
        
        # Update layout
        self.composition_layouts[composition_id] = {
            "type": layout_type.value,
            "positions": positions
        }
        
        # Update composition
        composition["updated_at"] = time.time()
        
        logger.info(f"Applied layout {layout_type.value} to composition {composition_id}")
        return True

    def _calculate_layout_positions(
        self,
        composition: Dict[str, Any],
        layout_type: CompositionLayout
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate positions for capsules based on layout type.
        
        Args:
            composition: Composition record
            layout_type: Type of layout
            
        Returns:
            Dictionary mapping capsule IDs to positions
        """
        positions = {}
        capsules = composition["capsules"]
        connections = composition["connections"]
        
        if layout_type == CompositionLayout.FLOW:
            # Simple left-to-right flow layout
            # Find root capsules (no incoming connections)
            incoming_connections = {}
            
            for connection in connections:
                target = connection["target"]
                if target not in incoming_connections:
                    incoming_connections[target] = []
                incoming_connections[target].append(connection["source"])
            
            # Identify root capsules
            root_capsules = []
            for capsule_def in capsules:
                capsule_id = capsule_def["id"]
                if capsule_id not in incoming_connections:
                    root_capsules.append(capsule_id)
            
            # If no root capsules, use the first capsule
            if not root_capsules and capsules:
                root_capsules = [capsules[0]["id"]]
            
            # Calculate positions
            level_width = 200
            level_height = 150
            current_level = 0
            capsules_by_level = {0: root_capsules}
            visited = set(root_capsules)
            
            # Assign positions to root capsules
            for i, capsule_id in enumerate(root_capsules):
                positions[capsule_id] = {
                    "x": 100,
                    "y": 100 + i * level_height
                }
            
            # Breadth-first traversal to assign positions to other capsules
            while current_level in capsules_by_level:
                next_level = current_level + 1
                capsules_by_level[next_level] = []
                
                for capsule_id in capsules_by_level[current_level]:
                    # Find outgoing connections
                    for connection in connections:
                        if connection["source"] == capsule_id:
                            target_id = connection["target"]
                            
                            if target_id not in visited:
                                capsules_by_level[next_level].append(target_id)
                                visited.add(target_id)
                
                # Assign positions to capsules in next level
                for i, capsule_id in enumerate(capsules_by_level[next_level]):
                    positions[capsule_id] = {
                        "x": 100 + next_level * level_width,
                        "y": 100 + i * level_height
                    }
                
                current_level = next_level
        
        elif layout_type == CompositionLayout.GRID:
            # Simple grid layout
            cols = max(int(len(capsules) ** 0.5), 1)
            rows = (len(capsules) + cols - 1) // cols
            
            for i, capsule_def in enumerate(capsules):
                row = i // cols
                col = i % cols
                
                positions[capsule_def["id"]] = {
                    "x": 100 + col * 200,
                    "y": 100 + row * 150
                }
        
        elif layout_type == CompositionLayout.RADIAL:
            # Simple radial layout
            center_x = 400
            center_y = 300
            radius = min(center_x, center_y) - 50
            
            for i, capsule_def in enumerate(capsules):
                angle = 2 * math.pi * i / len(capsules)
                
                positions[capsule_def["id"]] = {
                    "x": center_x + radius * math.cos(angle),
                    "y": center_y + radius * math.sin(angle)
                }
        
        elif layout_type == CompositionLayout.HIERARCHICAL:
            # Simple hierarchical layout
            # Similar to flow layout but with more vertical spacing
            # Find root capsules (no incoming connections)
            incoming_connections = {}
            
            for connection in connections:
                target = connection["target"]
                if target not in incoming_connections:
                    incoming_connections[target] = []
                incoming_connections[target].append(connection["source"])
            
            # Identify root capsules
            root_capsules = []
            for capsule_def in capsules:
                capsule_id = capsule_def["id"]
                if capsule_id not in incoming_connections:
                    root_capsules.append(capsule_id)
            
            # If no root capsules, use the first capsule
            if not root_capsules and capsules:
                root_capsules = [capsules[0]["id"]]
            
            # Calculate positions
            level_width = 250
            level_height = 200
            current_level = 0
            capsules_by_level = {0: root_capsules}
            visited = set(root_capsules)
            
            # Assign positions to root capsules
            for i, capsule_id in enumerate(root_capsules):
                positions[capsule_id] = {
                    "x": 100,
                    "y": 100 + i * level_height
                }
            
            # Breadth-first traversal to assign positions to other capsules
            while current_level in capsules_by_level:
                next_level = current_level + 1
                capsules_by_level[next_level] = []
                
                for capsule_id in capsules_by_level[current_level]:
                    # Find outgoing connections
                    for connection in connections:
                        if connection["source"] == capsule_id:
                            target_id = connection["target"]
                            
                            if target_id not in visited:
                                capsules_by_level[next_level].append(target_id)
                                visited.add(target_id)
                
                # Assign positions to capsules in next level
                for i, capsule_id in enumerate(capsules_by_level[next_level]):
                    positions[capsule_id] = {
                        "x": 100 + next_level * level_width,
                        "y": 100 + i * level_height
                    }
                
                current_level = next_level
        
        elif layout_type == CompositionLayout.FREEFORM:
            # Use existing positions or default
            for capsule_def in capsules:
                capsule_id = capsule_def["id"]
                if "position" in capsule_def:
                    positions[capsule_id] = capsule_def["position"]
                else:
                    positions[capsule_id] = {"x": 100, "y": 100}
        
        return positions

    def create_template_from_composition(
        self,
        composition_id: str,
        template_name: str,
        template_description: str
    ) -> Optional[str]:
        """
        Create a template from an existing composition.
        
        Args:
            composition_id: ID of the composition
            template_name: Name for the template
            template_description: Description for the template
            
        Returns:
            Template ID if creation was successful, None otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return None
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Generate template ID
        template_id = str(uuid.uuid4())
        
        # Create template
        template = {
            "id": template_id,
            "name": template_name,
            "description": template_description,
            "layout": composition["layout"],
            "capsules": [],
            "connections": []
        }
        
        # Copy capsules
        for capsule_def in composition["capsules"]:
            template["capsules"].append({
                "id": capsule_def["id"],
                "type": capsule_def["type"],
                "position": capsule_def.get("position", {"x": 0, "y": 0})
            })
        
        # Copy connections
        for connection in composition["connections"]:
            template["connections"].append({
                "source": connection["source"],
                "target": connection["target"],
                "type": connection["type"]
            })
        
        # Store template
        self.composition_templates[template_id] = template
        
        logger.info(f"Created template {template_id} from composition {composition_id}")
        return template_id

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a composition template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Template record if found, None otherwise
        """
        return self.composition_templates.get(template_id)

    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all composition templates.
        
        Returns:
            Dictionary of template records
        """
        return self.composition_templates

    def delete_template(self, template_id: str) -> bool:
        """
        Delete a composition template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if template_id not in self.composition_templates:
            logger.warning(f"Unknown template ID: {template_id}")
            return False
        
        # Delete template
        del self.composition_templates[template_id]
        
        logger.info(f"Deleted template {template_id}")
        return True

    def export_composition(
        self,
        composition_id: str,
        format: str = "json"
    ) -> Optional[str]:
        """
        Export a composition to a specified format.
        
        Args:
            composition_id: ID of the composition
            format: Export format ("json" or "yaml")
            
        Returns:
            Exported composition as string if successful, None otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return None
        
        # Get composition
        composition = self.compositions[composition_id]
        
        if format.lower() == "json":
            return json.dumps(composition, indent=2)
        
        elif format.lower() == "yaml":
            try:
                import yaml
                return yaml.dump(composition, default_flow_style=False)
            except ImportError:
                logger.error("PyYAML not installed, falling back to JSON")
                return json.dumps(composition, indent=2)
        
        else:
            logger.error(f"Unsupported export format: {format}")
            return None

    def import_composition(
        self,
        data: str,
        format: str = "json",
        name_suffix: str = ""
    ) -> Optional[str]:
        """
        Import a composition from a specified format.
        
        Args:
            data: Composition data
            format: Import format ("json" or "yaml")
            name_suffix: Optional suffix to add to composition name
            
        Returns:
            Composition ID if import was successful, None otherwise
        """
        try:
            if format.lower() == "json":
                composition_data = json.loads(data)
            
            elif format.lower() == "yaml":
                try:
                    import yaml
                    composition_data = yaml.safe_load(data)
                except ImportError:
                    logger.error("PyYAML not installed")
                    return None
            
            else:
                logger.error(f"Unsupported import format: {format}")
                return None
            
            # Generate new composition ID
            composition_id = str(uuid.uuid4())
            
            # Update composition data
            composition_data["id"] = composition_id
            composition_data["name"] = composition_data["name"] + name_suffix
            composition_data["created_at"] = time.time()
            composition_data["updated_at"] = time.time()
            
            # Store composition
            self.compositions[composition_id] = composition_data
            
            # Store layout
            self.composition_layouts[composition_id] = {
                "type": composition_data.get("layout", CompositionLayout.FLOW.value),
                "positions": {}
            }
            
            # Extract positions from capsules
            for capsule_def in composition_data["capsules"]:
                if "position" in capsule_def:
                    self.composition_layouts[composition_id]["positions"][capsule_def["id"]] = capsule_def["position"]
            
            logger.info(f"Imported composition {composition_id}")
            return composition_id
        
        except Exception as e:
            logger.error(f"Error importing composition: {e}")
            return None

    def activate_composition(
        self,
        composition_id: str,
        callback: Optional[Callable] = None
    ) -> bool:
        """
        Activate all capsules in a composition.
        
        Args:
            composition_id: ID of the composition
            callback: Optional callback function to call when activation completes
            
        Returns:
            True if activation was initiated, False otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return False
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Activate all capsules
        for capsule_def in composition["capsules"]:
            capsule_id = capsule_def["id"]
            self.capsule_lifecycle_manager.activate_capsule(capsule_id)
        
        # Store callback if provided
        if callback:
            self.composition_callbacks[composition_id] = callback
        
        logger.info(f"Activated composition {composition_id}")
        return True

    def deactivate_composition(
        self,
        composition_id: str,
        callback: Optional[Callable] = None
    ) -> bool:
        """
        Deactivate all capsules in a composition.
        
        Args:
            composition_id: ID of the composition
            callback: Optional callback function to call when deactivation completes
            
        Returns:
            True if deactivation was initiated, False otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return False
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Deactivate all capsules
        for capsule_def in composition["capsules"]:
            capsule_id = capsule_def["id"]
            self.capsule_lifecycle_manager.deactivate_capsule(capsule_id)
        
        # Store callback if provided
        if callback:
            self.composition_callbacks[composition_id] = callback
        
        logger.info(f"Deactivated composition {composition_id}")
        return True

    def get_composition_status(self, composition_id: str) -> Dict[str, Any]:
        """
        Get the status of a composition.
        
        Args:
            composition_id: ID of the composition
            
        Returns:
            Composition status
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return {
                "status": "unknown",
                "capsules": {},
                "connections": {}
            }
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Get status of all capsules
        capsule_statuses = {}
        for capsule_def in composition["capsules"]:
            capsule_id = capsule_def["id"]
            capsule_status = self.capsule_state_manager.get_capsule_state(capsule_id)
            capsule_statuses[capsule_id] = capsule_status or {"status": "unknown"}
        
        # Get status of all connections
        connection_statuses = {}
        for connection in composition["connections"]:
            connection_id = connection["id"]
            source_id = connection["source"]
            target_id = connection["target"]
            
            # Determine connection status based on capsule statuses
            source_status = capsule_statuses.get(source_id, {}).get("status", "unknown")
            target_status = capsule_statuses.get(target_id, {}).get("status", "unknown")
            
            if source_status == "active" and target_status == "active":
                connection_status = "active"
            elif source_status == "error" or target_status == "error":
                connection_status = "error"
            elif source_status == "inactive" or target_status == "inactive":
                connection_status = "inactive"
            else:
                connection_status = "unknown"
            
            connection_statuses[connection_id] = {
                "status": connection_status,
                "source_status": source_status,
                "target_status": target_status
            }
        
        # Determine overall composition status
        active_count = 0
        error_count = 0
        inactive_count = 0
        
        for status in capsule_statuses.values():
            if status.get("status") == "active":
                active_count += 1
            elif status.get("status") == "error":
                error_count += 1
            elif status.get("status") == "inactive":
                inactive_count += 1
        
        if error_count > 0:
            overall_status = "error"
        elif active_count == len(composition["capsules"]):
            overall_status = "active"
        elif inactive_count == len(composition["capsules"]):
            overall_status = "inactive"
        elif active_count > 0:
            overall_status = "partially_active"
        else:
            overall_status = "unknown"
        
        return {
            "status": overall_status,
            "capsules": capsule_statuses,
            "connections": connection_statuses,
            "active_count": active_count,
            "error_count": error_count,
            "inactive_count": inactive_count,
            "total_count": len(composition["capsules"])
        }

    def get_composition_analytics(self, composition_id: str) -> Dict[str, Any]:
        """
        Get analytics for a composition.
        
        Args:
            composition_id: ID of the composition
            
        Returns:
            Composition analytics
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return {}
        
        # Get composition
        composition = self.compositions[composition_id]
        
        # Calculate analytics
        capsule_count = len(composition["capsules"])
        connection_count = len(composition["connections"])
        
        # Count capsules by type
        capsule_types = {}
        for capsule_def in composition["capsules"]:
            capsule_type = capsule_def["type"]
            capsule_types[capsule_type] = capsule_types.get(capsule_type, 0) + 1
        
        # Count connections by type
        connection_types = {}
        for connection in composition["connections"]:
            connection_type = connection["type"]
            connection_types[connection_type] = connection_types.get(connection_type, 0) + 1
        
        # Calculate connectivity metrics
        if capsule_count > 0:
            avg_connections_per_capsule = connection_count / capsule_count
        else:
            avg_connections_per_capsule = 0
        
        # Calculate complexity metrics
        complexity = connection_count * 0.7 + capsule_count * 0.3
        
        return {
            "capsule_count": capsule_count,
            "connection_count": connection_count,
            "capsule_types": capsule_types,
            "connection_types": connection_types,
            "avg_connections_per_capsule": avg_connections_per_capsule,
            "complexity": complexity
        }

    def clone_composition(
        self,
        composition_id: str,
        new_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Clone a composition.
        
        Args:
            composition_id: ID of the composition to clone
            new_name: Optional name for the cloned composition
            
        Returns:
            ID of the cloned composition if successful, None otherwise
        """
        if composition_id not in self.compositions:
            logger.warning(f"Unknown composition ID: {composition_id}")
            return None
        
        # Export composition to JSON
        composition_json = self.export_composition(composition_id, "json")
        
        if not composition_json:
            logger.error(f"Failed to export composition {composition_id}")
            return None
        
        # Import composition with new name
        name_suffix = f" (Clone)" if new_name is None else f" ({new_name})"
        
        cloned_id = self.import_composition(composition_json, "json", name_suffix)
        
        if not cloned_id:
            logger.error(f"Failed to import cloned composition")
            return None
        
        logger.info(f"Cloned composition {composition_id} to {cloned_id}")
        return cloned_id
