"""
API Client for Web Frontend

This module provides a client for the web frontend to interact with the
Industriverse backend layers, primarily through the Agent Interaction Protocol.

It abstracts the communication details and provides convenient methods for
making requests, sending commands, and subscribing to events.

The API Client:
1. Connects to the backend via the Agent Interaction Protocol
2. Sends requests and handles responses (sync and async)
3. Sends commands and notifications
4. Subscribes to backend events and state updates
5. Manages authentication tokens for requests

Author: Manus
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, List

# Local imports
from ..core.agent_ecosystem.agent_interaction_protocol import AgentInteractionProtocol, MessageType
from .auth import AuthManager

# Configure logging
logger = logging.getLogger(__name__)

class APIClient:
    """
    API Client for the web frontend to interact with the backend.
    """
    
    def __init__(
        self,
        agent_protocol: AgentInteractionProtocol,
        auth_manager: AuthManager,
        config: Dict = None
    ):
        """
        Initialize the API Client.
        
        Args:
            agent_protocol: Agent Interaction Protocol instance
            auth_manager: Authentication Manager instance
            config: Optional configuration dictionary
        """
        self.agent_protocol = agent_protocol
        self.auth_manager = auth_manager
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "default_timeout": 30.0,  # seconds
            "log_requests": True
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        logger.info("API Client initialized")
    
    def _merge_config(self) -> None:
        """Merge provided configuration with defaults."""
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                # Merge nested dictionaries
                for nested_key, nested_value in value.items():
                    if nested_key not in self.config[key]:
                        self.config[key][nested_key] = nested_value
    
    def _get_default_target(self, target_type: str = "agent", target_id: str = "default_agent") -> Dict:
        """
        Get default target information.
        
        Args:
            target_type: Type of target (agent, model, system)
            target_id: ID of the target
            
        Returns:
            Target dictionary
        """
        # In a real application, this might involve discovery or configuration
        return {
            "type": target_type,
            "id": target_id,
            "protocol": "a2a" if target_type == "agent" else "mcp" if target_type == "model" else "a2a"
        }
    
    def _add_auth_to_payload(self, payload: Dict) -> Dict:
        """
        Add authentication information to the payload if available.
        
        Args:
            payload: Original payload
            
        Returns:
            Payload with authentication info
        """
        token = self.auth_manager.get_access_token()
        user_info = self.auth_manager.get_current_user_info()
        
        auth_info = {}
        if token:
            auth_info["token"] = token
        if user_info:
            auth_info["user_id"] = user_info.get("id")
            auth_info["roles"] = user_info.get("roles")
            
        if auth_info:
            # Add auth info under a specific key, e.g., __auth__
            payload["__auth__"] = auth_info
            
        return payload
    
    async def make_request_async(
        self,
        request_type: str,
        data: Dict,
        target: Optional[Dict] = None,
        timeout: Optional[float] = None
    ) -> Dict:
        """
        Make an asynchronous request to the backend.
        
        Args:
            request_type: Type identifier for the request
            data: Request data payload
            target: Optional target information (defaults to default agent)
            timeout: Optional timeout in seconds
            
        Returns:
            Response dictionary from the backend
        """
        if not self.agent_protocol.is_connected():
            logger.error("Cannot make request: Not connected to backend")
            return {"error": True, "error_message": "Not connected"}
        
        target = target or self._get_default_target()
        request_payload = {
            "request_type": request_type,
            "data": data
        }
        
        # Add authentication info
        request_payload = self._add_auth_to_payload(request_payload)
        
        if self.config["log_requests"]:
            logger.info(f"Sending async request: type={request_type}, target={target["id"]}")
            
        try:
            response = await self.agent_protocol.send_request_async(
                request_payload,
                target,
                timeout=timeout or self.config["default_timeout"]
            )
            
            if self.config["log_requests"]:
                log_response = response.get("payload", response)
                logger.info(f"Received response for {request_type}: {log_response}")
                
            return response.get("payload", response) # Return payload or full message on error
        except Exception as e:
            logger.error(f"Error during async request {request_type}: {str(e)}")
            return {"error": True, "error_message": str(e)}
    
    def make_request_sync(
        self,
        request_type: str,
        data: Dict,
        target: Optional[Dict] = None,
        timeout: Optional[float] = None
    ) -> Dict:
        """
        Make a synchronous request to the backend.
        
        Args:
            request_type: Type identifier for the request
            data: Request data payload
            target: Optional target information (defaults to default agent)
            timeout: Optional timeout in seconds
            
        Returns:
            Response dictionary from the backend
        """
        if not self.agent_protocol.is_connected():
            logger.error("Cannot make request: Not connected to backend")
            return {"error": True, "error_message": "Not connected"}
        
        target = target or self._get_default_target()
        request_payload = {
            "request_type": request_type,
            "data": data
        }
        
        # Add authentication info
        request_payload = self._add_auth_to_payload(request_payload)
        
        if self.config["log_requests"]:
            logger.info(f"Sending sync request: type={request_type}, target={target["id"]}")
            
        try:
            response = self.agent_protocol.send_request_sync(
                request_payload,
                target,
                timeout=timeout or self.config["default_timeout"]
            )
            
            if self.config["log_requests"]:
                log_response = response.get("payload", response)
                logger.info(f"Received response for {request_type}: {log_response}")
                
            return response.get("payload", response) # Return payload or full message on error
        except Exception as e:
            logger.error(f"Error during sync request {request_type}: {str(e)}")
            return {"error": True, "error_message": str(e)}
    
    def send_command(
        self,
        command_type: str,
        data: Dict,
        target: Optional[Dict] = None
    ) -> bool:
        """
        Send a command to the backend.
        
        Args:
            command_type: Type identifier for the command
            data: Command data payload
            target: Optional target information (defaults to default agent)
            
        Returns:
            Boolean indicating if the command was sent successfully
        """
        if not self.agent_protocol.is_connected():
            logger.error("Cannot send command: Not connected to backend")
            return False
        
        target = target or self._get_default_target()
        command_payload = {
            "command_type": command_type,
            "data": data
        }
        
        # Add authentication info
        command_payload = self._add_auth_to_payload(command_payload)
        
        if self.config["log_requests"]:
            logger.info(f"Sending command: type={command_type}, target={target["id"]}")
            
        try:
            message_id = self.agent_protocol.send_command(
                command_payload,
                target
            )
            return bool(message_id)
        except Exception as e:
            logger.error(f"Error sending command {command_type}: {str(e)}")
            return False
    
    def send_notification(
        self,
        notification_type: str,
        data: Dict,
        target: Optional[Dict] = None
    ) -> bool:
        """
        Send a notification to the backend.
        
        Args:
            notification_type: Type identifier for the notification
            data: Notification data payload
            target: Optional target information (defaults to default agent)
            
        Returns:
            Boolean indicating if the notification was sent successfully
        """
        if not self.agent_protocol.is_connected():
            logger.error("Cannot send notification: Not connected to backend")
            return False
        
        target = target or self._get_default_target()
        notification_payload = {
            "notification_type": notification_type,
            "data": data
        }
        
        # Add authentication info
        notification_payload = self._add_auth_to_payload(notification_payload)
        
        if self.config["log_requests"]:
            logger.info(f"Sending notification: type={notification_type}, target={target["id"]}")
            
        try:
            message_id = self.agent_protocol.send_notification(
                notification_payload,
                target
            )
            return bool(message_id)
        except Exception as e:
            logger.error(f"Error sending notification {notification_type}: {str(e)}")
            return False
    
    def subscribe_to_event(
        self,
        event_type: str,
        callback: Callable[[Dict], None],
        source_id: str = "*"
    ) -> None:
        """
        Subscribe to a specific type of event from the backend.
        
        Args:
            event_type: Event type identifier to subscribe to
            callback: Function to call when the event is received
            source_id: Optional source ID to filter events from
        """
        
        def event_handler(message: Dict) -> None:
            payload = message.get("payload", {})
            message_event_type = payload.get("event_type")
            message_source_id = message.get("source", {}).get("id")
            
            # Check if event type matches
            if message_event_type == event_type:
                # Check if source ID matches (if specified)
                if source_id == "*" or message_source_id == source_id:
                    # Call the user-provided callback
                    try:
                        callback(payload.get("data", {}))
                    except Exception as e:
                        logger.error(f"Error in event callback for {event_type}: {str(e)}")
        
        # Register the handler with the agent protocol
        # We register a wildcard handler and filter internally
        self.agent_protocol.register_message_handler(
            MessageType.EVENT.value,
            event_handler,
            message_id="*" # Handle all events
        )
        
        logger.info(f"Subscribed to event type 	'{event_type}" from source 	'{source_id}"")
        
        # Optionally, send a subscription request to the backend if needed
        # self.send_command("subscribe_event", {"event_type": event_type, "source_id": source_id})
    
    def subscribe_to_state_update(
        self,
        source_id: str,
        callback: Callable[[Dict], None]
    ) -> None:
        """
        Subscribe to state updates from a specific source.
        
        Args:
            source_id: Source ID to subscribe to
            callback: Function to call when a state update is received
        """
        
        def state_update_handler(message: Dict) -> None:
            message_source_id = message.get("source", {}).get("id")
            
            # Check if source ID matches
            if message_source_id == source_id:
                # Call the user-provided callback
                try:
                    callback(message.get("payload", {}))
                except Exception as e:
                    logger.error(f"Error in state update callback for {source_id}: {str(e)}")
        
        # Register the handler with the agent protocol
        self.agent_protocol.register_message_handler(
            MessageType.STATE_UPDATE.value,
            state_update_handler,
            message_id="*" # Handle all state updates
        )
        
        logger.info(f"Subscribed to state updates from source 	'{source_id}"")
        
        # Optionally, send a subscription request to the backend if needed
        # self.send_command("subscribe_state", {"source_id": source_id})
    
    def get_cached_state(self, source_id: str) -> Optional[Dict]:
        """
        Get cached state for a source.
        
        Args:
            source_id: Source identifier
            
        Returns:
            Cached state or None if not found or expired
        """
        return self.agent_protocol.get_cached_state(source_id)
    
    def is_connected(self) -> bool:
        """
        Check if the client is connected to the backend.
        
        Returns:
            Boolean indicating connection status
        """
        return self.agent_protocol.is_connected()

# Example Usage (within a Flask route or similar):
# from flask import current_app
# 
# @app.route("/get_data")
# @auth_manager.login_required()
# async def get_data():
#     api_client = current_app.api_client # Assuming client is stored in app context
#     response = await api_client.make_request_async("get_dashboard_data", {})
#     return jsonify(response)
# 
# @app.route("/start_workflow", methods=["POST"])
# @auth_manager.login_required()
# def start_workflow():
#     api_client = current_app.api_client
#     workflow_id = request.json.get("workflow_id")
#     success = api_client.send_command("start_workflow", {"id": workflow_id})
#     return jsonify({"success": success})

