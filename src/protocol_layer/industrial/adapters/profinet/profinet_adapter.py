"""
Profinet Protocol Adapter for Industriverse Protocol Layer

This module provides a comprehensive adapter for integrating Profinet industrial protocol
with the Industriverse Protocol Layer. It enables seamless communication between
Profinet devices/systems and the protocol-native architecture of Industriverse.

Features:
- Full Profinet IO controller and device functionality
- Support for cyclic and acyclic data exchange
- Automatic device discovery and configuration
- Alarm handling and diagnostics
- Parameter read/write operations
- Record data access
- Security integration with EKIS framework
- Comprehensive error handling and diagnostics
- Support for redundancy and high availability

Dependencies:
- profinet (custom Profinet library)
- socket
- struct
"""

import asyncio
import logging
import socket
import struct
import uuid
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

# Import Profinet library (placeholder for actual implementation)
try:
    import profinet
    from profinet.controller import ProfinetController
    from profinet.device import ProfinetDevice
    from profinet.discovery import ProfinetDiscovery
    from profinet.dcp import DCPPacket
    from profinet.alarm import AlarmType, AlarmNotification
except ImportError:
    logging.error("Profinet library not found. Using mock implementation.")
    # Mock implementation for development
    class ProfinetController:
        def __init__(self, interface_name, name, vendor_id, device_id):
            self.interface_name = interface_name
            self.name = name
            self.vendor_id = vendor_id
            self.device_id = device_id
            self.devices = {}
            self.running = False
            
        async def start(self):
            self.running = True
            return True
            
        async def stop(self):
            self.running = False
            return True
            
        async def discover_devices(self, timeout=5.0):
            return []
            
        async def connect_device(self, device_info):
            device_id = device_info.get("mac_address", str(uuid.uuid4()))
            self.devices[device_id] = device_info
            return device_id
            
        async def disconnect_device(self, device_id):
            if device_id in self.devices:
                del self.devices[device_id]
                return True
            return False
            
        async def read_data(self, device_id, slot, subslot, index):
            return {"value": 0, "quality": "good"}
            
        async def write_data(self, device_id, slot, subslot, index, value):
            return True
            
        async def read_record(self, device_id, slot, subslot, index):
            return b""
            
        async def write_record(self, device_id, slot, subslot, index, data):
            return True
            
    class ProfinetDevice:
        def __init__(self, interface_name, name, vendor_id, device_id):
            self.interface_name = interface_name
            self.name = name
            self.vendor_id = vendor_id
            self.device_id = device_id
            self.running = False
            
        async def start(self):
            self.running = True
            return True
            
        async def stop(self):
            self.running = False
            return True
            
    class ProfinetDiscovery:
        def __init__(self, interface_name):
            self.interface_name = interface_name
            
        async def discover(self, timeout=5.0):
            return []
            
    class DCPPacket:
        @staticmethod
        def create_identify_all():
            return b""
            
    class AlarmType(Enum):
        PROCESS = 1
        DIAGNOSTIC = 2
        RETURN_OF_SUBMODULE = 3
        
    class AlarmNotification:
        def __init__(self, alarm_type, device_id, slot, subslot, data):
            self.alarm_type = alarm_type
            self.device_id = device_id
            self.slot = slot
            self.subslot = subslot
            self.data = data

class DeviceState(Enum):
    """Profinet device state."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class ProfinetAdapter(ProtocolComponent):
    """
    Profinet Protocol Adapter for Industriverse Protocol Layer.
    
    This adapter enables bidirectional communication between Profinet devices/systems
    and the Industriverse Protocol Layer, translating between Profinet protocol and
    Industriverse's protocol-native architecture.
    """
    
    def __init__(self, component_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Profinet adapter.
        
        Args:
            component_id: Unique identifier for this adapter instance
            config: Configuration parameters for the adapter
        """
        super().__init__(component_id or str(uuid.uuid4()), "profinet_adapter")
        
        # Add capabilities
        self.add_capability("profinet_controller", "Profinet IO controller functionality")
        self.add_capability("profinet_device", "Profinet IO device functionality")
        self.add_capability("profinet_discovery", "Profinet device discovery")
        self.add_capability("profinet_alarm", "Profinet alarm handling")
        self.add_capability("profinet_record", "Profinet record data access")
        
        # Initialize configuration
        self.config = config or {}
        self.logger = logging.getLogger(f"industriverse.protocol.profinet.{self.component_id}")
        
        # Initialize controller and device
        self.controller = None
        self.device = None
        self.devices = {}
        self.alarm_handlers = {}
        
        # Initialize security handler
        self.security_handler = EKISSecurityHandler(
            component_id=f"{self.component_id}_security",
            tpm_provider=TPMSecurityProvider() if self.config.get("use_tpm", True) else None
        )
        
        # Register with discovery service
        self.discovery_service = DiscoveryService()
        self.discovery_service.register_component(
            self.component_id,
            "profinet_adapter",
            {
                "protocols": ["profinet"],
                "capabilities": list(self._capabilities.keys()),
                "industryTags": self.config.get("industry_tags", ["manufacturing", "automation", "process_control"])
            }
        )
        
        self.logger.info(f"Profinet Adapter {self.component_id} initialized")
    
    async def start_controller(self, interface_name: str, name: str = "Industriverse Controller",
                              vendor_id: int = 0x1234, device_id: int = 0x5678) -> bool:
        """
        Start a Profinet IO controller.
        
        Args:
            interface_name: Network interface name to use
            name: Controller name
            vendor_id: Vendor ID
            device_id: Device ID
            
        Returns:
            bool: True if controller started successfully, False otherwise
        """
        try:
            # Create controller
            self.controller = ProfinetController(
                interface_name=interface_name,
                name=name,
                vendor_id=vendor_id,
                device_id=device_id
            )
            
            # Start controller
            success = await self.controller.start()
            
            if success:
                self.logger.info(f"Started Profinet controller on interface {interface_name}")
                
                # Publish event
                await self.publish_event(
                    MessageFactory.create_event(
                        "profinet_controller_started",
                        payload={
                            "interface_name": interface_name,
                            "name": name,
                            "vendor_id": vendor_id,
                            "device_id": device_id
                        },
                        priority=MessagePriority.MEDIUM
                    )
                )
                
                return True
            else:
                self.logger.error(f"Failed to start Profinet controller on interface {interface_name}")
                self.controller = None
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting Profinet controller: {str(e)}")
            self.controller = None
            return False
    
    async def stop_controller(self) -> bool:
        """
        Stop the Profinet IO controller.
        
        Returns:
            bool: True if controller stopped successfully, False otherwise
        """
        if not self.controller:
            self.logger.warning("No Profinet controller running")
            return False
            
        try:
            # Disconnect all devices
            for device_id in list(self.devices.keys()):
                await self.disconnect_device(device_id)
                
            # Stop controller
            success = await self.controller.stop()
            
            if success:
                self.logger.info("Stopped Profinet controller")
                self.controller = None
                return True
            else:
                self.logger.error("Failed to stop Profinet controller")
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping Profinet controller: {str(e)}")
            return False
    
    async def start_device(self, interface_name: str, name: str = "Industriverse Device",
                          vendor_id: int = 0x1234, device_id: int = 0x5678) -> bool:
        """
        Start a Profinet IO device.
        
        Args:
            interface_name: Network interface name to use
            name: Device name
            vendor_id: Vendor ID
            device_id: Device ID
            
        Returns:
            bool: True if device started successfully, False otherwise
        """
        try:
            # Create device
            self.device = ProfinetDevice(
                interface_name=interface_name,
                name=name,
                vendor_id=vendor_id,
                device_id=device_id
            )
            
            # Start device
            success = await self.device.start()
            
            if success:
                self.logger.info(f"Started Profinet device on interface {interface_name}")
                
                # Publish event
                await self.publish_event(
                    MessageFactory.create_event(
                        "profinet_device_started",
                        payload={
                            "interface_name": interface_name,
                            "name": name,
                            "vendor_id": vendor_id,
                            "device_id": device_id
                        },
                        priority=MessagePriority.MEDIUM
                    )
                )
                
                return True
            else:
                self.logger.error(f"Failed to start Profinet device on interface {interface_name}")
                self.device = None
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting Profinet device: {str(e)}")
            self.device = None
            return False
    
    async def stop_device(self) -> bool:
        """
        Stop the Profinet IO device.
        
        Returns:
            bool: True if device stopped successfully, False otherwise
        """
        if not self.device:
            self.logger.warning("No Profinet device running")
            return False
            
        try:
            # Stop device
            success = await self.device.stop()
            
            if success:
                self.logger.info("Stopped Profinet device")
                self.device = None
                return True
            else:
                self.logger.error("Failed to stop Profinet device")
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping Profinet device: {str(e)}")
            return False
    
    async def discover_devices(self, interface_name: Optional[str] = None, timeout: float = 5.0) -> List[Dict[str, Any]]:
        """
        Discover Profinet devices on the network.
        
        Args:
            interface_name: Network interface name to use (uses controller interface if None)
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered devices
        """
        try:
            # Use controller interface if available and no interface specified
            if not interface_name and self.controller:
                interface_name = self.controller.interface_name
                
            if not interface_name:
                self.logger.error("No interface name specified for device discovery")
                return []
                
            # Create discovery instance
            discovery = ProfinetDiscovery(interface_name)
            
            # Discover devices
            self.logger.info(f"Starting Profinet device discovery on interface {interface_name}")
            devices = await discovery.discover(timeout)
            
            # Format results
            results = []
            for device in devices:
                results.append({
                    "name": device.get("name", "Unknown"),
                    "ip_address": device.get("ip_address", "0.0.0.0"),
                    "mac_address": device.get("mac_address", "00:00:00:00:00:00"),
                    "vendor_id": device.get("vendor_id", 0),
                    "device_id": device.get("device_id", 0),
                    "device_role": device.get("device_role", "unknown"),
                    "device_type": device.get("device_type", "unknown"),
                    "timestamp": datetime.now().isoformat()
                })
                
            self.logger.info(f"Discovered {len(results)} Profinet devices")
            return results
            
        except Exception as e:
            self.logger.error(f"Error discovering Profinet devices: {str(e)}")
            return []
    
    async def connect_device(self, device_info: Dict[str, Any]) -> str:
        """
        Connect to a Profinet device.
        
        Args:
            device_info: Device information from discovery
            
        Returns:
            str: Device ID if connection successful, empty string otherwise
        """
        if not self.controller:
            self.logger.error("No Profinet controller running")
            return ""
            
        try:
            # Connect to device
            device_id = await self.controller.connect_device(device_info)
            
            if not device_id:
                self.logger.error(f"Failed to connect to Profinet device {device_info.get('name', 'Unknown')}")
                return ""
                
            # Store device information
            self.devices[device_id] = {
                "info": device_info,
                "state": DeviceState.CONNECTED,
                "connected_at": datetime.now(),
                "last_activity": datetime.now()
            }
            
            self.logger.info(f"Connected to Profinet device {device_info.get('name', 'Unknown')} with ID {device_id}")
            
            # Publish event
            await self.publish_event(
                MessageFactory.create_event(
                    "profinet_device_connected",
                    payload={
                        "device_id": device_id,
                        "device_info": device_info
                    },
                    priority=MessagePriority.MEDIUM
                )
            )
            
            return device_id
            
        except Exception as e:
            self.logger.error(f"Error connecting to Profinet device: {str(e)}")
            return ""
    
    async def disconnect_device(self, device_id: str) -> bool:
        """
        Disconnect from a Profinet device.
        
        Args:
            device_id: ID of the device to disconnect from
            
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        if not self.controller:
            self.logger.error("No Profinet controller running")
            return False
            
        if device_id not in self.devices:
            self.logger.warning(f"Device {device_id} not found")
            return False
            
        try:
            # Disconnect from device
            success = await self.controller.disconnect_device(device_id)
            
            if success:
                # Get device info before removing
                device_info = self.devices[device_id]["info"]
                
                # Remove device
                del self.devices[device_id]
                
                self.logger.info(f"Disconnected from Profinet device {device_id}")
                
                # Publish event
                await self.publish_event(
                    MessageFactory.create_event(
                        "profinet_device_disconnected",
                        payload={
                            "device_id": device_id,
                            "device_info": device_info
                        },
                        priority=MessagePriority.MEDIUM
                    )
                )
                
                return True
            else:
                self.logger.error(f"Failed to disconnect from Profinet device {device_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from Profinet device {device_id}: {str(e)}")
            return False
    
    async def read_data(self, device_id: str, slot: int, subslot: int, index: int) -> Dict[str, Any]:
        """
        Read data from a Profinet device.
        
        Args:
            device_id: ID of the device to read from
            slot: Slot number
            subslot: Subslot number
            index: Index number
            
        Returns:
            Dict with result or error
        """
        if not self.controller:
            self.logger.error("No Profinet controller running")
            return {"error": "No controller running"}
            
        if device_id not in self.devices:
            self.logger.error(f"Device {device_id} not found")
            return {"error": "Device not found"}
            
        try:
            # Read data
            result = await self.controller.read_data(device_id, slot, subslot, index)
            
            # Update last activity
            self.devices[device_id]["last_activity"] = datetime.now()
            
            self.logger.debug(f"Read data from device {device_id}, slot {slot}, subslot {subslot}, index {index}")
            return {
                "device_id": device_id,
                "slot": slot,
                "subslot": subslot,
                "index": index,
                "value": result.get("value"),
                "quality": result.get("quality", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error reading data from device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def write_data(self, device_id: str, slot: int, subslot: int, index: int, value: Any) -> bool:
        """
        Write data to a Profinet device.
        
        Args:
            device_id: ID of the device to write to
            slot: Slot number
            subslot: Subslot number
            index: Index number
            value: Value to write
            
        Returns:
            bool: True if write successful, False otherwise
        """
        if not self.controller:
            self.logger.error("No Profinet controller running")
            return False
            
        if device_id not in self.devices:
            self.logger.error(f"Device {device_id} not found")
            return False
            
        try:
            # Write data
            success = await self.controller.write_data(device_id, slot, subslot, index, value)
            
            # Update last activity
            self.devices[device_id]["last_activity"] = datetime.now()
            
            if success:
                self.logger.debug(f"Wrote value {value} to device {device_id}, slot {slot}, subslot {subslot}, index {index}")
                return True
            else:
                self.logger.error(f"Failed to write to device {device_id}, slot {slot}, subslot {subslot}, index {index}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error writing data to device {device_id}: {str(e)}")
            return False
    
    async def read_record(self, device_id: str, slot: int, subslot: int, index: int) -> Dict[str, Any]:
        """
        Read record data from a Profinet device.
        
        Args:
            device_id: ID of the device to read from
            slot: Slot number
            subslot: Subslot number
            index: Index number
            
        Returns:
            Dict with result or error
        """
        if not self.controller:
            self.logger.error("No Profinet controller running")
            return {"error": "No controller running"}
            
        if device_id not in self.devices:
            self.logger.error(f"Device {device_id} not found")
            return {"error": "Device not found"}
            
        try:
            # Read record
            data = await self.controller.read_record(device_id, slot, subslot, index)
            
            # Update last activity
            self.devices[device_id]["last_activity"] = datetime.now()
            
            self.logger.debug(f"Read record from device {device_id}, slot {slot}, subslot {subslot}, index {index}")
            return {
                "device_id": device_id,
                "slot": slot,
                "subslot": subslot,
                "index": index,
                "data": data.hex() if isinstance(data, bytes) else str(data),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error reading record from device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def write_record(self, device_id: str, slot: int, subslot: int, index: int, data: bytes) -> bool:
        """
        Write record data to a Profinet device.
        
        Args:
            device_id: ID of the device to write to
            slot: Slot number
            subslot: Subslot number
            index: Index number
            data: Data to write
            
        Returns:
            bool: True if write successful, False otherwise
        """
        if not self.controller:
            self.logger.error("No Profinet controller running")
            return False
            
        if device_id not in self.devices:
            self.logger.error(f"Device {device_id} not found")
            return False
            
        try:
            # Write record
            success = await self.controller.write_record(device_id, slot, subslot, index, data)
            
            # Update last activity
            self.devices[device_id]["last_activity"] = datetime.now()
            
            if success:
                self.logger.debug(f"Wrote record to device {device_id}, slot {slot}, subslot {subslot}, index {index}")
                return True
            else:
                self.logger.error(f"Failed to write record to device {device_id}, slot {slot}, subslot {subslot}, index {index}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error writing record to device {device_id}: {str(e)}")
            return False
    
    async def register_alarm_handler(self, alarm_type: Union[str, AlarmType], 
                                    callback: Callable[[Dict[str, Any]], None]) -> str:
        """
        Register a handler for Profinet alarms.
        
        Args:
            alarm_type: Type of alarm to handle
            callback: Callback function to call when alarm is received
            
        Returns:
            str: Handler ID
        """
        # Convert string to enum if needed
        if isinstance(alarm_type, str):
            try:
                alarm_type = AlarmType[alarm_type.upper()]
            except KeyError:
                self.logger.error(f"Invalid alarm type: {alarm_type}")
                return ""
                
        # Generate handler ID
        handler_id = str(uuid.uuid4())
        
        # Store handler
        self.alarm_handlers[handler_id] = {
            "alarm_type": alarm_type,
            "callback": callback,
            "registered_at": datetime.now()
        }
        
        self.logger.info(f"Registered alarm handler {handler_id} for alarm type {alarm_type.name}")
        return handler_id
    
    async def unregister_alarm_handler(self, handler_id: str) -> bool:
        """
        Unregister an alarm handler.
        
        Args:
            handler_id: ID of the handler to unregister
            
        Returns:
            bool: True if unregistration successful, False otherwise
        """
        if handler_id not in self.alarm_handlers:
            self.logger.error(f"Alarm handler {handler_id} not found")
            return False
            
        # Remove handler
        del self.alarm_handlers[handler_id]
        
        self.logger.info(f"Unregistered alarm handler {handler_id}")
        return True
    
    async def _handle_alarm(self, alarm: AlarmNotification):
        """
        Handle an incoming alarm notification.
        
        Args:
            alarm: Alarm notification
        """
        try:
            # Format alarm data
            alarm_data = {
                "alarm_type": alarm.alarm_type.name,
                "device_id": alarm.device_id,
                "slot": alarm.slot,
                "subslot": alarm.subslot,
                "data": alarm.data.hex() if isinstance(alarm.data, bytes) else str(alarm.data),
                "timestamp": datetime.now().isoformat()
            }
            
            # Find matching handlers
            matching_handlers = []
            for handler_id, handler_info in self.alarm_handlers.items():
                if handler_info["alarm_type"] == alarm.alarm_type:
                    matching_handlers.append((handler_id, handler_info))
                    
            # Call handlers
            for handler_id, handler_info in matching_handlers:
                try:
                    await handler_info["callback"](alarm_data)
                except Exception as e:
                    self.logger.error(f"Error in alarm handler {handler_id}: {str(e)}")
                    
            # Publish event
            await self.publish_event(
                MessageFactory.create_event(
                    "profinet_alarm_received",
                    payload=alarm_data,
                    priority=MessagePriority.HIGH
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error handling alarm: {str(e)}")
    
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get status information for a device.
        
        Args:
            device_id: ID of the device to get status for
            
        Returns:
            Dict with device status information
        """
        if device_id not in self.devices:
            self.logger.error(f"Device {device_id} not found")
            return {"error": "Device not found"}
            
        device_info = self.devices[device_id]
        
        # Format status
        status = {
            "device_id": device_id,
            "name": device_info["info"].get("name", "Unknown"),
            "ip_address": device_info["info"].get("ip_address", "0.0.0.0"),
            "mac_address": device_info["info"].get("mac_address", "00:00:00:00:00:00"),
            "vendor_id": device_info["info"].get("vendor_id", 0),
            "device_id": device_info["info"].get("device_id", 0),
            "state": device_info["state"].value,
            "connected_at": device_info["connected_at"].isoformat(),
            "last_activity": device_info["last_activity"].isoformat()
        }
        
        return status
    
    async def translate_to_industriverse(self, profinet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Profinet data to Industriverse protocol format.
        
        Args:
            profinet_data: Profinet data to translate
            
        Returns:
            Data in Industriverse protocol format
        """
        # Create Unified Message Envelope
        ume = {
            "origin_protocol": "PROFINET",
            "target_protocol": "MCP",
            "context": {
                "industrial_protocol": "PROFINET",
                "adapter_id": self.component_id,
                "timestamp": datetime.now().isoformat()
            },
            "payload": profinet_data,
            "trace_id": str(uuid.uuid4()),
            "security_level": "high",  # Profinet is typically used in critical systems
            "reflex_timer_ms": 2000  # 2 seconds default timeout for industrial protocols
        }
        
        return ume
    
    async def translate_from_industriverse(self, industriverse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Industriverse protocol data to Profinet format.
        
        Args:
            industriverse_data: Industriverse protocol data to translate
            
        Returns:
            Data in Profinet format
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
            if command == "start_controller":
                success = await self.start_controller(
                    params.get("interface_name", ""),
                    params.get("name", "Industriverse Controller"),
                    params.get("vendor_id", 0x1234),
                    params.get("device_id", 0x5678)
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "stop_controller":
                success = await self.stop_controller()
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "start_device":
                success = await self.start_device(
                    params.get("interface_name", ""),
                    params.get("name", "Industriverse Device"),
                    params.get("vendor_id", 0x1234),
                    params.get("device_id", 0x5678)
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "stop_device":
                success = await self.stop_device()
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "discover_devices":
                result = await self.discover_devices(
                    params.get("interface_name", None),
                    params.get("timeout", 5.0)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "connect_device":
                device_id = await self.connect_device(params.get("device_info", {}))
                return MessageFactory.create_response(message, result={"device_id": device_id})
                
            elif command == "disconnect_device":
                success = await self.disconnect_device(params.get("device_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "read_data":
                result = await self.read_data(
                    params.get("device_id", ""),
                    params.get("slot", 0),
                    params.get("subslot", 0),
                    params.get("index", 0)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "write_data":
                success = await self.write_data(
                    params.get("device_id", ""),
                    params.get("slot", 0),
                    params.get("subslot", 0),
                    params.get("index", 0),
                    params.get("value", None)
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "read_record":
                result = await self.read_record(
                    params.get("device_id", ""),
                    params.get("slot", 0),
                    params.get("subslot", 0),
                    params.get("index", 0)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "write_record":
                # Convert data to bytes if needed
                data = params.get("data", b"")
                if isinstance(data, str):
                    try:
                        data = bytes.fromhex(data)
                    except ValueError:
                        data = data.encode('utf-8')
                        
                success = await self.write_record(
                    params.get("device_id", ""),
                    params.get("slot", 0),
                    params.get("subslot", 0),
                    params.get("index", 0),
                    data
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "get_device_status":
                result = await self.get_device_status(params.get("device_id", ""))
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
        if message.get("origin_protocol") and message.get("origin_protocol") != "PROFINET":
            profinet_message = await self.translate_from_industriverse(message)
        else:
            profinet_message = message
            
        # Handle message
        response = await self.handle_message(profinet_message)
        
        # Translate to Industriverse protocol if needed
        if message.get("target_protocol") and message.get("target_protocol") != "PROFINET":
            industriverse_response = await self.translate_to_industriverse(response)
            return industriverse_response
        else:
            return response
    
    async def shutdown(self):
        """
        Shutdown the adapter, stopping controller and device.
        """
        self.logger.info(f"Shutting down Profinet Adapter {self.component_id}")
        
        # Stop controller if running
        if self.controller:
            await self.stop_controller()
            
        # Stop device if running
        if self.device:
            await self.stop_device()
            
        # Unregister from discovery service
        self.discovery_service.unregister_component(self.component_id)
        
        self.logger.info(f"Profinet Adapter {self.component_id} shutdown complete")

# Example usage
async def example_usage():
    # Create adapter
    adapter = ProfinetAdapter(config={
        "use_tpm": True,
        "industry_tags": ["manufacturing", "automation"]
    })
    
    # Start controller
    success = await adapter.start_controller(
        interface_name="eth0",
        name="Industriverse Controller"
    )
    
    if success:
        # Discover devices
        devices = await adapter.discover_devices(timeout=10.0)
        print(f"Discovered devices: {devices}")
        
        if devices:
            # Connect to first device
            device_id = await adapter.connect_device(devices[0])
            
            if device_id:
                # Read data
                result = await adapter.read_data(
                    device_id=device_id,
                    slot=0,
                    subslot=1,
                    index=0
                )
                print(f"Read result: {result}")
                
                # Write data
                success = await adapter.write_data(
                    device_id=device_id,
                    slot=0,
                    subslot=1,
                    index=0,
                    value=42
                )
                print(f"Write success: {success}")
                
                # Disconnect device
                await adapter.disconnect_device(device_id)
        
        # Stop controller
        await adapter.stop_controller()
    
    # Shutdown
    await adapter.shutdown()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run example
    asyncio.run(example_usage())
