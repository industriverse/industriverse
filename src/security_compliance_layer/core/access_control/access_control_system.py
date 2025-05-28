"""
Access Control System Module for the Security & Compliance Layer of Industriverse.

This module implements a comprehensive access control system that supports:
- Role-Based Access Control (RBAC)
- Attribute-Based Access Control (ABAC)
- Policy-Based Access Control (PBAC)
- Just-In-Time Access Provisioning
- Dynamic Permission Adjustment
- Trust-Based Access Control
- Context-Aware Access Decisions

The Access Control System is a core component of the Zero-Trust Security architecture,
providing fine-grained access control for all resources in the Industriverse ecosystem.
"""

import os
import time
import uuid
import json
import logging
import hashlib
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AccessControlSystem:
    """
    Core Access Control System for the Security & Compliance Layer.
    
    This class provides comprehensive access control services including:
    - Role-Based Access Control (RBAC)
    - Attribute-Based Access Control (ABAC)
    - Policy-Based Access Control (PBAC)
    - Just-In-Time Access Provisioning
    - Dynamic Permission Adjustment
    - Trust-Based Access Control
    - Context-Aware Access Decisions
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Access Control System with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.roles = {}
        self.permissions = {}
        self.policies = {}
        self.resources = {}
        self.access_decisions = {}
        self.jit_requests = {}
        self.trust_thresholds = {}
        
        # Initialize from configuration
        self._initialize_from_config()
        
        logger.info("Access Control System initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration
        """
        default_config = {
            "default_deny": True,
            "rbac_enabled": True,
            "abac_enabled": True,
            "pbac_enabled": True,
            "jit_enabled": True,
            "trust_based_enabled": True,
            "context_aware_enabled": True,
            "decision_cache_ttl": 300,  # 5 minutes
            "jit_request_ttl": 3600,    # 1 hour
            "default_trust_threshold": 0.7,
            "permission_levels": ["read", "write", "execute", "admin"],
            "context_factors": ["time", "location", "device", "network"]
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        return default_config
    
    def _initialize_from_config(self):
        """Initialize access control components from configuration."""
        # Initialize default roles if defined in config
        if "default_roles" in self.config:
            for role_name, role_config in self.config["default_roles"].items():
                self.create_role(role_name, role_config.get("description", ""), role_config.get("permissions", []))
        
        # Initialize default permissions if defined in config
        if "default_permissions" in self.config:
            for perm_name, perm_config in self.config["default_permissions"].items():
                self.create_permission(perm_name, perm_config.get("description", ""), perm_config.get("resource_type", ""))
        
        # Initialize default policies if defined in config
        if "default_policies" in self.config:
            for policy_name, policy_config in self.config["default_policies"].items():
                self.create_policy(
                    policy_name,
                    policy_config.get("description", ""),
                    policy_config.get("rules", []),
                    policy_config.get("effect", "allow")
                )
        
        # Initialize trust thresholds
        if "trust_thresholds" in self.config:
            self.trust_thresholds = self.config["trust_thresholds"]
        else:
            # Default trust thresholds for different permission levels
            self.trust_thresholds = {
                "read": 0.3,
                "write": 0.5,
                "execute": 0.7,
                "admin": 0.9
            }
    
    def create_role(self, name: str, description: str, permissions: List[str] = None) -> str:
        """
        Create a new role.
        
        Args:
            name: Role name
            description: Role description
            permissions: List of permission names
            
        Returns:
            Role ID
        """
        role_id = str(uuid.uuid4())
        
        role = {
            "id": role_id,
            "name": name,
            "description": description,
            "permissions": permissions or [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.roles[role_id] = role
        
        logger.info(f"Created role {name} with ID {role_id}")
        
        return role_id
    
    def update_role(self, role_id: str, name: str = None, description: str = None, permissions: List[str] = None) -> bool:
        """
        Update an existing role.
        
        Args:
            role_id: Role ID
            name: New role name
            description: New role description
            permissions: New list of permission names
            
        Returns:
            True if update successful, False otherwise
        """
        if role_id not in self.roles:
            logger.warning(f"Role {role_id} not found")
            return False
        
        role = self.roles[role_id]
        
        if name is not None:
            role["name"] = name
        
        if description is not None:
            role["description"] = description
        
        if permissions is not None:
            role["permissions"] = permissions
        
        role["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated role {role_id}")
        
        return True
    
    def delete_role(self, role_id: str) -> bool:
        """
        Delete a role.
        
        Args:
            role_id: Role ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        if role_id not in self.roles:
            logger.warning(f"Role {role_id} not found")
            return False
        
        del self.roles[role_id]
        
        logger.info(f"Deleted role {role_id}")
        
        return True
    
    def get_role(self, role_id: str) -> Optional[Dict]:
        """
        Get role information.
        
        Args:
            role_id: Role ID
            
        Returns:
            Role information if found, None otherwise
        """
        return self.roles.get(role_id)
    
    def get_roles_by_name(self, name: str) -> List[Dict]:
        """
        Get roles by name.
        
        Args:
            name: Role name
            
        Returns:
            List of roles with matching name
        """
        return [role for role in self.roles.values() if role["name"] == name]
    
    def create_permission(self, name: str, description: str, resource_type: str) -> str:
        """
        Create a new permission.
        
        Args:
            name: Permission name
            description: Permission description
            resource_type: Resource type
            
        Returns:
            Permission ID
        """
        permission_id = str(uuid.uuid4())
        
        permission = {
            "id": permission_id,
            "name": name,
            "description": description,
            "resource_type": resource_type,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.permissions[permission_id] = permission
        
        logger.info(f"Created permission {name} with ID {permission_id}")
        
        return permission_id
    
    def update_permission(self, permission_id: str, name: str = None, description: str = None, resource_type: str = None) -> bool:
        """
        Update an existing permission.
        
        Args:
            permission_id: Permission ID
            name: New permission name
            description: New permission description
            resource_type: New resource type
            
        Returns:
            True if update successful, False otherwise
        """
        if permission_id not in self.permissions:
            logger.warning(f"Permission {permission_id} not found")
            return False
        
        permission = self.permissions[permission_id]
        
        if name is not None:
            permission["name"] = name
        
        if description is not None:
            permission["description"] = description
        
        if resource_type is not None:
            permission["resource_type"] = resource_type
        
        permission["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated permission {permission_id}")
        
        return True
    
    def delete_permission(self, permission_id: str) -> bool:
        """
        Delete a permission.
        
        Args:
            permission_id: Permission ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        if permission_id not in self.permissions:
            logger.warning(f"Permission {permission_id} not found")
            return False
        
        del self.permissions[permission_id]
        
        # Remove permission from all roles
        for role in self.roles.values():
            if permission_id in role["permissions"]:
                role["permissions"].remove(permission_id)
        
        logger.info(f"Deleted permission {permission_id}")
        
        return True
    
    def get_permission(self, permission_id: str) -> Optional[Dict]:
        """
        Get permission information.
        
        Args:
            permission_id: Permission ID
            
        Returns:
            Permission information if found, None otherwise
        """
        return self.permissions.get(permission_id)
    
    def get_permissions_by_name(self, name: str) -> List[Dict]:
        """
        Get permissions by name.
        
        Args:
            name: Permission name
            
        Returns:
            List of permissions with matching name
        """
        return [perm for perm in self.permissions.values() if perm["name"] == name]
    
    def create_policy(self, name: str, description: str, rules: List[Dict], effect: str = "allow") -> str:
        """
        Create a new policy.
        
        Args:
            name: Policy name
            description: Policy description
            rules: List of policy rules
            effect: Policy effect (allow or deny)
            
        Returns:
            Policy ID
        """
        policy_id = str(uuid.uuid4())
        
        policy = {
            "id": policy_id,
            "name": name,
            "description": description,
            "rules": rules,
            "effect": effect,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.policies[policy_id] = policy
        
        logger.info(f"Created policy {name} with ID {policy_id}")
        
        return policy_id
    
    def update_policy(self, policy_id: str, name: str = None, description: str = None, rules: List[Dict] = None, effect: str = None) -> bool:
        """
        Update an existing policy.
        
        Args:
            policy_id: Policy ID
            name: New policy name
            description: New policy description
            rules: New list of policy rules
            effect: New policy effect
            
        Returns:
            True if update successful, False otherwise
        """
        if policy_id not in self.policies:
            logger.warning(f"Policy {policy_id} not found")
            return False
        
        policy = self.policies[policy_id]
        
        if name is not None:
            policy["name"] = name
        
        if description is not None:
            policy["description"] = description
        
        if rules is not None:
            policy["rules"] = rules
        
        if effect is not None:
            policy["effect"] = effect
        
        policy["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated policy {policy_id}")
        
        return True
    
    def delete_policy(self, policy_id: str) -> bool:
        """
        Delete a policy.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        if policy_id not in self.policies:
            logger.warning(f"Policy {policy_id} not found")
            return False
        
        del self.policies[policy_id]
        
        logger.info(f"Deleted policy {policy_id}")
        
        return True
    
    def get_policy(self, policy_id: str) -> Optional[Dict]:
        """
        Get policy information.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Policy information if found, None otherwise
        """
        return self.policies.get(policy_id)
    
    def get_policies_by_name(self, name: str) -> List[Dict]:
        """
        Get policies by name.
        
        Args:
            name: Policy name
            
        Returns:
            List of policies with matching name
        """
        return [policy for policy in self.policies.values() if policy["name"] == name]
    
    def register_resource(self, resource_type: str, resource_id: str, attributes: Dict) -> str:
        """
        Register a resource with the access control system.
        
        Args:
            resource_type: Resource type
            resource_id: Resource ID
            attributes: Resource attributes
            
        Returns:
            Registration ID
        """
        registration_id = str(uuid.uuid4())
        
        resource = {
            "registration_id": registration_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "attributes": attributes,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.resources[registration_id] = resource
        
        logger.info(f"Registered resource {resource_id} of type {resource_type} with registration ID {registration_id}")
        
        return registration_id
    
    def update_resource(self, registration_id: str, attributes: Dict) -> bool:
        """
        Update a registered resource.
        
        Args:
            registration_id: Registration ID
            attributes: New resource attributes
            
        Returns:
            True if update successful, False otherwise
        """
        if registration_id not in self.resources:
            logger.warning(f"Resource with registration ID {registration_id} not found")
            return False
        
        resource = self.resources[registration_id]
        
        # Update attributes
        for key, value in attributes.items():
            resource["attributes"][key] = value
        
        resource["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated resource with registration ID {registration_id}")
        
        return True
    
    def unregister_resource(self, registration_id: str) -> bool:
        """
        Unregister a resource.
        
        Args:
            registration_id: Registration ID
            
        Returns:
            True if unregistration successful, False otherwise
        """
        if registration_id not in self.resources:
            logger.warning(f"Resource with registration ID {registration_id} not found")
            return False
        
        del self.resources[registration_id]
        
        logger.info(f"Unregistered resource with registration ID {registration_id}")
        
        return True
    
    def get_resource(self, registration_id: str) -> Optional[Dict]:
        """
        Get resource information.
        
        Args:
            registration_id: Registration ID
            
        Returns:
            Resource information if found, None otherwise
        """
        return self.resources.get(registration_id)
    
    def get_resources_by_type(self, resource_type: str) -> List[Dict]:
        """
        Get resources by type.
        
        Args:
            resource_type: Resource type
            
        Returns:
            List of resources with matching type
        """
        return [resource for resource in self.resources.values() if resource["resource_type"] == resource_type]
    
    def get_resources_by_id(self, resource_id: str) -> List[Dict]:
        """
        Get resources by ID.
        
        Args:
            resource_id: Resource ID
            
        Returns:
            List of resources with matching ID
        """
        return [resource for resource in self.resources.values() if resource["resource_id"] == resource_id]
    
    def check_access(self, identity_id: str, resource_id: str, action: str, context: Dict = None) -> Dict:
        """
        Check if an identity has access to perform an action on a resource.
        
        Args:
            identity_id: Identity ID
            resource_id: Resource ID
            action: Action to perform
            context: Access context
            
        Returns:
            Dict containing access decision
        """
        # Generate decision ID
        decision_id = str(uuid.uuid4())
        
        # Default context if not provided
        if context is None:
            context = {
                "timestamp": datetime.utcnow().isoformat(),
                "ip_address": "unknown",
                "user_agent": "unknown"
            }
        else:
            # Ensure timestamp is present
            if "timestamp" not in context:
                context["timestamp"] = datetime.utcnow().isoformat()
        
        # Check cache for recent decision
        cache_key = f"{identity_id}:{resource_id}:{action}"
        if cache_key in self.access_decisions:
            cached_decision = self.access_decisions[cache_key]
            cache_time = datetime.fromisoformat(cached_decision["timestamp"])
            if (datetime.utcnow() - cache_time).total_seconds() < self.config["decision_cache_ttl"]:
                # Return cached decision with new decision ID
                decision = cached_decision.copy()
                decision["id"] = decision_id
                decision["cached"] = True
                return decision
        
        # Find resources matching the resource ID
        resources = self.get_resources_by_id(resource_id)
        if not resources:
            logger.warning(f"Resource {resource_id} not found")
            return self._create_access_denied_decision(decision_id, identity_id, resource_id, action, context, "Resource not found")
        
        # For simplicity, use the first matching resource
        resource = resources[0]
        
        # Initialize decision factors
        decision_factors = {
            "rbac": {"allowed": False, "roles": []},
            "abac": {"allowed": False, "attributes": {}},
            "pbac": {"allowed": False, "policies": []},
            "trust": {"allowed": False, "score": 0.0, "threshold": 0.0},
            "context": {"allowed": False, "factors": {}}
        }
        
        # Check RBAC if enabled
        if self.config["rbac_enabled"]:
            rbac_decision = self._check_rbac_access(identity_id, resource, action)
            decision_factors["rbac"] = rbac_decision
        
        # Check ABAC if enabled
        if self.config["abac_enabled"]:
            abac_decision = self._check_abac_access(identity_id, resource, action, context)
            decision_factors["abac"] = abac_decision
        
        # Check PBAC if enabled
        if self.config["pbac_enabled"]:
            pbac_decision = self._check_pbac_access(identity_id, resource, action, context)
            decision_factors["pbac"] = pbac_decision
        
        # Check trust-based access if enabled
        if self.config["trust_based_enabled"]:
            trust_decision = self._check_trust_based_access(identity_id, action)
            decision_factors["trust"] = trust_decision
        
        # Check context-aware access if enabled
        if self.config["context_aware_enabled"]:
            context_decision = self._check_context_aware_access(identity_id, resource, action, context)
            decision_factors["context"] = context_decision
        
        # Determine final decision
        # If default deny, all checks must pass
        # If not default deny, any check can pass
        if self.config["default_deny"]:
            allowed = all([
                not self.config["rbac_enabled"] or decision_factors["rbac"]["allowed"],
                not self.config["abac_enabled"] or decision_factors["abac"]["allowed"],
                not self.config["pbac_enabled"] or decision_factors["pbac"]["allowed"],
                not self.config["trust_based_enabled"] or decision_factors["trust"]["allowed"],
                not self.config["context_aware_enabled"] or decision_factors["context"]["allowed"]
            ])
        else:
            allowed = any([
                self.config["rbac_enabled"] and decision_factors["rbac"]["allowed"],
                self.config["abac_enabled"] and decision_factors["abac"]["allowed"],
                self.config["pbac_enabled"] and decision_factors["pbac"]["allowed"],
                self.config["trust_based_enabled"] and decision_factors["trust"]["allowed"],
                self.config["context_aware_enabled"] and decision_factors["context"]["allowed"]
            ])
        
        # Create decision
        decision = {
            "id": decision_id,
            "identity_id": identity_id,
            "resource_id": resource_id,
            "action": action,
            "allowed": allowed,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "factors": decision_factors,
            "cached": False
        }
        
        # Cache decision
        self.access_decisions[cache_key] = decision
        
        # Log decision
        if allowed:
            logger.info(f"Access allowed for identity {identity_id} to perform {action} on resource {resource_id}")
        else:
            logger.warning(f"Access denied for identity {identity_id} to perform {action} on resource {resource_id}")
        
        return decision
    
    def _check_rbac_access(self, identity_id: str, resource: Dict, action: str) -> Dict:
        """
        Check access using Role-Based Access Control.
        
        Args:
            identity_id: Identity ID
            resource: Resource information
            action: Action to perform
            
        Returns:
            Dict containing RBAC decision
        """
        # In a production implementation, this would retrieve roles assigned to the identity
        # For demonstration, we assume roles are stored in the resource attributes
        allowed_roles = resource["attributes"].get("allowed_roles", {})
        
        # Check if identity has any of the allowed roles for the action
        identity_roles = []  # This would be retrieved from identity store
        
        # For demonstration, we assume the identity has a role if it's in the allowed roles
        for role_name, actions in allowed_roles.items():
            if action in actions:
                identity_roles.append(role_name)
        
        allowed = len(identity_roles) > 0
        
        return {
            "allowed": allowed,
            "roles": identity_roles
        }
    
    def _check_abac_access(self, identity_id: str, resource: Dict, action: str, context: Dict) -> Dict:
        """
        Check access using Attribute-Based Access Control.
        
        Args:
            identity_id: Identity ID
            resource: Resource information
            action: Action to perform
            context: Access context
            
        Returns:
            Dict containing ABAC decision
        """
        # In a production implementation, this would retrieve identity attributes
        # and evaluate them against resource attributes and access rules
        
        # For demonstration, we assume attribute rules are stored in the resource attributes
        attribute_rules = resource["attributes"].get("attribute_rules", {})
        
        # Check if any attribute rule allows the action
        matching_attributes = {}
        
        # For demonstration, we assume the identity attributes match if they're in the rules
        for attr_name, attr_values in attribute_rules.get(action, {}).items():
            # This would check if the identity has the attribute with one of the allowed values
            # For demonstration, we assume it does if the attribute is in the rules
            matching_attributes[attr_name] = attr_values
        
        allowed = len(matching_attributes) > 0
        
        return {
            "allowed": allowed,
            "attributes": matching_attributes
        }
    
    def _check_pbac_access(self, identity_id: str, resource: Dict, action: str, context: Dict) -> Dict:
        """
        Check access using Policy-Based Access Control.
        
        Args:
            identity_id: Identity ID
            resource: Resource information
            action: Action to perform
            context: Access context
            
        Returns:
            Dict containing PBAC decision
        """
        # In a production implementation, this would evaluate all applicable policies
        
        # For demonstration, we assume policies are stored in the resource attributes
        policy_references = resource["attributes"].get("policies", [])
        
        # Check if any policy allows the action
        matching_policies = []
        
        for policy_id in policy_references:
            if policy_id in self.policies:
                policy = self.policies[policy_id]
                
                # Check if policy applies to this action
                if self._evaluate_policy(policy, identity_id, resource, action, context):
                    matching_policies.append(policy["name"])
        
        allowed = len(matching_policies) > 0
        
        return {
            "allowed": allowed,
            "policies": matching_policies
        }
    
    def _evaluate_policy(self, policy: Dict, identity_id: str, resource: Dict, action: str, context: Dict) -> bool:
        """
        Evaluate a policy for an access request.
        
        Args:
            policy: Policy information
            identity_id: Identity ID
            resource: Resource information
            action: Action to perform
            context: Access context
            
        Returns:
            True if policy allows access, False otherwise
        """
        # In a production implementation, this would evaluate policy rules
        # against the identity, resource, action, and context
        
        # For demonstration, we assume a simple rule format
        for rule in policy["rules"]:
            if rule.get("action") == action:
                # Check if rule conditions match
                conditions_match = True
                
                for condition_key, condition_value in rule.get("conditions", {}).items():
                    # Check identity attributes
                    if condition_key.startswith("identity."):
                        attr_name = condition_key[len("identity."):]
                        # This would check identity attributes
                        # For demonstration, we assume it matches
                        pass
                    
                    # Check resource attributes
                    elif condition_key.startswith("resource."):
                        attr_name = condition_key[len("resource."):]
                        if attr_name in resource["attributes"]:
                            if resource["attributes"][attr_name] != condition_value:
                                conditions_match = False
                                break
                        else:
                            conditions_match = False
                            break
                    
                    # Check context attributes
                    elif condition_key.startswith("context."):
                        attr_name = condition_key[len("context."):]
                        if attr_name in context:
                            if context[attr_name] != condition_value:
                                conditions_match = False
                                break
                        else:
                            conditions_match = False
                            break
                
                if conditions_match:
                    return policy["effect"] == "allow"
        
        # If no rule matches, use the opposite of the policy effect
        return policy["effect"] != "allow"
    
    def _check_trust_based_access(self, identity_id: str, action: str) -> Dict:
        """
        Check access using Trust-Based Access Control.
        
        Args:
            identity_id: Identity ID
            action: Action to perform
            
        Returns:
            Dict containing trust-based decision
        """
        # In a production implementation, this would retrieve the identity's trust score
        # For demonstration, we use a random score
        trust_score = 0.8  # This would be retrieved from identity store
        
        # Get trust threshold for the action
        threshold = self.trust_thresholds.get(action, self.config["default_trust_threshold"])
        
        allowed = trust_score >= threshold
        
        return {
            "allowed": allowed,
            "score": trust_score,
            "threshold": threshold
        }
    
    def _check_context_aware_access(self, identity_id: str, resource: Dict, action: str, context: Dict) -> Dict:
        """
        Check access using Context-Aware Access Control.
        
        Args:
            identity_id: Identity ID
            resource: Resource information
            action: Action to perform
            context: Access context
            
        Returns:
            Dict containing context-aware decision
        """
        # In a production implementation, this would evaluate context factors
        # against access rules
        
        # For demonstration, we assume context rules are stored in the resource attributes
        context_rules = resource["attributes"].get("context_rules", {})
        
        # Check if context satisfies the rules for the action
        matching_factors = {}
        
        for factor_name in self.config["context_factors"]:
            if factor_name in context:
                # Check if factor has rules for this action
                if action in context_rules.get(factor_name, {}):
                    factor_rules = context_rules[factor_name][action]
                    
                    # Check if context value satisfies the rules
                    if self._evaluate_context_factor(factor_name, context[factor_name], factor_rules):
                        matching_factors[factor_name] = context[factor_name]
        
        # For demonstration, we require all defined factors to match
        required_factors = set(context_rules.keys())
        matching_factor_names = set(matching_factors.keys())
        
        allowed = required_factors.issubset(matching_factor_names)
        
        return {
            "allowed": allowed,
            "factors": matching_factors
        }
    
    def _evaluate_context_factor(self, factor_name: str, factor_value: Any, factor_rules: Dict) -> bool:
        """
        Evaluate a context factor against rules.
        
        Args:
            factor_name: Factor name
            factor_value: Factor value
            factor_rules: Factor rules
            
        Returns:
            True if factor satisfies rules, False otherwise
        """
        # In a production implementation, this would evaluate different types of rules
        # based on the factor type
        
        # For demonstration, we assume simple equality or range rules
        if "equals" in factor_rules:
            return factor_value == factor_rules["equals"]
        
        if "in" in factor_rules:
            return factor_value in factor_rules["in"]
        
        if "range" in factor_rules:
            min_value = factor_rules["range"].get("min")
            max_value = factor_rules["range"].get("max")
            
            if min_value is not None and factor_value < min_value:
                return False
            
            if max_value is not None and factor_value > max_value:
                return False
            
            return True
        
        # If no rule type matches, default to allow
        return True
    
    def _create_access_denied_decision(self, decision_id: str, identity_id: str, resource_id: str, action: str, context: Dict, reason: str) -> Dict:
        """
        Create an access denied decision.
        
        Args:
            decision_id: Decision ID
            identity_id: Identity ID
            resource_id: Resource ID
            action: Action to perform
            context: Access context
            reason: Denial reason
            
        Returns:
            Dict containing access denied decision
        """
        decision = {
            "id": decision_id,
            "identity_id": identity_id,
            "resource_id": resource_id,
            "action": action,
            "allowed": False,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "reason": reason,
            "cached": False
        }
        
        logger.warning(f"Access denied for identity {identity_id} to perform {action} on resource {resource_id}: {reason}")
        
        return decision
    
    def request_jit_access(self, identity_id: str, resource_id: str, action: str, justification: str, duration: int = None) -> Dict:
        """
        Request Just-In-Time access to a resource.
        
        Args:
            identity_id: Identity ID
            resource_id: Resource ID
            action: Action to perform
            justification: Access justification
            duration: Access duration in seconds
            
        Returns:
            Dict containing JIT request information
        """
        if not self.config["jit_enabled"]:
            raise ValueError("Just-In-Time access is not enabled")
        
        # Find resources matching the resource ID
        resources = self.get_resources_by_id(resource_id)
        if not resources:
            raise ValueError(f"Resource {resource_id} not found")
        
        # For simplicity, use the first matching resource
        resource = resources[0]
        
        # Check if JIT access is allowed for this resource and action
        jit_config = resource["attributes"].get("jit_access", {})
        if action not in jit_config.get("allowed_actions", []):
            raise ValueError(f"Just-In-Time access for action {action} is not allowed for resource {resource_id}")
        
        # Use default duration if not specified
        if duration is None:
            duration = jit_config.get("default_duration", self.config["jit_request_ttl"])
        
        # Check if duration exceeds maximum
        max_duration = jit_config.get("max_duration", self.config["jit_request_ttl"])
        if duration > max_duration:
            duration = max_duration
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Create request
        request = {
            "id": request_id,
            "identity_id": identity_id,
            "resource_id": resource_id,
            "action": action,
            "justification": justification,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=duration)).isoformat(),
            "approver_id": None,
            "approval_time": None,
            "access_granted": False
        }
        
        # Store request
        self.jit_requests[request_id] = request
        
        logger.info(f"Created JIT access request {request_id} for identity {identity_id} to perform {action} on resource {resource_id}")
        
        return request
    
    def approve_jit_request(self, request_id: str, approver_id: str) -> Dict:
        """
        Approve a Just-In-Time access request.
        
        Args:
            request_id: Request ID
            approver_id: Approver identity ID
            
        Returns:
            Dict containing updated JIT request information
        """
        if request_id not in self.jit_requests:
            raise ValueError(f"JIT request {request_id} not found")
        
        request = self.jit_requests[request_id]
        
        # Check if request is still pending
        if request["status"] != "pending":
            raise ValueError(f"JIT request {request_id} is not pending")
        
        # Check if request has expired
        expires_at = datetime.fromisoformat(request["expires_at"])
        if expires_at < datetime.utcnow():
            request["status"] = "expired"
            raise ValueError(f"JIT request {request_id} has expired")
        
        # Update request
        request["status"] = "approved"
        request["approver_id"] = approver_id
        request["approval_time"] = datetime.utcnow().isoformat()
        request["access_granted"] = True
        
        logger.info(f"Approved JIT access request {request_id} by approver {approver_id}")
        
        return request
    
    def deny_jit_request(self, request_id: str, approver_id: str, reason: str) -> Dict:
        """
        Deny a Just-In-Time access request.
        
        Args:
            request_id: Request ID
            approver_id: Approver identity ID
            reason: Denial reason
            
        Returns:
            Dict containing updated JIT request information
        """
        if request_id not in self.jit_requests:
            raise ValueError(f"JIT request {request_id} not found")
        
        request = self.jit_requests[request_id]
        
        # Check if request is still pending
        if request["status"] != "pending":
            raise ValueError(f"JIT request {request_id} is not pending")
        
        # Update request
        request["status"] = "denied"
        request["approver_id"] = approver_id
        request["approval_time"] = datetime.utcnow().isoformat()
        request["denial_reason"] = reason
        request["access_granted"] = False
        
        logger.info(f"Denied JIT access request {request_id} by approver {approver_id}: {reason}")
        
        return request
    
    def check_jit_access(self, identity_id: str, resource_id: str, action: str) -> bool:
        """
        Check if an identity has active JIT access to perform an action on a resource.
        
        Args:
            identity_id: Identity ID
            resource_id: Resource ID
            action: Action to perform
            
        Returns:
            True if JIT access is granted, False otherwise
        """
        # Find active JIT requests for the identity, resource, and action
        for request in self.jit_requests.values():
            if (request["identity_id"] == identity_id and
                request["resource_id"] == resource_id and
                request["action"] == action and
                request["status"] == "approved" and
                request["access_granted"]):
                
                # Check if request is still valid
                expires_at = datetime.fromisoformat(request["expires_at"])
                if expires_at >= datetime.utcnow():
                    return True
                else:
                    # Mark request as expired
                    request["status"] = "expired"
                    request["access_granted"] = False
        
        return False
    
    def get_jit_request(self, request_id: str) -> Optional[Dict]:
        """
        Get JIT request information.
        
        Args:
            request_id: Request ID
            
        Returns:
            JIT request information if found, None otherwise
        """
        return self.jit_requests.get(request_id)
    
    def get_jit_requests_by_identity(self, identity_id: str) -> List[Dict]:
        """
        Get JIT requests by identity.
        
        Args:
            identity_id: Identity ID
            
        Returns:
            List of JIT requests for the identity
        """
        return [request for request in self.jit_requests.values() if request["identity_id"] == identity_id]
    
    def get_jit_requests_by_resource(self, resource_id: str) -> List[Dict]:
        """
        Get JIT requests by resource.
        
        Args:
            resource_id: Resource ID
            
        Returns:
            List of JIT requests for the resource
        """
        return [request for request in self.jit_requests.values() if request["resource_id"] == resource_id]
    
    def get_pending_jit_requests(self) -> List[Dict]:
        """
        Get pending JIT requests.
        
        Returns:
            List of pending JIT requests
        """
        return [request for request in self.jit_requests.values() if request["status"] == "pending"]


class DynamicAccessAdjuster:
    """
    Dynamic Access Adjuster for the Security & Compliance Layer.
    
    This class provides dynamic access adjustment services including:
    - Trust-based permission scaling
    - Context-based access adjustment
    - Anomaly-based access restriction
    - Risk-based access control
    """
    
    def __init__(self, access_control_system: AccessControlSystem):
        """
        Initialize the Dynamic Access Adjuster.
        
        Args:
            access_control_system: Access Control System instance
        """
        self.access_control_system = access_control_system
        self.risk_assessments = {}
        self.anomaly_scores = {}
        self.permission_adjustments = {}
        
        logger.info("Dynamic Access Adjuster initialized successfully")
    
    def adjust_permissions_by_trust(self, identity_id: str, trust_score: float) -> Dict:
        """
        Adjust permissions based on trust score.
        
        Args:
            identity_id: Identity ID
            trust_score: Trust score (0.0 to 1.0)
            
        Returns:
            Dict containing permission adjustment information
        """
        # Generate adjustment ID
        adjustment_id = str(uuid.uuid4())
        
        # Determine permission levels based on trust score
        permission_levels = []
        
        if trust_score >= self.access_control_system.trust_thresholds.get("admin", 0.9):
            permission_levels = ["read", "write", "execute", "admin"]
        elif trust_score >= self.access_control_system.trust_thresholds.get("execute", 0.7):
            permission_levels = ["read", "write", "execute"]
        elif trust_score >= self.access_control_system.trust_thresholds.get("write", 0.5):
            permission_levels = ["read", "write"]
        elif trust_score >= self.access_control_system.trust_thresholds.get("read", 0.3):
            permission_levels = ["read"]
        
        # Create adjustment
        adjustment = {
            "id": adjustment_id,
            "identity_id": identity_id,
            "trust_score": trust_score,
            "permission_levels": permission_levels,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Store adjustment
        self.permission_adjustments[adjustment_id] = adjustment
        
        logger.info(f"Adjusted permissions for identity {identity_id} based on trust score {trust_score}")
        
        return adjustment
    
    def adjust_permissions_by_context(self, identity_id: str, context: Dict) -> Dict:
        """
        Adjust permissions based on context.
        
        Args:
            identity_id: Identity ID
            context: Access context
            
        Returns:
            Dict containing permission adjustment information
        """
        # Generate adjustment ID
        adjustment_id = str(uuid.uuid4())
        
        # Determine context risk level
        risk_level = self._assess_context_risk(context)
        
        # Determine permission levels based on risk level
        permission_levels = []
        
        if risk_level == "low":
            permission_levels = ["read", "write", "execute", "admin"]
        elif risk_level == "medium":
            permission_levels = ["read", "write"]
        elif risk_level == "high":
            permission_levels = ["read"]
        elif risk_level == "critical":
            permission_levels = []
        
        # Create adjustment
        adjustment = {
            "id": adjustment_id,
            "identity_id": identity_id,
            "context": context,
            "risk_level": risk_level,
            "permission_levels": permission_levels,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Store adjustment
        self.permission_adjustments[adjustment_id] = adjustment
        
        logger.info(f"Adjusted permissions for identity {identity_id} based on context risk level {risk_level}")
        
        return adjustment
    
    def adjust_permissions_by_anomaly(self, identity_id: str, anomaly_score: float) -> Dict:
        """
        Adjust permissions based on anomaly score.
        
        Args:
            identity_id: Identity ID
            anomaly_score: Anomaly score (0.0 to 1.0)
            
        Returns:
            Dict containing permission adjustment information
        """
        # Generate adjustment ID
        adjustment_id = str(uuid.uuid4())
        
        # Store anomaly score
        self.anomaly_scores[identity_id] = anomaly_score
        
        # Determine permission levels based on anomaly score
        permission_levels = []
        
        if anomaly_score < 0.3:
            permission_levels = ["read", "write", "execute", "admin"]
        elif anomaly_score < 0.5:
            permission_levels = ["read", "write", "execute"]
        elif anomaly_score < 0.7:
            permission_levels = ["read", "write"]
        elif anomaly_score < 0.9:
            permission_levels = ["read"]
        
        # Create adjustment
        adjustment = {
            "id": adjustment_id,
            "identity_id": identity_id,
            "anomaly_score": anomaly_score,
            "permission_levels": permission_levels,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Store adjustment
        self.permission_adjustments[adjustment_id] = adjustment
        
        logger.info(f"Adjusted permissions for identity {identity_id} based on anomaly score {anomaly_score}")
        
        return adjustment
    
    def assess_risk(self, identity_id: str, resource_id: str, action: str, context: Dict) -> Dict:
        """
        Assess risk for an access request.
        
        Args:
            identity_id: Identity ID
            resource_id: Resource ID
            action: Action to perform
            context: Access context
            
        Returns:
            Dict containing risk assessment information
        """
        # Generate assessment ID
        assessment_id = str(uuid.uuid4())
        
        # Calculate risk factors
        risk_factors = {
            "identity_risk": self._calculate_identity_risk(identity_id),
            "resource_risk": self._calculate_resource_risk(resource_id),
            "action_risk": self._calculate_action_risk(action),
            "context_risk": self._calculate_context_risk(context)
        }
        
        # Calculate overall risk score
        risk_score = (
            risk_factors["identity_risk"] * 0.3 +
            risk_factors["resource_risk"] * 0.3 +
            risk_factors["action_risk"] * 0.2 +
            risk_factors["context_risk"] * 0.2
        )
        
        # Determine risk level
        risk_level = "low"
        if risk_score >= 0.8:
            risk_level = "critical"
        elif risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        
        # Create assessment
        assessment = {
            "id": assessment_id,
            "identity_id": identity_id,
            "resource_id": resource_id,
            "action": action,
            "context": context,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store assessment
        self.risk_assessments[assessment_id] = assessment
        
        logger.info(f"Assessed risk for identity {identity_id} to perform {action} on resource {resource_id}: {risk_level} ({risk_score})")
        
        return assessment
    
    def get_effective_permissions(self, identity_id: str, context: Dict = None) -> List[str]:
        """
        Get effective permissions for an identity based on all adjustments.
        
        Args:
            identity_id: Identity ID
            context: Access context
            
        Returns:
            List of effective permission levels
        """
        # Get all active adjustments for the identity
        active_adjustments = []
        
        for adjustment in self.permission_adjustments.values():
            if adjustment["identity_id"] == identity_id:
                # Check if adjustment is still valid
                expires_at = datetime.fromisoformat(adjustment["expires_at"])
                if expires_at >= datetime.utcnow():
                    active_adjustments.append(adjustment)
        
        # If no active adjustments, return default permissions
        if not active_adjustments:
            return ["read", "write", "execute", "admin"]
        
        # Get intersection of permission levels from all adjustments
        effective_permissions = set(["read", "write", "execute", "admin"])
        
        for adjustment in active_adjustments:
            effective_permissions = effective_permissions.intersection(set(adjustment["permission_levels"]))
        
        return list(effective_permissions)
    
    def _assess_context_risk(self, context: Dict) -> str:
        """
        Assess risk level based on context.
        
        Args:
            context: Access context
            
        Returns:
            Risk level (low, medium, high, critical)
        """
        # In a production implementation, this would evaluate various context factors
        # to determine the risk level
        
        # For demonstration, we use a simple heuristic
        risk_level = "low"
        
        # Check time of day (if available)
        if "time" in context:
            time_obj = datetime.fromisoformat(context["time"])
            hour = time_obj.hour
            
            # Higher risk during non-business hours
            if hour < 8 or hour > 18:
                risk_level = "medium"
        
        # Check location (if available)
        if "location" in context:
            location = context["location"]
            
            # Higher risk for unusual locations
            if location not in ["office", "home"]:
                risk_level = "high"
        
        # Check network (if available)
        if "network" in context:
            network = context["network"]
            
            # Higher risk for public networks
            if network == "public":
                risk_level = "high"
        
        # Check device (if available)
        if "device" in context:
            device = context["device"]
            
            # Higher risk for unknown devices
            if device == "unknown":
                risk_level = "critical"
        
        return risk_level
    
    def _calculate_identity_risk(self, identity_id: str) -> float:
        """
        Calculate risk factor for an identity.
        
        Args:
            identity_id: Identity ID
            
        Returns:
            Risk factor (0.0 to 1.0)
        """
        # In a production implementation, this would evaluate various identity factors
        # to determine the risk factor
        
        # For demonstration, we use the anomaly score if available
        if identity_id in self.anomaly_scores:
            return self.anomaly_scores[identity_id]
        
        # Default risk factor
        return 0.2
    
    def _calculate_resource_risk(self, resource_id: str) -> float:
        """
        Calculate risk factor for a resource.
        
        Args:
            resource_id: Resource ID
            
        Returns:
            Risk factor (0.0 to 1.0)
        """
        # In a production implementation, this would evaluate various resource factors
        # to determine the risk factor
        
        # For demonstration, we use a simple heuristic based on resource ID
        # Higher risk for resources with "sensitive" or "critical" in the ID
        if "sensitive" in resource_id.lower():
            return 0.7
        elif "critical" in resource_id.lower():
            return 0.9
        
        # Default risk factor
        return 0.3
    
    def _calculate_action_risk(self, action: str) -> float:
        """
        Calculate risk factor for an action.
        
        Args:
            action: Action to perform
            
        Returns:
            Risk factor (0.0 to 1.0)
        """
        # In a production implementation, this would evaluate the risk associated with
        # different actions
        
        # For demonstration, we use a simple mapping
        risk_mapping = {
            "read": 0.1,
            "write": 0.5,
            "execute": 0.7,
            "admin": 0.9,
            "delete": 0.8
        }
        
        return risk_mapping.get(action, 0.5)
    
    def _calculate_context_risk(self, context: Dict) -> float:
        """
        Calculate risk factor for a context.
        
        Args:
            context: Access context
            
        Returns:
            Risk factor (0.0 to 1.0)
        """
        # In a production implementation, this would evaluate various context factors
        # to determine the risk factor
        
        # For demonstration, we map the risk level to a factor
        risk_level = self._assess_context_risk(context)
        
        risk_mapping = {
            "low": 0.1,
            "medium": 0.4,
            "high": 0.7,
            "critical": 0.9
        }
        
        return risk_mapping.get(risk_level, 0.5)


# Example usage
if __name__ == "__main__":
    # Initialize Access Control System
    acs = AccessControlSystem()
    
    # Create roles
    admin_role = acs.create_role("admin", "Administrator role", ["read", "write", "execute", "admin"])
    user_role = acs.create_role("user", "Standard user role", ["read", "write"])
    
    # Create permissions
    read_perm = acs.create_permission("read", "Read permission", "document")
    write_perm = acs.create_permission("write", "Write permission", "document")
    
    # Create policy
    policy_id = acs.create_policy(
        "business_hours_policy",
        "Allow access during business hours",
        [
            {
                "action": "read",
                "conditions": {
                    "context.time_of_day": "business_hours"
                }
            }
        ],
        "allow"
    )
    
    # Register resource
    resource_id = acs.register_resource(
        "document",
        "doc123",
        {
            "allowed_roles": {
                "admin": ["read", "write", "execute", "admin"],
                "user": ["read", "write"]
            },
            "attribute_rules": {
                "read": {
                    "department": ["engineering", "product"]
                },
                "write": {
                    "department": ["engineering"]
                }
            },
            "policies": [policy_id],
            "context_rules": {
                "time": {
                    "read": {
                        "range": {
                            "min": 8,
                            "max": 18
                        }
                    }
                }
            }
        }
    )
    
    # Check access
    decision = acs.check_access(
        "user123",
        "doc123",
        "read",
        {
            "time": "2023-01-01T14:30:00",
            "location": "office",
            "device": "corporate_laptop",
            "network": "corporate",
            "time_of_day": "business_hours"
        }
    )
    
    print(f"Access decision: {decision['allowed']}")
    
    # Initialize Dynamic Access Adjuster
    adjuster = DynamicAccessAdjuster(acs)
    
    # Adjust permissions by trust
    trust_adjustment = adjuster.adjust_permissions_by_trust("user123", 0.8)
    print(f"Trust-based permission levels: {trust_adjustment['permission_levels']}")
    
    # Adjust permissions by context
    context_adjustment = adjuster.adjust_permissions_by_context(
        "user123",
        {
            "time": "2023-01-01T22:30:00",
            "location": "home",
            "device": "personal_laptop",
            "network": "home"
        }
    )
    print(f"Context-based permission levels: {context_adjustment['permission_levels']}")
    
    # Get effective permissions
    effective_permissions = adjuster.get_effective_permissions("user123")
    print(f"Effective permissions: {effective_permissions}")
    
    # Request JIT access
    jit_request = acs.request_jit_access(
        "user123",
        "doc123",
        "admin",
        "Need to perform emergency maintenance",
        3600  # 1 hour
    )
    print(f"JIT request status: {jit_request['status']}")
    
    # Approve JIT request
    approved_request = acs.approve_jit_request(jit_request["id"], "admin456")
    print(f"JIT request status after approval: {approved_request['status']}")
    
    # Check JIT access
    jit_access = acs.check_jit_access("user123", "doc123", "admin")
    print(f"JIT access granted: {jit_access}")
