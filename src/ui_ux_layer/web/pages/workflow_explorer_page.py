"""
Workflow Explorer Page - The workflow explorer page component for the Industriverse UI/UX Layer.

This component provides a comprehensive interface for exploring, visualizing, and interacting with
workflows across the Industriverse ecosystem. It integrates with the Workflow Automation Layer
to provide real-time visibility into workflow execution, trust-weighted routing, and agent mesh topology.

Features:
- Workflow visualization with trust-weighted routing paths
- Agent mesh topology visualization
- Workflow execution timeline and status monitoring
- Workflow template browsing and instantiation
- Workflow debugging and forensics tools
- Integration with n8n for human-in-the-loop workflows
- Industry-specific workflow template galleries
- Workflow performance analytics and optimization suggestions

The component uses the Universal Skin architecture to adapt its presentation based on
device capabilities, user role, and context, while maintaining protocol-native visualization
of the underlying MCP/A2A communication.
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
from components.workflow_canvas.workflow_canvas import WorkflowCanvas
from components.trust_ribbon.trust_ribbon import TrustRibbon
from components.timeline_view.timeline_view import TimelineView
from components.ambient_veil.ambient_veil import AmbientVeil
from components.protocol_visualizer.protocol_visualizer import ProtocolVisualizer

class WorkflowExplorerPage:
    """
    Workflow Explorer Page component for the Industriverse UI/UX Layer.
    
    This page provides a comprehensive interface for exploring, visualizing, and
    interacting with workflows across the Industriverse ecosystem.
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
        Initialize the Workflow Explorer Page component.
        
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
        self.workflow_canvas = WorkflowCanvas(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            protocol_bridge=protocol_bridge,
            real_time_context_bus=real_time_context_bus
        )
        
        self.trust_ribbon = TrustRibbon(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            protocol_bridge=protocol_bridge
        )
        
        self.timeline_view = TimelineView(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            real_time_context_bus=real_time_context_bus
        )
        
        self.ambient_veil = AmbientVeil(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            context_engine=context_engine
        )
        
        self.protocol_visualizer = ProtocolVisualizer(
            universal_skin_shell=universal_skin_shell,
            rendering_engine=rendering_engine,
            protocol_bridge=protocol_bridge
        )
        
        # Initialize state
        self.state = {
            "selected_workflow_id": None,
            "workflow_templates": [],
            "active_workflows": [],
            "workflow_history": [],
            "filter_criteria": {
                "industry": None,
                "status": None,
                "trust_level": None,
                "date_range": None
            },
            "view_mode": "graph",  # Options: graph, timeline, list
            "detail_level": "medium",  # Options: low, medium, high
            "show_trust_paths": True,
            "show_agent_mesh": True,
            "show_performance_metrics": True
        }
        
        # Subscribe to workflow-related events
        self._subscribe_to_events()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Workflow Explorer Page initialized")
    
    def _subscribe_to_events(self):
        """Subscribe to workflow-related events from the Real-Time Context Bus."""
        self.real_time_context_bus.subscribe(
            topic="workflow.status.update",
            callback=self._handle_workflow_status_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="workflow.template.update",
            callback=self._handle_workflow_template_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="workflow.agent.update",
            callback=self._handle_workflow_agent_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="workflow.trust.update",
            callback=self._handle_workflow_trust_update
        )
        
        self.real_time_context_bus.subscribe(
            topic="workflow.performance.update",
            callback=self._handle_workflow_performance_update
        )
    
    def render(self) -> Dict[str, Any]:
        """
        Render the Workflow Explorer Page.
        
        Returns:
            Dict containing the rendered page structure
        """
        # Adapt rendering based on device capabilities and context
        device_capabilities = self.device_adapter.get_capabilities()
        user_context = self.context_engine.get_current_context()
        
        # Determine layout based on device and context
        layout = self._determine_layout(device_capabilities, user_context)
        
        # Render main components
        workflow_canvas_render = self.workflow_canvas.render(
            workflows=self.state["active_workflows"],
            selected_workflow_id=self.state["selected_workflow_id"],
            show_trust_paths=self.state["show_trust_paths"],
            show_agent_mesh=self.state["show_agent_mesh"],
            detail_level=self.state["detail_level"]
        )
        
        trust_ribbon_render = self.trust_ribbon.render(
            workflows=self.state["active_workflows"],
            selected_workflow_id=self.state["selected_workflow_id"]
        )
        
        timeline_view_render = self.timeline_view.render(
            workflows=self.state["active_workflows"],
            workflow_history=self.state["workflow_history"],
            selected_workflow_id=self.state["selected_workflow_id"]
        )
        
        ambient_veil_render = self.ambient_veil.render(
            context=user_context,
            workflows=self.state["active_workflows"]
        )
        
        protocol_visualizer_render = self.protocol_visualizer.render(
            selected_workflow_id=self.state["selected_workflow_id"],
            show_trust_paths=self.state["show_trust_paths"]
        )
        
        # Construct the page structure
        page_structure = {
            "type": "page",
            "id": "workflow_explorer_page",
            "title": "Workflow Explorer",
            "layout": layout,
            "components": {
                "header": self._render_header(),
                "sidebar": self._render_sidebar(),
                "main_content": {
                    "type": "container",
                    "layout": "flex",
                    "direction": "column",
                    "children": [
                        {
                            "type": "container",
                            "layout": "flex",
                            "direction": "row",
                            "children": [
                                {
                                    "type": "container",
                                    "layout": "flex",
                                    "direction": "column",
                                    "flex": 3,
                                    "children": [
                                        workflow_canvas_render
                                    ]
                                },
                                {
                                    "type": "container",
                                    "layout": "flex",
                                    "direction": "column",
                                    "flex": 1,
                                    "children": [
                                        trust_ribbon_render,
                                        protocol_visualizer_render
                                    ]
                                }
                            ]
                        },
                        timeline_view_render
                    ]
                },
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
            "title": "Workflow Explorer",
            "subtitle": "Visualize, monitor, and interact with workflows across the Industriverse ecosystem",
            "actions": [
                {
                    "type": "button",
                    "label": "New Workflow",
                    "icon": "plus",
                    "action": "create_workflow"
                },
                {
                    "type": "button",
                    "label": "Import",
                    "icon": "import",
                    "action": "import_workflow"
                },
                {
                    "type": "button",
                    "label": "Export",
                    "icon": "export",
                    "action": "export_workflow",
                    "disabled": self.state["selected_workflow_id"] is None
                }
            ],
            "filters": [
                {
                    "type": "dropdown",
                    "label": "Industry",
                    "options": [
                        {"value": "all", "label": "All Industries"},
                        {"value": "manufacturing", "label": "Manufacturing"},
                        {"value": "logistics", "label": "Logistics"},
                        {"value": "energy", "label": "Energy"},
                        {"value": "retail", "label": "Retail"}
                    ],
                    "value": self.state["filter_criteria"]["industry"] or "all",
                    "action": "filter_industry"
                },
                {
                    "type": "dropdown",
                    "label": "Status",
                    "options": [
                        {"value": "all", "label": "All Statuses"},
                        {"value": "active", "label": "Active"},
                        {"value": "paused", "label": "Paused"},
                        {"value": "completed", "label": "Completed"},
                        {"value": "failed", "label": "Failed"}
                    ],
                    "value": self.state["filter_criteria"]["status"] or "all",
                    "action": "filter_status"
                },
                {
                    "type": "dropdown",
                    "label": "Trust Level",
                    "options": [
                        {"value": "all", "label": "All Trust Levels"},
                        {"value": "high", "label": "High Trust"},
                        {"value": "medium", "label": "Medium Trust"},
                        {"value": "low", "label": "Low Trust"}
                    ],
                    "value": self.state["filter_criteria"]["trust_level"] or "all",
                    "action": "filter_trust_level"
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
                    "title": "Workflow Templates",
                    "items": [self._render_template_item(template) for template in self.state["workflow_templates"]]
                },
                {
                    "type": "section",
                    "title": "Active Workflows",
                    "items": [self._render_workflow_item(workflow) for workflow in self.state["active_workflows"]]
                },
                {
                    "type": "section",
                    "title": "View Options",
                    "items": [
                        {
                            "type": "radio_group",
                            "label": "View Mode",
                            "options": [
                                {"value": "graph", "label": "Graph View"},
                                {"value": "timeline", "label": "Timeline View"},
                                {"value": "list", "label": "List View"}
                            ],
                            "value": self.state["view_mode"],
                            "action": "change_view_mode"
                        },
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
                            "label": "Show Trust Paths",
                            "checked": self.state["show_trust_paths"],
                            "action": "toggle_trust_paths"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Agent Mesh",
                            "checked": self.state["show_agent_mesh"],
                            "action": "toggle_agent_mesh"
                        },
                        {
                            "type": "checkbox",
                            "label": "Show Performance Metrics",
                            "checked": self.state["show_performance_metrics"],
                            "action": "toggle_performance_metrics"
                        }
                    ]
                }
            ]
        }
    
    def _render_template_item(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a workflow template item.
        
        Args:
            template: Workflow template data
            
        Returns:
            Dict containing the rendered template item structure
        """
        return {
            "type": "list_item",
            "id": f"template_{template['id']}",
            "title": template.get("name", "Unnamed Template"),
            "subtitle": template.get("description", ""),
            "icon": template.get("icon", "template"),
            "tags": [
                {"label": template.get("industry", "General"), "color": "blue"},
                {"label": f"v{template.get('version', '1.0')}", "color": "gray"}
            ],
            "actions": [
                {
                    "type": "button",
                    "label": "Instantiate",
                    "icon": "play",
                    "action": "instantiate_template",
                    "params": {"template_id": template["id"]}
                }
            ]
        }
    
    def _render_workflow_item(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render an active workflow item.
        
        Args:
            workflow: Workflow data
            
        Returns:
            Dict containing the rendered workflow item structure
        """
        # Determine status color
        status_colors = {
            "active": "green",
            "paused": "yellow",
            "completed": "blue",
            "failed": "red"
        }
        status_color = status_colors.get(workflow.get("status", "active"), "gray")
        
        # Determine trust level color
        trust_colors = {
            "high": "green",
            "medium": "yellow",
            "low": "red"
        }
        trust_color = trust_colors.get(workflow.get("trust_level", "medium"), "gray")
        
        return {
            "type": "list_item",
            "id": f"workflow_{workflow['id']}",
            "title": workflow.get("name", "Unnamed Workflow"),
            "subtitle": workflow.get("description", ""),
            "icon": workflow.get("icon", "workflow"),
            "selected": workflow["id"] == self.state["selected_workflow_id"],
            "tags": [
                {"label": workflow.get("status", "active"), "color": status_color},
                {"label": workflow.get("industry", "General"), "color": "blue"},
                {"label": f"Trust: {workflow.get('trust_level', 'medium')}", "color": trust_color}
            ],
            "actions": [
                {
                    "type": "button",
                    "label": "Select",
                    "icon": "select",
                    "action": "select_workflow",
                    "params": {"workflow_id": workflow["id"]}
                },
                {
                    "type": "button",
                    "label": workflow.get("status") == "active" ? "Pause" : "Resume",
                    "icon": workflow.get("status") == "active" ? "pause" : "play",
                    "action": workflow.get("status") == "active" ? "pause_workflow" : "resume_workflow",
                    "params": {"workflow_id": workflow["id"]}
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
            "create_workflow": self.create_workflow,
            "import_workflow": self.import_workflow,
            "export_workflow": self.export_workflow,
            "filter_industry": self.filter_by_industry,
            "filter_status": self.filter_by_status,
            "filter_trust_level": self.filter_by_trust_level,
            "change_view_mode": self.change_view_mode,
            "change_detail_level": self.change_detail_level,
            "toggle_trust_paths": self.toggle_trust_paths,
            "toggle_agent_mesh": self.toggle_agent_mesh,
            "toggle_performance_metrics": self.toggle_performance_metrics,
            "instantiate_template": self.instantiate_template,
            "select_workflow": self.select_workflow,
            "pause_workflow": self.pause_workflow,
            "resume_workflow": self.resume_workflow
        }
    
    # Event handlers
    def _handle_workflow_status_update(self, event: Dict[str, Any]):
        """
        Handle workflow status update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        workflow_id = event.get("workflow_id")
        new_status = event.get("status")
        
        if not workflow_id or not new_status:
            return
        
        # Update workflow status in active workflows
        for workflow in self.state["active_workflows"]:
            if workflow["id"] == workflow_id:
                workflow["status"] = new_status
                break
        
        # If this is the selected workflow, update the canvas
        if self.state["selected_workflow_id"] == workflow_id:
            self.workflow_canvas.update_workflow_status(workflow_id, new_status)
    
    def _handle_workflow_template_update(self, event: Dict[str, Any]):
        """
        Handle workflow template update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        template_id = event.get("template_id")
        template_data = event.get("template_data")
        
        if not template_id or not template_data:
            return
        
        # Check if template already exists
        template_exists = False
        for i, template in enumerate(self.state["workflow_templates"]):
            if template["id"] == template_id:
                # Update existing template
                self.state["workflow_templates"][i] = template_data
                template_exists = True
                break
        
        # Add new template if it doesn't exist
        if not template_exists:
            self.state["workflow_templates"].append(template_data)
    
    def _handle_workflow_agent_update(self, event: Dict[str, Any]):
        """
        Handle workflow agent update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        workflow_id = event.get("workflow_id")
        agent_id = event.get("agent_id")
        agent_data = event.get("agent_data")
        
        if not workflow_id or not agent_id or not agent_data:
            return
        
        # If this is the selected workflow, update the canvas
        if self.state["selected_workflow_id"] == workflow_id:
            self.workflow_canvas.update_agent(workflow_id, agent_id, agent_data)
    
    def _handle_workflow_trust_update(self, event: Dict[str, Any]):
        """
        Handle workflow trust update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        workflow_id = event.get("workflow_id")
        trust_data = event.get("trust_data")
        
        if not workflow_id or not trust_data:
            return
        
        # Update workflow trust level in active workflows
        for workflow in self.state["active_workflows"]:
            if workflow["id"] == workflow_id:
                workflow["trust_level"] = trust_data.get("trust_level", workflow.get("trust_level", "medium"))
                break
        
        # If this is the selected workflow, update the trust ribbon
        if self.state["selected_workflow_id"] == workflow_id:
            self.trust_ribbon.update_trust_data(workflow_id, trust_data)
    
    def _handle_workflow_performance_update(self, event: Dict[str, Any]):
        """
        Handle workflow performance update events.
        
        Args:
            event: Event data from the Real-Time Context Bus
        """
        workflow_id = event.get("workflow_id")
        performance_data = event.get("performance_data")
        
        if not workflow_id or not performance_data:
            return
        
        # If this is the selected workflow and performance metrics are shown, update the canvas
        if self.state["selected_workflow_id"] == workflow_id and self.state["show_performance_metrics"]:
            self.workflow_canvas.update_performance_metrics(workflow_id, performance_data)
    
    # Action handlers
    def create_workflow(self, params: Dict[str, Any] = None):
        """
        Create a new workflow.
        
        Args:
            params: Optional parameters for workflow creation
        """
        # Request workflow creation from the Workflow Automation Layer
        self.real_time_context_bus.publish(
            topic="workflow.create.request",
            data={
                "source": "ui_ux_layer",
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested workflow creation with params: {params}")
    
    def import_workflow(self, params: Dict[str, Any] = None):
        """
        Import a workflow from file or URL.
        
        Args:
            params: Optional parameters for workflow import
        """
        # Request workflow import from the Workflow Automation Layer
        self.real_time_context_bus.publish(
            topic="workflow.import.request",
            data={
                "source": "ui_ux_layer",
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested workflow import with params: {params}")
    
    def export_workflow(self, params: Dict[str, Any] = None):
        """
        Export the selected workflow.
        
        Args:
            params: Optional parameters for workflow export
        """
        workflow_id = params.get("workflow_id") if params else self.state["selected_workflow_id"]
        
        if not workflow_id:
            self.logger.warning("Cannot export workflow: No workflow selected")
            return
        
        # Request workflow export from the Workflow Automation Layer
        self.real_time_context_bus.publish(
            topic="workflow.export.request",
            data={
                "source": "ui_ux_layer",
                "workflow_id": workflow_id,
                "params": params or {}
            }
        )
        
        self.logger.info(f"Requested export of workflow {workflow_id}")
    
    def filter_by_industry(self, params: Dict[str, Any]):
        """
        Filter workflows by industry.
        
        Args:
            params: Parameters containing the industry filter value
        """
        industry = params.get("value")
        if industry:
            self.state["filter_criteria"]["industry"] = industry if industry != "all" else None
            self._apply_filters()
    
    def filter_by_status(self, params: Dict[str, Any]):
        """
        Filter workflows by status.
        
        Args:
            params: Parameters containing the status filter value
        """
        status = params.get("value")
        if status:
            self.state["filter_criteria"]["status"] = status if status != "all" else None
            self._apply_filters()
    
    def filter_by_trust_level(self, params: Dict[str, Any]):
        """
        Filter workflows by trust level.
        
        Args:
            params: Parameters containing the trust level filter value
        """
        trust_level = params.get("value")
        if trust_level:
            self.state["filter_criteria"]["trust_level"] = trust_level if trust_level != "all" else None
            self._apply_filters()
    
    def _apply_filters(self):
        """Apply current filters to fetch updated workflow data."""
        # Request filtered workflows from the Workflow Automation Layer
        self.real_time_context_bus.publish(
            topic="workflow.list.request",
            data={
                "source": "ui_ux_layer",
                "filter_criteria": self.state["filter_criteria"]
            }
        )
        
        self.logger.info(f"Applied filters: {self.state['filter_criteria']}")
    
    def change_view_mode(self, params: Dict[str, Any]):
        """
        Change the view mode.
        
        Args:
            params: Parameters containing the view mode value
        """
        view_mode = params.get("value")
        if view_mode:
            self.state["view_mode"] = view_mode
    
    def change_detail_level(self, params: Dict[str, Any]):
        """
        Change the detail level.
        
        Args:
            params: Parameters containing the detail level value
        """
        detail_level = params.get("value")
        if detail_level:
            self.state["detail_level"] = detail_level
    
    def toggle_trust_paths(self, params: Dict[str, Any]):
        """
        Toggle display of trust paths.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_trust_paths = params.get("checked")
        if show_trust_paths is not None:
            self.state["show_trust_paths"] = show_trust_paths
    
    def toggle_agent_mesh(self, params: Dict[str, Any]):
        """
        Toggle display of agent mesh.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_agent_mesh = params.get("checked")
        if show_agent_mesh is not None:
            self.state["show_agent_mesh"] = show_agent_mesh
    
    def toggle_performance_metrics(self, params: Dict[str, Any]):
        """
        Toggle display of performance metrics.
        
        Args:
            params: Parameters containing the toggle value
        """
        show_performance_metrics = params.get("checked")
        if show_performance_metrics is not None:
            self.state["show_performance_metrics"] = show_performance_metrics
    
    def instantiate_template(self, params: Dict[str, Any]):
        """
        Instantiate a workflow from a template.
        
        Args:
            params: Parameters containing the template ID
        """
        template_id = params.get("template_id")
        if not template_id:
            self.logger.warning("Cannot instantiate template: No template ID provided")
            return
        
        # Request template instantiation from the Workflow Automation Layer
        self.real_time_context_bus.publish(
            topic="workflow.instantiate.request",
            data={
                "source": "ui_ux_layer",
                "template_id": template_id,
                "params": params
            }
        )
        
        self.logger.info(f"Requested instantiation of template {template_id}")
    
    def select_workflow(self, params: Dict[str, Any]):
        """
        Select a workflow.
        
        Args:
            params: Parameters containing the workflow ID
        """
        workflow_id = params.get("workflow_id")
        if workflow_id:
            self.state["selected_workflow_id"] = workflow_id
            
            # Request detailed workflow data from the Workflow Automation Layer
            self.real_time_context_bus.publish(
                topic="workflow.detail.request",
                data={
                    "source": "ui_ux_layer",
                    "workflow_id": workflow_id
                }
            )
            
            self.logger.info(f"Selected workflow {workflow_id}")
    
    def pause_workflow(self, params: Dict[str, Any]):
        """
        Pause a workflow.
        
        Args:
            params: Parameters containing the workflow ID
        """
        workflow_id = params.get("workflow_id")
        if not workflow_id:
            self.logger.warning("Cannot pause workflow: No workflow ID provided")
            return
        
        # Request workflow pause from the Workflow Automation Layer
        self.real_time_context_bus.publish(
            topic="workflow.pause.request",
            data={
                "source": "ui_ux_layer",
                "workflow_id": workflow_id
            }
        )
        
        self.logger.info(f"Requested pause of workflow {workflow_id}")
    
    def resume_workflow(self, params: Dict[str, Any]):
        """
        Resume a paused workflow.
        
        Args:
            params: Parameters containing the workflow ID
        """
        workflow_id = params.get("workflow_id")
        if not workflow_id:
            self.logger.warning("Cannot resume workflow: No workflow ID provided")
            return
        
        # Request workflow resume from the Workflow Automation Layer
        self.real_time_context_bus.publish(
            topic="workflow.resume.request",
            data={
                "source": "ui_ux_layer",
                "workflow_id": workflow_id
            }
        )
        
        self.logger.info(f"Requested resume of workflow {workflow_id}")
