"""
Digital Twin Viewer Component for the UI/UX Layer

This component provides a visual interface for interacting with digital twins
in the Industriverse ecosystem. It renders 3D models, real-time data streams,
and interactive controls for digital twin manipulation.

The Digital Twin Viewer:
1. Renders 3D models of physical assets and systems
2. Displays real-time telemetry and sensor data
3. Provides interactive controls for manipulation and simulation
4. Supports different visualization modes (wireframe, solid, x-ray, etc.)
5. Enables annotation and collaboration on digital twins
6. Integrates with the Capsule Framework for context-aware interactions

Author: Manus
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable
import time
import uuid

# Local imports
from ..core.rendering_engine.rendering_engine import RenderingEngine
from ..core.context_engine.context_engine import ContextEngine
from ..core.agent_ecosystem.agent_interaction_protocol import AgentInteractionProtocol
from ..core.capsule_framework.capsule_manager import CapsuleManager

# Configure logging
logger = logging.getLogger(__name__)

class DigitalTwinViewer:
    """
    Digital Twin Viewer component for visualizing and interacting with digital twins.
    """
    
    def __init__(
        self,
        rendering_engine: RenderingEngine,
        context_engine: ContextEngine,
        agent_protocol: AgentInteractionProtocol,
        capsule_manager: CapsuleManager,
        config: Dict = None
    ):
        """
        Initialize the Digital Twin Viewer.
        
        Args:
            rendering_engine: Rendering Engine instance
            context_engine: Context Engine instance
            agent_protocol: Agent Interaction Protocol instance
            capsule_manager: Capsule Manager instance
            config: Optional configuration dictionary
        """
        self.rendering_engine = rendering_engine
        self.context_engine = context_engine
        self.agent_protocol = agent_protocol
        self.capsule_manager = capsule_manager
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "default_view_mode": "solid",
            "enable_annotations": True,
            "enable_collaboration": True,
            "enable_simulations": True,
            "enable_real_time_data": True,
            "data_update_interval": 1.0,  # seconds
            "model_cache_size": 20,
            "default_rotation_speed": 0.5,
            "default_zoom_speed": 0.1,
            "default_pan_speed": 0.1,
            "auto_optimize_models": True,
            "max_polygon_count": 1000000,
            "texture_quality": "high",
            "shadow_quality": "medium",
            "lighting_quality": "high",
            "animation_quality": "high",
            "enable_physics": True,
            "physics_update_rate": 60,  # Hz
            "enable_vr_mode": True,
            "enable_ar_mode": True
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Current state
        self.current_twin_id = None
        self.current_view_mode = self.config["default_view_mode"]
        self.current_annotations = []
        self.current_simulation = None
        self.is_running_simulation = False
        self.real_time_data_subscriptions = {}
        self.loaded_models = {}
        self.selected_component = None
        self.camera_position = {"x": 0, "y": 0, "z": 10}
        self.camera_target = {"x": 0, "y": 0, "z": 0}
        self.camera_up = {"x": 0, "y": 1, "z": 0}
        self.view_history = []
        
        # Event handlers
        self.event_handlers = {
            "model_loaded": [],
            "view_changed": [],
            "component_selected": [],
            "annotation_added": [],
            "annotation_removed": [],
            "simulation_started": [],
            "simulation_stopped": [],
            "data_updated": [],
            "error": []
        }
        
        # Register with context engine
        self.context_engine.register_context_listener(self._handle_context_change)
        
        # Register with agent protocol for digital twin updates
        self.agent_protocol.register_message_handler(
            "state_update",
            self._handle_twin_update,
            "*"
        )
        
        logger.info("Digital Twin Viewer initialized")
    
    def _merge_config(self) -> None:
        """Merge provided configuration with defaults."""
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                # Merge nested dictionaries
                for nested_key, nested_value in value.items():
                    if nested_key not in self.config[key]:
                        self.config[key][nested_key] = nested_value
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        context_type = event.get("type")
        
        # Handle digital twin context changes
        if context_type == "digital_twin":
            twin_data = event.get("data", {})
            
            if "twin_id" in twin_data and twin_data["twin_id"] != self.current_twin_id:
                # Load the new digital twin
                self.load_digital_twin(twin_data["twin_id"])
    
    def _handle_twin_update(self, message: Dict) -> None:
        """
        Handle digital twin state updates.
        
        Args:
            message: State update message
        """
        try:
            payload = message.get("payload", {})
            source_id = message.get("source", {}).get("id")
            
            # Check if this update is for the current twin
            if source_id == self.current_twin_id:
                # Update the twin state
                self._update_twin_state(payload)
        except Exception as e:
            logger.error(f"Error handling twin update: {str(e)}")
    
    def _update_twin_state(self, state: Dict) -> None:
        """
        Update the digital twin state.
        
        Args:
            state: New state data
        """
        try:
            # Update component states
            if "components" in state:
                for component_id, component_state in state["components"].items():
                    self._update_component_state(component_id, component_state)
            
            # Update sensor data
            if "sensors" in state:
                for sensor_id, sensor_data in state["sensors"].items():
                    self._update_sensor_data(sensor_id, sensor_data)
            
            # Update simulation state
            if "simulation" in state:
                self._update_simulation_state(state["simulation"])
            
            # Trigger data updated event
            self._trigger_event("data_updated", {
                "twin_id": self.current_twin_id,
                "timestamp": time.time(),
                "state": state
            })
        except Exception as e:
            logger.error(f"Error updating twin state: {str(e)}")
    
    def _update_component_state(self, component_id: str, state: Dict) -> None:
        """
        Update a component's state.
        
        Args:
            component_id: Component identifier
            state: Component state data
        """
        try:
            # Get the component model
            if self.current_twin_id and component_id in self.loaded_models.get(self.current_twin_id, {}):
                component_model = self.loaded_models[self.current_twin_id][component_id]
                
                # Update position if provided
                if "position" in state:
                    component_model["position"] = state["position"]
                
                # Update rotation if provided
                if "rotation" in state:
                    component_model["rotation"] = state["rotation"]
                
                # Update scale if provided
                if "scale" in state:
                    component_model["scale"] = state["scale"]
                
                # Update visibility if provided
                if "visible" in state:
                    component_model["visible"] = state["visible"]
                
                # Update color if provided
                if "color" in state:
                    component_model["color"] = state["color"]
                
                # Update custom properties
                if "properties" in state:
                    component_model["properties"] = {
                        **component_model.get("properties", {}),
                        **state["properties"]
                    }
                
                # Update the rendering
                self.rendering_engine.update_model(
                    component_id,
                    component_model
                )
        except Exception as e:
            logger.error(f"Error updating component state for {component_id}: {str(e)}")
    
    def _update_sensor_data(self, sensor_id: str, data: Dict) -> None:
        """
        Update sensor data visualization.
        
        Args:
            sensor_id: Sensor identifier
            data: Sensor data
        """
        try:
            # Check if we have a subscription for this sensor
            if sensor_id in self.real_time_data_subscriptions:
                # Get the visualization type
                viz_type = self.real_time_data_subscriptions[sensor_id].get("type", "value")
                
                # Update the visualization based on type
                if viz_type == "value":
                    self._update_value_visualization(sensor_id, data)
                elif viz_type == "gauge":
                    self._update_gauge_visualization(sensor_id, data)
                elif viz_type == "chart":
                    self._update_chart_visualization(sensor_id, data)
                elif viz_type == "heatmap":
                    self._update_heatmap_visualization(sensor_id, data)
                elif viz_type == "color":
                    self._update_color_visualization(sensor_id, data)
                else:
                    logger.warning(f"Unknown visualization type: {viz_type}")
        except Exception as e:
            logger.error(f"Error updating sensor data for {sensor_id}: {str(e)}")
    
    def _update_value_visualization(self, sensor_id: str, data: Dict) -> None:
        """
        Update a value visualization.
        
        Args:
            sensor_id: Sensor identifier
            data: Sensor data
        """
        # Get the subscription
        subscription = self.real_time_data_subscriptions[sensor_id]
        
        # Get the value
        value = data.get("value")
        if value is None:
            return
        
        # Format the value
        if "format" in subscription:
            formatted_value = subscription["format"].format(value)
        else:
            formatted_value = str(value)
        
        # Update the label
        label_id = f"sensor_{sensor_id}_label"
        self.rendering_engine.update_label(
            label_id,
            {
                "text": formatted_value,
                "position": subscription.get("position"),
                "color": subscription.get("color", "#FFFFFF"),
                "size": subscription.get("size", 1.0)
            }
        )
    
    def _update_gauge_visualization(self, sensor_id: str, data: Dict) -> None:
        """
        Update a gauge visualization.
        
        Args:
            sensor_id: Sensor identifier
            data: Sensor data
        """
        # Get the subscription
        subscription = self.real_time_data_subscriptions[sensor_id]
        
        # Get the value
        value = data.get("value")
        if value is None:
            return
        
        # Calculate the gauge value (0-1)
        min_value = subscription.get("min_value", 0)
        max_value = subscription.get("max_value", 100)
        normalized_value = (value - min_value) / (max_value - min_value)
        normalized_value = max(0, min(1, normalized_value))
        
        # Update the gauge
        gauge_id = f"sensor_{sensor_id}_gauge"
        self.rendering_engine.update_gauge(
            gauge_id,
            {
                "value": normalized_value,
                "position": subscription.get("position"),
                "radius": subscription.get("radius", 1.0),
                "color": subscription.get("color", "#00FF00"),
                "background_color": subscription.get("background_color", "#333333")
            }
        )
    
    def _update_chart_visualization(self, sensor_id: str, data: Dict) -> None:
        """
        Update a chart visualization.
        
        Args:
            sensor_id: Sensor identifier
            data: Sensor data
        """
        # Get the subscription
        subscription = self.real_time_data_subscriptions[sensor_id]
        
        # Get the value
        value = data.get("value")
        if value is None:
            return
        
        # Get the timestamp
        timestamp = data.get("timestamp", time.time())
        
        # Add the data point to the series
        if "series" not in subscription:
            subscription["series"] = []
        
        subscription["series"].append({
            "timestamp": timestamp,
            "value": value
        })
        
        # Limit the series length
        max_points = subscription.get("max_points", 100)
        if len(subscription["series"]) > max_points:
            subscription["series"] = subscription["series"][-max_points:]
        
        # Update the chart
        chart_id = f"sensor_{sensor_id}_chart"
        self.rendering_engine.update_chart(
            chart_id,
            {
                "series": subscription["series"],
                "position": subscription.get("position"),
                "size": subscription.get("size", {"width": 2.0, "height": 1.0}),
                "color": subscription.get("color", "#00FF00"),
                "background_color": subscription.get("background_color", "#333333"),
                "axis_color": subscription.get("axis_color", "#FFFFFF"),
                "show_grid": subscription.get("show_grid", True),
                "grid_color": subscription.get("grid_color", "#555555")
            }
        )
    
    def _update_heatmap_visualization(self, sensor_id: str, data: Dict) -> None:
        """
        Update a heatmap visualization.
        
        Args:
            sensor_id: Sensor identifier
            data: Sensor data
        """
        # Get the subscription
        subscription = self.real_time_data_subscriptions[sensor_id]
        
        # Get the values
        values = data.get("values")
        if not values:
            return
        
        # Update the heatmap
        heatmap_id = f"sensor_{sensor_id}_heatmap"
        self.rendering_engine.update_heatmap(
            heatmap_id,
            {
                "values": values,
                "position": subscription.get("position"),
                "size": subscription.get("size", {"width": 2.0, "height": 2.0}),
                "min_value": subscription.get("min_value", 0),
                "max_value": subscription.get("max_value", 100),
                "color_scale": subscription.get("color_scale", [
                    {"value": 0, "color": "#0000FF"},
                    {"value": 0.5, "color": "#00FF00"},
                    {"value": 1, "color": "#FF0000"}
                ])
            }
        )
    
    def _update_color_visualization(self, sensor_id: str, data: Dict) -> None:
        """
        Update a color visualization (changes component color based on value).
        
        Args:
            sensor_id: Sensor identifier
            data: Sensor data
        """
        # Get the subscription
        subscription = self.real_time_data_subscriptions[sensor_id]
        
        # Get the value
        value = data.get("value")
        if value is None:
            return
        
        # Get the component ID
        component_id = subscription.get("component_id")
        if not component_id:
            return
        
        # Calculate the color
        min_value = subscription.get("min_value", 0)
        max_value = subscription.get("max_value", 100)
        normalized_value = (value - min_value) / (max_value - min_value)
        normalized_value = max(0, min(1, normalized_value))
        
        color_scale = subscription.get("color_scale", [
            {"value": 0, "color": "#0000FF"},
            {"value": 0.5, "color": "#00FF00"},
            {"value": 1, "color": "#FF0000"}
        ])
        
        # Find the color in the scale
        color = self._interpolate_color(normalized_value, color_scale)
        
        # Update the component color
        if self.current_twin_id and component_id in self.loaded_models.get(self.current_twin_id, {}):
            component_model = self.loaded_models[self.current_twin_id][component_id]
            component_model["color"] = color
            
            # Update the rendering
            self.rendering_engine.update_model(
                component_id,
                component_model
            )
    
    def _interpolate_color(self, value: float, color_scale: List[Dict]) -> str:
        """
        Interpolate a color from a color scale.
        
        Args:
            value: Normalized value (0-1)
            color_scale: Color scale definition
            
        Returns:
            Interpolated color as hex string
        """
        # Sort the color scale by value
        sorted_scale = sorted(color_scale, key=lambda x: x["value"])
        
        # Find the two colors to interpolate between
        for i in range(len(sorted_scale) - 1):
            if sorted_scale[i]["value"] <= value <= sorted_scale[i + 1]["value"]:
                color1 = sorted_scale[i]["color"]
                color2 = sorted_scale[i + 1]["color"]
                value1 = sorted_scale[i]["value"]
                value2 = sorted_scale[i + 1]["value"]
                
                # Calculate the interpolation factor
                factor = (value - value1) / (value2 - value1) if value2 != value1 else 0
                
                # Interpolate the color
                return self._interpolate_hex_colors(color1, color2, factor)
        
        # If we get here, use the last color
        return sorted_scale[-1]["color"]
    
    def _interpolate_hex_colors(self, color1: str, color2: str, factor: float) -> str:
        """
        Interpolate between two hex colors.
        
        Args:
            color1: First color as hex string
            color2: Second color as hex string
            factor: Interpolation factor (0-1)
            
        Returns:
            Interpolated color as hex string
        """
        # Convert hex to RGB
        r1 = int(color1[1:3], 16)
        g1 = int(color1[3:5], 16)
        b1 = int(color1[5:7], 16)
        
        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)
        
        # Interpolate
        r = int(r1 + factor * (r2 - r1))
        g = int(g1 + factor * (g2 - g1))
        b = int(b1 + factor * (b2 - b1))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _update_simulation_state(self, simulation_state: Dict) -> None:
        """
        Update the simulation state.
        
        Args:
            simulation_state: Simulation state data
        """
        # Update current simulation
        self.current_simulation = simulation_state
        
        # Update running state
        self.is_running_simulation = simulation_state.get("running", False)
        
        # Update time
        simulation_time = simulation_state.get("time", 0)
        
        # Update speed
        simulation_speed = simulation_state.get("speed", 1.0)
        
        # Update the simulation controls
        self.rendering_engine.update_simulation_controls({
            "time": simulation_time,
            "speed": simulation_speed,
            "running": self.is_running_simulation
        })
    
    def _trigger_event(self, event_type: str, data: Dict) -> None:
        """
        Trigger an event.
        
        Args:
            event_type: Event type
            data: Event data
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in {event_type} event handler: {str(e)}")
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler.
        
        Args:
            event_type: Event type
            handler: Event handler function
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            logger.debug(f"Registered {event_type} event handler")
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def unregister_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Unregister an event handler.
        
        Args:
            event_type: Event type
            handler: Event handler function
        """
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.debug(f"Unregistered {event_type} event handler")
    
    def load_digital_twin(self, twin_id: str) -> bool:
        """
        Load a digital twin.
        
        Args:
            twin_id: Digital twin identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            logger.info(f"Loading digital twin: {twin_id}")
            
            # Store the previous twin ID for history
            if self.current_twin_id:
                self.view_history.append(self.current_twin_id)
                # Limit history size
                if len(self.view_history) > 10:
                    self.view_history.pop(0)
            
            # Update current twin ID
            self.current_twin_id = twin_id
            
            # Clear current annotations
            self.current_annotations = []
            
            # Stop any running simulation
            if self.is_running_simulation:
                self.stop_simulation()
            
            # Clear real-time data subscriptions
            self.real_time_data_subscriptions = {}
            
            # Request twin data from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "get_digital_twin",
                    "twin_id": twin_id
                },
                {
                    "type": "agent",
                    "id": "digital_twin_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error loading digital twin: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to load digital twin: {response.get('error_message', 'Unknown error')}",
                    "twin_id": twin_id
                })
                return False
            
            # Extract twin data
            twin_data = response.get("payload", {})
            
            # Load the models
            self._load_twin_models(twin_id, twin_data)
            
            # Set up real-time data subscriptions
            self._setup_data_subscriptions(twin_id, twin_data)
            
            # Set up annotations
            if "annotations" in twin_data:
                for annotation in twin_data["annotations"]:
                    self.add_annotation(annotation)
            
            # Set up simulation if available
            if "simulation" in twin_data:
                self.current_simulation = twin_data["simulation"]
                self.rendering_engine.update_simulation_controls({
                    "time": self.current_simulation.get("time", 0),
                    "speed": self.current_simulation.get("speed", 1.0),
                    "running": False
                })
            
            # Reset camera
            if "default_camera" in twin_data:
                self.set_camera_position(
                    twin_data["default_camera"].get("position", self.camera_position),
                    twin_data["default_camera"].get("target", self.camera_target),
                    twin_data["default_camera"].get("up", self.camera_up)
                )
            else:
                # Reset to default
                self.set_camera_position(
                    {"x": 0, "y": 0, "z": 10},
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 0, "y": 1, "z": 0}
                )
            
            # Set view mode
            self.set_view_mode(twin_data.get("default_view_mode", self.config["default_view_mode"]))
            
            # Trigger model loaded event
            self._trigger_event("model_loaded", {
                "twin_id": twin_id,
                "twin_data": twin_data
            })
            
            logger.info(f"Digital twin loaded: {twin_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading digital twin: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to load digital twin: {str(e)}",
                "twin_id": twin_id
            })
            return False
    
    def _load_twin_models(self, twin_id: str, twin_data: Dict) -> None:
        """
        Load the 3D models for a digital twin.
        
        Args:
            twin_id: Digital twin identifier
            twin_data: Digital twin data
        """
        # Clear the rendering
        self.rendering_engine.clear_scene()
        
        # Initialize models dictionary for this twin
        if twin_id not in self.loaded_models:
            self.loaded_models[twin_id] = {}
        
        # Load components
        if "components" in twin_data:
            for component_id, component_data in twin_data["components"].items():
                # Load the model
                model_url = component_data.get("model_url")
                if not model_url:
                    logger.warning(f"No model URL for component: {component_id}")
                    continue
                
                # Create model data
                model_data = {
                    "url": model_url,
                    "position": component_data.get("position", {"x": 0, "y": 0, "z": 0}),
                    "rotation": component_data.get("rotation", {"x": 0, "y": 0, "z": 0}),
                    "scale": component_data.get("scale", {"x": 1, "y": 1, "z": 1}),
                    "color": component_data.get("color"),
                    "visible": component_data.get("visible", True),
                    "properties": component_data.get("properties", {})
                }
                
                # Store the model data
                self.loaded_models[twin_id][component_id] = model_data
                
                # Load the model in the rendering engine
                self.rendering_engine.load_model(
                    component_id,
                    model_data
                )
        
        # Limit cache size
        if len(self.loaded_models) > self.config["model_cache_size"]:
            # Remove oldest entries
            keys_to_remove = sorted(self.loaded_models.keys())[:-self.config["model_cache_size"]]
            for key in keys_to_remove:
                del self.loaded_models[key]
    
    def _setup_data_subscriptions(self, twin_id: str, twin_data: Dict) -> None:
        """
        Set up real-time data subscriptions.
        
        Args:
            twin_id: Digital twin identifier
            twin_data: Digital twin data
        """
        if "sensors" in twin_data:
            for sensor_id, sensor_data in twin_data["sensors"].items():
                # Get visualization type
                viz_type = sensor_data.get("visualization", {}).get("type", "value")
                
                # Create subscription
                subscription = {
                    "type": viz_type,
                    "position": sensor_data.get("position", {"x": 0, "y": 0, "z": 0}),
                    **sensor_data.get("visualization", {})
                }
                
                # Store subscription
                self.real_time_data_subscriptions[sensor_id] = subscription
                
                # Create initial visualization
                if viz_type == "value":
                    self._create_value_visualization(sensor_id, subscription)
                elif viz_type == "gauge":
                    self._create_gauge_visualization(sensor_id, subscription)
                elif viz_type == "chart":
                    self._create_chart_visualization(sensor_id, subscription)
                elif viz_type == "heatmap":
                    self._create_heatmap_visualization(sensor_id, subscription)
                elif viz_type == "color":
                    # No initial visualization needed for color type
                    pass
                else:
                    logger.warning(f"Unknown visualization type: {viz_type}")
    
    def _create_value_visualization(self, sensor_id: str, subscription: Dict) -> None:
        """
        Create a value visualization.
        
        Args:
            sensor_id: Sensor identifier
            subscription: Subscription data
        """
        label_id = f"sensor_{sensor_id}_label"
        self.rendering_engine.create_label(
            label_id,
            {
                "text": subscription.get("initial_value", "N/A"),
                "position": subscription.get("position"),
                "color": subscription.get("color", "#FFFFFF"),
                "size": subscription.get("size", 1.0)
            }
        )
    
    def _create_gauge_visualization(self, sensor_id: str, subscription: Dict) -> None:
        """
        Create a gauge visualization.
        
        Args:
            sensor_id: Sensor identifier
            subscription: Subscription data
        """
        gauge_id = f"sensor_{sensor_id}_gauge"
        self.rendering_engine.create_gauge(
            gauge_id,
            {
                "value": subscription.get("initial_value", 0) / (subscription.get("max_value", 100) - subscription.get("min_value", 0)),
                "position": subscription.get("position"),
                "radius": subscription.get("radius", 1.0),
                "color": subscription.get("color", "#00FF00"),
                "background_color": subscription.get("background_color", "#333333")
            }
        )
    
    def _create_chart_visualization(self, sensor_id: str, subscription: Dict) -> None:
        """
        Create a chart visualization.
        
        Args:
            sensor_id: Sensor identifier
            subscription: Subscription data
        """
        # Initialize series
        subscription["series"] = []
        
        # Add initial data point if provided
        if "initial_value" in subscription:
            subscription["series"].append({
                "timestamp": time.time(),
                "value": subscription["initial_value"]
            })
        
        chart_id = f"sensor_{sensor_id}_chart"
        self.rendering_engine.create_chart(
            chart_id,
            {
                "series": subscription["series"],
                "position": subscription.get("position"),
                "size": subscription.get("size", {"width": 2.0, "height": 1.0}),
                "color": subscription.get("color", "#00FF00"),
                "background_color": subscription.get("background_color", "#333333"),
                "axis_color": subscription.get("axis_color", "#FFFFFF"),
                "show_grid": subscription.get("show_grid", True),
                "grid_color": subscription.get("grid_color", "#555555")
            }
        )
    
    def _create_heatmap_visualization(self, sensor_id: str, subscription: Dict) -> None:
        """
        Create a heatmap visualization.
        
        Args:
            sensor_id: Sensor identifier
            subscription: Subscription data
        """
        heatmap_id = f"sensor_{sensor_id}_heatmap"
        self.rendering_engine.create_heatmap(
            heatmap_id,
            {
                "values": subscription.get("initial_values", []),
                "position": subscription.get("position"),
                "size": subscription.get("size", {"width": 2.0, "height": 2.0}),
                "min_value": subscription.get("min_value", 0),
                "max_value": subscription.get("max_value", 100),
                "color_scale": subscription.get("color_scale", [
                    {"value": 0, "color": "#0000FF"},
                    {"value": 0.5, "color": "#00FF00"},
                    {"value": 1, "color": "#FF0000"}
                ])
            }
        )
    
    def set_view_mode(self, mode: str) -> None:
        """
        Set the view mode.
        
        Args:
            mode: View mode (solid, wireframe, x-ray, etc.)
        """
        try:
            logger.info(f"Setting view mode: {mode}")
            
            # Update current mode
            self.current_view_mode = mode
            
            # Update rendering
            self.rendering_engine.set_view_mode(mode)
            
            # Trigger view changed event
            self._trigger_event("view_changed", {
                "mode": mode,
                "twin_id": self.current_twin_id
            })
        except Exception as e:
            logger.error(f"Error setting view mode: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to set view mode: {str(e)}",
                "mode": mode
            })
    
    def set_camera_position(
        self,
        position: Dict,
        target: Optional[Dict] = None,
        up: Optional[Dict] = None
    ) -> None:
        """
        Set the camera position.
        
        Args:
            position: Camera position
            target: Optional camera target
            up: Optional camera up vector
        """
        try:
            # Update camera position
            self.camera_position = position
            
            # Update target if provided
            if target:
                self.camera_target = target
            
            # Update up vector if provided
            if up:
                self.camera_up = up
            
            # Update rendering
            self.rendering_engine.set_camera({
                "position": self.camera_position,
                "target": self.camera_target,
                "up": self.camera_up
            })
            
            # Trigger view changed event
            self._trigger_event("view_changed", {
                "camera": {
                    "position": self.camera_position,
                    "target": self.camera_target,
                    "up": self.camera_up
                },
                "twin_id": self.current_twin_id
            })
        except Exception as e:
            logger.error(f"Error setting camera position: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to set camera position: {str(e)}"
            })
    
    def rotate_camera(self, delta_x: float, delta_y: float) -> None:
        """
        Rotate the camera around the target.
        
        Args:
            delta_x: Horizontal rotation delta
            delta_y: Vertical rotation delta
        """
        try:
            # Calculate new camera position
            # This is a simplified orbit camera calculation
            
            # Get current position relative to target
            rel_x = self.camera_position["x"] - self.camera_target["x"]
            rel_y = self.camera_position["y"] - self.camera_target["y"]
            rel_z = self.camera_position["z"] - self.camera_target["z"]
            
            # Calculate distance
            distance = (rel_x ** 2 + rel_y ** 2 + rel_z ** 2) ** 0.5
            
            # Calculate spherical coordinates
            theta = math.atan2(rel_z, rel_x)
            phi = math.acos(rel_y / distance)
            
            # Update angles
            theta += delta_x * self.config["default_rotation_speed"]
            phi += delta_y * self.config["default_rotation_speed"]
            
            # Clamp phi to avoid gimbal lock
            phi = max(0.1, min(math.pi - 0.1, phi))
            
            # Convert back to Cartesian
            new_rel_x = distance * math.sin(phi) * math.cos(theta)
            new_rel_y = distance * math.cos(phi)
            new_rel_z = distance * math.sin(phi) * math.sin(theta)
            
            # Calculate new position
            new_position = {
                "x": self.camera_target["x"] + new_rel_x,
                "y": self.camera_target["y"] + new_rel_y,
                "z": self.camera_target["z"] + new_rel_z
            }
            
            # Update camera
            self.set_camera_position(new_position)
        except Exception as e:
            logger.error(f"Error rotating camera: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to rotate camera: {str(e)}"
            })
    
    def zoom_camera(self, delta: float) -> None:
        """
        Zoom the camera.
        
        Args:
            delta: Zoom delta
        """
        try:
            # Calculate direction vector
            dir_x = self.camera_target["x"] - self.camera_position["x"]
            dir_y = self.camera_target["y"] - self.camera_position["y"]
            dir_z = self.camera_target["z"] - self.camera_position["z"]
            
            # Calculate distance
            distance = (dir_x ** 2 + dir_y ** 2 + dir_z ** 2) ** 0.5
            
            # Normalize direction
            if distance > 0:
                dir_x /= distance
                dir_y /= distance
                dir_z /= distance
            
            # Calculate zoom factor
            zoom_factor = delta * self.config["default_zoom_speed"] * distance
            
            # Calculate new position
            new_position = {
                "x": self.camera_position["x"] + dir_x * zoom_factor,
                "y": self.camera_position["y"] + dir_y * zoom_factor,
                "z": self.camera_position["z"] + dir_z * zoom_factor
            }
            
            # Update camera
            self.set_camera_position(new_position)
        except Exception as e:
            logger.error(f"Error zooming camera: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to zoom camera: {str(e)}"
            })
    
    def pan_camera(self, delta_x: float, delta_y: float) -> None:
        """
        Pan the camera.
        
        Args:
            delta_x: Horizontal pan delta
            delta_y: Vertical pan delta
        """
        try:
            # Calculate camera right vector (cross product of up and direction)
            dir_x = self.camera_target["x"] - self.camera_position["x"]
            dir_y = self.camera_target["y"] - self.camera_position["y"]
            dir_z = self.camera_target["z"] - self.camera_position["z"]
            
            # Calculate right vector (cross product of up and direction)
            right_x = dir_z * self.camera_up["y"] - dir_y * self.camera_up["z"]
            right_y = dir_x * self.camera_up["z"] - dir_z * self.camera_up["x"]
            right_z = dir_y * self.camera_up["x"] - dir_x * self.camera_up["y"]
            
            # Normalize right vector
            right_length = (right_x ** 2 + right_y ** 2 + right_z ** 2) ** 0.5
            if right_length > 0:
                right_x /= right_length
                right_y /= right_length
                right_z /= right_length
            
            # Calculate pan factors
            pan_x_factor = delta_x * self.config["default_pan_speed"]
            pan_y_factor = delta_y * self.config["default_pan_speed"]
            
            # Calculate pan offsets
            offset_x = right_x * pan_x_factor + self.camera_up["x"] * pan_y_factor
            offset_y = right_y * pan_x_factor + self.camera_up["y"] * pan_y_factor
            offset_z = right_z * pan_x_factor + self.camera_up["z"] * pan_y_factor
            
            # Calculate new position and target
            new_position = {
                "x": self.camera_position["x"] - offset_x,
                "y": self.camera_position["y"] - offset_y,
                "z": self.camera_position["z"] - offset_z
            }
            
            new_target = {
                "x": self.camera_target["x"] - offset_x,
                "y": self.camera_target["y"] - offset_y,
                "z": self.camera_target["z"] - offset_z
            }
            
            # Update camera
            self.set_camera_position(new_position, new_target)
        except Exception as e:
            logger.error(f"Error panning camera: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to pan camera: {str(e)}"
            })
    
    def select_component(self, component_id: str) -> None:
        """
        Select a component.
        
        Args:
            component_id: Component identifier
        """
        try:
            logger.info(f"Selecting component: {component_id}")
            
            # Update selected component
            self.selected_component = component_id
            
            # Highlight the component in the rendering
            self.rendering_engine.highlight_model(component_id)
            
            # Get component data
            component_data = None
            if self.current_twin_id and component_id in self.loaded_models.get(self.current_twin_id, {}):
                component_data = self.loaded_models[self.current_twin_id][component_id]
            
            # Trigger component selected event
            self._trigger_event("component_selected", {
                "component_id": component_id,
                "component_data": component_data
            })
            
            # Create a capsule for the component if not already exists
            self._create_component_capsule(component_id, component_data)
        except Exception as e:
            logger.error(f"Error selecting component: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to select component: {str(e)}",
                "component_id": component_id
            })
    
    def _create_component_capsule(self, component_id: str, component_data: Dict) -> None:
        """
        Create a capsule for a component.
        
        Args:
            component_id: Component identifier
            component_data: Component data
        """
        # Check if capsule already exists
        capsule_id = f"component_{component_id}"
        if self.capsule_manager.has_capsule(capsule_id):
            # Just focus the existing capsule
            self.capsule_manager.focus_capsule(capsule_id)
            return
        
        # Create capsule data
        capsule_data = {
            "id": capsule_id,
            "type": "component",
            "title": component_data.get("properties", {}).get("name", f"Component {component_id}"),
            "description": component_data.get("properties", {}).get("description", ""),
            "icon": component_data.get("properties", {}).get("icon", "cube"),
            "color": component_data.get("color", "#0056B3"),
            "source": {
                "type": "digital_twin",
                "id": self.current_twin_id,
                "component_id": component_id
            },
            "actions": [
                {
                    "id": "focus",
                    "label": "Focus",
                    "icon": "search"
                },
                {
                    "id": "hide",
                    "label": "Hide",
                    "icon": "eye-slash"
                },
                {
                    "id": "show_properties",
                    "label": "Properties",
                    "icon": "list"
                }
            ],
            "properties": component_data.get("properties", {})
        }
        
        # Create the capsule
        self.capsule_manager.create_capsule(capsule_data)
    
    def deselect_component(self) -> None:
        """Deselect the currently selected component."""
        try:
            if self.selected_component:
                logger.info(f"Deselecting component: {self.selected_component}")
                
                # Remove highlight
                self.rendering_engine.unhighlight_model(self.selected_component)
                
                # Clear selected component
                self.selected_component = None
                
                # Trigger component selected event with null
                self._trigger_event("component_selected", {
                    "component_id": None,
                    "component_data": None
                })
        except Exception as e:
            logger.error(f"Error deselecting component: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to deselect component: {str(e)}"
            })
    
    def add_annotation(self, annotation: Dict) -> str:
        """
        Add an annotation.
        
        Args:
            annotation: Annotation data
            
        Returns:
            Annotation ID
        """
        try:
            if not self.config["enable_annotations"]:
                logger.warning("Annotations are disabled")
                return ""
            
            # Generate ID if not provided
            annotation_id = annotation.get("id", str(uuid.uuid4()))
            
            # Ensure ID is set
            annotation["id"] = annotation_id
            
            # Add timestamp if not provided
            if "timestamp" not in annotation:
                annotation["timestamp"] = time.time()
            
            # Add to annotations
            self.current_annotations.append(annotation)
            
            # Create annotation in rendering engine
            self.rendering_engine.create_annotation(
                annotation_id,
                {
                    "text": annotation.get("text", ""),
                    "position": annotation.get("position", {"x": 0, "y": 0, "z": 0}),
                    "color": annotation.get("color", "#FFFFFF"),
                    "size": annotation.get("size", 1.0),
                    "author": annotation.get("author", "Unknown")
                }
            )
            
            # Trigger annotation added event
            self._trigger_event("annotation_added", {
                "annotation": annotation
            })
            
            logger.info(f"Added annotation: {annotation_id}")
            return annotation_id
        except Exception as e:
            logger.error(f"Error adding annotation: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to add annotation: {str(e)}"
            })
            return ""
    
    def remove_annotation(self, annotation_id: str) -> bool:
        """
        Remove an annotation.
        
        Args:
            annotation_id: Annotation identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            # Find the annotation
            annotation = None
            for ann in self.current_annotations:
                if ann["id"] == annotation_id:
                    annotation = ann
                    break
            
            if not annotation:
                logger.warning(f"Annotation not found: {annotation_id}")
                return False
            
            # Remove from list
            self.current_annotations.remove(annotation)
            
            # Remove from rendering engine
            self.rendering_engine.remove_annotation(annotation_id)
            
            # Trigger annotation removed event
            self._trigger_event("annotation_removed", {
                "annotation_id": annotation_id,
                "annotation": annotation
            })
            
            logger.info(f"Removed annotation: {annotation_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing annotation: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to remove annotation: {str(e)}",
                "annotation_id": annotation_id
            })
            return False
    
    def start_simulation(self) -> bool:
        """
        Start the simulation.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.config["enable_simulations"]:
                logger.warning("Simulations are disabled")
                return False
            
            if not self.current_simulation:
                logger.warning("No simulation available")
                return False
            
            if self.is_running_simulation:
                logger.info("Simulation is already running")
                return True
            
            logger.info("Starting simulation")
            
            # Update running state
            self.is_running_simulation = True
            
            # Update simulation controls
            self.rendering_engine.update_simulation_controls({
                "running": True
            })
            
            # Send command to backend
            self.agent_protocol.send_command(
                {
                    "command_type": "start_simulation",
                    "twin_id": self.current_twin_id
                },
                {
                    "type": "agent",
                    "id": "digital_twin_agent",
                    "protocol": "a2a"
                }
            )
            
            # Trigger simulation started event
            self._trigger_event("simulation_started", {
                "twin_id": self.current_twin_id,
                "simulation": self.current_simulation
            })
            
            return True
        except Exception as e:
            logger.error(f"Error starting simulation: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to start simulation: {str(e)}"
            })
            return False
    
    def stop_simulation(self) -> bool:
        """
        Stop the simulation.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.is_running_simulation:
                logger.info("Simulation is not running")
                return True
            
            logger.info("Stopping simulation")
            
            # Update running state
            self.is_running_simulation = False
            
            # Update simulation controls
            self.rendering_engine.update_simulation_controls({
                "running": False
            })
            
            # Send command to backend
            self.agent_protocol.send_command(
                {
                    "command_type": "stop_simulation",
                    "twin_id": self.current_twin_id
                },
                {
                    "type": "agent",
                    "id": "digital_twin_agent",
                    "protocol": "a2a"
                }
            )
            
            # Trigger simulation stopped event
            self._trigger_event("simulation_stopped", {
                "twin_id": self.current_twin_id,
                "simulation": self.current_simulation
            })
            
            return True
        except Exception as e:
            logger.error(f"Error stopping simulation: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to stop simulation: {str(e)}"
            })
            return False
    
    def set_simulation_speed(self, speed: float) -> bool:
        """
        Set the simulation speed.
        
        Args:
            speed: Simulation speed factor
            
        Returns:
            Boolean indicating success
        """
        try:
            if not self.current_simulation:
                logger.warning("No simulation available")
                return False
            
            logger.info(f"Setting simulation speed: {speed}")
            
            # Update simulation speed
            if self.current_simulation:
                self.current_simulation["speed"] = speed
            
            # Update simulation controls
            self.rendering_engine.update_simulation_controls({
                "speed": speed
            })
            
            # Send command to backend
            self.agent_protocol.send_command(
                {
                    "command_type": "set_simulation_speed",
                    "twin_id": self.current_twin_id,
                    "speed": speed
                },
                {
                    "type": "agent",
                    "id": "digital_twin_agent",
                    "protocol": "a2a"
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error setting simulation speed: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to set simulation speed: {str(e)}",
                "speed": speed
            })
            return False
    
    def set_simulation_time(self, time_value: float) -> bool:
        """
        Set the simulation time.
        
        Args:
            time_value: Simulation time value
            
        Returns:
            Boolean indicating success
        """
        try:
            if not self.current_simulation:
                logger.warning("No simulation available")
                return False
            
            logger.info(f"Setting simulation time: {time_value}")
            
            # Update simulation time
            if self.current_simulation:
                self.current_simulation["time"] = time_value
            
            # Update simulation controls
            self.rendering_engine.update_simulation_controls({
                "time": time_value
            })
            
            # Send command to backend
            self.agent_protocol.send_command(
                {
                    "command_type": "set_simulation_time",
                    "twin_id": self.current_twin_id,
                    "time": time_value
                },
                {
                    "type": "agent",
                    "id": "digital_twin_agent",
                    "protocol": "a2a"
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error setting simulation time: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to set simulation time: {str(e)}",
                "time": time_value
            })
            return False
    
    def get_component_properties(self, component_id: str) -> Optional[Dict]:
        """
        Get properties for a component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            Component properties or None if not found
        """
        if self.current_twin_id and component_id in self.loaded_models.get(self.current_twin_id, {}):
            component_model = self.loaded_models[self.current_twin_id][component_id]
            return component_model.get("properties", {})
        return None
    
    def get_annotations(self) -> List[Dict]:
        """
        Get all annotations.
        
        Returns:
            List of annotations
        """
        return self.current_annotations.copy()
    
    def get_simulation_state(self) -> Optional[Dict]:
        """
        Get the current simulation state.
        
        Returns:
            Simulation state or None if no simulation
        """
        return self.current_simulation
    
    def get_view_history(self) -> List[str]:
        """
        Get the view history.
        
        Returns:
            List of previously viewed twin IDs
        """
        return self.view_history.copy()
    
    def clear_view_history(self) -> None:
        """Clear the view history."""
        self.view_history = []
        logger.debug("View history cleared")
    
    def enable_vr_mode(self) -> bool:
        """
        Enable VR mode.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.config["enable_vr_mode"]:
                logger.warning("VR mode is disabled")
                return False
            
            logger.info("Enabling VR mode")
            
            # Enable VR mode in rendering engine
            self.rendering_engine.enable_vr_mode()
            
            return True
        except Exception as e:
            logger.error(f"Error enabling VR mode: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to enable VR mode: {str(e)}"
            })
            return False
    
    def disable_vr_mode(self) -> bool:
        """
        Disable VR mode.
        
        Returns:
            Boolean indicating success
        """
        try:
            logger.info("Disabling VR mode")
            
            # Disable VR mode in rendering engine
            self.rendering_engine.disable_vr_mode()
            
            return True
        except Exception as e:
            logger.error(f"Error disabling VR mode: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to disable VR mode: {str(e)}"
            })
            return False
    
    def enable_ar_mode(self) -> bool:
        """
        Enable AR mode.
        
        Returns:
            Boolean indicating success
        """
        try:
            if not self.config["enable_ar_mode"]:
                logger.warning("AR mode is disabled")
                return False
            
            logger.info("Enabling AR mode")
            
            # Enable AR mode in rendering engine
            self.rendering_engine.enable_ar_mode()
            
            return True
        except Exception as e:
            logger.error(f"Error enabling AR mode: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to enable AR mode: {str(e)}"
            })
            return False
    
    def disable_ar_mode(self) -> bool:
        """
        Disable AR mode.
        
        Returns:
            Boolean indicating success
        """
        try:
            logger.info("Disabling AR mode")
            
            # Disable AR mode in rendering engine
            self.rendering_engine.disable_ar_mode()
            
            return True
        except Exception as e:
            logger.error(f"Error disabling AR mode: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to disable AR mode: {str(e)}"
            })
            return False
    
    def export_twin_data(self, format_type: str = "json") -> Optional[str]:
        """
        Export digital twin data.
        
        Args:
            format_type: Export format (json, glb, etc.)
            
        Returns:
            Exported data string or None if failed
        """
        try:
            if not self.current_twin_id:
                logger.warning("No digital twin loaded")
                return None
            
            logger.info(f"Exporting digital twin data in {format_type} format")
            
            # Request twin data from backend
            response = self.agent_protocol.send_request_sync(
                {
                    "request_type": "export_digital_twin",
                    "twin_id": self.current_twin_id,
                    "format": format_type
                },
                {
                    "type": "agent",
                    "id": "digital_twin_agent",
                    "protocol": "a2a"
                }
            )
            
            if "error" in response and response["error"]:
                logger.error(f"Error exporting digital twin: {response.get('error_message', 'Unknown error')}")
                self._trigger_event("error", {
                    "message": f"Failed to export digital twin: {response.get('error_message', 'Unknown error')}",
                    "twin_id": self.current_twin_id
                })
                return None
            
            # Extract export data
            export_data = response.get("payload", {}).get("data")
            
            return export_data
        except Exception as e:
            logger.error(f"Error exporting digital twin data: {str(e)}")
            self._trigger_event("error", {
                "message": f"Failed to export digital twin data: {str(e)}"
            })
            return None
    
    def shutdown(self) -> None:
        """Shutdown the Digital Twin Viewer."""
        logger.info("Shutting down Digital Twin Viewer")
        
        # Stop any running simulation
        if self.is_running_simulation:
            self.stop_simulation()
        
        # Clear real-time data subscriptions
        self.real_time_data_subscriptions = {}
        
        # Clear annotations
        self.current_annotations = []
        
        # Clear the rendering
        self.rendering_engine.clear_scene()
