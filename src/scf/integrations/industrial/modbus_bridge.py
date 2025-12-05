import time
from typing import Dict, Optional, List

class ModbusBridge:
    """
    Industrial Connector for Modbus TCP.
    Reads/Writes registers on PLCs.
    Includes a 'Mock Mode' for development without hardware.
    """
    def __init__(self, host: str, port: int = 502, mock_mode: bool = False):
        self.host = host
        self.port = port
        self.mock_mode = mock_mode
        self.connected = False
        self.registers = {} # Mock memory

    def connect(self) -> bool:
        """
        Establish connection to the PLC.
        """
        if self.mock_mode:
            self.connected = True
            print(f"🔌 [MOCK] Connected to Modbus PLC at {self.host}:{self.port}")
            return True
        
        # In real implementation, we would use pymodbus here
        # try:
        #     self.client = ModbusTcpClient(self.host, self.port)
        #     self.connected = self.client.connect()
        # except: ...
        print(f"⚠️ Real Modbus connection not implemented yet. Use mock_mode=True.")
        return False

    def read_holding_registers(self, address: int, count: int = 1) -> List[int]:
        """
        Read holding registers (4xxxx).
        """
        if not self.connected:
            raise ConnectionError("Not connected to PLC")

        if self.mock_mode:
            # Return mock values or 0
            return [self.registers.get(address + i, 0) for i in range(count)]
        
        return []

    def write_register(self, address: int, value: int) -> bool:
        """
        Write a single register.
        """
        if not self.connected:
            raise ConnectionError("Not connected to PLC")

        if self.mock_mode:
            self.registers[address] = value
            print(f"📝 [MOCK] Wrote {value} to Register {address}")
            return True
            
        return False

    def close(self):
        self.connected = False
        print("🔌 Disconnected from PLC")
