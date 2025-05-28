"""
Audit Adapter for the Security & Compliance Layer Integration.

This module provides the Audit Adapter for integrating with
the Industriverse Audit components, enabling audit logging
and management.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime

from src.integration.base_integration_adapter import BaseIntegrationAdapter
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class AuditAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for the Audit components of the Industriverse Framework.
    
    This class provides integration with the Audit components,
    enabling audit logging and management.
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
        Initialize the Audit Adapter.
        
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
            adapter_type="audit",
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
        
        # Initialize Audit-specific resources
        self._audit_logs = {}
        self._audit_config = config.get("audit_config", {})
        
        # Initialize metrics
        self._metrics = {
            "total_audit_events": 0,
            "total_audit_queries": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Audit Adapter {adapter_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Audit operations
        self.mcp_bridge.register_context_handler(
            context_type="security_compliance_layer.audit",
            handler=self._handle_mcp_audit_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Audit operations
        self.mcp_bridge.unregister_context_handler(
            context_type="security_compliance_layer.audit"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Audit operations
        self.a2a_bridge.register_capability_handler(
            capability_type="audit_integration",
            handler=self._handle_a2a_audit_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Audit operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="audit_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Audit-related events
        self.event_bus.subscribe(
            topic="security_compliance_layer.audit.audit_event",
            handler=self._handle_audit_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Audit-related events
        self.event_bus.unsubscribe(
            topic="security_compliance_layer.audit.audit_event"
        )
    
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
            
            elif action == "get_audit_event_types":
                result = self.get_audit_event_types()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_audit_statistics":
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.get_audit_statistics(
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
            
            elif action == "get_audit_event_types":
                result = self.get_audit_event_types()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_audit_statistics":
                filter_criteria = capability_data.get("filter_criteria", {})
                
                result = self.get_audit_statistics(
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
            
            # Add timestamp if not present
            if "timestamp" not in event_data_content:
                event_data_content["timestamp"] = self.data_access.get_current_timestamp()
            
            self._audit_logs[event_type].append(event_data_content)
            
            # Update metrics
            self._metrics["total_audit_events"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling audit event: {str(e)}")
    
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
            
            if "user_id" not in event_data and self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    event_data["user_id"] = current_user.get("id")
            
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
                user_id = filter_criteria.get("user_id")
                
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
                
                # Filter by user ID if provided
                if user_id:
                    filtered_events = []
                    
                    for event in events:
                        event_user_id = event["event_data"].get("user_id")
                        
                        if not event_user_id:
                            continue
                        
                        if event_user_id != user_id:
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
            
            # Update metrics
            self._metrics["total_audit_queries"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return events
        except Exception as e:
            self.logger.error(f"Error getting audit events: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_audit_event_types(self) -> List[str]:
        """
        Get audit event types.
        
        Returns:
            List of audit event types
        """
        try:
            # Get event types
            event_types = list(self._audit_logs.keys())
            
            # Update metrics
            self._metrics["total_audit_queries"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return event_types
        except Exception as e:
            self.logger.error(f"Error getting audit event types: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_audit_statistics(self, filter_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get audit statistics.
        
        Args:
            filter_criteria: Optional filter criteria
        
        Returns:
            Audit statistics
        """
        try:
            # Get audit events with filters
            events = self.get_audit_events(filter_criteria)
            
            # Calculate statistics
            statistics = {
                "total_events": len(events),
                "events_by_type": {},
                "events_by_user": {},
                "events_by_day": {}
            }
            
            for event in events:
                event_type = event["event_type"]
                event_data = event["event_data"]
                
                # Count events by type
                if event_type not in statistics["events_by_type"]:
                    statistics["events_by_type"][event_type] = 0
                
                statistics["events_by_type"][event_type] += 1
                
                # Count events by user
                user_id = event_data.get("user_id")
                if user_id:
                    if user_id not in statistics["events_by_user"]:
                        statistics["events_by_user"][user_id] = 0
                    
                    statistics["events_by_user"][user_id] += 1
                
                # Count events by day
                timestamp = event_data.get("timestamp")
                if timestamp:
                    # Convert timestamp to date string
                    date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                    
                    if date_str not in statistics["events_by_day"]:
                        statistics["events_by_day"][date_str] = 0
                    
                    statistics["events_by_day"][date_str] += 1
            
            # Update metrics
            self._metrics["total_audit_queries"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return statistics
        except Exception as e:
            self.logger.error(f"Error getting audit statistics: {str(e)}")
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
            "total_audit_events": 0,
            "total_audit_queries": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
