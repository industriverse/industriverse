"""
Spatial Awareness Engine for the Industriverse UI/UX Layer.

This module provides spatial awareness capabilities for the Universal Skin and Agent Capsules,
enabling context-aware positioning and interaction in physical and virtual spaces.

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

class SpatialContextType(Enum):
    """Enumeration of spatial context types."""
    INDUSTRIAL_FLOOR = "industrial_floor"  # Factory/warehouse floor
    CONTROL_ROOM = "control_room"  # Control room environment
    FIELD_SITE = "field_site"  # Field site or outdoor industrial area
    OFFICE = "office"  # Office environment
    MEETING_ROOM = "meeting_room"  # Meeting room
    MOBILE = "mobile"  # Mobile context (on the move)
    VEHICLE = "vehicle"  # Vehicle context (car, truck, etc.)
    AR_OVERLAY = "ar_overlay"  # AR overlay on physical space
    VR_SPACE = "vr_space"  # Virtual reality space
    MIXED_REALITY = "mixed_reality"  # Mixed reality environment
    CUSTOM = "custom"  # Custom spatial context

class SpatialAnchorType(Enum):
    """Enumeration of spatial anchor types."""
    FIXED = "fixed"  # Fixed position in space
    DEVICE_RELATIVE = "device_relative"  # Relative to device
    USER_RELATIVE = "user_relative"  # Relative to user
    OBJECT_RELATIVE = "object_relative"  # Relative to physical object
    DIGITAL_TWIN = "digital_twin"  # Anchored to digital twin
    EQUIPMENT = "equipment"  # Anchored to industrial equipment
    PROCESS = "process"  # Anchored to industrial process
    CUSTOM = "custom"  # Custom anchor type

class SpatialInteractionMode(Enum):
    """Enumeration of spatial interaction modes."""
    DIRECT = "direct"  # Direct interaction (touch, click)
    PROXIMITY = "proximity"  # Proximity-based interaction
    GAZE = "gaze"  # Gaze-based interaction
    GESTURE = "gesture"  # Gesture-based interaction
    VOICE = "voice"  # Voice-based interaction
    MULTI_MODAL = "multi_modal"  # Multi-modal interaction
    CUSTOM = "custom"  # Custom interaction mode

class SpatialAwarenessEngine:
    """
    Provides spatial awareness capabilities for the Industriverse UI/UX Layer.
    
    This class provides:
    - Spatial context detection and adaptation
    - Spatial anchoring for UI elements and Agent Capsules
    - Proximity-based interaction and notifications
    - Integration with AR/VR systems
    - Spatial mapping and environment understanding
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Spatial Awareness Engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.current_context: Optional[SpatialContextType] = None
        self.context_confidence: float = 0.0
        self.spatial_anchors: Dict[str, Dict[str, Any]] = {}  # Map anchor ID to anchor data
        self.spatial_objects: Dict[str, Dict[str, Any]] = {}  # Map object ID to object data
        self.spatial_zones: Dict[str, Dict[str, Any]] = {}  # Map zone ID to zone data
        self.tracked_users: Dict[str, Dict[str, Any]] = {}  # Map user ID to user data
        self.tracked_devices: Dict[str, Dict[str, Any]] = {}  # Map device ID to device data
        self.interaction_history: List[Dict[str, Any]] = []  # List of recent spatial interactions
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.context_update_interval: float = self.config.get("context_update_interval", 1.0)  # seconds
        self.proximity_check_interval: float = self.config.get("proximity_check_interval", 0.5)  # seconds
        
        # Initialize spatial backend (placeholder)
        self.spatial_backend = self._initialize_spatial_backend()
        
        # Load spatial data from config
        self._load_spatial_data_from_config()
        
    def start(self) -> bool:
        """
        Start the Spatial Awareness Engine.
        
        Returns:
            True if the engine was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Start spatial backend (placeholder)
        # self.spatial_backend.start()
        
        # Start context update thread
        threading.Thread(target=self._context_update_loop, daemon=True).start()
        
        # Start proximity check thread
        threading.Thread(target=self._proximity_check_loop, daemon=True).start()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_awareness_engine_started"
        })
        
        self.logger.info("Spatial Awareness Engine started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Spatial Awareness Engine.
        
        Returns:
            True if the engine was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Stop spatial backend (placeholder)
        # self.spatial_backend.stop()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_awareness_engine_stopped"
        })
        
        self.logger.info("Spatial Awareness Engine stopped.")
        return True
    
    def get_current_context(self) -> Tuple[Optional[SpatialContextType], float]:
        """
        Get the current spatial context and confidence level.
        
        Returns:
            Tuple of (context_type, confidence)
        """
        return (self.current_context, self.context_confidence)
    
    def set_current_context(self, context_type: SpatialContextType, confidence: float = 1.0) -> None:
        """
        Manually set the current spatial context.
        
        Args:
            context_type: The spatial context type
            confidence: Confidence level (0.0-1.0)
        """
        old_context = self.current_context
        self.current_context = context_type
        self.context_confidence = max(0.0, min(1.0, confidence))
        
        # Dispatch event if context changed
        if old_context != context_type:
            self._dispatch_event({
                "event_type": "spatial_context_changed",
                "old_context": old_context.value if old_context else None,
                "new_context": context_type.value,
                "confidence": self.context_confidence
            })
            
        self.logger.debug(f"Spatial context set to {context_type.value} (confidence: {self.context_confidence:.2f})")
    
    def create_spatial_anchor(self,
                            anchor_id: str,
                            anchor_type: SpatialAnchorType,
                            position: Tuple[float, float, float],
                            rotation: Optional[Tuple[float, float, float, float]] = None,
                            scale: Optional[Tuple[float, float, float]] = None,
                            parent_id: Optional[str] = None,
                            valid_contexts: Optional[List[SpatialContextType]] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a spatial anchor.
        
        Args:
            anchor_id: Unique identifier for this anchor
            anchor_type: Type of spatial anchor
            position: 3D position (x, y, z)
            rotation: Optional quaternion rotation (x, y, z, w)
            scale: Optional 3D scale (x, y, z)
            parent_id: Optional parent anchor or object ID
            valid_contexts: Optional list of valid spatial contexts
            metadata: Additional metadata for this anchor
            
        Returns:
            True if the anchor was created, False if already exists
        """
        if anchor_id in self.spatial_anchors:
            self.logger.warning(f"Spatial anchor {anchor_id} already exists.")
            return False
            
        self.spatial_anchors[anchor_id] = {
            "anchor_id": anchor_id,
            "anchor_type": anchor_type,
            "position": position,
            "rotation": rotation or (0.0, 0.0, 0.0, 1.0),  # Default to identity quaternion
            "scale": scale or (1.0, 1.0, 1.0),  # Default to unit scale
            "parent_id": parent_id,
            "valid_contexts": valid_contexts or list(SpatialContextType),  # Default to all contexts
            "creation_time": time.time(),
            "last_update_time": time.time(),
            "attached_objects": [],  # List of attached object IDs
            "metadata": metadata or {}
        }
        
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.register_anchor(anchor_id, {
            #     "type": anchor_type.value,
            #     "position": position,
            #     "rotation": rotation or (0.0, 0.0, 0.0, 1.0),
            #     "scale": scale or (1.0, 1.0, 1.0),
            #     "parent_id": parent_id
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error registering spatial anchor with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_anchor_created",
            "anchor_id": anchor_id,
            "anchor_type": anchor_type.value,
            "position": position,
            "parent_id": parent_id
        })
        
        self.logger.debug(f"Created spatial anchor: {anchor_id} ({anchor_type.value})")
        return True
    
    def update_spatial_anchor(self,
                            anchor_id: str,
                            position: Optional[Tuple[float, float, float]] = None,
                            rotation: Optional[Tuple[float, float, float, float]] = None,
                            scale: Optional[Tuple[float, float, float]] = None,
                            parent_id: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a spatial anchor.
        
        Args:
            anchor_id: ID of the anchor to update
            position: Optional new 3D position
            rotation: Optional new quaternion rotation
            scale: Optional new 3D scale
            parent_id: Optional new parent anchor or object ID
            metadata: Optional new or updated metadata
            
        Returns:
            True if the anchor was updated, False if not found
        """
        if anchor_id not in self.spatial_anchors:
            self.logger.warning(f"Spatial anchor {anchor_id} not found.")
            return False
            
        anchor = self.spatial_anchors[anchor_id]
        
        # Update position if provided
        if position is not None:
            anchor["position"] = position
            
        # Update rotation if provided
        if rotation is not None:
            anchor["rotation"] = rotation
            
        # Update scale if provided
        if scale is not None:
            anchor["scale"] = scale
            
        # Update parent if provided
        if parent_id is not None:
            anchor["parent_id"] = parent_id
            
        # Update metadata if provided
        if metadata is not None:
            anchor["metadata"].update(metadata)
            
        # Update timestamp
        anchor["last_update_time"] = time.time()
        
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # update_params = {}
            # if position is not None:
            #     update_params["position"] = position
            # if rotation is not None:
            #     update_params["rotation"] = rotation
            # if scale is not None:
            #     update_params["scale"] = scale
            # if parent_id is not None:
            #     update_params["parent_id"] = parent_id
            # 
            # self.spatial_backend.update_anchor(anchor_id, update_params)
            pass
        except Exception as e:
            self.logger.error(f"Error updating spatial anchor with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_anchor_updated",
            "anchor_id": anchor_id,
            "position": anchor["position"],
            "rotation": anchor["rotation"],
            "scale": anchor["scale"],
            "parent_id": anchor["parent_id"]
        })
        
        self.logger.debug(f"Updated spatial anchor: {anchor_id}")
        return True
    
    def remove_spatial_anchor(self, anchor_id: str) -> bool:
        """
        Remove a spatial anchor.
        
        Args:
            anchor_id: ID of the anchor to remove
            
        Returns:
            True if the anchor was removed, False if not found
        """
        if anchor_id not in self.spatial_anchors:
            return False
            
        # Check if any objects are attached to this anchor
        anchor = self.spatial_anchors[anchor_id]
        if anchor["attached_objects"]:
            self.logger.warning(f"Spatial anchor {anchor_id} has attached objects. Detaching them first.")
            for object_id in anchor["attached_objects"]:
                if object_id in self.spatial_objects:
                    self.spatial_objects[object_id]["anchor_id"] = None
                    
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.unregister_anchor(anchor_id)
            pass
        except Exception as e:
            self.logger.error(f"Error unregistering spatial anchor with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        del self.spatial_anchors[anchor_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_anchor_removed",
            "anchor_id": anchor_id
        })
        
        self.logger.debug(f"Removed spatial anchor: {anchor_id}")
        return True
    
    def create_spatial_object(self,
                            object_id: str,
                            object_type: str,
                            anchor_id: Optional[str] = None,
                            position: Optional[Tuple[float, float, float]] = None,
                            rotation: Optional[Tuple[float, float, float, float]] = None,
                            scale: Optional[Tuple[float, float, float]] = None,
                            valid_contexts: Optional[List[SpatialContextType]] = None,
                            interaction_modes: Optional[List[SpatialInteractionMode]] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a spatial object.
        
        Args:
            object_id: Unique identifier for this object
            object_type: Type of spatial object
            anchor_id: Optional anchor ID to attach to
            position: Optional 3D position (if not anchored)
            rotation: Optional quaternion rotation
            scale: Optional 3D scale
            valid_contexts: Optional list of valid spatial contexts
            interaction_modes: Optional list of supported interaction modes
            metadata: Additional metadata for this object
            
        Returns:
            True if the object was created, False if already exists
        """
        if object_id in self.spatial_objects:
            self.logger.warning(f"Spatial object {object_id} already exists.")
            return False
            
        # Check if anchor exists if specified
        if anchor_id is not None and anchor_id not in self.spatial_anchors:
            self.logger.warning(f"Spatial anchor {anchor_id} not found.")
            return False
            
        # Position is required if not anchored
        if anchor_id is None and position is None:
            self.logger.warning("Position is required if not anchored.")
            return False
            
        self.spatial_objects[object_id] = {
            "object_id": object_id,
            "object_type": object_type,
            "anchor_id": anchor_id,
            "position": position if position is not None else (0.0, 0.0, 0.0),
            "rotation": rotation or (0.0, 0.0, 0.0, 1.0),  # Default to identity quaternion
            "scale": scale or (1.0, 1.0, 1.0),  # Default to unit scale
            "valid_contexts": valid_contexts or list(SpatialContextType),  # Default to all contexts
            "interaction_modes": interaction_modes or [SpatialInteractionMode.DIRECT],  # Default to direct interaction
            "creation_time": time.time(),
            "last_update_time": time.time(),
            "last_interaction_time": None,
            "is_visible": True,
            "is_interactive": True,
            "metadata": metadata or {}
        }
        
        # Add to anchor's attached objects if anchored
        if anchor_id is not None:
            self.spatial_anchors[anchor_id]["attached_objects"].append(object_id)
            
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.register_object(object_id, {
            #     "type": object_type,
            #     "anchor_id": anchor_id,
            #     "position": position if position is not None else (0.0, 0.0, 0.0),
            #     "rotation": rotation or (0.0, 0.0, 0.0, 1.0),
            #     "scale": scale or (1.0, 1.0, 1.0),
            #     "interaction_modes": [mode.value for mode in (interaction_modes or [SpatialInteractionMode.DIRECT])]
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error registering spatial object with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_object_created",
            "object_id": object_id,
            "object_type": object_type,
            "anchor_id": anchor_id,
            "position": self.spatial_objects[object_id]["position"]
        })
        
        self.logger.debug(f"Created spatial object: {object_id} ({object_type})")
        return True
    
    def update_spatial_object(self,
                            object_id: str,
                            anchor_id: Optional[str] = None,
                            position: Optional[Tuple[float, float, float]] = None,
                            rotation: Optional[Tuple[float, float, float, float]] = None,
                            scale: Optional[Tuple[float, float, float]] = None,
                            is_visible: Optional[bool] = None,
                            is_interactive: Optional[bool] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a spatial object.
        
        Args:
            object_id: ID of the object to update
            anchor_id: Optional new anchor ID
            position: Optional new 3D position
            rotation: Optional new quaternion rotation
            scale: Optional new 3D scale
            is_visible: Optional visibility flag
            is_interactive: Optional interactivity flag
            metadata: Optional new or updated metadata
            
        Returns:
            True if the object was updated, False if not found
        """
        if object_id not in self.spatial_objects:
            self.logger.warning(f"Spatial object {object_id} not found.")
            return False
            
        obj = self.spatial_objects[object_id]
        old_anchor_id = obj["anchor_id"]
        
        # Check if new anchor exists if specified
        if anchor_id is not None and anchor_id != old_anchor_id and anchor_id not in self.spatial_anchors:
            self.logger.warning(f"Spatial anchor {anchor_id} not found.")
            return False
            
        # Update anchor if provided
        if anchor_id is not None and anchor_id != old_anchor_id:
            # Remove from old anchor's attached objects if previously anchored
            if old_anchor_id is not None and old_anchor_id in self.spatial_anchors:
                if object_id in self.spatial_anchors[old_anchor_id]["attached_objects"]:
                    self.spatial_anchors[old_anchor_id]["attached_objects"].remove(object_id)
                    
            # Add to new anchor's attached objects
            if anchor_id in self.spatial_anchors:
                self.spatial_anchors[anchor_id]["attached_objects"].append(object_id)
                
            obj["anchor_id"] = anchor_id
            
        # Update position if provided
        if position is not None:
            obj["position"] = position
            
        # Update rotation if provided
        if rotation is not None:
            obj["rotation"] = rotation
            
        # Update scale if provided
        if scale is not None:
            obj["scale"] = scale
            
        # Update visibility if provided
        if is_visible is not None:
            obj["is_visible"] = is_visible
            
        # Update interactivity if provided
        if is_interactive is not None:
            obj["is_interactive"] = is_interactive
            
        # Update metadata if provided
        if metadata is not None:
            obj["metadata"].update(metadata)
            
        # Update timestamp
        obj["last_update_time"] = time.time()
        
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # update_params = {}
            # if anchor_id is not None and anchor_id != old_anchor_id:
            #     update_params["anchor_id"] = anchor_id
            # if position is not None:
            #     update_params["position"] = position
            # if rotation is not None:
            #     update_params["rotation"] = rotation
            # if scale is not None:
            #     update_params["scale"] = scale
            # if is_visible is not None:
            #     update_params["is_visible"] = is_visible
            # if is_interactive is not None:
            #     update_params["is_interactive"] = is_interactive
            # 
            # self.spatial_backend.update_object(object_id, update_params)
            pass
        except Exception as e:
            self.logger.error(f"Error updating spatial object with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_object_updated",
            "object_id": object_id,
            "anchor_id": obj["anchor_id"],
            "position": obj["position"],
            "rotation": obj["rotation"],
            "scale": obj["scale"],
            "is_visible": obj["is_visible"],
            "is_interactive": obj["is_interactive"]
        })
        
        self.logger.debug(f"Updated spatial object: {object_id}")
        return True
    
    def remove_spatial_object(self, object_id: str) -> bool:
        """
        Remove a spatial object.
        
        Args:
            object_id: ID of the object to remove
            
        Returns:
            True if the object was removed, False if not found
        """
        if object_id not in self.spatial_objects:
            return False
            
        obj = self.spatial_objects[object_id]
        
        # Remove from anchor's attached objects if anchored
        if obj["anchor_id"] is not None and obj["anchor_id"] in self.spatial_anchors:
            if object_id in self.spatial_anchors[obj["anchor_id"]]["attached_objects"]:
                self.spatial_anchors[obj["anchor_id"]]["attached_objects"].remove(object_id)
                
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.unregister_object(object_id)
            pass
        except Exception as e:
            self.logger.error(f"Error unregistering spatial object with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        del self.spatial_objects[object_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_object_removed",
            "object_id": object_id
        })
        
        self.logger.debug(f"Removed spatial object: {object_id}")
        return True
    
    def create_spatial_zone(self,
                          zone_id: str,
                          zone_type: str,
                          center: Tuple[float, float, float],
                          size: Tuple[float, float, float],
                          rotation: Optional[Tuple[float, float, float, float]] = None,
                          valid_contexts: Optional[List[SpatialContextType]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a spatial zone.
        
        Args:
            zone_id: Unique identifier for this zone
            zone_type: Type of spatial zone
            center: 3D center position
            size: 3D size (width, height, depth)
            rotation: Optional quaternion rotation
            valid_contexts: Optional list of valid spatial contexts
            metadata: Additional metadata for this zone
            
        Returns:
            True if the zone was created, False if already exists
        """
        if zone_id in self.spatial_zones:
            self.logger.warning(f"Spatial zone {zone_id} already exists.")
            return False
            
        self.spatial_zones[zone_id] = {
            "zone_id": zone_id,
            "zone_type": zone_type,
            "center": center,
            "size": size,
            "rotation": rotation or (0.0, 0.0, 0.0, 1.0),  # Default to identity quaternion
            "valid_contexts": valid_contexts or list(SpatialContextType),  # Default to all contexts
            "creation_time": time.time(),
            "last_update_time": time.time(),
            "contained_objects": [],  # List of object IDs currently in the zone
            "contained_users": [],  # List of user IDs currently in the zone
            "metadata": metadata or {}
        }
        
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.register_zone(zone_id, {
            #     "type": zone_type,
            #     "center": center,
            #     "size": size,
            #     "rotation": rotation or (0.0, 0.0, 0.0, 1.0)
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error registering spatial zone with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_zone_created",
            "zone_id": zone_id,
            "zone_type": zone_type,
            "center": center,
            "size": size
        })
        
        self.logger.debug(f"Created spatial zone: {zone_id} ({zone_type})")
        return True
    
    def update_spatial_zone(self,
                          zone_id: str,
                          center: Optional[Tuple[float, float, float]] = None,
                          size: Optional[Tuple[float, float, float]] = None,
                          rotation: Optional[Tuple[float, float, float, float]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a spatial zone.
        
        Args:
            zone_id: ID of the zone to update
            center: Optional new center position
            size: Optional new size
            rotation: Optional new quaternion rotation
            metadata: Optional new or updated metadata
            
        Returns:
            True if the zone was updated, False if not found
        """
        if zone_id not in self.spatial_zones:
            self.logger.warning(f"Spatial zone {zone_id} not found.")
            return False
            
        zone = self.spatial_zones[zone_id]
        
        # Update center if provided
        if center is not None:
            zone["center"] = center
            
        # Update size if provided
        if size is not None:
            zone["size"] = size
            
        # Update rotation if provided
        if rotation is not None:
            zone["rotation"] = rotation
            
        # Update metadata if provided
        if metadata is not None:
            zone["metadata"].update(metadata)
            
        # Update timestamp
        zone["last_update_time"] = time.time()
        
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # update_params = {}
            # if center is not None:
            #     update_params["center"] = center
            # if size is not None:
            #     update_params["size"] = size
            # if rotation is not None:
            #     update_params["rotation"] = rotation
            # 
            # self.spatial_backend.update_zone(zone_id, update_params)
            pass
        except Exception as e:
            self.logger.error(f"Error updating spatial zone with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_zone_updated",
            "zone_id": zone_id,
            "center": zone["center"],
            "size": zone["size"],
            "rotation": zone["rotation"]
        })
        
        self.logger.debug(f"Updated spatial zone: {zone_id}")
        return True
    
    def remove_spatial_zone(self, zone_id: str) -> bool:
        """
        Remove a spatial zone.
        
        Args:
            zone_id: ID of the zone to remove
            
        Returns:
            True if the zone was removed, False if not found
        """
        if zone_id not in self.spatial_zones:
            return False
            
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.unregister_zone(zone_id)
            pass
        except Exception as e:
            self.logger.error(f"Error unregistering spatial zone with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        del self.spatial_zones[zone_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_zone_removed",
            "zone_id": zone_id
        })
        
        self.logger.debug(f"Removed spatial zone: {zone_id}")
        return True
    
    def track_user(self,
                 user_id: str,
                 position: Tuple[float, float, float],
                 rotation: Optional[Tuple[float, float, float, float]] = None,
                 device_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Track a user's position and orientation.
        
        Args:
            user_id: Unique identifier for this user
            position: 3D position
            rotation: Optional quaternion rotation (head orientation)
            device_id: Optional associated device ID
            metadata: Additional metadata for this user
            
        Returns:
            True if the user was tracked, False if error
        """
        # Create or update user tracking data
        if user_id in self.tracked_users:
            # Update existing user
            user = self.tracked_users[user_id]
            user["position"] = position
            if rotation is not None:
                user["rotation"] = rotation
            if device_id is not None:
                user["device_id"] = device_id
            if metadata is not None:
                user["metadata"].update(metadata)
            user["last_update_time"] = time.time()
        else:
            # Create new user tracking
            self.tracked_users[user_id] = {
                "user_id": user_id,
                "position": position,
                "rotation": rotation or (0.0, 0.0, 0.0, 1.0),  # Default to identity quaternion
                "device_id": device_id,
                "creation_time": time.time(),
                "last_update_time": time.time(),
                "current_zones": [],  # List of zone IDs the user is currently in
                "metadata": metadata or {}
            }
            
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.update_user_tracking(user_id, {
            #     "position": position,
            #     "rotation": rotation or (0.0, 0.0, 0.0, 1.0),
            #     "device_id": device_id
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error updating user tracking with backend: {e}")
            return False
        # --- End Spatial Backend Interaction ---
        
        # Check if user has entered or exited any zones
        self._check_user_zone_intersections(user_id)
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "user_position_updated",
            "user_id": user_id,
            "position": position,
            "rotation": self.tracked_users[user_id]["rotation"],
            "device_id": self.tracked_users[user_id]["device_id"]
        })
        
        return True
    
    def stop_tracking_user(self, user_id: str) -> bool:
        """
        Stop tracking a user.
        
        Args:
            user_id: ID of the user to stop tracking
            
        Returns:
            True if the user was removed from tracking, False if not found
        """
        if user_id not in self.tracked_users:
            return False
            
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.stop_user_tracking(user_id)
            pass
        except Exception as e:
            self.logger.error(f"Error stopping user tracking with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        del self.tracked_users[user_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "user_tracking_stopped",
            "user_id": user_id
        })
        
        self.logger.debug(f"Stopped tracking user: {user_id}")
        return True
    
    def track_device(self,
                   device_id: str,
                   device_type: str,
                   position: Tuple[float, float, float],
                   rotation: Optional[Tuple[float, float, float, float]] = None,
                   user_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Track a device's position and orientation.
        
        Args:
            device_id: Unique identifier for this device
            device_type: Type of device
            position: 3D position
            rotation: Optional quaternion rotation
            user_id: Optional associated user ID
            metadata: Additional metadata for this device
            
        Returns:
            True if the device was tracked, False if error
        """
        # Create or update device tracking data
        if device_id in self.tracked_devices:
            # Update existing device
            device = self.tracked_devices[device_id]
            device["position"] = position
            if rotation is not None:
                device["rotation"] = rotation
            if user_id is not None:
                device["user_id"] = user_id
            if metadata is not None:
                device["metadata"].update(metadata)
            device["last_update_time"] = time.time()
        else:
            # Create new device tracking
            self.tracked_devices[device_id] = {
                "device_id": device_id,
                "device_type": device_type,
                "position": position,
                "rotation": rotation or (0.0, 0.0, 0.0, 1.0),  # Default to identity quaternion
                "user_id": user_id,
                "creation_time": time.time(),
                "last_update_time": time.time(),
                "current_zones": [],  # List of zone IDs the device is currently in
                "metadata": metadata or {}
            }
            
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.update_device_tracking(device_id, {
            #     "device_type": device_type,
            #     "position": position,
            #     "rotation": rotation or (0.0, 0.0, 0.0, 1.0),
            #     "user_id": user_id
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error updating device tracking with backend: {e}")
            return False
        # --- End Spatial Backend Interaction ---
        
        # Check if device has entered or exited any zones
        self._check_device_zone_intersections(device_id)
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "device_position_updated",
            "device_id": device_id,
            "device_type": device_type,
            "position": position,
            "rotation": self.tracked_devices[device_id]["rotation"],
            "user_id": self.tracked_devices[device_id]["user_id"]
        })
        
        return True
    
    def stop_tracking_device(self, device_id: str) -> bool:
        """
        Stop tracking a device.
        
        Args:
            device_id: ID of the device to stop tracking
            
        Returns:
            True if the device was removed from tracking, False if not found
        """
        if device_id not in self.tracked_devices:
            return False
            
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.stop_device_tracking(device_id)
            pass
        except Exception as e:
            self.logger.error(f"Error stopping device tracking with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        del self.tracked_devices[device_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "device_tracking_stopped",
            "device_id": device_id
        })
        
        self.logger.debug(f"Stopped tracking device: {device_id}")
        return True
    
    def record_spatial_interaction(self,
                                 object_id: str,
                                 interaction_type: SpatialInteractionMode,
                                 user_id: Optional[str] = None,
                                 device_id: Optional[str] = None,
                                 position: Optional[Tuple[float, float, float]] = None,
                                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record a spatial interaction with an object.
        
        Args:
            object_id: ID of the interacted object
            interaction_type: Type of interaction
            user_id: Optional ID of the user who interacted
            device_id: Optional ID of the device used for interaction
            position: Optional 3D position of the interaction
            metadata: Additional metadata for this interaction
            
        Returns:
            True if the interaction was recorded, False if object not found
        """
        if object_id not in self.spatial_objects:
            self.logger.warning(f"Spatial object {object_id} not found.")
            return False
            
        obj = self.spatial_objects[object_id]
        
        # Check if object is interactive
        if not obj["is_interactive"]:
            self.logger.warning(f"Spatial object {object_id} is not interactive.")
            return False
            
        # Check if interaction mode is supported
        if interaction_type not in obj["interaction_modes"]:
            self.logger.warning(f"Interaction mode {interaction_type.value} not supported by object {object_id}.")
            return False
            
        # Create interaction record
        interaction = {
            "interaction_id": str(uuid.uuid4()),
            "object_id": object_id,
            "object_type": obj["object_type"],
            "interaction_type": interaction_type,
            "user_id": user_id,
            "device_id": device_id,
            "position": position or obj["position"],  # Default to object position if not specified
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        # Add to interaction history
        self.interaction_history.append(interaction)
        
        # Limit history size
        max_history = self.config.get("max_interaction_history", 100)
        if len(self.interaction_history) > max_history:
            self.interaction_history = self.interaction_history[-max_history:]
            
        # Update object's last interaction time
        obj["last_interaction_time"] = interaction["timestamp"]
        
        # --- Spatial Backend Interaction (Placeholder) ---
        try:
            # self.spatial_backend.record_interaction(interaction["interaction_id"], {
            #     "object_id": object_id,
            #     "interaction_type": interaction_type.value,
            #     "user_id": user_id,
            #     "device_id": device_id,
            #     "position": interaction["position"]
            # })
            pass
        except Exception as e:
            self.logger.error(f"Error recording interaction with backend: {e}")
        # --- End Spatial Backend Interaction ---
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "spatial_interaction",
            "interaction_id": interaction["interaction_id"],
            "object_id": object_id,
            "object_type": obj["object_type"],
            "interaction_type": interaction_type.value,
            "user_id": user_id,
            "device_id": device_id,
            "position": interaction["position"],
            "timestamp": interaction["timestamp"]
        })
        
        self.logger.debug(f"Recorded spatial interaction: {interaction_type.value} with {object_id}")
        return True
    
    def get_objects_in_radius(self,
                            center: Tuple[float, float, float],
                            radius: float,
                            object_type: Optional[str] = None,
                            max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get spatial objects within a radius of a point.
        
        Args:
            center: 3D center position
            radius: Radius to search within
            object_type: Optional filter by object type
            max_results: Maximum number of results to return
            
        Returns:
            List of objects within the radius, sorted by distance
        """
        results = []
        
        # Convert center to numpy array for easier calculations
        center_np = np.array(center)
        
        # Check each object
        for obj_id, obj in self.spatial_objects.items():
            # Skip if not visible
            if not obj["is_visible"]:
                continue
                
            # Skip if type doesn't match filter
            if object_type is not None and obj["object_type"] != object_type:
                continue
                
            # Get object position
            if obj["anchor_id"] is not None and obj["anchor_id"] in self.spatial_anchors:
                # Object is anchored, use anchor position
                anchor = self.spatial_anchors[obj["anchor_id"]]
                position = anchor["position"]
            else:
                # Object has its own position
                position = obj["position"]
                
            # Calculate distance
            position_np = np.array(position)
            distance = np.linalg.norm(position_np - center_np)
            
            # Check if within radius
            if distance <= radius:
                results.append({
                    "object_id": obj_id,
                    "object_type": obj["object_type"],
                    "position": position,
                    "distance": distance,
                    "metadata": obj["metadata"]
                })
                
        # Sort by distance
        results.sort(key=lambda x: x["distance"])
        
        # Limit results
        return results[:max_results]
    
    def get_objects_in_zone(self, zone_id: str) -> List[str]:
        """
        Get IDs of spatial objects currently in a zone.
        
        Args:
            zone_id: ID of the zone
            
        Returns:
            List of object IDs in the zone
        """
        if zone_id not in self.spatial_zones:
            self.logger.warning(f"Spatial zone {zone_id} not found.")
            return []
            
        return self.spatial_zones[zone_id]["contained_objects"]
    
    def get_users_in_zone(self, zone_id: str) -> List[str]:
        """
        Get IDs of users currently in a zone.
        
        Args:
            zone_id: ID of the zone
            
        Returns:
            List of user IDs in the zone
        """
        if zone_id not in self.spatial_zones:
            self.logger.warning(f"Spatial zone {zone_id} not found.")
            return []
            
        return self.spatial_zones[zone_id]["contained_users"]
    
    def get_zones_for_user(self, user_id: str) -> List[str]:
        """
        Get IDs of zones a user is currently in.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of zone IDs the user is in
        """
        if user_id not in self.tracked_users:
            self.logger.warning(f"User {user_id} not being tracked.")
            return []
            
        return self.tracked_users[user_id]["current_zones"]
    
    def get_world_to_screen_position(self,
                                   world_position: Tuple[float, float, float],
                                   camera_position: Tuple[float, float, float],
                                   camera_rotation: Tuple[float, float, float, float],
                                   field_of_view: float,
                                   aspect_ratio: float,
                                   near_clip: float = 0.1,
                                   far_clip: float = 1000.0) -> Optional[Tuple[float, float, bool]]:
        """
        Convert a 3D world position to a 2D screen position.
        
        Args:
            world_position: 3D position in world space
            camera_position: 3D camera position
            camera_rotation: Camera rotation as quaternion (x, y, z, w)
            field_of_view: Vertical field of view in degrees
            aspect_ratio: Screen aspect ratio (width / height)
            near_clip: Near clip plane distance
            far_clip: Far clip plane distance
            
        Returns:
            Tuple of (screen_x, screen_y, is_visible) where screen coordinates are in range [-1, 1],
            or None if the calculation fails
        """
        try:
            # Convert to numpy arrays
            world_pos = np.array(world_position)
            cam_pos = np.array(camera_position)
            
            # Create view matrix from camera position and rotation
            # This is a simplified version; a real implementation would use proper quaternion to matrix conversion
            qx, qy, qz, qw = camera_rotation
            
            # Convert quaternion to rotation matrix
            rotation_matrix = np.array([
                [1 - 2*qy*qy - 2*qz*qz, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
                [2*qx*qy + 2*qz*qw, 1 - 2*qx*qx - 2*qz*qz, 2*qy*qz - 2*qx*qw],
                [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx*qx - 2*qy*qy]
            ])
            
            # Create view matrix
            view_matrix = np.eye(4)
            view_matrix[:3, :3] = rotation_matrix
            view_matrix[:3, 3] = -rotation_matrix @ cam_pos
            
            # Create projection matrix
            fov_rad = math.radians(field_of_view)
            f = 1.0 / math.tan(fov_rad / 2)
            
            projection_matrix = np.zeros((4, 4))
            projection_matrix[0, 0] = f / aspect_ratio
            projection_matrix[1, 1] = f
            projection_matrix[2, 2] = (far_clip + near_clip) / (near_clip - far_clip)
            projection_matrix[2, 3] = (2 * far_clip * near_clip) / (near_clip - far_clip)
            projection_matrix[3, 2] = -1
            
            # Convert world position to homogeneous coordinates
            world_pos_h = np.append(world_pos, 1)
            
            # Transform to view space
            view_pos = view_matrix @ world_pos_h
            
            # Check if behind camera
            if view_pos[2] > 0:
                return (0, 0, False)
                
            # Transform to clip space
            clip_pos = projection_matrix @ view_pos
            
            # Perspective division
            if abs(clip_pos[3]) > 1e-6:
                ndc_pos = clip_pos / clip_pos[3]
            else:
                return (0, 0, False)
                
            # Check if in frustum
            is_visible = (
                ndc_pos[0] >= -1 and ndc_pos[0] <= 1 and
                ndc_pos[1] >= -1 and ndc_pos[1] <= 1 and
                ndc_pos[2] >= -1 and ndc_pos[2] <= 1
            )
            
            return (ndc_pos[0], ndc_pos[1], is_visible)
            
        except Exception as e:
            self.logger.error(f"Error in world to screen conversion: {e}")
            return None
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for spatial awareness events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for spatial awareness events.
        
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
        event_data["source"] = "SpatialAwarenessEngine"
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in spatial awareness event listener: {e}")
                
    def _initialize_spatial_backend(self) -> Any:
        """Placeholder for initializing the spatial backend."""
        # In a real implementation, this would initialize a spatial tracking system
        # For now, we'll just return a dummy object
        return object()
    
    def _load_spatial_data_from_config(self) -> None:
        """Load spatial data from the configuration."""
        # Load anchors
        anchors_config = self.config.get("spatial_anchors", [])
        for anchor_config in anchors_config:
            try:
                anchor_id = anchor_config["anchor_id"]
                anchor_type = SpatialAnchorType(anchor_config["anchor_type"])
                position = anchor_config["position"]
                rotation = anchor_config.get("rotation")
                scale = anchor_config.get("scale")
                parent_id = anchor_config.get("parent_id")
                valid_contexts = [SpatialContextType(ctx) for ctx in anchor_config.get("valid_contexts", [])] if "valid_contexts" in anchor_config else None
                metadata = anchor_config.get("metadata")
                
                self.create_spatial_anchor(
                    anchor_id=anchor_id,
                    anchor_type=anchor_type,
                    position=position,
                    rotation=rotation,
                    scale=scale,
                    parent_id=parent_id,
                    valid_contexts=valid_contexts,
                    metadata=metadata
                )
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error loading spatial anchor from config: {e}")
                
        # Load objects
        objects_config = self.config.get("spatial_objects", [])
        for object_config in objects_config:
            try:
                object_id = object_config["object_id"]
                object_type = object_config["object_type"]
                anchor_id = object_config.get("anchor_id")
                position = object_config.get("position")
                rotation = object_config.get("rotation")
                scale = object_config.get("scale")
                valid_contexts = [SpatialContextType(ctx) for ctx in object_config.get("valid_contexts", [])] if "valid_contexts" in object_config else None
                interaction_modes = [SpatialInteractionMode(mode) for mode in object_config.get("interaction_modes", [])] if "interaction_modes" in object_config else None
                metadata = object_config.get("metadata")
                
                self.create_spatial_object(
                    object_id=object_id,
                    object_type=object_type,
                    anchor_id=anchor_id,
                    position=position,
                    rotation=rotation,
                    scale=scale,
                    valid_contexts=valid_contexts,
                    interaction_modes=interaction_modes,
                    metadata=metadata
                )
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error loading spatial object from config: {e}")
                
        # Load zones
        zones_config = self.config.get("spatial_zones", [])
        for zone_config in zones_config:
            try:
                zone_id = zone_config["zone_id"]
                zone_type = zone_config["zone_type"]
                center = zone_config["center"]
                size = zone_config["size"]
                rotation = zone_config.get("rotation")
                valid_contexts = [SpatialContextType(ctx) for ctx in zone_config.get("valid_contexts", [])] if "valid_contexts" in zone_config else None
                metadata = zone_config.get("metadata")
                
                self.create_spatial_zone(
                    zone_id=zone_id,
                    zone_type=zone_type,
                    center=center,
                    size=size,
                    rotation=rotation,
                    valid_contexts=valid_contexts,
                    metadata=metadata
                )
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error loading spatial zone from config: {e}")
                
    def _context_update_loop(self) -> None:
        """Background thread for updating spatial context."""
        while self.is_active:
            try:
                # In a real implementation, this would use sensor data, device position, etc.
                # to determine the current spatial context
                # For now, we'll just simulate context detection
                
                # --- Spatial Backend Interaction (Placeholder) ---
                # context_data = self.spatial_backend.detect_context()
                # if context_data:
                #     context_type = SpatialContextType(context_data["context_type"])
                #     confidence = context_data["confidence"]
                #     self.set_current_context(context_type, confidence)
                # --- End Spatial Backend Interaction ---
                
                # Simulate context detection
                if random.random() < 0.01:  # 1% chance of context change
                    contexts = list(SpatialContextType)
                    new_context = random.choice(contexts)
                    confidence = random.uniform(0.7, 1.0)
                    self.set_current_context(new_context, confidence)
                    
            except Exception as e:
                self.logger.error(f"Error in context update loop: {e}")
                
            # Sleep until next update
            time.sleep(self.context_update_interval)
            
    def _proximity_check_loop(self) -> None:
        """Background thread for checking proximity between objects, users, and zones."""
        while self.is_active:
            try:
                # Check object-zone intersections
                for object_id, obj in self.spatial_objects.items():
                    self._check_object_zone_intersections(object_id)
                    
                # Check user-zone intersections
                for user_id in self.tracked_users:
                    self._check_user_zone_intersections(user_id)
                    
                # Check device-zone intersections
                for device_id in self.tracked_devices:
                    self._check_device_zone_intersections(device_id)
                    
            except Exception as e:
                self.logger.error(f"Error in proximity check loop: {e}")
                
            # Sleep until next check
            time.sleep(self.proximity_check_interval)
            
    def _check_object_zone_intersections(self, object_id: str) -> None:
        """
        Check if an object intersects with any zones.
        
        Args:
            object_id: ID of the object to check
        """
        if object_id not in self.spatial_objects:
            return
            
        obj = self.spatial_objects[object_id]
        
        # Get object position
        if obj["anchor_id"] is not None and obj["anchor_id"] in self.spatial_anchors:
            # Object is anchored, use anchor position
            anchor = self.spatial_anchors[obj["anchor_id"]]
            position = anchor["position"]
        else:
            # Object has its own position
            position = obj["position"]
            
        # Convert to numpy array
        position_np = np.array(position)
        
        # Check each zone
        for zone_id, zone in self.spatial_zones.items():
            # Skip if context doesn't match
            if self.current_context is not None and self.current_context not in zone["valid_contexts"]:
                continue
                
            # Check if object is in zone
            is_in_zone = self._is_point_in_zone(position_np, zone)
            
            # Check if zone containment changed
            currently_in_zone = object_id in zone["contained_objects"]
            
            if is_in_zone and not currently_in_zone:
                # Object entered zone
                zone["contained_objects"].append(object_id)
                
                # Dispatch event
                self._dispatch_event({
                    "event_type": "object_entered_zone",
                    "object_id": object_id,
                    "object_type": obj["object_type"],
                    "zone_id": zone_id,
                    "zone_type": zone["zone_type"]
                })
                
            elif not is_in_zone and currently_in_zone:
                # Object exited zone
                zone["contained_objects"].remove(object_id)
                
                # Dispatch event
                self._dispatch_event({
                    "event_type": "object_exited_zone",
                    "object_id": object_id,
                    "object_type": obj["object_type"],
                    "zone_id": zone_id,
                    "zone_type": zone["zone_type"]
                })
                
    def _check_user_zone_intersections(self, user_id: str) -> None:
        """
        Check if a user intersects with any zones.
        
        Args:
            user_id: ID of the user to check
        """
        if user_id not in self.tracked_users:
            return
            
        user = self.tracked_users[user_id]
        position_np = np.array(user["position"])
        
        # Track zones the user is currently in
        current_zones = []
        
        # Check each zone
        for zone_id, zone in self.spatial_zones.items():
            # Skip if context doesn't match
            if self.current_context is not None and self.current_context not in zone["valid_contexts"]:
                continue
                
            # Check if user is in zone
            is_in_zone = self._is_point_in_zone(position_np, zone)
            
            # Check if zone containment changed
            currently_in_zone = user_id in zone["contained_users"]
            
            if is_in_zone:
                current_zones.append(zone_id)
                
            if is_in_zone and not currently_in_zone:
                # User entered zone
                zone["contained_users"].append(user_id)
                
                # Dispatch event
                self._dispatch_event({
                    "event_type": "user_entered_zone",
                    "user_id": user_id,
                    "zone_id": zone_id,
                    "zone_type": zone["zone_type"]
                })
                
            elif not is_in_zone and currently_in_zone:
                # User exited zone
                zone["contained_users"].remove(user_id)
                
                # Dispatch event
                self._dispatch_event({
                    "event_type": "user_exited_zone",
                    "user_id": user_id,
                    "zone_id": zone_id,
                    "zone_type": zone["zone_type"]
                })
                
        # Update user's current zones
        user["current_zones"] = current_zones
        
    def _check_device_zone_intersections(self, device_id: str) -> None:
        """
        Check if a device intersects with any zones.
        
        Args:
            device_id: ID of the device to check
        """
        if device_id not in self.tracked_devices:
            return
            
        device = self.tracked_devices[device_id]
        position_np = np.array(device["position"])
        
        # Track zones the device is currently in
        current_zones = []
        
        # Check each zone
        for zone_id, zone in self.spatial_zones.items():
            # Skip if context doesn't match
            if self.current_context is not None and self.current_context not in zone["valid_contexts"]:
                continue
                
            # Check if device is in zone
            is_in_zone = self._is_point_in_zone(position_np, zone)
            
            # Track current zones
            if is_in_zone:
                current_zones.append(zone_id)
                
        # Update device's current zones
        device["current_zones"] = current_zones
        
    def _is_point_in_zone(self, point: np.ndarray, zone: Dict[str, Any]) -> bool:
        """
        Check if a point is inside a zone.
        
        Args:
            point: 3D point as numpy array
            zone: Zone data
            
        Returns:
            True if the point is in the zone, False otherwise
        """
        # Get zone parameters
        center = np.array(zone["center"])
        half_size = np.array(zone["size"]) / 2
        
        # For simplicity, we'll just check an axis-aligned bounding box
        # In a real implementation, this would account for zone rotation
        
        # Check if point is within bounds in all dimensions
        return (
            point[0] >= center[0] - half_size[0] and point[0] <= center[0] + half_size[0] and
            point[1] >= center[1] - half_size[1] and point[1] <= center[1] + half_size[1] and
            point[2] >= center[2] - half_size[2] and point[2] <= center[2] + half_size[2]
        )

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create spatial awareness engine
    spatial_config = {
        "context_update_interval": 1.0,
        "proximity_check_interval": 0.5,
        "max_interaction_history": 100,
        "spatial_anchors": [
            {
                "anchor_id": "machine_1",
                "anchor_type": "equipment",
                "position": (10.0, 0.0, 5.0)
            }
        ],
        "spatial_zones": [
            {
                "zone_id": "work_area_1",
                "zone_type": "industrial_zone",
                "center": (10.0, 0.0, 5.0),
                "size": (5.0, 5.0, 3.0)
            }
        ]
    }
    
    spatial_engine = SpatialAwarenessEngine(config=spatial_config)
    
    # Start the engine
    spatial_engine.start()
    
    # Set initial context
    spatial_engine.set_current_context(SpatialContextType.INDUSTRIAL_FLOOR, 0.9)
    
    # Create a spatial anchor
    spatial_engine.create_spatial_anchor(
        anchor_id="control_panel",
        anchor_type=SpatialAnchorType.EQUIPMENT,
        position=(12.0, 1.5, 5.0),
        metadata={"equipment_id": "panel_1", "description": "Main control panel"}
    )
    
    # Create a spatial object
    spatial_engine.create_spatial_object(
        object_id="status_display",
        object_type="ui_element",
        anchor_id="control_panel",
        interaction_modes=[SpatialInteractionMode.DIRECT, SpatialInteractionMode.GAZE],
        metadata={"ui_type": "status", "description": "Machine status display"}
    )
    
    # Create a spatial zone
    spatial_engine.create_spatial_zone(
        zone_id="safety_zone",
        zone_type="safety",
        center=(10.0, 0.0, 5.0),
        size=(8.0, 8.0, 4.0),
        metadata={"safety_level": "caution", "description": "Machine operation safety zone"}
    )
    
    # Track a user
    spatial_engine.track_user(
        user_id="user_1",
        position=(9.0, 0.0, 4.0),
        rotation=(0.0, 0.0, 0.0, 1.0),
        metadata={"role": "operator", "name": "John Doe"}
    )
    
    # Record an interaction
    spatial_engine.record_spatial_interaction(
        object_id="status_display",
        interaction_type=SpatialInteractionMode.DIRECT,
        user_id="user_1",
        position=(12.0, 1.5, 5.0),
        metadata={"action": "check_status"}
    )
    
    # Find objects near a point
    nearby_objects = spatial_engine.get_objects_in_radius(
        center=(11.0, 1.0, 5.0),
        radius=2.0
    )
    
    print(f"Found {len(nearby_objects)} objects nearby")
    
    # Get users in a zone
    users_in_zone = spatial_engine.get_users_in_zone("safety_zone")
    print(f"Users in safety zone: {users_in_zone}")
    
    # Wait a bit to see events
    time.sleep(5)
    
    # Stop the engine
    spatial_engine.stop()
"""
