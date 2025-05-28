"""
OPC-UA Protocol Adapter for Industriverse Protocol Layer

This module provides a comprehensive adapter for integrating OPC-UA industrial protocol
with the Industriverse Protocol Layer. It enables seamless communication between
OPC-UA devices/systems and the protocol-native architecture of Industriverse.

Features:
- Full OPC-UA client and server capabilities
- Bidirectional translation between OPC-UA and Industriverse protocols
- Support for all OPC-UA data types and services
- Security integration with EKIS framework
- Automatic discovery of OPC-UA endpoints
- Subscription management for real-time data
- Historical data access
- Alarm and event handling
- Method calling support
- Certificate management

Dependencies:
- opcua-asyncio (https://github.com/FreeOpcUa/opcua-asyncio)
- cryptography
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

# Import Protocol Layer base components
from protocols.protocol_base import ProtocolComponent
from protocols.message_formats import MessageFactory, MessagePriority, MessageType
from protocols.discovery_service import DiscoveryService

# Import EKIS security components
from security.ekis.tpm_integration import TPMSecurityProvider
from security.ekis.security_handler import EKISSecurityHandler

# Import OPC-UA library
try:
    import asyncua
    from asyncua import Client, Server
    from asyncua.common.node import Node
    from asyncua.ua import NodeId, QualifiedName, DataValue, Variant, VariantType
    from asyncua.ua.uaerrors import UaError
except ImportError:
    logging.error("OPC-UA library not found. Please install opcua-asyncio package.")
    asyncua = None
    Client = None
    Server = None

class OPCUAAdapter(ProtocolComponent):
    """
    OPC-UA Protocol Adapter for Industriverse Protocol Layer.
    
    This adapter enables bidirectional communication between OPC-UA devices/systems
    and the Industriverse Protocol Layer, translating between OPC-UA protocol and
    Industriverse's protocol-native architecture.
    """
    
    def __init__(self, component_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OPC-UA adapter.
        
        Args:
            component_id: Unique identifier for this adapter instance
            config: Configuration parameters for the adapter
        """
        super().__init__(component_id or str(uuid.uuid4()), "opcua_adapter")
        
        # Add capabilities
        self.add_capability("opcua_client", "OPC-UA client functionality")
        self.add_capability("opcua_server", "OPC-UA server functionality")
        self.add_capability("opcua_discovery", "OPC-UA endpoint discovery")
        self.add_capability("opcua_subscription", "OPC-UA subscription management")
        self.add_capability("opcua_historical", "OPC-UA historical data access")
        self.add_capability("opcua_method", "OPC-UA method calling")
        self.add_capability("opcua_event", "OPC-UA event handling")
        
        # Initialize configuration
        self.config = config or {}
        self.logger = logging.getLogger(f"industriverse.protocol.opcua.{self.component_id}")
        
        # Initialize client and server
        self.client = None
        self.server = None
        self.subscriptions = {}
        self.connected_endpoints = {}
        
        # Initialize security handler
        self.security_handler = EKISSecurityHandler(
            component_id=f"{self.component_id}_security",
            tpm_provider=TPMSecurityProvider() if self.config.get("use_tpm", True) else None
        )
        
        # Register with discovery service
        self.discovery_service = DiscoveryService()
        self.discovery_service.register_component(
            self.component_id,
            "opcua_adapter",
            {
                "protocols": ["opcua"],
                "capabilities": list(self._capabilities.keys()),
                "industryTags": self.config.get("industry_tags", ["manufacturing", "energy", "utilities"])
            }
        )
        
        self.logger.info(f"OPC-UA Adapter {self.component_id} initialized")
    
    async def connect_client(self, endpoint_url: str, security_mode: Optional[str] = None) -> bool:
        """
        Connect to an OPC-UA server as a client.
        
        Args:
            endpoint_url: URL of the OPC-UA server endpoint
            security_mode: Security mode to use for the connection
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not asyncua:
            self.logger.error("OPC-UA library not installed. Cannot connect client.")
            return False
            
        try:
            # Create client with appropriate security settings
            self.client = Client(endpoint_url)
            
            # Configure security based on mode
            if security_mode:
                if security_mode == "sign":
                    await self.client.set_security_string("Basic256Sha256,SignAndEncrypt,cert.pem,key.pem")
                elif security_mode == "sign_encrypt":
                    await self.client.set_security_string("Basic256Sha256,SignAndEncrypt,cert.pem,key.pem")
                    
            # Connect to server
            await self.client.connect()
            
            # Store connected endpoint
            self.connected_endpoints[endpoint_url] = {
                "client": self.client,
                "connected_at": datetime.now(),
                "security_mode": security_mode
            }
            
            self.logger.info(f"Connected to OPC-UA server at {endpoint_url}")
            
            # Publish connection event
            await self.publish_event(
                MessageFactory.create_event(
                    "opcua_client_connected",
                    payload={
                        "endpoint_url": endpoint_url,
                        "security_mode": security_mode,
                        "server_info": str(await self.client.get_server_node().get_browse_name())
                    },
                    priority=MessagePriority.MEDIUM
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to OPC-UA server at {endpoint_url}: {str(e)}")
            return False
    
    async def disconnect_client(self, endpoint_url: Optional[str] = None) -> bool:
        """
        Disconnect from an OPC-UA server.
        
        Args:
            endpoint_url: URL of the OPC-UA server endpoint to disconnect from.
                          If None, disconnect from all endpoints.
                          
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if endpoint_url:
                if endpoint_url in self.connected_endpoints:
                    client = self.connected_endpoints[endpoint_url]["client"]
                    await client.disconnect()
                    del self.connected_endpoints[endpoint_url]
                    self.logger.info(f"Disconnected from OPC-UA server at {endpoint_url}")
                    return True
                else:
                    self.logger.warning(f"Not connected to OPC-UA server at {endpoint_url}")
                    return False
            else:
                # Disconnect from all endpoints
                for url, endpoint_data in list(self.connected_endpoints.items()):
                    client = endpoint_data["client"]
                    await client.disconnect()
                    self.logger.info(f"Disconnected from OPC-UA server at {url}")
                
                self.connected_endpoints = {}
                return True
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from OPC-UA server: {str(e)}")
            return False
    
    async def start_server(self, endpoint_url: str, server_name: str, security_enabled: bool = True) -> bool:
        """
        Start an OPC-UA server.
        
        Args:
            endpoint_url: URL for the server endpoint
            server_name: Name of the server
            security_enabled: Whether to enable security features
            
        Returns:
            bool: True if server started successfully, False otherwise
        """
        if not asyncua:
            self.logger.error("OPC-UA library not installed. Cannot start server.")
            return False
            
        try:
            # Create server
            self.server = Server()
            
            # Configure server
            await self.server.init()
            self.server.set_endpoint(endpoint_url)
            self.server.set_server_name(server_name)
            
            # Configure security if enabled
            if security_enabled:
                # Generate certificate if needed
                cert_path, private_key_path = await self.security_handler.generate_certificate(
                    common_name=server_name,
                    dns_name=endpoint_url.split("://")[1].split(":")[0],
                    uri=endpoint_url
                )
                
                # Set security policy
                self.server.set_security_policy([
                    # Allow anonymous access for discovery
                    {"policy": asyncua.ua.SecurityPolicyType.NoSecurity, "mode": asyncua.ua.MessageSecurityMode.None_, "certificate": None},
                    # Require signing for regular access
                    {"policy": asyncua.ua.SecurityPolicyType.Basic256Sha256, "mode": asyncua.ua.MessageSecurityMode.Sign, "certificate": cert_path},
                    # Require encryption for sensitive operations
                    {"policy": asyncua.ua.SecurityPolicyType.Basic256Sha256, "mode": asyncua.ua.MessageSecurityMode.SignAndEncrypt, "certificate": cert_path}
                ])
                
                # Set certificate and private key
                await self.server.load_certificate(cert_path)
                await self.server.load_private_key(private_key_path)
            
            # Set up namespace
            idx = await self.server.register_namespace(f"urn:industriverse:opcua:{self.component_id}")
            
            # Create objects folder
            objects = self.server.nodes.objects
            
            # Create Industriverse folder
            industriverse_folder = await objects.add_folder(idx, "Industriverse")
            
            # Create status variable
            status_var = await industriverse_folder.add_variable(idx, "Status", "Online")
            await status_var.set_writable()
            
            # Start server
            await self.server.start()
            
            self.logger.info(f"OPC-UA server started at {endpoint_url}")
            
            # Publish server start event
            await self.publish_event(
                MessageFactory.create_event(
                    "opcua_server_started",
                    payload={
                        "endpoint_url": endpoint_url,
                        "server_name": server_name,
                        "security_enabled": security_enabled
                    },
                    priority=MessagePriority.MEDIUM
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start OPC-UA server: {str(e)}")
            return False
    
    async def stop_server(self) -> bool:
        """
        Stop the OPC-UA server.
        
        Returns:
            bool: True if server stopped successfully, False otherwise
        """
        if not self.server:
            self.logger.warning("No OPC-UA server running")
            return False
            
        try:
            await self.server.stop()
            self.logger.info("OPC-UA server stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping OPC-UA server: {str(e)}")
            return False
    
    async def discover_endpoints(self, discovery_url: str) -> List[Dict[str, Any]]:
        """
        Discover OPC-UA endpoints at the given URL.
        
        Args:
            discovery_url: URL for OPC-UA discovery
            
        Returns:
            List of discovered endpoints with their properties
        """
        if not asyncua:
            self.logger.error("OPC-UA library not installed. Cannot discover endpoints.")
            return []
            
        try:
            # Create temporary client for discovery
            client = Client(discovery_url)
            
            # Get endpoints
            endpoints = await client.connect_and_get_server_endpoints()
            
            # Format endpoint information
            result = []
            for endpoint in endpoints:
                result.append({
                    "endpoint_url": endpoint.EndpointUrl,
                    "security_mode": str(endpoint.SecurityMode),
                    "security_policy_uri": endpoint.SecurityPolicyUri,
                    "transport_profile_uri": endpoint.TransportProfileUri,
                    "security_level": endpoint.SecurityLevel
                })
            
            self.logger.info(f"Discovered {len(result)} OPC-UA endpoints at {discovery_url}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error discovering OPC-UA endpoints at {discovery_url}: {str(e)}")
            return []
    
    async def browse_nodes(self, endpoint_url: str, node_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Browse nodes on an OPC-UA server.
        
        Args:
            endpoint_url: URL of the OPC-UA server endpoint
            node_id: ID of the node to browse (None for root)
            
        Returns:
            List of child nodes with their properties
        """
        if endpoint_url not in self.connected_endpoints:
            self.logger.error(f"Not connected to OPC-UA server at {endpoint_url}")
            return []
            
        client = self.connected_endpoints[endpoint_url]["client"]
        
        try:
            # Get node to browse
            if node_id:
                node = client.get_node(node_id)
            else:
                node = client.nodes.objects
                
            # Browse children
            children = await node.get_children()
            
            # Get properties for each child
            result = []
            for child in children:
                try:
                    browse_name = await child.get_browse_name()
                    display_name = await child.get_display_name()
                    node_class = await child.get_node_class()
                    
                    child_info = {
                        "node_id": child.nodeid.to_string(),
                        "browse_name": browse_name.Name,
                        "display_name": display_name.Text,
                        "node_class": str(node_class)
                    }
                    
                    # Get value if variable
                    if node_class == asyncua.ua.NodeClass.Variable:
                        try:
                            value = await child.get_value()
                            data_type = await child.get_data_type()
                            data_type_name = await client.get_node(data_type).get_browse_name()
                            
                            child_info["value"] = str(value)
                            child_info["data_type"] = data_type_name.Name
                        except Exception as e:
                            child_info["value"] = f"Error: {str(e)}"
                    
                    result.append(child_info)
                except Exception as e:
                    self.logger.warning(f"Error getting properties for node {child.nodeid}: {str(e)}")
                    result.append({
                        "node_id": child.nodeid.to_string(),
                        "error": str(e)
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error browsing nodes: {str(e)}")
            return []
    
    async def read_node(self, endpoint_url: str, node_id: str) -> Dict[str, Any]:
        """
        Read a node's value and properties from an OPC-UA server.
        
        Args:
            endpoint_url: URL of the OPC-UA server endpoint
            node_id: ID of the node to read
            
        Returns:
            Node properties and value
        """
        if endpoint_url not in self.connected_endpoints:
            self.logger.error(f"Not connected to OPC-UA server at {endpoint_url}")
            return {"error": "Not connected to server"}
            
        client = self.connected_endpoints[endpoint_url]["client"]
        
        try:
            # Get node
            node = client.get_node(node_id)
            
            # Get properties
            browse_name = await node.get_browse_name()
            display_name = await node.get_display_name()
            node_class = await node.get_node_class()
            
            result = {
                "node_id": node_id,
                "browse_name": browse_name.Name,
                "display_name": display_name.Text,
                "node_class": str(node_class)
            }
            
            # Get value if variable
            if node_class == asyncua.ua.NodeClass.Variable:
                value = await node.get_value()
                data_type = await node.get_data_type()
                data_type_name = await client.get_node(data_type).get_browse_name()
                
                result["value"] = value
                result["data_type"] = data_type_name.Name
                
                # Get additional properties
                try:
                    result["timestamp"] = await node.get_value_timestamp()
                except:
                    pass
                    
                try:
                    result["description"] = (await node.get_description()).Text
                except:
                    pass
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error reading node {node_id}: {str(e)}")
            return {"error": str(e)}
    
    async def write_node(self, endpoint_url: str, node_id: str, value: Any) -> bool:
        """
        Write a value to a node on an OPC-UA server.
        
        Args:
            endpoint_url: URL of the OPC-UA server endpoint
            node_id: ID of the node to write to
            value: Value to write
            
        Returns:
            bool: True if write successful, False otherwise
        """
        if endpoint_url not in self.connected_endpoints:
            self.logger.error(f"Not connected to OPC-UA server at {endpoint_url}")
            return False
            
        client = self.connected_endpoints[endpoint_url]["client"]
        
        try:
            # Get node
            node = client.get_node(node_id)
            
            # Write value
            await node.write_value(value)
            
            self.logger.info(f"Successfully wrote value to node {node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing to node {node_id}: {str(e)}")
            return False
    
    async def create_subscription(self, endpoint_url: str, node_id: str, 
                                 period: float = 1000.0, callback: Optional[callable] = None) -> str:
        """
        Create a subscription to monitor changes to a node.
        
        Args:
            endpoint_url: URL of the OPC-UA server endpoint
            node_id: ID of the node to monitor
            period: Sampling period in milliseconds
            callback: Optional callback function to call when value changes
            
        Returns:
            str: Subscription ID if successful, empty string otherwise
        """
        if endpoint_url not in self.connected_endpoints:
            self.logger.error(f"Not connected to OPC-UA server at {endpoint_url}")
            return ""
            
        client = self.connected_endpoints[endpoint_url]["client"]
        
        try:
            # Get node
            node = client.get_node(node_id)
            
            # Create subscription
            subscription = await client.create_subscription(period, self)
            
            # Define handler
            async def data_change_notification(node, val, data):
                self.logger.debug(f"Data change on {node_id}: {val}")
                
                # Create event message
                event_msg = MessageFactory.create_event(
                    "opcua_data_change",
                    payload={
                        "endpoint_url": endpoint_url,
                        "node_id": node_id,
                        "value": val,
                        "timestamp": datetime.now().isoformat()
                    },
                    priority=MessagePriority.MEDIUM
                )
                
                # Publish event
                await self.publish_event(event_msg)
                
                # Call callback if provided
                if callback:
                    try:
                        await callback(node, val, data)
                    except Exception as e:
                        self.logger.error(f"Error in subscription callback: {str(e)}")
            
            # Subscribe to node
            handle = await subscription.subscribe_data_change(node, data_change_notification)
            
            # Generate subscription ID
            subscription_id = str(uuid.uuid4())
            
            # Store subscription
            self.subscriptions[subscription_id] = {
                "endpoint_url": endpoint_url,
                "node_id": node_id,
                "subscription": subscription,
                "handle": handle,
                "period": period,
                "created_at": datetime.now()
            }
            
            self.logger.info(f"Created subscription {subscription_id} for node {node_id}")
            return subscription_id
            
        except Exception as e:
            self.logger.error(f"Error creating subscription for node {node_id}: {str(e)}")
            return ""
    
    async def delete_subscription(self, subscription_id: str) -> bool:
        """
        Delete a subscription.
        
        Args:
            subscription_id: ID of the subscription to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if subscription_id not in self.subscriptions:
            self.logger.error(f"Subscription {subscription_id} not found")
            return False
            
        try:
            # Get subscription data
            sub_data = self.subscriptions[subscription_id]
            subscription = sub_data["subscription"]
            handle = sub_data["handle"]
            
            # Unsubscribe
            await subscription.unsubscribe(handle)
            await subscription.delete()
            
            # Remove from subscriptions
            del self.subscriptions[subscription_id]
            
            self.logger.info(f"Deleted subscription {subscription_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting subscription {subscription_id}: {str(e)}")
            return False
    
    async def call_method(self, endpoint_url: str, parent_node_id: str, 
                         method_node_id: str, *args) -> Dict[str, Any]:
        """
        Call a method on an OPC-UA server.
        
        Args:
            endpoint_url: URL of the OPC-UA server endpoint
            parent_node_id: ID of the parent node
            method_node_id: ID of the method node
            *args: Arguments to pass to the method
            
        Returns:
            Dict with result or error
        """
        if endpoint_url not in self.connected_endpoints:
            self.logger.error(f"Not connected to OPC-UA server at {endpoint_url}")
            return {"error": "Not connected to server"}
            
        client = self.connected_endpoints[endpoint_url]["client"]
        
        try:
            # Get nodes
            parent_node = client.get_node(parent_node_id)
            method_node = client.get_node(method_node_id)
            
            # Call method
            result = await parent_node.call_method(method_node, *args)
            
            self.logger.info(f"Successfully called method {method_node_id}")
            return {"result": result}
            
        except Exception as e:
            self.logger.error(f"Error calling method {method_node_id}: {str(e)}")
            return {"error": str(e)}
    
    async def read_history(self, endpoint_url: str, node_id: str, 
                          start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Read historical data for a node.
        
        Args:
            endpoint_url: URL of the OPC-UA server endpoint
            node_id: ID of the node to read history for
            start_time: Start time for historical data
            end_time: End time for historical data
            
        Returns:
            Dict with historical data or error
        """
        if endpoint_url not in self.connected_endpoints:
            self.logger.error(f"Not connected to OPC-UA server at {endpoint_url}")
            return {"error": "Not connected to server"}
            
        client = self.connected_endpoints[endpoint_url]["client"]
        
        try:
            # Get node
            node = client.get_node(node_id)
            
            # Read history
            history = await node.read_raw_history(start_time, end_time)
            
            # Format results
            result = {
                "node_id": node_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "values": []
            }
            
            for datavalue in history:
                result["values"].append({
                    "value": datavalue.Value.Value,
                    "timestamp": datavalue.SourceTimestamp.isoformat() if datavalue.SourceTimestamp else None,
                    "status": str(datavalue.StatusCode)
                })
            
            self.logger.info(f"Successfully read history for node {node_id}, got {len(result['values'])} values")
            return result
            
        except Exception as e:
            self.logger.error(f"Error reading history for node {node_id}: {str(e)}")
            return {"error": str(e)}
    
    async def translate_to_industriverse(self, opcua_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate OPC-UA data to Industriverse protocol format.
        
        Args:
            opcua_data: OPC-UA data to translate
            
        Returns:
            Data in Industriverse protocol format
        """
        # Create Unified Message Envelope
        ume = {
            "origin_protocol": "OPCUA",
            "target_protocol": "MCP",
            "context": {
                "industrial_protocol": "OPCUA",
                "adapter_id": self.component_id,
                "timestamp": datetime.now().isoformat()
            },
            "payload": opcua_data,
            "trace_id": str(uuid.uuid4()),
            "security_level": "medium",
            "reflex_timer_ms": 5000  # 5 seconds default timeout
        }
        
        return ume
    
    async def translate_from_industriverse(self, industriverse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Industriverse protocol data to OPC-UA format.
        
        Args:
            industriverse_data: Industriverse protocol data to translate
            
        Returns:
            Data in OPC-UA format
        """
        # Extract payload from Unified Message Envelope
        if "payload" in industriverse_data:
            return industriverse_data["payload"]
        else:
            return industriverse_data
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming protocol messages.
        
        Args:
            message: Incoming message
            
        Returns:
            Response message
        """
        try:
            # Extract command from message
            command = message.get("command", "")
            params = message.get("params", {})
            
            # Process command
            if command == "discover_endpoints":
                result = await self.discover_endpoints(params.get("discovery_url", ""))
                return MessageFactory.create_response(message, result=result)
                
            elif command == "connect_client":
                success = await self.connect_client(
                    params.get("endpoint_url", ""),
                    params.get("security_mode", None)
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "disconnect_client":
                success = await self.disconnect_client(params.get("endpoint_url", None))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "browse_nodes":
                result = await self.browse_nodes(
                    params.get("endpoint_url", ""),
                    params.get("node_id", None)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "read_node":
                result = await self.read_node(
                    params.get("endpoint_url", ""),
                    params.get("node_id", "")
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "write_node":
                success = await self.write_node(
                    params.get("endpoint_url", ""),
                    params.get("node_id", ""),
                    params.get("value", None)
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "create_subscription":
                subscription_id = await self.create_subscription(
                    params.get("endpoint_url", ""),
                    params.get("node_id", ""),
                    params.get("period", 1000.0)
                )
                return MessageFactory.create_response(message, result={"subscription_id": subscription_id})
                
            elif command == "delete_subscription":
                success = await self.delete_subscription(params.get("subscription_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "call_method":
                result = await self.call_method(
                    params.get("endpoint_url", ""),
                    params.get("parent_node_id", ""),
                    params.get("method_node_id", ""),
                    *params.get("args", [])
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "read_history":
                result = await self.read_history(
                    params.get("endpoint_url", ""),
                    params.get("node_id", ""),
                    datetime.fromisoformat(params.get("start_time", "")),
                    datetime.fromisoformat(params.get("end_time", ""))
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "start_server":
                success = await self.start_server(
                    params.get("endpoint_url", ""),
                    params.get("server_name", "Industriverse OPC-UA Server"),
                    params.get("security_enabled", True)
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "stop_server":
                success = await self.stop_server()
                return MessageFactory.create_response(message, result={"success": success})
                
            else:
                return MessageFactory.create_response(
                    message,
                    success=False,
                    error=f"Unknown command: {command}"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            return MessageFactory.create_response(
                message,
                success=False,
                error=f"Error: {str(e)}"
            )
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming messages from the Protocol Layer.
        
        This method is called by the Protocol Layer when a message is received
        for this adapter.
        
        Args:
            message: Incoming message
            
        Returns:
            Response message
        """
        # Translate from Industriverse protocol if needed
        if message.get("origin_protocol") and message.get("origin_protocol") != "OPCUA":
            opcua_message = await self.translate_from_industriverse(message)
        else:
            opcua_message = message
            
        # Handle message
        response = await self.handle_message(opcua_message)
        
        # Translate to Industriverse protocol if needed
        if message.get("target_protocol") and message.get("target_protocol") != "OPCUA":
            industriverse_response = await self.translate_to_industriverse(response)
            return industriverse_response
        else:
            return response
    
    async def shutdown(self):
        """
        Shutdown the adapter, closing all connections and subscriptions.
        """
        self.logger.info(f"Shutting down OPC-UA Adapter {self.component_id}")
        
        # Stop server if running
        if self.server:
            await self.stop_server()
            
        # Disconnect all clients
        await self.disconnect_client()
        
        # Unregister from discovery service
        self.discovery_service.unregister_component(self.component_id)
        
        self.logger.info(f"OPC-UA Adapter {self.component_id} shutdown complete")

# Example usage
async def example_usage():
    # Create adapter
    adapter = OPCUAAdapter(config={
        "use_tpm": True,
        "industry_tags": ["manufacturing", "energy"]
    })
    
    # Discover endpoints
    endpoints = await adapter.discover_endpoints("opc.tcp://localhost:4840")
    print(f"Discovered endpoints: {endpoints}")
    
    # Connect to server
    success = await adapter.connect_client("opc.tcp://localhost:4840")
    if success:
        # Browse nodes
        nodes = await adapter.browse_nodes("opc.tcp://localhost:4840")
        print(f"Root nodes: {nodes}")
        
        # Read a node
        if nodes:
            node_id = nodes[0]["node_id"]
            node_data = await adapter.read_node("opc.tcp://localhost:4840", node_id)
            print(f"Node data: {node_data}")
            
        # Disconnect
        await adapter.disconnect_client("opc.tcp://localhost:4840")
    
    # Shutdown
    await adapter.shutdown()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run example
    asyncio.run(example_usage())
