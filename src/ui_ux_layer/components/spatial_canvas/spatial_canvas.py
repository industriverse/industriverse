"""
Spatial Canvas Component for the Industriverse UI/UX Layer.

This module provides a comprehensive spatial canvas for visualizing and interacting with
industrial spatial data, digital twins, and ambient intelligence elements in 2D and 3D space.

Author: Manus
"""

import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass, field

class SpatialMode(Enum):
    """Enumeration of spatial canvas modes."""
    MODE_2D = "2d"
    MODE_3D = "3d"
    MODE_AR = "ar"
    MODE_VR = "vr"
    MODE_HYBRID = "hybrid"

class SpatialObjectType(Enum):
    """Enumeration of spatial object types."""
    POINT = "point"
    LINE = "line"
    POLYGON = "polygon"
    MESH = "mesh"
    MODEL = "model"
    MARKER = "marker"
    ANNOTATION = "annotation"
    HEATMAP = "heatmap"
    FLOW = "flow"
    CONTAINER = "container"
    CUSTOM = "custom"

class InteractionMode(Enum):
    """Enumeration of interaction modes."""
    VIEW = "view"
    SELECT = "select"
    MOVE = "move"
    ROTATE = "rotate"
    SCALE = "scale"
    DRAW = "draw"
    MEASURE = "measure"
    ANNOTATE = "annotate"
    CUSTOM = "custom"

@dataclass
class SpatialVector:
    """Data class representing a 3D vector."""
    x: float
    y: float
    z: float = 0.0

@dataclass
class SpatialTransform:
    """Data class representing a spatial transform."""
    position: SpatialVector
    rotation: SpatialVector = field(default_factory=lambda: SpatialVector(0, 0, 0))
    scale: SpatialVector = field(default_factory=lambda: SpatialVector(1, 1, 1))

@dataclass
class SpatialStyle:
    """Data class representing visual style for spatial objects."""
    color: Optional[str] = None
    opacity: float = 1.0
    line_width: Optional[float] = None
    fill: bool = True
    fill_color: Optional[str] = None
    fill_opacity: Optional[float] = None
    texture: Optional[str] = None
    material: Optional[Dict[str, Any]] = None
    visible: bool = True
    render_order: int = 0
    custom_style: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SpatialObject:
    """Data class representing a spatial object."""
    object_id: str
    type: SpatialObjectType
    transform: SpatialTransform
    style: SpatialStyle
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    interactive: bool = True
    timestamp: float = field(default_factory=time.time)

@dataclass
class SpatialLayer:
    """Data class representing a spatial layer."""
    layer_id: str
    name: str
    objects: Dict[str, SpatialObject] = field(default_factory=dict)
    visible: bool = True
    locked: bool = False
    opacity: float = 1.0
    render_order: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SpatialCamera:
    """Data class representing a camera in spatial canvas."""
    position: SpatialVector
    target: SpatialVector
    up: SpatialVector = field(default_factory=lambda: SpatialVector(0, 1, 0))
    fov: float = 60.0
    near: float = 0.1
    far: float = 1000.0
    orthographic: bool = False
    orthographic_size: float = 10.0

@dataclass
class SpatialEnvironment:
    """Data class representing the spatial environment."""
    skybox: Optional[str] = None
    ambient_light: Optional[Dict[str, Any]] = None
    directional_lights: List[Dict[str, Any]] = field(default_factory=list)
    point_lights: List[Dict[str, Any]] = field(default_factory=list)
    spot_lights: List[Dict[str, Any]] = field(default_factory=list)
    fog: Optional[Dict[str, Any]] = None
    grid: Optional[Dict[str, Any]] = None
    axes: Optional[Dict[str, Any]] = None
    background_color: Optional[str] = None
    custom_environment: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SpatialSelection:
    """Data class representing a selection in the spatial canvas."""
    selected_objects: List[str]
    selection_box: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class SpatialEvent:
    """Data class representing an event in the spatial canvas."""
    event_type: str
    source: str
    target: Optional[str] = None
    position: Optional[SpatialVector] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class SpatialCanvasComponent:
    """
    Provides a comprehensive spatial canvas for the Industriverse UI/UX Layer.
    
    This class provides:
    - 2D and 3D spatial visualization
    - AR and VR mode support
    - Digital twin visualization and interaction
    - Spatial data visualization
    - Interactive spatial manipulation
    - Multi-layer spatial composition
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Spatial Canvas Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.mode = SpatialMode.MODE_3D
        self.interaction_mode = InteractionMode.VIEW
        self.layers: Dict[str, SpatialLayer] = {}
        self.active_layer_id: Optional[str] = None
        self.camera = SpatialCamera(
            position=SpatialVector(0, 5, 10),
            target=SpatialVector(0, 0, 0)
        )
        self.environment = SpatialEnvironment(
            background_color="#f0f0f0",
            grid={"visible": True, "size": 10, "divisions": 10, "color": "#888888"},
            axes={"visible": True, "size": 5}
        )
        self.selection = SpatialSelection(selected_objects=[])
        self.history: List[Dict[str, Any]] = []
        self.history_index = -1
        self.max_history = 50
        self.event_listeners: Dict[str, List[Callable[[SpatialEvent], None]]] = {}
        self.object_listeners: Dict[str, List[Callable[[SpatialObject], None]]] = {}
        self.layer_listeners: Dict[str, List[Callable[[SpatialLayer], None]]] = {}
        self.global_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize renderers
        self.renderers = {
            SpatialObjectType.POINT: self._render_point,
            SpatialObjectType.LINE: self._render_line,
            SpatialObjectType.POLYGON: self._render_polygon,
            SpatialObjectType.MESH: self._render_mesh,
            SpatialObjectType.MODEL: self._render_model,
            SpatialObjectType.MARKER: self._render_marker,
            SpatialObjectType.ANNOTATION: self._render_annotation,
            SpatialObjectType.HEATMAP: self._render_heatmap,
            SpatialObjectType.FLOW: self._render_flow,
            SpatialObjectType.CONTAINER: self._render_container,
            SpatialObjectType.CUSTOM: self._render_custom
        }
        
        # Create default layer
        self.create_layer("default", "Default Layer")
        self.active_layer_id = "default"
        
    def start(self) -> bool:
        """
        Start the Spatial Canvas Component.
        
        Returns:
            True if the component was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="canvas_started",
            source="SpatialCanvasComponent",
            data={}
        ))
        
        self.logger.info("Spatial Canvas Component started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Spatial Canvas Component.
        
        Returns:
            True if the component was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="canvas_stopped",
            source="SpatialCanvasComponent",
            data={}
        ))
        
        self.logger.info("Spatial Canvas Component stopped.")
        return True
    
    def set_mode(self, mode: SpatialMode) -> bool:
        """
        Set the spatial canvas mode.
        
        Args:
            mode: The spatial mode to set
            
        Returns:
            True if the mode was set, False if invalid
        """
        if not isinstance(mode, SpatialMode):
            try:
                mode = SpatialMode(mode)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid spatial mode: {mode}")
                return False
                
        old_mode = self.mode
        self.mode = mode
        
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="mode_changed",
            source="SpatialCanvasComponent",
            data={"old_mode": old_mode.value, "new_mode": mode.value}
        ))
        
        self.logger.debug(f"Spatial mode set to: {mode.value}")
        return True
    
    def set_interaction_mode(self, mode: InteractionMode) -> bool:
        """
        Set the interaction mode.
        
        Args:
            mode: The interaction mode to set
            
        Returns:
            True if the mode was set, False if invalid
        """
        if not isinstance(mode, InteractionMode):
            try:
                mode = InteractionMode(mode)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid interaction mode: {mode}")
                return False
                
        old_mode = self.interaction_mode
        self.interaction_mode = mode
        
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="interaction_mode_changed",
            source="SpatialCanvasComponent",
            data={"old_mode": old_mode.value, "new_mode": mode.value}
        ))
        
        self.logger.debug(f"Interaction mode set to: {mode.value}")
        return True
    
    def create_layer(self, layer_id: Optional[str] = None, name: Optional[str] = None) -> str:
        """
        Create a new spatial layer.
        
        Args:
            layer_id: Optional layer ID, generated if not provided
            name: Optional layer name, defaults to "Layer {id}"
            
        Returns:
            The layer ID
        """
        # Generate layer ID if not provided
        if layer_id is None:
            layer_id = str(uuid.uuid4())
            
        # Generate layer name if not provided
        if name is None:
            name = f"Layer {layer_id[:8]}"
            
        # Create layer
        layer = SpatialLayer(
            layer_id=layer_id,
            name=name
        )
        
        # Store layer
        self.layers[layer_id] = layer
        
        # Set as active layer if no active layer
        if self.active_layer_id is None:
            self.active_layer_id = layer_id
            
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="layer_created",
            source="SpatialCanvasComponent",
            target=layer_id,
            data={"layer_name": name}
        ))
        
        # Notify layer listeners
        self._notify_layer_listeners(layer)
        
        self.logger.debug(f"Created layer: {layer_id} ({name})")
        return layer_id
    
    def get_layer(self, layer_id: str) -> Optional[SpatialLayer]:
        """
        Get a layer by ID.
        
        Args:
            layer_id: ID of the layer to get
            
        Returns:
            The layer, or None if not found
        """
        return self.layers.get(layer_id)
    
    def set_active_layer(self, layer_id: str) -> bool:
        """
        Set the active layer.
        
        Args:
            layer_id: ID of the layer to set as active
            
        Returns:
            True if the layer was set as active, False if not found
        """
        if layer_id not in self.layers:
            self.logger.warning(f"Layer {layer_id} not found.")
            return False
            
        old_layer_id = self.active_layer_id
        self.active_layer_id = layer_id
        
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="active_layer_changed",
            source="SpatialCanvasComponent",
            target=layer_id,
            data={"old_layer_id": old_layer_id}
        ))
        
        self.logger.debug(f"Set active layer: {layer_id}")
        return True
    
    def update_layer(self,
                   layer_id: str,
                   name: Optional[str] = None,
                   visible: Optional[bool] = None,
                   locked: Optional[bool] = None,
                   opacity: Optional[float] = None,
                   render_order: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a layer.
        
        Args:
            layer_id: ID of the layer to update
            name: Optional new name
            visible: Optional new visibility
            locked: Optional new locked state
            opacity: Optional new opacity
            render_order: Optional new render order
            metadata: Optional new metadata
            
        Returns:
            True if the layer was updated, False if not found
        """
        if layer_id not in self.layers:
            self.logger.warning(f"Layer {layer_id} not found.")
            return False
            
        layer = self.layers[layer_id]
        
        # Update properties
        if name is not None:
            layer.name = name
        if visible is not None:
            layer.visible = visible
        if locked is not None:
            layer.locked = locked
        if opacity is not None:
            layer.opacity = opacity
        if render_order is not None:
            layer.render_order = render_order
        if metadata is not None:
            layer.metadata.update(metadata)
            
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="layer_updated",
            source="SpatialCanvasComponent",
            target=layer_id,
            data={"layer_name": layer.name}
        ))
        
        # Notify layer listeners
        self._notify_layer_listeners(layer)
        
        self.logger.debug(f"Updated layer: {layer_id} ({layer.name})")
        return True
    
    def delete_layer(self, layer_id: str) -> bool:
        """
        Delete a layer.
        
        Args:
            layer_id: ID of the layer to delete
            
        Returns:
            True if the layer was deleted, False if not found
        """
        if layer_id not in self.layers:
            self.logger.warning(f"Layer {layer_id} not found.")
            return False
            
        # Cannot delete the last layer
        if len(self.layers) <= 1:
            self.logger.warning("Cannot delete the last layer.")
            return False
            
        layer = self.layers[layer_id]
        
        # Remove layer
        del self.layers[layer_id]
        
        # Update active layer if needed
        if self.active_layer_id == layer_id:
            # Set first available layer as active
            self.active_layer_id = next(iter(self.layers.keys()))
            
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="layer_deleted",
            source="SpatialCanvasComponent",
            target=layer_id,
            data={"layer_name": layer.name}
        ))
        
        self.logger.debug(f"Deleted layer: {layer_id} ({layer.name})")
        return True
    
    def create_object(self,
                    type: SpatialObjectType,
                    position: Union[SpatialVector, Dict[str, float], Tuple[float, float, float]],
                    data: Any,
                    object_id: Optional[str] = None,
                    rotation: Optional[Union[SpatialVector, Dict[str, float], Tuple[float, float, float]]] = None,
                    scale: Optional[Union[SpatialVector, Dict[str, float], Tuple[float, float, float]]] = None,
                    style: Optional[Dict[str, Any]] = None,
                    layer_id: Optional[str] = None,
                    parent: Optional[str] = None,
                    interactive: bool = True,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new spatial object.
        
        Args:
            type: Type of spatial object
            position: Position vector
            data: Object-specific data
            object_id: Optional object ID, generated if not provided
            rotation: Optional rotation vector
            scale: Optional scale vector
            style: Optional style properties
            layer_id: Optional layer ID, uses active layer if not provided
            parent: Optional parent object ID
            interactive: Whether the object is interactive
            metadata: Optional metadata
            
        Returns:
            The object ID
        """
        # Generate object ID if not provided
        if object_id is None:
            object_id = str(uuid.uuid4())
            
        # Use active layer if not provided
        if layer_id is None:
            layer_id = self.active_layer_id
            
        if layer_id not in self.layers:
            self.logger.warning(f"Layer {layer_id} not found, using default layer.")
            layer_id = "default"
            
        # Convert position to SpatialVector if needed
        if not isinstance(position, SpatialVector):
            if isinstance(position, dict):
                position = SpatialVector(
                    x=position.get("x", 0),
                    y=position.get("y", 0),
                    z=position.get("z", 0)
                )
            elif isinstance(position, (list, tuple)) and len(position) >= 2:
                position = SpatialVector(
                    x=position[0],
                    y=position[1],
                    z=position[2] if len(position) > 2 else 0
                )
            else:
                position = SpatialVector(0, 0, 0)
                
        # Convert rotation to SpatialVector if needed
        if rotation is not None and not isinstance(rotation, SpatialVector):
            if isinstance(rotation, dict):
                rotation = SpatialVector(
                    x=rotation.get("x", 0),
                    y=rotation.get("y", 0),
                    z=rotation.get("z", 0)
                )
            elif isinstance(rotation, (list, tuple)) and len(rotation) >= 2:
                rotation = SpatialVector(
                    x=rotation[0],
                    y=rotation[1],
                    z=rotation[2] if len(rotation) > 2 else 0
                )
            else:
                rotation = SpatialVector(0, 0, 0)
        else:
            rotation = SpatialVector(0, 0, 0)
            
        # Convert scale to SpatialVector if needed
        if scale is not None and not isinstance(scale, SpatialVector):
            if isinstance(scale, dict):
                scale = SpatialVector(
                    x=scale.get("x", 1),
                    y=scale.get("y", 1),
                    z=scale.get("z", 1)
                )
            elif isinstance(scale, (list, tuple)) and len(scale) >= 2:
                scale = SpatialVector(
                    x=scale[0],
                    y=scale[1],
                    z=scale[2] if len(scale) > 2 else 1
                )
            else:
                scale = SpatialVector(1, 1, 1)
        else:
            scale = SpatialVector(1, 1, 1)
            
        # Create transform
        transform = SpatialTransform(
            position=position,
            rotation=rotation,
            scale=scale
        )
        
        # Create style
        style_obj = SpatialStyle()
        if style:
            for key, value in style.items():
                if hasattr(style_obj, key):
                    setattr(style_obj, key, value)
                else:
                    style_obj.custom_style[key] = value
                    
        # Convert type to SpatialObjectType if needed
        if not isinstance(type, SpatialObjectType):
            try:
                type = SpatialObjectType(type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid spatial object type: {type}, using CUSTOM.")
                type = SpatialObjectType.CUSTOM
                
        # Create object
        obj = SpatialObject(
            object_id=object_id,
            type=type,
            transform=transform,
            style=style_obj,
            data=data,
            metadata=metadata or {},
            parent=parent,
            interactive=interactive
        )
        
        # Add to layer
        layer = self.layers[layer_id]
        layer.objects[object_id] = obj
        
        # Add to parent's children if parent exists
        if parent and parent in layer.objects:
            parent_obj = layer.objects[parent]
            parent_obj.children.append(object_id)
            
        # Add to history
        self._add_to_history({
            "action": "create_object",
            "object_id": object_id,
            "layer_id": layer_id,
            "object": obj
        })
        
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="object_created",
            source="SpatialCanvasComponent",
            target=object_id,
            data={"type": type.value, "layer_id": layer_id}
        ))
        
        # Notify object listeners
        self._notify_object_listeners(obj)
        
        self.logger.debug(f"Created object: {object_id} ({type.value}) in layer {layer_id}")
        return object_id
    
    def get_object(self, object_id: str, layer_id: Optional[str] = None) -> Optional[SpatialObject]:
        """
        Get an object by ID.
        
        Args:
            object_id: ID of the object to get
            layer_id: Optional layer ID, searches all layers if not provided
            
        Returns:
            The object, or None if not found
        """
        if layer_id:
            if layer_id not in self.layers:
                return None
            return self.layers[layer_id].objects.get(object_id)
            
        # Search all layers
        for layer in self.layers.values():
            if object_id in layer.objects:
                return layer.objects[object_id]
                
        return None
    
    def update_object(self,
                    object_id: str,
                    position: Optional[Union[SpatialVector, Dict[str, float], Tuple[float, float, float]]] = None,
                    rotation: Optional[Union[SpatialVector, Dict[str, float], Tuple[float, float, float]]] = None,
                    scale: Optional[Union[SpatialVector, Dict[str, float], Tuple[float, float, float]]] = None,
                    style: Optional[Dict[str, Any]] = None,
                    data: Optional[Any] = None,
                    interactive: Optional[bool] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    layer_id: Optional[str] = None) -> bool:
        """
        Update an object.
        
        Args:
            object_id: ID of the object to update
            position: Optional new position
            rotation: Optional new rotation
            scale: Optional new scale
            style: Optional new style properties
            data: Optional new data
            interactive: Optional new interactive state
            metadata: Optional new metadata
            layer_id: Optional layer ID, searches all layers if not provided
            
        Returns:
            True if the object was updated, False if not found
        """
        # Find the object
        obj = None
        obj_layer_id = None
        
        if layer_id:
            if layer_id not in self.layers:
                self.logger.warning(f"Layer {layer_id} not found.")
                return False
            if object_id not in self.layers[layer_id].objects:
                self.logger.warning(f"Object {object_id} not found in layer {layer_id}.")
                return False
            obj = self.layers[layer_id].objects[object_id]
            obj_layer_id = layer_id
        else:
            # Search all layers
            for lid, layer in self.layers.items():
                if object_id in layer.objects:
                    obj = layer.objects[object_id]
                    obj_layer_id = lid
                    break
                    
        if obj is None:
            self.logger.warning(f"Object {object_id} not found.")
            return False
            
        # Store old state for history
        old_obj = SpatialObject(
            object_id=obj.object_id,
            type=obj.type,
            transform=SpatialTransform(
                position=SpatialVector(obj.transform.position.x, obj.transform.position.y, obj.transform.position.z),
                rotation=SpatialVector(obj.transform.rotation.x, obj.transform.rotation.y, obj.transform.rotation.z),
                scale=SpatialVector(obj.transform.scale.x, obj.transform.scale.y, obj.transform.scale.z)
            ),
            style=obj.style,
            data=obj.data,
            metadata=obj.metadata.copy(),
            children=obj.children.copy(),
            parent=obj.parent,
            interactive=obj.interactive
        )
        
        # Update position if provided
        if position is not None:
            if not isinstance(position, SpatialVector):
                if isinstance(position, dict):
                    position = SpatialVector(
                        x=position.get("x", 0),
                        y=position.get("y", 0),
                        z=position.get("z", 0)
                    )
                elif isinstance(position, (list, tuple)) and len(position) >= 2:
                    position = SpatialVector(
                        x=position[0],
                        y=position[1],
                        z=position[2] if len(position) > 2 else 0
                    )
                else:
                    position = SpatialVector(0, 0, 0)
            obj.transform.position = position
            
        # Update rotation if provided
        if rotation is not None:
            if not isinstance(rotation, SpatialVector):
                if isinstance(rotation, dict):
                    rotation = SpatialVector(
                        x=rotation.get("x", 0),
                        y=rotation.get("y", 0),
                        z=rotation.get("z", 0)
                    )
                elif isinstance(rotation, (list, tuple)) and len(rotation) >= 2:
                    rotation = SpatialVector(
                        x=rotation[0],
                        y=rotation[1],
                        z=rotation[2] if len(rotation) > 2 else 0
                    )
                else:
                    rotation = SpatialVector(0, 0, 0)
            obj.transform.rotation = rotation
            
        # Update scale if provided
        if scale is not None:
            if not isinstance(scale, SpatialVector):
                if isinstance(scale, dict):
                    scale = SpatialVector(
                        x=scale.get("x", 1),
                        y=scale.get("y", 1),
                        z=scale.get("z", 1)
                    )
                elif isinstance(scale, (list, tuple)) and len(scale) >= 2:
                    scale = SpatialVector(
                        x=scale[0],
                        y=scale[1],
                        z=scale[2] if len(scale) > 2 else 1
                    )
                else:
                    scale = SpatialVector(1, 1, 1)
            obj.transform.scale = scale
            
        # Update style if provided
        if style:
            for key, value in style.items():
                if hasattr(obj.style, key):
                    setattr(obj.style, key, value)
                else:
                    obj.style.custom_style[key] = value
                    
        # Update data if provided
        if data is not None:
            obj.data = data
            
        # Update interactive if provided
        if interactive is not None:
            obj.interactive = interactive
            
        # Update metadata if provided
        if metadata:
            obj.metadata.update(metadata)
            
        # Update timestamp
        obj.timestamp = time.time()
        
        # Add to history
        self._add_to_history({
            "action": "update_object",
            "object_id": object_id,
            "layer_id": obj_layer_id,
            "old_object": old_obj,
            "new_object": obj
        })
        
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="object_updated",
            source="SpatialCanvasComponent",
            target=object_id,
            data={"type": obj.type.value, "layer_id": obj_layer_id}
        ))
        
        # Notify object listeners
        self._notify_object_listeners(obj)
        
        self.logger.debug(f"Updated object: {object_id} ({obj.type.value}) in layer {obj_layer_id}")
        return True
    
    def delete_object(self, object_id: str, layer_id: Optional[str] = None) -> bool:
        """
        Delete an object.
        
        Args:
            object_id: ID of the object to delete
            layer_id: Optional layer ID, searches all layers if not provided
            
        Returns:
            True if the object was deleted, False if not found
        """
        # Find the object
        obj = None
        obj_layer_id = None
        
        if layer_id:
            if layer_id not in self.layers:
                self.logger.warning(f"Layer {layer_id} not found.")
                return False
            if object_id not in self.layers[layer_id].objects:
                self.logger.warning(f"Object {object_id} not found in layer {layer_id}.")
                return False
            obj = self.layers[layer_id].objects[object_id]
            obj_layer_id = layer_id
        else:
            # Search all layers
            for lid, layer in self.layers.items():
                if object_id in layer.objects:
                    obj = layer.objects[object_id]
                    obj_layer_id = lid
                    break
                    
        if obj is None:
            self.logger.warning(f"Object {object_id} not found.")
            return False
            
        layer = self.layers[obj_layer_id]
        
        # Remove from parent's children if parent exists
        if obj.parent and obj.parent in layer.objects:
            parent_obj = layer.objects[obj.parent]
            if object_id in parent_obj.children:
                parent_obj.children.remove(object_id)
                
        # Remove children recursively
        for child_id in obj.children.copy():
            self.delete_object(child_id, obj_layer_id)
            
        # Add to history
        self._add_to_history({
            "action": "delete_object",
            "object_id": object_id,
            "layer_id": obj_layer_id,
            "object": obj
        })
        
        # Remove from selection if selected
        if object_id in self.selection.selected_objects:
            self.selection.selected_objects.remove(object_id)
            
        # Remove from layer
        del layer.objects[object_id]
        
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="object_deleted",
            source="SpatialCanvasComponent",
            target=object_id,
            data={"type": obj.type.value, "layer_id": obj_layer_id}
        ))
        
        self.logger.debug(f"Deleted object: {object_id} ({obj.type.value}) from layer {obj_layer_id}")
        return True
    
    def select_objects(self, object_ids: List[str], clear_existing: bool = True) -> bool:
        """
        Select objects.
        
        Args:
            object_ids: IDs of objects to select
            clear_existing: Whether to clear existing selection
            
        Returns:
            True if any objects were selected
        """
        old_selection = self.selection.selected_objects.copy()
        
        # Clear existing selection if requested
        if clear_existing:
            self.selection.selected_objects = []
            
        # Add objects to selection
        for object_id in object_ids:
            # Find the object
            obj = self.get_object(object_id)
            if obj is None:
                continue
                
            # Add to selection if not already selected
            if object_id not in self.selection.selected_objects:
                self.selection.selected_objects.append(object_id)
                
        # Update timestamp
        self.selection.timestamp = time.time()
        
        # Dispatch event if selection changed
        if old_selection != self.selection.selected_objects:
            self._dispatch_event(SpatialEvent(
                event_type="selection_changed",
                source="SpatialCanvasComponent",
                data={
                    "old_selection": old_selection,
                    "new_selection": self.selection.selected_objects
                }
            ))
            
            self.logger.debug(f"Selected objects: {self.selection.selected_objects}")
            return True
            
        return False
    
    def clear_selection(self) -> bool:
        """
        Clear the current selection.
        
        Returns:
            True if selection was cleared, False if already empty
        """
        if not self.selection.selected_objects:
            return False
            
        old_selection = self.selection.selected_objects.copy()
        self.selection.selected_objects = []
        self.selection.timestamp = time.time()
        
        # Dispatch event
        self._dispatch_event(SpatialEvent(
            event_type="selection_changed",
            source="SpatialCanvasComponent",
            data={
                "old_selection": old_selection,
                "new_selection": []
            }
        ))
        
        self.logger.debug("Cleared selection")
        return True
    
    def set_camera(self,
                 position: Optional[Union[SpatialVector, Dict[str, float], Tuple[float, float, float]]] = None,
                 target: Optional[Union[SpatialVector, Dict[str, float], Tuple[float, float, float]]] = None,
                 up: Optional[Union[SpatialVector, Dict[str, float], Tuple[float, float, float]]] = None,
                 fov: Optional[float] = None,
                 near: Optional[float] = None,
                 far: Optional[float] = None,
                 orthographic: Optional[bool] = None,
                 orthographic_size: Optional[float] = None) -> bool:
        """
        Set camera properties.
        
        Args:
            position: Optional new camera position
            target: Optional new camera target
            up: Optional new camera up vector
            fov: Optional new field of view
            near: Optional new near plane
            far: Optional new far plane
            orthographic: Optional new orthographic mode
            orthographic_size: Optional new orthographic size
            
        Returns:
            True if any properties were updated
        """
        updated = False
        
        # Update position if provided
        if position is not None:
            if not isinstance(position, SpatialVector):
                if isinstance(position, dict):
                    position = SpatialVector(
                        x=position.get("x", 0),
                        y=position.get("y", 0),
                        z=position.get("z", 0)
                    )
                elif isinstance(position, (list, tuple)) and len(position) >= 2:
                    position = SpatialVector(
                        x=position[0],
                        y=position[1],
                        z=position[2] if len(position) > 2 else 0
                    )
                else:
                    position = SpatialVector(0, 0, 0)
            self.camera.position = position
            updated = True
            
        # Update target if provided
        if target is not None:
            if not isinstance(target, SpatialVector):
                if isinstance(target, dict):
                    target = SpatialVector(
                        x=target.get("x", 0),
                        y=target.get("y", 0),
                        z=target.get("z", 0)
                    )
                elif isinstance(target, (list, tuple)) and len(target) >= 2:
                    target = SpatialVector(
                        x=target[0],
                        y=target[1],
                        z=target[2] if len(target) > 2 else 0
                    )
                else:
                    target = SpatialVector(0, 0, 0)
            self.camera.target = target
            updated = True
            
        # Update up if provided
        if up is not None:
            if not isinstance(up, SpatialVector):
                if isinstance(up, dict):
                    up = SpatialVector(
                        x=up.get("x", 0),
                        y=up.get("y", 1),
                        z=up.get("z", 0)
                    )
                elif isinstance(up, (list, tuple)) and len(up) >= 2:
                    up = SpatialVector(
                        x=up[0],
                        y=up[1],
                        z=up[2] if len(up) > 2 else 0
                    )
                else:
                    up = SpatialVector(0, 1, 0)
            self.camera.up = up
            updated = True
            
        # Update other properties if provided
        if fov is not None:
            self.camera.fov = fov
            updated = True
        if near is not None:
            self.camera.near = near
            updated = True
        if far is not None:
            self.camera.far = far
            updated = True
        if orthographic is not None:
            self.camera.orthographic = orthographic
            updated = True
        if orthographic_size is not None:
            self.camera.orthographic_size = orthographic_size
            updated = True
            
        if updated:
            # Dispatch event
            self._dispatch_event(SpatialEvent(
                event_type="camera_updated",
                source="SpatialCanvasComponent",
                data={"camera": self._camera_to_dict()}
            ))
            
            self.logger.debug("Updated camera")
            
        return updated
    
    def set_environment(self,
                      skybox: Optional[str] = None,
                      ambient_light: Optional[Dict[str, Any]] = None,
                      directional_lights: Optional[List[Dict[str, Any]]] = None,
                      point_lights: Optional[List[Dict[str, Any]]] = None,
                      spot_lights: Optional[List[Dict[str, Any]]] = None,
                      fog: Optional[Dict[str, Any]] = None,
                      grid: Optional[Dict[str, Any]] = None,
                      axes: Optional[Dict[str, Any]] = None,
                      background_color: Optional[str] = None,
                      custom_environment: Optional[Dict[str, Any]] = None) -> bool:
        """
        Set environment properties.
        
        Args:
            skybox: Optional new skybox texture
            ambient_light: Optional new ambient light properties
            directional_lights: Optional new directional lights
            point_lights: Optional new point lights
            spot_lights: Optional new spot lights
            fog: Optional new fog properties
            grid: Optional new grid properties
            axes: Optional new axes properties
            background_color: Optional new background color
            custom_environment: Optional new custom environment properties
            
        Returns:
            True if any properties were updated
        """
        updated = False
        
        # Update properties if provided
        if skybox is not None:
            self.environment.skybox = skybox
            updated = True
        if ambient_light is not None:
            self.environment.ambient_light = ambient_light
            updated = True
        if directional_lights is not None:
            self.environment.directional_lights = directional_lights
            updated = True
        if point_lights is not None:
            self.environment.point_lights = point_lights
            updated = True
        if spot_lights is not None:
            self.environment.spot_lights = spot_lights
            updated = True
        if fog is not None:
            self.environment.fog = fog
            updated = True
        if grid is not None:
            self.environment.grid = grid
            updated = True
        if axes is not None:
            self.environment.axes = axes
            updated = True
        if background_color is not None:
            self.environment.background_color = background_color
            updated = True
        if custom_environment is not None:
            self.environment.custom_environment.update(custom_environment)
            updated = True
            
        if updated:
            # Dispatch event
            self._dispatch_event(SpatialEvent(
                event_type="environment_updated",
                source="SpatialCanvasComponent",
                data={"environment": self._environment_to_dict()}
            ))
            
            self.logger.debug("Updated environment")
            
        return updated
    
    def undo(self) -> bool:
        """
        Undo the last action.
        
        Returns:
            True if an action was undone, False if no actions to undo
        """
        if self.history_index < 0 or len(self.history) == 0:
            return False
            
        # Get the action to undo
        action = self.history[self.history_index]
        
        # Decrement history index
        self.history_index -= 1
        
        # Undo the action
        if action["action"] == "create_object":
            # Delete the created object
            self.delete_object(action["object_id"], action["layer_id"])
            
        elif action["action"] == "update_object":
            # Restore the old object state
            old_obj = action["old_object"]
            layer_id = action["layer_id"]
            
            if layer_id in self.layers and old_obj.object_id in self.layers[layer_id].objects:
                self.layers[layer_id].objects[old_obj.object_id] = old_obj
                
                # Dispatch event
                self._dispatch_event(SpatialEvent(
                    event_type="object_updated",
                    source="SpatialCanvasComponent",
                    target=old_obj.object_id,
                    data={"type": old_obj.type.value, "layer_id": layer_id}
                ))
                
                # Notify object listeners
                self._notify_object_listeners(old_obj)
                
        elif action["action"] == "delete_object":
            # Restore the deleted object
            obj = action["object"]
            layer_id = action["layer_id"]
            
            if layer_id in self.layers:
                self.layers[layer_id].objects[obj.object_id] = obj
                
                # Restore parent-child relationship
                if obj.parent and obj.parent in self.layers[layer_id].objects:
                    parent_obj = self.layers[layer_id].objects[obj.parent]
                    if obj.object_id not in parent_obj.children:
                        parent_obj.children.append(obj.object_id)
                        
                # Dispatch event
                self._dispatch_event(SpatialEvent(
                    event_type="object_created",
                    source="SpatialCanvasComponent",
                    target=obj.object_id,
                    data={"type": obj.type.value, "layer_id": layer_id}
                ))
                
                # Notify object listeners
                self._notify_object_listeners(obj)
                
        # Dispatch undo event
        self._dispatch_event(SpatialEvent(
            event_type="undo",
            source="SpatialCanvasComponent",
            data={"action": action["action"]}
        ))
        
        self.logger.debug(f"Undid action: {action['action']}")
        return True
    
    def redo(self) -> bool:
        """
        Redo the last undone action.
        
        Returns:
            True if an action was redone, False if no actions to redo
        """
        if self.history_index >= len(self.history) - 1:
            return False
            
        # Increment history index
        self.history_index += 1
        
        # Get the action to redo
        action = self.history[self.history_index]
        
        # Redo the action
        if action["action"] == "create_object":
            # Recreate the object
            obj = action["object"]
            layer_id = action["layer_id"]
            
            if layer_id in self.layers:
                self.layers[layer_id].objects[obj.object_id] = obj
                
                # Restore parent-child relationship
                if obj.parent and obj.parent in self.layers[layer_id].objects:
                    parent_obj = self.layers[layer_id].objects[obj.parent]
                    if obj.object_id not in parent_obj.children:
                        parent_obj.children.append(obj.object_id)
                        
                # Dispatch event
                self._dispatch_event(SpatialEvent(
                    event_type="object_created",
                    source="SpatialCanvasComponent",
                    target=obj.object_id,
                    data={"type": obj.type.value, "layer_id": layer_id}
                ))
                
                # Notify object listeners
                self._notify_object_listeners(obj)
                
        elif action["action"] == "update_object":
            # Restore the new object state
            new_obj = action["new_object"]
            layer_id = action["layer_id"]
            
            if layer_id in self.layers and new_obj.object_id in self.layers[layer_id].objects:
                self.layers[layer_id].objects[new_obj.object_id] = new_obj
                
                # Dispatch event
                self._dispatch_event(SpatialEvent(
                    event_type="object_updated",
                    source="SpatialCanvasComponent",
                    target=new_obj.object_id,
                    data={"type": new_obj.type.value, "layer_id": layer_id}
                ))
                
                # Notify object listeners
                self._notify_object_listeners(new_obj)
                
        elif action["action"] == "delete_object":
            # Delete the object again
            self.delete_object(action["object_id"], action["layer_id"])
            
        # Dispatch redo event
        self._dispatch_event(SpatialEvent(
            event_type="redo",
            source="SpatialCanvasComponent",
            data={"action": action["action"]}
        ))
        
        self.logger.debug(f"Redid action: {action['action']}")
        return True
    
    def add_event_listener(self, event_type: str, listener: Callable[[SpatialEvent], None]) -> None:
        """
        Add a listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            listener: Callback function that will be called when the event occurs
        """
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        self.event_listeners[event_type].append(listener)
        
    def add_object_listener(self, object_id: str, listener: Callable[[SpatialObject], None]) -> bool:
        """
        Add a listener for a specific object.
        
        Args:
            object_id: ID of the object to listen for
            listener: Callback function that will be called when the object is updated
            
        Returns:
            True if the listener was added, False if object not found
        """
        if self.get_object(object_id) is None:
            return False
            
        if object_id not in self.object_listeners:
            self.object_listeners[object_id] = []
            
        self.object_listeners[object_id].append(listener)
        return True
    
    def add_layer_listener(self, layer_id: str, listener: Callable[[SpatialLayer], None]) -> bool:
        """
        Add a listener for a specific layer.
        
        Args:
            layer_id: ID of the layer to listen for
            listener: Callback function that will be called when the layer is updated
            
        Returns:
            True if the listener was added, False if layer not found
        """
        if layer_id not in self.layers:
            return False
            
        if layer_id not in self.layer_listeners:
            self.layer_listeners[layer_id] = []
            
        self.layer_listeners[layer_id].append(listener)
        return True
    
    def add_global_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.global_listeners.append(listener)
        
    def remove_event_listener(self, event_type: str, listener: Callable[[SpatialEvent], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if event_type not in self.event_listeners:
            return False
            
        if listener in self.event_listeners[event_type]:
            self.event_listeners[event_type].remove(listener)
            return True
            
        return False
    
    def remove_object_listener(self, object_id: str, listener: Callable[[SpatialObject], None]) -> bool:
        """
        Remove an object listener.
        
        Args:
            object_id: ID of the object the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if object_id not in self.object_listeners:
            return False
            
        if listener in self.object_listeners[object_id]:
            self.object_listeners[object_id].remove(listener)
            return True
            
        return False
    
    def remove_layer_listener(self, layer_id: str, listener: Callable[[SpatialLayer], None]) -> bool:
        """
        Remove a layer listener.
        
        Args:
            layer_id: ID of the layer the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if layer_id not in self.layer_listeners:
            return False
            
        if listener in self.layer_listeners[layer_id]:
            self.layer_listeners[layer_id].remove(listener)
            return True
            
        return False
    
    def remove_global_listener(self, listener: Callable[[Dict[str, Any]], None]) -> bool:
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
    
    def render_scene(self) -> Dict[str, Any]:
        """
        Render the current scene.
        
        Returns:
            Rendered scene data
        """
        # Collect all visible layers and their objects
        layers_data = []
        
        for layer_id, layer in sorted(self.layers.items(), key=lambda x: x[1].render_order):
            if not layer.visible:
                continue
                
            layer_objects = []
            
            for object_id, obj in sorted(layer.objects.items(), key=lambda x: x[1].style.render_order):
                if not obj.style.visible:
                    continue
                    
                # Get the appropriate renderer
                renderer = self.renderers.get(obj.type)
                if not renderer:
                    continue
                    
                # Render the object
                try:
                    rendered_data = renderer(obj)
                    layer_objects.append(rendered_data)
                except Exception as e:
                    self.logger.error(f"Error rendering object {object_id}: {e}")
                    
            layers_data.append({
                "id": layer_id,
                "name": layer.name,
                "opacity": layer.opacity,
                "objects": layer_objects,
                "metadata": layer.metadata
            })
            
        # Build the scene data
        scene_data = {
            "mode": self.mode.value,
            "interaction_mode": self.interaction_mode.value,
            "camera": self._camera_to_dict(),
            "environment": self._environment_to_dict(),
            "layers": layers_data,
            "selection": {
                "selected_objects": self.selection.selected_objects,
                "selection_box": self.selection.selection_box
            }
        }
        
        return scene_data
    
    def _add_to_history(self, action: Dict[str, Any]) -> None:
        """
        Add an action to the history.
        
        Args:
            action: The action to add
        """
        # If we're not at the end of the history, truncate it
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
            
        # Add the action
        self.history.append(action)
        self.history_index = len(self.history) - 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
            self.history_index = len(self.history) - 1
    
    def _dispatch_event(self, event: SpatialEvent) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event: The event to dispatch
        """
        # Dispatch to event type listeners
        if event.event_type in self.event_listeners:
            for listener in self.event_listeners[event.event_type]:
                try:
                    listener(event)
                except Exception as e:
                    self.logger.error(f"Error in event listener for {event.event_type}: {e}")
                    
        # Dispatch to global listeners
        for listener in self.global_listeners:
            try:
                listener(self._event_to_dict(event))
            except Exception as e:
                self.logger.error(f"Error in global listener: {e}")
    
    def _notify_object_listeners(self, obj: SpatialObject) -> None:
        """
        Notify listeners for a specific object.
        
        Args:
            obj: The object that was updated
        """
        if obj.object_id in self.object_listeners:
            for listener in self.object_listeners[obj.object_id]:
                try:
                    listener(obj)
                except Exception as e:
                    self.logger.error(f"Error in object listener for {obj.object_id}: {e}")
    
    def _notify_layer_listeners(self, layer: SpatialLayer) -> None:
        """
        Notify listeners for a specific layer.
        
        Args:
            layer: The layer that was updated
        """
        if layer.layer_id in self.layer_listeners:
            for listener in self.layer_listeners[layer.layer_id]:
                try:
                    listener(layer)
                except Exception as e:
                    self.logger.error(f"Error in layer listener for {layer.layer_id}: {e}")
    
    def _camera_to_dict(self) -> Dict[str, Any]:
        """
        Convert camera to dictionary.
        
        Returns:
            Dictionary representation of the camera
        """
        return {
            "position": {
                "x": self.camera.position.x,
                "y": self.camera.position.y,
                "z": self.camera.position.z
            },
            "target": {
                "x": self.camera.target.x,
                "y": self.camera.target.y,
                "z": self.camera.target.z
            },
            "up": {
                "x": self.camera.up.x,
                "y": self.camera.up.y,
                "z": self.camera.up.z
            },
            "fov": self.camera.fov,
            "near": self.camera.near,
            "far": self.camera.far,
            "orthographic": self.camera.orthographic,
            "orthographic_size": self.camera.orthographic_size
        }
    
    def _environment_to_dict(self) -> Dict[str, Any]:
        """
        Convert environment to dictionary.
        
        Returns:
            Dictionary representation of the environment
        """
        return {
            "skybox": self.environment.skybox,
            "ambient_light": self.environment.ambient_light,
            "directional_lights": self.environment.directional_lights,
            "point_lights": self.environment.point_lights,
            "spot_lights": self.environment.spot_lights,
            "fog": self.environment.fog,
            "grid": self.environment.grid,
            "axes": self.environment.axes,
            "background_color": self.environment.background_color,
            "custom_environment": self.environment.custom_environment
        }
    
    def _event_to_dict(self, event: SpatialEvent) -> Dict[str, Any]:
        """
        Convert event to dictionary.
        
        Args:
            event: The event to convert
            
        Returns:
            Dictionary representation of the event
        """
        event_dict = {
            "event_type": event.event_type,
            "source": event.source,
            "timestamp": event.timestamp,
            "data": event.data
        }
        
        if event.target:
            event_dict["target"] = event.target
            
        if event.position:
            event_dict["position"] = {
                "x": event.position.x,
                "y": event.position.y,
                "z": event.position.z
            }
            
        return event_dict
    
    # Renderer methods
    
    def _render_point(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a point object."""
        return {
            "id": obj.object_id,
            "type": "point",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "size": obj.style.custom_style.get("size", 5),
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }
    
    def _render_line(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a line object."""
        return {
            "id": obj.object_id,
            "type": "line",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "line_width": obj.style.line_width,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }
    
    def _render_polygon(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a polygon object."""
        return {
            "id": obj.object_id,
            "type": "polygon",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "line_width": obj.style.line_width,
                "fill": obj.style.fill,
                "fill_color": obj.style.fill_color,
                "fill_opacity": obj.style.fill_opacity,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }
    
    def _render_mesh(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a mesh object."""
        return {
            "id": obj.object_id,
            "type": "mesh",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "material": obj.style.material,
                "texture": obj.style.texture,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }
    
    def _render_model(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a model object."""
        return {
            "id": obj.object_id,
            "type": "model",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }
    
    def _render_marker(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a marker object."""
        return {
            "id": obj.object_id,
            "type": "marker",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }
    
    def _render_annotation(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render an annotation object."""
        return {
            "id": obj.object_id,
            "type": "annotation",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }
    
    def _render_heatmap(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a heatmap object."""
        return {
            "id": obj.object_id,
            "type": "heatmap",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "opacity": obj.style.opacity,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }
    
    def _render_flow(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a flow object."""
        return {
            "id": obj.object_id,
            "type": "flow",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }
    
    def _render_container(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a container object."""
        return {
            "id": obj.object_id,
            "type": "container",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive,
            "children": obj.children
        }
    
    def _render_custom(self, obj: SpatialObject) -> Dict[str, Any]:
        """Render a custom object."""
        return {
            "id": obj.object_id,
            "type": "custom",
            "position": {
                "x": obj.transform.position.x,
                "y": obj.transform.position.y,
                "z": obj.transform.position.z
            },
            "rotation": {
                "x": obj.transform.rotation.x,
                "y": obj.transform.rotation.y,
                "z": obj.transform.rotation.z
            },
            "scale": {
                "x": obj.transform.scale.x,
                "y": obj.transform.scale.y,
                "z": obj.transform.scale.z
            },
            "style": {
                "color": obj.style.color,
                "opacity": obj.style.opacity,
                "custom_style": obj.style.custom_style
            },
            "data": obj.data,
            "metadata": obj.metadata,
            "interactive": obj.interactive
        }

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create spatial canvas component
    canvas = SpatialCanvasComponent()
    
    # Start the component
    canvas.start()
    
    # Add an event listener
    def on_event(event):
        print(f"Event: {event.event_type}")
        
    canvas.add_event_listener("object_created", on_event)
    
    # Create a layer
    layer_id = canvas.create_layer("main", "Main Layer")
    
    # Set as active layer
    canvas.set_active_layer(layer_id)
    
    # Create a point object
    point_id = canvas.create_object(
        type=SpatialObjectType.POINT,
        position=SpatialVector(0, 0, 0),
        data={},
        style={"color": "#FF0000", "size": 10}
    )
    
    # Create a line object
    line_id = canvas.create_object(
        type=SpatialObjectType.LINE,
        position=SpatialVector(0, 0, 0),
        data={
            "points": [
                {"x": 0, "y": 0, "z": 0},
                {"x": 10, "y": 10, "z": 0}
            ]
        },
        style={"color": "#0000FF", "line_width": 2}
    )
    
    # Update the point object
    canvas.update_object(
        point_id,
        position=SpatialVector(5, 5, 0),
        style={"color": "#00FF00", "size": 15}
    )
    
    # Select the objects
    canvas.select_objects([point_id, line_id])
    
    # Render the scene
    scene_data = canvas.render_scene()
    
    print(f"Scene mode: {scene_data['mode']}")
    print(f"Number of layers: {len(scene_data['layers'])}")
    print(f"Number of selected objects: {len(scene_data['selection']['selected_objects'])}")
    
    # Stop the component
    canvas.stop()
"""
