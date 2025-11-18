"""
Capsule Factory

This module is responsible for creating capsules from blueprints and deployment manifests.
It handles the instantiation process, applying configuration from manifests to blueprints
to create fully functional capsule instances ready for deployment.
"""

import logging
import uuid
import copy
import json
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class CapsuleFactory:
    """
    Factory for creating capsules from blueprints and manifests.
    """

    def __init__(self, lifecycle_coordinator=None):
        """
        Initialize the Capsule Factory.

        Args:
            lifecycle_coordinator: Optional CapsuleLifecycleCoordinator for unified lifecycle management

        Week 18-19 Day 3: Added coordinator integration
        """
        self.lifecycle_coordinator = lifecycle_coordinator

        # Register with lifecycle coordinator if available
        if self.lifecycle_coordinator:
            self.lifecycle_coordinator.register_deploy_factory(self)
            logger.info("Capsule Factory registered with Capsule Lifecycle Coordinator")

        logger.info("Capsule Factory initialized")
    
    def create_capsule(self,
                      blueprint: Dict[str, Any],
                      manifest: Dict[str, Any],
                      context: Dict[str, Any],
                      governance_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a capsule from a blueprint and manifest.

        Args:
            blueprint: Blueprint defining the capsule structure
            manifest: Deployment manifest with configuration
            context: Deployment context
            governance_metadata: Optional governance metadata from coordinator (Week 18-19 Day 3)

        Returns:
            Instantiated capsule as a dictionary
        """
        logger.info(f"Creating capsule from blueprint: {blueprint.get('name', 'unnamed')}")

        # Week 18-19 Day 3: Log if governance metadata provided
        if governance_metadata:
            logger.info(f"Applying governance metadata from coordinator: {governance_metadata.keys()}")
        
        # Generate a unique ID for the capsule
        capsule_id = str(uuid.uuid4())
        
        # Start with a deep copy of the blueprint
        capsule = copy.deepcopy(blueprint)
        
        # Apply manifest configuration
        self._apply_manifest_configuration(capsule, manifest)
        
        # Apply context-specific adaptations
        self._apply_context_adaptations(capsule, context)
        
        # Set capsule metadata
        capsule["metadata"] = {
            "id": capsule_id,
            "created_at": self._get_timestamp(),
            "blueprint_type": blueprint.get("type"),
            "blueprint_version": blueprint.get("version"),
            "manifest_id": manifest.get("id"),
            "lineage": {
                "parent_blueprint": blueprint.get("metadata", {}).get("id"),
                "parent_version": blueprint.get("version"),
                "generation_context": self._extract_generation_context(context)
            }
        }
        
        # Initialize capsule state
        capsule["state"] = {
            "status": "created",
            "health": 100,
            "last_updated": self._get_timestamp()
        }
        
        # Initialize runtime configuration
        capsule["runtime"] = {
            "environment": context.get("environment", {}).get("type", "default"),
            "resources": self._calculate_resources(blueprint, manifest, context),
            "scaling": manifest.get("scaling", blueprint.get("scaling", {"min": 1, "max": 1})),
            "networking": self._configure_networking(blueprint, manifest, context)
        }
        
        # Initialize security configuration
        capsule["security"] = {
            "trust_zone": context.get("trust_zone", "default"),
            "trust_score": 100,  # Initial trust score
            "crypto_zone": context.get("crypto_zone", "default"),
            "permissions": self._merge_permissions(blueprint.get("permissions", []), manifest.get("permissions", [])),
            "compliance": {
                "frameworks": context.get("compliance_frameworks", []),
                "status": "pending_validation"
            }
        }

        # Week 18-19 Day 3: Apply governance metadata from coordinator if provided
        if governance_metadata:
            capsule["governance"] = governance_metadata
            # Update compliance status based on governance validation
            if "validated_at" in governance_metadata:
                capsule["security"]["compliance"]["status"] = "validated"
                capsule["security"]["compliance"]["validated_at"] = governance_metadata["validated_at"]
            # Apply trust zone from governance if provided
            if "trust_zone" in governance_metadata:
                capsule["security"]["trust_zone"] = governance_metadata["trust_zone"]
        
        # Initialize protocol configuration
        capsule["protocols"] = {
            "mcp": self._configure_mcp(blueprint, manifest, context),
            "a2a": self._configure_a2a(blueprint, manifest, context)
        }
        
        # Initialize integration points
        capsule["integration"] = {
            "endpoints": self._configure_endpoints(blueprint, manifest, context),
            "dependencies": self._resolve_dependencies(blueprint, manifest, context),
            "events": {
                "publishers": blueprint.get("events", {}).get("publishers", []),
                "subscribers": blueprint.get("events", {}).get("subscribers", [])
            }
        }
        
        logger.info(f"Capsule created with ID: {capsule_id}")
        return capsule
    
    def _apply_manifest_configuration(self, capsule: Dict[str, Any], manifest: Dict[str, Any]):
        """
        Apply configuration from manifest to capsule.
        
        Args:
            capsule: Capsule being created
            manifest: Deployment manifest with configuration
        """
        # Apply name and description if provided
        if "name" in manifest:
            capsule["name"] = manifest["name"]
        
        if "description" in manifest:
            capsule["description"] = manifest["description"]
        
        # Apply configuration overrides
        if "configuration" in manifest:
            self._deep_merge(capsule.get("configuration", {}), manifest["configuration"])
            capsule["configuration"] = capsule.get("configuration", {})
        
        # Apply component overrides
        if "components" in manifest:
            for component_name, component_config in manifest["components"].items():
                if component_name in capsule.get("components", {}):
                    self._deep_merge(capsule["components"][component_name], component_config)
                else:
                    logger.warning(f"Component {component_name} specified in manifest but not in blueprint")
    
    def _apply_context_adaptations(self, capsule: Dict[str, Any], context: Dict[str, Any]):
        """
        Apply context-specific adaptations to capsule.
        
        Args:
            capsule: Capsule being created
            context: Deployment context
        """
        # Apply environment-specific adaptations
        env_type = context.get("environment", {}).get("type")
        if env_type:
            if "adaptations" in capsule and env_type in capsule["adaptations"]:
                self._deep_merge(capsule, capsule["adaptations"][env_type])
        
        # Apply region-specific adaptations
        region = context.get("region")
        if region:
            if "regional_adaptations" in capsule and region in capsule["regional_adaptations"]:
                self._deep_merge(capsule, capsule["regional_adaptations"][region])
        
        # Apply industry-specific adaptations
        industry = context.get("industry")
        if industry:
            if "industry_adaptations" in capsule and industry in capsule["industry_adaptations"]:
                self._deep_merge(capsule, capsule["industry_adaptations"][industry])
    
    def _calculate_resources(self, 
                            blueprint: Dict[str, Any], 
                            manifest: Dict[str, Any], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate resource requirements for the capsule.
        
        Args:
            blueprint: Blueprint defining the capsule structure
            manifest: Deployment manifest with configuration
            context: Deployment context
            
        Returns:
            Resource configuration
        """
        # Start with blueprint resources
        resources = copy.deepcopy(blueprint.get("resources", {
            "cpu": "100m",
            "memory": "128Mi",
            "storage": "1Gi"
        }))
        
        # Apply manifest overrides
        manifest_resources = manifest.get("resources", {})
        for key, value in manifest_resources.items():
            resources[key] = value
        
        # Apply environment-specific adjustments
        env_type = context.get("environment", {}).get("type")
        if env_type == "edge":
            # Reduce resource requirements for edge deployments
            resources["cpu"] = self._adjust_resource_for_edge(resources["cpu"], 0.7)
            resources["memory"] = self._adjust_resource_for_edge(resources["memory"], 0.7)
            resources["storage"] = self._adjust_resource_for_edge(resources["storage"], 0.5)
        
        return resources
    
    def _adjust_resource_for_edge(self, resource_value: str, factor: float) -> str:
        """
        Adjust resource value for edge deployment.
        
        Args:
            resource_value: Original resource value
            factor: Adjustment factor
            
        Returns:
            Adjusted resource value
        """
        # Parse resource value
        if resource_value.endswith('m'):
            value = float(resource_value[:-1]) * factor
            return f"{int(value)}m"
        elif resource_value.endswith('Mi'):
            value = float(resource_value[:-2]) * factor
            return f"{int(value)}Mi"
        elif resource_value.endswith('Gi'):
            value = float(resource_value[:-2]) * factor
            return f"{int(value)}Gi"
        else:
            try:
                value = float(resource_value) * factor
                return str(int(value))
            except ValueError:
                return resource_value
    
    def _configure_networking(self, 
                            blueprint: Dict[str, Any], 
                            manifest: Dict[str, Any], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure networking for the capsule.
        
        Args:
            blueprint: Blueprint defining the capsule structure
            manifest: Deployment manifest with configuration
            context: Deployment context
            
        Returns:
            Networking configuration
        """
        # Start with blueprint networking
        networking = copy.deepcopy(blueprint.get("networking", {
            "ports": [],
            "ingress": False,
            "egress": True,
            "dns": None
        }))
        
        # Apply manifest overrides
        manifest_networking = manifest.get("networking", {})
        for key, value in manifest_networking.items():
            networking[key] = value
        
        # Apply context-specific configurations
        if context.get("environment", {}).get("type") == "edge":
            networking["mesh_enabled"] = True
            networking["offline_mode_supported"] = True
        
        return networking
    
    def _merge_permissions(self, 
                          blueprint_permissions: List[str], 
                          manifest_permissions: List[str]) -> List[str]:
        """
        Merge permissions from blueprint and manifest.
        
        Args:
            blueprint_permissions: Permissions from blueprint
            manifest_permissions: Permissions from manifest
            
        Returns:
            Merged permissions list
        """
        # Combine permissions and remove duplicates
        return list(set(blueprint_permissions + manifest_permissions))
    
    def _configure_mcp(self, 
                      blueprint: Dict[str, Any], 
                      manifest: Dict[str, Any], 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure MCP for the capsule.
        
        Args:
            blueprint: Blueprint defining the capsule structure
            manifest: Deployment manifest with configuration
            context: Deployment context
            
        Returns:
            MCP configuration
        """
        # Start with blueprint MCP configuration
        mcp_config = copy.deepcopy(blueprint.get("protocols", {}).get("mcp", {
            "enabled": True,
            "version": "1.0",
            "endpoints": []
        }))
        
        # Apply manifest overrides
        manifest_mcp = manifest.get("protocols", {}).get("mcp", {})
        for key, value in manifest_mcp.items():
            mcp_config[key] = value
        
        # Add industry-specific metadata if available
        industry = context.get("industry")
        if industry:
            mcp_config["metadata"] = mcp_config.get("metadata", {})
            mcp_config["metadata"]["industry"] = industry
        
        return mcp_config
    
    def _configure_a2a(self, 
                      blueprint: Dict[str, Any], 
                      manifest: Dict[str, Any], 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure A2A for the capsule.
        
        Args:
            blueprint: Blueprint defining the capsule structure
            manifest: Deployment manifest with configuration
            context: Deployment context
            
        Returns:
            A2A configuration
        """
        # Start with blueprint A2A configuration
        a2a_config = copy.deepcopy(blueprint.get("protocols", {}).get("a2a", {
            "enabled": True,
            "version": "1.0",
            "agent_card": {}
        }))
        
        # Apply manifest overrides
        manifest_a2a = manifest.get("protocols", {}).get("a2a", {})
        for key, value in manifest_a2a.items():
            a2a_config[key] = value
        
        # Configure agent card with enhanced fields
        agent_card = a2a_config.get("agent_card", {})
        agent_card["name"] = capsule["name"]
        agent_card["description"] = capsule.get("description", "")
        
        # Add industry-specific metadata
        industry = context.get("industry")
        if industry:
            agent_card["industryTags"] = agent_card.get("industryTags", [])
            if industry not in agent_card["industryTags"]:
                agent_card["industryTags"].append(industry)
        
        # Add priority field
        agent_card["priority"] = manifest.get("priority", "normal")
        
        # Add workflow templates if available
        workflow_templates = blueprint.get("workflow_templates", [])
        if workflow_templates:
            agent_card["capabilities"] = agent_card.get("capabilities", {})
            agent_card["capabilities"]["workflowTemplates"] = workflow_templates
        
        a2a_config["agent_card"] = agent_card
        
        return a2a_config
    
    def _configure_endpoints(self, 
                           blueprint: Dict[str, Any], 
                           manifest: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure integration endpoints for the capsule.
        
        Args:
            blueprint: Blueprint defining the capsule structure
            manifest: Deployment manifest with configuration
            context: Deployment context
            
        Returns:
            Endpoint configuration
        """
        # Start with blueprint endpoints
        endpoints = copy.deepcopy(blueprint.get("integration", {}).get("endpoints", {}))
        
        # Apply manifest overrides
        manifest_endpoints = manifest.get("integration", {}).get("endpoints", {})
        for key, value in manifest_endpoints.items():
            endpoints[key] = value
        
        return endpoints
    
    def _resolve_dependencies(self, 
                            blueprint: Dict[str, Any], 
                            manifest: Dict[str, Any], 
                            context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Resolve dependencies for the capsule.
        
        Args:
            blueprint: Blueprint defining the capsule structure
            manifest: Deployment manifest with configuration
            context: Deployment context
            
        Returns:
            Resolved dependencies list
        """
        # Start with blueprint dependencies
        dependencies = copy.deepcopy(blueprint.get("integration", {}).get("dependencies", []))
        
        # Apply manifest overrides or additions
        manifest_dependencies = manifest.get("integration", {}).get("dependencies", [])
        
        # Merge dependencies by name
        dependency_map = {dep["name"]: dep for dep in dependencies}
        
        for dep in manifest_dependencies:
            name = dep["name"]
            if name in dependency_map:
                # Update existing dependency
                self._deep_merge(dependency_map[name], dep)
            else:
                # Add new dependency
                dependency_map[name] = dep
        
        return list(dependency_map.values())
    
    def _extract_generation_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant context information for capsule lineage.
        
        Args:
            context: Deployment context
            
        Returns:
            Extracted context for lineage tracking
        """
        return {
            "environment": context.get("environment", {}).get("type", "default"),
            "region": context.get("region", "default"),
            "industry": context.get("industry"),
            "trust_zone": context.get("trust_zone"),
            "crypto_zone": context.get("crypto_zone"),
            "compliance_frameworks": context.get("compliance_frameworks", []),
            "timestamp": self._get_timestamp()
        }
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """
        Deep merge two dictionaries.
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
