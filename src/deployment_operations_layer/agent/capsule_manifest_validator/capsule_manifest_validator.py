"""
Capsule Manifest Validator

This module is responsible for validating capsule manifests to ensure they meet all requirements
for deployment. It serves as a critical safeguard against deployment failures by verifying
that capsule manifests are complete, consistent, and compliant with organizational policies.

The Capsule Manifest Validator performs comprehensive validation of capsule manifests,
checking for required fields, proper formatting, dependency consistency, and compliance
with security and operational policies.
"""

import logging
import json
import hashlib
import time
import re
from typing import Dict, List, Any, Optional, Tuple, Set

from ...protocol.mcp_integration.mcp_context_schema import MCPContextSchema
from ...protocol.a2a_integration.a2a_agent_schema import A2AAgentSchema
from ..agent_utils import AgentBase

logger = logging.getLogger(__name__)

class CapsuleManifestValidator:
    """
    Validates capsule manifests to ensure they meet all requirements for deployment.
    
    This class serves as a critical safeguard against deployment failures by verifying
    that capsule manifests are complete, consistent, and compliant with organizational
    policies.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Capsule Manifest Validator.
        
        Args:
            config: Configuration dictionary for the validator
        """
        self.config = config or {}
        
        # Initialize validation rules
        self.validation_rules = self.config.get("validation_rules", {})
        if not self.validation_rules:
            self._initialize_default_validation_rules()
        
        # Initialize validation history
        self.validation_history = []
        
        # MCP/A2A integration
        self.mcp_schema = MCPContextSchema()
        self.a2a_schema = A2AAgentSchema()
        
        logger.info("Capsule Manifest Validator initialized")
    
    def _initialize_default_validation_rules(self):
        """
        Initialize default validation rules.
        """
        self.validation_rules = {
            "manifest": {
                "required_fields": [
                    "manifest_id",
                    "manifest_version",
                    "created_at",
                    "capsule_id",
                    "capsule_name",
                    "capsule_version",
                    "capsule_type",
                    "capabilities",
                    "requirements",
                    "dependencies",
                    "configuration",
                    "security",
                    "deployment"
                ],
                "version_format": r"^\d+\.\d+\.\d+$",  # Semantic versioning
                "id_format": r"^[a-zA-Z0-9_-]+$"  # Alphanumeric with underscore and hyphen
            },
            "capabilities": {
                "required_fields": [
                    "functions",
                    "protocols",
                    "interfaces"
                ],
                "max_capabilities": 50
            },
            "requirements": {
                "required_fields": [
                    "compute",
                    "storage",
                    "network",
                    "dependencies"
                ],
                "compute_required_fields": [
                    "cpu",
                    "memory",
                    "gpu"
                ],
                "storage_required_fields": [
                    "persistent",
                    "ephemeral"
                ],
                "network_required_fields": [
                    "ingress",
                    "egress",
                    "protocols"
                ]
            },
            "dependencies": {
                "circular_dependency_check": True,
                "version_compatibility_check": True,
                "max_dependencies": 20
            },
            "security": {
                "required_fields": [
                    "trust_requirements",
                    "authentication",
                    "authorization",
                    "encryption",
                    "compliance"
                ],
                "trust_required_fields": [
                    "minimum_trust_score",
                    "trust_zones",
                    "override_policy"
                ],
                "encryption_required_fields": [
                    "data_at_rest",
                    "data_in_transit"
                ]
            },
            "deployment": {
                "required_fields": [
                    "target_environments",
                    "scaling",
                    "health_checks",
                    "rollback_strategy"
                ],
                "environment_required_fields": [
                    "type",
                    "regions",
                    "constraints"
                ],
                "health_check_required_fields": [
                    "liveness",
                    "readiness",
                    "startup"
                ]
            }
        }
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a capsule manifest.
        
        Args:
            manifest: Capsule manifest dictionary
            
        Returns:
            Validation results dictionary
        """
        validation_id = f"manifest-validation-{int(time.time())}-{hashlib.md5(json.dumps(manifest).encode()).hexdigest()[:8]}"
        
        logger.info(f"Starting manifest validation: {validation_id}")
        
        # Initialize validation results
        validation_results = {
            "validation_id": validation_id,
            "timestamp": time.time(),
            "status": "pending",
            "manifest_id": manifest.get("manifest_id", "unknown"),
            "capsule_id": manifest.get("capsule_id", "unknown"),
            "validations": {},
            "issues": [],
            "recommendations": []
        }
        
        # Validate manifest structure
        structure_validation = self._validate_manifest_structure(manifest)
        validation_results["validations"]["structure"] = structure_validation
        validation_results["issues"].extend(structure_validation.get("issues", []))
        validation_results["recommendations"].extend(structure_validation.get("recommendations", []))
        
        # Validate capabilities
        if "capabilities" in manifest:
            capabilities_validation = self._validate_capabilities(manifest["capabilities"])
            validation_results["validations"]["capabilities"] = capabilities_validation
            validation_results["issues"].extend(capabilities_validation.get("issues", []))
            validation_results["recommendations"].extend(capabilities_validation.get("recommendations", []))
        
        # Validate requirements
        if "requirements" in manifest:
            requirements_validation = self._validate_requirements(manifest["requirements"])
            validation_results["validations"]["requirements"] = requirements_validation
            validation_results["issues"].extend(requirements_validation.get("issues", []))
            validation_results["recommendations"].extend(requirements_validation.get("recommendations", []))
        
        # Validate dependencies
        if "dependencies" in manifest:
            dependencies_validation = self._validate_dependencies(manifest["dependencies"])
            validation_results["validations"]["dependencies"] = dependencies_validation
            validation_results["issues"].extend(dependencies_validation.get("issues", []))
            validation_results["recommendations"].extend(dependencies_validation.get("recommendations", []))
        
        # Validate security
        if "security" in manifest:
            security_validation = self._validate_security(manifest["security"])
            validation_results["validations"]["security"] = security_validation
            validation_results["issues"].extend(security_validation.get("issues", []))
            validation_results["recommendations"].extend(security_validation.get("recommendations", []))
        
        # Validate deployment
        if "deployment" in manifest:
            deployment_validation = self._validate_deployment(manifest["deployment"])
            validation_results["validations"]["deployment"] = deployment_validation
            validation_results["issues"].extend(deployment_validation.get("issues", []))
            validation_results["recommendations"].extend(deployment_validation.get("recommendations", []))
        
        # Determine overall validation status
        if any(issue.get("severity") == "critical" for issue in validation_results["issues"]):
            validation_results["status"] = "failed"
        elif any(issue.get("severity") == "high" for issue in validation_results["issues"]):
            validation_results["status"] = "warning"
        else:
            validation_results["status"] = "passed"
        
        # Add to validation history
        self.validation_history.append({
            "validation_id": validation_id,
            "timestamp": validation_results["timestamp"],
            "manifest_id": validation_results["manifest_id"],
            "capsule_id": validation_results["capsule_id"],
            "status": validation_results["status"],
            "issue_count": len(validation_results["issues"])
        })
        
        logger.info(f"Manifest validation completed: {validation_id} - Status: {validation_results['status']}")
        
        return validation_results
    
    def _validate_manifest_structure(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate manifest structure.
        
        Args:
            manifest: Capsule manifest dictionary
            
        Returns:
            Validation results for manifest structure
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check required fields
        required_fields = self.validation_rules["manifest"]["required_fields"]
        for field in required_fields:
            if field not in manifest or not manifest[field]:
                results["issues"].append({
                    "type": "missing_field",
                    "component": "manifest",
                    "field": field,
                    "severity": "high",
                    "message": f"Required field '{field}' is missing or empty in manifest"
                })
        
        # Validate version format
        if "manifest_version" in manifest:
            version_format = self.validation_rules["manifest"]["version_format"]
            if not re.match(version_format, str(manifest["manifest_version"])):
                results["issues"].append({
                    "type": "invalid_version_format",
                    "component": "manifest",
                    "field": "manifest_version",
                    "severity": "medium",
                    "message": f"Manifest version '{manifest['manifest_version']}' does not match required format '{version_format}'"
                })
        
        if "capsule_version" in manifest:
            version_format = self.validation_rules["manifest"]["version_format"]
            if not re.match(version_format, str(manifest["capsule_version"])):
                results["issues"].append({
                    "type": "invalid_version_format",
                    "component": "manifest",
                    "field": "capsule_version",
                    "severity": "medium",
                    "message": f"Capsule version '{manifest['capsule_version']}' does not match required format '{version_format}'"
                })
        
        # Validate ID format
        if "manifest_id" in manifest:
            id_format = self.validation_rules["manifest"]["id_format"]
            if not re.match(id_format, str(manifest["manifest_id"])):
                results["issues"].append({
                    "type": "invalid_id_format",
                    "component": "manifest",
                    "field": "manifest_id",
                    "severity": "medium",
                    "message": f"Manifest ID '{manifest['manifest_id']}' does not match required format '{id_format}'"
                })
        
        if "capsule_id" in manifest:
            id_format = self.validation_rules["manifest"]["id_format"]
            if not re.match(id_format, str(manifest["capsule_id"])):
                results["issues"].append({
                    "type": "invalid_id_format",
                    "component": "manifest",
                    "field": "capsule_id",
                    "severity": "medium",
                    "message": f"Capsule ID '{manifest['capsule_id']}' does not match required format '{id_format}'"
                })
        
        # Validate created_at timestamp
        if "created_at" in manifest:
            try:
                created_at = float(manifest["created_at"])
                current_time = time.time()
                
                # Check if timestamp is in the future
                if created_at > current_time:
                    results["issues"].append({
                        "type": "future_timestamp",
                        "component": "manifest",
                        "field": "created_at",
                        "severity": "medium",
                        "message": f"Manifest creation timestamp is in the future"
                    })
                
                # Check if timestamp is too old (more than 1 year)
                if current_time - created_at > 365 * 24 * 60 * 60:
                    results["issues"].append({
                        "type": "old_manifest",
                        "component": "manifest",
                        "field": "created_at",
                        "severity": "low",
                        "message": f"Manifest is more than 1 year old"
                    })
                    
                    results["recommendations"].append({
                        "type": "update_manifest",
                        "component": "manifest",
                        "message": "Consider updating the manifest to ensure it meets current requirements"
                    })
            except (ValueError, TypeError):
                results["issues"].append({
                    "type": "invalid_timestamp",
                    "component": "manifest",
                    "field": "created_at",
                    "severity": "medium",
                    "message": f"Manifest creation timestamp is not a valid number"
                })
        
        # Validate capsule_type
        if "capsule_type" in manifest:
            valid_types = ["agent", "service", "utility", "infrastructure", "data", "ui", "integration", "security"]
            if manifest["capsule_type"] not in valid_types:
                results["issues"].append({
                    "type": "invalid_capsule_type",
                    "component": "manifest",
                    "field": "capsule_type",
                    "severity": "medium",
                    "message": f"Capsule type '{manifest['capsule_type']}' is not one of {valid_types}"
                })
        
        # Determine status
        if any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "medium" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _validate_capabilities(self, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate capabilities.
        
        Args:
            capabilities: Capabilities dictionary
            
        Returns:
            Validation results for capabilities
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check required fields
        required_fields = self.validation_rules["capabilities"]["required_fields"]
        for field in required_fields:
            if field not in capabilities or not capabilities[field]:
                results["issues"].append({
                    "type": "missing_field",
                    "component": "capabilities",
                    "field": field,
                    "severity": "medium",
                    "message": f"Required field '{field}' is missing or empty in capabilities"
                })
        
        # Check maximum capabilities
        max_capabilities = self.validation_rules["capabilities"]["max_capabilities"]
        total_capabilities = 0
        
        for field in ["functions", "protocols", "interfaces"]:
            if field in capabilities and isinstance(capabilities[field], list):
                total_capabilities += len(capabilities[field])
        
        if total_capabilities > max_capabilities:
            results["issues"].append({
                "type": "too_many_capabilities",
                "component": "capabilities",
                "count": total_capabilities,
                "max": max_capabilities,
                "severity": "medium",
                "message": f"Total capabilities ({total_capabilities}) exceeds maximum allowed ({max_capabilities})"
            })
            
            results["recommendations"].append({
                "type": "reduce_capabilities",
                "component": "capabilities",
                "message": f"Consider reducing the number of capabilities to improve performance and maintainability"
            })
        
        # Validate functions
        if "functions" in capabilities and isinstance(capabilities["functions"], list):
            for i, function in enumerate(capabilities["functions"]):
                if not isinstance(function, dict):
                    results["issues"].append({
                        "type": "invalid_function",
                        "component": "capabilities",
                        "index": i,
                        "severity": "medium",
                        "message": f"Function at index {i} is not a valid dictionary"
                    })
                    continue
                
                required_function_fields = ["id", "name", "description", "inputs", "outputs"]
                for field in required_function_fields:
                    if field not in function or not function[field]:
                        results["issues"].append({
                            "type": "missing_function_field",
                            "component": "capabilities",
                            "function_index": i,
                            "field": field,
                            "severity": "medium",
                            "message": f"Required field '{field}' is missing or empty in function at index {i}"
                        })
        
        # Validate protocols
        if "protocols" in capabilities and isinstance(capabilities["protocols"], list):
            for i, protocol in enumerate(capabilities["protocols"]):
                if not isinstance(protocol, dict):
                    results["issues"].append({
                        "type": "invalid_protocol",
                        "component": "capabilities",
                        "index": i,
                        "severity": "medium",
                        "message": f"Protocol at index {i} is not a valid dictionary"
                    })
                    continue
                
                required_protocol_fields = ["id", "name", "version", "specification"]
                for field in required_protocol_fields:
                    if field not in protocol or not protocol[field]:
                        results["issues"].append({
                            "type": "missing_protocol_field",
                            "component": "capabilities",
                            "protocol_index": i,
                            "field": field,
                            "severity": "medium",
                            "message": f"Required field '{field}' is missing or empty in protocol at index {i}"
                        })
        
        # Validate interfaces
        if "interfaces" in capabilities and isinstance(capabilities["interfaces"], list):
            for i, interface in enumerate(capabilities["interfaces"]):
                if not isinstance(interface, dict):
                    results["issues"].append({
                        "type": "invalid_interface",
                        "component": "capabilities",
                        "index": i,
                        "severity": "medium",
                        "message": f"Interface at index {i} is not a valid dictionary"
                    })
                    continue
                
                required_interface_fields = ["id", "name", "type", "endpoints"]
                for field in required_interface_fields:
                    if field not in interface or not interface[field]:
                        results["issues"].append({
                            "type": "missing_interface_field",
                            "component": "capabilities",
                            "interface_index": i,
                            "field": field,
                            "severity": "medium",
                            "message": f"Required field '{field}' is missing or empty in interface at index {i}"
                        })
        
        # Determine status
        if any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "medium" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate requirements.
        
        Args:
            requirements: Requirements dictionary
            
        Returns:
            Validation results for requirements
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check required fields
        required_fields = self.validation_rules["requirements"]["required_fields"]
        for field in required_fields:
            if field not in requirements or not requirements[field]:
                results["issues"].append({
                    "type": "missing_field",
                    "component": "requirements",
                    "field": field,
                    "severity": "high",
                    "message": f"Required field '{field}' is missing or empty in requirements"
                })
        
        # Validate compute requirements
        if "compute" in requirements and isinstance(requirements["compute"], dict):
            compute_required_fields = self.validation_rules["requirements"]["compute_required_fields"]
            for field in compute_required_fields:
                if field not in requirements["compute"]:
                    results["issues"].append({
                        "type": "missing_compute_field",
                        "component": "requirements",
                        "field": field,
                        "severity": "medium",
                        "message": f"Required field '{field}' is missing in compute requirements"
                    })
            
            # Validate CPU requirements
            if "cpu" in requirements["compute"]:
                try:
                    cpu = float(requirements["compute"]["cpu"])
                    if cpu <= 0:
                        results["issues"].append({
                            "type": "invalid_cpu_requirement",
                            "component": "requirements",
                            "value": cpu,
                            "severity": "medium",
                            "message": f"CPU requirement must be greater than 0, got {cpu}"
                        })
                except (ValueError, TypeError):
                    results["issues"].append({
                        "type": "invalid_cpu_requirement",
                        "component": "requirements",
                        "value": requirements["compute"]["cpu"],
                        "severity": "medium",
                        "message": f"CPU requirement must be a number, got {requirements['compute']['cpu']}"
                    })
            
            # Validate memory requirements
            if "memory" in requirements["compute"]:
                try:
                    memory = float(requirements["compute"]["memory"])
                    if memory <= 0:
                        results["issues"].append({
                            "type": "invalid_memory_requirement",
                            "component": "requirements",
                            "value": memory,
                            "severity": "medium",
                            "message": f"Memory requirement must be greater than 0, got {memory}"
                        })
                except (ValueError, TypeError):
                    results["issues"].append({
                        "type": "invalid_memory_requirement",
                        "component": "requirements",
                        "value": requirements["compute"]["memory"],
                        "severity": "medium",
                        "message": f"Memory requirement must be a number, got {requirements['compute']['memory']}"
                    })
        
        # Validate storage requirements
        if "storage" in requirements and isinstance(requirements["storage"], dict):
            storage_required_fields = self.validation_rules["requirements"]["storage_required_fields"]
            for field in storage_required_fields:
                if field not in requirements["storage"]:
                    results["issues"].append({
                        "type": "missing_storage_field",
                        "component": "requirements",
                        "field": field,
                        "severity": "medium",
                        "message": f"Required field '{field}' is missing in storage requirements"
                    })
            
            # Validate persistent storage requirements
            if "persistent" in requirements["storage"]:
                try:
                    persistent = float(requirements["storage"]["persistent"])
                    if persistent < 0:
                        results["issues"].append({
                            "type": "invalid_persistent_storage_requirement",
                            "component": "requirements",
                            "value": persistent,
                            "severity": "medium",
                            "message": f"Persistent storage requirement must be non-negative, got {persistent}"
                        })
                except (ValueError, TypeError):
                    results["issues"].append({
                        "type": "invalid_persistent_storage_requirement",
                        "component": "requirements",
                        "value": requirements["storage"]["persistent"],
                        "severity": "medium",
                        "message": f"Persistent storage requirement must be a number, got {requirements['storage']['persistent']}"
                    })
        
        # Validate network requirements
        if "network" in requirements and isinstance(requirements["network"], dict):
            network_required_fields = self.validation_rules["requirements"]["network_required_fields"]
            for field in network_required_fields:
                if field not in requirements["network"]:
                    results["issues"].append({
                        "type": "missing_network_field",
                        "component": "requirements",
                        "field": field,
                        "severity": "medium",
                        "message": f"Required field '{field}' is missing in network requirements"
                    })
            
            # Validate protocols
            if "protocols" in requirements["network"] and isinstance(requirements["network"]["protocols"], list):
                valid_protocols = ["tcp", "udp", "http", "https", "grpc", "websocket", "mqtt", "amqp"]
                for protocol in requirements["network"]["protocols"]:
                    if protocol not in valid_protocols:
                        results["issues"].append({
                            "type": "invalid_network_protocol",
                            "component": "requirements",
                            "protocol": protocol,
                            "severity": "low",
                            "message": f"Network protocol '{protocol}' is not one of {valid_protocols}"
                        })
        
        # Determine status
        if any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "medium" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _validate_dependencies(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate dependencies.
        
        Args:
            dependencies: Dependencies dictionary
            
        Returns:
            Validation results for dependencies
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check maximum dependencies
        max_dependencies = self.validation_rules["dependencies"]["max_dependencies"]
        if isinstance(dependencies, dict) and len(dependencies) > max_dependencies:
            results["issues"].append({
                "type": "too_many_dependencies",
                "component": "dependencies",
                "count": len(dependencies),
                "max": max_dependencies,
                "severity": "medium",
                "message": f"Number of dependencies ({len(dependencies)}) exceeds maximum allowed ({max_dependencies})"
            })
            
            results["recommendations"].append({
                "type": "reduce_dependencies",
                "component": "dependencies",
                "message": f"Consider reducing the number of dependencies to improve maintainability and reduce complexity"
            })
        
        # Check for circular dependencies
        if self.validation_rules["dependencies"]["circular_dependency_check"]:
            circular_deps = self._detect_circular_dependencies(dependencies)
            for dep_chain in circular_deps:
                results["issues"].append({
                    "type": "circular_dependency",
                    "component": "dependencies",
                    "dependency_chain": dep_chain,
                    "severity": "critical",
                    "message": f"Circular dependency detected: {' -> '.join(dep_chain)}"
                })
        
        # Validate dependency details
        if isinstance(dependencies, dict):
            for dep_id, dep_info in dependencies.items():
                if not isinstance(dep_info, dict):
                    results["issues"].append({
                        "type": "invalid_dependency",
                        "component": "dependencies",
                        "dependency_id": dep_id,
                        "severity": "high",
                        "message": f"Dependency '{dep_id}' is not a valid dictionary"
                    })
                    continue
                
                required_dep_fields = ["version", "type", "optional"]
                for field in required_dep_fields:
                    if field not in dep_info:
                        results["issues"].append({
                            "type": "missing_dependency_field",
                            "component": "dependencies",
                            "dependency_id": dep_id,
                            "field": field,
                            "severity": "medium",
                            "message": f"Required field '{field}' is missing in dependency '{dep_id}'"
                        })
                
                # Validate version format
                if "version" in dep_info:
                    version_format = self.validation_rules["manifest"]["version_format"]
                    if not re.match(version_format, str(dep_info["version"])):
                        results["issues"].append({
                            "type": "invalid_version_format",
                            "component": "dependencies",
                            "dependency_id": dep_id,
                            "field": "version",
                            "severity": "medium",
                            "message": f"Dependency version '{dep_info['version']}' does not match required format '{version_format}'"
                        })
                
                # Validate dependency type
                if "type" in dep_info:
                    valid_types = ["runtime", "build", "test", "optional"]
                    if dep_info["type"] not in valid_types:
                        results["issues"].append({
                            "type": "invalid_dependency_type",
                            "component": "dependencies",
                            "dependency_id": dep_id,
                            "type": dep_info["type"],
                            "severity": "medium",
                            "message": f"Dependency type '{dep_info['type']}' is not one of {valid_types}"
                        })
        
        # Determine status
        if any(issue["severity"] == "critical" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _validate_security(self, security: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate security.
        
        Args:
            security: Security dictionary
            
        Returns:
            Validation results for security
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check required fields
        required_fields = self.validation_rules["security"]["required_fields"]
        for field in required_fields:
            if field not in security or not security[field]:
                results["issues"].append({
                    "type": "missing_field",
                    "component": "security",
                    "field": field,
                    "severity": "high",
                    "message": f"Required field '{field}' is missing or empty in security"
                })
        
        # Validate trust requirements
        if "trust_requirements" in security and isinstance(security["trust_requirements"], dict):
            trust_required_fields = self.validation_rules["security"]["trust_required_fields"]
            for field in trust_required_fields:
                if field not in security["trust_requirements"] or not security["trust_requirements"][field]:
                    results["issues"].append({
                        "type": "missing_trust_field",
                        "component": "security",
                        "field": field,
                        "severity": "high",
                        "message": f"Required field '{field}' is missing or empty in trust requirements"
                    })
            
            # Validate minimum trust score
            if "minimum_trust_score" in security["trust_requirements"]:
                try:
                    trust_score = float(security["trust_requirements"]["minimum_trust_score"])
                    if trust_score < 0 or trust_score > 1:
                        results["issues"].append({
                            "type": "invalid_trust_score",
                            "component": "security",
                            "value": trust_score,
                            "severity": "high",
                            "message": f"Minimum trust score must be between 0 and 1, got {trust_score}"
                        })
                except (ValueError, TypeError):
                    results["issues"].append({
                        "type": "invalid_trust_score",
                        "component": "security",
                        "value": security["trust_requirements"]["minimum_trust_score"],
                        "severity": "high",
                        "message": f"Minimum trust score must be a number between 0 and 1"
                    })
            
            # Validate trust zones
            if "trust_zones" in security["trust_requirements"] and isinstance(security["trust_requirements"]["trust_zones"], list):
                valid_trust_zones = ["public", "private", "restricted", "confidential", "secret"]
                for zone in security["trust_requirements"]["trust_zones"]:
                    if zone not in valid_trust_zones:
                        results["issues"].append({
                            "type": "invalid_trust_zone",
                            "component": "security",
                            "zone": zone,
                            "severity": "medium",
                            "message": f"Trust zone '{zone}' is not one of {valid_trust_zones}"
                        })
        
        # Validate encryption
        if "encryption" in security and isinstance(security["encryption"], dict):
            encryption_required_fields = self.validation_rules["security"]["encryption_required_fields"]
            for field in encryption_required_fields:
                if field not in security["encryption"] or not security["encryption"][field]:
                    results["issues"].append({
                        "type": "missing_encryption_field",
                        "component": "security",
                        "field": field,
                        "severity": "high",
                        "message": f"Required field '{field}' is missing or empty in encryption"
                    })
            
            # Validate encryption algorithms
            valid_algorithms = ["AES-256-GCM", "AES-256-CBC", "ChaCha20-Poly1305", "RSA-2048", "RSA-4096", "ECDSA-P256", "ECDSA-P384", "Ed25519"]
            
            if "data_at_rest" in security["encryption"] and isinstance(security["encryption"]["data_at_rest"], dict):
                if "algorithm" in security["encryption"]["data_at_rest"]:
                    algorithm = security["encryption"]["data_at_rest"]["algorithm"]
                    if algorithm not in valid_algorithms:
                        results["issues"].append({
                            "type": "invalid_encryption_algorithm",
                            "component": "security",
                            "context": "data_at_rest",
                            "algorithm": algorithm,
                            "severity": "high",
                            "message": f"Encryption algorithm '{algorithm}' for data at rest is not one of {valid_algorithms}"
                        })
            
            if "data_in_transit" in security["encryption"] and isinstance(security["encryption"]["data_in_transit"], dict):
                if "algorithm" in security["encryption"]["data_in_transit"]:
                    algorithm = security["encryption"]["data_in_transit"]["algorithm"]
                    if algorithm not in valid_algorithms:
                        results["issues"].append({
                            "type": "invalid_encryption_algorithm",
                            "component": "security",
                            "context": "data_in_transit",
                            "algorithm": algorithm,
                            "severity": "high",
                            "message": f"Encryption algorithm '{algorithm}' for data in transit is not one of {valid_algorithms}"
                        })
        
        # Validate compliance
        if "compliance" in security and isinstance(security["compliance"], dict):
            if "regulations" in security["compliance"] and isinstance(security["compliance"]["regulations"], list):
                for regulation in security["compliance"]["regulations"]:
                    if not isinstance(regulation, dict):
                        continue
                    
                    required_regulation_fields = ["id", "name", "version", "status"]
                    for field in required_regulation_fields:
                        if field not in regulation or not regulation[field]:
                            results["issues"].append({
                                "type": "missing_regulation_field",
                                "component": "security",
                                "regulation": regulation.get("name", "unknown"),
                                "field": field,
                                "severity": "medium",
                                "message": f"Required field '{field}' is missing or empty in regulation '{regulation.get('name', 'unknown')}'"
                            })
        
        # Determine status
        if any(issue["severity"] == "critical" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _validate_deployment(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate deployment.
        
        Args:
            deployment: Deployment dictionary
            
        Returns:
            Validation results for deployment
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check required fields
        required_fields = self.validation_rules["deployment"]["required_fields"]
        for field in required_fields:
            if field not in deployment or not deployment[field]:
                results["issues"].append({
                    "type": "missing_field",
                    "component": "deployment",
                    "field": field,
                    "severity": "high",
                    "message": f"Required field '{field}' is missing or empty in deployment"
                })
        
        # Validate target environments
        if "target_environments" in deployment and isinstance(deployment["target_environments"], list):
            for i, env in enumerate(deployment["target_environments"]):
                if not isinstance(env, dict):
                    results["issues"].append({
                        "type": "invalid_environment",
                        "component": "deployment",
                        "index": i,
                        "severity": "high",
                        "message": f"Environment at index {i} is not a valid dictionary"
                    })
                    continue
                
                environment_required_fields = self.validation_rules["deployment"]["environment_required_fields"]
                for field in environment_required_fields:
                    if field not in env or not env[field]:
                        results["issues"].append({
                            "type": "missing_environment_field",
                            "component": "deployment",
                            "environment_index": i,
                            "field": field,
                            "severity": "medium",
                            "message": f"Required field '{field}' is missing or empty in environment at index {i}"
                        })
                
                # Validate environment type
                if "type" in env:
                    valid_env_types = ["cloud", "edge", "hybrid", "on-premise", "multi-cloud"]
                    if env["type"] not in valid_env_types:
                        results["issues"].append({
                            "type": "invalid_environment_type",
                            "component": "deployment",
                            "environment_index": i,
                            "type": env["type"],
                            "severity": "medium",
                            "message": f"Environment type '{env['type']}' is not one of {valid_env_types}"
                        })
        
        # Validate health checks
        if "health_checks" in deployment and isinstance(deployment["health_checks"], dict):
            health_check_required_fields = self.validation_rules["deployment"]["health_check_required_fields"]
            for field in health_check_required_fields:
                if field not in deployment["health_checks"] or not deployment["health_checks"][field]:
                    results["issues"].append({
                        "type": "missing_health_check_field",
                        "component": "deployment",
                        "field": field,
                        "severity": "medium",
                        "message": f"Required field '{field}' is missing or empty in health checks"
                    })
            
            # Validate health check details
            for check_type in ["liveness", "readiness", "startup"]:
                if check_type in deployment["health_checks"] and isinstance(deployment["health_checks"][check_type], dict):
                    check = deployment["health_checks"][check_type]
                    
                    required_check_fields = ["path", "port", "initial_delay_seconds", "period_seconds", "timeout_seconds", "success_threshold", "failure_threshold"]
                    for field in required_check_fields:
                        if field not in check:
                            results["issues"].append({
                                "type": "missing_health_check_detail",
                                "component": "deployment",
                                "check_type": check_type,
                                "field": field,
                                "severity": "medium",
                                "message": f"Required field '{field}' is missing in {check_type} health check"
                            })
        
        # Validate scaling
        if "scaling" in deployment and isinstance(deployment["scaling"], dict):
            required_scaling_fields = ["min_replicas", "max_replicas", "target_cpu_utilization_percentage"]
            for field in required_scaling_fields:
                if field not in deployment["scaling"]:
                    results["issues"].append({
                        "type": "missing_scaling_field",
                        "component": "deployment",
                        "field": field,
                        "severity": "medium",
                        "message": f"Required field '{field}' is missing in scaling"
                    })
            
            # Validate min and max replicas
            if "min_replicas" in deployment["scaling"] and "max_replicas" in deployment["scaling"]:
                try:
                    min_replicas = int(deployment["scaling"]["min_replicas"])
                    max_replicas = int(deployment["scaling"]["max_replicas"])
                    
                    if min_replicas < 0:
                        results["issues"].append({
                            "type": "invalid_min_replicas",
                            "component": "deployment",
                            "value": min_replicas,
                            "severity": "high",
                            "message": f"Minimum replicas must be non-negative, got {min_replicas}"
                        })
                    
                    if max_replicas < min_replicas:
                        results["issues"].append({
                            "type": "invalid_max_replicas",
                            "component": "deployment",
                            "min": min_replicas,
                            "max": max_replicas,
                            "severity": "high",
                            "message": f"Maximum replicas ({max_replicas}) must be greater than or equal to minimum replicas ({min_replicas})"
                        })
                except (ValueError, TypeError):
                    results["issues"].append({
                        "type": "invalid_replicas",
                        "component": "deployment",
                        "severity": "high",
                        "message": f"Replicas must be integers"
                    })
        
        # Validate rollback strategy
        if "rollback_strategy" in deployment and isinstance(deployment["rollback_strategy"], dict):
            required_rollback_fields = ["type", "timeout_seconds"]
            for field in required_rollback_fields:
                if field not in deployment["rollback_strategy"]:
                    results["issues"].append({
                        "type": "missing_rollback_field",
                        "component": "deployment",
                        "field": field,
                        "severity": "medium",
                        "message": f"Required field '{field}' is missing in rollback strategy"
                    })
            
            # Validate rollback type
            if "type" in deployment["rollback_strategy"]:
                valid_rollback_types = ["automatic", "manual", "gradual", "snapshot"]
                if deployment["rollback_strategy"]["type"] not in valid_rollback_types:
                    results["issues"].append({
                        "type": "invalid_rollback_type",
                        "component": "deployment",
                        "type": deployment["rollback_strategy"]["type"],
                        "severity": "medium",
                        "message": f"Rollback type '{deployment['rollback_strategy']['type']}' is not one of {valid_rollback_types}"
                    })
        
        # Determine status
        if any(issue["severity"] == "critical" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _detect_circular_dependencies(self, dependencies: Dict[str, Any]) -> List[List[str]]:
        """
        Detect circular dependencies in the dependency graph.
        
        Args:
            dependencies: Dictionary mapping dependency IDs to dependency information
            
        Returns:
            List of circular dependency chains
        """
        circular_deps = []
        visited = set()
        path = []
        
        # Build dependency graph
        graph = {}
        for dep_id, dep_info in dependencies.items():
            if isinstance(dep_info, dict) and "dependencies" in dep_info and isinstance(dep_info["dependencies"], list):
                graph[dep_id] = dep_info["dependencies"]
            else:
                graph[dep_id] = []
        
        def dfs(node):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                circular_deps.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for dep in graph.get(node, []):
                dfs(dep)
            
            path.pop()
        
        # Run DFS from each node
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return circular_deps
    
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """
        Get validation history.
        
        Returns:
            List of validation history entries
        """
        return self.validation_history
    
    def get_validation_result(self, validation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific validation result by ID.
        
        Args:
            validation_id: Validation ID
            
        Returns:
            Validation result dictionary or None if not found
        """
        # This would typically retrieve from a database or cache
        # For simplicity, we'll just return a placeholder
        return {
            "validation_id": validation_id,
            "timestamp": time.time(),
            "status": "passed",
            "manifest_id": "example-manifest",
            "capsule_id": "example-capsule",
            "validations": {},
            "issues": [],
            "recommendations": []
        }
    
    def generate_validation_report(self, validation_id: str) -> Dict[str, Any]:
        """
        Generate a detailed validation report.
        
        Args:
            validation_id: Validation ID
            
        Returns:
            Validation report dictionary
        """
        validation_result = self.get_validation_result(validation_id)
        
        if not validation_result:
            return {
                "status": "error",
                "message": f"Validation result not found for ID: {validation_id}"
            }
        
        # Generate report
        report = {
            "report_id": f"report-{validation_id}",
            "timestamp": time.time(),
            "validation_id": validation_id,
            "manifest_id": validation_result.get("manifest_id", "unknown"),
            "capsule_id": validation_result.get("capsule_id", "unknown"),
            "status": validation_result.get("status", "unknown"),
            "summary": self._generate_validation_summary(validation_result),
            "details": validation_result,
            "recommendations": validation_result.get("recommendations", [])
        }
        
        return report
    
    def _generate_validation_summary(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of validation results.
        
        Args:
            validation_result: Validation result dictionary
            
        Returns:
            Validation summary dictionary
        """
        issues = validation_result.get("issues", [])
        
        # Count issues by severity
        issue_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for issue in issues:
            severity = issue.get("severity", "low")
            issue_counts[severity] = issue_counts.get(severity, 0) + 1
        
        # Count issues by component
        component_counts = {}
        
        for issue in issues:
            component = issue.get("component", "unknown")
            component_counts[component] = component_counts.get(component, 0) + 1
        
        # Generate summary
        summary = {
            "status": validation_result.get("status", "unknown"),
            "issue_counts": issue_counts,
            "component_counts": component_counts,
            "total_issues": len(issues),
            "total_recommendations": len(validation_result.get("recommendations", [])),
            "pass_rate": self._calculate_pass_rate(validation_result)
        }
        
        return summary
    
    def _calculate_pass_rate(self, validation_result: Dict[str, Any]) -> float:
        """
        Calculate the pass rate for a validation result.
        
        Args:
            validation_result: Validation result dictionary
            
        Returns:
            Pass rate as a percentage
        """
        validations = validation_result.get("validations", {})
        
        if not validations:
            return 0.0
        
        passed = 0
        total = 0
        
        for component, result in validations.items():
            total += 1
            if result.get("status") == "passed":
                passed += 1
        
        return (passed / total * 100) if total > 0 else 0.0
