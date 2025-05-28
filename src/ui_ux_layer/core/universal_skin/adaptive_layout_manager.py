"""
Adaptive Layout Manager for Universal Skin Shell

This module manages adaptive layouts within the Universal Skin Shell
of the Industriverse UI/UX Layer. It implements responsive and context-aware
layout management across different devices, screen sizes, and interaction modes.

The Adaptive Layout Manager:
1. Defines and manages layout templates and grid systems
2. Adapts layouts based on device capabilities and screen dimensions
3. Handles layout transitions and animations
4. Provides an API for dynamic layout customization
5. Coordinates with the Context Engine for context-aware layout adaptations

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time

# Local imports
from ..context_engine.context_awareness_engine import ContextAwarenessEngine
from ..rendering_engine.rendering_engine import RenderingEngine

# Configure logging
logger = logging.getLogger(__name__)

class LayoutType(Enum):
    """Enumeration of standard layout types in Industriverse."""
    GRID = "grid"               # Grid-based layout with equal cells
    SPLIT = "split"             # Split view with primary and secondary panels
    WORKFLOW = "workflow"       # Workflow-oriented layout
    AGENT = "agent"             # Agent-centric layout
    CONTROL = "control"         # Control-oriented layout
    ANALYSIS = "analysis"       # Analysis-oriented layout
    ADMIN = "admin"             # Administration layout
    DEVELOPER = "developer"     # Developer layout
    CUSTOM = "custom"           # Custom layout type

class DeviceOrientation(Enum):
    """Enumeration of device orientations."""
    PORTRAIT = "portrait"       # Portrait orientation (taller than wide)
    LANDSCAPE = "landscape"     # Landscape orientation (wider than tall)
    SQUARE = "square"           # Square orientation (equal width and height)

class AdaptiveLayoutManager:
    """
    Manages adaptive layouts within the Universal Skin Shell.
    
    This class is responsible for implementing responsive and context-aware
    layout management across different devices, screen sizes, and interaction modes.
    """
    
    def __init__(
        self, 
        context_engine: ContextAwarenessEngine,
        rendering_engine: RenderingEngine
    ):
        """
        Initialize the Adaptive Layout Manager.
        
        Args:
            context_engine: The Context Awareness Engine instance
            rendering_engine: The Rendering Engine instance
        """
        self.context_engine = context_engine
        self.rendering_engine = rendering_engine
        
        # Layout definitions
        self.layout_definitions = self._load_layout_definitions()
        
        # Breakpoint definitions
        self.breakpoints = self._load_breakpoints()
        
        # Current active layout
        self.active_layout = None
        
        # Current device metrics
        self.device_metrics = {
            "width": 1920,
            "height": 1080,
            "orientation": DeviceOrientation.LANDSCAPE.value,
            "device_type": "desktop",
            "pixel_ratio": 1.0
        }
        
        # Layout transition history
        self.layout_history = []
        
        # Custom layout definitions
        self.custom_layouts = {}
        
        # Component positions and sizes
        self.component_layout = {}
        
        # Register as context listener
        self.context_engine.register_context_listener(self._handle_context_change)
        
        logger.info("Adaptive Layout Manager initialized")
    
    def _load_layout_definitions(self) -> Dict:
        """
        Load layout definitions.
        
        Returns:
            Dictionary of layout definitions
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard layouts inline
        
        return {
            LayoutType.GRID.value: {
                "name": "Grid Layout",
                "description": "Grid-based layout with equal cells",
                "grid_template": "repeat(auto-fit, minmax(300px, 1fr))",
                "grid_gap": "20px",
                "component_defaults": {
                    "mission_deck": {"grid_area": "1 / 1 / 3 / 3", "z_index": 10},
                    "trust_ribbon": {"grid_area": "1 / 3 / 2 / 5", "z_index": 5},
                    "swarm_lens": {"grid_area": "2 / 3 / 3 / 5", "z_index": 5},
                    "ambient_intelligence_dashboard": {"grid_area": "3 / 1 / 5 / 3", "z_index": 5},
                    "digital_twin_viewer": {"grid_area": "3 / 3 / 5 / 5", "z_index": 5},
                    "layer_avatars": {"grid_area": "1 / 5 / 3 / 6", "z_index": 15},
                    "context_panel": {"grid_area": "3 / 5 / 5 / 6", "z_index": 15},
                    "notification_center": {"grid_area": "5 / 1 / 6 / 6", "z_index": 20}
                },
                "responsive_adjustments": {
                    "mobile": {
                        "grid_template": "repeat(2, 1fr)",
                        "grid_gap": "10px",
                        "component_defaults": {
                            "mission_deck": {"grid_area": "1 / 1 / 3 / 3", "z_index": 10},
                            "layer_avatars": {"grid_area": "3 / 1 / 4 / 3", "z_index": 15},
                            "notification_center": {"grid_area": "4 / 1 / 5 / 3", "z_index": 20}
                        }
                    },
                    "tablet": {
                        "grid_template": "repeat(4, 1fr)",
                        "grid_gap": "15px"
                    }
                }
            },
            LayoutType.SPLIT.value: {
                "name": "Split Layout",
                "description": "Split view with primary and secondary panels",
                "grid_template": "1fr 3fr / 1fr 3fr",
                "grid_gap": "20px",
                "component_defaults": {
                    "digital_twin_viewer": {"grid_area": "1 / 2 / 3 / 3", "z_index": 5},
                    "workflow_canvas": {"grid_area": "1 / 1 / 2 / 2", "z_index": 5},
                    "data_visualization": {"grid_area": "2 / 1 / 3 / 2", "z_index": 5},
                    "layer_avatars": {"grid_area": "1 / 3 / 2 / 4", "z_index": 15},
                    "context_panel": {"grid_area": "2 / 3 / 3 / 4", "z_index": 15},
                    "notification_center": {"grid_area": "3 / 1 / 4 / 4", "z_index": 20},
                    "action_menu": {"position": "fixed", "bottom": "20px", "right": "20px", "z_index": 25}
                },
                "responsive_adjustments": {
                    "mobile": {
                        "grid_template": "repeat(4, 1fr) / 1fr",
                        "grid_gap": "10px",
                        "component_defaults": {
                            "digital_twin_viewer": {"grid_area": "1 / 1 / 3 / 2", "z_index": 5},
                            "workflow_canvas": {"grid_area": "3 / 1 / 4 / 2", "z_index": 5},
                            "layer_avatars": {"grid_area": "4 / 1 / 5 / 2", "z_index": 15},
                            "action_menu": {"position": "fixed", "bottom": "10px", "right": "10px", "z_index": 25}
                        }
                    }
                }
            },
            LayoutType.WORKFLOW.value: {
                "name": "Workflow Layout",
                "description": "Workflow-oriented layout",
                "grid_template": "2fr 1fr / 3fr 1fr",
                "grid_gap": "20px",
                "component_defaults": {
                    "workflow_canvas": {"grid_area": "1 / 1 / 3 / 2", "z_index": 5},
                    "timeline_view": {"grid_area": "1 / 2 / 2 / 3", "z_index": 5},
                    "data_visualization": {"grid_area": "2 / 2 / 3 / 3", "z_index": 5},
                    "layer_avatars": {"grid_area": "1 / 3 / 2 / 4", "z_index": 15},
                    "context_panel": {"grid_area": "2 / 3 / 3 / 4", "z_index": 15},
                    "notification_center": {"grid_area": "3 / 1 / 4 / 4", "z_index": 20},
                    "action_menu": {"position": "fixed", "bottom": "20px", "right": "20px", "z_index": 25}
                },
                "responsive_adjustments": {
                    "mobile": {
                        "grid_template": "repeat(4, 1fr) / 1fr",
                        "grid_gap": "10px"
                    }
                }
            },
            LayoutType.AGENT.value: {
                "name": "Agent Layout",
                "description": "Agent-centric layout",
                "grid_template": "2fr 1fr / 2fr 1fr",
                "grid_gap": "20px",
                "component_defaults": {
                    "layer_avatars": {"grid_area": "1 / 1 / 2 / 2", "z_index": 15},
                    "swarm_lens": {"grid_area": "2 / 1 / 3 / 2", "z_index": 5},
                    "trust_ribbon": {"grid_area": "1 / 2 / 2 / 3", "z_index": 5},
                    "context_panel": {"grid_area": "2 / 2 / 3 / 3", "z_index": 15},
                    "notification_center": {"grid_area": "3 / 1 / 4 / 3", "z_index": 20},
                    "action_menu": {"position": "fixed", "bottom": "20px", "right": "20px", "z_index": 25},
                    "negotiation_interface": {"position": "fixed", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)", "z_index": 30, "display": "none"}
                },
                "responsive_adjustments": {
                    "mobile": {
                        "grid_template": "repeat(3, 1fr) / 1fr",
                        "grid_gap": "10px"
                    }
                }
            },
            LayoutType.CONTROL.value: {
                "name": "Control Layout",
                "description": "Control-oriented layout",
                "grid_template": "3fr 1fr / 3fr 1fr",
                "grid_gap": "20px",
                "component_defaults": {
                    "digital_twin_viewer": {"grid_area": "1 / 1 / 3 / 2", "z_index": 5},
                    "action_menu": {"grid_area": "1 / 2 / 2 / 3", "z_index": 25},
                    "context_panel": {"grid_area": "2 / 2 / 3 / 3", "z_index": 15},
                    "notification_center": {"grid_area": "3 / 1 / 4 / 3", "z_index": 20},
                    "layer_avatars": {"position": "fixed", "top": "20px", "right": "20px", "z_index": 15},
                    "data_visualization": {"position": "fixed", "bottom": "80px", "right": "20px", "z_index": 5, "display": "none"}
                },
                "responsive_adjustments": {
                    "mobile": {
                        "grid_template": "repeat(3, 1fr) / 1fr",
                        "grid_gap": "10px"
                    }
                }
            },
            LayoutType.ANALYSIS.value: {
                "name": "Analysis Layout",
                "description": "Analysis-oriented layout",
                "grid_template": "2fr 1fr / 2fr 1fr",
                "grid_gap": "20px",
                "component_defaults": {
                    "data_visualization": {"grid_area": "1 / 1 / 3 / 2", "z_index": 5},
                    "ambient_intelligence_dashboard": {"grid_area": "1 / 2 / 2 / 3", "z_index": 5},
                    "context_panel": {"grid_area": "2 / 2 / 3 / 3", "z_index": 15},
                    "notification_center": {"grid_area": "3 / 1 / 4 / 3", "z_index": 20},
                    "layer_avatars": {"position": "fixed", "top": "20px", "right": "20px", "z_index": 15},
                    "spatial_canvas": {"position": "fixed", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)", "z_index": 30, "display": "none"}
                },
                "responsive_adjustments": {
                    "mobile": {
                        "grid_template": "repeat(3, 1fr) / 1fr",
                        "grid_gap": "10px"
                    }
                }
            },
            LayoutType.ADMIN.value: {
                "name": "Admin Layout",
                "description": "Administration layout",
                "grid_template": "1fr 2fr / 2fr 1fr",
                "grid_gap": "20px",
                "component_defaults": {
                    "mission_deck": {"grid_area": "1 / 1 / 2 / 2", "z_index": 10},
                    "trust_ribbon": {"grid_area": "1 / 2 / 2 / 3", "z_index": 5},
                    "system_admin_panel": {"grid_area": "2 / 1 / 3 / 3", "z_index": 5},
                    "layer_avatars": {"position": "fixed", "top": "20px", "right": "20px", "z_index": 15},
                    "context_panel": {"position": "fixed", "bottom": "80px", "right": "20px", "z_index": 15},
                    "notification_center": {"grid_area": "3 / 1 / 4 / 3", "z_index": 20},
                    "action_menu": {"position": "fixed", "bottom": "20px", "right": "20px", "z_index": 25}
                },
                "responsive_adjustments": {
                    "mobile": {
                        "grid_template": "repeat(3, 1fr) / 1fr",
                        "grid_gap": "10px"
                    }
                }
            },
            LayoutType.DEVELOPER.value: {
                "name": "Developer Layout",
                "description": "Developer layout",
                "grid_template": "2fr 1fr / 2fr 1fr",
                "grid_gap": "20px",
                "component_defaults": {
                    "workflow_canvas": {"grid_area": "1 / 1 / 2 / 2", "z_index": 5},
                    "protocol_visualizer": {"grid_area": "2 / 1 / 3 / 2", "z_index": 5},
                    "developer_tools": {"grid_area": "1 / 2 / 3 / 3", "z_index": 5},
                    "layer_avatars": {"position": "fixed", "top": "20px", "right": "20px", "z_index": 15},
                    "context_panel": {"position": "fixed", "bottom": "80px", "right": "20px", "z_index": 15},
                    "notification_center": {"grid_area": "3 / 1 / 4 / 3", "z_index": 20},
                    "action_menu": {"position": "fixed", "bottom": "20px", "right": "20px", "z_index": 25}
                },
                "responsive_adjustments": {
                    "mobile": {
                        "grid_template": "repeat(4, 1fr) / 1fr",
                        "grid_gap": "10px"
                    }
                }
            }
        }
    
    def _load_breakpoints(self) -> Dict:
        """
        Load breakpoint definitions.
        
        Returns:
            Dictionary of breakpoint definitions
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard breakpoints inline
        
        return {
            "device_types": {
                "mobile": {"max_width": 767},
                "tablet": {"min_width": 768, "max_width": 1023},
                "desktop": {"min_width": 1024},
                "large_desktop": {"min_width": 1440}
            },
            "orientations": {
                "portrait": {"aspect_ratio": 0.8},  # height > width
                "landscape": {"aspect_ratio": 1.25},  # width > height
                "square": {"aspect_ratio_min": 0.8, "aspect_ratio_max": 1.25}  # in between
            }
        }
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        context_type = event.get("type")
        
        # Handle device context changes
        if context_type == "device":
            device_data = event.get("data", {})
            
            # Check for screen size changes
            if "screen_size" in device_data:
                screen_size = device_data["screen_size"]
                width = screen_size.get("width")
                height = screen_size.get("height")
                
                if width and height:
                    self._update_device_metrics(width, height)
            
            # Check for device type changes
            if "device_type" in device_data:
                device_type = device_data["device_type"]
                self.device_metrics["device_type"] = device_type
                
                # Adapt layout based on device type
                self._adapt_to_device_type(device_type)
            
            # Check for orientation changes
            if "orientation" in device_data:
                orientation = device_data["orientation"]
                self.device_metrics["orientation"] = orientation
                
                # Adapt layout based on orientation
                self._adapt_to_orientation(orientation)
        
        # Handle task context changes
        elif context_type == "task":
            task_data = event.get("data", {})
            
            # Adapt layout based on workflow
            if "workflow_id" in task_data:
                workflow_id = task_data["workflow_id"]
                
                # Switch to workflow layout for workflow tasks
                if workflow_id and self.active_layout != LayoutType.WORKFLOW.value:
                    self.switch_to_layout(LayoutType.WORKFLOW.value)
    
    def _update_device_metrics(self, width: int, height: int) -> None:
        """
        Update device metrics based on screen dimensions.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        # Update metrics
        self.device_metrics["width"] = width
        self.device_metrics["height"] = height
        
        # Determine orientation
        aspect_ratio = width / height
        
        if aspect_ratio < self.breakpoints["orientations"]["portrait"]["aspect_ratio"]:
            orientation = DeviceOrientation.PORTRAIT.value
        elif aspect_ratio > self.breakpoints["orientations"]["landscape"]["aspect_ratio"]:
            orientation = DeviceOrientation.LANDSCAPE.value
        else:
            orientation = DeviceOrientation.SQUARE.value
        
        self.device_metrics["orientation"] = orientation
        
        # Determine device type
        device_type = "desktop"  # Default
        
        if width <= self.breakpoints["device_types"]["mobile"]["max_width"]:
            device_type = "mobile"
        elif (width >= self.breakpoints["device_types"]["tablet"]["min_width"] and 
              width <= self.breakpoints["device_types"]["tablet"]["max_width"]):
            device_type = "tablet"
        elif width >= self.breakpoints["device_types"]["large_desktop"]["min_width"]:
            device_type = "large_desktop"
        
        self.device_metrics["device_type"] = device_type
        
        # Adapt layout based on new metrics
        self._adapt_layout_to_metrics()
    
    def _adapt_layout_to_metrics(self) -> None:
        """Adapt current layout based on device metrics."""
        if not self.active_layout:
            return
        
        # Get current layout definition
        layout_def = self.layout_definitions.get(self.active_layout, {})
        if not layout_def:
            return
        
        # Get responsive adjustments for current device type
        device_type = self.device_metrics["device_type"]
        responsive_adjustments = layout_def.get("responsive_adjustments", {}).get(device_type, {})
        
        # Apply responsive adjustments
        if responsive_adjustments:
            # Update grid template
            if "grid_template" in responsive_adjustments:
                grid_template = responsive_adjustments["grid_template"]
                self._set_grid_template(grid_template)
            
            # Update grid gap
            if "grid_gap" in responsive_adjustments:
                grid_gap = responsive_adjustments["grid_gap"]
                self._set_grid_gap(grid_gap)
            
            # Update component defaults
            if "component_defaults" in responsive_adjustments:
                component_defaults = responsive_adjustments["component_defaults"]
                self._update_component_layout(component_defaults)
        else:
            # Revert to default layout
            grid_template = layout_def.get("grid_template")
            grid_gap = layout_def.get("grid_gap")
            component_defaults = layout_def.get("component_defaults", {})
            
            self._set_grid_template(grid_template)
            self._set_grid_gap(grid_gap)
            self._update_component_layout(component_defaults)
    
    def _adapt_to_device_type(self, device_type: str) -> None:
        """
        Adapt layout based on device type.
        
        Args:
            device_type: Device type (mobile, tablet, desktop, etc.)
        """
        # Adapt current layout to device type
        self._adapt_layout_to_metrics()
        
        # For mobile devices, switch to more compact layouts
        if device_type == "mobile" and self.active_layout in [LayoutType.GRID.value, LayoutType.SPLIT.value]:
            # Switch to a more mobile-friendly layout
            self.switch_to_layout(LayoutType.CONTROL.value)
    
    def _adapt_to_orientation(self, orientation: str) -> None:
        """
        Adapt layout based on device orientation.
        
        Args:
            orientation: Device orientation (portrait, landscape)
        """
        # Adapt current layout to orientation
        self._adapt_layout_to_metrics()
        
        # Additional orientation-specific adaptations could be added here
    
    def switch_to_layout(self, layout: str) -> bool:
        """
        Switch to a different layout.
        
        Args:
            layout: The layout to switch to
            
        Returns:
            Boolean indicating success
        """
        # Verify layout exists
        if layout not in self.layout_definitions and layout != LayoutType.CUSTOM.value:
            logger.error(f"Layout {layout} not found in layout definitions")
            return False
        
        # Record previous layout in history
        if self.active_layout:
            self.layout_history.append({
                "layout": self.active_layout,
                "timestamp": time.time()
            })
            
            # Limit history length
            if len(self.layout_history) > 10:
                self.layout_history.pop(0)
        
        # Set new active layout
        self.active_layout = layout
        
        # Get layout definition
        if layout == LayoutType.CUSTOM.value:
            # Use custom layout definition if available
            layout_def = self.custom_layouts.get(layout, {
                "name": "Custom Layout",
                "description": "Custom user-defined layout",
                "grid_template": "repeat(3, 1fr) / repeat(3, 1fr)",
                "grid_gap": "20px",
                "component_defaults": {}
            })
        else:
            layout_def = self.layout_definitions[layout]
        
        # Apply layout settings
        
        # Set grid template
        grid_template = layout_def.get("grid_template")
        self._set_grid_template(grid_template)
        
        # Set grid gap
        grid_gap = layout_def.get("grid_gap")
        self._set_grid_gap(grid_gap)
        
        # Set component layout
        component_defaults = layout_def.get("component_defaults", {})
        self._set_component_layout(component_defaults)
        
        # Adapt layout to current device metrics
        self._adapt_layout_to_metrics()
        
        logger.info(f"Switched to layout: {layout_def.get('name', layout)}")
        return True
    
    def _set_grid_template(self, grid_template: str) -> None:
        """
        Set grid template.
        
        Args:
            grid_template: CSS grid template value
        """
        # In a real implementation, this would update the rendering engine
        # For now, we'll just log the intent
        logger.debug(f"Setting grid template: {grid_template}")
        
        # Update rendering engine
        self.rendering_engine.set_grid_template(grid_template)
    
    def _set_grid_gap(self, grid_gap: str) -> None:
        """
        Set grid gap.
        
        Args:
            grid_gap: CSS grid gap value
        """
        # In a real implementation, this would update the rendering engine
        # For now, we'll just log the intent
        logger.debug(f"Setting grid gap: {grid_gap}")
        
        # Update rendering engine
        self.rendering_engine.set_grid_gap(grid_gap)
    
    def _set_component_layout(self, component_layout: Dict) -> None:
        """
        Set component layout.
        
        Args:
            component_layout: Dictionary of component layout settings
        """
        # Store component layout
        self.component_layout = component_layout
        
        # In a real implementation, this would update the rendering engine
        # For now, we'll just log the intent
        logger.debug(f"Setting component layout for {len(component_layout)} components")
        
        # Update rendering engine
        for component_id, layout_settings in component_layout.items():
            self.rendering_engine.set_component_layout(component_id, layout_settings)
    
    def _update_component_layout(self, component_layout_updates: Dict) -> None:
        """
        Update component layout with partial updates.
        
        Args:
            component_layout_updates: Dictionary of component layout updates
        """
        # Update component layout
        for component_id, layout_settings in component_layout_updates.items():
            if component_id in self.component_layout:
                # Update existing settings
                self.component_layout[component_id].update(layout_settings)
            else:
                # Add new settings
                self.component_layout[component_id] = layout_settings
            
            # Update rendering engine
            self.rendering_engine.set_component_layout(component_id, self.component_layout[component_id])
        
        logger.debug(f"Updated component layout for {len(component_layout_updates)} components")
    
    def get_active_layout(self) -> str:
        """
        Get the currently active layout.
        
        Returns:
            Active layout ID
        """
        return self.active_layout
    
    def get_layout_history(self) -> List[Dict]:
        """
        Get layout transition history.
        
        Returns:
            List of layout transition records
        """
        return self.layout_history
    
    def get_available_layouts(self) -> List[Dict]:
        """
        Get available layouts.
        
        Returns:
            List of available layout information
        """
        layouts = []
        
        for layout_id, layout_def in self.layout_definitions.items():
            layouts.append({
                "id": layout_id,
                "name": layout_def.get("name", layout_id),
                "description": layout_def.get("description", "")
            })
        
        # Add custom layout if defined
        if LayoutType.CUSTOM.value in self.custom_layouts:
            custom_def = self.custom_layouts[LayoutType.CUSTOM.value]
            layouts.append({
                "id": LayoutType.CUSTOM.value,
                "name": custom_def.get("name", "Custom Layout"),
                "description": custom_def.get("description", "Custom user-defined layout")
            })
        
        return layouts
    
    def create_custom_layout(self, layout_definition: Dict) -> bool:
        """
        Create or update a custom layout.
        
        Args:
            layout_definition: Custom layout definition
            
        Returns:
            Boolean indicating success
        """
        # Validate required fields
        required_fields = ["name", "grid_template", "grid_gap"]
        for field in required_fields:
            if field not in layout_definition:
                logger.error(f"Missing required field in custom layout definition: {field}")
                return False
        
        # Set custom layout
        self.custom_layouts[LayoutType.CUSTOM.value] = layout_definition
        
        logger.info(f"Created custom layout: {layout_definition.get('name')}")
        return True
    
    def get_layout_definition(self, layout: str) -> Dict:
        """
        Get layout definition.
        
        Args:
            layout: Layout ID to get definition for
            
        Returns:
            Layout definition dictionary
        """
        if layout == LayoutType.CUSTOM.value and layout in self.custom_layouts:
            return self.custom_layouts[layout]
        elif layout in self.layout_definitions:
            return self.layout_definitions[layout]
        else:
            return {}
    
    def get_component_layout(self, component_id: str = None) -> Dict:
        """
        Get component layout settings.
        
        Args:
            component_id: Optional component ID to get layout for
            
        Returns:
            Component layout settings dictionary
        """
        if component_id:
            return self.component_layout.get(component_id, {})
        else:
            return self.component_layout
    
    def set_component_position(self, component_id: str, position: Dict) -> bool:
        """
        Set position for a specific component.
        
        Args:
            component_id: Component ID to set position for
            position: Position settings dictionary
            
        Returns:
            Boolean indicating success
        """
        # Update component layout
        if component_id in self.component_layout:
            self.component_layout[component_id].update(position)
        else:
            self.component_layout[component_id] = position
        
        # Update rendering engine
        self.rendering_engine.set_component_layout(component_id, self.component_layout[component_id])
        
        logger.debug(f"Set position for component {component_id}")
        return True
    
    def get_device_metrics(self) -> Dict:
        """
        Get current device metrics.
        
        Returns:
            Device metrics dictionary
        """
        return self.device_metrics
    
    def adapt_to_context(self, context_data: Dict) -> None:
        """
        Adapt layout based on context data.
        
        Args:
            context_data: Context data to adapt to
        """
        # This method is called directly when needed, in addition to
        # the automatic adaptations from context change events
        
        # Check for device metrics
        device_context = context_data.get("device", {})
        if "screen_size" in device_context:
            screen_size = device_context["screen_size"]
            width = screen_size.get("width")
            height = screen_size.get("height")
            
            if width and height:
                self._update_device_metrics(width, height)
        
        # Check for task focus
        task_context = context_data.get("task", {})
        if "focus_area" in task_context:
            focus_area = task_context["focus_area"]
            
            # Highlight focused component
            if focus_area and focus_area in self.component_layout:
                # Increase z-index and add highlight
                highlight_settings = {
                    "z_index": 50,
                    "highlight": True
                }
                self.set_component_position(focus_area, highlight_settings)
"""
