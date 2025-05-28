"""
Application Layer Integration Manager for the Overseer System.

This module provides the Application Layer Integration Manager for integrating with
the Industriverse Application Layer components, enabling application management,
deployment, and monitoring.

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

class ApplicationLayerIntegrationManager(IntegrationManager):
    """
    Integration Manager for the Application Layer of the Industriverse Framework.
    
    This class provides integration with the Application Layer components,
    enabling application management, deployment, and monitoring.
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
        Initialize the Application Layer Integration Manager.
        
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
            manager_type="application_layer",
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            config=config,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize Application Layer-specific resources
        self._applications = {}
        self._deployments = {}
        self._monitors = {}
        
        # Initialize metrics
        self._metrics = {
            "total_application_deployments": 0,
            "total_application_updates": 0,
            "total_application_status_checks": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Application Layer Integration Manager {manager_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Application Layer operations
        self.mcp_bridge.register_context_handler(
            context_type="application_layer.application",
            handler=self._handle_mcp_application_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="application_layer.deployment",
            handler=self._handle_mcp_deployment_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="application_layer.monitor",
            handler=self._handle_mcp_monitor_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Application Layer operations
        self.mcp_bridge.unregister_context_handler(
            context_type="application_layer.application"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="application_layer.deployment"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="application_layer.monitor"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Application Layer operations
        self.a2a_bridge.register_capability_handler(
            capability_type="application_integration",
            handler=self._handle_a2a_application_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="deployment_integration",
            handler=self._handle_a2a_deployment_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="monitor_integration",
            handler=self._handle_a2a_monitor_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Application Layer operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="application_integration"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="deployment_integration"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="monitor_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Application Layer-related events
        self.event_bus.subscribe(
            topic="application_layer.application.application_created",
            handler=self._handle_application_created_event
        )
        
        self.event_bus.subscribe(
            topic="application_layer.application.application_updated",
            handler=self._handle_application_updated_event
        )
        
        self.event_bus.subscribe(
            topic="application_layer.deployment.deployment_started",
            handler=self._handle_deployment_started_event
        )
        
        self.event_bus.subscribe(
            topic="application_layer.deployment.deployment_completed",
            handler=self._handle_deployment_completed_event
        )
        
        self.event_bus.subscribe(
            topic="application_layer.monitor.status_changed",
            handler=self._handle_status_changed_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Application Layer-related events
        self.event_bus.unsubscribe(
            topic="application_layer.application.application_created"
        )
        
        self.event_bus.unsubscribe(
            topic="application_layer.application.application_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="application_layer.deployment.deployment_started"
        )
        
        self.event_bus.unsubscribe(
            topic="application_layer.deployment.deployment_completed"
        )
        
        self.event_bus.unsubscribe(
            topic="application_layer.monitor.status_changed"
        )
    
    def _handle_mcp_application_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Application context.
        
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
            if action == "create_application":
                application_data = context.get("application_data")
                if not application_data:
                    raise ValueError("application_data is required")
                
                result = self.create_application(
                    application_data=application_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "update_application":
                application_id = context.get("application_id")
                if not application_id:
                    raise ValueError("application_id is required")
                
                application_data = context.get("application_data")
                if not application_data:
                    raise ValueError("application_data is required")
                
                result = self.update_application(
                    application_id=application_id,
                    application_data=application_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_application":
                application_id = context.get("application_id")
                if not application_id:
                    raise ValueError("application_id is required")
                
                result = self.get_application(
                    application_id=application_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_applications":
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.list_applications(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Application context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_deployment_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Deployment context.
        
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
            if action == "deploy_application":
                application_id = context.get("application_id")
                if not application_id:
                    raise ValueError("application_id is required")
                
                deployment_config = context.get("deployment_config", {})
                
                result = self.deploy_application(
                    application_id=application_id,
                    deployment_config=deployment_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_deployment_status":
                deployment_id = context.get("deployment_id")
                if not deployment_id:
                    raise ValueError("deployment_id is required")
                
                result = self.get_deployment_status(
                    deployment_id=deployment_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_deployments":
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.list_deployments(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Deployment context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_monitor_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Monitor context.
        
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
            if action == "get_application_status":
                application_id = context.get("application_id")
                if not application_id:
                    raise ValueError("application_id is required")
                
                result = self.get_application_status(
                    application_id=application_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_application_metrics":
                application_id = context.get("application_id")
                if not application_id:
                    raise ValueError("application_id is required")
                
                metric_names = context.get("metric_names", [])
                
                result = self.get_application_metrics(
                    application_id=application_id,
                    metric_names=metric_names
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_application_logs":
                application_id = context.get("application_id")
                if not application_id:
                    raise ValueError("application_id is required")
                
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.get_application_logs(
                    application_id=application_id,
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Monitor context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_application_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Application capability.
        
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
            if action == "get_application":
                application_id = capability_data.get("application_id")
                if not application_id:
                    raise ValueError("application_id is required")
                
                result = self.get_application(
                    application_id=application_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_applications":
                filter_criteria = capability_data.get("filter_criteria", {})
                
                result = self.list_applications(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Application capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_deployment_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Deployment capability.
        
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
            if action == "get_deployment_status":
                deployment_id = capability_data.get("deployment_id")
                if not deployment_id:
                    raise ValueError("deployment_id is required")
                
                result = self.get_deployment_status(
                    deployment_id=deployment_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_deployments":
                filter_criteria = capability_data.get("filter_criteria", {})
                
                result = self.list_deployments(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Deployment capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_monitor_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Monitor capability.
        
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
            if action == "get_application_status":
                application_id = capability_data.get("application_id")
                if not application_id:
                    raise ValueError("application_id is required")
                
                result = self.get_application_status(
                    application_id=application_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_application_metrics":
                application_id = capability_data.get("application_id")
                if not application_id:
                    raise ValueError("application_id is required")
                
                metric_names = capability_data.get("metric_names", [])
                
                result = self.get_application_metrics(
                    application_id=application_id,
                    metric_names=metric_names
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Monitor capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_application_created_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle application created event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            application_id = event_data.get("application_id")
            application_data = event_data.get("application_data")
            
            # Validate required fields
            if not application_id:
                self.logger.warning("Received application created event without application_id")
                return
            
            if not application_data:
                self.logger.warning(f"Received application created event for application {application_id} without application_data")
                return
            
            self.logger.info(f"Application {application_id} created")
            
            # Store application data
            self._applications[application_id] = application_data
        except Exception as e:
            self.logger.error(f"Error handling application created event: {str(e)}")
    
    def _handle_application_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle application updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            application_id = event_data.get("application_id")
            application_data = event_data.get("application_data")
            
            # Validate required fields
            if not application_id:
                self.logger.warning("Received application updated event without application_id")
                return
            
            if not application_data:
                self.logger.warning(f"Received application updated event for application {application_id} without application_data")
                return
            
            self.logger.info(f"Application {application_id} updated")
            
            # Update application data
            self._applications[application_id] = application_data
            
            # Update metrics
            self._metrics["total_application_updates"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling application updated event: {str(e)}")
    
    def _handle_deployment_started_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle deployment started event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            deployment_id = event_data.get("deployment_id")
            application_id = event_data.get("application_id")
            deployment_config = event_data.get("deployment_config")
            
            # Validate required fields
            if not deployment_id:
                self.logger.warning("Received deployment started event without deployment_id")
                return
            
            if not application_id:
                self.logger.warning(f"Received deployment started event for deployment {deployment_id} without application_id")
                return
            
            self.logger.info(f"Deployment {deployment_id} started for application {application_id}")
            
            # Store deployment data
            self._deployments[deployment_id] = {
                "application_id": application_id,
                "deployment_config": deployment_config,
                "status": "in_progress",
                "start_time": self.data_access.get_current_timestamp(),
                "end_time": None,
                "result": None
            }
        except Exception as e:
            self.logger.error(f"Error handling deployment started event: {str(e)}")
    
    def _handle_deployment_completed_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle deployment completed event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            deployment_id = event_data.get("deployment_id")
            status = event_data.get("status")
            result = event_data.get("result")
            
            # Validate required fields
            if not deployment_id:
                self.logger.warning("Received deployment completed event without deployment_id")
                return
            
            if not status:
                self.logger.warning(f"Received deployment completed event for deployment {deployment_id} without status")
                return
            
            self.logger.info(f"Deployment {deployment_id} completed with status {status}")
            
            # Update deployment data
            if deployment_id in self._deployments:
                self._deployments[deployment_id]["status"] = status
                self._deployments[deployment_id]["end_time"] = self.data_access.get_current_timestamp()
                self._deployments[deployment_id]["result"] = result
            
            # Update metrics
            self._metrics["total_application_deployments"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling deployment completed event: {str(e)}")
    
    def _handle_status_changed_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle status changed event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            application_id = event_data.get("application_id")
            status = event_data.get("status")
            
            # Validate required fields
            if not application_id:
                self.logger.warning("Received status changed event without application_id")
                return
            
            if not status:
                self.logger.warning(f"Received status changed event for application {application_id} without status")
                return
            
            self.logger.info(f"Application {application_id} status changed to {status}")
            
            # Update monitor data
            self._monitors[application_id] = {
                "status": status,
                "timestamp": self.data_access.get_current_timestamp()
            }
        except Exception as e:
            self.logger.error(f"Error handling status changed event: {str(e)}")
    
    def create_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an application.
        
        Args:
            application_data: Application data
        
        Returns:
            Created application data
        """
        try:
            # Validate application data
            # In a real implementation, this would validate against a schema
            # For now, we'll just check for required fields
            if "name" not in application_data:
                raise ValueError("Application data must have a name field")
            
            if "version" not in application_data:
                raise ValueError("Application data must have a version field")
            
            # Generate application ID
            application_id = f"app-{self.data_access.generate_id()}"
            
            # Add metadata
            application_data["id"] = application_id
            application_data["created_at"] = self.data_access.get_current_timestamp()
            application_data["updated_at"] = self.data_access.get_current_timestamp()
            
            # Store application data
            self._applications[application_id] = application_data
            
            # Publish application created event
            self.event_bus.publish(
                topic="application_layer.application.application_created",
                data={
                    "application_id": application_id,
                    "application_data": application_data
                }
            )
            
            self.logger.info(f"Created application {application_id}")
            
            return {
                "application_id": application_id,
                "application_data": application_data
            }
        except Exception as e:
            self.logger.error(f"Error creating application: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def update_application(self, application_id: str, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an application.
        
        Args:
            application_id: Application ID
            application_data: Application data
        
        Returns:
            Updated application data
        """
        try:
            # Check if application exists
            if application_id not in self._applications:
                raise ValueError(f"Application {application_id} not found")
            
            # Validate application data
            # In a real implementation, this would validate against a schema
            # For now, we'll just check for required fields
            if "name" not in application_data:
                raise ValueError("Application data must have a name field")
            
            if "version" not in application_data:
                raise ValueError("Application data must have a version field")
            
            # Update metadata
            application_data["id"] = application_id
            application_data["created_at"] = self._applications[application_id]["created_at"]
            application_data["updated_at"] = self.data_access.get_current_timestamp()
            
            # Store application data
            self._applications[application_id] = application_data
            
            # Publish application updated event
            self.event_bus.publish(
                topic="application_layer.application.application_updated",
                data={
                    "application_id": application_id,
                    "application_data": application_data
                }
            )
            
            # Update metrics
            self._metrics["total_application_updates"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Updated application {application_id}")
            
            return {
                "application_id": application_id,
                "application_data": application_data
            }
        except Exception as e:
            self.logger.error(f"Error updating application {application_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_application(self, application_id: str) -> Dict[str, Any]:
        """
        Get an application.
        
        Args:
            application_id: Application ID
        
        Returns:
            Application data
        """
        try:
            # Check if application exists
            if application_id not in self._applications:
                raise ValueError(f"Application {application_id} not found")
            
            # Get application data
            application_data = self._applications[application_id]
            
            return application_data
        except Exception as e:
            self.logger.error(f"Error getting application {application_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_applications(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List applications.
        
        Args:
            filter_criteria: Optional filter criteria
        
        Returns:
            List of application data
        """
        try:
            # Apply filters if provided
            if filter_criteria:
                # In a real implementation, this would apply the filter criteria
                # For now, we'll just return all applications
                applications = list(self._applications.values())
            else:
                applications = list(self._applications.values())
            
            return applications
        except Exception as e:
            self.logger.error(f"Error listing applications: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def deploy_application(self, application_id: str, deployment_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Deploy an application.
        
        Args:
            application_id: Application ID
            deployment_config: Optional deployment configuration
        
        Returns:
            Deployment data
        """
        try:
            # Check if application exists
            if application_id not in self._applications:
                raise ValueError(f"Application {application_id} not found")
            
            # Initialize deployment config if not provided
            if deployment_config is None:
                deployment_config = {}
            
            # Generate deployment ID
            deployment_id = f"deploy-{self.data_access.generate_id()}"
            
            # Publish deployment started event
            self.event_bus.publish(
                topic="application_layer.deployment.deployment_started",
                data={
                    "deployment_id": deployment_id,
                    "application_id": application_id,
                    "deployment_config": deployment_config
                }
            )
            
            # In a real implementation, this would start the deployment process
            # For now, we'll just simulate a successful deployment
            
            # Store deployment data
            self._deployments[deployment_id] = {
                "application_id": application_id,
                "deployment_config": deployment_config,
                "status": "in_progress",
                "start_time": self.data_access.get_current_timestamp(),
                "end_time": None,
                "result": None
            }
            
            # Simulate deployment completion
            # In a real implementation, this would be done asynchronously
            # For now, we'll just simulate it
            self._deployments[deployment_id]["status"] = "completed"
            self._deployments[deployment_id]["end_time"] = self.data_access.get_current_timestamp()
            self._deployments[deployment_id]["result"] = {
                "success": True,
                "message": f"Application {application_id} deployed successfully"
            }
            
            # Publish deployment completed event
            self.event_bus.publish(
                topic="application_layer.deployment.deployment_completed",
                data={
                    "deployment_id": deployment_id,
                    "status": "completed",
                    "result": {
                        "success": True,
                        "message": f"Application {application_id} deployed successfully"
                    }
                }
            )
            
            # Update metrics
            self._metrics["total_application_deployments"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Deployed application {application_id} with deployment {deployment_id}")
            
            return {
                "deployment_id": deployment_id,
                "application_id": application_id,
                "status": "completed",
                "result": {
                    "success": True,
                    "message": f"Application {application_id} deployed successfully"
                }
            }
        except Exception as e:
            self.logger.error(f"Error deploying application {application_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get deployment status.
        
        Args:
            deployment_id: Deployment ID
        
        Returns:
            Deployment status data
        """
        try:
            # Check if deployment exists
            if deployment_id not in self._deployments:
                raise ValueError(f"Deployment {deployment_id} not found")
            
            # Get deployment data
            deployment_data = self._deployments[deployment_id]
            
            # Update metrics
            self._metrics["total_application_status_checks"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return deployment_data
        except Exception as e:
            self.logger.error(f"Error getting deployment status for deployment {deployment_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_deployments(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List deployments.
        
        Args:
            filter_criteria: Optional filter criteria
        
        Returns:
            List of deployment data
        """
        try:
            # Apply filters if provided
            if filter_criteria:
                # Extract filter criteria
                application_id = filter_criteria.get("application_id")
                status = filter_criteria.get("status")
                
                # Filter by application ID if provided
                if application_id:
                    deployments = [
                        {
                            "deployment_id": deployment_id,
                            "data": deployment_data
                        }
                        for deployment_id, deployment_data in self._deployments.items()
                        if deployment_data["application_id"] == application_id
                    ]
                else:
                    deployments = [
                        {
                            "deployment_id": deployment_id,
                            "data": deployment_data
                        }
                        for deployment_id, deployment_data in self._deployments.items()
                    ]
                
                # Filter by status if provided
                if status:
                    deployments = [
                        deployment
                        for deployment in deployments
                        if deployment["data"]["status"] == status
                    ]
            else:
                deployments = [
                    {
                        "deployment_id": deployment_id,
                        "data": deployment_data
                    }
                    for deployment_id, deployment_data in self._deployments.items()
                ]
            
            return deployments
        except Exception as e:
            self.logger.error(f"Error listing deployments: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """
        Get application status.
        
        Args:
            application_id: Application ID
        
        Returns:
            Application status data
        """
        try:
            # Check if application exists
            if application_id not in self._applications:
                raise ValueError(f"Application {application_id} not found")
            
            # Get monitor data
            if application_id in self._monitors:
                status_data = self._monitors[application_id]
            else:
                # If no monitor data exists, create it
                status_data = {
                    "status": "unknown",
                    "timestamp": self.data_access.get_current_timestamp()
                }
                self._monitors[application_id] = status_data
            
            # Update metrics
            self._metrics["total_application_status_checks"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return status_data
        except Exception as e:
            self.logger.error(f"Error getting application status for application {application_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_application_metrics(self, application_id: str, metric_names: List[str] = None) -> Dict[str, Any]:
        """
        Get application metrics.
        
        Args:
            application_id: Application ID
            metric_names: Optional list of metric names to retrieve
        
        Returns:
            Application metrics data
        """
        try:
            # Check if application exists
            if application_id not in self._applications:
                raise ValueError(f"Application {application_id} not found")
            
            # Initialize metrics if not provided
            if metric_names is None:
                metric_names = ["cpu", "memory", "requests"]
            
            # In a real implementation, this would retrieve metrics from a monitoring system
            # For now, we'll just return dummy metrics
            metrics_data = {
                "application_id": application_id,
                "timestamp": self.data_access.get_current_timestamp(),
                "metrics": {}
            }
            
            for metric_name in metric_names:
                if metric_name == "cpu":
                    metrics_data["metrics"]["cpu"] = {
                        "value": 0.5,
                        "unit": "cores"
                    }
                elif metric_name == "memory":
                    metrics_data["metrics"]["memory"] = {
                        "value": 1024,
                        "unit": "MB"
                    }
                elif metric_name == "requests":
                    metrics_data["metrics"]["requests"] = {
                        "value": 100,
                        "unit": "requests/sec"
                    }
            
            # Update metrics
            self._metrics["total_application_status_checks"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return metrics_data
        except Exception as e:
            self.logger.error(f"Error getting application metrics for application {application_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_application_logs(self, application_id: str, filter_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get application logs.
        
        Args:
            application_id: Application ID
            filter_criteria: Optional filter criteria
        
        Returns:
            Application logs data
        """
        try:
            # Check if application exists
            if application_id not in self._applications:
                raise ValueError(f"Application {application_id} not found")
            
            # Initialize filter criteria if not provided
            if filter_criteria is None:
                filter_criteria = {}
            
            # In a real implementation, this would retrieve logs from a logging system
            # For now, we'll just return dummy logs
            logs_data = {
                "application_id": application_id,
                "timestamp": self.data_access.get_current_timestamp(),
                "logs": [
                    {
                        "timestamp": self.data_access.get_current_timestamp() - 60,
                        "level": "INFO",
                        "message": f"Application {application_id} started"
                    },
                    {
                        "timestamp": self.data_access.get_current_timestamp() - 30,
                        "level": "INFO",
                        "message": f"Application {application_id} running"
                    },
                    {
                        "timestamp": self.data_access.get_current_timestamp(),
                        "level": "INFO",
                        "message": f"Application {application_id} healthy"
                    }
                ]
            }
            
            # Update metrics
            self._metrics["total_application_status_checks"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return logs_data
        except Exception as e:
            self.logger.error(f"Error getting application logs for application {application_id}: {str(e)}")
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
            "total_application_deployments": 0,
            "total_application_updates": 0,
            "total_application_status_checks": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
