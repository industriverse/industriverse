"""
Authorization Service

This module provides a comprehensive authorization service for the Deployment Operations Layer.
It handles role-based access control (RBAC), permission management, and policy enforcement
to ensure that users and systems can only access resources and perform actions they are authorized for.

The Authorization Service is a critical security component that works alongside the Authentication Service
to provide a complete security solution for the Deployment Operations Layer.
"""

import logging
import json
import time
import uuid
import os
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AuthorizationService:
    """
    Authorization Service for the Deployment Operations Layer.
    
    This service handles role-based access control (RBAC), permission management, and policy enforcement
    to ensure that users and systems can only access resources and perform actions they are authorized for.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Authorization Service.
        
        Args:
            config: Configuration dictionary for the service
        """
        self.config = config or {}
        
        # Initialize service ID and version
        self.service_id = self.config.get("service_id", "authz-service")
        self.service_version = self.config.get("service_version", "1.0.0")
        
        # Initialize role store (in a real implementation, this would be a database)
        self.role_store = self._initialize_default_roles()
        
        # Initialize permission store (in a real implementation, this would be a database)
        self.permission_store = self._initialize_default_permissions()
        
        # Initialize policy store (in a real implementation, this would be a database)
        self.policy_store = self._initialize_default_policies()
        
        # Initialize resource store (in a real implementation, this would be a database)
        self.resource_store = {}
        
        # Initialize decision cache (for performance optimization)
        self.decision_cache = {}
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes
        
        logger.info(f"Authorization Service initialized: {self.service_id}")
    
    def _initialize_default_roles(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize default roles.
        
        Returns:
            Dictionary of default roles
        """
        return {
            "admin": {
                "role_id": "admin",
                "name": "Administrator",
                "description": "Full administrative access to all resources and actions",
                "permissions": ["*"],
                "created_at": time.time(),
                "system_role": True
            },
            "operator": {
                "role_id": "operator",
                "name": "Operator",
                "description": "Operational access to deployment resources and actions",
                "permissions": [
                    "deployment:read",
                    "deployment:execute",
                    "deployment:monitor",
                    "mission:read",
                    "mission:execute",
                    "mission:monitor",
                    "capsule:read",
                    "template:read",
                    "manifest:read",
                    "simulation:read",
                    "simulation:execute"
                ],
                "created_at": time.time(),
                "system_role": True
            },
            "developer": {
                "role_id": "developer",
                "name": "Developer",
                "description": "Development access to create and modify resources",
                "permissions": [
                    "deployment:read",
                    "mission:read",
                    "mission:create",
                    "mission:update",
                    "capsule:read",
                    "capsule:create",
                    "capsule:update",
                    "template:read",
                    "template:create",
                    "template:update",
                    "manifest:read",
                    "manifest:create",
                    "manifest:update",
                    "simulation:read",
                    "simulation:create",
                    "simulation:execute"
                ],
                "created_at": time.time(),
                "system_role": True
            },
            "auditor": {
                "role_id": "auditor",
                "name": "Auditor",
                "description": "Read-only access to all resources for auditing purposes",
                "permissions": [
                    "*:read"
                ],
                "created_at": time.time(),
                "system_role": True
            },
            "user": {
                "role_id": "user",
                "name": "User",
                "description": "Basic user access",
                "permissions": [
                    "deployment:read",
                    "mission:read",
                    "capsule:read",
                    "template:read",
                    "manifest:read",
                    "simulation:read"
                ],
                "created_at": time.time(),
                "system_role": True
            }
        }
    
    def _initialize_default_permissions(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize default permissions.
        
        Returns:
            Dictionary of default permissions
        """
        permissions = {}
        
        # Resource types
        resource_types = [
            "deployment",
            "mission",
            "capsule",
            "template",
            "manifest",
            "simulation",
            "user",
            "role",
            "permission",
            "policy"
        ]
        
        # Action types
        action_types = [
            "create",
            "read",
            "update",
            "delete",
            "execute",
            "monitor",
            "approve",
            "reject"
        ]
        
        # Generate permissions for each resource type and action type
        for resource_type in resource_types:
            for action_type in action_types:
                permission_id = f"{resource_type}:{action_type}"
                permissions[permission_id] = {
                    "permission_id": permission_id,
                    "resource_type": resource_type,
                    "action_type": action_type,
                    "description": f"{action_type.capitalize()} {resource_type}",
                    "created_at": time.time(),
                    "system_permission": True
                }
        
        # Add wildcard permissions
        permissions["*"] = {
            "permission_id": "*",
            "resource_type": "*",
            "action_type": "*",
            "description": "All permissions",
            "created_at": time.time(),
            "system_permission": True
        }
        
        for resource_type in resource_types:
            permission_id = f"{resource_type}:*"
            permissions[permission_id] = {
                "permission_id": permission_id,
                "resource_type": resource_type,
                "action_type": "*",
                "description": f"All actions on {resource_type}",
                "created_at": time.time(),
                "system_permission": True
            }
        
        for action_type in action_types:
            permission_id = f"*:{action_type}"
            permissions[permission_id] = {
                "permission_id": permission_id,
                "resource_type": "*",
                "action_type": action_type,
                "description": f"{action_type.capitalize()} all resources",
                "created_at": time.time(),
                "system_permission": True
            }
        
        return permissions
    
    def _initialize_default_policies(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize default policies.
        
        Returns:
            Dictionary of default policies
        """
        return {
            "default_deny": {
                "policy_id": "default_deny",
                "name": "Default Deny",
                "description": "Deny all access by default",
                "effect": "deny",
                "resources": ["*"],
                "actions": ["*"],
                "conditions": {},
                "priority": 0,
                "created_at": time.time(),
                "system_policy": True
            },
            "admin_allow": {
                "policy_id": "admin_allow",
                "name": "Admin Allow",
                "description": "Allow all access for administrators",
                "effect": "allow",
                "resources": ["*"],
                "actions": ["*"],
                "conditions": {
                    "roles": ["admin"]
                },
                "priority": 100,
                "created_at": time.time(),
                "system_policy": True
            }
        }
    
    def authorize(self, user_id: str, roles: List[str], resource: str, action: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Authorize a user to perform an action on a resource.
        
        Args:
            user_id: User ID
            roles: List of user roles
            resource: Resource identifier
            action: Action to perform
            context: Additional context for authorization
            
        Returns:
            Authorization result dictionary
        """
        logger.info(f"Authorizing user {user_id} with roles {roles} to {action} on {resource}")
        
        # Check cache
        cache_key = f"{user_id}:{','.join(sorted(roles))}:{resource}:{action}"
        cached_decision = self._get_cached_decision(cache_key)
        if cached_decision is not None:
            logger.info(f"Using cached decision for {cache_key}: {cached_decision['authorized']}")
            return cached_decision
        
        # Initialize context
        context = context or {}
        context["user_id"] = user_id
        context["roles"] = roles
        context["resource"] = resource
        context["action"] = action
        context["timestamp"] = time.time()
        
        # Parse resource and action
        resource_parts = resource.split(":")
        resource_type = resource_parts[0] if len(resource_parts) > 0 else "*"
        resource_id = resource_parts[1] if len(resource_parts) > 1 else "*"
        
        action_parts = action.split(":")
        action_type = action_parts[0] if len(action_parts) > 0 else "*"
        
        # Check if user has required permissions
        has_permission = self._check_permissions(roles, resource_type, action_type)
        
        if not has_permission:
            logger.warning(f"User {user_id} with roles {roles} does not have permission to {action} on {resource}")
            decision = {
                "authorized": False,
                "reason": "insufficient_permissions",
                "user_id": user_id,
                "roles": roles,
                "resource": resource,
                "action": action,
                "timestamp": time.time()
            }
            
            # Cache decision
            self._cache_decision(cache_key, decision)
            
            return decision
        
        # Evaluate policies
        policy_decision = self._evaluate_policies(roles, resource, action, context)
        
        if not policy_decision["authorized"]:
            logger.warning(f"Policy denied user {user_id} with roles {roles} to {action} on {resource}: {policy_decision['reason']}")
            decision = {
                "authorized": False,
                "reason": f"policy_denied: {policy_decision['reason']}",
                "policy_id": policy_decision.get("policy_id"),
                "user_id": user_id,
                "roles": roles,
                "resource": resource,
                "action": action,
                "timestamp": time.time()
            }
            
            # Cache decision
            self._cache_decision(cache_key, decision)
            
            return decision
        
        logger.info(f"User {user_id} with roles {roles} is authorized to {action} on {resource}")
        decision = {
            "authorized": True,
            "user_id": user_id,
            "roles": roles,
            "resource": resource,
            "action": action,
            "timestamp": time.time()
        }
        
        # Cache decision
        self._cache_decision(cache_key, decision)
        
        return decision
    
    def _check_permissions(self, roles: List[str], resource_type: str, action_type: str) -> bool:
        """
        Check if the user has the required permissions based on their roles.
        
        Args:
            roles: List of user roles
            resource_type: Resource type
            action_type: Action type
            
        Returns:
            True if the user has the required permissions, False otherwise
        """
        # Get permissions for each role
        all_permissions = set()
        
        for role in roles:
            if role in self.role_store:
                role_permissions = self.role_store[role].get("permissions", [])
                all_permissions.update(role_permissions)
        
        # Check if user has the required permission
        permission_id = f"{resource_type}:{action_type}"
        
        # Check for exact permission
        if permission_id in all_permissions:
            return True
        
        # Check for wildcard permissions
        if "*" in all_permissions:
            return True
        
        if f"{resource_type}:*" in all_permissions:
            return True
        
        if f"*:{action_type}" in all_permissions:
            return True
        
        return False
    
    def _evaluate_policies(self, roles: List[str], resource: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate policies to determine if the action is allowed.
        
        Args:
            roles: List of user roles
            resource: Resource identifier
            action: Action to perform
            context: Additional context for policy evaluation
            
        Returns:
            Policy evaluation result dictionary
        """
        # Get all applicable policies
        applicable_policies = []
        
        for policy_id, policy in self.policy_store.items():
            if self._is_policy_applicable(policy, roles, resource, action, context):
                applicable_policies.append(policy)
        
        # Sort policies by priority (higher priority first)
        applicable_policies.sort(key=lambda p: p.get("priority", 0), reverse=True)
        
        # Evaluate policies in order
        for policy in applicable_policies:
            effect = policy.get("effect", "deny")
            
            if effect == "allow":
                return {
                    "authorized": True,
                    "policy_id": policy["policy_id"]
                }
            elif effect == "deny":
                return {
                    "authorized": False,
                    "reason": "policy_denied",
                    "policy_id": policy["policy_id"]
                }
        
        # Default to deny if no policies matched
        return {
            "authorized": False,
            "reason": "no_applicable_policies"
        }
    
    def _is_policy_applicable(self, policy: Dict[str, Any], roles: List[str], resource: str, action: str, context: Dict[str, Any]) -> bool:
        """
        Check if a policy is applicable to the current request.
        
        Args:
            policy: Policy dictionary
            roles: List of user roles
            resource: Resource identifier
            action: Action to perform
            context: Additional context for policy evaluation
            
        Returns:
            True if the policy is applicable, False otherwise
        """
        # Check resources
        policy_resources = policy.get("resources", [])
        if not self._matches_pattern_list(resource, policy_resources):
            return False
        
        # Check actions
        policy_actions = policy.get("actions", [])
        if not self._matches_pattern_list(action, policy_actions):
            return False
        
        # Check conditions
        policy_conditions = policy.get("conditions", {})
        
        # Check role condition
        if "roles" in policy_conditions:
            policy_roles = policy_conditions["roles"]
            if not any(role in policy_roles for role in roles) and "*" not in policy_roles:
                return False
        
        # Check time condition
        if "time_range" in policy_conditions:
            time_range = policy_conditions["time_range"]
            current_time = context.get("timestamp", time.time())
            
            if "start_time" in time_range and current_time < time_range["start_time"]:
                return False
            
            if "end_time" in time_range and current_time > time_range["end_time"]:
                return False
        
        # Check IP condition
        if "ip_ranges" in policy_conditions:
            ip_ranges = policy_conditions["ip_ranges"]
            client_ip = context.get("client_ip")
            
            if client_ip and not self._ip_in_ranges(client_ip, ip_ranges):
                return False
        
        # All conditions passed
        return True
    
    def _matches_pattern_list(self, value: str, patterns: List[str]) -> bool:
        """
        Check if a value matches any pattern in a list.
        
        Args:
            value: Value to check
            patterns: List of patterns to match against
            
        Returns:
            True if the value matches any pattern, False otherwise
        """
        if "*" in patterns:
            return True
        
        for pattern in patterns:
            if self._matches_pattern(value, pattern):
                return True
        
        return False
    
    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """
        Check if a value matches a pattern.
        
        Args:
            value: Value to check
            pattern: Pattern to match against
            
        Returns:
            True if the value matches the pattern, False otherwise
        """
        if pattern == "*":
            return True
        
        if ":" in pattern and ":" in value:
            pattern_parts = pattern.split(":")
            value_parts = value.split(":")
            
            if len(pattern_parts) != len(value_parts):
                return False
            
            for i, pattern_part in enumerate(pattern_parts):
                if pattern_part != "*" and pattern_part != value_parts[i]:
                    return False
            
            return True
        
        return pattern == value
    
    def _ip_in_ranges(self, ip: str, ip_ranges: List[str]) -> bool:
        """
        Check if an IP address is in any of the specified ranges.
        
        Args:
            ip: IP address to check
            ip_ranges: List of IP ranges to check against
            
        Returns:
            True if the IP is in any range, False otherwise
        """
        # In a real implementation, this would check if the IP is in any of the CIDR ranges
        # For this example, we'll just check for exact matches
        return ip in ip_ranges
    
    def _get_cached_decision(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a cached authorization decision.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached decision or None if not found or expired
        """
        if cache_key not in self.decision_cache:
            return None
        
        cached_entry = self.decision_cache[cache_key]
        cached_time = cached_entry.get("cached_at", 0)
        current_time = time.time()
        
        if current_time - cached_time > self.cache_ttl:
            # Cache entry has expired
            del self.decision_cache[cache_key]
            return None
        
        return cached_entry["decision"]
    
    def _cache_decision(self, cache_key: str, decision: Dict[str, Any]) -> None:
        """
        Cache an authorization decision.
        
        Args:
            cache_key: Cache key
            decision: Decision to cache
        """
        self.decision_cache[cache_key] = {
            "decision": decision,
            "cached_at": time.time()
        }
    
    def create_role(self, role_id: str, name: str, description: str, permissions: List[str]) -> Dict[str, Any]:
        """
        Create a new role.
        
        Args:
            role_id: Role ID
            name: Role name
            description: Role description
            permissions: List of permission IDs
            
        Returns:
            Role creation result dictionary
        """
        logger.info(f"Creating role: {role_id}")
        
        # Check if role already exists
        if role_id in self.role_store:
            logger.warning(f"Role already exists: {role_id}")
            return {
                "status": "error",
                "message": "Role already exists",
                "created": False
            }
        
        # Validate permissions
        invalid_permissions = [p for p in permissions if p not in self.permission_store and p != "*"]
        if invalid_permissions:
            logger.warning(f"Invalid permissions: {invalid_permissions}")
            return {
                "status": "error",
                "message": f"Invalid permissions: {invalid_permissions}",
                "created": False
            }
        
        # Create role
        role = {
            "role_id": role_id,
            "name": name,
            "description": description,
            "permissions": permissions,
            "created_at": time.time(),
            "system_role": False
        }
        
        # Store role
        self.role_store[role_id] = role
        
        logger.info(f"Role created successfully: {role_id}")
        
        return {
            "status": "success",
            "message": "Role created successfully",
            "created": True,
            "role": role
        }
    
    def update_role(self, role_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a role.
        
        Args:
            role_id: Role ID
            updates: Dictionary of updates to apply
            
        Returns:
            Role update result dictionary
        """
        logger.info(f"Updating role: {role_id}")
        
        # Check if role exists
        if role_id not in self.role_store:
            logger.warning(f"Role not found: {role_id}")
            return {
                "status": "error",
                "message": "Role not found",
                "updated": False
            }
        
        # Get role
        role = self.role_store[role_id]
        
        # Check if role is a system role
        if role.get("system_role", False) and not self.config.get("allow_system_role_updates", False):
            logger.warning(f"Cannot update system role: {role_id}")
            return {
                "status": "error",
                "message": "Cannot update system role",
                "updated": False
            }
        
        # Validate permissions if updating
        if "permissions" in updates:
            invalid_permissions = [p for p in updates["permissions"] if p not in self.permission_store and p != "*"]
            if invalid_permissions:
                logger.warning(f"Invalid permissions: {invalid_permissions}")
                return {
                    "status": "error",
                    "message": f"Invalid permissions: {invalid_permissions}",
                    "updated": False
                }
        
        # Apply updates
        for key, value in updates.items():
            if key in ["role_id", "created_at", "system_role"]:
                # Don't allow updating these fields
                continue
            
            role[key] = value
        
        # Update last modified timestamp
        role["last_modified"] = time.time()
        
        # Store updated role
        self.role_store[role_id] = role
        
        logger.info(f"Role updated successfully: {role_id}")
        
        return {
            "status": "success",
            "message": "Role updated successfully",
            "updated": True,
            "role": role
        }
    
    def delete_role(self, role_id: str) -> Dict[str, Any]:
        """
        Delete a role.
        
        Args:
            role_id: Role ID
            
        Returns:
            Role deletion result dictionary
        """
        logger.info(f"Deleting role: {role_id}")
        
        # Check if role exists
        if role_id not in self.role_store:
            logger.warning(f"Role not found: {role_id}")
            return {
                "status": "error",
                "message": "Role not found",
                "deleted": False
            }
        
        # Get role
        role = self.role_store[role_id]
        
        # Check if role is a system role
        if role.get("system_role", False) and not self.config.get("allow_system_role_deletion", False):
            logger.warning(f"Cannot delete system role: {role_id}")
            return {
                "status": "error",
                "message": "Cannot delete system role",
                "deleted": False
            }
        
        # Delete role
        del self.role_store[role_id]
        
        logger.info(f"Role deleted successfully: {role_id}")
        
        return {
            "status": "success",
            "message": "Role deleted successfully",
            "deleted": True,
            "role_id": role_id
        }
    
    def get_role(self, role_id: str) -> Dict[str, Any]:
        """
        Get a role.
        
        Args:
            role_id: Role ID
            
        Returns:
            Role dictionary
        """
        logger.info(f"Getting role: {role_id}")
        
        # Check if role exists
        if role_id not in self.role_store:
            logger.warning(f"Role not found: {role_id}")
            return {
                "status": "error",
                "message": "Role not found",
                "found": False
            }
        
        # Get role
        role = self.role_store[role_id]
        
        logger.info(f"Role retrieved successfully: {role_id}")
        
        return {
            "status": "success",
            "message": "Role retrieved successfully",
            "found": True,
            "role": role
        }
    
    def list_roles(self) -> Dict[str, Any]:
        """
        List all roles.
        
        Returns:
            Dictionary containing list of roles
        """
        logger.info("Listing roles")
        
        roles = list(self.role_store.values())
        
        logger.info(f"Listed {len(roles)} roles")
        
        return {
            "status": "success",
            "message": "Roles listed successfully",
            "roles": roles
        }
    
    def create_permission(self, permission_id: str, resource_type: str, action_type: str, description: str) -> Dict[str, Any]:
        """
        Create a new permission.
        
        Args:
            permission_id: Permission ID
            resource_type: Resource type
            action_type: Action type
            description: Permission description
            
        Returns:
            Permission creation result dictionary
        """
        logger.info(f"Creating permission: {permission_id}")
        
        # Check if permission already exists
        if permission_id in self.permission_store:
            logger.warning(f"Permission already exists: {permission_id}")
            return {
                "status": "error",
                "message": "Permission already exists",
                "created": False
            }
        
        # Create permission
        permission = {
            "permission_id": permission_id,
            "resource_type": resource_type,
            "action_type": action_type,
            "description": description,
            "created_at": time.time(),
            "system_permission": False
        }
        
        # Store permission
        self.permission_store[permission_id] = permission
        
        logger.info(f"Permission created successfully: {permission_id}")
        
        return {
            "status": "success",
            "message": "Permission created successfully",
            "created": True,
            "permission": permission
        }
    
    def update_permission(self, permission_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a permission.
        
        Args:
            permission_id: Permission ID
            updates: Dictionary of updates to apply
            
        Returns:
            Permission update result dictionary
        """
        logger.info(f"Updating permission: {permission_id}")
        
        # Check if permission exists
        if permission_id not in self.permission_store:
            logger.warning(f"Permission not found: {permission_id}")
            return {
                "status": "error",
                "message": "Permission not found",
                "updated": False
            }
        
        # Get permission
        permission = self.permission_store[permission_id]
        
        # Check if permission is a system permission
        if permission.get("system_permission", False) and not self.config.get("allow_system_permission_updates", False):
            logger.warning(f"Cannot update system permission: {permission_id}")
            return {
                "status": "error",
                "message": "Cannot update system permission",
                "updated": False
            }
        
        # Apply updates
        for key, value in updates.items():
            if key in ["permission_id", "created_at", "system_permission"]:
                # Don't allow updating these fields
                continue
            
            permission[key] = value
        
        # Update last modified timestamp
        permission["last_modified"] = time.time()
        
        # Store updated permission
        self.permission_store[permission_id] = permission
        
        logger.info(f"Permission updated successfully: {permission_id}")
        
        return {
            "status": "success",
            "message": "Permission updated successfully",
            "updated": True,
            "permission": permission
        }
    
    def delete_permission(self, permission_id: str) -> Dict[str, Any]:
        """
        Delete a permission.
        
        Args:
            permission_id: Permission ID
            
        Returns:
            Permission deletion result dictionary
        """
        logger.info(f"Deleting permission: {permission_id}")
        
        # Check if permission exists
        if permission_id not in self.permission_store:
            logger.warning(f"Permission not found: {permission_id}")
            return {
                "status": "error",
                "message": "Permission not found",
                "deleted": False
            }
        
        # Get permission
        permission = self.permission_store[permission_id]
        
        # Check if permission is a system permission
        if permission.get("system_permission", False) and not self.config.get("allow_system_permission_deletion", False):
            logger.warning(f"Cannot delete system permission: {permission_id}")
            return {
                "status": "error",
                "message": "Cannot delete system permission",
                "deleted": False
            }
        
        # Check if permission is used by any roles
        used_by_roles = []
        for role_id, role in self.role_store.items():
            if permission_id in role.get("permissions", []):
                used_by_roles.append(role_id)
        
        if used_by_roles:
            logger.warning(f"Permission is used by roles: {used_by_roles}")
            return {
                "status": "error",
                "message": f"Permission is used by roles: {used_by_roles}",
                "deleted": False
            }
        
        # Delete permission
        del self.permission_store[permission_id]
        
        logger.info(f"Permission deleted successfully: {permission_id}")
        
        return {
            "status": "success",
            "message": "Permission deleted successfully",
            "deleted": True,
            "permission_id": permission_id
        }
    
    def get_permission(self, permission_id: str) -> Dict[str, Any]:
        """
        Get a permission.
        
        Args:
            permission_id: Permission ID
            
        Returns:
            Permission dictionary
        """
        logger.info(f"Getting permission: {permission_id}")
        
        # Check if permission exists
        if permission_id not in self.permission_store:
            logger.warning(f"Permission not found: {permission_id}")
            return {
                "status": "error",
                "message": "Permission not found",
                "found": False
            }
        
        # Get permission
        permission = self.permission_store[permission_id]
        
        logger.info(f"Permission retrieved successfully: {permission_id}")
        
        return {
            "status": "success",
            "message": "Permission retrieved successfully",
            "found": True,
            "permission": permission
        }
    
    def list_permissions(self) -> Dict[str, Any]:
        """
        List all permissions.
        
        Returns:
            Dictionary containing list of permissions
        """
        logger.info("Listing permissions")
        
        permissions = list(self.permission_store.values())
        
        logger.info(f"Listed {len(permissions)} permissions")
        
        return {
            "status": "success",
            "message": "Permissions listed successfully",
            "permissions": permissions
        }
    
    def create_policy(self, policy_id: str, name: str, description: str, effect: str, resources: List[str], actions: List[str], conditions: Dict[str, Any], priority: int) -> Dict[str, Any]:
        """
        Create a new policy.
        
        Args:
            policy_id: Policy ID
            name: Policy name
            description: Policy description
            effect: Policy effect ("allow" or "deny")
            resources: List of resource patterns
            actions: List of action patterns
            conditions: Policy conditions
            priority: Policy priority
            
        Returns:
            Policy creation result dictionary
        """
        logger.info(f"Creating policy: {policy_id}")
        
        # Check if policy already exists
        if policy_id in self.policy_store:
            logger.warning(f"Policy already exists: {policy_id}")
            return {
                "status": "error",
                "message": "Policy already exists",
                "created": False
            }
        
        # Validate effect
        if effect not in ["allow", "deny"]:
            logger.warning(f"Invalid effect: {effect}")
            return {
                "status": "error",
                "message": f"Invalid effect: {effect}",
                "created": False
            }
        
        # Create policy
        policy = {
            "policy_id": policy_id,
            "name": name,
            "description": description,
            "effect": effect,
            "resources": resources,
            "actions": actions,
            "conditions": conditions,
            "priority": priority,
            "created_at": time.time(),
            "system_policy": False
        }
        
        # Store policy
        self.policy_store[policy_id] = policy
        
        logger.info(f"Policy created successfully: {policy_id}")
        
        return {
            "status": "success",
            "message": "Policy created successfully",
            "created": True,
            "policy": policy
        }
    
    def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a policy.
        
        Args:
            policy_id: Policy ID
            updates: Dictionary of updates to apply
            
        Returns:
            Policy update result dictionary
        """
        logger.info(f"Updating policy: {policy_id}")
        
        # Check if policy exists
        if policy_id not in self.policy_store:
            logger.warning(f"Policy not found: {policy_id}")
            return {
                "status": "error",
                "message": "Policy not found",
                "updated": False
            }
        
        # Get policy
        policy = self.policy_store[policy_id]
        
        # Check if policy is a system policy
        if policy.get("system_policy", False) and not self.config.get("allow_system_policy_updates", False):
            logger.warning(f"Cannot update system policy: {policy_id}")
            return {
                "status": "error",
                "message": "Cannot update system policy",
                "updated": False
            }
        
        # Validate effect if updating
        if "effect" in updates and updates["effect"] not in ["allow", "deny"]:
            logger.warning(f"Invalid effect: {updates['effect']}")
            return {
                "status": "error",
                "message": f"Invalid effect: {updates['effect']}",
                "updated": False
            }
        
        # Apply updates
        for key, value in updates.items():
            if key in ["policy_id", "created_at", "system_policy"]:
                # Don't allow updating these fields
                continue
            
            policy[key] = value
        
        # Update last modified timestamp
        policy["last_modified"] = time.time()
        
        # Store updated policy
        self.policy_store[policy_id] = policy
        
        logger.info(f"Policy updated successfully: {policy_id}")
        
        return {
            "status": "success",
            "message": "Policy updated successfully",
            "updated": True,
            "policy": policy
        }
    
    def delete_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Delete a policy.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Policy deletion result dictionary
        """
        logger.info(f"Deleting policy: {policy_id}")
        
        # Check if policy exists
        if policy_id not in self.policy_store:
            logger.warning(f"Policy not found: {policy_id}")
            return {
                "status": "error",
                "message": "Policy not found",
                "deleted": False
            }
        
        # Get policy
        policy = self.policy_store[policy_id]
        
        # Check if policy is a system policy
        if policy.get("system_policy", False) and not self.config.get("allow_system_policy_deletion", False):
            logger.warning(f"Cannot delete system policy: {policy_id}")
            return {
                "status": "error",
                "message": "Cannot delete system policy",
                "deleted": False
            }
        
        # Delete policy
        del self.policy_store[policy_id]
        
        logger.info(f"Policy deleted successfully: {policy_id}")
        
        return {
            "status": "success",
            "message": "Policy deleted successfully",
            "deleted": True,
            "policy_id": policy_id
        }
    
    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Get a policy.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Policy dictionary
        """
        logger.info(f"Getting policy: {policy_id}")
        
        # Check if policy exists
        if policy_id not in self.policy_store:
            logger.warning(f"Policy not found: {policy_id}")
            return {
                "status": "error",
                "message": "Policy not found",
                "found": False
            }
        
        # Get policy
        policy = self.policy_store[policy_id]
        
        logger.info(f"Policy retrieved successfully: {policy_id}")
        
        return {
            "status": "success",
            "message": "Policy retrieved successfully",
            "found": True,
            "policy": policy
        }
    
    def list_policies(self) -> Dict[str, Any]:
        """
        List all policies.
        
        Returns:
            Dictionary containing list of policies
        """
        logger.info("Listing policies")
        
        policies = list(self.policy_store.values())
        
        # Sort policies by priority (higher priority first)
        policies.sort(key=lambda p: p.get("priority", 0), reverse=True)
        
        logger.info(f"Listed {len(policies)} policies")
        
        return {
            "status": "success",
            "message": "Policies listed successfully",
            "policies": policies
        }
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        Clear the decision cache.
        
        Returns:
            Cache clearing result dictionary
        """
        logger.info("Clearing decision cache")
        
        cache_size = len(self.decision_cache)
        self.decision_cache = {}
        
        logger.info(f"Decision cache cleared ({cache_size} entries)")
        
        return {
            "status": "success",
            "message": "Decision cache cleared",
            "cleared": True,
            "cache_size": cache_size
        }
