"""
Compliance Framework Adapter for the Security & Compliance Layer Integration.

This module provides the Compliance Framework Adapter for integrating with
the Industriverse Compliance Framework components, enabling compliance
monitoring and management.

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

class ComplianceFrameworkAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for the Compliance Framework components of the Industriverse Framework.
    
    This class provides integration with the Compliance Framework components,
    enabling compliance monitoring and management.
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
        Initialize the Compliance Framework Adapter.
        
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
            adapter_type="compliance_framework",
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
        
        # Initialize Compliance Framework-specific resources
        self._compliance_frameworks = {}
        self._compliance_check_history = {}
        
        # Initialize metrics
        self._metrics = {
            "total_compliance_checks": 0,
            "total_framework_registrations": 0,
            "total_framework_lookups": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Compliance Framework Adapter {adapter_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Compliance Framework operations
        self.mcp_bridge.register_context_handler(
            context_type="security_compliance_layer.compliance_framework",
            handler=self._handle_mcp_compliance_framework_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Compliance Framework operations
        self.mcp_bridge.unregister_context_handler(
            context_type="security_compliance_layer.compliance_framework"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Compliance Framework operations
        self.a2a_bridge.register_capability_handler(
            capability_type="compliance_framework_integration",
            handler=self._handle_a2a_compliance_framework_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Compliance Framework operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="compliance_framework_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Compliance Framework-related events
        self.event_bus.subscribe(
            topic="security_compliance_layer.compliance_framework.compliance_checked",
            handler=self._handle_compliance_checked_event
        )
        
        self.event_bus.subscribe(
            topic="security_compliance_layer.compliance_framework.framework_registered",
            handler=self._handle_framework_registered_event
        )
        
        self.event_bus.subscribe(
            topic="security_compliance_layer.compliance_framework.framework_updated",
            handler=self._handle_framework_updated_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Compliance Framework-related events
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.compliance_framework.compliance_checked"
        )
        
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.compliance_framework.framework_registered"
        )
        
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.compliance_framework.framework_updated"
        )
    
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
            
            elif action == "register_framework":
                framework_id = context.get("framework_id")
                if not framework_id:
                    raise ValueError("framework_id is required")
                
                framework_data = context.get("framework_data")
                if not framework_data:
                    raise ValueError("framework_data is required")
                
                result = self.register_framework(
                    framework_id=framework_id,
                    framework_data=framework_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_framework":
                framework_id = context.get("framework_id")
                if not framework_id:
                    raise ValueError("framework_id is required")
                
                result = self.get_framework(
                    framework_id=framework_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_frameworks":
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.list_frameworks(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_compliance_history":
                framework_id = context.get("framework_id")
                if not framework_id:
                    raise ValueError("framework_id is required")
                
                target_id = context.get("target_id", None)
                
                result = self.get_compliance_history(
                    framework_id=framework_id,
                    target_id=target_id
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
            if action == "get_framework":
                framework_id = capability_data.get("framework_id")
                if not framework_id:
                    raise ValueError("framework_id is required")
                
                result = self.get_framework(
                    framework_id=framework_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_frameworks":
                filter_criteria = capability_data.get("filter_criteria", {})
                
                result = self.list_frameworks(
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
            
            if not result:
                self.logger.warning(f"Received compliance checked event for framework {framework_id} and target {target_id} without result")
                return
            
            self.logger.info(f"Compliance framework {framework_id} checked on target {target_id}")
            
            # Update compliance check history
            if framework_id not in self._compliance_check_history:
                self._compliance_check_history[framework_id] = {}
            
            if target_id not in self._compliance_check_history[framework_id]:
                self._compliance_check_history[framework_id][target_id] = []
            
            self._compliance_check_history[framework_id][target_id].append(result)
            
            # Update metrics
            self._metrics["total_compliance_checks"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling compliance checked event: {str(e)}")
    
    def _handle_framework_registered_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle framework registered event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            framework_id = event_data.get("framework_id")
            framework_data = event_data.get("framework_data")
            
            # Validate required fields
            if not framework_id:
                self.logger.warning("Received framework registered event without framework_id")
                return
            
            if not framework_data:
                self.logger.warning(f"Received framework registered event for framework {framework_id} without framework_data")
                return
            
            self.logger.info(f"Compliance framework {framework_id} registered")
            
            # Update local framework cache
            self._compliance_frameworks[framework_id] = framework_data
            
            # Update metrics
            self._metrics["total_framework_registrations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling framework registered event: {str(e)}")
    
    def _handle_framework_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle framework updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            framework_id = event_data.get("framework_id")
            framework_data = event_data.get("framework_data")
            
            # Validate required fields
            if not framework_id:
                self.logger.warning("Received framework updated event without framework_id")
                return
            
            if not framework_data:
                self.logger.warning(f"Received framework updated event for framework {framework_id} without framework_data")
                return
            
            self.logger.info(f"Compliance framework {framework_id} updated")
            
            # Update local framework cache
            self._compliance_frameworks[framework_id] = framework_data
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling framework updated event: {str(e)}")
    
    def check_compliance(self, framework_id: str, target_id: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check compliance of a target against a framework.
        
        Args:
            framework_id: Framework ID
            target_id: Target ID
            context_data: Optional context data
        
        Returns:
            Compliance check result
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
            
            # Update compliance check history
            if framework_id not in self._compliance_check_history:
                self._compliance_check_history[framework_id] = {}
            
            if target_id not in self._compliance_check_history[framework_id]:
                self._compliance_check_history[framework_id][target_id] = []
            
            self._compliance_check_history[framework_id][target_id].append(compliance_result)
            
            # Update metrics
            self._metrics["total_compliance_checks"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return compliance_result
        except Exception as e:
            self.logger.error(f"Error checking compliance of target {target_id} against framework {framework_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_framework(self, framework_id: str, framework_data: Dict[str, Any]) -> bool:
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
            
            # Initialize compliance check history if not exists
            if framework_id not in self._compliance_check_history:
                self._compliance_check_history[framework_id] = {}
            
            # Publish framework registered event
            self.event_bus.publish(
                topic="security_compliance_layer.compliance_framework.framework_registered",
                data={
                    "framework_id": framework_id,
                    "framework_data": framework_data
                }
            )
            
            self.logger.info(f"Registered compliance framework {framework_id}")
            
            # Update metrics
            self._metrics["total_framework_registrations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering compliance framework {framework_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_framework(self, framework_id: str) -> Dict[str, Any]:
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
            
            # Update metrics
            self._metrics["total_framework_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return framework
        except Exception as e:
            self.logger.error(f"Error getting compliance framework {framework_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_frameworks(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
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
            
            # Update metrics
            self._metrics["total_framework_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return frameworks
        except Exception as e:
            self.logger.error(f"Error listing compliance frameworks: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_compliance_history(self, framework_id: str, target_id: str = None) -> List[Dict[str, Any]]:
        """
        Get compliance check history for a framework.
        
        Args:
            framework_id: Framework ID
            target_id: Optional target ID
        
        Returns:
            List of compliance check results
        """
        try:
            # Check if framework exists
            if framework_id not in self._compliance_frameworks:
                raise ValueError(f"Compliance framework {framework_id} not found")
            
            # Check if framework has compliance check history
            if framework_id not in self._compliance_check_history:
                return []
            
            # Get compliance check history for specific target if provided
            if target_id:
                if target_id not in self._compliance_check_history[framework_id]:
                    return []
                
                history = self._compliance_check_history[framework_id][target_id]
            else:
                # Get compliance check history for all targets
                history = [
                    result
                    for target_history in self._compliance_check_history[framework_id].values()
                    for result in target_history
                ]
            
            # Update metrics
            self._metrics["total_framework_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return history
        except Exception as e:
            self.logger.error(f"Error getting compliance check history for framework {framework_id}: {str(e)}")
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
            "total_compliance_checks": 0,
            "total_framework_registrations": 0,
            "total_framework_lookups": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
