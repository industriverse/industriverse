"""
Modbus Protocol Adapter for Industriverse Protocol Layer

This module provides a comprehensive adapter for integrating Modbus industrial protocol
with the Industriverse Protocol Layer. It enables seamless communication between
Modbus devices/systems and the protocol-native architecture of Industriverse.

Features:
- Support for Modbus TCP, RTU, and ASCII variants
- Bidirectional translation between Modbus and Industriverse protocols
- Support for all Modbus function codes
- Security integration with EKIS framework
- Automatic device discovery
- Polling and event-based data acquisition
- Batch operations for efficient communication
- Comprehensive error handling and diagnostics
- Support for custom function codes

Dependencies:
- pymodbus
- serial (for RTU/ASCII)
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# Import Protocol Layer base components
from protocols.protocol_base import ProtocolComponent
from protocols.message_formats import MessageFactory, MessagePriority, MessageType
from protocols.discovery_service import DiscoveryService

# Import EKIS security components
from security.ekis.tpm_integration import TPMSecurityProvider
from security.ekis.security_handler import EKISSecurityHandler

# Import Modbus library
try:
    import pymodbus
    from pymodbus.client import AsyncModbusTcpClient, AsyncModbusSerialClient
    from pymodbus.constants import Endian
    from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
    from pymodbus.exceptions import ModbusException
    from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer, ModbusTcpFramer
except ImportError:
    logging.error("Modbus library not found. Please install pymodbus package.")
    pymodbus = None
    AsyncModbusTcpClient = None
    AsyncModbusSerialClient = None

class ModbusVariant(Enum):
    """Modbus protocol variants."""
    TCP = "tcp"
    RTU = "rtu"
    ASCII = "ascii"

class ModbusDataType(Enum):
    """Data types for Modbus registers."""
    BOOL = "bool"
    UINT16 = "uint16"
    INT16 = "int16"
    UINT32 = "uint32"
    INT32 = "int32"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    STRING = "string"

class ModbusAdapter(ProtocolComponent):
    """
    Modbus Protocol Adapter for Industriverse Protocol Layer.
    
    This adapter enables bidirectional communication between Modbus devices/systems
    and the Industriverse Protocol Layer, translating between Modbus protocol and
    Industriverse's protocol-native architecture.
    """
    
    def __init__(self, component_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Modbus adapter.
        
        Args:
            component_id: Unique identifier for this adapter instance
            config: Configuration parameters for the adapter
        """
        super().__init__(component_id or str(uuid.uuid4()), "modbus_adapter")
        
        # Add capabilities
        self.add_capability("modbus_tcp", "Modbus TCP client functionality")
        self.add_capability("modbus_rtu", "Modbus RTU client functionality")
        self.add_capability("modbus_ascii", "Modbus ASCII client functionality")
        self.add_capability("modbus_discovery", "Modbus device discovery")
        self.add_capability("modbus_polling", "Modbus polling functionality")
        self.add_capability("modbus_batch", "Modbus batch operations")
        
        # Initialize configuration
        self.config = config or {}
        self.logger = logging.getLogger(f"industriverse.protocol.modbus.{self.component_id}")
        
        # Initialize clients
        self.clients = {}
        self.polling_tasks = {}
        
        # Initialize security handler
        self.security_handler = EKISSecurityHandler(
            component_id=f"{self.component_id}_security",
            tpm_provider=TPMSecurityProvider() if self.config.get("use_tpm", True) else None
        )
        
        # Register with discovery service
        self.discovery_service = DiscoveryService()
        self.discovery_service.register_component(
            self.component_id,
            "modbus_adapter",
            {
                "protocols": ["modbus_tcp", "modbus_rtu", "modbus_ascii"],
                "capabilities": list(self._capabilities.keys()),
                "industryTags": self.config.get("industry_tags", ["manufacturing", "energy", "utilities", "oil_gas"])
            }
        )
        
        self.logger.info(f"Modbus Adapter {self.component_id} initialized")
    
    async def connect(self, device_id: str, host: Optional[str] = None, port: int = 502, 
                     variant: ModbusVariant = ModbusVariant.TCP, serial_port: Optional[str] = None,
                     baudrate: int = 9600, timeout: float = 1.0, unit_id: int = 1) -> bool:
        """
        Connect to a Modbus device.
        
        Args:
            device_id: Unique identifier for the device
            host: Host address for TCP connections
            port: Port number for TCP connections
            variant: Modbus variant (TCP, RTU, ASCII)
            serial_port: Serial port for RTU/ASCII connections
            baudrate: Baud rate for serial connections
            timeout: Connection timeout in seconds
            unit_id: Modbus unit ID (slave address)
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not pymodbus:
            self.logger.error("Modbus library not installed. Cannot connect.")
            return False
            
        try:
            # Create client based on variant
            if variant == ModbusVariant.TCP:
                if not host:
                    self.logger.error("Host address required for Modbus TCP connections")
                    return False
                    
                client = AsyncModbusTcpClient(
                    host=host,
                    port=port,
                    timeout=timeout,
                    retries=3,
                    retry_on_empty=True
                )
            else:
                if not serial_port:
                    self.logger.error("Serial port required for Modbus RTU/ASCII connections")
                    return False
                    
                framer = ModbusRtuFramer if variant == ModbusVariant.RTU else ModbusAsciiFramer
                client = AsyncModbusSerialClient(
                    port=serial_port,
                    baudrate=baudrate,
                    timeout=timeout,
                    framer=framer
                )
            
            # Connect to device
            connected = await client.connect()
            if not connected:
                self.logger.error(f"Failed to connect to Modbus device {device_id}")
                return False
                
            # Store client
            self.clients[device_id] = {
                "client": client,
                "variant": variant,
                "host": host,
                "port": port,
                "serial_port": serial_port,
                "baudrate": baudrate,
                "unit_id": unit_id,
                "connected_at": datetime.now()
            }
            
            self.logger.info(f"Connected to Modbus device {device_id}")
            
            # Publish connection event
            await self.publish_event(
                MessageFactory.create_event(
                    "modbus_client_connected",
                    payload={
                        "device_id": device_id,
                        "variant": variant.value,
                        "host": host,
                        "port": port,
                        "serial_port": serial_port,
                        "unit_id": unit_id
                    },
                    priority=MessagePriority.MEDIUM
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Modbus device {device_id}: {str(e)}")
            return False
    
    async def disconnect(self, device_id: Optional[str] = None) -> bool:
        """
        Disconnect from a Modbus device.
        
        Args:
            device_id: ID of the device to disconnect from.
                      If None, disconnect from all devices.
                      
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if device_id:
                if device_id in self.clients:
                    # Stop any polling tasks
                    if device_id in self.polling_tasks:
                        for task_id, task_info in list(self.polling_tasks.items()):
                            if task_info["device_id"] == device_id:
                                await self.stop_polling(task_id)
                    
                    # Disconnect client
                    client = self.clients[device_id]["client"]
                    client.close()
                    del self.clients[device_id]
                    self.logger.info(f"Disconnected from Modbus device {device_id}")
                    return True
                else:
                    self.logger.warning(f"Not connected to Modbus device {device_id}")
                    return False
            else:
                # Disconnect from all devices
                for dev_id, client_info in list(self.clients.items()):
                    # Stop any polling tasks
                    if dev_id in self.polling_tasks:
                        for task_id, task_info in list(self.polling_tasks.items()):
                            if task_info["device_id"] == dev_id:
                                await self.stop_polling(task_id)
                    
                    # Disconnect client
                    client = client_info["client"]
                    client.close()
                    self.logger.info(f"Disconnected from Modbus device {dev_id}")
                
                self.clients = {}
                return True
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from Modbus device: {str(e)}")
            return False
    
    async def read_coils(self, device_id: str, address: int, count: int = 1) -> Dict[str, Any]:
        """
        Read coils from a Modbus device.
        
        Args:
            device_id: ID of the device to read from
            address: Starting address of coils to read
            count: Number of coils to read
            
        Returns:
            Dict with result or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Read coils
            result = await client.read_coils(address, count, slave=unit_id)
            
            if result.isError():
                self.logger.error(f"Error reading coils from device {device_id}: {result}")
                return {"error": str(result)}
                
            # Format result
            coils = []
            for i in range(count):
                if i < len(result.bits):
                    coils.append(result.bits[i])
                else:
                    coils.append(None)
            
            self.logger.debug(f"Read {len(coils)} coils from device {device_id}")
            return {
                "device_id": device_id,
                "address": address,
                "count": count,
                "values": coils,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error reading coils from device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def read_discrete_inputs(self, device_id: str, address: int, count: int = 1) -> Dict[str, Any]:
        """
        Read discrete inputs from a Modbus device.
        
        Args:
            device_id: ID of the device to read from
            address: Starting address of discrete inputs to read
            count: Number of discrete inputs to read
            
        Returns:
            Dict with result or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Read discrete inputs
            result = await client.read_discrete_inputs(address, count, slave=unit_id)
            
            if result.isError():
                self.logger.error(f"Error reading discrete inputs from device {device_id}: {result}")
                return {"error": str(result)}
                
            # Format result
            inputs = []
            for i in range(count):
                if i < len(result.bits):
                    inputs.append(result.bits[i])
                else:
                    inputs.append(None)
            
            self.logger.debug(f"Read {len(inputs)} discrete inputs from device {device_id}")
            return {
                "device_id": device_id,
                "address": address,
                "count": count,
                "values": inputs,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error reading discrete inputs from device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def read_holding_registers(self, device_id: str, address: int, count: int = 1,
                                    data_type: Optional[ModbusDataType] = None) -> Dict[str, Any]:
        """
        Read holding registers from a Modbus device.
        
        Args:
            device_id: ID of the device to read from
            address: Starting address of registers to read
            count: Number of registers to read
            data_type: Optional data type for conversion
            
        Returns:
            Dict with result or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Read holding registers
            result = await client.read_holding_registers(address, count, slave=unit_id)
            
            if result.isError():
                self.logger.error(f"Error reading holding registers from device {device_id}: {result}")
                return {"error": str(result)}
                
            # Format result
            registers = [r for r in result.registers]
            
            # Convert data if type specified
            converted_value = None
            if data_type and registers:
                converted_value = self._convert_registers(registers, data_type)
            
            self.logger.debug(f"Read {len(registers)} holding registers from device {device_id}")
            response = {
                "device_id": device_id,
                "address": address,
                "count": count,
                "values": registers,
                "timestamp": datetime.now().isoformat()
            }
            
            if converted_value is not None:
                response["converted_value"] = converted_value
                response["data_type"] = data_type.value
                
            return response
            
        except Exception as e:
            self.logger.error(f"Error reading holding registers from device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def read_input_registers(self, device_id: str, address: int, count: int = 1,
                                  data_type: Optional[ModbusDataType] = None) -> Dict[str, Any]:
        """
        Read input registers from a Modbus device.
        
        Args:
            device_id: ID of the device to read from
            address: Starting address of registers to read
            count: Number of registers to read
            data_type: Optional data type for conversion
            
        Returns:
            Dict with result or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Read input registers
            result = await client.read_input_registers(address, count, slave=unit_id)
            
            if result.isError():
                self.logger.error(f"Error reading input registers from device {device_id}: {result}")
                return {"error": str(result)}
                
            # Format result
            registers = [r for r in result.registers]
            
            # Convert data if type specified
            converted_value = None
            if data_type and registers:
                converted_value = self._convert_registers(registers, data_type)
            
            self.logger.debug(f"Read {len(registers)} input registers from device {device_id}")
            response = {
                "device_id": device_id,
                "address": address,
                "count": count,
                "values": registers,
                "timestamp": datetime.now().isoformat()
            }
            
            if converted_value is not None:
                response["converted_value"] = converted_value
                response["data_type"] = data_type.value
                
            return response
            
        except Exception as e:
            self.logger.error(f"Error reading input registers from device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def write_coil(self, device_id: str, address: int, value: bool) -> Dict[str, Any]:
        """
        Write to a single coil on a Modbus device.
        
        Args:
            device_id: ID of the device to write to
            address: Address of the coil to write
            value: Value to write (True/False)
            
        Returns:
            Dict with result or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Write coil
            result = await client.write_coil(address, value, slave=unit_id)
            
            if result.isError():
                self.logger.error(f"Error writing coil to device {device_id}: {result}")
                return {"error": str(result)}
                
            self.logger.debug(f"Wrote value {value} to coil at address {address} on device {device_id}")
            return {
                "device_id": device_id,
                "address": address,
                "value": value,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error writing coil to device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def write_coils(self, device_id: str, address: int, values: List[bool]) -> Dict[str, Any]:
        """
        Write to multiple coils on a Modbus device.
        
        Args:
            device_id: ID of the device to write to
            address: Starting address of coils to write
            values: List of values to write
            
        Returns:
            Dict with result or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Write coils
            result = await client.write_coils(address, values, slave=unit_id)
            
            if result.isError():
                self.logger.error(f"Error writing coils to device {device_id}: {result}")
                return {"error": str(result)}
                
            self.logger.debug(f"Wrote {len(values)} values to coils starting at address {address} on device {device_id}")
            return {
                "device_id": device_id,
                "address": address,
                "count": len(values),
                "values": values,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error writing coils to device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def write_register(self, device_id: str, address: int, value: int) -> Dict[str, Any]:
        """
        Write to a single register on a Modbus device.
        
        Args:
            device_id: ID of the device to write to
            address: Address of the register to write
            value: Value to write (0-65535)
            
        Returns:
            Dict with result or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Write register
            result = await client.write_register(address, value, slave=unit_id)
            
            if result.isError():
                self.logger.error(f"Error writing register to device {device_id}: {result}")
                return {"error": str(result)}
                
            self.logger.debug(f"Wrote value {value} to register at address {address} on device {device_id}")
            return {
                "device_id": device_id,
                "address": address,
                "value": value,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error writing register to device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def write_registers(self, device_id: str, address: int, values: List[int]) -> Dict[str, Any]:
        """
        Write to multiple registers on a Modbus device.
        
        Args:
            device_id: ID of the device to write to
            address: Starting address of registers to write
            values: List of values to write
            
        Returns:
            Dict with result or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Write registers
            result = await client.write_registers(address, values, slave=unit_id)
            
            if result.isError():
                self.logger.error(f"Error writing registers to device {device_id}: {result}")
                return {"error": str(result)}
                
            self.logger.debug(f"Wrote {len(values)} values to registers starting at address {address} on device {device_id}")
            return {
                "device_id": device_id,
                "address": address,
                "count": len(values),
                "values": values,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error writing registers to device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def write_typed_value(self, device_id: str, address: int, value: Any, 
                               data_type: ModbusDataType) -> Dict[str, Any]:
        """
        Write a typed value to registers on a Modbus device.
        
        Args:
            device_id: ID of the device to write to
            address: Starting address of registers to write
            value: Value to write
            data_type: Data type of the value
            
        Returns:
            Dict with result or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Create payload builder
            builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
            
            # Add value based on data type
            if data_type == ModbusDataType.BOOL:
                builder.add_bits([value])
            elif data_type == ModbusDataType.UINT16:
                builder.add_16bit_uint(value)
            elif data_type == ModbusDataType.INT16:
                builder.add_16bit_int(value)
            elif data_type == ModbusDataType.UINT32:
                builder.add_32bit_uint(value)
            elif data_type == ModbusDataType.INT32:
                builder.add_32bit_int(value)
            elif data_type == ModbusDataType.FLOAT32:
                builder.add_32bit_float(value)
            elif data_type == ModbusDataType.FLOAT64:
                builder.add_64bit_float(value)
            elif data_type == ModbusDataType.STRING:
                builder.add_string(value)
            else:
                return {"error": f"Unsupported data type: {data_type}"}
                
            # Build payload
            registers = builder.to_registers()
            
            # Write registers
            result = await client.write_registers(address, registers, slave=unit_id)
            
            if result.isError():
                self.logger.error(f"Error writing typed value to device {device_id}: {result}")
                return {"error": str(result)}
                
            self.logger.debug(f"Wrote {data_type.value} value {value} to registers starting at address {address} on device {device_id}")
            return {
                "device_id": device_id,
                "address": address,
                "value": value,
                "data_type": data_type.value,
                "register_count": len(registers),
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error writing typed value to device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def read_device_identification(self, device_id: str) -> Dict[str, Any]:
        """
        Read device identification information.
        
        Args:
            device_id: ID of the device to read from
            
        Returns:
            Dict with device identification or error
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return {"error": "Not connected to device"}
            
        client_info = self.clients[device_id]
        client = client_info["client"]
        unit_id = client_info["unit_id"]
        
        try:
            # Read device identification
            result = await client.read_device_identification(unit=unit_id)
            
            if result.isError():
                self.logger.error(f"Error reading device identification from device {device_id}: {result}")
                return {"error": str(result)}
                
            # Format result
            identification = {}
            for key, value in result.information.items():
                identification[key] = value.decode('utf-8', errors='replace')
            
            self.logger.debug(f"Read device identification from device {device_id}")
            return {
                "device_id": device_id,
                "identification": identification,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error reading device identification from device {device_id}: {str(e)}")
            return {"error": str(e)}
    
    async def start_polling(self, device_id: str, register_type: str, address: int, count: int,
                           interval: float, data_type: Optional[ModbusDataType] = None) -> str:
        """
        Start polling a register or coil at regular intervals.
        
        Args:
            device_id: ID of the device to poll
            register_type: Type of register to poll ('coil', 'discrete_input', 'holding', 'input')
            address: Address to poll
            count: Number of registers/coils to poll
            interval: Polling interval in seconds
            data_type: Optional data type for conversion
            
        Returns:
            str: Polling task ID if successful, empty string otherwise
        """
        if device_id not in self.clients:
            self.logger.error(f"Not connected to Modbus device {device_id}")
            return ""
            
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Define polling function
        async def poll_task():
            try:
                while True:
                    # Read based on register type
                    if register_type == "coil":
                        result = await self.read_coils(device_id, address, count)
                    elif register_type == "discrete_input":
                        result = await self.read_discrete_inputs(device_id, address, count)
                    elif register_type == "holding":
                        result = await self.read_holding_registers(device_id, address, count, data_type)
                    elif register_type == "input":
                        result = await self.read_input_registers(device_id, address, count, data_type)
                    else:
                        self.logger.error(f"Invalid register type: {register_type}")
                        return
                        
                    # Check for error
                    if "error" in result:
                        self.logger.error(f"Error polling device {device_id}: {result['error']}")
                    else:
                        # Publish event
                        await self.publish_event(
                            MessageFactory.create_event(
                                "modbus_poll_data",
                                payload={
                                    "task_id": task_id,
                                    "device_id": device_id,
                                    "register_type": register_type,
                                    "address": address,
                                    "count": count,
                                    "data": result
                                },
                                priority=MessagePriority.LOW
                            )
                        )
                    
                    # Wait for next interval
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                self.logger.info(f"Polling task {task_id} cancelled")
            except Exception as e:
                self.logger.error(f"Error in polling task {task_id}: {str(e)}")
        
        # Start polling task
        task = asyncio.create_task(poll_task())
        
        # Store task
        self.polling_tasks[task_id] = {
            "device_id": device_id,
            "register_type": register_type,
            "address": address,
            "count": count,
            "interval": interval,
            "data_type": data_type.value if data_type else None,
            "task": task,
            "started_at": datetime.now()
        }
        
        self.logger.info(f"Started polling task {task_id} for device {device_id}")
        return task_id
    
    async def stop_polling(self, task_id: str) -> bool:
        """
        Stop a polling task.
        
        Args:
            task_id: ID of the polling task to stop
            
        Returns:
            bool: True if task stopped successfully, False otherwise
        """
        if task_id not in self.polling_tasks:
            self.logger.error(f"Polling task {task_id} not found")
            return False
            
        try:
            # Get task
            task_info = self.polling_tasks[task_id]
            task = task_info["task"]
            
            # Cancel task
            task.cancel()
            
            # Remove from polling tasks
            del self.polling_tasks[task_id]
            
            self.logger.info(f"Stopped polling task {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping polling task {task_id}: {str(e)}")
            return False
    
    async def discover_devices(self, start_ip: str, end_ip: str, port: int = 502, 
                              timeout: float = 0.5) -> List[Dict[str, Any]]:
        """
        Discover Modbus TCP devices on a network.
        
        Args:
            start_ip: Starting IP address
            end_ip: Ending IP address
            port: Port to scan
            timeout: Connection timeout in seconds
            
        Returns:
            List of discovered devices
        """
        if not pymodbus:
            self.logger.error("Modbus library not installed. Cannot discover devices.")
            return []
            
        # Parse IP addresses
        start_parts = [int(p) for p in start_ip.split('.')]
        end_parts = [int(p) for p in end_ip.split('.')]
        
        # Calculate IP range
        start_int = (start_parts[0] << 24) + (start_parts[1] << 16) + (start_parts[2] << 8) + start_parts[3]
        end_int = (end_parts[0] << 24) + (end_parts[1] << 16) + (end_parts[2] << 8) + end_parts[3]
        
        if start_int > end_int:
            self.logger.error(f"Invalid IP range: {start_ip} - {end_ip}")
            return []
            
        # Prepare discovery tasks
        tasks = []
        for ip_int in range(start_int, end_int + 1):
            ip = f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"
            tasks.append(self._check_device(ip, port, timeout))
            
        # Run discovery tasks
        self.logger.info(f"Starting discovery of Modbus TCP devices in range {start_ip} - {end_ip}")
        results = await asyncio.gather(*tasks)
        
        # Filter successful results
        discovered = [r for r in results if r is not None]
        
        self.logger.info(f"Discovered {len(discovered)} Modbus TCP devices")
        return discovered
    
    async def _check_device(self, ip: str, port: int, timeout: float) -> Optional[Dict[str, Any]]:
        """
        Check if a Modbus TCP device exists at the given IP and port.
        
        Args:
            ip: IP address to check
            port: Port to check
            timeout: Connection timeout in seconds
            
        Returns:
            Device info if found, None otherwise
        """
        try:
            # Create client
            client = AsyncModbusTcpClient(
                host=ip,
                port=port,
                timeout=timeout,
                retries=0
            )
            
            # Try to connect
            connected = await client.connect()
            if not connected:
                return None
                
            # Try to read device identification
            try:
                result = await client.read_device_identification(unit=1)
                identification = {}
                if not result.isError():
                    for key, value in result.information.items():
                        identification[key] = value.decode('utf-8', errors='replace')
            except (AttributeError, UnicodeDecodeError, KeyError):
                # AttributeError: result.information doesn't exist
                # UnicodeDecodeError: can't decode bytes
                # KeyError: missing expected keys
                identification = {}
                
            # Close connection
            client.close()
            
            # Return device info
            return {
                "ip": ip,
                "port": port,
                "identification": identification,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception:
            return None
    
    def _convert_registers(self, registers: List[int], data_type: ModbusDataType) -> Any:
        """
        Convert registers to the specified data type.
        
        Args:
            registers: List of register values
            data_type: Target data type
            
        Returns:
            Converted value
        """
        # Create decoder
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers,
            byteorder=Endian.Big,
            wordorder=Endian.Big
        )
        
        # Decode based on data type
        if data_type == ModbusDataType.BOOL:
            return decoder.decode_bits()[0]
        elif data_type == ModbusDataType.UINT16:
            return decoder.decode_16bit_uint()
        elif data_type == ModbusDataType.INT16:
            return decoder.decode_16bit_int()
        elif data_type == ModbusDataType.UINT32:
            return decoder.decode_32bit_uint()
        elif data_type == ModbusDataType.INT32:
            return decoder.decode_32bit_int()
        elif data_type == ModbusDataType.FLOAT32:
            return decoder.decode_32bit_float()
        elif data_type == ModbusDataType.FLOAT64:
            return decoder.decode_64bit_float()
        elif data_type == ModbusDataType.STRING:
            # Determine string length based on register count
            string_len = len(registers) * 2
            return decoder.decode_string(string_len).decode('utf-8', errors='replace')
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    async def translate_to_industriverse(self, modbus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Modbus data to Industriverse protocol format.
        
        Args:
            modbus_data: Modbus data to translate
            
        Returns:
            Data in Industriverse protocol format
        """
        # Create Unified Message Envelope
        ume = {
            "origin_protocol": "MODBUS",
            "target_protocol": "MCP",
            "context": {
                "industrial_protocol": "MODBUS",
                "adapter_id": self.component_id,
                "timestamp": datetime.now().isoformat()
            },
            "payload": modbus_data,
            "trace_id": str(uuid.uuid4()),
            "security_level": "medium",
            "reflex_timer_ms": 5000  # 5 seconds default timeout
        }
        
        return ume
    
    async def translate_from_industriverse(self, industriverse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Industriverse protocol data to Modbus format.
        
        Args:
            industriverse_data: Industriverse protocol data to translate
            
        Returns:
            Data in Modbus format
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
            if command == "connect":
                success = await self.connect(
                    params.get("device_id", ""),
                    params.get("host", None),
                    params.get("port", 502),
                    ModbusVariant(params.get("variant", "tcp")),
                    params.get("serial_port", None),
                    params.get("baudrate", 9600),
                    params.get("timeout", 1.0),
                    params.get("unit_id", 1)
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "disconnect":
                success = await self.disconnect(params.get("device_id", None))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "read_coils":
                result = await self.read_coils(
                    params.get("device_id", ""),
                    params.get("address", 0),
                    params.get("count", 1)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "read_discrete_inputs":
                result = await self.read_discrete_inputs(
                    params.get("device_id", ""),
                    params.get("address", 0),
                    params.get("count", 1)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "read_holding_registers":
                data_type = None
                if "data_type" in params:
                    try:
                        data_type = ModbusDataType(params["data_type"])
                    except ValueError:
                        pass
                        
                result = await self.read_holding_registers(
                    params.get("device_id", ""),
                    params.get("address", 0),
                    params.get("count", 1),
                    data_type
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "read_input_registers":
                data_type = None
                if "data_type" in params:
                    try:
                        data_type = ModbusDataType(params["data_type"])
                    except ValueError:
                        pass
                        
                result = await self.read_input_registers(
                    params.get("device_id", ""),
                    params.get("address", 0),
                    params.get("count", 1),
                    data_type
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "write_coil":
                result = await self.write_coil(
                    params.get("device_id", ""),
                    params.get("address", 0),
                    params.get("value", False)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "write_coils":
                result = await self.write_coils(
                    params.get("device_id", ""),
                    params.get("address", 0),
                    params.get("values", [])
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "write_register":
                result = await self.write_register(
                    params.get("device_id", ""),
                    params.get("address", 0),
                    params.get("value", 0)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "write_registers":
                result = await self.write_registers(
                    params.get("device_id", ""),
                    params.get("address", 0),
                    params.get("values", [])
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "write_typed_value":
                try:
                    data_type = ModbusDataType(params.get("data_type", ""))
                except ValueError:
                    return MessageFactory.create_response(
                        message,
                        success=False,
                        error=f"Invalid data type: {params.get('data_type', '')}"
                    )
                    
                result = await self.write_typed_value(
                    params.get("device_id", ""),
                    params.get("address", 0),
                    params.get("value", None),
                    data_type
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "read_device_identification":
                result = await self.read_device_identification(
                    params.get("device_id", "")
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "start_polling":
                try:
                    data_type = None
                    if "data_type" in params:
                        data_type = ModbusDataType(params["data_type"])
                except ValueError:
                    return MessageFactory.create_response(
                        message,
                        success=False,
                        error=f"Invalid data type: {params.get('data_type', '')}"
                    )
                    
                task_id = await self.start_polling(
                    params.get("device_id", ""),
                    params.get("register_type", ""),
                    params.get("address", 0),
                    params.get("count", 1),
                    params.get("interval", 1.0),
                    data_type
                )
                return MessageFactory.create_response(message, result={"task_id": task_id})
                
            elif command == "stop_polling":
                success = await self.stop_polling(params.get("task_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "discover_devices":
                result = await self.discover_devices(
                    params.get("start_ip", ""),
                    params.get("end_ip", ""),
                    params.get("port", 502),
                    params.get("timeout", 0.5)
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
        if message.get("origin_protocol") and message.get("origin_protocol") != "MODBUS":
            modbus_message = await self.translate_from_industriverse(message)
        else:
            modbus_message = message
            
        # Handle message
        response = await self.handle_message(modbus_message)
        
        # Translate to Industriverse protocol if needed
        if message.get("target_protocol") and message.get("target_protocol") != "MODBUS":
            industriverse_response = await self.translate_to_industriverse(response)
            return industriverse_response
        else:
            return response
    
    async def shutdown(self):
        """
        Shutdown the adapter, closing all connections and stopping all polling tasks.
        """
        self.logger.info(f"Shutting down Modbus Adapter {self.component_id}")
        
        # Stop all polling tasks
        for task_id in list(self.polling_tasks.keys()):
            await self.stop_polling(task_id)
            
        # Disconnect all clients
        await self.disconnect()
        
        # Unregister from discovery service
        self.discovery_service.unregister_component(self.component_id)
        
        self.logger.info(f"Modbus Adapter {self.component_id} shutdown complete")

# Example usage
async def example_usage():
    # Create adapter
    adapter = ModbusAdapter(config={
        "use_tpm": True,
        "industry_tags": ["manufacturing", "energy"]
    })
    
    # Connect to device
    success = await adapter.connect(
        device_id="device1",
        host="192.168.1.100",
        port=502,
        variant=ModbusVariant.TCP,
        unit_id=1
    )
    
    if success:
        # Read holding registers
        result = await adapter.read_holding_registers(
            device_id="device1",
            address=100,
            count=10,
            data_type=ModbusDataType.FLOAT32
        )
        print(f"Read result: {result}")
        
        # Start polling
        task_id = await adapter.start_polling(
            device_id="device1",
            register_type="holding",
            address=100,
            count=2,
            interval=5.0,
            data_type=ModbusDataType.FLOAT32
        )
        
        # Wait for some polling cycles
        await asyncio.sleep(15)
        
        # Stop polling
        await adapter.stop_polling(task_id)
        
        # Disconnect
        await adapter.disconnect("device1")
    
    # Discover devices
    devices = await adapter.discover_devices("192.168.1.1", "192.168.1.254")
    print(f"Discovered devices: {devices}")
    
    # Shutdown
    await adapter.shutdown()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run example
    asyncio.run(example_usage())
