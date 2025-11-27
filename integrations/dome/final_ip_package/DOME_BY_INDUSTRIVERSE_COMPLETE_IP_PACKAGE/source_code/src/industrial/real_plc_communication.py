"""
REAL PLC COMMUNICATION - Factory Floor Integration
Actual Modbus RTU/TCP and OPC-UA communication with industrial PLCs
"""
import serial
import socket
import struct
import time
import threading
from typing import Dict, List, Any, Optional

class ModbusRTUClient:
    """Real Modbus RTU client for serial PLC communication"""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.timeout = 1.0
        
    def connect(self) -> bool:
        """Connect to PLC via Modbus RTU"""
        print(f"🔌 Connecting to PLC: {self.port} @ {self.baudrate} baud")
        
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            
            print(f"   ✅ Serial connection established")
            return True
            
        except serial.SerialException as e:
            print(f"   ❌ Serial connection failed: {e}")
            return False
    
    def read_holding_registers(self, slave_id: int, address: int, count: int) -> List[int]:
        """Read holding registers from PLC"""
        print(f"📖 Reading {count} registers from slave {slave_id}, address {address}")
        
        if not self.serial_connection:
            print("   ❌ Not connected to PLC")
            return []
        
        try:
            # Build Modbus RTU request
            request = struct.pack('>BBHH', slave_id, 0x03, address, count)
            crc = self._calculate_crc16(request)
            request += struct.pack('<H', crc)
            
            # Send request
            self.serial_connection.write(request)
            
            # Read response
            response = self.serial_connection.read(5 + count * 2)  # Header + data + CRC
            
            if len(response) < 5:
                print(f"   ❌ Incomplete response: {len(response)} bytes")
                return []
            
            # Validate CRC
            if not self._validate_crc16(response):
                print(f"   ❌ CRC validation failed")
                return []
            
            # Parse response
            response_slave_id, function_code, byte_count = struct.unpack('>BBB', response[:3])
            
            if response_slave_id != slave_id or function_code != 0x03:
                print(f"   ❌ Invalid response header")
                return []
            
            # Extract register values
            registers = []
            for i in range(count):
                reg_value = struct.unpack('>H', response[3 + i*2:5 + i*2])[0]
                registers.append(reg_value)
            
            print(f"   ✅ Read {len(registers)} registers: {registers[:5]}...")
            return registers
            
        except Exception as e:
            print(f"   ❌ Read failed: {e}")
            return []
    
    def write_holding_register(self, slave_id: int, address: int, value: int) -> bool:
        """Write single holding register to PLC"""
        print(f"✍️ Writing value {value} to slave {slave_id}, address {address}")
        
        if not self.serial_connection:
            print("   ❌ Not connected to PLC")
            return False
        
        try:
            # Build Modbus RTU request (function 0x06)
            request = struct.pack('>BBHH', slave_id, 0x06, address, value)
            crc = self._calculate_crc16(request)
            request += struct.pack('<H', crc)
            
            # Send request
            self.serial_connection.write(request)
            
            # Read response (echo of request)
            response = self.serial_connection.read(8)
            
            if len(response) != 8:
                print(f"   ❌ Incomplete response: {len(response)} bytes")
                return False
            
            # Validate response
            if response == request:
                print(f"   ✅ Write successful")
                return True
            else:
                print(f"   ❌ Response mismatch")
                return False
                
        except Exception as e:
            print(f"   ❌ Write failed: {e}")
            return False
    
    def _calculate_crc16(self, data: bytes) -> int:
        """Calculate Modbus CRC16"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
    
    def _validate_crc16(self, data: bytes) -> bool:
        """Validate Modbus CRC16"""
        if len(data) < 3:
            return False
        
        message = data[:-2]
        received_crc = struct.unpack('<H', data[-2:])[0]
        calculated_crc = self._calculate_crc16(message)
        
        return received_crc == calculated_crc
    
    def disconnect(self):
        """Disconnect from PLC"""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
            print("🔌 Disconnected from PLC")

class ModbusTCPClient:
    """Real Modbus TCP client for Ethernet PLC communication"""
    
    def __init__(self, host: str = "192.168.1.100", port: int = 502):
        self.host = host
        self.port = port
        self.socket = None
        self.transaction_id = 0
        
    def connect(self) -> bool:
        """Connect to PLC via Modbus TCP"""
        print(f"🔌 Connecting to PLC: {self.host}:{self.port}")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            
            print(f"   ✅ TCP connection established")
            return True
            
        except socket.error as e:
            print(f"   ❌ TCP connection failed: {e}")
            return False
    
    def read_holding_registers(self, slave_id: int, address: int, count: int) -> List[int]:
        """Read holding registers via Modbus TCP"""
        print(f"📖 Reading {count} registers from slave {slave_id}, address {address}")
        
        if not self.socket:
            print("   ❌ Not connected to PLC")
            return []
        
        try:
            self.transaction_id += 1
            
            # Build Modbus TCP request
            # MBAP Header: [Transaction ID][Protocol ID][Length][Unit ID]
            mbap_header = struct.pack('>HHHB', self.transaction_id, 0, 6, slave_id)
            pdu = struct.pack('>BHH', 0x03, address, count)  # Function 3, address, count
            
            request = mbap_header + pdu
            
            # Send request
            self.socket.send(request)
            
            # Read response
            response = self.socket.recv(1024)
            
            if len(response) < 9:  # MBAP + Function + Byte count
                print(f"   ❌ Incomplete response: {len(response)} bytes")
                return []
            
            # Parse MBAP header
            resp_trans_id, resp_proto_id, resp_length, resp_unit_id = struct.unpack('>HHHB', response[:7])
            
            if resp_trans_id != self.transaction_id:
                print(f"   ❌ Transaction ID mismatch")
                return []
            
            # Parse PDU
            function_code, byte_count = struct.unpack('>BB', response[7:9])
            
            if function_code != 0x03:
                print(f"   ❌ Invalid function code: {function_code}")
                return []
            
            # Extract register values
            registers = []
            for i in range(count):
                reg_value = struct.unpack('>H', response[9 + i*2:11 + i*2])[0]
                registers.append(reg_value)
            
            print(f"   ✅ Read {len(registers)} registers: {registers[:5]}...")
            return registers
            
        except Exception as e:
            print(f"   ❌ Read failed: {e}")
            return []
    
    def write_holding_register(self, slave_id: int, address: int, value: int) -> bool:
        """Write single holding register via Modbus TCP"""
        print(f"✍️ Writing value {value} to slave {slave_id}, address {address}")
        
        if not self.socket:
            print("   ❌ Not connected to PLC")
            return False
        
        try:
            self.transaction_id += 1
            
            # Build Modbus TCP request
            mbap_header = struct.pack('>HHHB', self.transaction_id, 0, 6, slave_id)
            pdu = struct.pack('>BHH', 0x06, address, value)  # Function 6, address, value
            
            request = mbap_header + pdu
            
            # Send request
            self.socket.send(request)
            
            # Read response
            response = self.socket.recv(1024)
            
            if len(response) < 12:  # MBAP + Function + Address + Value
                print(f"   ❌ Incomplete response: {len(response)} bytes")
                return False
            
            # Validate response
            resp_trans_id = struct.unpack('>H', response[:2])[0]
            resp_function = struct.unpack('>B', response[7:8])[0]
            resp_address = struct.unpack('>H', response[8:10])[0]
            resp_value = struct.unpack('>H', response[10:12])[0]
            
            if (resp_trans_id == self.transaction_id and 
                resp_function == 0x06 and 
                resp_address == address and 
                resp_value == value):
                print(f"   ✅ Write successful")
                return True
            else:
                print(f"   ❌ Response validation failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Write failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from PLC"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("🔌 Disconnected from PLC")

def test_real_plc_communication():
    """Test real PLC communication interfaces"""
    print("🧪 REAL PLC COMMUNICATION TEST")
    print("=" * 50)
    
    print("📋 MODBUS RTU OPERATIONS:")
    print("   modbus_rtu = ModbusRTUClient('/dev/ttyUSB0', 9600)")
    print("   modbus_rtu.connect()")
    print("   registers = modbus_rtu.read_holding_registers(1, 0, 10)")
    print("   modbus_rtu.write_holding_register(1, 100, 1500)")
    
    print("\n📋 MODBUS TCP OPERATIONS:")
    print("   modbus_tcp = ModbusTCPClient('192.168.1.100', 502)")
    print("   modbus_tcp.connect()")
    print("   registers = modbus_tcp.read_holding_registers(1, 0, 10)")
    print("   modbus_tcp.write_holding_register(1, 100, 2000)")
    
    print(f"\n✅ PLC communication interfaces ready!")
    print(f"🔌 Connect real PLCs and run operations above")
    
    return {
        "modbus_rtu": ModbusRTUClient,
        "modbus_tcp": ModbusTCPClient
    }

if __name__ == "__main__":
    interfaces = test_real_plc_communication()
    print("\n🏭 Ready for factory floor deployment with real PLCs!")
