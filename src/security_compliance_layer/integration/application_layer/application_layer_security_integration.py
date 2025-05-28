"""
Application Layer Security Integration Module for the Security & Compliance Layer

This module implements security integration with the Application Layer, providing
application security controls, API security, authentication enforcement, and
secure application lifecycle management.

Key features:
1. Application security controls
2. API security and gateway protection
3. Authentication and authorization enforcement
4. Secure application lifecycle management
5. MCP and A2A protocol security integration

Dependencies:
- core.identity_trust.identity_provider
- core.access_control.access_control_system
- core.protocol_security.protocol_security_gateway
- core.policy_governance.regulatory_twin_engine

Author: Industriverse Security Team
"""

import logging
import uuid
import time
import json
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class ApplicationSecurityLevel(Enum):
    """Enumeration of application security levels"""
    STANDARD = "standard"  # Standard security level
    ENHANCED = "enhanced"  # Enhanced security level
    HIGH = "high"  # High security level
    CRITICAL = "critical"  # Critical security level

class ApplicationLayerSecurityIntegration:
    """
    Application Layer Security Integration for the Security & Compliance Layer
    
    This class implements security integration with the Application Layer, providing
    application security controls, API security, authentication enforcement, and
    secure application lifecycle management.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Application Layer Security Integration
        
        Args:
            config: Configuration dictionary for the Application Layer Security Integration
        """
        self.config = config or {}
        self.app_security_registry = {}  # Maps app_id to security details
        self.api_security_registry = {}  # Maps api_id to security details
        self.app_access_registry = {}  # Maps access_id to access details
        self.app_audit_registry = {}  # Maps audit_id to audit details
        
        # Default configuration
        self.default_config = {
            "default_security_level": ApplicationSecurityLevel.ENHANCED.value,
            "enable_api_security": True,
            "enable_jwt_validation": True,
            "enable_rate_limiting": True,
            "enable_input_validation": True,
            "enable_output_sanitization": True,
            "enable_secure_headers": True,
            "enable_csrf_protection": True,
            "enable_xss_protection": True,
            "enable_content_security_policy": True,
            "audit_log_retention_days": 365,
            "mcp_protocol_enabled": True,
            "a2a_protocol_enabled": True
        }
        
        # Merge default config with provided config
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Dependencies (will be set via dependency injection)
        self.identity_provider = None
        self.access_control_system = None
        self.protocol_security_gateway = None
        self.regulatory_twin_engine = None
        
        logger.info("Application Layer Security Integration initialized")
    
    def set_dependencies(self, identity_provider=None, access_control_system=None,
                        protocol_security_gateway=None, regulatory_twin_engine=None):
        """
        Set dependencies for the Application Layer Security Integration
        
        Args:
            identity_provider: Identity Provider instance
            access_control_system: Access Control System instance
            protocol_security_gateway: Protocol Security Gateway instance
            regulatory_twin_engine: Regulatory Twin Engine instance
        """
        self.identity_provider = identity_provider
        self.access_control_system = access_control_system
        self.protocol_security_gateway = protocol_security_gateway
        self.regulatory_twin_engine = regulatory_twin_engine
        logger.info("Application Layer Security Integration dependencies set")
    
    def register_application(self, app_id: str, app_name: str, app_owner: str,
                           security_level: Union[ApplicationSecurityLevel, str] = None,
                           authentication_required: bool = True,
                           authorization_required: bool = True,
                           api_endpoints: List[Dict[str, Any]] = None,
                           compliance_requirements: List[str] = None,
                           metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register security details for an application
        
        Args:
            app_id: ID of the application
            app_name: Name of the application
            app_owner: Owner of the application
            security_level: Security level for the application
            authentication_required: Whether authentication is required
            authorization_required: Whether authorization is required
            api_endpoints: List of API endpoints for the application
            compliance_requirements: Compliance requirements for the application
            metadata: Metadata for the application
            
        Returns:
            Application security details
        """
        # Convert enum to value
        if isinstance(security_level, ApplicationSecurityLevel):
            security_level = security_level.value
        
        # Set default values if not provided
        if security_level is None:
            security_level = self.config.get("default_security_level")
        
        # Create application security record
        security_id = str(uuid.uuid4())
        
        security_record = {
            "security_id": security_id,
            "app_id": app_id,
            "app_name": app_name,
            "app_owner": app_owner,
            "security_level": security_level,
            "authentication_required": authentication_required,
            "authorization_required": authorization_required,
            "api_endpoints": api_endpoints or [],
            "compliance_requirements": compliance_requirements or [],
            "metadata": metadata or {},
            "registration_date": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "status": "active",
            "security_controls": self._get_security_controls_for_level(security_level)
        }
        
        self.app_security_registry[app_id] = security_record
        
        # Register API endpoints if provided
        if api_endpoints:
            for endpoint in api_endpoints:
                self.register_api_endpoint(
                    app_id=app_id,
                    endpoint_path=endpoint.get("path"),
                    http_methods=endpoint.get("methods", ["GET"]),
                    requires_auth=endpoint.get("requires_auth", authentication_required),
                    requires_authorization=endpoint.get("requires_authorization", authorization_required),
                    rate_limit=endpoint.get("rate_limit"),
                    input_validation_schema=endpoint.get("input_validation_schema"),
                    output_sanitization_rules=endpoint.get("output_sanitization_rules")
                )
        
        # Register with Identity Provider if available
        if self.identity_provider and authentication_required:
            logger.info(f"Registered application {app_id} with Identity Provider for authentication")
        
        # Register with Access Control System if available
        if self.access_control_system and authorization_required:
            logger.info(f"Registered application {app_id} with Access Control System for authorization")
        
        # Register with Protocol Security Gateway if available
        if self.protocol_security_gateway:
            logger.info(f"Registered application {app_id} with Protocol Security Gateway")
        
        # Register with Regulatory Twin Engine if available
        if self.regulatory_twin_engine and compliance_requirements:
            logger.info(f"Registered application {app_id} with Regulatory Twin Engine for compliance monitoring")
        
        logger.info(f"Registered security for application {app_id} with security level {security_level}")
        return security_record
    
    def _get_security_controls_for_level(self, security_level: str) -> Dict[str, Any]:
        """
        Get security controls for a security level
        
        Args:
            security_level: Security level
            
        Returns:
            Security controls for the level
        """
        # Base controls for all levels
        base_controls = {
            "input_validation": True,
            "output_sanitization": True,
            "secure_headers": True,
            "csrf_protection": True,
            "xss_protection": True,
            "sql_injection_protection": True,
            "content_security_policy": True,
            "secure_cookies": True,
            "tls_required": True
        }
        
        # Enhanced controls
        if security_level == ApplicationSecurityLevel.ENHANCED.value:
            base_controls.update({
                "rate_limiting": True,
                "brute_force_protection": True,
                "session_timeout": 30,  # minutes
                "password_complexity": "medium"
            })
        
        # High controls
        elif security_level == ApplicationSecurityLevel.HIGH.value:
            base_controls.update({
                "rate_limiting": True,
                "brute_force_protection": True,
                "session_timeout": 15,  # minutes
                "password_complexity": "high",
                "mfa_required": True,
                "ip_restriction": True,
                "audit_logging": "detailed"
            })
        
        # Critical controls
        elif security_level == ApplicationSecurityLevel.CRITICAL.value:
            base_controls.update({
                "rate_limiting": True,
                "brute_force_protection": True,
                "session_timeout": 5,  # minutes
                "password_complexity": "very_high",
                "mfa_required": True,
                "ip_restriction": True,
                "audit_logging": "comprehensive",
                "context_aware_authentication": True,
                "just_in_time_access": True,
                "continuous_authorization": True,
                "anomaly_detection": True
            })
        
        return base_controls
    
    def register_api_endpoint(self, app_id: str, endpoint_path: str, http_methods: List[str] = None,
                            requires_auth: bool = True, requires_authorization: bool = True,
                            rate_limit: Dict[str, Any] = None, input_validation_schema: Dict[str, Any] = None,
                            output_sanitization_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register security details for an API endpoint
        
        Args:
            app_id: ID of the application
            endpoint_path: Path of the endpoint
            http_methods: HTTP methods supported by the endpoint
            requires_auth: Whether authentication is required
            requires_authorization: Whether authorization is required
            rate_limit: Rate limiting configuration
            input_validation_schema: Input validation schema
            output_sanitization_rules: Output sanitization rules
            
        Returns:
            API endpoint security details
        """
        if app_id not in self.app_security_registry:
            raise ValueError(f"Application not registered: {app_id}")
        
        # Set default values
        http_methods = http_methods or ["GET"]
        
        # Create API endpoint security record
        api_id = f"{app_id}:{endpoint_path}"
        
        # Default rate limit based on security level
        app_security_level = self.app_security_registry[app_id]["security_level"]
        default_rate_limit = self._get_default_rate_limit(app_security_level)
        
        api_security_record = {
            "api_id": api_id,
            "app_id": app_id,
            "endpoint_path": endpoint_path,
            "http_methods": http_methods,
            "requires_auth": requires_auth,
            "requires_authorization": requires_authorization,
            "rate_limit": rate_limit or default_rate_limit,
            "input_validation_schema": input_validation_schema or {},
            "output_sanitization_rules": output_sanitization_rules or {},
            "registration_date": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        self.api_security_registry[api_id] = api_security_record
        
        # Register with Protocol Security Gateway if available
        if self.protocol_security_gateway:
            logger.info(f"Registered API endpoint {api_id} with Protocol Security Gateway")
        
        logger.info(f"Registered security for API endpoint {api_id}")
        return api_security_record
    
    def _get_default_rate_limit(self, security_level: str) -> Dict[str, Any]:
        """
        Get default rate limit for a security level
        
        Args:
            security_level: Security level
            
        Returns:
            Default rate limit configuration
        """
        if security_level == ApplicationSecurityLevel.STANDARD.value:
            return {
                "requests_per_minute": 60,
                "burst": 10
            }
        elif security_level == ApplicationSecurityLevel.ENHANCED.value:
            return {
                "requests_per_minute": 30,
                "burst": 5
            }
        elif security_level == ApplicationSecurityLevel.HIGH.value:
            return {
                "requests_per_minute": 15,
                "burst": 3
            }
        elif security_level == ApplicationSecurityLevel.CRITICAL.value:
            return {
                "requests_per_minute": 5,
                "burst": 2
            }
        else:
            return {
                "requests_per_minute": 30,
                "burst": 5
            }
    
    def get_application_security(self, app_id: str) -> Dict[str, Any]:
        """
        Get security details for an application
        
        Args:
            app_id: ID of the application
            
        Returns:
            Application security details
        """
        if app_id not in self.app_security_registry:
            raise ValueError(f"Application security not found: {app_id}")
        
        return self.app_security_registry[app_id]
    
    def get_api_security(self, app_id: str, endpoint_path: str) -> Dict[str, Any]:
        """
        Get security details for an API endpoint
        
        Args:
            app_id: ID of the application
            endpoint_path: Path of the endpoint
            
        Returns:
            API endpoint security details
        """
        api_id = f"{app_id}:{endpoint_path}"
        
        if api_id not in self.api_security_registry:
            raise ValueError(f"API security not found: {api_id}")
        
        return self.api_security_registry[api_id]
    
    def update_application_security(self, app_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update security details for an application
        
        Args:
            app_id: ID of the application
            **kwargs: Fields to update
            
        Returns:
            Updated application security details
        """
        if app_id not in self.app_security_registry:
            raise ValueError(f"Application security not found: {app_id}")
        
        security_record = self.app_security_registry[app_id]
        
        # Convert enum to value
        if "security_level" in kwargs and isinstance(kwargs["security_level"], ApplicationSecurityLevel):
            kwargs["security_level"] = kwargs["security_level"].value
        
        # Update fields
        for key, value in kwargs.items():
            if key in security_record:
                security_record[key] = value
        
        # Update security controls if security level changed
        if "security_level" in kwargs:
            security_record["security_controls"] = self._get_security_controls_for_level(kwargs["security_level"])
        
        # Update last updated timestamp
        security_record["last_updated"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated security for application {app_id}")
        return security_record
    
    def update_api_security(self, app_id: str, endpoint_path: str, **kwargs) -> Dict[str, Any]:
        """
        Update security details for an API endpoint
        
        Args:
            app_id: ID of the application
            endpoint_path: Path of the endpoint
            **kwargs: Fields to update
            
        Returns:
            Updated API endpoint security details
        """
        api_id = f"{app_id}:{endpoint_path}"
        
        if api_id not in self.api_security_registry:
            raise ValueError(f"API security not found: {api_id}")
        
        security_record = self.api_security_registry[api_id]
        
        # Update fields
        for key, value in kwargs.items():
            if key in security_record:
                security_record[key] = value
        
        # Update last updated timestamp
        security_record["last_updated"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated security for API endpoint {api_id}")
        return security_record
    
    def check_application_access(self, app_id: str, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if a user has access to an application
        
        Args:
            app_id: ID of the application
            user_id: ID of the user
            context: Context for the access check
            
        Returns:
            Access check result
        """
        if app_id not in self.app_security_registry:
            raise ValueError(f"Application security not found: {app_id}")
        
        security_record = self.app_security_registry[app_id]
        
        # Use Access Control System if available
        if self.access_control_system:
            # In a real implementation, this would check access with the Access Control System
            # For this implementation, we'll simulate an access check
            access_result = self._simulate_app_access_check(security_record, user_id, context)
        else:
            # Simplified access check
            access_result = self._simplified_app_access_check(security_record, user_id, context)
        
        # Create access log
        access_id = str(uuid.uuid4())
        
        access_log = {
            "access_id": access_id,
            "app_id": app_id,
            "user_id": user_id,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
            "result": access_result["allowed"],
            "reason": access_result["reason"]
        }
        
        self.app_access_registry[access_id] = access_log
        
        logger.info(f"Checked access for application {app_id} by user {user_id}: {access_result['allowed']}")
        return access_result
    
    def _simulate_app_access_check(self, security_record: Dict[str, Any], user_id: str,
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Simulate an application access check with the Access Control System
        
        Args:
            security_record: Application security record
            user_id: ID of the user
            context: Context for the access check
            
        Returns:
            Access check result
        """
        # In a real implementation, this would call the Access Control System
        # For this implementation, we'll simulate an access check
        
        # Check if authentication is required
        if security_record["authentication_required"]:
            # Check if user is authenticated
            if not context or not context.get("authenticated", False):
                return {
                    "allowed": False,
                    "reason": "Authentication required"
                }
        
        # Check if authorization is required
        if security_record["authorization_required"]:
            # Check if user has required roles
            user_roles = context.get("user_roles", []) if context else []
            required_roles = security_record.get("metadata", {}).get("required_roles", [])
            
            if required_roles and not any(role in user_roles for role in required_roles):
                return {
                    "allowed": False,
                    "reason": "Authorization required"
                }
        
        # Check security level specific requirements
        security_level = security_record["security_level"]
        
        if security_level == ApplicationSecurityLevel.HIGH.value:
            # Check if MFA is completed
            if not context or not context.get("mfa_completed", False):
                return {
                    "allowed": False,
                    "reason": "MFA required for high security application"
                }
        
        elif security_level == ApplicationSecurityLevel.CRITICAL.value:
            # Check if MFA is completed
            if not context or not context.get("mfa_completed", False):
                return {
                    "allowed": False,
                    "reason": "MFA required for critical security application"
                }
            
            # Check if access is from allowed IP
            if not context or not self._check_ip_restriction(context.get("ip_address"), security_record):
                return {
                    "allowed": False,
                    "reason": "IP restriction enforced for critical security application"
                }
            
            # Check if just-in-time access is approved
            if not context or not context.get("jit_access_approved", False):
                return {
                    "allowed": False,
                    "reason": "Just-in-time access required for critical security application"
                }
        
        # All checks passed
        return {
            "allowed": True,
            "reason": "Access granted"
        }
    
    def _simplified_app_access_check(self, security_record: Dict[str, Any], user_id: str,
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform a simplified application access check
        
        Args:
            security_record: Application security record
            user_id: ID of the user
            context: Context for the access check
            
        Returns:
            Access check result
        """
        # Check if user is the application owner
        if user_id == security_record["app_owner"]:
            return {
                "allowed": True,
                "reason": "User is the application owner"
            }
        
        # Check if authentication is required
        if security_record["authentication_required"]:
            # Check if user is authenticated
            if not context or not context.get("authenticated", False):
                return {
                    "allowed": False,
                    "reason": "Authentication required"
                }
        
        # All checks passed
        return {
            "allowed": True,
            "reason": "Access granted"
        }
    
    def _check_ip_restriction(self, ip_address: str, security_record: Dict[str, Any]) -> bool:
        """
        Check if an IP address is allowed
        
        Args:
            ip_address: IP address to check
            security_record: Security record with IP restrictions
            
        Returns:
            Whether the IP address is allowed
        """
        if not ip_address:
            return False
        
        # Get allowed IPs from metadata
        allowed_ips = security_record.get("metadata", {}).get("allowed_ips", [])
        
        # If no restrictions are defined, allow all
        if not allowed_ips:
            return True
        
        # Check if IP is in allowed list
        return ip_address in allowed_ips
    
    def check_api_access(self, app_id: str, endpoint_path: str, user_id: str, http_method: str,
                       context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if a user has access to an API endpoint
        
        Args:
            app_id: ID of the application
            endpoint_path: Path of the endpoint
            user_id: ID of the user
            http_method: HTTP method being used
            context: Context for the access check
            
        Returns:
            Access check result
        """
        api_id = f"{app_id}:{endpoint_path}"
        
        if api_id not in self.api_security_registry:
            raise ValueError(f"API security not found: {api_id}")
        
        api_security_record = self.api_security_registry[api_id]
        
        # Check if HTTP method is supported
        if http_method not in api_security_record["http_methods"]:
            return {
                "allowed": False,
                "reason": f"HTTP method {http_method} not supported"
            }
        
        # Check application access first
        app_access_result = self.check_application_access(app_id, user_id, context)
        
        if not app_access_result["allowed"]:
            return app_access_result
        
        # Check API-specific access
        if api_security_record["requires_auth"]:
            # Check if user is authenticated
            if not context or not context.get("authenticated", False):
                return {
                    "allowed": False,
                    "reason": "Authentication required for API access"
                }
        
        if api_security_record["requires_authorization"]:
            # Check if user has required roles for this API
            user_roles = context.get("user_roles", []) if context else []
            required_roles = api_security_record.get("required_roles", [])
            
            if required_roles and not any(role in user_roles for role in required_roles):
                return {
                    "allowed": False,
                    "reason": "Authorization required for API access"
                }
        
        # Check rate limiting
        if self.config.get("enable_rate_limiting") and api_security_record.get("rate_limit"):
            # In a real implementation, this would check rate limits
            # For this implementation, we'll assume rate limits are not exceeded
            pass
        
        # All checks passed
        return {
            "allowed": True,
            "reason": "API access granted"
        }
    
    def validate_input(self, app_id: str, endpoint_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against schema
        
        Args:
            app_id: ID of the application
            endpoint_path: Path of the endpoint
            input_data: Input data to validate
            
        Returns:
            Validation result
        """
        api_id = f"{app_id}:{endpoint_path}"
        
        if api_id not in self.api_security_registry:
            raise ValueError(f"API security not found: {api_id}")
        
        api_security_record = self.api_security_registry[api_id]
        
        # Get validation schema
        schema = api_security_record.get("input_validation_schema")
        
        if not schema:
            # No schema defined, validation passes
            return {
                "valid": True,
                "errors": []
            }
        
        # In a real implementation, this would validate against the schema
        # For this implementation, we'll simulate validation
        validation_result = self._simulate_schema_validation(input_data, schema)
        
        return validation_result
    
    def _simulate_schema_validation(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate schema validation
        
        Args:
            data: Data to validate
            schema: Validation schema
            
        Returns:
            Validation result
        """
        # In a real implementation, this would use a schema validation library
        # For this implementation, we'll do a simple check
        
        errors = []
        
        # Check required fields
        required_fields = schema.get("required", [])
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Required field missing: {field}")
        
        # Check field types
        properties = schema.get("properties", {})
        
        for field, field_schema in properties.items():
            if field in data:
                field_type = field_schema.get("type")
                
                if field_type == "string" and not isinstance(data[field], str):
                    errors.append(f"Field {field} should be a string")
                elif field_type == "number" and not isinstance(data[field], (int, float)):
                    errors.append(f"Field {field} should be a number")
                elif field_type == "integer" and not isinstance(data[field], int):
                    errors.append(f"Field {field} should be an integer")
                elif field_type == "boolean" and not isinstance(data[field], bool):
                    errors.append(f"Field {field} should be a boolean")
                elif field_type == "array" and not isinstance(data[field], list):
                    errors.append(f"Field {field} should be an array")
                elif field_type == "object" and not isinstance(data[field], dict):
                    errors.append(f"Field {field} should be an object")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def sanitize_output(self, app_id: str, endpoint_path: str, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize output data
        
        Args:
            app_id: ID of the application
            endpoint_path: Path of the endpoint
            output_data: Output data to sanitize
            
        Returns:
            Sanitized output data
        """
        api_id = f"{app_id}:{endpoint_path}"
        
        if api_id not in self.api_security_registry:
            raise ValueError(f"API security not found: {api_id}")
        
        api_security_record = self.api_security_registry[api_id]
        
        # Get sanitization rules
        rules = api_security_record.get("output_sanitization_rules")
        
        if not rules:
            # No rules defined, return data as is
            return output_data
        
        # In a real implementation, this would apply sanitization rules
        # For this implementation, we'll simulate sanitization
        sanitized_data = self._simulate_output_sanitization(output_data, rules)
        
        return sanitized_data
    
    def _simulate_output_sanitization(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate output sanitization
        
        Args:
            data: Data to sanitize
            rules: Sanitization rules
            
        Returns:
            Sanitized data
        """
        # In a real implementation, this would apply complex sanitization rules
        # For this implementation, we'll do a simple sanitization
        
        sanitized_data = data.copy()
        
        # Apply field exclusions
        exclude_fields = rules.get("exclude_fields", [])
        
        for field in exclude_fields:
            if field in sanitized_data:
                del sanitized_data[field]
        
        # Apply field masks
        mask_fields = rules.get("mask_fields", {})
        
        for field, mask_type in mask_fields.items():
            if field in sanitized_data:
                if mask_type == "full":
                    sanitized_data[field] = "********"
                elif mask_type == "partial" and isinstance(sanitized_data[field], str):
                    value = sanitized_data[field]
                    if len(value) > 4:
                        sanitized_data[field] = value[:2] + "****" + value[-2:]
                    else:
                        sanitized_data[field] = "****"
        
        return sanitized_data
    
    def audit_application_access(self, app_id: str, user_id: str, action: str,
                               result: bool, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Audit application access
        
        Args:
            app_id: ID of the application
            user_id: ID of the user
            action: Action being performed
            result: Result of the action (success/failure)
            context: Context for the audit
            
        Returns:
            Audit record
        """
        audit_id = str(uuid.uuid4())
        
        audit_record = {
            "audit_id": audit_id,
            "app_id": app_id,
            "user_id": user_id,
            "action": action,
            "result": result,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.app_audit_registry[audit_id] = audit_record
        
        logger.info(f"Audited application access: {app_id}, {user_id}, {action}, {result}")
        return audit_record
    
    def get_application_audit_logs(self, app_id: str, start_time: str = None,
                                end_time: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get audit logs for an application
        
        Args:
            app_id: ID of the application
            start_time: Start time for the logs (ISO format)
            end_time: End time for the logs (ISO format)
            limit: Maximum number of logs to return
            
        Returns:
            List of audit logs
        """
        # Convert times to datetime objects if provided
        start_datetime = None
        end_datetime = None
        
        if start_time:
            start_datetime = datetime.fromisoformat(start_time)
        
        if end_time:
            end_datetime = datetime.fromisoformat(end_time)
        
        # Filter logs
        filtered_logs = []
        
        for audit_id, audit_record in self.app_audit_registry.items():
            if audit_record["app_id"] != app_id:
                continue
            
            audit_datetime = datetime.fromisoformat(audit_record["timestamp"])
            
            if start_datetime and audit_datetime < start_datetime:
                continue
            
            if end_datetime and audit_datetime > end_datetime:
                continue
            
            filtered_logs.append(audit_record)
            
            if len(filtered_logs) >= limit:
                break
        
        return filtered_logs
    
    def secure_mcp_message(self, message: Dict[str, Any], sender_id: str,
                         recipient_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Secure an MCP (Model Context Protocol) message
        
        Args:
            message: Message to secure
            sender_id: ID of the sender
            recipient_id: ID of the recipient
            context: Context for the message
            
        Returns:
            Secured message
        """
        if not self.config.get("mcp_protocol_enabled"):
            return message
        
        # Use Protocol Security Gateway if available
        if self.protocol_security_gateway:
            # In a real implementation, this would use the Protocol Security Gateway
            # For this implementation, we'll simulate securing the message
            secured_message = self._simulate_secure_mcp_message(message, sender_id, recipient_id, context)
        else:
            # Simplified security
            secured_message = self._simplified_secure_mcp_message(message, sender_id, recipient_id, context)
        
        logger.info(f"Secured MCP message from {sender_id} to {recipient_id}")
        return secured_message
    
    def _simulate_secure_mcp_message(self, message: Dict[str, Any], sender_id: str,
                                  recipient_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Simulate securing an MCP message with the Protocol Security Gateway
        
        Args:
            message: Message to secure
            sender_id: ID of the sender
            recipient_id: ID of the recipient
            context: Context for the message
            
        Returns:
            Secured message
        """
        # In a real implementation, this would use the Protocol Security Gateway
        # For this implementation, we'll add security metadata
        
        secured_message = message.copy()
        
        # Add security metadata
        secured_message["security"] = {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "timestamp": datetime.utcnow().isoformat(),
            "signature": f"simulated_signature_{uuid.uuid4()}",
            "encryption": "aes-256-gcm",
            "integrity": "hmac-sha256"
        }
        
        return secured_message
    
    def _simplified_secure_mcp_message(self, message: Dict[str, Any], sender_id: str,
                                    recipient_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform simplified securing of an MCP message
        
        Args:
            message: Message to secure
            sender_id: ID of the sender
            recipient_id: ID of the recipient
            context: Context for the message
            
        Returns:
            Secured message
        """
        secured_message = message.copy()
        
        # Add basic security metadata
        secured_message["security"] = {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return secured_message
    
    def secure_a2a_message(self, message: Dict[str, Any], sender_id: str,
                         recipient_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Secure an A2A (Agent to Agent) message
        
        Args:
            message: Message to secure
            sender_id: ID of the sender
            recipient_id: ID of the recipient
            context: Context for the message
            
        Returns:
            Secured message
        """
        if not self.config.get("a2a_protocol_enabled"):
            return message
        
        # Use Protocol Security Gateway if available
        if self.protocol_security_gateway:
            # In a real implementation, this would use the Protocol Security Gateway
            # For this implementation, we'll simulate securing the message
            secured_message = self._simulate_secure_a2a_message(message, sender_id, recipient_id, context)
        else:
            # Simplified security
            secured_message = self._simplified_secure_a2a_message(message, sender_id, recipient_id, context)
        
        logger.info(f"Secured A2A message from {sender_id} to {recipient_id}")
        return secured_message
    
    def _simulate_secure_a2a_message(self, message: Dict[str, Any], sender_id: str,
                                  recipient_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Simulate securing an A2A message with the Protocol Security Gateway
        
        Args:
            message: Message to secure
            sender_id: ID of the sender
            recipient_id: ID of the recipient
            context: Context for the message
            
        Returns:
            Secured message
        """
        # In a real implementation, this would use the Protocol Security Gateway
        # For this implementation, we'll add security metadata
        
        secured_message = message.copy()
        
        # Add security metadata to A2A message
        if "agentMessage" in secured_message:
            secured_message["agentMessage"]["security"] = {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "timestamp": datetime.utcnow().isoformat(),
                "signature": f"simulated_signature_{uuid.uuid4()}",
                "encryption": "aes-256-gcm",
                "integrity": "hmac-sha256"
            }
        else:
            # Add security metadata to top level if agentMessage not present
            secured_message["security"] = {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "timestamp": datetime.utcnow().isoformat(),
                "signature": f"simulated_signature_{uuid.uuid4()}",
                "encryption": "aes-256-gcm",
                "integrity": "hmac-sha256"
            }
        
        return secured_message
    
    def _simplified_secure_a2a_message(self, message: Dict[str, Any], sender_id: str,
                                    recipient_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform simplified securing of an A2A message
        
        Args:
            message: Message to secure
            sender_id: ID of the sender
            recipient_id: ID of the recipient
            context: Context for the message
            
        Returns:
            Secured message
        """
        secured_message = message.copy()
        
        # Add basic security metadata to A2A message
        if "agentMessage" in secured_message:
            secured_message["agentMessage"]["security"] = {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            # Add security metadata to top level if agentMessage not present
            secured_message["security"] = {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return secured_message
    
    def verify_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify an MCP message
        
        Args:
            message: Message to verify
            
        Returns:
            Verification result
        """
        if not self.config.get("mcp_protocol_enabled"):
            return {"verified": True, "reason": "MCP protocol not enabled"}
        
        # Use Protocol Security Gateway if available
        if self.protocol_security_gateway:
            # In a real implementation, this would use the Protocol Security Gateway
            # For this implementation, we'll simulate verification
            verification_result = self._simulate_verify_mcp_message(message)
        else:
            # Simplified verification
            verification_result = self._simplified_verify_mcp_message(message)
        
        logger.info(f"Verified MCP message: {verification_result['verified']}")
        return verification_result
    
    def _simulate_verify_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate verifying an MCP message with the Protocol Security Gateway
        
        Args:
            message: Message to verify
            
        Returns:
            Verification result
        """
        # In a real implementation, this would use the Protocol Security Gateway
        # For this implementation, we'll do a simple check
        
        # Check if security metadata exists
        if "security" not in message:
            return {
                "verified": False,
                "reason": "No security metadata found"
            }
        
        security = message["security"]
        
        # Check required fields
        required_fields = ["sender_id", "recipient_id", "timestamp", "signature"]
        
        for field in required_fields:
            if field not in security:
                return {
                    "verified": False,
                    "reason": f"Missing required security field: {field}"
                }
        
        # Check timestamp
        try:
            timestamp = datetime.fromisoformat(security["timestamp"])
            now = datetime.utcnow()
            
            # Check if timestamp is within acceptable range (5 minutes)
            if abs((now - timestamp).total_seconds()) > 300:
                return {
                    "verified": False,
                    "reason": "Timestamp outside acceptable range"
                }
        except Exception as e:
            return {
                "verified": False,
                "reason": f"Invalid timestamp format: {e}"
            }
        
        # In a real implementation, this would verify the signature
        # For this implementation, we'll assume the signature is valid
        
        return {
            "verified": True,
            "reason": "Message verified"
        }
    
    def _simplified_verify_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform simplified verification of an MCP message
        
        Args:
            message: Message to verify
            
        Returns:
            Verification result
        """
        # Check if security metadata exists
        if "security" not in message:
            return {
                "verified": False,
                "reason": "No security metadata found"
            }
        
        security = message["security"]
        
        # Check required fields
        required_fields = ["sender_id", "recipient_id", "timestamp"]
        
        for field in required_fields:
            if field not in security:
                return {
                    "verified": False,
                    "reason": f"Missing required security field: {field}"
                }
        
        return {
            "verified": True,
            "reason": "Message verified"
        }
    
    def verify_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify an A2A message
        
        Args:
            message: Message to verify
            
        Returns:
            Verification result
        """
        if not self.config.get("a2a_protocol_enabled"):
            return {"verified": True, "reason": "A2A protocol not enabled"}
        
        # Use Protocol Security Gateway if available
        if self.protocol_security_gateway:
            # In a real implementation, this would use the Protocol Security Gateway
            # For this implementation, we'll simulate verification
            verification_result = self._simulate_verify_a2a_message(message)
        else:
            # Simplified verification
            verification_result = self._simplified_verify_a2a_message(message)
        
        logger.info(f"Verified A2A message: {verification_result['verified']}")
        return verification_result
    
    def _simulate_verify_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate verifying an A2A message with the Protocol Security Gateway
        
        Args:
            message: Message to verify
            
        Returns:
            Verification result
        """
        # In a real implementation, this would use the Protocol Security Gateway
        # For this implementation, we'll do a simple check
        
        # Check if security metadata exists
        security = None
        
        if "agentMessage" in message and "security" in message["agentMessage"]:
            security = message["agentMessage"]["security"]
        elif "security" in message:
            security = message["security"]
        
        if not security:
            return {
                "verified": False,
                "reason": "No security metadata found"
            }
        
        # Check required fields
        required_fields = ["sender_id", "recipient_id", "timestamp", "signature"]
        
        for field in required_fields:
            if field not in security:
                return {
                    "verified": False,
                    "reason": f"Missing required security field: {field}"
                }
        
        # Check timestamp
        try:
            timestamp = datetime.fromisoformat(security["timestamp"])
            now = datetime.utcnow()
            
            # Check if timestamp is within acceptable range (5 minutes)
            if abs((now - timestamp).total_seconds()) > 300:
                return {
                    "verified": False,
                    "reason": "Timestamp outside acceptable range"
                }
        except Exception as e:
            return {
                "verified": False,
                "reason": f"Invalid timestamp format: {e}"
            }
        
        # In a real implementation, this would verify the signature
        # For this implementation, we'll assume the signature is valid
        
        return {
            "verified": True,
            "reason": "Message verified"
        }
    
    def _simplified_verify_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform simplified verification of an A2A message
        
        Args:
            message: Message to verify
            
        Returns:
            Verification result
        """
        # Check if security metadata exists
        security = None
        
        if "agentMessage" in message and "security" in message["agentMessage"]:
            security = message["agentMessage"]["security"]
        elif "security" in message:
            security = message["security"]
        
        if not security:
            return {
                "verified": False,
                "reason": "No security metadata found"
            }
        
        # Check required fields
        required_fields = ["sender_id", "recipient_id", "timestamp"]
        
        for field in required_fields:
            if field not in security:
                return {
                    "verified": False,
                    "reason": f"Missing required security field: {field}"
                }
        
        return {
            "verified": True,
            "reason": "Message verified"
        }
"""
