"""
Haptic Feedback Module for the Industriverse UI/UX Layer.

This module provides haptic feedback capabilities for the Universal Skin and Agent Capsules,
enhancing the Ambient Intelligence experience through tactile sensations that represent
system states, alerts, and interactions.

Author: Manus
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
import uuid
import json
import random
import math
import threading

class HapticPatternType(Enum):
    """Enumeration of haptic pattern types."""
    NOTIFICATION = "notification"  # Notification pattern
    ALERT = "alert"  # Alert pattern
    CONFIRMATION = "confirmation"  # Confirmation pattern
    TRANSITION = "transition"  # Transition pattern
    CONTINUOUS = "continuous"  # Continuous pattern
    PULSE = "pulse"  # Pulse pattern
    RAMP = "ramp"  # Ramp pattern
    CUSTOM = "custom"  # Custom pattern

class HapticIntensity(Enum):
    """Enumeration of haptic intensity levels."""
    SUBTLE = 0  # Subtle intensity
    LIGHT = 1  # Light intensity
    MEDIUM = 2  # Medium intensity
    STRONG = 3  # Strong intensity
    MAXIMUM = 4  # Maximum intensity

class HapticPriority(Enum):
    """Enumeration of haptic priority levels."""
    LOW = 0  # Low priority
    MEDIUM = 1  # Medium priority
    HIGH = 2  # High priority
    CRITICAL = 3  # Critical priority

class DeviceType(Enum):
    """Enumeration of haptic device types."""
    MOBILE = "mobile"  # Mobile device
    WEARABLE = "wearable"  # Wearable device
    CONTROLLER = "controller"  # VR/AR controller
    GLOVE = "glove"  # Haptic glove
    VEST = "vest"  # Haptic vest
    INDUSTRIAL = "industrial"  # Industrial haptic device
    CUSTOM = "custom"  # Custom device

class HapticFeedbackManager:
    """
    Provides haptic feedback capabilities for the Industriverse UI/UX Layer.
    
    This class provides:
    - Haptic pattern definition and playback
    - Device-specific haptic adaptation
    - Haptic feedback for system events and state changes
    - Data representation through haptic sensations
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Haptic Feedback Manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.patterns: Dict[str, Dict[str, Any]] = {}  # Map pattern ID to pattern data
        self.active_patterns: Dict[str, Dict[str, Any]] = {}  # Map instance ID to active pattern data
        self.connected_devices: Dict[str, Dict[str, Any]] = {}  # Map device ID to device data
        self.device_capabilities: Dict[DeviceType, List[HapticPatternType]] = {}  # Map device type to supported patterns
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        
        # Initialize haptic backend (placeholder)
        self.haptic_backend = self._initialize_haptic_backend()
        
        # Initialize device capabilities
        self._initialize_device_capabilities()
        
        # Load patterns from config
        self._load_patterns_from_config()
        
    def start(self) -> bool:
        """
        Start the Haptic Feedback Manager.
        
        Returns:
            True if the manager was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Start haptic backend (placeholder)
        # self.haptic_backend.start()
        
        # Discover connected devices
        self._discover_connected_devices()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "haptic_feedback_manager_started",
            "connected_devices": list(self.connected_devices.keys())
        })
        
        self.logger.info("Haptic Feedback Manager started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Haptic Feedback Manager.
        
        Returns:
            True if the manager was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Stop all active patterns
        for instance_id in list(self.active_patterns.keys()):
            self.stop_pattern(instance_id)
            
        # Stop haptic backend (placeholder)
        # self.haptic_backend.stop()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "haptic_feedback_manager_stopped"
        })
        
        self.logger.info("Haptic Feedback Manager stopped.")
        return True
    
    def register_pattern(self,
                       pattern_id: str,
                       pattern_type: HapticPatternType,
                       intensity: HapticIntensity,
                       duration: float,
                       waveform: Optional[List[float]] = None,
                       repeat: int = 1,
                       interval: float = 0.0,
                       priority: HapticPriority = HapticPriority.MEDIUM,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a haptic pattern.
        
        Args:
            pattern_id: Unique identifier for this pattern
            pattern_type: Type of haptic pattern
            intensity: Intensity level
            duration: Duration in seconds
            waveform: Optional waveform data (list of amplitude values 0.0-1.0)
            repeat: Number of times to repeat the pattern
            interval: Interval between repeats in seconds
            priority: Priority level
            metadata: Additional metadata for this pattern
            
        Returns:
            True if the pattern was registered, False if already exists
        """
        if pattern_id in self.patterns:
            self.logger.warning(f"Haptic pattern {pattern_id} already exists.")
            return False
            
        self.patterns[pattern_id] = {
            "pattern_id": pattern_id,
            "pattern_type": pattern_type,
            "intensity": intensity,
            "duration": duration,
            "waveform": waveform or self._generate_default_waveform(pattern_type, duration),
            "repeat": repeat,
            "interval": interval,
            "priority": priority,
            "metadata": metadata or {}
        }
        
        self.logger.debug(f"Registered haptic pattern: {pattern_id} ({pattern_type.value})")
        return True
    
    def unregister_pattern(self, pattern_id: str) -> bool:
        """
        Unregister a haptic pattern.
        
        Args:
            pattern_id: ID of the pattern to unregister
            
        Returns:
            True if the pattern was unregistered, False if not found
        """
        if pattern_id not in self.patterns:
            return False
            
        # Stop any active instances of this pattern
        for instance_id, active_pattern in list(self.active_patterns.items()):
            if active_pattern["pattern_id"] == pattern_id:
                self.stop_pattern(instance_id)
                
        del self.patterns[pattern_id]
        
        self.logger.debug(f"Unregistered haptic pattern: {pattern_id}")
        return True
    
    def play_pattern(self,
                   pattern_id: str,
                   device_id: Optional[str] = None,
                   intensity_multiplier: float = 1.0,
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Play a haptic pattern.
        
        Args:
            pattern_id: ID of the pattern to play
            device_id: Optional ID of the device to play on (None for all connected devices)
            intensity_multiplier: Multiplier for the pattern's intensity (0.0-1.0)
            metadata: Additional metadata for this pattern instance
            
        Returns:
            Instance ID of the played pattern, or None if the pattern was not found or could not be played
        """
        if not self.is_active:
            self.logger.warning("Haptic Feedback Manager is not active.")
            return None
            
        if pattern_id not in self.patterns:
            self.logger.warning(f"Haptic pattern {pattern_id} not found.")
            return None
            
        pattern = self.patterns[pattern_id]
        
        # Check if we have any connected devices
        if not self.connected_devices:
            self.logger.warning("No haptic devices connected.")
            return None
            
        # Determine target devices
        target_devices = []
        if device_id:
            # Specific device
            if device_id in self.connected_devices:
                target_devices = [device_id]
            else:
                self.logger.warning(f"Device {device_id} not found.")
                return None
        else:
            # All connected devices
            target_devices = list(self.connected_devices.keys())
            
        if not target_devices:
            self.logger.warning("No target devices available.")
            return None
            
        # Generate instance ID
        instance_id = str(uuid.uuid4())
        
        # Create active pattern data
        active_pattern = {
            "instance_id": instance_id,
            "pattern_id": pattern_id,
            "pattern_type": pattern["pattern_type"],
            "intensity": pattern["intensity"],
            "intensity_multiplier": intensity_multiplier,
            "duration": pattern["duration"],
            "waveform": pattern["waveform"],
            "repeat": pattern["repeat"],
            "interval": pattern["interval"],
            "priority": pattern["priority"],
            "target_devices": target_devices,
            "start_time": time.time(),
            "metadata": {**(pattern["metadata"] or {}), **(metadata or {})}
        }
        
        # Store active pattern
        self.active_patterns[instance_id] = active_pattern
        
        # --- Haptic Backend Interaction (Placeholder) ---
        try:
            self.logger.debug(f"Playing haptic pattern: {pattern_id} (instance: {instance_id}) on {len(target_devices)} device(s)")
            
            # Simulate interaction with a hypothetical haptic backend
            # backend_params = {
            #     "waveform": pattern["waveform"],
            #     "intensity": pattern["intensity"].value * intensity_multiplier,
            #     "duration": pattern["duration"],
            #     "repeat": pattern["repeat"],
            #     "interval": pattern["interval"]
            # }
            # for device_id in target_devices:
            #     device = self.connected_devices[device_id]
            #     self.haptic_backend.play_pattern(device_id, instance_id, backend_params)
            
            # Simulate haptic playback with a thread
            threading.Thread(target=self._simulate_haptic_playback, args=(instance_id,), daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error playing haptic pattern {pattern_id}: {e}")
            del self.active_patterns[instance_id]
            return None
        # --- End Haptic Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "haptic_pattern_played",
            "instance_id": instance_id,
            "pattern_id": pattern_id,
            "pattern_type": pattern["pattern_type"].value,
            "target_devices": target_devices,
            "intensity": pattern["intensity"].value * intensity_multiplier
        })
        
        return instance_id
    
    def stop_pattern(self, instance_id: str) -> bool:
        """
        Stop an active haptic pattern.
        
        Args:
            instance_id: Instance ID of the pattern to stop
            
        Returns:
            True if the pattern was stopped, False if not found
        """
        if instance_id not in self.active_patterns:
            return False
            
        active_pattern = self.active_patterns[instance_id]
        
        # --- Haptic Backend Interaction (Placeholder) ---
        try:
            self.logger.debug(f"Stopping haptic pattern instance: {instance_id}")
            
            # Simulate interaction with a hypothetical haptic backend
            # for device_id in active_pattern["target_devices"]:
            #     self.haptic_backend.stop_pattern(device_id, instance_id)
            
            # Nothing to do for simulation, as the thread will end naturally
            # or check a flag to stop early
            
        except Exception as e:
            self.logger.error(f"Error stopping haptic pattern instance {instance_id}: {e}")
        # --- End Haptic Backend Interaction ---
        
        del self.active_patterns[instance_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "haptic_pattern_stopped",
            "instance_id": instance_id,
            "pattern_id": active_pattern["pattern_id"],
            "pattern_type": active_pattern["pattern_type"].value,
            "target_devices": active_pattern["target_devices"]
        })
        
        return True
    
    def create_data_haptic_mapping(self,
                                 mapping_id: str,
                                 data_range: Tuple[float, float],
                                 pattern_id: str,
                                 map_to_intensity: bool = True,
                                 map_to_duration: bool = False,
                                 map_to_repeat: bool = False,
                                 intensity_range: Optional[Tuple[float, float]] = None,
                                 duration_range: Optional[Tuple[float, float]] = None,
                                 repeat_range: Optional[Tuple[int, int]] = None,
                                 curve: str = "linear",
                                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a data-to-haptic mapping.
        
        Args:
            mapping_id: Unique identifier for this mapping
            data_range: Range of input data values (min, max)
            pattern_id: ID of the haptic pattern to use
            map_to_intensity: Whether to map data to intensity
            map_to_duration: Whether to map data to duration
            map_to_repeat: Whether to map data to repeat count
            intensity_range: Range of intensity multiplier values (min, max)
            duration_range: Range of duration multiplier values (min, max)
            repeat_range: Range of repeat count values (min, max)
            curve: Mapping curve type ("linear", "exponential", "logarithmic", etc.)
            metadata: Additional metadata for this mapping
            
        Returns:
            True if the mapping was created, False if already exists or pattern not found
        """
        if mapping_id in self.patterns:
            self.logger.warning(f"Haptic mapping {mapping_id} already exists.")
            return False
            
        if pattern_id not in self.patterns:
            self.logger.warning(f"Haptic pattern {pattern_id} not found.")
            return False
            
        # Create mapping as a special type of pattern
        self.patterns[mapping_id] = {
            "pattern_id": mapping_id,
            "is_mapping": True,
            "data_range": data_range,
            "base_pattern_id": pattern_id,
            "map_to_intensity": map_to_intensity,
            "map_to_duration": map_to_duration,
            "map_to_repeat": map_to_repeat,
            "intensity_range": intensity_range or (0.1, 1.0),
            "duration_range": duration_range or (0.5, 2.0),
            "repeat_range": repeat_range or (1, 5),
            "curve": curve,
            "metadata": metadata or {}
        }
        
        self.logger.debug(f"Created data haptic mapping: {mapping_id} (using pattern: {pattern_id})")
        return True
    
    def play_data_haptic(self,
                       data_value: float,
                       mapping_id: str,
                       device_id: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Play a haptic pattern based on a data value and mapping.
        
        Args:
            data_value: The data value to map to haptic feedback
            mapping_id: ID of the data-to-haptic mapping to use
            device_id: Optional ID of the device to play on (None for all connected devices)
            metadata: Additional metadata for this pattern instance
            
        Returns:
            Instance ID of the played pattern, or None if the mapping was not found or could not be played
        """
        if not self.is_active:
            self.logger.warning("Haptic Feedback Manager is not active.")
            return None
            
        if mapping_id not in self.patterns:
            self.logger.warning(f"Haptic mapping {mapping_id} not found.")
            return None
            
        mapping = self.patterns[mapping_id]
        
        # Check if it's actually a mapping
        if not mapping.get("is_mapping", False):
            self.logger.warning(f"Haptic pattern {mapping_id} is not a mapping.")
            return None
            
        base_pattern_id = mapping["base_pattern_id"]
        if base_pattern_id not in self.patterns:
            self.logger.warning(f"Base haptic pattern {base_pattern_id} not found.")
            return None
            
        # Map data value to haptic parameters
        data_min, data_max = mapping["data_range"]
        
        # Clamp data value to data range
        data_value = max(data_min, min(data_max, data_value))
        
        # Normalize data value to 0-1 range
        normalized = (data_value - data_min) / (data_max - data_min) if data_max > data_min else 0
        
        # Apply curve
        if mapping["curve"] == "linear":
            curved = normalized
        elif mapping["curve"] == "exponential":
            curved = normalized ** 2
        elif mapping["curve"] == "logarithmic":
            curved = math.sqrt(normalized)
        else:
            # Default to linear
            curved = normalized
            
        # Determine haptic parameters
        intensity_multiplier = 1.0
        duration_multiplier = 1.0
        repeat_count = None
        
        if mapping["map_to_intensity"]:
            intensity_min, intensity_max = mapping["intensity_range"]
            intensity_multiplier = intensity_min + curved * (intensity_max - intensity_min)
            
        if mapping["map_to_duration"]:
            duration_min, duration_max = mapping["duration_range"]
            duration_multiplier = duration_min + curved * (duration_max - duration_min)
            
        if mapping["map_to_repeat"]:
            repeat_min, repeat_max = mapping["repeat_range"]
            repeat_count = math.floor(repeat_min + curved * (repeat_max - repeat_min))
            
        # Create a modified version of the base pattern
        base_pattern = self.patterns[base_pattern_id]
        
        # Generate instance ID
        instance_id = str(uuid.uuid4())
        
        # Determine target devices
        target_devices = []
        if device_id:
            # Specific device
            if device_id in self.connected_devices:
                target_devices = [device_id]
            else:
                self.logger.warning(f"Device {device_id} not found.")
                return None
        else:
            # All connected devices
            target_devices = list(self.connected_devices.keys())
            
        if not target_devices:
            self.logger.warning("No target devices available.")
            return None
            
        # Create active pattern data
        active_pattern = {
            "instance_id": instance_id,
            "pattern_id": base_pattern_id,
            "pattern_type": base_pattern["pattern_type"],
            "intensity": base_pattern["intensity"],
            "intensity_multiplier": intensity_multiplier,
            "duration": base_pattern["duration"] * duration_multiplier,
            "waveform": base_pattern["waveform"],
            "repeat": repeat_count if repeat_count is not None else base_pattern["repeat"],
            "interval": base_pattern["interval"],
            "priority": base_pattern["priority"],
            "target_devices": target_devices,
            "start_time": time.time(),
            "is_data_haptic": True,
            "mapping_id": mapping_id,
            "data_value": data_value,
            "metadata": {
                **base_pattern["metadata"],
                **mapping["metadata"],
                **(metadata or {}),
                "data_haptic": {
                    "data_value": data_value,
                    "normalized_value": normalized,
                    "curved_value": curved
                }
            }
        }
        
        # Store active pattern
        self.active_patterns[instance_id] = active_pattern
        
        # --- Haptic Backend Interaction (Placeholder) ---
        try:
            self.logger.debug(f"Playing data haptic: {mapping_id} (data: {data_value}, instance: {instance_id}) on {len(target_devices)} device(s)")
            
            # Simulate interaction with a hypothetical haptic backend
            # backend_params = {
            #     "waveform": active_pattern["waveform"],
            #     "intensity": active_pattern["intensity"].value * intensity_multiplier,
            #     "duration": active_pattern["duration"],
            #     "repeat": active_pattern["repeat"],
            #     "interval": active_pattern["interval"]
            # }
            # for device_id in target_devices:
            #     device = self.connected_devices[device_id]
            #     self.haptic_backend.play_pattern(device_id, instance_id, backend_params)
            
            # Simulate haptic playback with a thread
            threading.Thread(target=self._simulate_haptic_playback, args=(instance_id,), daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error playing data haptic {mapping_id}: {e}")
            del self.active_patterns[instance_id]
            return None
        # --- End Haptic Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "data_haptic_played",
            "instance_id": instance_id,
            "mapping_id": mapping_id,
            "data_value": data_value,
            "normalized_value": normalized,
            "target_devices": target_devices,
            "intensity_multiplier": intensity_multiplier,
            "duration_multiplier": duration_multiplier,
            "repeat_count": active_pattern["repeat"]
        })
        
        return instance_id
    
    def create_continuous_haptic(self,
                               continuous_id: str,
                               base_pattern_id: str,
                               update_interval: float = 0.1,
                               fade_in_time: float = 0.5,
                               fade_out_time: float = 0.5,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a continuous haptic pattern that can be updated in real-time.
        
        Args:
            continuous_id: Unique identifier for this continuous pattern
            base_pattern_id: ID of the base haptic pattern to use
            update_interval: Interval in seconds between updates
            fade_in_time: Time in seconds to fade in
            fade_out_time: Time in seconds to fade out
            metadata: Additional metadata for this continuous pattern
            
        Returns:
            True if the continuous pattern was created, False if already exists or base pattern not found
        """
        if continuous_id in self.patterns:
            self.logger.warning(f"Haptic pattern {continuous_id} already exists.")
            return False
            
        if base_pattern_id not in self.patterns:
            self.logger.warning(f"Base haptic pattern {base_pattern_id} not found.")
            return False
            
        base_pattern = self.patterns[base_pattern_id]
        
        # Create continuous pattern as a special type of pattern
        self.patterns[continuous_id] = {
            "pattern_id": continuous_id,
            "is_continuous": True,
            "base_pattern_id": base_pattern_id,
            "pattern_type": base_pattern["pattern_type"],
            "intensity": base_pattern["intensity"],
            "waveform": base_pattern["waveform"],
            "update_interval": update_interval,
            "fade_in_time": fade_in_time,
            "fade_out_time": fade_out_time,
            "priority": base_pattern["priority"],
            "metadata": {**base_pattern["metadata"], **(metadata or {})}
        }
        
        self.logger.debug(f"Created continuous haptic pattern: {continuous_id} (using pattern: {base_pattern_id})")
        return True
    
    def start_continuous_haptic(self,
                              continuous_id: str,
                              device_id: Optional[str] = None,
                              intensity_multiplier: float = 1.0,
                              metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Start a continuous haptic pattern.
        
        Args:
            continuous_id: ID of the continuous pattern to start
            device_id: Optional ID of the device to play on (None for all connected devices)
            intensity_multiplier: Initial intensity multiplier (0.0-1.0)
            metadata: Additional metadata for this pattern instance
            
        Returns:
            Instance ID of the continuous pattern, or None if the pattern was not found or could not be started
        """
        if not self.is_active:
            self.logger.warning("Haptic Feedback Manager is not active.")
            return None
            
        if continuous_id not in self.patterns:
            self.logger.warning(f"Continuous haptic pattern {continuous_id} not found.")
            return None
            
        continuous_pattern = self.patterns[continuous_id]
        
        # Check if it's actually a continuous pattern
        if not continuous_pattern.get("is_continuous", False):
            self.logger.warning(f"Haptic pattern {continuous_id} is not a continuous pattern.")
            return None
            
        # Determine target devices
        target_devices = []
        if device_id:
            # Specific device
            if device_id in self.connected_devices:
                target_devices = [device_id]
            else:
                self.logger.warning(f"Device {device_id} not found.")
                return None
        else:
            # All connected devices
            target_devices = list(self.connected_devices.keys())
            
        if not target_devices:
            self.logger.warning("No target devices available.")
            return None
            
        # Generate instance ID
        instance_id = str(uuid.uuid4())
        
        # Create active pattern data
        active_pattern = {
            "instance_id": instance_id,
            "pattern_id": continuous_id,
            "is_continuous": True,
            "pattern_type": continuous_pattern["pattern_type"],
            "intensity": continuous_pattern["intensity"],
            "intensity_multiplier": intensity_multiplier,
            "current_intensity": 0.0,  # Start at 0 and fade in
            "target_intensity": intensity_multiplier,
            "waveform": continuous_pattern["waveform"],
            "update_interval": continuous_pattern["update_interval"],
            "fade_in_time": continuous_pattern["fade_in_time"],
            "fade_out_time": continuous_pattern["fade_out_time"],
            "priority": continuous_pattern["priority"],
            "target_devices": target_devices,
            "start_time": time.time(),
            "last_update_time": time.time(),
            "is_fading_out": False,
            "metadata": {**continuous_pattern["metadata"], **(metadata or {})}
        }
        
        # Store active pattern
        self.active_patterns[instance_id] = active_pattern
        
        # --- Haptic Backend Interaction (Placeholder) ---
        try:
            self.logger.debug(f"Starting continuous haptic pattern: {continuous_id} (instance: {instance_id}) on {len(target_devices)} device(s)")
            
            # Simulate interaction with a hypothetical haptic backend
            # backend_params = {
            #     "waveform": active_pattern["waveform"],
            #     "intensity": 0.0,  # Start at 0 and fade in
            #     "is_continuous": True,
            #     "update_interval": active_pattern["update_interval"]
            # }
            # for device_id in target_devices:
            #     device = self.connected_devices[device_id]
            #     self.haptic_backend.start_continuous_pattern(device_id, instance_id, backend_params)
            
            # Simulate continuous haptic playback with a thread
            threading.Thread(target=self._simulate_continuous_haptic, args=(instance_id,), daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error starting continuous haptic pattern {continuous_id}: {e}")
            del self.active_patterns[instance_id]
            return None
        # --- End Haptic Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "continuous_haptic_started",
            "instance_id": instance_id,
            "continuous_id": continuous_id,
            "pattern_type": continuous_pattern["pattern_type"].value,
            "target_devices": target_devices,
            "intensity_multiplier": intensity_multiplier
        })
        
        return instance_id
    
    def update_continuous_haptic(self,
                               instance_id: str,
                               intensity_multiplier: Optional[float] = None) -> bool:
        """
        Update a continuous haptic pattern.
        
        Args:
            instance_id: Instance ID of the continuous pattern
            intensity_multiplier: New intensity multiplier (0.0-1.0)
            
        Returns:
            True if the pattern was updated, False if not found or not a continuous pattern
        """
        if instance_id not in self.active_patterns:
            return False
            
        active_pattern = self.active_patterns[instance_id]
        
        # Check if it's actually a continuous pattern
        if not active_pattern.get("is_continuous", False):
            return False
            
        # Update intensity if provided
        if intensity_multiplier is not None:
            # Clamp to valid range
            intensity_multiplier = max(0.0, min(1.0, intensity_multiplier))
            active_pattern["target_intensity"] = intensity_multiplier
            
        # Update last update time
        active_pattern["last_update_time"] = time.time()
        
        # --- Haptic Backend Interaction (Placeholder) ---
        try:
            self.logger.debug(f"Updating continuous haptic pattern instance: {instance_id} (intensity: {intensity_multiplier})")
            
            # Simulate interaction with a hypothetical haptic backend
            # backend_params = {
            #     "intensity": active_pattern["intensity"].value * intensity_multiplier
            # }
            # for device_id in active_pattern["target_devices"]:
            #     device = self.connected_devices[device_id]
            #     self.haptic_backend.update_continuous_pattern(device_id, instance_id, backend_params)
            
            # Nothing to do for simulation, as the thread will handle the update
            
        except Exception as e:
            self.logger.error(f"Error updating continuous haptic pattern instance {instance_id}: {e}")
            return False
        # --- End Haptic Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "continuous_haptic_updated",
            "instance_id": instance_id,
            "continuous_id": active_pattern["pattern_id"],
            "target_intensity": active_pattern["target_intensity"]
        })
        
        return True
    
    def stop_continuous_haptic(self, instance_id: str, fade_out: bool = True) -> bool:
        """
        Stop a continuous haptic pattern.
        
        Args:
            instance_id: Instance ID of the continuous pattern
            fade_out: Whether to fade out the pattern
            
        Returns:
            True if the pattern was stopped, False if not found or not a continuous pattern
        """
        if instance_id not in self.active_patterns:
            return False
            
        active_pattern = self.active_patterns[instance_id]
        
        # Check if it's actually a continuous pattern
        if not active_pattern.get("is_continuous", False):
            return False
            
        if fade_out and not active_pattern.get("is_fading_out", False):
            # Start fade out
            active_pattern["is_fading_out"] = True
            active_pattern["target_intensity"] = 0.0
            active_pattern["fade_out_start_time"] = time.time()
            active_pattern["fade_out_start_intensity"] = active_pattern["current_intensity"]
            
            # Dispatch event
            self._dispatch_event({
                "event_type": "continuous_haptic_fading_out",
                "instance_id": instance_id,
                "continuous_id": active_pattern["pattern_id"],
                "fade_out_time": active_pattern["fade_out_time"]
            })
            
            return True
        else:
            # Stop immediately
            # --- Haptic Backend Interaction (Placeholder) ---
            try:
                self.logger.debug(f"Stopping continuous haptic pattern instance: {instance_id}")
                
                # Simulate interaction with a hypothetical haptic backend
                # for device_id in active_pattern["target_devices"]:
                #     device = self.connected_devices[device_id]
                #     self.haptic_backend.stop_continuous_pattern(device_id, instance_id)
                
                # Nothing to do for simulation, as the thread will end naturally
                # or check a flag to stop early
                
            except Exception as e:
                self.logger.error(f"Error stopping continuous haptic pattern instance {instance_id}: {e}")
            # --- End Haptic Backend Interaction ---
            
            del self.active_patterns[instance_id]
            
            # Dispatch event
            self._dispatch_event({
                "event_type": "continuous_haptic_stopped",
                "instance_id": instance_id,
                "continuous_id": active_pattern["pattern_id"],
                "target_devices": active_pattern["target_devices"]
            })
            
            return True
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for haptic feedback events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for haptic feedback events.
        
        Args:
            listener: The listener to remove
        """
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            
    def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_data: The event data to dispatch
        """
        event_data["timestamp"] = time.time()
        event_data["source"] = "HapticFeedbackManager"
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in haptic feedback event listener: {e}")
                
    def _initialize_haptic_backend(self) -> Any:
        """Placeholder for initializing the haptic backend."""
        # In a real implementation, this would initialize a haptic engine
        # For now, we'll just return a dummy object
        return object()
    
    def _initialize_device_capabilities(self) -> None:
        """Initialize device capabilities for different device types."""
        # Mobile devices
        self.device_capabilities[DeviceType.MOBILE] = [
            HapticPatternType.NOTIFICATION,
            HapticPatternType.ALERT,
            HapticPatternType.CONFIRMATION,
            HapticPatternType.TRANSITION,
            HapticPatternType.PULSE
        ]
        
        # Wearable devices
        self.device_capabilities[DeviceType.WEARABLE] = [
            HapticPatternType.NOTIFICATION,
            HapticPatternType.ALERT,
            HapticPatternType.CONFIRMATION,
            HapticPatternType.TRANSITION,
            HapticPatternType.PULSE,
            HapticPatternType.CONTINUOUS
        ]
        
        # VR/AR controllers
        self.device_capabilities[DeviceType.CONTROLLER] = [
            HapticPatternType.NOTIFICATION,
            HapticPatternType.ALERT,
            HapticPatternType.CONFIRMATION,
            HapticPatternType.TRANSITION,
            HapticPatternType.PULSE,
            HapticPatternType.CONTINUOUS,
            HapticPatternType.RAMP
        ]
        
        # Haptic gloves
        self.device_capabilities[DeviceType.GLOVE] = [
            HapticPatternType.NOTIFICATION,
            HapticPatternType.ALERT,
            HapticPatternType.CONFIRMATION,
            HapticPatternType.TRANSITION,
            HapticPatternType.PULSE,
            HapticPatternType.CONTINUOUS,
            HapticPatternType.RAMP,
            HapticPatternType.CUSTOM
        ]
        
        # Haptic vests
        self.device_capabilities[DeviceType.VEST] = [
            HapticPatternType.NOTIFICATION,
            HapticPatternType.ALERT,
            HapticPatternType.CONFIRMATION,
            HapticPatternType.TRANSITION,
            HapticPatternType.PULSE,
            HapticPatternType.CONTINUOUS,
            HapticPatternType.RAMP,
            HapticPatternType.CUSTOM
        ]
        
        # Industrial haptic devices
        self.device_capabilities[DeviceType.INDUSTRIAL] = [
            HapticPatternType.NOTIFICATION,
            HapticPatternType.ALERT,
            HapticPatternType.CONFIRMATION,
            HapticPatternType.TRANSITION,
            HapticPatternType.PULSE,
            HapticPatternType.CONTINUOUS,
            HapticPatternType.RAMP,
            HapticPatternType.CUSTOM
        ]
        
        # Custom devices
        self.device_capabilities[DeviceType.CUSTOM] = [
            HapticPatternType.CUSTOM
        ]
    
    def _load_patterns_from_config(self) -> None:
        """Load haptic patterns from the configuration."""
        patterns_config = self.config.get("haptic_patterns", [])
        
        for pattern_config in patterns_config:
            try:
                pattern_id = pattern_config["pattern_id"]
                pattern_type = HapticPatternType(pattern_config["pattern_type"])
                intensity = HapticIntensity(pattern_config.get("intensity", 2))
                duration = pattern_config.get("duration", 0.5)
                waveform = pattern_config.get("waveform")
                repeat = pattern_config.get("repeat", 1)
                interval = pattern_config.get("interval", 0.0)
                priority = HapticPriority(pattern_config.get("priority", 1))
                metadata = pattern_config.get("metadata")
                
                self.register_pattern(
                    pattern_id=pattern_id,
                    pattern_type=pattern_type,
                    intensity=intensity,
                    duration=duration,
                    waveform=waveform,
                    repeat=repeat,
                    interval=interval,
                    priority=priority,
                    metadata=metadata
                )
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error loading haptic pattern from config: {e}")
                
    def _discover_connected_devices(self) -> None:
        """Discover connected haptic devices."""
        # In a real implementation, this would query the haptic backend for connected devices
        # For now, we'll simulate some devices
        
        # Simulate a mobile device
        self.connected_devices["mobile_1"] = {
            "device_id": "mobile_1",
            "device_type": DeviceType.MOBILE,
            "name": "Smartphone",
            "capabilities": self.device_capabilities[DeviceType.MOBILE],
            "connection_type": "bluetooth",
            "battery_level": 0.85,
            "metadata": {}
        }
        
        # Simulate a VR controller
        self.connected_devices["controller_1"] = {
            "device_id": "controller_1",
            "device_type": DeviceType.CONTROLLER,
            "name": "VR Controller",
            "capabilities": self.device_capabilities[DeviceType.CONTROLLER],
            "connection_type": "wireless",
            "battery_level": 0.72,
            "metadata": {}
        }
        
        # Simulate an industrial haptic device
        self.connected_devices["industrial_1"] = {
            "device_id": "industrial_1",
            "device_type": DeviceType.INDUSTRIAL,
            "name": "Industrial Haptic Interface",
            "capabilities": self.device_capabilities[DeviceType.INDUSTRIAL],
            "connection_type": "wired",
            "battery_level": None,  # Wired, no battery
            "metadata": {}
        }
        
        self.logger.info(f"Discovered {len(self.connected_devices)} haptic devices.")
    
    def _generate_default_waveform(self, pattern_type: HapticPatternType, duration: float) -> List[float]:
        """
        Generate a default waveform for a haptic pattern.
        
        Args:
            pattern_type: Type of haptic pattern
            duration: Duration in seconds
            
        Returns:
            List of amplitude values (0.0-1.0)
        """
        # Number of samples (assuming 100 samples per second)
        num_samples = max(1, int(duration * 100))
        
        if pattern_type == HapticPatternType.NOTIFICATION:
            # Simple bell curve
            return [math.sin(math.pi * i / num_samples) for i in range(num_samples)]
            
        elif pattern_type == HapticPatternType.ALERT:
            # Sharp attack, slow decay
            return [1.0 if i < num_samples * 0.1 else 1.0 - (i - num_samples * 0.1) / (num_samples * 0.9) for i in range(num_samples)]
            
        elif pattern_type == HapticPatternType.CONFIRMATION:
            # Quick double pulse
            return [1.0 if i < num_samples * 0.2 or (i > num_samples * 0.5 and i < num_samples * 0.7) else 0.0 for i in range(num_samples)]
            
        elif pattern_type == HapticPatternType.TRANSITION:
            # Smooth ramp up and down
            return [i / (num_samples / 2) if i < num_samples / 2 else 2.0 - i / (num_samples / 2) for i in range(num_samples)]
            
        elif pattern_type == HapticPatternType.CONTINUOUS:
            # Constant intensity
            return [1.0 for _ in range(num_samples)]
            
        elif pattern_type == HapticPatternType.PULSE:
            # Regular pulses
            pulse_width = max(1, int(num_samples * 0.2))
            pulse_interval = max(1, int(num_samples * 0.3))
            waveform = []
            for i in range(num_samples):
                cycle_pos = i % (pulse_width + pulse_interval)
                waveform.append(1.0 if cycle_pos < pulse_width else 0.0)
            return waveform
            
        elif pattern_type == HapticPatternType.RAMP:
            # Sawtooth wave
            ramp_width = max(1, int(num_samples * 0.5))
            waveform = []
            for i in range(num_samples):
                cycle_pos = i % ramp_width
                waveform.append(cycle_pos / ramp_width)
            return waveform
            
        else:  # CUSTOM or unknown
            # Default to sine wave
            return [0.5 + 0.5 * math.sin(2 * math.pi * i / (num_samples / 4)) for i in range(num_samples)]
    
    def _simulate_haptic_playback(self, instance_id: str) -> None:
        """
        Simulate haptic playback for a pattern.
        
        Args:
            instance_id: Instance ID of the pattern
        """
        if instance_id not in self.active_patterns:
            return
            
        active_pattern = self.active_patterns[instance_id]
        
        # Get pattern parameters
        duration = active_pattern["duration"]
        repeat = active_pattern["repeat"]
        interval = active_pattern["interval"]
        
        # Simulate each repetition
        for i in range(repeat):
            # Check if pattern has been stopped
            if instance_id not in self.active_patterns:
                return
                
            # Simulate haptic duration
            time.sleep(duration)
            
            # Dispatch repetition event
            if instance_id in self.active_patterns:
                self._dispatch_event({
                    "event_type": "haptic_pattern_repetition",
                    "instance_id": instance_id,
                    "pattern_id": active_pattern["pattern_id"],
                    "repetition": i + 1,
                    "total_repetitions": repeat
                })
                
            # Wait for interval if not the last repetition
            if i < repeat - 1:
                time.sleep(interval)
                
        # Remove from active patterns if still present
        if instance_id in self.active_patterns:
            # Dispatch event
            self._dispatch_event({
                "event_type": "haptic_pattern_finished",
                "instance_id": instance_id,
                "pattern_id": active_pattern["pattern_id"],
                "pattern_type": active_pattern["pattern_type"].value,
                "target_devices": active_pattern["target_devices"]
            })
            
            del self.active_patterns[instance_id]
            
    def _simulate_continuous_haptic(self, instance_id: str) -> None:
        """
        Simulate continuous haptic playback.
        
        Args:
            instance_id: Instance ID of the continuous pattern
        """
        if instance_id not in self.active_patterns:
            return
            
        active_pattern = self.active_patterns[instance_id]
        
        # Get pattern parameters
        update_interval = active_pattern["update_interval"]
        fade_in_time = active_pattern["fade_in_time"]
        fade_out_time = active_pattern["fade_out_time"]
        
        # Continuous loop
        while instance_id in self.active_patterns:
            current_time = time.time()
            pattern = self.active_patterns[instance_id]
            
            # Calculate current intensity
            if pattern.get("is_fading_out", False):
                # Fading out
                elapsed_fade_out_time = current_time - pattern["fade_out_start_time"]
                fade_progress = min(1.0, elapsed_fade_out_time / fade_out_time)
                pattern["current_intensity"] = pattern["fade_out_start_intensity"] * (1.0 - fade_progress)
                
                # Check if fade out is complete
                if fade_progress >= 1.0:
                    # Dispatch event
                    self._dispatch_event({
                        "event_type": "continuous_haptic_stopped",
                        "instance_id": instance_id,
                        "continuous_id": pattern["pattern_id"],
                        "target_devices": pattern["target_devices"]
                    })
                    
                    # Remove from active patterns
                    if instance_id in self.active_patterns:
                        del self.active_patterns[instance_id]
                    return
            else:
                # Normal operation or fading in
                elapsed_time = current_time - pattern["start_time"]
                
                if elapsed_time < fade_in_time:
                    # Fading in
                    fade_progress = min(1.0, elapsed_time / fade_in_time)
                    pattern["current_intensity"] = pattern["target_intensity"] * fade_progress
                else:
                    # Normal operation - interpolate toward target intensity
                    diff = pattern["target_intensity"] - pattern["current_intensity"]
                    # Smooth interpolation
                    pattern["current_intensity"] += diff * min(1.0, update_interval / 0.1)
                    
            # Dispatch update event
            self._dispatch_event({
                "event_type": "continuous_haptic_update",
                "instance_id": instance_id,
                "continuous_id": pattern["pattern_id"],
                "current_intensity": pattern["current_intensity"],
                "target_intensity": pattern["target_intensity"],
                "is_fading_out": pattern.get("is_fading_out", False)
            })
            
            # Wait for next update
            time.sleep(update_interval)

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create haptic manager
    haptic_config = {
        "haptic_patterns": [
            {
                "pattern_id": "notification_info",
                "pattern_type": "notification",
                "intensity": 1,  # LIGHT
                "duration": 0.3,
                "repeat": 1
            },
            {
                "pattern_id": "alert_warning",
                "pattern_type": "alert",
                "intensity": 3,  # STRONG
                "duration": 0.5,
                "repeat": 2,
                "interval": 0.1
            }
        ]
    }
    
    haptic_manager = HapticFeedbackManager(config=haptic_config)
    
    # Start the manager
    haptic_manager.start()
    
    # Register a custom pattern
    haptic_manager.register_pattern(
        pattern_id="machine_status",
        pattern_type=HapticPatternType.PULSE,
        intensity=HapticIntensity.MEDIUM,
        duration=1.0,
        repeat=3,
        interval=0.2
    )
    
    # Create a data-to-haptic mapping
    haptic_manager.create_data_haptic_mapping(
        mapping_id="temperature_to_haptic",
        data_range=(0, 100),
        pattern_id="machine_status",
        map_to_intensity=True,
        map_to_repeat=True,
        intensity_range=(0.2, 1.0),
        repeat_range=(1, 5)
    )
    
    # Play a notification
    haptic_manager.play_pattern("notification_info")
    
    # Play a data-mapped haptic
    haptic_manager.play_data_haptic(
        data_value=75.5,
        mapping_id="temperature_to_haptic"
    )
    
    # Create and start a continuous haptic
    haptic_manager.create_continuous_haptic(
        continuous_id="machine_running",
        base_pattern_id="machine_status",
        update_interval=0.1
    )
    
    continuous_instance = haptic_manager.start_continuous_haptic(
        continuous_id="machine_running",
        intensity_multiplier=0.5
    )
    
    # Wait a bit
    time.sleep(3)
    
    # Update continuous haptic
    haptic_manager.update_continuous_haptic(
        instance_id=continuous_instance,
        intensity_multiplier=0.8
    )
    
    # Wait a bit more
    time.sleep(3)
    
    # Stop continuous haptic with fade out
    haptic_manager.stop_continuous_haptic(
        instance_id=continuous_instance,
        fade_out=True
    )
    
    # Wait for fade out
    time.sleep(2)
    
    # Stop everything and shut down
    haptic_manager.stop()
"""
