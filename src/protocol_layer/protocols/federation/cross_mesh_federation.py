"""
Cross-Mesh Federation for Industriverse Protocol Layer

This module implements the Cross-Mesh Federation component of the Protocol Layer,
enabling secure communication and coordination between independent Industriverse protocol meshes.

Features:
1. Secure handshake and trust establishment between meshes
2. Identity and credential mapping across mesh boundaries
3. Policy enforcement for cross-mesh communication
4. Message translation and routing between meshes
5. Discovery bridging for sharing component information
6. Federated task orchestration across multiple meshes
"""

import uuid
import time
import asyncio
import logging
import json
import base64
import hashlib
import hmac
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FederationStatus(Enum):
    """Status of a federation relationship."""
    PENDING = "pending"  # Initial handshake in progress
    ACTIVE = "active"  # Federation is active
    SUSPENDED = "suspended"  # Federation is temporarily suspended
    REVOKED = "revoked"  # Federation has been revoked
    FAILED = "failed"  # Federation failed to establish


class FederationRole(Enum):
    """Role in a federation relationship."""
    INITIATOR = "initiator"  # Mesh that initiated the federation
    RESPONDER = "responder"  # Mesh that responded to federation request
    PEER = "peer"  # Equal peer in the federation


class FederationTrustLevel(Enum):
    """Trust level for a federation relationship."""
    NONE = "none"  # No trust
    LOW = "low"  # Low trust, limited access
    MEDIUM = "medium"  # Medium trust, standard access
    HIGH = "high"  # High trust, extended access
    FULL = "full"  # Full trust, unrestricted access


@dataclass
class FederationRelationship:
    """
    Represents a federation relationship between two meshes.
    """
    federation_id: str
    local_mesh_id: str
    remote_mesh_id: str
    status: FederationStatus
    role: FederationRole
    trust_level: FederationTrustLevel
    established_at: float
    expires_at: Optional[float] = None
    last_activity: float = field(default_factory=time.time)
    shared_secret: Optional[str] = None
    remote_endpoints: Dict[str, str] = field(default_factory=dict)
    policies: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if the federation is active."""
        return (
            self.status == FederationStatus.ACTIVE and
            (self.expires_at is None or self.expires_at > time.time())
        )
    
    def to_dict(self, include_secret: bool = False) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "federation_id": self.federation_id,
            "local_mesh_id": self.local_mesh_id,
            "remote_mesh_id": self.remote_mesh_id,
            "status": self.status.value,
            "role": self.role.value,
            "trust_level": self.trust_level.value,
            "established_at": self.established_at,
            "expires_at": self.expires_at,
            "last_activity": self.last_activity,
            "remote_endpoints": self.remote_endpoints,
            "policies": self.policies,
            "metadata": self.metadata,
            "is_active": self.is_active
        }
        
        if include_secret and self.shared_secret:
            result["shared_secret"] = self.shared_secret
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FederationRelationship':
        """Create from dictionary representation."""
        return cls(
            federation_id=data["federation_id"],
            local_mesh_id=data["local_mesh_id"],
            remote_mesh_id=data["remote_mesh_id"],
            status=FederationStatus(data["status"]),
            role=FederationRole(data["role"]),
            trust_level=FederationTrustLevel(data["trust_level"]),
            established_at=data["established_at"],
            expires_at=data.get("expires_at"),
            last_activity=data.get("last_activity", time.time()),
            shared_secret=data.get("shared_secret"),
            remote_endpoints=data.get("remote_endpoints", {}),
            policies=data.get("policies", {}),
            metadata=data.get("metadata", {})
        )


@dataclass
class FederatedMessage:
    """
    Represents a message that is being sent across federation boundaries.
    """
    message_id: str
    federation_id: str
    source_mesh_id: str
    target_mesh_id: str
    original_message: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None
    
    def sign(self, shared_secret: str) -> None:
        """Sign the message using the shared secret."""
        # Create a canonical representation for signing
        canonical = {
            "message_id": self.message_id,
            "federation_id": self.federation_id,
            "source_mesh_id": self.source_mesh_id,
            "target_mesh_id": self.target_mesh_id,
            "original_message": self.original_message,
            "timestamp": self.timestamp
        }
        canonical_str = json.dumps(canonical, sort_keys=True)
        
        # Create HMAC signature
        h = hmac.new(
            shared_secret.encode('utf-8'),
            canonical_str.encode('utf-8'),
            hashlib.sha256
        )
        self.signature = base64.b64encode(h.digest()).decode('utf-8')
    
    def verify(self, shared_secret: str) -> bool:
        """Verify the message signature using the shared secret."""
        if not self.signature:
            return False
        
        # Create a canonical representation for verification
        canonical = {
            "message_id": self.message_id,
            "federation_id": self.federation_id,
            "source_mesh_id": self.source_mesh_id,
            "target_mesh_id": self.target_mesh_id,
            "original_message": self.original_message,
            "timestamp": self.timestamp
        }
        canonical_str = json.dumps(canonical, sort_keys=True)
        
        # Create HMAC signature
        h = hmac.new(
            shared_secret.encode('utf-8'),
            canonical_str.encode('utf-8'),
            hashlib.sha256
        )
        expected_signature = base64.b64encode(h.digest()).decode('utf-8')
        
        # Compare signatures
        return hmac.compare_digest(self.signature, expected_signature)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "message_id": self.message_id,
            "federation_id": self.federation_id,
            "source_mesh_id": self.source_mesh_id,
            "target_mesh_id": self.target_mesh_id,
            "original_message": self.original_message,
            "timestamp": self.timestamp,
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FederatedMessage':
        """Create from dictionary representation."""
        return cls(
            message_id=data["message_id"],
            federation_id=data["federation_id"],
            source_mesh_id=data["source_mesh_id"],
            target_mesh_id=data["target_mesh_id"],
            original_message=data["original_message"],
            timestamp=data.get("timestamp", time.time()),
            signature=data.get("signature")
        )


class CrossMeshFederation(ProtocolService):
    """
    Service for managing cross-mesh federation.
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "cross_mesh_federation")
        self.config = config or {}
        
        # Initialize storage
        self.federations: Dict[str, FederationRelationship] = {}
        self.pending_handshakes: Dict[str, Dict[str, Any]] = {}
        self.message_cache: Dict[str, FederatedMessage] = {}
        
        # Local mesh information
        self.local_mesh_id = self.config.get("local_mesh_id", str(uuid.uuid4()))
        self.local_endpoints = self.config.get("local_endpoints", {})
        
        # State
        self.is_async = True
        self.lock = asyncio.Lock()
        
        # Callbacks
        self.message_handlers: Dict[str, Callable[[FederatedMessage], Awaitable[Dict[str, Any]]]] = {}
        
        self.logger = logging.getLogger(f"{__name__}.CrossMeshFederation.{self.component_id[:8]}")
        self.logger.info(f"Cross-Mesh Federation initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("cross_mesh_federation", "Manage federation between protocol meshes")
        self.add_capability("federated_messaging", "Send and receive messages across mesh boundaries")
        self.add_capability("federation_discovery", "Discover and connect to other meshes")
        self.add_capability("federation_policy", "Enforce policies for cross-mesh communication")

    async def initialize(self) -> bool:
        """Initialize the federation service."""
        self.logger.info("Initializing Cross-Mesh Federation")
        
        # Load existing federations if provided
        existing_federations = self.config.get("existing_federations", [])
        for fed_data in existing_federations:
            try:
                federation = FederationRelationship.from_dict(fed_data)
                self.federations[federation.federation_id] = federation
                self.logger.info(f"Loaded existing federation {federation.federation_id} with {federation.remote_mesh_id}")
            except Exception as e:
                self.logger.error(f"Error loading federation: {str(e)}")
        
        self.logger.info(f"Cross-Mesh Federation initialized with {len(self.federations)} existing federations")
        return True

    # --- Federation Management ---

    async def initiate_federation(
        self,
        remote_mesh_id: str,
        remote_endpoint: str,
        trust_level: FederationTrustLevel = FederationTrustLevel.MEDIUM,
        expiration: Optional[float] = None,
        policies: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Initiate a federation with another mesh."""
        # Generate federation ID
        federation_id = str(uuid.uuid4())
        
        # Generate handshake token
        handshake_token = str(uuid.uuid4())
        
        # Store pending handshake
        async with self.lock:
            self.pending_handshakes[handshake_token] = {
                "federation_id": federation_id,
                "remote_mesh_id": remote_mesh_id,
                "remote_endpoint": remote_endpoint,
                "trust_level": trust_level,
                "expiration": expiration,
                "policies": policies or {},
                "metadata": metadata or {},
                "timestamp": time.time()
            }
        
        # Create handshake request
        handshake_request = {
            "message_type": "federation_handshake_request",
            "federation_id": federation_id,
            "source_mesh_id": self.local_mesh_id,
            "target_mesh_id": remote_mesh_id,
            "handshake_token": handshake_token,
            "trust_level": trust_level.value,
            "expiration": expiration,
            "local_endpoints": self.local_endpoints,
            "policies": policies or {},
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        self.logger.info(f"Initiating federation {federation_id} with mesh {remote_mesh_id}")
        
        # In a real implementation, this would send the handshake request to the remote endpoint
        # For this simulation, we'll just return the handshake request
        return {
            "federation_id": federation_id,
            "handshake_token": handshake_token,
            "handshake_request": handshake_request,
            "remote_endpoint": remote_endpoint
        }

    async def process_handshake_request(
        self,
        handshake_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a federation handshake request from another mesh."""
        # Extract request data
        federation_id = handshake_request.get("federation_id")
        source_mesh_id = handshake_request.get("source_mesh_id")
        handshake_token = handshake_request.get("handshake_token")
        trust_level_str = handshake_request.get("trust_level")
        expiration = handshake_request.get("expiration")
        remote_endpoints = handshake_request.get("local_endpoints", {})
        policies = handshake_request.get("policies", {})
        metadata = handshake_request.get("metadata", {})
        
        # Validate request
        if not all([federation_id, source_mesh_id, handshake_token, trust_level_str]):
            self.logger.error("Invalid handshake request, missing required fields")
            return {
                "message_type": "federation_handshake_response",
                "federation_id": federation_id,
                "source_mesh_id": self.local_mesh_id,
                "target_mesh_id": source_mesh_id,
                "handshake_token": handshake_token,
                "status": "failed",
                "error": "Invalid handshake request, missing required fields",
                "timestamp": time.time()
            }
        
        # Check if federation already exists
        async with self.lock:
            existing_federation = next(
                (f for f in self.federations.values() if f.remote_mesh_id == source_mesh_id),
                None
            )
            
            if existing_federation and existing_federation.is_active:
                self.logger.warning(f"Federation already exists with mesh {source_mesh_id}")
                return {
                    "message_type": "federation_handshake_response",
                    "federation_id": federation_id,
                    "source_mesh_id": self.local_mesh_id,
                    "target_mesh_id": source_mesh_id,
                    "handshake_token": handshake_token,
                    "status": "failed",
                    "error": "Federation already exists",
                    "existing_federation_id": existing_federation.federation_id,
                    "timestamp": time.time()
                }
        
        # Generate shared secret
        shared_secret = base64.b64encode(os.urandom(32)).decode('utf-8')
        
        # Create federation relationship
        federation = FederationRelationship(
            federation_id=federation_id,
            local_mesh_id=self.local_mesh_id,
            remote_mesh_id=source_mesh_id,
            status=FederationStatus.ACTIVE,
            role=FederationRole.RESPONDER,
            trust_level=FederationTrustLevel(trust_level_str),
            established_at=time.time(),
            expires_at=expiration,
            shared_secret=shared_secret,
            remote_endpoints=remote_endpoints,
            policies=policies,
            metadata=metadata
        )
        
        # Store federation
        async with self.lock:
            self.federations[federation_id] = federation
        
        self.logger.info(f"Accepted federation {federation_id} from mesh {source_mesh_id}")
        
        # Create handshake response
        handshake_response = {
            "message_type": "federation_handshake_response",
            "federation_id": federation_id,
            "source_mesh_id": self.local_mesh_id,
            "target_mesh_id": source_mesh_id,
            "handshake_token": handshake_token,
            "status": "accepted",
            "shared_secret": shared_secret,
            "local_endpoints": self.local_endpoints,
            "policies": self.config.get("federation_policies", {}),
            "metadata": self.config.get("federation_metadata", {}),
            "timestamp": time.time()
        }
        
        return handshake_response

    async def process_handshake_response(
        self,
        handshake_response: Dict[str, Any]
    ) -> Optional[FederationRelationship]:
        """Process a federation handshake response from another mesh."""
        # Extract response data
        federation_id = handshake_response.get("federation_id")
        source_mesh_id = handshake_response.get("source_mesh_id")
        handshake_token = handshake_response.get("handshake_token")
        status = handshake_response.get("status")
        shared_secret = handshake_response.get("shared_secret")
        remote_endpoints = handshake_response.get("local_endpoints", {})
        policies = handshake_response.get("policies", {})
        metadata = handshake_response.get("metadata", {})
        
        # Validate response
        if not all([federation_id, source_mesh_id, handshake_token, status]):
            self.logger.error("Invalid handshake response, missing required fields")
            return None
        
        # Check if handshake token exists
        async with self.lock:
            if handshake_token not in self.pending_handshakes:
                self.logger.error(f"Unknown handshake token: {handshake_token}")
                return None
            
            # Get pending handshake
            handshake = self.pending_handshakes.pop(handshake_token)
            
            # Check if federation matches
            if handshake["federation_id"] != federation_id:
                self.logger.error(f"Federation ID mismatch: {handshake['federation_id']} != {federation_id}")
                return None
            
            # Check if remote mesh matches
            if handshake["remote_mesh_id"] != source_mesh_id:
                self.logger.error(f"Remote mesh ID mismatch: {handshake['remote_mesh_id']} != {source_mesh_id}")
                return None
        
        # Check status
        if status != "accepted":
            self.logger.warning(f"Federation handshake rejected: {handshake_response.get('error', 'Unknown error')}")
            return None
        
        # Create federation relationship
        federation = FederationRelationship(
            federation_id=federation_id,
            local_mesh_id=self.local_mesh_id,
            remote_mesh_id=source_mesh_id,
            status=FederationStatus.ACTIVE,
            role=FederationRole.INITIATOR,
            trust_level=handshake["trust_level"],
            established_at=time.time(),
            expires_at=handshake["expiration"],
            shared_secret=shared_secret,
            remote_endpoints=remote_endpoints,
            policies=policies,
            metadata=metadata
        )
        
        # Store federation
        async with self.lock:
            self.federations[federation_id] = federation
        
        self.logger.info(f"Completed federation {federation_id} with mesh {source_mesh_id}")
        return federation

    async def get_federation(self, federation_id: str) -> Optional[FederationRelationship]:
        """Get a federation by ID."""
        async with self.lock:
            if federation_id not in self.federations:
                self.logger.error(f"Federation {federation_id} not found")
                return None
            
            return self.federations[federation_id]

    async def get_federations_with_mesh(self, mesh_id: str) -> List[FederationRelationship]:
        """Get all federations with a specific mesh."""
        async with self.lock:
            return [f for f in self.federations.values() if f.remote_mesh_id == mesh_id]

    async def get_active_federations(self) -> List[FederationRelationship]:
        """Get all active federations."""
        async with self.lock:
            return [f for f in self.federations.values() if f.is_active]

    async def update_federation_status(
        self,
        federation_id: str,
        status: FederationStatus
    ) -> Optional[FederationRelationship]:
        """Update the status of a federation."""
        async with self.lock:
            if federation_id not in self.federations:
                self.logger.error(f"Federation {federation_id} not found")
                return None
            
            federation = self.federations[federation_id]
            federation.status = status
            federation.last_activity = time.time()
            
            self.logger.info(f"Updated federation {federation_id} status to {status.value}")
            return federation

    async def revoke_federation(
        self,
        federation_id: str,
        reason: str = "Revoked by administrator"
    ) -> bool:
        """Revoke a federation."""
        async with self.lock:
            if federation_id not in self.federations:
                self.logger.error(f"Federation {federation_id} not found")
                return False
            
            federation = self.federations[federation_id]
            federation.status = FederationStatus.REVOKED
            federation.last_activity = time.time()
            federation.metadata["revocation_reason"] = reason
            
            self.logger.info(f"Revoked federation {federation_id}: {reason}")
            
            # In a real implementation, this would notify the remote mesh
            # For this simulation, we'll just return success
            return True

    # --- Federated Messaging ---

    async def register_message_handler(
        self,
        message_type: str,
        handler: Callable[[FederatedMessage], Awaitable[Dict[str, Any]]]
    ) -> bool:
        """Register a handler for a specific message type."""
        async with self.lock:
            self.message_handlers[message_type] = handler
        
        self.logger.debug(f"Registered message handler for type {message_type}")
        return True

    async def send_federated_message(
        self,
        federation_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a message to a federated mesh."""
        # Get federation
        async with self.lock:
            if federation_id not in self.federations:
                self.logger.error(f"Federation {federation_id} not found")
                return {
                    "success": False,
                    "error": "Federation not found"
                }
            
            federation = self.federations[federation_id]
            
            # Check if federation is active
            if not federation.is_active:
                self.logger.error(f"Federation {federation_id} is not active")
                return {
                    "success": False,
                    "error": "Federation is not active"
                }
            
            # Check if we have a shared secret
            if not federation.shared_secret:
                self.logger.error(f"Federation {federation_id} has no shared secret")
                return {
                    "success": False,
                    "error": "Federation has no shared secret"
                }
        
        # Create federated message
        federated_message = FederatedMessage(
            message_id=str(uuid.uuid4()),
            federation_id=federation_id,
            source_mesh_id=self.local_mesh_id,
            target_mesh_id=federation.remote_mesh_id,
            original_message=message
        )
        
        # Sign message
        federated_message.sign(federation.shared_secret)
        
        # Cache message
        async with self.lock:
            self.message_cache[federated_message.message_id] = federated_message
        
        self.logger.debug(f"Sending federated message {federated_message.message_id} to mesh {federation.remote_mesh_id}")
        
        # In a real implementation, this would send the message to the remote mesh
        # For this simulation, we'll just return the message
        return {
            "success": True,
            "message_id": federated_message.message_id,
            "federated_message": federated_message.to_dict()
        }

    async def receive_federated_message(
        self,
        federated_message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Receive a message from a federated mesh."""
        # Parse federated message
        try:
            federated_message = FederatedMessage.from_dict(federated_message_data)
        except Exception as e:
            self.logger.error(f"Error parsing federated message: {str(e)}")
            return {
                "success": False,
                "error": "Invalid federated message format"
            }
        
        # Get federation
        async with self.lock:
            federation = next(
                (f for f in self.federations.values() if f.federation_id == federated_message.federation_id),
                None
            )
            
            if not federation:
                self.logger.error(f"Federation {federated_message.federation_id} not found")
                return {
                    "success": False,
                    "error": "Federation not found"
                }
            
            # Check if federation is active
            if not federation.is_active:
                self.logger.error(f"Federation {federated_message.federation_id} is not active")
                return {
                    "success": False,
                    "error": "Federation is not active"
                }
            
            # Check if we have a shared secret
            if not federation.shared_secret:
                self.logger.error(f"Federation {federated_message.federation_id} has no shared secret")
                return {
                    "success": False,
                    "error": "Federation has no shared secret"
                }
            
            # Check if message is from the expected mesh
            if federated_message.source_mesh_id != federation.remote_mesh_id:
                self.logger.error(f"Message source mesh {federated_message.source_mesh_id} does not match federation remote mesh {federation.remote_mesh_id}")
                return {
                    "success": False,
                    "error": "Message source mesh does not match federation remote mesh"
                }
            
            # Check if message is for this mesh
            if federated_message.target_mesh_id != self.local_mesh_id:
                self.logger.error(f"Message target mesh {federated_message.target_mesh_id} does not match local mesh {self.local_mesh_id}")
                return {
                    "success": False,
                    "error": "Message target mesh does not match local mesh"
                }
        
        # Verify message signature
        if not federated_message.verify(federation.shared_secret):
            self.logger.error(f"Invalid signature for federated message {federated_message.message_id}")
            return {
                "success": False,
                "error": "Invalid message signature"
            }
        
        # Cache message
        async with self.lock:
            self.message_cache[federated_message.message_id] = federated_message
            
            # Update federation last activity
            federation.last_activity = time.time()
        
        self.logger.debug(f"Received federated message {federated_message.message_id} from mesh {federation.remote_mesh_id}")
        
        # Process message
        original_message = federated_message.original_message
        message_type = original_message.get("message_type", "unknown")
        
        # Check if we have a handler for this message type
        handler = self.message_handlers.get(message_type)
        if handler:
            try:
                # Call handler
                response = await handler(federated_message)
                return {
                    "success": True,
                    "message_id": federated_message.message_id,
                    "response": response
                }
            except Exception as e:
                self.logger.error(f"Error in message handler for type {message_type}: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error in message handler: {str(e)}"
                }
        else:
            self.logger.warning(f"No handler registered for message type {message_type}")
            return {
                "success": True,
                "message_id": federated_message.message_id,
                "warning": f"No handler registered for message type {message_type}"
            }

    async def get_federated_message(self, message_id: str) -> Optional[FederatedMessage]:
        """Get a federated message by ID."""
        async with self.lock:
            if message_id not in self.message_cache:
                self.logger.error(f"Federated message {message_id} not found")
                return None
            
            return self.message_cache[message_id]

    # --- Federation Discovery ---

    async def discover_meshes(self, discovery_endpoint: str) -> Dict[str, Any]:
        """Discover other meshes through a discovery endpoint."""
        # In a real implementation, this would query a discovery service
        # For this simulation, we'll just return a mock response
        self.logger.info(f"Discovering meshes through endpoint {discovery_endpoint}")
        
        return {
            "success": True,
            "discovered_meshes": [
                {
                    "mesh_id": f"mesh_{i}",
                    "name": f"Mock Mesh {i}",
                    "endpoints": {
                        "federation": f"https://mesh{i}.example.com/federation",
                        "discovery": f"https://mesh{i}.example.com/discovery"
                    },
                    "capabilities": ["federation", "discovery", "messaging"],
                    "metadata": {
                        "region": f"Region {i}",
                        "industry": f"Industry {i % 3}"
                    }
                }
                for i in range(1, 4)
            ]
        }

    async def register_with_discovery(self, discovery_endpoint: str) -> Dict[str, Any]:
        """Register this mesh with a discovery endpoint."""
        # In a real implementation, this would register with a discovery service
        # For this simulation, we'll just return a mock response
        self.logger.info(f"Registering with discovery endpoint {discovery_endpoint}")
        
        registration_data = {
            "mesh_id": self.local_mesh_id,
            "name": self.config.get("mesh_name", f"Mesh {self.local_mesh_id[:8]}"),
            "endpoints": self.local_endpoints,
            "capabilities": ["federation", "discovery", "messaging"],
            "metadata": self.config.get("mesh_metadata", {})
        }
        
        return {
            "success": True,
            "registration_id": str(uuid.uuid4()),
            "registration_data": registration_data
        }

    # --- Policy Enforcement ---

    async def check_policy(
        self,
        federation_id: str,
        policy_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if an action is allowed by federation policy."""
        # Get federation
        async with self.lock:
            if federation_id not in self.federations:
                self.logger.error(f"Federation {federation_id} not found")
                return {
                    "allowed": False,
                    "reason": "Federation not found"
                }
            
            federation = self.federations[federation_id]
            
            # Check if federation is active
            if not federation.is_active:
                self.logger.error(f"Federation {federation_id} is not active")
                return {
                    "allowed": False,
                    "reason": "Federation is not active"
                }
            
            # Get policies
            policies = federation.policies.get(policy_type, {})
            
            # Check if policy exists
            if not policies:
                # Default to permissive if no policy exists
                return {
                    "allowed": True,
                    "reason": "No policy defined"
                }
            
            # In a real implementation, this would evaluate the policy against the context
            # For this simulation, we'll just check if the policy has an "allow" field
            if policies.get("allow", True):
                return {
                    "allowed": True,
                    "reason": "Allowed by policy"
                }
            else:
                return {
                    "allowed": False,
                    "reason": policies.get("reason", "Denied by policy")
                }

    # --- Message Handling ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "initiate_federation":
                params = msg_obj.params
                if "remote_mesh_id" in params and "remote_endpoint" in params:
                    result = await self.initiate_federation(
                        remote_mesh_id=params["remote_mesh_id"],
                        remote_endpoint=params["remote_endpoint"],
                        trust_level=FederationTrustLevel(params.get("trust_level", "medium")),
                        expiration=params.get("expiration"),
                        policies=params.get("policies"),
                        metadata=params.get("metadata")
                    )
                    response_payload = result
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing required parameters"}
            
            elif msg_obj.command == "process_handshake_request":
                params = msg_obj.params
                if "handshake_request" in params:
                    result = await self.process_handshake_request(params["handshake_request"])
                    response_payload = result
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing handshake_request parameter"}
            
            elif msg_obj.command == "process_handshake_response":
                params = msg_obj.params
                if "handshake_response" in params:
                    federation = await self.process_handshake_response(params["handshake_response"])
                    if federation:
                        response_payload = federation.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Failed to process handshake response"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing handshake_response parameter"}
            
            elif msg_obj.command == "update_federation_status":
                params = msg_obj.params
                if "federation_id" in params and "status" in params:
                    federation = await self.update_federation_status(
                        federation_id=params["federation_id"],
                        status=FederationStatus(params["status"])
                    )
                    if federation:
                        response_payload = federation.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Federation not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing required parameters"}
            
            elif msg_obj.command == "revoke_federation":
                params = msg_obj.params
                if "federation_id" in params:
                    success = await self.revoke_federation(
                        federation_id=params["federation_id"],
                        reason=params.get("reason", "Revoked by administrator")
                    )
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing federation_id parameter"}
            
            elif msg_obj.command == "send_federated_message":
                params = msg_obj.params
                if "federation_id" in params and "message" in params:
                    result = await self.send_federated_message(
                        federation_id=params["federation_id"],
                        message=params["message"]
                    )
                    response_payload = result
                    if not result.get("success", False):
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing required parameters"}
            
            elif msg_obj.command == "receive_federated_message":
                params = msg_obj.params
                if "federated_message" in params:
                    result = await self.receive_federated_message(params["federated_message"])
                    response_payload = result
                    if not result.get("success", False):
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing federated_message parameter"}
            
            elif msg_obj.command == "discover_meshes":
                params = msg_obj.params
                if "discovery_endpoint" in params:
                    result = await self.discover_meshes(params["discovery_endpoint"])
                    response_payload = result
                    if not result.get("success", False):
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing discovery_endpoint parameter"}
            
            elif msg_obj.command == "register_with_discovery":
                params = msg_obj.params
                if "discovery_endpoint" in params:
                    result = await self.register_with_discovery(params["discovery_endpoint"])
                    response_payload = result
                    if not result.get("success", False):
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing discovery_endpoint parameter"}
            
            elif msg_obj.command == "check_policy":
                params = msg_obj.params
                if all(k in params for k in ["federation_id", "policy_type", "context"]):
                    result = await self.check_policy(
                        federation_id=params["federation_id"],
                        policy_type=params["policy_type"],
                        context=params["context"]
                    )
                    response_payload = result
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing required parameters"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_federation":
                params = msg_obj.params
                if "federation_id" in params:
                    federation = await self.get_federation(params["federation_id"])
                    if federation:
                        response_payload = federation.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Federation not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing federation_id parameter"}
            
            elif msg_obj.query == "get_federations_with_mesh":
                params = msg_obj.params
                if "mesh_id" in params:
                    federations = await self.get_federations_with_mesh(params["mesh_id"])
                    response_payload = {"federations": [f.to_dict() for f in federations]}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing mesh_id parameter"}
            
            elif msg_obj.query == "get_active_federations":
                federations = await self.get_active_federations()
                response_payload = {"federations": [f.to_dict() for f in federations]}
            
            elif msg_obj.query == "get_federated_message":
                params = msg_obj.params
                if "message_id" in params:
                    message = await self.get_federated_message(params["message_id"])
                    if message:
                        response_payload = message.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Federated message not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing message_id parameter"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        else:
            status = MessageStatus.FAILED
            response_payload = {"error": "Unsupported message type"}

        # Create response
        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message (synchronous wrapper)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check."""
        async with self.lock:
            num_federations = len(self.federations)
            num_active = len([f for f in self.federations.values() if f.is_active])
            num_pending = len(self.pending_handshakes)
            num_cached = len(self.message_cache)
        
        return {
            "status": "healthy",
            "total_federations": num_federations,
            "active_federations": num_active,
            "pending_handshakes": num_pending,
            "cached_messages": num_cached
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
