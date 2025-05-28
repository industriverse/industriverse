"""
Digital Twin Explorer Page - The digital twin explorer page component for the Industriverse UI/UX Layer.

This component provides a comprehensive interface for discovering, exploring, and interacting
with digital twins across the Industriverse ecosystem. It visualizes digital twin states,
relationships, and historical data, enabling users to monitor and control physical assets
through their digital representations.

Features:
- Digital twin discovery and filtering by type, domain, and status
- Detailed digital twin profiles with real-time state visualization
- Historical data analysis and trend visualization
- Spatial visualization of digital twin relationships and physical locations
- Trust-weighted control interfaces with verification mechanisms
- Integration with Layer Avatars for personified digital twin representation
- Protocol-native visualization of digital twin communication and activities

The component uses the Universal Skin architecture to adapt its presentation based on
device capabilities, user role, and context, while maintaining protocol-native visualization
of the underlying digital twin ecosystem.
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
from components.digital_twin_viewer.digital_twin_viewer import DigitalTwinViewer
from components.data_visualization.data_visualization import DataVisualization

class DigitalTwinExplorerPage:
    """
    Digital Twin Explorer Page component for the Industriverse UI/UX Layer.
    
    This page provides a comprehensive interface for discovering, exploring, and interacting
    with digital twins across the Industriverse ecosystem.
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
        Initialize the Digital Twin Explorer Page component.
        
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
        
        self.digital_twin_viewer = DigitalTwinViewer(
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
            "selected_twin_id": None,
            "twins": [],
            "filter_criteria": {
                "type": None,  # e.g., machine, sensor, system
                "domain": None,  # e.g., manufacturing, logistics
                "status": None,  # e.g., online, offline, warning, error
                "trust_threshold": 0.7
            },
            "view_mode": "grid",  # Options: grid, list, spatial, detail
            "sort_by": "name",  # Options: name, type, status, last_updated
            "show_trust_scores": True,
            "show_real_time_data": True,
            "show_relationships": True,
            "show_historical_data": True,
            "time_range": "last_24h",  # Options: last_hour, last_24h, last_week, last_month, custom
            "custom_time_range": {
                "start": None,
                "end": None
            }
        }
        
        # Subscribe to digital twin-related events
        self._subscribe_to_events()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Digital Twin Explorer Page initialized")
    
    def _subscribe_to_events(self):
        """Subscribe to digital twin-related events from the Real-Time Context Bus."""
        self.real_time_context_bus.subscribe(
            topic="digital_twin.status.update",
            callback=self._handle_twin_status_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="digital_twin.data.update",
            callback=self._handle_twin_data_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="digital_twin.trust_score.update",
            callback=self._handle_twin_trust_score_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="digital_twin.relationship.update",
            callback=self._handle_twin_relationship_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="digital_twin.command.response",
            callback=self._handle_twin_command_response
        )
    
    def render(self) -> Dict[str, Any]:
        """
        Render the Digital Twin Explorer Page.
        
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
            selected_layer="data_layer"  # Focus on data layer for digital twins
        )
        
        # Render ambient veil
        ambient_veil_render = self.ambient_veil.render(
            context=user_context,
            twins=self.state["twins"]
        )
        
        # Construct the page structure
        page_structure = {
            "type": "page",
            "id": "digital_twin_explorer_page",
            "title": "Digital Twin Explorer",
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
            "title": "Digital Twin Explorer",
            "subtitle": "Discover, explore, and interact with digital twins across the Industriverse ecosystem",
            "actions": [
                {
                    "type": "button",
                    "label": "Create Digital Twin",
                    "icon": "plus",
                    "action": "create_twin"
                },
                {
                    "type": "button",
                    "label": "Import Digital Twin",
                    "icon": "import",
                    "action": "import_twin"
                },
                {
                    "type": "button",
                    "label": "Export Selected Twin",
                    "icon": "export",
                    "action": "export_twin",
                    "disabled": self.state["selected_twin_id"] is None
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
                        {"value": "last_updated", "label": "Last Updated"}
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
                            "options": self._get_twin_type_options(),
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
                                {"value": "online", "label": "Online"},
                                {"value": "offline", "label": "Offline"},
                                {"value": "warning", "label": "Warning"},
                                {"value": "error", "label": "Error"}
                            ],
                            "value": self.state["filter_criteria"]["status"] or "all",
                            "action": "filter_by_status"
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
                            "label": "Show Real-Time Data",
                            "checked": self.state["show_real_time_data"],
                            "action": "toggle_real_time_data"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Relationships",
                            "checked": self.state["show_relationships"],
                            "action": "toggle_relationships"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Historical Data",
                            "checked": self.state["show_historical_data"],
                            "action": "toggle_historical_data"
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
    
    def _get_twin_type_options(self) -> List[Dict[str, str]]:
        """
        Get digital twin type options for filtering.
        
        Returns:
            List of digital twin type options
        """
        # In a real implementation, this would fetch types from the Data Layer
        # For now, return mock options
        return [
            {"value": "all", "label": "All Types"},
            {"value": "machine", "label": "Machine"},
            {"value": "sensor", "label": "Sensor"},
            {"value": "system", "label": "System"},
            {"value": "process", "label": "Process"},
            {"value": "facility", "label": "Facility"},
            {"value": "product", "label": "Product"},
            {"value": "vehicle", "label": "Vehicle"}
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
            "children": [self._render_twin_card(twin) for twin in self.state["twins"]]
        }
    
    def _render_twin_card(self, twin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a digital twin card for the grid view.
        
        Args:
            twin: Digital twin data
            
        Returns:
            Dict containing the rendered digital twin card structure
        """
        # Determine status color
        status_colors = {
            "online": "green",
            "offline": "gray",
            "warning": "yellow",
            "error": "red"
        }
        status_color = status_colors.get(twin.get("status", "offline"), "gray")
        
        # Render trust ribbon if enabled
        trust_ribbon_render = None
        if self.state["show_trust_scores"]:
            trust_ribbon_render = self.trust_ribbon.render(
                trust_score=twin.get("trust_score", 0),
                verification_status=twin.get("verification_status", "unverified")
            )
        
        # Render real-time data if enabled
        real_time_data_render = None
        if self.state["show_real_time_data"]:
            real_time_data_render = {
                "type": "real_time_metrics",
                "metrics": twin.get("metrics", []),
                "max_display": 3,
                "show_trends": True
            }
        
        return {
            "type": "card",
            "id": f"twin_{twin["id"]}",
            "title": twin.get("name", "Unnamed Twin"),
            "subtitle": twin.get("description", ""),
            "avatar": {
                "type": "twin_avatar",
                "twin_id": twin["id"],
                "size": "medium"
            },
            "status": {
                "label": twin.get("status", "offline"),
                "color": status_color
            },
            "content": [
                trust_ribbon_render,
                {
                    "type": "twin_type_badge",
                    "type": twin.get("type", "unknown")
                },
                real_time_data_render
            ],
            "actions": [
                {
                    "type": "button",
                    "label": "View Details",
                    "icon": "details",
                    "action": "select_twin",
                    "params": {"twin_id": twin["id"]}
                },
                {
                    "type": "button",
                    "label": "Control",
                    "icon": "control",
                    "action": "control_twin",
                    "params": {"twin_id": twin["id"]},
                    "disabled": twin.get("status") != "online"
                }
            ],
            "selected": twin["id"] == self.state["selected_twin_id"]
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
            "children": [self._render_twin_list_item(twin) for twin in self.state["twins"]]
        }
    
    def _render_twin_list_item(self, twin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a digital twin list item for the list view.
        
        Args:
            twin: Digital twin data
            
        Returns:
            Dict containing the rendered digital twin list item structure
        """
        # Determine status color
        status_colors = {
            "online": "green",
            "offline": "gray",
            "warning": "yellow",
            "error": "red"
        }
        status_color = status_colors.get(twin.get("status", "offline"), "gray")
        
        # Render trust ribbon if enabled
        trust_ribbon_render = None
        if self.state["show_trust_scores"]:
            trust_ribbon_render = self.trust_ribbon.render(
                trust_score=twin.get("trust_score", 0),
                verification_status=twin.get("verification_status", "unverified"),
                compact=True
            )
        
        # Render real-time data if enabled
        real_time_data_render = None
        if self.state["show_real_time_data"]:
            real_time_data_render = {
                "type": "real_time_metrics_compact",
                "metrics": twin.get("metrics", []),
                "max_display": 2,
                "show_trends": True
            }
        
        return {
            "type": "list_item",
            "id": f"twin_{twin["id"]}",
            "title": twin.get("name", "Unnamed Twin"),
            "subtitle": twin.get("description", ""),
            "avatar": {
                "type": "twin_avatar",
                "twin_id": twin["id"],
                "size": "small"
            },
            "status": {
                "label": twin.get("status", "offline"),
                "color": status_color
            },
            "metadata": [
                {
                    "type": "text",
                    "label": "Type",
                    "value": twin.get("type", "Unknown")
                },
                {
                    "type": "text",
                    "label": "Domain",
                    "value": twin.get("domain", "General")
                },
                {
                    "type": "text",
                    "label": "Last Updated",
                    "value": twin.get("last_updated", "Unknown")
                },
                trust_ribbon_render,
                real_time_data_render
            ],
            "actions": [
                {
                    "type": "button",
                    "label": "View Details",
                    "icon": "details",
                    "action": "select_twin",
                    "params": {"twin_id": twin["id"]}
                },
                {
                    "type": "button",
                    "label": "Control",
                    "icon": "control",
                    "action": "control_twin",
                    "params": {"twin_id": twin["id"]},
                    "disabled": twin.get("status") != "online"
                }
            ],
            "selected": twin["id"] == self.state["selected_twin_id"]
        }
    
    def _render_spatial_view(self) -> Dict[str, Any]:
        """
        Render the spatial view.
        
        Returns:
            Dict containing the rendered spatial view structure
        """
        # Use the spatial canvas to render the digital twin spatial view
        return self.spatial_canvas.render(
            entities=self.state["twins"],
            entity_type="digital_twin",
            show_relationships=self.state["show_relationships"],
            show_trust_scores=self.state["show_trust_scores"],
            show_real_time_data=self.state["show_real_time_data"],
            selected_entity_id=self.state["selected_twin_id"]
        )
    
    def _render_detail_view(self) -> Dict[str, Any]:
        """
        Render the detail view.
        
        Returns:
            Dict containing the rendered detail view structure
        """
        selected_twin = self._get_selected_twin()
        
        if not selected_twin:
            return {
                "type": "message",
                "text": "Select a digital twin to view details."
            }
        
        # Render protocol visualization if relationships are enabled
        protocol_visualization = None
        if self.state["show_relationships"]:
            protocol_visualization = self.protocol_visualizer.render(
                entity_id=selected_twin["id"],
                entity_type="digital_twin",
                show_trust_paths=self.state["show_trust_scores"]
            )
        
        # Render digital twin viewer
        twin_viewer_render = self.digital_twin_viewer.render(
            twin=selected_twin,
            show_trust_scores=self.state["show_trust_scores"],
            show_real_time_data=self.state["show_real_time_data"]
        )
        
        # Render historical data visualization if enabled
        historical_data_render = None
        if self.state["show_historical_data"]:
            historical_data_render = self.data_visualization.render(
                entity_id=selected_twin["id"],
                entity_type="digital_twin",
                time_range=self._get_time_range(),
                metrics=selected_twin.get("available_metrics", [])
            )
        
        return {
            "type": "container",
            "layout": "split",
            "split_direction": "vertical",
            "children": [
                {
                    "type": "container",
                    "title": "Digital Twin Details",
                    "layout": "split",
                    "split_direction": "horizontal",
                    "children": [
                        {
                            "type": "container",
                            "flex": 1,
                            "children": [twin_viewer_render]
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
                                            "content": self._render_overview_tab(selected_twin)
                                        },
                                        {
                                            "label": "Historical Data",
                                            "content": historical_data_render or {
                                                "type": "message",
                                                "text": "Historical data visualization is disabled."
                                            }
                                        },
                                        {
                                            "label": "Control",
                                            "content": self._render_control_tab(selected_twin)
                                        },
                                        {
                                            "label": "Configuration",
                                            "content": self._render_configuration_tab(selected_twin)
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
    
    def _get_selected_twin(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected digital twin data.
        
        Returns:
            Dict containing selected digital twin data, or None if no twin is selected
        """
        if not self.state["selected_twin_id"]:
            return None
        
        for twin in self.state["twins"]:
            if twin["id"] == self.state["selected_twin_id"]:
                return twin
        
        return None
    
    def _get_time_range(self) -> Dict[str, Any]:
        """
        Get the current time range for historical data visualization.
        
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
    
    def _render_overview_tab(self, twin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the overview tab for the detail view.
        
        Args:
            twin: Digital twin data
            
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
                            {"label": "Name", "value": twin.get("name", "")},
                            {"label": "Type", "value": twin.get("type", "")},
                            {"label": "Domain", "value": twin.get("domain", "")},
                            {"label": "Status", "value": twin.get("status", "")},
                            {"label": "Last Updated", "value": twin.get("last_updated", "")},
                            {"label": "Created", "value": twin.get("created", "")},
                            {"label": "Owner", "value": twin.get("owner", "")},
                            {"label": "Location", "value": twin.get("location", "")}
                        ]
                    }
                },
                {
                    "type": "widget",
                    "title": "Description",
                    "position": {"row": 0, "col": 6, "width": 6, "height": 2},
                    "content": {
                        "type": "markdown",
                        "text": twin.get("description", "No description available.")
                    }
                },
                {
                    "type": "widget",
                    "title": "Key Metrics",
                    "position": {"row": 2, "col": 0, "width": 12, "height": 3},
                    "content": {
                        "type": "metrics_dashboard",
                        "metrics": twin.get("metrics", []),
                        "show_trends": True,
                        "show_thresholds": True
                    }
                },
                {
                    "type": "widget",
                    "title": "Related Twins",
                    "position": {"row": 5, "col": 0, "width": 6, "height": 3},
                    "content": {
                        "type": "related_entities",
                        "entities": twin.get("related_twins", []),
                        "entity_type": "digital_twin",
                        "action": "select_twin"
                    }
                },
                {
                    "type": "widget",
                    "title": "Related Agents",
                    "position": {"row": 5, "col": 6, "width": 6, "height": 3},
                    "content": {
                        "type": "related_entities",
                        "entities": twin.get("related_agents", []),
                        "entity_type": "agent",
                        "action": "navigate_to_agent"
                    }
                }
            ]
        }
    
    def _render_control_tab(self, twin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the control tab for the detail view.
        
        Args:
            twin: Digital twin data
            
        Returns:
            Dict containing the rendered control tab structure
        """
        # Check if twin is online
        if twin.get("status") != "online":
            return {
                "type": "message",
                "text": f"Digital twin is currently {twin.get("status", "offline")}. Control is only available for online twins.",
                "severity": "warning"
            }
        
        # Get available commands
        commands = twin.get("available_commands", [])
        
        if not commands:
            return {
                "type": "message",
                "text": "No control commands available for this digital twin.",
                "severity": "info"
            }
        
        # Render trust ribbon for control interface
        trust_ribbon_render = None
        if self.state["show_trust_scores"]:
            trust_ribbon_render = self.trust_ribbon.render(
                trust_score=twin.get("trust_score", 0),
                verification_status=twin.get("verification_status", "unverified"),
                context="control"
            )
        
        return {
            "type": "container",
            "layout": "vertical",
            "children": [
                trust_ribbon_render,
                {
                    "type": "message",
                    "text": "Control commands are trust-weighted. Higher trust scores enable more critical operations.",
                    "severity": "info"
                },
                {
                    "type": "command_panel",
                    "commands": [self._render_command(command, twin) for command in commands],
                    "recent_commands": twin.get("recent_commands", [])
                }
            ]
        }
    
    def _render_command(self, command: Dict[str, Any], twin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a control command for the control tab.
        
        Args:
            command: Command data
            twin: Digital twin data
            
        Returns:
            Dict containing the rendered command structure
        """
        # Check if command is available based on trust score
        twin_trust_score = twin.get("trust_score", 0)
        command_trust_threshold = command.get("trust_threshold", 0)
        is_available = twin_trust_score >= command_trust_threshold
        
        return {
            "type": "command",
            "id": command.get("id"),
            "name": command.get("name"),
            "description": command.get("description"),
            "parameters": command.get("parameters", []),
            "trust_threshold": command_trust_threshold,
            "criticality": command.get("criticality", "low"),
            "available": is_available,
            "action": "execute_twin_command",
            "params": {
                "twin_id": twin["id"],
                "command_id": command.get("id")
            }
        }
    
    def _render_configuration_tab(self, twin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the configuration tab for the detail view.
        
        Args:
            twin: Digital twin data
            
        Returns:
            Dict containing the rendered configuration tab structure
        """
        configuration = twin.get("configuration", {})
        
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
                            "value": twin.get("name", ""),
                            "name": "name"
                        },
                        {
                            "type": "text_area",
                            "label": "Description",
                            "value": twin.get("description", ""),
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
                            "value": twin.get("domain", "general"),
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
                                } for field_name, field_config in twin.get("configuration_schema", {}).items()
                            ]
                        }
                    ],
                    "actions": [
                        {
                            "type": "button",
                            "label": "Save Configuration",
                            "action": "save_twin_configuration",
                            "params": {"twin_id": twin["id"]}
                        },
                        {
                            "type": "button",
                            "label": "Reset to Defaults",
                            "action": "reset_twin_configuration",
                            "params": {"twin_id": twin["id"]}
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
            "create_twin": self.create_twin,
            "import_twin": self.import_twin,
            "export_twin": self.export_twin,
            "change_view_mode": self.change_view_mode,
            "change_sort_by": self.change_sort_by,
            "filter_by_type": self.filter_by_type,
            "filter_by_domain": self.filter_by_domain,
            "filter_by_status": self.filter_by_status,
            "filter_by_trust_threshold": self.filter_by_trust_threshold,
            "toggle_trust_scores": self.toggle_trust_scores,
            "toggle_real_time_data": self.toggle_real_time_data,
            "toggle_relationships": self.toggle_relationships,
            "toggle_historical_data": self.toggle_historical_data,
            "change_time_range": self.change_time_range,
            "set_custom_time_range": self.set_custom_time_range,
            "select_twin": self.select_twin,
            "control_twin": self.control_twin,
            "execute_twin_command": self.execute_twin_command,
            "save_twin_configuration": self.save_twin_configuration,
            "reset_twin_configuration": self.reset_twin_configuration,
            "navigate_to_agent": self.navigate_to_agent
        }
    
    # Event handlers
    def _handle_twin_status_update(self, event: Dict[str, Any]):
        """
        Handle digital twin status update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        twin_id = event.get("twin_id")
        new_status = event.get("status")
        
        if not twin_id or not new_status:
            return
        
        # Update twin status in twins list
        for twin in self.state["twins"]:
            if twin["id"] == twin_id:
                twin["status"] = new_status
                break
    
    def _handle_twin_data_update(self, event: Dict[str, Any]):
        """
        Handle digital twin data update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        twin_id = event.get("twin_id")
        metrics = event.get("metrics")
        
        if not twin_id or not metrics:
            return
        
        # Update twin metrics in twins list
        for twin in self.state["twins"]:
            if twin["id"] == twin_id:
                twin["metrics"] = metrics
                twin["last_updated"] = event.get("timestamp", "Unknown")
                break
    
    def _handle_twin_trust_score_update(self, event: Dict[str, Any]):
        """
        Handle digital twin trust score update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        twin_id = event.get("twin_id")
        trust_score = event.get("trust_score")
        verification_status = event.get("verification_status")
        
        if not twin_id or trust_score is None:
            return
        
        # Update twin trust score in twins list
        for twin in self.state["twins"]:
            if twin["id"] == twin_id:
                twin["trust_score"] = trust_score
                if verification_status:
                    twin["verification_status"] = verification_status
                break
    
    def _handle_twin_relationship_update(self, event: Dict[str, Any]):
        """
        Handle digital twin relationship update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        twin_id = event.get("twin_id")
        related_twins = event.get("related_twins")
        related_agents = event.get("related_agents")
        
        if not twin_id:
            return
        
        # Update twin relationships in twins list
        for twin in self.state["twins"]:
            if twin["id"] == twin_id:
                if related_twins:
                    twin["related_twins"] = related_twins
                if related_agents:
                    twin["related_agents"] = related_agents
                break
    
    def _handle_twin_command_response(self, event: Dict[str, Any]):
        """
        Handle digital twin command response events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        twin_id = event.get("twin_id")
        command_id = event.get("command_id")
        success = event.get("success")
        result = event.get("result")
        
        if not twin_id or not command_id:
            return
        
        # Update twin recent commands in twins list
        for twin in self.state["twins"]:
            if twin["id"] == twin_id:
                if "recent_commands" not in twin:
                    twin["recent_commands"] = []
                
                twin["recent_commands"].insert(0, {
                    "command_id": command_id,
                    "timestamp": event.get("timestamp", "Unknown"),
                    "success": success,
                    "result": result
                })
                
                # Limit recent commands list to 10 items
                if len(twin["recent_commands"]) > 10:
                    twin["recent_commands"] = twin["recent_commands"][:10]
                
                break
    
    # Action handlers
    def create_twin(self, params: Dict[str, Any] = None):
        """
        Create a new digital twin.
        
        Args:
            params: Optional parameters for digital twin creation
        """
        # Request digital twin creation
        self.real_time_context_bus.publish(
            topic="digital_twin.create.request",
            data={
                "source": "ui_ux_layer",
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested digital twin creation with params: {params}")
    
    def import_twin(self, params: Dict[str, Any] = None):
        """
        Import a digital twin.
        
        Args:
            params: Optional parameters for digital twin import
        """
        # Request digital twin import
        self.real_time_context_bus.publish(
            topic="digital_twin.import.request",
            data={
                "source": "ui_ux_layer",
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested digital twin import with params: {params}")
    
    def export_twin(self, params: Dict[str, Any] = None):
        """
        Export a digital twin.
        
        Args:
            params: Optional parameters for digital twin export
        """
        twin_id = params.get("twin_id") if params else self.state["selected_twin_id"]
        
        if not twin_id:
            self.logger.warning("Cannot export digital twin: No twin selected")
            return
        
        # Request digital twin export
        self.real_time_context_bus.publish(
            topic="digital_twin.export.request",
            data={
                "source": "ui_ux_layer",
                "twin_id": twin_id,
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested export of digital twin {twin_id}")
    
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
        """Apply current sort criteria to the twins list."""
        sort_key = self.state["sort_by"]
        
        if sort_key == "name":
            self.state["twins"].sort(key=lambda t: t.get("name", "").lower())
        elif sort_key == "type":
            self.state["twins"].sort(key=lambda t: t.get("type", "").lower())
        elif sort_key == "status":
            # Sort by status priority: error, warning, online, offline
            status_priority = {"error": 0, "warning": 1, "online": 2, "offline": 3}
            self.state["twins"].sort(key=lambda t: status_priority.get(t.get("status", "offline"), 4))
        elif sort_key == "last_updated":
            # This would require proper timestamp parsing in a real implementation
            self.state["twins"].sort(key=lambda t: t.get("last_updated", ""), reverse=True)
    
    def filter_by_type(self, params: Dict[str, Any]):
        """
        Filter digital twins by type.
        
        Args:
            params: Parameters containing the type filter value
        """
        twin_type = params.get("value")
        if twin_type:
            self.state["filter_criteria"]["type"] = twin_type if twin_type != "all" else None
            self._apply_filters()
    
    def filter_by_domain(self, params: Dict[str, Any]):
        """
        Filter digital twins by domain.
        
        Args:
            params: Parameters containing the domain filter value
        """
        domain = params.get("value")
        if domain:
            self.state["filter_criteria"]["domain"] = domain if domain != "all" else None
            self._apply_filters()
    
    def filter_by_status(self, params: Dict[str, Any]):
        """
        Filter digital twins by status.
        
        Args:
            params: Parameters containing the status filter value
        """
        status = params.get("value")
        if status:
            self.state["filter_criteria"]["status"] = status if status != "all" else None
            self._apply_filters()
    
    def filter_by_trust_threshold(self, params: Dict[str, Any]):
        """
        Filter digital twins by trust threshold.
        
        Args:
            params: Parameters containing the trust threshold value
        """
        trust_threshold = params.get("value")
        if trust_threshold is not None:
            self.state["filter_criteria"]["trust_threshold"] = trust_threshold
            self._apply_filters()
    
    def _apply_filters(self):
        """Apply current filters to fetch updated digital twin data."""
        # Request filtered digital twins
        self.real_time_context_bus.publish(
            topic="digital_twin.list.request",
            data={
                "source": "ui_ux_layer",
                "filter_criteria": self.state["filter_criteria"]
            }
        )
        
        self.logger.info(f"Applied digital twin filters: {self.state["filter_criteria"]}")
    
    def toggle_trust_scores(self, params: Dict[str, Any]):
        """
        Toggle display of trust scores.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_trust_scores = params.get("checked")
        if show_trust_scores is not None:
            self.state["show_trust_scores"] = show_trust_scores
    
    def toggle_real_time_data(self, params: Dict[str, Any]):
        """
        Toggle display of real-time data.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_real_time_data = params.get("checked")
        if show_real_time_data is not None:
            self.state["show_real_time_data"] = show_real_time_data
    
    def toggle_relationships(self, params: Dict[str, Any]):
        """
        Toggle display of relationships.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_relationships = params.get("checked")
        if show_relationships is not None:
            self.state["show_relationships"] = show_relationships
    
    def toggle_historical_data(self, params: Dict[str, Any]):
        """
        Toggle display of historical data.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_historical_data = params.get("checked")
        if show_historical_data is not None:
            self.state["show_historical_data"] = show_historical_data
    
    def change_time_range(self, params: Dict[str, Any]):
        """
        Change the time range for historical data.
        
        Args:
            params: Parameters containing the time range value
        """
        time_range = params.get("value")
        if time_range:
            self.state["time_range"] = time_range
    
    def set_custom_time_range(self, params: Dict[str, Any]):
        """
        Set a custom time range for historical data.
        
        Args:
            params: Parameters containing the custom time range values
        """
        start = params.get("start")
        end = params.get("end")
        
        if start and end:
            self.state["custom_time_range"]["start"] = start
            self.state["custom_time_range"]["end"] = end
            self.state["time_range"] = "custom"
    
    def select_twin(self, params: Dict[str, Any]):
        """
        Select a digital twin.
        
        Args:
            params: Parameters containing the digital twin ID
        """
        twin_id = params.get("twin_id")
        if twin_id:
            self.state["selected_twin_id"] = twin_id
            
            # If in grid or list view, switch to detail view
            if self.state["view_mode"] in ["grid", "list"]:
                self.state["view_mode"] = "detail"
            
            # Request detailed digital twin data
            self.real_time_context_bus.publish(
                topic="digital_twin.detail.request",
                data={
                    "source": "ui_ux_layer",
                    "twin_id": twin_id
                }
            )
            
            self.logger.info(f"Selected digital twin {twin_id}")
    
    def control_twin(self, params: Dict[str, Any]):
        """
        Open the control interface for a digital twin.
        
        Args:
            params: Parameters containing the digital twin ID
        """
        twin_id = params.get("twin_id")
        if twin_id:
            self.state["selected_twin_id"] = twin_id
            self.state["view_mode"] = "detail"
            
            # Request detailed digital twin data
            self.real_time_context_bus.publish(
                topic="digital_twin.detail.request",
                data={
                    "source": "ui_ux_layer",
                    "twin_id": twin_id
                }
            )
            
            self.logger.info(f"Opened control interface for digital twin {twin_id}")
    
    def execute_twin_command(self, params: Dict[str, Any]):
        """
        Execute a command on a digital twin.
        
        Args:
            params: Parameters containing the digital twin ID, command ID, and command parameters
        """
        twin_id = params.get("twin_id")
        command_id = params.get("command_id")
        command_params = params.get("command_params", {})
        
        if not twin_id or not command_id:
            self.logger.warning("Cannot execute command: Missing twin ID or command ID")
            return
        
        # Request command execution
        self.real_time_context_bus.publish(
            topic="digital_twin.command.execute.request",
            data={
                "source": "ui_ux_layer",
                "twin_id": twin_id,
                "command_id": command_id,
                "command_params": command_params
            }
        )
        
        self.logger.info(f"Requested execution of command {command_id} on digital twin {twin_id}")
    
    def save_twin_configuration(self, params: Dict[str, Any]):
        """
        Save the configuration for a digital twin.
        
        Args:
            params: Parameters containing the digital twin ID and configuration data
        """
        twin_id = params.get("twin_id")
        configuration = params.get("configuration")
        
        if not twin_id or not configuration:
            self.logger.warning("Cannot save configuration: Missing twin ID or configuration data")
            return
        
        # Request configuration save
        self.real_time_context_bus.publish(
            topic="digital_twin.configuration.save.request",
            data={
                "source": "ui_ux_layer",
                "twin_id": twin_id,
                "configuration": configuration
            }
        )
        
        self.logger.info(f"Requested save of configuration for digital twin {twin_id}")
    
    def reset_twin_configuration(self, params: Dict[str, Any]):
        """
        Reset the configuration for a digital twin to defaults.
        
        Args:
            params: Parameters containing the digital twin ID
        """
        twin_id = params.get("twin_id")
        
        if not twin_id:
            self.logger.warning("Cannot reset configuration: Missing twin ID")
            return
        
        # Request configuration reset
        self.real_time_context_bus.publish(
            topic="digital_twin.configuration.reset.request",
            data={
                "source": "ui_ux_layer",
                "twin_id": twin_id
            }
        )
        
        self.logger.info(f"Requested reset of configuration for digital twin {twin_id}")
    
    def navigate_to_agent(self, params: Dict[str, Any]):
        """
        Navigate to the agent explorer page for a specific agent.
        
        Args:
            params: Parameters containing the agent ID
        """
        agent_id = params.get("agent_id")
        
        if not agent_id:
            self.logger.warning("Cannot navigate to agent: Missing agent ID")
            return
        
        # Request navigation to agent explorer page
        self.real_time_context_bus.publish(
            topic="ui.navigate.request",
            data={
                "source": "ui_ux_layer",
                "target_page": "agent_explorer",
                "params": {
                    "agent_id": agent_id
                }
            }
        )
        
        self.logger.info(f"Requested navigation to agent explorer for agent {agent_id}")
