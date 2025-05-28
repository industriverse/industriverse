"""
Industrial Context Adapter for the Industriverse UI/UX Layer.

This module provides industry-specific context adaptation for the Universal Skin and Agent Capsules,
enabling seamless integration with different industrial environments and workflows.

Author: Manus
"""

import logging
import json
import time
import threading
import queue
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field

class IndustryType(Enum):
    """Enumeration of supported industry types."""
    MANUFACTURING = "manufacturing"
    LOGISTICS = "logistics"
    ENERGY = "energy"
    RETAIL = "retail"
    AEROSPACE = "aerospace"
    DEFENSE = "defense"
    DATA_CENTERS = "data_centers"
    EDGE_COMPUTING = "edge_computing"
    IOT = "iot"
    GENERAL = "general"

class IndustryRole(Enum):
    """Enumeration of industry roles."""
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    ENGINEER = "engineer"
    TECHNICIAN = "technician"
    ANALYST = "analyst"
    EXECUTIVE = "executive"
    ADMIN = "admin"
    GUEST = "guest"

@dataclass
class IndustryContext:
    """Data class representing industry context."""
    industry: IndustryType
    role: IndustryRole
    facility: str
    department: str
    process: str
    equipment: Optional[str] = None
    workflow: Optional[str] = None
    shift: Optional[str] = None
    safety_level: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the industry context to a dictionary."""
        return {
            "industry": self.industry.value,
            "role": self.role.value,
            "facility": self.facility,
            "department": self.department,
            "process": self.process,
            "equipment": self.equipment,
            "workflow": self.workflow,
            "shift": self.shift,
            "safety_level": self.safety_level,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndustryContext':
        """Create industry context from a dictionary."""
        return cls(
            industry=IndustryType(data["industry"]),
            role=IndustryRole(data["role"]),
            facility=data["facility"],
            department=data["department"],
            process=data["process"],
            equipment=data.get("equipment"),
            workflow=data.get("workflow"),
            shift=data.get("shift"),
            safety_level=data.get("safety_level", 0),
            metadata=data.get("metadata", {})
        )

class IndustrialContextAdapter:
    """
    Provides industry-specific context adaptation for the Universal Skin and Agent Capsules.
    
    This class provides:
    - Industry-specific terminology adaptation
    - Role-based view customization
    - Industry-specific visualization preferences
    - Workflow template adaptation
    - Metric and alert threshold customization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Industrial Context Adapter.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.event_handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self.current_context: Optional[IndustryContext] = None
        self.industry_templates: Dict[str, Dict[str, Any]] = {}
        self.role_templates: Dict[str, Dict[str, Any]] = {}
        self.terminology_maps: Dict[str, Dict[str, str]] = {}
        self.metric_thresholds: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.running = False
        self.worker_thread = None
        self.event_queue = queue.Queue()
        
        # Initialize from config if provided
        if config:
            if "industry_templates" in config:
                self.industry_templates = config["industry_templates"]
            if "role_templates" in config:
                self.role_templates = config["role_templates"]
            if "terminology_maps" in config:
                self.terminology_maps = config["terminology_maps"]
            if "metric_thresholds" in config:
                self.metric_thresholds = config["metric_thresholds"]
            if "current_context" in config:
                self.current_context = IndustryContext.from_dict(config["current_context"])
                
        # Load default templates if not provided
        if not self.industry_templates:
            self._load_default_industry_templates()
        if not self.role_templates:
            self._load_default_role_templates()
        if not self.terminology_maps:
            self._load_default_terminology_maps()
        if not self.metric_thresholds:
            self._load_default_metric_thresholds()
            
        self.logger.info("Industrial Context Adapter initialized")
        
    def _load_default_industry_templates(self) -> None:
        """
        Load default industry templates.
        """
        self.industry_templates = {
            IndustryType.MANUFACTURING.value: {
                "dashboard_layout": "production_focused",
                "primary_metrics": ["oee", "throughput", "quality", "downtime"],
                "secondary_metrics": ["energy_consumption", "material_usage", "maintenance_status"],
                "visualization_preferences": {
                    "color_scheme": "industrial",
                    "chart_types": {
                        "production": "bar",
                        "quality": "line",
                        "maintenance": "gauge"
                    }
                },
                "default_views": ["production_overview", "quality_control", "maintenance_status"]
            },
            IndustryType.LOGISTICS.value: {
                "dashboard_layout": "logistics_focused",
                "primary_metrics": ["on_time_delivery", "inventory_levels", "transportation_costs", "order_accuracy"],
                "secondary_metrics": ["warehouse_utilization", "route_efficiency", "fuel_consumption"],
                "visualization_preferences": {
                    "color_scheme": "logistics",
                    "chart_types": {
                        "delivery": "map",
                        "inventory": "bar",
                        "transportation": "line"
                    }
                },
                "default_views": ["shipment_tracking", "inventory_management", "route_optimization"]
            },
            IndustryType.ENERGY.value: {
                "dashboard_layout": "energy_focused",
                "primary_metrics": ["power_output", "efficiency", "uptime", "emissions"],
                "secondary_metrics": ["maintenance_status", "resource_consumption", "grid_stability"],
                "visualization_preferences": {
                    "color_scheme": "energy",
                    "chart_types": {
                        "power": "line",
                        "efficiency": "gauge",
                        "emissions": "area"
                    }
                },
                "default_views": ["power_generation", "grid_management", "emissions_monitoring"]
            },
            IndustryType.RETAIL.value: {
                "dashboard_layout": "retail_focused",
                "primary_metrics": ["sales", "inventory_turnover", "customer_satisfaction", "conversion_rate"],
                "secondary_metrics": ["foot_traffic", "average_transaction_value", "return_rate"],
                "visualization_preferences": {
                    "color_scheme": "retail",
                    "chart_types": {
                        "sales": "bar",
                        "inventory": "line",
                        "customer": "pie"
                    }
                },
                "default_views": ["sales_performance", "inventory_management", "customer_insights"]
            },
            IndustryType.AEROSPACE.value: {
                "dashboard_layout": "aerospace_focused",
                "primary_metrics": ["flight_status", "maintenance_schedule", "part_lifecycle", "safety_incidents"],
                "secondary_metrics": ["fuel_efficiency", "on_time_performance", "passenger_satisfaction"],
                "visualization_preferences": {
                    "color_scheme": "aerospace",
                    "chart_types": {
                        "flight": "timeline",
                        "maintenance": "gantt",
                        "safety": "heatmap"
                    }
                },
                "default_views": ["flight_operations", "maintenance_planning", "safety_management"]
            },
            IndustryType.DEFENSE.value: {
                "dashboard_layout": "defense_focused",
                "primary_metrics": ["operational_readiness", "mission_status", "equipment_availability", "security_status"],
                "secondary_metrics": ["training_completion", "supply_levels", "maintenance_status"],
                "visualization_preferences": {
                    "color_scheme": "defense",
                    "chart_types": {
                        "operations": "map",
                        "readiness": "gauge",
                        "security": "heatmap"
                    }
                },
                "default_views": ["operational_status", "equipment_readiness", "security_monitoring"]
            },
            IndustryType.DATA_CENTERS.value: {
                "dashboard_layout": "data_center_focused",
                "primary_metrics": ["server_uptime", "power_usage_effectiveness", "cooling_efficiency", "network_performance"],
                "secondary_metrics": ["rack_utilization", "backup_status", "security_incidents"],
                "visualization_preferences": {
                    "color_scheme": "data_center",
                    "chart_types": {
                        "uptime": "line",
                        "power": "gauge",
                        "network": "area"
                    }
                },
                "default_views": ["infrastructure_monitoring", "power_management", "network_operations"]
            },
            IndustryType.EDGE_COMPUTING.value: {
                "dashboard_layout": "edge_computing_focused",
                "primary_metrics": ["edge_device_status", "latency", "bandwidth_usage", "processing_load"],
                "secondary_metrics": ["power_consumption", "storage_utilization", "security_status"],
                "visualization_preferences": {
                    "color_scheme": "edge_computing",
                    "chart_types": {
                        "device_status": "map",
                        "latency": "line",
                        "processing": "heatmap"
                    }
                },
                "default_views": ["edge_device_management", "performance_monitoring", "network_topology"]
            },
            IndustryType.IOT.value: {
                "dashboard_layout": "iot_focused",
                "primary_metrics": ["device_status", "data_throughput", "battery_levels", "connectivity_status"],
                "secondary_metrics": ["sensor_readings", "firmware_versions", "alert_frequency"],
                "visualization_preferences": {
                    "color_scheme": "iot",
                    "chart_types": {
                        "device_status": "map",
                        "data": "line",
                        "battery": "gauge"
                    }
                },
                "default_views": ["device_management", "data_analytics", "alert_monitoring"]
            },
            IndustryType.GENERAL.value: {
                "dashboard_layout": "general_focused",
                "primary_metrics": ["performance", "efficiency", "quality", "cost"],
                "secondary_metrics": ["resource_utilization", "schedule_adherence", "customer_satisfaction"],
                "visualization_preferences": {
                    "color_scheme": "general",
                    "chart_types": {
                        "performance": "bar",
                        "efficiency": "line",
                        "quality": "gauge"
                    }
                },
                "default_views": ["overview", "performance_metrics", "resource_management"]
            }
        }
        
    def _load_default_role_templates(self) -> None:
        """
        Load default role templates.
        """
        self.role_templates = {
            IndustryRole.OPERATOR.value: {
                "dashboard_layout": "operational_focused",
                "primary_metrics": ["current_production", "quality_metrics", "equipment_status", "safety_alerts"],
                "secondary_metrics": ["upcoming_tasks", "shift_performance", "material_status"],
                "visualization_preferences": {
                    "detail_level": "high",
                    "update_frequency": "real-time",
                    "alert_threshold": "medium"
                },
                "default_views": ["current_operations", "equipment_status", "task_list"]
            },
            IndustryRole.SUPERVISOR.value: {
                "dashboard_layout": "supervisory_focused",
                "primary_metrics": ["team_performance", "production_status", "quality_metrics", "safety_incidents"],
                "secondary_metrics": ["resource_utilization", "schedule_adherence", "maintenance_status"],
                "visualization_preferences": {
                    "detail_level": "medium",
                    "update_frequency": "near-real-time",
                    "alert_threshold": "medium"
                },
                "default_views": ["team_overview", "production_status", "quality_control"]
            },
            IndustryRole.MANAGER.value: {
                "dashboard_layout": "management_focused",
                "primary_metrics": ["department_performance", "resource_utilization", "budget_status", "quality_trends"],
                "secondary_metrics": ["employee_metrics", "maintenance_costs", "compliance_status"],
                "visualization_preferences": {
                    "detail_level": "medium",
                    "update_frequency": "periodic",
                    "alert_threshold": "high"
                },
                "default_views": ["department_overview", "resource_management", "performance_trends"]
            },
            IndustryRole.ENGINEER.value: {
                "dashboard_layout": "engineering_focused",
                "primary_metrics": ["system_performance", "technical_parameters", "quality_metrics", "design_status"],
                "secondary_metrics": ["test_results", "resource_utilization", "issue_tracking"],
                "visualization_preferences": {
                    "detail_level": "very_high",
                    "update_frequency": "real-time",
                    "alert_threshold": "low"
                },
                "default_views": ["system_monitoring", "technical_parameters", "issue_tracking"]
            },
            IndustryRole.TECHNICIAN.value: {
                "dashboard_layout": "technical_focused",
                "primary_metrics": ["maintenance_tasks", "equipment_status", "spare_parts", "technical_alerts"],
                "secondary_metrics": ["maintenance_history", "tool_status", "documentation_access"],
                "visualization_preferences": {
                    "detail_level": "high",
                    "update_frequency": "real-time",
                    "alert_threshold": "low"
                },
                "default_views": ["maintenance_tasks", "equipment_status", "technical_documentation"]
            },
            IndustryRole.ANALYST.value: {
                "dashboard_layout": "analytical_focused",
                "primary_metrics": ["performance_trends", "efficiency_metrics", "quality_analysis", "cost_analysis"],
                "secondary_metrics": ["historical_data", "benchmark_comparisons", "forecast_models"],
                "visualization_preferences": {
                    "detail_level": "high",
                    "update_frequency": "periodic",
                    "alert_threshold": "medium"
                },
                "default_views": ["trend_analysis", "performance_metrics", "forecasting"]
            },
            IndustryRole.EXECUTIVE.value: {
                "dashboard_layout": "executive_focused",
                "primary_metrics": ["overall_performance", "financial_metrics", "strategic_initiatives", "market_position"],
                "secondary_metrics": ["resource_allocation", "risk_assessment", "compliance_status"],
                "visualization_preferences": {
                    "detail_level": "low",
                    "update_frequency": "periodic",
                    "alert_threshold": "high"
                },
                "default_views": ["executive_summary", "strategic_initiatives", "performance_overview"]
            },
            IndustryRole.ADMIN.value: {
                "dashboard_layout": "administrative_focused",
                "primary_metrics": ["system_status", "user_management", "security_status", "resource_allocation"],
                "secondary_metrics": ["audit_logs", "backup_status", "compliance_status"],
                "visualization_preferences": {
                    "detail_level": "medium",
                    "update_frequency": "near-real-time",
                    "alert_threshold": "medium"
                },
                "default_views": ["system_administration", "user_management", "security_monitoring"]
            },
            IndustryRole.GUEST.value: {
                "dashboard_layout": "guest_focused",
                "primary_metrics": ["overview_metrics", "public_information", "general_status"],
                "secondary_metrics": [],
                "visualization_preferences": {
                    "detail_level": "very_low",
                    "update_frequency": "periodic",
                    "alert_threshold": "very_high"
                },
                "default_views": ["general_overview", "public_information"]
            }
        }
        
    def _load_default_terminology_maps(self) -> None:
        """
        Load default terminology maps.
        """
        self.terminology_maps = {
            IndustryType.MANUFACTURING.value: {
                "production_line": "Production Line",
                "machine": "Machine",
                "operator": "Operator",
                "downtime": "Downtime",
                "cycle_time": "Cycle Time",
                "oee": "Overall Equipment Effectiveness",
                "quality_control": "Quality Control",
                "maintenance": "Maintenance",
                "work_order": "Work Order",
                "batch": "Batch",
                "material": "Material",
                "inventory": "Inventory",
                "scrap": "Scrap",
                "rework": "Rework",
                "assembly": "Assembly",
                "inspection": "Inspection"
            },
            IndustryType.LOGISTICS.value: {
                "warehouse": "Warehouse",
                "shipment": "Shipment",
                "delivery": "Delivery",
                "route": "Route",
                "carrier": "Carrier",
                "inventory": "Inventory",
                "order": "Order",
                "picking": "Picking",
                "packing": "Packing",
                "loading": "Loading",
                "unloading": "Unloading",
                "tracking": "Tracking",
                "transportation": "Transportation",
                "fleet": "Fleet",
                "dock": "Dock",
                "container": "Container"
            },
            IndustryType.ENERGY.value: {
                "plant": "Plant",
                "generator": "Generator",
                "turbine": "Turbine",
                "grid": "Grid",
                "substation": "Substation",
                "transmission": "Transmission",
                "distribution": "Distribution",
                "power": "Power",
                "energy": "Energy",
                "output": "Output",
                "efficiency": "Efficiency",
                "emissions": "Emissions",
                "renewable": "Renewable",
                "fossil_fuel": "Fossil Fuel",
                "load": "Load",
                "capacity": "Capacity"
            },
            IndustryType.RETAIL.value: {
                "store": "Store",
                "sales": "Sales",
                "inventory": "Inventory",
                "customer": "Customer",
                "transaction": "Transaction",
                "product": "Product",
                "category": "Category",
                "promotion": "Promotion",
                "discount": "Discount",
                "checkout": "Checkout",
                "return": "Return",
                "shelf": "Shelf",
                "display": "Display",
                "point_of_sale": "Point of Sale",
                "foot_traffic": "Foot Traffic",
                "conversion_rate": "Conversion Rate"
            },
            IndustryType.AEROSPACE.value: {
                "aircraft": "Aircraft",
                "flight": "Flight",
                "maintenance": "Maintenance",
                "inspection": "Inspection",
                "component": "Component",
                "system": "System",
                "avionics": "Avionics",
                "navigation": "Navigation",
                "propulsion": "Propulsion",
                "airframe": "Airframe",
                "cockpit": "Cockpit",
                "runway": "Runway",
                "hangar": "Hangar",
                "air_traffic_control": "Air Traffic Control",
                "flight_plan": "Flight Plan",
                "airworthiness": "Airworthiness"
            },
            IndustryType.DEFENSE.value: {
                "mission": "Mission",
                "operation": "Operation",
                "equipment": "Equipment",
                "personnel": "Personnel",
                "security": "Security",
                "intelligence": "Intelligence",
                "surveillance": "Surveillance",
                "reconnaissance": "Reconnaissance",
                "command": "Command",
                "control": "Control",
                "communications": "Communications",
                "logistics": "Logistics",
                "training": "Training",
                "readiness": "Readiness",
                "deployment": "Deployment",
                "threat": "Threat"
            },
            IndustryType.DATA_CENTERS.value: {
                "server": "Server",
                "rack": "Rack",
                "cooling": "Cooling",
                "power": "Power",
                "network": "Network",
                "storage": "Storage",
                "backup": "Backup",
                "virtualization": "Virtualization",
                "cloud": "Cloud",
                "data": "Data",
                "uptime": "Uptime",
                "latency": "Latency",
                "bandwidth": "Bandwidth",
                "security": "Security",
                "monitoring": "Monitoring",
                "infrastructure": "Infrastructure"
            },
            IndustryType.EDGE_COMPUTING.value: {
                "edge_device": "Edge Device",
                "gateway": "Gateway",
                "sensor": "Sensor",
                "actuator": "Actuator",
                "processing": "Processing",
                "latency": "Latency",
                "bandwidth": "Bandwidth",
                "connectivity": "Connectivity",
                "local_storage": "Local Storage",
                "local_processing": "Local Processing",
                "cloud_connection": "Cloud Connection",
                "deployment": "Deployment",
                "management": "Management",
                "security": "Security",
                "power_consumption": "Power Consumption",
                "reliability": "Reliability"
            },
            IndustryType.IOT.value: {
                "device": "Device",
                "sensor": "Sensor",
                "actuator": "Actuator",
                "gateway": "Gateway",
                "connectivity": "Connectivity",
                "data": "Data",
                "telemetry": "Telemetry",
                "firmware": "Firmware",
                "battery": "Battery",
                "power": "Power",
                "protocol": "Protocol",
                "network": "Network",
                "cloud": "Cloud",
                "edge": "Edge",
                "security": "Security",
                "provisioning": "Provisioning"
            },
            IndustryType.GENERAL.value: {
                "system": "System",
                "process": "Process",
                "resource": "Resource",
                "user": "User",
                "data": "Data",
                "report": "Report",
                "task": "Task",
                "project": "Project",
                "performance": "Performance",
                "efficiency": "Efficiency",
                "quality": "Quality",
                "cost": "Cost",
                "schedule": "Schedule",
                "status": "Status",
                "alert": "Alert",
                "notification": "Notification"
            }
        }
        
    def _load_default_metric_thresholds(self) -> None:
        """
        Load default metric thresholds.
        """
        self.metric_thresholds = {
            IndustryType.MANUFACTURING.value: {
                "oee": {
                    "warning": 75,
                    "critical": 60,
                    "unit": "%",
                    "direction": "higher_is_better"
                },
                "downtime": {
                    "warning": 10,
                    "critical": 20,
                    "unit": "%",
                    "direction": "lower_is_better"
                },
                "quality": {
                    "warning": 95,
                    "critical": 90,
                    "unit": "%",
                    "direction": "higher_is_better"
                },
                "throughput": {
                    "warning": 85,
                    "critical": 70,
                    "unit": "%",
                    "direction": "higher_is_better"
                }
            },
            IndustryType.LOGISTICS.value: {
                "on_time_delivery": {
                    "warning": 90,
                    "critical": 80,
                    "unit": "%",
                    "direction": "higher_is_better"
                },
                "inventory_accuracy": {
                    "warning": 95,
                    "critical": 90,
                    "unit": "%",
                    "direction": "higher_is_better"
                },
                "order_accuracy": {
                    "warning": 98,
                    "critical": 95,
                    "unit": "%",
                    "direction": "higher_is_better"
                },
                "warehouse_utilization": {
                    "warning": 85,
                    "critical": 95,
                    "unit": "%",
                    "direction": "middle_is_better"
                }
            },
            IndustryType.ENERGY.value: {
                "efficiency": {
                    "warning": 85,
                    "critical": 75,
                    "unit": "%",
                    "direction": "higher_is_better"
                },
                "uptime": {
                    "warning": 95,
                    "critical": 90,
                    "unit": "%",
                    "direction": "higher_is_better"
                },
                "emissions": {
                    "warning": 90,
                    "critical": 110,
                    "unit": "%",
                    "direction": "lower_is_better"
                },
                "grid_stability": {
                    "warning": 95,
                    "critical": 90,
                    "unit": "%",
                    "direction": "higher_is_better"
                }
            }
            # Additional industries would be defined here
        }
        
    def start(self) -> bool:
        """
        Start the Industrial Context Adapter.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.logger.warning("Industrial Context Adapter already running")
            return False
            
        self.running = True
        self.worker_thread = threading.Thread(target=self._event_worker, daemon=True)
        self.worker_thread.start()
        
        self.logger.info("Industrial Context Adapter started")
        return True
        
    def stop(self) -> bool:
        """
        Stop the Industrial Context Adapter.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.running:
            self.logger.warning("Industrial Context Adapter not running")
            return False
            
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            
        self.logger.info("Industrial Context Adapter stopped")
        return True
        
    def _event_worker(self) -> None:
        """
        Worker thread for processing events.
        """
        self.logger.info("Event worker thread started")
        
        while self.running:
            try:
                event_data = self.event_queue.get(timeout=1.0)
                self._process_event(event_data)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
                
        self.logger.info("Event worker thread stopped")
        
    def _process_event(self, event_data: Dict[str, Any]) -> None:
        """
        Process event data.
        
        Args:
            event_data: Event data to process
        """
        event_type = event_data.get("type")
        if not event_type:
            self.logger.warning("Event data missing type")
            return
            
        # Notify event handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {e}")
                    
        # Notify wildcard handlers
        if "*" in self.event_handlers:
            for handler in self.event_handlers["*"]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.logger.error(f"Error in wildcard event handler: {e}")
                    
    def register_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Register an event handler.
        
        Args:
            event_type: Event type to handle, or "*" for all events
            handler: Handler function
            
        Returns:
            True if the handler was registered, False otherwise
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
            
        self.event_handlers[event_type].append(handler)
        self.logger.debug(f"Registered event handler for {event_type}")
        
        return True
        
    def unregister_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unregister an event handler.
        
        Args:
            event_type: Event type the handler was registered for, or "*" for all events
            handler: Handler function to unregister
            
        Returns:
            True if the handler was unregistered, False otherwise
        """
        if event_type not in self.event_handlers:
            return False
            
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            self.logger.debug(f"Unregistered event handler for {event_type}")
            
            # Clean up empty handler lists
            if not self.event_handlers[event_type]:
                del self.event_handlers[event_type]
                
            return True
            
        return False
        
    def set_industry_context(self, context: IndustryContext) -> None:
        """
        Set the current industry context.
        
        Args:
            context: Industry context
        """
        old_context = self.current_context
        self.current_context = context
        
        # Dispatch context change event
        self._dispatch_event("industry_context_changed", {
            "old_context": old_context.to_dict() if old_context else None,
            "new_context": context.to_dict()
        })
        
        self.logger.info(f"Industry context changed to {context.industry.value}")
        
    def get_industry_context(self) -> Optional[IndustryContext]:
        """
        Get the current industry context.
        
        Returns:
            Industry context, or None if not set
        """
        return self.current_context
        
    def _dispatch_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event.
        
        Args:
            event_type: Event type
            event_data: Event data
        """
        # Add event type to data if not present
        if "type" not in event_data:
            event_data["type"] = event_type
            
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = time.time()
            
        # Queue for processing
        self.event_queue.put(event_data)
        
    def get_industry_template(self, industry: Union[IndustryType, str]) -> Dict[str, Any]:
        """
        Get the template for a specific industry.
        
        Args:
            industry: Industry type or value
            
        Returns:
            Industry template, or empty dict if not found
        """
        industry_value = industry.value if isinstance(industry, IndustryType) else industry
        return self.industry_templates.get(industry_value, {})
        
    def get_role_template(self, role: Union[IndustryRole, str]) -> Dict[str, Any]:
        """
        Get the template for a specific role.
        
        Args:
            role: Role type or value
            
        Returns:
            Role template, or empty dict if not found
        """
        role_value = role.value if isinstance(role, IndustryRole) else role
        return self.role_templates.get(role_value, {})
        
    def get_terminology_map(self, industry: Union[IndustryType, str]) -> Dict[str, str]:
        """
        Get the terminology map for a specific industry.
        
        Args:
            industry: Industry type or value
            
        Returns:
            Terminology map, or empty dict if not found
        """
        industry_value = industry.value if isinstance(industry, IndustryType) else industry
        return self.terminology_maps.get(industry_value, {})
        
    def get_metric_thresholds(self, industry: Union[IndustryType, str], metric: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the metric thresholds for a specific industry and optionally a specific metric.
        
        Args:
            industry: Industry type or value
            metric: Optional metric name
            
        Returns:
            Metric thresholds, or empty dict if not found
        """
        industry_value = industry.value if isinstance(industry, IndustryType) else industry
        
        if industry_value not in self.metric_thresholds:
            return {}
            
        if metric is not None:
            return self.metric_thresholds[industry_value].get(metric, {})
            
        return self.metric_thresholds[industry_value]
        
    def translate_term(self, term: str, industry: Optional[Union[IndustryType, str]] = None) -> str:
        """
        Translate a generic term to an industry-specific term.
        
        Args:
            term: Generic term
            industry: Optional industry type or value, or None to use current context
            
        Returns:
            Industry-specific term, or the original term if not found
        """
        if industry is None:
            if self.current_context is None:
                return term
                
            industry = self.current_context.industry
            
        industry_value = industry.value if isinstance(industry, IndustryType) else industry
        
        if industry_value not in self.terminology_maps:
            return term
            
        return self.terminology_maps[industry_value].get(term, term)
        
    def get_adapted_dashboard_layout(self) -> Dict[str, Any]:
        """
        Get the adapted dashboard layout based on the current context.
        
        Returns:
            Adapted dashboard layout, or empty dict if no context is set
        """
        if self.current_context is None:
            return {}
            
        industry_template = self.get_industry_template(self.current_context.industry)
        role_template = self.get_role_template(self.current_context.role)
        
        # Start with industry template
        layout = {}
        if "dashboard_layout" in industry_template:
            layout["layout_type"] = industry_template["dashboard_layout"]
            
        # Add primary metrics
        if "primary_metrics" in industry_template:
            layout["primary_metrics"] = industry_template["primary_metrics"]
            
        # Add secondary metrics
        if "secondary_metrics" in industry_template:
            layout["secondary_metrics"] = industry_template["secondary_metrics"]
            
        # Add visualization preferences
        if "visualization_preferences" in industry_template:
            layout["visualization_preferences"] = industry_template["visualization_preferences"]
            
        # Add default views
        if "default_views" in industry_template:
            layout["default_views"] = industry_template["default_views"]
            
        # Override with role-specific settings
        if "dashboard_layout" in role_template:
            layout["layout_type"] = role_template["dashboard_layout"]
            
        if "primary_metrics" in role_template:
            layout["primary_metrics"] = role_template["primary_metrics"]
            
        if "secondary_metrics" in role_template:
            layout["secondary_metrics"] = role_template["secondary_metrics"]
            
        if "visualization_preferences" in role_template:
            if "visualization_preferences" not in layout:
                layout["visualization_preferences"] = {}
                
            layout["visualization_preferences"].update(role_template["visualization_preferences"])
            
        if "default_views" in role_template:
            layout["default_views"] = role_template["default_views"]
            
        return layout
        
    def get_adapted_metric_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the adapted metric thresholds based on the current context.
        
        Returns:
            Adapted metric thresholds, or empty dict if no context is set
        """
        if self.current_context is None:
            return {}
            
        return self.get_metric_thresholds(self.current_context.industry)
        
    def get_adapted_terminology(self) -> Dict[str, str]:
        """
        Get the adapted terminology based on the current context.
        
        Returns:
            Adapted terminology, or empty dict if no context is set
        """
        if self.current_context is None:
            return {}
            
        return self.get_terminology_map(self.current_context.industry)

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create Industrial Context Adapter
    adapter = IndustrialContextAdapter()
    adapter.start()
    
    # Register event handler
    def handle_context_change(event_data):
        print(f"Industry context changed: {event_data}")
        
    adapter.register_event_handler("industry_context_changed", handle_context_change)
    
    # Set industry context
    context = IndustryContext(
        industry=IndustryType.MANUFACTURING,
        role=IndustryRole.OPERATOR,
        facility="Factory 1",
        department="Assembly",
        process="Final Assembly",
        equipment="Assembly Line 3",
        workflow="Standard Production",
        shift="Day Shift",
        safety_level=2
    )
    adapter.set_industry_context(context)
    
    # Get adapted dashboard layout
    layout = adapter.get_adapted_dashboard_layout()
    print(f"Adapted dashboard layout: {layout}")
    
    # Translate terms
    print(f"Generic term 'machine' translated to: {adapter.translate_term('machine')}")
    print(f"Generic term 'quality_control' translated to: {adapter.translate_term('quality_control')}")
    
    # Get metric thresholds
    thresholds = adapter.get_adapted_metric_thresholds()
    print(f"Adapted metric thresholds: {thresholds}")
    
    # Clean up
    adapter.stop()
