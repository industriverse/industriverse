"""
Agent Capsule Factory for the Industriverse Application Layer.

This module provides the Agent Capsule Factory functionality,
enabling dynamic creation and management of agent capsules with protocol-native interfaces.
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Week 18-19 Day 2: Import CapsuleSource for coordinator integration
try:
    from ..overseer_system.capsule_lifecycle import CapsuleSource
except ImportError:
    # Fallback if overseer system not available
    class CapsuleSource:
        APPLICATION_LAYER = "application_layer"

class AgentCapsuleFactory:
    """
    Agent Capsule Factory for the Industriverse platform.
    """
    
    def __init__(self, agent_core, lifecycle_coordinator=None):
        """
        Initialize the Agent Capsule Factory.

        Args:
            agent_core: Reference to the agent core
            lifecycle_coordinator: Optional CapsuleLifecycleCoordinator for unified lifecycle management
        """
        self.agent_core = agent_core
        self.capsule_templates = {}
        self.capsule_instances = {}
        self.capsule_registry = {}
        self.lifecycle_coordinator = lifecycle_coordinator  # NEW: Week 18-19 Day 2

        # Register with agent core
        self.agent_core.register_component("agent_capsule_factory", self)

        # Register with lifecycle coordinator if available (Week 18-19 integration)
        if self.lifecycle_coordinator:
            self.lifecycle_coordinator.register_app_factory(self)
            logger.info("Agent Capsule Factory registered with Capsule Lifecycle Coordinator")

        logger.info("Agent Capsule Factory initialized")
    
    def register_capsule_template(self, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new capsule template.
        
        Args:
            template_config: Template configuration
            
        Returns:
            Registration result
        """
        # Validate template configuration
        required_fields = ["template_id", "name", "description", "capabilities"]
        for field in required_fields:
            if field not in template_config:
                return {"error": f"Missing required field: {field}"}
        
        # Generate template ID if not provided
        template_id = template_config.get("template_id", f"template-{str(uuid.uuid4())}")
        
        # Add metadata
        template_config["registered_at"] = time.time()
        
        # Store template
        self.capsule_templates[template_id] = template_config
        
        # Log registration
        logger.info(f"Registered capsule template: {template_id}")
        
        return {
            "status": "success",
            "template_id": template_id
        }
    
    def create_capsule_instance(self, template_id: str, instance_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new capsule instance from a template.
        
        Args:
            template_id: Template ID
            instance_config: Instance configuration
            
        Returns:
            Creation result
        """
        # Check if template exists
        if template_id not in self.capsule_templates:
            return {"error": f"Template not found: {template_id}"}
        
        # Get template
        template = self.capsule_templates[template_id]
        
        # Generate instance ID
        instance_id = f"capsule-{str(uuid.uuid4())}"
        
        # Create instance
        instance = {
            "instance_id": instance_id,
            "template_id": template_id,
            "name": instance_config.get("name", template["name"]),
            "description": instance_config.get("description", template["description"]),
            "capabilities": template["capabilities"].copy(),
            "status": "created",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Add instance-specific configuration
        for key, value in instance_config.items():
            if key not in ["instance_id", "template_id", "created_at", "updated_at"]:
                instance[key] = value
        
        # Store instance
        self.capsule_instances[instance_id] = instance
        
        # Register instance
        self._register_capsule_instance(instance_id, instance)
        
        # Log creation
        logger.info(f"Created capsule instance: {instance_id} from template: {template_id}")
        
        # Emit MCP event for capsule creation
        self.agent_core.emit_mcp_event("application/capsule_lifecycle", {
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

    async def create_capsule_instance_with_coordinator(
        self,
        template_id: str,
        instance_config: Dict[str, Any],
        deployment_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create capsule instance using the full lifecycle coordinator.

        This method provides complete capsule lifecycle management including:
        - Governance validation
        - Infrastructure provisioning
        - Unified registry registration
        - Evolution tracking

        Args:
            template_id: Template ID
            instance_config: Instance configuration
            deployment_context: Deployment context for infrastructure layer

        Returns:
            Full lifecycle creation result

        Week 18-19 Day 2: New method for coordinator-based creation
        """
        if not self.lifecycle_coordinator:
            # Fallback to direct creation if no coordinator
            logger.warning("No lifecycle coordinator available - falling back to direct creation")
            return self.create_capsule_instance(template_id, instance_config)

        try:
            logger.info(f"Creating capsule instance with full lifecycle: template={template_id}")

            # Use lifecycle coordinator for full lifecycle management
            result = await self.lifecycle_coordinator.create_capsule_full_lifecycle(
                template_id=template_id,
                instance_config=instance_config,
                deployment_context=deployment_context or {},
                source=CapsuleSource.APPLICATION_LAYER
            )

            if result.get("status") == "success":
                # Store local copy for backward compatibility
                app_instance = result.get("application_instance", {})
                if app_instance and "instance_id" in app_instance:
                    self.capsule_instances[app_instance["instance_id"]] = app_instance.get("instance", {})

                logger.info(f"Capsule created with full lifecycle: {result.get('capsule_id')}")

            return result

        except Exception as e:
            logger.error(f"Coordinator-based creation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _register_capsule_instance(self, instance_id: str, instance: Dict[str, Any]):
        """
        Register a capsule instance in the registry.
        
        Args:
            instance_id: Instance ID
            instance: Instance data
        """
        # Create registry entry
        registry_entry = {
            "instance_id": instance_id,
            "template_id": instance["template_id"],
            "name": instance["name"],
            "description": instance["description"],
            "status": instance["status"],
            "capabilities": [cap["name"] for cap in instance["capabilities"]],
            "registered_at": time.time()
        }
        
        # Store in registry
        self.capsule_registry[instance_id] = registry_entry
        
        logger.info(f"Registered capsule instance in registry: {instance_id}")
    
    def get_capsule_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a capsule instance by ID.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Instance data or None if not found
        """
        return self.capsule_instances.get(instance_id)
    
    def update_capsule_instance(self, instance_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a capsule instance.
        
        Args:
            instance_id: Instance ID
            update_data: Update data
            
        Returns:
            Update result
        """
        # Check if instance exists
        if instance_id not in self.capsule_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Get instance
        instance = self.capsule_instances[instance_id]
        
        # Update instance
        for key, value in update_data.items():
            if key not in ["instance_id", "template_id", "created_at"]:
                instance[key] = value
        
        # Update timestamp
        instance["updated_at"] = time.time()
        
        # Update registry
        self._update_registry_entry(instance_id, instance)
        
        # Log update
        logger.info(f"Updated capsule instance: {instance_id}")
        
        # Emit MCP event for capsule update
        self.agent_core.emit_mcp_event("application/capsule_lifecycle", {
            "action": "update_instance",
            "instance_id": instance_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "instance": instance
        }
    
    def _update_registry_entry(self, instance_id: str, instance: Dict[str, Any]):
        """
        Update a registry entry for a capsule instance.
        
        Args:
            instance_id: Instance ID
            instance: Instance data
        """
        # Check if registry entry exists
        if instance_id not in self.capsule_registry:
            return
        
        # Get registry entry
        registry_entry = self.capsule_registry[instance_id]
        
        # Update registry entry
        registry_entry["name"] = instance["name"]
        registry_entry["description"] = instance["description"]
        registry_entry["status"] = instance["status"]
        registry_entry["capabilities"] = [cap["name"] for cap in instance["capabilities"]]
        
        logger.info(f"Updated registry entry for capsule instance: {instance_id}")
    
    def delete_capsule_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Delete a capsule instance.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Deletion result
        """
        # Check if instance exists
        if instance_id not in self.capsule_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Get instance
        instance = self.capsule_instances[instance_id]
        
        # Delete instance
        del self.capsule_instances[instance_id]
        
        # Delete from registry
        if instance_id in self.capsule_registry:
            del self.capsule_registry[instance_id]
        
        # Log deletion
        logger.info(f"Deleted capsule instance: {instance_id}")
        
        # Emit MCP event for capsule deletion
        self.agent_core.emit_mcp_event("application/capsule_lifecycle", {
            "action": "delete_instance",
            "instance_id": instance_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id
        }
    
    def get_capsule_templates(self) -> List[Dict[str, Any]]:
        """
        Get all capsule templates.
        
        Returns:
            List of templates
        """
        return list(self.capsule_templates.values())
    
    def get_capsule_instances(self) -> List[Dict[str, Any]]:
        """
        Get all capsule instances.
        
        Returns:
            List of instances
        """
        return list(self.capsule_instances.values())
    
    def get_capsule_registry(self) -> List[Dict[str, Any]]:
        """
        Get the capsule registry.
        
        Returns:
            Capsule registry
        """
        return list(self.capsule_registry.values())
    
    def search_capsule_registry(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search the capsule registry.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        results = []
        
        # Extract query parameters
        name = query.get("name")
        description = query.get("description")
        status = query.get("status")
        capabilities = query.get("capabilities", [])
        
        # Search registry
        for entry in self.capsule_registry.values():
            # Check name
            if name and name.lower() not in entry["name"].lower():
                continue
            
            # Check description
            if description and description.lower() not in entry["description"].lower():
                continue
            
            # Check status
            if status and entry["status"] != status:
                continue
            
            # Check capabilities
            if capabilities:
                has_all_capabilities = True
                for capability in capabilities:
                    if capability not in entry["capabilities"]:
                        has_all_capabilities = False
                        break
                
                if not has_all_capabilities:
                    continue
            
            # Add to results
            results.append(entry)
        
        return results
    
    def initialize_default_templates(self) -> Dict[str, Any]:
        """
        Initialize default capsule templates.
        
        Returns:
            Initialization result
        """
        logger.info("Initializing default capsule templates")
        
        # Define default templates
        default_templates = [
            {
                "template_id": "template-dashboard",
                "name": "Dashboard Capsule",
                "description": "Capsule for dashboard functionality",
                "capabilities": [
                    {
                        "name": "data_visualization",
                        "description": "Visualize data in various formats"
                    },
                    {
                        "name": "data_filtering",
                        "description": "Filter data based on criteria"
                    },
                    {
                        "name": "dashboard_customization",
                        "description": "Customize dashboard layout and components"
                    }
                ]
            },
            {
                "template_id": "template-digital-twin",
                "name": "Digital Twin Capsule",
                "description": "Capsule for digital twin functionality",
                "capabilities": [
                    {
                        "name": "twin_visualization",
                        "description": "Visualize digital twin"
                    },
                    {
                        "name": "twin_monitoring",
                        "description": "Monitor digital twin status"
                    },
                    {
                        "name": "twin_control",
                        "description": "Control digital twin"
                    }
                ]
            },
            {
                "template_id": "template-workflow",
                "name": "Workflow Capsule",
                "description": "Capsule for workflow functionality",
                "capabilities": [
                    {
                        "name": "workflow_visualization",
                        "description": "Visualize workflow"
                    },
                    {
                        "name": "workflow_execution",
                        "description": "Execute workflow"
                    },
                    {
                        "name": "workflow_monitoring",
                        "description": "Monitor workflow status"
                    }
                ]
            },
            {
                "template_id": "template-analytics",
                "name": "Analytics Capsule",
                "description": "Capsule for analytics functionality",
                "capabilities": [
                    {
                        "name": "data_analysis",
                        "description": "Analyze data"
                    },
                    {
                        "name": "predictive_analytics",
                        "description": "Perform predictive analytics"
                    },
                    {
                        "name": "anomaly_detection",
                        "description": "Detect anomalies in data"
                    }
                ]
            }
        ]
        
        # Register templates
        registered_templates = []
        for template_config in default_templates:
            result = self.register_capsule_template(template_config)
            if "error" not in result:
                registered_templates.append(result["template_id"])
        
        return {
            "status": "success",
            "registered_templates": registered_templates,
            "count": len(registered_templates)
        }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get component information.
        
        Returns:
            Component information
        """
        return {
            "id": "agent_capsule_factory",
            "type": "AgentCapsuleFactory",
            "name": "Agent Capsule Factory",
            "status": "operational",
            "templates": len(self.capsule_templates),
            "instances": len(self.capsule_instances),
            "registry_entries": len(self.capsule_registry)
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
        if action_id == "register_capsule_template":
            return self.register_capsule_template(data)
        elif action_id == "create_capsule_instance":
            return self.create_capsule_instance(
                data.get("template_id", ""),
                data.get("instance_config", {})
            )
        elif action_id == "get_capsule_instance":
            instance = self.get_capsule_instance(data.get("instance_id", ""))
            return {"instance": instance} if instance else {"error": "Instance not found"}
        elif action_id == "update_capsule_instance":
            return self.update_capsule_instance(
                data.get("instance_id", ""),
                data.get("update_data", {})
            )
        elif action_id == "delete_capsule_instance":
            return self.delete_capsule_instance(data.get("instance_id", ""))
        elif action_id == "get_capsule_templates":
            return {"templates": self.get_capsule_templates()}
        elif action_id == "get_capsule_instances":
            return {"instances": self.get_capsule_instances()}
        elif action_id == "get_capsule_registry":
            return {"registry": self.get_capsule_registry()}
        elif action_id == "search_capsule_registry":
            return {"results": self.search_capsule_registry(data.get("query", {}))}
        elif action_id == "initialize_default_templates":
            return self.initialize_default_templates()
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
            "templates": len(self.capsule_templates),
            "instances": len(self.capsule_instances),
            "registry_entries": len(self.capsule_registry)
        }
