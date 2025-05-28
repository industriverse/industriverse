"""
Resource Calculator

This module calculates resource requirements for deployments in different environments.
It determines the appropriate CPU, memory, storage, and other resources needed based on
deployment specifications and environment capabilities.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ResourceCalculator:
    """
    Calculator for deployment resource requirements.
    """
    
    def __init__(self, resource_profiles_path: Optional[str] = None):
        """
        Initialize the Resource Calculator.
        
        Args:
            resource_profiles_path: Path to resource profiles file
        """
        self.resource_profiles_path = resource_profiles_path or os.environ.get(
            "RESOURCE_PROFILES_PATH", "/var/lib/industriverse/environments/resource_profiles.json"
        )
        self.resource_profiles = self._load_resource_profiles()
        logger.info("Resource Calculator initialized")
    
    def calculate_resources(self, 
                          deployment_manifest: Dict[str, Any], 
                          environment_type: str,
                          capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate resource requirements for a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            environment_type: Type of environment
            capabilities: Environment capabilities
            
        Returns:
            Dict containing calculated resources
        """
        logger.info(f"Calculating resources for deployment: {deployment_manifest.get('name', 'unnamed')} in environment: {environment_type}")
        
        try:
            # Get resource profile for this environment type
            profile = self._get_resource_profile(environment_type)
            
            # Calculate component resources
            component_resources = self._calculate_component_resources(
                deployment_manifest, environment_type, profile, capabilities
            )
            
            # Calculate total resources
            total_resources = self._calculate_total_resources(component_resources)
            
            # Apply environment-specific adjustments
            adjusted_resources = self._apply_environment_adjustments(
                total_resources, environment_type, capabilities
            )
            
            # Check against environment capabilities
            resource_validation = self._validate_against_capabilities(
                adjusted_resources, capabilities
            )
            
            # Prepare result
            resources = {
                "components": component_resources,
                "total": total_resources,
                "adjusted": adjusted_resources,
                "validation": resource_validation,
                "timestamp": self._get_timestamp()
            }
            
            return {
                "success": True,
                "resources": resources
            }
            
        except Exception as e:
            logger.exception(f"Error calculating resources: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def estimate_cost(self, 
                    resources: Dict[str, Any], 
                    environment_type: str,
                    region: str = "us-east-1") -> Dict[str, Any]:
        """
        Estimate cost for resources in an environment.
        
        Args:
            resources: Resource requirements
            environment_type: Type of environment
            region: Cloud region (for cloud environments)
            
        Returns:
            Dict containing cost estimate
        """
        logger.info(f"Estimating cost for resources in environment: {environment_type}, region: {region}")
        
        try:
            # Get cost factors for this environment type and region
            cost_factors = self._get_cost_factors(environment_type, region)
            
            # Calculate compute costs
            compute_costs = self._calculate_compute_costs(
                resources["adjusted"]["cpu"],
                resources["adjusted"]["memory"],
                cost_factors
            )
            
            # Calculate storage costs
            storage_costs = self._calculate_storage_costs(
                resources["adjusted"]["storage"],
                cost_factors
            )
            
            # Calculate networking costs
            networking_costs = self._calculate_networking_costs(
                resources["adjusted"].get("networking", {}),
                cost_factors
            )
            
            # Calculate total costs
            total_monthly_cost = compute_costs["monthly"] + storage_costs["monthly"] + networking_costs["monthly"]
            
            # Prepare result
            cost_estimate = {
                "compute": compute_costs,
                "storage": storage_costs,
                "networking": networking_costs,
                "total": {
                    "monthly": total_monthly_cost,
                    "yearly": total_monthly_cost * 12
                },
                "currency": "USD",
                "environment_type": environment_type,
                "region": region,
                "timestamp": self._get_timestamp()
            }
            
            return {
                "success": True,
                "cost_estimate": cost_estimate
            }
            
        except Exception as e:
            logger.exception(f"Error estimating cost: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_resource_profiles(self) -> Dict[str, Any]:
        """
        Load resource profiles from file.
        
        Returns:
            Dict containing resource profiles
        """
        try:
            if os.path.exists(self.resource_profiles_path):
                with open(self.resource_profiles_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Resource profiles file not found: {self.resource_profiles_path}")
                return self._get_default_resource_profiles()
                
        except Exception as e:
            logger.exception(f"Error loading resource profiles: {str(e)}")
            return self._get_default_resource_profiles()
    
    def _get_default_resource_profiles(self) -> Dict[str, Any]:
        """
        Get default resource profiles.
        
        Returns:
            Dict containing default resource profiles
        """
        return {
            "cloud": {
                "component_defaults": {
                    "api": {
                        "cpu": {
                            "request": 0.5,
                            "limit": 1.0
                        },
                        "memory": {
                            "request": 512,
                            "limit": 1024
                        },
                        "storage": {
                            "request": 1,
                            "limit": 5
                        },
                        "replicas": 2
                    },
                    "web": {
                        "cpu": {
                            "request": 0.25,
                            "limit": 0.5
                        },
                        "memory": {
                            "request": 256,
                            "limit": 512
                        },
                        "storage": {
                            "request": 1,
                            "limit": 2
                        },
                        "replicas": 2
                    },
                    "database": {
                        "cpu": {
                            "request": 1.0,
                            "limit": 2.0
                        },
                        "memory": {
                            "request": 1024,
                            "limit": 2048
                        },
                        "storage": {
                            "request": 10,
                            "limit": 50
                        },
                        "replicas": 1
                    },
                    "worker": {
                        "cpu": {
                            "request": 0.5,
                            "limit": 1.0
                        },
                        "memory": {
                            "request": 512,
                            "limit": 1024
                        },
                        "storage": {
                            "request": 1,
                            "limit": 5
                        },
                        "replicas": 2
                    },
                    "cache": {
                        "cpu": {
                            "request": 0.5,
                            "limit": 1.0
                        },
                        "memory": {
                            "request": 1024,
                            "limit": 2048
                        },
                        "storage": {
                            "request": 1,
                            "limit": 5
                        },
                        "replicas": 1
                    }
                },
                "adjustment_factors": {
                    "cpu": 1.0,
                    "memory": 1.0,
                    "storage": 1.0
                },
                "cost_factors": {
                    "us-east-1": {
                        "cpu_per_core_hour": 0.0425,
                        "memory_per_gb_hour": 0.0053,
                        "storage_per_gb_month": 0.10,
                        "network_per_gb": 0.01
                    },
                    "us-west-1": {
                        "cpu_per_core_hour": 0.0467,
                        "memory_per_gb_hour": 0.0058,
                        "storage_per_gb_month": 0.11,
                        "network_per_gb": 0.01
                    },
                    "eu-west-1": {
                        "cpu_per_core_hour": 0.0467,
                        "memory_per_gb_hour": 0.0058,
                        "storage_per_gb_month": 0.11,
                        "network_per_gb": 0.01
                    }
                }
            },
            "edge": {
                "component_defaults": {
                    "api": {
                        "cpu": {
                            "request": 0.2,
                            "limit": 0.4
                        },
                        "memory": {
                            "request": 128,
                            "limit": 256
                        },
                        "storage": {
                            "request": 0.5,
                            "limit": 1
                        },
                        "replicas": 1
                    },
                    "web": {
                        "cpu": {
                            "request": 0.1,
                            "limit": 0.2
                        },
                        "memory": {
                            "request": 64,
                            "limit": 128
                        },
                        "storage": {
                            "request": 0.5,
                            "limit": 1
                        },
                        "replicas": 1
                    },
                    "database": {
                        "cpu": {
                            "request": 0.3,
                            "limit": 0.6
                        },
                        "memory": {
                            "request": 256,
                            "limit": 512
                        },
                        "storage": {
                            "request": 2,
                            "limit": 5
                        },
                        "replicas": 1
                    },
                    "worker": {
                        "cpu": {
                            "request": 0.2,
                            "limit": 0.4
                        },
                        "memory": {
                            "request": 128,
                            "limit": 256
                        },
                        "storage": {
                            "request": 0.5,
                            "limit": 1
                        },
                        "replicas": 1
                    },
                    "cache": {
                        "cpu": {
                            "request": 0.1,
                            "limit": 0.2
                        },
                        "memory": {
                            "request": 128,
                            "limit": 256
                        },
                        "storage": {
                            "request": 0.5,
                            "limit": 1
                        },
                        "replicas": 1
                    }
                },
                "adjustment_factors": {
                    "cpu": 0.8,
                    "memory": 0.8,
                    "storage": 0.8
                },
                "cost_factors": {
                    "default": {
                        "cpu_per_core_hour": 0.0,
                        "memory_per_gb_hour": 0.0,
                        "storage_per_gb_month": 0.0,
                        "network_per_gb": 0.0
                    }
                }
            },
            "on-premise": {
                "component_defaults": {
                    "api": {
                        "cpu": {
                            "request": 1.0,
                            "limit": 2.0
                        },
                        "memory": {
                            "request": 1024,
                            "limit": 2048
                        },
                        "storage": {
                            "request": 5,
                            "limit": 10
                        },
                        "replicas": 2
                    },
                    "web": {
                        "cpu": {
                            "request": 0.5,
                            "limit": 1.0
                        },
                        "memory": {
                            "request": 512,
                            "limit": 1024
                        },
                        "storage": {
                            "request": 2,
                            "limit": 5
                        },
                        "replicas": 2
                    },
                    "database": {
                        "cpu": {
                            "request": 2.0,
                            "limit": 4.0
                        },
                        "memory": {
                            "request": 4096,
                            "limit": 8192
                        },
                        "storage": {
                            "request": 50,
                            "limit": 100
                        },
                        "replicas": 2
                    },
                    "worker": {
                        "cpu": {
                            "request": 1.0,
                            "limit": 2.0
                        },
                        "memory": {
                            "request": 1024,
                            "limit": 2048
                        },
                        "storage": {
                            "request": 5,
                            "limit": 10
                        },
                        "replicas": 2
                    },
                    "cache": {
                        "cpu": {
                            "request": 1.0,
                            "limit": 2.0
                        },
                        "memory": {
                            "request": 2048,
                            "limit": 4096
                        },
                        "storage": {
                            "request": 5,
                            "limit": 10
                        },
                        "replicas": 2
                    }
                },
                "adjustment_factors": {
                    "cpu": 1.2,
                    "memory": 1.2,
                    "storage": 1.5
                },
                "cost_factors": {
                    "default": {
                        "cpu_per_core_hour": 0.02,
                        "memory_per_gb_hour": 0.003,
                        "storage_per_gb_month": 0.05,
                        "network_per_gb": 0.005
                    }
                }
            },
            "hybrid": {
                "component_defaults": {
                    "api": {
                        "cpu": {
                            "request": 0.5,
                            "limit": 1.0
                        },
                        "memory": {
                            "request": 512,
                            "limit": 1024
                        },
                        "storage": {
                            "request": 2,
                            "limit": 5
                        },
                        "replicas": 2
                    },
                    "web": {
                        "cpu": {
                            "request": 0.25,
                            "limit": 0.5
                        },
                        "memory": {
                            "request": 256,
                            "limit": 512
                        },
                        "storage": {
                            "request": 1,
                            "limit": 2
                        },
                        "replicas": 2
                    },
                    "database": {
                        "cpu": {
                            "request": 1.0,
                            "limit": 2.0
                        },
                        "memory": {
                            "request": 2048,
                            "limit": 4096
                        },
                        "storage": {
                            "request": 20,
                            "limit": 50
                        },
                        "replicas": 2
                    },
                    "worker": {
                        "cpu": {
                            "request": 0.5,
                            "limit": 1.0
                        },
                        "memory": {
                            "request": 512,
                            "limit": 1024
                        },
                        "storage": {
                            "request": 2,
                            "limit": 5
                        },
                        "replicas": 2
                    },
                    "cache": {
                        "cpu": {
                            "request": 0.5,
                            "limit": 1.0
                        },
                        "memory": {
                            "request": 1024,
                            "limit": 2048
                        },
                        "storage": {
                            "request": 2,
                            "limit": 5
                        },
                        "replicas": 2
                    }
                },
                "adjustment_factors": {
                    "cpu": 1.1,
                    "memory": 1.1,
                    "storage": 1.2
                },
                "cost_factors": {
                    "default": {
                        "cpu_per_core_hour": 0.03,
                        "memory_per_gb_hour": 0.004,
                        "storage_per_gb_month": 0.08,
                        "network_per_gb": 0.008
                    }
                }
            }
        }
    
    def _get_resource_profile(self, environment_type: str) -> Dict[str, Any]:
        """
        Get resource profile for an environment type.
        
        Args:
            environment_type: Type of environment
            
        Returns:
            Resource profile
        """
        if environment_type in self.resource_profiles:
            return self.resource_profiles[environment_type]
        else:
            logger.warning(f"Resource profile not found for environment type: {environment_type}")
            return {
                "component_defaults": {},
                "adjustment_factors": {
                    "cpu": 1.0,
                    "memory": 1.0,
                    "storage": 1.0
                }
            }
    
    def _calculate_component_resources(self, 
                                     deployment_manifest: Dict[str, Any], 
                                     environment_type: str,
                                     profile: Dict[str, Any],
                                     capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate resources for each component.
        
        Args:
            deployment_manifest: Deployment manifest
            environment_type: Type of environment
            profile: Resource profile
            capabilities: Environment capabilities
            
        Returns:
            Dict mapping components to resources
        """
        component_resources = {}
        
        # Get components from manifest
        components = deployment_manifest.get("components", {})
        
        # Get component defaults from profile
        component_defaults = profile.get("component_defaults", {})
        
        # Process each component
        for component_name, component_config in components.items():
            # Determine component type
            component_type = component_config.get("type", "api")
            
            # Get default resources for this component type
            default_resources = component_defaults.get(component_type, component_defaults.get("api", {}))
            
            # Get component-specific resource requirements
            component_resources[component_name] = self._calculate_component_specific_resources(
                component_name, component_config, default_resources, environment_type, capabilities
            )
        
        return component_resources
    
    def _calculate_component_specific_resources(self, 
                                             component_name: str,
                                             component_config: Dict[str, Any],
                                             default_resources: Dict[str, Any],
                                             environment_type: str,
                                             capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate resources for a specific component.
        
        Args:
            component_name: Name of the component
            component_config: Component configuration
            default_resources: Default resources for this component type
            environment_type: Type of environment
            capabilities: Environment capabilities
            
        Returns:
            Component resources
        """
        # Start with default resources
        resources = {
            "cpu": dict(default_resources.get("cpu", {"request": 0.5, "limit": 1.0})),
            "memory": dict(default_resources.get("memory", {"request": 512, "limit": 1024})),
            "storage": dict(default_resources.get("storage", {"request": 1, "limit": 5})),
            "replicas": default_resources.get("replicas", 1)
        }
        
        # Apply component-specific resource requirements if specified
        if "resources" in component_config:
            component_resources = component_config["resources"]
            
            # CPU resources
            if "cpu" in component_resources:
                if "request" in component_resources["cpu"]:
                    resources["cpu"]["request"] = component_resources["cpu"]["request"]
                if "limit" in component_resources["cpu"]:
                    resources["cpu"]["limit"] = component_resources["cpu"]["limit"]
            
            # Memory resources
            if "memory" in component_resources:
                if "request" in component_resources["memory"]:
                    resources["memory"]["request"] = component_resources["memory"]["request"]
                if "limit" in component_resources["memory"]:
                    resources["memory"]["limit"] = component_resources["memory"]["limit"]
            
            # Storage resources
            if "storage" in component_resources:
                if "request" in component_resources["storage"]:
                    resources["storage"]["request"] = component_resources["storage"]["request"]
                if "limit" in component_resources["storage"]:
                    resources["storage"]["limit"] = component_resources["storage"]["limit"]
        
        # Apply replicas if specified
        if "replicas" in component_config:
            resources["replicas"] = component_config["replicas"]
        
        # Adjust for environment constraints
        if environment_type == "edge":
            # Edge environments typically have limited resources
            resources["replicas"] = min(resources["replicas"], 1)
            
            # Ensure CPU doesn't exceed edge capabilities
            max_cpu = capabilities.get("max_cpu", 4)
            resources["cpu"]["request"] = min(resources["cpu"]["request"], max_cpu * 0.5)
            resources["cpu"]["limit"] = min(resources["cpu"]["limit"], max_cpu * 0.8)
            
            # Ensure memory doesn't exceed edge capabilities
            max_memory = capabilities.get("max_memory", 16)
            resources["memory"]["request"] = min(resources["memory"]["request"], max_memory * 0.5)
            resources["memory"]["limit"] = min(resources["memory"]["limit"], max_memory * 0.8)
        
        # Calculate total resources for this component (considering replicas)
        resources["total"] = {
            "cpu": resources["cpu"]["request"] * resources["replicas"],
            "memory": resources["memory"]["request"] * resources["replicas"],
            "storage": resources["storage"]["request"] * resources["replicas"]
        }
        
        return resources
    
    def _calculate_total_resources(self, component_resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate total resources across all components.
        
        Args:
            component_resources: Resources for each component
            
        Returns:
            Total resources
        """
        total_cpu = 0
        total_memory = 0
        total_storage = 0
        
        # Sum up resources across all components
        for component_name, resources in component_resources.items():
            total_cpu += resources["total"]["cpu"]
            total_memory += resources["total"]["memory"]
            total_storage += resources["total"]["storage"]
        
        return {
            "cpu": total_cpu,
            "memory": total_memory,
            "storage": total_storage
        }
    
    def _apply_environment_adjustments(self, 
                                     total_resources: Dict[str, Any], 
                                     environment_type: str,
                                     capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment-specific adjustments to resources.
        
        Args:
            total_resources: Total resources
            environment_type: Type of environment
            capabilities: Environment capabilities
            
        Returns:
            Adjusted resources
        """
        # Get resource profile for this environment type
        profile = self._get_resource_profile(environment_type)
        
        # Get adjustment factors
        adjustment_factors = profile.get("adjustment_factors", {
            "cpu": 1.0,
            "memory": 1.0,
            "storage": 1.0
        })
        
        # Apply adjustment factors
        adjusted_cpu = total_resources["cpu"] * adjustment_factors.get("cpu", 1.0)
        adjusted_memory = total_resources["memory"] * adjustment_factors.get("memory", 1.0)
        adjusted_storage = total_resources["storage"] * adjustment_factors.get("storage", 1.0)
        
        # Add networking resources (estimated)
        networking = {
            "ingress_bandwidth": adjusted_cpu * 0.5,  # GB per hour
            "egress_bandwidth": adjusted_cpu * 0.2    # GB per hour
        }
        
        return {
            "cpu": adjusted_cpu,
            "memory": adjusted_memory,
            "storage": adjusted_storage,
            "networking": networking
        }
    
    def _validate_against_capabilities(self, 
                                     adjusted_resources: Dict[str, Any], 
                                     capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate resources against environment capabilities.
        
        Args:
            adjusted_resources: Adjusted resources
            capabilities: Environment capabilities
            
        Returns:
            Validation result
        """
        validation = {
            "valid": True,
            "issues": []
        }
        
        # Check CPU
        max_cpu = capabilities.get("max_cpu", 0)
        if max_cpu > 0 and adjusted_resources["cpu"] > max_cpu:
            validation["valid"] = False
            validation["issues"].append({
                "resource": "cpu",
                "required": adjusted_resources["cpu"],
                "available": max_cpu,
                "message": f"Required CPU ({adjusted_resources['cpu']}) exceeds available ({max_cpu})"
            })
        
        # Check memory
        max_memory = capabilities.get("max_memory", 0)
        if max_memory > 0 and adjusted_resources["memory"] > max_memory:
            validation["valid"] = False
            validation["issues"].append({
                "resource": "memory",
                "required": adjusted_resources["memory"],
                "available": max_memory,
                "message": f"Required memory ({adjusted_resources['memory']}) exceeds available ({max_memory})"
            })
        
        # Check storage
        max_storage = capabilities.get("max_storage", 0)
        if max_storage > 0 and adjusted_resources["storage"] > max_storage:
            validation["valid"] = False
            validation["issues"].append({
                "resource": "storage",
                "required": adjusted_resources["storage"],
                "available": max_storage,
                "message": f"Required storage ({adjusted_resources['storage']}) exceeds available ({max_storage})"
            })
        
        return validation
    
    def _get_cost_factors(self, environment_type: str, region: str) -> Dict[str, Any]:
        """
        Get cost factors for an environment type and region.
        
        Args:
            environment_type: Type of environment
            region: Cloud region
            
        Returns:
            Cost factors
        """
        # Get resource profile for this environment type
        profile = self._get_resource_profile(environment_type)
        
        # Get cost factors
        cost_factors = profile.get("cost_factors", {})
        
        # Get region-specific cost factors, or default
        if region in cost_factors:
            return cost_factors[region]
        elif "default" in cost_factors:
            return cost_factors["default"]
        else:
            return {
                "cpu_per_core_hour": 0.04,
                "memory_per_gb_hour": 0.005,
                "storage_per_gb_month": 0.10,
                "network_per_gb": 0.01
            }
    
    def _calculate_compute_costs(self, 
                               cpu: float, 
                               memory: float, 
                               cost_factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate compute costs.
        
        Args:
            cpu: CPU cores
            memory: Memory in MB
            cost_factors: Cost factors
            
        Returns:
            Compute costs
        """
        # Convert memory from MB to GB
        memory_gb = memory / 1024
        
        # Calculate hourly costs
        cpu_hourly = cpu * cost_factors.get("cpu_per_core_hour", 0)
        memory_hourly = memory_gb * cost_factors.get("memory_per_gb_hour", 0)
        total_hourly = cpu_hourly + memory_hourly
        
        # Calculate monthly costs (730 hours per month)
        cpu_monthly = cpu_hourly * 730
        memory_monthly = memory_hourly * 730
        total_monthly = total_hourly * 730
        
        return {
            "hourly": {
                "cpu": cpu_hourly,
                "memory": memory_hourly,
                "total": total_hourly
            },
            "monthly": {
                "cpu": cpu_monthly,
                "memory": memory_monthly,
                "total": total_monthly
            }
        }
    
    def _calculate_storage_costs(self, 
                               storage: float, 
                               cost_factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate storage costs.
        
        Args:
            storage: Storage in GB
            cost_factors: Cost factors
            
        Returns:
            Storage costs
        """
        # Calculate monthly costs
        monthly = storage * cost_factors.get("storage_per_gb_month", 0)
        
        return {
            "monthly": monthly
        }
    
    def _calculate_networking_costs(self, 
                                  networking: Dict[str, Any], 
                                  cost_factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate networking costs.
        
        Args:
            networking: Networking resources
            cost_factors: Cost factors
            
        Returns:
            Networking costs
        """
        # Get bandwidth estimates
        ingress_bandwidth = networking.get("ingress_bandwidth", 0)
        egress_bandwidth = networking.get("egress_bandwidth", 0)
        
        # Calculate monthly costs (730 hours per month)
        ingress_monthly = ingress_bandwidth * 730 * cost_factors.get("network_per_gb", 0)
        egress_monthly = egress_bandwidth * 730 * cost_factors.get("network_per_gb", 0)
        total_monthly = ingress_monthly + egress_monthly
        
        return {
            "monthly": {
                "ingress": ingress_monthly,
                "egress": egress_monthly,
                "total": total_monthly
            }
        }
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
