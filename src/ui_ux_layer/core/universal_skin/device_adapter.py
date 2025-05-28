"""
Device Adapter Module for the UI/UX Layer of Industriverse

This module provides device-specific adaptation capabilities for the UI/UX Layer,
enabling the Universal Skin to adapt seamlessly across different devices and form factors.

The Device Adapter is responsible for:
1. Detecting device capabilities and constraints
2. Adapting UI layouts and components to different screen sizes
3. Optimizing interactions for different input methods (touch, mouse, keyboard, voice)
4. Managing device-specific features and limitations
5. Providing consistent experience across heterogeneous device ecosystem

This module works closely with the Adaptive Layout Manager and other Universal Skin
components to provide a cohesive cross-device experience.
"""

import logging
import platform
import json
import re
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union, Tuple

from .adaptive_layout_manager import AdaptiveLayoutManager
from .interaction_mode_manager import InteractionModeManager

logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """Enumeration of device types."""
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    TABLET = "tablet"
    PHONE = "phone"
    WEARABLE = "wearable"
    AR_HEADSET = "ar_headset"
    VR_HEADSET = "vr_headset"
    INDUSTRIAL_PANEL = "industrial_panel"
    KIOSK = "kiosk"
    TV = "tv"
    UNKNOWN = "unknown"


class InputType(Enum):
    """Enumeration of input types."""
    TOUCH = "touch"
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    VOICE = "voice"
    GESTURE = "gesture"
    CONTROLLER = "controller"
    EYE_TRACKING = "eye_tracking"
    BRAIN_COMPUTER_INTERFACE = "brain_computer_interface"


class DeviceOrientation(Enum):
    """Enumeration of device orientations."""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    SQUARE = "square"
    DYNAMIC = "dynamic"


class DeviceAdapter:
    """
    Provides device-specific adaptation capabilities for the UI/UX Layer.
    
    This class is responsible for detecting device capabilities and constraints,
    adapting UI layouts and components to different screen sizes, and optimizing
    interactions for different input methods.
    """

    def __init__(
        self,
        adaptive_layout_manager: AdaptiveLayoutManager,
        interaction_mode_manager: InteractionModeManager
    ):
        """
        Initialize the DeviceAdapter.
        
        Args:
            adaptive_layout_manager: Manager for adaptive layouts
            interaction_mode_manager: Manager for interaction modes
        """
        self.adaptive_layout_manager = adaptive_layout_manager
        self.interaction_mode_manager = interaction_mode_manager
        
        # Initialize device tracking
        self.current_device_info = {}
        self.device_capabilities = {}
        self.device_constraints = {}
        self.device_preferences = {}
        self.device_history = {}
        
        # Initialize callbacks
        self.device_change_callbacks = []
        self.orientation_change_callbacks = []
        self.capability_change_callbacks = []
        
        # Initialize device detection
        self._initialize_device_detection()
        
        logger.info("DeviceAdapter initialized")

    def _initialize_device_detection(self):
        """Initialize device detection."""
        # Detect initial device information
        self.current_device_info = self._detect_device_info()
        
        # Set device capabilities based on detected device
        self._set_device_capabilities(self.current_device_info)
        
        # Set device constraints based on detected device
        self._set_device_constraints(self.current_device_info)
        
        logger.debug(f"Initial device detection: {self.current_device_info.get('type', 'unknown')}")

    def _detect_device_info(self) -> Dict[str, Any]:
        """
        Detect device information.
        
        Returns:
            Device information
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated detection methods
        
        device_info = {
            "user_agent": self._get_user_agent(),
            "platform": platform.system(),
            "screen_width": 1920,  # Default values
            "screen_height": 1080,
            "pixel_ratio": 1.0,
            "orientation": DeviceOrientation.LANDSCAPE.value,
            "type": DeviceType.DESKTOP.value,
            "primary_input": InputType.MOUSE.value,
            "secondary_inputs": [InputType.KEYBOARD.value],
            "connection_type": "unknown",
            "connection_speed": "unknown",
            "battery_level": None,
            "is_low_power_mode": False,
            "preferred_color_scheme": "light",
            "preferred_reduced_motion": False,
            "supports_touch": False,
            "supports_pointer": True,
            "supports_keyboard": True,
            "supports_voice": False,
            "supports_ar": False,
            "supports_vr": False,
            "supports_3d": False,
            "supports_haptic": False
        }
        
        # Detect device type from user agent
        user_agent = device_info["user_agent"].lower()
        
        if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
            device_info["type"] = DeviceType.PHONE.value
            device_info["screen_width"] = 375
            device_info["screen_height"] = 812
            device_info["orientation"] = DeviceOrientation.PORTRAIT.value
            device_info["primary_input"] = InputType.TOUCH.value
            device_info["secondary_inputs"] = [InputType.VOICE.value]
            device_info["supports_touch"] = True
            device_info["supports_pointer"] = False
            device_info["pixel_ratio"] = 2.0
        
        elif "ipad" in user_agent or "tablet" in user_agent:
            device_info["type"] = DeviceType.TABLET.value
            device_info["screen_width"] = 768
            device_info["screen_height"] = 1024
            device_info["orientation"] = DeviceOrientation.PORTRAIT.value
            device_info["primary_input"] = InputType.TOUCH.value
            device_info["secondary_inputs"] = [InputType.KEYBOARD.value]
            device_info["supports_touch"] = True
            device_info["pixel_ratio"] = 2.0
        
        elif "oculus" in user_agent or "vive" in user_agent or "windows mixed reality" in user_agent:
            device_info["type"] = DeviceType.VR_HEADSET.value
            device_info["screen_width"] = 2880
            device_info["screen_height"] = 1600
            device_info["orientation"] = DeviceOrientation.LANDSCAPE.value
            device_info["primary_input"] = InputType.CONTROLLER.value
            device_info["secondary_inputs"] = [InputType.GESTURE.value]
            device_info["supports_vr"] = True
            device_info["supports_3d"] = True
            device_info["pixel_ratio"] = 1.0
        
        elif "hololens" in user_agent or "magic leap" in user_agent:
            device_info["type"] = DeviceType.AR_HEADSET.value
            device_info["screen_width"] = 1280
            device_info["screen_height"] = 720
            device_info["orientation"] = DeviceOrientation.LANDSCAPE.value
            device_info["primary_input"] = InputType.GESTURE.value
            device_info["secondary_inputs"] = [InputType.VOICE.value]
            device_info["supports_ar"] = True
            device_info["supports_3d"] = True
            device_info["pixel_ratio"] = 1.0
        
        # Detect connection type and speed
        # This would use the Network Information API in a real implementation
        device_info["connection_type"] = "wifi"
        device_info["connection_speed"] = "high"
        
        return device_info

    def _get_user_agent(self) -> str:
        """
        Get user agent string.
        
        Returns:
            User agent string
        """
        # In a real implementation, this would get the actual user agent
        # For this implementation, we'll return a default value
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def _set_device_capabilities(self, device_info: Dict[str, Any]):
        """
        Set device capabilities based on device information.
        
        Args:
            device_info: Device information
        """
        device_type = device_info.get("type", DeviceType.UNKNOWN.value)
        
        # Set base capabilities for all devices
        self.device_capabilities = {
            "layouts": ["standard"],
            "interactions": [device_info.get("primary_input", InputType.MOUSE.value)],
            "animations": True,
            "transitions": True,
            "notifications": True,
            "offline_support": True,
            "background_processing": True,
            "multi_window": False,
            "picture_in_picture": False,
            "split_screen": False,
            "drag_and_drop": False,
            "file_system_access": False,
            "camera_access": False,
            "microphone_access": False,
            "location_access": False,
            "bluetooth_access": False,
            "usb_access": False,
            "nfc_access": False,
            "push_notifications": False,
            "background_sync": False,
            "web_share": False,
            "web_payments": False,
            "web_authentication": False,
            "web_bluetooth": False,
            "web_usb": False,
            "web_nfc": False,
            "web_serial": False,
            "web_hid": False,
            "web_midi": False,
            "web_xr": False
        }
        
        # Add secondary inputs
        for input_type in device_info.get("secondary_inputs", []):
            if input_type not in self.device_capabilities["interactions"]:
                self.device_capabilities["interactions"].append(input_type)
        
        # Set device-specific capabilities
        if device_type == DeviceType.DESKTOP.value:
            self.device_capabilities.update({
                "layouts": ["standard", "wide", "multi_column"],
                "multi_window": True,
                "split_screen": True,
                "drag_and_drop": True,
                "file_system_access": True,
                "picture_in_picture": True,
                "web_share": True,
                "web_payments": True,
                "web_authentication": True
            })
        
        elif device_type == DeviceType.LAPTOP.value:
            self.device_capabilities.update({
                "layouts": ["standard", "wide", "multi_column"],
                "multi_window": True,
                "split_screen": True,
                "drag_and_drop": True,
                "file_system_access": True,
                "picture_in_picture": True,
                "camera_access": True,
                "microphone_access": True,
                "location_access": True,
                "web_share": True,
                "web_payments": True,
                "web_authentication": True
            })
        
        elif device_type == DeviceType.TABLET.value:
            self.device_capabilities.update({
                "layouts": ["standard", "adaptive", "touch_optimized"],
                "split_screen": True,
                "drag_and_drop": True,
                "picture_in_picture": True,
                "camera_access": True,
                "microphone_access": True,
                "location_access": True,
                "push_notifications": True,
                "web_share": True,
                "web_payments": True,
                "web_authentication": True
            })
        
        elif device_type == DeviceType.PHONE.value:
            self.device_capabilities.update({
                "layouts": ["compact", "adaptive", "touch_optimized"],
                "camera_access": True,
                "microphone_access": True,
                "location_access": True,
                "push_notifications": True,
                "web_share": True,
                "web_payments": True,
                "web_authentication": True
            })
        
        elif device_type == DeviceType.WEARABLE.value:
            self.device_capabilities.update({
                "layouts": ["minimal", "adaptive"],
                "animations": False,
                "transitions": False,
                "background_processing": False,
                "location_access": True,
                "push_notifications": True
            })
        
        elif device_type == DeviceType.AR_HEADSET.value:
            self.device_capabilities.update({
                "layouts": ["spatial", "adaptive", "minimal"],
                "web_xr": True,
                "camera_access": True,
                "microphone_access": True,
                "location_access": True
            })
        
        elif device_type == DeviceType.VR_HEADSET.value:
            self.device_capabilities.update({
                "layouts": ["spatial", "adaptive", "immersive"],
                "web_xr": True,
                "microphone_access": True
            })
        
        elif device_type == DeviceType.INDUSTRIAL_PANEL.value:
            self.device_capabilities.update({
                "layouts": ["industrial", "touch_optimized", "standard"],
                "camera_access": True,
                "microphone_access": True,
                "location_access": True,
                "bluetooth_access": True,
                "usb_access": True,
                "nfc_access": True
            })
        
        # Update capabilities based on specific device features
        if device_info.get("supports_touch", False):
            if "touch_optimized" not in self.device_capabilities["layouts"]:
                self.device_capabilities["layouts"].append("touch_optimized")
        
        if device_info.get("supports_ar", False):
            self.device_capabilities["web_xr"] = True
            if "spatial" not in self.device_capabilities["layouts"]:
                self.device_capabilities["layouts"].append("spatial")
        
        if device_info.get("supports_vr", False):
            self.device_capabilities["web_xr"] = True
            if "immersive" not in self.device_capabilities["layouts"]:
                self.device_capabilities["layouts"].append("immersive")
        
        # Update interaction mode manager with capabilities
        self.interaction_mode_manager.update_available_modes(
            self.device_capabilities["interactions"]
        )
        
        # Update adaptive layout manager with capabilities
        self.adaptive_layout_manager.update_available_layouts(
            self.device_capabilities["layouts"]
        )

    def _set_device_constraints(self, device_info: Dict[str, Any]):
        """
        Set device constraints based on device information.
        
        Args:
            device_info: Device information
        """
        device_type = device_info.get("type", DeviceType.UNKNOWN.value)
        
        # Set base constraints for all devices
        self.device_constraints = {
            "max_concurrent_connections": 6,
            "max_asset_size": 5 * 1024 * 1024,  # 5MB
            "max_local_storage": 5 * 1024 * 1024,  # 5MB
            "max_session_storage": 5 * 1024 * 1024,  # 5MB
            "max_indexed_db": 50 * 1024 * 1024,  # 50MB
            "max_cache_storage": 50 * 1024 * 1024,  # 50MB
            "max_web_sql": 50 * 1024 * 1024,  # 50MB
            "max_file_system": 0,  # Not supported by default
            "max_memory_usage": 512 * 1024 * 1024,  # 512MB
            "max_cpu_usage": 0.5,  # 50% of CPU
            "max_battery_usage": 0.2,  # 20% of battery
            "max_network_usage": 50 * 1024 * 1024,  # 50MB
            "max_background_time": 30,  # 30 seconds
            "max_notification_frequency": 10,  # 10 per hour
            "min_tap_target_size": 44,  # 44px
            "min_font_size": 12,  # 12px
            "max_animation_duration": 5000,  # 5 seconds
            "max_transition_duration": 1000,  # 1 second
            "max_concurrent_animations": 5,
            "max_concurrent_audio": 3,
            "max_concurrent_video": 1,
            "max_video_resolution": "1080p",
            "max_audio_channels": 2,
            "max_audio_bitrate": 128,  # 128kbps
            "max_video_bitrate": 2000,  # 2Mbps
            "requires_user_gesture_for_media": True,
            "requires_user_gesture_for_popups": True,
            "requires_https_for_features": True
        }
        
        # Set device-specific constraints
        if device_type == DeviceType.DESKTOP.value:
            self.device_constraints.update({
                "max_concurrent_connections": 10,
                "max_asset_size": 20 * 1024 * 1024,  # 20MB
                "max_local_storage": 10 * 1024 * 1024,  # 10MB
                "max_session_storage": 10 * 1024 * 1024,  # 10MB
                "max_indexed_db": 100 * 1024 * 1024,  # 100MB
                "max_cache_storage": 100 * 1024 * 1024,  # 100MB
                "max_web_sql": 100 * 1024 * 1024,  # 100MB
                "max_file_system": 100 * 1024 * 1024,  # 100MB
                "max_memory_usage": 1024 * 1024 * 1024,  # 1GB
                "max_cpu_usage": 0.8,  # 80% of CPU
                "max_network_usage": 100 * 1024 * 1024,  # 100MB
                "min_tap_target_size": 24,  # 24px
                "max_concurrent_animations": 10,
                "max_concurrent_audio": 5,
                "max_concurrent_video": 3,
                "max_video_resolution": "4K",
                "max_audio_channels": 5.1,
                "max_audio_bitrate": 320,  # 320kbps
                "max_video_bitrate": 8000  # 8Mbps
            })
        
        elif device_type == DeviceType.LAPTOP.value:
            self.device_constraints.update({
                "max_concurrent_connections": 8,
                "max_asset_size": 15 * 1024 * 1024,  # 15MB
                "max_local_storage": 10 * 1024 * 1024,  # 10MB
                "max_session_storage": 10 * 1024 * 1024,  # 10MB
                "max_indexed_db": 100 * 1024 * 1024,  # 100MB
                "max_cache_storage": 100 * 1024 * 1024,  # 100MB
                "max_web_sql": 100 * 1024 * 1024,  # 100MB
                "max_file_system": 100 * 1024 * 1024,  # 100MB
                "max_memory_usage": 768 * 1024 * 1024,  # 768MB
                "max_cpu_usage": 0.7,  # 70% of CPU
                "max_battery_usage": 0.3,  # 30% of battery
                "max_network_usage": 75 * 1024 * 1024,  # 75MB
                "min_tap_target_size": 24,  # 24px
                "max_concurrent_animations": 8,
                "max_concurrent_audio": 4,
                "max_concurrent_video": 2,
                "max_video_resolution": "1080p",
                "max_audio_channels": 5.1,
                "max_audio_bitrate": 256,  # 256kbps
                "max_video_bitrate": 5000  # 5Mbps
            })
        
        elif device_type == DeviceType.TABLET.value:
            self.device_constraints.update({
                "max_concurrent_connections": 6,
                "max_asset_size": 10 * 1024 * 1024,  # 10MB
                "max_local_storage": 5 * 1024 * 1024,  # 5MB
                "max_session_storage": 5 * 1024 * 1024,  # 5MB
                "max_indexed_db": 50 * 1024 * 1024,  # 50MB
                "max_cache_storage": 50 * 1024 * 1024,  # 50MB
                "max_web_sql": 50 * 1024 * 1024,  # 50MB
                "max_file_system": 50 * 1024 * 1024,  # 50MB
                "max_memory_usage": 512 * 1024 * 1024,  # 512MB
                "max_cpu_usage": 0.6,  # 60% of CPU
                "max_battery_usage": 0.25,  # 25% of battery
                "max_network_usage": 50 * 1024 * 1024,  # 50MB
                "min_tap_target_size": 44,  # 44px
                "max_concurrent_animations": 5,
                "max_concurrent_audio": 3,
                "max_concurrent_video": 1,
                "max_video_resolution": "1080p",
                "max_audio_channels": 2,
                "max_audio_bitrate": 192,  # 192kbps
                "max_video_bitrate": 3000  # 3Mbps
            })
        
        elif device_type == DeviceType.PHONE.value:
            self.device_constraints.update({
                "max_concurrent_connections": 4,
                "max_asset_size": 5 * 1024 * 1024,  # 5MB
                "max_local_storage": 5 * 1024 * 1024,  # 5MB
                "max_session_storage": 5 * 1024 * 1024,  # 5MB
                "max_indexed_db": 20 * 1024 * 1024,  # 20MB
                "max_cache_storage": 20 * 1024 * 1024,  # 20MB
                "max_web_sql": 20 * 1024 * 1024,  # 20MB
                "max_file_system": 20 * 1024 * 1024,  # 20MB
                "max_memory_usage": 256 * 1024 * 1024,  # 256MB
                "max_cpu_usage": 0.5,  # 50% of CPU
                "max_battery_usage": 0.2,  # 20% of battery
                "max_network_usage": 20 * 1024 * 1024,  # 20MB
                "min_tap_target_size": 48,  # 48px
                "max_concurrent_animations": 3,
                "max_concurrent_audio": 2,
                "max_concurrent_video": 1,
                "max_video_resolution": "720p",
                "max_audio_channels": 2,
                "max_audio_bitrate": 128,  # 128kbps
                "max_video_bitrate": 1500  # 1.5Mbps
            })
        
        elif device_type == DeviceType.WEARABLE.value:
            self.device_constraints.update({
                "max_concurrent_connections": 2,
                "max_asset_size": 1 * 1024 * 1024,  # 1MB
                "max_local_storage": 1 * 1024 * 1024,  # 1MB
                "max_session_storage": 1 * 1024 * 1024,  # 1MB
                "max_indexed_db": 5 * 1024 * 1024,  # 5MB
                "max_cache_storage": 5 * 1024 * 1024,  # 5MB
                "max_web_sql": 5 * 1024 * 1024,  # 5MB
                "max_file_system": 0,  # Not supported
                "max_memory_usage": 64 * 1024 * 1024,  # 64MB
                "max_cpu_usage": 0.3,  # 30% of CPU
                "max_battery_usage": 0.1,  # 10% of battery
                "max_network_usage": 5 * 1024 * 1024,  # 5MB
                "min_tap_target_size": 48,  # 48px
                "min_font_size": 14,  # 14px
                "max_animation_duration": 2000,  # 2 seconds
                "max_transition_duration": 500,  # 0.5 seconds
                "max_concurrent_animations": 2,
                "max_concurrent_audio": 1,
                "max_concurrent_video": 0,  # No video
                "max_video_resolution": "none",
                "max_audio_channels": 1,
                "max_audio_bitrate": 64  # 64kbps
            })
        
        elif device_type in [DeviceType.AR_HEADSET.value, DeviceType.VR_HEADSET.value]:
            self.device_constraints.update({
                "max_concurrent_connections": 4,
                "max_asset_size": 20 * 1024 * 1024,  # 20MB
                "max_local_storage": 10 * 1024 * 1024,  # 10MB
                "max_session_storage": 10 * 1024 * 1024,  # 10MB
                "max_indexed_db": 100 * 1024 * 1024,  # 100MB
                "max_cache_storage": 100 * 1024 * 1024,  # 100MB
                "max_web_sql": 50 * 1024 * 1024,  # 50MB
                "max_file_system": 50 * 1024 * 1024,  # 50MB
                "max_memory_usage": 512 * 1024 * 1024,  # 512MB
                "max_cpu_usage": 0.7,  # 70% of CPU
                "max_battery_usage": 0.4,  # 40% of battery
                "max_network_usage": 50 * 1024 * 1024,  # 50MB
                "min_tap_target_size": 0.05,  # 0.05 radians
                "min_font_size": 16,  # 16px
                "max_animation_duration": 3000,  # 3 seconds
                "max_transition_duration": 1000,  # 1 second
                "max_concurrent_animations": 5,
                "max_concurrent_audio": 4,
                "max_concurrent_video": 1,
                "max_video_resolution": "1080p",
                "max_audio_channels": 5.1,
                "max_audio_bitrate": 192,  # 192kbps
                "max_video_bitrate": 3000  # 3Mbps
            })
        
        elif device_type == DeviceType.INDUSTRIAL_PANEL.value:
            self.device_constraints.update({
                "max_concurrent_connections": 6,
                "max_asset_size": 10 * 1024 * 1024,  # 10MB
                "max_local_storage": 10 * 1024 * 1024,  # 10MB
                "max_session_storage": 10 * 1024 * 1024,  # 10MB
                "max_indexed_db": 100 * 1024 * 1024,  # 100MB
                "max_cache_storage": 100 * 1024 * 1024,  # 100MB
                "max_web_sql": 100 * 1024 * 1024,  # 100MB
                "max_file_system": 100 * 1024 * 1024,  # 100MB
                "max_memory_usage": 512 * 1024 * 1024,  # 512MB
                "max_cpu_usage": 0.6,  # 60% of CPU
                "max_network_usage": 50 * 1024 * 1024,  # 50MB
                "min_tap_target_size": 48,  # 48px for gloved operation
                "min_font_size": 16,  # 16px for readability in industrial environments
                "max_concurrent_animations": 3,
                "max_concurrent_audio": 2,
                "max_concurrent_video": 1,
                "max_video_resolution": "720p",
                "max_audio_channels": 2,
                "max_audio_bitrate": 128,  # 128kbps
                "max_video_bitrate": 2000  # 2Mbps
            })
        
        # Adjust constraints based on connection type and speed
        connection_type = device_info.get("connection_type", "unknown")
        connection_speed = device_info.get("connection_speed", "unknown")
        
        if connection_type == "cellular":
            # Reduce network usage for cellular connections
            self.device_constraints["max_asset_size"] = min(self.device_constraints["max_asset_size"], 2 * 1024 * 1024)  # 2MB max
            self.device_constraints["max_network_usage"] = min(self.device_constraints["max_network_usage"], 10 * 1024 * 1024)  # 10MB max
            self.device_constraints["max_concurrent_connections"] = min(self.device_constraints["max_concurrent_connections"], 4)
            self.device_constraints["max_video_bitrate"] = min(self.device_constraints["max_video_bitrate"], 1000)  # 1Mbps max
            self.device_constraints["max_audio_bitrate"] = min(self.device_constraints["max_audio_bitrate"], 96)  # 96kbps max
        
        if connection_speed == "low":
            # Further reduce for low speed connections
            self.device_constraints["max_asset_size"] = min(self.device_constraints["max_asset_size"], 1 * 1024 * 1024)  # 1MB max
            self.device_constraints["max_network_usage"] = min(self.device_constraints["max_network_usage"], 5 * 1024 * 1024)  # 5MB max
            self.device_constraints["max_concurrent_connections"] = min(self.device_constraints["max_concurrent_connections"], 2)
            self.device_constraints["max_video_bitrate"] = min(self.device_constraints["max_video_bitrate"], 500)  # 500kbps max
            self.device_constraints["max_audio_bitrate"] = min(self.device_constraints["max_audio_bitrate"], 64)  # 64kbps max
            self.device_constraints["max_video_resolution"] = "480p"
        
        # Adjust constraints based on battery level
        battery_level = device_info.get("battery_level")
        is_low_power_mode = device_info.get("is_low_power_mode", False)
        
        if battery_level is not None and battery_level < 0.2 or is_low_power_mode:
            # Reduce resource usage for low battery
            self.device_constraints["max_cpu_usage"] = min(self.device_constraints["max_cpu_usage"], 0.3)  # 30% max
            self.device_constraints["max_concurrent_animations"] = min(self.device_constraints["max_concurrent_animations"], 2)
            self.device_constraints["max_animation_duration"] = min(self.device_constraints["max_animation_duration"], 2000)  # 2 seconds max
            self.device_constraints["max_concurrent_audio"] = min(self.device_constraints["max_concurrent_audio"], 1)
            self.device_constraints["max_concurrent_video"] = min(self.device_constraints["max_concurrent_video"], 1)
            self.device_constraints["max_video_bitrate"] = min(self.device_constraints["max_video_bitrate"], 1000)  # 1Mbps max
        
        # Adjust constraints based on accessibility preferences
        if device_info.get("preferred_reduced_motion", False):
            self.device_constraints["max_animation_duration"] = 0  # No animations
            self.device_constraints["max_transition_duration"] = 0  # No transitions
            self.device_constraints["max_concurrent_animations"] = 0
        
        # Update adaptive layout manager with constraints
        self.adaptive_layout_manager.update_layout_constraints(self.device_constraints)

    def detect_device_changes(self) -> bool:
        """
        Detect changes in device information.
        
        Returns:
            True if changes were detected, False otherwise
        """
        # Get current device info
        current_info = self._detect_device_info()
        
        # Check for changes
        changes_detected = False
        
        # Check for device type change
        if current_info.get("type") != self.current_device_info.get("type"):
            changes_detected = True
            logger.info(f"Device type changed from {self.current_device_info.get('type')} to {current_info.get('type')}")
        
        # Check for orientation change
        if current_info.get("orientation") != self.current_device_info.get("orientation"):
            changes_detected = True
            logger.info(f"Device orientation changed from {self.current_device_info.get('orientation')} to {current_info.get('orientation')}")
            
            # Call orientation change callbacks
            for callback in self.orientation_change_callbacks:
                try:
                    callback(current_info.get("orientation"))
                except Exception as e:
                    logger.error(f"Error in orientation change callback: {e}")
        
        # Check for screen size change
        if (current_info.get("screen_width") != self.current_device_info.get("screen_width") or
            current_info.get("screen_height") != self.current_device_info.get("screen_height")):
            changes_detected = True
            logger.info(f"Screen size changed from {self.current_device_info.get('screen_width')}x{self.current_device_info.get('screen_height')} to {current_info.get('screen_width')}x{current_info.get('screen_height')}")
        
        # Check for connection change
        if (current_info.get("connection_type") != self.current_device_info.get("connection_type") or
            current_info.get("connection_speed") != self.current_device_info.get("connection_speed")):
            changes_detected = True
            logger.info(f"Connection changed from {self.current_device_info.get('connection_type')}/{self.current_device_info.get('connection_speed')} to {current_info.get('connection_type')}/{current_info.get('connection_speed')}")
        
        # Check for battery change
        if (current_info.get("battery_level") is not None and
            self.current_device_info.get("battery_level") is not None and
            abs(current_info.get("battery_level") - self.current_device_info.get("battery_level")) > 0.1):
            changes_detected = True
            logger.info(f"Battery level changed from {self.current_device_info.get('battery_level')} to {current_info.get('battery_level')}")
        
        # Check for low power mode change
        if current_info.get("is_low_power_mode") != self.current_device_info.get("is_low_power_mode"):
            changes_detected = True
            logger.info(f"Low power mode changed from {self.current_device_info.get('is_low_power_mode')} to {current_info.get('is_low_power_mode')}")
        
        # If changes detected, update device info and capabilities
        if changes_detected:
            # Store previous device info in history
            device_id = self.current_device_info.get("id", str(len(self.device_history)))
            self.device_history[device_id] = self.current_device_info
            
            # Update current device info
            self.current_device_info = current_info
            
            # Update capabilities and constraints
            self._set_device_capabilities(current_info)
            self._set_device_constraints(current_info)
            
            # Call device change callbacks
            for callback in self.device_change_callbacks:
                try:
                    callback(current_info)
                except Exception as e:
                    logger.error(f"Error in device change callback: {e}")
            
            # Call capability change callbacks
            for callback in self.capability_change_callbacks:
                try:
                    callback(self.device_capabilities)
                except Exception as e:
                    logger.error(f"Error in capability change callback: {e}")
        
        return changes_detected

    def get_device_info(self) -> Dict[str, Any]:
        """
        Get current device information.
        
        Returns:
            Device information
        """
        return self.current_device_info

    def get_device_capabilities(self) -> Dict[str, Any]:
        """
        Get current device capabilities.
        
        Returns:
            Device capabilities
        """
        return self.device_capabilities

    def get_device_constraints(self) -> Dict[str, Any]:
        """
        Get current device constraints.
        
        Returns:
            Device constraints
        """
        return self.device_constraints

    def get_device_preferences(self) -> Dict[str, Any]:
        """
        Get current device preferences.
        
        Returns:
            Device preferences
        """
        return self.device_preferences

    def set_device_preference(self, key: str, value: Any) -> bool:
        """
        Set a device preference.
        
        Args:
            key: Preference key
            value: Preference value
            
        Returns:
            True if preference was set, False otherwise
        """
        self.device_preferences[key] = value
        logger.debug(f"Set device preference {key} to {value}")
        return True

    def get_device_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a device preference.
        
        Args:
            key: Preference key
            default: Default value if preference not found
            
        Returns:
            Preference value
        """
        return self.device_preferences.get(key, default)

    def register_device_change_callback(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Register a callback for device changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if registration was successful, False otherwise
        """
        if callback not in self.device_change_callbacks:
            self.device_change_callbacks.append(callback)
            logger.debug(f"Registered device change callback {callback}")
            return True
        
        return False

    def unregister_device_change_callback(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unregister a callback for device changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if callback in self.device_change_callbacks:
            self.device_change_callbacks.remove(callback)
            logger.debug(f"Unregistered device change callback {callback}")
            return True
        
        return False

    def register_orientation_change_callback(self, callback: Callable[[str], None]) -> bool:
        """
        Register a callback for orientation changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if registration was successful, False otherwise
        """
        if callback not in self.orientation_change_callbacks:
            self.orientation_change_callbacks.append(callback)
            logger.debug(f"Registered orientation change callback {callback}")
            return True
        
        return False

    def unregister_orientation_change_callback(self, callback: Callable[[str], None]) -> bool:
        """
        Unregister a callback for orientation changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if callback in self.orientation_change_callbacks:
            self.orientation_change_callbacks.remove(callback)
            logger.debug(f"Unregistered orientation change callback {callback}")
            return True
        
        return False

    def register_capability_change_callback(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Register a callback for capability changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if registration was successful, False otherwise
        """
        if callback not in self.capability_change_callbacks:
            self.capability_change_callbacks.append(callback)
            logger.debug(f"Registered capability change callback {callback}")
            return True
        
        return False

    def unregister_capability_change_callback(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unregister a callback for capability changes.
        
        Args:
            callback: Callback function
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if callback in self.capability_change_callbacks:
            self.capability_change_callbacks.remove(callback)
            logger.debug(f"Unregistered capability change callback {callback}")
            return True
        
        return False

    def is_feature_supported(self, feature: str) -> bool:
        """
        Check if a feature is supported by the current device.
        
        Args:
            feature: Feature to check
            
        Returns:
            True if feature is supported, False otherwise
        """
        # Check capabilities
        if feature in self.device_capabilities:
            return bool(self.device_capabilities[feature])
        
        # Check specific features
        if feature == "touch":
            return self.current_device_info.get("supports_touch", False)
        
        if feature == "pointer":
            return self.current_device_info.get("supports_pointer", False)
        
        if feature == "keyboard":
            return self.current_device_info.get("supports_keyboard", False)
        
        if feature == "voice":
            return self.current_device_info.get("supports_voice", False)
        
        if feature == "ar":
            return self.current_device_info.get("supports_ar", False)
        
        if feature == "vr":
            return self.current_device_info.get("supports_vr", False)
        
        if feature == "3d":
            return self.current_device_info.get("supports_3d", False)
        
        if feature == "haptic":
            return self.current_device_info.get("supports_haptic", False)
        
        # Check layout support
        if feature.startswith("layout_"):
            layout = feature[7:]  # Remove "layout_" prefix
            return layout in self.device_capabilities.get("layouts", [])
        
        # Check interaction support
        if feature.startswith("interaction_"):
            interaction = feature[12:]  # Remove "interaction_" prefix
            return interaction in self.device_capabilities.get("interactions", [])
        
        # Unknown feature
        logger.warning(f"Unknown feature: {feature}")
        return False

    def get_optimal_layout(self) -> str:
        """
        Get the optimal layout for the current device.
        
        Returns:
            Optimal layout name
        """
        return self.adaptive_layout_manager.get_optimal_layout(
            self.current_device_info,
            self.device_capabilities,
            self.device_constraints
        )

    def get_optimal_interaction_mode(self) -> str:
        """
        Get the optimal interaction mode for the current device.
        
        Returns:
            Optimal interaction mode name
        """
        return self.interaction_mode_manager.get_optimal_mode(
            self.current_device_info,
            self.device_capabilities,
            self.device_constraints
        )

    def adapt_component(
        self,
        component_type: str,
        component_id: str,
        component_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapt a component for the current device.
        
        Args:
            component_type: Type of component
            component_id: ID of the component
            component_data: Component data
            
        Returns:
            Adapted component data
        """
        # Get optimal layout and interaction mode
        optimal_layout = self.get_optimal_layout()
        optimal_interaction_mode = self.get_optimal_interaction_mode()
        
        # Create adapted component data
        adapted_data = component_data.copy()
        
        # Add device-specific adaptations
        adapted_data["device_adaptations"] = {
            "device_type": self.current_device_info.get("type", DeviceType.UNKNOWN.value),
            "layout": optimal_layout,
            "interaction_mode": optimal_interaction_mode,
            "screen_width": self.current_device_info.get("screen_width", 1920),
            "screen_height": self.current_device_info.get("screen_height", 1080),
            "pixel_ratio": self.current_device_info.get("pixel_ratio", 1.0),
            "orientation": self.current_device_info.get("orientation", DeviceOrientation.LANDSCAPE.value),
            "supports_touch": self.current_device_info.get("supports_touch", False),
            "supports_pointer": self.current_device_info.get("supports_pointer", True),
            "supports_keyboard": self.current_device_info.get("supports_keyboard", True),
            "supports_voice": self.current_device_info.get("supports_voice", False),
            "supports_ar": self.current_device_info.get("supports_ar", False),
            "supports_vr": self.current_device_info.get("supports_vr", False),
            "supports_3d": self.current_device_info.get("supports_3d", False),
            "supports_haptic": self.current_device_info.get("supports_haptic", False),
            "min_tap_target_size": self.device_constraints.get("min_tap_target_size", 44),
            "min_font_size": self.device_constraints.get("min_font_size", 12),
            "max_animation_duration": self.device_constraints.get("max_animation_duration", 5000),
            "max_transition_duration": self.device_constraints.get("max_transition_duration", 1000),
            "preferred_color_scheme": self.current_device_info.get("preferred_color_scheme", "light"),
            "preferred_reduced_motion": self.current_device_info.get("preferred_reduced_motion", False)
        }
        
        # Apply component-specific adaptations
        if component_type == "button":
            # Adapt button for device
            if self.current_device_info.get("supports_touch", False):
                # Increase tap target size for touch devices
                adapted_data["size"] = max(adapted_data.get("size", 44), self.device_constraints.get("min_tap_target_size", 44))
            
            # Adjust for reduced motion preference
            if self.current_device_info.get("preferred_reduced_motion", False):
                adapted_data["animation_duration"] = 0
                adapted_data["transition_duration"] = 0
        
        elif component_type == "text":
            # Adapt text for device
            adapted_data["font_size"] = max(adapted_data.get("font_size", 14), self.device_constraints.get("min_font_size", 12))
            
            # Adjust for device type
            if self.current_device_info.get("type") == DeviceType.WEARABLE.value:
                # Increase contrast for wearables
                adapted_data["contrast_ratio"] = max(adapted_data.get("contrast_ratio", 4.5), 7.0)
            
            elif self.current_device_info.get("type") == DeviceType.INDUSTRIAL_PANEL.value:
                # Increase size for industrial panels
                adapted_data["font_size"] = max(adapted_data.get("font_size", 14), 16)
        
        elif component_type == "image":
            # Adapt image for device
            if self.current_device_info.get("connection_type") == "cellular" or self.current_device_info.get("connection_speed") == "low":
                # Use lower resolution for slow connections
                adapted_data["resolution"] = "low"
            
            # Adjust for device pixel ratio
            adapted_data["pixel_ratio"] = self.current_device_info.get("pixel_ratio", 1.0)
        
        elif component_type == "video":
            # Adapt video for device
            if self.current_device_info.get("connection_type") == "cellular" or self.current_device_info.get("connection_speed") == "low":
                # Use lower quality for slow connections
                adapted_data["quality"] = "low"
                adapted_data["autoplay"] = False
            
            # Adjust for battery level
            if self.current_device_info.get("battery_level", 1.0) < 0.2 or self.current_device_info.get("is_low_power_mode", False):
                adapted_data["autoplay"] = False
            
            # Set max resolution based on constraints
            adapted_data["max_resolution"] = self.device_constraints.get("max_video_resolution", "1080p")
            
            # Set max bitrate based on constraints
            adapted_data["max_bitrate"] = self.device_constraints.get("max_video_bitrate", 2000)
        
        elif component_type == "audio":
            # Adapt audio for device
            if self.current_device_info.get("connection_type") == "cellular" or self.current_device_info.get("connection_speed") == "low":
                # Use lower quality for slow connections
                adapted_data["quality"] = "low"
                adapted_data["autoplay"] = False
            
            # Adjust for battery level
            if self.current_device_info.get("battery_level", 1.0) < 0.2 or self.current_device_info.get("is_low_power_mode", False):
                adapted_data["autoplay"] = False
            
            # Set max channels based on constraints
            adapted_data["max_channels"] = self.device_constraints.get("max_audio_channels", 2)
            
            # Set max bitrate based on constraints
            adapted_data["max_bitrate"] = self.device_constraints.get("max_audio_bitrate", 128)
        
        elif component_type == "layout":
            # Adapt layout for device
            adapted_data["layout_type"] = optimal_layout
            
            # Adjust for orientation
            adapted_data["orientation"] = self.current_device_info.get("orientation", DeviceOrientation.LANDSCAPE.value)
            
            # Adjust for screen size
            adapted_data["screen_width"] = self.current_device_info.get("screen_width", 1920)
            adapted_data["screen_height"] = self.current_device_info.get("screen_height", 1080)
        
        elif component_type == "interaction":
            # Adapt interaction for device
            adapted_data["interaction_mode"] = optimal_interaction_mode
            
            # Adjust for input types
            adapted_data["primary_input"] = self.current_device_info.get("primary_input", InputType.MOUSE.value)
            adapted_data["secondary_inputs"] = self.current_device_info.get("secondary_inputs", [])
        
        # Return adapted component data
        return adapted_data

    def get_device_history(self) -> Dict[str, Dict[str, Any]]:
        """
        Get device history.
        
        Returns:
            Device history
        """
        return self.device_history

    def clear_device_history(self) -> bool:
        """
        Clear device history.
        
        Returns:
            True if history was cleared, False otherwise
        """
        self.device_history = {}
        logger.debug("Cleared device history")
        return True

    def export_device_profile(self) -> Dict[str, Any]:
        """
        Export device profile.
        
        Returns:
            Device profile
        """
        return {
            "device_info": self.current_device_info,
            "device_capabilities": self.device_capabilities,
            "device_constraints": self.device_constraints,
            "device_preferences": self.device_preferences
        }

    def import_device_profile(self, profile: Dict[str, Any]) -> bool:
        """
        Import device profile.
        
        Args:
            profile: Device profile
            
        Returns:
            True if profile was imported, False otherwise
        """
        try:
            # Import device info
            if "device_info" in profile:
                self.current_device_info = profile["device_info"]
            
            # Import device capabilities
            if "device_capabilities" in profile:
                self.device_capabilities = profile["device_capabilities"]
                
                # Update interaction mode manager with capabilities
                self.interaction_mode_manager.update_available_modes(
                    self.device_capabilities.get("interactions", [])
                )
                
                # Update adaptive layout manager with capabilities
                self.adaptive_layout_manager.update_available_layouts(
                    self.device_capabilities.get("layouts", [])
                )
            
            # Import device constraints
            if "device_constraints" in profile:
                self.device_constraints = profile["device_constraints"]
                
                # Update adaptive layout manager with constraints
                self.adaptive_layout_manager.update_layout_constraints(self.device_constraints)
            
            # Import device preferences
            if "device_preferences" in profile:
                self.device_preferences = profile["device_preferences"]
            
            logger.info("Imported device profile")
            return True
        
        except Exception as e:
            logger.error(f"Error importing device profile: {e}")
            return False

    def simulate_device(self, device_type: DeviceType) -> bool:
        """
        Simulate a specific device type.
        
        Args:
            device_type: Device type to simulate
            
        Returns:
            True if simulation was successful, False otherwise
        """
        try:
            # Create simulated device info
            simulated_info = {
                "user_agent": self._get_user_agent(),
                "platform": platform.system(),
                "type": device_type.value
            }
            
            # Add device-specific properties
            if device_type == DeviceType.DESKTOP:
                simulated_info.update({
                    "screen_width": 1920,
                    "screen_height": 1080,
                    "pixel_ratio": 1.0,
                    "orientation": DeviceOrientation.LANDSCAPE.value,
                    "primary_input": InputType.MOUSE.value,
                    "secondary_inputs": [InputType.KEYBOARD.value],
                    "supports_touch": False,
                    "supports_pointer": True,
                    "supports_keyboard": True,
                    "supports_voice": False,
                    "supports_ar": False,
                    "supports_vr": False,
                    "supports_3d": False,
                    "supports_haptic": False
                })
            
            elif device_type == DeviceType.LAPTOP:
                simulated_info.update({
                    "screen_width": 1366,
                    "screen_height": 768,
                    "pixel_ratio": 1.0,
                    "orientation": DeviceOrientation.LANDSCAPE.value,
                    "primary_input": InputType.MOUSE.value,
                    "secondary_inputs": [InputType.KEYBOARD.value, InputType.TOUCH.value],
                    "supports_touch": True,
                    "supports_pointer": True,
                    "supports_keyboard": True,
                    "supports_voice": False,
                    "supports_ar": False,
                    "supports_vr": False,
                    "supports_3d": False,
                    "supports_haptic": False
                })
            
            elif device_type == DeviceType.TABLET:
                simulated_info.update({
                    "screen_width": 768,
                    "screen_height": 1024,
                    "pixel_ratio": 2.0,
                    "orientation": DeviceOrientation.PORTRAIT.value,
                    "primary_input": InputType.TOUCH.value,
                    "secondary_inputs": [InputType.KEYBOARD.value],
                    "supports_touch": True,
                    "supports_pointer": False,
                    "supports_keyboard": True,
                    "supports_voice": True,
                    "supports_ar": False,
                    "supports_vr": False,
                    "supports_3d": False,
                    "supports_haptic": False
                })
            
            elif device_type == DeviceType.PHONE:
                simulated_info.update({
                    "screen_width": 375,
                    "screen_height": 812,
                    "pixel_ratio": 3.0,
                    "orientation": DeviceOrientation.PORTRAIT.value,
                    "primary_input": InputType.TOUCH.value,
                    "secondary_inputs": [InputType.VOICE.value],
                    "supports_touch": True,
                    "supports_pointer": False,
                    "supports_keyboard": False,
                    "supports_voice": True,
                    "supports_ar": True,
                    "supports_vr": False,
                    "supports_3d": True,
                    "supports_haptic": True
                })
            
            elif device_type == DeviceType.WEARABLE:
                simulated_info.update({
                    "screen_width": 320,
                    "screen_height": 320,
                    "pixel_ratio": 2.0,
                    "orientation": DeviceOrientation.SQUARE.value,
                    "primary_input": InputType.TOUCH.value,
                    "secondary_inputs": [InputType.VOICE.value],
                    "supports_touch": True,
                    "supports_pointer": False,
                    "supports_keyboard": False,
                    "supports_voice": True,
                    "supports_ar": False,
                    "supports_vr": False,
                    "supports_3d": False,
                    "supports_haptic": True
                })
            
            elif device_type == DeviceType.AR_HEADSET:
                simulated_info.update({
                    "screen_width": 1280,
                    "screen_height": 720,
                    "pixel_ratio": 1.0,
                    "orientation": DeviceOrientation.LANDSCAPE.value,
                    "primary_input": InputType.GESTURE.value,
                    "secondary_inputs": [InputType.VOICE.value, InputType.EYE_TRACKING.value],
                    "supports_touch": False,
                    "supports_pointer": False,
                    "supports_keyboard": False,
                    "supports_voice": True,
                    "supports_ar": True,
                    "supports_vr": False,
                    "supports_3d": True,
                    "supports_haptic": False
                })
            
            elif device_type == DeviceType.VR_HEADSET:
                simulated_info.update({
                    "screen_width": 2880,
                    "screen_height": 1600,
                    "pixel_ratio": 1.0,
                    "orientation": DeviceOrientation.LANDSCAPE.value,
                    "primary_input": InputType.CONTROLLER.value,
                    "secondary_inputs": [InputType.GESTURE.value, InputType.VOICE.value],
                    "supports_touch": False,
                    "supports_pointer": False,
                    "supports_keyboard": False,
                    "supports_voice": True,
                    "supports_ar": False,
                    "supports_vr": True,
                    "supports_3d": True,
                    "supports_haptic": True
                })
            
            elif device_type == DeviceType.INDUSTRIAL_PANEL:
                simulated_info.update({
                    "screen_width": 1024,
                    "screen_height": 768,
                    "pixel_ratio": 1.0,
                    "orientation": DeviceOrientation.LANDSCAPE.value,
                    "primary_input": InputType.TOUCH.value,
                    "secondary_inputs": [],
                    "supports_touch": True,
                    "supports_pointer": False,
                    "supports_keyboard": False,
                    "supports_voice": False,
                    "supports_ar": False,
                    "supports_vr": False,
                    "supports_3d": False,
                    "supports_haptic": False
                })
            
            # Store previous device info in history
            device_id = self.current_device_info.get("id", str(len(self.device_history)))
            self.device_history[device_id] = self.current_device_info
            
            # Update current device info
            self.current_device_info = simulated_info
            
            # Update capabilities and constraints
            self._set_device_capabilities(simulated_info)
            self._set_device_constraints(simulated_info)
            
            # Call device change callbacks
            for callback in self.device_change_callbacks:
                try:
                    callback(simulated_info)
                except Exception as e:
                    logger.error(f"Error in device change callback: {e}")
            
            # Call capability change callbacks
            for callback in self.capability_change_callbacks:
                try:
                    callback(self.device_capabilities)
                except Exception as e:
                    logger.error(f"Error in capability change callback: {e}")
            
            logger.info(f"Simulating device: {device_type.value}")
            return True
        
        except Exception as e:
            logger.error(f"Error simulating device: {e}")
            return False
