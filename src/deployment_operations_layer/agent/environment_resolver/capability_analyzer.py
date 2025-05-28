"""
Capability Analyzer

This module analyzes the capabilities of deployment environments. It determines
what features and resources are available in a given environment and how they
can be utilized for deployments.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class CapabilityAnalyzer:
    """
    Analyzer for environment capabilities.
    """
    
    def __init__(self, capability_profiles_path: Optional[str] = None):
        """
        Initialize the Capability Analyzer.
        
        Args:
            capability_profiles_path: Path to capability profiles file
        """
        self.capability_profiles_path = capability_profiles_path or os.environ.get(
            "CAPABILITY_PROFILES_PATH", "/var/lib/industriverse/environments/capability_profiles.json"
        )
        self.capability_profiles = self._load_capability_profiles()
        logger.info("Capability Analyzer initialized")
    
    def analyze_capabilities(self, 
                           environment_type: str, 
                           environment_details: Dict[str, Any],
                           deployment_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze capabilities of an environment.
        
        Args:
            environment_type: Type of environment
            environment_details: Details of the environment
            deployment_manifest: Deployment manifest
            
        Returns:
            Dict containing analyzed capabilities
        """
        logger.info(f"Analyzing capabilities for environment: {environment_type}")
        
        try:
            # Start with base capabilities from environment details
            base_capabilities = environment_details.get("capabilities", {})
            
            # Get capability profile for this environment type
            profile = self._get_capability_profile(environment_type)
            
            # Merge base capabilities with profile
            capabilities = self._merge_capabilities(base_capabilities, profile)
            
            # Analyze specific capabilities based on deployment requirements
            analyzed_capabilities = self._analyze_specific_capabilities(
                capabilities, environment_type, deployment_manifest
            )
            
            return {
                "success": True,
                "capabilities": analyzed_capabilities
            }
            
        except Exception as e:
            logger.exception(f"Error analyzing capabilities: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_capability_support(self, 
                               environment_type: str, 
                               capability: str) -> Dict[str, Any]:
        """
        Check if a specific capability is supported in an environment.
        
        Args:
            environment_type: Type of environment
            capability: Capability to check
            
        Returns:
            Dict containing support status
        """
        logger.info(f"Checking capability support for {capability} in {environment_type}")
        
        try:
            # Get capability profile for this environment type
            profile = self._get_capability_profile(environment_type)
            
            # Check if capability is supported
            if capability in profile.get("supported_features", []):
                return {
                    "supported": True,
                    "environment_type": environment_type,
                    "capability": capability
                }
            
            # Check if capability is in extended capabilities
            if capability in profile.get("extended_capabilities", {}):
                return {
                    "supported": True,
                    "environment_type": environment_type,
                    "capability": capability,
                    "details": profile["extended_capabilities"][capability]
                }
            
            return {
                "supported": False,
                "environment_type": environment_type,
                "capability": capability,
                "alternatives": self._get_alternative_capabilities(capability, profile)
            }
            
        except Exception as e:
            logger.exception(f"Error checking capability support: {str(e)}")
            return {
                "supported": False,
                "environment_type": environment_type,
                "capability": capability,
                "error": str(e)
            }
    
    def _load_capability_profiles(self) -> Dict[str, Any]:
        """
        Load capability profiles from file.
        
        Returns:
            Dict containing capability profiles
        """
        try:
            if os.path.exists(self.capability_profiles_path):
                with open(self.capability_profiles_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Capability profiles file not found: {self.capability_profiles_path}")
                return self._get_default_capability_profiles()
                
        except Exception as e:
            logger.exception(f"Error loading capability profiles: {str(e)}")
            return self._get_default_capability_profiles()
    
    def _get_default_capability_profiles(self) -> Dict[str, Any]:
        """
        Get default capability profiles.
        
        Returns:
            Dict containing default capability profiles
        """
        return {
            "cloud": {
                "compute": {
                    "cpu_types": ["x86_64", "arm64"],
                    "memory_types": ["ddr4", "ddr5"],
                    "instance_types": ["general_purpose", "compute_optimized", "memory_optimized"]
                },
                "storage": {
                    "types": ["block", "object", "file"],
                    "performance_tiers": ["standard", "premium", "high_performance"]
                },
                "networking": {
                    "types": ["vpc", "subnet", "load_balancer", "api_gateway"],
                    "features": ["auto_scaling", "traffic_management", "dns_management"]
                },
                "security": {
                    "features": ["encryption", "identity_management", "key_management", "certificate_management"]
                },
                "supported_features": [
                    "kubernetes", "serverless", "managed_databases", "load_balancing", 
                    "auto_scaling", "monitoring", "logging", "alerting"
                ],
                "extended_capabilities": {
                    "multi_region": {
                        "supported": True,
                        "implementation": "native"
                    },
                    "disaster_recovery": {
                        "supported": True,
                        "implementation": "native"
                    }
                }
            },
            "edge": {
                "compute": {
                    "cpu_types": ["arm", "x86"],
                    "memory_types": ["lpddr4", "ddr4"],
                    "instance_types": ["constrained", "standard"]
                },
                "storage": {
                    "types": ["local", "distributed"],
                    "performance_tiers": ["standard"]
                },
                "networking": {
                    "types": ["mesh", "local"],
                    "features": ["offline_operation", "sync"]
                },
                "security": {
                    "features": ["encryption", "secure_boot", "attestation"]
                },
                "supported_features": [
                    "containerization", "local_storage", "mesh_networking",
                    "offline_operation", "low_latency", "local_processing"
                ],
                "extended_capabilities": {
                    "multi_region": {
                        "supported": False
                    },
                    "disaster_recovery": {
                        "supported": True,
                        "implementation": "custom"
                    }
                }
            },
            "on-premise": {
                "compute": {
                    "cpu_types": ["x86_64", "power", "sparc"],
                    "memory_types": ["ddr4", "ddr5"],
                    "instance_types": ["physical", "virtual"]
                },
                "storage": {
                    "types": ["san", "nas", "das"],
                    "performance_tiers": ["standard", "high_performance"]
                },
                "networking": {
                    "types": ["lan", "wan", "load_balancer"],
                    "features": ["vlan", "routing", "firewall"]
                },
                "security": {
                    "features": ["encryption", "identity_management", "physical_security"]
                },
                "supported_features": [
                    "kubernetes", "virtualization", "storage_arrays",
                    "load_balancing", "monitoring", "high_availability"
                ],
                "extended_capabilities": {
                    "multi_region": {
                        "supported": True,
                        "implementation": "custom"
                    },
                    "disaster_recovery": {
                        "supported": True,
                        "implementation": "custom"
                    }
                }
            },
            "hybrid": {
                "compute": {
                    "cpu_types": ["x86_64", "arm64"],
                    "memory_types": ["ddr4", "ddr5"],
                    "instance_types": ["cloud", "on-premise", "edge"]
                },
                "storage": {
                    "types": ["block", "object", "file", "san", "nas"],
                    "performance_tiers": ["standard", "premium", "high_performance"]
                },
                "networking": {
                    "types": ["vpc", "lan", "wan", "load_balancer"],
                    "features": ["auto_scaling", "traffic_management", "dns_management", "vpn"]
                },
                "security": {
                    "features": ["encryption", "identity_management", "key_management", "certificate_management"]
                },
                "supported_features": [
                    "kubernetes", "multi-cloud", "cloud_bursting",
                    "load_balancing", "auto_scaling", "monitoring",
                    "data_replication", "hybrid_networking"
                ],
                "extended_capabilities": {
                    "multi_region": {
                        "supported": True,
                        "implementation": "hybrid"
                    },
                    "disaster_recovery": {
                        "supported": True,
                        "implementation": "hybrid"
                    }
                }
            }
        }
    
    def _get_capability_profile(self, environment_type: str) -> Dict[str, Any]:
        """
        Get capability profile for an environment type.
        
        Args:
            environment_type: Type of environment
            
        Returns:
            Capability profile
        """
        if environment_type in self.capability_profiles:
            return self.capability_profiles[environment_type]
        else:
            logger.warning(f"Capability profile not found for environment type: {environment_type}")
            return {}
    
    def _merge_capabilities(self, 
                          base_capabilities: Dict[str, Any], 
                          profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge base capabilities with profile.
        
        Args:
            base_capabilities: Base capabilities
            profile: Capability profile
            
        Returns:
            Merged capabilities
        """
        # Start with a copy of base capabilities
        merged = dict(base_capabilities)
        
        # Add profile capabilities
        for key, value in profile.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                merged[key] = self._merge_dict(merged[key], value)
            elif isinstance(merged[key], list) and isinstance(value, list):
                # Merge lists, removing duplicates
                merged[key] = list(set(merged[key] + value))
        
        return merged
    
    def _merge_dict(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries.
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            
        Returns:
            Merged dictionary
        """
        result = dict(dict1)
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dict(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _analyze_specific_capabilities(self, 
                                     capabilities: Dict[str, Any], 
                                     environment_type: str,
                                     deployment_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze specific capabilities based on deployment requirements.
        
        Args:
            capabilities: Base capabilities
            environment_type: Type of environment
            deployment_manifest: Deployment manifest
            
        Returns:
            Analyzed capabilities
        """
        # Start with a copy of capabilities
        analyzed = dict(capabilities)
        
        # Get deployment requirements
        requirements = deployment_manifest.get("requirements", {})
        
        # Analyze compute capabilities
        if "compute" in requirements:
            compute_req = requirements["compute"]
            analyzed["compute_analysis"] = {
                "meets_requirements": True,
                "details": {}
            }
            
            # Check CPU requirements
            if "min_cpu" in compute_req:
                min_cpu = compute_req["min_cpu"]
                max_cpu = analyzed.get("max_cpu", 0)
                analyzed["compute_analysis"]["details"]["cpu"] = {
                    "required": min_cpu,
                    "available": max_cpu,
                    "sufficient": max_cpu >= min_cpu
                }
                
                if max_cpu < min_cpu:
                    analyzed["compute_analysis"]["meets_requirements"] = False
            
            # Check memory requirements
            if "min_memory" in compute_req:
                min_memory = compute_req["min_memory"]
                max_memory = analyzed.get("max_memory", 0)
                analyzed["compute_analysis"]["details"]["memory"] = {
                    "required": min_memory,
                    "available": max_memory,
                    "sufficient": max_memory >= min_memory
                }
                
                if max_memory < min_memory:
                    analyzed["compute_analysis"]["meets_requirements"] = False
        
        # Analyze storage capabilities
        if "storage" in requirements:
            storage_req = requirements["storage"]
            analyzed["storage_analysis"] = {
                "meets_requirements": True,
                "details": {}
            }
            
            # Check capacity requirements
            if "min_capacity" in storage_req:
                min_capacity = storage_req["min_capacity"]
                max_storage = analyzed.get("max_storage", 0)
                analyzed["storage_analysis"]["details"]["capacity"] = {
                    "required": min_capacity,
                    "available": max_storage,
                    "sufficient": max_storage >= min_capacity
                }
                
                if max_storage < min_capacity:
                    analyzed["storage_analysis"]["meets_requirements"] = False
            
            # Check storage type requirements
            if "types" in storage_req:
                required_types = storage_req["types"]
                available_types = analyzed.get("storage", {}).get("types", [])
                missing_types = [t for t in required_types if t not in available_types]
                
                analyzed["storage_analysis"]["details"]["types"] = {
                    "required": required_types,
                    "available": available_types,
                    "missing": missing_types,
                    "sufficient": len(missing_types) == 0
                }
                
                if missing_types:
                    analyzed["storage_analysis"]["meets_requirements"] = False
        
        # Analyze networking capabilities
        if "networking" in requirements:
            network_req = requirements["networking"]
            analyzed["networking_analysis"] = {
                "meets_requirements": True,
                "details": {}
            }
            
            # Check ingress requirements
            if "ingress" in network_req:
                required_ingress = network_req["ingress"]
                supports_ingress = analyzed.get("supports_ingress", False)
                
                analyzed["networking_analysis"]["details"]["ingress"] = {
                    "required": required_ingress,
                    "available": supports_ingress,
                    "sufficient": not required_ingress or supports_ingress
                }
                
                if required_ingress and not supports_ingress:
                    analyzed["networking_analysis"]["meets_requirements"] = False
            
            # Check load balancer requirements
            if "load_balancer" in network_req:
                required_lb = network_req["load_balancer"]
                supports_lb = analyzed.get("supports_load_balancer", False)
                
                analyzed["networking_analysis"]["details"]["load_balancer"] = {
                    "required": required_lb,
                    "available": supports_lb,
                    "sufficient": not required_lb or supports_lb
                }
                
                if required_lb and not supports_lb:
                    analyzed["networking_analysis"]["meets_requirements"] = False
        
        # Analyze feature requirements
        if "features" in requirements:
            required_features = requirements["features"]
            supported_features = analyzed.get("supported_features", [])
            missing_features = [f for f in required_features if f not in supported_features]
            
            analyzed["feature_analysis"] = {
                "meets_requirements": len(missing_features) == 0,
                "details": {
                    "required": required_features,
                    "available": supported_features,
                    "missing": missing_features
                }
            }
        
        return analyzed
    
    def _get_alternative_capabilities(self, 
                                    capability: str, 
                                    profile: Dict[str, Any]) -> List[str]:
        """
        Get alternative capabilities for an unsupported capability.
        
        Args:
            capability: Unsupported capability
            profile: Capability profile
            
        Returns:
            List of alternative capabilities
        """
        # Define capability alternatives
        alternatives = {
            "kubernetes": ["containerization", "docker"],
            "serverless": ["containerization", "functions"],
            "managed_databases": ["local_storage", "containerized_databases"],
            "load_balancing": ["round_robin_dns", "application_routing"],
            "auto_scaling": ["manual_scaling", "scheduled_scaling"],
            "multi_region": ["data_replication", "backup_restore"],
            "disaster_recovery": ["backup_restore", "data_replication"]
        }
        
        if capability in alternatives:
            # Filter alternatives by what's supported in the profile
            supported_features = profile.get("supported_features", [])
            return [alt for alt in alternatives[capability] if alt in supported_features]
        
        return []
