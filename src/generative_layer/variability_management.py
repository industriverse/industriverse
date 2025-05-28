"""
Variability Management for Industriverse Generative Layer

This module implements the variability management system for customization and adaptation
with protocol-native architecture and MCP/A2A integration.
"""

import json
import logging
import os
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VariabilityManagement:
    """
    Implements the variability management system for the Generative Layer.
    Manages customization and adaptation with protocol-native architecture.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the variability management system.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.variation_points = {}
        self.variation_configurations = {}
        self.active_configurations = {}
        self.variation_history = {}
        
        # Initialize storage paths
        self.storage_path = os.path.join(os.getcwd(), "variability_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        
        logger.info("Variability Management System initialized")
    
    def register_variation_point(self, 
                               point_id: str, 
                               name: str,
                               description: str,
                               target_type: str,
                               options: List[Dict[str, Any]],
                               default_option: str,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new variation point.
        
        Args:
            point_id: Unique identifier for the variation point
            name: Name of the variation point
            description: Description of the variation point
            target_type: Type of target (template, component, code, etc.)
            options: List of available options for this variation point
            default_option: Default option ID
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        if point_id in self.variation_points:
            logger.warning(f"Variation point {point_id} already registered")
            return False
        
        # Validate options
        option_ids = [option["id"] for option in options]
        if default_option not in option_ids:
            logger.warning(f"Default option {default_option} not found in options")
            return False
        
        timestamp = time.time()
        
        # Create variation point record
        variation_point = {
            "id": point_id,
            "name": name,
            "description": description,
            "target_type": target_type,
            "options": options,
            "default_option": default_option,
            "metadata": metadata or {},
            "timestamp": timestamp
        }
        
        # Store variation point
        self.variation_points[point_id] = variation_point
        
        # Store variation point file
        point_path = os.path.join(self.storage_path, f"{point_id}_point.json")
        with open(point_path, 'w') as f:
            json.dump(variation_point, f, indent=2)
        
        logger.info(f"Registered variation point {point_id}: {name}")
        
        # Emit MCP event for variation point registration
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/variability/point_registered",
                {
                    "point_id": point_id,
                    "name": name,
                    "target_type": target_type
                }
            )
        
        return True
    
    def create_configuration(self, 
                           config_id: str, 
                           name: str,
                           description: str,
                           selections: Dict[str, str],
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new variation configuration.
        
        Args:
            config_id: Unique identifier for the configuration
            name: Name of the configuration
            description: Description of the configuration
            selections: Dictionary mapping variation point IDs to selected option IDs
            metadata: Additional metadata (optional)
            
        Returns:
            True if creation was successful, False otherwise
        """
        if config_id in self.variation_configurations:
            logger.warning(f"Configuration {config_id} already exists")
            return False
        
        # Validate selections
        invalid_points = []
        invalid_options = []
        
        for point_id, option_id in selections.items():
            if point_id not in self.variation_points:
                invalid_points.append(point_id)
                continue
                
            point = self.variation_points[point_id]
            option_ids = [option["id"] for option in point["options"]]
            
            if option_id not in option_ids:
                invalid_options.append((point_id, option_id))
        
        if invalid_points:
            logger.warning(f"Invalid variation points: {invalid_points}")
            return False
            
        if invalid_options:
            logger.warning(f"Invalid options: {invalid_options}")
            return False
        
        timestamp = time.time()
        
        # Create configuration record
        configuration = {
            "id": config_id,
            "name": name,
            "description": description,
            "selections": selections,
            "metadata": metadata or {},
            "timestamp": timestamp
        }
        
        # Store configuration
        self.variation_configurations[config_id] = configuration
        
        # Store configuration file
        config_path = os.path.join(self.storage_path, f"{config_id}_config.json")
        with open(config_path, 'w') as f:
            json.dump(configuration, f, indent=2)
        
        logger.info(f"Created variation configuration {config_id}: {name}")
        
        # Emit MCP event for configuration creation
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/variability/config_created",
                {
                    "config_id": config_id,
                    "name": name
                }
            )
        
        return True
    
    def activate_configuration(self, 
                             config_id: str,
                             target_id: str,
                             activation_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Activate a variation configuration for a specific target.
        
        Args:
            config_id: ID of the configuration to activate
            target_id: ID of the target to apply the configuration to
            activation_id: Optional ID for the activation (generated if not provided)
            
        Returns:
            Activation result if successful, None otherwise
        """
        if config_id not in self.variation_configurations:
            logger.warning(f"Configuration {config_id} not found")
            return None
        
        configuration = self.variation_configurations[config_id]
        
        # Generate activation ID if not provided
        if activation_id is None:
            activation_id = f"activation_{uuid.uuid4().hex[:8]}"
        
        timestamp = time.time()
        
        # Create activation record
        activation = {
            "id": activation_id,
            "config_id": config_id,
            "target_id": target_id,
            "timestamp": timestamp,
            "status": "active",
            "selections": configuration["selections"].copy()
        }
        
        # Store activation
        if target_id not in self.active_configurations:
            self.active_configurations[target_id] = {}
        
        self.active_configurations[target_id][config_id] = activation
        self.variation_history[activation_id] = activation
        
        # Store activation file
        activation_path = os.path.join(self.storage_path, f"{activation_id}_activation.json")
        with open(activation_path, 'w') as f:
            json.dump(activation, f, indent=2)
        
        logger.info(f"Activated configuration {config_id} for target {target_id} as {activation_id}")
        
        # Emit MCP event for configuration activation
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/variability/config_activated",
                {
                    "activation_id": activation_id,
                    "config_id": config_id,
                    "target_id": target_id
                }
            )
        
        return activation
    
    def deactivate_configuration(self, 
                               config_id: str,
                               target_id: str) -> bool:
        """
        Deactivate a variation configuration for a specific target.
        
        Args:
            config_id: ID of the configuration to deactivate
            target_id: ID of the target
            
        Returns:
            True if deactivation was successful, False otherwise
        """
        if target_id not in self.active_configurations:
            logger.warning(f"No active configurations for target {target_id}")
            return False
            
        if config_id not in self.active_configurations[target_id]:
            logger.warning(f"Configuration {config_id} not active for target {target_id}")
            return False
        
        # Get activation
        activation = self.active_configurations[target_id][config_id]
        activation_id = activation["id"]
        
        # Update activation status
        activation["status"] = "inactive"
        activation["deactivation_timestamp"] = time.time()
        
        # Remove from active configurations
        del self.active_configurations[target_id][config_id]
        if not self.active_configurations[target_id]:
            del self.active_configurations[target_id]
        
        # Update history
        self.variation_history[activation_id] = activation
        
        # Update activation file
        activation_path = os.path.join(self.storage_path, f"{activation_id}_activation.json")
        with open(activation_path, 'w') as f:
            json.dump(activation, f, indent=2)
        
        logger.info(f"Deactivated configuration {config_id} for target {target_id}")
        
        # Emit MCP event for configuration deactivation
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/variability/config_deactivated",
                {
                    "activation_id": activation_id,
                    "config_id": config_id,
                    "target_id": target_id
                }
            )
        
        return True
    
    def get_active_configurations(self, target_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all active configurations for a specific target.
        
        Args:
            target_id: ID of the target
            
        Returns:
            Dictionary of active configurations
        """
        if target_id not in self.active_configurations:
            return {}
        
        return self.active_configurations[target_id]
    
    def get_variation_point(self, point_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a variation point by ID.
        
        Args:
            point_id: ID of the variation point to retrieve
            
        Returns:
            Variation point data if found, None otherwise
        """
        if point_id not in self.variation_points:
            logger.warning(f"Variation point {point_id} not found")
            return None
        
        return self.variation_points[point_id]
    
    def get_configuration(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a configuration by ID.
        
        Args:
            config_id: ID of the configuration to retrieve
            
        Returns:
            Configuration data if found, None otherwise
        """
        if config_id not in self.variation_configurations:
            logger.warning(f"Configuration {config_id} not found")
            return None
        
        return self.variation_configurations[config_id]
    
    def get_activation(self, activation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an activation by ID.
        
        Args:
            activation_id: ID of the activation to retrieve
            
        Returns:
            Activation data if found, None otherwise
        """
        if activation_id not in self.variation_history:
            logger.warning(f"Activation {activation_id} not found")
            return None
        
        return self.variation_history[activation_id]
    
    def resolve_variations(self, 
                         target_id: str, 
                         content: Any) -> Any:
        """
        Resolve variations for a specific target and content.
        
        Args:
            target_id: ID of the target
            content: Content to resolve variations for
            
        Returns:
            Content with resolved variations
        """
        if target_id not in self.active_configurations:
            # No active configurations, return content as is
            return content
        
        # Get all active configurations for this target
        active_configs = self.active_configurations[target_id]
        
        # Apply each configuration
        resolved_content = content
        for config_id, activation in active_configs.items():
            resolved_content = self._apply_configuration(resolved_content, activation["selections"])
        
        return resolved_content
    
    def _apply_configuration(self, content: Any, selections: Dict[str, str]) -> Any:
        """
        Apply a configuration to content.
        
        Args:
            content: Content to apply configuration to
            selections: Dictionary mapping variation point IDs to selected option IDs
            
        Returns:
            Content with applied configuration
        """
        # If content is a string, apply string-based variations
        if isinstance(content, str):
            return self._apply_string_variations(content, selections)
        
        # If content is a dict, recursively apply to each value
        elif isinstance(content, dict):
            return {k: self._apply_configuration(v, selections) for k, v in content.items()}
        
        # If content is a list, recursively apply to each item
        elif isinstance(content, list):
            return [self._apply_configuration(item, selections) for item in content]
        
        # Otherwise, return content as is
        else:
            return content
    
    def _apply_string_variations(self, content: str, selections: Dict[str, str]) -> str:
        """
        Apply string-based variations.
        
        Args:
            content: String content to apply variations to
            selections: Dictionary mapping variation point IDs to selected option IDs
            
        Returns:
            String with applied variations
        """
        result = content
        
        # Look for variation point markers in the string
        # Format: {{variation:point_id}}
        import re
        pattern = r'\{\{variation:([\w-]+)\}\}'
        
        matches = re.findall(pattern, result)
        
        for point_id in matches:
            if point_id in selections and point_id in self.variation_points:
                point = self.variation_points[point_id]
                option_id = selections[point_id]
                
                # Find the selected option
                selected_option = None
                for option in point["options"]:
                    if option["id"] == option_id:
                        selected_option = option
                        break
                
                if selected_option and "value" in selected_option:
                    # Replace the marker with the selected option value
                    marker = f"{{{{variation:{point_id}}}}}"
                    result = result.replace(marker, str(selected_option["value"]))
        
        return result
    
    def create_industry_variation_points(self, industry: str) -> List[str]:
        """
        Create variation points for a specific industry.
        
        Args:
            industry: Industry to create variation points for
            
        Returns:
            List of created variation point IDs
        """
        created_points = []
        
        # Generate a unique prefix for this industry
        prefix = f"{industry.lower().replace(' ', '_')}"
        
        # Create color scheme variation point
        color_point_id = f"{prefix}_color_scheme"
        color_success = self.register_variation_point(
            point_id=color_point_id,
            name=f"{industry} Color Scheme",
            description=f"Color scheme variations for {industry}",
            target_type="style",
            options=[
                {
                    "id": "default",
                    "name": "Default",
                    "description": "Default color scheme",
                    "value": {
                        "primary": "#1890ff",
                        "secondary": "#52c41a",
                        "accent": "#722ed1",
                        "background": "#ffffff",
                        "text": "#000000"
                    }
                },
                {
                    "id": "dark",
                    "name": "Dark",
                    "description": "Dark color scheme",
                    "value": {
                        "primary": "#177ddc",
                        "secondary": "#49aa19",
                        "accent": "#642ab5",
                        "background": "#141414",
                        "text": "#ffffff"
                    }
                },
                {
                    "id": "industry_specific",
                    "name": f"{industry} Specific",
                    "description": f"Color scheme specific to {industry}",
                    "value": self._get_industry_colors(industry)
                }
            ],
            default_option="default",
            metadata={
                "industry": industry,
                "type": "color_scheme"
            }
        )
        
        if color_success:
            created_points.append(color_point_id)
        
        # Create terminology variation point
        terminology_point_id = f"{prefix}_terminology"
        terminology_success = self.register_variation_point(
            point_id=terminology_point_id,
            name=f"{industry} Terminology",
            description=f"Terminology variations for {industry}",
            target_type="text",
            options=[
                {
                    "id": "standard",
                    "name": "Standard",
                    "description": "Standard terminology",
                    "value": {
                        "user": "User",
                        "admin": "Administrator",
                        "dashboard": "Dashboard",
                        "report": "Report",
                        "alert": "Alert"
                    }
                },
                {
                    "id": "industry_specific",
                    "name": f"{industry} Specific",
                    "description": f"Terminology specific to {industry}",
                    "value": self._get_industry_terminology(industry)
                }
            ],
            default_option="standard",
            metadata={
                "industry": industry,
                "type": "terminology"
            }
        )
        
        if terminology_success:
            created_points.append(terminology_point_id)
        
        # Create layout variation point
        layout_point_id = f"{prefix}_layout"
        layout_success = self.register_variation_point(
            point_id=layout_point_id,
            name=f"{industry} Layout",
            description=f"Layout variations for {industry}",
            target_type="layout",
            options=[
                {
                    "id": "standard",
                    "name": "Standard",
                    "description": "Standard layout",
                    "value": "standard"
                },
                {
                    "id": "compact",
                    "name": "Compact",
                    "description": "Compact layout",
                    "value": "compact"
                },
                {
                    "id": "expanded",
                    "name": "Expanded",
                    "description": "Expanded layout",
                    "value": "expanded"
                },
                {
                    "id": "industry_specific",
                    "name": f"{industry} Specific",
                    "description": f"Layout specific to {industry}",
                    "value": self._get_industry_layout(industry)
                }
            ],
            default_option="standard",
            metadata={
                "industry": industry,
                "type": "layout"
            }
        )
        
        if layout_success:
            created_points.append(layout_point_id)
        
        return created_points
    
    def create_industry_configuration(self, industry: str) -> Optional[str]:
        """
        Create a configuration for a specific industry.
        
        Args:
            industry: Industry to create configuration for
            
        Returns:
            Configuration ID if successful, None otherwise
        """
        # Generate a unique ID for this configuration
        config_id = f"{industry.lower().replace(' ', '_')}_config"
        
        # Create variation points if they don't exist
        variation_points = self.create_industry_variation_points(industry)
        
        if not variation_points:
            logger.warning(f"Failed to create variation points for {industry}")
            return None
        
        # Create selections
        selections = {}
        for point_id in variation_points:
            point = self.variation_points[point_id]
            
            # Select industry-specific option if available
            industry_option = None
            for option in point["options"]:
                if option["id"] == "industry_specific":
                    industry_option = option["id"]
                    break
            
            selections[point_id] = industry_option or point["default_option"]
        
        # Create configuration
        success = self.create_configuration(
            config_id=config_id,
            name=f"{industry} Configuration",
            description=f"Configuration for {industry}",
            selections=selections,
            metadata={
                "industry": industry,
                "type": "industry_configuration"
            }
        )
        
        if success:
            return config_id
        else:
            return None
    
    def _get_industry_colors(self, industry: str) -> Dict[str, str]:
        """
        Get color scheme for a specific industry.
        
        Args:
            industry: Industry to get color scheme for
            
        Returns:
            Color scheme
        """
        # Define industry-specific color schemes
        industry_colors = {
            "Manufacturing": {
                "primary": "#0052cc",
                "secondary": "#ff5630",
                "accent": "#ffab00",
                "background": "#f4f5f7",
                "text": "#172b4d"
            },
            "Healthcare": {
                "primary": "#00a3bf",
                "secondary": "#57d9a3",
                "accent": "#ff8f73",
                "background": "#ffffff",
                "text": "#253858"
            },
            "Energy": {
                "primary": "#ff8b00",
                "secondary": "#36b37e",
                "accent": "#6554c0",
                "background": "#f4f5f7",
                "text": "#172b4d"
            },
            "Aerospace": {
                "primary": "#0747a6",
                "secondary": "#de350b",
                "accent": "#00b8d9",
                "background": "#f4f5f7",
                "text": "#172b4d"
            },
            "Defense": {
                "primary": "#006644",
                "secondary": "#bf2600",
                "accent": "#403294",
                "background": "#f4f5f7",
                "text": "#172b4d"
            },
            "Logistics": {
                "primary": "#00875a",
                "secondary": "#ff991f",
                "accent": "#998dd9",
                "background": "#f4f5f7",
                "text": "#172b4d"
            },
            "Construction": {
                "primary": "#ff8b00",
                "secondary": "#0052cc",
                "accent": "#6554c0",
                "background": "#f4f5f7",
                "text": "#172b4d"
            }
        }
        
        # Return industry-specific colors or default
        return industry_colors.get(industry, {
            "primary": "#1890ff",
            "secondary": "#52c41a",
            "accent": "#722ed1",
            "background": "#ffffff",
            "text": "#000000"
        })
    
    def _get_industry_terminology(self, industry: str) -> Dict[str, str]:
        """
        Get terminology for a specific industry.
        
        Args:
            industry: Industry to get terminology for
            
        Returns:
            Terminology
        """
        # Define industry-specific terminology
        industry_terminology = {
            "Manufacturing": {
                "user": "Operator",
                "admin": "Supervisor",
                "dashboard": "Production Monitor",
                "report": "Production Report",
                "alert": "Production Alert"
            },
            "Healthcare": {
                "user": "Clinician",
                "admin": "Medical Director",
                "dashboard": "Patient Monitor",
                "report": "Medical Report",
                "alert": "Clinical Alert"
            },
            "Energy": {
                "user": "Engineer",
                "admin": "Plant Manager",
                "dashboard": "Energy Monitor",
                "report": "Efficiency Report",
                "alert": "System Alert"
            },
            "Aerospace": {
                "user": "Engineer",
                "admin": "Program Manager",
                "dashboard": "Flight Monitor",
                "report": "Flight Report",
                "alert": "Safety Alert"
            },
            "Defense": {
                "user": "Operator",
                "admin": "Commander",
                "dashboard": "Command Center",
                "report": "Mission Report",
                "alert": "Security Alert"
            },
            "Logistics": {
                "user": "Dispatcher",
                "admin": "Fleet Manager",
                "dashboard": "Logistics Monitor",
                "report": "Shipment Report",
                "alert": "Delivery Alert"
            },
            "Construction": {
                "user": "Contractor",
                "admin": "Project Manager",
                "dashboard": "Project Monitor",
                "report": "Progress Report",
                "alert": "Safety Alert"
            }
        }
        
        # Return industry-specific terminology or default
        return industry_terminology.get(industry, {
            "user": "User",
            "admin": "Administrator",
            "dashboard": "Dashboard",
            "report": "Report",
            "alert": "Alert"
        })
    
    def _get_industry_layout(self, industry: str) -> str:
        """
        Get layout for a specific industry.
        
        Args:
            industry: Industry to get layout for
            
        Returns:
            Layout
        """
        # Define industry-specific layouts
        industry_layouts = {
            "Manufacturing": "production_floor",
            "Healthcare": "patient_centric",
            "Energy": "grid_view",
            "Aerospace": "mission_control",
            "Defense": "command_center",
            "Logistics": "route_map",
            "Construction": "project_timeline"
        }
        
        # Return industry-specific layout or default
        return industry_layouts.get(industry, "standard")
    
    def export_variability_data(self) -> Dict[str, Any]:
        """
        Export variability data for persistence.
        
        Returns:
            Variability data
        """
        return {
            "variation_points": self.variation_points,
            "variation_configurations": self.variation_configurations,
            "active_configurations": self.active_configurations
        }
    
    def import_variability_data(self, variability_data: Dict[str, Any]) -> None:
        """
        Import variability data from persistence.
        
        Args:
            variability_data: Variability data to import
        """
        if "variation_points" in variability_data:
            self.variation_points = variability_data["variation_points"]
        
        if "variation_configurations" in variability_data:
            self.variation_configurations = variability_data["variation_configurations"]
        
        if "active_configurations" in variability_data:
            self.active_configurations = variability_data["active_configurations"]
        
        logger.info("Imported variability data")
