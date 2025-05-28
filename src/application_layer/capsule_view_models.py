"""
Capsule View Models for Application Layer.

This module provides the view models for Dynamic Agent Capsules
in the Universal Skin UX concept.
"""

import logging
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CapsuleViewModels:
    """
    View models for Dynamic Agent Capsules.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the Capsule View Models.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        logger.info("Capsule View Models initialized")
    
    def get_capsule_view_model(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get view model for a capsule.
        
        Args:
            capsule: Capsule data
            
        Returns:
            Capsule view model
        """
        capsule_type = capsule.get("capsule_type", "status")
        
        # Get type-specific view model
        if capsule_type == "task":
            return self._get_task_capsule_view_model(capsule)
        elif capsule_type == "workflow":
            return self._get_workflow_capsule_view_model(capsule)
        elif capsule_type == "alert":
            return self._get_alert_capsule_view_model(capsule)
        elif capsule_type == "status":
            return self._get_status_capsule_view_model(capsule)
        elif capsule_type == "decision":
            return self._get_decision_capsule_view_model(capsule)
        else:
            return self._get_default_capsule_view_model(capsule)
    
    def _get_task_capsule_view_model(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get view model for a task capsule.
        
        Args:
            capsule: Capsule data
            
        Returns:
            Task capsule view model
        """
        # Get base view model
        view_model = self._get_base_capsule_view_model(capsule)
        
        # Add task-specific properties
        task_info = capsule.get("task_info", {})
        
        view_model["task"] = {
            "id": task_info.get("task_id", ""),
            "assignee": task_info.get("assignee", ""),
            "due_date": task_info.get("due_date", ""),
            "priority": task_info.get("priority", "medium"),
            "status": task_info.get("status", "pending"),
            "completion": task_info.get("completion", 0)
        }
        
        # Add task-specific UI components
        view_model["ui_components"].extend([
            {
                "type": "progress_bar",
                "value": task_info.get("completion", 0),
                "color": self._get_priority_color(task_info.get("priority", "medium"))
            },
            {
                "type": "assignee_avatar",
                "value": task_info.get("assignee", ""),
                "size": "small"
            },
            {
                "type": "due_date",
                "value": task_info.get("due_date", ""),
                "format": "relative"
            }
        ])
        
        # Add task-specific actions
        view_model["actions"].extend([
            {
                "id": "complete_task",
                "label": "Complete",
                "icon": "check",
                "enabled": task_info.get("status", "pending") != "completed"
            },
            {
                "id": "reassign_task",
                "label": "Reassign",
                "icon": "person_add",
                "enabled": True
            }
        ])
        
        return view_model
    
    def _get_workflow_capsule_view_model(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get view model for a workflow capsule.
        
        Args:
            capsule: Capsule data
            
        Returns:
            Workflow capsule view model
        """
        # Get base view model
        view_model = self._get_base_capsule_view_model(capsule)
        
        # Add workflow-specific properties
        workflow_info = capsule.get("workflow_info", {})
        
        view_model["workflow"] = {
            "id": workflow_info.get("workflow_id", ""),
            "current_step": workflow_info.get("current_step", 0),
            "total_steps": workflow_info.get("total_steps", 0),
            "step_status": workflow_info.get("step_status", []),
            "started_at": workflow_info.get("started_at", ""),
            "estimated_completion": workflow_info.get("estimated_completion", "")
        }
        
        # Calculate progress
        total_steps = workflow_info.get("total_steps", 0)
        current_step = workflow_info.get("current_step", 0)
        progress = 0
        if total_steps > 0:
            progress = (current_step / total_steps) * 100
        
        # Add workflow-specific UI components
        view_model["ui_components"].extend([
            {
                "type": "step_indicator",
                "current": current_step,
                "total": total_steps,
                "status": workflow_info.get("step_status", [])
            },
            {
                "type": "progress_bar",
                "value": progress,
                "color": "#34A853"  # Green
            },
            {
                "type": "time_estimate",
                "value": workflow_info.get("estimated_completion", ""),
                "format": "relative"
            }
        ])
        
        # Add workflow-specific actions
        view_model["actions"].extend([
            {
                "id": "pause_workflow",
                "label": "Pause",
                "icon": "pause",
                "enabled": True
            },
            {
                "id": "skip_step",
                "label": "Skip Step",
                "icon": "skip_next",
                "enabled": current_step < total_steps
            }
        ])
        
        return view_model
    
    def _get_alert_capsule_view_model(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get view model for an alert capsule.
        
        Args:
            capsule: Capsule data
            
        Returns:
            Alert capsule view model
        """
        # Get base view model
        view_model = self._get_base_capsule_view_model(capsule)
        
        # Add alert-specific properties
        alert_info = capsule.get("alert_info", {})
        
        view_model["alert"] = {
            "id": alert_info.get("alert_id", ""),
            "severity": alert_info.get("severity", "info"),
            "category": alert_info.get("category", "system"),
            "acknowledged": alert_info.get("acknowledged", False),
            "acknowledged_by": alert_info.get("acknowledged_by", ""),
            "acknowledged_at": alert_info.get("acknowledged_at", ""),
            "auto_dismiss": alert_info.get("auto_dismiss", False),
            "dismiss_after": alert_info.get("dismiss_after", 0)
        }
        
        # Add alert-specific UI components
        view_model["ui_components"].extend([
            {
                "type": "severity_indicator",
                "value": alert_info.get("severity", "info"),
                "color": self._get_severity_color(alert_info.get("severity", "info"))
            },
            {
                "type": "category_badge",
                "value": alert_info.get("category", "system"),
                "color": "#757575"  # Gray
            }
        ])
        
        # Add alert-specific actions
        view_model["actions"].extend([
            {
                "id": "acknowledge_alert",
                "label": "Acknowledge",
                "icon": "visibility",
                "enabled": not alert_info.get("acknowledged", False)
            },
            {
                "id": "dismiss_alert",
                "label": "Dismiss",
                "icon": "close",
                "enabled": True
            }
        ])
        
        return view_model
    
    def _get_status_capsule_view_model(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get view model for a status capsule.
        
        Args:
            capsule: Capsule data
            
        Returns:
            Status capsule view model
        """
        # Get base view model
        view_model = self._get_base_capsule_view_model(capsule)
        
        # Add status-specific properties
        status_info = capsule.get("status_info", {})
        
        view_model["status"] = {
            "id": status_info.get("status_id", ""),
            "category": status_info.get("category", "system"),
            "value": status_info.get("value", ""),
            "previous_value": status_info.get("previous_value", ""),
            "changed_at": status_info.get("changed_at", ""),
            "trend": status_info.get("trend", "stable"),
            "thresholds": status_info.get("thresholds", {})
        }
        
        # Add status-specific UI components
        view_model["ui_components"].extend([
            {
                "type": "status_indicator",
                "value": status_info.get("value", ""),
                "previous": status_info.get("previous_value", ""),
                "trend": status_info.get("trend", "stable"),
                "color": self._get_trend_color(status_info.get("trend", "stable"))
            },
            {
                "type": "category_badge",
                "value": status_info.get("category", "system"),
                "color": "#757575"  # Gray
            }
        ])
        
        # Add status-specific actions
        view_model["actions"].extend([
            {
                "id": "refresh_status",
                "label": "Refresh",
                "icon": "refresh",
                "enabled": True
            },
            {
                "id": "view_history",
                "label": "History",
                "icon": "history",
                "enabled": True
            }
        ])
        
        return view_model
    
    def _get_decision_capsule_view_model(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get view model for a decision capsule.
        
        Args:
            capsule: Capsule data
            
        Returns:
            Decision capsule view model
        """
        # Get base view model
        view_model = self._get_base_capsule_view_model(capsule)
        
        # Add decision-specific properties
        decision_info = capsule.get("decision_info", {})
        
        view_model["decision"] = {
            "id": decision_info.get("decision_id", ""),
            "options": decision_info.get("options", []),
            "recommended_option": decision_info.get("recommended_option", ""),
            "deadline": decision_info.get("deadline", ""),
            "impact": decision_info.get("impact", "medium"),
            "context": decision_info.get("context", ""),
            "decision_maker": decision_info.get("decision_maker", ""),
            "decision_made": decision_info.get("decision_made", False),
            "selected_option": decision_info.get("selected_option", ""),
            "decided_at": decision_info.get("decided_at", "")
        }
        
        # Add decision-specific UI components
        view_model["ui_components"].extend([
            {
                "type": "option_list",
                "options": decision_info.get("options", []),
                "recommended": decision_info.get("recommended_option", ""),
                "selected": decision_info.get("selected_option", "")
            },
            {
                "type": "impact_indicator",
                "value": decision_info.get("impact", "medium"),
                "color": self._get_impact_color(decision_info.get("impact", "medium"))
            },
            {
                "type": "deadline",
                "value": decision_info.get("deadline", ""),
                "format": "relative"
            }
        ])
        
        # Add decision-specific actions
        view_model["actions"].extend([
            {
                "id": "make_decision",
                "label": "Decide",
                "icon": "check_circle",
                "enabled": not decision_info.get("decision_made", False)
            },
            {
                "id": "request_more_info",
                "label": "More Info",
                "icon": "info",
                "enabled": True
            }
        ])
        
        return view_model
    
    def _get_default_capsule_view_model(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get default view model for a capsule.
        
        Args:
            capsule: Capsule data
            
        Returns:
            Default capsule view model
        """
        return self._get_base_capsule_view_model(capsule)
    
    def _get_base_capsule_view_model(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get base view model for a capsule.
        
        Args:
            capsule: Capsule data
            
        Returns:
            Base capsule view model
        """
        content = capsule.get("content", {})
        display = capsule.get("display", {})
        interaction = capsule.get("interaction", {})
        
        view_model = {
            "id": capsule.get("capsule_id", ""),
            "type": capsule.get("capsule_type", "status"),
            "source_id": capsule.get("source_id", ""),
            "created_at": capsule.get("created_at", ""),
            "updated_at": capsule.get("updated_at", ""),
            "state": capsule.get("state", "active"),
            "content": {
                "title": content.get("title", "Untitled Capsule"),
                "summary": content.get("summary", ""),
                "details": content.get("details", ""),
                "icon": content.get("icon", "circle"),
                "color": content.get("color", "#757575"),
                "progress": content.get("progress", 0),
                "status": content.get("status", "pending")
            },
            "display": {
                "size": display.get("size", "medium"),
                "expanded": display.get("expanded", False),
                "position": display.get("position", {"x": 0, "y": 0}),
                "priority": display.get("priority", 5),
                "animation": display.get("animation", "fade"),
                "theme": display.get("theme", "default")
            },
            "interaction": {
                "draggable": interaction.get("draggable", True),
                "resizable": interaction.get("resizable", True),
                "clickable": interaction.get("clickable", True),
                "expandable": interaction.get("expandable", True),
                "pinnable": interaction.get("pinnable", True)
            },
            "pinned": capsule.get("pin_info", {}).get("pinned", False),
            "pin_mode": capsule.get("pin_info", {}).get("pin_mode"),
            "pin_location": capsule.get("pin_info", {}).get("pin_location"),
            "ui_components": [],
            "actions": [
                {
                    "id": "expand_collapse",
                    "label": "Expand",
                    "icon": "expand_more",
                    "enabled": interaction.get("expandable", True)
                },
                {
                    "id": "pin_unpin",
                    "label": "Pin",
                    "icon": "push_pin",
                    "enabled": interaction.get("pinnable", True)
                }
            ],
            "links": content.get("links", []),
            "metrics": content.get("metrics", {})
        }
        
        return view_model
    
    def _get_priority_color(self, priority: str) -> str:
        """
        Get color for priority.
        
        Args:
            priority: Priority level
            
        Returns:
            Color for priority
        """
        colors = {
            "low": "#4285F4",  # Blue
            "medium": "#FBBC05",  # Yellow
            "high": "#EA4335",  # Red
            "critical": "#B31412"  # Dark Red
        }
        
        return colors.get(priority.lower(), "#757575")  # Gray default
    
    def _get_severity_color(self, severity: str) -> str:
        """
        Get color for severity.
        
        Args:
            severity: Severity level
            
        Returns:
            Color for severity
        """
        colors = {
            "info": "#4285F4",  # Blue
            "warning": "#FBBC05",  # Yellow
            "error": "#EA4335",  # Red
            "critical": "#B31412"  # Dark Red
        }
        
        return colors.get(severity.lower(), "#757575")  # Gray default
    
    def _get_trend_color(self, trend: str) -> str:
        """
        Get color for trend.
        
        Args:
            trend: Trend direction
            
        Returns:
            Color for trend
        """
        colors = {
            "up": "#34A853",  # Green
            "down": "#EA4335",  # Red
            "stable": "#4285F4",  # Blue
            "fluctuating": "#FBBC05"  # Yellow
        }
        
        return colors.get(trend.lower(), "#757575")  # Gray default
    
    def _get_impact_color(self, impact: str) -> str:
        """
        Get color for impact.
        
        Args:
            impact: Impact level
            
        Returns:
            Color for impact
        """
        colors = {
            "low": "#4285F4",  # Blue
            "medium": "#FBBC05",  # Yellow
            "high": "#EA4335",  # Red
            "critical": "#B31412"  # Dark Red
        }
        
        return colors.get(impact.lower(), "#757575")  # Gray default
