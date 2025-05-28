"""
Interaction Mode Manager for Universal Skin Shell

This module manages interaction modes within the Universal Skin Shell
of the Industriverse UI/UX Layer. It implements adaptive interaction patterns
based on device capabilities, user preferences, and context.

The Interaction Mode Manager:
1. Defines and manages interaction modes (touch, mouse, keyboard, voice, gesture, etc.)
2. Adapts interaction patterns based on device capabilities and user preferences
3. Handles interaction mode transitions and fallbacks
4. Provides an API for interaction customization
5. Coordinates with the Context Engine for context-aware interaction adaptations

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
from ..components.gesture_recognition.gesture_recognition import GestureRecognition
from ..components.voice_interface.voice_interface import VoiceInterface
from ..components.haptic_feedback.haptic_feedback import HapticFeedback

# Configure logging
logger = logging.getLogger(__name__)

class InteractionMode(Enum):
    """Enumeration of interaction modes in Industriverse."""
    POINTER = "pointer"         # Mouse/trackpad pointer interaction
    TOUCH = "touch"             # Touch screen interaction
    KEYBOARD = "keyboard"       # Keyboard-focused interaction
    VOICE = "voice"             # Voice command interaction
    GESTURE = "gesture"         # Gesture-based interaction
    GAZE = "gaze"               # Eye tracking/gaze interaction
    HAPTIC = "haptic"           # Haptic/force feedback interaction
    MIXED = "mixed"             # Mixed-mode interaction (combination)

class AccessibilityProfile(Enum):
    """Enumeration of accessibility profiles."""
    STANDARD = "standard"       # Standard interaction profile
    MOTOR_IMPAIRED = "motor_impaired"  # For users with motor impairments
    VISION_IMPAIRED = "vision_impaired"  # For users with vision impairments
    HEARING_IMPAIRED = "hearing_impaired"  # For users with hearing impairments
    COGNITIVE = "cognitive"     # For users with cognitive impairments
    CUSTOM = "custom"           # Custom accessibility profile

class InteractionModeManager:
    """
    Manages interaction modes within the Universal Skin Shell.
    
    This class is responsible for implementing adaptive interaction patterns
    based on device capabilities, user preferences, and context.
    """
    
    def __init__(
        self, 
        context_engine: ContextAwarenessEngine,
        rendering_engine: RenderingEngine,
        gesture_recognition: Optional[GestureRecognition] = None,
        voice_interface: Optional[VoiceInterface] = None,
        haptic_feedback: Optional[HapticFeedback] = None
    ):
        """
        Initialize the Interaction Mode Manager.
        
        Args:
            context_engine: The Context Awareness Engine instance
            rendering_engine: The Rendering Engine instance
            gesture_recognition: Optional Gesture Recognition component
            voice_interface: Optional Voice Interface component
            haptic_feedback: Optional Haptic Feedback component
        """
        self.context_engine = context_engine
        self.rendering_engine = rendering_engine
        self.gesture_recognition = gesture_recognition
        self.voice_interface = voice_interface
        self.haptic_feedback = haptic_feedback
        
        # Interaction mode definitions
        self.interaction_mode_definitions = self._load_interaction_mode_definitions()
        
        # Accessibility profile definitions
        self.accessibility_profiles = self._load_accessibility_profiles()
        
        # Current active interaction mode
        self.active_interaction_mode = InteractionMode.POINTER.value
        
        # Current active accessibility profile
        self.active_accessibility_profile = AccessibilityProfile.STANDARD.value
        
        # Available interaction modes based on device capabilities
        self.available_interaction_modes = [InteractionMode.POINTER.value, InteractionMode.KEYBOARD.value]
        
        # Interaction mode transition history
        self.interaction_mode_history = []
        
        # Custom interaction mode settings
        self.custom_interaction_settings = {}
        
        # Register as context listener
        self.context_engine.register_context_listener(self._handle_context_change)
        
        logger.info("Interaction Mode Manager initialized")
    
    def _load_interaction_mode_definitions(self) -> Dict:
        """
        Load interaction mode definitions.
        
        Returns:
            Dictionary of interaction mode definitions
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard interaction modes inline
        
        return {
            InteractionMode.POINTER.value: {
                "name": "Pointer Interaction",
                "description": "Mouse/trackpad pointer interaction",
                "required_capabilities": ["pointer"],
                "interaction_settings": {
                    "click_threshold": 1,
                    "double_click_threshold": 500,  # ms
                    "hover_delay": 300,  # ms
                    "drag_threshold": 5,  # pixels
                    "scroll_sensitivity": 1.0
                },
                "component_settings": {
                    "button_size": "medium",
                    "interactive_area_padding": 0,
                    "tooltip_delay": 500,  # ms
                    "cursor_feedback": True
                },
                "fallback_mode": None
            },
            InteractionMode.TOUCH.value: {
                "name": "Touch Interaction",
                "description": "Touch screen interaction",
                "required_capabilities": ["touch"],
                "interaction_settings": {
                    "tap_threshold": 1,
                    "double_tap_threshold": 300,  # ms
                    "long_press_threshold": 500,  # ms
                    "swipe_threshold": 10,  # pixels
                    "pinch_threshold": 10,  # pixels
                    "multi_touch_enabled": True
                },
                "component_settings": {
                    "button_size": "large",
                    "interactive_area_padding": 10,
                    "tooltip_delay": 0,  # No hover on touch
                    "cursor_feedback": False
                },
                "fallback_mode": InteractionMode.POINTER.value
            },
            InteractionMode.KEYBOARD.value: {
                "name": "Keyboard Interaction",
                "description": "Keyboard-focused interaction",
                "required_capabilities": ["keyboard"],
                "interaction_settings": {
                    "key_repeat_delay": 500,  # ms
                    "key_repeat_rate": 50,  # ms
                    "navigation_keys": ["Tab", "Arrow", "Enter", "Escape"],
                    "shortcut_keys_enabled": True,
                    "focus_highlight": True
                },
                "component_settings": {
                    "focus_indicator_style": "outline",
                    "focus_indicator_color": "#0078d7",
                    "focus_indicator_width": 2,
                    "keyboard_shortcuts_visible": True
                },
                "fallback_mode": InteractionMode.POINTER.value
            },
            InteractionMode.VOICE.value: {
                "name": "Voice Interaction",
                "description": "Voice command interaction",
                "required_capabilities": ["microphone", "speech_recognition"],
                "interaction_settings": {
                    "command_prefix": "Hey Industriverse",
                    "command_timeout": 5000,  # ms
                    "confidence_threshold": 0.7,
                    "continuous_listening": False,
                    "feedback_audio": True
                },
                "component_settings": {
                    "voice_command_indicators": True,
                    "voice_feedback_visual": True,
                    "command_suggestions": True
                },
                "fallback_mode": InteractionMode.POINTER.value
            },
            InteractionMode.GESTURE.value: {
                "name": "Gesture Interaction",
                "description": "Gesture-based interaction",
                "required_capabilities": ["camera", "gesture_recognition"],
                "interaction_settings": {
                    "gesture_confidence_threshold": 0.6,
                    "gesture_hold_time": 300,  # ms
                    "gesture_cooldown": 500,  # ms
                    "tracking_smoothing": 0.3
                },
                "component_settings": {
                    "gesture_indicators": True,
                    "gesture_feedback_visual": True,
                    "gesture_suggestions": True
                },
                "fallback_mode": InteractionMode.POINTER.value
            },
            InteractionMode.GAZE.value: {
                "name": "Gaze Interaction",
                "description": "Eye tracking/gaze interaction",
                "required_capabilities": ["eye_tracking"],
                "interaction_settings": {
                    "gaze_dwell_time": 1000,  # ms
                    "gaze_confidence_threshold": 0.7,
                    "gaze_smoothing": 0.5,
                    "blink_detection": True,
                    "blink_action_threshold": 300  # ms
                },
                "component_settings": {
                    "gaze_indicators": True,
                    "gaze_feedback_visual": True,
                    "enlarged_interaction_areas": True
                },
                "fallback_mode": InteractionMode.POINTER.value
            },
            InteractionMode.HAPTIC.value: {
                "name": "Haptic Interaction",
                "description": "Haptic/force feedback interaction",
                "required_capabilities": ["haptic_feedback"],
                "interaction_settings": {
                    "haptic_intensity": 0.7,
                    "haptic_duration": 50,  # ms
                    "haptic_patterns_enabled": True,
                    "force_feedback_enabled": True
                },
                "component_settings": {
                    "haptic_indicators": True,
                    "haptic_feedback_visual": True
                },
                "fallback_mode": None  # Haptic is supplementary
            },
            InteractionMode.MIXED.value: {
                "name": "Mixed Interaction",
                "description": "Mixed-mode interaction (combination)",
                "required_capabilities": [],  # Depends on enabled modes
                "interaction_settings": {
                    "primary_mode": InteractionMode.POINTER.value,
                    "secondary_modes": [],
                    "mode_switching_automatic": True,
                    "mode_switching_threshold": 0.8
                },
                "component_settings": {
                    "multi_mode_indicators": True,
                    "mode_feedback_visual": True,
                    "adaptive_interface": True
                },
                "fallback_mode": InteractionMode.POINTER.value
            }
        }
    
    def _load_accessibility_profiles(self) -> Dict:
        """
        Load accessibility profile definitions.
        
        Returns:
            Dictionary of accessibility profile definitions
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard accessibility profiles inline
        
        return {
            AccessibilityProfile.STANDARD.value: {
                "name": "Standard Profile",
                "description": "Standard interaction profile",
                "interaction_settings": {},  # Uses default settings
                "component_settings": {}  # Uses default settings
            },
            AccessibilityProfile.MOTOR_IMPAIRED.value: {
                "name": "Motor Accessibility",
                "description": "For users with motor impairments",
                "interaction_settings": {
                    "click_threshold": 0.5,
                    "double_click_threshold": 800,  # ms
                    "hover_delay": 600,  # ms
                    "drag_threshold": 10,  # pixels
                    "tap_threshold": 0.5,
                    "long_press_threshold": 800,  # ms
                    "key_repeat_delay": 800,  # ms
                    "key_repeat_rate": 100  # ms
                },
                "component_settings": {
                    "button_size": "x-large",
                    "interactive_area_padding": 20,
                    "focus_indicator_width": 4,
                    "enlarged_interaction_areas": True
                },
                "preferred_modes": [
                    InteractionMode.VOICE.value,
                    InteractionMode.GAZE.value,
                    InteractionMode.POINTER.value
                ]
            },
            AccessibilityProfile.VISION_IMPAIRED.value: {
                "name": "Vision Accessibility",
                "description": "For users with vision impairments",
                "interaction_settings": {
                    "hover_delay": 600,  # ms
                    "feedback_audio": True,
                    "screen_reader_enabled": True,
                    "high_contrast_mode": True
                },
                "component_settings": {
                    "button_size": "x-large",
                    "focus_indicator_width": 4,
                    "focus_indicator_color": "#ffff00",
                    "text_size_multiplier": 1.5,
                    "icon_size_multiplier": 1.5
                },
                "preferred_modes": [
                    InteractionMode.VOICE.value,
                    InteractionMode.KEYBOARD.value,
                    InteractionMode.HAPTIC.value
                ]
            },
            AccessibilityProfile.HEARING_IMPAIRED.value: {
                "name": "Hearing Accessibility",
                "description": "For users with hearing impairments",
                "interaction_settings": {
                    "feedback_audio": False,
                    "visual_alerts_enhanced": True,
                    "captions_enabled": True
                },
                "component_settings": {
                    "visual_feedback_enhanced": True,
                    "haptic_feedback_enhanced": True,
                    "text_transcription_enabled": True
                },
                "preferred_modes": [
                    InteractionMode.POINTER.value,
                    InteractionMode.TOUCH.value,
                    InteractionMode.HAPTIC.value
                ]
            },
            AccessibilityProfile.COGNITIVE.value: {
                "name": "Cognitive Accessibility",
                "description": "For users with cognitive impairments",
                "interaction_settings": {
                    "interface_complexity": "simple",
                    "animation_speed": 0.5,
                    "timeout_multiplier": 2.0,
                    "error_tolerance": "high"
                },
                "component_settings": {
                    "simplified_interface": True,
                    "reduced_distractions": True,
                    "clear_labeling": True,
                    "consistent_navigation": True,
                    "step_by_step_guidance": True
                },
                "preferred_modes": [
                    InteractionMode.TOUCH.value,
                    InteractionMode.POINTER.value
                ]
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
            
            # Check for device capabilities changes
            if "capabilities" in device_data:
                capabilities = device_data["capabilities"]
                self._update_available_interaction_modes(capabilities)
            
            # Check for device type changes
            if "device_type" in device_data:
                device_type = device_data["device_type"]
                
                # Adapt interaction mode based on device type
                if device_type == "mobile" or device_type == "tablet":
                    self.switch_to_interaction_mode(InteractionMode.TOUCH.value)
                elif device_type == "desktop":
                    self.switch_to_interaction_mode(InteractionMode.POINTER.value)
                elif device_type == "ar" or device_type == "vr":
                    # For AR/VR, prefer gesture if available, otherwise mixed mode
                    if InteractionMode.GESTURE.value in self.available_interaction_modes:
                        self.switch_to_interaction_mode(InteractionMode.GESTURE.value)
                    else:
                        self.switch_to_interaction_mode(InteractionMode.MIXED.value)
        
        # Handle user context changes
        elif context_type == "user":
            user_data = event.get("data", {})
            
            # Check for accessibility profile changes
            if "accessibility_profile" in user_data:
                profile = user_data["accessibility_profile"]
                self.switch_to_accessibility_profile(profile)
            
            # Check for interaction preferences
            if "interaction_preferences" in user_data:
                preferences = user_data["interaction_preferences"]
                
                if "preferred_mode" in preferences:
                    preferred_mode = preferences["preferred_mode"]
                    
                    # Switch to preferred mode if available
                    if preferred_mode in self.available_interaction_modes:
                        self.switch_to_interaction_mode(preferred_mode)
        
        # Handle environment context changes
        elif context_type == "environment":
            env_data = event.get("data", {})
            
            # Adapt to noise level
            if "noise_level" in env_data:
                noise_level = env_data["noise_level"]
                
                # In noisy environments, avoid voice interaction
                if noise_level == "high" and self.active_interaction_mode == InteractionMode.VOICE.value:
                    # Fall back to pointer or touch
                    if InteractionMode.TOUCH.value in self.available_interaction_modes:
                        self.switch_to_interaction_mode(InteractionMode.TOUCH.value)
                    else:
                        self.switch_to_interaction_mode(InteractionMode.POINTER.value)
            
            # Adapt to lighting conditions
            if "lighting_condition" in env_data:
                lighting = env_data["lighting_condition"]
                
                # In low light, avoid gesture and gaze if possible
                if lighting == "dark":
                    if self.active_interaction_mode in [InteractionMode.GESTURE.value, InteractionMode.GAZE.value]:
                        # Fall back to voice if available, otherwise pointer
                        if InteractionMode.VOICE.value in self.available_interaction_modes:
                            self.switch_to_interaction_mode(InteractionMode.VOICE.value)
                        else:
                            self.switch_to_interaction_mode(InteractionMode.POINTER.value)
    
    def _update_available_interaction_modes(self, capabilities: List[str]) -> None:
        """
        Update available interaction modes based on device capabilities.
        
        Args:
            capabilities: List of device capabilities
        """
        available_modes = []
        
        # Check each interaction mode against capabilities
        for mode_id, mode_def in self.interaction_mode_definitions.items():
            required_capabilities = mode_def.get("required_capabilities", [])
            
            # If all required capabilities are available, add mode to available list
            if all(cap in capabilities for cap in required_capabilities):
                available_modes.append(mode_id)
        
        # Always include mixed mode if at least two modes are available
        if len(available_modes) >= 2 and InteractionMode.MIXED.value not in available_modes:
            available_modes.append(InteractionMode.MIXED.value)
        
        # Update available modes
        self.available_interaction_modes = available_modes
        
        logger.info(f"Updated available interaction modes: {available_modes}")
        
        # If current mode is no longer available, switch to fallback
        if self.active_interaction_mode not in available_modes:
            # Find a fallback mode
            fallback = self.interaction_mode_definitions.get(self.active_interaction_mode, {}).get("fallback_mode")
            
            # If fallback is not available or not specified, use first available mode
            if not fallback or fallback not in available_modes:
                fallback = available_modes[0] if available_modes else InteractionMode.POINTER.value
            
            # Switch to fallback mode
            self.switch_to_interaction_mode(fallback)
    
    def switch_to_interaction_mode(self, mode: str) -> bool:
        """
        Switch to a different interaction mode.
        
        Args:
            mode: The interaction mode to switch to
            
        Returns:
            Boolean indicating success
        """
        # Verify mode exists
        if mode not in self.interaction_mode_definitions:
            logger.error(f"Interaction mode {mode} not found in definitions")
            return False
        
        # Verify mode is available
        if mode not in self.available_interaction_modes:
            logger.error(f"Interaction mode {mode} is not available with current device capabilities")
            return False
        
        # Record previous mode in history
        if self.active_interaction_mode:
            self.interaction_mode_history.append({
                "mode": self.active_interaction_mode,
                "timestamp": time.time()
            })
            
            # Limit history length
            if len(self.interaction_mode_history) > 10:
                self.interaction_mode_history.pop(0)
        
        # Set new active mode
        self.active_interaction_mode = mode
        
        # Get mode definition
        mode_def = self.interaction_mode_definitions[mode]
        
        # Apply interaction settings
        interaction_settings = mode_def.get("interaction_settings", {})
        self._apply_interaction_settings(interaction_settings)
        
        # Apply component settings
        component_settings = mode_def.get("component_settings", {})
        self._apply_component_settings(component_settings)
        
        # Apply accessibility overrides if needed
        if self.active_accessibility_profile != AccessibilityProfile.STANDARD.value:
            self._apply_accessibility_overrides()
        
        # Enable/disable specific interaction components
        self._configure_interaction_components(mode)
        
        logger.info(f"Switched to interaction mode: {mode_def.get('name', mode)}")
        return True
    
    def switch_to_accessibility_profile(self, profile: str) -> bool:
        """
        Switch to a different accessibility profile.
        
        Args:
            profile: The accessibility profile to switch to
            
        Returns:
            Boolean indicating success
        """
        # Verify profile exists
        if profile not in self.accessibility_profiles and profile != AccessibilityProfile.CUSTOM.value:
            logger.error(f"Accessibility profile {profile} not found in definitions")
            return False
        
        # Set new active profile
        self.active_accessibility_profile = profile
        
        # Get profile definition
        if profile == AccessibilityProfile.CUSTOM.value:
            # Use custom profile if available
            profile_def = self.custom_interaction_settings.get("accessibility_profile", {
                "name": "Custom Accessibility",
                "description": "Custom user-defined accessibility settings",
                "interaction_settings": {},
                "component_settings": {}
            })
        else:
            profile_def = self.accessibility_profiles[profile]
        
        # Check for preferred interaction modes
        preferred_modes = profile_def.get("preferred_modes", [])
        
        if preferred_modes:
            # Find first preferred mode that is available
            for preferred_mode in preferred_modes:
                if preferred_mode in self.available_interaction_modes:
                    # Switch to preferred mode
                    self.switch_to_interaction_mode(preferred_mode)
                    break
        
        # Apply accessibility settings
        interaction_settings = profile_def.get("interaction_settings", {})
        component_settings = profile_def.get("component_settings", {})
        
        # Apply settings as overrides to current interaction mode
        self._apply_interaction_settings(interaction_settings)
        self._apply_component_settings(component_settings)
        
        logger.info(f"Switched to accessibility profile: {profile_def.get('name', profile)}")
        return True
    
    def _apply_interaction_settings(self, settings: Dict) -> None:
        """
        Apply interaction settings.
        
        Args:
            settings: Interaction settings to apply
        """
        # In a real implementation, this would update various interaction parameters
        # For now, we'll just log the intent
        logger.debug(f"Applying interaction settings: {settings}")
        
        # Apply settings to specific interaction components
        
        # Gesture recognition settings
        if self.gesture_recognition and "gesture_confidence_threshold" in settings:
            self.gesture_recognition.set_confidence_threshold(settings["gesture_confidence_threshold"])
        
        # Voice interface settings
        if self.voice_interface:
            if "command_prefix" in settings:
                self.voice_interface.set_command_prefix(settings["command_prefix"])
            if "confidence_threshold" in settings:
                self.voice_interface.set_confidence_threshold(settings["confidence_threshold"])
            if "continuous_listening" in settings:
                self.voice_interface.set_continuous_listening(settings["continuous_listening"])
        
        # Haptic feedback settings
        if self.haptic_feedback:
            if "haptic_intensity" in settings:
                self.haptic_feedback.set_intensity(settings["haptic_intensity"])
            if "haptic_duration" in settings:
                self.haptic_feedback.set_duration(settings["haptic_duration"])
            if "haptic_patterns_enabled" in settings:
                self.haptic_feedback.set_patterns_enabled(settings["haptic_patterns_enabled"])
    
    def _apply_component_settings(self, settings: Dict) -> None:
        """
        Apply component settings.
        
        Args:
            settings: Component settings to apply
        """
        # In a real implementation, this would update the rendering engine
        # For now, we'll just log the intent
        logger.debug(f"Applying component settings: {settings}")
        
        # Update rendering engine
        for setting, value in settings.items():
            self.rendering_engine.set_component_setting(setting, value)
    
    def _apply_accessibility_overrides(self) -> None:
        """Apply accessibility profile overrides to current interaction mode."""
        # Get current accessibility profile
        if not self.active_accessibility_profile:
            return
        
        # Get profile definition
        if self.active_accessibility_profile == AccessibilityProfile.CUSTOM.value:
            profile_def = self.custom_interaction_settings.get("accessibility_profile", {})
        else:
            profile_def = self.accessibility_profiles.get(self.active_accessibility_profile, {})
        
        # Apply interaction settings as overrides
        interaction_settings = profile_def.get("interaction_settings", {})
        if interaction_settings:
            self._apply_interaction_settings(interaction_settings)
        
        # Apply component settings as overrides
        component_settings = profile_def.get("component_settings", {})
        if component_settings:
            self._apply_component_settings(component_settings)
    
    def _configure_interaction_components(self, mode: str) -> None:
        """
        Configure interaction components for specific mode.
        
        Args:
            mode: Interaction mode to configure for
        """
        # Enable/disable specific interaction components based on mode
        
        # Gesture recognition
        if self.gesture_recognition:
            enable_gesture = mode in [
                InteractionMode.GESTURE.value,
                InteractionMode.MIXED.value
            ]
            self.gesture_recognition.set_enabled(enable_gesture)
        
        # Voice interface
        if self.voice_interface:
            enable_voice = mode in [
                InteractionMode.VOICE.value,
                InteractionMode.MIXED.value
            ]
            self.voice_interface.set_enabled(enable_voice)
        
        # Haptic feedback
        if self.haptic_feedback:
            enable_haptic = mode in [
                InteractionMode.HAPTIC.value,
                InteractionMode.TOUCH.value,
                InteractionMode.MIXED.value
            ]
            self.haptic_feedback.set_enabled(enable_haptic)
    
    def get_active_interaction_mode(self) -> str:
        """
        Get the currently active interaction mode.
        
        Returns:
            Active interaction mode ID
        """
        return self.active_interaction_mode
    
    def get_active_accessibility_profile(self) -> str:
        """
        Get the currently active accessibility profile.
        
        Returns:
            Active accessibility profile ID
        """
        return self.active_accessibility_profile
    
    def get_available_interaction_modes(self) -> List[Dict]:
        """
        Get available interaction modes.
        
        Returns:
            List of available interaction mode information
        """
        modes = []
        
        for mode_id in self.available_interaction_modes:
            mode_def = self.interaction_mode_definitions.get(mode_id, {})
            modes.append({
                "id": mode_id,
                "name": mode_def.get("name", mode_id),
                "description": mode_def.get("description", "")
            })
        
        return modes
    
    def get_available_accessibility_profiles(self) -> List[Dict]:
        """
        Get available accessibility profiles.
        
        Returns:
            List of available accessibility profile information
        """
        profiles = []
        
        for profile_id, profile_def in self.accessibility_profiles.items():
            profiles.append({
                "id": profile_id,
                "name": profile_def.get("name", profile_id),
                "description": profile_def.get("description", "")
            })
        
        # Add custom profile if defined
        if "accessibility_profile" in self.custom_interaction_settings:
            custom_def = self.custom_interaction_settings["accessibility_profile"]
            profiles.append({
                "id": AccessibilityProfile.CUSTOM.value,
                "name": custom_def.get("name", "Custom Accessibility"),
                "description": custom_def.get("description", "Custom user-defined accessibility settings")
            })
        
        return profiles
    
    def create_custom_accessibility_profile(self, profile_definition: Dict) -> bool:
        """
        Create or update a custom accessibility profile.
        
        Args:
            profile_definition: Custom profile definition
            
        Returns:
            Boolean indicating success
        """
        # Validate required fields
        required_fields = ["name", "interaction_settings", "component_settings"]
        for field in required_fields:
            if field not in profile_definition:
                logger.error(f"Missing required field in custom profile definition: {field}")
                return False
        
        # Set custom profile
        self.custom_interaction_settings["accessibility_profile"] = profile_definition
        
        logger.info(f"Created custom accessibility profile: {profile_definition.get('name')}")
        return True
    
    def get_interaction_mode_definition(self, mode: str) -> Dict:
        """
        Get interaction mode definition.
        
        Args:
            mode: Interaction mode ID to get definition for
            
        Returns:
            Interaction mode definition dictionary
        """
        return self.interaction_mode_definitions.get(mode, {})
    
    def get_accessibility_profile_definition(self, profile: str) -> Dict:
        """
        Get accessibility profile definition.
        
        Args:
            profile: Accessibility profile ID to get definition for
            
        Returns:
            Accessibility profile definition dictionary
        """
        if profile == AccessibilityProfile.CUSTOM.value:
            return self.custom_interaction_settings.get("accessibility_profile", {})
        else:
            return self.accessibility_profiles.get(profile, {})
    
    def update_interaction_setting(self, setting: str, value: Any) -> bool:
        """
        Update a specific interaction setting.
        
        Args:
            setting: Setting name to update
            value: New setting value
            
        Returns:
            Boolean indicating success
        """
        # Get current mode definition
        mode_def = self.interaction_mode_definitions.get(self.active_interaction_mode, {})
        
        # Get current interaction settings
        interaction_settings = mode_def.get("interaction_settings", {}).copy()
        
        # Update setting
        interaction_settings[setting] = value
        
        # Apply updated settings
        self._apply_interaction_settings({setting: value})
        
        logger.debug(f"Updated interaction setting: {setting}={value}")
        return True
    
    def update_component_setting(self, setting: str, value: Any) -> bool:
        """
        Update a specific component setting.
        
        Args:
            setting: Setting name to update
            value: New setting value
            
        Returns:
            Boolean indicating success
        """
        # Get current mode definition
        mode_def = self.interaction_mode_definitions.get(self.active_interaction_mode, {})
        
        # Get current component settings
        component_settings = mode_def.get("component_settings", {}).copy()
        
        # Update setting
        component_settings[setting] = value
        
        # Apply updated settings
        self._apply_component_settings({setting: value})
        
        logger.debug(f"Updated component setting: {setting}={value}")
        return True
    
    def adapt_to_context(self, context_data: Dict) -> None:
        """
        Adapt interaction mode based on context data.
        
        Args:
            context_data: Context data to adapt to
        """
        # This method is called directly when needed, in addition to
        # the automatic adaptations from context change events
        
        # Check for device capabilities
        device_context = context_data.get("device", {})
        if "capabilities" in device_context:
            capabilities = device_context["capabilities"]
            self._update_available_interaction_modes(capabilities)
        
        # Check for user accessibility needs
        user_context = context_data.get("user", {})
        if "accessibility_profile" in user_context:
            profile = user_context["accessibility_profile"]
            if profile != self.active_accessibility_profile:
                self.switch_to_accessibility_profile(profile)
        
        # Check for environment factors
        environment_context = context_data.get("environment", {})
        
        # In public environments, prefer non-voice interaction
        if "privacy_level" in environment_context:
            privacy = environment_context["privacy_level"]
            
            if privacy == "public" and self.active_interaction_mode == InteractionMode.VOICE.value:
                # Switch to touch if available, otherwise pointer
                if InteractionMode.TOUCH.value in self.available_interaction_modes:
                    self.switch_to_interaction_mode(InteractionMode.TOUCH.value)
                else:
                    self.switch_to_interaction_mode(InteractionMode.POINTER.value)
"""
