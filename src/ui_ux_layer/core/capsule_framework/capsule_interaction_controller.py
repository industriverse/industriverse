"""
Capsule Interaction Controller for Capsule Framework

This module manages user interactions with capsules within the Capsule Framework
of the Industriverse UI/UX Layer. It implements interaction patterns, gestures,
and event handling for Dynamic Agent Capsules.

The Capsule Interaction Controller:
1. Defines and manages capsule interaction patterns
2. Handles user gestures and input events for capsules
3. Coordinates capsule focus and selection
4. Provides an API for customizing capsule interactions
5. Integrates with the Interaction Mode Manager for adaptive interactions

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import threading

# Local imports
from ..context_engine.context_awareness_engine import ContextAwarenessEngine
from ..universal_skin.interaction_mode_manager import InteractionModeManager
from .capsule_state_manager import CapsuleStateManager

# Configure logging
logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """Enumeration of capsule interaction types."""
    TAP = "tap"                  # Single tap/click
    DOUBLE_TAP = "double_tap"    # Double tap/click
    LONG_PRESS = "long_press"    # Long press/hold
    SWIPE = "swipe"              # Swipe gesture
    DRAG = "drag"                # Drag gesture
    PINCH = "pinch"              # Pinch gesture
    HOVER = "hover"              # Hover over
    FOCUS = "focus"              # Focus (keyboard/voice)
    COMMAND = "command"          # Voice/text command

class SwipeDirection(Enum):
    """Enumeration of swipe directions."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class CapsuleInteractionController:
    """
    Manages user interactions with capsules within the Capsule Framework.
    
    This class is responsible for implementing interaction patterns, gestures,
    and event handling for Dynamic Agent Capsules.
    """
    
    def __init__(
        self, 
        context_engine: ContextAwarenessEngine,
        interaction_mode_manager: InteractionModeManager,
        state_manager: CapsuleStateManager
    ):
        """
        Initialize the Capsule Interaction Controller.
        
        Args:
            context_engine: The Context Awareness Engine instance
            interaction_mode_manager: The Interaction Mode Manager instance
            state_manager: The Capsule State Manager instance
        """
        self.context_engine = context_engine
        self.interaction_mode_manager = interaction_mode_manager
        self.state_manager = state_manager
        
        # Interaction handlers by capsule ID and interaction type
        self.interaction_handlers = {}
        
        # Default interaction handlers
        self.default_handlers = self._create_default_handlers()
        
        # Currently focused capsule
        self.focused_capsule_id = None
        
        # Recently interacted capsules (for history)
        self.interaction_history = []
        
        # Interaction event listeners
        self.event_listeners = {}
        
        # Gesture recognition thresholds
        self.gesture_thresholds = {
            "tap_distance": 10,           # Max distance for tap (px)
            "double_tap_time": 300,       # Max time between taps (ms)
            "long_press_time": 500,       # Min time for long press (ms)
            "swipe_min_distance": 50,     # Min distance for swipe (px)
            "swipe_max_time": 300,        # Max time for swipe (ms)
            "drag_min_distance": 10,      # Min distance for drag (px)
            "pinch_min_distance": 30      # Min distance for pinch (px)
        }
        
        # Register as state listener
        self.state_manager.register_state_listener(self._handle_state_change)
        
        # Register for context changes
        self.context_engine.register_context_listener(self._handle_context_change)
        
        logger.info("Capsule Interaction Controller initialized")
    
    def _create_default_handlers(self) -> Dict:
        """
        Create default interaction handlers.
        
        Returns:
            Dictionary of default handlers by interaction type
        """
        return {
            InteractionType.TAP.value: self._default_tap_handler,
            InteractionType.DOUBLE_TAP.value: self._default_double_tap_handler,
            InteractionType.LONG_PRESS.value: self._default_long_press_handler,
            InteractionType.SWIPE.value: self._default_swipe_handler,
            InteractionType.DRAG.value: self._default_drag_handler,
            InteractionType.PINCH.value: self._default_pinch_handler,
            InteractionType.HOVER.value: self._default_hover_handler,
            InteractionType.FOCUS.value: self._default_focus_handler,
            InteractionType.COMMAND.value: self._default_command_handler
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
            
            # Adjust gesture thresholds based on device type
            if "device_type" in device_data:
                device_type = device_data["device_type"]
                self._adjust_gesture_thresholds(device_type)
        
        # Handle user context changes
        elif context_type == "user":
            user_data = event.get("data", {})
            
            # Adjust interaction based on user preferences
            if "interaction_preferences" in user_data:
                preferences = user_data["interaction_preferences"]
                self._apply_user_preferences(preferences)
    
    def _handle_state_change(self, capsule_id: str, state: str, metadata: Dict = None) -> None:
        """
        Handle capsule state changes.
        
        Args:
            capsule_id: Capsule ID that changed
            state: New state
            metadata: Optional metadata
        """
        # If focused capsule is terminated, clear focus
        if capsule_id == self.focused_capsule_id and state == "terminated":
            self.focused_capsule_id = None
    
    def _adjust_gesture_thresholds(self, device_type: str) -> None:
        """
        Adjust gesture thresholds based on device type.
        
        Args:
            device_type: Device type (mobile, tablet, desktop, etc.)
        """
        if device_type == "mobile":
            # Adjust for touch screens
            self.gesture_thresholds.update({
                "tap_distance": 15,
                "double_tap_time": 400,
                "long_press_time": 600,
                "swipe_min_distance": 40,
                "swipe_max_time": 400,
                "drag_min_distance": 15,
                "pinch_min_distance": 25
            })
        elif device_type == "tablet":
            # Adjust for larger touch screens
            self.gesture_thresholds.update({
                "tap_distance": 12,
                "double_tap_time": 350,
                "long_press_time": 550,
                "swipe_min_distance": 45,
                "swipe_max_time": 350,
                "drag_min_distance": 12,
                "pinch_min_distance": 30
            })
        elif device_type == "desktop":
            # Adjust for mouse/trackpad
            self.gesture_thresholds.update({
                "tap_distance": 5,
                "double_tap_time": 300,
                "long_press_time": 500,
                "swipe_min_distance": 50,
                "swipe_max_time": 300,
                "drag_min_distance": 5,
                "pinch_min_distance": 30
            })
        elif device_type == "ar" or device_type == "vr":
            # Adjust for spatial interactions
            self.gesture_thresholds.update({
                "tap_distance": 20,
                "double_tap_time": 450,
                "long_press_time": 700,
                "swipe_min_distance": 60,
                "swipe_max_time": 500,
                "drag_min_distance": 20,
                "pinch_min_distance": 40
            })
    
    def _apply_user_preferences(self, preferences: Dict) -> None:
        """
        Apply user interaction preferences.
        
        Args:
            preferences: User interaction preferences
        """
        # Adjust gesture thresholds based on user preferences
        if "gesture_sensitivity" in preferences:
            sensitivity = preferences["gesture_sensitivity"]
            
            # Scale thresholds based on sensitivity (0.5-2.0)
            if sensitivity < 1.0:
                # Higher sensitivity (lower thresholds)
                scale_factor = 1.0 / max(0.5, sensitivity)
                self.gesture_thresholds.update({
                    "tap_distance": self.gesture_thresholds["tap_distance"] * scale_factor,
                    "swipe_min_distance": self.gesture_thresholds["swipe_min_distance"] / scale_factor,
                    "drag_min_distance": self.gesture_thresholds["drag_min_distance"] / scale_factor,
                    "pinch_min_distance": self.gesture_thresholds["pinch_min_distance"] / scale_factor
                })
            elif sensitivity > 1.0:
                # Lower sensitivity (higher thresholds)
                scale_factor = min(2.0, sensitivity)
                self.gesture_thresholds.update({
                    "tap_distance": self.gesture_thresholds["tap_distance"] / scale_factor,
                    "swipe_min_distance": self.gesture_thresholds["swipe_min_distance"] * scale_factor,
                    "drag_min_distance": self.gesture_thresholds["drag_min_distance"] * scale_factor,
                    "pinch_min_distance": self.gesture_thresholds["pinch_min_distance"] * scale_factor
                })
        
        # Adjust timing thresholds based on user preferences
        if "interaction_speed" in preferences:
            speed = preferences["interaction_speed"]
            
            # Scale timing thresholds based on speed (0.5-2.0)
            if speed < 1.0:
                # Slower interactions (higher time thresholds)
                scale_factor = 1.0 / max(0.5, speed)
                self.gesture_thresholds.update({
                    "double_tap_time": self.gesture_thresholds["double_tap_time"] * scale_factor,
                    "long_press_time": self.gesture_thresholds["long_press_time"] * scale_factor,
                    "swipe_max_time": self.gesture_thresholds["swipe_max_time"] * scale_factor
                })
            elif speed > 1.0:
                # Faster interactions (lower time thresholds)
                scale_factor = min(2.0, speed)
                self.gesture_thresholds.update({
                    "double_tap_time": self.gesture_thresholds["double_tap_time"] / scale_factor,
                    "long_press_time": self.gesture_thresholds["long_press_time"] / scale_factor,
                    "swipe_max_time": self.gesture_thresholds["swipe_max_time"] / scale_factor
                })
    
    def register_interaction_handler(
        self, 
        capsule_id: str, 
        interaction_type: str, 
        handler: callable
    ) -> bool:
        """
        Register an interaction handler for a specific capsule.
        
        Args:
            capsule_id: Capsule ID to register handler for
            interaction_type: Type of interaction to handle
            handler: Handler function
            
        Returns:
            Boolean indicating success
        """
        # Verify interaction type
        if not any(t.value == interaction_type for t in InteractionType):
            logger.error(f"Invalid interaction type: {interaction_type}")
            return False
        
        # Initialize handlers for capsule if needed
        if capsule_id not in self.interaction_handlers:
            self.interaction_handlers[capsule_id] = {}
        
        # Register handler
        self.interaction_handlers[capsule_id][interaction_type] = handler
        
        logger.debug(f"Registered {interaction_type} handler for capsule {capsule_id}")
        return True
    
    def unregister_interaction_handler(
        self, 
        capsule_id: str, 
        interaction_type: str
    ) -> bool:
        """
        Unregister an interaction handler for a specific capsule.
        
        Args:
            capsule_id: Capsule ID to unregister handler for
            interaction_type: Type of interaction to unregister
            
        Returns:
            Boolean indicating success
        """
        # Verify capsule has handlers
        if capsule_id not in self.interaction_handlers:
            return False
        
        # Verify interaction type is registered
        if interaction_type not in self.interaction_handlers[capsule_id]:
            return False
        
        # Unregister handler
        del self.interaction_handlers[capsule_id][interaction_type]
        
        # Clean up empty handler dictionaries
        if not self.interaction_handlers[capsule_id]:
            del self.interaction_handlers[capsule_id]
        
        logger.debug(f"Unregistered {interaction_type} handler for capsule {capsule_id}")
        return True
    
    def register_event_listener(self, listener: callable) -> bool:
        """
        Register an event listener for all interaction events.
        
        Args:
            listener: Listener function
            
        Returns:
            Boolean indicating success
        """
        listener_id = id(listener)
        
        if listener_id not in self.event_listeners:
            self.event_listeners[listener_id] = listener
            logger.debug(f"Registered event listener {listener_id}")
            return True
        
        return False
    
    def unregister_event_listener(self, listener: callable) -> bool:
        """
        Unregister an event listener.
        
        Args:
            listener: Listener function to unregister
            
        Returns:
            Boolean indicating success
        """
        listener_id = id(listener)
        
        if listener_id in self.event_listeners:
            del self.event_listeners[listener_id]
            logger.debug(f"Unregistered event listener {listener_id}")
            return True
        
        return False
    
    def handle_interaction(
        self, 
        capsule_id: str, 
        interaction_type: str, 
        interaction_data: Dict
    ) -> bool:
        """
        Handle an interaction with a capsule.
        
        Args:
            capsule_id: Capsule ID the interaction is for
            interaction_type: Type of interaction
            interaction_data: Interaction data
            
        Returns:
            Boolean indicating success
        """
        # Verify capsule exists
        capsule_state = self.state_manager.get_capsule_state(capsule_id)
        if not capsule_state:
            logger.error(f"Capsule {capsule_id} not found")
            return False
        
        # Verify interaction type
        if not any(t.value == interaction_type for t in InteractionType):
            logger.error(f"Invalid interaction type: {interaction_type}")
            return False
        
        # Create interaction event
        event = {
            "capsule_id": capsule_id,
            "interaction_type": interaction_type,
            "interaction_data": interaction_data,
            "timestamp": time.time()
        }
        
        # Update interaction history
        self._update_interaction_history(capsule_id)
        
        # Notify event listeners
        self._notify_event_listeners(event)
        
        # Find and call appropriate handler
        handler = self._get_interaction_handler(capsule_id, interaction_type)
        
        try:
            handler(capsule_id, interaction_data)
            logger.debug(f"Handled {interaction_type} interaction for capsule {capsule_id}")
            return True
        except Exception as e:
            logger.error(f"Error handling {interaction_type} interaction for capsule {capsule_id}: {str(e)}")
            return False
    
    def _get_interaction_handler(self, capsule_id: str, interaction_type: str) -> callable:
        """
        Get the appropriate interaction handler for a capsule and interaction type.
        
        Args:
            capsule_id: Capsule ID to get handler for
            interaction_type: Type of interaction
            
        Returns:
            Handler function
        """
        # Check for capsule-specific handler
        if capsule_id in self.interaction_handlers and interaction_type in self.interaction_handlers[capsule_id]:
            return self.interaction_handlers[capsule_id][interaction_type]
        
        # Fall back to default handler
        return self.default_handlers.get(interaction_type, lambda *args: None)
    
    def _update_interaction_history(self, capsule_id: str) -> None:
        """
        Update interaction history with a new interaction.
        
        Args:
            capsule_id: Capsule ID that was interacted with
        """
        # Add to history
        self.interaction_history.append({
            "capsule_id": capsule_id,
            "timestamp": time.time()
        })
        
        # Limit history length
        if len(self.interaction_history) > 10:
            self.interaction_history.pop(0)
    
    def _notify_event_listeners(self, event: Dict) -> None:
        """
        Notify all event listeners of an interaction event.
        
        Args:
            event: Interaction event data
        """
        for listener in self.event_listeners.values():
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in event listener: {str(e)}")
    
    def set_focus(self, capsule_id: str) -> bool:
        """
        Set focus to a specific capsule.
        
        Args:
            capsule_id: Capsule ID to focus
            
        Returns:
            Boolean indicating success
        """
        # Verify capsule exists
        capsule_state = self.state_manager.get_capsule_state(capsule_id)
        if not capsule_state:
            logger.error(f"Capsule {capsule_id} not found")
            return False
        
        # Set focus
        previous_focus = self.focused_capsule_id
        self.focused_capsule_id = capsule_id
        
        # Create focus event
        event = {
            "capsule_id": capsule_id,
            "interaction_type": InteractionType.FOCUS.value,
            "interaction_data": {
                "previous_focus": previous_focus
            },
            "timestamp": time.time()
        }
        
        # Update interaction history
        self._update_interaction_history(capsule_id)
        
        # Notify event listeners
        self._notify_event_listeners(event)
        
        # Call focus handler
        handler = self._get_interaction_handler(capsule_id, InteractionType.FOCUS.value)
        
        try:
            handler(capsule_id, {"previous_focus": previous_focus})
            logger.debug(f"Set focus to capsule {capsule_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting focus to capsule {capsule_id}: {str(e)}")
            return False
    
    def clear_focus(self) -> bool:
        """
        Clear focus from current capsule.
        
        Returns:
            Boolean indicating success
        """
        if not self.focused_capsule_id:
            return False
        
        previous_focus = self.focused_capsule_id
        self.focused_capsule_id = None
        
        # Create focus event
        event = {
            "capsule_id": None,
            "interaction_type": InteractionType.FOCUS.value,
            "interaction_data": {
                "previous_focus": previous_focus
            },
            "timestamp": time.time()
        }
        
        # Notify event listeners
        self._notify_event_listeners(event)
        
        logger.debug(f"Cleared focus from capsule {previous_focus}")
        return True
    
    def get_focused_capsule(self) -> str:
        """
        Get the currently focused capsule.
        
        Returns:
            Focused capsule ID or None
        """
        return self.focused_capsule_id
    
    def get_interaction_history(self) -> List[Dict]:
        """
        Get recent interaction history.
        
        Returns:
            List of recent interactions
        """
        return self.interaction_history
    
    def get_gesture_thresholds(self) -> Dict:
        """
        Get current gesture thresholds.
        
        Returns:
            Dictionary of gesture thresholds
        """
        return self.gesture_thresholds
    
    def set_gesture_thresholds(self, thresholds: Dict) -> bool:
        """
        Set gesture thresholds.
        
        Args:
            thresholds: Dictionary of threshold values to set
            
        Returns:
            Boolean indicating success
        """
        # Update only provided thresholds
        for key, value in thresholds.items():
            if key in self.gesture_thresholds:
                self.gesture_thresholds[key] = value
        
        logger.debug(f"Updated gesture thresholds: {thresholds}")
        return True
    
    # Default interaction handlers
    
    def _default_tap_handler(self, capsule_id: str, data: Dict) -> None:
        """
        Default handler for tap interactions.
        
        Args:
            capsule_id: Capsule ID that was tapped
            data: Tap interaction data
        """
        # Set focus to tapped capsule
        self.set_focus(capsule_id)
        
        # Get capsule state
        capsule_state = self.state_manager.get_capsule_state(capsule_id)
        state = capsule_state.get("state")
        
        # Toggle between active and paused states
        if state == "active":
            self.state_manager.pause_capsule(capsule_id)
        elif state == "paused":
            self.state_manager.activate_capsule(capsule_id)
    
    def _default_double_tap_handler(self, capsule_id: str, data: Dict) -> None:
        """
        Default handler for double tap interactions.
        
        Args:
            capsule_id: Capsule ID that was double tapped
            data: Double tap interaction data
        """
        # Expand/collapse capsule
        # In a real implementation, this would toggle between expanded and collapsed views
        logger.debug(f"Double tap on capsule {capsule_id}")
    
    def _default_long_press_handler(self, capsule_id: str, data: Dict) -> None:
        """
        Default handler for long press interactions.
        
        Args:
            capsule_id: Capsule ID that was long pressed
            data: Long press interaction data
        """
        # Show context menu
        # In a real implementation, this would display a context menu
        logger.debug(f"Long press on capsule {capsule_id}")
    
    def _default_swipe_handler(self, capsule_id: str, data: Dict) -> None:
        """
        Default handler for swipe interactions.
        
        Args:
            capsule_id: Capsule ID that was swiped
            data: Swipe interaction data
        """
        direction = data.get("direction")
        
        if direction == SwipeDirection.UP.value:
            # Swipe up - suspend capsule
            self.state_manager.suspend_capsule(capsule_id)
        elif direction == SwipeDirection.DOWN.value:
            # Swipe down - activate capsule
            self.state_manager.activate_capsule(capsule_id)
        elif direction == SwipeDirection.LEFT.value:
            # Swipe left - previous state/view
            logger.debug(f"Swipe left on capsule {capsule_id}")
        elif direction == SwipeDirection.RIGHT.value:
            # Swipe right - next state/view
            logger.debug(f"Swipe right on capsule {capsule_id}")
    
    def _default_drag_handler(self, capsule_id: str, data: Dict) -> None:
        """
        Default handler for drag interactions.
        
        Args:
            capsule_id: Capsule ID that was dragged
            data: Drag interaction data
        """
        # Move capsule
        # In a real implementation, this would update the capsule position
        start_x = data.get("start_x", 0)
        start_y = data.get("start_y", 0)
        end_x = data.get("end_x", 0)
        end_y = data.get("end_y", 0)
        
        logger.debug(f"Drag capsule {capsule_id} from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    
    def _default_pinch_handler(self, capsule_id: str, data: Dict) -> None:
        """
        Default handler for pinch interactions.
        
        Args:
            capsule_id: Capsule ID that was pinched
            data: Pinch interaction data
        """
        # Resize capsule
        # In a real implementation, this would update the capsule size
        scale_factor = data.get("scale_factor", 1.0)
        
        logger.debug(f"Pinch capsule {capsule_id} with scale factor {scale_factor}")
    
    def _default_hover_handler(self, capsule_id: str, data: Dict) -> None:
        """
        Default handler for hover interactions.
        
        Args:
            capsule_id: Capsule ID that was hovered
            data: Hover interaction data
        """
        # Show tooltip or highlight
        # In a real implementation, this would display a tooltip or highlight
        logger.debug(f"Hover on capsule {capsule_id}")
    
    def _default_focus_handler(self, capsule_id: str, data: Dict) -> None:
        """
        Default handler for focus interactions.
        
        Args:
            capsule_id: Capsule ID that was focused
            data: Focus interaction data
        """
        # Highlight focused capsule
        # In a real implementation, this would highlight the focused capsule
        previous_focus = data.get("previous_focus")
        
        logger.debug(f"Focus on capsule {capsule_id} (previous: {previous_focus})")
    
    def _default_command_handler(self, capsule_id: str, data: Dict) -> None:
        """
        Default handler for command interactions.
        
        Args:
            capsule_id: Capsule ID that received the command
            data: Command interaction data
        """
        command = data.get("command", "").lower()
        
        # Handle common commands
        if command == "activate":
            self.state_manager.activate_capsule(capsule_id)
        elif command == "pause":
            self.state_manager.pause_capsule(capsule_id)
        elif command == "suspend":
            self.state_manager.suspend_capsule(capsule_id)
        elif command == "terminate":
            self.state_manager.terminate_capsule(capsule_id)
        elif command == "fork":
            self.state_manager.fork_capsule(capsule_id)
        else:
            logger.debug(f"Unknown command '{command}' for capsule {capsule_id}")
"""
