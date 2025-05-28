"""
Native Frontend Core for the Industriverse UI/UX Layer.

This module provides the core functionality for native frontends across different platforms,
enabling consistent implementation of the Universal Skin concept and Agent Capsules.

Author: Manus
"""

import logging
import json
import time
import threading
import queue
from typing import Dict, List, Optional, Any, Callable, Union, Set
from enum import Enum
from dataclasses import dataclass, field

class PlatformType(Enum):
    """Enumeration of supported platform types."""
    IOS = "ios"
    ANDROID = "android"
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    WEB = "web"
    AR = "ar"
    VR = "vr"
    EMBEDDED = "embedded"

class DeviceType(Enum):
    """Enumeration of supported device types."""
    PHONE = "phone"
    TABLET = "tablet"
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    WEARABLE = "wearable"
    HEADSET = "headset"
    INDUSTRIAL = "industrial"
    EMBEDDED = "embedded"
    OTHER = "other"

class InputType(Enum):
    """Enumeration of supported input types."""
    TOUCH = "touch"
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    VOICE = "voice"
    GESTURE = "gesture"
    CONTROLLER = "controller"
    GAZE = "gaze"
    HAPTIC = "haptic"
    OTHER = "other"

@dataclass
class DeviceCapabilities:
    """Data class representing device capabilities."""
    platform: PlatformType
    device_type: DeviceType
    input_types: List[InputType]
    screen_width: int
    screen_height: int
    pixel_ratio: float
    supports_touch: bool
    supports_haptic: bool
    supports_ar: bool
    supports_vr: bool
    supports_voice: bool
    supports_gesture: bool
    supports_biometric: bool
    additional_capabilities: Dict[str, Any] = field(default_factory=dict)

class NativeFrontendCore:
    """
    Provides core functionality for native frontends across different platforms.
    
    This class provides:
    - Platform detection and adaptation
    - Device capability detection
    - Universal Skin implementation
    - Capsule Framework integration
    - Cross-platform event handling
    - Native API integration
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Native Frontend Core.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.event_handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self.device_capabilities: Optional[DeviceCapabilities] = None
        self.platform_adapters: Dict[PlatformType, Any] = {}
        self.running = False
        self.worker_thread = None
        self.event_queue = queue.Queue()
        
        # Initialize from config if provided
        if config:
            pass
            
        self.logger.info("Native Frontend Core initialized")
        
    def start(self) -> bool:
        """
        Start the Native Frontend Core.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.logger.warning("Native Frontend Core already running")
            return False
            
        self.running = True
        self.worker_thread = threading.Thread(target=self._event_worker, daemon=True)
        self.worker_thread.start()
        
        self.logger.info("Native Frontend Core started")
        return True
        
    def stop(self) -> bool:
        """
        Stop the Native Frontend Core.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.running:
            self.logger.warning("Native Frontend Core not running")
            return False
            
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            
        self.logger.info("Native Frontend Core stopped")
        return True
        
    def _event_worker(self) -> None:
        """
        Worker thread for processing events.
        """
        self.logger.info("Event worker thread started")
        
        while self.running:
            try:
                event_data = self.event_queue.get(timeout=1.0)
                self._process_event(event_data)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
                
        self.logger.info("Event worker thread stopped")
        
    def _process_event(self, event_data: Dict[str, Any]) -> None:
        """
        Process event data.
        
        Args:
            event_data: Event data to process
        """
        event_type = event_data.get("type")
        if not event_type:
            self.logger.warning("Event data missing type")
            return
            
        # Notify event handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {e}")
                    
        # Notify wildcard handlers
        if "*" in self.event_handlers:
            for handler in self.event_handlers["*"]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.logger.error(f"Error in wildcard event handler: {e}")
                    
    def detect_device_capabilities(self) -> DeviceCapabilities:
        """
        Detect device capabilities.
        
        Returns:
            Device capabilities
        """
        # This is a placeholder implementation that should be overridden by platform-specific adapters
        capabilities = DeviceCapabilities(
            platform=PlatformType.WEB,
            device_type=DeviceType.DESKTOP,
            input_types=[InputType.MOUSE, InputType.KEYBOARD],
            screen_width=1920,
            screen_height=1080,
            pixel_ratio=1.0,
            supports_touch=False,
            supports_haptic=False,
            supports_ar=False,
            supports_vr=False,
            supports_voice=False,
            supports_gesture=False,
            supports_biometric=False
        )
        
        self.device_capabilities = capabilities
        return capabilities
        
    def register_platform_adapter(self, platform: PlatformType, adapter: Any) -> bool:
        """
        Register a platform adapter.
        
        Args:
            platform: Platform type
            adapter: Platform adapter
            
        Returns:
            True if the adapter was registered, False otherwise
        """
        if platform in self.platform_adapters:
            self.logger.warning(f"Platform adapter for {platform.value} already registered")
            return False
            
        self.platform_adapters[platform] = adapter
        self.logger.debug(f"Registered platform adapter for {platform.value}")
        
        return True
        
    def get_platform_adapter(self, platform: PlatformType) -> Optional[Any]:
        """
        Get a platform adapter.
        
        Args:
            platform: Platform type
            
        Returns:
            Platform adapter, or None if not found
        """
        return self.platform_adapters.get(platform)
        
    def register_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Register an event handler.
        
        Args:
            event_type: Event type to handle, or "*" for all events
            handler: Handler function
            
        Returns:
            True if the handler was registered, False otherwise
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
            
        self.event_handlers[event_type].append(handler)
        self.logger.debug(f"Registered event handler for {event_type}")
        
        return True
        
    def unregister_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unregister an event handler.
        
        Args:
            event_type: Event type the handler was registered for, or "*" for all events
            handler: Handler function to unregister
            
        Returns:
            True if the handler was unregistered, False otherwise
        """
        if event_type not in self.event_handlers:
            return False
            
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            self.logger.debug(f"Unregistered event handler for {event_type}")
            
            # Clean up empty handler lists
            if not self.event_handlers[event_type]:
                del self.event_handlers[event_type]
                
            return True
            
        return False
        
    def dispatch_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event.
        
        Args:
            event_type: Event type
            event_data: Event data
        """
        # Add event type to data if not present
        if "type" not in event_data:
            event_data["type"] = event_type
            
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = time.time()
            
        # Queue for processing
        self.event_queue.put(event_data)
        
    def get_device_capabilities(self) -> Optional[DeviceCapabilities]:
        """
        Get device capabilities.
        
        Returns:
            Device capabilities, or None if not detected
        """
        if self.device_capabilities is None:
            self.detect_device_capabilities()
            
        return self.device_capabilities
        
    def is_platform_supported(self, platform: PlatformType) -> bool:
        """
        Check if a platform is supported.
        
        Args:
            platform: Platform type
            
        Returns:
            True if the platform is supported, False otherwise
        """
        if self.device_capabilities is None:
            self.detect_device_capabilities()
            
        return self.device_capabilities.platform == platform
        
    def is_device_type_supported(self, device_type: DeviceType) -> bool:
        """
        Check if a device type is supported.
        
        Args:
            device_type: Device type
            
        Returns:
            True if the device type is supported, False otherwise
        """
        if self.device_capabilities is None:
            self.detect_device_capabilities()
            
        return self.device_capabilities.device_type == device_type
        
    def is_input_type_supported(self, input_type: InputType) -> bool:
        """
        Check if an input type is supported.
        
        Args:
            input_type: Input type
            
        Returns:
            True if the input type is supported, False otherwise
        """
        if self.device_capabilities is None:
            self.detect_device_capabilities()
            
        return input_type in self.device_capabilities.input_types
        
    def get_screen_dimensions(self) -> tuple[int, int]:
        """
        Get screen dimensions.
        
        Returns:
            Tuple of (width, height)
        """
        if self.device_capabilities is None:
            self.detect_device_capabilities()
            
        return (self.device_capabilities.screen_width, self.device_capabilities.screen_height)
        
    def get_pixel_ratio(self) -> float:
        """
        Get pixel ratio.
        
        Returns:
            Pixel ratio
        """
        if self.device_capabilities is None:
            self.detect_device_capabilities()
            
        return self.device_capabilities.pixel_ratio
        
    def supports_feature(self, feature: str) -> bool:
        """
        Check if a feature is supported.
        
        Args:
            feature: Feature name
            
        Returns:
            True if the feature is supported, False otherwise
        """
        if self.device_capabilities is None:
            self.detect_device_capabilities()
            
        # Check built-in features
        if feature == "touch":
            return self.device_capabilities.supports_touch
        elif feature == "haptic":
            return self.device_capabilities.supports_haptic
        elif feature == "ar":
            return self.device_capabilities.supports_ar
        elif feature == "vr":
            return self.device_capabilities.supports_vr
        elif feature == "voice":
            return self.device_capabilities.supports_voice
        elif feature == "gesture":
            return self.device_capabilities.supports_gesture
        elif feature == "biometric":
            return self.device_capabilities.supports_biometric
            
        # Check additional capabilities
        return feature in self.device_capabilities.additional_capabilities

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create Native Frontend Core
    frontend_core = NativeFrontendCore()
    frontend_core.start()
    
    # Register event handler
    def handle_ui_event(event_data):
        print(f"Received UI event: {event_data}")
        
    frontend_core.register_event_handler("ui.button.click", handle_ui_event)
    
    # Dispatch event
    frontend_core.dispatch_event(
        event_type="ui.button.click",
        event_data={
            "button_id": "submit_button",
            "screen": "login",
            "user_id": "user123"
        }
    )
    
    # Get device capabilities
    capabilities = frontend_core.get_device_capabilities()
    print(f"Device capabilities: {capabilities}")
    
    # Clean up
    frontend_core.stop()
