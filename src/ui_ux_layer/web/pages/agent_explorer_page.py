"""
Agent Explorer Page - The agent explorer page component for the Industriverse UI/UX Layer.

This component provides a comprehensive interface for discovering, exploring, and interacting
with agents across the Industriverse ecosystem. It visualizes agent capabilities, relationships,
and activities, enabling users to monitor and interact with the agent ecosystem.

Features:
- Agent discovery and filtering by type, domain, and status
- Detailed agent profiles with capability visualization
- Protocol-native visualization of agent communication and activities
- Trust-weighted routing visualization with the Trust Ribbon component
- Integration with Layer Avatars for personified agent representation
- Adaptive presentation based on device capabilities, user role, and context

The component uses the Universal Skin architecture to adapt its presentation based on
device capabilities, user role, and context, while maintaining protocol-native visualization
of the underlying agent ecosystem.
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
from components.layer_avatars.layer_avatars import LayerAvatars
from components.trust_ribbon.trust_ribbon import TrustRibbon
from components.protocol_visualizer.protocol_visualizer import ProtocolVisualizer
from components.ambient_veil.ambient_veil import AmbientVeil
from components.spatial_canvas.spatial_canvas import SpatialCanvas
from components.workflow_canvas.workflow_canvas import WorkflowCanvas
from components.data_visualization.data_visualization import DataVisualization

class AgentExplorerPage:
    """
    Agent Explorer Page component for the Industriverse UI/UX Layer.
    
    This page provides a comprehensive interface for discovering, exploring, and interacting
    with agents across the Industriverse ecosystem.
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
        Initialize the Agent Explorer Page component.
        
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
        self.layer_avatars = LayerAvatars(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            avatar_manager=avatar_manager,
            real_time_context_bus=real_time_context_bus
        )
        
        self.trust_ribbon = TrustRibbon(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            protocol_bridge=protocol_bridge
        )
        
        self.protocol_visualizer = ProtocolVisualizer(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            protocol_bridge=protocol_bridge
        )
        
        self.ambient_veil = AmbientVeil(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            context_engine=context_engine
        )
        
        self.spatial_canvas = SpatialCanvas(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            real_time_context_bus=real_time_context_bus,
            interaction_orchestrator=interaction_orchestrator
        )
        
        self.workflow_canvas = WorkflowCanvas(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            real_time_context_bus=real_time_context_bus,
            protocol_bridge=protocol_bridge,
            interaction_orchestrator=interaction_orchestrator
        )
        
        self.data_visualization = DataVisualization(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            real_time_context_bus=real_time_context_bus
        )
        
        # Initialize state
        self.state = {
            "selected_agent_id": None,
            "agents": [],
            "filter_criteria": {
                "type": None,  # e.g., workflow, data, core_ai
                "domain": None,  # e.g., manufacturing, logistics
                "status": None,  # e.g., active, idle, busy
                "trust_threshold": 0.7,
                "layer": None  # e.g., data_layer, core_ai_layer
            },
            "view_mode": "grid",  # Options: grid, list, spatial, detail
            "sort_by": "name",  # Options: name, type, status, trust_score
            "show_trust_scores": True,
            "show_capabilities": True,
            "show_relationships": True,
            "show_activity": True,
            "time_range": "last_24h",  # Options: last_hour, last_24h, last_week, last_month, custom
            "custom_time_range": {
                "start": None,
                "end": None
            }
        }
        
        # Subscribe to agent-related events
        self._subscribe_to_events()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Agent Explorer Page initialized")
    
    def _subscribe_to_events(self):
        """Subscribe to agent-related events from the Real-Time Context Bus."""
        self.real_time_context_bus.subscribe(
            topic="agent.status.update",
            callback=self._handle_agent_status_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="agent.capability.update",
            callback=self._handle_agent_capability_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="agent.trust_score.update",
            callback=self._handle_agent_trust_score_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="agent.relationship.update",
            callback=self._handle_agent_relationship_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="agent.activity.update",
            callback=self._handle_agent_activity_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="agent.task.update",
            callback=self._handle_agent_task_update
        )
    
    def render(self) -> Dict[str, Any]:
        """
        Render the Agent Explorer Page.
        
        Returns:
            Dict containing the rendered page structure
        """
        # Adapt rendering based on device capabilities and context
        device_capabilities = self.device_adapter.get_capabilities()
        user_context = self.context_engine.get_current_context()
        
        # Determine layout based on device and context
        layout = self._determine_layout(device_capabilities, user_context)
        
        # Render main content based on view mode
        main_content = self._render_main_content(self.state["view_mode"])
        
        # Render layer avatars
        layer_avatars_render = self.layer_avatars.render(
            selected_layer="workflow_automation_layer"  # Focus on workflow layer for agents
        )
        
        # Render ambient veil
        ambient_veil_render = self.ambient_veil.render(
            context=user_context,
            agents=self.state["agents"]
        )
        
        # Construct the page structure
        page_structure = {
            "type": "page",
            "id": "agent_explorer_page",
            "title": "Agent Explorer",
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
            "title": "Agent Explorer",
            "subtitle": "Discover, explore, and interact with agents across the Industriverse ecosystem",
            "actions": [
                {
                    "type": "button",
                    "label": "Create Agent",
                    "icon": "plus",
                    "action": "create_agent"
                },
                {
                    "type": "button",
                    "label": "Import Agent",
                    "icon": "import",
                    "action": "import_agent"
                },
                {
                    "type": "button",
                    "label": "Export Selected Agent",
                    "icon": "export",
                    "action": "export_agent",
                    "disabled": self.state["selected_agent_id"] is None
                }
            ],
            "filters": [
                {
                    "type": "dropdown",
                    "label": "View Mode",
                    "options": [
                        {"value": "grid", "label": "Grid"},
                        {"value": "list", "label": "List"},
                        {"value": "spatial", "label": "Spatial"},
                        {"value": "detail", "label": "Detail"}
                    ],
                    "value": self.state["view_mode"],
                    "action": "change_view_mode"
                },
                {
                    "type": "dropdown",
                    "label": "Sort By",
                    "options": [
                        {"value": "name", "label": "Name"},
                        {"value": "type", "label": "Type"},
                        {"value": "status", "label": "Status"},
                        {"value": "trust_score", "label": "Trust Score"}
                    ],
                    "value": self.state["sort_by"],
                    "action": "change_sort_by"
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
                    "title": "Filters",
                    "items": [
                        {
                            "type": "dropdown",
                            "label": "Type",
                            "options": self._get_agent_type_options(),
                            "value": self.state["filter_criteria"]["type"] or "all",
                            "action": "filter_by_type"
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
                        },
                        {
                            "type": "dropdown",
                            "label": "Status",
                            "options": [
                                {"value": "all", "label": "All Statuses"},
                                {"value": "active", "label": "Active"},
                                {"value": "idle", "label": "Idle"},
                                {"value": "busy", "label": "Busy"},
                                {"value": "paused", "label": "Paused"},
                                {"value": "offline", "label": "Offline"}
                            ],
                            "value": self.state["filter_criteria"]["status"] or "all",
                            "action": "filter_by_status"
                        },
                        {
                            "type": "dropdown",
                            "label": "Layer",
                            "options": [
                                {"value": "all", "label": "All Layers"},
                                {"value": "data_layer", "label": "Data Layer"},
                                {"value": "core_ai_layer", "label": "Core AI Layer"},
                                {"value": "generative_layer", "label": "Generative Layer"},
                                {"value": "application_layer", "label": "Application Layer"},
                                {"value": "protocol_layer", "label": "Protocol Layer"},
                                {"value": "workflow_automation_layer", "label": "Workflow Automation Layer"},
                                {"value": "ui_ux_layer", "label": "UI/UX Layer"},
                                {"value": "security_compliance_layer", "label": "Security & Compliance Layer"}
                            ],
                            "value": self.state["filter_criteria"]["layer"] or "all",
                            "action": "filter_by_layer"
                        },
                        {
                            "type": "slider",
                            "label": "Trust Threshold",
                            "min": 0,
                            "max": 1,
                            "step": 0.1,
                            "value": self.state["filter_criteria"]["trust_threshold"],
                            "action": "filter_by_trust_threshold"
                        }
                    ]
                },
                {
                    "type": "section",
                    "title": "View Options",
                    "items": [
                        {
                            "type": "checkbox",
                            "label": "Show Trust Scores",
                            "checked": self.state["show_trust_scores"],
                            "action": "toggle_trust_scores"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Capabilities",
                            "checked": self.state["show_capabilities"],
                            "action": "toggle_capabilities"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Relationships",
                            "checked": self.state["show_relationships"],
                            "action": "toggle_relationships"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Activity",
                            "checked": self.state["show_activity"],
                            "action": "toggle_activity"
                        }
                    ]
                },
                {
                    "type": "section",
                    "title": "Time Range",
                    "items": [
                        {
                            "type": "radio_group",
                            "options": [
                                {"value": "last_hour", "label": "Last Hour"},
                                {"value": "last_24h", "label": "Last 24 Hours"},
                                {"value": "last_week", "label": "Last Week"},
                                {"value": "last_month", "label": "Last Month"},
                                {"value": "custom", "label": "Custom Range"}
                            ],
                            "value": self.state["time_range"],
                            "action": "change_time_range"
                        },
                        {
                            "type": "date_time_range",
                            "start": self.state["custom_time_range"]["start"],
                            "end": self.state["custom_time_range"]["end"],
                            "action": "set_custom_time_range",
                            "disabled": self.state["time_range"] != "custom"
                        }
                    ]
                }
            ]
        }
    
    def _get_agent_type_options(self) -> List[Dict[str, str]]:
        """
        Get agent type options for filtering.
        
        Returns:
            List of agent type options
        """
        # In a real implementation, this would fetch types from the Workflow Automation Layer
        # For now, return mock options
        return [
            {"value": "all", "label": "All Types"},
            {"value": "workflow_trigger", "label": "Workflow Trigger"},
            {"value": "workflow_contract_parser", "label": "Workflow Contract Parser"},
            {"value": "human_intervention", "label": "Human Intervention"},
            {"value": "capsule_workflow_controller", "label": "Capsule Workflow Controller"},
            {"value": "n8n_sync_bridge", "label": "n8n Sync Bridge"},
            {"value": "workflow_optimizer", "label": "Workflow Optimizer"},
            {"value": "workflow_feedback", "label": "Workflow Feedback"},
            {"value": "task_contract_versioning", "label": "Task Contract Versioning"},
            {"value": "distributed_workflow_splitter", "label": "Distributed Workflow Splitter"},
            {"value": "workflow_router", "label": "Workflow Router"},
            {"value": "workflow_fallback", "label": "Workflow Fallback"},
            {"value": "workflow_feedback_loop", "label": "Workflow Feedback Loop"},
            {"value": "workflow_chaos_tester", "label": "Workflow Chaos Tester"},
            {"value": "workflow_visualizer", "label": "Workflow Visualizer"},
            {"value": "workflow_negotiator", "label": "Workflow Negotiator"},
            {"value": "n8n_adapter", "label": "n8n Adapter"},
            {"value": "workflow_forensics", "label": "Workflow Forensics"},
            {"value": "capsule_memory_manager", "label": "Capsule Memory Manager"},
            {"value": "workflow_evolution", "label": "Workflow Evolution"}
        ]
    
    def _render_main_content(self, view_mode: str) -> Dict[str, Any]:
        """
        Render the main content area based on the selected view mode.
        
        Args:
            view_mode: The current view mode
            
        Returns:
            Dict containing the rendered main content structure
        """
        if view_mode == "grid":
            return self._render_grid_view()
        elif view_mode == "list":
            return self._render_list_view()
        elif view_mode == "spatial":
            return self._render_spatial_view()
        elif view_mode == "detail":
            return self._render_detail_view()
        else:
            return {
                "type": "message",
                "text": f"Invalid view mode: {view_mode}"
            }
    
    def _render_grid_view(self) -> Dict[str, Any]:
        """
        Render the grid view.
        
        Returns:
            Dict containing the rendered grid view structure
        """
        return {
            "type": "container",
            "layout": "grid",
            "grid_columns": 3,
            "children": [self._render_agent_card(agent) for agent in self.state["agents"]]
        }
    
    def _render_agent_card(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render an agent card for the grid view.
        
        Args:
            agent: Agent data
            
        Returns:
            Dict containing the rendered agent card structure
        """
        # Determine status color
        status_colors = {
            "active": "green",
            "idle": "blue",
            "busy": "orange",
            "paused": "yellow",
            "offline": "gray"
        }
        status_color = status_colors.get(agent.get("status", "offline"), "gray")
        
        # Render trust ribbon if enabled
        trust_ribbon_render = None
        if self.state["show_trust_scores"]:
            trust_ribbon_render = self.trust_ribbon.render(
                trust_score=agent.get("trust_score", 0),
                verification_status=agent.get("verification_status", "unverified")
            )
        
        # Render capabilities if enabled
        capabilities_render = None
        if self.state["show_capabilities"]:
            capabilities_render = {
                "type": "capability_badges",
                "capabilities": agent.get("capabilities", []),
                "max_display": 3
            }
        
        # Render activity if enabled
        activity_render = None
        if self.state["show_activity"]:
            activity_render = {
                "type": "activity_indicator",
                "activity": agent.get("recent_activity", []),
                "max_display": 1
            }
        
        return {
            "type": "card",
            "id": f"agent_{agent["id"]}",
            "title": agent.get("name", "Unnamed Agent"),
            "subtitle": agent.get("description", ""),
            "avatar": {
                "type": "agent_avatar",
                "agent_id": agent["id"],
                "size": "medium"
            },
            "status": {
                "label": agent.get("status", "offline"),
                "color": status_color
            },
            "content": [
                trust_ribbon_render,
                {
                    "type": "agent_type_badge",
                    "type": agent.get("type", "unknown")
                },
                {
                    "type": "layer_badge",
                    "layer": agent.get("layer", "unknown")
                },
                capabilities_render,
                activity_render
            ],
            "actions": [
                {
                    "type": "button",
                    "label": "View Details",
                    "icon": "details",
                    "action": "select_agent",
                    "params": {"agent_id": agent["id"]}
                },
                {
                    "type": "button",
                    "label": "Interact",
                    "icon": "interact",
                    "action": "interact_with_agent",
                    "params": {"agent_id": agent["id"]},
                    "disabled": agent.get("status") == "offline"
                }
            ],
            "selected": agent["id"] == self.state["selected_agent_id"]
        }
    
    def _render_list_view(self) -> Dict[str, Any]:
        """
        Render the list view.
        
        Returns:
            Dict containing the rendered list view structure
        """
        return {
            "type": "container",
            "layout": "list",
            "children": [self._render_agent_list_item(agent) for agent in self.state["agents"]]
        }
    
    def _render_agent_list_item(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render an agent list item for the list view.
        
        Args:
            agent: Agent data
            
        Returns:
            Dict containing the rendered agent list item structure
        """
        # Determine status color
        status_colors = {
            "active": "green",
            "idle": "blue",
            "busy": "orange",
            "paused": "yellow",
            "offline": "gray"
        }
        status_color = status_colors.get(agent.get("status", "offline"), "gray")
        
        # Render trust ribbon if enabled
        trust_ribbon_render = None
        if self.state["show_trust_scores"]:
            trust_ribbon_render = self.trust_ribbon.render(
                trust_score=agent.get("trust_score", 0),
                verification_status=agent.get("verification_status", "unverified"),
                compact=True
            )
        
        # Render capabilities if enabled
        capabilities_render = None
        if self.state["show_capabilities"]:
            capabilities_render = {
                "type": "capability_badges_compact",
                "capabilities": agent.get("capabilities", []),
                "max_display": 2
            }
        
        # Render activity if enabled
        activity_render = None
        if self.state["show_activity"]:
            activity_render = {
                "type": "activity_indicator_compact",
                "activity": agent.get("recent_activity", []),
                "max_display": 1
            }
        
        return {
            "type": "list_item",
            "id": f"agent_{agent["id"]}",
            "title": agent.get("name", "Unnamed Agent"),
            "subtitle": agent.get("description", ""),
            "avatar": {
                "type": "agent_avatar",
                "agent_id": agent["id"],
                "size": "small"
            },
            "status": {
                "label": agent.get("status", "offline"),
                "color": status_color
            },
            "metadata": [
                {
                    "type": "text",
                    "label": "Type",
                    "value": agent.get("type", "Unknown")
                },
                {
                    "type": "text",
                    "label": "Layer",
                    "value": agent.get("layer", "Unknown")
                },
                {
                    "type": "text",
                    "label": "Domain",
                    "value": agent.get("domain", "General")
                },
                trust_ribbon_render,
                capabilities_render,
                activity_render
            ],
            "actions": [
                {
                    "type": "button",
                    "label": "View Details",
                    "icon": "details",
                    "action": "select_agent",
                    "params": {"agent_id": agent["id"]}
                },
                {
                    "type": "button",
                    "label": "Interact",
                    "icon": "interact",
                    "action": "interact_with_agent",
                    "params": {"agent_id": agent["id"]},
                    "disabled": agent.get("status") == "offline"
                }
            ],
            "selected": agent["id"] == self.state["selected_agent_id"]
        }
    
    def _render_spatial_view(self) -> Dict[str, Any]:
        """
        Render the spatial view.
        
        Returns:
            Dict containing the rendered spatial view structure
        """
        # Use the spatial canvas to render the agent spatial view
        return self.spatial_canvas.render(
            entities=self.state["agents"],
            entity_type="agent",
            show_relationships=self.state["show_relationships"],
            show_trust_scores=self.state["show_trust_scores"],
            show_activity=self.state["show_activity"],
            selected_entity_id=self.state["selected_agent_id"]
        )
    
    def _render_detail_view(self) -> Dict[str, Any]:
        """
        Render the detail view.
        
        Returns:
            Dict containing the rendered detail view structure
        """
        selected_agent = self._get_selected_agent()
        
        if not selected_agent:
            return {
                "type": "message",
                "text": "Select an agent to view details."
            }
        
        # Render protocol visualization if relationships are enabled
        protocol_visualization = None
        if self.state["show_relationships"]:
            protocol_visualization = self.protocol_visualizer.render(
                entity_id=selected_agent["id"],
                entity_type="agent",
                show_trust_paths=self.state["show_trust_scores"]
            )
        
        # Render workflow visualization if agent is workflow-related
        workflow_visualization = None
        if selected_agent.get("type", "").startswith("workflow_"):
            workflow_visualization = self.workflow_canvas.render(
                workflow_id=selected_agent.get("associated_workflow_id"),
                agent_id=selected_agent["id"],
                show_trust_scores=self.state["show_trust_scores"]
            )
        
        # Render activity visualization if enabled
        activity_visualization = None
        if self.state["show_activity"]:
            activity_visualization = self.data_visualization.render(
                entity_id=selected_agent["id"],
                entity_type="agent",
                time_range=self._get_time_range(),
                metrics=["activity", "performance", "trust_score"]
            )
        
        return {
            "type": "container",
            "layout": "split",
            "split_direction": "vertical",
            "children": [
                {
                    "type": "container",
                    "title": "Agent Details",
                    "layout": "split",
                    "split_direction": "horizontal",
                    "children": [
                        {
                            "type": "container",
                            "flex": 1,
                            "children": [
                                {
                                    "type": "agent_profile",
                                    "agent": selected_agent,
                                    "show_trust_scores": self.state["show_trust_scores"],
                                    "show_capabilities": self.state["show_capabilities"]
                                }
                            ]
                        },
                        {
                            "type": "container",
                            "flex": 2,
                            "children": [
                                {
                                    "type": "tabs",
                                    "tabs": [
                                        {
                                            "label": "Overview",
                                            "content": self._render_overview_tab(selected_agent)
                                        },
                                        {
                                            "label": "Capabilities",
                                            "content": self._render_capabilities_tab(selected_agent)
                                        },
                                        {
                                            "label": "Activity",
                                            "content": activity_visualization or {
                                                "type": "message",
                                                "text": "Activity visualization is disabled."
                                            }
                                        },
                                        {
                                            "label": "Workflow",
                                            "content": workflow_visualization or {
                                                "type": "message",
                                                "text": "No workflow visualization available for this agent."
                                            }
                                        },
                                        {
                                            "label": "Configuration",
                                            "content": self._render_configuration_tab(selected_agent)
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                protocol_visualization
            ]
        }
    
    def _get_selected_agent(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected agent data.
        
        Returns:
            Dict containing selected agent data, or None if no agent is selected
        """
        if not self.state["selected_agent_id"]:
            return None
        
        for agent in self.state["agents"]:
            if agent["id"] == self.state["selected_agent_id"]:
                return agent
        
        return None
    
    def _get_time_range(self) -> Dict[str, Any]:
        """
        Get the current time range for activity visualization.
        
        Returns:
            Dict containing time range information
        """
        if self.state["time_range"] == "custom":
            return {
                "type": "custom",
                "start": self.state["custom_time_range"]["start"],
                "end": self.state["custom_time_range"]["end"]
            }
        else:
            return {
                "type": self.state["time_range"]
            }
    
    def _render_overview_tab(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the overview tab for the detail view.
        
        Args:
            agent: Agent data
            
        Returns:
            Dict containing the rendered overview tab structure
        """
        return {
            "type": "container",
            "layout": "grid",
            "children": [
                {
                    "type": "widget",
                    "title": "Basic Information",
                    "position": {"row": 0, "col": 0, "width": 6, "height": 2},
                    "content": {
                        "type": "property_list",
                        "properties": [
                            {"label": "Name", "value": agent.get("name", "")},
                            {"label": "Type", "value": agent.get("type", "")},
                            {"label": "Layer", "value": agent.get("layer", "")},
                            {"label": "Domain", "value": agent.get("domain", "")},
                            {"label": "Status", "value": agent.get("status", "")},
                            {"label": "Version", "value": agent.get("version", "")},
                            {"label": "Created", "value": agent.get("created", "")},
                            {"label": "Last Active", "value": agent.get("last_active", "")}
                        ]
                    }
                },
                {
                    "type": "widget",
                    "title": "Description",
                    "position": {"row": 0, "col": 6, "width": 6, "height": 2},
                    "content": {
                        "type": "markdown",
                        "text": agent.get("description", "No description available.")
                    }
                },
                {
                    "type": "widget",
                    "title": "Performance Metrics",
                    "position": {"row": 2, "col": 0, "width": 12, "height": 3},
                    "content": {
                        "type": "metrics_dashboard",
                        "metrics": agent.get("performance_metrics", []),
                        "show_trends": True,
                        "show_thresholds": True
                    }
                },
                {
                    "type": "widget",
                    "title": "Related Agents",
                    "position": {"row": 5, "col": 0, "width": 6, "height": 3},
                    "content": {
                        "type": "related_entities",
                        "entities": agent.get("related_agents", []),
                        "entity_type": "agent",
                        "action": "select_agent"
                    }
                },
                {
                    "type": "widget",
                    "title": "Related Digital Twins",
                    "position": {"row": 5, "col": 6, "width": 6, "height": 3},
                    "content": {
                        "type": "related_entities",
                        "entities": agent.get("related_twins", []),
                        "entity_type": "digital_twin",
                        "action": "navigate_to_twin"
                    }
                }
            ]
        }
    
    def _render_capabilities_tab(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the capabilities tab for the detail view.
        
        Args:
            agent: Agent data
            
        Returns:
            Dict containing the rendered capabilities tab structure
        """
        capabilities = agent.get("capabilities", [])
        
        if not capabilities:
            return {
                "type": "message",
                "text": "No capabilities defined for this agent.",
                "severity": "info"
            }
        
        return {
            "type": "container",
            "layout": "vertical",
            "children": [
                {
                    "type": "capability_list",
                    "capabilities": capabilities,
                    "show_trust_thresholds": self.state["show_trust_scores"]
                }
            ]
        }
    
    def _render_configuration_tab(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the configuration tab for the detail view.
        
        Args:
            agent: Agent data
            
        Returns:
            Dict containing the rendered configuration tab structure
        """
        configuration = agent.get("configuration", {})
        
        return {
            "type": "container",
            "layout": "form",
            "children": [
                {
                    "type": "form",
                    "fields": [
                        {
                            "type": "text_input",
                            "label": "Name",
                            "value": agent.get("name", ""),
                            "name": "name"
                        },
                        {
                            "type": "text_area",
                            "label": "Description",
                            "value": agent.get("description", ""),
                            "name": "description"
                        },
                        {
                            "type": "dropdown",
                            "label": "Domain",
                            "options": [
                                {"value": "manufacturing", "label": "Manufacturing"},
                                {"value": "logistics", "label": "Logistics"},
                                {"value": "energy", "label": "Energy"},
                                {"value": "retail", "label": "Retail"},
                                {"value": "general", "label": "General"}
                            ],
                            "value": agent.get("domain", "general"),
                            "name": "domain"
                        }
                    ],
                    "sections": [
                        {
                            "title": "Advanced Configuration",
                            "fields": [
                                {
                                    "type": field_config.get("type", "text_input"),
                                    "label": field_config.get("label", ""),
                                    "value": configuration.get(field_name, ""),
                                    "name": field_name,
                                    "options": field_config.get("options", [])
                                } for field_name, field_config in agent.get("configuration_schema", {}).items()
                            ]
                        }
                    ],
                    "actions": [
                        {
                            "type": "button",
                            "label": "Save Configuration",
                            "action": "save_agent_configuration",
                            "params": {"agent_id": agent["id"]}
                        },
                        {
                            "type": "button",
                            "label": "Reset to Defaults",
                            "action": "reset_agent_configuration",
                            "params": {"agent_id": agent["id"]}
                        }
                    ]
                }
            ]
        }
    
    def _get_available_actions(self) -> Dict[str, Any]:
        """
        Get available actions for the page.
        
        Returns:
            Dict containing available actions and their handlers
        """
        return {
            "create_agent": self.create_agent,
            "import_agent": self.import_agent,
            "export_agent": self.export_agent,
            "change_view_mode": self.change_view_mode,
            "change_sort_by": self.change_sort_by,
            "filter_by_type": self.filter_by_type,
            "filter_by_domain": self.filter_by_domain,
            "filter_by_status": self.filter_by_status,
            "filter_by_layer": self.filter_by_layer,
            "filter_by_trust_threshold": self.filter_by_trust_threshold,
            "toggle_trust_scores": self.toggle_trust_scores,
            "toggle_capabilities": self.toggle_capabilities,
            "toggle_relationships": self.toggle_relationships,
            "toggle_activity": self.toggle_activity,
            "change_time_range": self.change_time_range,
            "set_custom_time_range": self.set_custom_time_range,
            "select_agent": self.select_agent,
            "interact_with_agent": self.interact_with_agent,
            "save_agent_configuration": self.save_agent_configuration,
            "reset_agent_configuration": self.reset_agent_configuration,
            "navigate_to_twin": self.navigate_to_twin
        }
    
    # Event handlers
    def _handle_agent_status_update(self, event: Dict[str, Any]):
        """
        Handle agent status update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        agent_id = event.get("agent_id")
        new_status = event.get("status")
        
        if not agent_id or not new_status:
            return
        
        # Update agent status in agents list
        for agent in self.state["agents"]:
            if agent["id"] == agent_id:
                agent["status"] = new_status
                agent["last_active"] = event.get("timestamp", "Unknown")
                break
    
    def _handle_agent_capability_update(self, event: Dict[str, Any]):
        """
        Handle agent capability update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        agent_id = event.get("agent_id")
        capabilities = event.get("capabilities")
        
        if not agent_id or not capabilities:
            return
        
        # Update agent capabilities in agents list
        for agent in self.state["agents"]:
            if agent["id"] == agent_id:
                agent["capabilities"] = capabilities
                break
    
    def _handle_agent_trust_score_update(self, event: Dict[str, Any]):
        """
        Handle agent trust score update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        agent_id = event.get("agent_id")
        trust_score = event.get("trust_score")
        verification_status = event.get("verification_status")
        
        if not agent_id or trust_score is None:
            return
        
        # Update agent trust score in agents list
        for agent in self.state["agents"]:
            if agent["id"] == agent_id:
                agent["trust_score"] = trust_score
                if verification_status:
                    agent["verification_status"] = verification_status
                break
    
    def _handle_agent_relationship_update(self, event: Dict[str, Any]):
        """
        Handle agent relationship update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        agent_id = event.get("agent_id")
        related_agents = event.get("related_agents")
        related_twins = event.get("related_twins")
        
        if not agent_id:
            return
        
        # Update agent relationships in agents list
        for agent in self.state["agents"]:
            if agent["id"] == agent_id:
                if related_agents:
                    agent["related_agents"] = related_agents
                if related_twins:
                    agent["related_twins"] = related_twins
                break
    
    def _handle_agent_activity_update(self, event: Dict[str, Any]):
        """
        Handle agent activity update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        agent_id = event.get("agent_id")
        activity = event.get("activity")
        
        if not agent_id or not activity:
            return
        
        # Update agent activity in agents list
        for agent in self.state["agents"]:
            if agent["id"] == agent_id:
                if "recent_activity" not in agent:
                    agent["recent_activity"] = []
                
                agent["recent_activity"].insert(0, activity)
                
                # Limit recent activity list to 10 items
                if len(agent["recent_activity"]) > 10:
                    agent["recent_activity"] = agent["recent_activity"][:10]
                
                agent["last_active"] = event.get("timestamp", "Unknown")
                break
    
    def _handle_agent_task_update(self, event: Dict[str, Any]):
        """
        Handle agent task update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        agent_id = event.get("agent_id")
        task = event.get("task")
        
        if not agent_id or not task:
            return
        
        # Update agent tasks in agents list
        for agent in self.state["agents"]:
            if agent["id"] == agent_id:
                if "tasks" not in agent:
                    agent["tasks"] = []
                
                # Check if task already exists
                task_exists = False
                for i, existing_task in enumerate(agent["tasks"]):
                    if existing_task["id"] == task["id"]:
                        # Update existing task
                        agent["tasks"][i] = task
                        task_exists = True
                        break
                
                # Add new task if it doesn't exist
                if not task_exists:
                    agent["tasks"].append(task)
                
                # Update performance metrics if provided
                if "performance_metrics" in event:
                    agent["performance_metrics"] = event["performance_metrics"]
                
                agent["last_active"] = event.get("timestamp", "Unknown")
                break
    
    # Action handlers
    def create_agent(self, params: Dict[str, Any] = None):
        """
        Create a new agent.
        
        Args:
            params: Optional parameters for agent creation
        """
        # Request agent creation
        self.real_time_context_bus.publish(
            topic="agent.create.request",
            data={
                "source": "ui_ux_layer",
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested agent creation with params: {params}")
    
    def import_agent(self, params: Dict[str, Any] = None):
        """
        Import an agent.
        
        Args:
            params: Optional parameters for agent import
        """
        # Request agent import
        self.real_time_context_bus.publish(
            topic="agent.import.request",
            data={
                "source": "ui_ux_layer",
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested agent import with params: {params}")
    
    def export_agent(self, params: Dict[str, Any] = None):
        """
        Export an agent.
        
        Args:
            params: Optional parameters for agent export
        """
        agent_id = params.get("agent_id") if params else self.state["selected_agent_id"]
        
        if not agent_id:
            self.logger.warning("Cannot export agent: No agent selected")
            return
        
        # Request agent export
        self.real_time_context_bus.publish(
            topic="agent.export.request",
            data={
                "source": "ui_ux_layer",
                "agent_id": agent_id,
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested export of agent {agent_id}")
    
    def change_view_mode(self, params: Dict[str, Any]):
        """
        Change the view mode.
        
        Args:
            params: Parameters containing the view mode value
        """
        view_mode = params.get("value")
        if view_mode:
            self.state["view_mode"] = view_mode
    
    def change_sort_by(self, params: Dict[str, Any]):
        """
        Change the sort criteria.
        
        Args:
            params: Parameters containing the sort criteria value
        """
        sort_by = params.get("value")
        if sort_by:
            self.state["sort_by"] = sort_by
            self._apply_sort()
    
    def _apply_sort(self):
        """Apply current sort criteria to the agents list."""
        sort_key = self.state["sort_by"]
        
        if sort_key == "name":
            self.state["agents"].sort(key=lambda a: a.get("name", "").lower())
        elif sort_key == "type":
            self.state["agents"].sort(key=lambda a: a.get("type", "").lower())
        elif sort_key == "status":
            # Sort by status priority: active, busy, idle, paused, offline
            status_priority = {"active": 0, "busy": 1, "idle": 2, "paused": 3, "offline": 4}
            self.state["agents"].sort(key=lambda a: status_priority.get(a.get("status", "offline"), 5))
        elif sort_key == "trust_score":
            self.state["agents"].sort(key=lambda a: a.get("trust_score", 0), reverse=True)
    
    def filter_by_type(self, params: Dict[str, Any]):
        """
        Filter agents by type.
        
        Args:
            params: Parameters containing the type filter value
        """
        agent_type = params.get("value")
        if agent_type:
            self.state["filter_criteria"]["type"] = agent_type if agent_type != "all" else None
            self._apply_filters()
    
    def filter_by_domain(self, params: Dict[str, Any]):
        """
        Filter agents by domain.
        
        Args:
            params: Parameters containing the domain filter value
        """
        domain = params.get("value")
        if domain:
            self.state["filter_criteria"]["domain"] = domain if domain != "all" else None
            self._apply_filters()
    
    def filter_by_status(self, params: Dict[str, Any]):
        """
        Filter agents by status.
        
        Args:
            params: Parameters containing the status filter value
        """
        status = params.get("value")
        if status:
            self.state["filter_criteria"]["status"] = status if status != "all" else None
            self._apply_filters()
    
    def filter_by_layer(self, params: Dict[str, Any]):
        """
        Filter agents by layer.
        
        Args:
            params: Parameters containing the layer filter value
        """
        layer = params.get("value")
        if layer:
            self.state["filter_criteria"]["layer"] = layer if layer != "all" else None
            self._apply_filters()
    
    def filter_by_trust_threshold(self, params: Dict[str, Any]):
        """
        Filter agents by trust threshold.
        
        Args:
            params: Parameters containing the trust threshold value
        """
        trust_threshold = params.get("value")
        if trust_threshold is not None:
            self.state["filter_criteria"]["trust_threshold"] = trust_threshold
            self._apply_filters()
    
    def _apply_filters(self):
        """Apply current filters to fetch updated agent data."""
        # Request filtered agents
        self.real_time_context_bus.publish(
            topic="agent.list.request",
            data={
                "source": "ui_ux_layer",
                "filter_criteria": self.state["filter_criteria"]
            }
        )
        
        self.logger.info(f"Applied agent filters: {self.state["filter_criteria"]}")
    
    def toggle_trust_scores(self, params: Dict[str, Any]):
        """
        Toggle display of trust scores.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_trust_scores = params.get("checked")
        if show_trust_scores is not None:
            self.state["show_trust_scores"] = show_trust_scores
    
    def toggle_capabilities(self, params: Dict[str, Any]):
        """
        Toggle display of capabilities.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_capabilities = params.get("checked")
        if show_capabilities is not None:
            self.state["show_capabilities"] = show_capabilities
    
    def toggle_relationships(self, params: Dict[str, Any]):
        """
        Toggle display of relationships.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_relationships = params.get("checked")
        if show_relationships is not None:
            self.state["show_relationships"] = show_relationships
    
    def toggle_activity(self, params: Dict[str, Any]):
        """
        Toggle display of activity.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_activity = params.get("checked")
        if show_activity is not None:
            self.state["show_activity"] = show_activity
    
    def change_time_range(self, params: Dict[str, Any]):
        """
        Change the time range for activity visualization.
        
        Args:
            params: Parameters containing the time range value
        """
        time_range = params.get("value")
        if time_range:
            self.state["time_range"] = time_range
    
    def set_custom_time_range(self, params: Dict[str, Any]):
        """
        Set a custom time range for activity visualization.
        
        Args:
            params: Parameters containing the custom time range values
        """
        start = params.get("start")
        end = params.get("end")
        
        if start and end:
            self.state["custom_time_range"]["start"] = start
            self.state["custom_time_range"]["end"] = end
            self.state["time_range"] = "custom"
    
    def select_agent(self, params: Dict[str, Any]):
        """
        Select an agent.
        
        Args:
            params: Parameters containing the agent ID
        """
        agent_id = params.get("agent_id")
        if agent_id:
            self.state["selected_agent_id"] = agent_id
            
            # If in grid or list view, switch to detail view
            if self.state["view_mode"] in ["grid", "list"]:
                self.state["view_mode"] = "detail"
            
            # Request detailed agent data
            self.real_time_context_bus.publish(
                topic="agent.detail.request",
                data={
                    "source": "ui_ux_layer",
                    "agent_id": agent_id
                }
            )
            
            self.logger.info(f"Selected agent {agent_id}")
    
    def interact_with_agent(self, params: Dict[str, Any]):
        """
        Open the interaction interface for an agent.
        
        Args:
            params: Parameters containing the agent ID
        """
        agent_id = params.get("agent_id")
        if agent_id:
            # Request agent interaction
            self.real_time_context_bus.publish(
                topic="agent.interaction.request",
                data={
                    "source": "ui_ux_layer",
                    "agent_id": agent_id,
                    "params": params or {}
                }
            )
            
            self.logger.info(f"Requested interaction with agent {agent_id}")
    
    def save_agent_configuration(self, params: Dict[str, Any]):
        """
        Save the configuration for an agent.
        
        Args:
            params: Parameters containing the agent ID and configuration data
        """
        agent_id = params.get("agent_id")
        configuration = params.get("configuration")
        
        if not agent_id or not configuration:
            self.logger.warning("Cannot save configuration: Missing agent ID or configuration data")
            return
        
        # Request configuration save
        self.real_time_context_bus.publish(
            topic="agent.configuration.save.request",
            data={
                "source": "ui_ux_layer",
                "agent_id": agent_id,
                "configuration": configuration
            }
        )
        
        self.logger.info(f"Requested save of configuration for agent {agent_id}")
    
    def reset_agent_configuration(self, params: Dict[str, Any]):
        """
        Reset the configuration for an agent to defaults.
        
        Args:
            params: Parameters containing the agent ID
        """
        agent_id = params.get("agent_id")
        
        if not agent_id:
            self.logger.warning("Cannot reset configuration: Missing agent ID")
            return
        
        # Request configuration reset
        self.real_time_context_bus.publish(
            topic="agent.configuration.reset.request",
            data={
                "source": "ui_ux_layer",
                "agent_id": agent_id
            }
        )
        
        self.logger.info(f"Requested reset of configuration for agent {agent_id}")
    
    def navigate_to_twin(self, params: Dict[str, Any]):
        """
        Navigate to the digital twin explorer page for a specific digital twin.
        
        Args:
            params: Parameters containing the digital twin ID
        """
        twin_id = params.get("twin_id")
        
        if not twin_id:
            self.logger.warning("Cannot navigate to digital twin: Missing twin ID")
            return
        
        # Request navigation to digital twin explorer page
        self.real_time_context_bus.publish(
            topic="ui.navigate.request",
            data={
                "source": "ui_ux_layer",
                "target_page": "digital_twin_explorer",
                "params": {
                    "twin_id": twin_id
                }
            }
        )
        
        self.logger.info(f"Requested navigation to digital twin explorer for twin {twin_id}")
