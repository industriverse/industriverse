"""
Compliance Policy Manager

This module is responsible for managing compliance policy sets used for validation.
It provides functionality to create, retrieve, update, and delete policy sets,
as well as to import and export policies in various formats.
"""

import logging
import json
import os
import time
import uuid
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class CompliancePolicyManager:
    """
    Manages compliance policy sets used for validation.
    
    This class provides functionality to create, retrieve, update, and delete policy sets,
    as well as to import and export policies in various formats. It maintains a registry
    of available policy sets and ensures their integrity and versioning.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Compliance Policy Manager.
        
        Args:
            config: Configuration dictionary for the policy manager
        """
        self.config = config or {}
        
        # Policy storage directory
        self.policy_dir = self.config.get("policy_dir", "/tmp/compliance_policies")
        os.makedirs(self.policy_dir, exist_ok=True)
        
        # Policy registry
        self.policy_registry = {}
        
        # Load built-in policies
        self._load_built_in_policies()
        
        # Load custom policies
        self._load_custom_policies()
        
        logger.info("Compliance Policy Manager initialized")
    
    def _load_built_in_policies(self):
        """
        Load built-in policy sets.
        """
        # Define built-in policy sets
        built_in_policies = {
            "default": self._create_default_policy_set(),
            "kubernetes": self._create_kubernetes_policy_set(),
            "edge": self._create_edge_policy_set(),
            "cloud": self._create_cloud_policy_set()
        }
        
        # Add to registry
        for policy_id, policy_set in built_in_policies.items():
            self.policy_registry[policy_id] = policy_set
        
        logger.info(f"Loaded {len(built_in_policies)} built-in policy sets")
    
    def _load_custom_policies(self):
        """
        Load custom policy sets from the policy directory.
        """
        # Find all JSON files in the policy directory
        policy_files = [f for f in os.listdir(self.policy_dir) if f.endswith(".json")]
        
        # Load each policy file
        for file_name in policy_files:
            file_path = os.path.join(self.policy_dir, file_name)
            try:
                with open(file_path, 'r') as f:
                    policy_set = json.load(f)
                
                # Validate policy set
                if self._validate_policy_set(policy_set):
                    policy_id = policy_set.get("id")
                    self.policy_registry[policy_id] = policy_set
                    logger.info(f"Loaded custom policy set: {policy_id}")
                else:
                    logger.warning(f"Invalid policy set in file: {file_path}")
            
            except Exception as e:
                logger.error(f"Error loading policy set from file {file_path}: {e}")
        
        logger.info(f"Loaded {len(policy_files)} custom policy sets")
    
    def _validate_policy_set(self, policy_set: Dict[str, Any]) -> bool:
        """
        Validate a policy set.
        
        Args:
            policy_set: Policy set to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["id", "name", "version", "policies"]
        for field in required_fields:
            if field not in policy_set:
                logger.warning(f"Policy set missing required field: {field}")
                return False
        
        # Check policies
        policies = policy_set.get("policies", [])
        if not isinstance(policies, list):
            logger.warning("Policies must be a list")
            return False
        
        # Validate each policy
        for policy in policies:
            if not self._validate_policy(policy):
                return False
        
        return True
    
    def _validate_policy(self, policy: Dict[str, Any]) -> bool:
        """
        Validate a policy.
        
        Args:
            policy: Policy to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["id", "name", "type", "severity"]
        for field in required_fields:
            if field not in policy:
                logger.warning(f"Policy missing required field: {field}")
                return False
        
        # Check severity
        valid_severities = ["high", "medium", "low"]
        if policy.get("severity") not in valid_severities:
            logger.warning(f"Invalid severity: {policy.get('severity')}")
            return False
        
        # Check type
        valid_types = ["security", "data_protection", "regulatory", "operational"]
        if policy.get("type") not in valid_types:
            logger.warning(f"Invalid policy type: {policy.get('type')}")
            return False
        
        # Validate rules if present
        rules = policy.get("rules", [])
        if rules and not isinstance(rules, list):
            logger.warning("Rules must be a list")
            return False
        
        for rule in rules:
            if not self._validate_rule(rule):
                return False
        
        return True
    
    def _validate_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Validate a rule.
        
        Args:
            rule: Rule to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["id", "type"]
        for field in required_fields:
            if field not in rule:
                logger.warning(f"Rule missing required field: {field}")
                return False
        
        # Check type
        valid_types = ["resource_check", "configuration_check", "evidence_check", "environment_check"]
        if rule.get("type") not in valid_types:
            logger.warning(f"Invalid rule type: {rule.get('type')}")
            return False
        
        # Type-specific validation
        rule_type = rule.get("type")
        
        if rule_type == "resource_check":
            if "resource_type" not in rule or "resource_property" not in rule:
                logger.warning("Resource check rule missing required fields")
                return False
        
        elif rule_type == "configuration_check":
            if "config_path" not in rule:
                logger.warning("Configuration check rule missing required fields")
                return False
        
        elif rule_type == "evidence_check":
            if "evidence_type" not in rule or "evidence_property" not in rule:
                logger.warning("Evidence check rule missing required fields")
                return False
        
        elif rule_type == "environment_check":
            if "env_property" not in rule:
                logger.warning("Environment check rule missing required fields")
                return False
        
        return True
    
    def get_policy_set(self, policy_set_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a policy set by ID.
        
        Args:
            policy_set_id: ID of the policy set to retrieve
            
        Returns:
            Policy set dictionary or None if not found
        """
        return self.policy_registry.get(policy_set_id)
    
    def list_policy_sets(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available policy sets.
        
        Returns:
            Dictionary of policy set IDs to policy sets
        """
        return self.policy_registry
    
    def create_policy_set(self, policy_set: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new policy set.
        
        Args:
            policy_set: Policy set to create
            
        Returns:
            Created policy set with generated ID and timestamp
        """
        # Generate ID if not provided
        if "id" not in policy_set:
            policy_set["id"] = str(uuid.uuid4())
        
        # Add timestamp
        policy_set["created_at"] = time.time()
        policy_set["updated_at"] = time.time()
        
        # Validate policy set
        if not self._validate_policy_set(policy_set):
            raise ValueError("Invalid policy set")
        
        # Add to registry
        self.policy_registry[policy_set["id"]] = policy_set
        
        # Save to file
        self._save_policy_set(policy_set)
        
        logger.info(f"Created policy set: {policy_set['id']}")
        
        return policy_set
    
    def update_policy_set(self, policy_set_id: str, policy_set: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing policy set.
        
        Args:
            policy_set_id: ID of the policy set to update
            policy_set: Updated policy set
            
        Returns:
            Updated policy set
        """
        # Check if policy set exists
        if policy_set_id not in self.policy_registry:
            raise ValueError(f"Policy set not found: {policy_set_id}")
        
        # Ensure ID matches
        if "id" in policy_set and policy_set["id"] != policy_set_id:
            raise ValueError("Policy set ID mismatch")
        
        policy_set["id"] = policy_set_id
        
        # Update timestamp
        policy_set["updated_at"] = time.time()
        
        # Preserve creation timestamp
        if "created_at" not in policy_set:
            policy_set["created_at"] = self.policy_registry[policy_set_id].get("created_at", time.time())
        
        # Validate policy set
        if not self._validate_policy_set(policy_set):
            raise ValueError("Invalid policy set")
        
        # Update registry
        self.policy_registry[policy_set_id] = policy_set
        
        # Save to file
        self._save_policy_set(policy_set)
        
        logger.info(f"Updated policy set: {policy_set_id}")
        
        return policy_set
    
    def delete_policy_set(self, policy_set_id: str) -> bool:
        """
        Delete a policy set.
        
        Args:
            policy_set_id: ID of the policy set to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Check if policy set exists
        if policy_set_id not in self.policy_registry:
            return False
        
        # Check if built-in
        policy_set = self.policy_registry[policy_set_id]
        if policy_set.get("built_in", False):
            logger.warning(f"Cannot delete built-in policy set: {policy_set_id}")
            return False
        
        # Remove from registry
        del self.policy_registry[policy_set_id]
        
        # Delete file
        file_path = os.path.join(self.policy_dir, f"{policy_set_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logger.info(f"Deleted policy set: {policy_set_id}")
        
        return True
    
    def _save_policy_set(self, policy_set: Dict[str, Any]):
        """
        Save a policy set to file.
        
        Args:
            policy_set: Policy set to save
        """
        # Skip if built-in
        if policy_set.get("built_in", False):
            return
        
        # Create file path
        file_path = os.path.join(self.policy_dir, f"{policy_set['id']}.json")
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(policy_set, f, indent=2)
        
        logger.info(f"Saved policy set to file: {file_path}")
    
    def import_policy_set(self, file_path: str) -> Dict[str, Any]:
        """
        Import a policy set from a file.
        
        Args:
            file_path: Path to the policy set file
            
        Returns:
            Imported policy set
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Load policy set from file
        with open(file_path, 'r') as f:
            policy_set = json.load(f)
        
        # Validate policy set
        if not self._validate_policy_set(policy_set):
            raise ValueError("Invalid policy set")
        
        # Add to registry
        self.policy_registry[policy_set["id"]] = policy_set
        
        # Save to policy directory
        self._save_policy_set(policy_set)
        
        logger.info(f"Imported policy set: {policy_set['id']}")
        
        return policy_set
    
    def export_policy_set(self, policy_set_id: str, file_path: str) -> bool:
        """
        Export a policy set to a file.
        
        Args:
            policy_set_id: ID of the policy set to export
            file_path: Path to save the policy set
            
        Returns:
            True if exported, False if not found
        """
        # Check if policy set exists
        if policy_set_id not in self.policy_registry:
            return False
        
        # Get policy set
        policy_set = self.policy_registry[policy_set_id]
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(policy_set, f, indent=2)
        
        logger.info(f"Exported policy set {policy_set_id} to file: {file_path}")
        
        return True
    
    def _create_default_policy_set(self) -> Dict[str, Any]:
        """
        Create the default policy set.
        
        Returns:
            Default policy set
        """
        return {
            "id": "default",
            "name": "Default Policy Set",
            "version": "1.0.0",
            "description": "Default policy set for general compliance validation",
            "built_in": True,
            "metadata": {
                "environment_type": "general",
                "is_edge": False,
                "region": "global",
                "industry": "general"
            },
            "policies": [
                {
                    "id": "security-001",
                    "name": "Basic Security Controls",
                    "type": "security",
                    "severity": "high",
                    "description": "Ensures basic security controls are implemented",
                    "require_secure_communication": True,
                    "require_authentication": True,
                    "require_authorization": True,
                    "required_controls": [
                        "access_control",
                        "encryption_in_transit",
                        "secure_configuration"
                    ],
                    "rules": [
                        {
                            "id": "security-001-rule-1",
                            "type": "configuration_check",
                            "config_path": "security.tls_enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        },
                        {
                            "id": "security-001-rule-2",
                            "type": "configuration_check",
                            "config_path": "security.authentication_enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "data-001",
                    "name": "Data Protection",
                    "type": "data_protection",
                    "severity": "medium",
                    "description": "Ensures data protection measures are implemented",
                    "require_encryption": True,
                    "require_data_classification": True,
                    "rules": [
                        {
                            "id": "data-001-rule-1",
                            "type": "configuration_check",
                            "config_path": "data.encryption_enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "operational-001",
                    "name": "Operational Controls",
                    "type": "operational",
                    "severity": "medium",
                    "description": "Ensures operational controls are implemented",
                    "require_monitoring": True,
                    "require_logging": True,
                    "rules": [
                        {
                            "id": "operational-001-rule-1",
                            "type": "configuration_check",
                            "config_path": "monitoring.enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        },
                        {
                            "id": "operational-001-rule-2",
                            "type": "configuration_check",
                            "config_path": "logging.enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        }
                    ]
                }
            ]
        }
    
    def _create_kubernetes_policy_set(self) -> Dict[str, Any]:
        """
        Create the Kubernetes policy set.
        
        Returns:
            Kubernetes policy set
        """
        return {
            "id": "kubernetes",
            "name": "Kubernetes Policy Set",
            "version": "1.0.0",
            "description": "Policy set for Kubernetes deployments",
            "built_in": True,
            "metadata": {
                "environment_type": "kubernetes",
                "is_edge": False,
                "region": "global",
                "industry": "general"
            },
            "policies": [
                {
                    "id": "k8s-security-001",
                    "name": "Kubernetes Security Controls",
                    "type": "security",
                    "severity": "high",
                    "description": "Ensures Kubernetes security controls are implemented",
                    "require_secure_communication": True,
                    "require_authentication": True,
                    "require_authorization": True,
                    "required_controls": [
                        "pod_security_policies",
                        "network_policies",
                        "rbac",
                        "secure_service_accounts"
                    ],
                    "rules": [
                        {
                            "id": "k8s-security-001-rule-1",
                            "type": "resource_check",
                            "resource_type": "NetworkPolicy",
                            "resource_property": "enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        },
                        {
                            "id": "k8s-security-001-rule-2",
                            "type": "resource_check",
                            "resource_type": "ServiceAccount",
                            "resource_property": "automountServiceAccountToken",
                            "expected_value": False,
                            "operator": "equals",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "k8s-operational-001",
                    "name": "Kubernetes Resource Management",
                    "type": "operational",
                    "severity": "medium",
                    "description": "Ensures Kubernetes resources are properly managed",
                    "require_resource_limits": True,
                    "rules": [
                        {
                            "id": "k8s-operational-001-rule-1",
                            "type": "resource_check",
                            "resource_type": "Pod",
                            "resource_property": "resources.limits",
                            "expected_value": None,
                            "operator": "not_equals",
                            "required": True
                        },
                        {
                            "id": "k8s-operational-001-rule-2",
                            "type": "resource_check",
                            "resource_type": "Pod",
                            "resource_property": "resources.requests",
                            "expected_value": None,
                            "operator": "not_equals",
                            "required": True
                        }
                    ]
                }
            ]
        }
    
    def _create_edge_policy_set(self) -> Dict[str, Any]:
        """
        Create the Edge policy set.
        
        Returns:
            Edge policy set
        """
        return {
            "id": "edge",
            "name": "Edge Computing Policy Set",
            "version": "1.0.0",
            "description": "Policy set for edge computing deployments",
            "built_in": True,
            "metadata": {
                "environment_type": "general",
                "is_edge": True,
                "region": "global",
                "industry": "general"
            },
            "policies": [
                {
                    "id": "edge-security-001",
                    "name": "Edge Security Controls",
                    "type": "security",
                    "severity": "high",
                    "description": "Ensures edge security controls are implemented",
                    "require_secure_communication": True,
                    "require_authentication": True,
                    "required_controls": [
                        "device_authentication",
                        "secure_boot",
                        "encrypted_storage",
                        "secure_communication"
                    ],
                    "rules": [
                        {
                            "id": "edge-security-001-rule-1",
                            "type": "configuration_check",
                            "config_path": "security.secure_boot_enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        },
                        {
                            "id": "edge-security-001-rule-2",
                            "type": "configuration_check",
                            "config_path": "security.encrypted_storage_enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "edge-operational-001",
                    "name": "Edge Resource Management",
                    "type": "operational",
                    "severity": "high",
                    "description": "Ensures edge resources are properly managed",
                    "require_resource_limits": True,
                    "require_monitoring": True,
                    "rules": [
                        {
                            "id": "edge-operational-001-rule-1",
                            "type": "configuration_check",
                            "config_path": "resources.cpu_limit",
                            "expected_value": 0,
                            "operator": "greater_than",
                            "required": True
                        },
                        {
                            "id": "edge-operational-001-rule-2",
                            "type": "configuration_check",
                            "config_path": "resources.memory_limit",
                            "expected_value": 0,
                            "operator": "greater_than",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "edge-data-001",
                    "name": "Edge Data Management",
                    "type": "data_protection",
                    "severity": "medium",
                    "description": "Ensures edge data is properly managed",
                    "require_encryption": True,
                    "require_data_retention_policy": True,
                    "rules": [
                        {
                            "id": "edge-data-001-rule-1",
                            "type": "configuration_check",
                            "config_path": "data.local_storage_encryption",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        },
                        {
                            "id": "edge-data-001-rule-2",
                            "type": "configuration_check",
                            "config_path": "data.retention_days",
                            "expected_value": 0,
                            "operator": "greater_than",
                            "required": True
                        }
                    ]
                }
            ]
        }
    
    def _create_cloud_policy_set(self) -> Dict[str, Any]:
        """
        Create the Cloud policy set.
        
        Returns:
            Cloud policy set
        """
        return {
            "id": "cloud",
            "name": "Cloud Computing Policy Set",
            "version": "1.0.0",
            "description": "Policy set for cloud computing deployments",
            "built_in": True,
            "metadata": {
                "environment_type": "cloud",
                "is_edge": False,
                "region": "global",
                "industry": "general"
            },
            "policies": [
                {
                    "id": "cloud-security-001",
                    "name": "Cloud Security Controls",
                    "type": "security",
                    "severity": "high",
                    "description": "Ensures cloud security controls are implemented",
                    "require_secure_communication": True,
                    "require_authentication": True,
                    "require_authorization": True,
                    "required_controls": [
                        "identity_management",
                        "access_control",
                        "encryption",
                        "network_security"
                    ],
                    "rules": [
                        {
                            "id": "cloud-security-001-rule-1",
                            "type": "configuration_check",
                            "config_path": "security.identity_provider",
                            "expected_value": None,
                            "operator": "not_equals",
                            "required": True
                        },
                        {
                            "id": "cloud-security-001-rule-2",
                            "type": "configuration_check",
                            "config_path": "security.network_acls_enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "cloud-data-001",
                    "name": "Cloud Data Protection",
                    "type": "data_protection",
                    "severity": "high",
                    "description": "Ensures cloud data protection measures are implemented",
                    "require_encryption": True,
                    "require_data_classification": True,
                    "require_data_backup": True,
                    "rules": [
                        {
                            "id": "cloud-data-001-rule-1",
                            "type": "configuration_check",
                            "config_path": "data.encryption_at_rest",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        },
                        {
                            "id": "cloud-data-001-rule-2",
                            "type": "configuration_check",
                            "config_path": "data.backup_enabled",
                            "expected_value": True,
                            "operator": "equals",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "cloud-regulatory-001",
                    "name": "Cloud Regulatory Compliance",
                    "type": "regulatory",
                    "severity": "medium",
                    "description": "Ensures cloud deployments comply with regulatory requirements",
                    "required_frameworks": [
                        "gdpr",
                        "hipaa",
                        "pci-dss"
                    ],
                    "rules": [
                        {
                            "id": "cloud-regulatory-001-rule-1",
                            "type": "evidence_check",
                            "evidence_type": "regulatory",
                            "evidence_property": "implemented_frameworks",
                            "expected_value": "gdpr",
                            "operator": "contains",
                            "required": False
                        }
                    ]
                }
            ]
        }
    
    def create_custom_policy_set(self, 
                                name: str,
                                description: str,
                                environment_type: str,
                                is_edge: bool,
                                region: str,
                                industry: str,
                                policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a custom policy set.
        
        Args:
            name: Name of the policy set
            description: Description of the policy set
            environment_type: Type of environment (kubernetes, cloud, etc.)
            is_edge: Whether the policy set is for edge deployments
            region: Region for the policy set
            industry: Industry for the policy set
            policies: List of policies
            
        Returns:
            Created policy set
        """
        # Create policy set
        policy_set = {
            "id": str(uuid.uuid4()),
            "name": name,
            "version": "1.0.0",
            "description": description,
            "built_in": False,
            "metadata": {
                "environment_type": environment_type,
                "is_edge": is_edge,
                "region": region,
                "industry": industry
            },
            "policies": policies
        }
        
        # Validate and create
        return self.create_policy_set(policy_set)
