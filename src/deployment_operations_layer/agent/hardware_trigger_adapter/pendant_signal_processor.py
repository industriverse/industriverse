"""
Pendant Signal Processor - Processes signals from pendant devices

This module processes signals from pendant devices that trigger capsule instantiation,
interpreting the signal data and extracting relevant information.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class PendantSignalProcessor:
    """
    Processes signals from pendant devices.
    
    This component is responsible for processing signals from pendant devices
    that trigger capsule instantiation, interpreting the signal data and
    extracting relevant information.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Pendant Signal Processor.
        
        Args:
            config: Configuration dictionary for the processor
        """
        self.config = config or {}
        self.pendant_profiles = {}  # Pendant ID -> Pendant profile
        self.signal_patterns = {}  # Pattern ID -> Pattern definition
        
        logger.info("Initializing Pendant Signal Processor")
    
    def initialize(self):
        """Initialize the processor and load pendant profiles and signal patterns."""
        logger.info("Initializing Pendant Signal Processor")
        
        # Load pendant profiles
        self._load_pendant_profiles()
        
        # Load signal patterns
        self._load_signal_patterns()
        
        logger.info(f"Loaded {len(self.pendant_profiles)} pendant profiles and {len(self.signal_patterns)} signal patterns")
        return True
    
    def process_signal(self, trigger_id: str, trigger_config: Dict[str, Any], 
                      signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a signal from a pendant device.
        
        Args:
            trigger_id: ID of the trigger
            trigger_config: Configuration for the trigger
            signal_data: Data from the trigger signal
            
        Returns:
            Dictionary with processing result
        """
        logger.info(f"Processing pendant signal for trigger {trigger_id}")
        
        # Extract pendant ID from trigger configuration
        pendant_id = trigger_config.get("pendant_id")
        if not pendant_id:
            logger.error(f"No pendant ID found in trigger configuration for {trigger_id}")
            return {"success": False, "error": "No pendant ID in trigger configuration"}
        
        # Check if pendant profile exists
        if pendant_id not in self.pendant_profiles:
            logger.error(f"No profile found for pendant {pendant_id}")
            return {"success": False, "error": f"No profile found for pendant {pendant_id}"}
        
        # Extract signal type and payload
        signal_type = signal_data.get("signal_type")
        payload = signal_data.get("payload", {})
        
        if not signal_type:
            logger.error("No signal type in signal data")
            return {"success": False, "error": "No signal type in signal data"}
        
        # Process signal based on type
        if signal_type == "button_press":
            return self._process_button_press(pendant_id, trigger_id, payload)
        elif signal_type == "gesture":
            return self._process_gesture(pendant_id, trigger_id, payload)
        elif signal_type == "voice_command":
            return self._process_voice_command(pendant_id, trigger_id, payload)
        elif signal_type == "sensor_reading":
            return self._process_sensor_reading(pendant_id, trigger_id, payload)
        else:
            logger.error(f"Unsupported signal type: {signal_type}")
            return {"success": False, "error": f"Unsupported signal type: {signal_type}"}
    
    def register_pendant(self, pendant_id: str, pendant_profile: Dict[str, Any]) -> bool:
        """
        Register a pendant device.
        
        Args:
            pendant_id: ID of the pendant
            pendant_profile: Profile for the pendant
            
        Returns:
            True if successful, False otherwise
        """
        if pendant_id in self.pendant_profiles:
            logger.warning(f"Pendant {pendant_id} is already registered")
            return False
        
        # Validate pendant profile
        if not self._validate_pendant_profile(pendant_profile):
            logger.error(f"Invalid pendant profile for {pendant_id}")
            return False
        
        # Register pendant
        self.pendant_profiles[pendant_id] = pendant_profile
        
        # Save pendant profiles
        self._save_pendant_profiles()
        
        logger.info(f"Registered pendant {pendant_id}")
        return True
    
    def unregister_pendant(self, pendant_id: str) -> bool:
        """
        Unregister a pendant device.
        
        Args:
            pendant_id: ID of the pendant
            
        Returns:
            True if successful, False otherwise
        """
        if pendant_id not in self.pendant_profiles:
            logger.warning(f"Pendant {pendant_id} is not registered")
            return False
        
        # Unregister pendant
        del self.pendant_profiles[pendant_id]
        
        # Save pendant profiles
        self._save_pendant_profiles()
        
        logger.info(f"Unregistered pendant {pendant_id}")
        return True
    
    def register_signal_pattern(self, pattern_id: str, pattern_definition: Dict[str, Any]) -> bool:
        """
        Register a signal pattern.
        
        Args:
            pattern_id: ID of the pattern
            pattern_definition: Definition for the pattern
            
        Returns:
            True if successful, False otherwise
        """
        if pattern_id in self.signal_patterns:
            logger.warning(f"Pattern {pattern_id} is already registered")
            return False
        
        # Validate pattern definition
        if not self._validate_pattern_definition(pattern_definition):
            logger.error(f"Invalid pattern definition for {pattern_id}")
            return False
        
        # Register pattern
        self.signal_patterns[pattern_id] = pattern_definition
        
        # Save signal patterns
        self._save_signal_patterns()
        
        logger.info(f"Registered signal pattern {pattern_id}")
        return True
    
    def unregister_signal_pattern(self, pattern_id: str) -> bool:
        """
        Unregister a signal pattern.
        
        Args:
            pattern_id: ID of the pattern
            
        Returns:
            True if successful, False otherwise
        """
        if pattern_id not in self.signal_patterns:
            logger.warning(f"Pattern {pattern_id} is not registered")
            return False
        
        # Unregister pattern
        del self.signal_patterns[pattern_id]
        
        # Save signal patterns
        self._save_signal_patterns()
        
        logger.info(f"Unregistered signal pattern {pattern_id}")
        return True
    
    def _process_button_press(self, pendant_id: str, trigger_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a button press signal.
        
        Args:
            pendant_id: ID of the pendant
            trigger_id: ID of the trigger
            payload: Signal payload
            
        Returns:
            Dictionary with processing result
        """
        # Extract button ID and press type
        button_id = payload.get("button_id")
        press_type = payload.get("press_type", "single")
        
        if not button_id:
            logger.error("No button ID in payload")
            return {"success": False, "error": "No button ID in payload"}
        
        # Get pendant profile
        pendant_profile = self.pendant_profiles[pendant_id]
        
        # Check if button exists in pendant profile
        if "buttons" not in pendant_profile or button_id not in pendant_profile["buttons"]:
            logger.error(f"Button {button_id} not found in pendant profile")
            return {"success": False, "error": f"Button {button_id} not found in pendant profile"}
        
        # Get button configuration
        button_config = pendant_profile["buttons"][button_id]
        
        # Check if press type is supported
        if press_type not in button_config.get("press_types", ["single"]):
            logger.error(f"Press type {press_type} not supported for button {button_id}")
            return {"success": False, "error": f"Press type {press_type} not supported for button {button_id}"}
        
        # Get action for this button and press type
        action = button_config.get("actions", {}).get(press_type)
        
        if not action:
            logger.error(f"No action defined for button {button_id} and press type {press_type}")
            return {"success": False, "error": f"No action defined for button {button_id} and press type {press_type}"}
        
        # Process action
        context = {
            "pendant_id": pendant_id,
            "trigger_id": trigger_id,
            "button_id": button_id,
            "press_type": press_type,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Processed button press for pendant {pendant_id}, button {button_id}, press type {press_type}")
        
        return {
            "success": True,
            "signal_type": "button_press",
            "context": context,
            "action": action
        }
    
    def _process_gesture(self, pendant_id: str, trigger_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a gesture signal.
        
        Args:
            pendant_id: ID of the pendant
            trigger_id: ID of the trigger
            payload: Signal payload
            
        Returns:
            Dictionary with processing result
        """
        # Extract gesture type
        gesture_type = payload.get("gesture_type")
        
        if not gesture_type:
            logger.error("No gesture type in payload")
            return {"success": False, "error": "No gesture type in payload"}
        
        # Get pendant profile
        pendant_profile = self.pendant_profiles[pendant_id]
        
        # Check if gestures are supported in pendant profile
        if "gestures" not in pendant_profile:
            logger.error(f"Gestures not supported in pendant profile for {pendant_id}")
            return {"success": False, "error": f"Gestures not supported in pendant profile for {pendant_id}"}
        
        # Check if gesture type is supported
        if gesture_type not in pendant_profile["gestures"]:
            logger.error(f"Gesture type {gesture_type} not supported for pendant {pendant_id}")
            return {"success": False, "error": f"Gesture type {gesture_type} not supported for pendant {pendant_id}"}
        
        # Get action for this gesture
        action = pendant_profile["gestures"][gesture_type].get("action")
        
        if not action:
            logger.error(f"No action defined for gesture {gesture_type}")
            return {"success": False, "error": f"No action defined for gesture {gesture_type}"}
        
        # Process action
        context = {
            "pendant_id": pendant_id,
            "trigger_id": trigger_id,
            "gesture_type": gesture_type,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Processed gesture for pendant {pendant_id}, gesture type {gesture_type}")
        
        return {
            "success": True,
            "signal_type": "gesture",
            "context": context,
            "action": action
        }
    
    def _process_voice_command(self, pendant_id: str, trigger_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a voice command signal.
        
        Args:
            pendant_id: ID of the pendant
            trigger_id: ID of the trigger
            payload: Signal payload
            
        Returns:
            Dictionary with processing result
        """
        # Extract command text
        command_text = payload.get("command_text")
        
        if not command_text:
            logger.error("No command text in payload")
            return {"success": False, "error": "No command text in payload"}
        
        # Get pendant profile
        pendant_profile = self.pendant_profiles[pendant_id]
        
        # Check if voice commands are supported in pendant profile
        if "voice_commands" not in pendant_profile:
            logger.error(f"Voice commands not supported in pendant profile for {pendant_id}")
            return {"success": False, "error": f"Voice commands not supported in pendant profile for {pendant_id}"}
        
        # Find matching command
        matched_command = None
        matched_action = None
        
        for command, config in pendant_profile["voice_commands"].items():
            if command.lower() in command_text.lower():
                matched_command = command
                matched_action = config.get("action")
                break
        
        if not matched_command or not matched_action:
            logger.error(f"No matching command found for '{command_text}'")
            return {"success": False, "error": f"No matching command found for '{command_text}'"}
        
        # Process action
        context = {
            "pendant_id": pendant_id,
            "trigger_id": trigger_id,
            "command_text": command_text,
            "matched_command": matched_command,
            "action": matched_action,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Processed voice command for pendant {pendant_id}, command '{matched_command}'")
        
        return {
            "success": True,
            "signal_type": "voice_command",
            "context": context,
            "action": matched_action
        }
    
    def _process_sensor_reading(self, pendant_id: str, trigger_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a sensor reading signal.
        
        Args:
            pendant_id: ID of the pendant
            trigger_id: ID of the trigger
            payload: Signal payload
            
        Returns:
            Dictionary with processing result
        """
        # Extract sensor ID and reading
        sensor_id = payload.get("sensor_id")
        reading = payload.get("reading")
        
        if not sensor_id or reading is None:
            logger.error("Missing sensor ID or reading in payload")
            return {"success": False, "error": "Missing sensor ID or reading in payload"}
        
        # Get pendant profile
        pendant_profile = self.pendant_profiles[pendant_id]
        
        # Check if sensors are supported in pendant profile
        if "sensors" not in pendant_profile:
            logger.error(f"Sensors not supported in pendant profile for {pendant_id}")
            return {"success": False, "error": f"Sensors not supported in pendant profile for {pendant_id}"}
        
        # Check if sensor exists in pendant profile
        if sensor_id not in pendant_profile["sensors"]:
            logger.error(f"Sensor {sensor_id} not found in pendant profile")
            return {"success": False, "error": f"Sensor {sensor_id} not found in pendant profile"}
        
        # Get sensor configuration
        sensor_config = pendant_profile["sensors"][sensor_id]
        
        # Check if reading is within thresholds
        min_threshold = sensor_config.get("min_threshold")
        max_threshold = sensor_config.get("max_threshold")
        
        if min_threshold is not None and reading < min_threshold:
            logger.warning(f"Reading {reading} below min threshold {min_threshold} for sensor {sensor_id}")
            return {"success": False, "error": f"Reading {reading} below min threshold {min_threshold}"}
        
        if max_threshold is not None and reading > max_threshold:
            logger.warning(f"Reading {reading} above max threshold {max_threshold} for sensor {sensor_id}")
            return {"success": False, "error": f"Reading {reading} above max threshold {max_threshold}"}
        
        # Get action for this sensor
        action = sensor_config.get("action")
        
        if not action:
            logger.error(f"No action defined for sensor {sensor_id}")
            return {"success": False, "error": f"No action defined for sensor {sensor_id}"}
        
        # Process action
        context = {
            "pendant_id": pendant_id,
            "trigger_id": trigger_id,
            "sensor_id": sensor_id,
            "reading": reading,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Processed sensor reading for pendant {pendant_id}, sensor {sensor_id}, reading {reading}")
        
        return {
            "success": True,
            "signal_type": "sensor_reading",
            "context": context,
            "action": action
        }
    
    def _validate_pendant_profile(self, pendant_profile: Dict[str, Any]) -> bool:
        """
        Validate a pendant profile.
        
        Args:
            pendant_profile: Profile to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "model", "manufacturer"]
        for field in required_fields:
            if field not in pendant_profile:
                logger.error(f"Missing required field in pendant profile: {field}")
                return False
        
        # At least one interaction method must be defined
        interaction_methods = ["buttons", "gestures", "voice_commands", "sensors"]
        if not any(method in pendant_profile for method in interaction_methods):
            logger.error("No interaction methods defined in pendant profile")
            return False
        
        return True
    
    def _validate_pattern_definition(self, pattern_definition: Dict[str, Any]) -> bool:
        """
        Validate a pattern definition.
        
        Args:
            pattern_definition: Definition to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "description", "pattern_type"]
        for field in required_fields:
            if field not in pattern_definition:
                logger.error(f"Missing required field in pattern definition: {field}")
                return False
        
        # Check pattern type
        pattern_type = pattern_definition.get("pattern_type")
        if pattern_type not in ["sequence", "timing", "combination"]:
            logger.error(f"Invalid pattern type: {pattern_type}")
            return False
        
        # Type-specific validation
        if pattern_type == "sequence" and "sequence" not in pattern_definition:
            logger.error("Missing sequence in sequence pattern definition")
            return False
        elif pattern_type == "timing" and "timing_thresholds" not in pattern_definition:
            logger.error("Missing timing_thresholds in timing pattern definition")
            return False
        elif pattern_type == "combination" and "combination" not in pattern_definition:
            logger.error("Missing combination in combination pattern definition")
            return False
        
        return True
    
    def _load_pendant_profiles(self):
        """Load pendant profiles from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.pendant_profiles = {}
            logger.info("Loaded pendant profiles")
        except Exception as e:
            logger.error(f"Failed to load pendant profiles: {str(e)}")
    
    def _save_pendant_profiles(self):
        """Save pendant profiles to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.pendant_profiles)} pendant profiles")
        except Exception as e:
            logger.error(f"Failed to save pendant profiles: {str(e)}")
    
    def _load_signal_patterns(self):
        """Load signal patterns from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.signal_patterns = {}
            logger.info("Loaded signal patterns")
        except Exception as e:
            logger.error(f"Failed to load signal patterns: {str(e)}")
    
    def _save_signal_patterns(self):
        """Save signal patterns to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.signal_patterns)} signal patterns")
        except Exception as e:
            logger.error(f"Failed to save signal patterns: {str(e)}")
