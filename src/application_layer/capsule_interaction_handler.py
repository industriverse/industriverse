"""
Capsule Interaction Handler for Application Layer.

This module provides the interaction handler for Dynamic Agent Capsules
in the Universal Skin UX concept.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CapsuleInteractionHandler:
    """
    Interaction handler for Dynamic Agent Capsules.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the Capsule Interaction Handler.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        logger.info("Capsule Interaction Handler initialized")
    
    def handle_interaction(self, capsule: Dict[str, Any], interaction_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle interaction with a capsule.
        
        Args:
            capsule: Capsule data
            interaction_type: Type of interaction
            data: Interaction data
            
        Returns:
            Response data
        """
        # Handle common interactions
        if interaction_type == "expand_collapse":
            return self._handle_expand_collapse(capsule, data)
        elif interaction_type == "pin_unpin":
            return self._handle_pin_unpin(capsule, data)
        elif interaction_type == "drag":
            return self._handle_drag(capsule, data)
        elif interaction_type == "resize":
            return self._handle_resize(capsule, data)
        elif interaction_type == "click":
            return self._handle_click(capsule, data)
        
        # Handle type-specific interactions
        capsule_type = capsule.get("capsule_type", "status")
        
        if capsule_type == "task":
            return self._handle_task_interaction(capsule, interaction_type, data)
        elif capsule_type == "workflow":
            return self._handle_workflow_interaction(capsule, interaction_type, data)
        elif capsule_type == "alert":
            return self._handle_alert_interaction(capsule, interaction_type, data)
        elif capsule_type == "status":
            return self._handle_status_interaction(capsule, interaction_type, data)
        elif capsule_type == "decision":
            return self._handle_decision_interaction(capsule, interaction_type, data)
        
        logger.warning(f"Unknown interaction type: {interaction_type} for capsule type: {capsule_type}")
        return {"error": f"Unknown interaction type: {interaction_type} for capsule type: {capsule_type}"}
    
    def _handle_expand_collapse(self, capsule: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle expand/collapse interaction.
        
        Args:
            capsule: Capsule data
            data: Interaction data
            
        Returns:
            Response data
        """
        # Check if expandable
        if not capsule.get("interaction", {}).get("expandable", True):
            return {"error": "Capsule is not expandable"}
        
        # Get current expanded state
        current_expanded = capsule.get("display", {}).get("expanded", False)
        
        # Toggle expanded state
        new_expanded = not current_expanded
        
        # Update capsule
        if "display" not in capsule:
            capsule["display"] = {}
        
        capsule["display"]["expanded"] = new_expanded
        capsule["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Capsule {capsule.get('capsule_id', '')} expanded state changed to {new_expanded}")
        
        return {
            "success": True,
            "capsule_id": capsule.get("capsule_id", ""),
            "expanded": new_expanded
        }
    
    def _handle_pin_unpin(self, capsule: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle pin/unpin interaction.
        
        Args:
            capsule: Capsule data
            data: Interaction data
            
        Returns:
            Response data
        """
        # Check if pinnable
        if not capsule.get("interaction", {}).get("pinnable", True):
            return {"error": "Capsule is not pinnable"}
        
        # Get current pinned state
        current_pinned = capsule.get("pin_info", {}).get("pinned", False)
        
        # Toggle pinned state
        new_pinned = not current_pinned
        
        # Get pin mode and location
        pin_mode = data.get("pin_mode", capsule.get("pin_info", {}).get("pin_mode"))
        pin_location = data.get("pin_location", capsule.get("pin_info", {}).get("pin_location"))
        
        # Validate pin mode
        valid_pin_modes = ["os_desktop", "browser", "mobile_bar", "ar_space"]
        if pin_mode and pin_mode not in valid_pin_modes:
            return {"error": f"Invalid pin mode: {pin_mode}"}
        
        # Update capsule
        if "pin_info" not in capsule:
            capsule["pin_info"] = {}
        
        capsule["pin_info"]["pinned"] = new_pinned
        
        if new_pinned and pin_mode:
            capsule["pin_info"]["pin_mode"] = pin_mode
        
        if new_pinned and pin_location:
            capsule["pin_info"]["pin_location"] = pin_location
        
        capsule["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Capsule {capsule.get('capsule_id', '')} pinned state changed to {new_pinned}")
        
        return {
            "success": True,
            "capsule_id": capsule.get("capsule_id", ""),
            "pinned": new_pinned,
            "pin_mode": capsule["pin_info"].get("pin_mode"),
            "pin_location": capsule["pin_info"].get("pin_location")
        }
    
    def _handle_drag(self, capsule: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle drag interaction.
        
        Args:
            capsule: Capsule data
            data: Interaction data
            
        Returns:
            Response data
        """
        # Check if draggable
        if not capsule.get("interaction", {}).get("draggable", True):
            return {"error": "Capsule is not draggable"}
        
        # Get new position
        position_x = data.get("position_x")
        position_y = data.get("position_y")
        
        if position_x is None or position_y is None:
            return {"error": "Missing position coordinates"}
        
        # Update capsule
        if "display" not in capsule:
            capsule["display"] = {}
        
        if "position" not in capsule["display"]:
            capsule["display"]["position"] = {}
        
        capsule["display"]["position"]["x"] = position_x
        capsule["display"]["position"]["y"] = position_y
        capsule["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Capsule {capsule.get('capsule_id', '')} position updated to ({position_x}, {position_y})")
        
        return {
            "success": True,
            "capsule_id": capsule.get("capsule_id", ""),
            "position": {
                "x": position_x,
                "y": position_y
            }
        }
    
    def _handle_resize(self, capsule: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle resize interaction.
        
        Args:
            capsule: Capsule data
            data: Interaction data
            
        Returns:
            Response data
        """
        # Check if resizable
        if not capsule.get("interaction", {}).get("resizable", True):
            return {"error": "Capsule is not resizable"}
        
        # Get new size
        size = data.get("size")
        
        if not size:
            return {"error": "Missing size"}
        
        # Validate size
        valid_sizes = ["small", "medium", "large", "custom"]
        if size not in valid_sizes and not isinstance(size, dict):
            return {"error": f"Invalid size: {size}"}
        
        # Update capsule
        if "display" not in capsule:
            capsule["display"] = {}
        
        capsule["display"]["size"] = size
        capsule["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Capsule {capsule.get('capsule_id', '')} size updated to {size}")
        
        return {
            "success": True,
            "capsule_id": capsule.get("capsule_id", ""),
            "size": size
        }
    
    def _handle_click(self, capsule: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle click interaction.
        
        Args:
            capsule: Capsule data
            data: Interaction data
            
        Returns:
            Response data
        """
        # Check if clickable
        if not capsule.get("interaction", {}).get("clickable", True):
            return {"error": "Capsule is not clickable"}
        
        # Get click target
        target = data.get("target", "capsule")
        
        # Handle click based on target
        if target == "capsule":
            # Default behavior is to expand/collapse
            return self._handle_expand_collapse(capsule, data)
        elif target.startswith("action:"):
            # Handle action click
            action_id = target.split(":", 1)[1]
            return self._handle_action_click(capsule, action_id, data)
        elif target.startswith("component:"):
            # Handle component click
            component_id = target.split(":", 1)[1]
            return self._handle_component_click(capsule, component_id, data)
        
        logger.warning(f"Unknown click target: {target}")
        return {"error": f"Unknown click target: {target}"}
    
    def _handle_action_click(self, capsule: Dict[str, Any], action_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle action click interaction.
        
        Args:
            capsule: Capsule data
            action_id: ID of the action
            data: Interaction data
            
        Returns:
            Response data
        """
        # Get capsule type
        capsule_type = capsule.get("capsule_type", "status")
        
        # Handle common actions
        if action_id == "expand_collapse":
            return self._handle_expand_collapse(capsule, data)
        elif action_id == "pin_unpin":
            return self._handle_pin_unpin(capsule, data)
        
        # Handle type-specific actions
        if capsule_type == "task":
            return self._handle_task_action(capsule, action_id, data)
        elif capsule_type == "workflow":
            return self._handle_workflow_action(capsule, action_id, data)
        elif capsule_type == "alert":
            return self._handle_alert_action(capsule, action_id, data)
        elif capsule_type == "status":
            return self._handle_status_action(capsule, action_id, data)
        elif capsule_type == "decision":
            return self._handle_decision_action(capsule, action_id, data)
        
        logger.warning(f"Unknown action: {action_id} for capsule type: {capsule_type}")
        return {"error": f"Unknown action: {action_id} for capsule type: {capsule_type}"}
    
    def _handle_component_click(self, capsule: Dict[str, Any], component_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle component click interaction.
        
        Args:
            capsule: Capsule data
            component_id: ID of the component
            data: Interaction data
            
        Returns:
            Response data
        """
        # Get capsule type
        capsule_type = capsule.get("capsule_type", "status")
        
        # Handle type-specific component clicks
        if capsule_type == "task":
            return self._handle_task_component_click(capsule, component_id, data)
        elif capsule_type == "workflow":
            return self._handle_workflow_component_click(capsule, component_id, data)
        elif capsule_type == "alert":
            return self._handle_alert_component_click(capsule, component_id, data)
        elif capsule_type == "status":
            return self._handle_status_component_click(capsule, component_id, data)
        elif capsule_type == "decision":
            return self._handle_decision_component_click(capsule, component_id, data)
        
        logger.warning(f"Unknown component: {component_id} for capsule type: {capsule_type}")
        return {"error": f"Unknown component: {component_id} for capsule type: {capsule_type}"}
    
    def _handle_task_interaction(self, capsule: Dict[str, Any], interaction_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task capsule interaction.
        
        Args:
            capsule: Capsule data
            interaction_type: Type of interaction
            data: Interaction data
            
        Returns:
            Response data
        """
        if interaction_type == "complete_task":
            return self._handle_task_action(capsule, "complete_task", data)
        elif interaction_type == "reassign_task":
            return self._handle_task_action(capsule, "reassign_task", data)
        
        logger.warning(f"Unknown task interaction: {interaction_type}")
        return {"error": f"Unknown task interaction: {interaction_type}"}
    
    def _handle_task_action(self, capsule: Dict[str, Any], action_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task capsule action.
        
        Args:
            capsule: Capsule data
            action_id: ID of the action
            data: Action data
            
        Returns:
            Response data
        """
        if action_id == "complete_task":
            # Update task status
            if "task_info" not in capsule:
                capsule["task_info"] = {}
            
            capsule["task_info"]["status"] = "completed"
            capsule["task_info"]["completion"] = 100
            
            # Update content
            if "content" not in capsule:
                capsule["content"] = {}
            
            capsule["content"]["status"] = "completed"
            capsule["content"]["progress"] = 100
            
            # Update timestamp
            capsule["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Task {capsule.get('task_info', {}).get('task_id', '')} marked as completed")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "task_id": capsule.get("task_info", {}).get("task_id", ""),
                "status": "completed"
            }
        elif action_id == "reassign_task":
            # Get new assignee
            assignee = data.get("assignee")
            
            if not assignee:
                return {"error": "Missing assignee"}
            
            # Update task assignee
            if "task_info" not in capsule:
                capsule["task_info"] = {}
            
            capsule["task_info"]["assignee"] = assignee
            
            # Update timestamp
            capsule["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Task {capsule.get('task_info', {}).get('task_id', '')} reassigned to {assignee}")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "task_id": capsule.get("task_info", {}).get("task_id", ""),
                "assignee": assignee
            }
        
        logger.warning(f"Unknown task action: {action_id}")
        return {"error": f"Unknown task action: {action_id}"}
    
    def _handle_task_component_click(self, capsule: Dict[str, Any], component_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task capsule component click.
        
        Args:
            capsule: Capsule data
            component_id: ID of the component
            data: Interaction data
            
        Returns:
            Response data
        """
        if component_id == "progress_bar":
            # Show task details
            return self._handle_expand_collapse(capsule, data)
        elif component_id == "assignee_avatar":
            # Show assignee details
            assignee = capsule.get("task_info", {}).get("assignee", "")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "action": "show_assignee_details",
                "assignee": assignee
            }
        elif component_id == "due_date":
            # Show calendar
            due_date = capsule.get("task_info", {}).get("due_date", "")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "action": "show_calendar",
                "due_date": due_date
            }
        
        logger.warning(f"Unknown task component: {component_id}")
        return {"error": f"Unknown task component: {component_id}"}
    
    def _handle_workflow_interaction(self, capsule: Dict[str, Any], interaction_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle workflow capsule interaction.
        
        Args:
            capsule: Capsule data
            interaction_type: Type of interaction
            data: Interaction data
            
        Returns:
            Response data
        """
        if interaction_type == "pause_workflow":
            return self._handle_workflow_action(capsule, "pause_workflow", data)
        elif interaction_type == "skip_step":
            return self._handle_workflow_action(capsule, "skip_step", data)
        
        logger.warning(f"Unknown workflow interaction: {interaction_type}")
        return {"error": f"Unknown workflow interaction: {interaction_type}"}
    
    def _handle_workflow_action(self, capsule: Dict[str, Any], action_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle workflow capsule action.
        
        Args:
            capsule: Capsule data
            action_id: ID of the action
            data: Action data
            
        Returns:
            Response data
        """
        if action_id == "pause_workflow":
            # Update workflow status
            if "content" not in capsule:
                capsule["content"] = {}
            
            capsule["content"]["status"] = "paused"
            
            # Update timestamp
            capsule["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Workflow {capsule.get('workflow_info', {}).get('workflow_id', '')} paused")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "workflow_id": capsule.get("workflow_info", {}).get("workflow_id", ""),
                "status": "paused"
            }
        elif action_id == "skip_step":
            # Get workflow info
            workflow_info = capsule.get("workflow_info", {})
            current_step = workflow_info.get("current_step", 0)
            total_steps = workflow_info.get("total_steps", 0)
            
            # Check if can skip
            if current_step >= total_steps:
                return {"error": "Cannot skip step, workflow already completed"}
            
            # Update workflow step
            if "workflow_info" not in capsule:
                capsule["workflow_info"] = {}
            
            capsule["workflow_info"]["current_step"] = current_step + 1
            
            # Update step status
            step_status = workflow_info.get("step_status", [])
            if len(step_status) > current_step:
                step_status[current_step] = "skipped"
            
            capsule["workflow_info"]["step_status"] = step_status
            
            # Calculate progress
            progress = 0
            if total_steps > 0:
                progress = ((current_step + 1) / total_steps) * 100
            
            # Update content
            if "content" not in capsule:
                capsule["content"] = {}
            
            capsule["content"]["progress"] = progress
            
            # Update timestamp
            capsule["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Workflow {workflow_info.get('workflow_id', '')} skipped step {current_step}")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "workflow_id": workflow_info.get("workflow_id", ""),
                "current_step": current_step + 1,
                "progress": progress
            }
        
        logger.warning(f"Unknown workflow action: {action_id}")
        return {"error": f"Unknown workflow action: {action_id}"}
    
    def _handle_workflow_component_click(self, capsule: Dict[str, Any], component_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle workflow capsule component click.
        
        Args:
            capsule: Capsule data
            component_id: ID of the component
            data: Interaction data
            
        Returns:
            Response data
        """
        if component_id == "step_indicator":
            # Show step details
            step_index = data.get("step_index")
            
            if step_index is None:
                return {"error": "Missing step index"}
            
            workflow_info = capsule.get("workflow_info", {})
            step_status = workflow_info.get("step_status", [])
            
            if step_index >= len(step_status):
                return {"error": f"Invalid step index: {step_index}"}
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "action": "show_step_details",
                "step_index": step_index,
                "step_status": step_status[step_index]
            }
        elif component_id == "progress_bar":
            # Show workflow details
            return self._handle_expand_collapse(capsule, data)
        elif component_id == "time_estimate":
            # Show timeline
            estimated_completion = capsule.get("workflow_info", {}).get("estimated_completion", "")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "action": "show_timeline",
                "estimated_completion": estimated_completion
            }
        
        logger.warning(f"Unknown workflow component: {component_id}")
        return {"error": f"Unknown workflow component: {component_id}"}
    
    def _handle_alert_interaction(self, capsule: Dict[str, Any], interaction_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle alert capsule interaction.
        
        Args:
            capsule: Capsule data
            interaction_type: Type of interaction
            data: Interaction data
            
        Returns:
            Response data
        """
        if interaction_type == "acknowledge_alert":
            return self._handle_alert_action(capsule, "acknowledge_alert", data)
        elif interaction_type == "dismiss_alert":
            return self._handle_alert_action(capsule, "dismiss_alert", data)
        
        logger.warning(f"Unknown alert interaction: {interaction_type}")
        return {"error": f"Unknown alert interaction: {interaction_type}"}
    
    def _handle_alert_action(self, capsule: Dict[str, Any], action_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle alert capsule action.
        
        Args:
            capsule: Capsule data
            action_id: ID of the action
            data: Action data
            
        Returns:
            Response data
        """
        if action_id == "acknowledge_alert":
            # Get user info
            user = data.get("user", "system")
            
            # Update alert status
            if "alert_info" not in capsule:
                capsule["alert_info"] = {}
            
            capsule["alert_info"]["acknowledged"] = True
            capsule["alert_info"]["acknowledged_by"] = user
            capsule["alert_info"]["acknowledged_at"] = datetime.utcnow().isoformat()
            
            # Update content
            if "content" not in capsule:
                capsule["content"] = {}
            
            capsule["content"]["status"] = "acknowledged"
            
            # Update timestamp
            capsule["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Alert {capsule.get('alert_info', {}).get('alert_id', '')} acknowledged by {user}")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "alert_id": capsule.get("alert_info", {}).get("alert_id", ""),
                "acknowledged": True,
                "acknowledged_by": user,
                "acknowledged_at": capsule["alert_info"]["acknowledged_at"]
            }
        elif action_id == "dismiss_alert":
            # Update alert status
            if "alert_info" not in capsule:
                capsule["alert_info"] = {}
            
            # Mark for deletion
            capsule["state"] = "deleted"
            
            # Update timestamp
            capsule["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Alert {capsule.get('alert_info', {}).get('alert_id', '')} dismissed")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "alert_id": capsule.get("alert_info", {}).get("alert_id", ""),
                "dismissed": True
            }
        
        logger.warning(f"Unknown alert action: {action_id}")
        return {"error": f"Unknown alert action: {action_id}"}
    
    def _handle_alert_component_click(self, capsule: Dict[str, Any], component_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle alert capsule component click.
        
        Args:
            capsule: Capsule data
            component_id: ID of the component
            data: Interaction data
            
        Returns:
            Response data
        """
        if component_id == "severity_indicator":
            # Show alert details
            return self._handle_expand_collapse(capsule, data)
        elif component_id == "category_badge":
            # Show category details
            category = capsule.get("alert_info", {}).get("category", "system")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "action": "show_category_details",
                "category": category
            }
        
        logger.warning(f"Unknown alert component: {component_id}")
        return {"error": f"Unknown alert component: {component_id}"}
    
    def _handle_status_interaction(self, capsule: Dict[str, Any], interaction_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle status capsule interaction.
        
        Args:
            capsule: Capsule data
            interaction_type: Type of interaction
            data: Interaction data
            
        Returns:
            Response data
        """
        if interaction_type == "refresh_status":
            return self._handle_status_action(capsule, "refresh_status", data)
        elif interaction_type == "view_history":
            return self._handle_status_action(capsule, "view_history", data)
        
        logger.warning(f"Unknown status interaction: {interaction_type}")
        return {"error": f"Unknown status interaction: {interaction_type}"}
    
    def _handle_status_action(self, capsule: Dict[str, Any], action_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle status capsule action.
        
        Args:
            capsule: Capsule data
            action_id: ID of the action
            data: Action data
            
        Returns:
            Response data
        """
        if action_id == "refresh_status":
            # Get source component
            source_id = capsule.get("source_id", "")
            
            # Request status update from source
            status_update = self.agent_core.request_status_update(source_id)
            
            if not status_update:
                return {"error": f"Failed to get status update from {source_id}"}
            
            # Update status info
            if "status_info" not in capsule:
                capsule["status_info"] = {}
            
            # Store previous value
            previous_value = capsule["status_info"].get("value", "")
            
            # Update with new values
            capsule["status_info"]["previous_value"] = previous_value
            capsule["status_info"]["value"] = status_update.get("value", "")
            capsule["status_info"]["changed_at"] = datetime.utcnow().isoformat()
            
            # Determine trend
            if "trend" in status_update:
                capsule["status_info"]["trend"] = status_update["trend"]
            else:
                # Calculate trend based on previous value
                if previous_value and status_update.get("value"):
                    try:
                        prev_val = float(previous_value)
                        curr_val = float(status_update["value"])
                        
                        if curr_val > prev_val:
                            capsule["status_info"]["trend"] = "up"
                        elif curr_val < prev_val:
                            capsule["status_info"]["trend"] = "down"
                        else:
                            capsule["status_info"]["trend"] = "stable"
                    except (ValueError, TypeError):
                        # Non-numeric values
                        if previous_value != status_update["value"]:
                            capsule["status_info"]["trend"] = "changed"
                        else:
                            capsule["status_info"]["trend"] = "stable"
            
            # Update content
            if "content" not in capsule:
                capsule["content"] = {}
            
            capsule["content"]["status"] = status_update.get("status", "updated")
            
            # Update timestamp
            capsule["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Status {capsule.get('status_info', {}).get('status_id', '')} refreshed")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "status_id": capsule.get("status_info", {}).get("status_id", ""),
                "value": capsule["status_info"]["value"],
                "previous_value": capsule["status_info"]["previous_value"],
                "trend": capsule["status_info"]["trend"]
            }
        elif action_id == "view_history":
            # Get source component
            source_id = capsule.get("source_id", "")
            
            # Request status history from source
            status_history = self.agent_core.request_status_history(source_id)
            
            if not status_history:
                return {"error": f"Failed to get status history from {source_id}"}
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "status_id": capsule.get("status_info", {}).get("status_id", ""),
                "history": status_history
            }
        
        logger.warning(f"Unknown status action: {action_id}")
        return {"error": f"Unknown status action: {action_id}"}
    
    def _handle_status_component_click(self, capsule: Dict[str, Any], component_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle status capsule component click.
        
        Args:
            capsule: Capsule data
            component_id: ID of the component
            data: Interaction data
            
        Returns:
            Response data
        """
        if component_id == "status_indicator":
            # Show status details
            return self._handle_expand_collapse(capsule, data)
        elif component_id == "category_badge":
            # Show category details
            category = capsule.get("status_info", {}).get("category", "system")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "action": "show_category_details",
                "category": category
            }
        
        logger.warning(f"Unknown status component: {component_id}")
        return {"error": f"Unknown status component: {component_id}"}
    
    def _handle_decision_interaction(self, capsule: Dict[str, Any], interaction_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle decision capsule interaction.
        
        Args:
            capsule: Capsule data
            interaction_type: Type of interaction
            data: Interaction data
            
        Returns:
            Response data
        """
        if interaction_type == "make_decision":
            return self._handle_decision_action(capsule, "make_decision", data)
        elif interaction_type == "request_more_info":
            return self._handle_decision_action(capsule, "request_more_info", data)
        
        logger.warning(f"Unknown decision interaction: {interaction_type}")
        return {"error": f"Unknown decision interaction: {interaction_type}"}
    
    def _handle_decision_action(self, capsule: Dict[str, Any], action_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle decision capsule action.
        
        Args:
            capsule: Capsule data
            action_id: ID of the action
            data: Action data
            
        Returns:
            Response data
        """
        if action_id == "make_decision":
            # Get selected option
            selected_option = data.get("selected_option")
            
            if not selected_option:
                return {"error": "Missing selected option"}
            
            # Get decision maker
            decision_maker = data.get("decision_maker", "system")
            
            # Update decision info
            if "decision_info" not in capsule:
                capsule["decision_info"] = {}
            
            capsule["decision_info"]["decision_made"] = True
            capsule["decision_info"]["selected_option"] = selected_option
            capsule["decision_info"]["decision_maker"] = decision_maker
            capsule["decision_info"]["decided_at"] = datetime.utcnow().isoformat()
            
            # Update content
            if "content" not in capsule:
                capsule["content"] = {}
            
            capsule["content"]["status"] = "decided"
            
            # Update timestamp
            capsule["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Decision {capsule.get('decision_info', {}).get('decision_id', '')} made: {selected_option}")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "decision_id": capsule.get("decision_info", {}).get("decision_id", ""),
                "selected_option": selected_option,
                "decision_maker": decision_maker
            }
        elif action_id == "request_more_info":
            # Get source component
            source_id = capsule.get("source_id", "")
            
            # Request more info from source
            more_info = self.agent_core.request_decision_info(source_id, capsule.get("decision_info", {}).get("decision_id", ""))
            
            if not more_info:
                return {"error": f"Failed to get more info from {source_id}"}
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "decision_id": capsule.get("decision_info", {}).get("decision_id", ""),
                "more_info": more_info
            }
        
        logger.warning(f"Unknown decision action: {action_id}")
        return {"error": f"Unknown decision action: {action_id}"}
    
    def _handle_decision_component_click(self, capsule: Dict[str, Any], component_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle decision capsule component click.
        
        Args:
            capsule: Capsule data
            component_id: ID of the component
            data: Interaction data
            
        Returns:
            Response data
        """
        if component_id == "option_list":
            # Handle option selection
            option = data.get("option")
            
            if not option:
                return {"error": "Missing option"}
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "action": "select_option",
                "option": option
            }
        elif component_id == "impact_indicator":
            # Show impact details
            impact = capsule.get("decision_info", {}).get("impact", "medium")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "action": "show_impact_details",
                "impact": impact
            }
        elif component_id == "deadline":
            # Show deadline details
            deadline = capsule.get("decision_info", {}).get("deadline", "")
            
            return {
                "success": True,
                "capsule_id": capsule.get("capsule_id", ""),
                "action": "show_deadline_details",
                "deadline": deadline
            }
        
        logger.warning(f"Unknown decision component: {component_id}")
        return {"error": f"Unknown decision component: {component_id}"}
