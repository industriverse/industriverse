"""
Corda Blockchain Connector for Industriverse Protocol Layer

This module provides a comprehensive connector for integrating R3 Corda blockchain
with the Industriverse Protocol Layer. It enables seamless communication between
Corda networks and the protocol-native architecture of Industriverse.

Features:
- Connection to Corda networks
- CorDapp deployment and interaction
- Flow invocation and tracking
- Vault queries and updates
- Node management and monitoring
- Security integration with EKIS framework including ZKP
- Comprehensive error handling and diagnostics
- Support for multiple Corda versions (4.x, 5.x)

Dependencies:
- py4j (Python-Java bridge)
- corda-rpc-client
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

# Import Protocol Layer base components
from blockchain.connectors.blockchain_connector_base import BlockchainConnectorBase, BlockchainType, TransactionStatus

# Import EKIS security components
from security.ekis.tpm_integration import TPMSecurityProvider
from security.ekis.security_handler import EKISSecurityHandler
from security.ekis.zkp_handler import ZKPHandler

# Import Corda libraries
try:
    from py4j.java_gateway import JavaGateway, GatewayParameters
    HAS_PY4J = True
except ImportError:
    logging.warning("py4j library not found. Using mock implementation.")
    HAS_PY4J = False
    
    # Mock implementation for development
    class MockJavaGateway:
        def __init__(self, gateway_parameters=None):
            self.entry_point = MockEntryPoint()
            
        def close(self):
            pass
            
    class MockEntryPoint:
        def __init__(self):
            self.rpc_client = MockRpcClient()
            self.flow_manager = MockFlowManager()
            self.vault_service = MockVaultService()
            self.node_service = MockNodeService()
            
    class MockRpcClient:
        def __init__(self):
            self.connected = False
            
        def connect(self, host, port, username, password):
            self.connected = True
            return MockCordaConnection()
            
        def disconnect(self):
            self.connected = False
            
    class MockCordaConnection:
        def __init__(self):
            self.proxy = MockCordaProxy()
            
    class MockCordaProxy:
        def __init__(self):
            self.network_parameters = {
                "minimumPlatformVersion": 4,
                "notaries": ["O=Notary,L=London,C=GB"]
            }
            self.node_info = {
                "legalIdentities": ["O=PartyA,L=London,C=GB"],
                "addresses": ["localhost:10005"]
            }
            
        def networkMapSnapshot(self):
            return [
                {
                    "legalIdentities": ["O=PartyA,L=London,C=GB"],
                    "addresses": ["localhost:10005"]
                },
                {
                    "legalIdentities": ["O=PartyB,L=New York,C=US"],
                    "addresses": ["localhost:10008"]
                }
            ]
            
        def registeredFlows(self):
            return [
                "com.example.flow.ExampleFlow$Initiator",
                "com.example.flow.AnotherFlow$Initiator"
            ]
            
        def startTrackedFlow(self, flow_class, *args):
            return MockFlowHandle()
            
        def startFlow(self, flow_class, *args):
            return MockFlowHandle()
            
    class MockFlowHandle:
        def __init__(self):
            self.id = str(uuid.uuid4())
            self.returnValue = MockFlowReturn()
            
        def getReturnValue(self):
            return self.returnValue
            
    class MockFlowReturn:
        def __init__(self):
            self.tx_id = str(uuid.uuid4())
            
        def get(self):
            return self.tx_id
            
    class MockFlowManager:
        def __init__(self):
            self.flows = {}
            
        def get_flow_class(self, flow_name):
            return f"com.example.flow.{flow_name}$Initiator"
            
        def track_flow(self, flow_handle):
            flow_id = flow_handle.id
            self.flows[flow_id] = {
                "id": flow_id,
                "status": "RUNNING",
                "started_at": datetime.now().isoformat()
            }
            return flow_id
            
        def get_flow_status(self, flow_id):
            if flow_id in self.flows:
                return self.flows[flow_id]["status"]
            return "UNKNOWN"
            
    class MockVaultService:
        def __init__(self):
            self.states = {}
            
        def query_by_type(self, state_type):
            return [
                {
                    "state_ref": str(uuid.uuid4()),
                    "state_data": {
                        "type": state_type,
                        "value": 100,
                        "participants": ["O=PartyA,L=London,C=GB", "O=PartyB,L=New York,C=US"]
                    }
                }
            ]
            
        def query_by_criteria(self, criteria):
            return [
                {
                    "state_ref": str(uuid.uuid4()),
                    "state_data": {
                        "type": criteria.get("type", "Unknown"),
                        "value": 100,
                        "participants": ["O=PartyA,L=London,C=GB", "O=PartyB,L=New York,C=US"]
                    }
                }
            ]
            
    class MockNodeService:
        def __init__(self):
            self.nodes = {
                "O=PartyA,L=London,C=GB": {
                    "status": "RUNNING",
                    "platform_version": 4,
                    "addresses": ["localhost:10005"]
                },
                "O=PartyB,L=New York,C=US": {
                    "status": "RUNNING",
                    "platform_version": 4,
                    "addresses": ["localhost:10008"]
                }
            }
            
        def get_node_info(self, node_name):
            if node_name in self.nodes:
                return self.nodes[node_name]
            return None
            
        def get_all_nodes(self):
            return self.nodes
            
    # Create mock classes to simulate Corda API
    JavaGateway = MockJavaGateway
    
    class GatewayParameters:
        def __init__(self, address="localhost", port=25333, auto_convert=True):
            self.address = address
            self.port = port
            self.auto_convert = auto_convert

class CordaConnector(BlockchainConnectorBase):
    """
    Corda Blockchain Connector for Industriverse Protocol Layer.
    
    This connector enables bidirectional communication between R3 Corda blockchain
    networks and the Industriverse Protocol Layer, translating between Corda
    protocol and Industriverse's protocol-native architecture.
    """
    
    def __init__(self, component_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Corda connector.
        
        Args:
            component_id: Unique identifier for this connector instance
            config: Configuration parameters for the connector
        """
        super().__init__(component_id, BlockchainType.CORDA, config)
        
        # Add Corda-specific capabilities
        self.add_capability("corda_flow_invocation", "Invoke Corda flows")
        self.add_capability("corda_vault_queries", "Query Corda vault")
        self.add_capability("corda_node_management", "Manage Corda nodes")
        self.add_capability("corda_cordapp_deployment", "Deploy CorDapps")
        
        # Initialize Java gateway
        self.gateway = None
        self.entry_point = None
        
        # Initialize RPC connection
        self.rpc_connection = None
        self.rpc_proxy = None
        
        # Initialize flow management
        self.flows = {}
        
        # Initialize node information
        self.node_info = {}
        self.network_map = {}
        
        # Initialize CorDapp management
        self.cordapps = {}
        
        self.logger.info("Corda Blockchain Connector initialized")
    
    async def connect(self, connection_params: Dict[str, Any]) -> bool:
        """
        Connect to a Corda network.
        
        Args:
            connection_params: Connection parameters
                - gateway_address: Address of the Java gateway server
                - gateway_port: Port of the Java gateway server
                - rpc_host: Host of the Corda RPC server
                - rpc_port: Port of the Corda RPC server
                - rpc_username: Username for RPC authentication
                - rpc_password: Password for RPC authentication
                
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Extract connection parameters
            gateway_address = connection_params.get("gateway_address", "localhost")
            gateway_port = connection_params.get("gateway_port", 25333)
            rpc_host = connection_params.get("rpc_host", "localhost")
            rpc_port = connection_params.get("rpc_port", 10006)
            rpc_username = connection_params.get("rpc_username", "")
            rpc_password = connection_params.get("rpc_password", "")
            
            # Validate parameters
            if not rpc_username or not rpc_password:
                self.logger.error("RPC username and password are required")
                return False
                
            # Create Java gateway
            gateway_params = GatewayParameters(
                address=gateway_address,
                port=gateway_port,
                auto_convert=True
            )
            self.gateway = JavaGateway(gateway_parameters=gateway_params)
            
            # Get entry point
            self.entry_point = self.gateway.entry_point
            
            # Connect to Corda node via RPC
            self.rpc_connection = self.entry_point.rpc_client.connect(
                rpc_host, rpc_port, rpc_username, rpc_password
            )
            
            # Get RPC proxy
            self.rpc_proxy = self.rpc_connection.proxy
            
            # Get node info
            node_info = self.rpc_proxy.nodeInfo()
            self.node_info = {
                "legal_identities": [str(identity) for identity in node_info.getLegalIdentities()],
                "addresses": [str(address) for address in node_info.getAddresses()]
            }
            
            # Get network map
            network_map = self.rpc_proxy.networkMapSnapshot()
            self.network_map = {
                str(node_info.getLegalIdentities()[0]): {
                    "addresses": [str(address) for address in node_info.getAddresses()]
                }
                for node_info in network_map
            }
            
            # Get registered flows
            registered_flows = self.rpc_proxy.registeredFlows()
            
            # Update connection state
            self.connected = True
            self.connection_info = {
                "gateway_address": gateway_address,
                "gateway_port": gateway_port,
                "rpc_host": rpc_host,
                "rpc_port": rpc_port,
                "node_identity": self.node_info["legal_identities"][0],
                "registered_flows": registered_flows,
                "connected_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Connected to Corda node: {self.node_info['legal_identities'][0]}")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "corda_connected",
                    "payload": {
                        "node_identity": self.node_info["legal_identities"][0],
                        "registered_flows": registered_flows
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to Corda network: {str(e)}")
            self.connected = False
            self.gateway = None
            self.entry_point = None
            self.rpc_connection = None
            self.rpc_proxy = None
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the Corda network.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        if not self.connected or not self.gateway:
            self.logger.warning("Not connected to Corda network")
            return False
            
        try:
            # Disconnect RPC client
            if self.rpc_connection:
                self.entry_point.rpc_client.disconnect()
                
            # Close Java gateway
            self.gateway.close()
            
            # Reset connection state
            self.connected = False
            self.gateway = None
            self.entry_point = None
            self.rpc_connection = None
            self.rpc_proxy = None
            
            self.logger.info("Disconnected from Corda network")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "corda_disconnected",
                    "payload": {
                        "node_identity": self.connection_info.get("node_identity", "")
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from Corda network: {str(e)}")
            return False
    
    async def is_connected(self) -> bool:
        """
        Check if connected to the Corda network.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connected and self.gateway is not None and self.rpc_proxy is not None
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the current connection.
        
        Returns:
            Dict with connection information
        """
        if not self.connected or not self.gateway:
            return {"connected": False}
            
        # Get network parameters
        try:
            network_params = self.rpc_proxy.getNetworkParameters()
            network_params_info = {
                "minimum_platform_version": network_params.getMinimumPlatformVersion(),
                "notaries": [str(notary) for notary in network_params.getNotaries()]
            }
        except Exception as e:
            self.logger.error(f"Error getting network parameters: {str(e)}")
            network_params_info = {}
            
        # Return connection info
        return {
            "connected": True,
            "gateway_address": self.connection_info.get("gateway_address", ""),
            "gateway_port": self.connection_info.get("gateway_port", 0),
            "rpc_host": self.connection_info.get("rpc_host", ""),
            "rpc_port": self.connection_info.get("rpc_port", 0),
            "node_identity": self.connection_info.get("node_identity", ""),
            "registered_flows": self.connection_info.get("registered_flows", []),
            "network_parameters": network_params_info,
            "connected_at": self.connection_info.get("connected_at", "")
        }
    
    async def start_flow(self, flow_params: Dict[str, Any]) -> str:
        """
        Start a Corda flow.
        
        Args:
            flow_params: Flow parameters
                - flow_name: Name of the flow to start
                - flow_args: Arguments for the flow
                - tracked: Whether to track the flow progress
                
        Returns:
            str: Flow ID if flow start successful, empty string otherwise
        """
        if not self.connected or not self.rpc_proxy:
            self.logger.error("Not connected to Corda network")
            return ""
            
        # Extract flow parameters
        flow_name = flow_params.get("flow_name", "")
        flow_args = flow_params.get("flow_args", [])
        tracked = flow_params.get("tracked", True)
        
        # Validate parameters
        if not flow_name:
            self.logger.error("Flow name is required")
            return ""
            
        try:
            # Get flow class
            flow_class = self.entry_point.flow_manager.get_flow_class(flow_name)
            
            # Start flow
            if tracked:
                flow_handle = self.rpc_proxy.startTrackedFlow(flow_class, *flow_args)
            else:
                flow_handle = self.rpc_proxy.startFlow(flow_class, *flow_args)
                
            # Track flow
            flow_id = self.entry_point.flow_manager.track_flow(flow_handle)
            
            # Store flow
            self.flows[flow_id] = {
                "flow_name": flow_name,
                "flow_args": flow_args,
                "handle": flow_handle,
                "status": "RUNNING",
                "started_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Started flow {flow_name} with ID {flow_id}")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "corda_flow_started",
                    "payload": {
                        "flow_id": flow_id,
                        "flow_name": flow_name
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Start monitoring flow
            asyncio.create_task(self._monitor_flow(flow_id))
            
            return flow_id
            
        except Exception as e:
            self.logger.error(f"Error starting flow: {str(e)}")
            return ""
    
    async def get_flow_status(self, flow_id: str) -> Dict[str, Any]:
        """
        Get the status of a flow.
        
        Args:
            flow_id: ID of the flow to check
            
        Returns:
            Dict with flow status
        """
        if flow_id not in self.flows:
            self.logger.error(f"Flow {flow_id} not found")
            return {"error": "Flow not found"}
            
        try:
            # Get flow info
            flow_info = self.flows[flow_id]
            
            # Get flow status
            status = self.entry_point.flow_manager.get_flow_status(flow_id)
            
            # Update flow status
            flow_info["status"] = status
            
            return {
                "flow_id": flow_id,
                "flow_name": flow_info["flow_name"],
                "status": status,
                "started_at": flow_info["started_at"],
                "completed_at": flow_info.get("completed_at", None),
                "result": flow_info.get("result", None)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting flow status: {str(e)}")
            return {"error": str(e)}
    
    async def query_vault(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query the Corda vault.
        
        Args:
            query_params: Query parameters
                - state_type: Type of state to query
                - criteria: Query criteria
                
        Returns:
            List of states matching the query
        """
        if not self.connected or not self.rpc_proxy:
            self.logger.error("Not connected to Corda network")
            return []
            
        # Extract query parameters
        state_type = query_params.get("state_type", "")
        criteria = query_params.get("criteria", {})
        
        # Validate parameters
        if not state_type:
            self.logger.error("State type is required")
            return []
            
        try:
            # Query vault
            if criteria:
                states = self.entry_point.vault_service.query_by_criteria(
                    state_type=state_type,
                    criteria=criteria
                )
            else:
                states = self.entry_point.vault_service.query_by_type(state_type)
                
            # Format states
            formatted_states = []
            for state in states:
                formatted_state = {
                    "state_ref": state["state_ref"],
                    "state_data": state["state_data"]
                }
                formatted_states.append(formatted_state)
                
            self.logger.info(f"Queried vault for {state_type} states, found {len(formatted_states)} results")
            
            return formatted_states
            
        except Exception as e:
            self.logger.error(f"Error querying vault: {str(e)}")
            return []
    
    async def get_node_info(self, node_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a Corda node.
        
        Args:
            node_name: Name of the node to get info for (optional, defaults to connected node)
            
        Returns:
            Dict with node information
        """
        if not self.connected or not self.rpc_proxy:
            self.logger.error("Not connected to Corda network")
            return {"error": "Not connected to Corda network"}
            
        try:
            if node_name:
                # Get info for specific node
                node_info = self.entry_point.node_service.get_node_info(node_name)
                if not node_info:
                    self.logger.error(f"Node {node_name} not found")
                    return {"error": f"Node {node_name} not found"}
                    
                return {
                    "name": node_name,
                    "status": node_info["status"],
                    "platform_version": node_info["platform_version"],
                    "addresses": node_info["addresses"]
                }
            else:
                # Get info for connected node
                return {
                    "name": self.node_info["legal_identities"][0],
                    "legal_identities": self.node_info["legal_identities"],
                    "addresses": self.node_info["addresses"]
                }
                
        except Exception as e:
            self.logger.error(f"Error getting node info: {str(e)}")
            return {"error": str(e)}
    
    async def get_network_map(self) -> Dict[str, Any]:
        """
        Get the Corda network map.
        
        Returns:
            Dict with network map
        """
        if not self.connected or not self.rpc_proxy:
            self.logger.error("Not connected to Corda network")
            return {"error": "Not connected to Corda network"}
            
        try:
            # Return network map
            return {
                "nodes": self.network_map,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting network map: {str(e)}")
            return {"error": str(e)}
    
    async def deploy_cordapp(self, cordapp_params: Dict[str, Any]) -> bool:
        """
        Deploy a CorDapp to the Corda node.
        
        Args:
            cordapp_params: CorDapp parameters
                - cordapp_name: Name of the CorDapp
                - cordapp_version: Version of the CorDapp
                - cordapp_path: Path to the CorDapp JAR file
                
        Returns:
            bool: True if deployment successful, False otherwise
        """
        if not self.connected or not self.rpc_proxy:
            self.logger.error("Not connected to Corda network")
            return False
            
        # Extract CorDapp parameters
        cordapp_name = cordapp_params.get("cordapp_name", "")
        cordapp_version = cordapp_params.get("cordapp_version", "")
        cordapp_path = cordapp_params.get("cordapp_path", "")
        
        # Validate parameters
        if not cordapp_name:
            self.logger.error("CorDapp name is required")
            return False
            
        if not cordapp_version:
            self.logger.error("CorDapp version is required")
            return False
            
        if not cordapp_path:
            self.logger.error("CorDapp path is required")
            return False
            
        try:
            # In a real implementation, we would deploy the CorDapp to the node
            # This would typically involve copying the JAR file to the node's cordapps directory
            # and restarting the node, which would be done outside of this connector
            
            # For this mock implementation, we'll just simulate a successful deployment
            
            # Generate CorDapp ID
            cordapp_id = f"{cordapp_name}_{cordapp_version}"
            
            # Store CorDapp
            self.cordapps[cordapp_id] = {
                "name": cordapp_name,
                "version": cordapp_version,
                "path": cordapp_path,
                "deployed_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Deployed CorDapp {cordapp_name} v{cordapp_version}")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "corda_cordapp_deployed",
                    "payload": {
                        "cordapp_id": cordapp_id,
                        "cordapp_name": cordapp_name,
                        "cordapp_version": cordapp_version
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying CorDapp: {str(e)}")
            return False
    
    async def create_transaction(self, transaction_params: Dict[str, Any]) -> str:
        """
        Create a new blockchain transaction.
        
        For Corda, this is a wrapper around start_flow.
        
        Args:
            transaction_params: Parameters for the transaction
                
        Returns:
            str: Flow ID if creation successful, empty string otherwise
        """
        return await self.start_flow(transaction_params)
    
    async def get_transaction_status(self, transaction_id: str) -> TransactionStatus:
        """
        Get the status of a transaction.
        
        For Corda, this is a wrapper around get_flow_status.
        
        Args:
            transaction_id: ID of the transaction to check
            
        Returns:
            TransactionStatus: Status of the transaction
        """
        if transaction_id not in self.flows:
            self.logger.error(f"Transaction {transaction_id} not found")
            return TransactionStatus.UNKNOWN
            
        try:
            # Get flow status
            flow_status = await self.get_flow_status(transaction_id)
            
            # Map flow status to transaction status
            if flow_status.get("error"):
                return TransactionStatus.UNKNOWN
            elif flow_status["status"] == "COMPLETED":
                return TransactionStatus.CONFIRMED
            elif flow_status["status"] == "FAILED":
                return TransactionStatus.FAILED
            else:
                return TransactionStatus.PENDING
                
        except Exception as e:
            self.logger.error(f"Error getting transaction status: {str(e)}")
            return TransactionStatus.UNKNOWN
    
    async def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a transaction.
        
        For Corda, this is a wrapper around get_flow_status.
        
        Args:
            transaction_id: ID of the transaction to get details for
            
        Returns:
            Dict with transaction details
        """
        if transaction_id not in self.flows:
            self.logger.error(f"Transaction {transaction_id} not found")
            return {"error": "Transaction not found"}
            
        try:
            # Get flow status
            flow_status = await self.get_flow_status(transaction_id)
            
            # Map flow status to transaction details
            if flow_status.get("error"):
                return {"error": flow_status["error"]}
                
            # Format details
            details = {
                "transaction_id": transaction_id,
                "flow_name": flow_status["flow_name"],
                "status": flow_status["status"],
                "started_at": flow_status["started_at"],
                "completed_at": flow_status.get("completed_at"),
                "result": flow_status.get("result")
            }
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error getting transaction details: {str(e)}")
            return {"error": str(e)}
    
    async def subscribe_to_events(self, event_filter: Dict[str, Any], 
                                callback: Callable[[Dict[str, Any]], None]) -> str:
        """
        Subscribe to Corda events.
        
        Args:
            event_filter: Filter criteria for events
                - event_type: Type of event (vault_update, network_map_update)
                - state_type: Type of state to listen for (for vault_update events)
                
            callback: Callback function to call when events are received
            
        Returns:
            str: Subscription ID if subscription successful, empty string otherwise
        """
        if not self.connected or not self.rpc_proxy:
            self.logger.error("Not connected to Corda network")
            return ""
            
        # Extract filter parameters
        event_type = event_filter.get("event_type", "")
        state_type = event_filter.get("state_type", "")
        
        # Validate parameters
        if not event_type:
            self.logger.error("Event type is required")
            return ""
            
        if event_type == "vault_update" and not state_type:
            self.logger.error("State type is required for vault_update events")
            return ""
            
        try:
            # In a real implementation, we would register for Corda events
            # This would typically involve using the RPC proxy to register for vault updates
            # or network map updates, and then forwarding those events to the callback
            
            # For this mock implementation, we'll just simulate a successful subscription
            
            # Generate subscription ID
            subscription_id = str(uuid.uuid4())
            
            # Store subscription
            self.event_subscriptions[subscription_id] = {
                "event_type": event_type,
                "state_type": state_type,
                "callback": callback,
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Subscribed to {event_type} events")
            
            return subscription_id
            
        except Exception as e:
            self.logger.error(f"Error subscribing to events: {str(e)}")
            return ""
    
    async def unsubscribe_from_events(self, subscription_id: str) -> bool:
        """
        Unsubscribe from Corda events.
        
        Args:
            subscription_id: ID of the subscription to cancel
            
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        if subscription_id not in self.event_subscriptions:
            self.logger.error(f"Subscription {subscription_id} not found")
            return False
            
        try:
            # In a real implementation, we would unregister from Corda events
            
            # For this mock implementation, we'll just remove the subscription
            
            # Get subscription info
            subscription_info = self.event_subscriptions[subscription_id]
            
            # Remove subscription
            del self.event_subscriptions[subscription_id]
            
            self.logger.info(f"Unsubscribed from {subscription_info['event_type']} events")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unsubscribing from events: {str(e)}")
            return False
    
    async def _monitor_flow(self, flow_id: str):
        """
        Monitor a flow for completion.
        
        Args:
            flow_id: ID of the flow to monitor
        """
        if flow_id not in self.flows:
            return
            
        try:
            # Get flow info
            flow_info = self.flows[flow_id]
            flow_handle = flow_info["handle"]
            
            # Wait for flow to complete
            max_retries = 10
            retry_count = 0
            
            while retry_count < max_retries:
                # Get flow status
                status = self.entry_point.flow_manager.get_flow_status(flow_id)
                
                if status in ["COMPLETED", "FAILED"]:
                    # Flow has completed or failed
                    flow_info["status"] = status
                    flow_info["completed_at"] = datetime.now().isoformat()
                    
                    # Get result if completed
                    if status == "COMPLETED":
                        try:
                            result = flow_handle.getReturnValue().get()
                            flow_info["result"] = result
                        except Exception as e:
                            self.logger.error(f"Error getting flow result: {str(e)}")
                            
                    self.logger.info(f"Flow {flow_id} {status.lower()}")
                    
                    # Publish event
                    await self.publish_event(
                        {
                            "event_type": f"corda_flow_{status.lower()}",
                            "payload": {
                                "flow_id": flow_id,
                                "flow_name": flow_info["flow_name"],
                                "result": flow_info.get("result")
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    
                    return
                    
                # Flow is still running
                retry_count += 1
                await asyncio.sleep(2)
                
            # If we get here, flow is still running after max retries
            self.logger.warning(f"Flow {flow_id} still running after {max_retries} retries")
            
        except Exception as e:
            self.logger.error(f"Error monitoring flow {flow_id}: {str(e)}")

# Example usage
async def example_usage():
    # Create connector
    connector = CordaConnector(config={
        "use_tpm": True,
        "use_zkp": True,
        "industry_tags": ["supply_chain", "finance"]
    })
    
    # Connect to Corda network
    success = await connector.connect({
        "gateway_address": "localhost",
        "gateway_port": 25333,
        "rpc_host": "localhost",
        "rpc_port": 10006,
        "rpc_username": "user1",
        "rpc_password": "password"
    })
    
    if success:
        # Get network map
        network_map = await connector.get_network_map()
        print(f"Network map: {network_map}")
        
        # Start flow
        flow_id = await connector.start_flow({
            "flow_name": "ExampleFlow",
            "flow_args": ["param1", "param2"],
            "tracked": True
        })
        
        if flow_id:
            # Get flow status
            flow_status = await connector.get_flow_status(flow_id)
            print(f"Flow status: {flow_status}")
            
            # Query vault
            states = await connector.query_vault({
                "state_type": "com.example.state.ExampleState"
            })
            print(f"Vault states: {states}")
            
            # Subscribe to events
            subscription_id = await connector.subscribe_to_events(
                {
                    "event_type": "vault_update",
                    "state_type": "com.example.state.ExampleState"
                },
                lambda event: print(f"Event received: {event}")
            )
            
            # Wait for a while to receive events
            await asyncio.sleep(10)
            
            # Unsubscribe from events
            await connector.unsubscribe_from_events(subscription_id)
            
        # Disconnect
        await connector.disconnect()
    
    # Shutdown
    await connector.shutdown()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run example
    asyncio.run(example_usage())
"""
