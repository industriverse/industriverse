"""
Security & Compliance Layer Integration Manager for the Overseer System.

This module provides the Security & Compliance Layer Integration Manager for integrating with
the Industriverse Security & Compliance Layer components, enabling security policy enforcement,
compliance monitoring, and audit capabilities.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union, Callable

from src.integration.integration_manager import IntegrationManager
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class SecurityComplianceLayerIntegrationManager(IntegrationManager):
    """
    Integration Manager for the Security & Compliance Layer of the Industriverse Framework.
    
    This class provides integration with the Security & Compliance Layer components,
    enabling security policy enforcement, compliance monitoring, and audit capabilities.
    """
    
    def __init__(
        self,
        manager_id: str,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        config_service: ConfigService,
        auth_service: AuthService,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Security & Compliance Layer Integration Manager.
        
        Args:
            manager_id: Unique identifier for this manager
            mcp_bridge: MCP protocol bridge for internal communication
            a2a_bridge: A2A protocol bridge for external communication
            event_bus: Event bus client for event-driven communication
            data_access: Data access service for persistence
            config_service: Configuration service for settings
            auth_service: Authentication service for security
            config: Manager-specific configuration
            logger: Optional logger instance
        """
        super().__init__(
            manager_id=manager_id,
            manager_type="security_compliance_layer",
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            config=config,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize Security & Compliance Layer-specific resources
        self._security_policies = {}
        self._compliance_frameworks = {}
        self._audit_logs = {}
        
        # Initialize metrics
        self._metrics = {
            "total_security_policy_enforcements": 0,
            "total_compliance_checks": 0,
            "total_audit_events": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Security & Compliance Layer Integration Manager {manager_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Security & Compliance Layer operations
        self.mcp_bridge.register_context_handler(
            context_type="security_compliance_layer.security_policy",
            handler=self._handle_mcp_security_policy_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="security_compliance_layer.compliance_framework",
            handler=self._handle_mcp_compliance_framework_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="security_compliance_layer.audit",
            handler=self._handle_mcp_audit_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Security & Compliance Layer operations
        self.mcp_bridge.unregister_context_handler(
            context_type="security_compliance_layer.security_policy"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="security_compliance_layer.compliance_framework"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="security_compliance_layer.audit"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Security & Compliance Layer operations
        self.a2a_bridge.register_capability_handler(
            capability_type="security_policy_integration",
            handler=self._handle_a2a_security_policy_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="compliance_framework_integration",
            handler=self._handle_a2a_compliance_framework_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="audit_integration",
            handler=self._handle_a2a_audit_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Security & Compliance Layer operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="security_policy_integration"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="compliance_framework_integration"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="audit_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Security & Compliance Layer-related events
        self.event_bus.subscribe(
            topic="security_compliance_layer.security_policy.policy_enforced",
            handler=self._handle_security_policy_enforced_event
        )
        
        self.event_bus.subscribe(
            topic="security_compliance_layer.compliance_framework.compliance_checked",
            handler=self._handle_compliance_checked_event
        )
        
        self.event_bus.subscribe(
            topic="security_compliance_layer.audit.audit_event",
            handler=self._handle_audit_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Security & Compliance Layer-related events
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.security_policy.policy_enforced"
        )
        
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.compliance_framework.compliance_checked"
        )
        
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.audit.audit_event"
        )
    
    def _handle_mcp_security_policy_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Security Policy context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "enforce_security_policy":
                policy_id = context.get("policy_id")
                if not policy_id:
                    raise ValueError("policy_id is required")
                
                target_id = context.get("target_id")
                if not target_id:
                    raise ValueError("target_id is required")
                
                context_data = context.get("context_data", {})
                
                result = self.enforce_security_policy(
                    policy_id=policy_id,
                    target_id=target_id,
                    context_data=context_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_security_policy":
                policy_id = context.get("policy_id")
                if not policy_id:
                    raise ValueError("policy_id is required")
                
                policy_data = context.get("policy_data")
                if not policy_data:
                    raise ValueError("policy_data is required")
                
                result = self.register_security_policy(
                    policy_id=policy_id,
                    policy_data=policy_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_security_policy":
                policy_id = context.get("policy_id")
                if not policy_id:
                    raise ValueError("policy_id is required")
                
                result = self.get_security_policy(
                    policy_id=policy_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_security_policies":
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.list_security_policies(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Security Policy context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_compliance_framework_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Compliance Framework context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "check_compliance":
                framework_id = context.get("framework_id")
                if not framework_id:
                    raise ValueError("framework_id is required")
                
                target_id = context.get("target_id")
                if not target_id:
                    raise ValueError("target_id is required")
                
                context_data = context.get("context_data", {})
                
                result = self.check_compliance(
                    framework_id=framework_id,
                    target_id=target_id,
                    context_data=context_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_compliance_framework":
                framework_id = context.get("framework_id")
                if not framework_id:
                    raise ValueError("framework_id is required")
                
                framework_data = context.get("framework_data")
                if not framework_data:
                    raise ValueError("framework_data is required")
                
                result = self.register_compliance_framework(
                    framework_id=framework_id,
                    framework_data=framework_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_compliance_framework":
                framework_id = context.get("framework_id")
                if not framework_id:
                    raise ValueError("framework_id is required")
                
                result = self.get_compliance_framework(
                    framework_id=framework_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_compliance_frameworks":
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.list_compliance_frameworks(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Compliance Framework context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_audit_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Audit context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "log_audit_event":
                event_type = context.get("event_type")
                if not event_type:
                    raise ValueError("event_type is required")
                
                event_data = context.get("event_data")
                if not event_data:
                    raise ValueError("event_data is required")
                
                result = self.log_audit_event(
                    event_type=event_type,
                    event_data=event_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_audit_events":
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.get_audit_events(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Audit context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_security_policy_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Security Policy capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_security_policy":
                policy_id = capability_data.get("policy_id")
                if not policy_id:
                    raise ValueError("policy_id is required")
                
                result = self.get_security_policy(
                    policy_id=policy_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_security_policies":
                filter_criteria = capability_data.get("filter_criteria", {})
                
                result = self.list_security_policies(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Security Policy capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_compliance_framework_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Compliance Framework capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_compliance_framework":
                framework_id = capability_data.get("framework_id")
                if not framework_id:
                    raise ValueError("framework_id is required")
                
                result = self.get_compliance_framework(
                    framework_id=framework_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_compliance_frameworks":
                filter_criteria = capability_data.get("filter_criteria", {})
                
                result = self.list_compliance_frameworks(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Compliance Framework capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_audit_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Audit capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_audit_events":
                filter_criteria = capability_data.get("filter_criteria", {})
                
                result = self.get_audit_events(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Audit capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_security_policy_enforced_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle security policy enforced event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            policy_id = event_data.get("policy_id")
            target_id = event_data.get("target_id")
            result = event_data.get("result")
            
            # Validate required fields
            if not policy_id:
                self.logger.warning("Received security policy enforced event without policy_id")
                return
            
            if not target_id:
                self.logger.warning(f"Received security policy enforced event for policy {policy_id} without target_id")
                return
            
            if result is None:
                self.logger.warning(f"Received security policy enforced event for policy {policy_id} and target {target_id} without result")
                return
            
            self.logger.info(f"Security policy {policy_id} enforced on target {target_id} with result {result}")
            
            # Log audit event
            self.log_audit_event(
                event_type="security_policy_enforced",
                event_data={
                    "policy_id": policy_id,
                    "target_id": target_id,
                    "result": result,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
        except Exception as e:
            self.logger.error(f"Error handling security policy enforced event: {str(e)}")
    
    def _handle_compliance_checked_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle compliance checked event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            framework_id = event_data.get("framework_id")
            target_id = event_data.get("target_id")
            result = event_data.get("result")
            
            # Validate required fields
            if not framework_id:
                self.logger.warning("Received compliance checked event without framework_id")
                return
            
            if not target_id:
                self.logger.warning(f"Received compliance checked event for framework {framework_id} without target_id")
                return
            
            if result is None:
                self.logger.warning(f"Received compliance checked event for framework {framework_id} and target {target_id} without result")
                return
            
            self.logger.info(f"Compliance framework {framework_id} checked on target {target_id} with result {result}")
            
            # Log audit event
            self.log_audit_event(
                event_type="compliance_checked",
                event_data={
                    "framework_id": framework_id,
                    "target_id": target_id,
                    "result": result,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
        except Exception as e:
            self.logger.error(f"Error handling compliance checked event: {str(e)}")
    
    def _handle_audit_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle audit event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            event_type = event_data.get("event_type")
            event_data_content = event_data.get("event_data")
            
            # Validate required fields
            if not event_type:
                self.logger.warning("Received audit event without event_type")
                return
            
            if not event_data_content:
                self.logger.warning(f"Received audit event of type {event_type} without event_data")
                return
            
            self.logger.info(f"Audit event of type {event_type} received")
            
            # Store audit event
            if event_type not in self._audit_logs:
                self._audit_logs[event_type] = []
            
            self._audit_logs[event_type].append(event_data_content)
            
            # Update metrics
            self._metrics["total_audit_events"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling audit event: {str(e)}")
    
    def enforce_security_policy(self, policy_id: str, target_id: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enforce a security policy on a target.
        
        Args:
            policy_id: Policy ID
            target_id: Target ID
            context_data: Optional context data
        
        Returns:
            Enforcement result
        """
        try:
            # Check if policy exists
            if policy_id not in self._security_policies:
                raise ValueError(f"Security policy {policy_id} not found")
            
            # Initialize context data if not provided
            if context_data is None:
                context_data = {}
            
            # Get policy
            policy = self._security_policies[policy_id]
            
            # Enforce policy
            # In a real implementation, this would apply the policy rules
            # For now, we'll just return a success result
            enforcement_result = {
                "enforced": True,
                "policy_id": policy_id,
                "target_id": target_id,
                "timestamp": self.data_access.get_current_timestamp()
            }
            
            # Publish security policy enforced event
            self.event_bus.publish(
                topic="security_compliance_layer.security_policy.policy_enforced",
                data={
                    "policy_id": policy_id,
                    "target_id": target_id,
                    "result": enforcement_result
                }
            )
            
            # Update metrics
            self._metrics["total_security_policy_enforcements"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return enforcement_result
        except Exception as e:
            self.logger.error(f"Error enforcing security policy {policy_id} on target {target_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_security_policy(self, policy_id: str, policy_data: Dict[str, Any]) -> bool:
        """
        Register a security policy.
        
        Args:
            policy_id: Policy ID
            policy_data: Policy data
        
        Returns:
            Success flag
        """
        try:
            # Validate policy data
            # In a real implementation, this would validate against a schema
            # For now, we'll just check for required fields
            if "name" not in policy_data:
                raise ValueError("Policy data must have a name field")
            
            if "description" not in policy_data:
                raise ValueError("Policy data must have a description field")
            
            if "rules" not in policy_data:
                raise ValueError("Policy data must have a rules field")
            
            # Register policy
            self._security_policies[policy_id] = policy_data
            
            self.logger.info(f"Registered security policy {policy_id}")
            
            # Log audit event
            self.log_audit_event(
                event_type="security_policy_registered",
                event_data={
                    "policy_id": policy_id,
                    "policy_name": policy_data.get("name"),
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering security policy {policy_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_security_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Get a security policy.
        
        Args:
            policy_id: Policy ID
        
        Returns:
            Policy data
        """
        try:
            # Check if policy exists
            if policy_id not in self._security_policies:
                raise ValueError(f"Security policy {policy_id} not found")
            
            # Get policy
            policy = self._security_policies[policy_id]
            
            return policy
        except Exception as e:
            self.logger.error(f"Error getting security policy {policy_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_security_policies(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List security policies.
        
        Args:
            filter_criteria: Optional filter criteria
        
        Returns:
            List of policy data
        """
        try:
            # Apply filters if provided
            if filter_criteria:
                # In a real implementation, this would apply the filter criteria
                # For now, we'll just return all policies
                policies = [
                    {
                        "id": policy_id,
                        "data": policy_data
                    }
                    for policy_id, policy_data in self._security_policies.items()
                ]
            else:
                policies = [
                    {
                        "id": policy_id,
                        "data": policy_data
                    }
                    for policy_id, policy_data in self._security_policies.items()
                ]
            
            return policies
        except Exception as e:
            self.logger.error(f"Error listing security policies: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def check_compliance(self, framework_id: str, target_id: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check compliance of a target against a framework.
        
        Args:
            framework_id: Framework ID
            target_id: Target ID
            context_data: Optional context data
        
        Returns:
            Compliance result
        """
        try:
            # Check if framework exists
            if framework_id not in self._compliance_frameworks:
                raise ValueError(f"Compliance framework {framework_id} not found")
            
            # Initialize context data if not provided
            if context_data is None:
                context_data = {}
            
            # Get framework
            framework = self._compliance_frameworks[framework_id]
            
            # Check compliance
            # In a real implementation, this would check compliance against the framework
            # For now, we'll just return a success result
            compliance_result = {
                "compliant": True,
                "framework_id": framework_id,
                "target_id": target_id,
                "timestamp": self.data_access.get_current_timestamp()
            }
            
            # Publish compliance checked event
            self.event_bus.publish(
                topic="security_compliance_layer.compliance_framework.compliance_checked",
                data={
                    "framework_id": framework_id,
                    "target_id": target_id,
                    "result": compliance_result
                }
            )
            
            # Update metrics
            self._metrics["total_compliance_checks"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return compliance_result
        except Exception as e:
            self.logger.error(f"Error checking compliance of target {target_id} against framework {framework_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_compliance_framework(self, framework_id: str, framework_data: Dict[str, Any]) -> bool:
        """
        Register a compliance framework.
        
        Args:
            framework_id: Framework ID
            framework_data: Framework data
        
        Returns:
            Success flag
        """
        try:
            # Validate framework data
            # In a real implementation, this would validate against a schema
            # For now, we'll just check for required fields
            if "name" not in framework_data:
                raise ValueError("Framework data must have a name field")
            
            if "description" not in framework_data:
                raise ValueError("Framework data must have a description field")
            
            if "requirements" not in framework_data:
                raise ValueError("Framework data must have a requirements field")
            
            # Register framework
            self._compliance_frameworks[framework_id] = framework_data
            
            self.logger.info(f"Registered compliance framework {framework_id}")
            
            # Log audit event
            self.log_audit_event(
                event_type="compliance_framework_registered",
                event_data={
                    "framework_id": framework_id,
                    "framework_name": framework_data.get("name"),
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering compliance framework {framework_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_compliance_framework(self, framework_id: str) -> Dict[str, Any]:
        """
        Get a compliance framework.
        
        Args:
            framework_id: Framework ID
        
        Returns:
            Framework data
        """
        try:
            # Check if framework exists
            if framework_id not in self._compliance_frameworks:
                raise ValueError(f"Compliance framework {framework_id} not found")
            
            # Get framework
            framework = self._compliance_frameworks[framework_id]
            
            return framework
        except Exception as e:
            self.logger.error(f"Error getting compliance framework {framework_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_compliance_frameworks(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List compliance frameworks.
        
        Args:
            filter_criteria: Optional filter criteria
        
        Returns:
            List of framework data
        """
        try:
            # Apply filters if provided
            if filter_criteria:
                # In a real implementation, this would apply the filter criteria
                # For now, we'll just return all frameworks
                frameworks = [
                    {
                        "id": framework_id,
                        "data": framework_data
                    }
                    for framework_id, framework_data in self._compliance_frameworks.items()
                ]
            else:
                frameworks = [
                    {
                        "id": framework_id,
                        "data": framework_data
                    }
                    for framework_id, framework_data in self._compliance_frameworks.items()
                ]
            
            return frameworks
        except Exception as e:
            self.logger.error(f"Error listing compliance frameworks: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def log_audit_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Log an audit event.
        
        Args:
            event_type: Event type
            event_data: Event data
        
        Returns:
            Success flag
        """
        try:
            # Validate event data
            # In a real implementation, this would validate against a schema
            # For now, we'll just check for required fields
            if "timestamp" not in event_data:
                event_data["timestamp"] = self.data_access.get_current_timestamp()
            
            # Log event
            if event_type not in self._audit_logs:
                self._audit_logs[event_type] = []
            
            self._audit_logs[event_type].append(event_data)
            
            # Publish audit event
            self.event_bus.publish(
                topic="security_compliance_layer.audit.audit_event",
                data={
                    "event_type": event_type,
                    "event_data": event_data
                }
            )
            
            # Update metrics
            self._metrics["total_audit_events"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error logging audit event of type {event_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_audit_events(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get audit events.
        
        Args:
            filter_criteria: Optional filter criteria
        
        Returns:
            List of audit events
        """
        try:
            # Apply filters if provided
            if filter_criteria:
                # Extract filter criteria
                event_type = filter_criteria.get("event_type")
                start_time = filter_criteria.get("start_time")
                end_time = filter_criteria.get("end_time")
                
                # Filter by event type if provided
                if event_type:
                    if event_type not in self._audit_logs:
                        return []
                    
                    events = [
                        {
                            "event_type": event_type,
                            "event_data": event_data
                        }
                        for event_data in self._audit_logs[event_type]
                    ]
                else:
                    events = [
                        {
                            "event_type": event_type,
                            "event_data": event_data
                        }
                        for event_type, event_data_list in self._audit_logs.items()
                        for event_data in event_data_list
                    ]
                
                # Filter by time range if provided
                if start_time or end_time:
                    filtered_events = []
                    
                    for event in events:
                        event_timestamp = event["event_data"].get("timestamp")
                        
                        if not event_timestamp:
                            continue
                        
                        if start_time and event_timestamp < start_time:
                            continue
                        
                        if end_time and event_timestamp > end_time:
                            continue
                        
                        filtered_events.append(event)
                    
                    events = filtered_events
            else:
                events = [
                    {
                        "event_type": event_type,
                        "event_data": event_data
                    }
                    for event_type, event_data_list in self._audit_logs.items()
                    for event_data in event_data_list
                ]
            
            return events
        except Exception as e:
            self.logger.error(f"Error getting audit events: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the manager metrics.
        
        Returns:
            Manager metrics
        """
        return self._metrics
    
    def reset_metrics(self) -> Dict[str, Any]:
        """
        Reset the manager metrics.
        
        Returns:
            Reset manager metrics
        """
        self._metrics = {
            "total_security_policy_enforcements": 0,
            "total_compliance_checks": 0,
            "total_audit_events": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
