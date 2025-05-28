"""
Mission Control Page - The mission control page component for the Industriverse UI/UX Layer.

This component provides a centralized interface for defining, monitoring, and managing
complex missions and objectives within the Industriverse ecosystem. It integrates with
the Workflow Automation Layer and Application Layer to orchestrate and track mission progress.

Features:
- Mission definition and planning tools
- Real-time mission progress monitoring
- Resource allocation and management for missions
- Agent tasking and coordination for mission objectives
- Risk assessment and mitigation planning
- Collaboration tools for mission teams
- Integration with Mission Deck component for tactical views
- Scenario simulation and what-if analysis

The component uses the Universal Skin architecture to adapt its presentation based on
device capabilities, user role, and context, while maintaining protocol-native visualization
of the underlying mission state and agent activities.
"""

import sys
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union

# Add parent directory to path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.universal_skin.universal_skin_shell import UniversalSkinShell
from core.universal_skin.device_adapter import DeviceAdapter
from core.agent_ecosystem.avatar_manager import AvatarManager
from core.capsule_framework.capsule_manager import CapsuleManager
from core.context_engine.context_engine import ContextEngine
from core.interaction_orchestrator.interaction_orchestrator import InteractionOrchestrator
from core.protocol_bridge.protocol_bridge import ProtocolBridge
from core.cross_layer_integration.real_time_context_bus import RealTimeContextBus
from core.rendering_engine.rendering_engine import RenderingEngine
from components.mission_deck.mission_deck import MissionDeck
from components.timeline_view.timeline_view import TimelineView
from components.spatial_canvas.spatial_canvas import SpatialCanvas
from components.ambient_veil.ambient_veil import AmbientVeil
from components.layer_avatars.layer_avatars import LayerAvatars

class MissionControlPage:
    """
    Mission Control Page component for the Industriverse UI/UX Layer.
    
    This page provides a centralized interface for defining, monitoring, and managing
    complex missions and objectives within the Industriverse ecosystem.
    """
    
    def __init__(
        self,
        universal_skin_shell: UniversalSkinShell,
        device_adapter: DeviceAdapter,
        avatar_manager: AvatarManager,
        capsule_manager: CapsuleManager,
        context_engine: ContextEngine,
        interaction_orchestrator: InteractionOrchestrator,
        protocol_bridge: ProtocolBridge,
        real_time_context_bus: RealTimeContextBus,
        rendering_engine: RenderingEngine
    ):
        """
        Initialize the Mission Control Page component.
        
        Args:
            universal_skin_shell: The Universal Skin Shell instance
            device_adapter: The Device Adapter instance
            avatar_manager: The Avatar Manager instance
            capsule_manager: The Capsule Manager instance
            context_engine: The Context Engine instance
            interaction_orchestrator: The Interaction Orchestrator instance
            protocol_bridge: The Protocol Bridge instance
            real_time_context_bus: The Real-Time Context Bus instance
            rendering_engine: The Rendering Engine instance
        """
        self.universal_skin_shell = universal_skin_shell
        self.device_adapter = device_adapter
        self.avatar_manager = avatar_manager
        self.capsule_manager = capsule_manager
        self.context_engine = context_engine
        self.interaction_orchestrator = interaction_orchestrator
        self.protocol_bridge = protocol_bridge
        self.real_time_context_bus = real_time_context_bus
        self.rendering_engine = rendering_engine
        
        # Initialize sub-components
        self.mission_deck = MissionDeck(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            real_time_context_bus=real_time_context_bus,
            interaction_orchestrator=interaction_orchestrator
        )
        
        self.timeline_view = TimelineView(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            real_time_context_bus=real_time_context_bus
        )
        
        self.spatial_canvas = SpatialCanvas(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            real_time_context_bus=real_time_context_bus,
            interaction_orchestrator=interaction_orchestrator
        )
        
        self.ambient_veil = AmbientVeil(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            context_engine=context_engine
        )
        
        self.layer_avatars = LayerAvatars(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            avatar_manager=avatar_manager,
            real_time_context_bus=real_time_context_bus
        )
        
        # Initialize state
        self.state = {
            "selected_mission_id": None,
            "missions": [],
            "mission_history": [],
            "filter_criteria": {
                "status": None,  # Options: planning, active, paused, completed, failed
                "priority": None,  # Options: critical, high, medium, low
                "domain": None  # e.g., manufacturing, logistics
            },
            "view_mode": "overview",  # Options: overview, planning, monitoring, analysis
            "detail_level": "medium",  # Options: low, medium, high
            "show_resource_allocation": True,
            "show_agent_tasking": True,
            "show_risk_assessment": True
        }
        
        # Subscribe to mission-related events
        self._subscribe_to_events()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Mission Control Page initialized")
    
    def _subscribe_to_events(self):
        """Subscribe to mission-related events from the Real-Time Context Bus."""
        self.real_time_context_bus.subscribe(
            topic="mission.status.update",
            callback=self._handle_mission_status_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="mission.objective.update",
            callback=self._handle_mission_objective_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="mission.resource.update",
            callback=self._handle_mission_resource_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="mission.agent.update",
            callback=self._handle_mission_agent_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="mission.risk.update",
            callback=self._handle_mission_risk_update
        )
    
    def render(self) -> Dict[str, Any]:
        """
        Render the Mission Control Page.
        
        Returns:
            Dict containing the rendered page structure
        """
        # Adapt rendering based on device capabilities and context
        device_capabilities = self.device_adapter.get_capabilities()
        user_context = self.context_engine.get_current_context()
        
        # Determine layout based on device and context
        layout = self._determine_layout(device_capabilities, user_context)
        
        # Render main components based on view mode
        main_content = self._render_main_content(self.state["view_mode"])
        
        # Render layer avatars
        layer_avatars_render = self.layer_avatars.render(
            selected_layer=None  # No specific layer selected for mission control
        )
        
        # Render ambient veil
        ambient_veil_render = self.ambient_veil.render(
            context=user_context,
            missions=self.state["missions"]
        )
        
        # Construct the page structure
        page_structure = {
            "type": "page",
            "id": "mission_control_page",
            "title": "Mission Control",
            "layout": layout,
            "components": {
                "header": self._render_header(),
                "sidebar": self._render_sidebar(),
                "main_content": main_content,
                "layer_avatars": layer_avatars_render,
                "ambient_veil": ambient_veil_render
            },
            "actions": self._get_available_actions(),
            "state": self.state
        }
        
        # Apply Universal Skin adaptations
        adapted_page = self.universal_skin_shell.adapt_component(
            component=page_structure,
            device_capabilities=device_capabilities,
            user_context=user_context
        )
        
        return adapted_page
    
    def _determine_layout(self, device_capabilities: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """
        Determine the appropriate layout based on device capabilities and user context.
        
        Args:
            device_capabilities: Device capabilities from the Device Adapter
            user_context: User context from the Context Engine
            
        Returns:
            String representing the layout type
        """
        if device_capabilities.get("form_factor") == "mobile":
            return "mobile"
        elif device_capabilities.get("form_factor") == "tablet":
            return "tablet"
        elif device_capabilities.get("is_ar_vr", False):
            return "immersive"
        else:
            return "desktop"
    
    def _render_header(self) -> Dict[str, Any]:
        """
        Render the header component.
        
        Returns:
            Dict containing the rendered header structure
        """
        return {
            "type": "header",
            "title": "Mission Control",
            "subtitle": "Define, monitor, and manage complex missions and objectives",
            "actions": [
                {
                    "type": "button",
                    "label": "New Mission",
                    "icon": "plus",
                    "action": "create_mission"
                },
                {
                    "type": "button",
                    "label": "Import Mission Plan",
                    "icon": "import",
                    "action": "import_mission_plan"
                },
                {
                    "type": "button",
                    "label": "Export Mission Report",
                    "icon": "export",
                    "action": "export_mission_report",
                    "disabled": self.state["selected_mission_id"] is None
                }
            ],
            "filters": [
                {
                    "type": "dropdown",
                    "label": "View Mode",
                    "options": [
                        {"value": "overview", "label": "Overview"},
                        {"value": "planning", "label": "Planning"},
                        {"value": "monitoring", "label": "Monitoring"},
                        {"value": "analysis", "label": "Analysis"}
                    ],
                    "value": self.state["view_mode"],
                    "action": "change_view_mode"
                }
            ]
        }
    
    def _render_sidebar(self) -> Dict[str, Any]:
        """
        Render the sidebar component.
        
        Returns:
            Dict containing the rendered sidebar structure
        """
        return {
            "type": "sidebar",
            "sections": [
                {
                    "type": "section",
                    "title": "Missions",
                    "items": [self._render_mission_item(mission) for mission in self.state["missions"]]
                },
                {
                    "type": "section",
                    "title": "Filters",
                    "items": [
                        {
                            "type": "dropdown",
                            "label": "Status",
                            "options": [
                                {"value": "all", "label": "All Statuses"},
                                {"value": "planning", "label": "Planning"},
                                {"value": "active", "label": "Active"},
                                {"value": "paused", "label": "Paused"},
                                {"value": "completed", "label": "Completed"},
                                {"value": "failed", "label": "Failed"}
                            ],
                            "value": self.state["filter_criteria"]["status"] or "all",
                            "action": "filter_by_status"
                        },
                        {
                            "type": "dropdown",
                            "label": "Priority",
                            "options": [
                                {"value": "all", "label": "All Priorities"},
                                {"value": "critical", "label": "Critical"},
                                {"value": "high", "label": "High"},
                                {"value": "medium", "label": "Medium"},
                                {"value": "low", "label": "Low"}
                            ],
                            "value": self.state["filter_criteria"]["priority"] or "all",
                            "action": "filter_by_priority"
                        },
                        {
                            "type": "dropdown",
                            "label": "Domain",
                            "options": [
                                {"value": "all", "label": "All Domains"},
                                {"value": "manufacturing", "label": "Manufacturing"},
                                {"value": "logistics", "label": "Logistics"},
                                {"value": "energy", "label": "Energy"},
                                {"value": "retail", "label": "Retail"}
                            ],
                            "value": self.state["filter_criteria"]["domain"] or "all",
                            "action": "filter_by_domain"
                        }
                    ]
                },
                {
                    "type": "section",
                    "title": "View Options",
                    "items": [
                        {
                            "type": "radio_group",
                            "label": "Detail Level",
                            "options": [
                                {"value": "low", "label": "Low"},
                                {"value": "medium", "label": "Medium"},
                                {"value": "high", "label": "High"}
                            ],
                            "value": self.state["detail_level"],
                            "action": "change_detail_level"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Resource Allocation",
                            "checked": self.state["show_resource_allocation"],
                            "action": "toggle_resource_allocation"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Agent Tasking",
                            "checked": self.state["show_agent_tasking"],
                            "action": "toggle_agent_tasking"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Risk Assessment",
                            "checked": self.state["show_risk_assessment"],
                            "action": "toggle_risk_assessment"
                        }
                    ]
                }
            ]
        }
    
    def _render_mission_item(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a mission item for the sidebar.
        
        Args:
            mission: Mission data
            
        Returns:
            Dict containing the rendered mission item structure
        """
        # Determine status color
        status_colors = {
            "planning": "gray",
            "active": "green",
            "paused": "yellow",
            "completed": "blue",
            "failed": "red"
        }
        status_color = status_colors.get(mission.get("status", "planning"), "gray")
        
        # Determine priority color
        priority_colors = {
            "critical": "red",
            "high": "orange",
            "medium": "yellow",
            "low": "blue"
        }
        priority_color = priority_colors.get(mission.get("priority", "medium"), "gray")
        
        return {
            "type": "list_item",
            "id": f"mission_{mission["id"]}",
            "title": mission.get("name", "Unnamed Mission"),
            "subtitle": mission.get("objective", ""),
            "icon": mission.get("icon", "mission"),
            "selected": mission["id"] == self.state["selected_mission_id"],
            "tags": [
                {"label": mission.get("status", "planning"), "color": status_color},
                {"label": mission.get("priority", "medium"), "color": priority_color},
                {"label": mission.get("domain", "General"), "color": "blue"}
            ],
            "actions": [
                {
                    "type": "button",
                    "label": "Select",
                    "icon": "select",
                    "action": "select_mission",
                    "params": {"mission_id": mission["id"]}
                },
                {
                    "type": "button",
                    "label": mission.get("status") == "active" ? "Pause" : "Resume",
                    "icon": mission.get("status") == "active" ? "pause" : "play",
                    "action": mission.get("status") == "active" ? "pause_mission" : "resume_mission",
                    "params": {"mission_id": mission["id"]},
                    "disabled": mission.get("status") not in ["active", "paused"]
                }
            ]
        }
    
    def _render_main_content(self, view_mode: str) -> Dict[str, Any]:
        """
        Render the main content area based on the selected view mode.
        
        Args:
            view_mode: The current view mode
            
        Returns:
            Dict containing the rendered main content structure
        """
        if view_mode == "overview":
            return self._render_overview_view()
        elif view_mode == "planning":
            return self._render_planning_view()
        elif view_mode == "monitoring":
            return self._render_monitoring_view()
        elif view_mode == "analysis":
            return self._render_analysis_view()
        else:
            return {
                "type": "message",
                "text": f"Invalid view mode: {view_mode}"
            }
    
    def _render_overview_view(self) -> Dict[str, Any]:
        """
        Render the overview view.
        
        Returns:
            Dict containing the rendered overview view structure
        """
        # Get overview data
        overview_data = self._get_overview_data()
        
        return {
            "type": "container",
            "layout": "grid",
            "children": [
                {
                    "type": "widget",
                    "title": "Mission Summary",
                    "position": {"row": 0, "col": 0, "width": 4, "height": 2},
                    "content": {
                        "type": "summary_panel",
                        "data": overview_data.get("summary", {})
                    }
                },
                {
                    "type": "widget",
                    "title": "Active Missions",
                    "position": {"row": 0, "col": 4, "width": 8, "height": 2},
                    "content": {
                        "type": "mission_list",
                        "missions": overview_data.get("active_missions", []),
                        "action": "select_mission"
                    }
                },
                {
                    "type": "widget",
                    "title": "Mission Timeline",
                    "position": {"row": 2, "col": 0, "width": 12, "height": 3},
                    "content": self.timeline_view.render(
                        missions=self.state["missions"],
                        mission_history=self.state["mission_history"],
                        selected_mission_id=self.state["selected_mission_id"]
                    )
                }
            ]
        }
    
    def _get_overview_data(self) -> Dict[str, Any]:
        """
        Get data for the overview view.
        
        Returns:
            Dict containing overview data
        """
        # In a real implementation, this would fetch data from the Real-Time Context Bus
        # For now, return mock data
        return {
            "summary": {
                "total_missions": len(self.state["missions"]),
                "active_missions": sum(1 for m in self.state["missions"] if m.get("status") == "active"),
                "completed_missions": sum(1 for m in self.state["missions"] if m.get("status") == "completed"),
                "failed_missions": sum(1 for m in self.state["missions"] if m.get("status") == "failed"),
                "average_completion_time": "12 days",
                "success_rate": "85%"
            },
            "active_missions": [m for m in self.state["missions"] if m.get("status") == "active"]
        }
    
    def _render_planning_view(self) -> Dict[str, Any]:
        """
        Render the planning view.
        
        Returns:
            Dict containing the rendered planning view structure
        """
        selected_mission = self._get_selected_mission()
        
        if not selected_mission:
            return {
                "type": "message",
                "text": "Select a mission or create a new one to start planning."
            }
        
        return {
            "type": "container",
            "layout": "split",
            "split_direction": "horizontal",
            "children": [
                {
                    "type": "container",
                    "title": "Mission Details",
                    "flex": 1,
                    "children": [
                        {
                            "type": "mission_planner",
                            "mission": selected_mission,
                            "actions": {
                                "save_plan": "save_mission_plan",
                                "add_objective": "add_mission_objective",
                                "allocate_resource": "allocate_mission_resource",
                                "assign_agent": "assign_mission_agent"
                            }
                        }
                    ]
                },
                {
                    "type": "container",
                    "title": "Resource Pool",
                    "flex": 1,
                    "children": [
                        {
                            "type": "resource_browser",
                            "available_resources": self._get_available_resources(),
                            "action": "allocate_mission_resource"
                        }
                    ]
                },
                {
                    "type": "container",
                    "title": "Agent Pool",
                    "flex": 1,
                    "children": [
                        {
                            "type": "agent_browser",
                            "available_agents": self._get_available_agents(),
                            "action": "assign_mission_agent"
                        }
                    ]
                }
            ]
        }
    
    def _get_selected_mission(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected mission data.
        
        Returns:
            Dict containing selected mission data, or None if no mission is selected
        """
        if not self.state["selected_mission_id"]:
            return None
        
        for mission in self.state["missions"]:
            if mission["id"] == self.state["selected_mission_id"]:
                return mission
        
        return None
    
    def _get_available_resources(self) -> List[Dict[str, Any]]:
        """
        Get available resources for mission planning.
        
        Returns:
            List of available resources
        """
        # In a real implementation, this would fetch data from relevant layers
        # For now, return mock data
        return [
            {"id": "res_1", "name": "Manufacturing Robot Arm", "type": "robot", "status": "available"},
            {"id": "res_2", "name": "Logistics Drone Fleet", "type": "drone", "status": "available"},
            {"id": "res_3", "name": "Energy Grid Sensor Network", "type": "sensor", "status": "available"},
            {"id": "res_4", "name": "Retail Inventory Scanner", "type": "scanner", "status": "available"},
            {"id": "res_5", "name": "High-Performance Compute Cluster", "type": "compute", "status": "available"}
        ]
    
    def _get_available_agents(self) -> List[Dict[str, Any]]:
        """
        Get available agents for mission planning.
        
        Returns:
            List of available agents
        """
        # In a real implementation, this would fetch data from the Agent Ecosystem
        # For now, return mock data
        return [
            {"id": "agent_1", "name": "Workflow Trigger Agent", "capabilities": ["workflow_trigger"], "status": "idle"},
            {"id": "agent_2", "name": "Data Ingestion Agent", "capabilities": ["data_ingestion"], "status": "idle"},
            {"id": "agent_3", "name": "Anomaly Detection Agent", "capabilities": ["anomaly_detection"], "status": "idle"},
            {"id": "agent_4", "name": "Human Intervention Agent", "capabilities": ["human_intervention"], "status": "idle"},
            {"id": "agent_5", "name": "Model Training Agent", "capabilities": ["model_training"], "status": "idle"},
            {"id": "agent_6", "name": "Workflow Optimizer Agent", "capabilities": ["workflow_optimization"], "status": "idle"}
        ]
    
    def _render_monitoring_view(self) -> Dict[str, Any]:
        """
        Render the monitoring view.
        
        Returns:
            Dict containing the rendered monitoring view structure
        """
        selected_mission = self._get_selected_mission()
        
        if not selected_mission:
            return {
                "type": "message",
                "text": "Select a mission to monitor its progress."
            }
        
        # Render mission deck for the selected mission
        mission_deck_render = self.mission_deck.render(
            mission=selected_mission,
            show_resource_allocation=self.state["show_resource_allocation"],
            show_agent_tasking=self.state["show_agent_tasking"],
            show_risk_assessment=self.state["show_risk_assessment"]
        )
        
        # Render spatial canvas for mission visualization
        spatial_canvas_render = self.spatial_canvas.render(
            mission=selected_mission,
            show_agents=self.state["show_agent_tasking"],
            show_resources=self.state["show_resource_allocation"]
        )
        
        return {
            "type": "container",
            "layout": "split",
            "split_direction": "vertical",
            "children": [
                {
                    "type": "container",
                    "title": f"Mission Monitoring: {selected_mission.get("name")}",
                    "flex": 2,
                    "children": [spatial_canvas_render]
                },
                {
                    "type": "container",
                    "title": "Mission Deck",
                    "flex": 1,
                    "children": [mission_deck_render]
                }
            ]
        }
    
    def _render_analysis_view(self) -> Dict[str, Any]:
        """
        Render the analysis view.
        
        Returns:
            Dict containing the rendered analysis view structure
        """
        selected_mission = self._get_selected_mission()
        
        if not selected_mission:
            return {
                "type": "message",
                "text": "Select a mission to analyze its performance."
            }
        
        # Get analysis data for the selected mission
        analysis_data = self._get_analysis_data(selected_mission["id"])
        
        return {
            "type": "container",
            "layout": "grid",
            "children": [
                {
                    "type": "widget",
                    "title": "Mission Performance Metrics",
                    "position": {"row": 0, "col": 0, "width": 6, "height": 3},
                    "content": {
                        "type": "performance_metrics",
                        "data": analysis_data.get("performance", {})
                    }
                },
                {
                    "type": "widget",
                    "title": "Resource Efficiency",
                    "position": {"row": 0, "col": 6, "width": 6, "height": 3},
                    "content": {
                        "type": "resource_efficiency",
                        "data": analysis_data.get("resources", {})
                    }
                },
                {
                    "type": "widget",
                    "title": "Agent Contribution",
                    "position": {"row": 3, "col": 0, "width": 6, "height": 3},
                    "content": {
                        "type": "agent_contribution",
                        "data": analysis_data.get("agents", {})
                    }
                },
                {
                    "type": "widget",
                    "title": "Risk Analysis",
                    "position": {"row": 3, "col": 6, "width": 6, "height": 3},
                    "content": {
                        "type": "risk_analysis",
                        "data": analysis_data.get("risks", {})
                    }
                }
            ]
        }
    
    def _get_analysis_data(self, mission_id: str) -> Dict[str, Any]:
        """
        Get analysis data for a specific mission.
        
        Args:
            mission_id: ID of the mission to analyze
            
        Returns:
            Dict containing analysis data
        """
        # In a real implementation, this would fetch data from relevant layers
        # For now, return mock data
        return {
            "performance": {
                "completion_time": "11 days",
                "objective_success_rate": "92%",
                "budget_adherence": "98%",
                "key_milestones": [
                    {"name": "Phase 1 Complete", "status": "on_time"},
                    {"name": "Phase 2 Complete", "status": "delayed"},
                    {"name": "Phase 3 Complete", "status": "on_time"}
                ]
            },
            "resources": {
                "overall_utilization": "78%",
                "bottlenecks": ["Compute Cluster"],
                "efficiency_score": 85
            },
            "agents": {
                "most_active": ["Data Ingestion Agent", "Workflow Optimizer Agent"],
                "task_completion_rate": "95%",
                "collaboration_index": 7.2
            },
            "risks": {
                "identified_risks": 12,
                "mitigated_risks": 9,
                "active_risks": 3,
                "impact_assessment": "medium"
            }
        }
    
    def _get_available_actions(self) -> Dict[str, Any]:
        """
        Get available actions for the page.
        
        Returns:
            Dict containing available actions and their handlers
        """
        return {
            "create_mission": self.create_mission,
            "import_mission_plan": self.import_mission_plan,
            "export_mission_report": self.export_mission_report,
            "change_view_mode": self.change_view_mode,
            "filter_by_status": self.filter_by_status,
            "filter_by_priority": self.filter_by_priority,
            "filter_by_domain": self.filter_by_domain,
            "change_detail_level": self.change_detail_level,
            "toggle_resource_allocation": self.toggle_resource_allocation,
            "toggle_agent_tasking": self.toggle_agent_tasking,
            "toggle_risk_assessment": self.toggle_risk_assessment,
            "select_mission": self.select_mission,
            "pause_mission": self.pause_mission,
            "resume_mission": self.resume_mission,
            "save_mission_plan": self.save_mission_plan,
            "add_mission_objective": self.add_mission_objective,
            "allocate_mission_resource": self.allocate_mission_resource,
            "assign_mission_agent": self.assign_mission_agent
        }
    
    # Event handlers
    def _handle_mission_status_update(self, event: Dict[str, Any]):
        """
        Handle mission status update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        mission_id = event.get("mission_id")
        new_status = event.get("status")
        
        if not mission_id or not new_status:
            return
        
        # Update mission status in missions list
        for mission in self.state["missions"]:
            if mission["id"] == mission_id:
                mission["status"] = new_status
                break
        
        # If this is the selected mission, update relevant components
        if self.state["selected_mission_id"] == mission_id:
            self.mission_deck.update_mission_status(mission_id, new_status)
            self.timeline_view.update_mission_status(mission_id, new_status)
    
    def _handle_mission_objective_update(self, event: Dict[str, Any]):
        """
        Handle mission objective update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        mission_id = event.get("mission_id")
        objective_id = event.get("objective_id")
        objective_data = event.get("objective_data")
        
        if not mission_id or not objective_id or not objective_data:
            return
        
        # Update objective in the selected mission
        selected_mission = self._get_selected_mission()
        if selected_mission and selected_mission["id"] == mission_id:
            # Find and update the objective
            for i, objective in enumerate(selected_mission.get("objectives", [])):
                if objective["id"] == objective_id:
                    selected_mission["objectives"][i] = objective_data
                    break
            else:
                # Add new objective if not found
                if "objectives" not in selected_mission:
                    selected_mission["objectives"] = []
                selected_mission["objectives"].append(objective_data)
            
            # Update relevant components
            self.mission_deck.update_objective(mission_id, objective_id, objective_data)
            self.timeline_view.update_objective(mission_id, objective_id, objective_data)
    
    def _handle_mission_resource_update(self, event: Dict[str, Any]):
        """
        Handle mission resource update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        mission_id = event.get("mission_id")
        resource_id = event.get("resource_id")
        resource_data = event.get("resource_data")
        
        if not mission_id or not resource_id or not resource_data:
            return
        
        # Update resource allocation in the selected mission
        selected_mission = self._get_selected_mission()
        if selected_mission and selected_mission["id"] == mission_id:
            # Find and update the resource allocation
            for i, resource in enumerate(selected_mission.get("resources", [])):
                if resource["id"] == resource_id:
                    selected_mission["resources"][i] = resource_data
                    break
            else:
                # Add new resource allocation if not found
                if "resources" not in selected_mission:
                    selected_mission["resources"] = []
                selected_mission["resources"].append(resource_data)
            
            # Update relevant components
            self.mission_deck.update_resource(mission_id, resource_id, resource_data)
            self.spatial_canvas.update_resource(mission_id, resource_id, resource_data)
    
    def _handle_mission_agent_update(self, event: Dict[str, Any]):
        """
        Handle mission agent update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        mission_id = event.get("mission_id")
        agent_id = event.get("agent_id")
        agent_data = event.get("agent_data")
        
        if not mission_id or not agent_id or not agent_data:
            return
        
        # Update agent tasking in the selected mission
        selected_mission = self._get_selected_mission()
        if selected_mission and selected_mission["id"] == mission_id:
            # Find and update the agent tasking
            for i, agent in enumerate(selected_mission.get("agents", [])):
                if agent["id"] == agent_id:
                    selected_mission["agents"][i] = agent_data
                    break
            else:
                # Add new agent tasking if not found
                if "agents" not in selected_mission:
                    selected_mission["agents"] = []
                selected_mission["agents"].append(agent_data)
            
            # Update relevant components
            self.mission_deck.update_agent(mission_id, agent_id, agent_data)
            self.spatial_canvas.update_agent(mission_id, agent_id, agent_data)
    
    def _handle_mission_risk_update(self, event: Dict[str, Any]):
        """
        Handle mission risk update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        mission_id = event.get("mission_id")
        risk_id = event.get("risk_id")
        risk_data = event.get("risk_data")
        
        if not mission_id or not risk_id or not risk_data:
            return
        
        # Update risk assessment in the selected mission
        selected_mission = self._get_selected_mission()
        if selected_mission and selected_mission["id"] == mission_id:
            # Find and update the risk
            for i, risk in enumerate(selected_mission.get("risks", [])):
                if risk["id"] == risk_id:
                    selected_mission["risks"][i] = risk_data
                    break
            else:
                # Add new risk if not found
                if "risks" not in selected_mission:
                    selected_mission["risks"] = []
                selected_mission["risks"].append(risk_data)
            
            # Update relevant components
            self.mission_deck.update_risk(mission_id, risk_id, risk_data)
    
    # Action handlers
    def create_mission(self, params: Dict[str, Any] = None):
        """
        Create a new mission.
        
        Args:
            params: Optional parameters for mission creation
        """
        # Request mission creation from the Application Layer or Workflow Layer
        self.real_time_context_bus.publish(
            topic="mission.create.request",
            data={
                "source": "ui_ux_layer",
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested mission creation with params: {params}")
    
    def import_mission_plan(self, params: Dict[str, Any] = None):
        """
        Import a mission plan.
        
        Args:
            params: Optional parameters for mission import
        """
        # Request mission import
        self.real_time_context_bus.publish(
            topic="mission.import.request",
            data={
                "source": "ui_ux_layer",
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested mission plan import with params: {params}")
    
    def export_mission_report(self, params: Dict[str, Any] = None):
        """
        Export a report for the selected mission.
        
        Args:
            params: Optional parameters for mission export
        """
        mission_id = params.get("mission_id") if params else self.state["selected_mission_id"]
        
        if not mission_id:
            self.logger.warning("Cannot export mission report: No mission selected")
            return
        
        # Request mission report export
        self.real_time_context_bus.publish(
            topic="mission.export.request",
            data={
                "source": "ui_ux_layer",
                "mission_id": mission_id,
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested export of mission report for {mission_id}")
    
    def change_view_mode(self, params: Dict[str, Any]):
        """
        Change the view mode.
        
        Args:
            params: Parameters containing the view mode value
        """
        view_mode = params.get("value")
        if view_mode:
            self.state["view_mode"] = view_mode
    
    def filter_by_status(self, params: Dict[str, Any]):
        """
        Filter missions by status.
        
        Args:
            params: Parameters containing the status filter value
        """
        status = params.get("value")
        if status:
            self.state["filter_criteria"]["status"] = status if status != "all" else None
            self._apply_filters()
    
    def filter_by_priority(self, params: Dict[str, Any]):
        """
        Filter missions by priority.
        
        Args:
            params: Parameters containing the priority filter value
        """
        priority = params.get("value")
        if priority:
            self.state["filter_criteria"]["priority"] = priority if priority != "all" else None
            self._apply_filters()
    
    def filter_by_domain(self, params: Dict[str, Any]):
        """
        Filter missions by domain.
        
        Args:
            params: Parameters containing the domain filter value
        """
        domain = params.get("value")
        if domain:
            self.state["filter_criteria"]["domain"] = domain if domain != "all" else None
            self._apply_filters()
    
    def _apply_filters(self):
        """Apply current filters to fetch updated mission data."""
        # Request filtered missions
        self.real_time_context_bus.publish(
            topic="mission.list.request",
            data={
                "source": "ui_ux_layer",
                "filter_criteria": self.state["filter_criteria"]
            }
        )
        
        self.logger.info(f"Applied mission filters: {self.state["filter_criteria"]}")
    
    def change_detail_level(self, params: Dict[str, Any]):
        """
        Change the detail level.
        
        Args:
            params: Parameters containing the detail level value
        """
        detail_level = params.get("value")
        if detail_level:
            self.state["detail_level"] = detail_level
    
    def toggle_resource_allocation(self, params: Dict[str, Any]):
        """
        Toggle display of resource allocation.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_resource_allocation = params.get("checked")
        if show_resource_allocation is not None:
            self.state["show_resource_allocation"] = show_resource_allocation
    
    def toggle_agent_tasking(self, params: Dict[str, Any]):
        """
        Toggle display of agent tasking.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_agent_tasking = params.get("checked")
        if show_agent_tasking is not None:
            self.state["show_agent_tasking"] = show_agent_tasking
    
    def toggle_risk_assessment(self, params: Dict[str, Any]):
        """
        Toggle display of risk assessment.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_risk_assessment = params.get("checked")
        if show_risk_assessment is not None:
            self.state["show_risk_assessment"] = show_risk_assessment
    
    def select_mission(self, params: Dict[str, Any]):
        """
        Select a mission.
        
        Args:
            params: Parameters containing the mission ID
        """
        mission_id = params.get("mission_id")
        if mission_id:
            self.state["selected_mission_id"] = mission_id
            
            # Request detailed mission data
            self.real_time_context_bus.publish(
                topic="mission.detail.request",
                data={
                    "source": "ui_ux_layer",
                    "mission_id": mission_id
                }
            )
            
            self.logger.info(f"Selected mission {mission_id}")
    
    def pause_mission(self, params: Dict[str, Any]):
        """
        Pause a mission.
        
        Args:
            params: Parameters containing the mission ID
        """
        mission_id = params.get("mission_id")
        if not mission_id:
            self.logger.warning("Cannot pause mission: No mission ID provided")
            return
        
        # Request mission pause
        self.real_time_context_bus.publish(
            topic="mission.pause.request",
            data={
                "source": "ui_ux_layer",
                "mission_id": mission_id
            }
        )
        
        self.logger.info(f"Requested pause of mission {mission_id}")
    
    def resume_mission(self, params: Dict[str, Any]):
        """
        Resume a paused mission.
        
        Args:
            params: Parameters containing the mission ID
        """
        mission_id = params.get("mission_id")
        if not mission_id:
            self.logger.warning("Cannot resume mission: No mission ID provided")
            return
        
        # Request mission resume
        self.real_time_context_bus.publish(
            topic="mission.resume.request",
            data={
                "source": "ui_ux_layer",
                "mission_id": mission_id
            }
        )
        
        self.logger.info(f"Requested resume of mission {mission_id}")
    
    def save_mission_plan(self, params: Dict[str, Any]):
        """
        Save the mission plan for the selected mission.
        
        Args:
            params: Parameters containing the mission plan data
        """
        mission_id = self.state["selected_mission_id"]
        mission_plan = params.get("mission_plan")
        
        if not mission_id or not mission_plan:
            self.logger.warning("Cannot save mission plan: Missing mission ID or plan data")
            return
        
        # Request mission plan save
        self.real_time_context_bus.publish(
            topic="mission.plan.save.request",
            data={
                "source": "ui_ux_layer",
                "mission_id": mission_id,
                "mission_plan": mission_plan
            }
        )
        
        self.logger.info(f"Requested save of mission plan for {mission_id}")
    
    def add_mission_objective(self, params: Dict[str, Any]):
        """
        Add an objective to the selected mission.
        
        Args:
            params: Parameters containing the objective data
        """
        mission_id = self.state["selected_mission_id"]
        objective_data = params.get("objective_data")
        
        if not mission_id or not objective_data:
            self.logger.warning("Cannot add objective: Missing mission ID or objective data")
            return
        
        # Request objective addition
        self.real_time_context_bus.publish(
            topic="mission.objective.add.request",
            data={
                "source": "ui_ux_layer",
                "mission_id": mission_id,
                "objective_data": objective_data
            }
        )
        
        self.logger.info(f"Requested addition of objective to mission {mission_id}")
    
    def allocate_mission_resource(self, params: Dict[str, Any]):
        """
        Allocate a resource to the selected mission.
        
        Args:
            params: Parameters containing the resource ID and allocation details
        """
        mission_id = self.state["selected_mission_id"]
        resource_id = params.get("resource_id")
        allocation_details = params.get("allocation_details")
        
        if not mission_id or not resource_id or not allocation_details:
            self.logger.warning("Cannot allocate resource: Missing mission ID, resource ID, or allocation details")
            return
        
        # Request resource allocation
        self.real_time_context_bus.publish(
            topic="mission.resource.allocate.request",
            data={
                "source": "ui_ux_layer",
                "mission_id": mission_id,
                "resource_id": resource_id,
                "allocation_details": allocation_details
            }
        )
        
        self.logger.info(f"Requested allocation of resource {resource_id} to mission {mission_id}")
    
    def assign_mission_agent(self, params: Dict[str, Any]):
        """
        Assign an agent to the selected mission.
        
        Args:
            params: Parameters containing the agent ID and assignment details
        """
        mission_id = self.state["selected_mission_id"]
        agent_id = params.get("agent_id")
        assignment_details = params.get("assignment_details")
        
        if not mission_id or not agent_id or not assignment_details:
            self.logger.warning("Cannot assign agent: Missing mission ID, agent ID, or assignment details")
            return
        
        # Request agent assignment
        self.real_time_context_bus.publish(
            topic="mission.agent.assign.request",
            data={
                "source": "ui_ux_layer",
                "mission_id": mission_id,
                "agent_id": agent_id,
                "assignment_details": assignment_details
            }
        )
        
        self.logger.info(f"Requested assignment of agent {agent_id} to mission {mission_id}")
