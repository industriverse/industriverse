"""
Capsule ACL Service Module for the Security & Compliance Layer of Industriverse.

This module implements a comprehensive Capsule Access Control List (ACL) Service that supports:
- Fine-grained access control for capsules
- Role-based, attribute-based, and policy-based access control
- Dynamic permission adjustment based on trust scores
- Contextual access decisions
- Permission inheritance and delegation
- Access audit trails

The Capsule ACL Service is a critical component of the Zero-Trust Security architecture,
enabling secure and controlled access to capsules across the Industriverse ecosystem.
"""

import os
import time
import uuid
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CapsuleACLService:
    """
    Capsule ACL Service for the Security & Compliance Layer.
    
    This class provides comprehensive access control services for capsules including:
    - Fine-grained access control for capsules
    - Role-based, attribute-based, and policy-based access control
    - Dynamic permission adjustment based on trust scores
    - Contextual access decisions
    - Permission inheritance and delegation
    - Access audit trails
    """
    
    def __init__(self, config_path: str = None, trust_score_agent=None):
        """
        Initialize the Capsule ACL Service with configuration.
        
        Args:
            config_path: Path to the configuration file
            trust_score_agent: Trust Score Agent instance for trust-based decisions
        """
        self.config = self._load_config(config_path)
        self.trust_score_agent = trust_score_agent
        self.capsule_acls = {}
        self.role_definitions = {}
        self.permission_definitions = {}
        self.access_policies = {}
        self.access_audit_trail = {}
        
        # Initialize from configuration
        self._initialize_from_config()
        
        logger.info("Capsule ACL Service initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration
        """
        default_config = {
            "acl_types": {
                "rbac": True,  # Role-Based Access Control
                "abac": True,  # Attribute-Based Access Control
                "pbac": True   # Policy-Based Access Control
            },
            "default_permissions": {
                "owner": ["read", "write", "execute", "delete", "share", "admin"],
                "admin": ["read", "write", "execute", "admin"],
                "contributor": ["read", "write", "execute"],
                "executor": ["read", "execute"],
                "reader": ["read"]
            },
            "trust_based_access": {
                "enabled": True,
                "min_trust_levels": {
                    "admin": 80,
                    "write": 60,
                    "execute": 50,
                    "read": 30
                }
            },
            "contextual_access": {
                "enabled": True,
                "context_factors": {
                    "location": True,
                    "device": True,
                    "network": True,
                    "time": True
                }
            },
            "inheritance": {
                "enabled": True,
                "max_inheritance_depth": 5
            },
            "delegation": {
                "enabled": True,
                "max_delegation_chain": 3,
                "delegation_trust_decay": 0.8
            },
            "audit": {
                "enabled": True,
                "log_access_attempts": True,
                "log_policy_changes": True,
                "max_audit_entries": 1000,
                "retention_days": 90
            }
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
        """Initialize capsule ACL service components from configuration."""
        # Initialize default role definitions
        for role, permissions in self.config["default_permissions"].items():
            self.role_definitions[role] = {
                "name": role,
                "permissions": permissions,
                "description": f"Default {role} role",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Initialize default permission definitions
        default_permissions = {
            "read": {
                "name": "read",
                "description": "Permission to read capsule content",
                "operations": ["view", "download", "list"]
            },
            "write": {
                "name": "write",
                "description": "Permission to modify capsule content",
                "operations": ["create", "update", "upload"]
            },
            "execute": {
                "name": "execute",
                "description": "Permission to execute capsule operations",
                "operations": ["run", "invoke", "trigger"]
            },
            "delete": {
                "name": "delete",
                "description": "Permission to delete capsule",
                "operations": ["remove", "archive"]
            },
            "share": {
                "name": "share",
                "description": "Permission to share capsule with others",
                "operations": ["grant", "revoke"]
            },
            "admin": {
                "name": "admin",
                "description": "Permission to administer capsule",
                "operations": ["configure", "manage_acl", "audit"]
            }
        }
        
        for perm_name, perm_data in default_permissions.items():
            self.permission_definitions[perm_name] = perm_data
    
    def create_capsule_acl(self, capsule_id: str, owner_id: str, initial_acl: Dict = None) -> Dict:
        """
        Create a new ACL for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            owner_id: Owner entity identifier
            initial_acl: Initial ACL configuration
            
        Returns:
            Dict containing capsule ACL information
        """
        # Check if ACL already exists
        if capsule_id in self.capsule_acls:
            logger.warning(f"ACL for capsule {capsule_id} already exists, returning existing ACL")
            return self.capsule_acls[capsule_id]
        
        # Create default ACL
        acl = {
            "capsule_id": capsule_id,
            "owner_id": owner_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "rbac": {
                "roles": {
                    owner_id: "owner"
                },
                "custom_roles": {}
            },
            "abac": {
                "rules": []
            },
            "pbac": {
                "policies": []
            },
            "inheritance": {
                "parent_capsules": [],
                "child_capsules": []
            },
            "delegations": []
        }
        
        # Apply initial ACL if provided
        if initial_acl:
            if "rbac" in initial_acl and "roles" in initial_acl["rbac"]:
                # Ensure owner always has owner role
                roles = initial_acl["rbac"]["roles"]
                roles[owner_id] = "owner"
                acl["rbac"]["roles"] = roles
            
            if "abac" in initial_acl and "rules" in initial_acl["abac"]:
                acl["abac"]["rules"] = initial_acl["abac"]["rules"]
            
            if "pbac" in initial_acl and "policies" in initial_acl["pbac"]:
                acl["pbac"]["policies"] = initial_acl["pbac"]["policies"]
        
        # Store ACL
        self.capsule_acls[capsule_id] = acl
        
        # Initialize audit trail if enabled
        if self.config["audit"]["enabled"]:
            self.access_audit_trail[capsule_id] = []
            self._add_to_audit_trail(
                capsule_id,
                owner_id,
                "create_acl",
                True,
                {"action": "create_acl"}
            )
        
        logger.info(f"Created ACL for capsule {capsule_id} with owner {owner_id}")
        
        return acl
    
    def get_capsule_acl(self, capsule_id: str) -> Optional[Dict]:
        """
        Get ACL for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            
        Returns:
            Dict containing capsule ACL information if found, None otherwise
        """
        return self.capsule_acls.get(capsule_id)
    
    def assign_role(self, capsule_id: str, entity_id: str, role: str, assigner_id: str) -> bool:
        """
        Assign a role to an entity for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            entity_id: Entity identifier
            role: Role to assign
            assigner_id: Entity making the assignment
            
        Returns:
            True if assignment successful, False otherwise
        """
        # Check if RBAC is enabled
        if not self.config["acl_types"]["rbac"]:
            logger.warning("RBAC is not enabled")
            return False
        
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Check if role exists
        if role not in self.role_definitions and role not in self.capsule_acls[capsule_id]["rbac"]["custom_roles"]:
            logger.warning(f"Role {role} not found")
            return False
        
        # Check if assigner has admin permission
        if not self.check_permission(capsule_id, assigner_id, "admin"):
            logger.warning(f"Entity {assigner_id} does not have admin permission for capsule {capsule_id}")
            return False
        
        # Assign role
        self.capsule_acls[capsule_id]["rbac"]["roles"][entity_id] = role
        self.capsule_acls[capsule_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to audit trail if enabled
        if self.config["audit"]["enabled"]:
            self._add_to_audit_trail(
                capsule_id,
                assigner_id,
                "assign_role",
                True,
                {"entity_id": entity_id, "role": role}
            )
        
        logger.info(f"Assigned role {role} to entity {entity_id} for capsule {capsule_id}")
        
        return True
    
    def remove_role(self, capsule_id: str, entity_id: str, remover_id: str) -> bool:
        """
        Remove a role from an entity for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            entity_id: Entity identifier
            remover_id: Entity removing the role
            
        Returns:
            True if removal successful, False otherwise
        """
        # Check if RBAC is enabled
        if not self.config["acl_types"]["rbac"]:
            logger.warning("RBAC is not enabled")
            return False
        
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Check if entity has a role
        if entity_id not in self.capsule_acls[capsule_id]["rbac"]["roles"]:
            logger.warning(f"Entity {entity_id} does not have a role for capsule {capsule_id}")
            return False
        
        # Check if remover has admin permission
        if not self.check_permission(capsule_id, remover_id, "admin"):
            logger.warning(f"Entity {remover_id} does not have admin permission for capsule {capsule_id}")
            return False
        
        # Cannot remove owner's role
        if entity_id == self.capsule_acls[capsule_id]["owner_id"]:
            logger.warning(f"Cannot remove role from owner {entity_id}")
            return False
        
        # Remove role
        del self.capsule_acls[capsule_id]["rbac"]["roles"][entity_id]
        self.capsule_acls[capsule_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to audit trail if enabled
        if self.config["audit"]["enabled"]:
            self._add_to_audit_trail(
                capsule_id,
                remover_id,
                "remove_role",
                True,
                {"entity_id": entity_id}
            )
        
        logger.info(f"Removed role from entity {entity_id} for capsule {capsule_id}")
        
        return True
    
    def create_custom_role(self, capsule_id: str, role_name: str, permissions: List[str], creator_id: str) -> bool:
        """
        Create a custom role for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            role_name: Custom role name
            permissions: List of permissions for the role
            creator_id: Entity creating the role
            
        Returns:
            True if creation successful, False otherwise
        """
        # Check if RBAC is enabled
        if not self.config["acl_types"]["rbac"]:
            logger.warning("RBAC is not enabled")
            return False
        
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Check if creator has admin permission
        if not self.check_permission(capsule_id, creator_id, "admin"):
            logger.warning(f"Entity {creator_id} does not have admin permission for capsule {capsule_id}")
            return False
        
        # Validate permissions
        for permission in permissions:
            if permission not in self.permission_definitions:
                logger.warning(f"Permission {permission} not found")
                return False
        
        # Create custom role
        self.capsule_acls[capsule_id]["rbac"]["custom_roles"][role_name] = {
            "name": role_name,
            "permissions": permissions,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": creator_id
        }
        
        self.capsule_acls[capsule_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to audit trail if enabled
        if self.config["audit"]["enabled"]:
            self._add_to_audit_trail(
                capsule_id,
                creator_id,
                "create_custom_role",
                True,
                {"role_name": role_name, "permissions": permissions}
            )
        
        logger.info(f"Created custom role {role_name} for capsule {capsule_id}")
        
        return True
    
    def add_attribute_rule(self, capsule_id: str, attribute: str, value: Any, permissions: List[str], creator_id: str) -> bool:
        """
        Add an attribute-based access control rule.
        
        Args:
            capsule_id: Capsule identifier
            attribute: Entity attribute to check
            value: Required attribute value
            permissions: Permissions granted if attribute matches
            creator_id: Entity creating the rule
            
        Returns:
            True if addition successful, False otherwise
        """
        # Check if ABAC is enabled
        if not self.config["acl_types"]["abac"]:
            logger.warning("ABAC is not enabled")
            return False
        
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Check if creator has admin permission
        if not self.check_permission(capsule_id, creator_id, "admin"):
            logger.warning(f"Entity {creator_id} does not have admin permission for capsule {capsule_id}")
            return False
        
        # Validate permissions
        for permission in permissions:
            if permission not in self.permission_definitions:
                logger.warning(f"Permission {permission} not found")
                return False
        
        # Create rule
        rule = {
            "id": str(uuid.uuid4()),
            "attribute": attribute,
            "value": value,
            "permissions": permissions,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": creator_id
        }
        
        # Add rule
        self.capsule_acls[capsule_id]["abac"]["rules"].append(rule)
        self.capsule_acls[capsule_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to audit trail if enabled
        if self.config["audit"]["enabled"]:
            self._add_to_audit_trail(
                capsule_id,
                creator_id,
                "add_attribute_rule",
                True,
                {"attribute": attribute, "value": value, "permissions": permissions}
            )
        
        logger.info(f"Added attribute rule for {attribute}={value} to capsule {capsule_id}")
        
        return True
    
    def remove_attribute_rule(self, capsule_id: str, rule_id: str, remover_id: str) -> bool:
        """
        Remove an attribute-based access control rule.
        
        Args:
            capsule_id: Capsule identifier
            rule_id: Rule identifier
            remover_id: Entity removing the rule
            
        Returns:
            True if removal successful, False otherwise
        """
        # Check if ABAC is enabled
        if not self.config["acl_types"]["abac"]:
            logger.warning("ABAC is not enabled")
            return False
        
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Check if remover has admin permission
        if not self.check_permission(capsule_id, remover_id, "admin"):
            logger.warning(f"Entity {remover_id} does not have admin permission for capsule {capsule_id}")
            return False
        
        # Find rule
        rules = self.capsule_acls[capsule_id]["abac"]["rules"]
        for i, rule in enumerate(rules):
            if rule["id"] == rule_id:
                # Remove rule
                del rules[i]
                self.capsule_acls[capsule_id]["updated_at"] = datetime.utcnow().isoformat()
                
                # Add to audit trail if enabled
                if self.config["audit"]["enabled"]:
                    self._add_to_audit_trail(
                        capsule_id,
                        remover_id,
                        "remove_attribute_rule",
                        True,
                        {"rule_id": rule_id}
                    )
                
                logger.info(f"Removed attribute rule {rule_id} from capsule {capsule_id}")
                
                return True
        
        logger.warning(f"Rule {rule_id} not found for capsule {capsule_id}")
        return False
    
    def add_policy(self, capsule_id: str, policy_name: str, policy_condition: Dict, permissions: List[str], creator_id: str) -> bool:
        """
        Add a policy-based access control policy.
        
        Args:
            capsule_id: Capsule identifier
            policy_name: Policy name
            policy_condition: Policy condition (e.g., {"type": "time_range", "start": "09:00", "end": "17:00"})
            permissions: Permissions granted if policy condition is met
            creator_id: Entity creating the policy
            
        Returns:
            True if addition successful, False otherwise
        """
        # Check if PBAC is enabled
        if not self.config["acl_types"]["pbac"]:
            logger.warning("PBAC is not enabled")
            return False
        
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Check if creator has admin permission
        if not self.check_permission(capsule_id, creator_id, "admin"):
            logger.warning(f"Entity {creator_id} does not have admin permission for capsule {capsule_id}")
            return False
        
        # Validate permissions
        for permission in permissions:
            if permission not in self.permission_definitions:
                logger.warning(f"Permission {permission} not found")
                return False
        
        # Create policy
        policy = {
            "id": str(uuid.uuid4()),
            "name": policy_name,
            "condition": policy_condition,
            "permissions": permissions,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": creator_id
        }
        
        # Add policy
        self.capsule_acls[capsule_id]["pbac"]["policies"].append(policy)
        self.capsule_acls[capsule_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to audit trail if enabled
        if self.config["audit"]["enabled"]:
            self._add_to_audit_trail(
                capsule_id,
                creator_id,
                "add_policy",
                True,
                {"policy_name": policy_name, "condition": policy_condition, "permissions": permissions}
            )
        
        logger.info(f"Added policy {policy_name} to capsule {capsule_id}")
        
        return True
    
    def remove_policy(self, capsule_id: str, policy_id: str, remover_id: str) -> bool:
        """
        Remove a policy-based access control policy.
        
        Args:
            capsule_id: Capsule identifier
            policy_id: Policy identifier
            remover_id: Entity removing the policy
            
        Returns:
            True if removal successful, False otherwise
        """
        # Check if PBAC is enabled
        if not self.config["acl_types"]["pbac"]:
            logger.warning("PBAC is not enabled")
            return False
        
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Check if remover has admin permission
        if not self.check_permission(capsule_id, remover_id, "admin"):
            logger.warning(f"Entity {remover_id} does not have admin permission for capsule {capsule_id}")
            return False
        
        # Find policy
        policies = self.capsule_acls[capsule_id]["pbac"]["policies"]
        for i, policy in enumerate(policies):
            if policy["id"] == policy_id:
                # Remove policy
                del policies[i]
                self.capsule_acls[capsule_id]["updated_at"] = datetime.utcnow().isoformat()
                
                # Add to audit trail if enabled
                if self.config["audit"]["enabled"]:
                    self._add_to_audit_trail(
                        capsule_id,
                        remover_id,
                        "remove_policy",
                        True,
                        {"policy_id": policy_id}
                    )
                
                logger.info(f"Removed policy {policy_id} from capsule {capsule_id}")
                
                return True
        
        logger.warning(f"Policy {policy_id} not found for capsule {capsule_id}")
        return False
    
    def add_inheritance(self, child_capsule_id: str, parent_capsule_id: str, adder_id: str) -> bool:
        """
        Add an inheritance relationship between capsules.
        
        Args:
            child_capsule_id: Child capsule identifier
            parent_capsule_id: Parent capsule identifier
            adder_id: Entity adding the inheritance
            
        Returns:
            True if addition successful, False otherwise
        """
        # Check if inheritance is enabled
        if not self.config["inheritance"]["enabled"]:
            logger.warning("Inheritance is not enabled")
            return False
        
        # Check if capsules exist
        if child_capsule_id not in self.capsule_acls:
            logger.warning(f"Child capsule {child_capsule_id} not found")
            return False
        
        if parent_capsule_id not in self.capsule_acls:
            logger.warning(f"Parent capsule {parent_capsule_id} not found")
            return False
        
        # Check if adder has admin permission for both capsules
        if not self.check_permission(child_capsule_id, adder_id, "admin"):
            logger.warning(f"Entity {adder_id} does not have admin permission for child capsule {child_capsule_id}")
            return False
        
        if not self.check_permission(parent_capsule_id, adder_id, "admin"):
            logger.warning(f"Entity {adder_id} does not have admin permission for parent capsule {parent_capsule_id}")
            return False
        
        # Check for circular inheritance
        if self._would_create_circular_inheritance(child_capsule_id, parent_capsule_id):
            logger.warning(f"Adding inheritance from {parent_capsule_id} to {child_capsule_id} would create a circular inheritance")
            return False
        
        # Check inheritance depth
        if self._get_inheritance_depth(parent_capsule_id) >= self.config["inheritance"]["max_inheritance_depth"]:
            logger.warning(f"Maximum inheritance depth reached for parent capsule {parent_capsule_id}")
            return False
        
        # Add inheritance
        child_acl = self.capsule_acls[child_capsule_id]
        parent_acl = self.capsule_acls[parent_capsule_id]
        
        # Add parent to child's parents
        if parent_capsule_id not in child_acl["inheritance"]["parent_capsules"]:
            child_acl["inheritance"]["parent_capsules"].append(parent_capsule_id)
        
        # Add child to parent's children
        if child_capsule_id not in parent_acl["inheritance"]["child_capsules"]:
            parent_acl["inheritance"]["child_capsules"].append(child_capsule_id)
        
        # Update timestamps
        child_acl["updated_at"] = datetime.utcnow().isoformat()
        parent_acl["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to audit trail if enabled
        if self.config["audit"]["enabled"]:
            self._add_to_audit_trail(
                child_capsule_id,
                adder_id,
                "add_inheritance",
                True,
                {"parent_capsule_id": parent_capsule_id}
            )
        
        logger.info(f"Added inheritance from parent capsule {parent_capsule_id} to child capsule {child_capsule_id}")
        
        return True
    
    def remove_inheritance(self, child_capsule_id: str, parent_capsule_id: str, remover_id: str) -> bool:
        """
        Remove an inheritance relationship between capsules.
        
        Args:
            child_capsule_id: Child capsule identifier
            parent_capsule_id: Parent capsule identifier
            remover_id: Entity removing the inheritance
            
        Returns:
            True if removal successful, False otherwise
        """
        # Check if inheritance is enabled
        if not self.config["inheritance"]["enabled"]:
            logger.warning("Inheritance is not enabled")
            return False
        
        # Check if capsules exist
        if child_capsule_id not in self.capsule_acls:
            logger.warning(f"Child capsule {child_capsule_id} not found")
            return False
        
        if parent_capsule_id not in self.capsule_acls:
            logger.warning(f"Parent capsule {parent_capsule_id} not found")
            return False
        
        # Check if remover has admin permission for both capsules
        if not self.check_permission(child_capsule_id, remover_id, "admin"):
            logger.warning(f"Entity {remover_id} does not have admin permission for child capsule {child_capsule_id}")
            return False
        
        if not self.check_permission(parent_capsule_id, remover_id, "admin"):
            logger.warning(f"Entity {remover_id} does not have admin permission for parent capsule {parent_capsule_id}")
            return False
        
        # Check if inheritance exists
        child_acl = self.capsule_acls[child_capsule_id]
        parent_acl = self.capsule_acls[parent_capsule_id]
        
        if parent_capsule_id not in child_acl["inheritance"]["parent_capsules"]:
            logger.warning(f"No inheritance from parent capsule {parent_capsule_id} to child capsule {child_capsule_id}")
            return False
        
        # Remove inheritance
        child_acl["inheritance"]["parent_capsules"].remove(parent_capsule_id)
        
        if child_capsule_id in parent_acl["inheritance"]["child_capsules"]:
            parent_acl["inheritance"]["child_capsules"].remove(child_capsule_id)
        
        # Update timestamps
        child_acl["updated_at"] = datetime.utcnow().isoformat()
        parent_acl["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to audit trail if enabled
        if self.config["audit"]["enabled"]:
            self._add_to_audit_trail(
                child_capsule_id,
                remover_id,
                "remove_inheritance",
                True,
                {"parent_capsule_id": parent_capsule_id}
            )
        
        logger.info(f"Removed inheritance from parent capsule {parent_capsule_id} to child capsule {child_capsule_id}")
        
        return True
    
    def _would_create_circular_inheritance(self, child_capsule_id: str, parent_capsule_id: str) -> bool:
        """
        Check if adding an inheritance relationship would create a circular inheritance.
        
        Args:
            child_capsule_id: Child capsule identifier
            parent_capsule_id: Parent capsule identifier
            
        Returns:
            True if circular inheritance would be created, False otherwise
        """
        # If parent is the same as child, it's circular
        if child_capsule_id == parent_capsule_id:
            return True
        
        # Check if child is already a parent of the parent (directly or indirectly)
        visited = set()
        to_visit = [child_capsule_id]
        
        while to_visit:
            current = to_visit.pop()
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current not in self.capsule_acls:
                continue
            
            # Get all children of the current capsule
            children = self.capsule_acls[current]["inheritance"]["child_capsules"]
            
            # If parent is a child of the current capsule, it would create a cycle
            if parent_capsule_id in children:
                return True
            
            # Add all children to the visit list
            to_visit.extend(children)
        
        return False
    
    def _get_inheritance_depth(self, capsule_id: str) -> int:
        """
        Get the inheritance depth of a capsule.
        
        Args:
            capsule_id: Capsule identifier
            
        Returns:
            Inheritance depth
        """
        if capsule_id not in self.capsule_acls:
            return 0
        
        # Get all parents
        parents = self.capsule_acls[capsule_id]["inheritance"]["parent_capsules"]
        
        if not parents:
            return 0
        
        # Recursively get the maximum depth of all parents
        max_parent_depth = 0
        for parent_id in parents:
            parent_depth = self._get_inheritance_depth(parent_id)
            max_parent_depth = max(max_parent_depth, parent_depth)
        
        return max_parent_depth + 1
    
    def add_delegation(self, capsule_id: str, delegator_id: str, delegatee_id: str, permissions: List[str], expiration: datetime = None) -> bool:
        """
        Add a delegation of permissions from one entity to another.
        
        Args:
            capsule_id: Capsule identifier
            delegator_id: Entity delegating permissions
            delegatee_id: Entity receiving delegated permissions
            permissions: Permissions to delegate
            expiration: Expiration time for the delegation
            
        Returns:
            True if addition successful, False otherwise
        """
        # Check if delegation is enabled
        if not self.config["delegation"]["enabled"]:
            logger.warning("Delegation is not enabled")
            return False
        
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Check if delegator has the permissions to delegate
        for permission in permissions:
            if not self.check_permission(capsule_id, delegator_id, permission):
                logger.warning(f"Entity {delegator_id} does not have permission {permission} for capsule {capsule_id}")
                return False
        
        # Set default expiration if not provided
        if expiration is None:
            expiration = datetime.utcnow() + timedelta(days=30)
        
        # Create delegation
        delegation = {
            "id": str(uuid.uuid4()),
            "delegator_id": delegator_id,
            "delegatee_id": delegatee_id,
            "permissions": permissions,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expiration.isoformat(),
            "status": "active"
        }
        
        # Add delegation
        self.capsule_acls[capsule_id]["delegations"].append(delegation)
        self.capsule_acls[capsule_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to audit trail if enabled
        if self.config["audit"]["enabled"]:
            self._add_to_audit_trail(
                capsule_id,
                delegator_id,
                "add_delegation",
                True,
                {"delegatee_id": delegatee_id, "permissions": permissions, "expires_at": expiration.isoformat()}
            )
        
        logger.info(f"Added delegation from {delegator_id} to {delegatee_id} for capsule {capsule_id}")
        
        return True
    
    def revoke_delegation(self, capsule_id: str, delegation_id: str, revoker_id: str) -> bool:
        """
        Revoke a delegation.
        
        Args:
            capsule_id: Capsule identifier
            delegation_id: Delegation identifier
            revoker_id: Entity revoking the delegation
            
        Returns:
            True if revocation successful, False otherwise
        """
        # Check if delegation is enabled
        if not self.config["delegation"]["enabled"]:
            logger.warning("Delegation is not enabled")
            return False
        
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Find delegation
        delegations = self.capsule_acls[capsule_id]["delegations"]
        for i, delegation in enumerate(delegations):
            if delegation["id"] == delegation_id:
                # Check if revoker is the delegator or has admin permission
                if revoker_id != delegation["delegator_id"] and not self.check_permission(capsule_id, revoker_id, "admin"):
                    logger.warning(f"Entity {revoker_id} cannot revoke delegation {delegation_id}")
                    return False
                
                # Revoke delegation
                delegation["status"] = "revoked"
                delegation["revoked_at"] = datetime.utcnow().isoformat()
                delegation["revoked_by"] = revoker_id
                
                self.capsule_acls[capsule_id]["updated_at"] = datetime.utcnow().isoformat()
                
                # Add to audit trail if enabled
                if self.config["audit"]["enabled"]:
                    self._add_to_audit_trail(
                        capsule_id,
                        revoker_id,
                        "revoke_delegation",
                        True,
                        {"delegation_id": delegation_id}
                    )
                
                logger.info(f"Revoked delegation {delegation_id} for capsule {capsule_id}")
                
                return True
        
        logger.warning(f"Delegation {delegation_id} not found for capsule {capsule_id}")
        return False
    
    def check_permission(self, capsule_id: str, entity_id: str, permission: str, context: Dict = None) -> bool:
        """
        Check if an entity has a specific permission for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            entity_id: Entity identifier
            permission: Permission to check
            context: Context information for contextual access decisions
            
        Returns:
            True if entity has permission, False otherwise
        """
        # Check if capsule exists
        if capsule_id not in self.capsule_acls:
            logger.warning(f"Capsule {capsule_id} not found")
            return False
        
        # Get capsule ACL
        acl = self.capsule_acls[capsule_id]
        
        # Check if entity is the owner
        if entity_id == acl["owner_id"]:
            # Add to audit trail if enabled
            if self.config["audit"]["enabled"]:
                self._add_to_audit_trail(
                    capsule_id,
                    entity_id,
                    "check_permission",
                    True,
                    {"permission": permission, "reason": "owner"}
                )
            
            return True
        
        # Check RBAC if enabled
        if self.config["acl_types"]["rbac"]:
            # Check if entity has a role
            if entity_id in acl["rbac"]["roles"]:
                role = acl["rbac"]["roles"][entity_id]
                
                # Get role definition
                role_def = None
                if role in self.role_definitions:
                    role_def = self.role_definitions[role]
                elif role in acl["rbac"]["custom_roles"]:
                    role_def = acl["rbac"]["custom_roles"][role]
                
                if role_def and permission in role_def["permissions"]:
                    # Check trust-based access if enabled
                    if self.config["trust_based_access"]["enabled"] and self.trust_score_agent:
                        min_trust = self.config["trust_based_access"]["min_trust_levels"].get(permission, 0)
                        trust_record = self.trust_score_agent.get_trust_score(entity_id)
                        
                        if trust_record and trust_record["score"] < min_trust:
                            # Add to audit trail if enabled
                            if self.config["audit"]["enabled"]:
                                self._add_to_audit_trail(
                                    capsule_id,
                                    entity_id,
                                    "check_permission",
                                    False,
                                    {"permission": permission, "reason": "insufficient_trust", "trust_score": trust_record["score"], "min_trust": min_trust}
                                )
                            
                            return False
                    
                    # Add to audit trail if enabled
                    if self.config["audit"]["enabled"]:
                        self._add_to_audit_trail(
                            capsule_id,
                            entity_id,
                            "check_permission",
                            True,
                            {"permission": permission, "reason": "rbac", "role": role}
                        )
                    
                    return True
        
        # Check ABAC if enabled
        if self.config["acl_types"]["abac"] and context:
            for rule in acl["abac"]["rules"]:
                attribute = rule["attribute"]
                value = rule["value"]
                
                if attribute in context and context[attribute] == value and permission in rule["permissions"]:
                    # Add to audit trail if enabled
                    if self.config["audit"]["enabled"]:
                        self._add_to_audit_trail(
                            capsule_id,
                            entity_id,
                            "check_permission",
                            True,
                            {"permission": permission, "reason": "abac", "attribute": attribute, "value": value}
                        )
                    
                    return True
        
        # Check PBAC if enabled
        if self.config["acl_types"]["pbac"] and context:
            for policy in acl["pbac"]["policies"]:
                if permission in policy["permissions"] and self._evaluate_policy_condition(policy["condition"], context):
                    # Add to audit trail if enabled
                    if self.config["audit"]["enabled"]:
                        self._add_to_audit_trail(
                            capsule_id,
                            entity_id,
                            "check_permission",
                            True,
                            {"permission": permission, "reason": "pbac", "policy": policy["name"]}
                        )
                    
                    return True
        
        # Check delegations if enabled
        if self.config["delegation"]["enabled"]:
            for delegation in acl["delegations"]:
                if delegation["delegatee_id"] == entity_id and delegation["status"] == "active" and permission in delegation["permissions"]:
                    # Check if delegation is expired
                    expires_at = datetime.fromisoformat(delegation["expires_at"])
                    if expires_at < datetime.utcnow():
                        continue
                    
                    # Add to audit trail if enabled
                    if self.config["audit"]["enabled"]:
                        self._add_to_audit_trail(
                            capsule_id,
                            entity_id,
                            "check_permission",
                            True,
                            {"permission": permission, "reason": "delegation", "delegator_id": delegation["delegator_id"]}
                        )
                    
                    return True
        
        # Check inheritance if enabled
        if self.config["inheritance"]["enabled"]:
            for parent_id in acl["inheritance"]["parent_capsules"]:
                if self.check_permission(parent_id, entity_id, permission, context):
                    # Add to audit trail if enabled
                    if self.config["audit"]["enabled"]:
                        self._add_to_audit_trail(
                            capsule_id,
                            entity_id,
                            "check_permission",
                            True,
                            {"permission": permission, "reason": "inheritance", "parent_capsule_id": parent_id}
                        )
                    
                    return True
        
        # Add to audit trail if enabled
        if self.config["audit"]["enabled"]:
            self._add_to_audit_trail(
                capsule_id,
                entity_id,
                "check_permission",
                False,
                {"permission": permission, "reason": "no_permission"}
            )
        
        return False
    
    def _evaluate_policy_condition(self, condition: Dict, context: Dict) -> bool:
        """
        Evaluate a policy condition against context.
        
        Args:
            condition: Policy condition
            context: Context information
            
        Returns:
            True if condition is met, False otherwise
        """
        condition_type = condition.get("type")
        
        if condition_type == "time_range":
            # Check if current time is within range
            if "time" not in context:
                return False
            
            current_time = context["time"]
            if isinstance(current_time, datetime):
                current_time = current_time.strftime("%H:%M")
            
            start_time = condition.get("start", "00:00")
            end_time = condition.get("end", "23:59")
            
            return start_time <= current_time <= end_time
        
        elif condition_type == "location":
            # Check if current location matches
            if "location" not in context:
                return False
            
            allowed_locations = condition.get("locations", [])
            return context["location"] in allowed_locations
        
        elif condition_type == "device":
            # Check if current device matches
            if "device" not in context:
                return False
            
            allowed_devices = condition.get("devices", [])
            return context["device"] in allowed_devices
        
        elif condition_type == "network":
            # Check if current network matches
            if "network" not in context:
                return False
            
            allowed_networks = condition.get("networks", [])
            return context["network"] in allowed_networks
        
        elif condition_type == "composite":
            # Evaluate composite condition (AND, OR, NOT)
            operator = condition.get("operator")
            subconditions = condition.get("conditions", [])
            
            if operator == "AND":
                return all(self._evaluate_policy_condition(subcond, context) for subcond in subconditions)
            
            elif operator == "OR":
                return any(self._evaluate_policy_condition(subcond, context) for subcond in subconditions)
            
            elif operator == "NOT":
                if len(subconditions) != 1:
                    return False
                
                return not self._evaluate_policy_condition(subconditions[0], context)
        
        return False
    
    def _add_to_audit_trail(self, capsule_id: str, entity_id: str, action: str, success: bool, details: Dict = None):
        """
        Add an entry to the access audit trail.
        
        Args:
            capsule_id: Capsule identifier
            entity_id: Entity identifier
            action: Action performed
            success: Whether the action was successful
            details: Additional details about the action
        """
        # Initialize audit trail for capsule if not exists
        if capsule_id not in self.access_audit_trail:
            self.access_audit_trail[capsule_id] = []
        
        # Create audit entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "entity_id": entity_id,
            "action": action,
            "success": success,
            "details": details or {}
        }
        
        # Add to audit trail
        self.access_audit_trail[capsule_id].append(audit_entry)
        
        # Trim audit trail if it exceeds max size
        max_entries = self.config["audit"]["max_audit_entries"]
        if len(self.access_audit_trail[capsule_id]) > max_entries:
            self.access_audit_trail[capsule_id] = self.access_audit_trail[capsule_id][-max_entries:]
        
        # Remove old audit entries
        retention_days = self.config["audit"]["retention_days"]
        if retention_days > 0:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            self.access_audit_trail[capsule_id] = [
                entry for entry in self.access_audit_trail[capsule_id]
                if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
            ]
    
    def get_audit_trail(self, capsule_id: str, entity_id: str = None, action: str = None, start_time: datetime = None, end_time: datetime = None, limit: int = None) -> List[Dict]:
        """
        Get access audit trail for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            entity_id: Filter by entity identifier
            action: Filter by action
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of entries to return
            
        Returns:
            List of audit trail entries
        """
        # Check if audit is enabled
        if not self.config["audit"]["enabled"]:
            return []
        
        # Check if capsule exists
        if capsule_id not in self.access_audit_trail:
            return []
        
        # Get audit trail
        audit_trail = self.access_audit_trail[capsule_id]
        
        # Apply filters
        if entity_id is not None:
            audit_trail = [entry for entry in audit_trail if entry["entity_id"] == entity_id]
        
        if action is not None:
            audit_trail = [entry for entry in audit_trail if entry["action"] == action]
        
        if start_time is not None:
            audit_trail = [entry for entry in audit_trail if datetime.fromisoformat(entry["timestamp"]) >= start_time]
        
        if end_time is not None:
            audit_trail = [entry for entry in audit_trail if datetime.fromisoformat(entry["timestamp"]) <= end_time]
        
        # Sort by timestamp (newest first)
        audit_trail.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        if limit is not None and limit > 0:
            audit_trail = audit_trail[:limit]
        
        return audit_trail


# Example usage
if __name__ == "__main__":
    # Initialize Capsule ACL Service
    acl_service = CapsuleACLService()
    
    # Create capsule ACL
    capsule_id = "capsule123"
    owner_id = "user456"
    acl = acl_service.create_capsule_acl(capsule_id, owner_id)
    
    print(f"Created ACL for capsule {capsule_id} with owner {owner_id}")
    
    # Assign roles
    acl_service.assign_role(capsule_id, "user789", "contributor", owner_id)
    acl_service.assign_role(capsule_id, "user101", "reader", owner_id)
    
    # Create custom role
    acl_service.create_custom_role(capsule_id, "developer", ["read", "write", "execute"], owner_id)
    acl_service.assign_role(capsule_id, "user202", "developer", owner_id)
    
    # Add attribute rule
    acl_service.add_attribute_rule(capsule_id, "department", "engineering", ["read", "execute"], owner_id)
    
    # Add policy
    acl_service.add_policy(
        capsule_id,
        "business_hours",
        {"type": "time_range", "start": "09:00", "end": "17:00"},
        ["read", "execute"],
        owner_id
    )
    
    # Check permissions
    context = {
        "time": "14:30",
        "department": "engineering",
        "location": "office",
        "device": "laptop"
    }
    
    print(f"Owner has admin permission: {acl_service.check_permission(capsule_id, owner_id, 'admin')}")
    print(f"Contributor has write permission: {acl_service.check_permission(capsule_id, 'user789', 'write')}")
    print(f"Reader has read permission: {acl_service.check_permission(capsule_id, 'user101', 'read')}")
    print(f"Reader has write permission: {acl_service.check_permission(capsule_id, 'user101', 'write')}")
    print(f"Engineering department has execute permission: {acl_service.check_permission(capsule_id, 'user303', 'execute', context)}")
    
    # Add delegation
    acl_service.add_delegation(capsule_id, "user789", "user404", ["read", "execute"])
    
    print(f"Delegated user has execute permission: {acl_service.check_permission(capsule_id, 'user404', 'execute')}")
    
    # Revoke delegation
    delegations = acl_service.capsule_acls[capsule_id]["delegations"]
    if delegations:
        acl_service.revoke_delegation(capsule_id, delegations[0]["id"], "user789")
        print(f"Delegation revoked, user now has execute permission: {acl_service.check_permission(capsule_id, 'user404', 'execute')}")
    
    # Get audit trail
    audit_trail = acl_service.get_audit_trail(capsule_id)
    print(f"Audit trail entries: {len(audit_trail)}")
    for entry in audit_trail[:5]:  # Show first 5 entries
        print(f"  {entry['timestamp']}: {entry['entity_id']} {entry['action']} - {entry['success']}")
