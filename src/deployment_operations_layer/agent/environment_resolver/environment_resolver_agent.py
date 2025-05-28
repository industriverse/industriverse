"""
Environment Resolver Agent

This agent is responsible for resolving deployment environments and their capabilities.
It determines the appropriate environment for deployment based on requirements and
constraints, and provides environment-specific configuration and adaptation.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any

from .environment_detector import EnvironmentDetector
from .capability_analyzer import CapabilityAnalyzer
from .environment_adapter import EnvironmentAdapter
from .resource_calculator import ResourceCalculator

logger = logging.getLogger(__name__)

class EnvironmentResolverAgent:
    """
    Agent responsible for resolving deployment environments.
    """
    
    def __init__(self, 
                 detector: Optional[EnvironmentDetector] = None,
                 analyzer: Optional[CapabilityAnalyzer] = None,
                 adapter: Optional[EnvironmentAdapter] = None,
                 calculator: Optional[ResourceCalculator] = None):
        """
        Initialize the Environment Resolver Agent.
        
        Args:
            detector: Detector for environment types
            analyzer: Analyzer for environment capabilities
            adapter: Adapter for environment-specific configurations
            calculator: Calculator for environment resources
        """
        self.detector = detector or EnvironmentDetector()
        self.analyzer = analyzer or CapabilityAnalyzer()
        self.adapter = adapter or EnvironmentAdapter()
        self.calculator = calculator or ResourceCalculator()
        self.resolution_history = {}
        logger.info("Environment Resolver Agent initialized")
    
    def resolve_environment(self, 
                          deployment_manifest: Dict[str, Any], 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve the deployment environment based on manifest and context.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            
        Returns:
            Dict containing the resolved environment
        """
        logger.info(f"Resolving environment for deployment: {deployment_manifest.get('name', 'unnamed')}")
        
        # Generate a unique ID for this resolution operation
        resolution_id = str(uuid.uuid4())
        self.resolution_history[resolution_id] = {
            "status": "started",
            "manifest": deployment_manifest,
            "context": context,
            "timestamp": {
                "start": self._get_timestamp()
            }
        }
        
        try:
            # Detect environment type
            detection_result = self.detector.detect_environment(deployment_manifest, context)
            if not detection_result["success"]:
                logger.error(f"Failed to detect environment: {detection_result['error']}")
                self._update_resolution_status(resolution_id, "failed", {
                    "error": f"Failed to detect environment: {detection_result['error']}"
                })
                return {
                    "success": False,
                    "resolution_id": resolution_id,
                    "error": f"Failed to detect environment: {detection_result['error']}"
                }
            
            environment_type = detection_result["environment_type"]
            environment_details = detection_result["environment_details"]
            
            # Analyze environment capabilities
            capability_result = self.analyzer.analyze_capabilities(environment_type, environment_details, deployment_manifest)
            if not capability_result["success"]:
                logger.error(f"Failed to analyze capabilities: {capability_result['error']}")
                self._update_resolution_status(resolution_id, "failed", {
                    "error": f"Failed to analyze capabilities: {capability_result['error']}"
                })
                return {
                    "success": False,
                    "resolution_id": resolution_id,
                    "error": f"Failed to analyze capabilities: {capability_result['error']}"
                }
            
            capabilities = capability_result["capabilities"]
            
            # Calculate resource requirements
            resource_result = self.calculator.calculate_resources(deployment_manifest, environment_type, capabilities)
            if not resource_result["success"]:
                logger.error(f"Failed to calculate resources: {resource_result['error']}")
                self._update_resolution_status(resolution_id, "failed", {
                    "error": f"Failed to calculate resources: {resource_result['error']}"
                })
                return {
                    "success": False,
                    "resolution_id": resolution_id,
                    "error": f"Failed to calculate resources: {resource_result['error']}"
                }
            
            resources = resource_result["resources"]
            
            # Adapt deployment for environment
            adaptation_result = self.adapter.adapt_for_environment(
                deployment_manifest, environment_type, capabilities, resources
            )
            if not adaptation_result["success"]:
                logger.error(f"Failed to adapt for environment: {adaptation_result['error']}")
                self._update_resolution_status(resolution_id, "failed", {
                    "error": f"Failed to adapt for environment: {adaptation_result['error']}"
                })
                return {
                    "success": False,
                    "resolution_id": resolution_id,
                    "error": f"Failed to adapt for environment: {adaptation_result['error']}"
                }
            
            adaptations = adaptation_result["adaptations"]
            
            # Prepare result
            result = {
                "success": True,
                "resolution_id": resolution_id,
                "environment": {
                    "type": environment_type,
                    "details": environment_details,
                    "capabilities": capabilities,
                    "resources": resources,
                    "adaptations": adaptations
                }
            }
            
            # Update resolution history
            self._update_resolution_status(resolution_id, "completed", result)
            
            logger.info(f"Environment resolution completed successfully for deployment: {deployment_manifest.get('name', 'unnamed')}")
            return result
            
        except Exception as e:
            logger.exception(f"Error resolving environment: {str(e)}")
            self._update_resolution_status(resolution_id, "failed", {
                "error": str(e)
            })
            return {
                "success": False,
                "resolution_id": resolution_id,
                "error": str(e)
            }
    
    def validate_environment_compatibility(self, 
                                         deployment_manifest: Dict[str, Any], 
                                         environment_type: str) -> Dict[str, Any]:
        """
        Validate compatibility between a deployment and an environment.
        
        Args:
            deployment_manifest: Deployment manifest
            environment_type: Environment type to validate against
            
        Returns:
            Dict containing validation result
        """
        logger.info(f"Validating compatibility between deployment {deployment_manifest.get('name', 'unnamed')} and environment {environment_type}")
        
        try:
            # Get environment details
            environment_details = self.detector.get_environment_details(environment_type)
            
            # Analyze environment capabilities
            capability_result = self.analyzer.analyze_capabilities(environment_type, environment_details, deployment_manifest)
            if not capability_result["success"]:
                return {
                    "compatible": False,
                    "reason": f"Failed to analyze capabilities: {capability_result['error']}"
                }
            
            capabilities = capability_result["capabilities"]
            
            # Check deployment requirements against capabilities
            requirements = deployment_manifest.get("requirements", {})
            
            # Check compute requirements
            if "compute" in requirements:
                compute_req = requirements["compute"]
                if compute_req.get("min_cpu") and compute_req["min_cpu"] > capabilities.get("max_cpu", 0):
                    return {
                        "compatible": False,
                        "reason": f"CPU requirement ({compute_req['min_cpu']}) exceeds environment capability ({capabilities.get('max_cpu', 0)})"
                    }
                
                if compute_req.get("min_memory") and compute_req["min_memory"] > capabilities.get("max_memory", 0):
                    return {
                        "compatible": False,
                        "reason": f"Memory requirement ({compute_req['min_memory']}) exceeds environment capability ({capabilities.get('max_memory', 0)})"
                    }
            
            # Check storage requirements
            if "storage" in requirements:
                storage_req = requirements["storage"]
                if storage_req.get("min_capacity") and storage_req["min_capacity"] > capabilities.get("max_storage", 0):
                    return {
                        "compatible": False,
                        "reason": f"Storage requirement ({storage_req['min_capacity']}) exceeds environment capability ({capabilities.get('max_storage', 0)})"
                    }
            
            # Check networking requirements
            if "networking" in requirements:
                network_req = requirements["networking"]
                if network_req.get("ingress") and not capabilities.get("supports_ingress", False):
                    return {
                        "compatible": False,
                        "reason": "Environment does not support ingress networking"
                    }
                
                if network_req.get("load_balancer") and not capabilities.get("supports_load_balancer", False):
                    return {
                        "compatible": False,
                        "reason": "Environment does not support load balancers"
                    }
            
            # Check feature requirements
            if "features" in requirements:
                for feature in requirements["features"]:
                    if feature not in capabilities.get("supported_features", []):
                        return {
                            "compatible": False,
                            "reason": f"Environment does not support required feature: {feature}"
                        }
            
            return {
                "compatible": True,
                "environment_type": environment_type,
                "capabilities": capabilities
            }
            
        except Exception as e:
            logger.exception(f"Error validating environment compatibility: {str(e)}")
            return {
                "compatible": False,
                "reason": f"Error: {str(e)}"
            }
    
    def get_resolution_status(self, resolution_id: str) -> Dict[str, Any]:
        """
        Get the status of an environment resolution operation.
        
        Args:
            resolution_id: ID of the resolution operation
            
        Returns:
            Dict containing the resolution status
        """
        if resolution_id not in self.resolution_history:
            return {"error": "Resolution ID not found"}
        
        return self.resolution_history[resolution_id]
    
    def _update_resolution_status(self, 
                                resolution_id: str, 
                                status: str, 
                                details: Dict[str, Any] = None):
        """
        Update the status of an environment resolution operation.
        
        Args:
            resolution_id: ID of the resolution operation
            status: New status
            details: Additional details to add to the history
        """
        if resolution_id in self.resolution_history:
            self.resolution_history[resolution_id]["status"] = status
            
            if status in ["completed", "failed"]:
                self.resolution_history[resolution_id]["timestamp"]["end"] = self._get_timestamp()
            
            if details:
                self.resolution_history[resolution_id].update(details)
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
