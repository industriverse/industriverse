"""
Voice Interface Component for the Industriverse UI/UX Layer.

This module provides comprehensive voice interaction capabilities for the Universal Skin
and Agent Capsules, enabling natural language communication in industrial environments.

Author: Manus
"""

import logging
import time
import threading
import uuid
import json
import random
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass

class VoiceCommandType(Enum):
    """Enumeration of voice command types."""
    NAVIGATION = "navigation"  # Navigation commands
    SELECTION = "selection"  # Selection commands
    ACTION = "action"  # Action commands
    QUERY = "query"  # Query commands
    SYSTEM = "system"  # System commands
    INDUSTRIAL = "industrial"  # Industrial-specific commands
    CUSTOM = "custom"  # Custom command type

class VoiceConfidenceLevel(Enum):
    """Enumeration of voice recognition confidence levels."""
    LOW = 0  # Low confidence
    MEDIUM = 1  # Medium confidence
    HIGH = 2  # High confidence
    VERY_HIGH = 3  # Very high confidence

@dataclass
class VoiceCommand:
    """Data class representing a voice command."""
    command_id: str  # Command identifier
    command_type: VoiceCommandType  # Command type
    phrases: List[str]  # List of trigger phrases
    description: str  # Human-readable description
    parameters: Dict[str, Any]  # Command-specific parameters
    metadata: Dict[str, Any]  # Additional metadata
    
@dataclass
class VoiceRecognitionResult:
    """Data class representing a voice recognition result."""
    result_id: str  # Result identifier
    text: str  # Recognized text
    command_id: Optional[str]  # Matched command ID, if any
    confidence: float  # Confidence level (0.0-1.0)
    confidence_level: VoiceConfidenceLevel  # Confidence level enum
    parameters: Dict[str, Any]  # Extracted parameters
    timestamp: float  # Recognition timestamp
    user_id: Optional[str]  # User ID, if available
    device_id: Optional[str]  # Device ID, if available
    metadata: Dict[str, Any]  # Additional metadata

class VoiceInterface:
    """
    Provides voice interaction capabilities for the Industriverse UI/UX Layer.
    
    This class provides:
    - Natural language voice command recognition
    - Voice-based interaction with UI elements and Agent Capsules
    - Industrial-specific voice commands
    - Integration with the Universal Skin and Capsule Framework
    - Multi-language support
    - Ambient voice recognition
    - Voice-based authentication
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Voice Interface.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.is_listening = False
        self.commands: Dict[str, VoiceCommand] = {}  # Map command ID to command data
        self.command_history: List[VoiceRecognitionResult] = []  # List of recent recognized commands
        self.command_listeners: Dict[str, List[Callable[[VoiceRecognitionResult], None]]] = {}  # Map command ID to listeners
        self.global_listeners: List[Callable[[VoiceRecognitionResult], None]] = []  # Global command listeners
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []  # Event listeners
        self.logger = logging.getLogger(__name__)
        self.current_language = self.config.get("default_language", "en-US")
        self.available_languages = self.config.get("available_languages", ["en-US"])
        self.wake_words = self.config.get("wake_words", ["assistant", "system", "industriverse"])
        self.ambient_mode_enabled = self.config.get("ambient_mode_enabled", False)
        self.voice_authentication_enabled = self.config.get("voice_authentication_enabled", False)
        self.authenticated_users: Dict[str, Dict[str, Any]] = {}  # Map user ID to authentication data
        
        # Initialize voice backend (placeholder)
        self.voice_backend = self._initialize_voice_backend()
        
        # Load commands from config
        self._load_commands_from_config()
        
    def start(self) -> bool:
        """
        Start the Voice Interface.
        
        Returns:
            True if the interface was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Start voice backend (placeholder)
        # self.voice_backend.start()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_interface_started"
        })
        
        self.logger.info("Voice Interface started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Voice Interface.
        
        Returns:
            True if the interface was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        self.is_listening = False
        
        # Stop voice backend (placeholder)
        # self.voice_backend.stop()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_interface_stopped"
        })
        
        self.logger.info("Voice Interface stopped.")
        return True
    
    def start_listening(self, user_id: Optional[str] = None, device_id: Optional[str] = None) -> bool:
        """
        Start actively listening for voice commands.
        
        Args:
            user_id: Optional user ID to associate with recognition
            device_id: Optional device ID to associate with recognition
            
        Returns:
            True if listening was started, False if already listening or interface not active
        """
        if not self.is_active:
            self.logger.warning("Voice Interface is not active.")
            return False
            
        if self.is_listening:
            return False
            
        self.is_listening = True
        
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.start_listening({
            #     "user_id": user_id,
            #     "device_id": device_id,
            #     "language": self.current_language,
            #     "ambient_mode": self.ambient_mode_enabled,
            #     "wake_words": self.wake_words
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error starting listening with voice backend: {e}")
            self.is_listening = False
            return False
        # --- End Voice Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_listening_started",
            "user_id": user_id,
            "device_id": device_id,
            "language": self.current_language,
            "ambient_mode": self.ambient_mode_enabled
        })
        
        self.logger.debug("Started listening for voice commands.")
        
        # Start background thread for simulating voice recognition
        threading.Thread(target=self._simulate_voice_recognition, args=(user_id, device_id), daemon=True).start()
        
        return True
    
    def stop_listening(self) -> bool:
        """
        Stop actively listening for voice commands.
        
        Returns:
            True if listening was stopped, False if not listening
        """
        if not self.is_listening:
            return False
            
        self.is_listening = False
        
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.stop_listening()
            pass
        except Exception as e:
            self.logger.error(f"Error stopping listening with voice backend: {e}")
        # --- End Voice Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_listening_stopped"
        })
        
        self.logger.debug("Stopped listening for voice commands.")
        return True
    
    def register_command(self,
                       command_id: str,
                       command_type: VoiceCommandType,
                       phrases: List[str],
                       description: str,
                       parameters: Optional[Dict[str, Any]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a voice command.
        
        Args:
            command_id: Unique identifier for this command
            command_type: Type of command
            phrases: List of trigger phrases
            description: Human-readable description
            parameters: Command-specific parameters
            metadata: Additional metadata for this command
            
        Returns:
            True if the command was registered, False if already exists
        """
        if command_id in self.commands:
            self.logger.warning(f"Command {command_id} already exists.")
            return False
            
        command = VoiceCommand(
            command_id=command_id,
            command_type=command_type,
            phrases=phrases,
            description=description,
            parameters=parameters or {},
            metadata=metadata or {}
        )
        
        self.commands[command_id] = command
        
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.register_command(command_id, {
            #     "type": command_type.value,
            #     "phrases": phrases,
            #     "parameters": parameters or {}
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error registering command with voice backend: {e}")
        # --- End Voice Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_command_registered",
            "command_id": command_id,
            "command_type": command_type.value,
            "phrases": phrases,
            "description": description
        })
        
        self.logger.debug(f"Registered voice command: {command_id} ({command_type.value})")
        return True
    
    def unregister_command(self, command_id: str) -> bool:
        """
        Unregister a voice command.
        
        Args:
            command_id: ID of the command to unregister
            
        Returns:
            True if the command was unregistered, False if not found
        """
        if command_id not in self.commands:
            return False
            
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.unregister_command(command_id)
            pass
        except Exception as e:
            self.logger.error(f"Error unregistering command with voice backend: {e}")
        # --- End Voice Backend Interaction ---
        
        del self.commands[command_id]
        
        # Remove any listeners for this command
        if command_id in self.command_listeners:
            del self.command_listeners[command_id]
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_command_unregistered",
            "command_id": command_id
        })
        
        self.logger.debug(f"Unregistered voice command: {command_id}")
        return True
    
    def create_navigation_command(self,
                                command_id: str,
                                phrases: List[str],
                                description: str,
                                target: str,
                                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a navigation voice command.
        
        Args:
            command_id: Unique identifier for this command
            phrases: List of trigger phrases
            description: Human-readable description
            target: Navigation target
            metadata: Additional metadata for this command
            
        Returns:
            True if the command was created, False if already exists
        """
        parameters = {
            "target": target
        }
        
        return self.register_command(
            command_id=command_id,
            command_type=VoiceCommandType.NAVIGATION,
            phrases=phrases,
            description=description,
            parameters=parameters,
            metadata=metadata
        )
    
    def create_action_command(self,
                            command_id: str,
                            phrases: List[str],
                            description: str,
                            action: str,
                            action_parameters: Optional[Dict[str, Any]] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create an action voice command.
        
        Args:
            command_id: Unique identifier for this command
            phrases: List of trigger phrases
            description: Human-readable description
            action: Action to perform
            action_parameters: Parameters for the action
            metadata: Additional metadata for this command
            
        Returns:
            True if the command was created, False if already exists
        """
        parameters = {
            "action": action,
            "action_parameters": action_parameters or {}
        }
        
        return self.register_command(
            command_id=command_id,
            command_type=VoiceCommandType.ACTION,
            phrases=phrases,
            description=description,
            parameters=parameters,
            metadata=metadata
        )
    
    def create_industrial_command(self,
                                command_id: str,
                                phrases: List[str],
                                description: str,
                                action: str,
                                safety_level: str = "normal",
                                requires_confirmation: bool = False,
                                action_parameters: Optional[Dict[str, Any]] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create an industrial-specific voice command.
        
        Args:
            command_id: Unique identifier for this command
            phrases: List of trigger phrases
            description: Human-readable description
            action: Action to perform
            safety_level: Safety level ("normal", "caution", "critical")
            requires_confirmation: Whether this command requires confirmation
            action_parameters: Parameters for the action
            metadata: Additional metadata for this command
            
        Returns:
            True if the command was created, False if already exists
        """
        parameters = {
            "action": action,
            "safety_level": safety_level,
            "requires_confirmation": requires_confirmation,
            "action_parameters": action_parameters or {}
        }
        
        return self.register_command(
            command_id=command_id,
            command_type=VoiceCommandType.INDUSTRIAL,
            phrases=phrases,
            description=description,
            parameters=parameters,
            metadata=metadata
        )
    
    def add_command_listener(self, command_id: str, listener: Callable[[VoiceRecognitionResult], None]) -> bool:
        """
        Add a listener for a specific voice command.
        
        Args:
            command_id: ID of the command to listen for
            listener: Callback function that will be called when the command is recognized
            
        Returns:
            True if the listener was added, False if command not found
        """
        if command_id not in self.commands:
            self.logger.warning(f"Command {command_id} not found.")
            return False
            
        if command_id not in self.command_listeners:
            self.command_listeners[command_id] = []
            
        self.command_listeners[command_id].append(listener)
        return True
    
    def remove_command_listener(self, command_id: str, listener: Callable[[VoiceRecognitionResult], None]) -> bool:
        """
        Remove a listener for a specific voice command.
        
        Args:
            command_id: ID of the command
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if command_id not in self.command_listeners:
            return False
            
        if listener in self.command_listeners[command_id]:
            self.command_listeners[command_id].remove(listener)
            return True
            
        return False
    
    def add_global_listener(self, listener: Callable[[VoiceRecognitionResult], None]) -> None:
        """
        Add a global listener for all voice commands.
        
        Args:
            listener: Callback function that will be called when any command is recognized
        """
        self.global_listeners.append(listener)
        
    def remove_global_listener(self, listener: Callable[[VoiceRecognitionResult], None]) -> bool:
        """
        Remove a global listener.
        
        Args:
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if listener in self.global_listeners:
            self.global_listeners.remove(listener)
            return True
            
        return False
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for voice interface events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            return True
            
        return False
    
    def get_recognized_commands(self, limit: int = 10) -> List[VoiceRecognitionResult]:
        """
        Get recently recognized voice commands.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of recently recognized commands
        """
        return self.command_history[:limit]
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the current language for voice recognition.
        
        Args:
            language_code: Language code (e.g., "en-US", "fr-FR")
            
        Returns:
            True if the language was set, False if not available
        """
        if language_code not in self.available_languages:
            self.logger.warning(f"Language {language_code} not available.")
            return False
            
        self.current_language = language_code
        
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.set_language(language_code)
            pass
        except Exception as e:
            self.logger.error(f"Error setting language with voice backend: {e}")
            return False
        # --- End Voice Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_language_changed",
            "language": language_code
        })
        
        self.logger.debug(f"Set voice recognition language to {language_code}")
        return True
    
    def set_ambient_mode(self, enabled: bool) -> None:
        """
        Enable or disable ambient voice recognition mode.
        
        In ambient mode, the system listens for wake words before processing commands.
        
        Args:
            enabled: Whether to enable ambient mode
        """
        self.ambient_mode_enabled = enabled
        
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.set_ambient_mode(enabled)
            pass
        except Exception as e:
            self.logger.error(f"Error setting ambient mode with voice backend: {e}")
        # --- End Voice Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_ambient_mode_changed",
            "enabled": enabled
        })
        
        self.logger.debug(f"{'Enabled' if enabled else 'Disabled'} ambient voice recognition mode.")
    
    def set_wake_words(self, wake_words: List[str]) -> None:
        """
        Set the wake words for ambient voice recognition mode.
        
        Args:
            wake_words: List of wake words
        """
        if not wake_words:
            self.logger.warning("Wake words list cannot be empty.")
            return
            
        self.wake_words = wake_words
        
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.set_wake_words(wake_words)
            pass
        except Exception as e:
            self.logger.error(f"Error setting wake words with voice backend: {e}")
        # --- End Voice Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_wake_words_changed",
            "wake_words": wake_words
        })
        
        self.logger.debug(f"Set wake words to: {', '.join(wake_words)}")
    
    def enable_voice_authentication(self, enabled: bool) -> None:
        """
        Enable or disable voice authentication.
        
        Args:
            enabled: Whether to enable voice authentication
        """
        self.voice_authentication_enabled = enabled
        
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.set_voice_authentication(enabled)
            pass
        except Exception as e:
            self.logger.error(f"Error setting voice authentication with voice backend: {e}")
        # --- End Voice Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_authentication_changed",
            "enabled": enabled
        })
        
        self.logger.debug(f"{'Enabled' if enabled else 'Disabled'} voice authentication.")
    
    def register_voice_profile(self, user_id: str, voice_data: Any) -> bool:
        """
        Register a voice profile for authentication.
        
        Args:
            user_id: User ID to associate with this voice profile
            voice_data: Voice profile data
            
        Returns:
            True if the profile was registered, False if error
        """
        if not self.voice_authentication_enabled:
            self.logger.warning("Voice authentication is not enabled.")
            return False
            
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.register_voice_profile(user_id, voice_data)
            pass
        except Exception as e:
            self.logger.error(f"Error registering voice profile with voice backend: {e}")
            return False
        # --- End Voice Backend Interaction ---
        
        self.authenticated_users[user_id] = {
            "user_id": user_id,
            "registration_time": time.time(),
            "last_authentication_time": None
        }
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_profile_registered",
            "user_id": user_id
        })
        
        self.logger.debug(f"Registered voice profile for user {user_id}")
        return True
    
    def unregister_voice_profile(self, user_id: str) -> bool:
        """
        Unregister a voice profile.
        
        Args:
            user_id: User ID to unregister
            
        Returns:
            True if the profile was unregistered, False if not found
        """
        if user_id not in self.authenticated_users:
            return False
            
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.unregister_voice_profile(user_id)
            pass
        except Exception as e:
            self.logger.error(f"Error unregistering voice profile with voice backend: {e}")
        # --- End Voice Backend Interaction ---
        
        del self.authenticated_users[user_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_profile_unregistered",
            "user_id": user_id
        })
        
        self.logger.debug(f"Unregistered voice profile for user {user_id}")
        return True
    
    def synthesize_speech(self, text: str, voice_id: Optional[str] = None, language: Optional[str] = None) -> bool:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice_id: Optional voice ID to use
            language: Optional language to use
            
        Returns:
            True if speech synthesis was started, False if error
        """
        if not self.is_active:
            self.logger.warning("Voice Interface is not active.")
            return False
            
        language = language or self.current_language
        
        # --- Voice Backend Interaction (Placeholder) ---
        try:
            # self.voice_backend.synthesize_speech(text, {
            #     "voice_id": voice_id,
            #     "language": language
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error synthesizing speech with voice backend: {e}")
            return False
        # --- End Voice Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "speech_synthesis_started",
            "text": text,
            "voice_id": voice_id,
            "language": language
        })
        
        self.logger.debug(f"Synthesizing speech: {text}")
        return True
    
    def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_data: The event data to dispatch
        """
        event_data["timestamp"] = time.time()
        event_data["source"] = "VoiceInterface"
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in voice interface event listener: {e}")
                
    def _dispatch_recognition_result(self, result: VoiceRecognitionResult) -> None:
        """
        Dispatch a voice recognition result to command-specific and global listeners.
        
        Args:
            result: The voice recognition result
        """
        # Add to command history
        self.command_history.insert(0, result)
        
        # Limit history size
        max_history = self.config.get("max_command_history", 100)
        if len(self.command_history) > max_history:
            self.command_history = self.command_history[:max_history]
            
        # Dispatch to command-specific listeners
        if result.command_id and result.command_id in self.command_listeners:
            for listener in self.command_listeners[result.command_id]:
                try:
                    listener(result)
                except Exception as e:
                    self.logger.error(f"Error in command listener for {result.command_id}: {e}")
                    
        # Dispatch to global listeners
        for listener in self.global_listeners:
            try:
                listener(result)
            except Exception as e:
                self.logger.error(f"Error in global voice command listener: {e}")
                
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_command_recognized",
            "result_id": result.result_id,
            "text": result.text,
            "command_id": result.command_id,
            "confidence": result.confidence,
            "confidence_level": result.confidence_level.value,
            "user_id": result.user_id,
            "device_id": result.device_id
        })
    
    def _initialize_voice_backend(self) -> Any:
        """Placeholder for initializing the voice backend."""
        # In a real implementation, this would initialize a voice recognition system
        # For now, we'll just return a dummy object
        return object()
    
    def _load_commands_from_config(self) -> None:
        """Load voice commands from the configuration."""
        commands_config = self.config.get("commands", [])
        
        for command_config in commands_config:
            try:
                command_id = command_config["command_id"]
                command_type = VoiceCommandType(command_config["command_type"])
                phrases = command_config["phrases"]
                description = command_config["description"]
                parameters = command_config.get("parameters", {})
                metadata = command_config.get("metadata", {})
                
                self.register_command(
                    command_id=command_id,
                    command_type=command_type,
                    phrases=phrases,
                    description=description,
                    parameters=parameters,
                    metadata=metadata
                )
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error loading command from config: {e}")
                
    def _simulate_voice_recognition(self, user_id: Optional[str], device_id: Optional[str]) -> None:
        """
        Simulate voice recognition for testing purposes.
        
        Args:
            user_id: User ID to associate with recognition
            device_id: Device ID to associate with recognition
        """
        while self.is_listening and self.is_active:
            try:
                # Randomly recognize a command occasionally
                if random.random() < 0.01:  # 1% chance per iteration
                    if self.commands:
                        # Pick a random command
                        command_id = random.choice(list(self.commands.keys()))
                        command = self.commands[command_id]
                        
                        # Pick a random phrase
                        phrase = random.choice(command.phrases)
                        
                        # Create recognition result
                        result = VoiceRecognitionResult(
                            result_id=str(uuid.uuid4()),
                            text=phrase,
                            command_id=command_id,
                            confidence=random.uniform(0.7, 1.0),
                            confidence_level=VoiceConfidenceLevel.HIGH,
                            parameters={},  # Recognition-specific parameters
                            timestamp=time.time(),
                            user_id=user_id,
                            device_id=device_id,
                            metadata={}
                        )
                        
                        # Dispatch the result
                        self._dispatch_recognition_result(result)
                        
            except Exception as e:
                self.logger.error(f"Error in voice recognition simulation: {e}")
                
            # Sleep a bit
            time.sleep(0.1)

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create voice interface
    voice_config = {
        "default_language": "en-US",
        "available_languages": ["en-US", "fr-FR", "de-DE", "es-ES"],
        "wake_words": ["assistant", "system", "industriverse"],
        "ambient_mode_enabled": True,
        "voice_authentication_enabled": False,
        "max_command_history": 100,
        "commands": [
            {
                "command_id": "navigate_home",
                "command_type": "navigation",
                "phrases": ["go home", "show home", "navigate to home"],
                "description": "Navigate to home screen",
                "parameters": {
                    "target": "home"
                }
            },
            {
                "command_id": "open_settings",
                "command_type": "navigation",
                "phrases": ["open settings", "show settings", "go to settings"],
                "description": "Open settings screen",
                "parameters": {
                    "target": "settings"
                }
            }
        ]
    }
    
    voice_interface = VoiceInterface(config=voice_config)
    
    # Start the interface
    voice_interface.start()
    
    # Register an action command
    voice_interface.create_action_command(
        command_id="refresh_data",
        phrases=["refresh data", "update data", "reload data"],
        description="Refresh current data",
        action="refresh",
        metadata={"category": "data"}
    )
    
    # Register an industrial command
    voice_interface.create_industrial_command(
        command_id="emergency_stop",
        phrases=["emergency stop", "stop immediately", "halt system"],
        description="Emergency stop command",
        action="emergency_stop",
        safety_level="critical",
        requires_confirmation=True,
        metadata={"category": "safety"}
    )
    
    # Add a command listener
    def on_emergency_stop(result):
        print(f"Emergency stop command recognized! Confidence: {result.confidence:.2f}")
        
    voice_interface.add_command_listener("emergency_stop", on_emergency_stop)
    
    # Add a global listener
    def on_any_command(result):
        print(f"Command recognized: {result.text} (Command ID: {result.command_id})")
        
    voice_interface.add_global_listener(on_any_command)
    
    # Start listening
    voice_interface.start_listening(user_id="user_1")
    
    # Wait a bit to see events
    time.sleep(5)
    
    # Synthesize speech
    voice_interface.synthesize_speech("System is operational and ready for commands.")
    
    # Get recognized commands
    recent_commands = voice_interface.get_recognized_commands()
    print(f"Recognized {len(recent_commands)} commands")
    
    # Stop listening
    voice_interface.stop_listening()
    
    # Stop the interface
    voice_interface.stop()
"""
