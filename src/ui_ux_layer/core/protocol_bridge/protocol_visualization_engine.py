"""
Protocol Visualization Engine Module for the UI/UX Layer of Industriverse

This module provides visualization capabilities for protocol interactions in the UI/UX Layer,
enabling rich, interactive, and adaptive visual representations of protocol exchanges
between agents, layers, and systems.

The Protocol Visualization Engine is responsible for:
1. Rendering protocol exchange visual representations
2. Visualizing MCP (Model Context Protocol) interactions
3. Visualizing A2A (Agent to Agent) interactions
4. Supporting different visualization modes and styles
5. Integrating with the Universal Skin for consistent visual language

This module works closely with the Protocol Bridge components to provide
a cohesive visual experience for protocol interactions.
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from enum import Enum
import json
import math

from ..rendering_engine.theme_manager import ThemeManager
from .mcp_integration_manager import MCPIntegrationManager
from .a2a_integration_manager import A2AIntegrationManager

logger = logging.getLogger(__name__)

class ProtocolVisualizationMode(Enum):
    """Enumeration of protocol visualization modes."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    TECHNICAL = "technical"
    FLOW = "flow"


class ProtocolVisualizationStyle(Enum):
    """Enumeration of protocol visualization styles."""
    STANDARD = "standard"
    INDUSTRIAL = "industrial"
    TECHNICAL = "technical"
    ORGANIC = "organic"
    CUSTOM = "custom"


class ProtocolVisualizationEngine:
    """
    Provides visualization capabilities for protocol interactions in the UI/UX Layer.
    
    This class is responsible for rendering protocol exchange visual representations,
    adapting to different platforms and devices, and providing animation effects.
    """

    def __init__(
        self,
        mcp_integration_manager: MCPIntegrationManager,
        a2a_integration_manager: A2AIntegrationManager,
        theme_manager: ThemeManager
    ):
        """
        Initialize the ProtocolVisualizationEngine.
        
        Args:
            mcp_integration_manager: Manager for MCP integration
            a2a_integration_manager: Manager for A2A integration
            theme_manager: Manager for UI themes
        """
        self.mcp_integration_manager = mcp_integration_manager
        self.a2a_integration_manager = a2a_integration_manager
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
        
        logger.info("ProtocolVisualizationEngine initialized")

    def _initialize_default_styles(self):
        """Initialize default visualization styles."""
        # Standard style
        self.visualization_styles[ProtocolVisualizationStyle.STANDARD.value] = {
            "name": "Standard",
            "description": "Default visualization style for protocol interactions",
            "colors": {
                "background": "#FFFFFF",
                "border": "#CCCCCC",
                "text": "#333333",
                "icon": "#666666",
                "accent": "#3498DB",
                "mcp_color": "#9B59B6",
                "a2a_color": "#2ECC71",
                "request_color": "#3498DB",
                "response_color": "#2ECC71",
                "error_color": "#E74C3C"
            },
            "shapes": {
                "border_radius": 8,
                "icon_size": 24,
                "padding": 12,
                "shadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                "line_width": 2,
                "arrow_size": 8
            },
            "animations": {
                "transition_duration": 0.3,
                "hover_scale": 1.05,
                "message_travel_duration": 0.8,
                "pulse_duration": 1.5
            },
            "typography": {
                "font_family": "Inter, sans-serif",
                "title_size": 16,
                "subtitle_size": 14,
                "body_size": 14,
                "caption_size": 12,
                "code_font_family": "JetBrains Mono, monospace"
            }
        }
        
        # Industrial style
        self.visualization_styles[ProtocolVisualizationStyle.INDUSTRIAL.value] = {
            "name": "Industrial",
            "description": "Industrial-themed visualization style for protocol interactions",
            "colors": {
                "background": "#2C3E50",
                "border": "#34495E",
                "text": "#ECF0F1",
                "icon": "#BDC3C7",
                "accent": "#F1C40F",
                "mcp_color": "#9B59B6",
                "a2a_color": "#2ECC71",
                "request_color": "#3498DB",
                "response_color": "#2ECC71",
                "error_color": "#E74C3C"
            },
            "shapes": {
                "border_radius": 2,
                "icon_size": 24,
                "padding": 10,
                "shadow": "0 3px 6px rgba(0, 0, 0, 0.3)",
                "line_width": 3,
                "arrow_size": 10
            },
            "animations": {
                "transition_duration": 0.2,
                "hover_scale": 1.02,
                "message_travel_duration": 0.6,
                "pulse_duration": 1.2
            },
            "typography": {
                "font_family": "Roboto Mono, monospace",
                "title_size": 16,
                "subtitle_size": 14,
                "body_size": 14,
                "caption_size": 12,
                "code_font_family": "Roboto Mono, monospace"
            }
        }
        
        # Technical style
        self.visualization_styles[ProtocolVisualizationStyle.TECHNICAL.value] = {
            "name": "Technical",
            "description": "Technical visualization style for protocol interactions",
            "colors": {
                "background": "#1E1E1E",
                "border": "#333333",
                "text": "#FFFFFF",
                "icon": "#CCCCCC",
                "accent": "#61DAFB",
                "mcp_color": "#C678DD",
                "a2a_color": "#98C379",
                "request_color": "#61AFEF",
                "response_color": "#98C379",
                "error_color": "#E06C75"
            },
            "shapes": {
                "border_radius": 0,
                "icon_size": 24,
                "padding": 12,
                "shadow": "0 0 10px rgba(97, 218, 251, 0.2)",
                "line_width": 2,
                "arrow_size": 8
            },
            "animations": {
                "transition_duration": 0.15,
                "hover_scale": 1.0,
                "message_travel_duration": 0.5,
                "pulse_duration": 1.0
            },
            "typography": {
                "font_family": "JetBrains Mono, monospace",
                "title_size": 16,
                "subtitle_size": 14,
                "body_size": 14,
                "caption_size": 12,
                "code_font_family": "JetBrains Mono, monospace"
            }
        }
        
        # Organic style
        self.visualization_styles[ProtocolVisualizationStyle.ORGANIC.value] = {
            "name": "Organic",
            "description": "Organic visualization style for protocol interactions",
            "colors": {
                "background": "#F5F5F5",
                "border": "#E0E0E0",
                "text": "#333333",
                "icon": "#555555",
                "accent": "#8BC34A",
                "mcp_color": "#9C27B0",
                "a2a_color": "#4CAF50",
                "request_color": "#2196F3",
                "response_color": "#4CAF50",
                "error_color": "#F44336"
            },
            "shapes": {
                "border_radius": 20,
                "icon_size": 24,
                "padding": 14,
                "shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                "line_width": 3,
                "arrow_size": 10
            },
            "animations": {
                "transition_duration": 0.4,
                "hover_scale": 1.08,
                "message_travel_duration": 1.0,
                "pulse_duration": 2.0
            },
            "typography": {
                "font_family": "Quicksand, sans-serif",
                "title_size": 18,
                "subtitle_size": 16,
                "body_size": 16,
                "caption_size": 14,
                "code_font_family": "Fira Code, monospace"
            }
        }

    def set_visualization_mode(
        self,
        protocol_type: str,
        mode: ProtocolVisualizationMode
    ) -> bool:
        """
        Set the visualization mode for a protocol type.
        
        Args:
            protocol_type: Type of protocol (e.g., "mcp", "a2a")
            mode: Visualization mode
            
        Returns:
            True if mode was set, False otherwise
        """
        # Set mode
        self.visualization_modes[protocol_type] = mode.value
        
        # Clear cache for this protocol type
        for key in list(self.visualization_cache.keys()):
            if key.startswith(f"{protocol_type}:"):
                del self.visualization_cache[key]
        
        logger.debug(f"Set visualization mode for protocol type {protocol_type} to {mode.value}")
        return True

    def set_visualization_style(
        self,
        protocol_type: str,
        style: ProtocolVisualizationStyle
    ) -> bool:
        """
        Set the visualization style for a protocol type.
        
        Args:
            protocol_type: Type of protocol (e.g., "mcp", "a2a")
            style: Visualization style
            
        Returns:
            True if style was set, False otherwise
        """
        # Verify style exists
        if style.value not in self.visualization_styles:
            logger.warning(f"Unknown visualization style: {style.value}")
            return False
        
        # Set style
        self.visualization_styles[protocol_type] = style.value
        
        # Clear cache for this protocol type
        for key in list(self.visualization_cache.keys()):
            if key.startswith(f"{protocol_type}:"):
                del self.visualization_cache[key]
        
        logger.debug(f"Set visualization style for protocol type {protocol_type} to {style.value}")
        return True

    def get_visualization_data(
        self,
        protocol_type: str,
        exchange_id: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get visualization data for a protocol exchange.
        
        Args:
            protocol_type: Type of protocol (e.g., "mcp", "a2a")
            exchange_id: ID of the protocol exchange
            force_refresh: Whether to force a refresh of the data
            
        Returns:
            Visualization data
        """
        # Create cache key
        cache_key = f"{protocol_type}:{exchange_id}"
        
        # Check cache if not forcing refresh
        if not force_refresh and cache_key in self.visualization_cache:
            return self.visualization_cache[cache_key]
        
        # Get exchange data based on protocol type
        exchange_data = None
        
        if protocol_type == "mcp":
            exchange_data = self.mcp_integration_manager.get_exchange(exchange_id)
        elif protocol_type == "a2a":
            exchange_data = self.a2a_integration_manager.get_exchange(exchange_id)
        
        if not exchange_data:
            logger.warning(f"Unknown protocol exchange: {protocol_type}:{exchange_id}")
            return {}
        
        # Get visualization mode
        mode = self.visualization_modes.get(protocol_type, ProtocolVisualizationMode.STANDARD.value)
        
        # Get visualization style
        style_id = self.visualization_styles.get(protocol_type, ProtocolVisualizationStyle.STANDARD.value)
        style = self.visualization_styles.get(style_id, self.visualization_styles[ProtocolVisualizationStyle.STANDARD.value])
        
        # Get current theme
        theme = self.theme_manager.get_current_theme()
        
        # Build visualization data
        visualization_data = {
            "protocol_type": protocol_type,
            "exchange_id": exchange_id,
            "mode": mode,
            "style": style_id,
            "name": exchange_data.get("name", f"{protocol_type.upper()} Exchange"),
            "description": exchange_data.get("description", ""),
            "timestamp": exchange_data.get("timestamp", time.time()),
            "status": exchange_data.get("status", "unknown"),
            "colors": self._merge_colors(style["colors"], theme.get("colors", {})),
            "shapes": style["shapes"],
            "animations": style["animations"],
            "typography": style["typography"],
            "content": self._get_content_for_mode(protocol_type, exchange_data, mode),
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
        protocol_type: str,
        exchange_data: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """
        Get content data for a specific visualization mode.
        
        Args:
            protocol_type: Type of protocol
            exchange_data: Protocol exchange data
            mode: Visualization mode
            
        Returns:
            Content data
        """
        content = {
            "title": exchange_data.get("name", f"{protocol_type.upper()} Exchange"),
            "subtitle": f"{protocol_type.upper()} Protocol",
            "description": exchange_data.get("description", ""),
            "timestamp": exchange_data.get("timestamp", time.time()),
            "status": exchange_data.get("status", "unknown"),
            "source": exchange_data.get("source", {}),
            "target": exchange_data.get("target", {}),
            "messages": [],
            "metadata": {}
        }
        
        # Add mode-specific content
        if mode == ProtocolVisualizationMode.MINIMAL.value:
            # Minimal content, just the basics
            # Add latest message
            messages = exchange_data.get("messages", [])
            if messages:
                content["messages"] = [messages[-1]]
        
        elif mode == ProtocolVisualizationMode.STANDARD.value:
            # Add all messages
            content["messages"] = exchange_data.get("messages", [])
            
            # Add basic metadata
            content["metadata"] = {
                "protocol_version": exchange_data.get("protocol_version", "1.0"),
                "exchange_type": exchange_data.get("exchange_type", "request-response"),
                "duration": exchange_data.get("duration", 0)
            }
        
        elif mode == ProtocolVisualizationMode.DETAILED.value:
            # Add all messages
            content["messages"] = exchange_data.get("messages", [])
            
            # Add detailed metadata
            content["metadata"] = {
                "protocol_version": exchange_data.get("protocol_version", "1.0"),
                "exchange_type": exchange_data.get("exchange_type", "request-response"),
                "duration": exchange_data.get("duration", 0),
                "created_at": exchange_data.get("created_at", time.time()),
                "updated_at": exchange_data.get("updated_at", time.time()),
                "tags": exchange_data.get("tags", []),
                "security": exchange_data.get("security", {}),
                "performance": exchange_data.get("performance", {})
            }
            
            # Add related exchanges
            content["related_exchanges"] = exchange_data.get("related_exchanges", [])
        
        elif mode == ProtocolVisualizationMode.TECHNICAL.value:
            # Add all messages with technical details
            messages = exchange_data.get("messages", [])
            technical_messages = []
            
            for message in messages:
                technical_message = message.copy()
                technical_message["raw_data"] = message.get("raw_data", "{}")
                technical_message["headers"] = message.get("headers", {})
                technical_message["encoding"] = message.get("encoding", "utf-8")
                technical_message["size"] = message.get("size", 0)
                technical_messages.append(technical_message)
            
            content["messages"] = technical_messages
            
            # Add technical metadata
            content["metadata"] = {
                "protocol_version": exchange_data.get("protocol_version", "1.0"),
                "exchange_type": exchange_data.get("exchange_type", "request-response"),
                "duration": exchange_data.get("duration", 0),
                "created_at": exchange_data.get("created_at", time.time()),
                "updated_at": exchange_data.get("updated_at", time.time()),
                "tags": exchange_data.get("tags", []),
                "security": exchange_data.get("security", {}),
                "performance": exchange_data.get("performance", {}),
                "network": exchange_data.get("network", {}),
                "debug_info": exchange_data.get("debug_info", {})
            }
        
        elif mode == ProtocolVisualizationMode.FLOW.value:
            # Add all messages
            content["messages"] = exchange_data.get("messages", [])
            
            # Add flow-specific data
            content["flow"] = {
                "nodes": exchange_data.get("flow_nodes", []),
                "edges": exchange_data.get("flow_edges", []),
                "layout": exchange_data.get("flow_layout", "horizontal")
            }
        
        return content

    def register_custom_renderer(
        self,
        protocol_type: str,
        renderer_function: Callable[[str, str, Dict[str, Any]], Dict[str, Any]]
    ) -> bool:
        """
        Register a custom renderer for a protocol type.
        
        Args:
            protocol_type: Type of protocol
            renderer_function: Function to render the protocol
            
        Returns:
            True if registration was successful, False otherwise
        """
        self.custom_renderers[protocol_type] = renderer_function
        logger.info(f"Registered custom renderer for protocol type {protocol_type}")
        return True

    def unregister_custom_renderer(self, protocol_type: str) -> bool:
        """
        Unregister a custom renderer for a protocol type.
        
        Args:
            protocol_type: Type of protocol
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if protocol_type in self.custom_renderers:
            del self.custom_renderers[protocol_type]
            logger.info(f"Unregistered custom renderer for protocol type {protocol_type}")
            return True
        
        logger.warning(f"No custom renderer registered for protocol type {protocol_type}")
        return False

    def render_protocol_exchange(
        self,
        protocol_type: str,
        exchange_id: str,
        target_platform: str = "web",
        target_container: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Render a protocol exchange for a specific platform.
        
        Args:
            protocol_type: Type of protocol
            exchange_id: ID of the protocol exchange
            target_platform: Target platform for rendering
            target_container: Optional target container ID
            callback: Optional callback function
            
        Returns:
            Rendering result
        """
        # Get visualization data
        visualization_data = self.get_visualization_data(protocol_type, exchange_id)
        
        if not visualization_data:
            logger.warning(f"Failed to get visualization data for protocol exchange {protocol_type}:{exchange_id}")
            return {}
        
        # Check for custom renderer
        if protocol_type in self.custom_renderers:
            # Use custom renderer
            renderer = self.custom_renderers[protocol_type]
            result = renderer(protocol_type, exchange_id, visualization_data)
        else:
            # Use default renderer
            result = self._default_renderer(protocol_type, exchange_id, visualization_data, target_platform)
        
        # Store callback if provided
        if callback:
            cache_key = f"{protocol_type}:{exchange_id}"
            self.visualization_callbacks[cache_key] = callback
        
        return result

    def _default_renderer(
        self,
        protocol_type: str,
        exchange_id: str,
        visualization_data: Dict[str, Any],
        target_platform: str
    ) -> Dict[str, Any]:
        """
        Default renderer for protocol exchanges.
        
        Args:
            protocol_type: Type of protocol
            exchange_id: ID of the protocol exchange
            visualization_data: Visualization data
            target_platform: Target platform for rendering
            
        Returns:
            Rendering result
        """
        # This is a simplified implementation
        # In a real system, this would generate actual rendering instructions
        
        mode = visualization_data.get("mode", ProtocolVisualizationMode.STANDARD.value)
        style = visualization_data.get("style", ProtocolVisualizationStyle.STANDARD.value)
        status = visualization_data.get("status", "unknown")
        
        # Generate rendering instructions based on platform
        if target_platform == "web":
            return self._generate_web_rendering(protocol_type, exchange_id, visualization_data)
        
        elif target_platform == "mobile":
            return self._generate_mobile_rendering(protocol_type, exchange_id, visualization_data)
        
        elif target_platform == "desktop":
            return self._generate_desktop_rendering(protocol_type, exchange_id, visualization_data)
        
        else:
            logger.warning(f"Unknown target platform: {target_platform}")
            return {}

    def _generate_web_rendering(
        self,
        protocol_type: str,
        exchange_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate web rendering instructions for a protocol exchange.
        
        Args:
            protocol_type: Type of protocol
            exchange_id: ID of the protocol exchange
            visualization_data: Visualization data
            
        Returns:
            Web rendering instructions
        """
        mode = visualization_data.get("mode", ProtocolVisualizationMode.STANDARD.value)
        style_id = visualization_data.get("style", ProtocolVisualizationStyle.STANDARD.value)
        status = visualization_data.get("status", "unknown")
        content = visualization_data.get("content", {})
        colors = visualization_data.get("colors", {})
        shapes = visualization_data.get("shapes", {})
        typography = visualization_data.get("typography", {})
        animations = visualization_data.get("animations", {})
        
        # Get protocol-specific color
        protocol_color = colors.get(f"{protocol_type}_color", colors.get("accent", "#3498DB"))
        
        # Generate CSS
        css = {
            "container": {
                "background-color": colors.get("background", "#FFFFFF"),
                "border": f"1px solid {colors.get('border', '#CCCCCC')}",
                "border-left": f"4px solid {protocol_color}",
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
                "color": protocol_color,
                "margin-bottom": "8px"
            },
            "description": {
                "font-size": f"{typography.get('body_size', 14)}px",
                "margin-bottom": "12px",
                "color": colors.get("text", "#333333")
            },
            "status": {
                "font-size": f"{typography.get('caption_size', 12)}px",
                "padding": "2px 6px",
                "border-radius": "4px",
                "display": "inline-block",
                "margin-bottom": "8px"
            },
            "metadata": {
                "font-size": f"{typography.get('caption_size', 12)}px",
                "color": colors.get("text", "#333333"),
                "opacity": "0.7",
                "margin-bottom": "12px"
            },
            "messages": {
                "margin-top": "16px",
                "border-top": f"1px solid {colors.get('border', '#CCCCCC')}",
                "padding-top": "12px"
            },
            "message": {
                "padding": "8px",
                "margin-bottom": "8px",
                "border-radius": f"{shapes.get('border_radius', 8)}px",
                "font-family": typography.get("code_font_family", "monospace"),
                "font-size": f"{typography.get('body_size', 14)}px"
            },
            "message_request": {
                "background-color": "rgba(52, 152, 219, 0.1)",
                "border-left": f"3px solid {colors.get('request_color', '#3498DB')}"
            },
            "message_response": {
                "background-color": "rgba(46, 204, 113, 0.1)",
                "border-left": f"3px solid {colors.get('response_color', '#2ECC71')}"
            },
            "message_error": {
                "background-color": "rgba(231, 76, 60, 0.1)",
                "border-left": f"3px solid {colors.get('error_color', '#E74C3C')}"
            },
            "message_header": {
                "font-weight": "bold",
                "margin-bottom": "4px",
                "display": "flex",
                "justify-content": "space-between"
            },
            "message_content": {
                "white-space": "pre-wrap",
                "overflow-x": "auto"
            },
            "timestamp": {
                "font-size": f"{typography.get('caption_size', 12)}px",
                "color": colors.get("text", "#333333"),
                "opacity": "0.6",
                "margin-top": "12px"
            }
        }
        
        # Add status-specific styles
        if status == "completed":
            css["status"]["background-color"] = colors.get("response_color", "#2ECC71")
            css["status"]["color"] = "#FFFFFF"
        
        elif status == "in_progress":
            css["status"]["background-color"] = colors.get("request_color", "#3498DB")
            css["status"]["color"] = "#FFFFFF"
        
        elif status == "error":
            css["status"]["background-color"] = colors.get("error_color", "#E74C3C")
            css["status"]["color"] = "#FFFFFF"
        
        # Generate HTML structure based on mode
        html_structure = {
            "tag": "div",
            "attributes": {
                "id": f"protocol-{protocol_type}-{exchange_id}",
                "class": f"protocol protocol-{style_id} protocol-{mode} protocol-{status}"
            },
            "children": [
                {
                    "tag": "div",
                    "attributes": {"class": "protocol-header"},
                    "children": [
                        {
                            "tag": "div",
                            "attributes": {"class": "protocol-title"},
                            "text": content.get("title", f"{protocol_type.upper()} Exchange")
                        },
                        {
                            "tag": "div",
                            "attributes": {"class": "protocol-subtitle"},
                            "text": content.get("subtitle", f"{protocol_type.upper()} Protocol")
                        },
                        {
                            "tag": "div",
                            "attributes": {"class": "protocol-status"},
                            "text": content.get("status", status)
                        }
                    ]
                }
            ]
        }
        
        # Add description if available
        if content.get("description"):
            html_structure["children"].append({
                "tag": "div",
                "attributes": {"class": "protocol-description"},
                "text": content.get("description", "")
            })
        
        # Add metadata if available and mode is appropriate
        if content.get("metadata") and mode in [ProtocolVisualizationMode.STANDARD.value, ProtocolVisualizationMode.DETAILED.value, ProtocolVisualizationMode.TECHNICAL.value]:
            metadata_items = []
            
            for key, value in content.get("metadata", {}).items():
                if isinstance(value, (dict, list)):
                    continue  # Skip complex objects in simple metadata display
                
                metadata_items.append(f"{key}: {value}")
            
            if metadata_items:
                html_structure["children"].append({
                    "tag": "div",
                    "attributes": {"class": "protocol-metadata"},
                    "text": " | ".join(metadata_items)
                })
        
        # Add messages if available
        if content.get("messages"):
            messages_container = {
                "tag": "div",
                "attributes": {"class": "protocol-messages"},
                "children": []
            }
            
            for message in content.get("messages", []):
                message_type = message.get("type", "request")
                message_class = f"protocol-message-{message_type}"
                
                message_element = {
                    "tag": "div",
                    "attributes": {
                        "class": f"protocol-message {message_class}",
                        "data-message-id": message.get("id", "")
                    },
                    "children": [
                        {
                            "tag": "div",
                            "attributes": {"class": "protocol-message-header"},
                            "children": [
                                {
                                    "tag": "span",
                                    "text": message.get("name", message_type.capitalize())
                                },
                                {
                                    "tag": "span",
                                    "text": time.strftime('%H:%M:%S', time.localtime(message.get("timestamp", time.time())))
                                }
                            ]
                        }
                    ]
                }
                
                # Add message content
                content_text = message.get("content", "")
                if isinstance(content_text, dict):
                    try:
                        content_text = json.dumps(content_text, indent=2)
                    except (TypeError, ValueError):
                        # TypeError: object not JSON serializable
                        # ValueError: circular reference or invalid data
                        content_text = str(content_text)
                
                message_element["children"].append({
                    "tag": "pre",
                    "attributes": {"class": "protocol-message-content"},
                    "text": content_text
                })
                
                messages_container["children"].append(message_element)
            
            html_structure["children"].append(messages_container)
        
        # Add timestamp
        html_structure["children"].append({
            "tag": "div",
            "attributes": {"class": "protocol-timestamp"},
            "text": f"Updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(content.get('timestamp', time.time())))}"
        })
        
        # Return rendering instructions
        return {
            "protocol_type": protocol_type,
            "exchange_id": exchange_id,
            "platform": "web",
            "css": css,
            "html": html_structure,
            "animations": {
                "message_travel": "@keyframes message-travel { 0% { transform: translateX(-20px); opacity: 0; } 100% { transform: translateX(0); opacity: 1; } }",
                "pulse": "@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }"
            },
            "event_handlers": {
                "click": f"handleProtocolClick('{protocol_type}', '{exchange_id}')",
                "mouseover": f"handleProtocolMouseOver('{protocol_type}', '{exchange_id}')",
                "mouseout": f"handleProtocolMouseOut('{protocol_type}', '{exchange_id}')"
            }
        }

    def _generate_mobile_rendering(
        self,
        protocol_type: str,
        exchange_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mobile rendering instructions for a protocol exchange.
        
        Args:
            protocol_type: Type of protocol
            exchange_id: ID of the protocol exchange
            visualization_data: Visualization data
            
        Returns:
            Mobile rendering instructions
        """
        # Similar to web rendering but with mobile-specific adjustments
        web_rendering = self._generate_web_rendering(protocol_type, exchange_id, visualization_data)
        
        # Adjust for mobile
        web_rendering["platform"] = "mobile"
        
        # Make touch-friendly adjustments
        if "css" in web_rendering:
            # Increase padding
            if "container" in web_rendering["css"]:
                web_rendering["css"]["container"]["padding"] = "16px"
            
            # Adjust font sizes
            for element in ["title", "subtitle", "body", "caption"]:
                if element in web_rendering["css"]:
                    current_size = web_rendering["css"][element].get("font-size", "14px")
                    size_value = int(current_size.replace("px", ""))
                    web_rendering["css"][element]["font-size"] = f"{size_value + 2}px"
        
        # Replace mouse events with touch events
        if "event_handlers" in web_rendering:
            web_rendering["event_handlers"] = {
                "touchstart": f"handleProtocolTouchStart('{protocol_type}', '{exchange_id}')",
                "touchend": f"handleProtocolTouchEnd('{protocol_type}', '{exchange_id}')"
            }
        
        return web_rendering

    def _generate_desktop_rendering(
        self,
        protocol_type: str,
        exchange_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate desktop rendering instructions for a protocol exchange.
        
        Args:
            protocol_type: Type of protocol
            exchange_id: ID of the protocol exchange
            visualization_data: Visualization data
            
        Returns:
            Desktop rendering instructions
        """
        # For desktop native apps
        # This would generate platform-specific instructions
        # For simplicity, we'll use a modified version of web rendering
        
        web_rendering = self._generate_web_rendering(protocol_type, exchange_id, visualization_data)
        
        # Adjust for desktop
        web_rendering["platform"] = "desktop"
        
        # Add desktop-specific properties
        web_rendering["desktop_properties"] = {
            "window_title": f"{protocol_type.upper()} Protocol Exchange",
            "window_icon": f"{protocol_type}_icon",
            "window_size": {"width": 600, "height": 400},
            "window_resizable": True,
            "window_always_on_top": False,
            "window_frameless": False,
            "window_transparent": False
        }
        
        return web_rendering

    def animate_protocol_exchange(
        self,
        protocol_type: str,
        exchange_id: str,
        animation_type: str,
        duration: float = 1.0,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Animate a protocol exchange.
        
        Args:
            protocol_type: Type of protocol
            exchange_id: ID of the protocol exchange
            animation_type: Type of animation
            duration: Duration of animation in seconds
            callback: Optional callback function
            
        Returns:
            Animation ID
        """
        # Generate animation ID
        animation_id = str(uuid.uuid4())
        
        # Create cache key
        cache_key = f"{protocol_type}:{exchange_id}"
        
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
        
        # Clear cache for this protocol exchange
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
        
        logger.debug(f"Started animation {animation_id} of type {animation_type} for protocol exchange {protocol_type}:{exchange_id}")
        return animation_id

    def get_animation_state(
        self,
        protocol_type: str,
        exchange_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the animation state of a protocol exchange.
        
        Args:
            protocol_type: Type of protocol
            exchange_id: ID of the protocol exchange
            
        Returns:
            Animation state if found, None otherwise
        """
        cache_key = f"{protocol_type}:{exchange_id}"
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
        if style_id in [s.value for s in ProtocolVisualizationStyle]:
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
