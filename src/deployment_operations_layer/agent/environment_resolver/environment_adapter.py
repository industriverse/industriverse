"""
Environment Adapter

This module adapts deployments for specific environments. It handles the necessary
modifications and configurations to ensure that deployments are optimized for their
target environments.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class EnvironmentAdapter:
    """
    Adapter for environment-specific deployment configurations.
    """
    
    def __init__(self, adaptation_templates_path: Optional[str] = None):
        """
        Initialize the Environment Adapter.
        
        Args:
            adaptation_templates_path: Path to adaptation templates file
        """
        self.adaptation_templates_path = adaptation_templates_path or os.environ.get(
            "ADAPTATION_TEMPLATES_PATH", "/var/lib/industriverse/environments/adaptation_templates.json"
        )
        self.adaptation_templates = self._load_adaptation_templates()
        logger.info("Environment Adapter initialized")
    
    def adapt_for_environment(self, 
                            deployment_manifest: Dict[str, Any], 
                            environment_type: str,
                            capabilities: Dict[str, Any],
                            resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt a deployment for a specific environment.
        
        Args:
            deployment_manifest: Deployment manifest
            environment_type: Type of environment
            capabilities: Environment capabilities
            resources: Resource requirements
            
        Returns:
            Dict containing adaptations
        """
        logger.info(f"Adapting deployment {deployment_manifest.get('name', 'unnamed')} for environment: {environment_type}")
        
        try:
            # Get adaptation template for this environment type
            template = self._get_adaptation_template(environment_type)
            
            # Apply general adaptations
            general_adaptations = self._apply_general_adaptations(
                deployment_manifest, environment_type, template, capabilities, resources
            )
            
            # Apply component-specific adaptations
            component_adaptations = self._apply_component_adaptations(
                deployment_manifest, environment_type, template, capabilities, resources
            )
            
            # Apply resource adaptations
            resource_adaptations = self._apply_resource_adaptations(
                deployment_manifest, environment_type, template, capabilities, resources
            )
            
            # Apply networking adaptations
            networking_adaptations = self._apply_networking_adaptations(
                deployment_manifest, environment_type, template, capabilities, resources
            )
            
            # Apply security adaptations
            security_adaptations = self._apply_security_adaptations(
                deployment_manifest, environment_type, template, capabilities, resources
            )
            
            # Prepare result
            adaptations = {
                "general": general_adaptations,
                "components": component_adaptations,
                "resources": resource_adaptations,
                "networking": networking_adaptations,
                "security": security_adaptations,
                "timestamp": self._get_timestamp()
            }
            
            return {
                "success": True,
                "adaptations": adaptations
            }
            
        except Exception as e:
            logger.exception(f"Error adapting for environment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_environment_specific_manifests(self, 
                                             deployment_manifest: Dict[str, Any], 
                                             adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate environment-specific manifests based on adaptations.
        
        Args:
            deployment_manifest: Original deployment manifest
            adaptations: Adaptations to apply
            
        Returns:
            Dict containing generated manifests
        """
        logger.info(f"Generating environment-specific manifests for deployment: {deployment_manifest.get('name', 'unnamed')}")
        
        try:
            # Create a deep copy of the original manifest
            adapted_manifest = self._deep_copy(deployment_manifest)
            
            # Apply general adaptations
            if "general" in adaptations:
                for key, value in adaptations["general"].items():
                    if key in adapted_manifest:
                        if isinstance(adapted_manifest[key], dict) and isinstance(value, dict):
                            self._deep_merge(adapted_manifest[key], value)
                        else:
                            adapted_manifest[key] = value
                    else:
                        adapted_manifest[key] = value
            
            # Apply component adaptations
            if "components" in adaptations:
                if "components" not in adapted_manifest:
                    adapted_manifest["components"] = {}
                
                for component_name, component_adaptations in adaptations["components"].items():
                    if component_name in adapted_manifest["components"]:
                        self._deep_merge(adapted_manifest["components"][component_name], component_adaptations)
                    else:
                        adapted_manifest["components"][component_name] = component_adaptations
            
            # Apply resource adaptations
            if "resources" in adaptations:
                if "resources" not in adapted_manifest:
                    adapted_manifest["resources"] = {}
                
                self._deep_merge(adapted_manifest["resources"], adaptations["resources"])
            
            # Apply networking adaptations
            if "networking" in adaptations:
                if "networking" not in adapted_manifest:
                    adapted_manifest["networking"] = {}
                
                self._deep_merge(adapted_manifest["networking"], adaptations["networking"])
            
            # Apply security adaptations
            if "security" in adaptations:
                if "security" not in adapted_manifest:
                    adapted_manifest["security"] = {}
                
                self._deep_merge(adapted_manifest["security"], adaptations["security"])
            
            # Add adaptation metadata
            if "metadata" not in adapted_manifest:
                adapted_manifest["metadata"] = {}
            
            adapted_manifest["metadata"]["adaptations"] = {
                "timestamp": self._get_timestamp(),
                "adapted_for": adaptations.get("general", {}).get("environment_type", "unknown")
            }
            
            return {
                "success": True,
                "adapted_manifest": adapted_manifest
            }
            
        except Exception as e:
            logger.exception(f"Error generating environment-specific manifests: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_adaptation_templates(self) -> Dict[str, Any]:
        """
        Load adaptation templates from file.
        
        Returns:
            Dict containing adaptation templates
        """
        try:
            if os.path.exists(self.adaptation_templates_path):
                with open(self.adaptation_templates_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Adaptation templates file not found: {self.adaptation_templates_path}")
                return self._get_default_adaptation_templates()
                
        except Exception as e:
            logger.exception(f"Error loading adaptation templates: {str(e)}")
            return self._get_default_adaptation_templates()
    
    def _get_default_adaptation_templates(self) -> Dict[str, Any]:
        """
        Get default adaptation templates.
        
        Returns:
            Dict containing default adaptation templates
        """
        return {
            "cloud": {
                "general": {
                    "environment_type": "cloud",
                    "scaling_strategy": "auto",
                    "high_availability": True,
                    "monitoring": {
                        "enabled": True,
                        "metrics": ["cpu", "memory", "network", "storage"]
                    }
                },
                "components": {
                    "default": {
                        "replicas": 2,
                        "auto_scaling": {
                            "enabled": True,
                            "min_replicas": 2,
                            "max_replicas": 10,
                            "target_cpu_utilization": 70
                        }
                    },
                    "database": {
                        "use_managed_service": True,
                        "backup": {
                            "enabled": True,
                            "schedule": "0 0 * * *"
                        }
                    },
                    "frontend": {
                        "cdn_enabled": True
                    }
                },
                "resources": {
                    "cpu_request_strategy": "standard",
                    "memory_request_strategy": "standard",
                    "storage_class": "standard"
                },
                "networking": {
                    "use_load_balancer": True,
                    "use_service_mesh": False,
                    "ingress": {
                        "enabled": True,
                        "annotations": {
                            "kubernetes.io/ingress.class": "nginx"
                        }
                    }
                },
                "security": {
                    "network_policies": {
                        "enabled": True
                    },
                    "secrets_management": {
                        "use_vault": False,
                        "use_cloud_secrets": True
                    }
                }
            },
            "edge": {
                "general": {
                    "environment_type": "edge",
                    "scaling_strategy": "fixed",
                    "high_availability": False,
                    "monitoring": {
                        "enabled": True,
                        "metrics": ["cpu", "memory", "storage"],
                        "local_storage": True,
                        "central_forwarding": {
                            "enabled": True,
                            "interval": "5m"
                        }
                    },
                    "offline_operation": {
                        "enabled": True,
                        "sync_strategy": "periodic"
                    }
                },
                "components": {
                    "default": {
                        "replicas": 1,
                        "auto_scaling": {
                            "enabled": False
                        },
                        "resource_constraints": {
                            "enabled": True,
                            "cpu_limit_factor": 0.8,
                            "memory_limit_factor": 0.8
                        }
                    },
                    "database": {
                        "use_managed_service": False,
                        "embedded": True,
                        "backup": {
                            "enabled": True,
                            "schedule": "0 0 * * *",
                            "local_retention": 3
                        }
                    },
                    "frontend": {
                        "cdn_enabled": False,
                        "optimize_for_low_bandwidth": True
                    }
                },
                "resources": {
                    "cpu_request_strategy": "conservative",
                    "memory_request_strategy": "conservative",
                    "storage_class": "local"
                },
                "networking": {
                    "use_load_balancer": False,
                    "use_service_mesh": True,
                    "mesh_networking": {
                        "enabled": True,
                        "discovery": "mdns"
                    },
                    "ingress": {
                        "enabled": False
                    }
                },
                "security": {
                    "network_policies": {
                        "enabled": True,
                        "default_deny": True
                    },
                    "secrets_management": {
                        "use_vault": False,
                        "use_local_secrets": True,
                        "encryption": {
                            "enabled": True
                        }
                    }
                }
            },
            "on-premise": {
                "general": {
                    "environment_type": "on-premise",
                    "scaling_strategy": "manual",
                    "high_availability": True,
                    "monitoring": {
                        "enabled": True,
                        "metrics": ["cpu", "memory", "network", "storage"],
                        "use_prometheus": True
                    }
                },
                "components": {
                    "default": {
                        "replicas": 2,
                        "auto_scaling": {
                            "enabled": False
                        }
                    },
                    "database": {
                        "use_managed_service": False,
                        "backup": {
                            "enabled": True,
                            "schedule": "0 0 * * *"
                        }
                    },
                    "frontend": {
                        "cdn_enabled": False
                    }
                },
                "resources": {
                    "cpu_request_strategy": "generous",
                    "memory_request_strategy": "generous",
                    "storage_class": "enterprise"
                },
                "networking": {
                    "use_load_balancer": True,
                    "use_service_mesh": False,
                    "ingress": {
                        "enabled": True,
                        "annotations": {
                            "kubernetes.io/ingress.class": "nginx"
                        }
                    }
                },
                "security": {
                    "network_policies": {
                        "enabled": True
                    },
                    "secrets_management": {
                        "use_vault": True,
                        "use_cloud_secrets": False
                    }
                }
            },
            "hybrid": {
                "general": {
                    "environment_type": "hybrid",
                    "scaling_strategy": "auto",
                    "high_availability": True,
                    "monitoring": {
                        "enabled": True,
                        "metrics": ["cpu", "memory", "network", "storage"],
                        "use_prometheus": True,
                        "cloud_integration": True
                    },
                    "multi_cluster": {
                        "enabled": True,
                        "federation": True
                    }
                },
                "components": {
                    "default": {
                        "replicas": 2,
                        "auto_scaling": {
                            "enabled": True,
                            "min_replicas": 2,
                            "max_replicas": 10,
                            "target_cpu_utilization": 70
                        },
                        "placement": {
                            "strategy": "spread",
                            "zones": ["cloud", "on-premise"]
                        }
                    },
                    "database": {
                        "use_managed_service": True,
                        "backup": {
                            "enabled": True,
                            "schedule": "0 0 * * *",
                            "multi_location": True
                        },
                        "replication": {
                            "enabled": True,
                            "strategy": "active-active"
                        }
                    },
                    "frontend": {
                        "cdn_enabled": True,
                        "multi_region": True
                    }
                },
                "resources": {
                    "cpu_request_strategy": "standard",
                    "memory_request_strategy": "standard",
                    "storage_class": "hybrid"
                },
                "networking": {
                    "use_load_balancer": True,
                    "use_service_mesh": True,
                    "multi_cluster_networking": {
                        "enabled": True,
                        "gateway": "istio"
                    },
                    "ingress": {
                        "enabled": True,
                        "global_routing": True,
                        "annotations": {
                            "kubernetes.io/ingress.class": "nginx"
                        }
                    }
                },
                "security": {
                    "network_policies": {
                        "enabled": True
                    },
                    "secrets_management": {
                        "use_vault": True,
                        "use_cloud_secrets": True,
                        "sync_strategy": "vault-to-cloud"
                    }
                }
            }
        }
    
    def _get_adaptation_template(self, environment_type: str) -> Dict[str, Any]:
        """
        Get adaptation template for an environment type.
        
        Args:
            environment_type: Type of environment
            
        Returns:
            Adaptation template
        """
        if environment_type in self.adaptation_templates:
            return self.adaptation_templates[environment_type]
        else:
            logger.warning(f"Adaptation template not found for environment type: {environment_type}")
            return {}
    
    def _apply_general_adaptations(self, 
                                 deployment_manifest: Dict[str, Any], 
                                 environment_type: str,
                                 template: Dict[str, Any],
                                 capabilities: Dict[str, Any],
                                 resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply general adaptations to a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            environment_type: Type of environment
            template: Adaptation template
            capabilities: Environment capabilities
            resources: Resource requirements
            
        Returns:
            General adaptations
        """
        # Start with template general adaptations
        general_adaptations = dict(template.get("general", {}))
        
        # Add environment-specific metadata
        general_adaptations.update({
            "environment_type": environment_type,
            "adapted_at": self._get_timestamp()
        })
        
        # Apply high availability adaptations based on capabilities
        if "high_availability" in general_adaptations:
            if not capabilities.get("supports_high_availability", False):
                general_adaptations["high_availability"] = False
        
        # Apply scaling strategy adaptations based on capabilities
        if "scaling_strategy" in general_adaptations:
            if not capabilities.get("supports_auto_scaling", False) and general_adaptations["scaling_strategy"] == "auto":
                general_adaptations["scaling_strategy"] = "manual"
        
        return general_adaptations
    
    def _apply_component_adaptations(self, 
                                   deployment_manifest: Dict[str, Any], 
                                   environment_type: str,
                                   template: Dict[str, Any],
                                   capabilities: Dict[str, Any],
                                   resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply component-specific adaptations to a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            environment_type: Type of environment
            template: Adaptation template
            capabilities: Environment capabilities
            resources: Resource requirements
            
        Returns:
            Component adaptations
        """
        component_adaptations = {}
        
        # Get components from manifest
        components = deployment_manifest.get("components", {})
        
        # Get template component adaptations
        template_components = template.get("components", {})
        
        # Apply default adaptations to all components
        default_adaptations = template_components.get("default", {})
        
        for component_name in components.keys():
            # Start with default adaptations
            component_adaptations[component_name] = dict(default_adaptations)
            
            # Apply component-specific adaptations if available
            if component_name in template_components:
                self._deep_merge(component_adaptations[component_name], template_components[component_name])
            
            # Apply environment-specific adjustments
            self._adjust_component_for_environment(
                component_adaptations[component_name], 
                component_name, 
                environment_type, 
                capabilities
            )
        
        return component_adaptations
    
    def _adjust_component_for_environment(self, 
                                        component_adaptation: Dict[str, Any], 
                                        component_name: str,
                                        environment_type: str,
                                        capabilities: Dict[str, Any]):
        """
        Adjust component adaptation for specific environment.
        
        Args:
            component_adaptation: Component adaptation to adjust
            component_name: Name of the component
            environment_type: Type of environment
            capabilities: Environment capabilities
        """
        # Adjust auto-scaling based on capabilities
        if "auto_scaling" in component_adaptation:
            if not capabilities.get("supports_auto_scaling", False):
                component_adaptation["auto_scaling"]["enabled"] = False
        
        # Adjust replicas based on high availability support
        if "replicas" in component_adaptation:
            if not capabilities.get("supports_high_availability", False) and component_adaptation["replicas"] > 1:
                component_adaptation["replicas"] = 1
        
        # Adjust database configuration for edge environments
        if component_name == "database" and environment_type == "edge":
            if "use_managed_service" in component_adaptation:
                component_adaptation["use_managed_service"] = False
            
            if "embedded" not in component_adaptation:
                component_adaptation["embedded"] = True
        
        # Adjust frontend configuration for edge environments
        if component_name == "frontend" and environment_type == "edge":
            if "cdn_enabled" in component_adaptation:
                component_adaptation["cdn_enabled"] = False
            
            if "optimize_for_low_bandwidth" not in component_adaptation:
                component_adaptation["optimize_for_low_bandwidth"] = True
    
    def _apply_resource_adaptations(self, 
                                  deployment_manifest: Dict[str, Any], 
                                  environment_type: str,
                                  template: Dict[str, Any],
                                  capabilities: Dict[str, Any],
                                  resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply resource adaptations to a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            environment_type: Type of environment
            template: Adaptation template
            capabilities: Environment capabilities
            resources: Resource requirements
            
        Returns:
            Resource adaptations
        """
        # Start with template resource adaptations
        resource_adaptations = dict(template.get("resources", {}))
        
        # Apply CPU request strategy
        cpu_strategy = resource_adaptations.get("cpu_request_strategy", "standard")
        resource_adaptations["cpu_adjustments"] = self._calculate_resource_adjustments(
            cpu_strategy, resources.get("cpu", {}), capabilities.get("max_cpu", 0)
        )
        
        # Apply memory request strategy
        memory_strategy = resource_adaptations.get("memory_request_strategy", "standard")
        resource_adaptations["memory_adjustments"] = self._calculate_resource_adjustments(
            memory_strategy, resources.get("memory", {}), capabilities.get("max_memory", 0)
        )
        
        # Apply storage class based on environment
        if environment_type == "edge":
            resource_adaptations["storage_class"] = "local"
        elif environment_type == "cloud":
            resource_adaptations["storage_class"] = "standard"
        elif environment_type == "on-premise":
            resource_adaptations["storage_class"] = "enterprise"
        elif environment_type == "hybrid":
            resource_adaptations["storage_class"] = "hybrid"
        
        return resource_adaptations
    
    def _calculate_resource_adjustments(self, 
                                      strategy: str, 
                                      resource_requirements: Dict[str, Any],
                                      max_available: float) -> Dict[str, Any]:
        """
        Calculate resource adjustments based on strategy.
        
        Args:
            strategy: Resource strategy (conservative, standard, generous)
            resource_requirements: Resource requirements
            max_available: Maximum available resource
            
        Returns:
            Resource adjustments
        """
        # Get base request and limit
        base_request = resource_requirements.get("request", 0)
        base_limit = resource_requirements.get("limit", base_request * 1.5)
        
        # Apply strategy factors
        if strategy == "conservative":
            request_factor = 0.8
            limit_factor = 1.2
        elif strategy == "generous":
            request_factor = 1.2
            limit_factor = 2.0
        else:  # standard
            request_factor = 1.0
            limit_factor = 1.5
        
        # Calculate adjusted values
        adjusted_request = base_request * request_factor
        adjusted_limit = base_request * limit_factor
        
        # Ensure values don't exceed maximum available
        if max_available > 0:
            adjusted_request = min(adjusted_request, max_available * 0.8)
            adjusted_limit = min(adjusted_limit, max_available)
        
        return {
            "original_request": base_request,
            "original_limit": base_limit,
            "adjusted_request": adjusted_request,
            "adjusted_limit": adjusted_limit,
            "strategy": strategy
        }
    
    def _apply_networking_adaptations(self, 
                                    deployment_manifest: Dict[str, Any], 
                                    environment_type: str,
                                    template: Dict[str, Any],
                                    capabilities: Dict[str, Any],
                                    resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply networking adaptations to a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            environment_type: Type of environment
            template: Adaptation template
            capabilities: Environment capabilities
            resources: Resource requirements
            
        Returns:
            Networking adaptations
        """
        # Start with template networking adaptations
        networking_adaptations = dict(template.get("networking", {}))
        
        # Adjust load balancer usage based on capabilities
        if "use_load_balancer" in networking_adaptations:
            if not capabilities.get("supports_load_balancer", False):
                networking_adaptations["use_load_balancer"] = False
        
        # Adjust ingress configuration based on capabilities
        if "ingress" in networking_adaptations:
            if not capabilities.get("supports_ingress", False):
                networking_adaptations["ingress"]["enabled"] = False
        
        # Add mesh networking for edge environments
        if environment_type == "edge" and "mesh_networking" not in networking_adaptations:
            networking_adaptations["mesh_networking"] = {
                "enabled": True,
                "discovery": "mdns"
            }
        
        # Add multi-cluster networking for hybrid environments
        if environment_type == "hybrid" and "multi_cluster_networking" not in networking_adaptations:
            networking_adaptations["multi_cluster_networking"] = {
                "enabled": True,
                "gateway": "istio"
            }
        
        return networking_adaptations
    
    def _apply_security_adaptations(self, 
                                  deployment_manifest: Dict[str, Any], 
                                  environment_type: str,
                                  template: Dict[str, Any],
                                  capabilities: Dict[str, Any],
                                  resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply security adaptations to a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            environment_type: Type of environment
            template: Adaptation template
            capabilities: Environment capabilities
            resources: Resource requirements
            
        Returns:
            Security adaptations
        """
        # Start with template security adaptations
        security_adaptations = dict(template.get("security", {}))
        
        # Adjust secrets management based on environment
        if "secrets_management" in security_adaptations:
            if environment_type == "edge":
                security_adaptations["secrets_management"]["use_vault"] = False
                security_adaptations["secrets_management"]["use_cloud_secrets"] = False
                security_adaptations["secrets_management"]["use_local_secrets"] = True
            elif environment_type == "cloud":
                security_adaptations["secrets_management"]["use_vault"] = False
                security_adaptations["secrets_management"]["use_cloud_secrets"] = True
            elif environment_type == "on-premise":
                security_adaptations["secrets_management"]["use_vault"] = True
                security_adaptations["secrets_management"]["use_cloud_secrets"] = False
        
        # Add encryption for edge environments
        if environment_type == "edge" and "encryption" not in security_adaptations:
            security_adaptations["encryption"] = {
                "enabled": True,
                "at_rest": True,
                "in_transit": True
            }
        
        return security_adaptations
    
    def _deep_copy(self, obj: Any) -> Any:
        """
        Create a deep copy of an object.
        
        Args:
            obj: Object to copy
            
        Returns:
            Deep copy of the object
        """
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
    
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
