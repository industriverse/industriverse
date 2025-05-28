"""
Protocol Bridge for the Deployment Operations Layer.

This module provides protocol bridge capabilities for standardized communication
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProtocolBridge:
    """
    Protocol Bridge for standardized communication.
    
    This class provides methods for bridging between different protocols,
    including MCP (Model Context Protocol) and A2A (Agent-to-Agent Protocol).
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Protocol Bridge.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.bridge_id = config.get("bridge_id", f"bridge-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9008")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize protocol configurations
        self.mcp_config = config.get("mcp", {})
        self.a2a_config = config.get("a2a", {})
        self.custom_protocols = config.get("custom_protocols", {})
        
        # Initialize protocol handlers
        self.protocol_handlers = {
            "mcp": self._handle_mcp,
            "a2a": self._handle_a2a
        }
        
        # Add custom protocol handlers
        for protocol_name in self.custom_protocols:
            self.protocol_handlers[protocol_name] = self._handle_custom_protocol
        
        # Initialize protocol version mappings
        self.protocol_versions = {
            "mcp": self.mcp_config.get("version", "1.0.0"),
            "a2a": self.a2a_config.get("version", "1.0.0")
        }
        
        # Add custom protocol versions
        for protocol_name, protocol_config in self.custom_protocols.items():
            self.protocol_versions[protocol_name] = protocol_config.get("version", "1.0.0")
        
        # Initialize protocol schemas
        self.protocol_schemas = {}
        self._load_protocol_schemas()
        
        # Initialize protocol metrics
        self.protocol_metrics = {
            "mcp": {"sent": 0, "received": 0, "errors": 0},
            "a2a": {"sent": 0, "received": 0, "errors": 0}
        }
        
        # Add custom protocol metrics
        for protocol_name in self.custom_protocols:
            self.protocol_metrics[protocol_name] = {"sent": 0, "received": 0, "errors": 0}
        
        # Initialize analytics manager for protocol tracking
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        logger.info(f"Protocol Bridge {self.bridge_id} initialized")
    
    def send_message(self, message: Dict, source_protocol: str, target_protocol: str) -> Dict:
        """
        Send a message from one protocol to another.
        
        Args:
            message: Message to send
            source_protocol: Source protocol
            target_protocol: Target protocol
            
        Returns:
            Dict: Message sending results
        """
        try:
            # Validate protocols
            if source_protocol not in self.protocol_handlers:
                return {
                    "status": "error",
                    "message": f"Unknown source protocol: {source_protocol}"
                }
            
            if target_protocol not in self.protocol_handlers:
                return {
                    "status": "error",
                    "message": f"Unknown target protocol: {target_protocol}"
                }
            
            # Validate message against source protocol schema
            validation_result = self._validate_message(message, source_protocol)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Transform message from source to target protocol
            transformed_message = self._transform_message(message, source_protocol, target_protocol)
            
            # Send message using target protocol handler
            send_result = self.protocol_handlers[target_protocol](transformed_message, "send")
            
            # Update metrics
            self.protocol_metrics[target_protocol]["sent"] += 1
            if send_result.get("status") != "success":
                self.protocol_metrics[target_protocol]["errors"] += 1
            
            # Track message sending
            self._track_protocol_event("send", target_protocol, send_result)
            
            return send_result
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"status": "error", "message": str(e)}
    
    def receive_message(self, message: Dict, source_protocol: str) -> Dict:
        """
        Receive a message from a protocol.
        
        Args:
            message: Message to receive
            source_protocol: Source protocol
            
        Returns:
            Dict: Message receiving results
        """
        try:
            # Validate protocol
            if source_protocol not in self.protocol_handlers:
                return {
                    "status": "error",
                    "message": f"Unknown source protocol: {source_protocol}"
                }
            
            # Validate message against source protocol schema
            validation_result = self._validate_message(message, source_protocol)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Receive message using source protocol handler
            receive_result = self.protocol_handlers[source_protocol](message, "receive")
            
            # Update metrics
            self.protocol_metrics[source_protocol]["received"] += 1
            if receive_result.get("status") != "success":
                self.protocol_metrics[source_protocol]["errors"] += 1
            
            # Track message receiving
            self._track_protocol_event("receive", source_protocol, receive_result)
            
            return receive_result
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_protocol_info(self, protocol_name: str) -> Dict:
        """
        Get information about a protocol.
        
        Args:
            protocol_name: Protocol name
            
        Returns:
            Dict: Protocol information
        """
        try:
            # Check if protocol exists
            if protocol_name not in self.protocol_handlers:
                return {
                    "status": "error",
                    "message": f"Unknown protocol: {protocol_name}"
                }
            
            # Get protocol version
            version = self.protocol_versions.get(protocol_name, "unknown")
            
            # Get protocol metrics
            metrics = self.protocol_metrics.get(protocol_name, {})
            
            # Get protocol schema
            schema = self.protocol_schemas.get(protocol_name, {})
            
            return {
                "status": "success",
                "protocol": protocol_name,
                "version": version,
                "metrics": metrics,
                "schema": schema
            }
        except Exception as e:
            logger.error(f"Error getting protocol info: {e}")
            return {"status": "error", "message": str(e)}
    
    def list_protocols(self) -> Dict:
        """
        List all available protocols.
        
        Returns:
            Dict: Protocol listing
        """
        try:
            protocols = []
            
            for protocol_name in self.protocol_handlers:
                protocols.append({
                    "name": protocol_name,
                    "version": self.protocol_versions.get(protocol_name, "unknown"),
                    "metrics": self.protocol_metrics.get(protocol_name, {})
                })
            
            return {
                "status": "success",
                "protocols": protocols
            }
        except Exception as e:
            logger.error(f"Error listing protocols: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_mcp(self, message: Dict, action: str) -> Dict:
        """
        Handle MCP protocol messages.
        
        Args:
            message: Message to handle
            action: Action to perform (send or receive)
            
        Returns:
            Dict: Handling results
        """
        try:
            # Get MCP configuration
            mcp_endpoint = self.mcp_config.get("endpoint", "http://localhost:9009")
            mcp_auth_token = self.mcp_config.get("auth_token", "")
            
            if action == "send":
                # Add MCP headers
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {mcp_auth_token}",
                    "X-MCP-Version": self.protocol_versions["mcp"]
                }
                
                # Send message to MCP endpoint
                response = requests.post(
                    f"{mcp_endpoint}/message",
                    headers=headers,
                    json=message,
                    timeout=self.timeout
                )
                
                # Check response
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "message": "Message sent successfully",
                        "protocol": "mcp",
                        "response": response.json()
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Error sending message: {response.text}",
                        "protocol": "mcp",
                        "status_code": response.status_code
                    }
            elif action == "receive":
                # Process received MCP message
                return {
                    "status": "success",
                    "message": "Message received successfully",
                    "protocol": "mcp",
                    "data": message
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "protocol": "mcp"
                }
        except Exception as e:
            logger.error(f"Error handling MCP message: {e}")
            return {"status": "error", "message": str(e), "protocol": "mcp"}
    
    def _handle_a2a(self, message: Dict, action: str) -> Dict:
        """
        Handle A2A protocol messages.
        
        Args:
            message: Message to handle
            action: Action to perform (send or receive)
            
        Returns:
            Dict: Handling results
        """
        try:
            # Get A2A configuration
            a2a_endpoint = self.a2a_config.get("endpoint", "http://localhost:9010")
            a2a_auth_token = self.a2a_config.get("auth_token", "")
            
            if action == "send":
                # Add A2A headers
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {a2a_auth_token}",
                    "X-A2A-Version": self.protocol_versions["a2a"]
                }
                
                # Add industry-specific metadata
                if "industryTags" not in message and "industryTags" in self.a2a_config:
                    message["industryTags"] = self.a2a_config["industryTags"]
                
                # Add task prioritization
                if "priority" not in message and "priority" in self.a2a_config:
                    message["priority"] = self.a2a_config["priority"]
                
                # Send message to A2A endpoint
                response = requests.post(
                    f"{a2a_endpoint}/agent/message",
                    headers=headers,
                    json=message,
                    timeout=self.timeout
                )
                
                # Check response
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "message": "Message sent successfully",
                        "protocol": "a2a",
                        "response": response.json()
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Error sending message: {response.text}",
                        "protocol": "a2a",
                        "status_code": response.status_code
                    }
            elif action == "receive":
                # Process received A2A message
                return {
                    "status": "success",
                    "message": "Message received successfully",
                    "protocol": "a2a",
                    "data": message
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "protocol": "a2a"
                }
        except Exception as e:
            logger.error(f"Error handling A2A message: {e}")
            return {"status": "error", "message": str(e), "protocol": "a2a"}
    
    def _handle_custom_protocol(self, message: Dict, action: str) -> Dict:
        """
        Handle custom protocol messages.
        
        Args:
            message: Message to handle
            action: Action to perform (send or receive)
            
        Returns:
            Dict: Handling results
        """
        try:
            # Get protocol name from message
            protocol_name = message.get("protocol")
            
            if not protocol_name or protocol_name not in self.custom_protocols:
                return {
                    "status": "error",
                    "message": f"Unknown custom protocol: {protocol_name}"
                }
            
            # Get protocol configuration
            protocol_config = self.custom_protocols[protocol_name]
            protocol_endpoint = protocol_config.get("endpoint", f"http://localhost:9011/{protocol_name}")
            protocol_auth_token = protocol_config.get("auth_token", "")
            
            if action == "send":
                # Add protocol headers
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {protocol_auth_token}",
                    f"X-{protocol_name.upper()}-Version": self.protocol_versions[protocol_name]
                }
                
                # Send message to protocol endpoint
                response = requests.post(
                    f"{protocol_endpoint}/message",
                    headers=headers,
                    json=message,
                    timeout=self.timeout
                )
                
                # Check response
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "message": "Message sent successfully",
                        "protocol": protocol_name,
                        "response": response.json()
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Error sending message: {response.text}",
                        "protocol": protocol_name,
                        "status_code": response.status_code
                    }
            elif action == "receive":
                # Process received protocol message
                return {
                    "status": "success",
                    "message": "Message received successfully",
                    "protocol": protocol_name,
                    "data": message
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "protocol": protocol_name
                }
        except Exception as e:
            logger.error(f"Error handling custom protocol message: {e}")
            return {"status": "error", "message": str(e), "protocol": message.get("protocol", "unknown")}
    
    def _validate_message(self, message: Dict, protocol: str) -> Dict:
        """
        Validate a message against a protocol schema.
        
        Args:
            message: Message to validate
            protocol: Protocol name
            
        Returns:
            Dict: Validation results
        """
        try:
            # Get protocol schema
            schema = self.protocol_schemas.get(protocol)
            
            if not schema:
                return {
                    "status": "warning",
                    "message": f"No schema available for protocol: {protocol}"
                }
            
            # In a real implementation, this would use a proper schema validator
            # For now, just check required fields
            
            # Check required fields
            for field in schema.get("required", []):
                if field not in message:
                    return {
                        "status": "error",
                        "message": f"Missing required field: {field}",
                        "protocol": protocol
                    }
            
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Error validating message: {e}")
            return {"status": "error", "message": str(e), "protocol": protocol}
    
    def _transform_message(self, message: Dict, source_protocol: str, target_protocol: str) -> Dict:
        """
        Transform a message from one protocol to another.
        
        Args:
            message: Message to transform
            source_protocol: Source protocol
            target_protocol: Target protocol
            
        Returns:
            Dict: Transformed message
        """
        try:
            # If protocols are the same, no transformation needed
            if source_protocol == target_protocol:
                return message
            
            # Get protocol schemas
            source_schema = self.protocol_schemas.get(source_protocol, {})
            target_schema = self.protocol_schemas.get(target_protocol, {})
            
            # Create transformed message
            transformed_message = {}
            
            # Add protocol-specific fields
            transformed_message["protocol"] = target_protocol
            transformed_message["version"] = self.protocol_versions[target_protocol]
            
            # Add timestamp
            transformed_message["timestamp"] = datetime.now().isoformat()
            
            # Add original protocol info
            transformed_message["original_protocol"] = source_protocol
            transformed_message["original_version"] = self.protocol_versions[source_protocol]
            
            # Transform specific protocol combinations
            if source_protocol == "mcp" and target_protocol == "a2a":
                # MCP to A2A transformation
                
                # Map common fields
                if "id" in message:
                    transformed_message["messageId"] = message["id"]
                
                if "sender" in message:
                    transformed_message["senderId"] = message["sender"]
                
                if "receiver" in message:
                    transformed_message["receiverId"] = message["receiver"]
                
                if "content" in message:
                    transformed_message["content"] = message["content"]
                
                # Add A2A-specific fields
                transformed_message["type"] = "task"
                
                if "industryTags" in self.a2a_config:
                    transformed_message["industryTags"] = self.a2a_config["industryTags"]
                
                if "priority" in self.a2a_config:
                    transformed_message["priority"] = self.a2a_config["priority"]
            elif source_protocol == "a2a" and target_protocol == "mcp":
                # A2A to MCP transformation
                
                # Map common fields
                if "messageId" in message:
                    transformed_message["id"] = message["messageId"]
                
                if "senderId" in message:
                    transformed_message["sender"] = message["senderId"]
                
                if "receiverId" in message:
                    transformed_message["receiver"] = message["receiverId"]
                
                if "content" in message:
                    transformed_message["content"] = message["content"]
                
                # Add MCP-specific fields
                transformed_message["type"] = "message"
            else:
                # Generic transformation for other protocol combinations
                
                # Copy all fields from source message
                for key, value in message.items():
                    if key not in ["protocol", "version"]:
                        transformed_message[key] = value
            
            return transformed_message
        except Exception as e:
            logger.error(f"Error transforming message: {e}")
            return message
    
    def _load_protocol_schemas(self) -> None:
        """
        Load protocol schemas.
        """
        try:
            # Load MCP schema
            self.protocol_schemas["mcp"] = {
                "type": "object",
                "required": ["id", "sender", "receiver", "content"],
                "properties": {
                    "id": {"type": "string"},
                    "sender": {"type": "string"},
                    "receiver": {"type": "string"},
                    "content": {"type": "object"},
                    "type": {"type": "string"},
                    "timestamp": {"type": "string"}
                }
            }
            
            # Load A2A schema
            self.protocol_schemas["a2a"] = {
                "type": "object",
                "required": ["messageId", "senderId", "receiverId", "content"],
                "properties": {
                    "messageId": {"type": "string"},
                    "senderId": {"type": "string"},
                    "receiverId": {"type": "string"},
                    "content": {"type": "object"},
                    "type": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "industryTags": {"type": "array"},
                    "priority": {"type": "integer"}
                }
            }
            
            # Load custom protocol schemas
            for protocol_name, protocol_config in self.custom_protocols.items():
                schema_path = protocol_config.get("schema_path")
                
                if schema_path and os.path.exists(schema_path):
                    with open(schema_path, "r") as f:
                        self.protocol_schemas[protocol_name] = json.load(f)
                else:
                    # Use default schema
                    self.protocol_schemas[protocol_name] = {
                        "type": "object",
                        "required": ["id", "sender", "receiver", "content"],
                        "properties": {
                            "id": {"type": "string"},
                            "sender": {"type": "string"},
                            "receiver": {"type": "string"},
                            "content": {"type": "object"},
                            "type": {"type": "string"},
                            "timestamp": {"type": "string"}
                        }
                    }
            
            logger.info(f"Loaded schemas for {len(self.protocol_schemas)} protocols")
        except Exception as e:
            logger.error(f"Error loading protocol schemas: {e}")
    
    def _track_protocol_event(self, event_type: str, protocol: str, result: Dict) -> None:
        """
        Track a protocol event in analytics.
        
        Args:
            event_type: Event type
            protocol: Protocol name
            result: Event result
        """
        try:
            # Prepare metrics
            metrics = {
                "type": f"protocol_{event_type}",
                "timestamp": datetime.now().isoformat(),
                "protocol": protocol,
                "status": result.get("status"),
                "bridge_id": self.bridge_id
            }
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking protocol event: {e}")
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Protocol Bridge.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "mcp" in config:
                self.mcp_config.update(config["mcp"])
                if "version" in config["mcp"]:
                    self.protocol_versions["mcp"] = config["mcp"]["version"]
            
            if "a2a" in config:
                self.a2a_config.update(config["a2a"])
                if "version" in config["a2a"]:
                    self.protocol_versions["a2a"] = config["a2a"]["version"]
            
            if "custom_protocols" in config:
                for protocol_name, protocol_config in config["custom_protocols"].items():
                    if protocol_name not in self.custom_protocols:
                        self.custom_protocols[protocol_name] = protocol_config
                        self.protocol_handlers[protocol_name] = self._handle_custom_protocol
                        self.protocol_versions[protocol_name] = protocol_config.get("version", "1.0.0")
                        self.protocol_metrics[protocol_name] = {"sent": 0, "received": 0, "errors": 0}
                    else:
                        self.custom_protocols[protocol_name].update(protocol_config)
                        if "version" in protocol_config:
                            self.protocol_versions[protocol_name] = protocol_config["version"]
            
            # Reload protocol schemas
            self._load_protocol_schemas()
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            return {
                "status": "success",
                "message": "Protocol Bridge configured successfully",
                "bridge_id": self.bridge_id,
                "analytics_result": analytics_result
            }
        except Exception as e:
            logger.error(f"Error configuring Protocol Bridge: {e}")
            return {"status": "error", "message": str(e)}
