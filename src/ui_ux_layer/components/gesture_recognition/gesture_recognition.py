"""
Gesture Recognition System for the Industriverse UI/UX Layer.

This module provides comprehensive gesture recognition capabilities for the Universal Skin
and Agent Capsules, enabling natural and intuitive interaction through hand and body gestures
in industrial environments.

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
import numpy as np
from dataclasses import dataclass

class GestureType(Enum):
    """Enumeration of gesture types."""
    HAND = "hand"  # Hand gestures
    FINGER = "finger"  # Finger gestures
    ARM = "arm"  # Arm gestures
    BODY = "body"  # Full body gestures
    HEAD = "head"  # Head gestures
    FACE = "face"  # Facial gestures
    MULTI_TOUCH = "multi_touch"  # Multi-touch gestures
    CUSTOM = "custom"  # Custom gesture type

class GestureCategory(Enum):
    """Enumeration of gesture categories."""
    NAVIGATION = "navigation"  # Navigation gestures
    SELECTION = "selection"  # Selection gestures
    MANIPULATION = "manipulation"  # Object manipulation gestures
    COMMAND = "command"  # Command gestures
    SYSTEM = "system"  # System control gestures
    INDUSTRIAL = "industrial"  # Industrial-specific gestures
    CUSTOM = "custom"  # Custom gesture category

class HandPose(Enum):
    """Enumeration of common hand poses."""
    OPEN = "open"  # Open hand
    CLOSED = "closed"  # Closed hand (fist)
    POINTING = "pointing"  # Pointing with index finger
    PINCH = "pinch"  # Pinch gesture (thumb and index finger)
    GRAB = "grab"  # Grab gesture (partially closed hand)
    THUMBS_UP = "thumbs_up"  # Thumbs up
    THUMBS_DOWN = "thumbs_down"  # Thumbs down
    VICTORY = "victory"  # Victory sign (V)
    OK = "ok"  # OK sign (circle with thumb and index finger)
    FLAT = "flat"  # Flat hand
    CUSTOM = "custom"  # Custom hand pose

class GestureConfidenceLevel(Enum):
    """Enumeration of gesture confidence levels."""
    LOW = 0  # Low confidence
    MEDIUM = 1  # Medium confidence
    HIGH = 2  # High confidence
    VERY_HIGH = 3  # Very high confidence

@dataclass
class HandJoint:
    """Data class representing a hand joint."""
    joint_id: str  # Joint identifier
    position: Tuple[float, float, float]  # 3D position
    rotation: Optional[Tuple[float, float, float, float]] = None  # Quaternion rotation
    confidence: float = 1.0  # Confidence level (0.0-1.0)

@dataclass
class HandData:
    """Data class representing hand tracking data."""
    hand_id: str  # Hand identifier
    is_left: bool  # Whether it's the left hand
    position: Tuple[float, float, float]  # Palm position
    rotation: Optional[Tuple[float, float, float, float]] = None  # Palm rotation
    joints: Dict[str, HandJoint] = None  # Map of joint ID to joint data
    velocity: Optional[Tuple[float, float, float]] = None  # Velocity vector
    confidence: float = 1.0  # Overall confidence level (0.0-1.0)
    
    def __post_init__(self):
        if self.joints is None:
            self.joints = {}

class GestureRecognitionSystem:
    """
    Provides gesture recognition capabilities for the Industriverse UI/UX Layer.
    
    This class provides:
    - Hand and body gesture recognition
    - Custom gesture definition and training
    - Gesture-based interaction with UI elements and Agent Capsules
    - Industrial-specific gesture recognition
    - Integration with AR/VR systems
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Gesture Recognition System.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.gestures: Dict[str, Dict[str, Any]] = {}  # Map gesture ID to gesture data
        self.active_recognizers: Dict[str, Dict[str, Any]] = {}  # Map recognizer ID to recognizer data
        self.tracked_hands: Dict[str, HandData] = {}  # Map hand ID to hand data
        self.gesture_history: List[Dict[str, Any]] = []  # List of recent recognized gestures
        self.gesture_listeners: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}  # Map gesture ID to listeners
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.update_interval: float = self.config.get("update_interval", 0.033)  # ~30 fps
        
        # Initialize gesture backend (placeholder)
        self.gesture_backend = self._initialize_gesture_backend()
        
        # Load gestures from config
        self._load_gestures_from_config()
        
    def start(self) -> bool:
        """
        Start the Gesture Recognition System.
        
        Returns:
            True if the system was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Start gesture backend (placeholder)
        # self.gesture_backend.start()
        
        # Start update thread
        threading.Thread(target=self._update_loop, daemon=True).start()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "gesture_recognition_system_started"
        })
        
        self.logger.info("Gesture Recognition System started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Gesture Recognition System.
        
        Returns:
            True if the system was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Stop gesture backend (placeholder)
        # self.gesture_backend.stop()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "gesture_recognition_system_stopped"
        })
        
        self.logger.info("Gesture Recognition System stopped.")
        return True
    
    def register_gesture(self,
                       gesture_id: str,
                       gesture_type: GestureType,
                       gesture_category: GestureCategory,
                       description: str,
                       parameters: Dict[str, Any],
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a gesture for recognition.
        
        Args:
            gesture_id: Unique identifier for this gesture
            gesture_type: Type of gesture
            gesture_category: Category of gesture
            description: Human-readable description
            parameters: Gesture-specific parameters
            metadata: Additional metadata for this gesture
            
        Returns:
            True if the gesture was registered, False if already exists
        """
        if gesture_id in self.gestures:
            self.logger.warning(f"Gesture {gesture_id} already exists.")
            return False
            
        self.gestures[gesture_id] = {
            "gesture_id": gesture_id,
            "gesture_type": gesture_type,
            "gesture_category": gesture_category,
            "description": description,
            "parameters": parameters,
            "creation_time": time.time(),
            "last_update_time": time.time(),
            "metadata": metadata or {}
        }
        
        # --- Gesture Backend Interaction (Placeholder) ---
        try:
            # self.gesture_backend.register_gesture(gesture_id, {
            #     "type": gesture_type.value,
            #     "category": gesture_category.value,
            #     "parameters": parameters
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error registering gesture with backend: {e}")
        # --- End Gesture Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "gesture_registered",
            "gesture_id": gesture_id,
            "gesture_type": gesture_type.value,
            "gesture_category": gesture_category.value,
            "description": description
        })
        
        self.logger.debug(f"Registered gesture: {gesture_id} ({gesture_type.value}, {gesture_category.value})")
        return True
    
    def unregister_gesture(self, gesture_id: str) -> bool:
        """
        Unregister a gesture.
        
        Args:
            gesture_id: ID of the gesture to unregister
            
        Returns:
            True if the gesture was unregistered, False if not found
        """
        if gesture_id not in self.gestures:
            return False
            
        # --- Gesture Backend Interaction (Placeholder) ---
        try:
            # self.gesture_backend.unregister_gesture(gesture_id)
            pass
        except Exception as e:
            self.logger.error(f"Error unregistering gesture with backend: {e}")
        # --- End Gesture Backend Interaction ---
        
        del self.gestures[gesture_id]
        
        # Remove any listeners for this gesture
        if gesture_id in self.gesture_listeners:
            del self.gesture_listeners[gesture_id]
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "gesture_unregistered",
            "gesture_id": gesture_id
        })
        
        self.logger.debug(f"Unregistered gesture: {gesture_id}")
        return True
    
    def create_hand_gesture(self,
                          gesture_id: str,
                          hand_pose: HandPose,
                          category: GestureCategory,
                          description: str,
                          requires_motion: bool = False,
                          motion_direction: Optional[Tuple[float, float, float]] = None,
                          duration_threshold: Optional[float] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a hand pose or motion gesture.
        
        Args:
            gesture_id: Unique identifier for this gesture
            hand_pose: Hand pose for this gesture
            category: Category of gesture
            description: Human-readable description
            requires_motion: Whether this gesture requires motion
            motion_direction: Optional motion direction vector
            duration_threshold: Optional minimum duration in seconds
            metadata: Additional metadata for this gesture
            
        Returns:
            True if the gesture was created, False if already exists
        """
        parameters = {
            "hand_pose": hand_pose.value,
            "requires_motion": requires_motion,
            "motion_direction": motion_direction,
            "duration_threshold": duration_threshold
        }
        
        return self.register_gesture(
            gesture_id=gesture_id,
            gesture_type=GestureType.HAND,
            gesture_category=category,
            description=description,
            parameters=parameters,
            metadata=metadata
        )
    
    def create_multi_touch_gesture(self,
                                 gesture_id: str,
                                 touch_points: int,
                                 gesture_pattern: str,
                                 category: GestureCategory,
                                 description: str,
                                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a multi-touch gesture.
        
        Args:
            gesture_id: Unique identifier for this gesture
            touch_points: Number of touch points
            gesture_pattern: Pattern name (e.g., "pinch", "spread", "rotate", "swipe")
            category: Category of gesture
            description: Human-readable description
            metadata: Additional metadata for this gesture
            
        Returns:
            True if the gesture was created, False if already exists
        """
        parameters = {
            "touch_points": touch_points,
            "gesture_pattern": gesture_pattern
        }
        
        return self.register_gesture(
            gesture_id=gesture_id,
            gesture_type=GestureType.MULTI_TOUCH,
            gesture_category=category,
            description=description,
            parameters=parameters,
            metadata=metadata
        )
    
    def create_industrial_gesture(self,
                                gesture_id: str,
                                gesture_type: GestureType,
                                description: str,
                                parameters: Dict[str, Any],
                                safety_level: str = "normal",
                                requires_confirmation: bool = False,
                                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create an industrial-specific gesture.
        
        Args:
            gesture_id: Unique identifier for this gesture
            gesture_type: Type of gesture
            description: Human-readable description
            parameters: Gesture-specific parameters
            safety_level: Safety level ("normal", "caution", "critical")
            requires_confirmation: Whether this gesture requires confirmation
            metadata: Additional metadata for this gesture
            
        Returns:
            True if the gesture was created, False if already exists
        """
        # Add industrial-specific parameters
        parameters.update({
            "safety_level": safety_level,
            "requires_confirmation": requires_confirmation
        })
        
        return self.register_gesture(
            gesture_id=gesture_id,
            gesture_type=gesture_type,
            gesture_category=GestureCategory.INDUSTRIAL,
            description=description,
            parameters=parameters,
            metadata=metadata
        )
    
    def start_gesture_recognizer(self,
                               recognizer_id: str,
                               gesture_ids: List[str],
                               user_id: Optional[str] = None,
                               device_id: Optional[str] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Start a gesture recognizer for specific gestures.
        
        Args:
            recognizer_id: Unique identifier for this recognizer
            gesture_ids: List of gesture IDs to recognize
            user_id: Optional user ID to associate with this recognizer
            device_id: Optional device ID to associate with this recognizer
            metadata: Additional metadata for this recognizer
            
        Returns:
            True if the recognizer was started, False if already exists or gestures not found
        """
        if not self.is_active:
            self.logger.warning("Gesture Recognition System is not active.")
            return False
            
        if recognizer_id in self.active_recognizers:
            self.logger.warning(f"Gesture recognizer {recognizer_id} already exists.")
            return False
            
        # Check if all gestures exist
        for gesture_id in gesture_ids:
            if gesture_id not in self.gestures:
                self.logger.warning(f"Gesture {gesture_id} not found.")
                return False
                
        # Create recognizer data
        self.active_recognizers[recognizer_id] = {
            "recognizer_id": recognizer_id,
            "gesture_ids": gesture_ids,
            "user_id": user_id,
            "device_id": device_id,
            "start_time": time.time(),
            "last_update_time": time.time(),
            "recognized_gestures": [],  # List of recently recognized gestures
            "metadata": metadata or {}
        }
        
        # --- Gesture Backend Interaction (Placeholder) ---
        try:
            # self.gesture_backend.start_recognizer(recognizer_id, {
            #     "gesture_ids": gesture_ids,
            #     "user_id": user_id,
            #     "device_id": device_id
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error starting gesture recognizer with backend: {e}")
            del self.active_recognizers[recognizer_id]
            return False
        # --- End Gesture Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "gesture_recognizer_started",
            "recognizer_id": recognizer_id,
            "gesture_ids": gesture_ids,
            "user_id": user_id,
            "device_id": device_id
        })
        
        self.logger.debug(f"Started gesture recognizer: {recognizer_id} for {len(gesture_ids)} gestures")
        return True
    
    def stop_gesture_recognizer(self, recognizer_id: str) -> bool:
        """
        Stop a gesture recognizer.
        
        Args:
            recognizer_id: ID of the recognizer to stop
            
        Returns:
            True if the recognizer was stopped, False if not found
        """
        if recognizer_id not in self.active_recognizers:
            return False
            
        # --- Gesture Backend Interaction (Placeholder) ---
        try:
            # self.gesture_backend.stop_recognizer(recognizer_id)
            pass
        except Exception as e:
            self.logger.error(f"Error stopping gesture recognizer with backend: {e}")
        # --- End Gesture Backend Interaction ---
        
        del self.active_recognizers[recognizer_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "gesture_recognizer_stopped",
            "recognizer_id": recognizer_id
        })
        
        self.logger.debug(f"Stopped gesture recognizer: {recognizer_id}")
        return True
    
    def update_hand_tracking(self,
                           hand_id: str,
                           is_left: bool,
                           position: Tuple[float, float, float],
                           rotation: Optional[Tuple[float, float, float, float]] = None,
                           joints: Optional[Dict[str, HandJoint]] = None,
                           velocity: Optional[Tuple[float, float, float]] = None,
                           confidence: float = 1.0) -> bool:
        """
        Update hand tracking data.
        
        Args:
            hand_id: Unique identifier for this hand
            is_left: Whether it's the left hand
            position: Palm position
            rotation: Optional palm rotation
            joints: Optional map of joint ID to joint data
            velocity: Optional velocity vector
            confidence: Overall confidence level (0.0-1.0)
            
        Returns:
            True if the hand tracking was updated, False if error
        """
        # Create or update hand tracking data
        hand_data = HandData(
            hand_id=hand_id,
            is_left=is_left,
            position=position,
            rotation=rotation,
            joints=joints or {},
            velocity=velocity,
            confidence=confidence
        )
        
        self.tracked_hands[hand_id] = hand_data
        
        # --- Gesture Backend Interaction (Placeholder) ---
        try:
            # self.gesture_backend.update_hand_tracking(hand_id, {
            #     "is_left": is_left,
            #     "position": position,
            #     "rotation": rotation,
            #     "joints": {j_id: {"position": j.position, "rotation": j.rotation, "confidence": j.confidence} 
            #                for j_id, j in (joints or {}).items()},
            #     "velocity": velocity,
            #     "confidence": confidence
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error updating hand tracking with backend: {e}")
            return False
        # --- End Gesture Backend Interaction ---
        
        return True
    
    def add_gesture_listener(self, gesture_id: str, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Add a listener for a specific gesture.
        
        Args:
            gesture_id: ID of the gesture to listen for
            listener: Callback function that will be called when the gesture is recognized
            
        Returns:
            True if the listener was added, False if gesture not found
        """
        if gesture_id not in self.gestures:
            self.logger.warning(f"Gesture {gesture_id} not found.")
            return False
            
        if gesture_id not in self.gesture_listeners:
            self.gesture_listeners[gesture_id] = []
            
        self.gesture_listeners[gesture_id].append(listener)
        return True
    
    def remove_gesture_listener(self, gesture_id: str, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Remove a listener for a specific gesture.
        
        Args:
            gesture_id: ID of the gesture
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if gesture_id not in self.gesture_listeners:
            return False
            
        if listener in self.gesture_listeners[gesture_id]:
            self.gesture_listeners[gesture_id].remove(listener)
            return True
            
        return False
    
    def get_recognized_gestures(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently recognized gestures.
        
        Args:
            limit: Maximum number of gestures to return
            
        Returns:
            List of recently recognized gestures
        """
        return self.gesture_history[:limit]
    
    def get_hand_pose(self, hand_id: str) -> Optional[HandPose]:
        """
        Get the current pose of a tracked hand.
        
        Args:
            hand_id: ID of the hand
            
        Returns:
            Current hand pose, or None if hand not tracked or pose not recognized
        """
        if hand_id not in self.tracked_hands:
            return None
            
        # --- Gesture Backend Interaction (Placeholder) ---
        # In a real implementation, this would query the gesture backend
        # For now, we'll just return a random pose for simulation
        poses = list(HandPose)
        return random.choice(poses)
        # --- End Gesture Backend Interaction ---
    
    def train_custom_gesture(self,
                           gesture_id: str,
                           gesture_type: GestureType,
                           category: GestureCategory,
                           description: str,
                           training_data: List[Dict[str, Any]],
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Train a custom gesture using example data.
        
        Args:
            gesture_id: Unique identifier for this gesture
            gesture_type: Type of gesture
            category: Category of gesture
            description: Human-readable description
            training_data: List of training examples
            metadata: Additional metadata for this gesture
            
        Returns:
            True if the gesture was trained, False if error
        """
        if gesture_id in self.gestures:
            self.logger.warning(f"Gesture {gesture_id} already exists.")
            return False
            
        if not training_data:
            self.logger.warning("No training data provided.")
            return False
            
        # --- Gesture Backend Interaction (Placeholder) ---
        try:
            # In a real implementation, this would train a gesture model
            # For now, we'll just register the gesture with the training data
            
            parameters = {
                "is_custom": True,
                "training_examples": len(training_data),
                "training_data": training_data
            }
            
            return self.register_gesture(
                gesture_id=gesture_id,
                gesture_type=gesture_type,
                gesture_category=category,
                description=description,
                parameters=parameters,
                metadata=metadata
            )
        except Exception as e:
            self.logger.error(f"Error training custom gesture: {e}")
            return False
        # --- End Gesture Backend Interaction ---
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for gesture recognition events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for gesture recognition events.
        
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
        event_data["source"] = "GestureRecognitionSystem"
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in gesture recognition event listener: {e}")
                
    def _dispatch_gesture_event(self, gesture_data: Dict[str, Any]) -> None:
        """
        Dispatch a gesture recognition event to gesture-specific listeners.
        
        Args:
            gesture_data: The gesture recognition data
        """
        gesture_id = gesture_data["gesture_id"]
        
        if gesture_id in self.gesture_listeners:
            for listener in self.gesture_listeners[gesture_id]:
                try:
                    listener(gesture_data)
                except Exception as e:
                    self.logger.error(f"Error in gesture listener for {gesture_id}: {e}")
                    
    def _initialize_gesture_backend(self) -> Any:
        """Placeholder for initializing the gesture backend."""
        # In a real implementation, this would initialize a gesture recognition system
        # For now, we'll just return a dummy object
        return object()
    
    def _load_gestures_from_config(self) -> None:
        """Load gestures from the configuration."""
        gestures_config = self.config.get("gestures", [])
        
        for gesture_config in gestures_config:
            try:
                gesture_id = gesture_config["gesture_id"]
                gesture_type = GestureType(gesture_config["gesture_type"])
                gesture_category = GestureCategory(gesture_config["gesture_category"])
                description = gesture_config["description"]
                parameters = gesture_config["parameters"]
                metadata = gesture_config.get("metadata")
                
                self.register_gesture(
                    gesture_id=gesture_id,
                    gesture_type=gesture_type,
                    gesture_category=gesture_category,
                    description=description,
                    parameters=parameters,
                    metadata=metadata
                )
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error loading gesture from config: {e}")
                
    def _update_loop(self) -> None:
        """Background thread for updating gesture recognition."""
        while self.is_active:
            try:
                # --- Gesture Backend Interaction (Placeholder) ---
                # In a real implementation, this would poll the gesture backend for new recognitions
                # For now, we'll just simulate gesture recognition
                
                # Simulate gesture recognition for each active recognizer
                for recognizer_id, recognizer in self.active_recognizers.items():
                    # Randomly recognize a gesture occasionally
                    if random.random() < 0.01:  # 1% chance per update
                        if recognizer["gesture_ids"]:
                            # Pick a random gesture from this recognizer
                            gesture_id = random.choice(recognizer["gesture_ids"])
                            gesture = self.gestures[gesture_id]
                            
                            # Create recognition data
                            recognition = {
                                "recognition_id": str(uuid.uuid4()),
                                "recognizer_id": recognizer_id,
                                "gesture_id": gesture_id,
                                "gesture_type": gesture["gesture_type"].value,
                                "gesture_category": gesture["gesture_category"].value,
                                "confidence": random.uniform(0.7, 1.0),
                                "confidence_level": GestureConfidenceLevel.HIGH.value,
                                "timestamp": time.time(),
                                "user_id": recognizer["user_id"],
                                "device_id": recognizer["device_id"],
                                "parameters": {},  # Recognition-specific parameters
                                "metadata": {}
                            }
                            
                            # Add to gesture history
                            self.gesture_history.insert(0, recognition)
                            
                            # Limit history size
                            max_history = self.config.get("max_gesture_history", 100)
                            if len(self.gesture_history) > max_history:
                                self.gesture_history = self.gesture_history[:max_history]
                                
                            # Add to recognizer's recognized gestures
                            recognizer["recognized_gestures"].insert(0, recognition)
                            
                            # Limit recognizer history size
                            max_recognizer_history = self.config.get("max_recognizer_history", 10)
                            if len(recognizer["recognized_gestures"]) > max_recognizer_history:
                                recognizer["recognized_gestures"] = recognizer["recognized_gestures"][:max_recognizer_history]
                                
                            # Update timestamp
                            recognizer["last_update_time"] = recognition["timestamp"]
                            
                            # Dispatch events
                            self._dispatch_event({
                                "event_type": "gesture_recognized",
                                "recognition_id": recognition["recognition_id"],
                                "recognizer_id": recognizer_id,
                                "gesture_id": gesture_id,
                                "gesture_type": gesture["gesture_type"].value,
                                "gesture_category": gesture["gesture_category"].value,
                                "confidence": recognition["confidence"],
                                "confidence_level": recognition["confidence_level"],
                                "user_id": recognizer["user_id"],
                                "device_id": recognizer["device_id"]
                            })
                            
                            self._dispatch_gesture_event(recognition)
                # --- End Gesture Backend Interaction ---
                
            except Exception as e:
                self.logger.error(f"Error in gesture recognition update loop: {e}")
                
            # Sleep until next update
            time.sleep(self.update_interval)

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create gesture recognition system
    gesture_config = {
        "update_interval": 0.033,  # ~30 fps
        "max_gesture_history": 100,
        "max_recognizer_history": 10,
        "gestures": [
            {
                "gesture_id": "swipe_right",
                "gesture_type": "hand",
                "gesture_category": "navigation",
                "description": "Swipe hand right",
                "parameters": {
                    "hand_pose": "open",
                    "requires_motion": True,
                    "motion_direction": (1.0, 0.0, 0.0),
                    "duration_threshold": 0.3
                }
            },
            {
                "gesture_id": "pinch_to_zoom",
                "gesture_type": "multi_touch",
                "gesture_category": "manipulation",
                "description": "Pinch to zoom",
                "parameters": {
                    "touch_points": 2,
                    "gesture_pattern": "pinch"
                }
            }
        ]
    }
    
    gesture_system = GestureRecognitionSystem(config=gesture_config)
    
    # Start the system
    gesture_system.start()
    
    # Register a hand gesture
    gesture_system.create_hand_gesture(
        gesture_id="thumbs_up",
        hand_pose=HandPose.THUMBS_UP,
        category=GestureCategory.COMMAND,
        description="Thumbs up gesture",
        requires_motion=False,
        metadata={"action": "approve"}
    )
    
    # Register an industrial gesture
    gesture_system.create_industrial_gesture(
        gesture_id="emergency_stop",
        gesture_type=GestureType.ARM,
        description="Emergency stop gesture",
        parameters={
            "arm_pose": "crossed",
            "requires_both_arms": True
        },
        safety_level="critical",
        requires_confirmation=True,
        metadata={"action": "emergency_stop"}
    )
    
    # Add a gesture listener
    def on_thumbs_up(gesture_data):
        print(f"Thumbs up gesture recognized! Confidence: {gesture_data['confidence']:.2f}")
        
    gesture_system.add_gesture_listener("thumbs_up", on_thumbs_up)
    
    # Start a gesture recognizer
    gesture_system.start_gesture_recognizer(
        recognizer_id="main_recognizer",
        gesture_ids=["swipe_right", "thumbs_up", "emergency_stop"],
        user_id="user_1"
    )
    
    # Simulate hand tracking
    gesture_system.update_hand_tracking(
        hand_id="right_hand",
        is_left=False,
        position=(0.0, 1.0, -0.5),
        rotation=(0.0, 0.0, 0.0, 1.0),
        confidence=0.95
    )
    
    # Wait a bit to see events
    time.sleep(5)
    
    # Get recognized gestures
    recent_gestures = gesture_system.get_recognized_gestures()
    print(f"Recognized {len(recent_gestures)} gestures")
    
    # Stop the system
    gesture_system.stop()
"""
