"""
Environment Detector

This module detects and identifies deployment environments and their characteristics.
It determines the type of environment (cloud, edge, on-premise, etc.) and provides
detailed information about the environment's capabilities and constraints.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class EnvironmentDetector:
    """
    Detector for deployment environments.
    """
    
    def __init__(self, environment_definitions_path: Optional[str] = None):
        """
        Initialize the Environment Detector.
        
        Args:
            environment_definitions_path: Path to environment definitions file
        """
        self.environment_definitions_path = environment_definitions_path or os.environ.get(
            "ENVIRONMENT_DEFINITIONS_PATH", "/var/lib/industriverse/environments/definitions.json"
        )
        self.environment_definitions = self._load_environment_definitions()
        logger.info("Environment Detector initialized")
    
    def detect_environment(self, 
                         deployment_manifest: Dict[str, Any], 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect the deployment environment based on manifest and context.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            
        Returns:
            Dict containing the detected environment
        """
        logger.info(f"Detecting environment for deployment: {deployment_manifest.get('name', 'unnamed')}")
        
        try:
            # Check if environment is explicitly specified in context
            if "environment" in context and "type" in context["environment"]:
                environment_type = context["environment"]["type"]
                logger.info(f"Environment explicitly specified in context: {environment_type}")
                
                # Get environment details
                environment_details = self.get_environment_details(environment_type)
                
                return {
                    "success": True,
                    "environment_type": environment_type,
                    "environment_details": environment_details,
                    "detection_method": "explicit"
                }
            
            # Check if environment is specified in manifest
            if "environment" in deployment_manifest:
                environment_type = deployment_manifest["environment"].get("type")
                if environment_type:
                    logger.info(f"Environment specified in manifest: {environment_type}")
                    
                    # Get environment details
                    environment_details = self.get_environment_details(environment_type)
                    
                    return {
                        "success": True,
                        "environment_type": environment_type,
                        "environment_details": environment_details,
                        "detection_method": "manifest"
                    }
            
            # Auto-detect environment based on requirements and constraints
            detected_environment = self._auto_detect_environment(deployment_manifest, context)
            
            logger.info(f"Auto-detected environment: {detected_environment['environment_type']}")
            
            return {
                "success": True,
                "environment_type": detected_environment["environment_type"],
                "environment_details": detected_environment["environment_details"],
                "detection_method": "auto",
                "detection_confidence": detected_environment["confidence"]
            }
            
        except Exception as e:
            logger.exception(f"Error detecting environment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_environment_details(self, environment_type: str) -> Dict[str, Any]:
        """
        Get details for a specific environment type.
        
        Args:
            environment_type: Type of environment
            
        Returns:
            Dict containing environment details
        """
        if environment_type in self.environment_definitions:
            return self.environment_definitions[environment_type]
        else:
            logger.warning(f"Environment type not found in definitions: {environment_type}")
            return {
                "type": environment_type,
                "description": f"Unknown environment: {environment_type}",
                "capabilities": {}
            }
    
    def list_available_environments(self) -> List[Dict[str, Any]]:
        """
        List all available environment types.
        
        Returns:
            List of environment types and summaries
        """
        environments = []
        
        for env_type, env_details in self.environment_definitions.items():
            environments.append({
                "type": env_type,
                "description": env_details.get("description", ""),
                "category": env_details.get("category", "unknown")
            })
        
        return environments
    
    def _load_environment_definitions(self) -> Dict[str, Any]:
        """
        Load environment definitions from file.
        
        Returns:
            Dict containing environment definitions
        """
        try:
            if os.path.exists(self.environment_definitions_path):
                with open(self.environment_definitions_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Environment definitions file not found: {self.environment_definitions_path}")
                return self._get_default_environment_definitions()
                
        except Exception as e:
            logger.exception(f"Error loading environment definitions: {str(e)}")
            return self._get_default_environment_definitions()
    
    def _get_default_environment_definitions(self) -> Dict[str, Any]:
        """
        Get default environment definitions.
        
        Returns:
            Dict containing default environment definitions
        """
        return {
            "cloud": {
                "type": "cloud",
                "description": "Cloud-based deployment environment",
                "category": "cloud",
                "providers": ["aws", "azure", "gcp"],
                "capabilities": {
                    "scalability": "high",
                    "reliability": "high",
                    "max_cpu": 128,
                    "max_memory": 512,
                    "max_storage": 10000,
                    "supports_ingress": True,
                    "supports_load_balancer": True,
                    "supports_auto_scaling": True,
                    "supports_high_availability": True,
                    "supported_features": [
                        "kubernetes", "serverless", "managed_databases", 
                        "load_balancing", "auto_scaling", "monitoring"
                    ]
                }
            },
            "edge": {
                "type": "edge",
                "description": "Edge computing deployment environment",
                "category": "edge",
                "capabilities": {
                    "scalability": "low",
                    "reliability": "medium",
                    "max_cpu": 4,
                    "max_memory": 16,
                    "max_storage": 500,
                    "supports_ingress": True,
                    "supports_load_balancer": False,
                    "supports_auto_scaling": False,
                    "supports_high_availability": False,
                    "supports_offline_operation": True,
                    "supported_features": [
                        "containerization", "local_storage", "mesh_networking",
                        "offline_operation", "low_latency"
                    ]
                }
            },
            "on-premise": {
                "type": "on-premise",
                "description": "On-premise deployment environment",
                "category": "on-premise",
                "capabilities": {
                    "scalability": "medium",
                    "reliability": "medium",
                    "max_cpu": 64,
                    "max_memory": 256,
                    "max_storage": 5000,
                    "supports_ingress": True,
                    "supports_load_balancer": True,
                    "supports_auto_scaling": True,
                    "supports_high_availability": True,
                    "supported_features": [
                        "kubernetes", "virtualization", "storage_arrays",
                        "load_balancing", "monitoring"
                    ]
                }
            },
            "hybrid": {
                "type": "hybrid",
                "description": "Hybrid cloud/on-premise deployment environment",
                "category": "hybrid",
                "capabilities": {
                    "scalability": "high",
                    "reliability": "high",
                    "max_cpu": 128,
                    "max_memory": 512,
                    "max_storage": 10000,
                    "supports_ingress": True,
                    "supports_load_balancer": True,
                    "supports_auto_scaling": True,
                    "supports_high_availability": True,
                    "supported_features": [
                        "kubernetes", "multi-cloud", "cloud_bursting",
                        "load_balancing", "auto_scaling", "monitoring",
                        "data_replication"
                    ]
                }
            }
        }
    
    def _auto_detect_environment(self, 
                               deployment_manifest: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-detect the most suitable environment based on manifest and context.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            
        Returns:
            Dict containing the detected environment
        """
        # Initialize scores for each environment type
        environment_scores = {
            env_type: 0 for env_type in self.environment_definitions.keys()
        }
        
        # Score based on requirements
        requirements = deployment_manifest.get("requirements", {})
        
        # Compute requirements
        if "compute" in requirements:
            compute_req = requirements["compute"]
            
            # CPU requirements
            if "min_cpu" in compute_req:
                min_cpu = compute_req["min_cpu"]
                for env_type, env_details in self.environment_definitions.items():
                    max_cpu = env_details.get("capabilities", {}).get("max_cpu", 0)
                    if max_cpu >= min_cpu:
                        environment_scores[env_type] += 10
                    else:
                        environment_scores[env_type] -= 50  # Significant penalty for not meeting minimum requirements
            
            # Memory requirements
            if "min_memory" in compute_req:
                min_memory = compute_req["min_memory"]
                for env_type, env_details in self.environment_definitions.items():
                    max_memory = env_details.get("capabilities", {}).get("max_memory", 0)
                    if max_memory >= min_memory:
                        environment_scores[env_type] += 10
                    else:
                        environment_scores[env_type] -= 50
        
        # Storage requirements
        if "storage" in requirements:
            storage_req = requirements["storage"]
            
            # Capacity requirements
            if "min_capacity" in storage_req:
                min_capacity = storage_req["min_capacity"]
                for env_type, env_details in self.environment_definitions.items():
                    max_storage = env_details.get("capabilities", {}).get("max_storage", 0)
                    if max_storage >= min_capacity:
                        environment_scores[env_type] += 10
                    else:
                        environment_scores[env_type] -= 50
        
        # Networking requirements
        if "networking" in requirements:
            network_req = requirements["networking"]
            
            # Ingress requirements
            if network_req.get("ingress", False):
                for env_type, env_details in self.environment_definitions.items():
                    if env_details.get("capabilities", {}).get("supports_ingress", False):
                        environment_scores[env_type] += 10
                    else:
                        environment_scores[env_type] -= 30
            
            # Load balancer requirements
            if network_req.get("load_balancer", False):
                for env_type, env_details in self.environment_definitions.items():
                    if env_details.get("capabilities", {}).get("supports_load_balancer", False):
                        environment_scores[env_type] += 10
                    else:
                        environment_scores[env_type] -= 20
        
        # Feature requirements
        if "features" in requirements:
            for feature in requirements["features"]:
                for env_type, env_details in self.environment_definitions.items():
                    supported_features = env_details.get("capabilities", {}).get("supported_features", [])
                    if feature in supported_features:
                        environment_scores[env_type] += 15
                    else:
                        environment_scores[env_type] -= 25
        
        # Score based on context
        
        # Industry context
        industry = context.get("industry")
        if industry:
            if industry in ["healthcare", "finance", "government"]:
                # These industries often prefer on-premise or hybrid for compliance
                environment_scores["on-premise"] += 20
                environment_scores["hybrid"] += 15
            elif industry in ["retail", "media", "technology"]:
                # These industries often prefer cloud for scalability
                environment_scores["cloud"] += 20
                environment_scores["hybrid"] += 10
            elif industry in ["manufacturing", "energy", "transportation"]:
                # These industries often have edge requirements
                environment_scores["edge"] += 20
                environment_scores["hybrid"] += 10
        
        # Region context
        region = context.get("region")
        if region:
            # Some regions may have specific preferences or constraints
            # This is a simplified example
            if region in ["eu", "europe"]:
                # European deployments might prefer on-premise for data sovereignty
                environment_scores["on-premise"] += 10
                environment_scores["hybrid"] += 5
        
        # Find the environment with the highest score
        best_environment = max(environment_scores.items(), key=lambda x: x[1])
        environment_type = best_environment[0]
        score = best_environment[1]
        
        # Calculate confidence level (0-100%)
        total_score = sum(abs(s) for s in environment_scores.values())
        confidence = (score / total_score * 100) if total_score > 0 else 50
        
        # Get environment details
        environment_details = self.get_environment_details(environment_type)
        
        return {
            "environment_type": environment_type,
            "environment_details": environment_details,
            "confidence": confidence,
            "scores": environment_scores
        }
