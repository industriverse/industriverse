"""
A2A Protocol Bridge

This module provides a bridge between the Deployment Operations Layer and other agents
using the Agent-to-Agent (A2A) Protocol. It handles communication, agent discovery, and
message exchange between different agents across layers and environments.
"""

import logging
import json
import os
import uuid
from typing import Dict, List, Optional, Any

from .a2a_integration_manager import A2AIntegrationManager
from .a2a_agent_schema import A2AAgentSchema

logger = logging.getLogger(__name__)

class A2AProtocolBridge:
    """
    Bridge for A2A protocol communication between agents.
    """
    
    def __init__(self, 
                 integration_manager: Optional[A2AIntegrationManager] = None,
                 config_path: Optional[str] = None):
        """
        Initialize the A2A Protocol Bridge.
        
        Args:
            integration_manager: A2A Integration Manager
            config_path: Path to bridge configuration file
        """
        self.integration_manager = integration_manager or A2AIntegrationManager()
        self.config_path = config_path or os.environ.get(
            "A2A_BRIDGE_CONFIG_PATH", "/var/lib/industriverse/protocol/a2a_bridge_config.json"
        )
        self.config = self._load_config()
        self.bridge_id = str(uuid.uuid4())
        logger.info("A2A Protocol Bridge initialized with bridge ID: %s", self.bridge_id)
    
    def discover_agents(self, 
                      capabilities: Optional[List[str]] = None,
                      industry_tags: Optional[List[str]] = None,
                      priority: Optional[str] = None) -> Dict[str, Any]:
        """
        Discover agents based on criteria.
        
        Args:
            capabilities: Optional list of required capabilities
            industry_tags: Optional list of industry tags
            priority: Optional priority level
            
        Returns:
            Dict containing the discovered agents
        """
        logger.info(f"Discovering agents with capabilities: {capabilities}")
        
        try:
            # Build filter criteria
            filter_criteria = {}
            
            if capabilities:
                filter_criteria["capabilities"] = capabilities
            
            if industry_tags:
                filter_criteria["industry_tags"] = industry_tags
            
            if priority:
                filter_criteria["priority"] = priority
            
            # List agents with filter criteria
            agents_result = self.integration_manager.list_agents(filter_criteria)
            
            if not agents_result["success"]:
                return {
                    "success": False,
                    "error": agents_result["error"]
                }
            
            # Create agent cards for discovered agents
            agent_cards = []
            for agent in agents_result["agents"]:
                card_result = self.integration_manager.create_agent_card(agent)
                if card_result["success"]:
                    agent_cards.append(card_result["agent_card"])
            
            return {
                "success": True,
                "agents": agent_cards,
                "count": len(agent_cards)
            }
            
        except Exception as e:
            logger.exception(f"Error discovering agents: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_request(self, 
                   source_agent_id: str, 
                   target_agent_id: str,
                   action: str,
                   parameters: Optional[Dict[str, Any]] = None,
                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a request from one agent to another.
        
        Args:
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            action: Action to request
            parameters: Optional parameters for the action
            context: Optional context for the action
            
        Returns:
            Dict containing the request result
        """
        logger.info(f"Sending request from {source_agent_id} to {target_agent_id}: {action}")
        
        try:
            # Create the request message
            message = {
                "id": str(uuid.uuid4()),
                "type": "request",
                "content": {
                    "action": action
                }
            }
            
            # Add parameters if provided
            if parameters:
                message["content"]["parameters"] = parameters
            
            # Add context if provided
            if context:
                message["content"]["context"] = context
            
            # Send the message
            send_result = self.integration_manager.send_message(
                source_agent_id, target_agent_id, message
            )
            
            if not send_result["success"]:
                return {
                    "success": False,
                    "error": send_result["error"]
                }
            
            return {
                "success": True,
                "message_id": send_result["message_id"],
                "source_agent_id": source_agent_id,
                "target_agent_id": target_agent_id,
                "action": action
            }
            
        except Exception as e:
            logger.exception(f"Error sending request: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_response(self, 
                    source_agent_id: str, 
                    target_agent_id: str,
                    request_id: str,
                    status: str,
                    result: Optional[Dict[str, Any]] = None,
                    error: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a response from one agent to another.
        
        Args:
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            request_id: ID of the request being responded to
            status: Status of the response (success, failure, pending)
            result: Optional result data
            error: Optional error information
            
        Returns:
            Dict containing the response result
        """
        logger.info(f"Sending response from {source_agent_id} to {target_agent_id} for request {request_id}: {status}")
        
        try:
            # Create the response message
            message = {
                "id": str(uuid.uuid4()),
                "type": "response",
                "content": {
                    "status": status
                },
                "metadata": {
                    "reply_to": request_id
                }
            }
            
            # Add result if provided
            if result:
                message["content"]["result"] = result
            
            # Add error if provided
            if error and status == "failure":
                message["content"]["error"] = error
            
            # Send the message
            send_result = self.integration_manager.send_message(
                source_agent_id, target_agent_id, message
            )
            
            if not send_result["success"]:
                return {
                    "success": False,
                    "error": send_result["error"]
                }
            
            return {
                "success": True,
                "message_id": send_result["message_id"],
                "source_agent_id": source_agent_id,
                "target_agent_id": target_agent_id,
                "request_id": request_id,
                "status": status
            }
            
        except Exception as e:
            logger.exception(f"Error sending response: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def register_handler(self, 
                       agent_id: str, 
                       action: str,
                       handler_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a handler for an agent action.
        
        Args:
            agent_id: ID of the agent
            action: Action to handle
            handler_config: Handler configuration
            
        Returns:
            Dict containing the registration result
        """
        logger.info(f"Registering handler for agent {agent_id}, action: {action}")
        
        try:
            # Update the bridge configuration
            if "action_handlers" not in self.config:
                self.config["action_handlers"] = {}
            
            if agent_id not in self.config["action_handlers"]:
                self.config["action_handlers"][agent_id] = {}
            
            self.config["action_handlers"][agent_id][action] = handler_config
            
            # Save the configuration
            self._save_config()
            
            return {
                "success": True,
                "agent_id": agent_id,
                "action": action,
                "handler_config": handler_config
            }
            
        except Exception as e:
            logger.exception(f"Error registering handler: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_message(self, 
                     agent_id: str, 
                     message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a message for an agent.
        
        Args:
            agent_id: ID of the agent
            message: Message to handle
            
        Returns:
            Dict containing the handling result
        """
        logger.info(f"Handling message for agent {agent_id}: {message.get('id')}")
        
        try:
            # Validate the message
            validation_result = A2AAgentSchema.validate_message(message)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Process the message based on its type
            message_type = message.get("type")
            
            if message_type == "request":
                return self._handle_request(agent_id, message)
            elif message_type == "response":
                return self._handle_response(agent_id, message)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {message_type}"
                }
            
        except Exception as e:
            logger.exception(f"Error handling message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load bridge configuration from file.
        
        Returns:
            Dict containing bridge configuration
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Bridge configuration file not found: {self.config_path}")
                return self._get_default_config()
                
        except Exception as e:
            logger.exception(f"Error loading bridge configuration: {str(e)}")
            return self._get_default_config()
    
    def _save_config(self):
        """
        Save bridge configuration to file.
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                
        except Exception as e:
            logger.exception(f"Error saving bridge configuration: {str(e)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default bridge configuration.
        
        Returns:
            Dict containing default bridge configuration
        """
        return {
            "bridge_version": "1.0",
            "action_handlers": {},
            "message_handlers": {
                "request": {
                    "default": {
                        "type": "echo",
                        "timeout": 30
                    }
                },
                "response": {
                    "default": {
                        "type": "log",
                        "level": "info"
                    }
                }
            },
            "discovery": {
                "cache_ttl": 300,  # 5 minutes
                "refresh_interval": 60  # 1 minute
            }
        }
    
    def _handle_request(self, 
                      agent_id: str, 
                      message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request message for an agent.
        
        Args:
            agent_id: ID of the agent
            message: Request message to handle
            
        Returns:
            Dict containing the handling result
        """
        # Get the action from the message
        action = message["content"].get("action")
        
        # Check if there's a handler for this action
        handler_config = None
        if "action_handlers" in self.config and agent_id in self.config["action_handlers"] and action in self.config["action_handlers"][agent_id]:
            handler_config = self.config["action_handlers"][agent_id][action]
        elif "message_handlers" in self.config and "request" in self.config["message_handlers"] and "default" in self.config["message_handlers"]["request"]:
            handler_config = self.config["message_handlers"]["request"]["default"]
        
        if not handler_config:
            return {
                "success": False,
                "error": f"No handler found for agent {agent_id}, action {action}"
            }
        
        # In a real implementation, this would invoke the handler
        # For this implementation, we'll just return a simulated result
        return {
            "success": True,
            "message_id": message["id"],
            "agent_id": agent_id,
            "action": action,
            "handled": True
        }
    
    def _handle_response(self, 
                       agent_id: str, 
                       message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a response message for an agent.
        
        Args:
            agent_id: ID of the agent
            message: Response message to handle
            
        Returns:
            Dict containing the handling result
        """
        # Get the request ID from the message
        request_id = message["metadata"].get("reply_to")
        
        # Check if there's a handler for responses
        handler_config = None
        if "message_handlers" in self.config and "response" in self.config["message_handlers"] and "default" in self.config["message_handlers"]["response"]:
            handler_config = self.config["message_handlers"]["response"]["default"]
        
        if not handler_config:
            return {
                "success": False,
                "error": f"No handler found for agent {agent_id}, response to {request_id}"
            }
        
        # In a real implementation, this would invoke the handler
        # For this implementation, we'll just return a simulated result
        return {
            "success": True,
            "message_id": message["id"],
            "agent_id": agent_id,
            "request_id": request_id,
            "handled": True
        }
