"""
Context Visualization Engine Module for the UI/UX Layer of Industriverse

This module provides visualization capabilities for contextual information in the UI/UX Layer,
enabling rich, interactive, and adaptive visual representations of context across
different platforms and devices.

The Context Visualization Engine is responsible for:
1. Rendering context visual representations
2. Adapting context visuals to different platforms and devices
3. Providing animation and transition effects for context changes
4. Supporting different visualization modes and styles
5. Integrating with the Universal Skin for consistent visual language

This module works closely with the Context Awareness Engine, Context Rules Engine,
and other context-related components to provide a cohesive visual experience.
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from enum import Enum
import json
import math

from ..rendering_engine.theme_manager import ThemeManager
from .context_awareness_engine import ContextAwarenessEngine
from .context_rules_engine import ContextRulesEngine
from .context_integration_bridge import ContextIntegrationBridge

logger = logging.getLogger(__name__)

class ContextVisualizationMode(Enum):
    """Enumeration of context visualization modes."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    AMBIENT = "ambient"
    IMMERSIVE = "immersive"


class ContextVisualizationStyle(Enum):
    """Enumeration of context visualization styles."""
    STANDARD = "standard"
    INDUSTRIAL = "industrial"
    TECHNICAL = "technical"
    ORGANIC = "organic"
    CUSTOM = "custom"


class ContextVisualizationEngine:
    """
    Provides visualization capabilities for contextual information in the UI/UX Layer.
    
    This class is responsible for rendering context visual representations,
    adapting to different platforms and devices, and providing animation effects.
    """

    def __init__(
        self,
        context_awareness_engine: ContextAwarenessEngine,
        context_rules_engine: ContextRulesEngine,
        context_integration_bridge: ContextIntegrationBridge,
        theme_manager: ThemeManager
    ):
        """
        Initialize the ContextVisualizationEngine.
        
        Args:
            context_awareness_engine: Engine for context awareness
            context_rules_engine: Engine for context rules
            context_integration_bridge: Bridge for context integration
            theme_manager: Manager for UI themes
        """
        self.context_awareness_engine = context_awareness_engine
        self.context_rules_engine = context_rules_engine
        self.context_integration_bridge = context_integration_bridge
        self.theme_manager = theme_manager
        
        # Initialize visualization tracking
        self.visualization_modes = {}
        self.visualization_styles = {}
        self.visualization_cache = {}
        self.visualization_callbacks = {}
        self.custom_renderers = {}
        self.animation_states = {}
        
        # Initialize default visualization styles
        self._initialize_default_styles()
        
        logger.info("ContextVisualizationEngine initialized")

    def _initialize_default_styles(self):
        """Initialize default visualization styles."""
        # Standard style
        self.visualization_styles[ContextVisualizationStyle.STANDARD.value] = {
            "name": "Standard",
            "description": "Default visualization style for context",
            "colors": {
                "background": "rgba(255, 255, 255, 0.9)",
                "border": "#CCCCCC",
                "text": "#333333",
                "icon": "#666666",
                "accent": "#3498DB",
                "highlight": "#F1C40F",
                "critical": "#E74C3C",
                "warning": "#F39C12",
                "info": "#3498DB",
                "success": "#2ECC71"
            },
            "shapes": {
                "border_radius": 8,
                "icon_size": 24,
                "padding": 12,
                "shadow": "0 2px 4px rgba(0, 0, 0, 0.1)"
            },
            "animations": {
                "transition_duration": 0.3,
                "hover_scale": 1.05,
                "highlight_pulse": True,
                "context_change_fade": True
            },
            "typography": {
                "font_family": "Inter, sans-serif",
                "title_size": 16,
                "subtitle_size": 14,
                "body_size": 14,
                "caption_size": 12
            }
        }
        
        # Industrial style
        self.visualization_styles[ContextVisualizationStyle.INDUSTRIAL.value] = {
            "name": "Industrial",
            "description": "Industrial-themed visualization style for context",
            "colors": {
                "background": "rgba(44, 62, 80, 0.9)",
                "border": "#34495E",
                "text": "#ECF0F1",
                "icon": "#BDC3C7",
                "accent": "#F1C40F",
                "highlight": "#F39C12",
                "critical": "#E74C3C",
                "warning": "#F39C12",
                "info": "#3498DB",
                "success": "#2ECC71"
            },
            "shapes": {
                "border_radius": 2,
                "icon_size": 24,
                "padding": 10,
                "shadow": "0 3px 6px rgba(0, 0, 0, 0.3)"
            },
            "animations": {
                "transition_duration": 0.2,
                "hover_scale": 1.02,
                "highlight_pulse": True,
                "context_change_fade": True
            },
            "typography": {
                "font_family": "Roboto Mono, monospace",
                "title_size": 16,
                "subtitle_size": 14,
                "body_size": 14,
                "caption_size": 12
            }
        }
        
        # Technical style
        self.visualization_styles[ContextVisualizationStyle.TECHNICAL.value] = {
            "name": "Technical",
            "description": "Technical visualization style for context",
            "colors": {
                "background": "rgba(30, 30, 30, 0.9)",
                "border": "#333333",
                "text": "#FFFFFF",
                "icon": "#CCCCCC",
                "accent": "#61DAFB",
                "highlight": "#FFD700",
                "critical": "#FF4136",
                "warning": "#FF851B",
                "info": "#0074D9",
                "success": "#2ECC40"
            },
            "shapes": {
                "border_radius": 0,
                "icon_size": 24,
                "padding": 12,
                "shadow": "0 0 10px rgba(97, 218, 251, 0.2)"
            },
            "animations": {
                "transition_duration": 0.15,
                "hover_scale": 1.0,
                "highlight_pulse": True,
                "context_change_fade": True
            },
            "typography": {
                "font_family": "JetBrains Mono, monospace",
                "title_size": 16,
                "subtitle_size": 14,
                "body_size": 14,
                "caption_size": 12
            }
        }
        
        # Organic style
        self.visualization_styles[ContextVisualizationStyle.ORGANIC.value] = {
            "name": "Organic",
            "description": "Organic visualization style for context",
            "colors": {
                "background": "rgba(245, 245, 245, 0.9)",
                "border": "#E0E0E0",
                "text": "#333333",
                "icon": "#555555",
                "accent": "#8BC34A",
                "highlight": "#CDDC39",
                "critical": "#F44336",
                "warning": "#FF9800",
                "info": "#2196F3",
                "success": "#4CAF50"
            },
            "shapes": {
                "border_radius": 20,
                "icon_size": 24,
                "padding": 14,
                "shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"
            },
            "animations": {
                "transition_duration": 0.4,
                "hover_scale": 1.08,
                "highlight_pulse": True,
                "context_change_fade": True
            },
            "typography": {
                "font_family": "Quicksand, sans-serif",
                "title_size": 18,
                "subtitle_size": 16,
                "body_size": 16,
                "caption_size": 14
            }
        }

    def set_visualization_mode(
        self,
        context_type: str,
        mode: ContextVisualizationMode
    ) -> bool:
        """
        Set the visualization mode for a context type.
        
        Args:
            context_type: Type of context
            mode: Visualization mode
            
        Returns:
            True if mode was set, False otherwise
        """
        # Set mode
        self.visualization_modes[context_type] = mode.value
        
        # Clear cache for this context type
        for key in list(self.visualization_cache.keys()):
            if key.startswith(f"{context_type}:"):
                del self.visualization_cache[key]
        
        logger.debug(f"Set visualization mode for context type {context_type} to {mode.value}")
        return True

    def set_visualization_style(
        self,
        context_type: str,
        style: ContextVisualizationStyle
    ) -> bool:
        """
        Set the visualization style for a context type.
        
        Args:
            context_type: Type of context
            style: Visualization style
            
        Returns:
            True if style was set, False otherwise
        """
        # Verify style exists
        if style.value not in self.visualization_styles:
            logger.warning(f"Unknown visualization style: {style.value}")
            return False
        
        # Set style
        self.visualization_styles[context_type] = style.value
        
        # Clear cache for this context type
        for key in list(self.visualization_cache.keys()):
            if key.startswith(f"{context_type}:"):
                del self.visualization_cache[key]
        
        logger.debug(f"Set visualization style for context type {context_type} to {style.value}")
        return True

    def get_visualization_data(
        self,
        context_type: str,
        context_id: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get visualization data for a context.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            force_refresh: Whether to force a refresh of the data
            
        Returns:
            Visualization data
        """
        # Create cache key
        cache_key = f"{context_type}:{context_id}"
        
        # Check cache if not forcing refresh
        if not force_refresh and cache_key in self.visualization_cache:
            return self.visualization_cache[cache_key]
        
        # Get context data
        context_data = self.context_awareness_engine.get_context(context_type, context_id)
        
        if not context_data:
            logger.warning(f"Unknown context: {context_type}:{context_id}")
            return {}
        
        # Get visualization mode
        mode = self.visualization_modes.get(context_type, ContextVisualizationMode.STANDARD.value)
        
        # Get visualization style
        style_id = self.visualization_styles.get(context_type, ContextVisualizationStyle.STANDARD.value)
        style = self.visualization_styles.get(style_id, self.visualization_styles[ContextVisualizationStyle.STANDARD.value])
        
        # Get current theme
        theme = self.theme_manager.get_current_theme()
        
        # Build visualization data
        visualization_data = {
            "context_type": context_type,
            "context_id": context_id,
            "mode": mode,
            "style": style_id,
            "name": context_data.get("name", "Unknown Context"),
            "description": context_data.get("description", ""),
            "priority": context_data.get("priority", "normal"),
            "timestamp": context_data.get("timestamp", time.time()),
            "colors": self._merge_colors(style["colors"], theme.get("colors", {})),
            "shapes": style["shapes"],
            "animations": style["animations"],
            "typography": style["typography"],
            "content": self._get_content_for_mode(context_data, mode),
            "animation_state": self.animation_states.get(cache_key, {})
        }
        
        # Cache visualization data
        self.visualization_cache[cache_key] = visualization_data
        
        return visualization_data

    def _merge_colors(
        self,
        style_colors: Dict[str, str],
        theme_colors: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Merge style colors with theme colors.
        
        Args:
            style_colors: Colors from the style
            theme_colors: Colors from the theme
            
        Returns:
            Merged colors
        """
        merged_colors = style_colors.copy()
        
        # Override with theme colors where available
        for key, value in theme_colors.items():
            if key in merged_colors:
                merged_colors[key] = value
        
        return merged_colors

    def _get_content_for_mode(
        self,
        context_data: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """
        Get content data for a specific visualization mode.
        
        Args:
            context_data: Context data
            mode: Visualization mode
            
        Returns:
            Content data
        """
        content = {
            "title": context_data.get("name", "Unknown Context"),
            "subtitle": context_data.get("type", "unknown"),
            "description": context_data.get("description", ""),
            "priority": context_data.get("priority", "normal"),
            "timestamp": context_data.get("timestamp", time.time()),
            "attributes": [],
            "related_contexts": [],
            "actions": []
        }
        
        # Add mode-specific content
        if mode == ContextVisualizationMode.MINIMAL.value:
            # Minimal content, just the basics
            pass
        
        elif mode == ContextVisualizationMode.STANDARD.value:
            # Add attributes
            attributes = context_data.get("attributes", {})
            for key, value in attributes.items():
                content["attributes"].append({
                    "name": key,
                    "value": value,
                    "type": "number" if isinstance(value, (int, float)) else "string"
                })
            
            # Add related contexts
            related_contexts = context_data.get("related_contexts", [])
            content["related_contexts"] = related_contexts[:3]  # Limit to 3 in standard mode
            
            # Add actions
            actions = context_data.get("actions", [])
            content["actions"] = actions[:3]  # Limit to 3 actions in standard mode
        
        elif mode == ContextVisualizationMode.DETAILED.value:
            # Add all attributes
            attributes = context_data.get("attributes", {})
            for key, value in attributes.items():
                content["attributes"].append({
                    "name": key,
                    "value": value,
                    "type": "number" if isinstance(value, (int, float)) else "string"
                })
            
            # Add all related contexts
            content["related_contexts"] = context_data.get("related_contexts", [])
            
            # Add all actions
            content["actions"] = context_data.get("actions", [])
            
            # Add history
            content["history"] = context_data.get("history", [])
            
            # Add rules
            content["rules"] = context_data.get("rules", [])
        
        elif mode == ContextVisualizationMode.AMBIENT.value:
            # Minimal content for ambient mode, focus on priority and changes
            # Add recent changes
            content["recent_changes"] = context_data.get("recent_changes", [])
        
        elif mode == ContextVisualizationMode.IMMERSIVE.value:
            # Add all attributes
            attributes = context_data.get("attributes", {})
            for key, value in attributes.items():
                content["attributes"].append({
                    "name": key,
                    "value": value,
                    "type": "number" if isinstance(value, (int, float)) else "string"
                })
            
            # Add all related contexts
            content["related_contexts"] = context_data.get("related_contexts", [])
            
            # Add all actions
            content["actions"] = context_data.get("actions", [])
            
            # Add history
            content["history"] = context_data.get("history", [])
            
            # Add rules
            content["rules"] = context_data.get("rules", [])
            
            # Add spatial data
            content["spatial_data"] = context_data.get("spatial_data", {})
            
            # Add immersive properties
            content["immersive_properties"] = context_data.get("immersive_properties", {})
        
        return content

    def register_custom_renderer(
        self,
        context_type: str,
        renderer_function: Callable[[str, str, Dict[str, Any]], Dict[str, Any]]
    ) -> bool:
        """
        Register a custom renderer for a context type.
        
        Args:
            context_type: Type of context
            renderer_function: Function to render the context
            
        Returns:
            True if registration was successful, False otherwise
        """
        self.custom_renderers[context_type] = renderer_function
        logger.info(f"Registered custom renderer for context type {context_type}")
        return True

    def unregister_custom_renderer(self, context_type: str) -> bool:
        """
        Unregister a custom renderer for a context type.
        
        Args:
            context_type: Type of context
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if context_type in self.custom_renderers:
            del self.custom_renderers[context_type]
            logger.info(f"Unregistered custom renderer for context type {context_type}")
            return True
        
        logger.warning(f"No custom renderer registered for context type {context_type}")
        return False

    def render_context(
        self,
        context_type: str,
        context_id: str,
        target_platform: str = "web",
        target_container: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Render a context for a specific platform.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            target_platform: Target platform for rendering
            target_container: Optional target container ID
            callback: Optional callback function
            
        Returns:
            Rendering result
        """
        # Get visualization data
        visualization_data = self.get_visualization_data(context_type, context_id)
        
        if not visualization_data:
            logger.warning(f"Failed to get visualization data for context {context_type}:{context_id}")
            return {}
        
        # Check for custom renderer
        if context_type in self.custom_renderers:
            # Use custom renderer
            renderer = self.custom_renderers[context_type]
            result = renderer(context_type, context_id, visualization_data)
        else:
            # Use default renderer
            result = self._default_renderer(context_type, context_id, visualization_data, target_platform)
        
        # Store callback if provided
        if callback:
            cache_key = f"{context_type}:{context_id}"
            self.visualization_callbacks[cache_key] = callback
        
        return result

    def _default_renderer(
        self,
        context_type: str,
        context_id: str,
        visualization_data: Dict[str, Any],
        target_platform: str
    ) -> Dict[str, Any]:
        """
        Default renderer for contexts.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            visualization_data: Visualization data
            target_platform: Target platform for rendering
            
        Returns:
            Rendering result
        """
        # This is a simplified implementation
        # In a real system, this would generate actual rendering instructions
        
        mode = visualization_data.get("mode", ContextVisualizationMode.STANDARD.value)
        style = visualization_data.get("style", ContextVisualizationStyle.STANDARD.value)
        priority = visualization_data.get("priority", "normal")
        
        # Generate rendering instructions based on platform
        if target_platform == "web":
            return self._generate_web_rendering(context_type, context_id, visualization_data)
        
        elif target_platform == "mobile":
            return self._generate_mobile_rendering(context_type, context_id, visualization_data)
        
        elif target_platform == "desktop":
            return self._generate_desktop_rendering(context_type, context_id, visualization_data)
        
        elif target_platform == "ar":
            return self._generate_ar_rendering(context_type, context_id, visualization_data)
        
        else:
            logger.warning(f"Unknown target platform: {target_platform}")
            return {}

    def _generate_web_rendering(
        self,
        context_type: str,
        context_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate web rendering instructions for a context.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            visualization_data: Visualization data
            
        Returns:
            Web rendering instructions
        """
        mode = visualization_data.get("mode", ContextVisualizationMode.STANDARD.value)
        style_id = visualization_data.get("style", ContextVisualizationStyle.STANDARD.value)
        priority = visualization_data.get("priority", "normal")
        content = visualization_data.get("content", {})
        colors = visualization_data.get("colors", {})
        shapes = visualization_data.get("shapes", {})
        typography = visualization_data.get("typography", {})
        animations = visualization_data.get("animations", {})
        
        # Generate CSS
        css = {
            "container": {
                "background-color": colors.get("background", "rgba(255, 255, 255, 0.9)"),
                "border": f"1px solid {colors.get('border', '#CCCCCC')}",
                "border-radius": f"{shapes.get('border_radius', 8)}px",
                "padding": f"{shapes.get('padding', 12)}px",
                "box-shadow": shapes.get("shadow", "0 2px 4px rgba(0, 0, 0, 0.1)"),
                "font-family": typography.get("font_family", "Inter, sans-serif"),
                "color": colors.get("text", "#333333"),
                "transition": f"all {animations.get('transition_duration', 0.3)}s ease-in-out"
            },
            "title": {
                "font-size": f"{typography.get('title_size', 16)}px",
                "font-weight": "bold",
                "margin-bottom": "4px",
                "color": colors.get("text", "#333333")
            },
            "subtitle": {
                "font-size": f"{typography.get('subtitle_size', 14)}px",
                "color": colors.get("text", "#333333"),
                "opacity": "0.8",
                "margin-bottom": "8px"
            },
            "description": {
                "font-size": f"{typography.get('body_size', 14)}px",
                "margin-bottom": "12px",
                "color": colors.get("text", "#333333")
            },
            "priority": {
                "font-size": f"{typography.get('caption_size', 12)}px",
                "padding": "2px 6px",
                "border-radius": "4px",
                "display": "inline-block",
                "margin-bottom": "8px"
            },
            "attributes": {
                "display": "flex",
                "flex-wrap": "wrap",
                "gap": "8px",
                "margin-bottom": "12px"
            },
            "attribute": {
                "font-size": f"{typography.get('body_size', 14)}px",
                "background-color": "rgba(0, 0, 0, 0.05)",
                "padding": "4px 8px",
                "border-radius": "4px"
            },
            "related_contexts": {
                "margin-top": "12px",
                "margin-bottom": "12px"
            },
            "related_context": {
                "font-size": f"{typography.get('body_size', 14)}px",
                "padding": "4px 8px",
                "border-radius": "4px",
                "background-color": "rgba(0, 0, 0, 0.05)",
                "margin-bottom": "4px",
                "cursor": "pointer"
            },
            "actions": {
                "display": "flex",
                "gap": "8px",
                "margin-top": "12px"
            },
            "action": {
                "font-size": f"{typography.get('body_size', 14)}px",
                "padding": "6px 12px",
                "border-radius": "4px",
                "background-color": colors.get("accent", "#3498DB"),
                "color": "#FFFFFF",
                "cursor": "pointer",
                "border": "none"
            },
            "timestamp": {
                "font-size": f"{typography.get('caption_size', 12)}px",
                "color": colors.get("text", "#333333"),
                "opacity": "0.6",
                "margin-top": "12px"
            }
        }
        
        # Add priority-specific styles
        if priority == "high":
            css["priority"]["background-color"] = colors.get("critical", "#E74C3C")
            css["priority"]["color"] = "#FFFFFF"
            css["container"]["border-left"] = f"4px solid {colors.get('critical', '#E74C3C')}"
            
            if animations.get("highlight_pulse", True):
                css["container"]["animation"] = "pulse 2s infinite"
        
        elif priority == "medium":
            css["priority"]["background-color"] = colors.get("warning", "#F39C12")
            css["priority"]["color"] = "#FFFFFF"
            css["container"]["border-left"] = f"4px solid {colors.get('warning', '#F39C12')}"
        
        elif priority == "low":
            css["priority"]["background-color"] = colors.get("info", "#3498DB")
            css["priority"]["color"] = "#FFFFFF"
        
        # Generate HTML structure based on mode
        html_structure = {
            "tag": "div",
            "attributes": {
                "id": f"context-{context_type}-{context_id}",
                "class": f"context context-{style_id} context-{mode} context-{priority}"
            },
            "children": [
                {
                    "tag": "div",
                    "attributes": {"class": "context-header"},
                    "children": [
                        {
                            "tag": "div",
                            "attributes": {"class": "context-title"},
                            "text": content.get("title", "Unknown Context")
                        },
                        {
                            "tag": "div",
                            "attributes": {"class": "context-subtitle"},
                            "text": content.get("subtitle", "")
                        },
                        {
                            "tag": "div",
                            "attributes": {"class": "context-priority"},
                            "text": content.get("priority", priority)
                        }
                    ]
                },
                {
                    "tag": "div",
                    "attributes": {"class": "context-description"},
                    "text": content.get("description", "")
                }
            ]
        }
        
        # Add attributes if available
        if content.get("attributes") and mode in [ContextVisualizationMode.STANDARD.value, ContextVisualizationMode.DETAILED.value, ContextVisualizationMode.IMMERSIVE.value]:
            attributes_container = {
                "tag": "div",
                "attributes": {"class": "context-attributes"},
                "children": []
            }
            
            for attribute in content.get("attributes", []):
                attributes_container["children"].append({
                    "tag": "div",
                    "attributes": {"class": "context-attribute"},
                    "text": f"{attribute.get('name', '')}: {attribute.get('value', '')}"
                })
            
            html_structure["children"].append(attributes_container)
        
        # Add related contexts if available
        if content.get("related_contexts") and mode in [ContextVisualizationMode.STANDARD.value, ContextVisualizationMode.DETAILED.value, ContextVisualizationMode.IMMERSIVE.value]:
            related_contexts_container = {
                "tag": "div",
                "attributes": {"class": "context-related-contexts"},
                "children": [
                    {
                        "tag": "div",
                        "attributes": {"class": "context-section-title"},
                        "text": "Related Contexts"
                    }
                ]
            }
            
            for related_context in content.get("related_contexts", []):
                related_contexts_container["children"].append({
                    "tag": "div",
                    "attributes": {
                        "class": "context-related-context",
                        "data-context-type": related_context.get("type", ""),
                        "data-context-id": related_context.get("id", "")
                    },
                    "text": related_context.get("name", "Unknown Context")
                })
            
            html_structure["children"].append(related_contexts_container)
        
        # Add actions if available
        if content.get("actions") and mode in [ContextVisualizationMode.STANDARD.value, ContextVisualizationMode.DETAILED.value, ContextVisualizationMode.IMMERSIVE.value]:
            actions_container = {
                "tag": "div",
                "attributes": {"class": "context-actions"},
                "children": []
            }
            
            for action in content.get("actions", []):
                actions_container["children"].append({
                    "tag": "button",
                    "attributes": {
                        "class": "context-action",
                        "data-action": action.get("id", ""),
                        "data-context-type": context_type,
                        "data-context-id": context_id
                    },
                    "text": action.get("name", "Action")
                })
            
            html_structure["children"].append(actions_container)
        
        # Add timestamp
        html_structure["children"].append({
            "tag": "div",
            "attributes": {"class": "context-timestamp"},
            "text": f"Updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(content.get('timestamp', time.time())))}"
        })
        
        # Return rendering instructions
        return {
            "context_type": context_type,
            "context_id": context_id,
            "platform": "web",
            "css": css,
            "html": html_structure,
            "animations": {
                "pulse": "@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }",
                "fade": "@keyframes fade { 0% { opacity: 0; } 100% { opacity: 1; } }"
            },
            "event_handlers": {
                "click": f"handleContextClick('{context_type}', '{context_id}')",
                "mouseover": f"handleContextMouseOver('{context_type}', '{context_id}')",
                "mouseout": f"handleContextMouseOut('{context_type}', '{context_id}')"
            }
        }

    def _generate_mobile_rendering(
        self,
        context_type: str,
        context_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mobile rendering instructions for a context.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            visualization_data: Visualization data
            
        Returns:
            Mobile rendering instructions
        """
        # Similar to web rendering but with mobile-specific adjustments
        web_rendering = self._generate_web_rendering(context_type, context_id, visualization_data)
        
        # Adjust for mobile
        web_rendering["platform"] = "mobile"
        
        # Make touch-friendly adjustments
        if "css" in web_rendering:
            # Increase touch targets
            if "action" in web_rendering["css"]:
                web_rendering["css"]["action"]["padding"] = "10px 16px"
            
            # Adjust font sizes
            for element in ["title", "subtitle", "body", "caption"]:
                if element in web_rendering["css"]:
                    current_size = web_rendering["css"][element].get("font-size", "14px")
                    size_value = int(current_size.replace("px", ""))
                    web_rendering["css"][element]["font-size"] = f"{size_value + 2}px"
        
        # Replace mouse events with touch events
        if "event_handlers" in web_rendering:
            web_rendering["event_handlers"] = {
                "touchstart": f"handleContextTouchStart('{context_type}', '{context_id}')",
                "touchend": f"handleContextTouchEnd('{context_type}', '{context_id}')"
            }
        
        return web_rendering

    def _generate_desktop_rendering(
        self,
        context_type: str,
        context_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate desktop rendering instructions for a context.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            visualization_data: Visualization data
            
        Returns:
            Desktop rendering instructions
        """
        # For desktop native apps
        # This would generate platform-specific instructions
        # For simplicity, we'll use a modified version of web rendering
        
        web_rendering = self._generate_web_rendering(context_type, context_id, visualization_data)
        
        # Adjust for desktop
        web_rendering["platform"] = "desktop"
        
        # Add desktop-specific properties
        web_rendering["desktop_properties"] = {
            "window_title": visualization_data.get("content", {}).get("title", "Context"),
            "window_icon": "context_icon",
            "window_size": {"width": 400, "height": 300},
            "window_resizable": True,
            "window_always_on_top": False,
            "window_frameless": False,
            "window_transparent": False
        }
        
        return web_rendering

    def _generate_ar_rendering(
        self,
        context_type: str,
        context_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AR rendering instructions for a context.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            visualization_data: Visualization data
            
        Returns:
            AR rendering instructions
        """
        # For AR applications
        # This would generate AR-specific rendering instructions
        
        mode = visualization_data.get("mode", ContextVisualizationMode.STANDARD.value)
        style_id = visualization_data.get("style", ContextVisualizationStyle.STANDARD.value)
        priority = visualization_data.get("priority", "normal")
        content = visualization_data.get("content", {})
        colors = visualization_data.get("colors", {})
        
        # Generate AR-specific rendering instructions
        ar_rendering = {
            "context_type": context_type,
            "context_id": context_id,
            "platform": "ar",
            "ar_object": {
                "type": "panel",
                "width": 0.4,
                "height": 0.3,
                "depth": 0.01,
                "color": colors.get("background", "rgba(255, 255, 255, 0.9)"),
                "border_color": colors.get("border", "#CCCCCC"),
                "border_width": 0.002,
                "corner_radius": 0.01,
                "opacity": 0.9
            },
            "ar_text": {
                "title": {
                    "text": content.get("title", "Unknown Context"),
                    "position": {"x": 0, "y": 0.12, "z": 0.011},
                    "scale": 0.025,
                    "color": colors.get("text", "#333333")
                },
                "subtitle": {
                    "text": content.get("subtitle", ""),
                    "position": {"x": 0, "y": 0.08, "z": 0.011},
                    "scale": 0.02,
                    "color": colors.get("text", "#333333"),
                    "opacity": 0.8
                },
                "description": {
                    "text": content.get("description", ""),
                    "position": {"x": 0, "y": 0.04, "z": 0.011},
                    "scale": 0.018,
                    "color": colors.get("text", "#333333"),
                    "max_width": 0.35
                },
                "priority": {
                    "text": content.get("priority", priority),
                    "position": {"x": 0.15, "y": 0.12, "z": 0.011},
                    "scale": 0.018,
                    "color": "#FFFFFF",
                    "background": self._get_priority_color(priority, colors)
                }
            },
            "ar_interactions": {
                "tap": {
                    "action": "select_context",
                    "parameters": {"context_type": context_type, "context_id": context_id}
                },
                "long_press": {
                    "action": "show_context_menu",
                    "parameters": {"context_type": context_type, "context_id": context_id}
                }
            },
            "ar_animations": {
                "idle": {
                    "type": "float",
                    "amplitude": 0.005,
                    "frequency": 0.5
                },
                "selected": {
                    "type": "pulse",
                    "scale_factor": 1.1,
                    "duration": 0.5
                }
            },
            "ar_positioning": {
                "attach_to": "user_gaze",
                "distance": 1.0,
                "follow_user": True,
                "collision_detection": True
            }
        }
        
        # Add priority-specific effects
        if priority == "high":
            ar_rendering["ar_animations"]["priority"] = {
                "type": "pulse",
                "color": colors.get("critical", "#E74C3C"),
                "intensity": 0.5,
                "frequency": 1.0
            }
            
            # Add border highlight
            ar_rendering["ar_object"]["border_color"] = colors.get("critical", "#E74C3C")
            ar_rendering["ar_object"]["border_width"] = 0.004
        
        elif priority == "medium":
            ar_rendering["ar_object"]["border_color"] = colors.get("warning", "#F39C12")
            ar_rendering["ar_object"]["border_width"] = 0.003
        
        # Add attributes if available and mode is appropriate
        if content.get("attributes") and mode in [ContextVisualizationMode.STANDARD.value, ContextVisualizationMode.DETAILED.value, ContextVisualizationMode.IMMERSIVE.value]:
            ar_rendering["ar_attributes"] = []
            
            for i, attribute in enumerate(content.get("attributes", [])[:3]):  # Limit to 3 attributes in AR
                ar_rendering["ar_attributes"].append({
                    "text": f"{attribute.get('name', '')}: {attribute.get('value', '')}",
                    "position": {"x": 0, "y": -0.02 - (i * 0.03), "z": 0.011},
                    "scale": 0.016,
                    "color": colors.get("text", "#333333")
                })
        
        return ar_rendering

    def _get_priority_color(
        self,
        priority: str,
        colors: Dict[str, str]
    ) -> str:
        """
        Get color for a priority.
        
        Args:
            priority: Priority value
            colors: Color definitions
            
        Returns:
            Color for the priority
        """
        if priority == "high":
            return colors.get("critical", "#E74C3C")
        elif priority == "medium":
            return colors.get("warning", "#F39C12")
        elif priority == "low":
            return colors.get("info", "#3498DB")
        else:
            return colors.get("info", "#3498DB")

    def animate_context(
        self,
        context_type: str,
        context_id: str,
        animation_type: str,
        duration: float = 1.0,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Animate a context.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            animation_type: Type of animation
            duration: Duration of animation in seconds
            callback: Optional callback function
            
        Returns:
            Animation ID
        """
        # Generate animation ID
        animation_id = str(uuid.uuid4())
        
        # Create cache key
        cache_key = f"{context_type}:{context_id}"
        
        # Create animation state
        animation_state = {
            "id": animation_id,
            "type": animation_type,
            "start_time": time.time(),
            "duration": duration,
            "progress": 0.0,
            "completed": False
        }
        
        # Store animation state
        self.animation_states[cache_key] = animation_state
        
        # Store callback if provided
        if callback:
            self.visualization_callbacks[animation_id] = callback
        
        # Clear cache for this context
        if cache_key in self.visualization_cache:
            del self.visualization_cache[cache_key]
        
        # In a real implementation, this would trigger the animation
        # For simplicity, we'll use a timer thread to simulate animation progress
        import threading
        
        def update_animation():
            # Update progress
            animation_state = self.animation_states.get(cache_key)
            if animation_state:
                animation_state["progress"] = 1.0
                animation_state["completed"] = True
                
                # Call callback if registered
                if animation_id in self.visualization_callbacks:
                    callback = self.visualization_callbacks[animation_id]
                    try:
                        callback(animation_state)
                    except Exception as e:
                        logger.error(f"Error in animation callback: {e}")
                    
                    # Remove callback after calling
                    del self.visualization_callbacks[animation_id]
        
        # Schedule animation completion
        threading.Timer(duration, update_animation).start()
        
        logger.debug(f"Started animation {animation_id} of type {animation_type} for context {context_type}:{context_id}")
        return animation_id

    def get_animation_state(
        self,
        context_type: str,
        context_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the animation state of a context.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            
        Returns:
            Animation state if found, None otherwise
        """
        cache_key = f"{context_type}:{context_id}"
        return self.animation_states.get(cache_key)

    def create_visualization_style(
        self,
        style_name: str,
        style_data: Dict[str, Any]
    ) -> str:
        """
        Create a custom visualization style.
        
        Args:
            style_name: Name of the style
            style_data: Style data
            
        Returns:
            Style ID
        """
        # Generate style ID
        style_id = f"custom_{style_name.lower().replace(' ', '_')}"
        
        # Store style
        self.visualization_styles[style_id] = {
            "name": style_name,
            "description": style_data.get("description", f"Custom style: {style_name}"),
            "colors": style_data.get("colors", {}),
            "shapes": style_data.get("shapes", {}),
            "animations": style_data.get("animations", {}),
            "typography": style_data.get("typography", {})
        }
        
        logger.info(f"Created custom visualization style {style_id}")
        return style_id

    def delete_visualization_style(self, style_id: str) -> bool:
        """
        Delete a custom visualization style.
        
        Args:
            style_id: ID of the style
            
        Returns:
            True if deletion was successful, False otherwise
        """
        # Cannot delete built-in styles
        if style_id in [s.value for s in ContextVisualizationStyle]:
            logger.warning(f"Cannot delete built-in style: {style_id}")
            return False
        
        # Delete style
        if style_id in self.visualization_styles:
            del self.visualization_styles[style_id]
            logger.info(f"Deleted visualization style {style_id}")
            return True
        
        logger.warning(f"Unknown visualization style: {style_id}")
        return False

    def get_visualization_style(self, style_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a visualization style.
        
        Args:
            style_id: ID of the style
            
        Returns:
            Style data if found, None otherwise
        """
        return self.visualization_styles.get(style_id)

    def get_all_visualization_styles(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all visualization styles.
        
        Returns:
            Dictionary of style data
        """
        return self.visualization_styles

    def export_visualization_style(
        self,
        style_id: str,
        format: str = "json"
    ) -> Optional[str]:
        """
        Export a visualization style to a specified format.
        
        Args:
            style_id: ID of the style
            format: Export format ("json" or "yaml")
            
        Returns:
            Exported style as string if successful, None otherwise
        """
        if style_id not in self.visualization_styles:
            logger.warning(f"Unknown visualization style: {style_id}")
            return None
        
        # Get style
        style = self.visualization_styles[style_id]
        
        if format.lower() == "json":
            return json.dumps(style, indent=2)
        
        elif format.lower() == "yaml":
            try:
                import yaml
                return yaml.dump(style, default_flow_style=False)
            except ImportError:
                logger.error("PyYAML not installed, falling back to JSON")
                return json.dumps(style, indent=2)
        
        else:
            logger.error(f"Unsupported export format: {format}")
            return None

    def import_visualization_style(
        self,
        data: str,
        format: str = "json"
    ) -> Optional[str]:
        """
        Import a visualization style from a specified format.
        
        Args:
            data: Style data
            format: Import format ("json" or "yaml")
            
        Returns:
            Style ID if import was successful, None otherwise
        """
        try:
            if format.lower() == "json":
                style_data = json.loads(data)
            
            elif format.lower() == "yaml":
                try:
                    import yaml
                    style_data = yaml.safe_load(data)
                except ImportError:
                    logger.error("PyYAML not installed")
                    return None
            
            else:
                logger.error(f"Unsupported import format: {format}")
                return None
            
            # Create style
            style_name = style_data.get("name", f"Imported Style {int(time.time())}")
            return self.create_visualization_style(style_name, style_data)
        
        except Exception as e:
            logger.error(f"Error importing visualization style: {e}")
            return None
