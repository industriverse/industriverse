"""
Hyperledger Fabric Blockchain Connector for Industriverse Protocol Layer

This module provides a comprehensive connector for integrating Hyperledger Fabric blockchain
with the Industriverse Protocol Layer. It enables seamless communication between
Hyperledger Fabric networks and the protocol-native architecture of Industriverse.

Features:
- Connection to Hyperledger Fabric networks
- Channel management and chaincode operations
- Transaction creation, submission, and monitoring
- Chaincode deployment and interaction
- Event subscription and notification
- Identity and certificate management
- Security integration with EKIS framework including ZKP
- Comprehensive error handling and diagnostics
- Support for multiple Fabric versions (1.4, 2.x)

Dependencies:
- fabric-sdk-py (Hyperledger Fabric Python SDK)
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

# Import Hyperledger Fabric libraries
try:
    import hfc
    from hfc.fabric import Client
    from hfc.fabric.user import create_user
    from hfc.fabric.transaction.tx_context import create_tx_context
    from hfc.fabric.transaction.tx_proposal_request import create_tx_prop_req, CC_TYPE_GOLANG, CC_INSTANTIATE, CC_INSTALL, CC_INVOKE, CC_QUERY
    HAS_FABRIC = True
except ImportError:
    logging.warning("Hyperledger Fabric SDK not found. Using mock implementation.")
    HAS_FABRIC = False
    
    # Mock implementation for development
    class MockClient:
        def __init__(self, net_profile=None):
            self.channels = {}
            self.users = {}
            self.peers = {}
            self.orderers = {}
            self.cas = {}
            self.chaincodes = {}
            self.net_profile = net_profile
            
        def new_channel(self, name):
            self.channels[name] = MockChannel(name)
            return self.channels[name]
            
        def get_user(self, org_name, name):
            user_id = f"{org_name}_{name}"
            if user_id in self.users:
                return self.users[user_id]
            return None
            
        def set_user(self, org_name, name, user):
            user_id = f"{org_name}_{name}"
            self.users[user_id] = user
            
        def new_peer(self, endpoint, tls_cacerts=None, opts=None):
            peer_id = str(uuid.uuid4())
            self.peers[peer_id] = MockPeer(endpoint)
            return self.peers[peer_id]
            
        def new_orderer(self, endpoint, tls_cacerts=None, opts=None):
            orderer_id = str(uuid.uuid4())
            self.orderers[orderer_id] = MockOrderer(endpoint)
            return self.orderers[orderer_id]
            
        def new_ca(self, endpoint, tls_cacerts=None, opts=None):
            ca_id = str(uuid.uuid4())
            self.cas[ca_id] = MockCA(endpoint)
            return self.cas[ca_id]
            
    class MockChannel:
        def __init__(self, name):
            self.name = name
            self.peers = {}
            self.orderers = {}
            self.chaincodes = {}
            
        def add_peer(self, peer):
            peer_id = str(uuid.uuid4())
            self.peers[peer_id] = peer
            return peer_id
            
        def add_orderer(self, orderer):
            orderer_id = str(uuid.uuid4())
            self.orderers[orderer_id] = orderer
            return orderer_id
            
        def join_channel(self, requestor):
            return {"status": "SUCCESS"}
            
        def query_info(self, requestor):
            return {
                "height": 10,
                "currentBlockHash": "0x1234567890abcdef",
                "previousBlockHash": "0xabcdef1234567890"
            }
            
        def query_block(self, block_number, requestor):
            return {
                "header": {
                    "number": block_number,
                    "previous_hash": "0xabcdef1234567890",
                    "data_hash": "0x1234567890abcdef"
                },
                "data": {
                    "data": []
                },
                "metadata": {
                    "metadata": []
                }
            }
            
        def query_transaction(self, tx_id, requestor):
            return {
                "transaction_id": tx_id,
                "status": "VALID",
                "timestamp": int(datetime.now().timestamp())
            }
            
        def query_instantiated_chaincodes(self, requestor):
            return {
                "chaincodes": [
                    {
                        "name": "example_cc",
                        "version": "1.0",
                        "path": "github.com/example_cc"
                    }
                ]
            }
            
        def query_installed_chaincodes(self, requestor, peer):
            return {
                "chaincodes": [
                    {
                        "name": "example_cc",
                        "version": "1.0",
                        "path": "github.com/example_cc"
                    }
                ]
            }
            
        def install_chaincode(self, requestor, cc_path, cc_name, cc_version, cc_type="golang"):
            chaincode_id = f"{cc_name}_{cc_version}"
            self.chaincodes[chaincode_id] = {
                "name": cc_name,
                "version": cc_version,
                "path": cc_path,
                "type": cc_type,
                "installed": True,
                "instantiated": False
            }
            return {"status": "SUCCESS"}
            
        def instantiate_chaincode(self, requestor, cc_name, cc_version, args=None, cc_endorsement_policy=None):
            chaincode_id = f"{cc_name}_{cc_version}"
            if chaincode_id in self.chaincodes:
                self.chaincodes[chaincode_id]["instantiated"] = True
                return {"status": "SUCCESS", "txid": str(uuid.uuid4())}
            return {"status": "FAILURE", "info": "Chaincode not installed"}
            
        def invoke_chaincode(self, requestor, cc_name, args, cc_pattern=None):
            tx_id = str(uuid.uuid4())
            return {"status": "SUCCESS", "txid": tx_id}
            
        def query_chaincode(self, requestor, cc_name, args, cc_pattern=None):
            return {"response": {"status": 200, "payload": "mock_result"}}
            
    class MockPeer:
        def __init__(self, endpoint):
            self.endpoint = endpoint
            
    class MockOrderer:
        def __init__(self, endpoint):
            self.endpoint = endpoint
            
    class MockCA:
        def __init__(self, endpoint):
            self.endpoint = endpoint
            
        def enroll(self, enrollment_id, enrollment_secret):
            return {
                "enrollmentCert": "-----BEGIN CERTIFICATE-----\nMOCK_CERTIFICATE\n-----END CERTIFICATE-----",
                "caCertChain": "-----BEGIN CERTIFICATE-----\nMOCK_CA_CERTIFICATE\n-----END CERTIFICATE-----"
            }
            
        def register(self, enrollmentID, enrollmentSecret, role, attrs=None):
            return {"secret": "mock_secret"}
            
    # Create mock classes to simulate Fabric SDK API
    Client = MockClient
    
    def create_user(name, org, state_store, msp_id, crypto_suite):
        return {"name": name, "org": org, "msp_id": msp_id}
        
    def create_tx_context(user, crypto):
        return {"user": user, "tx_id": str(uuid.uuid4())}
        
    def create_tx_prop_req(prop_type, cc_name, cc_version, args, cc_type="golang"):
        return {
            "prop_type": prop_type,
            "cc_name": cc_name,
            "cc_version": cc_version,
            "args": args,
            "cc_type": cc_type
        }
        
    CC_TYPE_GOLANG = "golang"
    CC_INSTANTIATE = "instantiate"
    CC_INSTALL = "install"
    CC_INVOKE = "invoke"
    CC_QUERY = "query"

class HyperledgerFabricConnector(BlockchainConnectorBase):
    """
    Hyperledger Fabric Blockchain Connector for Industriverse Protocol Layer.
    
    This connector enables bidirectional communication between Hyperledger Fabric blockchain
    networks and the Industriverse Protocol Layer, translating between Fabric
    protocol and Industriverse's protocol-native architecture.
    """
    
    def __init__(self, component_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Hyperledger Fabric connector.
        
        Args:
            component_id: Unique identifier for this connector instance
            config: Configuration parameters for the connector
        """
        super().__init__(component_id, BlockchainType.HYPERLEDGER_FABRIC, config)
        
        # Add Fabric-specific capabilities
        self.add_capability("fabric_channel_management", "Manage Fabric channels")
        self.add_capability("fabric_chaincode_operations", "Perform chaincode operations")
        self.add_capability("fabric_identity_management", "Manage Fabric identities")
        self.add_capability("fabric_event_subscription", "Subscribe to Fabric events")
        
        # Initialize Fabric client
        self.client = None
        self.net_profile = None
        
        # Initialize channel management
        self.channels = {}
        
        # Initialize user management
        self.users = {}
        
        # Initialize chaincode management
        self.chaincodes = {}
        
        # Initialize event listeners
        self.event_listeners = {}
        
        self.logger.info("Hyperledger Fabric Blockchain Connector initialized")
    
    async def connect(self, connection_params: Dict[str, Any]) -> bool:
        """
        Connect to a Hyperledger Fabric network.
        
        Args:
            connection_params: Connection parameters
                - net_profile: Path to network profile or network profile object
                - org_name: Organization name
                - user_name: User name
                - channel_name: Default channel name (optional)
                
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Extract connection parameters
            net_profile = connection_params.get("net_profile", "")
            org_name = connection_params.get("org_name", "")
            user_name = connection_params.get("user_name", "")
            channel_name = connection_params.get("channel_name", "")
            
            # Validate parameters
            if not net_profile:
                self.logger.error("Network profile is required")
                return False
                
            if not org_name:
                self.logger.error("Organization name is required")
                return False
                
            if not user_name:
                self.logger.error("User name is required")
                return False
                
            # Load network profile if it's a path
            if isinstance(net_profile, str) and os.path.exists(net_profile):
                with open(net_profile, "r") as f:
                    self.net_profile = json.load(f)
            else:
                self.net_profile = net_profile
                
            # Create Fabric client
            self.client = Client(net_profile=self.net_profile)
            
            # Get user
            user = self.client.get_user(org_name, user_name)
            if not user:
                self.logger.error(f"User {user_name} not found in organization {org_name}")
                return False
                
            # Store user
            self.users["default"] = {
                "org_name": org_name,
                "user_name": user_name,
                "user": user
            }
            
            # Connect to default channel if provided
            if channel_name:
                channel = self.client.new_channel(channel_name)
                if not channel:
                    self.logger.error(f"Failed to create channel {channel_name}")
                    return False
                    
                # Store channel
                self.channels["default"] = {
                    "name": channel_name,
                    "channel": channel
                }
                
            # Update connection state
            self.connected = True
            self.connection_info = {
                "net_profile": "loaded" if self.net_profile else "not_loaded",
                "org_name": org_name,
                "user_name": user_name,
                "default_channel": channel_name,
                "connected_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Connected to Hyperledger Fabric network as {user_name}@{org_name}")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "fabric_connected",
                    "payload": {
                        "org_name": org_name,
                        "user_name": user_name,
                        "default_channel": channel_name
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to Hyperledger Fabric network: {str(e)}")
            self.connected = False
            self.client = None
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the Hyperledger Fabric network.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.warning("Not connected to Hyperledger Fabric network")
            return False
            
        try:
            # Clean up resources
            
            # Clean up event listeners
            for listener_id, listener_info in list(self.event_listeners.items()):
                await self.unsubscribe_from_events(listener_id)
                
            # Reset connection state
            self.connected = False
            self.client = None
            self.channels = {}
            
            self.logger.info("Disconnected from Hyperledger Fabric network")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "fabric_disconnected",
                    "payload": {
                        "org_name": self.connection_info.get("org_name", ""),
                        "user_name": self.connection_info.get("user_name", "")
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from Hyperledger Fabric network: {str(e)}")
            return False
    
    async def is_connected(self) -> bool:
        """
        Check if connected to the Hyperledger Fabric network.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connected and self.client is not None
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the current connection.
        
        Returns:
            Dict with connection information
        """
        if not self.connected or not self.client:
            return {"connected": False}
            
        # Get default channel info
        channel_info = {}
        if "default" in self.channels:
            channel_name = self.channels["default"]["name"]
            channel = self.channels["default"]["channel"]
            
            try:
                # Get channel info
                user_info = self.users["default"]
                channel_query_info = channel.query_info(user_info["user"])
                
                channel_info = {
                    "name": channel_name,
                    "height": channel_query_info["height"],
                    "current_block_hash": channel_query_info["currentBlockHash"],
                    "previous_block_hash": channel_query_info["previousBlockHash"]
                }
            except Exception as e:
                self.logger.error(f"Error getting channel info: {str(e)}")
                channel_info = {"name": channel_name}
                
        # Return connection info
        return {
            "connected": True,
            "org_name": self.connection_info.get("org_name", ""),
            "user_name": self.connection_info.get("user_name", ""),
            "default_channel": self.connection_info.get("default_channel", ""),
            "channel_info": channel_info,
            "connected_at": self.connection_info.get("connected_at", "")
        }
    
    async def create_channel(self, channel_params: Dict[str, Any]) -> bool:
        """
        Create a new Fabric channel.
        
        Args:
            channel_params: Channel parameters
                - channel_name: Name of the channel to create
                - channel_config_path: Path to channel configuration file
                - orderer_name: Name of the orderer to use
                
        Returns:
            bool: True if channel creation successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to Hyperledger Fabric network")
            return False
            
        # Extract channel parameters
        channel_name = channel_params.get("channel_name", "")
        channel_config_path = channel_params.get("channel_config_path", "")
        orderer_name = channel_params.get("orderer_name", "")
        
        # Validate parameters
        if not channel_name:
            self.logger.error("Channel name is required")
            return False
            
        if not channel_config_path:
            self.logger.error("Channel configuration path is required")
            return False
            
        if not orderer_name:
            self.logger.error("Orderer name is required")
            return False
            
        try:
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return False
                
            user_info = self.users["default"]
            
            # Create channel
            response = self.client.create_channel(
                channel_name=channel_name,
                requestor=user_info["user"],
                config_yaml=channel_config_path,
                orderer_name=orderer_name
            )
            
            if response["status"] != "SUCCESS":
                self.logger.error(f"Failed to create channel: {response.get('info', '')}")
                return False
                
            # Create channel object
            channel = self.client.new_channel(channel_name)
            
            # Store channel
            self.channels[channel_name] = {
                "name": channel_name,
                "channel": channel
            }
            
            self.logger.info(f"Created channel {channel_name}")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "fabric_channel_created",
                    "payload": {
                        "channel_name": channel_name
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating channel: {str(e)}")
            return False
    
    async def join_channel(self, channel_params: Dict[str, Any]) -> bool:
        """
        Join a Fabric channel.
        
        Args:
            channel_params: Channel parameters
                - channel_name: Name of the channel to join
                - peer_names: List of peer names to join the channel
                
        Returns:
            bool: True if channel join successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to Hyperledger Fabric network")
            return False
            
        # Extract channel parameters
        channel_name = channel_params.get("channel_name", "")
        peer_names = channel_params.get("peer_names", [])
        
        # Validate parameters
        if not channel_name:
            self.logger.error("Channel name is required")
            return False
            
        if not peer_names:
            self.logger.error("Peer names are required")
            return False
            
        try:
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return False
                
            user_info = self.users["default"]
            
            # Get or create channel object
            if channel_name in self.channels:
                channel = self.channels[channel_name]["channel"]
            else:
                channel = self.client.new_channel(channel_name)
                self.channels[channel_name] = {
                    "name": channel_name,
                    "channel": channel
                }
                
            # Join channel for each peer
            for peer_name in peer_names:
                response = channel.join_channel(
                    requestor=user_info["user"],
                    peer_names=[peer_name]
                )
                
                if response["status"] != "SUCCESS":
                    self.logger.error(f"Failed to join channel for peer {peer_name}: {response.get('info', '')}")
                    return False
                    
            self.logger.info(f"Joined channel {channel_name} for peers {peer_names}")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "fabric_channel_joined",
                    "payload": {
                        "channel_name": channel_name,
                        "peer_names": peer_names
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error joining channel: {str(e)}")
            return False
    
    async def install_chaincode(self, chaincode_params: Dict[str, Any]) -> bool:
        """
        Install chaincode on Fabric peers.
        
        Args:
            chaincode_params: Chaincode parameters
                - channel_name: Name of the channel
                - cc_path: Path to chaincode source
                - cc_name: Name of the chaincode
                - cc_version: Version of the chaincode
                - cc_type: Type of the chaincode (golang, node, java)
                - peer_names: List of peer names to install the chaincode on
                
        Returns:
            bool: True if chaincode installation successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to Hyperledger Fabric network")
            return False
            
        # Extract chaincode parameters
        channel_name = chaincode_params.get("channel_name", "")
        cc_path = chaincode_params.get("cc_path", "")
        cc_name = chaincode_params.get("cc_name", "")
        cc_version = chaincode_params.get("cc_version", "")
        cc_type = chaincode_params.get("cc_type", "golang")
        peer_names = chaincode_params.get("peer_names", [])
        
        # Validate parameters
        if not channel_name:
            self.logger.error("Channel name is required")
            return False
            
        if not cc_path:
            self.logger.error("Chaincode path is required")
            return False
            
        if not cc_name:
            self.logger.error("Chaincode name is required")
            return False
            
        if not cc_version:
            self.logger.error("Chaincode version is required")
            return False
            
        if not peer_names:
            self.logger.error("Peer names are required")
            return False
            
        try:
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return False
                
            user_info = self.users["default"]
            
            # Get channel
            if channel_name not in self.channels:
                self.logger.error(f"Channel {channel_name} not found")
                return False
                
            channel = self.channels[channel_name]["channel"]
            
            # Install chaincode on each peer
            for peer_name in peer_names:
                response = channel.install_chaincode(
                    requestor=user_info["user"],
                    peers=[peer_name],
                    cc_path=cc_path,
                    cc_name=cc_name,
                    cc_version=cc_version,
                    cc_type=cc_type
                )
                
                if response["status"] != "SUCCESS":
                    self.logger.error(f"Failed to install chaincode on peer {peer_name}: {response.get('info', '')}")
                    return False
                    
            # Generate chaincode ID
            chaincode_id = f"{cc_name}_{cc_version}"
            
            # Store chaincode
            self.chaincodes[chaincode_id] = {
                "name": cc_name,
                "version": cc_version,
                "path": cc_path,
                "type": cc_type,
                "channel": channel_name,
                "installed_peers": peer_names,
                "instantiated": False,
                "installed_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Installed chaincode {cc_name} v{cc_version} on peers {peer_names}")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "fabric_chaincode_installed",
                    "payload": {
                        "chaincode_id": chaincode_id,
                        "channel_name": channel_name,
                        "cc_name": cc_name,
                        "cc_version": cc_version,
                        "peer_names": peer_names
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing chaincode: {str(e)}")
            return False
    
    async def instantiate_chaincode(self, chaincode_params: Dict[str, Any]) -> str:
        """
        Instantiate chaincode on a Fabric channel.
        
        Args:
            chaincode_params: Chaincode parameters
                - channel_name: Name of the channel
                - cc_name: Name of the chaincode
                - cc_version: Version of the chaincode
                - args: Arguments for chaincode instantiation
                - cc_endorsement_policy: Endorsement policy (optional)
                - collections_config: Private data collections config (optional)
                - peer_names: List of peer names to instantiate the chaincode on
                
        Returns:
            str: Transaction ID if instantiation successful, empty string otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to Hyperledger Fabric network")
            return ""
            
        # Extract chaincode parameters
        channel_name = chaincode_params.get("channel_name", "")
        cc_name = chaincode_params.get("cc_name", "")
        cc_version = chaincode_params.get("cc_version", "")
        args = chaincode_params.get("args", [])
        cc_endorsement_policy = chaincode_params.get("cc_endorsement_policy", None)
        collections_config = chaincode_params.get("collections_config", None)
        peer_names = chaincode_params.get("peer_names", [])
        
        # Validate parameters
        if not channel_name:
            self.logger.error("Channel name is required")
            return ""
            
        if not cc_name:
            self.logger.error("Chaincode name is required")
            return ""
            
        if not cc_version:
            self.logger.error("Chaincode version is required")
            return ""
            
        if not peer_names:
            self.logger.error("Peer names are required")
            return ""
            
        try:
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return ""
                
            user_info = self.users["default"]
            
            # Get channel
            if channel_name not in self.channels:
                self.logger.error(f"Channel {channel_name} not found")
                return ""
                
            channel = self.channels[channel_name]["channel"]
            
            # Instantiate chaincode
            response = channel.instantiate_chaincode(
                requestor=user_info["user"],
                peers=peer_names,
                cc_name=cc_name,
                cc_version=cc_version,
                args=args,
                cc_endorsement_policy=cc_endorsement_policy,
                collections_config=collections_config
            )
            
            if response["status"] != "SUCCESS":
                self.logger.error(f"Failed to instantiate chaincode: {response.get('info', '')}")
                return ""
                
            # Get transaction ID
            tx_id = response["txid"]
            
            # Generate chaincode ID
            chaincode_id = f"{cc_name}_{cc_version}"
            
            # Update chaincode
            if chaincode_id in self.chaincodes:
                self.chaincodes[chaincode_id]["instantiated"] = True
                self.chaincodes[chaincode_id]["instantiated_at"] = datetime.now().isoformat()
            else:
                self.chaincodes[chaincode_id] = {
                    "name": cc_name,
                    "version": cc_version,
                    "channel": channel_name,
                    "instantiated": True,
                    "instantiated_at": datetime.now().isoformat()
                }
                
            # Generate transaction ID
            transaction_id = str(uuid.uuid4())
            
            # Store transaction
            self.transactions[transaction_id] = {
                "tx_id": tx_id,
                "type": "instantiate_chaincode",
                "chaincode_id": chaincode_id,
                "channel": channel_name,
                "status": TransactionStatus.CONFIRMED,
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Instantiated chaincode {cc_name} v{cc_version} on channel {channel_name}")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "fabric_chaincode_instantiated",
                    "payload": {
                        "transaction_id": transaction_id,
                        "tx_id": tx_id,
                        "chaincode_id": chaincode_id,
                        "channel_name": channel_name,
                        "cc_name": cc_name,
                        "cc_version": cc_version
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return transaction_id
            
        except Exception as e:
            self.logger.error(f"Error instantiating chaincode: {str(e)}")
            return ""
    
    async def invoke_chaincode(self, chaincode_params: Dict[str, Any]) -> str:
        """
        Invoke a chaincode function.
        
        Args:
            chaincode_params: Chaincode parameters
                - channel_name: Name of the channel
                - cc_name: Name of the chaincode
                - fcn: Function name to invoke
                - args: Arguments for the function
                - peer_names: List of peer names to send the invocation to
                
        Returns:
            str: Transaction ID if invocation successful, empty string otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to Hyperledger Fabric network")
            return ""
            
        # Extract chaincode parameters
        channel_name = chaincode_params.get("channel_name", "")
        cc_name = chaincode_params.get("cc_name", "")
        fcn = chaincode_params.get("fcn", "")
        args = chaincode_params.get("args", [])
        peer_names = chaincode_params.get("peer_names", [])
        
        # Validate parameters
        if not channel_name:
            self.logger.error("Channel name is required")
            return ""
            
        if not cc_name:
            self.logger.error("Chaincode name is required")
            return ""
            
        if not fcn:
            self.logger.error("Function name is required")
            return ""
            
        if not peer_names:
            self.logger.error("Peer names are required")
            return ""
            
        try:
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return ""
                
            user_info = self.users["default"]
            
            # Get channel
            if channel_name not in self.channels:
                self.logger.error(f"Channel {channel_name} not found")
                return ""
                
            channel = self.channels[channel_name]["channel"]
            
            # Prepare args
            cc_args = [fcn] + args
            
            # Invoke chaincode
            response = channel.invoke_chaincode(
                requestor=user_info["user"],
                peers=peer_names,
                cc_name=cc_name,
                args=cc_args
            )
            
            if response["status"] != "SUCCESS":
                self.logger.error(f"Failed to invoke chaincode: {response.get('info', '')}")
                return ""
                
            # Get transaction ID
            tx_id = response["txid"]
            
            # Generate transaction ID
            transaction_id = str(uuid.uuid4())
            
            # Store transaction
            self.transactions[transaction_id] = {
                "tx_id": tx_id,
                "type": "invoke_chaincode",
                "channel": channel_name,
                "chaincode": cc_name,
                "function": fcn,
                "args": args,
                "status": TransactionStatus.PENDING,
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Invoked chaincode {cc_name} function {fcn} on channel {channel_name}")
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": "fabric_chaincode_invoked",
                    "payload": {
                        "transaction_id": transaction_id,
                        "tx_id": tx_id,
                        "channel_name": channel_name,
                        "cc_name": cc_name,
                        "function": fcn
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Start monitoring transaction
            asyncio.create_task(self._monitor_transaction(transaction_id))
            
            return transaction_id
            
        except Exception as e:
            self.logger.error(f"Error invoking chaincode: {str(e)}")
            return ""
    
    async def query_chaincode(self, chaincode_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query a chaincode function.
        
        Args:
            chaincode_params: Chaincode parameters
                - channel_name: Name of the channel
                - cc_name: Name of the chaincode
                - fcn: Function name to query
                - args: Arguments for the function
                - peer_names: List of peer names to send the query to
                
        Returns:
            Dict with query result
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to Hyperledger Fabric network")
            return {"error": "Not connected to Hyperledger Fabric network"}
            
        # Extract chaincode parameters
        channel_name = chaincode_params.get("channel_name", "")
        cc_name = chaincode_params.get("cc_name", "")
        fcn = chaincode_params.get("fcn", "")
        args = chaincode_params.get("args", [])
        peer_names = chaincode_params.get("peer_names", [])
        
        # Validate parameters
        if not channel_name:
            self.logger.error("Channel name is required")
            return {"error": "Channel name is required"}
            
        if not cc_name:
            self.logger.error("Chaincode name is required")
            return {"error": "Chaincode name is required"}
            
        if not fcn:
            self.logger.error("Function name is required")
            return {"error": "Function name is required"}
            
        if not peer_names:
            self.logger.error("Peer names are required")
            return {"error": "Peer names are required"}
            
        try:
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return {"error": "Default user not found"}
                
            user_info = self.users["default"]
            
            # Get channel
            if channel_name not in self.channels:
                self.logger.error(f"Channel {channel_name} not found")
                return {"error": f"Channel {channel_name} not found"}
                
            channel = self.channels[channel_name]["channel"]
            
            # Prepare args
            cc_args = [fcn] + args
            
            # Query chaincode
            response = channel.query_chaincode(
                requestor=user_info["user"],
                peers=[peer_names[0]],  # Use first peer for query
                cc_name=cc_name,
                args=cc_args
            )
            
            # Parse response
            if response["response"]["status"] != 200:
                self.logger.error(f"Failed to query chaincode: {response['response'].get('message', '')}")
                return {"error": response["response"].get("message", "Unknown error")}
                
            # Get payload
            payload = response["response"]["payload"]
            
            # Try to parse payload as JSON
            try:
                result = json.loads(payload)
            except json.JSONDecodeError:
                result = payload
                
            self.logger.info(f"Queried chaincode {cc_name} function {fcn} on channel {channel_name}")
            
            return {
                "channel_name": channel_name,
                "cc_name": cc_name,
                "function": fcn,
                "args": args,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error querying chaincode: {str(e)}")
            return {"error": str(e)}
    
    async def get_transaction_status(self, transaction_id: str) -> TransactionStatus:
        """
        Get the status of a transaction.
        
        Args:
            transaction_id: ID of the transaction to check
            
        Returns:
            TransactionStatus: Status of the transaction
        """
        if transaction_id not in self.transactions:
            self.logger.error(f"Transaction {transaction_id} not found")
            return TransactionStatus.UNKNOWN
            
        try:
            # Get transaction info
            tx_info = self.transactions[transaction_id]
            
            # If we already know the status is confirmed or failed, return it
            if tx_info["status"] in [TransactionStatus.CONFIRMED, TransactionStatus.FAILED]:
                return tx_info["status"]
                
            # Otherwise, check the current status
            tx_id = tx_info["tx_id"]
            channel_name = tx_info["channel"]
            
            # Get channel
            if channel_name not in self.channels:
                self.logger.error(f"Channel {channel_name} not found")
                return TransactionStatus.UNKNOWN
                
            channel = self.channels[channel_name]["channel"]
            
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return TransactionStatus.UNKNOWN
                
            user_info = self.users["default"]
            
            # Query transaction
            try:
                tx_info = channel.query_transaction(
                    requestor=user_info["user"],
                    tx_id=tx_id
                )
                
                # Update status based on transaction info
                if tx_info["status"] == "VALID":
                    tx_info["status"] = TransactionStatus.CONFIRMED
                    return TransactionStatus.CONFIRMED
                else:
                    tx_info["status"] = TransactionStatus.FAILED
                    return TransactionStatus.FAILED
            except Exception:
                # Transaction not found or still pending
                return TransactionStatus.PENDING
                
        except Exception as e:
            self.logger.error(f"Error getting transaction status: {str(e)}")
            return TransactionStatus.UNKNOWN
    
    async def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a transaction.
        
        Args:
            transaction_id: ID of the transaction to get details for
            
        Returns:
            Dict with transaction details
        """
        if transaction_id not in self.transactions:
            self.logger.error(f"Transaction {transaction_id} not found")
            return {"error": "Transaction not found"}
            
        try:
            # Get transaction info
            tx_info = self.transactions[transaction_id]
            tx_id = tx_info["tx_id"]
            channel_name = tx_info["channel"]
            
            # Get channel
            if channel_name not in self.channels:
                self.logger.error(f"Channel {channel_name} not found")
                return {"error": f"Channel {channel_name} not found"}
                
            channel = self.channels[channel_name]["channel"]
            
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return {"error": "Default user not found"}
                
            user_info = self.users["default"]
            
            # Query transaction
            try:
                fabric_tx_info = channel.query_transaction(
                    requestor=user_info["user"],
                    tx_id=tx_id
                )
                
                # Format details
                details = {
                    "transaction_id": transaction_id,
                    "tx_id": tx_id,
                    "channel": channel_name,
                    "type": tx_info["type"],
                    "status": tx_info["status"].value,
                    "created_at": tx_info["created_at"]
                }
                
                # Add type-specific details
                if tx_info["type"] == "invoke_chaincode":
                    details.update({
                        "chaincode": tx_info["chaincode"],
                        "function": tx_info["function"],
                        "args": tx_info["args"]
                    })
                elif tx_info["type"] == "instantiate_chaincode":
                    details.update({
                        "chaincode_id": tx_info["chaincode_id"]
                    })
                    
                # Add Fabric transaction details
                details.update({
                    "fabric_status": fabric_tx_info["status"],
                    "timestamp": fabric_tx_info["timestamp"]
                })
                
                return details
                
            except Exception as e:
                # Transaction not found or still pending
                return {
                    "transaction_id": transaction_id,
                    "tx_id": tx_id,
                    "channel": channel_name,
                    "type": tx_info["type"],
                    "status": tx_info["status"].value,
                    "created_at": tx_info["created_at"],
                    "fabric_status": "PENDING"
                }
                
        except Exception as e:
            self.logger.error(f"Error getting transaction details: {str(e)}")
            return {"error": str(e)}
    
    async def create_transaction(self, transaction_params: Dict[str, Any]) -> str:
        """
        Create a new blockchain transaction.
        
        For Fabric, this is a wrapper around invoke_chaincode.
        
        Args:
            transaction_params: Parameters for the transaction
                
        Returns:
            str: Transaction ID if creation successful, empty string otherwise
        """
        return await self.invoke_chaincode(transaction_params)
    
    async def subscribe_to_events(self, event_filter: Dict[str, Any], 
                                callback: Callable[[Dict[str, Any]], None]) -> str:
        """
        Subscribe to Fabric events.
        
        Args:
            event_filter: Filter criteria for events
                - channel_name: Name of the channel
                - event_type: Type of event (block, tx, chaincode)
                - chaincode_id: ID of the chaincode (for chaincode events)
                - event_name: Name of the event (for chaincode events)
                
            callback: Callback function to call when events are received
            
        Returns:
            str: Subscription ID if subscription successful, empty string otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to Hyperledger Fabric network")
            return ""
            
        # Extract filter parameters
        channel_name = event_filter.get("channel_name", "")
        event_type = event_filter.get("event_type", "")
        chaincode_id = event_filter.get("chaincode_id", "")
        event_name = event_filter.get("event_name", "")
        
        # Validate parameters
        if not channel_name:
            self.logger.error("Channel name is required")
            return ""
            
        if not event_type:
            self.logger.error("Event type is required")
            return ""
            
        if event_type == "chaincode" and (not chaincode_id or not event_name):
            self.logger.error("Chaincode ID and event name are required for chaincode events")
            return ""
            
        try:
            # Get channel
            if channel_name not in self.channels:
                self.logger.error(f"Channel {channel_name} not found")
                return ""
                
            channel = self.channels[channel_name]["channel"]
            
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return ""
                
            user_info = self.users["default"]
            
            # Create event hub
            peer_name = event_filter.get("peer_name", "peer0.org1.example.com")  # Default peer
            event_hub = channel.newChannelEventHub(peer_name, user_info["user"])
            
            # Generate subscription ID
            subscription_id = str(uuid.uuid4())
            
            # Register event listener based on type
            if event_type == "block":
                # Register for block events
                reg_id = event_hub.registerBlockEvent(
                    callback=lambda block: self._handle_event(subscription_id, "block", block, callback),
                    onError=lambda error: self.logger.error(f"Block event error: {error}")
                )
            elif event_type == "tx":
                # Register for transaction events
                reg_id = event_hub.registerTxEvent(
                    tx_id="all",  # Listen for all transactions
                    callback=lambda tx_id, status, block_number: self._handle_event(
                        subscription_id, "tx", {"tx_id": tx_id, "status": status, "block_number": block_number}, callback
                    ),
                    onError=lambda error: self.logger.error(f"Transaction event error: {error}")
                )
            elif event_type == "chaincode":
                # Register for chaincode events
                reg_id = event_hub.registerChaincodeEvent(
                    chaincode_id=chaincode_id,
                    event_name=event_name,
                    callback=lambda cc_event, block_number, tx_id, tx_status: self._handle_event(
                        subscription_id, "chaincode", {
                            "chaincode_id": chaincode_id,
                            "event_name": cc_event.event_name,
                            "payload": cc_event.payload,
                            "block_number": block_number,
                            "tx_id": tx_id,
                            "tx_status": tx_status
                        }, callback
                    ),
                    onError=lambda error: self.logger.error(f"Chaincode event error: {error}")
                )
            else:
                self.logger.error(f"Unsupported event type: {event_type}")
                return ""
                
            # Connect to event hub
            event_hub.connect()
            
            # Store event listener
            self.event_listeners[subscription_id] = {
                "channel_name": channel_name,
                "event_type": event_type,
                "event_hub": event_hub,
                "reg_id": reg_id,
                "callback": callback,
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Subscribed to {event_type} events on channel {channel_name}")
            
            return subscription_id
            
        except Exception as e:
            self.logger.error(f"Error subscribing to events: {str(e)}")
            return ""
    
    async def unsubscribe_from_events(self, subscription_id: str) -> bool:
        """
        Unsubscribe from Fabric events.
        
        Args:
            subscription_id: ID of the subscription to cancel
            
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        if subscription_id not in self.event_listeners:
            self.logger.error(f"Subscription {subscription_id} not found")
            return False
            
        try:
            # Get listener info
            listener_info = self.event_listeners[subscription_id]
            event_hub = listener_info["event_hub"]
            event_type = listener_info["event_type"]
            reg_id = listener_info["reg_id"]
            
            # Unregister based on event type
            if event_type == "block":
                event_hub.unregisterBlockEvent(reg_id)
            elif event_type == "tx":
                event_hub.unregisterTxEvent(reg_id)
            elif event_type == "chaincode":
                event_hub.unregisterChaincodeEvent(reg_id)
                
            # Disconnect from event hub
            event_hub.disconnect()
            
            # Remove listener
            del self.event_listeners[subscription_id]
            
            self.logger.info(f"Unsubscribed from {event_type} events")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unsubscribing from events: {str(e)}")
            return False
    
    async def _handle_event(self, subscription_id: str, event_type: str, event_data: Dict[str, Any], 
                          callback: Callable[[Dict[str, Any]], None]):
        """
        Handle an event from Fabric.
        
        Args:
            subscription_id: ID of the subscription
            event_type: Type of event
            event_data: Event data
            callback: Callback function to call
        """
        try:
            # Format event data
            event = {
                "subscription_id": subscription_id,
                "event_type": event_type,
                "data": event_data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Call callback
            await callback(event)
            
            # Publish event
            await self.publish_event(
                {
                    "event_type": f"fabric_{event_type}_event",
                    "payload": event,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error handling event: {str(e)}")
    
    async def _monitor_transaction(self, transaction_id: str):
        """
        Monitor a transaction for confirmation.
        
        Args:
            transaction_id: ID of the transaction to monitor
        """
        if transaction_id not in self.transactions:
            return
            
        try:
            # Get transaction info
            tx_info = self.transactions[transaction_id]
            tx_id = tx_info["tx_id"]
            channel_name = tx_info["channel"]
            
            # Get channel
            if channel_name not in self.channels:
                self.logger.error(f"Channel {channel_name} not found")
                return
                
            channel = self.channels[channel_name]["channel"]
            
            # Get default user
            if "default" not in self.users:
                self.logger.error("Default user not found")
                return
                
            user_info = self.users["default"]
            
            # Wait for transaction to be confirmed
            max_retries = 10
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Query transaction
                    tx_info = channel.query_transaction(
                        requestor=user_info["user"],
                        tx_id=tx_id
                    )
                    
                    # Update status based on transaction info
                    if tx_info["status"] == "VALID":
                        self.transactions[transaction_id]["status"] = TransactionStatus.CONFIRMED
                        status_str = "confirmed"
                    else:
                        self.transactions[transaction_id]["status"] = TransactionStatus.FAILED
                        status_str = "failed"
                        
                    self.logger.info(f"Transaction {tx_id} {status_str}")
                    
                    # Publish event
                    await self.publish_event(
                        {
                            "event_type": f"fabric_transaction_{status_str}",
                            "payload": {
                                "transaction_id": transaction_id,
                                "tx_id": tx_id,
                                "channel": channel_name
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    
                    return
                    
                except Exception:
                    # Transaction not found or still pending
                    retry_count += 1
                    await asyncio.sleep(2)
                    
            # If we get here, transaction is still pending after max retries
            self.logger.warning(f"Transaction {tx_id} still pending after {max_retries} retries")
            
        except Exception as e:
            self.logger.error(f"Error monitoring transaction {transaction_id}: {str(e)}")

# Example usage
async def example_usage():
    # Create connector
    connector = HyperledgerFabricConnector(config={
        "use_tpm": True,
        "use_zkp": True,
        "industry_tags": ["supply_chain", "manufacturing"]
    })
    
    # Connect to Fabric network
    success = await connector.connect({
        "net_profile": "/path/to/network-profile.json",
        "org_name": "Org1",
        "user_name": "Admin",
        "channel_name": "mychannel"
    })
    
    if success:
        # Install chaincode
        success = await connector.install_chaincode({
            "channel_name": "mychannel",
            "cc_path": "github.com/example_cc",
            "cc_name": "example_cc",
            "cc_version": "1.0",
            "cc_type": "golang",
            "peer_names": ["peer0.org1.example.com"]
        })
        
        if success:
            # Instantiate chaincode
            tx_id = await connector.instantiate_chaincode({
                "channel_name": "mychannel",
                "cc_name": "example_cc",
                "cc_version": "1.0",
                "args": ["init", "a", "100", "b", "200"],
                "peer_names": ["peer0.org1.example.com"]
            })
            
            if tx_id:
                # Query chaincode
                result = await connector.query_chaincode({
                    "channel_name": "mychannel",
                    "cc_name": "example_cc",
                    "fcn": "query",
                    "args": ["a"],
                    "peer_names": ["peer0.org1.example.com"]
                })
                print(f"Query result: {result}")
                
                # Invoke chaincode
                tx_id = await connector.invoke_chaincode({
                    "channel_name": "mychannel",
                    "cc_name": "example_cc",
                    "fcn": "invoke",
                    "args": ["a", "b", "10"],
                    "peer_names": ["peer0.org1.example.com"]
                })
                
                # Subscribe to events
                subscription_id = await connector.subscribe_to_events(
                    {
                        "channel_name": "mychannel",
                        "event_type": "chaincode",
                        "chaincode_id": "example_cc",
                        "event_name": "transfer"
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
