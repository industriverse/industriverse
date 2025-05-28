"""
Multi-Tenant Isolation Module for the Workflow Automation Layer.

This module implements multi-tenant isolation for workflow execution, ensuring
secure segregation of client workflows and data. It provides mechanisms for
tenant management, resource isolation, and secure cross-tenant communication
when explicitly permitted.

Key features:
- Tenant management and isolation
- Resource allocation and quotas
- Secure cross-tenant communication
- Tenant-specific configuration
- Audit logging for tenant operations
"""

import os
import json
import time
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class TenantManager:
    """
    Manages tenant registration, configuration, and isolation.
    
    This class provides methods for creating and managing tenants,
    and for enforcing isolation between tenant resources.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Tenant Manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.tenants = {}
        self._load_tenants()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "tenant_storage_path": "/data/tenants",
            "default_resource_quotas": {
                "max_workflows": 100,
                "max_concurrent_executions": 20,
                "max_storage_mb": 1000,
                "max_agents": 50
            },
            "isolation_level": "strict",  # strict, permissive, or custom
            "enable_cross_tenant_communication": False,
            "audit_log_retention_days": 90
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
            except Exception as e:
                print(f"Error loading config: {e}")
                
        return default_config
    
    def _load_tenants(self):
        """Load tenants from persistent storage."""
        storage_path = self.config["tenant_storage_path"]
        
        if os.path.exists(storage_path):
            for filename in os.listdir(storage_path):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(storage_path, filename), 'r') as f:
                            tenant = json.load(f)
                            self.tenants[tenant["tenant_id"]] = tenant
                    except Exception as e:
                        print(f"Error loading tenant {filename}: {e}")
    
    def create_tenant(self, 
                     name: str, 
                     description: Optional[str] = None,
                     resource_quotas: Optional[Dict[str, Any]] = None,
                     custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new tenant.
        
        Args:
            name: Name of the tenant
            description: Optional description of the tenant
            resource_quotas: Optional resource quotas for the tenant
            custom_config: Optional custom configuration for the tenant
            
        Returns:
            Tenant data
        """
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Use default resource quotas if not specified
        if resource_quotas is None:
            resource_quotas = self.config["default_resource_quotas"]
        
        tenant = {
            "tenant_id": tenant_id,
            "name": name,
            "description": description or "",
            "creation_time": time.time(),
            "last_updated": time.time(),
            "resource_quotas": resource_quotas,
            "resource_usage": {
                "workflows": 0,
                "concurrent_executions": 0,
                "storage_mb": 0,
                "agents": 0
            },
            "status": "active",
            "api_keys": [],
            "custom_config": custom_config or {}
        }
        
        # Generate an API key for the tenant
        api_key = self._generate_api_key(tenant_id)
        tenant["api_keys"].append({
            "key_id": f"key-{uuid.uuid4()}",
            "key_hash": self._hash_api_key(api_key),
            "creation_time": time.time(),
            "last_used": None,
            "status": "active",
            "description": "Default API key"
        })
        
        self.tenants[tenant_id] = tenant
        self._store_tenant(tenant)
        
        # Return the tenant data with the plaintext API key
        return {
            **tenant,
            "api_key": api_key
        }
    
    def _generate_api_key(self, tenant_id: str) -> str:
        """
        Generate an API key for a tenant.
        
        Args:
            tenant_id: Identifier for the tenant
            
        Returns:
            API key
        """
        # Generate a random UUID and combine with tenant ID
        random_uuid = str(uuid.uuid4())
        key_material = f"{tenant_id}:{random_uuid}:{time.time()}"
        
        # Hash the key material to create the API key
        hash_obj = hashlib.sha256(key_material.encode('utf-8'))
        api_key = hash_obj.hexdigest()
        
        return api_key
    
    def _hash_api_key(self, api_key: str) -> str:
        """
        Hash an API key for secure storage.
        
        Args:
            api_key: API key to hash
            
        Returns:
            Hashed API key
        """
        # In a production environment, this would use a secure password hashing algorithm
        # For this implementation, we'll use a simple hash
        hash_obj = hashlib.sha256(api_key.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _store_tenant(self, tenant: Dict[str, Any]):
        """
        Store a tenant to persistent storage.
        
        Args:
            tenant: The tenant data to store
        """
        storage_path = self.config["tenant_storage_path"]
        os.makedirs(storage_path, exist_ok=True)
        
        file_path = os.path.join(storage_path, f"{tenant['tenant_id']}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(tenant, f)
        except Exception as e:
            print(f"Error storing tenant: {e}")
    
    def get_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a tenant by its identifier.
        
        Args:
            tenant_id: Identifier for the tenant
            
        Returns:
            The tenant data if found, None otherwise
        """
        return self.tenants.get(tenant_id)
    
    def authenticate_tenant(self, api_key: str) -> Optional[str]:
        """
        Authenticate a tenant using an API key.
        
        Args:
            api_key: API key to authenticate
            
        Returns:
            Tenant ID if authenticated, None otherwise
        """
        api_key_hash = self._hash_api_key(api_key)
        
        for tenant_id, tenant in self.tenants.items():
            for key in tenant["api_keys"]:
                if key["key_hash"] == api_key_hash and key["status"] == "active":
                    # Update last used timestamp
                    key["last_used"] = time.time()
                    self._store_tenant(tenant)
                    return tenant_id
        
        return None
    
    def update_tenant(self, 
                     tenant_id: str, 
                     updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a tenant's configuration.
        
        Args:
            tenant_id: Identifier for the tenant
            updates: Updates to apply to the tenant
            
        Returns:
            Updated tenant data if successful, None otherwise
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None
        
        # Apply updates
        for key, value in updates.items():
            if key in ["name", "description", "status", "resource_quotas", "custom_config"]:
                if key == "resource_quotas" and isinstance(value, dict):
                    # Merge resource quotas
                    tenant[key] = {**tenant[key], **value}
                elif key == "custom_config" and isinstance(value, dict):
                    # Merge custom config
                    tenant[key] = {**tenant[key], **value}
                else:
                    tenant[key] = value
        
        tenant["last_updated"] = time.time()
        self._store_tenant(tenant)
        
        return tenant
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """
        Delete a tenant.
        
        Args:
            tenant_id: Identifier for the tenant
            
        Returns:
            True if successful, False otherwise
        """
        if tenant_id not in self.tenants:
            return False
        
        # Remove from memory
        del self.tenants[tenant_id]
        
        # Remove from storage
        file_path = os.path.join(self.config["tenant_storage_path"], f"{tenant_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting tenant: {e}")
            return False
    
    def generate_api_key(self, 
                        tenant_id: str, 
                        description: Optional[str] = None) -> Optional[str]:
        """
        Generate a new API key for a tenant.
        
        Args:
            tenant_id: Identifier for the tenant
            description: Optional description of the API key
            
        Returns:
            New API key if successful, None otherwise
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None
        
        # Generate a new API key
        api_key = self._generate_api_key(tenant_id)
        
        # Add to tenant
        tenant["api_keys"].append({
            "key_id": f"key-{uuid.uuid4()}",
            "key_hash": self._hash_api_key(api_key),
            "creation_time": time.time(),
            "last_used": None,
            "status": "active",
            "description": description or "API key"
        })
        
        self._store_tenant(tenant)
        
        return api_key
    
    def revoke_api_key(self, tenant_id: str, key_id: str) -> bool:
        """
        Revoke an API key for a tenant.
        
        Args:
            tenant_id: Identifier for the tenant
            key_id: Identifier for the API key
            
        Returns:
            True if successful, False otherwise
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        for key in tenant["api_keys"]:
            if key["key_id"] == key_id:
                key["status"] = "revoked"
                key["revocation_time"] = time.time()
                self._store_tenant(tenant)
                return True
        
        return False
    
    def update_resource_usage(self, 
                             tenant_id: str, 
                             resource_type: str, 
                             delta: int) -> bool:
        """
        Update resource usage for a tenant.
        
        Args:
            tenant_id: Identifier for the tenant
            resource_type: Type of resource to update
            delta: Change in resource usage
            
        Returns:
            True if successful, False otherwise
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        if resource_type not in tenant["resource_usage"]:
            return False
        
        # Check if the update would exceed quotas
        new_usage = tenant["resource_usage"][resource_type] + delta
        if new_usage < 0:
            new_usage = 0
        
        if resource_type in tenant["resource_quotas"] and new_usage > tenant["resource_quotas"][resource_type]:
            return False
        
        tenant["resource_usage"][resource_type] = new_usage
        self._store_tenant(tenant)
        
        return True
    
    def check_resource_availability(self, 
                                  tenant_id: str, 
                                  resource_type: str, 
                                  amount: int) -> bool:
        """
        Check if a tenant has sufficient resources available.
        
        Args:
            tenant_id: Identifier for the tenant
            resource_type: Type of resource to check
            amount: Amount of resource needed
            
        Returns:
            True if resources are available, False otherwise
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        if resource_type not in tenant["resource_usage"] or resource_type not in tenant["resource_quotas"]:
            return False
        
        current_usage = tenant["resource_usage"][resource_type]
        quota = tenant["resource_quotas"][resource_type]
        
        return current_usage + amount <= quota
    
    def list_tenants(self) -> List[Dict[str, Any]]:
        """
        List all tenants.
        
        Returns:
            List of tenant data
        """
        return list(self.tenants.values())


class TenantIsolationService:
    """
    Service for enforcing tenant isolation in workflow execution.
    
    This class provides methods for enforcing isolation between tenant
    resources, and for managing secure cross-tenant communication.
    """
    
    def __init__(self, tenant_manager: TenantManager):
        """
        Initialize the Tenant Isolation Service.
        
        Args:
            tenant_manager: Tenant Manager instance
        """
        self.tenant_manager = tenant_manager
        self.config = tenant_manager.config
        self.audit_log = []
    
    def validate_resource_access(self, 
                               tenant_id: str, 
                               resource_id: str, 
                               resource_type: str,
                               action: str) -> bool:
        """
        Validate if a tenant can access a resource.
        
        Args:
            tenant_id: Identifier for the tenant
            resource_id: Identifier for the resource
            resource_type: Type of resource
            action: Action being performed
            
        Returns:
            True if access is allowed, False otherwise
        """
        # Check if tenant exists and is active
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant or tenant["status"] != "active":
            self._log_audit_event(tenant_id, resource_id, resource_type, action, False, "Tenant not active")
            return False
        
        # Check if resource belongs to tenant
        resource_tenant = self._get_resource_tenant(resource_id, resource_type)
        
        if resource_tenant is None:
            # New resource being created
            self._log_audit_event(tenant_id, resource_id, resource_type, action, True, "New resource")
            return True
        
        if resource_tenant == tenant_id:
            # Resource belongs to tenant
            self._log_audit_event(tenant_id, resource_id, resource_type, action, True, "Resource belongs to tenant")
            return True
        
        # Resource belongs to another tenant
        if self.config["isolation_level"] == "strict":
            # Strict isolation: no cross-tenant access
            self._log_audit_event(tenant_id, resource_id, resource_type, action, False, "Strict isolation")
            return False
        
        if self.config["isolation_level"] == "permissive" and self.config["enable_cross_tenant_communication"]:
            # Permissive isolation: allow cross-tenant access if enabled
            self._log_audit_event(tenant_id, resource_id, resource_type, action, True, "Permissive isolation")
            return True
        
        if self.config["isolation_level"] == "custom":
            # Custom isolation: check tenant-specific rules
            allowed = self._check_custom_isolation_rules(tenant_id, resource_tenant, resource_type, action)
            self._log_audit_event(tenant_id, resource_id, resource_type, action, allowed, "Custom isolation")
            return allowed
        
        self._log_audit_event(tenant_id, resource_id, resource_type, action, False, "Default deny")
        return False
    
    def _get_resource_tenant(self, resource_id: str, resource_type: str) -> Optional[str]:
        """
        Get the tenant that owns a resource.
        
        Args:
            resource_id: Identifier for the resource
            resource_type: Type of resource
            
        Returns:
            Tenant ID if found, None otherwise
        """
        # In a production environment, this would query a database
        # For this implementation, we'll parse the resource ID
        
        # Check if resource ID has tenant prefix
        if resource_id.startswith("tenant-"):
            parts = resource_id.split("-", 2)
            if len(parts) >= 2:
                tenant_id = f"tenant-{parts[1]}"
                if tenant_id in self.tenant_manager.tenants:
                    return tenant_id
        
        # For workflow resources, check if they have tenant metadata
        if resource_type in ["workflow", "execution", "agent"]:
            # In a real implementation, this would query the resource metadata
            # For this implementation, we'll return None to indicate unknown ownership
            return None
        
        return None
    
    def _check_custom_isolation_rules(self, 
                                    tenant_id: str, 
                                    resource_tenant: str, 
                                    resource_type: str,
                                    action: str) -> bool:
        """
        Check custom isolation rules for cross-tenant access.
        
        Args:
            tenant_id: Identifier for the tenant
            resource_tenant: Identifier for the resource tenant
            resource_type: Type of resource
            action: Action being performed
            
        Returns:
            True if access is allowed, False otherwise
        """
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return False
        
        # Check if tenant has custom isolation rules
        custom_config = tenant.get("custom_config", {})
        isolation_rules = custom_config.get("isolation_rules", {})
        
        # Check for explicit allow rules
        allow_rules = isolation_rules.get("allow", [])
        for rule in allow_rules:
            if (rule.get("tenant") == resource_tenant or rule.get("tenant") == "*") and \
               (rule.get("resource_type") == resource_type or rule.get("resource_type") == "*") and \
               (rule.get("action") == action or rule.get("action") == "*"):
                return True
        
        # Check for explicit deny rules
        deny_rules = isolation_rules.get("deny", [])
        for rule in deny_rules:
            if (rule.get("tenant") == resource_tenant or rule.get("tenant") == "*") and \
               (rule.get("resource_type") == resource_type or rule.get("resource_type") == "*") and \
               (rule.get("action") == action or rule.get("action") == "*"):
                return False
        
        # Default to global setting
        return self.config["enable_cross_tenant_communication"]
    
    def _log_audit_event(self, 
                        tenant_id: str, 
                        resource_id: str, 
                        resource_type: str,
                        action: str,
                        allowed: bool,
                        reason: str):
        """
        Log an audit event for tenant isolation.
        
        Args:
            tenant_id: Identifier for the tenant
            resource_id: Identifier for the resource
            resource_type: Type of resource
            action: Action being performed
            allowed: Whether access was allowed
            reason: Reason for the decision
        """
        event = {
            "timestamp": time.time(),
            "tenant_id": tenant_id,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "action": action,
            "allowed": allowed,
            "reason": reason
        }
        
        self.audit_log.append(event)
        
        # In a production environment, this would write to a persistent audit log
        # For this implementation, we'll just keep it in memory
        
        # Trim audit log if it gets too large
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def get_audit_log(self, 
                     tenant_id: Optional[str] = None,
                     start_time: Optional[float] = None,
                     end_time: Optional[float] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get audit log events.
        
        Args:
            tenant_id: Optional tenant ID to filter by
            start_time: Optional start time for the log period
            end_time: Optional end time for the log period
            limit: Maximum number of events to return
            
        Returns:
            List of audit log events
        """
        filtered_log = self.audit_log
        
        if tenant_id:
            filtered_log = [event for event in filtered_log if event["tenant_id"] == tenant_id]
        
        if start_time:
            filtered_log = [event for event in filtered_log if event["timestamp"] >= start_time]
        
        if end_time:
            filtered_log = [event for event in filtered_log if event["timestamp"] <= end_time]
        
        # Sort by timestamp (newest first)
        filtered_log.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        return filtered_log[:limit]
    
    def create_cross_tenant_token(self, 
                                source_tenant_id: str, 
                                target_tenant_id: str,
                                resource_types: List[str],
                                actions: List[str],
                                expiration_time: float) -> Optional[Dict[str, Any]]:
        """
        Create a token for secure cross-tenant communication.
        
        Args:
            source_tenant_id: Identifier for the source tenant
            target_tenant_id: Identifier for the target tenant
            resource_types: Types of resources the token can access
            actions: Actions the token can perform
            expiration_time: Expiration time for the token
            
        Returns:
            Token data if successful, None otherwise
        """
        # Check if cross-tenant communication is enabled
        if not self.config["enable_cross_tenant_communication"]:
            return None
        
        # Check if both tenants exist and are active
        source_tenant = self.tenant_manager.get_tenant(source_tenant_id)
        target_tenant = self.tenant_manager.get_tenant(target_tenant_id)
        
        if not source_tenant or source_tenant["status"] != "active" or \
           not target_tenant or target_tenant["status"] != "active":
            return None
        
        # Generate token
        token_id = f"token-{uuid.uuid4()}"
        token_value = self._generate_token_value(source_tenant_id, target_tenant_id)
        
        token = {
            "token_id": token_id,
            "source_tenant_id": source_tenant_id,
            "target_tenant_id": target_tenant_id,
            "resource_types": resource_types,
            "actions": actions,
            "creation_time": time.time(),
            "expiration_time": expiration_time,
            "status": "active"
        }
        
        # Store token in source tenant's custom config
        source_tenant_config = source_tenant.get("custom_config", {})
        if "cross_tenant_tokens" not in source_tenant_config:
            source_tenant_config["cross_tenant_tokens"] = []
        
        source_tenant_config["cross_tenant_tokens"].append({
            **token,
            "token_hash": self._hash_token(token_value)
        })
        
        source_tenant["custom_config"] = source_tenant_config
        self.tenant_manager._store_tenant(source_tenant)
        
        # Store token reference in target tenant's custom config
        target_tenant_config = target_tenant.get("custom_config", {})
        if "incoming_tokens" not in target_tenant_config:
            target_tenant_config["incoming_tokens"] = []
        
        target_tenant_config["incoming_tokens"].append({
            "token_id": token_id,
            "source_tenant_id": source_tenant_id,
            "resource_types": resource_types,
            "actions": actions,
            "creation_time": time.time(),
            "expiration_time": expiration_time,
            "status": "active"
        })
        
        target_tenant["custom_config"] = target_tenant_config
        self.tenant_manager._store_tenant(target_tenant)
        
        # Return token with plaintext value
        return {
            **token,
            "token_value": token_value
        }
    
    def _generate_token_value(self, source_tenant_id: str, target_tenant_id: str) -> str:
        """
        Generate a token value for cross-tenant communication.
        
        Args:
            source_tenant_id: Identifier for the source tenant
            target_tenant_id: Identifier for the target tenant
            
        Returns:
            Token value
        """
        # Generate a random UUID and combine with tenant IDs
        random_uuid = str(uuid.uuid4())
        key_material = f"{source_tenant_id}:{target_tenant_id}:{random_uuid}:{time.time()}"
        
        # Hash the key material to create the token value
        hash_obj = hashlib.sha256(key_material.encode('utf-8'))
        token_value = hash_obj.hexdigest()
        
        return token_value
    
    def _hash_token(self, token_value: str) -> str:
        """
        Hash a token value for secure storage.
        
        Args:
            token_value: Token value to hash
            
        Returns:
            Hashed token value
        """
        # In a production environment, this would use a secure password hashing algorithm
        # For this implementation, we'll use a simple hash
        hash_obj = hashlib.sha256(token_value.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def validate_cross_tenant_token(self, 
                                  token_value: str, 
                                  source_tenant_id: str,
                                  target_tenant_id: str,
                                  resource_type: str,
                                  action: str) -> bool:
        """
        Validate a cross-tenant token.
        
        Args:
            token_value: Token value to validate
            source_tenant_id: Identifier for the source tenant
            target_tenant_id: Identifier for the target tenant
            resource_type: Type of resource being accessed
            action: Action being performed
            
        Returns:
            True if token is valid, False otherwise
        """
        # Check if cross-tenant communication is enabled
        if not self.config["enable_cross_tenant_communication"]:
            return False
        
        # Get source tenant
        source_tenant = self.tenant_manager.get_tenant(source_tenant_id)
        if not source_tenant or source_tenant["status"] != "active":
            return False
        
        # Hash the token value
        token_hash = self._hash_token(token_value)
        
        # Check if token exists in source tenant's custom config
        source_tenant_config = source_tenant.get("custom_config", {})
        cross_tenant_tokens = source_tenant_config.get("cross_tenant_tokens", [])
        
        for token in cross_tenant_tokens:
            if token["token_hash"] == token_hash and \
               token["target_tenant_id"] == target_tenant_id and \
               token["status"] == "active" and \
               token["expiration_time"] > time.time() and \
               (resource_type in token["resource_types"] or "*" in token["resource_types"]) and \
               (action in token["actions"] or "*" in token["actions"]):
                return True
        
        return False
    
    def revoke_cross_tenant_token(self, source_tenant_id: str, token_id: str) -> bool:
        """
        Revoke a cross-tenant token.
        
        Args:
            source_tenant_id: Identifier for the source tenant
            token_id: Identifier for the token
            
        Returns:
            True if successful, False otherwise
        """
        # Get source tenant
        source_tenant = self.tenant_manager.get_tenant(source_tenant_id)
        if not source_tenant:
            return False
        
        # Check if token exists in source tenant's custom config
        source_tenant_config = source_tenant.get("custom_config", {})
        cross_tenant_tokens = source_tenant_config.get("cross_tenant_tokens", [])
        
        for token in cross_tenant_tokens:
            if token["token_id"] == token_id:
                token["status"] = "revoked"
                token["revocation_time"] = time.time()
                
                # Update source tenant
                self.tenant_manager._store_tenant(source_tenant)
                
                # Update target tenant
                target_tenant_id = token["target_tenant_id"]
                target_tenant = self.tenant_manager.get_tenant(target_tenant_id)
                
                if target_tenant:
                    target_tenant_config = target_tenant.get("custom_config", {})
                    incoming_tokens = target_tenant_config.get("incoming_tokens", [])
                    
                    for incoming_token in incoming_tokens:
                        if incoming_token["token_id"] == token_id:
                            incoming_token["status"] = "revoked"
                            incoming_token["revocation_time"] = time.time()
                            
                            # Update target tenant
                            self.tenant_manager._store_tenant(target_tenant)
                            break
                
                return True
        
        return False


# Example usage
if __name__ == "__main__":
    # Initialize the tenant manager
    tenant_manager = TenantManager()
    
    # Create a tenant
    tenant_data = tenant_manager.create_tenant(
        name="Example Corp",
        description="Example Corporation Tenant",
        resource_quotas={
            "max_workflows": 200,
            "max_concurrent_executions": 50
        }
    )
    
    print(f"Created tenant: {tenant_data['tenant_id']}")
    print(f"API key: {tenant_data['api_key']}")
    
    # Initialize the tenant isolation service
    isolation_service = TenantIsolationService(tenant_manager)
    
    # Validate resource access
    tenant_id = tenant_data["tenant_id"]
    resource_id = f"{tenant_id}-workflow-123"
    
    access_allowed = isolation_service.validate_resource_access(
        tenant_id, resource_id, "workflow", "read"
    )
    
    print(f"Access allowed: {access_allowed}")
    
    # Create another tenant
    tenant_data2 = tenant_manager.create_tenant(
        name="Partner Inc",
        description="Partner Tenant"
    )
    
    # Create a cross-tenant token
    token = isolation_service.create_cross_tenant_token(
        source_tenant_id=tenant_id,
        target_tenant_id=tenant_data2["tenant_id"],
        resource_types=["workflow", "execution"],
        actions=["read"],
        expiration_time=time.time() + 3600  # 1 hour
    )
    
    if token:
        print(f"Created cross-tenant token: {token['token_id']}")
        
        # Validate the token
        is_valid = isolation_service.validate_cross_tenant_token(
            token_value=token["token_value"],
            source_tenant_id=tenant_id,
            target_tenant_id=tenant_data2["tenant_id"],
            resource_type="workflow",
            action="read"
        )
        
        print(f"Token valid: {is_valid}")
        
        # Revoke the token
        revoked = isolation_service.revoke_cross_tenant_token(
            source_tenant_id=tenant_id,
            token_id=token["token_id"]
        )
        
        print(f"Token revoked: {revoked}")
    
    # Get audit log
    audit_log = isolation_service.get_audit_log(tenant_id=tenant_id)
    print(f"Audit log entries: {len(audit_log)}")
"""
