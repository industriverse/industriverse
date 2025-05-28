"""
Specialized UI Component: Ambient Awareness Panel for the UI/UX Layer of Industriverse

This component provides an ambient awareness interface that displays contextual information,
system status, and environmental awareness in a non-intrusive manner.

The Ambient Awareness Panel is responsible for:
1. Displaying ambient contextual information
2. Providing system status awareness
3. Showing environmental conditions and changes
4. Adapting to user attention levels
5. Integrating with the Universal Skin for consistent visual language

This component works closely with the Context Engine and Agent Ecosystem to provide
a cohesive ambient intelligence experience.
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from enum import Enum
import json

from ...core.context_engine.context_awareness_engine import ContextAwarenessEngine
from ...core.agent_ecosystem.agent_state_visualizer import AgentStateVisualizer
from ...core.universal_skin.ambient_indicators import AmbientIndicators
from ...core.rendering_engine.theme_manager import ThemeManager

logger = logging.getLogger(__name__)

class AwarenessLevel(Enum):
    """Enumeration of awareness levels."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AmbientMode(Enum):
    """Enumeration of ambient modes."""
    BACKGROUND = "background"
    PERIPHERAL = "peripheral"
    FOCUSED = "focused"
    INTERACTIVE = "interactive"


class AmbientAwarenessPanel:
    """
    Provides an ambient awareness interface for the UI/UX Layer.
    
    This class is responsible for displaying ambient contextual information,
    system status, and environmental awareness in a non-intrusive manner.
    """

    def __init__(
        self,
        context_awareness_engine: ContextAwarenessEngine,
        agent_state_visualizer: AgentStateVisualizer,
        ambient_indicators: AmbientIndicators,
        theme_manager: ThemeManager
    ):
        """
        Initialize the AmbientAwarenessPanel.
        
        Args:
            context_awareness_engine: Engine for context awareness
            agent_state_visualizer: Visualizer for agent states
            ambient_indicators: Indicators for ambient awareness
            theme_manager: Manager for UI themes
        """
        self.context_awareness_engine = context_awareness_engine
        self.agent_state_visualizer = agent_state_visualizer
        self.ambient_indicators = ambient_indicators
        self.theme_manager = theme_manager
        
        # Initialize panel state
        self.panel_id = str(uuid.uuid4())
        self.current_mode = AmbientMode.BACKGROUND.value
        self.current_awareness_level = AwarenessLevel.MEDIUM.value
        self.is_visible = True
        self.is_expanded = False
        self.is_interactive = False
        self.position = "top-right"
        self.size = "medium"
        self.opacity = 0.8
        self.animation_speed = 1.0
        
        # Initialize content tracking
        self.context_items = {}
        self.agent_states = {}
        self.system_statuses = {}
        self.environmental_conditions = {}
        self.user_attention_metrics = {}
        
        # Initialize callbacks
        self.mode_change_callbacks = []
        self.awareness_level_change_callbacks = []
        self.visibility_change_callbacks = []
        self.interaction_callbacks = {}
        
        # Initialize panel
        self._initialize_panel()
        
        logger.info("AmbientAwarenessPanel initialized")

    def _initialize_panel(self):
        """Initialize the ambient awareness panel."""
        # Set default theme
        self.current_theme = self.theme_manager.get_current_theme()
        
        # Register for theme changes
        self.theme_manager.register_theme_change_callback(self._handle_theme_change)
        
        # Register for context changes
        self.context_awareness_engine.register_context_change_callback(self._handle_context_change)
        
        # Register for agent state changes
        self.agent_state_visualizer.register_state_change_callback(self._handle_agent_state_change)
        
        # Register for ambient indicator changes
        self.ambient_indicators.register_indicator_change_callback(self._handle_indicator_change)
        
        logger.debug("Ambient awareness panel initialized")

    def _handle_theme_change(self, theme_data):
        """
        Handle theme changes.
        
        Args:
            theme_data: New theme data
        """
        self.current_theme = theme_data
        logger.debug("Theme changed, updating ambient awareness panel")
        self.refresh()

    def _handle_context_change(self, context_type, context_id, context_data):
        """
        Handle context changes.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            context_data: Context data
        """
        # Store context item
        item_key = f"{context_type}:{context_id}"
        self.context_items[item_key] = {
            "type": context_type,
            "id": context_id,
            "data": context_data,
            "timestamp": time.time(),
            "priority": context_data.get("priority", "normal"),
            "is_new": True
        }
        
        # Update awareness level based on context priority
        self._update_awareness_level_from_context()
        
        logger.debug(f"Context changed: {context_type}:{context_id}")
        self.refresh()

    def _handle_agent_state_change(self, agent_id, agent_state):
        """
        Handle agent state changes.
        
        Args:
            agent_id: ID of the agent
            agent_state: Agent state
        """
        # Store agent state
        self.agent_states[agent_id] = {
            "id": agent_id,
            "state": agent_state,
            "timestamp": time.time(),
            "is_new": True
        }
        
        # Update awareness level based on agent state
        self._update_awareness_level_from_agent_state()
        
        logger.debug(f"Agent state changed: {agent_id}")
        self.refresh()

    def _handle_indicator_change(self, indicator_type, indicator_data):
        """
        Handle ambient indicator changes.
        
        Args:
            indicator_type: Type of indicator
            indicator_data: Indicator data
        """
        # Determine if this is a system status or environmental condition
        if indicator_type.startswith("system:"):
            # Store system status
            status_type = indicator_type.replace("system:", "")
            self.system_statuses[status_type] = {
                "type": status_type,
                "data": indicator_data,
                "timestamp": time.time(),
                "is_new": True
            }
            
            # Update awareness level based on system status
            self._update_awareness_level_from_system_status()
        
        elif indicator_type.startswith("environment:"):
            # Store environmental condition
            condition_type = indicator_type.replace("environment:", "")
            self.environmental_conditions[condition_type] = {
                "type": condition_type,
                "data": indicator_data,
                "timestamp": time.time(),
                "is_new": True
            }
            
            # Update awareness level based on environmental condition
            self._update_awareness_level_from_environmental_condition()
        
        logger.debug(f"Indicator changed: {indicator_type}")
        self.refresh()

    def _update_awareness_level_from_context(self):
        """Update awareness level based on context items."""
        # Check for high priority context items
        has_critical = False
        has_high = False
        has_medium = False
        
        for item in self.context_items.values():
            priority = item.get("priority", "normal")
            
            if priority == "critical":
                has_critical = True
                break
            elif priority == "high":
                has_high = True
            elif priority == "medium":
                has_medium = True
        
        # Set awareness level based on highest priority
        if has_critical:
            self.set_awareness_level(AwarenessLevel.CRITICAL)
        elif has_high:
            self.set_awareness_level(AwarenessLevel.HIGH)
        elif has_medium:
            self.set_awareness_level(AwarenessLevel.MEDIUM)

    def _update_awareness_level_from_agent_state(self):
        """Update awareness level based on agent states."""
        # Check for important agent states
        has_critical = False
        has_high = False
        has_medium = False
        
        for agent in self.agent_states.values():
            state = agent.get("state", {})
            status = state.get("status", "normal")
            
            if status == "critical":
                has_critical = True
                break
            elif status == "warning":
                has_high = True
            elif status == "active":
                has_medium = True
        
        # Set awareness level based on highest priority
        if has_critical:
            self.set_awareness_level(AwarenessLevel.CRITICAL)
        elif has_high:
            self.set_awareness_level(AwarenessLevel.HIGH)
        elif has_medium:
            self.set_awareness_level(AwarenessLevel.MEDIUM)

    def _update_awareness_level_from_system_status(self):
        """Update awareness level based on system statuses."""
        # Check for important system statuses
        has_critical = False
        has_high = False
        has_medium = False
        
        for status in self.system_statuses.values():
            level = status.get("data", {}).get("level", "normal")
            
            if level == "critical":
                has_critical = True
                break
            elif level == "warning":
                has_high = True
            elif level == "notice":
                has_medium = True
        
        # Set awareness level based on highest priority
        if has_critical:
            self.set_awareness_level(AwarenessLevel.CRITICAL)
        elif has_high:
            self.set_awareness_level(AwarenessLevel.HIGH)
        elif has_medium:
            self.set_awareness_level(AwarenessLevel.MEDIUM)

    def _update_awareness_level_from_environmental_condition(self):
        """Update awareness level based on environmental conditions."""
        # Check for important environmental conditions
        has_critical = False
        has_high = False
        has_medium = False
        
        for condition in self.environmental_conditions.values():
            level = condition.get("data", {}).get("level", "normal")
            
            if level == "critical":
                has_critical = True
                break
            elif level == "warning":
                has_high = True
            elif level == "notice":
                has_medium = True
        
        # Set awareness level based on highest priority
        if has_critical:
            self.set_awareness_level(AwarenessLevel.CRITICAL)
        elif has_high:
            self.set_awareness_level(AwarenessLevel.HIGH)
        elif has_medium:
            self.set_awareness_level(AwarenessLevel.MEDIUM)

    def set_mode(self, mode: AmbientMode) -> bool:
        """
        Set the ambient mode.
        
        Args:
            mode: Ambient mode
            
        Returns:
            True if mode was set, False otherwise
        """
        # Set mode
        previous_mode = self.current_mode
        self.current_mode = mode.value
        
        # Update panel properties based on mode
        if mode == AmbientMode.BACKGROUND:
            self.is_expanded = False
            self.is_interactive = False
            self.opacity = 0.5
            self.size = "small"
        
        elif mode == AmbientMode.PERIPHERAL:
            self.is_expanded = False
            self.is_interactive = False
            self.opacity = 0.8
            self.size = "medium"
        
        elif mode == AmbientMode.FOCUSED:
            self.is_expanded = True
            self.is_interactive = False
            self.opacity = 1.0
            self.size = "large"
        
        elif mode == AmbientMode.INTERACTIVE:
            self.is_expanded = True
            self.is_interactive = True
            self.opacity = 1.0
            self.size = "large"
        
        # Call mode change callbacks
        for callback in self.mode_change_callbacks:
            try:
                callback(previous_mode, self.current_mode)
            except Exception as e:
                logger.error(f"Error in mode change callback: {e}")
        
        logger.debug(f"Set ambient mode to {mode.value}")
        self.refresh()
        return True

    def set_awareness_level(self, level: AwarenessLevel) -> bool:
        """
        Set the awareness level.
        
        Args:
            level: Awareness level
            
        Returns:
            True if level was set, False otherwise
        """
        # Check if level is different
        if self.current_awareness_level == level.value:
            return True
        
        # Set level
        previous_level = self.current_awareness_level
        self.current_awareness_level = level.value
        
        # Update panel properties based on level
        if level == AwarenessLevel.MINIMAL:
            # Minimal awareness, stay in background
            self.set_mode(AmbientMode.BACKGROUND)
        
        elif level == AwarenessLevel.LOW:
            # Low awareness, peripheral visibility
            self.set_mode(AmbientMode.PERIPHERAL)
        
        elif level == AwarenessLevel.MEDIUM:
            # Medium awareness, peripheral visibility with occasional focus
            if self.current_mode == AmbientMode.BACKGROUND:
                self.set_mode(AmbientMode.PERIPHERAL)
        
        elif level == AwarenessLevel.HIGH:
            # High awareness, focused visibility
            self.set_mode(AmbientMode.FOCUSED)
        
        elif level == AwarenessLevel.CRITICAL:
            # Critical awareness, interactive mode
            self.set_mode(AmbientMode.INTERACTIVE)
        
        # Call awareness level change callbacks
        for callback in self.awareness_level_change_callbacks:
            try:
                callback(previous_level, self.current_awareness_level)
            except Exception as e:
                logger.error(f"Error in awareness level change callback: {e}")
        
        logger.debug(f"Set awareness level to {level.value}")
        self.refresh()
        return True

    def set_visibility(self, visible: bool) -> bool:
        """
        Set panel visibility.
        
        Args:
            visible: Whether panel is visible
            
        Returns:
            True if visibility was set, False otherwise
        """
        # Check if visibility is different
        if self.is_visible == visible:
            return True
        
        # Set visibility
        previous_visibility = self.is_visible
        self.is_visible = visible
        
        # Call visibility change callbacks
        for callback in self.visibility_change_callbacks:
            try:
                callback(previous_visibility, self.is_visible)
            except Exception as e:
                logger.error(f"Error in visibility change callback: {e}")
        
        logger.debug(f"Set visibility to {visible}")
        self.refresh()
        return True

    def set_position(self, position: str) -> bool:
        """
        Set panel position.
        
        Args:
            position: Panel position (e.g., "top-right", "bottom-left")
            
        Returns:
            True if position was set, False otherwise
        """
        # Validate position
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right", "top", "bottom", "left", "right", "center"]
        if position not in valid_positions:
            logger.warning(f"Invalid position: {position}")
            return False
        
        # Set position
        self.position = position
        
        logger.debug(f"Set position to {position}")
        self.refresh()
        return True

    def set_size(self, size: str) -> bool:
        """
        Set panel size.
        
        Args:
            size: Panel size (e.g., "small", "medium", "large")
            
        Returns:
            True if size was set, False otherwise
        """
        # Validate size
        valid_sizes = ["small", "medium", "large", "full"]
        if size not in valid_sizes:
            logger.warning(f"Invalid size: {size}")
            return False
        
        # Set size
        self.size = size
        
        logger.debug(f"Set size to {size}")
        self.refresh()
        return True

    def set_opacity(self, opacity: float) -> bool:
        """
        Set panel opacity.
        
        Args:
            opacity: Panel opacity (0.0 to 1.0)
            
        Returns:
            True if opacity was set, False otherwise
        """
        # Validate opacity
        if opacity < 0.0 or opacity > 1.0:
            logger.warning(f"Invalid opacity: {opacity}")
            return False
        
        # Set opacity
        self.opacity = opacity
        
        logger.debug(f"Set opacity to {opacity}")
        self.refresh()
        return True

    def set_animation_speed(self, speed: float) -> bool:
        """
        Set animation speed.
        
        Args:
            speed: Animation speed (0.1 to 2.0)
            
        Returns:
            True if speed was set, False otherwise
        """
        # Validate speed
        if speed < 0.1 or speed > 2.0:
            logger.warning(f"Invalid animation speed: {speed}")
            return False
        
        # Set speed
        self.animation_speed = speed
        
        logger.debug(f"Set animation speed to {speed}")
        self.refresh()
        return True

    def toggle_expansion(self) -> bool:
        """
        Toggle panel expansion.
        
        Returns:
            New expansion state
        """
        self.is_expanded = not self.is_expanded
        
        # Update mode based on expansion
        if self.is_expanded:
            if self.current_mode == AmbientMode.BACKGROUND:
                self.set_mode(AmbientMode.PERIPHERAL)
            elif self.current_mode == AmbientMode.PERIPHERAL:
                self.set_mode(AmbientMode.FOCUSED)
        else:
            if self.current_mode == AmbientMode.FOCUSED:
                self.set_mode(AmbientMode.PERIPHERAL)
            elif self.current_mode == AmbientMode.INTERACTIVE:
                self.set_mode(AmbientMode.FOCUSED)
        
        logger.debug(f"Toggled expansion to {self.is_expanded}")
        self.refresh()
        return self.is_expanded

    def toggle_interactivity(self) -> bool:
        """
        Toggle panel interactivity.
        
        Returns:
            New interactivity state
        """
        self.is_interactive = not self.is_interactive
        
        # Update mode based on interactivity
        if self.is_interactive:
            self.set_mode(AmbientMode.INTERACTIVE)
        else:
            self.set_mode(AmbientMode.FOCUSED)
        
        logger.debug(f"Toggled interactivity to {self.is_interactive}")
        self.refresh()
        return self.is_interactive

    def register_mode_change_callback(self, callback: Callable[[str, str], None]) -> bool:
        """
        Register a callback for mode changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if registration was successful, False otherwise
        """
        if callback not in self.mode_change_callbacks:
            self.mode_change_callbacks.append(callback)
            logger.debug(f"Registered mode change callback {callback}")
            return True
        
        return False

    def unregister_mode_change_callback(self, callback: Callable[[str, str], None]) -> bool:
        """
        Unregister a callback for mode changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if callback in self.mode_change_callbacks:
            self.mode_change_callbacks.remove(callback)
            logger.debug(f"Unregistered mode change callback {callback}")
            return True
        
        return False

    def register_awareness_level_change_callback(self, callback: Callable[[str, str], None]) -> bool:
        """
        Register a callback for awareness level changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if registration was successful, False otherwise
        """
        if callback not in self.awareness_level_change_callbacks:
            self.awareness_level_change_callbacks.append(callback)
            logger.debug(f"Registered awareness level change callback {callback}")
            return True
        
        return False

    def unregister_awareness_level_change_callback(self, callback: Callable[[str, str], None]) -> bool:
        """
        Unregister a callback for awareness level changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if callback in self.awareness_level_change_callbacks:
            self.awareness_level_change_callbacks.remove(callback)
            logger.debug(f"Unregistered awareness level change callback {callback}")
            return True
        
        return False

    def register_visibility_change_callback(self, callback: Callable[[bool, bool], None]) -> bool:
        """
        Register a callback for visibility changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if registration was successful, False otherwise
        """
        if callback not in self.visibility_change_callbacks:
            self.visibility_change_callbacks.append(callback)
            logger.debug(f"Registered visibility change callback {callback}")
            return True
        
        return False

    def unregister_visibility_change_callback(self, callback: Callable[[bool, bool], None]) -> bool:
        """
        Unregister a callback for visibility changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if callback in self.visibility_change_callbacks:
            self.visibility_change_callbacks.remove(callback)
            logger.debug(f"Unregistered visibility change callback {callback}")
            return True
        
        return False

    def register_interaction_callback(self, interaction_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Register a callback for interactions.
        
        Args:
            interaction_type: Type of interaction
            callback: Callback function
            
        Returns:
            True if registration was successful, False otherwise
        """
        self.interaction_callbacks[interaction_type] = callback
        logger.debug(f"Registered interaction callback for {interaction_type}")
        return True

    def unregister_interaction_callback(self, interaction_type: str) -> bool:
        """
        Unregister a callback for interactions.
        
        Args:
            interaction_type: Type of interaction
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if interaction_type in self.interaction_callbacks:
            del self.interaction_callbacks[interaction_type]
            logger.debug(f"Unregistered interaction callback for {interaction_type}")
            return True
        
        return False

    def handle_interaction(self, interaction_type: str, interaction_data: Dict[str, Any]) -> bool:
        """
        Handle an interaction.
        
        Args:
            interaction_type: Type of interaction
            interaction_data: Interaction data
            
        Returns:
            True if interaction was handled, False otherwise
        """
        # Check if interaction type has a registered callback
        if interaction_type in self.interaction_callbacks:
            callback = self.interaction_callbacks[interaction_type]
            try:
                callback(interaction_data)
                logger.debug(f"Handled interaction {interaction_type}")
                return True
            except Exception as e:
                logger.error(f"Error in interaction callback: {e}")
                return False
        
        # Handle standard interactions
        if interaction_type == "toggle_expansion":
            return self.toggle_expansion()
        
        elif interaction_type == "toggle_interactivity":
            return self.toggle_interactivity()
        
        elif interaction_type == "toggle_visibility":
            return self.set_visibility(not self.is_visible)
        
        elif interaction_type == "change_mode":
            mode_name = interaction_data.get("mode")
            try:
                mode = AmbientMode(mode_name)
                return self.set_mode(mode)
            except ValueError:
                logger.warning(f"Invalid mode: {mode_name}")
                return False
        
        elif interaction_type == "change_awareness_level":
            level_name = interaction_data.get("level")
            try:
                level = AwarenessLevel(level_name)
                return self.set_awareness_level(level)
            except ValueError:
                logger.warning(f"Invalid awareness level: {level_name}")
                return False
        
        elif interaction_type == "change_position":
            position = interaction_data.get("position")
            return self.set_position(position)
        
        elif interaction_type == "change_size":
            size = interaction_data.get("size")
            return self.set_size(size)
        
        elif interaction_type == "change_opacity":
            opacity = interaction_data.get("opacity")
            return self.set_opacity(opacity)
        
        elif interaction_type == "change_animation_speed":
            speed = interaction_data.get("speed")
            return self.set_animation_speed(speed)
        
        elif interaction_type == "dismiss_context":
            context_type = interaction_data.get("context_type")
            context_id = interaction_data.get("context_id")
            return self.dismiss_context_item(context_type, context_id)
        
        elif interaction_type == "focus_context":
            context_type = interaction_data.get("context_type")
            context_id = interaction_data.get("context_id")
            return self.focus_context_item(context_type, context_id)
        
        elif interaction_type == "dismiss_agent_state":
            agent_id = interaction_data.get("agent_id")
            return self.dismiss_agent_state(agent_id)
        
        elif interaction_type == "focus_agent_state":
            agent_id = interaction_data.get("agent_id")
            return self.focus_agent_state(agent_id)
        
        # Unknown interaction type
        logger.warning(f"Unknown interaction type: {interaction_type}")
        return False

    def dismiss_context_item(self, context_type: str, context_id: str) -> bool:
        """
        Dismiss a context item.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            
        Returns:
            True if item was dismissed, False otherwise
        """
        item_key = f"{context_type}:{context_id}"
        if item_key in self.context_items:
            del self.context_items[item_key]
            logger.debug(f"Dismissed context item {item_key}")
            self.refresh()
            return True
        
        return False

    def focus_context_item(self, context_type: str, context_id: str) -> bool:
        """
        Focus on a context item.
        
        Args:
            context_type: Type of context
            context_id: ID of the context
            
        Returns:
            True if item was focused, False otherwise
        """
        item_key = f"{context_type}:{context_id}"
        if item_key in self.context_items:
            # Mark all items as not new
            for key, item in self.context_items.items():
                item["is_new"] = False
            
            # Mark this item as new
            self.context_items[item_key]["is_new"] = True
            
            # Set mode to focused or interactive
            if self.current_mode == AmbientMode.BACKGROUND.value or self.current_mode == AmbientMode.PERIPHERAL.value:
                self.set_mode(AmbientMode.FOCUSED)
            
            logger.debug(f"Focused on context item {item_key}")
            self.refresh()
            return True
        
        return False

    def dismiss_agent_state(self, agent_id: str) -> bool:
        """
        Dismiss an agent state.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            True if state was dismissed, False otherwise
        """
        if agent_id in self.agent_states:
            del self.agent_states[agent_id]
            logger.debug(f"Dismissed agent state {agent_id}")
            self.refresh()
            return True
        
        return False

    def focus_agent_state(self, agent_id: str) -> bool:
        """
        Focus on an agent state.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            True if state was focused, False otherwise
        """
        if agent_id in self.agent_states:
            # Mark all states as not new
            for key, state in self.agent_states.items():
                state["is_new"] = False
            
            # Mark this state as new
            self.agent_states[agent_id]["is_new"] = True
            
            # Set mode to focused or interactive
            if self.current_mode == AmbientMode.BACKGROUND.value or self.current_mode == AmbientMode.PERIPHERAL.value:
                self.set_mode(AmbientMode.FOCUSED)
            
            logger.debug(f"Focused on agent state {agent_id}")
            self.refresh()
            return True
        
        return False

    def update_user_attention_metric(self, metric_type: str, metric_value: Any) -> bool:
        """
        Update a user attention metric.
        
        Args:
            metric_type: Type of metric
            metric_value: Metric value
            
        Returns:
            True if metric was updated, False otherwise
        """
        self.user_attention_metrics[metric_type] = {
            "type": metric_type,
            "value": metric_value,
            "timestamp": time.time()
        }
        
        # Adjust mode based on attention metrics
        self._adjust_mode_based_on_attention()
        
        logger.debug(f"Updated user attention metric {metric_type}")
        return True

    def _adjust_mode_based_on_attention(self):
        """Adjust mode based on user attention metrics."""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated attention tracking
        
        # Check if we have gaze data
        if "gaze" in self.user_attention_metrics:
            gaze_data = self.user_attention_metrics["gaze"]
            gaze_value = gaze_data.get("value", 0.0)
            
            # Adjust mode based on gaze
            if gaze_value > 0.8:  # User is looking directly at panel
                if self.current_mode == AmbientMode.BACKGROUND.value or self.current_mode == AmbientMode.PERIPHERAL.value:
                    self.set_mode(AmbientMode.FOCUSED)
            elif gaze_value > 0.4:  # User is looking near panel
                if self.current_mode == AmbientMode.BACKGROUND.value:
                    self.set_mode(AmbientMode.PERIPHERAL)
                elif self.current_mode == AmbientMode.FOCUSED.value:
                    self.set_mode(AmbientMode.PERIPHERAL)
            else:  # User is not looking at panel
                if self.current_mode == AmbientMode.PERIPHERAL.value or self.current_mode == AmbientMode.FOCUSED.value:
                    # Only go to background if awareness level allows
                    if self.current_awareness_level == AwarenessLevel.MINIMAL.value or self.current_awareness_level == AwarenessLevel.LOW.value:
                        self.set_mode(AmbientMode.BACKGROUND)
        
        # Check if we have focus data
        if "focus" in self.user_attention_metrics:
            focus_data = self.user_attention_metrics["focus"]
            focus_value = focus_data.get("value", 0.0)
            
            # Adjust mode based on focus
            if focus_value > 0.8:  # User is highly focused on task
                # Reduce ambient presence unless critical
                if self.current_awareness_level != AwarenessLevel.CRITICAL.value and self.current_awareness_level != AwarenessLevel.HIGH.value:
                    if self.current_mode == AmbientMode.FOCUSED.value or self.current_mode == AmbientMode.INTERACTIVE.value:
                        self.set_mode(AmbientMode.PERIPHERAL)
            elif focus_value < 0.3:  # User has low focus on task
                # Increase ambient presence
                if self.current_mode == AmbientMode.BACKGROUND.value:
                    self.set_mode(AmbientMode.PERIPHERAL)

    def refresh(self) -> bool:
        """
        Refresh the panel.
        
        Returns:
            True if refresh was successful, False otherwise
        """
        # This would trigger a re-render in a real implementation
        # For this implementation, we'll just log the refresh
        logger.debug("Refreshing ambient awareness panel")
        
        # Mark all new items as not new
        for key, item in self.context_items.items():
            if item["is_new"]:
                item["is_new"] = False
        
        for key, state in self.agent_states.items():
            if state["is_new"]:
                state["is_new"] = False
        
        for key, status in self.system_statuses.items():
            if status["is_new"]:
                status["is_new"] = False
        
        for key, condition in self.environmental_conditions.items():
            if condition["is_new"]:
                condition["is_new"] = False
        
        return True

    def get_panel_state(self) -> Dict[str, Any]:
        """
        Get the current panel state.
        
        Returns:
            Panel state
        """
        return {
            "id": self.panel_id,
            "mode": self.current_mode,
            "awareness_level": self.current_awareness_level,
            "is_visible": self.is_visible,
            "is_expanded": self.is_expanded,
            "is_interactive": self.is_interactive,
            "position": self.position,
            "size": self.size,
            "opacity": self.opacity,
            "animation_speed": self.animation_speed,
            "context_items_count": len(self.context_items),
            "agent_states_count": len(self.agent_states),
            "system_statuses_count": len(self.system_statuses),
            "environmental_conditions_count": len(self.environmental_conditions)
        }

    def get_context_items(self, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get context items.
        
        Args:
            max_items: Maximum number of items to return
            
        Returns:
            List of context items
        """
        # Sort items by priority and timestamp
        sorted_items = sorted(
            self.context_items.values(),
            key=lambda x: (
                0 if x["priority"] == "critical" else
                1 if x["priority"] == "high" else
                2 if x["priority"] == "medium" else
                3 if x["priority"] == "low" else 4,
                -x["timestamp"]
            )
        )
        
        # Limit number of items if specified
        if max_items is not None:
            sorted_items = sorted_items[:max_items]
        
        return sorted_items

    def get_agent_states(self, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get agent states.
        
        Args:
            max_items: Maximum number of items to return
            
        Returns:
            List of agent states
        """
        # Sort states by status and timestamp
        sorted_states = sorted(
            self.agent_states.values(),
            key=lambda x: (
                0 if x["state"].get("status") == "critical" else
                1 if x["state"].get("status") == "warning" else
                2 if x["state"].get("status") == "active" else
                3 if x["state"].get("status") == "idle" else 4,
                -x["timestamp"]
            )
        )
        
        # Limit number of items if specified
        if max_items is not None:
            sorted_states = sorted_states[:max_items]
        
        return sorted_states

    def get_system_statuses(self, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get system statuses.
        
        Args:
            max_items: Maximum number of items to return
            
        Returns:
            List of system statuses
        """
        # Sort statuses by level and timestamp
        sorted_statuses = sorted(
            self.system_statuses.values(),
            key=lambda x: (
                0 if x["data"].get("level") == "critical" else
                1 if x["data"].get("level") == "warning" else
                2 if x["data"].get("level") == "notice" else
                3 if x["data"].get("level") == "info" else 4,
                -x["timestamp"]
            )
        )
        
        # Limit number of items if specified
        if max_items is not None:
            sorted_statuses = sorted_statuses[:max_items]
        
        return sorted_statuses

    def get_environmental_conditions(self, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get environmental conditions.
        
        Args:
            max_items: Maximum number of items to return
            
        Returns:
            List of environmental conditions
        """
        # Sort conditions by level and timestamp
        sorted_conditions = sorted(
            self.environmental_conditions.values(),
            key=lambda x: (
                0 if x["data"].get("level") == "critical" else
                1 if x["data"].get("level") == "warning" else
                2 if x["data"].get("level") == "notice" else
                3 if x["data"].get("level") == "info" else 4,
                -x["timestamp"]
            )
        )
        
        # Limit number of items if specified
        if max_items is not None:
            sorted_conditions = sorted_conditions[:max_items]
        
        return sorted_conditions

    def get_user_attention_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get user attention metrics.
        
        Returns:
            User attention metrics
        """
        return self.user_attention_metrics

    def clear_all_items(self) -> bool:
        """
        Clear all items.
        
        Returns:
            True if items were cleared, False otherwise
        """
        self.context_items = {}
        self.agent_states = {}
        self.system_statuses = {}
        self.environmental_conditions = {}
        
        logger.debug("Cleared all items")
        self.refresh()
        return True

    def render(self, target_platform: str = "web") -> Dict[str, Any]:
        """
        Render the panel for a specific platform.
        
        Args:
            target_platform: Target platform for rendering
            
        Returns:
            Rendering result
        """
        # This is a simplified implementation
        # In a real system, this would generate actual rendering instructions
        
        # Get panel state
        panel_state = self.get_panel_state()
        
        # Get content based on mode and awareness level
        max_context_items = 10
        max_agent_states = 5
        max_system_statuses = 3
        max_environmental_conditions = 3
        
        if panel_state["mode"] == AmbientMode.BACKGROUND.value:
            max_context_items = 1
            max_agent_states = 1
            max_system_statuses = 1
            max_environmental_conditions = 0
        
        elif panel_state["mode"] == AmbientMode.PERIPHERAL.value:
            max_context_items = 3
            max_agent_states = 2
            max_system_statuses = 1
            max_environmental_conditions = 1
        
        # Get content
        context_items = self.get_context_items(max_context_items)
        agent_states = self.get_agent_states(max_agent_states)
        system_statuses = self.get_system_statuses(max_system_statuses)
        environmental_conditions = self.get_environmental_conditions(max_environmental_conditions)
        
        # Generate rendering instructions based on platform
        if target_platform == "web":
            return self._generate_web_rendering(panel_state, context_items, agent_states, system_statuses, environmental_conditions)
        
        elif target_platform == "mobile":
            return self._generate_mobile_rendering(panel_state, context_items, agent_states, system_statuses, environmental_conditions)
        
        elif target_platform == "desktop":
            return self._generate_desktop_rendering(panel_state, context_items, agent_states, system_statuses, environmental_conditions)
        
        elif target_platform == "ar":
            return self._generate_ar_rendering(panel_state, context_items, agent_states, system_statuses, environmental_conditions)
        
        else:
            logger.warning(f"Unknown target platform: {target_platform}")
            return {}

    def _generate_web_rendering(
        self,
        panel_state: Dict[str, Any],
        context_items: List[Dict[str, Any]],
        agent_states: List[Dict[str, Any]],
        system_statuses: List[Dict[str, Any]],
        environmental_conditions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate web rendering instructions.
        
        Args:
            panel_state: Panel state
            context_items: Context items
            agent_states: Agent states
            system_statuses: System statuses
            environmental_conditions: Environmental conditions
            
        Returns:
            Web rendering instructions
        """
        # Get theme colors
        theme = self.current_theme
        colors = theme.get("colors", {})
        
        # Determine panel color based on awareness level
        panel_color = colors.get("background", "#FFFFFF")
        border_color = colors.get("border", "#CCCCCC")
        text_color = colors.get("text", "#333333")
        
        if panel_state["awareness_level"] == AwarenessLevel.CRITICAL.value:
            panel_color = colors.get("critical", "#E74C3C")
            border_color = colors.get("critical", "#E74C3C")
            text_color = "#FFFFFF"
        
        elif panel_state["awareness_level"] == AwarenessLevel.HIGH.value:
            panel_color = colors.get("warning", "#F39C12")
            border_color = colors.get("warning", "#F39C12")
            text_color = "#FFFFFF"
        
        elif panel_state["awareness_level"] == AwarenessLevel.MEDIUM.value:
            panel_color = colors.get("info", "#3498DB")
            border_color = colors.get("info", "#3498DB")
            text_color = "#FFFFFF"
        
        # Generate CSS
        css = {
            "panel": {
                "position": "fixed",
                "z-index": "9999",
                "background-color": panel_color,
                "border": f"1px solid {border_color}",
                "border-radius": "8px",
                "box-shadow": "0 2px 10px rgba(0, 0, 0, 0.2)",
                "color": text_color,
                "font-family": "Inter, sans-serif",
                "transition": f"all {0.3 / panel_state['animation_speed']}s ease-in-out",
                "opacity": str(panel_state["opacity"])
            },
            "header": {
                "padding": "8px 12px",
                "border-bottom": f"1px solid {border_color}",
                "display": "flex",
                "justify-content": "space-between",
                "align-items": "center"
            },
            "title": {
                "font-size": "14px",
                "font-weight": "bold",
                "margin": "0"
            },
            "controls": {
                "display": "flex",
                "gap": "8px"
            },
            "control": {
                "background": "none",
                "border": "none",
                "color": text_color,
                "cursor": "pointer",
                "padding": "4px",
                "border-radius": "4px",
                "opacity": "0.8",
                "transition": "opacity 0.2s ease-in-out"
            },
            "content": {
                "padding": "12px",
                "overflow-y": "auto"
            },
            "section": {
                "margin-bottom": "12px"
            },
            "section_title": {
                "font-size": "12px",
                "font-weight": "bold",
                "margin": "0 0 8px 0",
                "opacity": "0.8"
            },
            "item": {
                "padding": "8px",
                "border-radius": "4px",
                "margin-bottom": "8px",
                "background-color": "rgba(255, 255, 255, 0.1)",
                "transition": "background-color 0.2s ease-in-out"
            },
            "item_new": {
                "border-left": "3px solid #FFFFFF"
            },
            "item_title": {
                "font-size": "13px",
                "font-weight": "bold",
                "margin": "0 0 4px 0"
            },
            "item_description": {
                "font-size": "12px",
                "margin": "0 0 4px 0",
                "opacity": "0.9"
            },
            "item_meta": {
                "font-size": "11px",
                "opacity": "0.7",
                "display": "flex",
                "justify-content": "space-between"
            },
            "footer": {
                "padding": "8px 12px",
                "border-top": f"1px solid {border_color}",
                "font-size": "11px",
                "opacity": "0.7",
                "text-align": "center"
            }
        }
        
        # Set position based on panel position
        if panel_state["position"] == "top-left":
            css["panel"]["top"] = "16px"
            css["panel"]["left"] = "16px"
        
        elif panel_state["position"] == "top-right":
            css["panel"]["top"] = "16px"
            css["panel"]["right"] = "16px"
        
        elif panel_state["position"] == "bottom-left":
            css["panel"]["bottom"] = "16px"
            css["panel"]["left"] = "16px"
        
        elif panel_state["position"] == "bottom-right":
            css["panel"]["bottom"] = "16px"
            css["panel"]["right"] = "16px"
        
        elif panel_state["position"] == "top":
            css["panel"]["top"] = "16px"
            css["panel"]["left"] = "50%"
            css["panel"]["transform"] = "translateX(-50%)"
        
        elif panel_state["position"] == "bottom":
            css["panel"]["bottom"] = "16px"
            css["panel"]["left"] = "50%"
            css["panel"]["transform"] = "translateX(-50%)"
        
        elif panel_state["position"] == "left":
            css["panel"]["left"] = "16px"
            css["panel"]["top"] = "50%"
            css["panel"]["transform"] = "translateY(-50%)"
        
        elif panel_state["position"] == "right":
            css["panel"]["right"] = "16px"
            css["panel"]["top"] = "50%"
            css["panel"]["transform"] = "translateY(-50%)"
        
        elif panel_state["position"] == "center":
            css["panel"]["top"] = "50%"
            css["panel"]["left"] = "50%"
            css["panel"]["transform"] = "translate(-50%, -50%)"
        
        # Set size based on panel size
        if panel_state["size"] == "small":
            css["panel"]["width"] = "240px"
            css["panel"]["max-height"] = "320px"
            css["content"]["max-height"] = "240px"
        
        elif panel_state["size"] == "medium":
            css["panel"]["width"] = "320px"
            css["panel"]["max-height"] = "480px"
            css["content"]["max-height"] = "400px"
        
        elif panel_state["size"] == "large":
            css["panel"]["width"] = "400px"
            css["panel"]["max-height"] = "640px"
            css["content"]["max-height"] = "560px"
        
        elif panel_state["size"] == "full":
            css["panel"]["width"] = "100%"
            css["panel"]["height"] = "100%"
            css["panel"]["top"] = "0"
            css["panel"]["left"] = "0"
            css["panel"]["right"] = "0"
            css["panel"]["bottom"] = "0"
            css["panel"]["border-radius"] = "0"
            css["panel"]["transform"] = "none"
            css["content"]["max-height"] = "calc(100% - 80px)"
        
        # Generate HTML structure
        html_structure = {
            "tag": "div",
            "attributes": {
                "id": f"ambient-awareness-panel-{panel_state['id']}",
                "class": f"ambient-awareness-panel mode-{panel_state['mode']} level-{panel_state['awareness_level']}"
            },
            "children": [
                {
                    "tag": "div",
                    "attributes": {"class": "ambient-awareness-panel-header"},
                    "children": [
                        {
                            "tag": "h3",
                            "attributes": {"class": "ambient-awareness-panel-title"},
                            "text": "Ambient Awareness"
                        },
                        {
                            "tag": "div",
                            "attributes": {"class": "ambient-awareness-panel-controls"},
                            "children": [
                                {
                                    "tag": "button",
                                    "attributes": {
                                        "class": "ambient-awareness-panel-control",
                                        "data-action": "toggle_expansion"
                                    },
                                    "text": panel_state["is_expanded"] ? "−" : "+"
                                },
                                {
                                    "tag": "button",
                                    "attributes": {
                                        "class": "ambient-awareness-panel-control",
                                        "data-action": "toggle_visibility"
                                    },
                                    "text": "×"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        // Add content if panel is expanded
        if (panel_state["is_expanded"]) {
            const content_element = {
                "tag": "div",
                "attributes": {"class": "ambient-awareness-panel-content"},
                "children": []
            };
            
            // Add context items section if there are items
            if (context_items.length > 0) {
                const context_section = {
                    "tag": "div",
                    "attributes": {"class": "ambient-awareness-panel-section"},
                    "children": [
                        {
                            "tag": "h4",
                            "attributes": {"class": "ambient-awareness-panel-section-title"},
                            "text": "Context"
                        }
                    ]
                };
                
                // Add context items
                for (const item of context_items) {
                    const item_element = {
                        "tag": "div",
                        "attributes": {
                            "class": `ambient-awareness-panel-item ${item["is_new"] ? "ambient-awareness-panel-item-new" : ""}`,
                            "data-context-type": item["type"],
                            "data-context-id": item["id"]
                        },
                        "children": [
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-title"},
                                "text": item["data"]["name"] || "Unnamed Context"
                            },
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-description"},
                                "text": item["data"]["description"] || ""
                            },
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-meta"},
                                "children": [
                                    {
                                        "tag": "span",
                                        "text": item["priority"]
                                    },
                                    {
                                        "tag": "span",
                                        "text": new Date(item["timestamp"] * 1000).toLocaleTimeString()
                                    }
                                ]
                            }
                        ]
                    };
                    
                    context_section["children"].push(item_element);
                }
                
                content_element["children"].push(context_section);
            }
            
            // Add agent states section if there are states
            if (agent_states.length > 0) {
                const agent_section = {
                    "tag": "div",
                    "attributes": {"class": "ambient-awareness-panel-section"},
                    "children": [
                        {
                            "tag": "h4",
                            "attributes": {"class": "ambient-awareness-panel-section-title"},
                            "text": "Agents"
                        }
                    ]
                };
                
                // Add agent states
                for (const state of agent_states) {
                    const state_element = {
                        "tag": "div",
                        "attributes": {
                            "class": `ambient-awareness-panel-item ${state["is_new"] ? "ambient-awareness-panel-item-new" : ""}`,
                            "data-agent-id": state["id"]
                        },
                        "children": [
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-title"},
                                "text": state["state"]["name"] || "Unnamed Agent"
                            },
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-description"},
                                "text": state["state"]["status"] || "Unknown Status"
                            },
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-meta"},
                                "children": [
                                    {
                                        "tag": "span",
                                        "text": state["state"]["activity"] || "Idle"
                                    },
                                    {
                                        "tag": "span",
                                        "text": new Date(state["timestamp"] * 1000).toLocaleTimeString()
                                    }
                                ]
                            }
                        ]
                    };
                    
                    agent_section["children"].push(state_element);
                }
                
                content_element["children"].push(agent_section);
            }
            
            // Add system statuses section if there are statuses
            if (system_statuses.length > 0) {
                const status_section = {
                    "tag": "div",
                    "attributes": {"class": "ambient-awareness-panel-section"},
                    "children": [
                        {
                            "tag": "h4",
                            "attributes": {"class": "ambient-awareness-panel-section-title"},
                            "text": "System"
                        }
                    ]
                };
                
                // Add system statuses
                for (const status of system_statuses) {
                    const status_element = {
                        "tag": "div",
                        "attributes": {
                            "class": `ambient-awareness-panel-item ${status["is_new"] ? "ambient-awareness-panel-item-new" : ""}`,
                            "data-status-type": status["type"]
                        },
                        "children": [
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-title"},
                                "text": status["data"]["name"] || status["type"]
                            },
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-description"},
                                "text": status["data"]["message"] || ""
                            },
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-meta"},
                                "children": [
                                    {
                                        "tag": "span",
                                        "text": status["data"]["level"] || "info"
                                    },
                                    {
                                        "tag": "span",
                                        "text": new Date(status["timestamp"] * 1000).toLocaleTimeString()
                                    }
                                ]
                            }
                        ]
                    };
                    
                    status_section["children"].push(status_element);
                }
                
                content_element["children"].push(status_section);
            }
            
            // Add environmental conditions section if there are conditions
            if (environmental_conditions.length > 0) {
                const condition_section = {
                    "tag": "div",
                    "attributes": {"class": "ambient-awareness-panel-section"},
                    "children": [
                        {
                            "tag": "h4",
                            "attributes": {"class": "ambient-awareness-panel-section-title"},
                            "text": "Environment"
                        }
                    ]
                };
                
                // Add environmental conditions
                for (const condition of environmental_conditions) {
                    const condition_element = {
                        "tag": "div",
                        "attributes": {
                            "class": `ambient-awareness-panel-item ${condition["is_new"] ? "ambient-awareness-panel-item-new" : ""}`,
                            "data-condition-type": condition["type"]
                        },
                        "children": [
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-title"},
                                "text": condition["data"]["name"] || condition["type"]
                            },
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-description"},
                                "text": condition["data"]["message"] || ""
                            },
                            {
                                "tag": "div",
                                "attributes": {"class": "ambient-awareness-panel-item-meta"},
                                "children": [
                                    {
                                        "tag": "span",
                                        "text": condition["data"]["level"] || "info"
                                    },
                                    {
                                        "tag": "span",
                                        "text": new Date(condition["timestamp"] * 1000).toLocaleTimeString()
                                    }
                                ]
                            }
                        ]
                    };
                    
                    condition_section["children"].push(condition_element);
                }
                
                content_element["children"].push(condition_section);
            }
            
            // Add content element to panel
            html_structure["children"].push(content_element);
            
            // Add footer
            html_structure["children"].push({
                "tag": "div",
                "attributes": {"class": "ambient-awareness-panel-footer"},
                "text": `Awareness Level: ${panel_state["awareness_level"]} | Mode: ${panel_state["mode"]}`
            });
        }
        
        // Return rendering instructions
        return {
            "panel_id": panel_state["id"],
            "platform": "web",
            "css": css,
            "html": html_structure,
            "animations": {
                "fade_in": "@keyframes fade-in { 0% { opacity: 0; } 100% { opacity: 1; } }",
                "pulse": "@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }"
            },
            "event_handlers": {
                "click": "handleAmbientPanelClick(event)",
                "mouseover": "handleAmbientPanelMouseOver(event)",
                "mouseout": "handleAmbientPanelMouseOut(event)"
            }
        };
    }

    def _generate_mobile_rendering(
        self,
        panel_state: Dict[str, Any],
        context_items: List[Dict[str, Any]],
        agent_states: List[Dict[str, Any]],
        system_statuses: List[Dict[str, Any]],
        environmental_conditions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate mobile rendering instructions.
        
        Args:
            panel_state: Panel state
            context_items: Context items
            agent_states: Agent states
            system_statuses: System statuses
            environmental_conditions: Environmental conditions
            
        Returns:
            Mobile rendering instructions
        """
        # Similar to web rendering but with mobile-specific adjustments
        web_rendering = self._generate_web_rendering(panel_state, context_items, agent_states, system_statuses, environmental_conditions)
        
        # Adjust for mobile
        web_rendering["platform"] = "mobile"
        
        # Make touch-friendly adjustments
        if "css" in web_rendering:
            # Increase touch targets
            if "control" in web_rendering["css"]:
                web_rendering["css"]["control"]["padding"] = "8px"
            
            # Adjust font sizes
            for element in ["title", "section_title", "item_title", "item_description", "item_meta"]:
                if element in web_rendering["css"]:
                    current_size = web_rendering["css"][element].get("font-size", "14px")
                    size_value = int(current_size.replace("px", ""))
                    web_rendering["css"][element]["font-size"] = f"{size_value + 2}px"
            
            # Adjust panel size for mobile
            web_rendering["css"]["panel"]["width"] = "90%"
            web_rendering["css"]["panel"]["max-width"] = "360px"
        
        # Replace mouse events with touch events
        if "event_handlers" in web_rendering:
            web_rendering["event_handlers"] = {
                "touchstart": "handleAmbientPanelTouchStart(event)",
                "touchend": "handleAmbientPanelTouchEnd(event)"
            }
        
        return web_rendering

    def _generate_desktop_rendering(
        self,
        panel_state: Dict[str, Any],
        context_items: List[Dict[str, Any]],
        agent_states: List[Dict[str, Any]],
        system_statuses: List[Dict[str, Any]],
        environmental_conditions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate desktop rendering instructions.
        
        Args:
            panel_state: Panel state
            context_items: Context items
            agent_states: Agent states
            system_statuses: System statuses
            environmental_conditions: Environmental conditions
            
        Returns:
            Desktop rendering instructions
        """
        # For desktop native apps
        # This would generate platform-specific instructions
        # For simplicity, we'll use a modified version of web rendering
        
        web_rendering = self._generate_web_rendering(panel_state, context_items, agent_states, system_statuses, environmental_conditions)
        
        # Adjust for desktop
        web_rendering["platform"] = "desktop"
        
        # Add desktop-specific properties
        web_rendering["desktop_properties"] = {
            "window_title": "Ambient Awareness",
            "window_icon": "ambient_icon",
            "window_size": {"width": 400, "height": 600},
            "window_resizable": True,
            "window_always_on_top": True,
            "window_frameless": True,
            "window_transparent": True
        }
        
        return web_rendering

    def _generate_ar_rendering(
        self,
        panel_state: Dict[str, Any],
        context_items: List[Dict[str, Any]],
        agent_states: List[Dict[str, Any]],
        system_statuses: List[Dict[str, Any]],
        environmental_conditions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate AR rendering instructions.
        
        Args:
            panel_state: Panel state
            context_items: Context items
            agent_states: Agent states
            system_statuses: System statuses
            environmental_conditions: Environmental conditions
            
        Returns:
            AR rendering instructions
        """
        # For AR applications
        # This would generate AR-specific rendering instructions
        
        # Get theme colors
        theme = self.current_theme
        colors = theme.get("colors", {})
        
        # Determine panel color based on awareness level
        panel_color = colors.get("background", "#FFFFFF")
        border_color = colors.get("border", "#CCCCCC")
        text_color = colors.get("text", "#333333")
        
        if panel_state["awareness_level"] == AwarenessLevel.CRITICAL.value:
            panel_color = colors.get("critical", "#E74C3C")
            border_color = colors.get("critical", "#E74C3C")
            text_color = "#FFFFFF"
        
        elif panel_state["awareness_level"] == AwarenessLevel.HIGH.value:
            panel_color = colors.get("warning", "#F39C12")
            border_color = colors.get("warning", "#F39C12")
            text_color = "#FFFFFF"
        
        elif panel_state["awareness_level"] == AwarenessLevel.MEDIUM.value:
            panel_color = colors.get("info", "#3498DB")
            border_color = colors.get("info", "#3498DB")
            text_color = "#FFFFFF"
        
        # Generate AR-specific rendering instructions
        ar_rendering = {
            "panel_id": panel_state["id"],
            "platform": "ar",
            "ar_object": {
                "type": "panel",
                "width": 0.4,
                "height": 0.3,
                "depth": 0.01,
                "color": panel_color,
                "border_color": border_color,
                "border_width": 0.002,
                "corner_radius": 0.01,
                "opacity": panel_state["opacity"]
            },
            "ar_text": {
                "title": {
                    "text": "Ambient Awareness",
                    "position": {"x": 0, "y": 0.12, "z": 0.011},
                    "scale": 0.025,
                    "color": text_color
                }
            },
            "ar_interactions": {
                "tap": {
                    "action": "toggle_expansion",
                    "parameters": {}
                },
                "long_press": {
                    "action": "toggle_visibility",
                    "parameters": {}
                }
            },
            "ar_animations": {
                "idle": {
                    "type": "float",
                    "amplitude": 0.005,
                    "frequency": 0.5
                },
                "alert": {
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
        
        # Add content if panel is expanded
        if panel_state["is_expanded"]:
            # Add context items
            ar_rendering["ar_content"] = {
                "context_items": [],
                "agent_states": [],
                "system_statuses": [],
                "environmental_conditions": []
            }
            
            # Add context items
            for i, item in enumerate(context_items):
                y_position = 0.08 - (i * 0.04)
                
                ar_rendering["ar_content"]["context_items"].append({
                    "text": item["data"].get("name", "Unnamed Context"),
                    "position": {"x": 0, "y": y_position, "z": 0.011},
                    "scale": 0.02,
                    "color": text_color,
                    "priority": item["priority"],
                    "is_new": item["is_new"]
                })
            
            # Add agent states
            for i, state in enumerate(agent_states):
                y_position = 0.08 - (len(context_items) * 0.04) - (i * 0.04)
                
                ar_rendering["ar_content"]["agent_states"].append({
                    "text": state["state"].get("name", "Unnamed Agent"),
                    "position": {"x": 0, "y": y_position, "z": 0.011},
                    "scale": 0.02,
                    "color": text_color,
                    "status": state["state"].get("status", "unknown"),
                    "is_new": state["is_new"]
                })
            
            # Add system statuses
            for i, status in enumerate(system_statuses):
                y_position = 0.08 - (len(context_items) * 0.04) - (len(agent_states) * 0.04) - (i * 0.04)
                
                ar_rendering["ar_content"]["system_statuses"].append({
                    "text": status["data"].get("name", status["type"]),
                    "position": {"x": 0, "y": y_position, "z": 0.011},
                    "scale": 0.02,
                    "color": text_color,
                    "level": status["data"].get("level", "info"),
                    "is_new": status["is_new"]
                })
        
        # Add awareness level animation
        if panel_state["awareness_level"] == AwarenessLevel.CRITICAL.value:
            ar_rendering["ar_animations"]["awareness"] = {
                "type": "pulse",
                "color": colors.get("critical", "#E74C3C"),
                "intensity": 0.8,
                "frequency": 1.0
            }
        
        elif panel_state["awareness_level"] == AwarenessLevel.HIGH.value:
            ar_rendering["ar_animations"]["awareness"] = {
                "type": "pulse",
                "color": colors.get("warning", "#F39C12"),
                "intensity": 0.5,
                "frequency": 0.5
            }
        
        return ar_rendering
