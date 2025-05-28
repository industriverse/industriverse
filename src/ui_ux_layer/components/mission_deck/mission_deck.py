"""
Mission Deck Component for the UI/UX Layer

This component provides a mission control interface for managing and monitoring
complex industrial operations and workflows. It integrates with the workflow
automation layer and provides a unified view of all active missions.

The Mission Deck:
1. Displays active missions and their status
2. Provides detailed mission information and progress tracking
3. Enables mission creation, modification, and termination
4. Integrates with workflow automation for mission execution
5. Supports role-based mission views and permissions
6. Provides real-time alerts and notifications for mission events

Author: Manus
"""

import logging
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta

# Local imports
from ..core.rendering_engine.rendering_engine import RenderingEngine
from ..core.context_engine.context_engine import ContextEngine
from ..core.agent_ecosystem.agent_interaction_protocol import AgentInteractionProtocol
from ..core.protocol_bridge.mcp_integration_manager import MCPIntegrationManager
from ..core.protocol_bridge.a2a_integration_manager import A2AIntegrationManager
from ..core.capsule_framework.capsule_manager import CapsuleManager

# Configure logging
logger = logging.getLogger(__name__)

class MissionDeck:
    """
    Mission Deck component for managing and monitoring industrial operations and workflows.
    """
    
    def __init__(
        self,
        rendering_engine: RenderingEngine,
        context_engine: ContextEngine,
        agent_protocol: AgentInteractionProtocol,
        mcp_manager: MCPIntegrationManager,
        a2a_manager: A2AIntegrationManager,
        capsule_manager: CapsuleManager,
        config: Dict = None
    ):
        """
        Initialize the Mission Deck.
        
        Args:
            rendering_engine: Rendering Engine instance
            context_engine: Context Engine instance
            agent_protocol: Agent Interaction Protocol instance
            mcp_manager: MCP Integration Manager instance
            a2a_manager: A2A Integration Manager instance
            capsule_manager: Capsule Manager instance
            config: Optional configuration dictionary
        """
        self.rendering_engine = rendering_engine
        self.context_engine = context_engine
        self.agent_protocol = agent_protocol
        self.mcp_manager = mcp_manager
        self.a2a_manager = a2a_manager
        self.capsule_manager = capsule_manager
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "max_active_missions": 50,
            "mission_history_limit": 100,
            "refresh_interval": 5,  # seconds
            "auto_refresh": True,
            "default_view": "active",
            "default_sort": "priority",
            "default_filter": {
                "status": [],
                "priority": [],
                "types": [],
                "tags": []
            },
            "enable_notifications": True,
            "notification_levels": ["critical", "warning", "info"],
            "enable_mission_templates": True,
            "enable_mission_scheduling": True,
            "enable_mission_dependencies": True,
            "enable_mission_automation": True,
            "enable_mission_analytics": True,
            "enable_mission_export": True,
            "enable_mission_sharing": True,
            "enable_mission_comments": True,
            "enable_mission_attachments": True,
            "enable_mission_versioning": True,
            "enable_mission_history": True,
            "enable_mission_timeline": True,
            "enable_mission_gantt": True,
            "enable_mission_kanban": True,
            "enable_mission_calendar": True,
            "enable_mission_map": True,
            "enable_mission_dashboard": True,
            "enable_mission_reports": True,
            "enable_mission_insights": True,
            "enable_mission_recommendations": True,
            "enable_mission_predictions": True,
            "enable_mission_optimization": True,
            "enable_mission_simulation": True,
            "enable_mission_digital_twin": True,
            "color_scheme": {
                "background": "#1E1E2E",
                "text": "#FFFFFF",
                "accent": "#4CAF50",
                "status": {
                    "not_started": "#9E9E9E",
                    "planning": "#2196F3",
                    "in_progress": "#FFC107",
                    "on_hold": "#FF9800",
                    "completed": "#4CAF50",
                    "failed": "#F44336",
                    "cancelled": "#9E9E9E"
                },
                "priority": {
                    "critical": "#F44336",
                    "high": "#FF9800",
                    "medium": "#FFC107",
                    "low": "#4CAF50",
                    "none": "#9E9E9E"
                }
            }
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Current state
        self.missions = {}
        self.mission_templates = {}
        self.mission_history = []
        self.current_view = self.config["default_view"]
        self.current_sort = self.config["default_sort"]
        self.current_filter = self.config["default_filter"].copy()
        self.selected_mission = None
        self.last_refresh_time = 0
        self.refresh_timer = None
        
        # Event handlers
        self.event_handlers = {
            "mission_added": [],
            "mission_updated": [],
            "mission_removed": [],
            "mission_selected": [],
            "mission_deselected": [],
            "view_changed": [],
            "sort_changed": [],
            "filter_changed": [],
            "refresh": [],
            "error": []
        }
        
        # Register with context engine
        self.context_engine.register_context_listener(self._handle_context_change)
        
        # Register with agent protocol for mission updates
        self.agent_protocol.register_message_handler(
            "mission_update",
            self._handle_mission_update,
            "*"
        )
        
        # Start auto-refresh if enabled
        if self.config["auto_refresh"]:
            self._start_auto_refresh()
        
        logger.info("Mission Deck initialized")
    
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
        
        # Handle mission filter context changes
        if context_type == "mission_filter":
            filter_data = event.get("data", {})
            self.set_filter(filter_data)
        
        # Handle mission selection context changes
        elif context_type == "mission_selection":
            selection_data = event.get("data", {})
            if "mission_id" in selection_data:
                self.select_mission(selection_data["mission_id"])
    
    def _handle_mission_update(self, message: Dict) -> None:
        """
        Handle mission update messages.
        
        Args:
            message: Mission update message
        """
        try:
            payload = message.get("payload", {})
            source_id = message.get("source", {}).get("id")
            source_type = message.get("source", {}).get("type")
            
            # Only process mission updates
            if source_type != "mission_manager" and source_type != "workflow_engine":
                return
            
            # Update or add mission
            mission_id = payload.get("id")
            if not mission_id:
                logger.warning("Mission update missing ID")
                return
            
            self._update_mission(mission_id, payload)
        except Exception as e:
            logger.error(f"Error handling mission update: {str(e)}")
    
    def _update_mission(self, mission_id: str, data: Dict) -> None:
        """
        Update or add a mission.
        
        Args:
            mission_id: Mission identifier
            data: Mission data
        """
        # Check if mission exists
        is_new = mission_id not in self.missions
        
        # Get current time
        current_time = time.time()
        
        if is_new:
            # Create new mission
            mission = {
                "id": mission_id,
                "name": data.get("name", f"Mission {mission_id}"),
                "description": data.get("description", ""),
                "type": data.get("type", "standard"),
                "status": data.get("status", "not_started"),
                "priority": data.get("priority", "medium"),
                "progress": data.get("progress", 0),
                "start_time": data.get("start_time", current_time),
                "end_time": data.get("end_time"),
                "estimated_duration": data.get("estimated_duration"),
                "actual_duration": data.get("actual_duration"),
                "owner": data.get("owner", {
                    "id": "system",
                    "name": "System",
                    "type": "system"
                }),
                "assignees": data.get("assignees", []),
                "tags": data.get("tags", []),
                "workflows": data.get("workflows", []),
                "dependencies": data.get("dependencies", []),
                "resources": data.get("resources", []),
                "metrics": data.get("metrics", {}),
                "alerts": data.get("alerts", []),
                "comments": data.get("comments", []),
                "attachments": data.get("attachments", []),
                "history": data.get("history", []),
                "created_at": data.get("created_at", current_time),
                "updated_at": current_time,
                "metadata": data.get("metadata", {})
            }
            
            # Add to missions dictionary
            self.missions[mission_id] = mission
            
            # Add to history if completed or failed
            if mission["status"] in ["completed", "failed", "cancelled"]:
                self._add_to_history(mission)
            
            # Trigger mission added event
            self._trigger_event("mission_added", {
                "mission_id": mission_id,
                "mission": mission
            })
            
            # Create mission capsule
            self._create_mission_capsule(mission_id)
            
            # Send notification if enabled
            if self.config["enable_notifications"]:
                self._send_notification(
                    "info",
                    f"New mission created: {mission['name']}",
                    {
                        "mission_id": mission_id,
                        "mission_name": mission["name"],
                        "mission_type": mission["type"],
                        "mission_status": mission["status"],
                        "mission_priority": mission["priority"]
                    }
                )
        else:
            # Update existing mission
            mission = self.missions[mission_id]
            old_status = mission["status"]
            
            # Update properties
            if "name" in data:
                mission["name"] = data["name"]
            
            if "description" in data:
                mission["description"] = data["description"]
            
            if "type" in data:
                mission["type"] = data["type"]
            
            if "status" in data:
                mission["status"] = data["status"]
            
            if "priority" in data:
                mission["priority"] = data["priority"]
            
            if "progress" in data:
                mission["progress"] = data["progress"]
            
            if "start_time" in data:
                mission["start_time"] = data["start_time"]
            
            if "end_time" in data:
                mission["end_time"] = data["end_time"]
            
            if "estimated_duration" in data:
                mission["estimated_duration"] = data["estimated_duration"]
            
            if "actual_duration" in data:
                mission["actual_duration"] = data["actual_duration"]
            
            if "owner" in data:
                mission["owner"] = data["owner"]
            
            if "assignees" in data:
                mission["assignees"] = data["assignees"]
            
            if "tags" in data:
                mission["tags"] = data["tags"]
            
            if "workflows" in data:
                mission["workflows"] = data["workflows"]
            
            if "dependencies" in data:
                mission["dependencies"] = data["dependencies"]
            
            if "resources" in data:
                mission["resources"] = data["resources"]
            
            if "metrics" in data:
                mission["metrics"] = {**mission.get("metrics", {}), **data["metrics"]}
            
            if "alerts" in data:
                mission["alerts"] = data["alerts"]
            
            if "comments" in data:
                mission["comments"] = data["comments"]
            
            if "attachments" in data:
                mission["attachments"] = data["attachments"]
            
            if "history" in data:
                mission["history"] = data["history"]
            
            if "metadata" in data:
                mission["metadata"] = {**mission.get("metadata", {}), **data["metadata"]}
            
            # Update timestamp
            mission["updated_at"] = current_time
            
            # Add to history if status changed to completed or failed
            if old_status != mission["status"] and mission["status"] in ["completed", "failed", "cancelled"]:
                self._add_to_history(mission)
            
            # Trigger mission updated event
            self._trigger_event("mission_updated", {
                "mission_id": mission_id,
                "mission": mission,
                "updates": data
            })
            
            # Update mission capsule
            self._update_mission_capsule(mission_id)
            
            # Send notification if status changed
            if self.config["enable_notifications"] and old_status != mission["status"]:
                notification_level = "info"
                if mission["status"] == "failed":
                    notification_level = "critical"
                elif mission["status"] == "on_hold":
                    notification_level = "warning"
                
                self._send_notification(
                    notification_level,
                    f"Mission status changed: {mission['name']} is now {mission['status']}",
                    {
                        "mission_id": mission_id,
                        "mission_name": mission["name"],
                        "mission_type": mission["type"],
                        "mission_status": mission["status"],
                        "mission_priority": mission["priority"],
                        "old_status": old_status
                    }
                )
    
    def _add_to_history(self, mission: Dict) -> None:
        """
        Add a mission to the history.
        
        Args:
            mission: Mission data
        """
        # Create history entry
        history_entry = {
            "id": mission["id"],
            "name": mission["name"],
            "type": mission["type"],
            "status": mission["status"],
            "priority": mission["priority"],
            "progress": mission["progress"],
            "start_time": mission["start_time"],
            "end_time": mission["end_time"] or time.time(),
            "owner": mission["owner"],
            "created_at": mission["created_at"],
            "completed_at": time.time()
        }
        
        # Add to history
        self.mission_history.append(history_entry)
        
        # Limit history size
        if len(self.mission_history) > self.config["mission_history_limit"]:
            self.mission_history = self.mission_history[-self.config["mission_history_limit"]:]
    
    def _create_mission_capsule(self, mission_id: str) -> None:
        """
        Create a capsule for a mission.
        
        Args:
            mission_id: Mission identifier
        """
        # Check if mission exists
        if mission_id not in self.missions:
            return
        
        # Check if capsule already exists
        capsule_id = f"mission_{mission_id}"
        if self.capsule_manager.has_capsule(capsule_id):
            # Just update the existing capsule
            self._update_mission_capsule(mission_id)
            return
        
        # Get mission data
        mission = self.missions[mission_id]
        
        # Create capsule data
        capsule_data = {
            "id": capsule_id,
            "type": "mission",
            "title": mission["name"],
            "description": mission["description"],
            "icon": "flag",
            "color": self._get_mission_color(mission),
            "source": {
                "type": "mission",
                "id": mission_id
            },
            "actions": [
                {
                    "id": "view",
                    "label": "View",
                    "icon": "eye"
                },
                {
                    "id": "edit",
                    "label": "Edit",
                    "icon": "edit"
                },
                {
                    "id": "pause",
                    "label": "Pause",
                    "icon": "pause",
                    "condition": "status == 'in_progress'"
                },
                {
                    "id": "resume",
                    "label": "Resume",
                    "icon": "play",
                    "condition": "status == 'on_hold'"
                },
                {
                    "id": "cancel",
                    "label": "Cancel",
                    "icon": "times",
                    "condition": "status != 'completed' && status != 'cancelled' && status != 'failed'"
                }
            ],
            "properties": {
                "type": mission["type"],
                "status": mission["status"],
                "priority": mission["priority"],
                "progress": mission["progress"],
                "start_time": mission["start_time"],
                "end_time": mission["end_time"],
                "owner": mission["owner"],
                "tags": mission["tags"]
            }
        }
        
        # Create the capsule
        self.capsule_manager.create_capsule(capsule_data)
    
    def _update_mission_capsule(self, mission_id: str) -> None:
        """
        Update a mission capsule.
        
        Args:
            mission_id: Mission identifier
        """
        # Check if mission exists
        if mission_id not in self.missions:
            return
        
        # Check if capsule exists
        capsule_id = f"mission_{mission_id}"
        if not self.capsule_manager.has_capsule(capsule_id):
            # Create the capsule if it doesn't exist
            self._create_mission_capsule(mission_id)
            return
        
        # Get mission data
        mission = self.missions[mission_id]
        
        # Update capsule data
        capsule_data = {
            "title": mission["name"],
            "description": mission["description"],
            "color": self._get_mission_color(mission),
            "properties": {
                "type": mission["type"],
                "status": mission["status"],
                "priority": mission["priority"],
                "progress": mission["progress"],
                "start_time": mission["start_time"],
                "end_time": mission["end_time"],
                "owner": mission["owner"],
                "tags": mission["tags"]
            }
        }
        
        # Update the capsule
        self.capsule_manager.update_capsule(capsule_id, capsule_data)
    
    def _get_mission_color(self, mission: Dict) -> str:
        """
        Get the color for a mission based on its status and priority.
        
        Args:
            mission: Mission data
            
        Returns:
            Color string
        """
        status = mission["status"]
        priority = mission["priority"]
        
        # Use status color
        if status in self.config["color_scheme"]["status"]:
            return self.config["color_scheme"]["status"][status]
        
        # Fallback to priority color
        if priority in self.config["color_scheme"]["priority"]:
            return self.config["color_scheme"]["priority"][priority]
        
        # Default color
        return self.config["color_scheme"]["accent"]
    
    def _send_notification(self, level: str, message: str, data: Dict = None) -> None:
        """
        Send a notification.
        
        Args:
            level: Notification level (critical, warning, info)
            message: Notification message
            data: Optional notification data
        """
        # Skip if notifications are disabled or level is not enabled
        if not self.config["enable_notifications"] or level not in self.config["notification_levels"]:
            return
        
        # Create notification
        notification = {
            "id": str(uuid.uuid4()),
            "level": level,
            "message": message,
            "data": data or {},
            "timestamp": time.time(),
            "source": "mission_deck"
        }
        
        # Send to context engine
        self.context_engine.publish_context_update({
            "type": "notification",
            "data": notification
        })
    
    def _start_auto_refresh(self) -> None:
        """Start auto-refresh timer."""
        # In a real implementation, this would use a timer or scheduler
        # For this example, we'll rely on periodic update calls
        pass
    
    def _stop_auto_refresh(self) -> None:
        """Stop auto-refresh timer."""
        # In a real implementation, this would cancel the timer or scheduler
        pass
    
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
    
    def refresh(self) -> None:
        """Refresh mission data."""
        try:
            logger.info("Refreshing mission data")
            
            # Update last refresh time
            self.last_refresh_time = time.time()
            
            # Request mission data from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "get_missions",
                    "filter": self.current_filter
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error refreshing missions: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to refresh missions: {response.get('error_message', 'Unknown error')}"
                })
                return
            
            # Process mission data
            missions_data = response.get("payload", {}).get("missions", [])
            for mission_data in missions_data:
                mission_id = mission_data.get("id")
                if mission_id:
                    self._update_mission(mission_id, mission_data)
            
            # Trigger refresh event
            self._trigger_event("refresh", {
                "timestamp": self.last_refresh_time
            })
        except Exception as e:
            logger.error(f"Error refreshing missions: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to refresh missions: {str(e)}"
            })
    
    def set_view(self, view: str) -> None:
        """
        Set the current view.
        
        Args:
            view: View name
        """
        try:
            logger.info(f"Setting view: {view}")
            
            # Update current view
            self.current_view = view
            
            # Trigger view changed event
            self._trigger_event("view_changed", {
                "view": view
            })
        except Exception as e:
            logger.error(f"Error setting view: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to set view: {str(e)}"
            })
    
    def set_sort(self, sort: str) -> None:
        """
        Set the current sort.
        
        Args:
            sort: Sort field
        """
        try:
            logger.info(f"Setting sort: {sort}")
            
            # Update current sort
            self.current_sort = sort
            
            # Trigger sort changed event
            self._trigger_event("sort_changed", {
                "sort": sort
            })
        except Exception as e:
            logger.error(f"Error setting sort: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to set sort: {str(e)}"
            })
    
    def set_filter(self, filter_data: Dict) -> None:
        """
        Set the mission filter.
        
        Args:
            filter_data: Filter configuration
        """
        try:
            logger.info(f"Setting mission filter: {filter_data}")
            
            # Update current filter
            self.current_filter = {
                **self.config["default_filter"],
                **filter_data
            }
            
            # Trigger filter changed event
            self._trigger_event("filter_changed", {
                "filter": self.current_filter
            })
            
            # Refresh missions with new filter
            self.refresh()
        except Exception as e:
            logger.error(f"Error setting filter: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to set filter: {str(e)}"
            })
    
    def get_filter(self) -> Dict:
        """
        Get the current mission filter.
        
        Returns:
            Current filter configuration
        """
        return self.current_filter.copy()
    
    def select_mission(self, mission_id: str) -> bool:
        """
        Select a mission.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            logger.info(f"Selecting mission: {mission_id}")
            
            # Update selected mission
            self.selected_mission = mission_id
            
            # Trigger mission selected event
            self._trigger_event("mission_selected", {
                "mission_id": mission_id,
                "mission": self.missions[mission_id]
            })
            
            # Focus mission capsule
            capsule_id = f"mission_{mission_id}"
            if self.capsule_manager.has_capsule(capsule_id):
                self.capsule_manager.focus_capsule(capsule_id)
            
            return True
        except Exception as e:
            logger.error(f"Error selecting mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to select mission: {str(e)}",
                "mission_id": mission_id
            })
            return False
    
    def deselect_mission(self) -> None:
        """Deselect the current mission."""
        try:
            if not self.selected_mission:
                return
            
            logger.info(f"Deselecting mission: {self.selected_mission}")
            
            # Get mission before clearing selection
            mission_id = self.selected_mission
            mission = self.missions.get(mission_id)
            
            # Clear selected mission
            self.selected_mission = None
            
            # Trigger mission deselected event
            self._trigger_event("mission_deselected", {
                "mission_id": mission_id,
                "mission": mission
            })
        except Exception as e:
            logger.error(f"Error deselecting mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to deselect mission: {str(e)}"
            })
    
    def get_mission(self, mission_id: str) -> Optional[Dict]:
        """
        Get a mission by ID.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Mission data or None if not found
        """
        return self.missions.get(mission_id)
    
    def get_missions(self, view: str = None, sort: str = None, filter_data: Dict = None) -> List[Dict]:
        """
        Get missions based on view, sort, and filter.
        
        Args:
            view: Optional view name (defaults to current view)
            sort: Optional sort field (defaults to current sort)
            filter_data: Optional filter data (defaults to current filter)
            
        Returns:
            List of mission data
        """
        try:
            # Use current values if not provided
            view = view or self.current_view
            sort = sort or self.current_sort
            filter_data = filter_data or self.current_filter
            
            # Get all missions
            missions = list(self.missions.values())
            
            # Apply view filter
            if view == "active":
                missions = [m for m in missions if m["status"] not in ["completed", "cancelled", "failed"]]
            elif view == "completed":
                missions = [m for m in missions if m["status"] == "completed"]
            elif view == "failed":
                missions = [m for m in missions if m["status"] == "failed"]
            elif view == "cancelled":
                missions = [m for m in missions if m["status"] == "cancelled"]
            elif view == "in_progress":
                missions = [m for m in missions if m["status"] == "in_progress"]
            elif view == "on_hold":
                missions = [m for m in missions if m["status"] == "on_hold"]
            elif view == "not_started":
                missions = [m for m in missions if m["status"] == "not_started"]
            elif view == "planning":
                missions = [m for m in missions if m["status"] == "planning"]
            
            # Apply custom filter
            if filter_data:
                # Filter by status
                if filter_data.get("status"):
                    missions = [m for m in missions if m["status"] in filter_data["status"]]
                
                # Filter by priority
                if filter_data.get("priority"):
                    missions = [m for m in missions if m["priority"] in filter_data["priority"]]
                
                # Filter by type
                if filter_data.get("types"):
                    missions = [m for m in missions if m["type"] in filter_data["types"]]
                
                # Filter by tags
                if filter_data.get("tags"):
                    missions = [m for m in missions if any(tag in m["tags"] for tag in filter_data["tags"])]
            
            # Apply sort
            if sort == "name":
                missions.sort(key=lambda m: m["name"])
            elif sort == "priority":
                # Sort by priority (critical > high > medium > low > none)
                priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "none": 4}
                missions.sort(key=lambda m: priority_order.get(m["priority"], 5))
            elif sort == "status":
                # Sort by status (in_progress > planning > not_started > on_hold > completed > failed > cancelled)
                status_order = {
                    "in_progress": 0,
                    "planning": 1,
                    "not_started": 2,
                    "on_hold": 3,
                    "completed": 4,
                    "failed": 5,
                    "cancelled": 6
                }
                missions.sort(key=lambda m: status_order.get(m["status"], 7))
            elif sort == "progress":
                missions.sort(key=lambda m: m["progress"])
            elif sort == "start_time":
                missions.sort(key=lambda m: m["start_time"] or 0)
            elif sort == "end_time":
                missions.sort(key=lambda m: m["end_time"] or float('inf'))
            elif sort == "created_at":
                missions.sort(key=lambda m: m["created_at"])
            elif sort == "updated_at":
                missions.sort(key=lambda m: m["updated_at"])
            
            return missions
        except Exception as e:
            logger.error(f"Error getting missions: {str(e)}")
            return []
    
    def get_mission_history(self) -> List[Dict]:
        """
        Get mission history.
        
        Returns:
            List of mission history entries
        """
        return self.mission_history.copy()
    
    def create_mission(self, mission_data: Dict) -> Optional[str]:
        """
        Create a new mission.
        
        Args:
            mission_data: Mission data
            
        Returns:
            Mission ID or None if creation failed
        """
        try:
            logger.info(f"Creating mission: {mission_data.get('name', 'Unnamed')}")
            
            # Generate mission ID if not provided
            if "id" not in mission_data:
                mission_data["id"] = str(uuid.uuid4())
            
            # Set creation time if not provided
            if "created_at" not in mission_data:
                mission_data["created_at"] = time.time()
            
            # Send create request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "create_mission",
                    "mission": mission_data
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error creating mission: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to create mission: {response.get('error_message', 'Unknown error')}"
                })
                return None
            
            # Get mission ID from response
            mission_id = response.get("payload", {}).get("mission_id", mission_data["id"])
            
            # Update local mission data
            self._update_mission(mission_id, mission_data)
            
            return mission_id
        except Exception as e:
            logger.error(f"Error creating mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to create mission: {str(e)}"
            })
            return None
    
    def update_mission(self, mission_id: str, updates: Dict) -> bool:
        """
        Update a mission.
        
        Args:
            mission_id: Mission identifier
            updates: Mission updates
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            logger.info(f"Updating mission: {mission_id}")
            
            # Send update request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "update_mission",
                    "mission_id": mission_id,
                    "updates": updates
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error updating mission: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to update mission: {response.get('error_message', 'Unknown error')}"
                })
                return False
            
            # Update local mission data
            self._update_mission(mission_id, updates)
            
            return True
        except Exception as e:
            logger.error(f"Error updating mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to update mission: {str(e)}"
            })
            return False
    
    def delete_mission(self, mission_id: str) -> bool:
        """
        Delete a mission.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            logger.info(f"Deleting mission: {mission_id}")
            
            # Send delete request to backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "delete_mission",
                    "mission_id": mission_id
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error deleting mission: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to delete mission: {response.get('error_message', 'Unknown error')}"
                })
                return False
            
            # Remove mission capsule
            capsule_id = f"mission_{mission_id}"
            if self.capsule_manager.has_capsule(capsule_id):
                self.capsule_manager.remove_capsule(capsule_id)
            
            # Remove from missions dictionary
            mission = self.missions.pop(mission_id)
            
            # Add to history
            self._add_to_history(mission)
            
            # Clear selection if this mission was selected
            if self.selected_mission == mission_id:
                self.deselect_mission()
            
            # Trigger mission removed event
            self._trigger_event("mission_removed", {
                "mission_id": mission_id,
                "mission": mission
            })
            
            return True
        except Exception as e:
            logger.error(f"Error deleting mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to delete mission: {str(e)}"
            })
            return False
    
    def start_mission(self, mission_id: str) -> bool:
        """
        Start a mission.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            mission = self.missions[mission_id]
            
            # Check if mission can be started
            if mission["status"] not in ["not_started", "planning", "on_hold"]:
                logger.warning(f"Cannot start mission with status {mission['status']}")
                return False
            
            logger.info(f"Starting mission: {mission_id}")
            
            # Update mission status
            return self.update_mission(mission_id, {
                "status": "in_progress",
                "start_time": time.time()
            })
        except Exception as e:
            logger.error(f"Error starting mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to start mission: {str(e)}"
            })
            return False
    
    def pause_mission(self, mission_id: str) -> bool:
        """
        Pause a mission.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            mission = self.missions[mission_id]
            
            # Check if mission can be paused
            if mission["status"] != "in_progress":
                logger.warning(f"Cannot pause mission with status {mission['status']}")
                return False
            
            logger.info(f"Pausing mission: {mission_id}")
            
            # Update mission status
            return self.update_mission(mission_id, {
                "status": "on_hold"
            })
        except Exception as e:
            logger.error(f"Error pausing mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to pause mission: {str(e)}"
            })
            return False
    
    def resume_mission(self, mission_id: str) -> bool:
        """
        Resume a paused mission.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            mission = self.missions[mission_id]
            
            # Check if mission can be resumed
            if mission["status"] != "on_hold":
                logger.warning(f"Cannot resume mission with status {mission['status']}")
                return False
            
            logger.info(f"Resuming mission: {mission_id}")
            
            # Update mission status
            return self.update_mission(mission_id, {
                "status": "in_progress"
            })
        except Exception as e:
            logger.error(f"Error resuming mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to resume mission: {str(e)}"
            })
            return False
    
    def complete_mission(self, mission_id: str) -> bool:
        """
        Mark a mission as completed.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            mission = self.missions[mission_id]
            
            # Check if mission can be completed
            if mission["status"] in ["completed", "failed", "cancelled"]:
                logger.warning(f"Cannot complete mission with status {mission['status']}")
                return False
            
            logger.info(f"Completing mission: {mission_id}")
            
            # Calculate actual duration if not set
            actual_duration = mission.get("actual_duration")
            if not actual_duration and mission.get("start_time"):
                actual_duration = time.time() - mission["start_time"]
            
            # Update mission status
            return self.update_mission(mission_id, {
                "status": "completed",
                "progress": 100,
                "end_time": time.time(),
                "actual_duration": actual_duration
            })
        except Exception as e:
            logger.error(f"Error completing mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to complete mission: {str(e)}"
            })
            return False
    
    def fail_mission(self, mission_id: str, reason: str = None) -> bool:
        """
        Mark a mission as failed.
        
        Args:
            mission_id: Mission identifier
            reason: Optional failure reason
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            mission = self.missions[mission_id]
            
            # Check if mission can be failed
            if mission["status"] in ["completed", "failed", "cancelled"]:
                logger.warning(f"Cannot fail mission with status {mission['status']}")
                return False
            
            logger.info(f"Failing mission: {mission_id}")
            
            # Calculate actual duration if not set
            actual_duration = mission.get("actual_duration")
            if not actual_duration and mission.get("start_time"):
                actual_duration = time.time() - mission["start_time"]
            
            # Update mission status
            updates = {
                "status": "failed",
                "end_time": time.time(),
                "actual_duration": actual_duration
            }
            
            if reason:
                updates["metadata"] = {
                    "failure_reason": reason
                }
            
            return self.update_mission(mission_id, updates)
        except Exception as e:
            logger.error(f"Error failing mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to fail mission: {str(e)}"
            })
            return False
    
    def cancel_mission(self, mission_id: str, reason: str = None) -> bool:
        """
        Cancel a mission.
        
        Args:
            mission_id: Mission identifier
            reason: Optional cancellation reason
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            mission = self.missions[mission_id]
            
            # Check if mission can be cancelled
            if mission["status"] in ["completed", "failed", "cancelled"]:
                logger.warning(f"Cannot cancel mission with status {mission['status']}")
                return False
            
            logger.info(f"Cancelling mission: {mission_id}")
            
            # Calculate actual duration if not set
            actual_duration = mission.get("actual_duration")
            if not actual_duration and mission.get("start_time"):
                actual_duration = time.time() - mission["start_time"]
            
            # Update mission status
            updates = {
                "status": "cancelled",
                "end_time": time.time(),
                "actual_duration": actual_duration
            }
            
            if reason:
                updates["metadata"] = {
                    "cancellation_reason": reason
                }
            
            return self.update_mission(mission_id, updates)
        except Exception as e:
            logger.error(f"Error cancelling mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to cancel mission: {str(e)}"
            })
            return False
    
    def add_mission_comment(self, mission_id: str, comment: str, user: Dict = None) -> bool:
        """
        Add a comment to a mission.
        
        Args:
            mission_id: Mission identifier
            comment: Comment text
            user: Optional user data
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            if not self.config["enable_mission_comments"]:
                logger.warning("Mission comments are disabled")
                return False
            
            logger.info(f"Adding comment to mission: {mission_id}")
            
            # Get mission
            mission = self.missions[mission_id]
            
            # Create comment
            comment_data = {
                "id": str(uuid.uuid4()),
                "text": comment,
                "user": user or {
                    "id": "system",
                    "name": "System",
                    "type": "system"
                },
                "timestamp": time.time()
            }
            
            # Add to comments
            comments = mission.get("comments", [])
            comments.append(comment_data)
            
            # Update mission
            return self.update_mission(mission_id, {
                "comments": comments
            })
        except Exception as e:
            logger.error(f"Error adding mission comment: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to add mission comment: {str(e)}"
            })
            return False
    
    def add_mission_attachment(self, mission_id: str, attachment: Dict) -> bool:
        """
        Add an attachment to a mission.
        
        Args:
            mission_id: Mission identifier
            attachment: Attachment data
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            if not self.config["enable_mission_attachments"]:
                logger.warning("Mission attachments are disabled")
                return False
            
            logger.info(f"Adding attachment to mission: {mission_id}")
            
            # Get mission
            mission = self.missions[mission_id]
            
            # Create attachment if not provided
            if "id" not in attachment:
                attachment["id"] = str(uuid.uuid4())
            
            if "timestamp" not in attachment:
                attachment["timestamp"] = time.time()
            
            # Add to attachments
            attachments = mission.get("attachments", [])
            attachments.append(attachment)
            
            # Update mission
            return self.update_mission(mission_id, {
                "attachments": attachments
            })
        except Exception as e:
            logger.error(f"Error adding mission attachment: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to add mission attachment: {str(e)}"
            })
            return False
    
    def get_mission_templates(self) -> List[Dict]:
        """
        Get mission templates.
        
        Returns:
            List of mission templates
        """
        try:
            if not self.config["enable_mission_templates"]:
                logger.warning("Mission templates are disabled")
                return []
            
            # Request templates from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "get_mission_templates"
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error getting mission templates: {response.get('error_message', 'Unknown error')}")
                return []
            
            # Get templates from response
            templates = response.get("payload", {}).get("templates", [])
            
            # Update local templates
            self.mission_templates = {template["id"]: template for template in templates}
            
            return templates
        except Exception as e:
            logger.error(f"Error getting mission templates: {str(e)}")
            return []
    
    def create_mission_from_template(self, template_id: str, mission_data: Dict = None) -> Optional[str]:
        """
        Create a mission from a template.
        
        Args:
            template_id: Template identifier
            mission_data: Optional additional mission data
            
        Returns:
            Mission ID or None if creation failed
        """
        try:
            if not self.config["enable_mission_templates"]:
                logger.warning("Mission templates are disabled")
                return None
            
            logger.info(f"Creating mission from template: {template_id}")
            
            # Request template-based mission creation from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "create_mission_from_template",
                    "template_id": template_id,
                    "mission_data": mission_data or {}
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error creating mission from template: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to create mission from template: {response.get('error_message', 'Unknown error')}"
                })
                return None
            
            # Get mission ID from response
            mission_id = response.get("payload", {}).get("mission_id")
            
            # Refresh to get the new mission
            self.refresh()
            
            return mission_id
        except Exception as e:
            logger.error(f"Error creating mission from template: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to create mission from template: {str(e)}"
            })
            return None
    
    def get_mission_analytics(self, mission_id: str = None, filter_data: Dict = None) -> Dict:
        """
        Get mission analytics.
        
        Args:
            mission_id: Optional mission identifier for specific mission analytics
            filter_data: Optional filter for aggregated analytics
            
        Returns:
            Analytics data
        """
        try:
            if not self.config["enable_mission_analytics"]:
                logger.warning("Mission analytics are disabled")
                return {}
            
            logger.info("Getting mission analytics")
            
            # Request analytics from backend
            request_data = {
                "request_type": "get_mission_analytics"
            }
            
            if mission_id:
                request_data["mission_id"] = mission_id
            
            if filter_data:
                request_data["filter"] = filter_data
            
            response = self.agent_protocol.send_request_sync(
                request_data,
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error getting mission analytics: {response.get('error_message', 'Unknown error')}")
                return {}
            
            # Get analytics from response
            analytics = response.get("payload", {}).get("analytics", {})
            
            return analytics
        except Exception as e:
            logger.error(f"Error getting mission analytics: {str(e)}")
            return {}
    
    def export_mission_data(self, mission_id: str = None, format: str = "json") -> Optional[str]:
        """
        Export mission data.
        
        Args:
            mission_id: Optional mission identifier for specific mission export
            format: Export format (json, csv, etc.)
            
        Returns:
            Export data or None if export failed
        """
        try:
            if not self.config["enable_mission_export"]:
                logger.warning("Mission export is disabled")
                return None
            
            logger.info(f"Exporting mission data: {mission_id or 'all'}")
            
            # Request export from backend
            request_data = {
                "request_type": "export_mission_data",
                "format": format
            }
            
            if mission_id:
                request_data["mission_id"] = mission_id
            
            response = self.agent_protocol.send_request_sync(
                request_data,
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error exporting mission data: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to export mission data: {response.get('error_message', 'Unknown error')}"
                })
                return None
            
            # Get export data from response
            export_data = response.get("payload", {}).get("export_data")
            
            return export_data
        except Exception as e:
            logger.error(f"Error exporting mission data: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to export mission data: {str(e)}"
            })
            return None
    
    def simulate_mission(self, mission_data: Dict) -> Dict:
        """
        Simulate a mission without creating it.
        
        Args:
            mission_data: Mission data
            
        Returns:
            Simulation results
        """
        try:
            if not self.config["enable_mission_simulation"]:
                logger.warning("Mission simulation is disabled")
                return {}
            
            logger.info("Simulating mission")
            
            # Request simulation from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "simulate_mission",
                    "mission": mission_data
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error simulating mission: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to simulate mission: {response.get('error_message', 'Unknown error')}"
                })
                return {}
            
            # Get simulation results from response
            simulation_results = response.get("payload", {}).get("simulation_results", {})
            
            return simulation_results
        except Exception as e:
            logger.error(f"Error simulating mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to simulate mission: {str(e)}"
            })
            return {}
    
    def optimize_mission(self, mission_id: str, optimization_params: Dict = None) -> bool:
        """
        Optimize a mission.
        
        Args:
            mission_id: Mission identifier
            optimization_params: Optional optimization parameters
            
        Returns:
            Boolean indicating success
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return False
            
            if not self.config["enable_mission_optimization"]:
                logger.warning("Mission optimization is disabled")
                return False
            
            logger.info(f"Optimizing mission: {mission_id}")
            
            # Request optimization from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "optimize_mission",
                    "mission_id": mission_id,
                    "optimization_params": optimization_params or {}
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error optimizing mission: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to optimize mission: {response.get('error_message', 'Unknown error')}"
                })
                return False
            
            # Get optimization results from response
            optimization_results = response.get("payload", {}).get("optimization_results", {})
            
            # Update mission with optimization results
            if "updates" in optimization_results:
                return self.update_mission(mission_id, optimization_results["updates"])
            
            return True
        except Exception as e:
            logger.error(f"Error optimizing mission: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to optimize mission: {str(e)}"
            })
            return False
    
    def get_mission_recommendations(self, mission_id: str = None) -> List[Dict]:
        """
        Get mission recommendations.
        
        Args:
            mission_id: Optional mission identifier for specific recommendations
            
        Returns:
            List of recommendations
        """
        try:
            if not self.config["enable_mission_recommendations"]:
                logger.warning("Mission recommendations are disabled")
                return []
            
            logger.info(f"Getting mission recommendations: {mission_id or 'all'}")
            
            # Request recommendations from backend
            request_data = {
                "request_type": "get_mission_recommendations"
            }
            
            if mission_id:
                request_data["mission_id"] = mission_id
            
            response = self.agent_protocol.send_request_sync(
                request_data,
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error getting mission recommendations: {response.get('error_message', 'Unknown error')}")
                return []
            
            # Get recommendations from response
            recommendations = response.get("payload", {}).get("recommendations", [])
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting mission recommendations: {str(e)}")
            return []
    
    def get_mission_predictions(self, mission_id: str) -> Dict:
        """
        Get mission predictions.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Prediction data
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return {}
            
            if not self.config["enable_mission_predictions"]:
                logger.warning("Mission predictions are disabled")
                return {}
            
            logger.info(f"Getting mission predictions: {mission_id}")
            
            # Request predictions from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "get_mission_predictions",
                    "mission_id": mission_id
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error getting mission predictions: {response.get('error_message', 'Unknown error')}")
                return {}
            
            # Get predictions from response
            predictions = response.get("payload", {}).get("predictions", {})
            
            return predictions
        except Exception as e:
            logger.error(f"Error getting mission predictions: {str(e)}")
            return {}
    
    def get_mission_digital_twin(self, mission_id: str) -> Dict:
        """
        Get mission digital twin.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Digital twin data
        """
        try:
            if mission_id not in self.missions:
                logger.warning(f"Mission not found: {mission_id}")
                return {}
            
            if not self.config["enable_mission_digital_twin"]:
                logger.warning("Mission digital twin is disabled")
                return {}
            
            logger.info(f"Getting mission digital twin: {mission_id}")
            
            # Request digital twin from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "get_mission_digital_twin",
                    "mission_id": mission_id
                },
                {
                    "type": "agent",
                    "id": "mission_manager",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error getting mission digital twin: {response.get('error_message', 'Unknown error')}")
                return {}
            
            # Get digital twin from response
            digital_twin = response.get("payload", {}).get("digital_twin", {})
            
            return digital_twin
        except Exception as e:
            logger.error(f"Error getting mission digital twin: {str(e)}")
            return {}
    
    def shutdown(self) -> None:
        """Shutdown the Mission Deck."""
        logger.info("Shutting down Mission Deck")
        
        # Stop auto-refresh
        if self.config["auto_refresh"]:
            self._stop_auto_refresh()
