"""
Security Policy Adapter for the Security & Compliance Layer Integration.

This module provides the Security Policy Adapter for integrating with
the Industriverse Security Policy components, enabling security policy
enforcement and management.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union, Callable

from src.integration.base_integration_adapter import BaseIntegrationAdapter
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class SecurityPolicyAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for the Security Policy components of the Industriverse Framework.
    
    This class provides integration with the Security Policy components,
    enabling security policy enforcement and management.
    """
    
    def __init__(
        self,
        adapter_id: str,
        manager: Any,
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
        Initialize the Security Policy Adapter.
        
        Args:
            adapter_id: Unique identifier for this adapter
            manager: Parent integration manager
            mcp_bridge: MCP protocol bridge for internal communication
            a2a_bridge: A2A protocol bridge for external communication
            event_bus: Event bus client for event-driven communication
            data_access: Data access service for persistence
            config_service: Configuration service for settings
            auth_service: Authentication service for security
            config: Adapter-specific configuration
            logger: Optional logger instance
        """
        super().__init__(
            adapter_id=adapter_id,
            adapter_type="security_policy",
            manager=manager,
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            config=config,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize Security Policy-specific resources
        self._security_policies = {}
        self._policy_enforcement_history = {}
        
        # Initialize metrics
        self._metrics = {
            "total_policy_enforcements": 0,
            "total_policy_registrations": 0,
            "total_policy_lookups": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Security Policy Adapter {adapter_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Security Policy operations
        self.mcp_bridge.register_context_handler(
            context_type="security_compliance_layer.security_policy",
            handler=self._handle_mcp_security_policy_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Security Policy operations
        self.mcp_bridge.unregister_context_handler(
            context_type="security_compliance_layer.security_policy"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Security Policy operations
        self.a2a_bridge.register_capability_handler(
            capability_type="security_policy_integration",
            handler=self._handle_a2a_security_policy_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Security Policy operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="security_policy_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Security Policy-related events
        self.event_bus.subscribe(
            topic="security_compliance_layer.security_policy.policy_enforced",
            handler=self._handle_policy_enforced_event
        )
        
        self.event_bus.subscribe(
            topic="security_compliance_layer.security_policy.policy_registered",
            handler=self._handle_policy_registered_event
        )
        
        self.event_bus.subscribe(
            topic="security_compliance_layer.security_policy.policy_updated",
            handler=self._handle_policy_updated_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Security Policy-related events
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.security_policy.policy_enforced"
        )
        
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.security_policy.policy_registered"
        )
        
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.security_policy.policy_updated"
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
            if action == "enforce_policy":
                policy_id = context.get("policy_id")
                if not policy_id:
                    raise ValueError("policy_id is required")
                
                target_id = context.get("target_id")
                if not target_id:
                    raise ValueError("target_id is required")
                
                context_data = context.get("context_data", {})
                
                result = self.enforce_policy(
                    policy_id=policy_id,
                    target_id=target_id,
                    context_data=context_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_policy":
                policy_id = context.get("policy_id")
                if not policy_id:
                    raise ValueError("policy_id is required")
                
                policy_data = context.get("policy_data")
                if not policy_data:
                    raise ValueError("policy_data is required")
                
                result = self.register_policy(
                    policy_id=policy_id,
                    policy_data=policy_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_policy":
                policy_id = context.get("policy_id")
                if not policy_id:
                    raise ValueError("policy_id is required")
                
                result = self.get_policy(
                    policy_id=policy_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_policies":
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.list_policies(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_enforcement_history":
                policy_id = context.get("policy_id")
                if not policy_id:
                    raise ValueError("policy_id is required")
                
                target_id = context.get("target_id", None)
                
                result = self.get_enforcement_history(
                    policy_id=policy_id,
                    target_id=target_id
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
            if action == "get_policy":
                policy_id = capability_data.get("policy_id")
                if not policy_id:
                    raise ValueError("policy_id is required")
                
                result = self.get_policy(
                    policy_id=policy_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_policies":
                filter_criteria = capability_data.get("filter_criteria", {})
                
                result = self.list_policies(
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
    
    def _handle_policy_enforced_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle policy enforced event.
        
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
                self.logger.warning("Received policy enforced event without policy_id")
                return
            
            if not target_id:
                self.logger.warning(f"Received policy enforced event for policy {policy_id} without target_id")
                return
            
            if not result:
                self.logger.warning(f"Received policy enforced event for policy {policy_id} and target {target_id} without result")
                return
            
            self.logger.info(f"Policy {policy_id} enforced on target {target_id}")
            
            # Update enforcement history
            if policy_id not in self._policy_enforcement_history:
                self._policy_enforcement_history[policy_id] = {}
            
            if target_id not in self._policy_enforcement_history[policy_id]:
                self._policy_enforcement_history[policy_id][target_id] = []
            
            self._policy_enforcement_history[policy_id][target_id].append(result)
            
            # Update metrics
            self._metrics["total_policy_enforcements"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling policy enforced event: {str(e)}")
    
    def _handle_policy_registered_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle policy registered event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            policy_id = event_data.get("policy_id")
            policy_data = event_data.get("policy_data")
            
            # Validate required fields
            if not policy_id:
                self.logger.warning("Received policy registered event without policy_id")
                return
            
            if not policy_data:
                self.logger.warning(f"Received policy registered event for policy {policy_id} without policy_data")
                return
            
            self.logger.info(f"Policy {policy_id} registered")
            
            # Update local policy cache
            self._security_policies[policy_id] = policy_data
            
            # Update metrics
            self._metrics["total_policy_registrations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling policy registered event: {str(e)}")
    
    def _handle_policy_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle policy updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            policy_id = event_data.get("policy_id")
            policy_data = event_data.get("policy_data")
            
            # Validate required fields
            if not policy_id:
                self.logger.warning("Received policy updated event without policy_id")
                return
            
            if not policy_data:
                self.logger.warning(f"Received policy updated event for policy {policy_id} without policy_data")
                return
            
            self.logger.info(f"Policy {policy_id} updated")
            
            # Update local policy cache
            self._security_policies[policy_id] = policy_data
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling policy updated event: {str(e)}")
    
    def enforce_policy(self, policy_id: str, target_id: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
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
            
            # Publish policy enforced event
            self.event_bus.publish(
                topic="security_compliance_layer.security_policy.policy_enforced",
                data={
                    "policy_id": policy_id,
                    "target_id": target_id,
                    "result": enforcement_result
                }
            )
            
            # Update enforcement history
            if policy_id not in self._policy_enforcement_history:
                self._policy_enforcement_history[policy_id] = {}
            
            if target_id not in self._policy_enforcement_history[policy_id]:
                self._policy_enforcement_history[policy_id][target_id] = []
            
            self._policy_enforcement_history[policy_id][target_id].append(enforcement_result)
            
            # Update metrics
            self._metrics["total_policy_enforcements"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return enforcement_result
        except Exception as e:
            self.logger.error(f"Error enforcing security policy {policy_id} on target {target_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_policy(self, policy_id: str, policy_data: Dict[str, Any]) -> bool:
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
            
            # Initialize enforcement history if not exists
            if policy_id not in self._policy_enforcement_history:
                self._policy_enforcement_history[policy_id] = {}
            
            # Publish policy registered event
            self.event_bus.publish(
                topic="security_compliance_layer.security_policy.policy_registered",
                data={
                    "policy_id": policy_id,
                    "policy_data": policy_data
                }
            )
            
            self.logger.info(f"Registered security policy {policy_id}")
            
            # Update metrics
            self._metrics["total_policy_registrations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering security policy {policy_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_policy(self, policy_id: str) -> Dict[str, Any]:
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
            
            # Update metrics
            self._metrics["total_policy_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return policy
        except Exception as e:
            self.logger.error(f"Error getting security policy {policy_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_policies(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
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
            
            # Update metrics
            self._metrics["total_policy_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return policies
        except Exception as e:
            self.logger.error(f"Error listing security policies: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_enforcement_history(self, policy_id: str, target_id: str = None) -> List[Dict[str, Any]]:
        """
        Get enforcement history for a policy.
        
        Args:
            policy_id: Policy ID
            target_id: Optional target ID
        
        Returns:
            List of enforcement results
        """
        try:
            # Check if policy exists
            if policy_id not in self._security_policies:
                raise ValueError(f"Security policy {policy_id} not found")
            
            # Check if policy has enforcement history
            if policy_id not in self._policy_enforcement_history:
                return []
            
            # Get enforcement history for specific target if provided
            if target_id:
                if target_id not in self._policy_enforcement_history[policy_id]:
                    return []
                
                history = self._policy_enforcement_history[policy_id][target_id]
            else:
                # Get enforcement history for all targets
                history = [
                    result
                    for target_history in self._policy_enforcement_history[policy_id].values()
                    for result in target_history
                ]
            
            # Update metrics
            self._metrics["total_policy_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return history
        except Exception as e:
            self.logger.error(f"Error getting enforcement history for policy {policy_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the adapter metrics.
        
        Returns:
            Adapter metrics
        """
        return self._metrics
    
    def reset_metrics(self) -> Dict[str, Any]:
        """
        Reset the adapter metrics.
        
        Returns:
            Reset adapter metrics
        """
        self._metrics = {
            "total_policy_enforcements": 0,
            "total_policy_registrations": 0,
            "total_policy_lookups": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
