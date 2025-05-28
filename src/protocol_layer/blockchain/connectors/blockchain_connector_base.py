"""
Blockchain Connector Base for Industriverse Protocol Layer

This module provides the base classes and interfaces for blockchain integration
with the Industriverse Protocol Layer. It enables seamless communication between
blockchain networks and the protocol-native architecture of Industriverse.

Features:
- Abstract base classes for blockchain connectors
- Support for multiple blockchain platforms (Ethereum, Hyperledger Fabric, Corda)
- Transaction management and monitoring
- Smart contract interaction
- Event subscription and notification
- Security integration with EKIS framework
- Comprehensive error handling and diagnostics
- Support for on-chain and off-chain data management
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

# Import Protocol Layer base components
from protocols.protocol_base import ProtocolComponent
from protocols.message_formats import MessageFactory, MessagePriority, MessageType
from protocols.discovery_service import DiscoveryService

# Import EKIS security components
from security.ekis.tpm_integration import TPMSecurityProvider
from security.ekis.security_handler import EKISSecurityHandler
from security.ekis.zkp_handler import ZKPHandler

class BlockchainType(Enum):
    """Supported blockchain types."""
    ETHEREUM = "ethereum"
    HYPERLEDGER_FABRIC = "hyperledger_fabric"
    CORDA = "corda"
    QUORUM = "quorum"
    POLYGON = "polygon"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    CUSTOM = "custom"

class TransactionStatus(Enum):
    """Transaction status enum."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    UNKNOWN = "unknown"

class BlockchainConnectorBase(ProtocolComponent, ABC):
    """
    Abstract base class for blockchain connectors.
    
    This class defines the interface that all blockchain connectors must implement
    to integrate with the Industriverse Protocol Layer.
    """
    
    def __init__(self, component_id: Optional[str] = None, 
                 blockchain_type: BlockchainType = BlockchainType.CUSTOM,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the blockchain connector.
        
        Args:
            component_id: Unique identifier for this connector instance
            blockchain_type: Type of blockchain this connector interfaces with
            config: Configuration parameters for the connector
        """
        super().__init__(component_id or str(uuid.uuid4()), f"{blockchain_type.value}_connector")
        
        # Store blockchain type
        self.blockchain_type = blockchain_type
        
        # Add capabilities
        self.add_capability("blockchain_connection", "Connect to blockchain networks")
        self.add_capability("transaction_management", "Create and monitor transactions")
        self.add_capability("smart_contract_interaction", "Interact with smart contracts")
        self.add_capability("event_subscription", "Subscribe to blockchain events")
        
        # Initialize configuration
        self.config = config or {}
        self.logger = logging.getLogger(f"industriverse.protocol.blockchain.{self.component_id}")
        
        # Initialize connection state
        self.connected = False
        self.connection_info = {}
        
        # Initialize transaction tracking
        self.transactions = {}
        
        # Initialize event subscriptions
        self.event_subscriptions = {}
        self.event_callbacks = {}
        
        # Initialize security handler with ZKP support
        self.security_handler = EKISSecurityHandler(
            component_id=f"{self.component_id}_security",
            tpm_provider=TPMSecurityProvider() if self.config.get("use_tpm", True) else None,
            zkp_handler=ZKPHandler() if self.config.get("use_zkp", True) else None
        )
        
        # Register with discovery service
        self.discovery_service = DiscoveryService()
        self.discovery_service.register_component(
            self.component_id,
            f"{blockchain_type.value}_connector",
            {
                "protocols": ["blockchain", blockchain_type.value],
                "capabilities": list(self._capabilities.keys()),
                "industryTags": self.config.get("industry_tags", ["supply_chain", "manufacturing", "energy", "finance"])
            }
        )
        
        self.logger.info(f"{blockchain_type.value.capitalize()} Blockchain Connector {self.component_id} initialized")
    
    @abstractmethod
    async def connect(self, connection_params: Dict[str, Any]) -> bool:
        """
        Connect to the blockchain network.
        
        Args:
            connection_params: Connection parameters specific to the blockchain
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the blockchain network.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if connected to the blockchain network.
        
        Returns:
            bool: True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the current connection.
        
        Returns:
            Dict with connection information
        """
        pass
    
    @abstractmethod
    async def create_transaction(self, transaction_params: Dict[str, Any]) -> str:
        """
        Create a new blockchain transaction.
        
        Args:
            transaction_params: Parameters for the transaction
            
        Returns:
            str: Transaction ID if creation successful, empty string otherwise
        """
        pass
    
    @abstractmethod
    async def get_transaction_status(self, transaction_id: str) -> TransactionStatus:
        """
        Get the status of a transaction.
        
        Args:
            transaction_id: ID of the transaction to check
            
        Returns:
            TransactionStatus: Status of the transaction
        """
        pass
    
    @abstractmethod
    async def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a transaction.
        
        Args:
            transaction_id: ID of the transaction to get details for
            
        Returns:
            Dict with transaction details
        """
        pass
    
    @abstractmethod
    async def deploy_smart_contract(self, contract_params: Dict[str, Any]) -> str:
        """
        Deploy a smart contract to the blockchain.
        
        Args:
            contract_params: Parameters for the contract deployment
            
        Returns:
            str: Contract address/ID if deployment successful, empty string otherwise
        """
        pass
    
    @abstractmethod
    async def call_smart_contract(self, contract_address: str, function_name: str, 
                                 function_params: List[Any]) -> Dict[str, Any]:
        """
        Call a function on a deployed smart contract.
        
        Args:
            contract_address: Address/ID of the deployed contract
            function_name: Name of the function to call
            function_params: Parameters to pass to the function
            
        Returns:
            Dict with function call result
        """
        pass
    
    @abstractmethod
    async def subscribe_to_events(self, event_filter: Dict[str, Any], 
                                callback: Callable[[Dict[str, Any]], None]) -> str:
        """
        Subscribe to blockchain events.
        
        Args:
            event_filter: Filter criteria for events
            callback: Callback function to call when events are received
            
        Returns:
            str: Subscription ID if subscription successful, empty string otherwise
        """
        pass
    
    @abstractmethod
    async def unsubscribe_from_events(self, subscription_id: str) -> bool:
        """
        Unsubscribe from blockchain events.
        
        Args:
            subscription_id: ID of the subscription to cancel
            
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        pass
    
    async def translate_to_industriverse(self, blockchain_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate blockchain data to Industriverse protocol format.
        
        Args:
            blockchain_data: Blockchain data to translate
            
        Returns:
            Data in Industriverse protocol format
        """
        # Create Unified Message Envelope
        ume = {
            "origin_protocol": self.blockchain_type.value.upper(),
            "target_protocol": "MCP",
            "context": {
                "blockchain_type": self.blockchain_type.value,
                "connector_id": self.component_id,
                "timestamp": datetime.now().isoformat()
            },
            "payload": blockchain_data,
            "trace_id": str(uuid.uuid4()),
            "security_level": "high",  # Blockchain typically requires high security
            "reflex_timer_ms": 5000  # 5 seconds default timeout for blockchain operations
        }
        
        return ume
    
    async def translate_from_industriverse(self, industriverse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Industriverse protocol data to blockchain format.
        
        Args:
            industriverse_data: Industriverse protocol data to translate
            
        Returns:
            Data in blockchain format
        """
        # Extract payload from Unified Message Envelope
        if "payload" in industriverse_data:
            return industriverse_data["payload"]
        else:
            return industriverse_data
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming messages from the Protocol Layer.
        
        This method is called by the Protocol Layer when a message is received
        for this connector.
        
        Args:
            message: Incoming message
            
        Returns:
            Response message
        """
        # Translate from Industriverse protocol if needed
        if message.get("origin_protocol") and message.get("origin_protocol") != self.blockchain_type.value.upper():
            blockchain_message = await self.translate_from_industriverse(message)
        else:
            blockchain_message = message
            
        # Handle message
        response = await self.handle_message(blockchain_message)
        
        # Translate to Industriverse protocol if needed
        if message.get("target_protocol") and message.get("target_protocol") != self.blockchain_type.value.upper():
            industriverse_response = await self.translate_to_industriverse(response)
            return industriverse_response
        else:
            return response
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming blockchain messages.
        
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
            if command == "connect":
                success = await self.connect(params)
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "disconnect":
                success = await self.disconnect()
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "is_connected":
                connected = await self.is_connected()
                return MessageFactory.create_response(message, result={"connected": connected})
                
            elif command == "get_connection_info":
                info = await self.get_connection_info()
                return MessageFactory.create_response(message, result=info)
                
            elif command == "create_transaction":
                transaction_id = await self.create_transaction(params)
                return MessageFactory.create_response(message, result={"transaction_id": transaction_id})
                
            elif command == "get_transaction_status":
                status = await self.get_transaction_status(params.get("transaction_id", ""))
                return MessageFactory.create_response(message, result={"status": status.value})
                
            elif command == "get_transaction_details":
                details = await self.get_transaction_details(params.get("transaction_id", ""))
                return MessageFactory.create_response(message, result=details)
                
            elif command == "deploy_smart_contract":
                contract_address = await self.deploy_smart_contract(params)
                return MessageFactory.create_response(message, result={"contract_address": contract_address})
                
            elif command == "call_smart_contract":
                result = await self.call_smart_contract(
                    params.get("contract_address", ""),
                    params.get("function_name", ""),
                    params.get("function_params", [])
                )
                return MessageFactory.create_response(message, result=result)
                
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
    
    async def shutdown(self):
        """
        Shutdown the connector, disconnecting from the blockchain.
        """
        self.logger.info(f"Shutting down {self.blockchain_type.value.capitalize()} Blockchain Connector {self.component_id}")
        
        # Disconnect if connected
        if self.connected:
            await self.disconnect()
            
        # Unregister from discovery service
        self.discovery_service.unregister_component(self.component_id)
        
        self.logger.info(f"{self.blockchain_type.value.capitalize()} Blockchain Connector {self.component_id} shutdown complete")
