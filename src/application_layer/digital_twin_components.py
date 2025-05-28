"""
Digital Twin Components for the Industriverse Application Layer.

This module provides digital twin functionality for industrial assets,
enabling real-time monitoring, simulation, and control with protocol-native interfaces.
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DigitalTwinComponents:
    """
    Digital Twin Components for the Industriverse platform.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the Digital Twin Components.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        self.twin_models = {}
        self.twin_instances = {}
        self.twin_states = {}
        self.twin_visualizations = {}
        
        # Register with agent core
        self.agent_core.register_component("digital_twin_components", self)
        
        logger.info("Digital Twin Components initialized")
    
    def register_twin_model(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new digital twin model.
        
        Args:
            model_config: Model configuration
            
        Returns:
            Registration result
        """
        # Validate model configuration
        required_fields = ["model_id", "name", "description", "asset_type", "attributes"]
        for field in required_fields:
            if field not in model_config:
                return {"error": f"Missing required field: {field}"}
        
        # Generate model ID if not provided
        model_id = model_config.get("model_id", f"model-{str(uuid.uuid4())}")
        
        # Add metadata
        model_config["registered_at"] = time.time()
        
        # Store model
        self.twin_models[model_id] = model_config
        
        # Log registration
        logger.info(f"Registered twin model: {model_id}")
        
        return {
            "status": "success",
            "model_id": model_id
        }
    
    def create_twin_instance(self, model_id: str, instance_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new digital twin instance from a model.
        
        Args:
            model_id: Model ID
            instance_config: Instance configuration
            
        Returns:
            Creation result
        """
        # Check if model exists
        if model_id not in self.twin_models:
            return {"error": f"Model not found: {model_id}"}
        
        # Get model
        model = self.twin_models[model_id]
        
        # Generate instance ID
        instance_id = f"twin-{str(uuid.uuid4())}"
        
        # Create instance
        instance = {
            "instance_id": instance_id,
            "model_id": model_id,
            "name": instance_config.get("name", model["name"]),
            "description": instance_config.get("description", model["description"]),
            "asset_type": model["asset_type"],
            "attributes": {},
            "status": "created",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Initialize attributes from model
        for attr in model["attributes"]:
            attr_name = attr["name"]
            attr_default = attr.get("default", None)
            instance["attributes"][attr_name] = instance_config.get("attributes", {}).get(attr_name, attr_default)
        
        # Add instance-specific configuration
        for key, value in instance_config.items():
            if key not in ["instance_id", "model_id", "attributes", "created_at", "updated_at"]:
                instance[key] = value
        
        # Store instance
        self.twin_instances[instance_id] = instance
        
        # Initialize twin state
        self.twin_states[instance_id] = {
            "current_state": "idle",
            "last_updated": time.time(),
            "telemetry": {},
            "alerts": [],
            "history": []
        }
        
        # Log creation
        logger.info(f"Created twin instance: {instance_id} from model: {model_id}")
        
        # Emit MCP event for twin creation
        self.agent_core.emit_mcp_event("application/digital_twin", {
            "action": "create",
            "instance_id": instance_id,
            "model_id": model_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "instance": instance
        }
    
    def get_twin_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a digital twin instance by ID.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Instance data or None if not found
        """
        return self.twin_instances.get(instance_id)
    
    def update_twin_attributes(self, instance_id: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update digital twin attributes.
        
        Args:
            instance_id: Instance ID
            attributes: Attribute updates
            
        Returns:
            Update result
        """
        # Check if instance exists
        if instance_id not in self.twin_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Get instance
        instance = self.twin_instances[instance_id]
        
        # Update attributes
        for attr_name, attr_value in attributes.items():
            if attr_name in instance["attributes"]:
                instance["attributes"][attr_name] = attr_value
        
        # Update timestamp
        instance["updated_at"] = time.time()
        
        # Log update
        logger.info(f"Updated twin attributes: {instance_id}")
        
        # Emit MCP event for twin update
        self.agent_core.emit_mcp_event("application/digital_twin", {
            "action": "update_attributes",
            "instance_id": instance_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "updated_attributes": list(attributes.keys())
        }
    
    def update_twin_state(self, instance_id: str, state: str, telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update digital twin state.
        
        Args:
            instance_id: Instance ID
            state: New state
            telemetry: Telemetry data
            
        Returns:
            Update result
        """
        # Check if instance exists
        if instance_id not in self.twin_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Check if state exists
        if instance_id not in self.twin_states:
            return {"error": f"State not found for instance: {instance_id}"}
        
        # Get twin state
        twin_state = self.twin_states[instance_id]
        
        # Update state
        twin_state["current_state"] = state
        twin_state["last_updated"] = time.time()
        
        # Update telemetry if provided
        if telemetry:
            twin_state["telemetry"].update(telemetry)
            
            # Add to history
            history_entry = {
                "timestamp": time.time(),
                "state": state,
                "telemetry": telemetry.copy()
            }
            twin_state["history"].append(history_entry)
            
            # Trim history if needed
            max_history = 100
            if len(twin_state["history"]) > max_history:
                twin_state["history"] = twin_state["history"][-max_history:]
        
        # Log update
        logger.info(f"Updated twin state: {instance_id} to {state}")
        
        # Emit MCP event for twin state update
        self.agent_core.emit_mcp_event("application/digital_twin", {
            "action": "update_state",
            "instance_id": instance_id,
            "state": state,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "state": state
        }
    
    def add_twin_alert(self, instance_id: str, alert_type: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an alert to a digital twin.
        
        Args:
            instance_id: Instance ID
            alert_type: Alert type
            alert_data: Alert data
            
        Returns:
            Alert result
        """
        # Check if instance exists
        if instance_id not in self.twin_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Check if state exists
        if instance_id not in self.twin_states:
            return {"error": f"State not found for instance: {instance_id}"}
        
        # Get twin state
        twin_state = self.twin_states[instance_id]
        
        # Create alert
        alert = {
            "alert_id": f"alert-{str(uuid.uuid4())}",
            "alert_type": alert_type,
            "alert_data": alert_data,
            "timestamp": time.time(),
            "status": "active"
        }
        
        # Add to alerts
        twin_state["alerts"].append(alert)
        
        # Log alert
        logger.info(f"Added twin alert: {alert['alert_id']} to instance: {instance_id}")
        
        # Emit MCP event for twin alert
        self.agent_core.emit_mcp_event("application/digital_twin", {
            "action": "add_alert",
            "instance_id": instance_id,
            "alert_id": alert["alert_id"],
            "alert_type": alert_type,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "alert_id": alert["alert_id"],
            "alert": alert
        }
    
    def resolve_twin_alert(self, instance_id: str, alert_id: str, resolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a digital twin alert.
        
        Args:
            instance_id: Instance ID
            alert_id: Alert ID
            resolution_data: Resolution data
            
        Returns:
            Resolution result
        """
        # Check if instance exists
        if instance_id not in self.twin_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Check if state exists
        if instance_id not in self.twin_states:
            return {"error": f"State not found for instance: {instance_id}"}
        
        # Get twin state
        twin_state = self.twin_states[instance_id]
        
        # Find alert
        alert = None
        for a in twin_state["alerts"]:
            if a["alert_id"] == alert_id:
                alert = a
                break
        
        if not alert:
            return {"error": f"Alert not found: {alert_id}"}
        
        # Update alert
        alert["status"] = "resolved"
        alert["resolution_data"] = resolution_data
        alert["resolved_at"] = time.time()
        
        # Log resolution
        logger.info(f"Resolved twin alert: {alert_id} for instance: {instance_id}")
        
        # Emit MCP event for twin alert resolution
        self.agent_core.emit_mcp_event("application/digital_twin", {
            "action": "resolve_alert",
            "instance_id": instance_id,
            "alert_id": alert_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "alert_id": alert_id,
            "alert": alert
        }
    
    def create_twin_visualization(self, instance_id: str, visualization_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a visualization for a digital twin.
        
        Args:
            instance_id: Instance ID
            visualization_config: Visualization configuration
            
        Returns:
            Creation result
        """
        # Check if instance exists
        if instance_id not in self.twin_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Validate visualization configuration
        required_fields = ["type", "config"]
        for field in required_fields:
            if field not in visualization_config:
                return {"error": f"Missing required field: {field}"}
        
        # Generate visualization ID
        visualization_id = f"viz-{str(uuid.uuid4())}"
        
        # Create visualization
        visualization = {
            "visualization_id": visualization_id,
            "instance_id": instance_id,
            "type": visualization_config["type"],
            "config": visualization_config["config"],
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Add optional fields
        optional_fields = ["name", "description", "layout", "refresh_interval"]
        for field in optional_fields:
            if field in visualization_config:
                visualization[field] = visualization_config[field]
        
        # Store visualization
        if instance_id not in self.twin_visualizations:
            self.twin_visualizations[instance_id] = {}
        
        self.twin_visualizations[instance_id][visualization_id] = visualization
        
        # Log creation
        logger.info(f"Created twin visualization: {visualization_id} for instance: {instance_id}")
        
        return {
            "status": "success",
            "visualization_id": visualization_id,
            "visualization": visualization
        }
    
    def get_twin_visualization(self, instance_id: str, visualization_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a digital twin visualization.
        
        Args:
            instance_id: Instance ID
            visualization_id: Visualization ID
            
        Returns:
            Visualization data or None if not found
        """
        if instance_id not in self.twin_visualizations:
            return None
        
        return self.twin_visualizations[instance_id].get(visualization_id)
    
    def get_twin_visualizations(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        Get all visualizations for a digital twin.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            List of visualizations
        """
        if instance_id not in self.twin_visualizations:
            return []
        
        return list(self.twin_visualizations[instance_id].values())
    
    def simulate_twin(self, instance_id: str, simulation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate a digital twin.
        
        Args:
            instance_id: Instance ID
            simulation_config: Simulation configuration
            
        Returns:
            Simulation result
        """
        # Check if instance exists
        if instance_id not in self.twin_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Get instance
        instance = self.twin_instances[instance_id]
        
        # Extract simulation parameters
        duration = simulation_config.get("duration", 3600)  # Default: 1 hour
        interval = simulation_config.get("interval", 60)    # Default: 1 minute
        scenarios = simulation_config.get("scenarios", [])
        
        # Log simulation
        logger.info(f"Simulating twin: {instance_id} for {duration} seconds with {interval} second intervals")
        
        # Create simulation result
        simulation_result = {
            "instance_id": instance_id,
            "duration": duration,
            "interval": interval,
            "timestamps": [],
            "states": [],
            "telemetry": []
        }
        
        # Generate simulation data
        current_time = time.time()
        for i in range(0, duration, interval):
            timestamp = current_time + i
            
            # Determine state and telemetry based on scenarios
            state, telemetry = self._calculate_simulation_state(instance, scenarios, i, duration)
            
            # Add to simulation result
            simulation_result["timestamps"].append(timestamp)
            simulation_result["states"].append(state)
            simulation_result["telemetry"].append(telemetry)
        
        # Emit MCP event for twin simulation
        self.agent_core.emit_mcp_event("application/digital_twin", {
            "action": "simulate",
            "instance_id": instance_id,
            "duration": duration,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "simulation": simulation_result
        }
    
    def _calculate_simulation_state(self, instance: Dict[str, Any], scenarios: List[Dict[str, Any]], 
                                   time_offset: int, duration: int) -> tuple:
        """
        Calculate simulation state and telemetry based on scenarios.
        
        Args:
            instance: Twin instance
            scenarios: Simulation scenarios
            time_offset: Current time offset in simulation
            duration: Total simulation duration
            
        Returns:
            Tuple of (state, telemetry)
        """
        # Default state and telemetry
        state = "normal"
        telemetry = {}
        
        # Initialize telemetry with instance attributes
        for attr_name, attr_value in instance["attributes"].items():
            if isinstance(attr_value, (int, float)):
                telemetry[attr_name] = attr_value
        
        # Apply scenarios
        for scenario in scenarios:
            scenario_type = scenario.get("type", "")
            
            if scenario_type == "linear_change":
                # Linear change of a parameter over time
                param = scenario.get("parameter", "")
                start_value = scenario.get("start_value", 0)
                end_value = scenario.get("end_value", 0)
                
                if param in telemetry:
                    # Calculate value based on time offset
                    progress = time_offset / duration
                    value = start_value + (end_value - start_value) * progress
                    telemetry[param] = value
            
            elif scenario_type == "threshold_event":
                # Event when a parameter crosses a threshold
                param = scenario.get("parameter", "")
                threshold = scenario.get("threshold", 0)
                event_state = scenario.get("state", "alert")
                trigger_time = scenario.get("trigger_time", duration / 2)
                
                if param in telemetry and time_offset >= trigger_time:
                    telemetry[param] = threshold + 1
                    state = event_state
            
            elif scenario_type == "oscillation":
                # Oscillating parameter
                param = scenario.get("parameter", "")
                base_value = scenario.get("base_value", 0)
                amplitude = scenario.get("amplitude", 1)
                period = scenario.get("period", duration / 10)
                
                if param in telemetry:
                    # Calculate oscillating value
                    import math
                    value = base_value + amplitude * math.sin((time_offset / period) * 2 * math.pi)
                    telemetry[param] = value
        
        return state, telemetry
    
    def get_twin_models(self) -> List[Dict[str, Any]]:
        """
        Get all digital twin models.
        
        Returns:
            List of models
        """
        return list(self.twin_models.values())
    
    def get_twin_instances(self) -> List[Dict[str, Any]]:
        """
        Get all digital twin instances.
        
        Returns:
            List of instances
        """
        return list(self.twin_instances.values())
    
    def get_twin_state(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the state of a digital twin.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Twin state or None if not found
        """
        return self.twin_states.get(instance_id)
    
    def initialize_default_models(self) -> Dict[str, Any]:
        """
        Initialize default digital twin models.
        
        Returns:
            Initialization result
        """
        logger.info("Initializing default digital twin models")
        
        # Define default models
        default_models = [
            {
                "model_id": "model-machine",
                "name": "Industrial Machine",
                "description": "Digital twin model for industrial machines",
                "asset_type": "machine",
                "attributes": [
                    {
                        "name": "temperature",
                        "type": "float",
                        "unit": "celsius",
                        "min": 0,
                        "max": 100,
                        "default": 25
                    },
                    {
                        "name": "pressure",
                        "type": "float",
                        "unit": "bar",
                        "min": 0,
                        "max": 10,
                        "default": 1
                    },
                    {
                        "name": "vibration",
                        "type": "float",
                        "unit": "mm/s",
                        "min": 0,
                        "max": 50,
                        "default": 5
                    },
                    {
                        "name": "power",
                        "type": "float",
                        "unit": "kW",
                        "min": 0,
                        "max": 500,
                        "default": 100
                    },
                    {
                        "name": "status",
                        "type": "string",
                        "options": ["off", "idle", "running", "error"],
                        "default": "idle"
                    }
                ]
            },
            {
                "model_id": "model-sensor",
                "name": "Industrial Sensor",
                "description": "Digital twin model for industrial sensors",
                "asset_type": "sensor",
                "attributes": [
                    {
                        "name": "value",
                        "type": "float",
                        "unit": "variable",
                        "min": 0,
                        "max": 1000,
                        "default": 0
                    },
                    {
                        "name": "battery",
                        "type": "float",
                        "unit": "percent",
                        "min": 0,
                        "max": 100,
                        "default": 100
                    },
                    {
                        "name": "signal_strength",
                        "type": "float",
                        "unit": "percent",
                        "min": 0,
                        "max": 100,
                        "default": 80
                    },
                    {
                        "name": "status",
                        "type": "string",
                        "options": ["offline", "online", "error"],
                        "default": "online"
                    }
                ]
            },
            {
                "model_id": "model-process",
                "name": "Industrial Process",
                "description": "Digital twin model for industrial processes",
                "asset_type": "process",
                "attributes": [
                    {
                        "name": "throughput",
                        "type": "float",
                        "unit": "units/hour",
                        "min": 0,
                        "max": 10000,
                        "default": 1000
                    },
                    {
                        "name": "efficiency",
                        "type": "float",
                        "unit": "percent",
                        "min": 0,
                        "max": 100,
                        "default": 80
                    },
                    {
                        "name": "quality",
                        "type": "float",
                        "unit": "percent",
                        "min": 0,
                        "max": 100,
                        "default": 95
                    },
                    {
                        "name": "status",
                        "type": "string",
                        "options": ["stopped", "starting", "running", "stopping", "error"],
                        "default": "stopped"
                    }
                ]
            }
        ]
        
        # Register models
        registered_models = []
        for model_config in default_models:
            result = self.register_twin_model(model_config)
            if "error" not in result:
                registered_models.append(result["model_id"])
        
        return {
            "status": "success",
            "registered_models": registered_models,
            "count": len(registered_models)
        }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get component information.
        
        Returns:
            Component information
        """
        return {
            "id": "digital_twin_components",
            "type": "DigitalTwinComponents",
            "name": "Digital Twin Components",
            "status": "operational",
            "models": len(self.twin_models),
            "instances": len(self.twin_instances),
            "visualizations": sum(len(vizs) for vizs in self.twin_visualizations.values())
        }
    
    def handle_action(self, action_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle component action.
        
        Args:
            action_id: Action ID
            data: Action data
            
        Returns:
            Response data
        """
        # Handle different actions
        if action_id == "register_twin_model":
            return self.register_twin_model(data)
        elif action_id == "create_twin_instance":
            return self.create_twin_instance(
                data.get("model_id", ""),
                data.get("instance_config", {})
            )
        elif action_id == "get_twin_instance":
            instance = self.get_twin_instance(data.get("instance_id", ""))
            return {"instance": instance} if instance else {"error": "Instance not found"}
        elif action_id == "update_twin_attributes":
            return self.update_twin_attributes(
                data.get("instance_id", ""),
                data.get("attributes", {})
            )
        elif action_id == "update_twin_state":
            return self.update_twin_state(
                data.get("instance_id", ""),
                data.get("state", ""),
                data.get("telemetry")
            )
        elif action_id == "add_twin_alert":
            return self.add_twin_alert(
                data.get("instance_id", ""),
                data.get("alert_type", ""),
                data.get("alert_data", {})
            )
        elif action_id == "resolve_twin_alert":
            return self.resolve_twin_alert(
                data.get("instance_id", ""),
                data.get("alert_id", ""),
                data.get("resolution_data", {})
            )
        elif action_id == "create_twin_visualization":
            return self.create_twin_visualization(
                data.get("instance_id", ""),
                data.get("visualization_config", {})
            )
        elif action_id == "get_twin_visualization":
            visualization = self.get_twin_visualization(
                data.get("instance_id", ""),
                data.get("visualization_id", "")
            )
            return {"visualization": visualization} if visualization else {"error": "Visualization not found"}
        elif action_id == "get_twin_visualizations":
            return {"visualizations": self.get_twin_visualizations(data.get("instance_id", ""))}
        elif action_id == "simulate_twin":
            return self.simulate_twin(
                data.get("instance_id", ""),
                data.get("simulation_config", {})
            )
        elif action_id == "get_twin_models":
            return {"models": self.get_twin_models()}
        elif action_id == "get_twin_instances":
            return {"instances": self.get_twin_instances()}
        elif action_id == "get_twin_state":
            state = self.get_twin_state(data.get("instance_id", ""))
            return {"state": state} if state else {"error": "State not found"}
        elif action_id == "initialize_default_models":
            return self.initialize_default_models()
        else:
            return {"error": f"Unsupported action: {action_id}"}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get component status.
        
        Returns:
            Component status
        """
        return {
            "status": "operational",
            "models": len(self.twin_models),
            "instances": len(self.twin_instances),
            "states": len(self.twin_states),
            "visualizations": sum(len(vizs) for vizs in self.twin_visualizations.values())
        }
