"""
Mobile + Voice + AR-native Smart Panels for the Industriverse UI/UX Layer.

This module provides capsule summary cards with voice-first triggers, decision previews, 
or gesture-based interactions for mobile or in-field devices. Combines with AR overlays via BitNet.

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

class PanelType(Enum):
    """Enumeration of smart panel types."""
    SUMMARY = "summary"  # Summary panel
    DECISION = "decision"  # Decision panel
    CONTROL = "control"  # Control panel
    STATUS = "status"  # Status panel
    ALERT = "alert"  # Alert panel
    CUSTOM = "custom"  # Custom panel type

class PanelSize(Enum):
    """Enumeration of panel sizes."""
    COMPACT = "compact"  # Compact size
    STANDARD = "standard"  # Standard size
    EXPANDED = "expanded"  # Expanded size
    FULL = "full"  # Full size
    CUSTOM = "custom"  # Custom size

class PanelPosition(Enum):
    """Enumeration of panel positions."""
    TOP = "top"  # Top of the screen
    BOTTOM = "bottom"  # Bottom of the screen
    LEFT = "left"  # Left side of the screen
    RIGHT = "right"  # Right side of the screen
    CENTER = "center"  # Center of the screen
    FLOATING = "floating"  # Floating position
    AR_ANCHORED = "ar_anchored"  # Anchored to AR object
    CUSTOM = "custom"  # Custom position

class InteractionMode(Enum):
    """Enumeration of interaction modes."""
    TOUCH = "touch"  # Touch interaction
    VOICE = "voice"  # Voice interaction
    GESTURE = "gesture"  # Gesture interaction
    GAZE = "gaze"  # Gaze interaction
    PROXIMITY = "proximity"  # Proximity interaction
    MULTI_MODAL = "multi_modal"  # Multiple interaction modes
    CUSTOM = "custom"  # Custom interaction mode

class GestureType(Enum):
    """Enumeration of gesture types."""
    TAP = "tap"  # Tap gesture
    DOUBLE_TAP = "double_tap"  # Double tap gesture
    SWIPE = "swipe"  # Swipe gesture
    PINCH = "pinch"  # Pinch gesture
    ROTATE = "rotate"  # Rotate gesture
    WAVE = "wave"  # Wave gesture
    POINT = "point"  # Point gesture
    GRAB = "grab"  # Grab gesture
    CUSTOM = "custom"  # Custom gesture

class VoiceCommand(Enum):
    """Enumeration of voice commands."""
    OPEN = "open"  # Open command
    CLOSE = "close"  # Close command
    EXPAND = "expand"  # Expand command
    COLLAPSE = "collapse"  # Collapse command
    CONFIRM = "confirm"  # Confirm command
    CANCEL = "cancel"  # Cancel command
    NEXT = "next"  # Next command
    PREVIOUS = "previous"  # Previous command
    CUSTOM = "custom"  # Custom command

class ARDisplayMode(Enum):
    """Enumeration of AR display modes."""
    WORLD_LOCKED = "world_locked"  # Locked to world coordinates
    BODY_LOCKED = "body_locked"  # Locked to user's body
    OBJECT_LOCKED = "object_locked"  # Locked to a physical object
    FLOATING = "floating"  # Floating in space
    CUSTOM = "custom"  # Custom display mode

class SmartPanel:
    """Represents a smart panel for mobile, voice, and AR interactions."""
    
    def __init__(self,
                 panel_id: str,
                 panel_type: PanelType,
                 capsule_id: Optional[str],
                 title: str,
                 content: str,
                 size: PanelSize = PanelSize.STANDARD,
                 position: PanelPosition = PanelPosition.FLOATING,
                 interaction_modes: List[InteractionMode] = None,
                 ar_display_mode: Optional[ARDisplayMode] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a smart panel.
        
        Args:
            panel_id: Unique identifier for this panel
            panel_type: Type of panel
            capsule_id: Optional ID of the capsule this panel is associated with
            title: Title of the panel
            content: Content of the panel
            size: Size of the panel
            position: Position of the panel
            interaction_modes: List of interaction modes for this panel
            ar_display_mode: Optional AR display mode for this panel
            metadata: Additional metadata for this panel
        """
        self.panel_id = panel_id
        self.panel_type = panel_type
        self.capsule_id = capsule_id
        self.title = title
        self.content = content
        self.size = size
        self.position = position
        self.interaction_modes = interaction_modes or [InteractionMode.TOUCH]
        self.ar_display_mode = ar_display_mode
        self.metadata = metadata or {}
        self.is_visible = False
        self.is_expanded = False
        self.is_interactive = True
        self.position_data: Dict[str, Any] = {}  # Position-specific data
        self.ar_anchor_id: Optional[str] = None  # ID of AR anchor
        self.voice_commands: Dict[VoiceCommand, Callable] = {}  # Voice command handlers
        self.gesture_handlers: Dict[GestureType, Callable] = {}  # Gesture handlers
        self.actions: List[Dict[str, Any]] = []  # Available actions
        self.last_update = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this panel to a dictionary representation."""
        return {
            "panel_id": self.panel_id,
            "panel_type": self.panel_type.value,
            "capsule_id": self.capsule_id,
            "title": self.title,
            "content": self.content,
            "size": self.size.value,
            "position": self.position.value,
            "interaction_modes": [mode.value for mode in self.interaction_modes],
            "ar_display_mode": self.ar_display_mode.value if self.ar_display_mode else None,
            "is_visible": self.is_visible,
            "is_expanded": self.is_expanded,
            "is_interactive": self.is_interactive,
            "position_data": self.position_data,
            "ar_anchor_id": self.ar_anchor_id,
            "actions": self.actions,
            "last_update": self.last_update,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SmartPanel':
        """Create a smart panel from a dictionary representation."""
        panel = cls(
            panel_id=data["panel_id"],
            panel_type=PanelType(data["panel_type"]),
            capsule_id=data["capsule_id"],
            title=data["title"],
            content=data["content"],
            size=PanelSize(data["size"]),
            position=PanelPosition(data["position"]),
            interaction_modes=[InteractionMode(mode) for mode in data["interaction_modes"]],
            ar_display_mode=ARDisplayMode(data["ar_display_mode"]) if data.get("ar_display_mode") else None,
            metadata=data.get("metadata", {})
        )
        
        panel.is_visible = data.get("is_visible", False)
        panel.is_expanded = data.get("is_expanded", False)
        panel.is_interactive = data.get("is_interactive", True)
        panel.position_data = data.get("position_data", {})
        panel.ar_anchor_id = data.get("ar_anchor_id")
        panel.actions = data.get("actions", [])
        panel.last_update = data.get("last_update", time.time())
        
        return panel

class PanelAction:
    """Represents an action that can be performed on a smart panel."""
    
    def __init__(self,
                 action_id: str,
                 label: str,
                 icon: Optional[str] = None,
                 handler: Optional[Callable] = None,
                 voice_trigger: Optional[str] = None,
                 gesture_trigger: Optional[GestureType] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a panel action.
        
        Args:
            action_id: Unique identifier for this action
            label: Label for the action
            icon: Optional icon for the action
            handler: Optional handler function for the action
            voice_trigger: Optional voice trigger for the action
            gesture_trigger: Optional gesture trigger for the action
            metadata: Additional metadata for this action
        """
        self.action_id = action_id
        self.label = label
        self.icon = icon
        self.handler = handler
        self.voice_trigger = voice_trigger
        self.gesture_trigger = gesture_trigger
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this action to a dictionary representation."""
        return {
            "action_id": self.action_id,
            "label": self.label,
            "icon": self.icon,
            "voice_trigger": self.voice_trigger,
            "gesture_trigger": self.gesture_trigger.value if self.gesture_trigger else None,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PanelAction':
        """Create a panel action from a dictionary representation."""
        return cls(
            action_id=data["action_id"],
            label=data["label"],
            icon=data.get("icon"),
            voice_trigger=data.get("voice_trigger"),
            gesture_trigger=GestureType(data["gesture_trigger"]) if data.get("gesture_trigger") else None,
            metadata=data.get("metadata", {})
        )

class ARAnchor:
    """Represents an AR anchor for smart panels."""
    
    def __init__(self,
                 anchor_id: str,
                 anchor_type: str,
                 position: Tuple[float, float, float],
                 rotation: Tuple[float, float, float, float] = (0, 0, 0, 1),
                 scale: Tuple[float, float, float] = (1, 1, 1),
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an AR anchor.
        
        Args:
            anchor_id: Unique identifier for this anchor
            anchor_type: Type of anchor (e.g., "image", "object", "plane", "face")
            position: Position of the anchor (x, y, z)
            rotation: Rotation of the anchor as quaternion (x, y, z, w)
            scale: Scale of the anchor (x, y, z)
            metadata: Additional metadata for this anchor
        """
        self.anchor_id = anchor_id
        self.anchor_type = anchor_type
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.metadata = metadata or {}
        self.is_tracked = False
        self.confidence = 0.0
        self.attached_panels: List[str] = []  # List of panel IDs attached to this anchor
        self.last_update = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this anchor to a dictionary representation."""
        return {
            "anchor_id": self.anchor_id,
            "anchor_type": self.anchor_type,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "is_tracked": self.is_tracked,
            "confidence": self.confidence,
            "attached_panels": self.attached_panels,
            "last_update": self.last_update,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ARAnchor':
        """Create an AR anchor from a dictionary representation."""
        anchor = cls(
            anchor_id=data["anchor_id"],
            anchor_type=data["anchor_type"],
            position=data["position"],
            rotation=data.get("rotation", (0, 0, 0, 1)),
            scale=data.get("scale", (1, 1, 1)),
            metadata=data.get("metadata", {})
        )
        
        anchor.is_tracked = data.get("is_tracked", False)
        anchor.confidence = data.get("confidence", 0.0)
        anchor.attached_panels = data.get("attached_panels", [])
        anchor.last_update = data.get("last_update", time.time())
        
        return anchor

class VoiceCommandRecognizer:
    """Handles voice command recognition for smart panels."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the voice command recognizer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_listening = False
        self.commands: Dict[str, Dict[str, Any]] = {}  # Map of command phrases to handlers
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        
    def start_listening(self) -> bool:
        """
        Start listening for voice commands.
        
        Returns:
            True if listening was started, False if already listening
        """
        if self.is_listening:
            return False
            
        self.is_listening = True
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_listening_started"
        })
        
        return True
    
    def stop_listening(self) -> bool:
        """
        Stop listening for voice commands.
        
        Returns:
            True if listening was stopped, False if not listening
        """
        if not self.is_listening:
            return False
            
        self.is_listening = False
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "voice_listening_stopped"
        })
        
        return True
    
    def register_command(self,
                       command_phrase: str,
                       handler: Callable,
                       panel_id: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a voice command.
        
        Args:
            command_phrase: Phrase that triggers this command
            handler: Handler function for this command
            panel_id: Optional ID of the panel this command is associated with
            metadata: Additional metadata for this command
        """
        self.commands[command_phrase.lower()] = {
            "handler": handler,
            "panel_id": panel_id,
            "metadata": metadata or {}
        }
        
    def unregister_command(self, command_phrase: str) -> bool:
        """
        Unregister a voice command.
        
        Args:
            command_phrase: Phrase of the command to unregister
            
        Returns:
            True if the command was unregistered, False if not found
        """
        command_phrase = command_phrase.lower()
        if command_phrase not in self.commands:
            return False
            
        del self.commands[command_phrase]
        return True
    
    def process_speech(self, text: str) -> bool:
        """
        Process speech text and trigger commands if recognized.
        
        Args:
            text: Speech text to process
            
        Returns:
            True if a command was recognized and processed, False otherwise
        """
        if not self.is_listening:
            return False
            
        text = text.lower()
        
        # Check for exact matches
        if text in self.commands:
            command = self.commands[text]
            
            # Dispatch event
            self._dispatch_event({
                "event_type": "voice_command_recognized",
                "command": text,
                "panel_id": command.get("panel_id")
            })
            
            # Call handler
            try:
                command["handler"](text)
                return True
            except Exception as e:
                self.logger.error(f"Error in voice command handler: {e}")
                return False
                
        # Check for partial matches
        for command_phrase, command in self.commands.items():
            if command_phrase in text:
                # Dispatch event
                self._dispatch_event({
                    "event_type": "voice_command_recognized",
                    "command": command_phrase,
                    "panel_id": command.get("panel_id")
                })
                
                # Call handler
                try:
                    command["handler"](text)
                    return True
                except Exception as e:
                    self.logger.error(f"Error in voice command handler: {e}")
                    return False
                    
        return False
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for voice command events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for voice command events.
        
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
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in event listener: {e}")

class GestureRecognizer:
    """Handles gesture recognition for smart panels."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the gesture recognizer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.gesture_handlers: Dict[GestureType, List[Dict[str, Any]]] = {}
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        
        # Initialize gesture handlers
        for gesture_type in GestureType:
            self.gesture_handlers[gesture_type] = []
            
    def start(self) -> bool:
        """
        Start gesture recognition.
        
        Returns:
            True if recognition was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "gesture_recognition_started"
        })
        
        return True
    
    def stop(self) -> bool:
        """
        Stop gesture recognition.
        
        Returns:
            True if recognition was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "gesture_recognition_stopped"
        })
        
        return True
    
    def register_gesture_handler(self,
                               gesture_type: GestureType,
                               handler: Callable,
                               panel_id: Optional[str] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a gesture handler.
        
        Args:
            gesture_type: Type of gesture
            handler: Handler function for this gesture
            panel_id: Optional ID of the panel this handler is associated with
            metadata: Additional metadata for this handler
        """
        self.gesture_handlers[gesture_type].append({
            "handler": handler,
            "panel_id": panel_id,
            "metadata": metadata or {}
        })
        
    def unregister_gesture_handler(self,
                                 gesture_type: GestureType,
                                 handler: Callable) -> bool:
        """
        Unregister a gesture handler.
        
        Args:
            gesture_type: Type of gesture
            handler: Handler function to unregister
            
        Returns:
            True if the handler was unregistered, False if not found
        """
        if gesture_type not in self.gesture_handlers:
            return False
            
        handlers = self.gesture_handlers[gesture_type]
        for i, h in enumerate(handlers):
            if h["handler"] == handler:
                handlers.pop(i)
                return True
                
        return False
    
    def process_gesture(self,
                      gesture_type: GestureType,
                      gesture_data: Dict[str, Any]) -> bool:
        """
        Process a recognized gesture and trigger handlers.
        
        Args:
            gesture_type: Type of gesture
            gesture_data: Data associated with the gesture
            
        Returns:
            True if the gesture was processed by at least one handler, False otherwise
        """
        if not self.is_active or gesture_type not in self.gesture_handlers:
            return False
            
        handlers = self.gesture_handlers[gesture_type]
        if not handlers:
            return False
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "gesture_recognized",
            "gesture_type": gesture_type.value,
            "gesture_data": gesture_data
        })
        
        # Call handlers
        processed = False
        for handler_info in handlers:
            try:
                handler_info["handler"](gesture_type, gesture_data)
                processed = True
            except Exception as e:
                self.logger.error(f"Error in gesture handler: {e}")
                
        return processed
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for gesture events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for gesture events.
        
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
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in event listener: {e}")

class ARManager:
    """Manages AR anchors and overlays for smart panels."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AR manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.anchors: Dict[str, ARAnchor] = {}
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        
    def start(self) -> bool:
        """
        Start AR tracking.
        
        Returns:
            True if tracking was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "ar_tracking_started"
        })
        
        return True
    
    def stop(self) -> bool:
        """
        Stop AR tracking.
        
        Returns:
            True if tracking was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "ar_tracking_stopped"
        })
        
        return True
    
    def create_anchor(self,
                    anchor_type: str,
                    position: Tuple[float, float, float],
                    rotation: Tuple[float, float, float, float] = (0, 0, 0, 1),
                    scale: Tuple[float, float, float] = (1, 1, 1),
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create an AR anchor.
        
        Args:
            anchor_type: Type of anchor (e.g., "image", "object", "plane", "face")
            position: Position of the anchor (x, y, z)
            rotation: Rotation of the anchor as quaternion (x, y, z, w)
            scale: Scale of the anchor (x, y, z)
            metadata: Additional metadata for this anchor
            
        Returns:
            ID of the created anchor
        """
        anchor_id = str(uuid.uuid4())
        
        self.anchors[anchor_id] = ARAnchor(
            anchor_id=anchor_id,
            anchor_type=anchor_type,
            position=position,
            rotation=rotation,
            scale=scale,
            metadata=metadata or {}
        )
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "anchor_created",
            "anchor_id": anchor_id,
            "anchor_type": anchor_type,
            "position": position
        })
        
        return anchor_id
    
    def remove_anchor(self, anchor_id: str) -> bool:
        """
        Remove an AR anchor.
        
        Args:
            anchor_id: ID of the anchor to remove
            
        Returns:
            True if the anchor was removed, False if not found
        """
        if anchor_id not in self.anchors:
            return False
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "anchor_removed",
            "anchor_id": anchor_id
        })
        
        del self.anchors[anchor_id]
        return True
    
    def update_anchor(self,
                    anchor_id: str,
                    position: Optional[Tuple[float, float, float]] = None,
                    rotation: Optional[Tuple[float, float, float, float]] = None,
                    scale: Optional[Tuple[float, float, float]] = None,
                    is_tracked: Optional[bool] = None,
                    confidence: Optional[float] = None) -> bool:
        """
        Update an AR anchor.
        
        Args:
            anchor_id: ID of the anchor to update
            position: Optional new position of the anchor (x, y, z)
            rotation: Optional new rotation of the anchor as quaternion (x, y, z, w)
            scale: Optional new scale of the anchor (x, y, z)
            is_tracked: Optional new tracking state
            confidence: Optional new tracking confidence
            
        Returns:
            True if the anchor was updated, False if not found
        """
        if anchor_id not in self.anchors:
            return False
            
        anchor = self.anchors[anchor_id]
        
        # Update anchor properties
        if position is not None:
            anchor.position = position
            
        if rotation is not None:
            anchor.rotation = rotation
            
        if scale is not None:
            anchor.scale = scale
            
        if is_tracked is not None:
            anchor.is_tracked = is_tracked
            
        if confidence is not None:
            anchor.confidence = confidence
            
        anchor.last_update = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "anchor_updated",
            "anchor_id": anchor_id,
            "position": anchor.position,
            "is_tracked": anchor.is_tracked,
            "confidence": anchor.confidence
        })
        
        return True
    
    def attach_panel_to_anchor(self, panel_id: str, anchor_id: str) -> bool:
        """
        Attach a smart panel to an AR anchor.
        
        Args:
            panel_id: ID of the panel to attach
            anchor_id: ID of the anchor to attach to
            
        Returns:
            True if the panel was attached, False if the anchor was not found
        """
        if anchor_id not in self.anchors:
            return False
            
        anchor = self.anchors[anchor_id]
        
        # Add panel to anchor's attached panels
        if panel_id not in anchor.attached_panels:
            anchor.attached_panels.append(panel_id)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_attached_to_anchor",
            "panel_id": panel_id,
            "anchor_id": anchor_id
        })
        
        return True
    
    def detach_panel_from_anchor(self, panel_id: str, anchor_id: str) -> bool:
        """
        Detach a smart panel from an AR anchor.
        
        Args:
            panel_id: ID of the panel to detach
            anchor_id: ID of the anchor to detach from
            
        Returns:
            True if the panel was detached, False if the anchor was not found or the panel was not attached
        """
        if anchor_id not in self.anchors:
            return False
            
        anchor = self.anchors[anchor_id]
        
        # Remove panel from anchor's attached panels
        if panel_id in anchor.attached_panels:
            anchor.attached_panels.remove(panel_id)
            
            # Dispatch event
            self._dispatch_event({
                "event_type": "panel_detached_from_anchor",
                "panel_id": panel_id,
                "anchor_id": anchor_id
            })
            
            return True
        else:
            return False
    
    def get_anchor(self, anchor_id: str) -> Optional[ARAnchor]:
        """
        Get an AR anchor by ID.
        
        Args:
            anchor_id: ID of the anchor
            
        Returns:
            The anchor, or None if not found
        """
        return self.anchors.get(anchor_id)
    
    def get_all_anchors(self) -> List[ARAnchor]:
        """
        Get all AR anchors.
        
        Returns:
            List of all anchors
        """
        return list(self.anchors.values())
    
    def get_tracked_anchors(self) -> List[ARAnchor]:
        """
        Get all tracked AR anchors.
        
        Returns:
            List of all tracked anchors
        """
        return [anchor for anchor in self.anchors.values() if anchor.is_tracked]
    
    def get_anchors_by_type(self, anchor_type: str) -> List[ARAnchor]:
        """
        Get all AR anchors of a specific type.
        
        Args:
            anchor_type: Type of anchors to get
            
        Returns:
            List of all anchors of the specified type
        """
        return [anchor for anchor in self.anchors.values() if anchor.anchor_type == anchor_type]
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for AR events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for AR events.
        
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
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in event listener: {e}")

class SmartPanelManager:
    """
    Provides capsule summary cards with voice-first triggers, decision previews, 
    or gesture-based interactions for mobile or in-field devices.
    
    This class provides:
    - Smart panel creation and management
    - Voice command recognition
    - Gesture recognition
    - AR integration
    - Multi-modal interaction support
    - Integration with the Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Smart Panel Manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.panels: Dict[str, SmartPanel] = {}
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        
        # Initialize sub-components
        self.voice_recognizer = VoiceCommandRecognizer(config.get("voice_config"))
        self.gesture_recognizer = GestureRecognizer(config.get("gesture_config"))
        self.ar_manager = ARManager(config.get("ar_config"))
        
        # Connect event listeners
        self.voice_recognizer.add_event_listener(self._handle_voice_event)
        self.gesture_recognizer.add_event_listener(self._handle_gesture_event)
        self.ar_manager.add_event_listener(self._handle_ar_event)
        
    def create_panel(self,
                   panel_type: PanelType,
                   capsule_id: Optional[str],
                   title: str,
                   content: str,
                   size: PanelSize = PanelSize.STANDARD,
                   position: PanelPosition = PanelPosition.FLOATING,
                   interaction_modes: List[InteractionMode] = None,
                   ar_display_mode: Optional[ARDisplayMode] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a smart panel.
        
        Args:
            panel_type: Type of panel
            capsule_id: Optional ID of the capsule this panel is associated with
            title: Title of the panel
            content: Content of the panel
            size: Size of the panel
            position: Position of the panel
            interaction_modes: List of interaction modes for this panel
            ar_display_mode: Optional AR display mode for this panel
            metadata: Additional metadata for this panel
            
        Returns:
            ID of the created panel
        """
        panel_id = str(uuid.uuid4())
        
        self.panels[panel_id] = SmartPanel(
            panel_id=panel_id,
            panel_type=panel_type,
            capsule_id=capsule_id,
            title=title,
            content=content,
            size=size,
            position=position,
            interaction_modes=interaction_modes or [InteractionMode.TOUCH],
            ar_display_mode=ar_display_mode,
            metadata=metadata or {}
        )
        
        # Register default voice commands if voice interaction is enabled
        if InteractionMode.VOICE in (interaction_modes or [InteractionMode.TOUCH]):
            self._register_default_voice_commands(panel_id)
            
        # Register default gesture handlers if gesture interaction is enabled
        if InteractionMode.GESTURE in (interaction_modes or [InteractionMode.TOUCH]):
            self._register_default_gesture_handlers(panel_id)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_created",
            "panel_id": panel_id,
            "panel_type": panel_type.value,
            "capsule_id": capsule_id
        })
        
        return panel_id
    
    def remove_panel(self, panel_id: str) -> bool:
        """
        Remove a smart panel.
        
        Args:
            panel_id: ID of the panel to remove
            
        Returns:
            True if the panel was removed, False if not found
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Detach from AR anchor if attached
        if panel.ar_anchor_id:
            self.ar_manager.detach_panel_from_anchor(panel_id, panel.ar_anchor_id)
            
        # Unregister voice commands
        if InteractionMode.VOICE in panel.interaction_modes:
            self._unregister_voice_commands(panel_id)
            
        # Unregister gesture handlers
        if InteractionMode.GESTURE in panel.interaction_modes:
            self._unregister_gesture_handlers(panel_id)
            
        # Remove panel
        del self.panels[panel_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_removed",
            "panel_id": panel_id
        })
        
        return True
    
    def show_panel(self, panel_id: str) -> bool:
        """
        Show a smart panel.
        
        Args:
            panel_id: ID of the panel to show
            
        Returns:
            True if the panel was shown, False if not found
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Skip if already visible
        if panel.is_visible:
            return True
            
        # Show panel
        panel.is_visible = True
        panel.last_update = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_shown",
            "panel_id": panel_id
        })
        
        return True
    
    def hide_panel(self, panel_id: str) -> bool:
        """
        Hide a smart panel.
        
        Args:
            panel_id: ID of the panel to hide
            
        Returns:
            True if the panel was hidden, False if not found
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Skip if already hidden
        if not panel.is_visible:
            return True
            
        # Hide panel
        panel.is_visible = False
        panel.last_update = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_hidden",
            "panel_id": panel_id
        })
        
        return True
    
    def expand_panel(self, panel_id: str) -> bool:
        """
        Expand a smart panel.
        
        Args:
            panel_id: ID of the panel to expand
            
        Returns:
            True if the panel was expanded, False if not found
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Skip if already expanded
        if panel.is_expanded:
            return True
            
        # Expand panel
        panel.is_expanded = True
        panel.last_update = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_expanded",
            "panel_id": panel_id
        })
        
        return True
    
    def collapse_panel(self, panel_id: str) -> bool:
        """
        Collapse a smart panel.
        
        Args:
            panel_id: ID of the panel to collapse
            
        Returns:
            True if the panel was collapsed, False if not found
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Skip if already collapsed
        if not panel.is_expanded:
            return True
            
        # Collapse panel
        panel.is_expanded = False
        panel.last_update = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_collapsed",
            "panel_id": panel_id
        })
        
        return True
    
    def update_panel_content(self,
                           panel_id: str,
                           title: Optional[str] = None,
                           content: Optional[str] = None) -> bool:
        """
        Update the content of a smart panel.
        
        Args:
            panel_id: ID of the panel to update
            title: Optional new title for the panel
            content: Optional new content for the panel
            
        Returns:
            True if the panel was updated, False if not found
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Update panel content
        if title is not None:
            panel.title = title
            
        if content is not None:
            panel.content = content
            
        panel.last_update = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_content_updated",
            "panel_id": panel_id,
            "title": panel.title,
            "content": panel.content
        })
        
        return True
    
    def update_panel_position(self,
                            panel_id: str,
                            position: Optional[PanelPosition] = None,
                            position_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update the position of a smart panel.
        
        Args:
            panel_id: ID of the panel to update
            position: Optional new position for the panel
            position_data: Optional position-specific data
            
        Returns:
            True if the panel was updated, False if not found
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Update panel position
        if position is not None:
            panel.position = position
            
        if position_data is not None:
            panel.position_data.update(position_data)
            
        panel.last_update = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_position_updated",
            "panel_id": panel_id,
            "position": panel.position.value,
            "position_data": panel.position_data
        })
        
        return True
    
    def add_panel_action(self,
                       panel_id: str,
                       label: str,
                       handler: Callable,
                       icon: Optional[str] = None,
                       voice_trigger: Optional[str] = None,
                       gesture_trigger: Optional[GestureType] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add an action to a smart panel.
        
        Args:
            panel_id: ID of the panel to add the action to
            label: Label for the action
            handler: Handler function for the action
            icon: Optional icon for the action
            voice_trigger: Optional voice trigger for the action
            gesture_trigger: Optional gesture trigger for the action
            metadata: Additional metadata for this action
            
        Returns:
            ID of the created action, or None if the panel was not found
        """
        if panel_id not in self.panels:
            return None
            
        panel = self.panels[panel_id]
        
        # Create action ID
        action_id = str(uuid.uuid4())
        
        # Create action
        action = {
            "action_id": action_id,
            "label": label,
            "icon": icon,
            "voice_trigger": voice_trigger,
            "gesture_trigger": gesture_trigger.value if gesture_trigger else None,
            "metadata": metadata or {}
        }
        
        # Add action to panel
        panel.actions.append(action)
        
        # Register voice command if provided
        if voice_trigger and InteractionMode.VOICE in panel.interaction_modes:
            self.voice_recognizer.register_command(
                command_phrase=voice_trigger,
                handler=handler,
                panel_id=panel_id,
                metadata={"action_id": action_id}
            )
            
        # Register gesture handler if provided
        if gesture_trigger and InteractionMode.GESTURE in panel.interaction_modes:
            self.gesture_recognizer.register_gesture_handler(
                gesture_type=gesture_trigger,
                handler=lambda gesture_type, gesture_data: handler(),
                panel_id=panel_id,
                metadata={"action_id": action_id}
            )
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_action_added",
            "panel_id": panel_id,
            "action_id": action_id,
            "label": label
        })
        
        return action_id
    
    def remove_panel_action(self, panel_id: str, action_id: str) -> bool:
        """
        Remove an action from a smart panel.
        
        Args:
            panel_id: ID of the panel to remove the action from
            action_id: ID of the action to remove
            
        Returns:
            True if the action was removed, False if not found
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Find action
        action_index = None
        action = None
        
        for i, a in enumerate(panel.actions):
            if a["action_id"] == action_id:
                action_index = i
                action = a
                break
                
        if action_index is None:
            return False
            
        # Unregister voice command if provided
        if action.get("voice_trigger") and InteractionMode.VOICE in panel.interaction_modes:
            self.voice_recognizer.unregister_command(action["voice_trigger"])
            
        # Remove action
        panel.actions.pop(action_index)
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "panel_action_removed",
            "panel_id": panel_id,
            "action_id": action_id
        })
        
        return True
    
    def attach_panel_to_ar_anchor(self, panel_id: str, anchor_id: str) -> bool:
        """
        Attach a smart panel to an AR anchor.
        
        Args:
            panel_id: ID of the panel to attach
            anchor_id: ID of the anchor to attach to
            
        Returns:
            True if the panel was attached, False if the panel or anchor was not found
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Detach from previous anchor if attached
        if panel.ar_anchor_id:
            self.ar_manager.detach_panel_from_anchor(panel_id, panel.ar_anchor_id)
            
        # Attach to new anchor
        if self.ar_manager.attach_panel_to_anchor(panel_id, anchor_id):
            panel.ar_anchor_id = anchor_id
            
            # Set AR display mode if not already set
            if not panel.ar_display_mode:
                panel.ar_display_mode = ARDisplayMode.OBJECT_LOCKED
                
            # Dispatch event
            self._dispatch_event({
                "event_type": "panel_attached_to_ar_anchor",
                "panel_id": panel_id,
                "anchor_id": anchor_id
            })
            
            return True
        else:
            return False
    
    def detach_panel_from_ar_anchor(self, panel_id: str) -> bool:
        """
        Detach a smart panel from its AR anchor.
        
        Args:
            panel_id: ID of the panel to detach
            
        Returns:
            True if the panel was detached, False if the panel was not found or not attached
        """
        if panel_id not in self.panels:
            return False
            
        panel = self.panels[panel_id]
        
        # Skip if not attached
        if not panel.ar_anchor_id:
            return True
            
        # Detach from anchor
        anchor_id = panel.ar_anchor_id
        if self.ar_manager.detach_panel_from_anchor(panel_id, anchor_id):
            panel.ar_anchor_id = None
            
            # Dispatch event
            self._dispatch_event({
                "event_type": "panel_detached_from_ar_anchor",
                "panel_id": panel_id,
                "anchor_id": anchor_id
            })
            
            return True
        else:
            return False
    
    def process_speech(self, text: str) -> bool:
        """
        Process speech text and trigger voice commands.
        
        Args:
            text: Speech text to process
            
        Returns:
            True if a command was recognized and processed, False otherwise
        """
        return self.voice_recognizer.process_speech(text)
    
    def process_gesture(self, gesture_type: GestureType, gesture_data: Dict[str, Any]) -> bool:
        """
        Process a recognized gesture and trigger handlers.
        
        Args:
            gesture_type: Type of gesture
            gesture_data: Data associated with the gesture
            
        Returns:
            True if the gesture was processed by at least one handler, False otherwise
        """
        return self.gesture_recognizer.process_gesture(gesture_type, gesture_data)
    
    def get_panel(self, panel_id: str) -> Optional[SmartPanel]:
        """
        Get a smart panel by ID.
        
        Args:
            panel_id: ID of the panel
            
        Returns:
            The panel, or None if not found
        """
        return self.panels.get(panel_id)
    
    def get_all_panels(self) -> List[SmartPanel]:
        """
        Get all smart panels.
        
        Returns:
            List of all panels
        """
        return list(self.panels.values())
    
    def get_visible_panels(self) -> List[SmartPanel]:
        """
        Get all visible smart panels.
        
        Returns:
            List of all visible panels
        """
        return [panel for panel in self.panels.values() if panel.is_visible]
    
    def get_panels_by_type(self, panel_type: PanelType) -> List[SmartPanel]:
        """
        Get all smart panels of a specific type.
        
        Args:
            panel_type: Type of panels to get
            
        Returns:
            List of all panels of the specified type
        """
        return [panel for panel in self.panels.values() if panel.panel_type == panel_type]
    
    def get_panels_by_capsule(self, capsule_id: str) -> List[SmartPanel]:
        """
        Get all smart panels for a specific capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            List of all panels for the specified capsule
        """
        return [panel for panel in self.panels.values() if panel.capsule_id == capsule_id]
    
    def get_panel_css(self, panel_id: str) -> Optional[Dict[str, str]]:
        """
        Get CSS styles for a smart panel.
        
        Args:
            panel_id: ID of the panel
            
        Returns:
            CSS styles dictionary, or None if the panel was not found
        """
        if panel_id not in self.panels:
            return None
            
        panel = self.panels[panel_id]
        styles = {}
        
        # Base styles
        styles["position"] = "absolute"
        
        # Size styles
        if panel.size == PanelSize.COMPACT:
            styles["width"] = "200px"
            styles["height"] = "auto"
            styles["min-height"] = "60px"
        elif panel.size == PanelSize.STANDARD:
            styles["width"] = "300px"
            styles["height"] = "auto"
            styles["min-height"] = "120px"
        elif panel.size == PanelSize.EXPANDED:
            styles["width"] = "400px"
            styles["height"] = "auto"
            styles["min-height"] = "200px"
        elif panel.size == PanelSize.FULL:
            styles["width"] = "100%"
            styles["height"] = "100%"
            
        # Position styles
        if panel.position == PanelPosition.TOP:
            styles["top"] = "0"
            styles["left"] = "50%"
            styles["transform"] = "translateX(-50%)"
        elif panel.position == PanelPosition.BOTTOM:
            styles["bottom"] = "0"
            styles["left"] = "50%"
            styles["transform"] = "translateX(-50%)"
        elif panel.position == PanelPosition.LEFT:
            styles["left"] = "0"
            styles["top"] = "50%"
            styles["transform"] = "translateY(-50%)"
        elif panel.position == PanelPosition.RIGHT:
            styles["right"] = "0"
            styles["top"] = "50%"
            styles["transform"] = "translateY(-50%)"
        elif panel.position == PanelPosition.CENTER:
            styles["top"] = "50%"
            styles["left"] = "50%"
            styles["transform"] = "translate(-50%, -50%)"
        elif panel.position == PanelPosition.FLOATING:
            # Use position data if available
            if "x" in panel.position_data and "y" in panel.position_data:
                styles["left"] = f"{panel.position_data['x']}px"
                styles["top"] = f"{panel.position_data['y']}px"
            else:
                styles["left"] = "20px"
                styles["top"] = "20px"
                
        # Visibility styles
        if not panel.is_visible:
            styles["display"] = "none"
            
        # Expanded styles
        if panel.is_expanded:
            if panel.size == PanelSize.COMPACT:
                styles["width"] = "300px"
                styles["min-height"] = "120px"
            elif panel.size == PanelSize.STANDARD:
                styles["width"] = "400px"
                styles["min-height"] = "200px"
            elif panel.size == PanelSize.EXPANDED:
                styles["width"] = "500px"
                styles["min-height"] = "300px"
                
        # Panel type styles
        if panel.panel_type == PanelType.SUMMARY:
            styles["background-color"] = "#f8f9fa"
            styles["border-left"] = "4px solid #007bff"
        elif panel.panel_type == PanelType.DECISION:
            styles["background-color"] = "#fff3cd"
            styles["border-left"] = "4px solid #ffc107"
        elif panel.panel_type == PanelType.CONTROL:
            styles["background-color"] = "#d1e7dd"
            styles["border-left"] = "4px solid #198754"
        elif panel.panel_type == PanelType.STATUS:
            styles["background-color"] = "#cfe2ff"
            styles["border-left"] = "4px solid #0d6efd"
        elif panel.panel_type == PanelType.ALERT:
            styles["background-color"] = "#f8d7da"
            styles["border-left"] = "4px solid #dc3545"
            
        # Common styles
        styles["border-radius"] = "8px"
        styles["box-shadow"] = "0 4px 8px rgba(0, 0, 0, 0.1)"
        styles["padding"] = "16px"
        styles["font-family"] = "system-ui, -apple-system, sans-serif"
        styles["transition"] = "all 0.3s ease"
        styles["z-index"] = "1000"
        
        return styles
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for smart panel events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for smart panel events.
        
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
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in event listener: {e}")
                
    def _handle_voice_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle voice events from the voice recognizer.
        
        Args:
            event_data: Voice event data
        """
        # Forward event to listeners
        self._dispatch_event({
            "event_type": f"voice_{event_data['event_type']}",
            **event_data
        })
        
    def _handle_gesture_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle gesture events from the gesture recognizer.
        
        Args:
            event_data: Gesture event data
        """
        # Forward event to listeners
        self._dispatch_event({
            "event_type": f"gesture_{event_data['event_type']}",
            **event_data
        })
        
    def _handle_ar_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle AR events from the AR manager.
        
        Args:
            event_data: AR event data
        """
        # Forward event to listeners
        self._dispatch_event({
            "event_type": f"ar_{event_data['event_type']}",
            **event_data
        })
        
    def _register_default_voice_commands(self, panel_id: str) -> None:
        """
        Register default voice commands for a panel.
        
        Args:
            panel_id: ID of the panel
        """
        panel = self.panels[panel_id]
        
        # Register open/show command
        self.voice_recognizer.register_command(
            command_phrase=f"show {panel.title}",
            handler=lambda text: self.show_panel(panel_id),
            panel_id=panel_id
        )
        
        # Register close/hide command
        self.voice_recognizer.register_command(
            command_phrase=f"hide {panel.title}",
            handler=lambda text: self.hide_panel(panel_id),
            panel_id=panel_id
        )
        
        # Register expand command
        self.voice_recognizer.register_command(
            command_phrase=f"expand {panel.title}",
            handler=lambda text: self.expand_panel(panel_id),
            panel_id=panel_id
        )
        
        # Register collapse command
        self.voice_recognizer.register_command(
            command_phrase=f"collapse {panel.title}",
            handler=lambda text: self.collapse_panel(panel_id),
            panel_id=panel_id
        )
        
    def _unregister_voice_commands(self, panel_id: str) -> None:
        """
        Unregister voice commands for a panel.
        
        Args:
            panel_id: ID of the panel
        """
        panel = self.panels[panel_id]
        
        # Unregister default commands
        self.voice_recognizer.unregister_command(f"show {panel.title}")
        self.voice_recognizer.unregister_command(f"hide {panel.title}")
        self.voice_recognizer.unregister_command(f"expand {panel.title}")
        self.voice_recognizer.unregister_command(f"collapse {panel.title}")
        
        # Unregister action commands
        for action in panel.actions:
            if action.get("voice_trigger"):
                self.voice_recognizer.unregister_command(action["voice_trigger"])
                
    def _register_default_gesture_handlers(self, panel_id: str) -> None:
        """
        Register default gesture handlers for a panel.
        
        Args:
            panel_id: ID of the panel
        """
        # Register tap gesture for show/hide toggle
        self.gesture_recognizer.register_gesture_handler(
            gesture_type=GestureType.TAP,
            handler=lambda gesture_type, gesture_data: self._handle_tap_gesture(panel_id, gesture_data),
            panel_id=panel_id
        )
        
        # Register double tap gesture for expand/collapse toggle
        self.gesture_recognizer.register_gesture_handler(
            gesture_type=GestureType.DOUBLE_TAP,
            handler=lambda gesture_type, gesture_data: self._handle_double_tap_gesture(panel_id, gesture_data),
            panel_id=panel_id
        )
        
        # Register swipe gesture for navigation
        self.gesture_recognizer.register_gesture_handler(
            gesture_type=GestureType.SWIPE,
            handler=lambda gesture_type, gesture_data: self._handle_swipe_gesture(panel_id, gesture_data),
            panel_id=panel_id
        )
        
    def _unregister_gesture_handlers(self, panel_id: str) -> None:
        """
        Unregister gesture handlers for a panel.
        
        Args:
            panel_id: ID of the panel
        """
        # Find and remove all handlers for this panel
        for gesture_type in GestureType:
            handlers = self.gesture_recognizer.gesture_handlers.get(gesture_type, [])
            for handler_info in list(handlers):
                if handler_info.get("panel_id") == panel_id:
                    self.gesture_recognizer.gesture_handlers[gesture_type].remove(handler_info)
                    
    def _handle_tap_gesture(self, panel_id: str, gesture_data: Dict[str, Any]) -> None:
        """
        Handle tap gesture for a panel.
        
        Args:
            panel_id: ID of the panel
            gesture_data: Gesture data
        """
        panel = self.panels.get(panel_id)
        if not panel:
            return
            
        # Toggle visibility
        if panel.is_visible:
            self.hide_panel(panel_id)
        else:
            self.show_panel(panel_id)
            
    def _handle_double_tap_gesture(self, panel_id: str, gesture_data: Dict[str, Any]) -> None:
        """
        Handle double tap gesture for a panel.
        
        Args:
            panel_id: ID of the panel
            gesture_data: Gesture data
        """
        panel = self.panels.get(panel_id)
        if not panel:
            return
            
        # Toggle expanded state
        if panel.is_expanded:
            self.collapse_panel(panel_id)
        else:
            self.expand_panel(panel_id)
            
    def _handle_swipe_gesture(self, panel_id: str, gesture_data: Dict[str, Any]) -> None:
        """
        Handle swipe gesture for a panel.
        
        Args:
            panel_id: ID of the panel
            gesture_data: Gesture data
        """
        panel = self.panels.get(panel_id)
        if not panel:
            return
            
        # Get swipe direction
        direction = gesture_data.get("direction", "")
        
        # Handle swipe based on direction
        if direction == "left":
            # Move panel to the left
            if panel.position == PanelPosition.FLOATING and "x" in panel.position_data:
                panel.position_data["x"] = max(0, panel.position_data["x"] - 50)
                self.update_panel_position(panel_id, position_data=panel.position_data)
        elif direction == "right":
            # Move panel to the right
            if panel.position == PanelPosition.FLOATING and "x" in panel.position_data:
                panel.position_data["x"] = panel.position_data["x"] + 50
                self.update_panel_position(panel_id, position_data=panel.position_data)
        elif direction == "up":
            # Move panel up
            if panel.position == PanelPosition.FLOATING and "y" in panel.position_data:
                panel.position_data["y"] = max(0, panel.position_data["y"] - 50)
                self.update_panel_position(panel_id, position_data=panel.position_data)
        elif direction == "down":
            # Move panel down
            if panel.position == PanelPosition.FLOATING and "y" in panel.position_data:
                panel.position_data["y"] = panel.position_data["y"] + 50
                self.update_panel_position(panel_id, position_data=panel.position_data)
"""
