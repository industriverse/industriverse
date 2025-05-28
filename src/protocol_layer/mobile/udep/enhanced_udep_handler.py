"""
Enhanced UDEP (Universal Device Endpoint Protocol) Handler for Industriverse Protocol Layer

This module implements the Enhanced UDEP Handler component of the Protocol Layer,
enabling dynamic agent transfer capabilities and optimized communication for mobile/edge devices.

Features:
1. Dynamic agent transfer between devices
2. Optimized protocol envelope for resource-constrained devices
3. Adaptive compression based on device capabilities
4. Secure credential management for mobile endpoints
5. Offline operation support with store-and-forward
"""

import uuid
import time
import asyncio
import logging
import json
import base64
import hashlib
import zlib
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


class DeviceCapabilityLevel(Enum):
    """Capability levels for devices."""
    LOW = "low"  # Very constrained devices (e.g., sensors)
    MEDIUM = "medium"  # Moderately capable devices (e.g., smartphones)
    HIGH = "high"  # Highly capable devices (e.g., tablets, laptops)
    FULL = "full"  # Full-capability devices (e.g., servers, desktops)


class ConnectionType(Enum):
    """Connection types for devices."""
    OFFLINE = "offline"  # No connection
    INTERMITTENT = "intermittent"  # Unreliable connection
    CELLULAR = "cellular"  # Cellular connection
    WIFI = "wifi"  # WiFi connection
    WIRED = "wired"  # Wired connection
    SATELLITE = "satellite"  # Satellite connection


class AgentTransferStatus(Enum):
    """Status of an agent transfer."""
    PENDING = "pending"  # Transfer is pending
    IN_PROGRESS = "in_progress"  # Transfer is in progress
    COMPLETED = "completed"  # Transfer completed successfully
    FAILED = "failed"  # Transfer failed
    CANCELLED = "cancelled"  # Transfer was cancelled


@dataclass
class DeviceProfile:
    """
    Represents a device profile with capabilities and constraints.
    """
    device_id: str
    capability_level: DeviceCapabilityLevel
    connection_type: ConnectionType
    max_message_size: int
    supports_compression: bool
    supports_encryption: bool
    battery_constrained: bool
    cpu_constrained: bool
    memory_constrained: bool
    storage_constrained: bool
    last_seen: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "device_id": self.device_id,
            "capability_level": self.capability_level.value,
            "connection_type": self.connection_type.value,
            "max_message_size": self.max_message_size,
            "supports_compression": self.supports_compression,
            "supports_encryption": self.supports_encryption,
            "battery_constrained": self.battery_constrained,
            "cpu_constrained": self.cpu_constrained,
            "memory_constrained": self.memory_constrained,
            "storage_constrained": self.storage_constrained,
            "last_seen": self.last_seen,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceProfile':
        """Create from dictionary representation."""
        return cls(
            device_id=data["device_id"],
            capability_level=DeviceCapabilityLevel(data["capability_level"]),
            connection_type=ConnectionType(data["connection_type"]),
            max_message_size=data["max_message_size"],
            supports_compression=data["supports_compression"],
            supports_encryption=data["supports_encryption"],
            battery_constrained=data["battery_constrained"],
            cpu_constrained=data["cpu_constrained"],
            memory_constrained=data["memory_constrained"],
            storage_constrained=data["storage_constrained"],
            last_seen=data["last_seen"],
            metadata=data.get("metadata", {})
        )


@dataclass
class AgentTransfer:
    """
    Represents an agent transfer between devices.
    """
    transfer_id: str
    agent_id: str
    source_device_id: str
    target_device_id: str
    status: AgentTransferStatus
    start_time: float
    completion_time: Optional[float] = None
    agent_state: Dict[str, Any] = field(default_factory=dict)
    transfer_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "transfer_id": self.transfer_id,
            "agent_id": self.agent_id,
            "source_device_id": self.source_device_id,
            "target_device_id": self.target_device_id,
            "status": self.status.value,
            "start_time": self.start_time,
            "completion_time": self.completion_time,
            "agent_state": self.agent_state,
            "transfer_metadata": self.transfer_metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTransfer':
        """Create from dictionary representation."""
        return cls(
            transfer_id=data["transfer_id"],
            agent_id=data["agent_id"],
            source_device_id=data["source_device_id"],
            target_device_id=data["target_device_id"],
            status=AgentTransferStatus(data["status"]),
            start_time=data["start_time"],
            completion_time=data.get("completion_time"),
            agent_state=data.get("agent_state", {}),
            transfer_metadata=data.get("transfer_metadata", {})
        )


@dataclass
class OfflineMessage:
    """
    Represents a message stored for offline delivery.
    """
    message_id: str
    target_device_id: str
    message: Dict[str, Any]
    created_at: float
    expires_at: Optional[float] = None
    priority: MessagePriority = MessagePriority.NORMAL
    delivery_attempts: int = 0
    last_attempt: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "message_id": self.message_id,
            "target_device_id": self.target_device_id,
            "message": self.message,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "priority": self.priority.value,
            "delivery_attempts": self.delivery_attempts,
            "last_attempt": self.last_attempt
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OfflineMessage':
        """Create from dictionary representation."""
        return cls(
            message_id=data["message_id"],
            target_device_id=data["target_device_id"],
            message=data["message"],
            created_at=data["created_at"],
            expires_at=data.get("expires_at"),
            priority=MessagePriority(data["priority"]),
            delivery_attempts=data["delivery_attempts"],
            last_attempt=data.get("last_attempt")
        )


class EnhancedUDEPHandler(ProtocolService):
    """
    Service for handling Enhanced UDEP (Universal Device Endpoint Protocol).
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "enhanced_udep_handler")
        self.config = config or {}
        
        # Initialize storage
        self.device_profiles: Dict[str, DeviceProfile] = {}
        self.agent_transfers: Dict[str, AgentTransfer] = {}
        self.offline_messages: Dict[str, OfflineMessage] = {}
        
        # State
        self.is_async = True
        self.lock = asyncio.Lock()
        
        # Callbacks
        self.device_callbacks: Dict[str, Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]] = {}
        
        self.logger = logging.getLogger(f"{__name__}.EnhancedUDEPHandler.{self.component_id[:8]}")
        self.logger.info(f"Enhanced UDEP Handler initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("enhanced_udep", "Handle Enhanced UDEP protocol")
        self.add_capability("agent_transfer", "Transfer agents between devices")
        self.add_capability("offline_messaging", "Store and forward messages for offline devices")
        self.add_capability("device_management", "Manage device profiles and capabilities")

    async def initialize(self) -> bool:
        """Initialize the UDEP handler."""
        self.logger.info("Initializing Enhanced UDEP Handler")
        
        # Load existing device profiles if provided
        existing_profiles = self.config.get("existing_profiles", [])
        for profile_data in existing_profiles:
            try:
                profile = DeviceProfile.from_dict(profile_data)
                self.device_profiles[profile.device_id] = profile
                self.logger.info(f"Loaded existing device profile for {profile.device_id}")
            except Exception as e:
                self.logger.error(f"Error loading device profile: {str(e)}")
        
        self.logger.info(f"Enhanced UDEP Handler initialized with {len(self.device_profiles)} existing device profiles")
        return True

    # --- Device Management ---

    async def register_device(
        self,
        device_id: str,
        capability_level: DeviceCapabilityLevel,
        connection_type: ConnectionType,
        max_message_size: int,
        supports_compression: bool,
        supports_encryption: bool,
        battery_constrained: bool = False,
        cpu_constrained: bool = False,
        memory_constrained: bool = False,
        storage_constrained: bool = False,
        metadata: Dict[str, Any] = None
    ) -> DeviceProfile:
        """Register a device with the UDEP handler."""
        # Create device profile
        profile = DeviceProfile(
            device_id=device_id,
            capability_level=capability_level,
            connection_type=connection_type,
            max_message_size=max_message_size,
            supports_compression=supports_compression,
            supports_encryption=supports_encryption,
            battery_constrained=battery_constrained,
            cpu_constrained=cpu_constrained,
            memory_constrained=memory_constrained,
            storage_constrained=storage_constrained,
            last_seen=time.time(),
            metadata=metadata or {}
        )
        
        # Store profile
        async with self.lock:
            self.device_profiles[device_id] = profile
        
        self.logger.info(f"Registered device {device_id} with capability level {capability_level.value}")
        return profile

    async def update_device_status(
        self,
        device_id: str,
        connection_type: Optional[ConnectionType] = None,
        metadata_updates: Dict[str, Any] = None
    ) -> Optional[DeviceProfile]:
        """Update a device's status."""
        async with self.lock:
            if device_id not in self.device_profiles:
                self.logger.error(f"Device {device_id} not found")
                return None
            
            profile = self.device_profiles[device_id]
            
            # Update connection type if provided
            if connection_type is not None:
                profile.connection_type = connection_type
            
            # Update metadata if provided
            if metadata_updates:
                profile.metadata.update(metadata_updates)
            
            # Update last seen timestamp
            profile.last_seen = time.time()
        
        self.logger.debug(f"Updated status for device {device_id}")
        
        # Check for offline messages
        if connection_type != ConnectionType.OFFLINE:
            await self._deliver_offline_messages(device_id)
        
        return profile

    async def get_device_profile(self, device_id: str) -> Optional[DeviceProfile]:
        """Get a device profile."""
        async with self.lock:
            if device_id not in self.device_profiles:
                self.logger.error(f"Device {device_id} not found")
                return None
            
            return self.device_profiles[device_id]

    async def list_devices(self, filters: Dict[str, Any] = None) -> List[DeviceProfile]:
        """List devices with optional filtering."""
        filters = filters or {}
        
        async with self.lock:
            profiles = list(self.device_profiles.values())
        
        # Apply filters
        if "capability_level" in filters:
            level = DeviceCapabilityLevel(filters["capability_level"])
            profiles = [p for p in profiles if p.capability_level == level]
        
        if "connection_type" in filters:
            conn_type = ConnectionType(filters["connection_type"])
            profiles = [p for p in profiles if p.connection_type == conn_type]
        
        if "online_only" in filters and filters["online_only"]:
            profiles = [p for p in profiles if p.connection_type != ConnectionType.OFFLINE]
        
        return profiles

    async def register_device_callback(
        self,
        device_id: str,
        callback: Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> bool:
        """Register a callback for a device."""
        async with self.lock:
            self.device_callbacks[device_id] = callback
        
        self.logger.debug(f"Registered callback for device {device_id}")
        return True

    # --- Agent Transfer ---

    async def initiate_agent_transfer(
        self,
        agent_id: str,
        source_device_id: str,
        target_device_id: str,
        agent_state: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> AgentTransfer:
        """Initiate an agent transfer between devices."""
        # Check if source device exists
        source_profile = await self.get_device_profile(source_device_id)
        if not source_profile:
            raise ValueError(f"Source device {source_device_id} not found")
        
        # Check if target device exists
        target_profile = await self.get_device_profile(target_device_id)
        if not target_profile:
            raise ValueError(f"Target device {target_device_id} not found")
        
        # Create transfer
        transfer_id = str(uuid.uuid4())
        transfer = AgentTransfer(
            transfer_id=transfer_id,
            agent_id=agent_id,
            source_device_id=source_device_id,
            target_device_id=target_device_id,
            status=AgentTransferStatus.PENDING,
            start_time=time.time(),
            agent_state=agent_state,
            transfer_metadata=metadata or {}
        )
        
        # Store transfer
        async with self.lock:
            self.agent_transfers[transfer_id] = transfer
        
        self.logger.info(f"Initiated agent transfer {transfer_id} for agent {agent_id} from {source_device_id} to {target_device_id}")
        
        # Start transfer process
        asyncio.create_task(self._process_agent_transfer(transfer_id))
        
        return transfer

    async def get_agent_transfer(self, transfer_id: str) -> Optional[AgentTransfer]:
        """Get an agent transfer by ID."""
        async with self.lock:
            if transfer_id not in self.agent_transfers:
                self.logger.error(f"Agent transfer {transfer_id} not found")
                return None
            
            return self.agent_transfers[transfer_id]

    async def list_agent_transfers(
        self,
        agent_id: Optional[str] = None,
        device_id: Optional[str] = None,
        status: Optional[AgentTransferStatus] = None
    ) -> List[AgentTransfer]:
        """List agent transfers with optional filtering."""
        async with self.lock:
            transfers = list(self.agent_transfers.values())
        
        # Apply filters
        if agent_id:
            transfers = [t for t in transfers if t.agent_id == agent_id]
        
        if device_id:
            transfers = [t for t in transfers if t.source_device_id == device_id or t.target_device_id == device_id]
        
        if status:
            transfers = [t for t in transfers if t.status == status]
        
        return transfers

    async def cancel_agent_transfer(self, transfer_id: str) -> bool:
        """Cancel an agent transfer."""
        async with self.lock:
            if transfer_id not in self.agent_transfers:
                self.logger.error(f"Agent transfer {transfer_id} not found")
                return False
            
            transfer = self.agent_transfers[transfer_id]
            
            # Check if transfer can be cancelled
            if transfer.status not in (AgentTransferStatus.PENDING, AgentTransferStatus.IN_PROGRESS):
                self.logger.warning(f"Cannot cancel transfer {transfer_id} with status {transfer.status.value}")
                return False
            
            # Update transfer status
            transfer.status = AgentTransferStatus.CANCELLED
            transfer.completion_time = time.time()
        
        self.logger.info(f"Cancelled agent transfer {transfer_id}")
        return True

    async def _process_agent_transfer(self, transfer_id: str) -> None:
        """Process an agent transfer."""
        # Get transfer
        async with self.lock:
            if transfer_id not in self.agent_transfers:
                self.logger.error(f"Agent transfer {transfer_id} not found for processing")
                return
            
            transfer = self.agent_transfers[transfer_id]
            
            # Update status
            transfer.status = AgentTransferStatus.IN_PROGRESS
        
        try:
            # Get source and target device profiles
            source_profile = await self.get_device_profile(transfer.source_device_id)
            target_profile = await self.get_device_profile(transfer.target_device_id)
            
            if not source_profile or not target_profile:
                raise ValueError("Source or target device not found")
            
            # Check if target device is online
            if target_profile.connection_type == ConnectionType.OFFLINE:
                self.logger.warning(f"Target device {transfer.target_device_id} is offline, queuing transfer")
                
                # Create offline message for agent transfer
                message = {
                    "message_type": "agent_transfer",
                    "transfer_id": transfer.transfer_id,
                    "agent_id": transfer.agent_id,
                    "agent_state": transfer.agent_state,
                    "source_device_id": transfer.source_device_id,
                    "metadata": transfer.transfer_metadata
                }
                
                await self._store_offline_message(
                    target_device_id=transfer.target_device_id,
                    message=message,
                    priority=MessagePriority.HIGH
                )
                
                # Update transfer status
                async with self.lock:
                    transfer.status = AgentTransferStatus.PENDING
                    transfer.transfer_metadata["queued_for_offline_delivery"] = True
                
                return
            
            # Check if target device has callback registered
            callback = self.device_callbacks.get(transfer.target_device_id)
            if not callback:
                self.logger.warning(f"No callback registered for target device {transfer.target_device_id}")
                
                # Try to deliver via message
                message = {
                    "message_type": "agent_transfer",
                    "transfer_id": transfer.transfer_id,
                    "agent_id": transfer.agent_id,
                    "agent_state": transfer.agent_state,
                    "source_device_id": transfer.source_device_id,
                    "metadata": transfer.transfer_metadata
                }
                
                # In a real implementation, this would send the message to the device
                # For this simulation, we'll just log it
                self.logger.info(f"Would send agent transfer message to device {transfer.target_device_id}")
                
                # Update transfer status
                async with self.lock:
                    transfer.status = AgentTransferStatus.COMPLETED
                    transfer.completion_time = time.time()
                
                return
            
            # Call device callback
            result = await callback(
                "agent_transfer",
                {
                    "transfer_id": transfer.transfer_id,
                    "agent_id": transfer.agent_id,
                    "agent_state": transfer.agent_state,
                    "source_device_id": transfer.source_device_id,
                    "metadata": transfer.transfer_metadata
                }
            )
            
            # Check result
            if result.get("success", False):
                # Update transfer status
                async with self.lock:
                    transfer.status = AgentTransferStatus.COMPLETED
                    transfer.completion_time = time.time()
                    transfer.transfer_metadata["result"] = result
                
                self.logger.info(f"Completed agent transfer {transfer_id}")
            else:
                # Update transfer status
                async with self.lock:
                    transfer.status = AgentTransferStatus.FAILED
                    transfer.completion_time = time.time()
                    transfer.transfer_metadata["error"] = result.get("error", "Unknown error")
                
                self.logger.error(f"Failed agent transfer {transfer_id}: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            # Update transfer status
            async with self.lock:
                transfer.status = AgentTransferStatus.FAILED
                transfer.completion_time = time.time()
                transfer.transfer_metadata["error"] = str(e)
            
            self.logger.error(f"Error processing agent transfer {transfer_id}: {str(e)}")

    # --- Message Handling ---

    async def optimize_message_for_device(
        self,
        device_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize a message for a specific device."""
        # Get device profile
        profile = await self.get_device_profile(device_id)
        if not profile:
            self.logger.warning(f"Device {device_id} not found, using default optimization")
            return message
        
        # Check message size
        message_json = json.dumps(message)
        message_size = len(message_json.encode('utf-8'))
        
        # If message is already small enough, return as is
        if message_size <= profile.max_message_size:
            return message
        
        # Apply optimizations based on device capabilities
        optimized_message = message.copy()
        
        # Apply compression if supported
        if profile.supports_compression:
            # Compress message
            compressed_data = zlib.compress(message_json.encode('utf-8'))
            
            # Check if compression helped
            if len(compressed_data) < message_size:
                optimized_message = {
                    "compressed": True,
                    "algorithm": "zlib",
                    "original_size": message_size,
                    "data": base64.b64encode(compressed_data).decode('utf-8')
                }
                
                # Check if still too large
                optimized_json = json.dumps(optimized_message)
                if len(optimized_json.encode('utf-8')) <= profile.max_message_size:
                    return optimized_message
        
        # If still too large, apply more aggressive optimizations
        if profile.capability_level == DeviceCapabilityLevel.LOW:
            # For very constrained devices, strip all non-essential data
            if "payload" in optimized_message:
                # Keep only essential payload fields
                essential_payload = {}
                for key, value in optimized_message["payload"].items():
                    if key in ["id", "type", "status", "priority"]:
                        essential_payload[key] = value
                optimized_message["payload"] = essential_payload
            
            # Remove any large metadata
            if "metadata" in optimized_message:
                del optimized_message["metadata"]
        
        elif profile.capability_level == DeviceCapabilityLevel.MEDIUM:
            # For medium devices, keep more data but still optimize
            if "payload" in optimized_message and isinstance(optimized_message["payload"], dict):
                # Remove any large arrays or nested objects
                for key, value in list(optimized_message["payload"].items()):
                    if isinstance(value, list) and len(value) > 10:
                        optimized_message["payload"][key] = value[:10]
                    elif isinstance(value, dict) and len(json.dumps(value).encode('utf-8')) > 1000:
                        # Keep only top-level keys for large nested objects
                        optimized_message["payload"][key] = {k: "..." for k in value.keys()}
        
        # Check final size
        optimized_json = json.dumps(optimized_message)
        optimized_size = len(optimized_json.encode('utf-8'))
        
        if optimized_size > profile.max_message_size:
            self.logger.warning(f"Message for device {device_id} still too large after optimization: {optimized_size} > {profile.max_message_size}")
            
            # As a last resort, create a minimal message with error
            return {
                "message_type": "error",
                "error": "Message too large for device",
                "original_message_id": message.get("message_id", "unknown"),
                "original_size": message_size,
                "max_size": profile.max_message_size
            }
        
        return optimized_message

    async def send_message_to_device(
        self,
        device_id: str,
        message: Dict[str, Any],
        optimize: bool = True
    ) -> Dict[str, Any]:
        """Send a message to a device."""
        # Get device profile
        profile = await self.get_device_profile(device_id)
        if not profile:
            self.logger.error(f"Device {device_id} not found")
            return {
                "success": False,
                "error": "Device not found"
            }
        
        # Check if device is offline
        if profile.connection_type == ConnectionType.OFFLINE:
            self.logger.info(f"Device {device_id} is offline, storing message for later delivery")
            
            # Store message for offline delivery
            offline_message = await self._store_offline_message(
                target_device_id=device_id,
                message=message
            )
            
            return {
                "success": True,
                "offline": True,
                "message_id": offline_message.message_id
            }
        
        # Optimize message if requested
        if optimize:
            message = await self.optimize_message_for_device(device_id, message)
        
        # Check if device has callback registered
        callback = self.device_callbacks.get(device_id)
        if callback:
            try:
                # Call device callback
                result = await callback("message", message)
                
                if result.get("success", False):
                    self.logger.debug(f"Successfully sent message to device {device_id}")
                    return {
                        "success": True,
                        "result": result
                    }
                else:
                    self.logger.warning(f"Failed to send message to device {device_id}: {result.get('error', 'Unknown error')}")
                    return {
                        "success": False,
                        "error": result.get("error", "Unknown error")
                    }
            except Exception as e:
                self.logger.error(f"Error calling device callback for {device_id}: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error calling device callback: {str(e)}"
                }
        else:
            # In a real implementation, this would send the message through another channel
            # For this simulation, we'll just log it
            self.logger.info(f"Would send message to device {device_id} (no callback registered)")
            
            return {
                "success": True,
                "note": "Message would be sent through default channel"
            }

    # --- Offline Messaging ---

    async def _store_offline_message(
        self,
        target_device_id: str,
        message: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        ttl: Optional[int] = None
    ) -> OfflineMessage:
        """Store a message for offline delivery."""
        # Generate message ID
        message_id = str(uuid.uuid4())
        
        # Calculate expiration time
        expires_at = None
        if ttl is not None:
            expires_at = time.time() + ttl
        
        # Create offline message
        offline_message = OfflineMessage(
            message_id=message_id,
            target_device_id=target_device_id,
            message=message,
            created_at=time.time(),
            expires_at=expires_at,
            priority=priority
        )
        
        # Store message
        async with self.lock:
            self.offline_messages[message_id] = offline_message
        
        self.logger.debug(f"Stored offline message {message_id} for device {target_device_id}")
        return offline_message

    async def _deliver_offline_messages(self, device_id: str) -> Dict[str, Any]:
        """Deliver stored offline messages to a device."""
        # Get device profile
        profile = await self.get_device_profile(device_id)
        if not profile:
            self.logger.error(f"Device {device_id} not found")
            return {
                "success": False,
                "error": "Device not found"
            }
        
        # Check if device is online
        if profile.connection_type == ConnectionType.OFFLINE:
            self.logger.warning(f"Device {device_id} is offline, cannot deliver messages")
            return {
                "success": False,
                "error": "Device is offline"
            }
        
        # Get messages for this device
        async with self.lock:
            device_messages = [
                msg for msg in self.offline_messages.values()
                if msg.target_device_id == device_id
            ]
            
            # Sort by priority and creation time
            device_messages.sort(
                key=lambda msg: (
                    # Higher priority first
                    0 if msg.priority == MessagePriority.CRITICAL else
                    1 if msg.priority == MessagePriority.HIGH else
                    2 if msg.priority == MessagePriority.NORMAL else 3,
                    # Older messages first
                    msg.created_at
                )
            )
        
        if not device_messages:
            self.logger.debug(f"No offline messages for device {device_id}")
            return {
                "success": True,
                "delivered": 0
            }
        
        # Deliver messages
        delivered = 0
        failed = 0
        
        for offline_msg in device_messages:
            # Check if message has expired
            if offline_msg.expires_at and offline_msg.expires_at < time.time():
                self.logger.debug(f"Offline message {offline_msg.message_id} has expired, removing")
                
                async with self.lock:
                    if offline_msg.message_id in self.offline_messages:
                        del self.offline_messages[offline_msg.message_id]
                
                continue
            
            # Try to deliver message
            result = await self.send_message_to_device(
                device_id=device_id,
                message=offline_msg.message,
                optimize=True
            )
            
            if result.get("success", False) and not result.get("offline", False):
                # Message delivered successfully
                delivered += 1
                
                # Remove from offline storage
                async with self.lock:
                    if offline_msg.message_id in self.offline_messages:
                        del self.offline_messages[offline_msg.message_id]
            else:
                # Delivery failed
                failed += 1
                
                # Update delivery attempts
                async with self.lock:
                    if offline_msg.message_id in self.offline_messages:
                        self.offline_messages[offline_msg.message_id].delivery_attempts += 1
                        self.offline_messages[offline_msg.message_id].last_attempt = time.time()
        
        self.logger.info(f"Delivered {delivered} offline messages to device {device_id}, {failed} failed")
        
        return {
            "success": True,
            "delivered": delivered,
            "failed": failed
        }

    async def get_offline_messages(
        self,
        device_id: Optional[str] = None,
        include_expired: bool = False
    ) -> List[OfflineMessage]:
        """Get offline messages for a device."""
        now = time.time()
        
        async with self.lock:
            if device_id:
                # Get messages for specific device
                messages = [
                    msg for msg in self.offline_messages.values()
                    if msg.target_device_id == device_id and
                    (include_expired or not msg.expires_at or msg.expires_at > now)
                ]
            else:
                # Get all messages
                messages = [
                    msg for msg in self.offline_messages.values()
                    if include_expired or not msg.expires_at or msg.expires_at > now
                ]
        
        return messages

    async def clear_expired_messages(self) -> int:
        """Clear expired offline messages."""
        now = time.time()
        removed = 0
        
        async with self.lock:
            # Find expired messages
            expired_ids = [
                msg_id for msg_id, msg in self.offline_messages.items()
                if msg.expires_at and msg.expires_at < now
            ]
            
            # Remove expired messages
            for msg_id in expired_ids:
                del self.offline_messages[msg_id]
                removed += 1
        
        self.logger.info(f"Cleared {removed} expired offline messages")
        return removed

    # --- Message Processing ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "register_device":
                params = msg_obj.params
                try:
                    profile = await self.register_device(
                        device_id=params.get("device_id", str(uuid.uuid4())),
                        capability_level=DeviceCapabilityLevel(params.get("capability_level", "medium")),
                        connection_type=ConnectionType(params.get("connection_type", "wifi")),
                        max_message_size=params.get("max_message_size", 1024 * 1024),  # 1MB default
                        supports_compression=params.get("supports_compression", True),
                        supports_encryption=params.get("supports_encryption", True),
                        battery_constrained=params.get("battery_constrained", False),
                        cpu_constrained=params.get("cpu_constrained", False),
                        memory_constrained=params.get("memory_constrained", False),
                        storage_constrained=params.get("storage_constrained", False),
                        metadata=params.get("metadata")
                    )
                    response_payload = profile.to_dict()
                except Exception as e:
                    status = MessageStatus.FAILED
                    response_payload = {"error": f"Failed to register device: {str(e)}"}
            
            elif msg_obj.command == "update_device_status":
                params = msg_obj.params
                if "device_id" in params:
                    connection_type = None
                    if "connection_type" in params:
                        connection_type = ConnectionType(params["connection_type"])
                    
                    profile = await self.update_device_status(
                        device_id=params["device_id"],
                        connection_type=connection_type,
                        metadata_updates=params.get("metadata_updates")
                    )
                    
                    if profile:
                        response_payload = profile.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Device not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing device_id parameter"}
            
            elif msg_obj.command == "initiate_agent_transfer":
                params = msg_obj.params
                if all(k in params for k in ["agent_id", "source_device_id", "target_device_id", "agent_state"]):
                    try:
                        transfer = await self.initiate_agent_transfer(
                            agent_id=params["agent_id"],
                            source_device_id=params["source_device_id"],
                            target_device_id=params["target_device_id"],
                            agent_state=params["agent_state"],
                            metadata=params.get("metadata")
                        )
                        response_payload = transfer.to_dict()
                    except Exception as e:
                        status = MessageStatus.FAILED
                        response_payload = {"error": f"Failed to initiate agent transfer: {str(e)}"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing required parameters"}
            
            elif msg_obj.command == "cancel_agent_transfer":
                params = msg_obj.params
                if "transfer_id" in params:
                    success = await self.cancel_agent_transfer(params["transfer_id"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing transfer_id parameter"}
            
            elif msg_obj.command == "send_message_to_device":
                params = msg_obj.params
                if "device_id" in params and "message" in params:
                    result = await self.send_message_to_device(
                        device_id=params["device_id"],
                        message=params["message"],
                        optimize=params.get("optimize", True)
                    )
                    response_payload = result
                    if not result.get("success", False):
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing required parameters"}
            
            elif msg_obj.command == "clear_expired_messages":
                removed = await self.clear_expired_messages()
                response_payload = {"removed": removed}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_device_profile":
                params = msg_obj.params
                if "device_id" in params:
                    profile = await self.get_device_profile(params["device_id"])
                    if profile:
                        response_payload = profile.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Device not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing device_id parameter"}
            
            elif msg_obj.query == "list_devices":
                profiles = await self.list_devices(msg_obj.params.get("filters"))
                response_payload = {"devices": [p.to_dict() for p in profiles]}
            
            elif msg_obj.query == "get_agent_transfer":
                params = msg_obj.params
                if "transfer_id" in params:
                    transfer = await self.get_agent_transfer(params["transfer_id"])
                    if transfer:
                        response_payload = transfer.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Transfer not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing transfer_id parameter"}
            
            elif msg_obj.query == "list_agent_transfers":
                params = msg_obj.params
                status_param = params.get("status")
                status_enum = None
                if status_param:
                    status_enum = AgentTransferStatus(status_param)
                
                transfers = await self.list_agent_transfers(
                    agent_id=params.get("agent_id"),
                    device_id=params.get("device_id"),
                    status=status_enum
                )
                response_payload = {"transfers": [t.to_dict() for t in transfers]}
            
            elif msg_obj.query == "get_offline_messages":
                params = msg_obj.params
                messages = await self.get_offline_messages(
                    device_id=params.get("device_id"),
                    include_expired=params.get("include_expired", False)
                )
                response_payload = {"messages": [m.to_dict() for m in messages]}
            
            elif msg_obj.query == "optimize_message_for_device":
                params = msg_obj.params
                if "device_id" in params and "message" in params:
                    optimized = await self.optimize_message_for_device(
                        device_id=params["device_id"],
                        message=params["message"]
                    )
                    response_payload = {"optimized_message": optimized}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing required parameters"}
            
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
            num_devices = len(self.device_profiles)
            num_transfers = len(self.agent_transfers)
            num_offline = len(self.offline_messages)
            
            # Count online devices
            online_devices = sum(1 for p in self.device_profiles.values() if p.connection_type != ConnectionType.OFFLINE)
        
        return {
            "status": "healthy",
            "total_devices": num_devices,
            "online_devices": online_devices,
            "offline_devices": num_devices - online_devices,
            "agent_transfers": num_transfers,
            "offline_messages": num_offline
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
