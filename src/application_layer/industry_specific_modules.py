"""
Industry-Specific Modules for the Industriverse Application Layer.

This module provides industry-specific functionality and templates for various industrial sectors,
enabling rapid deployment of specialized applications with protocol-native interfaces.
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndustrySpecificModules:
    """
    Industry-Specific Modules for the Industriverse platform.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the Industry-Specific Modules.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        self.industry_templates = {}
        self.industry_instances = {}
        self.industry_configs = {}
        
        # Register with agent core
        self.agent_core.register_component("industry_specific_modules", self)
        
        logger.info("Industry-Specific Modules initialized")
    
    def register_industry_template(self, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new industry-specific template.
        
        Args:
            template_config: Template configuration
            
        Returns:
            Registration result
        """
        # Validate template configuration
        required_fields = ["template_id", "name", "description", "industry", "modules"]
        for field in required_fields:
            if field not in template_config:
                return {"error": f"Missing required field: {field}"}
        
        # Generate template ID if not provided
        template_id = template_config.get("template_id", f"industry-{str(uuid.uuid4())}")
        
        # Add metadata
        template_config["registered_at"] = time.time()
        
        # Store template
        self.industry_templates[template_id] = template_config
        
        # Log registration
        logger.info(f"Registered industry template: {template_id}")
        
        return {
            "status": "success",
            "template_id": template_id
        }
    
    def create_industry_instance(self, template_id: str, instance_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new industry-specific instance from a template.
        
        Args:
            template_id: Template ID
            instance_config: Instance configuration
            
        Returns:
            Creation result
        """
        # Check if template exists
        if template_id not in self.industry_templates:
            return {"error": f"Template not found: {template_id}"}
        
        # Get template
        template = self.industry_templates[template_id]
        
        # Generate instance ID
        instance_id = f"industry-{str(uuid.uuid4())}"
        
        # Create instance
        instance = {
            "instance_id": instance_id,
            "template_id": template_id,
            "name": instance_config.get("name", template["name"]),
            "description": instance_config.get("description", template["description"]),
            "industry": template["industry"],
            "modules": template["modules"].copy(),
            "status": "created",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Add instance-specific configuration
        for key, value in instance_config.items():
            if key not in ["instance_id", "template_id", "created_at", "updated_at"]:
                instance[key] = value
        
        # Store instance
        self.industry_instances[instance_id] = instance
        
        # Initialize instance configuration
        self.industry_configs[instance_id] = {
            "instance_id": instance_id,
            "config": instance_config.get("config", {}),
            "last_updated": time.time()
        }
        
        # Log creation
        logger.info(f"Created industry instance: {instance_id} from template: {template_id}")
        
        # Emit MCP event for industry instance creation
        self.agent_core.emit_mcp_event("application/industry", {
            "action": "create_instance",
            "instance_id": instance_id,
            "template_id": template_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "instance": instance
        }
    
    def get_industry_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an industry-specific instance by ID.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Instance data or None if not found
        """
        return self.industry_instances.get(instance_id)
    
    def update_industry_instance(self, instance_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an industry-specific instance.
        
        Args:
            instance_id: Instance ID
            update_data: Update data
            
        Returns:
            Update result
        """
        # Check if instance exists
        if instance_id not in self.industry_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Get instance
        instance = self.industry_instances[instance_id]
        
        # Update instance
        for key, value in update_data.items():
            if key not in ["instance_id", "template_id", "created_at"]:
                instance[key] = value
        
        # Update timestamp
        instance["updated_at"] = time.time()
        
        # Log update
        logger.info(f"Updated industry instance: {instance_id}")
        
        # Emit MCP event for industry instance update
        self.agent_core.emit_mcp_event("application/industry", {
            "action": "update_instance",
            "instance_id": instance_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "instance": instance
        }
    
    def update_industry_config(self, instance_id: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an industry-specific instance configuration.
        
        Args:
            instance_id: Instance ID
            config_data: Configuration data
            
        Returns:
            Update result
        """
        # Check if instance exists
        if instance_id not in self.industry_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Check if config exists
        if instance_id not in self.industry_configs:
            # Initialize config if it doesn't exist
            self.industry_configs[instance_id] = {
                "instance_id": instance_id,
                "config": {},
                "last_updated": time.time()
            }
        
        # Get config
        config = self.industry_configs[instance_id]
        
        # Update config
        for key, value in config_data.items():
            config["config"][key] = value
        
        # Update timestamp
        config["last_updated"] = time.time()
        
        # Log update
        logger.info(f"Updated industry config: {instance_id}")
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "config": config["config"]
        }
    
    def get_industry_config(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an industry-specific instance configuration.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Configuration data or None if not found
        """
        if instance_id not in self.industry_configs:
            return None
        
        return self.industry_configs[instance_id]["config"]
    
    def delete_industry_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Delete an industry-specific instance.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Deletion result
        """
        # Check if instance exists
        if instance_id not in self.industry_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Delete instance
        del self.industry_instances[instance_id]
        
        # Delete config if it exists
        if instance_id in self.industry_configs:
            del self.industry_configs[instance_id]
        
        # Log deletion
        logger.info(f"Deleted industry instance: {instance_id}")
        
        # Emit MCP event for industry instance deletion
        self.agent_core.emit_mcp_event("application/industry", {
            "action": "delete_instance",
            "instance_id": instance_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id
        }
    
    def get_industry_templates(self) -> List[Dict[str, Any]]:
        """
        Get all industry-specific templates.
        
        Returns:
            List of templates
        """
        return list(self.industry_templates.values())
    
    def get_industry_instances(self) -> List[Dict[str, Any]]:
        """
        Get all industry-specific instances.
        
        Returns:
            List of instances
        """
        return list(self.industry_instances.values())
    
    def get_industry_instances_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """
        Get all industry-specific instances for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            List of instances
        """
        return [instance for instance in self.industry_instances.values() if instance["industry"] == industry]
    
    def initialize_default_templates(self) -> Dict[str, Any]:
        """
        Initialize default industry-specific templates.
        
        Returns:
            Initialization result
        """
        logger.info("Initializing default industry templates")
        
        # Define default templates
        default_templates = [
            {
                "template_id": "industry-manufacturing",
                "name": "Manufacturing Industry Template",
                "description": "Template for manufacturing industry applications",
                "industry": "manufacturing",
                "modules": [
                    {
                        "id": "predictive_maintenance",
                        "name": "Predictive Maintenance",
                        "description": "Predict maintenance needs for manufacturing equipment",
                        "enabled": True,
                        "config": {
                            "prediction_interval": 24,
                            "alert_threshold": 0.7
                        }
                    },
                    {
                        "id": "quality_control",
                        "name": "Quality Control",
                        "description": "Monitor and control product quality",
                        "enabled": True,
                        "config": {
                            "sampling_rate": 10,
                            "defect_threshold": 0.05
                        }
                    },
                    {
                        "id": "production_optimization",
                        "name": "Production Optimization",
                        "description": "Optimize production processes",
                        "enabled": True,
                        "config": {
                            "optimization_interval": 12,
                            "efficiency_target": 0.9
                        }
                    },
                    {
                        "id": "inventory_management",
                        "name": "Inventory Management",
                        "description": "Manage manufacturing inventory",
                        "enabled": True,
                        "config": {
                            "reorder_threshold": 0.2,
                            "safety_stock": 0.1
                        }
                    }
                ]
            },
            {
                "template_id": "industry-energy",
                "name": "Energy Industry Template",
                "description": "Template for energy industry applications",
                "industry": "energy",
                "modules": [
                    {
                        "id": "grid_monitoring",
                        "name": "Grid Monitoring",
                        "description": "Monitor energy grid performance",
                        "enabled": True,
                        "config": {
                            "monitoring_interval": 5,
                            "alert_threshold": 0.8
                        }
                    },
                    {
                        "id": "demand_forecasting",
                        "name": "Demand Forecasting",
                        "description": "Forecast energy demand",
                        "enabled": True,
                        "config": {
                            "forecast_horizon": 24,
                            "update_interval": 1
                        }
                    },
                    {
                        "id": "renewable_integration",
                        "name": "Renewable Integration",
                        "description": "Integrate renewable energy sources",
                        "enabled": True,
                        "config": {
                            "optimization_interval": 6,
                            "renewable_target": 0.3
                        }
                    },
                    {
                        "id": "energy_efficiency",
                        "name": "Energy Efficiency",
                        "description": "Optimize energy efficiency",
                        "enabled": True,
                        "config": {
                            "analysis_interval": 12,
                            "efficiency_target": 0.85
                        }
                    }
                ]
            },
            {
                "template_id": "industry-logistics",
                "name": "Logistics Industry Template",
                "description": "Template for logistics industry applications",
                "industry": "logistics",
                "modules": [
                    {
                        "id": "route_optimization",
                        "name": "Route Optimization",
                        "description": "Optimize delivery routes",
                        "enabled": True,
                        "config": {
                            "optimization_interval": 1,
                            "cost_weight": 0.7,
                            "time_weight": 0.3
                        }
                    },
                    {
                        "id": "fleet_management",
                        "name": "Fleet Management",
                        "description": "Manage logistics fleet",
                        "enabled": True,
                        "config": {
                            "maintenance_interval": 7,
                            "utilization_target": 0.8
                        }
                    },
                    {
                        "id": "warehouse_optimization",
                        "name": "Warehouse Optimization",
                        "description": "Optimize warehouse operations",
                        "enabled": True,
                        "config": {
                            "layout_update_interval": 30,
                            "picking_efficiency_target": 0.9
                        }
                    },
                    {
                        "id": "delivery_tracking",
                        "name": "Delivery Tracking",
                        "description": "Track deliveries in real-time",
                        "enabled": True,
                        "config": {
                            "update_interval": 0.1,
                            "geofence_radius": 0.5
                        }
                    }
                ]
            },
            {
                "template_id": "industry-healthcare",
                "name": "Healthcare Industry Template",
                "description": "Template for healthcare industry applications",
                "industry": "healthcare",
                "modules": [
                    {
                        "id": "patient_monitoring",
                        "name": "Patient Monitoring",
                        "description": "Monitor patient health in real-time",
                        "enabled": True,
                        "config": {
                            "monitoring_interval": 0.5,
                            "alert_threshold": 0.7
                        }
                    },
                    {
                        "id": "resource_allocation",
                        "name": "Resource Allocation",
                        "description": "Optimize healthcare resource allocation",
                        "enabled": True,
                        "config": {
                            "optimization_interval": 1,
                            "utilization_target": 0.85
                        }
                    },
                    {
                        "id": "treatment_optimization",
                        "name": "Treatment Optimization",
                        "description": "Optimize treatment plans",
                        "enabled": True,
                        "config": {
                            "update_interval": 24,
                            "effectiveness_threshold": 0.8
                        }
                    },
                    {
                        "id": "inventory_management",
                        "name": "Medical Inventory Management",
                        "description": "Manage medical supplies inventory",
                        "enabled": True,
                        "config": {
                            "reorder_threshold": 0.3,
                            "expiry_alert_days": 30
                        }
                    }
                ]
            },
            {
                "template_id": "industry-agriculture",
                "name": "Agriculture Industry Template",
                "description": "Template for agriculture industry applications",
                "industry": "agriculture",
                "modules": [
                    {
                        "id": "crop_monitoring",
                        "name": "Crop Monitoring",
                        "description": "Monitor crop health and growth",
                        "enabled": True,
                        "config": {
                            "monitoring_interval": 6,
                            "alert_threshold": 0.6
                        }
                    },
                    {
                        "id": "irrigation_optimization",
                        "name": "Irrigation Optimization",
                        "description": "Optimize irrigation schedules",
                        "enabled": True,
                        "config": {
                            "optimization_interval": 1,
                            "water_efficiency_target": 0.9
                        }
                    },
                    {
                        "id": "yield_prediction",
                        "name": "Yield Prediction",
                        "description": "Predict crop yields",
                        "enabled": True,
                        "config": {
                            "prediction_interval": 7,
                            "confidence_threshold": 0.7
                        }
                    },
                    {
                        "id": "pest_management",
                        "name": "Pest Management",
                        "description": "Manage pests and diseases",
                        "enabled": True,
                        "config": {
                            "monitoring_interval": 3,
                            "treatment_threshold": 0.5
                        }
                    }
                ]
            },
            {
                "template_id": "industry-defense",
                "name": "Defense Industry Template",
                "description": "Template for defense industry applications",
                "industry": "defense",
                "modules": [
                    {
                        "id": "asset_tracking",
                        "name": "Asset Tracking",
                        "description": "Track defense assets",
                        "enabled": True,
                        "config": {
                            "update_interval": 0.1,
                            "geofence_radius": 1.0
                        }
                    },
                    {
                        "id": "maintenance_optimization",
                        "name": "Maintenance Optimization",
                        "description": "Optimize maintenance of defense equipment",
                        "enabled": True,
                        "config": {
                            "prediction_interval": 24,
                            "readiness_target": 0.95
                        }
                    },
                    {
                        "id": "logistics_management",
                        "name": "Logistics Management",
                        "description": "Manage defense logistics",
                        "enabled": True,
                        "config": {
                            "optimization_interval": 6,
                            "efficiency_target": 0.9
                        }
                    },
                    {
                        "id": "training_simulation",
                        "name": "Training Simulation",
                        "description": "Simulate training scenarios",
                        "enabled": True,
                        "config": {
                            "complexity_level": 0.8,
                            "realism_level": 0.9
                        }
                    }
                ]
            },
            {
                "template_id": "industry-aerospace",
                "name": "Aerospace Industry Template",
                "description": "Template for aerospace industry applications",
                "industry": "aerospace",
                "modules": [
                    {
                        "id": "flight_monitoring",
                        "name": "Flight Monitoring",
                        "description": "Monitor flight performance",
                        "enabled": True,
                        "config": {
                            "update_interval": 0.1,
                            "alert_threshold": 0.8
                        }
                    },
                    {
                        "id": "maintenance_prediction",
                        "name": "Maintenance Prediction",
                        "description": "Predict maintenance needs for aerospace equipment",
                        "enabled": True,
                        "config": {
                            "prediction_horizon": 100,
                            "confidence_threshold": 0.9
                        }
                    },
                    {
                        "id": "fuel_optimization",
                        "name": "Fuel Optimization",
                        "description": "Optimize fuel consumption",
                        "enabled": True,
                        "config": {
                            "optimization_interval": 1,
                            "efficiency_target": 0.95
                        }
                    },
                    {
                        "id": "route_planning",
                        "name": "Route Planning",
                        "description": "Plan optimal flight routes",
                        "enabled": True,
                        "config": {
                            "update_interval": 1,
                            "weather_weight": 0.7,
                            "fuel_weight": 0.3
                        }
                    }
                ]
            },
            {
                "template_id": "industry-datacenter",
                "name": "Data Center Industry Template",
                "description": "Template for data center industry applications",
                "industry": "datacenter",
                "modules": [
                    {
                        "id": "power_management",
                        "name": "Power Management",
                        "description": "Manage data center power consumption",
                        "enabled": True,
                        "config": {
                            "optimization_interval": 0.1,
                            "efficiency_target": 0.9
                        }
                    },
                    {
                        "id": "cooling_optimization",
                        "name": "Cooling Optimization",
                        "description": "Optimize data center cooling",
                        "enabled": True,
                        "config": {
                            "update_interval": 0.1,
                            "temperature_target": 22
                        }
                    },
                    {
                        "id": "capacity_planning",
                        "name": "Capacity Planning",
                        "description": "Plan data center capacity",
                        "enabled": True,
                        "config": {
                            "planning_horizon": 90,
                            "utilization_target": 0.8
                        }
                    },
                    {
                        "id": "fault_prediction",
                        "name": "Fault Prediction",
                        "description": "Predict hardware faults",
                        "enabled": True,
                        "config": {
                            "prediction_interval": 1,
                            "confidence_threshold": 0.8
                        }
                    }
                ]
            }
        ]
        
        # Register templates
        registered_templates = []
        for template_config in default_templates:
            result = self.register_industry_template(template_config)
            if "error" not in result:
                registered_templates.append(result["template_id"])
        
        return {
            "status": "success",
            "registered_templates": registered_templates,
            "count": len(registered_templates)
        }
    
    def get_low_ticket_offers(self, industry: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get low ticket offers for specific industry or all industries.
        
        Args:
            industry: Optional industry filter
            
        Returns:
            List of low ticket offers
        """
        # Define low ticket offers by industry
        low_ticket_offers = {
            "manufacturing": [
                {
                    "id": "predictive_maintenance_basic",
                    "name": "Basic Predictive Maintenance",
                    "description": "Basic predictive maintenance for manufacturing equipment",
                    "price_tier": "low",
                    "features": [
                        "Equipment health monitoring",
                        "Basic failure prediction",
                        "Maintenance scheduling"
                    ]
                },
                {
                    "id": "quality_inspection_basic",
                    "name": "Basic Quality Inspection",
                    "description": "Basic quality inspection for manufacturing processes",
                    "price_tier": "low",
                    "features": [
                        "Visual defect detection",
                        "Quality metrics tracking",
                        "Basic reporting"
                    ]
                },
                {
                    "id": "inventory_optimization_basic",
                    "name": "Basic Inventory Optimization",
                    "description": "Basic inventory optimization for manufacturing",
                    "price_tier": "low",
                    "features": [
                        "Inventory level tracking",
                        "Basic reorder point calculation",
                        "Inventory reports"
                    ]
                }
            ],
            "energy": [
                {
                    "id": "energy_monitoring_basic",
                    "name": "Basic Energy Monitoring",
                    "description": "Basic energy consumption monitoring",
                    "price_tier": "low",
                    "features": [
                        "Real-time energy usage tracking",
                        "Basic usage analytics",
                        "Simple alerts"
                    ]
                },
                {
                    "id": "demand_forecasting_basic",
                    "name": "Basic Demand Forecasting",
                    "description": "Basic energy demand forecasting",
                    "price_tier": "low",
                    "features": [
                        "Short-term demand prediction",
                        "Historical trend analysis",
                        "Basic reporting"
                    ]
                },
                {
                    "id": "grid_monitoring_basic",
                    "name": "Basic Grid Monitoring",
                    "description": "Basic monitoring for energy grids",
                    "price_tier": "low",
                    "features": [
                        "Grid status monitoring",
                        "Basic anomaly detection",
                        "Simple alerts"
                    ]
                }
            ],
            "logistics": [
                {
                    "id": "route_optimization_basic",
                    "name": "Basic Route Optimization",
                    "description": "Basic route optimization for logistics",
                    "price_tier": "low",
                    "features": [
                        "Simple route planning",
                        "Fuel consumption estimation",
                        "Basic delivery scheduling"
                    ]
                },
                {
                    "id": "fleet_tracking_basic",
                    "name": "Basic Fleet Tracking",
                    "description": "Basic fleet tracking for logistics",
                    "price_tier": "low",
                    "features": [
                        "Real-time location tracking",
                        "Basic route history",
                        "Simple alerts"
                    ]
                },
                {
                    "id": "warehouse_management_basic",
                    "name": "Basic Warehouse Management",
                    "description": "Basic warehouse management for logistics",
                    "price_tier": "low",
                    "features": [
                        "Inventory tracking",
                        "Basic picking optimization",
                        "Simple space utilization"
                    ]
                }
            ],
            "healthcare": [
                {
                    "id": "patient_monitoring_basic",
                    "name": "Basic Patient Monitoring",
                    "description": "Basic patient health monitoring",
                    "price_tier": "low",
                    "features": [
                        "Vital signs tracking",
                        "Basic anomaly detection",
                        "Simple alerts"
                    ]
                },
                {
                    "id": "medication_tracking_basic",
                    "name": "Basic Medication Tracking",
                    "description": "Basic medication tracking for healthcare",
                    "price_tier": "low",
                    "features": [
                        "Medication schedule tracking",
                        "Basic adherence monitoring",
                        "Simple reminders"
                    ]
                },
                {
                    "id": "resource_scheduling_basic",
                    "name": "Basic Resource Scheduling",
                    "description": "Basic resource scheduling for healthcare",
                    "price_tier": "low",
                    "features": [
                        "Staff scheduling",
                        "Basic resource allocation",
                        "Simple utilization tracking"
                    ]
                }
            ],
            "agriculture": [
                {
                    "id": "crop_monitoring_basic",
                    "name": "Basic Crop Monitoring",
                    "description": "Basic crop health monitoring",
                    "price_tier": "low",
                    "features": [
                        "Growth stage tracking",
                        "Basic health assessment",
                        "Simple alerts"
                    ]
                },
                {
                    "id": "irrigation_management_basic",
                    "name": "Basic Irrigation Management",
                    "description": "Basic irrigation management for agriculture",
                    "price_tier": "low",
                    "features": [
                        "Soil moisture tracking",
                        "Basic irrigation scheduling",
                        "Water usage reporting"
                    ]
                },
                {
                    "id": "weather_monitoring_basic",
                    "name": "Basic Weather Monitoring",
                    "description": "Basic weather monitoring for agriculture",
                    "price_tier": "low",
                    "features": [
                        "Local weather tracking",
                        "Basic forecast integration",
                        "Simple alerts"
                    ]
                }
            ],
            "defense": [
                {
                    "id": "asset_tracking_basic",
                    "name": "Basic Asset Tracking",
                    "description": "Basic asset tracking for defense",
                    "price_tier": "low",
                    "features": [
                        "Real-time location tracking",
                        "Basic movement history",
                        "Simple geofencing"
                    ]
                },
                {
                    "id": "maintenance_scheduling_basic",
                    "name": "Basic Maintenance Scheduling",
                    "description": "Basic maintenance scheduling for defense equipment",
                    "price_tier": "low",
                    "features": [
                        "Maintenance calendar",
                        "Basic service tracking",
                        "Simple alerts"
                    ]
                },
                {
                    "id": "inventory_management_basic",
                    "name": "Basic Inventory Management",
                    "description": "Basic inventory management for defense",
                    "price_tier": "low",
                    "features": [
                        "Inventory level tracking",
                        "Basic reorder management",
                        "Simple reporting"
                    ]
                }
            ],
            "aerospace": [
                {
                    "id": "flight_monitoring_basic",
                    "name": "Basic Flight Monitoring",
                    "description": "Basic flight performance monitoring",
                    "price_tier": "low",
                    "features": [
                        "Flight parameter tracking",
                        "Basic performance analysis",
                        "Simple alerts"
                    ]
                },
                {
                    "id": "maintenance_tracking_basic",
                    "name": "Basic Maintenance Tracking",
                    "description": "Basic maintenance tracking for aerospace",
                    "price_tier": "low",
                    "features": [
                        "Maintenance schedule tracking",
                        "Basic service history",
                        "Simple compliance reporting"
                    ]
                },
                {
                    "id": "fuel_monitoring_basic",
                    "name": "Basic Fuel Monitoring",
                    "description": "Basic fuel consumption monitoring",
                    "price_tier": "low",
                    "features": [
                        "Fuel usage tracking",
                        "Basic efficiency analysis",
                        "Simple reporting"
                    ]
                }
            ],
            "datacenter": [
                {
                    "id": "power_monitoring_basic",
                    "name": "Basic Power Monitoring",
                    "description": "Basic power consumption monitoring for data centers",
                    "price_tier": "low",
                    "features": [
                        "Power usage tracking",
                        "Basic efficiency metrics",
                        "Simple alerts"
                    ]
                },
                {
                    "id": "temperature_monitoring_basic",
                    "name": "Basic Temperature Monitoring",
                    "description": "Basic temperature monitoring for data centers",
                    "price_tier": "low",
                    "features": [
                        "Temperature tracking",
                        "Basic hotspot detection",
                        "Simple alerts"
                    ]
                },
                {
                    "id": "server_monitoring_basic",
                    "name": "Basic Server Monitoring",
                    "description": "Basic server performance monitoring",
                    "price_tier": "low",
                    "features": [
                        "CPU/memory usage tracking",
                        "Basic performance metrics",
                        "Simple alerts"
                    ]
                }
            ]
        }
        
        # Return offers for specific industry or all industries
        if industry:
            return low_ticket_offers.get(industry, [])
        else:
            all_offers = []
            for industry_offers in low_ticket_offers.values():
                all_offers.extend(industry_offers)
            return all_offers
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get component information.
        
        Returns:
            Component information
        """
        return {
            "id": "industry_specific_modules",
            "type": "IndustrySpecificModules",
            "name": "Industry-Specific Modules",
            "status": "operational",
            "templates": len(self.industry_templates),
            "instances": len(self.industry_instances),
            "industries": len(set(template["industry"] for template in self.industry_templates.values()))
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
        if action_id == "register_industry_template":
            return self.register_industry_template(data)
        elif action_id == "create_industry_instance":
            return self.create_industry_instance(
                data.get("template_id", ""),
                data.get("instance_config", {})
            )
        elif action_id == "get_industry_instance":
            instance = self.get_industry_instance(data.get("instance_id", ""))
            return {"instance": instance} if instance else {"error": "Instance not found"}
        elif action_id == "update_industry_instance":
            return self.update_industry_instance(
                data.get("instance_id", ""),
                data.get("update_data", {})
            )
        elif action_id == "update_industry_config":
            return self.update_industry_config(
                data.get("instance_id", ""),
                data.get("config_data", {})
            )
        elif action_id == "get_industry_config":
            config = self.get_industry_config(data.get("instance_id", ""))
            return {"config": config} if config else {"error": "Config not found"}
        elif action_id == "delete_industry_instance":
            return self.delete_industry_instance(data.get("instance_id", ""))
        elif action_id == "get_industry_templates":
            return {"templates": self.get_industry_templates()}
        elif action_id == "get_industry_instances":
            return {"instances": self.get_industry_instances()}
        elif action_id == "get_industry_instances_by_industry":
            return {"instances": self.get_industry_instances_by_industry(data.get("industry", ""))}
        elif action_id == "initialize_default_templates":
            return self.initialize_default_templates()
        elif action_id == "get_low_ticket_offers":
            return {"offers": self.get_low_ticket_offers(data.get("industry"))}
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
            "templates": len(self.industry_templates),
            "instances": len(self.industry_instances),
            "configs": len(self.industry_configs),
            "industries": len(set(template["industry"] for template in self.industry_templates.values()))
        }
