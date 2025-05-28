"""
Cross-Layer Integration Module for the Workflow Automation Layer.

This module provides integration between the Workflow Automation Layer
and the Protocol Layer, enabling seamless communication and coordination.
"""

import requests
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolLayerIntegration:
    """Integration with the Protocol Layer."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Protocol Layer integration.

        Args:
            config: Configuration dictionary with protocol layer settings.
        """
        self.protocol_layer_url = config.get("protocol_layer_url", "http://protocol-layer-service:8080")
        self.api_key = config.get("api_key")
        self.workflow_runtime = None
        self.message_handlers = {}
        self.connection_status = "disconnected"
        self.retry_count = 0
        self.max_retries = config.get("max_retries", 5)
        self.retry_delay = config.get("retry_delay_seconds", 5)

    def register_workflow_runtime(self, workflow_runtime):
        """Register the workflow runtime for callbacks.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime

    def register_message_handler(self, message_type: str, handler_func):
        """Register a handler for a specific message type.

        Args:
            message_type: Type of message to handle.
            handler_func: Function to call when message is received.
        """
        self.message_handlers[message_type] = handler_func
        logger.info(f"Registered handler for message type: {message_type}")

    async def connect(self) -> Dict[str, Any]:
        """Establish connection with the Protocol Layer.

        Returns:
            Dict containing connection status and details.
        """
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.protocol_layer_url}/api/connections",
                headers=headers,
                json={
                    "client_type": "workflow_automation_layer",
                    "capabilities": ["workflow_execution", "task_management", "agent_coordination"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.connection_id = data.get("connection_id")
                self.connection_status = "connected"
                self.retry_count = 0
                logger.info(f"Connected to Protocol Layer with connection ID: {self.connection_id}")
                return {
                    "success": True,
                    "connection_id": self.connection_id,
                    "status": self.connection_status
                }
            else:
                logger.error(f"Failed to connect to Protocol Layer: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Connection failed with status code {response.status_code}",
                    "status": self.connection_status
                }
        except Exception as e:
            logger.error(f"Error connecting to Protocol Layer: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status": self.connection_status
            }

    async def reconnect(self) -> Dict[str, Any]:
        """Attempt to reconnect to the Protocol Layer.

        Returns:
            Dict containing reconnection status and details.
        """
        if self.retry_count >= self.max_retries:
            logger.error(f"Maximum retry count ({self.max_retries}) reached. Giving up reconnection attempts.")
            return {
                "success": False,
                "error": "Maximum retry count reached",
                "status": self.connection_status
            }
        
        self.retry_count += 1
        logger.info(f"Attempting to reconnect to Protocol Layer (attempt {self.retry_count}/{self.max_retries})")
        
        await asyncio.sleep(self.retry_delay)
        return await self.connect()

    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the Protocol Layer.

        Args:
            message: Message to send.

        Returns:
            Dict containing send status and details.
        """
        if self.connection_status != "connected":
            logger.warning("Not connected to Protocol Layer. Attempting to connect...")
            connect_result = await self.connect()
            if not connect_result["success"]:
                return {
                    "success": False,
                    "error": "Not connected to Protocol Layer",
                    "status": self.connection_status
                }
        
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.protocol_layer_url}/api/messages",
                headers=headers,
                json={
                    "connection_id": self.connection_id,
                    **message
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Message sent successfully: {data.get('message_id')}")
                return {
                    "success": True,
                    "message_id": data.get("message_id")
                }
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                if response.status_code == 401:
                    self.connection_status = "disconnected"
                    logger.info("Connection invalidated. Will reconnect on next attempt.")
                
                return {
                    "success": False,
                    "error": f"Failed to send message with status code {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error sending message to Protocol Layer: {str(e)}")
            self.connection_status = "disconnected"
            return {
                "success": False,
                "error": str(e)
            }

    async def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a message received from the Protocol Layer.

        Args:
            message: Received message.

        Returns:
            Dict containing handling status and details.
        """
        try:
            message_type = message.get("message_type")
            logger.info(f"Received message of type: {message_type}")
            
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                result = await handler(message)
                return {
                    "success": True,
                    "message_id": message.get("message_id"),
                    "handled_by": message_type,
                    "result": result
                }
            elif self.workflow_runtime:
                # Default to workflow runtime handler
                result = await self.workflow_runtime.handle_protocol_message(message)
                return {
                    "success": True,
                    "message_id": message.get("message_id"),
                    "handled_by": "workflow_runtime",
                    "result": result
                }
            else:
                logger.warning(f"No handler registered for message type: {message_type}")
                return {
                    "success": False,
                    "error": f"No handler registered for message type: {message_type}",
                    "message_id": message.get("message_id")
                }
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": message.get("message_id")
            }

    async def register_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a workflow with the Protocol Layer.

        Args:
            workflow_data: Workflow definition data.

        Returns:
            Dict containing registration status and details.
        """
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.protocol_layer_url}/api/workflows",
                headers=headers,
                json=workflow_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Workflow registered successfully: {data.get('workflow_id')}")
                return {
                    "success": True,
                    "workflow_id": data.get("workflow_id")
                }
            else:
                logger.error(f"Failed to register workflow: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Failed to register workflow with status code {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error registering workflow with Protocol Layer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def update_workflow_status(self, workflow_id: str, status: Dict[str, Any]) -> Dict[str, Any]:
        """Update workflow status in the Protocol Layer.

        Args:
            workflow_id: ID of the workflow to update.
            status: Status information to update.

        Returns:
            Dict containing update status and details.
        """
        try:
            headers = self._get_headers()
            response = requests.put(
                f"{self.protocol_layer_url}/api/workflows/{workflow_id}/status",
                headers=headers,
                json=status,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Workflow status updated successfully: {workflow_id}")
                return {
                    "success": True,
                    "workflow_id": workflow_id
                }
            else:
                logger.error(f"Failed to update workflow status: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Failed to update workflow status with status code {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error updating workflow status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_protocol_layer_status(self) -> Dict[str, Any]:
        """Get the status of the Protocol Layer.

        Returns:
            Dict containing Protocol Layer status information.
        """
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.protocol_layer_url}/api/status",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Retrieved Protocol Layer status successfully")
                return {
                    "success": True,
                    "status": data.get("status"),
                    "version": data.get("version"),
                    "uptime_seconds": data.get("uptime_seconds"),
                    "active_connections": data.get("active_connections")
                }
            else:
                logger.error(f"Failed to get Protocol Layer status: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Failed to get status with status code {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error getting Protocol Layer status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def start_message_listener(self):
        """Start listening for messages from the Protocol Layer.

        This method establishes a long-polling connection to receive messages.
        """
        logger.info("Starting message listener...")
        
        while True:
            if self.connection_status != "connected":
                logger.warning("Not connected to Protocol Layer. Attempting to connect...")
                connect_result = await self.connect()
                if not connect_result["success"]:
                    logger.error("Failed to connect. Retrying...")
                    await asyncio.sleep(self.retry_delay)
                    continue
            
            try:
                headers = self._get_headers()
                response = requests.get(
                    f"{self.protocol_layer_url}/api/messages",
                    headers=headers,
                    params={"connection_id": self.connection_id, "timeout": 30},
                    timeout=35  # Slightly longer than the long-polling timeout
                )
                
                if response.status_code == 200:
                    messages = response.json().get("messages", [])
                    for message in messages:
                        # Process each message asynchronously
                        asyncio.create_task(self.receive_message(message))
                elif response.status_code == 204:
                    # No messages, continue polling
                    pass
                else:
                    logger.error(f"Error in message listener: {response.status_code} - {response.text}")
                    self.connection_status = "disconnected"
                    await asyncio.sleep(self.retry_delay)
            except requests.exceptions.Timeout:
                # This is expected with long polling when no messages are available
                logger.debug("Long polling timeout, continuing...")
            except Exception as e:
                logger.error(f"Error in message listener: {str(e)}")
                self.connection_status = "disconnected"
                await asyncio.sleep(self.retry_delay)

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests.

        Returns:
            Dict containing request headers.
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        if hasattr(self, 'connection_id') and self.connection_id:
            headers["X-Connection-ID"] = self.connection_id
        
        return headers


class CoreAILayerIntegration:
    """Integration with the Core AI Layer."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Core AI Layer integration.

        Args:
            config: Configuration dictionary with Core AI layer settings.
        """
        self.core_ai_url = config.get("core_ai_url", "http://core-ai-layer-service:8080")
        self.api_key = config.get("api_key")

    async def get_prediction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a prediction from the Core AI Layer.

        Args:
            data: Input data for prediction.

        Returns:
            Dict containing prediction results.
        """
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.core_ai_url}/api/predict",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Prediction successful")
                return {
                    "success": True,
                    "prediction": result.get("prediction"),
                    "confidence": result.get("confidence"),
                    "model_id": result.get("model_id")
                }
            else:
                logger.error(f"Prediction failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Prediction failed with status code {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error getting prediction from Core AI Layer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_semantic_embedding(self, text: str) -> Dict[str, Any]:
        """Get semantic embedding for text from the Core AI Layer.

        Args:
            text: Input text to embed.

        Returns:
            Dict containing embedding results.
        """
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.core_ai_url}/api/embed",
                headers=headers,
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Embedding successful")
                return {
                    "success": True,
                    "embedding": result.get("embedding"),
                    "dimensions": result.get("dimensions")
                }
            else:
                logger.error(f"Embedding failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Embedding failed with status code {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error getting embedding from Core AI Layer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests.

        Returns:
            Dict containing request headers.
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        return headers


class ApplicationLayerIntegration:
    """Integration with the Application Layer."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Application Layer integration.

        Args:
            config: Configuration dictionary with Application layer settings.
        """
        self.application_url = config.get("application_url", "http://application-layer-service:8080")
        self.api_key = config.get("api_key")

    async def notify_application(self, app_id: str, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Send a notification to an application.

        Args:
            app_id: ID of the application to notify.
            notification: Notification data.

        Returns:
            Dict containing notification status.
        """
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.application_url}/api/applications/{app_id}/notifications",
                headers=headers,
                json=notification,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Notification sent to application {app_id}")
                return {
                    "success": True,
                    "notification_id": result.get("notification_id")
                }
            else:
                logger.error(f"Notification failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Notification failed with status code {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error sending notification to Application Layer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_application_context(self, app_id: str) -> Dict[str, Any]:
        """Get context information from an application.

        Args:
            app_id: ID of the application.

        Returns:
            Dict containing application context.
        """
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.application_url}/api/applications/{app_id}/context",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                context = response.json()
                logger.info(f"Retrieved context for application {app_id}")
                return {
                    "success": True,
                    "context": context
                }
            else:
                logger.error(f"Context retrieval failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Context retrieval failed with status code {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error getting application context: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests.

        Returns:
            Dict containing request headers.
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        return headers


class CrossLayerIntegrationManager:
    """Manager for cross-layer integrations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the cross-layer integration manager.

        Args:
            config: Configuration dictionary with integration settings.
        """
        self.protocol_layer = ProtocolLayerIntegration(config.get("protocol_layer", {}))
        self.core_ai_layer = CoreAILayerIntegration(config.get("core_ai_layer", {}))
        self.application_layer = ApplicationLayerIntegration(config.get("application_layer", {}))
        self.workflow_runtime = None

    def register_workflow_runtime(self, workflow_runtime):
        """Register the workflow runtime for callbacks.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.protocol_layer.register_workflow_runtime(workflow_runtime)

    async def initialize(self) -> Dict[str, Any]:
        """Initialize all layer integrations.

        Returns:
            Dict containing initialization status.
        """
        protocol_result = await self.protocol_layer.connect()
        
        if protocol_result["success"]:
            # Start the message listener in the background
            asyncio.create_task(self.protocol_layer.start_message_listener())
        
        return {
            "success": protocol_result["success"],
            "protocol_layer": protocol_result,
            "status": "initialized" if protocol_result["success"] else "initialization_failed"
        }

    async def register_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a workflow across all relevant layers.

        Args:
            workflow_data: Workflow definition data.

        Returns:
            Dict containing registration status.
        """
        # Register with Protocol Layer first
        protocol_result = await self.protocol_layer.register_workflow(workflow_data)
        
        if not protocol_result["success"]:
            return protocol_result
        
        # Additional registrations with other layers could be added here
        
        return protocol_result

    async def update_workflow_status(self, workflow_id: str, status: Dict[str, Any]) -> Dict[str, Any]:
        """Update workflow status across all relevant layers.

        Args:
            workflow_id: ID of the workflow to update.
            status: Status information to update.

        Returns:
            Dict containing update status.
        """
        # Update in Protocol Layer
        protocol_result = await self.protocol_layer.update_workflow_status(workflow_id, status)
        
        # Notify relevant applications if needed
        if status.get("status") in ["completed", "failed", "aborted"]:
            app_ids = status.get("related_applications", [])
            for app_id in app_ids:
                await self.application_layer.notify_application(app_id, {
                    "type": "workflow_status_change",
                    "workflow_id": workflow_id,
                    "status": status.get("status"),
                    "timestamp": status.get("timestamp")
                })
        
        return protocol_result

    async def get_prediction_for_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a prediction from the Core AI Layer for a workflow.

        Args:
            workflow_id: ID of the workflow.
            data: Input data for prediction.

        Returns:
            Dict containing prediction results.
        """
        # Add workflow context to the prediction request
        data["context"] = {
            "workflow_id": workflow_id,
            "source": "workflow_automation_layer"
        }
        
        return await self.core_ai_layer.get_prediction(data)

    async def check_system_health(self) -> Dict[str, Any]:
        """Check the health of all integrated layers.

        Returns:
            Dict containing health status of all layers.
        """
        protocol_status = await self.protocol_layer.get_protocol_layer_status()
        
        # Additional health checks for other layers could be added here
        
        return {
            "success": protocol_status["success"],
            "protocol_layer": {
                "status": protocol_status.get("status"),
                "version": protocol_status.get("version"),
                "uptime_seconds": protocol_status.get("uptime_seconds")
            },
            "core_ai_layer": {
                "status": "unknown"  # Would be populated with actual status
            },
            "application_layer": {
                "status": "unknown"  # Would be populated with actual status
            },
            "overall_status": "healthy" if protocol_status["success"] and protocol_status.get("status") == "healthy" else "degraded"
        }
