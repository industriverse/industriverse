"""
Capsule Visualization Engine Module for the UI/UX Layer of Industriverse

This module provides visualization capabilities for Agent Capsules in the UI/UX Layer,
enabling rich, interactive, and context-aware visual representations of capsules
across different platforms and devices.

The Capsule Visualization Engine is responsible for:
1. Rendering capsule visual representations
2. Adapting capsule visuals to different contexts and devices
3. Providing animation and transition effects for capsules
4. Supporting different visualization modes and styles
5. Integrating with the Universal Skin for consistent visual language

This module works closely with the Capsule Manager, Capsule State Manager, and
other capsule-related components to provide a cohesive visual experience.
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from enum import Enum
import json
import math

from .capsule_state_manager import CapsuleStateManager
from ..rendering_engine.theme_manager import ThemeManager
from ..context_engine.context_awareness_engine import ContextAwarenessEngine
from ..agent_ecosystem.agent_state_visualizer import AgentStateVisualizer

logger = logging.getLogger(__name__)

class VisualizationMode(Enum):
    """Enumeration of capsule visualization modes."""
    COMPACT = "compact"
    EXPANDED = "expanded"
    DETAILED = "detailed"
    AMBIENT = "ambient"
    FOCUSED = "focused"


class VisualizationStyle(Enum):
    """Enumeration of capsule visualization styles."""
    STANDARD = "standard"
    INDUSTRIAL = "industrial"
    MINIMAL = "minimal"
    TECHNICAL = "technical"
    ORGANIC = "organic"
    CUSTOM = "custom"


class CapsuleVisualizationEngine:
    """
    Provides visualization capabilities for Agent Capsules in the UI/UX Layer.
    
    This class is responsible for rendering capsule visual representations,
    adapting to different contexts and devices, and providing animation effects.
    """

    def __init__(
        self,
        capsule_state_manager: CapsuleStateManager,
        theme_manager: ThemeManager,
        context_awareness_engine: ContextAwarenessEngine,
        agent_state_visualizer: AgentStateVisualizer
    ):
        """
        Initialize the CapsuleVisualizationEngine.
        
        Args:
            capsule_state_manager: Manager for capsule states
            theme_manager: Manager for UI themes
            context_awareness_engine: Engine for context awareness
            agent_state_visualizer: Visualizer for agent states
        """
        self.capsule_state_manager = capsule_state_manager
        self.theme_manager = theme_manager
        self.context_awareness_engine = context_awareness_engine
        self.agent_state_visualizer = agent_state_visualizer
        
        # Initialize visualization tracking
        self.visualization_modes = {}
        self.visualization_styles = {}
        self.visualization_cache = {}
        self.visualization_callbacks = {}
        self.custom_renderers = {}
        self.animation_states = {}
        
        # Initialize default visualization styles
        self._initialize_default_styles()
        
        logger.info("CapsuleVisualizationEngine initialized")

    def _initialize_default_styles(self):
        """Initialize default visualization styles."""
        # Standard style
        self.visualization_styles[VisualizationStyle.STANDARD.value] = {
            "name": "Standard",
            "description": "Default visualization style for capsules",
            "colors": {
                "background": "#FFFFFF",
                "border": "#CCCCCC",
                "text": "#333333",
                "icon": "#666666",
                "accent": "#3498DB",
                "status_active": "#2ECC71",
                "status_inactive": "#95A5A6",
                "status_error": "#E74C3C",
                "status_warning": "#F39C12"
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
                "active_pulse": True,
                "error_shake": True
            },
            "typography": {
                "font_family": "Inter, sans-serif",
                "title_size": 14,
                "subtitle_size": 12,
                "body_size": 12,
                "caption_size": 10
            }
        }
        
        # Industrial style
        self.visualization_styles[VisualizationStyle.INDUSTRIAL.value] = {
            "name": "Industrial",
            "description": "Industrial-themed visualization style for capsules",
            "colors": {
                "background": "#2C3E50",
                "border": "#34495E",
                "text": "#ECF0F1",
                "icon": "#BDC3C7",
                "accent": "#F1C40F",
                "status_active": "#2ECC71",
                "status_inactive": "#7F8C8D",
                "status_error": "#E74C3C",
                "status_warning": "#F39C12"
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
                "active_pulse": True,
                "error_shake": True
            },
            "typography": {
                "font_family": "Roboto Mono, monospace",
                "title_size": 14,
                "subtitle_size": 12,
                "body_size": 12,
                "caption_size": 10
            }
        }
        
        # Minimal style
        self.visualization_styles[VisualizationStyle.MINIMAL.value] = {
            "name": "Minimal",
            "description": "Minimalist visualization style for capsules",
            "colors": {
                "background": "#FFFFFF",
                "border": "#EEEEEE",
                "text": "#333333",
                "icon": "#555555",
                "accent": "#3498DB",
                "status_active": "#2ECC71",
                "status_inactive": "#CCCCCC",
                "status_error": "#E74C3C",
                "status_warning": "#F39C12"
            },
            "shapes": {
                "border_radius": 4,
                "icon_size": 20,
                "padding": 8,
                "shadow": "none"
            },
            "animations": {
                "transition_duration": 0.2,
                "hover_scale": 1.0,
                "active_pulse": False,
                "error_shake": True
            },
            "typography": {
                "font_family": "Inter, sans-serif",
                "title_size": 13,
                "subtitle_size": 11,
                "body_size": 11,
                "caption_size": 9
            }
        }
        
        # Technical style
        self.visualization_styles[VisualizationStyle.TECHNICAL.value] = {
            "name": "Technical",
            "description": "Technical visualization style for capsules",
            "colors": {
                "background": "#1E1E1E",
                "border": "#333333",
                "text": "#FFFFFF",
                "icon": "#CCCCCC",
                "accent": "#61DAFB",
                "status_active": "#4CAF50",
                "status_inactive": "#9E9E9E",
                "status_error": "#F44336",
                "status_warning": "#FF9800"
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
                "active_pulse": True,
                "error_shake": True
            },
            "typography": {
                "font_family": "JetBrains Mono, monospace",
                "title_size": 14,
                "subtitle_size": 12,
                "body_size": 12,
                "caption_size": 10
            }
        }
        
        # Organic style
        self.visualization_styles[VisualizationStyle.ORGANIC.value] = {
            "name": "Organic",
            "description": "Organic visualization style for capsules",
            "colors": {
                "background": "#F5F5F5",
                "border": "#E0E0E0",
                "text": "#333333",
                "icon": "#555555",
                "accent": "#8BC34A",
                "status_active": "#4CAF50",
                "status_inactive": "#9E9E9E",
                "status_error": "#F44336",
                "status_warning": "#FF9800"
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
                "active_pulse": True,
                "error_shake": True
            },
            "typography": {
                "font_family": "Quicksand, sans-serif",
                "title_size": 15,
                "subtitle_size": 13,
                "body_size": 13,
                "caption_size": 11
            }
        }

    def set_visualization_mode(
        self,
        capsule_id: str,
        mode: VisualizationMode
    ) -> bool:
        """
        Set the visualization mode for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            mode: Visualization mode
            
        Returns:
            True if mode was set, False otherwise
        """
        # Verify capsule exists
        if not self.capsule_state_manager.get_capsule_state(capsule_id):
            logger.warning(f"Unknown capsule ID: {capsule_id}")
            return False
        
        # Set mode
        self.visualization_modes[capsule_id] = mode.value
        
        # Clear cache for this capsule
        if capsule_id in self.visualization_cache:
            del self.visualization_cache[capsule_id]
        
        logger.debug(f"Set visualization mode for capsule {capsule_id} to {mode.value}")
        return True

    def set_visualization_style(
        self,
        capsule_id: str,
        style: VisualizationStyle
    ) -> bool:
        """
        Set the visualization style for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            style: Visualization style
            
        Returns:
            True if style was set, False otherwise
        """
        # Verify capsule exists
        if not self.capsule_state_manager.get_capsule_state(capsule_id):
            logger.warning(f"Unknown capsule ID: {capsule_id}")
            return False
        
        # Verify style exists
        if style.value not in self.visualization_styles:
            logger.warning(f"Unknown visualization style: {style.value}")
            return False
        
        # Set style
        self.visualization_styles[capsule_id] = style.value
        
        # Clear cache for this capsule
        if capsule_id in self.visualization_cache:
            del self.visualization_cache[capsule_id]
        
        logger.debug(f"Set visualization style for capsule {capsule_id} to {style.value}")
        return True

    def get_visualization_data(
        self,
        capsule_id: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get visualization data for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            force_refresh: Whether to force a refresh of the data
            
        Returns:
            Visualization data
        """
        # Check cache if not forcing refresh
        if not force_refresh and capsule_id in self.visualization_cache:
            return self.visualization_cache[capsule_id]
        
        # Get capsule state
        capsule_state = self.capsule_state_manager.get_capsule_state(capsule_id)
        
        if not capsule_state:
            logger.warning(f"Unknown capsule ID: {capsule_id}")
            return {}
        
        # Get visualization mode
        mode = self.visualization_modes.get(capsule_id, VisualizationMode.COMPACT.value)
        
        # Get visualization style
        style_id = self.visualization_styles.get(capsule_id, VisualizationStyle.STANDARD.value)
        style = self.visualization_styles.get(style_id, self.visualization_styles[VisualizationStyle.STANDARD.value])
        
        # Get current theme
        theme = self.theme_manager.get_current_theme()
        
        # Get context
        context = self.context_awareness_engine.get_current_context()
        
        # Build visualization data
        visualization_data = {
            "capsule_id": capsule_id,
            "mode": mode,
            "style": style_id,
            "state": capsule_state.get("status", "unknown"),
            "name": capsule_state.get("name", "Unknown Capsule"),
            "type": capsule_state.get("type", "unknown"),
            "icon": capsule_state.get("icon", "default"),
            "colors": self._merge_colors(style["colors"], theme.get("colors", {})),
            "shapes": style["shapes"],
            "animations": style["animations"],
            "typography": style["typography"],
            "content": self._get_content_for_mode(capsule_state, mode),
            "context_adaptations": self._get_context_adaptations(capsule_state, context),
            "animation_state": self.animation_states.get(capsule_id, {})
        }
        
        # Cache visualization data
        self.visualization_cache[capsule_id] = visualization_data
        
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
        capsule_state: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """
        Get content data for a specific visualization mode.
        
        Args:
            capsule_state: State of the capsule
            mode: Visualization mode
            
        Returns:
            Content data
        """
        content = {
            "title": capsule_state.get("name", "Unknown Capsule"),
            "subtitle": capsule_state.get("type", "unknown"),
            "status_text": capsule_state.get("status", "unknown"),
            "metrics": [],
            "actions": [],
            "details": {}
        }
        
        # Add mode-specific content
        if mode == VisualizationMode.COMPACT.value:
            # Minimal content for compact mode
            pass
        
        elif mode == VisualizationMode.EXPANDED.value:
            # Add metrics
            metrics = capsule_state.get("metrics", {})
            for key, value in metrics.items():
                content["metrics"].append({
                    "name": key,
                    "value": value,
                    "type": "number" if isinstance(value, (int, float)) else "string"
                })
            
            # Add actions
            actions = capsule_state.get("actions", [])
            content["actions"] = actions[:3]  # Limit to 3 actions in expanded mode
        
        elif mode == VisualizationMode.DETAILED.value:
            # Add all metrics
            metrics = capsule_state.get("metrics", {})
            for key, value in metrics.items():
                content["metrics"].append({
                    "name": key,
                    "value": value,
                    "type": "number" if isinstance(value, (int, float)) else "string"
                })
            
            # Add all actions
            content["actions"] = capsule_state.get("actions", [])
            
            # Add details
            content["details"] = {
                "description": capsule_state.get("description", ""),
                "created_at": capsule_state.get("created_at", 0),
                "updated_at": capsule_state.get("updated_at", 0),
                "version": capsule_state.get("version", "1.0.0"),
                "author": capsule_state.get("author", "Unknown")
            }
        
        elif mode == VisualizationMode.AMBIENT.value:
            # Minimal content for ambient mode, focus on status
            pass
        
        elif mode == VisualizationMode.FOCUSED.value:
            # Add all metrics
            metrics = capsule_state.get("metrics", {})
            for key, value in metrics.items():
                content["metrics"].append({
                    "name": key,
                    "value": value,
                    "type": "number" if isinstance(value, (int, float)) else "string"
                })
            
            # Add all actions
            content["actions"] = capsule_state.get("actions", [])
            
            # Add details
            content["details"] = {
                "description": capsule_state.get("description", ""),
                "created_at": capsule_state.get("created_at", 0),
                "updated_at": capsule_state.get("updated_at", 0),
                "version": capsule_state.get("version", "1.0.0"),
                "author": capsule_state.get("author", "Unknown")
            }
            
            # Add activity
            content["activity"] = capsule_state.get("activity", [])
            
            # Add connections
            content["connections"] = capsule_state.get("connections", [])
        
        return content

    def _get_context_adaptations(
        self,
        capsule_state: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get context-specific adaptations for a capsule.
        
        Args:
            capsule_state: State of the capsule
            context: Current context
            
        Returns:
            Context adaptations
        """
        adaptations = {
            "priority": "normal",
            "visibility": "normal",
            "size_adjustment": 1.0,
            "highlight": False,
            "custom_properties": {}
        }
        
        # Apply context-based adaptations
        
        # Adjust priority based on context relevance
        if "current_task" in context:
            task_relevance = self._calculate_task_relevance(capsule_state, context["current_task"])
            
            if task_relevance > 0.8:
                adaptations["priority"] = "high"
            elif task_relevance > 0.5:
                adaptations["priority"] = "medium"
            else:
                adaptations["priority"] = "low"
        
        # Adjust visibility based on user role
        if "user_role" in context:
            role_relevance = self._calculate_role_relevance(capsule_state, context["user_role"])
            
            if role_relevance > 0.8:
                adaptations["visibility"] = "high"
            elif role_relevance > 0.5:
                adaptations["visibility"] = "normal"
            else:
                adaptations["visibility"] = "low"
        
        # Adjust size based on device
        if "device" in context:
            if context["device"] == "mobile":
                adaptations["size_adjustment"] = 0.8
            elif context["device"] == "tablet":
                adaptations["size_adjustment"] = 0.9
            elif context["device"] == "desktop":
                adaptations["size_adjustment"] = 1.0
            elif context["device"] == "large_display":
                adaptations["size_adjustment"] = 1.2
        
        # Highlight based on alerts or notifications
        if "alerts" in context and "capsule_alerts" in context["alerts"]:
            if capsule_id in context["alerts"]["capsule_alerts"]:
                adaptations["highlight"] = True
        
        # Add custom properties based on industry context
        if "industry" in context:
            industry = context["industry"]
            
            if industry == "manufacturing":
                adaptations["custom_properties"]["show_production_metrics"] = True
            elif industry == "energy":
                adaptations["custom_properties"]["show_energy_metrics"] = True
            elif industry == "logistics":
                adaptations["custom_properties"]["show_logistics_metrics"] = True
        
        return adaptations

    def _calculate_task_relevance(
        self,
        capsule_state: Dict[str, Any],
        current_task: Dict[str, Any]
    ) -> float:
        """
        Calculate relevance of a capsule to the current task.
        
        Args:
            capsule_state: State of the capsule
            current_task: Current task context
            
        Returns:
            Relevance score between 0 and 1
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated relevance calculation
        
        relevance = 0.0
        
        # Check if capsule type matches task type
        if capsule_state.get("type") == current_task.get("type"):
            relevance += 0.5
        
        # Check if capsule is mentioned in task
        if capsule_state.get("id") in current_task.get("related_capsules", []):
            relevance += 0.5
        
        # Ensure relevance is between 0 and 1
        return min(max(relevance, 0.0), 1.0)

    def _calculate_role_relevance(
        self,
        capsule_state: Dict[str, Any],
        user_role: Dict[str, Any]
    ) -> float:
        """
        Calculate relevance of a capsule to the user role.
        
        Args:
            capsule_state: State of the capsule
            user_role: User role context
            
        Returns:
            Relevance score between 0 and 1
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated relevance calculation
        
        relevance = 0.5  # Default medium relevance
        
        # Check if capsule is relevant to role
        if "relevant_capsule_types" in user_role and capsule_state.get("type") in user_role["relevant_capsule_types"]:
            relevance += 0.5
        
        # Check if capsule is explicitly assigned to role
        if "assigned_capsules" in user_role and capsule_state.get("id") in user_role["assigned_capsules"]:
            relevance += 0.5
        
        # Ensure relevance is between 0 and 1
        return min(max(relevance, 0.0), 1.0)

    def register_custom_renderer(
        self,
        capsule_type: str,
        renderer_function: Callable[[str, Dict[str, Any]], Dict[str, Any]]
    ) -> bool:
        """
        Register a custom renderer for a capsule type.
        
        Args:
            capsule_type: Type of capsule
            renderer_function: Function to render the capsule
            
        Returns:
            True if registration was successful, False otherwise
        """
        self.custom_renderers[capsule_type] = renderer_function
        logger.info(f"Registered custom renderer for capsule type {capsule_type}")
        return True

    def unregister_custom_renderer(self, capsule_type: str) -> bool:
        """
        Unregister a custom renderer for a capsule type.
        
        Args:
            capsule_type: Type of capsule
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if capsule_type in self.custom_renderers:
            del self.custom_renderers[capsule_type]
            logger.info(f"Unregistered custom renderer for capsule type {capsule_type}")
            return True
        
        logger.warning(f"No custom renderer registered for capsule type {capsule_type}")
        return False

    def render_capsule(
        self,
        capsule_id: str,
        target_platform: str = "web",
        target_container: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Render a capsule for a specific platform.
        
        Args:
            capsule_id: ID of the capsule
            target_platform: Target platform for rendering
            target_container: Optional target container ID
            callback: Optional callback function
            
        Returns:
            Rendering result
        """
        # Get visualization data
        visualization_data = self.get_visualization_data(capsule_id)
        
        if not visualization_data:
            logger.warning(f"Failed to get visualization data for capsule {capsule_id}")
            return {}
        
        # Get capsule type
        capsule_type = visualization_data.get("type", "unknown")
        
        # Check for custom renderer
        if capsule_type in self.custom_renderers:
            # Use custom renderer
            renderer = self.custom_renderers[capsule_type]
            result = renderer(capsule_id, visualization_data)
        else:
            # Use default renderer
            result = self._default_renderer(capsule_id, visualization_data, target_platform)
        
        # Store callback if provided
        if callback:
            self.visualization_callbacks[capsule_id] = callback
        
        return result

    def _default_renderer(
        self,
        capsule_id: str,
        visualization_data: Dict[str, Any],
        target_platform: str
    ) -> Dict[str, Any]:
        """
        Default renderer for capsules.
        
        Args:
            capsule_id: ID of the capsule
            visualization_data: Visualization data
            target_platform: Target platform for rendering
            
        Returns:
            Rendering result
        """
        # This is a simplified implementation
        # In a real system, this would generate actual rendering instructions
        
        mode = visualization_data.get("mode", VisualizationMode.COMPACT.value)
        style = visualization_data.get("style", VisualizationStyle.STANDARD.value)
        state = visualization_data.get("state", "unknown")
        
        # Generate rendering instructions based on platform
        if target_platform == "web":
            return self._generate_web_rendering(capsule_id, visualization_data)
        
        elif target_platform == "mobile":
            return self._generate_mobile_rendering(capsule_id, visualization_data)
        
        elif target_platform == "desktop":
            return self._generate_desktop_rendering(capsule_id, visualization_data)
        
        elif target_platform == "ar":
            return self._generate_ar_rendering(capsule_id, visualization_data)
        
        else:
            logger.warning(f"Unknown target platform: {target_platform}")
            return {}

    def _generate_web_rendering(
        self,
        capsule_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate web rendering instructions for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            visualization_data: Visualization data
            
        Returns:
            Web rendering instructions
        """
        mode = visualization_data.get("mode", VisualizationMode.COMPACT.value)
        style_id = visualization_data.get("style", VisualizationStyle.STANDARD.value)
        state = visualization_data.get("state", "unknown")
        content = visualization_data.get("content", {})
        colors = visualization_data.get("colors", {})
        shapes = visualization_data.get("shapes", {})
        typography = visualization_data.get("typography", {})
        animations = visualization_data.get("animations", {})
        
        # Generate CSS
        css = {
            "container": {
                "background-color": colors.get("background", "#FFFFFF"),
                "border": f"1px solid {colors.get('border', '#CCCCCC')}",
                "border-radius": f"{shapes.get('border_radius', 8)}px",
                "padding": f"{shapes.get('padding', 12)}px",
                "box-shadow": shapes.get("shadow", "0 2px 4px rgba(0, 0, 0, 0.1)"),
                "font-family": typography.get("font_family", "Inter, sans-serif"),
                "color": colors.get("text", "#333333"),
                "transition": f"all {animations.get('transition_duration', 0.3)}s ease-in-out"
            },
            "title": {
                "font-size": f"{typography.get('title_size', 14)}px",
                "font-weight": "bold",
                "margin-bottom": "4px",
                "color": colors.get("text", "#333333")
            },
            "subtitle": {
                "font-size": f"{typography.get('subtitle_size', 12)}px",
                "color": colors.get("text", "#333333"),
                "opacity": "0.8",
                "margin-bottom": "8px"
            },
            "status": {
                "font-size": f"{typography.get('caption_size', 10)}px",
                "padding": "2px 6px",
                "border-radius": "4px",
                "display": "inline-block",
                "margin-bottom": "8px"
            },
            "metrics": {
                "display": "flex",
                "flex-wrap": "wrap",
                "gap": "8px",
                "margin-bottom": "12px"
            },
            "metric": {
                "font-size": f"{typography.get('body_size', 12)}px",
                "background-color": "rgba(0, 0, 0, 0.05)",
                "padding": "4px 8px",
                "border-radius": "4px"
            },
            "actions": {
                "display": "flex",
                "gap": "8px",
                "margin-top": "12px"
            },
            "action": {
                "font-size": f"{typography.get('body_size', 12)}px",
                "padding": "6px 12px",
                "border-radius": "4px",
                "background-color": colors.get("accent", "#3498DB"),
                "color": "#FFFFFF",
                "cursor": "pointer",
                "border": "none"
            },
            "icon": {
                "width": f"{shapes.get('icon_size', 24)}px",
                "height": f"{shapes.get('icon_size', 24)}px",
                "margin-right": "8px",
                "color": colors.get("icon", "#666666")
            }
        }
        
        # Add status-specific styles
        if state == "active":
            css["status"]["background-color"] = colors.get("status_active", "#2ECC71")
            css["status"]["color"] = "#FFFFFF"
            
            if animations.get("active_pulse", True):
                css["container"]["animation"] = "pulse 2s infinite"
        
        elif state == "inactive":
            css["status"]["background-color"] = colors.get("status_inactive", "#95A5A6")
            css["status"]["color"] = "#FFFFFF"
            css["container"]["opacity"] = "0.7"
        
        elif state == "error":
            css["status"]["background-color"] = colors.get("status_error", "#E74C3C")
            css["status"]["color"] = "#FFFFFF"
            
            if animations.get("error_shake", True):
                css["container"]["animation"] = "shake 0.5s"
        
        elif state == "warning":
            css["status"]["background-color"] = colors.get("status_warning", "#F39C12")
            css["status"]["color"] = "#FFFFFF"
        
        # Generate HTML structure based on mode
        html_structure = {
            "tag": "div",
            "attributes": {
                "id": f"capsule-{capsule_id}",
                "class": f"capsule capsule-{style_id} capsule-{mode} capsule-{state}"
            },
            "children": [
                {
                    "tag": "div",
                    "attributes": {"class": "capsule-header"},
                    "children": [
                        {
                            "tag": "div",
                            "attributes": {"class": "capsule-title"},
                            "text": content.get("title", "Unknown Capsule")
                        },
                        {
                            "tag": "div",
                            "attributes": {"class": "capsule-subtitle"},
                            "text": content.get("subtitle", "")
                        },
                        {
                            "tag": "div",
                            "attributes": {"class": "capsule-status"},
                            "text": content.get("status_text", state)
                        }
                    ]
                }
            ]
        }
        
        # Add metrics if available
        if content.get("metrics") and mode in [VisualizationMode.EXPANDED.value, VisualizationMode.DETAILED.value, VisualizationMode.FOCUSED.value]:
            metrics_container = {
                "tag": "div",
                "attributes": {"class": "capsule-metrics"},
                "children": []
            }
            
            for metric in content.get("metrics", []):
                metrics_container["children"].append({
                    "tag": "div",
                    "attributes": {"class": "capsule-metric"},
                    "text": f"{metric.get('name', '')}: {metric.get('value', '')}"
                })
            
            html_structure["children"].append(metrics_container)
        
        # Add actions if available
        if content.get("actions") and mode in [VisualizationMode.EXPANDED.value, VisualizationMode.DETAILED.value, VisualizationMode.FOCUSED.value]:
            actions_container = {
                "tag": "div",
                "attributes": {"class": "capsule-actions"},
                "children": []
            }
            
            for action in content.get("actions", []):
                actions_container["children"].append({
                    "tag": "button",
                    "attributes": {
                        "class": "capsule-action",
                        "data-action": action.get("id", ""),
                        "data-capsule": capsule_id
                    },
                    "text": action.get("name", "Action")
                })
            
            html_structure["children"].append(actions_container)
        
        # Add details if available
        if content.get("details") and mode in [VisualizationMode.DETAILED.value, VisualizationMode.FOCUSED.value]:
            details_container = {
                "tag": "div",
                "attributes": {"class": "capsule-details"},
                "children": [
                    {
                        "tag": "div",
                        "attributes": {"class": "capsule-description"},
                        "text": content.get("details", {}).get("description", "")
                    }
                ]
            }
            
            html_structure["children"].append(details_container)
        
        # Return rendering instructions
        return {
            "capsule_id": capsule_id,
            "platform": "web",
            "css": css,
            "html": html_structure,
            "animations": {
                "pulse": "@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }",
                "shake": "@keyframes shake { 0%, 100% { transform: translateX(0); } 10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); } 20%, 40%, 60%, 80% { transform: translateX(5px); } }"
            },
            "event_handlers": {
                "click": f"handleCapsuleClick('{capsule_id}')",
                "mouseover": f"handleCapsuleMouseOver('{capsule_id}')",
                "mouseout": f"handleCapsuleMouseOut('{capsule_id}')"
            }
        }

    def _generate_mobile_rendering(
        self,
        capsule_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mobile rendering instructions for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            visualization_data: Visualization data
            
        Returns:
            Mobile rendering instructions
        """
        # Similar to web rendering but with mobile-specific adjustments
        web_rendering = self._generate_web_rendering(capsule_id, visualization_data)
        
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
                "touchstart": f"handleCapsuleTouchStart('{capsule_id}')",
                "touchend": f"handleCapsuleTouchEnd('{capsule_id}')"
            }
        
        return web_rendering

    def _generate_desktop_rendering(
        self,
        capsule_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate desktop rendering instructions for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            visualization_data: Visualization data
            
        Returns:
            Desktop rendering instructions
        """
        # For desktop native apps
        # This would generate platform-specific instructions
        # For simplicity, we'll use a modified version of web rendering
        
        web_rendering = self._generate_web_rendering(capsule_id, visualization_data)
        
        # Adjust for desktop
        web_rendering["platform"] = "desktop"
        
        # Add desktop-specific properties
        web_rendering["desktop_properties"] = {
            "window_title": visualization_data.get("content", {}).get("title", "Capsule"),
            "window_icon": visualization_data.get("content", {}).get("icon", "default"),
            "window_size": {"width": 300, "height": 200},
            "window_resizable": True,
            "window_always_on_top": False,
            "window_frameless": False,
            "window_transparent": False
        }
        
        return web_rendering

    def _generate_ar_rendering(
        self,
        capsule_id: str,
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AR rendering instructions for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            visualization_data: Visualization data
            
        Returns:
            AR rendering instructions
        """
        # For AR applications
        # This would generate AR-specific rendering instructions
        
        mode = visualization_data.get("mode", VisualizationMode.COMPACT.value)
        style_id = visualization_data.get("style", VisualizationStyle.STANDARD.value)
        state = visualization_data.get("state", "unknown")
        content = visualization_data.get("content", {})
        colors = visualization_data.get("colors", {})
        
        # Generate AR-specific rendering instructions
        ar_rendering = {
            "capsule_id": capsule_id,
            "platform": "ar",
            "ar_object": {
                "type": "panel",
                "width": 0.3,
                "height": 0.2,
                "depth": 0.01,
                "color": colors.get("background", "#FFFFFF"),
                "border_color": colors.get("border", "#CCCCCC"),
                "border_width": 0.002,
                "corner_radius": 0.01,
                "opacity": 0.9
            },
            "ar_text": {
                "title": {
                    "text": content.get("title", "Unknown Capsule"),
                    "position": {"x": 0, "y": 0.08, "z": 0.011},
                    "scale": 0.02,
                    "color": colors.get("text", "#333333")
                },
                "subtitle": {
                    "text": content.get("subtitle", ""),
                    "position": {"x": 0, "y": 0.05, "z": 0.011},
                    "scale": 0.015,
                    "color": colors.get("text", "#333333"),
                    "opacity": 0.8
                },
                "status": {
                    "text": content.get("status_text", state),
                    "position": {"x": 0, "y": 0.02, "z": 0.011},
                    "scale": 0.015,
                    "color": "#FFFFFF",
                    "background": self._get_status_color(state, colors)
                }
            },
            "ar_interactions": {
                "tap": {
                    "action": "select_capsule",
                    "parameters": {"capsule_id": capsule_id}
                },
                "long_press": {
                    "action": "show_capsule_menu",
                    "parameters": {"capsule_id": capsule_id}
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
        
        # Add status-specific effects
        if state == "active":
            ar_rendering["ar_animations"]["status"] = {
                "type": "glow",
                "color": colors.get("status_active", "#2ECC71"),
                "intensity": 0.5,
                "frequency": 1.0
            }
        
        elif state == "error":
            ar_rendering["ar_animations"]["status"] = {
                "type": "shake",
                "amplitude": 0.01,
                "frequency": 5.0,
                "duration": 0.5
            }
        
        # Add metrics if available and mode is appropriate
        if content.get("metrics") and mode in [VisualizationMode.EXPANDED.value, VisualizationMode.DETAILED.value, VisualizationMode.FOCUSED.value]:
            ar_rendering["ar_metrics"] = []
            
            for i, metric in enumerate(content.get("metrics", [])[:3]):  # Limit to 3 metrics in AR
                ar_rendering["ar_metrics"].append({
                    "text": f"{metric.get('name', '')}: {metric.get('value', '')}",
                    "position": {"x": 0, "y": -0.02 - (i * 0.025), "z": 0.011},
                    "scale": 0.012,
                    "color": colors.get("text", "#333333")
                })
        
        return ar_rendering

    def _get_status_color(
        self,
        status: str,
        colors: Dict[str, str]
    ) -> str:
        """
        Get color for a status.
        
        Args:
            status: Status value
            colors: Color definitions
            
        Returns:
            Color for the status
        """
        if status == "active":
            return colors.get("status_active", "#2ECC71")
        elif status == "inactive":
            return colors.get("status_inactive", "#95A5A6")
        elif status == "error":
            return colors.get("status_error", "#E74C3C")
        elif status == "warning":
            return colors.get("status_warning", "#F39C12")
        else:
            return colors.get("status_inactive", "#95A5A6")

    def animate_capsule(
        self,
        capsule_id: str,
        animation_type: str,
        duration: float = 1.0,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Animate a capsule.
        
        Args:
            capsule_id: ID of the capsule
            animation_type: Type of animation
            duration: Duration of animation in seconds
            callback: Optional callback function
            
        Returns:
            Animation ID
        """
        # Generate animation ID
        animation_id = str(uuid.uuid4())
        
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
        self.animation_states[capsule_id] = animation_state
        
        # Store callback if provided
        if callback:
            self.visualization_callbacks[animation_id] = callback
        
        # Clear cache for this capsule
        if capsule_id in self.visualization_cache:
            del self.visualization_cache[capsule_id]
        
        # In a real implementation, this would trigger the animation
        # For simplicity, we'll use a timer thread to simulate animation progress
        import threading
        
        def update_animation():
            # Update progress
            animation_state = self.animation_states.get(capsule_id)
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
        
        logger.debug(f"Started animation {animation_id} of type {animation_type} for capsule {capsule_id}")
        return animation_id

    def get_animation_state(
        self,
        capsule_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the animation state of a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Animation state if found, None otherwise
        """
        return self.animation_states.get(capsule_id)

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
        if style_id in [s.value for s in VisualizationStyle]:
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
